# Workshop and training edit craft

> Installed to `content/reference/workshop-edit.md`. Covers a recorded live session with attendees: a video call or a livestream with a shared deck, a presenter or 2, a gallery of people who did not agree to be on camera, and a Q&A. Podcast episodes have their own file, `content/reference/podcast-edit.md`. A worked pipeline for exactly this shape is in the repo at `examples/workshop-edit/`.
>
> **How to read the numbers.** Every measurement below came off a real recording. Where something is a hypothesis, it says so.

---

## 1. The house defaults for a recorded workshop

These are the calls that shipped. Your host's own calls go in `content/taste/editing-rules.md`.

- **Attendees blurred, voices kept.** Every attendee tile and its name label is blurred, and any meeting-bot tiles (notetakers, recorders) go with them. The presenters stay sharp. Attendee voices, and first names spoken on tape, stay in.
- **The blur is soft, not a smear.** The point is to show the viewer there are other people in the room without showing who they are. Measured on one tape: a box blur of radius 16 in 3 passes on a 1756-wide frame keeps a person a person; radius 40 was a smear and was rejected. The name-label strip under every tile gets a **second, hard blur** so no label survives.
- **Captions on, every cut.** House karaoke captions (bold sans, 3 to 4 words, the current word in `{BRAND_ACCENT}`), burned before the speed pass. Spoken numbers render as numerals (65%, 9,000, 2.5 million), with the "one" exception below.
- **A slight speed-up, 1.05x, pitch preserved.** A training reads better a touch faster; a conversational episode can go to 1.1x. Both numbers are the host's to move.
- **2 cuts off one recording**: the full session for long-form, and a condensed cut (under 15 minutes) for social and possibly long-form too. Then the derivatives (see `content-waterfall`).
- **The condensed cut is rendered from a machine draft spine and the host subtracts after watching**, rather than shaping the spine on a table first.
- **Ready to post means the host does not review it.** When they say "make it ready to post", the loop is: render, watch every boundary and a 5 second contact sheet of the whole runtime, fix, render again, until nothing is left to fix.

## 2. What the tape looks like, and the fixes that follow

- **A local call recording carries the presenter's whole browser.** On one tape the browser bar showed a local file path and 2 private tab titles on every slide. **Crop below the browser bar, put the deck full frame, and put the presenter picture-in-picture.**
- **The gallery reflows** as people join and leave (3x2 for most of an hour, 3x3 for the 2 minutes a seventh person was in). Tile positions are measured per layout and the presenters' tiles are checked every 5 seconds before a render, never assumed.
- **Drop the pre-show.** On one tape that was the first 9 minutes. Open on the host's first real words ("good afternoon everyone, and welcome"), never on pre-show banter.
- **Video segments render without audio; the audio is cut sample-exact to each segment's real frame count at join time.** Frame-quantised segments drift otherwise: 118 of them drifted the audio by seconds.
- **The speaker's name is baked into the active tile**, so who is talking is on the tape. OCR the label at the midpoint of every segment and compare it with the transcriber's diarization. On one tape the diarization attributed the closing line, the button of the whole video, to the wrong person, and the tile said otherwise for every frame of it. Diarization is good enough to drive a layout and not good enough to trust on a hand-off. The same read confirms the order of a tile strip by its own labels instead of assuming it.

## 3. The opening of a condensed cut

- **An animated title with the voices running under it, no subtitle line, and the deck on screen within the first 15 seconds** even while people are still speaking.
- **The faces stay on the opening.** Never a still of the presentation where a face could be. The layout that came out of this: faces top left, the deck shifted right to make room.
- **The opener works because of the resolve, not the animation.** Render the opener into the exact slot the live footage will occupy and dissolve it onto a **real frame of what comes next**. The hand-off is then invisible and the only thing that changes at the cut is one face appearing. `examples/workshop-edit/opener.py` does exactly this.
- **When the tape cannot honour a house rule, put the trade to the host rather than bending the rule.** On a tape whose screen share did not start for 23 minutes, "deck within 15 seconds" was impossible. 3 priced options went to the host; they picked "cut the cold open to one story", which got the screen on at about 0:50 instead of 1:20.

