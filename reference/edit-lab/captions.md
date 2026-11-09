# Edit lab: captions, highlighting, cards, safe areas, fonts

> Part of the edit lab book, `content/reference/edit-lab/README.md` (what was tried, what failed, how the version that works was reached). Each lesson: final method, what was tried and dropped, how we got there, the ruling, receipts, and where the rule also lives. A new lesson learned while editing is added here in the same session (README, "Keeping it alive").

First written 2026-10-29 by a read-only sweep of the build logs, the taste files, the podcast runbook, the shorts-editor and cut-review skills and the build folders. Receipts name the kind of evidence (a review, a measurement, a build log row, a round-3 verdict) and its date. "The build log" is the shorts build's log, whose lessons are in `examples/podcast-shorts-pipeline/README.md`; "row N" is one of its numbered fixes. Guests are letters, tutorials are numbers, and a ruling quoted here was the creator's taste: take it as a starting default and change it in your taste file.

---

## A. Karaoke captions (per-word highlight)

### 1. Per-word highlight renders in one libass pass, never frame by frame
- **Final method:** pure ASS karaoke events burned through libass (`subtitles=`/`ass=` filter) in one pass. Podcast episodes: a `captions_karaoke.py` in the episode build, named in the podcast runbook. Style block that "should stay": `Y_BASE 862 / SIZE 62 / CALIB 0.63 / GAP 24 / MAXW 4`.
- **Tried and dropped:** a frame-by-frame PIL karaoke path (guest O's episode). Why: it "took hours and hours to render... because I think it was frame by frame" (the creator, guest X teaser v1 review, 2026-08-29).
- **How we got there:** 5 ASS-karaoke caption styles were rendered at about 4 s a burn against hours frame by frame (2026-08-29).
- **Ruling:** *"Figure out a great, attractive, sophisticated set of captions that we can use that don't take forever to render, and then show me five different styles, libraries, and vibes."* The creator, 2026-08-29.
- **Receipts:** the creator's teaser review, 29 Aug; the 5-style bench render the same day.
- **Where it lives now:** `content/reference/podcast-edit.md` (captions), `content/reference/podcast-edit-runbook.md` (captions step).

### 2. Pin the base colour or the karaoke runs backwards
- **Final method:** put `\1c&H00FFFFFF` before the `\t(...)` colour transitions on every karaoke line.
- **Tried and dropped:** emitting `{\t(k0,k0+40,\c<accent>)\t(k1,k1+60,\c<white>)}word` with no pinned base. Why: libass resolves the first `\t` target for t before its start, so a line arrives all in the accent colour and drains as the words are said; the accent marks what has NOT been said. Shipped on 705 of 705 captions of the 22 Jul cut of tutorial-1 (a live workshop); found 2026-09-16.
- **How we got there:** the creator said "the captions look really weird"; a 46-agent audit found it and proved it on a bench render (all 4 words in the accent at t=0.2 s). 2 other workshop builders had always pinned it.
- **Ruling:** none needed; a mechanical fault. The symptom words: "the captions look really weird" (2026-09-16).
- **Receipts:** the 46-agent audit and its bench render, 16 Sep.
- **Where it lives now:** `content/reference/workshop-edit.md` (karaoke). Not in the podcast runbook or the shorts-editor skill.

### 3. The karaoke check must read its target colour from the design file
- **Final method:** the verifier reads the highlight colour out of `design.py`, the same file the build imports.
- **Tried and dropped:** a verifier hard-coded to the old bright accent. Why: after the palette changed it passed on a colour no longer on screen (2026-09-16).
- **Ruling:** none; mechanical.
- **Receipts:** the verifier fix, 16 Sep.
- **Where it lives now:** here. The related "preview must render through the shipping path" rule is in `content/reference/workshop-edit.md`.

### 4. Words are highlighted as they are said, and the style does not jump
- **Final method (podcast long form):** uppercase Montserrat Bold, current word in the brand accent, no scale pop, about 62 px on 1920x1080, 3 to 4 words a group, one group on screen at a time.
- **Tried and dropped:** the "Punch Pop" scale-pop style (the pop "belongs to the style demo, not the podcast", 2026-09-02); a second line stacking above the previous group (2026-08-29: *"Time it such that it can replace the previous line."*).
- **How we got there:** on guest O's episode (2026-08-26) the ask was Instagram captions with 3 or 4 words; guest X's v1 (2026-09-02) removed the pop and raised the size.
- **Ruling:** *"I like the captions of the same color and same style, but that don't jump at the viewer (like the [guest O] podcast) - font size can be a bit bigger than it is right now."* The creator, 2026-09-02.
- **Receipts:** the creator's reviews of 26 Aug and 2 Sep.
- **Where it lives now:** `content/reference/podcast-edit.md`, `content/reference/podcast-edit-runbook.md`. Note: an older line in `podcast-edit.md` describing "Main (sentence case, 3-7 word clause chunks, Helvetica...)" is the first episode's style, not the current one. **[Fixed 2026-10-29: marked as the first-episode style; the current style is the libass karaoke above]**

### 5. Shorts captions: the Instagram look
- **Final method:** white, bold, sentence case, soft drop shadow, no box, no outline, no all-caps, centred, 1 or 2 lines; the current word may lift in weight or take one accent colour.
- **Tried and dropped:** the 1 to 2 word UPPERCASE style for talking lines (banned by clip-bar Rule 1); one-word karaoke inside a long form ("One word flashes. That's too much.", 2026-08-17).
- **Ruling:** *"I really like captions when they look like the ones from Instagram."* The creator, 2026-09-24.
- **Receipts:** `content/taste/shorts-formats.md`, `content/taste/editing-checklist.md`, `content/taste/clip-bar.md`.
- **Where it lives now:** `content/taste/shorts-formats.md`, `content/taste/kinds/short.md`, `.claude/skills/shorts-editor/SKILL.md`.

### 6. Highlight a contiguous run as one shape, keep punctuation inside it (the co-host's kit)
- **Final method:** one rectangle per contiguous highlighted run per line; trailing punctuation pulled inside the marks (`[[compound.]]`).
- **Tried and dropped:** a lilac box per word (white slivers between words) and a highlighted word followed by a detached full stop ("compound ."). Found 2026-09-18 by looking at the render.
- **Ruling:** none; mechanical.
- **Receipts:** a render read on the co-host's channel, 18 Sep.
- **Where it lives now:** here and in the co-host's own editor code. Applies to any boxed highlight the editor builds.

---

## B. Caption size and fonts

### 7. The caption size floor, and why the number in px is not the number on screen
- **Final method (shorts):** measure the capital H as libass draws it. Floor 47 px capital for captions, 53 px for the first 8 s. With the static `assets/fonts/Montserrat-Bold.ttf` that means font size 104 and 118 in the wave-1 shorts builder (`wave1.py`), every other size times 4/3, wrap at 835 PIL units (about 712 px drawn). Its `check_sizes()` stops the build under 47 or 53.
- **Tried and dropped:** 52 px ("way, way, way too small", 2026-09-04); reviewers recommending smaller (76 to 62, 60 to 54) on corpus grounds (overruled: a corpus finding never overrides the creator's floor); the static Montserrat-Bold at the old sizes from 28 Sep to 3 Oct, which drew 35 px capitals instead of 47, so every short that week shipped small.
- **How we got there:** floor set 3 times (2026-08-21, 2026-09-03, 2026-09-04); measured through libass on 2026-09-24; restored wave-wide 2026-10-03.
- **Ruling:** *"you have to make captions bigger. You keep underestimating how small the fonts that you're using are. [...] The bottom captions are way, way, way too small."* The creator, 2026-09-04.
- **Receipts:** the creator's reviews of 21 Aug, 3 Sep and 4 Sep; the libass measurement of 24 Sep; the wave-wide fix of 3 Oct.
- **Where it lives now:** `content/taste/shorts-formats.md` (caption size), `content/reference/podcast-edit-runbook.md`. **Settled in the pack's copy:** `check_caption_size.py` says `CAP_FLOOR_PX = 47` (at 35 a style drawing a 36 to 46 px capital passed the gate though it was under the floor). An older example command showed `captions_brand.py ... 12 58` (size 58) while the floor is 78; the skill's command now passes 78, which that PIL renderer draws as a 55 px capital.

### 8. A font file change is a caption size change
- **Final method:** after any font or font-folder change, re-run `check_caption_size.py --style` and re-measure before rendering.
- **Tried and dropped:** swapping the variable Montserrat for the static Bold "for cloud-render parity" with the sizes unchanged (28 Sep, about 25% smaller capitals).
- **Ruling:** none; found by a final adversarial check on 2026-10-03.
- **Receipts:** the final check of 3 Oct.
- **Where it lives now:** `content/taste/shorts-formats.md` (caption size).

### 9. libass and PIL disagree on width and size; calibrate
- **Final method:** set width limits in PIL units measured against what libass actually draws: 940 PIL units drew about 715 px on the variable face (0.76), 835 draws about 712 on the static face (0.85). On guest O's and guest X's long forms, libass draws Montserrat at 0.63x the PIL size (`CALIB 0.63`).
- **Tried and dropped:** trusting PIL widths (583 PIL units drew 443 px; captions came out small and gappy).
- **Receipts:** a measurement through libass on the static and variable faces; the wave-1 builder's constants.
- **Where it lives now:** `content/taste/shorts-formats.md`, `content/reference/podcast-edit.md`, `content/reference/podcast-edit-runbook.md`.

### 10. Make libass pick the real font, not a fallback
- **Final method:** point libass at the fonts folder holding `Montserrat-Bold.ttf` (`fontsdir`), then look at a frame.
- **Tried and dropped:** a build where libass silently fell back to Helvetica (a demo short, version A, fixed 2026-09-28).
- **Receipts:** the demo short's fix, 28 Sep.
- **Where it lives now:** here.

### 11. Variable fonts in a headless-Chrome card render
- **Final method:** prove each font loads in Chrome before rendering (`check_fonts()`); do not declare a variable TTF with `format('truetype')`.
- **Tried and dropped:** `@font-face` with `format('truetype')` on variable Inter and Lexend Exa: both fell back to a condensed system face while static DM Serif loaded (2026-09-01). Also a root class `slide figure` colliding with a `.figure` rule and collapsing every word space.
- **Receipts:** a card build on the co-host's side, 1 Sep.
- **Where it lives now:** the carousel notes. Not in any file read for video cards (HyperFrames, masterclass cards), so this entry is the video copy.

### 12. Fonts on cards and titles: which families are in use and which were turned down
- **Final method:** shorts titles in DM Serif Display, money line in the brand accent at a light weight, from y=236 (`content/taste/shorts-formats.md`); masterclass cards offered in 2 type directions, A Inter 600 at 78/56/44 px, B DM Serif Display headline (the masterclass card builder, `build_cards.py`); brand labels Lexend Exa (`content/taste/thumbnails.md`).
- **Tried and dropped:** handwriting and Comic Sans-looking fonts on thumbnails (2026-10-06: *"let's remove all the Comic Sans looking fonts. Let's get serious with the fonts."*); for the co-host's open look Montserrat, Avenir Next Heavy, Inter ExtraBold, Lexend and Futura were all turned down (2026-10-07); a font change inside one caption when capitalisation changed (the creator, 2026-10-14: *"when you, like, change to the capitalization, the font also changed. Weird."*).
- **Open:** "card typography moves to Fraunces/Lexend Exa once font files are bundled" (a shorts-editor note) is still open; which masterclass card direction (A or B) to use is a choice for your taste file.
- **Receipts:** the creator's thumbnail review, 6 Oct; the co-host's font round, 7 Oct; the creator's review, 14 Oct.
- **Where it lives now:** the thumbnail font ruling in `content/taste/kinds/masterclass.md` (quote only) and the editor's guidelines file; the masterclass card fonts only in the card builder.

---

## C. Caption timing and grouping

### 13. Break lines where language breaks, never by word count
- **Final method:** score candidate breaks (sentence end, clause, real pause, speaker change) and pick the whole set by shortest path. The 2026-10-28 tutorial pipeline costs: 1-word line 1000, line under 0.3 s 500, a cut crossed 8, a function-word ending 4, width over 760 px refused.
- **Tried and dropped:** a hard 4-word chop (524 of 705 lines at exactly 4 words, "So I was in / an instance where, a / firm was trying to", 2026-09-16); greedy breaking (leaves 3-word fragments); the 2026-10-28 one-line mode with no width floor (1-word lines, lines under 0.3 s, 2 events at once stacked on the host's chin).
- **Receipts:** the 16 Sep caption audit; the build log, row 143.
- **Where it lives now:** the principle in `content/reference/workshop-edit.md`; the cost numbers in the build log (`examples/podcast-shorts-pipeline/README.md`).

### 14. No 1-word flashes, nothing under 0.3 s, nothing faster than 35 characters a second
- **Final method:** drop a caption whose reading speed is over 35 characters a second (catches clipped fragments; "Yeah." at 0.28 s reads 18 c/s and stays); on the 3-card podcast frame fold a lone word into its neighbour when same speaker and style, gap under 0.15 s, shrink at most 15%; shorts pipeline default since 2026-10-27: no 1-word or sub-0.3 s captions.
- **Tried and dropped:** a duration floor alone (it clipped a host's self-introduction, "I'm your host, [name], and", to 0.28 s, 104 c/s, 2026-09-10); 32% of guest G's groups were single-word flashes (a 13 Oct review page).
- **Receipts:** a reading-speed measurement, 10 Sep; the 13 Oct review page; the shorts pipeline default, 27 Oct.
- **Where it lives now:** the fold rule in `content/reference/podcast-edit.md`; the 35 c/s rule and the sub-0.3 s default here and in the shorts pipeline.

### 15. A caption never crosses a cut, a shot change or a layout switch
- **Final method:** every group ends at least 1 frame before any cut or layout switch and is split there (`respect_bounds` in guest G's build `captions.py`, ported to guest Q's); in shorts, every phrase ends at every cut and every crop change, with no timing grace; subtitle times snap to the midpoint between frames; `wave1.py --ass-only <out.ass>` rebuilds captions alone to prove a change on every short.
- **Tried and dropped:** the rule on the teaser only (19 body captions ran 1 to 3 frames past a cut, 2026-10-20); centisecond rounding that left the old caption on the join frame (2026-10-03); a caption hanging 80 to 250 ms under the next speaker's chip (2026-09-28).
- **Receipts:** frame reads at the joins, 28 Sep, 3 Oct and 20 Oct; the shorts fix of 22 Oct.
- **Where it lives now:** `content/reference/podcast-edit.md`, `content/taste/shorts-formats.md`. The frame-midpoint snap here.

### 16. Key captions on a word's START, not its end
- **Final method:** keep a word whose start is inside the segment and run its highlight through a contiguous seam; on Deepgram words cut on starts (its ends are the next word's start).
- **Tried and dropped:** builders keyed on Scribe's word END, which dropped audible words at every cut ("return.", "we've", 2026-09-10).
- **Receipts:** a word-boundary audit, 10 Sep.
- **Where it lives now:** `content/reference/workshop-edit.md` (word boundaries), the Deepgram note in `content/reference/podcast-edit.md`.

### 17. What never gets captioned
- **Final method:** captions drop standalone um/uh, backchannels ("Mm-hmm", "Yeah", "Okay") when the other speaker holds the floor, false starts ("c-", "jo-", "machi-"), stutter prefixes (keep "FIRST" not "FI-FIRST"), immediate repeats, quote marks, a crosstalk fragment whose words share one timestamp, anyone off screen; any 1-letter token but A or I; a hyphen-closed token under 3 letters. The audio keeps the fillers.
- **Tried and dropped:** stripping a false start's dash (shows a stray letter); 22 lone letters on guest R's round 4 (a run like "... IS THE Z", 2026-09-10); a lone-backchannel rule that also ate a speaker's own last word ("okay.", guest U, the build log, row 24).
- **Ruling:** captions only, never the audio (`content/taste/shorts-formats.md`); fillers stay in the audio (`content/reference/podcast-edit.md`).
- **Receipts:** the editor's caption rounds 4 and 5 on guest R's episode, 10 Sep; the build log, row 24.
- **Where it lives now:** mostly in `content/reference/podcast-edit.md`, `content/reference/workshop-edit.md` and `content/reference/podcast-edit-runbook.md`. The round-4/5 rules (1-letter, 3-letter hyphen, shared-timestamp crosstalk, 350 ms floor, 200 ms minimum, fades 30/20 ms) and the last-word backchannel exception live here and in the build log.

### 18. Numbers on captions
- **Final method:** numerals for spoken numbers when a unit follows; "one" stays a word as a pronoun; a number word closing a sentence stays a word ("one of the two."); money written the way the graphic writes it (a `$` figure with its own `K` or thousands separator, never a bare spelled-out number); Deepgram writes numbers as words, so a number pass first; Scribe is not deterministic on numbers, so transcribe once and copy when 2 versions share the audio.
- **Tried and dropped:** a blanket numerals rule ("see them 1 by 1" 15 times, 2026-09-16); "THE 2." (guest G); a dollar figure captioned as a bare number with no `$` (the build log, row 25).
- **Receipts:** the 16 Sep caption audit; the build log, row 25.
- **Where it lives now:** `content/reference/workshop-edit.md`, `content/reference/podcast-edit.md`, `.claude/skills/shorts-editor/SKILL.md`, except the money rule (here and the build log).

### 19. Proper nouns are fixed before the burn
- **Final method:** keyterms file at transcription (Scribe `--keyterms-file`), then `check_captions_nouns.py` over the ASS with verified names in `known_nouns.txt`; in an all-caps style a person spot-reads the intro captions, because the checker sees nothing in caps.
- **Tried and dropped:** whisper as first engine (a mishearing of the host's own name reached a v1, 2026-09-02); "AND POUNDS" for "compounds, compounds"; a context guess that swapped in a second wrong word for a misheard one (the tape settled it).
- **Ruling:** *"When you want accurate transcriptions with clear timestamps, you need to use ElevenLabs."* The creator, 2026-09-03.
- **Receipts:** the v1 review of 2 Sep; the creator's ruling of 3 Sep.
- **Where it lives now:** `content/reference/podcast-edit.md`, `content/reference/podcast-edit-runbook.md`.

### 20. Captions burn before the speed pass
- **Final method:** burn captions, then speed up (1.1x podcast, 1.05x workshop), pitch preserved.
- **Receipts:** `content/reference/podcast-edit.md`; `content/reference/workshop-edit.md`.
- **Where it lives now:** `content/reference/podcast-edit-runbook.md`.

### 21. The burn's cost is the encoder, not libass
- **Final method:** finalize with `libx264 -preset veryfast -crf 18` (135 s to 68 s and a smaller file); a subtitles burn is libass-bound per worker, so it parallelises: 8 workers beat 4 (`finalize_parallel.py --bench 4,8`).
- **Tried and dropped:** blaming the karaoke markup (measured libass 18%, encoder 70%, 2026-09-16); capping at 4 workers by core count.
- **Receipts:** a profile of the finalize step, 16 Sep.
- **Where it lives now:** the worker count in `content/reference/podcast-edit.md`; the encoder setting here.

### 22. Check the ffmpeg has the filters before planning the caption route
- **Final method:** check `ffmpeg -filters` for `ass`, `subtitles`, `drawtext`; Homebrew `ffmpeg-full` carries libass.
- **Tried and dropped:** stock Homebrew ffmpeg 9.0.1_1 had no ass/subtitles (guest R's episode, 2026-09-09); the co-host's machine's Homebrew 8.1.2 had no ass/drawtext/zscale (2026-10-27); the skill's fallback is PIL PNG caption layers, which is the slow route item 1 rules out for long form.
- **Receipts:** the editor's build of 9 Sep; the co-host's machine, 27 Oct and 8 Sep.
- **Where it lives now:** the PIL fallback note in `.claude/skills/shorts-editor/SKILL.md`; the "install ffmpeg-full" fix here. Check the ffmpeg build on every machine that renders.

---

## D. Position and the safe frame

### 23. The shorts safe frame (one frame for all platforms)
- **Final method:** on 1080x1920, nothing in the top 12% (0 to 230), captions block between y 1190 and 1500 (62% to 78%), max width 720 (x 180 to 900), nothing in the bottom 22%, right 16% dead from y 960 down; top text from y 290 (the LinkedIn 4:5 precaution). Gate: `check_safe_area.py` (top 200, bottom 1500, right 940 from y 960, face lower third below 1500 fails).
- **Tried and dropped:** captions 78 px from the bottom (90% of height, covered on every platform); the gate's old y=1680 line, which passed a testimonial short (v2) with the speaker's mouth covered at about 24 s (2026-09-23); the right-rail test at any height, which forced an unreadable 800 px board panel (fixed 2026-09-28).
- **Ruling:** *"we need to standardize to the best common denominator, where you can see the full captions in each platform."* The creator, 2026-09-16.
- **Receipts:** `content/taste/shorts-formats.md` (safe frame); `check_safe_area.py`'s header; `.claude/skills/shorts-editor/SKILL.md`.
- **Where it lives now:** `content/taste/shorts-formats.md`. An older cut-review line said "no card or caption ink above y=200, below y=1680". **[Fixed 2026-10-29: cut-review now says y=1500]**

### 24. Measure the whole caption block, descenders included
- **Final method:** place a 2-line block by its measured ink bottom (the shorts of a live training, tutorial-2, v3: overlay y 676, block bottom 1499).
- **Tried and dropped:** anchoring so the second line's descenders ran to y 1523, 23 px into the bottom band, on all 20 shorts (cut-review round 2, 2026-10-21); the co-host's captions lowered to 1510 (2026-10-07); a chunk that wraps to 3 lines growing upward into the footage strip while the check printed PASS (2026-09-11; now split past 2 lines and the check fails it).
- **Receipts:** tutorial-2's cut-review round 2, 21 Oct; the co-host's renders of 7 Oct and 11 Sep.
- **Where it lives now:** here and in the co-host's kit.

### 25. Captions sit below the mouths; cards give way
- **Final method:** check a full-resolution frame of each speaker talking; on guest P's 2-card frame caption bottom y 928 and name cards from y 944 (overlapping the frame edge by design); on the collapsed screen card caption bottom y 895 inside the well; shorts: the face is framed from the whole cut's lowest mouth (leans included), chin and mouth never below 1500.
- **Tried and dropped:** captions "a little High, such that it covers my mouth" (guest P's episode, 2026-09-28); the shorts answer panel starting at y 940 with chins at 1330 to 1390 inside the caption block (the build log, row 10, 2026-10-27); a tutorial block top 1280 with the mouth at 1270 (row 144, fixed to one line at 1420 to 1496 with `chin_clear_of_captions`).
- **Ruling:** *"the captions need to be at the right space, which is a little lower than they are now."* The creator, 2026-09-28; *"my face is a little too low... there's going to be a lower band, like the lower fifth, where nothing fits."* The creator, 2026-09-23.
- **Receipts:** `content/reference/podcast-edit.md`; `content/taste/shorts-formats.md`; the build log, rows 10 and 144.
- **Where it lives now:** `content/reference/podcast-edit.md`, `content/taste/shorts-formats.md`. The pipeline numbers (1420 line, chin pass keys) in the build log.

### 26. Captions never sit on a seam, and the word gap is visible
- **Final method:** a caption block sits clearly inside one zone, never on the seam between face cam and card area; per-word layouts add the style's per-letter Spacing and both outlines to the PIL advance (`ink_w`), visible gap 26 px; a group wider than 1500 px goes out as 2 caption frames.
- **Tried and dropped:** a visible gap of about 7 px ("looks like one long running word", 2026-09-28).
- **Receipts:** `content/taste/shorts-formats.md`; `content/reference/podcast-edit.md`.
- **Where it lives now:** both of those files.

### 27. A caption on a light ground goes in a box or turns dark
- **Final method:** tutorial style B: one line at y 1410 to 1486 in a dark box, ASS `BorderStyle 3`, 75% black, 10 px padding (the build log, row 179). For a cream page (the 22 Jul workshop): ink on cream with the accent highlight (2026-09-16).
- **Tried and dropped:** white captions on the paper ground (style I, 2026-10-28); white-on-black-outline designed for a deep-green page used on cream (2026-09-16); white subtitle on bright B-roll (a shorts-editor errors row).
- **Ruling:** "A caption on a light background sits in a box or takes a dark colour; white on light is out." The creator and the editor, styles review 2026-10-28.
- **Receipts:** `content/taste/shorts-formats.md`; the build log, row 179; the 16 Sep cream-page fix; `.claude/skills/shorts-editor/SKILL.md`.
- **Where it lives now:** the rule in `content/taste/shorts-formats.md`; the BorderStyle recipe in the build log.

### 28. Nothing on a face; the title leaves to make room
- **Final method:** bullets, cards and list stickers stack above the head from y 238; the title fades at 28 s on every short, or earlier at the first list sticker or callout, never inside the hook (`title_until`, rows 175 and 189b; the tutorial title the same, T:228); the credit's 6 s end where the introduction starts (row 232; shown on guest Q's after-M31 render: the credit 31.5 to 37.0 s, off before the co-host's introduction, round-3 verdict, taste note 1).
- **Tried and dropped:** list stickers between chin and caption line (on guest Q's face) and a callout on the forehead (2026-10-28); a credit that stayed over the co-host's introduction so a viewer read the co-host as the guest (row 187); the under-35 s exception that kept the title (row 175's reading), failed by round 3 on guest Q's F1 (34.9 s) and dropped for the literal 28 s (row 189b); 3 longer shorts then kept the title past 28 s for other causes: guest C's F1, because a story-proof short sends `hook_end` as the whole short; guest C's M2, because the drawn look had no 28 s exit; tutorial-3 B, because the tutorial title left only for the credit (T:228; the round-3 verdicts); a list row stacked at y 238 to 480 over the hair when the face sits high (guest C's M1 round 3: brow at 522), so "above the head" means above the crown, not above the brow.
- **Ruling:** "Nothing is ever placed on a face." Styles review 2026-10-28.
- **Receipts:** `content/taste/shorts-formats.md`; the build log, rows 175, 187, 189b, 232 and T:228.
- **Where it lives now:** the rule in `content/taste/shorts-formats.md`; the timings in the build log.

### 29. Captions are never regenerated by a video model
- **Final method:** do the camera move (push-in, punch) in ffmpeg or HyperFrames on the face layer before captions; captions burn last.
- **Tried and dropped:** Gemini Omni video-in/video-out on a captioned 8 s clip (2026-10-27, $1.64 each): take 1 over-zoomed, cropped the title and redrew and retimed the captions with one invented line; take 2 did no zoom and merged a caption; both re-synthesised the audio.
- **Receipts:** the 2 Omni takes of 27 Oct and the 28 Oct read ("never regenerate pixels that carry captions"); `content/taste/story-animations.md`.
- **Where it lives now:** the general rule ("a model regenerates every pixel, including the text") in `content/taste/story-animations.md`; the captions-specific line here.

---

## E. Cards, text boxes, lower thirds

### 30. Text on screen is always in a card or box (long-form masterclass)
- **Final method:** a card in a dark shade of the brand accent (`{BRAND_ACCENT_DARK}`), white words, small shadow, no stroke, loose padding, Title Case; the machine is handed the exact words, never chooses them. Built as transparent 1920x1080 PNGs by the masterclass card builder (`build_cards.py`: Inter 600 78/56/44 px, radius 36, padding 56/84); the editor places and animates them in After Effects.
- **Tried and dropped:** floating text ("now it's just floating text", 2026-10-15); orange as the card ground (the editor picked the accent colour, the creator agreed, 2026-10-15).
- **Ruling:** *"It just needs to get done the cards with the text so the text is not just floating on screen."* The creator, 2026-10-14; *"But it needs a box."* The creator, 2026-10-15.
- **Receipts:** the creator's review calls of 14 and 15 Oct; `content/taste/kinds/masterclass.md`; the editor's guidelines file.
- **Where it lives now:** as a rule only in the editor's guidelines file; the taste file holds the raw quotes (`content/taste/kinds/masterclass.md`) without the spec; the card builder only in its build folder.

### 31. One fixed Claude orange, used on Claude, numbers and 20x inside a card
- **Final method:** #D97757 on the word Claude, the numbers and "20x"; errata cards in that orange; the rest of the card unchanged.
- **Tried and dropped:** varying oranges (the creator asked it to "always be the same", 2026-10-14). The shorts-editor palette once listed "Claude orange #f0813f / bright #ffa766" (`.claude/skills/shorts-editor/references/style.md`), a different value. **[Fixed 2026-10-29: style.md now says #D97757, one Claude orange]**
- **Ruling:** *"You do have to figure out what specific color combination Claude orange is, because I just want it to always be the same."* The creator, 2026-10-14.
- **Receipts:** the creator's review call of 14 Oct; `content/taste/kinds/masterclass.md`; `content/taste/thumbnails.md`.
- **Where it lives now:** the editor's guidelines file, `content/taste/thumbnails.md` (thumbnails), `.claude/skills/shorts-editor/references/style.md`. Not in a video-card taste file.

### 32. The stage timeline is the stage card, and the current stage goes about 250% bigger
- **Final method:** the timeline drops from above at each stage, the current stage glows and grows about 250% so it reads on a phone, then goes back up; no separate stage cards; full screen with no frame at the intro, the end and the story insert.
- **Ruling:** *"This part where you're highlighting it and the text becomes bigger, it needs to be significantly bigger."* and *"I think 250 is good."* The creator, 2026-10-15.
- **Receipts:** the creator's review call of 15 Oct; `content/taste/kinds/masterclass.md`.
- **Where it lives now:** the editor's guidelines file; quotes only in `content/taste/kinds/masterclass.md`.

### 33. Free-resource lines, the AskUserQuestion label, and key-lesson cards
- **Final method:** two short yellow lines, "Free resource, no email required" about 1 s after the creator switches to the page, then "Second link below" with an arrow 0.5 s later, both gone before "you can follow along"; a term a beginner may not know gets a red-edged box with the name in quotes; a key-lesson card comes down whenever the creator says "this is a key lesson", at a section's start or end.
- **Receipts:** the editor's guidelines file; `content/taste/kinds/masterclass.md`.
- **Where it lives now:** only in the editor's guidelines file (rules) and `content/taste/kinds/masterclass.md` (quotes).

### 34. Card copy: few words, names its own subject, numerals, sized for a phone
- **Final method:** headlines of 2 to 6 words; a card never opens with a verb plus it/this/that, never spells a number, Title Case (`cards.py check()` enforces it); in a 1080x864 shorts band minimums headline 96 px, number 180 px, label 44 px, read on a frame scaled to 375 px wide; one convention of capitalisation per video; US number formats.
- **Tried and dropped:** an early short's seven invoice rows with chips (unreadable in the hand, 2026-08-21); deck-over-voice (body text about 12 px); "install it in 4 clicks" (no subject, 2026-09-16); dashboards with the whole anatomy in small type (2026-10-06); round-1 podcast shorts with card type under 44 px (2026-10-27).
- **Ruling:** *"We had to take that into account to put a few words that carry weight and impact."* The creator, 2026-08-21; *"We don't need all the small letters."* The creator, 2026-10-06.
- **Receipts:** `content/reference/lessons.md`; `content/reference/workshop-edit.md`; `content/taste/on-screen-graphics.md`; `content/taste/editing-checklist.md`; `.claude/skills/shorts-editor/SKILL.md`; `.claude/skills/cut-review/SKILL.md`.
- **Where it lives now:** all of those files.

### 35. Cards never overlap, and anchor on the right word
- **Final method:** the composer refuses any overlapping or zero-length card; word-index anchors carry an `EXPECT={idx:"word"}` assert; anchor the key visual early in the beat.
- **Tried and dropped:** `at('can',1,0)` matched the cold open's "can" instead of the outro's, so one card ran 2.2 s to 136.9 s over 17 others (a short on the co-host's channel, v4, shipped, 2026-09-14).
- **Receipts:** the co-host's v4 short, 14 Sep; `.claude/skills/shorts-editor/SKILL.md`.
- **Where it lives now:** the anchor assert in `.claude/skills/shorts-editor/SKILL.md`; the overlap refusal in the co-host's own editor notes.

### 36. Lower thirds and name cards
- **Final method:** podcast name plates on from the intro for about the first minute, off for the body, back at the goodbye; guest plate fires on the guest's name; no plates in the teaser; plates give way to captions (lower, may overlap the frame edge); a guest's credit names the guest's own firm; on shorts the credit is larger text in the last 5 to 7 s, replacing the running chip.
- **Tried and dropped:** always-on plates; a credit "<guest> · <our brand>" (*"That doesn't make any sense. It should be the name of her firm"*, 2026-10-28); the co-host's lower thirds cutting into her face (made 104 px, sub line 36 px, seated 118 px off the bottom, 2026-09-10); a credit pill mid-frame covering a card (row 145).
- **Ruling:** *"After the first minute, we want the name cards to go away and then come back at the very end."* The creator, a review call, 3 Sep.
- **Receipts:** `content/reference/podcast-edit-runbook.md`; `content/reference/podcast-edit.md`; `content/taste/shorts-formats.md`; the co-host's lower-third fix, 10 Sep; the build log, row 145.
- **Where it lives now:** those files; the co-host's lower-third sizes here.

---

## F. The yellow highlighter

### 37. Yellow highlighter on prompts the creator reads
- **Final method (built, never used on a real cut):** a highlight pass script, `highlight_pass.py <video.mp4> <scribe.json> <out_dir> [--fps 2] [--mode marker|word] [--only keys]`. It fuzzy-matches the Scribe words against 10 known prompt texts (ratio over 0.62), OCRs frames at 2 fps with tesseract `--psm 11` (conf over 45), places a box only when a neighbour word also matches (score at least 1.5, "a guess is a wrong mark"), ends a mark when the word leaves its spot for 2 frames, fills 1 to 2 word holes on the same line, draws `drawbox ... color=yellow@0.42:t=fill`, writes `overlay.mov` (ProRes 4444 with alpha) for Premiere or After Effects plus 720p previews and `report.json`. On a 12 Oct rough cut it placed 80 of 90 and 26 of 30 words; never checked on a real cut. Limits from its page: boxes lag a fast zoom by about 0.5 s; a prompt not in the 10 gets no marks.
- **Tried and dropped:** the overnight pass on the editor's export, because the export never landed; the editor highlighted by hand and the creator accepted (2026-10-15). The task closed with nothing rendered (2026-10-20).
- **How we got there:** the creator asked for it 2026-10-14; the editor proposed the highlight, the creator took it; then on 15 and 16 Oct the lesson became: the creator highlights with the mouse while recording, so the pass is not edit work.
- **Ruling:** *"highlighting words as I'm speaking them, but only the words that I'm speaking and at the exact right timing with like a yellow highlighter marker."* The creator, 2026-10-14; every prompt read is zoomed in from the box's top-left edge at 1.2x with the yellow highlight (same call). Promoted guideline: "on the record the creator highlights what they are reading with the native mouse highlight, so the zoom-and-highlight pass is not hand work in the edit" (the editor's guidelines file, 2 days, 15 and 16 Oct).
- **Open conflict, settled in practice:** the creator also said *"Put the captions of what I'm reading there as well."*, against the editor's guideline "no caption strip of the prompt text". On a later review call the creator took the highlight over the strip (README, closed list); it is current practice, not a written rule.
- **Receipts:** the script's own header and its results page; the editor's notes of 14 and 15 Oct; the task close of 20 Oct; `content/taste/kinds/masterclass.md`.
- **Where it lives now:** the method is the description above (the script is not in this pack); the rulings in the editor's guidelines file and quotes in `content/taste/kinds/masterclass.md`.

### 38. A drawbox fill comes back darker than its RGB
- **Final method:** measure a fill by rendering candidates; only `0xFFFFFF` lands within 1 level on near-white; convert PNG patches with `scale=out_color_matrix=bt709:out_range=tv,format=yuv420p`.
- **Tried and dropped:** `0xFDFDFD` for an RGB 253 card decoded to 250; an RGB still laid on BT.709 tape put a greenish box on 38 of 45 minutes.
- **Receipts:** `content/reference/workshop-edit.md` (colour).
- **Where it lives now:** `content/reference/workshop-edit.md`. Relevant to the yellow@0.42 overlay colour, which was not measured this way (untested).

---

## G. Review of captions

### 39. Caption review is its own dense pass
- **Final method:** one agent per vector: captions sampled every 1.5 s, suspect stretches 0.4 s, the karaoke at 0.04 s; every seam at -0.6/-0.2/+0.2/+0.6 s; the shorts self-check reads a frame every 2 s and at every join; a post-build word diff lists every word of 3 or more letters that never reaches the screen (guest R's episode).
- **Tried and dropped:** a 100-frame board for a 15-minute cut (could not catch the backwards karaoke).
- **Ruling:** *"You need to adversarially attack different vectors of the video itself, including the layouts, transitions, and captions."* The creator, 2026-09-16.
- **Receipts:** `content/reference/workshop-edit.md` (review); the editor's word diff, 10 Sep.
- **Where it lives now:** `content/reference/workshop-edit.md`. The word-diff check here.

### 40. Measured glyph gate in the trial editor loop
- **Final method:** a Gemini editing trial's `editor_loop.py` (guest X's footage) measures the actual libass capital height and glyph bounds before render, acceptance and completion (Arial 84 draws 54 px, 76 draws 49 px).
- **Tried and dropped:** Gemini's own acceptance of short1 v03 (chin cropped, caption bounds wrong, small glyphs), revoked after an independent review (2026-10-25).
- **Receipts:** the trial's independent review, 25 Oct.
- **Where it lives now:** here and the trial's folder.

---

## H. From the co-host's channel (added 2026-10-29)

### 41. Scribe caption-text traps on a Live
- **Final method:** a trailing dash means a false start (`f-`) or a talked-over whole word (`memory-`): drop a dashed token only when its stem is 3 letters or fewer or starts the next word; recapitalise after `.?!` because a capital rides on a dropped filler; strip a trailing quote mark that hides a sentence end from chunking; a straight leading apostrophe glues words, so curl it (`'cause`); `card_anim.py` honours one starred word, not a starred phrase.
- **Receipts:** the co-host's take notes for a Live, 23 Sep.

### 42. Never caption a misspeak
- **Final method:** listen before captioning; a misspeak ("16 hours a day" meant a week; "They're bad at the craft" said opposite to the point being made) is cut or left uncaptioned, never burned in as said.
- **Receipts:** the co-host's take notes for a long form, 7 Oct.

## I. The 27 to 29 Oct podcast and tutorial shorts build (added 2026-10-29 evening)

Read off the whole build log (rows 1 to 235, T:210 to T:231) and the round-3 verdict of each short. The pipeline is `pipeline.py` with `looks.html` and `anim_looks.html` (the overlay pages) and `tutorial_look.py` with `tutorial.html`, all in `examples/podcast-shorts-pipeline/`. "Row N" is a build log row.

### 43. Caption lines are laid out by a shortest path over a block, not cut greedily
- **Final method:** on the Instagram look `ig_lines_dp` lays the sticker lines over blocks of one speaker's groups under 1.5 s apart (1-word line costs 1000, a line under 0.3 s after the speed 500, 22 characters stretching to 26 for a merge, fewer fuller lines); the drawn looks run `drawn_chunks` over blocks of pieces (2 lines of 2 words a line preferred, a 760 px stretch, a Big group may step down to 104) then `fix_caption_groups`; a drawn group under 0.3 s may be held up to 0.10 s into the next same-speaker group (`CAP_HOLD`); 2 hook groups merge when they fit one line. On the drawn looks a lone word of 12 letters or more passes (it fills a line; the rule's target is the flashing short word); an Instagram line of 1 word always fails. Check `caption_lines_ok`. Pending: builder H (29 Oct evening) was briefed to let the long lone word pass only when no neighbour can share the line (the build log).
- **Tried and dropped:** greedy `ig_chunks` (1-word lines, 'always' 0.17 s, 'say,' 0.07 s, round 1 cause 3, row 84); merging a lone last word into a 4-word line, which reached x 1075 in the rail (row 60: merge only within 22 characters); a 0.155 s 'How do' on guest U's M1 hook that no split could fix until the hold (rows 90, 183, 202).
- **Receipts:** rows 60, 84, 143, 202, 235; `pipeline.py` `--selftest` cases ('licenses over breaches.', 'say,' at 0.07 s).

### 44. A caption is never on a face, and the check measures it
- **Final method:** `caption_face_ok`: no caption ink box (the line box less its ascender space; the IG sticker at 1556) meets a face box from brow to lower lip on any panel on screen at that time. The drawn stacked hook captions one line at 104 px centred in the seam between the host's lowest chin and the guest's brow (`hook_caption_y`, `\an5\pos`); over a card-state answer panel a Big group stays one line or is set at 104 (row 200); the drawn answer solve holds the lower lip over the block's ink (`lip_max` 1262). Tutorial A and C: the chin estimate sits 48 px over the dark caption box at 1400 (T:229).
- **Tried and dropped:** the libass block foot fixed at 1492 while the 1.5x guest face sat at 1222 to 1442 under it (guest O's M1, a caption across the guest's mouth, row 90); a caption box 5 to 12 px under the chin that veiled neck and collar (tutorial-4 C, round 3); tutorial-1 A with the caption on chin and mouth in nearly every frame (rendered before T:210, caught by the round-3 check).
- **The check's gap:** `caption_face_ok`'s face box stops at the lower lip, so a caption on a chin passes it: guest S's F3 question caption over the guest's beard and chin (round-3 verdict, fix 2) and guest Q's after-M31 box that "kisses her chin" 4.5 to 8.0 s (round-3 verdict, taste note 2). Read the chin at full resolution until the box is extended.
- **Receipts:** rows 90, 200, T:229; guest O's M1-animB round-3 verdict, taste note 2.

### 45. The Instagram caption sticker, as built
- **Final method:** Montserrat 700, 52 px (floor 50), white, at y 1556, lines of at most 4 words never across a cut, the current word on a pink box #F41CC8 (measured off a reference reel the editor picked, signature 3 of its teardown); libass writes no captions on this look; capitals checked by PIL (floor 34). Since 29 Oct each line sits in ONE dark translucent box (rgba 14,14,14 at 0.70, `box-decoration-break: clone`, alpha under the ink checks' 200) with the pink word box over it; `caption_boxes` widens the box by its padding (24 px). A line still wider than 780 px wraps to 2 lines lifted one line.
- **Tried and dropped:** white with a soft shadow only, unreadable on guest C's white-and-teal blouse (row 220, builder G; round-3 I); the drawn looks still had shadow-only white captions on 29 Oct (guest C's M2 round-3 fix 3, open). (The box-per-word stripes are the tutorial look's captions, `picture.md` 18.)
- **Open conflict, a choice for your taste file:** this look draws 52 px type with a 34 px capital floor, measured off Instagram's own caption, while the shared gate `check_caption_size.py` fails under a 47 px capital since 29 Oct (`captions.md` 7). The 2 floors disagree on the default look.
- **Receipts:** rows 56, 60, 220 (builder G).

### 46. Word fixes in captions go through `caption_fix`, and punctuation is part of the key
- **Final method:** `caption_fix` {word: replacement} on the spec for a misheard word ('eye' to 'AI'), a spelled stutter ('r-removing', 'W-when'), a stray comma; a key written with punctuation replaces the word whole ('22,' to '22', row 89); a replacement may add the full stop that closes a cut sentence ('month' to 'month.', row 162). Read the plan (`pipeline.py --plan`) to see the caption text before rendering.
- **Tried and dropped:** notes asking for the fix with no `caption_fix` on the spec (row 123); a punctuated key that was a no-op because `clean_caption_words` re-appended the word's own punctuation (row 123, fixed in 89).
- **Receipts:** rows 89, 123, 162; guest E's M2-animA round-3 verdict, fix 2 ('W-when I').

### 47. Titles: lines, case, and the first 4 seconds
- **Final method:** `breakLines` balances the lines, never leaves a word alone when 2 a line fit, breaks after a comma or before 'in', 'to', never after 'a', 'the', 'to'; `capWord` capitalises each hyphen part ('4-Letter', 'Month-To-Month'); punctuation attaches to the word before (row 14); the emoji is bound to the first word. The title says what the first 4 s say: when an opener changes, the title is rewritten to it (3 to 8 words, `scripts/copy_check.py` clean), and the creator's own titles are kept. `title_fits_ok` floor 220 since the drawn title moved to y 260 (row 199).
- **Tried and dropped:** greedy browser wrapping (a 7-word question title left its last word alone on line 2, row 87); 30 aha-opener twins and 9 tutorial twins that inherited the base's title over a different line (rows 120, 152, 165, round 1 cause 6).
- **Receipts:** rows 14, 87, 120, 152, 165, 199.

### 48. The credit: who it names, where it sits, when it shows
- **Final method:** `credit_for(S)` reads `people.guest.firm`, else the FIRMS table by slug (each filled from your contact notes), else the name alone; the brand's own name only on a short with no guest (row 173). Drawn looks: the credit takes the title's own box in the last 6 s (row 176); Instagram looks: 60 px white with a 7 px dark outline at y 1400, one line shrunk to fit (floor 40 to 44, then 2 lines at the dot). The credit's window ends where the introduction starts (`creditEnd`, row 232), so it is on the guest, never on the person introducing them; `credit_face_ok` reads that window against every face box. "Full talk in the comments" is stripped unless the spec says `long_form_live: true` (row 45: a promise on screen must be a live link).
- **Tried and dropped:** a Menlo caps chip all through (the round-2 ruling); '<guest name> · <brand>' wrapping to 2 lines at 60 px (row 75); a drawn credit at a fixed y across guest C's and guest O's mouths (row 86); the credit off from the introduction with the window still counted from the end, so guest S's F3 showed no credit at all (row 232) and guest E's M2-animA showed it 1.5 s (round-3 fix 1); a spec whose own `credit` field still read '· <brand>' while `credit_for` overrode it: 6 round-3 verdicts flag it (guest S's F3, guest Q's after-M31, guest X's F2, guest C's M2-animC, guest E's M2-animA, guest O's M1-animB), because a path that reads `credit` brings the line back. Fix the field, not only the function.
- **Receipts:** rows 45, 66, 68, 75, 86, 173, 176, 188, 232; the round-3 verdicts named.

### 49. Graphic and sticker type: the floor, the window, the fit
- **Final method:** labels 44 px minimum, one column, a window of 4 rows that pages as later keys light (3 when a label needs 2 lines); a label sits in its own span and shrinks until the span fits (floor 30), because a flex box's scrollHeight never reports the overflow (row 35); a prose item is a `card_text`, never a row (row 38); bars without a value draw as rows; `graphic_type_ok` reads the page's own smallest font (`type_min`). IG list stickers at most 780 px wide, so the 1.08 pop's peak (912) stays out of the rail.
- **Tried and dropped:** type at 22 to 40 px and 2 columns (row 27); a 'scene' chip clipped at 4 lines (row 35); a timeline pin drawn over the odd labels (row 39); on guest E's M2-animA the lit row's 2-word label wrapped and the money count-up landed on its second line (round-3 fix 0, open).
- **Receipts:** rows 27, 35, 37, 38, 39, 60, 86.

---

## J. The 3 to 6 Nov builds (added 2026-11-07)

### 50. A credit or lower third is checked against the lowest chin, never the face detector's box
- **Final method:** each person under the credit gets a panel solve that holds their lowest chin (leans included) at least 24 px above the credit's top, and the check reads the measured chin line, not the detector box. Read the last 6 s of every podcast short at full resolution, the credit's window.
- **Tried and dropped:** a credit check keyed on the face detector's box. A Haar-style box ends around the mouth, so a credit at y 1400 to 1464 ran across the guest's chin and beard for the last 6 s and still passed (the builder's own chin line read 1444 and 1429, inside the credit). A re-frame made earlier the same night had moved the faces down and created the fault.
- **How we got there:** an independent round-3 checker failed the first 2 re-renders on it; the fix went into the panel solve and the check; every podcast short rendered before the fix that night was re-rendered after it, and the next round-3 read passed all 3 with the credit 8 to 170 px clear.
- **Receipts:** round-3 verdicts, 2026-11-03 21:23 and 2026-11-04 12:41.
- **Where it lives now:** here, and the shorts builder's errors table (`.claude/skills/shorts-editor/SKILL.md`). Same gap as item 44's caption check: any box test against a face needs the chin, not the detector box.

### 51. A caption calibration from one machine does not hold on another
- **Final method:** measure 1 known word through libass on the machine that burns, before the first burn (`privacy-and-pipeline.md` C1).

---

## Still open in this file

1. **The native look's own floor.** The shared gate fails under 47 px (item 7); settle the Instagram look's 34 px capital floor (item 45) against it in your taste file.
2. **The chin gap in `caption_face_ok`.** Its face box stops at the lower lip, so a caption on a chin passes (item 44). Until the box is extended, read the chin at full resolution. The credit's check was moved onto the measured chin on 3 Nov (item 50); the caption check can follow the same way.
3. **The yellow highlighter pass** (item 37) was never run on a real cut, and its yellow@0.42 colour was never measured the way item 38 measures a fill.
4. **Masterclass card type** (item 12): a sans (A) or a display serif (B) is a choice for your taste file.
5. **Where each lesson sits.** Several of these lessons first lived only in a build log or one review file (the reading-speed rule 14, the frame-midpoint snap 15, the encoder setting 21, the ffmpeg-full fix 22, descender-aware placement 24, never regenerating captioned pixels 29, variable fonts in headless Chrome 11). When one of them becomes a rule for your channel, copy it into the taste file it belongs to.
