#!/usr/bin/env python3
"""The posting plan: one leg per platform per slot, in content/posting/plan.jsonl.

A leg is one post on one platform at one time. Its life:
  empty -> draft -> approved (approved_by recorded) -> uploaded (the platform took it) -> posted (read back, proof on the leg)
  a leg on a platform with no posting API for your account (TikTok, Substack by default) becomes `hand`: a card, your hand
  failed (3 errors), skipped (an empty slot given up to a moved leg)

    python3 posting/scripts/plan.py skeleton --start 2026-11-09         # 7 days of empty legs from the slots in your config
    python3 posting/scripts/plan.py next-week                           # the Sunday job: next Monday's week, then the check
    python3 posting/scripts/plan.py add 2026-11-12 substack_post --time 09:00   # one empty leg outside the grid
    python3 posting/scripts/plan.py list [--week 2026-11-09] [--all]
    python3 posting/scripts/plan.py show <leg>                          # one leg in full, caption and all
    python3 posting/scripts/plan.py set <leg> file=/abs/clip.mp4 'caption=...' [title=...] [thumb=/abs/t.jpg] [first_comment=...] --by "You"
    python3 posting/scripts/plan.py lock <leg> caption file --by "You"  # fields the night may never change
    python3 posting/scripts/plan.py check [--week ...] [--all]          # every gate; exit 1 on any failure
    python3 posting/scripts/plan.py approve <leg|DATE> [--week] --by "Your name, date, where you read it"
    python3 posting/scripts/plan.py links-pending                       # shorts that still owe the full-video link
    python3 posting/scripts/plan.py add-link <leg> 'Full video: https://...' --by "You"
    python3 posting/scripts/plan.py posted <leg> --url https://... --by "You"   # your own hand post, recorded with its URL
    python3 posting/scripts/plan.py reslot-missed [--at 2026-11-10T09:00] [--dry-run]
    python3 posting/scripts/plan.py --selftest                          # offline, temp files only

Project folder: --project DIR, else $CONTENT_PROJECT, else the current folder. Config: content/posting/config.json
(copy posting/config.example.json there). Standard library only.

Rules this file enforces in code:
- Nothing is approved without a name (`approve --by`, refused when empty), and `set` can never write approved_by or status=approved.
- Approval is on the exact file: its sha256 is recorded, and a changed file, caption, title, description or first comment drops it.
- The night (`--by night`) can never change a field on the leg's `locked` list.
- No leg is held for a missing full-video link: the short goes first, `add-link` adds the link later, approval kept.
- A missed machine leg moves to the soonest open slot of its kind in the same Monday-to-Sunday week (next week when
  this one is full); a missed hand leg stays open until its slot's day ends, then moves by the same rule.
"""
import sys
sys.dont_write_bytecode = True   # no __pycache__ next to the scripts

import argparse, hashlib, json, os, re, shutil, subprocess, tempfile
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import unquote
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
DOW = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
KINDS = {
    "youtube_long": "youtube", "youtube_short": "youtube",
    "linkedin_video": "linkedin", "linkedin_written": "linkedin",
    "instagram_reel": "instagram",
    "tiktok_video": "tiktok",
    "substack_post": "substack",
}
VIDEO_KINDS = {"youtube_long", "youtube_short", "linkedin_video", "instagram_reel", "tiktok_video"}
SHORT_KINDS = {"youtube_short", "instagram_reel", "tiktok_video", "linkedin_video"}
STATUSES = ("empty", "draft", "approved", "uploaded", "posted", "failed", "hand", "skipped")
OUT_OF_SLOT = ("empty", "failed", "skipped")          # a leg in one of these does not hold its slot
WORD_FIELDS = ("caption", "title", "description", "first_comment")
GUARDED = ("approved_by", "approved_at", "file_sha256", "post_id", "comment_id")   # only the commands write these
DEFAULT_HAND = ["tiktok", "substack"]


# ---------- context ----------

class Ctx:
    def __init__(self, project=None, config=None):
        self.project = Path(project or os.environ.get("CONTENT_PROJECT") or os.getcwd()).resolve()
        cfg_path = Path(config) if config else self.project / "content" / "posting" / "config.json"
        if not cfg_path.exists():
            raise SystemExit(f"no config at {cfg_path}. Copy posting/config.example.json there and fill it in.")
        self.cfg_path = cfg_path
        self.cfg = json.loads(cfg_path.read_text())
        self.tz = ZoneInfo(self.cfg.get("timezone", "UTC"))
        self.plan = self.path(self.cfg.get("plan", "content/posting/plan.jsonl"))
        self.log = self.path(self.cfg.get("log", "content/posting/log.jsonl"))
        self.cards = self.path(self.cfg.get("hand_cards_dir", "content/posting/hand-cards"))
        self.hand_platforms = set(self.cfg.get("hand_platforms", DEFAULT_HAND))
        self.stale_hours = float(self.cfg.get("stale_hours", 6))
        self.slots = self.cfg.get("slots", {})
        self._clock = None

    def path(self, p):
        p = Path(p)
        return p if p.is_absolute() else self.project / p

    def now(self):
        return self._clock or datetime.now(self.tz).replace(second=0, microsecond=0)

    def set_clock(self, at):
        if at:
            dt = datetime.fromisoformat(at)
            self._clock = dt if dt.tzinfo else dt.replace(tzinfo=self.tz)

    def is_hand(self, leg):
        return leg.get("platform") in self.hand_platforms or leg.get("status") == "hand"


