---
name: long-form-editor
description: >-
  Take a long raw recording and get real content out of it. A 90 minute Zoom call, a single camera
  pointed at a room, a screen share with a webcam column, a recorded training, a livestream with a deck,
  a recorded interview or a podcast episode. Covers the whole path: getting the tape in, transcribing it with key terms, knowing
  what is on it before cutting, the privacy pass, picking the moments, the cuts that make a raw
  recording watchable, multiple people on one camera, the finish, and what comes off the recording
  afterwards. Use when someone says "I have a 2 hour Zoom and no idea what to do with it", "cut
  this training down", "make this recording watchable", "edit this long form", "condense this
  call", "edit the podcast episode", or hands over a long raw file with no instruction attached. NOT an auto-clipper: a person
  picks every moment. NOT for a single picked clip (that is shorts-editor). NOT the review gate
  (that is cut-review). NOT for deciding what to record.
---

# Long-Form Editor

**Load before any step:** `content/PRINCIPLES.md` (the constitution: it wins over every step here), then `content/reference/long-form-lessons.md` (the taste and the errors table for this lane), then `content/reference/lessons.md` (the rules that cross every lane, publishing included), then their `content/taste/editing-rules.md` and `content/taste/editing-checklist.md`. Load the lane file that matches the tape as well: `content/reference/workshop-edit.md` for a recorded session with attendees and a deck, or `content/reference/podcast-edit.md` plus `content/reference/podcast-edit-runbook.md` for a conversational episode.

**The thing this exists to stop.** Somebody has a 90 minute recording and treats it as raw material they cannot use, so it sits on a drive and the week produces nothing. A raw recording is not an impediment. It is the cheapest content you will ever have, because the hard part, saying the thing out loud, already happened.

> Work inside one folder per recording, `content/videos/<slug>/`, with `raw/` (untouched files), `build/` (scripts, transcripts and everything they produce, including `build/review/` for frames you look at) and `renders/` (the files people watch).

**Every command below is one you can run directly**, and the Python snippets are short enough to paste. **A worked, config-driven pipeline for a recorded workshop** (plan, probe, render, captions, finalise, chapters, the boundary snap, the slide-reveal timeline, the deep pass and a handover page) is in the repo at `examples/workshop-edit/`. Copy it into the recording's `build/` folder, fill in its `config.json`, and adapt; its README says which parts are tape-specific. What you reuse from elsewhere in the pack is named by path at the point of use.

---

## The law, in 3 lines

1. **The transcript is a search index, never evidence.** It does not know who spoke, when the voice actually starts, where the silence is, or what is on screen. All 4 are settled by measuring the audio or by looking at frames. This is the same law `shorts-editor` opens with, and it gets worse at length, not better: at 90 minutes nobody is spot-checking.
2. **A person picks the moments.** This skill never scans a recording for "best moments". If nobody has picked, stop and ask. The judgment is the point of having a person.
3. **The tape settles the layout.** Who is talking, what is on screen, when a slide changed, where the window edge is: all of it is in the pixels and none of it needs to be inferred. Measure it.

---

## Step 0: get the tape in, and know what it cost you

Ask which of these it is before anything else, because the answer decides half the pipeline. Every row here was worked with except the last one.

| What they have | What it gives you | What it costs you |
|---|---|---|
| **A call recording with one file per participant** (some meeting tools export this) | Already aligned tracks, so one shared timeline where every cut hits every feed. Per-person audio, so you can gate silence per speaker and clean one person's mic without touching the other's. The easiest shape there is. | Nothing. Start here when you have the choice. |
| **A cloud recording of a call** | Usually one mixed video with the platform's own layout baked in, plus separate audio if you are lucky. Speaker names are often burned into the active tile, which is a gift: who is talking is on the tape. | The layout is not yours any more. Gallery tiles reflow when people join and leave, so the crop you measured at minute 5 is wrong at minute 40. |
| **A local recording of a call** | Higher bitrate than the cloud copy, and it captures the presenter's whole screen. | It captures the presenter's **whole screen**. Browser chrome, tab titles, file paths, notifications. See the privacy pass. |
| **A screen share with a webcam column** | The clearest material to cut: a deck full frame, one face in the corner, and a structure the slides already give you. | Everyone in the webcam column is on camera without having agreed to be. Cropping the column off is usually the whole fix. |
| **A single camera pointed at a room** | One angle, usually wide, usually with more of the room than you want. | No second angle, no per-person audio, and whoever is off mic stays off mic. Punch-ins become your only shot variety. |
| **One mixed audio track** | Simple. | You cannot separate voices. One person's boom, one person's room tone and one person's clipping all have to be fixed on the same bus, and a fix for one hurts the others. |

