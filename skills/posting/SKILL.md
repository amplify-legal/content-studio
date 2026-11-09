---
name: posting
description: >-
  The auto-post module's driver: the weekly posting plan (content/posting/plan.jsonl), the approval
  gate, the runner that posts approved legs through each platform's official API, the watcher that
  moves missed legs and writes hand cards, and the log that proves every post. Use for - "build next
  week's posting plan", "fill the week", "approve the week", "what posts today", "did it post",
  "go live with posting", "a post did not go", "the full video is live, add the link", "I posted
  the TikTok", "read the posting log", "set up YouTube posting". Full install level only. NOT for
  writing captions (that is post-writer), choosing pieces (content-waterfall), or any message or
  connection request to a person (always a human's hand).
---

# Posting

**Load before any step:** `content/PRINCIPLES.md`, then `content/profile/summary.md` and
`content/setup/preferences.md` (which platforms they post on now, which they want, and whether
they chose auto-posting at all), then `posting/README.md` (the module's own doc: the life of a
leg, the platform notes, the setup). This skill is the order of work; the
README is the reference. Every command below runs from the project folder.

The rule over everything here: **nothing posts without a named person's approval on the exact
file and the exact words, the default is a dry run, and every post is proven by reading the
platform back.** TikTok, Substack and any platform with no posting API for the creator's account
are hand cards. Never a session cookie, never a website script, never computer control on a
platform's site to post. Messages and connection requests to people are never automated.

---

## When it runs

| Moment | What happens | Who |
|---|---|---|
| Sunday (or by hand) | `plan.py next-week` lays next week's empty legs; this skill fills them and asks for approval | The machine lays and fills; the creator approves |
| Every 10 minutes | `runner.py tick` then `watch.py tick` (from `posting/launchd.example.plist` or `posting/cron.example.txt`) | The machine |
| Each night, optional | `routines/posting-refresh.md` adjusts what is not locked and not posted | The machine; nothing it touches stays approved |
| When the creator says so | Approve, hold, record a hand post, add a link, go live | The creator, through this skill |

If `content/posting/config.json` does not exist, stop and set it up first: copy
`posting/config.example.json` there (`cp -n`), then walk the creator through the slots (which
days, what time, which platforms) and the setup section of `posting/README.md`. Every route
starts on `fake`. **Lay the first week from what they already told you:** `platforms_now`,
`platforms_wanted` and `auto_posting` in `content/setup/preferences.md`, and
`content/profile/platforms.md`. Keep slots only for the platforms they post on now; ask before
adding one from `platforms_wanted`. If `auto_posting` says no, the runner stays a dry run and
every leg is a hand card: put every platform in `hand_platforms`.

---

## 1. Build the week

1. `python3 posting/scripts/plan.py next-week` (or `skeleton --start <Monday>`). It prints the legs
   it laid and the check.
2. **Fill each leg from the bench**: finished pieces that the creator has watched or that cut
   review has cleared. Never raw footage, never a piece they dropped, never a short nobody watched.
   ```bash
   python3 posting/scripts/plan.py set <leg> file=/full/path/clip.mp4 thumb=/full/path/thumb.jpg \
     'caption=...' title='...' piece=<slug> --by "machine"
   ```
3. **Captions come from `post-writer`**, one native caption per platform, never one pasted
   everywhere. Run `scripts/copy_check.py` on each, and the voice-check reviewer if they have one.
4. **The creator's dictated words and picks get locked** the moment they give them:
   `plan.py lock <leg> caption file --by "<their name>"`.
5. `python3 posting/scripts/plan.py check --week <Monday>`. Fix every `FAIL` before asking for
   approval. A `LINK` line is information, not a failure: the short goes first.

---

## 2. The approval

1. **Show every caption in full in chat**, one code box per leg, named by platform, day and time,
   and end the turn. The question comes in the next turn. A go on a video is not a go on its words.
2. Ask: approve the whole week, approve some legs, or change words. Changed words are applied with
   `set` and shown again in full.
3. Approve with their name, the date and where they read it:
   ```bash
   python3 posting/scripts/plan.py approve <Monday> --week --by "<name>, <date>, read in session"
   python3 posting/scripts/plan.py approve <leg> --by "<name>, <date>, read in session"
   ```
   `approve` refuses an empty name and any leg failing a gate, and prints every caption it
   approved. Paste that printout back if it differs from what they read.
4. Never approve on their behalf, never infer an approval from a thumbs up on something else, and
   never write `approved_by` by hand. `set` refuses it.

---

## 3. Going live (dry run first, for a week)

1. **Practice**: every route `fake`, run `python3 posting/scripts/runner.py tick --live` and
   `watch.py tick` with `--at` times across one day. Show the creator the log and a hand card.
2. **Connect the accounts** (`posting/README.md`, "Setup, per platform"). The sign-ins are the
   creator's hand. Pin each connection id in the config. Switch the routes to `composio`, then
   run `runner.py whoami <platform>` and ask the creator whether that id is their own channel or
   profile. Only on their yes does it go in `expected_account_id`. The runner refuses every upload
   until it matches.
3. **A dry week**: schedule the tick WITHOUT `--live`. Each morning, read yesterday's
   `would-post` lines with the creator: right legs, right times, nothing missing.
4. **One real leg**: `runner.py tick --live --leg <id> --force`, then the creator looks at the post
   on the platform, and the log's `read-back` line must say `live`.
5. **Add `--live` to the schedule**, on one computer only. Say in one line which computer runs it.

---

## 4. Reading the log

`content/posting/log.jsonl`, one JSON line per event. To see one leg's story:
`grep '<leg id>' content/posting/log.jsonl`.

| Event | Means |
|---|---|
| `would-post` | Dry run: this leg would have posted now (once a day per leg) |
| `accepted` | The platform took it and gave a post id. Not proof yet |
| `scheduled` | YouTube: private video, `publishAt` set to the slot |
| `read-back` | The platform was read: `state` is `live`, `scheduled`, `processing`, `missing` or `unconfirmed` |
| `posted` | Proven. The proof is on the line and the leg |
| `full-video-comment` | The link went under the post, once |
| `refused` | Not posted, and why (no name, a failing check, a changed file) |
| `error` | An upload failed; 3 of them mark the leg `failed` |
| `re-slot` | The watcher moved a missed leg, from and to, and by which rule |
| `hand-card` | A card was written for the creator's hand |
| `posted-by-hand` | The creator recorded a hand post with its URL (`waiting_for_read_back` true on YouTube and LinkedIn) |
| `not-approved` | A filled leg is still not approved 3 hours before its slot, in the plan the runner reads |
| `unconfirmed-stop` | 24 hours without proof: the creator looks at the post and records it |

When the creator asks "did it post": read the leg's last lines, then say the fact, the proof (the
post id and URL), and anything that needs them. Never say posted off an `accepted` line.

