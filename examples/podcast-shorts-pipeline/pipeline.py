#!/usr/bin/env python3
"""The podcast and tutorial shorts pipeline: one spec JSON in, one finished 1080x1920 short out.

A short is cut from a recorded conversation (the host's track and the guest's track, each with a word-level transcript)
or from a solo tutorial recording: a hook (the question or the claim, the two faces stacked), then the answer (the
speaker full frame), captions burned in word by word, a graphic layer (a title, a list, a card, an animation) drawn by a
headless Chrome page, the audio rebuilt from each speaker's own track, then a battery of frame and audio checks. A short
that fails a check is written as checks-failed with the reasons, never shipped quietly.

    python3 pipeline.py --build <spec.json> [--look <look>] [--force]     build one short (idempotent, cached)
    python3 pipeline.py --plan  <spec.json>                               print the cut plan, write nothing heavy
    python3 pipeline.py --status                                          what is done, running, failed, to go
    python3 pipeline.py --selftest                                        the caption calibration and the checks' plumbing
    python3 pipeline.py --requeue <id> [...]                              forget a finished short so the next build redoes it

Spec: README.md "The spec" (one JSON per short under specs/<slug>/; specs/example/ is a worked one). Stages (README.md
"The pipeline"): cut, captions, overlay, checks, write.
Cache: paths.WORKROOT/<id>/ (keep it outside any folder a sync job mirrors).
Output: paths.OUT/<slug>/<id>.mp4 (+ poster, sheet, checks).
Paths and brand values: paths.py (config.json beside it, or environment variables); every spec is read through
load_spec, which remaps the paths it holds (config "path_remap"), so the same specs run on a second machine.
Dates and "row N" / "fix N" in the comments point at the build log (README.md): the order things were learned, and why.

Rules carried in code: every ffmpeg -nostdin with a bounded timeout; every -loop 1 image input carries -t; no shell rm on a
variable path (only Python os.replace on literal names built here); scratch paths are absolute. The graphic layer is
looks.html rendered by Chrome at every frame whose state changes (deterministic in t, springs closed form), held frames
hardlinked. Faces are Haar-measured once per person per spec (inside people.*.crop when given). Captions: libass,
Montserrat Bold 104 / 118 (first 8 s), current word in the brand accent, block inside y 1190..1500 and x 180..900, grouped by
sentence into balanced 1 or 2 lines, never across a cut. Audio: each piece from the speaker's own track through the house
chain, -14 LUFS, -1.5 dBTP, a short fade on the last breath.
"""
import argparse
import datetime as dt
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
import traceback
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths as PATHS  # noqa: E402  (every path and brand value of THIS machine; spec paths remapped on read)

ROOT = PATHS.REPO
HERE = PATHS.BUILD
SPECS = PATHS.SPECS
OUT = PATHS.OUT
WORKROOT = PATHS.WORKROOT
AUDIO16 = PATHS.AUDIO16
RESULTS = PATHS.RESULTS
FONTDIR = PATHS.FONTDIR
MONT = FONTDIR / "Montserrat-Bold.ttf"
LOOKS_HTML = HERE / "looks.html"
SK = PATHS.SK
FF = "ffmpeg"
FPS = 30
VW, VH = 1080, 1920
SAFE_BOTTOM = 1500
CAP_MAXW = 710           # drawn px, the caption column 180..900 minus a hair
CAP_BOTTOM = 1492
ACCENT_HEX, ACCENT_DARK_HEX = PATHS.ACCENT.lstrip("#").upper(), PATHS.ACCENT_DARK.lstrip("#").upper()   # for ffmpeg colours
ACCENT_ASS, ACCENT_DARK_ASS, WHITE_ASS = PATHS.ACCENT_ASS, PATHS.ACCENT_DARK_ASS, "&H00FFFFFF"   # the brand accent (paths.py), libass order
STYLE_CAP = "Style: Cap,Montserrat,104,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,1,0,1,0,3,2,180,180,428,1"
STYLE_BIG = "Style: Big,Montserrat,118,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,1,0,1,0,3,2,180,180,428,1"
# the AI agent's words on a tutorial's live call: the same block in the accent, the current word white, a chip above
STYLE_AGENT = f"Style: Agent,Montserrat,104,{ACCENT_ASS},&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,1,0,1,0,3,2,180,180,428,1"
STYLE_CHIP = f"Style: Chip,Montserrat,34,{ACCENT_ASS},&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,6,0,1,0,2,2,180,180,0,1"
# 29 Oct (builder H, guest C's M2 r3: the drawn captions white with a soft shadow over the guest's white blouse; Round-3 I, "a caption
# on a light background sits in a box"; the Instagram sticker got its box in row 220): every drawn caption line sits in a
# dark translucent box (#0E0E0E at 0.70, as #ig-cap), drawn as its own layer under the words: the glyphs transparent, the
# opaque-box border (BorderStyle 3) 14 px each side and 0 above and below (\ybord0), so the 2 lines' boxes meet without a
# darker seam and the per-word colour runs of the text layer never split a box. The text styles above are unchanged (the
# caption size check reads them)
CAP_BOX_PAD = 14
STYLE_CAP_BOX = "Style: CapBox,Montserrat,104,&HFF000000,&HFF000000,&H4D0E0E0E,&HFF000000,-1,0,0,0,100,100,1,0,3,14,0,2,180,180,428,1"
STYLE_BIG_BOX = "Style: BigBox,Montserrat,118,&HFF000000,&HFF000000,&H4D0E0E0E,&HFF000000,-1,0,0,0,100,100,1,0,3,14,0,2,180,180,428,1"
STYLE_AGENT_BOX = "Style: AgentBox,Montserrat,104,&HFF000000,&HFF000000,&H4D0E0E0E,&HFF000000,-1,0,0,0,100,100,1,0,3,14,0,2,180,180,428,1"
FILLER = re.compile(r"^(uh|um|mm|hmm|mhm|er|ah|uh-huh|mm-hmm)[,.\-?!…]*$", re.I)
FIXES = {"ai": "AI", "chatgpt": "ChatGPT", "chatgpt's": "ChatGPT's", "claude": "Claude", "llm": "LLM", "llms": "LLMs",
         "notebooklm": "NotebookLM", "linkedin": "LinkedIn", "sops": "SOPs", "cio": "CIO", "roi": "ROI"}
# your own spellings (a guest's name the transcriber writes wrong, a product name): config "word_fixes", lower-case keys
FIXES.update({str(k).lower(): v for k, v in (PATHS.CONFIG.get("word_fixes") or {}).items()})

# geometry: hook (host above, guest below) and answer (speaker full frame). Faces: panel y/h on the 1920 frame, the face
# box centre at cy of the panel and the box ff of its height (eyes about 40 % of the visible panel, chin above 1500).
# h is the VISIBLE panel (the real crop); below it, to the frame's foot, the same crop continues mirrored and blurred under
# the look's fade from y=1500 (never a bar). Hook guest: box about 270 px, chin about 1335; answer: box about 325, chin 1385.
# Since 27 Oct (reviewers A, B1, B2: the mouth sat under the 2-line caption block on every short, the head was cut
# at the hook panel's top, 460 px of empty ground under the title): the face sits HIGH, the chin at or above y 1180 so the
# captions (1190 to 1500) fall under it; `low_at` is where the lowest chin seen (plus a quarter head) is placed. A short
# with a graphic keeps the graphic in the band (540 to 836) and the panel from 880; one without starts the panel at 640
# under the sub line's band (520 to 600). "duo" is the stacked pair kept through the answer (story-proof).
# low_at = cy + ff/2 + 0.25 ff (the quarter-head margin inside `low`) + 0.04, or the low clamp lifts the face out of the
# panel's top (the first proof at 02:43 put the hook guest's box top 64 px above the panel)
HOOK_LAYOUT_R1 = {"top_band_h": 516, "host": {"y": 516, "h": 440, "cy": 0.50, "ff": 0.55, "low_at": 0.95},
                  "guest": {"y": 956, "h": 544, "cy": 0.25, "ff": 0.36, "low_at": 0.56}}
ANSWER_NONE_R1 = {"top_band_h": 640, "guest": {"y": 640, "h": 860, "cy": 0.44, "ff": 0.38, "low_at": 0.77}}
ANSWER_GRAPHIC_R1 = {"top_band_h": 880, "guest": {"y": 880, "h": 620, "cy": 0.32, "ff": 0.36, "low_at": 0.63}}
# 27 Oct (builder A, round-1 causes 1 and 2, 14 of 14 renders: blur 26 to 32 % of the frame, faces of 140 to 175 px
# on the drawn looks, both hook panels pillared over their own blur): every panel is now SOLVED (`solve_geo`), never
# placed by cy/ff alone. The rules it holds, in order: the crop never narrower than the panel needs (no pillar: the office
# comes off the sides), the crown inside with 2 % of the panel above it, real footage down to y 1536 on the bottom panel
# (the blurred extension only 1536 to 1920, BLUR_TOP) and down to its own foot on a top panel, a run-over above the
# source's top filled with the look's GROUND colour (never blur) and only as far as `top_ext` allows, the mouth over 1500
# in the lowest lean-in seen, the panel's own chin or mouth bound; the face as close to `face_px` (about 1.5x round 1's)
# as those allow. The drawn looks' bands are re-cut so a face can be 1.5x and its mouth stay above the 2-line caption
# block (y 1240): the hook host 516 to 1076 (the host's head fills his 720 px source, so a 440 px panel could only pillar),
# the guest 1076 to the foot; the card state's band ends at 736 (the graphic is compacted into 540 to 720); between the
# card's beats (`answer_full`) the panel starts under the title at 520 (640 when the short has a sub line). The _R1
# dicts above are the round-1 values, kept for the record.
BLUR_TOP = 1640          # 28 Oct (polish, guest O's M1 D: "the blur seems a little too high"): the blurred extension starts at or under 1640 (was 1536), the bottom 15 % only
SOFT_REACH = (0.5, 1.5, 2.5)   # 29 Oct (builder G): the solve's relax steps whose footage reach is 104 px short of BLUR_TOP (1536)
SOLVE_V = 4              # 29 Oct builder G: relax 0.5, the pillar relax 3, top panels never soften. In every piece's cache key: bump it when solve_geo or panel_chain changes what a piece looks like
CAP_BLOCK_TOP = 1240     # the drawn looks' 2-line caption block (Cap 104 px, foot at 1492): a mouth above it is clear
CAP_INK_TOP = 1262       # where that block's ink starts (its line box from 1238, capitals 0.26 em under it)
HOOK_LAYOUT = {"top_band_h": 516,
               "host": {"y": 516, "h": 540, "cy": 0.50, "ff": 0.55, "low_at": 0.95, "solve": True, "face_px": 300, "top_ext": 0.12, "collar_max": 1048},
               "guest": {"y": 1056, "h": 864, "cy": 0.32, "ff": 0.26, "low_at": 0.56, "solve": True, "face_px": 220, "chin_max": 1460, "top_ext": 0.0}}
ANSWER_NONE = {"top_band_h": 640, "guest": {"y": 640, "h": 1280, "cy": 0.30, "ff": 0.35, "low_at": 0.77, "solve": True, "face_px": 450, "mouth_max": CAP_BLOCK_TOP, "lip_max": CAP_INK_TOP, "top_ext": 0.10}}
ANSWER_GRAPHIC = {"top_band_h": 736, "guest": {"y": 736, "h": 1184, "cy": 0.30, "ff": 0.23, "low_at": 0.63, "solve": True, "face_px": 270, "mouth_max": CAP_BLOCK_TOP, "lip_max": CAP_INK_TOP, "top_ext": 0.10}}
ANSWER_FULL = {"top_band_h": 520, "guest": {"y": 520, "h": 1400, "cy": 0.30, "ff": 0.32, "low_at": 0.77, "solve": True, "face_px": 450, "mouth_max": CAP_BLOCK_TOP, "lip_max": CAP_INK_TOP, "top_ext": 0.10}}


# 27 Oct (the creator's pick, option B of the Instagram-native research): the `ig_native` look is full bleed: no band, no fade; the hook stacks
# the host 0 to 880 under the title stickers and the guest 880 to 1920 over the caption line at about 1560 to 1630; the
# answer is the speaker 0 to 1920, the face centred at half height (chin near 1140) so list stickers sit between the chin
# and the caption line, and the callout and title above the crown
# (guest Q's F1 first IG render: the low clamp pushed the full-height crop 123 source px off the bottom, a dark faded
# band from 1650): `bounded` panels never run off the source, the scale carries the face (the spec proposal's Frame row)
# 27 Oct (night conductor, Round-2 defaults 1 and 2, the creator: faces about 50 % bigger, blur only the bottom 20 %):
# 4 of the 6 ig_native renders failed safe_face (tutorial-1: mouths at 1524 to 1796; guest G's close webcam face 800 px tall) because
# a bounded crop could not grow past the 720 px source, so the scale blew the face up and dropped the chin under 1500.
# Now `bounded` means bounded at the TOP only: the crop may run past the source's bottom by up to 25 % of its height
# (IG_EXT), the blurred extension fills that last fifth of the frame and nothing more, and the faces take ff 0.25 / 0.30 /
# 0.36 of the panel (was 0.19 / 0.23 / 0.30), the chin held at or above 0.72 of the answer crop (1382) so the mouth
# stays over 1500 and the caption sticker at 1556 falls under it.
IG_EXT = 1.25
IG_TOP_EXT = 0.22   # an ig_native crop may run up to 22 % of the source above its top (a mirrored blur fills it)
# (guest C's F3: a host framed close at the top of his source cannot sit under the title in an 880 px panel): the hook
# host panel may run 60 % above the source's top and 70 % past its bottom (`top_ext`, `ext`), so the face shrinks to ff
# and a mirrored blur carries the title stickers above the head
IG_LAYOUT_R1 = {"hook": {"top_band_h": 0, "host": {"y": 0, "h": 880, "cy": 0.72, "ff": 0.28, "low_at": 0.90, "bounded": True, "ext": 1.7, "top_ext": 0.6},
                         "guest": {"y": 880, "h": 1040, "cy": 0.40, "ff": 0.34, "low_at": 0.58, "bounded": True, "ext": 1.5, "top_ext": 0.4}},   # (guest S's F3: a 364 px face in a 720 source could not shrink, chin 1630, mouth 1529): the hook guest panel may run past the source too
                "answer": {"top_band_h": 0, "guest": {"y": 0, "h": 1920, "cy": 0.48, "ff": 0.25, "low_at": 0.72, "bounded": True}}}
# 27 Oct (builder A, causes 1 and 2): solved like the drawn looks. The hook host's run-over above his source (guest C's F3
# 0 to 336, guest O's F2 0 to 315: a mirrored blur of his own face) is the plain ground 101010 now and only as tall as the
# title stickers need: the crop zooms until his eyes sit just under the stickers (`eyes_min`, set per spec from the
# title's line count), which also makes his face bigger; the hook guest targets 360 px (guest O 245, guest X 270 in round 1)
# with the mouth at or above 1480 over the caption sticker; the answer keeps round 1's size (about a third of the frame,
# the checker's "about right") with no run-over at the top (guest C's F2 blurred band 0 to 128 is gone) and its footage
# down to 1536.
IG_LAYOUT = {"hook": {"top_band_h": 0,
                      "host": {"y": 0, "h": 880, "cy": 0.72, "ff": 0.28, "low_at": 0.90, "bounded": True, "solve": True, "face_px": 380, "top_ext": 1.0, "pin_top": True, "crown_min": 474, "collar_max": 868},
                      "guest": {"y": 880, "h": 1040, "cy": 0.40, "ff": 0.34, "low_at": 0.58, "bounded": True, "solve": True, "face_px": 360, "mouth_max": 1480, "chin_max": 1610, "top_ext": 0.0}},
             "answer": {"top_band_h": 0, "guest": {"y": 0, "h": 1920, "cy": 0.48, "ff": 0.25, "low_at": 0.72, "bounded": True, "solve": True, "face_px": 480, "chin_max": 1380, "eyes_min": 470, "top_ext": 0.0}}}


# 28 Oct (polish, guest Q's A: the credit read "<guest> - <our company>", which makes no sense; the creator: it should
# be the name of the guest's firm, and our firm or show name may appear on the short, but never right next to the guest's
# name): the credit beside a guest's name is the guest's own firm or organisation, read from `people.guest.firm` when the
# spec carries it, else this table (config "firms": slug -> firm, from your own contact notes); a guest with no firm on
# record gets the name alone. Your own brand beside YOUR name (a tutorial, the creator alone) stays.
OWN_BRAND = next((n for n in PATHS.OWN_NAMES if n), "")   # your own brand as written (config "own_names", first entry)
FIRMS = PATHS.FIRMS     # slug -> the guest's own firm (config "firms"); an empty table means every guest is credited by name


# your own brand and show names (config "own_names"): the pattern that strips one from the end of a guest's credit
_OWN_RE = (r"\s*[·\-|]\s*(?:" + "|".join(re.escape(n) for n in PATHS.OWN_NAMES if n) + r")\s*$") if any(PATHS.OWN_NAMES) else None


def credit_for(S):
    """the credit line: '<guest> · <firm>' (never '<guest> · <your own brand>'); a spec with no guest keeps its own credit"""
    people = S.get("people") or {}
    g = people.get("guest") or {}
    credit = S.get("credit") or ""
    if not g or not g.get("name"):
        return credit
    firm = g.get("firm") or FIRMS.get(S.get("slug") or "")
    name = g["name"]
    if firm:
        return f"{name} · {firm}"
    # no firm on record: the name alone, our name never beside it (a guest's credit is the guest's own firm, never our
    # brand beside their name); with no own_names configured there is nothing to strip
    if _OWN_RE is None:
        return credit.strip() or name
    return re.sub(_OWN_RE, "", credit, flags=re.I).strip() or name


def has_sub(S):
    """the drawn looks' sub line (520 to 630) shows from the answer on: overlay_payload's own conditions"""
    return bool((S.get("format") == "pov-bit" and S.get("pov_line")) or (S.get("held_top") and S.get("held_top") != S.get("title"))
                or (S.get("format") == "claim-band" and S.get("band_text") and S.get("band_text") != S.get("title")))


def ig_title_lines(S):
    """how many sticker lines the ig_native title takes (looks.html igSetup: Montserrat Bold 56 in 900 px, balanced, at
    most 2), measured with PIL; the emoji counted as one 56 px glyph"""
    try:
        f = ImageFont.truetype(str(MONT), 56)
        t = " ".join(w[:1].upper() + w[1:] for w in str(S.get("title") or "").split())
        w = f.getlength(t) + (70 if (S.get("ig") or {}).get("emoji") else 0) + 44
        return 1 if w <= 900 else 2
    except Exception:  # noqa: BLE001
        return 2


# 28 Oct (polish, guest E's E: half the screen was black; the creator: when the guest is just talking and there are
# no animations, keep his face cam in the centre of the screen with the blurred outline and the Instagram headline, and
# when there are animations, switch back; Round-3 ruling on animated shorts): with `ig_between: true` an animated short's
# footage is the Instagram look outside a card window (the hook stacked under the title stickers, the answer full bleed,
# the face centred, the blurred extension where the source runs out: the reading of "the blurred outline") and, inside a
# window, the face in the lower 1040 px under the animation, which takes the whole top (the band to 880, the title gone).
IGB_ANSWER = {"top_band_h": 880, "guest": {"y": 880, "h": 1040, "cy": 0.40, "ff": 0.34, "low_at": 0.58, "bounded": True, "solve": True, "face_px": 340,
                                            "mouth_max": 1440, "chin_max": 1520, "top_ext": 0.0}}
# 29 Oct (builder G, guest X's after-wave1-02-animB/Bd r3: the guest 195 px under the animation): the 1300 mouth and 1360 chin kept
# the face clear of the credit at 1400, but since row 193 no card window runs in the credit's last 6 s, so inside a window
# only the caption sticker (1556, 1494 for 2 rows) is under the face: mouth at or above 1440, chin 1520 (lip about 1462)


def is_igmode(S, look=None):
    """the overlay draws the Instagram stickers and the caption sticker (no ASS captions): the ig_native look, or an animated
    short with ig_between"""
    return (look or S.get("_look")) == "ig_native" or bool(S.get("ig_between"))


IG_LIST_TOP = 238       # looks.html igTime: once the title has left, the list stacks down from the title's own top
IG_LIST_ROW_H = 80      # one list sticker at 44 px (line-height 1.5 plus its padding), the page's floor; a 2-line sticker 144
IG_LIST_GAP = 12


def ig_list_height(S):
    """the stacked list's height on the Instagram look (looks.html igSetup and igTime: 44 px stickers, a sticker wider than
    744 px wraps to 2 lines, 12 px between, the newest 4 on screen), measured with PIL"""
    items = [str(x).replace("|", ": ") for x in ((S.get("graphic") or {}).get("items") or [])][-4:]
    if not items:
        return 0
    try:
        f = ImageFont.truetype(str(MONT), 44)
        hs = [IG_LIST_ROW_H if f.getlength(" ".join(w[:1].upper() + w[1:] for w in t.split())) + 36 <= 744 else 144 for t in items]
    except Exception:  # noqa: BLE001
        hs = [144] * len(items)
    return sum(hs) + IG_LIST_GAP * (len(hs) - 1)


def ig_list_layout(S, answer):
    """29 Oct (builder H, guest C's M1 r3: the 3 list rows at y 238 to 480 sat on her hair, crown 59, face 622 px; Round-3 C:
    lists go in the space above the head): `answer_list`, the Instagram answer framing for the pieces the list is on screen
    over (a spec's `ig_list_room`): the crown at or under the list's foot plus 16 px (the run-over above her tape is the
    mirrored blur, allowed from relax 0 so the chin and mouth bounds hold: chin at or above 1380, over the credit at 1400),
    the face as near 520 px as that leaves, no title to sit under (the title has left before the first row)"""
    import copy
    lay = copy.deepcopy(answer)
    g = lay["guest"]
    g.pop("eyes_min", None)
    g["crown_min"] = IG_LIST_TOP + ig_list_height(S) + 16
    g["top_ext"] = 1.0
    g["face_px"] = 520
    return lay


def layout_for(S):
    import copy
    if S.get("ig_between") and S.get("_look") != "ig_native":
        lay = copy.deepcopy(IG_LAYOUT)
        foot = 238 + 94.1 * ig_title_lines(S) + 1
        lay["hook"]["host"]["crown_min"] = round(foot + 24)
        lay["answer"]["guest"]["eyes_min"] = round(foot + 33)
        ans = copy.deepcopy(IGB_ANSWER)
        # 29 Oct (builder H, guest X's after-wave1-02-animB r3: the guest 282 px under the contract; with his lean-in seen (low 514)
        # and the crown under the band, 300 px needs the face panel to start higher): a spec may move the band's foot
        # (`igb_answer.top_band_h`, the face panel starting there) and the face bounds, for its own short only
        o = S.get("igb_answer") or {}
        if o.get("top_band_h"):
            ans["top_band_h"] = int(o["top_band_h"])
            ans["guest"]["y"], ans["guest"]["h"] = ans["top_band_h"], VH - ans["top_band_h"]
        for k in ("mouth_max", "chin_max", "face_px"):
            if k in o:
                ans["guest"][k] = o[k]
        return {"hook": lay["hook"], "duo": lay["hook"], "answer": ans, "answer_full": lay["answer"]}
    if S.get("_look") == "ig_native":
        lay = copy.deepcopy(IG_LAYOUT)
        # the stickers' foot: 238 + 94 a line (line-height 1.68 at 56 px); the answer's eyes 34 px under it
        # (conductor, guest O's F3 r2: the title's lower box sat on the host's hairline, his crown behind it, once row 83
        # made his hook face bigger): the hook host's CROWN lands 24 px or more under the stack's foot, the face
        # shrinking toward round 1's size only as much as that needs, plain ground above (row 82)
        foot = 238 + 94.1 * ig_title_lines(S) + 1
        lay["hook"]["host"]["crown_min"] = round(foot + 24)
        lay["answer"]["guest"]["eyes_min"] = round(foot + 33)
        out = {"hook": lay["hook"], "duo": lay["hook"], "answer": lay["answer"], "answer_full": lay["answer"]}
        if S.get("ig_list_room"):
            out["answer_list"] = ig_list_layout(S, lay["answer"])
        return out
    kind = (S.get("graphic") or {}).get("kind") or "none"
    graphic = kind != "none" or bool(S.get("screen"))
    # `answer_full` is the face-only geometry a card-only-while-it-moves short uses between the card's beats
    # under the title at 520 (640 when the short carries a sub line in 520 to 630)
    full = ANSWER_NONE if has_sub(S) else ANSWER_FULL
    return {"hook": HOOK_LAYOUT, "duo": HOOK_LAYOUT, "answer": ANSWER_GRAPHIC if graphic else ANSWER_NONE, "answer_full": full}


def panel_roles(it, lay, people):
    """which person sits in which panel of this piece: hook = the speaker above, the other below; duo = host above,
    guest below whoever speaks; answer = the speaker alone."""
    if it["layout"] == "duo":
        roles = [("host", lay["host"]), ("guest", lay["guest"])]
    elif it["layout"] == "hook":
        roles = [(it["speaker"], lay["host"]), ("guest" if it["speaker"] != "guest" else "host", lay["guest"])]
    else:
        roles = [(it["speaker"], lay["guest"])]
    return [(r, pn) for r, pn in roles if r in people]


# ---------------------------------------------------------------- plumbing
def log(work, msg):
    line = f"{dt.datetime.now():%H:%M:%S} {msg}"
    print(line, flush=True)
    try:
        with open(work / "build.log", "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


def run(cmd, timeout=600, label="", binary=False):
    cmd = [str(c) for c in cmd]
    if cmd[0] == FF and "-nostdin" not in cmd:
        cmd.insert(1, "-nostdin")
    # 29 Oct (row 191): the timeout counts only time the child is not stopped. A render guard (if you run one) freezes
    # a render with SIGSTOP when the disk runs low; with a wall-clock timeout guest C's F2 piece 'timed out after 725 s' when
    # the guard let it go 6 hours later, and the render died. A stopped child (state T) keeps its clock still.
    pr = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=not binary)
    active, out_b, err_b = 0.0, None, None
    while True:
        t0 = time.time()
        try:
            out_b, err_b = pr.communicate(timeout=20)
            break
        except subprocess.TimeoutExpired:
            st = subprocess.run(["ps", "-o", "state=", "-p", str(pr.pid)], capture_output=True, text=True).stdout.strip()
            if not st.startswith("T"):
                active += time.time() - t0
            if active > timeout:
                pr.kill()
                pr.communicate()
                raise subprocess.TimeoutExpired(cmd, timeout)
    r = subprocess.CompletedProcess(cmd, pr.returncode, out_b, err_b)
    if r.returncode != 0:
        err = r.stderr if not binary else r.stderr.decode("utf-8", "replace")
        raise RuntimeError(f"{label or cmd[0]} failed ({r.returncode}): {err[-2500:]}")
    return r


def key_of(obj):
    return hashlib.sha1(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()[:12]


def probe(path):
    r = run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate,pix_fmt,color_range,sample_rate",
             "-show_entries", "format=duration", "-of", "json", path], timeout=60, label="ffprobe")
    j = json.loads(r.stdout)
    v = next(s for s in j["streams"] if s["codec_type"] == "video")
    num, den = v["r_frame_rate"].split("/")
    return {"w": int(v["width"]), "h": int(v["height"]), "fps": int(num) / int(den), "range": v.get("color_range", "tv"),
            "pix": v.get("pix_fmt", ""), "dur": float(j["format"]["duration"])}


def duration(path):
    return probe(path)["dur"]


def fq(sec):
    return max(1, int(round(sec * FPS)))


# ---------------------------------------------------------------- words
_WORDS = {}


def load_words(path, speaker=None, words_offset=0.0):
    """Scribe-shaped word files: {words: [{text,start,end,type,speaker_id?|track?}]}; a transcript-words.json export too.
    words_offset: added to every time, for a transcript made from an extract of the track (guest Z's co-host-full.json
    starts at track second 693)."""
    k = (str(path), speaker, round(float(words_offset or 0.0), 3))
    if k in _WORDS:
        return _WORDS[k]
    d = json.loads(Path(path).read_text())
    ws = d["words"] if isinstance(d, dict) else d
    out = []
    for w in ws:
        if w.get("type", "word") != "word":
            continue
        if speaker and w.get("speaker_id", w.get("track")) != speaker:
            continue
        t = (w.get("text") or "").strip()
        if not t or t in ("...", "…"):
            continue
        if float(w["end"]) - float(w["start"]) > 4.0:
            continue   # (podcast-guest-j M1: the guest's file carries one "Got" from 3226.06 to 3277.72 that "covered" the host's pieces): a word over 4 s is a Scribe artefact
        out.append({"t": t, "s": float(w["start"]) + float(words_offset or 0.0), "e": float(w["end"]) + float(words_offset or 0.0)})
    out.sort(key=lambda w: w["s"])
    _WORDS[k] = out
    return out


# ---------------------------------------------------------------- audio analysis (quiet points, onsets)
_A16 = {}


