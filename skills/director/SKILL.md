---
name: director
description: >-
  The director before a recording. Runs before every recording session and asks only what the
  brief has not already answered: how the creator wants to come across, the goal, the one
  learning, what the viewer gets, why the viewer should care, a free resource or not, an intro or
  straight in. Prints the must-dos that bear on this video, then writes the answers into the brief
  as the frame the edit serves. Use for - "we're recording", "director", "before we record",
  "recording now", "run the checklist", a recording block on the calendar with no brief behind
  it. NOT the brief interview itself (that is the `content` skill), NOT the cut review (that is
  `cut-review`).
---

> **Metric:** recordings whose brief carried a frame before the camera turned on, out of recordings made. Target: every one. A skill nobody can name a number for is a candidate to retire.

# The director

This skill is a coach in a session: before the creator goes into the flow, it asks the few questions that decide what the video is for, the way a good director or editor asks them in the room. It exists because an editor once asked for exactly this: a checklist that reminds the team, every time, what the viewer is getting and how the creator wants to come across, before anyone hits record.

The questions live in `content/taste/director.md` and are never restated here. Taste is data, skills are engines: change a question there and this skill picks it up.

**Load before any step:**

1. `content/PRINCIPLES.md`, the constitution. When it conflicts with anything in this file, it wins.
2. `content/taste/director.md`, the 7 questions and the frame.
3. `content/taste/must-dos.md`, sections A (before the camera turns on), B (the intro beats) and D (the moment the take ends).
4. `content/taste/kinds/README.md`, which tells the kinds of video apart.

**What it writes:** only the brief it names, one row in `content/work-record.md` and, in page mode, one page beside the video's folder. **What it never does:** send anything, start a render, or write the promise or the spine for the creator. Those belong to the brief interview (`content` skill, section 3, and its `references/interview-stages.md`).

## 1. Find the video and its kind

- The video is the one named in the ask; else the recording block on the calendar with no brief behind it; else ask which.
- The brief is `content/briefs/<date>-<slug>.md`. If there is none, create one with the title, a `Type:` line and an empty frame section, say so in one line, and carry on. The director can run before the interview; the interview fills the rest later.
- The kind: read it off the brief's `Type:` line. If it is not there, ask it first, with the table in `content/taste/kinds/README.md` as the options. Then read `content/taste/kinds/<kind>.md` in full: its opening, pacing and packaging defaults are what the questions carry.
- Optional, if you run several sessions at once: write your claim into `content/in-flight.md` (who, start time, "director on <slug>", the brief you will write). It is a map, never a gate.

## 2. Read before asking

Read the whole brief and the last 3 turns of the conversation. For each of the 7 questions in `director.md`, decide: already answered (quote the answer back in 1 line, with where it came from), or open. **Re-asking an answered question is banned.** Getting asked the same thing twice is where a creator's energy goes, and the interview skill already asked the promise, the spine, what to leave out, the CTA and the titles.

## 3. Ask the open ones, in one batch

One structured question call (if your harness has a structured question tool, use it) carrying every open question, in the phrasing from `director.md`, with headers in plain words ("Come across as", "Goal", "The one learning", "What they get", "Why care", "Free resource", "Intro or straight in"), and an open "something else" field on every one, because that is where people riff.

- Where the kind sheet has a default (a tutorial opens on the finished output; a short's first frame is the packaged promise), the question states the default and asks whether this video keeps it.
- Options are sentences the creator could have said, never a label ("educational", "authoritative"). A label as an answer is a sign the question was not really answered.
- When the creator answers 3 in 1 sentence, take all 3.

**Somebody else in the room** (an editor or producer on set, or "page" in the ask): skip the chat question, build the page in step 6, and come back for the answers afterwards.

## 4. Write the frame into the brief

Under `## The frame (director, asked before the record)`:

- The 7 answers in the creator's words, 1 sentence each, with the date and who asked (this session, or the person on set).
- Then the frame in 3 lines (`director.md`, "The frame, said back in 3 lines").
- Where an answer came from an earlier section of the brief, say so in that line rather than inventing a second wording.
- A missing answer reads `OPEN: <the question>`, never a guess.

Write the file once, re-reading it immediately before you write (another session may have touched the brief in the meantime; a claims file is never the gate, the re-read is).

## 5. Say the frame back, and the must-dos that bear

In chat, 3 lines: the frame. Then the rows of `must-dos.md` sections A and B that bear on this video, each with its number and its receipt, as a short list, with no questions about them: they are rules, not options. One line naming section D: the "what did we miss" questions, asked the moment the take ends, while the set is still up. If the answer to the intro-or-straight-in question was "straight in", say where the name-and-authority beat (section B) now goes instead.

## 6. Page mode (somebody on set)

One light page of big boxes, full width with a fluid side gutter, type 16px or larger, no em dashes:

- a box per open question, with the kind's default under it;
- a box for the frame;
- a box for the must-dos from sections A and B that bear;
- a box for the end-of-take questions from section D.

Build it on your design system (`design-dna`), write it to `content/videos/<slug>/director.html`, run `python3 scripts/copy_check.py` on it, and hand it over. The answers still land in the brief afterwards (step 4), from what the person on set reports.

## 7. Close

- One row in `content/work-record.md`: `YYYY-MM-DD HH:MM · content/build · director on <slug>: <N> asked, <M> quoted from the brief, frame written to content/briefs/<file>`.
- Clear your row in `content/in-flight.md` if you wrote one.

## What this skill never does

- Never asks a question the brief already answers; never asks about a must-do.
- Never writes a label where the creator's sentence should be.
- Never runs the edit, the cut review or the interview. It hands the frame to them: `cut-review` checks the third line of the frame first, and the vision handoff after the recording opens against it.
