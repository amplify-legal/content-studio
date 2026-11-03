#!/usr/bin/env python3
"""The TUTORIAL look ("screen is the subject"): the tutorial profile (content/taste/shorts-profiles.md), built.

    python3 tutorial_look.py --build <spec.json> --layout A|B|C [--force]   render one short in one layout
    python3 tutorial_look.py --regions <spec.json>                         print the regions it would use, per layout

Reads the spec (never edits it) and its sidecar <specs>/<slug>/<id>-tutorial.json (the zoom regions on the screen
file with their clock times, the marks, the one card, the private rects and masks, the face region; every number
measured on real frames pulled with ffmpeg -nostdin). Imports pipeline.py and reuses plan, load_words, info, face_box
(Haar inside the webcam region), caption_groups, ass_text, audio_take, spec_speed, render_overlay, contact_sheet,
true_peak, lufs_of and the shorts-editor check scripts; it never edits pipeline.py, looks.html or any spec.

Layouts (1080x1920; first drawn as preview stills, changed where noted):
  A  screen hero: the zoomed screen in a rounded card x 57..1023, y 392..846, the face inset 720x640 (a third of the
     frame) x 180..900, y 860..1500, captions bottom-anchored over the shirt (block bottom 1492), the title above.
  B  face across the top (0..800, faded into the ground), the title in the seam 812..950, the zoomed screen strip
     x 40..906, y 962..1184, captions top-anchored at 1214.
  C  the screen full bleed, the line placed at y 650, everything but the line dimmed, the title on a dark top fade;
     the face a 640 px circle x 220..860, y 860..1500 (the still's 290 px corner circle is gone: the creator, "the
     person is big on screen too, never small in a corner"), captions bottom-anchored over its lower part.
29 Oct (builder T, the 5 round-3 FAILs): A and C are no longer fixed bands. fit_layout solves them per short from the face
  measured with cv2 (no ffmpeg): the face panel full width from P_top to 1920, the chin at 1386, the hair top whole at
  P_top, captions one line in a dark box 1400..1496 under the chin, the webcam's edges stretched and blurred where the
  crop runs past it (soft pillars on a small webcam, a darkening floor under its foot); the screen fills 384..P_top-12
  (A a rounded card, C edge to edge with its own band under the title); B's card takes the title's seam, never the face.
  A region may carry "block" (the text block it sits in): the view then shows lines from their first word at the read
  floor x 1.10 and pans right only as he reads. A region whose focus fits gives up the read margin before the focus.
The zoom: each region's `at` is snapped to the nearest word start, mapped to output time through the plan; between
regions the view (log scale and centre) moves on a critically damped spring (95 % at 0.4 s), inside a hold it pushes in
4 % with a 1 % drift (the movement the creator asked for on tutorial-1 F1). The base video is composited per
output frame in numpy (cv2.warpAffine, subpixel), not with ffmpeg crop: crop cannot change size per frame and zoompan
steps on whole source pixels, which jitters a slow push. The marks and the card are drawn by tutorial.html through
the same per-frame transform, so they stay glued to the text while the zoom moves.

Rules carried in code: every ffmpeg -nostdin; no -loop 1 inputs; no shell rm (Python removes nothing but its own
.part files by literal name); caches under <work dir>/<id>-tut<L>/ (paths.WORKROOT); scratch paths absolute.

Specs and sidecars: examples/podcast-shorts-pipeline/specs/example/ holds an invented sidecar in the exact shape the
loader reads (tutorial-1-T1-tutorial.json); every number in a real one is measured on frames of your own recording.
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
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # this folder (paths.py, pipeline.py)
import numpy as np  # noqa: E402
import pipeline as PL  # noqa: E402
from PIL import Image, ImageFont  # noqa: E402

import paths as PATHS  # noqa: E402
HERE = PATHS.BUILD
OUT = PATHS.OUT
WORKROOT = PATHS.WORKROOT
RESULTS = PATHS.RESULTS
TUT_HTML = HERE / "tutorial.html"
FONTDIR = PATHS.FONTDIR
SK = PATHS.SK
FF = "ffmpeg"
FPS = 30
VW, VH = 1080, 1920
CODE_V = 10         # bump when the base compositor changes (the base cache key); 9: the polish layouts, 28 Oct; 10: fit_layout + the foot extension, 29 Oct (builder T)
# the credit in the last 6 s (the round-2 credit): your own brand's name, config "tutorial_credit", else the first of
# config "own_names", else none (an empty credit is not drawn and its check is skipped)
CREDIT = str(PATHS.CONFIG.get("tutorial_credit") or (PATHS.OWN_NAMES[0] if PATHS.OWN_NAMES else ""))
ACC = PATHS.ACCENT          # the brand accent (paths.py: config "brand", else brand.py, else a placeholder blue)
ACC_DARK = PATHS.ACCENT_DARK

PAPER = (247, 246, 242)
DARK = (16, 22, 25)
# 27 Oct (tutorial fixer, round-1 verdicts 22:30): captions sit lower in A and C (marginV 406, the ink 1420..1496,
# clear of his chin at 1341..1376), a caption line may run to x 930 (CAP_LINE_MAX 760 px, x 160..920), and B's face
# panel starts at y 90 at 2.09x (was 0 at 2.35x: his crown sat under the platform chrome, tutorial-2 M1 verdict).
# The credit has no fixed place any more: it takes the title's own box in the last 6 s (tutorial.html), so it never
# covers a face, a mouth, the card or the screen (tutorial-3 F1 tutA and tutC verdicts).
# 28 Oct (polish, the styles review; the creator on H: "my face box should usually span all the way from left to right", on
# I: "white captions on top of light background is not gonna work. Put a box around them", "make the window of the screen
# capture bigger, use more of the screen", on J: "I don't know how I feel about being a little circle", "the light mode
# ones are easier on the eye", "we could definitely make better use of the full screen"):
#   A: the screen card 1040 wide (x 20..1060) and 468 tall (y 392..860); the face a full-width rectangle y 874..1514
#      (ff 0.46, bigger), captions one line at 1420..1496 over the shirt.
#   B: the screen strip 1040 x 420 (y 962..1382), captions one line at 1410..1486 in a dark box on the paper.
#   C: light (paper ground, dark ink), the screen full width edge to edge in the top 860 px (zoomed, the rest dimmed), the
#      face the same full-width rectangle as A: nobody is a circle.
# 29 Oct (builder T, the 5 round-3 verdicts, all FAIL): the fixed A and C bands (face 874..1514 at 1080x640, captions
# 1420..1496) were laid out without a render. A 1080x640 panel is 1.69:1, so a square webcam (tutorial-1 330x330)
# could only fill it by cropping 195 of its 330 rows: crown cut by the card edge, chin under the caption line; tutorial-3's
# wide webcam fit but its chin still sat on the caption line; 406 px of paper under the face. A and C are now SOLVED per
# short (fit_layout, from the face measured with cv2, no ffmpeg): the face panel runs from P_top to the frame's foot, full
# width, the crop scaled so the chin lands at CHIN_Y and the crown (with headroom) at P_top; captions one line in a dark
# box at 1400..1496 over the shirt, under the chin; where the webcam ends above the foot, its last rows are stretched and
# blurred down to 1920 (the ig_native extension), so no paper is left; the screen card fills title_bottom..P_top. C is A
# with the screen edge to edge in that band (no veil under the title: the title has its own band, the screen never runs
# behind it). The numbers below are the TEMPLATES; LAYOUTS[L] is replaced per short by fit_layout.
CHIN_Y = 1352        # (tutorial-3 tutC r3, second read: the box top 1387 sat 5..12 px under the real chin, veiling neck
                     # and collar): the chin estimate now sits 48 px above the caption box (box 1400..1496)
HEAD_MIN = 450       # (same verdict: hair to chin 285 px, "a small webcam floating in blur"): hair to chin at least
                     # 450 px and the real picture across the full 1080 where the webcam is wide enough
FACE_TOP_MIN = 884   # and the face panel starts no higher than this, so the screen card keeps 364..872 (1040 x 508);
                     # a webcam that would need more (a small square one) shrinks to fit with soft pillars
CHIN_Y_OLD = 1386        # the chin estimate's frame row: 14 px above the caption box (box 1400..1496, ink 1410..1486)
HEAD_TARGET = 600    # crown (with headroom) to chin on the frame, px, when the webcam allows it (a webcam narrower than
                     # 1080/k forces a bigger head: full width wins)
CROWN_K = 0.30       # Haar box top minus 0.30 of its height: the hair top plus headroom (measured 29 Oct: hair top at
                     # 0.12..0.16 of the box above it on tutorial-3 941 s, tutorial-1 480 s, tutorial-2 382 s)
CROWN_TRUE = 0.17    # the hair top itself (the crop never starts below it)
CHIN_K = 1.12        # the chin under the box top (measured 1.05..1.12 on the same 3 frames)
HEAD_MAX = 620      # hair top to chin on the frame at most: a webcam too small to fill 1080 at this size (tutorial-1's
                     # 330 px square gave an 800 px head and a 188 px screen card) is shown with soft pillars instead: the
                     # panel stays full width, its outer columns the webcam's own edge stretched and blurred
FACE_TOP = 1036     # 29 Oct (conductor, on the first render of the per-short solve: the face took y 720..1920 and the
                     # screen card shrank to 354..714, unreadable at phone size; I, J, H: the screen is the subject): the
                     # screen card is 1040 x 640 (384..1024) in A and C on every short, the face panel 1036..1920 full
                     # width, the head (hair plus headroom to chin) sized to 1036..1386, soft pillars where the webcam is
                     # narrower than the crop; the constants HEAD_TARGET, HEAD_MAX, P_TOP_MIN, P_TOP_FLOOR are no longer read
P_TOP_MIN = 660      # the face panel starts no higher than this while headroom can be trimmed (the screen card keeps ~260)
P_TOP_FLOOR = 520    # and never higher than this even to keep the crown (then the log says the crown is tight)
TITLE_TOP, TITLE_MAX_BOTTOM, GAP = 236, 352, 12   # 2 lines at 58 px (was 68 to 372): 20 px more screen
LAYOUTS = {
    "A": {"ground": PAPER, "hole": [20, 392, 1040, 468], "hole_r": 26, "anchor": None, "adaptive": True,
          "face": {"box": [0, 874, 1080, 1046], "shape": "rect", "cy": 0.44, "ff": 0.46},
          "title": {"top": TITLE_TOP, "max_bottom": TITLE_MAX_BOTTOM, "size": 58, "color": "#1C1C1E", "accent": ACC_DARK},
          "cap": {"align": 2, "marginV": 416, "area": [150, 1190, 930, 1500], "one_line": True, "box": True}},
    "B": {"ground": PAPER, "hole": [20, 962, 1040, 420], "hole_r": 20, "anchor": None,
          "face": {"box": [0, 90, 1080, 710], "shape": "fade", "fade": 90, "fade_top": 40, "cy": 0.47, "ff": 0.44},
          "title": {"top": 814, "max_bottom": 952, "size": 62, "color": "#1C1C1E", "accent": ACC_DARK},
          "cap": {"align": 2, "marginV": 416, "area": [150, 1190, 930, 1500], "one_line": True, "box": True}},
    "C": {"ground": PAPER, "hole": [0, 384, 1080, 476], "hole_r": 0, "anchor": [540, 622], "adaptive": True,
          "face": {"box": [0, 874, 1080, 1046], "shape": "rect", "cy": 0.44, "ff": 0.46},
          "title": {"top": TITLE_TOP, "max_bottom": TITLE_MAX_BOTTOM, "size": 58, "color": "#1C1C1E", "accent": ACC_DARK},
          "cap": {"align": 2, "marginV": 416, "area": [150, 1190, 930, 1500], "one_line": True, "box": True}},
}
LAYOUT_BASE = json.loads(json.dumps(LAYOUTS))   # the templates; fit_layout rebuilds LAYOUTS[L] from these per short
CAP_LINE_MAX = 760   # a drawn caption line at most 760 px wide, centred: x 160..920, never past 930 (the conductor's rule)
CAP_LINE_SOFT = 710  # the column the captions aim for (x 185..895); 710..760 costs a little in the line search
MARK_LAND = 0.35     # a region's mark waits until the view's spring has landed (95 % at 0.4 s): no mark rides a move
MARK_LEAVE = 0.20    # and leaves this long before the next region's move starts (tutorial-3 tutC: an outline swept
                     # through the title band on the spring to the next region, 7.5 to 7.6 s)
SPEED = [1.1]       # the spec's speed, set by prepare (grow times are clock seconds)
SMAX = 3.8          # never past 3.8x on a screen recording (the 1080p tutorial-3 tape is soft above it)
READ_PX = 9.0       # the tutorial profile: the marked text's cap height at 375 px wide is at least 9 px
READ_MARGIN = 1.15  # the floor plus 15 % (the 18:15 storyboard: a prompt line at the bare 9 px read small on the sheet)
BLOCK_OVER = 1.12   # a region inside a text block (region field "block"): 12 % past the bare 9 px floor, about 10 px cap
                    # height at 375 wide (conductor 17:56: "at least about 10 px")
PUSH = 0.04         # the slow push inside a hold
DRIFT = 0.010       # and its drift, as a share of the visible width


def spring_cd(t, w=13.0):
    """critically damped spring (springs.js make(1, w)): 0 at t <= 0, 0.966 at 0.4 s, 1 at the settle time."""
    if t <= 0:
        return 0.0
    if t >= 16.0 / w:
        return 1.0
    return 1.0 - (1.0 + w * t) * math.exp(-w * t)


def log(work, msg):
    PL.log(work, msg)


# ---------------------------------------------------------------- sidecar and timing
def sidecar_path(spec_path, S):
    """a `-hook2` twin (the aha line first, 18:33) reads its base's sidecar: the regions are clock times, so they fit both"""
    base = re.sub(r"-hook2$", "", S["id"])
    return Path(spec_path).parent / f"{base}-tutorial.json"


