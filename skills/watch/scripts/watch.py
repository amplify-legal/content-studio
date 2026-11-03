#!/usr/bin/env python3
"""Watch a video: pull it, slice it into timestamped frames, get the transcript,
and print the pair so Claude can actually look at it.

The point of the whole thing: a transcript is half a video. Cuts, overlays,
what is on screen while a claim is made, whether a face is centred or a slide is
being read off, none of that survives a transcript. This hands over both.

Usage
    python3 watch.py "<url-or-path>"
    python3 watch.py "<url>" --hook                 dense over the first 15s
    python3 watch.py "<url>" --detail deep          scene-aware, uncapped
    python3 watch.py "<url>" --start 2:15 --end 2:45
    python3 watch.py local.mp4 --timestamps 4:32,7:10
    python3 watch.py --self-test                    offline check of the download cache

Prints a report to stdout ending in a list of frame paths. Read those paths.

A downloaded video is reused only through the `source.json` written beside it
when the download finished, and only for the same link (the same YouTube id
counts). Until 2026-10-11 any `video.*` in the work folder was handed back as
"cached", so an `--out-dir` reused for a second link returned the first link's
file, and the frames and transcript described the wrong video. Nothing here
deletes; a reused folder gets a new download subfolder instead.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from frames import (  # noqa: E402
    MAX_FPS,
    auto_fps,
    auto_fps_focus,
    extract_at_timestamps,
    extract_keyframes,
    extract_scene_or_uniform,
    format_time,
    get_metadata,
    merge_frames,
    parse_time,
    parse_timestamps,
)
from transcript import is_url, resolve as resolve_transcript, youtube_id  # noqa: E402
from vtt import filter_range, format_transcript  # noqa: E402

DETAIL_CAPS = {
    "transcript": 0,
    "efficient": 50,
    "balanced": 100,
    "deep": None,
}
VIDEO_SUFFIXES = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v", ".flv", ".ts"}
HOOK_DEFAULT_SECONDS = 15.0
HOOK_FPS = 2.0

# The record written beside a finished download, and the prefix of the
# subfolders a reused work folder gets for a second link.
SOURCE_RECORD = "source.json"
DOWNLOAD_PREFIX = "video-"

# Where --self-test works: the system temp folder, never your project.
SELF_TEST_ROOT = Path(tempfile.gettempdir()) / "watch-selftest"


def say(message: str) -> None:
    """Progress to stderr. A scene pass on a 20-minute VP9 file takes minutes and
    a silent terminal reads as a hang, which is how people kill a working run."""
    print(f"  · {message}", file=sys.stderr, flush=True)


def preflight() -> list[str]:
    missing = [b for b in ("ffmpeg", "ffprobe") if shutil.which(b) is None]
    return missing


def work_dir_for(source: str, explicit: str | None) -> Path:
    if explicit:
        path = Path(explicit).expanduser().resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path
    slug = hashlib.sha256(source.encode()).hexdigest()[:12]
    path = Path(tempfile.gettempdir()) / "watch" / slug
    path.mkdir(parents=True, exist_ok=True)
    return path


def same_source(record: dict, source: str) -> bool:
    """Whether a download record belongs to this link. A YouTube link matches on
    its id, so youtu.be/X and watch?v=X share one download; anything else must be
    the exact same link."""
    vid = youtube_id(source)
    if vid:
        return record.get("youtube_id") == vid
    return record.get("youtube_id") is None and record.get("source") == source


def read_record(folder: Path) -> dict | None:
    try:
        record = json.loads((folder / SOURCE_RECORD).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return record if isinstance(record, dict) else None


def cached_download(source: str, work: Path) -> Path | None:
    """A video this work folder already holds for THIS link, or None.

    Looks in the folder and in its download subfolders, and trusts a file only
    through the record beside it: the record must name this link, and the file it
    names must still be there at the size recorded. A `video.*` with no record (a
    download from an older version of this script, or one that never finished)
    is never reused.
    """
    folders = [work] + sorted(
        p for p in work.glob(f"{DOWNLOAD_PREFIX}*") if p.is_dir()
    )
    for folder in folders:
        record = read_record(folder)
        if not record or not same_source(record, source):
            continue
        video = folder / Path(str(record.get("video") or "")).name
        if (video.name and video.suffix.lower() in VIDEO_SUFFIXES and video.is_file()
                and video.stat().st_size == record.get("size")):
            return video
    return None


def download_dir_for(source: str, work: Path) -> Path:
    """Where a new download goes: the work folder itself while it holds no video
    and no record (the usual first run in a per-link folder), otherwise a new
    subfolder named for the link.

    Never the occupied folder, because yt-dlp told to write video.mp4 beside an
    existing video.mp4 keeps the old file, reports "has already been downloaded"
    and prints that file's path as the result (read in yt-dlp's own
    yt_dlp/YoutubeDL.py, 2026-10-11).
    """
    occupied = any(work.glob("video.*")) or (work / SOURCE_RECORD).exists()
    if not occupied:
        return work
    key = youtube_id(source) or hashlib.sha256(source.encode()).hexdigest()[:12]
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return Path(tempfile.mkdtemp(prefix=f"{DOWNLOAD_PREFIX}{key}-{stamp}-", dir=str(work)))


def write_record(video: Path, source: str, quality: str, via: str) -> None:
    """Written only after a download finished, so its presence means the file
    beside it is complete and belongs to `source`."""
    record = {
        "source": source,
        "youtube_id": youtube_id(source),
        "video": video.name,
        "size": video.stat().st_size,
        "quality": quality,
        "via": via,
        "downloaded_at": datetime.now().isoformat(timespec="seconds"),
    }
    (video.parent / SOURCE_RECORD).write_text(json.dumps(record, indent=2), encoding="utf-8")


def fetch_video(source: str, work: Path, quality: str) -> tuple[Path | None, str]:
    """Get the file. URLs go through the self-healing yt-dlp wrapper that ships
    beside this script, which upgrades yt-dlp and retries when YouTube hands
    back a bare 403."""
    if not is_url(source):
        local = Path(source).expanduser().resolve()
        if not local.exists():
            raise SystemExit(f"No such file: {local}")
        return local, "local file"

    cached = cached_download(source, work)
    if cached:
        return cached, "cached (downloaded earlier for this same link)"

    video, via = download(source, download_dir_for(source, work), quality)
    write_record(video, source, quality, via)
    return video, via


def download(source: str, dest: Path, quality: str) -> tuple[Path, str]:
    """Download `source` into `dest` as video.<ext>. `dest` holds no other video
    (download_dir_for sees to that), so whatever lands there is this link's."""
    wrapper = Path(__file__).resolve().parent / "yt_download.sh"
    if wrapper.exists() and shutil.which("zsh") is None:
        detail = "yt_download.sh needs zsh, which is not installed here"
    elif wrapper.exists():
        proc = subprocess.run(
            ["zsh", str(wrapper), source, "--quality", quality,
             "--codec", "h264", "--out", str(dest), "--name", "video"],
            capture_output=True, text=True, timeout=3600,
        )
        tail = (proc.stdout or "").strip().splitlines()
        if proc.returncode == 0 and tail:
            candidate = Path(tail[-1].strip())
            if candidate.exists():
                return candidate, "yt_download.sh (self-healing)"
        note = (proc.stderr or proc.stdout or "").strip().splitlines()
        detail = note[-1] if note else "no output"
    else:
        detail = "yt_download.sh is not beside this script"

    if shutil.which("yt-dlp") is None:
        raise SystemExit(f"Could not download and yt-dlp is not on PATH. {detail}")
    proc = subprocess.run(
        ["yt-dlp", "-f",
         f"bv*[vcodec^=avc1][height<={quality}]+ba/b[vcodec^=avc1][height<={quality}]"
         f"/bv*[height<={quality}]+ba/b[height<={quality}]/b",
         "--merge-output-format", "mp4", "-o", str(dest / "video.%(ext)s"), source],
        capture_output=True, text=True, timeout=3600,
    )
    # stem "video" only: a merge that died leaves format parts like video.f137.mp4.
    files = [p for p in dest.glob("video.*")
             if p.stem == "video" and p.suffix.lower() in VIDEO_SUFFIXES]
    if not files:
        err = (proc.stderr or "").strip().splitlines()
        raise SystemExit(
            "Download failed.\n"
            f"  wrapper: {detail}\n"
            f"  yt-dlp:  {err[-1] if err else 'no error text'}\n"
            "If this is login-required, age-gated or region-locked, say so rather than retrying."
        )
    return files[0], "yt-dlp (direct fallback)"


