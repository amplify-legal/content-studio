# Setup

**First, a 2-minute choice: 5 questions that pick how much of the system you install today. Then you walk only that level's steps.**

| Level | What you get | Setup time | Keys |
|---|---|---|---|
| `lite` | The deep dive on you and your business, the one door for ideas, the director before a recording, scripts and posts in your voice, your taste files, and a checklist for posting by hand | About 10 minutes to install, then the first profile sitting of 25 to 35 minutes: 35 to 45 minutes in all | None |
| `standard` | Lite, plus the video half: watching videos properly, the long-form edit, vertical shorts, the review gate, search work, thumbnails, the board you film from, and the waterfall that turns one recording into many pieces | About 2 hours over a few evenings, plus downloads you do not have to watch | None required. A transcription key is recommended; image generation needs a paid key only if you use it |
| `full` | Standard, plus posting by machine after your approval, the morning routine, the verify loop, the overnight render queue, and the example pipelines | Standard, plus 1 to 2 hours, plus each platform's own app approval | One official app or token per platform you post to by machine |

You can start small and upgrade any day: say **"upgrade me to standard"** in Claude Code and it runs "Changing level" at the bottom of this file. Nothing you wrote is ever overwritten.

Every step ends with a command you can run and a line saying what you should see. If the check does not say that, the fix is written under it. If something breaks and the fix does not cover it, `TROUBLESHOOTING.md` has the errors these scripts actually produce.

**The easiest route:** open Claude Code in your project folder and paste the prompt from `INSTALL-PROMPT.md`. It asks the 5 questions, installs your level and runs the checks with you. This file is what it follows.

### The names used below

- **The clone**: where you cloned this repo. The examples use `~/content-studio`.
- **Your project**: the folder you do content work in, and the folder you open Claude Code in for content. The examples use `~/my-content`. Use your own path everywhere you see it.

### What goes where

| From the clone | Into your project | Level |
|---|---|---|
| `skills/<the level's skills>` | `.claude/skills/` | each level adds its own |
| `scripts/copy_check.py`, `scripts/first_taste_check.py` | `scripts/` | lite |
| `scripts/render_detached.sh`, `render_preflight.sh`, `render_status.sh`, `serve_outputs.py`, `yt_download.sh`, `seo_updates.py` | `scripts/` | standard |
| `scripts/verify_loop.py`, `render_queue.sh`, `render_soak.sh` | `scripts/` | full |
| `reference/*.md` | `content/reference/` | lite |
| `reference/edit-lab/` | `content/reference/edit-lab/` | standard |
| `reference/PRINCIPLES.md` | `content/PRINCIPLES.md` (never over your own file) | lite |
| `reference/frameworks/*` | `content/frameworks/` | lite |
| `templates/taste/*` (the `kinds/` folder included) | `content/taste/` (never over your own files) | lite |
| `templates/brand.md` | `content/brand.md` (never over your own file) | lite |
| `routines/*.md` | `routines/` (never over your own filled-in copies) | full |
| `posting/` | `posting/` at your project root; its config to `content/posting/config.json` (never over your own file) | full |
| `examples/podcast-shorts-pipeline/` | `content/videos/<set>/pipeline/`, only when you build podcast or tutorial shorts (step 13b) | full |

The skills per level are listed in `skills/creator-profile/reference/levels.md`, which is the one place the install and the profile both read. Skills live in the project's own `.claude/skills/`, so they load only when you work in that project.

---

# 0. The 2-minute choice, every level

Claude Code asks these one at a time (the install prompt does it for you). Answer roughly; you can change any of it later.

1. **Time today.** Under an hour, 1 to 2 hours, or an evening or more?
2. **Editing.** Who edits your videos? You, in your own editor; you, and you'd like this system to do the cutting; someone else; or you don't make video?
3. **Posting.** Do you want to press post yourself, or have posting done by machine once you've approved each piece? Or later?
4. **Platforms.** Where do you post now, and where do you want to?
5. **Computer.** Mac, Linux or Windows?

