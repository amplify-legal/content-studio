# The interview, stage by stage

> What the door **asks** versus what it just **does and shows**. Ask-more depth, deliberately chosen over a shorter interview: the creator is spending their own time to keep assembly decisions theirs.
>
> **These are the questions that tend to matter, not a script.** Ask them in whatever order the conversation wants, skip what they already answered, and follow them when they go somewhere better. A stage where they answered everything in one paragraph is a finished stage.
>
> The failure mode this file exists to prevent is producing without them, not asking too few questions in the wrong order.
>
> The method under all of it is `content/taste/interview/protocol.md`. Layer order is law: never lock a layer before the one above it.
>
> **The retro may shorten this when they say "stop asking me about X." It never drifts the other way.**

---

## How the questions actually reach them

**Ask in small batches, not a wall of prose.** If your harness has a structured question tool, use it, and always leave an open "something else" option, because that is how they riff. Some people want the wall instead. Give them the wall when they ask for it.

**4 questions per batch is the cap**, so a brief interview is roughly 3 batches, most upstream first:

1. The map and the promise. Get these right before anything downstream.
2. The spine, what to leave out, and their honest read.
3. Packaging, the CTA and slot, the derivative map.

Put real context in each question and a real tradeoff in each option, not a restatement of the label. Lead with a recommendation and label it as one, **except where they are the only honest source: scope, the spine, and anything where they are correcting the machine's read get asked open, with no recommendation attached.** A labelled recommendation on a scope question has to pick, and picking is exactly what the machine gets wrong.

3 more rules in the same spirit:

- When they say they do not understand a question, **re-ask it as a batch with real options** rather than re-explaining it in more prose. The longer wall does not help.
- When their answer is a bare pick, **ask the one-line why before recording it.** A brief full of single letters cannot be defended by a later session.
- If they answer 3 questions in one sentence, **do not ask them again.** And when they dictate one continuous answer across a batch, treat ambiguity as a reason to ask, not to infer.

**Before any batch fires: read the work in progress and the last 3 turns, and drop every question whose answer is already on the page.** Getting asked the same question twice is where the energy goes. When a re-ask is genuinely needed, open with a quote of what they said and ask only the delta.

**A hedge with an instruction inside it is a build instruction, not an open question.** "That is fine, but not final, needs refining" means go refine, and come back with 3 concrete refinements attached to the artifact. It never re-enters an open-questions list as the same bare question. That happened to one title for 3 days straight.

### Provenance in every read-back (hard rule, it protects the record)

When reading an idea or a map back, **quote only their own verbatim line as theirs**, and label anything the machine added as the machine's proposal awaiting their answer. The shape: "here is what I recorded, and here is what you actually said."

One map option should always break the machine's own frame (scope, count, audience), so that a yes cannot quietly ratify an unexamined premise.

### The conflict rule (hard rule, it protects their judgment)

**When their answer does not fit the map, the map is wrong.** Say the mismatch back ("you said 3, I have been carrying one, which of us is holding it wrong?") and reopen the scope before anything below it moves.

**"That's not my question" is banned as a response to them answering.** If their answer does not fit the question, the question was wrong. One creator gave the correct scope twice and was told both times he was answering a different question.

### Nothing is locked without a quotable answer (hard rule, it protects the record)

A layer closes on an option they picked or a sentence they wrote. Everything else is **proposed**, and gets read back as such ("I have assumed the close does X, you have not said"). Never open a downstream question by listing endpoints as fixed unless you can quote the answer that fixed them.

The machine never says **locked, settled, final or decided** about their answers. It says what they said, and who decides. An option they did not tick is an open question, never a keep, and never a downstream blocker.

### If the interview stalls (guideline)

After roughly 30 minutes of silence mid-interview, write the current state into the file with `OPEN:` markers rather than holding it in the thread, and do not fill the gap with downstream drafting. A 6-hour silent gap is where 2 same-day briefs once diverged.

---

## Brief (the highest-judgment stage, and where the failure happened)

Roughly in this order:

