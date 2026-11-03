"""Where things live for the shorts pipeline, and the per-project config every script reads.

Every script in this folder imports this module and never hard-codes a path. Each value comes from, later wins:
  1. the defaults below
  2. config.json beside this file (copy config.example.json), or the file named by SHORTS_CONFIG
  3. an environment variable of the name given against each value

    BUILD     this folder (the code, looks.html, tutorial.html, springs.js)
    REPO      your project root: SHORTS_PROJECT_ROOT, else config "project_root", else the first folder above this one
              that holds .claude/ or .git/, else the current folder
    SPECS     one JSON per short, in <slug>/ subfolders: SHORTS_SPECS_DIR, else config "specs_dir", else BUILD/specs
    OUT       the finished shorts, in <slug>/ subfolders: SHORTS_OUT_DIR, else config "out_dir", else BUILD/finished
    WORKROOT  the render cache: SHORTS_WORK_DIR, else config "work_dir", else ~/.cache/shorts-pipeline/work.
              Keep it OUTSIDE any folder a sync job mirrors (cloud drive, a git auto-commit): a cache inside one is
              copied 2 or 3 times while it renders and fills the disk (render-reliability.md).
    MEDIA     the tracks and their transcripts: SHORTS_MEDIA_ROOT, else config "media_root", else ~/media-cache
    FONTDIR   the fonts the captions and the pages load: SHORTS_FONT_DIR, else config "font_dir", else
              REPO/.claude/skills/shorts-editor/assets/fonts
    SK        the shorts-editor scripts (check_caption_size.py, check_safe_area.py, verify_speaker.py, brand.py):
              SHORTS_EDITOR_SCRIPTS, else config "skill_scripts", else REPO/.claude/skills/shorts-editor/scripts

Paths inside config.json are relative to the config file. Brand values (the accent colour, its dark partner, an
optional logo and mascot illustration) come from config "brand", else from the shorts-editor's brand.py (which reads
content/brand.md), else a neutral placeholder blue.

Specs written on another machine: config "path_remap" is a list of [old_prefix, new_prefix] pairs. Every loader
passes what it reads through remap_obj, and anything written back into a spec goes through canon_obj first, so the
spec files keep one spelling whichever machine renders them. With no pairs, remap is the identity.

The looks pages (looks.html, anim_looks.html, tutorial.html) carry tokens instead of absolute URLs:
{{FONT_DIR}}, {{PIPELINE_DIR}}, {{LOGO_SVG}}, {{MASCOT_PNG}}, {{ACCENT}}, {{ACCENT_DARK}}. page_for_this_mac writes
a copy with the tokens filled into the cache, and that copy is what the browser opens.

    python3 paths.py        prints what it resolved and from where
"""
import json
import os
from pathlib import Path

BUILD = Path(os.path.abspath(__file__)).parent      # abspath, never resolve(): a symlinked project keeps its own spelling
HOME = Path.home()


def _find_config():
    env = os.environ.get("SHORTS_CONFIG")
    if env:
        return Path(env).expanduser()
    for name in ("config.json", "config.example.json"):
        p = BUILD / name
        if p.is_file():
            return p
    return None


CONFIG_PATH = _find_config()
CONFIG = json.loads(CONFIG_PATH.read_text()) if CONFIG_PATH and CONFIG_PATH.is_file() else {}
_CFG_DIR = CONFIG_PATH.parent if CONFIG_PATH else BUILD


def _cfg_path(key):
    v = CONFIG.get(key)
    if not v:
        return None
    p = Path(os.path.expanduser(str(v)))
    return p if p.is_absolute() else (_CFG_DIR / p)


def _pick(env, key, default):
    e = os.environ.get(env)
    if e:
        return Path(os.path.expanduser(e))
    c = _cfg_path(key)
    return c if c else default


def _project_root():
    for d in [BUILD, *BUILD.parents]:
        if (d / ".claude").is_dir() or (d / ".git").exists():
            return d
    return Path.cwd()


