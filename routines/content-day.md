# Routine: the content day (optional)

One scheduled run on weekdays that answers a single question: **what does content need from me today?** It reads your recording plan, the cuts waiting on review, your shorts and posting state and every promise still open, sends a few specialist sub-agents to do the checking in parallel, and hands you one short list. Each item on it says what it is, why, how many minutes it takes and the file you act on.

It sends nothing and posts nothing. Ever. The list is the whole output.

This routine is for the `full` install level. It needs the `content`, `director`, `cut-review`, `content-waterfall` and `search-visibility` skills, and it reads your posting plan if you run the `posting` module. On a smaller setup, `routines/content-briefing.md` (one thing to make today) is the better first routine.

---

## Which routine, if you only run one

| You are... | Run |
|---|---|
| Posting rarely and want something drafted for you each morning | `content-briefing.md` |
| Recording several things a week, with cuts in review, shorts on a plan and guests or people you promised things to | this one |
| Both | This one, at a time after the briefing; it never repeats the briefing's decision |

A working channel moved from the briefing to this shape once it had recordings, long-form cuts, a shorts plan and podcast guests all moving at once. Its creator's words for why: content runs best as its own focused conversation, apart from the rest of the business, worked through specialists rather than one session doing everything.

---

## What it is for

The failure it prevents is the thing that slips because nobody looked: a recording tomorrow with no frame written, a cut that waited 3 days for a review nobody started, a short whose full-video link was never added, a guest who was promised their clips and never got them.

So the run does the looking, and leaves you the part that is judgment. Each specialist reads one area and writes what it found. The run puts every item that needs you on one list, in clock order, with minutes, and stops.

---

## How it works, in one picture

```
[your time] the run fires (after you are up, before your first work block)
  -> takes today's lock (only one firing a day)
  -> reads the inputs (calendar, briefs, cuts, posting plan, promises)
  -> decides which specialists have work today
  -> launches them in parallel, 1 message, each with a full brief
       director  cuts  waterfall  posting  promises  (guests, if you host a podcast)
  -> reads each specialist's file, relaunches a failed one once
  -> runs every drafted message through your voice check
  -> builds the list (title, why, minutes, file, what it needs from you)
  -> a separate checker reads the list against the inputs
  -> writes the list, releases the lock, ends on the ready line
```

The specialists are sub-agents inside the run, not separate conversations. Work that continues past today (a cut in review rounds, a guest sequence with steps left) gets a brief written for a conversation you can open later, on your word. The run itself cannot open a conversation for you.

---

## First, the part that trips people up

**Run it by hand once before you schedule it.** Open Claude Code in your project, paste the prompt below, and read what comes back. `SETUP.md` step 15 is the whole procedure for scheduling a task and checking the next morning that it fired. A prompt you have never watched run is not ready to fire while you are asleep.

**Untested as a generic routine.** It is a port of a coordinator routine that runs on one working channel. The shape, the limits and the lessons below come from that channel; your first run is where you find out which inputs your project actually has. Say so in your work log after the first week.

---

## The prompt

Everything between the lines is the prompt. Replace anything in `[SQUARE BRACKETS]` before you save it.

