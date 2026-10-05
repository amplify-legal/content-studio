# Prompts to paste into Claude Code

Ready-made prompts for every stage, in the order you will hit them. Edit the bracketed parts before you paste.

**First night and short on time?** Skip to "Tonight instead" below and do only that. The full install will still be here tomorrow.

---

## 1. The full install

Open Claude Code in the folder you do content work in (your project), and paste:

> Install Content Studio into this project with me, one step at a time.
>
> 1. Clone `https://github.com/amplify-legal/content-studio.git` to `~/content-studio` (or `git pull` there if it already exists). Read its `START-HERE.md` and `SETUP.md` before doing anything else.
> 2. Before you change anything, check what I already have: ffmpeg, ffprobe, node, python3 (3.10 or newer), yt-dlp, an existing `.claude/skills/` in this project, an existing `CLAUDE.md`, an existing `content/taste/` folder, and which of these keys are set in `.env` or my environment: ELEVENLABS_API_KEY, DEEPGRAM_API_KEY, MIXROUTE_API_KEY. Show me what is there and what is missing. Never print a key's value.
> 3. Copy, following the table at the top of `SETUP.md`: `skills/*` into `.claude/skills/`, `scripts/*` into `scripts/`, `reference/*.md` into `content/reference/`, `reference/PRINCIPLES.md` into `content/PRINCIPLES.md` (only if I do not have one), `reference/frameworks/*` into `content/frameworks/`, `templates/taste/*` into `content/taste/` and `templates/brand.md` into `content/brand.md`. Use `cp -n` for anything under `content/taste/`, `content/brand.md` and `content/PRINCIPLES.md`, so nothing of mine is ever overwritten. If a skill folder of the same name already exists and differs, show me the difference and ask before replacing it.
> 4. Add the lines from `SETUP.md` step 5 to this project's `CLAUDE.md`, never to `~/.claude/CLAUDE.md`.
> 5. Make sure `.env` is in this project's `.gitignore`.
> 6. Run every self-test in `SETUP.md` step 13 and show me the output. Use `PYTHONDONTWRITEBYTECODE=1`.
>
> I **[do / don't]** want the video half (ffmpeg, node, transcription). I **[do / don't]** want media-gen, which spends money. Ask before installing any system package. Never delete anything: if something is in the way, tell me. Do not summarise the repo back to me.

---

## Tonight instead: your first taste file, 20 minutes

Have 3 pieces by other people in front of you that made you stop scrolling. Do `SETUP.md` step 1 (2 minutes of copying), then open Claude Code in your project and paste:

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

If you did the 20 minute sitting, start with: *"I already have hooks.md. Read it, do not redo it, and start at round 1."* Then:

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

## 6. A long recording you have not touched

> Use `long-form-editor` on `**[path to the recording]**`. Tell me which recording shape it is and show me a real frame with its true duration and dimensions. Before you transcribe, ask me for the names, companies, products and terms on this tape and pass them as key terms. Then run the privacy pass: sample any screen share at 1 frame per second at full resolution and list every face, name label and piece of private interface you find, with what you would crop, blur or freeze. Render nothing until I have seen that list. Then mark the moments worth keeping with one sentence each and stop. I am picking, not you.

For a podcast episode, add: *"Follow `content/reference/podcast-edit-runbook.md`."* For a workshop or training, add: *"Follow `content/reference/workshop-edit.md` and adapt the pipeline in `~/content-studio/examples/workshop-edit/`."*

---

## 7. Making a short

> Make a vertical short from `**[path to clip]**` with `shorts-editor`. Read `content/brand.md` for my colours and fonts. Transcribe with Scribe and this key-terms file: `**[path]**`. Run the safe-area and caption-size checks and `cut-review` before you show me anything.

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

> Run `content-waterfall` on `**[path to the finished video]**`. Plan the pieces per platform and show me the plan. Post nothing. Anything I write or pick stays exactly as I wrote or picked it.

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

> Run `git pull` in `~/content-studio`, show me what changed, then redo the copy from `SETUP.md` step 4. Never overwrite anything in `content/taste/`, `content/brand.md` or `content/PRINCIPLES.md`. If I edited a skill, show me the difference before replacing it.
