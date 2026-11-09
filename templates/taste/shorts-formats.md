> **`content/taste/shorts-formats.md`** · written by you, in your own words, through the `taste-builder` skill and your shorts reviews · read by `shorts-editor` (before any vertical clip is cut), `cut-review`, `content`, `content-waterfall`, and the example shorts pipeline (`examples/podcast-shorts-pipeline/`).

# Shorts formats: the safe frame and the format family

> **Starting defaults** are measured craft numbers that held up across 3 platforms, plus the rules a working channel settled over 4 review rounds of podcast and tutorial shorts. They are not your taste: change any of them, but measure (or watch the short on a phone) before you do, and write the new number and the reason here. **Mine** is your own format family and your own rulings.
>
> The method behind every number (what was tried, what failed, the version that works) is the edit lab book, `content/reference/edit-lab/`. This file says what the short should look like; the book says how it was got to render that way.

## Starting defaults, change them

### The safe frame (1080x1920, one frame for every platform)

Measured on screenshots of LinkedIn's full-screen player, Instagram Reels and YouTube Shorts on a 5.4 inch phone. The small phone is the floor: a bigger one shows the same overlays with more room. One frame for all platforms, no per-platform caption variants.

| Zone | Rule |
|---|---|
| Top 12% (0 to 230px) | Nothing that matters. Platform chrome sits here. Any top text starts at or below 290px (15%), in case a feed crops 9:16 to 4:5. On an animated or tutorial short the top band may serve the animation (the chrome is still avoided). |
| 12% to 50% (230 to 960px) | Title bands, held lines, tables and cards, full width. |
| Captions | The block sits between 62% and 78% of height (1190 to 1500px), max width about 720px centred (x 180 to 900). |
| Bottom 22% (1500 to 1920px) | Nothing that matters. Author name, caption text and chips cover it on every platform. |
| Right 16% from 50% down (x over 905, y over 960) | Dead. The icon rail lives here. No numbers, chips or credit. A panel that runs below 960 ends at x 904. |
| Sides | Keep faces and words inside the middle 92% of the width; some players crop the sides. |
| Credit | Bottom-left inside the safe zone, x 60 to 700, bottom edge at or above 1500. |

`shorts-editor/scripts/check_safe_area.py` enforces the 1500 line and checks that the mouth and chin never enter the bottom band.

### Faces

- **The face is framed, never cornered.** Whole head with room above it, eyes around 40% of height, chin above 60%.
- **The face box spans the full width of the frame, left to right; a cropped chin, neck or collar is a fail; nobody is a small circle.** Reason: on a phone a face is the anchor, and a face cut at the chin reads as a mistake.
- **Nobody small.** Every face about 300px or more, hair to chin about 380px; a stacked question whose smaller face would solve under about 272px plays full frame on its own speaker instead. Reason: a small face on a phone is a dot.
- **The mouth and chin never enter the bottom band, at any second.** Frame the face band from the whole cut's lowest mouth position, not from one frame, including when the speaker leans in.
- **When there is headroom to spare, lift the face and fill the freed bottom with a blurred, faded extension of the same video**, never a hard black bar and never a black pillar beside a narrow crop. The blur sits low: the bottom 15% of the frame (the footage reaches at least y 1640). Reason: a blur that climbs toward the face reads as a mistake.
- **Nothing is ever placed on a face**: no sticker, list row, card, credit or caption. Lists and cards go in the space above the head, and the title leaves (by about 28 s, or as soon as the graphic needs the top) to make that room.
- **Captions never sit on the seam** between a face cam and a card area. They sit clearly inside one zone.
- **A landscape source is transformed into vertical, never letterboxed onto a blurred copy of itself.** Crop to the speaker so the face fills the frame; crop the office off the sides. Use as much of the screen as possible.

### Captions

