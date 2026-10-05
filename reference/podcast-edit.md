# Podcast edit craft

> Installed to `content/reference/podcast-edit.md`. The generic pipeline craft for editing a conversational episode in a Claude session: the rulings a working pipeline converged on and every trap it paid for, written as rules. The step-by-step manual is `content/reference/podcast-edit-runbook.md`. Your own host's taste calls go in `content/taste/editing-rules.md` and win over any default here.
>
> **How to read the numbers.** Every measurement below came off a real tape on a real pipeline. Where something is unproven, it says so.

---

## 1. The opener

- **A trailer, not a teaser.** A chain of micro-clips, 1 to 5 seconds each (a hair over is fine when the line needs it), hard cuts, about 25 to 45 seconds total, capped at 30 to 40. The bar is energy and impact: "I should definitely stay to listen to this conversation."
- It may sit as a cold open or right after the intro. That is the host's call per episode; a cold open first is a sensible v1 default.
- **A laugh is a pickable moment on its own.** One working pick was a single line plus the other person laughing, with the rest of that candidate cut.
- **Nobody introduces themselves inside it.** The introduction comes after.
- **Before a trailer clip ships, look at both faces.** An unengaged listener face kills the clip even when the line is good. It adds nothing to the viewer.
- **It closes on suspense**: a clip that alludes to the big deliverable, hard-cut right before the reveal.
- **Inside the trailer, a clip ends on the last word's decay, not on a policy gap.** The body's silence policy is too loose for a montage: a 0.6s tail on a 3s clip is a fifth of it. Any residual tail over about 0.15s is trimmed.
- **The candidate clips go to the host as clips before they are assembled**, and the assembled trailer is rendered and shown as its own file before the long render starts. 3 passes once shipped "a bit awkward" because self-review kept passing it and the host only ever saw it welded to 28 minutes.
- **Any structural change to an opening is read back as a table and confirmed, then a 60 second opening preview goes out before the full chain runs.** A promise to "ask at the end" is a question that blocks the build.
- Trailer clips carry the bold uppercase caption style. No name plates during the trailer.

## 2. The cut

- **One shared timeline** when the recorder exports one aligned track per participant: every cut hits every feed.
- **Joint-silence gaps of 1.0s or more tighten to about 0.6s.** Never leave a kept sliver under 1.2s between 2 cuts (the machine-gun guard). **Laughs sit inside protected no-cut zones.** Keep all 3: together they are what makes cuts read as clean.
- **Filler stays in the audio**; captions drop standalone uh and um. Chasing every "um" in a 2-shot makes visible jump cuts.
- **False starts and stutter runs cut on word boundaries** from the word-level transcript, and every boundary gets a machine-checkable verification: snap to measured silence and report the energy at the boundary. Word-timestamp cuts straight from a transcript leave words cut off and words that run long.
- **A pause is cut only between 2 transcript words**, and only where at least 0.6s of that gap is measured quiet. Tightening every stretch below a dB threshold clipped 5 quiet spoken words in a 9 minute cut.
- **Post-show tape is a quarry, not garbage.** An outro insert and a sign-off have both lived after "we'll edit this part out".
- **Content trims prefer list-like litanies over stories.** A trim that breaks a sentence's weave does not happen for a few seconds' gain.

## 3. Shots on one camera

- **Show crop options as stills before committing** to any reframe.
- **The leg problem is a pose problem, not a bottom-of-frame problem.** With crossed legs the knees and feet sit centre-frame, so any symmetric punch-in makes legs bigger. All 3 zoom levels on one reference frame were rejected for exactly this. The fix is **singles**: chest up for one person, head and shoulders for the person whose crossed knee rides chest-high. Singles double as the missing second angle.
- **Judge a reframe on the frame where both people have their legs crossed.** That is the episode's resting composition, not a gesture frame.
- A grammar that worked: the wide at a 1.35x punch-in as the base, singles at 2x and 2.5x, and once both people settle the wide dominates with singles sprinkled by feel. The numbers are properties of that framing; measure yours.
- **A generated second angle of a real person on a real tape is unproven.** Its first attempt is a test clip the host sees alone.
- **Transitions get a vocabulary per cut type** (wide to single, single to card, card to a second feed), designed with the host on real footage: 3 to 4 treatments per pair, and they react to clips, not to descriptions. No transition rule is written before the host has watched one.

## 4. Captions

