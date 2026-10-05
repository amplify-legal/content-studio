# Editing a podcast episode, end to end: the runbook

> Installed to `content/reference/podcast-edit-runbook.md`. This is the operating manual for the person who edits the episodes (called "the editor" below) and for the Claude session that runs the commands with them. The reasoning behind each rule, and every trap the pipeline has already paid for, lives in `content/reference/podcast-edit.md`. Why long renders die is `content/reference/render-reliability.md`. Read in that order when you want the why.
>
> **The editor does not run any of this by hand.** They open a Claude session in the project, say which episode they are editing, and the session runs the commands. This runbook is what both of them work from, so the editor can tell whether the session is doing the right thing.
>
> **Jargon, translated once.** *Raw* = the untouched camera or track file. *EDL* (edit decision list) = a plain list of which seconds of the raw tape are kept, in what order, in which shot: the cut, written down as numbers. *Segment* or *clip* = one entry in that list, rendered as its own small video file. *Master* = all the clips joined, before captions. *Render* = the machine turning that into a video file, which takes minutes to hours. *ASS* = the subtitle file format the captions are burned from. *Plates* = the name cards under each person. *Deep pass* = the automatic quality check that has to go green before anybody uploads.

---

## 0. Who owns what

| Owner | What they own |
|---|---|
| **The editor** | The whole lane. Getting the tracks out of the recorder, the taste, what stays in, driving the initial cut through the session, the animations, the finish in the NLE (Premiere Pro, or your equivalent), and the derivatives. Watching every output and saying "that is wrong". Closing spare Claude sessions before a render. |
| **The session (Claude)** | Every command in this runbook, every file it writes, the checks, the status reports, proposing the things nobody asked for at the animation and video-AI stage, and saying "hypothesis" out loud when it does not know why something failed. |
| **The creator (the host whose channel it is)** | **One review call per episode.** The editor brings a few opening options and 3 music options to it, and they watch the episode all the way through in that call. The final watch is the first watch: the creator points things out as it plays. |

**What that means in practice.** The creator does not see a version before that call. Nothing is held back for a second pass, because there is no second pass. The cut that arrives has already passed the deep pass and the editor's own review, and the editor comes with options rather than with a question.

**Why one gate and not five.** A pipeline with a review stop after the teaser, after the music, after the rough cut, after the captions and before the upload costs the host 5 sittings and the editor 5 waits. Collapsing them into one call, with options prepared for each open choice, keeps the host's judgment and removes the waiting. Re-evaluate the shape after a few episodes; it is a working agreement, not a law.

**Aerial and b-roll elements are per episode, never standing.** If one episode had drone footage, the aerial rules apply to that episode. They are not carried into a plan for an episode that has no aerial footage.

---

## 0.5 The path a podcast takes

Six stages. The handoff point is named, and it is not the end of the session's job: it is the start of the editor's finish.

| # | Stage | Where | What it means |
|---|---|---|---|
| 1 | Download the tracks | The call recorder, by hand | Most remote-recording tools have no headless pull. The editor downloads and stages the files, then the session runs the transcriber over them. A recorder that exports **one track per participant, already aligned** is the shape to want: the cut becomes one shared timeline where every cut hits every feed. A single camera pointed at 2 people is the exception and needs the single-camera notes in `podcast-edit.md`. |
| 2 | The initial cut | The session | The EDL, the silence policy, the shot grammar, the captions and the deep pass are machine work. This is why the pipeline has to be **generalised** rather than copied per episode: see section 7. |
| 3 | Animations | The session | Anything that assembles on screen is built as an alpha composition (HyperFrames, or your equivalent motion tool) and handed over as a `.mov` with alpha, not rebuilt by hand in the NLE. |
| 4 | Side angles and video AI | The session | On one-camera footage the reliable fix is crops of the wide (singles). A **generated** second angle of a real person is unproven: the first attempt is a test clip the creator sees on its own, never something that arrives welded into an episode. |
| 5 | "Anything I may be missing" | The session | At this stage the session proposes what nobody asked for, 2 or 3 concrete opportunities off this tape with the clip to look at. It is the one point in the pipeline where being unprompted is the instruction. |
| 6 | Final cleanups and manual animations | The NLE | The session hands over. It does not finish. |

