"""Transcribe a video with Deepgram nova-3 (word-level timestamps).

**THE DECLARED FALLBACK, not the default.** ElevenLabs Scribe (`transcribe.py`) is the
route. Reach for this one when Scribe is unavailable: no key, the plan's credits are out,
or the API is down. Whisper (`transcribe_local.py`) drops below this to last resort, for
no network and no key at all.

Why Deepgram and not whisper as the fallback, measured over about 2 hours of real tape
(3 tapes: on one all 3 engines ran, on the others only 2):

| | Deepgram nova-3 + keyterms | whisper large-v3 |
|---|---|---|
| proper nouns, tape 1 (all 3 engines ran) | 16/17 | 11/17 |
| proper nouns, tape 2 (2 engines ran) | 47/47 | 25/47 |
| proper nouns, tape 3 (whisper never ran) | 21/21 | not run |
| word starts, median error | 60 to 65 ms | 170 ms |
| word ends, median error | 125 to 160 ms | 170 ms |
| cost | paid, check the provider's pricing page | free |

**Two things this engine does that the pipeline has to know about.**

1. **Its word END times are not acoustic offsets.** 90 percent of its inter-word gaps are
   exactly 0, so a word's `end` is really the next word's start. Its word STARTS are better
   than Scribe's. So prefer starts when you can, and know what the ends are.

   End snapping is ON by default: each end is rewritten to the nearest measured energy
   offset, one pass over the audio, no model call. **Measured** on 12 minutes of a real
   tape, 2,000 words aligned by text against Scribe v2 as an independent reference:

   |  | signed median | median absolute | within 50 ms | within 100 ms |
   |---|---|---|---|---|
   | raw Deepgram ends | **+45.0 ms late** | 60.5 ms | 41.1% | 72.8% |
   | snapped | **+9.0 ms** | 59.0 ms | 42.8% | 73.6% |

   So snapping buys ONE thing and it is worth having: it removes a 45 ms systematic late
   bias, which is the part that clips a syllable off every outpoint the same way. It does
   NOT meaningfully tighten the scatter. `--raw-ends` turns it off.

   **A warning for whoever measures this next.** Scoring the snapped ends with the same
   energy detector that produced them returns a median error of 0.0 ms and 96.6 percent
   within 50 ms. That number is circular and means nothing. The table above is scored
   against Scribe, which never saw the snapper. A first pass at this also matched words by
   nearest timestamp rather than by text, which at 2.7 words a second just measures word
   density; align the sequences by their text.
2. **Numbers come back as words** ("twenty seven years", "ninety five percent") where Scribe
   writes digits. Captions show numerals as digits, so any caption built on this output
   needs a number pass that Scribe output does not.
3. **Its speaker labels are not good enough to burn a name from.** Diarization measured 87
   percent overall and only 72 percent on the guest. Use them to search, never to caption.

Output is the SAME SHAPE `transcribe.py` writes, so `gen.py`, `captions.py` and the verify
loop take it unchanged:
{ "words": [ { "text": "...", "start": 0.12, "end": 0.34, "type": "word",
               "speaker_id": "speaker_0" }, ... ] }
plus a `_engine` block naming what produced it, because an engine is declared in the file's
own header and never inferred: no engine is ever a silent default.

API key: reads DEEPGRAM_API_KEY from a `.env` file in the current directory, next to this
script, or in any parent folder up to the project root, then from the environment. NEVER
hard-code it.

Cached: if the output JSON already exists the upload is skipped, unless --force. The cache
is keyed on the FILENAME, exactly like `transcribe.py`, so a pipeline that rewrites the same
name with new content must pass --force or it will read back the previous run.

Usage:
    python scripts/transcribe_deepgram.py <video_path>
    python scripts/transcribe_deepgram.py <video_path> --edit-dir edit
    python scripts/transcribe_deepgram.py <video_path> --keyterms-file build/keyterms.txt
    python scripts/transcribe_deepgram.py <video_path> --raw-ends
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.parse
import wave
from pathlib import Path

import requests


DEEPGRAM_URL = "https://api.deepgram.com/v1/listen"


def load_api_key() -> str:
    here = Path(__file__).resolve()
    candidates = [Path.cwd() / ".env", here.parent / ".env"]
    # The skill lives at <project>/.claude/skills/shorts-editor/scripts/, and the
    # key is in <project>/.env, which is ABOVE .claude. Walk up from both the
    # current folder and this file, and stop at the folder that HOLDS .claude or
    # .git (breaking at .claude itself stops one directory short).
    for up in list(Path.cwd().resolve().parents) + list(here.parents):
        candidates.append(up / ".env")
        if (up / ".claude").is_dir() or (up / ".git").is_dir():
            break
    for candidate in candidates:
        if not candidate.exists():
            continue
        for line in candidate.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            if k.strip() == "DEEPGRAM_API_KEY":
                return v.strip().strip('"').strip("'")
    v = os.environ.get("DEEPGRAM_API_KEY", "")
    if not v:
        sys.exit(
            "DEEPGRAM_API_KEY not found.\n"
            "  This is the FALLBACK transcriber. Try scripts/transcribe.py first:\n"
            "  ElevenLabs Scribe is the route and it is more accurate on word ends.\n"
            "  For Deepgram, put a line  DEEPGRAM_API_KEY=...  in the project .env\n"
            "  With neither key and no network, scripts/transcribe_local.py runs\n"
            "  faster-whisper offline. It is measurably worse than both; spot-read\n"
            "  every proper noun before any caption burns."
        )
    return v


def extract_audio(video_path: Path, dest: Path) -> None:
    cmd = [
        "ffmpeg", "-y", "-i", str(video_path),
        "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le",
        str(dest),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def call_deepgram(audio_path: Path, api_key: str, language="en", model="nova-3",
                  keyterms=None, diarize=True) -> dict:
    params = [
        ("model", model), ("smart_format", "true"), ("punctuate", "true"),
        ("utterances", "true"), ("filler_words", "true"),
    ]
    if language:
        params.append(("language", language))
    if diarize:
        params.append(("diarize", "true"))

    # Keyterms are not optional here. Measured per tape: nova-3 with keyterms
    # scored 21 of 21 confirmed proper-noun sites on one tape and 16 of 17 on
    # another, and the same model bare scored 12 of 21 and 13 of 17. Keyterms cost
    # a little extra per minute: check the provider's pricing page.
    # NOTE nova-3 takes `keyterm`. The older nova-2 `keywords=term:boost` form is
    # deliberately NOT offered: measured, a x10 boost INSERTED the keyword where
    # nobody said it, 6 times in 18 minutes (a product name replacing "host" in
    # the guest's own introduction).
    for t in (keyterms or []):
        params.append(("keyterm", t))

    url = DEEPGRAM_URL + "?" + urllib.parse.urlencode(params)
    with open(audio_path, "rb") as f:
        resp = requests.post(
            url,
            headers={"Authorization": f"Token {api_key}",
                     "Content-Type": "audio/wav"},
            data=f.read(),
            timeout=1800,
        )
    if resp.status_code != 200:
        raise RuntimeError(f"Deepgram returned {resp.status_code}: {resp.text[:500]}")
    return resp.json()


def energy_offsets(wav_path: Path, words: list, search=0.40) -> int:
    """Rewrite each word's END to the nearest real energy offset in the audio.

    Deepgram runs a word's end into the next word's start rather than reporting
    where speech stopped, so a cut taken from a raw `end` lands up to 160 ms late.
    A threshold-crossing detector on 20 ms RMS windows at a 5 ms hop. It passed
    a nudge self-test (shift a known boundary, check it comes back) on 3 real
    tapes. Returns how many ends it moved.
    """
    import array
    import math
    hop, win, hold = 0.005, 0.020, 0.030
    w = wave.open(str(wav_path))
    sr, n = w.getframerate(), w.getnframes()
    raw = array.array("h", w.readframes(n))
    w.close()
    hop_n, win_n = int(sr * hop), int(sr * win)
    frames = max(0, 1 + (len(raw) - win_n) // hop_n)
    if frames < 32:
        return 0

    try:                                   # numpy when it is here: ~100x faster
        import numpy as np
        a = np.frombuffer(raw, dtype=np.int16).astype(np.float64)
        wins = np.lib.stride_tricks.sliding_window_view(a, win_n)[::hop_n][:frames]
        rms = np.sqrt((wins ** 2).mean(axis=1)) + 1e-6
        db = (20 * np.log10(rms)).tolist()
    except Exception:                      # pure Python, no extra dependency
        db = []
        step = 4                           # every 4th sample is plenty at 16 kHz
        k = len(range(0, win_n, step))
        for i in range(frames):
            s = i * hop_n
            acc = 0
            for v in raw[s:s + win_n:step]:
                acc += v * v
            rms = math.sqrt(acc / k) + 1e-6
            db.append(20 * math.log10(rms))

    def nearest_offset(t):
        lo = max(0, int((t - search) / hop))
        hi = min(len(db), int((t + search) / hop) + 1)
        if hi - lo < 16:
            return None
        ctx = sorted(db[max(0, int((t - 0.8) / hop)):
                        min(len(db), int((t + 0.8) / hop) + 1)])
        if not ctx:
            return None
        floor, peak = ctx[len(ctx) // 10], ctx[max(0, len(ctx) * 9 // 10 - 1)]
        if peak - floor < 6:
            return None
        thr = floor + max(6.0, 0.35 * (peak - floor))
        hold_n = max(1, int(hold / hop))
        best = None
        for i in range(lo + 1, hi - hold_n):
            if db[i - 1] > thr and not any(d > thr for d in db[i:i + hold_n]):
                if best is None or abs(i * hop - t) < abs(best - t):
                    best = i * hop
        return best

    moved = 0
    for i, word in enumerate(words):
        nxt = words[i + 1]["start"] if i + 1 < len(words) else None
        # The clamp runs on EVERY word, including the ones the detector cannot
        # place. The first version of this put it after `if e is None: continue`,
        # so a word the detector missed kept Deepgram's raw end and never got
        # clamped: measured on the 3 bench tapes that left 2, 5 and 10 ends
        # running PAST the next word's start, the worst by 665 ms, and make_edl.py
        # writes that end as an out-point.
        lo = word["start"] + 0.02
        hi = (nxt - 0.005) if nxt is not None else word["end"] + search
        if hi <= lo:
            # the next word starts inside this one's floor; nothing safe to do
            continue
        e = nearest_offset(word["end"])
        if e is None:
            e = word["end"]
        e = max(lo, min(e, hi))
        if abs(e - word["end"]) > 0.005:
            word["end"] = round(e, 3)
            moved += 1
    return moved


def to_scribe_shape(payload: dict, snapped: int, meta: dict) -> dict:
    """The shape gen.py, captions.py and the verify loop already read."""
    alt = payload["results"]["channels"][0]["alternatives"][0]
    words = []
    for w in alt.get("words", []):
        entry = {
            "text": w.get("punctuated_word", w["word"]),
            "start": w["start"],
            "end": w["end"],
            "type": "word",
        }
        if "speaker" in w:
            entry["speaker_id"] = f"speaker_{w['speaker']}"
        words.append(entry)
    dur = payload.get("metadata", {}).get("duration")
    return {
        "words": words,
        "text": alt.get("transcript", ""),
        "audio_duration_secs": dur,
        # An engine is DECLARED in the file's own header, never inferred. Whisper
        # was a declared fallback and never a silent default; so is this.
        "_engine": {
            "engine": "deepgram",
            "role": "declared fallback, NOT the default. The default is ElevenLabs "
                    "Scribe scribe_v2 via transcribe.py.",
            "word_ends": ("snapped to measured energy offsets" if snapped
                          else "RAW Deepgram ends: late by 125 to 160 ms median, "
                               "do not cut on them"),
            "ends_moved": snapped,
            "numerals": "Deepgram writes numbers as words; a number pass is needed "
                        "before any caption burns",
            **meta,
        },
    }


def transcribe_one(video: Path, edit_dir: Path, api_key: str, language="en",
                   model="nova-3", keyterms=None, force=False,
                   snap_ends=True, diarize=True) -> Path:
    transcripts_dir = edit_dir / "transcripts"
    transcripts_dir.mkdir(parents=True, exist_ok=True)
    out_path = transcripts_dir / f"{video.stem}.json"
    if out_path.exists() and not force:
        # All 3 engines write <stem>.json to the same place, so a cache hit here
        # can be ANOTHER engine's words. Returning them would be the silent
        # default the whole routing rule exists to prevent: the run would say
        # "cached", the file would say Scribe, and the caller would believe it
        # had fallen back. So the cache only counts when this engine wrote it.
        try:
            prev = json.loads(out_path.read_text())
            was = prev.get("_engine", {}).get("engine")
        except Exception:
            was = None
        if was == "deepgram":
            print(f"cached: {out_path.name}  (--force to re-transcribe)")
            return out_path
        print(f"  {out_path.name} exists but was written by "
              f"{was or 'another engine (no _engine header)'}; re-transcribing "
              f"with Deepgram rather than handing back its words", flush=True)

    print("  FALLBACK ENGINE: Deepgram. The route is ElevenLabs Scribe "
          "(transcribe.py); say why this one is running.", flush=True)
    print(f"  extracting audio from {video.name}", flush=True)
    t0 = time.time()
    with tempfile.TemporaryDirectory() as tmp:
        audio = Path(tmp) / f"{video.stem}.wav"
        extract_audio(video, audio)
        size_mb = audio.stat().st_size / (1024 * 1024)
        print(f"  uploading {video.stem}.wav ({size_mb:.1f} MB) to {model}"
              f"{' with ' + str(len(keyterms)) + ' keyterms' if keyterms else ''}",
              flush=True)
        payload = call_deepgram(audio, api_key, language, model, keyterms, diarize)
        alt = payload["results"]["channels"][0]["alternatives"][0]
        words = [{"start": w["start"], "end": w["end"]} for w in alt.get("words", [])]
        moved = 0
        if snap_ends and words:
            print("  snapping word ends to measured energy offsets", flush=True)
            moved = energy_offsets(audio, words)
            for src, w in zip(words, alt.get("words", [])):
                w["end"] = src["end"]

    out = to_scribe_shape(payload, moved if snap_ends else 0, {
        "model": model, "keyterms": keyterms or [],
        "language": language, "diarize": diarize,
    })
    if not out["words"]:
        sys.exit(f"Deepgram returned 200 but 0 words for {video.name}; nothing "
                 f"written. Check the file has an audio track and that --language "
                 f"matches what is spoken. Writing an empty transcript would cache "
                 f"it and then crash captions.py on ws[-1].")
    out_path.write_text(json.dumps(out, indent=2))
    dt = time.time() - t0
    kb = out_path.stat().st_size / 1024
    print(f"  saved: {out_path.name} ({kb:.1f} KB) in {dt:.1f}s")
    print(f"    words: {len(out['words'])}"
          + (f", {moved} word ends snapped" if moved else ""))
    if not keyterms:
        print("    WARNING: no keyterms. Measured, bare nova-3 scored 12 of 21 "
              "confirmed proper-noun sites on one tape and 13 of 17 on another, "
              "against 21 of 21 and 16 of 17 with keyterms. "
              "Pass --keyterms-file build/keyterms.txt")
    return out_path


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Transcribe a video with Deepgram nova-3. THE DECLARED FALLBACK; "
                    "ElevenLabs Scribe (transcribe.py) is the route.")
    ap.add_argument("video", type=Path, help="Path to video file")
    ap.add_argument("--edit-dir", type=Path, default=None,
                    help="Edit output directory (default: <video_parent>/edit)")
    ap.add_argument("--language", type=str, default="en",
                    help="ISO language code (default en)")
    ap.add_argument("--model", type=str, default="nova-3",
                    help="nova-3 (default). nova-2 is NOT recommended: its legacy "
                         "keyword boost inserts terms nobody said")
    ap.add_argument("--keyterms", type=str, default=None,
                    help="comma separated names to bias the model toward")
    ap.add_argument("--keyterms-file", type=Path, default=None,
                    help="a file with one keyterm per line, same shape transcribe.py takes")
    ap.add_argument("--force", action="store_true",
                    help="re-transcribe even when the JSON already exists")
    ap.add_argument("--raw-ends", action="store_true",
                    help="keep Deepgram's own word ends. They run into the next word's "
                         "start and are 125 to 160 ms late; do not cut on them")
    ap.add_argument("--no-diarize", action="store_true",
                    help="skip speaker labels. Measured 87 percent overall and only 72 "
                         "percent on the guest, so never burn a named caption from them")
    args = ap.parse_args()

    video = args.video.resolve()
    if not video.exists():
        sys.exit(f"video not found: {video}")
    edit_dir = (args.edit_dir or (video.parent / "edit")).resolve()
    api_key = load_api_key()
    kt = []
    if args.keyterms:
        kt += [t.strip() for t in args.keyterms.split(",") if t.strip()]
    if args.keyterms_file and args.keyterms_file.exists():
        kt += [l.strip() for l in args.keyterms_file.read_text().splitlines()
               if l.strip() and not l.startswith("#")]
    transcribe_one(video, edit_dir, api_key, args.language, model=args.model,
                   keyterms=kt or None, force=args.force,
                   snap_ends=not args.raw_ends, diarize=not args.no_diarize)


if __name__ == "__main__":
    main()
