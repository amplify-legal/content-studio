"""Transcribe a video with ElevenLabs Scribe (word-level timestamps).

THE ROUTE, first of three engines. Deepgram nova-3 (transcribe_deepgram.py) is the
declared fallback; local whisper (transcribe_local.py) is last resort for no network and
no key at all. All three write the same shape to the same path and name themselves in
the output file's "_engine" header, so which one ran is never inferred.

Standalone: no external project needed,
only `requests` + `ffmpeg` on PATH. Extracts mono 16kHz audio, uploads to Scribe with
verbatim + word-level timestamps, and writes the full response to
<edit_dir>/transcripts/<video_stem>.json in the shape gen.py / captions.py expect:
{ "words": [ { "text": "...", "start": 0.12, "end": 0.34, "type": "word" }, ... ] }

API key: reads ELEVENLABS_API_KEY from a `.env` file in the current directory, next to
this script, or in any parent folder up to the project root (the folder holding .git or
.claude), then from the environment. NEVER hard-code it.

Keyterms: pass the names on the tape (people, products, places) with --keyterms or
--keyterms-file. Names go INTO the transcriber, never into a find-and-replace afterwards.

Cached: if the output JSON already exists the upload is skipped, unless --force.
The cache is keyed on the FILENAME, so a pipeline that rewrites the same name
with new content must pass --force or it will read back the previous run.

Usage:
    python scripts/transcribe.py <video_path>
    python scripts/transcribe.py <video_path> --edit-dir edit
    python scripts/transcribe.py <video_path> --language en
    python scripts/transcribe.py <video_path> --language it --num-speakers 1
    python scripts/transcribe.py <video_path> --keyterms-file build/keyterms.txt
    python scripts/transcribe.py <video_path> --force     # re-run on a rewritten file
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import requests


SCRIBE_URL = "https://api.elevenlabs.io/v1/speech-to-text"


def load_api_key() -> str:
    # Walk UP to the project root, not just cwd and this folder. A video pipeline
    # often runs from content/videos/<slug>/build/, where neither of those holds
    # the key, so a cwd-only lookup exits "not found" while the project .env has it.
    here = Path(__file__).resolve()
    candidates = [Path.cwd() / ".env", here.parent / ".env"]
    for up in list(Path.cwd().resolve().parents) + list(here.parents):
        candidates.append(up / ".env")
        if (up / ".claude").is_dir() or (up / ".git").is_dir():
            break
    for candidate in candidates:
        if candidate.exists():
            for line in candidate.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                if k.strip() == "ELEVENLABS_API_KEY":
                    return v.strip().strip('"').strip("'")
    v = os.environ.get("ELEVENLABS_API_KEY", "")
    if not v:
        sys.exit(
            "ELEVENLABS_API_KEY not found.\n"
            "  Set it once:  export ELEVENLABS_API_KEY=sk_...   (add to ~/.zshrc)\n"
            "  Or put a line  ELEVENLABS_API_KEY=sk_...  in a .env file here.\n"
            "  Get a key at https://elevenlabs.io (Speech-to-Text / Scribe).\n"
            "  No key? scripts/transcribe_deepgram.py is the declared fallback\n"
            "  (DEEPGRAM_API_KEY, same CLI, same --keyterms-file). Local whisper\n"
            "  (scripts/transcribe_local.py) is last resort: no keyterms, and it\n"
            "  misses names both APIs catch."
        )
    return v


def extract_audio(video_path: Path, dest: Path) -> None:
    cmd = [
        "ffmpeg", "-y", "-i", str(video_path),
        "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le",
        str(dest),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def call_scribe(audio_path: Path, api_key: str, language=None, num_speakers=None,
                model_id="scribe_v2", keyterms=None) -> dict:
    data = {
        "model_id": model_id,
        "diarize": "true",
        "tag_audio_events": "true",
        "timestamps_granularity": "word",
    }
    if language:
        data["language_code"] = language
    if num_speakers:
        data["num_speakers"] = str(num_speakers)

    # Keyterms bias the model toward names it would otherwise guess at. Measured
    # on 40s of a real guest tape: scribe_v1 and bare scribe_v2 both misheard the
    # guest's surname and the host's name, and scribe_v2 with keyterms got both
    # right. Correcting names downstream with a find-and-replace patches a problem
    # that should never reach the file. Keyterms cost extra: check the provider's
    # pricing page.
    if keyterms:
        data = ([(k, v) for k, v in data.items()] +
                [("keyterms", k) for k in keyterms])

    with open(audio_path, "rb") as f:
        resp = requests.post(
            SCRIBE_URL,
            headers={"xi-api-key": api_key},
            files={"file": (audio_path.name, f, "audio/wav")},
            data=data,
            timeout=1800,
        )
    if resp.status_code != 200:
        raise RuntimeError(f"Scribe returned {resp.status_code}: {resp.text[:500]}")
    return resp.json()


def transcribe_one(video: Path, edit_dir: Path, api_key: str, language=None,
                   num_speakers=None, model_id="scribe_v2", keyterms=None,
                   force=False) -> Path:
    transcripts_dir = edit_dir / "transcripts"
    transcripts_dir.mkdir(parents=True, exist_ok=True)
    out_path = transcripts_dir / f"{video.stem}.json"
    if out_path.exists() and not force:
        # All 3 engines write <stem>.json here. A run that fell back to Deepgram
        # or whisper leaves its words in this exact path, so a later Scribe run
        # would print "cached" and hand back the fallback's output under the
        # route's name. The cache only counts when THIS engine wrote it.
        try:
            was = json.loads(out_path.read_text()).get("_engine", {}).get("engine")
        except Exception:
            was = None
        if was == "elevenlabs-scribe":
            print(f"cached: {out_path.name}  (--force to re-transcribe)")
            return out_path
        print(f"  {out_path.name} exists but was written by "
              f"{was or 'another engine (no _engine header)'}; re-transcribing "
              f"with Scribe rather than handing back its words", flush=True)

    print(f"  extracting audio from {video.name}", flush=True)
    t0 = time.time()
    with tempfile.TemporaryDirectory() as tmp:
        audio = Path(tmp) / f"{video.stem}.wav"
        extract_audio(video, audio)
        size_mb = audio.stat().st_size / (1024 * 1024)
        print(f"  uploading {video.stem}.wav ({size_mb:.1f} MB)", flush=True)
        payload = call_scribe(audio, api_key, language, num_speakers,
                              model_id=model_id, keyterms=keyterms)

    # The engine is named in the output's own header, never inferred. A rule that
    # says so is only true if every engine actually writes the header.
    if isinstance(payload, dict):
        payload["_engine"] = {
            "engine": "elevenlabs-scribe",
            "role": "THE ROUTE, first of three (Deepgram is the fallback, whisper last resort)",
            "model": model_id,
            "keyterms": keyterms or [],
            "language": language,
        }
    out_path.write_text(json.dumps(payload, indent=2))
    dt = time.time() - t0
    kb = out_path.stat().st_size / 1024
    print(f"  saved: {out_path.name} ({kb:.1f} KB) in {dt:.1f}s")
    if isinstance(payload, dict) and "words" in payload:
        print(f"    words: {len(payload['words'])}")
    return out_path


def main() -> None:
    ap = argparse.ArgumentParser(description="Transcribe a video with ElevenLabs Scribe")
    ap.add_argument("video", type=Path, help="Path to video file")
    ap.add_argument("--edit-dir", type=Path, default=None,
                    help="Edit output directory (default: <video_parent>/edit)")
    ap.add_argument("--language", type=str, default=None,
                    help="ISO language code (e.g. 'en', 'it'). Omit to auto-detect.")
    ap.add_argument("--model", type=str, default="scribe_v2",
                    help="scribe_v2 (default) or scribe_v1")
    ap.add_argument("--keyterms", type=str, default=None,
                    help="comma separated names to bias the model toward, e.g. "
                         "'Jane Example,Acme Widgets,Claude Code'. Max 1000 terms, "
                         "each under 50 chars and at most 5 words")
    ap.add_argument("--keyterms-file", type=Path, default=None,
                    help="a file with one keyterm per line, for a pipeline that "
                         "keeps its own list beside the episode")
    ap.add_argument("--force", action="store_true",
                    help="re-transcribe even when the JSON already exists")
    ap.add_argument("--num-speakers", type=int, default=None,
                    help="Number of speakers when known (use 1 for a single talking head).")
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
    transcribe_one(video, edit_dir, api_key, args.language, args.num_speakers,
                   model_id=args.model, keyterms=kt or None, force=args.force)


if __name__ == "__main__":
    main()
