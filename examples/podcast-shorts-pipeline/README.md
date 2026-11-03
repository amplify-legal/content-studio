# Example pipeline: podcast and tutorial shorts

The reference implementation of the shorts builder as it ran after a multi-day build of podcast and tutorial shorts (about 230 numbered fixes, hundreds of renders, 4 review rounds). One spec JSON in, one finished 1080x1920 short out, with its poster, contact sheet and a checks file. It is the code behind the "Before you build a short" rules in `.claude/skills/shorts-editor/SKILL.md`.

It is an example to copy and adapt, not a black box. Every number in it was measured on real tapes and is a starting point for yours. The method under every number (what was tried, what failed, the version that works) is in the edit lab book, `content/reference/edit-lab/`, and the lessons of the build are at the end of this file.

## What is here

| File | What it does |
|---|---|
| `pipeline.py` | The builder. `plan` (the cut plan from the spec), `solve_geo` (each panel's scale and top row, solved from the rules together), `ig_hook_seam` (where the stacked hook splits), `panel_chain` (the ffmpeg chain per panel, the blurred extension, never black), `caption_groups` (sentence groups, laid out by a shortest path), `card_windows_split` (a card only around its key word), `credit_for` (the guest's own firm, never your brand beside their name), `AUDIO_CHAIN` and `SHAPE` (noise, echo, harshness, the limiter), `run_checks` (every gate). CLI: `--plan`, `--build`, `--status`, `--selftest`, `--requeue`. |
| `paths.py` | Every path and brand value, from `config.json` and environment variables. Nothing else hard-codes a path. |
| `config.example.json` | Copy to `config.json`: folders, the brand accent, your own brand and show names, guests' firms, path remaps. |
| `looks.html` | The graphic layer for the drawn looks (whiteboard, flat 2D, account-book, operator) and the native look (the title stickers, the caption sticker). Chrome renders it at every frame whose state changes; `window.setup(payload)` and `window.setTime(t)` make every frame deterministic in `t`. |
| `anim_looks.html` | The animation directions A, B and C and `ig_between` (the native look between animations). Picked per run with `SHORTS_LOOKS_HTML=anim_looks.html`. |
| `anim_variants.py` | Writes the direction variants of a keeper spec (title stays or goes, light or dark) and their queue lines. |
| `anim_selftest.py` | Proves `anim_looks.html` returns what `looks.html` returns when no direction is set, and that its ink stays inside the safe frame. Needs Playwright with Chrome or Chromium. |
| `tutorial_look.py` + `tutorial.html` | The tutorial look ("screen is the subject"): layouts A (screen hero), B (face on top, screen strip under) and C (the screen in its own band), from a per-short sidecar of zoom regions, marks, a card, and private boxes and masks. The screen is masked frame by frame. |
| `check_frames.py` | The frames a checker that did not build the short reads at full resolution, in a folder keyed on the render's mtime and size. |
| `lane_runner.sh` | One supervisor per lane (podcast, tutorial), its own queue file, run detached through `scripts/render_detached.sh`. |
| `springs.js` | Closed-form damped springs used as GSAP-style eases, so a seek to any frame is exact. |
| `specs/example/` | 1 invented podcast spec, 1 invented tutorial spec and its sidecar. Invented speakers, invented words, invented times: the shape is real, nothing else is. |

## What you need

