# Start here

**This document is addressed to the Claude Code session, not to the person running it.**

You have been pointed at Content Studio. Do not summarise it back to them. Work out which situation below you are in and do that.

---

## Read the constitution first, and let it win

`content/PRINCIPLES.md` (in this repo: `reference/PRINCIPLES.md`) governs everything here. When a rule there conflicts with a process step anywhere else, including this file, the constitution wins. Read it before you answer them.

---

## Your standing posture

1. **Ask, then show, then render. In that order, every time.** Your first move on any content thought is a question, not a draft. Your second is something they can look at: a rendered thumbnail, labelled samples, a cut. The full render is last. Generation without questions happens only when they say "just draft it" or re-run a stage they already shaped.
2. **Their taste is theirs.** It lives in `content/taste/` in their own words. You apply it. You never average it toward what performs and never tell them their judgment was wrong. When you disagree, show them the thing and let them look.
3. **Keep open what they leave open.** Anything they have not settled is written as **proposed**, with who decides named. Never stamp their name on a decision they did not make.
4. **Show, never describe.** Never propose a thumbnail in words: build it, show it, captions of candidate titles underneath. Never ask them to choose between options they have not seen. Every option carries a visible label, and the label is the same in the image, the file name, the chat and the board.
5. **Catch what any viewer would catch; ask about taste.** A clipped word, a black first frame, audio out of sync, a misspelled name in a caption: yours to fix without asking. Pace, style, music, framing: theirs, and their answer becomes a rule in a taste file.
6. **Green is not done.** `scripts/verify_loop.py` and the check scripts passing means nothing mechanical is broken. Before you hand anything over, look at frames yourself (start, middle, end, and around every cut) and read the captions.
7. **cut-review runs before any cut reaches them.** Whatever question is still open about a cut, the review runs first and the open question rides with it. The end-of-run review of a whole video is a separate reviewer sub-agent reading the whole conversation, never you reviewing yourself.
8. **Privacy is checked at full resolution.** Every frame pulled from a recording is checked for faces, name labels, client names and private screen content (sidebars, conversation titles, file paths) before it can be used.
9. **Long renders run detached.** `scripts/render_detached.sh`, never a conversation background task. Several overnight go through `scripts/render_queue.sh`. Check free disk first.
10. **A video page is served, not opened.** Start `scripts/serve_outputs.py` and open `http://localhost:4200/<path>`, because a page opened as a file often will not play its videos.
11. **A correction lands where the next session will see it, in the same session.** Their edit goes into the skill, the taste file or the check script now, and you say which file. A fix that only touches today's piece says so and why.
12. **Nothing publishes without the person's approval recorded on the row** (`approved_by`), and only through the posting module at the `full` level, proven by reading the platform back. At `lite` and `standard`, and on any platform that stays a hand card, drafts, queues and finished files are the output and the person presses the button. Messages and connection requests to people are never automated.
13. **Know their level, and never fake a missing skill.** `content/setup/preferences.md` says `lite`, `standard` or `full`. When a step needs a skill their level did not install, say which skill and which level carries it, offer "upgrade me to <level>", and carry on with what is installed.
14. **Read the profile before the first question.** `content/profile/summary.md` holds who they are, the business, the objectives and the one metric. Never ask what it already answers. When it is missing, the deep dive has not run: say so in one line and offer it.

---

## Situation 1: nothing is installed yet

1. **The level choice first.** Ask the 5 preference questions in `SETUP.md` section 0, one at a time (time today, who edits, posting by hand or by machine, platforms, computer). Recommend a level following "The pick, in order" in `skills/creator-profile/reference/levels.md`, in 2 lines with the reason, and let them choose. Write `content/setup/preferences.md` (`SETUP.md` step 2).
2. **Install that level only.** Walk `SETUP.md` steps 1 to 6, using only the step 4 blocks for their level, running each step's check before the next. For `standard` and `full`, walk that level's remaining steps on the evenings they choose; they need not be tonight.
3. **The first sitting, at every level, is the deep dive:** `.claude/skills/creator-profile/SKILL.md` (`SETUP.md` step 7). Nothing is drafted in their name before sitting 1 of it is on disk. It runs in 3 sittings they can stop and resume ("pick up my profile"), and it ends with a summary they confirm and a recommended level; if that differs from what they installed, say so and offer the change.

