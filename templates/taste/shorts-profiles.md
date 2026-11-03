> **`content/taste/shorts-profiles.md`** · written by you (or rebuilt from your review exports, then corrected by you) · read by `shorts-editor` (every shorts brief lists these as options), `cut-review`, `content`, and the example shorts pipeline (`examples/podcast-shorts-pipeline/`).

# Shorts taste profiles

> A taste profile is a named style of short that your own feedback keeps asking for. Designers pick from them and add creativity on top, so nothing starts from scratch and no single style is over-indexed.
>
> **The rules of the file:** a pattern needs **3 or more receipts** (a tick or note of yours on a review page, an editor's note, a reviewer's verdict, a ruling you gave) before it is a profile line; 1 or 2 receipts make a candidate. Every profile names when it fits and 2 examples with receipts. **A shorts brief lists 2 or more profiles as options, never one.** Rebuild the file after every review round. If you rebuild it with a script that mines your exports, the script rewrites the file, so keep a hand-kept section at the end and carry it over after every rebuild.
>
> The profiles below are **starting points** a working podcast-and-tutorial channel arrived at over 4 review rounds. Keep the ones your own receipts confirm, drop the rest, and replace every receipt line with yours.

## What was read

<Each rebuild: how many shorts carried your opinions, from which exports; how many reviewer files; how many rulings. A note with no tick counts as "fix, then keep" unless you say otherwise.>

## Profiles (styles to pick from: pick several, add your own creativity)

### Native look
- When it fits: a talking moment with no drawn mechanism: one or two people saying a strong line. Also the fallback whenever a card would sit still.
- What it does: looks edited in the platform's own app: full-bleed faces, a title sticker on top that names the topic, one caption line with the spoken word lit, a handmade feel rather than a branded template.
- Receipts: <your 3 or more>.
- Examples: <short id and the note, twice>.

### Card only while it moves
- When it fits: a moment with a real mechanism to draw (steps, a climb, a checklist) inside a longer talking stretch.
- What it does: the card is on screen only while it animates something with a purpose; between beats the short goes full screen on whoever is talking, then brings the card back to finish it. Scene changes get a real visual transition, never a jump.
- Receipts: <...>.

### Drawn mechanism (flat 2D)
- When it fits: the guest tells something that unfolds over time or climbs (days, steps of escalation).
- What it does: a flat 2D drawing that follows what is said, beat by beat (a timeline with a counter, a climb, a small scene), picked over a list when the sauce is a sequence or a mechanism rather than a list of names.
- Receipts: <...>.

### Guest banger, all guest
- When it fits: the guest has one quotable line that carries the whole story, and the host's question does not set it up.
- What it does: opens on the guest saying the line, the story develops, the line can return at the end; the host's question is dropped; clips may be reordered.
- Receipts: <...>.

### Screen is the subject (tutorials and long forms)
- When it fits: any short cut from a tutorial or long form where what is on screen is the lesson (a permission box, a prompt, a slide). The podcast style never goes on these.
- What it does: the real screen, zoomed until the words read at phone width, stays on frame while it is explained. The person's face spans the full width under it, head whole. One mark (an outline, a highlighter, a dim on the rest) lands on the word. Layout by moment: A screen hero (the standard to iterate from), B face on top with the screen strip under it, C the screen in its own band. Nothing on screen is sliced by the card or frame edge. No private UI: mask frame by frame.
- Built by: `examples/podcast-shorts-pipeline/tutorial_look.py` with `tutorial.html`, from a per-short sidecar.
- Receipts: <...>.

### Native between animations (`ig_between`)
- When it fits: one of the few shorts (about 2 in 10) whose tape has a moment that earns motion: a number that matters, a named sequence, many becoming one, a state change, a step in a tool.
- What it does: the native hook and headline open it. While nobody animates, the native look carries it (full-bleed face, blurred extension). When the animation plays, the title goes and the animation takes the full top. Light and dark twins render side by side.
- Built by: the pipeline's `ig_between: true` spec field, with `anim_looks.html` directions A, B and C.
- Receipts: <...>.

## Across every profile (3+ receipts; these hold whatever style is picked)

Starting points; confirm or strike each with your own receipts:
- **Faces fill the frame and use the space.** The face box spans the full width; chin, neck and collar inside; nobody a circle; nobody under about 300px.
- **The hook says the topic before the first word.**
- **Speech sped up 1.1x to 1.25x.**
- **Blur only on the bottom 15%, none with several people stacked.**
- **The name and credit right and readable; the credit beside a guest is their own firm.**
- **Keep the whole bit: the setup and the joke.**
- **The saved line lands early; trim the back half.**
- **The aha moment first, then the question, then the full answer; the guest's introduction at the end.**
- **Nothing on a face, ever.** The title is gone by about 28 s to make room above the head.
- **A caption over a light ground sits in a dark box, one box per line.**
- **The screen capture big, the words readable at phone width; the top band may serve the animation.**
- **Noise and echo cleaned on every short; no sharp peaks, and never dulled.**

## Mechanics, not taste (a pipeline rule, never a profile)

A pattern that only reviewers raise and you never did is usually a pipeline fault (a credit under the wrong face, a credit on for 1.5 s). It is fixed in the code, never written up as a style. Examples a working build hit: the credit showing while another person was on screen; no credit at all; captions on a chin; a sticker landing a second after its word.

## Candidates (1 or 2 receipts)

<Each with its count and receipts. Starting candidates worth testing: host and guest split or switching; show the thing itself; a key-word band over the speaker; pull to the full video with an attractive end card, never a 3 s marketing card; titles plain, never elaborate or obviously machine-written; a sticker or card lands on its own word and carries a purpose.>

## Over-index watch (flag a look or a format above 40%)

<Each rebuild: the share of each look and each format across the review set and across all specs. Above 40% is a flag. Count how many shorts no human touched (no tick, no note): untouched means transform under the rulings, never a keep or a pass.>

## Added by hand (what a miner does not read)

<Rulings and verdicts your rebuild script does not read yet (final-round reviewer verdicts, rulings given in chat). Carry this section over after every rebuild.>