```
You are my content coordinator for today. Work in [FULL PATH TO YOUR PROJECT].
Every path below is relative to that folder. Today is the date on the system clock,
in [YOUR TIMEZONE].

STEP 0. ONLY ONE RUN A DAY.

Look for content/day/locks/content-day-YYYY-MM-DD.lock for today. If it exists and
is under [3] hours old, another firing owns today: say so in one line and stop,
writing nothing. If it is older, the run that wrote it died: overwrite it and say
so in the first line of the list. If it does not exist, create it with the current
time. Delete it as your very last action.

STEP 1. THE RULES THAT BIND THIS RUN.

Read content/PRINCIPLES.md (it wins over this prompt), the profile in
content/profile/, the level in content/setup/preferences.md, and
content/reference/lessons.md. Then these limits, all binding:

- Send nothing on any channel. Post nothing. Upload nothing. Schedule no publish.
  Stage no email draft. Change nothing on a live video.
- Never approve, fill, lock or re-slot a posting leg. Read the posting plan only.
- Titles, thumbnails, clip picks and anything sent to another person are mine:
  propose them as labelled options (A, B, C), never choose.
- You coordinate; you never build. No render, no edit, no new cut. When you catch
  yourself fixing something, stop and write it as an item with its fix.
- Build all of it, however late you start. A specialist with no work today is
  skipped with 1 line saying what it checked; that is not doing less.
- Every sub-agent runs on [YOUR STRONGEST MODEL]. Each one gets the shell rule:
  never rm a path built from a variable or a glob, and every scratch file goes
  under [AN ABSOLUTE SCRATCH FOLDER OUTSIDE THE PROJECT], never inside it.
- A statement about how a tool behaves is quoted from the file that implements
  it, or labelled untested.

STEP 2. THE INPUTS. Read each one and note its state (found, empty, missing) in
content/day/YYYY-MM-DD-journal.md, 1 line each:

- My calendar: recording blocks today and the next 3 working days, and any call
  with a guest or a person I owe something to.
- content/live.md (what is in motion), content/seeds.md (my newest seeds),
  content/briefs/ (one file per video).
- The cuts: every video folder in content/videos/ with a staged cut and no
  cut-review file newer than the cut.
- The posting plan, if I run one: [PATH, e.g. content/posting/plan.jsonl] and
  its log [PATH, e.g. content/posting/log.jsonl]. Read only.
- My channels, read live from the platforms themselves, for what actually went
  out since yesterday. A status file is a claim; the channel is the fact.
- Promises: every on-camera promise in the take notes of videos going live in the
  next 7 days, and every promise to a person in my notes (a clip to a guest, a
  collaborator invite, a resource, a reply).

STEP 3. PLAN THE FAN-OUT. Decide which specialists have work today (the table
below) and write 1 line per specialist in the journal: launched, or skipped with
what was checked. Launch every one that has work in ONE message, in parallel,
each with the common brief below plus its own.

THE COMMON BRIEF (paste into every specialist's prompt):
  "You are the <name> specialist of my content day, working in <project>, date
  <YYYY-MM-DD>. Load the skill named below and follow it. LIMITS: send nothing,
  post nothing, upload nothing, change nothing live, never write a posting leg,
  never pick a title, thumbnail or clip for me (label options instead), no git
  commands, no rm on a variable path, scratch files only under <scratch folder>.
  Any message you draft is marked DRAFT. OUTPUT: write exactly one file,
  content/day/YYYY-MM-DD/<name>.md: a 1-line summary, then 1 section per thing
  you checked (what you read, what you found), then '## Needs me' with 1 bullet
  per item: title · why (1 line with where it came from) · minutes · the file I
  act on · my eye | my pick | my hand. Then '## Continues' (work that needs a
  live conversation after today, or 'nothing'). Then '## Done-test', each test
  with pass or fail. Return under 150 words."

THE SPECIALISTS:

| Name      | Skill            | Its job today |
|-----------|------------------|---------------|
| director  | director         | Every recording in the next 3 working days: the director's questions the brief already answers (quoted), and the ones still mine. A recording with no brief is an item. On a podcast, the conversation comes first: questions for the guest, never audience questions as a gate. |
| cuts      | cut-review       | Every staged cut with no review yet gets one before I watch it. Each review's pass and fix counts in the summary. A cut I edit myself whose master is not where the launch needs it is an item. |
| waterfall | content-waterfall, search-visibility | Every long form approved or live in the last 14 days: the state of each piece (shorts, posts, the search pack). A missing search pack is drafted; titles, thumbnails and live changes are proposals with an undo line, never applied. On Fridays, also scripts/seo_updates.py due, then draft. |
| posting   | none; read posting/README.md | Today's and this week's legs: ready, failing a check, needing my eye or my hand. Every hand card due today. Every short still owed its full-video link. An approval that is not in the copy the poster reads is an item. A video I posted by hand is marked posted only from the channel read. Read only. |
| promises  | content          | Every on-camera promise of a video going live in 7 days is a live URL returning 200 in its description, or an item. Every promise to a person is done (with where) or owed (with a DRAFT of the message). |
| guests    | content (and your podcast prep, if any) | Only if I host a podcast: every guest booked in the next 7 days or recorded in the last 14, each step (brief, reminder, after-call note, recording link, clips sent, collaborator invite) done or owed, owed text drafted, nothing sent. |

STEP 4. READ EVERY SPECIALIST'S FILE. A missing or empty one is relaunched once
with the failure named; a second failure is an item ("the <name> check failed:
<why>").

STEP 5. EVERY DRAFT THROUGH THE VOICE CHECK. Any message text a specialist wrote
goes through my voice check (content/taste/voice.md, and
python3 scripts/copy_check.py on the file) before it reaches the list.

STEP 6. THE LIST. Every item that needs me: title, why (1 line with its source),
minutes, file (the absolute path of the thing I act on: the cut, the rendered
options page, the drafted message; a message is carried in full), needs (my eye,
my pick or my hand). Minutes: 2 for choosing between options, 3 for reading a
caption or description, 6 for a message I edit and send, 3 for a hand post,
the runtime plus 5 for watching a cut, 2 for each director question, else 5.
Order: items with a clock first, in clock order; then whatever blocks a
recording, a person or a slot. Never ranked by how valuable you guess it is.

STEP 7. WRITE THE OUTPUTS.
- content/day/YYYY-MM-DD.md: the first screen (below), then the list.
- [Optional, if design-dna is installed: content/day/YYYY-MM-DD.html, the same
  list as one light page, checked with page_check.py.]
- 1 brief per piece of work that continues past today, at
  content/day/briefs/YYYY-MM-DD-<name>.md: the objective in 1 sentence, the
  specialist file it starts from, the skill to load, the limits above, the
  done-test.

STEP 8. THE FINAL CHECK. One separate checker sub-agent (not you, and on your
most careful model) reads the list, the journal and every specialist file
against the inputs and the limits: every item's file exists, the minutes add up,
no item asks me for something the machine could do itself, nothing was sent or
posted, nothing a specialist found was left off, no title or pick was chosen
for me. Apply its fixes, then rewrite the list.

STEP 9. CLOSE. Append 1 line to content/work-record.md:
  - YYYY-MM-DD HH:MM · [YOUR NAME] · content/build · content day: <n> items,
    <m> minutes, <k> specialists
(time from the system clock). Delete the lock. Print the first screen and end
on the ready line.

THE FIRST SCREEN, about 8 lines:
  Content day · <weekday day month>
  List: <path> · <n> items · <minutes> min
  <1 line per item needing me today, at most 4, clock first>
  Specialists: <n> launched, <n> skipped · final check: <ready | n fixes applied>
  <a late start, a failed specialist: 1 line each when they apply>
  Ready to open: <brief names, comma separated, or none>

The ready line is the last line of the run, in exactly that shape.

WHEN I TYPE IN THIS CONVERSATION, it is no longer unattended:
- Find your question tool on every message (some apps withhold it from a
  scheduled run and hand it over once the conversation reloads).
- Re-check an item before asking about it when over 1 hour has passed since
  the list was written; an item already done is closed, never asked.
- Before any question about a message, write the message out in full in its own
  code box, in a reply that ends the turn; ask on the next turn.
- 4 questions at a time, in the list's order, real choices as options.
- Act on each answer the same turn through the skill that owns the thing, write
  the work-record line, take the item off the list, put up the next 4.
- My word that I already did something is the record; never ask me to prove it.
- A continuing brief is opened as its own conversation only when I say so.
```

