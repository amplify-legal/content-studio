#!/usr/bin/env python3
"""Deep pass on a finished cut. Not spot samples: the WHOLE runtime.

  python3 check.py <cut> [--config config.json]   -> <out>/<cut>.check.json plus contact sheets

What it measures:
  - video and audio stream durations, and the drift between them (over 0.10 s is a finding)
  - a frame every 5 s across the whole runtime, tiled into contact sheets with timestamps
  - black stretches and frozen picture (freezedetect, 3 s)
  - silences over 1 s on the DELIVERED file (dead air hides from every visual check)
  - how much of the runtime has a caption on screen

A green report means the file is worth a person's time. It does not mean done: a person still watches it, and
the dense per-vector review (captions, seams, blur, layout, pacing, audio alone) still runs. See
content/reference/workshop-edit.md, section 11.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_config, probe_duration  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cut")
    ap.add_argument("--config", default=None)
    args = ap.parse_args()
    cfg = load_config(args.config, need_recording=False)
    out_dir = cfg["out_dir"]
    f = out_dir / f"{args.cut}.mp4"
    if not f.exists():
        raise SystemExit(f"not found: {f}. Run build.py finalize {args.cut} first.")
    vd, ad = probe_duration(f, "v:0"), probe_duration(f, "a:0")
    rep = {"file": str(f), "video_s": vd, "audio_s": ad, "av_diff_s": round(vd - ad, 3), "findings": []}
    if abs(vd - ad) > 0.10:
        rep["findings"].append(f"video and audio differ by {vd - ad:.3f}s")
    per, sheets = 60, []
    n = int(vd // 5) + 1
    for k in range(0, n, per):
        p = out_dir / f"{args.cut}.sheet{k // per:02d}.jpg"
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", str(k * 5), "-i", str(f), "-t", str(per * 5),
                        "-vf", "fps=1/5,scale=320:-1,drawtext=text='%{pts\\:hms}':x=4:y=4:fontsize=18:fontcolor=yellow"
                               ":box=1:boxcolor=black,tile=6x10", "-frames:v", "1", str(p)])
        sheets.append(str(p))
    rep["sheets"] = sheets
    log = subprocess.run(["ffmpeg", "-nostdin", "-v", "info", "-i", str(f), "-vf",
                          "blackdetect=d=1.0:pic_th=0.98,freezedetect=n=0.001:d=3", "-an", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    rep["black"] = re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", log)
    rep["freeze_start"] = re.findall(r"freeze_start: ([\d.]+)", log)
    rep["freeze_end"] = re.findall(r"freeze_end: ([\d.]+)", log)
    alog = subprocess.run(["ffmpeg", "-nostdin", "-v", "info", "-i", str(f), "-vn", "-af", "silencedetect=n=-50dB:d=1.0",
                           "-f", "null", "-"], capture_output=True, text=True).stderr
    rep["silences_over_1s"] = re.findall(r"silence_start: ([\d.]+)", alog)
    for kind in ("black", "freeze_start", "silences_over_1s"):
        if rep[kind]:
            rep["findings"].append(f"{len(rep[kind])} {kind.replace('_', ' ')}: check each is a designed card")
    ass_p = out_dir / f"{args.cut}.captions.ass"
    if ass_p.exists():
        def t(s):
            h, m, sec = s.split(":")
            return int(h) * 3600 + int(m) * 60 + float(sec)
        cov = set()
        for line in ass_p.read_text().splitlines():
            if line.startswith("Dialogue"):
                a, b = line.split(",")[1:3]
                cov.update(range(int(t(a)), int(t(b)) + 1))
        rep["caption_seconds_at_1x"] = len(cov)
        rep["caption_share"] = round(len(cov) / max(vd * cfg.get("speed", 1.0), 1e-6), 3)
    rep["status"] = "green" if not rep["findings"] else "red"
    (out_dir / f"{args.cut}.check.json").write_text(json.dumps(rep, indent=1))
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
