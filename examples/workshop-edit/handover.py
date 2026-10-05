#!/usr/bin/env python3
"""The handover page: the files, their lengths, the deep-pass result, the chapters, the publish kit, what was
left out on purpose, the open decisions and the next steps with an owner on each. Light mode, one HTML file.

  python3 handover.py [--config config.json]      -> <out>/handover.html

A page that embeds <video> must be served, not opened as a file: `python3 scripts/serve_outputs.py`, then
http://localhost:4200/<path under outputs/>. This page links the files by path and embeds no video.
"""
import argparse
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_config, probe_duration  # noqa: E402

CSS = """:root{--ink:#111111;--muted:#666666;--line:#E0E0E0;--panel:#F6F3EC;--accent:#2B5C8A}
body{font-family:system-ui,-apple-system,"Segoe UI",sans-serif;font-size:18px;color:var(--ink);background:#FFFFFF;margin:0;
padding:clamp(16px,4vw,64px);line-height:1.5}
h1{font-size:36px;margin:0 0 8px}h2{font-size:26px;margin:40px 0 12px;color:var(--accent)}
table{border-collapse:collapse;width:100%;margin:12px 0}td,th{border:1px solid var(--line);padding:10px 12px;text-align:left;vertical-align:top}
th{background:var(--panel)}code{font-size:16px;background:var(--panel);padding:2px 6px;border-radius:4px;word-break:break-all}
pre{background:var(--panel);padding:14px;border-radius:6px;white-space:pre-wrap;font-size:16px}
.card{border:1px solid var(--line);border-left:6px solid var(--accent);padding:16px 20px;border-radius:8px;margin:12px 0}
.muted{color:var(--muted);font-size:16px}"""


def mmss(s):
    return f"{int(s // 60)}:{int(s % 60):02d}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=None)
    args = ap.parse_args()
    cfg = load_config(args.config, need_recording=False)
    out_dir, ho = cfg["out_dir"], cfg.get("handover", {})
    e = html.escape
    h = [f"<!doctype html><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
         f"<title>{e(ho.get('title', 'Handover'))}</title><style>{CSS}</style>",
         f"<h1>{e(ho.get('title', 'Handover'))}</h1>"]
    if ho.get("rulings"):
        h.append(f"<p class='muted'>{e(ho['rulings'])}</p>")
    h.append("<h2>The files</h2><table><tr><th>Cut</th><th>File</th><th>Length</th><th>Deep pass</th></tr>")
    for cut in cfg.get("cuts", {}):
        p = out_dir / f"{cut}.mp4"
        if not p.exists():
            h.append(f"<tr><td>{e(cut)}</td><td>not rendered yet</td><td></td><td></td></tr>")
            continue
        chk_p = out_dir / f"{cut}.check.json"
        dp = "not run"
        if chk_p.exists():
            chk = json.loads(chk_p.read_text())
            dp = f"{chk.get('status', '?')}: video and audio differ by {chk['av_diff_s']}s; " + (
                "; ".join(chk.get("findings", [])) or "no findings")
        size = f"{mmss(probe_duration(p))}, {p.stat().st_size / 1e6:.0f} MB"
        h.append(f"<tr><td>{e(cut)}</td><td><code>{e(str(p.resolve()))}</code></td><td>{e(size)}</td><td>{e(dp)}</td></tr>")
    h.append("</table>")
    for cut, pub in cfg.get("publish", {}).items():
        h.append(f"<h2>{e(cut)}: publish kit</h2><p><b>Title</b></p><pre>{e(pub.get('title', ''))}</pre>"
                 f"<p><b>Description</b></p><pre>{e(pub.get('description', ''))}</pre>")
        ch = out_dir / f"{cut}.chapters.txt"
        if ch.exists():
            h.append(f"<p><b>Chapters</b> (on the delivered timeline)</p><pre>{e(ch.read_text().strip())}</pre>")
    if ho.get("left_out"):
        h.append("<h2>Left out on purpose</h2><ul>" + "".join(f"<li>{e(x)}</li>" for x in ho["left_out"]) + "</ul>"
                 "<p class='muted'>Say which to put back, in one line each.</p>")
    if ho.get("decisions"):
        h.append("<h2>What is yours to decide</h2>" + "".join(f"<div class='card'>{e(x)}</div>" for x in ho["decisions"]))
    if ho.get("next_steps"):
        h.append("<h2>Next steps</h2><table><tr><th>Step</th><th>Owner</th></tr>" +
                 "".join(f"<tr><td>{e(s)}</td><td>{e(o)}</td></tr>" for s, o in ho["next_steps"]) + "</table>")
    out = out_dir / "handover.html"
    out.write_text("\n".join(h))
    print(out)


if __name__ == "__main__":
    main()
