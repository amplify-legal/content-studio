#!/usr/bin/env python3
"""Brand karaoke captions: phrase-level, sentence case, slow build, current word highlighted.

Captions are phrases of about 5 to 10 words in sentence case that build in word by word
in sync with speech, with the currently spoken word highlighted in your brand accent.
This is the default caption layer for talking lines; captions.py is the one-word
UPPERCASE alternative, kept for A/B checks only. The taste rule this implements lives in
content/taste/clip-bar.md; this script is the engine, never the taste.

Brand: the highlight colour is BRAND_ACCENT and the font file is BRAND_CAPTION_FONT,
both resolved by brand.py from content/brand.md, then env vars, then the flags below.
Nothing brand-specific is hard-coded here.

Same contract as captions.py: transparent PNG sequence at FPS, consumed by compose.sh
(`-framerate 12 -i "$CAPT/%05d.png"` ... overlay at y=78). Times must come from the
transcript of the ALREADY-CUT video. Patch transcriber typos in the JSON first (and, on a
Deepgram transcript, turn spelled-out numbers into digits).

Size: the default is 78, the caption floor (Montserrat 78px at 1080 wide = a capital H
35px tall; check_caption_size.py gates it). A phrase that does not fit in 2 lines is
shrunk to fit, and the script warns when that takes it under the floor, so you can
re-cut the phrase rather than ship small type.

Usage: python captions_brand.py <cut_transcript.json> <out_dir> [fps=12] [size=78]
                                [--accent #RRGGBB] [--font /path/to/font.ttf]
Env:   BRAND_ACCENT, BRAND_CAPTION_FONT (or CAPTION_FONT), BRAND_FILE.
"""
import json, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter


def _usage(msg=None, code=2):
    """Plain English instead of a traceback when the arguments are missing."""
    if msg:
        print(msg)
    print(__doc__.strip() if __doc__ else "")
    sys.exit(code)


def _need(n, names):
    """Require n positional arguments; -h/--help prints the usage and stops."""
    if any(a in ("-h", "--help") for a in sys.argv[1:]):
        _usage(code=0)
    if len(sys.argv) - 1 < n:
        got = len(sys.argv) - 1
        _usage(f"Missing arguments. This needs {n} ({names}); it got {got}.")


def _load_json(path, what, needs_words=True):
    """Read a JSON input, or say plainly what is wrong with it."""
    try:
        data = json.load(open(path, encoding="utf-8"))
    except json.JSONDecodeError as err:
        _usage(f"{path} is not valid JSON ({err}).")
    if needs_words and (not isinstance(data, dict) or "words" not in data):
        _usage(f'{path} has no "words" list. This needs a word-level transcript,\n'
               f'the shape {{"words": [{{"text": "hi", "start": 0.0, "end": 0.3}}, ...]}}.')
    return data


def _need_file(path, what):
    """A missing input is a sentence, not a stack trace."""
    if not os.path.isfile(path):
        _usage(f"Cannot find the {what}: {path}\n"
               f"Check the path. Nothing here creates it for you.")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import brand as _brand

_flags = {}
_argv = [sys.argv[0]]
_it = iter(sys.argv[1:])
for _a in _it:
    if _a in ("--accent", "--font"):
        _flags[_a] = next(_it, "")
    else:
        _argv.append(_a)
sys.argv = _argv

_need(2, "<cut_transcript.json> <out_dir>")
_need_file(sys.argv[1], "transcript JSON")

TRANSCRIPT, OUT = sys.argv[1], sys.argv[2]
FPS = int(sys.argv[3]) if len(sys.argv) > 3 else 12
SIZE = int(sys.argv[4]) if len(sys.argv) > 4 else 78
REQUESTED = SIZE
FLOOR = 78              # the caption floor at 1080 wide; raised by a person, never by a script
W, H = 1080, 1920
BASE_Y = 640            # phrase block bottom-anchors near the band edge (band edge = 864-78 overlay)
LINE_W = 960            # max pixel width per line
MAX_LINES = 2
BRAND = _brand.load_brand({"BRAND_ACCENT": _flags.get("--accent") or os.environ.get("CAPTION_ACCENT"),
                           "BRAND_CAPTION_FONT": _flags.get("--font")})
ACCENT = BRAND["BRAND_ACCENT"]
PHRASE_MAX_WORDS = 9
PHRASE_GAP = 0.6        # a silence >= this starts a new phrase
END_PUNCT = (".", "?", "!")

def _find_font():
    return _brand.find_caption_font(BRAND)

def font(sz, weight=700):
    f = ImageFont.truetype(_find_font(), sz)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f

F = font(SIZE)

def accent_rgb():
    return _brand.hex_to_rgba(ACCENT)

d = _load_json(TRANSCRIPT, "transcript")
ws = [w for w in d.get("words", [])
      if w.get("type") != "spacing" and w.get("start") is not None and w.get("end") is not None]

