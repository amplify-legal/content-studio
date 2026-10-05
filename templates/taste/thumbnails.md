> **`content/taste/thumbnails.md`** · written by you, in your own words, through the `taste-builder` skill (round 3), grown on every thumbnail round · read by `media-gen`, `content`, `watch`, `design-dna`, `shorts-editor` (first frame).

# Thumbnail rules (living)

> Two halves. **Starting defaults** are generic craft rules that held up on a working channel. They are not anybody's taste: change them, delete them, or mark them "not for me". **Mine** is your own taste, in your words, and it outranks the defaults wherever they disagree.
>
> Brand colours and fonts are not here. They live in `content/brand.md`.

## What stands today

<Your current direction in 3 lines. Rewritten, not appended, when it changes.>

## Starting defaults, change them

### How a thumbnail is proposed

- **Never propose a thumbnail in words.** Build it and show it, with the candidate titles captioned underneath each image, because the thumbnail and the title are one story.
- **Board captions come from the brief's recorded title candidates**, never invented at render time. A better title found mid-round goes back into the brief in the same session.
- **Deliver a labelled contact grid AND every individual full-resolution file**, every round. The grid is for comparing, the individuals are for judging faces and legibility.
- **One label per option, identical everywhere it appears**: in the image, the file name, the chat line and the board. Send files in label order. A later round continues the letters rather than restarting them.
- **The machine brings options, never the judgment.** A board describes what is there and lays options side by side. It does not rank or pick. Your picks are the data the system learns from.
- **A sub-agent that looks at thumbnails or frames runs on your most visual model.** Pulling and downloading can run on anything.

### What a board carries

- **A board is several different thumbnails, not variations of one.** Different concept, setting, composition and format per render. Variations of one idea only when asked.
- **Never reuse a setting because it won last time.** A winner is a data point, not a template.
- **Several categories side by side, every time**, allowed to conflict with each other. Suggested starting categories: a real frame from the video, the speaker looking at the camera, the speaker big on one side with a product screen as the headline, a faceless or word-only card, the speaker somewhere real (outside, at a desk). Add a category when one works; never let one replace the others.
- **The 1-of-3 rule.** Every thumbnail test carries at least 1 candidate that is a real frame from the actual video, the speaker talking to camera with what was on screen in that video visible. Not a recreation, not a staged still: the tape. Continuity between thumbnail and first frame is a credibility device.
- **The finish axis, picked per video, never a default:** polished (designed), raw (screenshot-grade), and handmade (deliberately imperfect, documentary). Caption each render with its finish.
- **Every build shows the pair** where an image model is used: the composited version (code, PIL, ffmpeg) and the model-finished version, side by side with the same label plus a suffix (`T1`, `T1-AI`). Once a layout is picked, the deliverable is the model-finished one and the code render becomes its brief.

### Words and composition

- **Big words or no words.** No small type, ever: no sub-line, eyebrow or tracked caption that cannot be read at feed size. Every word is headline-sized or it is not there.
- **Fewer words wins**, as long as the value is clear and the title complements it. Putting the whole title in the thumbnail is out.
- **Nothing may require a second look.** The instant-read test: would a stranger understand what this is about, instantly?
- **Not cluttered is the bar, not empty.** One central anchor, busy material pushed to the rim, nothing overlapping the words. Clean means boxes align and nothing blocks anything else.
- **Higher than average brightness and contrast.** A dark, moody ground still has to read punchier than the feed around it.
- **Thumbnail words must do one of 3 jobs:** make the problem clear, make the solution obvious, or create urgency. If they do none, they go.
- **Props, badges, receipts, mock screens and staged scenes tend to read as an ad.** The open loop and the familiar format live in the words and the face, unless a real asset (a real screen, a real board) is the picture.
- **Real logos only.** A product logo is the real asset, pixel-true, composited or passed as a reference with "reproduce exactly". A model-invented lookalike is a defect.

### Faces and real people

- **Every generated image of a real person points at a real photograph as its reference.** References live in `content/brand/people/`, photographs only. A face is never invented from a text prompt. Pass the reference images together, named ahead of the prompt.
- **The image model polishes the real frame and never changes an expression.** Design on the real frame in code first (crop, type, plates), then hand the model the original screenshot plus the design as the layout idea.
- **A wrong face is fixed from a real photo, never by editing the drifted face.** Pick the reference that already has the right expression and make it the image being edited. A degraded render never goes back in as a reference.
- **Edit passes chain off the last approved clean source**, in one batched pass carrying every correction. Stacked passes degrade skin into obvious AI texture.
- **When only the words are wrong, swap the words.** Same picture, faces untouched, no re-render.
- **When only the gaze must change, edit the eyes and paste back only the eye areas** with a feathered mask. Everything else stays the approved picture's own pixels.
- **Check every close face at full resolution** before it is shown: skin folds near the eyes, over-smoothing, a redrawn face. A redrawn face is flagged, never offered.
- **Compare every model-polished output to its source** at feed size and full size. Image models tend to zoom 10 to 15 percent and warm skin on a "clean only" pass, and they read and rewrite any legible text in a reference. Blur anything meant to stay blurred past legibility before the pass.
- **Two people on a thumbnail:** one line naming who is where before any label goes on. Left to right on the thumbnail is left to right on the tape.

### Sizes

- YouTube thumbnail: 1280x720.
- A custom thumbnail for a native feed video post: render it at the **video's own pixel size**, not just its aspect ratio. Some platforms refuse a smaller thumbnail and fail the whole post with a message that names nothing.
- YouTube draws the duration badge over roughly the bottom-right 300x130 of a 1920x1080 frame. Nothing that has to be read lives there.

## Mine

- Faces: <yes / no / whose>
- Expressions that are in: <for example "explaining, or a big smile">
- Expressions that are out: <...>
- Wardrobe: <what signals your audience at a glance>
- Maximum words: <a number>
- Colour: <beyond `content/brand.md`, any thumbnail-only rule>
- Instant rejection: "<your verbatim phrase for a thumbnail that is wrong>"
- Finish level: <one default / decided per piece>
- Arrows: <yes / no / some>

## Rounds and what they taught

<One dated entry per round worth remembering. Shape: what was on the board, what you picked, your words, the rule it became or "guideline, first instance".>

## Retro

A rule joins "Mine" only from your own pick or your own words. A starting default you disagree with gets struck through and replaced, never silently deleted.
