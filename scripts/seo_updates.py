#!/usr/bin/env python3
"""Weekly read of Google Search Central into a dated note.

Part of the search-visibility skill: the Friday measure's "Google's own changes,
weekly" step (skills/search-visibility/reference/geo.md).

Three public sources, no sign-in, no key, read with urllib (standard library only):
  blog    https://developers.google.com/search/blog/feed.xml           (RSS 2.0)
  docs    https://developers.google.com/search/updates/search_docs_updates.rss (RSS 2.0)
  status  https://status.search.google.com/incidents.json              (ranking updates, incidents)

Commands (run from your project folder, or pass --root <folder>)
  fetch  [--since D]           print the items in the window (JSON), tagged by surface
  draft  --date D [--since S]  write content/seo-updates/notes/D.json; since defaults to
                               the newest earlier note's date, else 30 days back
  render --date D              write content/seo-updates/D.html and index.html;
                               refuses (exit 1) while an item tagged as yours has no
                               `meaning` (a session writes that line, never the script)
  due                          exit 0 and print "due" when the newest note is 6 or more
                               days old (or none exists); exit 3 and print "not due"
  --selftest                   fixtures only, no network, no files outside a temp folder

The weekly hook is a session, never a scheduler: the search-visibility Friday measure
runs `due`, then `draft`, fills `meaning`, `owner`, `action` per tagged item, then
`render`. Nothing is sent, posted or deployed by this script.
"""
import argparse
import datetime as dt
import email.utils
import html
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

ROOT = os.getcwd()  # replaced by --root in main()
NOTES_DIR = os.path.join(ROOT, "content/seo-updates/notes")
OUT_DIR = os.path.join(ROOT, "content/seo-updates")


def set_root(root):
    global ROOT, NOTES_DIR, OUT_DIR
    ROOT = os.path.abspath(root)
    NOTES_DIR = os.path.join(ROOT, "content/seo-updates/notes")
    OUT_DIR = os.path.join(ROOT, "content/seo-updates")

SOURCES = {
    "blog": "https://developers.google.com/search/blog/feed.xml",
    "docs": "https://developers.google.com/search/updates/search_docs_updates.rss",
    "status": "https://status.search.google.com/incidents.json",
}
SOURCE_LABEL = {"blog": "Search Central blog", "docs": "Search docs updates",
                "status": "Search status dashboard"}

# First-pass tags; the session reading the note confirms or clears them.
# Edit both lists for your own business: a shop cares about merchant and product
# changes, so take those words out of NOT_OURS and add a "shop" surface.
SURFACES = {
    "watch page": ["videoobject", "video", "clip", "key moment", "youtube", "thumbnail",
                   "transcript", "structured data"],
    "blog article": ["article", "generative ai content", "helpful", "core update",
                     "spam update", "author", "e-e-a-t", "quality rater", "site reputation",
                     "review snippet", "discover"],
    "site": ["robots", "sitemap", "crawl", "index", "canonical", "favicon", "url",
             "search console", "snippet", "google-extended", "ai training", "core web vitals",
             "page experience", "https", "llms", "core update", "spam update",
             "generative ai feature", "ai overview", "ai mode"],
}
NOT_OURS = ["search central live", "learning path", "merchant", "product structured",
            "package tracking", "aggregator unit", "supplier unit", "dataset licensing",
            "ugc fresh data", "indexing api", "job posting", "user-generated spam"]


