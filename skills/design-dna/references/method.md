# The method

8 steps. Step 6 is the one nobody does and the one that works.

Adapted from a public "Design DNA" method for posters. What we changed, and why, is at the bottom.

---

## 1. Find a design worth measuring

**Only measure something that shipped and that the creator liked.** A draft nobody approved
encodes a guess, and the guess then becomes law on every page built afterwards.

The page we measured first qualified on 3 counts: it shipped, the creator had shaped its most
important element himself, and it was the freshest thing he had signed off on.

## 2. Measure it. Do not describe it.

2 passes, both mechanical.

**Pixels, for colour share.** Render at the real width, trim the uniform tail off the bottom,
and count exact token colours over what is left. This is the only honest way to answer "how much
of this page is the accent colour", and the answer is usually nothing like the guess.

`dna_check.py` does the counting once a `pixels` block is in the spec (families of hexes, the
ground, registers with min and max shares, connected-region counts). Use it at the composition's
real width.

**Source, for sizes.** Parse every `font-size`, `border-radius`, `gap`, `line-height`,
`letter-spacing` and `max-width`. Count occurrences. Do not eyeball.

Map every size to the element that carries it. A ratio written without the pixel it came from is
a guess with a decimal point in it, and that failure mode is documented in `traps.md` because it
cost 2 rebuild runs.

## 3. Decide what actually carries the look

6 things carry a design. Most people write down the wrong ones.

| Thing | Why |
|---|---|
| **Ratios, not numbers** | "96px" is nearly useless. "2.95x the body, never under 2.5x" is the style. The look lives in the gap between 2 sizes, not in either size. |
| **How much, not just what** | The same 3 colours at 60/30/10 and at 90/8/2 are different designs. Write down the share of the page each one covers. |
| **The one weird move** | Nearly every design that works breaks its own system exactly once. It is the most important single element and the first thing a copy loses, because a copy copies the system and this is a break from it. |
| **The refusals** | Listing 6 colours tells the model it may use 6. Bans are rules. |
| **What is missing** | No nav, no testimonials, no pricing table, no second call to action. Absences are rules. |
| **Named layouts** | Unnamed layouts drift, and section 6 stops matching section 1. |

## 4. Write `dna.json`, the record

Unbounded. Every measured value with the pixel beside the ratio, the register (who reads this,
on what device, for how long), the named layouts, the weird move with **why it must survive**,
the refusals, the deliberate absences, the tests, and the rebuild log.

## 5. Write tests a bad copy would fail

Then **run them against the original first.** That is calibration, not validation.

**Anything that fails on the original is a broken test, not a broken page.** On the first real
run here the battery scored 8 out of 10 and both failures were test faults. One was counting
media-query attribute selectors as elements. The other had inherited a type floor from a
different surface, which turned out to be a genuine bug in the workspace's own standing rules
rather than anything wrong with the page.

Then prove the tests have teeth by running them against a deliberately slopped copy. A battery
that only ever passes is measuring nothing. Ours: 10 out of 10 on the original, 5 out of 10 on
the slop.

## 6. Rebuild the original from the rules alone

**The step that does the work.**

Regenerate the page from `PROMPT.md` only, in a context that has never seen the original.
Whatever comes out wrong is a rule you forgot. Add it. Go again.

The mechanism, so your next surface can use it:

1. Extract the copy as plain text in reading order.
2. Copy `core.json` and `PROMPT.md` into a scratch directory and scrub every path out of both.
3. Launch a fresh agent with only those files, tell it which register to build, tell it to
   declare that register in the page head, and tell it that reading anything else invalidates
   the test. **Check your brief against the payload before you launch.** One of our runs was
   told to build a register the payload said was not buildable, and neither instruction was
   wrong on its own.
4. Ask for `GAPS.md`: every place the payload left it guessing, what it chose, and its
   confidence. **That list is the finding; the page is secondary.**
5. Run the battery on the rebuild, render both at the same width, and diff by eye.
6. Classify every difference as one of: a forgotten rule, a payload error, a test fault, a
   deliberate divergence, or builder judgment. Fix the first 3. Go again.

A session that has read the source **cannot honestly perform this**. It needs a clean context
handed only the payload plus the copy. Never claim it ran when it did not, and never write the
rebuild log before the rebuild.

## 7. Compile `PROMPT.md`, the payload

Judged on quality, **not on a byte count**. Keep it tight because a rule buried mid-document
gets ignored, never because a number says so, and never cut a load-bearing rule to hit a size.

The original method's 2KB cap was set for posters, roughly 9 moves. A 6-layout long-form page
does not compress to it without losing rules. Ours lost the register, the mobile behaviour and
the measure values across 4 compression passes before we dropped the cap. Aim under about 4KB
and cut filler, not constraints.

## 8. Author directions

Not in the original method. Added because measuring alone kept producing better copies of last
month's page.

**Measuring produces a record, not a design.** Codifying what exists can only ever reproduce
what exists. So a surface is not finished until at least 2 directions have been authored that
differ on a **real axis**:

- colour share (starved vs structural)
- type character (serif body vs sans, one weight vs many)
- whether cards exist at all
- where the weird move lives
- density (newspaper vs one idea per card)

2 versions of the same layout with different accent colours is not 2 directions.

Build them with the same content inside one surface, so the comparison is design language and
nothing else. Render them. **Hand over images**, with a short list of plain-English questions at
the end. The creator reacts in prose, and the rules get assembled from what they say.

---

## What changed from the original method, and why

| Original | Ours | Why |
|---|---|---|
| 2KB hard cap on the payload | quality first, no cap | The cap fits a poster. A long-form page loses rules hitting it. |
| measure, codify, done | measure, codify, **author** | Codification alone reproduces. It never proposes. |
| tests as a checklist | tests as a runnable battery, calibrated against the original and then against slop | A test that never fails is measuring nothing. |
| one document | `dna.json` plus `PROMPT.md` | Kept unchanged, and it is the best idea in the method. |
| present the rules to the human | **show the move, never name it** | A board of 50 named moves with checkboxes failed. The creator could not tell what he was opting into. |
