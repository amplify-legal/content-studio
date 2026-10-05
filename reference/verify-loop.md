# The verify loop

> A render that checks itself, repairs what it safely can, and wakes a model only for what it cannot settle. Built for overnight runs.
>
> **The loop runner ships: `scripts/verify_loop.py`.** The 4 build files it drives are yours to write against your own pipeline, because what counts as a defect and what counts as a safe repair is specific to your show. `--scaffold` writes stubs that satisfy the contract, and `--selftest` proves the loop's 3 outcomes offline. What the runner never does is invent a check or a repair you did not write.
>
> The ask it came from: *"these edits should have a loop where they can verify themselves until the work is properly fully done. There's a massive advantage to leveraging these on overnight runs, such that we don't burn through too many tokens, but we leverage the time we have for computer time on the renders."*

---

## The economics, which are the whole design

Overnight, machine time is free and abundant. Tokens are neither. Every decision below falls out of that one sentence.

| The thing | Machine time | Token cost |
|---|---|---|
| A render | 15 minutes | ~200 |
| A check battery | 4 minutes | 0 |
| A model reading a night of ffmpeg logs to work out what went wrong | minutes | ~80,000, and usually wrong anyway |

So: **the checking is a script. Most of the repairing is a script. A model is woken only for what the script genuinely cannot settle, and is handed a verdict small enough to read in a few thousand tokens.**

---

## The 3 tiers

**A finding names its own tier and the loop never promotes one.** This is the rule the whole design rests on.

| Tier | Who settles it | Cost | Examples |
|---|---|---|---|
| `auto` | The bounded repair table | Machine time, zero tokens | Loudness missed its target. 2 captions overlap. A caption sits over a card. A caption is too short to read |
| `model` | A woken session reading the verdict | A few thousand tokens | The captions drift against the finished audio. A word is clipped at a join. Black frames outside a card. The duration disagrees with the edit list |
| `human` | The operator, on the morning queue | Their attention | Does this join sound right. Is the title right. Does that segment belong at all |

**A loop that lets one tier pretend to be another is worse than no loop.** A script that guesses at taste ships something wrong with great confidence, at 3am, with nobody watching.

---

## The 4-file convention

Convention over configuration, because somebody who is not the author has to be able to use it. Point the loop at a piece's folder and it expects `build/` to hold exactly 4 files:

| File | What it owns |
|---|---|
| `build_cut.py` | The edit list, the segment renders, the concat, the caption file |
| `finalize.py` | The caption burn and the audio |
| `verify.py` | The check battery. Writes a verdict as JSON |
| `autofix.py` | The bounded repair table. Writes `overrides.json` |

```bash
python3 scripts/verify_loop.py content/videos/<slug> --scaffold          # stubs, never overwrites
python3 scripts/verify_loop.py content/videos/<slug> --max-iterations 4 --deep --deadline 07:00
python3 scripts/verify_loop.py content/videos/<slug> --status            # the state file
python3 scripts/verify_loop.py --selftest                                # offline proof
```

Any folder carrying those 4 files self-checks its own render. That is the entire contract. Run it detached for a real night: `scripts/render_detached.sh start loop-<slug> --watch content/videos/<slug>/raw/edit -- "python3 scripts/verify_loop.py content/videos/<slug> --deep --deadline 07:00"`.

### What each file has to do

| File | Contract |
|---|---|
| `build_cut.py` | Exit 0 on success. **Never rewrite unchanged output** (write to a temp file, replace only when the bytes differ), or the freshness check below lies |
| `finalize.py` | Write the finished `.mp4` into the edit dir (default `raw/edit/`, change with `--edit-dir`). Read loudness and quality repairs from `build/overrides.json` |
| `verify.py` | Accept `--iteration N` and `--deep`. Write `<edit-dir>/verify/verdict.json` |
| `autofix.py` | Expose `apply(findings, iteration)` returning `(widest rebuild scope or None, [what changed])`, and `prepare_rebuild(scope)` returning the list of files it removed |

The verdict, which is the only thing the loop reads from `verify.py`:

```json
{
  "status": "red",
  "tiers": {"auto": 1, "model": 1, "human": 0},
  "loudness_lufs": -16.4,
  "findings": [
    {"check": "loudness", "tier": "auto", "detail": "-16.4 LUFS against -14",
     "fix": "reloudnorm", "args": {"measured_i": -16.4}, "rebuild": "burn"},
    {"check": "av_drift", "tier": "model", "detail": "0.114s between streams",
     "rebuild": "segments+burn"}
  ]
}
```

The loop moves the previous verdict aside before each verify, so a stale verdict from the last iteration can never pass for this one.

### The state a waking session reads

Everything lives in `<edit-dir>/verify/`, and it is deliberately small:

