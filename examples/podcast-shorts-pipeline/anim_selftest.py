#!/usr/bin/env python3
"""Self-test for anim_looks.html (the animation directions page), run before the pipeline renders through it
(SHORTS_LOOKS_HTML=<this folder>/anim_looks.html). Run: PYTHONDONTWRITEBYTECODE=1 python3 anim_selftest.py [frames_dir]

1. anim unset: window.setup returns the same keys AND values as looks.html for the same payload (the pipeline's checks
   read them), the same state signatures and pixel-identical layers at 6 output times, on every drawn look and ig_native.
2. anim A, B, C x anim_title stays/goes x anim_dark false/true: setup returns looks.html's key set and the page throws
   nothing.
3. card_windows: the state signature changes on every frame of every panel transition (in 0.3 s, out 0.3 s), so no
   transition frame is hardlinked away. (The page's IN was 0.4 s when this test was first written; it became 0.3 s, the
   footage's own crossfade, the same night: anim_looks.html SP.IN.)
4. The pipeline's own ink tests (pipeline.py run_checks, safe_ink_layer and the frame-0 band edge) on the anim layer:
   under 400 ink px above y 230 (x >= 140) and in the rail (x >= 940, y 960 to 1500) on every sampled frame, under 40
   on frame 0's band edge. (230 is the safe frame's own top line, the one pipeline.py counts since 27 Oct; the old 290
   was the eyebrow's line, and the title has sat from y 260 since 28 Oct, so a 290 line counts the title as ink.)

Both pages are opened through paths.page_for_this_mac, so the tokens (fonts, springs.js, logo, mascot, accent) are filled
exactly as the pipeline fills them. Needs Playwright with Chrome or Chromium, numpy and Pillow, and the fonts the pages
load in the font folder (paths.FONTDIR); a missing one is named and the test exits 2. Renders no video; its frames go to
a fresh folder in the system temp folder (or under argv[1]). Exit 0 on pass, 1 on any failure, 2 when it cannot run.
"""
import copy
import os
import re
import sys
import tempfile
import urllib.parse
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths as PATHS  # noqa: E402

BUILD = PATHS.BUILD
LOOKS, ANIM = BUILD / "looks.html", BUILD / "anim_looks.html"
PAGES = PATHS.WORKROOT / "pages"   # where the filled copies go (the same folder pipeline.open_page uses)
FPS = 30
IN_S, OUT_S = 0.3, 0.3   # the panel's spring in and out (anim_looks.html SP.IN and SP.OUT)
TOP_LINE = 230          # pipeline.py run_checks: safe_ink_layer counts ink above this line
# a payload of the shape pipeline.overlay_payload writes for a data-table short, plus the answer_full layout and the card
# windows card_only_moving gives it (plan.json pieces). The words are invented (a 3-step kitchen-order flow); the times,
# the key order and the layout sizes are measured ones, so the test exercises: 3 keyed items, the title's accent naming
# the first one (the ring), 3 card windows, and `anim_doc` set so direction B draws its document (the page's other
# trigger for the document is 2 or more items naming red, yellow or green).
BASE = {
    "look": "whiteboard", "title": "Every order runs on 3 steps", "title_accent": "every order",
    "eyebrow": "Riley Morgan · on the podcast", "credit": "Riley Morgan", "format": "data-table", "story_proof": False,
    "pov_line": None, "held_top": None, "band_text": None, "hook_end": 2.666666666666667, "duration": 63.1,
    "graphic": {"kind": "table", "items": ["Order|taken at the counter", "Prep|starts on the ticket", "Serve|within 8 minutes"],
                "keys": [["Order|taken at the counter", 3.492], ["Prep|starts on the ticket", 8.472], ["Serve|within 8 minutes", 49.36]],
                "source_line": "so every order goes through the same three steps, start to finish", "clawd": False},
    "anim_doc": "Order ticket",
    "source_name": "Riley Morgan", "screen_rect": None, "window_title": "Screen",
    "layout": {"hook": {"top_band_h": 516, "host": [516, 440], "guest": [956, 544]},
               "answer": {"top_band_h": 880, "guest": [880, 620]}, "answer_full": {"top_band_h": 640, "guest": [640, 860]}},
}
WINS = [[2.667, 15.567], [49.2, 50.9], [59.067, 63.1]]
TS = [0.0, 1.2, 3.0, 8.65, 30.0, 61.5]
FG = {"ledger": "1C1C1E", "none": "1C1C1E", "whiteboard": "1C1C1E", "flat2d": "1C1C1E", "operator": "F2F3F4"}
# the accent the ink check counts: the light accent on the dark operator look, the dark partner everywhere else
ACC = {"operator": PATHS.ACCENT.lstrip("#")}
ACC_DEFAULT = PATHS.ACCENT_DARK.lstrip("#")
fails = []


