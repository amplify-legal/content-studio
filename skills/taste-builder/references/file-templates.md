# Taste file templates

> The canonical list of taste files, the round that fills each one, and the shape every entry takes. The skeletons themselves are the template files: the repo ships them in `templates/taste/`, and the install copies them into `content/taste/`. This file never restates a skeleton, so the 2 can never drift apart.

## The rules for every file

- **These filenames are the only ones this pack uses.** Every skill opens them by name. Never invent a near-miss (`voice-rules.md` for `voice.md`, `packaging-inbox.md` for `packaging/inbox.md`): a skill that opens the right name and finds nothing reports an empty folder and drafts in nobody's voice.
- **A missing file is copied from the repo clone's `templates/taste/<file>`**, never written from memory.
- **Every file opens with one header line** saying what file it is, who writes it, and which skills read it. Keep that line when filling the file in.
- **Their words, verbatim.** Write their sentences into the sections, in quotes where they said them. Do not fill a section because the template has one: an empty section with `OPEN:` on it is honest and useful, and a section filled with a sensible default is neither.
- **Placeholders look like `<...>`**, and like `[...]` in `hooks.md`, which `scripts/first_taste_check.py` looks for. A file is not started while its main sections are still placeholders.
- **Starting defaults stay visibly separate from theirs.** A file with a "Starting defaults, change them" section keeps those lines under that heading until the operator has looked at them. What they accept, change or strike is dated.
- **Every file ends with a Retro section** where new rules land.

## The canonical set

| File (in `content/taste/`) | Filled in | What it holds | Read by |
|---|---|---|---|
| `README.md` | before round 1, updated every sitting | views or clients, the one problem customers repeat, which file answers which question, rules versus guidelines, status | every skill |
| `voice.md` | round 1 | how they talk and write: register, banned words, mechanics, per-surface rules, corrections | `script-writer`, `post-writer`, `content`, `shorts-editor`, `content-waterfall` |
| `hooks.md` | round 2 | 3 pieces that stopped them and why, the rule the 3 point at, their own openings that landed and died | `script-writer`, `post-writer`, `content`, `shorts-editor` |
| `packaging.md` | round 3 | the 4 questions, title patterns with proof, exclusion, creator teardowns | `content`, `media-gen`, `watch`, `content-waterfall`, `script-writer` |
| `thumbnails.md` | round 3, grown every round | starting defaults for building and judging thumbnails, then their own rules and rounds | `media-gen`, `content`, `watch`, `design-dna`, `shorts-editor` |
| `packaging/inbox.md` | any time a link stops them | links with their verbatim reaction and who sent it, before any teardown | `watch`, `content`, `media-gen` |
| `formats.md` | round 4 | what they refuse, the shapes and length bands they record in, how they record | `content`, `on-camera-board`, `script-writer`, `content-waterfall` |
| `script-format.md` | round 4 | the shape of the script they record from | `script-writer`, `on-camera-board`, `content` |
| `must-dos.md` | round 4, grown every recording | what every recording carries: before the camera, intro beats, in the take, after the take, before publish | `content`, `on-camera-board`, `script-writer`, `cut-review`, `long-form-editor` |
| `stories.md` | round 5 | the fact ledger: named stories, numbers with receipts, the anonymity rule | `script-writer`, `post-writer`, `content`, `content-waterfall`, `cut-review` |
| `bio.md` | round 5 | the canonical first-person bio, a short version, and its fact ledger | `script-writer`, `post-writer`, `content`, `content-waterfall` |
| `clip-bar.md` | round 6 | what makes a moment a clip, and the 6 craft rules for how a cut lands, grounded in their own clips | `shorts-editor`, `script-writer`, `cut-review`, `content`, `content-waterfall` |
| `shorts-formats.md` | round 6 | the vertical safe frame, caption floors and look, crops, their format family | `shorts-editor`, `cut-review`, `content`, `content-waterfall` |
| `editing-rules.md` | round 6 | the durable cuts: starting defaults, their "every edit" rules, contextual taste, how they like to be worked with | `long-form-editor`, `shorts-editor`, `cut-review`, `content` |
| `editing-checklist.md` | round 6, grown on every fault | the mechanical pass, one line per thing that has gone wrong once | `cut-review`, `long-form-editor`, `shorts-editor` |
| `story-animations.md` | round 7, before the first animation | animations that teach the sentence, never mood footage; which tool for which job | `media-gen`, `long-form-editor`, `shorts-editor`, `content`, `on-camera-board` |
| `podcast-hosting.md` | round 7, before the first guest | the run sheet: intro, frame, anatomy, cut test, guest mode | `content`, `script-writer`, `long-form-editor` |
| `comments-and-pinned-comment.md` | round 7, before the first launch | the comment ask, the pinned comment, the closing line | `script-writer`, `content`, `content-waterfall`, `post-writer` |
| `interview/protocol.md` | round 7, walked once | the brief interview method: layer order and 9 principles | `content`, `script-writer` |
| `interview/template.md` | copied per video | the blank each brief interview fills, at `content/videos/<slug>/interview.md` | `content`, `script-writer` |
| `lessons.md` | after a piece ships | what a finished piece taught, the taste metric, what only they can say | `content`, `content-waterfall`, `long-form-editor`, `script-writer` |
| `cut-feedback/README.md` | written by `cut-review` at each review | the format for one verbatim file per review, and when a note becomes a rule | `cut-review`, `long-form-editor`, `shorts-editor`, `taste-builder` |

Files a session may add as the folder grows, and only these shapes: `packaging/<slug>.md` (one creator teardown), `packaging/thumbs/` and `packaging/frames/` (images for teardowns), `interview/example-<slug>.md` (one of their own real interviews), `cut-feedback/YYYY-MM-DD-<slug>.md` (one review).

## The minimum to call a file started

| File | Started when it has |
|---|---|
| `voice.md` | 3 quoted sentences of theirs in the register, and the Mechanics filled |
| `hooks.md` | 3 entries with their words quoted, and a rule they corrected (`scripts/first_taste_check.py` passes) |
| `packaging.md` | all 4 questions answered in their words |
| `thumbnails.md` | the starting defaults walked, and "Mine" partly filled |
| `formats.md` | at least 3 "I will never" lines with reasons |
| `script-format.md` | the read-or-improvise answer and the shape |
| `must-dos.md` | every section walked, rules and guidelines marked |
| `stories.md` | the anonymity rule and 1 story with its numbers marked SOURCED or UNSOURCED |
| `bio.md` | a current version with every fact in the ledger |
| `editing-checklist.md` | 5 real lines, each from a real failure |
| everything else | the starting defaults walked, or the first real entry |

## The entry shape, in every file

```markdown
## The rule, stated in one line

YYYY-MM-DD. What happened, in 2 sentences. Rule or guideline. Scope, if it was given for one piece.

> "Their words, verbatim, whole."
```

A correction that lands in a file is also one line in the work log, naming the file:

```
- YYYY-MM-DD HH:MM · <who> · taste/decision · <the rule, in one line> → content/taste/<file>.md
```
