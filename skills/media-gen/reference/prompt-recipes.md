# Prompt recipes for story animations

> Copy-ready shapes for `SKILL.md`. Each one says how sure it is: **picked** (the creator chose a clip made this way from a board of 5 directions), **1 take** (rendered once, not picked), or **untested** (from published guides, not yet run through this script). The example subject throughout is a mascot turning red marks on a page into black bars; swap the subject, keep the structure.

## The prompt file header (every clip)

```
Tape line: "<the exact sentence said on tape, with the transcript path and timestamp>"
Sound off, a viewer sees: <one sentence: what is there, what changes, how it ends>
Lane: omni | seedance | veo-fast     Length: <s>     Mode: text+ref | start | start+ref
```

## The character card

**Write it from the reference image, not from memory, and paste it word for word into every prompt with the mascot.** When the card and the reference disagree, the words win: a card that said "two small black square eyes" for a drawing whose eyes were holes the background showed through produced black eyes in every clip, and 1 clip grew antennae the drawing never had.

The shape (fill it in by looking at your sheet):

```
The reference image is the character: a flat, <style> <colour> creature with <body shape>, <eyes exactly as drawn>, <arms exactly as drawn>, and <legs exactly as drawn>. No <features the drawing does not have, for example antennae, a mouth>. Keep it exactly as drawn, flat and <edge style>, never rounded.
```

A filled example for a flat pixel mascot (untested as written; the picked set used a looser card that drifted as described above):

```
The reference image is the character: a flat, pixel-art terracotta-orange creature with a wide rectangular body, two square eye holes the background shows through, one straight bar of arms that sticks out past the body on both sides, and four short square legs. No antennae, no mouth. Keep it exactly as drawn, flat and pixel-edged, never rounded.
```

## The flat 2D plate

**Picked: the plate behind the chosen set.** Paste it unchanged into every prompt of a set, with your own colour words in place of these.

```
Style: flat 2D vector motion graphics, clean geometric shapes, no outlines, no gradients, off-white background, dark charcoal, deep teal, light aqua-teal, orange, deep red and solid black only, smooth eased motion, polished, high-end animated film, generous negative space. Silent. No watermark, no label, no title card, no colour swatches, no palette chips, no design sheet, no text, no letters, no numbers, no logos, no people, no camera shake, no 3D, no photorealism.
```

Colours are words, never hex, on Omni (hex came back as a palette strip with garbled labels). "Polished, high-end animated film" is the quality line; nothing that reads like a product name, which comes back as lettering. "Silent." is the only silence Omni gets: the script does not send `--no-audio` to it.

## A. Omni, text plus the character reference

**Picked, as it rendered:**

```
<card> A flat 2D close view: the creature holds up one large white paper rectangle carrying eight soft grey lines, six short pieces of those lines coloured deep red. The creature's arm sweeps down the page and each red piece it passes becomes a solid black bar, six bars top to bottom, until no red is left; a light aqua-teal circle draws around the page once and the creature's eyes brighten. <plate>
```

The shape: card, scene, the one action with its count and its end state, one small closing beat, plate. It ran as `image_to_video` (a single `--ref` counts as 1 image). It drew 5 marks and ended on 7 fully black lines, so the count is never trusted.

**1 take: the same line with the published-guide additions.** Inserted after the card: `In a single unbroken scene, locked camera, no scene cuts. The clip ends on one white page showing six solid black bars and no red.`; the closing circle dropped (one action); `and the six bars stay on the page to the last frame` added. It held one scene and the end state to the last frame, with partial bars that read better as redaction; it also drew 7, not 6. About $0.64 for 6 s on Omni, rendered in 40 s.

```bash
python3 -u .claude/skills/media-gen/scripts/media_gen.py video --model omni --duration 6 --aspect 16:9 --yes \
  --ref <mascot-sheet.png> --out <folder> --slug <label>-<line> --prompt "<prompt>"
```

## B. Omni, a pinned start frame

