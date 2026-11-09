---
name: media-gen
description: >-
  Generate pictures and story animations: a thumbnail on a real frame, a title card, a brand
  image, a still to animate, a 3 to 10 second story animation that shows the sentence being
  said on tape. Use for - "make the thumbnail", "render that story animation", "animate this
  line", "generate an image of", "we need a title card", "show me 4 thumbnail options", "what
  size does this thumbnail need to be", a clip with your mascot, or any step that needs a picture
  or a clip that does not exist yet. One script: Gemini Omni Flash (the default story-animation
  lane when a Google Cloud project is set), Seedance 2.5 and Veo 3.1 through one gateway, and
  nano-banana-pro and nano-banana-lite for images. The only skill in this pack that spends money:
  it prints the cost of every call before it runs and refuses anything over a ceiling you set.
  NOT for editing existing footage (shorts-editor, long-form-editor). NOT for exact numbers, UI or
  layout that must be right to the pixel (HTML or HyperFrames, recorded). NOT for the board
  presented from on camera (on-camera-board).
---

# Media Gen: pictures and story animations

**Load before any step:** `content/PRINCIPLES.md` (the constitution: it wins over every step here), then the taste file for the job: `content/taste/thumbnails.md` and `content/taste/packaging.md` for a picture, `content/taste/story-animations.md` (and `content/taste/motion-craft.md` if you keep one) for video. This file is the engine: which route, which model, how the prompt is built, how a clip is judged. What good looks like is taste and lives in those files. Copy-ready prompt shapes are in `reference/prompt-recipes.md` beside this file. The full reference, with the traps, the costs and the reasons behind them, is `content/reference/media-gen.md`.

**This skill spends real money.** Every gateway and image call prints its cost before it runs, waits for a yes, and refuses anything above the per-call ceiling. Nothing here should surprise anyone on a bill.

**One script does everything:** `.claude/skills/media-gen/scripts/media_gen.py` (`doctor`, `image`, `video`, `board`, `thumb-size`, `models`, `spend`, `selftest`). Run it from the project root (or set `MEDIA_GEN_ROOT`), because the spend log, the default output folder and the default face references are all relative to that root.

**How sure each fact is.** Most of the video findings below rest on 1 test set (24 clips over 5 script lines, all on Omni) plus 1 follow-up test. They are the current best read, not settled craft. Anything marked untested has not been tried through this script.

---

## The four rules that hold on every render

1. **A real person's face is never invented from a text prompt.** Every image that shows a real person passes 2 or more real photographs of them from `content/brand/people/` as references. The script enforces part of this: `image` with exactly 1 reference is refused unless `--allow-single-ref` says there is no face in the render; 0 references pass, and `video` has no face check, so there the rule holds by hand. **When a person asks for an AI edit of their own look** (hair, styling, looking older or more polished), it is built, not refused: render on the real frame plus 2 or more real photos of them as references, keep anyone else in the frame unchanged, and show labelled options. Never edit another person's face without that person's word. The faithful-face rule governs edits nobody asked for; it is not a reason to refuse the person in the picture.
2. **A thumbnail is built on a real frame of the real video.** The image model edits on the frame (cleanup, background, relight, cut-out) or builds the background; it never regenerates a person and never changes an expression. An AI-edited picture of a person is not a thumbnail photo, even one approved for a social cover: the approval covered that cover. A thumbnail is never proposed in words: it is built and shown with candidate titles captioned underneath, and every test carries at least 1 real frame of the person talking to camera. Detail and the round shape are in `content/taste/thumbnails.md`.
3. **Generated video is a story animation, never "b-roll".** It shows the sentence on tape while it is said, so a viewer with the sound off still gets the claim. Quote the tape line and write the sound-off sentence at the top of the prompt file before anything renders; with no line, there is nothing to render.
4. **A render whose face is wrong is never the reference for the fix.** The model anchors on the image it edits: 5 edit passes with the bad render in the stack came back with the same face. Rebuild from the real photographs, then edit the clean result for composition only.

---

## Setup

```bash
echo 'export MIXROUTE_API_KEY=your_key_here' >> ~/.zshrc   # the gateway: Seedance, Veo, and images when no Google project is set
echo 'export MEDIA_GEN_MAX_CALL_USD=5.00' >> ~/.zshrc      # the per-call ceiling you choose
echo 'export MEDIA_GEN_FACE_REFS=content/brand/people/me/hires.png,content/brand/people/me/ref.png' >> ~/.zshrc
source ~/.zshrc
```

