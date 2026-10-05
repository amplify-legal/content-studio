# Traps

Every one of these was found live and cost real time. Ordered by how easily each one passes for
something else.

---

## The ones that look like a design fault but are not

**Headless Chrome needs an absolute `file://` path.** A relative one renders Chrome's own "this
site can't be reached" error page. The render pipeline then trims it and saves a PNG that looks
like a real output. Our first batch of renders came back as dark error screens and read, for a
moment, like a CSS bug. Resolve the directory with `cd && pwd` before you build the URL.

**Render width must match the composition width.** A 1920px screen-capture frame rendered at 940
comes back with every number cut in half, which reads exactly like a broken layout. Pass the real
width.

**A viewport shorter than the page silently clips it and overwrites a good PNG.** Hit while
testing the tooling itself: a quick render at 940 x 1200, run only to prove a moved script still
worked, destroyed all 7 finished renders and replaced 2,000px pages with 1,200px stumps. Nothing
errored. The tell is that the trimmer finds no uniform tail, because the page ran past the bottom
edge. Make your render script reject that case and keep the previous file. Horizontal clipping is
still undetected, which is why a wide composition has to be rendered at its real width.

**`--default-background-color=0` is rejected.** Chrome wants hex, and on macOS the error is
buried among unrelated `CVDisplayLink` noise. Omit the flag.

**A font that did not load fails silently.** A display face that ships 1 weight, asked for 600,
returns a synthetic bold that looks almost right and is not the face. Check the weights your
display face actually ships, and never set `font-weight` above 400 on a display element that has
only one.

## The ones that make a test lie

**`font-size` inside a `[style*="..."]` attribute selector is not an element.** A responsive
override written as `div[style*="font-size: 64px"] { ... }` contains the literal text of a size.
Any check that counts occurrences in the source counts those too. Our "exactly one hero number"
test reported 3, and 2 of them were media-query selectors. Strip attribute selectors before
counting.

**Pixel colour-share counting cannot see a gradient.** Gradient pixels are not exact token
hexes, so a page that turned a brand colour into a gradient surface still passed the colour-share
check at 7.2%. The explicit "no gradients" check is what caught it. Never rely on colour share
alone to detect slop.

**Pixel counting cannot see anything small, either.** A hero carried 4 coloured dots beside the
headline lines, off-palette, the only non-brand colour on an approved page. 4 dots sit under
the noise floor, so the measurement reported the page as brand-clean. Small features are found by
reading source, never by counting pixels.

**A battery that only passes is measuring nothing.** Run it against the original first, then
against a deliberately slopped copy, and record both numbers.

## The one that finds real bugs

**When the battery fails on a page you know is right, the test is wrong.** That is the whole
point of calibrating against the original.

Both failures on our first real run were test faults, and the second one mattered. A 16px
reading-text floor was failing on a page the creator had approved, because a floor set for
**prep docs** in one month had been silently inherited by every surface. That page carries
genuine reading text at 15px and 15.5px in 5 places, and at a 17px base that is 0.88x,
proportionally larger than a 16px caption on a 16px-base prep doc.

The fix was per-surface floors expressed as a ratio plus an absolute backstop. A test calibration
found a bug in the workspace's own standing rules.

## The ones the clean-room rebuild found, running for real

**A ratio written without the pixel it came from is a guess with a decimal point.** Our first
type-scale table was written from memory and never checked against the page. Both clean-room
agents built to it, and both built sizes the original does not have: a 2.95 headline at 50px
where the real one is 46px and 2.71, a 1.06 tier at 18px where the page has no 18px text at all,
and a 0.82 tier that computes to 13.94 and fails its own 14px floor. Measuring means mapping
every size on the page to the element that carries it. The record now holds the pixel value
beside every ratio for exactly this reason.

**A register is a set of structural moves; the colour share is their consequence.** The payload
gave one register an 18% accent share and the original's layouts. An agent building that register
therefore built the original's white story card and landed at 8%, because the 18% comes from a
deep proof band the original does not have. Describe what each register changes structurally. The
share follows.

