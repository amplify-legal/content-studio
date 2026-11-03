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
| `skills/` | 14 Claude Code skills, one folder each (table below) |
| `scripts/` | Shared tools: the verify loop, detached and queued renders, preflight and status checks, the copy checker, a video-friendly local server, a self-healing downloader |
| `reference/` | How the parts fit, the constitution, the podcast and workshop edit runbooks, render reliability, the verify loop contract, and `lessons.md`: the durable rules every expensive mistake taught us |
| `reference/edit-lab/` | The edit lab book: how each editing technique was got to work (captions, picture, motion, sound, privacy and the pipeline), what was tried and failed, and why |
| `reference/frameworks/` | Shapes for a short, a pillar video, a carousel, a research brief, a send artifact, proof without bragging |
| `templates/taste/` | Your taste files, as empty templates with the structure and starting craft defaults. You fill them in your words |
| `templates/taste/kinds/` | One sheet per kind of video (tutorial, masterclass, short, podcast, live): what that kind is for, read before a recording, an edit or a review |
| `templates/brand.md` | Your colours, fonts, caption style, logo and photo paths. The scripts read it |
| `examples/workshop-edit/` | A complete, working pipeline for editing a recorded workshop or training: silences, boundaries, blur config, captions, chapters, checks, handover |
| `examples/podcast-shorts-pipeline/` | The reference shorts builder for podcast and tutorial shorts: one spec in, one finished 1080x1920 short out, with its poster, contact sheet and checks. Invented example specs, self-tests, and the lessons of a multi-day build |
| `routines/` | The morning content briefing, and an optional nightly posting refresh |

### The skills

| Skill | What it does |
|---|---|
| `content` | The one door. Every content thought goes through it, and it interviews you rather than generating at you |
| `taste-builder` | Does no content work. It interviews you and writes your taste files |
| `script-writer` | A script in your voice, from your own material |
| `post-writer` | Written posts, drafted, refined and checked |
| `watch` | Actually watches a video: frames and words together, not a transcript skim |
| `director` | Runs before every recording: asks only what the brief hasn't answered (how you want to come across, the goal, the one learning, what the viewer gets) and writes the answers into the brief as the frame the edit serves |
| `on-camera-board` | The surface you present from and draw on live while filming |
| `long-form-editor` | A long raw recording becomes content: the privacy pass, the cuts, several people on one camera, the finish |
| `shorts-editor` | One picked clip becomes a finished vertical short: word-timed captions, animated cards, music, self-checks. For podcast and tutorial shorts it points at the example pipeline and the 10 rules from its build |
| `cut-review` | The mechanical gate before you watch any cut, so your time goes to taste |
| `media-gen` | Thumbnails, title cards, story animations. The only skill that spends money, and it prints the cost first |
| `design-dna` | Your design system for any HTML surface, held as a measured record with a check script |
| `content-waterfall` | One recording becomes many pieces across platforms, with nothing posted without your approval |
| `search-visibility` | The search engines behind the waterfall, never a door: the searched phrase, chapters from 0:00, the description, tags, captions, the watch page, the blog and newsletter versions, and a weekly search read. Every live fix carries an undo line |

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
| GSAP (`gsap.min.js`, `MotionPathPlugin.min.js`) | The animated cards load it from their own folder, never from a CDN. 2 download lines in `skills/shorts-editor/assets/README.md` | For shorts |
| Fonts (Montserrat, variable and static Bold; DM Serif Display, Inter, Lexend Exa for the example pipeline's pages) | Captions and graphics. Free from Google Fonts; none ship here | For shorts |
| `playwright` with a local Chrome or Chromium (`python3 -m playwright install chromium`) | `design-dna`'s `page_check.py`, and the graphic layer and self-tests of the example shorts pipeline | Optional |
| `opencv-python` and an `ffmpeg` built with libass | The example shorts pipeline (face reads, burned captions) | For the example pipeline |
| `yt-dlp` | Pulling a reference video to study | Optional |
| `ELEVENLABS_API_KEY` | Word-level transcription, the default engine (Scribe `scribe_v2` with a key-terms list) | Recommended |
| `DEEPGRAM_API_KEY` | The fallback transcriber (Deepgram `nova-3`, same key-terms list) | Optional |
| `faster-whisper` | Last-resort local transcription, no key and no network | Optional |
| `MIXROUTE_API_KEY` | Image and video generation in `media-gen`, through the MixRoute gateway. An optional Google Cloud project (`GOOGLE_CLOUD_PROJECT`) can bill images and story animations there instead | Optional, costs money |
| `YOUTUBE_OAUTH_TOKEN` | `watch` reading caption files of your own channel through the YouTube Data API (untested in this form; public videos need no token) | Optional |

Keys go in a `.env` file in your project root or in your shell profile. Never paste a key into a chat.

The ideation, taste, script and board half needs none of the video tools and no keys at all.

---

## Install

`SETUP.md` walks it step by step with a check after every step, on macOS and Linux. `INSTALL-PROMPT.md` has the prompt to paste into Claude Code so it does the copying for you. The short version:

```bash
git clone https://github.com/amplify-legal/content-studio.git
```

then copy `skills/` into your project's `.claude/skills/`, `scripts/` into `scripts/`, `reference/` (the edit lab book included) into `content/reference/`, and `templates/taste/` (the kinds sheets included) into `content/taste/`, and run the self-tests. The example pipelines stay in the clone until you copy one into a video's folder. The full layout is in `START-HERE.md`.

What changed since the last version is in `CHANGELOG.md`.

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

MIT. See `LICENSE`. The fonts, music, logos and the GSAP files you add to `skills/shorts-editor/assets/` are yours to license; none ship here.
