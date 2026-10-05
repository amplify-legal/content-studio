#!/usr/bin/env python3
"""An animated title opener that RESOLVES onto a real frame of what comes next.

Why it works: the opener is rendered into the exact slot the live footage will occupy and dissolves onto a real
frame of the next shot (usually the deck's title slide as the share showed it). The hand-off to the real footage
is then invisible, and the only thing that changes at the cut is a face appearing. The animation is not the
point; the resolve is.

  python3 opener.py --slide renders/title-slide.png --duration 6 --out renders/opener-condensed.mp4 \
      --line "Your title," --line "on 2 or 3 lines" [--font fonts/Display.ttf] [--colour "#111111"]

Extract the slide frame from the recording first, at the exact second the live footage will cut in:
  ffmpeg -ss 645.9 -i raw/workshop.mp4 -frames:v 1 renders/title-slide.png

Then point the config's "overrides" block at the output so build.py uses it for the opening raw ranges, with
the voices running under it. The output carries no audio.

Timings (seconds into the opener): the title lines rise in from 0.7 s, staggered 0.32 s; the real slide fades in
over 1.3 s starting at --resolve-at (default: duration minus 1.5 s), so the last frames ARE the slide.
"""
import argparse
import subprocess
from pathlib import Path


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--slide", required=True, type=Path, help="a REAL frame of what comes next, at frame size")
    ap.add_argument("--duration", required=True, type=float)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--line", action="append", default=[], help="a title line (repeat for each line)")
    ap.add_argument("--font", type=Path, default=None, help="a display .ttf you hold a licence for")
    ap.add_argument("--size", type=int, default=110)
    ap.add_argument("--colour", default="#111111")
    ap.add_argument("--background", default="#F6F3EC")
    ap.add_argument("--x", type=int, default=330)
    ap.add_argument("--y", type=int, default=285)
    ap.add_argument("--pitch", type=int, default=121, help="line pitch in px, measured off the slide if it carries the title")
    ap.add_argument("--fps", type=int, default=25)
    ap.add_argument("--resolve-at", type=float, default=None)
    args = ap.parse_args()

    from PIL import Image, ImageDraw, ImageFont
    slide = Image.open(args.slide).convert("RGB")
    W, H = slide.size
    if args.font:
        font = ImageFont.truetype(str(args.font), args.size)
    else:
        try:
            font = ImageFont.load_default(size=args.size)
        except TypeError:  # older Pillow: fixed-size bitmap font
            font = ImageFont.load_default()
    bg = Image.new("RGB", (W, H), args.background)
    layers = []
    for txt in args.line:
        L = Image.new("RGBA", (W, args.size * 2), (0, 0, 0, 0))
        ImageDraw.Draw(L).text((0, 0), txt, font=font, fill=args.colour)
        layers.append(L)
    resolve_at = args.resolve_at if args.resolve_at is not None else max(0.0, args.duration - 1.5)
    n = int(round(args.duration * args.fps))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    # an explicit -t on the piped input as well as the output: nothing here can run past the duration
    p = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(args.fps), "-t", f"{args.duration:.3f}", "-i", "-",
                          "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
                          "-c:v", "libx264", "-crf", "16", "-t", f"{args.duration:.3f}", str(args.out)],
                         stdin=subprocess.PIPE)
    for i in range(n):
        t = i / args.fps
        im = bg.copy().convert("RGBA")
        for k, L in enumerate(layers):
            a = ease((t - (0.7 + k * 0.32)) / 0.75)
            if a <= 0:
                continue
            dy = int((1 - a) * 90)
            faded = L.copy()
            faded.putalpha(faded.getchannel("A").point(lambda v, a=a: int(v * a)))
            im.alpha_composite(faded, (args.x, args.y + k * args.pitch + dy))
        x = ease((t - resolve_at) / 1.3)
        frame = Image.blend(im.convert("RGB"), slide, x) if x > 0 else im.convert("RGB")
        p.stdin.write(frame.tobytes())
    p.stdin.close()
    p.wait()
    if p.returncode:
        raise SystemExit("ffmpeg failed")
    print(args.out, args.duration)


if __name__ == "__main__":
    main()
