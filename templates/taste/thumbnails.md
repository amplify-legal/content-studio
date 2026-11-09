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
- **Before any round, pull the channel's live thumbnails into one sheet and match the register**, so the first round is already in the family (`yt-dlp --flat-playlist` on the channel, then each video's `hqdefault.jpg`). A thumbnail built in another surface's register (a calm white social cover, a serif lockup) reads wrong in a YouTube feed even when it was right where it came from.
- **When a style is borrowed from a public creator, rebuild against the original.** Pull the creator's real thumbnail that the style came from, put it beside each iteration, and make about 3 iterations per style. Borrow the element (a box, a pill, a cut-out), never the whole style.
- **Before a top set is shown, polish every candidate against every note in this file**, live notes and chat notes alike. This file is that list; read it whole before the polish.
- **The editor brings a top 5 and the creator picks 2 to test.** A specialised long video rarely gets the views to settle more than 2.
- **Once a round has a house style, build it with a script, never as raw frames with a caption.** The script takes the house layout as the code brief, places people by face size with the chin a set distance above any plate, runs the model finish (2 takes, the brief as image 1, the real frames as pose, real photos for identity), runs the chin check, and builds a board of the top 5 plus the real-frame and real-photo options. Then the round does not depend on which model or session runs it.

### What a board carries

- **A board is several different thumbnails, not variations of one.** Different concept, setting, composition and format per render. Variations of one idea only when asked.
- **Never reuse a setting because it won last time.** A winner is a data point, not a template.
- **Several categories side by side, every time**, allowed to conflict with each other. Suggested starting categories: a real frame from the video, the speaker looking at the camera, the speaker big on one side with a product screen as the headline, a faceless or word-only card, the speaker somewhere real (outside, at a desk). Add a category when one works; never let one replace the others.
- **The 1-of-3 rule.** Every thumbnail test carries at least 1 candidate that is a real frame from the actual video, the speaker talking to camera with what was on screen in that video visible. Not a recreation, not a staged still: the tape. Continuity between thumbnail and first frame is a credibility device.
- **The finish axis, picked per video, never a default:** polished (designed), raw (screenshot-grade), and handmade (deliberately imperfect, documentary). Caption each render with its finish.
- **Every build shows the pair** where an image model is used: the composited version (code, PIL, ffmpeg) and the model-finished version, side by side with the same label plus a suffix (`T1`, `T1-AI`). Once a layout is picked, the deliverable is the model-finished one and the code render becomes its brief.
- **A two-person (podcast or interview) round has 3 kinds of option:** model edits of the real frames with every face unchanged (checked at full resolution against the frame), 1 option built from the real frames with no model edit, and 1 built from real published photos of the people. When a guest's published portrait carries the face, it reads as that portrait's year, so run a take with the face from the recording beside it and say on the card which one it is.
- **A live replay's thumbnail is the live event's own announcement card**, with the date swapped for "Full recording". It already carries the title, the real faces and the brand, and people who saw the event recognise it. Never ship it with the live date on it.
- **A deck screenshot as the hero reads as a slide, not a promise.**

### Words and composition

- **Big words or no words.** No small type, ever: no sub-line, eyebrow or tracked caption that cannot be read at feed size. Every word is headline-sized or it is not there, step labels included.
- **A thumbnail line is 3 to 5 words, and the type fills the frame.** A starting floor: the fitted type is at least 20% of the canvas height (144 px at 1280x720). Lines of 6 to 8 words fitted at 108 to 126 px on a 720 canvas against 174 to 198 px for the short ones, and the long ones could not be read. A longer thought is rewritten to its short form, never squeezed to fit. A builder that refuses a line under the floor, and says how many words it tried to fit, keeps this from depending on memory.
- **Serious, blocky type.** No handwriting or comic-style faces on a thumbnail.
- **Fewer words wins**, as long as the value is clear and the title complements it. Putting the whole title in the thumbnail is out.
- **Nothing may require a second look.** The instant-read test: would a stranger understand what this is about, instantly?
- **Not cluttered is the bar, not empty.** One central anchor, busy material pushed to the rim, nothing overlapping the words. Clean means boxes align and nothing blocks anything else.
- **Higher than average brightness and contrast.** A dark, moody ground still has to read punchier than the feed around it.
- **Thumbnail words must do one of 3 jobs:** make the problem clear, make the solution obvious, or create urgency. If they do none, they go.
- **Props, badges, receipts, mock screens and staged scenes tend to read as an ad.** The open loop and the familiar format live in the words and the face, unless a real asset (a real screen, a real board) is the picture.
- **Real logos only.** A product logo is the real asset, pixel-true, composited or passed as a reference with "reproduce exactly". A model-invented lookalike is a defect.

### Faces and real people

