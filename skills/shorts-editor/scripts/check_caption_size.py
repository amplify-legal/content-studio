#!/usr/bin/env python3
"""Caption floor gate for any 1080x1920 short.

The floor: Montserrat 78px at 1080 wide, which renders a capital H 35px tall. 52px was far too small in
the hand. A research finding or a review that wants a different size is reported as a conflict for a person
to settle; it never moves this number on its own. The floor once lived in one episode's build script instead
of in the skill, and 12 of 15 renders repeated the miss three days later.

Two modes:
  --style "<ASS Style: line>" [--fontsdir DIR]   exact: renders H, measures cap height, fails under 35px
  <render.mp4> [--band 1100 1750] [--out DIR]   for eyes, not a gate: writes <name>-caption-375.png, the caption
                                                 band of the inkiest frame scaled to 375px wide, so a person reads
                                                 it at phone size. Ink-run measurement is fooled by a face or a
                                                 shirt in the band, so it prints the numbers and never passes or
                                                 fails on them.
The gate is --style. Exit 1 means fix the size and re-render.
"""
import argparse, os, pathlib, subprocess, sys, tempfile
try:
    import numpy as np
except ImportError:
    sys.exit("numpy is not installed. Run:  python3 -m pip install numpy\n"
             "(inside the virtual environment SETUP.md makes).")

CAP_FLOOR_PX = 35      # capital H, 1080-wide frame, = Montserrat 78. Raised by a person, never by a script.

STYLE_EXAMPLE = ("Style: Brand,Montserrat,78,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,"
                 "0,0,0,0,100,100,0,0,1,3,0,2,60,60,120,1")

def style_name(style_line):
    """The Name field of an ASS Style: line. Says what it needs instead of raising."""
    if not style_line.strip().lower().startswith("style:"):
        sys.exit("--style wants a whole ASS Style: line, not just a name.\n"
                 f"For example:\n  --style \"{STYLE_EXAMPLE}\"\n"
                 "It is the line your caption renderer writes into its .ass file; copy that one.")
    fields = style_line.split(":", 1)[1].split(",")
    name = fields[0].strip()
    if not name or len(fields) < 3:
        sys.exit("That Style: line is missing fields. It needs at least Name, Fontname and "
                 "Fontsize, comma separated.\n"
                 f"For example:\n  --style \"{STYLE_EXAMPLE}\"")
    return name

def cap_height(style_line, fontsdir):
    name = style_name(style_line)
    ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
{style_line}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:01.00,{name},,0,0,0,,{{\\pos(540,960)}}H
"""
    tmp = pathlib.Path("_capcheck.ass"); tmp.write_text(ass)
    fd = f":fontsdir={fontsdir}" if fontsdir else ""
    out = subprocess.run(f'ffmpeg -nostdin -v error -f lavfi -t 1 -i color=c=black:s=1080x1920:r=1 -vf "ass=_capcheck.ass{fd}" -frames:v 1 -f rawvideo -pix_fmt gray -', shell=True, capture_output=True).stdout
    tmp.unlink(missing_ok=True)
    if len(out) < 1920 * 1080:
        sys.exit("ffmpeg rendered no frame from that style line, so there is nothing to measure.\n"
                 "Usual causes: ffmpeg is not installed or has no libass, or the Style: line is "
                 "malformed.\n"
                 "Check with:  ffmpeg -filters | grep ass\n"
                 f"Known-good line:\n  --style \"{STYLE_EXAMPLE}\"")
    fr = np.frombuffer(out[: 1920 * 1080], np.uint8).reshape(1920, 1080)
    rows = np.where((fr > 128).sum(axis=1) > 0)[0]
    return int(rows.max() - rows.min() + 1) if len(rows) else 0

def frames(path):
    out = subprocess.run(f'ffmpeg -nostdin -v error -i "{path}" -vf fps=1,scale=1080:1920 -f rawvideo -pix_fmt gray -', shell=True, capture_output=True).stdout
    n = len(out) // (1080 * 1920)
    return np.frombuffer(out[: n * 1080 * 1920], np.uint8).reshape(n, 1920, 1080)

def tallest_line(band, bright=200):
    ink = (band > bright).sum(axis=1) > 3
    best = run = 0
    for v in ink:
        run = run + 1 if v else 0
        best = max(best, run)
    return best

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("render", nargs="?")
    ap.add_argument("--style")
    ap.add_argument("--fontsdir")
    ap.add_argument("--band", nargs=2, type=int, default=[1100, 1750])
    ap.add_argument("--out", help="folder for the 375px PNG (default: $CLAUDE_SCRATCHPAD_DIR, else the system temp folder; never the working directory)")
    a = ap.parse_args()
    if a.style:
        h = cap_height(a.style, a.fontsdir)
        ok = h >= CAP_FLOOR_PX
        print(f"cap height {h}px (floor {CAP_FLOOR_PX}px = Montserrat 78 at 1080): {'OK' if ok else 'TOO SMALL'}")
        sys.exit(0 if ok else 1)
    if not a.render:
        ap.error("give a render or --style")
    fr = frames(a.render)
    y0, y1 = a.band
    heights = [tallest_line(f[y0:y1]) for f in fr]
    with_ink = [h for h in heights if h > 0]
    if not with_ink:
        print("no caption ink found in the band; check --band"); sys.exit(1)
    typical = int(np.median(with_ink))
    i = int(np.argmax(heights))
    # never "." : the working directory is usually the project repo, and a check that drops
    # PNGs there gets them committed. Fall back to the system temp folder instead.
    outdir = pathlib.Path(a.out or os.environ.get("CLAUDE_SCRATCHPAD_DIR") or tempfile.gettempdir())
    outdir.mkdir(parents=True, exist_ok=True)
    png = (outdir / (pathlib.Path(a.render).stem + "-caption-375.png")).as_posix()
    subprocess.run(f'ffmpeg -nostdin -v error -y -ss {i} -i "{a.render}" -frames:v 1 -vf "crop=1080:{y1-y0}:0:{y0},scale=375:-1" "{png}"', shell=True)
    print(f"ink runs in the band: median {typical}px over {len(with_ink)} frames (a number for context, not a verdict: a face or a shirt in the band inflates it)")
    print(f"read it at phone width: {png}")
    sys.exit(0)

if __name__ == "__main__":
    main()
