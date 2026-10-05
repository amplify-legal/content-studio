# Content Studio

**The full local recording and editing setup we run every day, refined over months, with everything specific to one business taken out.** Ideation, taste, scripts, packaging, the board you film from, the long-form edit, vertical shorts, the review gate, the render discipline that stops a long job dying at 3am, and the waterfall that turns one recording into many pieces.

This is not a cut-down. It is the same system, anonymized. When we change the local system, this repo is refreshed.

It runs inside [Claude Code](https://docs.claude.com/en/docs/claude-code/overview). You clone it, copy its parts into your own project, and Claude does the work with you. Nothing here publishes anything, and nothing runs on its own until you wire it.

> Point Claude Code at this folder and say: **"Read START-HERE.md and set this up with me."**

---

## The one idea

**This system exists to amplify your creativity, not to replace your judgment.**

A question you answer beats a list you ignore. Every surface that produces something you put your name on opens by asking. Generation is the exception you ask for with explicit words ("just draft it"), not the default you have to fight.

And the order of the work is: **learn first, automate after, hand off last.** Your taste lives in plain files in your own words. Every skill reads those files and none of them restates them, so a correction goes in one place and every skill gets it at once. `reference/PRINCIPLES.md` is the constitution, and it wins over every process step in the repo.

---

## What is inside

| Folder | What it holds |
|---|---|
| `skills/` | 12 Claude Code skills, one folder each (table below) |
| `scripts/` | Shared tools: the verify loop, detached and queued renders, preflight and status checks, the copy checker, a video-friendly local server, a self-healing downloader |
| `reference/` | How the parts fit, the constitution, the podcast and workshop edit runbooks, render reliability, the verify loop contract, and `lessons.md`: the durable rules every expensive mistake taught us |
| `reference/frameworks/` | Shapes for a short, a pillar video, a carousel, a research brief, a send artifact, proof without bragging |
| `templates/taste/` | Your taste files, as empty templates with the structure and starting craft defaults. You fill them in your words |
| `templates/brand.md` | Your colours, fonts, caption style, logo and photo paths. The scripts read it |
| `examples/workshop-edit/` | A complete, working pipeline for editing a recorded workshop or training: silences, boundaries, blur config, captions, chapters, checks, handover |
| `routines/` | The morning content briefing, and an optional nightly posting refresh |

### The skills

| Skill | What it does |
|---|---|
| `content` | The one door. Every content thought goes through it, and it interviews you rather than generating at you |
| `taste-builder` | Does no content work. It interviews you and writes your taste files |
| `script-writer` | A script in your voice, from your own material |
| `post-writer` | Written posts, drafted, refined and checked |
| `watch` | Actually watches a video: frames and words together, not a transcript skim |
| `on-camera-board` | The surface you present from and draw on live while filming |
| `long-form-editor` | A long raw recording becomes content: the privacy pass, the cuts, several people on one camera, the finish |
| `shorts-editor` | One picked clip becomes a finished vertical short: word-timed captions, animated cards, music, self-checks |
| `cut-review` | The mechanical gate before you watch any cut, so your time goes to taste |
| `media-gen` | Thumbnails, title cards, story animations. The only skill that spends money, and it prints the cost first |
| `design-dna` | Your design system for any HTML surface, held as a measured record with a check script |
| `content-waterfall` | One recording becomes many pieces across platforms, with nothing posted without your approval |

---

## Requirements

| Need | For | Required? |
|---|---|---|
| Claude Code | Everything | Yes |
| `git` | Cloning this repo | Yes |
| `python3` 3.10 or newer | Every script | Yes |
| `ffmpeg` and `ffprobe` | Any video editing | For the edit half |
| `node` (gives `npx`) | Rendering the animated cards in shorts | For shorts |
| Python packages `pillow`, `numpy`, `requests` | Captions, caption checks, API calls | For the edit half |
| `yt-dlp` | Pulling a reference video to study | Optional |
| `ELEVENLABS_API_KEY` | Word-level transcription, the default engine (Scribe `scribe_v2` with a key-terms list) | Recommended |
| `DEEPGRAM_API_KEY` | The fallback transcriber (Deepgram `nova-3`, same key-terms list) | Optional |
| `faster-whisper` | Last-resort local transcription, no key and no network | Optional |
| `MIXROUTE_API_KEY` | Image and video generation in `media-gen`, through the MixRoute gateway. An optional Google Cloud project (`GOOGLE_CLOUD_PROJECT`) can bill images there instead | Optional, costs money |

Keys go in a `.env` file in your project root or in your shell profile. Never paste a key into a chat.

The ideation, taste, script and board half needs none of the video tools and no keys at all.

---

## Install

`SETUP.md` walks it step by step with a check after every step, on macOS and Linux. `INSTALL-PROMPT.md` has the prompt to paste into Claude Code so it does the copying for you. The short version:

```bash
git clone https://github.com/amplify-legal/content-studio.git
```

then copy `skills/` into your project's `.claude/skills/`, `scripts/` into `scripts/`, `reference/` into `content/reference/`, and `templates/taste/` into `content/taste/`, and run the self-tests. The full layout is in `START-HERE.md`.

**Tonight, 20 minutes, nothing to download:** bring 3 pieces by other people that made you stop scrolling, and finish the evening holding your first taste file, in your own words. It is the top of `SETUP.md`.

---

## What costs money

`media-gen` spends money on image and video generation. It prints the cost of every call before it spends and refuses anything over a ceiling you set. Transcription uses a paid speech-to-text key for the best word timings, with a free local fallback. Everything else costs nothing beyond your Claude plan and your computer's time. Check each provider's pricing page before you pick; prices move.

---

## What it will never do

- **Publish.** Drafts, queues and finished files are the output. You press the button.
- **Decide your taste.** It holds your answers and applies them. It never averages you toward what performs.
- **Show you a cut it has not reviewed.** `cut-review` runs before any cut reaches you.

---

## When something breaks

`TROUBLESHOOTING.md` has the errors these scripts actually produce, with the exact text and the fix.

## License

MIT. See `LICENSE`. The fonts, music and logos you add to `skills/shorts-editor/assets/` are yours to license; none ship here.
