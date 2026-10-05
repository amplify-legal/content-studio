---
name: design-dna
description: >-
  The design system for every HTML surface this pack produces, held as a measured record plus a
  compiled payload rather than as a style guide nobody reads. Use for - building a prep doc, a
  report, a send artifact, a review board, a one-page dashboard or a screen-capture frame; "make
  this look right", "does this match the brand", "build the page", "what font do we use", "check
  this page before it ships"; measuring a design you like into reusable rules; authoring new
  directions when a surface has no DNA yet; putting design options in front of the creator; or
  any moment a page is about to be built and nobody has said what it should look like. NOT for
  the board presented from on camera (that is on-camera-board). NOT for generating images or
  video (that is media-gen).
---

# Design DNA

**Load before any step:** `content/PRINCIPLES.md` (the constitution: it wins over every step here), then `content/brand.md` (the brand values: colours, fonts, voice of the surface). This skill is the engine and never restates the brand. Wherever this file says `{BRAND_ACCENT}`, `{BRAND_FONT_DISPLAY}` and so on, the value lives in `content/brand.md`.

Two ideas do the work.

**Compile, do not paste.** One document cannot serve both a person and a model. So every surface keeps two:

| | `dna.json` | `PROMPT.md` |
|---|---|---|
| Read by | people, and `dna_check.py` | the model, and only the model |
| Size | unbounded | tight, judged on quality, no byte cap |
| Holds | every measured value with the pixel beside the ratio, the tests, the rebuild log | register, ratios, the weird move, the bans |

**Measure, do not describe.** "Clean and modern" produces a different page every time it is read. "The headline is 96px" is nearly useless. "The headline is 2.95x the body" is the style, because a look lives in the gaps between things rather than in any one thing. 2 sessions reading a measured DNA produce the same page.

---

## The data

Everything lives in `content/brand/dna/`, beside the brand sheet:

```
content/brand.md                  the human brand sheet: palette, fonts, voice ({BRAND_*} values)
content/brand/dna/core.json       what every surface inherits: locked rules, palette with each
                                  colour's ROLE, the font families
content/brand/dna/RULINGS.md      the creator's design judgments, newest first. READ THIS FIRST.
content/brand/dna/<surface>/      dna.json (record) + PROMPT.md (payload)
content/brand/dna/_versions/      the authoring lane: generators, renders, the option board
```

A surface may override the scale, the colour shares and the layouts. **A surface never overrides `core.locked`.**

Keep a small state table at the top of `RULINGS.md`: each surface, and whether it is **measured and passing** or **authored, not measured**. **Never cite a scale or a score for a surface that is not measured.** Say it is unmeasured and use the nearest measured one, naming the borrow.

---

## The four jobs

### 1. BUILD a page

On a fresh install none of these files exist yet: start at job 2, measure a page you like, and run `scripts/dna_check.py --example` to see the check working.

1. Read `RULINGS.md`, then `core.json`, then the surface's `PROMPT.md`. Do **not** read `dna.json` to build; it is the record.
2. Build. If generating with code, take fonts and guarded copy from one tokens module so they come from one place.
3. `python3 .claude/skills/design-dna/scripts/dna_check.py content/brand/dna/<surface> <page.html>`
4. Render it and **look at it** before handing it over, at 1728x1080, 1920x1080 and phone width.

### 2. MEASURE an existing design into DNA

Only ever measure something that **shipped and that the creator liked**. Full method in `references/method.md`. In short: render it, count pixels for colour share, parse the source for sizes, convert every size to a ratio of the body size (keeping the pixel beside it), name the one weird move, write down the refusals and the deliberate absences, write tests a bad copy would fail, then compile the payload.

```bash
python3 .claude/skills/design-dna/scripts/dna_check.py --example > content/brand/dna/<surface>/dna.json
# edit every number to what you measured, then run it against the ORIGINAL:
python3 .claude/skills/design-dna/scripts/dna_check.py content/brand/dna/<surface> <the-original.html>
```