def ctx_from(a):
    c = Ctx(getattr(a, "project", None), getattr(a, "config", None))
    c.set_clock(getattr(a, "at", None))
    return c


# ---------- the plan file ----------

def load(ctx):
    if not ctx.plan.exists():
        return []
    return [json.loads(x) for x in ctx.plan.read_text().splitlines() if x.strip()]


def save(ctx, rows, floor):
    """Read all, write once, never fewer rows than were read."""
    if len(rows) < floor:
        raise SystemExit(f"refusing to write {len(rows)} legs over a plan that held {floor}")
    ctx.plan.parent.mkdir(parents=True, exist_ok=True)
    tmp = ctx.plan.with_name(ctx.plan.name + ".writing")
    with open(tmp, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(tmp, ctx.plan)


def log(ctx, leg_id, event, **kw):
    ctx.log.parent.mkdir(parents=True, exist_ok=True)
    with open(ctx.log, "a") as f:
        f.write(json.dumps({"at": ctx.now().isoformat(), "leg": leg_id, "event": event, **kw}, ensure_ascii=False) + "\n")


def logged_today(ctx, event, leg_id):
    if not ctx.log.exists():
        return False
    day = ctx.now().date().isoformat()
    for line in ctx.log.read_text().splitlines():
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if e.get("event") == event and e.get("leg") == leg_id and str(e.get("at", "")).startswith(day):
            return True
    return False


def find(rows, lid):
    for r in rows:
        if r["id"] == lid:
            return r
    raise SystemExit(f"no leg {lid}; plan.py list shows them")


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def slot_dt(ctx, leg):
    dt = datetime.fromisoformat(leg["slot"])
    return dt if dt.tzinfo else dt.replace(tzinfo=ctx.tz)


def week_of(d):
    return d - timedelta(days=d.weekday())


def leg_week(r):
    return week_of(date.fromisoformat(r["date"])).isoformat()


def stamp(ctx):
    return ctx.now().isoformat(timespec="minutes")


# ---------- building the week ----------

def new_leg(ctx, lid, day, kind, slot, by):
    return {
        "id": lid, "date": day.isoformat(), "slot": slot.isoformat(), "kind": kind, "platform": KINDS[kind],
        "piece": "", "title": "", "file": "", "file_sha256": "", "thumb": "", "caption": "", "description": "",
        "first_comment": "", "mentions": [], "status": "empty", "approved_by": "", "approved_at": "", "locked": [],
        "review": "", "post_id": "", "post_url": "", "comment_id": "", "scheduled_for": "", "attempts": 0,
        "comment_attempts": 0, "last_error": "", "notes": "", "changed_by": by, "updated_at": stamp(ctx),
    }


def leg_id(rows, day, kind):
    base = f"{day.isoformat()}-{kind.replace('_', '-')}"
    have = {r["id"] for r in rows}
    if base not in have:
        return base
    n = 2
    while f"{base}-{n}" in have:
        n += 1
    return f"{base}-{n}"


def build_skeleton(ctx, rows, start, by="skeleton"):
    """7 days of empty legs from the config's slots. A day that already holds a live leg of that kind gets no second,
    empty one, so a moved leg and a fresh slot never double the day."""
    added, taken = [], []
    for i in range(7):
        day = start + timedelta(days=i)
        for kind, spec in ctx.slots.items():
            if kind not in KINDS or DOW[day.weekday()] not in spec.get("days", []):
                continue
            base = f"{day.isoformat()}-{kind.replace('_', '-')}"
            if any(r["id"] == base for r in rows):
                continue
            holder = [r["id"] for r in rows if r["date"] == day.isoformat() and r["kind"] == kind and r["status"] not in OUT_OF_SLOT]
            if len(holder) >= int(spec.get("max_per_day", 1)):
                taken.append((base, holder[0]))
                continue
            hh, mm = (int(x) for x in spec["time"].split(":"))
            slot = datetime(day.year, day.month, day.day, hh, mm, tzinfo=ctx.tz)
            rows.append(new_leg(ctx, base, day, kind, slot, by))
            added.append(base)
    return added, taken


# ---------- changing a leg ----------

def apply_fields(ctx, r, kv, by):
    """Change fields on one leg. Refuses: a locked field when the night asks, approved_by and the other guarded fields,
    status=approved (approval is its own command), and new words on media that already went up."""
    night = by.strip().lower().startswith("night")
    for k in kv:
        if night and k in r.get("locked", []):
            raise SystemExit(f"{r['id']}: {k} is locked; the night may never change it")
        if k in GUARDED:
            raise SystemExit(f"{k} is written only by approve, the runner or add-link, never by set")
        if k == "status" and kv[k] in ("approved", "uploaded", "posted"):
            raise SystemExit(f"status={kv[k]} is set only by approve, the runner or `posted`")
        if k == "status" and kv[k] not in STATUSES:
            raise SystemExit(f"status must be one of {', '.join(STATUSES)}")
    changed_words = [k for k in WORD_FIELDS if k in kv and kv[k] != r.get(k, "")]
    if changed_words and r["status"] in ("uploaded", "posted"):
        raise SystemExit(f"{r['id']} is already on the platform; change its words there, then record it in notes")
    drop = bool(changed_words and r.get("approved_by"))
    for k, v in kv.items():
        if k == "locked":
            r["locked"] = [x for x in v.split(",") if x] if isinstance(v, str) else list(v)
        elif k == "mentions":
            r["mentions"] = json.loads(v) if isinstance(v, str) else v
        elif k in ("attempts", "comment_attempts"):
            r[k] = int(v)
        elif k in ("file", "thumb"):
            if not v:
                r[k] = ""
                if k == "file":
                    r["file_sha256"] = ""
                continue
            p = Path(v)
            if not p.is_absolute() or not p.exists() or p.stat().st_size == 0:
                raise SystemExit(f"{k} must be an existing, non-empty file given by its full path: {v}")
            if k == "file":
                new = sha(p)
                if r.get("file_sha256") and new != r["file_sha256"] and r.get("approved_by"):
                    drop = True
                    changed_words.append("file")
                r["file_sha256"] = new
            r[k] = str(p)
        elif k in r or k in ("date", "slot"):
            r[k] = v
        else:
            raise SystemExit(f"unknown field {k}; the fields are: {', '.join(sorted(r))}")
    if "slot" in kv:
        r["date"] = datetime.fromisoformat(r["slot"]).date().isoformat()
    if r["status"] == "empty" and (r["file"] or r["caption"]):
        r["status"] = "draft"
    if drop:
        r.update(approved_by="", approved_at="", status="draft")
        r["notes"] = (r.get("notes", "") + f" | {', '.join(changed_words)} changed by {by}; approval dropped").strip(" |")
    r["changed_by"], r["updated_at"] = by, stamp(ctx)


def parse_kv(items):
    out = {}
    for it in items:
        if "=" not in it:
            raise SystemExit(f"expected key=value, got {it!r}")
        k, v = it.split("=", 1)
        out[k.strip()] = v
    return out


# ---------- the gates ----------

def copy_check_script(ctx):
    for p in (ctx.project / "scripts" / "copy_check.py", HERE.parent.parent / "scripts" / "copy_check.py"):
        if p.exists():
            return p
    return None


def copy_ok(ctx, text):
    """(ok, message). Em dashes fail here even with no copy_check.py; copy_check.py runs when it is installed."""
    if "\u2014" in text:
        return False, "em dash in the caption"
    script = copy_check_script(ctx)
    if not script:
        return True, "copy_check.py not found; only the em dash was checked"
    fd, tmp = tempfile.mkstemp(suffix=".txt")
    with os.fdopen(fd, "w") as f:
        f.write(text)
    try:
        r = subprocess.run([sys.executable, str(script), tmp], capture_output=True, text=True, timeout=60,
                           env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    finally:
        os.unlink(tmp)
    lines = [x for x in (r.stdout + r.stderr).splitlines() if x.strip()]
    return r.returncode == 0, (lines[1] if len(lines) > 1 else (lines[0] if lines else ""))


def probe(path):
    """(width, height, seconds) through ffprobe, or None when ffprobe is missing or cannot read the file."""
    if not shutil.which("ffprobe"):
        return None
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:format=duration",
                        "-of", "json", str(path)], capture_output=True, text=True, timeout=60)
    try:
        d = json.loads(r.stdout)
        s = d["streams"][0]
        return int(s["width"]), int(s["height"]), float(d["format"]["duration"])
    except Exception:
        return None