**The pick** follows "The pick, in order" in `skills/creator-profile/reference/levels.md`. In short: posting by machine points at `full`; wanting this system to cut your videos or make shorts points at `standard`; otherwise `lite`. With under an hour today you install `lite` now and keep the bigger level as your target. On Windows, `lite` works anywhere Claude Code runs; `standard` and `full` are untested there (WSL with Ubuntu and the Linux lines below is the likely route).

Your answers are written to `content/setup/preferences.md` in step 2. The deep dive in step 7 asks more, recommends a level again from what it learns, and tells you if it disagrees.

---

# Every level: steps 1 to 7

## 1. Clone. 1 minute.

```bash
git clone https://github.com/amplify-legal/content-studio.git ~/content-studio
mkdir -p ~/my-content
cd ~/my-content
```

**Check it:** `ls ~/content-studio` shows `skills`, `scripts`, `reference` and `templates` among others.

**If `git` is not found:** on a Mac run `xcode-select --install` and wait; on Linux `sudo apt install git`.

## 2. Write your preferences. 1 minute.

Claude Code writes `content/setup/preferences.md` from your 5 answers, in the shape at the bottom of `skills/creator-profile/reference/levels.md`: the `level:` line, your `target:`, today's date, and your answers in your own words.

**Check it:**

```bash
python3 ~/content-studio/skills/creator-profile/scripts/profile_check.py --preferences content/setup/preferences.md
```

It prints `PASS     preferences` and `result: PASS`. **If it says the level is wrong,** the `level:` line must read exactly `level: lite`, `level: standard` or `level: full`.

**If `python3` is not found:** on a Mac run `xcode-select --install`; on Linux `sudo apt install python3`.

## 3. Read the constitution and argue with it. 10 minutes, now or before your first piece.

Open `~/content-studio/reference/PRINCIPLES.md` (it is copied into your project as `content/PRINCIPLES.md` in step 4). If you disagree with a principle, edit your copy after step 4, before anything is built on it. At lite with 45 minutes tonight, skim it now and argue with it on another evening; the deep dive does not need it done first.

**Check it:** you changed or deleted at least one line, or you decided out loud that you agree with all of it.

## 4. Copy for your level

Run the lite block. Then the standard block if your level is `standard` or `full`. Then the full block if your level is `full`. Each block only adds; none removes anything.

**Lite (every level):**

```bash
cd ~/my-content
mkdir -p .claude/skills scripts content/reference content/frameworks content/taste content/setup content/profile outputs
for s in creator-profile content director post-writer taste-builder script-writer; do cp -R ~/content-studio/skills/$s .claude/skills/; done
cp ~/content-studio/scripts/copy_check.py ~/content-studio/scripts/first_taste_check.py scripts/
cp ~/content-studio/reference/*.md content/reference/
cp -n ~/content-studio/reference/PRINCIPLES.md content/PRINCIPLES.md
cp ~/content-studio/reference/frameworks/*.md content/frameworks/
cp -Rn ~/content-studio/templates/taste/* content/taste/
cp -n ~/content-studio/templates/brand.md content/brand.md
```

**Standard (adds to lite):**

```bash
cd ~/my-content
mkdir -p content/videos
for s in watch long-form-editor shorts-editor cut-review search-visibility media-gen design-dna on-camera-board content-waterfall; do cp -R ~/content-studio/skills/$s .claude/skills/; done
for f in render_detached.sh render_preflight.sh render_status.sh serve_outputs.py yt_download.sh seo_updates.py; do cp ~/content-studio/scripts/$f scripts/; done
cp -R ~/content-studio/reference/edit-lab content/reference/
chmod +x scripts/*.sh .claude/skills/*/scripts/*.sh 2>/dev/null
```

**Full (adds to standard):**

```bash
cd ~/my-content
mkdir -p routines content/posting
cp -R ~/content-studio/skills/posting .claude/skills/
cp -R ~/content-studio/posting ./
cp -n ~/content-studio/posting/config.example.json content/posting/config.json
for f in verify_loop.py render_queue.sh render_soak.sh; do cp ~/content-studio/scripts/$f scripts/; done
cp -n ~/content-studio/routines/*.md routines/
chmod +x scripts/*.sh 2>/dev/null
```

