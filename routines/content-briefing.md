# Routine: the content briefing

One scheduled run, every weekday, before you sit down. It reads what you have already said and already shipped, picks one thing for you to make today, does the work that is only effort, asks you the questions it has, and ends with a single decision you have to make.

It exists to fix consistency rather than quality. Consistency is nearly always the real problem. In our own copy, the complaint that produced this routine was the creator posting once every few weeks and knowing it.

---

## First, the part that trips people up

**Paste this into a scheduled task. `SETUP.md` step 15 is the whole procedure if you have never set one up, including how to check the morning after that it actually fired.**

Every skill in this repo waits until you call it. A routine fires on its own, which is the entire point of this one and the reason it carries a dependency the rest does not.

Before you schedule anything, run it by hand once: open Claude Code in your workspace, paste the prompt below, and read what comes back. A prompt you have never watched run is not ready to fire at 6am while you are asleep. The first run is also where you find out that half the placeholders need your actual answers.

---

## What it is for

The failure it prevents is not a bad draft. It is opening the day with nothing ready, deciding in that moment that today is not the day, and doing that 5 days in a row.

So the run does the part that is effort, and leaves you the part that is judgment. Something is drafted before you arrive. What you do is react to it, answer 2 or 3 questions, and make one call.

The run never publishes. Ever. Drafts and questions are the whole output.

---

## The prompt

Everything between the lines is the prompt. Replace anything in `[SQUARE BRACKETS]` with your answer before you save it. The bracketed items are not decoration; a run that reaches one it cannot resolve will guess, and the guess will be wrong in a way you only notice 3 weeks later.

A scheduled run has no memory of yesterday and no idea what you were doing. Everything it needs is in the prompt or in a file the prompt names by path. That is why this is long.

---

