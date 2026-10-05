---
name: cut-review
description: >-
  The review gate before the creator watches any cut. Checks the cut against the editing
  checklist, the durable editing rules and the video's brief (the vision handoff), runs the
  privacy frame check, and produces a timestamped pass/fix list so the creator's watch is spent
  on taste instead of typos. Use for - "review this cut", "run the cut review", "check the
  editor's cut", "is this ready for me to watch", "cut review for <video>", or any cut delivered
  for one of the two review gates. Runs before BOTH gates (post-cut vision correction and launch
  readiness), and before any cut reaches the creator from any source (an editor, a builder, an
  overnight run, an episode pipeline). NOT a taste replacement: it clears the mechanical layer
  and rules on nothing. NOT for studying someone else's video (that is watch). NOT for rendering
  or editing (that is shorts-editor or long-form-editor).
---

# Cut Review (the gate before the creator watches)

**Load before any step:** `content/PRINCIPLES.md` (the constitution: this system amplifies the creator's creativity, it never replaces their judgment; when it conflicts with a step here, it wins). Then `content/taste/editing-checklist.md` and `content/taste/editing-rules.md`. How taste files work, and why this skill never restates them, is in `content/reference/taste-system.md`.

Every cut gets this pass **before the creator watches it**. Each video has 2 review gates: after the initial cut (vision correction) and at claimed-finished (launch readiness). This skill runs before both. The output is a fix list for whoever is editing, so the creator's minutes go to taste and vision, never to a typo or a number in the wrong format.

**This gate approves nothing.** It clears mechanics. Taste is settled by the creator watching the file, and **the creator sees the file before anything is uploaded**, without exception, including under an explicit "just handle it end to end" mandate. A finished public artifact is not what an autonomy grant covers.

---

## The standing rules

1. **Cut-review runs before any cut reaches the creator, whatever question is still open about it.** A staged cut from an editor, a spin-off, an overnight builder or an episode pipeline goes through this gate first. An open question (consent, a music choice, which ending) rides along with the review. It never replaces the review. The failure this prevents: a builder skipped the review and put a question to the creator instead, so the creator was asked to decide about a cut nobody had checked.

2. **The consent test is seen, heard or named.** A third party on a recording who is not seen, not heard and not named in the cut needs no consent: there is nothing of theirs in the file. Do not raise a consent question for them.

3. **If their speech makes the cut better, keep it and anonymise the voice.** Apply a pitch change to **their voice only** (a voice-changer pass, for example through an ElevenLabs voice tool, on their isolated audio), never to the creator's. It should sound like a different person, not like a disguise: subtle, natural, not creepy. Their face and name still go (see the frame check below).

4. **Every frame pulled from a recording is checked at full resolution before it can be posted.** Look for:
   - attendee faces in webcam tiles or gallery views
   - name labels under tiles, in participant lists, in chat panes
   - client or customer names anywhere on screen
   - private interface behind the work: sidebars, conversation titles, file paths, browser tabs, notification toasts, inbox previews

   A thumbnail-sized check misses all of these. A frame cleared as "clean, no names anywhere" has carried a stranger's face and name in a webcam tile, and another carried an undimmed sidebar of private conversation titles. Where the recording is a screen share with a webcam column, cropping the column off is usually the whole fix. On a moving recording, sample for exposures at 1 second or finer: a 1.8-second exposure survives a sweep that samples every 5 seconds.

5. **A page with videos on it is served, never opened as a file.** A review board, pick page or handover page carrying `<video>` goes to the creator over a local server that answers HTTP Range requests: `python3 scripts/serve_outputs.py [port]` (serves `outputs/`, default port 4200), then open `http://localhost:4200/<path under outputs/>`. Chromium's player needs Range (206) responses to start and seek an mp4, so a plain `python3 -m http.server` or a `file://` page shows empty players while the files are fine. Put the localhost URL and the file's path in the chat line.

---

## Inputs

1. **The cut itself**, as a local file. Download a shared link first. Never review from memory of a previous version: this version is the one being checked.
2. **The brief**: `content/videos/<slug>/brief.md` or wherever the video's brief lives. **If no brief exists, say so first.** A cut reviewed against nothing is half a review, and it is worth saying which half you did. The vision-handoff section (what the creator said the great version looks like, recorded right after the shoot) is the heart of the check.
   - **A podcast episode usually has no brief.** Its vision handoff is the episode's own plan file (for example `content/videos/<episode>/re-edit-plan.md`, the creator's notes verbatim per version) plus `content/reference/podcast-edit.md`. Read those two instead, and say which you used.

