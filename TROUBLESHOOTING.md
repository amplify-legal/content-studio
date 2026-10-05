# Troubleshooting

The failures this repo actually produces, with the exact text where we know it, and the fix.

Find your error by the words in it. If yours is not here, the last section has a prompt that gets you useful help instead of a guess.

**One rule before anything else:** paste the whole error, not a description of it. "It didn't work" costs an hour. The exact text usually costs a minute.

---

## The first 20 minutes

The path at the top of `SETUP.md`. These are its failures, and most of them are fixed by saying 1 sentence back in the same conversation.

### `cp: ... No such file or directory` during the copy

The clone did not finish, or you are copying from the wrong place. Check `ls ~/content-studio` shows `skills`, `scripts`, `reference` and `templates`. If it does not, run the `git clone` line from `SETUP.md` step 1 again and read what it prints.

### `zsh: command not found: claude`

Claude Code is not installed, or not on this terminal's path. The 20 minute path needs it, because the whole middle step is a conversation. Install Claude Code first and come back; the 3 copy lines you already ran are still good.

### `python3: command not found` when you run the check

This Mac has never had developer tools on it. Nothing is wrong with the repo. Either:

```bash
xcode-select --install
```

wait for it to finish, and run the check again. Or skip the script tonight and check the file by eye, which is 4 things: 3 separate entries, your own words in quotation marks on each one, a rule at the bottom, and no `[SQUARE BRACKETS]` left in.

### The check says `MISSING  exists` and the file is not there

It interviewed you for 15 minutes and wrote nothing to disk. This is the one failure that feels worst and is easiest to fix, as long as you have not closed the conversation.

Go back to **that same conversation**, not a new one, and say:

```
write what I have told you so far into content/taste/hooks.md now, before anything else
```

Then run the check again. Everything you said is still in that conversation until you close it.

### The check says `MISSING  your words   0 quoted passages, 3 wanted`

It summarised you instead of quoting you. The file will read fine tonight and be worthless in a month, because a voice file written in somebody else's prose describes your voice rather than holding it.

In the same conversation:

```
go back through what I actually said and put my sentences in as quotes, one per example, not your summary
```

If it says it cannot recall your exact words, that is honest and the fix is to redo the 3 answers out loud. It is 5 minutes and it is the whole point of the evening.

### The check says `MISSING  examples   1 found, 3 wanted`

Your 3 pieces got merged into 1 block of prose. Say:

```
break that back out into one entry per piece, 3 of them, each with its own heading
```

### The check says `MISSING  the rule`

The examples went in and nothing was concluded from them. The 3 examples are the evidence and the rule is the point of having them. Say:

```
what do my 3 have in common, ask me until we have 1 rule I agree with, then write it into the file
```

Do not accept the first rule it offers if it does not sound like something you would say. Argue with it. The argument is where the rule comes from.

### `Warning: 3 unfilled placeholders left in, such as [link]`

It pasted the blank template instead of filling it in with your answers. Either answer them now, or:

```
delete the sections I have not answered, an empty file is honest and a half-filled one is not
```

### It started the full interview, or made 10 other files

It ran the whole `taste-builder` skill instead of round 2 only. Nothing is broken and nothing is lost, but the evening is now an hour, not 20 minutes. Say:

```
stop, tonight is round 2 only. Finish hooks.md with my 3 examples and the rule, and leave every other file alone.
```

The other files it created are empty headers and they do no harm sitting there.

### I only have 2 pieces that stopped me

Do the 2 and say so in the file. Say in the conversation: *"I have 2 tonight, write the pattern as UNTESTED until I bring a third."* 2 examples is a coincidence with a hypothesis attached, which is worth writing down as long as it is labelled. Add the third the next time something stops you, and rewrite the rule then.

### I do not recognise myself in the file, but the check passed

The check counts structure. It cannot tell whether the rule is a good one, and it never claims to.

This is the correction worth making tonight, because it gets harder every week: say which line is wrong and why, in the same conversation, and have it rewritten before you close it.

---

## Installing the skills

### The skills do not show up in Claude Code