**The person setting up the test can contradict the payload before the agent reads a word.** Run
2 was told to build a register while the payload said the baseline register was historic and not
built to any more. Neither instruction was wrong on its own. Check the brief against the payload
before launching.

**A test that passes a worse page and fails a better one is the dangerous kind, and this battery
had 4.** `calc(var(--base) * ratio)` is a more faithful reading of "ratios, not pixels" than
literal px, and one test scored it as having no hero number. 2 rules sharing one `.rule` class
is cleaner CSS, and another test failed it. A label family declared once as `--label` and used by
`var()` is better hygiene, and a third test counted every label as small reading text. The fix in
each case was to resolve what the browser resolves. **Any check that greps source for a literal
is a check that punishes indirection.**

**The clean-room agent's own gap list is the finding, not the rebuild.** Both runs' 3
least-confident guesses were exactly the holes visible from the copy alone, which is how you know
the test is measuring something real. Ask for the list. The page is secondary.

## The ones about losing rules

**Rules that live only in a document come back undone.** Em dashes had been stripped from a live
page at the creator's request. All 10 authored directions reintroduced them the next day,
written from scratch by a session that had read the brand sheet. A guarded claim about what a set
of numbers did and did not add up to came back the same way, in the same week.

Both are now build errors rather than memories: the token module refuses any generated page
containing an em dash or the banned claim. **If a rule matters and keeps getting lost, guard it
in code.**

**A blanket strip breaks the non-prose case.** Replacing every em dash with a comma turned a
table cell's standalone "no value" placeholder into a stray comma on a card. Handle the
standalone case first (a lone dash between tags becomes an en dash), then the prose case.

## The one about honesty

**Never write a record of a step before running it.** In the first hour here, a `rebuild_log` was
written into `dna.json` listing 5 findings from a rebuild that had not happened. It was
plausible, and 3 of the 5 guesses may even have been right, which is exactly what makes it
dangerous. It was caught on a re-read and removed.

The rule that follows: a log entry describes a run that happened. If the step cannot be performed
in this context, record that it is **open**, name why, and say how to run it.

## The ones about shipping a page

**A flex parent crushes a fixed-size canvas from the sides.** A 1920x1080 deck inside a flex
container was squeezed narrow on a laptop screen until the deck container got `flex: none` and the
canvas its minimum size. A fixed canvas scales uniformly to fill the window; it never lets its
container resize it.

**A fixed `max-width` column looks fine on the screen it was built on.** On a wide monitor it
floats in the middle with empty margins. The page spans the viewport with a fluid gutter
(`padding-inline: clamp(16px, 4vw, 64px)`) and grids reflow with
`repeat(auto-fit, minmax(...))`. Check every page at 1728x1080, 1920x1080 and phone width.
`dna_check.py`'s `full-screen` check catches the source half of this.

**Check what a page says by its rendered text, never by one tag.** A heading grep on a live page
found 1 item where 3 were on it, because the titles sat in an eyebrow class the grep could not
see. Strip the tags and read the text, then count what a reader would count.

**Read the HTML comments before a link goes out.** A published page carried build comments naming
internal file paths and a contact's name, one right-click away from every reader. A comment that
is right in a prep doc is wrong in anything published.

**2 options that render the same are 1 option.** A pair of colour washes measured 1 to 3 values
apart out of 255. Nobody can see that, so it was one option offered twice. Measure options
against each other before a board goes out, and put close ones on one row, side by side.

**A DOM query that finds nothing has 2 explanations.** In a viewport too narrow for the layout,
the pane being queried was never rendered, so the query found zero and looked like a finding.
Scope the query to the element you meant, assert it exists, then trust a zero.

## Cost notes

- A full render of 7 directions takes about 4 minutes, mostly the 2 tall wide compositions.
  Background it.
- Rendering for the web at 620 to 660px wide JPEG at quality 78 puts 10 designs under 1MB, which
  embeds comfortably inside an artifact.
- Cache the render keyed on the file's modification time. Re-running a check after an edit is
  then cheap, and after no edit it is free.