**The handover contract.** Every derivative the episode owes (chapters, description timestamps, short in and out points) is re-derived against **the editor's NLE export**, never against the session's master, because the runtimes differ the moment the editor touches it. Build a small `rederive` step into your per-episode pipeline: it takes the export plus one or more `old=new` anchor pairs and maps every timestamp across. Handing the file to the editor is the designed ending, not a fallback, which makes that step load-bearing.

**The objective settles arguments: save the editor time while raising the quality over time.** A step that costs the editor more time than it saves is wrong even when its output is better. A step that saves time by lowering the bar is wrong too.

---

## 1. The 3 machine rules. Break these and you lose a night

| Rule | Why | What it means in practice |
|---|---|---|
| **Close spare Claude sessions before any render.** | With 18 to 20 sessions resident, load average once hit 716, swap 96.8%, and the OS killed the render, which is always the biggest process. An automatic sweep closed **0** of them, because no automatic sweep is allowed to touch interactive sessions. | Only a person can do this. Close them in the app before a long render, and before bed on an overnight run. |
| **Every long render runs detached, never inside the conversation.** | A render started as a child of a chat dies when the chat is interrupted or the session ends. | `scripts/render_detached.sh start <name> --watch <dir> -- "<command>"`, then `scripts/render_detached.sh status <name>` from any session, any time. It gives the job its own session, keeps the machine awake, retries once, writes a status line every 60 seconds, and stops anything that balloons past 4 GB (the runaway-tail shape). |
| **While a render is running, nothing gets killed. Period.** | Paid for twice in one day: an out-of-memory kill took a 4 hour render at 98%, then a memory-freeing sweep killed the rerun at 95%. A forked session keeps the *original* process, so a process's age tells you nothing about what it currently owns. | If the machine must be thinned mid-render: pause file sync, close browsers. Never a Claude process, never an ffmpeg. Never start a second heavy job (thumbnails, image generation, browser automation) against a live render. |

**"Is it working?" has exactly one answer: is the output file growing.** Never the CPU meter, never a spinner, never a guess.

```bash
scripts/render_status.sh content/videos/<episode>/build      # is the file growing
scripts/render_detached.sh status <name>                     # running / finished / died
scripts/render_detached.sh tail <name>                       # last 40 log lines
```

**Overnight, more than one video:** `scripts/render_queue.sh add <name> --watch <dir> -- <command>` for each, close your sessions, then `scripts/render_queue.sh run`. It runs them one at a time behind `scripts/render_preflight.sh` (25 GB free disk, ffmpeg present, and a lint that no pipeline script has a looping image without a time limit) and a memory gate that refuses to start into a swapping machine. `scripts/render_queue.sh status` in the morning.

---

## 2. The taste rules that have already rejected a cut

These are the house defaults a working pipeline converged on. They are starting points: your host's own calls go in `content/taste/editing-rules.md` and win over anything here.

**The cut**
- Joint-silence gaps of 1.0s or more tighten to about 0.6s. **Never leave a kept sliver shorter than 1.2s between 2 cuts** (the machine-gun guard). Laughs sit inside protected no-cut zones. This combination is the thing a host named as worth replicating: clean cuts that skip the long thinking moments and keep the flow going.
- Filler words stay in the audio (chasing every "um" in a 2-shot makes visible jump cuts). Captions drop standalone uh and um.
- False starts and stutter runs cut on word boundaries from the word-level transcript, and **every boundary is machine-checked**, because words that get cut off, and words that run a little long, are the first thing a host hears.
- Post-show tape is a quarry, not garbage: an outro insert and a sign-off have both come from after "we'll edit this part out".
- Content trims prefer list-like litanies over stories. A trim that breaks a sentence's weave does not happen for a few seconds' gain.

**The opening**
- The pre-episode open is a **trailer**, not a teaser: more impactful, more "I should definitely stay for this". Micro-clips of 1 to 5 seconds, hard cuts, 30 to 40 seconds total.
- Nobody introduces themselves inside the trailer.
- **Any structural change to an opening is read back to the host as a table and confirmed, then a 60 second opening preview goes to them before the full chain runs.** A promise to "ask at the end" is a question that blocks the build: a version rendered on a guess gets thrown out.
- **The editor brings a few opening options to the review call, not one version.** The trailer is still built and watched as its own file before it is welded to the episode.