Then, before anything is planned:

```bash
ffprobe -v error -show_entries format=duration,bit_rate -show_entries stream=codec_type,width,height,r_frame_rate,channels -of default=noprint_wrappers=1 raw/tape.mp4
```

**Look at what it tells you, do not skim it.** A file reported as 1920x1080 can carry a rotation flag that makes it vertical on decode. Extract one frame and look before you crop anything:

```bash
ffmpeg -v error -y -ss 60 -i raw/tape.mp4 -frames:v 1 build/review/frame-0060.png
```

**You end this step looking at a real frame of the recording**, and knowing its true duration and dimensions.

---

## Step 1: transcribe, with the names in the transcriber

`shorts-editor` ships the transcribers and this skill uses them as they are. **The engine order is fixed: ElevenLabs Scribe `scribe_v2` by default, Deepgram `nova-3` as the declared fallback, local whisper last.**

```bash
# 1. the default: Scribe scribe_v2 with the tape's own key terms (ELEVENLABS_API_KEY)
python3 .claude/skills/shorts-editor/scripts/transcribe.py raw/tape.mp4 --edit-dir build --language en --keyterms-file build/keyterms.txt
# 2. the fallback, when Scribe is out of credits, keyless or down (DEEPGRAM_API_KEY): same key terms
python3 .claude/skills/shorts-editor/scripts/transcribe_deepgram.py raw/tape.mp4 --edit-dir build --language en --keyterms-file build/keyterms.txt
# 3. last resort, no network and no key: takes no key terms at all
python3 .claude/skills/shorts-editor/scripts/transcribe_local.py raw/tape.mp4 --edit-dir build --language en
```

**The engine that ran is named in the output file's own header**, never inferred and never a silent default. If the Scribe key is missing, say so before the first caption burn, not after somebody's ear finds a mangled name. On the one tape all 3 engines ran on, the confirmed proper-noun sites scored 17/17 (Scribe with key terms), 16/17 (Deepgram with key terms) and 11/17 (whisper); bare Deepgram with no key terms scored 12/21 on another tape where both APIs with key terms scored 21/21. The key terms are most of the difference.

**2 things about Deepgram output:** its word ENDS are not acoustic offsets (90% of its inter-word gaps are exactly zero, so a word's end is really the next word's start), so cut on word starts; the script snaps ends to measured energy by default, which removes a 45ms late bias. And it writes numbers as words where Scribe writes digits, so captions built on it need a number pass. Never burn a named caption from its diarization.

**Names go into the transcriber as key terms, never into a find-and-replace afterwards.** Write a plain list before you run it: every person on the tape, every company, every product, every term of art your field uses. A real list from a recorded training ran to 18 lines and held people, 6 products, and 2 phrases the industry uses that no general model has heard.

Measured on one tape: the plain model returned 2 different wrong spellings of the same 2 names across 2 versions. The same model, same tape, with a key-terms list, returned both correctly. A find-and-replace afterwards cannot fix this, because the model does not fail the same way twice: it mangles a name into a different wrong string each run, and you cannot grep for a string you have not seen yet.

2 things that bite:

- **The transcribers cache on the filename**, so a pipeline that re-runs with a new key-terms list will serve you the old wrong transcript forever. Pass `--force`, or change the name.
- **A single mushy passage** does not need the whole tape re-run. Re-transcribe that window alone and merge it, and copy the transcript before you do, because a merge that overwrites in place has no undo.

**You end this step reading the key-terms list back against the transcript**, checking that every name on it came out right. One grep per name.

---

## Step 2: know what is on the tape before you cut it

3 scans, none of them expensive, all of them things the transcript cannot tell you. Run all 3 before a single boundary is chosen.

### 2a. The layout scan: where does the picture change shape

A recording of a call changes layout. A gallery becomes a screen share and becomes a gallery again. The grid reflows from 3x2 to 3x3 when a seventh person joins. **Every one of those is a hand-off you have to measure, and measuring it to the half second is not good enough.**

```bash
# one frame every 10 seconds, tiled, so you can see the whole recording's shape in a few images
ffmpeg -v error -y -i raw/tape.mp4 -vf "fps=1/10,scale=320:-1,drawtext=text='%{pts\:hms}':x=4:y=4:fontsize=18:fontcolor=yellow:box=1:boxcolor=black,tile=6x10" -frames:v 1 build/review/layout-%02d.jpg
```

Read the sheets and write down every hand-off to the nearest 10 seconds. Then pin each one **to the frame**, by stepping through the second around it:

```bash
ffmpeg -v error -y -ss 645.0 -i raw/tape.mp4 -t 1.5 -vf "fps=25,scale=480:-1,tile=8x5" -frames:v 1 build/review/handoff-645.jpg
```