## 4. How a sub-15 cut is composed

- **Pure subtraction, in the tape's own order.** Every version of one measured condensed cut ascended monotonically in raw seconds; nothing was ever re-sequenced. That is what makes "subtract after watching" tractable: the host can point at a minute and say drop it.
- **The draft rule: one unit per beat, plus the call to action.** The only things ever added were a rendered opener and one still frame.
- **Under 15 minutes.** A 12 minute target was a target, not a ceiling: finishing every slide build beat hitting the number, and 14 was right.
- **Every slide shows all its value, not every detail.**
- **Name what was dropped, in the handover**: "left out on purpose: the chat-reading moments, a tier list, 2 tangents, the whole Q&A. Those are yours to put back." A list of what is missing lets the host subtract in one word instead of re-watching an hour.
- **When finishing every build breaks the target, price the trade.** Name the slides that could come out, each with its duration in seconds. Without the priced list the machine silently cuts something the host wanted.
- **Predict the overrun.** Finishing every slide build cost 28% of runtime on one cut: 10 share units became 13, 35 segments became 43, 11:15 became 14:22.
- **Close on the viewer, not on the room.** A cut ending on a question to named people in the room ("so, what's on your mind?") is a question to people the viewer is not among. Move the end to a line that closes ("I think we're all aligned on that. Cool.").
- **End on the button.** One cut reached its real closing line, ran 42 more seconds and stopped mid-breath.
- **A condensed cut needs transition cards.** 12 of 33 real cuts on one audited cut jumped 17 to 330 raw seconds with no bridge, and 11 sat exactly on a chapter mark: each was a new teaching beat that needed announcing. A card is not a title slide. It answers what the viewer gets next, in 6 words or fewer, title case, **names its own subject** (never a verb plus "it" or "this"), and numbers are numerals.
- **A running chapter label can eat a third of the picture.** One layout put the current topic under the title top left and the next topic in the opposite corner, which freed the right column and made the faces bigger. Whether "next" helps retention is a hypothesis to test, not a rule.

## 5. Slides and builds

- **A cut never leaves a slide before its build finishes.** A slide reading "5 actions is all it takes" was cut before the fourth action appeared. The spine was picked off the transcript, and **a transcript cannot see a reveal.** Build the reveal timeline from the frames (`examples/workshop-edit/slides.py`) and extend any unit that ends inside a build to the last reveal and the end of the sentence.
- **A card the presenter never got to is the editor's to reveal, never to drop.** Where a reveal was clicked late, after the words, the cut shows the finished slide **as the words land**, off a real frame of it.
- **A stream's shared window is not always the deck.** On one livestream the browser shrank twice, zoomed out for about 45 seconds, and once showed a new-tab page with bookmarks and a local file path. Matching every half second of the share against renders of every build state of the deck finds all of them. Under about 8/255 mean difference, repair the corner a camera box covered from the matching render; 8 to 30, show the whole slide clean from the render; 30 and over, hold the last good slide.
- **Half-second sampling puts the wrong build on screen for up to 0.8s at every slide change** (28 changes on a 45 minute stream). Re-measure every change to the frame.
- **A stream's layout switch is a 0.4 to 0.6s crossfade, not a cut**: talk-to-deck fades before the switch, deck-to-talk after it. Measure each switch at full frame rate and hold the last clean frame, or the faces ghost inside the deck for 5 to 8 frames.
- **A slide-led short shows the slide for the point, not whatever was on screen at that second.** On one tape the agenda slide was still up while the presenter explained a different point; a faithful timeline put a picture on screen that contradicted the words. Give each short a per-piece slide pin.
- **A stream's own graphics fade over the camera at layout switches.** A piece that ends inside one freezes its picture and keeps the audio.