- **Size floor: a capital H at least 47px tall on a 1080-wide frame**, gated by `check_caption_size.py --style` on the exact style that burns. That is Montserrat 78 in the variable face and 104 in the static Montserrat Bold face (the static face draws about 25% smaller at the same size, which is why the gate measures the capital, never the point size). A font change is a caption-size change: re-measure before rendering.
- **The first 8 seconds run bigger** (a 53px capital: 118 in the static face). That stretch plays muted in the small feed autoplay, and it has to read there.
- **Check it small:** `check_caption_size.py <render.mp4>` writes a frame scaled to 375px wide. Read it by eye on every short before cut review.
- **Look:** white, bold, sentence case, a soft drop shadow, no outline, 1 or 2 lines, centred. The current word may take the accent colour (`content/brand.md`). **On a light background a caption sits in a dark box, one box per line** (a box per word makes stripes), or takes a dark colour: white on light is out.
- **Grouping:** by sentence, then balanced 2-line chunks laid out by a shortest path, never greedily. Never across a cut, and **a shot change is a cut**: no phrase from one speaker stays over the next speaker's face. No caption line of 1 word, none on screen under 0.3s.
- **Captions clean the words, never the audio:** drop um and uh, the other speaker's lone "yeah", false starts and immediate repeats from the caption text. Numbers as digits (a transcriber that writes "twenty seven" needs a number pass).
- **A short opens and closes on a sentence edge**; when it starts mid-sentence, its first caption word is capitalised.
- **Phone-sized card copy:** a card is read at phone size. A few words that carry weight, big type, with any animation complementing the words rather than carrying detail of its own. If a card needs a legend or more than about 6 words, it is the wrong card.
- **No option label is burned into a short.** A label (S1, U5) is a review aid on the board and in the file name, never in the frame.

### The order of a podcast short

- **The aha moment first (the kicker, the shocking or funny line), then the question, then the full answer, and the guest's introduction at the END of the clip**, never in the middle and never right after the question. Reason: the first 4 seconds are the most important 4 seconds of the reel, and an introduction as the second beat lands awkwardly. Exception: a question so good it opens the short on its own.
- **Render the hook both ways and compare** (opens on the question, opens on the aha line) rather than letting the finder pick one; a reviewer, human or model, forms the opinion on the pair against your past feedback.
- **Give the viewer the context the podcast gave you**: who the guest is and what the topic is, in a few seconds, when the line needs it. A hook title names who the guest is when the viewer would not know ("Tax adviser explains why she turns down her biggest clients" is the shape, an invented example). Clips may be reordered to build the setup.
- **One clear purpose: what the viewer learns.** A short that is all over the place is recut, not polished. Cut for the sauce: name the one thing a viewer saves the short for and make sure it is in; a speaker stays only if they add something new; a run of examples of the same thing is cut to the first 1 or 2.
- **Under 60 seconds unless the moment really deserves more, the arc kept whole, and snappy.** Trim inside (repeats, restarts, asides) before cutting the end. Speech at 1.1x to 1.25x.

### The credit

- **Larger text at the bottom in the last 5 to 7 seconds**, never a small chip all the way through.
- **The credit beside a guest's name is the guest's own firm or organisation, never yours.** Your brand or show name may appear elsewhere, never beside their name. A guest with no firm on record gets the name alone.
- **The credit shows only while the person it names is on screen, and long enough to read.**

### Looks and motion

- **A plain look carries most shorts.** On one working channel the split that held was about 2 shorts in 10 with animation, and only where the tape has a moment that earns motion (a number that matters, a named sequence, many becoming one, a state change, a step in a tool); the rest in a native look (full-bleed face, a title sticker on top that names the topic, one caption line). Reason: a set that animates everything over-indexes on one style and the motion stops meaning anything.
- **An animated short opens on the native hook and headline; while nobody animates, the native look carries it; when the animation plays, the title goes and the animation takes the full top; between animations, back to the native look.** Reason: half a screen of black while the guest talks is the failure this rule came from.
- **A card is on screen only while it animates with a purpose**, and every scene change gets a real transition, never a jump.
- **The top of a short never sits still for long.** A graphic leaves when its beat is over, and the title follows the conversation (a title swap when the subject changes).
- **A money fact gets a visual with weight** (bars, a count-up), not a table row. The title hook matches the clip under it.
- **Light and dark twins**: render both side by side until your taste settles one; a soft accent glow reads in both.
- **Tutorial and long-form shorts get their own look, never the podcast style.** What is on screen is the subject: the real screen, zoomed until the words read at phone width, stays on frame while it is explained, the person big under it, one mark (an outline, a highlighter, a dim on the rest) on the word, nothing sliced by an edge, no private UI. Mask the screen frame by frame.

### Sound