- **Keep a long episode's captions calm.** Uppercase bold sans, 3 to 4 words, the current word in `{BRAND_ACCENT}`, one group on screen at a time, **no scale pop**, about 62px on 1920x1080. A pop belongs to a style demo; across 30 minutes it jumps at the viewer.
- **The highlight renders in one libass pass**, as pure ASS karaoke events. A frame-by-frame PIL path took hours to render.
- **Pin the base colour before the transitions** in every word's override, or the highlight runs backwards (every word arrives highlighted and drains as it is spoken).
- **No group ever wraps to a second line stacked above the previous one.** Time it so each group replaces the last (`\q2`, and size the longest group to fit).
- **Calibrate the font size.** libass rendered one bold sans at 0.63x of the size PIL measured. Uncalibrated captions come out small and gappy.
- **The ASS `Format:` line declares all 10 Dialogue fields**, or margins render as literal text on screen.
- **The caption block never crosses a speaker's mouth**, on any layout. Check a full-resolution frame of each speaker talking before the render ships. Name cards give way: they go lower and may overlap the frame's bottom edge. Captions do not move up to make room for them. On a collapsed screen-share card, the caption block stays inside the share well, never straddling its edge.
- **The word gap is measured as libass draws it.** A per-word layout must add the style's per-letter spacing and both outlines to the PIL advance, or the visible gap shrinks to about 7px and a line reads as one run-on word. About 26px visible is right. A group wider than about 1500px on a 1920 frame goes out as 2 caption frames.
- **Proper nouns and URLs are verified at caption build, before the burn.** Every capitalised token, domain and organisation name comes out of the ASS and is checked against the guest's real assets. A misheard compound word and a missing letter in a domain both got burned in and passed self-review. Verified names go into a `known_nouns.txt` as the audit trail.
- **An all-caps style hides every proper noun from the checker**, so a person spot-reads the intro captions on every episode.
- **A key word guessed from context is still a guess.** A machine heard one word, a context guess picked a second, and both were wrong. The tape settles it.
- **A transcript false start ("c-", "jo-") is dropped from the captions, never stripped of its dash**, or it shows as a stray letter.
- **Backchannels ("mm-hmm") are dropped** when the other speaker holds the floor. On a 2-host recording, crosstalk under the other person's sentence is the main caption fault: read every caption against who is speaking before the review.
- **On a vertical derivative: 78px in a 1080-wide frame and never below it**, judged at 375px phone width. On shorts the block also ends at or above 78% of frame height (`content/taste/shorts-formats.md`). A corpus finding never overrides a floor the host set: 2 independent review passes once recommended shrinking and both were wrong.

## 5. Key terms: names are fixed at transcription time

**Every tape carrying names gets a key-terms list handed to the transcriber, never a find-and-replace afterwards.** Write the episode's own `build/keyterms.txt` (the hosts, the guest, the companies, the products, the terms of art) and pass it:

```bash
python3 .claude/skills/shorts-editor/scripts/transcribe.py raw/guest-720p.mp4 --edit-dir build --keyterms-file build/keyterms.txt
```

**The engine order:**

1. **ElevenLabs Scribe `scribe_v2`** (`transcribe.py`, `ELEVENLABS_API_KEY`) is the default.
2. **Deepgram `nova-3`** (`transcribe_deepgram.py`, `DEEPGRAM_API_KEY`) is the declared fallback, for when Scribe is out of credits, keyless or down. It takes the same `--keyterms-file`.
3. **Local whisper** (`transcribe_local.py`) is last resort, for no network and no key. It takes no key terms at all, which is the practical reason it sits last.

**The engine that ran is named in the output file's own header**, never inferred and never a silent default.

**Why it matters, measured.** On one tape, an older Scribe model returned 2 wrong spellings of 2 names; `scribe_v2` with key terms returned both correctly. A downstream replace cannot recover what the model never heard, because the word boundaries and timings move with it. A bench across 3 tapes scored the confirmed proper-noun sites per engine:

| Tape | Scribe v2 + key terms | Deepgram nova-3 + key terms | Deepgram, no key terms | Local whisper |
|---|---|---|---|---|
| A (all 3 engines ran) | 17/17 | 16/17 | 13/17 | 11/17 |
| B | 21/21 | 21/21 | 12/21 | did not run |
| C (2 engine families only) | did not run | 47/47 | | 25/47 |

The key terms are most of the difference on either API.

**3 things that bite:**

- **The transcribers cache on the filename.** A pipeline that rewrites the same output name needs `--force`, or it hands back the previous run's words and every caption index points at the wrong line.
- **A cut built on Deepgram words cuts on STARTS.** 90% of its inter-word gaps are exactly zero, so a word's end is really the next word's start, and an outpoint taken from a raw end lands late. `transcribe_deepgram.py` snaps ends to measured energy by default, which removes a 45ms systematic late bias but does not tighten the scatter. Prefer starts anyway.
- **Deepgram writes numbers as words** where Scribe writes digits, so a caption built on it needs a number pass first. And its diarization is weaker on the guest than on the host: never burn a named caption from it.

