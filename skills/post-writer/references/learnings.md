# Learnings

What past posts taught, kept as rules with the reason attached. Read before drafting. Add to it
after every post the creator reacts to.

**An entry holds 4 things:** what happened, what they said about it (in their own words, in your
copy of this file), the rule
that follows, and what it cost. One example gives a guideline. The same correction arriving
twice gives a rule, and a rule that keeps getting broken needs a check rather than a longer
paragraph.

---

## Inside, not outside

**What happened.** A post about a hard stretch of work was drafted with the stat wall as its
spine: usage counts, hours, totals. The body of the post was the dashboard. The creator had
described what the stretch actually felt like, and none of that survived into the draft.

**What they said, in short.** The inside of the experience was the point, not the data about it.

**The rule.** Lead with the felt thing. Numbers are punctuation and never the spine. If the post
can be reduced to a wall of stats and still holds together, the spine is wrong and it gets
rewritten from the inside out.

**Cost.** A full redraft, and a post that would have read as a humblebrag if it had shipped.

---

## No comparison that needs a lookup

**What happened.** The same draft carried "[N] times the length of a famous novel" as the
punchline on a usage count.

**What they said, in short.** No person would know that off the top of their head, so it gave the
machine away.

**The rule.** Any comparison requiring arithmetic, a lookup, or trivia is banned. It only ever
appears when a language model is reaching for impressive. The raw number alone, or no number.

**Cost.** Nothing, because it was caught before it shipped. It would have cost credibility with
exactly the readers who check.

---

## Writerly imagery is a tell

**What happened.** The same draft contained 2 lines of polished, essay-style imagery about
tiredness that nobody would say out loud.

**The rule.** Would they say this sentence out loud, to a friend, across a kitchen table? If it
sounds like an essay, cut it and write the plain version of the same idea. This is the rule that
gets broken most often, because the sentences it kills are usually the ones that felt best to
write.

---

## What worked, in the same pair of drafts

Worth keeping, because a learnings file that only records failures teaches half the lesson.

- An opener anchored to a real artifact they had just made, rather than to a topic.
- One capitalised verb doing the emphasis, in a sentence that was otherwise plain.
- A short, unglamorous verdict as the takeaway, earned by the story rather than announced.
- Leading with the watching and the pattern they had lived, with no stat in the first 3 lines.

---

## Their dictated words are not a draft

**What happened.** The creator dictated a short public reply word for word. The session cut one
word it judged too strong, posted it, and mentioned the cut afterwards.

**The rule.** When they dictate the wording, fix typos, capitalisation and names, add a greeting
if the surface needs one, and change nothing else. A word that looks worth cutting is asked
about before the post goes, because a posted message cannot be taken back.

**Cost.** A public message that said something slightly different from what they meant.

---

## A fixed phrase gets replaced by variety, not by another fixed phrase

**What happened.** One reaction phrase had crept into about a third of a batch of letters. It was
retired and replaced everywhere by find-and-replace with a different phrase, which then sat in
the same third of the batch. Several had already gone out before anybody noticed.

**The rule.** Each letter or post in a batch is individually fine; the problem is only visible
across the batch. Keep a ceiling (no single reaction phrase in more than about 1 piece in 8),
check the batch as a whole before anything is uploaded or scheduled, and fix a retired phrase by
rewriting each piece, never by swapping one string for another.

**Cost.** A batch that read as templated to anyone who received 2 of them.

---

## A rule written for one surface never reached the next

**What happened.** The same voice correction (machine constructions in short copy) arrived again
and again over a few weeks, each time on a surface the previous fix had not named: first
connection notes, then email templates, then a form, then a dashboard. Each fix was written into
the instructions for one kind of artifact.

**The rule.** Keep the named constructions in one place (`voice.md` and this file) and have a
reviewer read that place at run time for every draft on every surface, rather than copying the
rule into each surface's instructions. Phrases somebody wrote down word for word can go into
`scripts/copy_check.py`; constructions need a reader, because a pattern match on a construction
fires on good sentences.

**Cost.** The same correction made by hand about 8 times.

---

## A checker that refuses approved copy is broken

**What happened.** A new mechanical check, added to catch a struck phrase, also refused copy the
creator had written and approved, because the pattern was wider than what they had actually
struck.

**The rule.** Narrow every check to exactly what was struck, and add the approved lines as test
cases that must pass. A checker never rewrites approved copy; it reports and asks.

**Cost.** An afternoon of approved copy flagged as wrong, and nearly rewritten.

---

## 2 people, one event, one post twice

**What happened.** 2 co-hosts drafted posts about the same live session. The drafts shared
whole phrases and the same structure, so anyone following both would have read the same
announcement twice.

**The rule.** The second post gets its own hook, its own structure and at least one line only
that person can say. Measure it: 0 shared 5-word phrases, checked against what the first person
actually posted, not their draft.

**Cost.** A rewrite, caught before it went out.

---

## How to add to this file

1. What did they change? Write the change.
2. Why? Ask them in the same session, and write their answer in their words.
3. Where does the rule belong? If it is about how they sound, it goes in their voice file. If it
   is about how a post gets built, it goes here.
4. What did it cost? An hour, a redraft, a post that underperformed, a reader who noticed.

Keep this to about 20 entries and prune what newer entries have replaced.