TS_LINE = re.compile(r"^\s*\(?((?:\d{1,2}:)?\d{1,2}:\d{2})\)?\s+\S")


def first_chapter(desc):
    """The first timestamp of the first run of 2 or more timestamp lines in a row, or None."""
    run = []
    for line in (desc or "").splitlines():
        m = TS_LINE.match(line)
        if m:
            run.append(m.group(1))
            continue
        if len(run) >= 2:
            break
        run = []
    return run[0] if len(run) >= 2 else None


def check_rows(ctx, rows, quiet=False):
    lim = ctx.cfg.get("limits", {})
    probe_on = ctx.cfg.get("probe_video", True)
    problems, warned = [], set()
    for r in rows:
        if r["status"] in ("empty", "skipped"):
            continue
        p = []
        if r["kind"] in VIDEO_KINDS:
            if not r["file"]:
                p.append("no file")
            elif not Path(r["file"]).exists():
                p.append("file missing on disk")
            else:
                if r["file_sha256"] and sha(r["file"]) != r["file_sha256"]:
                    p.append("file changed since it was set (hash differs)")
                dims = probe(r["file"]) if probe_on else None
                if probe_on and dims is None:
                    if shutil.which("ffprobe"):
                        p.append("video could not be read by ffprobe")
                    elif "ffprobe" not in warned:
                        warned.add("ffprobe")
                        print("WARN ffprobe not installed: video size and length are not checked")
                elif dims:
                    w, h, dur = dims
                    if r["kind"] in ("youtube_short", "instagram_reel", "tiktok_video") and not h > w:
                        p.append(f"not vertical ({w}x{h})")
                    if r["kind"] == "youtube_short" and dur > int(lim.get("youtube_short_max_s", 180)):
                        p.append(f"{dur:.0f} s is over the Short limit in your config")
        if r["thumb"] and not Path(r["thumb"]).exists():
            p.append("thumbnail missing on disk")
        if r["kind"] == "youtube_long" and not r["thumb"]:
            p.append("long form has no thumbnail")
        if r["kind"] == "linkedin_video" and not r["thumb"] and lim.get("linkedin_video_needs_thumbnail", True):
            p.append("LinkedIn video has no thumbnail (it cannot be added after the post is live)")
        if r["platform"] == "youtube" and not r["title"]:
            p.append("no title")
        if r["kind"] == "substack_post" and not r["title"]:
            p.append("no title")
        if r["kind"] == "youtube_long":
            first = first_chapter(r.get("description") or r["caption"])
            if first and first not in ("0:00", "00:00"):
                p.append(f"chapters start at {first}, not 0:00 (YouTube then draws none)")
        if not r["caption"] and r["kind"] != "youtube_long":
            p.append("no caption")
        text = "\n".join(x for x in (r["caption"], r.get("description", ""), r["first_comment"]) if x)
        if re.search(r"PLACEHOLDER|\bTBD\b|\[[A-Z ]{3,}\]", text):
            p.append("words still carry a placeholder")
        if text:
            ok, msg = copy_ok(ctx, text)
            if not ok:
                p.append("fails copy_check: " + msg[:120])
            elif msg.startswith("copy_check.py not found") and "copy" not in warned:
                warned.add("copy")
                print("WARN " + msg)
        if r["platform"] == "linkedin" and len(r["caption"]) > int(lim.get("linkedin_caption_max", 3000)):
            p.append("LinkedIn text over the limit in your config")
        if r["platform"] == "instagram" and len(r["caption"]) > int(lim.get("instagram_caption_max", 2200)):
            p.append("Instagram caption over the limit in your config")
        if r["platform"] == "instagram" and r["caption"].count("#") > int(lim.get("instagram_hashtags_max", 5)):
            p.append("too many hashtags for Instagram")
        if r["platform"] == "linkedin" and "http" in r["caption"] and "http" in r["first_comment"]:
            p.append("link in both the body and the first comment")
        if r["status"] == "approved" and not r["approved_by"]:
            p.append("approved with no approved_by")
        problems.extend((r["id"], x) for x in p)
    per_day, per_minute = {}, {}
    for r in rows:
        if r["status"] in OUT_OF_SLOT:
            continue
        per_day.setdefault((r["date"], r["kind"]), []).append(r["id"])
        per_minute.setdefault((r["platform"], r["slot"][:16]), []).append(r["id"])
    for (d, kind), ids in sorted(per_day.items()):
        cap = int((ctx.slots.get(kind) or {}).get("max_per_day", 1))
        if len(ids) > cap:
            problems.extend((i, f"{len(ids)} {kind} legs on {d}; your config allows {cap} a day") for i in ids)
    for (plat, minute), ids in sorted(per_minute.items()):
        if len(ids) > 1:
            problems.extend((i, f"{len(ids)} {plat} legs at {minute}; move one") for i in ids)
    if not quiet:
        for lid, x in problems:
            print(f"FAIL {lid}: {x}")
    return problems


