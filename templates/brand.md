> **`content/brand.md`** · filled in by you, once, then changed only when your brand changes · read by `shorts-editor` (through its `scripts/brand.py`), `design-dna`, `on-camera-board`, `media-gen`, `long-form-editor`, and the edit runbooks in `content/reference/`.

# Brand

> Your brand values in one place, so no renderer or page hard-codes a colour or a font. Change a value here and every short, card, board and page re-themes.
>
> **How to fill it in:** replace each `<...>` or `#RRGGBB` in the **Value** column with your own value. Keep the key column exactly as it is: scripts find each row by its key. A row you leave unfilled keeps the script's neutral default.
>
> **One caution for editing:** `scripts/brand.py` reads any line that contains a key name, so write key names only in the tables below, never in your own notes.
>
> Check what the shorts pipeline resolved, and from where: `python3 .claude/skills/shorts-editor/scripts/brand.py`

## Name

| Key | Value | Read by |
|---|---|---|
| `{BRAND_NAME}` | `<your brand or channel name, exactly as written>` | `design-dna`, `on-camera-board`, page footers, end screens |
| `{SHOW_NAME}` | `<your podcast or show name, if any>` | `long-form-editor` (wordmark band), podcast run sheets |

## Colours

One accent per video. Every colour has a role, and a role is what skills ask for.

| Key | Value | Role | Read by |
|---|---|---|---|
| `{BRAND_ACCENT}` | `#RRGGBB` | the one accent: highlighted caption word, card accent, the claim and the call to action | `shorts-editor`, `design-dna`, `on-camera-board`, `media-gen` |
| `{BRAND_ACCENT_DARK}` | `#RRGGBB` | a darker partner for fills and secondary elements | `shorts-editor` |
| `{BRAND_ACCENT_PALE}` | `#RRGGBB` | a pale panel behind a fix or a "after" | `on-camera-board`, `design-dna` |
| `{BRAND_INK}` | `#RRGGBB` | all main type | `design-dna`, `on-camera-board` |
| `{BRAND_GROUND}` | `#RRGGBB` | the background | `design-dna`, `on-camera-board` |
| `{BRAND_RED}` | `#RRGGBB` | "no, lost, expensive" on shorts cards | `shorts-editor` |
| `{BRAND_PROBLEM}` | `#RRGGBB` | the problem, the "before", on boards and pages (often the same as the red above) | `on-camera-board`, `design-dna` |
| `{BRAND_PROBLEM_PALE}` | `#RRGGBB` | a pale panel behind a problem | `on-camera-board` |
| `{BRAND_NEUTRAL}` | `#RRGGBB` | a neutral or muted item on shorts cards | `shorts-editor` |
| `{BRAND_MUTED}` | `#RRGGBB` | dimmed, not-today, dead weight on boards and pages | `on-camera-board`, `design-dna` |

Thumbnails may step off the brand colours when contrast demands it. That rule lives in `content/taste/thumbnails.md`, not here.

## Fonts

Use font family names as your system or the web knows them. If the display face ships only 1 weight, never let a renderer fake a bold on it.

| Key | Value | Role | Read by |
|---|---|---|---|
| `{BRAND_FONT_DISPLAY}` | `<display font family>` | headlines and card titles | `shorts-editor`, `design-dna`, `on-camera-board` |
| `{BRAND_FONT_BODY}` | `<body font family>` | body text | `shorts-editor`, `design-dna` |
| `{BRAND_FONT_LABEL}` | `<label font family>` | small uppercase labels | `design-dna`, `on-camera-board` |
| `{BRAND_FONT_CAPTION}` | `<caption font family>` | burned-in captions, by name | `long-form-editor`, the edit runbooks |
| `{BRAND_CAPTION_FONT}` | `<path to the caption .ttf file, relative to this file or absolute>` | the font file the caption renderers bake with | `shorts-editor` (`captions.py`, `captions_brand.py`) |

Examples only, from Google Fonts, to show the kind of pairing that works (pick your own): a serif display such as Fraunces or Playfair Display, a sans body such as Source Sans 3, a wide label face such as Space Grotesk, a bold caption face such as Montserrat.

**A font change is a caption-size change.** Different font files draw different cap heights at the same size, so re-run `check_caption_size.py --style` after changing the caption font (see `content/taste/shorts-formats.md`).

## Caption style

The size and position floors are craft rules in `content/taste/shorts-formats.md`. The look is yours.

| Key | Value | Notes | Read by |
|---|---|---|---|
| `{CAPTION_COLOUR}` | `#RRGGBB` | the caption text colour. White reads on most footage. | `shorts-editor`, `long-form-editor` (applied by the skill, not by brand.py) |
| `{CAPTION_HIGHLIGHT}` | `<accent, or a hex>` | the current-word highlight. Defaults to the brand accent. | `shorts-editor`, `long-form-editor` |
| `{CAPTION_OUTLINE}` | `<none, shadow, or outline plus width>` | a soft drop shadow with no box is a common readable choice | `shorts-editor`, `long-form-editor` |
| `{CAPTION_CASE}` | `<sentence case or uppercase>` | sentence case is the starting default for spoken lines | `shorts-editor`, `long-form-editor` |

## Logos and marks

Real files only. A model-invented lookalike of a logo is a defect.

| Key | Value | Read by |
|---|---|---|
| `{LOGO_MARK}` | `<path, for example content/brand/logo/mark.png>` | `media-gen`, `design-dna`, `shorts-editor` cards |
| `{LOGO_WORDMARK}` | `<path, for example content/brand/logo/wordmark.png>` | `design-dna`, `long-form-editor` (show wordmark band) |
| `{LOGO_ON_DARK}` | `<path to a version that reads on dark grounds>` | `media-gen`, `on-camera-board` |

Third-party product logos you show in thumbnails go in `content/brand/logos/`, one real file per product.

## Real photos of the people

| Key | Value | Read by |
|---|---|---|
| `{PEOPLE_FOLDER}` | `content/brand/people/` | `media-gen`, thumbnail builders |
| `{PERSON_REFERENCE_1}` | `<path to your best front-facing photo>` | `media-gen` |
| `{PERSON_REFERENCE_2}` | `<path to a second photo, different light or angle>` | `media-gen` |

- `content/brand/people/` holds **photographs only**, one subfolder per person. Never an AI-generated image, never a recreation.
- **Every image generation of a real person points at these photographs as its reference.** A face is never invented from a text prompt.
- Frames pulled from your own recordings (front-facing, sharp, mid-speech) make strong references. Save them here too, labelled as frames.
- A generated image that drifted never goes back in as a reference. Only the real photographs do.

## Where values are read, in short

| Who | What it reads |
|---|---|
| `shorts-editor/scripts/brand.py` | the accent, dark accent, red, neutral, display font, body font and caption font file rows above, then environment variables of the same name, then command-line flags |
| `design-dna` | name, every colour role, display, body and label fonts |
| `on-camera-board` | ink, ground, accent, pale panels, problem, muted, fonts |
| `media-gen` | logo paths, the people folder and the reference photos |
| `long-form-editor` and the edit runbooks | caption font and style rows, show name, wordmark |