One measured hand-off on a real training sat at 645.88 and had been written down as 645.5. Those 10 frames put raw, unblurred gallery into the deck slot in the finished cut, and it read to a viewer as a flicker. It was a privacy leak wearing a cosmetic costume.

**And a layout seam can move mid-tape.** On one recording the shared screen was 1669px wide for the first half hour and 1621px after it, because a participant strip widened when somebody joined. A crop fixed at the first measurement leaked 48px of attendee tiles across the entire back half. **Measure the seam every 10 seconds, take the narrowest value, and use it for the whole cut.** Losing a strip of window chrome is free; leaking faces is not.

### 2b. The slide timeline: what is on screen and when it changed

If the recording carries a deck, the transcript cannot see a reveal. Somebody says "5 things" and clicks the fifth one in 12 seconds later; a cut picked off the words leaves before the slide finishes. That shipped once and had to be re-cut.

Sample the deck region at 4fps, tiny and grey, and measure how much of the picture changed frame to frame. A large change is a new slide; a small one is a card or a band appearing:

```python
# slides.py, run it from the recording folder
import json, subprocess
import numpy as np
SHARE = (645.9, 3056.7)          # the share window you measured in 2a
CROP = "crop=1490:838:0:122"     # the deck region, measured off a real frame
FPS, W, H = 4, 192, 108
SLIDE_T, REVEAL_T, SETTLE = 0.20, 0.012, 0.6
p = subprocess.Popen(['ffmpeg','-v','error','-ss',str(SHARE[0]),'-i','raw/tape.mp4','-t',str(SHARE[1]-SHARE[0]),
                      '-vf',f'{CROP},scale={W}:{H},fps={FPS}','-f','rawvideo','-pix_fmt','gray','-'], stdout=subprocess.PIPE)
prev, events, last_t, i = None, [], -9, 0
while True:
    buf = p.stdout.read(W*H)
    if len(buf) < W*H: break
    f = np.frombuffer(buf, np.uint8).astype(np.int16); t = SHARE[0] + i/FPS; i += 1
    if prev is not None:
        d = float((np.abs(f-prev) > 24).mean())
        if d > REVEAL_T and t - last_t > SETTLE:
            events.append(dict(t=round(t,2), kind='slide' if d > SLIDE_T else 'reveal', delta=round(d,3))); last_t = t
        elif d > REVEAL_T:
            last_t = t
    prev = f
p.stdout.close(); p.wait()
open('build/slides.json','w').write(json.dumps(events, indent=0))
print(len(events), 'events:', sum(e['kind']=='slide' for e in events), 'slides,', sum(e['kind']=='reveal' for e in events), 'reveals')
```

Keep this file. In step 5 you check every boundary against it: **a unit that ends between a reveal and the next slide change is cutting through a build**, and it gets extended to the last reveal and the end of the sentence.

### 2c. The speaker check: who is actually talking

Most call recordings bake the speaker's name into the active tile. That means who is talking is **on the tape** and does not have to be inferred from a diarization guess.

```bash
ffmpeg -v error -y -ss 1032 -i raw/tape.mp4 -frames:v 1 -vf "crop=300:40:14:400" build/review/spk-1032.png
```

Crop the name strip at the midpoint of each segment you care about and read it, with OCR or with your eyes. On one recording the transcriber attributed the closing line, the button of the whole video, to the wrong person. The name on the tile said otherwise for every frame of it. Diarization is good enough to drive a layout. It is not good enough to be trusted on a hand-off.

**You end this step with 3 artifacts you can look at:** the layout contact sheets with hand-offs written to the frame, `build/slides.json`, and a handful of labelled speaker crops.

---

## Step 3: the privacy pass, and it happens before the first render

**This is mandatory and it is the step people skip.** Every rule here was paid for.

### What you are looking for

1. **Faces and name labels of anyone who did not agree to be on camera.** In a call recording that is everybody in the gallery, every tile, and every name strip under it.
2. **Client or customer names**, spoken or on screen.
3. **Private interface behind the work.** This is the one that gets missed. Browser sidebars, conversation titles, file paths, tab strips, address bars, notification badges, search history, bookmark bars, a dropdown that opened over the slide for 2 seconds.

### The rules, each with what it cost

**A screen share is the host's entire screen, and 2 frames do not clear a 2 minute stretch.** One build note read "their own tabs only, checked at full resolution", off 2 frames of the tab strip. An independent pass at full resolution across the whole share then found, on that same stretch: an address bar dropdown carrying the subject line of a private email, an analytics dashboard with account identifiers in the rows, a logged-in social feed with notification counts, search history, and the tab strip and address bar on literally every frame.