If they are tired or short on time after the install, offer the 20 minute path in `SETUP.md` step 7b instead of a profile sitting tonight: they bring 3 pieces by other people that stopped them, and it produces `content/taste/hooks.md` in their own words. `scripts/first_taste_check.py` is the check at the end of it. The profile still comes next.

Never ask them to paste an API key into the chat. Tell them which file (`.env` in their project root) and which variable name. `lite` needs no key at all.

## Situation 1b: they want to change level

"Upgrade me to standard", "go full", "take me back to lite". Follow "Changing level" in `SETUP.md`: read `content/setup/preferences.md`, run only what the new level adds (or, going down, stop what runs on its own first and move the skills above the new level to `.claude/skills-parked/`), run that level's self-tests, and rewrite the `level:` and `upgrades:` lines with the date. Nothing they wrote is overwritten, and nothing is deleted. When they ask which level fits, read `content/profile/` and answer with `skills/creator-profile/reference/levels.md`.

## Situation 1c: their business, goals or platforms changed

Run `.claude/skills/creator-profile/SKILL.md`, "Keeping it current": open only the section that changed, write the change dated with the old line struck and visible, rebuild the summary, and ask them to confirm it again.

## Situation 2: installed, and they bring a content thought

Run `.claude/skills/content/SKILL.md`. It is the one door. Read `content/profile/summary.md` and their taste files before your first question and never ask something a file already answers.

## Situation 2b: they are about to record

Run `.claude/skills/director/SKILL.md` before the camera turns on. It asks only what the brief has not answered, prints the must-dos that bear on this video, and writes the answers into the brief as the frame. Every later step (the edit, the cut review, the shorts) reads that frame and the kind's sheet in `content/taste/kinds/` first.

## Situation 3: they have a recording to edit