REPO = _pick("SHORTS_PROJECT_ROOT", "project_root", _project_root())
SET = BUILD                                          # the set folder: the code and its specs travel together
SPECS = _pick("SHORTS_SPECS_DIR", "specs_dir", BUILD / "specs")
OUT = _pick("SHORTS_OUT_DIR", "out_dir", BUILD / "finished")
WORKROOT = _pick("SHORTS_WORK_DIR", "work_dir", HOME / ".cache" / "shorts-pipeline" / "work")
AUDIO16 = WORKROOT.parent / "audio16"
MEDIA = _pick("SHORTS_MEDIA_ROOT", "media_root", HOME / "media-cache")
FONTDIR = _pick("SHORTS_FONT_DIR", "font_dir", REPO / ".claude" / "skills" / "shorts-editor" / "assets" / "fonts")
SK = _pick("SHORTS_EDITOR_SCRIPTS", "skill_scripts", REPO / ".claude" / "skills" / "shorts-editor" / "scripts")
RESULTS = WORKROOT.parent / "results.jsonl"          # one row per finished build; the last row per id is the one that counts

# ---------------------------------------------------------------- brand
_DEFAULT_ACCENT, _DEFAULT_ACCENT_DARK = "#4F9DFF", "#1F4F8F"   # neutral placeholder blue: set yours in config or content/brand.md


def _brand_from_skill():
    try:
        import sys
        if str(SK) not in sys.path:
            sys.path.insert(0, str(SK))
        import brand as _b   # the shorts-editor's brand layer (reads content/brand.md)
        return _b.load_brand()
    except Exception:  # noqa: BLE001  (brand.py absent or unreadable: the placeholder stands)
        return {}


_B = CONFIG.get("brand") or {}
_SB = {} if (_B.get("accent") and _B.get("accent_dark")) else _brand_from_skill()
ACCENT = _B.get("accent") or _SB.get("BRAND_ACCENT") or _DEFAULT_ACCENT
ACCENT_DARK = _B.get("accent_dark") or _SB.get("BRAND_ACCENT_DARK") or _DEFAULT_ACCENT_DARK
LOGO_SVG = _cfg_path("logo_svg") if not _B.get("logo_svg") else (
    Path(os.path.expanduser(_B["logo_svg"])) if os.path.isabs(os.path.expanduser(_B["logo_svg"])) else _CFG_DIR / _B["logo_svg"])
MASCOT_PNG = (Path(os.path.expanduser(_B["mascot_png"])) if os.path.isabs(os.path.expanduser(_B["mascot_png"])) else _CFG_DIR / _B["mascot_png"]) if _B.get("mascot_png") else None
EMPTY_IMG = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='1' height='1'/%3E"


def ass_colour(hex_rgb, alpha="00"):
    """#RRGGBB -> libass &HAABBGGRR (libass writes blue first)."""
    h = hex_rgb.lstrip("#")
    return f"&H{alpha}{h[4:6]}{h[2:4]}{h[0:2]}".upper()


ACCENT_ASS = ass_colour(ACCENT)
ACCENT_DARK_ASS = ass_colour(ACCENT_DARK)

# names that are YOURS (your brand, your show): the credit never puts one beside a guest's name
OWN_NAMES = list(CONFIG.get("own_names") or [])
# slug -> the guest's own firm or organisation, for the credit line when a spec carries no people.guest.firm
FIRMS = dict(CONFIG.get("firms") or {})

# ---------------------------------------------------------------- path remap (specs written on another machine)
_TABLE = sorted(((str(a), str(b)) for a, b in (CONFIG.get("path_remap") or [])), key=lambda t: -len(t[0]))


def _swap(s, table):
    for old, new in table:
        if s == old or s.startswith(old.rstrip("/") + "/"):
            return new + s[len(old):]
    return s


def remap(p):
    """a path as another machine wrote it -> this machine's path; str in, str out; Path in, Path out; else untouched."""
    if isinstance(p, Path):
        return Path(_swap(str(p), _TABLE))
    if isinstance(p, str):
        return _swap(p, _TABLE)
    return p