Skills install into your project's own `.claude/skills/`, so they load only when Claude Code is opened in that project. Check you started `claude` from your project folder, then `ls .claude/skills` and expect 12 folders: `content`, `content-waterfall`, `cut-review`, `design-dna`, `long-form-editor`, `media-gen`, `on-camera-board`, `post-writer`, `script-writer`, `shorts-editor`, `taste-builder`, `watch`.

### `.claude/skills/` has loose files like `SKILL.md` in it

You copied the contents instead of the folders. Nothing is broken and you do not need to delete anything by hand. Run the copy again exactly as written in `SETUP.md` step 4, including the `/*`, then move the loose files out of the way when you are ready.

### A skill says it cannot find `content/PRINCIPLES.md` or a taste file

The skills are installed and the content folder is not. From your project root:

```bash
cp -n ~/content-studio/reference/PRINCIPLES.md content/PRINCIPLES.md
cp -Rn ~/content-studio/templates/taste/* content/taste/
ls content/PRINCIPLES.md content/taste/hooks.md
```

Every path a skill names is relative to your project root. A session opened in another folder cannot see them.

### I updated and my taste file was replaced

It should not be: every copy into `content/taste/`, `content/brand.md` and `content/PRINCIPLES.md` uses `cp -n`, which never overwrites. If a copy without `-n` ran, your previous version is in git if your project is a repository (`git log -- content/taste/`), or in your machine's backups. Add `-n` to that line so it cannot happen again.

## System tools

### `command not found: brew`

Homebrew is a program that installs other programs and it is not on a Mac by default. Install it from brew.sh first. It takes about 10 minutes, it asks for your Mac password, and on an Apple Silicon Mac it finishes by printing 2 or 3 extra commands it wants you to run. **Run those too.** Skipping them is the usual reason `brew` still says `command not found` after a successful install.

### `command not found: ffmpeg` after `brew install` said it worked

Almost always the same cause as above: Homebrew installed, but your terminal does not yet know where it put things. Close the terminal window, open a new one, and try again. If it still fails, run `brew install ffmpeg` on its own and read the last 5 lines it prints.

### `error: externally-managed-environment`

This is python refusing a plain `pip install`, and it is not a fault in the repo. It means packages have to go in a private box rather than into the system python. SETUP step 9 makes the box:

```bash
python3 -m venv ~/.content-studio-venv
source ~/.content-studio-venv/bin/activate
python3 -m pip install --upgrade pip pillow requests numpy
```

### `ModuleNotFoundError: No module named 'PIL'` (or `numpy`, or `requests`)

You are in a terminal window that is not inside the box. The box only applies to the window you activated it in.

```bash
source ~/.content-studio-venv/bin/activate
python3 -c "import PIL, requests, numpy; print('ok')"
```

If that fixes it, make it permanent so tomorrow's window is already inside:

```bash
echo 'source ~/.content-studio-venv/bin/activate' >> ~/.zshrc
```

### The caption check fails saying numpy is missing, but PIL works

Same cause, and worth its own line because the caption-size gate is the one place this repo treats numpy as mandatory. Run the `source` line, then `python3 -m pip install numpy`.

---

## Transcription

### `ELEVENLABS_API_KEY not found`

The script looks in your environment and in a `.env` file in the folder you run it from. Check:

```bash
grep -c "^ELEVENLABS_API_KEY=" .env
```

It should print `1`. If it prints `0`, add the line `ELEVENLABS_API_KEY=your_real_key` to `.env` in your project root and run the script from there. If you set it in your shell profile instead, open a brand new terminal window, because a profile only loads in windows opened after you edited it.

If Scribe is out of credits or down, the declared fallback is Deepgram (`transcribe_deepgram.py`, `DEEPGRAM_API_KEY`). Local whisper is the last resort.

### `DEEPGRAM_API_KEY not found`

The fallback transcriber has no key. Either add `DEEPGRAM_API_KEY=...` to `.env`, or go back to the default route, `transcribe.py` with Scribe, which is more accurate on word ends anyway.

### `Deepgram returned 200 but 0 words`

The request worked and the audio had nothing it could hear: a silent track, the wrong audio stream, or a video whose speech is on a second track. Check with `ffprobe -hide_banner <file>` which audio streams exist, and extract the right one before transcribing.