- `ffmpeg` and `ffprobe` with libass (`ffmpeg -filters | grep ass`), Python 3.9+ with `numpy`, `scipy`, `Pillow` and `opencv-python` (the Haar face reads), and `playwright` with Chrome or Chromium (`python3 -m playwright install chromium`) for the graphic layer.
- macOS ffmpeg for a build: the encoders are `h264_videotoolbox` (pipeline.py `venc()`, tutorial_look.py lines 832 and 1494) and `aac_at` (pipeline.py `AAC`). On Linux change them to `libx264` and `aac`; `aac` overshot true peak on the build machine, so read `true_peak_ok` on the first shorts.
- The shorts-editor skill installed at `.claude/skills/shorts-editor/` (the pipeline calls its `check_caption_size.py`, `check_safe_area.py` and `verify_speaker.py`, and reads `brand.py`).
- Fonts in `.claude/skills/shorts-editor/assets/fonts/` (or `SHORTS_FONT_DIR`): the captions burn with the **static** `Montserrat-Bold.ttf` (in the Google Fonts zip under `static/`); the pages also load `DMSerifDisplay-Regular.ttf`, `DMSerifDisplay-Italic.ttf`, `Inter[opsz,wght].ttf` and `LexendExa[wght].ttf`. All are free Google fonts; none ships here. The pages also load the system monospace face Menlo from `/System/Library/Fonts/Menlo.ttc` (macOS): on another system, point that `@font-face` at a monospace `.ttf` you have, or the build stops on the missing face. A page that cannot load a face stops the build with the face's name, because a silent fallback would burn the wrong type into every frame.
- Per person, a constant-frame-rate video track (`<person>-cfr.mp4`) and a word-level transcript of that track in the Scribe JSON shape (`{"words": [{"text", "start", "end", "type", "speaker_id"}]}`), made with the shorts-editor transcriber and your key terms. Separate tracks per speaker are what let the cut take each person's own audio.

## Set up

```bash
mkdir -p content/videos/<set>/pipeline
cp -R ~/content-studio/examples/podcast-shorts-pipeline/* content/videos/<set>/pipeline/
cd content/videos/<set>/pipeline
cp config.example.json config.json      # then edit it: your accent, your own names, your guests' firms
python3 paths.py                        # prints every folder and value it resolved, and from where
```

Media paths in a spec may be relative: they are read from `media_root` (default `~/media-cache`), so a spec says `podcasts/podcast-guest-a/guest-cfr.mp4`. The render cache defaults to `~/.cache/shorts-pipeline/work`: keep it outside any folder a sync job mirrors, or the cache is copied while it renders and fills the disk.

## Run it

```bash
PYTHONDONTWRITEBYTECODE=1 python3 pipeline.py --selftest           # caption calibration, the round-1 caption cases, the solver on a measured source
PYTHONDONTWRITEBYTECODE=1 python3 pipeline.py --plan specs/<slug>/<id>.json      # the cut plan and the caption groups, nothing heavy written
PYTHONDONTWRITEBYTECODE=1 python3 pipeline.py --build specs/<slug>/<id>.json     # one short (cached, idempotent; --force to rebuild)
PYTHONDONTWRITEBYTECODE=1 python3 pipeline.py --status                            # ok, checks failed, no checks row, running, failed, to go
PYTHONDONTWRITEBYTECODE=1 python3 tutorial_look.py --regions specs/<slug>/<id>.json   # a tutorial's regions per layout
PYTHONDONTWRITEBYTECODE=1 python3 tutorial_look.py --build specs/<slug>/<id>.json --layout A
```

- `--selftest` needs no footage and no network: only ffmpeg with libass, the static Montserrat Bold and the shorts-editor scripts. It exits non-zero on any failed case.
- `--plan` needs the spec's word files and tracks (it measures the audio for the quiet points and reads the words to snap the cuts and group the captions); it writes only small caches under the work folder. On the invented example spec it stops at the first missing track, which is the expected result until you point it at your own.
- A whole set runs through a lane runner, detached:

```bash
# from your project root
echo "specs/<slug>/<id>.json" >> content/videos/<set>/pipeline/queue-podcast.txt
scripts/render_detached.sh start shorts-lane-podcast -- bash content/videos/<set>/pipeline/lane_runner.sh podcast
```

## The spec

One JSON per short, in `specs/<slug>/<id>.json`. `specs/example/podcast-guest-a-F1.json` is a complete invented example; the fields the pipeline reads:

