# media-gen: images and video through one gateway

> Skill: `.claude/skills/media-gen/SKILL.md`. Script: `.claude/skills/media-gen/scripts/media_gen.py`. This is the reference behind the skill: what each lane is, the traps found against the live APIs, and why the guardrails exist.

## What it is

One CLI, one gateway, one key. MixRoute is an OpenAI-compatible aggregator carrying a couple of hundred models; media-gen wraps the handful a content system actually uses and puts spend guardrails around them. It replaced per-provider credit packs, which ran dry at the worst moment (one stopped a shoot).

| Say this | Model id | Where it bills |
|---|---|---|
| `nano-banana-pro` | `gemini-3-pro-image` | Google project if configured, else the gateway |
| `nano-banana-lite` | `gemini-3.1-flash-lite-image` | the gateway |
| `seedance` | `doubao-seedance-2-5-260628` | the gateway (priced per second, by resolution) |
| `veo-fast` | `veo-3.1-fast-generate-preview` | the gateway (per second, always 8s) |
| `veo` | `veo-3.1-generate-preview` | the gateway (per second, always 8s) |
| `omni` | `gemini-omni-flash-preview` (Google-direct) | your Google Cloud project, token-priced |

The script carries a rate table that drives the pre-spend estimate and the spend log. Check the provider's pricing page before you trust any figure, and re-check the table every quarter. **The gateway's own dashboard is the truth for what was billed**; it has no usable balance endpoint on the API.

**Setup.** `export MIXROUTE_API_KEY=...` (or a `.env` in the project root), then `python3 .claude/skills/media-gen/scripts/media_gen.py doctor`. `selftest` checks the guards offline.

## The two gaps you need to know about

**1. Gemini Omni Flash is not carried by the gateway.** Both `gemini-omni-flash-preview` and `gemini-omni-flash` return HTTP 503 `model_not_found`. `models` re-probes it on every run, so the day it appears the check says so. Until then Omni runs **Google-direct** (`--model omni`) on Vertex with Application Default Credentials (ADC), billing a Google Cloud project. It is token-priced, not per-second, and it honours the duration you ask for (max 10s).

**2. Veo always returns 8 seconds.** `durationSeconds` is accepted and silently ignored: asked for 4, got 8. The script warns and bills at 8s so the estimate never under-reports. **When length matters, use `seedance`**, which honours duration exactly (asked 4s at 480p, got 4.06s at 854x480).

## Five places the docs are wrong, and what is true

All found by calling the live API. The script handles every one.

| Documented | Actually |
|---|---|
| Poll response has top-level `status` and `url` | Everything nests under `data` |
| One status vocabulary | Casing varies: Seedance `SUCCESS`, Veo `succeeded` |
| Seedance returns `url` | `url` is empty; a signed 24h link is in `result_url` |
| The video URL is fetchable | `/videos/{id}/content` returns 401 without the auth header |
| `/v1/models` lists the catalogue | It does not list video models. Veo works and is absent |

The last one matters most: **absence from `/v1/models` is not proof a model is missing.** Probe `/v1/video/generations` before concluding a video model is unavailable.

## Omni is priced per token, so length is not the whole bill

Google prices Omni output per token, at a fixed number of tokens per second of 720p video. Input (text, image, reference video, audio) is far cheaper per token, and reasoning tokens bill at the text-output rate. Worth knowing when you pass references:

- an image reference costs roughly 1,100 input tokens (measured; the docs claim more, so measure rather than trust)
- **a reference video costs the same tokens per second as generating one**, so a 10-second reference clip is not free
- the script reads the real token counts off the response and prices them, so the spend log matches the invoice. It never logs an absent usage as zero: an absent bill is not a free one

An earlier version logged every Omni render as zero cost, and several renders of real spend went unrecorded before anyone noticed. That is why the usage is read off the response now.

## Images can bill a Google project too