So: **sample the share at 1 frame per second, at full resolution, before the first render.**

```bash
mkdir -p build/review/expo
ffmpeg -v error -y -ss 645 -i raw/tape.mp4 -t 2411 -vf "fps=1" -q:v 2 build/review/expo/%05d.jpg
```

Then look at them. Not a thumbnail sheet: at full size, at least across the bands where interface lives (the top 150px and whichever edge the sidebar is on).

**Sampling every 5 seconds is not enough.** A 1.8 second exposure of a private list survived a sweep that sampled at 5 seconds. **Exposure checks sample at 1 second or finer**, always.

**Blur windows are derived, never hand written.** On one recording a detector for "is a sidebar open" fired on any numbered list, which meant 95% of the blurred runtime had no sidebar on it: roughly 90 of 800 seconds of teaching content was smeared, the worst of it 27 seconds of the closing answer. A blur that is on when the private thing is absent is a fault, not a safety margin.

Then somebody fixed it by hand, removing the windows the audit named, and **dropped a window covering a genuinely open sidebar listing 15 private conversation titles.** Both directions cost. Derive the windows from what is actually legible: OCR the band at 2fps across every kept second and emit a window only where private text is really readable. On the tape that was measured, that gave 7 windows totalling 70 seconds, against a hand list that had 142 seconds of blur over a closed sidebar.

**Where a repair is needed, the repair is data.** A list of windows in a JSON file, each one either a blur or a freeze that holds the last clean frame of the page over the private span. Never a hand edit to the build code, because a night of changes has to be readable in one small file in the morning.

**Cropping is usually the whole fix.** A screen share with a webcam column becomes clean by taking the column off. A local recording becomes clean by taking 110px off the top, which is the menu bar, the tab strip and the address bar. Do the crop before you reach for a blur.

**Your own workspace going on camera is rebuilt, not blurred.** When the recording would show your own screen, an app or a dashboard, copy the real page, replace every person with who they are, drop client names, replace figures with ones of the same shape, read the copy's rendered text and its HTML comments, and record that copy. A moving blur has 4 measured failure modes (`content/reference/workshop-edit.md`, section 7); a rebuilt still has none. Attendees in a call cannot be rebuilt, so for them the blur stays, derived and checked as above.

**The consent test is seen, heard or named.** Somebody who is none of the 3 in the cut needs no consent. Where their speech makes the cut better, keep it and anonymise their voice only (a pitch change, nothing creepy).

### The check that clears the step

```bash
# every kept second, top band and left band, at full resolution
ffmpeg -v error -y -i renders/cut.mp4 -vf "fps=1,crop=1920:160:0:0" -q:v 2 build/review/band-top/%05d.jpg
ffmpeg -v error -y -i renders/cut.mp4 -vf "fps=1,crop=380:1080:0:0"  -q:v 2 build/review/band-left/%05d.jpg
```

**You end this step having looked at every one of those frames**, and the cut does not leave the machine until you have. A frame cleared as "clean, no names anywhere" once carried an uncleared attendee's face and name in a webcam tile, and a second carried an undimmed sidebar of private conversation titles. Both were cleared by somebody who believed they had checked.

---

## Step 4: find the moments, and a person picks

You have read the transcript. Now find what is worth keeping, and hand it to them to choose.

**How to read a long transcript for the parts worth keeping.** Read it in one pass, top to bottom, marking as you go. What you are marking:

- **A complete thought that stands without its setup.** If it needs the 3 minutes before it, it is not a moment.
- **A number, a name of a thing, a mechanism.** Concrete beats abstract every time.
- **A question somebody asks and the answer lands.** Those are already shaped.
- **A change of energy.** A laugh, an interruption, somebody saying "actually, no".
- **The line the whole recording hangs on.** There is usually one. It is often near the end and often said quietly.

**Then check each mark against the tape.** A clip list assembled from a transcript alone reliably picks moments that read well and play badly, because a transcript cannot see that they trailed off, looked away, or said it better 40 seconds later. Pull a frame at each candidate's midpoint and look.

**Then a person picks.** Hand over the marked list with a sentence each on why that one, and stop. If nobody picks, this skill stops here. Do not build a spine out of your own favourites and present it as a draft of theirs unless they said "just draft it".

**One exception, and it is how a condensed cut actually gets made.** For a long training or a long talk where the shape is already the speaker's, render a draft spine and let them subtract after watching, rather than agreeing a table first. The rules that make that work are in `long-form-lessons.md` under "The shape of a condensed cut", and the first one is: **pure subtraction, in the tape's own order, nothing re-sequenced.**

**You end this step with a written list of keep ranges** and a name against whoever approved it.

---

## Step 5: the cuts that make a raw recording watchable