| Field | What it is |
|---|---|
| `id`, `slug` | The short's id (`<slug>-F1`, `-M1` for a motion short) and its episode or tutorial folder. |
| `kind` | `format`, `motion` or `after` (a re-cut of a short already posted; `after_of` names the posted file). |
| `title`, `title_accent` | The title on top and the phrase in the accent colour. The title must match what the first 4 s say. |
| `format`, `look` | The format of the family (claim-band, held-line, pov-bit, story-proof, data-table, card-band, motion) and the look (`ig_native`, `whiteboard`, `flat2d`, `ledger`, `operator`, `tutorial`, `none`). `compare_look` renders a second look of the same short. |
| `people` | `host`, `cohost`, `guest`: each `name`, `file` (the track), `words` (its transcript), `offset` (file time = clock time + offset), `fps`, and optional `crop` (a region the face search stays inside), `firm` (for the credit), `note`. |
| `clock` | Whose file the times in `hook`, `question`, `answer` and `intro` are on. |
| `hook` | `mode` (`aha` opens on the kicker line, else the question opens), `pieces` ([start, end, speaker] on the clock), `text`. |
| `question`, `answer`, `intro`, `opening_line` | Pieces. The order rule: the aha line, then the question, then the answer, and the introduction of the guest at the END. |
| `speed` | 1.1 to 1.25 on talk. |
| `caption_drops`, `caption_fix` | Words dropped from the captions only (never the audio), and word fixes for the captions. |
| `credit` | The credit line. `credit_for` replaces it with `<guest> · <their firm>` when the guest has a firm on record; your own names never sit beside a guest's. |
| `graphic` | `kind` (`list`, `table`, `timeline`, `scene`, `bars`, `screen`, `none`), `items`, `keys` ([item, clock time] when each lights), `source_line`. |
| `screen` | A screen track to composite: `file`, `pieces`, `crop` (measured, or it is not composited). |
| `ig`, `ig_between`, `card_only_moving`, `igb_answer`, `ig_list_room` | Native-look options: the title emoji and a callout sticker; the native look between animations; a card only while it animates; per-short bounds. |
| `anim`, `anim_title`, `anim_dark` | Animation direction A, B or C, whether the title stays or goes, light or dark (written by `anim_variants.py`). |
| `notes`, `plan_why` | For people: why the cut is the cut. Never read by the code. |
| `blocked_on` | Set it and `--status` lists the short as blocked instead of building it. |

**Fix the spec's own fields, not only the function that overrides them**, keep the original spec in `specs-r<N>/` before a round of edits, and dry-plan every touched spec with `--plan` before a queue runs.

## The pipeline (the stages of `--build`)

Each stage is idempotent and cached under `WORKROOT/<id>/`, keyed on what it read, so a rebuild redoes only what changed.

1. **Plan and cut.** `plan` orders the pieces (the aha opener, the question, the answer, the introduction at the end), snaps every edge to a quiet point (a word that straddles an edge is kept whole, with its decay), and cuts each piece from the right person's own track in one trim-and-concat pass per person. A stacked hook shows the questioner above and the listener below on the same clock; an answer shows the speaker alone; every speaker change is a shot change. `solve_geo` solves each panel's scale and top row from the face read about once a second across the short (crown inside, footage to the blur line, the lowest mouth over the caption line, the face as big as that allows), with a fixed relax ladder; `panel_chain` builds the ffmpeg chain, the blurred and faded extension where the source runs out, never black.
2. **Audio.** Each piece from the speaker's own track through `AUDIO_CHAIN` (resample, declip, high-pass, low shelf, tracked denoise, de-esser, a dynamic EQ cut around 5.5 kHz, a soft gate) and `SHAPE` on the joined take (a soft transient compressor, a 3 to 8 kHz band compressor, the limiter), each piece read back and stepped down a ladder of lighter chains when it is not finite or runs hot, a band guard per speaker against dulling, the level corrected on the wav, then a limiter (oversampled) and one AAC encode: -14 LUFS, true peak under -1 dBTP.
3. **Captions.** `caption_groups` groups the words by sentence and lays the lines out by a shortest path (no 1-word line, nothing under 0.3 s, never across a cut or a shot change, a function word never ends a line), drops fillers and backchannels from the captions only, prints numbers as digits, and keeps every caption box off every face box on screen at that moment. Drawn looks burn through libass (the static Montserrat Bold at 104, 118 for the first 8 s, the current word in the accent, a dark box per line on light ground); the native look draws its caption sticker on the page.
4. **Overlay.** The looks page (`looks.html`, or the page `SHORTS_LOOKS_HTML` names) opens in Chrome through `paths.page_for_this_mac` (tokens filled: fonts, springs, accent, logo, mascot), `window.setup(payload)` lays it out and returns what the checks read, and `window.setTime(t)` draws every output frame; a frame whose state signature matches the one before is a hardlink, so only frames that change are screenshot. A card shows only in its window (`card_windows_split`: 1.2 s before its key to 2.5 s after, a 0.3 s crossfade, never in the credit's last 6 s). Composited with ffmpeg; every `-loop 1` input carries `-t`.
5. **Checks** (`run_checks`, below), a contact sheet and a poster.
6. **Write.** The finished files and one results row. `--requeue <tag>` removes only that tag's exact outputs and its exit file (never a reviewer's file) so a runner builds it again. With lane_runner.sh, also take the tag's line out of done-<lane>.txt: the runner never renders a line that file already holds.