```
You are building my content briefing for today. Work in [FULL PATH TO YOUR PROJECT].
Every path below is relative to that folder.

STEP 0. ONLY ONE RUN A DAY.

Before you read or write anything else, look for the file
content/briefings/locks/content-briefing-YYYY-MM-DD.lock for today's date.

If it exists and was written less than [3] hours ago, another firing of this
routine already owns today. Say that in one line and stop there. No files, no
messages, no work-record row.

If it exists but is older than that, the run that wrote it died. Overwrite it
with the current time and carry on, and say so in one line at the top of the
file.

If it does not exist, create it with the current time inside it, and carry on.
Delete it as your very last action.

STEP 1. START AT THE DOOR.

Invoke the content skill first (.claude/skills/content/). It loads
content/PRINCIPLES.md, the constitution, which wins over anything in this
prompt, plus content/live.md (what is in motion) and content/graveyard.md (what
was deliberately killed). Its hard rules bind this run in full: my words
verbatim, never invent a fact or a timestamp, never pick clips for me, never
send or publish anything.

STEP 2. IF YOU STARTED LATE, BUILD THE WHOLE THING ANYWAY.

A scheduled task can replay an overdue slot hours late, for example when the
computer was asleep. Lateness is never a reason to build less. Do every section
below, however late it is and whatever failed before you.

What a late run owes me instead is one plain line at the TOP of the file: the
time it fired, how late that is, and anything still landing with the time it
will land. Nothing is dropped to keep that line short.

Then check my calendar. If right now falls inside a meeting, write the file but
hold the message in step 6 until that meeting ends, and say so at the top of
the file.

You never decide on your own how thorough to be. If a day does not need the
whole briefing, I will say so in a session.

STEP 3. READ BEFORE YOU THINK.

- My taste files in content/taste/: voice, hooks, packaging, what I will never
  do on camera.
- content/seeds.md, where my own half-thoughts land verbatim.
- content/signal.md, what the weekly mine found.
- content/briefs/, one file per video.
- content/work-record.md, so you know what has already been done.
- [YOUR RECORDING AND POSTING DAYS, e.g. "Tue and Wed record, Tue and Thu post,
  Friday is review day"].
- What is actually live on my channel and my profiles, pulled from the
  platforms themselves. Never from a status file, a spreadsheet or a task row.
  A status file is a claim; the channel is the fact. A search tool that cannot
  find a video is never evidence that it was not published.
- If I run a weekly posting plan, today's slots in [PATH TO YOUR POSTING PLAN].

STEP 4. MISSING WORK IS WORK, NOT A LINE IN A REPORT.

Before you write the file: if something is owed to a recording or a launch
inside the next 3 days and the only thing standing between me and it is effort,
do it in this run and report that it now exists. Research, a packaging pass, a
draft, a rewrite, a seed riff. Do not tell me it has not been done.

Anything needing my judgment stays a question: a promise, a spine, a date, a
packaging pick, anything that sends or publishes.

STEP 5. WRITE THE FILE at content/briefings/YYYY-MM-DD-content.md, in this
order, with THE DECISION last. Everything above THE DECISION is reference I
may skim or skip.

1. TODAY'S JOB. One line: which kind of day this is and what it asks of me.

2. LAUNCH CHECK, on a posting day. What is meant to go out, what is ready, what
   is not. List only the rows where my own notes and the live channel
   disagree, one line each. If a posting plan exists: which slots are
   approved, which are not, which failed yesterday. If I have not posted in
   over a week, that is the lead item and you say so plainly in those words.

3. MY OWN OPEN SEEDS. Up to 3 from content/seeds.md, newest first, one line
   each. A seed sitting untouched for 2 weeks says so. My ideas always rank
   above anything you found or generated.

4. ONE THING TO SAY TODAY, drafted. Drawn from something I actually said, and
   you name where it came from: which seed, which recording, which sentence I
   used on a call. Not a machine-generated idea. If a story in it could carry
   a photo, ask me for the photo.

5. INSPIRATION, real pieces only. 2 or 3 actual videos or posts in or near my
   lane worth me watching before I make something. For each: the title, the
   thumbnail image, the link, and one line on why it is relevant to me. Every
   link verified live before it goes in the file. Never invented, and never a
   description of a piece you did not open.

6. WHAT WAS DONE IN THIS RUN. Anything step 4 produced, with where it is.

7. THE DECISION. The last section, and the only one I have to read. The single
   highest-cost call I have not made, with 2 or 3 concrete options, each one
   quoting the thing it is about, and a labelled default.

   Pick it in this order: first, anything finished or nearly finished that has
   been sitting untouched for more than 3 days, where the question is a date or
   a kill. Otherwise, the oldest question blocking real work.

   Every open question carries "open since [date], carried [n] times". On its
   3rd carry it arrives with a stated default and an expiry: "no answer by
   tomorrow and [default] happens, veto in one word". When an expiry passes, a
   reversible internal call (a pick between 2 cuts, a working title, a format)
   is executed and recorded as decided by default with my veto still standing.
   Anything irreversible (publishing, sending, deleting) is NEVER executed on
   its own. It goes to the top of the message instead. Nothing is carried a
   4th time without one of those 2 outcomes.

FRIDAY IS DIFFERENT. On my review day, skip the prose. Build the weekly
scoreboard as a visual, clickable page instead (the content-waterfall skill's
scoreboard engine): every number the machine can know pre-filled, including
days since my last long-form recording and days since my last publish, both
read from the live channel; the judgment cells left empty for me to fill on the
review. Link it in the file and in the message.

STEP 6. CLOSE OUT.

- Send THE DECISION, and only THE DECISION, to me on [YOUR CHANNEL, e.g. a
  chat DM, an email, a message to yourself]. The file holds everything else.
- Append one line to content/work-record.md, in this exact shape:
  `- YYYY-MM-DD HH:MM · [YOUR NAME] · content/build · <one line saying what
  this run produced>`
  Take the time from the system clock, never from your own sense of it.
- State in one plain line anything you could not reach or could not do. Never
  paste a raw error at me.
- Delete the lock file from step 0.

RULES THAT BIND EVERY RUN.

- Never publish, post, schedule or send anything except the message in step 6.
  Drafts only.
- Never invent a fact, a number, a quote, a timestamp or a link.
- Quote me verbatim when you quote me. Never tidy my words, and never shorten a
  quote without marking the cut.
- Do not hand me a list of machine-generated ideas. One thing, drawn from
  something I said, with its origin named.
- Ask me real questions, the kind that pull something out of me. Not questions
  about scheduling. A question never points at a text it does not show: quote
  the draft, the title or the clip it is about.
- Never pause, shorten or switch off this routine from inside it, and never edit
  this prompt. Count the briefings in a row I have not acted on (no seed
  captured, no decision answered, no default vetoed) and, at 5 or more, open the
  file with one plain line saying so. Whether to change the routine is my call.
- In the first 2 weeks, end the section above THE DECISION with one paragraph
  titled "What this run would change about itself": the one thing that cost the
  most time or produced the least, with a concrete proposal. Proposals only.
```

