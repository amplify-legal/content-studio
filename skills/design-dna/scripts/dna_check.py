#!/usr/bin/env python3
"""
dna_check.py - run a surface's design test battery against an HTML page.

    python3 .claude/skills/design-dna/scripts/dna_check.py <surface>/dna.json <page.html>
    python3 .claude/skills/design-dna/scripts/dna_check.py <surface-dir> <page.html> --json
    python3 .claude/skills/design-dna/scripts/dna_check.py --example > dna.json
    python3 .claude/skills/design-dna/scripts/dna_check.py --selftest

The point of the tests: a bad copy of the page should FAIL at least one. So the
first thing you do with a new battery is run it against the ORIGINAL, the page
you already know is right. Anything that fails there is a broken test, not a
broken page. Fix the test, then trust it on rebuilds. Then run it against a
deliberately slopped copy and record that number too, because a battery that
only ever passes is measuring nothing.

Two halves:

  SOURCE checks (standard library only, always run): type floor, type tiers,
  shadows, required signatures and CSS, bans (em dashes, dark mode, gradients,
  emoji), counted phrases, and the full-screen adaptive layout rule.

  PIXEL checks (only when the spec asks for them): colour share by family and
  connected-region counts, measured on a headless render. They need Pillow and
  Chrome or Chromium. Set CHROME=/path/to/chrome if it is not found. If either
  is missing, pixel checks are reported as SKIPPED, never as passed.

  Colour share answers "how much of this page is actually the accent colour",
  which no amount of source reading can answer. It cannot see gradients, whose
  pixels are not exact token hexes, which is why the gradient ban exists.

One rule when you add a check: ask what BETTER page it would fail. A check that
greps the source for a literal punishes indirection, and a page written as
calc(var(--base) * var(--f-hero)) is following "ratios, not pixels" more
faithfully than one with a hardcoded 46px. This file resolves custom properties
for exactly that reason.
"""

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter, deque

EM_DASH = chr(0x2014)  # the character itself never appears in this file
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F900-\U0001F9FF]")

EXAMPLE = {
    "surface": "report",
    "_note": ("Every value here is a placeholder to replace with what you MEASURED on the "
              "original page. Brand colours and fonts come from content/brand.md. "
              "reading_floor_px is the absolute backstop, reading_floor_ratio is the real "
              "constraint: a bare pixel floor breaks on any page with a different base size "
              "(15.5px on a 17px base is 0.91x, proportionally larger than a 16px caption on "
              "a 16px base). Set both, per surface. Delete the pixel block if you have no "
              "Chrome; it is reported as skipped, not passed."),
    "type": {
        "base_px": 18,
        "label_family": "{BRAND_FONT_LABEL}",
        "reading_floor_px": 16,
        "reading_floor_ratio": 0.8,
        "tiers": {"hero": {"ratio": 2.7, "count": 1, "tolerance_px": 1.5}},
    },
    "limits": {"box_shadow_max": 1},
    "require": {
        "_note": "the signature move of the original, as text and as CSS, once measured",
        "strings": [],
        "css": [],
    },
    "ban": {
        "em_dash": True,
        "dark_mode": True,
        "gradients": True,
        "emoji": True,
        "strings": [],
        "regex": [],
    },
    "layout": {
        "full_screen": True,
        "_note": ("no fixed max-width column on the page container, a fluid side gutter "
                  "(clamp), and grids that reflow with auto-fit or auto-fill"),
    },
    "counts": [
        {"id": "cta", "regex": "(?i)book a call|schedule a call", "want": 1}
    ],
    "pixels": {
        "width": 1440,
        "height": 4200,
        "ground": ["#FFFFFF"],
        "families": {"accent": ["#000000"]},
        "registers": {
            "any": {"ground_min": 60, "accent_min": 5, "accent_max": 25}
        },
        "regions": [],
    },
}


# ------------------------------------------------------------------ source half
def strip_attr_selectors(src):
    """A responsive override written as div[style*="font-size: 64px"] carries the
    literal text of a size and is not an element. Strip those before counting."""
    return re.sub(r'\[style\*=\s*"[^"]*"\]', "", src)


def custom_props(src):
    props = {}
    for name, val in re.findall(r"--([\w-]+)\s*:\s*([^;}]+)", src):
        props.setdefault(name, val.strip())
    return props


