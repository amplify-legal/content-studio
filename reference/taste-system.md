# The taste system

> Installed at `content/reference/taste-system.md`. Read by `taste-builder` (which writes the files described here) and by every engine in this pack before it reads the files themselves. This document explains what the files are, who reads each one, and why they are shaped this way. It does not hold anybody's taste.

---

## The problem this solves

Every skill in this pack is an engine. An engine needs fuel, and the fuel is your judgment written down in a form a session can read on its way to doing the work.

Without these files, a content system produces competent generic output and you spend your time correcting the same things forever. The corrections do not accumulate, because there is nowhere for them to land. With the files, a correction lands once and the next session already knows.

That is the whole mechanism, and it is worth being blunt about the cost: the files take an hour to start and they are never finished. The hour is the price of the system sounding like you.

---

## Where everything lives

```
content/
  PRINCIPLES.md        the constitution: wins over every step in every skill
  brand.md             your colours, fonts, logos and photo paths (not taste)
  brand/people/        real photographs of the people, photographs only
  taste/               your judgment, one file per question (below)
  frameworks/          how each kind of piece is shaped (starting points)
  reference/           how the machinery works, including this file
  live.md ... work-record.md   the working files (below)
  briefs/              one brief per piece
  videos/<slug>/       one folder per video: raw/, build/, renders/
```

The repo ships the blank taste files in `templates/taste/` and the install copies them into `content/taste/`. **The folder is plain markdown on purpose.** You have to be able to open any of these files, disagree with a line, and change it in 10 seconds. A taste file you cannot argue with in a text editor is a taste file that stops being true.

---

## The taste files, and who reads each one

Every file opens with a header line saying what it is, who writes it, and which skills read it. You write them, in your own words, through `taste-builder`. Some carry a section headed **Starting defaults, change them**: generic craft rules that held up on a working channel (caption floors, the safe frame, the real-frame thumbnail rule). Those are not anybody's taste until you have looked at them and kept them.

| File | What it holds | Read by |
|---|---|---|
| `README.md` | what you are trying to get out of this (views or clients), the one problem your customers keep repeating, which file answers which question, rules versus guidelines, status | every skill |
| `voice.md` | how you talk and write: register, banned words, mechanics, per-surface rules, corrections to lines put in your mouth | `script-writer`, `post-writer`, `content`, `shorts-editor`, `content-waterfall` |
| `bio.md` | your canonical first-person bio, a short version, and the fact ledger behind it | `script-writer`, `post-writer`, `content`, `content-waterfall` |
| `hooks.md` | 3 pieces that stopped you and why, the rule they point at, your own openings that landed and died | `script-writer`, `post-writer`, `content`, `shorts-editor` |
| `packaging.md` | the 4 packaging questions, title patterns with proof, exclusion, creator teardowns | `content`, `media-gen`, `watch`, `content-waterfall`, `script-writer` |
| `thumbnails.md` | how thumbnails are proposed, built and judged, then your own rules and rounds | `media-gen`, `content`, `watch`, `design-dna`, `shorts-editor` |
| `packaging/inbox.md` | links that stopped you, with your verbatim reaction and who sent it, before any teardown. Teardowns sit beside it as `packaging/<slug>.md` | `watch`, `content`, `media-gen` |
| `formats.md` | what you refuse, the shapes and length bands you record in, how you record | `content`, `on-camera-board`, `script-writer`, `content-waterfall` |
| `script-format.md` | the shape of the script you actually record from | `script-writer`, `on-camera-board`, `content` |
| `must-dos.md` | what every recording carries: before the camera, the intro beats, in the take, the "what did we miss" question after the take, before publish | `content` (every recording plan, session and launch), `on-camera-board`, `script-writer`, `cut-review`, `long-form-editor` |
| `stories.md` | the fact ledger: named stories, numbers with receipts, your anonymity rule | `script-writer`, `post-writer`, `content`, `content-waterfall`, `cut-review` |
| `clip-bar.md` | what makes a moment a clip, and how a cut lands, grounded in your own best clips | `shorts-editor`, `script-writer`, `cut-review`, `content`, `content-waterfall` |
| `shorts-formats.md` | the vertical safe frame, caption floors and look, crops, your format family | `shorts-editor`, `cut-review`, `content`, `content-waterfall` |
| `story-animations.md` | animations that teach the sentence being said, never mood footage, and which tool for which job | `media-gen`, `long-form-editor`, `shorts-editor`, `content`, `on-camera-board` |
| `editing-rules.md` | the durable layer: pace, silence, music, endings, your "every edit" rules, how you like to be worked with | `long-form-editor`, `shorts-editor`, `cut-review`, `content` |
| `editing-checklist.md` | the mechanical layer, one line per thing that has gone wrong once, run by a machine before a person watches | `cut-review`, `long-form-editor`, `shorts-editor` |
| `cut-feedback/` | one file per cut review, your verbatim words. The corpus the checklist learns from | `cut-review`, `long-form-editor`, `shorts-editor`, `taste-builder` |
| `podcast-hosting.md` | the run sheet you record a guest conversation from, and the kit for when you are the guest | `content`, `script-writer`, `long-form-editor` |
| `comments-and-pinned-comment.md` | the comment ask, the pinned comment, the closing line | `script-writer`, `content`, `content-waterfall`, `post-writer` |
| `interview/protocol.md` | the method for a brief interview: layer order and 9 principles | `content`, `script-writer` |
| `interview/template.md` | the blank each brief interview fills, copied to `content/videos/<slug>/interview.md` | `content`, `script-writer` |
| `lessons.md` | what each finished piece taught you, the taste metric, what only you can say | `content`, `content-waterfall`, `long-form-editor`, `script-writer` |

