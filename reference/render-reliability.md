# Why long renders never finish, and what fixes each cause

> Read before any render longer than about 10 minutes. Every cause below actually happened on a real pipeline, with the symptom that made it hard to diagnose. A single vertical short, 2 to 5 minutes of rendering, rarely meets any of these. A 40 minute episode meets them all.
>
> Tools: `scripts/render_detached.sh`, `scripts/render_queue.sh`, `scripts/render_preflight.sh`, `scripts/render_status.sh`, `scripts/render_soak.sh`. Companion: `content/reference/verify-loop.md` for a render that checks itself.

8 things kill a long render. 7 have fixes you can apply today. The last one is the machine itself, and only a person can fix it.

---

## 1. The runaway tail

**What it is.** A still image fed to ffmpeg with `-loop 1` never ends. When the video underneath finishes, ffmpeg keeps encoding copies of the last frame, forever, growing the output until the disk fills or the kernel kills the process.

**Symptom.** A render that sits at what looks like 98 percent for hours and then dies. It looks exactly like running out of memory, which is why it cost 3 days of blaming the wrong thing. Later, one new function written without the fix reproduced it for 13 hours and left a 21.7GB file.

**The fix.** **Every command with a looped image carries an explicit duration**: `-t <seconds>` on the input, and `shortest=1` on the first overlay as a second line of defence. Three layers enforce it here, because the rule alone did not hold:

- `scripts/render_preflight.sh` lints every pipeline script for a `-loop` input with no `-t` and refuses the job.
- `scripts/render_detached.sh` has a runaway guard: any watched file past 4GB (`RENDER_MAX_BYTES`) gets its encoder an interrupt, so the file closes valid instead of filling the disk.
- The tell in the log is "More than 100000 frames duplicated". Search for it first.

---

## 2. The framesync stall

**What it is.** Overlaying a finite sequence of PNGs onto a video running at a different frame rate makes ffmpeg wait for a frame that never arrives.

**Symptom.** 13 hours, no output file, no error, and an enormous memory figure (437GB of virtual size in the measured case).

**The fix.** Never hand ffmpeg a finite PNG sequence and an infinite video in the same graph. Composite the sequence into the frames first (in Python or your renderer) and bake it into the segment, so ffmpeg only ever sees plain video or properly bounded loops.

---

## 3. Something killed the render on purpose

**What happened.** A memory-freeing sweep killed a 4 hour render at 98 percent, then killed its rerun at 95 percent, the same day. ffmpeg was the largest process, and every "free up memory" heuristic targets the largest process.

**The fix, a rule rather than code.** **While a render runs, nothing gets killed.** No cleanup sweep, no "close the big one", no process manager. If you run any automated cleanup, it must refuse to touch anything with an ffmpeg child.

---

## 4. The conversation itself killed it

**What it is.** A render started as a child of an AI conversation dies with that conversation: the session ends, the harness restarts, somebody interrupts.

**Symptom.** Instant, silent death. No error, no log line, no growth after the moment the session ended. You find out 40 minutes later.

**A note on diagnosis.** The first reading of one such death blamed a new chat message arriving. It was wrong: the job had been stopped by hand. A message arriving does not kill a background task. The structural risk is real anyway, and a cause is a hypothesis until something reproduces it.

**The fix.** **Anything over 10 minutes runs detached, never as a conversation background task.** `scripts/render_detached.sh start <name> --watch <dir> -- "<command>"` gives the job its own process session (macOS ships no `setsid` command, so a one-line Python `os.setsid()` does it), `nohup` survives the session ending, `caffeinate` stops a Mac sleeping, the supervisor retries once, and a status line lands every 60 seconds.

**One limit found the hard way: a detached job sends no completion notice to the session.** A watcher beside it closes that gap: `until [ -s .renders/<name>/exit ]; do sleep 30; done` as a background task in the session wakes it when the job finishes.

---

## 5. A scheduler killed the detached runner as it started

**What it is.** A scheduler (launchd, systemd, a cron wrapper) starts `render_detached.sh` and exits within a second. Some schedulers then kill every process left in the job's process group, and the runner had not yet reached `os.setsid()`, so it died with the group.

