# The intent map

> What arrives, what it probably means, what to ask when it does not resolve, and which engine runs.
>
> **This is a reading aid, not a switch statement, and it will always be incomplete.** When 2 rows fit, ask. When none fit, ask what they are after in their own words, and add the row afterwards. Guessing wrong and saying so is better than a long clarifying interrogation about something obvious.
>
> **It grows by retro.** The bottom section is where a real run adds a row. A door that never gains rows is a door nobody is using.

| What arrives | Likely intent | Ask when unclear | Engine, and where it lands |
|---|---|---|---|
| A dictated thought about a piece, an idea, a half-formed angle | Capture, then riff | If it sounds like a decision rather than an idea, ask whether to capture or to act | Verbatim into `content/seeds.md`, then the riff per `content/taste/interview/protocol.md` |
| Links (YouTube, Instagram, TikTok) **with reactions** about what they like | Could be 3 things at once: inspiration for the taste library, ideation fuel, or the visual reference for one specific upcoming piece | Ask: "Filing this as taste, mining it for ideas, or is this the look for a specific short?" All 3 is a valid answer | Inspiration goes to `content/taste/packaging/inbox.md` with `by:` naming who sent it, plus the teardown (the `watch` skill, packaging lens). Ideation goes to `content/seeds.md`. Visual reference gets noted against the piece in `content/live.md` |
| Links **with no reaction** | Probably inspiration, but the reaction is the asset | Ask what they liked about it before doing the teardown. Never tear down a link whose "why" is missing | `content/taste/packaging/inbox.md`, after they answer |
| "What should I record today / this week" | Propose with reasoning, then ask | If the week's slots are already filled, ask whether they want to change one or add one | Read `content/live.md`, `seeds.md`, `ideas.md`, `signal.md`, analytics and the next 7 days of the calendar. Propose 3 with a reason each. Ask |
| "Let's ideate" | Fresh ideation, with them | Ask what it is for: a slot this week, the backlog, a specific lane | The riff, run generatively. Their ideas first, signal second, one retrieval each |
| "Review all the ideas" / "what have we got" | Read back and triage together | Ask what they are deciding: what to kill, what to promote to a brief, or just a look | Read `content/seeds.md` and `ideas.md` first, then `signal.md`, group, present, ask what to kill, keep and promote |
| "Brief the X piece" | The brief interview | If no shaped idea exists, name it and offer riff-first, brief-from-raw, or both | The interview per `interview-stages.md`, then `content-waterfall` as the brief writer, into `content/briefs/` |
| "I need a title / thumbnail for X" | Packaging | Ask which framing is true before generating candidates | Pattern research plus `content/taste/thumbnails.md` plus `media-gen` for renders. A title question is multi-select: ask for the 3 they want tested |
| "Make the short(s)" | Rendering picked clips | **Ask for their clip picks. Hard rule: no auto-selection** | `shorts-editor` |
| "Review this cut" / a cut arrives | The pre-human gate | If no brief exists, say so. A cut reviewed against nothing is half a review | `cut-review`, then their feedback verbatim into `content/taste/cut-feedback/` |
| "How is the channel doing" / an analytics export | Diagnostic | If the export is stale, ask them to pull a fresh one and say how long it takes | The analytics read |
| "Waterfall X" / a recording is done | Derivatives | Confirm the derivative map and ask for their clip picks from the tape | `content-waterfall`, after the interview |
| A raw footage link | Footage arriving | Ask what it is: a recording, a handoff, or reference | Pull it, then route by their answer |
| "Edit the episode" / a long recording arrives for a full cut | The long-form edit | Ask what it is (a podcast episode, a live workshop, a solo video) and whether a brief exists | `long-form-editor`, after `watch` |
| "What's alive" | Status | Rarely ambiguous | Read `content/live.md` back, grouped |
| A frustration, a "this did not work", a redirect | **Retro material first** | Nothing to ask. Capture it verbatim, then fix what it points at | Whichever file produced the thing, the same session; door rules go to `learnings.md` |

---

## How a row gets added

A run ends. Something was ambiguous, or was read wrong. Write the row the same session, in this shape:

- **What arrived**, in enough words that a cold reader recognises the shape next time.
- **What it turned out to mean**, and what the machine read instead.
- **What it cost.** A rebuild, a wasted render, an hour. If it cost nothing, it is probably not a row.
- **What changed**, naming the file.

Rows with no cost and no file named are the ones to prune first.

---

## Rows added by retro (worked examples, keep or replace with your own)

These 6 came from real runs. They are here as examples of the shape, and because 3 of them generalise cleanly.

- **A named piece can hide a scope question.** "Brief the X episode" where X is "the 3 biggest mistakes": the creator meant one video with 3 sections, the machine read 3 episodes, briefed one of them, and had to rebuild the lot. **Ask scope before the map: one piece or several, and what is in each.** One sentence, always worth it. This is now step 1 of the interview.

- **2 sessions briefed the same piece on the same day**, and not because either skipped its check. Both ran the sweep at the prescribed moment and both came back clean, because the first brief was committed 58 minutes after the second run's first question. **The mechanism that works: write your claim into a shared in-flight file at open, sweep cheaply, and re-read immediately before writing the file.** The sweep is not the load-bearing part. The re-read is, because a long interview can be overtaken while it runs. When shown both briefs, the creator's call was to merge them into one and mark genuine conflicts as open rather than picking.

- **A deliberately deleted brief is not raw material**, however real the facts inside it are. The creator's words when a session reconstructed one: *"pause. there's a reason I deleted the brief from Git. I don't want you to use it."* A deletion is a decision. Never rebuild killed work from version control, and never rebuild it from a live document that still points at it. Fix the pointer instead. Killed work gets a row in a graveyard file, hooked from the live file so it is read every run.

- **A real question asked back at the machine is not ambiguity and is not a new intent.** Mid-interview, instead of picking an option, the creator asked "is that enough? will it lead to a consult, or to skepticism?" The right move is to answer it with a view and the evidence behind it, record the answer as reasoning, and carry on. Firing another question batch at a question is the wrong read.

- **When every option in a batch is a way to lose, the option set is the failure, not their indecision.** 4 short-form formats were offered for a difficult recording and all 4 conceded the same constraint. Their reply: *"you have to get creative to make a super high-quality short."* The real answer was to solve the constraint, which turned out to be possible, rather than to pick the least bad concession. Build the way out before asking anyone to choose among compromises. The retrieval half of the work is where the creative work hides.

- **"Make the video about X, the conversation is archived here: <path>".** Read it as a brief, with the archive as source material rather than as the intent. 2 things to know. First, the path a harness shows for an archived session can be a metadata file that holds no messages; find the actual transcript file it points at, extract the user and assistant text to a scratch file, and index the turns before reading. Second, the name in their sentence may be their own reframe of what the archive calls it. Say the mapping back in one line rather than treating it as a new item.
