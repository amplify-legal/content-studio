#!/usr/bin/env python3
"""The slide-state timeline of the shared deck, read off the frames, not the transcript.

Why: a cut once left a slide reading "5 actions is all it takes" before the fourth action appeared, because the
spine was picked off the transcript and a transcript cannot see a reveal. This samples the deck region at 4 fps,
measures how much of the picture changed frame to frame, and records every change as a `slide` (a large change)
or a `reveal` (a card or a band appearing).

  python3 slides.py build [--config config.json]        -> <out>/slides.json (events: t, kind, delta)
  python3 slides.py audit <cut> [--config config.json]  -> every unit of the cut against the events

A unit that ends after a reveal but before the next slide change is cutting through a build: extend it to the
last reveal and the end of the sentence. Half-second sampling is too coarse for the final boundary (it put the
wrong build on screen for up to 0.8 s at every change on one stream): re-measure each change to the frame.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_config  # noqa: E402

FPS, W, H = 4, 192, 108
SLIDE_T, REVEAL_T, SETTLE = 0.20, 0.012, 0.6  # fraction of pixels changed; settle merges one step's frames


def share_windows(cfg):
    return [(L["start"], L["end"]) for L in cfg.get("layouts", []) if L["kind"] == "share"]


def build(cfg):
    dw, dh, dx, dy = cfg["share"]["deck_crop"]
    events = []
    for s0, s1 in share_windows(cfg):
        p = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-ss", str(s0), "-i", str(cfg["recording"]),
                              "-t", str(s1 - s0), "-vf", f"crop={dw}:{dh}:{dx}:{dy},scale={W}:{H},fps={FPS}",
                              "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
        prev, last_t, i = None, -9, 0
        while True:
            buf = p.stdout.read(W * H)
            if len(buf) < W * H:
                break
            f = np.frombuffer(buf, np.uint8).astype(np.int16)
            t = s0 + i / FPS
            i += 1
            if prev is not None:
                d = float((np.abs(f - prev) > 24).mean())
                if d > REVEAL_T and t - last_t > SETTLE:
                    events.append(dict(t=round(t, 2), kind="slide" if d > SLIDE_T else "reveal", delta=round(d, 3)))
                    last_t = t
                elif d > REVEAL_T:
                    last_t = t  # still moving: extend the settle window
            prev = f
        p.stdout.close()
        p.wait()
    out = cfg["out_dir"] / "slides.json"
    out.write_text(json.dumps(events, indent=0))
    print(len(events), "events:", sum(e["kind"] == "slide" for e in events), "slide changes,",
          sum(e["kind"] == "reveal" for e in events), "reveals ->", out)


def audit(cfg, cut):
    ev = json.loads((cfg["out_dir"] / "slides.json").read_text())
    wins = share_windows(cfg)
    print(f"{'unit':>18}  {'slide starts':>13}  inside / after the end on the same slide")
    for a, b in cfg["cuts"][cut]:
        win = next(((s0, s1) for s0, s1 in wins if s0 <= a < s1), None)
        if not win:
            continue
        slide_start = max([e["t"] for e in ev if e["kind"] == "slide" and e["t"] <= a], default=win[0])
        nxt_slide = min([e["t"] for e in ev if e["kind"] == "slide" and e["t"] > b], default=win[1])
        inside = [e for e in ev if a <= e["t"] <= b]
        after = [e for e in ev if b < e["t"] < nxt_slide]
        flag = "  <-- cuts through a build" if after else ""
        n_rev = len([e for e in inside if e["kind"] == "reveal"])
        print(f"{a:8.1f}-{b:7.1f}  {slide_start:13.1f}  {n_rev} reveals inside; after: {[e['t'] for e in after][:6]}{flag}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("op", choices=["build", "audit"])
    ap.add_argument("cut", nargs="?")
    ap.add_argument("--config", default=None)
    args = ap.parse_args()
    cfg = load_config(args.config, need_recording=args.op == "build")
    if args.op == "build":
        build(cfg)
    else:
        if not args.cut:
            ap.error("audit needs a cut name")
        audit(cfg, args.cut)


if __name__ == "__main__":
    main()
