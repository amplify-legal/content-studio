# Changelog

What changed in the pack, newest first. After a `git pull`, read the newest entry, then redo the copy in `SETUP.md` step 4.

## 2026-11-07

Three additions: a setup that fits you, posting by machine, and the lessons learned since 3 Nov. After a `git pull`, read `SETUP.md` "Changing level" before you redo the copy: step 4 now has one copy block per level.

### Setup in 3 levels, with a deep dive on you first

- `SETUP.md` opens with a 2-minute choice: 5 questions (time today, who edits, posting by hand or by machine, platforms, computer). The answers go in `content/setup/preferences.md` and pick a level.
- **lite** (about 35 to 45 minutes, no keys): the deep dive, the content door, the director, script and post writing, the taste files, a checklist for posting by hand. **standard** adds editing, shorts, cut review, search, media generation and the design system. **full** adds posting by machine, the routines, the verify loop and the example pipelines. `skills/creator-profile/reference/levels.md` is the one table.
- "Upgrade me to standard" runs only what the new level adds. Going down deletes nothing; it parks skills in `.claude/skills-parked/`.
- New skill `creator-profile`: a conversation in 3 sittings, saved after every answer. Who you are and how you want to come across; the business (what you sell, to whom, what a customer is worth, always asked, never estimated); your objectives, broad (12 months) and specific (the next 90 days and the one number to move); your style, read from 3 to 10 of your own pieces and played back for you to confirm; your inspirations, the ones you love and the ones you dislike, each torn down; your platforms and hours. It writes `content/profile/` and seeds the taste files, ends on a 1-page summary you confirm, and recommends a level. `profile_check.py --selftest` runs offline.
- The content door, the director, script-writer, post-writer, taste-builder and posting read your profile before their first question, and the door offers only what your level installed.
- `START-HERE.md` rule 12 changed: nothing publishes without your approval recorded on the row, and only through the posting module at full, proven by reading the platform back. `INSTALL-PROMPT.md` prompt 1 is now the one paste.

### Posting by machine (full level)

- New `posting/` module and `posting` skill. A weekly plan in `content/posting/plan.jsonl`, one leg per platform per slot. An approval needs a name, and drops when the file or the words change. Locked fields the night refresh can't touch.
- `runner.py` posts approved legs whose slot has come, through YouTube, LinkedIn and Instagram's official APIs (Composio as the easy route, the direct API as a stub). It runs dry until you add `--live`, refuses an account that is not yours (`whoami`), never posts a leg twice, proves every post by reading it back, and comments the full-video link once per leg. YouTube goes up private with its publish time set; a LinkedIn video carries its custom thumbnail through LinkedIn's Videos API.
- `watch.py` moves missed legs (a machine leg to the soonest open slot of its kind that week, a hand leg only once its day has ended), writes hand cards for TikTok and Substack, warns about legs not yet approved near their slot, and can run your reminder command. It never posts.
- The example config starts every platform on a fake route, so a practice week sends nothing anywhere. 3 offline self-tests. The adapters' real-account calls are ported from a live system and are untested in this generalized form; `posting/README.md` has the tested and untested table.
- content-waterfall, post-writer and the nightly posting refresh now point at the module.

### Lessons since 3 Nov

- `reference/lessons.md`: 18 new or changed lessons. Publishing: a short never waits for its full-video link (replaces the hold); a machine post first proves the account is yours; a hand post is marked posted only from the channel; an approval counts once it reaches the poster's copy; decide the mix before upload; testimonial names need permission; a cause in a script is sourced; a number on a cover says what was counted; a live apply lists every write by kind. Review: one board per round with letters never reused; build what was asked; reviews repeat and check every folded fix; 3 good options with no known fault; a video you never watched is no reference; a new format is learned from real winners; on a podcast the conversation comes first. Rendering: day and night render limits with a freeze instead of a kill; a watchdog on output size and CPU together.
- `reference/long-form-lessons.md`: 6 new error rows (a render that hangs only when detached, 2 builds racing on one cache, raw tracks deleted too early, a caption calibration carried to a new machine, fixes in the notes that never reached the render, a style study with no frames) and Part 6, 10 standing long-form rulings as starting defaults.
- The edit lab book: B16 and C1 to C6 in `privacy-and-pipeline.md` (from a podcast edit run in a cloud session overnight), `captions.md` 50 and 51 (the credit checked against the chin), `picture.md` 37, a new mix entry in `sound.md`, traps 20 to 23 in the README.
- Taste templates: new `carousels.md`; the podcast "conversation first" default in `kinds/podcast.md` and `director.md`; 2 tutorial lessons; a fifth review round's 6 shorts defaults in `shorts-formats.md`; pixel-diff proof and "a twin that moved a face is not offered" in `thumbnails.md`.
- Skills: `content` reads your profile before its first question and offers only the engines your install level has; `director` skips the audience questions on a podcast; `cut-review`, `long-form-editor`, `shorts-editor`, `media-gen`, `watch`, `script-writer` and `search-visibility` each carry the new lessons that touch them.
- New `routines/content-day.md`: an optional weekday routine for when you have a pipeline. Specialist sub-agents check the recording plan, the cuts waiting on review, shorts and posting, open promises and podcast guests, and you get one list of what content needs from you today, with minutes. It sends and posts nothing.
- New `scripts/seo_updates.py`: the weekly read of what Google changed in Search (3 public sources, no key), used by search-visibility's Friday measure. `--selftest` runs offline.

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