def drop_near_pins(primary: list[dict], pinned: list[dict], tolerance: float = 0.6) -> list[dict]:
    """Throw away detail-engine frames that land on top of a pinned one.

    With `--hook`, or with `--start/--end` inside the hook window, the scene pass
    and the cue pass sample the same seconds, and the merged list then carries the
    same picture twice with two different filenames. That is pure token waste and
    it makes the timeline read as though something happened twice.
    """
    if not pinned or not primary:
        return primary
    pins = sorted(f["timestamp_seconds"] for f in pinned)
    kept = []
    for frame in primary:
        t = frame["timestamp_seconds"]
        if any(abs(t - pin) <= tolerance for pin in pins):
            Path(frame["path"]).unlink(missing_ok=True)
            continue
        kept.append(frame)
    return kept


def hook_timestamps(seconds: float, duration: float) -> list[float]:
    window = min(seconds, duration if duration > 0 else seconds)
    step = 1.0 / HOOK_FPS
    out, t = [], 0.0
    while t < window:
        out.append(round(t, 2))
        t += step
    return out


def _self_test() -> int:
    """No network. `download` is swapped for a stub that behaves like yt-dlp on
    the one point that matters here: pointed at a folder that already holds
    video.mp4, it keeps that file and hands it back as the result."""
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

    SELF_TEST_ROOT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    base = Path(tempfile.mkdtemp(prefix=f"{stamp}-", dir=str(SELF_TEST_ROOT)))

    # Made-up ids in the YouTube shape; no real video is named here.
    vid_a, vid_b = "AAAAAAAAAa1", "BBBBBBBBBb2"
    link_a = f"https://www.youtube.com/watch?v={vid_a}"
    link_b = f"https://www.youtube.com/watch?v={vid_b}"
    calls: list[tuple[str, Path]] = []

    def pixels(source: str) -> str:
        return f"pixels of {source}\n"

    def fake_download(source: str, dest: Path, quality: str) -> tuple[Path, str]:
        calls.append((source, dest))
        target = dest / "video.mp4"
        if target.exists():
            return target, "stub (kept the file already there, as yt-dlp does)"
        target.write_text(pixels(source))
        return target, "stub download"

    def out_dir(name: str, source: str) -> Path:
        """A work folder the way `--out-dir <folder>` makes it."""
        return work_dir_for(source, str(base / name))

    saved = globals()["download"]
    globals()["download"] = fake_download
    try:
        def legacy_file_refused():
            # The folder as a reused --out-dir left it before this fix: link A's
            # video.mp4 at the top, with no record beside it.
            work = out_dir("legacy", link_b)
            stale = work / "video.mp4"
            stale.write_text(pixels(link_a))
            video, note = fetch_video(link_b, work, "720")
            assert video != stale, f"handed back the other link's file ({note})"
            assert video.read_text() == pixels(link_b), f"{video} holds {video.read_text()!r}"
            assert video.parent.parent == work, f"not a subfolder of the work folder: {video}"
            assert video.parent.name.startswith(f"{DOWNLOAD_PREFIX}{vid_b}-"), video.parent.name
            assert read_record(video.parent)["youtube_id"] == vid_b, "record missing"
            assert stale.read_text() == pixels(link_a), "the old file was touched"

        check("a reused --out-dir holding another link's video.mp4 does not return it",
              legacy_file_refused)

        def recorded_other_link_refused():
            work = out_dir("reused", link_a)
            first, _ = fetch_video(link_a, work, "720")
            assert first == work / "video.mp4", f"first download went to {first}"
            second, note = fetch_video(link_b, work, "720")
            assert second != first, f"link B got link A's download ({note})"
            assert second.read_text() == pixels(link_b), f"{second} holds {second.read_text()!r}"
            assert first.read_text() == pixels(link_a), "link A's download was overwritten"

        check("a recorded download of link A is never reused for link B",
              recorded_other_link_refused)

        def same_link_reused():
            work = out_dir("same", link_a)
            first, _ = fetch_video(link_a, work, "720")
            before = len(calls)
            again, note = fetch_video(link_a, work, "720")
            short, _ = fetch_video(f"https://youtu.be/{vid_a}?t=30", work, "720")
            assert again == first == short, f"{first} / {again} / {short}"
            assert len(calls) == before, "downloaded the same link twice"
            assert note.startswith("cached"), f"note was {note!r}"

        check("the same video, in any YouTube link shape, reuses its download", same_link_reused)

        def switching_back_and_forth():
            work = out_dir("switch", link_a)
            a1, _ = fetch_video(link_a, work, "720")
            b1, _ = fetch_video(link_b, work, "720")
            before = len(calls)
            a2, _ = fetch_video(link_a, work, "720")
            b2, _ = fetch_video(link_b, work, "720")
            assert (a2, b2) == (a1, b1), f"A {a1} then {a2}, B {b1} then {b2}"
            assert a2.read_text() == pixels(link_a), f"link A's file holds {a2.read_text()!r}"
            assert b2.read_text() == pixels(link_b), f"link B's file holds {b2.read_text()!r}"
            assert len(calls) == before, "re-downloaded a link the folder already held"

        check("switching links in one folder returns each link's own file",
              switching_back_and_forth)

        def changed_file_refused():
            work = out_dir("changed", link_a)
            first, _ = fetch_video(link_a, work, "720")
            first.write_text("a different video put here by hand, longer than the first\n")
            again, note = fetch_video(link_a, work, "720")
            assert again != first, f"trusted a file whose size changed ({note})"
            assert again.read_text() == pixels(link_a), f"{again} holds {again.read_text()!r}"

        check("a recorded file whose size changed is downloaded again", changed_file_refused)

        def exact_link_off_youtube():
            one, two = "https://vimeo.com/123456", "https://vimeo.com/654321"
            work = out_dir("vimeo", one)
            v1, _ = fetch_video(one, work, "720")
            v2, _ = fetch_video(two, work, "720")
            v1_again, _ = fetch_video(one, work, "720")
            assert v1 != v2 and v1_again == v1, f"{v1} / {v2} / {v1_again}"
            assert v2.read_text() == pixels(two), f"{v2} holds {v2.read_text()!r}"

        check("a link off YouTube matches only on the exact link", exact_link_off_youtube)
    finally:
        globals()["download"] = saved

    if failures:
        print("SELF-TEST FAILED")
        for line in failures:
            print("  -", line)
        print(f"  (scratch left in {base})")
        return 1
    print(f"watch self-test: {passed} cases pass (scratch left in {base})")
    return 0


