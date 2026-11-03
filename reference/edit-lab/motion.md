# Edit lab: animation and motion graphics lessons

> Part of the edit lab book (copied by the reader to `content/reference/edit-lab/`; the book's index is `README.md` in the same folder). It records what was tried, what failed, and how each technique got to the version that works. Each lesson: the final method, what was tried and dropped, how we got there, the ruling (a starting default you can change in your taste file), the receipts, and where the rule also lives. A new lesson learned while editing is added here in the same session it is learned.

The lessons were swept on 29 Oct 2026 from a working system's build notes, taste files, skills and the example pipeline's build log. Receipts below are generic on purpose: "the build log, row 63" points at the method notes in `examples/podcast-shorts-pipeline/README.md`; "the motion lab page" is the 10 Oct motion lab write-up whose findings are folded in here; "the creator's review, 28 Oct" is a ruling made on a review of the renders.

How "Where it lives now" reads:
- **In a taste or reference file**: the rule is written in a file a session loads or is routed to (`content/taste/`, `content/reference/`, `.claude/skills/`).
- **Partly**: the rule is in a guidance file but a load-bearing detail (the why, the numbers, the failed tries) is only in this book or in build notes.
- **Build notes only**: the lesson lived only in one project's build folder or a work log before this book. This book is now its home; copy it into a taste file when you rule on it.

Notes marked **[Fixed 29 Oct]** record a contradiction that was found while sweeping and corrected the same day.

---

## A. HyperFrames craft

### House motion: springs, overlap, one shape, handoff, camera
- **Final method**: every tween uses a closed-form spring from `examples/podcast-shorts-pipeline/springs.js` (copied into the project's `assets/`): TYPE z 0.9 w 16 (lands about 0.39 s), UI z 0.78 w 14 (about 0.28 s, about 2 % overshoot), CARD z 0.85 w 10 (about 0.49 s), FADE z 1 w 22, EXIT z 1 w 18, MASK z 1 w 19.5. The helper `spr(tl, target, from, to, spring, at)` sets the duration to the settle time. Starts overlap (a group arrives within about 0.5 s); a state change is 1 element changing size, radius and fill through a clip-path inset, content swapping behind a 14 px, 0.16 s blur; a title becomes a slide headline by travelling to identical geometry (within 2 px, measured from a snapshot); a world wrapper pushes 1 to 3 % across a hold (`content/taste/motion-craft.md`). Process: take a reference's grammar, never its content; write the state list on a beat grid before code; snapshot the opening, the signature move and the final hold at full resolution.
- **Tried and dropped**:
  - Fixed ease curves (power3.out, power2.out, back.out) and scene crossfades. The 10 Oct lab counted 0 springs across 46 compositions; a live training's intro option "fades to 0 while the deck fades in, and the camera tiles land on top of the title at 4.2 s" (the motion lab page, gap table). Why: a fixed curve looks cheap, a spring gives the move mass (one public creator tutorial's step 8).
  - `back.out(2)` in a tutorial's story animation (20 Aug), banned for story animations on 10 Oct (`content/taste/story-animations.md`).
  - Words waiting under a line mask at yPercent 108: about 24 px of every glyph showed in the first second of H1 (10 Oct). Fixed to 140 % (`motion-craft.md`; the motion lab page, "Fix 1").
  - A container growing before its content moved: H1's "into" line poked 27 px out of the card at 4.83 s (10 Oct). Fix: lines start 0.06 s before the plate grows (`motion-craft.md`).
  - Liquid-glass cards (seen in 2 public creator tutorials): skipped, "a look, not a mechanism"; in one tutorial the glass covered the presenter's face (the motion lab page, verdict item 7). Not carried into any taste file.
- **How we got there**: on 10 Oct the AI video lab read 10 public creator tutorials on motion design, remade the live training's intro option as H1, a separate verifier rebuilt it as H1r with 3 fixes, then proposals P1 to P5 were applied.
- **Ruling**: the creator, 10 Oct: apply the HyperFrames P1 to P5 and HTML A to E upgrades, with independent checks and refinements by a separate verifier. Open: whether springs reach the shorts-editor cards is still the creator's call (`motion-craft.md`, top).
- **Receipts**: `motion-craft.md`; `springs.js`; the motion lab page (sections 0, 5, 7).
- **Where it lives now**: in a taste or reference file: `content/taste/motion-craft.md`, `examples/podcast-shorts-pipeline/springs.js`, and the routing rule that a session reads the HyperFrames gotchas list and `motion-craft.md` before a HyperFrames build. The creator sources and the intro's before and after are build notes only. Liquid glass: build notes only.

### Shutter motion blur settings
- **Final method**: the registry `motion-blur` on travelling text only, `{"shutterAngle": 180, "shutterPhase": -180, "samplesPerFrame": 24}`; the target has no animated children (an entrance copy animates, an identical still copy takes over at rest and travels), the mask is `position: relative`, targets are addressed by id (`motion-craft.md`; the HyperFrames gotchas list).
- **Tried and dropped** (all 10 Oct):
  - 360 degrees, 16 samples (the lane's first setting): "stepped dark copies that read as a drop shadow".
  - 48 samples: the smear came out 19 points short on blue, with a yellow tint.
  - `sharp: 0`: black ink went olive, darkest pixels RGB 50, 51, 5.
  - Default phase (-360): the smear is a detached copy trailing the word (H1r at 4.83 s).
  - Phase -90: froze the plate's clip-path tween for about 0.4 s (held 6.00 to 6.37 s, snapped at 6.40 s) in 3 renders of 3. Hypothesis, untested: keep `shutterPhase` at most minus the `shutterAngle`.
  - The registry defaults are 720 and 16 (the vendor's motion-blur reference).
  - The lab's claim "several times the render time" was wrong: 11.6 s with blur, 11.3 s without.
- **How we got there**: the lane's build, a verifier's measurement, then an applied proof set the phase.
- **Ruling**: no ruling on the look itself; the lab said the creator judges H1 against H1c and it is adopted only if he sees it. Applied under the 10 Oct P1 to P5 go; the blur phase correction to -180 changed approved text and was flagged.
- **Receipts**: as above.
- **Where it lives now**: in a taste or reference file (`motion-craft.md`; the HyperFrames gotchas list).

### HyperFrames CLI and composition traps
- **Final method** (the HyperFrames gotchas list): every CLI call with `HYPERFRAMES_SKIP_SKILLS=1 HYPERFRAMES_TELEMETRY=0 DO_NOT_TRACK=1`; `hyperframes add <block> --no-clipboard`; 1 root composition per project (a variant gets its own project folder with an assets symlink); clip-path numbers without trailing zeros ("456px", never "456.00px"); a dim or tint layer is its own layer, never inside a video's wrapper; intentionally hidden text carries `data-layout-allow-occlusion`; `hyperframes snapshot --describe false` so a frame check does not send each frame to Gemini; sound stays on the `<video>` with `data-has-audio="true"`.
- **Tried and dropped**: the first lab render's CLI hung 10 minutes after writing a complete file without the telemetry vars (10 Oct, cause untested); `add motion-blur` overwrote the system clipboard; `init` updates global skills without SKIP_SKILLS; a dim inside the video wrapper never showed in the render (the injected frame painted over it); a brand-accent mark left a visible square edge, while the official transparent mark on a white orb was clean (the motion lab page, section 7).
- **Ruling**: applied as P4 under the creator's 10 Oct go.
- **Where it lives now**: in a taste or reference file (the HyperFrames gotchas list). The mark-edge note is build notes only.

### Build-time entrance state (immediateRender)
- **Final method**: entrances use `fromTo` with `immediateRender` true so a box is hidden before its word; exits use `immediateRender: false`. The guest U teaching-card builder: `window.spr = function(tl, t, f, to, sp, at){ return tl.fromTo(t, f, Object.assign({}, to, {duration: sp.dur, ease: sp.ease, immediateRender: to.opacity !== 0}), at); }` and every box "lands 0.1 s before its word" (`LEAD = 0.10`). The house `springs.js` hard-sets `immediateRender: false`, so a project using it as-is shows its from-state wrongly before the tween starts (untested whether this bit anywhere; the guest U builder overrode it).
- **Tried and dropped**: none recorded.
- **Ruling**: none; a builder choice.
- **Where it lives now**: build notes only (the guest U card builder). **[Fixed 29 Oct: the builder is now tracked with the project.]**

### No network inside a render (GSAP from a CDN)
- **Final method**: on 4 Sep the guest X shorts moved object animation to PIL because the first object animation loaded GSAP from a CDN and the script tag stalled page load until the build timed out twice. The lesson as filed: no CDN in a render pipeline (GSAP stalled it twice), and an object lands on its word, not on a rhythm. The cloud adapters render with a local GSAP.
- **Tried and dropped**: a CDN `<script>` in a rendered page, 4 Sep, timed out twice.
- **Contradiction found**: the shorts-editor template still loaded GSAP and MotionPathPlugin from jsdelivr (its `gen.py` and 2 reference examples), and so did the 27 Oct guest U card builder. 65 files across the video, shorts and output folders carried the jsdelivr GSAP tag (a grep count). Whether HyperFrames now inlines or caches it is untested.
- **Ruling**: none; a build lesson.
- **Where it lives now**: build notes only (the guest X shorts plan and its object script). Not yet in the HyperFrames gotchas list.

### HyperFrames wants card-shaped compositions; free-form diagrams go to PIL
- **Final method**: "HyperFrames' renderer wants card-shaped compositions; a free-form diagram silently produced black frames. Frame-exact PIL was the reliable path." (`content/taste/story-animations.md`, 24 Aug.) PIL frame by frame is also the route for podcast plate entrances (`content/reference/podcast-edit.md`) and the guest Z cover B (alpha PNG frames at 1242x956, 24 fps, "Every element moves once, 0.5 s ... Nothing bounces and nothing scales past 1").
- **Where it lives now**: in a taste or reference file (`story-animations.md`, `podcast-edit.md`).

### Text behind the subject
- **Final method**: `hyperframes remove-background` on 1080p source; layer order footage, dim, type, cutout; the dim is its own layer; pick a word or a height the speaker's head cannot cover (`motion-craft.md`).
- **Tried and dropped**: H3 on a 720p guest track (guest O, 10 Oct): the head covered the "d" and "c" for about 2 s so it read "po cast"; hair edges were soft at a 1.5x upscale (the motion lab page, verdict item 4, section 2).
- **Ruling**: the lab left H3 for the creator to judge; no recorded verdict.
- **Where it lives now**: in a taste or reference file (`motion-craft.md`); the "po cast" example is build notes only.

### Sound on the beat grid
- **Final method**: standalone stings only; hits live in 1 `beats.json` that both the picture and the synthesized sound read; story animations under the speaker's voice stay silent (`motion-craft.md`).
- **Tried**: H2 (10 Oct): 4 of 7 peaks within 10 ms of their hit (the motion lab page, item 6).
- **Ruling**: open; the creator was to rule on H2's register. No answer on record.
- **Where it lives now**: in a taste or reference file (`motion-craft.md`).

### The September HyperFrames story for a tutorial (tutorial-2)
- **What happened**: 9 Sep, 13 scenes, direction "Split Swap", a 2 m 30 s continuous bed. It was built before the creator's brief answers reached the brief, so it carried a machine line instead of his own sentence and ran as a bed when he had ticked "You full frame, animation as inserts".
- **Ruling**: the creator, 9 Sep, on all 3 variations (HTML deck, HyperFrames story, on-camera board rebuild): all 3 rejected, start from scratch. The why was never recorded.
- **Lesson to carry**: animation is inserts while the creator is full frame, built after the brief answers land, never a continuous bed.
- **Where it lives now**: build notes only (the tutorial's interview file). Not in any taste file.

---

## B. Alpha, overlays and compositing over footage

### Alpha overlay format
- **Final method**: anything that assembles on screen is a HyperFrames alpha composition handed over as a `.mov` (`content/reference/podcast-edit-runbook.md`; `content/reference/podcast-edit.md`). 3 alpha encodings are in use, read with ffprobe:
  - a podcast prompt walkthrough: `codec_name=prores ... pix_fmt=yuva444p12le ... r_frame_rate=30/1`.
  - a tutorial's animated title: `codec_name=vp9 ... pix_fmt=yuv420p ... tag:ALPHA_MODE=1`, 30 fps.
  - the guest U teaching cards: `codec_name=png pix_fmt=rgba`.
  The vendor CLI renders alpha with `npx hyperframes render --format webm` (transparent WebM) or `--format mov` (the vendor's preview-render and cloud references: "webm/mov carry alpha"; 4k cannot combine with webm or mov). Which flags produced the PNG-in-MOV guest U files is untested; the command is not in the builder.
- **Tried and dropped**:
  - 20 Aug: a transparent-PNG frame overlay abandoned: the card interiors are white in the design, so a knocked-out alpha well was the wrong architecture, and HyperFrames renders the frame as HTML with the video inside it, which needs no PNG at all.
  - 20 Aug, later: abandoned again: Chrome headless returned RGB with no alpha despite `--default-background-color=00000000`, and the CSS knock-out was wrong anyway since `.set` paints the accent behind the cards, so the wells came out accent-coloured rather than empty. A true alpha frame needs an SVG evenodd path or a CSS mask, not a border trick. Related: `--default-background-color=0` is rejected; Chrome wants hex (the design-dna traps list).
- **Contradictions found**: the shorts-editor skill said "`hyperframes render` outputs `yuv420p` (no alpha)", which the 8 Sep tutorial overlays (WebM and MOV with alpha) and the vendor docs disprove. `content/taste/clip-bar.md` carries an older SOP line, "Overlays must be ProRes 4444 `.mov @24fps`", while the prompt walkthrough overlay is 30 fps and the guest U cards are PNG-in-MOV at 24 fps. **[Fixed 29 Oct: the shorts-editor skill now names `--format mov|webm` for alpha; clip-bar's 24 fps is still open.]**
- **Ruling**: the creator, 8 Sep, handing the editor the podcast lane: the HyperFrames-based animations are made in the Claude session, not in the editing app.
- **Where it lives now**: partly. The route (alpha `.mov`) is in `podcast-edit-runbook.md` and `podcast-edit.md`. The formats, the render flag and both 20 Aug failures are build notes only.

### Frame rate of an overlay against its master
- **What the builds did**: Riverside masters are 24 fps and the guest Z cover animation was rendered at 24 fps to match its Riverside master; the guest U cards set `data-fps="24"`; Omni returns 24 fps (`content/reference/media-gen.md`); the prompt walkthrough and tutorial overlays are 30 fps.
- **Tried and dropped**: 28 Sep, a shorts set: a `-loop 1 -i mask.png` defaults to 25 fps, so an alphamerge against 30 fps video "stretched every masked window by 20% and a later window landed 5.9 s late" (the shorts-editor skill). Finite image sequences against a mismatched-fps main stream hang forever (`podcast-edit.md`; `podcast-edit-runbook.md`).
- **Gap**: no file said "render the overlay at the master's frame rate". Each build chose its own. Starting default: render every overlay at the master's frame rate.
- **Where it lives now**: the 2 traps are in the shorts-editor skill, `podcast-edit.md` and the runbook; the matching rule is this book.

### ffmpeg compositing traps that render clean and are wrong
- **Final method** (all in taste or reference files):
  - Any graph with a `-loop 1` still carries an explicit output `-t` (plus `shortest=1` on the first overlay); the tell is "More than 100000 frames duplicated" (`podcast-edit.md`; the shorts-editor skill). Found 28 Aug, after it cost 3 renders.
  - A seeked input carries the tape's timestamps: every `[1:v]` chain starts with `setpts=PTS-STARTPTS` (`content/reference/workshop-edit.md`, "Two faults that render clean").
  - Cropped overlay images go at the original frame bbox position, not their own 0,0 (`podcast-edit.md`).
  - An RGB still on a BT.709 tape is converted with BT.601 unless told otherwise: a greenish box on 38 of 45 minutes (`workshop-edit.md`).
  - A card under a b-roll window flashes 1 to 2 frames when the b-roll detaches: cover it with a black band to the start of the next beat (the shorts-editor skill).
  - Bake plates into segment renders with `-loop 1` images only; composite entrance animations frame by frame in PIL; keep the final pass to subtitles and loudnorm (`podcast-edit.md`).

### A still holds still
- **Final method**: never a slow push-in on a card or a photo; test a still section with `tblend=all_mode=difference,signalstats` above the caption band, where YMAX should sit at 0 to 2 (`workshop-edit.md`).
- **Tried and dropped**: `zoompan` on a guest's still (guest O, Sep): "median 11 levels of per-frame change in the picture area with spikes to 223" (`workshop-edit.md`).
- **Ruling**: the creator, 11 Sep: a slow push read as a weird static or flicker; the screen with the guest's picture stays static. Starting default: stills hold still.
- **Where it lives now**: in a taste or reference file (`workshop-edit.md`).

---

## C. Story animations (generated video)

### A visual aid of the sentence, never b-roll
- **Final method**: quote the tape line and write the sound-off sentence at the top of the prompt file before anything renders; countable, proportional, resolved; where an exact quantity carries the meaning, build it deterministically (HyperFrames or PIL) and let generated video carry only the world (`content/taste/story-animations.md`; `.claude/skills/media-gen/SKILL.md`).
- **Tried and dropped** (`story-animations.md`):
  1. Mood (glass rods, a paper stack, a leaking building), 21 Aug: "Atmosphere with no meaning."
  2. Mechanism metaphor (accent-coloured cubes into a tray, a gold bar sliced at gates): "a cube is a poetic stand-in".
  3. Cinematic Omni worlds, rejected 24 Aug: animations should help a human learn better, not b-roll that just keeps a human watching.
  4. The arithmetic made physical, 24 Aug: a step in the right direction, but still coarse and confusing to the eyes.
  - Omni handed a correct teaching diagram as an edit reference (24 Aug) "kept the look and rebuilt the structure": proportion gone, the count no longer countable.
  - Banning all text from prompts on 24 Aug "is what emptied the animations out".
  - Smoke and ash (tutorial-1, scene 1 v1, 21 Aug): read as the mechanism for about 2 seconds, then collapsed into an ash cloud and became texture. Fix: "a hard-edged container with a visible fill level" against "a visibly full source", with smoke, dust, haze, fog and debris in the negative.
- **Ruling**: the creator, 21 Aug (never "b-roll") and 24 Aug: the tests are meant to be animations that are the visual aid of what is being said on screen, and b-roll is not that. Kept as guidelines the same day. Starting default: a story animation is a visual aid of the sentence.
- **Where it lives now**: in a taste or reference file (`story-animations.md`, media-gen skill rule 3). The smoke lesson was build notes only (a superseded tutorial file); this book is its home now.

### Which lane, which prompt shape (Omni, Seedance, Veo)
- **Final method**: route first (exact numbers, UI and screens to HyperFrames or HTML; a world to generated video), Omni the default lane, prompt order (tape line header, 1 action and 1 camera intention, "In a single unbroken scene, no scene cuts", the end state early in words, the character card word for word, 1 plate pasted unchanged, colour words not hex, plain quality adjectives, exclusions last), judge by a 6-tile strip plus the first and last frame (`.claude/skills/media-gen/SKILL.md`; `.claude/skills/media-gen/reference/prompt-recipes.md`). Command shape: `python3 -u .claude/skills/media-gen/scripts/media_gen.py video --model omni --duration 6 --aspect 16:9 --yes --ref <img> --out <folder> --slug <label> --prompt "<prompt>"`.
- **Tried and dropped**:
  - Hex codes in an Omni prompt (14 Oct): a palette strip with garbled labels ("Lat awy Coffic", "Cooblext").
  - "premium explainer-animation finish" (14 Oct) rendered as a "Premium EXPLAINER" caption.
  - 2 images as the first and last frame on Omni (E4, 14 Oct): reframed the opening, ended on about 10 bars (media-gen skill).
  - A pinned `--start` holds the first frame but not the end: D4c lost its bars.
  - Counts drift: of 6 clips asked for 6 bars, the 3 counted ended on 7 or more.
  - Seedance 8 s at 720p outran the 900 s poll and the task id was lost (21 Aug); use veo-fast or short jobs.
  - Veo returns 8 s whatever is asked through the API reseller (21 Aug) (`content/reference/media-gen.md`).
  - Seedance on UI text (tutorial-5, 25 Aug) rewrote the message into "we're excited to minute help you"; Omni kept the text exact but tripled the chips (`story-animations.md`). The creator, 25 Aug: Omni did a much better job, and a few more runs would likely get it right.
  - The API reseller account at a negative balance, silently: every Seedance submit returned 403 `insufficient_user_quota` on 14 Oct and again on 27 to 28 Oct, so Seedance and Veo video-in stay untested.
- **How we got there**: on 14 Oct a 24-clip matrix over 5 tape lines and 5 sets plus a 30-source research report, rebuilt into the skill on 21 Oct (`content/reference/media-gen.md`).
- **Ruling**: the creator, 14 Oct: the media-gen skill had been lackluster; think it through from scratch.
- **Where it lives now**: in a taste or reference file (the media-gen skill, `prompt-recipes.md`, `content/reference/media-gen.md`, `story-animations.md`). The Omni-versus-Seedance prompt family disagreement is named as untested in the skill.

### Omni edit lane: the HyperFrames band as video reference
- **Final method**: pass the HyperFrames render of the same window as a `gs://` video reference; Omni inherits the beat structure so turns land on the words. Build the reference at the aspect you want back and at an exact integer of seconds; upload each revision under a new object name (`story-animations.md`).
- **Tried and dropped** (24 Aug): `aspect_ratio` on an edit returns 400; a 9.292 s reference against a 9 s ask fails; overwriting a `gs://` object cost 2 failed renders that looked like a duration bug and were not.
- **Ruling**: a session finding, 24 Aug.
- **Where it lives now**: in a taste or reference file (`story-animations.md`).

### The flat 2D mascot look (picked 15 Oct)
- **Final method**: the C-set character card and the flat 2D plate pasted word for word (`prompt-recipes.md`), with a reference image of the mascot illustration (optional, your own); Omni, 5 to 6 s, `image_to_video` with 1 `--ref`.
- **Tried and dropped**: A photoreal office (the mascot came back rounded or voxel, eyes half closed), B isometric diorama, D image-first stills, E research rules. The session had recommended A and E (`story-animations.md`).
- **Known flaws in the picked look**: every C clip took the card's black eyes over the drawing's eye holes, and C4 grew antennae; a card written from the reference is untested (`prompt-recipes.md`).
- **Ruling**: the creator, 15 Oct, picked C1, C2, C3 and "C4 or D4c", no reason given. The follow-up question went unanswered and the tutorial shipped on 18 Oct without these clips. Later, 26 Oct: looks assigned by moment (an account-book look where a true number is said, Whiteboard for lists, Flat 2D mascot for mechanisms, Operator for screens and tutorials). Starting default: assign the look by the moment.
- **Open**: a word heard on a call was assumed to mean the mascot; the editor was asked to confirm. A 2-mascots-then-a-human scene for the masterclass (tutorial-4) was specified, not built. In the shorts pipeline, "the mascot sprite sits on the 4th chip" was left open (the build log).
- **Where it lives now**: in a taste or reference file (`story-animations.md`, `prompt-recipes.md`, the media-gen skill). The 26 Oct look-by-moment assignment was build notes only; it is here now.

### Omni as a camera move or second angle
- **Final method**: the real-pixel punch-in is the default cutaway; keyframe any movement (push-in, punch-in, handheld) in ffmpeg or HyperFrames, "$0, audio bit-identical"; never regenerate pixels that carry captions (`content/reference/media-gen.md`).
- **Tried and dropped**: 11 Omni angle runs on a tutorial's camera track (28 Oct), 1 survivor at 15 to 20 degrees for about 3.3 s; sync 0.30 without real audio against 0.93 with it; a reference image of the real frame dropped sync to 0.30 and 0.64; hands always dropped or invented; the room always redrawn. Omni as the movement pass, 27 Oct: $1.64 per 8 s, and it over-zoomed and broke captions, or did nothing.
- **Ruling**: pending the creator's ruling on the movement page.
- **Where it lives now**: the angle findings are in `content/reference/media-gen.md`. The movement-style recommendation (3 variants, measured 1.11x to 1.44x push-in, punch-in 2x to 3x eased over 0.5 to 0.9 s) was build notes only; it is here now.

---

## D. Footage plus animation

### Background shift with a swoosh into an animation
- **Final method**: a background-shift script (not shipped in this pack; this is the shape of the one in the source system): `python3 scripts/footage_bg_shift.py apply --video V.mp4 --window A,B --anim ANIM.mp4 --in T1 --out T2 --output OUT.mp4 --sfx WHOOSH.wav [--swoosh 0.45] [--slide -230] [--slide-dur 0.5] [--sfx-under 10] [--no-sfx] [--report R.json]`. The person matte comes from macOS Vision (`VNGeneratePersonSegmentationRequest`, a small helper compiled by `swiftc` into a cache folder) with a 3-frame median; a quintic in-out wipe right to left with a light accent streak; the speaker slides by whole pixels; interior pixels are copied, never blended (the self-test asserts 0 differ); the whoosh is a recorded file passed with `--sfx` since 29 Oct (it was synthesised from filtered noise before the creator's real-sound ruling); the animation is any opaque mp4 at frame size, a HyperFrames render on the house springs being the worked example. Then check the report's interior count is 0 and look at the sweep frames at full size before cut-review.
- **Tried and dropped** (10 Oct): the first version left the stage list on screen while the speaker slid back across it; the list now leaves first. HyperFrames' own remove-background was compared (it disagrees on 1.5 % of the speaker's area, 529 ms for 1 frame) and Vision was kept because it needs no model file and ran about 10 frames a second. The first text said "10 dB under his speech" without saying which level, so `--sfx-under` became a dial measured against the loudest 30 %.
- **Untested**: never used in a shipped cut. A Tella route (`transitionStyle: spring`, a whoosh from Tella's catalog, presenter cut out over a HyperFrames render) is untested. It needs `swiftc` (the Xcode command line tools) on the editor's machine; untested there.
- **Possible conflict**: the co-host's editing rule "Transition sounds ... nothing synthetic ... a real sound she picked, never a synthesised 'page flip' or pop" sits under "Rules for every edit" in `content/taste/editing-rules.md`, while this tool synthesised its whoosh by default. **[Fixed 29 Oct: the creator ruled real recordings only, for everyone; the tool now needs `--sfx`.]**
- **Ruling**: the creator, 10 Oct: only in some situations, as an effect that shifts the background with a transition to help explain something better with an animation and a swoosh on the visual transition, keeping his face intact; never to clean the background of a normal video. Starting default: background change only as an explanatory effect, the face untouched.
- **Where it lives now**: the rule and route are in the content rules, the cut-review skill and the media-gen skill. The before and after, the refinements and the Vision-versus-HyperFrames comparison were build notes only; they are here now.

### Prompt walkthrough over the podcast (guest X, 3 Sep)
- **Final method**: a HyperFrames alpha composition (a 22.3 s ProRes alpha, 5 lines assembling in sync with the tape, a camera hole cut out of the page fill, a footer "Paste this into ChatGPT or Claude · full prompt in the description"), staged as `build/assets/prompt-anim.mov`; the render step uses it when present (`podcast-edit.md`).
- **Tried and dropped**: built first from the guest's own prompt; rebuilt the same day to the host's own check-our-work prompt, 24.2 s, 2 steps typing to his words.
- **Ruling**: the host, 3 Sep: the episode needed a HyperFrames animation walking through the full prompt a viewer should paste, and the first prompt pulled up was the wrong one. Starting default: the walkthrough shows the prompt the speaker is actually describing, typed to his words.
- **Where it lives now**: in a taste or reference file (`podcast-edit.md`, `podcast-edit-runbook.md`). The camera-hole technique detail is here.

---

## E. Cards, plates, title cards, count-ups

### Shorts cards (shorts-editor, top band)
- **Final method**: cards contiguous and anchored to real word times from the re-transcribed cut, the key visual early in the beat, few words at phone size (headline 96 px, number 180 px, label 44 px, 6 words max), no per-word pulsing, no text-in-a-box cards, `EXPECT={idx:"word"}` asserts, card classes namespaced `c-{t}`, `white-space:pre-line` on display type, logos verified on black (`.claude/skills/shorts-editor/SKILL.md`). Snippets in `references/card-snippets.md`, the catalogue in `references/animation-library.md`.
- **Tried and dropped**: E1's 7 invoice rows with chips, 21 Aug, unreadable on a phone; deck-over-voice in the top band (`content/taste/lessons.md`); TextPlugin for the typewriter eats `<role>` tags (the shorts-editor skill).
- **Ruling**: the creator, 21 Aug: a few words that carry weight and impact, and the animation preferred over the deck under the voice. Starting default: a few weighty words, animation over a deck.
- **Where it lives now**: in a taste or reference file. Note an internal conflict: the shorts-editor style reference says entrances use "ease back.out/power3.out", while the skill says "no bounces, spins, or glows on content elements" and `motion-craft.md` keeps back.out on shorts cards on purpose until the creator says otherwise.

### Stat count-ups
- **Final method (shorts-editor)**: a count-up on a proxy `{v}` with `onUpdate` writing `textContent`, only when the beat lasts over 1.2 s; below that, pop the final number (`opacity:0, scale:1.45 -> 1`, back.out); force the pop on beat 0 and on beats under about 2.2 s because a count-up under the title card resolves hidden ("28" instead of "30") (the shorts-editor skill; `references/animation-library.md`, "Count-up vs POP"). A bare big number is "sterile": make it a curve that draws itself, with the number popping at the peak.
- **Tried and dropped**: 0 to 91,000 in 0.9 s, unreadable; 21 Aug, 3 count-ups switched to a pop after they were caught resolving under the title card.
- **Newer read, not yet reconciled**: the 27 Oct teardown of 2 public AI-tutorial creators' shorts: count-ups decelerate and stop on the said number, about 0.6 to 0.7 s, fast at the start, crawling at the end, then a state change (teardown signature 6). The podcast-shorts animation layer counts "a number of 10 or more ... 0 to the value over 0.6 s in 160 px DM Serif, then an underline draws" (`examples/podcast-shorts-pipeline/README.md`, the animation looks notes). The teardown also says settle with no overshoot, which the shorts-editor back.out pop does not do.
- **Ruling**: none on the count style itself.
- **Where it lives now**: the shorts-editor rules are in the skill. The teardown timing and the 0.6 s count are in the example pipeline's notes and here.

### Podcast teaching cards (guest U, 27 Oct) and guest-named resource cards (guest Q, 21 Oct)
- **Final method**: 2 tiers, a small card for a note, a full animated teaching card for a prompt, a strategy, a tactic or an acronym; boxes build in step with the words; a guest's named book, podcast or website is shown as the real thing, animated (`story-animations.md`). The guest U cards F1 to F5 were built as 1 HyperFrames project each, on springs, every box landing 0.1 s before its word, the full last state holding to the window end and the last 4 frames softening behind a 14 px blur so the next card swaps content on the same board; rendered as alpha `.mov` into `raw/edit/cards/` and overlaid by the finalize step under the captions at tape times. The guest Q cards overlay the finished episode in 1 ffmpeg pass after finalize, mapping tape time to final time through the cut plan and the 1.1x speed, splitting a card at every layout change and placing it off faces and the caption band, audio stream-copied.
- **Tried and dropped**: "a blank whiteboard with black words" (guest U's F2, 27 Oct). Cut-review on 27 Oct fixed F5 not holding its last state and F1's eyebrow and headline arriving late.
- **Ruling**: the creator, 27 Oct: more going on than a blank whiteboard with black words, in the style of the 2 public AI-tutorial creators; use boxes and animation without being overwhelming; the animation serves the message. Guest Q, 21 Oct: overlay the cards the host picks over the finished episode at their timestamps, as the final step. Starting default: teaching cards are boxes that build with the words, overlaid last.
- **Where it lives now**: the rule is in `story-animations.md` and `podcast-edit.md`. The builders were untracked build files at first. **[Fixed 29 Oct: tracked with their projects.]**

### Masterclass on-screen style (tutorial-4, 14 to 15 Oct)
- **Final method**: every text sits on a card, never floating; a brand-accent ground, white words, a small shadow, no stroke, loose padding, Title Case; the featured product's orange on numbers, the product's name and "20x"; the stage timeline comes down from above with the current stage about 250 % bigger, then goes back up, replacing stage cards; a zoom and a yellow word highlight at 1.2x when the creator reads a prompt; an errata card in the same orange; a key-lesson card when he says "key lesson" (the 2 action lists of 14 and 15 Oct). An overnight machine pass built 36 transparent card PNGs and a word-level highlighter (Scribe words, tesseract boxes, a ProRes 4444 alpha overlay) placing 80 of 90 and 26 of 30 words.
- **Tried and dropped**: the highlighter overlay was not used: the editor highlighted by hand and the creator accepted it; next time the creator highlights with his own mouse on the recording. The fake smooth cursor: kept in mind for next time (action list 1).
- **Contradiction**: the featured product's orange is #D97757 in `content/taste/thumbnails.md`, while the shorts-editor style reference said "#f0813f". The creator: always the same orange. The eyedropper shade he picked on 15 Oct was never confirmed against #D97757. **[Fixed 29 Oct: the style reference now says #D97757.]**
- **Ruling**: the creator on 2 review calls (14 and 15 Oct); "250 is good, way more readable" (action list 2); promoted into the editor's guidelines. Starting default: text on cards, 1 accent ground, 1 second colour on numbers.
- **Where it lives now**: partly. Tape quotes are in `content/taste/kinds/masterclass.md` (cut-review reads the kinds sheets); the promoted rules were in the editor's own guidelines file. No taste file states the card style as a rule.

### Title cards and intros
- **Final method**:
  - Shorts: frame 0 is the packaged promise, a title card on its own high track, `tl.set(opacity:1)` at 0, held about 0.95 s then faded (the shorts-editor skill; found 21 Aug). On the Omni composite lane a promise overlay on the first beat replaces the black title card.
  - Podcasts: the trailer, then the title card with the host's welcome heard under it, the bed at 0.10 fading over the 7 s before the intro animation ends; plates on from the intro through about the first minute, off, back at the goodbye (`podcast-edit.md`; `podcast-edit-runbook.md`). A teaser bed is at least the teaser plus the title card; the 20 Oct guest G check found the title card was digital silence (`podcast-edit.md`).
  - Live and workshop cuts: "The opener works because of the RESOLVE, not the animation": render the opener into the slot the real footage lands in and dissolve onto a real frame of what follows (`workshop-edit.md`); faces stay on the opening.
- **Tried and dropped**: the black title card format in shorts, dropped 27 Oct as too jarring (guest R's F3) (`content/taste/shorts-formats.md`); a live training's animated title resolving into a bare slide (11 Sep, "Our faces stay on the opening"); the crossfade of a title into the deck (24 Sep), replaced in the lab by H1's handoff (see section A).
- **Ruling**: the creator, 27 Oct: the black title card dropped everywhere; the host, 3 Sep, the exact podcast opening (`podcast-edit.md`); the creator, 11 Sep, on faces (`workshop-edit.md`).
- **Where it lives now**: in a taste or reference file.

---

## F. Shorts motion (the 27 to 29 Oct rounds)

The 4 entries after the first were added on 29 Oct from the whole build log of the shorts pipeline ("row N", now in `examples/podcast-shorts-pipeline/README.md`) and the round-3 verdict files. The overlay pages are `examples/podcast-shorts-pipeline/looks.html` (the drawn looks and the Instagram look) and `examples/podcast-shorts-pipeline/anim_looks.html` (the 3 animation directions), picked by an environment variable, its hash in the render cache key.

### HyperFrames only with a purpose, 2 in 10; animated shorts layout
- **Final method**: about 2 shorts of 10 use HyperFrames, the rest Instagram-native; a card is on screen only while it animates with purpose; animated shorts open on the Instagram hook and headline, the title goes when the animation plays and the animation takes the full top; light mode preferred, with light and dark rendered side by side; the brand-accent glow on our animations; the drawn timeline (flat 2D) and the tutorial screen-hero layout A are the standard (`content/taste/shorts-formats.md`; `content/taste/shorts-profiles.md`).
- **Tried and dropped**: the set "over-indexed on HyperFrames"; the black title card; "half of the friggin screen is black" (on guest E's short); reviewer batch C2 found motion graphics never built and finder prose burned on screen in 11 of 11 motion tutorial shorts.
- **How we got there**: a teardown of 2 public AI-tutorial creators (16 shorts, 5 long-form openings, 17 signatures); 3 animation directions built: direction A (status cards: lift 6 px, scale 1.035, a bloom 0 to 40 px over 0.6 s, a ring ping 0 to 3x over 0.5 s, a 2.2 % push on holds), direction B (1 object changes state, no glow), direction C (our blend) (the animation looks notes in the example pipeline's README).
- **Ruling**: the creator, 27 Oct: about 2 of 10 use HyperFrames, and only with a purpose; the research is about the source of the motion (fluid, purposeful), never reduced to a glow effect (`shorts-formats.md`). The creator and the editor, 28 Oct, round 3 (`shorts-formats.md`). Starting default: 2 in 10, with a purpose.
- **Where it lives now**: the rulings are in the taste files. The 17 signatures (the move is the sentence on the word, 1 object lives and changes, many become 1, state change as emphasis, settle 0.2 to 0.3 s with no overshoot, ghosted upcoming items, slow motion in every hold, a ring or box pointer, a highlighter sweep, fake UI, hubs that grow a node per named thing) and the A, B and C parameters are in the example pipeline's notes and here. `shorts-formats.md` names the research but not its contents.

### The Instagram-native look, as built (`ig_native`)
- **Final method**: no band and no fade; the title as Classic stickers (Montserrat 700, 56 px, black on white rounded boxes, title case, the spec's `ig.emoji` bound to the first word) at y 238; the red Strong callout (#F81820, 60 px) from `ig.callout` [text, clock or null], where null shows it from frame 0 on the guest panel's top edge until the list starts; list items as white stickers popping 1.08 to 1.0 over 4 frames on their key and staying, 4 at most, 780 px wide at most so the pop's peak stays out of the rail; once the title has left (28 s) the list stacks from y 238 above the head and the callout takes the title's slot; the list hides under the credit only while the title is still up. A cut between speakers is a jump cut, the reel's own recipe. Checks for the look: `check_safe_area.py --top 220 --bottom 1640 --right 930 --right-from 1050` (`--top 120` on `ig_between`, `pipeline.py` `sa_args`), the title inside y 220 to 560, frame 0 compared on the sticker pixels only (frame 0 still carries the title stickers: only the black title card was dropped).
- **Tried and dropped**: a callout keyed after the first list key, so it never showed (guest Q's F1, row 63); list stickers at x 958 to 966 in the rail during the pop (row 60); a list that hid under the credit and showed 1 of 3 rows (guest C's M1, row 222); a red sticker on guest C's mouth and chin at 52 to 57.7 s (guest C's F1 round 3, fix 0, open).
- **Receipts**: the build log, rows 56, 59 to 63, 175, 222; the Instagram-native teardown (9 signatures, measured on 1 of the editor's tutorial reels).

### Card windows: a card only around its key, crossfaded, never in the credit's tail
- **Final method** (`card_windows_split`): a window runs from 1.2 s before a key to 2.5 s after it, windows closer than 2 s merge, the piece splits at a word gap of 0.12 s or more within 0.6 s of the window edge, else at the word boundary nearest the edge, never inside a word; on the drawn looks the last 3 s finish on the card, and a full-face stretch under 2 s between 2 card parts stays on the card. An aha piece is full face and takes no key unless the spec sets `aha_keys`. The 2 framings cross in 0.3 s (a 9-frame blended xfade piece, 4 frames before, 5 after), the band and the card moving over the same 0.3 s; sound and captions read the contiguous runs, so nothing is heard or captioned differently. On the Instagram looks no window runs in the credit's last 6 s. Check `card_still_ok` (no window holds more than 3.4 s past its last key).
- **Tried and dropped**: a window per piece, which kept guest C's M2 card up 37 s and spent the timeline in the aha preview (row 85, round 1 cause 4); a hard cut between the 2 geometries (a same-day proof render); a card held 36 to 42.6 s because the guest never paused 0.12 s (row 91). The cost of the credit rule: guest C's M2-animC never draws its last 2 beats (round 3, fix 0, a quality note). Open (row 232): the last-6-s rule still counts from the end of the short while the credit ends where an introduction starts, so on a short with an introduction it can sit a few seconds early (untested).
- **Ruling**: the creator on guest X's F2, 27 Oct: if there is a scene transition, do a proper visual transition, not a jarring jump; on guest X's M1: the HyperFrames card should be there when it is animating something with a purpose. Starting default: a card only around its key, crossfaded in and out.
- **Receipts**: the build log, rows 85, 91, 193, and the 2 log lines that state the window rule.

### `ig_between`: the animated short between Instagram looks
- **Final method**: the hook is the Instagram stacked hook under the title stickers; outside a card window the answer is the full-bleed face with the blurred extension; inside a window the face sits in the lower 1040 (`IGB_ANSWER`, `face_px` 340, mouth to 1440, chin to 1520) and the animation takes y 140 to 844 with the title gone (the title sticker fades with the window's envelope, `window.__igbEnv`); the Instagram caption sticker throughout; light and dark twins of every animated short; the brand-accent glow on every direction (alpha 0.20 light, 0.26 dark). Checks: the footage safe area and the layer test both use the 120 line (`--top 120`), and in the top 120 only pixels away from the band's own colour (sampled on row 0) count.
- **Tried and dropped**: the drawn band from frame 0 ("half of the friggin screen is black", on guest E's short, styles E); direction A's rounded panel corners and direction C's rule drawn at y 0 when the ground is 0 high, 798 and 6,480 ink px in the top 120 (rows 186, 192: now shown only while the ground is 300 px or more); the dark twin's opaque near-black band counted as ink (row 206), and a 2 px band mid-transition sampled at y 4 (row 219); the glow wrap starting at y 0 and blooming into the band (row 217); the light twin rendering dark because the direction A palette and every `ANIM === "A"` colour switch ignored `anim_light` (row 208: `PAL.AL`); the page reading 0 to `hook_end` as the hook after the order rule moved the stacked hook behind the aha, which clipped guest X's animation and left the band black 4.5 to 10.75 s (row 223, `AN.hookStart`; the drawn path in `looks.html` the same, row 227); a title-goes variant, retired because on this look the title always goes (polish reading 6, 28 Oct).
- **Ruling**: styles E, F and G, 28 Oct (`shorts-formats.md`, the round-3 animated-shorts and light-mode lines).
- **Receipts**: the build log, rows 177, 186, 192, 206, 208, 209, 217, 219, 223, 227; the round-3 verdicts for guest C's M2-animC (pass) and guest E's M2-animA (taste 0 to 2).

### The 3 animation directions as built, and the traps their ink checks set
- **Final method** (the animation looks notes; `anim_selftest.py`, 106 checks): direction A (status cards; a landing lifts 6 px, scales 1.035, blooms 0 to 40 px decaying over 0.6 s, pings a ring 0 to 3x over 0.5 s; pending cards at 35 % with an 8 px blur; a 2.2 % push on holds); direction B (1 object changes state; when 2 or more items name red, yellow or green, or `anim_doc` is set, the document itself, each paragraph tinted in its said colour, the red one stamped DO NOT SIGN); direction C, our blend (1 white panel, direction A's landing on the active row). Every direction shows a said colour in that colour; a number of 10 or more counts 0 to the value over 0.6 s in 160 px DM Serif, then an underline draws. Picked by moment with the reason on each spec's `anim_why` (guest X's after-wave1-02 B, guest C's M2 C, guest O's M1 B, guest E's M2 A, guest J's M1 A, guest P's M1 B, guest U's M1 C). Ambient motion steps at 15 fps; frames outside the windows are hardlinked.
- **Ink-check traps**: when the page was built (27 Oct) the drawn ink check counted anything within 60 of #1C1C1E above y 290, so the dark ground is near-black #030405 above 300 and #15171A only under the card; since row 86 the drawn check's top line is 230 (the safe frame's), and 290 survives only in the frame-0 band-edge test (`pipeline.py`, around the `edge = ` line). On the operator look every direction is dark, because that look's ink reads as light.
- **Open on the round-3 renders**: guest E's M2-animA lit row wraps and its dollar count-up lands on the row's second line; guest O's M1-animB accent rule slides through a row label and reads as a strikethrough at 8.8 to 9.2 s; guest X's animB document header clips at the frame top at 10 s (the round-3 verdict files).
- **Receipts**: the build log, rows 72, 211; the animation looks notes; the "our version" research note (the 17 signatures mapped onto `graphic_v2`, with the beat verbs `land`, `count`, `flip`, `focus`, `ring`, `sweep`, `type card`); the picks list, item 2.

---

## G. Transitions

### Every section change gets a transition
- **Final method**: a few seconds or 1 card telling the viewer what comes next, the insight and why to keep watching; cut-review fails a jump with no bridge (`content/taste/editing-rules.md`). A condensed cut gets transition cards, 6 words or fewer, title case (`workshop-edit.md`).
- **Ruling**: the creator, 13 Oct: transitions are a skill to get good at; those extra few seconds for each transition are pivotal (`editing-rules.md`). On the masterclass it was the first thing to elevate. Starting default: every section change gets a bridge.
- **Where it lives now**: in a taste or reference file.

### The pause transition into an insert
- **Final method**: an insert is announced: a pause button with the screen going grey and the clip coming up from below, or a zoom out with the creator coming in from above; and the pause is shown again on the way back.
- **Tried and dropped**: the hectic cut tried before (15 Oct, action list 2).
- **Ruling**: the creator, 15 Oct: he liked the pause button where the screen goes grey and the other screen shows up, and the zoom out with him coming in from above (`content/taste/kinds/masterclass.md`); 16 Oct: the pause was shown going in but not shown again coming back. Starting default: announce an insert and close it the same way.
- **Where it lives now**: partly (quotes in `kinds/masterclass.md`; a promoted rule in the editor's guidelines; no taste rule file).

### Transition sounds
- **Final method**: on the cut, measured on the picture, centred in the speaker's pause, skipped under 0.3 s; never on plan or section times (they drifted up to 1.6 s); a real picked sound, never synthesised (`editing-rules.md`). A worked example is a rebuild script on the co-host's long form.
- **Tried and dropped**: the pop that the base render mixed on each chapter's first piece landed up to 3 s into the speaker's speech (22 Oct).
- **Ruling**: the co-host, 22 Oct (`editing-rules.md`). Starting default: real sounds, on the cut, in the pause.
- **Where it lives now**: in a taste or reference file. See the swoosh conflict in section D.

### Podcast transitions between shot types
- **Status**: open since 3 Sep. The host: next time, work on transitions; they need to be cleaner and a good experience for the viewer, not as jarring (`podcast-edit.md`); scoped 8 Sep as a joint working session with the editor, 3 to 4 treatments per cut pair on real footage, "No transition vocabulary is written into a rule before he has watched one" (`podcast-edit.md`; `podcast-edit-runbook.md`). Shorts got "a real visual transition on every scene change" on 27 Oct (`shorts-formats.md`; `shorts-profiles.md`). Guest Z options Y2 (a page slides in over 0.6 s while 3 cards shrink to the margin, no sound) and Y3 (a 0.4 s accent wipe and a short whoosh on "show") were rendered and never answered.
- **Where it lives now**: in a taste or reference file as an open item. No transition vocabulary exists yet anywhere.

### LinkedIn Live layout animation
- **Final method**: LinkedIn's Live layout animates for about 1.3 s at every switch and carries browser bars in motion: freeze each switch on the last clean frame (`workshop-edit.md`); a piece ending inside the stream graphics fade freezes its picture (`workshop-edit.md`).
- **Where it lives now**: in a taste or reference file.

---

## H. Progress bars, end screens, the on-camera board

### Section progress (loading) bar
- **Final method so far**: must-do 23, 1 segment per chapter, built from the description's chapter list (`content/taste/must-dos.md`). On the masterclass the yellow loading bar shipped; the creator asked not to change it or thicken it yet.
- **Tried and dropped**: 6 directions on real frames (30 Sep); the editor's thin yellow bar refused on 9 Oct as not sophisticated enough; a 35-style board modelled on a large business-education channel's progress bars; the brand accent was tried and rejected on the shared screen (the 14 Oct action list, the loading bar row).
- **Ruling**: the creator, 30 Sep: loading bars for each section of the video, sophisticated and helpful for retention, but not intrusive (`must-dos.md`). 14 Oct: too discreet on his phone ("yellow on yellow"), but keep it (action list 1; `kinds/masterclass.md`).
- **Contradiction**: `must-dos.md` still said no cut ships one until a pick, while the masterclass shipped one on 18 Oct. **[Fixed 29 Oct: must-do 23 now says the yellow bar is the pick, on every video and podcast.]**
- **Where it lives now**: partly (must-do 23; the yellow-bar ruling is in `kinds/masterclass.md` quotes and the editor's guidelines).

### End screens and end cards
- **Final method**: the YouTube end screen carries the subscribe ask and the next video (`must-dos.md`); every long form's end screen points at 1 chosen flagship video plus subscribe (the creator, 27 Oct), set on 31 of 31 long forms by 28 Oct. Shorts: pull to the full video with an attractive end card, never a 3 s marketing card, the credit as larger bottom text in the last 5 to 7 s (`shorts-profiles.md`; `shorts-formats.md`). A podcast end card "dark and silent" was accepted in verify (`podcast-edit-runbook.md`); the guest U episode shipped with no end card.
- **Where it lives now**: in a taste or reference file, except the flagship end-screen ruling, which landed in `.claude/skills/search-visibility/reference/youtube-seo.md` section 4, not in an editing file.

### The on-camera board
- **Final method**: a canvas is a place, not a list; zoom spent as emphasis at seams; never rotate, move on a beat, 2 zoom levels, land square on a frame; headlines and numbers only; frames stacked vertically with heavy arrows. Route: the on-camera-board skill.
- **Tried and dropped**: the 9 Sep board rebuild for tutorial-2, rejected with the other 2 variations (section A).
- **Where it lives now**: in a taste or reference file.

---

## I. Render speed and reliability for motion work

- **Measured**: a blank HyperFrames composition, 300 frames to MP4 in 6.7 s on the editor's machine (5 Sep, v0.8.29); H1r renders in 10.4 s, H1 11.6 s warm, H1c 11.3 s (blur free); a remove-background cut of 175 frames in 77 s (the motion lab page, T8); Omni 40 to 60 s per clip; veo-fast about 50 s, Seedance 8 s at 720p past 900 s; podcast shorts 40 to 130 s each, 3 at a time on a saturated machine (the example pipeline's notes); ambient motion stepped at 15 fps so a hold costs about 15 unique frames a second, frames outside card windows hardlinked; a parallel finalize width of 4 at 2.12x realtime beat a width of 8 at 1.25x (`content/reference/render-reliability.md`).
- **Traps**: anything over 10 minutes goes through `scripts/render_detached.sh` (the shorts-editor skill); never kill during a render; "is it working" means the output file grows; an `npx hyperframes` ETARGET flake: run the cached binary from the npx cache; a runner waiting with `pgrep` on its own name matched itself and hung 4 hours; `render_detached.sh stop` kills the runner's whole process group (the build log); uncompressed `.mov` intermediates reached 98.7 GB across 4 projects; Chrome headless writes its screenshot then hangs on exit, so poll for a stable size, then kill it, and delete the target first.
- **Where it lives now**: mostly in a taste or reference file (the shorts-editor skill, `render-reliability.md`, the media-gen skill). The Chrome headless hang, the 15 fps ambient step and the hardlink trick were build notes only; they are here now.

---

## J. The editor's HyperFrames install versus the main machine's

- The editor's machine got HyperFrames on 5 Sep: `npx hyperframes` v0.8.29, ffmpeg 9.0.1 via brew, and `hyperframes skills` wrote 20 skill docs into the user-level Claude skills folder.
- The main machine's vendor skills were refreshed on 10 Oct as proposal P5 (refreshed by their own updater, 12 current); the folders there carry dates of 10 and 17 Oct. Nothing recorded the editor's machine being refreshed, so its vendor skills may predate the `--no-clipboard` flag notes, the `data-has-audio` change and the refreshed `springEase` helper that the HyperFrames gotchas list cites by file and line. Starting default: refresh the vendor skills on every machine on the same day, and note the date.
- Local customization of the vendor skills (hyperframes, motion-graphics, general-video, media-use): none found. Every local addition lives in tracked project files instead (the HyperFrames gotchas list, `motion-craft.md`, `springs.js`), which every machine gets by a pull. 3 vendor skills were symlinks into a separate local checkout on the main machine. A repo mirror of the skills folder differed from the live vendor skills (`diff -rq` listed changed files in motion-graphics and hyperframes-animation), so it was not a safe copy for another machine either.
- Project pins drift: 0.8.4, 0.8.17, 0.8.31, 0.8.33, 0.8.145 (the motion lab page, item 8), 0.8.71 (a live training's options script), 0.8.181 (the shorts studio research). Untested whether an old pinned project renders the same on a newer or older CLI.

---

## K. From the co-host's channel (added 29 Oct)

### No `-r` before a stills concat; ImageDraw on RGBA writes alpha
- **Final method:** never put `-r` before a concat of stills (it overrides the per-image durations and the motion collapses to a flash); draw onto an RGBA layer and `alpha_composite` it, because `ImageDraw` on an RGBA image writes the alpha instead of blending, so a step drawn at alpha 0 still shows once flattened.
- **Receipts:** the co-host's channel notes (the list-reveal notes).

## What was scattered before this book (29 Oct 2026), and what still waits on a ruling

1. **Untracked build files**: the guest U teaching-card builder and its `immediateRender` and 0.1 s lead pattern, the guest U state file with the card fixes, the guest U picks file that `story-animations.md` cites, and the guest Q guest-resource card overlay. The worked examples behind the newest podcast card rule were not on the editor's machine. **[Fixed 29 Oct: tracked with their projects.]**
2. **No CDN in a render** (GSAP from jsdelivr stalled the 4 Sep build twice) lived only in the guest X build files and a work log, and the shorts-editor template and the guest U builder still loaded GSAP from the CDN. It belongs in the HyperFrames gotchas list.
3. **Alpha formats and how to render them** (`--format mov|webm`, ProRes 4444 `yuva444p12le`, VP9 `ALPHA_MODE=1`, PNG-in-MOV) and the 2 failed transparent-PNG attempts of 20 Aug were in a work log only; the shorts-editor skill said HyperFrames has no alpha, and `content/taste/clip-bar.md` says ProRes 4444 at 24 fps while live overlays are 30 fps. **[Fixed 29 Oct: the shorts-editor skill corrected.]**
4. **Overlay frame rate must match the master**: practised per build (24 fps on Riverside), never written as a rule.
5. **The 17 signatures from the teardown** and the A, B and C animation parameters (settle 0.2 to 0.3 s, count-ups decelerating over 0.6 to 0.7 s and stopping on the said number, the ring ping, ghosted upcoming rows) were only in the research teardown and the animation looks notes. `shorts-formats.md` names the research without its contents. The count-up timing there disagrees with the shorts-editor back.out pop.
6. **The masterclass card style** (accent ground, white, Title Case, the featured product's orange on numbers, the timeline at 250 %, the pause-button transition, the errata card) is only tape quotes in `kinds/masterclass.md` and promoted lines in the editor's own guidelines; no taste rule. The orange hex conflicted: #D97757 (`thumbnails.md`) against #f0813f (the shorts-editor style reference), and the creator's eyedropper pick was never checked.
7. **Loading bar**: `must-dos.md` said no cut ships one until a pick; the yellow bar shipped on the masterclass, and "the accent was tried and rejected" was in an output page only. **[Fixed 29 Oct: the yellow bar is the pick, the creator's ruling.]**
8. **"Smoke and ash destroy the explanation"** and the hard-edged-container fix lived only in a tutorial's story-animations file marked superseded at its top.
9. **Movement passes** (push-in, punch-in, handheld keyframed in ffmpeg or HyperFrames; never regenerate pixels that carry captions) were only in a research folder and a work log, awaiting the creator's ruling.
10. **The 26 Oct look-by-moment assignment** (the account-book look for true numbers, Whiteboard for lists, Flat 2D mascot for mechanisms, Operator for screens) was in a work log only.
11. **The 9 Sep rejection of the HyperFrames story**: the why was never recorded; the 1 usable tick, "You full frame, animation as inserts", was only in the tutorial's interview file.
12. **The background-shift swoosh**: never used on a shipped cut; its synthesised whoosh might have conflicted with the "nothing synthetic" transition-sound rule (`editing-rules.md`); it needs `swiftc` on the editor's machine, untested there. **[Fixed 29 Oct: ruled real recordings only; the tool now needs `--sfx`.]**
13. **Liquid glass skipped, the text-behind-subject "po cast" example, the mark edge on the accent, the Chrome headless hang on exit, the 15 fps ambient step and frame hardlinks**: build notes or work log only.
14. **Vendor skill freshness**: the main machine refreshed the vendor skills on 10 Oct (and the folders show 17 Oct); no record showed the editor's machine refreshed since 5 Sep, while the HyperFrames gotchas list cites vendor files by line.
15. **Open with no answer on record**: a transitions vocabulary (podcast, since 3 Sep), H2's sound register, H1's blur judged by the creator, H3 text behind the subject, the guest Z covers and the Y2 and Y3 transitions, whether a word heard on a call meant the mascot, springs for shorts cards, the 2-mascots-and-a-human scene.

What the sweep could not reach: the transcripts behind the call quotes (the quotes were used as filed, not the raw tapes); the editor's machine itself (its vendor skill versions and whether `swiftc` exists there were inferred from its work log, untested); the render command that produced the guest U PNG-in-MOV cards (not in the builder or the chain scripts read).