A raw recording is not unwatchable because of what is in it. It is unwatchable because of what is between things.

### Silence

The policy that has shipped, in numbers: **any silence of 1.0 second or more is tightened to about 0.6 seconds, by leaving 0.3 seconds on each side.** Then a machine-gun guard: **never leave a kept sliver shorter than 1.2 seconds between 2 cuts**, and never merge across 2 separate keep ranges.

```bash
ffmpeg -v error -i raw/tape.mp4 -af "silencedetect=n=-30dB:d=1.0" -f null - 2> build/silences.txt
```

The threshold is a property of the room, not a constant. A quiet studio detects at -40dB; a conference room with air conditioning detects nothing at -40dB and needs -30dB or -27dB. **If `silencedetect` returns nothing, the room is noisy, not the cut clean.** Never respond by dropping the threshold toward -30 on a clean tape, because that eats soft word endings.

### Filler

**Filler words stay in the audio. Captions drop standalone "uh" and "um".** Chasing every filler in a 2 shot makes visible jump cuts, and the cure is worse than the disease. False starts and stutter runs are different: those cut, on word boundaries.

### Boundaries

**A pause is cut only between 2 transcript words**, and only where at least 0.6 seconds of that gap is measured quiet. Tightening every stretch below -38 dB off a silence list alone clipped 5 quiet spoken words in a 9 minute cut.

**Snap every boundary to measured audio energy, not to the transcript's word spans.** Transcribers hang the trailing pause on the word, so snapping to a word's end puts the dead air back in.

The method, in numbers that worked: 20ms RMS windows on 16kHz mono, threshold -38 dBFS, 3 consecutive quiet windows, walking outward in 20ms steps, capped at 1.5 seconds, with a 0.05 second pad. Only real cuts move. Where the next unit starts exactly where this one ends, that is continuous audio and it is left alone.

**Then read the rendered captions back across every join.** A corrected opening cut once landed at 610.00 and sliced the word "opportunity" in half. The plan looked right and the automatic pass was green, because neither checks whether a word survived. Reading the caption text across the join found it in one pass and the boundary moved to 610.55.

### Slide builds

Check every boundary against `build/slides.json` from step 2b. **A unit that ends after a reveal but before the next slide change is cutting through a build.** Extend it to the last reveal and to the end of the sentence.

**And a card the presenter never got to is yours to reveal, not to drop.** Where the presenter clicked a reveal late, after they had already said the words, the cut shows the finished slide as the words land, off a real frame of it. Finishing every build on one measured cut cost 28% of runtime, 11:15 to 14:22. **Predict that overrun before it happens and price the trade**, rather than silently cutting something they wanted.

### Pacing

**1.05x on a workshop or a training, pitch preserved.** 1.1x on a conversational episode. Both were picked by the person whose channel it is, by watching, and both numbers are theirs to move.

**The speed pass goes last, after the captions are burned**, so the captions stay in sync. And then:

**Every timestamp handed to a human comes off the delivered file, never the pre-speed timeline.** Chapter marks derived from a 1.0x edit list are 5% late, which on a 46 minute cut is over 2 minutes by the end. That was caught with 34 wrong chapter lines already drafted into 2 descriptions.

### Audio

```
acompressor, then loudnorm=I=-14:TP=-1.5:LRA=11
```

Tame the loud close-mic moments first, then normalise once, at the end. For a mono bus that booms, the chain that worked was: declip, highpass at 120 Hz, low shelf -5 dB at 220 Hz, noise reduction, limiter. Measured on a 30 second slice, that took the low band from -27.9 dB to -31.3 dB mean and peaks from -10.5 to -14.5.

**A music bed is measured against the voices, never judged by ear on laptop speakers.** About 19 to 20 dB under the speech was right where 6 to 7 dB under was "way too loud". Measure both in the same window and say the number before anybody watches. Music comes from a licensed library, never generated.

**And every derivative inherits the long form's audio chain.** Shorts cut from the recording run the same chain or reproduce it exactly. 3 rounds of clips once shipped with raw camera audio because the chain lived only inside the episode's own build script.

### Cutting audio and video separately, which you have to do

Video segments render without audio, and the audio is cut to each segment's **real frame count**, read back from the rendered file, not to the duration you asked for. A 25fps segment can come out a frame longer or shorter than requested. On one cut, 118 segments each off by a frame or 2 drifted the audio by seconds.

```python
n = int(subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames',
                        '-of','csv=p=0', str(seg)], capture_output=True, text=True).stdout.strip())
samples = n * (48000 // 25)      # the audio length this segment actually needs
```

Then a 30ms fade at each edge, and join. **You end this step with the joined file's video and audio durations printed side by side**, agreeing to within a frame.