## What it writes

Per short, in `OUT/<slug>/` (default `finished/<slug>/`): `<id>.mp4` (h264 1080x1920 30 fps, AAC 48 kHz, -14 LUFS, true peak under -1 dBTP), `<id>-poster.jpg`, `<id>-sheet.jpg` (frames at the start, every cut and every 5 s, for a reviewer), `<id>-checks.json` (every gate and its numbers), and one row appended to `results.jsonl` beside the work folder. The last row per id is the one that counts, and `ok` in that row means the gates passed, not that a person or a reviewer passed the short.

## The checks (`run_checks`)

The build stops non-zero on a failed gate. Among them: the caption size (the exact style that burns, through `check_caption_size.py --style`), the safe frame and the face in the bottom band (`check_safe_area.py`), no caption box meeting a face box at the same time (`caption_face_ok`), the face high and whole, the blur only under y 1640, nothing black, the title fitting its band and leaving in time, the credit under the right face and long enough to read, the speaker on every answer piece (`verify_speaker.py`, read with the word files), caption coverage, duration, true peak and loudness, and frame 0 being the designed title frame. The reviewer's read is separate: a checker that did not build the short reads `check_frames.py`'s frames at full resolution and writes its verdict as `<id>-r<N>.json`.

## Lessons from the build (as method)

These rules come from the build log of the run that produced this pipeline: about 300 specs (podcast shorts, tutorial shorts, animated variants, before-and-after remakes), 4 review rounds, about 240 numbered fixes, each written as "what failed, cause, fix". Every lesson below is one of those fixes generalized; "(fix N)" points at its row in the build log, "T:N" at the tutorial look's rows. The numbers are measurements of the pipeline, kept so you can check your own.

### Geometry and faces