## 6. Repurposing for a different audience

- **Screen the pixels as well as the words.** A talk recorded for one audience was condensed for another. The spoken vocabulary screened clean across every unit; one phrase survived anyway because it was **printed on a slide** and on screen for 11 seconds. OCR every second of the delivered file for the other audience's vocabulary.
- **A 2-word change on a slide is a patch, not a re-render.** Measure the text's bounding box with tesseract TSV across the whole window (it drifted 4px on one tape), cover it, re-set the line in the same font and size, then OCR the rendered file to prove the old words are gone.
- **A drawbox fill is converted to limited-range YUV and comes back darker.** A card measuring RGB 253 patched with `0xFDFDFD` decodes to 250, and 3 levels on near-white is a visible block at 2x zoom. Encoder quality makes no difference, which proves it is the colour and not the encode. Only `0xFFFFFF` lands within one level. Measure fills by rendering candidates.
- **An RGB still laid onto a BT.709 tape is converted with BT.601 unless told otherwise**, which put a greenish box on 38 of 45 minutes of deck (242/242/230 against 246/243/238). Convert every PNG patch or slide with `scale=out_color_matrix=bt709:out_range=tv,format=yuv420p` and measure the rendered frame against the pixels beside it.

## 7. The blur, and the measured failures of blurring a moving recording

Blurring people out of a moving recording fails in more ways than it looks. Every row here cost a render or leaked something.

| Failure | Rule |
|---|---|
| **A layout hand-off timed to the half second** | The share was written down at 645.5 and actually started at 645.88. Those **10 frames put raw, unblurred attendee faces** into the deck slot, and the host saw it as "a weird flicker around second 26". It was a privacy leak wearing a cosmetic costume. **Measure every hand-off to the frame**, by frame difference across the second around it. This is a different fault from the push-in shimmer in section 9; the same word described both. |
| **A layout seam that moves mid-tape** | A shared screen 1669px wide until about 29:30 and 1621px after it, because a participant strip widened. A crop fixed at the first measurement leaked 48px of attendee tiles across the whole back half. Measure the seam every 10 seconds, take the **narrowest** value for the whole cut, and lose window chrome instead. |
| **An exposure check sampling every 5 seconds** | A **1.8 second exposure** of a private list survived an OCR sweep at 5 seconds. **Exposure checks sample at 1 second or finer.** |
| **Over-blur** | A sidebar detector fired on any numbered list, so 95% of the blurred runtime had no sidebar on screen: **about 90 of 800 seconds** of teaching content was smeared, the worst 27 seconds of the closing answer. A blur with nothing behind it is a fault, not a safety margin. |
| **Hand-editing blur windows off an audit list** | Removing the false positives by hand then dropped a window over a genuinely open sidebar listing 15 private conversation titles. **Derive the windows**: OCR each band at 2 fps across every kept second and emit a window only where private text is actually legible. On that tape: 7 windows totalling 70 seconds, against a hand list with 142 seconds of blur over a closed sidebar. |
| **`boxblur` radius caps** | **ffmpeg's `boxblur` caps silently**: `luma_radius` must be 24 or less, and `chroma_radius` must be at most half the chroma height of the region being blurred (on a 48px name strip in 4:2:0, that is 12). Exceeding either fails the render with no useful message. 2 render failures paid for this. `examples/workshop-edit/build.py` validates both before it renders. |
| **A filter tuned by re-rendering** | **Probe a filter as a PNG first.** The final blur radius was chosen from 2 still probes, not 2 renders. |
| **A seeked input composited onto a looped background** | The seeked input carries the tape's timestamps, so the overlay reads the background's clock, the tile frames are permanently in the future, and the output is a bare background with no people. **ffmpeg exits 0.** Every overlaid input chain starts with `setpts=PTS-STARTPTS`. |