---

## Step 6: multiple people on one camera

This is the part nobody writes down, so here it is with the numbers.

### The tile is the ceiling

A typical gallery tile in a 1080p call recording is around 384x216. **It upscales cleanly to 2x, acceptably to 2.5x (960x540), and mushily at 3x.** Design inside that or the hero face is soft, and no amount of sharpening fixes it. Check the real tile size on a frame before you design a layout around it.

### The layout follows the voice

**A picture-in-picture hard wired to one person lies about who is talking.** On one measured cut, across 3 minutes 32 seconds of screen share, the only face on screen was one person's, including roughly 48 seconds where somebody else was teaching.

The speaker timeline is knowable: the transcriber's diarization plus the name baked into the active tile (step 2c). Drive the layout off it.

### Equal boxes give the loudest real estate to whoever is silent

Check who actually speaks **in the kept material** before you design. On one recording, a person who never speaks once in the final cut held an equal-sized box for the entire opening, carrying a competing wordmark and then a frozen photograph. The person whose cut it is said it plainly: equal boxes take attention away from the main act.

### A still of a speaker reads as frozen video, not as a photo

Where the tape has no footage of somebody speaking, because the platform spotlighted the other person, **do not freeze a wide 16:9 frame of them mid-word in a video-shaped box.** It reads as a broken file. Use a portrait-shaped photo, 4:5, mouth closed, eyes to camera, name and title beside it. And look in your own archive before the web: somebody who has been recorded before already has an approved headshot somewhere.

**And a still holds still.** Never put a slow push-in on a card or a photo. A zoom filter resamples the frame by a fraction of a pixel every frame, and on flat ground, type and a face shimmer. Measured: 11 levels of per-frame change in the picture area with spikes to 223, against 0 to 2 when the still is left alone. Test it:

```bash
ffmpeg -v error -ss 120 -t 4 -i renders/cut.mp4 -vf "crop=1920:900:0:0,tblend=all_mode=difference,signalstats,metadata=print:key=lavfi.signalstats.YMAX" -f null - 2>&1 | tail -20
```

A still section sits at YMAX 0 to 2. Anything else is moving when it should not be.

### Somebody speaking off mic

There is no fix in post that makes an off-mic voice good. What you can do, in order of preference: cut to whoever is on mic and let the off-mic voice be heard as a question rather than seen as a shot; caption the off-mic line so it reads even where it does not hear well; or lift it and accept the room tone that comes with it, at roughly 6 dB under the on-mic mix rather than the 12 dB it usually sits at. Err toward the lower volume. Never boost it until it matches, because what you are boosting is the room.

### When the recording is a livestream with a deck

- **The shared window is not always the deck.** A browser can shrink, zoom out or flash a new-tab page with bookmarks and a local path. Match every half second of the share against renders of every build state of the deck: under about 8/255 mean difference, repair the corner a camera box covered from the matching render; 8 to 30, show the clean render; 30 and over, hold the last good slide.
- **Slide changes are measured to the frame.** Half-second sampling put the wrong build on screen for up to 0.8 seconds at every change.
- **A layout switch is a 0.4 to 0.6 second crossfade, not a cut.** Measure it at full frame rate and hold the last clean frame, or faces ghost inside the deck for 5 to 8 frames.
- **An RGB still laid onto a BT.709 tape needs an explicit conversion** (`scale=out_color_matrix=bt709:out_range=tv,format=yuv420p`), or it lands as a visibly green box. Measure the rendered frame against the pixels beside it.

### When to cut to the deck instead of the room

Cut to the deck when the deck is doing the explaining, which is most of the time on a training. Cut to the room on a laugh, on an interruption, on a question from a person, and on the closing line. **The deck should be on screen within the first 15 seconds** of a cut made from a presentation, even while people are still talking over it. And the faces stay on the opening: never a still of the presentation where a face could be.

**You end this step looking at one rendered frame per layout**, before any long run starts. Render a single probe segment per layout and extract its first frame:

```bash
ffmpeg -v error -y -i renders/probe-share.mp4 -frames:v 1 build/review/probe-share.png
```

One version rendered for 13 hours overnight and was rejected in the first minute, on the frame.

---

## Step 7: captions, cards and the finish

**3 caption rules that bite at long-form length**, with the full set in `content/reference/podcast-edit.md` section 4:

- **The caption block never crosses a speaker's mouth.** Check a full-resolution frame of each speaker talking. Name cards go lower and give way; captions do not move up for them.
- **The word gap is measured as libass draws it**: add the style's letter spacing and both outlines to the measured advance, or a line reads as one run-on word. About 26px visible on a 1920 frame; a group wider than about 1500px becomes 2 caption frames.
- **Crosstalk is the main fault on a 2-presenter recording.** Read every caption against who is speaking.