def links_pending(rows):
    """Short-form legs with a piece and no https link in first_comment yet. None of them is held for it."""
    return [r for r in rows if r["kind"] in SHORT_KINDS and r.get("piece") and r["status"] not in ("empty", "skipped")
            and "https://" not in (r.get("first_comment") or "")]


def add_link(ctx, r, text, by):
    """The full-video link onto a leg that has none, posted or not. Approval kept: the link is not the creator's words
    about the piece, and the short never waits for it."""
    if "https://" not in text:
        raise SystemExit("the text carries no https:// link")
    if "https://" in (r.get("first_comment") or "") or r.get("comment_id"):
        raise SystemExit(f"{r['id']} already carries a link or a comment")
    r["first_comment"] = text.strip()
    r["notes"] = (r.get("notes", "") + f" | full-video link added {stamp(ctx)} by {by}").strip(" |")
    r["changed_by"], r["updated_at"] = by, stamp(ctx)


# ---------- approval ----------

def approve(ctx, rows, picked, by):
    if not by or not by.strip():
        raise SystemExit("approve needs --by with a person's name; nothing is approved without one")
    bad = {lid for lid, _ in check_rows(ctx, picked, quiet=True)}
    done, refused = [], []
    for r in picked:
        if r["status"] not in ("draft", "failed"):
            continue
        if r["id"] in bad:
            refused.append(r["id"])
            continue
        if r["file"]:
            r["file_sha256"] = sha(r["file"])
        r.update(approved_by=by.strip(), approved_at=stamp(ctx), status="approved", changed_by=by.strip(), attempts=0, last_error="")
        done.append(r)
    return done, refused


# ---------- missed legs ----------

def week_slot(ctx, rows, leg, from_dt, at):
    """The soonest open slot of the leg's kind in the Monday-to-Sunday week of from_dt, at least 15 minutes after now.
    A day is open while its live legs of the kind are under max_per_day; the time is the slot time, else
    second_offset_h after it, else before it. On a kind allowing 2 or more a day, an empty leg's time counts as held,
    so the empty leg stays for the night to fill."""
    spec = ctx.slots.get(leg["kind"])
    if not spec:
        return None
    cap = int(spec.get("max_per_day", 1))
    gap = timedelta(hours=float(spec.get("second_offset_h", 3)))
    hh, mm = (int(x) for x in spec["time"].split(":"))
    end = week_of(from_dt.date()) + timedelta(days=6)
    d = max(from_dt.date(), at.date())
    while d <= end:
        if DOW[d.weekday()] in spec.get("days", []):
            same = [r for r in rows if r["id"] != leg["id"] and r["date"] == d.isoformat() and r["kind"] == leg["kind"]]
            live = [r for r in same if r["status"] not in OUT_OF_SLOT]
            if len(live) < cap:
                held = {r["slot"][:16] for r in live}
                if cap > 1:
                    held |= {r["slot"][:16] for r in same if r["status"] == "empty"}
                base = datetime(d.year, d.month, d.day, hh, mm, tzinfo=ctx.tz)
                for t in (base, base + gap, base - gap):
                    if t.date() == d and t > at + timedelta(minutes=15) and t.isoformat()[:16] not in held:
                        return t
        d += timedelta(days=1)
    return None