- **Sample the face across the whole short, never at a few fixed points.** The first face cache read 10 frames at 3 points and missed the lean-ins: 12 shorts landed 2 to 106 px into the caption band. About 1 frame a second (up to 28), the lowest chin plus a quarter head, fixed it. (fix 4)
- **Take the crown from the highest brow seen, not the median box.** The detector's box runs brow to chin; the crown sits about 0.55 box heights above its top (0.45 was short under a hairline). Holding the median box's crown still cut heads that lift. (fixes 23, 34, 40)
- **When the crown and the chin bound fight, the crop grows (the face gets smaller); it never cuts.** Grow 8 % a step, past the source if needed (up to 1.6x its height, the faded extension fills below); pillar only when the region's width runs out. (fixes 33, 36, 48)
- **Solve each panel; do not place and clamp.** After 12 fixes that clamped, 14 of 14 renders were 26 to 32 % blur. A solver that picks scale and top row inside the rules (crown inside with 2 % above, real footage to the blur line, the mouth of the lowest lean-in over the caption line), with the old clamps kept as an ordered relax ladder, fixed the class at once. (fix 82)
- **Make faces big, and bind the mouth, not a fixed chin y.** Faces of 140 to 175 px read as "nobody is here"; about 1.5x that is the default. The real rule behind a "chin at 1260" bound is "the mouth stays above the caption ink". (fix 83)
- **Never a flat band and never black pillars.** A crop narrower than the panel sits over its own picture stretched, blurred (boxblur 30) and dimmed (-0.12); a run-over above the tape is blurred picture, or plain ground only as tall as needed. (fixes 82, 228)
- **Blur only the bottom of the frame.** First 20 % (footage to y 1536), then 15 % (to 1640) by taste. (fixes 71, 171)
- **Size the blur radius to the strip.** boxblur fails when its radius passes the chroma plane's limit: radius = min(40, height/4 - 1) at every size. It took 3 crashes (a 2 px, a 56 px and a 128 px strip) to land on the formula. (fixes 59, 64, 79)
- **Ask for the neck and collar only down to the tape's own bottom.** A webcam picture that ends at the chin cannot show a collar; asking for one pushed every seam to the last relax step and zoomed the face. (fix 230)
- **A small face in a stacked question: search the seam, then play it full frame.** Search the seam in 8 px steps, solve both panels at each, keep the seam whose smaller face is biggest; if that face is still under 272 px, the question plays full frame on its own speaker. 300 px would have flipped every hook in the set. (fixes 201, 221, 233, 234, 238)
- **Measure a webcam bubble's crop inside its corner radius, and mark it a hard edge.** A crop at the bubble's bounding box showed board text and the app's zoom bar; a crop free to rise above the region showed the board over the hair. (fixes 47, 49)
- **A full-frame face search has a minimum size.** On a 1920 frame the detector's minimum was about 230 px, so a 100 to 150 px bubble face was never found and the fallback shipped the raw screen. Give a crop hint, and refuse a person with no face and no box (a named row, exit 2). (fix 19)
- **Keep where the detector looks apart from where the crop may go.** A tight hint was both the search window and the crop's limit, so the crop came out narrower than the frame. 2 fields: `face_region` (search) and `crop` (allowed area). (fixes 224, 229)
- **Hand-measured face boxes use the detector's convention.** Boxes drawn brow to beard (420 px tall) failed the bounds set for brow-to-mouth squares. (fix 54)
- **A recording whose layout switches inside a piece needs per-run crops.** 1 crop per person showed the wrong person or an empty wall on a composed solo/split file; a layout list per person, measured from the frames, picks a crop per run. A lean on one piece gets its own crop the same way. (fixes 51, 126)
- **A tiny tile is a medallion, never a 4.4x blow-up.** A 244x136 video-call tile scales 2.5x with a border, over its own blurred, darkened stretch: on light ground, white captions vanished. (fixes 50, 58)

### Captions

- **Measure caption size in pixels.** libass sizes 104 and 118 give 47 and 53 px capitals; a check measures the drawn capitals on every build.
- **Snap a piece edge only to a word that straddles it.** Keeping any word that starts within 80 ms after the out point pulled in the next word; the rule that held: a word starting before b - 0.02 and ending after b + 0.02 is kept whole to its end plus its decay. (fixes 16, 22)
- **Backchannel removal must not eat the speaker's own last word.** A closing "okay." that ends the speaker's sentence stays; a lone "Okay." between sentences goes. (fix 24)
- **Lay out caption lines by shortest path, never greedily.** Greedy chunking stranded words for 0.05 to 0.39 s. Costs that held: a 1-word line 1000, a line under 0.3 s 500, a width over 760 px refused, a crossed cut 8, a function-word ending 4; a short group may hold up to 0.10 s into the next. (fixes 84, 143, 202)
- **A lone word passes only when no neighbour could share its line.** A "12 letters or more" rule missed an 11-letter word; the rule that means what it says asks whether any neighbour fits beside it at the caption width. (fixes 235, 242)
- **Captions never sit on a face.** The check: no caption ink box meets a face box (brow to lower lip) of any panel on screen at that moment. On a stacked hook the caption is 1 line in the seam; a block that would start above a chin is set lower; a big opening group over a face stays 1 line. (fixes 90, 200, 238)
- **Captions over light footage get a box.** A dark translucent box (0.70) per line, on its own layer: the box on the text layer showed darker seams at colour runs and between lines. (fixes 220, 238)
- **Numbers print the way the graphic prints them.** Money said on tape takes the graphic's money format ($25K, $3,500); "twenty-six-page" becomes "26-page". A per-spec word fix map repairs transcriber errors, and a key written with punctuation replaces the word whole. (fixes 25, 89, 123)
- **A second voice inside a one-person spec gets its own caption style.** An AI agent on a live call was filtered out by the speaker filter; a piece the speaker's own words cover under 30 % takes the other voice's words, in a second style with a label. (fix 5)