`nano-banana-pro` routes to Vertex when `GOOGLE_CLOUD_PROJECT` is set, because Google and the gateway charge the identical list price for Gemini 3 Pro Image (a live Vertex render returned exactly the token count Google's footnote quotes). So this is not a cheaper route; it is the same price paid from a different balance, which matters when that balance is trial credit that expires whether it is used or not.

```bash
python3 .claude/skills/media-gen/scripts/media_gen.py image --prompt "..." --slug thumb              # auto
python3 .claude/skills/media-gen/scripts/media_gen.py image --prompt "..." --via mixroute            # force the gateway
```

`--via auto` (the default) uses Google when the credentials work and falls back to the gateway if Vertex returns anything unexpected, so a stale token costs a retry rather than the batch. Every render prints which wallet paid, and the spend log records it.

### The wallet guard

The dangerous failure here is not an error. It is **quietly paying cash for what another balance already covers.** That happened once for 6 renders on a stale token, and the line saying so scrolled past unread. So for `nano-banana-pro`, **when a Google project is configured** and its route is unreachable, the script refuses and prints the reauth command instead of switching:

```bash
gcloud auth application-default login                                   # the fix, almost always
python3 .claude/skills/media-gen/scripts/media_gen.py image ... --pay-cash   # deliberate cash spend
```

With no Google project configured the guard does nothing and everything runs on the gateway.

### Traps on the Vertex image endpoint

| | |
|---|---|
| **Role is mandatory** | Vertex rejects a content block with no `role` ("Please use a valid role: user, model"). The OpenAI-compatible gateway does not care. |
| **No `-preview` suffix** | `gemini-3-pro-image-preview` returns 404 on Vertex; `gemini-3-pro-image` serves. The opposite of the video lane, where the model really is `gemini-omni-flash-preview`. |
| **Location** | must be `global`, `us` or `eu`; classic Vertex regions return 400 |
| **Listing hangs** | `client.models.list()` can hang against the global endpoint. Probe a model by calling it (a wrong id 404s for free) rather than by listing |

### Getting another person onto the same Google project

They need the IAM role `roles/aiplatform.user` (the console may display it under a renamed product, "Agent Platform User"; the role id is the same). If your organisation restricts IAM members to its own domain, a personal Gmail can never be granted and the invite fails with no useful error: create them a domain account first, then grant. Sharing a project means sharing one credit pool.

### When ADC keeps expiring

If `gcloud auth application-default login` is demanded every few hours with `RefreshError: Reauthentication is needed`, the cause is usually not local. It is a server-side reauth demand from a Google Workspace "Google Cloud session control" policy, which expires the cloud session on a timer and revokes the refresh token. No script change survives that. An admin can set that policy to never require reauthentication for the relevant org unit (the security cost: a cloud session on a stolen laptop stays valid, so keep disk encryption on). Check that setting before debugging the script.

### The sign-in warning that is not a failure

The login can end with `Cannot add the project ... as the quota project because the account in ADC does not have the "serviceusage.services.use" permission`. The render still works: the script names the project in the URL, so no quota project is consulted. Proof is the newest spend-log row showing the Google wallet, or `doctor` saying credentials are live. Granting the account `roles/serviceusage.serviceUsageConsumer` makes the warning go away.

## The face lock

**Reference photos are real photographs of the people, never AI recreations.** Keep them in `content/brand/people/` and list their paths in `content/brand.md`.

Every image of a person passes **both** references, and the script puts them ahead of the prompt so the model anchors identity before it reads words:

```bash
python3 .claude/skills/media-gen/scripts/media_gen.py image \
  --prompt "..." \
  --ref content/brand/people/me-hires.png \
  --ref content/brand/people/me-ref.png \
  --resolution 2k --slug my-thumb
```

Verified live on both image models: the references are genuinely ingested (counted in the prompt's image tokens) and the renders come back as the person. Drop one and you get a different person, which is why a single `--ref` is refused unless `--allow-single-ref` says the render has no face in it.

Three more rules, all from real corrections:

- **A render whose face is wrong is never a reference for the fix.** Repeated edit passes with the shipped render in the stack, real photo alongside, came back with the same wrong face every time. Rebuild from real photographs, then edit for composition only.
- **A thumbnail is a real frame of the real people.** The model edits on the frame or builds the background; it never regenerates a person. Every thumbnail test carries at least 1 real frame from the actual video (the 1-of-3 rule).
- **An edit never changes an expression**, and a face is never invented from a text prompt.

## Story animations, never b-roll

Generated video is called a **story animation**: professional, highly relevant to what is being said, and it carries the explanation rather than decorating it. "B-roll" means mood footage under narration, which is not what this makes. Direction and taste live in `content/taste/story-animations.md`. Generated video cannot be trusted with on-screen UI text; for a legible line use Veo or Omni, or composite a real screen capture.

## Thumbnail size

- **YouTube:** 1280x720.
- **A native video upload** (LinkedIn and similar): match the video's own pixel dimensions, not just its aspect ratio. `media_gen.py thumb-size --video <file> [--image <thumb>]` prints the size and fits a picture to it.

## Guardrails

- Every call **prints its cost and waits for a yes**; `--yes` skips the prompt for an approved scripted run.
- Anything over **`MEDIA_GEN_MAX_CALL_USD`** (default 5.00) in one call is refused before a request is sent.
- Bad reference paths, over-long durations and unsupported resolutions fail **before** the spend prompt.
- Veo's ignored duration is billed at its real 8s, so estimates never under-report.
- Seedance prompts that mention text or UI get a warning before the confirm.
- Every call appends to `outputs/media-gen/spend.jsonl`; `spend` totals the month, split by wallet.
- `selftest` proves the face lock, the ceiling, the reference checks, caption parsing, thumbnail sizing and the wallet guard offline.

## Validation record (shape of the original live test)

| Test | Result |
|---|---|
| `gemini-3.1-flash-lite-image`, text only | 200, real JPEG |
| `gemini-3-pro-image` + 2 face refs, 2K 16:9 | 200, face locked, confirmed visually |
| `doubao-seedance-2-5-260628` 4s 480p | 854x480, 4.06s, h264 + aac, duration honoured |
| `veo-3.1-fast-generate-preview` | 1280x720, 8s, h264 + aac |
| `veo-3.1-generate-preview` | 1280x720, 8s, h264 + aac |
| Omni through the gateway, both ids | 503 `model_not_found` |
| Guardrails: over-cap, duration ceiling, bad resolution, missing ref, bad key | all fail clean |

The bulk of the verification cost was 2 Veo availability probes that each rendered a full 8s clip before their cost was known. Probe cheaply when you can.

## Open

- Omni on the gateway: re-probed automatically by `models`. Wire it the day it appears.
- If the gateway's Veo channel ever honours `durationSeconds`, drop the `fixed_dur` field from the 2 Veo specs in the script.
- `GEMINI_API_KEY` and `FAL_KEY` are no longer used. `doctor` flags them if present.
