# The blog article and the Substack post, from one long form

> Module of the search-visibility skill. Starting default: the blog lives on your own website, the newsletter post goes on Substack under the creator's own name. Change either in your taste files.

## The page pair: 2 pages answering 2 different questions

One page cannot do both jobs: video on top makes it a weak article, article on top makes it "a blog post that reviews an embedded video", which Google says is not a watch page (official, `evidence.md` section 2). So each long form with a written question worth answering gets a pair:

| | Watch page (`watch-page.md`) | Blog article |
|---|---|---|
| Job | the video found as a video (video results, key moments) | the written answer to a question people type or ask an assistant |
| Top of the page | the embedded video, the title on the search phrase | a direct 2 to 3 sentence answer, then question headings |
| Body | chapters as links, the full corrected transcript, VideoObject plus Clip | rewritten as a guide: steps, prompts, a table, what to watch out for; never the transcript |
| Title and h1 | the video's phrase ("<tool> for <audience>: ...") | a **different, question-shaped** phrase ("How do <sub-niche> <audience> use <tool> for <task>?") |
| The video | the main content | linked near the top ("watch the 26-minute walkthrough"), or embedded lower down |
| Links | to the article, YouTube, the booking page | to the watch page near the top, related articles |
| Canonical | itself | itself |
| Structured data | VideoObject, Clip, Person, Organization | `Article` or `BlogPosting` with the author `Person` (for Google's understanding; no AI-citation lift is measured, `evidence.md` section 3) |

That the 2 will not compete with each other rests on their different titles and intents and is **untested**; Search Console's position bands for each page are where it would show.

**When one page is enough:** a video with no written question worth answering (a vlog, a podcast clip) gets a watch page only. An existing long text page that already carries everything the video says is the article half of its pair; its watch page is the missing half.

## The blog article

- **The question** goes in the search pack's `blog.question`: a question your audience types, different from the watch page's phrase, and one this video's material answers honestly. Prefer one of the open searches in `geo.md` when it fits.
- **The outline, then the draft**, at the path in `blog.outline_path` (under `content/videos/<slug>/search/`). The AEO method in `aeo.md` governs it whole: answer first, question headings no wider than what people ask, steps as lists, products named, nothing invented, no client figure.
- **Voice:** it is the creator's voice on their own domain, so a voice read against `content/taste/voice.md` runs and `python3 scripts/copy_check.py <file>` passes, then **the creator approves the text** before it can go live.
- **If the site has no blog route yet**, building it once is usually a copy of an existing one-page-per-item pattern (each page with its own title, description, Open Graph and canonical), plus sitemap and `llms.txt` lines. Building the route is a website change: the creator's go.
- **Old drafts and plans** may seed it, but re-read them against today's taste files first: a topic the creator has since ruled out stays out, and whether any old draft seeds the blog is their call.
- **Goes live** with the watch page or after it, never before the video is public, then `geo.md` "On publish".

## The Substack post

- **The account is the creator's.** A session never creates it; until it exists, every card for a Substack post says the account comes first.
- **No machine publishes to Substack.** Its official developer API returns public profile data only, and cookie-driven unofficial "APIs" conflict with the reverse-engineering clause of Substack's Terms. **A person pastes it**, the same shape as any other hand-posted platform.
- **A different, shorter piece, never a copy.** Substack reports no per-post canonical field, so a verbatim copy of the blog article risks Google showing the Substack copy instead of yours. The post is first person, newsletter-voiced (what the creator saw, the one thing to do), and **links to the blog article and the watch page** for the full version.
- **The draft** at the search pack's `substack.draft_path` (under `content/videos/<slug>/search/`): title, subtitle, SEO title, SEO description, slug, the text, the links. The voice read and `copy_check.py` run; the creator approves the words.
- **The leg:** a hand card in your posting queue for the day, carrying the title, the text and the links as one paste, with a calendar block before the slot. The creator pastes and publishes; their word that it went is the record.
- **When:** 1 to 7 days after the pages are live, so your domain is indexed first (the delay's effect is untested).
- **Notes and restacks** are where Substack's own network growth comes from (Substack: recommendations plus the app drive about 50% of new subscriptions, 2024-02-22, platform-wide). Showing up there is a person's time, and whether to spend it is the creator's call, never the machine's.

## What this module never does

Publish to the website without the creator's go; paste, post or schedule on Substack; reuse the blog article's text as the Substack post; describe the business as new or make any claim your `scripts/copy_check.py` bans.
