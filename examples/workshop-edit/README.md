# Example pipeline: editing a recorded workshop

A working, config-driven pipeline for the hardest common long-form shape: a recorded video call with a shared deck, one or 2 presenters, and a gallery of attendees who did not agree to be on camera. It turns the raw recording into a full cut and a condensed cut, with attendees blurred and voices kept, karaoke captions, a slight speed-up, loudness normalised, chapters on the delivered timeline, a deep pass and a handover page.

It is an example to copy and adapt, not a black box. Every number in `config.example.json` marked EXAMPLE was measured on one specific recording and is wrong for yours. The craft behind each stage is in `content/reference/workshop-edit.md`; the skill that drives it is `long-form-editor`.

Tested end to end on a synthetic 30 second recording (every stage below ran green). `python3 build.py selftest` checks the caption and config logic offline.

## What you need

- `ffmpeg` and `ffprobe` on your PATH
- Python 3.9+ with `numpy` and `Pillow` (`pip install numpy pillow`)
- A word-level transcript in the Scribe JSON shape: `{"words": [{"text", "start", "end", "type": "word", "speaker_id"}]}`. Make it with the shorts-editor transcriber and your key terms (below).
- A caption font file (and optionally a display font for the opener) that you hold a licence for, in a `fonts/` folder. None is shipped.

## Set up

```bash
mkdir -p content/videos/<slug>/raw content/videos/<slug>/build
cp examples/workshop-edit/*.py examples/workshop-edit/config.example.json examples/workshop-edit/keyterms.example.txt content/videos/<slug>/build/
cd content/videos/<slug>/build
cp config.example.json config.json            # then edit it
cp keyterms.example.txt keyterms.txt          # then replace every {PLACEHOLDER} with the names on this tape
# put the recording at content/videos/<slug>/raw/workshop.mp4 (or point "recording" at it)
```

Every script finds its config through `--config <path>`, then the `WORKSHOP_CONFIG` environment variable, then `./config.json`. Paths inside the config are relative to the config file.

## The stages

| # | Stage | Command | What you check before moving on |
|---|---|---|---|
| 0 | Transcribe, names in the transcriber | `python3 ../../../../.claude/skills/shorts-editor/scripts/transcribe.py ../raw/workshop.mp4 --edit-dir . --keyterms-file keyterms.txt` (fallback: `transcribe_deepgram.py` with the same key terms; last resort `transcribe_local.py`) | Grep the transcript for every name in `keyterms.txt`. The engine is named in the output's header. |
| 1 | Measure the tape | Contact sheets and hand-off frames (see `long-form-editor`, step 2), then write `layouts`, `share`, `grids` and `probe_times` into the config | Every hand-off pinned **to the frame**, the seam measured every 10 s (take the narrowest), the presenters' tiles checked every 5 s |
| 2 | Silences | `python3 build.py silences` | If it finds none, the room is noisy: raise `threshold_db` toward -30 |
| 3 | Boundaries | `python3 boundary.py report` | Which cut points sit on speech, and where they will move |
| 4 | Slide reveals | `python3 slides.py build`, then `python3 slides.py audit <cut>` | No unit "cuts through a build"; extend any that does |
| 5 | Plan | `python3 build.py plan <cut>` | Segment count and runtime at 1.0x and at the delivered speed |
| 6 | Probe | `python3 build.py probe` | Open every probe PNG at full size: blur soft but present, every name strip unreadable, presenters sharp, deck below the browser bar |
| 7 | Render | `scripts/render_detached.sh start <slug>-render --watch ../renders -- "python3 build.py render <cut>"` | The joined file's video and audio durations agree within a frame |
| 8 | Captions | `python3 build.py captions <cut>` | Read the caption text back across every join: no word cut in half, nothing over a mouth |
| 9 | Finalise | `python3 build.py finalize <cut>` | Captions burn first, then the speed pass, then loudnorm |
| 10 | Chapters | `python3 build.py chapters <cut>` | On the delivered timeline; spot-check 2 against the file |
| 11 | Deep pass | `python3 check.py <cut>` | `status: green`, then the dense per-vector review and a person's watch |
| 12 | Publish kit | `python3 meta.py <cut> --check-links > payload.json` | Every on-camera promise is a live URL returning 200 |
| 13 | Handover | `python3 handover.py` | Files, lengths, what was left out on purpose, the open decisions with owners |

Optional: `python3 opener.py --slide ../renders/title-slide.png --duration 6 --out ../renders/opener-condensed.mp4 --line "Your title"` builds an animated opener that resolves onto a real frame of the next shot. Point the config's `overrides` block at it.

## How to adapt it

**Tape-specific, change for every recording:** `recording`, `transcript`, `layouts` (the hand-off times), `share` crops, `grids` (tile geometry, which tiles to keep sharp), `probe_times`, `cuts`, `no_tighten`, `overrides`, `deck_stills`, `splits`, `chapters`, `publish`, `handover`.

**Format-level, change once for your channel:** `frame`, `speed`, `video_codec_args`, `silence`, `blur`, `captions` (font, colours from `content/brand.md`, size, baseline), `grid_out_h`, `grid_y`.

**A different layout shape** (a stage camera, a 2x2 grid, a speaker-view recording): add a layout kind in `mode()` and a filter function beside `share_filter()` and `grid_filter()` in `build.py`, then add it to `seg_cmd()`. Keep `seg_cmd()` the only place a segment is built, so `probe` keeps showing you the shipping frame.

**A podcast instead of a workshop:** the plan, boundary, captions, finalise, chapters and check stages carry over unchanged. Replace the layout filters with your per-speaker crops and add name plates; `content/reference/podcast-edit-runbook.md` lists what a podcast build needs on top.

## Rules this code enforces, so you do not have to remember them

- A pause is cut only between 2 transcript words; a quiet word is never cut through.
- Boundaries snap to measured audio energy, never to the transcript's word spans.
- `boxblur` radius caps (luma 24 or less; chroma at most half the label strip's chroma height) are validated before any render, because ffmpeg fails them silently.
- Every overlaid input chain starts with `setpts=PTS-STARTPTS`; every looped image carries `-t`; every ffmpeg runs with `-nostdin` and a bounded wait with one retry.
- Audio is cut to each segment's real frame count, sample-exact, with 30 ms fades.
- The karaoke base colour is pinned before the highlight transitions; "one" stays a word; a false start is dropped, not de-dashed; caption groups break where language breaks, by shortest path.
- Captions burn before the speed pass; chapters are divided by the speed factor.

## What it does not do

- It does not pick the moments. A person picks the keep ranges in `cuts`.
- It does not clear privacy for you. The probe frames, the 1 fps full-resolution sweep of every share and the blur windows are checked by a person (`long-form-editor`, step 3). If your own workspace appears on screen, rebuild it clean instead of blurring it (`content/reference/lessons.md`, rule 9).
- It does not upload. `meta.py` writes a private payload; a person publishes after watching.
