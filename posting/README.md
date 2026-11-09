# Auto-post: the posting module

This module posts what you approved, when you planned it, on the platforms that allow a machine to post, and proves each post by reading it back from the platform. Everything else becomes a hand card with the paste ready.

It is the full level of the install. You can run a whole content system without it: a weekly plan posted by hand works fine. Turn it on when posting every day on several platforms has become the bottleneck.

The rule that governs all of it: **the machine's hands are fast, the human keeps the heart.** You pick the pieces and approve every word. The machine does the clicking.

---

## What is in the folder

| File | What it does |
|---|---|
| `posting/scripts/plan.py` | The plan: lay the week, fill legs, check, approve, lock, links, missed legs |
| `posting/scripts/runner.py` | Posts approved legs whose slot has come. A dry run unless you say `--live` |
| `posting/scripts/watch.py` | Moves missed legs, writes hand cards, reminds you. Never posts |
| `posting/scripts/adapters/` | One file per platform (`youtube.py`, `linkedin.py`, `instagram.py`), the interface in `base.py`, and `fake.py`, a pretend platform for practice and the self-tests |
| `posting/config.example.json` | Your slots, platforms, routes and limits. Copy it to `content/posting/config.json` |
| `posting/launchd.example.plist`, `posting/cron.example.txt` | The 10-minute schedule, for a Mac or for cron |

In your project the module keeps its state in `content/posting/`: `plan.jsonl` (the legs), `log.jsonl` (every decision, dry runs included), `hand-cards/` and `config.json`.

**Install** (the full level does this for you, from your project folder):

```bash
cp -R ~/content-studio/posting ./posting
mkdir -p content/posting
cp -n posting/config.example.json content/posting/config.json
```

The module lives in `posting/` at your project root; your settings live in `content/posting/config.json`, which `cp -n` never overwrites.

The skill that drives it is `.claude/skills/posting/SKILL.md`. Ask Claude Code to "build next week's posting plan" or "go live with posting" and it reads that skill.

---

## The shape of a week

```
Sunday      plan.py next-week        lays next week's empty legs from your slots
            you and Claude           fill each leg from the bench of finished, reviewed pieces; a native caption per platform
            plan.py check            every gate, before anything is approved
            plan.py approve --week   you approve the week, every caption read in full
Every 10 min runner.py tick          posts the approved legs whose slot has come (dry run until you add --live)
            watch.py tick            moves missed legs, writes hand cards, reminds you
Every night routines/posting-refresh.md (optional) adjusts what is not locked and not posted yet
```

A **leg** is one post on one platform at one time. The same video can go to 4 platforms: that is 4 legs, each with its own caption and hook.

---

## The life of a leg

| Status | Means | Who moves it on |
|---|---|---|
| `empty` | A slot with nothing in it yet | You, or the night, filling it from the bench |
| `draft` | Filled, not approved | You, with `plan.py approve --by "<your name>"` |
| `approved` | Approved by a named person, on the exact file | The runner at the slot, or the watcher's hand card |
| `uploaded` | The platform took it and gave an id; proof not read yet (on YouTube: a private video scheduled for its slot) | The runner's read-back on the next tick |
| `posted` | Read back from the platform: this is the proof, with the post id and URL on the leg | Done. The full-video comment follows when a link exists |
| `hand` | A card is waiting for your hand (TikTok, Substack) | You post it, then `plan.py posted <leg> --url ... --by ...` |
| `uploaded` with `posted_by_hand` | You uploaded it yourself in the platform's own app (YouTube Studio, the LinkedIn composer) and recorded the URL | The runner reads it on the channel and marks it `posted`; a record alone never does |
| `failed` | 3 errors on the upload | You: read `last_error`, fix, approve again |
| `skipped` | An empty slot given up to a moved leg | Nobody |

---

## The approval gate