### Deepgram captions show "twenty five" instead of 25

Deepgram writes numbers as words; Scribe writes digits. Captions want digits, so a transcript from Deepgram needs a number pass before captions are built. The output file's header names which engine produced it, so check that first.

### `faster-whisper not installed`

Only the last-resort local route needs it: `python3 -m pip install faster-whisper` inside the virtual environment. Whisper takes no key-terms list, so expect names to come out wrong more often.

### The first local transcription sits there for a long time

It is downloading the model, about 1.5GB, once. It is cached afterwards. If it is genuinely stuck rather than slow, check you have several GB free: a download that fills the disk fails quietly and then fails again on every retry.

### A name came out wrong in the transcript

Do not fix it with a find and replace. **Names go into the transcriber, not into a find and replace afterwards.** Re-transcribe with a key-terms file carrying the names on the tape (`--keyterms-file`). A find and replace cannot fix a name the transcriber never heard, because it heard something else entirely.

One trap underneath that: `transcribe.py` caches on the filename. A re-run on the same file name serves the old transcript unless you pass `--force`. If the fix appears not to have worked, that is why.

## Rendering a short

### The captions stop and the message names a caption font

No font. `.claude/skills/shorts-editor/assets/` ships empty on purpose, because fonts are not ours to redistribute. Download Montserrat from Google Fonts, take the variable `.ttf` out of the zip, and put it at `.claude/skills/shorts-editor/assets/fonts/Montserrat-VariableFont_wght.ttf`. Or set `BRAND_CAPTION_FONT` (in `.env` or `content/brand.md`) to the full path of the font you want. `.claude/skills/shorts-editor/assets/README.md` lists every place the scripts look.

### A logo renders as an empty gap, or renders black on black

2 known causes, both in `.claude/skills/shorts-editor/assets/README.md`. A `viewBox` that does not match the path coordinates renders invisible. A logo drawn with `currentColor` loaded through an `<img>` tag renders black, which is black on a black band. Open every logo over a black background and look at it before you render.

### `npx hyperframes` takes ages the first time

It is downloading the renderer. Normal, and cached afterwards.

### The short has no music

Expected. No music ships with this repo, because music licensing does not travel. `compose.sh` detects that no track is present, says so, and renders with voice only. Point `MUSIC` at your own track when you want one, at 2%.

### The video will not open after export

It should already carry the fast-start flag. If you remuxed it by hand, add `-movflags +faststart` and remux again.

---

## Cutting a long recording

### The cut jumps around and feels jarring, and I cannot say why

Almost always 2 mechanical faults rather than a taste problem. On one audited cut, **12 of 33 cuts jumped between 17 and 330 seconds of the original with no bridge at all**, and of those same 33 cuts, 13 left mid-sentence, 12 landed mid-sentence and 8 fell inside a word. Ask for both counts before anything else:

> Count the cuts in this edit. For each one, how many seconds of the source it skips,
> and whether each side lands on a sentence boundary. Give me the 2 tables.

A jump over about 20 seconds needs a transition card. A cut that does not land on a sentence needs moving. `content/reference/long-form-lessons.md` has the full set.

### The captions look wrong and I cannot describe how

Check the highlight direction first. If the base colour is not pinned before the colour transitions, the renderer resolves the first transition's target for any time before it starts, which means **every word arrives already highlighted and the colour drains away as the words are spoken.** The highlight marks what has not been said yet. Proved on a bench render: 0.2 seconds into a 4 word line, all 4 words were highlighted. It is one token to fix and it is the first thing anybody's eye catches.

The second suspect is line breaking by word count. A hard 4 word cap put **524 of 705 lines at exactly 4 words** on one cut and read "So I was in / an instance where, a / firm was trying to". Break where the language breaks.

### Something private is on screen and I only noticed after publishing

There is no good recovery, which is why the privacy pass in the privacy step of `long-form-editor` runs before the first render. The 3 rules that would have caught it:

1. **A screen share is the presenter's whole screen.** Sample it at 1 frame per second at full resolution, not 2 frames of the tab strip. A share cleared that way still carried a private email subject in an address bar dropdown, account identifiers, notification badges and search history.
2. **Exposure checks sample at 1 second or finer.** A 1.8 second exposure of a private list survived a sweep at 5 seconds.
3. **Cropping is usually the whole fix.** Take the webcam column off, or take 110 pixels off the top for the menu bar, tab strip and address bar. Reach for a crop before you reach for a blur.

### The blur is covering things I want people to see

That is the other direction of the same fault, and it is just as real. On one cut **95% of the blurred runtime had no private thing on screen**, because the detector fired on any numbered list, smearing roughly 90 of 800 seconds of teaching content including 27 seconds of the closing answer.

Do not fix it by deleting windows by hand: somebody did that and dropped a window covering a genuinely open sidebar listing 15 private conversation titles. **Derive the windows** from what is actually legible, by reading the band at 2 frames per second across every kept second.

### The chapters or timestamps are all late

The cut renders sped up, usually 1.05x or 1.1x, so any timestamp taken off the 1.0x edit list is 5% or 10% late. On a 46 minute cut that is over 2 minutes of error by the end. It was caught once with 34 wrong chapter lines already drafted into 2 descriptions. **Every timestamp handed to a human comes off the delivered file.**

### A word is cut in half at a join

The boundary was snapped to the transcript's word span rather than to measured audio. Transcribers hang the pause **after** a word onto the word, so its reported end is later than when it was actually spoken. Snap to measured audio energy instead, and then read the rendered captions back across every join. A cut that sliced "opportunity" in half passed a green automatic pass, because nothing in it checks whether a word survived.

### A still or a photo shimmers

A slow push-in on a still resamples the frame by a fraction of a pixel every frame, and on flat ground, type and a face shimmer. It reads as a broken file. A still holds still. Measure it:

```bash
ffmpeg -v error -ss 120 -t 4 -i out/cut.mp4 -vf "crop=1920:900:0:0,tblend=all_mode=difference,signalstats,metadata=print:key=lavfi.signalstats.YMAX" -f null - 2>&1 | tail -20
```

A still section sits at 0 to 2. Anything higher is moving when it should not be.

### It re-rendered and nothing changed

Compare the file sizes. One version came back **byte for byte identical** to the previous one and only a size comparison caught it: the cause was 2 identical keys in the same dictionary, so the edit landed in the block the language throws away. "The render finished" is not "the change landed", and the check is one command:

```bash
ls -l out/*.mp4 && md5 out/cut-v4.mp4 out/cut-v5.mp4
```

### A segment render has been going for 20 minutes and there is no output

Check whether it is using any CPU before you call it slow. A render at 0% is a deadlock, not a slow job. The usual cause is an input window that runs out of audio exactly where a padding filter starts, so the graph never flushes: one 1.5 second segment hung for 13 minutes and rendered in 0.4 seconds with a second of slack on the window. Run every call with `-nostdin` and put a bounded wait on each segment, 60 seconds plus 3 times its duration, with one retry.

### A verification step produced nothing and did not error

Look for a colon inside a filter label. It silently fails the whole filter graph, so the step looks like it ran. Escape it (`00\:30`). This is worse than an error, because nothing tells you.

### A step exits 127 on a Mac

`timeout` does not exist on macOS. `perl -e "alarm N; exec @ARGV"` is the portable version.

### A check fails on a file I can see is fine

**The check is wrong.** Two real examples: a probe reading a title card's last frame as empty because it sampled 0.03 seconds into a segment instead of 0.20, and a 2 pixel probe that landed in a gap between layout regions. Fix the check, do not accept the finding, and do not loosen a threshold quietly.

---

## Long renders

### The render died when the conversation ended

That is the whole reason `render_detached.sh` exists. A 40 minute job that is a child of a chat dies when the chat does, and you find out in the morning with a partial file and no error. Run it detached:

```bash
scripts/render_detached.sh start myvideo --watch out -- "python3 build.py"
scripts/render_detached.sh status myvideo
```

### The disk filled up during a render

A still image fed into an encoder with a loop flag and no duration encodes duplicate frames forever. Every `-loop 1` input carries an explicit `-t`. There is no subtle version of this failure; it takes the machine down.

### Several overnight jobs all died