### Graphics and the looks pages

- **Type floor 44 px; page a window instead of shrinking.** Rows of 22 to 40 px failed review; 1 column, labels 44 px, a window of 4 rows that pages as keys light. The page reports its smallest font set and a check reads it. (fixes 27, 86)
- **Never delete what the page cannot place; give it its own band.** A sub line deleted when it passed y 506 erased every 2-line title's sub. (fix 11)
- **Shrink-to-fit measures the inner span.** A flex box's scrollHeight never reports the overflow, so labels clipped at 4 lines. (fix 35)
- **A compare look must change the drawing, not the theme.** Compares came out as the same graphic recoloured; the look now remaps the kind (timeline as table rows on one look, as numbered boxes on another). (fix 30)
- **Show pending rows dim from frame 0.** Hidden rows left a whiteboard panel blank for up to 10 s before its first key. (fixes 15, 41)
- **Break titles in balanced lines and title-case each hyphen part.** Greedy browser wrapping left "A" alone at a line end; punctuation attaches to the word before it. (fixes 14, 87)
- **The title leaves at 28 s on every short.** An "under 35 s keeps it" exception confused the checker and was dropped for the literal rule. (fixes 175, 189b, T:228)
- **A card shows only around its keys, with a 0.3 s crossfade.** A window from 1.2 s before a key to 2.5 s after, the piece split at the nearest 0.12 s gap (else the nearest word boundary, never inside a word); a check fails a card still for 3.4 s past its last key. (fixes 85, 91)
- **The credit: 1 line, fitted, off while the introduction says the name, ending where the guest last speaks.** A credit over the host's introduction made viewers read the host as the guest. (fixes 75, 188, 232, 239)
- **Nothing else fights the credit in its last 6 s.** No card window and no stacked pair there; a duo piece straddling the line splits at the last word boundary. (fixes 193, 204)
- **Strip on-screen promises that are not live.** "Full talk in the comments" shows only when the spec says the long form is live. (fix 45)
- **Tie page decoration to state, never to frame 0.** Rounded panel corners sat at y 0 whenever the band was 0 high (798 to 6,480 ink px in the top 120); a glow bloomed into the band; a 2 px band mid-transition was misread. (fixes 192, 206, 217, 219)
- **A light variant needs its own palette, and a look at it.** The light twin rendered as dark as the dark one because every colour choice ignored the flag. (fix 208)
- **When the order changes, every page reads the new hook window.** Moving the stacked question after the opener broke 2 pages separately, 1 fix apart. (fixes 223, 227, 236)
- **Prose belongs on a card, not in a row.** An 80-character prompt written as a row clipped at 3 lines. (fix 38)

### Audio