| File | What it holds |
|---|---|
| `loop-state.json` | Every iteration's timings, tiers, repairs and rebuild scope, plus the outcome (`green`, `escalated`, `build_failed`, `verify_failed`, `deadline`, `iterations_exhausted`) and 2 short lists: `for_the_model` and `for_the_human` |
| `verdict.json` | The last battery's findings |
| `loop.log` | The full trail, for when the 2 files above are not enough |

A session woken in the morning reads `loop-state.json` and the verdict, a few thousand tokens, and nothing else unless something is genuinely unclear. Exit 0 means green, 1 means anything else.

---

## Repairs are data, never code

Every repair the loop applies lands in `build/overrides.json` **as data**. 3 reasons, all load-bearing:

1. A person can read exactly what a night of unattended looping changed, in one small file, without reading a log.
2. Deleting that file returns the cut to what the code says it should be.
3. **A loop that edits its own generator is a loop nobody can review in the morning.**

**A repair that turns out to be an invariant gets promoted into the generator and out of the override table.** The loop once recorded a clamp for 2 captions overlapping a card, but "no caption touches a card" is true of every episode of that show, so it became a rule in the generator and the override died. Overrides are for per-instance repairs only.

**An override keyed on an index is only valid for the transcript that produced it.** Re-transcribing one episode moved the caption count from 520 to 517, so every index-keyed repair the loop had recorded silently pointed at a different line. Nothing broke that time, only because the one repair that mattered had already been promoted into the generator. Which is the second reason to prefer promotion.

---

### A starting repair table

The bounded table one show ran with. Every entry is deterministic, capped, and recorded in `overrides.json`. Anything needing judgment is not in it, by design.

| Fix | What it records | Bound | Rebuild |
|---|---|---|---|
| `reloudnorm` | A two-pass loudnorm fed the measured figures, so the second pass lands on target instead of guessing again | Once per measurement | `burn` |
| `raise_crf` | The encoder CRF up 3 at a time | Stops at 23, where a webcam source starts showing blocking on flat walls | `burn` |
| `drop_caption` | One caption index dropped (a caption shorter than readable, a duplicate) | Per index | `captions+burn` |
| `clamp_caption` | One caption index clamped off a card it bleeds onto | Per index | `captions+burn` |
| `nudge_boundary` | A request to move a cut point | 400ms, and escalates instead of applying | `segments+burn` |

Every fix carries a budget: the same fix with the same arguments is applied at most 3 times. A 4th failure escalates that finding to `model` with the reason written into its detail. That is the only way a tier ever changes: upward, toward more judgment. Nothing a script finds is ever settled below the tier it named.

## Rebuild only what changed

The other half of the economy. Every finding carries a `rebuild` scope, and the loop deletes only what that scope names.

| Scope | What gets redone | Roughly |
|---|---|---|
| `burn` | The final encode | 1 pass |
| `captions+burn` | The caption file, then the final encode | 1 pass |
| `segments+burn` | Every segment, the concat, then the final encode | 2 passes, and the slow one |

Rebuilding everything every iteration is how a self-healing loop eats a whole night and finishes one round.

The same applies to the loop's own first iteration: if the finished file is already newer than the master, the captions and the overrides, skip the render. That case is the common one, because a detached render usually made the file minutes earlier, and burning it again is a whole pass spent arriving at the same bytes.

---

## The check that only an overnight run can afford

Re-transcribe the **finished file** and hold the burned captions against it. One call, about 40 seconds, and it needs a transcription key (see the note at the bottom).

**Name the engine that produced the check, in what the check prints.** A deep check run on a weaker engine than the one that made the captions reports differences that are the checker's fault, not the cut's. The order that measured best: a word-level commercial engine with a keyterms list first, a second commercial engine with the same keyterms list as the declared fallback, and a local model only with no network and no key. Wire the fallback deliberately; a deep check that silently fails when credits run out is worse than one that says it did not run.

Every other check reads the cut against its own arithmetic, which means none of them can catch a caption remap that is consistently wrong: the edit list and the captions agree with each other, and both are wrong. The deep check is the only one that reads what actually came out.

**This pattern generalises far beyond video, and it is probably the biggest idea in this file. Verify the artifact by reading it back fresh, rather than by re-checking the inputs that made it.**

A report could be verified by re-reading what was actually sent. A set of books could be verified by re-reading the statements rather than the parsed rows. A carousel could be verified by reading the text back off the rendered image. **Every one of those is a class of error the current checks are structurally blind to**, for exactly the same reason.

---

## The guards

