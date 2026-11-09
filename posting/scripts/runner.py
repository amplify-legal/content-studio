#!/usr/bin/env python3
"""The runner: posts the APPROVED legs of content/posting/plan.jsonl whose slot has come, through the platform adapters.

    python3 posting/scripts/runner.py tick                 # DRY RUN (the default): says what it would post, posts nothing
    python3 posting/scripts/runner.py tick --live          # posts for real
    python3 posting/scripts/runner.py tick --live --leg <id> --force   # one leg now, ignoring its slot (still needs approval)
    python3 posting/scripts/runner.py readback <leg>       # read one posted leg back from the platform
    python3 posting/scripts/runner.py whoami youtube       # which account the connection posts as (pin it in the config)
    python3 posting/scripts/runner.py status               # the next 12 legs and where each stands
    python3 posting/scripts/runner.py --selftest           # offline, the fake adapter on a throwaway project

Every decision is a line in content/posting/log.jsonl (dry runs too, once per leg per day), so a dry week reads back as
"this is what would have gone out, and when".

What it will never do:
- post a leg with no approved_by, a leg on hold, a leg that fails plan.py check, or a leg whose file changed since approval
- post a hand leg (TikTok, Substack, anything in hand_platforms): the watcher writes those as cards for your hand
- post a leg twice: the post id goes on the leg before anything else happens, and a leg with a post id is never uploaded
  again; a failed read-back retries the READ, never the upload
- post late: a machine leg more than stale_hours past its slot is left for the watcher to move
- comment twice: the full-video comment's id goes on the leg, at most 3 tries
- upload to an account that is not the creator's: before every upload it reads the connected account's own id
  (`whoami`) and refuses unless it equals adapters.<platform>.expected_account_id in the config
A video the creator uploaded by hand on a machine platform (`plan.py posted <leg> --url ...`) is marked posted only
when the runner reads it back from the channel, never from the record alone.
YouTube legs upload early as PRIVATE videos with publishAt set to the slot, so YouTube publishes them itself; the
runner then reads them back after the slot and marks them posted only on processing succeeded, a real duration and public.
"""
import sys
sys.dont_write_bytecode = True

import argparse, json, tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import plan as pp            # noqa: E402
import adapters              # noqa: E402
from adapters.base import Unsupported   # noqa: E402

CONFIRM_FOR_HOURS = 24       # an unconfirmed post is read back on every tick for this long, then left for your eye


def update(ctx, lid, **fields):
    """Write fields onto one leg at once (reads the plan fresh, so nothing another step wrote is lost)."""
    rows = pp.load(ctx)
    r = pp.find(rows, lid)
    r.update(fields)
    r["changed_by"], r["updated_at"] = "runner", pp.stamp(ctx)
    pp.save(ctx, rows, len(rows))
    return r


def note_once(ctx, leg, event, mode, **kw):
    if not pp.logged_today(ctx, event, leg["id"]):
        pp.log(ctx, leg["id"], event, mode=mode, by="runner", **kw)


def why_not(ctx, leg, at, force):
    """None when the leg should be posted now, else the reason it is not."""
    if leg["status"] != "approved" or leg.get("post_id"):
        return "not approved or already sent"
    if ctx.is_hand(leg):
        return "hand leg: the watcher writes its card, the runner never posts it"
    if not leg.get("approved_by", "").strip():
        return "REFUSED: status approved but no approved_by"
    if leg.get("review") == "hold":
        return "on hold"
    slot = pp.slot_dt(ctx, leg)
    if not force:
        if leg["platform"] == "youtube":
            lead = float(ctx.cfg.get("youtube_upload_lead_days", 7))
            if slot <= at + timedelta(minutes=20):
                return "too close to its slot to schedule; the watcher moves it"
            if slot > at + timedelta(days=lead):
                return "not in the upload window yet"
        else:
            if slot > at:
                return "slot not reached"
            if slot < at - timedelta(hours=ctx.stale_hours):
                return f"slot more than {ctx.stale_hours:g} h old; never posted late, the watcher moves it"
    problems = [x for _, x in pp.check_rows(ctx, [leg], quiet=True)]
    if problems:
        return "BLOCKED by check: " + "; ".join(problems)
    if leg.get("file") and pp.sha(leg["file"]) != leg.get("file_sha256"):
        return "BLOCKED: file changed since approval"
    return None