def load_side(spec_path, S):
    p = sidecar_path(spec_path, S)
    if not p.exists():
        raise SystemExit(f"no sidecar: {p} (write it from measured frames first; the shape is specs/example/tutorial-1-T1-tutorial.json)")
    return PATHS.load_json(p), p


def snap_word(ws, t, win=0.6):
    """the start of the word nearest t (within win), else t"""
    best = None
    for w in ws:
        d = abs(w["s"] - t)
        if d <= win and (best is None or d < best[0]):
            best = (d, w["s"], w["t"])
    return (best[1], best[2]) if best else (t, None)


def to_out(P, tc, speed):
    """a clock time -> output seconds (the plan's kept pieces); outside every piece: the next piece's start."""
    for it in P["items"]:
        if it["kind"] == "card":
            continue
        if it["a"] - 0.05 <= tc <= it["b"] + 0.05:
            return (it["out"] + max(0.0, min(tc, it["b"]) - it["a"])) / speed
    after = [it for it in P["items"] if it["kind"] != "card" and it["a"] > tc]
    if after:
        return min(it["out"] for it in after) / speed
    return (P["total_n"] / FPS) / speed - 0.5


def regions_of(T):
    out = []
    for r in T["regions"]:
        r = dict(r)
        ms = r.get("marks") or ([r["mark"]] if r.get("mark") else [])
        r["marks"] = ms
        r["focus"] = r.get("crop") or r.get("focus")
        out.append(r)
    return out


def view_for(L, focus, read_cap, bounds, mark_box=None, smax=None, align=None, block=None):
    """the target view (s, cx, cy): the source point (cx, cy) shown at the layout's anchor, at scale s.
    align "left" (a region field, 27 Oct 22:50): when the focus does not fit, the view's left edge sits on the focus's
    left edge instead of centring on the mark (tutorial-3 tutA at 5.0 s cut the Deny button to 'eny'), as long as the
    mark stays whole inside the view."""
    lay = LAYOUTS[L]
    hx, hy, hw, hh = lay["hole"]
    fx, fy, fw, fh = focus
    if lay["anchor"]:
        ax, ay = lay["anchor"][0] - hx, lay["anchor"][1] - hy
        fit = min(1040.0 / fw, hh * 0.86 / fh)   # 29 Oct: C's band is solved per short (fit_layout), so is its fit
    else:
        ax, ay = hw / 2.0, hh / 2.0
        fit = min(hw * 0.94 / fw, hh * 0.88 / fh)
    smin = (READ_PX / (read_cap * 375.0 / 1080.0)) * READ_MARGIN if read_cap else 1.0
    s = min(max(fit, smin), smax or SMAX)
    cx, cy = fx + fw / 2.0, fy + fh / 2.0
    if block:
        # 29 Oct (tutorial-1 tutA verdict: 'Write a summary of my own n', 'tell me', 'as th' ran off the card's
        # right edge): a region inside a wider block of text (a prompt he reads aloud) is shown at the scale that fits
        # the block, never zoomed past the bare read floor x BLOCK_OVER when the block cannot fit; the view's left edge
        # sits on the block's left edge (the lines read from their start) and moves right only as far as the focus
        # needs (it pans once he reads past the visible line), so every line is whole from its first word
        bx_, by_, bw_, bh_ = block
        s_floor = (READ_PX / (read_cap * 375.0 / 1080.0)) * BLOCK_OVER if read_cap else 1.0
        s = min(s, max(min(hw * 0.96 / bw_, hh * 0.9 / bh_), s_floor), smax or SMAX)
        half = (hw / 2.0) / s if not lay["anchor"] else (ax - 24.0) / s
        cx = bx_ - 10.0 / s + half
        if fx + fw + 12.0 / s > cx + half:
            cx = fx + fw + 12.0 / s - half
        vh_half = (hh / 2.0) / s if not lay["anchor"] else (hh * 0.5) / s
        cy = by_ + bh_ / 2.0 if bh_ / 2.0 <= vh_half - 8.0 / s else min(max(fy + fh / 2.0, by_ + vh_half - 8.0 / s), by_ + bh_ - vh_half + 8.0 / s)
        # rebalance: the taller card must not push a block's scale up to fill itself (the bounds' height would
        # zoom the prompt past its first word); the card shows the app's own fill around it instead
        return [s, cx, cy, ax, ay] if lay["anchor"] else list(clamp_view(lay, s, cx, cy, bounds, grow=False)) + [ax, ay]
    if fit < smin and not block:
        # 29 Oct (tutorial-3 tutA verdict: 'Allow once' clipped at the card's edge 0 to 3.5 s, the focus held both
        # buttons): the read margin gives way before the focus does: down to 2 % over the bare floor if that keeps the
        # focus whole with the hold's 4 % push and the edge fades
        s_bare = smin / READ_MARGIN
        s_alt = min(max(fit / 1.10, s_bare * 1.12), smax or SMAX)   # never under about 10 px caps at 375 wide
        if s_alt < s:
            s = s_alt
        vis = (hw if not lay["anchor"] else 2.0 * (ax - 24.0)) / s
        if vis >= fw * 1.02:   # the 10 px floor leaves less room; a focus that fits at all is centred whole
            mark_box = None   # the focus fits whole: centre on it, not on the mark
    if fit < smin and mark_box:
        # the focus does not fit at a readable scale: the view centres on the marked thing (the rest runs off the hole)
        mx, my, mw, mh = mark_box
        cx, cy = mx + mw / 2.0, my + mh / 2.0
        if align == "left":
            half = (ax - 30.0) / s if lay["anchor"] else hw / 2.0 / s
            cx = fx + half
            cx = max(cx, mx + mw + 8.0 / s - half)     # the mark's right edge stays inside the view
    if not lay["anchor"]:
        s, cx, cy = clamp_view(lay, s, cx, cy, bounds)
    return [s, cx, cy, ax, ay]


def clamp_view(lay, s, cx, cy, bounds, grow=True):
    """A and B: the crop stays inside the region's bounds where it can (the scale rises to fill the hole, never past
    SMAX); a bounds smaller than the hole at SMAX shows the app's own background around it (the sidecar's fill)."""
    hx, hy, hw, hh = lay["hole"]
    bx, by, bw, bh = bounds
    if grow:
        s = max(s, min(SMAX, max(hw / bw, hh / bh)))
    cw, ch = hw / s, hh / s
    cx = min(max(cx, bx + cw / 2.0), bx + bw - cw / 2.0) if cw <= bw else bx + bw / 2.0
    cy = min(max(cy, by + ch / 2.0), by + bh - ch / 2.0) if ch <= bh else by + bh / 2.0
    return s, cx, cy


def occurrences(P, tc, speed):
    """every output time where clock time tc plays (a `-hook2` twin plays its aha line as the preview and again in place):
    a piece holds tc from 50 ms before its start to 20 ms before its end (a time on a cut belongs to the piece it opens);
    a time up to 0.6 s before a piece maps to that piece's start; a time in no piece (the opening line a twin drops) has none"""
    outs = [(it["out"] + max(0.0, tc - it["a"])) / speed for it in P["items"]
            if it["kind"] != "card" and it["a"] - 0.05 <= tc < it["b"] - 0.02]
    if outs:
        return outs
    near = [it for it in P["items"] if it["kind"] != "card" and 0 < it["a"] - tc <= 0.6]
    return [min(it["out"] for it in near) / speed] if near else []


def timeline(S, P, T, speed):
    """regions in output time (one per occurrence of the region's clock time), each with its marks' output times inside
    the same occurrence; sorted by output time."""
    # 28 Oct: the words of every person in the spec (a live has one track per person), so a region on a guest's
    # line snaps to the guest's word; a one-person tutorial reads its one file as before
    ws, seen = [], set()
    for pp in P["people"].values():
        if not pp or not pp.get("words") or (pp["words"], pp.get("scribe_speaker")) in seen:
            continue
        seen.add((pp["words"], pp.get("scribe_speaker")))
        ws += PL.load_words(pp["words"], pp.get("scribe_speaker"), pp.get("words_offset") or 0.0)
    ws.sort(key=lambda w: w["s"])
    regs = []
    for i, r in enumerate(regions_of(T)):
        at_w, word = snap_word(ws, float(r["at"]))
        occ = occurrences(P, at_w, speed)   # a region in no piece of this spec (a twin drops the opening line) is skipped
        for k, t0 in enumerate(occ):
            marks = []
            for m in r["marks"]:
                mw_, mword = snap_word(ws, float(m.get("at", r["at"])))
                mo = [o for o in occurrences(P, mw_, speed) if o >= t0 - 0.01]
                marks.append(dict(m, t0=round(max(t0, mo[0] if mo else t0), 3), word=mword, at_snapped=round(mw_, 3)))
            regs.append(dict(r, idx=i, occ=k, t0=round(t0, 3), word=word, at_snapped=round(at_w, 3), marks=marks))
    regs.sort(key=lambda r: (r["t0"], r["idx"]))
    total = P["total_n"] / FPS / speed
    if T.get("card"):
        c = T["card"]
        cat, cword = snap_word(ws, float(c["at"]))
        occ_c = occurrences(P, cat, speed)
        if not occ_c:
            # 29 Oct (tutorial-2 M1-hook2 tutB: the card's line was recut out with an off-limits stretch): a card whose
            # line is in no piece of this spec is not shown at all, never moved onto another line
            print(f"NOTE: the card '{c.get('line')}' (clock {c['at']}) is in no piece of {S['id']}: not shown", file=sys.stderr)
            T["card"] = None
        c0 = (occ_c or [to_out(P, cat, speed)])[0]   # the card plays once, at the first occurrence
        # its end inside the same play of the line (a twin plays it twice: never from the preview into the replay)
        pe = [(it["out"] + it["n"] / FPS) / speed for it in P["items"] if it["kind"] != "card" and it["out"] / speed <= c0 + 1e-6 < (it["out"] + it["n"] / FPS) / speed]
        c1 = c0 + max(0.8, (float(c["until"]) - cat) / speed)
        T["_card_t"] = [round(c0, 3), round(min(c1, pe[0] - 0.05) if pe else c1, 3), cword]
    for k, r in enumerate(regs):
        r["t1"] = regs[k + 1]["t0"] if k + 1 < len(regs) else total
        for m in r["marks"]:
            m["t1"] = round(min(r["t1"], to_out(P, float(m["until"]), speed)) if m.get("until") else r["t1"], 3)
            # a mark is drawn only while the view holds still on its region: it waits for the spring to land and
            # is gone before the next move (tutorial-3 tutC 7.5 s: an outline rode the spring through the title band)
            if k > 0 and m["t0"] < r["t0"] + MARK_LAND <= r["t1"] - 0.6:
                m["t0"] = round(r["t0"] + MARK_LAND, 3)
            if k + 1 < len(regs) and m["t1"] > r["t1"] - MARK_LEAVE >= m["t0"] + 0.4:
                m["t1"] = round(r["t1"] - MARK_LEAVE, 3)
    if regs and regs[0]["t0"] > 0.3:
        # nothing measured for the first frames (a twin's aha line with no region at its clock time): say so loudly
        print(f"WARNING: no region covers output 0.00 to {regs[0]['t0']:.2f} s; the first region's view is shown there", file=sys.stderr)
    return regs, total