These are the only taste filenames any skill in this pack opens. `taste-builder/references/file-templates.md` holds the same list with the round that fills each file and the minimum to call it started.

### What goes in each, and what does not

**`voice.md` is how you talk, not how you want to sound.** The best source is a transcript of you talking, not a draft you wrote carefully. A voice file that describes an aspiration produces copy in the aspiration's voice, which is nobody's.

**`hooks.md` is evidence, not theory.** Pieces that stopped you, not pieces you admired, and a pattern only once 3 instances point at it.

**`packaging.md` and `thumbnails.md` hold rules you have proven, with the proof next to each one.** An untested opinion goes in marked UNTESTED, so a later session does not treat it as settled. Raw links never go straight into either: they land in `packaging/inbox.md` with your reaction first, because your first reaction is the data and analysis overwrites it.

**`editing-rules.md` is judgment a machine applies but never rules on. `editing-checklist.md` is mechanics a machine runs item by item.** The split matters: the checklist clears typos before you watch, so your review time goes to taste.

**`formats.md` names what you will not do**, which is as load-bearing as what you will. A refusal written down is a refusal a session stops proposing.

**`must-dos.md` is one list instead of rules scattered across files.** Every line names the recording or review it came from, so it can be checked rather than trusted.

**`stories.md` is the only place a script may take a figure from.** Anything not in it gets flagged rather than written, and an UNSOURCED number stays marked.

---

## The working files, beside the taste folder

The taste folder holds your judgment. These hold what is in motion. They sit in `content/`, one level up from `taste/`, and they exist from day 1 even when empty, because every skill reads at least one of them. When `taste-builder` creates one, it writes only the header line in the second column.

| File | Header line | What it is for |
|---|---|---|
| `content/live.md` | one row per piece in motion, with its stage and what it is waiting on | answers "what's alive" without anybody remembering. A piece leaves when it ships or is killed |
| `content/graveyard.md` | killed work, one dated row each with the reason. Read every run so nothing gets rebuilt | a decision nobody wrote down gets remade in 6 weeks by somebody being helpful |
| `content/ideas.md` | your own half-thoughts, verbatim, newest first | these outrank anything a machine found, always |
| `content/seeds.md` | raw fragments exactly as you said them, untouched | a seed is a sentence you said, an idea is a thought you formed. Any dictated block about content lands here verbatim before any analysis |
| `content/signal.md` | what the machine found: outliers, competitor pieces, buyer language. Your ideas always rank above this | kept apart from `ideas.md` so nobody has to trust a session to remember which was which |
| `content/briefs/` | one file per piece, the record of its interview | `cut-review` checks the cut against the brief, not against memory |
| `content/in-flight.md` | one row per open session: who, start time, item, what it intends to write. Cleared at close | a map, never a gate. The real duplicate check is re-reading a file right before writing it |
| `content/scoreboard.md` | the numbers you keep by hand | makes a weekly review possible without exporting anything |
| `content/work-record.md` | one line per piece of work, written as it happens | described next, because it does a different job |

