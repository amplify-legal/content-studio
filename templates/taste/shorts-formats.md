> **`content/taste/shorts-formats.md`** · written by you, in your own words, through the `taste-builder` skill and your shorts reviews · read by `shorts-editor` (before any vertical clip is cut), `cut-review`, `content`, `content-waterfall`.

# Shorts formats: the safe frame and the format family

> **Starting defaults** are measured craft numbers that held up across 3 platforms. They are not anybody's taste: change them, but measure before you do. **Mine** is your own format family and your own rulings.

## Starting defaults, change them

### The safe frame (1080x1920, one frame for every platform)

Measured on screenshots of LinkedIn's full-screen player, Instagram Reels and YouTube Shorts on a small phone. The small phone is the floor: a bigger one shows the same overlays with more room. One frame for all platforms, no per-platform caption variants.

| Zone | Rule |
|---|---|
| Top 12% (0 to 230px) | Nothing that matters. Platform chrome sits here. Any top text starts at or below 290px (15%), in case a feed crops 9:16 to 4:5. |
| 12% to 50% (230 to 960px) | Title bands, held lines, tables and cards, full width. |
| Captions | The block sits between 62% and 78% of height (1190 to 1500px), max width about 720px centred (x 180 to 900). |
| Bottom 22% (1500 to 1920px) | Nothing that matters. Author name, caption text and chips cover it on every platform. |
| Right 16% from 50% down (x over 905, y over 960) | Dead. The icon rail lives here. No numbers, chips or credit. |
| Sides | Keep faces and words inside the middle 92% of the width; some players crop the sides. |
| Credit chip | Bottom-left inside the safe zone, x 60 to 700, bottom edge at or above 1500. |

`shorts-editor/scripts/check_safe_area.py` enforces the 1500 line and checks that the mouth and chin never enter the bottom band.

### Faces

- **The face is framed, never cornered.** Whole head with room above it, eyes around 40% of height, chin above 60%.
- **The mouth and chin never enter the bottom band, at any second.** Frame the face band from the whole cut's lowest mouth position, not from one frame, including when the speaker leans in.
- **When there is headroom to spare, lift the face and fill the freed bottom with a faded extension of the same video** (a soft gradient or blurred extension), never a hard black bar.
- **Captions never sit on the seam** between a face cam and a card area. They sit clearly inside one zone.

### Captions

- **Size floor:** `check_caption_size.py --style` gates every caption style: a capital H at least 35px tall on a 1080-wide frame. Measure the exact style that burns, because a bold weight or a different font file draws a different cap height at the same point size. A font change is a caption-size change: re-measure before rendering.
- **The first 8 seconds run bigger** (about 1.5x the floor's cap height). That stretch plays muted in the small feed autoplay, and it has to read there.
- **Check it small:** `check_caption_size.py <render.mp4>` writes a frame scaled to 375px wide. Read it by eye on every short before cut review.
- **Look:** a starting default many viewers find easiest to read: white, bold, sentence case, a soft drop shadow, no box, 1 or 2 lines, centred. The current word may lift in weight or take one accent colour (`content/brand.md`).
- **Grouping:** by sentence, then balanced 2-line chunks. Never across a cut, and **a shot change is a cut**: no phrase from one speaker stays over the next speaker's face.
- **Captions clean the words, never the audio:** drop um and uh, the other speaker's lone "yeah", false starts and immediate repeats from the caption text.
- **Phone-sized card copy:** a card in a short is read at phone size. A few words that carry weight, big type, with any animation complementing the words rather than carrying detail of its own. If a card needs a legend or more than about 6 words, it is the wrong card.

### Crops and cuts

- **A landscape source is transformed into vertical, never letterboxed onto a blurred copy of itself.** Crop to the speaker so the face fills the frame. Use as much of the screen as possible.
- **Wide two-person shots need a zoom, not a full-height crop.** A full-height crop keeps the whole body and puts the face small at the top. Set a crop per speaker shot by eye on a gridded frame; automatic face detection is unreliable on busy wide shots.
- **Cut every piece in one trim-and-concat pass.** Seeking each piece separately can hold a duplicated frame at every join.
- **Judge sharpness at 1:1 pixels.** See `content/frameworks/short.md` for the upscale arithmetic.

### The short's job

Teach something and deliver real value in under 60 seconds. Every format is judged on that first. **Self-check before it is shown:** every frame and every short is opened at full size and checked against this file before a person sees it.

## Mine

### My format family

| Format | What it is | Status (trying / keeping / dropped) | Notes in my words |
|---|---|---|---|
| <talking head plus card band> | | | |
| <screen walkthrough> | | | |
| <two-person clip> | | | |

An unticked format is not a rejected one. Every format gets another pass until you make the call.

### Cadence

<How often you post, and what the rest of the week's pieces are.>

### Post text that goes with a short

<What you changed on your own posts, measured against what you actually posted, not the draft.>

### Picks and what they taught

<Dated entries: which shorts went, which got fixed, your words, the rule or guideline.>

## Retro

A starting default you change gets the new number and the reason. Numbers here are measurements: re-measure on your own devices before you trust them.
