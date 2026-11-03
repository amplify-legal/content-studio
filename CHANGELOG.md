# Changelog

What changed in the pack, newest first. After a `git pull`, read the newest entry, then redo the copy in `SETUP.md` step 4.

## 2026-11-03

The first refresh since the 5 Oct version. Most of it comes from a multi-day build of podcast and tutorial shorts (about 230 numbered fixes, hundreds of renders, 4 review rounds), written down as method.

### The shorts builder: 10 new rules

`skills/shorts-editor/SKILL.md` has a new section, "Before you build a short", with a reading order and 10 rules a builder must not break. Each was broken at least once on that build:

1. Solve each panel's scale and top row from the rules together; never place it and clamp.
2. Nothing black and nobody small: a narrow crop sits over its own blurred picture, and a face too small goes full frame.
3. Measure each caption against the faces on screen, and lay caption lines out by a shortest path, not greedily.
4. A card shows only around its key word, split at a word boundary.
5. Read the hook from where it starts, never from 0.
6. Fix the spec's own fields, not only the code that overrides them, and dry-plan every spec you touched.
7. Clean the sound and measure it with a band meter, before and after.
8. A tutorial short is built in the tutorial look from its own sidecar, its screen masked frame by frame, and its words read against your off-limits topics first.
9. One render supervisor per lane, never stop a runner with builds in flight, and never kill or resume a frozen job.
10. A checker that didn't build the short reads it at full resolution, from frames keyed on that render; an `ok` row is not a pass.

Also in shorts-editor: the caption floor is now a 47px capital H (it was 35px), loudness is -14 LUFS (it was -16), entrances ease out with no overshoot, GSAP is loaded from a local `assets/vendor/` folder instead of a CDN (no network inside a render), and 3 new rows in the errors table.

### The edit lab book, new

`reference/edit-lab/`: 6 files on how each editing technique was got to work (captions, picture, motion, sound, privacy and the pipeline), what was tried and failed, and why. It installs to `content/reference/edit-lab/`, which the older copy line didn't reach.

### The example podcast and tutorial shorts pipeline, new

`examples/podcast-shorts-pipeline/`: the reference builder behind the 10 rules. One spec in, a finished 1080x1920 short out, with its poster, contact sheet and checks file. It has the looks pages, the tutorial look, a lane runner, invented example specs, `--selftest` and `anim_selftest.py`, and its README carries the lessons of the build. Setup is `SETUP.md` step 13b. It needs Playwright with a Chromium, OpenCV, an `ffmpeg` with libass and a few free Google fonts; on Linux, one `config.json` line points its monospace font somewhere other than macOS's Menlo.

### New skills and taste templates

- `director`: runs before every recording, asks only what the brief hasn't answered, and writes the frame into the brief.
- `search-visibility`: the search engines the waterfall calls: the searched phrase, chapters from 0:00, description, tags, captions, the watch page, the blog and newsletter versions, the weekly search read. Live fixes carry an undo line.
- `templates/taste/kinds/`: one sheet per kind of video (tutorial, masterclass, short, podcast, live). Every recording, edit and review reads the kind's sheet first.
- New taste templates: `director.md`, `shorts-profiles.md`, `motion-craft.md`, `on-screen-graphics.md`, `live-training.md`. `shorts-formats.md` is rewritten as starting defaults with reasons.

### Other changes

- `cut-review`: a mechanical pass is never "ready"; it reads the brief's frame, the kind sheet and the edit lab; privacy frames sampled at 1 second; runs on every short.
- `content-waterfall`: new rules (a short is seen or reviewed before it's planned, every promise on camera is a live link before publish, a go on a video isn't a go on its caption) and it now calls `search-visibility`.
- `design-dna`: a finish pass and `page_check.py`, which reads a rendered page in a real browser (optional, needs Playwright).
- `media-gen`: rewritten, one image render at a time, more guards on video generation, prompt recipes.
- `watch`: a fresh folder per run, caption files proven fresh, and an optional route for your own channel's captions.
- `scripts/copy_check.py`: 5 advisory AI-tell warnings (they warn, never fail). `render_detached.sh` waits for its supervisor to report ready; `render_queue.sh` retries a paused start every 5 minutes instead of hanging.
- Reference: podcast edit (the frame follows the people, the trailer is the picked moments, more audio and caption rules), render reliability, workshop edit, lessons and the constitution (quality, then consistency, then speed).
- Docs: `SETUP.md`, `START-HERE.md`, `INSTALL-PROMPT.md` and `TROUBLESHOOTING.md` cover all of the above. `.gitignore` now also keeps GSAP, stills and the example pipeline's own config, queues and logs out of git.