def reslot_missed(ctx, rows, dry=False):
    """Move every missed leg by the rules. Returns [(leg id, from, to, rule, skipped ids)]."""
    at = ctx.now()
    moved = []
    for leg in sorted(rows, key=lambda r: r["slot"]):
        if leg["status"] not in ("approved", "hand") or leg.get("review") == "hold" or leg.get("post_id") or leg.get("post_url"):
            continue
        slot = slot_dt(ctx, leg).astimezone(ctx.tz)
        hand = ctx.is_hand(leg)
        if hand:
            if at.date() <= slot.date():          # a hand leg stays open, postable, until its slot's own day ends
                continue
        elif slot > at - timedelta(hours=ctx.stale_hours):
            continue
        new, rule, probe_dt = week_slot(ctx, rows, leg, slot, at), "same-week", slot
        for _ in range(3):
            if new:
                break
            probe_dt = datetime.combine(week_of(probe_dt.date()) + timedelta(days=7), probe_dt.timetz())
            new, rule = week_slot(ctx, rows, leg, probe_dt, at), "next-week"
        if not new:
            if not dry and not logged_today(ctx, "stale-unmoved", leg["id"]):
                log(ctx, leg["id"], "stale-unmoved", reason="no open slot of its kind this week or the 3 after", by="watch")
            continue
        why = "a hand leg whose day ended unposted" if hand else f"a machine leg {ctx.stale_hours:g} h past its slot"
        skipped = []
        if not dry:
            old = leg["slot"]
            leg.update(slot=new.isoformat(), date=new.date().isoformat(), attempts=0, changed_by="watch", updated_at=stamp(ctx))
            leg["notes"] = (leg.get("notes", "") + f" | moved {old[:16]} to {new.isoformat()[:16]} ({rule}: {why})").strip(" |")
            cap = int(ctx.slots[leg["kind"]].get("max_per_day", 1))
            live = [r for r in rows if r["id"] != leg["id"] and r["date"] == leg["date"] and r["kind"] == leg["kind"] and r["status"] not in OUT_OF_SLOT]
            for r in rows:
                if r["id"] != leg["id"] and r["date"] == leg["date"] and r["kind"] == leg["kind"] and r["status"] == "empty":
                    if len(live) + 1 >= cap or r["slot"][:16] == leg["slot"][:16]:
                        r.update(status="skipped", changed_by="watch", updated_at=stamp(ctx))
                        r["notes"] = (r.get("notes", "") + f" | slot given to {leg['id']}").strip(" |")
                        skipped.append(r["id"])
            log(ctx, leg["id"], "re-slot", rule=rule, hand=hand, skipped=skipped, by="watch", **{"from": old, "to": leg["slot"]})
        moved.append((leg["id"], slot.isoformat()[:16], new.isoformat()[:16], rule, skipped))
    return moved


# ---------- commands ----------

def pick(rows, a):
    if getattr(a, "all", False):
        return rows
    wk = a.week or week_of(date.today()).isoformat()
    return [r for r in rows if leg_week(r) == week_of(date.fromisoformat(wk)).isoformat()]


def cmd_skeleton(a):
    ctx = ctx_from(a)
    rows = load(ctx)
    floor = len(rows)
    start = date.fromisoformat(a.start)
    added, taken = build_skeleton(ctx, rows, start)
    save(ctx, rows, floor)
    print(f"skeleton: {len(added)} empty legs for the week of {week_of(start)} ({len(rows)} legs in the plan)")
    for lid, holder in taken:
        print(f"  no {lid}: {holder} already holds that day")


def cmd_next_week(a):
    ctx = ctx_from(a)
    today = ctx.now().date()
    a.start = (today + timedelta(days=7 - today.weekday())).isoformat()
    cmd_skeleton(a)
    a.week, a.all = a.start, False
    n = len(check_rows(ctx, pick(load(ctx), a)))
    print(f"check: {n} problem(s). Fill the legs from your bench, then approve the week with every caption read.")


def cmd_add(a):
    ctx = ctx_from(a)
    if a.kind not in KINDS:
        raise SystemExit(f"kind must be one of {', '.join(KINDS)}")
    rows = load(ctx)
    floor = len(rows)
    day = date.fromisoformat(a.date)
    t = a.time or (ctx.slots.get(a.kind) or {}).get("time", "12:00")
    hh, mm = (int(x) for x in t.split(":"))
    lid = leg_id(rows, day, a.kind)
    rows.append(new_leg(ctx, lid, day, a.kind, datetime(day.year, day.month, day.day, hh, mm, tzinfo=ctx.tz), a.by))
    save(ctx, rows, floor)
    print(f"added {lid}")


def cmd_list(a):
    ctx = ctx_from(a)
    rows = sorted(pick(load(ctx), a), key=lambda r: r["slot"])
    for r in rows:
        flag = " LOCKED:" + ",".join(r["locked"]) if r.get("locked") else ""
        print(f"{r['slot'][:16].replace('T', ' ')}  {r['kind']:<17} {r['status']:<9} {r['id']:<34} {r.get('piece') or '-'}{flag}")
    print(f"{len(rows)} legs")