- **Every generated image of a real person points at a real photograph as its reference.** References live in `content/brand/people/`, photographs only. A face is never invented from a text prompt. Pass the reference images together, named ahead of the prompt.
- **An AI-edited picture of a person is not a thumbnail photo**, even one approved for a social cover: that approval covered that cover. The thumbnail photograph is a real frame of the real people.
- **Thumbnail boards render on the best image model, not the cheap one**, because the cheap model's face and logo fidelity cannot be judged.
- **The image model polishes the real frame and never changes an expression.** Design on the real frame in code first (crop, type, plates), then hand the model the original screenshot plus the design as the layout idea.
- **A wrong face is fixed from a real photo, never by editing the drifted face.** Pick the reference that already has the right expression and make it the image being edited. A degraded render never goes back in as a reference.
- **Edit passes chain off the last approved clean source**, in one batched pass carrying every correction. Stacked passes degrade skin into obvious AI texture.
- **When only the words are wrong, swap the words.** Same picture, faces untouched, no re-render.
- **When only the gaze must change, edit the eyes and paste back only the eye areas** with a feathered mask. Everything else stays the approved picture's own pixels.
- **Check every close face at full resolution** before it is shown: skin folds near the eyes, over-smoothing, a redrawn face. A redrawn face is flagged, never offered.
- **Compare every model-polished output to its source** at feed size and full size. Image models tend to zoom 10 to 15 percent and warm skin on a "clean only" pass, and they read and rewrite any legible text in a reference. Blur anything meant to stay blurred past legibility before the pass.
- **Two people on a thumbnail:** one line naming who is where before any label goes on. Left to right on the thumbnail is left to right on the tape.
- **Two people on a pair thumbnail look toward each other at about 45 degrees, and no name plate or headline covers a face or a chin.** Measure it: the gap between each chin and the top of the plate or headline below it; under 20 px at 1920x1080 fails.
- **Identity comes from how the person looks now.** An image model reads old brand photos as identity: a year-old photo with a full beard drew a person older and bearded who had short stubble on the recording. For a thumbnail, the recording frame of that video is the identity reference; a model pass may only sharpen it.
- **Skin folds near the eyes on a generated face are rebuilt, not retouched.** Pass the finished render plus the 2 real reference photos, ask for the same image with only the face re-rendered to the photographs (no folds, no plastic smoothing), make 2 takes and compare the eye region at full resolution: of 2 takes, 1 tends to come back over-smoothed and younger. Overlays (dates, tags) go on afterwards in code, so the cleared face is the one that ships.
- **A real frame of a call or a live stream is picked by scanning every second**, not from a contact sheet at 30 s: 1 frame a second across every face-to-face stretch, then each person's best moment at full resolution (natural smile, eyes to camera, mouth closed or a real laugh), composited per tile if needed. The goodbyes at the end are where everyone smiles.
- **Two real photos on one thumbnail are matched on the skin, in colour, never on a brightness number.** Take the skin pixels inside each person's cut-out (a YCrCb skin range inside the cut-out's alpha), compute their Lab mean and spread, and move one image's skin statistics onto the other's, or both to the midpoint (a Reinhard transfer). A brightness mean is not a check: a gamma lift that equalises a number drains a warm face to pale, and a bright backdrop pulls a frame mean up while the face stays dark. Two passes that matched a luminance mean reported "even" while the faces plainly differed. Look at the 2 faces side by side at the same size before saying they match, and say what was measured.
- **Cut-outs:** a human-segmentation model kept the wall behind a person; a portrait-specific matting model (for example BiRefNet portrait) did not. Check the edge at full resolution.
- **A face at 720p on the tape is a pose reference, not a face reference.** A small video tile cannot hold a face; use it for the pose and a real photo for the face.
- **When a person asks for an AI edit of their own look** (styling, looking older or more polished), build it from the real frame plus 2 or more real photos of them, keep anyone else unchanged, and show labelled options. Their own look is theirs to change; another person's face is never edited without that person's word.

- **An edit the creator asks for changes only what they named, and a pixel diff proves it** (2026-09-23 on a working channel, ported 2026-11-07). The edit is made on the exact file they picked, never a fresh render of it. Before it is shown, a diff against the picked file shows every changed pixel inside what they named (a capital letter in a headline: every change inside the headline line, 0 changed pixels anywhere else). Re-render the untouched source first and check it comes back byte-identical, so the diff is the edit and nothing else.
- **A model twin of a real frame that changed an eye, a mouth, a tilt or the framing is not offered.** On one round 6 polished twins were built from real frames and every one moved something on a face; all 6 stayed in the build folder and the real frames went on the board (2026-11-05).

### Sizes

- YouTube thumbnail: 1280x720.
- A custom thumbnail for a native feed video post: render it at the **video's own pixel size**, not just its aspect ratio. Some platforms refuse a smaller thumbnail and fail the whole post with a message that names nothing.
- YouTube draws the duration badge over roughly the bottom-right 300x130 of a 1920x1080 frame. Nothing that has to be read lives there: no name plate, no word, no face. A builder that places plates should keep their right edge clear of it.

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