## 6. Audio

- **Mix every track with `normalize=0`**, 30ms fades at every segment edge, `loudnorm=I=-14:TP=-1.5:LRA=11` once, at the very end.
- **A boomy mono bus** (one mic for 2 people, peaking at 0 dBFS): `adeclip,highpass=f=120:poles=2,lowshelf=f=220:g=-5,afftdn=nr=8:nf=-34,alimiter=limit=0.95`, then loudnorm. Measured on a 30 second slice: the low band (under 150 Hz) went from -27.9 to -31.3 dB mean, peaks from -10.5 to -14.5 dB. A built clip peaked at -1.4 dB after the chain.
- **Every derivative inherits the episode's audio chain.** Every short, reel and clip runs the episode's own chain before the speed pass, or reproduces it exactly. Write the chain down where a shorts session will find it, not only inside one render script.
- **Music from a licensed library, never generated.** The bed sits clearly under the speech: about 19 to 20 dB under the voices was right where 6 to 7 dB under was "way too loud". **Measure bed against voice in the same window before a render is shown, and say the number.** One shape that worked: the bed under the trailer and intro animation, fading out over the 7 seconds before the intro animation ends.
- **A secondary feed** (a phone livestream) measured about 12 dB under the main mix (mean -25.4 dB against -12.8 dB). Lift it to roughly 6 dB under, and err toward lower volume.

## 7. The finish

- **Speed last, captions first.** A conversational episode can ship at 1.1x with pitch preserved; captions burn before the speed pass so they stay synced.
- **A resource promised on tape is shown on screen**, as an animation that walks through it (step one appears, then step two), not just a static card and not just a link. The resource takes the frame screen-share style (the document fills the card, the speaker shrinks to a corner) while it is being enumerated.
- **On-screen text that quotes the tape names its transcript line and timestamp** at the top of its build prompt. A walkthrough built from the wrong passage cost a re-render.
- **Name plates**: on from the intro through about the first minute of conversation, off for the body, back on for the goodbye. Each EDL segment carries a `plates` flag and the clip cache key carries a no-plates suffix so both states coexist.
- **Never upload before the host has seen the file**, even under an explicit end-to-end autonomous mandate. A long public artifact is not the kind of irreversible thing an autonomy grant covers.
- **Handing the file to an editor or an NLE is a supported ending.** Hand over the derivative-dependency list (chapters, description timestamps, short in and out points) with the one command that re-derives them from the new runtime.

## 8. Pipeline lessons, paid for in hours

### The render

- **"Is it working?" is "is the output file growing"**, never the CPU meter. Every long render writes a status file beside its output every 30 seconds or so (elapsed, bytes, growth rate, ETA, PASS or STALLED), and the session surfaces it unprompted rather than waiting to be asked. A host once asked "is it actually working?" 3 times over 3 days and got 3 opinions.
- **Long renders run detached** (their own session, parent is the system, never a child of the conversation). A conversation-owned render died 3 ways in one day: an out-of-memory kill, a session sweep, and the user's own pause. Use `scripts/render_detached.sh`.
- **While any render runs, no Claude process gets killed.** A forked session keeps the original process, so its age says nothing about what it currently owns. Prefer pausing file sync and closing browsers.
- **Render lock: while a render's pid is alive, no other heavy job starts.** Load average once hit 241 and blocked an upload for 35 minutes.
- **The runaway tail.** Any ffmpeg graph with `-loop 1` image inputs keeps producing frames after the main video ends ("More than 100000 frames duplicated" is the tell). It masqueraded as an out-of-memory crash at "98%" and as 17 hour renders. **Every command with a looped image gets an explicit output `-t`**, belt and braces with `shortest=1` on the first overlay. Salvage: SIGINT, not SIGKILL; the head of the file is intact. An aerial step with `-t` only on the inputs produced a 367 second trailer; the duration check after every build caught it in seconds.
- **The framesync stall.** Finite image-sequence overlay inputs against a mismatched frame rate can hang forever at a huge memory number with zero output. Bake plates in with `-loop 1` (infinite) images only, composite entrance animations frame by frame in PIL, and keep the final pass to subtitles plus loudnorm.
- **A segment at 0% CPU is a deadlock.** A 1.5s segment hung 13 minutes with `-ss S -t d+pre+0.2` because its audio ran out exactly where `apad` began. With 1.0s of slack on the input window it rendered in 0.4s. That was not the whole cause: a 75s segment then stalled the same way under memory pressure while the identical command ran in 11s by hand (cause unproven). The fix that holds is structural: `-nostdin` on every call, a bounded wait of 60s plus 3x the duration, one retry.
- **The memory gate reads memory pressure, not swap used.** The OS keeps swap allocated after the pressure is gone; a gate on swap used sat waiting on a machine that was 49% free. On macOS, `memory_pressure`'s free percentage is the kernel's own verdict (25% or more free releases the render).
- **`timeout` does not exist on macOS** and every step using it exits 127. `perl -e "alarm N; exec @ARGV"` is the portable version.