def confirm(ctx, leg, adapter, mode):
    state, info = adapter.read_back(leg)
    pp.log(ctx, leg["id"], "read-back", mode=mode, state=state, info=info, by="runner")
    if state == "live":
        update(ctx, leg["id"], status="posted", last_error="")
        pp.log(ctx, leg["id"], "posted", mode=mode, post_id=leg["post_id"], url=leg.get("post_url", ""), proof=info, by="runner")
        return True
    update(ctx, leg["id"], last_error=f"read-back {state}: {info}"[:400])
    return False


def identity_problem(ctx, adapter, platform):
    """None when the connected account is the one pinned as the creator's own, else why not. Run before every upload."""
    expected = str(((ctx.cfg.get("adapters") or {}).get(platform) or {}).get("expected_account_id", "")).strip()
    if not expected:
        return f"no expected_account_id pinned for {platform}; run runner.py whoami {platform} and pin your own id"
    try:
        who = str(adapter.whoami())
    except Exception as ex:
        return f"could not read which account is connected: {str(ex)[:160]}"
    if who != expected:
        return f"the connected {platform} account is {who}, not the creator's {expected}"
    return None


def post_one(ctx, leg, mode):
    adapter = adapters.get(ctx, leg["platform"])
    adapter.check_connection()
    wrong = identity_problem(ctx, adapter, leg["platform"])
    if wrong:
        note_once(ctx, leg, "refused", mode, reason="REFUSED: " + wrong)
        return "REFUSED: " + wrong
    try:
        res = adapter.upload(leg)
    except Exception as ex:
        n = int(leg.get("attempts", 0)) + 1
        update(ctx, leg["id"], attempts=n, last_error=str(ex)[:400], status="failed" if n >= 3 else "approved")
        pp.log(ctx, leg["id"], "error", mode=mode, attempt=n, error=str(ex)[:400], by="runner")
        return f"ERROR ({n}/3): {str(ex)[:160]}"
    leg = update(ctx, leg["id"], post_id=res["post_id"], post_url=res.get("post_url", ""), status="uploaded",
                 attempts=int(leg.get("attempts", 0)) + 1, last_error="")
    pp.log(ctx, leg["id"], "accepted", mode=mode, post_id=res["post_id"], url=res.get("post_url", ""), by="runner")
    if adapter.supports_schedule:
        return schedule(ctx, leg, adapter, mode)
    return f"posted {leg['post_id']}" if confirm(ctx, leg, adapter, mode) else f"accepted {leg['post_id']}; not yet read back"


def schedule(ctx, leg, adapter, mode):
    utc = pp.slot_dt(ctx, leg).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        adapter.schedule(leg, leg["post_id"], utc)
    except Exception as ex:
        update(ctx, leg["id"], last_error=f"uploaded private, schedule failed: {str(ex)[:300]}")
        pp.log(ctx, leg["id"], "schedule-failed", mode=mode, error=str(ex)[:300], by="runner")
        return f"uploaded {leg['post_id']} private; schedule failed, retried next tick"
    update(ctx, leg["id"], scheduled_for=utc)
    pp.log(ctx, leg["id"], "scheduled", mode=mode, post_id=leg["post_id"], publish_at=utc, by="runner")
    return f"uploaded {leg['post_id']} private, publishes {utc}"


def comment_due(leg):
    return (leg["status"] == "posted" and leg.get("post_id") and "https://" in (leg.get("first_comment") or "")
            and not leg.get("comment_id") and int(leg.get("comment_attempts", 0)) < 3)


def comment_one(ctx, leg, mode):
    try:
        cid = adapters.get(ctx, leg["platform"]).comment(leg, leg["post_id"], leg["first_comment"])
    except Exception as ex:
        update(ctx, leg["id"], comment_attempts=int(leg.get("comment_attempts", 0)) + 1)
        pp.log(ctx, leg["id"], "comment-failed", mode=mode, error=str(ex)[:300], by="runner")
        return f"comment failed: {str(ex)[:120]}"
    update(ctx, leg["id"], comment_id=cid)
    pp.log(ctx, leg["id"], "full-video-comment", mode=mode, comment_id=cid, by="runner")
    return f"comment {cid}"