**The coming-up section, and the 2 faults that make one feel awkward**

| Fault | What to do differently |
|---|---|
| **Half-second lingering silences** | The body's gap policy is too loose for a montage of 1 to 5 second clips: a 0.6s tail on a 3s clip is a fifth of it. **Inside the trailer and the coming-up, a clip ends on the last word's decay, not on a policy gap**, and any residual tail over about 0.15s is trimmed. The body policy (1.0s tightens to 0.6s) is unchanged. |
| **The choice of clips** | The pick list is the other half, not just the assembly. **Trailer candidates go to the host as clips before they are assembled**, the same standalone treatment the assembled trailer already gets. |

**Shots (single camera)**
- A shot grammar that worked on one wide 2-shot: the wide at a 1.35x punch-in as the base, one single at 2.5x (head and shoulders), the other at 2x (chest up), and once both people settle, the wide dominates with singles sprinkled by feel. Your zoom levels are a property of your framing; measure them on your own tape.
- **The leg problem is a pose problem.** With crossed legs the knees sit centre-frame, so a symmetric punch-in makes legs bigger, not smaller. Singles are the fix, and they double as the missing second angle on one-camera footage. Judge reframing on the frame where both people have their legs crossed: that is the resting composition, not a gesture frame.
- **Transitions are worked through with the host, never dropped on them as a batch.** 3 to 4 treatments per cut pair, rendered on real footage, and they react to clips. No transition vocabulary goes into a rule before the host has watched one.

**Audio**
- Every track mixed with `normalize=0`, 30ms fades at every segment edge, loudness normalised to -14 LUFS at the very end (`loudnorm=I=-14:TP=-1.5:LRA=11`).
- A phone or room recording is often one mic bus, mono in both channels, and it booms. The chain that fixed one: `adeclip,highpass=f=120:poles=2,lowshelf=f=220:g=-5,afftdn=nr=8:nf=-34,alimiter=limit=0.95`, then loudnorm.
- **Music comes from a licensed library, never generated.** The editor brings 3 options to the review call and the host picks.
- **The music bed sits clearly under the speech, and the gap is measured, not judged by ear on laptop speakers.** A bed at 6 to 7 dB under the voices was called "way too loud"; about 19 to 20 dB under was right. Measure bed against voice in the same window and say the number before a render is shown.
- A secondary feed (a phone livestream, a room mic) often sits about 12 dB under the main mix. Lift it to roughly 6 dB under, and err toward lower volume.

**The finish**
- A conversational episode can ship sped up slightly with pitch preserved (1.1x is a house value that worked). **Captions burn before the speed pass** so they stay in sync.
- A resource the episode promises on tape is shown **on screen** as an animation (step one appears, then step two), not just linked.
- **On-screen text that quotes the tape names its transcript line and timestamp at the top of its build prompt.** One walkthrough animation was built from the wrong passage of the tape and cost a re-render.
- **Never upload before the host has seen the file**, even under an explicit end-to-end autonomous mandate. The review call is where they see it.
- **Every derivative inherits the episode's audio chain.** Every short, reel and clip runs the episode's own chain before the speed pass, or reproduces it exactly. 3 rounds of shorts once shipped with raw camera audio because the chain lived only inside one episode's render script, so **write each episode's chain down where a shorts session will find it**.

---

## 3. Captions: the rules

