# The install levels, and how to pick one

> The one table the install and the profile both use. `SETUP.md` asks the preference questions and picks a level with the rules below; `creator-profile` recommends a level at the end of the deep dive with the same rules, using the richer answers in `content/profile/`. If the 2 disagree, say so and let the creator choose.

## What each level installs

| Level | Skills | Also | Keys needed | Setup time |
|---|---|---|---|---|
| `lite` | `creator-profile`, `content`, `director`, `post-writer`, `taste-builder`, `script-writer` | The constitution, the taste templates, the frameworks, the reference docs, `copy_check.py`, `first_taste_check.py`, the manual posting checklist in `SETUP.md` | None | About 10 minutes to install, then the first profile sitting (25 to 35 minutes): 35 to 45 minutes in all |
| `standard` | lite, plus `watch`, `long-form-editor`, `shorts-editor`, `cut-review`, `search-visibility`, `media-gen`, `design-dna`, `on-camera-board`, `content-waterfall` | ffmpeg, node, the Python packages, fonts and GSAP, the edit lab book, the render scripts (`render_detached.sh`, `render_preflight.sh`, `render_status.sh`), `serve_outputs.py`, `yt_download.sh`, `seo_updates.py` | None required. A transcription key is recommended (local whisper is the free fallback). `media-gen` needs a paid key only if you use it | About 2 hours over a few evenings, plus downloads |
| `full` | standard, plus `posting` (auto-post) | The posting module (`posting/`), the routines (`routines/`), the verify loop (`verify_loop.py`), the render queue (`render_queue.sh`, `render_soak.sh`), the example pipelines (`examples/`) | Each platform you post to by machine needs its own official app or token; `posting/README.md` lists them | Standard, plus 1 to 2 hours, plus whatever each platform's own approval takes (untested here; `posting/README.md` is the place that says) |

**Every level starts the same way:** the preference questions, the install for that level, then the `creator-profile` deep dive as the first sitting.

## The preference questions

Asked in `SETUP.md` before anything is copied, one at a time. They take about 2 minutes. The answers go into `content/setup/preferences.md` in the shape at the bottom of this file.

1. **Time today.** "How much time do you have for setup today? Under an hour, 1 to 2 hours, or an evening or more?"
2. **Editing.** "Who edits your videos? You, in your own editor; you, and you'd like this system to do the cutting; someone else; or you don't make video?"
3. **Posting.** "Do you want to press post yourself, or would you like posting done by machine once you've approved each piece? Or later?"
4. **Platforms.** "Which platforms do you post on now, and which do you want to?"
5. **Computer.** "Are you on a Mac, Linux, or Windows?"

## The pick, in order

Apply the first rule that matches for the **target level**, then rule 5 for **what to install today**.

1. They want posting done by machine once they approve each piece → target `full`.
2. They want this system to cut their videos or make shorts → target `standard`.
3. Someone else edits and they want a review gate on that editor's cuts → target `standard` (for `cut-review` and `watch`).
4. Otherwise → target `lite`.
5. **What to install today:** if they have under an hour today, install `lite` today whatever the target, record the target, and say when the next level makes sense ("upgrade me to standard" on an evening with 2 hours). Otherwise install the target.

Two guidelines that ride with the pick:

- **Learn first, automate after, hand off last** (`content/PRINCIPLES.md`, section 2). When the target is `full` and nothing has gone through the system yet, say once that `full` works best after 1 piece has shipped through `standard`, and let them choose. Posting at `full` stays in dry-run until they approve a row either way (`posting/README.md`).
- **Windows.** `lite` is files only, and Claude Code can do the copy on any computer it runs on. `standard` and `full` lean on bash and ffmpeg and are untested on Windows; the likely route is WSL with Ubuntu and the Linux lines in `SETUP.md`, labelled untested.

## The recommendation at the end of the deep dive

Same rules, with the profile's answers in place of the quick ones:

- Hours a week (`platforms.md`) under about 3, posting by hand, video edited elsewhere or no video → `lite`.
- They edit long recordings, want shorts from them, or publish on a search-led video platform → `standard`.
- They post 5 or more pieces a week across 3 or more platforms, want posting by machine, and at least 1 piece has shipped through `standard` → `full`.

Write the level and the reason in 2 lines built on their own words, then compare with `content/setup/preferences.md`. Never change the installed level without their word.

## Changing level

- **Up** ("upgrade me to standard", "go full"): `SETUP.md`, "Changing level". It runs only the new level's steps, never overwrites a taste file, and adds a dated line to `upgrades:` in `preferences.md`.
- **Down** ("take me back to lite"): nothing is deleted. Any scheduled routine and the posting runner are stopped first, then the skills above the chosen level move from `.claude/skills/` to `.claude/skills-parked/`, outside the folder Claude Code reads project skills from. The check is a new session's skill list, which no longer names them. Moving a folder back undoes it.

## `content/setup/preferences.md`

```markdown
> The setup choices, in the creator's words. Written by the install session; rewritten by "upgrade me to <level>" or "change my preferences". Read by creator-profile, content, and posting (at full).
updated: 2026-01-12

level: lite
target: standard
installed: 2026-01-12 (lite)
upgrades: none yet

time_today: under an hour
edits_video: "I edit in my own editor, but I'd love shorts made for me"
auto_posting: later
platforms_now: a video platform, a professional feed
platforms_wanted: a short-video platform
computer: mac

why this level: under an hour today, so lite now; standard is the target for shorts.
skipped on purpose: media-gen ("not paying for images yet")
```

`level` is one of `lite`, `standard`, `full`, and `scripts/profile_check.py --preferences` checks it. `auto_posting` is one of `no`, `later`, `yes`.