def cmd_show(a):
    ctx = ctx_from(a)
    print(json.dumps(find(load(ctx), a.leg), indent=2, ensure_ascii=False))


def cmd_set(a):
    ctx = ctx_from(a)
    rows = load(ctx)
    r = find(rows, a.leg)
    apply_fields(ctx, r, parse_kv(a.fields), a.by)
    save(ctx, rows, len(rows))
    print(f"{r['id']}: {', '.join(parse_kv(a.fields))} set by {a.by}; status {r['status']}")


def cmd_lock(a):
    ctx = ctx_from(a)
    rows = load(ctx)
    r = find(rows, a.leg)
    r["locked"] = sorted(set(r.get("locked", [])) | set(a.fields))
    r["changed_by"], r["updated_at"] = a.by, stamp(ctx)
    save(ctx, rows, len(rows))
    print(f"{r['id']}: locked {', '.join(r['locked'])}")


def cmd_check(a):
    ctx = ctx_from(a)
    rows = pick(load(ctx), a)
    problems = check_rows(ctx, rows)
    for r in links_pending(rows):
        print(f"LINK {r['id']}: owes its full-video link (not a hold; add-link once the full video is live)")
    print(f"{len(problems)} problem(s) in {len(rows)} legs")
    sys.exit(1 if problems else 0)


def cmd_approve(a):
    ctx = ctx_from(a)
    rows = load(ctx)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.target):
        d = date.fromisoformat(a.target)
        picked = [r for r in rows if (leg_week(r) == week_of(d).isoformat() if a.week else r["date"] == a.target)]
    else:
        picked = [find(rows, a.target)]
    done, refused = approve(ctx, rows, picked, a.by)
    save(ctx, rows, len(rows))
    for r in done:
        print(f"\nAPPROVED {r['id']} ({r['platform']}, {r['slot'][:16].replace('T', ' ')}) by {r['approved_by']}")
        for k in ("title", "caption", "description", "first_comment"):
            if r.get(k):
                print(f"  {k}:\n    " + r[k].replace("\n", "\n    "))
    if refused:
        print(f"\nNOT approved, failing a gate: {', '.join(refused)} (plan.py check shows why)")
    print(f"\n{len(done)} leg(s) approved by {a.by.strip() if a.by else ''}")


def cmd_links_pending(a):
    ctx = ctx_from(a)
    legs = links_pending(load(ctx))
    for r in legs:
        print(f"{r['id']}  {r['status']}  {r['piece']}")
    print(f"{len(legs)} leg(s) owe their full-video link; none is held for it. Once the long form is live: plan.py add-link <leg> '<text with the https link>'")


def cmd_add_link(a):
    ctx = ctx_from(a)
    if "https://" not in a.text:
        raise SystemExit("the text carries no https:// link")
    rows = load(ctx)
    r = find(rows, a.leg)
    add_link(ctx, r, a.text, a.by)
    save(ctx, rows, len(rows))
    print(f"{r['id']}: link added, approval kept (status {r['status']})" + ("; the runner comments it on its next tick" if r["status"] == "posted" else ""))


def post_id_from_url(platform, url):
    """The platform's post id out of a post URL, where the URL carries it (YouTube, LinkedIn), else ""."""
    if platform == "youtube":
        m = re.search(r"(?:youtu\.be/|v=|/shorts/|/live/)([A-Za-z0-9_-]{11})", url)
        return m.group(1) if m else ""
    if platform == "linkedin":
        m = re.search(r"urn:li:(?:ugcPost|share|activity):\d+", unquote(url))
        return m.group(0) if m else ""
    return ""


def record_hand_post(ctx, r, url, by):
    """A post the creator made by hand. On a platform the runner can read (YouTube, LinkedIn), the leg waits as
    `uploaded` with posted_by_hand until the runner reads it on the channel; a hand board that only the machine's own
    posts can update is wrong every time a person posts. On a hand platform (TikTok, Substack) or where the URL
    carries no id, the creator's word with the URL is the record."""
    if not by.strip() or not url.startswith("https://"):
        raise SystemExit("posted needs --by with a name and --url starting https://")
    pid = "" if ctx.is_hand(r) else post_id_from_url(r["platform"], url)
    if pid:
        r.update(status="uploaded", post_id=pid, post_url=url, posted_by_hand=True)
        note = f"posted by hand, recorded by {by}; marked posted once the runner reads it on the channel"
    else:
        r.update(status="posted", post_url=url)
        note = f"posted by hand, recorded on {by}'s word"
    r["notes"] = (r.get("notes", "") + " | " + note).strip(" |")
    r["changed_by"], r["updated_at"] = by, stamp(ctx)
    log(ctx, r["id"], "posted-by-hand", url=url, by=by, waiting_for_read_back=bool(pid))
    return bool(pid)


def cmd_posted(a):
    ctx = ctx_from(a)
    rows = load(ctx)
    r = find(rows, a.leg)
    waits = record_hand_post(ctx, r, a.url, a.by)
    save(ctx, rows, len(rows))
    print(f"{r['id']}: " + ("recorded; the runner's next live tick reads it on the channel and marks it posted" if waits
                             else f"recorded as posted by hand, {a.url}"))


