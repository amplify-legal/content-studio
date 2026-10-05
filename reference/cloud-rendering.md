# Rendering on a cloud machine

> A short, generic version. The working setup this came from is a long log tied to one cloud account, one bucket and one set of episode adapters, so it is not ported. What carries over is the design and the lessons it paid for. Read `content/reference/render-reliability.md` first: the local runner stays the route for urgent work, and every local lesson still applies on the cloud worker.

---

## When it is worth it

A laptop that renders overnight cannot be used, can panic on a full disk under memory pressure, and sleeps. A cloud worker renders while you keep editing. The cost is setup and a new class of failure: the job now runs on a different operating system, with different fonts and a different ffmpeg build, far from the files.

Start local. Move a recipe to the cloud only once it renders correctly and repeatably at home.

---

## The shape that worked

```
spec (inputs hashed) -> private bucket -> one worker VM, serial jobs -> checks -> receipt
                                                                              |
                         your machine reconnects -> verify hashes -> place in the usual folder
```

1. **A spec per job.** A profile (which container), a project-relative working dir, the command as an argument array (never a shell string), every input file (code, media, fonts) with its hash, and every output with its worker path and its local destination. A script that is not explicitly declared is not staged. Credential-like files are refused.
2. **A dry run first.** Hash the inputs and print the planned job without uploading anything.
3. **Publish the manifest last.** The job becomes visible to the worker only after every input has uploaded. The worker re-hashes each downloaded file before it starts.
4. **One worker, serial jobs.** The same rule as the local queue: 2 encodes at once is how one gets killed.
5. **A per-job time limit, an idle shutdown, and a watchdog** that stops the machine only when its worker is genuinely inactive, so a long queue is not cut off mid-job.
6. **The worker checks its own output before calling a job done**: a video stream with dimensions, a positive duration, a full decode, and a receipt naming every declared output exactly once with its size and hash. An incomplete receipt fails the job so it can be retried. It never becomes a delivery.
7. **A return agent on your machine.** It waits for you to be online, copies each verified file to an ignored inbox first, and moves it to its usual destination only if that destination still has the hash it had at submission. If you edited the destination meanwhile, it reports a conflict and leaves your file alone.

---

## Rules that held

- **A cloud failure never silently starts a local encode.** Failures stay visible with a reason and a worker log. Retrying makes a fresh job from the same frozen inputs.
- **A changed source file rejects a resume.** Resume finishes an interrupted upload under the same frozen identity; it never mixes old and new inputs.
- **A malformed job is marked failed with a reason**, never restarts the worker forever, and never holds valid jobs behind it.
- **A partial download is never placed as a finished file.**
- **No automatic deletion of finished files** until local delivery is verified, and retention is agreed before any lifecycle rule goes on.
- **Cost estimates are estimates, not caps.** Per-job limits and watchdogs reduce spend; they do not stop it. A stopped VM still bills for its disk. Billing alerts warn, they do not halt. Read your provider's pricing pages and budget docs before the first job.
- **Lock down network access** to the worker before it holds anything: deny all inbound by default and allow only the admin route your provider recommends.

---

## The lessons it paid for

- **Pin the ffmpeg build per recipe.** The same lossless stages encoded to AAC on 2 different ffmpeg builds produced audio that differed enough to fail an alignment check. The edit had not changed; the lossy encoder had. Compare alignment on a lossless sidecar, not on the lossy output, rather than widening the acceptance limits.
- **Freeze the fonts and check on the target OS.** Caption fonts and their rendering differ between operating systems. A recipe is cloud-ready only after a real render on the worker's OS has been reviewed.
- **Hardcoded paths break on the worker.** Scan a recipe for absolute paths to your own machine before submitting it, and refuse the submission with a clear message rather than uploading a job that cannot run.
- **A stream-copy concat can drift the audio** a few milliseconds per join. One delivery showed 18ms, corrected by remuxing without re-encoding the video. Check the joined file's picture and audio durations, as in the local reliability doc.
- **A Linux worker has no `memory_pressure` and no `caffeinate`.** Gates and keep-awake helpers must degrade gracefully there; `scripts/render_detached.sh` reads `/proc/meminfo` instead and skips keep-awake.
- **An unattended reboot is a test you have to run.** One reboot exposed a missing CLI account selection that only showed up when nobody was logged in. Boot the worker cold once and watch it pick up a queued job before trusting it overnight.
- **A security prompt from a helper binary is not a reason to loosen security settings.** When a checksum helper triggered repeated system alerts, the fix was restoring that one binary from the vendor's official archive after verifying its published hash, nothing global.

---

## What you would need to build it

A cloud account with billing, a private storage bucket, one small VM (4 vCPU and 16GB RAM handled a 1080p episode), a container image with your exact ffmpeg build, fonts and Python packages, a submit script that writes the spec, and a return agent on your machine. Expect a few days of setup and a pilot per recipe before any of it is your overnight default.
