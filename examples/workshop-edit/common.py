#!/usr/bin/env python3
"""Shared config loading for the workshop-edit example pipeline.

Every script in this folder reads one JSON config (copy config.example.json to config.json and fill it in).
Paths inside the config are resolved relative to the config file's own folder, so the whole edit folder can
move without editing anything. Keys starting with "_" are comments and are ignored.

Config location, first match wins:
  1. --config <path> on the command line
  2. the WORKSHOP_CONFIG environment variable
  3. ./config.json in the current working directory
"""
import json
import os
from pathlib import Path

PATH_KEYS = ("recording", "transcript", "silences", "out_dir", "fonts_dir", "slide_states")


def strip_comments(obj):
    if isinstance(obj, dict):
        return {k: strip_comments(v) for k, v in obj.items() if not str(k).startswith("_")}
    if isinstance(obj, list):
        return [strip_comments(v) for v in obj]
    return obj


def load_config(path=None, need_recording=True):
    p = Path(path or os.environ.get("WORKSHOP_CONFIG") or "config.json").expanduser().resolve()
    if not p.exists():
        raise SystemExit(f"config not found: {p}\nCopy config.example.json to config.json and fill it in, "
                         f"or pass --config <path>.")
    cfg = strip_comments(json.loads(p.read_text()))
    base = p.parent
    cfg["_base"] = base
    for k in PATH_KEYS:
        if cfg.get(k):
            cfg[k] = (base / cfg[k]).resolve()
    cfg.setdefault("out_dir", (base / "renders").resolve())
    if not isinstance(cfg["out_dir"], Path):
        cfg["out_dir"] = (base / cfg["out_dir"]).resolve()
    cfg["out_dir"].mkdir(parents=True, exist_ok=True)
    cfg.setdefault("silences", cfg["out_dir"] / "silences.json")
    if need_recording and not (cfg.get("recording") and Path(cfg["recording"]).exists()):
        raise SystemExit(f"recording not found: {cfg.get('recording')}. Set \"recording\" in {p}.")
    return cfg


def resolve(cfg, rel):
    """Resolve a path string from the config against the config's folder."""
    if rel is None:
        return None
    q = Path(rel).expanduser()
    return q if q.is_absolute() else (cfg["_base"] / q).resolve()


def hex_to_ass(hex_colour):
    """'#RRGGBB' -> '&H00BBGGRR' (ASS colours are little-endian BGR with a leading alpha byte)."""
    h = hex_colour.lstrip("#")
    if len(h) != 6:
        raise ValueError(f"colour must be #RRGGBB, got {hex_colour!r}")
    r, g, b = h[0:2], h[2:4], h[4:6]
    return f"&H00{b}{g}{r}".upper()


def probe_duration(path, stream=None):
    import subprocess
    if stream:
        args = ["ffprobe", "-v", "error", "-select_streams", stream, "-show_entries", "stream=duration",
                "-of", "csv=p=0", str(path)]
    else:
        args = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)]
    out = subprocess.run(args, capture_output=True, text=True).stdout.strip()
    try:
        return float(out.splitlines()[0])
    except (ValueError, IndexError):
        return 0.0