| Rule | Detail |
|---|---|
| Style | Uppercase bold sans (`{BRAND_FONT_CAPTION}` from `content/brand.md`), current word highlighted in `{BRAND_ACCENT}`, **no scale pop** on a long episode, about 62px on a 1920x1080 frame. A pop that suits a style demo jumps at the viewer across 30 minutes. |
| Highlighting | Per-word highlight renders in **one libass pass** (pure ASS karaoke events). Never frame by frame in Python: that path took hours to render. |
| Pin the base colour | Every word's override starts with its base colour (`\1c&H00FFFFFF`) **before** the transitions, or libass resolves the first transition's target for any time before its start and the highlight runs backwards. |
| Layout | 3 to 4 words a group, one line at a time, each group replacing the last. **No group ever wraps to a second line stacked above the previous one.** |
| Below the mouths | **The caption block never crosses a speaker's mouth** on any layout. Check a full-resolution frame of each speaker talking before a render ships. The name cards give way to the captions: they go lower and may overlap the frame edge. The captions do not move up to make room for the cards. |
| Word gap | **The visible gap between words is measured as libass draws it.** A per-word layout must add the style's per-letter spacing and both outlines to the measured advance, or the visible gap shrinks to about 7px and a line reads as one run-on word. About 26px visible worked. A group wider than about 1500px on a 1920 frame goes out as 2 caption frames, never squeezed. |
| Sizing calibration | libass can render a font at a different size than PIL measures it (0.63x was measured for one bold sans). Calibrate once per font; if captions come out small and gappy, that is the number that moved. |
| Format trap | The ASS header `Format:` line must declare all 10 Dialogue fields, or margins render as literal text on screen. |
| Proper nouns | Every capitalised token, domain and organisation name is pulled out of the caption file and checked against the guest's real assets (their site, their bio) **before the burn**, while fixing is free. A misheard word and a missing letter in a domain have both shipped burned in. Keep the verified names in a `known_nouns.txt` beside the build as the audit trail. |
| The all-caps hole | A proper-noun checker flags nothing in an all-caps style, so **a human spot-reads the intro captions every time.** A host's own name once reached a v1 as two unrelated words. |
| Corrections | Word fixes and timestamped overrides live in a per-episode fix list; a token the transcriber splits in two is merged by a small post-pass. Both are per-episode data (section 7). |
| Engine | **ElevenLabs Scribe `scribe_v2` is the default, Deepgram `nova-3` is the declared fallback, and local whisper is last resort** for no network and no key. The engine that ran is named in the output file's own header, never a silent default. If the Scribe key is missing, the session says so **before the first burn**, not after the host's ear finds the mistake. |
| Size on a vertical clip | **78px in a 1080-wide frame, never below it**, judged at 375px phone width, never at preview size. On shorts the caption block also ends at or above 78% of frame height (see `content/taste/shorts-formats.md`). **A corpus finding never overrides a floor the host set**: 2 independent review passes once recommended shrinking and were both wrong. The 62px above is the horizontal episode; this is the vertical derivative. |

---

## 4. Plates (the name cards): the rules

| Rule | Detail |
|---|---|
| When they are on | **On from the intro through roughly the first minute of conversation, off for the body, back on for the goodbye.** |
| How it is carried | Every segment in the EDL carries a `plates` true/false flag, and the clip cache key carries a suffix (for example `_np`) for the no-plates version, so both states can exist side by side without one overwriting the other. |
| The wordmark | If the show has a wordmark, it sits in a fixed band from the very first frame. Decide this once per show and write it in `content/brand.md`. |
| Entrances | Plates animate in at the intro with a quick stagger, the guest's plate firing as their name is spoken. No plates during the trailer. |
| Position | Plates sit below the caption block; see "Below the mouths" in section 3. |
| The check that matters | **Assert the frame before spending the hours.** The first plated segment renders alone and its frame 0 is compared against the real plate and wordmark assets, pixel for pixel, before the rest of the run starts. A "busy pixels" heuristic is not this check: the video behind a missing plate is plenty busy. One version rendered 13 hours overnight and was rejected in the first minute, on the frame. |

---

## 5. The pipeline, step by step

Everything lives under one folder per episode: `content/videos/<episode>/`, with `raw/` (the untouched files), `build/` (the scripts and everything they produce) and `renders/` (the files people watch). **Never work in a synced or mirrored copy of the project.** A worked pipeline of the same shape, for a recorded workshop, is in the repo at `examples/workshop-edit/`; start a podcast build from its structure.

### The state file is the resume point

`build/STATE.md` is written by the pipeline after every stage: stage, status, artifact, next command. **A session that wakes up, resumes, or takes a handoff reads that file, never a runbook from memory.** On one morning somebody typed the pipeline's steps by hand and it replayed stages that had already finished.

### The steps

