# Prompts to paste into Claude Code

Ready-made prompts for every stage, in the order you will hit them. Edit the bracketed parts before you paste.

**Start with prompt 1.** It is the only one you need to install. It asks you 5 quick questions, picks a level (`lite`, `standard` or `full`), installs only that level, runs the checks, and then starts the deep dive on you. Every other prompt here is for later.

**Which level each prompt needs.** Prompts 1 to 3, 5b and 12 to 14 work at every level. Prompts 4, 5, 6 to 9 and 11 use skills from `standard` (prompt 4 builds thumbnails with `media-gen` only if you added its key). Prompt 10 uses the verify loop from `full`. At a lower level, Claude says which skill is missing and offers the upgrade; it never pretends.

---

## 1. The install, the one paste

Open Claude Code in the folder you do content work in (your project), and paste:

> Install Content Studio into this project with me, one step at a time.
>
> 1. Clone `https://github.com/amplify-legal/content-studio.git` to `~/content-studio` (or `git pull` there if it already exists). Read its `START-HERE.md`, `SETUP.md` and `skills/creator-profile/reference/levels.md` before doing anything else. Do not summarise the repo back to me.
> 2. Ask me the 5 preference questions from `SETUP.md` section 0, one at a time, and stop talking after each one: how much time I have today, who edits my videos, whether I want posting done by machine, which platforms I use and want, and which computer I am on. Then tell me in 2 lines which level you recommend and why, following "The pick, in order" in `levels.md`, and let me choose.
> 3. Write my answers to `content/setup/preferences.md` in the shape at the bottom of `levels.md`, in my words, with today's date, and run the preferences check from `SETUP.md` step 2.
> 4. Before you copy anything, check what I already have and show me: an existing `.claude/skills/`, `CLAUDE.md`, `content/taste/`, `content/profile/`. For `standard` or `full`, also check ffmpeg (with libass: the `ffmpeg -filters` line in step 8), ffprobe, node, python3 (3.10 or newer), yt-dlp, Playwright with a Chrome or Chromium (optional), and which of these keys are set in `.env` or my environment: ELEVENLABS_API_KEY, DEEPGRAM_API_KEY, MIXROUTE_API_KEY. Never print a key's value. For `lite`, check only python3.
> 5. Copy with the blocks in `SETUP.md` step 4 for my level only: the lite block, then the standard block for `standard` or `full`, then the full block for `full`. Use `cp -n` exactly where the blocks do, so nothing of mine under `content/taste/`, `routines/`, `content/brand.md` or `content/PRINCIPLES.md` is ever overwritten. If a skill folder of the same name already exists and differs, show me the difference and ask before replacing it.
> 6. Add the lines from `SETUP.md` step 5 to this project's `CLAUDE.md`, never to `~/.claude/CLAUDE.md`. Make sure `.env` is in this project's `.gitignore`.
> 7. Run the self-tests for my level and show me the output: step 6 for `lite`, step 13 for `standard`, steps 13 and 17 for `full`. Use `PYTHONDONTWRITEBYTECODE=1`. Say plainly which tests you skipped and why.
> 8. For `standard` or `full`, walk the rest of that level's steps with me, one at a time, running each step's check before the next. For `full`, step 16 follows `posting/README.md` from the top, and nothing posts: dry-run until I approve a row.
> 9. Then start the first sitting of `creator-profile` (`SETUP.md` step 7). If I have to stop, save where we are in `content/profile/progress.md` and tell me how to resume.
>
> Ask before installing any system package. Never delete anything: if something is in the way, tell me. Never ask me to paste a key into the chat: tell me the file (`.env` in this project) and the variable name.

If you already know your level, add one line at the end: *"My level is **[lite / standard / full]**, skip the recommendation."* The questions are still asked, because the deep dive reads your answers.

---

## 1b. The deep dive, any time after

> Start my profile.

> Pick up my profile.

> My business changed: **[what changed]**. Update my profile.

It asks one question at a time, writes your words into `content/profile/` as you go, and ends with a 1-page summary you confirm and a recommended level. For sitting 2, have 3 to 10 of your own pieces ready (2 you are proud of, 2 typical, 1 you dislike), and 3 to 10 creators or pieces you love plus 3 you dislike.

---

## 1c. Changing level

> Upgrade me to **[standard / full]**. Read `content/setup/preferences.md` and `SETUP.md` "Changing level", run only what the new level adds, run its self-tests, and update my preferences file.

> Take me back to **[lite / standard]**. Follow "Changing level" in `SETUP.md`: stop anything that runs on its own first, move the skills above that level to `.claude/skills-parked/`, delete nothing, and update my preferences file.

---

## Tonight instead: your first taste file, 20 minutes

Have 3 pieces by other people in front of you that made you stop scrolling. It needs the lite copy in place (prompt 1 at `lite`, or `SETUP.md` steps 1 and 4 by hand, about 3 minutes). Then open Claude Code in your project and paste:

> I am setting up Content Studio and tonight I am doing only the first 20 minutes.
>
> Read `content/PRINCIPLES.md` and `.claude/skills/taste-builder/SKILL.md` first. Then run round 2 of that skill, hooks, and nothing else. Do not create my other taste files, do not run the other rounds, do not write any content, and do not summarise anything back to me.
>
> I have 3 pieces by other people that made me stop scrolling. Interview me about them one at a time. One question at a time, and stop talking after each question.
>
> After each piece, before you ask me anything else, write what I said into `content/taste/hooks.md`. Put my sentences in quotation marks exactly as I said them, filler included. Do not tidy them. If I answer "I just know it when I see it", do not accept it: ask me what exactly I saw the last time.
>
> When all 3 are in the file, tell me in 1 sentence the rule you think they point at. I will correct it. Write my corrected version, in my words, under a heading called "The rule my 3 point at".
>
> Stop at 15 minutes even if we are mid answer, and tell me what is in the file and what is still thin.

