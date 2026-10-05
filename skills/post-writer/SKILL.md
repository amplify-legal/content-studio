---
name: post-writer
description: >-
  Short-form written posts in the creator's own voice, from their own material. 4 modes:
  draft (an idea becomes a post), refine (a rough draft becomes a finished one), shape (raw
  notes or a voice dump become a structured post), hook (one topic becomes 7 alternative
  openers to choose between). Use for - "write a post about", "turn this into a post", "clean
  up this draft", "give me some hooks for", "shape these notes", a voice note about an idea, a
  caption for a video going out on several platforms, or a recording's written derivatives.
  Reads their voice file and never carries a voice of its own. NOT for video scripts (that is
  script-writer). NOT for outreach messages to named people.
---

# Post Writer

**Load before any step, in this order:**

1. `content/PRINCIPLES.md`, the constitution. When it conflicts with anything here, it wins.
2. `content/taste/voice.md` and `content/taste/hooks.md`: how they write, and the openers that
   stopped them versus the ones they killed.
3. `content/taste/stories.md`: the only place a number or a story may come from.
4. `content/frameworks/post-frameworks.md`: the post shapes they run each week.
5. `references/examples.md` in this skill, once they have filled it with their own posts: load
   5 to 7 of the starred ones as cadence references per draft.
6. `references/platform-craft.md` when the post is for a specific feed.

**This skill states no voice of its own.** It ships no house style and no opinion about how a
post should sound. Where it needs to know how the creator writes, it reads their file. A writing
skill with somebody's voice baked in makes every post sound like that person, and the person it
sounds like is not the one whose name is on it.

If `voice.md` does not exist or is thin, say so before writing anything and offer to run the
`taste-builder` skill first. A post written against an empty voice file is a competent
stranger's post.

---

## The iron rules

These hold in every mode.

- **Never draft from a video script.** A post is mined from what they actually said (a
  recording, a call, a voice note, a seed), not from the script they planned to say. The script
  is the machine's scaffolding; the tape is their language.
- **Extract their story first.** The post exists to carry one real moment of theirs. Find it
  before you write a word.
- **Never invent anything.** No moment, name, date, number or quote they did not give you. If a
  draft needs one, ask, or leave it out. Manufactured vulnerability is the first failure mode of
  a writing skill.
- **No engagement bait.** No "comment WORD below", no "agree?", no "tag someone".
- **Their dictated words go out as given.** When they dictate the wording, fix typos,
  capitalisation and product names, and change nothing else. A word that looks worth cutting
  or softening is asked about before it ships, never reported after. A posted message cannot
  be taken back.
- **Nothing publishes from here.** This skill writes drafts. Posting is the
  `content-waterfall` skill's publishing step, and it needs their explicit approval.

---

## The 4 modes

Say which one is running, in one line, before it runs.

| Command | Input | Output |
|---|---|---|
| `draft <topic>` | A topic or idea | One post plus a one-line "why this shape" |
| `refine` | Their rough draft | The edited post plus a short summary of what changed |
| `shape` | Raw notes, a voice memo, a dump | One structured post plus a one-line "why this shape" |
| `hook <topic>` | A topic | Exactly 7 numbered openers, each tagged with its opener type |

### draft: an idea becomes a post

1. **Media?** Ask: "Is there a photo or a video going with this? Give me one sentence on it, so
   the post earns the media instead of captioning it."
2. **Moment?** Ask: "What real moment, number, name or line anchors this? A specific day, a
   result you actually hit, something somebody said to you." Wait for the answer. If they have
   none, offer a version that does not lean on a personal moment, or decline. Never invent one.
3. **Who is it for, and what should they do afterwards?** One person, one change.
4. **Pick the shape from the material, not from a template.** Look at the topic and the moment
   and choose: a vulnerable opener, a scene, a named moment, encouragement, a contrarian
   opinion, a longer story with dialogue. `references/examples.md` shows how they handle each,
   as cadence, never as a fill-in template.
5. **Draft one version, not 3.** 3 versions asks them to do the editorial work while looking
   like generosity.
6. **Run the litmus below.** Return only a draft that passes.

### refine: a rough draft becomes a finished one

**Their draft is the source of truth for the argument.** Refining means their sentences,
tightened. It does not mean your sentences, arranged around their idea.