**Symptom.** The scheduler's log says "started" and a pid file exists, but no `status` and no `run.log`, both of which the supervisor writes in its first second.

**The fix.** On macOS launchd, `<key>AbandonProcessGroup</key><true/>` in the agent's plist. Reproduced with 2 throwaway agents: without the key nothing ran; with it the child wrote and survived. Either way, have the scheduled script check 15 seconds later that the runner pid is alive and its status file exists, and alert if not. **Any scheduled job that starts a detached job needs the same key.**

---

## 6. Nobody could tell working from stuck

**Symptom.** "Is it actually working?" asked 3 times over 3 days, answered with 3 opinions.

**The fix.** **Working means the output file is growing.** Not the CPU meter, which is high both when ffmpeg encodes and when it spins on a stall. `scripts/render_status.sh <dir>` samples every recent output twice, 3 seconds apart, and reads a `_render.status` heartbeat if your pipeline writes one. `render_detached.sh status <name>` reads the 60 second trail.

**And a promised time gets a status line before it expires.** When a render passes the time you said it would finish, say so with the new estimate and the cause, before anybody has to ask. Read the bytes-per-minute rate and the encoder count in the status trail before quoting a time.

---

## 7. A concurrent write silently shortened a shot

**What it is.** 2 style variants of the same edit rendered at once, and one rewrote an image file the other's encoder was reading. A segment returned exit 0 with 305 frames where its plan required 641. A short segment shifts every later caption against the audio.

**The fix.**
- Give every generated still a variant-specific filename, and write generated images through an atomic rename (write to a temp name, then rename).
- Accept a cached segment only when its recipe fingerprint AND its actual frame count (`nb_frames`) both match the plan.
- Before muxing, check each new segment and the joined picture again. After export, fully decode each delivered file and compare picture and audio durations.

**A zero exit code from the encoder is not proof the output is right.**

---

## 8. The machine is genuinely out of room

**What it is.** Too many heavy processes resident at once. On one measured evening, 18 to 20 AI sessions were open, the load average hit 716, swap reached 96.8 percent, and macOS killed the largest process, which is always ffmpeg.

**Worse: a full disk plus memory pressure took the whole machine down.** Twice, on 2 different laptops, the machine kernel-panicked and restarted during overnight work. Both times the cause was memory running dry on a nearly full disk, not hardware. On a full disk the OS cannot even grow swap.

**What helps.**
- **Check free disk first.** `scripts/render_preflight.sh` refuses below 25GB (`RENDER_MIN_DISK_GB`). On macOS, deleting files frees nothing while a local Time Machine snapshot still holds them: check `tmutil listlocalsnapshots /`.
- **A memory gate that reads the right signal.** Free memory percentage (macOS `memory_pressure`, Linux `MemAvailable`), not swap used. An OS keeps swap allocated long after the pressure is gone: one gate waited all night on "swap 85 percent" with 49 percent memory free. `render_detached.sh` waits until free memory is at least 25 percent or swap is under 85 percent. `RENDER_GATE=strict` (what the queue uses) never starts into swap.
- **An optional pause hook.** `RENDER_PAUSE_CHECK` is any command that exits 0 when renders must wait (a screen recording is live, your own memory brake is on). `start` then refuses with exit 75 instead of competing.
- **Close things before bed.** No script can close your interactive sessions for you, and an automated reaper that respects them closes nothing. This is a human step and it belongs in the evening, not at 3am.

---

## 2 smaller risks worth knowing

**No timeouts.** A `subprocess.run` with no `timeout=` waits forever. One wedged ffmpeg and a whole worker pool never returns, with nothing reporting it. A timeout turns a silent hang into a clean failure.

**Worker counts measured on an idle machine.** A soak (`scripts/render_soak.sh`) on a 16GB laptop: width 4 ran at 2.12x realtime, width 8 at 1.25x, the opposite of an earlier benchmark taken under different load. Re-measure under real conditions, and default lower than the idle benchmark says.

---

## What the soak showed

Clear machine, 21 minute master, captions and a speed change:

