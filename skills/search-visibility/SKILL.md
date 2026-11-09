---
name: search-visibility
description: >-
  The search engines behind the content waterfall, never a door: YouTube SEO, the watch page,
  AEO, GEO, the blog article and the Substack post. It works out the searched phrase, builds
  the search pack (chapters from 0:00, the description, tags, language, the captions file, the
  playlist), the watch-page content pack, the blog question and the Substack draft, makes live
  fixes that each carry an undo line, and reads the weekly search measure. Called by
  content-waterfall (at the brief, at the waterfall hook when a cut is approved, and at the
  Friday scoreboard); it runs only when that skill calls it. Triggers when routed here - "make
  this findable", "search pack", "chapters", "tags", "watch page", "are we showing up in
  search". NOT for posting, NOT for deploying the website, and NOT for choosing titles and
  thumbnails (it proposes them; the creator picks).
---

# Search visibility (YouTube, SEO, AEO, GEO)

**Load before any step:**

1. `reference/evidence.md`, the bottom line and section 9 at least. **It wins over every other source**: a blog post, a vendor, an SEO plugin you installed, your own memory.
2. The module file for the job (table below). Never load all 5 for a one-module job.
3. `content/PRINCIPLES.md` (the constitution) and your taste files in `content/taste/` already govern; this skill restates neither.

**Metric:** the weekly search measure in `reference/geo.md` (on how many of your fixed queries your videos and pages are found). It is the 1 number this skill moves; a skill nobody can name a number for is a candidate to retire.

## Why it exists

Search tricks are cheap to install and hard to prove. A workspace can collect dozens of SEO and GEO skills and still not move, because the skills never run inside the real workflow and their figures come from nowhere anyone could check. So this skill keeps only what a dated evidence file supports, and it runs **only when content-waterfall calls it**: the execution is the waterfall, and a better skill does nothing if the waterfall does not use it.

**The shape that started it:** on the channel this was built on, the one video whose title was the exact phrase people type drew most of its views from YouTube search, and the other videos drew almost none. The single difference was the title. Measure your own channel the same way before you change anything (`reference/geo.md`, the weekly measure).

## The call points (content-waterfall owns when; this skill owns how)

| Called from | What it asks this skill for | Module | Output |
|---|---|---|---|
| The brief (before recording) | The searched phrase offered as one of the honest title framings, and the searches nobody owns yet that fit this video | `youtube-seo.md` (the phrase), `geo.md` (the open searches) | 2 lines in the brief: `phrase:` and `open searches:` |
| **The waterfall hook** (per long form, when the cut is approved) | The search pack, the captions file, the live fixes, the watch-page content pack, the blog question and outline, the Substack draft | all 5 | `content/videos/<slug>/search/` (contract below) |
| The scoreboard (Friday) | The weekly measure and how to read it | `geo.md` | a trend line on the Friday board |
| The scoreboard (Friday), same sitting | What Google changed in Search this week | `geo.md` ("Google's own changes, weekly"), run with `scripts/seo_updates.py` | `content/seo-updates/<date>.html` and 1 line on the Friday board |

## The modules

| Module | File | What it produces per video | Human pass |
|---|---|---|---|
| YouTube SEO | `reference/youtube-seo.md` | the phrase, 3 title candidates, chapters from 0:00, the phrase lines of the description, tags, language, the captions file, the playlist | The creator picks the title and the thumbnail; the rest the machine fixes and reports |
| Watch page (SEO) | `reference/watch-page.md` | `watch-page.json` and the rendered page: video first, one h1, every word in static HTML, VideoObject plus Clip | The creator's go before it goes live |
| AEO | `reference/aeo.md` | question headings with direct answers, from real calls and workshops, traced privately | The creator rules on any question that did not come from a member of the audience |
| GEO | `reference/geo.md` | on publish: sitemap, IndexNow, Bing, Brave, Search Console; weekly: the fixed-query measure; off-site mentions as seeds | Sign-ins and form submits are a person's; nothing off-site is ever sent |
| Blog and Substack | `reference/blog-substack.md` | a blog article answering a different question than the watch page; a shorter Substack piece linking home, as a hand card | The creator approves both and pastes the Substack post by hand |

## The shared contract

**The search pack**, one per long form: `content/videos/<slug>/search/search-pack.json`