def check(ok, msg):
    print(("PASS  " if ok else "FAIL  ") + msg, flush=True)
    if not ok:
        fails.append(msg)


def filled(path):
    """the page with its tokens filled (a copy in the work folder), or exit 2 naming the files it loads that are missing"""
    url_path = PATHS.page_for_this_mac(path, PAGES)
    text = Path(url_path).read_text()
    missing = sorted({urllib.parse.unquote(u) for u in re.findall(r"file://([^\"'()\s<>]+)", text)
                      if not os.path.exists(urllib.parse.unquote(u))})
    system = [m for m in missing if m.startswith("/System/")]   # Menlo on a machine that is not a Mac: monospace stands in
    need = [m for m in missing if m not in system]
    if need:
        print(f"cannot run: {Path(path).name} loads files that are missing here: {need} "
              f"(put the fonts in {PATHS.FONTDIR} or set SHORTS_FONT_DIR)")
        sys.exit(2)
    if system:
        print(f"note: {system} not on this machine; both pages fall back to monospace alike")
    return url_path


def open_page(br, path, errors):
    """a fresh page in the one browser (launching Chrome once per case hung the first run after about 12 launches)"""
    pg = br.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
    pg.set_default_timeout(30000)
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    pg.goto(f"file://{URLS[Path(path).name]}")
    pg.wait_for_load_state("networkidle")
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(200)
    return pg, pg


def shot(pg, path):
    from PIL import Image
    pg.screenshot(path=str(path), omit_background=True)
    return Image.open(path).convert("RGBA")


def ink_counts(img, look, band_h=None):
    import numpy as np
    a = np.asarray(img)
    near = lambda hx: np.abs(a[:, :, :3].astype(int) - np.array([int(hx[i:i + 2], 16) for i in (0, 2, 4)])).sum(axis=2) < 60  # noqa: E731
    ink = (a[:, :, 3] > 200) & (near(FG[look]) | near(ACC.get(look, ACC_DEFAULT)))
    top = int(ink[:TOP_LINE, :].sum()) - int(ink[:TOP_LINE, :140].sum())
    rail = int(ink[960:1500, 940:].sum())
    edge = None
    if band_h:
        edge = int(ink[band_h - 3:band_h, 40:1040].sum() + ink[290:band_h, 0:6].sum() + ink[290:band_h, 1074:1080].sum())
    return top, rail, edge


URLS = {}