Do not start 3 encodes at once. The kernel kills the biggest process and that is always the encoder. Use `render_queue.sh`, which runs them one at a time through the same protections, and close what you can spare before you go to bed.

### The verify loop says a build file is missing

`scripts/verify_loop.py` drives a piece folder that holds 4 files: `build/build_cut.py`, `build/finalize.py`, `build/verify.py` and `build/autofix.py`. It prints which one is missing and stops. Write stubs with:

```bash
python3 scripts/verify_loop.py content/videos/<slug> --scaffold
```

then fill them in for your piece. `content/reference/verify-loop.md` is the contract. Repairs go in `build/overrides.json` as data, never as edits to code.

### The verify loop came back green and the cut is still wrong

Green is not done. Green means nothing in the check battery fired, which makes the file worth a person's watch. Watch it. When you find something the battery missed, add a check for it to `build/verify.py` in the same session, so the next loop catches it.

### The loop stopped with a finding it did not fix

That is the design. A finding the repair table cannot fix safely stops at the `model` tier, with a short verdict file a session reads cheaply. A taste call stops at the `human` tier. The loop never promotes a finding to a tier it can fix, so it never "fixes" taste.

## Watching review pages

### The videos on a review page do not play

The page was opened as a file. Browsers and embedded browser panes often refuse to play a page's relative `<video>` files off disk, and some need HTTP Range requests to start or seek an mp4. Serve the folder instead:

```bash
python3 scripts/serve_outputs.py --root outputs --port 4200
```

then open `http://localhost:4200/<path under outputs>`. The server answers Range requests with 206, which is what the player needs.

### `Address already in use` when starting the server

Something is already on port 4200, often an earlier copy of the same server. Use another port (`--port 4201`) or stop the old one.

---

## Publishing by hand

### A platform says the upload failed with a generic message

Do not guess at the cause. Post the smallest honest version of the same thing first: a 30 to 60 second clip of the same encode. If that goes up, the account, the session and the text are fine, and only the variables that differ remain. Add them back one at a time. `content/reference/lessons.md` has the measured cases.

### A LinkedIn native video sits at 0% or fails when it has a custom thumbnail

Add the video first and wait until its upload bar reaches 100%, then add the thumbnail. The thumbnail must match the video's own pixel dimensions (a 1920x1080 video needs a 1920x1080 thumbnail, not 1280x720). A LinkedIn video thumbnail cannot be changed once the post is live, so never post first and plan to add it later. If every custom thumbnail stalls, render the thumbnail as the video's first second instead.

### The platform said it failed, and now the post is up 3 times

A generic refusal can be untrue about the outcome: retries may each have landed. After any publish that took more than 1 attempt, open the profile and count what is actually there. Deleting duplicates is yours to do by hand.

---

## Media generation

### `MIXROUTE_API_KEY is not set`

Same shape as the transcription key. Open a new terminal window first, because a shell profile only loads in windows opened after you edited it. Then:

```bash
echo 'export MIXROUTE_API_KEY=your_real_key' >> ~/.zshrc
source ~/.zshrc
python3 ./.claude/skills/media-gen/scripts/media_gen.py doctor
```

`doctor` is the right first command every single time this skill behaves oddly. It prints what is set, what is missing and what a call would cost.

### `MixRoute rejected the key`

The key is set but wrong, or it belongs to an account with no balance. Run `doctor`, then check the key on mixroute.ai. A key pasted with a trailing space is the common one.

### It refused a call saying it is over the cap

**That is the script working, not failing.** Either make the call smaller (lower resolution, fewer variations, shorter video) or raise the ceiling deliberately:

```bash
echo 'export MEDIA_GEN_MAX_CALL_USD=10.00' >> ~/.zshrc
```

Never work around it by splitting one job into pieces that each slip under the ceiling. That is how a bill surprises you.

### I have no key and it wants to describe thumbnails to me in words

Stop it. Packaging in this repo means looking at candidates, never reading about them. Build the candidates in whatever design tool you already use, bring the images back into the conversation, and run the 4 packaging questions on what you brought.

---

## The check script

### `python3: can't open file 'scripts/copy_check.py': No such file or directory`

The path is relative to your project root. `cd` into your project first. If `ls scripts/copy_check.py` also says no such file, redo the copy in `SETUP.md` step 4.

