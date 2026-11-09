# Content Studio

**The full content system we run every day, from the first idea to the post going out, refined over months, with everything specific to one business taken out.** A deep dive on you and your business, ideation, taste, scripts and posts in your voice, packaging, the board you film from, the long-form edit, vertical shorts, the review gate, the render discipline that stops a long job dying at 3am, the waterfall that turns one recording into many pieces, and posting by machine after your approval. With every lesson along the way written down.

This is not a cut-down. It is the same system, anonymized. When we change the local system, this repo is refreshed.

It runs inside [Claude Code](https://docs.claude.com/en/docs/claude-code/overview). You install as much of it as you want today (`lite`, `standard` or `full`), and Claude does the work with you. Nothing posts without your approval recorded on the row, and nothing runs on its own until you wire it.

> **The one paste.** Open Claude Code in the folder you do content work in, and paste prompt 1 from `INSTALL-PROMPT.md`. It asks you 5 quick questions, installs the level that fits, runs the checks, and starts the deep dive on you.
>
> Or just say: **"Read START-HERE.md and set this up with me."**

---

## The one idea

**This system exists to amplify your creativity, not to replace your judgment.**

A question you answer beats a list you ignore. Every surface that produces something you put your name on opens by asking. Generation is the exception you ask for with explicit words ("just draft it"), not the default you have to fight.

And the order of the work is: **learn first, automate after, hand off last.** It starts by learning who you are, what you sell and what the content is for. Your taste and your profile live in plain files in your own words. Every skill reads those files and none of them restates them, so a correction goes in one place and every skill gets it at once. `reference/PRINCIPLES.md` is the constitution, and it wins over every process step in the repo.

---

## The 3 levels

You pick one in the first 2 minutes of setup, from 5 questions: how much time you have today, who edits your videos, whether you want posting done by machine, which platforms, and which computer. Upgrade any day by saying "upgrade me to standard".

| Level | What it installs | Setup time | Keys needed |
|---|---|---|---|
| `lite` | `creator-profile`, `content`, `director`, `post-writer`, `taste-builder`, `script-writer`, the taste templates, the constitution, the copy checker, and a checklist for posting by hand | About 10 minutes, then a first sitting of 25 to 35 minutes: 35 to 45 minutes in all | None |
| `standard` | Lite, plus `watch`, `long-form-editor`, `shorts-editor`, `cut-review`, `search-visibility`, `media-gen`, `design-dna`, `on-camera-board`, `content-waterfall`, the edit lab book and the render scripts | About 2 hours over a few evenings, plus downloads | None required. A transcription key is recommended (a free local fallback exists); `media-gen` needs a paid key only if you use it |
| `full` | Standard, plus `posting` (posting by machine), the morning routine, the verify loop, the overnight render queue, and the example pipelines | Standard, plus 1 to 2 hours, plus each platform's own app approval | One official app or token per platform you post to by machine |

**Every level starts with the deep dive.** `creator-profile` is a conversation, never a questionnaire, in sittings you can stop and resume: who you are and how you want to come across; your business (what you sell, to whom, the price band, how a viewer becomes a customer, what one customer is worth, always asked and never assumed); your objectives for the next 12 months and one number for the next 90 days; your style, read off 3 to 10 of your own past pieces and played back for you to confirm; your inspirations, each torn down into what to steal and what to avoid; and your platforms and hours. It ends with a 1-page summary you confirm and a recommended level, with the reason.

The full list per level, and how the pick works, is `skills/creator-profile/reference/levels.md`.

---

## The module map

| Folder | What it holds | Level |
|---|---|---|
| `skills/` | 16 Claude Code skills, one folder each (table below) | each level adds its own |
| `scripts/` | Shared tools: the copy checker and the first taste check (lite); the detached render, preflight, status, the video-friendly local server, a self-healing downloader and the weekly Search changes read (standard); the verify loop, the render queue and the soak run (full) | per script |
| `reference/` | How the parts fit, the constitution, the podcast and workshop edit runbooks, render reliability, the verify loop contract, and `lessons.md`: the durable rules every expensive mistake taught us | lite |
| `reference/edit-lab/` | The edit lab book: how each editing technique was got to work (captions, picture, motion, sound, privacy and the pipeline), what was tried and failed, and why | standard |
| `reference/frameworks/` | Shapes for a short, a pillar video, a carousel, a research brief, a send artifact, proof without bragging | lite |
| `templates/taste/` | Your taste files, as empty templates with the structure and starting craft defaults. You fill them in your words; the deep dive seeds them | lite |
| `templates/taste/kinds/` | One sheet per kind of video (tutorial, masterclass, short, podcast, live): what that kind is for, read before a recording, an edit or a review | lite |
| `templates/brand.md` | Your colours, fonts, caption style, logo and photo paths. The scripts read it | lite |
| `posting/` | Posting by machine: the plan (one leg per platform per slot, each needing `approved_by`), the runner (dry-run by default, it posts approved legs and reads each one back from the platform), the watcher (moves missed legs and writes hand cards for platforms with no posting route), and one adapter per platform. Installs to `posting/` in your project; its own `README.md` connects the platforms and walks the dry week | full |
| `routines/` | The morning content briefing, an optional weekday content-day routine, and an optional nightly posting refresh | full |
| `examples/workshop-edit/` | A complete, working pipeline for editing a recorded workshop or training: silences, boundaries, blur config, captions, chapters, checks, handover | full |
| `examples/podcast-shorts-pipeline/` | The reference shorts builder for podcast and tutorial shorts: one spec in, one finished 1080x1920 short out, with its poster, contact sheet and checks. Invented example specs, self-tests, and the lessons of a multi-day build | full |

In your project, the deep dive writes `content/profile/` (`who.md`, `business.md`, `objectives.md`, `style.md`, `inspirations.md`, `platforms.md`, a `summary.md` you confirm, and `progress.md` so any session can pick it up), and setup writes your level to `content/setup/preferences.md`.

### The skills

| Skill | Level | What it does |
|---|---|---|
| `creator-profile` | lite | The deep dive on you, your business and your objectives, in sittings you can stop and resume. Reads your own past content and plays back your style. Ends with a summary you confirm and a recommended level |
| `content` | lite | The one door. Every content thought goes through it, and it interviews you rather than generating at you |
| `taste-builder` | lite | Does no content work. It interviews you and writes your taste files |
| `script-writer` | lite | A script in your voice, from your own material |
| `post-writer` | lite | Written posts, drafted, refined and checked |
| `director` | lite | Runs before every recording: asks only what the brief hasn't answered (how you want to come across, the goal, the one learning, what the viewer gets) and writes the answers into the brief as the frame the edit serves |
| `watch` | standard | Actually watches a video: frames and words together, not a transcript skim |
| `on-camera-board` | standard | The surface you present from and draw on live while filming |
| `long-form-editor` | standard | A long raw recording becomes content: the privacy pass, the cuts, several people on one camera, the finish |
| `shorts-editor` | standard | One picked clip becomes a finished vertical short: word-timed captions, animated cards, music, self-checks. For podcast and tutorial shorts it points at the example pipeline and the 10 rules from its build |
| `cut-review` | standard | The mechanical gate before you watch any cut, so your time goes to taste |
| `media-gen` | standard | Thumbnails, title cards, story animations. The only skill that spends money, and it prints the cost first |
| `design-dna` | standard | Your design system for any HTML surface, held as a measured record with a check script |
| `content-waterfall` | standard | One recording becomes many pieces across platforms, with nothing posted without your approval |
| `search-visibility` | standard | The search engines behind the waterfall, never a door: the searched phrase, chapters from 0:00, the description, tags, captions, the watch page, the blog and newsletter versions, and a weekly search read. Every live fix carries an undo line |
| `posting` | full | Posts the approved rows of your plan through each platform's official route, dry-run by default, and proves every post by reading the platform back. Platforms with no official route for your account stay hand cards |

---

## Requirements

| Need | For | Level |
|---|---|---|
| Claude Code | Everything | every level |
| `git` | Cloning this repo | every level |
| `python3` 3.10 or newer | Every script | every level |
| `ffmpeg` and `ffprobe` | Any video editing | standard |
| `node` (gives `npx`) | Rendering the animated cards in shorts | standard |
| Python packages `pillow`, `numpy`, `requests` | Captions, caption checks, API calls | standard |
| GSAP (`gsap.min.js`, `MotionPathPlugin.min.js`) | The animated cards load it from their own folder, never from a CDN. 2 download lines in `skills/shorts-editor/assets/README.md` | standard, for shorts |
| Fonts (Montserrat, variable and static Bold; DM Serif Display, Inter, Lexend Exa for the example pipeline's pages) | Captions and graphics. Free from Google Fonts; none ship here | standard, for shorts |
| `yt-dlp` | Pulling a reference video to study, and the style read of public videos | standard (an optional no-key extra at lite) |
| `playwright` with a local Chrome or Chromium (`python3 -m playwright install chromium`) | `design-dna`'s `page_check.py`, and the graphic layer and self-tests of the example shorts pipeline | optional |
| `opencv-python` and an `ffmpeg` built with libass | The example shorts pipeline (face reads, burned captions) | full, for the example pipeline |
| `ELEVENLABS_API_KEY` | Word-level transcription, the default engine (Scribe `scribe_v2` with a key-terms list) | standard, recommended |
| `DEEPGRAM_API_KEY` | The fallback transcriber (Deepgram `nova-3`, same key-terms list) | standard, optional |
| `faster-whisper` | Last-resort local transcription, no key and no network | standard, optional |
| `MIXROUTE_API_KEY` | Image and video generation in `media-gen`, through the MixRoute gateway. An optional Google Cloud project (`GOOGLE_CLOUD_PROJECT`) can bill images and story animations there instead | standard, optional, costs money |
| `YOUTUBE_OAUTH_TOKEN` | `watch` reading caption files of your own channel through the YouTube Data API (untested in this form; public videos need no token) | standard, optional |
| One official app or token per platform | Posting by machine; `posting/README.md` lists what each platform needs | full |

Keys go in a `.env` file in your project root or in your shell profile. Never paste a key into a chat. `lite` needs no keys and none of the video tools.

macOS and Linux are the tested computers. On Windows, `lite` works wherever Claude Code runs; `standard` and `full` are untested there.

---

## Install

`INSTALL-PROMPT.md`, prompt 1, is the one paste: Claude asks the 5 questions, installs your level, runs its checks and starts the deep dive. `SETUP.md` is what it follows, step by step with a check after every step, for each level. The short version, by hand:

```bash
git clone https://github.com/amplify-legal/content-studio.git ~/content-studio
```

then answer the 5 questions at the top of `SETUP.md`, run the step 4 copy blocks for your level, and say **"Start my profile"** in Claude Code. The full layout is in `START-HERE.md`.

What changed since the last version is in `CHANGELOG.md`.

---

## What costs money

`media-gen` spends money on image and video generation. It prints the cost of every call before it spends and refuses anything over a ceiling you set. Transcription uses a paid speech-to-text key for the best word timings, with a free local fallback. Posting by machine uses each platform's own official route; check each platform's own terms for what that costs, if anything. Everything else costs nothing beyond your Claude plan and your computer's time. Check each provider's pricing page before you pick; prices move.

---

## What it will never do

- **Post without you.** Nothing posts without your approval recorded on the row. At `lite` and `standard` you press the button. At `full` the posting module posts only the rows you approved, dry-run by default, through each platform's official route, and proves every post by reading the platform back. Never a session cookie, never a website scrape, never a script driving a site. Messages and connection requests to people are never automated.
- **Guess about your business.** A price, a customer's worth, a target: it asks, and writes `UNKNOWN` when you do not know.
- **Decide your taste.** It holds your answers and applies them. It never averages you toward what performs.
- **Show you a cut it has not reviewed.** `cut-review` runs before any cut reaches you.

---

## When something breaks

`TROUBLESHOOTING.md` has the errors these scripts actually produce, with the exact text and the fix.

## License

MIT. See `LICENSE`. The fonts, music, logos and the GSAP files you add to `skills/shorts-editor/assets/` are yours to license; none ship here.
