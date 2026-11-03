# The watch page: one per video on your own site

> Module of the search-visibility skill. A spec built and checked on 2 real pages before it was written down. Starting default: a watch page for every video in your core topic, built to be easy to follow for both people and AI crawlers.

## Why a page per video (official, `evidence.md` section 2)

Google gives video results and key moments only to **a dedicated watch page, where watching the video is the main reason to visit**; a blog post that reviews an embedded video is explicitly not one, though it can still rank as text. Since 2023-04-13 a video thumbnail shows beside a Google result only when the video is the page's main content. Embedding your YouTube video on your own page can give a second eligible result on your domain, and no source says it harms the YouTube one. A companion page that only links to the video, with no embed and no video structured data, is not eligible: check your existing pages for exactly that.

## The spec

| # | The page | Why |
|---|---|---|
| 1 | **The video first.** Either the embed straight under the h1, full width, or pinned beside the steps on desktop with a small docked player when it scrolls away | Google's main-content rule above. A guide whose long text leads, with the player beside or below it, is by that rule closer to an article than to a watch page |
| 2 | **Every word in the static HTML and visible**: intro, chapters, steps, questions with answers, the full transcript. JavaScript only adds seeking, a now-playing highlight and the docked player. Nothing behind a tab, an accordion closed by default, a click or an email gate | The major AI crawlers do not run JavaScript (Vercel, 2024-12, older); chatbots read visible HTML only on a direct fetch (searchVIU, 2025-10); Microsoft: never hide answers in tabs, PDFs or images (`evidence.md` section 3) |
| 3 | **One h1** carrying the search phrase; the `<title>`, the h1 and the meta description aligned on it, each unique to this page | Microsoft's own guidance for Copilot and Bing; Google: a unique title and description per watch page |
| 4 | **An answer-first intro**: 2 to 3 sentences that answer the page's question before anything else ("To set up <tool>, open <app>, go to <place>, ...") | Front-loaded, definitional passages are what ChatGPT cites (Indig, 2026-02-18: 44.2% of citations from the first 30% of a page) |
| 5 | **Chapters as links**, every one seeking the player to its second; `?t=<seconds>` on the page address starts the embed there | Key moments; every Clip in the structured data points at `<page_url>?t=<start>` |
| 6 | **Question headings with direct answers**, the method in `aeo.md` | 78.4% of question-linked ChatGPT citations came from headings (Indig, 2026-02-18) |
| 7 | **The full corrected transcript** under its chapter headings, with paragraph timestamps | Google: make important content available as text; the corrected words fix the proper nouns every index reads |
| 8 | **Structured data, one JSON-LD graph in the server HTML:** `VideoObject` (name, description, thumbnailUrl, uploadDate, duration, embedUrl, url, inLanguage, transcript, author, publisher) with **one `Clip` per chapter** in `hasPart` (name, startOffset, endOffset, url), a `Person` for the creator (`sameAs` the YouTube channel and their main profile, `worksFor` the organisation) and the `Organization`. No `FAQPage` (Google restricted its rich result to government and health sites in Aug 2023) and no `HowTo` (rich result removed Sep 2023) | For Google's video features and key moments only; **no AI-citation lift is measured** (Ahrefs, 2026-05-11). The Person `sameAs` ties the channel to the creator, which many sites never do |
| 9 | **Canonical in the form your site actually serves** (with or without the trailing slash), and every JSON-LD page URL in the same form | Many hosts redirect one form to the other; measure yours with `curl -I` and match it |
| 10 | **A stable, crawlable thumbnail** (for a YouTube video, `https://i.ytimg.com/vi/<id>/maxresdefault.jpg`) | Google's video requirements |
| 11 | **A byline**: the creator, linking their about page; the call to action the video itself makes, quoted from the video at its timestamp | The call to action is the creator's pick (open, below) |
| 12 | **Resources**: every link the video promises, each fetched this session with its status recorded (`resources[].status`) | The on-camera promise rule (`content/taste/must-dos.md`) |
| 13 | **Nothing internal in the rendered text or the HTML comments**: no names of people who asked, no meeting ids, no workspace paths, no presenter notes | Check by stripping the tags and reading the text, then grepping `<!--`; a build comment that names a source file is right in a prep doc and wrong on anything published |

Then, in the website repo at publish: the page in `sitemap.xml`, a line in `llms.txt` if you keep one (zero cost, not a lever, `evidence.md` section 4) and a card on whatever index page lists your resources. A video sitemap entry is allowed by Google and optional.

## The content pack: `content/videos/<slug>/search/watch-page.json`

Once a renderer reads these keys, never rename one; a new pack copies the shape of the last good one.