| Field | What it holds |
|---|---|
| `slug`, `video_id` | the video folder name and the YouTube id (null before upload) |
| `phrase` | the searched phrase: the core term, then a comma and the sub-niche when the video serves one (`youtube-seo.md` section 1) |
| `title_candidates` | proposals only; titles and thumbnails are the creator's pick |
| `description` | the full YouTube description: the phrase at the top, your own link block right under it, the watch-page link once it exists, the chapters, the links (`youtube-seo.md` section 4) |
| `chapters` | `[{start_seconds, label}]`, the first at 0, each at least 10 s, at least 3 |
| `tags`, `default_language` | a list; the language code (for example `"en"`) |
| `captions_path` | an `.srt` under the same `search/` folder, or null |
| `playlist_id` | the topic playlist, or null until it exists |
| `watch_page` | `{proposed_url, content_path}` (content_path is `content/videos/<slug>/search/watch-page.json`) |
| `blog` | `{question, outline_path}` |
| `substack` | `{draft_path}` |

Whatever posting queue you use should read `tags`, `description`, `chapters` and `playlist_id` from this file onto a YouTube upload that has none of them yet, so the pack is the one place these fields are written. The watch-page content pack's keys are listed in `reference/watch-page.md`; never rename a key once a renderer reads it.

**One script ships with this skill: `scripts/seo_updates.py`, the weekly read of what Google changed in Search** (3 public sources, no key, no sign-in; `python3 scripts/seo_updates.py --selftest` runs offline). On the Friday measure: `python3 scripts/seo_updates.py due`; when it prints `due`, `draft --date <today>`, then write a `meaning`, `owner` and `action` line on every item tagged as yours in `content/seo-updates/notes/<today>.json` (or clear its tag with a `why_not`), then `render --date <today>`, which refuses while a tagged item has no meaning line and writes `content/seo-updates/<today>.html`. It sends, posts and deploys nothing. Every other step is written in its module so a session can do it by hand, or you can script it against the YouTube Data API (or your tool of choice). If you do script it, give every write command a dry-run mode that prints each change, an apply mode that writes one change at a time with one undo line each, and an undo command that reads an undo line back. Then put the script's own `--help` in front of anyone you tell what it does: a statement about how a tool behaves is quoted from the tool, or labelled untested.

## Hard rules

1. **The evidence file wins.** These popular claims are not supported by it, and no output here leans on them (`reference/evidence.md` sections 3, 4 and 9):
   - **llms.txt** gets you cited by AI: no correlation across about 300,000 domains (SE Ranking, 2025-11-07); Google says no AI text file is needed (2025-12-10). If your site serves one, leave it and add a line when a page goes up because it costs nothing; invest nothing more.
   - **Schema markup** gets you cited by ChatGPT or AI Overviews: no lift in a 1,885-page controlled study (Ahrefs, 2026-05-11); chatbots read visible HTML only on a direct fetch (searchVIU, 2025-10). VideoObject and Clip stay, **for Google's video features and key moments only**.
   - **"YouTube is X% of AI citations"**: vendor figures run from 1.9% (Profound) to 29.5% (BrightEdge) because they measure different things; YouTube citations concentrate in Perplexity and AI Overviews, and Gemini 0.2% and Copilot 0.5% of them (OtterlyAI, 2026-03-02). Never quote one figure as the share.
   - Also unsupported: tags drive discovery (YouTube says minimal role); uploaded captions boost ranking (a hypothesis; they are done for accuracy); new videos settle in 24 to 72 hours; "GEO raises visibility 40%" (a 2023 lab benchmark); write the ultimate guide (moderate coverage beat exhaustive, Indig 2026-04).
   - Figures that circulate in third-party SEO and GEO skills with no checkable source are not used anywhere: a fixed "134 to 167 word" passage target, "92% of AI Overview citations come from the top 10", per-engine preference tables, a 0 to 100 citability score.