The rest of the caption craft is already in this pack and is not restated here:

- **Style, sizing and the caption gate:** `.claude/skills/shorts-editor`, the Style section. The floor and the checker are `python3 .claude/skills/shorts-editor/scripts/check_caption_size.py`.
- **The mechanical review before a person watches:** `.claude/skills/cut-review`. Run it on the finished file, every time.
- **Cards and title treatments:** `.claude/skills/shorts-editor/references/card-snippets.md` and `.claude/skills/shorts-editor/references/animation-library.md`.
- **Anything that assembles on screen:** `.claude/skills/media-gen` for generated imagery, and the `on-camera-board` skill for the surface they present from.

The 4 caption faults that are specific to long form, because they only show up across hundreds of lines, are in `long-form-lessons.md`: the karaoke highlight running backwards, word-count line breaking, "one" as a pronoun, and a caption filter keyed on the wrong end of a word. Read those before you generate a caption file for anything over 10 minutes.

**2 finish rules that belong here:**

**A condensed cut needs transition cards, and a card is not a title slide.** On one audited cut, 12 of 33 real cuts jumped between 17 and 330 raw seconds with no bridge at all, and 11 of those sat exactly on a chapter mark, which is the proof that each one was a new teaching beat that needed announcing. A card answers what the viewer gets next, in 6 words or fewer, title case. It names its own subject: never a verb plus "it" or "this", and numbers are numerals.

**A promise made on camera is a live link before the video publishes.** If somebody says "link below", "free resource", "the prompt", then every one of those is a real URL in the description, fetched and returning 200, in the session that publishes. Grep the take notes for every on-camera promise and check each against the description itself. Somebody cancelled an appointment once because they thought a video was clickbait, over a resource that existed and had been live for 6 days, because the person writing the description did not know it existed.

**The publishing rules that cost the most** (a native LinkedIn video's thumbnail matching the video's pixel dimensions and going on only after the upload reaches 100%, a publish proven by reading the profile back, an upload failure diagnosed with the smallest honest clip, upload caps that differ per tool route) are in `content/reference/lessons.md`, rules 1 to 7. Read them before the first publish.

**You end this step with the finished file and a publish kit beside it**: title, description with chapters measured off the delivered file, and tags. Build it as an HTML page with copy buttons if they are going to paste it by hand.

---

## Step 8: render discipline at long-form length

`content/reference/render-reliability.md` covers the 8 things that kill a long render and is the file to read before your first one. 4 things are specific to this length:

**Cache by segment, and rebuild only what changed.** When the blur changed on one cut, every deck segment was kept and only the gallery segments were deleted, which is why an 11 minute and a 46 minute cut both came back in 12 minutes. **A geometry change invalidates every segment**, so that cache gets deleted deliberately when the frame layout moves.

**"The render finished" is not "the change landed."** An edit that misses its target block produces a clean render that changed nothing. One version came back byte for byte identical to the previous one and only a file size comparison caught it. The cause was 2 identical keys in the same Python dictionary, so the edit landed in the block the language discards. **Compare every output against the previous output before delivering it.**

```bash
ls -l renders/*.mp4 && md5 renders/cut-v4.mp4 renders/cut-v5.mp4
```

**Probe a filter as a still before you re-encode anything.** The blur radius on one cut was chosen from 2 PNG probes, not from 2 renders. 2 ffmpeg failures were paid for on the way, both of them silent radius caps.

**A segment render at 0% CPU is a deadlock, not a slow render.** Check `ps` for its CPU before calling it slow. The first suspect is the input window: a short segment whose audio runs out exactly where a padding filter begins will never flush. Give the input window a second of slack, run every ffmpeg with `-nostdin`, and put a bounded wait on each segment (60 seconds plus 3 times its duration) with one retry, so a stall costs minutes instead of half an hour.

**2 portability traps that waste a whole night:** `timeout` does not exist on macOS, and a step that uses it exits 127 every time (`perl -e "alarm N; exec @ARGV"` is the portable version). And a filter label containing a colon silently fails the entire filter graph, so escape it (`00\:30`). The second one is worse, because a verification step that produces nothing while looking like it ran is harder to notice than an error.

**You end this step with the render running detached and a heartbeat you can read**, and the answer to "is it working" is the output file growing, never the CPU meter.

---

## Step 9: the review, one dense pass per vector

**A 100 frame contact sheet of a 15 minute video cannot catch any of the faults in `long-form-lessons.md`.** The person whose cut it was said exactly that: 100 screenshots gives you a general idea and nothing more, and what is needed is a set of specialised passes, each with its own sampling rate, attacking a different vector.

