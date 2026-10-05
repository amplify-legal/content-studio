# shorts-editor, a Claude Code skill

Turn ONE picked talking-head clip (vertical, or landscape 4K) into a finished, branded
**9:16 short**: the speaker in the bottom half, animated motion-graphics cards in the top
half, karaoke captions that build word by word, and a music bed. Colours and fonts come
from your own `content/brand.md`, so every short matches your brand without touching code.

This is a **skill for [Claude Code](https://claude.com/claude-code)**. You don't run the
scripts by hand. Claude follows `SKILL.md` to do the edit, iterating with you.

**The real value is the error table.** `SKILL.md` carries an "ERRORS NOT TO REPEAT"
section where every row is a bug that already cost someone a re-render: clipped word
tails, A/V drift from concat-copy, a white caption baked over a white screen recording,
a face crop set once for a whole tape, card type sized for a laptop and unreadable on a
phone, a mouth hidden under the platform overlay that a safe-area check passed. That table
is worth more than the scripts.

**It is not an auto-clipper.** A human picks the clips. Hand it timestamps, or it stops and
asks. Which 20 seconds are worth cutting is the one judgment worth keeping human.

---

## What's inside

```
shorts-editor/
├── SKILL.md                      ← the playbook Claude follows (read this to understand it)
├── README.md                     ← you are here (setup, first prompts, troubleshooting)
├── scripts/
│   ├── transcribe.py             ← transcription, THE ROUTE (ElevenLabs Scribe, keyterms)
│   ├── transcribe_deepgram.py    ← declared fallback (Deepgram nova-3, same shape, keyterms,
│   │                               word ends snapped to energy)
│   ├── transcribe_local.py       ← last resort (faster-whisper, no key, no network, no keyterms)
│   ├── verify_speaker.py         ← GATE: prove who is speaking, from the picture
│   ├── make_edl.py               ← build an EDL from a transcript (single-take clips only)
│   ├── cutjoin.py                ← cut and join segments (sample-accurate, no OOM)
│   ├── silence_keep.py           ← trim residual silences without clipping word tails
│   ├── brand.py                  ← reads your colours and fonts from content/brand.md
│   ├── gen.py                    ← the card generator template (HTML/GSAP motion graphics)
│   ├── captions_brand.py         ← phrase-level karaoke captions in your accent (the default)
│   ├── captions.py               ← the legacy one-word caption renderer, kept for A/B
│   ├── compose.sh                ← final composite: face + cards + captions + music
│   ├── check_caption_size.py     ← GATE: the caption floor, and the 375px phone read
│   └── check_safe_area.py        ← GATE: ink outside the shorts safe area, and a face in
│                                   the covered bottom band
├── references/
│   ├── style.md                  ← the visual style and schema catalog
│   ├── animation-library.md      ← a big catalog of animated schemas to use and vary
│   ├── card-snippets.md          ← copy-paste code for ready-made cards
│   └── examples/                 ← 2 complete working card generators + a B-roll composite
└── assets/
    └── README.md                 ← what to put here. Nothing is bundled. Read this first.
```

## Setup (once, about 10 minutes)

The easiest way: open Claude Code in your project and say *"read
.claude/skills/shorts-editor/README.md and set this up for me, ask before installing
anything"*. It runs the steps below and checks what is already there.

### 1. System tools: ffmpeg, node, python, yt-dlp

macOS with Homebrew:
```bash
brew install ffmpeg node python yt-dlp
```
Debian or Ubuntu: `sudo apt install ffmpeg nodejs npm python3 python3-pip`, and `yt-dlp` via pip if it is not packaged.

- **ffmpeg / ffprobe**: the whole video pipeline. Required.
- **node**: provides `npx`, which renders the cards (`npx hyperframes render`). Required. npx downloads `hyperframes` itself on first run.
- **python** 3.10 or newer: runs every script. Required.
- **yt-dlp**: only to download a reference reel you want to copy the style from. Optional. For some YouTube URLs it also needs `deno` (`brew install deno`), otherwise you get a 403.

### 2. Python packages

```bash
python3 -m pip install --upgrade pillow requests numpy
python3 -m pip install opencv-python      # optional: the safe-area face test's better detector
python3 -m pip install faster-whisper     # optional: only for the last-resort local transcriber
```

### 3. The caption font and your brand

- Put a caption font at `assets/fonts/` (Montserrat from Google Fonts is the tested default). [assets/README.md](assets/README.md) has the exact filenames.
- Fill in `content/brand.md` (installed from the repo's `templates/brand.md`). The scripts read these keys from it: `BRAND_ACCENT`, `BRAND_ACCENT_DARK`, `BRAND_RED`, `BRAND_NEUTRAL`, `BRAND_FONT_DISPLAY`, `BRAND_FONT_BODY`, `BRAND_CAPTION_FONT`. A line like `BRAND_ACCENT: #RRGGBB` is enough; table rows work too.
- Check what was picked up: `python3 .claude/skills/shorts-editor/scripts/brand.py`.

### 4. Transcription: a ranked order, not a menu

The pipeline needs word-level timestamps. 3 engines, same output shape, same arguments. Each names itself in its output file's `_engine` header.

**A. ElevenLabs Scribe (the route, paid).** Best word ends and the best on names. Get a Speech-to-Text key at elevenlabs.io, then put `ELEVENLABS_API_KEY=...` in your project's `.env` (or export it). Claude calls `scripts/transcribe.py`.

**B. Deepgram nova-3 (the declared fallback, paid).** For when Scribe is out of credits, has no key, or is down. Put `DEEPGRAM_API_KEY=...` in `.env`. Claude uses `scripts/transcribe_deepgram.py`, same CLI and the same `--keyterms-file`. It matches Scribe on names and beats it on where a word STARTS. 3 things to know: its raw word ENDS run into the next word's start (the script snaps them to measured energy by default, and you should still cut on starts); it writes numbers as words ("twenty seven"), so captions need a pass to digits; its speaker labels are not good enough to burn a named caption.

**C. Local whisper (free, offline, LAST RESORT).** `pip install faster-whisper`, then Claude uses `scripts/transcribe_local.py`. The first run downloads the model (about 1.5 GB for `large-v3`). Know what you give up: it takes no keyterms, so it cannot be told the names on the tape; on one tape all 3 engines ran on, it found 11 of 17 proper-noun sites where the APIs found 17 and 16; its word boundaries are about 3 times looser. Spot-read every name before anything burns.

**Keyterms:** for every video, write the names on the tape (people, products, places) one per line in `content/videos/<slug>/build/keyterms.txt`. Names go into the transcriber, never into a find-and-replace afterwards.

**Cache:** every transcriber skips the upload when its own output already exists. After you rewrite a file under the same name, pass `--force`.

Check prices on each provider's pricing page; keyterms cost a little extra on both APIs.

### 5. One-shot check

```bash
echo "ffmpeg:   $(command -v ffmpeg)"
echo "node:     $(node -v 2>/dev/null)"
echo "python:   $(python3 --version 2>/dev/null)"
python3 -c "import PIL, requests, numpy; print('python deps: ok')"
python3 -c "import cv2" 2>/dev/null && echo "opencv:   installed (face test uses Haar)" || echo "opencv:   not installed (face test uses the skin-band fallback)"
echo "skill:    $([ -f .claude/skills/shorts-editor/SKILL.md ] && echo installed || echo MISSING)"
echo "scribe:   ${ELEVENLABS_API_KEY:+set}${ELEVENLABS_API_KEY:-(unset in this shell; .env also works)}   # A, the route"
echo "deepgram: ${DEEPGRAM_API_KEY:+set}${DEEPGRAM_API_KEY:-(unset in this shell; .env also works)}   # B, the fallback"
python3 -c "import faster_whisper" 2>/dev/null && echo "whisper:  installed   # C, last resort" || echo "whisper:  not installed   # C, last resort"
python3 .claude/skills/shorts-editor/scripts/brand.py --self-test
```

## Your first short

Open Claude Code in your project and paste (edit the path and the timestamps):

> Make a vertical short from `content/videos/my-video/raw/clip.mov`, the part from 1:12 to 1:31.
> Use the **shorts-editor** skill. It's a single talking head in English. The names on the
> tape are in `content/videos/my-video/build/keyterms.txt`.

Variations you can add:

- **Match a reference reel:** *"make it look like this reel: <link>. Copy the style and the accent colour, not the text."*
- **One-off colour:** *"use an orange accent for this one"* (Claude sets `BRAND_ACCENT` for that render only).
- **Landscape 4K source:** *"the source is landscape 4K, crop it to vertical centered on my face first."*
- **B-roll over your face:** *"while I talk about the website around 0:10, overlay this screen recording: <path>."*
- **Your own music:** *"use this track: <path to .m4a or .mp3>."*

What Claude will do, so you know what to expect:

1. Transcribe the raw clip (word-level timing, with your keyterms).
2. Pick the clean takes (raws are often multi-take with spoken notes; it drops those) and verify the speaker on any line that is a claim about them.
3. Cut and trim silences, then re-transcribe the cut for exact sync.
4. Author the animated cards (one per beat, anchored to the words you say).
5. Bake the captions, composite face, cards, captions and music.
6. Run the gates (caption size, safe area and face position), self-check frames against the reference style, hand the short to the `cut-review` skill, then show you the result and iterate on your feedback.

Expect a round or two of "tighten this pause, fix this word, change this card" before it is final. The skill writes what it learns from that feedback into its own errors table.

## Troubleshooting

- **`npx hyperframes` is slow the first time.** It is downloading the renderer. Cached afterwards. If npm 404s the latest version ("No matching version found"), see the ETARGET row in `SKILL.md`.
- **Caption font error.** Put a `.ttf` at `assets/fonts/` or set `CAPTION_FONT=/full/path/font.ttf`. See [assets/README.md](assets/README.md).
- **The accent is the placeholder blue.** `content/brand.md` was not found or its `BRAND_ACCENT` line has no `#RRGGBB` yet. Run `python3 .claude/skills/shorts-editor/scripts/brand.py` to see where each value came from.
- **`ELEVENLABS_API_KEY not found`.** Put it in the project `.env`, or switch to Deepgram (B), or, with no network at all, local whisper (C).
- **A re-transcription returned the old words.** The cache is keyed on the filename. Pass `--force`.
- **Video won't open after export.** `compose.sh` already adds `+faststart`; if you remux by hand, add `-movflags +faststart`.

## Credits and licensing

The `shorts-editor` lineage starts with an earlier open reel editor, rebuilt and extended
over dozens of real shorts. The pipeline shape, the scripts and the first half of the errors
table come from that earlier work.

**Montserrat** is under the [SIL Open Font License](https://openfontlicense.org), free to
use, bundle and redistribute. Get it from [Google Fonts](https://fonts.google.com/specimen/Montserrat).

**Brand logos** the card examples reference (Claude, GitHub, OpenAI, WhatsApp and any
others) are **third-party marks belonging to those companies**. None of them ship here.
Supply your own, or swap them out, before anything you make ships commercially.