def main() -> int:
    if "--self-test" in sys.argv[1:]:
        return _self_test()

    ap = argparse.ArgumentParser(description="Watch a video (frames + transcript)")
    ap.add_argument("source", help="Video URL or local file path")
    ap.add_argument("--detail", choices=list(DETAIL_CAPS), default="balanced",
                    help="transcript=no frames, efficient=keyframes, balanced=scene (default), deep=uncapped")
    ap.add_argument("--hook", nargs="?", const=HOOK_DEFAULT_SECONDS, type=float, default=None,
                    metavar="SECONDS",
                    help=f"Pin a frame every {1/HOOK_FPS:g}s across the opening (default {HOOK_DEFAULT_SECONDS:g}s)")
    ap.add_argument("--start", default=None, help="Range start (SS, MM:SS, HH:MM:SS)")
    ap.add_argument("--end", default=None, help="Range end")
    ap.add_argument("--timestamps", default=None,
                    help="Comma-separated absolute times to pin a frame at (transcript cues)")
    ap.add_argument("--max-frames", type=int, default=None, help="Override the detail cap")
    ap.add_argument("--resolution", type=int, default=512, help="Frame width px (default 512)")
    ap.add_argument("--fps", type=float, default=None, help="Override auto-fps (clamped to 2)")
    ap.add_argument("--quality", default="720", help="Max download height (default 720)")
    ap.add_argument("--out-dir", default=None, help="Working directory")
    ap.add_argument("--no-dedup", action="store_true", help="Keep near-identical frames")
    ap.add_argument("--no-whisper", action="store_true", help="Skip the local whisper fallback")
    ap.add_argument("--json", action="store_true", help="Emit machine-readable json instead")
    ap.add_argument("--self-test", action="store_true",
                    help="Offline check that a reused work folder never hands back another link's video")
    args = ap.parse_args()

    missing = preflight()
    if missing:
        print(f"Missing: {', '.join(missing)}. Install with: brew install ffmpeg", file=sys.stderr)
        return 2

    work = work_dir_for(args.source, args.out_dir)
    frames_dir = work / "frames"
    start = parse_time(args.start)
    end = parse_time(args.end)
    cues = parse_timestamps(args.timestamps)
    cap = args.max_frames if args.max_frames is not None else DETAIL_CAPS[args.detail]

    # --- video ------------------------------------------------------------
    video_path: Path | None = None
    fetch_note = "skipped (transcript detail, no frames needed)"
    needs_pixels = args.detail != "transcript" or bool(cues) or args.hook is not None
    if needs_pixels:
        say("fetching the video")
        video_path, fetch_note = fetch_video(args.source, work, args.quality)
    elif not is_url(args.source):
        video_path = Path(args.source).expanduser().resolve()
        fetch_note = "local file"

    meta = get_metadata(str(video_path)) if video_path else {"duration_seconds": 0.0}
    duration = meta.get("duration_seconds") or 0.0

    # --- frames -----------------------------------------------------------
    frames: list[dict] = []
    engine_meta: dict = {"engine": "none", "selected_count": 0}
    cue_meta: dict = {}

    if args.hook is not None:
        cues = sorted(set(cues + hook_timestamps(args.hook, duration)))

    if needs_pixels and video_path:
        pinned: list[dict] = []
        if cues:
            # `cap` is 0 at transcript detail, where cue frames are the *only*
            # frames, so they get the whole budget the user set (or none at all).
            # Otherwise reserve half the cap for cues so the detail engine can
            # never evict a moment the speaker explicitly pointed at.
            if cap is None:
                cue_cap = None
            elif cap == 0:
                cue_cap = args.max_frames
            else:
                cue_cap = max(1, cap // 2)
            say(f"pinning {len(cues)} frames at exact timestamps")
            pinned, cue_meta = extract_at_timestamps(
                str(video_path), frames_dir, cues,
                resolution=args.resolution, max_frames=cue_cap,
                start_seconds=start, end_seconds=end,
            )

        if args.detail == "transcript":
            frames = pinned
            engine_meta = {"engine": "cue-only", "selected_count": len(pinned)}
        else:
            remaining = None if cap is None else max(1, cap - len(pinned))
            window = (end if end is not None else duration) - (start or 0.0)
            window = window if window > 0 else duration
            budget = remaining if remaining is not None else 100
            if start is not None or end is not None:
                fps, target = auto_fps_focus(window, budget)
            else:
                fps, target = auto_fps(window, budget)
            if args.fps:
                fps = min(args.fps, MAX_FPS)
                target = budget

            if args.detail == "efficient":
                say("decoding keyframes")
                primary, engine_meta = extract_keyframes(
                    str(video_path), frames_dir, resolution=args.resolution,
                    max_frames=remaining, start_seconds=start, end_seconds=end,
                    dedup=not args.no_dedup,
                )
            else:
                say(
                    f"scanning {format_time(window)} for scene changes"
                    " (a full decode; fast on h264, brutal on AV1)"
                )
                primary, engine_meta = extract_scene_or_uniform(
                    str(video_path), frames_dir, fps=fps, target_frames=target,
                    resolution=args.resolution, max_frames=remaining,
                    start_seconds=start, end_seconds=end, dedup=not args.no_dedup,
                )
            primary = drop_near_pins(primary, pinned)
            engine_meta["selected_count"] = len(primary)
            frames = merge_frames(primary, pinned)

    # --- transcript -------------------------------------------------------
    say("resolving the transcript")
    segments, route, notes = resolve_transcript(
        args.source, work, video_path, allow_whisper=not args.no_whisper
    )
    segments = filter_range(segments, start, end)
    transcript_text = format_transcript(segments) if segments else ""
    if transcript_text:
        (work / "transcript.txt").write_text(transcript_text, encoding="utf-8")
    elif (work / "transcript.txt").exists():
        # A reused work folder still holds an earlier link's words; overwrite them
        # so nobody opening the folder reads another video's transcript as this one's.
        (work / "transcript.txt").write_text(
            f"No transcript on any route for {args.source}\n", encoding="utf-8"
        )

    payload = {
        "source": args.source,
        "work_dir": str(work),
        "video": str(video_path) if video_path else None,
        "fetch": fetch_note,
        "duration_seconds": round(duration, 2),
        "duration": format_time(duration) if duration else "unknown",
        "detail": args.detail,
        "range": {"start": start, "end": end},
        "frames": frames,
        "frame_engine": engine_meta,
        "cue_frames": cue_meta,
        "transcript_route": route,
        "transcript_notes": notes,
        "transcript_segments": len(segments),
        "transcript_path": str(work / "transcript.txt") if transcript_text else None,
    }
    (work / "meta.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(payload, indent=2))
        return 0

    # --- the report Claude reads -----------------------------------------
    out: list[str] = []
    out.append(f"Source     {args.source}")
    out.append(f"Duration   {payload['duration']}  ({fetch_note})")
    if video_path:
        out.append(f"Video      {video_path}")
    span = ""
    if start is not None or end is not None:
        span = f"  [{format_time(start or 0)} → {format_time(end) if end else 'end'}]"
    dropped = engine_meta.get("deduped_count", 0)
    dropped_note = f", {dropped} near-duplicates dropped" if dropped else ""
    n_pinned = cue_meta.get("selected_count", 0)
    n_engine = len(frames) - n_pinned
    split = f"{n_engine} via {engine_meta.get('engine')}" if n_engine else "all pinned"
    out.append(
        f"Frames     {len(frames)} at {args.detail} detail{span}"
        f" ({split}{dropped_note})"
    )
    if n_pinned:
        pinned_kind = "hook window" if args.hook is not None else "pinned cue"
        out.append(f"           {n_pinned} {pinned_kind} frames")
    out.append(f"Transcript {route}, {len(segments)} segments")
    for note in notes:
        out.append(f"           · {note}")
    if (duration > 600 and args.detail in ("balanced", "efficient")
            and start is None and end is None):
        out.append(
            "NOTE       Over 10 minutes on a full scan, so frame coverage is sparse. "
            "Re-run with --start/--end on the part that matters."
        )
    if not segments:
        out.append("NOTE       No transcript on any route. This is frames only; say so in the answer.")
    out.append(f"Work dir   {work}")
    out.append("")

    if transcript_text:
        out.append("=== TRANSCRIPT ===")
        out.append(transcript_text)
        out.append("")

    out.append("=== FRAMES (read every path) ===")
    for frame in frames:
        out.append(
            f"t={format_time(frame['timestamp_seconds'])}  "
            f"{frame['path']}  ({frame['reason']})"
        )
    if not frames:
        out.append("(none)")

    print("\n".join(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