**0. Announce, then sweep (guideline, a map and never a gate).** If you run several sessions at once, write your claim into `content/in-flight.md` first (seat, start time, item, what you intend to write). Then the sweep, which is cheap and usually empty. A live row for the same item means join that work or say so out loud, never open a second interview. A row older than about 4 hours is stale and gets surfaced in one line, never silently ignored. Also look at `content/live.md` and the modification times in `content/briefs/`. **The load-bearing check is the re-read immediately before you write the file** (the claims file, `content/briefs/`, today's rows in `content/work-record.md`, `content/taste/voice.md`), because a long interview can be overtaken while it runs. Clear your row at close.

**1. The scope, before the map. Asked open, no recommendation.** Is this one piece or several, and what is in each? If they say "3 X", ask whether those are 3 sections or 3 episodes. One run assumed episodes, briefed one of them, and had to be rebuilt.

**2. The map, read back, with provenance.** "Here is what I recorded, and here is what you actually said. Does that match how you would actually teach it, or does something move, drop, or get added?" Get the yes before anything below it, and the yes has to be to a map whose machine-written parts were labelled as such.

**3. The promise, and the numbers they will defend.** Not a title yet. The sentence a viewer would use to describe this to a colleague. Offer 3 or 4 honest framings and ask which is true, or what the fourth is. Fire this early, never at the end.

**In the same breath, the numbers:** which figures they will actually defend on camera, what each is sourced to, and which are their own credibility claims. Skipping this once buried a real warning ("the dollar figures are gross") inside an HTML attribute for 10 hours. One question converts a hidden warning into a decision somebody made.

**4. The spine, in their order. Asked open, no recommendation.** The wording that works, and it is the wording rather than a stylistic preference:

> "If someone opened this on YouTube and looked at the chapter list down the side, what would the chapters say, top to bottom? First chapter is the belief. What are the 4 or 5 in the middle?"

The gloss, if they need one: the pieces, in the order they would actually teach them. Keep the chapter framing as the question. The teach-order phrasing had one creator answering "I'm not understanding"; the chapter phrasing unblocked him in one go.

Never propose the spine first. Their sequencing is the argument. On a series, ask what the dependency order is. **Record their names for the sections beside any working names**, because theirs goes on camera.

**5. What to leave out, and what to keep that a shorter version would drop.** The cut nobody asks for and everybody needs. Ask it explicitly. This is where the piece gets good.

**Ask both halves.** A menu of pure subtractions reads the question wrong. On one brief the creator rejected 3 of 4 proposed cuts and explained why each one stays: tool recommendations with an honest counter attached, statistics provided they carry an animation, backstory as long as it is unforced. His words: *"I think it's a little more nuanced than that. I still wanna give a couple recommendations on how to solve it easily and then give an honest counter to what the issues are with those tools."*

**Never offer "keep it abstract" as a serious option.** Authority is built, sold and delivered, never gestured at. When a layer threatens the runtime, propose asymmetric depth (one item at full depth, the rest at one constraint each) rather than cutting the layer.

**6. Packaging candidates.** 3 to 5 title framings and a thumbnail direction, drawn from `content/taste/thumbnails.md` and the teardowns in `content/taste/packaging/`. **Ask which is true, not which is best.**

**When the brief reaches for a story**, from their bank in `content/taste/stories.md` or anywhere else, pick it for the viewer's situation, never for its drama. Ask: would someone in this audience see themselves in this? A dramatic story the viewer will never live through cannot help them avoid the mistake.

**7. The CTA and the slot.** What is the ask, where does it sit, and is there a resource behind it? Then the record date and the launch slot, or write both as proposed with the decider named. Any framework's default position for a CTA is **the default this question offers**, never the answer. Ask what the end CTA is for THIS video; it varies with the video's purpose. Their answer outranks it everywhere it is written down. One machine asserted a mid-video CTA and a free resource, and was wrong on both halves at once.

**8. The derivative map, and the memorable lines you come up with together.** Say out loud that this is not a recording decision, because otherwise it reads as one and they will ask what it has to do with the piece.

Which sections carry the shorts, which lines carry the posts, what the carousel is, what the send artifact claims. The bar a short has to clear is `content/taste/clip-bar.md`. **Per spine piece, mark which beat is expected to become the short**, usually the analogy or the framework. This complements, never replaces, picking clips from the tape: the skeleton raises the odds the tape contains clean clips, and the picks still come from watching it.

**The memorable lines are co-created here, never planted by the machine.** In their words: *"throughout the interview, we come up with those zingers together. It still needs to be my words and needs to be my essence."* Lines they want verbatim go into the brief's key-lines slot, their count, no promises about pause brackets.

### 2 things to do alongside the asking

**Offer a view, once, before the spine is locked.** After they have given the promise, say what you actually think: the strongest angle, the part that sounds like everybody else, the thing that would make somebody stop scrolling. Cite what it is built on. Then drop it and follow their call, and record their call, not yours.

**Say when an idea looks weak.** If the answers are thin, if there is no real example and no real number, if it is a view-winner rather than a taste-winner, say so plainly and early. They would rather hear it at the brief than after the edit. This is not a veto: they can overrule it in one word and the brief records that they did.

### DO AND SHOW, without asking

Pull their mined language and the buyer language from `content/signal.md`. Find and verify timestamps against the raw. Fill the template. Check claims against the canon and flag anything needing a plausibility check. Write the file.

---

## Script

**Load first:** `content/taste/script-format.md`, the shape they record from (full written hook, guide bullets per section, key lines verbatim and visually distinct, transitions offered, analogies placed).

**ASK, by name:**

- **The analogy, per spine piece. Never skipped.** For every piece: "what's the analogy that makes this click?" The bar: move from something familiar to the thing being taught, so the viewer feels smart instead of lost. When they say "you come up with a few", offer from these modes (everyday, scenario, demonstration, case, counterexample, before and after, numerical, personal story), with hypotheticals labelled as hypothetical. Every section ends with an analogy placed or an `OPEN:` marker.
- **The transitions pass, once, across the joints.** After per-piece content locks and before hook corrections: "what makes someone need piece 2 after piece 1?" Offer from the transition modes (sequence, contrast, escalation, question, callback, cause and effect, zoom). Fast by design: a transition can be one sentence, so this pass takes 2 minutes, not 10.
- Goal, audience and value. Title, promise and authority calibration. Hook corrections, which they react to and edit live. Build sequence. The close. CTA placement per the brief's recorded plan.

**DO AND SHOW:** the research pass beforehand (`content/frameworks/research-brief.md`), the draft after the interview (a full v1, self-reviewed, handed over without asking once the interview is on record), the visuals plan, and the on-camera surface (`on-camera-board`). Check the draft against `content/taste/must-dos.md`, so every resource, ask and on-camera promise it needs has a place.

**The deck derives from the approved script, never the other way around.** When both exist for the same recording, read them against each other and report the diff: section order, numbering, every number said aloud versus every number on screen.

Run the mechanical copy check (`python3 scripts/copy_check.py <file>`) before any script is called final.

**Writing the script first and asking them to react to it is the thing to avoid.** Their framings and analogies are the asset, and those only come out in conversation.

---

## Shorts

**ASK:** their clip picks, and nothing else. Timestamps, or "the bit where I said X".

**DO AND SHOW:** everything else. Transcription, the edit list, the cut, silence trim, re-transcribe for sync, cards, captions, composite, self-check, retro.

**Auto-selecting clips is out. Hard rule.** That is the whole input contract.

---

## Posts

**ASK:** which approved line each post carries, and the CTA mix for the week (one CTA per piece).

**DO AND SHOW:** the drafts themselves (`post-writer`), from approved material only, in their voice per `content/taste/voice.md`.

**Never drafted from the video script.** Drafted from the source material and the mined language. On our own feed, posts drafted off the script consistently underperformed posts drafted off the source. Measure your own before you treat the gap as a number.

---

## Packaging (titles, thumbnails)

**A title question is always multi-select.** If every video tests 3 titles, a single-pick question makes no sense: ask for their 3, then ask which goes first. The test order is their call, because the first slot owns the launch window.

**Titles first, on text, at zero render cost.** If the brief's title candidates are machine-written and unconfirmed, the title round runs before any render fires. Their pick or their sentence goes into the brief, and only then does the board render against it. One run burned 2 render rounds partly on title triage, and the creator ended up typing the title himself.

**The competitor sweep runs automatically** when the lane has no dated sweep from the last 30 days. Before the direction question, offered as directions, never waiting for somebody to ask for research.

**ASK:** which framing is true. Which thumbnail direction. Whether it is a series template or a one-off. Which finish level, per piece, never a lane default.

**DO AND SHOW:** candidates informed by `content/taste/thumbnails.md`, the teardowns and the pattern research. Renders through `media-gen`. Every thumbnail test carries at least one candidate built on a real frame from the actual video.

**The face lock is stated here because this is where the render is ordered: both reference images passed together, named ahead of the prompt, or the render comes back as a different person.**

**Before showing any render, state which standing rules were applied and show the check** (the 2 references, the title-caption rule, the taste file consulted). A render shown without that line is asking them to be the compliance check on rules they already wrote down.

**An unconverged round leaves a record and a resumption point.** "Another turn" is a required continuation, not a session end. Their verbatim reactions get written to the piece's packaging file before the round closes, and if the session ends unconverged, the open round lands as a row in `content/live.md`. Any packaging rule they state that is not specific to this video is copied into `content/taste/thumbnails.md` the same session, not only into the brief.

**Round 3 must change inputs.** New references, or an edit of the exact render they liked. Never a third generation from the same prompt family. One board burned 15 renders across 2 rounds and left no record at all.

**Never propose a thumbnail in words.** Build it and show it, with the candidate titles captioned underneath, because the thumbnail and the title are one story.

---

## Ideation and review

**Ask, and mostly listen.** This stage is entirely theirs. What have they been chewing on, which of these is alive, what should die, what do they want to make.

**DO AND SHOW:** the read-back (their seeds and ideas first, the machine's signal second), one retrieval per idea in service of their answer (a real buyer's words, an outlier, an adjacent pain), and the grouping.