def cmd_reslot(a):
    ctx = ctx_from(a)
    rows = load(ctx)
    moved = reslot_missed(ctx, rows, dry=a.dry_run)
    if moved and not a.dry_run:
        save(ctx, rows, len(rows))
    for lid, frm, to, rule, skipped in moved:
        print(f"{'WOULD MOVE' if a.dry_run else 'moved'} {lid}: {frm} -> {to} ({rule})" + (f", {', '.join(skipped)} skipped" if skipped else ""))
    print(f"{len(moved)} leg(s) {'would move' if a.dry_run else 'moved'}")


# ---------- self-test ----------

SELFTEST_CONFIG = {
    "timezone": "America/New_York", "stale_hours": 6, "probe_video": False, "hand_platforms": ["tiktok", "substack"],
    "slots": {
        "linkedin_video": {"days": ["Mon", "Wed", "Fri"], "time": "12:00", "max_per_day": 1},
        "youtube_short": {"days": DOW, "time": "14:00", "max_per_day": 1},
        "instagram_reel": {"days": DOW, "time": "16:00", "max_per_day": 2, "second_offset_h": 3},
        "tiktok_video": {"days": DOW, "time": "19:00", "max_per_day": 1},
        "youtube_long": {"days": ["Sat"], "time": "10:00", "max_per_day": 1},
    },
    "adapters": {p: {"route": "fake", "account_id": "fake-creator", "expected_account_id": "fake-creator"} for p in ("youtube", "linkedin", "instagram")},
}


def make_test_project(base, config=None):
    """A throwaway project under `base`: config, a 2-file media folder. Returns (Ctx, media dir)."""
    proj = Path(tempfile.mkdtemp(prefix="posting-selftest-", dir=base))
    (proj / "content" / "posting").mkdir(parents=True)
    (proj / "content" / "posting" / "config.json").write_text(json.dumps(config or SELFTEST_CONFIG))
    media = proj / "media"
    media.mkdir()
    (media / "clip.mp4").write_bytes(b"fake video bytes")
    (media / "thumb.jpg").write_bytes(b"fake thumb bytes")
    return Ctx(proj), media