def canon(p):
    """the inverse: this machine's path -> the spelling the spec files keep (longest new prefix first)."""
    inv = sorted(((new, old) for old, new in _TABLE), key=lambda t: -len(t[0]))
    if isinstance(p, Path):
        return Path(_swap(str(p), inv))
    if isinstance(p, str):
        return _swap(p, inv)
    return p


def _walk(o, f):
    if isinstance(o, dict):
        return {k: _walk(v, f) for k, v in o.items()}
    if isinstance(o, list):
        return [_walk(v, f) for v in o]
    if isinstance(o, tuple):
        return tuple(_walk(v, f) for v in o)
    return f(o)


def _media_rel(o):
    """a spec path that is relative is read from MEDIA (so a spec can say "podcast-guest-a/host-cfr.mp4")."""
    if isinstance(o, str) and o and not o.startswith(("/", "~", "http:", "https:", "data:")) and o.endswith(
            (".mp4", ".mov", ".m4a", ".wav", ".json", ".png", ".jpg")):
        return str(MEDIA / o)
    if isinstance(o, str) and o.startswith("~"):
        return os.path.expanduser(o)
    return o


def remap_obj(o):
    """every string in a loaded spec that STARTS with an old prefix is remapped; a relative media path is read from
    MEDIA; prose that only mentions a path stays."""
    return _walk(_walk(o, remap), _media_rel)


def canon_obj(o):
    return _walk(o, canon)


def load_json(path):
    return remap_obj(json.loads(Path(path).read_text()))


# ---------------------------------------------------------------- the looks pages
def page_tokens():
    return {
        "{{FONT_DIR}}": str(FONTDIR),
        "{{PIPELINE_DIR}}": str(BUILD),
        "{{LOGO_SVG}}": ("file://" + str(LOGO_SVG)) if LOGO_SVG and Path(LOGO_SVG).is_file() else EMPTY_IMG,
        "{{MASCOT_PNG}}": ("file://" + str(MASCOT_PNG)) if MASCOT_PNG and Path(MASCOT_PNG).is_file() else EMPTY_IMG,
        "{{ACCENT}}": ACCENT,
        "{{ACCENT_DARK}}": ACCENT_DARK,
    }


def remap_text(s):
    """the page's tokens filled in, then every file:// URL that starts with an old prefix remapped."""
    import re
    for k, v in page_tokens().items():
        s = s.replace(k, v)
    if not _TABLE:
        return s
    return re.sub(r"file://(/[^\"'()\s<>]*)", lambda m: "file://" + remap(m.group(1)), s)


def page_for_this_mac(html_path, cache_dir):
    """the page the browser should open: a copy with the tokens filled, under cache_dir, named by the original's hash
    (the pages hold no relative URLs, only file:/// ones and url(#id) fragments, so the copy may live anywhere)."""
    import hashlib
    html_path = Path(html_path)
    src = html_path.read_text()
    out = remap_text(src)
    if out == src:
        return html_path
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha1((src + json.dumps(page_tokens(), sort_keys=True)).encode()).hexdigest()[:10]
    dst = cache_dir / f"{html_path.stem}-{key}.html"
    if not dst.exists() or dst.read_text() != out:
        dst.write_text(out)
    return dst


page_for_this_machine = page_for_this_mac


def free_gb():
    """free space on the disk that holds the work folder."""
    import shutil
    d = WORKROOT if WORKROOT.exists() else HOME
    return shutil.disk_usage(str(d)).free / 1e9


if __name__ == "__main__":
    print(f"config   {CONFIG_PATH}")
    for k in ("BUILD", "REPO", "SPECS", "OUT", "WORKROOT", "MEDIA", "FONTDIR", "SK", "RESULTS"):
        print(f"{k:9}{globals()[k]}")
    print(f"accent   {ACCENT} (ASS {ACCENT_ASS}), dark {ACCENT_DARK}")
    print(f"remap    {len(_TABLE)} pair(s); own names {OWN_NAMES}; firms for {len(FIRMS)} slug(s)")