def main():
    try:
        import numpy  # noqa: F401
        from PIL import ImageChops
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        print(f"cannot run: {e.name} is not installed (pip install playwright numpy pillow, then playwright install chromium)")
        return 2
    for p in (LOOKS, ANIM):
        URLS[p.name] = filled(p)
    # the frames go to a fresh folder in the system temp folder, or under the folder given as the first argument
    if len(sys.argv) > 1:
        Path(sys.argv[1]).mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="anim-selftest-", dir=sys.argv[1] if len(sys.argv) > 1 else None))
    with sync_playwright() as pw:
        try:
            BR = pw.chromium.launch(channel="chrome")
        except Exception:  # noqa: BLE001
            try:
                BR = pw.chromium.launch()
            except Exception as e:  # noqa: BLE001
                print(f"cannot run: no Chrome or Chromium for Playwright ({str(e).splitlines()[0]}); run: playwright install chromium")
                return 2
        # 1. anim unset: the page is looks.html
        for look in ["whiteboard", "ledger", "flat2d", "operator", "none", "ig_native"]:
            P = copy.deepcopy(BASE)
            P["look"] = look
            P.pop("card_windows", None)
            if look == "ig_native":
                P["ig"] = {"emoji": "", "callout": ["Every order, 3 steps", 0.0], "items": ["Order: taken at the counter", "Prep: starts on the ticket", "Serve: within 8 minutes"]}
                P["captions"] = [{"s": 3.0, "e": 4.2, "w": [["every", 3.0], ["order", 3.4], ["goes", 3.8]]}]
            errs = []
            b1, p1 = open_page(BR, LOOKS, errs)
            b2, p2 = open_page(BR, ANIM, errs)
            s1 = p1.evaluate("(p) => window.setup(p)", P)
            s2 = p2.evaluate("(p) => window.setup(p)", P)
            check(sorted(s1) == sorted(s2), f"[{look}] anim unset: setup keys match looks.html ({sorted(s2)})")
            check(s1 == s2, f"[{look}] anim unset: setup values match looks.html")
            same_sig, same_px = True, True
            for t in TS:
                g1 = p1.evaluate("(t) => window.setTime(t)", t)
                g2 = p2.evaluate("(t) => window.setTime(t)", t)
                same_sig &= g1 == g2
                i1, i2 = shot(p1, tmp / f"l-{look}-{t}.png"), shot(p2, tmp / f"a-{look}-{t}.png")
                same_px &= ImageChops.difference(i1, i2).getbbox() is None
            check(same_sig, f"[{look}] anim unset: state signatures match looks.html at {TS}")
            check(same_px, f"[{look}] anim unset: layers pixel-identical to looks.html at {TS}")
            check(not errs, f"[{look}] anim unset: no page errors {errs[:2]}")
            b1.close(); b2.close()  # noqa: E702
        # 2. every direction and variant: the same setup keys, no errors
        errs = []
        b0, p0 = open_page(BR, LOOKS, errs)
        ref_keys = sorted(p0.evaluate("(p) => window.setup(p)", BASE))
        b0.close()
        for look in ["whiteboard", "ledger", "operator"]:
            for anim in "ABC":
                for title in ["stays", "goes"]:
                    for dark in [False, True]:
                        P = copy.deepcopy(BASE)
                        P.update(look=look, anim=anim, anim_title=title, anim_dark=dark, card_windows=WINS)
                        errs = []
                        br, pg = open_page(BR, ANIM, errs)
                        st = pg.evaluate("(p) => window.setup(p)", P)
                        for t in TS:
                            pg.evaluate("(t) => window.setTime(t)", t)
                        check(sorted(st) == ref_keys and not errs, f"[{look} {anim} title {title} dark {dark}] setup keys match, no errors {errs[:2]}")
                        br.close()
        # 3 and 4. transitions change the signature on every frame; the pipeline's ink tests pass
        for anim, dark, title in [("A", True, "stays"), ("B", False, "stays"), ("B", True, "goes"), ("C", False, "stays"), ("C", True, "goes")]:
            for look in ["whiteboard", "operator"]:
                P = copy.deepcopy(BASE)
                P.update(look=look, anim=anim, anim_title=title, anim_dark=dark, card_windows=WINS)
                errs = []
                br, pg = open_page(BR, ANIM, errs)
                pg.evaluate("(p) => window.setup(p)", P)
                tag = f"[{look} {anim} dark {dark} title {title}]"
                changed = True
                for a, b in WINS:
                    spans = [(a, a + IN_S)] + ([(b - OUT_S, b)] if b < P["duration"] - 0.05 else [])
                    for s, e in spans:
                        f0, f1 = int(round(s * FPS)), int(round(e * FPS))
                        prev = None
                        for f in range(f0, f1 + 1):
                            sig = pg.evaluate("(t) => window.setTime(t)", f / FPS)
                            if prev is not None and sig == prev:
                                changed = False
                            prev = sig
                check(changed, f"{tag} the signature changes on every panel transition frame")
                frames = [0.0, 2.5, 2.7, 3.0, 3.6, 8.6, 9.2, 15.4, 15.7, 30.0, 49.3, 49.5, 50.8, 59.2, 61.5]
                worst_top = worst_rail = 0
                for t in frames:
                    pg.evaluate("(t) => window.setTime(t)", t)
                    img = shot(pg, tmp / f"ink-{anim}-{look}-{dark}-{t}.png")
                    top, rail, edge = ink_counts(img, look, 516 if t == 0.0 else None)
                    worst_top, worst_rail = max(worst_top, top), max(worst_rail, rail)
                    if t == 0.0:
                        check(edge < 40, f"{tag} frame 0 band edge ink {edge} px (< 40)")
                check(worst_top < 400 and worst_rail < 400, f"{tag} layer ink above y {TOP_LINE} at most {worst_top} px, in the rail at most {worst_rail} px (< 400)")
                check(not errs, f"{tag} no page errors {errs[:2]}")
                br.close()
        BR.close()
    print(f"\n{'ALL PASS' if not fails else str(len(fails)) + ' FAILED'} (scratch: {tmp})")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
