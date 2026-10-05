---
name: media-gen
description: >-
  Generate images and video through one gateway and one key: thumbnails, title cards, brand
  images, story animations. Use for - "make the thumbnail", "generate an image of", "we need a
  title card", "render that story animation", "show me 4 thumbnail options", "what size does
  this thumbnail need to be", or any step in the content system that needs a picture or a clip
  that does not exist yet. Covers nano-banana-pro and nano-banana-lite (images), Seedance and
  Veo / Veo Fast (video), and an optional Google-direct Omni lane. The only skill in this pack
  that spends money: it prints the cost of every call before it runs and refuses anything over a
  ceiling the user sets. NOT for editing existing footage (that is shorts-editor or
  long-form-editor). NOT for the board presented from on camera (that is on-camera-board).
---

# Media Gen

**Load before any step:** `content/PRINCIPLES.md` (the constitution: it wins over every step here), then `content/taste/thumbnails.md`, `content/taste/packaging.md` and, for video, `content/taste/story-animations.md`. The full reference, with the traps and the reasons behind them, is `content/reference/media-gen.md`.

**This skill spends real money.** Every call prints its cost before it runs, waits for a yes, and refuses anything above the per-call ceiling. Nothing here should surprise anyone on a bill.

**One script does everything:** `.claude/skills/media-gen/scripts/media_gen.py`. Run it from the project root (or set `MEDIA_GEN_ROOT`), because the spend log, the default output folder and the default face references are all relative to that root.

---

## Setup

```bash
echo 'export MIXROUTE_API_KEY=your_key_here' >> ~/.zshrc   # required: the gateway
echo 'export MEDIA_GEN_MAX_CALL_USD=5.00' >> ~/.zshrc      # the per-call ceiling you choose
echo 'export MEDIA_GEN_FACE_REFS=content/brand/people/me-hires.png,content/brand/people/me-ref.png' >> ~/.zshrc
source ~/.zshrc
```

A `.env` in the project root works too; an exported variable always wins.

```bash
python3 .claude/skills/media-gen/scripts/media_gen.py doctor     # what is set, what is missing
python3 .claude/skills/media-gen/scripts/media_gen.py selftest   # offline guard checks, no key needed
```

`doctor` is the right first command every time something behaves unexpectedly. `models` lists what the gateway currently carries. `spend` prints what this skill has spent, split by wallet.

Optional: `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` (`global`, `us` or `eu`) route `nano-banana-pro` and the `omni` video lane through a Google Cloud project instead of the gateway's cash balance, at the same list price. `doctor` says whether that route is live. Without it everything bills the gateway, which is fine and is the default.

**Without a key, packaging still happens, it just happens elsewhere.** Do not describe thumbnails in words as a workaround. Ask the creator to build candidates in whatever design tool they use and bring the images back, then run the packaging questions on what they brought.

---

## The models, and when to reach for each

| Say this | Model id | Use it for |
|---|---|---|
| `--model nano-banana-pro` | `gemini-3-pro-image` | the thumbnail workhorse; **thumbnail boards always render here** |
| `--model nano-banana-lite` | `gemini-3.1-flash-lite-image` | cheap exploration of non-face, non-logo directions |
| `--model seedance` | `doubao-seedance-2-5-260628` | video that must be an exact length; material physics |
| `--model veo-fast` | `veo-3.1-fast-generate-preview` | the default story animation lane |
| `--model veo` | `veo-3.1-generate-preview` | when it has to look filmed |
| `--model omni` | `gemini-omni-flash-preview` (Google-direct) | reference-driven shots with native audio, if a Google project is set |

Rates live in the script's table and drive the pre-spend estimate. They are estimates: check the provider's pricing page, and treat the gateway's dashboard as the truth for what was billed.

**The traps, all verified against the live API:**

- **Veo always returns 8 seconds**, whatever `--duration` says. The script warns and bills at 8s so the estimate never under-reports. **When the length matters, use `seedance`**, which honours duration exactly.
- **Omni is not on the gateway** (it returns `model_not_found`). It runs Google-direct with `--model omni`: max 10s, returns 1280x720 at 24fps with an audio track to mute. Video references must be `gs://` URIs, the duration must match a reference video exactly, no `aspect_ratio`, and a replaced object is cached by URI, so always upload under a new name.
- **Seedance with a first-frame image** takes its aspect from the image; the script sends `adaptive` for you.
- **Absence from the gateway's model list is not proof a model is missing.** Video models are not listed there and still work.

**Write the two video prompt families differently.** Omni and Veo want one flowing cinematographic paragraph. Seedance wants an explicit shot list with numbered beats and named hex colours, and it holds a reference's colour discipline harder.

**Seedance and on-screen text.** When a Seedance prompt mentions text, UI, a screen, a phone or an interface, the script warns before the confirm: generated video renders garbled words, invented logos and wrong numbers. For a legible line use Veo or Omni, or composite a real screen capture in afterwards.

---

## The commands

```bash
MG=".claude/skills/media-gen/scripts/media_gen.py"

# an image of a person: BOTH real-photo references, every time
python3 $MG image --prompt "..." \
  --ref content/brand/people/me-hires.png --ref content/brand/people/me-ref.png \
  --aspect 16:9 --resolution 2k -n 4 --slug my-thumb

# a story animation
python3 $MG video --model veo-fast --prompt "..." --start still.jpg --duration 8 --slug scene

# the captioned contact grid, then the grid AND every full-size image opened
python3 $MG board --dir content/videos/<slug>/thumbs --captions captions.json

# the size a thumbnail must be for a native video upload, and fit a picture to it
python3 $MG thumb-size --video content/videos/<slug>/renders/final.mp4 --image thumb.png
python3 $MG thumb-size --platform youtube        # always 1280x720
```

