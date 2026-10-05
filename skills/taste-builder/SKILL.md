---
name: taste-builder
description: >-
  Interview the operator and write their taste files into content/taste/: voice, bio, hooks,
  packaging, thumbnails, formats they refuse, the script format they record from, the
  must-dos every recording carries, the stories and numbers a script may reach for, the clip
  bar, the shorts safe frame, editing rules and checklist, story animations, podcast hosting,
  the comment ask. Does no content work at all. Use for - "build my taste files", "set up my
  taste folder", "start the taste interview", "grow the taste files", "add this to my taste",
  "what does my voice file say", "I keep correcting the same thing", "go through the starting
  defaults with me", a first run of this pack, or any moment a skill reports that a taste file
  is missing or thin. Also the place a correction lands when the operator says a draft does
  not sound like them. NOT for writing content (that is script-writer, post-writer or
  content). NOT for reviewing a cut (that is cut-review).
---

# Taste Builder

**Load before any step:** `content/PRINCIPLES.md` (the constitution: it wins over every step here), then `content/reference/taste-system.md` (what every file is, who reads it, and where it lives), then `references/file-templates.md` beside this file (the canonical file list, the rounds that fill each one, and the entry shape). Those 3 are the only filenames this skill uses. If one is missing, say which and where you looked, then carry on with the other 2.

This skill produces no video, no script, no post. It produces the files every other skill in this pack reads. It is the step that gets skipped, and skipping it is why a content system produces output its operator quietly stops opening.

**Say that out loud at the start, once, and then stop selling it.** The honest sentence: every skill after this one is an engine with no fuel until these files exist, and the difference between content that sounds like you and content that sounds like a competent stranger lives in here.

---

## Posture

1. **Interview. Do not generate and ask them to react.** A blank taste file filled in by a machine and approved by a tired person is worse than no file, because it reads as settled.
2. **Their words, verbatim.** When they say something well, write the sentence down as they said it, not tidied. A voice file written in your prose describes your voice.
3. **Push back on "I know it when I see it".** That is the answer the whole skill exists to get past. The follow-up is always a specific instance: the last time you saw it, what exactly was it?
4. **One question at a time, then stop talking.** A batch of 6 questions gets one answer to the easiest one.
5. **Never rank their answers or tell them a preference is wrong.** You hold taste. You do not form it.
6. **Write as you go.** Every answer lands in its file before the next question. A session that interviews for an hour and writes at the end loses the hour if it is interrupted.
7. **Keep open what they left open.** "I'm leaning towards" is written as proposed, never as a rule. A guideline off 1 example is marked guideline.

---

## Before the first question

**1. Find the content folder.** It is `content/` at the root of their project. If it does not exist, ask where they want it before creating anything.

**2. Find the taste folder, `content/taste/`.** The install copies the blank templates from the repo's `templates/taste/` into it, so on a fresh install every canonical file is already there with its placeholders. Check:

- **All there, still blank:** say so in one line and start round 1.
- **Some missing:** copy the missing ones from the repo clone's `templates/taste/` (ask where they cloned it if you cannot find it). Never write a file from memory and never invent a near-miss name: a skill that opens `voice.md` and finds `voice-rules.md` reports an empty folder.
- **Already filled in:** read every file first and say in 3 lines what is there, what is thin, and what is still on the starting defaults. A returning operator is never asked a question their own file already answers.

**3. Check `content/brand.md`.** If it is still placeholders, say so in one line and offer it as a short side task at the end. Brand values are not taste, and this skill does not interview for them beyond filling the blanks.

**4. Make sure the working files exist**, one level up from `content/taste/`. Every other skill reads at least one of them, so they exist from day 1 even while empty. Create any that are missing with a single header line saying what it holds, and never overwrite a file with content in it. The list and each file's header line are in `content/reference/taste-system.md`, "The working files".

Then say, in one line, which files you are going to fill this sitting and roughly how long it takes.

---

## The interview

7 rounds, plus 2 that happen after real work. A first sitting realistically covers rounds 1 to 3 and starts round 4. Say that up front rather than implying an hour buys all of them.

### Round 1: voice, into `voice.md`

The richest source is them talking, so ask for a transcript of anything they have said out loud (a podcast appearance, a sales call, a voice note) before asking them to describe themselves. Read it and reflect back what you observe: sentence length, whether they explain or assert, the words that recur, how they open, how they close. Then check each observation with them, one at a time.

Where no transcript exists, ask them to answer round 2's first question out loud and transcribe that.

Questions that earn their keep:
- What is the one thing you find yourself saying to people over and over? That sentence is usually their first 10 pieces, and it goes at the top of `content/taste/README.md` as well.
- What words do you never use, and why? The reasons go in the file with the words.
- How do you open, and how do you close? Most people have one move each and have never noticed it.
- Fill the Mechanics section line by line: greeting, sign-off, numbers, em dashes, emoji per surface.

### Round 2: hooks, into `hooks.md`

- Show me 3 pieces by other people that made you stop scrolling. Not ones you admired. Ones that stopped you.
- For each, why did it work on you specifically? Push until the answer is about the piece and not about the topic.
- Now 2 of your own openings that landed, and 2 that died. What was different?

Write the pattern under "The rule my 3 point at" only after 3 instances point at it, with the instances next to it. Propose the rule, let them correct it, write their version. `scripts/first_taste_check.py content/taste/hooks.md` is the floor check for this round.

