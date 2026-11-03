# YouTube SEO: the search pack for one long form

> Module of the search-visibility skill. Writes the YouTube half of `content/videos/<slug>/search/search-pack.json` (contract in `../SKILL.md`). Evidence: `evidence.md` sections 1, 2 and 7 (levers 1, 2, 9, 10, 11, 20).

## What YouTube says it reads (official, `evidence.md` section 1)

Relevance from the title, tags, description and the video itself; engagement for that query; quality signals on the topic. Give every video a unique description, pick 1 or 2 main words and put them prominently in both the title and the description, and check the search terms each video is found by. Tags play a minimal role. Chapters: timestamps in the description, the first at 00:00, at least 3, each at least 10 seconds.

## 1. The phrase

**Starting default (change it in your taste files):** the phrase is the core term your audience types for what the video teaches, plus the sub-niche when the video serves one. When a video is titled with a contested head term, it fights for that term.

| The video is | `phrase` |
|---|---|
| a walkthrough for one sub-niche | the core term plus the sub-niche, written with a comma: "<tool> for <audience>, <sub-niche>" |
| a general walkthrough shown on one sub-niche example | the same sub-niche row, so the sub-niche sits in a phrase line as well as in the title, the h1 and the meta ("A <sub-niche> Example") |
| a general walkthrough with no sub-niche example | the core term alone |
| titled with the head term itself | the head term |
| not about the core topic (an episode, a broader business video) | the words your audience would type for its one promise, from the channel's own search terms first; say so in one line and ask the creator when nothing on the channel's terms fits |

**The form of the field:** `phrase` is the core, a comma, then the sub-niche. A check splits it on the comma: the core must be in the first phrase line of the description, and every word of the sub-niche somewhere in the top lines, so the sentence a reader sees still reads naturally ("... shown on a <sub-niche> example"). The second line carries the core only where it fits a sentence: a check that forced it into both lines produced phrase stuffing. Never use a separator that appears inside the phrase itself (a phrase like "<tool> for <audience>" already contains " for ", so a " for " split cannot find the sub-niche).

**What people actually type:** pull the channel's YouTube search terms for the last 90 days (YouTube Analytics, traffic source "YouTube search", by search term; available through the YouTube Analytics API or Studio). Write the top terms and their counts into the pack's notes. Refresh this list at the Friday scoreboard (`geo.md`), never from memory.

**Check a phrase's results page before choosing it.** A phrase can belong to another audience entirely: on YouTube, "AI ROI" belongs to retail investing, not to business owners. Open the search results signed out and look at who owns them.

## 2. Title candidates (proposals only)

3 candidates in `title_candidates`, then **the creator picks**. They go on the video's pick board (or a repackaging board for a live video), each with its rendered thumbnail beside it: the thumbnail and the title are one story (`content/taste/thumbnails.md`), and a thumbnail is never proposed in words.

