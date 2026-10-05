---
name: script-writer
description: >-
  Write and refine video scripts in the creator's own voice, built out of an interview instead
  of a blank page. 3 modes: brainstorm (a topic becomes ranked angles), new (an interview
  becomes a recording-ready draft with the analogy pass and the transitions pass), review (an
  existing script or a recording transcript gets pulled apart beat by beat). Use for - "write
  the script for this video", "what should this video be", "here is the brief, script it",
  "review my script", "the hook is weak", "give me transitions between these sections", "read
  the deck against the script". NOT for written posts (that is post-writer). NOT for cutting
  footage. NOT for packaging: titles and thumbnails belong to the content door.
---

# Script writer

**Load before any step, in this order:**

1. `content/PRINCIPLES.md`, the constitution. When it conflicts with anything in this file, it
   wins.
2. `content/taste/script-format.md`, the shape the creator records from. **It is the single
   home of the format.** This skill conforms to it and never restates it where the two differ.
3. `content/taste/voice.md`, `content/taste/hooks.md`, `content/taste/stories.md` and
   `content/taste/clip-bar.md`: how they talk, what an opening that stops them looks like, the
   real stories and numbers a script may reach for, and the quality bar a moment has to clear.
4. `content/frameworks/youtube-pillar.md`, the structural rules for a flagship video.
5. The video's brief at `content/briefs/<date>-<slug>.md`, when one exists.

If a taste file is missing or thin, say so before writing anything and offer to run the
`taste-builder` skill first. A script written against an empty voice file is a competent
stranger's script.

The creator records from this page. Everything here serves one outcome: they sit down, glance
at the script, and talk like themselves for 12 minutes without reading a word aloud.

## The one rule

**Do not write a script before the interview has happened.**

Either the interview happened in this conversation, or its output is already written down in
the video's brief. If neither is true, interview first (`content/taste/interview/protocol.md`
holds the method: layer order is law, never lock a layer before the one above it), and say that
is what you are doing.

Writing the script first and asking them to react to it is the exact failure this skill exists
to prevent. A draft they react to gets edits. A conversation gets their framings, their
analogies and the order they actually think in, and that is the whole asset. It never comes out
of a reaction pass, because reacting and explaining are different mental acts.

Skip the interview only when:

- they say "just draft it" or "no questions", or
- you are re-running a script they already shaped, or
- they gave a delivery instruction with a deadline and a named use ("ready for me to record
  tomorrow"). That authorises every artifact the use needs. Name them back in one line so they
  can subtract ("recording tomorrow needs the script, the board and a thumbnail pick, building
  all 3"), and never park one behind a confirmation they have to come back for. The interview
  posture protects their shaping, not their typing.

Write which one applied at the top of the draft.

Then, once the interview is on record, **draft the whole thing**. Do not hand back an outline
and ask permission to keep going. A full v1 that you have already run your own litmus against
is the deliverable, and that is what they react to.

---

## What loads first, and why

Taste is data. This skill is an engine.

| File | What it holds |
|---|---|
| `content/taste/voice.md` | How they talk. Sentence length, the words they use, the words they never use, their signature phrases, the line they close on |
| `content/taste/hooks.md` | What an opening that worked on them looks like, and the shapes they have killed |
| `content/taste/stories.md` | The real stories, the real numbers, the moments a script can reach for |
| `content/taste/script-format.md` | The page they record from |
| `content/taste/clip-bar.md` | What a moment has to do to be worth a short later |
| The video's brief | The record of the interview for this one video |

**This skill states no voice of its own.** It carries no list of anybody's phrases, and it never
invents one. Where it needs to know how the creator sounds, it reads their file. A writing
skill that ships someone else's voice baked in makes every video sound like that person.

**Every claim gets checked before it goes in.** A number, a statistic, a result, a quote: if it
cannot be traced to `content/taste/stories.md` or to a source you can name, flag it and ask.
Never smooth over a figure nobody can source. The sourcing itself lives in the brief, never in
the bullets they read on camera.

---

## Modes

| Command | Input | Output |
|---|---|---|
| `brainstorm [topic]` | A topic, or nothing | 3 to 5 ranked angles, one line of pitch each, and why now |
| `new [topic]` | A brief, or an interview run here | A recording-ready script: written hook, guide bullets, verbatim key lines, transitions, visual cues |
| `review` | An existing script or a recording transcript | Named fixes, rewritten transitions, and the deck-against-script diff |

---

## Brainstorm mode

1. **Start from their own seeds.** Read `content/seeds.md` first. Their ideas always rank above
   anything you find, and a seed sitting untouched for 2 weeks is worth naming.

2. **Mine what they already said.** Their own recordings, calls, community posts, the questions
   they get asked repeatedly. The strongest video idea is usually a sentence they have said out
   loud 10 times without noticing. A question that came up on a sales or client call is the
   best signal there is.

3. **Check what they already published, on the live channel.** Never a status file. Find the
   angle that is not covered. Never propose a re-do of a video that exists; propose the
   companion.

4. **Check the graveyard.** `content/graveyard.md` holds what was deliberately killed. Never
   bring a dead idea back without saying it is on that list.

5. **Find the gap.** Look at the 3 or 4 channels covering this topic well. What does everybody
   say, and where is the thing nobody will say?

6. **Borrow a format.** Search for the best-performing FORMAT in a completely different corner
   of the platform that would carry this topic. Tier lists, "I tried X for 30 days", cheap
   versus expensive, brackets, power rankings, "if I started over". The principle: **the format
   gets the click, their expertise keeps the viewer watching.** Thin supply plus proven demand
   is the opportunity, so check whether anybody in their space has used the format yet.

   2 tests before recommending one:
   - **The 3-audience test.** Can an existing subscriber, somebody who has seen one video,
     and somebody who has never heard of them all click this and enjoy it?
   - **The language test.** The format is borrowed, the language is theirs. Never copy the tone
     of the creator you took the format from. Adapt the structure, fill it with their real data
     and their real stories.

7. **Output 3 to 5 ranked ideas.** Per idea: the one-line pitch, who it is for, why now, which
   of their stories it uses, and the recommended format. They pick, then the content door runs
   the brief interview, then `new`.

---

## New script mode

### The brief is the input

The brief is the record of the interview: the promise, the spine in their order and their names
for the sections, what to leave out, the lines they want verbatim, where the call to action
goes, and the analogies they reached for. The quotes and analogies recorded there **are** the
script's voice. Quote them directly. Never paraphrase the spine, and never reorder it to suit
a framework.

When the brief carries both their name for a section and a working name, their name goes on
camera.

No brief and no interview means you stop and interview. `references/brief.md` holds both
shapes: the research brief written before the interview, and the interview record it becomes.

**An `OPEN:` line in the brief stays open.** Do not fill a question they have not answered with
a good guess. Carry it into the script as a visible question and ask.

### Step 1. Research

Read the brief, then go one layer deeper for each section:

- At least 1 real story of their own, from `content/taste/stories.md` or the interview
- At least 1 real number with a source
- At least 1 visual idea (a board frame, a screen, a thing they hold up)

Present the combined structure back in a few lines before drafting, so they can move a section
before you write 2,000 words around it.

**A story is picked for the viewer's situation, never for its drama.** Ask first: would the
person this video is for see themselves in this? The most dramatic moment in the creator's life
is usually the least useful one, because the viewer is unlikely to ever be in it.

### Step 2. Structure

A default skeleton. `content/frameworks/youtube-pillar.md` and the brief both outrank it.

```
HOOK (15 to 30 sec)
  The promise in 1 sentence. Specific outcome, specific number.
  1 line of why they are the person saying it, concrete.

ROADMAP (30 to 60 sec)
  Name the sections out loud. "The order is intentional."

FILTER (20 to 30 sec)
  Who this is not for, then who it is for. Then launch.

SECTIONS (the body)
  Each one runs the teaching cycle below.

RECAP (60 to 90 sec)
  Bring it back together. The map, in one view.

CALL TO ACTION (60 to 90 sec)
  Earned by everything above it, never pushed.

CLOSE (15 to 30 sec)
  Their own closer, from their voice file.
```

**The teaching cycle**, repeated 2 to 4 times inside each section:

1. **Concept.** 1 or 2 sentences, plain.
2. **Why it matters.** 2 or 3 sentences of real-world logic.
3. **A real story.** 30 to 60 seconds. Context, what happened, the result, and the link back.
   Name the person when they have agreed to be named. Otherwise describe them by shape, with
   real detail ("a 12-person agency that answered its inbox 4 hours a day"). "One of my
   clients" with no detail is not a story, it is a placeholder, and viewers hear it as one.
4. **The takeaway.** 1 crisp sentence.
5. **A forward reference** where it applies. "We will get to that in a minute." Then actually
   get to it.

**Where the call to action sits.** The brief's recorded placement wins, always. When the brief
has none, ask; the fallback default is soft at roughly 30% ("I will leave a link below"), soft
again at 50% after a story lands, the real one at 80% once the value has been given, and the
outro. A framework percentage never overrides what they said.

**No date in a spoken call to action.** A live date ("the session on the 14th") said on camera
turns the video into an expired ad the day after that date. Point at the place the current
date lives instead (the description, a pinned comment, a page), and keep the date there.

### Step 3. The shape they record from

`content/taste/script-format.md` is the authority. In short, and only as a reminder:

1. **The hook, written out in full.** Word for word, because the first 30 seconds are rehearsed
   rather than improvised. Alternates get written out in full too.
2. **Every section after that: a heading plus small bullets.** Each bullet is a beat to hit, not
   a sentence to say. Their phrasing happens on camera. The bullets keep them on the spine.
3. **Key lines they want verbatim: written out in full inside their section, visually distinct
   from the guide bullets.** A bold line, not a bullet, so the eye can tell at a glance what is
   a prompt and what is a line. Key lines are co-created with them in the interview and stay in
   their words. The machine never plants one.
4. **A suggested transition at every section boundary**, offered and never imposed. They use it
   or ignore it.
5. **Analogies placed in the section they serve**, taken from the interview.

**Bullets say what to say next, not what to know.** At most 2 lines of context in italics at the
top of a section, and only where they genuinely need the context. Then bullets that are the
things to say, in the order they get said. Sourcing, rulings and machine notes belong in the
brief. A script with the provenance inside the bullets cannot be read as a script.

What not to do: a full word-by-word body (they will not read it, and it kills the delivery), or
a bare outline with no written hook (the hook is the one part that must not be improvised).

Section headings carry the timing and the visual in one line, separated by a middle dot:

```
## 0:30 · The chart (45s) · Scroll to the chart
- One bullet per beat. Short. Compressed.
- Not a sentence to read aloud. The bullet anchors them and they expand live.
```

### Step 4. The analogy pass

For every piece of the spine, ask: **"What's the analogy that makes this click?"**

A good one moves from something the viewer already lives with to the thing being taught, so they
feel smart instead of lost. Household objects, a job everybody has had, something physical they
can picture. If the creator gave you one in the interview, use theirs word for word. If a spine
piece has none, ask for one before drafting that section rather than inventing a metaphor they
would never say.

### Step 5. The transitions pass

Go across the joints, one at a time, and ask: **"What makes someone need piece 2 after piece 1?"**

That question has a one-sentence answer, which is why this pass takes 2 minutes and not 10. Run
it across every boundary, then write each answer into the script as the offered transition.

A transition that reads "now let's move on to the next topic" has failed. The shape that works:

```
[what we just covered] + [why it forces the next thing] + [the move forward]
```

### Step 6. The visuals, and what derives from what

Inline cues, used sparingly:

```
[BOARD: what is on the board at this moment]
[SCREEN: what they show on screen]
[B-ROLL: what runs underneath]
[EDITOR: a note to whoever cuts this, written the way they talk to that person]
```

Prefer putting the visual intent in the section heading over scattering cues through the body.
Avoid minute-by-minute prescriptions like "expand card X at moment Y"; describe the intent and
let the editor work.

**Who builds the surface.** The `on-camera-board` skill owns everything they present from while
filming. The `design-dna` skill owns pages that are sent or read, never filmed (a send
artifact, a prep doc). Hand either one the approved script, never a draft.

**The surface derives from the approved script, never the other way round.** A deck written
first becomes the thing the script has to obey, and then the video serves the slides instead of
the viewer. It also gets thrown away: every visual built before the content was stable had to be
rebuilt once the script moved.

**When a deck and a script both exist for the same recording, read them against each other and
report the diff.** Check all of it:

- Section order, and whether the deck uses their section names
- The numbering (a deck that says "3 moves" against a script with 4 is caught here, not on camera)
- Every number said aloud against every number on screen

Report the differences as a short list and let them settle which side is right.

### Step 7. Promises made on camera

List, at the bottom of the script and in the brief's post-record notes, every promise the script
makes out loud: "link below", "a free template", "the prompt is in the description", "no email
needed". Each one is a URL that has to be live in the description before the video publishes.
A promise with no link reads as clickbait to exactly the viewer who was about to trust them.

### Step 8. Self-review, then hand it over

Run the litmus below and `python3 scripts/copy_check.py <script-file>` before you show them
anything. A draft that fails your own checks and gets handed over anyway spends their attention
on work you could have done.

Hand over one version. If you rewrite it later, show the new one once, in full, say in one line
what changed, and say plainly that the earlier version is dead. 2 versions standing in one
conversation means they will read the wrong one.

### Step 9. After it is approved

Only once they have approved the script:

1. **The description.** A hook paragraph, the chapters, every link the video promised (step 7),
   keywords.
2. **Tags.** 10 to 15.
3. **A community post**, if they run a community, with one discussion prompt.

Titles, thumbnails and written posts belong to the content door and `post-writer`. This skill
does not generate them.

If they keep scripts in a task tool or a doc system, put the approved script there as well, in
the same shape: headings for sections with the visual cue inline, bullets for talking points,
one quote block for the hook. The repo copy stays the source of truth.

---

## Review mode

**Fix the beat, not the script.** A revision request touches only the named beat. If the hook is
weak, fix the hook. Never regenerate 2,000 words hoping everything improves, because the parts
that were working get quietly replaced.

**Hook shapes are read backwards only.** Given what they actually have (a result, an opinion, a
mistake, a story), name which hook shape that material honestly supports. Never run the
taxonomy forwards as a generator, or you get a hook the video cannot pay off.

### The adversarial pass

1. **Read the whole thing first.** Never suggest a change to a section you have not read.
2. **Attack it.** Does this contradict what the video is trying to do? Where would a sharp
   viewer stop believing it?
3. **The machine-voice check.** Read each section. Does it sound like them or like a language
   model? Flag every sentence that fails and rewrite the flagged ones from their voice file.
4. **Proof density.** Every section needs at least 1 real number or 1 real story. Flag the
   sections with neither.
5. **Forward references.** Every "we will get to that" has to actually arrive. Track them all.
6. **Pacing.** No section past about 15 minutes. Suggest the split.
7. **Energy map.** Name where it dips, and what goes there: a question, a story, a visual break.
8. **Say it and move on.** Flag anywhere the same point is made more than twice.
9. **Format check.** If the video borrowed a format, is the adaptation honest? Tier lists need
   reveals, brackets need upsets, challenges need stakes. Do not fight the format.
10. **Promises.** Every on-camera promise listed, per step 7.

### The transitions pass

Run step 5 again on the existing script. Rewrite every joint that reads abrupt or automatic.

### The deck pass

Run the step 6 diff. Report it. Change nothing on either side without them.

---

## The litmus test

Before delivering any script:

1. Would they say "move on" to any section? Cut it.
2. Any section with zero real stories and zero numbers? Fix it.
3. Does any sentence sound like it came out of a chatbot? Rewrite it from their voice file.
4. Em dashes anywhere? Remove them. Commas, periods, or parentheses.
   `scripts/copy_check.py` catches them mechanically.
5. Is the call to action earned, or bolted on? If bolted on, more value goes in front of it.
   Does it sit where the brief said?
6. Is the hook written out in full, and is everything else bullets?
7. Does every section boundary carry an offered transition?
8. Is every number traceable, and every on-camera promise backed by a link?
9. Would somebody watching this on their phone at 2am feel like the creator is talking directly
   to them? That is the bar.

---

## Retro, every real run

After they react to a script, note what they kept and what they rewrote. A one-off gets noted. A
pattern that shows up twice becomes a rule, written into their voice file, into
`content/taste/script-format.md`, or into `references/learnings.md` here, in the same session,
along with what it cost to learn. Say which file it went in.

Then ask them why they changed it. The answer is worth more than the edit, and it is the only
thing that stops the same correction arriving a third time.

**A content run ends when the video has shipped, not when the script is approved.** The
end-of-run review is done by a separate reviewer agent reading the whole conversation, never by
the session reviewing itself. The content skill holds that mechanism.

---

## References

- `references/brief.md` - the research brief written before the interview, and the interview
  record a script serves
- `references/learnings.md` - what past scripts taught, kept as rules with the reason attached