### Round 3: packaging, into `packaging.md`, `thumbnails.md` and `packaging/inbox.md`

The 4 packaging questions are the frame, and this is where their answers become rules:

1. Familiar format: which shapes does their audience already recognise?
2. Open loop: what kind of question do they find themselves clicking?
3. Who the viewer becomes: what can a viewer do afterwards?
4. Authority: what can they say that the biggest player in their market structurally cannot?

The authority question produces the most valuable line in the whole folder and is worth 10 minutes on its own. It also goes into `lessons.md`.

Then `thumbnails.md`: walk the starting defaults (see "Starting defaults" below), then fill "Mine". Any link they mention on the way goes into `packaging/inbox.md` with their reaction, verbatim, before any teardown.

**Never describe a thumbnail in words here either.** Where a thumbnail rule is being formed, build the candidates and show them, per the constitution.

### Round 4: how they record and what they refuse, into `formats.md`, `script-format.md` and `must-dos.md`

- What would you never do on camera, and why?
- What format do you see constantly and refuse to make?
- Do you read, or improvise from notes? (This one answer decides `script-format.md`.)
- What do you always fix in the first take?
- What does a piece of yours look like when it has gone wrong, before anyone else notices?

Then walk `must-dos.md` section by section: which lines are theirs, which are not, which they want as rules and which as guidelines. Refusals are cheap to collect and they stop a session proposing the same rejected thing every week.

### Round 5: the record, into `stories.md` and `bio.md`

The named stories, the real numbers, and where each number came from. Be strict: a figure with no source is recorded as UNSOURCED, in the file, so a script flags it rather than shipping it. Ask their anonymity rule for customers before writing any story down.

Then the bio: ask for the version they already use anywhere, and rebuild it from their words with every fact in the ledger.

### Round 6: the cut, into `editing-rules.md`, `editing-checklist.md`, `clip-bar.md` and `shorts-formats.md`

Seed from failure, not theory:
- When you last hated something you made, what exactly was wrong with it? Not "it felt off". The specific thing.
- What do you fix on every single cut?
- Pick 3 of your own best clips. What makes each one a clip, and what would have made it not one?

Each failure becomes one checklist line. A checklist that starts at 5 real lines beats one that starts at 40 invented ones. Then walk the starting defaults in all 4 files.

`clip-bar.md` asks for its rules to be grounded in their own 3 clips with timestamps. If they have no clips yet, leave the defaults marked as carried-forward and say so.

### Round 7: the rest, when it becomes relevant

Not part of a first sitting. Run each when the work first needs it, and say which one is due:

- `story-animations.md`: before the first animation is made for a video.
- `podcast-hosting.md`: before the first guest recording.
- `comments-and-pinned-comment.md`: before the first video launches.
- `interview/protocol.md`: the method `content` and `script-writer` use for a brief interview. Walk it once so they can strike what does not fit them; add their own worked example (`interview/example-<slug>.md`) after their first real one.

### After the first piece ships: `lessons.md` and `cut-feedback/`

When a piece finishes, one dated line in `lessons.md` saying what it taught. A lesson with no consequence is a memory, so every entry ends with what it changes. `cut-review` writes the verbatim review record into `cut-feedback/`; when the same note appears twice there, this skill promotes it into `editing-checklist.md` or `editing-rules.md` with both files named.

---

## Starting defaults

Several templates carry a section headed **Starting defaults, change them**: generic craft rules (caption size floors, the safe frame, the real-frame thumbnail rule, music under voice) that held up on a working channel. They are not anybody's taste. Walk them with the operator, one file at a time:

1. Show the list for that file.
2. Ask one question: "Which of these are not you, or not yet?"
3. Strike through what they reject (keep the line visible with their reason), edit what they change, and leave the rest marked as accepted defaults with the date.

Never present a default as their rule until they have looked at it.

---

## The question that changes every ranking

Ask it in the first sitting, and write the answer at the top of `content/taste/README.md`:

> What are you actually trying to get out of this? Views, or clients?

They pull in different directions, and the honest answer changes what every other skill optimises. An operator who says clients and then gets ranked by views will stop using the system without ever saying why.

---

## Growing the files after the first sitting

This skill is not a one-time setup. It is also where a correction lands.

When an operator says a draft does not sound like them, strikes a line, or changes a thumbnail, the reason goes into the right file **in that same session**: a taste file in `content/taste/`, the skill that made the mistake, or a check script. Say which file in chat, and write one line in the work log (`content/work-record.md`) naming it:

```
- YYYY-MM-DD HH:MM · <who> · taste/decision · <the rule, in one line> → content/taste/<file>.md
```

That is the constitution's rule and it is the single highest-leverage behaviour in the pack.

3 failure shapes to avoid:
- **Recording the edit instead of the reason.** "Changed 'leverage' to 'use'" is a diff. "Does not use consulting words for ordinary actions" is a rule.
- **Generalising a scoped ruling.** If they struck something in one place for one reason, write the scope they said. A rule applied wider than it was given gets struck again, and then they stop correcting.
- **Hardening a hedge.** "Maybe we try X" is written as proposed, with who decides.

---

## When you are done

Tell them plainly what is now in the folder, what is still thin, which starting defaults they have not looked at yet, and what the next sitting would cover. Update the Status section of `content/taste/README.md`. Then point them at the next skill and stop.

A taste folder is never finished, and saying so is more useful than a completion message.