- **The phrase leads the title**, then one concrete promise. In a niche scan, the titles that win a head term usually lead with the query words, then a promise (tips, every feature, setup, a specific task), often a year (`evidence.md` section 6). A named product in the title tends to help reach in a tutorial niche; measure it on your own channel before you lean on it.
- **Starting default for a guest who serves one region:** a podcast episode whose guest serves one state or region leads with it (region, then the guest's role, then the promise). A guest with a national audience keeps a national title. The region comes from the guest's own material and the tape, never a guess.
- **About 68 characters at most**, where YouTube cuts titles in search and on a phone.
- **The packaging still passes its 4 questions** (familiar format, open loop, who the viewer becomes, authority; `content/PRINCIPLES.md` section 4). A search-shaped title that fails them is a worse title, not a better one; offer at least one candidate that is the creator's own packaging framing with the phrase worked in.
- A year ahead of the current one may read as a typo to some searchers (`evidence.md` section 1, untested).
- **Test & compare** runs up to 3 titles and thumbnails and judges on watch-time share (official); which candidates go into the test, and which goes first, is the creator's call, because slot 1 owns the launch window.

## 3. Chapters

`chapters: [{start_seconds, label}]`, from the **final cut** (never the script). Your posting step should refuse a long form whose description's chapters do not start at 0:00.

- **First at 0** (`start_seconds: 0`), at least 3, each at least 10 seconds, in order. A video that shipped with its first chapter at 0:31 got an untitled chapter drawn in front of it by YouTube.
- **Labelled the way your audience searches, not the way the script names a section.** A label is a phrase someone could type or ask an assistant: the action plus the named product or task ("Install the <plugin> marketplace", "Which <tool> settings to use for <task>", "Do you need the enterprise plan? Training, retention, client work"). Not "Part 2", not "The setup", not a joke.
- **Why it pays:** Google prefers key moments the creator sets in the YouTube description, and timestamped YouTube citations in AI Overviews and AI Mode often span 2 to 5 chapters of one video (`evidence.md` lever 1: official guidance plus a vendor measurement).
- **Any on-screen progress bar in the edit uses the same chapter list** (`content/taste/must-dos.md`, the chapters row), so a chapter change after the edit is a change the editor makes too; say so.

## 4. The description

The full text goes in `description`; the upload step appends the chapters when the text carries none.

**The order (starting default: "phrase first, links right under"):**

1. **The phrase line or lines at the top, kept tight:** 1 to 2 sentences, at most about 20 words in total, every one a word somebody searches; the `phrase` in the first, the sub-niche in one of them, no link in either. They are new public copy, so the voice read against `content/taste/voice.md` runs on them before anything is applied.
2. **Your own link block, word for word, right under, with no blank line before it**: the fixed lines from `content/taste/must-dos.md` (the description row), with the booking or resource line matched to what this video actually asks for, read off the transcript; then the watch-page link right after the first link once the page is live ("Chapters, steps and the full transcript: https://..."). Always `https://` on the front (`scripts/copy_check.py`, rule `bare-link`). 2 variants worth supporting: a video that promises "the first link below" on camera keeps that link first, and a video whose tape makes no ask gets the block without a booking line.
3. The guest's name line and links, when there is a guest (a guest bio paragraph goes below or goes).
4. 2 to 3 short paragraphs about the video, written for your audience, naming the products and tasks (named entities are what AI answers quote, `evidence.md` section 3).
5. The chapters.
6. Every link the video promises on camera, each fetched and returning 200 in the session that ships it.

**If your must-dos say links open every description**, the 2 orders conflict: decide which one you keep and change the other file, so a session never has to guess.

**End screen (starting default):** every long form in the topic carries your flagship video for the phrase as a chosen end-screen video, plus the subscribe element. End screens are set in Studio; the Data API has no end-screen write.

**Replacing old lines:** when an instruction says to "update" an old line (an old contact address, an old bio), replace it with its current version taken word for word from your newest live description and your fixed link block. Never invent an address, a bio line or a claim. Where no current version exists anywhere on record, that is a question to the creator before the write, never a silent drop and never reported as "updated" (a run once did both, and a contact line came off several live videos). An outdated address with a current home is swapped, not dropped.

**Never in a description:** an internal receipt or source line (a draft once ended with one that would have gone public); an unsourced figure; a link to a page that is not yours where yours exists; a dead old address; a client's name; a topic your taste files rule out. **Unique per video**: never paste one video's description onto another. **A cut's "full version" link** is checked against the caption tracks of the video it points at before it is kept.

## 5. Tags and language

- `tags`: the phrase, its close variants from the search-terms list, the products named in the video, and the common misspellings. Tags help mainly with misspellings (official, `evidence.md` lever 20); keep the list short and never stuff it. YouTube caps tags at 500 characters in total.
- `default_language` and the audio language both set explicitly (for example `"en"`), and read back after the write. Some update tools rewrite them, which left one channel with several mixed codes (`en`, `en-US`) across its videos; send the whole snippet on every edit.

## 6. Captions

**The file:** an `.srt` under `content/videos/<slug>/search/`, with `captions_path` set. Its source, in order:

1. The edit's own word-level transcript of the final cut, made with a keyterms list of the names on the tape (`.claude/skills/shorts-editor/scripts/transcribe.py`, with `transcribe_deepgram.py` as the fallback and `transcribe_local.py` last).
2. For a live video with no local tape: YouTube's own caption track through the Data API (`captions.list`, then `captions.download`; this works on your own videos and refuses with 403 on other channels'), corrected by hand against the video.

**What the correction fixes:** proper nouns first (your product names, people's names, the channel's own name), numbers as digits (some engines write them as words), no client name the edit masked. Auto-captions mangle exactly these words (`evidence.md` section 1).

**Why:** YouTube recommends uploaded captions because automatic quality varies (official). That they help ranking is a **hypothesis** with no YouTube statement behind it (`evidence.md` section 9); they are done because they cost almost nothing and fix the words every index reads. The upload is part of the live fixes (rule 3 in `../SKILL.md`). A caption upload is expensive on the YouTube API quota (check the current quota cost table), so a catch-up of many videos spreads over several days. A video can carry a manual track that failed to process: read the track state before uploading over it.

## 7. The topic playlist

Check where the topic's videos sit today: on an older channel they often sit in wrong-topic playlists, a neighbour that tells YouTube the wrong thing. Create 1 playlist per topic or series, take the videos out of the wrong-topic lists, and give every playlist a description. Do it one operation at a time, each with a read-back and an undo line, dry run first; then set each pack's `playlist_id` to the video's primary playlist. Until then `playlist_id` is null and nothing fails on it. Playlists can take their own result slot in a niche (a third party's topic playlist did for a head term, `evidence.md` section 1, an anecdote); a series playlist (one video per sub-niche) is a proposal for the creator, not a default.

## 8. Things to flag, never fix

- **2 public copies of one recording competing for the same phrase.** Which one stays is the creator's; deleting or hiding a video is a person's hand.
- **A public placeholder with no recording** (a scheduled live that never ran).
- Any title or thumbnail that would do better on search: a candidate on the pick board, never a live edit.

## 9. The check before the pack is done

By eye or by your own script: the phrase is in the title candidates and the phrase sentence; chapters start at 0, at least 3, at least 10 s each, labels read like searches; every link in the description fetched 200 this session; no internal line, no client, no em dash (`python3 scripts/copy_check.py <description file>`); `title_candidates` are on the pick board, not in a live field.
