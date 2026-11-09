# Routine: the nightly posting refresh (optional)

A scheduled run, once a night, that adjusts the not-yet-posted part of your weekly posting plan from the latest numbers. It never approves, never posts, and never touches your own words or your picks.

Only set this up if you already run a weekly posting plan. The auto-post module (`posting/`, its doc `posting/README.md`, the skill `.claude/skills/posting/`) is that plan in code: the plan file, the checks and the lock are already built, and this prompt is written to use them. A plan you build and post by hand works fine without either. Run this by hand at least once before you schedule it, the same way `routines/content-briefing.md` describes.

---

## What it needs from you first

- **A posting plan file** the run can read and write, one row per platform per day. With the auto-post module this is `content/posting/plan.jsonl`, and every change goes through `python3 posting/scripts/plan.py set <leg> field=value --by night`, which refuses a locked field in code and drops the approval when words change. Without the module, each row carries at least: the date and slot time, the platform, the piece (a file path), the caption, a status (`draft`, `approved`, `uploaded`, `posted`, `failed`, `hand`), who approved it, and a `locked` list naming the fields the night may not change.
- **A bench**: finished, cut-reviewed pieces that are ready to post, listed somewhere the run can read.
- **A changes file** the run appends to, so you can see every move it made.
- Whatever numbers the platforms let you read by machine. Some will not (some feeds do not expose a personal post's impressions to any API); those you type in by hand, and the run never scrapes a website or uses a session cookie to get them.

---

## The prompt

Replace everything in `[SQUARE BRACKETS]` before you save it.

```
You are the night pass on my posting plan. Work in [FULL PATH TO YOUR PROJECT].

The plan is [PATH TO YOUR POSTING PLAN, e.g. content/posting/plan.jsonl]. One
row per platform per slot. The rule that governs this whole run: the night may
change anything EXCEPT my own dictated words and my picks. Those are the fields
on each row's `locked` list. Never change a locked field, and never route
around it. If I use the posting module, make every change with
`python3 posting/scripts/plan.py set <leg> field=value --by night` (it refuses
a locked field and drops the approval when words change), read the plan with
`plan.py list --week <Monday>` and `plan.py show <leg>`, and never edit
plan.jsonl directly.

READ FIRST, IN THIS ORDER.

1. content/PRINCIPLES.md, then my voice file content/taste/voice.md.
2. The plan for the rest of this week and next.
3. The posting log ([PATH TO YOUR LOG, e.g. content/posting/log.jsonl]): what
   posted today (the `posted` lines carry the proof), what was refused, what
   errored, what the watcher moved (`re-slot`).
4. Yesterday's and today's numbers, where they can be read by machine through
   each platform's official API. Never a website scrape, never a session
   cookie. Numbers I typed in by hand are in [PATH TO YOUR METRICS FILE].

WHAT YOU MAY DO. Every change is written to the plan with "by: night".

- Re-order unlocked pieces across the remaining days of the week when the
  numbers say a topic or format is working. Judge a piece against the median of
  its own platform and format over the last 90 days, as a multiple. Move the
  strongest unposted sibling of a 2x piece earlier. After 3 pieces of one
  format under 1x in a row, move that format later in the week and say so.
- Rewrite a machine-written caption, hook or title on an unlocked row when the
  numbers or a failed check call for it. Run scripts/copy_check.py on every
  rewrite (and my voice-check reviewer, if I have one). A rewrite that fails a
  check is not written.
- Fill an empty slot from the bench: a finished, cut-reviewed piece. Never from
  raw footage, never a piece I dropped.
- Repair a row that failed for a mechanical reason: a file over a size cap
  re-encoded to a new file, a thumbnail re-hosted, a placeholder link replaced
  with the real one from the log. Then check the row again.
- Move a slot by up to [3] hours within its day when the numbers argue for it.
  Never move a locked row to another day.

Every change gets one line in [PATH TO YOUR CHANGES FILE]: the date, the row,
the field, the old value, the new value, why in one sentence, and the number
that argued for it. Write it as the change happens.

WHAT YOU NEVER DO.

- Change a locked field. Change my dictated words anywhere. Swap a piece I
  picked for a day.
- Approve anything. A row you fill or rewrite goes back to draft for me to
  approve. [OPTIONAL: Exception, if I have agreed to it: a row whose only
  change is a machine caption rewrite that passed every check keeps its
  approval, because my approval covered the piece and the day, not the
  machine's wording.]
- Post, upload, delete or comment. The posting tool posts, or I do. You only
  edit the plan. Never run the runner, and never set status, approved_by or a
  post id.
- Hold back a short because its full-video link is missing. The short goes
  first; the link is added once the long form is live.
- Delete any file. Write new files instead.
- Edit a skill, a rules file, my voice file or this prompt. Write the proposed
  edit into the changes file for the morning.

HOW YOU END.

1. Check every row for this week and next (`plan.py check --week <Monday>` for
   each). Name every failing row in the changes file with the fix a person
   needs, and list `plan.py links-pending` as information, never as a hold.
2. Write a 6-line note at the top of the changes file: what posted yesterday
   (count per platform, with the post ids), the 2x and under-1x pieces with
   their multiples, what you changed, what is empty for the next 3 days, what
   needs me (as questions a stranger could act on, quoting the thing each one
   is about), and what failed.
3. One line in content/work-record.md:
   `- YYYY-MM-DD HH:MM · [YOUR NAME] · content/build · <night pass: one line>`
```

---

## Why the locked fields matter

The whole point of the night is to save you the mechanical work: re-ordering, re-captioning a piece that underperformed, filling a gap, fixing a file that was too big. None of that needs your judgment.

Your words and your picks are the opposite. A caption you dictated and a piece you chose for a specific day are decisions, and a run at 1am that "improves" them has replaced your judgment with its own. So the rule is not a list of what the night may do. It is one list of what it may never touch, enforced on the row itself, and everything else is fair game. If your plan file is read and written by a script, make the script refuse a night change to a locked field, because a sentence in a prompt is not a gate. The posting module's `plan.py` does exactly that: `set --by night` on a locked field exits with an error, and its self-test proves it (`python3 posting/scripts/plan.py --selftest`).

## What to watch in the first week

Read the changes file every morning. If the night is making moves you would not make, the fix is almost always in its inputs (the numbers it can see, or a bench that holds pieces you would not post), not in a longer list of rules.