- **Nothing posts without `approved_by`.** `approve` refuses an empty name. `set` can never write `approved_by` or `status=approved`. The runner refuses a leg marked approved with no name, even if somebody edited the file by hand.
- **Approval is on the exact file.** `approve` records the file's sha256. If the file changes, the approval drops and the runner refuses the leg.
- **Approval is on the exact words.** A change to the caption, title, description or first comment drops the approval.
- **A go on a video is not a go on its words.** `approve` prints every caption in full as it approves. The skill shows them to you in chat first. If you have not read that exact text, you have not approved it.
- **A short reaches the plan only after you have watched it, or a cut review has cleared it.**
- **The post goes on the creator's own account, or nowhere.** Before every upload the runner reads the connected account's own id (the platform's "who am I" read: the channel id, the member id, the Instagram user id) and refuses unless it equals `expected_account_id` in the config. An empty pin is refused too. `runner.py whoami <platform>` prints the id to pin. Why: a post on the wrong profile cannot be moved, only deleted, and in the live system 2 shorts once went out on a co-host's profile because a second account was linked to the same tool.
- **An approval counts once it is in the plan the runner reads.** The runner reads `content/posting/plan.jsonl` fresh on every tick, so an approval made in any session on that computer reaches it (the self-test approves from a separate process and posts on the next tick). An approval made on another computer, or in a copy that stopped syncing, does not. The watcher warns once a day about any filled leg still not approved 3 hours before its slot (`approval_warn_hours`), so a lost approval is caught before the slot passes.
- **One computer runs the runner.** 2 computers posting the same plan post twice.

---

## Locked fields: what the night never touches

Each leg carries a `locked` list. Put your dictated words and your picks on it: `plan.py lock <leg> caption file`. Any change made `--by night` to a locked field is refused in code. Everything else the night may change, and every change goes back to draft for your approval (see `routines/posting-refresh.md`).

---

## Links later: the short goes first

Every short carries the full video's link in its comments, on every platform. But no short waits for it.

1. The short posts when its slot comes, link or no link.
2. `plan.py links-pending` lists every leg that still owes its link. `check` prints a `LINK` line for each. Neither is a hold.
3. When the long form is live: `plan.py add-link <leg> 'Full video: https://...' --by "<you>"`. The approval is kept.
4. On a leg already posted, the runner's next tick posts that text as a comment, once (the comment id goes on the leg, at most 3 tries). On a hand leg, the card carries the first comment for you to paste.

---

## Missed legs

The watcher moves a missed leg; it never deletes one and never leaves one on the floor.

- **A machine leg** (YouTube, LinkedIn, Instagram) more than `stale_hours` (6 by default) past its slot, unposted, moves to **the soonest open slot of its kind in the same Monday-to-Sunday week**. Only when this week has no room does it go to next week. A day is open while it holds fewer legs of that kind than `max_per_day`. The runner never posts a leg late; it waits for the move.
- **A hand leg** (TikTok, Substack) **stays in its slot, postable, until its slot's day ends**, however late you post it. After midnight it moves by the same rule.
- A move keeps the words, the locks and the approval, and writes a `re-slot` line in the log. An empty leg on the new day gives up its slot (`skipped`) when the day would otherwise go over its limit.

---

## Proof: every post is read back

A composer going quiet is not proof. Generic errors have been seen on posts that actually went up, sometimes more than once. So the runner reads each post back and records the proof on the leg and in the log.

| Platform | What counts as proof | When it cannot read |
|---|---|---|
| YouTube | `processingStatus` succeeded, a duration above 0, and privacy public. A row in a listing is not proof | The leg stays `uploaded` and the next tick reads again |
| LinkedIn | The caption found on the post, through the API or the public post page | In the live system the API read of a personal post came back Forbidden. If neither read works, the leg stays `uploaded` for 24 hours, then the log says to look at it yourself and record it with `plan.py posted` |
| Instagram | The media id among your most recent posts | The leg stays `uploaded` and the next tick reads again |

A failed read retries the read, never the upload. A leg with a post id is never uploaded again.

**A post you made by hand is proven the same way.** If you uploaded a planned video yourself on YouTube or LinkedIn, run `plan.py posted <leg> --url <the post's URL> --by "<you>"`. The leg takes the id from the URL and waits as `uploaded`; the runner's next live tick reads it on the channel and marks it `posted`, and never uploads it. A status that only the machine's own posts can update is wrong every time a person posts. On a hand platform (TikTok, Substack), or a URL that carries no id (an Instagram link), your word with the URL is the record.

---

## Platform notes

### YouTube

- **Scheduling is native.** The runner uploads up to `youtube_upload_lead_days` (7) ahead as a **private** video, then sets `publishAt` to the slot. YouTube publishes it by itself. The runner reads it back after the slot.
- **A long form needs a thumbnail, and chapters from 0:00** (YouTube draws no chapters otherwise). `check` refuses both. A Short's cover is picked by hand in the YouTube app; the API thumbnail does not show on a Short.
- **Quota.** Composio's default YouTube connection runs on Composio's own Google Cloud project, which every Composio customer shares. The live system this module came from hit that pool's daily limit on a day it had uploaded nothing. The fix is your own Google Cloud project (setup below), whose quota is yours alone. The numbers: a project gets 10,000 units a day by default. Many guides say an upload costs 1,600 of them, which caps a project at about 6 uploads a day. When the live system read Google's quota calculator on 2 Nov 2026, uploads were listed in their own bucket of 100 a day instead. Untested here: open your project's Quotas page for YouTube Data API v3 and read your own numbers.
- **Unverified projects.** Google used to lock uploads from an unverified API project to private. Google's `videos.insert` page, read on 2 Nov 2026, said that restriction no longer applies. Read your first upload back and check its privacy before you trust it.

### LinkedIn

- **A native video always carries its custom thumbnail, and the thumbnail goes up with the video.** It cannot be changed once the post is live, so "post first, add the thumbnail after" is never an option. The only route found that carries one is LinkedIn's own Videos API (initialize the upload with a thumbnail, upload the parts and the picture, finalize). Composio's ready-made upload tool has no thumbnail field, so the adapter calls the Videos API through Composio's proxy. `check` refuses a LinkedIn video with no thumbnail.
- **Make the thumbnail at the video's own pixel size.** In LinkedIn's own composer, a 1280x720 thumbnail on a 1920x1080 video failed the whole post with a generic error. Whether the API is as strict is untested; match the size anyway.
- **Tagging people.** A person is tagged only when the leg's `mentions` carries their LinkedIn member id. LinkedIn gives a member id only inside the app that person connected, so in practice you can tag only people who connected their own LinkedIn to the same app. Everyone else is named untagged, or tagged by your hand. Untested in this module.
- **Messages and connection requests are never automated**, by this module or anything else. Only posts.

### Instagram

- Reels on a **professional account** (Business or Creator). Instagram fetches the video from a **public https URL**, so the file needs hosting: put `file_url` on the leg, or name an upload command in the config's `hosting` block.
- Limits the live system worked to: audio at 48 kHz at most, caption 2,200 characters, 5 hashtags at most, and a Reel over 3 minutes is not shown to non-followers.

### TikTok and Substack: hand cards

- **TikTok**: at the time of writing, TikTok's developer guidelines do not allow a posting API for a tool that uploads to accounts you or your team manage, and an unaudited app posts privately only. So TikTok is a hand card. A third-party scheduler that holds its own audited access is a possible route; this module does not ship one.
- **Substack** has no publishing API. The post is a shorter piece that links home, never a copy.
- The watcher writes the card from 07:00 on the leg's day: `content/posting/hand-cards/<date>-<platform>.md`, with the file path, the caption in full, the first comment, and the command to record the post. You post it from the platform's own app. Never a session cookie, never a website script, never a tool clicking through the site for you.

---

## Setup, per platform

Pick one route per platform in `content/posting/config.json` (`adapters.<platform>.route`). The example config starts every platform on `fake`, so nothing can leave your computer until you change it.

### The easy route: Composio

[Composio](https://composio.dev) holds your sign-ins and calls each platform's official API for you.

1. Install the Composio CLI and sign in (follow Composio's own install page).
2. Connect each account once: `composio link youtube`, `composio link linkedin`, `composio link instagram`. Each opens a sign-in page. Sign in with the account you post from.
3. List the connections: `composio connections list --toolkit youtube` (and the same for the others). Copy the id of the one you want into `adapters.<platform>.composio_account`. The runner refuses to post unless exactly 1 active connection matches, so a second account can never be picked by mistake.
4. Set `route` to `composio` for that platform, delete `account_id` (it is for the fake route only), and run `python3 posting/scripts/runner.py whoami <platform>`. If the id it prints is YOUR channel or profile, put it in `expected_account_id`. Until then the runner refuses every upload on that platform.

**YouTube on your own quota (recommended once you post daily).** Composio's default YouTube connection shares Composio's quota with every customer. To get your own:

1. In the Google Cloud console, create a project.
2. Enable **YouTube Data API v3** on it.
3. Set up the OAuth consent screen (External, then publish it to production so the sign-in does not expire after 7 days). Add yourself as the user.
4. Create an **OAuth client** of type Web application, with Composio's redirect address as the authorised redirect URI (Composio's "custom auth config" page names it).
5. In Composio, create a custom auth config for YouTube with that client id and secret, then connect your channel through it.

The live system did exactly this. Composio's own docs describe it: their default OAuth app shares quota across all users, your own app gets a dedicated quota. One thing it found: a connection made through a custom auth config lived in a different Composio project, and the plain `composio` commands could not see it. Check that `composio connections list --toolkit youtube` shows your new connection before you pin it; if it does not, ask Composio's support which project it landed in. Untested in this port.

### The direct route: each platform's own API (untested stubs)

The direct adapters are stubs. Each file's docstring names the calls it would make. Build them only if you want to hold the tokens yourself.

| Platform | What you need |
|---|---|
| YouTube | A Google Cloud project with YouTube Data API v3 enabled, an OAuth consent screen and client, scopes `youtube.upload` and `youtube.force-ssl`, and a refresh token you keep out of the repo |
| LinkedIn | A LinkedIn developer app with the **Share on LinkedIn** product (the `w_member_social` scope) for posts and videos on your personal profile. Reading a personal post back may need a scope that product does not give |
| Instagram | An Instagram **professional** account linked to a **Facebook Page**, a Meta developer app with the Instagram Graph API and the `instagram_content_publish` permission. Meta also offers an Instagram-login variant that skips the Page; untested here |

---

## Going live: a dry week first

1. **Practice on the fake route.** Lay a week, fill 2 legs, approve them, and run `runner.py tick --live` with every route still `fake`. The fake platform keeps its posts in `content/posting/fake-platform.json`, so you can watch the whole life of a leg with nothing leaving your computer.
2. **Connect the real accounts** (setup above) and switch the routes to `composio`.
3. **Run a dry week.** Schedule the tick (`launchd.example.plist` or `cron.example.txt`) WITHOUT `--live`. Every day, read the log: each `would-post` line says what would have gone out and when. Fix what reads wrong.
4. **Post 1 real leg by hand-run:** `runner.py tick --live --leg <id> --force`. Then look at the post on the platform yourself, and check the log's `read-back` line says `live`.
5. **Add `--live` to the schedule.** That one word is the switch.

---

## Switching it off

Remove the cron line (`crontab -e`, delete the posting line) or the launchd job
(`launchctl unload ~/Library/LaunchAgents/com.example.posting-tick.plist`, then delete the file).
After that nothing ticks and nothing posts. The plan, the log and the hand cards stay in
`content/posting/`, so you can post from them by hand or switch it back on later. To stop only
the machine posting and keep the watcher's cards and reminders, take `--live` off the runner line.

---

## What was tested, and where

This module is a generalised port of a posting system that runs live every day. Port means: the same rules, rewritten without that system's accounts, paths and private tools.

| What | Status |
|---|---|
| The approval gate, the file hash, words dropping approval, locked fields, the checks, the week skeleton, links later, both missed-leg rules, one post per leg, read-back retrying the read, the full-video comment once, the account identity refusal, an approval from another process reaching the runner, a hand upload marked posted only from a channel read, the not-approved warning, hand cards, reminders | **Tested offline in this port** by the 3 self-tests, on the fake adapter |
| The Composio calls for YouTube (private upload, publishAt, read-back), LinkedIn (video with custom thumbnail through the Videos API, written posts, first comment) and Instagram (Reel, publish, comment) | **Tested in the live system this was ported from**, October and November 2026, through Composio. Rewritten here; **untested in this port** against a real account |
| LinkedIn read-back through the public post page, LinkedIn @-mentions, the hosting command, the YouTube thumbnail on a long form, the `whoami` reads (YouTube `channels?mine=true`, LinkedIn's member id, Instagram's user id), the `composio connections list` output shape on your CLI version | **Untested** |
| The direct routes for all 3 platforms | **Stubs, untested** |
| TikTok and Substack posting by machine | **Not built, by design**: hand cards |

Run the self-tests any time. They touch nothing real:

```bash
python3 posting/scripts/plan.py --selftest
python3 posting/scripts/runner.py --selftest
python3 posting/scripts/watch.py --selftest
```
