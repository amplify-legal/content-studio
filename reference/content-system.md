# The content system, as a map

> How the parts fit. `content/PRINCIPLES.md` is the constitution and wins over anything here: the system amplifies the creator's judgment and never replaces it. This file is the operating map; each part's detail lives in the skill or doc it names.

One recording becomes a week of output across every surface, governed by the creator's taste, operated by the skills, and measured by the outcome the creator cares about (bookings, sign-ups, replies), never by views alone.

---

## The shape

```
 ideas in                 before recording            record            after recording
 ---------                ----------------            ------            ---------------
 seeds (theirs)    ->     brief (interview)    ->     on-camera  ->     edit (long form, shorts)
 signal (mined)           script (interview)          board             cut-review gate x2
 inspiration (links)      packaging (title +                            verify loop + render
                          thumbnail together)                           launch checks
                                                                              |
                                                                              v
                                       waterfall: shorts, posts, carousel, community post, send list
                                                                              |
                                                                              v
                                       publish (platform native) -> read it back -> scoreboard -> retro
```

Nothing in it is a strict pipeline. Ideas ebb and flow. State is a map, never a gate: when something upstream is missing, the system names it and offers options, and never blocks.

---

## The parts, and who owns each

| Part | What it is | Owner |
|---|---|---|
| **The door** | `/content`. Hand it an objective, a half-thought, a link, a pile of references, or nothing. It reads what you are after, asks when it is unclear, and pulls in the right skill | `.claude/skills/content/` |
| **Principles** | The constitution. Loads before any content step | `content/PRINCIPLES.md` |
| **Taste** | The shared brain, as data: voice, hooks, packaging, thumbnails, formats, stories, the clip bar, editing rules and checklist, must-dos. Every skill reads it; no skill restates it | `content/taste/`, written by `taste-builder` |
| **Frameworks** | Per-surface rules: the long-form pillar, the short, the post, the carousel, the send artifact, the research brief | `content/frameworks/` |
| **Seeds** | The creator's own ideas, captured verbatim first, riffed second. Outranks anything the machine mined | `content/seeds.md`, via `content-waterfall` seed |
| **Signal** | Real audience language mined weekly from comments, calls and searches | `content-waterfall` mine |
| **Inspiration** | A link, a thumbnail, a creator dropped with a reaction. Lands verbatim in the packaging inbox, then gets a teardown from actually watching it | `content/taste/packaging/inbox.md`, `watch` |
| **Brief** | The pre-recording interview record: the promise, the numbers they will defend, the spine in their order, what to leave out, the call to action, the derivative map | `content-waterfall` brief |
| **Script** | Built from an interview, never a blank page. Analogy pass, transitions pass | `script-writer` |
| **Packaging** | Title and thumbnail as one story, shown as built images with candidate titles under each, never proposed in words | `content/taste/packaging.md`, `content/taste/thumbnails.md`, `media-gen` |
| **On-camera board** | The surface the creator presents from and draws on while filming | `on-camera-board` |
| **Edit** | Long raw recordings into real content; picked clips into branded 9:16 shorts | `long-form-editor`, `shorts-editor` |
| **Review gate** | Before the creator watches any cut: checklist, brief, privacy frame check, a timestamped fix list. Runs before both gates (after the first cut and before launch) | `cut-review` |
| **Render** | Long renders detached, a self-checking loop for repeat formats | `content/reference/render-reliability.md`, `content/reference/verify-loop.md` |
| **Design** | Every HTML surface (prep docs, review boards, reports, send artifacts) on a measured design payload | `design-dna` |
| **Waterfall** | Per-surface chains off a finished recording | `content-waterfall`, `post-writer` |
| **Checks** | The claims and phrases copy must never carry, checked by a script | `scripts/copy_check.py`, `content/reference/the-checks.md` |

---

## How the door behaves

1. **Reads the room.** One clear intent: says it back and goes. Two or more: asks, with real options. Resolving ambiguity in conversation is the work, not a failure.
2. **Knows what exists before proposing.** Reads what is in motion, the seeds, the signal, the briefs and the packaging inbox, and says what it found.
3. **Interviews by default.** It generates without asking only when told "just draft it" or "no questions", when re-running a stage already shaped, or when given a delivery instruction with a deadline and a named use. It writes which rule applied into the output's header.
4. **Retro with teeth.** Every "I wanted X instead" lands verbatim in the skill or taste file that produced the thing, the same session.

Every shortcut (seed, brief, mine, waterfall, send list, scoreboard) is the door with a fixed intent, so the posture is identical whichever one is typed. One shortcut once generated a whole brief without asking a single question, because its interview step lived in a different entry point. That is why there is one door.

---

## Rules that cross every part

- **Capture before analysis.** Any unprompted dictated block about content goes verbatim into seeds first.
- **Taste is data, skills are engines.** A skill never restates a taste rule; it reads the file.
- **Only the creator's own words are quoted as theirs.** Anything the machine inferred is labelled as inferred.
- **Show the asset, never describe it.** Thumbnails, boards and cards are built and shown before anybody decides.
- **A video that promises anything on camera does not publish until every promise is a live link in the description**, fetched and returning 200 in the launch session. A viewer who is promised a resource and does not get it reads the whole video as clickbait.
- **Any frame pulled from a recording is checked at full resolution before it can be posted** for attendee faces, name labels, client names and private interface behind the work. Where a screen share has a webcam column, cropping the column off is usually the whole fix.
- **A workspace surface going on camera is rebuilt clean, never the real page blurred in motion.** A moving blur leaks frames at handoffs, misses short exposures between samples, and smears teaching content when over-applied. A clean copy with stand-in names and same-shape figures has nothing to leak.
- **A publish is proven by reading the profile back, never by the composer going quiet.** A platform can show an error and still accept a retry, and 4 copies of one post went live that way. After any publish that took more than one attempt, count what is actually there.
- **The end-of-run review is a separate reader**, never the session reviewing its own work.
- **Two sessions producing at once announce themselves** on a shared in-flight list at open (a map, never a gate). The load-bearing duplicate check is re-reading the target file immediately before writing it.

---

## Publishing

Use each platform's native scheduling where it exists (for example YouTube's scheduled publish time on a private upload), and put a date on only after the creator says go. Where a platform's posting API is closed to tools that post for accounts you manage, a hand card (the file, the caption, the time) is the honest route. Whatever posts, a person approved it first.

---

## The learning loop

Every skill ends with a retro. A repeated error becomes a dated rule in the skill, taste file or framework that produced it, capped and pruned. Cut feedback from a review is captured verbatim the moment the review closes, into `content/taste/cut-feedback/`, and becomes labelled examples for the review gate. A weekly scoreboard picks one improvement, writes it into the right file the same day, and the next week opens with whether it held.