def strip_tags(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def tag(title, summary):
    t = (title + " " + summary).lower()
    if any(k in t for k in NOT_OURS):
        return []
    return [name for name, keys in SURFACES.items() if any(k in t for k in keys)]


def parse_rss(text, source):
    root = ET.fromstring(text)
    out = []
    for it in root.iter("item"):
        pub = it.findtext("pubDate") or ""
        try:
            day = email.utils.parsedate_to_datetime(pub).date().isoformat()
        except (TypeError, ValueError):
            continue
        title = strip_tags(it.findtext("title"))
        summary = strip_tags(it.findtext("description"))[:600]
        out.append({"source": source, "date": day, "title": title,
                    "url": (it.findtext("link") or "").strip(), "summary": summary,
                    "id": it.findtext("guid") or (it.findtext("link") or "") + day + title})
    return out


def parse_status(text):
    out = []
    for x in json.loads(text):
        begin = (x.get("begin") or "")[:10]
        end = (x.get("end") or "")[:10]
        latest = (x.get("most_recent_update") or {}).get("text", "")
        upd = (x.get("modified") or x.get("begin") or "")[:10]
        title = x.get("external_desc", "")
        summary = f"Began {begin}" + (f", ended {end}" if end else ", still running") + \
            (f". {strip_tags(latest)}" if latest else "")
        out.append({"source": "status", "date": upd, "title": title,
                    "url": "https://status.search.google.com/incidents/" + x.get("id", ""),
                    "summary": summary[:600], "id": x.get("id", title)})
    return out


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (content-studio seo_updates.py)"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode("utf-8", "replace")


def fetch(since):
    items, errors = [], []
    for src, url in SOURCES.items():
        try:
            text = get(url)
            got = parse_status(text) if src == "status" else parse_rss(text, src)
            items += got
        except Exception as e:  # a dead source is named in the note, never silent
            errors.append(f"{src}: {type(e).__name__}: {e}")
    return window(items, since), errors


def window(items, since):
    keep = [i for i in items if i["date"] >= since]
    for i in keep:
        i["touches"] = tag(i["title"], i["summary"])
    keep.sort(key=lambda i: (i["date"], i["source"]), reverse=True)
    return keep


def note_dates(notes_dir=None):
    notes_dir = notes_dir or NOTES_DIR
    if not os.path.isdir(notes_dir):
        return []
    return sorted(f[:-5] for f in os.listdir(notes_dir)
                  if re.fullmatch(r"\d{4}-\d{2}-\d{2}\.json", f))


def default_since(date, notes_dir=None):
    earlier = [d for d in note_dates(notes_dir) if d < date]
    if earlier:
        return earlier[-1]
    return (dt.date.fromisoformat(date) - dt.timedelta(days=30)).isoformat()


def is_due(today, notes_dir=None):
    ds = note_dates(notes_dir)
    if not ds:
        return True
    return (dt.date.fromisoformat(today) - dt.date.fromisoformat(ds[-1])).days >= 6


def missing_meaning(note):
    return [i["title"] for i in note["items"] if i.get("touches") and not i.get("meaning", "").strip()]


E = html.escape

CSS = """:root{--ink:#1a1a1a;--accent:#2f5d8a;--soft:#eef3f8;--line:#d9d9d9}
*{box-sizing:border-box}
body{font-family:system-ui,-apple-system,"Segoe UI",sans-serif;font-size:18px;line-height:1.5;background:#fff;color:var(--ink);margin:0;padding:32px clamp(16px,4vw,64px)}
h1{font-size:36px;line-height:1.15;margin:0 0 12px}
h2{font-size:26px;margin:40px 0 12px}
h3{font-size:22px;margin:0 0 8px}
p,li,td,th{font-size:18px}
code,pre{font-family:ui-monospace,Menlo,monospace;font-size:16px;overflow-wrap:anywhere}
.k{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin:24px 0}
.k div{background:var(--soft);border-radius:12px;padding:18px}
.k b{display:block;font-size:40px;color:var(--accent)}
.box{border:2px solid var(--accent);border-radius:12px;padding:18px;margin:16px 0}
table{border-collapse:collapse;width:100%;table-layout:fixed}
th,td{text-align:left;vertical-align:top;padding:10px 8px;border-bottom:1px solid var(--line);word-break:break-word}
th{background:#f4f4f4}
ol li{margin:8px 0}
.who{color:var(--accent);font-weight:600}
.tag{display:inline-block;background:var(--soft);color:var(--accent);border-radius:6px;padding:0 8px;margin:2px 4px 2px 0;font-size:16px}
a{color:var(--accent)}
a:focus-visible,button:focus-visible{outline:3px solid var(--accent);outline-offset:2px}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
td,th,a,li,p{overflow-wrap:anywhere}
@media (max-width:600px){.hide-sm{display:none}table,tbody,tr,td{display:block;width:auto!important}tr:first-child{display:none}tr{border-bottom:1px solid var(--line);padding:8px 0}td{border:0;padding:4px 0}}"""

HEAD = ('<!doctype html><html lang=en><head><meta charset=utf-8>'
        '<meta name=viewport content="width=device-width,initial-scale=1"><title>{title}</title>'
        '<style>{css}</style></head><body>')


def render_note(note):
    items = note["items"]
    ours = [i for i in items if i.get("touches")]
    rest = [i for i in items if not i.get("touches")]
    acts = [i for i in ours if i.get("action", "").strip() and i.get("action", "").strip().lower() != "none"]
    o = [HEAD.format(title="Search Central " + E(note["date"]), css=CSS)]
    o.append(f"<h1>Google Search changes, week to {E(note['date'])}</h1>")
    o.append(f"<p>Read {E(note['date'])} from Google's own 3 sources, covering {E(note['since'])} to "
             f"{E(note['date'])}: the <a href=\"https://developers.google.com/search/blog\">Search Central blog</a>, "
             f"the <a href=\"https://developers.google.com/search/updates\">Search documentation updates</a> and the "
             f"<a href=\"https://status.search.google.com/\">Search status dashboard</a>. Made by "
             f"<code>scripts/seo_updates.py</code>; the meaning lines are written by "
             f"{E(note.get('read_by', 'the session that read the note'))}.</p>")
    if note.get("errors"):
        o.append("<div class=box><h3>A source could not be read</h3><ul>" +
                 "".join(f"<li>{E(e)}</li>" for e in note["errors"]) + "</ul></div>")
    o.append(f"<div class=k><div><b>{len(items)}</b>changes read</div><div><b>{len(ours)}</b>touch a watch page, "
             f"a blog article or the site</div><div><b>{len(acts)}</b>with an action</div></div>")
    o.append("<h2>Actions, with the owner of each</h2>")
    if acts:
        o.append("<ol>" + "".join(
            f"<li><span class=who>{E(i.get('owner', 'Unassigned'))}.</span> {E(i['action'])} "
            f"(<a href=\"{E(i['url'])}\">{E(i['title'])}</a>)</li>" for i in acts) + "</ol>")
    else:
        o.append("<p>Nothing to do this week.</p>")
    o.append("<h2>What touches us, 1 line each</h2>")
    if ours:
        o.append("<table><tr><th style=\"width:16%\">Date and source</th><th style=\"width:30%\">The change</th>"
                 "<th>What it means for us</th></tr>")
        for i in ours:
            tags = "".join(f"<span class=tag>{E(t)}</span>" for t in i["touches"])
            o.append(f"<tr><td>{E(i['date'])}<br>{E(SOURCE_LABEL[i['source']])}</td>"
                     f"<td><a href=\"{E(i['url'])}\">{E(i['title'])}</a><br>{tags}</td>"
                     f"<td>{E(i.get('meaning', ''))}</td></tr>")
        o.append("</table>")
    else:
        o.append("<p>No change this week touches a watch page, a blog article or the site.</p>")
    o.append("<h2>Read, not ours</h2>")
    if rest:
        o.append("<table><tr><th style=\"width:16%\">Date</th><th>The change</th><th class=hide-sm style=\"width:24%\">Source</th></tr>" +
                 "".join(f"<tr><td>{E(i['date'])}</td><td><a href=\"{E(i['url'])}\">{E(i['title'])}</a>"
                         f"{(' ' + E(i['why_not'])) if i.get('why_not') else ''}</td>"
                         f"<td class=hide-sm>{E(SOURCE_LABEL[i['source']])}</td></tr>" for i in rest) + "</table>")
    else:
        o.append("<p>None.</p>")
    o.append("<h2>How next week's note gets made</h2><ol>"
             "<li><span class=who>The search-visibility Friday measure (a session).</span> "
             "<code>python3 scripts/seo_updates.py due</code>; when it prints due, "
             "<code>python3 scripts/seo_updates.py draft --date &lt;today&gt;</code>.</li>"
             "<li><span class=who>The same session.</span> In <code>content/seo-updates/notes/&lt;today&gt;.json</code> "
             "write <code>meaning</code> (1 line), <code>owner</code> and <code>action</code> on every item tagged as ours, "
             "or clear its <code>touches</code> and give a <code>why_not</code>.</li>"
             "<li><span class=who>The same session.</span> <code>python3 scripts/seo_updates.py render --date &lt;today&gt;</code>, "
             "then 1 line on the Friday board linking the note.</li></ol>")
    if note.get("appendix_html"):
        o.append(note["appendix_html"])
    o.append("</body></html>")
    return "\n".join(o)


def render_index(dates):
    o = [HEAD.format(title="Search Central notes", css=CSS),
         "<h1>Google Search changes, the weekly notes</h1>",
         "<p>One note a week from Google's own sources, made by "
         "<code>scripts/seo_updates.py</code>.</p><table><tr><th>Week to</th><th>Note</th></tr>"]
    for d in sorted(dates, reverse=True):
        o.append(f"<tr><td>{E(d)}</td><td><a style=\"display:inline-block;min-height:44px;padding:10px 0\" href=\"{E(d)}.html\">{E(d)}.html</a></td></tr>")
    o.append("</table></body></html>")
    return "\n".join(o)


def cmd_draft(a):
    since = a.since or default_since(a.date)
    items, errors = fetch(since)
    path = os.path.join(NOTES_DIR, a.date + ".json")
    old = {}
    if os.path.exists(path):  # keep any meaning lines already written
        with open(path) as f:
            prev = json.load(f)
        old = {i["id"]: i for i in prev.get("items", [])}
    for i in items:
        for k in ("meaning", "owner", "action", "why_not", "touches"):
            if i["id"] in old and k in old[i["id"]]:
                i[k] = old[i["id"]][k]
        i.setdefault("meaning", "")
        i.setdefault("owner", "")
        i.setdefault("action", "")
    note = {"date": a.date, "since": since, "items": items, "errors": errors}
    if old and "appendix_html" in prev:
        note["appendix_html"] = prev["appendix_html"]
    os.makedirs(NOTES_DIR, exist_ok=True)
    with open(path, "w") as f:
        json.dump(note, f, indent=1, ensure_ascii=False)
    print(f"{path}: {len(items)} item(s) since {since}, {sum(1 for i in items if i['touches'])} tagged as ours, "
          f"{len(errors)} source error(s)")
    return 0


def cmd_render(a):
    path = os.path.join(NOTES_DIR, a.date + ".json")
    with open(path) as f:
        note = json.load(f)
    miss = missing_meaning(note)
    if miss:
        print("refused: no meaning line on " + "; ".join(miss))
        return 1
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, a.date + ".html")
    with open(out, "w") as f:
        f.write(render_note(note))
    with open(os.path.join(OUT_DIR, "index.html"), "w") as f:
        f.write(render_index(note_dates()))
    print(out)
    return 0


