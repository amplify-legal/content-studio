# Reel style + schema catalog

## Reference reels (the style to replicate)

Keep your own list of 3 to 5 reference reels in `content/taste/shorts-formats.md`, each with one line on what to take from it (the layout, a schema, the caption style, the accent). Study them before your first render and before any style change. Never copy their text, only their visual vocabulary.

Shared DNA: talking-head at the bottom, glass schemas in the upper half, one-word karaoke subtitles, ONE accent per video, graphics ALMOST always present that change every ~2-3s, count-up on numbers, graphs that draw themselves.

**Themeable palette (ONE accent per video):** your `BRAND_ACCENT` from `content/brand.md` is the default (`scripts/brand.py` resolves it; `python3 scripts/brand.py` prints what it found) · `BRAND_ACCENT_DARK` for fills · `BRAND_RED` (default #ff5470) for expensive / lost · `BRAND_NEUTRAL` (default steel #7f93ad) for a neutral competitor. A one-off video can override the accent (for example a sponsored video themed to the sponsor's colour): `BRAND_ACCENT=#RRGGBB` in the environment, or set `A` at the top of `gen.py`. The 2 worked examples in `examples/` hard-code their own green and orange on purpose.

## Schema catalog (types in gen.py)
- **intro**: a plane (✈) flying along a dashed arc that draws itself (MotionPathPlugin) + an elegant title. For hooks.
- **statgraph**: large number with count-up (e.g. 0→340+) + unit + sparkline. For "hundreds of leads".
- **summary**: eyebrow + large keyword (e.g. "THOUSANDS LOST"). A summary sentence, NOT a paragraph.
- **graph**: just a line graph that draws itself, down+red (loss) or up+green (growth).
- **crm**: a labelled row list. Each row is an avatar, a name, a detail and a status tag, entering in stagger. Up to 5 rows.
- **listcheck**: rows with a checkmark ✓ that enter on the trigger words.
- **calendar**: calendar grid with one day highlighted in the accent. NO red "elsewhere" arrow.
- **comstep**: "BY HAND" list with a red struck-through ✕, items entering ONE PER WORD (step-by-step synced), then an "IMPOSSIBLE" stamp.
- **iphone**: reveal of the real product screenshot (`assets/iphone_phone.png`) + a "POWERED BY" logo row. For the product moment.
- **wachat**: a dark chat panel (header with an app logo, a name and a status line, incoming and outgoing bubbles with read ticks), bubbles entering on the words.
- **msgtpl**: a single chat bubble carrying a template message, with the variable parts highlighted in the accent, e.g. "Hi [first name]! You asked about [the thing]... here is [the answer]".
- **vflow**: 3 boxes stacked VERTICALLY (top→bottom) with ↓ arrows (e.g. CONTACTS → THE PRODUCT → CLIENTS).
- **cta**: accent-bordered card with a keyword + a meter bar that fills up.

## Animations
- Snappy entrances (0.15-0.25s, ease `back.out` or `power3.out`). NEVER a pulsing loop on the boxes.
- Graphs/sparklines: stroke-dashoffset 760→0 in ~1s.
- Count-up: tween on a proxy {v} with onUpdate → textContent.
- Decorative (always on, deterministic loops on a scrubbed timeline): particles y-drift + opacity, streaks x-translate, glow scale/move, grid background-position.

## Music + audio mix
`assets/bg-music.m4a` if you put one there (nothing ships: see `assets/README.md`), or any track you point `MUSIC=` at. Default: from second 0:04 of the track, from the start of the short, final fade-out (see compose.sh). With no track at all, compose.sh renders voice only.
**The voice must DOMINATE**: compose.sh normalizes the voice to dialogue level (loudnorm I=-16) and keeps the music LOW (**volume 0.02, which is 2% and the shipping level**, override with `MUSIC_VOL=`). Both 0.15 and 0.06 are RETIRED defaults, named here only so nobody reinstates one: 0.15 drowned out the voice, and 0.06 was still called way too loud on a real review.
