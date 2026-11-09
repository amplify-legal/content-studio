---
name: creator-profile
description: >-
  The content deep dive: a conversation, never a questionnaire, that learns who the creator is
  and how they want to come across, the business behind the content (what they sell, to whom,
  the price band, how a viewer becomes a customer, what one customer is worth), their broad and
  specific objectives, their style (read off their own past content and played back for them to
  confirm), their inspirations torn down into what to steal and what to avoid, and their
  platforms and time budget. Runs in sittings they can stop and resume; state lives in
  content/profile/. Writes content/profile/ in their own words, seeds the taste files, ends with
  a 1-page summary they confirm and a recommended install level with the reason. Use for -
  "start my profile", "the deep dive", "pick up my profile", "who am I as a creator", "what is
  my content for", "read my old videos and tell me my style", "here are creators I love", the
  first sitting of any install, "my business changed", "update my objectives", "which level
  should I be on". NOT for writing content (content, script-writer, post-writer). NOT for the
  full taste interview (taste-builder, which this skill feeds).
---

> **Metric:** the share of later drafts the creator accepts without a "that is not me" correction. A profile that does not move that number is a questionnaire with a nicer name.

# Creator profile (the deep dive)

**Load before any step:**

1. `content/PRINCIPLES.md`, the constitution. When it conflicts with anything here, it wins.
2. `content/profile/progress.md`, if it exists. It says where the last sitting stopped.
3. `content/setup/preferences.md`, if it exists. It holds the level they picked and the platforms they named, so you never ask those again.
4. `reference/question-bank.md` beside this file: what each section is trying to learn, the opening question, the follow-ups, the push-backs.
5. `reference/file-shapes.md` beside this file: the exact shape of every file this skill writes.
6. `reference/levels.md` beside this file, at the end only: how to recommend an install level.

If one is missing, say which in one line and carry on with the rest.

**What this skill writes:** `content/profile/` (`who.md`, `business.md`, `objectives.md`, `style.md`, `inspirations.md`, `platforms.md`, `summary.md`, `progress.md`), seed lines in `content/taste/` where an answer bears on a taste file, and one row in `content/work-record.md` per sitting. **What it never writes:** content of any kind, a post, a script, a title. It never sends anything and never posts anything.

**Say once, at the start, why this exists.** Every skill after this one drafts in the creator's name. A draft built on a stranger's guess about their business, their buyer and their goal reads like a competent stranger wrote it. This sitting is where the system stops guessing. Then stop selling it.

---

## Posture (all of it is hard)

1. **A conversation, never a questionnaire.** One question at a time, then stop talking. If they answer 3 questions in one sentence, take all 3 and never ask them again. If they go somewhere better, follow them and come back to what is still open.
2. **Their words, verbatim.** Write their sentence as they said it, filler included. A profile written in your prose describes a person you imagined.
3. **Ask, never assume.** A price, a customer's worth, a conversion path, a target number: these are asked, every time. If they do not know, the file says `UNKNOWN (asked YYYY-MM-DD)`. You never estimate one, never fill one from "typical for the niche", and never round one.
4. **Push past the generic answer once.** "I want to help people" and "authentic" are not answers yet. Ask for the last specific instance: the last customer, the last comment, the last piece that worked. One push, then accept what they give.
5. **Keep open what they leave open.** "Probably", "I'm thinking about", "maybe next year" are written as `proposed`, with who decides. Never stamp a goal on them they did not set.
6. **Write as you go.** Every answer lands in its file before the next question. A sitting that interviews for 40 minutes and writes at the end loses everything when the laptop closes.
7. **Never rank them or judge them.** You hold the profile. You do not form it. You may offer one view, once, saying what it is built on (see "Have a view, once" in the content skill), then record their call.
8. **Private stays private.** Before the business section, ask one question: do prices, revenue and customer worth go in `business.md`, or in `content/profile/private.md`, which is kept out of git? Do what they say. Never print a real figure back into chat once they chose private.

---

## Sittings, and how to stop and resume

The deep dive is 3 sittings. They can do them in one evening or across a week, in any order, and stop mid-question.

| Sitting | Sections | About |
|---|---|---|
| 1 | Who, business, objectives | 25 to 35 minutes |
| 2 | Style (their own past content), inspirations | 30 to 45 minutes, plus reading time while they wait |
| 3 | Platforms and time, then the summary and the level | 10 to 20 minutes |

**At the start of every sitting:**

- Read `content/profile/progress.md`. If it exists, say in 2 lines where they stopped and what is next, then ask the next question. Never re-ask an answered one. Read the section's file first and quote back the line that answers it if you are unsure.
- If it does not exist, create `content/profile/` and `progress.md` (shape in `reference/file-shapes.md`), say which sitting this is and roughly how long it takes, and ask whether they want to start with who they are or with the business. Recommend "who" if they have no preference.

