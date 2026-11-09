#!/usr/bin/env python3
"""The watcher: what a cron or launchd tick runs next to the runner. It NEVER posts.

    python3 posting/scripts/watch.py tick [--dry-run] [--at 2026-11-09T18:05]   # all 3 steps below
    python3 posting/scripts/watch.py status                                      # today's hand legs and today's moves
    python3 posting/scripts/watch.py --selftest                                  # offline, a throwaway project

Each tick:
1. Moves missed legs (plan.py reslot-missed): a machine leg more than stale_hours past its slot goes to the soonest
   open slot of its kind that Monday-to-Sunday week, else next week; a hand leg stays open until its slot's day ends,
   then moves by the same rule. Words, locks and approval are kept; every move is a `re-slot` line in the log.
2. Writes hand cards: for each APPROVED leg on a hand platform (TikTok, Substack, anything in hand_platforms) whose day
   has come (from hand_card_hour, 07:00 by default), content/posting/hand-cards/<date>-<platform>.md with the file
   path, the caption in full, the first comment and how to record the post. Once per leg; the leg becomes `hand`.
3. Warns once a day about a filled leg still not approved within approval_warn_hours (3) of its slot, in the plan
   copy the runner reads: an approval made where the runner cannot see it is caught before the slot passes.
4. Reminds you, if the config names a reminder_command (a desktop notification, a chat message to yourself):
   once reminder_lead_min before a hand leg's slot and once at the slot, while it is still not recorded as posted.
"""
import sys
sys.dont_write_bytecode = True

import argparse, subprocess
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import plan as pp            # noqa: E402

WORD = {"tiktok": "TikTok", "substack": "Substack", "youtube": "YouTube", "linkedin": "LinkedIn", "instagram": "Instagram"}


def card_path(ctx, leg):
    base = ctx.cards / f"{leg['date']}-{leg['platform']}.md"
    n = 2
    while base.exists() and f"Leg: {leg['id']}\n" not in base.read_text():
        base = ctx.cards / f"{leg['date']}-{leg['platform']}-{n}.md"
        n += 1
    return base


def card_text(ctx, leg):
    slot = pp.slot_dt(ctx, leg)
    word = WORD.get(leg["platform"], leg["platform"])
    lines = [f"# Post by hand: {word}, {slot.strftime('%a %d %b %H:%M')}", "",
             f"Leg: {leg['id']}", f"Approved by: {leg['approved_by']}"]
    if leg.get("file"):
        lines.append(f"File: {leg['file']}")
    if leg.get("thumb"):
        lines.append(f"Cover picture: {leg['thumb']}")
    if leg.get("title"):
        lines += ["", "## Title", "", "```", leg["title"], "```"]
    lines += ["", "## Caption (copy all of it, exactly as approved)", "", "```", leg.get("caption", ""), "```", ""]
    if "https://" in (leg.get("first_comment") or ""):
        lines += ["## First comment (post it right after the post goes up)", "", "```", leg["first_comment"], "```", ""]
    else:
        lines += ["## First comment", "", "No full-video link yet. Post anyway: the short goes first. When the long form is",
                  f"live, add it with: python3 posting/scripts/plan.py add-link {leg['id']} 'Full video: https://...'", ""]
    lines += ["## When it is up", "", "Tell Claude the post's link, or run:", "",
              f"    python3 posting/scripts/plan.py posted {leg['id']} --url https://... --by \"Your name\"", "",
              f"Until then it stays open in its slot until midnight of {slot.strftime('%a %d %b')}. If the day ends",
              "unposted, the watcher moves it to the next open slot of its kind and keeps its words.", ""]
    return "\n".join(lines)


def step_cards(ctx, rows, dry):
    at = ctx.now()
    hour = int(ctx.cfg.get("hand_card_hour", 7))
    written = []
    for leg in rows:
        if not ctx.is_hand(leg) or leg["status"] not in ("approved", "hand") or not leg.get("approved_by", "").strip():
            continue
        if leg.get("post_url") or "hand card " in (leg.get("notes") or ""):
            continue
        if leg["date"] > at.date().isoformat() or at.hour < hour:
            continue
        dst = card_path(ctx, leg)
        if dry:
            written.append((leg["id"], f"WOULD WRITE {dst}"))
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(card_text(ctx, leg))
        leg["status"] = "hand"
        leg["notes"] = (leg.get("notes", "") + f" | hand card {dst}").strip(" |")
        leg["changed_by"], leg["updated_at"] = "watch", pp.stamp(ctx)
        pp.log(ctx, leg["id"], "hand-card", file=str(dst), by="watch")
        written.append((leg["id"], str(dst)))
    return written