The posting module's scripts run from your project root as `posting/scripts/...` and keep their state in `content/posting/` (`posting/README.md`, "What is in the folder"). Its example config starts every platform on the `fake` route, so nothing can leave your computer until you change it (`posting/README.md`, "Setup, per platform"). Connecting real accounts is step 16. The example pipelines stay in the clone until you copy one into a video's folder (step 13b).

`-n` means never overwrite. Your taste files, your brand file, your filled-in routines and your edited constitution are never replaced when you run this again to update. A taste template that is new in the clone (a new kind sheet, say) is still added, because `-n` only skips files you already have.

**Check it:**

```bash
ls .claude/skills
ls content/taste | head -40
ls content/taste/kinds
```

The first prints 6 folders at lite (`content`, `creator-profile`, `director`, `post-writer`, `script-writer`, `taste-builder`), 15 at standard (adding `content-waterfall`, `cut-review`, `design-dna`, `long-form-editor`, `media-gen`, `on-camera-board`, `search-visibility`, `shorts-editor`, `watch`) and 16 at full (adding `posting`). The second prints the taste templates. The third prints 6 kind files (`README.md`, `live.md`, `masterclass.md`, `podcast.md`, `short.md`, `tutorial.md`).

At standard and full, also: `ls content/reference/edit-lab` prints the 6 edit lab files (`README.md`, `captions.md`, `motion.md`, `picture.md`, `privacy-and-pipeline.md`, `sound.md`). At full, `ls routines` prints the routine files, `content-briefing.md` and `posting-refresh.md` among them, and `ls posting/scripts` prints `plan.py`, `runner.py`, `watch.py` and the `adapters` folder.

**If you see loose files like `SKILL.md` directly in `.claude/skills/`,** you copied the contents instead of the folders. Run the block again exactly as written. **If a `cp` line says `No such file or directory`,** the clone did not finish: run step 1 again and read what it says.

## 5. Tell your sessions the rules that matter most

Claude Code reads `CLAUDE.md` in the folder you open it in at the start of every session. Put these lines in your project's `CLAUDE.md`, not in `~/.claude/CLAUDE.md`, which loads in every project you own:

```bash
cd ~/my-content
cat >> CLAUDE.md <<'EOF'

Content work here follows content/PRINCIPLES.md, which wins over any process step. Taste lives in content/taste/ in my words; skills read it and never restate it. Who I am, my business and what the content is for live in content/profile/; read content/profile/summary.md before any content step.
My install level is in content/setup/preferences.md. When a skill names another skill my level did not install, say so and offer the upgrade; never fake it.
When I correct something, put the correction in the file the next session reads, in the same session: the skill, the taste file, the profile or the check script, never only in today's piece. Tell me which file.
Nothing publishes without my approval recorded on the row. At lite and standard I post by hand; at full only the posting module posts, and only rows I approved. A post is proven by reading the platform back. Long renders run through scripts/render_detached.sh. cut-review runs before any cut reaches me.
EOF
```

**Check it:** `grep -c "content/PRINCIPLES.md" CLAUDE.md` prints `1` or more.

## 6. Run the lite self-tests

```bash
cd ~/my-content
PYTHONDONTWRITEBYTECODE=1 python3 scripts/copy_check.py --self-test
PYTHONDONTWRITEBYTECODE=1 python3 .claude/skills/creator-profile/scripts/profile_check.py --selftest
```

**Check it:** the first ends `self-test: 60/60 cases pass`; the second ends `selftest: 16/16 cases pass`. Neither needs a network or a key.

## 7. The first sitting: the deep dive on you

Every level starts here, before any content is made. Open Claude Code in your project and say:

> Start my profile.

It runs `creator-profile`: a conversation, one question at a time, about who you are and how you want to come across, your business (what you sell, to whom, the price band, how a viewer becomes a customer, what one customer is worth), and your objectives (the next 12 months, and one number for the next 90 days). That is sitting 1, 25 to 35 minutes. Sitting 2 reads 3 to 10 of your own past pieces and plays back your style for you to confirm, then tears down 3 to 10 creators you love and 3 you dislike. Sitting 3 is your platforms and your hours, then a 1-page summary you confirm and a recommended level.

Stop whenever you like. Say **"pick up my profile"** next time and it starts where you stopped.