---

## Long-form first: the machine gate

**A full long-form episode has a machine gate that runs before this skill.** The episode's verify loop must be green: `python3 scripts/verify_loop.py` on the episode folder (the four-file convention in `content/reference/verify-loop.md`). The machine pass owns duration, A/V drift, freezes, black frames, dead air, empty layout wells, and a frame every few seconds across the whole runtime. This skill owns everything it cannot see. Do not re-check those by hand, and do not review a cut whose report is red: the fix list would be about a file that is being re-rendered anyway. **Green is not done.** Green means the machine found nothing; this gate and the creator's watch still run.

**On a long-form episode the end-of-run review is a separate sub-agent, not this session.** Spawn an independent reviewer (on your strongest model), hand it the file path, the plan file and the whole conversation, and relay what it found. A session reviewing its own work is the wrong reviewer.

**When the cut is a podcast episode**, load `content/reference/podcast-edit.md` first and check the episode rules in it:
- the teaser is a teaser, not an intro, and it is shown to the creator as its own file before the full render
- any structural change to an opening is read back as a table and confirmed, then a 60-second opening preview goes to the creator before the full chain runs
- name plates on from the intro through the first minute, and back for the goodbye
- captions in the house style set in `content/taste/editing-rules.md`

Episode edits run through **long-form-editor**, not shorts-editor.

---

## The protocol

Work mechanically. Frame sampling is the tool; your eyes are the instrument.

**1. Ground truth.** `ffprobe` the file: duration, resolution, audio streams, sample rate. Extract a contact sheet at roughly 1 frame per 10 seconds (`fps=1/10` tiles), plus targeted frames at every moment carrying on-screen text.

**2. Run the editing checklist** (`content/taste/editing-checklist.md`), item by item, with a timestamp on every finding. Typical lines:

- on-screen words minimal (keywords, never sentences)
- capitalisation consistent across every card and banner
- number and currency formats in the audience's convention
- step arrows or progress markers on tutorials
- every visual change purposeful
- one call to action, placed where the brief says it goes (the creator's recorded placement, never a framework's default)
- no subscribe interruptions
- **safe area clean on any vertical short:** `python3 .claude/skills/shorts-editor/scripts/check_safe_area.py <cut.mp4>`. No card or caption ink above y=200, below y=1500 (the bottom 22% is covered on every platform), or right of x=940 from y=960 down where the platform's action rail sits, and no face whose mouth and chin sit below y=1500. Exit 1 means fix and re-render. A breach that ships costs a full re-upload, because platforms will not swap the file on a live video.
- **caption size gated:** `python3 .claude/skills/shorts-editor/scripts/check_caption_size.py --style "<style line>" --fontsdir <fonts>`. Exit 1 means raise the size.

If either of those scripts is not there, shorts-editor is not installed. Run the rest without those 2 gates and name both in the verdict as not run.

**3. Run the durable editing rules** (`content/taste/editing-rules.md`). Audio tamed at the loud moments (check `volumedetect`, and listen). Endings keep a beat of tail (check the last 2 seconds of each section against the waveform). The opening is on camera (frame-check 0:00 to 0:05) or whatever the rules say it should be. Livestream cuts keep the live feel. Pace matches the rules, not the tool defaults.

**4. Run the privacy frame check** (standing rule 4). Every frame that will be posted as a still (thumbnail, cover, carousel slide) at full resolution. On a recording with other people or private screens in it, sample at 1 second or finer for exposures. List every finding with a timestamp and the fix (crop, blur, rebuild the surface clean, cut the moment).

**5. Check the cut against the vision handoff.** For each point the creator made about what the great version looks like: is it in the cut? Timestamped yes, no or partial. This is the check that catches an edit which is mechanically perfect and is not the piece they described.

**6. Check the key lines and short beats.** The lines the creator wanted verbatim, and the beats the derivative plan expects to carry short-form clips: intact, or trimmed mid-sentence? Check against the brief's key-lines slot and derivative map.

**7. Check the recording followed its spine.** Each section of the brief's spine present, in the creator's order, under the creator's names. Timestamped yes, no or moved per piece. A cut that reorders the argument is a **vision finding, not a mechanical one.** Flag it and do not rule on it.