**Anything that fails on the original is a broken test, not a broken page.** Fix the number in `dna.json`, never the page. Then prove the battery discriminates: a deliberately slopped copy must fail at least one check. `dna_check.py --selftest` shows the shape of that proof on 2 built-in pages.

### 3. AUTHOR directions

**Measuring produces a record, not a design.** A surface is not finished until at least 2 directions exist that differ on a *real* axis: colour share, type character, whether cards exist at all, where the weird move lives, density. 2 versions of the same layout with a different accent colour is one direction shown twice.

Build them with the same content, render them, hand over the images. The creator reacts in prose and the DNA is assembled from what they say.

### 4. CHECK a page

`dna_check.py` has a source half (always runs, standard library only) and a pixel half (runs when the spec has a `pixels` block, needs Pillow plus Chrome or Chromium; set `CHROME=/path` if it is not found). Source checks: type floor, type tiers, shadows, required signatures and CSS, bans (em dashes, dark mode, gradients, emoji), counted phrases, and the full-screen layout rule. Pixel checks: ground share, colour-family shares per declared register (`<meta name="dna-register" content="...">`), and connected-region counts. A missing renderer is reported as **SKIP**, never as a pass.

**When the battery fails on a page you know is right, the test is wrong.** That is what the first run against the original is for.

---

## How the creator is asked, and how they are not

**Show the move, never name it.** A board of 50 described design moves with checkboxes failed: the person could not tell what each sentence meant or what they were opting into. A design decision has to be **visible in the artifact they are looking at**. Hand over **rendered images**, not HTML files or descriptions, with at most a handful of plain-English questions at the end. Their prose reaction is the input; this skill does the translation.

**The option rules.** Every one was bought with a wrong pick:

- **Every option carries a visible label, and the label is identical everywhere it appears**: in the rendered image itself, in the file name, in the chat sentence and on the board. Send the files in label order, because a person counts files in the order they arrive, not the headings on a board. Never renumber between rounds; a new round continues the sequence or starts new names.
- **1 letter names 1 thing on a page, never 2.** If titles are A to E, photos are F to H. When the same letter serves 2 option sets, "option C" means nothing.
- **Options go side by side in 1 view**, adjacent on one row, never in sequential sections a screen apart. Send a comparison image in chat as well as the board.
- **2 options that render the same are 1 option.** Measure the options against each other before the board goes. Colour washes 1 to 3 values apart out of 255 are invisible; one settled threshold was a mean difference of 5 to 6 and a max of about 34. If they differ only slightly, they must sit adjacent.
- **A question never points at a text it does not show.** A choice between paragraphs, variants or clauses quotes each one word for word next to its option.
- **A label lets the creator point at something they can see.** It is never a handle for you to point at something they cannot (a bare number for a decision, or "the card above").

---

## Standing rules that govern every build

Full text belongs in `core.json`; these are the ones most easily lost.

**One mode, chosen deliberately.** Light mode is the default for these surfaces. Pick it and commit: no half-supported `prefers-color-scheme` block. A page that half-supports both looks broken in one of them.

**Full screen, adaptive size.** No fixed `max-width` column floating in the middle of a wide screen. The layout spans the viewport with a fluid side gutter, `padding-inline: clamp(16px, 4vw, 64px)`. Grids reflow with `repeat(auto-fit, minmax(...))`, never a fixed column count. Type may scale with `clamp()` above the floor. A fixed-size canvas (a 1920x1080 deck, a thumbnail) scales uniformly to fill the window and never lets its container squeeze it: the container carries `flex: none` and the canvas its minimum size. Check at 1728x1080, 1920x1080 and phone width before it ships.

**Type floors.** 18px in components, 16px anywhere. Each surface also declares its floor as a ratio of its body size plus an absolute backstop in its `dna.json`, because a bare pixel floor inherited from another surface fails pages that are proportionally fine. When inheriting CSS from somewhere else, scale sizes up to meet the floor; never copy a small size forward.

