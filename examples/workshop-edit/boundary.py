#!/usr/bin/env python3
"""Find cut points that land on speech, and move them to measured quiet.

Why: cuts picked off a transcript leave words cut off and words that run long. Two signals, combined:
  1. The transcript's word spans say WHICH word a boundary lands in.
  2. Audio energy (20 ms RMS on 16 kHz mono of the tape) says whether sound is actually there.
     Transcribers attach the trailing pause to the word, so snapping to a word's span would put back
     the dead air a cut was meant to remove.
A boundary moves only when energy says speech is on it, and it moves to the nearest measured quiet,
walking outward from the cut in 20 ms steps (capped at 1.5 s), with a 0.05 s pad.

  python3 boundary.py report [--config config.json]     # every boundary of every cut that sits on speech
  from boundary import Snapper                          # used by build.py plan
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_config  # noqa: E402

SR, WIN = 16000, 0.02
THR_DB, QUIET_RUN, PAD, MAX_WALK = -38.0, 3, 0.05, 1.5


class Snapper:
    def __init__(self, cfg):
        self.cfg = cfg
        self.pcm = cfg["out_dir"] / "mono16k.pcm"
        self._env = None
        self._words = None

    def env(self):
        """RMS envelope in dBFS, one value per 20 ms window."""
        if self._env is None:
            if not self.pcm.exists():
                subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(self.cfg["recording"]), "-vn",
                                "-ac", "1", "-ar", str(SR), "-f", "s16le", str(self.pcm)], check=True)
            x = np.frombuffer(self.pcm.read_bytes(), dtype=np.int16).astype(np.float32) / 32768.0
            n = int(SR * WIN)
            m = len(x) // n
            rms = np.sqrt((x[:m * n].reshape(m, n) ** 2).mean(axis=1)) + 1e-9
            self._env = 20 * np.log10(rms)
        return self._env

    def loud(self, t0, t1):
        e = self.env()
        a, b = max(0, int(t0 / WIN)), min(len(e), int(np.ceil(t1 / WIN)))
        return b > a and float(e[a:b].max()) > THR_DB

    def quiet_at(self, i):
        e = self.env()
        return i >= 0 and i + QUIET_RUN <= len(e) and bool((e[i:i + QUIET_RUN] < THR_DB).all())

    def words(self):
        if self._words is None:
            p = self.cfg.get("transcript")
            if p and Path(p).exists():
                self._words = [(w["start"], w["end"], w["text"]) for w in json.loads(Path(p).read_text())["words"]
                               if w.get("type", "word") == "word"]
            else:
                self._words = []
        return self._words

    def word_at(self, t):
        return " ".join(w[2] for w in self.words() if w[0] - 0.05 < t < w[1] + 0.05) or "(sound)"

    def snap_out(self, t):
        """Cut-out point: if sound is on the last 60 ms, walk forward to quiet."""
        if not self.loud(t - 0.06, t):
            return t, None
        i = int(t / WIN)
        for k in range(int(MAX_WALK / WIN)):
            if self.quiet_at(i + k):
                return round((i + k) * WIN + PAD, 3), self.word_at(t)
        return t, None

    def snap_in(self, t):
        """Cut-in point: if sound is on the first 60 ms, walk backward to quiet."""
        if not self.loud(t, t + 0.06):
            return t, None
        i = int(t / WIN)
        for k in range(int(MAX_WALK / WIN)):
            j = i - k - QUIET_RUN
            if self.quiet_at(j):
                return round((j + QUIET_RUN) * WIN - PAD, 3), self.word_at(t)
        return t, None

    def snap_units(self, units):
        """units: [(a, b, ...)] on the raw timeline, in order. Only REAL cuts move: the first in, the last out,
        and any edge with a gap to its neighbour. An edge where the next unit starts exactly where this one ends
        is a beat or layout seam with continuous audio, not a cut, and is left alone."""
        out, log = [], []
        n = len(units)
        for i, u in enumerate(units):
            a, b, rest = u[0], u[1], tuple(u[2:])
            cut_in = i == 0 or abs(units[i - 1][1] - a) > 0.002
            cut_out = i == n - 1 or abs(units[i + 1][0] - b) > 0.002
            a2, wa = self.snap_in(a) if cut_in else (a, None)
            b2, wb = self.snap_out(b) if cut_out else (b, None)
            if wa:
                log.append(("in", a, a2, wa))
            if wb:
                log.append(("out", b, b2, wb))
            if b2 - a2 < 0.4:
                a2, b2 = a, b
            out.append((a2, b2) + rest)
        for i in range(1, len(out)):  # keep contiguity across seams
            if abs(units[i][0] - units[i - 1][1]) <= 0.002:
                out[i] = (out[i - 1][1],) + tuple(out[i][1:])
        return out, log


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("op", choices=["report"])
    ap.add_argument("--config", default=None)
    args = ap.parse_args()
    cfg = load_config(args.config)
    sn = Snapper(cfg)
    total = 0
    for cut, units in cfg.get("cuts", {}).items():
        _, log = sn.snap_units([tuple(x) for x in units])
        for kind, t, t2, txt in log:
            print(f"{cut:16s} {kind:3s} {t:8.2f} -> {t2:8.2f}  on \"{txt}\"")
            total += 1
    print(f"\n{total} boundaries sit on measured speech")


if __name__ == "__main__":
    main()