**Have ready for sitting 2:** links or files of 3 to 10 of your own pieces (2 you are proud of, 2 typical, 1 you dislike), and links to 3 to 10 creators or pieces you love and 3 you dislike. At lite, a video is read from its transcript: paste it, or add the one no-key extra (copy `~/content-studio/skills/watch` into `.claude/skills/` and `python3 -m pip install yt-dlp`, plus `ffmpeg`, which `watch.py` checks for before it runs: `brew install ffmpeg` on a Mac, `sudo apt install ffmpeg` on Linux), which reads public captions.

Before the money questions it asks whether prices and customer worth go in the profile or in `content/profile/private.md`, which it keeps out of git.

**Check it, after any sitting:**

```bash
python3 .claude/skills/creator-profile/scripts/profile_check.py content/profile
```

Sections you finished print `PASS` lines; sections not started yet print `OPEN`, which is fine. A `MISSING` line prints the exact sentence to say back **in the same conversation**. After sitting 3, `result: PASS` with no `OPEN` lines means the profile is done.

## 7b. Your taste files

`creator-profile` seeds your taste files where your answers bear on them. `taste-builder` grows them properly: open Claude Code in your project and paste prompt 2 in `INSTALL-PROMPT.md`. Give it 45 minutes on another evening. It reads your profile first and does not ask what it already answers.

This is the step everyone wants to skip and the one that decides whether your content sounds like you or like a competent stranger.

**Check it:** `ls content/taste/` shows `voice.md`, `hooks.md` and `packaging.md` with your words in them, not just the template headings. Open one and look.

**Short on time tonight instead? Your first taste file in 20 minutes.** Put 3 pieces by other people in front of you that actually stopped you mid scroll (1 is a preference, 2 is a coincidence, 3 is the smallest pile you can find a real rule in). Paste the prompt under "Tonight instead" in `INSTALL-PROMPT.md`. It runs round 2 of `taste-builder` (hooks) and nothing else, and writes your sentences into `content/taste/hooks.md` in quotation marks, exactly as you said them. Answer out loud and roughly. Then:

```bash
python3 scripts/first_taste_check.py content/taste/hooks.md
```

A finished sitting prints 4 `PASS` lines (exists, examples, your words, the rule). Any `MISSING` line prints the exact sentence to say back in the same conversation. **If you see a tidy summary of you instead of your own sentences,** say *"those are your words, not mine, go back and put my sentences in."*

## 7c. Posting by hand: the checklist (lite and standard)

At lite and standard you press post yourself. Run this list on every piece, every platform. Claude Code can walk it with you: say *"run the posting checklist on [the piece]"*.

1. **It is finished and checked.** At standard, `cut-review` ran on it. At lite, you watched or read it end to end yourself.
2. **The caption is yours and you have read all of it.** Drafted with `post-writer` if you like, then read in full. `python3 scripts/copy_check.py <the caption file>` passes.
3. **Every promise made on camera is a live link.** "Link below", "the free template": each one is in the description, opened, and loads (`content/taste/must-dos.md` row 19).
4. **Every frame is clear to post.** Checked at full resolution for faces of people who did not agree to appear, name labels, customer names and private screens (row 20).
5. **The title and the thumbnail are set before you press post.** On at least one feed a video's thumbnail cannot be changed once the post is live (`content/reference/lessons.md`, lesson 1).
6. **You press post.**
7. **Read it back.** Open the live post: the words, the link, the thumbnail, and that it is there once. If it took more than 1 attempt, count the copies before you call it done (lesson 2). A post is posted when you can see it on the platform, not when the composer goes quiet (lesson 7e).
8. **Write 1 line** in `content/work-record.md`: the date, the platform, the link, and `approved_by: <you>`.
9. **The day it goes live, tell every person the piece names, quotes or shows**, with the link, so they can share it (row 24).

At full, `skills/posting/` and `posting/README.md` take over the posting for platforms with an official posting route, and this list still applies to every platform that stays a hand card.

---

# Standard: steps 8 to 14

A sensible order: the system tools and packages (steps 8 and 9) on one evening, then transcription, fonts and the self-tests (10 to 13) on the evening you actually want to edit.

## 8. System tools, for the video half

**macOS** (needs Homebrew from brew.sh):