def tick(ctx, live=False, only=None, force=False):
    """One pass. Returns [(leg id, what happened)]."""
    mode = "live" if live else "dry-run"
    at = ctx.now()
    out, sent = [], set()
    for leg in sorted(pp.load(ctx), key=lambda r: r["slot"]):
        if only and leg["id"] != only:
            continue
        reason = why_not(ctx, leg, at, force and bool(only))
        if reason:
            if reason.startswith(("REFUSED", "BLOCKED")):
                note_once(ctx, leg, "refused", mode, reason=reason)
                out.append((leg["id"], reason))
            elif only:
                out.append((leg["id"], reason))
            continue
        if not live:
            note_once(ctx, leg, "would-post", mode, platform=leg["platform"], slot=leg["slot"])
            out.append((leg["id"], f"DRY RUN: would post on {leg['platform']} ({leg['kind']})"))
            continue
        fake_route = ((ctx.cfg.get("adapters") or {}).get(leg["platform"]) or {}).get("route") == "fake"
        out.append((leg["id"], post_one(ctx, leg, mode) + (" (fake route: practice only, nothing left this computer)" if fake_route else "")))
        sent.add(leg["id"])
    if not live:
        return out
    for leg in pp.load(ctx):                    # sent, not yet proven: read back, never re-upload
        if only and leg["id"] != only:
            continue
        if leg["status"] != "uploaded" or not leg.get("post_id") or ctx.is_hand(leg) or leg["id"] in sent:
            continue
        slot = pp.slot_dt(ctx, leg)
        try:
            adapter = adapters.get(ctx, leg["platform"])
            if leg.get("posted_by_hand"):          # the creator uploaded it in the platform's own app: read the channel
                ok = confirm(ctx, leg, adapter, mode)
                out.append((leg["id"], "hand post read back, posted" if ok else "hand post not found on the channel yet"))
                continue
            if adapter.supports_schedule and not leg.get("scheduled_for"):
                if slot > at:
                    out.append((leg["id"], schedule(ctx, leg, adapter, mode)))
                continue
            if adapter.supports_schedule and slot > at:
                continue
            if at > slot + timedelta(hours=CONFIRM_FOR_HOURS):
                note_once(ctx, leg, "unconfirmed-stop", mode, info="no proof after 24 h; look at the post and record it with plan.py posted")
                continue
            ok = confirm(ctx, leg, adapter, mode)
            out.append((leg["id"], "posted (read back)" if ok else "still not read back"))
        except Exception as ex:
            pp.log(ctx, leg["id"], "read-back-failed", mode=mode, error=str(ex)[:300], by="runner")
    for leg in pp.load(ctx):                    # the full-video link, once per leg
        if (not only or leg["id"] == only) and comment_due(leg) and not ctx.is_hand(leg):
            out.append((leg["id"], comment_one(ctx, leg, mode)))
    return out


# ---------- commands ----------

def cmd_tick(a):
    ctx = pp.ctx_from(a)
    res = tick(ctx, live=a.live, only=a.leg, force=a.force)
    for lid, what in res:
        print(f"{lid} -> {what}")
    if not res:
        print(f"nothing due ({'live' if a.live else 'dry run'})")


def cmd_whoami(a):
    ctx = pp.ctx_from(a)
    adapter = adapters.get(ctx, a.platform)
    adapter.check_connection()
    who = adapter.whoami()
    pinned = ((ctx.cfg.get("adapters") or {}).get(a.platform) or {}).get("expected_account_id", "")
    print(f"{a.platform}: the connected account is {who}")
    print("matches the pinned expected_account_id" if who == pinned else
          f"pinned: {pinned or 'nothing'}. If {who} is YOUR account, put it in adapters.{a.platform}.expected_account_id")


def cmd_readback(a):
    ctx = pp.ctx_from(a)
    leg = pp.find(pp.load(ctx), a.leg)
    if not leg.get("post_id"):
        raise SystemExit(f"{a.leg} has no post id yet")
    adapter = adapters.get(ctx, leg["platform"])
    ok = confirm(ctx, leg, adapter, "live")
    print(f"{a.leg}: {'live, marked posted' if ok else 'not proven'}; see the log for the platform's answer")