| Vector | Sampling | What it finds |
|---|---|---|
| Captions | 1.5s, with suspect stretches at 0.4s and the karaoke itself at 0.04s | Highlight running backwards, broken line breaks, 2 sentences welded into one card |
| Every seam | 4 frames per join: -0.6, -0.2, +0.2, +0.6 seconds | Clipped words, mid-sentence cuts, a frame of the wrong layout |
| Privacy | 1s inside every blur window, 3s outside every one | A blur that is on with nothing behind it, and a leak the windows missed |
| Layout | Every speaker change | A picture-in-picture showing the wrong person |
| Pacing | 2s across the whole runtime | Dead stretches where nothing moves |
| Audio, on its own | The whole file | Dead air and a speaker imbalance. On one review 5 visual passes missed 4.7 seconds of digital silence and a 2.2 LU imbalance, and the audio-only pass found both |

**Run each vector as its own independent pass, so nobody is marking their own homework.** If you have subagents, that is what they are for, and the reviewer reads the whole conversation rather than a summary of it.

And the mechanical battery, which is cheap and catches the stupid ones:

```bash
ffmpeg -v info -i renders/cut.mp4 -vf "blackdetect=d=1.0:pic_th=0.98,freezedetect=n=0.001:d=3" -an -f null - 2>&1 | grep -E "black_start|freeze_"
ffmpeg -v info -i renders/cut.mp4 -af "silencedetect=n=-50dB:d=1.0" -f null - 2>&1 | grep silence_start
ffprobe -v error -select_streams v:0 -show_entries stream=duration -of csv=p=0 renders/cut.mp4
ffprobe -v error -select_streams a:0 -show_entries stream=duration -of csv=p=0 renders/cut.mp4
```

The 2 durations agree to within a frame, or there is drift.

**Then a person watches it, and that never gets skipped.** A green battery means the file is now worth their time. It does not mean done. A finished public artifact is not what an autonomy grant covers, even an explicit one.

**You end this step with a timestamped fix list**, and you run `cut-review` for the mechanical half of it.

---

## Step 10: what comes off one recording

One long recording is not one piece of content. Hand it over rather than rebuilding any of this:

| What | Who owns it |
|---|---|
| The full long form | This skill, steps 0 to 9 |
| A condensed cut, usually under 15 minutes | This skill, on the subtraction rules in `long-form-lessons.md` |
| The vertical shorts | `.claude/skills/shorts-editor`, one picked clip at a time. Hand it the in and out points and the episode's audio chain |
| The written posts, the carousel, the derivative map | `.claude/skills/content-waterfall`, which owns the whole "one recording becomes many pieces" question and the interview posture that goes with it |
| The review gate | `.claude/skills/cut-review` |

**Run `content-waterfall` before you plan the shorts**, not after. Its step 1 is watching the whole recording and its step 2 is putting a derivative map to the person before anything is written, and both of those change which clips are worth cutting.

**Never auto-clip.** If a waterfall comes back with clips nobody picked, stop and ask.

---

## The handover, and what it must say

Whatever you hand over, name **what you left out on purpose.** A real handover said it in one line: the chat-reading moments, one whole tier list, 2 tangents and the entire question and answer section, "those are yours to put back." A list of what is missing is what lets somebody subtract in one word instead of re-watching an hour.

Also name, in the same handover:

- The full absolute path of the file, right before you show it.
- A review or handover page that carries `<video>` is served, never opened as a file: `python3 scripts/serve_outputs.py`, then `http://localhost:4200/<path under outputs/>`. Its Range support is what lets a browser start and seek an mp4.
- The runtime, and how far it is from whatever target they set.
- Anything you could not check and why, in plain words. A caveat is not a check, but an honest "I could not reach this" beats a confident wrong answer.
- Every trade you made, priced. When finishing every slide build would break a runtime target, the useful message names the 3 things that could come out and what each one costs in seconds. That is what produces a real decision instead of a silent one.

---

## Self-learning, at the end of every recording

Same mechanism as `shorts-editor`, and it is the whole compounding story:

1. **Honest retro**, in the conversation: what went well, what went badly, how many rounds, what you should have anticipated. No self-praise: write down the error.
2. **A repeatable error becomes a row in the errors table** in `content/reference/long-form-lessons.md`, with its real cost, in the same session. Not in this recording's folder. A caption rule fixed inside one episode's build script shipped the same fault on 12 of 15 renders 3 days later, which is the most expensive mistake in this pack.
3. **A taste call they made becomes a line in `content/taste/editing-rules.md`**, dated, with their words quoted.
4. **A rule that keeps getting broken becomes a check script**, never a longer paragraph.