def _px(value):
    m = re.match(r"([\d.]+)(px)?$", value.strip())
    return float(m.group(1)) if m else None


def sizes_in(block, props):
    """Every font-size in a block, resolved: literal px, var(--x), and
    calc(var(--a) * var(--b)). Capture runs to the end of the declaration
    because calc(var(--a) * var(--b)) has nested parens."""
    out = [float(x) for x in re.findall(r"font-size:\s*([\d.]+)px", block)]
    for m in re.finditer(r"font-size:\s*((?:calc|var)\([^;}]*)", block):
        expr = m.group(1).strip()
        refs = re.findall(r"var\(--([\w-]+)\)", expr)
        vals = [_px(props.get(r, "")) for r in refs]
        if not refs or any(v is None for v in vals):
            continue
        if expr.startswith("var("):
            out.append(vals[0])
        elif "*" in expr and len(vals) == 2:
            out.append(vals[0] * vals[1])
    return out


def label_sizes(src, props, family):
    """Sizes carried by the uppercase label family, which is not reading text.

    Three ways a page can declare it, all seen live:
      inline style, a class whose block names the family, and a class whose
      block sets font-family: var(--label) with the family named in :root.
    """
    if not family:
        return set()
    found = set()
    for blk in re.findall(r'style="[^"]*' + re.escape(family) + r'[^"]*"', src):
        found.update(sizes_in(blk, props))
    fam_vars = {n for n, v in re.findall(r"--([\w-]+)\s*:\s*([^;}]+)", src) if family in v}
    rules = re.findall(r"([^{}]+)\{([^}]*)\}", src)
    classes = set()
    for sel, block in rules:
        is_label = family in block or any(
            re.search(r"font-family:\s*var\(--" + re.escape(v) + r"\)", block) for v in fam_vars
        )
        if is_label and ":root" not in sel:
            classes.update(re.findall(r"\.([\w-]+)", sel))
    if not classes:
        return found
    # class="label eyebrow" makes .eyebrow's size a label size too, even though
    # .eyebrow's own selector never names the family.
    for attr in re.findall(r'class="([^"]*)"', src):
        parts = set(attr.split())
        if parts & classes:
            classes |= parts
    for sel, block in rules:
        if set(re.findall(r"\.([\w-]+)", sel)) & classes:
            found.update(sizes_in(block, props))
    return found


CONTAINER_SEL = re.compile(
    r"(^|[\s,>])(html|body|main|\.(page|wrap|wrapper|container|content|shell|main))\b", re.I)


def layout_findings(src):
    """The full-screen adaptive rule: a page spans the viewport with a fluid
    gutter, and grids reflow. Returns a list of plain findings."""
    out = []
    for sel, block in re.findall(r"([^{}@]+)\{([^}]*)\}", src):
        sel = sel.strip()
        if not CONTAINER_SEL.search(sel):
            continue
        m = re.search(r"max-width:\s*([\d.]+)(px|rem|em)", block)
        if m:
            out.append("fixed max-width %s%s on %s" % (m.group(1), m.group(2), sel[:40]))
    for m in re.finditer(r"grid-template-columns:\s*([^;}]+)", src):
        val = m.group(1)
        if re.search(r"repeat\(\s*\d+\s*,", val) and not re.search(r"auto-(fit|fill)", val):
            out.append("fixed column count: grid-template-columns: %s" % val.strip()[:40])
    if not re.search(r"padding(-inline)?:[^;}]*clamp\(", src):
        out.append("no fluid side gutter (padding-inline with clamp(), e.g. clamp(16px,4vw,64px))")
    return out


# ------------------------------------------------------------------- pixel half
def find_chrome():
    env = os.environ.get("CHROME")
    if env and os.path.exists(env):
        return env
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome"):
        p = shutil.which(name)
        if p:
            return p
    for p in ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
              "/Applications/Chromium.app/Contents/MacOS/Chromium"):
        if os.path.exists(p):
            return p
    return None


