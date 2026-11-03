# AEO: passages an AI answer can quote

> Module of the search-visibility skill. Built on `evidence.md` section 3 and checked on real watch pages. It governs the questions on a watch page and the whole of a blog article. Starting default for where page questions come from: real calls and workshops, not invented FAQs.

## What the evidence supports, and only that

| Finding | Source and label |
|---|---|
| Retrieval rank and query match dominate: a page first in ChatGPT's search had a 58% citation rate, about 14% by position 10; query match was measured as how well the page's **best heading** matches the query; moderate coverage beat exhaustive guides | Indig, 815,000 query-page pairs, reported 2026-04-14. Measured, independent analyst |
| 44.2% of citations came from the first 30% of a page; cited passages were about twice as likely to use definitional language ("X is"); 78.4% of question-linked citations came from headings; cited text averaged 20.6% proper nouns | Indig, 1.2M answers, reported 2026-02-18. Measured, analyst |
| Align the page title, h1 and meta description; question-style h2s with direct answers; lists, steps and tables for how-to content; never hide answers in tabs, PDFs or images; no walls of text | Microsoft Advertising, 2025-10. Official guidance (Copilot and Bing) |
| No special optimisation; make important content available as text | Google AI features doc, 2025-12-10. Official guidance |

**Dropped from the third-party "citability" skills this replaced, because nothing could check them:** a fixed 134 to 167 word passage target; "definition patterns increase citation 2.1x", "statistics +40%", "quotations +115%" (the GEO paper is a 2023 lab benchmark on simulated engines, `evidence.md` section 9); per-engine preference tables; statistical density as a goal (your own real numbers are often client figures that stay private, and an invented statistic is banned outright); and a 0 to 100 score, replaced by the pass-or-fail check at the end.

## The method, per page

### 1. Find the questions people actually asked

- **Sources, in order:** call transcripts and workshop recordings (read from the cleaned transcript, never a raw machine copy with unchecked speaker labels); workshop chat exports; the comments on the video; the video's YouTube search terms (`youtube-seo.md` section 1).
- **Who counts:** a member of your audience, on a call or at a workshop or training. **A co-host, a vendor, a guest who is not part of the audience, or the creator does not source a question** until the creator rules otherwise. A checker pass once took 2 co-host questions off a page for exactly this and held them for a ruling.
- **Check the speaker** on every meeting a question comes from: when a transcript's speaker labels are suspect, check the turn against the recording before the question is used. A bare first name resolves to one person or it is asked, never picked.
- **Match to the video:** keep a question only when this video actually answers it, at a timestamp you can name. A good question the video does not answer is a seed for the next video (`content/seeds.md`, verbatim), never a page question with an invented answer.

### 2. Trace every question privately

A private, git-ignored file (for example `private/content/<YYYY-MM-DD>-page-question-sources-<slug>.md`). Per question: the meeting id and timestamp or the chat export time, the person's role, their words verbatim, the speaker-check status, the video timestamp of the answer, and the route used to find it. Then a section for what was searched and not used, and why. **Names live in this file and nowhere else.** The pack's `asked_in` carries only `status` (`receipted`), `receipt` (the meeting id or chat time), `asked_by` (a role: "customer on a call", "workshop attendee") and a `note` pointing at the private file.

### 3. Anonymize fully

The page never names who asked, their company, their client, a meeting id or a date that identifies a private call. The heading the page prints says only where questions come from, and only what is true: "Questions from our workshops" when every one is a workshop question, "Questions from our workshops and calls" when calls are in it too, "Common questions" when any one could not be receipted. The heading lives in the pack's `questions_heading`, and the renderer prints it as written. A vendor named in the video is masked in the transcript ("[a <category> platform]") unless the creator rules otherwise.

### 4. Word the heading no wider than what was asked

The heading may be tidied into the form someone would search ("Why can't I find the <plugin> in <tool>?"), and it may carry the product name where the asker said "it". It may not broaden the question into a topic the asker never raised, merge 2 askers' questions into one claim, or turn a question about one feature into "How do I set up <tool>?". If the searchable form changes what was asked, keep the narrower one.

### 5. Answer first, from the video

- **The first 1 or 2 sentences answer the question on their own**, naming the subject rather than "it" or "this", with the products and tasks named (the entity density the citations show). Then the detail.
- **Every answer is checked against the video's own words**, with the `timestamp` where the video shows it, linked to `?t=<seconds>`. Spot-check every answer against the caption track before the page ships.
- **Steps as an ordered list, a comparison as a table**, never a wall of text.
- **No number that is not on the tape or sourced**, no client figure, no promise the video does not make. A date-sensitive fact (a plan's retention terms) carries its source and date, in `transcript_notes` (`watch-page.md`).

### 6. Place them where the evidence says they pay

Visible on the page, never collapsed by default; question headings at the h2 or h3 level under one questions heading; the questions block high enough that the page's best heading matches the query (Indig's measure). The intro above everything stays the answer to the page's own question.

## The check before a page or article ships (pass or fail, per question)

| Check | Pass |
|---|---|
| Traced | a row in the private file with its receipt; the asker is an audience member, or the creator ruled them in |
| No wider than asked | the heading means what the asker meant |
| Answer first | sentence 1 answers it alone and names the subject |
| From the video | the answer matches the video at the named timestamp |
| Anonymous | no name, company, client or meeting id in the rendered text or the comments |
| Clean copy | `python3 scripts/copy_check.py <file>` passes; the answers pass a voice read against `content/taste/voice.md` (they are the creator's voice on their own domain) |

A question that fails one check comes off the page, and the trace file says why.