def remind(ctx, text):
    cmd = ctx.cfg.get("reminder_command") or []
    if not cmd:
        return False
    safe = text.replace('"', "'").replace("\\", "/")
    try:
        r = subprocess.run([c.replace("{text}", safe) for c in cmd], capture_output=True, text=True, timeout=30)
        return r.returncode == 0
    except Exception:
        return False


def step_reminders(ctx, rows, dry):
    if not ctx.cfg.get("reminder_command"):
        return []
    at = ctx.now()
    lead = timedelta(minutes=int(ctx.cfg.get("reminder_lead_min", 60)))
    sent = []
    for leg in rows:
        if leg["status"] != "hand" or leg.get("post_url") or leg["date"] != at.date().isoformat():
            continue
        slot = pp.slot_dt(ctx, leg)
        word = WORD.get(leg["platform"], leg["platform"])
        card = (leg.get("notes") or "").rsplit("hand card ", 1)[-1].split(" |")[0]
        for event, when, text in (("reminder", slot - lead, f"{word} post due at {slot.strftime('%H:%M')}: {card}"),
                                  ("reminder-again", slot, f"{word} post is due now: {card}")):
            if at >= when and not pp.logged_today(ctx, event, leg["id"]):
                if dry:
                    sent.append((leg["id"], f"WOULD REMIND: {text}"))
                    continue
                ok = remind(ctx, text)
                pp.log(ctx, leg["id"], event, ok=ok, by="watch")
                sent.append((leg["id"], text))
                break
    return sent


def step_unapproved(ctx, rows, dry):
    """A filled leg still not approved within approval_warn_hours of its slot, in the plan copy the runner reads: say
    so once a day. An approval made somewhere the runner cannot read (another computer, a copy that stopped syncing)
    shows up here, before the slot passes unposted."""
    at = ctx.now()
    ahead = timedelta(hours=float(ctx.cfg.get("approval_warn_hours", 3)))
    out = []
    for leg in rows:
        if leg["status"] != "draft":
            continue
        slot = pp.slot_dt(ctx, leg)
        if not at < slot <= at + ahead or pp.logged_today(ctx, "not-approved", leg["id"]):
            continue
        text = f"{WORD.get(leg['platform'], leg['platform'])} post at {slot.strftime('%H:%M')} is not approved in the plan the runner reads: {leg['id']}"
        if dry:
            out.append((leg["id"], "WOULD WARN: " + text))
            continue
        pp.log(ctx, leg["id"], "not-approved", plan=str(ctx.plan), by="watch")
        remind(ctx, text)
        out.append((leg["id"], text))
    return out


def tick(ctx, dry=False):
    rows = pp.load(ctx)
    floor = len(rows)
    moved = pp.reslot_missed(ctx, rows, dry=dry)
    cards = step_cards(ctx, rows, dry)
    if not dry and (moved or cards):
        pp.save(ctx, rows, floor)
    reminders = step_reminders(ctx, rows, dry) + step_unapproved(ctx, rows, dry)
    return moved, cards, reminders


def cmd_tick(a):
    ctx = pp.ctx_from(a)
    moved, cards, reminders = tick(ctx, a.dry_run)
    for lid, frm, to, rule, skipped in moved:
        print(f"{'WOULD MOVE' if a.dry_run else 'moved'} {lid}: {frm} -> {to} ({rule})")
    for lid, what in cards + reminders:
        print(f"{lid} -> {what}")
    if not (moved or cards or reminders):
        print("nothing to do")


def cmd_status(a):
    ctx = pp.ctx_from(a)
    today = ctx.now().date().isoformat()
    for r in pp.load(ctx):
        if r["date"] == today and ctx.is_hand(r) and r["status"] not in ("empty", "skipped"):
            print(f"{r['slot'][11:16]}  {r['platform']:<9} {r['status']:<8} {r['id']}  {r.get('post_url') or 'not recorded as posted'}")
    if ctx.log.exists():
        for line in ctx.log.read_text().splitlines():
            if today in line and '"re-slot"' in line:
                print("moved today: " + line)


# ---------- self-test ----------

