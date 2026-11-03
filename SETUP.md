# Setup

**Tonight: 20 minutes, and you finish holding a file that is yours. Everything else: about 2 hours of attention over a few evenings, plus downloads you do not have to watch.**

Every step ends with a command you can run and a line saying what you should see. If the check does not say that, the fix is written under it. If something breaks and the fix does not cover it, `TROUBLESHOOTING.md` has the errors these scripts actually produce.

**The easiest route:** open Claude Code in your project folder and paste prompt 1 from `INSTALL-PROMPT.md`. It does the copying and runs the checks with you. This file is what it follows.

### The names used below

- **The clone**: where you cloned this repo. The examples use `~/content-studio`.
- **Your project**: the folder you do content work in, and the folder you open Claude Code in for content. The examples use `~/my-content`. Use your own path everywhere you see it.

Everything gets copied into your project like this:

| From the clone | Into your project |
|---|---|
| `skills/*` | `.claude/skills/` |
| `scripts/*` | `scripts/` |
| `reference/*.md` | `content/reference/` |
| `reference/edit-lab/` | `content/reference/edit-lab/` |
| `reference/PRINCIPLES.md` | `content/PRINCIPLES.md` |
| `reference/frameworks/*` | `content/frameworks/` |
| `templates/taste/*` (the `kinds/` folder included) | `content/taste/` (never over your own files) |
| `templates/brand.md` | `content/brand.md` (never over your own file) |
| `routines/*.md` | `routines/` (never over your own filled-in copies) |
| `examples/podcast-shorts-pipeline/` | `content/videos/<set>/pipeline/`, only when you build podcast or tutorial shorts (step 13b) |

Skills live in the project's own `.claude/skills/`, so they load only when you work in that project.

---

# Start here: 20 minutes, tonight

**What you get:** 1 file, `content/taste/hooks.md`. In it: 3 pieces by other people that made you stop scrolling, your own sentences on why each one worked on you, and the rule the 3 point at.

**What you do not get:** no video, nothing rendered, nothing published, no `ffmpeg`, no keys.

**Why it is worth it even if you stop here.** Every skill in this repo opens `hooks.md` by name. And set the repo aside entirely, the file still earns its 20 minutes: next time you write an opening you reach for a rule instead of a feeling.

## Before the clock starts

Put 3 pieces in front of you. Posts, videos, emails, ads. Not ones you admired. Ones that actually stopped you mid scroll. 1 is a preference, 2 is a coincidence, 3 is the smallest pile you can find a real rule in.

## 1. Clone and copy. 2 minutes.

```bash
git clone https://github.com/amplify-legal/content-studio.git ~/content-studio
mkdir -p ~/my-content/.claude/skills ~/my-content/scripts ~/my-content/content/taste
cd ~/my-content
cp -R ~/content-studio/skills/taste-builder .claude/skills/
cp ~/content-studio/reference/PRINCIPLES.md content/PRINCIPLES.md
cp ~/content-studio/scripts/first_taste_check.py scripts/
cp -n ~/content-studio/templates/taste/hooks.md content/taste/hooks.md
```

**Check it:**

```bash
ls .claude/skills/taste-builder/SKILL.md content/PRINCIPLES.md scripts/first_taste_check.py content/taste/hooks.md
```

It prints those 4 paths back and nothing else.

**If `git` is not found:** on a Mac run `xcode-select --install` and wait; on Linux `sudo apt install git`. **If a `cp` line says `No such file or directory`,** the clone did not finish. Run the `git clone` line again and read what it says.

## 2. The interview. 15 minutes.

```bash
cd ~/my-content
claude
```

Paste the prompt under "Tonight instead" in `INSTALL-PROMPT.md`. It runs round 2 of `taste-builder` (hooks) and nothing else, one question at a time, and writes your sentences into `content/taste/hooks.md` in quotation marks, exactly as you said them.

**Answer out loud and roughly.** The half-finished sentence you would actually say is worth more than the tidy one.

