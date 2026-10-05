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
| `reference/PRINCIPLES.md` | `content/PRINCIPLES.md` |
| `reference/frameworks/*` | `content/frameworks/` |
| `templates/taste/*` | `content/taste/` (never over your own files) |
| `templates/brand.md` | `content/brand.md` (never over your own file) |

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
mkdir -p .claude/skills scripts content/reference content/frameworks content/taste content/videos outputs
cp -R ~/content-studio/skills/* .claude/skills/
cp -R ~/content-studio/scripts/* scripts/
cp ~/content-studio/reference/*.md content/reference/
cp -n ~/content-studio/reference/PRINCIPLES.md content/PRINCIPLES.md
cp ~/content-studio/reference/frameworks/*.md content/frameworks/
cp -Rn ~/content-studio/templates/taste/* content/taste/
cp -n ~/content-studio/templates/brand.md content/brand.md
chmod +x scripts/*.sh .claude/skills/*/scripts/*.sh 2>/dev/null
```

`-n` means never overwrite. Your taste files, your brand file and your edited constitution are never replaced when you run this again to update.

**Check it:**

```bash
ls .claude/skills
ls content/taste | head -30
```

The first prints 12 folders: `content`, `content-waterfall`, `cut-review`, `design-dna`, `long-form-editor`, `media-gen`, `on-camera-board`, `post-writer`, `script-writer`, `shorts-editor`, `taste-builder`, `watch`. The second prints the taste templates.

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
brew install ffmpeg node python yt-dlp
```

**Linux** (Debian or Ubuntu):

```bash
sudo apt update
sudo apt install ffmpeg nodejs npm python3 python3-venv python3-pip
python3 -m pip install --user yt-dlp
```

**Check it:**

```bash
ffmpeg -version | head -1
ffprobe -version | head -1
node -v
python3 --version
```

Each prints a version. Python must be 3.10 or newer. **If one prints `command not found`,** re-run the install line and read what it says about that tool.

## 9. Python packages, in a private box

A virtual environment keeps these packages away from the rest of your machine, and avoids the `externally-managed-environment` error.

```bash
python3 -m venv ~/.content-studio-venv
source ~/.content-studio-venv/bin/activate
python3 -m pip install --upgrade pip pillow numpy requests
```

To activate it in every new terminal: `echo 'source ~/.content-studio-venv/bin/activate' >> ~/.zshrc` (or `~/.bashrc` on Linux).

**Check it:** `python3 -c "import PIL, numpy, requests; print('python packages ok')"` prints `python packages ok`.

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

Open `.claude/skills/shorts-editor/assets/README.md`. It names the exact files the scripts look for. The short version: put a caption font at `.claude/skills/shorts-editor/assets/fonts/` (Montserrat from Google Fonts is the tested default), and optionally a music bed you have a licence for at `.claude/skills/shorts-editor/assets/bg-music.m4a`. No fonts, music or logos ship with this repo.

Then fill in `content/brand.md`: your accent colour, fonts, caption style and the folder of real photographs of you (`content/brand/people/`) that every image generation points at.

**Check it:**

```bash
python3 .claude/skills/shorts-editor/scripts/brand.py --self-test
ls .claude/skills/shorts-editor/assets/fonts/
```

The first ends `self-test: PASS`. The second lists your font.

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
bash scripts/render_preflight.sh
```

**Check it:** each Python line ends in a pass line (`53/53 cases pass`, `all pass`, `PASS`, `selftest passed`). The preflight prints free disk and whether ffmpeg is found. None of them needs a network or a key.

**If one fails,** paste the whole output into Claude Code and ask it to read `TROUBLESHOOTING.md` first.

## 14. See a video page play

Review boards with videos on them play only when served, not opened as a file:

```bash
python3 scripts/serve_outputs.py --root outputs --port 4200
```

Then open `http://localhost:4200/` in your browser.

**Check it:** the folder listing loads. Stop it with Ctrl+C.

## 15. The morning routine, optional

`routines/content-briefing.md` is the one thing that fires without you. Run it by hand once first, in a normal session, and fill every `[SQUARE BRACKET]` with your answer and a full path. Then ask Claude Code: *"Create a scheduled task named content-briefing that runs every weekday at 06:30 with the contents of routines/content-briefing.md as its prompt. Show me when it next fires."* Pick a time when the machine is awake.

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

Then run step 4 again from your project. The `-n` copies never touch your taste files, brand file or constitution; skills and scripts are replaced with the current versions. If you edited a skill, copy your version somewhere safe first.
