#!/usr/bin/env python3
"""Get a timestamped transcript for a video, by whichever route works.

Three routes, in order, stopping at the first that returns something:

  1. yt-dlp subs   native or auto captions written as WebVTT. Free, no key, and
                   it covers YouTube plus most of the ~1,000 sites yt-dlp knows
                   (Vimeo, Loom, Twitch and the rest). URLs only.
  2. YouTube API   your own channel's caption tracks (captions.list, then
                   captions.download as vtt), read-only. Optional: it runs only
                   when YOUTUBE_OAUTH_TOKEN holds an OAuth access token for the
                   channel that owns the video. YouTube hands captions over only
                   for videos that channel owns, so on anybody else's video it is
                   a clean 403 and the ladder moves on. This is what carries your
                   own videos on the days YouTube blocks yt-dlp.
  3. faster-whisper  local, offline, no key. The only route that works on a file
                   sitting on this machine, which is most of your own footage.

No paid key is needed. Nothing leaves the machine except the URL on route 1 and
the video id on route 2. If you pay for a transcript API and want it first in
the ladder, add a `from_<yours>()` that returns the same shape and call it at
the top of `resolve()`.

Every route returns the same shape, so nothing downstream cares which one ran:

    [{"start": 12.4, "end": 15.1, "text": "..."}, ...]

Every run gets its own new folder, and a route only reads files it wrote in that
run for that video. On 2026-10-10 the old shared folder (`watch-transcript` in
the temp folder) still held captions from an earlier run of a different video,
and when yt-dlp was blocked on 2 later videos the caption route parsed the
leftover file and returned the other video's words as theirs, with nothing
saying so. Nothing here deletes; new folders instead.

Run it directly to check a route:
    python3 transcript.py "<url-or-path>" [--video local.mp4] [--no-whisper]
    python3 transcript.py --self-test
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlparse
from urllib.request import Request, urlopen

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

# The parent of every run folder: the system temp folder, never your project, so
# nothing a run writes can end up committed. Each run makes a new child under
# it; nothing ever reads the parent itself.
WORK_ROOT = Path(tempfile.gettempdir()) / "watch-transcript"

# Route 2. An OAuth 2.0 access token (scope youtube.force-ssl) for the channel
# that owns the videos. Access tokens expire after about an hour; a 401 says so.
YOUTUBE_TOKEN_ENV = "YOUTUBE_OAUTH_TOKEN"
YOUTUBE_API = "https://www.googleapis.com/youtube/v3"


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


YOUTUBE_HOSTS = ("youtube.com", "youtu.be", "youtube-nocookie.com")
YOUTUBE_ID_RE = re.compile(
    r"(?:[?&]v=|youtu\.be/|/shorts/|/embed/|/live/|/v/)([A-Za-z0-9_-]{11})(?![A-Za-z0-9_-])"
)


def youtube_id(source: str) -> str | None:
    """The 11-character id of a YouTube link, or None for anything else."""
    if not is_url(source):
        return None
    host = (urlparse(source).hostname or "").lower()
    if not any(host == h or host.endswith("." + h) for h in YOUTUBE_HOSTS):
        return None
    match = YOUTUBE_ID_RE.search(source)
    return match.group(1) if match else None


def fresh_work_dir(source: str, root: Path = WORK_ROOT) -> Path:
    """A folder that did not exist before this call, named for the video.

    Keyed on the YouTube id when there is one (so a person can find it), else a
    hash of the source, then the time, then a random tail from mkdtemp so two
    runs in the same second still never share a folder.
    """
    key = youtube_id(source) or hashlib.sha256(source.encode()).hexdigest()[:12]
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    root.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix=f"{key}-{stamp}-", dir=str(root)))


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

def captions_from_this_run(sub_dir: Path, video_id: str | None, since: float) -> list[Path]:
    """The .vtt files in `sub_dir` that this run wrote for this video, and no others.

    Two tests, because the folder being new is the first guard and this is the
    second: the file must be named for the video id when we know it (a playlist
    sibling or a leftover is named for a different id), and it must have been
    written after the run started. `--no-mtime` on the yt-dlp call keeps the
    second test honest even if a yt-dlp config file turns `--mtime` on.
    """
    found = []
    for path in sorted(sub_dir.glob("*.vtt")):
        if video_id and not path.name.startswith(f"{video_id}."):
            continue
        if path.stat().st_mtime < since:
            continue
        found.append(path)
    return found


def from_ytdlp_captions(url: str, work_dir: Path) -> tuple[list[dict], str | None]:
    if shutil.which("yt-dlp") is None:
        return [], "yt-dlp not on PATH"

    # Whole seconds, because some filesystems store mtime to the second and a
    # file written in the same second as the start must still count as fresh.
    run_started = float(int(time.time()))
    # A new folder for this call, even inside a reused work folder (watch.py
    # reuses one per URL, and --work-dir can be anything), so nothing in it can
    # be from another run.
    work_dir.mkdir(parents=True, exist_ok=True)
    sub_dir = Path(tempfile.mkdtemp(prefix="subs-", dir=str(work_dir)))
    expected_id = youtube_id(url)
    cmd = [
        "yt-dlp",
        "--skip-download",
        "--no-playlist",
        "--no-mtime",
        "--write-subs",
        "--write-auto-subs",
        "--sub-langs", "en.*,en",
        "--sub-format", "vtt",
        "--convert-subs", "vtt",
        "-o", str(sub_dir / "%(id)s.%(ext)s"),
        url,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    # A failed yt-dlp is a failed route, even if it left a file behind.
    if proc.returncode != 0:
        return [], (
            f"yt-dlp failed (exit {proc.returncode}): {last_error_line(proc.stderr)}"
        )

    files = captions_from_this_run(sub_dir, expected_id, run_started)
    if not files:
        written = sorted(p.name for p in sub_dir.glob("*.vtt"))
        if written:
            return [], (
                f"yt-dlp wrote captions, but none for {expected_id or 'this video'} "
                f"in this run ({', '.join(written)})"
            )
        return [], "no captions on the source"

    segments = collapse_rolling(parse_vtt(str(files[0])))
    if not segments:
        return [], "caption file parsed to nothing"
    return segments, None


# --- Route 2: YouTube Data API, your own channel only ----------------------

class YouTubeHTTPError(Exception):
    def __init__(self, code: int, body: str):
        super().__init__(f"HTTP {code}: {body[:200]}")
        self.code = code
        self.body = body


def _youtube_get(path: str, params: dict, token: str, timeout: int) -> str:
    """One GET against the YouTube Data API v3, the body back as text."""
    url = f"{YOUTUBE_API}/{path}?{urlencode(params)}"
    req = Request(url, headers={"Authorization": f"Bearer {token}", "Accept": "*/*"})
    try:
        with urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", "replace")
    except HTTPError as exc:
        body = exc.read().decode("utf-8", "replace") if exc.fp else ""
        raise YouTubeHTTPError(exc.code, body) from None


def pick_caption_track(items: list[dict], video_id: str) -> dict | None:
    """The best English track for THIS video: serving, not a draft, a human
    track before YouTube's automatic (asr) one. A track whose videoId is another
    video's is never picked."""
    usable = []
    for item in items or []:
        snip = item.get("snippet") or {}
        if snip.get("videoId") != video_id:
            continue
        if not str(snip.get("language", "")).lower().startswith("en"):
            continue
        if snip.get("isDraft") or snip.get("status", "serving") != "serving":
            continue
        if not item.get("id"):
            continue
        usable.append(item)
    if not usable:
        return None
    usable.sort(key=lambda it: (it["snippet"].get("trackKind") == "asr",
                                it["snippet"].get("language") != "en"))
    return usable[0]