- **Every short gets a noise and echo clean-up pass, then a de-esser and a soft transient limit**, so no syllable spikes or stings the ear: about -14 LUFS, true peak at or under -1 dBTP, measured before and after with a 3 to 8 kHz band meter. Stop before the voice dulls. The chain and its failed tries are in `content/reference/edit-lab/sound.md`, "Harshness and sharp peaks".
- **Music bed at 2%** on a talking short (`compose.sh`'s default).

### Crops, cuts and builds

- **Wide two-person shots need a zoom, not a full-height crop.** Set a crop per speaker shot by eye on a gridded frame; automatic face detection is unreliable on busy wide shots.
- **Cut every piece in one trim-and-concat pass.** Seeking each piece separately can hold a duplicated frame at every join.
- **libass draws Montserrat Bold narrower than PIL measures it** (583 PIL units drew 443px): set caption width in measured drawn pixels, not PIL units.
- **Judge sharpness at 1:1 pixels.** See `content/frameworks/short.md` for the upscale arithmetic.
- **A short carries a face.** When the source is a screen with a small camera bubble, the real face from that bubble, upscaled (lanczos plus a light unsharp, 2.5x held on a phone from a 318px source), is the anchor. Never a generated face.

### Process

- **The first board puts every picked short in a different format from the family**; mixing and matching comes after.
- **Animated shorts: the raw cuts go to the person first**, then they describe the animation for each. No animation is designed before the raw cut is seen.
- **A short skipped on the review page is not a pass.** A short with no tick and no note, whose style already has feedback elsewhere, is transformed under that feedback, never left as it is.
- **Recorded as a short beats lifted from a long form.** A clip lifted from a long form is the fallback, and the board says it is a lifted clip.
- **A guest's shorts are for the guest to post**: they feature the guest (their face, their voice, their name on screen), and the guest gets the MP4 files, not only links to your posts.
- **Taste profiles from the feedback:** mine every review for patterns that repeat. A pattern with 3 or more receipts becomes a profile in `content/taste/shorts-profiles.md`; 1 or 2 is a candidate. A brief lists 2 or more profiles as options, never one.

### Lessons from a fifth review round (starting defaults, 2026-11-04)

An editor reviewed 21 shorts from one page: 14 kept, 7 cut, each cut with its fix named. The cuts, written as rules:

- **Never the same clip twice in a row.** The opening line followed by the same line again inside the answer reads as a mistake. Remove the first one.
- **Never cut a speaker mid-sentence, at the hook seam or at the end.** Let them finish the point, then end the shot.
- **A list on screen never mixes the mistakes and the fixes.** When the talk turns to what to do instead, a new list in another colour starts.
- **One short, one topic.** When a short would cut from an explanation to a demo, it is 2 shorts, and in the demo short the viewer sees the cause before the result (the button being pressed, then the result appearing).
- **A tutorial short never shows only the face in a centred box with no screen.** The same video made better shorts with the screen in them.
- **Name 1 benchmark short per kind once a reviewer calls one "the benchmark"**, and build the next round toward it; write its name and why in `## Mine` below.

### The short's job

Teach something and deliver real value in under 60 seconds. Every format is judged on that first. **Self-check before it is shown:** every frame and every short is opened at full size and checked against this file before a person sees it.

## Mine

### My format family

| Format | What it is | Status (trying / keeping / dropped) | Notes in my words |
|---|---|---|---|
| <talking head plus card band> | | | |
| <native look: full-bleed face, title sticker> | | | |
| <screen walkthrough (tutorial look)> | | | |
| <two-person clip (stacked question, then answer)> | | | |

An unticked format is not a rejected one. Every format gets another pass until you make the call.

### My reference reels

<3 to 5 reels, each with one line on what to take from it (the layout, a schema, the caption style, the accent).>

### Cadence

<How often you post, and what the rest of the week's pieces are.>

### Post text that goes with a short

<What you changed on your own posts, measured against what you actually posted, not the draft.>

### Review rounds and what they taught

<Dated entries: the round, which shorts went, which got fixed, your words, the rule or guideline it made. A rule that repeats across styles moves up into the starting defaults above, in your own words.>

## Retro

A starting default you change gets the new number and the reason. Numbers here are measurements: re-measure on your own devices before you trust them.
