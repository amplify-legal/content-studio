#!/usr/bin/env python3
"""Prove WHO is speaking in a clip range, from the picture, not the transcript.

Why this exists: the transcript is a search index, never evidence. A line spoken by
someone else on the tape (a second voice, a quote read on screen, a playback) reads in
whisper exactly like the on-camera speaker saying it. The real incident measured a
mouth-motion score of 2.1 on the misattributed line against 13-22 on ranges where the
speaker genuinely talks. Anything that will be published as THEIR self-description,
credential or claim gets checked here BEFORE the EDL is written.

Method (dependency-light on purpose: ffmpeg + PIL only):
  sample frames in the range, crop the mouth region (center-lower third of a face box
  if one is given, otherwise a fixed lower-center crop), and compute the mean
  frame-to-frame absolute pixel delta in that crop. A talking mouth moves; a still
  listener's does not. Compare the range against a CALIBRATION range known to be the
  target speaker talking. Threshold = HALF the calibration score.

Usage:
  python verify_speaker.py <video> --range 12.4-18.9 --calibration 3.0-8.0
        [--face X,Y,W,H]      # face box in source pixels; mouth = its lower-center third
        [--fps 12]            # sampling rate (default 12)
        [--keep DIR]          # keep the extracted crops for eyeballing

Exit 0 = the range moves like real speech (>= half the calibration score).
Exit 1 = SUSPECT: the mouth is not moving like the calibration. Do NOT attribute
         this line to the speaker without looking at frames yourself.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

try:
    from PIL import Image
except ImportError:
    sys.exit("PIL (Pillow) is required: pip install Pillow")


def parse_range(s):
    if "-" not in s:
        raise argparse.ArgumentTypeError(f"range must be START-END, got {s!r}")
    a, b = s.rsplit("-", 1)
    a, b = float(a), float(b)
    if b <= a:
        raise argparse.ArgumentTypeError(f"range end must exceed start: {s!r}")
    return (a, b)


def parse_face(s):
    parts = [int(float(p)) for p in s.replace(" ", "").split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("--face wants X,Y,W,H")
    return tuple(parts)


def probe_size(video):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", video],
        capture_output=True, text=True).stdout.strip()
    w, h = out.split("x")[:2]
    return int(w), int(h)


def mouth_box(vw, vh, face):
    """Mouth region. With a face box: its lower-center third. Without: a fixed
    lower-center crop of the frame, which is where a 9:16 talking head sits."""
    if face:
        fx, fy, fw, fh = face
        mw = int(fw * 0.55)
        mh = int(fh * 0.33)
        mx = fx + (fw - mw) // 2
        my = fy + int(fh * 0.60)
    else:
        mw = int(vw * 0.24)
        mh = int(vh * 0.12)
        mx = (vw - mw) // 2
        my = int(vh * 0.62)
    mx = max(0, min(mx, vw - 1))
    my = max(0, min(my, vh - 1))
    mw = max(8, min(mw, vw - mx))
    mh = max(8, min(mh, vh - my))
    return mx, my, mw, mh


def extract(video, start, end, box, fps, outdir):
    x, y, w, h = box
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-t", str(end - start),
         "-i", video, "-vf", f"fps={fps},crop={w}:{h}:{x}:{y},format=gray",
         os.path.join(outdir, "%05d.png")],
        check=True)
    return sorted(f for f in os.listdir(outdir) if f.endswith(".png"))


def motion_score(video, rng, box, fps, keep=None):
    """Mean frame-to-frame absolute pixel delta in the mouth crop."""
    tmp = keep or tempfile.mkdtemp(prefix="vspk_")
    os.makedirs(tmp, exist_ok=True)
    try:
        frames = extract(video, rng[0], rng[1], box, fps, tmp)
        if len(frames) < 2:
            return 0.0, len(frames)
        prev = None
        deltas = []
        for f in frames:
            cur = Image.open(os.path.join(tmp, f)).convert("L").tobytes()
            if prev is not None:
                n = min(len(prev), len(cur))
                deltas.append(sum(abs(cur[i] - prev[i]) for i in range(n)) / n)
            prev = cur
        return (sum(deltas) / len(deltas) if deltas else 0.0), len(frames)
    finally:
        if keep is None:
            shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--range", required=True, type=parse_range,
                    help="the clip range under suspicion, START-END in seconds")
    ap.add_argument("--calibration", required=True, type=parse_range,
                    help="a range KNOWN to be the target speaker talking, START-END")
    ap.add_argument("--face", type=parse_face, default=None,
                    help="face box X,Y,W,H in source pixels (mouth = its lower-center third)")
    ap.add_argument("--fps", type=int, default=12)
    ap.add_argument("--keep", default=None, help="directory to keep the crops in")
    a = ap.parse_args()

    if not os.path.exists(a.video):
        sys.exit(f"no such file: {a.video}")

    vw, vh = probe_size(a.video)
    box = mouth_box(vw, vh, a.face)
    print(f"source {vw}x{vh}  mouth crop x={box[0]} y={box[1]} w={box[2]} h={box[3]}"
          + ("  (from --face)" if a.face else "  (fixed lower-center; pass --face to aim it)"))

    keep_c = os.path.join(a.keep, "calibration") if a.keep else None
    keep_r = os.path.join(a.keep, "range") if a.keep else None
    cal, ncal = motion_score(a.video, a.calibration, box, a.fps, keep_c)
    rng, nrng = motion_score(a.video, a.range, box, a.fps, keep_r)

    thresh = cal / 2.0
    ratio = (rng / cal) if cal else 0.0
    print(f"calibration {a.calibration[0]}-{a.calibration[1]}s : score {cal:.2f}  ({ncal} frames)")
    print(f"range       {a.range[0]}-{a.range[1]}s : score {rng:.2f}  ({nrng} frames)")
    print(f"ratio {ratio:.2f}   threshold {thresh:.2f} (half the calibration)")

    if cal < 1.0:
        print("INCONCLUSIVE: the calibration range barely moves either. Pick a calibration "
              "range where the speaker is clearly talking, or aim the crop with --face.")
        return 1
    if rng >= thresh:
        print("PASS: the mouth moves like real speech in this range.")
        return 0
    print("SUSPECT: the mouth is not moving like the calibration (the 2.1-vs-13-22 shape "
          "of the misattributed-line incident). Do NOT attribute this line to the speaker. "
          "Extract frames and look before writing the EDL.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
