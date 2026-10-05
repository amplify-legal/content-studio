# scripts

10 scripts, installed to `scripts/` in your project and run from your project root. Standard library Python and bash only, nothing here needs a key, and nothing here sends anything anywhere.

| Script | What it does | Offline proof |
|---|---|---|
| `copy_check.py` | Checks copy before it ships: always-on form rules (no em dashes, no bare `host/path` link without `https://`), an editable table of banned phrases and claims, optional rules under `--strict`, and an advisory voice tier that never fails a run | `--self-test` |
| `first_taste_check.py` | The check after your first taste-file sitting: the file exists, 3 separate entries, 3 passages in your own words, a rule written under them, no template brackets left | run it on your file |
| `verify_loop.py` | Render, check, repair from a bounded table, render again, and wake a model only for what a script cannot settle. Drives the 4-file build convention; `--scaffold` writes stubs | `--selftest` |
| `render_detached.sh` | Runs a long job outside the conversation: its own process session, keep-awake, memory gate, runaway-file guard, 60 second status trail, one retry, `stop` for the whole process group | |
| `render_queue.sh` | Several long jobs overnight, one at a time, each behind the preflight and the strict memory gate | |
| `render_preflight.sh` | Before a long job: free disk first, ffmpeg present, a lint for any `-loop` image input with no output `-t`, plus your own `RENDER_PREFLIGHT` check | run it |
| `render_status.sh` | "Is it actually working?" Answers from the files: is the output growing, is the heartbeat fresh, what the log says | run it on a folder |
| `render_soak.sh` | An evidence run for renders that never finish: a monolithic encode and your parallel finalize at several worker counts, each time-limited, with memory sampled | |
| `yt_download.sh` | Downloads a video, a slice or the audio, and heals itself when yt-dlp goes stale (upgrade and retry, then cookies) | `--help` |
| `serve_outputs.py` | Serves a folder on localhost with HTTP Range support (206), so review pages with `<video>` play and seek in a browser pane. Default `./outputs` on port 4200 | `--selftest` |

The reasons behind every render behaviour are in `content/reference/render-reliability.md`. The verify loop's contract is in `content/reference/verify-loop.md`. The thinking behind the copy checker is in `content/reference/the-checks.md`.

---

## The most common commands

```
python3 scripts/copy_check.py draft.md
python3 scripts/first_taste_check.py content/taste/hooks.md

scripts/render_detached.sh start ep-01 --watch content/videos/ep-01/renders -- "python3 content/videos/ep-01/build/finalize.py"
scripts/render_detached.sh status ep-01
scripts/render_detached.sh stop ep-01

scripts/render_queue.sh add ep-01 --watch content/videos/ep-01/renders -- "python3 content/videos/ep-01/build/finalize.py"
scripts/render_queue.sh run
scripts/render_queue.sh status

python3 scripts/verify_loop.py content/videos/ep-01 --scaffold
python3 scripts/verify_loop.py content/videos/ep-01 --max-iterations 4 --deep --deadline 07:00

scripts/yt_download.sh "<video url>" --section 00:01:00-00:01:30 --codec h264
python3 scripts/serve_outputs.py --root outputs --port 4200
```

## Environment variables the render scripts read

All optional, all with working defaults.

| Variable | Default | What it changes |
|---|---|---|
| `RENDER_DIR` | `./.renders` | Where state and logs live |
| `RENDER_ROOT` | current directory | Where the job runs from |
| `RENDER_GATE` | unset | `strict` waits for memory however long it takes (the queue sets it) |
| `RENDER_GATE_MAX` | 30 | Minutes to wait for memory before going anyway |
| `RENDER_MAX_BYTES` | 4294967296 | The runaway ceiling: a watched file past it gets its encoder an interrupt |
| `RENDER_GUARD_PROC` | `ffmpeg` | Which process the runaway guard interrupts |
| `RENDER_PREHOOK` | unset | A command run once before the job |
| `RENDER_PAUSE_CHECK` | unset | A command that exits 0 when renders must wait (a screen recording is live, your memory brake is on). `start` then refuses with exit 75 |
| `RENDER_MIN_DISK_GB` | 25 | The preflight refuses below this |
| `RENDER_LINT_GLOBS` | `content/videos/*/build/*.py .claude/skills/*/scripts/*.py scripts/*.py` | Which pipeline scripts the `-loop` lint reads |
| `RENDER_PREFLIGHT` | unset | Your own check, run before each queued job |

`render_soak.sh` and `yt_download.sh` document their own variables in their headers. `verify_loop.py` reads `VERIFY_LOOP_MEMORY_WAIT_MAX` (seconds, default 900).

---

## Scripts that live with their skill

These ship inside the skill that uses them, so they install with it:

| Where | What |
|---|---|
| `.claude/skills/shorts-editor/scripts/` | The shorts pipeline: transcription (with keyterms), cuts, captions, cards, the render |
| `.claude/skills/media-gen/scripts/media_gen.py` | One gateway for images and video: thumbnails, title cards, story animations |
| `.claude/skills/design-dna/scripts/dna_check.py` | Scores an HTML page against the design spec you write |
| `.claude/skills/watch/scripts/` | Pulls a video, slices it into timestamped frames, and gets the transcript by whichever route works |

---

## Why so few

The system these came out of has well over 100 scripts. Most are welded to one business's data, accounts and folder shapes: calendars, inboxes, deal boards, finance exports, meeting recorders, posting runners. Shipping them would hand you a folder of things that fail on first run with an error about a file you have never heard of. The ones here are the ones that are about the craft itself and run on any project. If you want one of the others, writing your own against your own data is a smaller job than adapting somebody else's, and it will match the shape of your business.