def render(html_path, width, height):
    """Headless-render the page to a PNG and return the path, or None.

    Two traps live here: headless Chrome needs an ABSOLUTE file:// path (a
    relative one renders Chrome's own error page, which then looks like a
    successful render), and the render width must match the composition width
    (a 1920px frame rendered at 940 comes back clipped and reads as a design
    fault)."""
    chrome = find_chrome()
    if not chrome:
        return None
    absp = os.path.abspath(html_path)
    key = hashlib.md5((absp + str(os.path.getmtime(absp)) + "%dx%d" % (width, height))
                      .encode()).hexdigest()[:10]
    out = os.path.join(tempfile.gettempdir(), "dna_render_%s.png" % key)
    if not os.path.exists(out):
        subprocess.run([chrome, "--headless", "--disable-gpu", "--screenshot=%s" % out,
                        "--window-size=%d,%d" % (width, height), "--hide-scrollbars",
                        "file://" + absp], capture_output=True, timeout=120)
    return out if os.path.exists(out) else None


def hx(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def trimmed(png):
    """Crop the uniform tail off the render; return (Counter, total, image)."""
    from PIL import Image
    im = Image.open(png).convert("RGB")
    w, h = im.size
    px = im.load()
    bg = px[5, h - 1]
    last = h - 1
    while last > 0 and all(px[x, last] == bg for x in range(0, w, 7)):
        last -= 1
    im = im.crop((0, 0, w, last + 1))
    data = im.get_flattened_data() if hasattr(im, "get_flattened_data") else im.getdata()
    return Counter(data), im.size[0] * im.size[1], im


def components(im, target, tol=10, min_px=40):
    """Count connected regions matching a colour (4-way BFS on a coarse grid)."""
    w, h = im.size
    px = im.load()
    step = 2

    def match(x, y):
        r, g, b = px[x, y]
        return abs(r - target[0]) <= tol and abs(g - target[1]) <= tol and abs(b - target[2]) <= tol

    seen = set()
    regions = 0
    for y in range(0, h, step):
        for x in range(0, w, step):
            if (x, y) in seen or not match(x, y):
                continue
            q = deque([(x, y)])
            seen.add((x, y))
            size = 0
            while q:
                cx, cy = q.popleft()
                size += 1
                for dx, dy in ((step, 0), (-step, 0), (0, step), (0, -step)):
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in seen and match(nx, ny):
                        seen.add((nx, ny))
                        q.append((nx, ny))
            if size * step * step >= min_px:
                regions += 1
    return regions


def pixel_checks(spec_px, html_path, src, check):
    try:
        import PIL  # noqa: F401
    except ImportError:
        check("pixels", None, "SKIPPED: Pillow not installed (pip install pillow)")
        return
    png = render(html_path, int(spec_px.get("width", 1440)), int(spec_px.get("height", 4200)))
    if not png:
        check("pixels", None, "SKIPPED: no Chrome or Chromium found (set CHROME=/path)")
        return
    cnt, total, im = trimmed(png)

    def share(hexes):
        return 100.0 * sum(cnt.get(hx(c), 0) for c in hexes) / total

    # The page declares its register in <meta name="dna-register" content="...">;
    # each register carries its own measured band. A page with no declaration
    # gets the "any" band and is told so, because passing "any" proves little.
    regs = spec_px.get("registers") or {}
    m = re.search(r'<meta\s+name="dna-register"\s+content="([\w-]+)"', src, re.I)
    reg = m.group(1).lower() if m else "any"
    band = regs.get(reg) or regs.get("any") or {}
    tag = "[%s]" % reg if m else "[no register declared, widest band]"
    if "ground_min" in band:
        g = share(spec_px.get("ground", []))
        check("ground", g >= band["ground_min"],
              "ground %.1f%% (want >=%s%%) %s" % (g, band["ground_min"], tag))
    for fam, hexes in (spec_px.get("families") or {}).items():
        lo, hi = band.get(fam + "_min"), band.get(fam + "_max")
        if lo is None and hi is None:
            continue
        s = share(hexes)
        ok = (lo is None or s >= lo) and (hi is None or s <= hi)
        check("share-" + fam, ok, "%s family %.1f%% (want %s-%s%%) %s"
              % (fam, s, lo if lo is not None else 0, hi if hi is not None else 100, tag))
    for r in spec_px.get("regions") or []:
        n = components(im, hx(r["hex"]), tol=r.get("tol", 10))
        s = share([r["hex"]])
        ok = n == r["want"] and (r.get("max_share") is None or s < r["max_share"])
        check("regions-" + r["id"], ok, "%s in %s region(s) at %.2f%% (want %s regions%s)"
              % (r["hex"], n, s, r["want"],
                 ", <%s%%" % r["max_share"] if r.get("max_share") is not None else ""))


# ------------------------------------------------------------------------ run
def run(spec, src, html_path=None):
    el = strip_attr_selectors(src)
    props = custom_props(el)
    sizes = sizes_in(el, props)
    t = spec.get("type", {})
    base = float(t.get("base_px", 16))
    labels = label_sizes(el, props, t.get("label_family"))
    reading = [s for s in sizes if s not in labels]

    results = []

    def check(cid, ok, detail):
        results.append({"id": cid, "pass": ok if ok is None else bool(ok), "detail": detail})

    floor = t.get("reading_floor_px", 16)
    ratio_floor = t.get("reading_floor_ratio", 0)
    small = sorted({s for s in reading if s < floor or (ratio_floor and s / base < ratio_floor)})
    check("type-floor", not small,
          "reading text under %spx or %sx base: %s" % (floor, ratio_floor, small or "none"))

    for name, tier in (t.get("tiers") or {}).items():
        want = int(tier.get("count", 1))
        px = base * float(tier["ratio"])
        tol = float(tier.get("tolerance_px", 1.5))
        n = sum(1 for s in sizes if abs(s - px) < tol)
        check("tier-" + name, n == want,
              "%s element(s) at %s tier ~%.0fpx (want %s)" % (n, name, px, want))

    limits = spec.get("limits") or {}
    if "box_shadow_max" in limits:
        n = len(re.findall(r"box-shadow:\s*(?!none)", src))
        check("shadows", n <= limits["box_shadow_max"],
              "%s box-shadow(s) (max %s)" % (n, limits["box_shadow_max"]))

    req = spec.get("require") or {}
    if req.get("strings"):
        missing = [s for s in req["strings"] if s.lower() not in src.lower()]
        check("signatures", not missing, "missing signature(s): %s" % (missing or "none"))
    if req.get("css"):
        missing_css = [c for c in req["css"]
                       if not re.search(re.escape(c).replace(r"\ ", r"\s*"), src)]
        check("required-css", not missing_css, "missing css: %s" % (missing_css or "none"))

    ban = spec.get("ban") or {}
    markers = []
    if ban.get("em_dash", True) and EM_DASH in src:
        n = src.count(EM_DASH)
        standalone = len(re.findall(r">\s*" + EM_DASH + r"\s*<", src))
        markers.append("%s em dash(es), %s of them standalone placeholders" % (n, standalone))
    if ban.get("dark_mode", True) and "prefers-color-scheme" in src:
        markers.append("dark-mode block")
    if ban.get("gradients", True) and re.search(r"linear-gradient|radial-gradient", src):
        markers.append("gradient")
    if ban.get("emoji", True) and EMOJI.search(src):
        markers.append("emoji")
    for s in ban.get("strings", []):
        if s.lower() in src.lower():
            markers.append('banned string "%s"' % s)
    for r in ban.get("regex", []):
        if re.search(r, src):
            markers.append("banned pattern /%s/" % r)
    check("bans", not markers, "slop markers: %s" % (markers or "none"))

    if (spec.get("layout") or {}).get("full_screen"):
        found = layout_findings(el)
        check("full-screen", not found, "layout: %s" % ("; ".join(found) if found else
                                                          "spans the viewport, fluid gutter, reflowing grids"))

    for c in spec.get("counts", []):
        n = len(re.findall(c["regex"], src))
        check("count-" + c["id"], n == c["want"],
              "%s match(es) for %s (want %s)" % (n, c["id"], c["want"]))

    if spec.get("pixels") and html_path:
        pixel_checks(spec["pixels"], html_path, src, check)

    return results


# -------------------------------------------------------------------- selftest
GOOD = """<!doctype html><html><head><style>
:root{--base:18px;--f-hero:2.7;--label:'Label Sans'}
body{margin:0;padding-inline:clamp(16px,4vw,64px);font-size:var(--base)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr))}
.hero{font-size:calc(var(--base) * var(--f-hero))}
.l{font-family:var(--label);font-size:12px;text-transform:uppercase}
.card{box-shadow:0 1px 3px #0002}
</style></head><body><div class="l eyebrow">Step 1</div><h1 class="hero">42</h1>
<div class="grid"><p>Body copy.</p></div><a>Book a call</a></body></html>"""

BAD = """<!doctype html><html><head><style>
body{max-width:880px;margin:0 auto;font-size:14px}
.grid{display:grid;grid-template-columns:repeat(3,1fr)}
.a{box-shadow:0 1px 3px #0002}.b{box-shadow:0 2px 6px #0003}
.c{background:linear-gradient(#fff,#eee)}
@media (prefers-color-scheme: dark){body{background:#000}}
</style></head><body><h1 style="font-size:40px">Hi EMDASH there</h1>
<div class="grid"><p>Body.</p></div><a>Book a call</a> <a>Schedule a call</a></body></html>""".replace("EMDASH", EM_DASH)


def selftest():
    spec = {
        "type": {"base_px": 18, "label_family": "Label Sans", "reading_floor_px": 16,
                 "reading_floor_ratio": 0.8, "tiers": {"hero": {"ratio": 2.7, "count": 1}}},
        "limits": {"box_shadow_max": 1},
        "ban": {"em_dash": True, "dark_mode": True, "gradients": True, "emoji": True},
        "layout": {"full_screen": True},
        "counts": [{"id": "cta", "regex": "(?i)book a call|schedule a call", "want": 1}],
    }
    good = run(spec, GOOD)
    bad = run(spec, BAD)
    fails = []
    if not all(r["pass"] for r in good):
        fails.append("good page failed: %s" % [r for r in good if not r["pass"]])
    n_bad = sum(1 for r in bad if r["pass"] is False)
    if n_bad < 5:
        fails.append("slopped page failed only %s check(s); battery is not discriminating" % n_bad)
    if fails:
        print("selftest FAILED")
        for f in fails:
            print("  - " + f)
        return 1
    print("selftest passed: good page %s/%s, slopped page failed %s/%s"
          % (len(good), len(good), n_bad, len(bad)))
    return 0


def main():
    if "--example" in sys.argv:
        print(json.dumps(EXAMPLE, indent=2))
        return 0
    if "--selftest" in sys.argv or "--self-test" in sys.argv:
        return selftest()
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) < 2:
        print(__doc__)
        return 2
    spec_path, html_path = args[0], args[1]
    if os.path.isdir(spec_path):
        spec_path = os.path.join(spec_path, "dna.json")
    if not os.path.isfile(spec_path):
        print("Cannot find the DNA file: %s" % spec_path)
        print("A surface has no DNA until you measure one. Start from the example:")
        print("    python3 dna_check.py --example > dna.json")
        print("then edit it, and run this again pointing at that file.")
        return 2
    try:
        with open(spec_path) as f:
            spec = json.load(f)
    except json.JSONDecodeError as err:
        print("%s is not valid JSON (%s)." % (spec_path, err))
        return 2
    if not os.path.isfile(html_path):
        print("Cannot find the page: %s" % html_path)
        print("Point the second argument at the .html file you want checked.")
        return 2
    with open(html_path) as f:
        src = f.read()
    results = run(spec, src, html_path)
    scored = [r for r in results if r["pass"] is not None]
    passed = sum(1 for r in scored if r["pass"])
    skipped = len(results) - len(scored)
    if "--json" in sys.argv:
        print(json.dumps({"surface": spec.get("surface"), "tests": results,
                          "passed": passed, "total": len(scored), "skipped": skipped}, indent=2))
    else:
        print("\n  %s  (%s)\n" % (html_path, spec.get("surface", "unnamed surface")))
        for r in results:
            mark = "SKIP" if r["pass"] is None else ("PASS" if r["pass"] else "FAIL")
            print("  [%s] %-16s %s" % (mark, r["id"], r["detail"]))
        print("\n  %s/%s passed%s\n" % (passed, len(scored),
                                       ", %s skipped (not passed)" % skipped if skipped else ""))
    return 0 if passed == len(scored) else 1


if __name__ == "__main__":
    sys.exit(main())