def cmd_status(a):
    ctx = pp.ctx_from(a)
    at = ctx.now()
    rows = [r for r in sorted(pp.load(ctx), key=lambda r: r["slot"]) if pp.slot_dt(ctx, r) >= at - timedelta(days=1)
            and r["status"] not in ("empty", "skipped")][:12]
    for r in rows:
        print(f"{r['slot'][:16].replace('T', ' ')}  {r['platform']:<9} {r['status']:<9} {r['id']:<34} "
              f"{'approved by ' + r['approved_by'] if r['approved_by'] else 'NOT approved'}"
              + (f"  last error: {r['last_error'][:80]}" if r.get("last_error") else ""))
    print(f"{len(rows)} legs shown")


# ---------- self-test ----------

def run_selftest(base):
    from adapters import fake
    fails = []

    def check(label, ok):
        print(("  ok    " if ok else "  FAIL  ") + label)
        if not ok:
            fails.append(label)

    ctx, media = pp.make_test_project(base)
    ctx.set_clock("2026-11-09T08:00")
    rows = []
    pp.build_skeleton(ctx, rows, datetime(2026, 11, 9).date())
    link = "Full video: https://example.com/full"
    fill = {
        "2026-11-09-linkedin-video": {"caption": "A short about the week.", "thumb": str(media / "thumb.jpg"), "first_comment": link},
        "2026-11-09-instagram-reel": {"caption": "A reel about the week.", "first_comment": link},
        "2026-11-10-youtube-short": {"caption": "A short.", "title": "A short", "first_comment": link},
        "2026-11-09-tiktok-video": {"caption": "A TikTok."},
        "2026-11-11-instagram-reel": {"caption": "A reel that will fail."},
        "2026-11-13-linkedin-video": {"caption": "A short read back late.", "thumb": str(media / "thumb.jpg")},
        "2026-11-11-linkedin-video": {"caption": "Approved with no name.", "thumb": str(media / "thumb.jpg")},
    }
    for lid, kv in fill.items():
        r = pp.find(rows, lid)
        pp.apply_fields(ctx, r, {"file": str(media / "clip.mp4"), "piece": "ep1", **kv}, "test")
        if lid != "2026-11-11-linkedin-video":
            pp.approve(ctx, rows, [r], "Creator A, in session")
    nameless = pp.find(rows, "2026-11-11-linkedin-video")
    nameless["status"] = "approved"          # a row edited by hand into approved, with no name
    pp.save(ctx, rows, 0)

    ctx.set_clock("2026-11-09T12:05")
    dry = dict(tick(ctx, live=False))
    check("dry run posts nothing", fake.posts(ctx) == {})
    check("dry run says the LinkedIn leg would post", "would post" in dry.get("2026-11-09-linkedin-video", ""))
    check("dry run writes a would-post line to the log", "would-post" in ctx.log.read_text())
    check("the hand TikTok leg is never posted, even in dry run", "2026-11-09-tiktok-video" not in dry)

    res = dict(tick(ctx, live=True))
    legs = {r["id"]: r for r in pp.load(ctx)}
    check("live: the due LinkedIn leg is posted and proven", legs["2026-11-09-linkedin-video"]["status"] == "posted")
    check("live: its full-video comment went once", legs["2026-11-09-linkedin-video"]["comment_id"] != "")
    check("live: the YouTube Short uploads early, private, with publishAt set",
          legs["2026-11-10-youtube-short"]["status"] == "uploaded" and legs["2026-11-10-youtube-short"]["scheduled_for"].startswith("2026-11-10T19:00"))
    check("live: the Reel waits for its slot", legs["2026-11-09-instagram-reel"]["status"] == "approved")
    check("live: the TikTok hand leg is untouched", legs["2026-11-09-tiktok-video"]["status"] == "approved" and not legs["2026-11-09-tiktok-video"]["post_id"])
    check("live: a leg with no approved_by is refused", "REFUSED" in res.get("2026-11-11-linkedin-video", "") and not legs["2026-11-11-linkedin-video"]["post_id"])
    n = len(fake.posts(ctx))
    tick(ctx, live=True)
    check("a second tick posts nothing twice", len(fake.posts(ctx)) == n == 2)

    ctx.set_clock("2026-11-09T16:05")
    tick(ctx, live=True)
    tick(ctx, live=True)
    reel = pp.find(pp.load(ctx), "2026-11-09-instagram-reel")
    posts = fake.posts(ctx)
    check("the Reel posts at its slot", reel["status"] == "posted")
    check("its comment went exactly once", len(posts[reel["post_id"]]["comments"]) == 1)

    ctx.set_clock("2026-11-10T14:05")
    tick(ctx, live=True)
    yt = pp.find(pp.load(ctx), "2026-11-10-youtube-short")
    check("after its slot the Short reads back public and is marked posted", yt["status"] == "posted")
    check("then gets its full-video comment", yt["comment_id"] != "")

    ctx.cfg["adapters"]["instagram"] = {"route": "fake", "fail_uploads": 3, "account_id": "fake-creator", "expected_account_id": "fake-creator"}
    for t in ("2026-11-11T16:05", "2026-11-11T16:15", "2026-11-11T16:25"):
        ctx.set_clock(t)
        tick(ctx, live=True)
    bad = pp.find(pp.load(ctx), "2026-11-11-instagram-reel")
    check("3 upload errors mark the leg failed, no post made", bad["status"] == "failed" and not bad["post_id"])
    ctx.cfg["adapters"]["instagram"] = {"route": "fake", "account_id": "fake-creator", "expected_account_id": "fake-creator"}

    ctx.cfg["adapters"]["linkedin"] = {"route": "fake", "read_back": "unconfirmed", "confirm_after": 1, "account_id": "fake-creator", "expected_account_id": "fake-creator"}
    ctx.set_clock("2026-11-13T12:05")
    before = len(fake.posts(ctx))
    tick(ctx, live=True)
    late = pp.find(pp.load(ctx), "2026-11-13-linkedin-video")
    check("an unconfirmed read-back leaves the leg uploaded, not posted", late["status"] == "uploaded")
    ctx.set_clock("2026-11-13T12:15")
    tick(ctx, live=True)
    late = pp.find(pp.load(ctx), "2026-11-13-linkedin-video")
    check("the next tick retries the read, not the upload", late["status"] == "posted" and len(fake.posts(ctx)) == before + 1)

    rows = pp.load(ctx)
    wed = pp.find(rows, "2026-11-11-youtube-short")
    pp.apply_fields(ctx, wed, {"file": str(media / "clip.mp4"), "caption": "Wed short.", "title": "Wed"}, "test")
    ctx.set_clock("2026-11-10T15:00")
    pp.approve(ctx, rows, [wed], "Creator A")
    pp.save(ctx, rows, len(rows))
    (media / "clip.mp4").write_bytes(b"the file changed after approval")
    res = dict(tick(ctx, live=True))
    check("a file changed after approval is refused", "BLOCKED" in res.get("2026-11-11-youtube-short", "") and not pp.find(pp.load(ctx), "2026-11-11-youtube-short")["post_id"])

    ctx2, media2 = pp.make_test_project(base)
    ctx2.set_clock("2026-11-09T08:00")
    rows = []
    pp.build_skeleton(ctx2, rows, datetime(2026, 11, 9).date())
    r = pp.find(rows, "2026-11-09-linkedin-video")
    pp.apply_fields(ctx2, r, {"file": str(media2 / "clip.mp4"), "thumb": str(media2 / "thumb.jpg"), "caption": "Late."}, "test")
    pp.approve(ctx2, rows, [r], "Creator A")
    pp.save(ctx2, rows, 0)
    ctx2.set_clock("2026-11-09T19:00")
    tick(ctx2, live=True)
    check("a machine leg 7 h past its slot is never posted late", fake.posts(ctx2) == {})

    # the approval reaches the copy the runner reads: approve from a separate process, then tick
    rows = pp.load(ctx2)
    wed = pp.find(rows, "2026-11-11-linkedin-video")
    pp.apply_fields(ctx2, wed, {"file": str(media2 / "clip.mp4"), "thumb": str(media2 / "thumb.jpg"), "caption": "Wednesday."}, "test")
    pp.save(ctx2, rows, len(rows))
    import subprocess
    r = subprocess.run([sys.executable, str(Path(__file__).resolve().parent / "plan.py"), "--project", str(ctx2.project),
                        "approve", wed["id"], "--by", "Creator A, from another terminal"], capture_output=True, text=True,
                       env={**__import__("os").environ, "PYTHONDONTWRITEBYTECODE": "1"})
    ctx2.set_clock("2026-11-11T12:05")
    ctx2.cfg["adapters"]["linkedin"] = {"route": "fake", "account_id": "a-co-host", "expected_account_id": "fake-creator"}
    res = dict(tick(ctx2, live=True))
    check("a connected account that is not the creator's is refused before any upload",
          "REFUSED" in res.get(wed["id"], "") and "a-co-host" in res.get(wed["id"], "") and fake.posts(ctx2) == {})
    ctx2.cfg["adapters"]["linkedin"] = {"route": "fake", "account_id": "fake-creator", "expected_account_id": ""}
    res = dict(tick(ctx2, live=True))
    check("an empty expected_account_id is refused too", "REFUSED" in res.get(wed["id"], "") and fake.posts(ctx2) == {})
    ctx2.cfg["adapters"]["linkedin"] = {"route": "fake", "account_id": "fake-creator", "expected_account_id": "fake-creator"}
    tick(ctx2, live=True)
    check("an approval made in another process is read fresh by the next tick and posts",
          r.returncode == 0 and pp.find(pp.load(ctx2), wed["id"])["status"] == "posted")

    # a video the creator uploaded by hand in the platform's own app is marked posted only from a channel read
    rows = pp.load(ctx2)
    yt = pp.find(rows, "2026-11-12-youtube-short")
    pp.apply_fields(ctx2, yt, {"file": str(media2 / "clip.mp4"), "caption": "By hand.", "title": "By hand"}, "test")
    pp.approve(ctx2, rows, [yt], "Creator A")
    waits = pp.record_hand_post(ctx2, yt, "https://youtube.com/shorts/AbCdEfGhIjK", "Creator A")
    pp.save(ctx2, rows, len(rows))
    ctx2.set_clock("2026-11-11T13:00")
    tick(ctx2, live=True)
    yt = pp.find(pp.load(ctx2), yt["id"])
    check("a hand upload waits as uploaded until the channel shows it", waits and yt["status"] == "uploaded" and yt["post_id"] == "AbCdEfGhIjK")
    store_path = ctx2.project / "content" / "posting" / "fake-platform.json"
    st = json.loads(store_path.read_text())
    st["posts"]["AbCdEfGhIjK"] = {"leg": yt["id"], "platform": "youtube", "caption": "By hand.", "public": True, "publish_at": "", "comments": []}
    store_path.write_text(json.dumps(st))
    uploads = st["uploads"]
    tick(ctx2, live=True)
    yt = pp.find(pp.load(ctx2), yt["id"])
    check("once the channel read finds it public it is marked posted, and the runner never uploads it",
          yt["status"] == "posted" and json.loads(store_path.read_text())["uploads"] == uploads)
    tk = pp.find(pp.load(ctx2), "2026-11-11-tiktok-video")
    check("a hand platform's post is recorded on the creator's word", not pp.record_hand_post(ctx2, tk, "https://example.com/tt/9", "Creator A") and tk["status"] == "posted")
    print(f"runner selftest: {len(fails)} failed" if fails else "runner selftest: all pass")
    return not fails


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project")
    ap.add_argument("--config")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--tmp", help="where the self-test makes its throwaway project (default: the system temp folder)")
    sub = ap.add_subparsers(dest="cmd")
    s = sub.add_parser("tick")
    s.add_argument("--live", action="store_true", help="post for real (without it, a dry run)")
    s.add_argument("--dry-run", action="store_true", help="the default; kept so a schedule can say it out loud")
    s.add_argument("--leg")
    s.add_argument("--force", action="store_true", help="with --leg: ignore the slot (approval and checks still apply)")
    s.add_argument("--at", help="pretend it is this local time (testing)")
    s.set_defaults(fn=cmd_tick)
    s = sub.add_parser("readback"); s.add_argument("leg"); s.set_defaults(fn=cmd_readback)
    s = sub.add_parser("whoami", help="which account a platform's connection posts as"); s.add_argument("platform"); s.set_defaults(fn=cmd_whoami)
    s = sub.add_parser("status"); s.set_defaults(fn=cmd_status)
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if run_selftest(a.tmp) else 1)
    if not a.cmd:
        ap.print_help()
        sys.exit(2)
    if getattr(a, "live", False) and getattr(a, "dry_run", False):
        raise SystemExit("--live and --dry-run together: pick one")
    a.fn(a)


if __name__ == "__main__":
    main()