**Check it, while still in the conversation:** say `show me hooks.md as it stands right now`. You should see your own sentences in quotes. **If you see a tidy summary of you instead,** say *"those are your words, not mine, go back and put my sentences in."*

## 3. The check, then read it. 3 minutes.

```bash
python3 scripts/first_taste_check.py content/taste/hooks.md
```

A finished sitting prints 4 `PASS` lines (exists, examples, your words, the rule). Any `MISSING` line prints the exact sentence to say back **in the same conversation**, where your answers still are.

Then open the file and read the rule at the bottom. Agreeing or disagreeing with it is the real point of the evening.

**If `python3` is not found:** on a Mac run `xcode-select --install`; on Linux `sudo apt install python3`.

---

# The rest, over the next few evenings

A sensible order: the constitution and the full copy (steps 4 to 6), your taste files (step 7), then the video tools (steps 8 to 12) on the evening you actually want to edit.

## 4. Copy everything else

From your project folder:

```bash
cd ~/my-content
mkdir -p .claude/skills scripts routines content/reference content/frameworks content/taste content/videos outputs
cp -R ~/content-studio/skills/* .claude/skills/
cp -R ~/content-studio/scripts/* scripts/
cp ~/content-studio/reference/*.md content/reference/
cp -R ~/content-studio/reference/edit-lab content/reference/
cp -n ~/content-studio/reference/PRINCIPLES.md content/PRINCIPLES.md
cp ~/content-studio/reference/frameworks/*.md content/frameworks/
cp -Rn ~/content-studio/templates/taste/* content/taste/
cp -n ~/content-studio/templates/brand.md content/brand.md
cp -n ~/content-studio/routines/*.md routines/
chmod +x scripts/*.sh .claude/skills/*/scripts/*.sh 2>/dev/null
```

`-n` means never overwrite. Your taste files, your brand file, your filled-in routines and your edited constitution are never replaced when you run this again to update. A taste template that is new in the clone (a new kind sheet, say) is still added, because `-n` only skips files you already have.

**Check it:**

```bash
ls .claude/skills
ls content/taste | head -40
ls content/taste/kinds content/reference/edit-lab
ls routines
```

The first prints 14 folders: `content`, `content-waterfall`, `cut-review`, `design-dna`, `director`, `long-form-editor`, `media-gen`, `on-camera-board`, `post-writer`, `script-writer`, `search-visibility`, `shorts-editor`, `taste-builder`, `watch`. The second prints the taste templates. The third prints 6 kind files (`README.md`, `live.md`, `masterclass.md`, `podcast.md`, `short.md`, `tutorial.md`) and the 6 edit lab files (`README.md`, `captions.md`, `motion.md`, `picture.md`, `privacy-and-pipeline.md`, `sound.md`). The fourth prints `content-briefing.md` and `posting-refresh.md`.

**If you see loose files like `SKILL.md` directly in `.claude/skills/`,** you copied the contents instead of the folders. Run the `cp -R ~/content-studio/skills/*` line again exactly as written.

## 5. Tell your sessions the 2 rules that matter most

Claude Code reads `CLAUDE.md` in the folder you open it in at the start of every session. Put these lines in your project's `CLAUDE.md`, not in `~/.claude/CLAUDE.md`, which loads in every project you own:

```bash
cd ~/my-content
cat >> CLAUDE.md <<'EOF'

Content work here follows content/PRINCIPLES.md, which wins over any process step. Taste lives in content/taste/ in my words; skills read it and never restate it.
When I correct something, put the correction in the file the next session reads, in the same session: the skill, the taste file or the check script, never only in today's piece. Tell me which file.
Nothing publishes. Long renders run through scripts/render_detached.sh. cut-review runs before any cut reaches me.
EOF
```

**Check it:** `grep -c "content/PRINCIPLES.md" CLAUDE.md` prints `1` or more.

## 6. Read the constitution and argue with it

Open `content/PRINCIPLES.md`. 10 minutes. If you disagree with a principle, edit it now, before anything is built on it.

