---
name: watch
description: >
  Actually watch a video instead of skimming its transcript. Pulls the file, slices it into
  timestamped frames, gets the transcript by whichever route works, and hands both to Claude
  together. Use for - a YouTube link dropped with a reaction, "watch this", "what's in this
  video", "break down this hook", "why does this intro work", "tear down this thumbnail",
  "what did they say at 4:30", a competitor's video, a conference talk, a podcast episode,
  a tool demo, a local mp4 on this machine, or any moment where what is ON SCREEN matters
  and a transcript alone would miss it. NOT for reviewing your own cut before the person
  whose taste decides watches it (that is cut-review). NOT for rendering or editing (that is
  shorts-editor or long-form-editor). NOT for a transcript you only need as text (pull that straight from the
  platform).
user-invocable: true
---

# watch

**Load before any step:** `content/PRINCIPLES.md` (the constitution: it wins over every step here).

## Why this exists

A transcript is half a video. It cannot tell you that the claim at 0:04 lands over
a static face and the claim at 0:09 lands over a document zoom, that the title card
holds for 9 seconds, that the number on screen disagrees with the number being
said, or that the thumbnail's promise is contradicted by the first frame.

It also cannot tell you **who is on screen**, whose face is croppable, what got
accidentally shared on a screen share (a sidebar, a file path, a client name, an
attendee's name badge), or whether a visual is good enough to use. Those are the
questions people actually ask about video, and words alone cannot answer any of
them.

Frames routinely change the answer to the question you were about to ask. Run the
script before you answer, not after.

## Run it

```bash
python3 .claude/skills/watch/scripts/watch.py "<url-or-path>"
```

Then **Read every frame path it prints**, in one message with parallel calls so you
see them together. Each path carries its `t=MM:SS`, so you can line the frames up
against the transcript printed above them. Then answer through a lens.

The path assumes the skill is installed at `.claude/skills/watch/` in your project. If you installed it user-wide, use `~/.claude/skills/watch/` instead.

## Pick the lens before you run

The lens decides the flags, so choose first. Read the one file, not all 5.

| Lens | For | Flags it wants |
|---|---|---|
| `lenses/digest.md` | **Default.** What is in this, is it worth the time | `--detail balanced` |
| `lenses/hook.md` | The first 15s taken apart, the reusable formula | `--hook` |
| `lenses/packaging.md` | Thumbnail + title + first frame + first line as one package | `--hook`, plus the capture first |
| `lenses/retention.md` | Where viewers leave and the one edit that fixes it | `--detail balanced`, then `--start/--end` on soft spots |
| `lenses/study.md` | Mine the substance: claims, frameworks, numbers, who is in it | `--detail balanced` |

**A link dropped with a reaction and no instruction is `packaging`**, and the
verbatim capture of that reaction into `content/taste/packaging/inbox.md` (with
`by:` naming who sent it) happens *before* the run. The link is only a pointer;
the reason somebody sent it is the part worth keeping.

## Flags

| Flag | What it does |
|---|---|
| `--detail transcript` | No frames. Skips the download when captions exist. |
| `--detail efficient` | Keyframes only, cap 50. Near-instant. |
| `--detail balanced` | Scene-aware, cap 100. **Default.** |
| `--detail deep` | Scene-aware, uncapped. Expensive; only under 10 minutes. |
| `--hook [SECONDS]` | Pin a frame every 0.5s across the opening (default 15s), merged with the normal pass. Without this the open gets 3 frames and you are guessing. |
| `--start T --end T` | Focus a range. `SS`, `MM:SS` or `HH:MM:SS`. Budgets go denser inside a range. |
| `--timestamps T1,T2` | Pin frames at exact moments. See "Transcript cues" below. |
| `--resolution 1024` | Read on-screen text properly. Roughly 4x the image tokens, so use it on a range, never a whole video. |
| `--max-frames N` | Override the cap for a tighter budget. |
| `--quality 1080` | Download height, default 720. Bump only when detail on screen matters. |
| `--no-dedup` | Keep near-identical frames. Only when judging subtle motion. |
| `--no-whisper` | Skip the local transcription fallback. |
| `--json` | Machine-readable instead of the report. |

Frame sampling never exceeds 2 fps, whatever you ask for.

## Transcript cues

Scene detection misses the moments a presenter *tells* you to look ("look here",
"as you can see", "notice this") because pointing at a slide is a low visual
change. Those are often the most important frames in the video.

So: run once, read the transcript, pick the moments yourself, re-run pinned.

```bash
python3 .claude/skills/watch/scripts/watch.py "$URL" --detail transcript
# read it, choose the moments, then:
python3 .claude/skills/watch/scripts/watch.py <work dir from the first run>/video.mp4 --timestamps 4:32,7:10,9:55
```

Point the second run at the **downloaded file**, not the URL, so it does not
download twice. Cue frames are reserved against the cap before anything else, so
they never get evicted.

## What this costs: nothing but compute

No API key, anywhere in this skill. What it does need installed:

| Thing | Needed for | Install |
|---|---|---|
| `ffmpeg` / `ffprobe` | every frame, always, found on your PATH | `brew install ffmpeg` (macOS) or your package manager |
| `yt-dlp` | any URL, found on your PATH (the bundled wrapper installs it if missing) | `pip3 install yt-dlp` |
| `faster-whisper` | transcribing a file with no captions | `pip3 install faster-whisper` |

faster-whisper is optional. Skip it and a video with no captions comes back as
frames only, which the script says out loud in its header.

## Where the transcript comes from

A ladder, first one that works wins, and the run header always names which one did:

1. **yt-dlp captions** - native or auto captions, free, no key. Covers YouTube
   and most of the ~1,000 sites yt-dlp supports (Vimeo, Loom, Twitch and the
   rest). URLs only.
2. **faster-whisper, local** - offline, no key, and the only route that works on
   a file sitting on this machine, which is most of your own footage.

Nothing but extracted audio ever leaves the machine, and only on route 2. If you
pay for a hosted transcript API and want it first, add a function to
`scripts/transcript.py` that returns the same `[{start, end, text}]` shape and
call it at the top of `resolve()`. The rest of the pipeline will not notice.

**YouTube auto-captions arrive as rolling duplicates**, each line repeated as it
scrolls, which triples the token cost and makes every quote read like a stutter.
The word-level overlap collapse in `transcript.py` strips it. If you ever see a
stuttered quote in output, that collapse did not run.

## Traps, all of them found live

- **The python that runs this script is often not the one with faster-whisper on
  it.** A Mac commonly carries a Homebrew python, a system python and a conda
  python, with the library in exactly one. `transcript.py` probes for an
  interpreter that can import what the route needs rather than hard-coding one.
  Set `WATCH_PYTHON` to put yours first. Do not "fix" it back to `sys.executable`.
- **First whisper run downloads the model** (a few minutes, once, cached after).
  A 106-second clip that seems to hang on the first run is that download, not a
  stall. Set `WATCH_WHISPER_MODEL=base` for speed, `large-v3` for accuracy.
- **Downloads go through `scripts/yt_download.sh`**, the self-healing wrapper,
  because yt-dlp breaks against YouTube roughly monthly and the failure looks
  like a bare 403 that never says it is out of date. A direct `yt-dlp` call is
  the fallback, not the route.
- **YouTube serves AV1, and most Macs have no hardware decode for it.** This is
  the single biggest cost in the whole pipeline and it hides completely: the same
  20-minute video took **21 minutes of CPU** in one ffmpeg scene pass as AV1 and
  **34 seconds** as h264. `watch.py` passes `--codec h264` to `yt_download.sh`
  and prefers `vcodec^=avc1` in its own fallback, with a plain fallback when h264
  is not offered. If a scan ever feels impossibly slow, run `ffprobe` on the
  file: `av1` is the answer.
- **Over 10 minutes on a full scan is a sparse scan** and the script says so. Run
  the full pass to find the regions, then `--start/--end` into each one. Do not
  answer a detailed question off a sparse scan.
- **Login-required, age-gated or region-locked** fails at download. Say so plainly
  and stop; do not retry in a loop. Cookies are the escape hatch and the route is
  documented in the header of `scripts/yt_download.sh`.
- **Working files land in your system temp folder, under `watch/<hash>/`** (the run header prints the exact path as `Work dir`; on a Mac it is under `$TMPDIR`, on Linux usually `/tmp`) and a downloaded video is large.
  Delete the directory when the conversation moves on; keep it if follow-ups are
  likely, since a second run reuses the download.

## Token cost, so it is a decision and not a surprise

Frames are the cost; the transcript is nearly free. Roughly 200 image tokens per
frame at 512px, so:

- `efficient`, 50 frames, about 10k image tokens
- `balanced`, 100 frames, about 20k
- `--resolution 1024`, about 4x per frame

A 20-minute video at `balanced` is a normal read. `deep` on the same video is not.
When someone asks about one moment, a focused `--start/--end` beats a full scan on
both cost and answer quality.

**If you already watched a video this session, do not re-run for a follow-up.** The
frames and transcript are in context. Answer from them.

## What this does not do

- **`cut-review` owns your own cuts.** It has the gates and the checklist and it
  runs before the person whose taste decides watches anything. This skill reads
  other people's video, and your own only when the question is analysis rather
  than approval.
- **It never renders or edits.** That is `shorts-editor` or `long-form-editor`.
- **It is not a transcript fetcher.** If you only need the words as text, pull
  them from the platform instead of downloading a video.

## Engine credit

`frames.py` and `vtt.py` are vendored from `bradautomates/claude-video` (MIT); the
lens framing comes from `alexlarcheveque/claude-watch` (MIT). What changed in this
version, and why, is in `scripts/ATTRIBUTION.md`. Keep that file with the skill.