Then in a terminal: `python3 scripts/first_taste_check.py content/taste/hooks.md`. 4 `PASS` lines and you are done for the night.

---

## 2. Taste, the important one

If you did the 20 minute sitting, start with: *"I already have hooks.md. Read it, do not redo it, and start at round 1."* If your profile is done, add: *"Read content/profile/ first and do not ask what it already answers."* Then:

> Run `taste-builder`. Give this a proper 45 minutes and interview me hard. When I say "I just know it when I see it", ask me for 3 examples and work out the rule from what they have in common. Write into `content/taste/` as you go, not at the end. Then walk me through the "starting defaults" sections in the templates and ask which I keep, change or strike.

---

## 3. Using the door

Everything goes through `content`, including the half-thoughts:

> **[paste a link]** this is great, I want to do something like it

> what should I record this week

> I have a half idea: **[say it out loud]**

It will ask you questions. That is the design. Say *"just draft it"* to skip straight to a draft.

---

## 4. Packaging, before you record anything

> I want to record something about **[topic]**. Run the 4 packaging questions with me: familiar format, open loop, who the viewer becomes, authority. Build a board of thumbnail directions with candidate titles captioned underneath each, render them and show me. Do not describe them in words. At least one candidate is a real frame from actual footage of me.

No image key? Add: *"I have no image key, so give me the directions as briefs I can build myself, and I will bring the images back."*

---

## 5. The board you film from

> Read `.claude/skills/on-camera-board/SKILL.md`. Build me the board I present from for **[the piece]**, off the script at **[path]**. I will click through it and draw on it live while filming, so shape it for that, not for reading.

---

## 5b. Right before you record

> Run `director` for **[the piece]**. The brief is at **[path]**. Ask me only what the brief does not already answer, one question at a time, print the must-dos that bear on this video, and write my answers into the brief as the frame before I turn the camera on.

---

## 6. A long recording you have not touched

> Use `long-form-editor` on `**[path to the recording]**`. Tell me which recording shape it is and show me a real frame with its true duration and dimensions. Before you transcribe, ask me for the names, companies, products and terms on this tape and pass them as key terms. Then run the privacy pass: sample any screen share at 1 frame per second at full resolution and list every face, name label and piece of private interface you find, with what you would crop, blur or freeze. Render nothing until I have seen that list. Then mark the moments worth keeping with one sentence each and stop. I am picking, not you.

For a podcast episode, add: *"Follow `content/reference/podcast-edit-runbook.md`."* For a workshop or training, add: *"Follow `content/reference/workshop-edit.md` and adapt the pipeline in `~/content-studio/examples/workshop-edit/`."*

---

## 7. Making a short

> Make a vertical short from `**[path to clip]**` with `shorts-editor`. Read `content/brand.md` for my colours and fonts. Transcribe with Scribe and this key-terms file: `**[path]**`. Run the safe-area and caption-size checks and `cut-review` before you show me anything.

For a podcast or tutorial short, use this instead:

> Read the "Before you build a short" section of `.claude/skills/shorts-editor/SKILL.md` and the files it names, in that order. Then copy `~/content-studio/examples/podcast-shorts-pipeline/` into `content/videos/**[set]**/pipeline/`, set up its `config.json` with me, and run its `--selftest`. My picks are **[the brief's picks list, or the timestamps]**. Write one spec per short, run `--plan` on each and show me the plans before anything renders. A checker that did not build a short reads it at full resolution before I see it.

Expect a round or 2 of "tighten this pause, fix this word". **Say why each time.** The skill writes your correction into its own table, and that is how it compounds.

---

## 8. Reviewing a cut

> Run `cut-review` on `**[path to the cut]**`. The brief is at `**[path]**`. Give me the timestamped fix list, and serve any video page with `scripts/serve_outputs.py` so I can watch it in the browser.

---

## 9. Watching something properly

> Use `watch` on **[link]**. Frames and transcript together. Tear down the hook and the first 30 seconds, and tell me what is on screen while they say it.

---

## 10. A long render, overnight

> Render **[the thing]** with `scripts/render_detached.sh`, never as a background task in this conversation. Run `scripts/render_preflight.sh` first. If the piece folder has the 4 build files, run `scripts/verify_loop.py` on it with a deadline of **[07:00]**. In the morning, tell me what the loop fixed, what it left for a model, and what it left for me. Green is not done: look at the frames yourself before you call it ready.

---

## 11. One recording into many pieces

> Run `content-waterfall` on `**[path to the finished video]**`. Plan the pieces per platform and show me the plan, with the search pack (the searched phrase, chapters from 0:00, the description and tags) from `search-visibility`. Post nothing and change nothing live. Anything I write or pick stays exactly as I wrote or picked it.

---

## 12. When you correct it

Add this to any correction:

> and put that rule where the next session will see it: the skill, the taste file or the check script. Tell me which file.

---

## 13. When something is broken

> **[paste the exact error text, all of it]**
>
> Read `~/content-studio/TROUBLESHOOTING.md` first and tell me whether this is a known one. If not, tell me what you would need to look at to find out, and do not guess.

---

## 14. Updating

> Run `git pull` in `~/content-studio`, read `CHANGELOG.md` and show me what changed, then redo the copy from `SETUP.md` step 4, the blocks for the level in `content/setup/preferences.md` only. Never overwrite anything in `content/taste/`, `content/profile/`, `content/setup/`, `content/brand.md` or `content/PRINCIPLES.md`. If I edited a skill, show me the difference before replacing it.