def run_selftest(base):
    from adapters import fake
    fails = []

    def check(label, ok):
        print(("  ok    " if ok else "  FAIL  ") + label)
        if not ok:
            fails.append(label)

    ctx, media = pp.make_test_project(base)
    out = media / "reminders.txt"
    ctx.cfg["reminder_command"] = [sys.executable, "-c", "import sys; open(sys.argv[1], 'a').write(sys.argv[2] + '\\n')", str(out), "{text}"]
    ctx.set_clock("2026-11-08T20:00")
    rows = []
    pp.build_skeleton(ctx, rows, datetime(2026, 11, 9).date())
    tk = pp.find(rows, "2026-11-09-tiktok-video")
    pp.apply_fields(ctx, tk, {"file": str(media / "clip.mp4"), "caption": "A TikTok caption.", "first_comment": "Full video: https://example.com/v"}, "test")
    pp.approve(ctx, rows, [tk], "Creator A, in session")
    tue = pp.find(rows, "2026-11-10-tiktok-video")
    pp.apply_fields(ctx, tue, {"file": str(media / "clip.mp4"), "caption": "Not approved yet."}, "test")
    pp.save(ctx, rows, 0)

    ctx.set_clock("2026-11-09T06:30")
    _, cards, _ = tick(ctx)
    check("no card before the card hour", cards == [])
    ctx.set_clock("2026-11-09T07:05")
    _, cards, _ = tick(ctx, dry=True)
    check("a dry tick writes no card", not ctx.cards.exists() and pp.find(pp.load(ctx), tk["id"])["status"] == "approved")
    _, cards, _ = tick(ctx)
    card = ctx.cards / "2026-11-09-tiktok.md"
    text = card.read_text() if card.exists() else ""
    check("the card is written at <date>-<platform>.md", card.exists())
    check("it carries the caption, the file path and the first comment",
          "A TikTok caption." in text and str(media / "clip.mp4") in text and "https://example.com/v" in text)
    check("the leg becomes hand", pp.find(pp.load(ctx), tk["id"])["status"] == "hand")
    tick(ctx)
    check("the card is written once", len(list(ctx.cards.iterdir())) == 1)

    ctx.set_clock("2026-11-09T18:05")
    tick(ctx)
    tick(ctx)
    n1 = len(out.read_text().splitlines()) if out.exists() else 0
    ctx.set_clock("2026-11-09T19:05")
    tick(ctx)
    tick(ctx)
    n2 = len(out.read_text().splitlines()) if out.exists() else 0
    check("one reminder an hour before the slot", n1 == 1)
    check("one more at the slot, and no more", n2 == 2)

    ctx.set_clock("2026-11-09T23:50")
    tick(ctx)
    check("the hand leg stays in its slot until its day ends", pp.find(pp.load(ctx), tk["id"])["slot"].startswith("2026-11-09T19:00"))
    ctx.set_clock("2026-11-10T00:10")
    moved, _, _ = tick(ctx)
    leg = pp.find(pp.load(ctx), tk["id"])
    check("after midnight it moves to the next open slot of its kind, still hand",
          leg["slot"].startswith("2026-11-11T19:00") and leg["status"] == "hand")
    check("the move is in the log", '"re-slot"' in ctx.log.read_text())
    ctx.set_clock("2026-11-10T07:30")
    tick(ctx)
    check("an unapproved hand leg gets no card", not (ctx.cards / "2026-11-10-tiktok.md").exists())
    check("the watcher never posts", fake.posts(ctx) == {})
    wed = pp.find(pp.load(ctx), "2026-11-12-tiktok-video")
    rows = pp.load(ctx)
    pp.apply_fields(ctx, pp.find(rows, wed["id"]), {"file": str(media / "clip.mp4"), "caption": "Thursday, not approved."}, "test")
    pp.save(ctx, rows, len(rows))
    ctx.set_clock("2026-11-12T16:30")
    _, _, warned = tick(ctx)
    tick(ctx)
    check("a filled leg not approved 3 h before its slot is warned about, once",
          [x for x, _ in warned] == [wed["id"]] and ctx.log.read_text().count('"not-approved"') == 1)
    print(f"watch selftest: {len(fails)} failed" if fails else "watch selftest: all pass")
    return not fails


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project")
    ap.add_argument("--config")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--tmp", help="where the self-test makes its throwaway project (default: the system temp folder)")
    sub = ap.add_subparsers(dest="cmd")
    s = sub.add_parser("tick"); s.add_argument("--dry-run", action="store_true"); s.add_argument("--at"); s.set_defaults(fn=cmd_tick)
    s = sub.add_parser("status"); s.add_argument("--at"); s.set_defaults(fn=cmd_status)
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if run_selftest(a.tmp) else 1)
    if not a.cmd:
        ap.print_help()
        sys.exit(2)
    a.fn(a)


if __name__ == "__main__":
    main()