def from_youtube_api(url: str, work_dir: Path) -> tuple[list[dict], str | None]:
    vid = youtube_id(url)
    if not vid:
        return [], "not a YouTube link"
    token = (os.environ.get(YOUTUBE_TOKEN_ENV) or "").strip()
    if not token:
        return [], f"skipped, {YOUTUBE_TOKEN_ENV} is not set (optional, own channel only)"

    try:
        listing = json.loads(
            _youtube_get("captions", {"part": "snippet", "videoId": vid}, token, 120) or "{}"
        )
    except YouTubeHTTPError as exc:
        if exc.code == 401:
            return [], "the token was refused (401); access tokens last about an hour, get a fresh one"
        if exc.code == 403:
            return [], "YouTube lists captions only for videos the token's channel owns (403)"
        return [], f"could not list caption tracks: {exc}"
    except (URLError, OSError, ValueError) as exc:
        return [], f"could not list caption tracks: {str(exc)[:200]}"

    track = pick_caption_track(listing.get("items") or [], vid)
    if track is None:
        return [], "no serving English caption track on this video"

    try:
        vtt_text = _youtube_get(f"captions/{quote(track['id'], safe='')}",
                                {"tfmt": "vtt"}, token, 180)
    except YouTubeHTTPError as exc:
        if exc.code == 403:
            return [], "YouTube hands over captions only for videos the token's channel owns (403)"
        return [], f"could not load the caption track: {exc}"
    except (URLError, OSError) as exc:
        return [], f"could not load the caption track: {str(exc)[:200]}"

    if "-->" not in (vtt_text or ""):
        return [], "the caption track came back with no cues"

    work_dir.mkdir(parents=True, exist_ok=True)
    out_dir = Path(tempfile.mkdtemp(prefix="ytapi-", dir=str(work_dir)))
    lang = track["snippet"].get("language") or "en"
    vtt_path = out_dir / f"{vid}.{lang}.vtt"
    vtt_path.write_text(vtt_text, encoding="utf-8")
    segments = collapse_rolling(parse_vtt(str(vtt_path)))
    if not segments:
        return [], "caption track parsed to nothing"
    return segments, None