---

## The work record

One plain markdown file per person. One line per meaningful piece of work, written **as the work happens**, never as a summary at the end of the session or the week.

The shape, exactly, because scripts read these rows field by field:

```
- YYYY-MM-DD HH:MM · <who> · <area>/<type> · <one line>
```

**Who** did it, written the same way every time. **Area and type joined by a forward slash**: the area is whatever part of the work it touched (content, packaging, the edit, taste), and the type is one of 5 words: `build` for something made, `decision` for something settled, `ship` for something that went live, `research` for something found out, `note` for everything else worth a line. Then the **one line**.

Write the who field even when you work alone, and keep the slash. Drop the name and the area slides into the position anything reading the file treats as the person.

```
- 2026-03-04 11:20 · sam · packaging/decision · killed the split-screen thumbnail direction, reads as a reaction video
- 2026-03-04 14:05 · sam · taste/decision · caption cap height raised after the phone read failed → content/taste/shorts-formats.md
```

One file per person (`content/work-record.md`, `content/work-record-<name>.md` for a second person) is what lets 2 people work the same day without writing over each other.

---

## The 2 rules that keep the system honest

**1. Taste is data. A skill is an engine. A skill never restates a taste rule.**

The moment a rule about your hooks is written inside a skill, you have 2 copies, and one of them will be wrong within a month. Skills read these files. They do not quote them, cache them, or carry a default version of them "to start from". The starting defaults inside the templates are the one deliberate exception, and they live in your taste files, where you can strike them, not in the skills.

The practical test: hand this pack's skills to someone whose taste is the opposite of yours, point them at their own taste folder, and they should get output that sounds like them.

**2. A correction lands where the next session will see it, in the same session, and the work log names which file.**

Not later, not in a summary at the end of the week. You say "that hook is wrong and here is why", and before that conversation ends the reason is a line in the right file, the session tells you which file in chat, and one work-record line names it (the second example row above). The right file is one of 3:

- **a taste file** in `content/taste/`, when it is about your judgment (voice, packaging, what a clip is);
- **the skill** that made the mistake, when it is about how the machine works;
- **a check script**, when a rule keeps being broken and can be checked mechanically.

A fix that only touches today's piece says so out loud, and says why.

The cost of getting this wrong is measurable. A caption size rule that lived in one episode's build script instead of the taste folder was broken again on 12 of 15 renders 3 days later. The rule was known. It was simply not written where the next session would look. The work-record line is what tells you, 3 weeks later when a fault reappears, whether the rule was ever written down and where to look.

---

## How the files get built and grow

`taste-builder` interviews you and writes them. It does no content work at all, which is exactly why it gets skipped, and skipping it is why most content systems produce output their operator quietly stops reading.

They then grow 3 ways, none of them scheduled:

- **A correction on a live piece** goes into the right file the same session, per rule 2.
- **A finished piece** gets a dated entry in `lessons.md`.
- **A cut review** gets a verbatim file in `cut-feedback/`, and a note that appears twice becomes a checklist line.

A stalled taste folder is a real signal that the system is not being used.

---

## The one thing a machine must never do to these files

**It never averages your taste toward what performs.**

A session may report that a piece underperformed, and it may show you a pattern in the numbers. It may not quietly soften a rule you wrote because the data leans the other way, and it may not tell you your judgment was wrong. Where a finding conflicts with a line in your taste folder, that conflict is reported to you as a conflict, with both sides, and you settle it.

This is the constitution's rule. `content/PRINCIPLES.md` wins over everything here.