```bash
brew install ffmpeg-full node python yt-dlp
brew unlink ffmpeg 2>/dev/null
echo 'export PATH="$(brew --prefix ffmpeg-full)/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc
```

The plain `ffmpeg` formula has no libass and no freetype, so it can't burn captions or draw text. `ffmpeg-full` has both, and it installs out of the way of other tools (keg-only), which is why the PATH line is there.

**Linux** (Debian or Ubuntu):

```bash
sudo apt update
sudo apt install ffmpeg nodejs npm python3 python3-venv python3-pip
```

**Windows:** untested. The likely route is WSL with Ubuntu, then the Linux lines above inside it.

**Check it:**

```bash
ffmpeg -version | head -1
ffprobe -version | head -1
node -v
python3 --version
ffmpeg -filters | grep -wE "ass|subtitles|drawtext"
```

Each of the first 4 prints a version. Python must be 3.10 or newer. The last prints 3 lines, 1 each for `ass`, `subtitles` and `drawtext`: without them the caption gate, the karaoke burn and the workshop pipeline all stop. **If it prints fewer than 3,** your ffmpeg has no libass or freetype: on macOS run the 3 install lines above again and open a new terminal, then `which ffmpeg` should point inside `ffmpeg-full`. **If one prints `command not found`,** re-run the install line and read what it says about that tool.

## 9. Python packages, in a private box

A virtual environment keeps these packages away from the rest of your machine, and avoids the `externally-managed-environment` error.

```bash
python3 -m venv ~/.content-studio-venv
source ~/.content-studio-venv/bin/activate
python3 -m pip install --upgrade pip pillow numpy scipy requests yt-dlp
```

To activate it in every new terminal: `echo 'source ~/.content-studio-venv/bin/activate' >> ~/.zshrc` (or `~/.bashrc` on Linux).

**Check it:** `python3 -c "import PIL, numpy, scipy, requests, yt_dlp; print('python packages ok')"` prints `python packages ok`.

**Optional, for the page check and the example shorts pipeline:** Playwright drives a local Chrome or Chromium to read a rendered page, and OpenCV reads faces.

```bash
python3 -m pip install playwright opencv-python
python3 -m playwright install chromium
```

`design-dna`'s `page_check.py` uses Google Chrome at its macOS default path when it's there, or the path in `CHROME`, and Playwright's own Chromium otherwise. **Check it:** `python3 -c "import playwright, cv2; print('optional packages ok')"`.

## 10. Transcription keys

The editing pipeline needs word-level timings. 3 engines, in this order:

1. **ElevenLabs Scribe `scribe_v2`**, the default (`transcribe.py`). Best on names and word ends.
2. **Deepgram `nova-3`**, the declared fallback (`transcribe_deepgram.py`), for when Scribe is out of credits or down. It writes numbers as words, so captions need a number pass, and its speaker labels are not good enough to burn named captions.
3. **Local whisper**, last resort (`transcribe_local.py`), for no network and no key. It takes no key-terms list.

Put the keys you have in a `.env` file in your project root:

```bash
cd ~/my-content
cat >> .env <<'EOF'
ELEVENLABS_API_KEY=your_key_here
DEEPGRAM_API_KEY=your_key_here
EOF
```

Optional local fallback: `python3 -m pip install faster-whisper` (first run downloads about 1.5 GB). With no key at all, standard still works on local whisper.

**The rule that matters either way: names go into the transcriber, not into a find-and-replace afterwards.** Every recording with names on it gets a key-terms file passed with `--keyterms-file`. A find-and-replace cannot fix a name the transcriber never heard.

**Check it:**

```bash
grep -c "_API_KEY=" .env
grep -q "^\.env" .gitignore 2>/dev/null && echo "env is ignored" || echo ".env" >> .gitignore
```

The first prints how many keys you set. The second makes sure `.env` never reaches git.

## 11. Fonts, music and your brand

Open `.claude/skills/shorts-editor/assets/README.md`. It names the exact files the scripts look for. The short version: put a caption font at `.claude/skills/shorts-editor/assets/fonts/` (Montserrat from Google Fonts is the tested default: the variable file, and the static `Montserrat-Bold.ttf` from the zip's `static/` folder too if you'll use the example shorts pipeline), GSAP in `.claude/skills/shorts-editor/assets/vendor/` (the animated cards load it from their own folder, never from a CDN), and optionally a music bed you have a licence for at `.claude/skills/shorts-editor/assets/bg-music.m4a`. No fonts, music, logos or GSAP ship with this repo.

