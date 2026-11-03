# media-gen: pictures and story animations

> Skill: `.claude/skills/media-gen/SKILL.md` (the engine: route, model, prompt, judging), with copy-ready prompts in `.claude/skills/media-gen/reference/prompt-recipes.md`. Script: `.claude/skills/media-gen/scripts/media_gen.py`. Taste: `content/taste/story-animations.md`, `content/taste/thumbnails.md`, and `content/taste/motion-craft.md` if you keep one. This is the reference behind the skill: how the lanes work, what they cost, the traps found against the live APIs, and why the guardrails exist.

## What it is

One CLI over two wallets. **The gateway** (MixRoute, an OpenAI-compatible aggregator carrying a couple of hundred models) runs Seedance and Veo, and the image models when no Google project is set. **Your Google Cloud project** (Vertex, through Application Default Credentials) runs Gemini Omni Flash, which the gateway does not carry, and the image models when it is set. media-gen wraps the handful a content system actually uses and puts spend guardrails around them. It replaced per-provider credit packs, which ran dry at the worst moment (one stopped a shoot).

## The lanes

| Say this | Model id | Route and wallet | Cost (list price at the last check; check the provider's pricing page, prices move) |
|---|---|---|---|
| `nano-banana-pro` | `gemini-3-pro-image` | Google project when set and reachable; the gateway with `--via mixroute` or `--pay-cash`, or when no project is set | Google publishes $0.134 an image at 1K and 2K, $0.24 at 4K; the gateway charged the same |
| `nano-banana-lite` | `gemini-3.1-flash-lite-image` | Google project when its sign-in is live, the gateway unguarded when it is not | about 4 times cheaper than Pro; the script's table carries the figure |
| `omni` | `gemini-omni-flash-preview` | Google project only (Google-direct) | token-priced, about $0.10 a second of 720p (below) |
| `seedance` | `doubao-seedance-2-5-260628` | the gateway | per second, by resolution; the provider publishes a price, the gateway publishes none |
| `veo-fast` | `veo-3.1-fast-generate-preview` | the gateway | per second, always billed at 8 s |
| `veo` | `veo-3.1-generate-preview` | the gateway | per second, always billed at 8 s, about 4 times `veo-fast` |

The script carries a rate table that drives the pre-spend estimate and the spend log. Re-check it against the pricing pages every quarter. **Each provider's dashboard is the truth for what was billed**; the gateway has no usable balance endpoint on the API (its billing endpoint returns a placeholder).

**Setup is one line per wallet.** The gateway: `MIXROUTE_API_KEY=...` in your shell profile or a project `.env`. Google: `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION=global`, then `gcloud auth application-default login` once. `media_gen.py doctor` checks both; `selftest` checks the guards offline.

## Omni is priced per token, so length is not the whole bill

Google prices Omni output per token, at a fixed number of tokens per second of 720p video. At the last check: 5,792 tokens per second of 720p video output at $17.50 per 1M; input at $1.50 per 1M across text, image, video and audio; reasoning at $9.00 per 1M. That works out near $0.1014 a second of output, which held against a real bill (11 renders, 90 s of video, the credit drawn down within about 2% of the computed figure).

One 6-second render, itemised: video output 34,752 tokens $0.6082, 2 reference frames 2,200 tokens $0.0033, the prompt 263 tokens $0.0004, reasoning 590 tokens $0.0053, total $0.6172.

- an image reference costs about 1,100 input tokens (measured; Google's docs say more, so measure rather than trust)
- **a reference video costs the same tokens per second as generating one**, so a 10-second reference clip is not free
- **before the render** the script estimates from the video-output rate plus the references and runs the normal confirm, so the per-call ceiling applies to Omni too; the estimate can be a few cents low because reasoning tokens are unknown until the job runs
- **after the render** the script reads the real token counts off the response and prices them, so the spend log matches the invoice. It never logs an absent usage as zero: an absent bill is not a free one

An earlier version logged every Omni render as zero cost, and about $9 of real spend over 11 renders went unrecorded before anyone noticed. That is why the usage is read off the response now.

## Trial credit: the clock is the constraint, not the balance

A Google Cloud trial credit expires on a fixed date whether it is spent or not. At a normal content pace, a large share of it can expire unused. So before the expiry date, rerolls on Omni and Pro are close to free: go wide rather than ration. After it, the same lanes bill real money on that billing account, so **set a budget alert before the date**. The images were moved onto the Google route for the same reason: Google and the gateway charge the identical list price for Gemini 3 Pro Image (a live Vertex render returned exactly the 1,120 image tokens Google's footnote quotes), so it is not cheaper, it is the same price paid from a balance that would otherwise expire.

```bash
python3 .claude/skills/media-gen/scripts/media_gen.py image --prompt "..." --slug thumb              # auto
python3 .claude/skills/media-gen/scripts/media_gen.py image --prompt "..." --via mixroute            # force the gateway
```

### The wallet guard

The dangerous failure here is not an error. It is **quietly paying cash for what another balance already covers.** That happened once for 6 renders on a stale token, and the line saying so scrolled past unread. So for `nano-banana-pro`, **when a Google project is configured** and its route is unreachable, the script refuses and prints the reauth command instead of switching:

```bash
gcloud auth application-default login                                        # the fix, almost always
python3 .claude/skills/media-gen/scripts/media_gen.py image ... --pay-cash   # deliberate cash spend
```

`nano-banana-lite` is unguarded and falls back to the gateway. With no Google project configured the guard does nothing and everything runs on the gateway. A run that says it paid with the gateway balance when the project was expected means the sign-in is the reason.

### One image render at a time

Four parallel Pro renders on one project got two 429s; three workers in one session did it again weeks later. So `image` takes a machine-wide lock after the confirm (`MEDIA_GEN_LOCK`, default `~/.cache/media-gen/media-gen.lock`) and waits its turn; `MEDIA_GEN_NO_LOCK=1` bypasses it on purpose. The video lanes take no lock. A builder that fires 2K image bursts of its own should also wait and retry on a 429.

### Getting another person onto the same Google project

They need the IAM role `roles/aiplatform.user` (the console may display it under a renamed product, "Agent Platform User"; the role id is the same), and usually `roles/serviceusage.serviceUsageConsumer` too, which also clears the quota-project warning below. If your organisation restricts IAM members to its own domain, a personal Gmail can never be granted and the invite fails with no useful error: create them a domain account first, then grant. Do not suggest a personal-account workaround. Sharing a project means sharing one credit pool; a person who starts their own trial gets a separate credit with its own expiry instead.

**Prove a new account with one real render before promising it anything.** A machine-level health check read green while Vertex refused every render on a newly granted account (the predict permission was denied), and `doctor` would too. One Pro image (it refuses on a Vertex error), a lite image whose output says the Google project paid (lite falls back to gateway cash without refusing), or a read of the IAM binding is the proof.

### When ADC keeps expiring

If `gcloud auth application-default login` is demanded every few hours with `RefreshError: Reauthentication is needed`, the cause is usually not local. It is a server-side reauth demand from a Google Workspace "Google Cloud session control" policy, which expires the cloud session on a timer and revokes the refresh token. No script change survives that. An admin can set that policy to never require reauthentication for the relevant org unit (the security cost: a cloud session on a stolen laptop stays valid, so keep disk encryption on). Check that setting before debugging the script.

### The sign-in warning that is not a failure

The login can end with `Cannot add the project ... as the quota project because the account in ADC does not have the "serviceusage.services.use" permission`. The render still works: the script names the project in the URL, so no quota project is consulted. Proof is the newest spend-log row showing the Google wallet. Granting `roles/serviceusage.serviceUsageConsumer` makes the warning go away.

## Traps, all found live

**Setting up the Google route:**

- A missing active `gcloud` CLI account does not mean ADC is missing: Storage uploads through ADC worked while `gcloud storage` had no CLI account.
- A failed `which gcloud` can be PATH, not installation. Look for the SDK's own `bin` folder before reinstalling.
- Treat `gs://` references as Cloud objects, never as local paths to `stat` (the script skips them on purpose).
- **The Gemini API key is a separate wallet.** A key naming the same project still bills its own prepaid pool, which returns `429 credits_depleted` when empty: that 429 means the wrong wallet, not no money. `google-genai` silently prefers `GOOGLE_API_KEY` over Vertex mode, so the script removes `GOOGLE_API_KEY` and `GEMINI_API_KEY` from the environment before it builds the Vertex client. When you remove one key-first fallback from your own code, look for the next one: removing only one left another key-first branch active.
- Service-account keys are often blocked by organisation policy ("secure by default"); ADC on a person's account is the route then. Do not route around the policy.

**The gateway's API differs from its docs:**

| Documented | Actually |
|---|---|
| Poll response has top-level `status` and `url` | Everything nests under `data` |
| One status vocabulary | Casing varies: Seedance `SUCCESS`, Veo `succeeded` |
| Seedance returns `url` | `url` is empty; a signed 24h link is in `result_url` |
| The video URL is fetchable | `/videos/{id}/content` returns 401 without the auth header |
| `/v1/models` lists the catalogue | It does not list video models. Veo works and is absent |

**Absence from `/v1/models` is not proof a model is missing.** Probe `/v1/video/generations` before concluding a video model is unavailable.

**The gateway's balance can go negative silently.** `doctor` printed "key works, 257 models reachable" while the balance was negative and every Seedance submit returned 403 `insufficient_user_quota`. The doctor reads no balance; that 403 means a top-up.

**Veo returns 8 s through the gateway whatever is asked** (asked 4, got 8; asked 6, got 8), so the script warns and bills 8. Google's own spec offers 4 and 6 on plain and first-frame jobs and requires 8 only with references, extension or 1080p; whether the gateway ever honours 4 or 6 is untested beyond those 2 calls. **When length matters, use `seedance`**, which honours duration exactly (asked 4 s at 480p, got 4.06 s at 854x480).

**Seedance with a first frame rejects an explicit ratio** (`InvalidParameter.TaskTypeConstraint`); the script sends `ratio: adaptive`. First and last frame cannot share a job with reference images (2 provider docs say so); the script will send both without refusing, so leave `--ref` off. The script's reference role string differs from the native API's `reference_image`; untested. An 8 s 720p Seedance job outran the script's 900 s poll and its task id was lost: keep jobs short, or note the id from the log.

**The Vertex image endpoint:**

| | |
|---|---|
| **Role is mandatory** | Vertex rejects a content block with no `role` ("Please use a valid role: user, model"). The gateway does not care. |
| **No `-preview` suffix** | `gemini-3-pro-image-preview` returns 404 on Vertex; `gemini-3-pro-image` serves. The opposite of the video lane, where the model really is `gemini-omni-flash-preview`. |
| **Location** | must be `global`, `us` or `eu`; classic Vertex regions return 400 "Unsupported location" |
| **Listing hangs** | `client.models.list()` can hang against the global endpoint. Probe a model by calling it (a wrong id 404s for free) rather than by listing |

**Omni:**

- Not on the gateway: both `gemini-omni-flash-preview` and `gemini-omni-flash` return 503 `model_not_found`. `models` re-probes it on every run.
- Video references must be `gs://` URIs. A video reference makes the job an `edit`, which rejects `aspect_ratio` and needs the asked duration to equal the reference's exactly.
- An overwritten `gs://` object stays cached by URI, so upload each revision under a new name (a content hash in the object name does it for you).
- A failure's reason is on the `model_output` step of `interaction.model_dump()`, never `interaction.error`; the script reads it from there.
- **Output:** 1280x720, 24 fps, h264, with an AAC track to drop. Length follows the ask (5 s and 6 s honoured); an 8 s result came from the edit task. The AAC track comes back whatever is asked: the script never sends `--no-audio` to Omni.
- Max 10 s a generation; the script refuses more before any spend.

## The face lock

**Reference photos are real photographs of the people, never AI recreations.** Keep them in `content/brand/people/`, one subfolder per person, and list their paths in `content/brand.md`. Keep them current: a model reads an old photo (a beard since shaved) as identity and draws the old face, so for a thumbnail the recording frame of that video is the strongest identity reference.

Every image of a person passes **both** references, and the script puts them ahead of the prompt so the model anchors identity before it reads words:

```bash
python3 .claude/skills/media-gen/scripts/media_gen.py image \
  --prompt "..." \
  --ref content/brand/people/me/hires.png \
  --ref content/brand/people/me/ref.png \
  --resolution 2k --slug my-thumb
```

Verified live on both image models: the references are genuinely ingested (1,120 image tokens counted) and the renders come back as the person. Drop one and you get a different person, which is why a single `--ref` is refused unless `--allow-single-ref` says the render has no face in it. 0 references pass, and `video` has no face check, so there the rule holds by hand.

More rules, all from real corrections:

- **A render whose face is wrong is never a reference for the fix.** Repeated edit passes with the shipped render in the stack, real photo alongside, came back with the same wrong face every time. Rebuild from real photographs, then edit for composition only.
- **A thumbnail is a real frame of the real people.** The model edits on the frame or builds the background; it never regenerates a person. Every thumbnail test carries at least 1 real frame from the actual video (the 1-of-3 rule).
- **An edit never changes an expression**, and a face is never invented from a text prompt.
- **A person may ask for an AI edit of their own look**, and then it is built: on the real frame plus 2 or more real photos of them, anyone else in the frame unchanged, labelled options shown. Never another person's face without that person's word.

## Story animations, never b-roll

Generated video is called a **story animation**: professional, highly relevant to what is being said, and it carries the explanation rather than decorating it. "B-roll" means mood footage under narration, which is not what this makes. Direction and taste live in `content/taste/story-animations.md`; the prompt order and the frame facts are in the skill.

**What one test set taught** (24 clips over 5 script lines in 5 directions: a photoreal office, an isometric diorama, a flat 2D mascot world, image-first stills, and a set built on published-guide rules: one unbroken scene, locked camera, timecodes, first and last frame). The creator picked the flat 2D clip on every row they answered, over the photoreal and rule-shaped clips the session had recommended. What the skill took from it: the route table (exact things to HTML, a world to generated video); Omni as the default lane; the prompt order (one action, one camera intention, one scene, the end state early, the character card and the plate word for word, colour words, plain quality words, exclusions last); the frame facts (one `--start` still is held as the first frame; two images run as `reference_to_video` and neither is held); the count drift (of 6 clips asked for 6 bars, the 3 counted ended on 7 or more and 2 ended with none); frame-strip judging; and the reroll budget. A first adversarial review of the rebuilt skill failed it on 13 points, among them a misread clip and a verdict judged against an earlier clip instead of the reference image: judge against the source, always.

**Still untested:** a last-frame pin on Omni through this script; a character card written from the reference against the looser one behind the pick; Seedance first and last frame on these clips; a deterministic mascot layer over a generated plate; Veo at 6 s through the gateway; a prompt past 6 s in timecode form; the "No X" lines against the noun list beyond 1 take each; the Omni multi-turn edit on the same interaction, which the script does not wire.

## Omni as a second camera angle (measured, and not dependable)

On real talking-head footage Omni is not a dependable second camera. Of 11 runs on one camera track, the only survivor was a calm 6 s clip at 15 to 20 degrees, hands down, holding for about 3.3 s. What was learned, so the next run does not relearn it:

- send the real audio in (the same clip scored 0.30 on lip sync without it and 0.93 with it)
- never attach a reference image of the real frame (sync fell to 0.30 and 0.64)
- Omni ran 10 to 45 ms early, fixed by shifting the real audio
- outputs are 24 fps; a 0.8x slowed input gives true 30 fps but loses the locked camera
- 5 of 11 angles drifted or snapped back, so every output needs a frame check for where the angle holds
- hands are always dropped, ghosted or invented, and the room behind the speaker is always redrawn

A real-pixel punch-in (sync 0.985) is the safer default cutaway.

## Thumbnail size

- **YouTube:** 1280x720.
- **A native video upload** (LinkedIn and similar): match the video's own pixel dimensions, not just its aspect ratio. `media_gen.py thumb-size --video <file> [--image <thumb>]` prints the size and fits a picture to it.

## Guardrails

- Every call **prints its cost and waits for a yes**; `--yes` skips the prompt for an approved scripted run and never lifts the ceiling.
- Anything over **`MEDIA_GEN_MAX_CALL_USD`** (default 5.00) in one call is refused before a request is sent, Omni included (from its pre-render estimate).
- Bad reference paths, over-long durations (Omni's 10 s included) and unsupported resolutions fail **before** the spend prompt.
- Veo's ignored duration is billed at its real 8 s, so estimates never under-report.
- Seedance prompts that mention text or UI get a warning before the confirm; Omni says out loud which flags it does not send.
- One image render at a time, machine-wide, through the lock file.
- Every call appends to `outputs/media-gen/spend.jsonl` with the wallet that paid; `spend` totals the month, split by wallet.
- `selftest` proves the face lock, the ceiling, the reference checks, caption parsing, thumbnail sizing, the wallet guard, the render lock and the Omni estimate offline.

## Validation record (shape of the original live test)

| Test | Result |
|---|---|
| `gemini-3.1-flash-lite-image`, text only | 200, real JPEG |
| `gemini-3-pro-image` + 2 face refs, 2K 16:9 | 200 in 62 s, face locked, confirmed visually |
| `doubao-seedance-2-5-260628` 4 s 480p | 854x480, 4.06 s, h264 + aac, duration honoured |
| `veo-3.1-fast-generate-preview` | 1280x720, 8 s, h264 + aac |
| `veo-3.1-generate-preview` | 1280x720, 8 s, h264 + aac |
| Omni through the gateway, both ids | 503 `model_not_found` (then wired Google-direct) |
| Omni Google-direct, 6 s, 1 image reference | 1280x720, 6.04 s, 24 fps, about $0.64, 40 s to render |
| Guardrails: over-cap, duration ceiling, bad resolution, missing ref, bad key | all fail clean |

The bulk of the first verification cost was 2 Veo availability probes that each rendered a full 8 s clip before their cost was known. Probe cheaply when you can.

## Open

- Omni on the gateway: re-probed automatically by `models`. Wire it the day it appears.
- Veo could move onto the Google project the way Omni did; unbuilt.
- `doctor` should read the gateway balance, or run a 1-second probe, before it says ready.
- If the gateway's Veo channel ever honours `durationSeconds`, drop the `fixed_dur` field from the 2 Veo specs in the script.
- `GEMINI_API_KEY` and `FAL_KEY` are no longer used. `doctor` flags them if present.