**Type families.** `{BRAND_FONT_DISPLAY}` headlines, `{BRAND_FONT_BODY}` body, `{BRAND_FONT_LABEL}` uppercase labels, as set in `content/brand.md`. If the display face ships 1 weight, never set `font-weight` above 400 on a display element: you get a synthetic bold. Hierarchy comes from size and colour.

**Colour.** `{BRAND_ACCENT}`, `{BRAND_INK}`, `{BRAND_GROUND}` and the rest come from `content/brand.md`, each with its role. More colour and more boxes than feels safe: the common failure is a page so restrained it reads as a draft. A measured share describes a page that was approved, not a ceiling.

**Short, and shaped as process.** Action steps with an owner on each. Tables for state.

**Copy rules apply to pages.** No em dashes, numerals as digits, and every guarded claim in `content/reference/the-checks.md`. A page is copy with a layout attached: run `python3 scripts/copy_check.py <page.html>`. **Guard the rules that keep getting lost in code, not in memory**: an em dash ban that lived only in a document came back on all 10 freshly authored directions the next day.

**Every link resolves, and everything named is a link.** Verify every link and path before the page ships. Every page, doc, video or person a page names is a clickable link on its name; a thing that cannot be found says so instead.

**A page with video on it is served, never opened as a file.** `python3 scripts/serve_outputs.py` answers the Range requests a browser's video player needs; a `file://` page shows empty players.

---

## 2 rules about what appears on a published page

**A source line is a receipt the reader can check, never your own file path.** Every formal claim carries where it came from, where the reader sees it: the vendor, the study, "measured from our own engagements". Internal paths and meeting ids stay in prep docs and out of anything an audience reads. **Read the HTML comments too**: a build comment naming internal paths is one right-click from every reader.

**Notes to the presenter never appear on the surface the audience sees.** "Say this out loud", "pause here". Those live in the prep doc.

---

## Traps

All found live, all cost real time. Details in `references/traps.md`.

- **Headless Chrome needs an absolute `file://` path.** A relative one renders Chrome's error page, which then gets trimmed and saved looking like a successful render.
- **Render width must match the composition width.** A 1920px frame rendered at 940 comes back clipped and reads as a design fault.
- **`font-size` inside a `[style*="..."]` attribute selector is a media-query override, not an element.** Counting occurrences in text counts those too.
- **Pixel colour-share counting cannot see gradients or anything small.** The explicit gradient ban and a source read catch what pixels miss.
- **A check that greps source for a literal punishes indirection.** Resolve what the browser resolves.
- **Never write a rebuild log before running the rebuild.** A record of a test that did not run is worse than no record.

---

## The clean-room rebuild (step 6 of the method)

A fresh sub-agent is handed only `core.json`, the surface's `PROMPT.md` and the page's words as plain text, with every workspace path scrubbed, and told that reading anything else invalidates the test. It builds the page and writes `GAPS.md`: every place the payload left it guessing, what it chose, and its confidence. **That list is the finding; the page is secondary.**

1. Extract the copy as plain text in reading order.
2. Copy `core.json` and `PROMPT.md` into a scratch directory; scrub every path.
3. Launch the agent; tell it which register to build and to declare it in the page head. **Check the brief against the payload first**: a brief can ask for a register the payload says is not buildable.
4. Run the battery on the rebuild; render both at the same width; diff by eye.
5. Classify every difference: forgotten rule, payload error, test fault, deliberate divergence, builder judgment. Fix the first 3. Go again.

A session that has read the original cannot honestly perform this. Never claim it ran when it did not.

---

## When the creator corrects a page

The correction goes into `RULINGS.md` and the surface's payload in the same session, as a number where it can be a number, and you say which file it went in. A design ruling that lives only in the conversation gets re-broken on the next page, which is the failure this whole skill is shaped to prevent.