| # | Step | Owner | What runs | It produces | Working looks like | When it fails |
|---|---|---|---|---|---|---|
| 0 | Open the session | Editor | Say which episode you are editing | A session that knows the episode | It names the episode and the last state | Point it at `build/STATE.md` and `content/reference/podcast-edit.md` |
| 1 | Stage the tracks | Editor | Download the participant tracks by hand and copy them into `raw/`, plus the music bed and any extra source. One file per speaker, named by role and height (`host-720p.mp4`, `guest-360p.mp4`) | `raw/` holding every source | `ffprobe` on each file reports the duration and resolution you expect, and the tracks are the same length | If the recorder has no download API, this is always a manual step. That is fine. |
| 2 | Transcribe, word level | Session | `python3 .claude/skills/shorts-editor/scripts/transcribe.py raw/<track> --edit-dir build --keyterms-file build/keyterms.txt`. Fallback: `transcribe_deepgram.py` with the same `--keyterms-file`, then `transcribe_local.py` last | `build/transcripts/<track>.json` | Every word carries its own start time; Scribe also returns speaker ids | Missing key: say so before the first burn. A mushy passage: re-transcribe that window alone and merge it, **copying the transcript first** because a merge that overwrites in place has no undo. The transcriber caches on the filename: a re-run with a new key-terms list needs `--force`. |
| 3 | Build the assets | Session | The episode's asset script | Name plates and their entrance frames, the title card, the end card, the frame overlay, any on-screen document, in `build/assets/` | The plate PNGs show the right names, roles and sides | A wrong name or side is a literal in the script (section 7): fix and re-run |
| 4 | Chapter chips | Session | The chips script | One chip image per chapter plus `chapters.json` | Labels readable | Chapter times written in 2 places drift apart. Keep them in one file the EDL also reads. |
| 5 | Write the cut (the EDL) | Editor decides, session writes | The EDL script | `build/edl.json`: every kept span, its shot, its plates flag, the total body duration | The printed total matches the runtime you expect | Silence gaps and slivers are policy (1.0s to 0.6s, never under 1.2s). Boundaries are snapped to measured audio and checked, never trusted from the transcript alone. |
| 6 | The trailer, on its own | Editor + host | Render the trailer segment alone | `build/trailer/trailer-vN.mp4` | 30 to 40 seconds, and the host has seen it as a file | **Never weld an unapproved trailer to a long render.** 3 passes shipped "a bit awkward" because the trailer was only ever seen inside the episode. |
| 7 | Render the segments | Session, detached | `scripts/render_detached.sh start <ep>-segments --watch content/videos/<ep>/build -- "python3 content/videos/<ep>/build/render_segments.py"` | `build/clips/*.mp4`, then `build/master-nosubs.mp4` | One probe segment renders first and its frame 0 is asserted against the real plate assets, then the pool runs; the master duration matches the expected one within a second | A clip already on disk is skipped (the cache is content-keyed), so a retry only redoes what is missing. If the master is short, one clip failed: look for the missing name in `clips/`. |
| 8 | Captions | Session | The captions script, then the split-token post-pass | `build/captions.ass` | Line count looks right for the runtime; groups are 3 to 4 words | Anything not handled by the post-pass is a per-episode fix list |
| 9 | Verify the captions | Editor | Spot-read the intro captions against the tape; check every proper noun and URL | A caption file somebody has actually read | Names, companies and domains spelled the way the guest spells them | This is the step that catches what the checkers structurally cannot see |
| 10 | Finalise | Session, detached | Chunked caption burn, chapter chips, the speed pass, then the audio rebuilt sample-exact with the music bed, then the deep pass, all as one detached chain | `renders/final-vN.mp4` | The log prints the chunk bounds, the final duration against the expected one, the chapter list, the music bed timing, and the 2 stream durations agreeing within a frame or 2 | Make sure the file you ship is the one the last step of the chain names. Two scripts disagreeing on the output filename has shipped the wrong file before. |
| 11 | The deep pass | Session | The review script (last command of step 10) | `build/verify/deep-pass-report.json` plus contact sheets | `"status": "green"`, coverage 99.9% or better, `open_findings: []` | See the table below |
| 12 | The upload gate | Session | The review script in gate mode | A refusal or an allowance | It prints "upload allowed" | It refuses on anything but a green report at full coverage, and the report must be newer than the file |
| 13 | Animations and video AI | Session | Alpha compositions for anything that assembles on screen; a generated side angle only as a standalone test | `.mov` files with alpha, staged in `build/assets/` | Renders locally | A generated angle goes to the host as its own clip first |
| 14 | What nobody asked for | Session | Propose it | 2 or 3 concrete opportunities with the clip to look at | | The one step where being unprompted is the instruction |
| 15 | Independent review | Session (a **sub-agent**) | Spawn a separate reviewer that reads the whole conversation and watches the file | A second opinion | It watched the file, not the log | Never the session reviewing itself |
| 16 | Into the NLE | Editor | Final cleanups and manual animations | The shipping cut | | The designed ending, not a fallback |
| 17 | Re-derive against the export | Session | The `rederive` step with `--file <export> --anchor old=new` | Chapters, description timestamps and short in/out points on the export's runtime | Chapter times match the editor's cut | Deriving from the session's master after the editor touched it is a bug |
| 18 | The review call | Editor + host | Bring the opening options and 3 music options; watch it through together | The host's picks and notes | They have seen the whole thing | This is their first and only watch |
| 19 | Close the day | Editor | Write the work log and commit by explicit path | A record the next session reads | The next session picks up where you left off | |