1. Run the mechanical checks and fix each failing sentence inline.
2. Score the voice checks (0 to 6).
3. Branch on the score:
   - **5 or 6, already strong:** surgical edits only. At most 3 changes, each touching at most
     one sentence. No reordering, nothing new added, every name, number, date and quote kept
     verbatim.
   - **4, partial:** revise only the failing items. A failed opener gets a new opener; a
     declared lesson gets stripped. Passing parts stay untouched. One line per change.
   - **3 or below, far from their voice:** stop and ask: "Before I rewrite this, is the message
     you want to land: [one sentence]?" Rewrite only after they confirm, keeping every specific
     they supplied.

Show what changed and why, briefly. A refine that comes back as a clean block with no summary
teaches them nothing, and they cannot tell whether their point survived.

### shape: raw notes become a post

A voice dump or a page of notes has the whole post in it, out of order, with the best line
buried 2 thirds down.

1. **Capture the raw material verbatim before shaping it**, in `content/seeds.md` or wherever
   they keep raw fragments. The shaped version is a derivative; the dump is the record, and it
   usually contains the next 2 posts as well.
2. Ask the media question from draft step 1.
3. Pull out the specifics: every number, name, date and quote in the notes.
4. Find the best line, put it first, and cut everything that was them thinking rather than them
   saying.
5. If the notes carry 2 stories or 2 pivots, ask which one leads. One idea per post.
6. Run the litmus.

### hook: one topic becomes 7 openers

7 openers, each a genuinely different angle, not 7 rewordings of one. Read `hooks.md` first:
the openers that stopped them are the shape to aim at, and the ones they killed are the shapes
to skip.

Tag each with its type, for example: vulnerable, scene, named moment, second person, contrarian,
permission to feel, a number. Each one must pass the mechanical checks and the anchored-opener
check on its own.

Present them plainly, numbered 1 to 7, and let them pick. Never rank them, and never mark one
as recommended.

---

## The litmus

### Mechanical (every one must pass)

| # | Check | Fails when | Fix |
|---|---|---|---|
| M1 | Em dashes | Any em dash or `--` in the copy | A period, a comma, or a restructured sentence |
| M2 | Banned phrases | Any phrase on the ban list below or in their `voice.md` | Rewrite the sentence in plain words |
| M3 | Sentence length | Any sentence longer than their `voice.md` allows (20 words if it says nothing) | Split it |
| M4 | Hashtags | Any, unless their `voice.md` or the platform's craft note says otherwise | Remove |
| M5 | Plural voice | "we", "our", "us" when they have not confirmed it is a team post | Singular, or ask |
| M6 | Looked-up comparisons | "X times the length of", "N books' worth", "the size of", "equivalent to" | Remove it. The raw number alone, or no number |

M6 exists because a person writing a post does not stop to work out how many novels a number
equals. That comparison only appears when a language model is reaching to sound impressive.
Numbers they gave you are fine. A comparison that needs a lookup or arithmetic is not.

**A starter ban list.** Generic phrases that mark a post as machine-written or as corporate.
Extend it in their `voice.md`; never shrink it there without them saying so.

- "thrilled to announce", "excited to share", "proud to share", "humbled"
- "game-changer", "revolutionize", "leverage", "synergy", "circle back"
- "thoughts?", "agree?", "drop a comment", "let's connect"
- "Real talk:", "Hot take:", "Here's the thing", "Unpopular opinion:", "Plot twist:",
  "The truth is:", "Let me explain:"
- "Here's what I learned:", "The lesson is:", "Takeaway:"

### Voice (score 1 per pass, 0 to 6)

| # | Check | Passes when |
|---|---|---|
| V1 | Their specifics | At least 1 number, name, date or quote that THEY supplied |
| V2 | Anchored opener | The first sentence is anchored in a time ("this morning"), a place, or a sensation |
| V3 | A pivot | A short line somewhere in lines 3 to 7 flips direction, adds conflict, or shifts tone |
| V4 | Earned lesson | The takeaway comes out of the story; nothing announces it |
| V5 | Their cadence | You can name which starred example in `references/examples.md` it most resembles, and no sentence reads like an essay |
| V6 | Inside, not outside | The first 3 lines put the reader inside the felt moment before any number appears; numbers are punctuation, never the spine |

V6 is the one that fails most. If the post can be reduced to a wall of stats and still hold
together, the spine is wrong. Tell the story of the moment, not the metrics around it.