A `.env` in the project root works too; an exported variable always wins.

**Optional, and the default for story animations once set:** `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` (`global`, `us` or `eu`; classic Vertex regions are refused), then `gcloud auth application-default login` once. That routes `omni`, `nano-banana-pro` and `nano-banana-lite` through your Google Cloud project at the same list price as the gateway. It matters most when that project carries trial credit, which expires whether it is spent or not.

```bash
python3 .claude/skills/media-gen/scripts/media_gen.py doctor     # what is set, what is missing
python3 .claude/skills/media-gen/scripts/media_gen.py selftest   # offline guard checks, no key needed
```

`doctor` names a missing gateway key, an unset Google project or a stale sign-in. It reads no balance and checks no library, so it can say "ready" while a render still fails (see When something breaks). `models` lists what the gateway currently carries. `spend` prints what this skill has spent, split by wallet.

**Without a key, packaging still happens, it just happens elsewhere.** Do not describe thumbnails in words as a workaround. Ask the creator to build candidates in whatever design tool they use and bring the images back, then run the packaging questions on what they brought.

---

## Pick the route before the model

| The clip has to... | Route | Why |
|---|---|---|
| carry an exact number, a proportion, a UI or a screen | HTML or HyperFrames, recorded | generated video drifts on all of these: of 6 clips asked for 6 bars, the 3 that were counted ended on 7 or more, and 2 more ended with no bars at all |
| show one thing happening in a world with depth, light or a character | generated video, below | precision carries no meaning there |
| keep a flat mascot inside a photoreal scene | one unbroken scene, a locked camera, the character card in words and the mascot sheet as a reference; otherwise a flat world, or the mascot animated deterministically over a generated plate | in one set, photoreal scenes mostly came back with the mascot rounded or blocky 3D; 1 clip of that shape kept it pixel-true |
| be a thumbnail | a real frame plus an image-model edit, or a code composite for typography | rule 2 |

## Which video model

| Lane | Use it for | What it does, measured | Wallet |
|---|---|---|---|
| `--model omni` (Gemini Omni Flash, Google-direct) | **the default for story animations** when a Google project is set | 3 to 10 s a generation; 5 s and 6 s asked, honoured; renders in 40 to 60 s; roughly $0.10 a second of 720p, priced off its own token count; returns 1280x720, 24 fps, with an AAC track whatever is asked | your Google Cloud project |
| `--model seedance` (Seedance 2.5) | length past 10 s (up to 30 s), material physics, a reference's colour held hard | honours duration exactly (4 asked, 4.06 returned); an 8 s 720p job outran the script's 900 s poll and its task id was lost, so keep jobs short or note the id; blocks identifiable real faces; garbles on-screen text, and the script warns | the gateway, per second by resolution |
| `--model veo-fast`, `--model veo` | a filmed look where 8 s is fine | always returns 8 s through the gateway and the script bills 8; `--ref` and `--end` are not sent on this lane | the gateway, per second, always 8 s |

Rates live in the script's table and drive the pre-spend estimate. They are estimates: check the provider's pricing page, because prices move, and treat each provider's dashboard as the truth for what was billed.

**What the script does on Omni** (`cmd_omni`; `cmd_video` hands off to it before the gateway checks): it refuses a duration over 10 s before any spend; it estimates the job from Google's published video-output rate plus the references and runs the normal confirm, so the per-call ceiling applies; the real cost prints after the render, from the job's own token count, and that is what lands in the spend log (the estimate can be a few cents low, because reasoning tokens are unknown before the run). It does not send `--no-audio`, `--end` or `--negative`, and it says so when you pass them. It picks Omni's task from the images: none is `text_to_video`, 1 (a `--start` or a single `--ref`) is `image_to_video`, 2 or more is `reference_to_video`, and any video reference makes it `edit`.

**Seedance and on-screen text.** When a Seedance prompt mentions text, UI, a screen, a phone or an interface, the script warns before the confirm: generated video renders garbled words, invented logos and wrong numbers. For a legible line, build it in HTML, or composite a real screen capture in afterwards.

**Absence from the gateway's model list is not proof a model is missing.** Video models are not listed there and still work.

---

## The prompt

Write it in this order, then check it against the list. Copy-ready shapes are in `reference/prompt-recipes.md`.

