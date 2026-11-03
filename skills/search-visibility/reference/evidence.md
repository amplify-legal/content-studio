> **This is the reference the search-visibility skill reads first.** Researched in October 2026 with dated public sources, for a small channel teaching tutorials to one professional audience. It is method plus sources: nothing here is a figure from one channel's own analytics.
>
> **When it wins:** wherever an installed skill, a blog post or a vendor disagrees with it (llms.txt, schema as an AI-citation lever, the "YouTube is X% of AI citations" figures, the numbers inside third-party SEO and GEO skills), this file wins until a newer dated source replaces the line.
>
> **When to refresh it:** (1) a quarter after its date; (2) when a platform changes a rule it quotes (YouTube chapters or captions help pages, Google's video or AI features docs, Bing's AI Performance report, Anthropic's subprocessor list); (3) when your weekly measure (`geo.md`) moves the same way for 4 weeks running and nothing here explains it. Refresh means a research run with dated sources and the same labels (official guidance, measured, vendor claim, anecdote, hypothesis), written over this file with a new date in this header, the old copy kept beside your research. Never edit a single figure by hand without its source and date.

---

# Search visibility for tutorials: what the evidence says

Every claim names its source and date next to it. Quotes are kept under 15 words; everything else is paraphrase.

**Confidence labels used throughout**

| Label | Meaning |
|---|---|
| official guidance | The platform's own documentation or an employee speaking for it. Says what the system is designed to use, not how much it moves rankings. |
| measured | A study with a stated method and sample. Usually correlational. The vendor's commercial interest is named. |
| vendor claim | A number from a company selling a tool or service, with a thin or missing method. |
| anecdote | One test, one site, one experiment, or one observation. |
| hypothesis | Plausible, untested. |

**Effort scale for a small team:** Low = under 1 hour per video or under 1 day once. Medium = 1 to 3 hours per video or 1 to 3 days once. High = an ongoing weekly commitment, or engineering beyond the existing pipeline.

---

## Bottom line in 6 lines

1. YouTube, Google and Google's AI answers all read the same few text fields: title, description, chapters, and the spoken words. Making those precise and query-shaped is the cheapest lever with official backing on all 3 surfaces.
2. Google gives video features (video results, key moments) only to a page where the video is the main content. A companion page that links to the video without embedding it, with no structured data, can rank as text but is not eligible for video features.
3. YouTube is heavily cited by Google AI Overviews and Perplexity, rarely by Gemini and Copilot, and only moderately by ChatGPT. "Make videos and every AI cites you" is overstated.
4. Each assistant reads a different index: Google (AI Overviews, AI Mode, Gemini), Bing plus other providers plus OpenAI's own crawl (ChatGPT), Brave (Claude), Perplexity's own index, Bing (Copilot). Submitting to Bing and Brave is a one-time, low-effort move that covers 3 of them.
5. llms.txt and schema markup show no measured effect on AI citations. Keep VideoObject schema for Google's video features, not for AI.
6. In a typical niche the broad "AI tutorial for <audience>" query is owned by institutions, the head term "<tool> for <audience>" is contested by an exact-match channel or site, and feature-by-feature or sub-niche walkthroughs are thinly covered. Scan your own niche (section 6) before you believe this.

---

## 0. Which index each AI assistant reads

This decides where a page has to be indexed before an assistant can cite it.

| Assistant | Index it searches | Evidence | Label |
|---|---|---|---|
| Google AI Overviews and AI Mode | Google's own index. A page must be indexed and eligible for a snippet; no extra requirement. Both use "query fan-out" (many related sub-searches). | Google, "AI features and your website", last updated 2025-12-10, https://developers.google.com/search/docs/appearance/ai-features | official guidance |
| Gemini app | Google. In one test Gemini also fetched a brand-new page directly before Google had indexed it. | Aleyda Solis test, 2025-07-24, https://aleydasolis.com/en/ai-search/chatgpt-uses-google-serp-snippets-for-answers/ | anecdote |
| ChatGPT search | Third-party search providers (OpenAI's help page links Microsoft's and Shopify's privacy policies as the providers) plus OpenAI's own crawl. A site must allow OAI-SearchBot to be eligible. TechCrunch: Bing partnership plus undisclosed sources. One test showed ChatGPT answering from a Google result snippet for a page Bing had not indexed. | OpenAI Help "ChatGPT search", https://help.openai.com/en/articles/9237897-chatgpt-search ; OpenAI bots page, https://platform.openai.com/docs/bots ; TechCrunch 2025-03-21 (link below); Aleyda Solis 2025-07-24 (above) | official guidance (providers, crawler); anecdote (Google snippets) |
| Claude (web search) | Brave Search, confirmed: Anthropic added Brave to its subprocessor list on 2025-03-19. A second "web search" subprocessor, turbopuffer, is also listed. Profound re-ran its overlap test in June 2026 on about 400 queries: 79.2% of Claude's citations matched Brave's top results; 64% of Claude's cited URLs sat in Google's top 50 for the same query. | TechCrunch 2025-03-21, https://techcrunch.com/2025/03/21/anthropic-appears-to-be-using-brave-to-power-web-searches-for-its-claude-chatbot/ ; Xponent21 (an AI-SEO agency, discloses its interest), 2026-07-02, https://xponent21.com/insights/claude-web-search-brave-turbopuffer/ | official (subprocessor list); vendor claim (overlap %) |
| Brave itself | Brave's crawler will not crawl a page that Googlebot is not allowed to crawl. Brave accepts URL submissions. | Brave Search Help, "Brave Search Crawler", accessed 2026-10-09, https://search.brave.com/help/brave-search-crawler ; submit page https://search.brave.com/submit-url | official guidance |
| Perplexity | Its own index, built by PerplexityBot; allow it in robots.txt to appear. | Perplexity docs, accessed 2026-10-09, https://docs.perplexity.ai/guides/bots | official guidance |
| Microsoft Copilot | Bing. Bing Webmaster Tools now has an "AI Performance" report showing how often a site is cited in Copilot and Bing AI summaries, with the grounding phrases. Bing recommends IndexNow to get changes into AI answers quickly. | Bing Webmaster Blog, 2026-02, https://blogs.bing.com/webmaster/February-2026/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview | official guidance |
| Anthropic crawlers | Claude-SearchBot indexes for search quality; blocking it may reduce visibility in Claude's answers. ClaudeBot is training; Claude-User is user-triggered fetches. | Anthropic support, accessed 2026-10-09, https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler | official guidance |

**Check your own site the same way:** robots.txt allows the crawlers above and lists the sitemap; the sitemap returns 200; each page is server-rendered (its full text in the raw HTML, which matters because the major AI crawlers do not run JavaScript, per Vercel, 2024-12, https://vercel.com/blog/the-rise-of-the-ai-crawler , older source); whether any page embeds a video and carries JSON-LD.

---

## 1. YouTube search ranking

### What YouTube says search uses (official guidance)

- **3 elements: relevance, engagement, quality.** Relevance is estimated from how well the title, tags, description and video content match the query. Engagement includes watch time of a video *for that query*. Quality means signals that a channel shows expertise, authoritativeness and trustworthiness on the topic. Results are personalised by search and watch history. Source: YouTube Help, "How YouTube search works", accessed 2026-10-09 (no date on page), https://support.google.com/youtube/answer/16090438
- **Descriptions.** Give every video a unique description; pick 1 or 2 main words and put them prominently in both title and description; search terms are matched against the video and its description text; check the "How viewers find your video" search-terms report and add missing words. Source: YouTube Help, "Tips for video descriptions", accessed 2026-10-09, https://support.google.com/youtube/answer/12948449
- **Tags play a minimal role.** Title, thumbnail and description matter more; tags help mainly when a word is commonly misspelled. Source: YouTube Help, "Add tags", accessed 2026-10-09, https://support.google.com/youtube/answer/146402
- **Chapters.** Timestamps in the description, first at 00:00, at least 3, each at least 10 seconds; manual chapters override automatic ones; chapters may appear in the transcript. Source: YouTube Help, "Video Chapters", accessed 2026-10-09, https://support.google.com/youtube/answer/9884579
- **Satisfaction, not raw watch time.** Todd Beaupré (YouTube's senior director of growth and discovery) on Creator Insider, 2026-09-01: YouTube uses surveys to separate time spent from satisfaction; it does not judge a video on its first moments only; evergreen videos stay in consideration and some get most of their audience a month or more after publishing. Source: ppc.land write-up of the interview, accessed 2026-10-09, https://ppc.land/subscribers-skip-90-of-uploads-in-their-feed-youtube-director-says/ . Label: official guidance, second-hand transcript.
- **Title and thumbnail A/B testing.** "Test & compare" runs up to 3 titles and thumbnails and picks the winner by watch-time share; results take days to 2 weeks. Source: YouTube Help, accessed 2026-10-09, https://support.google.com/youtube/answer/16391400 ; title testing added 2025-12-09 per https://ppc.land/youtube-expands-a-b-testing-to-include-titles-alongside-thumbnails/

### Captions: uploaded file versus automatic

- YouTube's own help says automatic caption quality varies and encourages creators to add professional captions first. Source: YouTube Help, "Use automatic captioning", accessed 2026-10-09, https://support.google.com/youtube/answer/6373554 . Label: official guidance (for accuracy).
- **No YouTube statement found that an uploaded caption file ranks better in search than automatic captions.** Third-party pages assert it without a source. Label for the ranking claim: hypothesis.
- Why it may still be worth doing: "video content" is one of the relevance inputs YouTube names, and automatic captions mangle proper nouns. Even YouTube's own Creator Insider interview carried a machine transcript that misspelled both participants' names (ppc.land, above). For a tutorial channel the words that matter are proper nouns (product names, feature names, people's names). A pipeline that already makes a word-level transcript with a keyterms list can upload a corrected caption file for almost nothing. Label: hypothesis on ranking, near-zero effort.

### Playlists and series

- No official statement found that playlists change a video's search rank. YouTube's description tips suggest linking to playlists of related videos (source above).
- Observation, 2026-10-09: a third-party topic playlist appeared as its own result in YouTube search for a niche head term. So playlists can take a result slot of their own. Label: anecdote.

### How fast a new video's position settles

- No official settle time exists. Claims of "24 to 72 hours" on third-party blogs carry no source. Label: unsupported.
- Official direction: decisions are not based only on the first moments, and audiences can build for a month or more (Beaupré, above).
- Side note, untested: a year in a title that is ahead of the current year may read as a typo to some searchers.

---

## 2. Google Search and video

### Requirements for a video to be indexed and shown with video features (official guidance)

Source: Google Search Central, "Video SEO best practices", last updated 2025-12-18, https://developers.google.com/search/docs/appearance/video

- The watch page must be indexed **and performing well in Search** before its video is considered; an indexed page does not guarantee an indexed video.
- To be eligible for video features (video results, Video mode, key moments, live badge), build **a dedicated watch page for each video**, where watching the video is the main reason to visit. A blog post that reviews an embedded video is explicitly *not* a watch page. A non-watch page can still rank as a normal text result.
- Each watch page needs a unique title and description.
- **Embedding YouTube on your own page:** Google may index the video both on your page and on YouTube, and both may appear in video features if both meet the criteria. Google still recommends structured data on your own watch page and allows a video sitemap.
- Thumbnail must be stable and crawlable.

**The 2023 change behind the "main content" rule:** since 2023-04-13, video thumbnails show next to a Google result only when the video is the page's main content. Source: Google Search Central blog, 2023-04-13, https://developers.google.com/search/blog/2023/04/simplifying-video (older source, still reflected in the 2025 doc).

### Key moments

Source: same doc, plus "Video structured data", last updated 2026-09-24, https://developers.google.com/search/docs/appearance/structured-data/video

- Google tries to detect segments automatically but **prefers key moments the creator sets**, through structured data or the YouTube description.
- For a video embedded on your own page: `Clip` structured data (exact start, end, label; all languages) or `SeekToAction` (tell Google your timestamp URL pattern; English supported).
- For a video on YouTube: timestamps and labels in the YouTube description, one per line, chronological, each label at least 1 word.
- Label: official guidance.

### How YouTube videos appear in Google

- YouTube videos mostly occupy the video carousel; video rankings for the same query differed between Google and YouTube about 64% of the time; Google shows video most for informational, tutorial, how-to and review queries. Source: Perficient study reported by Search Engine Land, 2020, https://searchengineland.com/youtube-remains-dominant-source-of-video-in-top-google-ranking-positions-344458 . Label: measured, **older source (2020)**.
- Google's John Mueller: embedded and self-hosted video carry the same SEO value. Source: Search Engine Journal, 2021, https://www.searchenginejournal.com/google-embedded-videos-have-same-seo-value-as-uploaded-content/394216/ . Label: official guidance, **older (2021)**.

**Does embedding split signals?** No source says embedding hurts the YouTube video. Google's doc says both versions can appear. The honest summary: embed on a real watch page with structured data and you get a second eligible result (your domain) without evidence of harm to the YouTube one. Label: official guidance for eligibility; "no harm" is the absence of contrary evidence, not a measurement.

### AI Overviews draw from beyond the top 10 now, and YouTube is the outlier

Source: Ahrefs, 2026-03-02, https://ahrefs.com/blog/ai-overview-citations-top-10/ (Ahrefs sells Brand Radar). Method: 863K keyword results pages, 4M AI Overview URLs.

- 38% of pages cited in AI Overviews also ranked in Google's top 10 for that keyword (down from 76% in Ahrefs' July 2025 study); 31.2% ranked 11 to 100; 31.0% ranked beyond 100.
- Of cited pages that did **not** rank in the top 100, 18.2% were YouTube URLs; YouTube was 5.6% of all AI Overview citations in the set.
- Label: measured. Implication: a YouTube video can be cited in an AI Overview without ranking in classic Google for the same words.

---

## 3. AI answers citing video

### The studies, side by side

Numbers differ by up to 15 times because the metrics differ. "Share of all citations" (Profound) is not "share of answers that cite the domain at least once" (BrightEdge, Surfer). Never compare across rows.

| Study | Date | Method | What it found about YouTube | Vendor interest |
|---|---|---|---|---|
| BrightEdge, https://www.brightedge.com/resources/weekly-ai-search-insights/youtube-presence-ai-search | about 2025-09-25; data May 2024 to Sept 2025 | Citation tracking in its own tool; method otherwise thin | YouTube about 20% average citation share across AI platforms; 29.5% in AI Overviews (#1 domain), 16.6% in AI Mode, 9.7% in Perplexity; about 200x any other video platform; usually cited in positions 3 to 10 (supporting, not primary); how-to and instructional queries rising | Sells AI Catalyst. vendor claim |
| Ahrefs, top 10 cited domains, https://ahrefs.com/blog/top-10-most-cited-domains-ai-assistants/ | June 2025 data | 76.7M AI Overviews, 957k ChatGPT prompts, 953.5k Perplexity prompts | YouTube mention share 16.1% in Perplexity, 9.5% in AI Overviews, absent from ChatGPT's top 10 | Sells Brand Radar. measured |
| Profound, https://www.tryprofound.com/blog/ai-platform-citation-patterns | Aug 2024 to June 2025 | 680M citations | YouTube 1.9% of all AI Overview citations (#2 after Reddit 2.2%), 2.0% of Perplexity's (#2 after Reddit 6.6%), not in ChatGPT's top 10 (Wikipedia leads at 7.8%) | Sells Profound. measured |
| Surfer, https://surferseo.com/blog/ai-citation-report | March to Aug 2025 | 36M AI Overviews, 46M citations | YouTube about 23.3% across industries; 39.1% in SEO topics, about 23% in finance (appears to be share of Overviews that cite it) | Sells AI Tracker. measured |
| Semrush, https://www.semrush.com/blog/most-cited-domains-ai/ | 2025-11-10; weekly 2025-07-14 to 2025-10-12 | 230K prompts, ChatGPT search, AI Mode, Perplexity, 100M+ citations | YouTube among AI Mode's top domains and among the biggest gainers after mid-September; ChatGPT's Reddit and Wikipedia citations collapsed mid-September (Reddit from about 60% of answers to about 10%) | Sells AI toolkit; owns Search Engine Land. measured |
| OtterlyAI YouTube study, https://otterly.ai/blog/youtube-ai-citation-study-2026/ | 2026-03-02 | 100M+ citations, 30 days, 6 platforms; Pearson correlations on cited videos' metadata | Social and video sites were 5.54% of citations; YouTube 31.8% of those. YouTube citations by platform: Perplexity 38.7%, AI Overviews 36.6%, ChatGPT 4.4%, Copilot 0.5%, Gemini 0.2%. 94% went to long-form, 5.7% to Shorts. Views, likes and subscribers had near-zero correlation with citation frequency (r about -0.03). Timestamped YouTube citations appeared only in AI Overviews (73%) and AI Mode (27%); 78% of timestamped videos were cited repeatedly across 2 to 5 chapters. 40.83% of cited videos had under 1,000 views (figure as reported by WebFX, https://www.webfx.com/blog/ai/youtube-ai-citations/ ) | Sells AI search monitoring. measured |
| OtterlyAI video vs blog experiment, https://otterly.ai/blog/geo-experiment-video-to-blog/ | 2026-08-05; measured 2026-07-30 to 08-04 | 8 interview stories each published as a YouTube video and a transcript-based article; 2 prompts each; 7 platforms daily | The article earned about 79.5% of format citations at first; video's share rose from 15% to 26% within a week; video share by platform: Perplexity 41.5%, AI Mode 29%, Gemini 20%, AI Overviews 12%; the pair whose titles matched best saw the video take 53% | Vendor, small sample, 6 days. anecdote |
| TRYSEO guest experiment on OtterlyAI, https://otterly.ai/blog/geo-experiment-youtube-ai-generated-videos/ | 2026-04-22 | 25 AI-generated videos on a new channel, titles and scripts matching 25 German B2B prompts word for word; about 10 days | 19 of 25 ranked first in Google for their exact prompt within the week; share-of-voice moved +53% AI Mode, +44% Copilot, +38% ChatGPT, +34% Gemini, +20% Perplexity, +3% AI Overviews | Agency plus vendor; low-competition niche; single brand. anecdote |

### What kind of video gets cited

- **Long-form reference videos, not Shorts** (OtterlyAI, 94% long-form). Label: measured, vendor.
- **Popularity is not the gate** (OtterlyAI r about -0.03; 40.83% under 1,000 views). Label: measured, vendor. Good news for a small channel.
- **Chapters matter for Google's AI only**: timestamped citations appeared only in AI Overviews and AI Mode (OtterlyAI). Label: measured, vendor; consistent with Google's official key-moments guidance.
- **How-to, demonstration and comparison queries** trigger YouTube citations (BrightEdge, OtterlyAI). Label: vendor claim.

### What content shape AI engines quote

- **Retrieval rank and query match dominate.** Kevin Indig, 815,000 query-page pairs across 16,851 queries: a page returned first by ChatGPT's search tool had a 58% citation rate, falling to about 14% by position 10; covering every fan-out subtopic added only 4.6 percentage points over covering none; moderate coverage beat exhaustive "ultimate guides"; query match was measured as how well the page's best heading matches the query. Source: Growth Memo 2026-04-13 (paywalled), reported by Search Engine Journal 2026-04-14, https://www.searchenginejournal.com/shorter-focused-content-wins-in-chatgpt/571857/ . Label: measured (independent analyst).
- **Front-load and answer directly.** Indig, 1.2M ChatGPT answers, 18,012 verified citations: 44.2% of citations came from the first 30% of a page; cited passages were about twice as likely to use definitional language ("X is"); 78.4% of question-linked citations came from headings; cited text averaged 20.6% proper nouns versus 5 to 8% in typical English. Source: Search Engine Land, 2026-02-18, https://searchengineland.com/chatgpt-citations-content-study-469483 . Label: measured (analyst; SEL is owned by Semrush).
- **Microsoft's own guidance** for Copilot and Bing: align page title, H1 and meta description; use question-style H2s with direct answers; lists, steps and tables for how-to content; do not hide answers in tabs, PDFs or images; avoid walls of text. Source: Microsoft Advertising blog, 2025-10, https://about.ads.microsoft.com/en/blog/post/october-2025/optimizing-your-content-for-inclusion-in-ai-search-answers . Label: official guidance.
- **Google's guidance**: no special optimisation; make important content available as text and support it with video. Source: Google AI features doc, 2025-12-10 (above). Label: official guidance.
- **Older academic baseline:** GEO paper (Aggarwal et al., KDD 2024, arXiv 2311.09735, first posted 2023-11-16) reports visibility gains of up to 40% on a simulated benchmark; its best methods added quotations, statistics and cited sources (from the paper body, not re-verified). https://arxiv.org/abs/2311.09735 . Label: measured in a lab setting, **older**, not a production measurement.

### Schema markup and AI citations

- **No measured lift.** Ahrefs tracked 1,885 pages that added JSON-LD between Aug 2025 and Mar 2026 against about 4,000 matched controls: AI Overviews citations -4.6% relative to controls (small, statistically significant), AI Mode +2.4% and ChatGPT +2.2% (indistinguishable from zero). Caveat: every page was already heavily cited, so this says nothing about schema helping a page get noticed the first time. Source: Ahrefs, 2026-05-11, https://ahrefs.com/blog/schema-ai-citations/ . Label: measured (Ahrefs sells tools).
- In a controlled test page, ChatGPT, Claude, Perplexity and Gemini extracted only visible HTML during direct fetch and ignored data present only in JSON-LD. Source: searchVIU, tests run 2025-10, https://www.searchviu.com/en/schema-markup-and-ai-in-2025-what-chatgpt-claude-perplexity-gemini-really-see/ . Label: anecdote (single test page, vendor).
- **Keep VideoObject and Clip anyway**: Google's video features and key moments use them (official, section 2). Just do not expect AI citations from them.

---

## 4. llms.txt

- **No measured effect.** SE Ranking, about 300,000 domains: 10.13% had an llms.txt; no correlation with how often a domain is cited by LLMs; removing the llms.txt variable *improved* their XGBoost model. Source: SE Ranking, 2025-11-07, https://seranking.com/blog/llms-txt/ (SE Ranking sells SEO tools). Label: measured.
- **Google:** you do not need new machine-readable files or AI text files to appear in AI Overviews or AI Mode. Source: Google AI features doc, 2025-12-10 (above). Label: official guidance.
- **Google's John Mueller** said no AI system currently uses llms.txt (Bluesky, 2025-06-17), per Search Engine Roundtable 2025-06-18, https://www.seroundtable.com/google-ai-llms-txt-39607.html . Gary Illyes said at Search Central Live (July 2025) that Google does not support it, per SE Ranking's citation of a LinkedIn post (link in the SE Ranking article). Label: official guidance (Mueller direct; Illyes second-hand).
- No AI lab has stated that llms.txt affects search inclusion or citation. OpenAI's stated route is allowing OAI-SearchBot (OpenAI bots page). Anthropic and Perplexity document their crawlers and robots.txt only (section 0).
- **For your site:** if it already serves an llms.txt, leave it (zero cost) and invest nothing more.

---

## 5. Off-site mentions

### Evidence

- **Brand mentions, especially on YouTube, track AI visibility; backlinks barely do.** Ahrefs, 75,000 brands, millions of AI responses, Spearman correlations: "YouTube mentions" (brand named in a video title, transcript or description) about 0.737 with AI visibility across ChatGPT, AI Mode and AI Overviews, the strongest factor tested; branded web mentions 0.66 to 0.71; backlink counts weak; for ChatGPT, branded search volume 0.352 and Domain Rating 0.266. Low-view videos did not seem to disadvantage a brand if it was mentioned widely. Ahrefs states correlation is not causation and that these may just mark existing brand strength. Source: Ahrefs, 2025-12-12, https://ahrefs.com/blog/ai-brand-visibility-correlations/ . Label: measured (brand-level, not video-level; Ahrefs sells the Brand Radar data it used).
- **Earned media dominates what AI cites.** Muck Rack, third edition, more than 1M links cited by ChatGPT, Claude and Gemini for realistic prompts: about 99% of cited links are non-paid, about 84% earned, journalism about 27%. Claude cites in only 55% of answers but averages 13 sources when it does; ChatGPT cites in 96% with about 5. Source: Muck Rack, "What Is AI Reading?", 2026-05, https://media.muckrack.com/documents/What_Is_AI_Reading__May_2026.pdf . Label: measured (Muck Rack sells PR software).
- **Academic confirmation of the earned-media bias.** Chen, Wang, Chen and Koudas, large controlled comparisons of AI search versus Google across verticals and languages: AI search shows a systematic, overwhelming bias toward earned third-party sources over brand-owned and social content, unlike Google's more balanced mix. Source: arXiv 2509.08919, 2025-09-10, https://arxiv.org/abs/2509.08919 . Label: measured (academic preprint, not peer reviewed at time of reading).
- **Reddit is the most-cited community source.** Reddit leads Perplexity (6.6% of all citations) and AI Overviews (2.2%) in Profound's data; Reddit and LinkedIn were in the top 5 cited domains on ChatGPT, AI Mode and Perplexity in Semrush's 13-week panel, though ChatGPT's Reddit citations fell sharply in mid-September 2025 (sources in section 3). Label: measured, vendors.
- **Check your own niche:** whether a forum thread ranks in the top web results for your head term, and whether Google autocomplete for it suggests "... reddit". Both were true in the niche this was researched on. Label: anecdote.

### What it implies for a small team

- The one off-site channel the evidence supports most directly is **video mentions**: being named in other people's YouTube titles, descriptions and transcripts. Podcast guest spots that publish to YouTube create exactly that. The pipeline lever is to make sure the creator's name and the company's name are said aloud and written in the host's title or description. Label: inference from a correlational study (hypothesis for causation).
- **Your niche's trade publications** are the earned-media lever with the strongest support, and the highest effort. Label: measured direction, high effort.
- **Forum** participation is measured as heavily cited, but niche subreddits have self-promotion norms; helpful answers link a resource page only when it answers the question. Label: measured share, medium effort, account risk if done badly.

---

## 6. The niche scan: who owns your queries today (method)

Method: signed-out scrapes of YouTube search result pages and a web search tool that tracks Google closely, plus Google and YouTube autocomplete, all on the same day. A quick look, not a rank tracker; results vary by person and day. Write it down dated, and refresh it from the weekly measure.

1. **YouTube, your head term, top 15:** title, channel, views and age per result. Note whether one exact-match channel owns several slots, whether institutions own the broad query, and whether any playlist takes a slot.
2. **Google, your head term, top 10:** which domains (forums, trade publications, the tool's own docs, exact-match sites, YouTube videos). Run a second engine to see what it adds.
3. **Autocomplete, Google and YouTube:** the head term, "<tool> for <audience>", "how to use <tool> for ...". It is a demand signal, not search volume.
4. **Title shape that wins:** in the niche this was researched on, most top titles led with the exact query words, then a concrete promise (tips, every feature, setup, a specific task), often with a year. Check whether yours is the same.
5. **Gaps worth testing** (observation, not measured demand): sub-niche or feature-by-feature walkthroughs titled by name; the trust or confidentiality question; task how-tos phrased as the query; "<tool> vs <competitor>"; cost and plan choice; adjacent products that autocomplete offers. Write them into the open-searches list in `geo.md`.

---

## 7. Every lever, with evidence, label and effort

| # | Lever | Evidence (source, date) | Label | Effort |
|---|---|---|---|---|
| 1 | **Chapters with descriptive, query-shaped labels** in every YouTube description | YouTube chapters rules (accessed 2026-10-09); Google prefers creator-set key moments from the YouTube description (2025-12-18, 2026-09-24); timestamped YouTube citations appear in AI Overviews and AI Mode, often 2 to 5 chapters per video (OtterlyAI 2026-03-02) | official guidance + measured (vendor) | Low: generate from the transcript in the pipeline |
| 2 | **Title and first description lines use the exact phrase your audience types**, 1 to 2 main words in both, unique description per video | YouTube description tips and How Search Works (accessed 2026-10-09); query match predicts ChatGPT citation (Indig 2026-04); exact-match titles ranked 19 of 25 first in Google within a week (TRYSEO 2026-04-22) | official guidance + measured + anecdote | Low |
| 3 | **Submit to Bing (Webmaster Tools, IndexNow on publish), Brave (submit-url) and Google Search Console** | Copilot is Bing; ChatGPT uses Microsoft among its providers; Claude uses Brave; Brave crawls only what Googlebot may crawl (sources in section 0) | official guidance | Low: one-time setup, a ping per publish |
| 4 | **Pick queries the field has not claimed** (sub-niche walkthroughs, the trust question, task how-tos, vs a competitor, cost) | Your niche scan (section 6) | anecdote (direct observation of a niche) | Low: a planning choice |
| 5 | **A dedicated watch page per video on your own site**: video embedded as the main content, unique title and description, full transcript as HTML, VideoObject plus Clip, listed in a sitemap | Google video best practices (2025-12-18): required for video features and key moments on your own domain; third-party embeds eligible; written version earned citations first and pairing helped (OtterlyAI experiment 2026-08-05) | official guidance + anecdote | Medium once (a page template), Low per video after |
| 6 | **Long-form tutorials as the citation asset; Shorts for reach only** | 94% of YouTube AI citations went to long-form (OtterlyAI 2026-03-02) | measured (vendor) | Low: a format rule |
| 7 | **Answer-first companion text**: question H2s, a definition in the first lines, steps as lists, named tools and products, the main point in the first third | Indig 2026-02-18 and 2026-04-14; Microsoft 2025-10 | measured (analyst) + official guidance | Medium per video, Low if drafted from the transcript |
| 8 | **Say and write the brand and named entities**: the creator's name, the company's name, product names, on camera and in guest-spot titles and descriptions | Ahrefs 75k brands, YouTube mentions about 0.737 (2025-12-12); cited text is entity-dense (Indig 2026-02-18) | measured (correlation, brand-level) | Low on own videos; Medium for guest spots |
| 9 | **Upload a corrected caption file** (the word-level transcript with keyterms your pipeline already makes) | YouTube encourages professional captions because automatic quality varies (accessed 2026-10-09); no source ties it to ranking | official guidance (accuracy); hypothesis (ranking) | Low: near zero |
| 10 | **Topic series playlists** (one video per sub-niche, say) | Playlists can take their own result slots (observation 2026-10-09); YouTube tips suggest linking playlists | anecdote + official guidance | Low |
| 11 | **Title and thumbnail A/B tests** with Test & compare, judged on watch-time share | YouTube Help (accessed 2026-10-09) | official guidance (feature exists); effect on search untested | Low |
| 12 | **Rank in classic Google and Bing for the query** (the page and the video) | ChatGPT citation odds fall from 58% at position 0 to about 14% at position 10 (Indig 2026-04); 38% of AI Overview citations come from the top 10 (Ahrefs 2026-03-02); 64% of Claude citations sit in Google's top 50 (Profound via Xponent21, 2026-07-02) | measured + vendor claim | Medium to High: this is ordinary SEO over time |
| 13 | **Keep crawlers allowed and pages server-rendered** (OAI-SearchBot, PerplexityBot, Claude-SearchBot, Googlebot, Bingbot) | Official crawler docs (section 0); AI crawlers do not run JavaScript (Vercel 2024-12, older) | official guidance | Low: a check after each site change |
| 14 | **Podcast guest spots that publish to YouTube** | Ahrefs YouTube mentions correlation (2025-12-12); Muck Rack earned media 84% (2026-05) | measured (correlational) | Medium ongoing |
| 15 | **Helpful answers in the forums your audience uses** | Reddit heavily cited (Profound 2025, Semrush 2025-11-10) | measured share + anecdote | Medium ongoing, account risk |
| 16 | **Bylines or quotes in your niche's trade publications** | Earned-media bias (Chen et al. 2025-09-10; Muck Rack 2026-05) | measured | High |
| 17 | **Satisfying the query** (retention, no bait titles) | YouTube names engagement for the query and survey-based satisfaction (accessed 2026-10-09; Beaupré 2026-09-01) | official guidance | High: it is the content itself |
| 18 | **VideoObject and other schema, for AI citations** | No lift measured (Ahrefs 2026-05-11); JSON-LD ignored on direct fetch (searchVIU 2025-10). Keep it for Google video features only | measured: no effect | Low, but expect nothing for AI |
| 19 | **llms.txt** | No correlation (SE Ranking 2025-11-07); Google says not needed (2025-12-10) | measured: no effect | Leave one if it exists; stop there |
| 20 | **Tags** | Minimal role per YouTube (accessed 2026-10-09) | official guidance: minimal | Low, low value; only for common misspellings of your product names |

### How to measure whether any of this works

- YouTube Studio, "How viewers find your video": the search terms each video is found by (official, description tips page).
- Google Search Console: AI Overviews and AI Mode traffic is folded into normal search traffic, not separated (Google AI features doc, 2025-12-10).
- Bing Webmaster Tools, AI Performance: citations in Copilot and Bing AI summaries, with grounding phrases (Bing, 2026-02).
- A fixed prompt panel (the same 10 to 20 audience questions) run on a schedule in ChatGPT, Claude, Perplexity, Gemini and AI Mode, logging which URLs are cited (the weekly measure in `geo.md`). Paid monitors exist (OtterlyAI, Profound, Ahrefs Brand Radar); every vendor number quoted above came from one of them, which is the reason to keep your own panel.

---

## 8. Ranked: the 10 levers with the best evidence-to-effort ratio for a small channel

1. **Chapters with query-shaped labels** (lever 1). Official on YouTube and Google, measured in Google's AI answers, generated from the transcript the pipeline already has.
2. **Exact-phrase titles and description openings, unique per video** (lever 2). Official on YouTube, supported by the ChatGPT query-match data.
3. **Bing + IndexNow, Brave submit, Search Console** (lever 3). One-time, official, covers Copilot, part of ChatGPT and Claude.
4. **Target the unclaimed queries** (lever 4), from your own niche scan.
5. **A real watch page per video with transcript, VideoObject and Clip** (lever 5). The only route to Google video features on your own domain; a companion page that only links the video does not qualify.
6. **Long-form as the citation format** (lever 6). Measured, costs nothing but a rule.
7. **Answer-first structure on the companion text** (lever 7). Measured by an independent analyst, matches Microsoft's guidance.
8. **Brand and entities spoken and written, including on guest spots** (levers 8 and 14). The strongest correlation in the off-site evidence.
9. **Corrected caption upload** (lever 9). Weak evidence for ranking, but near-zero effort and it fixes proper nouns for every index that reads the transcript.
10. **Series playlists and title A/B tests** (levers 10 and 11). Low effort, official features, effect on search untested.

---

## 9. Popular claims that turned out unsupported or overstated

| Claim | What the evidence says |
|---|---|
| "Add llms.txt to get cited by AI" | No correlation across about 300,000 domains (SE Ranking 2025-11-07); Google says no AI text files are needed (2025-12-10); Mueller says no AI system uses it (2025-06-17). |
| "Schema markup gets you cited by ChatGPT and AI Overviews" | No lift in a 1,885-page controlled study, slight decline on AI Overviews (Ahrefs 2026-05-11); chatbots ignored JSON-LD-only data on direct fetch (searchVIU 2025-10). Schema still matters for Google video features. |
| "YouTube is X% of all AI citations, so videos get you cited everywhere" | Vendor figures run from 1.9% (Profound, share of all AI Overview citations) to 29.5% (BrightEdge) because the metrics differ. YouTube citations concentrate in Perplexity and AI Overviews; Gemini 0.2% and Copilot 0.5% of YouTube citations (OtterlyAI 2026-03-02). |
| "Tags drive YouTube discovery" | YouTube says tags play a minimal role (accessed 2026-10-09). |
| "Uploaded captions boost YouTube ranking" | No YouTube statement found; YouTube recommends them for accuracy only. Hypothesis. |
| "You need views and subscribers before AI will cite you" | Near-zero correlation between popularity and citation; 40.83% of cited videos had under 1,000 views (OtterlyAI 2026-03-02, vendor). |
| "Your Google ranking does not matter for Claude or ChatGPT" | Brave, Claude's index, will not crawl what Googlebot cannot (Brave docs); 64% of Claude's cited URLs sit in Google's top 50 (vendor); retrieval rank is the strongest ChatGPT citation predictor (Indig 2026-04). |
| "Write the ultimate guide that covers every subtopic" | Exhaustive fan-out coverage added 4.6 points and underperformed moderate coverage (Indig, 815,000 pairs, 2026-04). |
| "New videos settle in search within 24 to 72 hours" | No official source. YouTube says it does not judge on first moments and evergreen videos can peak a month or more later (Beaupré 2026-09-01). |
| "GEO raises visibility by 40%" | A 2023 lab benchmark on simulated engines (arXiv 2311.09735), not a measurement on live ChatGPT, Perplexity or Google. |
| "Embedding your YouTube video on your site splits or steals its signals" | No source found. Google says both your page and YouTube's can appear in video features (2025-12-18). |

---

## Open questions an experiment could settle

- Does a corrected caption file change which search terms find a video? Test: upload corrected captions on half of new videos, compare the "How viewers find your video" terms after 30 days.
- Does a watch page on your own site get its own video result or key moments in Google? Test: build the template for 3 videos, check the Search Console video indexing report after 4 weeks.
- Which assistants cite the channel at all today? Test: the fixed prompt panel, starting before any change, so there is a baseline.