**Half of a picked row, and the start pin held.** One still passed as `--start` runs as `image_to_video`, and all 3 clips made this way opened on their still (all 3 were Pro stills). The end did not hold: 1 of them ended with its bars gone. Use this to fix where a clip begins; stitching one clip onto another's last frame is the published method and untested here.

Make the still first (lite to explore, Pro once picked; 1 reference and no face needs `--allow-single-ref`):

```bash
python3 .claude/skills/media-gen/scripts/media_gen.py image --model nano-banana-lite --aspect 16:9 --allow-single-ref --yes \
  --ref <mascot-sheet.png> --out <folder> --slug <label>-still \
  --prompt "<card> A 16:9 flat 2D vector illustration ... <the opening state> ... no text, no letters, no logos, no people."
```

Then animate it, the prompt describing only the motion:

```
Animate this flat 2D illustration in the same flat vector style, no 3D. <the one action, until <end state>>. Smooth eased motion, locked camera. Silent. No watermark, no label, no title card, no text, no letters, no numbers, no logos, no people, no camera shake.
```

```bash
python3 -u .claude/skills/media-gen/scripts/media_gen.py video --model omni --duration 6 --aspect 16:9 --yes \
  --start <still.png> --out <folder> --slug <label> --prompt "<prompt>"
```

## C. Omni, two images (not a frame pin)

**1 take each, neither image held as a literal frame.** Two images run as `reference_to_video`. A first still (4 red marks) and an edited last still (4 black bars) passed as `--start` and `--ref`, under the tag line `[# Sources <FIRST_FRAME>@Image1 <LAST_FRAME>@Image2]`: the clip reframed the opening and ended on about 10 bars. A start still plus the mascot under `[# Sources <FIRST_FRAME>@Image1] [# References <IMAGE_REF_0>@Image2]` was not checked for whether its start held. Treat two images as strong references to the look, and keep anything that must land exactly out of this route.

## D. Seedance, first and last frame (untested here)

From the official guide's shape. Six slots in order, under about 60 to 100 words; hex colours are fine here; leave `--ref` off, because the provider docs say references and frames cannot share a job and the script will send both without refusing. Older notes preferred a longer numbered shot list with hex codes for Seedance; which wins on your clips is untested.

```
<subject>, <one event with its end state>, <scene>, <style>, locked camera, silent. @Image1 is the first frame: <what it shows>. @Image2 is the last frame: <the same, changed only in X>. Nothing else changes.
```

```bash
python3 -u .claude/skills/media-gen/scripts/media_gen.py video --model seedance --duration 5 --resolution 480p --no-audio --yes \
  --start <first.png> --end <last.png> --out <folder> --slug <label> --prompt "<prompt>"
```

Draft at 480p and re-render the keeper at 720p; keep jobs short, since an 8 s 720p job outran the script's 900 s poll and lost its task id. A reference, when one is used instead of frames, gets one job and an exclusion: "@Image1 defines the creature only. Do not use its background."

## E. Veo 3.1 Fast

Veo rewards the detailed prompt: subject, action, style, camera position and motion, composition, focus and lens, ambience (Google's Veo guide). It returns 8 s through the gateway whatever is asked, takes `--start` and `--negative` but not `--ref` or `--end`, so cut it on the timeline.

## Judging a clip

```bash
ffmpeg -loglevel error -i <clip.mp4> -vf "fps=1,scale=854:-1,tile=6x1" -frames:v 1 <folder>/strip-<label>.png
ffmpeg -loglevel error -ss 0.3 -i <clip.mp4> -frames:v 1 <folder>/first-<label>.png
ffmpeg -loglevel error -sseof -0.3 -i <clip.mp4> -frames:v 1 <folder>/last-<label>.png
```

Read the strip for the sequence, the first frame for lettering, swatches or labels (where the hex and product-name bugs appeared), and the last frame for the count and the end state (where a pinned-start clip lost its bars, and every counted clip asked for 6 ended on 7 or more). Hold the mascot against its original sheet, never against an earlier clip.