### Thresholds

- **draft and shape:** all mechanical checks pass, and voice 5 or more. At 4, one revision pass
  and re-score. At 3 or below, decline and ask for more substance: a real moment, a number, a
  name. A failing V6 usually means the input had no felt experience in it, so ask for one.
- **refine:** all mechanical checks pass (fixed inline). The voice score picks the branch above.
- **hook:** each opener passes M1, M2, M3, M4, M6 and V2 on its own.

---

## Rules that hold across every mode

**Never label the post's own intent.** "No pitch here", "just sharing", "quick thought, not
selling anything". Naming what a message is not makes the reader look for the thing it denies.
`scripts/copy_check.py` catches this shape.

**A short message reads as typed, not written.** The failure is not jargon, it is craft: an
observation about the reader before the point, a closing clause doing extra work, a knowing
aside. Anything that would read well in an essay comes out of a short post.

The machine constructions that produce most of it, named so they can be caught:

- **The antithesis.** "It's not about X, it's about Y." Say the one thing and drop the contrast.
- **The connoisseur's rating.** "the clearest example I have ever heard of". Nobody rates things
  out loud this way.
- **The aphorism closer.** A final clause whose job is to sound wise. Cut it.
- **The essay verb.** A post "explores", "unpacks", "touches on". A post says things.
- **The purpose clause.** "so nothing gets lost", "so you have it handy". It explains why the
  message exists instead of saying the thing.
- **The abstract reference.** "the point you made", "the second one". Name the actual thing.
- **The setup sentence.** "Quick one.", "Two things." A standalone sentence carries content or
  goes.
- **Writerly imagery.** "the weight of the silence", "a quiet storm of thoughts". Would they say
  it out loud to a friend across a kitchen table? If not, write the plain version.

**No em dashes.** The loudest tell that a machine wrote the sentence.

**One idea per post.** A post carrying 2 ideas gets read as carrying none.

**Every number traces to `content/taste/stories.md`.** A figure that cannot be sourced gets
flagged, never smoothed over, never rounded into confidence.

**A half-finished edit is worse than either version.** If a sentence needs rewriting on the way
out, rewrite the whole sentence. A machine sentence with a hand edit driven through the middle
of it reads worse than either the original or a clean rewrite.

**Don't re-do a post that exists.** If the topic overlaps something they already posted, say so
and offer a companion angle or a continuation.

**Same video, a native caption per platform.** When one video goes to several feeds, the video
stays the same and each platform gets its own caption and hook, written to that feed's craft
note. Never paste one caption everywhere.

**2 people, one event, 2 different posts.** When 2 people (co-hosts, partners) both post about
the same thing, each post needs its own hook, its own structure, and at least one thing only
that person can say. The check is mechanical: 0 shared 5-word phrases between the 2 posts, run
against what actually went out on the first one, never against the draft, because people edit
on the way in. `references/platform-craft.md` has the detail.

**Length matches the energy.** Never pad to a target. `references/platform-craft.md` has the
bands per feed.

---

## Before it ships

```bash
python3 scripts/copy_check.py <draft-file>
```

Exit 1 means something in the banned table is in the copy. The advisory tier warns and never
fails the run; their ear beats the pattern every time, and a warning they overrule is worth a
line in `voice.md` saying so.

If you run a voice-check reviewer (a separate agent that reads drafts against the voice and
learnings files and quotes each offending sentence with a plain rewrite), run it on every draft
before the creator sees it, and apply its rewrites to fresh drafts only. A reviewer never
changes copy the creator already approved; it reports and asks.

Every link in the post carries `https://` on the front. Without it, whether the address becomes
clickable is up to the app, and on some feeds it will not.

---

## When they correct it

A struck line, a reworded opener, a "this doesn't sound like me": the reason goes into
`voice.md`, `hooks.md` or `references/learnings.md` **in the same session**, and you say which
file it went in. An approved post goes into `references/examples.md` with its number once it
has one; a rejected draft gets one line saying why.

Record the reason, not the diff. "Changed 'leverage' to 'use'" is a diff. "They do not use
business words for ordinary actions" is a rule, and it fixes the next 40 posts.

---

## References

- `references/platform-craft.md` - what is true because of how a specific feed works
- `references/examples.md` - the creator's own posts, annotated (a template until they fill it)
- `references/learnings.md` - what past posts taught, as rules with the reason attached