### What the deep pass actually checks

Not spot samples. A host once named the difference exactly: a full dive into the video, not a mechanical pass.

| Check | What it catches |
|---|---|
| duration | The finished file against the EDL's own arithmetic, within 2 seconds |
| av_drift | Video and audio stream lengths disagreeing by more than 0.10s (a 0.366s lip-sync drift shipped once before this existed) |
| freeze / black detect | A frozen or black stretch that is not a designed card |
| silence over 2s | Dead air that is not a designed silent card |
| empty first frames | A segment that starts before the video has decoded. Probed **0.20s in, never 0.03s**, with pixels chosen per layout |
| frame sweep | A frame every 5 seconds across the **whole** runtime, checked for near-black, with coverage reported as a percentage |

**Accepted findings** (a document takeover freezing by design, an end card being dark and silent) live in `build/verify-allow.json` with a written reason each. Never loosen a threshold quietly; add an allow entry with its why, or fix the video. `scripts/verify_loop.py` and `content/reference/verify-loop.md` describe how to run this check and its safe repairs as an overnight loop.

### When the deep pass or the render goes wrong

| Symptom | What it means | What to do |
|---|---|---|
| `status: red`, findings listed | A real finding | Read them; each names a timestamp. Fix the cut or the asset, re-render, re-run |
| `status: red`, findings empty | Coverage fell below 99.9%: the sweep did not reach the end of the file | Re-run the review. If it persists, the file is shorter than the EDL expects: a chunk was cut short |
| The chain exits 1 and the detached runner retries the whole thing | The deep pass is the last command, so a red report fails the chain | Expected. Read the report, not the exit code |
| A render sits at "98%" for hours, then dies | The **runaway tail**: a still image fed with `-loop 1` never ends, so ffmpeg encodes duplicate frames forever. The log tell is "More than 100000 frames duplicated" | Every command with a looped image needs an explicit output `-t`. `scripts/render_preflight.sh` lints for it. Salvage: interrupt with SIGINT (never SIGKILL); the file closes valid and the good head trims out cheaply |
| Hours, no output, huge memory number | The **framesync stall**: a finite image sequence overlaid on a stream at a different frame rate | Never overlay finite image sequences. Composite animations frame by frame in Python and bake them into the segment |
| Instant, silent death, no error | The render was a child of the conversation | Restart it through `render_detached.sh` |
| A segment at 0% CPU for minutes | A deadlock, not a slow render. The first suspect is the input window: audio running out exactly where `apad` begins never flushes | Give the input window 1 second of slack, run every ffmpeg with `-nostdin`, bound each segment's wait (60s plus 3x its duration) with one retry |
| Load average through the roof, swap over 80% | Too many sessions | Close sessions yourself, restart the render |
| A step exits 127 | `timeout` does not exist on macOS | `perl -e "alarm N; exec @ARGV"` is the portable version |
| A check fails on a file you can see is fine | **The check is wrong.** Two real ones: a 0.03s probe reading a title card's last frame as empty, and a 2-pixel probe landing in the gap between 2 layout regions | Fix the check, do not accept the finding |

**And the rule under all of them: a failure cause is a hypothesis until an artifact proves it, and your own command gets audited first.** 3 confident misdiagnoses in a row once hid a self-inflicted missing flag for 3 days, with the machine's owner closing browsers and blaming their own hardware. Say "hypothesis" out loud until it reproduces.

---

## 6. Numbers worth knowing before you plan a day