if not ws:
    os.makedirs(OUT, exist_ok=True)
    print(f"caption frames: 0 (empty transcript, nothing to render) -> {OUT}")
    sys.exit(0)

# a single word wider than the line clips at large font sizes; shrink until the widest word fits
_dr = ImageDraw.Draw(Image.new("RGBA", (W, H)))
while SIZE > 24 and max(_dr.textlength(w["text"].strip(), font=F) for w in ws) > LINE_W:
    SIZE -= 4
    F = font(SIZE)

# --- group words into phrases ---
phrases, cur = [], []
for i, w in enumerate(ws):
    cur.append(w)
    text = w["text"].strip()
    nxt = ws[i + 1] if i + 1 < len(ws) else None
    gap = (nxt["start"] - w["end"]) if nxt else 99
    if text.endswith(END_PUNCT) or gap >= PHRASE_GAP or len(cur) >= PHRASE_MAX_WORDS or nxt is None:
        phrases.append(cur)
        cur = []

os.makedirs(OUT, exist_ok=True)
total = ws[-1]["end"] + 0.3
n = int(total * FPS)
ACC = accent_rgb()

def layout(words_txt, f=None):
    """Wrap the phrase into lines. Returns {word index: (x, y)}, or None if it needs more than MAX_LINES."""
    f = f or F
    dr = ImageDraw.Draw(Image.new("RGBA", (W, H)))
    space_w = dr.textlength(" ", font=f)
    lines, line, line_w = [], [], 0
    for t in words_txt:
        wd = dr.textlength(t, font=f)
        if line and line_w + space_w + wd > LINE_W:
            lines.append(line)
            line, line_w = [], 0
        line_w = line_w + (space_w if line else 0) + wd
        line.append(t)
    if line:
        lines.append(line)
    if len(lines) > MAX_LINES:
        # never merge lines (that overflows the frame); the caller shrinks the font instead
        return None
    pos = {}
    idx = 0
    line_h = int(f.size * 1.25)
    for li, ln in enumerate(lines):
        widths = [dr.textlength(t, font=f) for t in ln]
        total_w = sum(widths) + space_w * (len(ln) - 1)
        x = (W - total_w) // 2
        for t, wd in zip(ln, widths):
            pos[idx] = (x, BASE_Y + li * line_h)
            x += wd + space_w
            idx += 1
    return pos

def fit(words_txt):
    """Shrink the font until the phrase fits in MAX_LINES and sits fully inside the frame."""
    size = SIZE
    while size >= 24:
        f = font(size)
        pos = layout(words_txt, f)
        if pos is not None:
            dr = ImageDraw.Draw(Image.new("RGBA", (W, H)))
            ok = all(0 <= x and x + dr.textlength(t, font=f) <= W
                     for (x, _), t in zip(pos.values(), words_txt))
            if ok:
                return pos, f
        size -= 4
    return layout(words_txt, font(24)) or {}, font(24)

_under_floor = set()


for fi in range(n):
    t = fi / FPS
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ph = next((p for p in phrases if p[0]["start"] <= t < p[-1]["end"] + 0.25), None)
    if ph:
        texts = [w["text"].strip() for w in ph]  # sentence case = transcript as-is
        pos, F_ph = fit(texts)
        if F_ph.size < FLOOR:
            _under_floor.add((round(ph[0]["start"], 2), F_ph.size))
        # words visible so far (slow build), current word highlighted
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ds = ImageDraw.Draw(sh)
        top = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dt = ImageDraw.Draw(top)
        for i, w in enumerate(ph):
            if w["start"] > t:
                break
            x, y = pos[i]
            current = w["start"] <= t < (ph[i + 1]["start"] if i + 1 < len(ph) else w["end"] + 0.25)
            ds.text((x, y + 3), texts[i], font=F_ph, fill=(0, 0, 0, 180))
            ds.text((x, y), texts[i], font=F_ph, fill=(0, 0, 0, 180))
            dt.text((x, y), texts[i], font=F_ph, fill=ACC if current else (255, 255, 255, 255))
        img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(7)))
        img = Image.alpha_composite(img, top)
    img.save(f"{OUT}/{fi:05d}.png")
print(f"caption frames: {n} ({len(phrases)} phrases, {len(ws)} words) -> {OUT}")
print(f"accent {ACCENT} (from {BRAND['_source']['BRAND_ACCENT']}), font {_find_font()}")
if REQUESTED < FLOOR:
    print(f"WARNING: size {REQUESTED} is under the {FLOOR}px caption floor. Raise it unless a person ruled otherwise.")
elif SIZE < REQUESTED:
    print(f"WARNING: the widest single word only fits at {SIZE}px, so every phrase starts there. "
          f"Patch or split that word in the caption JSON.")
for _t, _sz in sorted(_under_floor):
    print(f"WARNING: phrase at {_t:.2f}s was shrunk to {_sz}px to fit 2 lines, under the {FLOOR}px floor. "
          f"Split the phrase or shorten it.")