**The rule these add up to: when a workspace surface (your own screen, an app, a dashboard) has to appear on camera, rebuild it clean and record the rebuild, rather than blurring the real page in motion.** Copy the real page's file so the layout is identical, replace every person with who they are ("a podcast host"), drop client names, replace every figure with one of the same shape, then record that copy. A still has none of the failures above, because one frame is checked once. Before recording, read the copy's **rendered text** (not one tag: titles in a styled class are invisible to a heading grep) and its **HTML comments** (a build comment can carry paths and names one right-click from the audience). Attendees in a recorded call cannot be rebuilt, so for them the blur stays, with every rule above.

## 8. Captions on a long cut

- **Pin the karaoke base colour or the highlight runs backwards.** Emitting `{\t(k0,k0+40,\c<accent>)\t(k1,k1+60,\c<white>)}word` makes libass resolve the first transition's target for any time before its start, so a line arrives with every word highlighted and the colour drains as the words are spoken. Proved on a bench render: 0.2s into a 4 word line, all 4 were highlighted. The fix is one token, `\1c&H00FFFFFF`, pinned before the transitions. It was the first thing the viewer's eye caught.
- **Never let a word count do the line breaking.** A hard 4 word cap put 524 of 705 lines at exactly 4 words and read "So I was in / an instance where, a / firm was trying to". Break where language breaks: score every candidate boundary (sentence end, clause, a real pause, a speaker change) and choose the whole set with a shortest path, not greedily. Greedy leaves 3 word fragments after every forced break.
- **"one" is a pronoun.** A numerals rule that converts it shipped "the big 1,", "see them 1 by 1" 15 times in one cut. A small number becomes a digit only when it is part of a larger number or a unit word follows it.
- **Finish the sentence, then cut.** Of 33 cuts on one audited cut, 13 left mid-sentence, 12 landed mid-sentence and 8 fell inside a word. 5 caption cards welded 2 different sentences into one line.
- **A caption filter keyed on the word's END drops audible words at a cut.** The transcriber attaches the following pause to the word (one word spoken at 595.3 was reported to 596.54), so a cut on measured quiet at 595.79 left it fully audible and the caption builder threw it away. **Keep a word whose START is inside the segment**, and let its highlight run through a contiguous seam.
- **Crosstalk and backchannels** ("yes", "I see" said under the other presenter's sentence) are the main caption fault on a 2-presenter session. Read every caption against who is speaking.

## 9. Cut boundaries, in numbers

- **The silence gate:** silences of 1.0s or more are tightened to 0.6s by leaving 0.3s each side; a machine-gun guard merges any fragment under 1.2s into its neighbour, never across 2 keep ranges.
- **A pause is cut only between 2 transcript words**, where at least 0.6s of the gap is measured quiet. A silence map alone clipped 5 quiet words in a 9 minute cut.
- **The boundary gate:** snap to **measured audio energy**, not to the transcriber's word spans (they hang the trailing pause on the word, so snapping to a span puts the dead air back). 20ms RMS windows on 16kHz mono, threshold -38 dBFS, 3 consecutive quiet windows, walking outward in 20ms steps, capped at 1.5s, 0.05s pad. Only real cuts move; a seam where the next unit starts exactly where this one ends is continuous audio and is left alone. `examples/workshop-edit/boundary.py` implements this.
- **Read the rendered captions back across every join.** A corrected opening cut at 610.00 sliced a word in half; the plan looked right and the deep pass was green, because neither checks whether a word survived. The boundary moved to 610.55.
- **When the host gives a timestamp, trust it to the frame.** "Second 21" became a boundary at 595.6. "A flicker around second 26" was 26.4s, and it was the 10-frame leak above.
- **`silencedetect` returning nothing means a noisy room**, not a clean cut. Diagnose at -35 or -30 dB; never drop a clean tape's threshold toward -30, because it eats soft word endings.

## 10. Layout

- **A picture-in-picture hard-wired to one person lies about who is talking.** For 3 minutes 32 seconds of a share the only face was one presenter's, including about 48 seconds of the other one teaching. The layout follows the voice.
- **Equal boxes give the loudest real estate to whoever is silent.** Check who actually speaks in the **kept** material before designing. On one cut a person who never spoke once held an equal box through the whole opening.
- **The tile is the ceiling.** A 384x216 gallery tile upscales cleanly to 2x, acceptably to 2.5x (960x540), mushily at 3x.
- **Use the space.** Empty space on a frame is wasted: the title can be bigger and the faces can be bigger.
- **A still of a speaker taken from the recording reads as frozen video.** Where the tape has no footage of someone speaking, use a portrait-shaped photo (4:5, mouth closed, eyes to camera, name and title beside it). Look in your own archive first; a clean frame from the same tape is the last resort, and say which it is.
- **A still holds still.** Never put a slow push-in on a card or a photo: `zoompan` resamples by a fraction of a pixel every frame and flat ground, type and faces shimmer. Measured: median 11 levels of per-frame change with spikes to 223, against 0 to 2 once the still was left alone. Test with `crop` above the caption band, then `tblend=all_mode=difference,signalstats`, and read YMAX: a still sits at 0 to 2.
- **The preview renders through the shipping path, or it lies.** 3 layout candidates were judged with a mock caption in plain white while the real captions were coloured the whole time. One module holds every number, and a preview frame is produced by the shipping segment function itself. `examples/workshop-edit/build.py probe` works this way.

## 11. Render and review

- **Any timestamp handed to a human comes off the delivered file.** Chapters derived from a 1.0x edit list are 5% late at 1.05x, over 2 minutes by the end of a 46 minute cut. Caught with 34 wrong chapter lines already drafted. Divide by the speed factor in the generator and check the result against the delivered file.
- **Re-render only the segments a change touches**, and delete the segment cache deliberately on a **geometry** change. When only the blur changed, every deck segment was kept and an 11 minute and a 46 minute cut both came back in 12 minutes.
- **"The render finished" is not "the change landed."** One version came back byte for byte identical to the previous one; the cause was 2 identical keys in one Python dict, so the edit landed in the block Python discards. Compare every output against the previous one.
- **A `drawtext` label containing a colon silently fails the whole filter.** Escape it (`00\:30`).
- **Watch for dead air and frozen picture**: neither shows up in the usual checks. One cut carried 4.7 seconds of digital silence (-74 dBFS while a spinner loaded) and a 101 second stretch where the share never changed; 41.6% of the runtime sat in runs of 10s or more with nothing moving. Run `silencedetect` on the delivered file, flag any silence over 1s, and measure how long the picture goes without changing.
- **A repo-wide `git add` from an edit folder sweeps hundreds of MB of renders** (one run made 331 MB). Ignore render folders in `.gitignore` and stage by explicit path.

**How to review, since a 100 frame board catches none of this.** One dense pass **per vector**, each with its own sampling rate, and an independent reviewer per vector so nobody marks their own homework:

| Vector | Sampling |
|---|---|
| Captions | 1.5s, suspect stretches at 0.4s, the karaoke itself at 0.04s |
| Every seam | -0.6, -0.2, +0.2, +0.6s around each join |
| Blur | 1s inside every window, 3s outside |
| Layout | Every speaker change |
| Pacing | 2s across the whole runtime |
| Audio, alone | The whole file. On one review this pass found dead air and a 2.2 LU speaker imbalance after 5 visual passes missed both |

Then a person watches it. Green is not done. The end-of-run review is a separate reviewer that reads the whole conversation.

## 12. Reading a build session back later

If you mine a past Claude conversation for the host's rulings, know that a host's mid-turn messages are often stored as queued-message records that a digest renders as a bare "system event". Parse those records directly, or you will find none of the host's words and conclude the machine decided everything itself. And count primary sources, not hits: most hits for a quoted ruling are later sessions reading this file back.