# --- Route 3: local faster-whisper -----------------------------------------

def _extract_audio(video_path: Path, dest: Path) -> bool:
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(video_path),
        "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le",
        str(dest),
    ]
    return subprocess.run(cmd, capture_output=True).returncode == 0


def audio_path_for(video_path: Path, work_dir: Path) -> Path:
    """Where this video's extracted audio lives. Named for the file (path, size,
    modified time), so a reused work folder hands back the same video's audio
    and never a different video's, which a fixed `audio.wav` would."""
    video = Path(video_path).resolve()
    stat = video.stat()
    key = hashlib.sha256(f"{video}|{stat.st_size}|{stat.st_mtime_ns}".encode()).hexdigest()[:12]
    return work_dir / f"audio-{key}.wav"


def from_local_whisper(video_path: Path, work_dir: Path) -> tuple[list[dict], str | None]:
    py = python_with("faster_whisper")
    if py is None:
        return [], (
            "faster-whisper is not installed on any interpreter here; install with: "
            "pip3 install faster-whisper  (then re-run, or set WATCH_PYTHON to the "
            "interpreter that has it)"
        )

    work_dir.mkdir(parents=True, exist_ok=True)
    audio = audio_path_for(video_path, work_dir)
    if not audio.exists() and not _extract_audio(video_path, audio):
        return [], "could not extract audio from the file"

    # Say this out loud. Measured on a laptop, 25 seconds of audio took 4:51
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

        if youtube_id(source):
            segments, why = from_youtube_api(source, work_dir)
            if segments:
                return segments, "captions (YouTube API, own channel)", notes
            notes.append(f"youtube api: {why}")

    if allow_whisper and video_path and Path(video_path).exists():
        segments, why = from_local_whisper(Path(video_path), work_dir)
        if segments:
            return segments, f"faster-whisper ({WHISPER_MODEL}, local)", notes
        notes.append(f"whisper: {why}")
    elif allow_whisper and not video_path:
        notes.append("whisper: no local file to transcribe")

    return [], "none", notes


