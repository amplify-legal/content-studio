# The file shapes

> Read by `creator-profile` before it writes. Every file in `content/profile/` follows the shape below. `scripts/profile_check.py` checks the parts marked **checked**. The examples are invented; never copy one into a real profile.

## Rules for every file

- **Line 1 is the header line**, a quote block saying what the file holds, who writes it and who reads it.
- **Line 2 is `updated: YYYY-MM-DD`** (checked), rewritten on every change.
- **Their words go in quotation marks**, exactly as said (checked: at least 1 quoted passage in every file except `progress.md`).
- **Every entry is dated**, `(YYYY-MM-DD)` at the end of the line.
- **Open is visible.** `proposed`, `UNKNOWN (asked YYYY-MM-DD)`, `private` and `OPEN: <the question>` are real values. A blank or a leftover `<placeholder>` is not (checked).
- **A change strikes the old line and keeps it.** `~~old line~~ (changed YYYY-MM-DD: their reason)`, then the new line.

---

## `content/profile/progress.md`

```markdown
> What sitting the profile is on, so any session can pick it up. Written by creator-profile after every answer. Read first by creator-profile.
updated: 2026-01-12

| Section | File | State | Last asked |
|---|---|---|---|
| Who | who.md | done | |
| Business | business.md | started | "Think of your last 3 customers..." |
| Objectives | objectives.md | not started | |
| Style | style.md | not started | |
| Inspirations | inspirations.md | not started | |
| Platforms | platforms.md | not started | |
| Summary | summary.md | not started | |

Private file chosen: yes, content/profile/private.md (2026-01-12)

## Open threads
- They started a story about their first paying customer and stopped mid-way. Pick it up in business. (2026-01-12)

## Next question
"Of everyone who watches your content, what do you hope the next step is?"
```

`State` is one of `not started`, `started`, `done` (checked).

---

## `content/profile/who.md`

```markdown
> Who the creator is and how they want to come across, in their words. Written by creator-profile, section 1. Read by content, director, script-writer, post-writer, taste-builder.
updated: 2026-01-12

## In one breath
"I help small bakeries stop guessing what to bake on a Tuesday." (2026-01-12)

## How I want to be described
"Like the friend who actually ran a shop and tells you the boring truth." (2026-01-12)

## What I never want to be associated with
- "The get-rich-quick, rented-car crowd." Why: "it's the opposite of how money works in my world." (2026-01-12)

## What people already praise me for
- "People say I make spreadsheets feel less scary." Last time: a comment on a post in December. (2026-01-12)

## What I believe that most of my space does not
"Most bakeries don't have a sales problem, they have a waste problem." (2026-01-12)

## The moments that made me
1. "The week we threw out 40 loaves a day and I finally counted." What changed: "I started measuring everything." (2026-01-12)

## Never on camera
- My family. (2026-01-12)
```

---

## `content/profile/business.md`

```markdown
> The business behind the content, in the creator's words. Written by creator-profile, section 2. Read by content, director, script-writer, post-writer, content-waterfall, posting. Prices and worth live in private.md when the creator chose so.
updated: 2026-01-12

## What I sell
| Offer | In their words | Buyer (shape, never a name) | Price band |
|---|---|---|---|
| A 6-week course | "the waste course" | owners of 1 to 3 shop bakeries | 100 to 1,000 |
| 1:1 review | "I look at your numbers with you" | the same, after the course | private |

## How a viewer becomes a customer
- Customer 1 (shape: a 2-shop bakery owner): saw a short, followed, joined the newsletter, replied to an email, bought the course. (2026-01-12)
- The step they hope a viewer takes next: "join the newsletter". (2026-01-12)

## What one customer is worth
UNKNOWN (asked 2026-01-12). "I've never added it up." 

## Capacity
"About 10 new course students a month before support gets messy." (2026-01-12)

## What content must never sell or promise
- "Never promise a revenue number." (2026-01-12)

## Proposed, not decided
- A templates pack, "maybe in spring". Decides: the creator. (2026-01-12)
```

The **checked** fields: the "What I sell" section exists (or the file says `no offer yet` in their words), and "What one customer is worth" holds a value, `UNKNOWN (asked ...)` or `private`. When the creator chose private, `private.md` holds the figures and is listed in `.gitignore`; `business.md` says `private` in their place and never a number.

---

## `content/profile/objectives.md`

```markdown
> What the content is for, broad and specific, in the creator's words. Written by creator-profile, section 3. Read by content (every "what should I record" read), content-waterfall, the morning routine at full.
updated: 2026-01-12

## Broad, the next 12 months
"A year from now I want the course to be the thing people in my world recommend without me asking." (2026-01-12)

What content is for, in order: 1 customers, 2 a personal brand. When they conflict: "customers win." (2026-01-12)

## Specific, the next 90 days
| The number | Where I read it | Today | Target | By |
|---|---|---|---|---|
| Newsletter sign-ups from content | the newsletter tool's sources page | UNKNOWN (asked 2026-01-12) | proposed: 150, "but I'm guessing" | 2026-04-12 |

## The one metric this system moves
Pieces shipped a week, with the next step in them. Theirs: "posts that end with the newsletter link." (2026-01-12)

## What I will stop doing
- "Posting on the platform I hate just because everyone says to." (2026-01-12)

## 90-day reviews
- (none yet)
```

The **checked** fields: the 90-day table has a row, and "The one metric this system moves" has something under it.

---

## `content/profile/style.md`

