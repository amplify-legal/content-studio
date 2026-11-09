# Edit lab: editing lessons on privacy (Topic A) and the shorts and long-form pipeline (Topic B)

> Part of the edit lab book. Installed to `content/reference/edit-lab/privacy-and-pipeline.md`; the book's index is `README.md` in the same folder. The book records what was tried, what failed and how a pipeline got to the version that works. Each lesson: final method, what was tried and dropped, how it got there, the ruling, receipts, and where the rule also lives. A new lesson learned while editing is added here in the same session.

Built 2026-10-29 from a read-only sweep of one working content system: its work logs (searched for 31 words), its taste files, its reference docs, its skills, its content rules and its build folders. Names are replaced by roles ("the host", "the co-host", "the editor", "the creator") and guests by letters; episode and video folders are shapes (`podcast-guest-x`, `tutorial-1`, `wave1-05`). Receipts are generic: a date, a measurement, "the build log, row N" (the lessons log of the podcast shorts build, kept in `examples/podcast-shorts-pipeline/README.md`). "Shared" below means a file your editing sessions read: `content/taste/`, `content/reference/`, `.claude/skills/`, your rules files, your `CLAUDE.md`. "Not shared" means it lives only in a work-log row, a build folder, a script comment or a per-episode folder.

Script names that are not in this pack are named so you can rebuild them from the method written beside them; where a script ships in the pack, its path is given.

A naming trap to tell your editor first: in the shorts lane in October, "blur" means the blurred, faded extension of the video under the face panel ("blur only the bottom 20%", `content/taste/shorts-formats.md`, `content/taste/shorts-profiles.md`). It has nothing to do with privacy. Privacy blur is Topic A below.

---

# TOPIC A: blurs and privacy on footage

### A1. Attendee faces and name labels on a Zoom gallery (live trainings)
- **Final method**: soft box blur over the attendee gallery, radius 16 in 3 passes on the 1756-wide frame, so "a person stays a person"; a second hard blur on each tile's name-label strip; the hosts' tiles put back sharp; attendee voices and spoken first names kept. Code: `examples/workshop-edit/build.py` (config `blur.soft_radius` 16, `blur.soft_passes` 3, `boxblur={soft_radius}:3`; label strip `crop=1728:48`, `boxblur=luma_radius=20:luma_power=4:chroma_radius=10:chroma_power=4`).
- **Tried and dropped**: radius 40, rejected on the first render as a smear (2026-09-09). Radius 10 was probed as a still and lost to 16 (`content/reference/workshop-edit.md`).
- **How it got there**: the first render used a hard blur; the creator corrected it; the fix was picked from 2 PNG probes at radius 10 and 16, not from 2 renders, and only the gallery segments were re-rendered.
- **Ruling**: the creator, 2026-09-09: "Use blurring of the faces and names. Keep the voices." Then: "The blurs are too hard. We want to show the viewer that there are other people in the room. We just don't want to show the viewer who they are." (`content/reference/workshop-edit.md`). A starting default: a soft blur that keeps people as people.
- **Receipts**: `content/reference/workshop-edit.md`; `examples/workshop-edit/build.py`.
- **Where it lives now**: shared, `content/reference/workshop-edit.md`; a pointer in `content/taste/kinds/live.md`. The exact filter numbers for the label strip were only in the build script (in a per-video folder an editor would not open unless told; `kinds/live.md` does name the build script as the pipeline).

### A2. A layout hand-off is measured to the frame, never to the half second
- **Final method**: find each switch between gallery and share by frame difference; at a stream's 0.4 to 0.6 s crossfade hold the last clean frame (`DISSOLVES` in a live session's build). On LinkedIn Live layouts, which animate for about 1.3 s, freeze on the last clean frame 3 frames before the measured animation start (`content/reference/workshop-edit.md`).
- **Tried and dropped**: a hand-off measured to the half second (645.5 against a real 645.88) put 10 frames of raw, unblurred attendee gallery into the deck slot. The creator saw it as "a weird flicker around second 26" (tutorial-3, a live training, September 2026).
- **How it got there**: the creator gave a timestamp; it was trusted to the frame (26.4 s) and turned out to be a privacy leak, not a cosmetic fault.
- **Ruling**: no creator quote; a measured rule.
- **Receipts**: `content/reference/workshop-edit.md`; your content rules (the full-resolution frame check).
- **Where it lives now**: shared.

