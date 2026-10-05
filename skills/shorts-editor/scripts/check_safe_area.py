#!/usr/bin/env python3
"""Catch ink outside the shorts safe area, AND a face in the covered bottom band, BEFORE upload.

Why this exists: a top card was once cut off on mobile with all three edges in breach at
once (card ink at y=96, captions ending at y=1680, text reaching x=1014 under the action
rail). Five videos had to be re-uploaded, because YouTube cannot swap the file on an
existing video. This is the cheap check that would have caught it.

Later a short PASSED this script with the speaker's mouth covered by the platform's bottom
overlay at about 24 s: the face sat too low, and a bright-ink test can never see a face
(skin is mid-tone). So the bottom line moved from y=1680 to y=1500 (the safe frame in
content/taste/shorts-formats.md: nothing that matters in the bottom 22 percent), and a
FACE-IN-BAND test was added.

Safe area enforced on a 1080x1920 short:
    top     ink above  y=200   is unsafe
    bottom  ink below  y=1500  is unsafe (the old line was 1680; pass --bottom 1680 for it)
    right   ink right of x=940 AND below y=960 is unsafe (the action rail: like / dislike / share;
            measured on a phone as the right 16% from 50% down, so a card above 960 may use the full
            width; an earlier version tested any height and forced an unreadable 800 px panel)
    face    the lower third of the face box (mouth and chin) below y=1500 is unsafe

"Ink" = BRIGHT graphic pixels (cards, captions, numbers) sitting well above the sampled
local background. Bright-only is deliberate: mid-tone footage is not an ink breach -- a
white caption or a card edge is. The FACE test covers the footage: it finds the largest
face per sampled frame and fails when any of the box's lower third (where the mouth and
chin are) sits below the bottom line. Method, printed in the output:
    opencv-haar  OpenCV's Haar cascades (frontal default, then frontal alt2, then profile
                 both ways) on the sampled frame at half size. Used whenever cv2 imports.
                 A Haar frontal box runs from mid-forehead to about the chin: on the
                 calibration frames the mouth sat at 0.78 of its height and the
                 bottom of the beard at 1.05, so "box bottom below the line" means the mouth's
                 lower lip is within about a quarter box of the line and the chin is past it.
    skin-band    fallback when cv2 is missing: skin-tone pixels (YCbCr: Y over 80, Cb 90..112,
                 Cr 150..180) in the face column (middle 60 percent of the width by default,
                 --face-col), rows grouped into the largest run, that run treated as the face
                 box. Coarse: the chroma band was set against a beige wall that a
                 wider band reads as skin (wall Cb 112..116 / Cr 142..143, cheek Cb 105 / Cr 158);
                 a bare neck makes it stricter, a dark beard laxer, another wall may fool it.
                 Install opencv-python to get Haar.
A frame where no face is found is counted and reported, never passed silently as clean.
Approximate detection is the point: this exists to catch gross breaches, not to grade
typography. It samples at --fps (default 1) and reports the timestamps and edges.

Usage:
  python check_safe_area.py <render.mp4> [--fps 1] [--tol 40] [--min-px 400] [--bright 245]
                            [--top 200] [--bottom 1500] [--right 940] [--keep DIR]
                            [--no-face] [--face-min 150] [--face-col 216,864]

Exit 0 = clean. Exit 1 = violations listed (timestamp + edge + pixel count, or the face box).
With --keep DIR the sampled frames stay there, plus <frame>_face.png with the box, its lower
third and the bottom line drawn on every frame the face test flagged.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

try:
    from PIL import Image, ImageDraw
except ImportError:
    sys.exit("PIL (Pillow) is required: pip install Pillow")

try:
    import cv2  # optional: the face test's primary method
    import numpy as np
except Exception:  # noqa: BLE001 - any import failure means "use the fallback"
    cv2 = None

W, H = 1080, 1920


def probe_size(video):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", video],
        capture_output=True, text=True).stdout.strip()
    w, h = out.split("x")[:2]
    return int(w), int(h)


def sample_frames(video, fps, outdir, fmt="gray", prefix=""):
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", video,
         "-vf", f"fps={fps},scale={W}:{H},format={fmt}",
         os.path.join(outdir, f"{prefix}%05d.png")],
        check=True)
    return sorted(f for f in os.listdir(outdir)
                  if f.endswith(".png") and f.startswith(prefix) and not f.endswith("_face.png")
                  and (prefix or not f.startswith("rgb_")))


def band_background(px, x0, y0, x1, y1):
    """Sample the background of a band as the median of its pixels. On a black card
    band or a video plate the median is the plate; ink is the tail away from it."""
    vals = []
    step_x = max(1, (x1 - x0) // 60)
    step_y = max(1, (y1 - y0) // 30)
    for y in range(y0, y1, step_y):
        for x in range(x0, x1, step_x):
            vals.append(px[x, y])
    if not vals:
        return 0
    vals.sort()
    return vals[len(vals) // 2]


def count_ink(px, x0, y0, x1, y1, tol, bright):
    """Bright graphic ink only: well above the band background AND bright in absolute
    terms. Footage is mid-tone and continuous; cards and captions are not."""
    bg = band_background(px, x0, y0, x1, y1)
    floor = max(bg + tol, bright)
    n = 0
    step = 2  # every other pixel: plenty for a gross-breach check, 4x faster
    for y in range(y0, y1, step):
        for x in range(x0, x1, step):
            if px[x, y] >= floor:
                n += 1
    return n * step * step  # scale back to full-resolution pixel count


# ---------------------------------------------------------------- face in the bottom band

_CASCADES = None


def _cascades():
    global _CASCADES
    if _CASCADES is None:
        d = cv2.data.haarcascades
        _CASCADES = [("frontal", cv2.CascadeClassifier(d + "haarcascade_frontalface_default.xml")),
                     ("frontal-alt2", cv2.CascadeClassifier(d + "haarcascade_frontalface_alt2.xml")),
                     ("profile", cv2.CascadeClassifier(d + "haarcascade_profileface.xml"))]
    return _CASCADES


def face_haar(gray_path, face_min):
    """Largest face as (x, y, w, h, which) in 1080x1920 pixels, or None. Frontal first; the
    profile cascade (and its mirror) only when no frontal face is found."""
    g = cv2.imread(gray_path, cv2.IMREAD_GRAYSCALE)
    if g is None:
        return None
    s = 0.5
    gs = cv2.resize(g, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    ms = max(24, int(face_min * s))
    for name, c in _cascades():
        found = []
        for (x, y, w, h) in c.detectMultiScale(gs, 1.08, 5, minSize=(ms, ms)):
            found.append((x, y, w, h))
        if name == "profile":
            fl = cv2.flip(gs, 1)
            for (x, y, w, h) in c.detectMultiScale(fl, 1.08, 5, minSize=(ms, ms)):
                found.append((gs.shape[1] - x - w, y, w, h))
        if found:
            x, y, w, h = max(found, key=lambda b: b[2] * b[3])
            return (x / s, y / s, w / s, h / s, name)
    return None


def face_skin(rgb_path, face_min, col, top):
    """Fallback: the largest run of rows with skin-tone pixels in the face column."""
    im = Image.open(rgb_path).convert("YCbCr")
    px = im.load()
    x0, x1 = col
    step = 3
    rows = []
    for y in range(top, H, step):
        n = tot = 0
        for x in range(x0, x1, step):
            yy, cb, cr = px[x, y]
            tot += 1
            if yy > 80 and 90 <= cb <= 112 and 150 <= cr <= 180:
                n += 1
        rows.append((y, n / max(1, tot)))
    best, cur = None, None
    for y, frac in rows:
        if frac >= 0.18:
            if cur and y - cur[1] <= 24:
                cur[1] = y
            else:
                cur = [y, y]
            if best is None or (cur[1] - cur[0]) > (best[1] - best[0]):
                best = list(cur)
    if not best or best[1] - best[0] < face_min:
        return None
    return (x0, best[0], x1 - x0, best[1] - best[0] + step, "skin-band")


def draw_face(gray_path, box, bottom, out_path):
    im = Image.open(gray_path).convert("RGB")
    d = ImageDraw.Draw(im)
    x, y, w, h, _ = box
    d.rectangle((x, y, x + w, y + h), outline=(0, 255, 0), width=4)
    d.rectangle((x, y + 2 * h / 3, x + w, y + h), outline=(255, 160, 0), width=4)
    d.line((0, bottom, W, bottom), fill=(255, 0, 0), width=4)
    im.save(out_path)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--fps", type=float, default=1.0)
    ap.add_argument("--tol", type=int, default=40,
                    help="how far from the sampled background a pixel counts as ink")
    ap.add_argument("--min-px", type=int, default=400,
                    help="bright ink pixels in a band before it counts as a violation")
    ap.add_argument("--bright", type=int, default=245,
                    help="absolute luminance floor for graphic ink. 245 = caption-white and "
                         "card-white only; calibrated on real renders so bright FOOTAGE "
                         "(a lit wall, a white shirt) in the lower band is not flagged. "
                         "Lower it to ~200 to sweep more aggressively and eyeball the hits.")
    ap.add_argument("--top", type=int, default=200)
    ap.add_argument("--bottom", type=int, default=1500,
                    help="the covered bottom band starts here (safe frame: 1500 = "
                         "the bottom 22 percent). 1680 was the old default.")
    ap.add_argument("--right", type=int, default=940)
    ap.add_argument("--right-from", type=int, default=960,
                    help="the right rail starts at this y (content/taste/shorts-formats.md: the right 16%% is dead from 50%% down); above it the full width is usable")
    ap.add_argument("--keep", default=None)
    ap.add_argument("--no-face", action="store_true",
                    help="skip the face-in-band test (ink test only, the older check)")
    ap.add_argument("--face-min", type=int, default=150,
                    help="smallest face box counted, in pixels on the 1080-wide frame")
    ap.add_argument("--face-col", default="216,864",
                    help="x0,x1 of the face column for the skin-band fallback only")
    a = ap.parse_args()

    if not os.path.exists(a.video):
        sys.exit(f"no such file: {a.video}")

    vw, vh = probe_size(a.video)
    if (vw, vh) != (W, H):
        print(f"note: source is {vw}x{vh}, scaling to {W}x{H} for the check")

    face_on = not a.no_face
    method = ("opencv-haar" if cv2 is not None else "skin-band") if face_on else None
    col = tuple(int(v) for v in a.face_col.split(","))

    tmp = a.keep or tempfile.mkdtemp(prefix="safearea_")
    os.makedirs(tmp, exist_ok=True)
    violations = []
    face_hits, face_found, lowest = [], 0, None
    try:
        frames = sample_frames(a.video, a.fps, tmp)
        if not frames:
            sys.exit("no frames extracted; is this a video file?")
        rgb = []
        if face_on and method == "skin-band":
            rgb = sample_frames(a.video, a.fps, tmp, fmt="rgb24", prefix="rgb_")
        for i, f in enumerate(frames):
            t = i / a.fps
            img = Image.open(os.path.join(tmp, f)).convert("L")
            px = img.load()
            checks = [
                ("top",    (0, 0, W, a.top)),
                ("bottom", (0, a.bottom, W, H)),
                ("right",  (a.right, max(a.top, a.right_from), W, a.bottom)),
            ]
            for edge, (x0, y0, x1, y1) in checks:
                n = count_ink(px, x0, y0, x1, y1, a.tol, a.bright)
                if n >= a.min_px:
                    violations.append((t, edge, n))
            if face_on:
                if method == "opencv-haar":
                    box = face_haar(os.path.join(tmp, f), a.face_min)
                else:
                    box = face_skin(os.path.join(tmp, rgb[i]), a.face_min, col, a.top) if i < len(rgb) else None
                if box:
                    face_found += 1
                    x, y, w, h, which = box
                    if lowest is None or y + h > lowest[1]:
                        lowest = (t, y + h)
                    if y + h > a.bottom:   # any of the lower third (mouth, chin) below the line
                        face_hits.append((t, box))
                        if a.keep:
                            draw_face(os.path.join(tmp, f), box, a.bottom,
                                      os.path.join(tmp, f.replace(".png", "_face.png")))
        print(f"scanned {len(frames)} frames at {a.fps}fps  "
              f"(safe area: top>{a.top}, bottom<{a.bottom}, right<{a.right})")
        if face_on:
            low = f"; lowest face-box bottom y={lowest[1]:.0f} at {lowest[0]:.2f}s" if lowest else ""
            print(f"face test: method {method}; a face found in {face_found} of {len(frames)} frames{low}")
            if face_found == 0:
                print("  note: no face found in any frame, so the face test checked nothing "
                      "(a format with no face, or the detector missed it: look at the frames)")
        else:
            print("face test: skipped (--no-face)")
        if not violations and not face_hits:
            print("PASS: no ink outside the safe area" + (", no face in the bottom band." if face_on else "."))
            return 0
        if violations:
            print(f"FAIL: {len(violations)} violating frame/edge pairs")
            for t, edge, n in violations:
                print(f"  {t:7.2f}s  {edge:<6}  ~{n} ink px outside the safe area")
            edges = sorted({e for _, e, _ in violations})
            print(f"edges in breach: {', '.join(edges)}")
        if face_hits:
            print(f"FAIL: the face's lower third (mouth, chin) is below y={a.bottom} in "
                  f"{len(face_hits)} of {len(frames)} frames")
            for t, (x, y, w, h, which) in face_hits:
                print(f"  {t:7.2f}s  face    box y {y:.0f}..{y + h:.0f} ({which}), lower third from "
                      f"{y + 2 * h / 3:.0f}, {y + h - a.bottom:.0f} px into the covered band; "
                      f"mouth about y {y + 0.78 * h:.0f}")
            print("Lift the face (less headroom on top) so the mouth and chin clear the line in "
                  "every frame, including lean-ins, and fill the bottom with a faded extension.")
        print("Fix the layout and re-render. YouTube cannot swap the file on an "
              "existing video, so a breach that ships costs a re-upload.")
        return 1
    finally:
        if a.keep is None:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