```markdown
> How the creator actually sounds, read off their own past content and confirmed by them. Written by creator-profile, section 4. Read by script-writer, post-writer, shorts-editor (caption clean-up), cut-review. Only confirmed lines are copied into content/taste/voice.md.
updated: 2026-01-12

## The pieces read
| # | Piece | How it was read | Their label |
|---|---|---|---|
| 1 | a link or a file name | watch.py, balanced | proud |
| 2 | ... | pasted transcript | typical |
| 3 | ... | read the text | dislike |

## Confirmed
- Opens by asking the viewer a question. Receipt: piece 1 at 0:02, piece 3 at 0:00. Their words: "Yes, always, it's how I'd start at the counter." (2026-01-12) → voice.md

## Corrected
- ~~Talks fast when excited.~~ Their words: "No, I talk fast when I'm nervous. Slow is excited." (2026-01-12)

## Heard, not confirmed
- Says "here's the thing" before the main point (pieces 1, 2, 4). They said: "not sure, let me think." (2026-01-12)

## What the proud pieces do that the disliked one does not
"In the good ones I'm showing the shop. In the bad one I'm just talking at a wall." (2026-01-12)
```

The **checked** fields: "The pieces read" has at least 3 rows, and "Confirmed" has at least 1 line.

---

## `content/profile/inspirations.md`

```markdown
> Creators and pieces the creator loves and dislikes, each torn down into moves to steal and moves to avoid. Written by creator-profile, section 5. Read by content, media-gen, script-writer, post-writer. Reactions were captured verbatim in content/taste/packaging/inbox.md first.
updated: 2026-01-12

## Loved
### Creator A, a cooking channel (a link)
- Why, their words: "She shows you the mess before she shows you the dish." (2026-01-12)
- Steal: the before shot first, 0:00 to 0:03, then the turn.
- Avoid: "the 2-minute intro about her week."

### Creator B, a woodworking channel (a link)
- Why, their words: "He never explains what he's about to do, he just does it." (2026-01-12)
- Steal: no setup line; the first frame is the first cut.
- Avoid: "the music, it's way too loud."

### A single post by Creator C (a link)
- Why, their words: "One sentence and I had to read the rest." (2026-01-12)
- Steal: a first line that states a number the reader can check.
- Avoid: nothing named.

## Disliked
### Creator D, a business channel (a link)
- Why, their words: "Every title is a fake fight with someone." (2026-01-12)
- The move behind it: a title that invents an opponent.
- Avoid: titles with an invented villain. Seeded into hooks.md, "Hooks I would be embarrassed to use".
```

The **checked** fields: at least 3 under "Loved", at least 1 under "Disliked" (3 is the target; 1 passes so a short sitting is not failed).

---

## `content/profile/platforms.md`

```markdown
> Where the creator posts, where they want to, and the time they really have. Written by creator-profile, section 6. Read by the level recommendation, content-waterfall, posting (at full).
updated: 2026-01-12

## Now
| Platform | How often | Format | Working? (their read) | A number they read |
|---|---|---|---|---|
| a video platform | 1 a week | 8 to 12 minute videos | "the tutorials, not the vlogs" | UNKNOWN (asked 2026-01-12) |

## Wanted
- a short-video platform, "in the next 3 months". (2026-01-12)

## Time, in a real week
| Recording | Editing | Writing | Posting | Total |
|---|---|---|---|---|
| 2 h | 3 h | 1 h | 0.5 h | 6.5 h |

Their words: "6 hours, and that's being generous." (2026-01-12)

## Who helps
"Nobody yet. Maybe an editor in the summer." (2026-01-12)

## Tools already in use
- the phone camera, a desktop editor, a scheduler for the newsletter.

## Posting
By hand, or by machine after approval: "by hand for now." (2026-01-12)
```

The **checked** fields: "Now" or "Wanted" has a row, and "Time, in a real week" has a total.

---

## `content/profile/summary.md`

```markdown
> The 1-page version of the creator profile. Rebuilt by creator-profile from the 6 section files, never edited on its own. Read first by content, director, script-writer, post-writer, taste-builder.
updated: 2026-01-12
confirmed: 2026-01-12

**Who:** "I help small bakeries stop guessing what to bake on a Tuesday."
**Business:** a 6-week course for owners of 1 to 3 shop bakeries; the next step for a viewer is the newsletter; one customer's worth is UNKNOWN.
**12 months:** "the course is the thing people in my world recommend without me asking."
**90 days:** newsletter sign-ups from content, target proposed at 150 by 2026-04-12.
**The one metric:** posts that end with the newsletter link, per week.
**Style, confirmed:** opens with a question to the viewer; slow means excited; shows the shop, never talks at a wall.
**Steal:** the before shot first. **Avoid:** titles with an invented villain; long intros.
**Platforms and time:** 1 video platform now, 1 short-video platform wanted; 6.5 hours a week; no helper.
**Every skill now optimises for:** customers over views, and the newsletter as the next step.

## Open, as questions
- What is one customer worth to you over their whole time as a customer? Yours to answer; until then the system cannot weigh a lead against a view.

## Recommended level
**lite**, because: 6.5 hours a week, no editor, posting by hand, and the video edit happens in your own editor today. Upgrade to standard when you want the system to cut your videos and make shorts. (2026-01-12)
Chosen at setup: lite. Matches.
```

The **checked** fields: `confirmed: YYYY-MM-DD` on its own line (it is written only after the creator says yes), and a "Recommended level" naming `lite`, `standard` or `full`.

---

## `content/profile/private.md` (only when they chose it)

Same shape as the money lines of `business.md`. Add `content/profile/private.md` to the project's `.gitignore` the moment the file is created, and check it with `git check-ignore content/profile/private.md` (it prints the path when ignored). Never print its figures back into chat.