**Whenever they stop** ("I have to go", "pause", "stop here", or 15 minutes past the sitting's time), update `progress.md` before anything else: each section's state (`not started`, `started`, `done`), the last question asked, any thread they opened that is not finished, and the exact next question. Then tell them in 1 line how to resume: say "pick up my profile".

**Never chase.** A sitting not finished is not a failure and is never put to them as one.

---

## The sections

The questions, follow-ups and push-backs for each section are in `reference/question-bank.md`. What follows is what each section must leave behind, and where it lands.

### 1. Who they are and how they want to come across, into `who.md`

Leaves behind: who they are in one sentence their way; how they want a viewer to describe them to a friend; what they never want to be associated with; what people already praise them for; the one thing they believe that most people in their space do not; 3 to 5 moments that made them who they are on this subject.

Seeds: the praise and the belief go into `content/taste/voice.md` "The register" only as quotes they confirm. The moments go into `content/taste/stories.md` "The named stories" as story stubs (what happened, in their words; cleared for: `not yet`). The one-sentence version goes into `content/taste/bio.md` "Short version" marked `proposed (creator-profile, YYYY-MM-DD)`.

### 2. The business, into `business.md`

Leaves behind: each thing they sell, in their words; who buys it (the shape of the buyer, never a named customer); the price band, or `private` or `UNKNOWN`; how a viewer actually becomes a customer, step by step, read off their last 3 real customers where they can remember them; what one customer is worth to them, or `UNKNOWN`; how many new customers they can take on in a month; anything content must never sell or promise.

Some creators have no offer yet. Then the file says so in their words, records what they might sell and when, and the objectives section carries the weight. Never invent an offer for them.

Seeds: the path from viewer to customer becomes the close in `content/taste/must-dos.md` row 16 and the link order in row 22, both marked `proposed` until they confirm the wording. Any customer story with a result goes into `content/taste/stories.md` with its receipt, or `UNSOURCED`.

### 3. Objectives, broad and specific, into `objectives.md`

Leaves behind:

- **Broad, 12 months:** what has to be true a year from now for this year of content to have been worth it, in their words. What content is for, in order: audience, leads, a launch, a personal brand, a community, or something else. If 2 pull in different directions, ask which wins when they conflict.
- **Specific, the next 90 days:** the one number they will measure, where they read it, its value today (asked, or `UNKNOWN`), the target they name, and the date.
- **The one metric the system moves:** the number this system is judged on week to week. It is usually a leading number the creator controls (pieces shipped, booked conversations from content, newsletter sign-ups), not a vanity number. Propose one, say why, and write theirs.

Seeds: the answer to "views or customers" goes at the top of `content/taste/README.md`, "What I am actually trying to get out of this", verbatim, if that section is still a placeholder.

### 4. Style, read off their own content, into `style.md`

This section is a playback, not a question. Ask them for 3 to 10 links or files of their own past content: ideally 2 they are proud of, 2 that are typical, and 1 they dislike. Then do the reading while they wait, and play back what you heard.

How to read each piece, by what is installed:

| The piece | How |
|---|---|
| A written post, an article, a newsletter, a caption | Read it. If it is a URL you cannot fetch, ask them to paste the text |
| A video or a podcast, with the `watch` skill installed (standard and full) | `python3 .claude/skills/watch/scripts/watch.py "<url-or-path>" --detail balanced`, then read every frame it prints next to the transcript. `--detail transcript` when only the words matter |
| A video, at lite with no `watch` | Ask them to paste the transcript or the script they recorded from. Or offer the one no-key extra at lite: copy the `watch` skill, `pip install yt-dlp` and install `ffmpeg` (`watch.py` refuses to start without it), then run `watch.py` with `--detail transcript`, which reads public captions with no key (per `skills/watch/SKILL.md`, "Where the transcript comes from") |

**Confirm the speaker before you read a word as theirs.** A transcript line is not proof of who said it. On a piece with more than one voice, ask which voice is theirs, or check whose mouth moves in the frames.

Then play back, one observation at a time, each with its receipt (a quote with its timestamp or its line):

- the phrases they repeat across pieces, quoted;
- how they open and how they close;
- pacing: words per minute where you have a timed transcript (words divided by minutes of speech, and say that is how you counted), sentence length, pauses;
- energy and delivery, from the frames where you watched (framing, gesture, where they look), never guessed from words alone;
- what the pieces they are proud of do that the one they dislike does not.

Each observation is a question: "In 4 of your 6 pieces you open by asking the viewer a question. Is that on purpose?" Their answer is the record. **Only a confirmed observation goes into `content/taste/voice.md`**, marked `confirmed in creator-profile, YYYY-MM-DD`. An unconfirmed one stays in `style.md` under "Heard, not confirmed". A corrected one is written as they corrected it, with your version struck and visible.

Seeds: confirmed phrases into `voice.md` "The register"; their own openings that landed and died into `content/taste/hooks.md` "My openings that landed, and the ones that died".

### 5. Inspirations, into `inspirations.md`

Ask for 3 to 10 creators or pieces they love, and why, and then 3 they dislike, and why. **Capture each reaction verbatim first**, into `content/taste/packaging/inbox.md` with `by:` naming them and the date, before any teardown. The link is a pointer; the reason they sent it is the part worth keeping.

Then tear each one down (with `watch` where installed, `--hook` for the opening; or from the text, or from what they describe), into 2 short lists per piece:

- **What to steal:** a move, never the words. Specific and with a timestamp: "opens on the finished result before any setup, 0:00 to 0:04".
- **What to avoid:** what they said put them off, in their words, and the move behind it.

Play each teardown back in 2 lines and ask if it is what they meant. Write their version.

Seeds: the loved pieces that stopped them mid-scroll go into `content/taste/hooks.md` "What I clicked on, and whether it delivered" if it still has fewer than 3 entries. A thumbnail or title move they want to steal goes into `content/taste/packaging.md` as a `proposed` line. The dislikes go into `voice.md` "What I hate in other people's writing in my field" and `hooks.md` "Hooks I would be embarrassed to use".

**Never copy an identity.** Inspiration teaches moves. If the teardown starts to describe who they should become, stop and go back to section 1.

### 6. Platforms and time, into `platforms.md`

Leaves behind: where they post now (per platform: how often, what format, what they think is working, and any number they can read off their own analytics, asked); where they want to post; the hours a week they really have, split into recording, editing, writing and posting; who helps them (an editor, an assistant, nobody); the tools they already use; and whether they post by hand or want posting done by machine.

Platforms already named in `content/setup/preferences.md` are quoted back, not asked again.

Seeds: none in the taste files. `platforms.md` is what the level recommendation and the posting module read.

---

## The end: the summary and the level

When all 6 sections are `done` (or they say "summarise what you have"):

1. **Write `content/profile/summary.md`**, 1 page, shape in `reference/file-shapes.md`: who in 1 line, the business in 3, the 12-month line and the 90-day number, the one metric, style in 3 confirmed lines, the top 3 moves to steal and to avoid, platforms and hours, what every skill will now optimise for, and every open item as a question a stranger could act on.
2. **Show it in full in chat** and ask: "Is this you? Correct anything, in your words." A correction is written into the section file first, then the summary is rebuilt. Never edit only the summary.
3. **When they say yes**, write `confirmed: YYYY-MM-DD` at the top of the summary. Never write it on silence.
4. **Recommend an install level**, following `reference/levels.md`: the level, the reason in 2 lines built on their own answers (hours, platforms, whether they edit, whether they want posting by machine), and what they would gain or skip. Compare it to `content/setup/preferences.md`. If it differs, say so plainly and offer the change ("upgrade me to standard" runs `SETUP.md` for that level). If it matches, say so in 1 line. Their choice is recorded either way.
5. **Run the check:** `python3 .claude/skills/creator-profile/scripts/profile_check.py content/profile`. Each `MISSING` line prints the sentence to say back in the same conversation.
6. **Close:** one row in `content/work-record.md`:

```
- YYYY-MM-DD HH:MM · <who> · profile/build · creator-profile sitting <n>: <sections done> → content/profile/
```

Then point them at the next skill (`taste-builder` round 1, which now starts from the profile and asks less) and stop.

---

## Keeping it current

The profile is a living record, not a form filled once.

- **"My business changed", "new offer", "new goal", "I'm on a new platform":** open only that section, read its file, ask what changed, write the change dated with the old line struck and visible, rebuild the summary, ask for the confirm again.
- **Every 90 days**, when the specific objective's date arrives, the next session that reads `objectives.md` asks one question: what did the number do, and what is the next 90-day number? Write both. This is a question to ask, never a report to file.
- **A correction from any other skill** ("that is not who I am", "I don't sell that anymore") lands here in the same session, in the right section file, and the session says which file.

---

## What this skill will not do

- Fill a field with a guess, an industry average, or a number they did not say.
- Write an observation about their style into `voice.md` before they confirm it.
- Tell them who to be, what to sell, or what to charge.
- Turn into a list of 30 questions on one screen.
- Write anything public, post anything, or send anything.