**8. Sponsored check** (when the brief says sponsored): every deliverable promised to the sponsor is present, in the agreed form.

**9. Promises on camera.** Any on-camera promise ("link below", "a free resource", "the template") is listed for the launch step, which must fetch each URL and see a 200 before the video publishes. A video that promises a resource it does not deliver reads as clickbait and costs trust.

---

## Output

A fix list, written into the brief under a `## Cut review <n> (YYYY-MM-DD)` heading and given in the conversation at the same time:

- **PASS or FIX per checklist item**, with timestamps on every finding (`3:12 card says "$5.000"`)
- **Privacy findings**, each with a timestamp and the fix
- **Vision scorecard:** each handoff point marked landed, partial or missing
- **Open questions** that ride with the review (consent, choices), each written so the creator can answer it without opening anything
- **One verdict line:** "ready to watch" or "fix list first", with the count

The verdict clears mechanics and says so in those words. Nothing here approves a piece.

When the cut is handed over for the creator's watch, a page with video players on it goes over `scripts/serve_outputs.py` (standing rule 5); a single file goes as its path.

---

## The retro, and it is the point

**Capture it when the review closes, not next week.** After the creator watches and reacts, write their verbatim reactions with timestamps into `content/taste/cut-feedback/` in the format that folder's README sets, and record 2 things here:

- what this gate **missed** that the creator caught
- what it **flagged** that turned out to be fine

A miss that repeats becomes a new line in `content/taste/editing-checklist.md`, dated, in the same session. A false positive that repeats gets softened here.

Timing is the whole mechanism. Attached to a weekly review instead of the moment, feedback lands after the week's pieces have already shipped, and the checklist can never learn faster than 1 rule a week.

---

## Rules learned from real runs (cap about 15, prune the stale)

Seeded from failures proven in shorts-editor's errors table, so this gate starts with what that pipeline learned the hard way.

| Rule | Where it came from |
|---|---|
| **Card type sized for a laptop, not a phone.** The band is read at 375px wide, so a 25px label is 9px in the hand. Minimums: headline 96px, number 180px, supporting label 44px, 6 words maximum per card, no per-row label plus chip lists. Check by cropping one frame per card to the band, scaling to 375px, and reading it. | A 7-row list that looked tidy in review and was unreadable on a phone |
| **A silent lead at the head is stray video, not just dead air.** Transcribers routinely time the first word at 0.00 when the voice starts hundreds of milliseconds later, so the clip opens on whatever the speaker was doing before speaking. Read the first `silence_end` from `silencedetect` as the true onset, then look at frames at 0.0, 0.3 and 0.6. Same check on the tail. | A short that shipped opening on the speaker fixing their hair, onset 0.754s against a transcript that said 0.00 |
| **Duplicates and false starts hide inside one long "word".** Transcribers collapse a repeated take and dead air into a single stretched word (a 4.4s "word" hiding 3.4s of silence), so no gap exists for a silence rule to find. Scan the re-transcribed cut for consecutive duplicate phrases and micro-truncations, then `silencedetect` the original window to find the split. | A 3.37s pause inside what the transcript called one word |
| **`silence_keep` finding 0 silences means a noisy room, not a clean cut.** Above a -40dB noise floor the default threshold detects nothing and 0.5 to 1.1s emphasis pauses survive. Diagnose at `silencedetect=n=-35dB:d=0.35` and hand-write a tight keep list. Never blindly drop to -30 or -32dB, which eats soft word endings. | Documented twice in the shorts-editor errors table |
| **A full-resolution frame check, not a thumbnail glance.** Faces, name labels, private interface. Crop the webcam column off a screen share where possible. | A cleared frame carried a stranger's face and name; another carried a sidebar of private conversation titles |
| **Exposure sweeps sample at 1 second or finer.** A brief flash of a private list survives a 5-second sample. | A 1.8-second exposure that passed an OCR sweep at 5-second spacing |
| **A video board opened as a file shows empty players.** Serve it with Range support. | Review boards whose videos would not play in the embedded browser |

---

## What this skill must not become

Do not build automated audio and video analysis into this gate until `content/taste/cut-feedback/` holds several real reviews showing the checklist missing things a machine could have caught. Then propose it to the creator with the evidence files named. Learn first, automate after, hand off last: that order is in `content/PRINCIPLES.md`. A gate automated ahead of its evidence checks the wrong things confidently.
