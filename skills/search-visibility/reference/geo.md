# GEO: indexed where each assistant looks, and measured weekly

> Module of the search-visibility skill. Evidence: `evidence.md` sections 0, 5 and 7 (levers 3, 4, 8, 12 to 16). Kept from the third-party GEO skills this replaced: Bing Webmaster Tools, IndexNow and the idea that mentions matter. Dropped: their figures (Wikipedia, Reddit and "92% from the top 10" shares with no source anyone could check), Wikipedia and Wikidata creation, and any off-site action taken by the machine.

## Which index each assistant reads (`evidence.md` section 0)

| Assistant | Reads | So you need |
|---|---|---|
| Google AI Overviews, AI Mode, Gemini | Google's index | Google indexing (Search Console) and classic ranking |
| ChatGPT search | third-party providers (Microsoft among them) plus OpenAI's own crawl; OAI-SearchBot allowed | Bing indexing, OAI-SearchBot allowed |
| Claude | Brave (Anthropic's subprocessor list, 2025-03-19); Brave never crawls what Googlebot may not | Brave indexing, Googlebot allowed, Claude-SearchBot allowed |
| Perplexity | its own index (PerplexityBot) | PerplexityBot allowed |
| Copilot | Bing | Bing indexing; Bing's AI Performance report shows citations |

**Bing plus Brave covers 3 of them in one sitting** (lever 3: official guidance, low effort). Check once that every AI crawler gets HTTP 200 and the full server-rendered page from your site (fetch with each crawler's user agent through `curl`), and re-check after every site change.

## On publish of any page (watch page, blog article)

| # | Step | Who |
|---|---|---|
| 1 | The page live, 200, in `sitemap.xml`, a line in `llms.txt` if you keep one, a card on your resources index | machine, after the creator's go on the page |
| 2 | **IndexNow ping** to Bing (and the engines that share it) for the new or changed URL | machine, once the key file is hosted on the site (hosting it is a website change and needs the creator's go) |
| 3 | **Bing Webmaster Tools**: the site verified, the sitemap submitted; it can import the Search Console property | the creator's sign-in, once |
| 4 | **Brave URL submission** (`https://search.brave.com/submit-url`) | a person submits the form, or the session after the creator's go in that session |
| 5 | **Google Search Console**: the sitemap, then URL inspection for the new page; later the video indexing report | the session, once connected (connecting is a Google sign-in) |
| 6 | The YouTube description gains the page link | machine, through the live-fix step (dry run first, undo line, report) |

Steps 3 to 5 are person-only and come last, after everything around them is done; each run that finds them still open says so in one line rather than skipping silently.

## Ranking in classic search is the lever under all of it

ChatGPT's citation odds fall from 58% at the first retrieval position to about 14% at position 10 (Indig, 2026-04); 38% of AI Overview citations come from Google's top 10 (Ahrefs, 2026-03-02); 64% of Claude's cited URLs sat in Google's top 50 (vendor figure via Xponent21, 2026-07-02). So the levers that rank (the phrase in the title and description, chapters, a real watch page, answer-first text) are the GEO levers too; there is no separate trick. Effort: ordinary SEO over weeks (lever 12).

## The searches nobody owns yet (for the brief)

Run a niche scan once, then refresh it from the weekly measure (method in `evidence.md` section 6): signed-out YouTube and Google results for your head terms, plus Google and YouTube autocomplete. Write the open searches as a list in your notes. Shapes that are often thin in a tutorial niche:

1. **One video per sub-niche or per feature**, titled with the feature and the sub-niche.
2. **The trust or safety question** your audience asks before adopting (privacy, confidentiality, data handling), when it shows up in autocomplete.
3. **Task how-tos phrased as the query**: "how to use <tool> for <task>".
4. **<tool> vs <competitor>**, and **cost and plan choice**.
5. **Adjacent products for your audience** ("<adjacent tool> for <audience>") that autocomplete offers.

A head term owned by an exact-match channel or by institutions is contested and hard. The brief offers the open searches this video could honestly serve, and the creator picks. The weekly measure below is what tells whether one opened or closed; refresh the list from it, never from memory.

## Off-site mentions: seeds, never sends

Brand mentions in other people's YouTube titles, descriptions and transcripts correlate most strongly with AI visibility (Ahrefs, 75,000 brands, about 0.737, 2025-12-12; correlation, brand-level, may only mark existing strength); earned media dominates what AI cites (Muck Rack, 2026-05; Chen et al., 2025-09-10). What this lane does with that:

- **Podcast guest spots**: the run sheet carries one line, say the creator's name and the company name aloud, and the after-call note asks the host to write both in the episode title or description. The ask is a line in the creator's own message, never one the machine sends.
- **Forums** (a subreddit that ranks for your head term) and **your niche's trade publications**: an idea lands verbatim in `content/seeds.md` with the thread or outlet and why, for the creator to act on by hand. Self-promotion norms make a careless answer an account risk.
- Nothing is posted, commented or messaged off-site by a session.

## The weekly measure: a fixed list of queries

**Set the list once:** 10 to 20 queries your audience types for your topic, taken from your search-terms report and the niche scan. **The list is the contract: never edit it; when it no longer fits, start a new list beside it**, so the trend stays comparable.

**The surfaces, per query:**

| Surface | How | Keep |
|---|---|---|
| A1 YouTube search, API | the YouTube Data API `search.list` (region and language pinned, top 20) | your videos' positions |
| A2 YouTube search, page | a signed-out read of the results page (top 20) through a scraping tool of your choice | your videos' positions |
| B Google web | a SERP tool or scraper (one country, desktop, top 10, plus whether an AI Overview appears and what it cites) | your pages' and videos' positions |
| C AI answers | 1 call per engine per query through an API with web search on (for example Perplexity's online model, an OpenAI model with web search, Gemini with Google grounding), with one fixed prompt: "I'm a <audience member>. Can you recommend a good video tutorial or guide on <topic>?" | whether your channel, site or name is cited |

**When:** once a week, same day, in the daytime or whenever your API quota is fresh. A shared API project can run out of quota and refuse most calls; when a surface has to run through a fallback route, mark the route in the run notes and never compare a fallback week with a normal week. Note the cost of one run in your notes; a run of AI-answer calls across 3 engines usually costs a few dollars.

**How to read it (a trend, never one run):**
- YouTube positions can move several places between 2 passes minutes apart. Read any single position as plus or minus a few places, and a change as real only when it holds 3 weeks or more.
- Report per surface: on how many of the queries you appear, and your best position; then which of your videos or pages appeared. Compare with your first run, the baseline, taken before any change.
- AI answers are one call per engine per query: a sample, not a rate. "Absent" on one call proves little; absent for 4 weeks says more.
- Name what changed in the week (a watch page went live, chapters fixed, a new video titled with the phrase) beside any move, as a **hypothesis** about the cause, never as proven.
- The "who wins instead" table is context for the brief (which searches are contested), not a target list.

**Beside it on the Friday board:** the channel's YouTube search terms and AI-assistant referrers for the week (YouTube Analytics); Bing's AI Performance report (citations in Copilot and Bing's AI answers, with the grounding phrases) once Bing Webmaster Tools is set up; Search Console's queries once it is connected. Impressions and click-through rate per video are in Studio; check what your analytics route returns before promising them on a board.

## Google's own changes, weekly

Every Friday measure also reads what Google changed in Search that week, from 3 public sources with no key: the Search Central blog (`https://developers.google.com/search/blog`), the Search documentation updates page (`https://developers.google.com/search/updates`) and the Search status dashboard (`https://status.search.google.com/`). Tag each change by the surface it could touch (watch page, blog article, site, YouTube). Write 1 meaning line per tagged change, with an owner and an action (or "none"), or clear the tag with the reason it does not touch you; a note with a tagged change and no meaning line is not finished. Keep the dated note with the scoreboard and put 1 line on the Friday board. A change to a live page it suggests is still the creator's go; a ranking update finishing is read against the trend above, never as a cause on its own.
