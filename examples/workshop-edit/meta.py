#!/usr/bin/env python3
"""Emit a YouTube-style upload payload for one cut, from the config's "publish" block plus the measured chapters.

  python3 meta.py <cut> [--config config.json] > payload.json

The chapters come from <out>/<cut>.chapters.txt, which build.py writes on the DELIVERED (sped) timeline. The
payload is private by default: a person flips it public after watching the file.

Before this payload is used: every promise made on camera ("link below", "the free resource") must be a live URL
in the description, fetched and returning 200 in the same session. `--check-links` fetches every URL in the
description and refuses if any does not return 200.
"""
import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_config  # noqa: E402


def check_links(text):
    bad = []
    for url in sorted(set(re.findall(r"https?://[^\s)>\]]+", text))):
        try:
            req = urllib.request.Request(url, method="GET", headers={"User-Agent": "Mozilla/5.0 link-check"})
            with urllib.request.urlopen(req, timeout=15) as r:
                if r.status != 200:
                    bad.append((url, r.status))
        except Exception as e:  # noqa: BLE001
            bad.append((url, str(e)))
    return bad


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cut")
    ap.add_argument("--config", default=None)
    ap.add_argument("--check-links", action="store_true", help="fetch every URL in the description; refuse on any non-200")
    args = ap.parse_args()
    cfg = load_config(args.config, need_recording=False)
    pub = cfg.get("publish", {}).get(args.cut)
    if not pub:
        raise SystemExit(f"no publish block for {args.cut!r} in the config")
    desc = pub["description"].strip()
    ch = cfg["out_dir"] / f"{args.cut}.chapters.txt"
    if ch.exists() and ch.read_text().strip():
        desc += "\n\nChapters:\n" + ch.read_text().strip()
    if "{" in pub["title"] + desc:
        print("warning: the title or description still carries a {PLACEHOLDER}", file=sys.stderr)
    if args.check_links:
        bad = check_links(desc)
        if bad:
            for url, why in bad:
                print(f"NOT LIVE: {url} ({why})", file=sys.stderr)
            raise SystemExit(1)
    print(json.dumps({
        "title": pub["title"],
        "description": desc,
        "tags": pub.get("tags", []),
        "categoryId": str(pub.get("category_id", "22")),
        "privacyStatus": "private",
        "videoFile": str((cfg["out_dir"] / f"{args.cut}.mp4").resolve()),
    }, indent=1))


if __name__ == "__main__":
    main()