### The frame and the timeline

- **Assert the frame before spending the hours.** The first plated segment renders alone and its frame 0 is checked against the real assets pixel for pixel. A version rendered 13 hours overnight was rejected in the first minute on the frame.
- **Cropped overlay images go at the original frame bbox position**, not at their own (0,0).
- **A segment rendered without pre-roll starts with an empty well.** Seek 0.5s early and trim.
- **Chunk bounds sit on the output frame grid.** A parallel finalise cuts the master into chunks and speeds each up; a chunk whose sped-up length is not a whole number of frames loses up to a frame at its tail, and sample-exact audio then runs ahead one frame per chunk (121ms on one cut). An earlier version passed only because its bounds happened to align.
- **The finalise bounds its chunks on the real master, never on EDL arithmetic.** An EDL total 0.19s short of the master cut the last chunk short, and the deep pass read it as A/V drift.
- **A layout probe is a property of the tape it was measured on.** "It is a screen share if the left region is brighter than 110" read every 2-shot on another tape as a share, because that guest's wall was bright. Every episode gets a fresh 1 fps layout scan checked against a contact sheet, and the trailer reads that scan rather than probing a frame.
- **Layout-aware probes.** A 2-pixel empty-well check landed in the gap between 2 wells on a dual layout and read "empty" on a good frame. Probe pixels are chosen per segment kind.
- **The deep pass probes 0.20s into a segment, never 0.03s.** After a sped-up chunked pass a cut can sit a frame off, and a 0.03s probe read a title card's last frame as an empty well.

### Privacy on a screen share

- **A screen share is the host's whole screen, and 2 frames do not clear a 2 minute stretch.** A build note said "own tabs only, checked at full res" off 2 frames. The independent review, at full resolution across the whole share, found an address-bar dropdown carrying a private email subject, an analytics dashboard with account identifiers, a logged-in social feed with notification badges, search history, and the tab strip and address bar with full URLs on every frame. **Sample a share at 1 fps at full resolution before the first render, and assume the browser belongs to the presenter.**
- **The repair is data**: a `build/overrides.json` with `freezes` that hold the last clean frame of the page over each private span, and a crop that takes about 110px off the top (menu bar, tab strip, address bar) on a full-frame browser.
- See `content/reference/lessons.md` for the full-resolution frame check and the rebuild-clean rule for workspace surfaces going on camera.

### The process

- **A failure cause is a hypothesis until an artifact proves it** (an exit signal, a log line, the command itself), and **the pipeline's own command gets audited first**. 3 confident misdiagnoses in a row hid a self-inflicted missing output `-t` for 3 days.
- **`build/STATE.md` is the resume point.** Every wake-up, handoff and resume reads it.
- **Benchmark, do not argue.** A throughput change proposed during a deadline render gets a 60 second measurement and an answer in numbers. "4 workers is the limit" was once reasoned from core count; 8 won that time because a subtitle burn is libass-bound, not CPU-bound. On a different load, 4 beat 8. Measure.
- **The deep pass writes a report, and the upload gate reads it.** A report with coverage, checks run and findings; the gate refuses unless green at full coverage and newer than the file. Accepted findings go in `verify-allow.json` with a reason, never quietly loosened. "I ran spot checks and called it a deep pass" then fails structurally: run against a shipped episode, the report's one open finding was a 0.366s A/V drift a person had caught by eye.
- **A deep pass is every-N-second frames across the whole runtime, plus freeze and black detection, plus an A/V drift check.** Never spot samples at boundaries.
- **A claimed check names the artifact it read**: the frames, the report file, the numbers. "Verified frame by frame" with a skip in it is not a check.
- **The end-of-run review is a separate sub-agent that reads the whole conversation**, never the session reviewing itself.
- **A correction lands where the next session will see it, in the same session.** A caption floor once lived in a single episode's script and was wrong again on 12 of 15 renders 3 days later. Copy a fix into the next episode's build and into this file or `content/taste/editing-rules.md`.
