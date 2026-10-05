"""Local transcription with faster-whisper (no API key, free, runs on your machine).

**LAST RESORT, third of three.** The route is ElevenLabs Scribe (`transcribe.py`) and the
declared fallback is Deepgram nova-3 (`transcribe_deepgram.py`). Reach for this one only
when there is no network and no key at all.

**What you give up, measured over about 2 hours of real tape:**

- **It takes no keyterms.** There is no argument for them and no way to tell it the names on
  the tape, which is the single biggest lever on proper-noun accuracy for the other two.
- On one episode all 3 engines ran on, it found 11 of 17 confirmed proper-noun sites where
  Scribe found 17 and Deepgram found 16. On another tape it found 25 of 47 where Deepgram
  found 47.
- Word boundaries about 3 times looser: 170 ms median error against 60 to 67 ms for either API.
- It once turned the host's own first name into a different two-word name in a shipped caption.

Spot-read every proper noun before anything burns.

Drop-in alternative to transcribe.py: same CLI, same output JSON shape, so every other
script in this skill (gen.py, captions.py, make_edl.py) reads it without changes:
{ "language": "en", "words": [ { "text": "...", "start": 0.12, "end": 0.34, "type": "word" }, ... ] }

Needs:  pip install faster-whisper   (plus ffmpeg on PATH)
First run downloads the model (cached afterwards). "large-v3" = best quality; "medium"
or "small" are faster on weak machines.

Usage:
    python scripts/transcribe_local.py <video_path> --edit-dir edit --language en
    python scripts/transcribe_local.py <video_path> --language it --model medium
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def extract_audio(video_path: Path, dest: Path) -> None:
    cmd = [
        "ffmpeg", "-y", "-i", str(video_path),
        "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le",
        str(dest),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main() -> None:
    ap = argparse.ArgumentParser(description="Transcribe a video locally with faster-whisper")
    ap.add_argument("video", type=Path, help="Path to video file")
    ap.add_argument("--edit-dir", type=Path, default=None,
                    help="Edit output directory (default: <video_parent>/edit)")
    ap.add_argument("--language", type=str, default=None,
                    help="ISO language code (e.g. 'en', 'it'). Omit to auto-detect.")
    ap.add_argument("--model", type=str, default="large-v3",
                    help="Whisper model: large-v3 (best) | medium | small | base.")
    ap.add_argument("--num-speakers", type=int, default=None,
                    help="Accepted for CLI parity; ignored (local model is single-speaker).")
    ap.add_argument("--force", action="store_true",
                    help="re-transcribe even when the JSON already exists")
    args = ap.parse_args()

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("faster-whisper not installed. Run:  pip install faster-whisper")

    video = args.video.resolve()
    if not video.exists():
        sys.exit(f"video not found: {video}")
    edit_dir = (args.edit_dir or (video.parent / "edit")).resolve()
    transcripts_dir = edit_dir / "transcripts"
    transcripts_dir.mkdir(parents=True, exist_ok=True)
    out_path = transcripts_dir / f"{video.stem}.json"
    if out_path.exists() and not args.force:
        # All 3 engines write <stem>.json here, so a cache hit can be another
        # engine's words. Handing those back silently is the thing the routing
        # rule bans, so the cache only counts when whisper wrote it.
        try:
            was = json.loads(out_path.read_text()).get("_engine", {}).get("engine")
        except Exception:
            was = None
        if was == "faster-whisper":
            print(f"cached: {out_path.name}  (--force to re-transcribe)")
            return
        print(f"  {out_path.name} exists but was written by "
              f"{was or 'another engine (no _engine header)'}; re-transcribing "
              f"locally rather than handing back its words", flush=True)

    print(f"  loading model {args.model} (first run downloads it)", flush=True)
    model = WhisperModel(args.model, device="auto", compute_type="auto")

    with tempfile.TemporaryDirectory() as tmp:
        audio = Path(tmp) / f"{video.stem}.wav"
        print(f"  extracting audio from {video.name}", flush=True)
        extract_audio(video, audio)
        print("  transcribing (word timestamps)...", flush=True)
        segments, info = model.transcribe(
            str(audio),
            language=args.language,
            word_timestamps=True,
            vad_filter=True,
        )
        words = []
        for seg in segments:
            for w in (seg.words or []):
                words.append({
                    "text": w.word.strip(),
                    "start": round(float(w.start), 3),
                    "end": round(float(w.end), 3),
                    "type": "word",
                })

    payload = {
        "language": info.language,
        "words": words,
        # The engine is named in the output's own header, never inferred.
        "_engine": {
            "engine": "faster-whisper",
            "role": "LAST RESORT, third of three. Route is ElevenLabs Scribe, "
                    "declared fallback is Deepgram nova-3.",
            "model": args.model,
            "keyterms": [],
            "keyterms_supported": False,
            "warning": "no keyterms: spot-read every proper noun before captions burn",
        },
    }
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    print(f"  saved: {out_path.name} ({len(words)} words) -> {out_path}")


if __name__ == "__main__":
    main()