def wav16(file):
    """a 16 kHz mono wav of the whole source, shared across shorts (paths.AUDIO16)."""
    AUDIO16.mkdir(parents=True, exist_ok=True)
    out = AUDIO16 / f"{key_of(str(file))}.wav"
    if not out.exists():
        run([FF, "-y", "-v", "error", "-i", file, "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(out) + ".part.wav"],
            timeout=1800, label="wav16")
        os.replace(str(out) + ".part.wav", out)
    if str(out) not in _A16:
        from scipy.io import wavfile
        sr, d = wavfile.read(out, mmap=True)
        _A16[str(out)] = d
    return _A16[str(out)]


class Track:
    def __init__(self, file, offset=0.0):
        self.file, self.off = str(file), float(offset or 0.0)
        self.d = wav16(file)
        self._floor = None

    def db(self, t, win=0.01):
        i = int((t + self.off) * 16000)
        n = int(win * 16000)
        x = np.asarray(self.d[max(0, i - n // 2): i + n // 2], dtype=np.float32)
        v = float(np.sqrt(np.mean(x * x))) if len(x) else 0.0
        return 20 * math.log10(v + 1e-6)

    def floor(self):
        if self._floor is None:
            n = len(self.d) / 16000
            ts = np.arange(5.0, max(6.0, n - 5), 0.37)
            vals = sorted(self.db(t - self.off) for t in ts)
            self._floor = vals[len(vals) // 10]
        return self._floor

    def snap_in(self, t, win=0.10):
        ts = np.arange(t - win, t + 0.0001, 0.005)
        vals = [self.db(x) for x in ts]
        return float(ts[int(np.argmin(vals))])

    def decay_end(self, t, cap=0.5):
        fl = self.floor() + 6
        for x in np.arange(t, t + cap + 0.0001, 0.005):
            if self.db(x) <= fl:
                return float(x)
        return float(t + cap)


# ---------------------------------------------------------------- faces
def detect_face(file, times, region=None, work=None, tag=""):
    """the median Haar face box (x, y, w, h, source px) over sampled frames, searched inside region when given. Frontal
    default at a 1.05 step and 3 neighbours (guest X's two-shot tape only yields at that setting), then alt2; a box is
    kept only when it is plausible for a head in that region (width 12 to 60 % of the region, centre in its top 70 %)."""
    import cv2
    casc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    alt = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_alt2.xml")
    boxes = []
    fr_dir = (work / "faces") if work else None
    if fr_dir:
        fr_dir.mkdir(parents=True, exist_ok=True)
    for i, t in enumerate(times):
        png = (fr_dir / f"{tag}-{t:.2f}.png") if fr_dir else Path(f"/tmp/shorts-pipeline-face-{tag}-{t:.2f}.png")
        if not png.exists():
            run([FF, "-y", "-v", "error", "-ss", f"{t:.3f}", "-i", file, "-frames:v", "1", "-vf", "format=gray", str(png)], timeout=120, label="face frame")
        g = cv2.imread(str(png), cv2.IMREAD_GRAYSCALE)
        if g is None:
            continue
        H, W = g.shape
        ox = oy = 0
        rw, rh = W, H
        if region:
            x, y, w, h = [int(v) for v in region]
            x, y = max(0, x), max(0, y)
            g = g[y:min(H, y + h), x:min(W, x + w)]
            ox, oy = x, y
            rh, rw = g.shape
        ms = max(36, int(rw * 0.12))
        found = []
        for c, sf, nb in ((casc, 1.08, 5), (alt, 1.08, 5), (casc, 1.05, 3), (alt, 1.05, 3)):
            fs = c.detectMultiScale(g, sf, nb, minSize=(ms, ms))
            for (x, y, w, h) in fs:
                if 0.12 * rw <= w <= 0.6 * rw and (y + h / 2) <= 0.7 * rh:
                    found.append((x + ox, y + oy, w, h))
            if found:
                break
        if found:
            boxes.append(max(found, key=lambda r: r[2] * r[3]))
    if len(boxes) < 2:
        return None
    arr = np.array(boxes, dtype=float)
    med = np.median(arr, axis=0)
    # outliers (a poster, a plant, the other person's hair) are boxes whose centre sits over half a head from the median
    # centre; the LOW mark (the lowest chin, a lean-in) is the max bottom of the kept boxes, plus a lean the samples missed:
    # 2 Oct 27 renders landed 100 px into the band on a lean-in no sampled frame caught, so a quarter head is added
    cx, cy = arr[:, 0] + arr[:, 2] / 2, arr[:, 1] + arr[:, 3] / 2
    keep = (np.abs(cx - (med[0] + med[2] / 2)) < 0.6 * med[2]) & (np.abs(cy - (med[1] + med[3] / 2)) < 0.9 * med[3])
    if keep.sum() >= 2:
        med = np.median(arr[keep], axis=0)
        detect_face.low = float(np.max(arr[keep][:, 1] + arr[keep][:, 3])) + 0.25 * float(med[3])
        detect_face.high = float(np.min(arr[keep][:, 1]))   # (pass 3: heads cut at the seam on guest X's host, guest Q, guest E): the HIGHEST brow seen
    else:
        detect_face.low = float(np.max(arr[:, 1] + arr[:, 3])) + 0.25 * float(med[3])
        detect_face.high = float(np.min(arr[:, 1]))
    detect_face.samples = int(keep.sum())
    return [float(v) for v in med]


def face_box(person, p, pieces, work, tag):
    """measured once per spec per person; a people.*.face override wins; a crop region bounds the search."""
    # 29 Oct (builder G, guest X's F2 and after-wave1-02-animB/Bd r3: black pillars beside a face held in a 405 px crop hint):
    # `face_region` is where Haar looks (the old tight hint, where it misfires least on a two-shot); `crop` is then only
    # the region the crop may use, and may be wider so the panel fills the width with no ground pillars
    if p.get("face_region"):
        p = dict(p, crop=p["face_region"])
    cache = work / f"face-{tag}-v6-{key_of([p.get('crop'), p.get('face'), p.get('offset')])}.json"   # the box depends on the crop hint (03:14: a stale box from a crop-less run put the face at y -1000)
    if cache.exists():
        return json.loads(cache.read_text())
    if p.get("face"):
        box = [float(v) for v in p["face"]]
    else:
        # v5 (27 Oct): about 1 frame a second across every piece, at most 28, so a lean-in is in the sample (v4 took
        # 10 frames at 3 fixed points and the finished video put the chin 2 to 106 px into the band on 12 shorts)
        ts = set()
        for a, b in pieces:
            t = a + 0.3
            while t < b:
                ts.add(round(t, 2))
                t += 1.0
        ts = sorted(ts)
        if len(ts) > 16:
            ts = ts[:: -(-len(ts) // 16)][:16]
        ts = [t + float(p.get("offset") or 0) for t in ts]
        detect_face.low = None
        detect_face.high = None
        box = detect_face(p["file"], ts, p.get("crop"), work, tag)
        low = detect_face.low
        high = detect_face.high
        if box is None and pieces:
            # short pieces give 1 to 3 samples (a 2 s hook): widen to 12 frames across the pieces' span plus 20 s each
            # side before refusing (guest S's F3 03:42: the host's hook had 3 frames, none with a frontal face)
            lo, hi = min(a for a, b in pieces) - 20.0, max(b for a, b in pieces) + 20.0
            ts2 = [round(max(0.3, lo) + i * (hi - max(0.3, lo)) / 11, 2) + float(p.get("offset") or 0) for i in range(12)]
            detect_face.low = None
            detect_face.high = None
            box = detect_face(p["file"], ts2, p.get("crop"), work, tag)
            low = detect_face.low
            high = detect_face.high
        if box is None:
            info = probe(p["file"])
            if not p.get("crop"):
                raise NoFaceBox(f"{tag}: no Haar face in {len(ts)} sampled frames of {Path(p['file']).name} and no people.{tag}.crop or .face box in the spec")
            if p.get("crop"):
                # the posted 405x720 crops put the eyes near 40 % of the crop: a head about 22 % of the crop's height
                x, y, w, h = p["crop"]
                fh = 0.22 * h
                box = [x + w / 2 - fh / 2, y + 0.40 * h - fh / 2, fh, fh]
            else:
                box = [info["w"] * 0.36, info["h"] * 0.18, info["w"] * 0.28, info["w"] * 0.28 * 1.1]
            box = {"box": box, "method": "fallback (no Haar face in the sampled frames)"}
        else:
            box = {"box": box, "method": "opencv-haar median", "low": low, "high": high}
    if isinstance(box, list):
        box = {"box": box, "method": "spec face override" if p.get("face") else "opencv-haar median"}
    cache.write_text(json.dumps(box))
    return box


def crop_geo(info, face, panel, region=None, low=None, high=None, hard=False):
    """the panel's crop: solved (`solve_geo`) for every panel that carries `solve`, the round-1 placement otherwise; a
    solve that finds no crop meeting even its relaxed rules falls back to the round-1 placement and says so (`legacy`),
    which `blur_bottom_ok` then reads as a fail when its footage stops above 1536"""
    if panel.get("solve"):
        g = solve_geo(info, face, panel, region, low, high, hard)
        if g is not None:
            return g
        g = crop_geo_legacy(info, face, panel, region, low, high, hard)
        g["legacy"] = True
        return g
    return crop_geo_legacy(info, face, panel, region, low, high, hard)


def solve_geo(info, face, panel, region=None, low=None, high=None, hard=False):
    """27 Oct 22:10 (builder A, causes 1 and 2). The crop as a scale k (frame px per source px) and a top row y (source px,
    above the source's top = a run-over the GROUND fills). For each k the rules give an interval for y:
      the crown (the highest brow seen less 0.55 of the box) inside, 2 % of the panel above it   -> y <= ...
      real footage down to BLUR_TOP on a bottom panel, to its own foot on a top panel             -> y <= ...
      the eyes under the title stickers (`eyes_min`)                                               -> y <= ...
      the run-over at most `top_ext` of the source's height (none on a crop_hard region)          -> y >= ...
      the chin at or above `chin_max`, the mouth at or above `mouth_max`                          -> y >= ...
      the mouth of the lowest lean-in seen over 1500 (the safe frame)                              -> y >= ...
      a top panel holds the lowest lean-in seen whole                                              -> y >= ...
    k runs from the narrowest crop the panel allows (the region's full width: never a pillar) up; the k closest to
    `face_px` / box height with a non-empty interval wins and y takes the panel's cy inside it (`pin_top`: the highest y,
    the least run-over). With none, the chin and mouth bounds go first, then the run-over may reach 0.6, then the crown
    margin; still none returns None (the caller falls back and the check fails it)."""
    iw, ih = info["w"], info["h"]
    rx, ry, rw, rh = (0, 0, iw, ih) if not region else [int(v) for v in region]
    rx, ry = max(0, rx), max(0, ry)
    rw, rh = min(rw, iw - rx), min(rh, ih - ry)
    fx, fy, fw, fh = [float(v) for v in face]
    py, ph = float(panel["y"]), float(panel["h"])
    foot = py + ph >= VH - 1
    need = (BLUR_TOP - py) if foot else ph
    crown = min(fy, high if high is not None else fy) - 0.55 * fh
    chin = fy + fh
    lowc = max(chin, (low - 0.25 * fh) if low else chin)          # the lowest chin seen
    eyes = fy + 0.38 * fh
    fcx, fcy = fx + fw / 2, fy + fh / 2
    k_w = VW / rw
    k_t = max(k_w, float(panel.get("face_px") or panel.get("ff", 0.3) * ph) / fh)

    def interval(k, relax, te_min=0.0):
        hi = crown - (0.02 if relax < 3 else 0.0) * ph / k
        # 28 Oct (polish, guest Q's F1 proof: the IG answer took a 75 px run-over above the source to reach 1640 on a 720p
        # tape): the footage reaches BLUR_TOP where it can; before a run-over is allowed (relax 2) the reach softens to
        # 1536 (the old line) at relax 1.5, recorded on the geometry as `need_used`
        # 29 Oct (builder G, guest S's F3 blur_bottom_ok 1536 vs 1640): once a run-over is allowed anyway (relax 2) the
        # footage is asked to reach BLUR_TOP again (the run-over grows, the blur stays in the bottom 15 %); the softened
        # 1536 comes back only at relax 2.5, after the full reach with a run-over found nothing
        # 29 Oct (builder G, guest C's M2: her chin sits 90 source px over the bottom of a 720p tape, so with the footage to
        # 1640 her mouth fell to 1325 under the caption block at relax 1): the softened reach is tried at relax 0.5 too,
        # WITH the mouth, lip and chin bounds, before they are dropped at relax 1 (a caption is never on a face; blur from
        # 1536 is the lesser fault and blur_bottom_ok reads it by `need_used`); a top panel never softens (its foot is
        # the seam)
        need_k = max(0.0, need - 104.0) if (foot and relax in SOFT_REACH) else need
        hi = min(hi, ry + rh - need_k / k)
        if panel.get("eyes_min") is not None:
            hi = min(hi, eyes - (float(panel["eyes_min"]) - py) / k)
        if panel.get("crown_min") is not None:   # the crown under the title stack (ig_native hook host)
            hi = min(hi, crown - (float(panel["crown_min"]) - py) / k)
        te = 0.0 if hard else float(panel.get("top_ext", 0.0))
        if relax >= 2 and not hard:
            te = max(te, 0.6)
        if not hard:
            te = max(te, te_min)
        lo = ry - te * rh
        if relax < 1:
            if panel.get("lip_max") is not None:   # the lower lip (0.85 of the box) over the caption block's ink
                lo = max(lo, fy + 0.85 * fh - (float(panel["lip_max"]) - py) / k)
            if panel.get("chin_max") is not None:
                lo = max(lo, chin - (float(panel["chin_max"]) - py) / k)
            if panel.get("mouth_max") is not None:
                lo = max(lo, fy + 0.78 * fh - (float(panel["mouth_max"]) - py) / k)
        lo = max(lo, lowc - 0.22 * fh - (SAFE_BOTTOM - 4 - py) / k)
        if panel.get("collar_max") is not None and relax < 3:
            # 28 Oct (polish, guest X's F2 B: "you cut half my face off. In the question-first clip, you can't see my chin,
            # my neck, nor the collar of my shirt"; Round-3 ruling: the head whole with chin, neck and collar inside): the
            # chin of the lowest lean-in plus half a box (the neck and the collar) sits at or above `collar_max`, the face
            # shrinking as far as that needs; dropped only at relax 3, after the run-over and the crown margin
            # 29 Oct (builder G, guest S's F3 and guest Q's after-M31 r3: the host's webcam ends at his chin, so no crop can show a
            # collar the tape does not hold, and asking for it only drove the solve to relax 3): the collar is asked down to the
            # source's own bottom at most
            lo = max(lo, min(lowc + 0.5 * fh - (float(panel["collar_max"]) - py) / k, ry + rh - (ph + 2) / k))   # the tape ends first: no more than the reach itself
        if not foot:
            # a top panel holds the lowest chin seen plus 8 % of the box (the lean-in), not `low`'s quarter head, which
            # would leave the host's full-width head no room in a 540 px host panel (guest C's M2: 665 rows against 640)
            lo = max(lo, lowc + 0.08 * fh - (ph - 4) / k)
        return lo, hi

    ks = []
    k = k_w
    while k <= max(k_t, k_w) * 4 and len(ks) < 2000:
        ks.append(k)
        k *= 1.004
    gp = False
    for relax in (0, 0.5, 1, 1.5, 2, 2.5, 3):
        feas = [(abs(math.log(k / k_t)), k) for k in ks if interval(k, relax)[0] <= interval(k, relax)[1]]
        if feas and relax >= 2:
            # a run-over is needed (the head at the source's very top): the k with the least ground band above, then
            # the closest to face_px (guest S's IG answer took a 572 px band for a face at its target size)
            feas = [(round(max(0.0, ry - interval(k, relax)[1]) * k / 8), d, k) for d, k in feas]
            feas = [(a, k) for a, d, k in sorted(feas)[:1]]
        if feas:
            break
    else:
        # (builder A): a face too close for the region's full width (guest S inside the crop hint that keeps his
        # burned name tag out; guest I's 720x1280 phone) is shown narrower than the panel, the sides in the GROUND colour,
        # never over a blurred copy of itself: the biggest k under the full width that meets the panel's own bounds
        feas = []
        # 29 Oct (builder G, guest Q's after-M31 ig hook host: a 2-line title puts his crown at 451 and the 1000 seam leaves
        # 545 px to the lowest chin, under the full width's scale, so no bound set held and the round-1 crop came back,
        # footage 978 of 1000 and the crown at 77 under the title): the narrower crop is tried with the panel's own bounds
        # first, then with relax 3's (the chin of the lowest lean-in still inside a top panel, the crown under the title),
        # before giving up to the legacy crop
        for gp_rx in (0, 3):
            kk = k_w / 1.004
            while kk >= k_w / 4 and not feas:
                for te_min in (0.0, 0.3):      # a run-over over the head only when the head needs one (guest I's phone)
                    if interval(kk, gp_rx, te_min)[0] <= interval(kk, gp_rx, te_min)[1]:
                        feas = [(0, kk)]
                        gp_te = te_min
                        break
                kk /= 1.004
            if feas:
                break
        if not feas:
            return None
        relax, gp = 4, True
    k = min(feas)[1]
    lo, hi = interval(k, gp_rx, gp_te) if gp else interval(k, relax)
    ch, cw = ph / k, (rw if gp else VW / k)
    if gp and panel.get("bounded"):
        # 29 Oct (builder G, guest S's F3 r3: the guest at the left edge of his box, his face cut there): on the Instagram
        # panels a narrower-than-frame crop is taken symmetric about the face (the blurred fill takes the sides), never the
        # whole region with the face off to one side
        cw = max(2.0, min(rw, 2 * min(fcx - rx, rx + rw - fcx)))
    y = hi if (panel.get("pin_top") or (relax in (2, 2.5, 3) and hi < ry)) else min(max(fcy - panel.get("cy", 0.4) * ch, lo), hi)
    x = min(max(fcx - cw / 2, rx), rx + rw - cw)
    ev = lambda v: int(round(v / 2) * 2)  # noqa: E731
    top_cut = max(0.0, ry - y)
    y_vis = y + top_cut
    ch_vis = max(2.0, min(y + ch, ry + rh) - y_vis)
    top_h = ev(top_cut * k)
    vis_h = min(int(ph), max(2, ev(ch_vis * k) + top_h))
    # integer crop inside the source (ffmpeg refuses a crop that runs past the frame by a rounding pixel)
    cw_i = min(ev(cw), rw // 2 * 2)
    x_i = max(rx, min(ev(x), rx + rw - cw_i))
    yv_i = max(ry, ev(y_vis))
    chv_i = max(2, min(ev(ch_vis), (ry + rh - yv_i) // 2 * 2))
    return {"cw": cw_i, "ch": ev(ch), "ch_vis": chv_i, "x": x_i, "y": ev(y), "y_vis": yv_i, "top_h": top_h,
            "vis_h": vis_h, "k": k, "pillar": gp, "ground_pillar": gp, "out_w": min(VW, ev(cw_i * k)) if gp else VW,
            "solved": True, "relax": relax, "k_target": round(k_t, 4), "need_used": (max(0.0, need - 104.0) if (foot and not gp and relax in SOFT_REACH) else need) + (py if foot else 0.0),
            "blur_mirror_top": bool(panel.get("bounded")) and top_h >= 4}


def crop_geo_legacy(info, face, panel, region=None, low=None, high=None, hard=False):
    """the source crop with the panel's aspect: the face box centre at cy of the panel height, the box ff of it, never
    past people.*.crop when given (the other person on a two-shot stays out). Since 27 Oct 03:30 the crop may run off
    the BOTTOM of the source: the visible panel is then shorter (vis_h) and the faded extension fills from there, so a
    webcam that frames the chin at the frame's bottom (guest D, guest O's 640x360 track) still gets the face high and the
    head whole. The head is never cut at the panel's top: the box top keeps 4 % of the crop above it."""
    iw, ih = info["w"], info["h"]
    rx, ry, rw, rh = (0, 0, iw, ih) if not region else [int(v) for v in region]
    fx, fy, fw, fh = face
    # (guest C's F3 ig_native hook: the host framed at the top of his source, so the title stickers sat over his mouth):
    # an ig_native (`bounded`) crop may also run up to 22 % ABOVE the source's top; `ry_t` is the clamp the y
    # placements use, and panel_chain fills the run-over with a mirrored blur above the crop (IG_TOP_EXT)
    ry_t = ry - int(panel.get("top_ext", IG_TOP_EXT) * rh) if panel.get("bounded") else ry
    fcx, fcy = fx + fw / 2, fy + fh / 2
    r = VW / panel["h"]
    ch = fh / panel["ff"]
    cap = rh * panel.get("ext", IG_EXT) if panel.get("bounded") else rh   # an ig_native crop may run a fifth past the source's bottom (the hook host panel more: its `ext`)
    ch = min(ch, cap, (fcy - ry_t) / panel["cy"] if panel["cy"] > 0 else ch)   # the top run-over counts as room above the face
    ch = max(ch, 200)
    pillar = False
    if ch * r > rw:
        # the region is narrower than the panel's aspect needs (a webcam bubble, a close face inside a crop hint): a
        # full-width crop would blow the face past 70 % of the panel (tutorial-2 M2: 85 %, chin at 1433), so
        # the crop keeps its face size and is PILLARED on the panel over a blurred copy of itself (27 Oct)
        if fh / (rw / r) > 0.70 and (not panel.get("bounded") or rw < iw - 2):   # a full-bleed panel pillars only inside a crop hint narrower than the source (guest S's F3: the name-tag region, 20:20)
            pillar = True
            cw = rw
        else:
            cw, ch = rw, rw / r
    else:
        cw = ch * r
    x = min(max(fcx - cw / 2, rx), rx + rw - cw)
    y = max(fcy - ch * panel["cy"], ry_t)
    if low:
        y = max(y, low - panel.get("low_at", 0.70) * ch)   # a lean-in seen in the samples stays above low_at
    # 27 Oct (pass 2, sets AB and CE: crowns cut on 6 of 8): the Haar box is brow to chin, the crown sits about
    # 0.45 of the box above its top, so the crop keeps the crown plus 2 % of its height; when that pushes the chin past
    # low_at, the crop GROWS (the face gets smaller), never cuts, within the region
    # (pass 3: guest X's host at 0 and 32 s, guest Q at 8 and 12 s, guest E at 3 and 12 s cut at the seam): the crown is taken
    # from the HIGHEST brow the samples saw (a head that lifts), not the median box, and the crop may rise above the
    # region's top (the crop hint bounds the other person sideways, never the head) so the head shrinks, never cuts
    crown = min(fy, high if high is not None else fy) - 0.55 * fh   # 0.45 left the host's hair on the hook panel's edge (guest C's F2); the Haar box starts under the hairline
    if not hard:   # a `crop_hard` region (a webcam bubble on a board) is a real edge; above it is somebody else's UI
        ry = min(ry, max(0, crown - 0.02 * ch))
    if low:
        need = (low - (crown - 0.02 * ch)) / panel.get("low_at", 0.70)
        if need > ch:
            ch = min(max(need, ch), cap)
            if not pillar:
                cw = min(ch * r, rw)
                if cw < ch * r:
                    ch = cw / r
            x = min(max(fcx - cw / 2, rx), rx + rw - cw)
            y = max(fcy - ch * panel["cy"], ry_t)
            y = max(y, low - panel.get("low_at", 0.70) * ch)
    y = max(ry_t, min(y, crown - 0.02 * ch))             # the head whole: the crown inside the crop
    # (guest Q's M31: the crown clamp put the chin 12 px under the answer bound): with the crown inside, the chin and
    # the lowest chin seen stay above low_at of the crop, or the crop grows 8 % a step (bounded by the region)
    for _ in range(10):
        chin = max(low or 0, fy + fh)
        if chin - y <= panel.get("low_at", 0.70) * ch or ch >= rh * (panel.get("ext", IG_EXT) if panel.get("bounded") else 1.6) - 1:   # (pass 3, tutorial-2 M2: a 330 px bubble region, chin 27 px under the bound at 1.45x): 1.6x
            break
        # (guest R's F3: a face 46 % of a 720 px source cannot hold crown and chin inside 63 % of the panel): the crop
        # may grow PAST the source (up to 1.45x its height; the faded extension fills below, as for a low chin), and
        # when the region's width runs out the crop is pillared over its own blur instead of stopping
        ch = min(rh * (panel.get("ext", IG_EXT) if panel.get("bounded") else 1.6), ch * 1.08)
        if ch * r > rw and panel.get("bounded") and rw >= iw - 2:
            ch = rw / r                       # the width is the limit on a full-bleed panel
            cw = rw
        elif ch * r > rw:
            pillar = True
            cw = rw
        elif not pillar:
            cw = ch * r
        x = min(max(fcx - cw / 2, rx), rx + rw - cw)
        y = max(ry_t, min(max(fcy - ch * panel["cy"], ry_t), crown - 0.02 * ch))
    if panel.get("bounded") and ch <= rh:
        y = max(ry_t, min(y, ry + rh - ch))   # ig_native: the crop stays on the source's bottom when it fits
    if pillar:
        y = max(y, ry)                        # a pillared crop has no top extension
    k = panel["h"] / ch
    ev = lambda v: int(round(v / 2) * 2)  # noqa: E731
    top_cut = max(0.0, ry - y)                # source rows above the source's top (ig_native only)
    y_vis = y + top_cut
    ch_vis = min(y + ch, ry + rh) - y_vis
    top_h = ev(top_cut * k)
    return {"cw": ev(cw), "ch": ev(ch), "ch_vis": max(2, ev(ch_vis)), "x": ev(x), "y": ev(y), "y_vis": ev(y_vis), "top_h": top_h,
            "vis_h": max(2, ev(ch_vis * k) + top_h), "k": k,
            "pillar": pillar, "out_w": ev(min(VW, cw * k)) if pillar else VW}


def crop_for(info, face, panel, region=None, low=None, high=None, hard=False):
    g = crop_geo(info, face, panel, region, low, high, hard)
    return g["cw"], g["ch"], g["x"], g["y"]


def face_on_frame(info, face, panel, region=None, low=None, high=None, hard=False):
    g = crop_geo(info, face, panel, region, low, high, hard)
    k = g["k"]
    fx, fy, fw, fh = face
    top = panel["y"] + (fy - g["y"]) * k
    left = ((VW - g["out_w"]) // 2 if g.get("pillar") else 0) + (fx - g["x"]) * k
    crown_y = panel["y"] + (min(fy, high if high is not None else fy) - 0.55 * fh - g["y"]) * k   # crop_geo's crown on the frame
    # the box's sides (the credit check reads them) and where the panel's real footage starts and stops
    return {"top": round(top), "bottom": round(top + fh * k), "mouth": round(top + 0.78 * fh * k), "scale": round(k, 3), "vis_h": g["vis_h"],
            "left": round(left), "right": round(left + fw * k), "top_h": g.get("top_h") or 0, "foot_y": panel["y"] + g["vis_h"],
            "pillar": bool(g.get("pillar")) and not g.get("ground_pillar"), "ground_pillar": bool(g.get("ground_pillar")), "legacy": bool(g.get("legacy")),
            "relax": g.get("relax", 0), "height": round(fh * k), "crown": round(crown_y),
            # 29 Oct (builder G): the reach the solve settled for, which blur_bottom_ok reads (it never arrived before: the
            # check's `g.get("need_used")` read a key face_on_frame dropped, so a softened 1536 always failed)
            "need_used": g.get("need_used")}


def medallion_geo(p, face, panel):
    """14:20 (the creator's ruling, tutorial-3, a live training: the only face during the deck is a 244x136 Zoom tile): a person
    with `medallion: {"box": [x, y, w, h], "scale": 2.5}` is shown as that source box scaled `scale`x (never more), centred
    as a medallion at the panel's top over the look's ground, instead of a face crop blown up to the panel's width."""
    m = p["medallion"]
    bx, by, bw, bh = [int(v) for v in m["box"]]
    k = float(m.get("scale", 2.5))
    mw, mh = int(round(bw * k / 2) * 2), int(round(bh * k / 2) * 2)
    fx, fy, fw, fh = face
    top = panel["y"] + (fy - by) * k
    return {"box": [bx, by, bw, bh], "k": k, "mw": mw, "mh": mh,
            "frame": {"top": round(top), "bottom": round(top + fh * k), "mouth": round(top + 0.78 * fh * k), "scale": round(k, 3), "vis_h": mh}}


# ---------------------------------------------------------------- retime (spans on a gone composed export's clock)
def _norm_tok(t):
    return re.sub(r"[^a-z0-9']", "", t.lower())


FILL_TOK = {"uh", "um", "like", "you", "know", "so", "i", "mean", "right", "okay", "yeah", "the", "a", "and"}


def _pieces_of(S, role):
    hook = S.get("hook") or {}
    out = []
    if hook.get("pieces"):
        # (guest R's F3, a retimed spec with an aha hook: its pieces carry the speaker as a 3rd element)
        for pc in hook["pieces"]:
            spk = pc[2] if len(pc) > 2 else (hook.get("speaker") or ("guest" if hook.get("mode") == "aha" and "guest" in (S.get("people") or {}) else "host"))
            if spk == role:
                out.append((float(pc[0]), float(pc[1])))
    out += [(float(pc[0]), float(pc[1])) for pc in (S.get("answer") or {}).get("pieces", []) if (pc[2] if len(pc) > 2 else "guest") == role]
    return out


def _coverage(ws, pieces, off):
    tot = sum(b - a for a, b in pieces) or 1.0
    inside = 0.0
    for a, b in pieces:
        inside += sum(max(0.0, min(b, w["e"] - off) - max(a, w["s"] - off)) for w in ws if w["e"] - off > a and w["s"] - off < b)
    return inside / tot


def scan_offset(ws, pieces, ref, span=45.0, step=0.02):
    """the offset in [ref - span, ref + span] that puts the most of this person's words inside this person's spans
    (a word-activity cross-correlation); returns (offset, coverage, runner-up coverage outside 1 s of the peak)."""
    best = []
    o = ref - span
    while o <= ref + span:
        best.append((_coverage(ws, pieces, o), o))
        o += step
    best.sort(reverse=True)
    top_cov, top = best[0]
    runner = max([c for c, o in best if abs(o - top) > 1.0] or [0.0])
    return top, top_cov, runner


def edge_scan(ws, pieces, ref, span=45.0, step=0.01, tol=0.04):
    """the offset that puts the most span EDGES on word edges (the spec writer cut on sentence edges): a piece start
    within tol of a word start, a piece end within tol of a word end. Sharp where word activity is flat (a monologue).
    Returns (offset, score, edges, runner-up score outside 0.3 s)."""
    import bisect
    starts = sorted(w["s"] for w in ws)
    ends = sorted(w["e"] for w in ws)

    def near(arr, t):
        i = bisect.bisect_left(arr, t)
        return any(abs(arr[j] - t) <= tol for j in (i - 1, i) if 0 <= j < len(arr))

    edges = [(a, True) for a, b in pieces] + [(b, False) for a, b in pieces]
    res = []
    o = ref - span
    while o <= ref + span:
        sc = sum(1 for t, is_start in edges if near(starts if is_start else ends, t + o))
        res.append((sc, o))
        o += step
    res.sort(key=lambda x: (-x[0], abs(x[1] - ref)))
    top_sc, top = res[0]
    runner = max([sc for sc, o in res if abs(o - top) > 0.3] or [0])
    return top, top_sc, len(edges), runner


def retime(S, work, spec_path=None):
    """needs_retime specs (guests Q, E and C): the spans sit on the composed export's clock and a person's offset
    is null. For each such person: (1) the span text (the hook's `text`, or a piece's 4th element) is matched against
    the person's own word file, the first 3 text words in order with fillers allowed between them, the candidate nearest
    the known offsets wins; (2) with no text, the offset is scanned 45 s either side of the known offset for the one that
    puts the most of the person's words inside the person's spans (coverage at least 60 %, the runner-up a second away at
    most 85 % of it). Then every piece of every person must have words under it on that person's file (30 %). A miss
    raises RetimeFailed (status retime-failed, never a crash). Measured offsets are written back into the spec."""
    if not S.get("needs_retime"):
        return S
    people = {k: v for k, v in S["people"].items() if v}
    known = [float(v["offset"]) for v in people.values() if v.get("offset") is not None]
    rec = S.get("retime") if isinstance(S.get("retime"), dict) else {}
    for role, p in people.items():
        if p.get("offset") is not None:
            continue
        ref = known[0] if known else 0.0
        ws = load_words(p["words"], p.get("scribe_speaker"), p.get("words_offset") or 0.0)
        pieces = _pieces_of(S, role)
        if not pieces:
            continue
        texts = []
        hook = S.get("hook") or {}
        if hook.get("pieces") and (hook.get("speaker") or "host") == role and hook.get("text"):
            texts.append((float(hook["pieces"][0][0]), hook["text"]))
        for pc in (S.get("answer") or {}).get("pieces", []):
            if len(pc) > 3 and pc[2] == role and isinstance(pc[3], str):
                texts.append((float(pc[0]), pc[3]))
        toks = [_norm_tok(w["t"]) for w in ws]
        cands = []
        for a, text in texts:
            tt = [_norm_tok(x) for x in text.split() if _norm_tok(x)]
            if len(tt) < 3:
                continue
            for i in range(len(toks)):
                if toks[i] != tt[0]:
                    continue
                j, k, n = i + 1, 1, 1
                while k < len(tt) and j < len(toks) and j - i < 4 * k + 6:
                    if toks[j] == tt[k]:
                        n += 1
                        k += 1
                    elif toks[j] not in FILL_TOK:
                        break
                    j += 1
                if n >= 3:
                    off = ws[i]["s"] - a
                    cands.append((abs(off - ref) if known else -n, -n, off, n))
        method, off, n = None, None, 0
        if cands:
            cands.sort()
            _, _, off, n = cands[0]
            method = f"span text, {n} words matched in order"
        else:
            if not known:
                raise RetimeFailed(f"{role}: no span text matched and no known offset to scan around")
            off, sc, n_edges, runner = edge_scan(ws, pieces, ref)
            off_ref, sc_ref, _, _ = edge_scan(ws, pieces, ref, span=0.08)
            if sc >= max(3, 0.5 * n_edges) and runner <= 0.8 * sc:
                method = f"span edges on word edges around {ref}: {sc} of {n_edges} edges, runner-up {runner}"
            elif sc_ref >= max(3, 0.6 * n_edges):
                off, method = off_ref, f"the known same-session offset {ref}: {sc_ref} of {n_edges} span edges sit on word edges there"
            else:
                off2, cov, runner2 = scan_offset(ws, pieces, ref)
                if cov < 0.6 or runner2 > 0.85 * cov:
                    raise RetimeFailed(f"{role}: edge scan {sc}/{n_edges} (runner-up {runner}) and activity scan coverage {cov:.2f} "
                                       f"(runner-up {runner2}) around {ref}: neither distinct")
                off, method = off2, f"word-activity scan around {ref}: coverage {cov:.2f}, runner-up {runner2:.2f}"
        cov = _coverage(ws, pieces, off)
        if cov < 0.3:
            raise RetimeFailed(f"{role}: offset {off:.2f} by {method} leaves {cov:.0%} of the spans with words")
        p["offset"] = round(off, 3)
        known.append(p["offset"])
        rec[role] = {"offset": round(off, 3), "method": method, "coverage": round(cov, 2), "nearest_known": ref}
    # every piece has words under it on its person's file
    for role, p in people.items():
        pieces = _pieces_of(S, role)
        if not pieces:
            continue
        off = float(p["offset"])
        ws = load_words(p["words"], p.get("scribe_speaker"), p.get("words_offset") or 0.0)
        for a, b in pieces:
            inside = sum(max(0.0, min(b, w["e"] - off) - max(a, w["s"] - off)) for w in ws if w["e"] - off > a and w["s"] - off < b)
            if (b - a) > 1.5 and inside < 0.3 * (b - a):
                raise RetimeFailed(f"{role} piece {a}-{b}: only {inside:.1f} s of words on the file at offset {off} (coverage under 30 %)")
    S["retime"] = {**rec, "checked": dt.datetime.now().strftime("%Y-%m-%d %H:%M"), "all_pieces_have_words": True}
    if spec_path:
        Path(spec_path).write_text(json.dumps(PATHS.canon_obj(S), indent=2))   # git keeps one spelling (paths.py)
    return S


class NoFaceBox(Exception):
    """a person with no face found and no box in the spec: the short is refused (status no-face-box), never built on a
    letterboxed full frame (reviewer C2, 27 Oct: the raw screen with private UI filled the face slot)."""


class RetimeFailed(Exception):
    pass


class _IgInk(Exception):
    """routes a check to ig_native's own bounds"""


# ---------------------------------------------------------------- the plan
def plan(S, work=None):
    """pieces -> output timeline. Returns dict(items=[{kind, speaker, a, b, n, out, layout}], hook_end, total_n)."""
    people = {k: v for k, v in S["people"].items() if v}
    for v in people.values():
        if not v.get("crop") and v.get("face_crop"):   # the tutorial specs' name for the box the face must stay inside
            v["crop"] = v["face_crop"]
    files = [v["file"] for v in people.values()]
    if len(files) > 1 and len(set(files)) < len(files):
        # a two-shot (guest X's phone tape): a person's crop hint keeps the other person out, so it may grow sideways
        # AWAY from the frame's centre to the edge, which a wide panel needs (a 405 px column gives the hook's 1080x440
        # panel a 165 px tall crop and cuts the head: proof of 02:43)
        for v in people.values():
            c = v.get("crop")
            if c and not v.get("crop_wide"):
                inf = info(v["file"])
                x, y, w, h = [int(t) for t in c]
                if x + w / 2 >= inf["w"] / 2:
                    v["crop"] = [x, y, inf["w"] - x, h]
                else:
                    v["crop"] = [0, y, x + w, h]
                v["crop_wide"] = True
    clock_p = S.get("clock") or "guest"
    tracks = {}
    LY = layout_for(S)
    duo = S.get("format") == "story-proof" and "guest" in people and "host" in people
    # 29 Oct (builder H, guest C's F1 r3: the stacked duo for 51.5 s, nobody full width; the reviewer: "aha full face on her,
    # the question stacked, the answer full face from 7.8 s with the duo only on the pieces where his reaction matters"):
    # a story-proof spec may name the answer pieces that keep the pair (`duo_pieces`, their spec start times); every other
    # piece, the aha opener and the introduction play full face. Without the field the whole short keeps the duo as before.
    duo_pcs = [float(x) for x in S["duo_pieces"]] if duo and isinstance(S.get("duo_pieces"), list) else None

    def duo_lay(a0):
        if not duo:
            return "answer"
        if duo_pcs is None:
            return "duo"
        return "duo" if any(abs(float(a0) - x) < 0.05 for x in duo_pcs) else "answer"

    def track(role):
        p = people[role]
        if role not in tracks:
            tracks[role] = Track(p["file"], p.get("offset") or 0.0)
        return tracks[role]

    def words(role):
        p = people[role]
        return load_words(p["words"], p.get("scribe_speaker"), p.get("words_offset") or 0.0)

    def snap(role, a, b):
        """in-point: the quietest 5 ms within 0.10 s before a. Out-point: the last kept word's decay toward the room floor,
        at most 0.5 s, never past the start of the first word the spec did NOT keep (its middle after b) minus 30 ms, so a
        trim the spec writer made ("kind of", a repeated "I,") never creeps back in. Kept words are the ones whose middle
        sits inside [a, b]."""
        tr = track(role)
        p = people[role]
        off = float(p.get("offset") or 0.0)
        ws = words(role)
        # 27 Oct (reviewers: 14 piece edges 80 to 300 ms inside a word): a kept word that straddles the out point
        # or starts within 80 ms after it is kept whole (b moves to its end); a kept word that straddles the in point is
        # kept whole too (a moves to its start). Kept = its middle inside the span.
        # 27 Oct (pass 2, set AB): only a word that STRADDLES b (starts before it) is kept whole; the old "starts
        # within 80 ms after b" clause pulled the NEXT word in ("answer," and "regardless" on guest G's S5, a stray "Or" on wave1-03)
        tail = [w for w in ws if w["s"] - off < b - 0.02 and w["e"] - off > b + 0.02 and (w["s"] + w["e"]) / 2 - off >= a]
        if tail:
            b = max(w["e"] - off for w in tail)
        head = [w for w in ws if w["s"] - off < a - 0.02 and w["e"] - off > a + 0.08 and (w["s"] + w["e"]) / 2 - off >= a]
        if head:
            a = max(0.0, min(w["s"] - off for w in head) - 0.01)
        a2 = tr.snap_in(a)
        lo = max([w["e"] - off for w in ws if (w["s"] + w["e"]) / 2 - off < a and w["e"] - off > a - 0.15] or [a - 1])
        a2 = max(a2, lo + 0.005) if lo > a - 0.15 else a2   # never back into a word the spec trimmed off the front
        a2 = min(a2, a)
        nxt = min([w["s"] - off for w in ws if (w["s"] + w["e"]) / 2 - off > b and w["e"] - off > b - 0.05] or [b + 10])
        cap = min(0.5, max(0.0, nxt - 0.03 - b))
        b2 = tr.decay_end(b, cap) if cap > 0.02 else b
        b2 = max(b, min(b2, nxt - 0.03)) if nxt - 0.03 > b else b
        return a2, max(b2, a2 + 0.2)

    items, out_t = [], 0.0
    cards = []
    if S.get("format") == "black-card" and S.get("cards"):
        cards = sorted(S["cards"], key=lambda c: c.get("before", 0))
    hook = S.get("hook")
    hook_end = -1.0
    hook_start = 0.0
    if hook and hook.get("pieces") and hook.get("mode") == "aha":
        # 27 Oct (Round-2 ruling, the creator: the hook rendered both ways): hook v2 opens on the aha line as a
        # preview, the speaker full frame (an answer-layout piece), no stacked pair, hook_end stays -1 so the overlay
        # treats the whole short as the answer; the spec is the `<id>-hook2` variant written beside the base spec
        for pc in hook["pieces"]:
            spk = pc[2] if len(pc) > 2 else (hook.get("speaker") or ("guest" if "guest" in people else "host"))
            a2, b2 = snap(spk, float(pc[0]), float(pc[1]))
            n = fq(b2 - a2)
            items.append({"kind": "answer", "speaker": spk, "a": a2, "b": a2 + n / FPS, "n": n, "out": out_t, "layout": duo_lay(pc[0]) if duo_pcs is None else "answer", "aha": True})
            out_t += n / FPS
        # 28 Oct (polish, the Round-3 order rule, the creator on guests D, P and F: "we kind of need the punchline first
        # ... unless there's such a good question that we would put that at the start"): after the aha the spec's `question`
        # (the stacked question hook, the host asking, the guest listening) plays, then the full answer, then `intro`
        q = S.get("question")
        if q and q.get("pieces") and S.get("question_full"):
            # 29 Oct (builder G; the conductor's reading of the creator's A note on guest Q's short: the co-host asks the
            # question, then the guest answers, with Round-3 "nobody small"): `question_full` plays the question full frame on
            # its own speaker (the answer_full framing, no stacked pair), so the short has no stacked hook (hook_end -1) and
            # the title stickers run as on any other stretch; _build2 sets it itself when the stacked faces cannot reach
            # IG_Q_FULL_BELOW (ig_question_full)
            spk = q.get("speaker") or "host"
            for a, b in q["pieces"]:
                a2, b2 = snap(spk, float(a), float(b))
                n = fq(b2 - a2)
                # on ig_native `answer` and `answer_full` are the same full-bleed framing: `answer` keeps add_transitions from
                # inserting a crossfade between 2 speakers' tapes at the cut (its fades are for one speaker's card splits)
                items.append({"kind": "answer", "speaker": spk, "a": a2, "b": a2 + n / FPS, "n": n, "out": out_t,
                              "layout": "answer" if S.get("_look") == "ig_native" else "answer_full", "question": True})
                out_t += n / FPS
        elif q and q.get("pieces"):
            spk = q.get("speaker") or "host"
            hook_start = out_t
            for a, b in q["pieces"]:
                a2, b2 = snap(spk, float(a), float(b))
                n = fq(b2 - a2)
                items.append({"kind": "hook", "speaker": spk, "a": a2, "b": a2 + n / FPS, "n": n, "out": out_t, "layout": "hook"})
                out_t += n / FPS
            hook_end = out_t
    elif hook and hook.get("pieces") and S.get("hook_full"):
        # 29 Oct (builder H, guest O's M1-animB r3: the guest 220 px in the stacked opener; at every seam of the drawn hook her
        # 300 px face with the host's head and collar above it needs her chin near 1574, past the 1500 safe line, so a zoom cannot
        # get there): `hook_full` plays the opening hook full frame on its own speaker, as `question_full` does for a question
        # (the conductor's reading of 19:05 on guest Q's F1), no stacked pair, hook_end -1
        spk = hook.get("speaker") or "host"
        for a, b in hook["pieces"]:
            a2, b2 = snap(spk, float(a), float(b))
            n = fq(b2 - a2)
            items.append({"kind": "answer", "speaker": spk, "a": a2, "b": a2 + n / FPS, "n": n, "out": out_t,
                          "layout": "answer" if S.get("_look") == "ig_native" else "answer_full", "question": True})
            out_t += n / FPS
    elif hook and hook.get("pieces"):
        spk = hook.get("speaker") or "host"
        for a, b in hook["pieces"]:
            a2, b2 = snap(spk, float(a), float(b))
            n = fq(b2 - a2)
            items.append({"kind": "hook", "speaker": spk, "a": a2, "b": a2 + n / FPS, "n": n, "out": out_t, "layout": "hook"})
            out_t += n / FPS
        hook_end = out_t
    op = S.get("opening_line")
    if op and op.get("pieces") and not (hook and hook.get("pieces")):
        for pc in op["pieces"]:
            spk = pc[2] if len(pc) > 2 else ("guest" if "guest" in people else "host")
            a2, b2 = snap(spk, float(pc[0]), float(pc[1]))
            n = fq(b2 - a2)
            items.append({"kind": "answer", "speaker": spk, "a": a2, "b": a2 + n / FPS, "n": n, "out": out_t, "layout": "answer"})
            out_t += n / FPS
    for pc in S["answer"]["pieces"]:
        a, b = float(pc[0]), float(pc[1])
        spk = pc[2] if len(pc) > 2 else ("guest" if "guest" in people else "host")
        for c in [c for c in cards if abs(float(c.get("before", -1)) - a) < 0.02]:
            n = fq(float(c.get("dur", 1.5)))
            items.append({"kind": "card", "speaker": None, "text": c["text"], "a": 0, "b": 0, "n": n, "out": out_t, "layout": "card"})
            out_t += n / FPS
        a2, b2 = snap(spk, a, b)
        n = fq(b2 - a2)
        items.append({"kind": "answer", "speaker": spk, "a": a2, "b": a2 + n / FPS, "n": n, "out": out_t, "layout": duo_lay(a)})
        out_t += n / FPS
    # 28 Oct (polish, the order rule): the guest's introduction (the host or cohost saying who they are) at the END of
    # the clip, never mid-clip and never right after the question (guest Q's B: "at the end of the clip we can do the
    # introduction, so it's not awkwardly in the middle"; guest S's A: "introducing him as the second thing ... awkward")
    intro = S.get("intro")
    for pc in ((intro or {}).get("pieces") or []):
        a, b = float(pc[0]), float(pc[1])
        spk = pc[2] if len(pc) > 2 else ("cohost" if "cohost" in people else "host")
        a2, b2 = snap(spk, a, b)
        n = fq(b2 - a2)
        items.append({"kind": "answer", "speaker": spk, "a": a2, "b": a2 + n / FPS, "n": n, "out": out_t, "layout": duo_lay(a) if duo_pcs is None else "answer", "intro": True})
        out_t += n / FPS
    # 27 Oct (night conductor; the creator on guest X's after-wave1-02: "the top card stays on screen too long without doing
    # anything ... change to full screen, showing me when I'm talking, showing [the guest] when he's talking, and then, when
    # there's something to do on the card, continue it to finish it. Then you can bring the card back on screen"):
    # with `card_only_moving: true` the card layout is kept only while a key animates; the short finishes on the card for
    # its last 3 s; the overlay reads `card_windows`.
    # (builder A, cause 4: guest C's M2 kept the card up 37 s, 1932.45 to 1969.51, because one long piece held all 6
    # keys): PER KEY, not per piece. Each key opens a window from 1.2 s before it to 2.5 s after it (windows closer than
    # 2 s merge); an answer piece is SPLIT at the word gap nearest each window edge (at least 0.12 s of silence, never
    # inside a word), the parts inside a window keep the card (`answer`), the rest go `answer_full`. An aha hook piece
    # never keeps the card. The split parts are contiguous on the tape (`cont`): their audio is cut as one run and their
    # captions read as one span, so nothing is heard or captioned differently.
    if S.get("card_only_moving") and (S.get("graphic") or {}).get("keys") and S.get("_look") != "ig_native":
        items = card_windows_split(S, items, words, people)
    if duo and is_igmode(S):
        items = duo_tail_full(S, items, words, people)
    if S.get("ig_list_room") and S.get("_look") == "ig_native" and (S.get("graphic") or {}).get("keys"):
        items = ig_list_split(S, items, words, people)
    runs = runs_of(items)
    # (builder A, cause 4, "a real transition in and out"): every change between `answer_full` and the card
    # layout is a 0.3 s crossfade of the two framings (an `xfade` piece of 9 frames: the last 4 of the piece before and
    # the first 5 of the piece after), so the face glides from one framing to the other while the page's band moves in
    # the same 0.3 s; the audio and the captions read the runs above, untouched and continuous
    items = add_transitions(items)
    return {"items": items, "hook_end": hook_end, "hook_start": hook_start, "total_n": int(round(out_t * FPS)), "people": people, "clock": clock_p,
            "duo_part": duo_pcs is not None,
            "words": words, "track": track, "layout": LY, "runs": runs}


XF_N = 9          # the crossfade, frames (0.3 s at 30 fps)
XF_PRE = 4        # frames taken from the piece before the change


def _gaps(ws, off, a, b, min_gap=0.12):
    """the silences between consecutive words inside (a, b) on the tape's clock, as (start, end, middle)"""
    ws = sorted(ws, key=lambda w: w["s"])
    out = []
    for w0, w1 in zip(ws, ws[1:]):
        g0, g1 = w0["e"] - off, w1["s"] - off
        if g1 - g0 >= min_gap and a + 0.25 < g0 and g1 < b - 0.25:
            out.append((g0, g1, (g0 + g1) / 2))
    return out


def card_windows_split(S, items, words, people):
    ks = sorted(float(k[1]) for k in S["graphic"]["keys"] if len(k) > 1 and k[1] is not None)
    wins = []
    for k in ks:
        w = [k - 1.2, k + 2.5]
        if wins and w[0] - wins[-1][1] < 2.0:
            wins[-1][1] = max(wins[-1][1], w[1])
        else:
            wins.append(w)
    out = []
    aha_keys = bool(S.get("aha_keys"))   # 28 Oct (polish, guest X's F: "Start with the kicker, with the animation of the red, yellow, green"): the aha opener takes its keys
    ans = [it for it in items if it["kind"] == "answer" and it["layout"] == "answer" and (aha_keys or not it.get("aha")) and not it.get("intro")]
    last_ans = ans[-1] if ans else None
    # 29 Oct (row 193): on ig_between the last 6 s of the output carry the credit at y 1400 over the full-bleed face, so no
    # card window runs into them (guest C's M2-animC: the window held to the end and the credit crossed her chin)
    igb_cut = None
    if S.get("ig_between") and items:
        tot_1x = max(x["out"] + x["n"] / FPS for x in items)
        igb_cut = tot_1x - 6.0 * spec_speed(S) - 0.3
    for it in items:
        if (it.get("aha") and not aha_keys and it["layout"] == "answer") or (it.get("intro") and it["layout"] == "answer"):
            out.append(dict(it, layout="answer_full"))   # an aha preview never keeps the card (guest C's M2-hook2, guest O's M1-hook2); nor the intro at the end
            continue
        if not any(it is x for x in ans):
            out.append(it)
            continue
        p = people[it["speaker"]]
        off = float(p.get("offset") or 0.0)
        ws = words(it["speaker"])
        gaps = _gaps(ws, off, it["a"], it["b"])
        bounds = _gaps(ws, off, it["a"], it["b"], min_gap=0.0)   # every word boundary (touching words included)
        # the edges inside this piece: a window start must leave the card up at least 0.3 s before its key word lands,
        # an end at least 1.0 s after; the gap nearest the window's edge on the right side of that bound wins
        cuts = []
        for w0, w1 in wins:
            kin = [k for k in ks if w0 <= k <= w1]
            if not kin:
                continue
            k_first, k_last = kin[0], kin[-1]
            # (conductor, after guest C's M2 held the card still 36 to 42.6 s: she never pauses 0.12 s there): a gap of
            # 0.12 s or more within 0.6 s of the edge wins; failing that, the word boundary nearest the edge (between 2
            # words, never inside one; the 0.3 s crossfade hides the cut, and the sound is the run's, untouched)
            for edge, ok in ((w0, lambda t: t <= k_first - 0.3), (w1, lambda t: t >= k_last + 1.0)):
                if not it["a"] < edge < it["b"]:
                    continue
                c = [g for g in gaps if ok(g[2]) and abs(g[2] - edge) <= 0.6]
                if not c:
                    c = [g for g in bounds if ok(g[2])]
                if c:
                    cuts.append(min(c, key=lambda g: abs(g[2] - edge))[2])
        # the finish: the last 3 s of the short on the card (a gap near it, else the exact 3 s)
        igb_end = bool(S.get("ig_between"))   # 29 Oct (row 193, guest C's M2-animC credit_face_ok): an animated short ends in the Instagram look, the credit at y 1400 over the full-bleed face, never on the card's low face
        if it is last_ans and it["n"] >= 6 * FPS and not igb_end:
            t3 = it["b"] - 3.0
            c = [g for g in gaps if abs(g[2] - t3) <= 0.6] or [g for g in bounds if abs(g[2] - t3) <= 1.0]
            cuts.append(min(c, key=lambda g: abs(g[2] - t3))[2] if c else t3)
        if igb_cut is not None and it["out"] < igb_cut < it["out"] + it["n"] / FPS:
            e_src = it["a"] + (igb_cut - it["out"])
            c = [g for g in bounds if g[2] <= e_src and e_src - g[2] <= 1.5]
            cuts.append(max(c, key=lambda g: g[2])[2] if c else e_src)
        cuts = sorted(set(round(c, 3) for c in cuts if it["a"] + 0.4 < c < it["b"] - 0.4))
        parts, prev_n = [], 0
        for c in cuts + [it["b"]]:
            n_at = it["n"] if c == it["b"] else int(round((c - it["a"]) * FPS))
            if n_at - prev_n < 6:     # under 0.2 s: no part
                continue
            parts.append((prev_n, n_at))
            prev_n = n_at
        if parts and parts[-1][1] != it["n"]:
            parts[-1] = (parts[-1][0], it["n"])
        for j, (n0, n1) in enumerate(parts):
            a = it["a"] + n0 / FPS
            b = it["a"] + n1 / FPS
            mid = (a + b) / 2
            on = any(w0 - 0.05 <= mid <= w1 + 0.05 and any(a - 1.6 <= k <= b + 0.3 for k in ks) for w0, w1 in wins) or any(a - 0.05 <= k <= b for k in ks)
            if it is last_ans and n1 == it["n"] and len(parts) > 1 and (n1 - n0) <= 4 * FPS and not igb_end:
                on = True        # the finish
            if igb_cut is not None and it["out"] + (n0 + n1) / 2 / FPS >= igb_cut:   # the part lies mostly in the last 6 s
                on = False       # the credit's last 6 s on an animated short: the Instagram look
            out.append(dict(it, a=a, b=b, n=n1 - n0, out=it["out"] + n0 / FPS, layout="answer" if on else "answer_full", cont=j > 0))
        if not parts:
            out.append(it)
    # a full-face stretch under 2 s between two card parts stays on the card (no flash), and a lone card part with no
    # key and no finish inside goes full
    for i in range(1, len(out) - 1):
        if out[i].get("layout") == "answer_full" and not (out[i].get("aha") and not aha_keys) and not out[i].get("intro") and out[i]["kind"] == "answer" and out[i]["n"] < 2 * FPS \
                and not (igb_cut is not None and out[i]["out"] >= igb_cut - 0.05) \
                and out[i - 1].get("layout") == "answer" and out[i + 1].get("layout") == "answer":
            out[i] = dict(out[i], layout="answer")
    if last_ans is not None and out and out[-1]["kind"] == "answer" and out[-1].get("layout") == "answer_full" and out[-1]["n"] < 6 * FPS and not out[-1].get("intro") and not S.get("ig_between"):
        out[-1] = dict(out[-1], layout="answer")   # a short last piece finishes on the card whole (17:05)
    return out


def duo_tail_full(S, items, words, people):
    """29 Oct (builder G, conductor 17:25, guest C's F1: credit_face_ok failed at 48.82 s, the ig credit at y 1400 to 1460 across
    the duo guest's face, 1314 to 1524, a 210 px face): on the Instagram looks a story-proof short's `duo` (host above, guest
    below, the guest's face low and small) never runs in the credit's last 6 s. A duo piece lying in them goes to the full
    face (`answer_full`: the speaker alone, chin at or above 1380, the credit under it); one that straddles the line is split
    at the last word boundary before it (within 1.5 s), the part after contiguous (`cont`), so the sound and the captions
    are one run. The change of framing is a cut at that word boundary (add_transitions fades only answer to answer_full)."""
    if not items:
        return items
    tot_1x = max(x["out"] + x["n"] / FPS for x in items)
    cut = tot_1x - 6.0 * spec_speed(S) - 0.3
    out = []
    for it in items:
        end = it["out"] + it["n"] / FPS
        if it["kind"] == "card" or it.get("layout") != "duo" or end <= cut:
            out.append(it)
            continue
        if it["out"] >= cut - 0.05:
            out.append(dict(it, layout="answer_full"))
            continue
        p = people[it["speaker"]]
        off = float(p.get("offset") or 0.0)
        e_src = it["a"] + (cut - it["out"])
        bounds = _gaps(words(it["speaker"]), off, it["a"], it["b"], min_gap=0.0)
        c = [g for g in bounds if g[2] <= e_src and e_src - g[2] <= 1.5]
        t = max(c, key=lambda g: g[2])[2] if c else e_src
        n0 = int(round((t - it["a"]) * FPS))
        if n0 < 6:
            out.append(dict(it, layout="answer_full"))
            continue
        if it["n"] - n0 < 6:
            out.append(it)      # the tail under 0.2 s: left on the duo (the check will name it)
            continue
        out.append(dict(it, b=it["a"] + n0 / FPS, n=n0))
        out.append(dict(it, a=it["a"] + n0 / FPS, n=it["n"] - n0, out=it["out"] + n0 / FPS, layout="answer_full", cont=True))
    return out


def ig_list_split(S, items, words, people):
    """29 Oct (builder H, guest C's M1 r3): with `ig_list_room` the answer pieces from the one the first list key lands in
    to the end take `answer_list` (her head lowered under the list, ig_list_layout); the introduction keeps its framing (the
    list is off over it). A first key more than 4 s into its piece splits that piece at the word gap nearest 0.3 s before
    the key (the part after contiguous, `cont`: one run for sound and captions), so the reframe is a cut between 2 words;
    otherwise the reframe sits on the piece's own cut."""
    ks = sorted(float(k[1]) for k in S["graphic"]["keys"] if len(k) > 1 and k[1] is not None)
    if not ks:
        return items
    k0 = ks[0]
    host = next((it for it in items if it["kind"] == "answer" and not it.get("aha") and not it.get("intro")
                 and it["a"] - 0.05 <= k0 <= it["b"] + 0.05), None)
    if host is None:
        later = [it for it in items if it["kind"] == "answer" and not it.get("aha") and not it.get("intro") and it["a"] > k0]
        host = min(later, key=lambda it: it["out"]) if later else None
    if host is None:
        return items
    out = []
    for it in items:
        if it["out"] < host["out"] - 1e-6 or it["kind"] != "answer" or it.get("intro") or it.get("aha") or it["layout"] != "answer":
            out.append(it)
            continue
        if it is host and k0 - it["a"] > 4.0:
            p = people[it["speaker"]]
            off = float(p.get("offset") or 0.0)
            ws = words(it["speaker"])
            want = k0 - 0.3
            c = [g for g in _gaps(ws, off, it["a"], it["b"]) if g[2] <= want and want - g[2] <= 1.5] or \
                [g for g in _gaps(ws, off, it["a"], it["b"], min_gap=0.0) if g[2] <= want]
            t = max(c, key=lambda g: g[2])[2] if c else want
            n0 = int(round((t - it["a"]) * FPS))
            if 6 <= n0 <= it["n"] - 6:
                out.append(dict(it, b=it["a"] + n0 / FPS, n=n0))
                out.append(dict(it, a=it["a"] + n0 / FPS, n=it["n"] - n0, out=it["out"] + n0 / FPS, layout="answer_list", cont=True))
                continue
        out.append(dict(it, layout="answer_list"))
    return out


def runs_of(items):
    """the contiguous runs of the tape: consecutive pieces of one speaker cut back to back from one stretch (`cont`)
    merged, so the audio, the captions and the speaker check see one piece where the card split made several"""
    runs = []
    for it in items:
        if it["kind"] == "card":
            runs.append(dict(it))
            continue
        if runs and it.get("cont") and runs[-1]["kind"] == it["kind"] and runs[-1]["speaker"] == it["speaker"] \
                and abs(runs[-1]["b"] - it["a"]) < 0.5 / FPS:
            runs[-1]["b"] = it["b"]
            runs[-1]["n"] += it["n"]
            continue
        runs.append({k: v for k, v in it.items() if k != "cont"})
    return runs


def add_transitions(items):
    """a 9-frame `xfade` piece at every change between `answer_full` and `answer` (the card): 4 frames from the end of the
    piece before, 5 from the start of the piece after; each side of the fade is cut from its own piece's tape (the
    piece before runs on 5 frames past its end, the piece after starts 4 frames early), so a contiguous split fades
    between 2 framings of the same frames and a real cut dissolves"""
    out = []
    for it in items:
        prev = out[-1] if out else None
        pair = {prev.get("layout") if prev else None, it.get("layout")}
        if prev and prev["kind"] == "answer" and it["kind"] == "answer" and pair == {"answer", "answer_full"} \
                and prev["n"] >= XF_PRE + 6 and it["n"] >= (XF_N - XF_PRE) + 6:
            post = XF_N - XF_PRE
            prev["n"] -= XF_PRE
            prev["b"] = prev["a"] + prev["n"] / FPS
            xf = {"kind": "answer", "speaker": it["speaker"], "a": prev["b"], "b": prev["b"] + XF_N / FPS, "n": XF_N,
                  "out": prev["out"] + prev["n"] / FPS, "layout": "xfade", "from": prev["layout"], "to": it["layout"],
                  "src_a": [prev["speaker"], prev["b"]], "src_b": [it["speaker"], it["a"] - XF_PRE / FPS], "cont": True}
            nxt = dict(it, a=it["a"] + post / FPS, n=it["n"] - post, out=it["out"] + post / FPS, cont=True)
            nxt["b"] = nxt["a"] + nxt["n"] / FPS
            out.append(xf)
            out.append(nxt)
            continue
        out.append(dict(it))
    return out




# ---------------------------------------------------------------- captions
_CALIB = {}


def calib_ratio(size):
    """libass drawn width / PIL textlength for Montserrat Bold at this size, measured once (the 2 earlier builds disagreed:
    0.649 and 0.85), cached beside the work root."""
    if size in _CALIB:
        return _CALIB[size]
    cache = WORKROOT / f"calib-{size}.json"
    if cache.exists():
        _CALIB[size] = json.loads(cache.read_text())["ratio"]
        return _CALIB[size]
    txt = "reviewing what AI wrote"
    f = ImageFont.truetype(str(MONT), size)
    pil_w = ImageDraw.Draw(Image.new("RGB", (8, 8))).textlength(txt, font=f)
    style = STYLE_CAP.replace(",104,", f",{size},")
    ass = ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 2\n\n[V4+ Styles]\n"
           "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
           f"{style}\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
           f"Dialogue: 0,0:00:00.00,0:00:01.00,Cap,,0,0,0,,{{\\an5\\pos(540,960)\\shad0}}{txt}\n")
    WORKROOT.mkdir(parents=True, exist_ok=True)
    tmp = WORKROOT / f"calib-{size}.ass"
    tmp.write_text(ass)
    out = run([FF, "-v", "error", "-f", "lavfi", "-t", "1", "-i", "color=c=black:s=1080x1920:r=1", "-vf",
               f"ass={tmp}:fontsdir={FONTDIR}", "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "gray", "-"], timeout=120, label="calib", binary=True).stdout
    fr = np.frombuffer(out, np.uint8).reshape(1920, 1080)
    cols = np.where((fr > 128).sum(axis=0) > 0)[0]
    drawn = int(cols.max() - cols.min() + 1)
    ratio = drawn / pil_w
    cache.write_text(json.dumps({"ratio": ratio, "drawn": drawn, "pil": pil_w, "text": txt}))
    _CALIB[size] = ratio
    return ratio


def drawn_width(text, size):
    f = ImageFont.truetype(str(MONT), size)
    return ImageDraw.Draw(Image.new("RGB", (8, 8))).textlength(text, font=f) * calib_ratio(size)


_UNITS = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
          "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19}
_TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}
_SCALE = {"hundred": 100, "thousand": 1000, "million": 1000000, "billion": 1000000000}


def digits(words, money=None):
    """number words to digits, captions only ("three or four" -> "3 or 4", "twenty percent" -> "20%"); never "one" alone
    (an article more often than a count)."""
    out, i = [], 0
    while i < len(words):
        w = words[i]
        core = re.sub(r"[^a-z\-]", "", w["t"].lower())
        parts = core.split("-")
        val, j, consumed = 0, i, 0
        cur = 0
        # 27 Oct: "twenty-six-page" -> "26-page" (number parts, then a word part, in one hyphenated token)
        if len(parts) >= 2 and parts[-1] and parts[-1] not in _UNITS and parts[-1] not in _TENS and parts[-1] not in _SCALE \
                and all(pt in _UNITS or pt in _TENS for pt in parts[:-1]):
            tot = sum(_UNITS.get(pt, 0) + _TENS.get(pt, 0) for pt in parts[:-1])
            punct = re.search(r"[,.?!]+$", w["t"])
            out.append({**w, "t": f"{tot}-{parts[-1]}" + (punct.group(0) if punct else "")})
            i += 1
            continue
        while j < len(words):
            c = re.sub(r"[^a-z\-]", "", words[j]["t"].lower())
            ps = c.split("-")
            ok = True
            for ptok in ps:
                if ptok in _UNITS:
                    cur += _UNITS[ptok]
                elif ptok in _TENS:
                    cur += _TENS[ptok]
                elif ptok in _SCALE:
                    cur = (cur or 1) * _SCALE[ptok]
                    val += cur
                    cur = 0
                elif ptok == "and" and consumed and j + 1 < len(words) and re.sub(r"[^a-z]", "", words[j + 1]["t"].lower()) in (_UNITS | _TENS):
                    pass
                else:
                    ok = False
                    break
            if not ok:
                break
            consumed += 1
            j += 1
            if words[j - 1]["t"].rstrip().endswith((",", ".", "?", "!")):
                break
        total = val + cur
        # 2 Nov (guest V's W-A: "$2 billion" became "$2 1,000,000,000" and "a billion dollars" "$1000000K"): a bare
        # scale word with no count before it stays a word
        if consumed and not (consumed == 1 and core == "one") and not (consumed == 1 and core == "zero") and not (consumed == 1 and core in _SCALE):
            last = words[j - 1]
            punct = re.search(r"[,.?!]+$", last["t"])
            suffix = ""
            if j < len(words) and re.sub(r"[^a-z]", "", words[j]["t"].lower()) == "percent":
                suffix = "%"
                punct = re.search(r"[,.?!]+$", words[j]["t"]) or punct
                j += 1
            txt = f"{total:,}{suffix}" if total < 1e4 else f"{total:,}{suffix}"
            txt = f"{total}{suffix}" if total < 10000 else txt
            # 27 Oct (pass 2, a guest's figure said with no $): a figure the spec's graphic writes as money, or
            # one followed by "dollars"/"bucks", is captioned as money, "$25K" when it is a round thousand, else "$3,500"
            nxt_core = re.sub(r"[^a-z]", "", words[j]["t"].lower()) if j < len(words) else ""
            if not suffix and money and total < 1000 and total * 1000 in money and total not in money:
                total *= 1000   # "twenty" beside "$25K" in a ledger of thousands (20 and 5 are $20K and $5K)
            if not suffix and (nxt_core in ("dollars", "bucks") or (money and total in money)):
                txt = f"${total // 1000}K" if total >= 1000 and total % 1000 == 0 else f"${total:,}"
                if nxt_core in ("dollars", "bucks"):
                    punct = re.search(r"[,.?!]+$", words[j]["t"]) or punct
                    j += 1
            out.append({**w, "t": txt + (punct.group(0) if punct else ""), "e": words[j - 1]["e"]})
            i = j
        else:
            out.append(w)
            i += 1
    return out


def clean_caption_words(ws, drops=(), fixes=None, money=None):
    """fillers, the spec's drops, immediate repeats and false starts out of the CAPTIONS only; house spellings; digits."""
    drops = {d.lower().strip(",.") for d in (drops or [])}
    out = []
    for w in ws:
        t = w["t"].replace("“", '"').replace("”", '"').replace("’", "'")
        core = re.sub(r"[^a-z0-9'\-]", "", t.lower())
        if FILLER.match(t) or core in drops:
            continue
        if t.endswith("-") and len(core) <= 5 and not t.endswith("--"):   # a false start: "gon-", "w-", "s-"
            continue
        if t.endswith("--"):
            t = t[:-2] + ","
        base = re.sub(r"[^a-z0-9']", "", t.lower())
        if base in FIXES:
            punct = re.search(r"[,.?!\"]+$", t)
            t = FIXES[base] + (punct.group(0) if punct else "")
        if fixes:
            for k, v in fixes.items():
                kp = re.search(r"[,.?!;:]+$", k)
                if kp:
                    # (builder B's open item, guest R's F3 'Those 22,'): a target that names its own punctuation
                    # ("22," -> "22") matches the word with that punctuation and the fix replaces it whole, so the
                    # fix's punctuation wins; a target without punctuation keeps the word's own, as before
                    if base == re.sub(r"[^a-z0-9']", "", k.lower()) and t.rstrip('"').lower().endswith(kp.group(0)):
                        t = v
                        break
                elif base == re.sub(r"[^a-z0-9']", "", k.lower()):
                    punct = re.search(r"[,.?!\"]+$", t)
                    t = v + (punct.group(0) if punct else "")
        t = t.replace('"', "")
        if not re.sub(r"[^a-z0-9]", "", t.lower()):
            continue
        out.append({**w, "t": t})
    # a lone backchannel sentence ("Yeah.", "Basically.", "Okay.") between sentence ends is dropped from the captions
    BACK = re.compile(r"^(yeah|yes|yep|okay|ok|right|basically|exactly|sure|wow|mm)[,.?!]*$", re.I)
    kept = []
    for i, w in enumerate(out):
        prev_end = not kept or kept[-1]["t"].endswith((".", "?", "!"))
        this_end = w["t"].endswith((".", "?", "!", ","))
        last_of_piece = i == len(out) - 1
        if BACK.match(w["t"]) and (this_end and prev_end or w["t"].endswith((".", "?", "!"))) and not (last_of_piece and not prev_end):
            # 27 Oct (pass 2, set CE): the LAST word of a piece that closes a running sentence ("healthy, okay.",
            # "...right.") is the speaker's own close and stays; a lone "Okay." between sentences still goes
            # an "Okay." inside a running sentence (bleed or her own aside) goes, and the word after it loses the
            # capital Scribe gave it, unless it is a house spelling or an acronym
            if not prev_end and i + 1 < len(out):
                nx = out[i + 1]["t"]
                if nx[:1].isupper() and not nx.isupper() and nx.rstrip(",.?!") not in FIXES.values() and len(nx) > 1 and not nx[1:2].isupper():
                    out[i + 1] = dict(out[i + 1], t=nx[:1].lower() + nx[1:])
            continue
        kept.append(w)
    out = kept
    # immediate repeats by the same speaker ("I, I feel"): keep the second, give it the first's capital
    res = []
    for i, w in enumerate(out):
        if i + 1 < len(out):
            a, b = re.sub(r"[^a-z0-9']", "", w["t"].lower()), re.sub(r"[^a-z0-9']", "", out[i + 1]["t"].lower())
            if a and a == b and out[i + 1]["s"] - w["e"] < 1.0:
                if w["t"][:1].isupper() and out[i + 1]["t"][:1].islower():
                    out[i + 1]["t"] = out[i + 1]["t"][:1].upper() + out[i + 1]["t"][1:]
                continue
        res.append(w)
    return digits(res, money)


def spec_money(S):
    """the dollar figures the spec's graphic writes ("Product|$25,000 a year", "Setup fee: $2,500") as ints."""
    g = S.get("graphic") or {}
    txt = " ".join(map(str, (g.get("items") or []))) + " " + " ".join(str(k[0]) for k in (g.get("keys") or []))
    vals = set()
    for m in re.finditer(r"\$\s?([0-9][0-9,]*(?:\.[0-9]+)?)\s?([KkMm])?", txt):
        v = float(m.group(1).replace(",", ""))
        v *= {"k": 1e3, "m": 1e6}.get((m.group(2) or "").lower(), 1)
        vals.add(int(round(v)))
    return vals


def drawn_chunks(W, speed=1.0, one_line=False):
    """the drawn looks' caption groups for one block of words ({t, os, oe, run, run_start, run_end}, output seconds at
    1.0x): a shortest path over break points. A group costs 1.5, plus 1 a word under 4; 1000 for a line of 1 word (or a
    group of 1 word), 500 when on screen under 0.3 s after the speed, 3 when it needs the 760 px stretch, unplaceable
    past 2 lines; 6 for running across a sentence end or a pause over 0.6 s inside it, 4 across a cut, 3 for ending on a
    function word, minus 2 for ending on a comma or a full stop. Size 118 for a group starting in the first 8 s (6 words
    at most), else 104 (7)."""
    n = len(W)
    if n == 0:
        return []

    def cost(i, j):
        texts = [W[k]["t"] for k in range(i, j)]
        nw = j - i
        g_s = max(W[i]["run_start"], W[i]["os"] - 0.06)
        g_e = min(W[j - 1]["oe"] + 0.16, W[j - 1]["run_end"] - 1.0 / FPS)
        if j < n:
            g_e = min(g_e, W[j]["os"] - 0.07)
        size = 104 if one_line else (118 if W[i]["os"] < 8.0 else 104)
        if nw > (6 if size == 118 else 7) + 1:
            return math.inf
        c = 1.5 + 1.0 * max(0, 4 - nw)
        ln = two_lines(texts, size)
        if one_line and ln is not None and len(ln) > 1:
            ln = None                     # the hook's caption is 1 line (it sits in the seam between the faces)
        if ln is None:
            ln = two_lines(texts, size, CAP_MERGE_W)
            c += 3
            if one_line and ln is not None and len(ln) > 1:
                ln = None
        if ln is None:
            if nw > 1:
                return math.inf
            c += 1000
        elif nw == 1 or any(len(x) < 2 for x in ln):
            c += 1000
        # 29 Oct (builder G): a group with a group after it in the block may be held up to CAP_HOLD past its own end
        # (caption_groups pushes the next group's start by as much), so fast speech is not forced into a 2-word flash
        if (max(g_e, g_s + 0.12) + (CAP_HOLD if j < n else 0.0) - g_s) / speed < MIN_LINE_S:
            c += 500
        for k in range(i, j - 1):
            if re.search(r"[.?!]$", W[k]["t"]) or W[k + 1]["os"] - W[k]["oe"] > 0.6:
                c += 6
            if W[k + 1]["run"] != W[k]["run"]:
                c += 4
        last = W[j - 1]["t"]
        if re.sub(r"[^a-z']", "", last.lower()) in NO_END:
            c += 3
        if re.search(r"[,.?!;:]$", last):
            c -= 2
        return c
    best = [0.0] + [math.inf] * n
    back = [0] * (n + 1)
    for j in range(1, n + 1):
        for i in range(max(0, j - 8), j):
            if best[i] == math.inf:
                continue
            v = best[i] + cost(i, j)
            if v < best[j]:
                best[j], back[j] = v, i
    out, j = [], n
    while j > 0:
        i = back[j]
        out.append(W[i:j])
        j = i
    return list(reversed(out))


def caption_groups(P, S):
    """[{style, s, e, words:[(text, s, e)], lines:[[idx..]]}] in OUTPUT time (1.0x, before speed), never across a piece."""
    groups = []
    prev_word = {}
    drawn_runs = []
    for it in (P.get("runs") or P["items"]):   # a card split is one span to the captions
        if it["kind"] == "card":
            continue
        ws = P["words"](it["speaker"])
        p = P["people"][it["speaker"]]
        off = float(p.get("offset") or 0.0)
        a, b = it["a"], it["b"]
        inw = [dict(w, s=w["s"] - off, e=w["e"] - off) for w in ws if a - 0.02 <= ((w["s"] + w["e"]) / 2 - off) <= b]
        agent = False
        if p.get("scribe_speaker") and sum(w["e"] - w["s"] for w in inw) < 0.3 * (b - a):
            # a shared word file where this piece belongs to another voice on the same track: a tutorial's live test call
            # (tutorial-1, the AI voice agent as speaker_1) is captioned in the Agent style with a chip (27 Oct)
            allw = load_words(p["words"], None, p.get("words_offset") or 0.0)
            oth = [dict(w, s=w["s"] - off, e=w["e"] - off) for w in allw if a - 0.02 <= ((w["s"] + w["e"]) / 2 - off) <= b]
            if sum(w["e"] - w["s"] for w in oth) >= 0.3 * (b - a) and len(P["people"]) == 1:
                inw, agent = oth, True
        inw = clean_caption_words(inw, S.get("caption_drops"), S.get("caption_fix"), spec_money(S))
        if not inw:
            continue
        # a span that opens mid-sentence gets a capital, but a trim inside one sentence (same speaker, under 2 s of tape
        # cut, the word before the cut not a sentence end) does not
        prev_end = prev_word.get(it["speaker"])
        opens = prev_end is None or (a - prev_end["b"]) > 2.0 or prev_end["t"].endswith((".", "?", "!"))
        if opens and inw[0]["t"][:1].islower():
            inw[0] = dict(inw[0], t=inw[0]["t"][:1].upper() + inw[0]["t"][1:])
        prev_word[it["speaker"]] = {"b": b, "t": inw[-1]["t"]}
        for i in range(1, len(inw)):   # a word after a sentence end takes a capital (a dropped "Like," left it lowercase)
            if inw[i - 1]["t"].endswith((".", "?", "!")) and inw[i]["t"][:1].islower():
                inw[i] = dict(inw[i], t=inw[i]["t"][:1].upper() + inw[i]["t"][1:])
        # sentences: punctuation, a pause over 0.6 s
        sents, cur = [], []
        for w in inw:
            if cur and w["s"] - cur[-1]["e"] > 0.6:
                sents.append(cur)
                cur = []
            cur.append(w)
            if w["t"].endswith((".", "?", "!")) and not w["t"].upper().rstrip(".") in ("DR", "MR", "MS", "MRS", "ST"):
                sents.append(cur)
                cur = []
        if cur:
            sents.append(cur)
        merged = []
        for sn in sents:
            if merged and len(merged[-1]) <= 2 and not merged[-1][-1]["t"].endswith((".", "?", "!")) and sn[0]["s"] - merged[-1][-1]["e"] < 1.5:
                merged[-1] = merged[-1] + sn
            else:
                merged.append(sn)
        if S.get("_look") != "ig_native":
            # (builder A, cause 3: guest U's M1 'language,' and 'accusations, / defensiveness,' kept a lone word
            # after the greedy chunker and the merge pass; guest J's M1 'Where' sat alone on a 7-frame piece): the drawn
            # looks lay the words out by a shortest path over BLOCKS of pieces (one speaker, under 1 s apart), after
            # this loop (`drawn_chunks`), so a group never leaves a word alone on a line when any layout avoids it
            drawn_runs.append({"it": it, "a": a, "b": b, "agent": agent, "hook": it.get("layout") == "hook",
                               "w": [{"t": x["t"], "os": it["out"] + max(0.0, x["s"] - a), "oe": it["out"] + min(b - a, x["e"] - a)} for x in inw]})
            plan_chunks = []
        else:
            plan_chunks = []
            for sn in merged:
                out_s = it["out"] + (sn[0]["s"] - a)
                sz = 118 if out_s < 8.0 else 104
                plan_chunks += [(c, sz) for c in chunk_sentence(sn, sz, 6 if sz == 118 else 7)]
        for c, size in plan_chunks:
            big = size == 118
            if True:
                lines = two_lines([x["t"] for x in c], size) or two_lines([x["t"] for x in c], size, CAP_MERGE_W) or [list(range(len(c)))]
                g_s = it["out"] + max(0.0, c[0]["s"] - a - 0.06)
                g_e = it["out"] + min(b - a, c[-1]["e"] - a + 0.16)
                g_e = min(g_e, it["out"] + (b - a) - 1.0 / FPS)   # never onto the cut
                if g_e - g_s < 0.12:
                    g_e = g_s + 0.12
                words = [(x["t"], it["out"] + max(0.0, x["s"] - a), it["out"] + min(b - a, x["e"] - a)) for x in c]
                groups.append({"style": "Agent" if agent else "Big" if big else "Cap", "s": g_s, "e": g_e, "w": words, "lines": lines,
                               "piece_end": it["out"] + (b - a), "agent": agent, "spk": it["speaker"]})
    # the drawn looks' blocks: consecutive pieces of one speaker (and one style, agent or not) under 1 s apart
    blocks = []
    for r in drawn_runs:
        if not r["w"]:
            continue
        if blocks and blocks[-1][-1]["it"]["speaker"] == r["it"]["speaker"] and blocks[-1][-1]["agent"] == r["agent"] \
                and blocks[-1][-1]["hook"] == r["hook"] and r["w"][0]["os"] - blocks[-1][-1]["w"][-1]["oe"] <= 1.0:
            blocks[-1].append(r)
        else:
            blocks.append([r])
    for bl in blocks:
        W = []
        for ri, r in enumerate(bl):
            r_end = r["it"]["out"] + (r["b"] - r["a"])
            for x in r["w"]:
                W.append(dict(x, run=ri, run_end=r_end, run_start=r["it"]["out"]))
        hook_bl = bool(bl[0].get("hook"))
        for c in drawn_chunks(W, spec_speed(S), one_line=hook_bl):
            size = 104 if hook_bl else (118 if c[0]["os"] < 8.0 else 104)
            texts = [x["t"] for x in c]
            lines = [list(range(len(c)))] if hook_bl else (two_lines(texts, size) or two_lines(texts, size, CAP_MERGE_W) or [list(range(len(c)))])
            # 29 Oct (builder G, guest O's M1-animB 7.4 s: a 2-line Big group's ink starts at 1235, while the card state's
            # `answer` face is solved to keep its lower lip over the 104 px block's ink at 1262): over an `answer` piece
            # (or a crossfade into or out of one) a Big group stays on one line, else it is set at 104 like the rest
            lays_c = set()   # the layouts of every piece the group is on screen over (a run spans a card split's pieces)
            c_s, c_e = c[0]["os"] - 0.06, c[-1]["oe"] + 0.16
            for it_c in P["items"]:
                if it_c["kind"] != "card" and it_c["out"] < c_e and it_c["out"] + it_c["n"] / FPS > c_s:
                    lays_c |= {it_c.get("layout"), it_c.get("from"), it_c.get("to")}
            if size == 118 and len(lines) > 1 and "answer" in lays_c:
                size = 104
                lines = two_lines(texts, 104) or two_lines(texts, 104, CAP_MERGE_W) or lines
            g_s = max(c[0]["run_start"], c[0]["os"] - 0.06)
            g_e = min(c[-1]["oe"] + 0.16, c[-1]["run_end"] - 1.0 / FPS)
            if g_e - g_s < 0.12:
                g_e = g_s + 0.12
            agent = bl[0]["agent"]
            groups.append({"style": "Agent" if agent else "Big" if size == 118 else "Cap", "s": g_s, "e": g_e,
                           "w": [(x["t"], x["os"], x["oe"]) for x in c], "lines": lines, "piece_end": c[-1]["run_end"], "agent": agent,
                           "spk": bl[0]["it"]["speaker"], "hook": hook_bl})
    groups.sort(key=lambda g: g["s"])
    for i in range(len(groups) - 1):
        if groups[i + 1]["s"] < groups[i]["e"]:
            groups[i]["e"] = max(groups[i]["s"] + 0.12, groups[i + 1]["s"] - 0.01)
    # 29 Oct (builder G, guest U's M1 hook 'How do' 0.155 s, rows 94 and 183: 'How do you' is spoken in 0.24 s right
    # after the cut and 'How do you approach' is 19 px too wide for the hook's one line): a group under 0.3 s after the
    # speed is held up to CAP_HOLD (output s at 1.0x) longer when the next group is the same speaker's, follows within
    # 0.05 s and stays 0.3 s or longer itself; that group appears as much later (its first word is then at most about
    # 2 frames ahead of it). The DP above prices the same hold.
    sp_ = spec_speed(S)
    for i in range(len(groups) - 1):
        g, nx = groups[i], groups[i + 1]
        d = MIN_LINE_S * sp_ - (g["e"] - g["s"])
        if 0 < d <= CAP_HOLD and nx.get("spk") == g.get("spk") and bool(nx.get("hook")) == bool(g.get("hook")) \
                and nx["s"] - g["e"] <= 0.05 and (nx["e"] - nx["s"] - d) / sp_ >= MIN_LINE_S:
            g["e"] += d + 0.002
            nx["s"] += d + 0.002
    if not (S.get("_look") == "ig_native"):
        groups = fix_caption_groups(groups, spec_speed(S))   # (builder A, cause 3); ig_native merges its own lines
    return groups


NO_END = {"a", "an", "the", "to", "of", "and", "or", "in", "on", "is", "i", "but", "so", "that", "with", "for", "at", "my", "your", "our", "it's", "if"}


def fits(c, size, maxwords):
    # (builder A, cause 3: 'designer or / developers'): a chunk set on 2 lines fits only with 2 words or more on
    # each, so the chunker cuts a sentence where no line is left with a lone word
    ln = two_lines([x["t"] for x in c], size)
    return len(c) <= maxwords and ln is not None and (len(ln) < 2 or all(len(x) >= 2 for x in ln))


def chunk_sentence(sn, size, maxwords):
    """a sentence into caption chunks: clauses at commas packed greedily while they fit 2 lines; a clause too long is
    split at the most even point that does not end on a function word; never a 1-word chunk when the one before can take it."""
    clauses, cur = [], []
    for w in sn:
        cur.append(w)
        if w["t"].endswith((",", ";", ":")) and len(cur) >= 2:
            clauses.append(cur)
            cur = []
    if cur:
        clauses.append(cur)
    out, cur = [], []
    for cl in clauses:
        if cur and fits(cur + cl, size, maxwords):
            cur = cur + cl
            continue
        if cur:
            out.append(cur)
        cur = cl
    if cur:
        out.append(cur)
    final = []
    for c in out:
        final += split_even(c, size, maxwords)
    # a lone word folds into the chunk before it when that still fits
    fixed = []
    for c in final:
        if fixed and len(c) == 1 and fits(fixed[-1] + c, size, maxwords):
            fixed[-1] = fixed[-1] + c
        else:
            fixed.append(c)
    return fixed


def split_even(c, size, maxwords):
    if fits(c, size, maxwords) or len(c) == 1:
        return [c]
    n = 2
    while True:
        sz = -(-len(c) // n)
        cuts = list(range(sz, len(c), sz))
        # nudge each cut off a function word
        adj = []
        for k in cuts:
            kk = k
            for d in (0, 1, -1, 2, -2):
                j = k + d
                if 0 < j < len(c) and re.sub(r"[^a-z']", "", c[j - 1]["t"].lower()) not in NO_END:
                    kk = j
                    break
            adj.append(kk)
        adj = sorted(set(a for a in adj if 0 < a < len(c)))
        parts, prev = [], 0
        for k in adj + [len(c)]:
            if k > prev:
                parts.append(c[prev:k])
                prev = k
        if all(fits(p, size, maxwords) for p in parts) or sz == 1:
            return parts
        n += 1


def two_lines(texts, size, maxw=None):
    """word indexes per line, 1 or 2 balanced lines inside CAP_MAXW (or maxw), else None."""
    CAP_MAXW = maxw or globals()["CAP_MAXW"]  # noqa: N806
    if drawn_width(" ".join(texts), size) <= CAP_MAXW:
        return [list(range(len(texts)))]
    best = None
    for k in range(1, len(texts)):
        a, b = " ".join(texts[:k]), " ".join(texts[k:])
        wa, wb = drawn_width(a, size), drawn_width(b, size)
        if wa <= CAP_MAXW and wb <= CAP_MAXW:
            # (builder A, cause 3): a line of 1 word only when no split with 2 or more a line fits
            sc = abs(wa - wb) + (10000 if min(k, len(texts) - k) < 2 and len(texts) >= 4 else 0)
            if best is None or sc < best[0]:
                best = (sc, k)
    if best is None:
        return None
    k = best[1]
    return [list(range(k)), list(range(k, len(texts)))]


def fmt_t(t):
    t = max(0.0, t)
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


IG_LINE_CH = 22        # the caption sticker's line, characters (50 px inside x 150 to 930, clear of the button rail)
IG_MERGE_CH = 26       # a merge may stretch the line to 26 (builder A, cause 3)
MIN_LINE_S = 0.3       # no caption on screen under 0.3 s, after the speed
CAP_HOLD = 0.10        # 29 Oct (builder G): a drawn group may be held this much (s at 1.0x) into the next group's start
CAP_MERGE_W = 760      # a drawn caption line rebuilt to lose a lone word may stretch to 760 px (x 160 to 920)


def ig_chunks(groups, speed=1.0):
    """ig_native's caption sticker: the caption groups cut into phrase-length lines of at most 4 words (a comma or a
    sentence end closes a line of 2 or more), each word with its own output time, never across a group (so never
    across a cut). Returns [{s, e, w: [[text, s], ...]}] in output seconds.
    22:25 (builder A, cause 3: 'always' 0.17 s, 'say,' 0.07 s, 'breaches.' and 'privilege.' alone on round 1): then
    every line of 1 word and every line under 0.3 s (after the speed) is merged into the line before it in its group, or
    the one after when it is the first, within 26 characters; failing that, across the group's edge into the
    neighbouring line of the same speaker less than 1.5 s away (`fix_ig_lines`)."""
    lines = []
    for gi, g in enumerate(groups):
        ws = g["w"]
        cur, chunks = [], []
        for i, w in enumerate(ws):
            cur.append(i)
            nxt = ws[i + 1][0] if i + 1 < len(ws) else ""
            chars = len(" ".join(ws[k][0] for k in cur))
            # a line ends at 4 words, at a comma or sentence end once it has 2, or before it would pass 22 characters (the
            # 50 px line stays inside x 150 to 930, clear of the button rail: guest Q's F1 14:49 ran 'currently using that's been' into it)
            if len(cur) >= 4 or (len(cur) >= 2 and re.search(r"[,.?!;:]$", w[0])) or (nxt and chars + 1 + len(nxt) > IG_LINE_CH):
                chunks.append(cur)
                cur = []
        if cur:
            if chunks and len(cur) == 1 and len(chunks[-1]) < 5 and len(" ".join(ws[k][0] for k in chunks[-1] + cur)) <= IG_LINE_CH:
                chunks[-1] += cur
            else:
                chunks.append(cur)
        for ci, ch in enumerate(chunks):
            s0 = g["s"] if ci == 0 else ws[ch[0]][1]
            e0 = ws[chunks[ci + 1][0]][1] if ci + 1 < len(chunks) else g["e"]
            lines.append({"g": gi, "spk": g.get("spk"), "s": s0, "e": e0, "w": [[ws[k][0], (s0 if k == ch[0] else ws[k][1])] for k in ch]})
    lines = ig_lines_dp(groups, speed) or fix_ig_lines(lines, speed)
    return [{"s": round(ln["s"] / speed, 3), "e": round(ln["e"] / speed, 3), "w": [[t, round(ts / speed, 3)] for t, ts in ln["w"]]} for ln in lines]


def ig_lines_dp(groups, speed=1.0, gap_max=1.5):
    """22:40 (builder A, cause 3, after a greedy merge left guest O's F3 'ChatGPT?' alone once 'asking?' had gone forward):
    the caption sticker's lines laid out by a shortest path over each BLOCK of words (consecutive groups of one speaker
    under gap_max s apart). A line costs: 1000 for 1 word, 500 when on screen under 0.3 s after the speed, 1000 past 26
    characters or 5 words, 3 a character past 22, 4 for running across a group's edge (a sentence end or a pause),
    minus 2 for ending on punctuation, plus 1 a line and 1 per word under 4. Lines are dicts {g, spk, s, e, w: [[text, s], ...]}
    in 1.0x output seconds; a line's start is its first word's (the group's start for a group's first word) and its
    end is the next line's start inside its group, or the group's end."""
    if not groups:
        return []
    blocks, cur = [], [0]
    for gi in range(1, len(groups)):
        a, b = groups[gi - 1], groups[gi]
        if b.get("spk") == a.get("spk") and b["s"] - a["e"] <= gap_max:
            cur.append(gi)
        else:
            blocks.append(cur)
            cur = [gi]
    blocks.append(cur)
    out = []
    for bl in blocks:
        W = []      # (text, start, group index, first of its group, last of its group)
        for gi in bl:
            g = groups[gi]
            for k, w in enumerate(g["w"]):
                W.append((w[0], g["s"] if k == 0 else w[1], gi, k == 0, k == len(g["w"]) - 1))
        n = len(W)

        def span(i, j):   # words i..j-1 as one line: start, end
            st = W[i][1]
            if W[j - 1][4]:
                en = groups[W[j - 1][2]]["e"]
            else:
                en = W[j][1]
            return st, en

        def cost(i, j):
            nw = j - i
            txt = " ".join(W[k][0] for k in range(i, j))
            st, en = span(i, j)
            c = 0.0
            if nw < 2 and n >= 2:
                c += 1000
            if nw > 5 or len(txt) > IG_MERGE_CH:
                c += 1000
            if len(txt) > IG_LINE_CH:
                c += 3 * (len(txt) - IG_LINE_CH)
            if (en - st) / speed < MIN_LINE_S:
                c += 500
            c += 4 * sum(1 for k in range(i, j - 1) if W[k][4])
            if re.search(r"[,.?!;:]$", W[j - 1][0]):
                c -= 2
            c += 1.0 + 1.0 * max(0, 4 - nw)       # fewer, fuller lines (the round-1 chunker's 4 words a line)
            return c
        best = [0.0] + [math.inf] * n
        back = [0] * (n + 1)
        for j in range(1, n + 1):
            for i in range(max(0, j - 6), j):
                v = best[i] + cost(i, j)
                if v < best[j]:
                    best[j], back[j] = v, i
        cuts, j = [], n
        while j > 0:
            cuts.append((back[j], j))
            j = back[j]
        for i, j in reversed(cuts):
            st, en = span(i, j)
            out.append({"g": W[i][2], "spk": groups[W[i][2]].get("spk"), "s": st, "e": en,
                        "w": [[W[k][0], W[k][1]] for k in range(i, j)]})
    return out


def _chars(ws):
    return len(" ".join(t for t, *_ in ws))


def fix_ig_lines(lines, speed=1.0, line_ch=IG_LINE_CH, merge_ch=IG_MERGE_CH, gap_max=1.5):
    """merge each caption line of 1 word or under MIN_LINE_S (after speed) into a neighbour: the previous line of its
    group, else the next of its group, else across the group's edge (same speaker, under gap_max s apart), the merged
    line within merge_ch characters; the stretch rule is tried before a last resort of 32 (the page wraps such a line to
    2 rows, lifted). Lines are dicts {g, spk, s, e, w: [[text, s], ...]} in 1.0x output seconds."""
    bad = lambda ln: len(ln["w"]) < 2 or (ln["e"] - ln["s"]) / speed < MIN_LINE_S  # noqa: E731
    for limit in (merge_ch, 32):
        changed = True
        guard = 0
        while changed and guard < 400:
            changed = False
            guard += 1
            for i, ln in enumerate(lines):
                if not bad(ln):
                    continue
                opts = []
                for j in (i - 1, i + 1):
                    if not 0 <= j < len(lines):
                        continue
                    o = lines[j]
                    same = o["g"] == ln["g"]
                    gap = (ln["s"] - o["e"]) if j < i else (o["s"] - ln["e"])
                    if not same and (o.get("spk") != ln.get("spk") or gap > gap_max):
                        continue
                    ch = _chars(o["w"] + ln["w"])
                    if ch > limit:
                        continue
                    opts.append((0 if same else 1, 0 if j < i else 1, ch, j))
                if not opts:
                    continue
                _, _, _, j = min(opts)
                a, b = (lines[j], ln) if j < i else (ln, lines[j])
                merged = {"g": a["g"], "spk": a.get("spk"), "s": a["s"], "e": b["e"], "w": a["w"] + b["w"]}
                k0 = min(i, j)
                lines = lines[:k0] + [merged] + lines[k0 + 2:]
                changed = True
                break
    return lines


def caption_line_faults(groups, ig_caps=None, speed=1.0):
    """the caption lines a viewer would see as 1 word or for under 0.3 s: the ig sticker lines when given, else each
    drawn group (shown as a block, its lines read from `lines`)"""
    bad = []
    if ig_caps is not None:
        for c in ig_caps:
            d = c["e"] - c["s"]
            if len(c["w"]) < 2 or d < MIN_LINE_S - 0.005:
                bad.append({"s": c["s"], "dur": round(d, 3), "text": " ".join(w[0] for w in c["w"])})
        return bad
    def lone_ok(gi, idx):
        """29 Oct (builder H, guest U's M1: row 235's 12-letter pass missed 'accusations,' at 11 letters): a word alone on
        its line passes only when NO neighbour word (the word before and after it in the group, or across the group's edge
        into the same speaker's group within 1 s) can share its line at the widest the caption layout allows (CAP_MERGE_W,
        measured with drawn_width, the layout's own measure, at the group's size); anything else still fails"""
        g = groups[gi]
        texts = [w[0] for w in g["w"]]
        size = 118 if g.get("style") == "Big" else 104
        word = texts[idx]
        pairs = []
        if idx > 0:
            pairs.append(texts[idx - 1] + " " + word)
        elif gi > 0 and groups[gi - 1].get("spk") == g.get("spk") and g["s"] - groups[gi - 1]["e"] <= 1.0 and groups[gi - 1]["w"]:
            pairs.append(groups[gi - 1]["w"][-1][0] + " " + word)
        if idx < len(texts) - 1:
            pairs.append(word + " " + texts[idx + 1])
        elif gi + 1 < len(groups) and groups[gi + 1].get("spk") == g.get("spk") and groups[gi + 1]["s"] - g["e"] <= 1.0 and groups[gi + 1]["w"]:
            pairs.append(word + " " + groups[gi + 1]["w"][0][0])
        return bool(pairs) and all(drawn_width(pr, size) > CAP_MERGE_W for pr in pairs)

    for gi, g in enumerate(groups):
        d = (g["e"] - g["s"]) / speed
        texts = [w[0] for w in g["w"]]
        one = [" ".join(texts[i] for i in ln) for ln in g["lines"] if len(ln) < 2 and not (ln and lone_ok(gi, ln[0]))]
        if len(texts) < 2 or d < MIN_LINE_S - 0.005 or one:
            bad.append({"s": round(g["s"] / speed, 3), "dur": round(d, 3), "text": " / ".join(" ".join(texts[i] for i in ln) for ln in g["lines"])})
    return bad


def fix_caption_groups(groups, speed=1.0):
    """the drawn looks' libass groups: a group of 1 word, or shown under 0.3 s after the speed, joins the group before it
    (else the one after) of the same speaker less than 1.5 s away when the words still fit 2 lines at the larger of
    the 2 sizes (8 words at most); the merged group is re-split into balanced lines (2 words or more a line where any
    split allows it) and runs from the first group's start to the second's end"""
    hard = lambda g: len(g["w"]) < 2 or (g["e"] - g["s"]) / speed < MIN_LINE_S  # noqa: E731
    lone = lambda g: any(len(ln) < 2 for ln in g["lines"])  # noqa: E731
    # the size and width ladder a re-split or a merge may use: the group's own size in the column, then 104 px (a Big
    # group of the first 8 s steps down), then a line stretched to 760 px (x 160 to 920), as ig's 22 stretch to 26
    ladder = lambda size: [(size, CAP_MAXW), (104, CAP_MAXW), (size, CAP_MERGE_W), (104, CAP_MERGE_W)]  # noqa: E731

    def resplit(texts, size, need_two=True):
        for sz, mw in ladder(size):
            ln = two_lines(texts, sz, mw)
            if ln is not None and (not need_two or all(len(x) >= 2 for x in ln) or len(texts) < 2):
                return ln, sz
        return None, size
    # a group with a lone-word line that re-splits on its own (a smaller size or the wider line) is fixed in place
    for gi, g in enumerate(groups):
        if len(g["w"]) >= 2 and lone(g) and not g.get("hook"):
            ln, sz = resplit([w[0] for w in g["w"]], 118 if g["style"] == "Big" else 104)
            if ln is not None and all(len(x) >= 2 for x in ln):
                groups[gi] = dict(g, lines=ln, style=("Cap" if sz == 104 and g["style"] == "Big" else g["style"]))
    changed, guard = True, 0
    tried = set()
    while changed and guard < 400:
        changed, guard = False, guard + 1
        for i, g in enumerate(groups):
            if not (hard(g) or lone(g)) or (not hard(g) and id(g) in tried):
                continue
            opts = []
            for j in (i - 1, i + 1):
                if not 0 <= j < len(groups):
                    continue
                o = groups[j]
                if o.get("spk") != g.get("spk") or bool(o.get("agent")) != bool(g.get("agent")) or bool(g.get("hook")) != bool(o.get("hook")):
                    continue
                gap = (g["s"] - o["e"]) if j < i else (o["s"] - g["e"])
                if gap > 1.5:
                    continue
                a, b = (o, g) if j < i else (g, o)
                texts = [w[0] for w in a["w"] + b["w"]]
                if g.get("hook"):
                    # 29 Oct (builder G, guest U's M1 'How do' 0.155 s, rows 94 and 183): the stacked hook's caption is ONE line
                    # centred in the seam (hook_caption_y), so 2 hook groups of one speaker merge only when the words still
                    # fit one 104 px line (stretched to 760 px at most, 6 words); a hook group never joins an answer group
                    if len(texts) > 6 or drawn_width(" ".join(texts), 104) > CAP_MERGE_W:
                        continue
                    opts.append((0 if j < i else 1, j, [list(range(len(texts)))], 104))
                    continue
                size = 118 if "Big" in (a["style"], b["style"]) else 104
                lines, size = resplit(texts, size, need_two=not hard(g))
                if lines is None or len(texts) > 8:
                    continue
                if not hard(g) and any(len(ln) < 2 for ln in lines):
                    continue          # a merge for a lone-word LINE only when it removes it
                opts.append((0 if j < i else 1, j, lines, size))
            if not opts:
                tried.add(id(g))
                continue
            _, j, lines, size = min(opts, key=lambda x: x[0])
            a, b = (groups[j], g) if j < i else (g, groups[j])
            merged = dict(a, w=a["w"] + b["w"], lines=lines, s=a["s"], e=b["e"], style="Big" if size == 118 else "Cap",
                          piece_end=max(a.get("piece_end", 0), b.get("piece_end", 0)))
            k0 = min(i, j)
            groups = groups[:k0] + [merged] + groups[k0 + 2:]
            changed = True
            break
    return groups


def ass_text(groups, speed=1.0, boxes=False):
    head = ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 2\nScaledBorderAndShadow: yes\n\n[V4+ Styles]\n"
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
            f"{STYLE_CAP}\n{STYLE_BIG}\n{STYLE_AGENT}\n{STYLE_CHIP}\n{STYLE_CAP_BOX}\n{STYLE_BIG_BOX}\n{STYLE_AGENT_BOX}\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
    lines = []
    for gi, g in enumerate(groups):
        texts = [w[0] for w in g["w"]]
        n = len(texts)
        agent = g.get("agent")
        # 29 Oct (builder H): the box layer, one event for the group's whole time, the same lines and position
        box_body = "\\N".join(" ".join(texts[i].replace("{", "").replace("}", "") for i in line) for line in g["lines"])
        box_pos = f"\\an5\\pos(540,{int(g['pos_y'])})" if g.get("pos_y") else ""
        if boxes and g["e"] / speed - g["s"] / speed >= 0.01:   # the tutorial look (tutorial_look.py) styles its own box
            lines.append(f"Dialogue: 0,{fmt_t(g['s'] / speed)},{fmt_t(g['e'] / speed)},{g['style']}Box,b{gi:04d},0,0,0,,{{{box_pos}\\ybord0}}{box_body}")
        if agent:
            # the chip above the block names the voice: the words are the AI agent's, not the person on screen
            lines.append(f"Dialogue: 0,{fmt_t(g['s'] / speed)},{fmt_t(g['e'] / speed)},Chip,c{gi:04d},0,0,0,,{{\\an7\\pos(180,962)}}AI AGENT")
        # one Dialogue per current word: the word in the accent, the rest white (the Agent style inverts that), the line break fixed
        hi, lo = (WHITE_ASS, ACCENT_ASS) if agent else (ACCENT_ASS, WHITE_ASS)
        for k in range(n):
            s = g["s"] if k == 0 else g["w"][k][1]
            e = g["w"][k + 1][1] if k + 1 < n else g["e"]
            s, e = s / speed, e / speed
            if e - s < 0.01:
                continue
            parts = []
            for li, line in enumerate(g["lines"]):
                segs = []
                for idx in line:
                    t = texts[idx].replace("{", "").replace("}", "")
                    segs.append(f"{{\\1c{hi}}}{t}{{\\1c{lo}}}" if idx == k else t)
                parts.append(" ".join(segs))
            body = "\\N".join(parts)
            if g.get("pos_y"):   # the drawn hook's caption, centred in the seam between the 2 faces
                body = f"{{\\an5\\pos(540,{int(g['pos_y'])})}}" + body
            lines.append(f"Dialogue: 1,{fmt_t(s)},{fmt_t(e)},{g['style']},g{gi:04d},0,0,0,,{body}")
    return head + "\n".join(lines) + "\n"


# ---------------------------------------------------------------- video pieces
_INFO = {}


def info(path):
    if path not in _INFO:
        _INFO[path] = probe(path)
    return _INFO[path]


def venc(final=False):
    mbps = 6 if final else 8
    return ["-c:v", "h264_videotoolbox", "-allow_sw", "1", "-profile:v", "high", "-b:v", f"{mbps}M", "-maxrate", f"{int(mbps * 1.5)}M",
            "-bufsize", f"{mbps * 2}M", "-pix_fmt", "yuv420p", "-color_range", "tv", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709"]


def panel_chain(idx, p, inf, face, panel, ground, mask_on=False):
    """ffmpeg filter text: input idx -> [c{idx}] the panel crop scaled to the visible panel, [x{idx}] the crop's lower part
    mirrored and blurred, scaled to fill from the panel's foot to the frame's foot (the faded extension)."""
    g = crop_geo(inf, face["box"] if isinstance(face, dict) else face, panel, p.get("crop"), face.get("low") if isinstance(face, dict) else None,
                 face.get("high") if isinstance(face, dict) else None, bool(p.get("crop_hard")))
    cw, ch, cx, cy, vis_h = g["cw"], g["ch_vis"], g["x"], g["y_vis"], g["vis_h"]
    top_h = g.get("top_h") or 0
    main_h = vis_h - top_h
    rng = "pc" if inf["range"] == "pc" or inf["pix"].startswith("yuvj") else "tv"
    base = f"[{idx}:v]setpts=PTS-STARTPTS,fps={FPS},scale=in_range={rng}:out_range=tv,format=yuv420p"
    mk = p.get("mask") if mask_on else None
    if mk:
        # a region of the source blurred away for the pieces inside mask.between: the long form's burned-in caption of
        # the AI agent's words on tutorial-1 (845-945 s) sits where the crop keeps the phone in frame (27 Oct)
        mx, my, mw, mh = [int(v) for v in mk["box"]]
        base += f",split=2[m{idx}a][m{idx}b];[m{idx}b]crop={mw}:{mh}:{mx}:{my},boxblur=30:3[m{idx}c];[m{idx}a][m{idx}c]overlay={mx}:{my}"
    if p.get("medallion"):
        mg = medallion_geo(p, face["box"] if isinstance(face, dict) else face, panel)
        bx, by, bw, bh = mg["box"]
        mw, mh = mg["mw"], mg["mh"]
        # (tutorial-3's M1 and M2 on the light looks: white captions on the paper ground under the medallion, unreadable):
        # from the panel's top to the frame's foot the tile itself, stretched, blurred and darkened, under the medallion
        fh_all = VH - panel["y"]
        return (f"{base},split=3[s{idx}][b{idx}][e{idx}];[b{idx}]crop={bw}:{bh}:{bx}:{by},scale={VW}:{fh_all}:flags=bilinear,boxblur=40:3,"
                f"eq=brightness=-0.22,setsar=1[bb{idx}];[s{idx}]crop={bw}:{bh}:{bx}:{by},scale={mw}:{mh}:flags=lanczos,"
                f"drawbox=0:0:iw:ih:color=0x{ACCENT_HEX}:t=6,setsar=1[mm{idx}];[bb{idx}][mm{idx}]overlay={(VW - mw) // 2}:0[c{idx}];"
                f"[e{idx}]crop=2:2:0:0,scale={VW}:2,drawbox=0:0:iw:ih:color=0x{ground}:t=fill,setsar=1[x{idx}]", fh_all, 2)
    ext_h = max(2, VH - panel["y"] - vis_h)
    tail = max(2, int(round(ch * 0.12)) // 2 * 2)
    xb = min(40, max(0, ext_h // 4 - 1))   # (guest C's F2, a 128 px extension): the chroma radius must stay under a quarter of the height at every size   # chroma is half height: radius within a quarter (guest E's F1 ig, 15:24)   # a bounded ig_native panel leaves a 2 px extension; boxblur's radius must fit it
    if g.get("ground_pillar") and panel.get("bounded"):
        # 29 Oct (builder G, guest Q's after-M31 r3: a flat black band 0 to 520 and 25 px black pillars beside the host in the
        # question; guest S's F3: the guest boxed in black; the conductor: "no black band or pillars ever: the blurred
        # extension"): on the Instagram panels the narrower crop sits over its own crop stretched to the whole panel,
        # blurred and dimmed (the reel's treatment), which fills the sides and the run-over above the source alike
        ow = g["out_w"]
        return (f"{base},split=3[s{idx}][p{idx}][e{idx}];[p{idx}]crop={cw}:{ch}:{cx}:{cy},scale={VW}:{vis_h}:flags=bilinear,boxblur=30:3,eq=brightness=-0.12,setsar=1[pb{idx}];"
                f"[s{idx}]crop={cw}:{ch}:{cx}:{cy},scale={ow}:{main_h}:flags=lanczos,setsar=1[pf{idx}];[pb{idx}][pf{idx}]overlay={(VW - ow) // 2}:{top_h}[c{idx}];"
                f"[e{idx}]crop={cw}:{tail}:{cx}:{cy + ch - tail},scale={VW}:{ext_h}:flags=bilinear,boxblur={xb}:{3 if xb >= 40 else 1},setsar=1[x{idx}]",
                vis_h, ext_h)
    if g.get("ground_pillar"):
        # (builder A): the crop at its own width centred on the panel over the look's GROUND (never its own blur),
        # the run-over above the source's top padded in the same ground; the extension under it as for any panel
        ow = g["out_w"]
        return (f"{base},split=2[s{idx}][e{idx}];[s{idx}]crop={cw}:{ch}:{cx}:{cy},scale={ow}:{main_h}:flags=lanczos,setsar=1,"
                f"pad={VW}:{vis_h}:{(VW - ow) // 2}:{top_h}:color=0x{ground}[c{idx}];"
                f"[e{idx}]crop={cw}:{tail}:{cx}:{cy + ch - tail},scale={VW}:{ext_h}:flags=bilinear,boxblur={xb}:{3 if xb >= 40 else 1},setsar=1[x{idx}]",
                vis_h, ext_h)
    if g["pillar"]:
        # the crop at its own width centred on the panel over a blurred, stretched copy of itself
        ow = g["out_w"]
        return (f"{base},split=3[s{idx}][p{idx}][e{idx}];[p{idx}]crop={cw}:{ch}:{cx}:{cy},scale={VW}:{vis_h}:flags=bilinear,boxblur=30:3,setsar=1[pb{idx}];"
                f"[s{idx}]crop={cw}:{ch}:{cx}:{cy},scale={ow}:{vis_h}:flags=lanczos,setsar=1[pf{idx}];[pb{idx}][pf{idx}]overlay={(VW - ow) // 2}:0[c{idx}];"
                f"[e{idx}]crop={cw}:{tail}:{cx}:{cy + ch - tail},scale={VW}:{ext_h}:flags=bilinear,boxblur={xb}:{3 if xb >= 40 else 1},setsar=1[x{idx}]",
                vis_h, ext_h)
    if top_h >= 4 and panel.get("bounded"):
        # 28 Oct (polish, guest Q's F1 proof: 315 px of plain black above the co-host's head in the question hook, 75 above
        # the guest's in the answer; Round-3: "no long black empty band ever"): on the Instagram panels the run-over above
        # the source is the crop's own top rows mirrored, blurred and dimmed (the reel's own treatment behind a sticker),
        # never a plain band; the drawn looks keep the ground (builder A, cause 1)
        ttop = max(2, int(round(min(ch, max(16, top_h / g["k"])))) // 2 * 2)
        xt = min(40, max(1, top_h // 4 - 1))
        return (f"{base},split=3[s{idx}][t{idx}][e{idx}];[s{idx}]crop={cw}:{ch}:{cx}:{cy},scale={VW}:{main_h}:flags=lanczos,setsar=1[sm{idx}];"
                f"[t{idx}]crop={cw}:{ttop}:{cx}:{cy},vflip,scale={VW}:{top_h}:flags=bilinear,boxblur={xt}:{3 if xt >= 40 else 1},eq=brightness=-0.12,setsar=1[tb{idx}];"
                f"[tb{idx}][sm{idx}]vstack=inputs=2[c{idx}];"
                f"[e{idx}]crop={cw}:{tail}:{cx}:{cy + ch - tail},scale={VW}:{ext_h}:flags=bilinear,boxblur={xb}:{3 if xb >= 40 else 1},setsar=1[x{idx}]",
                vis_h, ext_h)
    if top_h >= 4:
        # the run-over above the source's top: 27 Oct (builder A, cause 1: guest C's F3 0 to 336, guest O's F2 0 to 315 of
        # mirrored blur) the look's plain GROUND colour, padded above the crop, never blur
        return (f"{base},split=2[s{idx}][e{idx}];[s{idx}]crop={cw}:{ch}:{cx}:{cy},scale={VW}:{main_h}:flags=lanczos,setsar=1,"
                f"pad={VW}:{vis_h}:0:{top_h}:color=0x{ground}[c{idx}];"
                f"[e{idx}]crop={cw}:{tail}:{cx}:{cy + ch - tail},scale={VW}:{ext_h}:flags=bilinear,boxblur={xb}:{3 if xb >= 40 else 1},setsar=1[x{idx}]",
                vis_h, ext_h)
    return (f"{base},split=2[s{idx}][e{idx}];[s{idx}]crop={cw}:{ch}:{cx}:{cy},scale={VW}:{vis_h}:flags=lanczos,setsar=1[c{idx}];"
            f"[e{idx}]crop={cw}:{tail}:{cx}:{cy + ch - tail},scale={VW}:{ext_h}:flags=bilinear,boxblur={xb}:{3 if xb >= 40 else 1},setsar=1[x{idx}]",
            vis_h, ext_h)


def layout_segments(p, src_a, n):
    """14:30 (guest K's Riverside 'magic' export: one composed file whose layout switches between the guest solo, the host solo
    and a split): a person with `layouts` [[t0, t1, crop_name | null], ...] (source seconds, measured from the frames) is cut
    from `crops[crop_name]` frame by frame; returns [(source start, frames, crop_name)] for n frames from src_a. A frame
    where the person is not on screen (null) takes the nearest named layout (logged by the caller)."""
    def at(t):
        for t0, t1, nm in p["layouts"]:
            if t0 <= t < t1:
                return nm
        return None
    names = [at(src_a + (j + 0.5) / FPS) for j in range(n)]
    known = [x for x in names if x]
    if not known:
        raise NoFaceBox(f"no layout with this person on screen from {src_a:.2f} s")
    last = None
    for j in range(n):
        if names[j]:
            last = names[j]
        elif last:
            names[j] = last
    first = next(x for x in names if x)
    names = [x or first for x in names]
    segs = []
    for j, nm in enumerate(names):
        if segs and segs[-1][2] == nm:
            segs[-1][1] += 1
        else:
            segs.append([src_a + j / FPS, 1, nm])
    return [tuple(x) for x in segs]


def layout_faces(role, p, pcs, work):
    """one face box per named crop of a `layouts` person, measured on the spans of that layout inside the pieces"""
    off = float(p.get("offset") or 0.0)
    spans = [(a + off, b + off) for a, b in pcs] + [(float(t), float(t) + 3.0) for _, t in (p.get("listen_at") or [])]
    by, secs = {}, {}
    for t0, t1, nm in p["layouts"]:
        if not nm:
            continue
        for a, b in spans:
            lo, hi = max(a, t0), min(b, t1)
            if hi - lo > 0.2:
                by.setdefault(nm, []).append((lo - off, hi - off))
                secs[nm] = secs.get(nm, 0) + hi - lo
    out = {}
    for nm, sp in by.items():
        # (guest K's F3: Haar took an eye for the face on the soft upscaled split tile, 154 px, and a 120 px box for
        # the guest solo): `layout_face` {crop name: [x, y, w, h]} measured by hand on a gridded frame wins over Haar
        out[nm] = face_box(role, {**p, "crop": p["crops"][nm], "face": (p.get("layout_face") or {}).get(nm),
                                  "face_region": (p.get("face_regions") or {}).get(nm, p.get("face_region"))}, sp, work, f"{role}-{nm}")
    main = max(secs, key=secs.get)
    return {**out[main], "by": out, "method": f"per layout ({', '.join(sorted(out))})"}


def render_piece(S, P, it, faces, work, ground_hex):
    """one piece of timeline as a 1080x1920 video (ground + face panels + extension), 30 fps, exactly n frames."""
    rec = {"v": 10, "solver": SOLVE_V, "a": round(it["a"], 4), "n": it["n"], "layout": it["layout"], "geom": P["layout"].get(it["layout"]), "spk": it["speaker"], "faces": faces, "ground": ground_hex,
           "files": {k: v["file"] for k, v in P["people"].items()}, "crops": {k: v.get("crop") for k, v in P["people"].items()}, "text": it.get("text"),
           "masks": {k: v.get("mask") for k, v in P["people"].items()}}
    # the medallion and layout keys enter the cache key only where a spec uses them (every other piece keeps its cache)
    if any(v.get("medallion") for v in P["people"].values()):
        rec["meds"] = {k: v.get("medallion") for k, v in P["people"].items()}
    if any(v.get("layouts") for v in P["people"].values()):
        rec["lays"] = {k: [v.get("layouts"), v.get("listen_at")] for k, v in P["people"].items()}
    if it["layout"] == "xfade":
        rec["xf"] = [it.get("from"), it.get("to"), it.get("src_a"), it.get("src_b")]
        rec["geom"] = [P["layout"][it["from"]], P["layout"][it["to"]]]
    out = work / f"piece-{key_of(rec)}.mp4"
    if out.exists() and abs(duration(out) - it["n"] / FPS) < 0.08:
        return out
    n, d = it["n"], it["n"] / FPS
    inputs, fc = [], []
    if it["kind"] == "card":
        png = card_png(S, it["text"], work, P["layout"]["answer"]["top_band_h"])
        inputs += ["-loop", "1", "-framerate", str(FPS), "-t", f"{d + 0.5:.3f}", "-i", str(png)]
        fc.append(f"[0:v]scale=out_range=tv:out_color_matrix=bt709,format=yuv420p,trim=end_frame={n},setpts=N/({FPS}*TB)[v]")
    elif it["layout"] == "xfade":
        # (builder A, cause 4): the crossfade between the full-face framing and the card framing: each side is
        # its own single-panel composite from its own tape position, blended frame by frame (frame i takes (i+1)/(n+1)
        # of the incoming side), so neither end frame repeats the pieces around it
        sides = []
        for si, (lay_name, (role, src_t)) in enumerate(((it["from"], it["src_a"]), (it["to"], it["src_b"]))):
            panel = P["layout"][lay_name]["guest"]
            p = P["people"][role]
            inf = info(p["file"])
            off = float(p.get("offset") or 0.0)
            inputs += ["-ss", f"{max(0.0, float(src_t) + off):.4f}", "-t", f"{d + 0.6:.3f}", "-i", p["file"]]
            chain, vis_h, ext_h = panel_chain(si, p, inf, faces[role], panel, ground_hex)
            fc.append(f"color=c=0x{ground_hex}:s={VW}x{VH}:r={FPS}:d={d + 0.5:.3f},format=yuv420p[bg{si}]")
            fc.append(chain)
            fc.append(f"[bg{si}][x{si}]overlay=0:{panel['y'] + vis_h}[y{si}]")
            fc.append(f"[y{si}][c{si}]overlay=0:{panel['y']}:shortest=1,trim=end_frame={n},setpts=N/({FPS}*TB),format=yuv420p[sd{si}]")
            sides.append(f"[sd{si}]")
        fc.append(f"{sides[0]}{sides[1]}blend=all_expr='A+(B-A)*(N+1)/{n + 1}',format=yuv420p[v]")
    else:
        lay = P["layout"][it["layout"]]
        roles = panel_roles(it, lay, P["people"])
        fc.append(f"color=c=0x{ground_hex}:s={VW}x{VH}:r={FPS}:d={d + 0.5:.3f},format=yuv420p[bg]")
        cur = "bg"
        pre = 0.0
        nin = 0
        for idx, (role, panel) in enumerate(roles):
            p = P["people"][role]
            inf = info(p["file"])
            off = float(p.get("offset") or 0.0)
            if p.get("layouts"):
                # a layout-switching composed file: the panel is cut per layout run and the runs are joined (video only)
                src_a = it["a"] + off
                if it["layout"] == "hook" and role != it["speaker"]:
                    for ha, lt in (p.get("listen_at") or []):
                        if abs(float(ha) - it["a"]) < 0.3:
                            src_a = float(lt)   # the listener from a stretch where this person is on screen
                qs = []
                for sa, k, nm in layout_segments(p, src_a, n):
                    inputs += ["-ss", f"{max(0.0, sa):.4f}", "-t", f"{k / FPS + 0.6:.3f}", "-i", p["file"]]
                    chain, vis_h, ext_h = panel_chain(nin, {**p, "crop": p["crops"][nm]}, inf, faces[role]["by"][nm], panel, ground_hex)
                    fc.append(chain)
                    fc.append(f"color=c=0x{ground_hex}:s={VW}x{VH - panel['y']}:r={FPS}:d={k / FPS + 0.5:.3f},format=yuv420p[g{nin}];"
                              f"[g{nin}][x{nin}]overlay=0:{vis_h}[h{nin}];[h{nin}][c{nin}]overlay=0:0,trim=end_frame={k},setpts=PTS-STARTPTS[q{nin}]")
                    qs.append(f"[q{nin}]")
                    nin += 1
                fc.append(f"{''.join(qs)}concat=n={len(qs)}:v=1:a=0[l{idx}]")
                fc.append(f"[{cur}][l{idx}]overlay=0:{panel['y']}{':shortest=1' if idx == 0 else ''}[w{idx}]")
                cur = f"w{idx}"
                continue
            idx_in, idx = idx, nin
            nin += 1
            inputs += ["-ss", f"{max(0.0, it['a'] + off):.4f}", "-t", f"{d + 0.6:.3f}", "-i", p["file"]]
            mk = p.get("mask")
            mask_on = bool(mk and mk.get("between") and it["a"] < float(mk["between"][1]) and it["b"] > float(mk["between"][0]))
            chain, vis_h, ext_h = panel_chain(idx, p, inf, faces[role], panel, ground_hex, mask_on)
            fc.append(chain)
            fc.append(f"[{cur}][x{idx}]overlay=0:{panel['y'] + vis_h}[y{idx}]")
            fc.append(f"[y{idx}][c{idx}]overlay=0:{panel['y']}{':shortest=1' if idx_in == 0 else ''}[w{idx}]")
            cur = f"w{idx}"
        fc.append(f"[{cur}]trim=end_frame={n},setpts=N/({FPS}*TB),format=yuv420p[v]")
    tmp = str(out) + ".part.mp4"
    run([FF, "-y", "-v", "error"] + inputs + ["-filter_complex", ";".join(fc), "-map", "[v]", "-frames:v", str(n), "-r", str(FPS)] + venc() + ["-an", tmp],
        timeout=min(3600, 600 + 30 * d), label=f"piece at {it['a']:.2f}")
    os.replace(tmp, out)
    return out


def card_png(S, text, work, band_top=640):
    """a black assertion card: its own stretch of timeline, the line in DM Serif Display centred in the panel under the
    title band (27 Oct: centred on the whole frame it was cut by the band on every 2-line card)."""
    out = work / f"card-{key_of([text, band_top, 2])}.png"
    if out.exists():
        return out
    img = Image.new("RGB", (VW, VH), (10, 10, 10))
    d = ImageDraw.Draw(img)
    size = 120
    while size > 60:
        f = ImageFont.truetype(str(FONTDIR / "DMSerifDisplay-Regular.ttf"), size)
        words = text.split()
        lines, cur = [], []
        for w in words:
            if d.textlength(" ".join(cur + [w]), font=f) > 940 and cur:
                lines.append(" ".join(cur))
                cur = [w]
            else:
                cur.append(w)
        lines.append(" ".join(cur))
        if len(lines) <= 3:
            break
        size -= 8
    lh = int(size * 1.1)
    y = (band_top + SAFE_BOTTOM) // 2 - lh * len(lines) // 2
    for ln in lines:
        d.text((540, y), ln, font=f, fill=(255, 255, 255), anchor="ma")
        y += lh
    img.save(out)
    return out


def concat_pieces(paths, work, tag):
    out = work / f"cut-{tag}.mp4"
    lst = work / f"cut-{tag}.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in paths))
    rec = key_of([str(p) for p in paths])
    if out.exists() and (work / f"cut-{tag}.key").exists() and (work / f"cut-{tag}.key").read_text() == rec:
        return out
    tmp = str(out) + ".part.mp4"
    run([FF, "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", tmp], timeout=600, label="concat")
    os.replace(tmp, out)
    (work / f"cut-{tag}.key").write_text(rec)
    return out


# ---------------------------------------------------------------- audio
# 28 Oct (polish, Round-3 ruling "every short gets a noise and echo clean-up pass"; the creator's words on E, H and J: "remove the
# background noise", "clean up the background noise", "you should clean up the echo"): afftdn tracks the noise floor
# (tn=1, nr 18 dB), a gentle deesser (i 0.25) tames the hiss the denoise leaves on sibilants, and a mild downward
# expander (agate ratio 1.6, release 160 ms) lowers the room tail between words, which is the echo a one-filter chain
# can reach; arnndn is NOT used: no .rnnn model was on the build machine (find / -name "*.rnnn": none). LUFS and true peak are
# measured after it as before (audio_take pass 3). AUDIO_V keys every cached piece so the old chain is never reused.
AUDIO_V = 8   # 29 Oct row 190: pieces read back, fallback chains; row 207: the harshness pass; 21:30 (builder H): the band guard
AUDIO_CHAIN = ("aresample=48000,adeclip,highpass=f=120,lowshelf=f=220:g=-5,afftdn=nr=18:nf=-42:tn=1,"
               "deesser=i=0.4:m=0.5:f=0.45:s=o,"
               "adynamicequalizer=dfrequency=5500:dqfactor=1.2:tfrequency=5500:tqfactor=1.2:attack=1:release=80:ratio=2.5:range=8:mode=cutabove:auto=adaptive,"
               "agate=threshold=0.015:ratio=1.6:attack=8:release=160:knee=6")
# 29 Oct (row 207, the creator: high peaks in guest C's voice, a little sharp on the ear; clean up the audio in any
# sharp places): a stronger de-esser and a dynamic cut above threshold around 5.5 kHz (3 to 8 kHz, at most
# 8 dB, adaptive threshold) on every piece, and SHAPE (a fast soft compressor on transients, then the true-peak limiter) on
# the joined take in pass 3, its gain found through the shape so the take still lands at -14 LUFS. Measured on guest C's F2
# loudest 22 s (1988.69 and 1837.51 pieces, at 1.25x and -14 LUFS): 3 to 8 kHz windows over -12 dBFS 70 -> 33, the 3 to 8 kHz
# peak -1.8 -> -5.1 dBFS, 50 ms windows over -3 dBFS 119 -> 0, the loudest 2 s' 3 to 8 kHz balance -20.4 -> -21.1 dB (not dulled)
SHAPE = ("acompressor=threshold=-18dB:ratio=3:attack=0.5:release=60:knee=8,"
         # (row 218): the 3 to 8 kHz band alone through a fast compressor, so a sharp onset (guest C's F2 'Just' at 8.75 s,
         # a 60 ms all-treble burst at -3.8 dBFS) is held without dulling the rest: band peak -3.8 -> -9.6 dBFS, the speech's
         # 3 to 8 kHz balance -14.9 -> -16.1 dB (a stronger chain tried at 18:00 took it to -20.7 and -24.9: dull, rejected)
         "acrossover=split=3000 8000:order=8th[lo][mid][hi];[mid]acompressor=threshold=-16dB:ratio=4:attack=0.1:release=40:knee=4[midc];"
         "[lo][midc][hi]amix=inputs=3:normalize=0")
# 29 Oct (row 190): on guest X's clipped single-camera phone file the chain above measured +12.2 LUFS before
# loudnorm (a filter ran away on the clipped peaks adeclip rebuilds above 1.0), so loudnorm refused measured_I and 3 renders
# died ('Result too large'). Each piece is now read back and, when it is not finite or peaks over +6 dBFS, rebuilt down this
# list (the de-esser out first, then the gate), and the chain that held is logged; the source never reaches loudnorm hot.
AUDIO_FALLBACKS = (
    "aresample=48000,adeclip,highpass=f=120,lowshelf=f=220:g=-5,afftdn=nr=18:nf=-42:tn=1,agate=threshold=0.015:ratio=1.6:attack=8:release=160:knee=6,alimiter=limit=0.95:level=false",
    "aresample=48000,highpass=f=120,lowshelf=f=220:g=-5,afftdn=nr=18:nf=-42,alimiter=limit=0.95:level=false",
)


# 29 Oct (builder H, guest O's M1-animB r3: her voice dulled, the loudest 2 s' 3 to 8 kHz balance -23.4 dB against
# her own source's -14.0 on a quiet, hissy Zoom 360p rail, where afftdn nr 18 and the de-esser ate her consonants): the band
# guard in audio_take, per speaker on the joined take (a per-piece test was tried first and lightened guest C's F3 and M1, whose
# de-essed pieces read -23 alone while their takes read -16 to -19.5: 89 band windows over -12 came back, rejected)
BAND_GUARD_DB = 6.0
BAND_GUARD_FLOOR = -20.0
BAND_GUARD_QUIET = -12.0
_DYN = "adynamicequalizer=dfrequency=5500:dqfactor=1.2:tfrequency=5500:tqfactor=1.2:attack=1:release=80:ratio=2.5:range=8:mode=cutabove:auto=adaptive,"
_L1 = AUDIO_CHAIN.replace("afftdn=nr=18:nf=-42:tn=1", "afftdn=nr=10:nf=-42:tn=1")
_L2 = _L1.replace("deesser=i=0.4:m=0.5:f=0.45:s=o,", "")
AUDIO_LIGHTER = (
    _L1,                                                                  # 1: the noise pass lighter
    _L2,                                                                  # 2: and the de-esser out
    _L2.replace(_DYN, _DYN.replace("ratio=2.5:range=8", "ratio=1.6:range=4")),   # 3: and the dynamic cut halved
    _L2.replace(_DYN, ""),                                                # 4: and the dynamic cut out
)


def band_balance(x, sr=48000):
    """the 3 to 8 kHz balance of a signal, dB (band energy over total), on its loudest 2 s (the whole of a shorter one): the
    reviewers' meter (their measuring script: a 6th-order Butterworth band, zero phase)"""
    from scipy.signal import butter, sosfiltfilt
    x = np.asarray(x, dtype=np.float64)
    if x.size < int(0.2 * sr):
        return None
    h = sosfiltfilt(butter(6, [3000, 8000], btype="band", fs=sr, output="sos"), x)
    r2, hop = int(2 * sr), int(0.1 * sr)
    if x.size > r2:
        best = max(range(0, x.size - r2, hop), key=lambda i: float((x[i:i + r2] ** 2).mean()))
        x, h = x[best:best + r2], h[best:best + r2]
    tot = float((x ** 2).mean())
    return None if tot < 1e-12 else 10 * math.log10(max(float((h ** 2).mean()), 1e-15) / tot)


def _wav_mono(path):
    from scipy.io import wavfile
    sr, x = wavfile.read(path)
    x = np.asarray(x, dtype=np.float32)
    return x.mean(axis=1) if x.ndim > 1 else x


def _piece_bad(path):
    from scipy.io import wavfile
    try:
        _sr, x = wavfile.read(path)
    except Exception:
        return True
    x = np.asarray(x, dtype=np.float32)
    return x.size == 0 or not np.isfinite(x).all() or float(np.abs(x).max()) > 2.0


def spec_speed(S):
    """15:40 (round 2, the creator; a starting default, change it in your taste file): speech runs at 1.1x by default; a
    spec's own speed other than 1.0 wins (guest C's F2 and F3 1.25, guest C's M2 and guest O's F2 1.1); `speed_locked: true`
    keeps a written 1.0"""
    v = S.get("speed")
    if v is None or (float(v) == 1.0 and not S.get("speed_locked")):
        return 1.1
    return float(v)


def audio_take(S, P, work):
    """each piece from its speaker's own track (audio_file override, else the video), the house chain, 8 ms joins, then the
    speed, loudnorm to -14 LUFS / -1.5 dBTP (2 passes), a 0.25 s fade on the last breath; true peak measured after."""
    from scipy.io import wavfile
    speed = spec_speed(S)
    src_items = P.get("runs") or P["items"]   # the contiguous runs (a card split or a crossfade never cuts the sound)
    rec = {"v": 5, "audio_v": AUDIO_V, "items": [(it["kind"], it["speaker"], round(it["a"], 4), it["n"]) for it in src_items], "speed": speed,
           "files": {k: v.get("audio_file") or v["file"] for k, v in P["people"].items()}, "offs": {k: v.get("offset") for k, v in P["people"].items()},
           "extra": {k: v.get("audio_extra") for k, v in P["people"].items() if v.get("audio_extra")} or None}
    out = work / f"audio-{key_of(rec)}.wav"
    meta = Path(str(out) + ".json")
    if out.exists() and meta.exists():
        return out, json.loads(meta.read_text())
    SR = 48000
    # 29 Oct (builder H): a piece is cut with the house chain (step 0) or a lighter step of AUDIO_LIGHTER (the band
    # guard below), each cached under its own name; `_src` is the same span with no chain (the guard's reference)
    def cut_piece(it, step):
        p = P["people"][it["speaker"]]
        src = p.get("audio_file") or p["file"]
        off = float(p.get("offset") or 0.0)
        extra = p.get("audio_extra")   # a per-source cleanup pass (tutorial-4's room echo)
        part = work / f"aud-{key_of([src, round(it['a'], 4), it['n'], AUDIO_V] + ([extra] if extra else []) + ([f'lighter{step}'] if step else []))}.wav"
        if not part.exists():
            tmpp = f"{part}.{os.getpid()}.part.wav"   # per process: a sibling build of the same spec writes the same piece
            first = AUDIO_CHAIN if step == 0 else AUDIO_LIGHTER[step - 1]
            for ci, chain in enumerate((first,) + AUDIO_FALLBACKS):
                run([FF, "-y", "-v", "error", "-ss", f"{max(0.0, it['a'] + off):.4f}", "-t", f"{it['n'] / FPS + 0.05:.4f}", "-i", src, "-vn",
                     "-af", chain + ("," + extra if extra else ""), "-ac", "1", "-c:a", "pcm_f32le", tmpp], timeout=600, label="audio piece")
                if not _piece_bad(tmpp):
                    if ci:
                        log(work, f"audio piece {it['a']:.2f}: the {'house' if step == 0 else 'lighter'} chain ran away, fallback {ci} held")
                    break
            else:
                raise RuntimeError(f"audio piece {it['a']:.2f} of {src}: every chain ran away (not finite or over +6 dBFS)")
            os.replace(tmpp, part)
        return part

    def src_piece(it):
        p = P["people"][it["speaker"]]
        src = p.get("audio_file") or p["file"]
        off = float(p.get("offset") or 0.0)
        part = work / f"aud-src-{key_of([src, round(it['a'], 4), it['n']])}.wav"
        if not part.exists():
            tmpp = f"{part}.{os.getpid()}.part.wav"
            run([FF, "-y", "-v", "error", "-ss", f"{max(0.0, it['a'] + off):.4f}", "-t", f"{it['n'] / FPS + 0.05:.4f}", "-i", src, "-vn",
                 "-af", "aresample=48000", "-ac", "1", "-c:a", "pcm_f32le", tmpp], timeout=600, label="audio piece source")
            os.replace(tmpp, part)
        return part

    def chunk_of(path, it):
        ln = it["n"] * (SR // FPS)
        sr, x = wavfile.read(path)
        x = np.asarray(x, dtype=np.float32)
        if x.ndim > 1:
            x = x.mean(axis=1)
        x = x[:ln]
        if len(x) < ln:
            x = np.concatenate([x, np.zeros(ln - len(x), dtype=np.float32)])
        return x

    def build_take(steps):
        """the take as before (joins, speed, loudnorm, SHAPE, limiter) into `out`, each speaker's pieces cut at its step"""
        chunks = []
        for it in src_items:
            ln = it["n"] * (SR // FPS)
            if it["kind"] == "card":
                chunks.append(np.zeros(ln, dtype=np.float32))
                continue
            x = chunk_of(cut_piece(it, steps.get(it["speaker"], 0)), it)
            f = min(int(0.008 * SR), ln // 4)
            fi = min(int(0.025 * SR), ln // 4)   # 29 Oct (row 218): a 25 ms fade in at every join (the 8 ms one let an onset click through, guest C's F2 8.77 s)
            if f > 1:
                ramp = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, f, dtype=np.float32))
                ramp_i = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, fi, dtype=np.float32))
                x[:fi] *= ramp_i
                x[-f:] *= ramp[::-1]
            chunks.append(x)
        y = np.concatenate(chunks)
        raw = work / f"audio-raw-{os.getpid()}.wav"
        wavfile.write(str(raw), SR, y)
        # pass 1: measure; pass 2: loudnorm linear with the measured values, after the speed
        tempo = f"atempo={speed:.4f}," if abs(speed - 1.0) > 1e-3 else ""
        r = run([FF, "-v", "info", "-i", str(raw), "-af", f"{tempo}loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"], timeout=600, label="loudnorm measure")
        j = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
        if float(j["input_i"]) > 0 or float(j["input_i"]) < -99:
            raise RuntimeError(f"loudnorm measured {j['input_i']} LUFS on the joined pieces: a piece ran away (row 190)")
        total = len(y) / SR / speed
        fade_d = 0.25
        ln2 = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
               f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true:print_format=summary")
        tmpo = f"{out}.{os.getpid()}.part.wav"
        run([FF, "-y", "-v", "error", "-i", str(raw), "-af", f"{tempo}{ln2},afade=t=out:st={max(0, total - fade_d):.3f}:d={fade_d},aresample=48000",
             "-ac", "2", "-c:a", "pcm_s16le", tmpo], timeout=600, label="loudnorm apply")
        os.replace(tmpo, out)
        try:
            os.remove(raw)
        except OSError:
            pass
        # pass 3, in PCM: loudnorm's linear pass lands 1 to 2 LU under -14 on some takes (guest O's M1 -16.1, guest C's F1 -17.9), so the
        # gain is corrected here on the wav under a limiter at -2.0 dBTP, never on the finished file through a second AAC
        # generation (27 Oct: the native aac encoder overshot a -2.1 dBTP limited signal to +5.7 dBTP on guest O's M1)
        # row 207: the transient shape always runs; the gain is found by measuring THROUGH the shape (up to 5 tries), then the
        # shape is applied once, so the compressor never runs twice on the take
        pre = f"{out}.{os.getpid()}.pre.wav"
        os.replace(out, pre)
        gain = 0.0
        for _ in range(8):
            r = subprocess.run([FF, "-nostdin", "-hide_banner", "-i", pre, "-af", f"volume={gain:.2f}dB,aresample=192000,{SHAPE},{LIMITER},aresample=48000,ebur128=peak=true", "-f", "null", "-"],
                               capture_output=True, text=True, timeout=600)
            mm = re.search(r"I:\s*(-?[\d.]+) LUFS", r.stderr[r.stderr.rfind("Summary:"):])
            if not mm:
                break
            d = -14.0 - float(mm.group(1))
            if abs(d) <= 0.2:
                break
            gain += d
        run([FF, "-y", "-v", "error", "-i", pre, "-af", f"volume={gain:.2f}dB,aresample=192000,{SHAPE},{LIMITER},aresample=48000", "-c:a", "pcm_s16le", f"{out}.{os.getpid()}.lim.wav"], timeout=600, label="shape")
        os.replace(f"{out}.{os.getpid()}.lim.wav", out)
        try:
            os.remove(pre)
        except OSError:
            pass
        lu = lufs_of(out)
        tp = true_peak(out)
        for limiter in (LIMITER, LIMITER_HARD):
            # the limiter runs on 4x oversampled audio so it holds the TRUE peak (03:35: guest C's F2 clipped source came out of
            # the sample limiter at -2.05 dBFS with a true peak of -0.8); a second, harder pass if the first still misses
            if not ((lu is not None and abs(lu + 14.0) > 0.3) or tp > -1.9):
                break
            gain = (-14.0 - lu) if lu is not None else 0.0
            run([FF, "-y", "-v", "error", "-i", str(out), "-af", f"volume={gain:.2f}dB,aresample=192000,{limiter},aresample=48000", "-c:a", "pcm_s16le", f"{out}.{os.getpid()}.lim.wav"], timeout=600, label="limiter")
            os.replace(f"{out}.{os.getpid()}.lim.wav", out)
            tp = true_peak(out)
            lu = lufs_of(out)
        return lu, tp, j, total

    def speaker_balance(spk):
        """the speaker's own stretches of the finished take, joined, on the reviewers' meter"""
        from scipy.io import wavfile as _wf
        _sr, xt = _wf.read(str(out))
        xt = (xt.astype(np.float64) / (32768.0 if xt.dtype == np.int16 else 1.0))
        xt = xt.mean(axis=1) if xt.ndim > 1 else xt
        segs = [xt[int(it["out"] / speed * SR):int((it["out"] + it["n"] / FPS) / speed * SR)] for it in src_items if it["kind"] != "card" and it["speaker"] == spk]
        segs = [g for g in segs if g.size]
        return band_balance(np.concatenate(segs)) if segs else None

    # 29 Oct (builder H, guest O's M1-animB r3: her voice dulled, the loudest 2 s' 3 to 8 kHz balance -23.4 dB against her own
    # source's -14.0): the take is built on the house chain, then each speaker's own stretches OF THE FINISHED TAKE (after
    # loudnorm, SHAPE and the limiter, as the reviewers measure) are read against the same spans of the source; on a quiet
    # track (the source's 95th-percentile 50 ms level under BAND_GUARD_QUIET) a speaker both more than BAND_GUARD_DB under the
    # source and under BAND_GUARD_FLOOR steps down AUDIO_LIGHTER (afftdn lighter, the de-esser out, the dynamic cut halved, then
    # out) and the take is built again, until every such speaker is back over min(source - 6, -20) or out of steps (the
    # brightest step kept). A chunk-level test was tried first and missed: SHAPE's band compressor takes up to 4 dB more in
    # the take, and a per-piece test lightened guest C's F3 and M1 (89 band windows over -12): both rejected
    speakers = sorted({it["speaker"] for it in src_items if it["kind"] != "card"})
    steps = {spk: 0 for spk in speakers}
    ref = {}
    for spk in speakers:
        its = [it for it in src_items if it["kind"] != "card" and it["speaker"] == spk]
        xs = np.concatenate([chunk_of(src_piece(it), it) for it in its])
        nw = xs.size // 2400
        lvl95 = 20 * math.log10(float(np.percentile(np.sqrt((xs[:nw * 2400].astype(np.float64).reshape(nw, 2400) ** 2).mean(1) + 1e-12), 95))) if nw >= 4 else 0.0
        b_src = band_balance(xs)
        if b_src is not None and lvl95 < BAND_GUARD_QUIET:
            # dull: more than 6 dB under its source AND under -20; once stepping, back over max(source - 6, -20) (the
            # conductor's "about -20 or brighter" for guest O, the reviewer's -17 to -20)
            ref[spk] = (b_src, min(b_src - BAND_GUARD_DB, BAND_GUARD_FLOOR), lvl95, max(b_src - BAND_GUARD_DB, BAND_GUARD_FLOOR))
    lu, tp, j, total = build_take(steps)
    seen = {spk: [] for spk in ref}
    for _round in range(len(AUDIO_LIGHTER) + 1):
        dull = []
        for spk, (b_src, trig, lvl95, stop) in ref.items():
            b_now = speaker_balance(spk)
            if b_now is None:
                continue
            seen[spk].append((b_now, steps[spk]))
            if b_now < (trig if steps[spk] == 0 else stop) and steps[spk] < len(AUDIO_LIGHTER):
                dull.append(spk)
        if not dull:
            break
        for spk in dull:
            steps[spk] += 1
        lu, tp, j, total = build_take(steps)
    final = {}
    for spk, hist in seen.items():
        if not hist or hist[0][0] >= ref[spk][1]:
            continue
        ok = [h for h in hist if h[0] >= ref[spk][3]]
        pick = ok[0] if ok else max(hist)
        final[spk] = pick[1]
        log(work, f"audio {spk}: 3 to 8 kHz {hist[0][0]:.1f} dB in the take on the house chain against the source's {ref[spk][0]:.1f} "
                  f"(level {ref[spk][2]:.1f} dBFS): lighter step {pick[1]} at {pick[0]:.1f}")
    if final and any(final.get(spk, 0) != steps[spk] for spk in steps):
        steps = {spk: final.get(spk, 0) for spk in steps}
        lu, tp, j, total = build_take(steps)
    m = {"input_i": j["input_i"], "true_peak_dbtp": tp, "lufs": lu, "secs": total}
    try:
        # 29 Oct (builder H): the take's 3 to 8 kHz band peak and its 50 ms windows over -12 dBFS (the reviewers' meter),
        # logged so a lighter step that let a sharp second back in is named
        from scipy.signal import butter, sosfiltfilt
        from scipy.io import wavfile as _wf
        _sr, xt = _wf.read(str(out))
        xt = (xt.astype(np.float64) / (32768.0 if xt.dtype == np.int16 else 1.0))
        xt = xt.mean(axis=1) if xt.ndim > 1 else xt
        hb = np.abs(sosfiltfilt(butter(6, [3000, 8000], btype="band", fs=48000, output="sos"), xt))
        nwt = hb.size // 2400
        if nwt:
            pk = hb[:nwt * 2400].reshape(nwt, 2400).max(1)
            m["band_peak_dbfs"] = round(20 * math.log10(float(pk.max()) + 1e-9), 1)
            m["band_over_-12"] = int((pk > 10 ** (-12 / 20)).sum())
            log(work, f"audio take: 3 to 8 kHz peak {m['band_peak_dbfs']} dBFS, {m['band_over_-12']} windows over -12 dBFS" + (" (OVER -6: a sharp second)" if m["band_peak_dbfs"] > -6 else ""))
    except Exception as e:  # noqa: BLE001
        log(work, f"audio take: band measure failed ({e})")
    meta.write_text(json.dumps(m))
    return out, m


LIMITER = "alimiter=limit=0.79:level=false:attack=5:release=60"   # -2.05 dBTP: 0.5 dB of headroom for the AAC encoder
LIMITER_HARD = "alimiter=limit=0.71:level=false:attack=3:release=80"   # -3 dB, the second pass on a clipped source
AAC = ["-c:a", "aac_at", "-b:a", "192k", "-ar", "48000"]            # Apple's encoder: measured 0.2 dB over the PCM peak where ffmpeg's aac went +5.7


def true_peak(path):
    r = subprocess.run([FF, "-nostdin", "-hide_banner", "-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True, timeout=600)
    s = r.stderr[r.stderr.rfind("Summary:"):]
    m = re.search(r"Peak:\s*(-?[\d.]+) dBFS", s)
    return float(m.group(1)) if m else 0.0


def lufs_of(path):
    r = subprocess.run([FF, "-nostdin", "-hide_banner", "-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True, timeout=600)
    s = r.stderr[r.stderr.rfind("Summary:"):]
    m = re.search(r"I:\s*(-?[\d.]+) LUFS", s)
    return float(m.group(1)) if m else None


# ---------------------------------------------------------------- the graphic layer (Chrome)
GROUND = {"ledger": "F7F6F2", "none": "F7F6F2", "whiteboard": "FFFFFF", "operator": "15171A", "flat2d": "F3F7F8", "ig_native": "101010"}   # whiteboard white since 27 Oct: its dark ground flashed at the cut


def usable_screen(S):
    """the spec's screen only when it has a file AND a measured crop (27 Oct 11:45, pass 2 set CE: tutorial-2 F1
    composited an unseeked, unmeasured full-frame crop and showed 45 s of white); otherwise None and the operator window
    draws the spec's steps as its panel content."""
    scr = S.get("screen")
    if not scr or not scr.get("file") or not scr.get("crop"):
        return None
    if "not measured" in str(scr.get("crop_note") or "").lower():
        return None
    if scr.get("draw_steps"):   # (pass 3, tutorial-4 F1: the measured crop landed on blank screen): the spec asks for the steps instead
        return None
    return scr


def overlay_payload(S, P, look, speed):
    g = S.get("graphic") or {}
    clock_role = P["clock"] if P["clock"] in P["people"] else next(iter(P["people"]))
    LY = P["layout"]
    # the eyebrow names the person who speaks the answer (reviewer A: wave1-04 named the guest over the co-host's short)
    secs = {}
    for it in P["items"]:
        if it["kind"] == "answer":
            secs[it["speaker"]] = secs.get(it["speaker"], 0) + it["n"]
    lead = max(secs, key=secs.get) if secs else ("guest" if "guest" in P["people"] else "host")

    def to_out(tc):
        """a clock time (on the clock person's file time minus their offset... the spec's keys are on the clock) -> output s.
        22:20 (builder A, cause 4: guest C's M2-hook2 lit its last key from the aha preview at 0 s, so the timeline was
        spent before the story began): an aha preview piece never takes a key; the key lands where the line is heard
        again in the story"""
        runs = [it for it in (P.get("runs") or P["items"]) if it["kind"] != "card" and (S.get("aha_keys") or not it.get("aha"))]
        for it in runs:
            if it["a"] - 0.05 <= tc <= it["b"] + 0.05:
                return (it["out"] + max(0.0, tc - it["a"])) / speed
        # a key outside every kept piece: the nearest piece start after it, else the end
        after = [it for it in runs if it["a"] > tc]
        if after:
            return min(it["out"] for it in after) / speed
        return (P["total_n"] / FPS) / speed - 0.5

    keys = [[k[0], round(to_out(float(k[1])), 3)] for k in (g.get("keys") or [])]
    guest = P["people"].get("guest") or P["people"].get("host")
    lp = P["people"][lead]
    if S.get("eyebrow"):
        eyebrow = S["eyebrow"]
    elif lead == "guest":
        eyebrow = f"{lp['name']} · on the podcast"
    elif lead == "cohost":
        eyebrow = f"{lp['name']} · {OWN_BRAND}" if OWN_BRAND else lp["name"]
    else:
        # the creator's own name and brand, spelled exactly as the brand writes it (never a near variant of the company
        # name): config "host_eyebrow", else "<host name> · <first own name>"
        eyebrow = PATHS.CONFIG.get("host_eyebrow") or " · ".join(
            x for x in ((P["people"].get("host") or lp).get("name"), OWN_BRAND) if x)
    story = S.get("format") == "story-proof" and "guest" in P["people"] and "host" in P["people"]
    credit = credit_for(S)   # 28 Oct (polish): the guest's own firm beside the guest's name, never ours
    # (pass 3: guest G's and guest D's credits promised the full talk with nothing saying it is live; the rule: a promise
    # on screen ships only once it is a live link):
    # the promise shows only when the spec says `long_form_live: true`; otherwise the plain name
    credit_full = credit
    if not S.get("long_form_live"):
        credit = re.sub(r"\s*[·\-|]\s*full (talk|video|episode|conversation)[^·|]*$", "", credit, flags=re.I).strip()
    ig = None
    hook_start_out = (P.get("hook_start") or 0.0) / speed
    hook_end_out = P["hook_end"] / speed if P["hook_end"] > 0 else -1
    title_until = None
    if is_igmode(S, look):
        sig = S.get("ig") or {}
        co = sig.get("callout")
        start_out = (P["hook_end"] / speed) if P["hook_end"] > 0 else 0.0
        if co:
            # a callout with no clock shows from frame 0 (on the hook's guest panel, as on still B) until the list starts
            callout = [co[0], round(to_out(float(co[1])), 3) if len(co) > 1 and co[1] is not None else 0.0]
        else:
            line = S.get("pov_line") or S.get("band_text") or S.get("held_top")
            callout = [line, start_out] if line and line != S["title"] else None
        items = [str(x).replace("|", ": ") for x in (g.get("items") or [])] if (g.get("kind") or "none") not in ("none", "screen") and not S.get("ig_between") else []
        ig = {"emoji": sig.get("emoji") or "", "callout": callout, "items": items}
        # 28 Oct (polish, guest Q's C: "use the space above her head: remove the headline on top after 28 seconds, then put
        # these bullet points above her head"; Round-3 ruling: nothing is ever placed on a face, the title leaves at about
        # 28 s or when a graphic needs the top): the title stickers leave at 28 s, or earlier at the first list sticker or
        # the callout's own time (the top is the only place off the face), never inside the hook or its first second
        dur_out = P["total_n"] / FPS / speed
        cands = [28.0]
        item_ts = [k[1] for k in keys if k[1] is not None] if items else []
        if item_ts:
            cands.append(min(item_ts))
        if callout and callout[1] and callout[1] > max(hook_end_out, 0) + 1.0:
            cands.append(callout[1])
        title_until = round(max(min(cands), max(hook_end_out, 0) + 1.0), 3)
        # 29 Oct (row 189, the r3 checker on guest Q's F1 and the handoff's open point): the under-35 s exception is gone;
        # the reading taken of "the title leaves after about 28 seconds" is the literal one, on every short, so the title
        # never returns over the introduction at the end (the credit still takes its box in the last 6 s)
        if S.get("title_until") is not None:
            title_until = float(S["title_until"])   # the spec's own word (guest Q's after-M31: 28 s, the creator's C note)
        if sig.get("list_at") == "title_off" and items and title_until is not None:
            # guest Q's C: the bullets land above her head once the title has left, as the closing summary, 0.7 s apart
            keys = [[k[0], round(title_until + 0.35 + 0.7 * i, 3)] for i, k in enumerate(g.get("keys") or [])]
    else:
        # 29 Oct (builder H, guest C's M2 r3: the drawn timeline look kept its title to 47 s, where the credit took the box):
        # the drawn looks' title leaves at 28 s too (row 189b's reading, every short), never inside the stacked question; the
        # spec's own `title_until` wins; the credit still takes the title's box in the last 6 s
        title_until = round(max(28.0, max(hook_end_out, 0) + 1.0), 3)
        if S.get("title_until") is not None:
            title_until = float(S["title_until"])
    wins, cur = [], None
    if S.get("card_only_moving"):
        # a window opens where the crossfade INTO the card starts and closes where the crossfade out of it starts,
        # so the page's band and card move over the same 0.3 s as the footage (looks.html: 0.3 s in and out)
        for it in P["items"]:
            on = it["kind"] == "answer" and (it["layout"] == "answer" or (it["layout"] == "xfade" and it.get("to") == "answer"))
            a_o, b_o = it["out"] / speed, (it["out"] + it["n"] / FPS) / speed
            if on:
                if cur and abs(cur[1] - a_o) < 0.05:
                    cur[1] = b_o
                else:
                    cur = [a_o, b_o]
                    wins.append(cur)
            if it["layout"] == "xfade" and it.get("from") == "answer" and cur is not None:
                cur[1] = a_o          # the out crossfade starts here
                cur = None
        wins = [[round(a, 3), round(b, 3)] for a, b in wins]
    # 29 Oct (builder H, guest C's F1 r3: the title held 0 to 57.7 s and the red callout on her mouth from 52 s): a story-proof
    # short sends hook_end as the whole short (the drawn looks' duo credit), so on the Instagram looks the title never left
    # and the callout kept the stacked hook's seam spot (seam + 32) over a full-face tail. The pages now read `stack` (the
    # output windows where the frame really is the stacked pair: hook and duo pieces) for the callout's spot and the list,
    # and `q_end` (the stacked question's own end) for the title's 28 s exit
    stack, cw = [], None
    for it in P["items"]:
        a_o, b_o = it["out"] / speed, (it["out"] + it["n"] / FPS) / speed
        if it["kind"] != "card" and it["layout"] in ("hook", "duo"):
            if cw and abs(cw[1] - a_o) < 0.05:
                cw[1] = b_o
            else:
                cw = [a_o, b_o]
                stack.append(cw)
        else:
            cw = None
    stack = [[round(a, 3), round(b, 3)] for a, b in stack]
    # 29 Oct (builder H, guest E's M2-animA r3: the credit '<guest> · <firm>' ended where the host's introduction
    # starts (row 232), but the 2.5 s before it are the host's own answer piece, so the guest's name sat over the host): the
    # credit's 6 s end where the guest last speaks before the introduction (or before the end), `credit_end`
    _intro0 = min([it["out"] for it in P["items"] if it.get("intro")] or [P["total_n"] / FPS])
    _cr_role = "guest" if "guest" in P["people"] else None
    _g_ends = [it["out"] + it["n"] / FPS for it in P["items"] if _cr_role and it["kind"] == "answer" and it.get("speaker") == _cr_role
               and it["out"] + it["n"] / FPS <= _intro0 + 1e-6]
    credit_end = round(max(_g_ends) / speed, 3) if _g_ends else None
    title_swaps = [[round(to_out(float(sw[0])), 3), str(sw[1]), str(sw[2] if len(sw) > 2 else "")] for sw in (S.get("title_swaps") or [])]   # 2 Nov: the title sentence follows the talk
    return {"title_swaps": title_swaps, "ig_list_under_title": bool(S.get("ig_list_under_title")), "credit_end": credit_end,"look": look, "ig": ig, "anim": S.get("anim"), "stack": stack, "q_end": round(hook_end_out, 3), "anim_title": S.get("anim_title") or "stays", "anim_dark": bool(S.get("anim_dark")), "anim_light": bool(S.get("anim_light")), "anim_doc": S.get("anim_doc"), "card_windows": wins, "title": S["title"], "title_accent": S.get("title_accent") or "", "eyebrow": eyebrow, "credit": credit,
            "ig_between": bool(S.get("ig_between")), "hook_start": round(hook_start_out, 3), "title_until": title_until,
            "intro_start": round(min([it["out"] for it in P["items"] if it.get("intro")] or [-1]) / speed, 3) if any(it.get("intro") for it in P["items"]) else None,
            "format": S.get("format") or "", "story_proof": story,
            "pov_line": S.get("pov_line") if S.get("format") == "pov-bit" else None,
            "held_top": S.get("held_top") if S.get("held_top") and S.get("held_top") != S["title"] else None,
            "band_text": S.get("band_text") if S.get("format") == "claim-band" else None,
            "hook_end": (P["total_n"] / FPS + 1) / speed if story else (P["hook_end"] / speed if P["hook_end"] > 0 else -1), "duration": P["total_n"] / FPS / speed,
            "graphic": {"kind": g.get("kind") or "none", "items": g.get("items") or [], "keys": keys, "source_line": g.get("source_line"), "clawd": bool(g.get("clawd"))},   # clawd: any mascot illustration you own (paths.MASCOT_PNG), optional
            "source_name": guest["name"] if guest else "", "screen_rect": [60, 540, 960, 360] if usable_screen(S) else None,
            "window_title": (S.get("screen") or {}).get("title") or "Screen",
            "layout": {"hook": {"top_band_h": LY["hook"]["top_band_h"], "host": [LY["hook"]["host"]["y"], LY["hook"]["host"]["h"]],
                                "guest": [LY["hook"]["guest"]["y"], LY["hook"]["guest"]["h"]]},
                       "answer": {"top_band_h": LY["answer"]["top_band_h"], "guest": [LY["answer"]["guest"]["y"], LY["answer"]["guest"]["h"]]},
                       "answer_full": {"top_band_h": LY["answer_full"]["top_band_h"], "guest": [LY["answer_full"]["guest"]["y"], LY["answer_full"]["guest"]["h"]]}}}


def open_page(page, html_path):
    """open a looks page in Chrome on THIS machine: its tokens filled and its file:// URLs remapped
    (paths.page_for_this_mac; with nothing to fill, the original file itself), then every @font-face the page declares loaded,
    or a RuntimeError naming the face (a font that silently fell back would burn the wrong type into every frame)."""
    url_path = PATHS.page_for_this_mac(html_path, WORKROOT / "pages")
    import urllib.parse
    text = Path(url_path).read_text()
    missing = sorted({u for u in re.findall(r"file://([^\"'()\s<>]+)", text) if not os.path.exists(urllib.parse.unquote(u))})
    if missing:   # a font, springs.js, the logo or the mascot illustration that is not on this machine
        raise RuntimeError(f"overlay page {Path(html_path).name}: files it loads are missing on this machine: {missing}")
    page.goto(f"file://{url_path}")
    page.wait_for_load_state("networkidle")
    faces = page.evaluate("""() => Promise.all([...document.fonts].map(f => f.load().then(() => [f.family, 'loaded'], e => [f.family, String(e)])))""")
    bad = [f for f in faces if f[1] != "loaded"]
    if bad:
        raise RuntimeError(f"overlay page {Path(html_path).name}: font faces not loaded on this machine: {bad}")
    if "springs.js" in text and not page.evaluate("() => typeof window.SPR === 'object'"):
        raise RuntimeError(f"overlay page {Path(html_path).name}: springs.js did not load (window.SPR missing)")
    if not page.evaluate("() => typeof window.setup === 'function' && typeof window.setTime === 'function'"):
        raise RuntimeError(f"overlay page {Path(html_path).name}: setup/setTime missing (springs.js or the page script failed)")
    return faces


def render_overlay(payload, nfr, work, tag):
    """PNG sequence (alpha) of the graphic layer, one file per output frame; a frame whose state signature matches the one
    before is a hardlink. Returns (seq_dir, unique_count, setup_info)."""
    from playwright.sync_api import sync_playwright
    # 27 Oct (night conductor): an alternative looks page (the animation-direction compares, anim_looks.html beside
    # this file) is named by the env SHORTS_LOOKS_HTML; the page hash keys the cache so a page edit re-renders
    html_path = Path(PATHS.remap(os.environ.get("SHORTS_LOOKS_HTML") or "") or LOOKS_HTML)   # a queue line may name a page as another machine spells it
    rec = {"v": 3, "payload": payload, "nfr": nfr, "html": hashlib.sha1(html_path.read_bytes()).hexdigest()[:10], "page": html_path.name}
    seq = work / f"ov-{tag}-{key_of(rec)}"
    done = seq / "DONE.json"
    if done.exists():
        d = json.loads(done.read_text())
        return seq, d["unique"], d["setup"]
    seq.mkdir(parents=True, exist_ok=True)
    unique = 0
    with sync_playwright() as pw:
        try:
            browser = pw.chromium.launch(channel="chrome")
        except Exception:
            browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": VW, "height": VH}, device_scale_factor=1)
        page_errs = []
        page.on("pageerror", lambda e: page_errs.append(str(e)))   # 2 Nov 2026: a page that throws fails the build
        open_page(page, html_path)
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(200)
        setup = page.evaluate("(p) => window.setup(p)", payload)
        page.wait_for_timeout(100)
        if page_errs:
            raise RuntimeError(f"overlay page {html_path.name} threw: {page_errs[:3]}")
        last_sig, last_path = None, None
        for i in range(nfr):
            t = i / FPS
            sig = page.evaluate("(t) => window.setTime(t)", t)
            path = seq / f"{i:05d}.png"
            if path.exists():
                last_sig, last_path = sig, path
                continue
            if sig == last_sig and last_path is not None:
                os.link(last_path, path)
            else:
                page.screenshot(path=str(path), omit_background=True)
                unique += 1
                last_sig, last_path = sig, path
        browser.close()
    if page_errs:
        raise RuntimeError(f"overlay page {html_path.name} threw: {page_errs[:3]}")
    done.write_text(json.dumps({"unique": unique, "setup": setup}))
    return seq, unique, setup


# ---------------------------------------------------------------- checks
def contact_sheet(final, P, speed, out_path, every=5.0):
    """frames at the start, every cut and every 5 s, at full resolution scaled into a sheet for the reviewer."""
    total = P["total_n"] / FPS / speed
    ts = {0.0}
    for it in P["items"]:
        ts.add(round(it["out"] / speed + 0.05, 2))
    t = 0.0
    while t < total:
        ts.add(round(t, 2))
        t += every
    ts = sorted(x for x in ts if x < total - 0.02)
    frames = []
    fr_dir = out_path.parent / f"sheet-frames-{out_path.stem}"   # per look: a sibling build of the same spec never shares it
    fr_dir.mkdir(parents=True, exist_ok=True)
    for i, t in enumerate(ts):
        f = fr_dir / f"{i:03d}.jpg"
        run([FF, "-y", "-v", "error", "-ss", f"{t:.3f}", "-i", str(final), "-frames:v", "1", "-q:v", "3", str(f)], timeout=120, label="sheet frame")
        frames.append((t, f))
    cols = 4
    tw, th = 405, 720
    rows = -(-len(frames) // cols)
    sheet = Image.new("RGB", (cols * (tw + 10) + 10, rows * (th + 40) + 10), (30, 30, 30))
    d = ImageDraw.Draw(sheet)
    f = ImageFont.truetype(str(FONTDIR / "Inter[opsz,wght].ttf"), 22)
    for i, (t, p) in enumerate(frames):
        im = Image.open(p).resize((tw, th))
        x, y = 10 + (i % cols) * (tw + 10), 10 + (i // cols) * (th + 40)
        sheet.paste(im, (x, y))
        d.text((x, y + th + 6), f"{t:.2f} s", font=f, fill=(255, 255, 255))
    sheet.save(out_path, quality=85)
    return frames


CAP_LH = 1.219          # Montserrat's line box in em (ascender 968 + descender 251 of 1000): libass's line height


IG_SEAM_MAX = 1000   # the lowest the ig hook seam may go (the guest panel keeps 920 px)
IG_SEAM_MAX_SMALL = 1160   # 29 Oct (builder G): ... when the questioner's face is small in her source (the guest panel keeps 760 px)
IG_Q_FACE = 300            # 29 Oct (builder G): the questioner's face on the ig hook, px, at least (Round-3: nobody is small)
IG_SEAM_SHARE = 1066       # 29 Oct (builder G): the seam cap for a questioner of 260 to 300 px at full width: 1480 - 15 - 1.33 x 300, the guest's own 300 px
IG_Q_TRIGGER = 260         # ... applied when her face at the full width is under this (guest S's 297 px host keeps his 1000 seam and his guest's 338)


def ig_hook_seam(P, faces):
    """23:25 (conductor, guest O's F3 r2): on the ig_native stacked hook the host's crown must sit 24 px under the title
    stack's foot (`crown_min`), and the host's head fills his 720 px source, so at the crop's full width (the narrowest
    the panel allows) crown to chin needs more than 880 - crown_min px. The seam then moves down to fit his head (crown,
    chin of the lowest lean-in seen plus 8 % of the box), at most to 1000; the guest panel starts there (its own solve
    keeps her mouth over 1480). Changes P's hook layout in place; returns the new seam or None."""
    lay = P["layout"].get("hook") or {}
    host = lay.get("host")
    if not host or not host.get("crown_min") or P["hook_end"] <= 0:
        return None
    need = host["y"] + host["h"]
    small_any = False
    for it in P["items"]:
        if it["layout"] != "hook" or it["kind"] == "card":
            continue
        role = it["speaker"]
        p = P["people"].get(role)
        if not p or p.get("layouts") or p.get("medallion"):
            continue
        fx, fy, fw, fh = faces[role]["box"]
        hi_ = faces[role].get("high")
        crown = min(fy, hi_ if hi_ is not None else fy) - 0.55 * fh
        low = faces[role].get("low")
        lowc = max(fy + fh, (low - 0.25 * fh) if low else fy + fh)
        rw = (p.get("crop") or [0, 0, info(p["file"])["w"], 0])[2]
        k_w = VW / rw
        # 28 Oct (polish): crown to COLLAR (the chin plus half a box: the neck and the shirt collar, guest X's F2 B), at most 1000
        # 29 Oct (builder G, guest Q's F1 r3: the co-host's question face 184 px, her 215 px face at the full width under a 2-line
        # title): a questioner whose face at the full width is under IG_Q_FACE gets the panel her face needs at IG_Q_FACE
        # px with the head whole to the collar, the seam then going as low as IG_SEAM_MAX_SMALL (the listening guest
        # below shrinks for those seconds); a face big at the full width keeps the 1000 cap
        # (not on a story-proof short: its `duo` shares this panel through the whole answer, and the guest would stay small
        # under the credit; guest C's F1, conductor 17:25, a 210 px guest)
        # 29 Oct (builder H, guest C's F1): a duo limited to the pieces a spec names (`duo_pieces`) shares this panel for
        # those seconds only, so the questioner search runs as on any other hook (the duo piece takes the same seam)
        duo_used = any(x.get("layout") == "duo" for x in P["items"]) and not P.get("duo_part")
        # 29 Oct to 18:10 (builder G; guest C's F3 r3: the host 274 px in the question, his office uncropped; guest X's animB/Bd:
        # the 1160 seam left the guest 146 px; guest C's M1: a formula balance took her from 292 to 261 px): a questioner under IG_Q_FACE
        # at the full width marks the hook for the search below
        if fh * k_w < IG_Q_FACE and not duo_used:
            small_any = True
        src_bot = (p.get("crop") or [0, 0, 0, info(p["file"])["h"]])
        src_bot = src_bot[1] + src_bot[3]
        need = max(need, min(IG_SEAM_MAX, host["crown_min"] + (min(lowc + 0.5 * fh, src_bot) - crown) * k_w + 12))   # the collar only as far as the tape holds it
    if small_any:
        # the seam from the full-width need down to IG_SEAM_MAX_SMALL, 8 px a step, each solved as the build will cut it
        # (face_on_frame on both panels of every hook piece): the seam whose smaller face is biggest wins (a ground-sided
        # crop counts 40 px less), the highest seam on a tie; every panel keeps its own rules (crown under the title,
        # collar, mouth over the caption line)
        base = max(host["y"] + host["h"], int(math.ceil(min(IG_SEAM_MAX, need) / 2) * 2))
        best = None
        for s_ in range(base, IG_SEAM_MAX_SMALL + 1, 8):
            hp = dict(host, h=s_ - host["y"])
            if hp.get("collar_max") is not None:
                hp["collar_max"] = s_ - 12
            gp_ = dict(lay["guest"], y=s_, h=VH - s_)
            sc = None
            for it in P["items"]:
                if it["layout"] != "hook" or it["kind"] == "card":
                    continue
                for role_, pn in panel_roles(it, {"host": hp, "guest": gp_}, P["people"]):
                    pp = P["people"][role_]
                    if pp.get("medallion") or role_ not in faces:
                        continue
                    if pp.get("layouts"):   # a person with named crops: every crop counts (guest X's F2 listener)
                        gs = [face_on_frame(info(pp["file"]), fb["box"], pn, pp["crops"][nm], fb.get("low"), fb.get("high")) for nm, fb in faces[role_]["by"].items()]
                    else:
                        gs = [face_on_frame(info(pp["file"]), faces[role_]["box"], pn, pp.get("crop"), faces[role_].get("low"), faces[role_].get("high"), bool(pp.get("crop_hard")))]
                    for g in gs:
                        v = g["height"] - (40 if (g.get("ground_pillar") or g.get("pillar") or g.get("legacy")) else 0)
                        if pn is hp and g.get("relax", 0) >= 3:
                            v -= 40   # 29 Oct (guest S's F3 r3: the host's chin and collar on the seam at relax 3; a cut collar is a Round-3 fail): a top panel that dropped its collar counts 40 px less
                        sc = v if sc is None else min(sc, v)
            if sc is not None and (best is None or sc > best[0]):
                best = (sc, s_)
        if best is not None:
            need = best[1]
    seam = int(min(IG_SEAM_MAX_SMALL, math.ceil(need / 2) * 2))
    if seam <= host["y"] + host["h"]:
        return None
    host["h"] = seam - host["y"]
    if host.get("collar_max") is not None:
        host["collar_max"] = seam - 12
    lay["guest"]["y"], lay["guest"]["h"] = seam, VH - seam
    return seam


IG_Q_FULL_BELOW = 272   # 29 Oct (builder G): a stacked question whose smaller face solves under this goes full frame (the shorts the 18:52 review passed at 276 and up stay stacked)


def ig_question_full(S, P, faces):
    """29 Oct 19:10 (builder G, conductor 19:05): True when the short's stacked question (the `question` after an aha opener,
    Instagram looks) solves with its smaller face under IG_Q_FULL_BELOW px after ig_hook_seam, so _build2 re-plans it with
    `question_full`; a duo short never (its pair is the format)"""
    if S.get("question_full") or not (S.get("question") or {}).get("pieces") or P["hook_end"] <= 0:
        return False
    if any(it.get("layout") == "duo" for it in P["items"]):
        return False
    lay = P["layout"].get("hook") or {}
    small = None
    for it in P["items"]:
        if it["layout"] != "hook" or it["kind"] == "card":
            continue
        for role, pn in panel_roles(it, lay, P["people"]):
            pp = P["people"][role]
            if pp.get("medallion") or role not in faces:
                continue
            if pp.get("layouts"):
                gs = [face_on_frame(info(pp["file"]), fb["box"], pn, pp["crops"][nm], fb.get("low"), fb.get("high")) for nm, fb in faces[role]["by"].items()]
            else:
                gs = [face_on_frame(info(pp["file"]), faces[role]["box"], pn, pp.get("crop"), faces[role].get("low"), faces[role].get("high"), bool(pp.get("crop_hard")))]
            for g in gs:
                small = g["height"] if small is None else min(small, g["height"])
    return small is not None and small < IG_Q_FULL_BELOW


DRAWN_SEAM_RANGE = (960, 1200)   # 29 Oct (builder H): where the drawn hook's seam may move (the host under the title band at 516)


def _hook_score(P, faces, lay):
    """the smaller face of every stacked hook piece under `lay` (hook pieces only), (actual px, scored px): a ground-sided,
    pillared or legacy crop counts 40 px less, a top panel that dropped its collar (relax 3) 40 px less"""
    small, score = None, None
    for it in P["items"]:
        if it["layout"] != "hook" or it["kind"] == "card":
            continue
        for role_, pn in panel_roles(it, lay, P["people"]):
            pp = P["people"][role_]
            if pp.get("medallion") or role_ not in faces:
                continue
            if pp.get("layouts"):
                gs = [face_on_frame(info(pp["file"]), fb["box"], pn, pp["crops"][nm], fb.get("low"), fb.get("high")) for nm, fb in faces[role_]["by"].items()]
            else:
                gs = [face_on_frame(info(pp["file"]), faces[role_]["box"], pn, pp.get("crop"), faces[role_].get("low"), faces[role_].get("high"), bool(pp.get("crop_hard")))]
            for g in gs:
                v = g["height"] - (40 if (g.get("ground_pillar") or g.get("pillar") or g.get("legacy")) else 0)
                if pn is lay["host"] and g.get("relax", 0) >= 3:
                    v -= 40
                small = g["height"] if small is None else min(small, g["height"])
                score = v if score is None else min(score, v)
    return small, score


def drawn_hook_fit(S, P, faces):
    """29 Oct (builder H, guest C's M2 r3: the drawn timeline look's question hook stacked the guest at 230 px; rows 221, 233 and
    234 were written for the Instagram looks only): the drawn looks get the same two steps. (1) When the stacked hook's
    smaller face is under IG_Q_FULL_BELOW, the seam between the host (under the title band) and the guest is SEARCHED over
    DRAWN_SEAM_RANGE in 8 px steps with the guest's face target at 300 (Round-3: nobody small), every panel keeping its own
    rules; a seam is taken only when its smaller face reaches IG_Q_FULL_BELOW (so a hook that already holds stays as it was).
    (2) If no seam gets there and the short has a `question` after an aha opener (not a duo short), it plays full frame
    (`question_full`: the caller re-plans). Returns "seam <y>", "flip" or None. Changes P's hook layout (a copy) in place."""
    import copy
    lay = P["layout"].get("hook") or {}
    if P["hook_end"] <= 0 or not lay.get("host") or not lay.get("guest"):
        return None
    small, _ = _hook_score(P, faces, lay)
    if small is None or small >= IG_Q_FULL_BELOW:
        return None
    best = None
    hy = lay["host"]["y"]
    for s_ in range(DRAWN_SEAM_RANGE[0], DRAWN_SEAM_RANGE[1] + 1, 8):
        hp = dict(lay["host"], h=s_ - hy)
        if hp.get("collar_max") is not None:
            hp["collar_max"] = s_ - 8
        gp_ = dict(lay["guest"], y=s_, h=VH - s_, face_px=max(300, lay["guest"].get("face_px") or 0))
        sm, sc = _hook_score(P, faces, {"host": hp, "guest": gp_})
        if sm is not None and sm >= IG_Q_FULL_BELOW and (best is None or sc > best[0]):
            best = (sc, s_, hp, gp_)
    if best is not None:
        nl = copy.deepcopy(lay)
        nl["host"], nl["guest"] = best[2], best[3]
        same = P["layout"].get("duo") is lay
        P["layout"]["hook"] = nl
        if same:
            P["layout"]["duo"] = nl
        return f"seam {best[1]}"
    if (S.get("question") or {}).get("pieces") and not S.get("question_full") and not any(it.get("layout") == "duo" for it in P["items"]):
        # the flip only where the asker's full-face framing holds its own rules (relax under 1: the mouth over the caption
        # block): guest U's M1 host, whose chin sits at the foot of his tape, would land with the mouth at 1357, a
        # face_high fail and a caption that cannot clear him, so his stacked hook stays and is named instead
        spk = (S.get("question") or {}).get("speaker") or "host"
        pp = P["people"].get(spk)
        full = (P["layout"].get("answer_full") or {}).get("guest")
        if pp and full and spk in faces and not pp.get("layouts") and not pp.get("medallion"):
            g = face_on_frame(info(pp["file"]), faces[spk]["box"], full, pp.get("crop"), faces[spk].get("low"), faces[spk].get("high"), bool(pp.get("crop_hard")))
            if g.get("relax", 0) >= 1 or g.get("legacy") or g.get("ground_pillar") or (full.get("mouth_max") and g["mouth"] > full["mouth_max"] + 2):
                return None
        return "flip"
    return None


CAP_FOOT_MAX = 1620   # 29 Oct (builder H): the lowest a drawn caption block's foot may go to clear a chin (the Instagram sticker's own foot)


def caption_clear_chin(P, faces, groups):
    """29 Oct (builder H, guest C's M2 r3: in the card state the first caption line sat on her chin and jaw, mouth 1239, ink
    from 1265, chin 1303): a drawn caption block (not the hook's, which hook_caption_y centres in the seam) whose box would
    start above the chin of a face on screen under it (the lowest chin of every panel it spans, crossfades both sides) plus
    8 px is set lower, its box from that line, its foot at most CAP_FOOT_MAX (the blurred band takes a boxed caption);
    blocks that already clear are left where they were. Sets g['pos_y']; returns how many moved."""
    moved = 0
    for g in groups:
        if g.get("hook") or g.get("pos_y"):
            continue
        size = 118 if g["style"] == "Big" else 104
        h = size * CAP_LH * len(g["lines"])
        top = CAP_BOTTOM - h
        chin = None
        for it in P["items"]:
            if it["kind"] == "card" or it["out"] >= g["e"] or it["out"] + it["n"] / FPS <= g["s"]:
                continue
            for ln in ([it["from"], it["to"]] if it["layout"] == "xfade" else [it["layout"]]):
                for role, panel in panel_roles(dict(it, layout=ln), P["layout"][ln], P["people"]):
                    p = P["people"][role]
                    if p.get("layouts") or p.get("medallion") or role not in faces:
                        continue
                    fg = face_on_frame(info(p["file"]), faces[role]["box"], panel, p.get("crop"), faces[role].get("low"), faces[role].get("high"), bool(p.get("crop_hard")))
                    if fg["bottom"] < VH - 1:
                        chin = fg["bottom"] if chin is None else max(chin, fg["bottom"])
        if chin is None or top >= chin + 8:
            continue
        new_top = min(chin + 8, CAP_FOOT_MAX - h)
        if new_top <= top:
            continue
        g["pos_y"] = int(round(new_top + h / 2))
        moved += 1
    return moved


def hook_caption_y(P, faces):
    """23:10 (conductor, guest O's M1 1.0 s: the host's caption 'asking, a brain surgeon,' across the guest's mouth): the drawn
    hook's caption line is centred in the seam between the host's chin (the lowest seen on any hook piece) and the
    guest's brow, when the seam holds a 104 px line (127 px); None when there is no stacked hook"""
    lo, hi = 0, VH
    for it in P["items"]:
        if it["kind"] == "card" or it["layout"] != "hook":
            continue
        lay = P["layout"]["hook"]
        for role, panel in panel_roles(it, lay, P["people"]):
            p = P["people"][role]
            if p.get("layouts") or p.get("medallion"):
                continue
            g = face_on_frame(info(p["file"]), faces[role]["box"], panel, p.get("crop"), faces[role].get("low"), faces[role].get("high"), bool(p.get("crop_hard")))
            if panel is lay["host"]:
                lo = max(lo, g["bottom"])
            else:
                hi = min(hi, g["top"])
    if lo == 0 or hi == VH:
        return None
    lh = 104 * CAP_LH
    y = (lo + hi) / 2 if hi - lo >= lh + 12 else lo + 6 + lh / 2
    return int(round(min(y, SAFE_BOTTOM - lh / 2)))


def caption_boxes(groups, speed, ig_caps=None):
    """(s, e, [l, t, r, b]) in output seconds for every caption on screen: the drawn groups' libass block (its foot at 1492,
    or centred on pos_y), the ig sticker line at 1556 (2 rows lifted one line when over 780 px)"""
    out = []
    if ig_caps is not None:
        f = ImageFont.truetype(str(MONT), 52)
        for c in ig_caps:
            w = f.getlength(" ".join(x[0] for x in c["w"])) + 12 * len(c["w"]) + 24   # + the dark line box's padding (29 Oct, builder G)
            rows = 2 if w > 780 else 1
            top = 1556 - (62 if rows == 2 else 0)
            out.append((c["s"], c["e"], [540 - min(w, 780) / 2, top, 540 + min(w, 780) / 2, top + 62 * rows]))
        return out
    for g in groups:
        size = 118 if g["style"] == "Big" else 104
        texts = [w[0] for w in g["w"]]
        w = max(drawn_width(" ".join(texts[i] for i in ln), size) for ln in g["lines"])
        h = size * CAP_LH * len(g["lines"])
        if g.get("pos_y"):
            top = g["pos_y"] - h / 2
        else:
            top = CAP_BOTTOM - h
        # the ink starts under the line box's ascender space (Montserrat: 0.968 em ascender, 0.70 em capitals)
        # 29 Oct (builder H): since the drawn lines sit in their dark box, what covers the frame is the box: the line
        # boxes from their top, CAP_BOX_PAD wider each side
        out.append((g["s"] / speed, g["e"] / speed, [540 - w / 2 - CAP_BOX_PAD, top, 540 + w / 2 + CAP_BOX_PAD, top + h]))
    return out


def run_checks(S, P, final, work, faces, speed, ass_path, ov_setup):
    checks = {"screen_crop_ok": ov_setup.get("screen_crop_ok", True)}
    # 1. caption size, both styles, as burned
    ig = ov_setup.get("look") == "ig_native" or bool(ov_setup.get("igmode"))   # 28 Oct: ig_between reads as the ig look
    igb = bool(ov_setup.get("igmode")) and ov_setup.get("look") != "ig_native"
    for name, st in (("Cap", STYLE_CAP), ("Big", STYLE_BIG)):
        if ig:
            # the caption sticker is drawn on the overlay in Montserrat Bold at the smallest size the page used (52 px, 44
            # on a long line), capitals measured with PIL; the floor for this look is 34 px (the reel's own 36 on 1920)
            fs = int((ov_setup.get("setup") or {}).get("cap_font_min") or 52)
            bb = ImageFont.truetype(str(FONTDIR / "Montserrat-Bold.ttf"), fs).getbbox("H")
            checks[f"caption_{name}_px"] = bb[3] - bb[1]
            checks[f"caption_{name}_ok"] = (bb[3] - bb[1]) >= 34
            continue
        r = subprocess.run([sys.executable, str(SK / "check_caption_size.py"), "--style", st, "--fontsdir", str(FONTDIR)], capture_output=True, text=True, cwd=str(work))
        px = int(r.stdout.split("cap height ")[1].split("px")[0]) if "cap height" in r.stdout else 0
        floor = 47 if name == "Cap" else 53
        checks[f"caption_{name}_px"] = px
        checks[f"caption_{name}_ok"] = px >= floor
    # 2. safe area: the face-in-band test (mouth and chin above 1500) on the finished video; the ink test on OUR layer (the
    #    graphic PNGs), because a white shirt in sunlight reads as ink to the bright-pixel test on footage (guest X, 26 Oct)
    # ig_native: Instagram's own zones (the Instagram safe-zone teardown): the username and caption area from 86 % (1650), the button rail x > 930
    # 29 Oct (row 209): on ig_between the animation may use the top band down to 120 (Round-3 F, row 177), so the footage
    # test reads the same line the layer test does
    sa_args = ["--top", "120" if S.get("ig_between") else "220", "--bottom", "1640", "--right", "930", "--right-from", "1050"] if ig else []
    r = subprocess.run([sys.executable, str(SK / "check_safe_area.py")] + sa_args + [str(final)], capture_output=True, text=True, timeout=900)
    out_lines = r.stdout.strip().splitlines()
    checks["safe_area_report"] = out_lines[-6:]
    checks["safe_face_ok"] = not any("FAIL: the face" in ln for ln in out_lines) and any("face found in" in ln for ln in out_lines)
    # (builder B's open item, guest O's F2-hook2: check_safe_area's Haar read a 600 px "face" at y 1282 to 1906, her
    # neckline and chest, while the pipeline's own box put her face at 657 to 1186; read at full resolution on the 2.0 s
    # frame, the pipeline was right): a failing face box from the safe-area read that does not overlap, by a third of its
    # height, the pipeline's own face box on any panel on screen at that time is that tool misreading, and the
    # pipeline's geometry (mouth_ok, face_high_ok) decides; every override is listed in `safe_face_override`
    if not checks["safe_face_ok"] and any("face found in" in ln for ln in out_lines):
        fails, overrides = [], []
        for ln in out_lines:
            m = re.match(r"\s*([\d.]+)s\s+face\s+box y (-?\d+)\.\.(-?\d+)", ln)
            if not m:
                continue
            t, y0, y1 = float(m.group(1)), float(m.group(2)), float(m.group(3))
            boxes = []
            for it in P["items"]:
                if it["kind"] == "card" or not (it["out"] / speed - 0.05 <= t < (it["out"] + it["n"] / FPS) / speed + 0.05):
                    continue
                for ln_name in ([it["from"], it["to"]] if it["layout"] == "xfade" else [it["layout"]]):
                    for role, panel in panel_roles(dict(it, layout=ln_name), P["layout"][ln_name], P["people"]):
                        pp = P["people"][role]
                        if pp.get("medallion"):
                            continue
                        if pp.get("layouts"):
                            # 29 Oct (builder G, guest X's F2: a person with named crops gave the override no box, so a Haar
                            # misfire could never be told from a real low face): every named crop's box counts (the max
                            # overlap only grows, so the override stays the conservative side)
                            for nm, fb in faces[role]["by"].items():
                                boxes.append(face_on_frame(info(pp["file"]), fb["box"], panel, pp["crops"][nm], fb.get("low"), fb.get("high")))
                            continue
                        boxes.append(face_on_frame(info(pp["file"]), faces[role]["box"], panel, pp.get("crop"), faces[role].get("low"), faces[role].get("high"), bool(pp.get("crop_hard"))))
            ov = max([max(0.0, min(y1, g["bottom"]) - max(y0, g["top"])) / max(1, g["bottom"] - g["top"]) for g in boxes] or [1.0])
            (overrides if boxes and ov < 0.34 and all(g["mouth"] <= SAFE_BOTTOM for g in boxes) else fails).append(
                {"t": t, "tool_box_y": [y0, y1], "pipeline_boxes_y": [[g["top"], g["bottom"]] for g in boxes], "overlap": round(ov, 2)})
        if fails:
            checks["safe_face_ok"] = False
        elif overrides:
            checks["safe_face_ok"] = True
        checks["safe_face_override"] = overrides[:8]
    checks["safe_ink_footage_warning"] = [ln.strip() for ln in out_lines if ln.strip().endswith("outside the safe area")][:6]
    try:
        look = ov_setup["look"]
        if ig:
            raise _IgInk()
        fgc = {"ledger": "1C1C1E", "none": "1C1C1E", "whiteboard": "1C1C1E", "flat2d": "1C1C1E", "operator": "F2F3F4"}[look]
        acc = {"operator": ACCENT_HEX}.get(look, ACCENT_DARK_HEX)   # the looks page's accent ink (paths.py)
        bad = []
        seen = set()
        for png in sorted(ov_setup["seq"].glob("*.png")):
            ino = png.stat().st_ino
            if ino in seen:
                continue
            seen.add(ino)
            a = np.asarray(Image.open(png).convert("RGBA"))
            near = lambda hx: np.abs(a[:, :, :3].astype(int) - np.array([int(hx[i:i + 2], 16) for i in (0, 2, 4)])).sum(axis=2) < 60  # noqa: E731
            ink = (a[:, :, 3] > 200) & (near(fgc) | near(acc))
            # (builder A, cause 5): the safe frame's own top line, 230 (content/taste/shorts-formats.md: nothing that matters in
            # 0 to 230); the old 290 was the eyebrow's line, and the credit now sits on it (232 to 326) in the last 6 s
            top = int(ink[:230, :].sum()) - int(ink[:230, :140].sum())      # the whiteboard mark top-left is disposable by design
            rail = int(ink[960:1500, 940:].sum())
            if top > 400 or rail > 400:
                bad.append({"frame": png.name, "top_px": top, "rail_px": rail})
        checks["safe_ink_layer"] = bad[:8]
        checks["safe_ink_ok"] = not bad
    except _IgInk:
        # ig_native: any opaque pixel of our layer in the rail (x > 930, y 1050 to 1650), under 1650 or above 220
        bad, seen = [], set()
        for png in sorted(ov_setup["seq"].glob("*.png")):
            ino = png.stat().st_ino
            if ino in seen:
                continue
            seen.add(ino)
            rgba = np.asarray(Image.open(png).convert("RGBA"))
            al = rgba[:, :, 3] > 200
            if igb:
                # 29 Oct (row 206, guest E's M2-animAd: 129,600 px in the top 120 on every window frame): on ig_between the plain
                # ground band under the animation (near-black on the dark variants) is a background, not ink; only
                # pixels away from the band's own colour (read at x 540, y 4) count in the top 120
                g0 = rgba[0, 540, :3].astype(int)   # row 219: sampled on row 0
                flat = np.abs(rgba[:120, :, :3].astype(int) - g0).sum(axis=2) < 40
                al = al.copy()
                al[:120, :] &= ~flat
            # 28 Oct (polish, Round-3: on animated and tutorial shorts the top band may serve the animation): ig_between keeps
            # only the top 120 px clear, the ig_native look its 220
            rail, low, top = int(al[1050:1650, 931:].sum()), int(al[1650:, :].sum()), int(al[:(120 if igb else 220), :].sum())
            if rail > 200 or low > 200 or top > 200:
                bad.append({"frame": png.name, "rail_px": rail, "low_px": low, "top_px": top})
        checks["safe_ink_layer"] = bad[:8]
        checks["safe_ink_ok"] = not bad
    except Exception as e:  # noqa: BLE001
        checks["safe_ink_ok"] = False
        checks["safe_ink_error"] = str(e)[:200]
    checks["safe_area_ok"] = bool(checks["safe_face_ok"] and checks["safe_ink_ok"])
    # 3. the face bands by geometry (mouth never below 1500 on any panel)
    geom = {}
    for it in P["items"]:
        if it["kind"] == "card" or it["layout"] == "xfade":   # a crossfade's 2 framings are its neighbours'
            continue
        lay = P["layout"][it["layout"]]
        for role, panel in panel_roles(it, lay, P["people"]):
            p = P["people"][role]
            if p.get("layouts"):
                for nm, fb in faces[role]["by"].items():
                    g = face_on_frame(info(p["file"]), fb["box"], panel, p["crops"][nm], fb.get("low"), fb.get("high"))
                    g["panel_top"] = panel["y"]
                    geom[f"{it['layout']}:{role}:{nm}"] = g
                continue
            g = (medallion_geo(p, faces[role]["box"], panel)["frame"] if p.get("medallion") else
                 face_on_frame(info(p["file"]), faces[role]["box"], panel, p.get("crop"), faces[role].get("low"), faces[role].get("high"), bool(p.get("crop_hard"))))
            g["panel_top"] = panel["y"]
            geom[f"{it['layout']}:{role}"] = g
    checks["face_geometry"] = geom
    checks["mouth_ok"] = all(g["mouth"] <= SAFE_BOTTOM for g in geom.values())
    # 3b. the face is high: the chin (the box bottom) at or above 1200 on every panel that reaches the captions, and
    #     the box top at least 20 px under the panel's top (the head not cut), reviewers A, B1, B2 on 27 Oct
    # the hook's guest is listening for 3 s and a close webcam face cannot be small in a 2:1 panel (guest S: 54 % of the
    # panel at best), so the hook only asks that the chin stays inside the panel; the answer and duo panels ask for 1200
    # answer and duo: 1260 (a close webcam face in the 620 px graphic panel lands its chin at about 1230 with the head
    # whole: tutorial-5 M1 proof 03:02; the 2-line caption block starts about 1240, so the mouth stays clear)
    # duo (story-proof) keeps the hook's 2:1 guest panel for the whole short: a face that fills a 16:9 source (guest Z,
    # 578 px of 1080) cannot sit higher than a chin at about 1300 with the head whole, so the duo bound is 1320 (the
    # mouth stays above the 2-line caption block at about 1240; the chin may sit under its first line)
    hb = (1620, 1620, 1560) if ig else (1460, 1320, 1260)   # ig_native: the caption line sits at 1556 to 1620 under the mouth (mouth_ok keeps it above 1500), so the chin may sit at the line, as in the reel (15:02)

    def high_ok(k, g):
        if ig or k.startswith("hook:"):
            return g["bottom"] <= (hb[0] if k.startswith("hook:") else hb[1] if k.startswith("duo:") else hb[2])
        # (builder A, cause 2: faces 1.5x): on the drawn looks' answer panels the rule is the one the 1260 chin
        # stood for (the mouth above the 2-line caption block, y 1240); the chin may sit up to 1340 under a bigger face
        return g["mouth"] <= CAP_BLOCK_TOP + 2 and g["bottom"] <= 1340
    checks["face_high_ok"] = all(high_ok(k, g) for k, g in geom.items()) and all(g["top"] >= g["panel_top"] + 10 for g in geom.values())
    # 3c. 22:10 (builder A, cause 1: blur 26 to 32 % of the frame on 14 of 14 round-1 renders): blur only on the bottom
    #     20 %. Read off the geometry each piece was cut with: the bottom panel's real footage reaches BLUR_TOP (its
    #     blurred extension starts at or under 1536), a top panel's footage reaches its own foot (no blurred strip
    #     between the panels), no panel pillared over its own blur, and the run-over above a source's top is the ground
    #     (panel_chain pads it; it is never blur since 22:10)
    blur = {}
    for k, g in geom.items():
        lay_name = k.split(":")[0]
        pnl = P["layout"].get(lay_name) or {}
        ph = None
        for role_name in ("guest", "host"):
            if (pnl.get(role_name) or {}).get("y") == g["panel_top"]:
                ph = pnl[role_name]["h"]
        foot = ph is None or g["panel_top"] + ph >= VH - 1
        need = BLUR_TOP if foot else g["panel_top"] + ph
        if foot and g.get("need_used"):
            need = min(need, g["need_used"])   # 28 Oct: a solve that softened its reach to 1536 is read by its own number
        blur[k] = {"footage_to": g.get("foot_y", BLUR_TOP), "needs": need, "pillar": bool(g.get("pillar")), "ground_pillar": bool(g.get("ground_pillar")),
                   "ground_runover_px": g.get("top_h", 0),
                   "face_px": g.get("height", g["bottom"] - g["top"]), "legacy_crop": bool(g.get("legacy"))}
    checks["blur_geometry"] = blur
    checks["blur_bottom_ok"] = all(b["footage_to"] >= b["needs"] - 2 and not b["pillar"] for b in blur.values())
    # 3d. 22:25 (builder A, cause 5: guest C's and guest O's credits ran across their mouths, y 1112 to 1160): the credit's box
    #     (measured by the page in its shown state, `credit_box`) never meets a face box on any panel on screen in the
    #     last 6 s (each side of a crossfade counted)
    st0 = ov_setup.get("setup") or {}
    cb = st0.get("credit_box")
    total_out = P["total_n"] / FPS / speed
    # 29 Oct (builder G): the credit's 6 s end where the introduction starts (the pages' creditEnd), else at the end
    _is = (ov_setup.get("payload") or {}).get("intro_start")
    c_end = min(float(_is), total_out) if (_is is not None and float(_is) > 1) else total_out
    _ce = (ov_setup.get("payload") or {}).get("credit_end")   # 29 Oct (builder H): the guest's own last seconds
    if _ce is not None and float(_ce) > 1:
        c_end = min(float(_ce), total_out)
    hits = []
    if cb and S.get("credit"):
        cl, ctop, cr, cbot = cb
        for it in P["items"]:
            if it["kind"] == "card" or (it["out"] + it["n"] / FPS) / speed < c_end - 6.0 or it["out"] / speed >= c_end:
                continue
            lays = [it["from"], it["to"]] if it["layout"] == "xfade" else [it["layout"]]
            for ln in lays:
                lay = P["layout"][ln]
                for role, panel in panel_roles(dict(it, layout=ln), lay, P["people"]):
                    p = P["people"][role]
                    if p.get("layouts") or p.get("medallion"):
                        continue
                    g = face_on_frame(info(p["file"]), faces[role]["box"], panel, p.get("crop"), faces[role].get("low"), faces[role].get("high"), bool(p.get("crop_hard")))
                    if g["left"] < cr and g["right"] > cl and g["top"] < cbot and g["bottom"] > ctop:
                        hits.append({"out": round(it["out"] / speed, 2), "layout": ln, "role": role, "face": [g["left"], g["top"], g["right"], g["bottom"]]})
    checks["credit_box"] = cb
    checks["credit_face_hits"] = hits[:6]
    checks["credit_face_ok"] = not hits
    # 3d2. 23:20 (conductor, guest O's F3 r2): on the ig_native hook the host's crown sits 24 px or more under the title
    #      stack's measured foot (the page's title_bottom)
    if ig and P["hook_end"] > 0 and st0.get("title_bottom"):
        crowns = [g["crown"] for k, g in geom.items() if k.startswith("hook:") and g.get("panel_top") == 0 and "crown" in g]
        checks["title_crown"] = {"title_bottom": round(st0["title_bottom"]), "host_crown": min(crowns) if crowns else None}
        checks["title_crown_ok"] = bool(crowns) and min(crowns) >= st0["title_bottom"] + 24 - 2
    else:
        checks["title_crown_ok"] = True
    # 3e. 22:25 (builder A, cause 5): every piece of graphic type 44 px or more on the 1920 frame (the page reports the
    #     smallest font it set on the title, sub, graphic, stickers and credit, and which element: `type_min`)
    checks["graphic_type_min"] = st0.get("type_min")
    checks["graphic_type_where"] = st0.get("type_min_where")
    checks["graphic_type_ok"] = st0.get("type_min") is None or float(st0["type_min"]) >= 44 - 0.01
    # 3f. 22:25 (builder A, cause 3): no caption line of 1 word and none on screen under 0.3 s (after the speed)
    bad_lines = caption_line_faults(ov_setup.get("groups") or [], ov_setup.get("ig_caps"), speed)
    checks["caption_line_faults"] = bad_lines[:10]
    checks["caption_lines_ok"] = not bad_lines
    # 3g. 23:10 (conductor): no caption box meets a visible face box. The face box is the Haar box from the brow to the
    #     lower lip (0.85 of its height): the chin under the caption block is the house layout (mouth over 1240 on the
    #     drawn answer, the sticker under the mouth on ig_native), a caption over eyes, nose or mouth is the fault
    capb = caption_boxes(ov_setup.get("groups") or [], speed, ov_setup.get("ig_caps"))
    face_hits = []
    for it in P["items"]:
        if it["kind"] == "card":
            continue
        i0, i1 = it["out"] / speed, (it["out"] + it["n"] / FPS) / speed
        caps_here = [c for c in capb if min(c[1], i1) - max(c[0], i0) > 0.02]
        if not caps_here:
            continue
        for ln in ([it["from"], it["to"]] if it["layout"] == "xfade" else [it["layout"]]):
            for role, panel in panel_roles(dict(it, layout=ln), P["layout"][ln], P["people"]):
                p = P["people"][role]
                if p.get("layouts") or p.get("medallion"):
                    continue
                g = face_on_frame(info(p["file"]), faces[role]["box"], panel, p.get("crop"), faces[role].get("low"), faces[role].get("high"), bool(p.get("crop_hard")))
                fb = [g["left"], g["top"], g["right"], g["top"] + 0.85 * (g["bottom"] - g["top"])]
                for s0, e0, cb in caps_here:
                    if cb[0] < fb[2] and cb[2] > fb[0] and cb[1] < fb[3] and cb[3] > fb[1]:
                        face_hits.append({"t": round(max(s0, i0), 2), "layout": ln, "role": role, "caption": [round(v) for v in cb], "face": [round(v) for v in fb]})
    checks["caption_face_hits"] = face_hits[:8]
    checks["caption_face_ok"] = not face_hits
    # 3h. 23:10 (conductor): a card is never up more than about 3 s past its last key, the closing 3 s aside
    pl = ov_setup.get("payload") or {}
    kts = sorted(k[1] for k in ((pl.get("graphic") or {}).get("keys") or []))
    still = []
    for w0, w1 in pl.get("card_windows") or []:
        ks_in = [k for k in kts if w0 - 0.05 <= k <= w1]
        end = w1 if w1 < pl.get("duration", 0) - 0.05 else w1 - 3.0
        last = max(ks_in) if ks_in else w0
        if end - last > 3.4:
            still.append({"window": [w0, w1], "last_key": round(last, 2), "still_s": round(end - last, 2)})
    checks["card_still"] = still
    checks["card_still_ok"] = not still
    # 4. speaker proof on the answer pieces: the mouth moves on the speaker's own track, each piece against the piece of the
    #    same speaker with the most motion (calibration), on the source file with the measured face box. Since 27 Oct
    #    the lip score is read together with the word files: a piece whose speaker's own words cover it (and nobody else's
    #    do) is that speaker's whatever the lips scored (a soft line, a sub-second piece, a face off frame on a tutorial),
    #    and a piece another person's words cover is the WRONG speaker whatever the lips scored (guest X's after-wave1-02 carried a
    #    6 s host line as a guest piece: the lips caught it, the words agree). A one-person spec cannot name the wrong
    #    person, so its lip scores are recorded as a note and never fail it (the face is off frame on screen pieces).
    sp = {}
    try:
        by = {}
        for it in (P.get("runs") or P["items"]):   # the runs (a card split's parts are one stretch of tape)
            if it["kind"] == "answer":
                by.setdefault(it["speaker"], []).append(it)
        single = len(P["people"]) == 1

        def cov(role, a, b):
            p = P["people"][role]
            off = float(p.get("offset") or 0.0)
            ws = load_words(p["words"], p.get("scribe_speaker"), p.get("words_offset") or 0.0)
            c = sum(max(0.0, min(b + off, w["e"]) - max(a + off, w["s"])) for w in ws if w["e"] > a + off and w["s"] < b + off)
            return c / max(0.2, b - a)

        for role, its in by.items():
            p = P["people"][role]
            off = float(p.get("offset") or 0.0)
            fx, fy, fw, fh = [int(v) for v in faces[role]["box"]]
            scores, words = [], []
            for it in its:
                a, b = it["a"] + off, min(it["b"], it["a"] + 6.0) + off
                r = subprocess.run([sys.executable, str(SK / "verify_speaker.py"), p["file"], "--range", f"{a:.2f}-{b:.2f}", "--calibration", f"{a:.2f}-{b:.2f}",
                                    "--face", f"{fx},{fy},{fw},{fh}", "--fps", "8"], capture_output=True, text=True, timeout=600)
                m = re.search(r"range\s+\S+ : score ([\d.]+)", r.stdout)
                scores.append((round(it["a"], 2), float(m.group(1)) if m else None))
                own = cov(role, it["a"], it["b"])
                other = max([cov(o, it["a"], it["b"]) for o in P["people"] if o != role] or [0.0])
                words.append((round(it["a"], 2), round(own, 2), round(other, 2), round(it["b"] - it["a"], 2)))
            vals = [s for _, s in scores if s is not None]
            cal = max(vals) if vals else 0
            lips = [t for t, s in scores if s is not None and cal >= 1.0 and s < cal / 2]
            wrong = [t for t, own, other, dur in words if other >= 0.5 and own < 0.2]
            # cleared by the words: the speaker's own words cover the piece and nobody else's do, or the piece is a cut-in
            # under 1.5 s where the other voice overlaps (guest Y's F2 03:21: a 1.1 s host line over the cohost's laugh)
            cleared = [t for t, own, other, dur in words if own >= 0.45 and (other <= 0.30 or dur < 1.5)]
            suspect = sorted(set(wrong) | {t for t in lips if t not in cleared})
            sp[role] = {"scores": scores, "calibration": cal, "words": words, "lips_low": lips, "wrong_speaker": wrong,
                        "suspect": suspect if not single else [], "note": "one-person spec: lips recorded, never a fail" if single else ""}
            if single and suspect:
                sp[role]["lips_low_note"] = suspect
        checks["speaker"] = sp
        checks["speaker_ok"] = all(not v["suspect"] for v in sp.values())
    except Exception as e:  # noqa: BLE001
        checks["speaker"] = {"error": str(e)[:300]}
        checks["speaker_ok"] = False
    # 4b. caption coverage: every spoken piece has words under it (a word file on the wrong clock renders a silent-looking
    #     short: guest Z's wave1-04, 27 Oct)
    spoken = [(it["out"] / speed, (it["out"] + it["n"] / FPS) / speed) for it in (P.get("runs") or P["items"]) if it["kind"] != "card"]
    covered = 0.0
    uncovered = []
    for a, b in spoken:
        c = sum(max(0.0, min(b, g["e"] / speed) - max(a, g["s"] / speed)) for g in ov_setup.get("groups", []))
        covered += c
        if (b - a) > 1.5 and c < 0.3 * (b - a):
            uncovered.append([round(a, 2), round(b, 2), round(c, 2)])
    total_spoken = sum(b - a for a, b in spoken) or 1.0
    checks["caption_coverage"] = round(covered / total_spoken, 3)
    checks["caption_uncovered_pieces"] = uncovered[:8]
    checks["caption_coverage_ok"] = not uncovered and checks["caption_coverage"] >= 0.5
    # 5. duration, peak, loudness
    secs = duration(final)
    checks["seconds"] = round(secs, 2)
    checks["under_60_ok"] = secs <= 60.0 or bool(S.get("notes"))
    checks["true_peak_dbtp"] = true_peak(final)
    checks["true_peak_ok"] = checks["true_peak_dbtp"] <= -1.4
    checks["lufs"] = lufs_of(final)
    # 6a. the title fits: 2 lines inside the band, above the hook's host panel (516) or the answer band (940), no glyph clipped
    try:
        st = ov_setup.get("setup") or {}
        if ig:
            # ig_native: the title stickers inside y 220 to 560 and x 60 to 930 (the spec proposal's checks row), nothing clipped
            checks["title"] = {"top": st.get("title_top"), "bottom": st.get("title_bottom"), "left": st.get("title_left"), "right": st.get("title_right")}
            checks["title_fits_ok"] = bool((st.get("title_top") or 0) >= 220 and (st.get("title_bottom") or 9999) <= 560
                                           and (st.get("title_left") or 0) >= 60 and (st.get("title_right") or 9999) <= 1020)
            raise _IgInk()
        band_h = P["layout"]["hook"]["top_band_h"] if P["hook_end"] > 0 else P["layout"]["answer"]["top_band_h"]
        low = st.get("title_bottom") or 9999
        sub_low = st.get("sub_bottom") or 0
        a_band = P["layout"]["answer"]["top_band_h"]
        ov0 = np.asarray(Image.open(ov_setup["seq"] / "00000.png").convert("RGBA"))
        fgc = {"ledger": "1C1C1E", "none": "1C1C1E", "whiteboard": "1C1C1E", "flat2d": "1C1C1E", "operator": "F2F3F4"}[ov_setup["look"]]
        acc = {"operator": ACCENT_HEX}.get(ov_setup["look"], ACCENT_DARK_HEX)
        near = lambda hx: np.abs(ov0[:, :, :3].astype(int) - np.array([int(hx[i:i + 2], 16) for i in (0, 2, 4)])).sum(axis=2) < 60  # noqa: E731
        ink = (ov0[:, :, 3] > 200) & (near(fgc) | near(acc))
        edge = int(ink[band_h - 3:band_h, 40:1040].sum() + ink[290:band_h, 0:6].sum() + ink[290:band_h, 1074:1080].sum())
        checks["title"] = {"top": st.get("title_top"), "bottom": st.get("title_bottom"), "size_px": st.get("title_size"),
                           "overflow": st.get("title_overflow"), "band_h": band_h, "edge_ink_px": edge}
        # 29 Oct (builder G, guest C's M2 and guest O's M1-animB title_fits_ok false at title_top 260): row 176 raised the drawn
        # looks' #title to 260 on the creator's Round-3 word (guest O's D: the 2 top titles higher); the floor is the platform's top zone
        # (220, the ig check's own), no longer the old title's 290
        checks["title_fits_ok"] = bool(st.get("title_top", 0) >= 220 and low <= band_h - 8 and sub_low <= a_band - 8 and not st.get("title_overflow") and not st.get("sub_overflow") and edge < 40)
        checks["sub_text"] = st.get("sub_text") or ""
    except _IgInk:
        pass
    except Exception as e:  # noqa: BLE001
        checks["title_fits_ok"] = False
        checks["title_fits_error"] = str(e)[:200]
    # 6. first frame is the designed title frame: the top band of frame 0 against the layer's own t=0 PNG
    try:
        f0 = work / f"frame0-{ov_setup.get('tag') or ov_setup['look']}.png"
        run([FF, "-y", "-v", "error", "-i", str(final), "-frames:v", "1", str(f0)], timeout=120, label="frame0")
        a = np.asarray(Image.open(f0).convert("RGB")).astype(np.int16)[300:520, 60:1020]
        ov0 = Image.open(ov_setup["seq"] / "00000.png").convert("RGBA")
        ground = tuple(int(GROUND[ov_setup["look"]][i:i + 2], 16) for i in (0, 2, 4))
        bg = Image.new("RGBA", ov0.size, ground + (255,))
        comp = np.asarray(Image.alpha_composite(bg, ov0).convert("RGB")).astype(np.int16)[300:520, 60:1020]
        if ig:
            # full bleed: only the sticker pixels (opaque on the layer) are the designed frame; the footage shows around them
            m = np.asarray(ov0)[300:520, 60:1020, 3] > 240
            diff = float(np.abs(a - comp)[m].mean()) if m.any() else 99.0
        else:
            diff = float(np.abs(a - comp).mean())
        checks["title_frame_diff"] = round(diff, 2)
        checks["title_frame_ok"] = diff < 12.0
    except Exception as e:  # noqa: BLE001
        checks["title_frame_ok"] = False
        checks["title_frame_error"] = str(e)[:200]
    checks["ok"] = all(checks.get(k, False) for k in ("caption_Cap_ok", "caption_Big_ok", "safe_area_ok", "mouth_ok", "face_high_ok", "screen_crop_ok", "under_60_ok", "true_peak_ok", "title_frame_ok", "title_fits_ok", "speaker_ok", "caption_coverage_ok",
                                                   "blur_bottom_ok", "credit_face_ok", "graphic_type_ok", "caption_lines_ok",
                                                   "caption_face_ok", "card_still_ok", "title_crown_ok"))
    return checks


# ---------------------------------------------------------------- build
def build(spec_path, look_override=None, force=False):
    spec_path = PATHS.remap(str(spec_path))   # the queue files may hold spec paths as another machine spells them (paths.py)
    S = load_spec(spec_path)
    sid = S["id"]
    look = look_override or S.get("look") or "none"
    tag = sid if not look_override or look_override == S.get("look") else f"{sid}-cmp-{look_override}"
    work = WORKROOT / sid
    work.mkdir(parents=True, exist_ok=True)
    outdir = OUT / S["slug"]
    outdir.mkdir(parents=True, exist_ok=True)
    final = outdir / f"{tag}.mp4"
    t0 = time.time()
    log(work, f"build {tag} look={look} from {spec_path}")
    free_gb = PATHS.free_gb()
    if free_gb < 3:
        raise RuntimeError(f"disk: {free_gb:.1f} GB free, refusing to render (floor 3 GB)")
    if final.exists() and not force:
        log(work, f"exists, skipping: {final}")
        return final
    lock = work / f"building-{tag}.json"
    lock.write_text(json.dumps({"pid": os.getpid(), "tag": tag, "look": look, "started": dt.datetime.now().isoformat(timespec="seconds")}))
    try:
        return _build(S, spec_path, sid, look, tag, work, outdir, final, t0)
    finally:
        try:
            lock.unlink()
        except OSError:
            pass


def _build(S, spec_path, sid, look, tag, work, outdir, final, t0):
    speed = spec_speed(S)
    try:
        S = retime(S, work, spec_path)
        if S.get("retime"):
            log(work, f"retime: {S['retime']}")
    except RetimeFailed as e:
        log(work, f"retime failed: {e}")
        with open(RESULTS, "a") as f:
            f.write(json.dumps({"id": tag, "spec": str(PATHS.canon(str(spec_path))), "status": "retime-failed", "reason": str(e), "path": None,
                                "when": dt.datetime.now().strftime("%Y-%m-%d %H:%M")}) + "\n")
        raise SystemExit(2)
    try:
        return _build2(S, spec_path, sid, look, tag, work, outdir, final, t0, speed)
    except NoFaceBox as e:
        log(work, f"no face box: {e}")
        with open(RESULTS, "a") as f:
            f.write(json.dumps({"id": tag, "spec": str(PATHS.canon(str(spec_path))), "status": "no-face-box", "reason": str(e), "path": None,
                                "when": dt.datetime.now().strftime("%Y-%m-%d %H:%M")}) + "\n")
        raise SystemExit(2)


def _build2(S, spec_path, sid, look, tag, work, outdir, final, t0, speed):
    S["_look"] = look   # layout_for reads it (ig_native is full bleed); never written back to the spec
    P = plan(S, work)
    (work / "plan.json").write_text(json.dumps({k: v for k, v in P.items() if k not in ("words", "track")}, indent=1, default=str))
    log(work, f"plan: {len(P['items'])} pieces, {P['total_n'] / FPS:.2f} s at 1.0x, hook_end {P['hook_end']:.2f}")
    # faces
    faces = {}
    for role, p in P["people"].items():
        pcs = [(it["a"], it["b"]) for it in P["items"] if it["kind"] != "card" and (it["speaker"] == role or it["layout"] == "hook")]
        if not pcs:
            pcs = [(it["a"], it["b"]) for it in P["items"] if it["kind"] != "card"]
        faces[role] = layout_faces(role, p, pcs, work) if p.get("layouts") else face_box(role, p, pcs, work, role)
        log(work, f"face {role}: {[round(v) for v in faces[role]['box']]} ({faces[role]['method']})")
    ground = GROUND.get(look, GROUND["none"])
    if S.get("anim") and (S.get("anim_dark") or (str(S.get("anim")).upper() == "A" and not S.get("anim_light"))):
        ground = "030405"   # anim_looks.html DARK.ground: the band under the animation on the dark variants (28 Oct)
    igmode = is_igmode(S, look)
    if not igmode:
        fit = drawn_hook_fit(S, P, faces)   # 29 Oct (builder H, guest C's M2 r3): the drawn looks' seam search and question flip
        if fit == "flip":
            S["question_full"] = True
            P = plan(S, work)
            (work / "plan.json").write_text(json.dumps({k: v for k, v in P.items() if k not in ("words", "track")}, indent=1, default=str))
            log(work, f"question full frame (the drawn stacked faces stay under {IG_Q_FULL_BELOW} px at every seam): re-planned, {len(P['items'])} pieces")
        elif fit:
            log(work, f"drawn hook {fit} (the smaller stacked face lifted to {IG_Q_FULL_BELOW} px or more)")
    if igmode:
        seam = ig_hook_seam(P, faces)
        if seam:
            log(work, f"ig hook seam at y {seam} (the host's head from the title's foot to its chin at full width)")
        if ig_question_full(S, P, faces):
            # 29 Oct (builder G): the stacked question cannot hold both faces at IG_Q_FULL_BELOW: full frame instead
            S["question_full"] = True
            P = plan(S, work)
            (work / "plan.json").write_text(json.dumps({k: v for k, v in P.items() if k not in ("words", "track")}, indent=1, default=str))
            log(work, f"question full frame (the stacked faces fell under {IG_Q_FULL_BELOW} px): re-planned, {len(P['items'])} pieces")
    # cut
    pieces = [render_piece(S, P, it, {r: faces[r] for r in faces}, work, ground) for it in P["items"]]
    cut = concat_pieces(pieces, work, f"{look}")
    log(work, f"cut: {cut.name} {duration(cut):.2f} s")
    # audio
    audio, am = audio_take(S, P, work)
    log(work, f"audio: in {am['input_i']} LUFS, true peak {am['true_peak_dbtp']} dBTP, {am['secs']:.2f} s")
    # captions
    groups = caption_groups(P, S)
    if not igmode:
        hy = hook_caption_y(P, faces)
        for g in groups:
            if g.get("hook") and hy:
                g["pos_y"] = hy
        log(work, f"hook caption centred at y {hy}")
        nmv = caption_clear_chin(P, faces, groups)   # 29 Oct (builder H, guest C's M2 r3)
        if nmv:
            log(work, f"captions: {nmv} blocks set lower to clear a chin (box from the chin plus 8, foot at most {CAP_FOOT_MAX})")
    ass = work / f"captions-{key_of([ (g['s'], g['e'], [w[0] for w in g['w']], g.get('pos_y')) for g in groups] + [speed])}.ass"
    ass.write_text(ass_text([] if igmode else groups, speed, boxes=True))   # ig_native (and ig_between): the caption sticker is on the overlay
    log(work, f"captions: {len(groups)} groups -> {ass.name}")
    # overlay
    nfr_out = int(round(P["total_n"] / speed))
    payload = overlay_payload(S, P, look, speed)
    if igmode:
        payload["captions"] = ig_chunks(groups, speed)
    (work / f"payload-{look}.json").write_text(json.dumps(payload, indent=1))
    seq, uniq, setup = render_overlay(payload, nfr_out, work, look)
    log(work, f"overlay: {uniq} unique frames of {nfr_out} -> {seq.name}")
    # screen (tutorials): the screen video inside the window hole during its pieces
    screen_fc, screen_inputs = "", []
    scr = S.get("screen")
    hole = (setup or {}).get("screen_hole") if setup else None
    screen_crop_ok = True
    if scr and scr.get("file") and not scr.get("crop") and not scr.get("draw_steps"):   # draw_steps never composites the raw frame
        screen_crop_ok = False   # reviewer C2: a screen file with no crop carries the raw frame (paths, private UI)
        scr = None
    if scr and not usable_screen(S):
        scr = None   # an unmeasured crop: the window draws the steps instead (usable_screen)
    if scr and scr.get("file") and hole:
        hx, hy, hw, hh = hole
        for i, (a, b) in enumerate(scr.get("pieces") or []):
            pass  # screen pieces are composited by time below (one input, enable windows)
        screen_inputs = ["-i", scr["file"]]
        crop = scr.get("crop")
        cr = f"crop={crop[2]}:{crop[3]}:{crop[0]}:{crop[1]}," if crop else ""
        screen_fc = f"[2:v]{cr}scale={hw}:{hh}:force_original_aspect_ratio=increase,crop={hw}:{hh},setsar=1,fps={FPS}[scr];"
    # compose: speed, overlay, captions, audio
    tempo_v = f"setpts=PTS/{speed:.4f}," if abs(speed - 1) > 1e-3 else ""
    fc = f"[0:v]{tempo_v}fps={FPS},format=yuv420p[b];"
    cur = "b"
    if screen_fc:
        # the screen plays during the answer pieces where the spec's screen.pieces fall (output time), under the layer
        wins = []
        for it in P["items"]:
            if it["kind"] == "answer":
                wins.append((it["out"] / speed, (it["out"] + it["n"] / FPS) / speed))
        en = "+".join(f"between(t,{a:.3f},{b:.3f})" for a, b in wins) or "0"
        fc += screen_fc + f"[{cur}][scr]overlay={hx}:{hy}:enable='{en}'[bs];"
        cur = "bs"
    fc += f"[1:v]format=rgba[ov];[{cur}][ov]overlay=0:0:shortest=1:format=auto[m];[m]ass='{ass}':fontsdir='{FONTDIR}',format=yuv420p[v]"
    tmp = str(final) + ".part.mp4"
    run([FF, "-y", "-v", "error", "-i", str(cut), "-framerate", str(FPS), "-i", str(seq / "%05d.png")] + screen_inputs + ["-i", str(audio),
         "-filter_complex", fc, "-map", "[v]", "-map", f"{3 if screen_inputs else 2}:a", "-frames:v", str(nfr_out), "-r", str(FPS)] + venc(final=True) +
        AAC + ["-movflags", "+faststart", "-t", f"{nfr_out / FPS:.3f}", tmp],
        timeout=min(3600, 300 + 10 * nfr_out / FPS), label="compose")
    os.replace(tmp, final)
    lu, tp = lufs_of(final), true_peak(final)
    if (lu is not None and abs(lu + 14.0) > 0.5) or tp > -1.4:
        # the encoded file missed (the wav was corrected in audio_take, so this is rare): the audio is re-cut from the
        # wav, not from the AAC, so there is still only one AAC generation; the video stream is copied
        lv = str(final) + ".lvl.mp4"
        run([FF, "-y", "-v", "error", "-i", str(final), "-i", str(audio), "-map", "0:v", "-map", "1:a", "-c:v", "copy",
             "-af", f"volume={-14.0 - (lu if lu is not None else -14.0):.2f}dB,aresample=192000,{LIMITER},aresample=48000"] + AAC + ["-movflags", "+faststart", "-t", f"{nfr_out / FPS:.3f}", lv], timeout=600, label="level")
        os.replace(lv, final)
        log(work, f"loudness {lu} LUFS / {tp} dBTP -> re-cut from the wav (second pass)")
    log(work, f"compose: {final} {duration(final):.2f} s")
    try:
        os.remove(str(cut))   # the concat copy of the pieces (the pieces stay cached); Python, never a shell rm
        (work / f"cut-{look}.key").unlink(missing_ok=True)
    except OSError:
        pass
    # write: poster, sheet, checks, before copy, results row
    poster = outdir / f"{tag}-poster.jpg"
    run([FF, "-y", "-v", "error", "-i", str(final), "-frames:v", "1", "-q:v", "2", str(poster)], timeout=120, label="poster")
    sheet = outdir / f"{tag}-sheet.jpg"
    contact_sheet(final, P, speed, work / f"sheet-{look}.jpg")
    shutil.copyfile(work / f"sheet-{look}.jpg", sheet)
    checks = run_checks(S, P, final, work, faces, speed, ass, {"seq": seq, "look": look, "setup": setup, "groups": groups, "tag": tag, "screen_crop_ok": screen_crop_ok,
                                                       "ig_caps": payload.get("captions") if igmode else None, "payload": payload, "igmode": igmode})
    checks["unique_overlay_frames"] = uniq
    checks["screen_crop_ok"] = screen_crop_ok
    checks["caption_groups"] = len(groups)
    checks["caption_text"] = " ".join(w[0] for g in groups for w in g["w"])
    checks["plan"] = [{"kind": it["kind"], "speaker": it["speaker"], "a": round(it["a"], 3), "b": round(it["b"], 3), "out": round(it["out"] / speed, 3)} for it in P["items"]]
    (outdir / f"{tag}-checks.json").write_text(json.dumps(checks, indent=1, default=str))
    if S.get("kind") == "after" and (S.get("after_of") or {}).get("posted_file"):
        pf = Path(S["after_of"]["posted_file"])
        if pf.exists():
            before = outdir / f"{tag}-before.mp4"
            if not before.exists() and not before.is_symlink():
                os.symlink(str(pf), str(before))   # a link, not a 50 MB copy: the disk is at 98 % (26 Oct)
    row = {"id": tag, "spec": PATHS.canon(str(spec_path)), "status": "ok" if checks["ok"] else "checks-failed", "seconds": checks["seconds"],
           "checks": {k: v for k, v in checks.items() if k.endswith("_ok") or k in ("caption_Cap_px", "caption_Big_px", "true_peak_dbtp", "lufs", "title_frame_diff")},
           "path": PATHS.canon(str(final)), "when": dt.datetime.now().strftime("%Y-%m-%d %H:%M"), "build_secs": round(time.time() - t0), "look": look}
    with open(RESULTS, "a") as f:
        f.write(json.dumps(row) + "\n")
    log(work, f"done {tag}: {row['status']} in {row['build_secs']} s; checks {row['checks']}")
    if checks["ok"]:
        prune_work(work, look)
    if not checks["ok"]:
        failed = [k for k in checks if k.endswith("_ok") and not checks[k]]
        raise SystemExit(f"checks failed for {tag}: {failed} (see {outdir / (tag + '-checks.json')})")
    return final


def other_builds_alive(work, own_pid=None):
    """the lock files of sibling builds of the same spec (the compare look) whose process is still alive."""
    alive = []
    for lk in work.glob("building-*.json"):
        try:
            d = json.loads(lk.read_text())
            if int(d["pid"]) == (own_pid or os.getpid()):
                continue
            os.kill(int(d["pid"]), 0)
            alive.append(d)
        except Exception:
            try:
                lk.unlink()
            except OSError:
                pass
    return alive


def prune_work(work, look=None):
    """after a short passes: this look's overlay frames, sheet frames and cut go; the pieces, the audio takes and the face
    frames (shared by the compare look) go only when no sibling build of the spec is alive (27 Oct 02:40: the primary's
    prune wiped the compare render's frames mid-build on 12 specs and failed 3 of them outright). The plan, the faces,
    the captions, the log and the sheet stay. Python removes, every path checked to sit under WORKROOT."""
    work = Path(work).resolve()
    assert str(work).startswith(str(WORKROOT.resolve()) + "/"), work
    freed = 0
    own = [work.glob(f"sheet-frames-sheet-{look}/*.jpg"), work.glob(f"frame0-*{look}.png"), work.glob(f"cut-{look}.mp4")] if look else []
    shared = [work.glob("piece-*.mp4"), work.glob("aud-*.wav"), work.glob("audio-*.wav"), work.glob("faces/*.png"), work.glob("safe/*.png")]
    sib = other_builds_alive(work)
    files = [f for g in own for f in g]
    if not sib:
        files += [f for g in shared for f in g]
    for f in files:
        try:
            freed += f.stat().st_size
            os.remove(f)
        except OSError:
            pass
    dirs = list(work.glob(f"ov-{look}-*")) if look else []
    if not sib:
        dirs += [work / "safe"] + ([] if look else list(work.glob("ov-*")))
    for d in dirs:
        if d.is_dir():
            try:
                freed += sum(x.stat().st_size for x in d.iterdir() if x.is_file())
                shutil.rmtree(d)
            except OSError:
                pass
    log(work, f"pruned {freed / 1e6:.0f} MB of intermediates" + (f" (a sibling build is alive: {[s['tag'] for s in sib]}, shared pieces kept)" if sib else ""))


def load_spec(path):
    """a spec as this machine sees it: every path it holds remapped (paths.py); the file on disk is never rewritten here."""
    return PATHS.remap_obj(json.loads(Path(PATHS.remap(str(path))).read_text()))


def all_specs():
    """every spec under SPECS/<slug>/, never a tutorial sidecar (<id>-tutorial.json sits beside its spec)."""
    return sorted(p for p in SPECS.glob("*/*.json") if not p.name.endswith("-tutorial.json"))


def status():
    rows = {}
    if RESULTS.exists():
        for ln in RESULTS.read_text().splitlines():
            try:
                r = json.loads(ln)
                rows[r["id"]] = r
            except Exception:
                pass
    now = dt.datetime.now()
    done, failed, running, todo = [], [], [], []
    blocked, norow, checks_failed = [], [], []
    for sp in all_specs():
        S = load_spec(sp)
        sid = S["id"]
        if S.get("blocked_on"):
            blocked.append(f"{sid}  blocked on: {S['blocked_on']}")
            continue
        looks = [S.get("look") or "none"] + ([S["compare_look"]] if S.get("compare_look") else [])
        for lk in looks:
            tag = sid if lk == (S.get("look") or "none") else f"{sid}-cmp-{lk}"
            final = OUT / S["slug"] / f"{tag}.mp4"
            rd = PATHS.WORKROOT.parent / "renders" / tag   # the render_detached state folder (pid, exit) of this tag
            if final.exists():
                r = rows.get(tag)
                if r is None or PATHS.remap(r.get("path")) != str(final):
                    # a file with no results row: the build was stopped after compose and before its checks (the 2-hour
                    # pause of 27 Oct left 5 of these); the runner re-renders it with --force
                    norow.append(f"{tag}  file written {dt.datetime.fromtimestamp(final.stat().st_mtime):%H:%M}, no checks row")
                    continue
                if (rd / "pid").exists() and not (rd / "exit").exists():
                    try:
                        os.kill(int((rd / "pid").read_text().strip()), 0)
                        running.append(f"{tag}  (re-render) since {dt.datetime.fromtimestamp((rd / 'pid').stat().st_mtime):%H:%M}")
                        continue
                    except Exception:
                        pass
                line = f"{tag}  {r.get('seconds', '?')} s  {r.get('status', 'ok')}  {r.get('when', '')}"
                if r.get("status") == "ok":
                    done.append(line)
                else:
                    fails = [k for k, v in (r.get("checks") or {}).items() if k.endswith("_ok") and v is False]
                    checks_failed.append(f"{line}  {fails}")
            elif (rd / "pid").exists() and not (rd / "exit").exists():
                try:
                    pid = int((rd / "pid").read_text().strip())
                    os.kill(pid, 0)
                    running.append(f"{tag}  since {dt.datetime.fromtimestamp((rd / 'pid').stat().st_mtime):%H:%M}")
                    continue
                except Exception:
                    pass
                failed.append(f"{tag}  (died, no exit file)")
            elif (rd / "exit").exists() and (rd / "exit").read_text().strip() not in ("0", ""):
                failed.append(f"{tag}  exit {(rd / 'exit').read_text().strip()[:30]}")
            else:
                todo.append(tag)
    per = [r["build_secs"] for r in rows.values() if r.get("build_secs")]
    avg = sum(per) / len(per) if per else 240
    eta = now + dt.timedelta(seconds=avg * max(0, len(todo) + len(running) + len(norow)) / 3)
    print(f"{now:%Y-%m-%d %H:%M}  ok {len(done)}  checks-failed {len(checks_failed)}  no-checks-row {len(norow)}  running {len(running)}  failed {len(failed)}  "
          f"to go {len(todo)}  blocked {len(blocked)}  (avg {avg:.0f} s a short, 3 at a time; expected finish about {eta:%H:%M})")
    for name, lst in (("OK", done), ("CHECKS FAILED (the file exists; which checks)", checks_failed), ("NO CHECKS ROW (re-rendered with --force by the runner)", norow),
                      ("RUNNING", running), ("FAILED", failed), ("TO GO", todo), ("BLOCKED (spec says blocked_on)", blocked)):
        if lst:
            print(f"\n{name}")
            for x in lst:
                print("  " + x)


def selftest():
    if not MONT.is_file():
        print(f"selftest needs the caption font {MONT.name} in {FONTDIR} (set SHORTS_FONT_DIR or config font_dir): not found.")
        raise SystemExit(2)
    print("calibration ratio at 104:", round(calib_ratio(104), 3), "at 118:", round(calib_ratio(118), 3))
    for name, st in (("Cap", STYLE_CAP), ("Big", STYLE_BIG)):
        r = subprocess.run([sys.executable, str(SK / "check_caption_size.py"), "--style", st, "--fontsdir", str(FONTDIR)], capture_output=True, text=True, cwd=str(WORKROOT))
        print(name, r.stdout.strip())
    ws = [{"t": w, "s": i, "e": i + 0.5} for i, w in enumerate("We hire three or four people for the desk twenty percent".split())]
    print([w["t"] for w in digits(ws)])
    print(two_lines("It's not which tool you pick, it's, do you actually check it".split(), 104))
    # (builder A): the round-1 causes as cases; any failure raises
    fails = []

    def grp(words, t0=0.0, step=0.3, spk="guest", e=None):
        w = [(t, t0 + i * step, t0 + i * step + step * 0.8) for i, t in enumerate(words)]
        return {"s": t0, "e": e if e is not None else w[-1][2] + 0.1, "w": w, "lines": [list(range(len(words)))], "style": "Cap", "spk": spk}

    def lines_of(caps):
        return [" ".join(x[0] for x in c["w"]) for c in caps]
    # (the test sentences are invented, the same shape as the tape that broke each rule: word lengths, punctuation, timing)
    # cause 3, ig_native: 'deposits over' + 'disputes.' one line (guest C's F3-hook2 3.5 s)
    c1 = lines_of(ig_chunks([grp("There are owners that have lost their deposits over disputes.".split())], 1.25))
    if "deposits over disputes." not in c1:
        fails.append(f"deposits over disputes.: {c1}")
    # 'say,' on screen 0.07 s (guest O's F2 30.58 s) is merged into its neighbour
    g_say = grp("So the coach would".split(), 0.0)
    g_say["w"].append(("say,", 1.30, 1.36))
    g_say["e"] = 1.37
    caps = ig_chunks([g_say, grp("this is the plan.".split(), 1.45)], 1.1)
    if any(lines == "say," for lines in lines_of(caps)) or any((c["e"] - c["s"]) < MIN_LINE_S - 0.005 for c in caps):
        fails.append(f"say, 0.07 s: {[(lines_of([c])[0], round(c['e'] - c['s'], 2)) for c in caps]}")
    # a hyphenated word + the next word one line, 'teacher-student' + 'agreement.' (guest C's F3 1.0 to 1.5 s)
    c3 = lines_of(ig_chunks([grp(["teacher-student", "agreement."], 0.0, 0.5)], 1.25))
    if c3 != ["teacher-student agreement."]:
        fails.append(f"teacher-student agreement.: {c3}")
    # no ig line of 1 word or under 0.3 s on a run of short words (guest O's F3 'are' 0.05 s, 'what' 0.08 s)
    g4 = grp("and what are the choices".split(), 0.0, 0.06)
    caps4 = ig_chunks([g4, grp("you have for holiday?".split(), 0.5)], 1.1)
    if caption_line_faults([], caps4, 1.1):
        fails.append(f"short words: {caption_line_faults([], caps4, 1.1)}")
    # the drawn looks: a 1-word group joins its neighbour; a 2-line split keeps 2 words a line when it can
    gd = fix_caption_groups([dict(grp("The coach signs it the same".split(), 0.0), lines=two_lines("The coach signs it the same".split(), 104)),
                             dict(grp(["day."], 1.85), lines=[[0]])], 1.1)
    if len(gd) != 1 or caption_line_faults(gd, None, 1.1):
        fails.append(f"drawn 1-word group: {[[w[0] for w in g['w']] for g in gd]} {caption_line_faults(gd, None, 1.1)}")
    tl = two_lines("we sat down and planned the whole timetable".split(), 104)
    if tl and any(len(x) < 2 for x in tl):
        fails.append(f"two_lines 1-word line: {tl}")
    # causes 1 and 2: the solved crop on guest C's own source (1280x720, face [556, 231, 264, 264], high 213, low 593)
    jinf = {"w": 1280, "h": 720}
    jf = [556.0, 231.0, 264.0, 264.0]
    for name, lay, ln in (("card", ANSWER_GRAPHIC, "guest"), ("full", ANSWER_FULL, "guest"), ("hook guest", HOOK_LAYOUT, "guest"),
                          ("ig answer", IG_LAYOUT["answer"], "guest"), ("ig hook guest", IG_LAYOUT["hook"], "guest")):
        pn = lay[ln]
        g = face_on_frame(jinf, jf, pn, None, 593.0, 213.0)
        foot = pn["y"] + pn["h"] >= VH - 1
        # 29 Oct (builder G): the reach the solve settled for (1536 at a SOFT_REACH step), as blur_bottom_ok reads it
        ok = (g["foot_y"] >= min(BLUR_TOP, g.get("need_used") or BLUR_TOP) - 2 if foot else True) and not g["pillar"] and not g["legacy"] and g["mouth"] <= 1500
        if pn.get("mouth_max"):
            ok = ok and g["mouth"] <= pn["mouth_max"] + 2
        print(f"  solve {name:13} face {g['height']:4} px, mouth {g['mouth']}, footage to {g['foot_y']}, ground run-over {g['top_h']}, relax {g['relax']}")
        if not ok:
            fails.append(f"solve {name}: {g}")
    jh = face_on_frame(jinf, [533.0, 197.0, 341.0, 341.0], HOOK_LAYOUT["host"], None, 634.25, 157.0)
    print(f"  solve hook host     face {jh['height']:4} px, footage to {jh['foot_y']}, pillar {jh['pillar']}, run-over {jh['top_h']}")
    if jh["pillar"] or jh["legacy"] or jh["foot_y"] < HOOK_LAYOUT["host"]["y"] + HOOK_LAYOUT["host"]["h"] - 2:
        fails.append(f"hook host: {jh}")
    print("selftest:", "PASS" if not fails else "FAIL")
    for f in fails:
        print("  FAIL", f)
    if fails:
        raise SystemExit(1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--build")
    ap.add_argument("--plan")
    ap.add_argument("--look")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--requeue", help="a render tag: its outputs and the exit file of its render state folder (paths.WORKROOT/../renders/<tag>) go, so the queue builds it again")
    a = ap.parse_args()
    if a.requeue:
        tag = a.requeue
        gone = []
        for sp in all_specs():
            S = load_spec(sp)
            # exact names only: `--requeue <id>` must leave `<id>-cmp-<look>*` alone
            # never a reviewer's file: `-review.json` was on this list from 02:30 to 03:05 and the requeues of that window
            # removed the per-short review jsons beside the old renders (the .md twins and the reviews/ folder stayed)
            for name in (f"{tag}.mp4", f"{tag}-poster.jpg", f"{tag}-sheet.jpg", f"{tag}-checks.json", f"{tag}-before.mp4"):
                f = OUT / S["slug"] / name
                if f.is_symlink() or f.is_file():
                    os.remove(f)
                    gone.append(f.name)
        rd = PATHS.WORKROOT.parent / "renders" / tag
        for name in ("exit", "pid"):
            if (rd / name).exists():
                os.remove(rd / name)
                gone.append(f"renders/{tag}/{name}")
        print("requeued", tag, "removed:", gone)
    elif a.selftest:
        selftest()
    elif a.status:
        status()
    elif a.plan:
        S = load_spec(a.plan)
        S["_look"] = a.look or S.get("look") or "none"   # the plan the build would make for this look
        P = plan(S, WORKROOT / S["id"])
        sp = spec_speed(S)
        for it in P["items"]:
            xf = f" {it.get('from')}->{it.get('to')}" if it["layout"] == "xfade" else ""
            print(f"{it['kind']:6} {str(it['speaker']):6} {it['a']:9.3f} {it['b']:9.3f} n={it['n']:4d} out={it['out']:7.3f} ({it['out'] / sp:6.2f} s at {sp}x) {it['layout']}{xf}{' aha' if it.get('aha') else ''}{' cont' if it.get('cont') else ''}")
        print("hook_end", P["hook_end"], "total", P["total_n"] / FPS, "runs", len(P["runs"]))
        gs = caption_groups(P, S)
        if S["_look"] == "ig_native":
            caps = ig_chunks(gs, sp)
            for c in caps:
                print(f"  ig {c['s']:6.2f}-{c['e']:6.2f} ({c['e'] - c['s']:.2f} s) | " + " ".join(w[0] for w in c["w"]))
            print("caption faults:", caption_line_faults([], caps, sp))
        else:
            for g in gs:
                print(f"  {g['style']} {g['s']:6.2f}-{g['e']:6.2f} | " + " / ".join(" ".join(g['w'][i][0] for i in ln) for ln in g["lines"]))
            print("caption faults:", caption_line_faults(gs, None, sp))
    elif a.build:
        try:
            build(a.build, a.look, a.force)
        except SystemExit:
            raise
        except Exception:
            traceback.print_exc()
            sys.exit(1)
    else:
        ap.print_help()