---

## 5. Day to day

- **"I posted the TikTok"**: their word is the record.
  `plan.py posted <leg> --url https://... --by "<name>"`. Ask for the URL only if they have it
  handy; never make believing them depend on it.
- **"I uploaded it myself on YouTube"** (or LinkedIn): the same command with the post's URL. The
  leg waits as `uploaded` and the runner's next live tick reads it on the channel before it is
  marked `posted`. Never mark a machine-platform leg posted from a tick or a board alone.
- **A `not-approved` warning**: a filled leg near its slot is not approved in the plan the runner
  reads. Ask whether they approved it somewhere else (another computer, another copy); if so,
  approve it here with their name, after showing the caption again.
- **"The full video is live"**: `plan.py links-pending`, then `plan.py add-link <leg> 'Full video:
  https://...' --by "<name>"` for each. The runner comments it under the posted ones on its next
  tick; hand legs get it pasted by hand.
- **"Hold that one"**: `plan.py set <leg> review=hold --by "<name>"`. The runner and the watcher
  leave it alone. `review=` clears the hold.
- **A missed leg**: the watcher moves it by the rules in `posting/README.md`. Never ask the creator
  where a missed leg goes; tell them where it went.
- **A second session never posts a leg the schedule owns.** Use the same commands; never call an
  adapter from a conversation.

---

## Errors

| What you see | Why | What to do |
|---|---|---|
| `approve needs --by with a person's name` | No name given | Ask who approves, then run it again with their name |
| `NOT approved, failing a gate` | `check` found a problem | `plan.py check`, fix, show the changed words again, approve |
| `REFUSED: status approved but no approved_by` | Somebody edited the plan by hand | Show the caption, get the approval, run `approve` |
| `BLOCKED: file changed since approval` | The file was re-rendered | Show the new file to the creator; `set file=...` again, approve again |
| `ACTIVE connection(s) ... refusing to post` | 0 or 2+ connected accounts match | `composio connections list --toolkit <name>`, pin the right id in the config |
| `REFUSED: the connected <platform> account is X, not the creator's Y` | The connection is somebody else's account (a co-host, an old channel) | Never post around it. Find which account is linked, reconnect the creator's own, run `whoami` again |
| `REFUSED: no expected_account_id pinned` | The platform was switched to a real route without the pin | `runner.py whoami <platform>`, the creator confirms it is theirs, pin it |
| `slot more than 6 h old` | The computer was asleep or the tick was off | Nothing: the watcher moves it on its next tick |
| `read-back unconfirmed` (LinkedIn) | The platform refused the read | The creator opens the post URL and looks; then `plan.py posted` |
| `ERROR (3/3)` and status `failed` | 3 upload errors | Read `last_error`. A generic refusal: try the smallest honest version of the same file first (a short cut, same encode). Fix, then approve again |
| `needs a public URL` (Instagram) | No hosting set | Put `file_url` on the leg, or fill the config's `hosting` block |
| `publishAt did not stick` | YouTube kept the video unscheduled | It is private, nothing is public. `runner.py tick --live` retries the schedule while the slot is ahead |
| A quota error from YouTube | The shared Composio project ran out | Move YouTube to your own Google Cloud project (`posting/README.md`) |

---

## What this skill never does

- Approves, or writes `approved_by` or `status=approved` by hand.
- Posts to TikTok, Substack, or any hand platform, by any route.
- Uses a session cookie, a website scrape, or computer control on a platform's site to post or read.
- Sends a message or a connection request to anybody.
- Deletes a post, or tidies a duplicate. It reports the count; deleting is the creator's hand.
- Runs the runner live on a second computer.