These skills come with `standard`. At `lite`, say so in one line, offer "upgrade me to standard", and meanwhile help with what lite can do (the director's frame before the next recording, the posts and the script from what they already have).

- A long raw recording (a call, a podcast, a workshop, a screen share): `.claude/skills/long-form-editor/`, then `content/reference/podcast-edit-runbook.md` or `content/reference/workshop-edit.md`. The privacy pass runs before anything renders. `examples/workshop-edit/` is a working pipeline to adapt.
- A picked clip to a vertical short: `.claude/skills/shorts-editor/`. A human picks the clips. This is not an auto-clipper. For podcast and tutorial shorts, read its "Before you build a short" section, then copy `examples/podcast-shorts-pipeline/` into the video's own folder and read its `README.md`. The method behind every number is in `content/reference/edit-lab/`.
- A finished cut: `.claude/skills/cut-review/` before they watch it.

## Situation 3b: something is ready to post

- At `lite` and `standard`: walk the hand checklist in `SETUP.md` step 7c with them. They press post; you read the platform back with them before it is called posted.
- At `full`: `.claude/skills/posting/SKILL.md`. Rows go out only once they carry `approved_by`, through each platform's official route, and each is read back. A platform with no posting route for their account stays a hand card, and the step 7c checklist applies to it.

## Situation 4: they want to change how it works

That is their taste, not a setting. Write their words into the right file in `content/taste/`, quoted, with today's date, and say in one line which file you changed.

---

## The sittings, for a first install

| # | Sitting | Level | Run | Produces |
|---|---|---|---|---|
| 1 | The deep dive on them | every level | `creator-profile` (3 sittings) | `content/profile/` in their words, a summary they confirm, a recommended level |
| 2 | The constitution | every level | `content/PRINCIPLES.md` | Their version of it, argued with and edited |
| 3 | Taste | every level | `taste-builder` | Their taste files, in their words, starting from the profile |
| 4 | The door | every level | `content` | A week of one entry point for everything |
| 5 | Packaging and the board | standard | `media-gen`, `design-dna`, `on-camera-board` | A thumbnail that passed the 4 questions, and the board they film from |
| 6 | The recording and the edit | `director` at every level; the edit at standard | `director`, `long-form-editor`, `shorts-editor`, `cut-review` | A frame written before the camera turns on, a watchable cut, a finished short, a review gate |
| 7 | The waterfall | standard | `content-waterfall` (it calls `search-visibility`) | One recording into many pieces, findable in search |
| 8 | What runs without them | full | `routines/content-briefing.md`, `scripts/verify_loop.py`, `posting/README.md` and `posting` | A briefing that fires before they sit down, an overnight render that checks itself, and approved posts going out on time, each read back |

Sitting 1 always comes first. After it, recommend sitting 2 if they have no preference. If they have a long recording doing nothing and they are at `standard`, start sitting 6 there, because it is the fastest way they see this produce something real.

**Sitting 3 is the one they will want to skip.** Say plainly that every skill after it is an engine with no fuel until it is done. The profile makes it shorter, not unnecessary.

**Sitting 5 does not need the paid image skill.** Without a key they build thumbnail candidates in any design tool and bring the images back. What you never do is describe a thumbnail in words because the renderer is missing.

**Sitting 8 comes last on purpose:** learn first, automate after, hand off last (`content/PRINCIPLES.md`, section 2).

---

## The 4 packaging questions

A piece is not ready to record until it passes all 4, run with the thumbnail built and shown:

1. **Familiar format.** Does the viewer recognise the shape before they understand the topic?
2. **Open loop.** Is there a question in the title and thumbnail that only watching answers?
3. **Who the viewer becomes.** What are they after watching that they were not before?
4. **Authority.** Why this person, on this subject?

They perform this check, not you. A self-review that comes back green proves nothing.

---

## The files

| Path in this repo | Installed to | For |
|---|---|---|
| `skills/` | `.claude/skills/` | 16 skills, one folder each; which ones depend on the level (`skills/creator-profile/reference/levels.md`) |
| `skills/creator-profile/` | `.claude/skills/creator-profile/` | The deep dive; it writes `content/profile/` |
| `skills/posting/` and `posting/` | `.claude/skills/posting/` and `posting/` at the project root | Posting by machine, `full` only; the plan is `content/posting/plan.jsonl`, the log `content/posting/log.jsonl`, the config `content/posting/config.json` |
| `scripts/` | `scripts/` | Render discipline, the verify loop, the copy check, the video server |
| `reference/` | `content/reference/` | How the system fits, the edit runbooks, the lessons |
| `reference/edit-lab/` | `content/reference/edit-lab/` | The edit lab book: how each technique was got to work and what failed |
| `reference/PRINCIPLES.md` | `content/PRINCIPLES.md` | The constitution |
| `reference/frameworks/` | `content/frameworks/` | Shapes for a short, a pillar video, a carousel, a brief |
| `templates/taste/` | `content/taste/` | Their taste files, empty until they fill them |
| `templates/taste/kinds/` | `content/taste/kinds/` | One sheet per kind of video, starting defaults they change |
| `templates/brand.md` | `content/brand.md` | Their colours, fonts, logo and photo paths |
| `examples/workshop-edit/` | stays in the clone, copied into a video's folder when used | A working workshop edit pipeline |
| `examples/podcast-shorts-pipeline/` | stays in the clone, copied into `content/videos/<set>/pipeline/` when used | The reference podcast and tutorial shorts builder |
| `routines/` | `routines/`, then their scheduler (`full`) | The morning content briefing, the content-day routine, the nightly posting refresh |
| (written during setup) | `content/setup/preferences.md` | Their level and the answers that picked it |
| (written by the deep dive) | `content/profile/` | `who.md`, `business.md`, `objectives.md`, `style.md`, `inspirations.md`, `platforms.md`, `summary.md`, `progress.md` |
