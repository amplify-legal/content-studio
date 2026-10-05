> **`content/taste/story-animations.md`** · written by you, in your own words, through the `taste-builder` skill and your animation reviews · read by `media-gen`, `long-form-editor`, `shorts-editor`, `content`, `on-camera-board`.

# Story animations

> The visual half of a video: animations that are the visual aid of what is being said, at the moment it is said. **Never call these "b-roll".** That word means mood footage running under narration, and a session that says it has already misunderstood the job.

## Starting defaults, change them

These are guidelines from a working channel, not settled craft. Keep what fits, rewrite what does not.

### The centre of it

**Point at the sentence in the script that the animation illustrates.** If you cannot, it is probably b-roll.

### 4 attempts that teach the difference

| Attempt | What gets built | Why it fails or works |
|---|---|---|
| 1. Mood | Abstract objects, atmosphere, a building leaking light | Explains nothing. |
| 2. Mechanism metaphor | Cubes into a tray standing for hours, a bar sliced at gates | Looks expensive and feels like an explanation, but the viewer has to decode cube = hour. Decoding is not learning. The dangerous one, because it reads as progress. |
| 3. Cinematic world | A photoreal place where something analogous to the claim happens | Still b-roll. Beautiful, on-sentence, and teaches nothing countable or proportional. |
| 4. The arithmetic, made physical | One working day as a bar, the small daily loss as its true fraction, the days counted, the total measured back against the bar | The right direction. The craft (legibility, not confusing the eye) is the open problem. |

### What a visual aid is

The source material for an animation is **a line of the script**, not a concept.

| Script line | The visual aid |
|---|---|
| "<15 minutes a day adds up to a full working day every month>" | the arithmetic assembling, the minutes accumulating into a day |
| "<3 out of 10 visitors leave before the page loads>" | 10 visitors, 7 staying, 3 dropping |
| "<a typical subscription loses 9 cents of every dollar to fees>" | a dollar arriving as 91 cents, the missing 9 visible |

Abstraction is allowed inside that, in how beautifully the dollar or the hour is rendered. It is never allowed to replace it.

### Before writing any prompt

1. Quote the exact sentence from the script it serves, at the top of the prompt file.
2. Say what a viewer must understand after 8 seconds, in one sentence.
3. Only then describe the shot.

If step 1 is missing, do not render.

### 4 tests every animation passes

1. **Highly relevant.** It illustrates the specific claim in the specific sentence. If it would work under a different paragraph, it is too generic.
2. **Immersive.** The viewer is inside the idea, not looking at a chart of it.
3. **Sophisticated and modern.** No template motion, no bounce eases, no stock icons, no clip-art metaphors.
4. **It explains with the sound off.** Mute it: can a viewer still get the quantity, the proportion, the change? This is the test that kills pretty work.

### 3 properties worth trying

- **Countable.** Discrete units the eye can count. "Streams of light" are uncountable and drift toward decoration.
- **Proportional.** Sizes carry the arithmetic.
- **Resolved.** Before and after visible in the same frame, so the change is seen rather than remembered.

### Working practice

- **Sequence beats mood.** A beginning, a turn and a consequence. State the 3 beats before the prompt.
- **Numbers belong to one surface.** If the on-camera board carries a figure, the animation does not repeat it. In a short with no board, the animation may carry it.
- **Silent by default.** Generate without audio where the model allows it, mute where it does not.
- **Match the palette** in `content/brand.md`, so the cut needs no grade.
- **Real product footage or a real screen capture is allowed.** It is the actual thing being discussed, not generated mood.

### Which tool for which job

- **Where meaning lives in exact quantity, render it deterministically** (HTML, code, frame-exact image rendering). A generative video pass tends to keep the look and rebuild the structure, which eats the proportion.
- **A screen or UI is almost always HTML.** A generative model regenerates every pixel, including the text you handed it, so on-screen text gets rewritten or duplicated. Rebuild the screen in HTML and animate it. If you must generate, crop tighter or start from a frame that already holds the final text.
- **Generative video is right where precision carries no meaning**: depth, light, atmosphere. Route it through `media-gen`.
- **Pass a deterministic version of the same beat as a video reference** when the model accepts one. It hands over the beat structure and the colours.
- **Video-model edit requests have quiet traps.** Common ones: the output takes the reference's aspect ratio, the requested duration must match the reference exactly, a re-uploaded reference under the same storage name may be cached, and the real error detail can sit deeper in the response than the top-level error field. Check `content/reference/media-gen.md` for the ones known for your model.

## Mine

- What a good animation looks like to me: <your words, with a reference>
- What I have rejected and why: <dated entries>
- My palette or style notes beyond `content/brand.md`: <...>

## Retro

Dated entries, with the animation and the sentence it served.
