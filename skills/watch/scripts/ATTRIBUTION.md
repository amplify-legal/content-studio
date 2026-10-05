# Where the engine came from

`frames.py` and `vtt.py` are vendored, largely unchanged, from
**bradautomates/claude-video** (MIT, Copyright (c) 2026 Bradley Bonanno),
https://github.com/bradautomates/claude-video

They are the best-tested part of that project: scene-change frame selection with a
luma-delta dedupe pass, focused-range budgets, transcript-cue pinning, and a WebVTT
parser that collapses YouTube's rolling-duplicate auto-caption cues.

The lenses in `lenses/` are adapted from **alexlarcheveque/claude-watch** (MIT),
whose contribution is the creator framing: hook mode, retention mode, and the idea
that a video is worth sampling densely at the open and sparsely through the body.

Both are MIT. Keep this file with the skill, keep both credits in any fork, and
read each project's own licence before anything ships commercially.

## What this version changed, and why

- **Download goes through `yt_download.sh`**, which sits beside these scripts,
  rather than a bare `yt-dlp` call. That wrapper self-heals the monthly 403 that
  never says it is out of date, and it asks YouTube for h264 rather than AV1
  (see the AV1 trap in `SKILL.md`, which is the largest hidden cost in the whole
  pipeline). A direct `yt-dlp` call is still the fallback when the wrapper is
  missing.
- **Transcripts run on two free routes**: yt-dlp's own captions first, then local
  faster-whisper. No API key is needed and none is used. The upstream
  `setup.py` / `config.py` / `whisper.py` are dropped, because they exist to
  chase hosted transcription keys this skill does not need.
- **The interpreter is probed, not hard-coded.** faster-whisper is usually
  installed on one python out of the three or four a Mac carries, so
  `transcript.py` looks for an interpreter that can import it. `WATCH_PYTHON`
  puts yours at the front of that queue.
- **Em dashes were removed from comments** to match the pack's house style.
  Nothing else in `frames.py` or `vtt.py` was touched.