Every spending command takes `--yes` to skip the confirmation. Use it only when the creator has already approved this specific run.

---

## The rules that matter more than the flags

**Never propose a thumbnail in words. Build it and show it.** Candidate titles go captioned underneath, because the thumbnail and the title are one story and neither is judged alone.

**A thumbnail is built on a REAL frame of the real people, never a recreation.** Pull a frame from the actual video. The model may edit ON the frame (cleanup, background, relight, cut-out) or build a background, but nothing under the words regenerates a person. A thumbnail is designed (crop, depth, grade, type), not a still with a plate dropped on it.

**The 1-of-3 rule.** Every thumbnail test carries at least one candidate that is a real frame from the actual video: the person talking to camera with what is on screen in that video behind them. A test where every option is generated tells you which generation you prefer, not whether generation beats reality.

**Every generated image of a person points at a real photograph of them.** Real photographs live in `content/brand/people/` (or pass any path with `--ref`). Pass **both** references together; the script puts them ahead of the prompt so the model anchors identity first, and it refuses a single reference unless you add `--allow-single-ref`, which is only for renders with no face in them. Drop one reference and the render comes back as a different person.

**A face is never invented from a text prompt, and an edit never changes an expression.** Keep the face register honest.

**A render whose face is wrong is never a reference for the fix.** The model anchors on the image it edits, so repeated edits with the bad render in the stack return the same wrong face. Rebuild from real photographs with the layout in words, then edit the clean result for composition only.

**Real product logos only.** Use the real asset file, never a model-invented lookalike. Keep the paths to face references and logos listed in `content/brand.md`, and copy them from there: a guessed path is how a face lock silently breaks and how a fake logo ships.

**Typography the model keeps drifting** (quote marks, a dropped glyph) is cheaper to composite afterwards (Pillow, or an HTML page rendered to PNG in headless Chrome) than to re-prompt.

**Generated video is a story animation, never b-roll.** It carries the explanation of something said, professional and relevant. It does not pretend to be footage of a thing that happened.

**Show the grid, then ask.** Render, build the grid with `board`, put it in front of the creator, then ask. Never ask them to choose by number before they have seen the options.

---

## Boards go through `board`, and "open" is never claimed

`board` builds the captioned contact grid (filename and caption under each image), saves it into the same folder, then opens the grid **and every individual image** in one call and prints that exact invocation.

- **A board is built by this command, never improvised.** The grid is for scanning; the full-size files are what get judged. Judging a set off a downscaled grid is a known failure.
- **Never write that images are open unless this command's output is in context.** If you did not see the `exited 0` line, you do not know they are open.
- A board page with video on it goes over `scripts/serve_outputs.py`, never as a `file://` page (empty players otherwise).

---

## Thumbnail size for native video uploads

**A native video post (LinkedIn and similar) takes its custom thumbnail's pixel size from the video, not just its aspect ratio.** A 1280x720 thumbnail on a 1920x1080 video has made a post fail wholesale with an error that named neither. `thumb-size --video <file>` prints the size and `--image` fits a picture to it; render natively at that size where you can. **YouTube stays 1280x720.**

When uploading a native video with a custom thumbnail: add the video, wait for its upload bar to reach 100%, only then add the thumbnail. If it stalls, try the same picture as PNG, then as a lighter JPEG. A native video's thumbnail usually cannot be changed once the post is live, so never plan "post first, thumbnail after". The last-resort fallback is a render with the thumbnail as the video's first second.

**When a platform refuses an upload with a generic error, post the smallest honest version first** (a 60-second clip of the same encode), then add back 1 variable at a time. **And after any publish that took more than 1 attempt, read the profile back and count the posts**: a platform can accept retries while still showing the error.

---

## Money

- **The ceiling.** Anything over `MEDIA_GEN_MAX_CALL_USD` (default 5.00) is refused before a request is sent, even with `--yes`. Raise it deliberately and say why, or make the call smaller. Never split a job to slip under it.
- **Cheap first, then commit.** Explore non-face directions on `nano-banana-lite`, then commit to Pro once the direction is picked. Thumbnail boards with faces or logos render on Pro, because lite's face and logo fidelity is not judgeable.
- **Iterate on 1, then batch.** 4 variations of a wrong prompt cost 4 times what finding out costs.
- **Video is the expensive lane.** Ask before rendering one, every time.
- **One render at a time on a Google project.** Parallel calls come back 429.
- **The wallet guard.** When a Google project is configured and its route is unreachable, `nano-banana-pro` refuses rather than quietly paying cash; the fix is almost always `gcloud auth application-default login`, and `--pay-cash` is the deliberate override. With no Google project configured the guard does nothing.
- Every call appends a row to `outputs/media-gen/spend.jsonl` with the wallet that paid. `spend` totals it.

## When a model id stops working

Providers rename these. Run `models` (the configured table, then what the key can actually reach), pass the current id with `--model-id`, and update the table in the script in the same session.

---

## When the creator reacts to a render

Their reaction is taste and it goes into `content/taste/thumbnails.md` or `content/taste/packaging.md` in the same session, with the render it was about named. "Too busy" is not a rule. "Faces read at thumbnail size, screenshots do not" is.
