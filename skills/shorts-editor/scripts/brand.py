#!/usr/bin/env python3
"""Brand tokens for the shorts pipeline: colours and fonts, read from YOUR brand file.

Every visual choice that belongs to a brand (the accent colour, the display and body
fonts, the caption font file) is read here, never hard-coded in a renderer. Change the
brand once and every short re-themes.

Where the values come from, later wins:
  1. the neutral defaults below (a placeholder blue, Montserrat for captions)
  2. content/brand.md in your project (found by walking up from the current folder),
     or the file named by BRAND_FILE
  3. environment variables of the same name (BRAND_ACCENT=#4F9DFF, and so on)
  4. command-line flags on the script that calls this (for example --accent)

What it reads out of content/brand.md: any line that carries one of the key names below
and then a value, in any of these shapes, so a table row, a list item or a plain line
all work:

    BRAND_ACCENT: #4F9DFF
    - BRAND_ACCENT = #4F9DFF
    | BRAND_ACCENT | #4F9DFF |
    | `{BRAND_ACCENT}` | `#4F9DFF` |

A colour key needs a #RRGGBB value on the same line; a line still holding the unfilled
placeholder (`{BRAND_ACCENT}` with no hex after it) is ignored and the default stands.

Keys:
  BRAND_ACCENT          the one accent colour per video (highlighted caption word, card accent)
  BRAND_ACCENT_DARK     a darker partner for fills and secondary elements
  BRAND_RED             "no / lost / expensive"           (default #ff5470)
  BRAND_NEUTRAL         a neutral competitor or muted item (default #7f93ad)
  BRAND_FONT_DISPLAY    display font family name for cards (CSS font-family)
  BRAND_FONT_BODY       body font family name for cards
  BRAND_CAPTION_FONT    path to the .ttf the caption renderers bake with
                        (also read from CAPTION_FONT, the older name)

Run it to see what it resolved and from where:
    python3 brand.py
    python3 brand.py --self-test
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_DIR = HERE.parent

DEFAULTS = {
    "BRAND_ACCENT": "#4F9DFF",        # neutral placeholder blue: replace it in content/brand.md
    "BRAND_ACCENT_DARK": "#1F4F8F",
    "BRAND_RED": "#ff5470",
    "BRAND_NEUTRAL": "#7f93ad",
    "BRAND_FONT_DISPLAY": "Montserrat",
    "BRAND_FONT_BODY": "Inter",
    "BRAND_CAPTION_FONT": "",
}
COLOUR_KEYS = {"BRAND_ACCENT", "BRAND_ACCENT_DARK", "BRAND_RED", "BRAND_NEUTRAL"}
HEX = re.compile(r"#[0-9a-fA-F]{6}\b")

# Caption font fallbacks, in order, after any explicit setting.
CAPTION_FONT_CANDIDATES = [
    SKILL_DIR / "assets" / "fonts" / "caption.ttf",
    SKILL_DIR / "assets" / "fonts" / "Montserrat-VariableFont_wght.ttf",
    Path.home() / "Library" / "Fonts" / "Montserrat-VariableFont_wght.ttf",
    Path.home() / ".fonts" / "Montserrat-VariableFont_wght.ttf",
    Path("/usr/share/fonts/truetype/montserrat/Montserrat-VariableFont_wght.ttf"),
]


def find_brand_file() -> Path | None:
    env = os.environ.get("BRAND_FILE")
    if env:
        p = Path(env).expanduser()
        return p if p.is_file() else None
    start = Path.cwd().resolve()
    for d in [start, *start.parents]:
        cand = d / "content" / "brand.md"
        if cand.is_file():
            return cand
        if (d / ".git").exists() or (d / ".claude").is_dir():
            break
    return None


def parse_brand_text(text: str) -> dict:
    out: dict = {}
    for raw in text.splitlines():
        line = raw.strip()
        for key in DEFAULTS:
            m_key = re.search(r"\b" + key + r"\b", line)
            if not m_key:
                continue
            # the value is whatever follows the key name on the line
            rest = line[m_key.end():]
            if key in COLOUR_KEYS:
                m = HEX.search(rest)
                if m:
                    out[key] = m.group(0)
                continue
            # text value: strip table pipes, backticks, braces, separators
            val = re.sub(r"^[\s}`'\"|:=\-]+", "", rest)
            val = val.split("|")[0].strip().strip("`'\"").strip()
            if val and "{" not in val and not val.startswith("<"):
                out[key] = val
    return out


def load_brand(overrides: dict | None = None) -> dict:
    """Resolve every key. Returns the values plus a '_source' map saying where each came from."""
    vals = dict(DEFAULTS)
    src = {k: "default" for k in DEFAULTS}
    bf = find_brand_file()
    if bf:
        for k, v in parse_brand_text(bf.read_text(encoding="utf-8", errors="replace")).items():
            vals[k], src[k] = v, str(bf)
    for k in DEFAULTS:
        v = os.environ.get(k)
        if v:
            vals[k], src[k] = v, f"env {k}"
    if os.environ.get("CAPTION_FONT"):
        vals["BRAND_CAPTION_FONT"], src["BRAND_CAPTION_FONT"] = os.environ["CAPTION_FONT"], "env CAPTION_FONT"
    for k, v in (overrides or {}).items():
        if v:
            vals[k], src[k] = v, "command line"
    vals["_source"] = src
    return vals


def find_caption_font(brand: dict | None = None) -> str:
    """The caption .ttf, or exit with a sentence that says how to supply one."""
    brand = brand or load_brand()
    explicit = brand.get("BRAND_CAPTION_FONT")
    cands = []
    if explicit:
        p = Path(explicit).expanduser()
        if not p.is_absolute():
            bf = find_brand_file()
            if bf:
                cands.append(bf.parent / p)
            cands.append(SKILL_DIR / p)
        cands.append(p)
    cands += CAPTION_FONT_CANDIDATES
    for c in cands:
        if c.is_file():
            return str(c)
    raise SystemExit(
        "Caption font not found.\n"
        "  Put a .ttf at assets/fonts/caption.ttf (or assets/fonts/Montserrat-VariableFont_wght.ttf),\n"
        "  or set BRAND_CAPTION_FONT in content/brand.md, or export CAPTION_FONT=/path/to/font.ttf.\n"
        "  Free fonts: Google Fonts. See assets/README.md.")


def hex_to_rgba(h: str, alpha: int = 255) -> tuple:
    h = h.strip().lstrip("#")
    if not re.fullmatch(r"[0-9a-fA-F]{6}", h):
        raise SystemExit(f"Not a #RRGGBB colour: #{h}")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def rgba_css(h: str, a: float) -> str:
    r, g, b, _ = hex_to_rgba(h)
    return f"rgba({r},{g},{b},{a})"


def _self_test() -> int:
    sample = (
        "| Token | Value |\n|---|---|\n"
        "| `{BRAND_ACCENT}` | `#12AB34` |\n"
        "- BRAND_ACCENT_DARK = #0a2b3c\n"
        "BRAND_FONT_DISPLAY: Playfair Display\n"
        "| BRAND_FONT_BODY | `{BRAND_FONT_BODY}` |\n"
        "BRAND_RED: {BRAND_RED}\n"
    )
    got = parse_brand_text(sample)
    checks = [
        (got.get("BRAND_ACCENT") == "#12AB34", "table row with backticks"),
        (got.get("BRAND_ACCENT_DARK") == "#0a2b3c", "list item with ="),
        (got.get("BRAND_FONT_DISPLAY") == "Playfair Display", "plain key: value"),
        ("BRAND_FONT_BODY" not in got, "unfilled placeholder ignored (text)"),
        ("BRAND_RED" not in got, "unfilled placeholder ignored (colour)"),
        (hex_to_rgba("#ff0080") == (255, 0, 128, 255), "hex to rgba"),
        (rgba_css("#ff0080", 0.5) == "rgba(255,0,128,0.5)", "rgba css"),
    ]
    bad = [n for ok, n in checks if not ok]
    for ok, n in checks:
        print(f"  {'ok  ' if ok else 'FAIL'} {n}")
    print("self-test:", "PASS" if not bad else f"FAIL ({len(bad)})")
    return 1 if bad else 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(_self_test())
    b = load_brand()
    src = b.pop("_source")
    bf = find_brand_file()
    print(f"brand file: {bf or '(none found; using defaults and env)'}")
    for k, v in b.items():
        print(f"  {k:<20} {v or '(unset)':<28} from {src[k]}")
    try:
        print(f"  caption font file    {find_caption_font(b)}")
    except SystemExit as e:
        print(f"  caption font file    MISSING\n{e}")