- **Correct loudness on the wav and encode AAC once.** The native aac encoder took a -2.1 dBTP wav to +3.6 dBTP; `aac_at` gave -1.9. 12 shorts failed true peak until the take was levelled before the single encode. (fix 2)
- **Limit true peak oversampled.** A sample-rate limiter let a clipped source out at -0.8 dBTP; at 192 kHz (4x) it holds. (pass 1 notes)
- **Read every piece back and fall down a ladder of lighter chains.** A clipped phone source ran to +12 LUFS before loudnorm; each piece is checked finite and under +6 dBFS, the chain stepping down until one holds, and the one used is logged. (fix 190)
- **Measure harshness with a band meter.** The first numbers came from a whole-signal FFT band cut on a mono downmix and read the limiter's ceiling as spikes. The meter that held: a 6th-order IIR band 3 to 8 kHz, 50 ms windows, stereo averaged. (fixes 207, 218)
- **De-harsh in layers, then reject anything that dulls.** De-esser, a dynamic EQ cut above 5.5 kHz, a band compressor on 3 to 8 kHz, a 25 ms fade at every join. Measured: 50 ms windows over -3 dBFS 231 to 6, band peak -3.0 to -9.6 dBFS. A stronger chain was rejected: it took the voice's 3 to 8 kHz balance from -14.9 to -20.7 dB. (fix 218)
- **Guard each speaker against dulling on the finished take.** A quiet call track lost 9 dB of brightness; each speaker's stretches of the take are read against the source, and a speaker more than 6 dB under (and under -20) steps to a lighter chain. Per-piece and per-chunk versions were tried and rejected on measurement. (fix 240)
- **With no dereverb model, use what a filter chain reaches.** Tracked-floor FFT denoise, a gentle de-esser and a mild downward expander on the tail; per-person extras go in the spec and in the cache key. (fixes 69, 170)

### Specs and the planner

- **A starting default order (change it in your taste file): the aha line first, then the question, the answer, the introduction at the end.** The question before the introduction read as jarring. (fix 174)
- **The title says what the first 4 s say.** 30 of 136 openers carried a title from a different line; every twin is retitled to its own opener, and a twin identical to its base is never written. (fixes 73, 120, 152, 165)
- **A spec fault is fixed in the spec.** A host line labelled as guest showed the guest saying "Yeah" for 6 s; crops sat in reviewers' notes and never in the specs. (fixes 3b, 20, 53)
- **A new shape for a field breaks every reader of it.** A hook piece with a 3rd element crashed the retime path; an invented role crashed the planner. Grep every reader when a shape changes. (fixes 78, 128)
- **Off-limits topics are cut in the spec, base and twins alike.** A cut made on a twin was missed on its base until the next round. (fixes 150, 162, T:214, 216)
- **Private UI is masked on every frame it reaches.** A config path masked at 1 scroll position came back at 2 others; masks are tracked per frame by template match and each carries a check entry. (fixes 104, 105, 140, 141)
- **Dry-plan everything before and after a change.** `--plan` on every spec, old pipeline against new: the lists differ only on the specs the change meant to touch. (fixes 183, 242, 243)

### Checks and reviewing

- **The speaker check reads the word files, not only the lips.** 23 false fails came from lip motion alone (a screen piece, a sub-second piece, a soft line); word coverage clears or convicts a piece first. Words over 4 s long (a 51 s transcriber artefact) are dropped. (fixes 3, 55)
- **A check reads the layer it is about.** Ink outside the safe frame is tested on the overlay layer; a white shirt in the rail is footage and a warning. (pipeline notes)
- **When a third-party check misreads, record an override with its rule.** A safe-area tool read a neckline as a 614 px face; the override fires only when its box barely overlaps the pipeline's own face box and the mouth is clear. (fixes 89, 127, 225)
- **Move check thresholds with the layout.** A title raised to y 260 failed a check still floored at 290; face bounds differ per look. (fixes 61, 199)
- **Status reads the results row, never the file.** A file with no checks row was reported "ok". (fix 9)
- **Key check frames to the render.** A re-render was read through the old frames; frames now sit in a folder named by the render's mtime and size. (fix 88)
- **Every failure class becomes a check.** The run added `face_high_ok`, `blur_bottom_ok`, `caption_lines_ok`, `caption_face_ok`, `card_still_ok`, `credit_face_ok`, `graphic_type_ok`, `title_crown_ok`, `screen_crop_ok`.

### Running the queue

