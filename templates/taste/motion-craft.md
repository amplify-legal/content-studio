> **`content/taste/motion-craft.md`** · written by you, in your own words, and changed on your animation reviews · read by `media-gen`, `long-form-editor`, `shorts-editor` and any HTML or HyperFrames composition builder, before the timeline is written.

# Motion craft: how an animated piece should move

> Taste is data; builders read this and never restate it. Scope: story animations, title cards, intros and explainers built as HTML compositions (for example with HyperFrames and GSAP). A shorts builder's animated cards may keep their own snippets until you decide these moves reach the shorts too.
>
> The lines below are **starting defaults** from a working lab where each one was rendered, measured frame by frame and judged. Keep, change or strike each one.

## The 5 moves

1. **Springs, not curves.** Every move uses a closed-form spring ease (a damping ratio and a natural frequency, not a bezier). Starting values that held: type at damping 0.9, frequency 16; interface elements 0.78 and 14; cards 0.85 and 10; fades and exits critically damped. Type never visibly overshoots; interface may by about 2%; exits and opacity never do. No power, back, bounce or elastic eases. Why: a spring settles the way a physical thing does, and a back or bounce ease reads as a template.
2. **Overlap.** Each element starts before the previous one settles. A group arrives within about 0.5 s in total.
3. **One shape, never cut.** When a state changes, the same element changes size, radius and fill (a clip-path inset with a radius) and its content swaps behind a short blur (about 14 px, 0.16 s). No crossfade between scenes unless the scenes share nothing.
4. **Hand off at identical geometry.** When something becomes something else (a title becomes a slide headline), it travels to the target's exact position and the target fades in underneath at the same geometry. Measure the landing from a snapshot: within 2 px.
5. **A camera.** A world wrapper with a slow push across a hold (1 to 3%), pulling back as the next state lands. A layer that should sit behind moves about half as much.

## Optional, by case

- **Shutter blur on travelling text only**, never on text meant to be read at rest. A setting that measured well: shutter angle 180, phase -180, 24 samples per frame. What failed and why: 360 with 16 samples drew stepped dark copies that read as a drop shadow; 48 samples tinted the smear; the default phase left the smear as a detached copy trailing the word; a phase of -90 froze a clip-path tween for about 0.4 s in 3 renders of 3 (it is the only setting whose window reaches ahead of the frame; keep the phase at most minus the angle). Render cost measured as none (11.6 s with blur against 11.3 s without). A blur target must have no animated children and its mask must be `position: relative`.
- **Text behind the subject:** remove the background on a 1080p source; stack footage, dim layer, type, cutout. The dim is its own layer, never inside the video's wrapper (the injected video frame paints over it). Pick a word or a height the subject's head cannot cover.
- **Sound on the grid for standalone stings only:** the hits live in one beats file that both picture and sound read. Story animations under your voice stay silent.

## The process

1. If there is a reference, take its grammar (palette, type, shot length, transitions, camera, how text enters and exits), never its content.
2. Write the state list on the beat grid before any code: time, shape state, content, sound, spring.
3. Snapshot the opening, the signature move and the final hold; look at them at full resolution and fix the worst thing before anyone sees it.

## Known traps

- Clip-path numbers carry no trailing zeros ("456px", never "456.00px"), or GSAP snaps the tween instead of animating it.
- Address blurred elements by id: the blur copies keep their classes.
- A word waiting under a line mask sits fully below it (140%, not 108%), or its glyph tops float on the page.
- Content leads the container: lines start moving before the card edge grows (about 0.06 s), or they poke out.
- One root composition per project: a variant goes in its own project folder.
- Intentionally hidden text (behind a cutout, inside a mask) needs the framework's occlusion allowance, or its layout check fails.
- A frame check that sends each frame to a vision model can cost money silently when a key is set in the shell; turn the description off for a plain frame check.
- Run the framework's CLI with telemetry and skill auto-updates off; one render's CLI hung for 10 minutes after writing a complete file with them on (cause untested).

## Mine

- <your own changes to the defaults above, dated, with the piece that taught each one>