| Guard | Value | Why |
|---|---|---|
| Memory gate | Waits up to 15 minutes for 20 percent free memory (the OS's own figure: macOS `memory_pressure`, Linux `MemAvailable`), then goes anyway. `--no-gate` skips it, `VERIFY_LOOP_MEMORY_WAIT_MAX` changes the wait | A render started into a thrashing machine takes all night. One 15-minute encode took 30 under load. Free pages alone is the wrong reading: it once said 66MB free while the OS said 56 percent free, so a gate built on it is a stopwatch |
| Repair budget | The same repair is never applied a fourth time | If 3 attempts have not fixed it, the repair is wrong. Escalate instead of looping on it all night |
| Boundary nudge | 400ms maximum, and deliberately not wired | Moving a cut point changes what the audience hears. Designed as an auto repair, shipped as an escalation |
| Iterations and deadline | `--max-iterations 4` and `--deadline HH:MM`, either one stops it | A loop with no ceiling is a loop that renders until morning |

**Every number in that table is a guess.** Not one was derived from data. Say so, and derive them from your own render history when you have one.

---

## What green does not mean

**Green is not done.**

Green means the file is now worth the operator's time to watch. Done is them having watched it. The loop exists to stop wasting their watches on files with a fixable defect in them, never to replace the watch.

---

## What the first real run found

Worth keeping, because it is the argument for the whole thing. The battery ran once and returned 5 auto findings and 1 for the model. 3 of them were real defects nobody had noticed.

| Finding | What it was | Would a person have caught it? |
|---|---|---|
| Loudness | Landed at -16.4 LUFS against a -14 target, out by 2.4 dB | No. Nothing measures it. It just plays quiet |
| Oversized | 5.33 Mbps against a 3.78 Mbps source, a 600 MB file for a webcam tape | Only when the upload took an hour |
| Caption over card | 2 captions bled 0.02s and 0.14s onto a card that show never puts captions on | Almost certainly not |
| A/V drift | 0.114s between the streams, escalated to the model | Not until somebody said the end looked dubbed |

The drift one is the case the deep check exists for. Diagnosing it meant measuring word positions in the finished file against the captions, bucketed across the runtime: **flat at +0.220s for 850 seconds, then a step to +0.324s.** Steps at the joins, not drift within them. Probing each clip proved it: every clip's audio ran 40 to 75 ms shorter than its video, and a stream-copy concat carries that forward once per join. By the end the audio was about a third of a second behind the picture.

**None of the arithmetic checks could have found it.** The edit list and the captions agreed with each other and both were right. Only reading the artifact back showed it.

---

## Standing rules

- **Repairs are data in `overrides.json`, never edits to a build script.** A night of unattended looping has to be readable in one small file.
- **A finding names its tier and the loop never promotes one.** Taste is never settled by a script, or by a woken model working alone.
- **Every finding carries a rebuild scope**, and the loop deletes only what that scope names.
- **The loop stops rather than repeating a repair a fourth time.**
- **A repair that is true for every run gets promoted into the generator** and out of the override table.
- **A build step never rewrites unchanged output**, or every freshness check downstream of it lies.
- **Fix a transcription at transcription time, not downstream.** Bias the transcriber with the piece's own list of names and terms, rather than find-and-replacing afterwards. Measured on one tape: the plain model heard a guest's name 2 different wrong ways across 2 versions; the same model with a keyterms list heard it correctly. And if your transcription caches on the filename, a pipeline that rewrites the same name needs a force flag or it will serve you the old wrong transcript forever.
- **An override keyed on an index is only valid for the transcript that produced it.** Invalidate index-keyed repairs whenever the transcript changes.
- **Close what you can spare before an overnight run.** An overnight loop is worth nothing on a thrashing machine, and closing interactive sessions is a human step that belongs in the evening.
- **Green is not done.** A script repairs only what is in its bounded table, a woken model handles what the script cannot, and taste stays the operator's.

---

## The open questions, stated honestly

Ship these as open rather than pretending the design is finished.

**Which taste judgments have a machinable proxy?** The battery checks arithmetic, levels and alignment. It cannot check whether a join sounds abrupt, whether a card reads at a glance, whether the pacing is theirs. Some of that might have a proxy worth testing: the pitch and energy discontinuity across a splice, a caption that outruns its shot, a shot held longer than that show ever holds one, a card failing a contrast threshold. **The question is not whether these are measurable. It is whether they correlate with what the operator actually calls wrong**, and that is answerable from history if you have been capturing cut feedback as labelled examples. Most people have and have never used it as one.

**The escalation tier is designed and untested.** 2 shapes are possible and nobody has compared them: a loop in dynamic mode where a session wakes on its own schedule and reads the loop state, or a callback where the script triggers a session at the moment it escalates. The second wastes nothing and the first survives a script that dies. Measure the real token cost of a wake before choosing.

**Which lane pays first.** A one-off cut proves the idea. The real payoff is a show that renders every week, run by somebody who is not going to read an ffmpeg log. The 4-file convention was chosen for that person.

**Needs a key.** The deep check re-transcribes the finished file, which needs a transcription API key. Word-level timings on the commercial services are cheap per hour of audio (check the provider's pricing page), and there is a free local path (a local whisper model) that is slower and looser on word boundaries. The loop runs without the deep check, and loses the one check that reads the artifact back. Say which path you are on rather than letting it be a silent default.