def _self_test() -> int:
    """No network. A fake yt-dlp on PATH plays each failure, a real stale
    caption file sits in the folder the way it did on 2026-10-10, and the
    YouTube API call is stubbed."""
    failures: list[str] = []
    passed = 0

    def check(name, fn):
        nonlocal passed
        try:
            fn()
            passed += 1
        except AssertionError as exc:
            failures.append(f"{name}: {exc}")
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{name}: unexpected {type(exc).__name__}: {exc}")

    # Made-up ids in the YouTube shape; no real video is named here.
    vid_a, vid_b = "AAAAAAAAAa1", "BBBBBBBBBb2"
    stale_words = "These words belong to a different video from an earlier run"
    fresh_words = "These are the words of the video this run asked for"

    def vtt(words: str) -> str:
        return f"WEBVTT\n\n00:00:00.000 --> 00:00:03.000\n{words}\n"

    base = fresh_work_dir("self-test", root=WORK_ROOT / "selftest")
    bin_dir = base / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "yt-dlp"
    fake.write_text(
        f"#!{sys.executable}\n"
        "import os, re, sys\n"
        "mode = os.environ['FAKE_YTDLP_MODE']\n"
        "args = sys.argv[1:]\n"
        "out = args[args.index('-o') + 1]\n"
        "url = args[-1]\n"
        "m = re.search(r'v=([A-Za-z0-9_-]{11})', url)\n"
        "vid = 'OtherVideo1' if mode == 'other-id' else (m.group(1) if m else 'unknownid00')\n"
        "path = out.replace('%(id)s', vid).replace('%(ext)s', 'en.vtt')\n"
        "if mode in ('ok', 'other-id', 'fail-but-write'):\n"
        f"    open(path, 'w').write({vtt(fresh_words)!r})\n"
        "if mode.startswith('fail'):\n"
        "    sys.stderr.write('ERROR: [youtube] ' + vid + \": Sign in to confirm you're not a bot\\n\")\n"
        "    sys.exit(1)\n"
    )
    fake.chmod(0o755)

    url = f"https://www.youtube.com/watch?v={vid_a}"

    def stale_folder() -> Path:
        """A work folder laid out like the shared one on 2026-10-10."""
        work = Path(tempfile.mkdtemp(prefix="work-", dir=str(base)))
        (work / "subs").mkdir()
        (work / "subs" / "subs.en-orig.vtt").write_text(vtt(stale_words))
        (work / "subs" / "subs.en-US.vtt").write_text(vtt(stale_words))
        (work / f"{vid_a}.en.vtt").write_text(vtt(stale_words))
        return work

    old_path = os.environ.get("PATH", "")
    os.environ["PATH"] = f"{bin_dir}{os.pathsep}{old_path}"
    try:
        def stale_plus_failing():
            os.environ["FAKE_YTDLP_MODE"] = "fail"
            segs, why = from_ytdlp_captions(url, stale_folder())
            assert segs == [], f"returned {len(segs)} segments: {segs[:1]}"
            assert why and "yt-dlp failed" in why, f"reason was {why!r}"

        check("a stale .vtt plus a failing yt-dlp returns [] with a reason", stale_plus_failing)

        def failing_but_wrote():
            os.environ["FAKE_YTDLP_MODE"] = "fail-but-write"
            segs, why = from_ytdlp_captions(url, stale_folder())
            assert segs == [], f"accepted a file from a failed run: {segs[:1]}"
            assert why and "exit 1" in why, f"reason was {why!r}"

        check("a yt-dlp that errors is refused even when it wrote a file", failing_but_wrote)

        def happy_path():
            os.environ["FAKE_YTDLP_MODE"] = "ok"
            segs, why = from_ytdlp_captions(url, stale_folder())
            text = " ".join(s["text"] for s in segs)
            assert why is None, f"reason was {why!r}"
            assert fresh_words in text, f"got {text!r}"
            assert "different video" not in text, "the stale file leaked into a good run"

        check("a working yt-dlp returns this run's captions, not the stale ones", happy_path)

        def other_id():
            os.environ["FAKE_YTDLP_MODE"] = "other-id"
            segs, why = from_ytdlp_captions(url, stale_folder())
            assert segs == [], f"accepted another video's captions: {segs[:1]}"
            assert why and f"none for {vid_a}" in why, f"reason was {why!r}"

        check("captions named for a different video id are refused", other_id)

        def whole_ladder():
            # The 2026-10-10 run end to end: yt-dlp blocked, and the YouTube API
            # route stubbed so the test needs no network.
            os.environ["FAKE_YTDLP_MODE"] = "fail"
            saved = globals()["from_youtube_api"]
            globals()["from_youtube_api"] = lambda u, w: ([], "stubbed")
            try:
                segs, route, notes = resolve(url, stale_folder(), None, allow_whisper=False)
            finally:
                globals()["from_youtube_api"] = saved
            assert segs == [] and route == "none", f"route {route!r}, {len(segs)} segments"
            assert any("yt-dlp failed" in n for n in notes), f"notes {notes}"

        check("the whole ladder returns nothing rather than another video's words", whole_ladder)
    finally:
        os.environ["PATH"] = old_path
        os.environ.pop("FAKE_YTDLP_MODE", None)

    def old_mtime_refused():
        folder = Path(tempfile.mkdtemp(prefix="mtime-", dir=str(base)))
        old = folder / f"{vid_a}.en.vtt"
        old.write_text(vtt(stale_words))
        an_hour_ago = time.time() - 3600
        os.utime(old, (an_hour_ago, an_hour_ago))
        got = captions_from_this_run(folder, vid_a, time.time() - 60)
        assert got == [], f"accepted a file older than the run: {got}"
        since = float(int(time.time()))
        new = folder / f"{vid_a}.en-US.vtt"
        new.write_text(vtt(fresh_words))
        got = captions_from_this_run(folder, vid_a, since)
        assert got == [new], f"expected only the new file, got {got}"

    check("a file written before the run started is refused", old_mtime_refused)

    def fresh_folders():
        a = fresh_work_dir(url, root=base / "roots")
        b = fresh_work_dir(url, root=base / "roots")
        assert a != b, "two runs got the same folder"
        assert a.is_dir() and b.is_dir() and not any(a.iterdir()), "folder not new and empty"
        assert a.name.startswith(f"{vid_a}-"), f"folder not named for the video: {a.name}"
        default = fresh_work_dir(url)
        assert default.parent == WORK_ROOT and default != WORK_ROOT, f"default was {default}"

    check("every run gets its own new folder", fresh_folders)

    def ids():
        cases = {
            f"https://www.youtube.com/watch?v={vid_a}": vid_a,
            f"https://youtu.be/{vid_b}?t=30": vid_b,
            f"https://www.youtube.com/shorts/{vid_b}": vid_b,
            f"https://www.youtube.com/watch?v={vid_a}&list=PLx": vid_a,
            f"https://vimeo.com/watch?v={vid_a}": None,
            "clips/video.mp4": None,
        }
        for source, want in cases.items():
            got = youtube_id(source)
            assert got == want, f"{source} gave {got!r}, wanted {want!r}"

    check("YouTube ids are read off every link shape, and only off YouTube", ids)

    def item(vid, lang, kind, tid, draft=False):
        return {"id": tid, "snippet": {"videoId": vid, "language": lang,
                                       "trackKind": kind, "isDraft": draft,
                                       "status": "serving"}}

    tracks = [
        item("OtherVideo1", "en", "standard", "other"),
        item(vid_a, "de-DE", "standard", "german"),
        item(vid_a, "en", "standard", "draft", draft=True),
        item(vid_a, "en", "asr", "auto"),
        item(vid_a, "en-US", "standard", "human"),
    ]

    def track_pick():
        got = pick_caption_track(tracks, vid_a)
        assert got and got["id"] == "human", f"picked {got and got['id']}"
        assert pick_caption_track(tracks[:1], vid_a) is None, "picked another video's track"

    check("the API route picks this video's human English track", track_pick)

    def api_route_stubbed():
        saved_get = globals()["_youtube_get"]
        saved_token = os.environ.get(YOUTUBE_TOKEN_ENV)
        asked: list[str] = []

        def fake_get(path, params, token, timeout):
            asked.append(path)
            if path == "captions":
                assert params.get("videoId") == vid_a, f"listed for {params}"
                return json.dumps({"items": tracks})
            if path == "captions/human":
                return vtt(fresh_words)
            raise YouTubeHTTPError(403, "forbidden")

        globals()["_youtube_get"] = fake_get
        try:
            os.environ.pop(YOUTUBE_TOKEN_ENV, None)
            segs, why = from_youtube_api(url, base)
            assert segs == [] and why and "not set" in why, f"no token gave {why!r}"
            assert asked == [], "called the API with no token"

            os.environ[YOUTUBE_TOKEN_ENV] = "test-token"
            segs, why = from_youtube_api(url, base)
            assert why is None, f"reason was {why!r}"
            assert fresh_words in " ".join(s["text"] for s in segs), f"got {segs}"

            def refuse(path, params, token, timeout):
                if path == "captions":
                    return json.dumps({"items": tracks})
                raise YouTubeHTTPError(403, "forbidden")

            globals()["_youtube_get"] = refuse
            segs, why = from_youtube_api(url, base)
            assert segs == [] and why and "403" in why, f"a 403 gave {why!r}"
        finally:
            globals()["_youtube_get"] = saved_get
            if saved_token is None:
                os.environ.pop(YOUTUBE_TOKEN_ENV, None)
            else:
                os.environ[YOUTUBE_TOKEN_ENV] = saved_token

    check("the API route skips with no token, reads a track, and names a 403", api_route_stubbed)

    def audio_names():
        one = base / "one.mp4"
        two = base / "two.mp4"
        one.write_bytes(b"first video")
        two.write_bytes(b"second video, a different file")
        work = base / "shared-work"
        assert audio_path_for(one, work) != audio_path_for(two, work), "two videos share audio"
        assert audio_path_for(one, work) == audio_path_for(one, work), "same video, new audio"

    check("two videos in one work folder never share extracted audio", audio_names)

    if failures:
        print("SELF-TEST FAILED")
        for line in failures:
            print("  -", line)
        print(f"  (scratch left in {base})")
        return 1
    print(f"transcript self-test: {passed} cases pass (scratch left in {base})")
    return 0


def main() -> int:
    if "--self-test" in sys.argv[1:]:
        return _self_test()

    ap = argparse.ArgumentParser(description="Resolve a transcript for a video")
    ap.add_argument("source", help="URL or local file path")
    ap.add_argument("--video", default=None, help="Local file to fall back to for whisper")
    ap.add_argument("--work-dir", default=None,
                    help="Folder to work in; by default a new one per run under "
                         f"{WORK_ROOT}")
    ap.add_argument("--no-whisper", action="store_true")
    ap.add_argument("--self-test", action="store_true", help="Run the offline self-test")
    args = ap.parse_args()

    work = Path(args.work_dir) if args.work_dir else fresh_work_dir(args.source)
    work.mkdir(parents=True, exist_ok=True)
    print(f"work folder: {work}", file=sys.stderr)
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
