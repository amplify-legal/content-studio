#!/usr/bin/env python3
"""Generate karaoke subtitles (one word at a time) as a transparent PNG sequence.
Fixed style: the caption font at weight 900 (Montserrat Black by default), white, UPPERCASE, one word, positioned at the edge with the video.
NO hard black outline (stroke) but a soft blurred SHADOW: invisible on black, readable
over bright B-roll (lesson: a white subtitle over a bright screen-recording disappeared).
LEGACY: kept for A/B checks only. captions_brand.py is the default for talking lines.
Usage: python captions.py <cut_transcript.json> <out_dir> [fps=12] [size=100]
The times are ALREADY in the output timeline (ALWAYS transcribe the already-cut video).
NB: the transcriber mangles proper nouns / tech terms. Typos seen before, to patch in the
    caption JSON (the "text" field, times do NOT change): "Cloud"->"Claude", etc.
    BEFORE generating the subtitles, patch those errors in the JSON (substring replace on the
    "text" field of each word) and pass the CORRECTED transcript here. The card triggers in
    gen.py stay anchored to the ORIGINAL transcript (the word times don't change)."""
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

_need(2, "<cut_transcript.json> <out_dir>")
_need_file(sys.argv[1], "transcript JSON")

TRANSCRIPT, OUT = sys.argv[1], sys.argv[2]
FPS = int(sys.argv[3]) if len(sys.argv) > 3 else 12
SIZE = int(sys.argv[4]) if len(sys.argv) > 4 else 100   # 100 default; raise/lower to taste
W, H, CY = 1080, 1920, 700   # CY + overlay y=78 in compose => word sits at the video edge
# Font resolution goes through brand.py: BRAND_CAPTION_FONT / CAPTION_FONT, then assets/fonts/.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import brand as _brand
def _find_font():
    return _brand.find_caption_font()
FONT = _find_font()

os.makedirs(OUT, exist_ok=True)
d = _load_json(TRANSCRIPT, "transcript")
ws = [w for w in d["words"] if w.get("type") != "spacing" and w.get("start") is not None]
ents = []
for i, w in enumerate(ws):
    a = w["start"]; nxt = ws[i+1]["start"] if i+1 < len(ws) else a+0.4
    b = min(nxt, a+1.0); b = b if b > a else a+0.12
    ents.append((a, b, w["text"].strip().upper()))

def font(sz):
    f = ImageFont.truetype(FONT, sz)
    try: f.set_variation_by_axes([900])   # Black
    except Exception: pass
    return f
F = font(SIZE)
total = ws[-1]["end"] + 0.3
n = int(total*FPS)
for i in range(n):
    t = i/FPS; word = next((txt for a, b, txt in ents if a <= t < b), None)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if word:
        dr = ImageDraw.Draw(img); bb = dr.textbbox((0, 0), word, font=F); tw = bb[2]-bb[0]
        x = (W-tw)//2
        # SOFT shadow (no hard stroke): blurred semi-transparent black text -> readable halo
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
        ds.text((x, CY+4), word, font=F, fill=(0, 0, 0, 180))
        ds.text((x, CY), word, font=F, fill=(0, 0, 0, 180))
        img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(9)))
        ImageDraw.Draw(img).text((x, CY), word, font=F, fill=(255, 255, 255, 255))   # clean white on top
    img.save(f"{OUT}/{i:05d}.png")
print(f"caption frames: {n} ({len(ents)} words) -> {OUT}")