RSS_FIX = """<?xml version="1.0"?><rss version="2.0"><channel>
<item><title>Added creator property in VideoObject structured data</title><link>https://x/a</link>
<description>&lt;p&gt;What: VideoObject docs&lt;/p&gt;</description><pubDate>Thu, 24 Sep 2026 00:00:00 +0000</pubDate><guid>g1</guid></item>
<item><title>Search Central Live is coming to Bogota</title><link>https://x/b</link>
<description>event</description><pubDate>Tue, 08 Sep 2026 00:00:00 +0000</pubDate><guid>g2</guid></item>
<item><title>Updated guidance on crawlable URL structures</title><link>https://x/c</link>
<description>hyphens</description><pubDate>Fri, 23 Oct 2026 00:00:00 +0000</pubDate><guid>g3</guid></item>
<item><title>Bad date</title><pubDate>not a date</pubDate></item>
</channel></rss>"""
STATUS_FIX = json.dumps([{"id": "abc", "begin": "2026-09-24T16:15:00+00:00", "end": "2026-10-08T08:00:00+00:00",
                          "modified": "2026-10-08T08:37:28+00:00", "external_desc": "September 2026 spam update",
                          "most_recent_update": {"text": "The rollout was complete."}}])


def self_test():
    import tempfile
    ok = fails = 0

    def check(name, cond):
        nonlocal ok, fails
        ok, fails = (ok + 1, fails) if cond else (ok, fails + 1)
        print(("ok   " if cond else "FAIL ") + name)

    items = parse_rss(RSS_FIX, "docs") + parse_status(STATUS_FIX)
    check("rss parses 3 dated items, skips the bad date", len([i for i in items if i["source"] == "docs"]) == 3)
    check("status parses with its modified date", any(i["date"] == "2026-10-08" for i in items if i["source"] == "status"))
    w = window(items, "2026-09-20")
    check("window drops the 8 Sep item", all(i["date"] >= "2026-09-20" for i in w) and len(w) == 3)
    by = {i["title"]: i for i in w}
    check("VideoObject change tags the watch page", "watch page" in by["Added creator property in VideoObject structured data"]["touches"])
    check("URL structure tags the site", "site" in by["Updated guidance on crawlable URL structures"]["touches"])
    check("spam update tags blog article and site", set(by["September 2026 spam update"]["touches"]) >= {"blog article", "site"})
    check("an event is not ours", tag("Search Central Live is coming to Bogota", "event") == [])
    check("newest first", [i["date"] for i in w] == sorted([i["date"] for i in w], reverse=True))
    with tempfile.TemporaryDirectory() as d:
        check("due with no notes", is_due("2026-11-02", d))
        check("since defaults to 30 days back", default_since("2026-11-02", d) == "2026-10-03")
        open(os.path.join(d, "2026-11-02.json"), "w").write("{}")
        check("not due 4 days later", not is_due("2026-11-06", d))
        check("due 6 days later", is_due("2026-11-08", d))
        check("since defaults to the previous note", default_since("2026-11-09", d) == "2026-11-02")
    note = {"date": "2026-11-02", "since": "2026-09-20", "items": w, "errors": []}
    for i in w:
        i.setdefault("meaning", "")
    check("render refuses an ours item with no meaning", len(missing_meaning(note)) == 3)
    for i in w:
        i["meaning"] = "line"
        i["owner"], i["action"] = "The creator", "none"
    page = render_note(note)
    check("render passes once every line is written", not missing_meaning(note) and "<h1>" in page)
    check("rendered page carries no em dash", "\u2014" not in page)
    check("action none is not listed as an action", "Nothing to do this week." in page)
    with tempfile.TemporaryDirectory() as d:
        keep = (ROOT, NOTES_DIR, OUT_DIR)
        set_root(d)
        os.makedirs(NOTES_DIR)
        with open(os.path.join(NOTES_DIR, "2026-11-02.json"), "w") as f:
            json.dump(note, f)

        class A:
            date = "2026-11-02"
        import io
        import contextlib
        with contextlib.redirect_stdout(io.StringIO()):
            rc = cmd_render(A())
        idx = open(os.path.join(OUT_DIR, "index.html")).read()
        check("render writes the note and the index under --root", rc == 0 and
              os.path.exists(os.path.join(OUT_DIR, "2026-11-02.html")))
        check("the index links each note by a relative path", 'href="2026-11-02.html"' in idx and "file://" not in idx)
        set_root(os.path.dirname(os.path.dirname(keep[1])))
    print(f"{ok} passed, {fails} failed")
    return 1 if fails else 0


def main():
    if "--self-test" in sys.argv or "--selftest" in sys.argv:
        return self_test()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=os.getcwd(), help="your project folder (default: the current folder)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch")
    f.add_argument("--since", default=(dt.date.today() - dt.timedelta(days=7)).isoformat())
    d = sub.add_parser("draft")
    d.add_argument("--date", required=True)
    d.add_argument("--since")
    r = sub.add_parser("render")
    r.add_argument("--date", required=True)
    sub.add_parser("due")
    a = ap.parse_args()
    set_root(a.root)
    if a.cmd == "fetch":
        items, errors = fetch(a.since)
        print(json.dumps({"items": items, "errors": errors}, indent=1, ensure_ascii=False))
        return 1 if errors else 0
    if a.cmd == "draft":
        return cmd_draft(a)
    if a.cmd == "render":
        return cmd_render(a)
    if a.cmd == "due":
        due = is_due(dt.date.today().isoformat())
        print("due" if due else "not due")
        return 0 if due else 3


if __name__ == "__main__":
    sys.exit(main())
