#!/usr/bin/env python3
"""
check_frames.py: the frames a checker reads at full resolution, for a checker that did not build the short.

    PYTHONDONTWRITEBYTECODE=1 python3 check_frames.py <render id> [<render id> ...]

For each id (any `<OUT>/<slug>/<id>.mp4`, OUT from paths.py): frames every 0.5 s through the first 5 s (the hook and
its end), every 0.5 s through the last 6 s (the credit), and 1 a second between, written as 1080x1920 PNGs to
<WORKROOT>/../check/<id>/r<mtime>-<size>/t-<ss.s>.png, plus a 3-column contact sheet `sheet.jpg` of the same frames at
half size, and `src.json` naming the render they came from. Prints the folder.

The folder is named by the render's mtime and size, never its id alone: on the build this came from, a first round
of checks read a re-render through the FIRST render's frames, because an existing frame was kept and the folder was
keyed on the id (`content/reference/edit-lab/README.md`, trap 19). `check/<id>/CURRENT.txt` names the folder of
the latest call. Idempotent per render; never deletes. ffmpeg runs with -nostdin and a bounded wait.
"""
import json
import os as _os
import subprocess
import sys
import sys as _sys
from pathlib import Path

from PIL import Image

_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import paths as PATHS  # noqa: E402

SHORTS = PATHS.OUT
CHECK = PATHS.WORKROOT.parent / "check"


def find(rid):
    if not SHORTS.exists():
        return None
    for d in SHORTS.iterdir():
        f = d / f"{rid}.mp4"
        if f.exists():
            return f
    return None


def dur(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(f)], capture_output=True, text=True, timeout=60)
    return float(json.loads(r.stdout)["format"]["duration"])


def times(d):
    ts = [i * 0.5 for i in range(0, 11)]                      # 0 .. 5 s
    ts += [float(t) for t in range(6, max(6, int(d - 6)))]    # 6 .. d-6, 1 a second
    k = max(0.0, d - 6.0)
    ts += [round(k + i * 0.5, 2) for i in range(0, 13) if k + i * 0.5 < d - 0.05]
    return sorted({round(t, 2) for t in ts if t < d - 0.03})


def main(ids):
    if not ids:
        print(__doc__)
        return 2
    for rid in ids:
        f = find(rid)
        if not f:
            print("no render:", rid, "under", SHORTS)
            continue
        st = f.stat()
        out = CHECK / rid / f"r{int(st.st_mtime)}-{st.st_size}"
        out.mkdir(parents=True, exist_ok=True)
        (out / "src.json").write_text(json.dumps({"path": str(f), "mtime": st.st_mtime, "size": st.st_size}))
        (CHECK / rid / "CURRENT.txt").write_text(str(out) + "\n")
        d = dur(f)
        frames = []
        for t in times(d):
            png = out / f"t-{t:05.1f}.png"
            if not png.exists():
                subprocess.run(["ffmpeg", "-nostdin", "-y", "-v", "error", "-ss", f"{t:.3f}", "-i", str(f), "-frames:v", "1", str(png)], timeout=120)
            if png.exists():
                frames.append((t, png))
        cols, w, h = 3, 540, 960
        rows = (len(frames) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * w, max(1, rows) * (h + 28)), (20, 20, 20))
        from PIL import ImageDraw
        dr = ImageDraw.Draw(sheet)
        for i, (t, png) in enumerate(frames):
            im = Image.open(png).convert("RGB").resize((w, h))
            x, y = (i % cols) * w, (i // cols) * (h + 28)
            sheet.paste(im, (x, y))
            dr.text((x + 8, y + h + 6), f"{t:.1f} s", fill=(240, 240, 240))
        sheet.save(out / "sheet.jpg", quality=82)
        print(out, f"{len(frames)} frames, {d:.2f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