| Shape | Result |
|---|---|
| Monolithic finalize (one ffmpeg, full length) | **completed**, 16.6 minutes wall, peak ffmpeg memory 851MB |
| Parallel finalize, width 4 | 2.12x realtime, peak 2.56GB across workers |
| Parallel finalize, width 8 | 1.25x realtime (slower than 4), peak 2.36GB |

So the monolithic render does not hang by itself. The deaths that week were the runaway tail plus a loaded machine. The same full finalize took about 10 minutes at width 4 on a clear machine and about 25 minutes under heavy load. **Measure before you rewrite.**

---

## The routine

**The job runs from your project root, with every path relative to it**, the same way every time. 5 failed launches in one day came from running the same script from different places.

**One render:**
```
scripts/render_detached.sh start ep-01 \
  --watch content/videos/ep-01/renders \
  -- "python3 content/videos/ep-01/build/finalize.py"

scripts/render_detached.sh status ep-01           # running, finished, or died
scripts/render_status.sh content/videos/ep-01     # is the file growing
scripts/render_detached.sh tail ep-01             # last 40 log lines
scripts/render_detached.sh stop ep-01             # the whole process group
```

**Stop with `stop`, never by killing the pid in the folder.** The pid is the supervisor; the encoder is a grandchild in the same process group. Killing only the supervisor once left 3 encoders writing one output file at a tenth of normal speed for 47 minutes.

**Several overnight:**
1. `scripts/render_queue.sh add <name> --watch <dir> -- "<command>"` for each video.
2. Close what you can spare.
3. `scripts/render_queue.sh run`. Detached, serial, each job behind `render_preflight.sh` (disk, ffmpeg, the `-loop` lint, your `RENDER_PREFLIGHT`) and the strict memory gate.
4. Morning: `scripts/render_queue.sh status`, one line per video.

---

## If it hangs again, check in this order

1. **Is the file growing?** `scripts/render_status.sh <dir>`. Growing means working, however slow.
2. **Is the job alive?** `scripts/render_detached.sh status <name>`. "NOT RUNNING and no exit file" means something killed it.
3. **How loaded is the machine?** Load per core over 4, or memory under 20 percent free with heavy swap, and it was killed for memory. Close things and restart it detached.
4. **Was it a conversation child?** If it was not started through `render_detached.sh`, assume the session took it. Restart detached.
5. **Read the log for the tell.** `tail <name>`. "frames duplicated" means the runaway tail is back.
6. **Was it self-inflicted?** Audit your own ffmpeg command before blaming the machine. 3 confident misdiagnoses in a row once hid a missing flag for 3 days. Say "hypothesis" out loud until it reproduces.

---

## Tried, and what happened

Keep a table like this for your own pipeline. Every row is an attempt with its outcome.

| What | Outcome |
|---|---|
| Explicit `-t` on every `-loop 1` | Works, but a new function without it reproduced the runaway. Now also a preflight lint and a 4GB guard |
| Parallel finalize instead of one monolithic encode | Works. Width 4 beat width 8 on a laptop |
| A conversation background task for the whole chain | Vulnerable to the session ending |
| `render_detached.sh` | Works, survives the night. No completion notice to the session, so pair it with a watcher |
| Memory gate on swap used | Wrong signal. Replaced with free memory percentage |
| An automated reaper before every render | Runs, closes nothing interactive by design. Only a person clears the machine |
| 3 overnight supervisors waiting with `pgrep -f` | They matched each other's command lines and ran a stale job. Replaced by one queue waiting on exit files |
| A soak script using `timeout` | macOS has no `timeout`: every step exited 127. Replaced with a perl alarm |
| Serial queue plus preflight | Works |

## Not tried yet, worth trying

- A scheduler agent that watches `.renders/*/exit` and notifies you, so no watcher task is needed.
- Hardware-encoded chunks (`h264_videotoolbox` on a Mac) to cut finalize time and memory. Quality against libx264 unmeasured.
- Chunk-level checkpointing, so a retry skips chunks already rendered.
- A hard per-job memory ceiling so the kernel never has to choose.
- Rendering on a second machine or a cloud worker. See `content/reference/cloud-rendering.md`.