---

## Why the last section is the only one that has to be read

The first version of this in our own copy produced 24 open issues in one run and got exactly 1 reply. Not because the issues were wrong. Because a person opening a document at 8am cannot make 24 decisions, so they make none and close the tab.

One decision per run, at the end, with the rest held back. If several qualify, the run picks the one that unblocks the most and says in one line what it left out. Everything above that section is reference you may skim or skip entirely, and the routine is written knowing you will.

## Why real pieces instead of generated ideas

The section that used to sit at number 5 was a list of ideas the machine came up with. They never got used, and the creator admitted to never really looking at them. A good system that never gets used is not a good system.

It was replaced with real videos in the same lane: the title, the thumbnail, the link, one line on relevance. A real piece is something you can react to. A generated idea is something you have to evaluate, which is work, which is why it never got done.

There is a second retirement worth copying. The briefing used to end with a friendly daily question, "what has been on your mind for a video", sent as a message. Over 12 days it produced 0 seeds. It was killed and written into the graveyard file so nobody rebuilds it. Ideas arrive in live conversation and on calls, not in reply to a scheduled prompt.

## The failures this prompt is shaped around

None of these are hypothetical. Each one cost a morning in our own copy.

**It fired 3 times in the same second.** Every open copy of the desktop app reads the same task registry and fires the routine independently, so the number of runs equals the number of open windows. 3 sessions read the same files, wrote the same file, and raced each other. That is what step 0 is for. The stale-lock rule is there so a run that died does not block the next day's.

**It ran 9 hours late, straight into a call.** A scheduled task replays an overdue slot whenever the app opens, with no cutoff, so a 5am slot can start at 2pm on a machine that was closed all weekend. That is the calendar check in step 2: a briefing read after the call is worth more than one that lands in the middle of it.

**Then it cut itself short for being late, and nobody had asked it to.** The first fix for lateness told the run to build a 3-line briefing past a cutoff time. The creator got a short briefing on a day that needed the whole thing, and said so: the run should always do the job fully, and anything more urgent gets raised by a person, explicitly. So the run never decides how thorough to be. It builds all of it and says up front what is still landing.

**It reported missing work instead of doing it.** A run found that research it needed had not happened, and said so in 3 separate places, 31 hours before the recording that depended on it. The correction was that the run should be doing the research, not reporting it. That is step 4, and the test in it is the useful part: if the only thing between the workspace and the thing existing is effort, the run spends the effort. If it needs your judgment, it stays a question.

**It switched itself off.** An earlier version paused itself after 5 unread briefings, to save effort on a briefing nobody opened. The creator ruled against it: build in full every weekday, and say plainly how long it has gone unread. A routine that turns itself off is a routine that is gone the week you need it back.

## When to change it

Run it for a week before you touch it. Then change one thing at a time, and change it in this file, because a routine edited only inside the scheduled task is a routine you cannot read, diff or recover.

The number to watch is not how good the drafts are. It is how often you engaged: a seed captured, a decision answered, a default vetoed. The briefing counts that for you and puts it on its first line once it reaches 5. If it stays high for a week, the briefing is firing into a void, and the honest move is yours to make: cut it to the decision alone, move it to a time you actually read it, or turn it off. The run will not make that call for you.

## The optional second routine

If you run a weekly posting plan, `routines/posting-refresh.md` is a nightly pass that adjusts the unposted part of the week from the latest numbers, without ever touching your own words or picks. It is optional; the content-waterfall skill explains the weekly-skeleton idea it belongs to.

## What this routine is not

- Not a publisher. Nothing goes live from a scheduled run.
- Not an idea generator. It works from what you already said.
- Not the door. Every content thought you have during the day still goes through the `content` skill, which interviews you. The briefing is one scheduled visit; the door is open all day.