1. **The tape line and the sound-off sentence** sit at the top of the prompt file, never inside the prompt (rule 3).
2. **One action and one camera intention per clip.** A camera move counts as an action; lock the camera when the subject already has several moving parts. A single move on a simple subject is fine (a slow glide down the floors of a cutaway building was one of the picked clips).
3. **On Omni, ask for one scene:** "In a single unbroken scene, no scene cuts", because Omni cuts between shots by default (Google's Omni guide). Clips of 5 to 6 s that did not ask showed no hard cut; the reason for the line is longer clips, untested past 6 s here.
4. **The payoff and the end state early and in words** ("until no red is left") so the model weights them. Write the count, but do not rely on it: see the route table.
5. **The character card, word for word, in every prompt of a set**, never paraphrased, because when the words and the reference image disagree, the words win. In one set the card said "two small black square eyes" while the drawing had eye holes the background showed through: every clip took the black eyes, and 1 grew antennae the drawing never had. So write the card from the reference image, not from memory.
6. **One art-direction plate pasted unchanged into every prompt of a set**: the world, the light, the colour words.
7. **Colours as words on Omni** ("deep teal", "warm off-white"). Hex codes came back as a palette strip with garbled labels in the opening frames. Hex is fine on Seedance.
8. **Quality in plain adjectives** ("polished, high-end animated film"). A phrase that reads like a product name or a sticker comes back as a caption: "premium explainer-animation finish" rendered as on-screen lettering.
9. **Exclusions last, in the prompt text** (only Veo takes `--negative`). Both short lines ("No dialogue. No on-screen text.") and a noun list ("Exclude: watermark, label, title card, lettering, palette swatch") came back clean on 1 take each; Google's guide recommends the noun form. Name "no watermark, no label, no title card" whenever a style word could be read as a label.
10. **Length.** Up to 6 s on Omni both shapes worked: one paragraph with the beats in order, and timecode beats `[0-1s] ... [1-5s] ...`. Published guides say "over about 5 s, write a timeline, not a paragraph" (and for Seedance, any clip longer than 8 s); past 6 s it is untested here.
11. **The two prompt families.** Omni and Veo want one flowing cinematographic paragraph. For Seedance, older notes found an explicit shot list with numbered beats and named hex colours held best; current published guides say keep it under about 60 to 100 words in a six-slot order (subject, action, scene, style, camera, audio), because past that it drops requirements. Which wins on your clips is untested; try both on one line.
12. **Silent.** `--no-audio` sends the audio-off flag to Seedance and Veo (whether the files come back silent is unchecked). Omni ignores it and always returns an AAC track, so write "Silent." in the prompt and mute on the timeline, which happens anyway under a voice.
13. **Which input carries what.** Words decide who is in the scene and what happens, and the mood and light; a reference image decides a character's exact look; a reference video decides a camera move's feel or a choreography. Google's Omni guide gives 3 reference clips of 3 s each, but an `edit` job took a 9 s reference, so that limit is untested against the script.

## Stills and frames

- **One still as `--start` is held as the first frame on Omni.** It runs as `image_to_video`, and all 3 clips made that way opened on their still (a mean pixel gap of 2.6 to 7.2 out of 255 between still and first frame, against 30 for a two-image job). Use it to pin where a clip starts. Stitching on it (the next clip's `--start` is the previous clip's last frame, the prompt says only what happens next, the cut sits at a natural point, `ffmpeg -f concat -c copy` joins them) is the published method and untested here.
- **A pinned start does not pin the end.** One clip drew its bars and then lost them: its final frame at full resolution showed grey lines with no bars.
- **Two images are not held as frames.** `--start first.png --ref last.png` runs as `reference_to_video`: the clip reframed the opening and ended on about 10 bars where the stills carried 4. A tag line naming the first and last frame did not make them literal. Through this script there is no tested way to pin a last frame on Omni; when the exact end state is the claim, build it in HTML or overlay it deterministically.
- **A single `--ref` with no `--start` also runs as `image_to_video`,** and of 4 clips checked none opened on that reference image. Use `--start` when you mean a first frame.
- **Make the still on `nano-banana-lite` first and on Pro once the direction is picked**; a still with no face that passes 1 reference needs `--allow-single-ref`. An edited end frame is an edit of the first ("... Keep everything else the same.") so the pair matches. Every route redraws a mascot to some degree, so judge it against the original sheet.
- **On Seedance**, `--start` and `--end` are first and last frame. The script will also send `--ref` in the same job without refusing, and the provider docs say the two modes cannot mix: leave `--ref` off. Whether the gateway maps the script's reference role string to Seedance's own is untested.

- **A polished twin of a real frame is judged against that frame before it is offered.** On one thumbnail round 6 twins built from real frames each changed an eye, a mouth, a head tilt or the framing; none was offered, and the real frames went on the board (2026-11-05). An edit the creator asks for changes only what they named, proven by a pixel diff against the picked file (`content/taste/thumbnails.md`, faces and real people).
- **A carousel is designed, never a frame with a caption box** (`content/taste/carousels.md`): read that file before rendering any carousel slide.

## Draft, judge, keep

- **Rewrite the prompt before rerolling it.** One published creator went from 0 usable takes in 10 rerolls to 10 in 10 by rewriting to one action and one locked camera. Then plan for about 3 generations per usable shot. On trial credit that expires anyway, go wide rather than ration.
- **Judge every clip at full resolution before anyone sees it,** with the strip, first-frame and last-frame commands in the recipes file: the sound-off sentence; the count on the first and last frame; the end state on the last frame; the mascot against its sheet; the first second for lettering, swatches or labels. The four tests in `content/taste/story-animations.md` and cut-review still gate anything going into a cut.
- **A clip that is nearly right gets a narrow edit, not a reroll:** "Make X. Keep everything else the same.", at most about 3 edits before drift. Through this script an edit is a new Omni `edit` job with the clip uploaded to `gs://` as a video reference, the asked duration matching the reference exactly, and a new object name on every upload (a replaced object is cached by URI). The conversational edit on the same interaction is not wired.
- **Finish last.** A stylised look may need retiming (12 poses a second reads as stop motion for clay or paper); upscale or interpolate only after the pick. Neither is wired here.
- **Show options side by side with their labels**, in the same order as the files. A board page with video goes over a local server that answers range requests, never as a `file://` page (empty players otherwise).
- **Runner scripts log unbuffered** (`python3 -u`), because block-buffered logs hid a gateway error for a whole queue, and **a chained queue runs as one script or waits on a done-file**, never `pgrep` on its own name, which matched itself and hung for 4 hours.
- **When Omni says only "failed"**, the reason is on the `model_output` step of `interaction.model_dump()`, not `interaction.error`; the script now reads it from there. One job failed with no reason on a still of a page of pseudo-text with red marks while the same scene rendered on the mascot sheet: the image differed, and the cause is untested.

---

## Images

- **Cheap first, except thumbnails.** Exploration boards with no face and no logo run on `nano-banana-lite`; thumbnail boards run on `nano-banana-pro`, because lite's face and logo fidelity cannot be judged.
- **Real product logos only.** Use the real asset file, never a model-invented lookalike. Keep the paths to face references and logos listed in `content/brand.md`, and copy them from there: a guessed path is how a face lock silently breaks and how a fake logo ships.
- **Identity comes from how the person looks now.** If the reference photos are a year old (a beard since shaved, a different haircut), the model draws the old face. The recording frame of that video is the best identity reference; an older brand photo alone is not.
- **Typography the model keeps drifting** (quote marks, a dropped glyph) is cheaper to composite afterwards (Pillow, or an HTML page rendered to PNG in headless Chrome) than to re-prompt.
- **Show the grid, then ask.** Render, build the grid with `board`, put it in front of the creator, then ask. Never ask them to choose by number before they have seen the options.

## The commands

```bash
MG=".claude/skills/media-gen/scripts/media_gen.py"

# an image of a person: BOTH real-photo references, every time
python3 $MG image --prompt "..." \
  --ref content/brand/people/me/hires.png --ref content/brand/people/me/ref.png \
  --aspect 16:9 --resolution 2k -n 4 --slug my-thumb

# a story animation on Omni (needs GOOGLE_CLOUD_PROJECT)
python3 -u $MG video --model omni --duration 6 --aspect 16:9 --ref mascot.png --prompt "..." --slug scene

# a story animation through the gateway
python3 $MG video --model veo-fast --prompt "..." --start still.jpg --duration 8 --slug scene

# the captioned contact grid, then the grid AND every full-size image opened
python3 $MG board --dir content/videos/<slug>/thumbs --captions captions.json

# the size a thumbnail must be for a native video upload, and fit a picture to it
python3 $MG thumb-size --video content/videos/<slug>/renders/final.mp4 --image thumb.png
python3 $MG thumb-size --platform youtube        # always 1280x720
```

Every spending command takes `--yes` to skip the confirmation. Use it only when the creator has already approved this specific run. `--yes` never lifts the ceiling.

## Boards go through `board`, and "open" is never claimed

`board` builds the captioned contact grid (filename and caption under each image), saves it into the same folder, then opens the grid **and every individual image** in one call and prints that exact invocation.

- **A board is built by this command, never improvised.** The grid is for scanning; the full-size files are what get judged. Judging 15 thumbnails off a downscaled grid, because the full-size files were never opened, is a known failure.
- **Never write that images are open unless this command's `exited 0` line is in context.** A session once said 9 renders were open without ever calling `open`.

## Thumbnail size for native video uploads

**A native video post (LinkedIn and similar) takes its custom thumbnail's pixel size from the video, not just its aspect ratio.** A 1280x720 thumbnail on a 1920x1080 video has made a post fail wholesale with an error that named neither. `thumb-size --video <file>` prints the size and `--image` fits a picture to it; render natively at that size where you can. **YouTube stays 1280x720.**

When uploading a native video with a custom thumbnail: add the video, wait for its upload bar to reach 100%, only then add the thumbnail. If it stalls, try the same picture as PNG, then as a lighter JPEG. A native video's thumbnail usually cannot be changed once the post is live, so never plan "post first, thumbnail after". The last-resort fallback is a render with the thumbnail as the video's first second.

**When a platform refuses an upload with a generic error, post the smallest honest version first** (a 60-second clip of the same encode), then add back 1 variable at a time. **And after any publish that took more than 1 attempt, read the profile back and count the posts**: a platform can accept retries while still showing the error.

---

## Money and wallets

- **The ceiling.** Anything over `MEDIA_GEN_MAX_CALL_USD` (default 5.00) is refused before a request is sent, even with `--yes`, on every lane including Omni. Raise it deliberately and say why, or make the call smaller. Never split a job to slip under it.
- **Which wallet pays.** With a Google project set and its sign-in live, Omni and both image models bill the project; Seedance and Veo always bill the gateway. Every render prints which wallet paid and appends a row to `outputs/media-gen/spend.jsonl`; `spend` splits the month by wallet.
- **The wallet guard.** When a Google project is configured and its route is unreachable, `nano-banana-pro` refuses rather than quietly paying gateway cash, and prints `gcloud auth application-default login`; `--pay-cash` is the deliberate override. `nano-banana-lite` falls back to the gateway unguarded. With no Google project configured the guard does nothing.
- **Iterate on 1, then batch.** 4 variations of a wrong prompt cost 4 times what finding out costs. On credit that expires, the opposite holds for rerolls of a prompt you already trust.
- **Video on the gateway is the expensive lane.** Ask before rendering one, every time.
- **One image render at a time on one Google project.** Parallel calls come back 429. `image` takes a machine-wide lock after the confirm (`MEDIA_GEN_LOCK`, default `~/.cache/media-gen/media-gen.lock`), so parallel sessions and sub-agents queue instead of colliding; `MEDIA_GEN_NO_LOCK=1` bypasses it on purpose. The video lanes take no lock.
- **`doctor` saying the gateway key works does not prove there is money behind it**: it said so while the balance was negative and every Seedance job returned 403 `insufficient_user_quota`. That 403 means a top-up.

## When something breaks

- Run `doctor` first. Then, before promising renders on a new machine or a new account, prove the Google route with one real job: one Pro image (it refuses on a Vertex error, where lite would quietly render on gateway cash), or a lite image whose output says it was paid by the Google project. A green `doctor` has coexisted with Vertex refusing every render on a new account.
- A model id that stops working: `models` prints the configured table and asks the gateway what it carries (probing Omni there). It never asks Vertex, so an Omni or Pro rename shows up as a failed render. Pass the current id with `--model-id` and update the table in the script in the same session.
- The Google sign-in may end with a "quota project" warning; renders still work, and the newest spend-log row showing the Google wallet is the proof.
- The rest of the traps (Vertex roles, the `-preview` suffix, `gs://` objects cached by URI, the Gemini API key's separate wallet, the gateway's response shapes) are in `content/reference/media-gen.md`.

## What this skill does not do

Editing real footage (light, eye line, a regenerated word, a background shift) belongs to the editing skills. Omni as a second camera angle on real talking-head footage was tested and is not dependable (the reference has the numbers); a real-pixel punch-in is the safer cutaway. Lipsync, upscaling, retiming and background removal are not wired; the gateway carries more models (`models` lists them), and one gets wired when a job needs it.

## When the creator reacts to a render

Their reaction is taste, and it goes into `content/taste/thumbnails.md`, `content/taste/packaging.md` or `content/taste/story-animations.md` in the same session, with the render it was about named. "Too busy" is not a rule. "Faces read at thumbnail size, screenshots do not" is.