def rbounds(T, r):
    return r.get("bounds") or T["bounds"]


def views(L, regs, T):
    cap_default = T.get("text_cap_px", 9)
    out = []
    for r in regs:
        readable = [m for m in r["marks"] if m.get("read", True) and m.get("kind") != "dim-rest-only"]
        cap = min([m.get("cap_px", cap_default) for m in readable]) if readable else None
        mb = readable[0]["box"] if readable else (r["marks"][0]["box"] if r["marks"] else None)
        out.append(view_for(L, r["focus"], cap, rbounds(T, r), mb, r.get("max_scale"), r.get("align"), r.get("block")))
    return out


def xf_series(L, regs, V, nfr, T):
    """per output frame: [s, ox, oy] (source -> frame) and the region index; a spring from wherever the view was when a
    region starts (a quick succession starts from the unfinished move), a slow push and drift inside a hold."""
    lay = LAYOUTS[L]
    hx, hy, hw, hh = lay["hole"]
    res, idxs = [], []
    k = 0
    start = {}
    last = None

    vis_w = (lambda s: 1000.0 / s) if lay["anchor"] else (lambda s: hw / s)

    def hold_state(i, t):
        s, cx, cy, ax, ay = V[i]
        r = regs[i]
        dur = max(1.0, r["t1"] - r["t0"])
        u = min(1.0, max(0.0, (t - r["t0"]) / dur))
        e = u * u * (3 - 2 * u) * 0.35 + u * 0.65          # mostly linear, a soft start
        s2 = s * (1.0 + PUSH * e)
        g = next((m for m in r["marks"] if m.get("grow")), None)
        if g and g["box"][2] > 0.9 * vis_w(s2):
            # a line wider than the view: the view travels along it as the highlighter sweeps, at his reading pace
            gx0, gx1 = g["box"][0], g["box"][0] + g["box"][2]
            v = vis_w(s2)
            gu = min(1.0, max(0.0, (t - g["t0"]) / max(0.3, float(g["grow"]) / SPEED[0])))
            gu = gu * gu * (3 - 2 * gu)
            return [s2, (gx0 + 0.45 * v) + ((gx1 - 0.45 * v) - (gx0 + 0.45 * v)) * gu, cy, ax, ay]
        dx = DRIFT * (hw / s) * (e - 0.5) * (1 if i % 2 == 0 else -1)
        return [s2, cx + dx, cy, ax, ay]

    for j in range(nfr):
        t = j / FPS
        while k + 1 < len(regs) and t >= regs[k + 1]["t0"]:
            k += 1
            start[k] = list(last) if last is not None else hold_state(k - 1, regs[k]["t0"])
        cur = hold_state(k, t)
        if not lay["anchor"]:
            # the target is clamped into ITS region's bounds; a move interpolates from the view last shown (already
            # clamped into the previous region's bounds), so a change of bounds never jumps
            cur[0], cur[1], cur[2] = clamp_view(lay, cur[0], cur[1], cur[2], rbounds(T, regs[k]), grow=not regs[k].get("block"))
        if k in start:
            a = start[k]
            p = spring_cd(t - regs[k]["t0"])
            if p < 1.0:
                ls = math.log(a[0]) + (math.log(cur[0]) - math.log(a[0])) * p
                cur = [math.exp(ls), a[1] + (cur[1] - a[1]) * p, a[2] + (cur[2] - a[2]) * p, cur[3], cur[4]]
        last = list(cur)
        s, cx, cy, ax, ay = cur
        ox = hx + ax - cx * s
        oy = hy + ay - cy * s
        res.append([round(s, 5), round(ox, 3), round(oy, 3)])
        idxs.append(k)
    return res, idxs


# ---------------------------------------------------------------- faces
def face_geom(L, fbox, region):
    """the face crop for the layout's panel: the Haar box at cy of the panel, ff of its height, never past the webcam
    region (its rounded corners and border stay out); returns crop [x, y, w, h] in source px and the mouth on the frame."""
    lay = LAYOUTS[L]["face"]
    px, py, pw, ph = lay["box"]
    rx, ry, rw, rh = region
    fx, fy, fw, fh = fbox
    if LAYOUTS[L].get("adaptive"):
        # 29 Oct (builder T): full width, the chin at CHIN_Y, the crown (with what headroom fits) at the panel's top;
        # the crop may run below the webcam's foot (the compositor stretches and blurs its last rows down to 1920)
        chin = fy + CHIN_K * fh
        top_h = max(ry, fy - CROWN_K * fh)
        top_c = max(ry, fy - CROWN_TRUE * fh)
        # the head at HEAD_MIN or more and full width where the webcam allows; never bigger than the panel holds
        k = min(max(pw / rw, HEAD_MIN / max(1.0, chin - top_c)), (CHIN_Y - py) / max(1.0, chin - top_c))
        cw = pw / k
        y = chin - (CHIN_Y - py) / k
        ch = ph / k
        if cw <= rw:
            x = min(max(fx + fw / 2.0 - cw / 2.0, rx), rx + rw - cw)
        else:
            x = min(max(fx + fw / 2.0 - cw / 2.0, rx + rw - cw), rx)   # wider than the webcam: the webcam stays inside
        return {"crop": [x, y, cw, ch], "k": k, "mouth_y": py + (fy + 0.78 * fh - y) * k, "face_top": py + (fy - y) * k,
                "face_bottom": py + (chin - y) * k, "chin_y": py + (chin - y) * k, "crown_y": py + (fy - CROWN_TRUE * fh - y) * k,
                "foot_y": py + (ry + rh - y) * k, "roof_y": py + (ry - y) * k, "pillar_x": [(rx - x) * k, (rx + rw - x) * k], "head_px": (chin - (fy - CROWN_TRUE * fh)) * k, "crown_cut": bool(y > fy - CROWN_TRUE * fh + 0.5)}
    ch = min(rh, fh / lay["ff"])
    cw = ch * pw / ph
    if cw > rw:
        cw = rw
        ch = cw * ph / pw
    fcx, fcy = fx + fw / 2.0, fy + fh / 2.0
    x = min(max(fcx - cw / 2.0, rx), rx + rw - cw)
    y = min(max(fcy - lay["cy"] * ch, ry), ry + rh - ch)
    k = ph / ch
    mouth = py + (fy + 0.78 * fh - y) * k
    return {"crop": [x, y, cw, ch], "k": k, "mouth_y": mouth, "face_top": py + (fy - y) * k, "face_bottom": py + (fy + fh - y) * k,
            "head_px": fh * k * 1.45}


def face_specs(P, T):
    """[(role, file, region, explicit box or None, pieces)] for every speaker the short shows"""
    host_role = next(iter(P["people"]))
    if not T.get("faces"):
        pcs = [(it["a"], it["b"]) for it in P["items"] if it["kind"] != "card"]
        return [(host_role, T.get("face_file") or T["screen_file"], T["face_region"], T.get("face_box"), pcs)]
    out = []
    roles = sorted(set(it.get("speaker") or host_role for it in P["items"] if it["kind"] != "card"))
    for role in roles:
        fc = T["faces"].get(role)
        if not fc:
            raise SystemExit(f"sidecar faces has no '{role}' and a piece is spoken by {role}")
        pcs = [(it["a"], it["b"]) for it in P["items"] if it["kind"] != "card" and (it.get("speaker") or host_role) == role]
        out.append((role, fc.get("file") or P["people"][role]["file"], fc["face_region"], fc.get("face_box"), pcs))
    return out


def measure_head(file, region, pcs, box=None):
    """29 Oct (builder T): the face box measured with cv2 alone (no ffmpeg: the disk guard freezes ffmpeg), Haar inside the
    webcam region on up to 7 frames across the pieces, the median box; cached under WORKROOT/headbox/. A sidecar's
    face_box wins. Returns [x, y, w, h] in source px."""
    if box:
        return [float(v) for v in box]
    key = key_of([str(file), region, [round(a, 2) for a, _ in pcs][:12]])
    cache = WORKROOT / "headbox" / f"{key}.json"
    if cache.exists():
        return json.loads(cache.read_text())["box"]
    import cv2
    rx, ry, rw, rh = [int(v) for v in region]
    casc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    ts = []
    for a, b in pcs:
        ts += [a + (b - a) * f for f in (0.25, 0.6)]
    ts = ts[:: max(1, len(ts) // 7)][:7]
    cap = cv2.VideoCapture(str(file))
    boxes = []
    for t in ts:
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000.0)
        ok, fr = cap.read()
        if not ok:
            continue
        g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)[ry:ry + rh, rx:rx + rw]
        fs = casc.detectMultiScale(g, 1.05, 3, minSize=(int(min(rw, rh) * 0.18), int(min(rw, rh) * 0.18)))
        if len(fs):
            x, y, w, h = max(fs, key=lambda r: r[2] * r[3])
            boxes.append([rx + x, ry + y, w, h])
    cap.release()
    if not boxes:
        fb = [rx + rw * 0.3, ry + rh * 0.2, min(rw, rh) * 0.45, min(rw, rh) * 0.45]
        print(f"WARNING: no face found in {Path(file).name} {region}; a guessed box {fb}", file=sys.stderr)
        return fb
    fb = [float(np.median([b[i] for b in boxes])) for i in range(4)]
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps({"box": fb, "n": len(boxes), "of": len(ts), "file": str(file), "region": region}))
    return fb