**Check it:** you changed or deleted at least one line, or you decided out loud that you agree with all of it.

## 7. Build your taste files

Open Claude Code in your project and run `taste-builder` (prompt 2 in `INSTALL-PROMPT.md`). Give it 45 minutes. If you did tonight's sitting, say *"I already have hooks.md. Read it, do not redo it, start at round 1."*

This is the step everyone wants to skip and the one that decides whether your content sounds like you or like a competent stranger.

**Check it:** `ls content/taste/` shows `voice.md`, `hooks.md` and `packaging.md` with your words in them, not just the template headings. Open one and look.

---

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

Optional local fallback: `python3 -m pip install faster-whisper` (first run downloads about 1.5 GB).

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

Skip it if you like, but know this: packaging here means building thumbnail candidates and looking at them, never describing them in words. Without a key, build candidates in any design tool and bring the images back into the conversation.

## 13. Run every self-test

From your project root, inside the virtual environment:

```bash
python3 scripts/copy_check.py --self-test
python3 scripts/verify_loop.py --selftest
python3 scripts/serve_outputs.py --selftest
python3 .claude/skills/shorts-editor/scripts/brand.py --self-test
python3 .claude/skills/media-gen/scripts/media_gen.py selftest
python3 .claude/skills/design-dna/scripts/dna_check.py --selftest
python3 .claude/skills/watch/scripts/transcript.py --self-test
python3 .claude/skills/watch/scripts/watch.py --self-test
bash scripts/render_preflight.sh
```

**Check it:** each Python line ends in a pass line (`60/60 cases pass`, `all pass`, `PASS`, `selftest passed`, `11 cases pass`, `6 cases pass`). The preflight prints free disk and whether ffmpeg is found. None of them needs a network or a key.

If you installed Playwright in step 9, add the page check's own test. It renders 19 small pages in a headless browser and takes about 2 minutes:

```bash
python3 .claude/skills/design-dna/scripts/page_check.py --self-test
```

It ends `self-test: 19 of 19 fixtures behave as expected`.

**If one fails,** paste the whole output into Claude Code and ask it to read `TROUBLESHOOTING.md` first.

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

Edit `config.json` first: your accent, your own brand and show names, your guests' firms. `python3 paths.py` prints every folder and value it resolved and where each came from. It needs the shorts-editor skill installed (step 4), the fonts (step 11, plus `DMSerifDisplay-Regular.ttf`, `DMSerifDisplay-Italic.ttf`, `Inter[opsz,wght].ttf` and `LexendExa[wght].ttf`, all free from Google Fonts, in the same fonts folder), Playwright and OpenCV (step 9), and an `ffmpeg` built with libass (`ffmpeg -filters | grep -wE "ass|subtitles|drawtext"` prints 3 lines; if it doesn't, see step 8).

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

## 14. See a video page play

Review boards with videos on them play only when served, not opened as a file:

```bash
python3 scripts/serve_outputs.py --root outputs --port 4200
```

Then open `http://localhost:4200/` in your browser.

**Check it:** the folder listing loads. Stop it with Ctrl+C.

## 15. The morning routine, optional

`routines/content-briefing.md` is the one thing that fires without you. Run it by hand once first, in a normal session, and fill every `[SQUARE BRACKET]` with your answer and a full path. Then ask Claude Code: *"Create a scheduled task named content-briefing that runs every weekday at 06:30 with the prompt between the lines in routines/content-briefing.md as its prompt. Show me when it next fires."* Pick a time when the machine is awake.

**Check it:** the morning after, a briefing file dated today is in the folder the routine names.

---

## Before your first render, 5 things that will bite

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

Read `CHANGELOG.md` in the clone first: it says what changed since the last version. Then run step 4 again from your project. The `-n` copies never touch your taste files, brand file or constitution; skills, scripts and the edit lab book are replaced with the current versions. If you edited a skill, copy your version somewhere safe first. A pipeline you copied out of `examples/` into a video's folder is yours and is never touched: compare it with the new example by hand if you want the changes.