```bash
cd ~/my-content
mkdir -p .claude/skills/shorts-editor/assets/vendor
curl -L -o .claude/skills/shorts-editor/assets/vendor/gsap.min.js https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js
curl -L -o .claude/skills/shorts-editor/assets/vendor/MotionPathPlugin.min.js https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/MotionPathPlugin.min.js
```

Read GSAP's licence on its site before you ship anything commercially.

Then fill in `content/brand.md`: your accent colour, fonts, caption style and the folder of real photographs of you (`content/brand/people/`) that every image generation points at.

**Check it:**

```bash
python3 .claude/skills/shorts-editor/scripts/brand.py --self-test
ls .claude/skills/shorts-editor/assets/fonts/ .claude/skills/shorts-editor/assets/vendor/
```

The first ends `self-test: PASS`. The second lists your font and the 2 GSAP files.

## 12. Media generation, only if you want it

`media-gen` spends real money. It prints the cost of every call first and refuses anything over your ceiling.

```bash
cat >> .env <<'EOF'
MIXROUTE_API_KEY=your_key_here
MEDIA_GEN_MAX_CALL_USD=5.00
EOF
python3 .claude/skills/media-gen/scripts/media_gen.py doctor
```

**Check it:** `doctor` shows `OK  MIXROUTE_API_KEY` and your per-call cap.

Skip it if you like, but know this: packaging here means building thumbnail candidates and looking at them, never describing them in words. Without a key, build candidates in any design tool and bring the images back into the conversation. Write `skipped on purpose: media-gen` in `content/setup/preferences.md` so no session asks again.

## 13. Run the standard self-tests

From your project root, inside the virtual environment:

```bash
python3 scripts/copy_check.py --self-test
python3 scripts/serve_outputs.py --selftest
python3 .claude/skills/shorts-editor/scripts/brand.py --self-test
python3 .claude/skills/media-gen/scripts/media_gen.py selftest
python3 .claude/skills/design-dna/scripts/dna_check.py --selftest
python3 .claude/skills/watch/scripts/transcript.py --self-test
python3 .claude/skills/watch/scripts/watch.py --self-test
python3 .claude/skills/creator-profile/scripts/profile_check.py --selftest
python3 scripts/seo_updates.py --selftest
bash scripts/render_preflight.sh
```

**Check it:** each Python line ends in a pass line (`60/60 cases pass`, `all pass`, `PASS`, `selftest passed`, `11 cases pass`, `6 cases pass`, `16/16 cases pass`, `0 failed`). The preflight prints free disk and whether ffmpeg is found; `preflight: REFUSED` with under 25 GB free is the gate working, so clear space and run it again. None of them needs a network or a key.

If you installed Playwright in step 9, add the page check's own test. It renders 19 small pages in a headless browser and takes about 2 minutes:

```bash
python3 .claude/skills/design-dna/scripts/page_check.py --self-test
```

It ends `self-test: 19 of 19 fixtures behave as expected`.

**If one fails,** paste the whole output into Claude Code and ask it to read `TROUBLESHOOTING.md` first.

## 14. See a video page play

Review boards with videos on them play only when served, not opened as a file:

```bash
python3 scripts/serve_outputs.py --root outputs --port 4200
```

Then open `http://localhost:4200/` in your browser.

**Check it:** the folder listing loads. Stop it with Ctrl+C.

---

# Full: steps 13b, 15, 16 and 17

Do standard first. Full adds what runs without you in the room, so it comes last: learn first, automate after, hand off last (`content/PRINCIPLES.md`, section 2). If nothing has shipped through standard yet, consider shipping 1 piece first.

## 13b. The example shorts pipeline, only when you build podcast or tutorial shorts

`examples/podcast-shorts-pipeline/` is the reference builder behind the 10 rules in `shorts-editor`'s "Before you build a short". Copy it into the folder of the set of shorts you're building, so the code and its specs travel together:

```bash
cd ~/my-content
mkdir -p content/videos/<set>/pipeline
cp -R ~/content-studio/examples/podcast-shorts-pipeline/* content/videos/<set>/pipeline/
cd content/videos/<set>/pipeline
cp config.example.json config.json
python3 paths.py
```

Edit `config.json` first: your accent, your own brand and show names, your guests' companies. `python3 paths.py` prints every folder and value it resolved and where each came from. It needs the shorts-editor skill installed (step 4, standard), the fonts (step 11, plus `DMSerifDisplay-Regular.ttf`, `DMSerifDisplay-Italic.ttf`, `Inter[opsz,wght].ttf` and `LexendExa[wght].ttf`, all free from Google Fonts, in the same fonts folder), Playwright and OpenCV (step 9), and an `ffmpeg` built with libass (`ffmpeg -filters | grep -wE "ass|subtitles|drawtext"` prints 3 lines; if it doesn't, see step 8).

**On Linux, the monospace font.** The graphic pages load macOS's Menlo from `/System/Library/Fonts/Menlo.ttc`, and a page that can't load a face stops the build with the face's name, on purpose. Point it at a monospace font you have, without editing the page, with one line in `config.json`:

```json
"path_remap": [["/System/Library/Fonts/Menlo.ttc", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"]]
```

(`sudo apt install fonts-dejavu-core` gives you that file.) Or change the `@font-face` line for Menlo near the top of `looks.html`.