### The checker flags my own rules document

Correct and expected. A rules file quotes the banned phrases in order to ban them. **Run the checker on the copy that ships, never on the documents that describe the copy, and never rewrite a rule to make the report go green.**

### The design battery fails on a page I know is right

Also expected, and it is the whole method. A test that fails on the original is a broken test, not a broken page. Edit the number in `dna.json`. Never edit the page to satisfy the battery.

---

## The morning routine

### There is no briefing file with today's date

Look in `content/briefings/` in your project, or the folder you named in the prompt.

It did not run, or it ran and stopped early. 3 usual causes, in the order worth checking:

1. **The machine was asleep at the fire time.** A closed laptop misses its slot. Pick a time the machine is awake, or leave it awake.
2. **A `[SQUARE BRACKET]` it could not resolve.** The run has no conversation history and cannot ask you anything, so an unfilled placeholder stops it. Ask Claude Code: *"show me the recent runs of content-briefing and what each one did"*, then fix the bracket it named in `routines/content-briefing.md`.
3. **The task is switched off.** A task can exist, look perfect and be disabled. Ask: *"list my scheduled tasks and tell me whether each one is enabled"*.

### The briefing arrived in the middle of the afternoon

An overdue slot replays whenever the app next opens. A late run still builds the whole briefing, and owes you one line at the top of the file: the time it fired, how late that is, and anything still landing. If it arrived late without that line, step 2 is missing from your filled-in copy. Put it back, and move the schedule to a time the machine is awake.

### Several briefings appeared for the same day, and they disagree

Every open copy of the app runs the scheduler, so the number of runs equals the number of open windows. The prompt's step 0 takes a lock file named for today's date and stops if the lock is held. If you removed that step, put it back. The symptom is usually a document that looks strange in a way you cannot describe, so check for duplicate output files with the same date before debugging anything else.

### It tells me work has not been done instead of doing it

That is step 4 of the prompt and it is worth quoting at the session. If the only thing between you and the thing existing is effort, the run spends the effort. If it needs your judgment, it stays a question. A run that reports missing research instead of doing the research has the rule and is not following it: say so in the same session and make the correction land in the routine file, not just in the chat.

---

## The system itself

### The taste folder is still empty after an hour of interview

The skill is supposed to write as it goes, precisely so an interrupted hour is not a lost hour. Say it plainly in the same session: *"write what I have told you so far into the files now, before the next question."* Then check with `ls content/taste/`.

### It generates at me instead of asking me questions

That is the failure this whole system is shaped against, and it usually means the constitution is not loading. From the folder you open Claude Code in, check `test -f content/PRINCIPLES.md && echo ok` and `grep -c PRINCIPLES CLAUDE.md`. If both are fine, say it directly: *"stop. Ask me one question and wait."* Then make the correction land in the skill file, because a correction that lives only in the chat gets re-broken tomorrow.

### I fixed the same thing twice and it came back a third time

The correction landed in today's piece instead of in the file the next session reads. That is the single most expensive failure in here: a caption rule fixed inside one episode's build script shipped broken again on 12 of 15 renders 3 days later. Add this to every correction from now on:

> and put that rule where the next session will see it, then tell me which file you put it in and write the row in my work record.

---

## When it is not on this page

Paste this into the thread where it broke, with the error included:

> Something in Content Studio is not working and it is not in `TROUBLESHOOTING.md`.
>
> Here is exactly what I ran and exactly what came back:
>
> ```
> [paste the command and the FULL error, every line of it]
> ```
>
> Before you suggest anything, tell me these 4 things:
> 1. Which step of `SETUP.md` this belongs to, and whether that step's check passes right
>    now. Run the check and show me the output.
> 2. Whether this is the repo, my machine, or a key. Say which, and say how you know.
> 3. The smallest command that would prove your diagnosis, and run it.
> 4. What you do NOT know. Do not guess and do not try 3 fixes in a row hoping one lands.
>
> Then give me one fix at a time, with the check I run after each one.
>
> If the fix is a change to one of the repo's own files, make the change in the installed
> copy and tell me which file you changed, so it survives the next session.
