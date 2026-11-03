# The finish pass

Run it on every page after the build and before the page check. It is where a page stops looking
assembled. It draws on a public motion-pass method from a design creator's video, the
make-interfaces-feel-better checklist and the Impeccable craft floor. **Your own locked rules
(`content/brand.md`, `RULINGS.md`) win every conflict**: the defaults below assume a light-mode,
single-accent, full-width house style with an 18px floor and no em dashes. Change the ones that
are not yours.

## 1. One built visual per section that holds numbers

A section whose numbers sit only in paragraphs is unfinished. Turn them into the visual: a split
bar for shares of a whole, a line of the real readings for a day, a size bar beside each row of a
list, a gauge for one used-of-total. Plot only measured points and say so under the visual. Keep
the paragraph under it; the visual never replaces the words. A steps list or a warning gets no
visual.

## 2. One type scale

Base 18px times 1.333: 18, 24, 32, 43, 57, plus one hero size up to about 135px. At most 6 sizes
on a page. Nothing under 18px, code included. Headings take `text-wrap: balance`, body
`text-wrap: pretty`, the body tabular numerals.

## 3. Motion: one authored moment, the rest is feedback

- One element per page moves on its own when it enters the view: a chart drawing its line, a
  split bar filling. 500 to 800ms, `cubic-bezier(.16, 1, .3, 1)`.
- A list enters with a 40ms stagger, 300ms per item, the delay capped at 8 steps. Sections never
  stagger.
- A card lifts 4px on hover and its border turns `{BRAND_ACCENT_PALE}`, 260ms. No shadow.
- A button presses to scale .97, 160ms.
- A number that matters counts up once, under 1 second.
- An icon swaps by opacity 0 to 1, scale .25 to 1 and blur 4px to 0, 200ms.
- Exits are faster than entrances. Never `transition: all`. Animate transform, opacity and a
  line's `stroke-dashoffset`, nothing that moves layout.
- The page reads fully if the script never runs: hidden states come from a class the script adds
  before paint.
- The `prefers-reduced-motion` block is always there and shows every final state.

## 4. The browser surfaces

`::selection` in a pale tint of the accent, `caret-color: {BRAND_ACCENT}`, `scrollbar-color` in
the pale accent on the ground, a 2px accent focus ring that eases in, `-webkit-font-smoothing:
antialiased`. Cheap, and the first thing a generated page forgets.

## 5. Shapes and targets

Corners are concentric: an inner radius equals the outer radius minus the padding between them.
One radius scale per page. Every control, links included, is 44px tall at least.

## 6. Check it in the render

Run the page check at 1440 and 390:

```bash
python3 .claude/skills/design-dna/scripts/page_check.py <page.html>
```

It must report: no sideways scroll on the page or inside any box, no text under 18px, at most 6
sizes, reading text at 4.5:1 (3:1 above 43px), no control under 44px, the reduced-motion block
present, no `prefers-color-scheme`, no gradient. Then open the screenshots it wrote and look. One
batched fix round, one confirm round, then stop.

## 7. Keep it short

- One focal number per screen. A tile that repeats the hero number on the same screen goes; its
  one new fact moves into the hero caption.
- Rows that all passed the same tests open folded, the shared reason stated once in the list
  header. Rows that are each a decision stay open.

## Never

This pass never changes the words, never adds a dark theme, a second accent, a gradient, glass,
emoji, a fake browser frame, a coloured stripe on a card, or motion a reader has to wait through.

## Found while applying it

- **A code chip inside muted prose takes the ink colour.** A muted grey on a stone tint measured
  4.43:1, under the 4.5 reading floor; the page check found 20 such runs on one page that a
  single-threshold check had missed. Ink on the same tint was 14.5:1.
- **At phone width the hero number shrinks, and 43px is not above 43px.** A `clamp()` hero that
  reaches 43px at 390 is held to 4.5:1, not 3:1. One hero passed at 1440 (57px) and failed at 390
  (43px, 4.43:1).