**Check it,** from that pipeline folder:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 pipeline.py --selftest
PYTHONDONTWRITEBYTECODE=1 python3 pipeline.py --status
PYTHONDONTWRITEBYTECODE=1 python3 anim_selftest.py
```

The first ends `selftest: PASS` (no footage, no network). The second lists the 2 invented example shorts under `TO GO`. The third ends `ALL PASS`. `--plan` and `--build` on the invented examples stop at the first missing track, because there's no footage behind them: that's the expected result until you write a spec for your own tapes. The example's `README.md` has the spec, the stages, the checks and the lessons.

The workshop pipeline in `examples/workshop-edit/` is copied the same way, into a video's own folder, when you edit a recorded workshop; its `README.md` walks it.

## 15. The morning routine

`routines/content-briefing.md` is a run that fires without you. Run it by hand once first, in a normal session, and fill every `[SQUARE BRACKET]` with your answer and a full path. Then ask Claude Code: *"Create a scheduled task named content-briefing that runs every weekday at 06:30 with the prompt between the lines in routines/content-briefing.md as its prompt. Show me when it next fires."* Pick a time when the machine is awake.

**Check it:** the morning after, a briefing file dated today is in the folder the routine names.

`routines/content-day.md` is an optional second weekday routine for when you have a pipeline running: specialist checkers read the recording plan, the cuts waiting on review, shorts and posting, open promises and podcast guests, and you get one list of what content needs from you today. It sends and posts nothing. Set it up the same way, after the morning briefing has run for a week.

`routines/posting-refresh.md` is the optional nightly refresh of a weekly posting plan. Set it up only once the posting module (step 16) holds a plan; its own file says what it needs first.

## 16. Posting by machine

The module and the skill are already copied (step 4). Open `posting/README.md` in your project and follow it from the top: it explains the plan (`content/posting/plan.jsonl`), the log (`content/posting/log.jsonl`) and the approval gate, then "Setup, per platform" connects each account through its official route, and "Going live: a dry week first" is the order to switch it on. The skill that drives it is `.claude/skills/posting/`: say *"build next week's posting plan"*. Run the schedule on one computer only: 2 computers running the same plan post twice (`posting/cron.example.txt`).

What holds whatever that file says:

- **Nothing posts without your approval recorded on the row** (`approved_by`). Dry-run is the default.
- **Every post is proven by reading the platform back**, never by the call returning quietly.
- **A platform with no official posting route for your account stays a hand card**: the file, the caption and the time, and you press post with the checklist in step 7c. Never a session cookie, never a website scrape, never a script driving the site.
- **Messages and connection requests to people are never automated**, on any platform.

**Check it,** from your project root (the commands are the ones the scripts' own headers name; `posting/README.md` is the authority if it says otherwise):

```bash
PYTHONDONTWRITEBYTECODE=1 python3 posting/scripts/plan.py --selftest
PYTHONDONTWRITEBYTECODE=1 python3 posting/scripts/runner.py --selftest
PYTHONDONTWRITEBYTECODE=1 python3 posting/scripts/watch.py --selftest
python3 posting/scripts/runner.py tick
```

The 3 self-tests pass offline. `runner.py tick` with no `--live` is the dry run: it says what it would post and posts nothing. A post you make by hand at full is recorded with `python3 posting/scripts/plan.py posted <leg> --url <the live link> --by "<you>"`, after you have opened the link.

## 17. Run the full self-tests

```bash
cd ~/my-content
PYTHONDONTWRITEBYTECODE=1 python3 scripts/verify_loop.py --selftest
```

Plus the 3 posting self-tests from step 16, and the example pipeline's from step 13b if you copied one.

**Check it:** the verify loop ends `all pass`.

---

# Changing level

**Up: "upgrade me to standard" or "upgrade me to full".** Claude Code reads `content/setup/preferences.md`, then runs only what the new level adds:

1. The new level's block in step 4 (standard, then full if going straight from lite to full). The lite block is not re-run, so nothing you have is touched.
2. That level's remaining steps: 8 to 14 for standard; 13b, 15, 16 and 17 for full.
3. Its self-tests.
4. Rewrites `level:` in `preferences.md` and adds a dated line to `upgrades:` (for example `upgrades: 2026-02-03 lite to standard`).

**Check it:** `ls .claude/skills | wc -l` prints 15 at standard and 16 at full, and `python3 .claude/skills/creator-profile/scripts/profile_check.py --preferences content/setup/preferences.md` passes.

**Down: "take me back to lite" or "back to standard".** Nothing is deleted.

1. At full, stop what runs on its own first: remove the scheduled tasks from step 15, and remove the posting schedule you installed from `posting/cron.example.txt` (the line in `crontab -e`) or `posting/launchd.example.plist`. With no schedule, nothing ticks and nothing posts.
2. Move the skills above the new level out of the folder Claude Code loads, by name, with literal paths. For example, from full to standard:

```bash
cd ~/my-content
mkdir -p .claude/skills-parked
mv .claude/skills/posting .claude/skills-parked/
```

From standard to lite, the same `mv` line for each of `watch`, `long-form-editor`, `shorts-editor`, `cut-review`, `search-visibility`, `media-gen`, `design-dna`, `on-camera-board` and `content-waterfall`.

3. Rewrite `level:` in `preferences.md` and add a dated line to `upgrades:` saying what went down.

**Check it:** start a new Claude Code session in your project and ask it to list its skills: the parked ones are gone from the list. Moving a folder back from `.claude/skills-parked/` to `.claude/skills/` undoes it.

**Change your answers without changing level:** say *"change my preferences"*, and it rewrites the lines you name, dated.

---

## Before your first render, 5 things that will bite (standard and full)

1. **Long renders run detached** with `scripts/render_detached.sh`, never as a background task in a conversation. When the conversation ends, so does a render owned by it.
2. **Any `-loop 1` image input carries an explicit `-t`.** Without it ffmpeg encodes until the disk is full.
3. **Check free disk first.** A full disk plus memory pressure is what takes a machine down overnight. `scripts/render_preflight.sh` checks it.
4. **Every frame pulled from a recording is checked at full resolution** for faces, name labels and private screen content. A screen share is somebody's whole screen: sample it at 1 frame per second, never 5.
5. **Green is not done.** A check passing means nothing mechanical broke. Watch it before anyone else does.

`content/reference/render-reliability.md` and `content/reference/lessons.md` have the rest.

## Updating later

```bash
cd ~/content-studio && git pull
```

Read `CHANGELOG.md` in the clone first: it says what changed since the last version. Then run step 4 again from your project, the blocks for your level only. The `-n` copies never touch your taste files, brand file, routines or constitution; skills, scripts and the edit lab book are replaced with the current versions. If you edited a skill, copy your version somewhere safe first. Your profile in `content/profile/` and your preferences are never copied over. A pipeline you copied out of `examples/` into a video's folder is yours and is never touched: compare it with the new example by hand if you want the changes.
