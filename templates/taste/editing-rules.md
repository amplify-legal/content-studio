> **`content/taste/editing-rules.md`** · written by you, in your own words, through the `taste-builder` skill (round 6) and promoted during real cut reviews · read by `long-form-editor`, `shorts-editor`, `cut-review`, `content`.

# Editing rules (the durable set)

> 3 sections, deliberately separate. Conflating them is how a one-off preference gets carried forward for a year as a default. Rules join "every edit" only when you promote them out loud during a real review.

## Starting defaults, change them

Generic craft rules that held up on a working channel. Keep, edit or strike each one.

1. **Tame loud close-mic moments.** A compressor before loudness normalisation (in ffmpeg: `acompressor`, then `loudnorm`).
2. **Give endings a beat of tail.** Never clip the last word. Trim at the waveform trough, not at the transcript boundary.
3. **The opening is on camera.** Frame-check the chosen open, not just the transcript.
4. **A live stays live.** Natural 1 to 3 second silences stay, no quick cuts. Cut only tangents, mistakes and dead air. A live recut into a designed presentation has lost what made it a live.
5. **Every visual change carries information.** Each cut, zoom or graphic advances the point. Motion for motion's sake fails.
6. **Music sits well under the voice and ducks when you talk.** Sound effects mark real transitions only.
7. **Cut for the best part, not only for the filler.** Before a cut is built, name the one thing a viewer saves it for (usually the prompt, the number or the line) and make sure it is in, reached fast. Setup that only leads to it gets cut.
8. **A second speaker stays only if they add something new.** Repetition of what was already said gets cut unless it is worth the seconds.
9. **Every section change gets a spoken or shown transition.** Wherever the video moves from one idea to the next (story to framework, one point to the next), a few seconds tell the viewer what comes next, what the insight is and why to keep watching. One sentence or one card per transition, never verbose. A cut that removes a section re-checks the joins on either side for a count or a promise the cut has broken ("four" said, "five" shown). Why: a real 9-minute cut jumped from a story to a numbered list with no bridge and the creator called the first 50 seconds "all over the place".
10. **Transition sounds sit between words, at a real screen change, and nothing synthetic.** Place the sound on the cut measured on the picture, centred in the speaker's pause, and skip a cut whose pause is under 0.3 s. Measure the pause on the speaker's own voice track (the quietest 0.2 s within 0.3 s of the cut, only where it is under about -28 dBFS), because transcript gaps lie and plan or section times drift up to 1.6 s from the picture. No click baked into a piece's start. A real recorded sound you picked, never a synthesised "page flip" or pop. Why: a sound landing in the middle of a sentence makes no sense to the viewer, and a baked-in pop landed up to 3 s into speech on a real cut.
11. **Sync is proven against the original tape, the way a player reads the file.** Never call sync fine by comparing a new cut with the last one: both can carry the same fault. For each camera stretch, find which tape moment the picture shows and which the sound plays, seeking by timestamp. Any audio pulled out of a cut is read by its timestamps (`aresample=async=1`), never sample by sample: joined tracks can carry hundreds of timestamp jumps, and reading straight through put the sound 0.77 s late by minute 4 on a real cut.
12. **A video card shows the video's real thumbnail, looked at before it is used.** A platform's preview image is not a thumbnail (some tools use the recording's first frame, which can be a browser start page). Open the image at full size before it goes on a card; a video with no real thumbnail gets no card, or one built from a real frame.

## Rules for every edit (mine)

<Promoted out loud during a real review. Each one dated, in your words.>

1. <...>

## Contextual taste, re-decided per piece

Filler words, motion-graphics intensity, card density, duration targets, banner placement and the look are decided in that piece's brief and its cut reviews, never inherited. <Any baseline for your audience, for example "motion without being flashy: no bounces, spins or glows".>

## Must never happen

- <...>

## How I like to be worked with

<Your words on collaboration. Starting defaults most people agree with, change them:>

- Find the things before I do. Come with options and questions before I give directions.
- Check more frames than feels necessary.
- Offer options, then let me pick.
- Bring discernment and flag doubts.
- Render it so I can watch it. Do not describe it to me.
- When something breaks, explain why, so it is prevented next time.

## Retro

Candidates sit here with the date and the piece until promoted. A per-piece choice (a named creator's style for one video, for example) is written as scoped to that piece, not as a default.
