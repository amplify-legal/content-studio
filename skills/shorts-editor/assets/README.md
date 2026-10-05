# assets/, and why it arrives empty

This folder ships with nothing in it but this file. The scripts expect up to 3 kinds of
file here, and none of them is ours to hand you: a caption font, a background music
track, and optional logo SVGs. This page says exactly what goes where, the filenames the
scripts look for, where to get free ones, how to point the scripts elsewhere, and what
breaks if you skip each one.

Add the caption font and the whole pipeline runs. The music and the logos are optional.

## What belongs here

```
assets/
├── fonts/
│   ├── caption.ttf                          ← your caption font (any name works via BRAND_CAPTION_FONT)
│   │   or Montserrat-VariableFont_wght.ttf  ← the tested default, found automatically
│   ├── <display font>.ttf                   ← optional: BRAND_FONT_DISPLAY from content/brand.md
│   └── <body font>.ttf                      ← optional: BRAND_FONT_BODY from content/brand.md
├── logos/                                   ← optional: SVG marks you have the right to use
│   └── <name>.svg                           (gen.py names whatsapp, claude, openai, github; the examples name logo, github, model-a to model-c)
└── bg-music.m4a                             ← optional: the default music bed
```

Filenames matter where they are listed above. Everything can also be pointed elsewhere with
an environment variable or a line in `content/brand.md`, as below.

## 1. The caption font (do this one)

`scripts/captions_brand.py` and `scripts/captions.py` both resolve the font through
`scripts/brand.py`, in this order:

1. `--font /path/to/font.ttf` on `captions_brand.py`
2. `CAPTION_FONT` or `BRAND_CAPTION_FONT` in the environment
3. `BRAND_CAPTION_FONT: <path>` in `content/brand.md` (a relative path is read from the folder holding `brand.md`, then from this skill folder)
4. `assets/fonts/caption.ttf`
5. `assets/fonts/Montserrat-VariableFont_wght.ttf`
6. `~/Library/Fonts/Montserrat-VariableFont_wght.ttf`, then `~/.fonts/...`, then `/usr/share/fonts/truetype/montserrat/...`

Find nothing and the script exits with a sentence saying how to supply one, rather than
rendering the wrong face.

**Where to get it:** [Google Fonts](https://fonts.google.com) is the free source. The tested
default is [Montserrat](https://fonts.google.com/specimen/Montserrat): "Get font", then
"Download all", and the zip contains `Montserrat-VariableFont_wght.ttf`. Drop it in
`assets/fonts/`. Use the **variable** file: the scripts set the weight axis themselves (900
for the one-word renderer, 700 for the phrase renderer). A static font still works, at its
own weight.

**The size floor goes with the font.** The floor is a capital H at least 35px tall on a
1080-wide frame, which is Montserrat at 78px. With another font, check the height, not the
point size: `python3 scripts/check_caption_size.py --style "<your ASS Style line>" --fontsdir assets/fonts`.

**Licensing:** Google Fonts are under the [SIL Open Font License 1.1](https://openfontlicense.org)
or similar open licences. You can use them commercially and redistribute them. Keep the
`OFL.txt` from the zip next to the font if you pass it on.

## 2. The card fonts (optional)

The cards are HTML. `gen.py` writes `font-family: "{BRAND_FONT_DISPLAY}", "{BRAND_FONT_BODY}", sans-serif`
from `content/brand.md`. For the render to actually use them, the font must be installed on
the machine that renders, or loaded in the card page (copy the `.ttf` into the project's
`cards/assets/` and add an `@font-face` rule to the page). If it is neither, the browser
silently falls back to a system face, so look at a rendered frame.

## 3. The music (optional)

**No music ships with this skill.** Music licensing does not travel: a bed that one person
may use is not a thing anyone can hand out. Use a track from a royalty-free library you hold
a licence for, or your own.

`scripts/compose.sh` (and `references/examples/compose-broll.sh`) read:

```bash
MUSIC="${MUSIC:-$SKILL_DIR/assets/bg-music.m4a}"   # the track
MUSIC_VOL="${MUSIC_VOL:-0.02}"                      # its level: 2%, the shipping level
```

So, either:

```bash
# point at your track for one render
MUSIC=/path/to/my-licensed-track.m4a bash scripts/compose.sh ...

# or make it the default for every render
cp /path/to/my-licensed-track.m4a assets/bg-music.m4a
```

The file must be named exactly `bg-music.m4a` to be the default. Any format ffmpeg reads works
through `MUSIC=`. `compose.sh` takes the track from its 0:04 mark, holds it at 2% under a voice
normalised to dialog level, fades in over 0.5s and out over the last 2s. 6% is a retired
default that was called way too loud on review; it is named only so nobody reinstates it.

## 4. The logos (optional, only if your cards use them)

`scripts/gen.py`'s phone card builds a "POWERED BY" row from `assets/logos/<name>.svg`, and the
example generators and `references/card-snippets.md` reference `logo.svg`, `github.svg` and
`model-a.svg` to `model-c.svg` by name. At pipeline step 9 the project copies this folder into
its own `cards/assets/logos/`. Change the names in the card code to match the files you have.

**Any product logo is another company's trademark.** They are not ours to redistribute, so they are not
here. Put only marks you have the right to use in this folder:

- Your own logo, which is the usual answer.
- Or a mark from that company's own brand or press page, used under its trademark guidelines.
  Most permit unmodified editorial use and forbid anything that implies endorsement.
  Convenient is not the same as licensed. **Check before anything ships commercially.**

2 things the errors table learned about logo SVGs, worth knowing before you drop one in:

- A `viewBox` that does not match the path coordinates renders **invisible**. One logo once had
  `viewBox 0 0 1024 1024` with path coords in the 0-16 range.
- A logo drawn with `currentColor` and loaded through `<img>` renders **black**, which is
  black-on-black on the card band. Bake `fill="#fff"` into the file.

Open every logo over a black background and look at it before you render.

## What breaks with an empty folder

| Missing | What happens |
|---|---|
| The caption font | **The captions stop.** Both caption scripts exit with a message naming `CAPTION_FONT`. Nothing renders past step 11. This is the one to fix. |
| The card fonts | Nothing breaks. The cards render in a system fallback face; look at a frame and decide. |
| The music | Nothing breaks. `compose.sh` says no track is present and renders voice only. |
| The logos | Only cards that ask for a logo break, and visually: a broken-image gap in the band. Cards built from type, numbers, graphs, terminals or lists are unaffected, which is most of the schema vocabulary. |

## One more file the template mentions

`scripts/gen.py`'s `iphone` schema loads `assets/iphone_phone.png`, a product screenshot. That is
a per-project image, not a skill asset: put your own screenshot at `cards/assets/iphone_phone.png`
inside the project folder if you use that card, or use another schema.