def fit_layout(L, T, P):
    """29 Oct (builder T): LAYOUTS[L] rebuilt for this short from its template. A and C: the face panel's top P_top is
    solved from the measured face (full width, chin at CHIN_Y, crown plus headroom at P_top; headroom is trimmed before
    the panel may rise past P_TOP_MIN, and it never rises past P_TOP_FLOOR), the panel runs to 1920, the screen fills
    TITLE_MAX_BOTTOM + GAP .. P_top - GAP. B keeps its template. Returns {role: face box} for the compositor and checks."""
    LAYOUTS[L] = json.loads(json.dumps(LAYOUT_BASE[L]))
    boxes = {role: measure_head(f, reg, pcs, box) for role, f, reg, box, pcs in face_specs(P, T)}
    regions = {role: reg for role, f, reg, box, pcs in face_specs(P, T)}
    lay = LAYOUTS[L]
    if not lay.get("adaptive"):
        return boxes, regions
    tops = []
    for role, fb in boxes.items():
        rx, ry, rw, rh = regions[role]
        fx, fy, fw, fh = fb
        chin = fy + CHIN_K * fh
        top_h, top_c = max(ry, fy - CROWN_K * fh), max(ry, fy - CROWN_TRUE * fh)
        k = max(min(1080.0 / rw, HEAD_MAX / max(1.0, chin - top_c)), HEAD_TARGET / max(1.0, chin - top_h))
        p_nat = CHIN_Y - (chin - top_h) * k
        if p_nat < P_TOP_MIN:
            p_nat = min(P_TOP_MIN, CHIN_Y - (chin - top_c) * k)
        tops.append(max(P_TOP_FLOOR, p_nat))
    tops = []
    for role, fb in boxes.items():
        rx, ry, rw, rh = regions[role]
        fx, fy, fw, fh = fb
        chin = fy + CHIN_K * fh
        top_h, top_c = max(ry, fy - CROWN_K * fh), max(ry, fy - CROWN_TRUE * fh)
        k = max(1080.0 / rw, HEAD_MIN / max(1.0, chin - top_c))
        tops.append(CHIN_Y - (chin - top_h) * k)
    # (tutorial-3 tutC r3): the head first at 450 px or more, the screen card down to 1040 x 508 at least
    p_top = int(round(max(FACE_TOP_MIN, min(tops))))
    lay["face"]["box"] = [0, p_top, 1080, 1920 - p_top]
    h0 = TITLE_MAX_BOTTOM + GAP
    if L == "A":
        lay["hole"] = [20, h0, 1040, p_top - GAP - h0]
    else:
        lay["hole"] = [0, h0, 1080, p_top - GAP - h0]
        lay["anchor"] = [540, h0 + (p_top - GAP - h0) // 2]
    return boxes, regions


# ---------------------------------------------------------------- frames
class Reader:
    """sequential rgb24 frames of one file from a, at 30 fps; get(k) is the frame at a + k/30."""

    def __init__(self, file, a, dur, w, h, rng):
        vf = f"fps={FPS},scale=in_range={rng}:out_range=pc:in_color_matrix=bt709:out_color_matrix=bt709,format=rgb24"
        self.w, self.h = w, h
        self.p = subprocess.Popen([FF, "-nostdin", "-v", "error", "-ss", f"{max(0.0, a):.4f}", "-i", str(file), "-t", f"{dur + 0.4:.3f}",
                                   "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        self.k = -1
        self.cur = None

    def get(self, k):
        n = self.w * self.h * 3
        while self.k < k:
            buf = self.p.stdout.read(n)
            if len(buf) < n:
                break
            self.cur = np.frombuffer(buf, np.uint8).reshape(self.h, self.w, 3)
            self.k += 1
        return self.cur

    def close(self):
        try:
            self.p.stdout.close()
            self.p.wait(timeout=30)
        except Exception:
            self.p.kill()


def still(file, t, w, h, rng):
    vf = f"scale=in_range={rng}:out_range=pc:in_color_matrix=bt709:out_color_matrix=bt709,format=rgb24"
    r = PL.run([FF, "-v", "error", "-ss", f"{t:.4f}", "-i", str(file), "-frames:v", "1", "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
               timeout=120, label="still", binary=True)
    return np.frombuffer(r.stdout, np.uint8).reshape(h, w, 3).copy()


def rounded_mask(w, h, r):
    m = np.ones((h, w), np.float32)
    if r <= 0:
        return m
    yy, xx = np.mgrid[0:h, 0:w]
    for cx, cy in ((r, r), (w - r - 1, r), (r, h - r - 1), (w - r - 1, h - r - 1)):
        inq = ((xx < r) if cx == r else (xx > w - r - 1)) & ((yy < r) if cy == r else (yy > h - r - 1))
        d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        m[inq] = np.clip(r + 0.5 - d[inq], 0, 1)
    return m


def circle_mask(d):
    yy, xx = np.mgrid[0:d, 0:d]
    c = (d - 1) / 2.0
    return np.clip(d / 2.0 + 0.5 - np.sqrt((xx - c) ** 2 + (yy - c) ** 2), 0, 1).astype(np.float32)


def unsharp(img, amount, sigma=1.1):
    import cv2
    if amount <= 0:
        return img
    b = cv2.GaussianBlur(img, (0, 0), sigma)
    return cv2.addWeighted(img, 1 + amount, b, -amount, 0)


def clean_screen(fr, T, src_t, L, rect, fill):
    """the screen frame with the private masks painted in their own background and, outside the bounds rect, the fill
    (four slice writes: a boolean-mask write is numpy's slow path, about a second a frame under load)."""
    img = fr.copy()
    for m in T.get("private_masks") or []:
        bt = m.get("between")
        if bt and not (float(bt[0]) <= src_t <= float(bt[1])):
            continue
        x, y, w, h = [int(v) for v in m["box"]]
        if m.get("fill"):
            col = np.array(m["fill"], np.uint8)
        else:
            ring = np.concatenate([img[max(0, y - 3):y, x:x + w].reshape(-1, 3), img[y + h:y + h + 3, x:x + w].reshape(-1, 3)])
            col = np.median(ring, axis=0).astype(np.uint8) if len(ring) else np.array([255, 255, 255], np.uint8)
        img[y:y + h, x:x + w] = col
    bx, by, bw, bh = [int(v) for v in rect]
    H, W = img.shape[:2]
    col = np.array(fill, np.uint8)
    img[:max(0, by)] = col
    img[min(H, by + bh):] = col
    img[max(0, by):min(H, by + bh), :max(0, bx)] = col
    img[max(0, by):min(H, by + bh), min(W, bx + bw):] = col
    return img


class Compositor:
    """one output frame from a screen frame and a face frame: the ground, the warped screen in the layout's hole (the
    private masks and the out-of-bounds fill applied first), the face crop in its panel with the panel's shape."""

    def __init__(self, L, T, fgeo, W, H):
        import cv2
        self.cv2 = cv2
        self.L, self.T, self.lay = L, T, LAYOUTS[L]
        lay = self.lay
        self.W, self.H = W, H
        self.ground = np.zeros((VH, VW, 3), np.uint8)
        self.ground[:] = lay["ground"]
        hx, hy, hw, hh = lay["hole"]
        self.hmask = rounded_mask(hw, hh, lay["hole_r"])[..., None]
        fx0, fy0, fw0, fh0 = lay["face"]["box"]
        if lay["face"]["shape"] == "round":
            self.fmask = rounded_mask(fw0, fh0, lay["face"].get("r", 36))[..., None]
        elif lay["face"]["shape"] == "circle":
            self.fmask = circle_mask(fw0)[..., None]
        elif lay["face"]["shape"] == "rect":
            self.fmask = np.ones((fh0, fw0, 1), np.float32)   # 28 Oct (polish): the full-width face box, edge to edge
        else:
            fm = np.ones((fh0, fw0), np.float32)
            fd = lay["face"].get("fade", 90)
            fm[fh0 - fd:, :] = np.linspace(1, 0, fd, dtype=np.float32)[:, None]
            ft = lay["face"].get("fade_top", 0)
            if ft:
                # B since 22:50: the panel starts at y 90 on the paper ground, its top edge faded in
                fm[:ft, :] *= np.linspace(0, 1, ft, dtype=np.float32)[:, None]
            self.fmask = fm[..., None]
        # the face crop as an affine map so subpixel positions hold (cv2.resize would round the crop to whole pixels);
        # 28 Oct: one map per speaker when the sidecar names a face per role (a live training: 3 people, 3 tracks)
        self.Mf = {}
        self.foot = {}
        for role, g in (fgeo.get("by_role") or {"_": fgeo}).items():
            fcx, fcy, fcw, fch = g["crop"]
            kx, ky = fw0 / fcw, fh0 / fch
            self.Mf[role] = np.array([[kx, 0, -fcx * kx], [0, ky, -fcy * ky]], np.float32)
            # 29 Oct: the panel row where the webcam's footage ends (below it the screen would show): from there down
            # the last rows are stretched and blurred to the frame's foot
            fy_ = g.get("foot_y")
            ft = int(math.floor(fy_ - fy0)) if fy_ is not None and fy_ - fy0 < fh0 - 1 else None
            px_ = g.get("pillar_x") or [0, fw0]
            xl, xr = int(math.ceil(max(0.0, px_[0]))), int(math.floor(min(float(fw0), px_[1])))
            rf = g.get("roof_y")
            rt = int(math.ceil(rf - fy0)) if rf is not None and rf - fy0 > 0 else None   # the crop above the webcam
            self.foot[role] = (ft, xl if xl > 0 else None, xr if xr < fw0 else None, rt) if (ft is not None or xl > 0 or xr < fw0 or rt) else None

    def fill_outside(self, face, ft, xl, xr, rt=None):
        """29 Oct (builder T): where the crop runs past the webcam (its sides on a small webcam, its foot above 1920), the
        webcam's own edge band is stretched over that part, blurred hard and darkened a little (the ig_native extension),
        blended over up to 40 px, so the panel is full width and runs to the frame's foot with no screen and no paper"""
        cv2 = self.cv2
        H, W = face.shape[:2]
        out = face.astype(np.float32)

        def soft(img, w, h):
            sm = cv2.resize(img, (max(2, w // 8), max(2, h // 8)), interpolation=cv2.INTER_AREA)
            sm = cv2.GaussianBlur(sm, (0, 0), 5)
            return cv2.resize(sm, (w, h), interpolation=cv2.INTER_LINEAR).astype(np.float32) * 0.86

        y1 = H if ft is None else max(8, min(H - 1, ft - 14))   # 14 px inside: the webcam's border rows never show
        if rt:
            # headroom above the webcam's top (the head sized up past it): its top rows stretched and blurred up
            y0 = min(y1 - 8, rt + 10)
            src_h = max(8, int((y1 - y0) * 0.10))
            ext = soft(face[y0:y0 + src_h], W, y0 + src_h)
            out[:y0] = ext[:y0]
            bl = min(30, src_h)
            ramp = np.linspace(1, 0, bl, dtype=np.float32)[:, None, None]
            out[y0:y0 + bl] = out[y0:y0 + bl] * (1 - ramp) + ext[y0:y0 + bl] * ramp
        if xl:
            xl = min(W - 8, xl + 10)
            bw = max(8, int((W - xl) * 0.12))
            ext = soft(face[:y1, xl:xl + bw], xl + bw, y1)
            out[:y1, :xl] = ext[:, :xl]
            bl = min(40, bw)
            ramp = np.linspace(1, 0, bl, dtype=np.float32)[None, :, None]
            out[:y1, xl:xl + bl] = out[:y1, xl:xl + bl] * (1 - ramp) + ext[:, xl:xl + bl] * ramp
        if xr:
            xr = max(8, xr - 10)
            bw = max(8, int(xr * 0.12))
            ext = soft(face[:y1, xr - bw:xr], W - xr + bw, y1)
            out[:y1, xr:] = ext[:, bw:]
            bl = min(40, bw)
            ramp = np.linspace(0, 1, bl, dtype=np.float32)[None, :, None]
            out[:y1, xr - bl:xr] = out[:y1, xr - bl:xr] * (1 - ramp) + ext[:, bw - bl:bw] * ramp
        if ft is not None and y1 < H:
            src_h = max(8, int(y1 * 0.14))
            ext = soft(np.clip(out[y1 - src_h:y1], 0, 255).astype(np.uint8), W, H - y1 + src_h)
            bl = min(40, src_h)
            ramp = np.linspace(0, 1, bl, dtype=np.float32)[:, None, None]
            # the foot settles toward the ink colour as it goes down (a designed floor, not a smear): 0.86 of the blur at the
            # footage's edge to 0.45 at 1920, mixed with the ground ink (16, 22, 25)
            g = np.linspace(1.0, 0.0, H - y1, dtype=np.float32)[:, None, None]
            ink = np.array(DARK, np.float32)[None, None, :]
            out[y1:] = ext[src_h:] * (0.52 + 0.48 * g) + ink * (0.48 - 0.48 * g)
            out[y1 - bl:y1] = out[y1 - bl:y1] * (1 - ramp) + ext[src_h - bl:src_h] * ramp
        return np.clip(out, 0, 255).astype(np.uint8)

    def frame(self, scr_src, scr_t, reg, face_src, xfj, role=None):
        cv2, lay, T = self.cv2, self.lay, self.T
        hx, hy, hw, hh = lay["hole"]
        fx0, fy0, fw0, fh0 = lay["face"]["box"]
        frame = self.ground.copy()
        s, ox, oy = xfj
        fill = lay["ground"] if lay["anchor"] else tuple(reg.get("fill") or T.get("fill") or lay["ground"])
        cs = clean_screen(scr_src, T, scr_t, self.L, rbounds(T, reg), fill)
        M = np.array([[s, 0, ox - hx], [0, s, oy - hy]], np.float32)
        warped = cv2.warpAffine(cs, M, (hw, hh), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT,
                                borderValue=tuple(int(c) for c in lay["ground"]))
        if s > 1.4:
            warped = unsharp(warped, min(0.6, 0.25 * (s - 1.0)))
        region = frame[hy:hy + hh, hx:hx + hw]
        if lay["hole_r"] <= 0:
            region[:] = warped
        else:
            region[:] = (warped * self.hmask + region * (1 - self.hmask)).astype(np.uint8)
        Mf = self.Mf.get(role) if role in self.Mf else next(iter(self.Mf.values()))
        face = cv2.warpAffine(face_src, Mf, (fw0, fh0), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
        face = unsharp(face, 0.35, 1.3)
        fk = role if role in self.foot else next(iter(self.foot))
        ft = self.foot.get(fk)
        if ft is not None:
            face = self.fill_outside(face, *ft)
        freg = frame[fy0:fy0 + fh0, fx0:fx0 + fw0]
        freg[:] = (face * self.fmask + freg * (1 - self.fmask)).astype(np.uint8)
        return frame


def faces_for(P, T, L, work):
    """the face geometry from the boxes fit_layout measured (29 Oct, builder T: cv2 Haar in the webcam region, no ffmpeg;
    the same box the layout was solved on); one per speaker when the sidecar has "faces" (a live, each person on their
    own track). The returned dict is the worst case for the checks (lowest mouth and chin, highest crown, smallest
    head), with "by_role" for the compositor."""
    boxes, regions = T["_face_boxes"], T["_face_regions"]
    files = {role: f for role, f, reg, box, pcs in face_specs(P, T)}
    by = {}
    for role, fb in boxes.items():
        g = face_geom(L, fb, regions[role])
        g["file"] = files[role]
        by[role] = g
        log(work, f"face {role}: box {[round(v) for v in fb]} in {Path(files[role]).name}; crop {[round(v) for v in g['crop']]} x{g['k']:.2f}, "
                  f"mouth {g['mouth_y']:.0f}, chin {g.get('chin_y', g['face_bottom']):.0f}, crown {g.get('crown_y', 0):.0f}, foot {g.get('foot_y', 0):.0f}"
                  + (" CROWN TIGHT" if g.get("crown_cut") else ""))
    if not T.get("faces"):
        return next(iter(by.values()))
    worst = dict(next(iter(by.values())))
    for k_, f_ in (("mouth_y", max), ("face_bottom", max), ("chin_y", max), ("face_top", min), ("crown_y", min), ("head_px", min)):
        vals = [g[k_] for g in by.values() if k_ in g]
        if vals:
            worst[k_] = f_(vals)
    worst["crown_cut"] = any(g.get("crown_cut") for g in by.values())
    worst["by_role"] = by
    return worst


def render_base(S, P, T, L, regs, xf, idxs, fgeo, work, speed, nfr):
    """the base video at OUTPUT timing (the speed is applied here, frame by frame): ground, screen, face."""
    lay = LAYOUTS[L]
    scr_file = T["screen_file"]
    face_file = T.get("face_file") or scr_file
    by_role = fgeo.get("by_role") or {}
    si, fi = PL.info(scr_file), PL.info(face_file)
    srng = "pc" if si["range"] == "pc" or si["pix"].startswith("yuvj") else "tv"
    frng = "pc" if fi["range"] == "pc" or fi["pix"].startswith("yuvj") else "tv"
    rec = {"v": CODE_V, "L": L, "xf": key_of(xf), "regs": [(r.get("src_at"), r["t0"], r.get("bounds"), r.get("fill")) for r in regs],
           "masks": T.get("private_masks"), "bounds": T["bounds"], "fill": T.get("fill"),
           "items": [(it["a"], it["n"], it["out"]) for it in P["items"]], "speed": speed, "fgeo": fgeo["crop"], "files": [scr_file, face_file],
           "by_role": {r: [g["crop"], g["file"]] for r, g in by_role.items()}}
    out = work / f"base-{L}-{key_of(rec)}.mp4"
    if out.exists() and abs(PL.duration(out) - nfr / FPS) < 0.08:
        return out
    comp = Compositor(L, T, fgeo, si["w"], si["h"])
    stills = {}
    tmp = str(out) + ".part.mp4"
    enc = subprocess.Popen([FF, "-nostdin", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{VW}x{VH}", "-r", str(FPS), "-i", "-",
                            "-vf", "scale=in_range=pc:out_range=tv:in_color_matrix=bt709:out_color_matrix=bt709,format=yuv420p",
                            "-c:v", "h264_videotoolbox", "-allow_sw", "1", "-profile:v", "high", "-b:v", "26M", "-maxrate", "36M", "-bufsize", "52M",
                            "-color_range", "tv", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-an", tmp],
                           stdin=subprocess.PIPE)
    items = [it for it in P["items"] if it["kind"] != "card"]
    readers = {}
    t_start = time.time()
    try:
        for j in range(nfr):
            tb = (j / FPS) * speed
            it = items[-1]
            for x in items:
                if x["out"] <= tb + 1e-6 < x["out"] + x["n"] / FPS:
                    it = x
                    break
            kk = min(it["n"] - 1, max(0, int(round((tb - it["out"]) * FPS))))
            src_t = it["a"] + kk / FPS
            key = id(it)
            if key not in readers:
                for r in readers.values():
                    r["s"].close()
                    if r.get("f"):
                        r["f"].close()
                readers.clear()
                rs = {"s": Reader(scr_file, it["a"], it["n"] / FPS, si["w"], si["h"], srng)}
                ffile = by_role[it.get("speaker")]["file"] if it.get("speaker") in by_role else face_file
                if ffile != scr_file:
                    ii = PL.info(ffile)
                    irng = "pc" if ii["range"] == "pc" or ii["pix"].startswith("yuvj") else "tv"
                    rs["f"] = Reader(ffile, it["a"], it["n"] / FPS, ii["w"], ii["h"], irng)
                readers[key] = rs
            rs = readers[key]
            live = rs["s"].get(kk)
            face_src = rs["f"].get(kk) if rs.get("f") else live
            reg = regs[idxs[j]]
            if reg.get("src_at") is not None:
                sa = float(reg["src_at"])
                if sa not in stills:
                    stills[sa] = still(scr_file, sa, si["w"], si["h"], srng)
                scr_src, scr_t = stills[sa], sa
            else:
                scr_src, scr_t = live, src_t
            enc.stdin.write(comp.frame(scr_src, scr_t, reg, face_src, xf[j], it.get("speaker")).tobytes())
            if j % 150 == 0:
                log(work, f"base {L}: frame {j}/{nfr} ({time.time() - t_start:.0f} s)")
    finally:
        for r in readers.values():
            r["s"].close()
            if r.get("f"):
                r["f"].close()
        enc.stdin.close()
        enc.wait(timeout=600)
    if enc.returncode != 0:
        raise RuntimeError(f"base encode failed ({enc.returncode})")
    os.replace(tmp, out)
    return out


def preview_still(spec_path, L, png, t_out, out_png, face_png=None):
    """ONE frame of the look with no ffmpeg at all: the screen and the face from PNGs already on disk, the overlay page
    through Playwright at t_out, captions drawn with PIL at the libass block's measured place (a preview, never shipped)."""
    import cv2
    S, T, tpath, P, speed, regs, total, V, nfr, xf, idxs = prepare(spec_path, L)
    j = min(nfr - 1, int(round(t_out * FPS)))
    src = np.asarray(Image.open(png).convert("RGB"))
    fsrc = np.asarray(Image.open(face_png).convert("RGB")) if face_png else src
    H, W = src.shape[:2]
    # 29 Oct (builder T): the face box the layout was solved on (fit_layout, cv2 on the video), not a Haar on this PNG,
    # so the still shows exactly the crop the build will use
    role0 = next(iter(T["_face_boxes"]))
    fb = T["_face_boxes"][role0]
    fgeo = face_geom(L, fb, T["_face_regions"][role0])
    reg = regs[idxs[j]]
    frame = Compositor(L, T, fgeo, W, H).frame(src, float(reg.get("src_at") or regs[idxs[j]]["at"]), reg, fsrc, xf[j])
    SPEED[0] = speed
    payload = payload_for(S, T, L, regs, xf, total)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        try:
            br = pw.chromium.launch(channel="chrome")
        except Exception:
            br = pw.chromium.launch()
        pg = br.new_page(viewport={"width": VW, "height": VH}, device_scale_factor=1)
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        PL.open_page(pg, TUT_HTML)   # 2 Nov 2026: the page's tokens filled, file:/// URLs remapped, every font face loaded
        setup = pg.evaluate("(p) => window.setup(p)", payload)
        sig = pg.evaluate("(t) => window.setTime(t)", j / FPS)
        ov_path = Path(str(out_png) + ".overlay.png")
        pg.screenshot(path=str(ov_path), omit_background=True)
        br.close()
    base = Image.fromarray(frame).convert("RGBA")
    comp = Image.alpha_composite(base, Image.open(ov_path).convert("RGBA"))
    # captions: the group on screen at t_out, Montserrat Bold at the PIL size whose capital measures 47 px
    groups = groups_for(P, S, L)
    gnow = [gg for gg in groups if gg["s"] / speed <= j / FPS < gg["e"] / speed]
    if gnow:
        from PIL import ImageDraw
        gg = gnow[0]
        d = ImageDraw.Draw(comp)
        f = ImageFont.truetype(str(FONTDIR / "Montserrat-Bold.ttf"), 67 if gg["style"] == "Cap" else 76)
        lines = [" ".join(gg["w"][k][0] for k in ln) for ln in gg["lines"]]
        lh = int(f.size * 1.22)
        c = LAYOUTS[L]["cap"]
        y = (VH - c["marginV"] - lh * len(lines)) if c["align"] == 2 else c["marginV"]
        for ln in lines:
            w = d.textlength(ln, font=f)
            if c.get("box"):
                # the ASS opaque box (BorderStyle 3, padding 10) approximated: 75 % black behind the line's ink
                bb = d.textbbox((540 - w / 2, y), ln, font=f)
                ov = Image.new("RGBA", comp.size, (0, 0, 0, 0))
                ImageDraw.Draw(ov).rectangle([bb[0] - 10, bb[1] - 10, bb[2] + 10, bb[3] + 10], fill=(16, 16, 16, 191))
                comp.alpha_composite(ov)
                d = ImageDraw.Draw(comp)
                d.text((540 - w / 2, y), ln, font=f, fill=(255, 255, 255))
            else:
                d.text((540 - w / 2, y), ln, font=f, fill=(255, 255, 255), stroke_width=4, stroke_fill=(10, 10, 10))
            y += lh
    comp.convert("RGB").save(out_png)
    return {"t": round(j / FPS, 3), "region": reg.get("label"), "scale": round(xf[j][0], 2), "setup": setup, "errors": errs, "face": fb,
            "mouth_y": round(fgeo["mouth_y"]), "chin_y": round(fgeo.get("chin_y", 0)), "crown_y": round(fgeo.get("crown_y", 0)),
            "foot_y": round(fgeo.get("foot_y", 0)), "crown_cut": fgeo.get("crown_cut"), "k": round(fgeo["k"], 2), "hole": LAYOUTS[L]["hole"],
            "face_panel": LAYOUTS[L]["face"]["box"], "caption": [" ".join(w[0] for w in gg["w"]) for gg in gnow]}


def key_of(obj):
    return hashlib.sha1(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()[:12]


# ---------------------------------------------------------------- captions
def groups_for(P, S, L):
    """the caption groups for the layout (27 Oct 22:50, the tutorial fixer, round-1 verdicts 22:30 and the creator's defaults):
    pipeline.caption_groups gives the words (cleaned, capitalised, in output time, never across a piece); this lays them
    out again with a shortest-path search per block of words (one speaker, under 1.5 s apart), so that
      - no line holds 1 word and none is on screen under 0.3 s after the speed (a lone word joins its neighbour line,
        across a cut or a pause when it must: tutorial-3 'so,' and 'Great.', tutorial-2 'That's,');
      - no line is drawn wider than 760 px (x 160..920, never past 930: tutorial-1 'in for longer-running'
        ran x 88..989), and a Big line (the first 8 s) that does not fit steps down to the Cap size;
      - in A and C every group is ONE line (the face sits behind the block), in B up to 2 lines of 2 words or more;
      - groups never overlap in time (tutorial-3 tutC 7.39: 'and this' and 'is a really' were on screen together, and
        libass stacked the second a line higher, on his chin)."""
    base = PL.caption_groups(P, S)
    speed = PL.spec_speed(S)
    one = bool(LAYOUTS[L]["cap"].get("one_line"))
    pieces = [(it["out"], it["out"] + it["n"] / FPS) for it in (P.get("runs") or P["items"]) if it["kind"] != "card"]

    def piece_of(t):
        for i, (a, b) in enumerate(pieces):
            if a - 0.02 <= t <= b + 0.02:
                return i
        return -1
    W = []   # one dict per word, in output seconds (1.0x)
    for g in base:
        for k, w in enumerate(g["w"]):
            W.append({"t": w[0], "s": float(w[1]), "e": float(w[2]), "gs": float(g["s"]) if k == 0 else None,
                      "ge": float(g["e"]) if k == len(g["w"]) - 1 else None, "spk": g.get("spk"), "agent": bool(g.get("agent")),
                      "pc": piece_of((float(w[1]) + float(w[2])) / 2.0), "pend": g.get("piece_end")})
    if not W:
        return []
    blocks, cur = [], [0]
    for i in range(1, len(W)):
        a, b = W[i - 1], W[i]
        if b["spk"] == a["spk"] and b["agent"] == a["agent"] and b["s"] - a["e"] <= 1.5:
            cur.append(i)
        else:
            blocks.append(cur)
            cur = [i]
    blocks.append(cur)
    # a block of 1 word joins its nearest neighbour block of the same voice (up to 4 s away)
    changed = True
    while changed:
        changed = False
        for bi, bl in enumerate(blocks):
            if len(bl) != 1 or len(blocks) == 1:
                continue
            w = W[bl[0]]
            opts = []
            if bi > 0 and W[blocks[bi - 1][-1]]["spk"] == w["spk"] and W[blocks[bi - 1][-1]]["agent"] == w["agent"]:
                opts.append((w["s"] - W[blocks[bi - 1][-1]]["e"], bi - 1))
            if bi + 1 < len(blocks) and W[blocks[bi + 1][0]]["spk"] == w["spk"] and W[blocks[bi + 1][0]]["agent"] == w["agent"]:
                opts.append((W[blocks[bi + 1][0]]["s"] - w["e"] + 0.01, bi + 1))
            opts = [o for o in opts if o[0] <= 4.0]
            if not opts:
                continue
            _, nb = min(opts)
            lo, hi = min(bi, nb), max(bi, nb)
            blocks = blocks[:lo] + [blocks[lo] + blocks[hi]] + blocks[hi + 1:]
            changed = True
            break

    def start_of(i):
        w = W[i]
        return w["gs"] if w["gs"] is not None else w["s"] - 0.06

    def layout_line(texts, t0):
        """(style, lines, cost) or None: the size ladder Big (first 8 s) then Cap; one line or 2 balanced lines"""
        big = t0 < 8.0
        sizes = [(118, "Big"), (104, "Cap")] if big else [(104, "Cap")]
        best = None
        for size, st in sizes:
            for mw, extra in ((CAP_LINE_SOFT, 0), (CAP_LINE_MAX, 3)):
                if one:
                    ln = [list(range(len(texts)))] if PL.drawn_width(" ".join(texts), size) <= mw else None
                else:
                    ln = PL.two_lines(texts, size, mw)
                    if ln is not None and len(ln) == 2 and len(texts) >= 2 and min(len(x) for x in ln) < 2:
                        ln = None
                if ln is not None:
                    c = extra + (2 if (big and st == "Cap") else 0)
                    if best is None or c < best[2]:
                        best = (st, ln, c)
                    break
        return best
    NO_END = PL.NO_END
    out = []
    for bl in blocks:
        n = len(bl)
        block_end = next((W[i]["ge"] for i in reversed(bl) if W[i]["ge"] is not None), W[bl[-1]]["e"] + 0.16)

        def cost(i, j):
            idx = bl[i:j]
            texts = [W[k]["t"] for k in idx]
            nw = len(texts)
            if nw > (7 if one else 9):
                return None
            st0 = start_of(idx[0])
            lay = layout_line(texts, st0)
            penalty = 0.0
            if lay is None:
                if nw > 1:
                    return None
                lay, penalty = ("Cap", [[0]], 0), 100000.0     # one word wider than the line: never chosen while any split exists
            en = (start_of(bl[j]) - 0.01) if j < n else block_end
            c = 1.0 + lay[2] + penalty
            if nw < 2 and n >= 2:
                c += 1000
            if (en - st0) / speed < 0.30:
                c += 500
            lo, hi = (3, 5) if one else (4, 7)
            if nw < lo:
                c += 2.0 * (lo - nw)
            if nw > hi:
                c += 3.0 * (nw - hi)
            last = texts[-1]
            if j < n and re.sub(r"[^a-z']", "", last.lower()) in NO_END:
                c += 4
            if re.search(r"[,.?!;:]$", last):
                c -= 2
            if any(re.search(r"[.?!]$", t) for t in texts[:-1]):
                c += 3
            pcs = [W[k]["pc"] for k in idx]
            if len(set(pcs)) > 1:
                c += 8
            return c, lay
        best = [None] * (n + 1)
        best[0] = (0.0, None, None)
        for j in range(1, n + 1):
            for i in range(max(0, j - (7 if one else 9)), j):
                if best[i] is None:
                    continue
                r = cost(i, j)
                if r is None:
                    continue
                c = best[i][0] + r[0]
                if best[j] is None or c < best[j][0]:
                    best[j] = (c, i, r[1])
        if best[n] is None:
            raise SystemExit(f"captions: no layout for the block starting {W[bl[0]]['t']!r} at {W[bl[0]]['s']:.2f}")
        cuts, j = [], n
        while j > 0:
            c, i, lay = best[j]
            cuts.append((i, j, lay))
            j = i
        cuts.reverse()
        for ci, (i, j, lay) in enumerate(cuts):
            idx = bl[i:j]
            s0 = start_of(idx[0])
            e0 = (start_of(bl[j]) - 0.01) if j < n else block_end
            out.append({"style": "Agent" if W[idx[0]]["agent"] else lay[0], "s": s0, "e": e0,
                        "w": [(W[k]["t"], (s0 if q == 0 else W[k]["s"]), W[k]["e"]) for q, k in enumerate(idx)],
                        "lines": lay[1], "piece_end": W[idx[-1]]["pend"], "agent": W[idx[0]]["agent"], "spk": W[idx[0]]["spk"],
                        "pieces": sorted(set(W[k]["pc"] for k in idx))})
    out.sort(key=lambda g: g["s"])
    for i in range(len(out) - 1):     # never two caption events on screen at once
        if out[i]["e"] > out[i + 1]["s"] - 0.01:
            out[i]["e"] = out[i + 1]["s"] - 0.01
        # a line whose words all sit before a cut leaves at the cut (it held on to the next line's start, up to 0.06 s
        # past it), unless that would put it on screen under 0.3 s
        lp = out[i]["pieces"][-1]
        if lp >= 0 and lp not in out[i + 1]["pieces"]:
            cut = pieces[lp][1] - 1.0 / FPS
            if out[i]["s"] + 0.3 * speed <= cut < out[i]["e"]:
                out[i]["e"] = cut
    return out


def style_lines(L):
    c = LAYOUTS[L]["cap"]
    cap = PL.STYLE_CAP.split(",")
    big = PL.STYLE_BIG.split(",")
    for st in (cap, big):
        st[18] = str(c["align"])    # Alignment
        st[21] = str(c["marginV"])  # MarginV
        if c.get("box"):
            # 28 Oct (polish, I: "white captions on top of light background is not gonna work. Put a box around them"): an
            # opaque dark box (BorderStyle 3) behind the line on the paper ground; the box and shadow colours both dark
            st[5] = "&H40101010"    # OutlineColour (the box, 75 % opaque)
            st[6] = "&H40101010"    # BackColour
            st[15] = "3"            # BorderStyle: opaque box
            st[16] = "10"           # Outline: the box's padding
            st[17] = "0"            # Shadow
    return ",".join(cap), ",".join(big)


def ass_for(groups, speed, L):
    txt = PL.ass_text(groups, speed)
    cap, big = style_lines(L)
    txt = txt.replace(PL.STYLE_CAP, cap).replace(PL.STYLE_BIG, big)
    return txt


def caption_boxes(ass_path, groups, speed, work, L):
    """the drawn caption block of every group, measured by burning the ASS alone on black at each group's middle."""
    ns = [int(round(((g["s"] + g["e"]) / 2) / speed * FPS)) for g in groups]
    if not ns:
        return []
    uniq = sorted(set(ns))
    dur = max(uniq) / FPS + 0.5
    sel = "+".join(f"eq(n,{n})" for n in uniq)
    d = work / f"capbox-{L}"
    d.mkdir(exist_ok=True)
    PL.run([FF, "-y", "-v", "error", "-f", "lavfi", "-i", f"color=c=black:s={VW}x{VH}:r={FPS}:d={dur:.2f}", "-vf",
            f"ass='{ass_path}':fontsdir='{FONTDIR}',select='{sel}',format=gray", "-fps_mode", "passthrough", str(d / "c%03d.png")],
           timeout=600, label="caption boxes")
    got = {}
    for i, n in enumerate(uniq):
        p = d / f"c{i + 1:03d}.png"
        if not p.exists():
            continue
        a = np.asarray(Image.open(p)) > 128
        ys, xs = np.where(a)
        got[n] = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())] if len(ys) else None
    return [got.get(n) for n in ns]


# ---------------------------------------------------------------- payload
def payload_for(S, T, L, regs, xf, total):
    lay = LAYOUTS[L]
    marks, dims = [], []
    card = None
    cside = T.get("card")
    for r in regs:
        for m in r["marks"]:
            if m.get("kind") == "none":
                continue
            marks.append({"box": m["box"], "kind": m.get("kind", "outline"), "t0": m["t0"], "t1": m["t1"], "label": m.get("label"),
                          "region": r["idx"], "mark_id": m.get("id"), "grow": round(float(m["grow"]) / SPEED[0], 3) if m.get("grow") else None})
        if L == "C" or r.get("dim"):
            # C: everything but the line is dimmed; the dim follows the first mark of the region, else its focus
            # a region whose mark is a wash ("ignore all of this") dims everything, the code included: no hole
            # A and B take the same dim (a paper veil, tutorial.html COL) on a region marked "dim": true
            # (tutorial-3 tutA verdict: "borrow C's dim wash into A for 1010.6..1016.2")
            first = r["marks"][0].get("kind") if r["marks"] else None
            box = None if first == "wash" else (r["marks"][0]["box"] if first and first != "none" else r["focus"])
            d1 = r["t1"]
            if r["marks"] and r["marks"][0].get("until"):
                d1 = min(d1, r["marks"][0]["t1"])     # the dim leaves with a mark that has its own end (the screen changed)
            dims.append({"box": box, "t0": r["t0"], "t1": d1, "alpha": 0.62 if L == "C" else 0.70})
    if cside:
        ci = None
        cands = [(abs(m["t0"] - T["_card_t"][0]), i) for i, m in enumerate(marks) if cside.get("points_to") and m.get("mark_id") == cside["points_to"]]
        if cands:
            ci = min(cands)[1]
        card = {"eyebrow": cside["eyebrow"], "line": cside["line"], "mark": ci, "t0": T["_card_t"][0], "t1": T["_card_t"][1]}
    return {"layout": L, "fps": FPS, "duration": round(total, 3), "title": S["title"], "title_accent": S.get("title_accent") or "",
            "credit": CREDIT, "hole": lay["hole"], "hole_r": lay["hole_r"], "face": lay["face"], "title_box": lay["title"],
            "xf": xf, "marks": marks, "dims": dims, "card": card, "credit_mode": "title", "spec_id": S["id"]}


# ---------------------------------------------------------------- checks
def run_tut_checks(S, P, T, L, regs, xf, idxs, fgeo, final, work, speed, ass_path, groups, seq, setup, payload, nfr):
    checks = {}
    # 1. caption capitals at the floor, both styles as burned (the shorts-editor check, the layout's own style lines)
    cap, big = style_lines(L)
    for name, st, floor in (("Cap", cap, 47), ("Big", big, 53)):
        r = subprocess.run([sys.executable, str(SK / "check_caption_size.py"), "--style", st, "--fontsdir", str(FONTDIR)],
                           capture_output=True, text=True, cwd=str(work))
        px = int(r.stdout.split("cap height ")[1].split("px")[0]) if "cap height" in r.stdout else 0
        checks[f"caption_{name}_px"] = px
        checks[f"caption_{name}_ok"] = px >= floor
    # 2. the caption block inside the layout's caption area, every group; never across a cut
    x0, y0, x1, y1 = LAYOUTS[L]["cap"]["area"]
    boxes = caption_boxes(ass_path, groups, speed, work, L)
    bad = [[i, b] for i, b in enumerate(boxes) if b is None or b[0] < x0 - 4 or b[2] > x1 + 4 or b[1] < y0 - 4 or b[3] > y1]
    checks["caption_boxes"] = {"n": len(boxes), "top_min": min([b[1] for b in boxes if b] or [0]), "bottom_max": max([b[3] for b in boxes if b] or [0]),
                               "left_min": min([b[0] for b in boxes if b] or [0]), "right_max": max([b[2] for b in boxes if b] or [0]), "outside": bad[:6]}
    checks["caption_area_ok"] = not bad
    pieces = [(it["out"], it["out"] + it["n"] / FPS) for it in P["items"] if it["kind"] != "card"]
    across = [g for g in groups if not any(a - 0.02 <= g["s"] and g["e"] <= b + 0.02 for a, b in pieces)]
    # a group runs across a cut only to rescue a lone word or a line under 0.3 s (the creator's caption default): a
    # crossing with 2 words or more on each side of the cut and both sides 0.3 s or longer is a fault
    def needless(g):
        sides = {}
        for w in g["w"]:
            k = next((i for i, (a, b) in enumerate(pieces) if a - 0.02 <= w[1] <= b + 0.02), -1)
            sides.setdefault(k, []).append(w)
        if len(sides) < 2:
            return False
        return all(len(ws) >= 2 and (ws[-1][2] - ws[0][1]) / speed >= 0.3 for ws in sides.values())
    checks["caption_cut_ok"] = not any(needless(g) for g in across)
    checks["caption_across_cut"] = [[round(g["s"] / speed, 2), " ".join(w[0] for w in g["w"])] for g in across][:8]
    # (the creator's defaults, round-1 verdicts): no caption line of 1 word, none on screen under 0.3 s, never 2 at once
    faults = PL.caption_line_faults(groups, None, speed)
    checks["caption_line_faults"] = faults[:10]
    checks["caption_lines_ok"] = not faults
    over = [[round(groups[i]["e"] / speed, 2), round(groups[i + 1]["s"] / speed, 2)] for i in range(len(groups) - 1) if groups[i + 1]["s"] < groups[i]["e"]]
    checks["caption_overlaps"] = over[:6]
    checks["caption_overlap_ok"] = not over
    checks["caption_one_line_ok"] = (not LAYOUTS[L]["cap"].get("one_line")) or all(len(g["lines"]) == 1 for g in groups)
    # 3. the face: big (a third of the frame or more), the mouth above 1500, and clear of the caption block's top
    fb = LAYOUTS[L]["face"]["box"]
    checks["face"] = {"panel": fb, "crop": [round(v, 1) for v in fgeo["crop"]], "scale": round(fgeo["k"], 2), "mouth_y": round(fgeo["mouth_y"]),
                      "face_top": round(fgeo["face_top"]), "face_bottom": round(fgeo["face_bottom"]), "head_px": round(fgeo["head_px"])}
    checks["face_big_ok"] = fb[3] >= 640 and fgeo["head_px"] >= 300
    checks["mouth_ok"] = fgeo["mouth_y"] <= 1500
    ctop = checks["caption_boxes"]["top_min"]
    checks["mouth_clear_of_captions"] = bool(fgeo["mouth_y"] + 18 <= ctop) if LAYOUTS[L]["face"]["box"][1] + LAYOUTS[L]["face"]["box"][3] > 1190 else True
    # and the chin (the face box's foot) clear of the caption block too, where the block sits on the face panel
    checks["chin_clear_of_captions"] = bool(fgeo["face_bottom"] + 6 <= ctop) if LAYOUTS[L]["face"]["box"][1] + LAYOUTS[L]["face"]["box"][3] > 1190 else True
    # 4. the marked text reads at 375 px wide: cap px x the scale while the mark is up x 375/1080 >= 9
    reads = []
    for r in regs:
        for m in r["marks"]:
            if not m.get("read", True) or m.get("kind") == "none":
                continue
            j0, j1 = int(m["t0"] * FPS), max(int(m["t0"] * FPS) + 1, int(m["t1"] * FPS))
            j0 = min(nfr - 1, j0 + 12)   # after the spring has landed
            ss = [xf[j][0] for j in range(j0, min(nfr, j1))] or [xf[min(nfr - 1, j0)][0]]
            cp = m.get("cap_px", T.get("text_cap_px", 9))
            px375 = cp * min(ss) * 375.0 / 1080.0
            reads.append({"mark": m.get("id") or m.get("kind"), "at": m["t0"], "cap_src": cp, "scale": round(min(ss), 2), "px_at_375": round(px375, 1), "ok": px375 >= READ_PX})
    checks["marks_read"] = reads
    checks["marks_read_ok"] = all(x["ok"] for x in reads)
    # 5. private UI outside every crop: the visible source rect (crop inside the layout's hole, cut to bounds) never meets
    #    a private rect unless a mask covers it at that source time
    hx, hy, hw, hh = LAYOUTS[L]["hole"]
    hits = []
    for j in range(0, nfr, 3):
        bx, by, bw, bh = rbounds(T, regs[idxs[j]])
        s, ox, oy = xf[j]
        vx0, vy0 = (hx - ox) / s, (hy - oy) / s
        vx1, vy1 = vx0 + hw / s, vy0 + hh / s
        vx0, vy0, vx1, vy1 = max(vx0, bx), max(vy0, by), min(vx1, bx + bw), min(vy1, by + bh)
        if vx1 <= vx0 or vy1 <= vy0:
            continue
        reg = regs[idxs[j]]
        tb = (j / FPS) * speed
        it = next((x for x in P["items"] if x["out"] <= tb < x["out"] + x["n"] / FPS), P["items"][-1])
        src_t = float(reg["src_at"]) if reg.get("src_at") is not None else it["a"] + (tb - it["out"])
        for pr in T.get("private") or []:
            if pr.get("between") and not (float(pr["between"][0]) <= src_t <= float(pr["between"][1])):
                continue
            px, py, pw, ph = pr["box"]
            if px < vx1 and px + pw > vx0 and py < vy1 and py + ph > vy0:
                covered = any(m["box"][0] <= px and m["box"][1] <= py and m["box"][0] + m["box"][2] >= px + pw and m["box"][1] + m["box"][3] >= py + ph
                              and (not m.get("between") or float(m["between"][0]) <= src_t <= float(m["between"][1])) for m in T.get("private_masks") or [])
                if not covered:
                    hits.append({"t": round(j / FPS, 2), "what": pr.get("what"), "src_t": round(src_t, 2)})
    checks["private_hits"] = hits[:10]
    checks["private_ok"] = not hits
    # 6. the screen on frame every second of an answer piece: at least half the hole shows in-bounds screen
    gaps = []
    for sec in range(int(nfr / FPS) + 1):
        j = min(nfr - 1, sec * FPS)
        bx, by, bw, bh = rbounds(T, regs[idxs[j]])
        s, ox, oy = xf[j]
        vx0, vy0 = (hx - ox) / s, (hy - oy) / s
        vx1, vy1 = vx0 + hw / s, vy0 + hh / s
        iw = max(0.0, min(vx1, bx + bw) - max(vx0, bx))
        ih = max(0.0, min(vy1, by + bh) - max(vy0, by))
        frac = (iw * ih) / ((vx1 - vx0) * (vy1 - vy0))
        need = 0.5 if not LAYOUTS[L]["anchor"] else 0.12
        if frac < need:
            gaps.append([sec, round(frac, 2)])
    checks["screen_every_second"] = gaps[:8]
    checks["screen_on_ok"] = not gaps
    # 7. our layer inside the safe frame: the title in the band, the card above 960 (or left of 905 below it), the credit
    #    above 1500 and left of 905, the marks left of 905 below 960; then the layer's own pixels in the top 230 and the rail
    st = setup or {}
    geo_bad = []
    if (st.get("title_top") or 0) < 230 or (st.get("title_bottom") or 9999) > LAYOUTS[L]["title"]["max_bottom"] + 4 or st.get("title_overflow"):
        geo_bad.append({"title": [st.get("title_top"), st.get("title_bottom"), st.get("title_overflow")]})
    cr = st.get("card_rect")
    if cr and (cr[1] < 230 or (cr[1] + cr[3] > 960 and cr[0] + cr[2] > 905) or cr[0] + cr[2] > 1040 or cr[0] < 30):
        geo_bad.append({"card": cr})
    kr = st.get("credit_rect")
    if kr and (kr[1] + kr[3] > 1500 or (kr[1] + kr[3] > 960 and kr[0] + kr[2] > 905) or kr[1] < 230):
        geo_bad.append({"credit": kr})
    # (tutorial-3 tutA and tutC: the credit pill covered the card and the screen): the credit sits in the title's
    # own box, and never meets the face panel, the card or (A, B) the screen card
    def meets(r1, r2):
        return r1 and r2 and r1[0] < r2[0] + r2[2] and r1[0] + r1[2] > r2[0] and r1[1] < r2[1] + r2[3] and r1[1] + r1[3] > r2[1]
    cbad = []
    if kr:
        if meets(kr, LAYOUTS[L]["face"]["box"]):
            cbad.append("face panel")
        if cr and meets(kr, cr):
            cbad.append("card")
        if L != "C" and meets(kr, LAYOUTS[L]["hole"]):
            cbad.append("screen card")
        if not ((st.get("title_top") or 0) - 12 <= kr[1] and kr[1] + kr[3] <= max(st.get("title_bottom") or 0, LAYOUTS[L]["title"]["max_bottom"]) + 12):
            cbad.append("outside the title box")
    # 29 Oct (tutorial-2 tutB verdict: the card under his chin on the jacket): a card never meets the face
    # panel; and the head is whole (the crop never starts below the hair top)
    if cr and meets(cr, LAYOUTS[L]["face"]["box"]):
        geo_bad.append({"card_on_face": cr})
    checks["crown_ok"] = not fgeo.get("crown_cut")
    checks["credit_rect"] = kr
    checks["credit_clear"] = cbad
    checks["credit_ok"] = (not CREDIT) or (bool(kr) and not cbad)   # no credit configured: nothing to place
    checks["graphic_type_min"] = [st.get("type_min"), st.get("type_min_where")]
    checks["graphic_type_ok"] = st.get("type_min") is not None and float(st["type_min"]) >= 44 - 0.01
    checks["title_burned"] = [S["id"], S["title"]]
    for m in payload["marks"]:
        j = min(nfr - 1, int(m["t0"] * FPS) + 12)
        s, ox, oy = xf[j]
        x, y, w, h = m["box"]
        rx0, ry1, rx1 = x * s + ox, (y + h) * s + oy, (x + w) * s + ox
        if ry1 > 960 and rx1 > 905 + 12 and L != "B":
            geo_bad.append({"mark_rail": [m.get("mark_id"), round(rx1), round(ry1)]})
    checks["layer_geometry"] = geo_bad
    ink_bad, seen = [], set()
    a_, ad_ = ACC.lstrip("#").upper(), ACC_DARK.lstrip("#").upper()   # our layer's inks: the title ink, the accents, white
    cols = {"A": ["1C1C1E", ad_, "FFFFFF"], "B": ["1C1C1E", ad_, "FFFFFF"], "C": ["FFFFFF", a_, ad_]}[L]
    for png in sorted(Path(seq).glob("*.png")):
        ino = png.stat().st_ino
        if ino in seen:
            continue
        seen.add(ino)
        a = np.asarray(Image.open(png).convert("RGBA"))
        near = np.zeros(a.shape[:2], bool)
        for hx_ in cols:
            near |= np.abs(a[:, :, :3].astype(int) - np.array([int(hx_[i:i + 2], 16) for i in (0, 2, 4)])).sum(axis=2) < 60
        ink = (a[:, :, 3] > 200) & near
        top = int(ink[:228, :].sum())
        rail = int(ink[960:1500, 910:].sum())
        low = int(ink[1502:, :].sum())
        if top > 300 or rail > 300 or low > 300:
            ink_bad.append({"frame": png.name, "top_px": top, "rail_px": rail, "low_px": low})
    checks["safe_ink_layer"] = ink_bad[:8]
    checks["safe_layer_ok"] = not ink_bad and not geo_bad
    # 8. the shorts-editor safe-area test on the finished video: the face test (mouth and chin above 1500) is the check;
    #    bright footage outside the frame is a warning (a white screen is footage, not our ink)
    r = subprocess.run([sys.executable, str(SK / "check_safe_area.py"), str(final)], capture_output=True, text=True, timeout=900)
    lines = r.stdout.strip().splitlines()
    checks["safe_area_report"] = lines[-6:]
    checks["safe_face_ok"] = not any("FAIL: the face" in ln for ln in lines) and any("face found in" in ln for ln in lines)
    checks["safe_ink_footage_warning"] = [ln.strip() for ln in lines if ln.strip().endswith("outside the safe area")][:6]
    # 9. caption coverage (the pipeline's rule): every spoken piece has words under it
    spoken = [(it["out"] / speed, (it["out"] + it["n"] / FPS) / speed) for it in P["items"] if it["kind"] != "card"]
    covered, unc = 0.0, []
    for a, b in spoken:
        c = sum(max(0.0, min(b, g["e"] / speed) - max(a, g["s"] / speed)) for g in groups)
        covered += c
        if (b - a) > 1.5 and c < 0.3 * (b - a):
            unc.append([round(a, 2), round(b, 2), round(c, 2)])
    tot = sum(b - a for a, b in spoken) or 1.0
    checks["caption_coverage"] = round(covered / tot, 3)
    checks["caption_coverage_ok"] = not unc and checks["caption_coverage"] >= 0.5
    # 10. duration, peak, loudness
    secs = PL.duration(final)
    checks["seconds"] = round(secs, 2)
    checks["under_60_ok"] = secs <= 60.0 or bool(S.get("notes"))
    checks["true_peak_dbtp"] = PL.true_peak(final)
    checks["true_peak_ok"] = checks["true_peak_dbtp"] <= -1.4
    checks["lufs"] = PL.lufs_of(final)
    checks["lufs_ok"] = checks["lufs"] is not None and abs(checks["lufs"] + 14.0) <= 1.0
    checks["title_fits_ok"] = not any("title" in g for g in geo_bad)
    keys = ("caption_Cap_ok", "caption_Big_ok", "caption_area_ok", "caption_cut_ok", "face_big_ok", "mouth_ok", "marks_read_ok", "private_ok",
            "screen_on_ok", "safe_layer_ok", "safe_face_ok", "caption_coverage_ok", "under_60_ok", "true_peak_ok", "lufs_ok", "title_fits_ok",
            "caption_lines_ok", "caption_overlap_ok", "caption_one_line_ok", "mouth_clear_of_captions", "chin_clear_of_captions", "credit_ok",
            "graphic_type_ok", "crown_ok")
    checks["ok"] = all(checks.get(k, False) for k in keys)
    return checks


# ---------------------------------------------------------------- build
def prepare(spec_path, L):
    spec_path = PATHS.remap(str(spec_path))   # a queue file may hold spec paths written on another machine (paths.py)
    S = PL.load_spec(spec_path)
    T, tpath = load_side(spec_path, S)
    S["_look"] = "operator"
    P = PL.plan(S, None)
    speed = PL.spec_speed(S)
    SPEED[0] = speed
    regs, total = timeline(S, P, T, speed)
    T["_face_boxes"], T["_face_regions"] = fit_layout(L, T, P)   # 29 Oct: the layout solved on the measured face first
    V = views(L, regs, T)
    nfr = int(round(P["total_n"] / speed))
    xf, idxs = xf_series(L, regs, V, nfr, T)
    return S, T, tpath, P, speed, regs, total, V, nfr, xf, idxs


def print_regions(spec_path):
    for L in "ABC":
        S, T, tpath, P, speed, regs, total, V, nfr, xf, idxs = prepare(spec_path, L)
        if L == "A":
            print(f"{S['id']}: sidecar {tpath}\n  {len(P['items'])} pieces, {total:.2f} s out at {speed}x; screen {T['screen_file']}; bounds {T['bounds']}")
        print(f"  layout {L} (hole {LAYOUTS[L]['hole']}):")
        for r, v in zip(regs, V):
            hx, hy, hw, hh = LAYOUTS[L]["hole"]
            s, cx, cy, ax, ay = v
            crop = [round(cx - ax / s), round(cy - ay / s), round(hw / s), round(hh / s)]
            mk = "; ".join(f"{m.get('kind')} {m['box']} at {m['t0']:.2f}-{m['t1']:.2f} on '{m.get('word')}'" for m in r["marks"]) or "no mark"
            src = f" FREEZE src {r['src_at']}" if r.get("src_at") is not None else ""
            print(f"    {r['t0']:6.2f}-{r['t1']:6.2f} s  clock {r['at']} -> word '{r['word']}' {r['at_snapped']}  {r.get('label', '')}{src}\n"
                  f"       focus {r['focus']} scale {s:.2f} crop {crop}  marks: {mk}")
    if T.get("card"):
        print(f"  card: {T['card']}")
    if T.get("layout_pick"):
        lp = T["layout_pick"]
        print(f"  layout pick: {lp.get('layout')} (runner-up {lp.get('runner_up')}): {lp.get('why')}")


def build(spec_path, L, force=False):
    spec_path = PATHS.remap(str(spec_path))
    S, T, tpath, P, speed, regs, total, V, nfr, xf, idxs = prepare(spec_path, L)
    sid = S["id"]
    tag = f"{sid}-tut{L}"
    work = WORKROOT / tag
    work.mkdir(parents=True, exist_ok=True)
    outdir = OUT / S["slug"]
    outdir.mkdir(parents=True, exist_ok=True)
    final = outdir / f"{tag}.mp4"
    t0 = time.time()
    log(work, f"build {tag} from {spec_path} + {tpath.name}; {len(P['items'])} pieces, {nfr} frames at {speed}x")
    free_gb = PATHS.free_gb()
    if free_gb < 5:
        raise SystemExit(f"disk: {free_gb:.1f} GB free, under the 5 GB floor: hold the batch and wait")
    if final.exists() and not force:
        log(work, f"exists, skipping: {final}")
        return final
    (work / "plan.json").write_text(json.dumps({k: v for k, v in P.items() if k not in ("words", "track")}, indent=1, default=str))
    (work / "regions.json").write_text(json.dumps({"regs": regs, "views": V}, indent=1, default=str))
    # the face: Haar inside the webcam region, measured once per spec (pipeline.face_box caches it in the work dir)
    fgeo = faces_for(P, T, L, work)
    base = render_base(S, P, T, L, regs, xf, idxs, fgeo, work, speed, nfr)
    log(work, f"base: {base.name} {PL.duration(base):.2f} s")
    audio, am = PL.audio_take(S, P, work)
    log(work, f"audio: in {am['input_i']} LUFS, true peak {am['true_peak_dbtp']} dBTP, {am['secs']:.2f} s")
    groups = groups_for(P, S, L)
    ass_txt = ass_for(groups, speed, L)
    ass = work / f"captions-{L}-{key_of(ass_txt)}.ass"
    ass.write_text(ass_txt)
    log(work, f"captions: {len(groups)} groups -> {ass.name}")
    SPEED[0] = speed
    payload = payload_for(S, T, L, regs, xf, total)
    (work / f"payload-{L}.json").write_text(json.dumps({k: v for k, v in payload.items() if k != "xf"}, indent=1))
    os.environ["SHORTS_LOOKS_HTML"] = str(TUT_HTML)
    seq, uniq, setup = PL.render_overlay(payload, nfr, work, f"tut{L}")
    log(work, f"overlay: {uniq} unique frames of {nfr} -> {seq.name}; setup {setup}")
    fc = (f"[1:v]format=rgba[ov];[0:v][ov]overlay=0:0:shortest=1:format=auto[m];"
          f"[m]ass='{ass}':fontsdir='{FONTDIR}',format=yuv420p[v]")
    venc = ["-c:v", "h264_videotoolbox", "-allow_sw", "1", "-profile:v", "high", "-b:v", "10M", "-maxrate", "15M", "-bufsize", "20M", "-pix_fmt", "yuv420p",
            "-color_range", "tv", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709"]
    tmp = str(final) + ".part.mp4"
    PL.run([FF, "-y", "-v", "error", "-i", str(base), "-framerate", str(FPS), "-i", str(seq / "%05d.png"), "-i", str(audio),
            "-filter_complex", fc, "-map", "[v]", "-map", "2:a", "-frames:v", str(nfr), "-r", str(FPS)] + venc + PL.AAC +
           ["-movflags", "+faststart", "-t", f"{nfr / FPS:.3f}", tmp], timeout=min(3600, 300 + 10 * nfr / FPS), label="compose")
    os.replace(tmp, final)
    lu, tp = PL.lufs_of(final), PL.true_peak(final)
    if (lu is not None and abs(lu + 14.0) > 0.5) or tp > -1.4:
        lv = str(final) + ".lvl.mp4"
        PL.run([FF, "-y", "-v", "error", "-i", str(final), "-i", str(audio), "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                "-af", f"volume={-14.0 - (lu if lu is not None else -14.0):.2f}dB,aresample=192000,{PL.LIMITER},aresample=48000"] + PL.AAC +
               ["-movflags", "+faststart", "-t", f"{nfr / FPS:.3f}", lv], timeout=600, label="level")
        os.replace(lv, final)
        log(work, f"loudness {lu} LUFS / {tp} dBTP -> re-cut from the wav")
    log(work, f"compose: {final} {PL.duration(final):.2f} s")
    poster = outdir / f"{tag}-poster.jpg"
    PL.run([FF, "-y", "-v", "error", "-ss", "1.0", "-i", str(final), "-frames:v", "1", "-q:v", "2", str(poster)], timeout=120, label="poster")
    sheet_w = work / f"sheet-{L}.jpg"
    PL.contact_sheet(final, P, speed, sheet_w, every=1.0)
    shutil.copyfile(sheet_w, outdir / f"{tag}-sheet.jpg")
    checks = run_tut_checks(S, P, T, L, regs, xf, idxs, fgeo, final, work, speed, ass, groups, seq, setup, payload, nfr)
    checks["unique_overlay_frames"] = uniq
    checks["caption_groups"] = len(groups)
    checks["caption_text"] = " ".join(w[0] for g in groups for w in g["w"])
    checks["regions"] = [{"t0": r["t0"], "t1": round(r["t1"], 3), "word": r["word"], "label": r.get("label"), "src_at": r.get("src_at"),
                          "scale": round(v[0], 2)} for r, v in zip(regs, V)]
    checks["plan"] = [{"kind": it["kind"], "a": round(it["a"], 3), "b": round(it["b"], 3), "out": round(it["out"] / speed, 3)} for it in P["items"]]
    (outdir / f"{tag}-checks.json").write_text(json.dumps(checks, indent=1, default=str))
    row = {"id": tag, "spec": PATHS.canon(str(spec_path)), "status": "ok" if checks["ok"] else "checks-failed", "seconds": checks["seconds"],
           "checks": {k: v for k, v in checks.items() if k.endswith("_ok") or k in ("caption_Cap_px", "caption_Big_px", "true_peak_dbtp", "lufs")},
           "path": PATHS.canon(str(final)), "when": dt.datetime.now().strftime("%Y-%m-%d %H:%M"), "build_secs": round(time.time() - t0), "look": f"tutorial-{L}"}
    with open(RESULTS, "a") as f:
        f.write(json.dumps(row) + "\n")
    log(work, f"done {tag}: {row['status']} in {row['build_secs']} s; checks {row['checks']}")
    if checks["ok"]:
        # the pipeline's own prune (this layout's overlay frames, the audio takes, the face frames; never the face box,
        # the plan, the captions or the log), plus this layout's base video; Python removes, every path under WORKROOT
        PL.prune_work(work, f"tut{L}")
        for b in work.glob(f"base-{L}-*.mp4"):
            assert str(b.resolve()).startswith(str(WORKROOT.resolve()) + "/"), b
            os.remove(b)
    if not checks["ok"]:
        failed = [k for k in checks if k.endswith("_ok") and not checks[k]]
        raise SystemExit(f"checks failed for {tag}: {failed} (see {outdir / (tag + '-checks.json')})")
    return final


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build")
    ap.add_argument("--layout", choices=["A", "B", "C", "pick", "runner_up"], help="a layout, or the sidecar's layout_pick (pick / runner_up)")
    ap.add_argument("--regions")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--still", help="spec: one preview frame from a PNG on disk (no ffmpeg)")
    ap.add_argument("--png")
    ap.add_argument("--face-png")
    ap.add_argument("--t", type=float)
    ap.add_argument("--out")
    a = ap.parse_args()
    if a.still:
        print(json.dumps(preview_still(a.still, a.layout, a.png, a.t, a.out, a.face_png), default=str))
    elif a.regions:
        print_regions(a.regions)
    elif a.build:
        if not a.layout:
            raise SystemExit("--layout A|B|C|pick|runner_up")
        L = a.layout
        if L in ("pick", "runner_up"):
            S0 = PL.load_spec(a.build)
            T0, _ = load_side(PATHS.remap(a.build), S0)
            lp = T0.get("layout_pick") or {}
            L = lp.get("layout") if a.layout == "pick" else lp.get("runner_up")
            if not L:
                raise SystemExit(f"{S0['id']}: the sidecar names no {a.layout}")
        build(a.build, L, a.force)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
