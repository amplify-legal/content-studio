#!/usr/bin/env python3
"""Get a timestamped transcript for a video, by whichever route works.

Two routes, both free, in order, stopping at the first that returns something:

  1. yt-dlp subs   native or auto captions written as WebVTT. Free, no key, and
                   it covers YouTube plus most of the ~1,000 sites yt-dlp knows
                   (Vimeo, Loom, Twitch and the rest). URLs only.
  2. faster-whisper  local, offline, no key. The only route that works on a file
                   sitting on this machine, which is most of your own footage.

No API key is needed and none is used. Nothing leaves the machine except the
URL on route 1. If you pay for a transcript API and want it first in the ladder,
add a `from_<yours>()` that returns the same shape and call it at the top of
`resolve()`.

Every route returns the same shape, so nothing downstream cares which one ran:

    [{"start": 12.4, "end": 15.1, "text": "..."}, ...]

Run it directly to check a route:
    python3 transcript.py "<url-or-path>" [--video local.mp4] [--no-whisper]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import tempfile
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vtt import parse_vtt  # noqa: E402

# Interpreter map, and it matters. The python3 that runs this script is often
# not the one that has faster-whisper installed (Homebrew python, a system
# python and a conda python commonly all exist on the same Mac, with the
# library in exactly one of them). Rather than hard-code a path, probe for an
# interpreter that can import what the route needs. Set WATCH_PYTHON to put
# your own interpreter at the front of the queue.
CANDIDATE_PYTHONS = [
    os.environ.get("WATCH_PYTHON"),
    sys.executable,
    shutil.which("python3"),
    "/usr/bin/python3",
    str(Path.home() / "anaconda3" / "bin" / "python3"),
    str(Path.home() / "miniconda3" / "bin" / "python3"),
    "/opt/homebrew/bin/python3",
]
WHISPER_MODEL = os.environ.get("WATCH_WHISPER_MODEL", "small")


def last_error_line(stderr: str) -> str:
    """The line worth showing out of a stderr dump.

    Naively taking the last line reports a `resource_tracker` warning as the cause
    of a failure it had nothing to do with, which is exactly the kind of wrong
    diagnosis that costs an hour. Prefer a real exception line, then the last line
    that is not a warning or a traceback frame.
    """
    lines = [ln.rstrip() for ln in (stderr or "").splitlines() if ln.strip()]
    if not lines:
        return "no error text"
    for line in reversed(lines):
        if re.match(r"^\w*(Error|Exception|Exit)\b|^\w+Error:", line.strip()):
            return line.strip()
    noise = ("warn", "warning:", "file \"", "  ", "traceback")
    for line in reversed(lines):
        low = line.lower()
        if not any(low.startswith(n) or n in low for n in noise):
            return line.strip()
    return lines[-1].strip()


def python_with(module: str) -> str | None:
    """First interpreter on this machine that can import `module`."""
    for py in CANDIDATE_PYTHONS:
        if not py or not Path(py).exists():
            continue
        probe = subprocess.run([py, "-c", f"import {module}"], capture_output=True)
        if probe.returncode == 0:
            return py
    return None


def is_url(source: str) -> bool:
    return source.startswith(("http://", "https://"))


def collapse_rolling(segments: list[dict]) -> list[dict]:
    """Strip YouTube's rolling-caption overlap.

    Auto-captions scroll, so consecutive cues repeat the tail of the one before:

        [20:34] and that is the whole setup in under a minute. So, next
        [20:36] under a minute. So, next we look at the part that breaks

    Read literally that triples the token cost and makes every quote look stuttered.
    For each cue, find the longest word-suffix of what we already have that opens
    this cue, and drop it. Harmless on a clean transcript, where no overlap exists.
    """
    out: list[dict] = []
    for seg in segments:
        words = seg["text"].split()
        if not words:
            continue
        if not out:
            out.append({**seg, "text": " ".join(words)})
            continue

        prev = out[-1]["text"].split()
        overlap = 0
        for n in range(min(len(prev), len(words)), 0, -1):
            if [w.lower() for w in prev[-n:]] == [w.lower() for w in words[:n]]:
                overlap = n
                break

        fresh = words[overlap:]
        if not fresh:
            # Wholly contained in the previous cue: just extend its time range.
            out[-1]["end"] = max(out[-1]["end"], seg["end"])
            continue
        out.append({"start": seg["start"], "end": seg["end"], "text": " ".join(fresh)})
    return out


# --- Route 1: yt-dlp native captions ---------------------------------------

def from_ytdlp_captions(url: str, work_dir: Path) -> tuple[list[dict], str | None]:
    if shutil.which("yt-dlp") is None:
        return [], "yt-dlp not on PATH"

    sub_dir = work_dir / "subs"
    sub_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "yt-dlp",
        "--skip-download",
        "--write-subs",
        "--write-auto-subs",
        "--sub-langs", "en.*,en",
        "--sub-format", "vtt",
        "--convert-subs", "vtt",
        "-o", str(sub_dir / "subs.%(ext)s"),
        url,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    files = sorted(sub_dir.glob("*.vtt"))
    if not files:
        return [], f"no captions on the source ({last_error_line(proc.stderr)})"

    segments = collapse_rolling(parse_vtt(str(files[0])))
    if not segments:
        return [], "caption file parsed to nothing"
    return segments, None


# --- Route 2: local faster-whisper -----------------------------------------

def _extract_audio(video_path: Path, dest: Path) -> bool:
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(video_path),
        "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le",
        str(dest),
    ]
    return subprocess.run(cmd, capture_output=True).returncode == 0


def from_local_whisper(video_path: Path, work_dir: Path) -> tuple[list[dict], str | None]:
    py = python_with("faster_whisper")
    if py is None:
        return [], (
            "faster-whisper is not installed on any interpreter here; install with: "
            "pip3 install faster-whisper  (then re-run, or set WATCH_PYTHON to the "
            "interpreter that has it)"
        )

    audio = work_dir / "audio.wav"
    if not audio.exists() and not _extract_audio(video_path, audio):
        return [], "could not extract audio from the file"

    # Say this out loud. Measured on this machine, 25 seconds of audio took 4:51
    # wall at 29% CPU with Chrome and Zoom running, and a silent wait that long
    # reads as a hang. It is not one.
    probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(audio)],
        capture_output=True, text=True,
    )
    try:
        minutes = float((probe.stdout or "0").strip()) / 60.0
    except ValueError:
        minutes = 0.0
    print(
        f"  · transcribing {minutes:.1f} min locally with faster-whisper "
        f"({WHISPER_MODEL}). Slow on a busy machine, and slower still on the "
        "first run for a model. --no-whisper skips it.",
        file=sys.stderr, flush=True,
    )

    # Two settings that decide whether this takes 40 seconds or 20 minutes on a
    # laptop that is also running Chrome and a Zoom call:
    #   cpu_threads  the default leaves most cores idle under contention.
    #   beam_size=1  greedy decoding. Beam search buys accuracy this lens does
    #                  not need; we want to know what was said, not caption it.
    threads = max(1, (os.cpu_count() or 4) - 2)
    code = (
        "import json,sys\n"
        "from faster_whisper import WhisperModel\n"
        f"m = WhisperModel({WHISPER_MODEL!r}, device='cpu', compute_type='int8',"
        f" cpu_threads={threads})\n"
        f"segs, info = m.transcribe({str(audio)!r}, vad_filter=True, beam_size=1)\n"
        "out=[{'start':round(s.start,2),'end':round(s.end,2),'text':s.text.strip()} for s in segs]\n"
        "print(json.dumps(out))\n"
    )
    proc = subprocess.run([py, "-c", code], capture_output=True, text=True, timeout=7200)
    if proc.returncode != 0:
        return [], f"faster-whisper failed: {last_error_line(proc.stderr)}"
    try:
        segments = [s for s in json.loads(proc.stdout or "[]") if s.get("text")]
    except json.JSONDecodeError:
        return [], "faster-whisper returned something that was not json"
    if not segments:
        return [], "faster-whisper heard nothing"
    return segments, None


# --- The ladder -------------------------------------------------------------

def resolve(
    source: str,
    work_dir: Path,
    video_path: Path | None = None,
    allow_whisper: bool = True,
) -> tuple[list[dict], str, list[str]]:
    """Returns (segments, route_that_worked, notes_from_routes_that_did_not)."""
    notes: list[str] = []

    if is_url(source):
        segments, why = from_ytdlp_captions(source, work_dir)
        if segments:
            return segments, "captions (yt-dlp)", notes
        notes.append(f"captions: {why}")

    if allow_whisper and video_path and Path(video_path).exists():
        segments, why = from_local_whisper(Path(video_path), work_dir)
        if segments:
            return segments, f"faster-whisper ({WHISPER_MODEL}, local)", notes
        notes.append(f"whisper: {why}")
    elif allow_whisper and not video_path:
        notes.append("whisper: no local file to transcribe")

    return [], "none", notes


def main() -> int:
    ap = argparse.ArgumentParser(description="Resolve a transcript for a video")
    ap.add_argument("source", help="URL or local file path")
    ap.add_argument("--video", default=None, help="Local file to fall back to for whisper")
    ap.add_argument("--work-dir", default=None)
    ap.add_argument("--no-whisper", action="store_true")
    args = ap.parse_args()

    work = Path(args.work_dir) if args.work_dir else Path(tempfile.gettempdir()) / "watch-transcript"
    work.mkdir(parents=True, exist_ok=True)
    video = Path(args.video) if args.video else (
        Path(args.source) if not is_url(args.source) else None
    )
    if video is not None and not video.exists():
        print(f"Cannot find the video: {video}", file=sys.stderr)
        print("Check the path. Pass a URL instead if you want it fetched.", file=sys.stderr)
        return 2

    segments, route, notes = resolve(
        args.source, work, video, allow_whisper=not args.no_whisper
    )
    for note in notes:
        print(f"  · {note}", file=sys.stderr)
    print(f"route: {route}, {len(segments)} segments", file=sys.stderr)
    print(json.dumps(segments, indent=2))
    return 0 if segments else 1


if __name__ == "__main__":
    raise SystemExit(main())