- **2 builds of 1 spec must not share scratch.** A primary and its compare in 1 work folder pruned each other's files mid-render; a lock per tag, per-tag scratch names and a pruner that removes only its own look fixed it. (fix 1)
- **Stopping a detached runner by process group kills its builds.** 6 builds died mid-render. Kill the supervisor processes first, then the runner; a supervisor relaunches a killed child once; restart under a new name. (pass 2 notes)
- **Timeouts count only running time and are sized for a loaded machine.** A 120 s + 8 s a second timeout killed pieces at load 400; 600 s + 30 s a second (cap 3600) held. A frozen job's wall clock is not its time. (fixes 65, 191)
- **A saturated machine is slower, not faster, with more lanes.** At its worst a build took 280 to 430 s instead of 100, then 30 to 45 minutes; the queue dropped to 1 or 2 renders at a time.
- **Disk: hold, never delete to make room.** Under the floor (`HOLD_GB`, 25 GB by default in `lane_runner.sh`) a batch is written to a hold file and polled; a full disk killed builds and then the whole machine (swap could not grow). Keep render caches out of any synced folder, and freeze a render (SIGSTOP, resumed with SIGCONT), never kill it.
- **1 supervisor per lane when a render gate counts supervisors.** A second lane's start was refused all evening; 1 runner per lane, counting only its own render, runs every kind of line. (fix 74)
- **1 queue file per line; a re-render voids a pass.** A short listed in 2 queues rendered twice, after its pass. (fix 236c)
- **Never delete a reviewer's file.** A requeue's exact-name list carried the reviewers' per-short JSON for 35 minutes and removed them. (pass 1 notes)
- **A redo list must know when a row is already newer than the fix.** It rebuilt a fixed short twice. (pass 2 notes)
- **Hold lines in place while builders change the code.** No render is spent on code about to change. (polish notes)
- **A synced-drive file can be a placeholder.** A source sat dataless until downloaded; check the bytes before a build.

### Process

- **The conductor writes a table: what failed, cause, fix, where.** A row without a cause is not a fix.
- **Proof builds before a queue.** 1 to 3 real specs, read at full resolution, before the queue starts; each fix gets its own proof render.
- **A reviewer that did not build it.** After pass 1, 0 of 57 passed a separate reviewer; 2 passes later 3 of 12 passed the smoke read. The builder's "looks fine" is not a verdict.
- **Probe without rendering when renders are blocked.** A scratch probe runs the plan and the solve exactly as the build does; label every result UNTESTED until a render proves it.
- **Readings taken are logged.** Where the creator's words allow 2 readings, take the closest, write which, and move on.
- **Rulings land in the taste file.** A ruling repeated across shorts becomes a default in the pipeline and a line in your taste file, never a fix on 1 spec.
- **Read the clock off `date`.** The log's stamps ran ahead of the machine 6 times; a correction note fixes them.

### Known edges

- A pause over 1 s inside a piece is not cut.
- A measured screen file is composited from its 0 s, never seeked to its pieces.
- A timeline has no marker for a moment that is not an event.
- Bars with values have no type floor.
- A face estimate is 1 box per short in the tutorial look: a deeper lean is not caught.
- A collar below the bottom of the webcam picture cannot be shown.
- A stacked question cannot always reach 300 px for both faces under a 2-line title; the full-frame fallback trades that.
- A 1.5x face on a drawn stacked hook can sit under the hook's caption for its 2 to 4 s.

### How to keep your own build log

| # | What failed | Cause | Fix | Re-rendered |
|---|---|---|---|---|

- A fix names its cause; "changed X" without "because Y" is not a row.
- A re-render is named: which tags, on which code.
- A slip of your own is written down (a delete on a variable path, a stop that killed builds), with what replaces it.
- A rule reported "fixed" carries the measurement that proves it, or the word UNTESTED.
- Correct a wrong row with a new row; never edit the old one.
- The trap to name: anything keyed on an id alone (frames, redo lists, caches, requeues) goes stale the moment the same id renders again; key it to the render.