| Key | Holds |
|---|---|
| `slug` | the folder name |
| `page_url_proposed`, `page_url`, `page_url_status` | the address the JSON-LD was written against, the canonical one the renderer rebases onto, and why it is still proposed |
| `search_phrase` | the search pack's `phrase` |
| `page_title`, `h1`, `meta_description`, `intro` | the head and the answer-first intro. A pack with a headline choice still open also carries `h1_previous` and `h1_status` |
| `video` | `id`, `youtube_url`, `embed_url`, `title_live` (read live, never typed), `duration_iso8601`, `duration_seconds`, `upload_date`, `thumbnail_url`, `description`, `deep_link` (`param`, `page_url_template`, `embed_url_template`, `note`) |
| `chapters[]` | `start_seconds`, `end_seconds`, `start` (m:ss), `label`; the same list as the search pack's chapters |
| `steps[]` | `number`, `start_seconds`, `start`, `text`: what to do, in order, each tied to the second it is shown |
| `questions[]` | `q`, `answer`, `timestamp_seconds`, `timestamp`, `asked_in` (`status`, `receipt`, `asked_by` as a role, `note` pointing at the private trace); method in `aeo.md` |
| `questions_heading`, `questions_receipt_summary` | the heading the page prints and one line on how every question traces |
| `transcript[]` | `chapter_start_seconds`, `chapter_start`, `heading`, `paragraphs[]` (`start_seconds`, `start`, `text`) |
| `transcript_notes[]` (optional) | `chapter_start_seconds`, `chapter_start`, `placement`, `text`, `links[]` (`url`, `label`): a dated correction or source note placed in the transcript where the video's words need one (a plan's terms that changed since recording) |
| `resources[]` | `url`, `label`, `status` |
| `cta` | `status`, `options[]` (`label`, `text`, `url`, `from_video`), `note` |
| `jsonld` | `@context` and `@graph` (VideoObject with `hasPart` Clips, Person, Organization) |

`asked_in.receipt` names a meeting id or a chat export time. It lives in the pack and **never renders**; the people's names live only in the private trace.

## 2 directions worth building

| Direction | What makes it |
|---|---|
| **A, "Follow along"** | On desktop the video stays pinned beside one timeline where every chapter carries its numbered step cards, each with a "Watch at" button; a short answer box and a numbered chapter strip under the video. The shorter page |
| **B, "Read it like a guide"** | A big headline, the embed full width straight under it, then the walkthrough as an article whose chapters each open with their timestamp, "what you'll learn" boxes and the creator's own lines as pull quotes. The longer page |

**Direction B needs editorial choices** (the "what you'll learn" boxes, the pull quotes, the featured line, the CTA wording), written from the transcript into a separate file beside the pack. **Every pull quote must be word for word in the transcript, or the build stops** rather than inventing one. Until the creator picks a direction, render both and show them side by side, on one row, never in sequential sections.

**Untested:** a privacy-friendly embed host (`youtube-nocookie.com`) while the JSON-LD `embedUrl` names `youtube.com/embed`; whether Google pairs them is unknown until Search Console's video indexing report reads a live page. Whether Google shows the chapters as key moments is also untested until a page is live.

## The calls the creator makes once (then they become defaults)

Put these on a pick board as rendered options with visible letters, then record the answers as the defaults for every later watch page (in `../SKILL.md`, "Rules learned", with the date):

| # | Call | Typical options |
|---|---|---|
| 1 | Which design | A Follow along, B Read it like a guide |
| 2 | Anything to take from the other | each element of the other direction as its own letter |
| 3 | The call to action | book a call, the next free live session (needs a current date first), copy the free resource with no email needed |
| 4 | Whose questions count | audience members only, or also a co-host's |
| 5 | The address scheme | all under one folder such as `/videos/`, or the watch page replaces an existing text page at its address |
| 6 | The headline | the candidates, side by side |
| 7 | A vendor named in the transcript | keep a mask ("[a <category> platform]") or name it as said on camera |

## Going live (after the creator's go, never before)

1. Re-read every live value the page carries (video id, title, duration, the CTA link) from its source in the same session.
2. The website repo: reconcile the local copy with the live site first (a local copy can be missing live routes), then add the page and deploy the way your site deploys.
3. **The same day the video goes public**, so the description's link resolves and your domain is crawled first (the effect of the order is untested).
4. Then `geo.md`, "On publish", and the YouTube description edit that adds the page link, through the live-fix step (dry run first, undo line, report).
5. Fetch the live page: 200, the rendered text read, the comments read, every link 200, the JSON-LD present in the raw HTML (`curl`, not the browser).