---

## The lessons this shape came from

Each one is a real failure on the channel this routine was built on, with the case changed.

- **Sub-agents first, conversations later.** The first version opened a separate conversation per area. A scheduled run cannot open conversations, and 5 open conversations is more than a person tracks. So the run does the day's work through sub-agents and only writes briefs for the work that really continues; the conversations open on the creator's word (2026-11-02).
- **The coordinator never builds.** A coordinator that starts fixing a cut stops coordinating, and the other 4 areas go unread that morning. It writes the fix as an item and hands it to the specialist that owns it (2026-11-02).
- **A conversation that needs the creator asks through the coordinator's question tool**, never a line in a file they have to go and find (2026-11-04).
- **Approvals have to reach the copy the poster reads.** Approvals made on a second computer never reached the one that posts, because it had stopped syncing; their slots passed unposted (2026-11-06). The posting specialist checks it.
- **A hand post is read off the channel.** A board called 3 published videos unposted because the editor uploaded them by hand and nothing read the channel (2026-11-06).
- **The short never waits for the full-video link.** It goes out on its slot and the link is added when the full video is live; the posting specialist lists what is still owed (2026-11-04).
- **On a podcast, the conversation comes first.** The run once asked the host for audience answers an hour before a recording; the host wanted that hour spent on better questions for the guest (2026-11-04).
- **Build all of it.** A run that shortens itself for being late leaves the creator a thin list on the day that needed the whole thing. It says what is still landing instead.
- **Measure it by what shipped.** The number to watch is videos shipped and posts out on their slot per week, and how often you had to chase the same item twice. An item chased twice is a fault in the routine, not in you.

## When to change it

Run it for a week before you touch it, then change one thing at a time, in this file, so the change can be read and undone. If the list keeps carrying items you never act on, cut that specialist. If an area keeps slipping that no specialist reads, add one, with its own done-test.

## What this routine is not

- Not a publisher, a sender or an editor. Nothing goes live, nothing is sent, nothing is rendered from it.
- Not the door. Every content thought you have during the day still goes through the `content` skill.
- Not a ranking of your work. It puts things in clock order and leaves the priorities to you.