def run_selftest(base):
    fails = []

    def check(label, ok):
        print(("  ok    " if ok else "  FAIL  ") + label)
        if not ok:
            fails.append(label)

    def raises(fn):
        try:
            fn()
        except SystemExit:
            return True
        return False

    ctx, media = make_test_project(base)
    ctx.set_clock("2026-11-09T08:00")        # a Monday
    rows = []
    added, _ = build_skeleton(ctx, rows, date(2026, 11, 9))
    check("skeleton lays 25 legs (3 LinkedIn videos, 7 Shorts, 7 Reels, 7 TikToks, 1 long form)", len(added) == 25)
    again, _ = build_skeleton(ctx, rows, date(2026, 11, 9))
    check("a second skeleton on the same week adds nothing", again == [])
    save(ctx, rows, 0)
    check("refuses to write fewer legs than it read", raises(lambda: save(ctx, rows[:3], len(rows))))

    li = find(rows, "2026-11-09-linkedin-video")
    apply_fields(ctx, li, {"file": str(media / "clip.mp4"), "thumb": str(media / "thumb.jpg"), "caption": "A plain caption about the week.", "piece": "ep1"}, "You")
    check("filling a leg makes it a draft and records the file hash", li["status"] == "draft" and len(li["file_sha256"]) == 64)
    check("approve refuses an empty name", raises(lambda: approve(ctx, rows, [li], "  ")))
    check("set can never write approved_by", raises(lambda: apply_fields(ctx, li, {"approved_by": "Someone"}, "You")))
    check("set can never write status=approved", raises(lambda: apply_fields(ctx, li, {"status": "approved"}, "You")))
    done, _ = approve(ctx, rows, [li], "Creator A, 2026-11-08, in session")
    check("approve with a name approves", li["status"] == "approved" and li["approved_by"].startswith("Creator A"))
    apply_fields(ctx, li, {"caption": "A different caption."}, "You")
    check("changed words drop the approval", li["status"] == "draft" and not li["approved_by"])
    approve(ctx, rows, [li], "Creator A")
    (media / "clip2.mp4").write_bytes(b"other bytes")
    apply_fields(ctx, li, {"file": str(media / "clip2.mp4")}, "You")
    check("a changed file drops the approval", li["status"] == "draft" and not li["approved_by"])
    li["locked"] = ["caption"]
    check("the night cannot change a locked field", raises(lambda: apply_fields(ctx, li, {"caption": "night words"}, "night")))
    apply_fields(ctx, li, {"title": "A title"}, "night")
    check("the night can change an unlocked field", li["title"] == "A title")

    bad = find(rows, "2026-11-10-youtube-short")
    apply_fields(ctx, bad, {"file": str(media / "clip.mp4"), "title": "T", "caption": "Dash \u2014 here"}, "You")
    check("an em dash fails the check", any("copy_check" in x for i, x in check_rows(ctx, [bad], quiet=True)))
    apply_fields(ctx, bad, {"caption": "Link at PLACEHOLDER"}, "You")
    check("a placeholder fails the check", any("placeholder" in x for i, x in check_rows(ctx, [bad], quiet=True)))
    _, refused = approve(ctx, rows, [bad], "Creator A")
    check("approve refuses a leg failing a gate", refused == [bad["id"]] and bad["status"] == "draft")
    apply_fields(ctx, li, {"first_comment": "Full video: https://example.com/v"}, "You")
    apply_fields(ctx, li, {"caption": "Read more at https://example.com/a"}, "Creator A")
    check("a LinkedIn link in both body and comment fails", any("both" in x for i, x in check_rows(ctx, [li], quiet=True)))
    nolong = find(rows, "2026-11-14-youtube-long")
    apply_fields(ctx, nolong, {"file": str(media / "clip.mp4"), "title": "Long", "thumb": str(media / "thumb.jpg"),
                               "description": "Intro\n0:31 Start\n2:00 Middle"}, "You")
    check("long-form chapters not starting at 0:00 fail", any("0:00" in x for i, x in check_rows(ctx, [nolong], quiet=True)))
    apply_fields(ctx, nolong, {"description": "0:00 Start\n2:00 Middle"}, "You")
    check("chapters from 0:00 pass", not any("0:00" in x for i, x in check_rows(ctx, [nolong], quiet=True)))

    reel = find(rows, "2026-11-09-instagram-reel")
    apply_fields(ctx, reel, {"file": str(media / "clip.mp4"), "caption": "A reel.", "piece": "ep1"}, "You")
    check("links-pending lists a short with no full-video link", reel["id"] in [r["id"] for r in links_pending(rows)])
    approve(ctx, rows, [reel], "Creator A")
    add_link(ctx, reel, "Full video: https://example.com/v", "You")
    check("add-link refuses a second link", raises(lambda: add_link(ctx, reel, "https://example.com/w", "You")))
    check("add-link clears links-pending and keeps the approval",
          reel["id"] not in [r["id"] for r in links_pending(rows)] and reel["status"] == "approved")
    save(ctx, rows, 0)

    # missed legs
    ctx.set_clock("2026-11-09T23:30")       # Monday night: the 16:00 Reel is 7.5 h late
    rows = load(ctx)
    moved = reslot_missed(ctx, rows)
    reel = find(rows, "2026-11-09-instagram-reel")
    check("a missed Reel moves to the soonest open slot that week (Tue 16:00 is an empty leg, so 19:00 on a 2-a-day kind)",
          moved and reel["slot"].startswith("2026-11-10T19:00"))
    check("the empty Reel leg on the new day is kept for the night", find(rows, "2026-11-10-instagram-reel")["status"] == "empty")
    tk = find(rows, "2026-11-09-tiktok-video")
    apply_fields(ctx, tk, {"file": str(media / "clip.mp4"), "caption": "A TikTok."}, "You")
    approve(ctx, rows, [tk], "Creator A")
    tk["status"] = "hand"
    reslot_missed(ctx, rows)
    check("a hand leg stays in its slot until its day ends", tk["slot"].startswith("2026-11-09T19:00"))
    ctx.set_clock("2026-11-10T00:10")
    reslot_missed(ctx, rows)
    check("after midnight the hand leg moves to the next open day, still hand", tk["slot"].startswith("2026-11-10T19:00") and tk["status"] == "hand")
    check("the empty TikTok leg it landed on is skipped", find(rows, "2026-11-10-tiktok-video")["status"] == "skipped")
    lv = find(rows, "2026-11-14-youtube-long")
    approve(ctx, rows, [lv], "Creator A")
    ctx.set_clock("2026-11-14T18:00")
    reslot_missed(ctx, rows)
    check("a missed weekly long form with no room this week goes to next week", lv["slot"].startswith("2026-11-21T10:00"))
    save(ctx, rows, 0)
    print(f"plan selftest: {len(fails)} failed" if fails else "plan selftest: all pass")
    return not fails


# ---------- main ----------

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project")
    ap.add_argument("--config")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--tmp", help="where the self-test makes its throwaway project (default: the system temp folder)")
    sub = ap.add_subparsers(dest="cmd")

    def p(name, fn, **kw):
        s = sub.add_parser(name, **kw)
        s.set_defaults(fn=fn)
        return s
    s = p("skeleton", cmd_skeleton); s.add_argument("--start", required=True)
    s = p("next-week", cmd_next_week); s.add_argument("--at")
    s = p("add", cmd_add); s.add_argument("date"); s.add_argument("kind"); s.add_argument("--time"); s.add_argument("--by", default="session")
    for name in ("list", "check"):
        s = p(name, cmd_list if name == "list" else cmd_check); s.add_argument("--week"); s.add_argument("--all", action="store_true")
    s = p("show", cmd_show); s.add_argument("leg")
    s = p("set", cmd_set); s.add_argument("leg"); s.add_argument("fields", nargs="+"); s.add_argument("--by", default="session")
    s = p("lock", cmd_lock); s.add_argument("leg"); s.add_argument("fields", nargs="+"); s.add_argument("--by", default="session")
    s = p("approve", cmd_approve); s.add_argument("target"); s.add_argument("--by", required=True); s.add_argument("--week", action="store_true")
    s = p("links-pending", cmd_links_pending)
    s = p("add-link", cmd_add_link); s.add_argument("leg"); s.add_argument("text"); s.add_argument("--by", default="session")
    s = p("posted", cmd_posted); s.add_argument("leg"); s.add_argument("--url", required=True); s.add_argument("--by", required=True)
    s = p("reslot-missed", cmd_reslot); s.add_argument("--at"); s.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if run_selftest(a.tmp) else 1)
    if not a.cmd:
        ap.print_help()
        sys.exit(2)
    a.fn(a)


if __name__ == "__main__":
    main()