### A3. The share seam can move in the middle of a tape
- **Final method**: measure the seam between the share and the participant strip every 10 seconds, take the narrowest value for the whole cut, and lose window chrome instead.
- **Tried and dropped**: a crop fixed at the first measurement (2026-09-16, tutorial-4, a recorded workshop): the share is 1669 px wide until about 29:30 and 1621 px after, so 48 px of attendee tiles leaked across the back half.
- **Same failure later, a different surface**: tutorial-5, a live training, 2026-10-21: the deck crop line was fixed, the browser window sat lower, and a URL bar with a local path showed for 0.6 s; the fix was not a blur but a switch to the 3-camera layout over tape 2429.5 to 2430.5 (that cut's first review).
- **Ruling**: no creator quote; measured.
- **Receipts**: `content/reference/workshop-edit.md`; tutorial-5's first cut review.
- **Where it lives now**: the moving seam is shared (`content/reference/workshop-edit.md`). The 21 Oct case and its "switch the layout off the screen" fix were only in that cut review and a work-log row.

### A4. ffmpeg boxblur radius caps fail silently
- **Final method**: `luma_radius` at most 24; `chroma_radius` at most half the chroma height of the region (12 on a 48 px strip). In the 27 Oct shorts pipeline the extension's blur radius follows its height: 40 at 90 px and over, else height/2 - 1, power 1.
- **Tried and dropped**: radii over the cap; 2 render failures in September (`content/reference/workshop-edit.md`). It came back on 2026-10-28: "a bounded panel leaves a 2 px faded extension and boxblur 40 cannot run on it" (the build log, row 59).
- **Ruling**: none; measured.
- **Where it lives now**: shared (`content/reference/workshop-edit.md`, your content rules). The October repeat shows the shorts builder did not read it; the height-based radius rule was only in the build log. `examples/workshop-edit/build.py` validates the caps before it renders.

### A5. Blur windows on moving footage are derived from OCR, not from a detector or a hand list
- **Final method**: an `expo_scan.py` crops each band, OCRs it at 2 fps across every kept second, and emits a window only where private text is legible, padded outward. Measured: 7 sidebar windows, 70 s, where the hand list had 142 s.
- **Tried and dropped** (all September 2026, tutorial-4 rebuild):
  - dark-pixel ink, background colour and row-structure detectors all failed; row structure shipped and fired on numbered answer lists, so 95% of the blurred runtime had nothing private and about 90 of 800 seconds of teaching were smeared;
  - hand-editing the windows off the audit list then dropped a real open sidebar at raw 2700 listing 15 private and client conversation titles.
- **Ruling**: the creator, 2026-09-16: "being careful that you're not blurring something that you shouldn't or for too much time such that it blurs things that are useful for the viewer (which actually happened several times)." (that video's cut-feedback file, the verbatim block).
- **Receipts**: `content/reference/workshop-edit.md`; the `expo_scan.py` docstring.
- **Where it lives now**: shared, `content/reference/workshop-edit.md`. The fact that 3 detectors were tried before OCR was only in the `expo_scan.py` docstring. The script sat in one episode's folder; no shared file said "copy it for the next video".

### A6. Sampling rate for an exposure check: 1 s or finer, at full resolution
- **Final method**: an exposure check on moving footage samples at 1 s or finer; review one vector at a time, each at its own rate (blur at 1 s inside every window and 3 s outside; seams at -0.6, -0.2, +0.2 and +0.6 s; captions 1.5 s, suspect stretches 0.4 s). A screen share is sampled at 1 fps at full resolution before the first render, assuming the browser is the creator's own.
- **Tried and dropped**: an OCR sweep at 5 s missed a 1.8 s exposure of the creator's private skills list (September 2026). A 100-frame board over 800 to 900 s (2026-09-16). On guest D's episode (2026-09-16) "her own tabs only" was cleared off 2 frames; the full-resolution review then found the omnibox with one of our email subjects, YouTube Studio rows, the creator's logged-in LinkedIn and his search history.
- **Ruling**: the creator, 2026-09-16: "100 screenshots of 800 to 900 seconds of videos might give you a general idea... You need to adversarially attack different vectors of the video itself, including the layouts, transitions, and captions." (`content/reference/workshop-edit.md`).
- **Receipts**: `content/reference/workshop-edit.md`; `content/reference/podcast-edit.md`; your content rules.
- **Where it lives now**: shared in 3 files. **Conflict an editor will hit**: `.claude/skills/cut-review/SKILL.md` told the reviewer to pull a contact sheet at `fps=1/10` (1 frame per 10 s), and the podcast deep pass samples "a frame every 5 seconds" (`content/reference/podcast-edit-runbook.md`, the "What the deep pass actually checks" table). Neither named the 1 s rule. `content/taste/editing-checklist.md` had no privacy item at all.

### A7. Crop rather than blur where you can
- **Final method**: on a Zoom local recording crop below the browser bar and put the deck full frame, presenter picture-in-picture (`content/reference/workshop-edit.md`). On a share with a webcam column, "cropping the column off is usually the whole fix" (your content rules). On a guest's share, hold the last clean frame over private spans (`overrides.json` `freezes`) and crop 110 px off the top (`content/reference/podcast-edit.md`). When the private thing is on screen too long to crop, cut to the camera layout instead (tutorial-5, A3).
- **Tried and dropped**: a frame cleared on 2026-09-08 as "clean, no names anywhere" carried an attendee's face and name in a webcam tile, and a second an undimmed sidebar of conversation titles.
- **Ruling**: measured, 2026-09-08 (the full-resolution frame check in your content rules).
- **Where it lives now**: shared (your content rules; `content/taste/must-dos.md` row 20).

### A8. A workspace surface going on camera is rebuilt clean, never blurred in motion; a page clearing check
- **Final method**: copy the real page's own file, turn every person's name into who they are ("a podcast host"), remove client names, replace every figure with one of the same shape, record that copy. A `clear_page.py page.html [--figures figures.txt] [--allow "<host>,<co-host>"]` must pass: it reads the rendered text with every tag stripped and every HTML comment, and refuses (exit 1) on paths, emails, phone numbers, meeting or message ids, any full name from your contacts, a client from your deal list, or a figure from the figures file. Then the full-resolution look at the PNG, then a separate adversarial reader that did not build the page.
- **Tried and dropped**: blurring the real page in motion, rejected on 2026-10-03 on the measured failures of A2, A5 and A6 plus the radius caps (A4).
- **How it got there**: 2 pre-record checks come from an 18 Sep incident on a case-studies page: a heading grep found 1 case study where 3 were on the page, and a build comment carried 3 workspace paths and a contact's name. The tool was built 2026-10-07 for the co-host's long form. The co-host's shorts builder swaps a real page behind her bubble for the cleaned copy with `--page <png>` (2026-10-07).
- **Ruling**: the co-host, 2026-10-03 (the rebuilt-clean rule in your content rules). A starting default: rebuild and record a clean copy; never blur a real page in motion.
- **Where it lives now**: shared (your content rules, a routing line in your `CLAUDE.md`, the script under version control).

### A9. Stills from calls and podcasts: a face and label blur script
- **Final method**: a `blur_frame.py IN.png OUT.jpg [--text] [--keep x,y,w,h] [--box x,y,w,h] [--report]`. macOS Vision face detection (a small Swift helper, compiled once into a cache folder) plus OpenCV Haar as a second net; each face box widened over hair, ears and chin, then pixelated and blurred; an inverted OCR pass for Zoom name labels; `--box` for what it missed. Its output is "a first pass, never a clearance" (its docstring).
- **Tried and dropped**: Haar alone missed faces under caps and glasses on the first run (2026-09-30).
- **How it got there**: a stills board, 2026-09-30: 44 real frames blurred, hand boxes on 10. The adversarial full-resolution check then failed 9 of 67: T-shirt logos (C1, C16, C21), a certificate with a first name (C2), an office wall logo (C3, C23), family photos (C20), a logo tile (C9, C36); all 9 blurred plus a poster and book spines. So detection covers faces and labels; logos, certificates, family photos and book spines need a human or an adversarial reader's look.
- **Second use**: a masterclass lessons page's stills, 2026-10-07: webcams, tabs and paths cropped, the editor's projects screen blurred (8 conversation titles).
- **Ruling**: the creator, 2026-09-30, "a pic of the meeting with faces blurred".
- **Where it lives now**: the script's docstring carries the method. No shared taste or rules file named the script, and the "logos, certificates, family photos" miss list was only in a work-log row.

### A10. Recorded tutorials and masterclasses on real screens (the editor's lane)
- **Final method (pre-record)**: must-do row 3, "Clear the screen": sidebar collapsed, project picker and conversation titles out of frame, browser tabs with local paths closed, mail connectors off (`content/taste/must-dos.md`).
- **Final method (post, when the tape already carries it)**: blur by default anything that could name a client. The editor's method on tutorial-2, 2026-10-24: OCR every second of the finished cut (408 frames), measure the word boxes, and pixelate each box on its own seconds with an ffmpeg filter graph of `crop=W:H:X:Y,scale=W/24:H/24:flags=area,scale=W:H:flags=neighbor` then `overlay=X:Y:enable='between(t,A,B)'`, 21 boxes; encode `h264_videotoolbox` 30M, audio copied; OCR every second of the export to prove 0 private strings. The filter graph is kept as a `.filter` file beside the video.
- **Tried and dropped (24 Oct, 7 renders)**: the detached helper split the file path on its spaces; the first boxes were 1 s late "because frame 1 is t=0"; then 3 widenings of the boxes.
- **What it covered**: an API key warning from 3:35 to 3:58 ("cannot ship" in the tape notes), the desktop app's sidebar, a Finder username, the browser's tab strip and address bar. Row 3 of the must-dos had not been followed on that tape.
- **Rulings**: the creator, 2026-10-08, on a recorded call: "When I show all my files, it's very hard to say what yes and wait, what no. So always blur. Like for example, I know that's a real [client] at the top, but you don't. So just blur everything by default." (`content/taste/kinds/tutorial.md`). The creator, 2026-10-15: "Just the names. We need to blur the names." (`content/taste/kinds/masterclass.md`, the LinkedIn names on a masterclass). The editor's guideline: "Proof is shown on screen, never claimed, and blurred where it names a client". A starting default: blur anything that could name a client, by default.
- **Where it lives now**: the 2 rulings and must-do row 3 are shared. The editor's pixelate recipe, the OCR-measured boxes, the t=0 off-by-one and the spaces-in-path failure were only in 2 work-log rows and the `.filter` file (no comments). No shared file said how to blur a finished tutorial.

### A11. Privacy crops in the 27 Oct shorts pipeline live in the spec, per short
- **Final method**: every spec carries `people.<role>.crop` (and `crop_hard: true` where a webcam bubble edge is a real edge) so a guest's burned name tag, a framed photo or family photos stay out; a webcam bubble crop is set inside its rounded corners so the board behind never shows.
- **Tried and dropped (2026-10-27 and 28)**: the crops sat in the finders' notes, not in the specs, so guest S's burned name tag, guest T's framed photo and guest M's family photos shipped in renders (row 20). Guest S's F1 repeated it because F1 had no crop while its 4 siblings did (row 53). A crop allowed to rise above the bubble showed the Miro board over the host's hair (rows 47 to 49, crop finally `[1520,700,350,310]`). A tutorial-7 short's burned caption was blurred and its chip moved through `people.host.mask` (line 22).
- **Ruling**: none recorded; conductor fixes.
- **Receipts**: the build log, lines 22, 38, 113, 120, 128, 136.
- **Where it lives now**: only in the build log. Not in `shorts-formats.md`, the shorts-editor skill or `kinds/short.md`.

### A12. A third party who is not seen, heard or named needs no consent; anonymise a voice only
- **Final method**: the consent test is whether they are seen, heard or named in the cut. Where their speech makes the short better, keep it and pitch-shift their voice only through ElevenLabs. The full-resolution frame check still runs.
- **Ruling**: the creator, 2026-09-23: "If someone is not seen, heard, or named, then what do they need to give consent about? If the short is better because of their speech and needs to be heard, then we can change the voice pitch to become anonymous (not creepy, just a voice change that maybe elevenlabs can do, and only on the other person's voice)." (the third-party-consent rule in your content rules).
- **Where it lives now**: shared. No script or worked example of the voice change was found (see `sound.md`, "Anonymising a third party's voice").

### A13. A landscape short is never letterboxed on a blurred copy of itself
- **Final method**: crop to the speaker so the face fills the frame. Since 27 to 28 Oct the only blur in a short is the faded extension under the face panel, the bottom 15% since 28 Oct ("Blur stays low on the frame"), plus, on the Instagram looks, the blurred picture beside and above a crop narrower than the frame (`picture.md` 34).
- **Tried and dropped**: wave1-05 (2026-10-03): the whole landscape plopped onto a blurred background, the creator's face too small; rebuilt as wave1-05-v3 with "no blur anywhere". Round-1 shorts (2026-10-27): blur at 26 to 32% of the frame, failed 14 of 14; made a default of 20%, then 15% (2026-10-28; the build log, rows 170 to 181).
- **Rulings**: the creator, 2026-10-03: "my issue is that I am too small. You took the whole landscape and just plopped it in... It is not just arranging, it is transforming." (`content/taste/shorts-formats.md`). The creator and the editor, 2026-10-27: "blur only the bottom 20%"; 2026-10-28: "Blur stays low on the frame" (`content/taste/shorts-formats.md`). A starting default: the face fills the frame, and the only blur is a low extension.
- **Where it lives now**: shared. The 15% figure the pipeline now uses was only in the work log and the build log; the shared file said 20%.

### A14. check_safe_area.py can read the blurred extension as a face
- **What happened**: tutorial-5 short A, 2026-10-21: `check_safe_area` (`.claude/skills/shorts-editor/scripts/check_safe_area.py`) flagged a chin below y 1500 at 11, 14, 15, 43 and 64 s; the box was the blurred background copy, the real face band ended at y 1190 (that short's first cut review). Marked a pass by hand.
- **Where it lives now**: only in that cut review. The shorts-editor ERRORS table (`.claude/skills/shorts-editor/SKILL.md`) did not carry it.

---

# TOPIC B: the pipeline, shorts and long form

### B1. How clips get picked
- **Final method**:
  - The moments are the creator's: every teaser and short candidate goes to him as its own rendered clip before anything is assembled; an unanswered pick stays open; a rule is not a pick (`content/reference/podcast-edit.md`).
  - Narrow before the options page: a `moment_shortlist.py rank --spec <options/spec.json> --transcript <options/transcript-fixed.md>`, 6 scores (hook 3, stands alone 3, payoff 2, topics 2, speaker clarity 2, length 2), cap 12 moments, never more than 15, page about 30 clips, dropped moments listed as 1 text line each (`content/reference/podcast-edit.md`; the weights are proposals).
  - Trailer moments are a hook or a punchline only; over about 8 s needs a reason (`content/reference/podcast-edit.md`).
  - Cut for the sauce: name the one thing a viewer saves the short for and make sure it is in (`content/taste/shorts-formats.md`).
  - Keep the whole bit: setup before the laugh (a demo short's cut-feedback file).
  - The co-host's recordings only: a shorts-finder skill (readers, marker, faster-whisper edge check, energy, an adversarial ranker), not in this pack.
- **Tried and dropped**:
  - Planted "pause-bracketed zingers" (August): on one raw (2026-08-21) most lines ran 2 to 5 takes with the editor talking through them, and the best material was never in the brief; zingers became co-creation in the interview (2026-08-21) and the brief's zinger table was replaced by a key-lines slot (2026-08-24).
  - 116-clip options pages (guest Z) and 83 to 112 for other episodes, dropped 2026-10-21 (`content/reference/podcast-edit.md`).
  - One format repeated 10 times (2026-10-19, `content/taste/shorts-formats.md`).
  - Machine picks from the transcript called "decided" in a hand-off (guest G, 2026-10-13, `content/reference/podcast-edit.md`).
- **Rulings**: the creator, 2026-10-13: "We had a major fuck-up in the [guest G] video because I never actually made the decisions on frames, intros, and key moments to highlight in the teaser or capture." The creator, 2026-10-21: "you're going to need a better method than running a massive amount of clips for each podcast". The creator, 2026-10-27: "again, too long, we just need hooks or punchlines for the trailers." A starting default: the creator picks every moment, from a shortlist of about 30 clips.
- **Where it lives now**: shared (`podcast-edit.md`, `shorts-formats.md`, `cut-feedback/`). **Stale line an editor will hit**: `.claude/skills/shorts-editor/SKILL.md` still named "Planted-zinger timestamps from the video's brief (... the zinger table)" as an input, while `.claude/skills/cut-review/SKILL.md` said "never against a zinger table the brief no longer has".

### B2. EDLs
- **Final method**: shorts: a hand keep-EDL of the clean take of each sentence for multi-take raws, each `end` extended +0.2 or 0.4 s, then `cutjoin.py` (concat filter, not concat copy) (`.claude/skills/shorts-editor/SKILL.md`). Podcasts: an EDL builder writes `raw/edit/edl.json`; silence 1.0 s tightened to 0.6 s, no sliver under 1.2 s (`content/reference/podcast-edit-runbook.md`, step 5). Repairs are data in `overrides.json`, never edits to a build script (`content/reference/verify-loop.md`, Standing rules). A condensed workshop cut is pure subtraction in tape order (`content/reference/workshop-edit.md`). A retaken intro replaces the first take whole (`content/reference/podcast-edit.md`).
- **Tried and dropped**: `make_edl.py` on multi-take raws (director's notes ended up in the voice-over); a generic renderer that doubled the path and forced `scale=1920` (OOM) (`.claude/skills/shorts-editor/SKILL.md`).
- **Where it lives now**: shared.

### B3. Transcription engine and keyterms
- **Final method**: ElevenLabs Scribe `scribe_v2` with `--keyterms-file keyterms.txt` (hosts, guest, companies, products); Deepgram `nova-3` with the same file as fallback; local faster-whisper last, it takes no keyterms. Engine named in the output header. `--force` when an output name is reused (cache on filename). Transcribe once and copy when 2 versions share the audio. Scripts: `.claude/skills/shorts-editor/scripts/transcribe.py`, `transcribe_deepgram.py`, `transcribe_local.py`.
- **Measured**: guest K, 2026-09-09: `scribe_v1` misspelled both the guest's and the host's names; `scribe_v2` with keyterms got both right. Bench 2026-09-21: guest R, Scribe 17/17, Deepgram with keyterms 16/17, whisper 11/17; bare Deepgram 12/21 and 13/17 (`content/reference/podcast-edit.md`).
- **Tried and dropped**: whisper as default (2026-09-03: it missed "with em dashes and everything" and rendered the host's name as a nonsense phrase into a shipped v1, `.claude/skills/shorts-editor/SKILL.md`); find-and-replace after transcription (`content/reference/verify-loop.md`, Standing rules); Deepgram nova-2 with legacy keyword boost: it scored best on "did the name appear" by jamming a keyword in where nobody said it (a guest's name dropped into a line about a chatbot) (2026-09-21); keyterm boosting could not pull 4 engines toward a product acronym at 30:00 (2026-09-18).
- **Quirks**: Scribe is not deterministic on numbers ("30" against "thirty" on bit-identical audio, 2026-10-06, `.claude/skills/shorts-editor/SKILL.md`); Deepgram writes numbers as words and its word ends run into the next start, so cut on starts (`content/reference/podcast-edit.md`). A Scribe word lasting 51 s ("Got", 3226.06 to 3277.72) broke a speaker check; `load_words` now skips any word over 4 s (the build log, row 55, 2026-10-28).
- **Ruling**: the creator, 2026-09-03: "When you want accurate transcriptions with clear timestamps, you need to use ElevenLabs." Deepgram declared the fallback by the creator, 2026-09-21 (`content/reference/podcast-edit.md`). A starting default: Scribe with keyterms, Deepgram as fallback, whisper last.
- **Where it lives now**: shared (`content/reference/podcast-edit.md`, `.claude/skills/shorts-editor/SKILL.md`, the runbook step 2). Not shared: the keyword-boost trap and the 4 s word artefact.

### B4. Cutting on word boundaries
- **Final method**: the transcript is a search index, never evidence. Before the EDL: `silencedetect` on the source and `verify_speaker.py` on any self-description. For each in, out and splice point dump the window to 16 kHz mono and read 10 ms RMS (onsets jump from 1 to 4 to 200+). Long form: snap to measured audio energy, 20 ms windows, -38 dBFS, 3 quiet windows, cap 1.5 s, 0.05 s pad, only real cuts move (`content/reference/workshop-edit.md`). A pause is cut only between 2 transcript words where at least 0.6 s is measured quiet (`content/reference/workshop-edit.md`). After a dropped stutter the in-point sits at the dip right before the kept word; a doubled word in the re-transcribed cut is a fragment until proven otherwise (`.claude/skills/shorts-editor/SKILL.md`). A cut edge is a floor for the piece that resumes after it (`content/reference/podcast-edit.md`). Layout switches move to the nearest 0.12 s gap within 1.5 s (`content/reference/podcast-edit.md`).
- **Tried and dropped**: whisper boundaries (a testimonial, 2026-09-01, drift up to 0.5 s, 4 clipped words and 130 ms of a removed clause, `.claude/skills/shorts-editor/SKILL.md`); Scribe word spans as snap points (they hang the trailing pause on the word, `content/reference/workshop-edit.md`); silence-map trimming at -38 dB (clipped 5 words in a 9-minute live cut, 2026-09-25); silence_keep at -30 or -32 dB (eats releases); frame-grid rounding of every boundary (guest Q, 2026-10-22: 12 one-frame holes where segments touch on the tape, 2 inside words; fixed by rounding only where the tape jumps).
- **Ruling**: the creator, 2026-09-04: "I just gave you access to ElevenLabs ... it might be helpful for the word boundaries." after "clean up the endings of each clip because the words get cut off" (guest X's shorts cut-feedback file, round 3 notes); the third time he asked.
- **Where it lives now**: shared, except the guest Q frame-grid holes lesson (work log only) and the shorts pipeline's "quietest 5 ms before the start, 30 ms guard" snap (the example's README, method notes item 4).

### B5. The verify loop and the deep pass
- **Final method**: 3 tiers; repairs are data; every finding carries a rebuild scope; stop rather than repeat a repair a 4th time; promote an invariant into the generator; a build step never rewrites unchanged output; green is never done (`content/reference/verify-loop.md`, Standing rules; `scripts/verify_loop.py`). The podcast deep pass's `--gate` refuses upload unless green at full coverage (the runbook, steps 11 to 12). Compare every output against the previous one: v5b came back byte-identical (2 `'twelve-v5'` keys in one dict, `content/reference/workshop-edit.md`).
- **First run found** (2026-09-09): loudness -16.4 LUFS, 5.33 Mbps oversize, captions over a card, and 0.114 s A/V drift that was a step at every stream-copy join (`content/reference/verify-loop.md`, "What the first run actually found").
- **The editor's own finding, 2026-10-13**: both of guest G's loop's audio-against-picture checks were blind to a constant whole-file offset, and a 1.5 to 2.3 frame lag shipped; `verify.py` fires `av_drift` only on a duration mismatch over 0.10 s and `caption_drift` only on a median over 0.30 s (the editor's guidelines file; guest G's adversarial run 4).
- **Where it lives now**: the loop is shared. The editor's constant-offset finding was only in the editor's guidelines file (and cut-review reads only its newest 3 entries); `content/reference/verify-loop.md` did not carry it. Related shared rule: sync is proven against the original tape (`content/taste/editing-rules.md` rule 11, the co-host, 2026-10-22).

### B6. Cut-review: findings that kept repeating
- **Final method**: cut-review runs before any cut reaches the creator (the creator, 2026-09-23: "Cut review always has to run before it is presented to me.", your content rules); a pass is mechanical and never calls a cut ready (`.claude/skills/cut-review/SKILL.md`); the end-of-run review is a separate sub-agent on the strongest model, with a high-effort fallback when it is out.
- **Repeats, each with where it is now fixed**:
  - Mouth or caption in the bottom band (a consult short v2, 2026-09-23): `check_safe_area.py` moved to y 1500 with a face test (`content/taste/shorts-formats.md`).
  - Captions bridging a cut or a shot change: wave 1, 2026-10-03; guest G's teaser and then 19 body captions, 2026-10-20 (`content/taste/shorts-formats.md`, `content/reference/podcast-edit.md`).
  - Caption size after a font change: every short of a week shipped about 25% small (2026-09-28 to 10-03) (`content/taste/shorts-formats.md`).
  - Opens or closes mid-sentence, 7 of 14 guest Q options; a burned option label on all 14 (2026-10-20, `content/taste/shorts-formats.md`).
  - Named person off screen (guest Q, 2026-10-22; guest U's laugh 2026-10-27) (`content/reference/podcast-edit.md`).
  - Privacy leaks found by the reviewer, not the builder: guest D's share (2026-09-16), tutorial-5's URL bar and YouTube subscriptions sidebar (2026-10-21, its first cut review).
  - Round-1 shorts 2026-10-27: 14 of 14 failed on 6 shared causes (blur 26 to 32%, faces small, 1-word caption flashes, a card that never leaves, a credit over the mouth and type under 44 px, hook 2 not matching the title), made pipeline defaults.
- **Contradictions inside the shared files**: `cut-review/SKILL.md` said the safe-area bottom is y 1680 (the retired line); `shorts-formats.md` and the shorts-editor skill say 1500. `editing-checklist.md` item 9 said "One CTA per video, around the 35% mark", while cut-review said "his recorded placement, never the framework's ~35% default". The checklist had no privacy line. **[Fixed 2026-10-29: cut-review now says 1500]** **[CTA ruled 2026-10-29: between 30% and 40%, the creator; checklist and cut-review agree. A starting default you can change in your taste file]**
- **Where it lives now**: mostly shared; round-1 causes are in `shorts-formats.md` Rounds 2 and 3 as rulings, the causes list itself in the work log.

### B7. Render reliability
- **Final method**: `scripts/render_detached.sh start <name> --watch <dir> -- "<command>"` for anything over 10 minutes; `status`, `tail`, `stop` (stop kills the process group); every `-loop 1` input carries `-t` plus `shortest=1` and `-framerate 30`; never a finite PNG sequence over a different-fps stream; "working" means the output file is growing; nothing killed while a render runs; width 4 beats 8; serial overnight queue (`content/reference/render-reliability.md`, `content/reference/podcast-edit-runbook.md` section 1, `.claude/skills/shorts-editor/SKILL.md`).
- **Also shared**: never stream-copy a concat of h264 pieces (shuffled frames at boundaries, 2026-10-08, `content/reference/workshop-edit.md`); `loudnorm` never in the final graph of a clip cut with `-t` (`content/reference/podcast-edit.md`); `-nostdin`, bounded wait 60 s + 3x duration, 1 retry (`content/reference/podcast-edit.md`); concurrent artwork writes shortened a shot, check `nb_frames` (2026-10-04); a cut in a finished master is a splice, not a re-render (a `splice_full.py`, 2026-10-22) (`content/reference/render-reliability.md`, last 2 sections).
- **Disk and memory**: on the main machine, the 2026-10-22 rule "only a recording mode holds a render" was replaced on 2026-10-27 by day and night limits and a 15 GB freeze (how the shorts build lived with it is B11 below); the co-host's machine kept a memory brake and a 25 GB floor (`content/reference/render-reliability.md`, overnight section). The editor's runbook still said preflight wants 25 GB free (`content/reference/podcast-edit-runbook.md`, sections 1 and 6); which rule the editor's machine ran was not stated anywhere. Lesson: write down which disk rule each machine runs.
- **Not shared, learned on one machine**:
  - The editor's machine renders 3 to 4x slower: the stall guard (60 s + 3x piece length) killed 5 pieces; widened to 120 s + 8x (2026-10-12). The shared rule still read 60 s + 3x. **[Fixed 2026-10-29: `content/reference/podcast-edit.md` now carries 120 s + 8x for a slower machine]**
  - A command handed to the detached runner is re-parsed by the shell: `|` in end-card text lost the first command (the co-host, 2026-10-07: "the runner now gets a script file"); a path with spaces was split (the editor, 2026-10-24). `scripts/render_detached.sh` builds the job as `JOB="$*"`, which is consistent with both (a reading of the code, untested). Lesson: put the chain in a script file and pass that.
  - `render_detached.sh stop` on a runner kills its whole group, including builds it started: 6 shorts died mid-render (the build log, line 85, 2026-10-27).
  - Mixed SAR refuses the concat filter and left a 0-byte file another step accepted; fix `setsar=1` on every join input and refuse a file under 1 MB (the co-host, 2026-10-16).
  - The editor used `h264_videotoolbox` 30M for tutorial-2's export (2026-10-24) while `content/reference/render-reliability.md` listed it as not tried.
  - Disk: the editor's disk was full twice (116 MB free on 2026-10-22 with 67 GB of After Effects caches; 114 GB freed on 2026-10-12).

### B8. Uploads
- **LinkedIn thumbnail**: add the video, wait until the upload bar reaches 100%, then add the thumbnail; the thumbnail matches the video's own pixel size (1920x1080 for a 1080p video; YouTube stays 1280x720); never "post first, thumbnail later" because it cannot be edited once live; the fallback is a render with the thumbnail as the first second (your content rules). Tried and dropped: a 1280x720 thumbnail on a 1920x1080 video (2026-09-22, "We encountered a problem sharing your post"); dropping the thumbnail (2026-09-29). Rulings: the creator, 2026-09-29: "No, we absolutely have to post the thumbnail as well." and "You can't edit a thumbnail once the video is live." Untested: JPEG after 100%, PNG, lighter JPEG. Shared.
- **LinkedIn file**: a `linkedin_video_file.py` checks h264 High, yuv420p, SDR, AAC 48 kHz, faststart, under 200 MB and re-encodes to `<stem>-li.mp4` (your posting notes). HDR (HLG) as the cause of "file not supported" is a hypothesis, untested (2026-10-07). Shared.
- **48 kHz**: rebuild with `-c:v copy -c:a aac -ar 48000` as a precaution, never claimed as a diagnosis; the 96 kHz theory was wrong, the 48 kHz file failed the same way (2026-09-22, "still errored out") (your content rules). Shared.
- **YouTube collaborator**: every podcast guest's short on the channel carries the guest as collaborator; Studio's invite makes a link that must be emailed or it never arrives (guest Q's team waited 5 days, found 2026-10-28). The creator, 2026-10-23: "add the podcast guest as collaborator as well, always" (your content rules). Shared. A starting default: the guest is a collaborator, and the invite link is emailed.
- **YouTube**: you cannot swap the file on a live video, so a safe-area breach costs a re-upload (5 re-uploads on 2026-08-19, `.claude/skills/shorts-editor/SKILL.md`); proof of upload is `processingStatus: succeeded` plus a real duration (your content rules); every on-camera promise is a live URL before publish (your content rules). The daily upload quota refused a private upload with 429 on 2026-09-29; a shared integration project allowed 100 uploads a day, resetting at a fixed morning hour (2026-10-03). The quota facts were work log only.
- **Guests' own files**: every guest gets the MP4s in their own shared folder (the co-host, 2026-10-21, `content/taste/shorts-formats.md`). Shared.

### B9. What the creator rejected on review and why
- `content/taste/cut-feedback/` held 7 files: a software demo's options on screen and US commas (2026-08-17); guest X's shorts, clean audio from the episode chain, Scribe boundaries, Instagram research not done (2026-09-03 to 09-07); tutorial-4, equal boxes, captions unchecked, cut mid-sentence on a product name, blur too long (2026-09-16); a demo short dropped, context and setup cut (2026-09-30); a masterclass V5 "robotic and clunky" (2026-10-09); a masterclass's retention (2026-10-23); guest X and guest S "way too basic" (2026-10-25). All shared.
- Also shared: on guest X's live session, "youre doing too much - its just a live" (2026-10-05, `content/taste/editing-rules.md`, the live correction); "This is not really a short. This is just a crop of a recording." (2026-10-05, `content/taste/shorts-formats.md`); every section change gets a transition (2026-10-13, `content/taste/editing-rules.md`).
- **Not shared**: a masterclass edit review (2026-10-10): never put his face and the screen together (asked on 8 Oct and again on 9 Oct), 546 s of screen talk shown as face only, his hook rewritten and his on-camera promise dropped, 45 minutes cut to 26:09 unasked, one design polished 4 times at 1.2 GB each before he saw any (a review page). The editor's guidelines carried the screen-with-face part.
- Gap in the corpus itself: cut-review's retro is meant to write a cut-feedback file per review, and the editor's 22 Oct finding was "cut-feedback captured 5 times since August". The 27 and 28 Oct shorts reviews lived as opinion JSON in the build folder and as `shorts-formats.md` rulings, with no cut-feedback file.

### B10. Retention lessons from analytics
- **Final method**: judge a video on click-through, engaged views and retention, never views; 5 days is a first read, 10 days to conclude; every drop gets a why before moving on; the first minute is counted in sentences (about 5 s each) (a masterclass's retention cut-feedback file).
- **Found on a masterclass (2026-10-23, a review call)**: about 20% leave at the 13 to 20 s marketing line, cut it from the live video; the name-and-authority beat holds; "let's get into it" then 40 s of talk is the 2-minute drop; the 20x speed-ups are 2 dips, use 40x for 2 s with the reason on screen; a CTA plate with no message; 1 in 5 at halfway is good on a 28-minute masterclass. The same picture with different thumbnail words got half the click-through.
- **Earlier**: "I just talked for 40 seconds before anything changes on the screen... No bueno." (9 Oct) leading to section progress bars (`content/taste/must-dos.md` row 23); one-person podcast stretches change frame every 10 to 20 s (`content/reference/podcast-edit.md`); about-us sentences after the teaser as a measured trial with a `podcast_retention.py compare` against a saved retention baseline (`content/reference/podcast-edit.md`).
- **Rulings**: the creator, 2026-10-23: "And more than views, we're gonna want to look at engaged views. So thumbnail click through rates, engaged views and retention."; "The doing the 20x speed. Let's just not do that again. It's just losing people." (`content/taste/kinds/masterclass.md`). A starting default: judge on click-through, engaged views and retention.
- **Where it lives now**: shared (cut-feedback, `kinds/masterclass.md`, `podcast-edit.md`, `must-dos.md`). The 2 candidate rules in the retention file (a speed-up carries a reason at 40x and 2 s; the first minute cut against the graph) were marked "His to rule" and were not yet in `editing-checklist.md` or `editing-rules.md`.

---

## From the co-host's channel (added 2026-10-29)

### P1. The runner's 4 GB runaway guard kills a legitimate long form
- **Final method:** point `--watch` at the job's data folder, not the video, and bound the length with the encode's own `-t` (`content/reference/render-reliability.md` and the detached supervisor's comment, both corrected 29 Oct).
- **Tried and dropped:** watching the output video: her 60:35 live cut at 12 Mbps is about 5.5 GB, and ffmpeg was SIGINT'd at 4.33 and 4.37 GB (2026-10-08).
- **Receipts:** her render of 2026-10-08.

### P2. 20 looped PNG overlay inputs made a 2 h 15 min final; one furniture timeline made it 8.5 min
- **Final method:** one "furniture" timeline encoded as qtrle (25 distinct frames) plus 2 caption timelines, overlaid with `eof_action=repeat`, or everything after its last frame loses the plate and chip.
- **Tried and dropped:** 20 separate `-loop 1` PNG inputs in one graph (a 2 h 15 min render).
- **Receipts:** her render of 2026-10-08.

### P3. A still overlay without `-loop 1 -framerate 30 -t` makes a 1-frame video that passes the decode check
- **Final method:** every still input carries `-loop 1 -framerate 30 -t <dur>`, and every render's `nb_frames` is read (ffprobe) before it is called done; the browser's duration and a decode check both passed the broken files.
- **Receipts:** her render of 2026-10-07; a shorts retro of 2026-10-19, item 2.

### P4. Tella word timings start late and end early; retakes against parallel lists
- **Final method:** Tella's word starts run up to 0.3 s late and ends 0.2 to 0.4 s early, so cut edges come from a second transcriber (`"hard"` windows), with the tail extended by energy and a sibilant check (`EXTRA_TAIL` in her assemble step); captions keep any word that STARTS inside a span (her shorts-bar taste file).
- **Retakes:** drop a first take only when what followed it is the start of what follows the second (`restarted()` in her assemble step); the old rule took parallel list items for retakes.
- **Receipts:** her edits of 2026-10-09; a long-form retro of 2026-10-23.

### P5. A 1 fps frame check missed a black frame at all 6 joins
- **Final method:** read every join at 30 fps (the frames either side of each join), not a 1 fps sweep.
- **Receipts:** a live-recaps retro of 2026-10-15.

### P6. A whole-screen share leaks the browser bar into every recap frame
- **Final method:** crop the shared window to the page (`auto_box` in her recap compose step) before anything else.
- **Receipts:** the same retro.

### P7. A frame she names off a sheet comes from the file the sheet was made from
- **Final method:** copy a render aside the moment she starts picking; an exact pixel match reads under 1, a graded near-match 6 to 10. Run a smile scan before any thumbnail round; a 403 on a thumbnail upload can be a running YouTube Test & Compare.
- **Receipts:** her project README (the thumbnail section).

## From the 27 to 29 Oct podcast and tutorial shorts build (added 2026-10-29 evening)

"Row N" and "line N" point into the build log, kept in `examples/podcast-shorts-pipeline/README.md`; the code is in that example folder.

### A15. Tutorial screens: private masks tracked on every frame, freezes over live private spans
- **Final method**: a tutorial sidecar (`specs/<slug>/<id>-tutorial.json`) lists every private rect in `private` with source-time spans, and the check `private_ok` refuses a crop that holds one unmasked at that time. A line that scrolls is tracked on every frame by template match across every take it shows in (tutorial-2's plugin config path: 7 masks painted in the code block's colour); a panel whose shape changes (the connectors panel behind a permission box) is masked by the box's state, its header tracked per frame. Where the live span itself carries something private (a demo card with a dollar figure, a macOS dialog with a local path at 613.9 s), the screen is frozen on a clean frame (the prompt at 480.0, a slash command at 609.0) and the notes say so plainly. Bounds keep out the menu bar clock, the tabs, the URL bar's local path and Riverside's sharing bar (tutorial-5, row 164).
- **Tried and dropped**: a mask on one scroll position (943.3 to 946.65) while the lines scrolled back at 949.3 to 963.4 and their clipped foot showed in 2 other takes (row 140, the round-1 checker's extreme); bounds starting above the box, so the connectors panel (a list of connected tools) read undimmed (row 141); a 3.7x zoom that showed the command's first line, a home-folder plugin path, at 8.8 s (row 104); a spec rewrite whose new spans ran into the dialog (row 105).
- **Receipts**: rows 104, 105, 140, 141, 164; the example's README, tutorial look notes item 7; tutorial-2's F1 round-3 verdict, taste 1.

### A16. Off-limits topics get into shorts through the opener and the answer, not the pick
- **Final method**: before a render, read every opener (the aha twin's line too) and every answer piece against your own off-limits topics list in your taste files; cut an off-limits stretch from the spec (the old pieces kept as `answer_pieces_was_<date>`) and drop a card whose line is gone. An exception is the creator's word per short (2 shorts on 27 Oct, 2 more on 29 Oct).
- **Tried and dropped**: tutorial-6's M1-hook2 opening on a line from the off-limits topic (the round-1 extreme, row 150); M1 opening on a longer off-limits line, trimmed to a short neutral fragment (row 162); the hook2 and then the base carrying 14 to 22.5 s on the off-limits topic (T:214, row 216).
- **Open**: tutorial-6's F1 still opened on a line close to the topic (rows 155, 160 item 4); no line the creator said is reworded, so it was the creator's call.
- **Receipts**: rows 150, 155, 162, T:214, 216; the build log, line 132; the creator's ruling of 29 Oct.

### B11. Running a long shorts build on one machine: the render gate, the disk freeze and the runners
- **Final method**:
  - Every render goes through `scripts/render_detached.sh`. A render gate (a function the detached runner calls before it starts a job) counts render supervisors across every session: 1 in day mode, 3 at night (your render rules). So one supervisor per lane: the night runner takes `tut <spec> --layout <X>` lines too and renders tutorials inside its own supervisor (row 74); a second lane on the same queue takes lines from the end under an mkdir lock (a second runner script, `lane_runner.sh` in the example; line 281); each runner counts only its own renders, or one lane's tutorials stall the other for 15 minutes (line 444).
  - A start refused with exit 75 is the render gate, not a recording flag: read the gate's reasons before guessing (it was first misread as recording mode, lines 214 to 215).
  - A render guard freezes whole render process trees (SIGSTOP) under 15 GB truly empty and resumes them at 25. A frozen job is never killed, and no session sends SIGCONT to another session's job. So a timeout counts only the time the child is not stopped (`ps` state T, row 191); a piece's ffmpeg gets 600 s plus 30 s a second of piece, capped at 3600 (row 65); a wait inside a check (check_safe_area's 900 s) still runs out across a freeze, so a job that died during one is requeued, not debugged (line 268, row 89). A gate override file (the creator's word, valid until midnight) lifts every gate wait in any mode, the 30 GB disk wait included, but never the guard's 15 GB freeze.
  - Before each batch run `df -g /`. Under the floor, write the batch to a `HELD.md` and poll; nothing is deleted to make room (line 184). A full disk is how the main machine panicked on 27 Oct: swap could not grow, and every detached render and the planners' scratchpad died (lines 192, 202).
  - To stop a runner without killing its builds, kill its 2 supervisor bash pids first, then its python. `render_detached.sh stop` kills the whole process group (6 builds died, lines 85 and 88), and the supervisor relaunches a python killed alone, once (line 93). Never `render_detached.sh stop` a runner with builds in flight. Remove stale `building-*.json` locks (dead pid) in Python, on literal paths.
  - To pause the queue for someone else's render, move the pending lines to a hold file and let the runner idle (`requeue.py --hold`, line 248), never a placeholder process.
- **Tried and dropped**: 2 builds of one spec in one `work/<id>/` pruning each other's overlays and audio (row 1: per-tag locks, `prune_work` by look, the pid on `.part` files); 6 to 9 builds at once while superseded runners finished (lines 80, 82); a load of 300 to 500 on 10 cores, where a build took 30 to 45 minutes (lines 82, 185).
- **Receipts**: rows 1, 65, 74, 89, 185, 191; lines 85, 88, 93, 184, 192, 202, 215 to 216, 247 to 248, 268, 281, 444; the build hand-off notes ("Gotchas").

### B12. The conductor's own record-keeping traps
- `results.jsonl` holds every attempt: take the last row per id. `ok` means the machine checks passed, not that a reviewer did, and `--status` must read the rows, not the files (row 9). A short is postable only with a passing round-3 verdict written after its mp4 (the posting queue script), so any re-render of a passed short voids the pass until it is re-checked, and a requeue goes in ONE queue file only: a line in both lanes' files rendered guest C's F3 twice and voided its pass (row 236c). The done file matches whole lines, trailing spaces included, which is how a line was re-listed on purpose (row 184) and how the double render happened.
- A check that reads frames keys them on the render: `check_frames.py` takes a frame every 0.5 s through the first 5 s and the last 6 s and 1 a second between, and writes them to `check/<id>/r<mtime>-<size>/` with `CURRENT.txt`, because round 1 read a re-render through the first render's frames (row 88; the build log, line 199).
- Caches are keyed on everything that changes the picture or the sound: the face cache on the crop hint (row 52), `AUDIO_V`, `SOLVE_V`, the looks page's hash.
- A requeue deletes by exact name: `--requeue` once carried `<tag>-review.json` and removed the reviewers' machine-readable verdicts (line 46). A redo list re-queues an ok row it cannot tell is already newer than the fix (line 90).
- A field a function overrides still regresses: the specs' `credit` read the brand's company name while `credit_for` printed the guest's firm, and 6 round-3 verdicts flagged it. Every touched spec keeps its original in `specs-r<N>/` and dry-plans (`pipeline.py --plan`, `--selftest`) before a render.
- The session's clock stamps ran ahead of the machine's 9 times (the clock notes, plus row 166): read `date`. A conductor writes its state to the log and the hand-off as it goes: on 27 Oct a model usage limit ended the night conductor at about 20:30 and a second limit ended its replacement at about 22:00. Scratchpad backups die with the session, so the version-control diff is the durable record (line 61). An `rm -f` on a variable path (line 19) is why a shell rule bans `rm` on any path built from a variable.
- **Receipts**: rows 9, 52, 88; lines 19, 46, 61, 90; the build hand-off notes.

### B13. Review rounds that converged
- **Final method** (the build program, in the example's README): a checker that did not build the short reads it at full resolution against the rulings, the profile it claims and the note it answers, and writes `shorts/<slug>/<id>-r<N>.json` {pass, fixes, taste}. Up to 3 rounds; a 4th only when the checker names it extreme (a face cut, a wrong name, a private screen, a hook that does not match the title). When a round fails many shorts on shared causes, the causes become pipeline defaults before anything re-renders: round 1 failed 14 of 14 on 6 causes and every one went into code (rows 82 to 89); pass 1 failed 57 of 57 and pass 2 failed 18 of 18 the same way (lines 22, 60). A human note with no tick counts as Fix then keep (row 62); a skipped short is transformed. The checkers measured sound too (band peak, LUFS, true peak) and caught spec hygiene that a build never sees. The creator reviewed the rounds that mattered and his notes became rulings in `content/taste/shorts-formats.md`.
- **Models**: the strongest available model designed and checked, and a fallback model at high effort ran when it was out (named in each verdict). From 29 Oct evening the shorts work ran on one model only.
- **Receipts**: the build program; rows 62, 82 to 89; the `-r3.json` verdict files (at 29 Oct 20:25: 21 verdicts, 6 pass, 15 fail; guest C's F3 pass was voided by a second render and passed again 32 minutes later).

### B14. Snap, speaker and word-file traps in the shorts pipeline
- The out point keeps a word whole only when it straddles b (starts before b - 0.02, ends after b + 0.02), to its measured end plus the decay. The first rule, which kept any word starting within 80 ms after b, took the next word ('answer,' 'regardless', a stray 'Or') (rows 16, 22). A restart inside a piece is split at its own gap (guest U's F3, 140 ms, row 124).
- The speaker check reads the word files with the lips: a piece the speaker's own words cover (45% or more) and nobody else's (30% or less) is cleared; a piece another person's words cover (50% or more) while its own cover under 20% is `wrong_speaker` whatever the lips say; a one-person spec records the scores and never fails on them; a cut-in under 1.5 s that its own words cover passes over overlap (row 3; line 55). A Scribe word over 4 s is skipped (row 55).
- A one-person spec's piece whose own words cover under 30% takes the other voice's words in the Agent style with an AI AGENT chip (tutorial-7's live AI call, row 5).
- **Receipts**: rows 3, 5, 16, 22, 55, 124.

### B15. The spec shape behind the ruled order (aha, question, answer, introduction)
- **Final method**: a podcast short's spec carries `hook` (mode `aha`, played first, as answer-layout pieces of their own speaker), `question` (the stacked hook, after the aha; `question_full` plays it full frame instead), `answer`, and `intro` (the host's or co-host's introduction, at the end, full face, never a card); `aha_keys` lets the aha opener light the graphic's keys; a short with no question sets `single_hook: true` and opens on the aha line. A hook piece may name its speaker as a 3rd element (an aha piece with none is the guest's). `P.hook_start` marks where the stacked hook starts, and every page reads `hook_start` to `hook_end` as the hook (rows 70, 73, 174, 223, 227). The order is the creator's ruling: a starting default you can change in `content/taste/shorts-formats.md`.
- **Tried and dropped**: a `-hook2` twin per short (the aha version beside the question version, row 70 and the build log line 188, 27 Oct), superseded once the Round-3 order put both in one short: every podcast `-hook2` is out of the posting set, 63 marked `superseded_by` in their specs (row 195 b); the tutorial `-hook2` twins are held as hook compares, rendered only on the creator's word (row 195 d); a twin written even when the base had no question, so 17 twins opened on the same line as their base (row 73).
- **Receipts**: rows 70, 73, 174, 195, 223, 227; the build hand-off notes (the defaults table).

### B16. A detached render can hang at a piece's final flush (measured 2026-11-05)
- **Final method**: a piece runner that watches each piece's output size AND its CPU. When both are flat for 20 s, it is a hang: kill that piece and retry it, up to 4 times. The finalize passes use the same watch with 60 s and 3 tries. On the machine where it hung, the pieces and the finalize ran from the session that owned the edit, said in the work log, against the standing "long renders run detached" rule.
- **Tried and dropped**: the plain stall watchdog, which killed and retried the same piece, and the piece hung the same way again (deterministic per piece); 1 worker instead of several (hung the same); swapping `h264_videotoolbox` for `libx264` (hung the same).
- **How we got there**: the pieces of a 3-track podcast episode (1080p) hung 6 times across 3 starts of `scripts/render_detached.sh` on the editor's machine: ffmpeg at 0 CPU, state S, the output 1 to 2 s short of its length, one input's demuxer thread gone. The same command run by hand from the login session finished in 2 to 3 s. Running it by hand in its own session (`subprocess.run(cmd, start_new_session=True)`) hung too. That is what a detached launcher does: this pack's `scripts/render_detached.sh` starts the job with `os.setsid()`. So the cause is the job's own session, not the encoder, the worker count or memory (77% free).
- **Not pinned**: why the session matters (untested guesses: a quirk of that ffmpeg 9.0.1 build on macOS 27, or an end-of-file race in the filter graph that only shows without a controlling terminal). The same detached route kept working on the other machine.
- **Receipts**: the editor's work log, 2026-11-05 17:36 and 18:12; the episode's render log.
- **Where it lives now**: here and `content/reference/long-form-lessons.md` (the render errors table). If your renders hang the same way, test one piece with `start_new_session=True` before blaming the encoder.

## Where these lived before this book (29 Oct 2026), and what still waited on a ruling

Each of these lived only in a work-log row, a build folder, a per-episode folder or a script comment.

1. **How to blur a finished tutorial** (the editor's own 24 Oct method on tutorial-2): per-second OCR boxes, the pixelate filter (`scale=W/24:H/24:flags=area` then `flags=neighbor`), the 1 s off-by-one because frame 1 is t=0, widening the boxes, OCR-proving the export. Only in 2 work-log rows and the `.filter` file.
2. **The detached runner re-parses the command**: spaces in a path (the editor, 24 Oct) and `|` in text (the co-host, 7 Oct). Pass a script file. Work log only; `JOB="$*"` in `render_detached.sh` is the likely mechanism, untested.
3. **The stall guard on a slower machine**: 60 s + 3x killed pieces; 120 s + 8x worked (2026-10-12). **[Fixed 2026-10-29: `podcast-edit.md` now carries it]**
4. **Privacy crops belong in each short's spec, not in finder notes** (burned name tags, framed and family photos, a webcam bubble showing the board): the build log, rows 20, 47 to 49, 53.
5. **Stills miss list**: Vision and Haar find faces and Zoom labels, not T-shirt logos, certificates with names, wall logos, family photos or book spines (2026-09-30). The blur script was not named in any shared taste or rules file.
6. **"Switch to the camera layout" as the fix for a private screen moment**, and a crop line that fails when a window sits lower (tutorial-5's first cut review).
7. **check_safe_area reads the blurred extension as a face** (the same cut review).
8. **The verify loop is blind to a constant whole-file A/V offset** (the editor's 13 Oct finding); not in `content/reference/verify-loop.md`.
9. **Guest Q frame-grid holes**: round a boundary only where the tape jumps (2026-10-22).
10. **Transcription traps**: the Deepgram keyword-boost false positives (2026-09-21) and the 51 s Scribe "word" (the build log, row 55).
11. **Mixed SAR in a concat and a 0-byte output accepted** (the co-host, 2026-10-16).
12. **`render_detached.sh stop` on a runner kills the builds under it** (the build log, line 85).
13. **The 27 Oct shorts pipeline method** (cut snapping, face geometry, audio chain `aresample 48k, adeclip, highpass 120, lowshelf 220 -5 dB, afftdn`, the checks list, the 4 GB disk stop): only in the build's method notes and the build log (now `examples/podcast-shorts-pipeline/README.md`). `shorts-formats.md` carries the rulings, not the method. The blur default is 15% in code against 20% in the shared file.
14. **YouTube upload quota** (429 on 2026-09-29; 100 a day on a shared integration project, reset at a fixed morning hour): work log only.
15. **The masterclass edit review faults** (2026-10-10): a review page and the work log only; partly covered by the editor's guidelines.
16. **Contradictions in shared files that will mislead an editor**: cut-review's safe-area bottom y 1680 against 1500; the 35% CTA in `editing-checklist.md` item 9 against cut-review's "never the framework's ~35% default"; the zinger-table input in the shorts-editor skill against cut-review; cut-review's `fps=1/10` contact sheet and the deep pass's 5 s sweep against the 1 s exposure rule; `editing-checklist.md` has no privacy item; the runbook has no frame-check step for a guest's screen share (the rule is in `podcast-edit.md`); `render-reliability.md` calls `h264_videotoolbox` untried while the editor used it; the runbook's 25 GB preflight floor against the main machine running without it since 22 Oct, with the editor's machine not stated. **[Fixed 2026-10-29: cut-review 1500 fixed; the rest still open, the book's README "Still open"]** **[CTA ruled 2026-10-29: between 30% and 40%, the creator; checklist and cut-review agree]**

Not reached: session transcripts were not opened (only work logs, shared files, build logs and code), so a lesson spoken in a session and never written to a row is not here. No script was run, and nothing was rendered.

## From a podcast edit run in a cloud session overnight (added 2026-11-05)

A whole episode (the full cut, a shorter standalone cut, trailers and intros) was edited in a cloud session on a Linux box while the creator slept. These 6 came out of its review rounds.

### C1. libass draws a different width on another machine: calibrate where the burn runs
- **Final method**: before the first burn on any new machine, render 1 known word on a black frame through `ass=...:fontsdir=` and measure its pixel width against the layout's own measure (`textlength`). Use the ratio you get. On the Linux box the factor was 0.691 against 0.63 on the Mac.
- **Tried and dropped**: the Mac's calibration carried to the Linux box. libass drew a word 436 px wide where the layout expected 398, so every caption lost its word gap and the letters ran together (a review block on the first cut).
- **Receipts**: the cloud session's review round 1, block 2. **Where it lives now**: here and `captions.md` 50.

### C2. 2 builds sharing one content-keyed piece cache race each other
- **Final method**: run builds that share a piece cache one after the other, or give the second build its own cache folder.
- **How we got there**: the full episode's build, the shorter cut's build and both pick renders wrote into the same cache. When 2 wanted the same key at once, one finished and the other's temporary file was gone (`FileNotFoundError` on `os.replace`, 3 times in one night).

### C3. Keep the raw tracks until the finals have passed cut-review
- **Final method**: when disk runs short, delete the piece cache and the intermediates first and the raw tracks last.
- **How we got there**: the raw tracks were deleted for disk after the first finals rendered. Cut-review then asked for a different body start and a layout change on the goodbye, and the new pieces needed the raw tracks again (a 15-minute download).

### C4. An opener that carries the welcome means the body starts after it
- **Final method**: when the title card's audio already holds the welcome line, the body starts on the next sentence.
- **How we got there**: the title card's audio and the body both started at the same second, so "Hey, welcome back" played twice (a review block on the first cut).

### C5. The bed level is measured on this tape's trailer, never copied from another episode
- **Final method**: measure bed against voice on this episode's trailer windows and set it to sit about 19.5 dB under.
- **How we got there**: another episode's level put the bed 4.7 dB under the voices here, because these voices measured about 15 dB quieter before loudness normalization. 2 measures landed it at 19.5 dB under.

### C6. A paid listening pass that fails is named, never stood in for
- **Final method**: when an AI listening pass is refused (here a prepaid-credit error, HTTP 402 `RESOURCE_EXHAUSTED`, on every trailer moment), say so on the page. A loudness (RMS) flag is a stand-in, not a listen.