2. **Titles and thumbnails are proposals; the creator picks.** `title_candidates` go on the video's pick board with rendered thumbnails beside them (`content/taste/thumbnails.md`): the thumbnail and the title are one story, and a thumbnail is never proposed in words. Nothing here ever writes a live title or thumbnail.
3. **The machine fixes captions, chapters, the playlist, tags and description lines on live videos, with an undo list, and reports after** (a starting default you can change to "ask first"). Always dry-run first and read every change; then apply; then one plain report listing each change with its undo line. A description edit sends back every other snippet field it read (on the YouTube Data API, `videos.update` replaces the parts you send, so a partial snippet can wipe the title, tags or category). A read straight after a write can serve the old version, so a stale read-back is retried before it is called a failure.
4. **Nothing goes live on your website without the creator's go.** The watch page's open design calls (`reference/watch-page.md`) are theirs, and a local copy of the website repo can be behind the live site, so reconcile it before any page goes up.
5. **Questions on your pages come from real calls and workshops, are fully anonymized, are traced in a private sources file, and are worded no wider than what was asked.** A question from a co-host, a vendor or anyone outside the audience is held until the creator rules. Method: `reference/aeo.md`.
6. **Off-site mentions are seeds, never sends.** A podcast host to ask, a forum thread worth answering, a publication to pitch: a verbatim line in `content/seeds.md`, never a message.
7. **A statement about how a tool, page or platform behaves is quoted from its source (the help page, the docstring, the API reference), or labelled untested.**
8. **The content system's standing rules apply unchanged:** no client or customer named, every number sourced (`content/taste/stories.md`), every on-camera promise a live URL returning 200 before publish (`content/taste/must-dos.md`).
9. **A live id, link or price is re-read from its source immediately before anyone acts on it**: a pack built yesterday can carry a video id that changed overnight.

## What a run leaves behind

- The files in the contract, under `content/videos/<slug>/search/`.
- The question trace in a private, git-ignored file (for example `private/content/<YYYY-MM-DD>-page-question-sources-<slug>.md`); names live there and nowhere else.
- For live fixes: the undo lines and the report.
- A line in `content/work-record.md` per meaningful unit, and the video's state in `content/live.md` (content-waterfall's record step).

## Person-only steps (asked last, after everything around them is done)

- **Google Search Console:** connecting or relinking it is a Google sign-in.
- **Bing Webmaster Tools:** a sign-in (it can import the Search Console property).
- **Brave URL submission:** a web form; a person submits it, or the session after the creator's go in that session.
- **The Substack account:** created by the creator, under their own name as the starting default.
- **The IndexNow key file** goes on the website, which is a deploy and needs the creator's go.

## Rules learned from real runs (each names the file it changed)

- **When an instruction says "update" and no current version exists, ask before the write.** A run read "update the old contact lines" as a drop, because no newer version of the line existed anywhere on record, then reported it as "updated"; a contact line came off several live videos. A drop is never reported as an update. (`reference/youtube-seo.md` section 4)
- **The voice read runs on every new description line before the live apply.** A run put dozens of new description openings live before the voice check (a nested call hit a spending limit), the check ran afterwards and about a third were rewritten live. A build that cannot run the voice read stops at the dry run and says so. (`reference/youtube-seo.md` section 4)
- **A phrase check that forces the phrase into every line produces stuffing.** The second phrase line carries the core term only where it fits a sentence. (`reference/youtube-seo.md` section 1)
- **Never split the phrase on a separator that appears inside the phrase itself** (a phrase like "<tool> for <audience>" already contains " for "); use a comma. (`reference/youtube-seo.md` section 1)
- **A cut's "full version" link is checked against the caption tracks before it is kept.** A short cut's description once linked the wrong full session; the captions matched a different one. (`reference/youtube-seo.md` section 4)
- **A live apply lists every write it plans, by kind, and a kind the run was not asked to make is held and asked.** A run sent to fix one description would also have uploaded a caption track, because the pack carried a captions file path; the dry run caught it (2026-11-04). An ask to fix the description is not an ask to replace the captions, even where rule 3 lets the machine fix captions. (`reference/youtube-seo.md` section 4)
- **Captions corrected by rule still get a hand read before upload.** A by-rule pass on one long video was followed by a hand-read pass that made 52 more corrections on the same cues and timings, and listed 9 lines it was unsure of (2026-11-04). Stage the corrected file, and upload it as a live fix under rule 3 only after that read. (`reference/youtube-seo.md` section 6)
- **Set both the default language and the audio language explicitly, and read them back.** Some update tools rewrite them, which left a channel with several mixed language codes. (`reference/youtube-seo.md` section 5)