Measured on one machine. Yours will differ; the point is to measure.

| Thing | Measured |
|---|---|
| Full finalise of a 21 minute master, clear machine | About 10 minutes at 4 parallel chunks |
| The same job on a loaded machine | About 25 minutes |
| Parallel width | **4 beat 8** on that machine (2.12x realtime against 1.25x). An earlier "8 is faster" measurement was taken under a different load |
| Monolithic single-pass finalise | 997 seconds, peak memory 851 MB: it does not hang on its own |
| Disk needed | 25 GB free, checked by preflight |

**Benchmark, do not argue.** A throughput question gets a 60 second measurement at each width and an answer in numbers inside 2 minutes. Build a `--bench 4,8` flag into your finalise script.

---

## 7. Generalise the pipeline, and know its tape-specific surface

There are 2 recording shapes and they want different base pipelines:

| | One aligned track per participant | One camera on 2 people |
|---|---|---|
| **The cut** | One shared timeline, every cut hits every feed | A single wide reframed into singles, because there is no second angle |
| **Naming** | Keep the scripts generically named (`build_edl.py`, `render_segments.py`, `captions.py`) | Same. Never suffix scripts with an episode or guest name |
| **Shape of a future podcast** | **This one**, if your recorder exports tracks | The exception, kept for its single-camera reframing work |

### The reusable components every podcast build needs

None of these is tape-specific. Build them once and copy them forward.

| Component | What it does |
|---|---|
| A pipeline-state module | Writes `STATE.md` after every stage (where the pipeline is, what it left, the exact next command) plus a status writer that answers "is it working". |
| A review script with a gate mode | The deep pass. Writes `verify/deep-pass-report.json` and refuses the upload on anything but green at full coverage. |
| A proper-noun checker | The noun and URL pass over the ASS **before** the burn. |
| A `rederive` script | Chapters, description timestamps and short in and out points re-derived against a re-cut file. |
| A karaoke caption builder | Per-word highlight as pure ASS karaoke, one libass pass. |
| A chunked parallel finalise | Chunk bounds rounded onto the output frame grid, measured on the real master. |

### The tape-specific surface: keep it small and in one place

Everything that is a property of this tape goes in one per-episode config file, never scattered as literals. The list a working pipeline found when it was generalised:

| # | What | Why it is per tape |
|---|---|---|
| 1 | **The track names** | Written in 3 files they drift; write them once |
| 2 | **The crops** for each person | Properties of how each person framed themselves on their own camera |
| 3 | **The key-terms list** (names on this tape) | Goes into the transcriber; see `podcast-edit.md` |
| 4 | **The spans**, and any out-of-order insert | The cut itself |
| 5 | Plate names and roles | Data, not code; the plate-drawing function stays generic |
| 6 | The accepted deep-pass findings | `verify-allow.json`, per episode |

**The single-camera shape had a much longer list**, and the shape of that list is the warning: hand-written spans carrying the shot choice as prose notes; 4 crops that were properties of where 2 people sat; source filenames hard-coded in 4 scripts; guest identity used as an enum value across every script; and 2 scripts disagreeing on the output filename so a human bridged them. Also: branches keyed off English prose in a note field instead of a structured flag, the speed factor written 7 times, chapter boundaries duplicated by hand between 2 files, and a segment-kind list that silently omitted 4 kinds so a chapter chip could not land in them. **Every one of those is a structured field in a config, read by every script.**

**What stays the same across episodes** (format level, not episode level): the frame geometry and well positions, brand colours and fonts, plate entrance timing, the caption style block (baseline, size, calibration, gap, max words), the encode parameters, the gap policy (1.0 to 0.6, sliver floor 1.2), `loudnorm I=-14:TP=-1.5:LRA=11`, the speed pass itself, chip typography and position, every deep-pass threshold, the memory-aware worker widths, and the 2 hard-won ffmpeg rules: an explicit output `-t` on every looped-image graph, and chunk bounds rounded onto the output frame grid.

---

## 8. When something is not in here

Ask in the session, then **write the answer into this file or into `content/reference/podcast-edit.md` in the same session**, and the host's taste calls into `content/taste/editing-rules.md`. Every rule in these files exists because somebody lost hours to it once. A rule that keeps getting broken becomes a script or a check, not a longer paragraph.
