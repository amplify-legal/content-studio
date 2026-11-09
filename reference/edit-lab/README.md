# The edit lab book

> For the editor, the creator and any session that edits video. Copy this folder to `content/reference/edit-lab/` in your project and keep adding to it the same way (see "Keeping it alive" at the end).

**What this is.** A lab book of how each editing technique was got to render: what was tried, what failed and why, the numbers that worked, and the code or settings that made the final version. It was first written on 29 Oct 2026 from about 145 lessons swept out of build logs, taste files, the podcast runbook, the editing skills and every build folder. Before the book, most methods already had a rule somewhere, but the failed tries, the numbers and the working code sat in build folders and log rows that no session was ever sent to. The creator's ask that started it: not only how to do a thing, but how it was done, what was tried, what did not work, and how the final version that did work was reached, for highlighting, sound, zooms, animations, motion graphics, boxes, positioning, blurs and the rest.

**Taste files say what the creator wants. This book says how it was got to render that way, and what broke on the way.** When the two disagree, the taste file and the newest dated ruling win, and the line here gets corrected.

## Which file

| You are working on | Read | What it covers |
|---|---|---|
| Captions, the karaoke word highlight, the yellow highlighter, cards, boxes, lower thirds, fonts, where text sits | `captions.md` | 51 lessons in 10 groups (the credit checked against the chin, added 7 Nov; karaoke, size and fonts, timing, safe frame, cards, highlighter, review, the co-host's channel, the 27 to 29 Oct shorts build: caption layout, caption on a face, the Instagram sticker, `caption_fix`, titles, the credit, graphic type) |
| Sound: loudness, clean-up, de-reverb, music beds, ducking, laughs, swooshes, 48 kHz, regenerated words, Riverside tracks, drift, silences, fillers | `sound.md` | 30 entries (a podcast mix through 3 review rounds, added 7 Nov; the 29 Oct harshness chain and its meter, retime offsets, the Riverside ingest of 26 Oct among them) |
| Picture: shot grammar, layouts, face reading, second angles, upscale limits, 9:16 crops, push-ins, screen zooms, tutorial layouts, light and colour, eye line, jump cuts, frame rate, encode | `picture.md` | 37 techniques (a darker face lifted on its own track, added 7 Nov; the panel solver, the stacked question hook, blurred never black, hand face boxes, duo tails, tutorial layouts as of 29 Oct) |
| Motion: HyperFrames craft, alpha overlays, compositing traps, story animations (Omni, Seedance, Veo, a flat 2D mascot), cards and count-ups, shorts motion, transitions, progress bars, end screens | `motion.md` | about 39 lessons in 11 groups (the Instagram look as built, card windows, `ig_between`, animation directions A, B, C and their ink traps) |
| Blurs and privacy on footage, then the pipeline end to end: clip picks, EDLs, transcription, word boundaries, verify loop, cut-review repeats, render reliability, uploads, what the creator rejected, retention | `privacy-and-pipeline.md` | 16 privacy lessons and 16 pipeline lessons (B16, a detached render hanging at its final flush, added 7 Nov; the shorts build added tutorial screen masks, off-limits topic openers, the render gate and disk freeze, the build log's record traps, review rounds, snap and speaker traps, the spec shape), plus 7 from the co-host's channel and 6 from a podcast edit run in a cloud session (C1 to C6, added 7 Nov) |

**On the co-host's channel** (a second creator with their own taste file) their own rulings govern taste; the methods and shared mechanics here apply. 17 lessons from that channel were added on 29 Oct (the "From the co-host's channel" entries in each file).

**How the examples are named.** Every person is a role (the creator, the host, the co-host, the editor) and every podcast guest a letter (guest X, guest C), the same letter in every file. Tutorials are numbered in the order each file first meets them (`tutorial-1`, `tutorial-2`), so `tutorial-3` in `picture.md` is not necessarily `tutorial-3` in `captions.md`. The numbers, the failed tries and the dates are real.

Each file is under 400 lines, so a session can read the whole of one. Read the one for the job before the first render, the same way `content/taste/kinds/<kind>.md` is read before a cut.

## The traps that cost the most time

The lessons a new edit session is most likely to relearn the hard way. Detail and receipts in the file named.

1. **Burn karaoke captions in one libass pass, never frame by frame**: frame-by-frame PIL took hours, while ASS karaoke burns in about 4 s. **Pin the base colour**, or the highlight runs backwards (`captions.md` 1 and 2).
2. **The shorts safe frame is the 2026-09-16 one**: captions end at or above y 1500, nothing in the top 12%, the right rail dead from y 960 down. Measure the whole caption block, descenders included (`captions.md` 23 and 24).
3. **Never `zoompan` on footage.** It repeated each frame 18x on guest X's source. A punch-in is a hard cut to a tighter crop, and a push-in on an insert is one continuous piece (`picture.md` 12).
4. **A generated second angle is not dependable** (11 Omni runs, 28 Oct). The real-pixel punch-in is the default cutaway (`picture.md` 5, `content/reference/media-gen.md`).
5. **Native AAC overshoots the true peak by 4 to 5.7 dB.** Keep PCM intermediates, encode AAC once at the end, at 256k with `aac_low` or `aac_at` (`sound.md`, loudness).
6. **The podcast intro music bed sits about 19 to 20 dB under the voices** (0.0224 on guest P's episode; 0.10 was "way too loud"). Shorts beds sit at 0.02. Measure the bed against the voice in the same window and say the number (`sound.md`, music beds).
7. **Riverside opens a second track when a mic switches**, and its aligned export is digitally silent before the switch: stitch the 2 tracks. Prove sync by cross-correlating one speaker with their bleed in the other track (`sound.md`, Riverside).
8. **No network inside a render**: GSAP from a CDN stalled a 4 Sep render twice, so vendor the library (the shorts-editor template `gen.py` copies it from `assets/vendor/`; its 2 example generators still name the CDN, so swap those lines when you copy one). A HyperFrames overlay with alpha comes out of `--format mov` (ProRes 4444) or `webm`. Matching the overlay's frame rate to the master is practised per build (24 fps on Riverside) and is now a closed default below (`motion.md` A and B).
9. **Blur windows on moving footage come from OCR, sampled every 1 s or finer, at full resolution.** The editor's 24 Oct method: per-second OCR boxes, then pixelate. Frame 1 is t=0, so boxes land 1 s late unless shifted. Crop instead of blurring where you can (`privacy-and-pipeline.md` A5, A6, A7, A10).
10. **The detached render runner re-reads the command**: a space in a path or a `|` in text breaks it, so pass a script file. On a slower second machine the segment stall guard is 120 s + 8x, not 60 s + 3x (`privacy-and-pipeline.md` B7).
11. **The verify loop cannot see a constant audio-to-picture offset** across the whole file (the editor, 13 Oct). Check sync against the original tape, never by duration alone (`privacy-and-pipeline.md` B5, `picture.md` 29).
12. **A cut the creator rejected stays rejected** until the creator accepts a revision against a reference they picked. Mechanical passes don't make a cut good (`privacy-and-pipeline.md` B9, `content/taste/cut-feedback/`).

From the 27 to 29 Oct podcast and tutorial shorts build (about 230 numbered fixes in its build log, whose lessons are in `examples/podcast-shorts-pipeline/README.md`). The build kept changing after these were written on 29 Oct evening (builder H, rows 236 on: the duo shorts, the title exit, the list layout), so read the log past row 236 before copying those parts:

13. **Solve every panel, never place a crop by a fixed share and clamp it.** The clamps let the footage stop wherever they landed: round 1 had blur on 26 to 32% of the frame in 14 of 14 shorts. The solver holds the crown, footage to 1640, the mouth over 1500 and the face size together, with a fixed relax ladder (`picture.md` 32).
14. **Nobody small, nothing black.** A stacked question whose smaller face solves under 272 px plays full frame on its own speaker; a narrow crop sits over its own blurred picture, never on a black band or pillar (still read as dark pillars on guest S's F3, open); the collar is asked only where the tape has one, and whether the host's webcam tape has one was disputed (`picture.md` 33, 34).
15. **Never `render_detached.sh stop` a runner with builds in flight**: it kills the whole process group. Kill its 2 supervisor bash pids, then its python. The render gate counts supervisors across sessions, so run one supervisor per lane (`privacy-and-pipeline.md` B11).
16. **A frozen render is not a hung render.** If you run a render guard that SIGSTOPs every ffmpeg when the disk drops under 15 GB truly empty: count a timeout only while the child is not stopped, never kill or SIGCONT a frozen job, and requeue a job whose check timed out across a freeze (`privacy-and-pipeline.md` B11).
17. **Measure harshness with a 3 to 8 kHz band-pass meter in 50 ms windows through the AAC encode**, never a whole-signal FFT band cut (it read the limiter's ceiling as spikes), and stop before the voice dulls: the stronger chain took the speech balance from -14.9 to -20.7 dB (`sound.md`, harshness).
18. **When the order rule moved the stacked hook off t=0, every page that read "0 to hook_end" as the hook broke** (a black band where guest X's animation should play). Read `hook_start` to `hook_end` everywhere (`motion.md`, `ig_between`).
19. **A field a function overrides still regresses, and a check keyed on the id reads old frames.** Fix the spec's own `credit`, key check frames on the render's mtime and size, take the last results row per id, and never call `ok` a reviewer's pass (`privacy-and-pipeline.md` B12, `captions.md` 48).

From the 3 to 6 Nov builds (added 2026-11-07):

20. **A detached render can hang at a piece's final flush.** On one machine, a job started in its own session (what `scripts/render_detached.sh` does with `os.setsid`) hung at 0 CPU with its file 1 to 2 s short, while the same command finished in 3 s from the login session. A piece runner that watches output size AND CPU (both flat 20 s: kill and retry) held (`privacy-and-pipeline.md` B16).
21. **Calibrate libass on the machine that burns.** The same caption layout drew letters together on a Linux box because its factor was 0.691, not the Mac's 0.63 (`privacy-and-pipeline.md` C1).
22. **A credit is checked against the lowest chin, never the face detector's box**, or it runs across a beard and passes (`captions.md` 50).
23. **Keep the raw tracks until the finals pass cut-review**, and run builds that share a piece cache one after the other (`privacy-and-pipeline.md` C2, C3).

## After any episode build, commit its text files

The general lesson of 29 Oct: a sync job that leaves out build folders as render paths also leaves out the scripts, notes, state files and card builders inside them, so for weeks the only copy of how 3 episodes were built sat on one machine. **After any episode build, commit its small text files by path** (`.py`, `.md`, `.json`, `.sh`, `.txt`, `.jsonl`, under 2 MB each, plus the transcript json), or the next editor cannot see how it was made. Renders and raw footage stay out. When a line number into a runbook or a skill looks off after an edit, search the quoted words instead.

## Rules that apply to any video tool

Whatever editing skill or tool you use, these 4 hold:

- **Any render over 10 minutes runs detached, never as a child of the conversation.** A conversation-owned render dies silently when the turn is interrupted. With this pack: `scripts/render_detached.sh start <name> --watch <dir> -- "<command>"`, checked with `render_detached.sh status <name>`. "Is it working" is answered by the output file growing, never by the CPU meter.
- **Every ffmpeg graph with a `-loop 1` image input carries an explicit output `-t`**, plus `shortest=1` on the first overlay. A looped still never ends: the tell in the log is "More than 100000 frames duplicated". The same family of trap: never overlay a finite image sequence onto a stream at a different frame rate. Composite frame by frame in PIL and bake it into the segment instead.
- **While a render is running, no process gets killed.** A forked session keeps the original process, so a process's age says nothing about what it owns.
- **Transcription: ElevenLabs Scribe is the route** (`.claude/skills/shorts-editor/scripts/transcribe.py`, with a `--keyterms-file`), Deepgram the fallback, local whisper the last resort.

## Starting defaults settled on 29 October (they were contradictions)

Each was the creator's taste; take it as a starting default and change it in your taste file.

- **Shorts hit -14 LUFS everywhere**: `compose.sh` moved from -16.
- **Transition sounds are real recordings, never synthesised**: a background-shift tool takes a recorded whoosh as an argument and refuses without one (`editing-rules.md` rule 10). The refusal was read in code only, not run on a clip yet.
- **A section progress bar in one fixed colour (yellow) on every video and podcast** (`must-dos.md`).
- **One exact colour per product shown on screen**: Claude's orange is #D97757 everywhere (the shorts-editor palette and its example moved off #f0813f).
- **One CTA per video, between 30% and 40% of the runtime**: `editing-checklist.md` item 9 and cut-review agree.

## Closed on 29 October without a new ruling (each settled by an existing ruling or a measurement)

- **Caption size gate**: `check_caption_size.py` fails under a 47 px capital (it said 35 px before this). 35 px was what the static Montserrat face draws at 78, which let a week of small shorts through. Tested on the static face at 78 (35 px, TOO SMALL) and 104 (47 px, OK).
- **GSAP is vendored**: the shorts-editor `gen.py` copies `assets/vendor/gsap.min.js` and `MotionPathPlugin.min.js` (3.15.0, which you download once: `assets/README.md`) beside `index.html`, with no CDN. The script runs and warns when the files are missing; a full short had not been rendered through it yet.
- **Exposure checks sample every 1 s**: cut-review's 10 s contact sheet is for structure only, and any privacy check samples every 1 s at full resolution.
- **shorts-editor takes a brief's picks list** as well as the old zinger table.
- **Entrances use `power3.out`**, never back.out or an overshoot (shorts cards: `.claude/skills/shorts-editor/references/style.md`; HTML compositions use the springs in `content/taste/motion-craft.md`).
- **Overlays render at the master's frame rate**: 24 on Riverside episodes, 30 on shorts (`clip-bar.md`).
- **`podcast-edit.md`'s Helvetica line** is marked as the first episode's style.
- **The 25 GB disk preflight** (`scripts/render_preflight.sh`) holds before a render. A machine that runs a render guard (renders frozen when the disk is low) may use that instead.
- **The shorts blur extension is the bottom 15%**: a 28 Oct "a little too high" note narrowed the 27 Oct 20% (`shorts-formats.md`).
- **A prompt the creator reads on screen gets the yellow highlight and no caption strip**: on a review call the creator took the editor's highlight over the strip they had just asked for (current practice, not a written rule).
- **Push-ins on stills**: `workshop-edit.md` governs the creator's cuts; a co-host's channel follows its own rulings.

## Still open: choices to settle in your taste file

Nothing here is a session's to guess. Each is a choice the creator makes once and writes down.

- **The caption floor on the default look.** The Instagram look draws 52 px type with a 34 px capital floor (measured off Instagram's own caption), while `check_caption_size.py` fails under a 47 px capital. Pick one floor for that look (`captions.md` 45 and 7).
- **Whether talking footage gets a movement pass** (small camera moves on the face layer), and how much. The 27 Oct research left it open; whatever you pick, the move happens before captions burn (`captions.md` 29).
- **Whether a generated second camera angle is ever worth it for your footage.** 11 Omni runs on 28 Oct were not dependable; see `content/reference/media-gen.md`, "Omni as a second camera angle".
- **The masterclass card type direction**: A, a sans (Inter 600 at 78/56/44 px), or B, a display serif headline (DM Serif Display) (`captions.md` 12).

## Keeping it alive

**A lesson learned while editing (a try that failed, a number that worked, a trap) lands in the right file here in the same session**, as a new `###` entry with the same 6 bullets: Final method, Tried and dropped, How we got there, Ruling, Receipts, Where it lives now. Number it after the last entry in that file so cross-references never move. A ruling still goes into the taste file it belongs to; this book holds the method and the failed tries under it. Before saying "we never tried that", grep this folder.
