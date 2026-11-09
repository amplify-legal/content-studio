#!/usr/bin/env python3
"""
profile_check.py, the check after a creator-profile sitting.

WHAT THIS IS FOR

The creator-profile deep dive writes content/profile/ in the creator's own
words. A sitting can go wrong in quiet ways that all look like success in the
conversation:

  1. It talked for 30 minutes and wrote nothing to disk.
  2. It paraphrased the creator instead of quoting them.
  3. It left a template <placeholder> in a file.
  4. It skipped the money questions, or filled them with a guess, so the
     price band or a customer's worth is simply blank.
  5. It wrote the summary and stamped it confirmed before anyone said yes,
     or never asked.
  6. It put real figures in a private file that git will happily commit.

So the folder gets a check, run before the laptop closes.

WHAT IT CHECKS

For every section the progress table marks `done` (or every section, with
--all):

  exists       the file is there and has something in it
  updated      an `updated: YYYY-MM-DD` line
  your words   at least 1 passage in quotation marks
  filled in    no <placeholder> left from a template
  the fields   the few fields each file must carry (see file-shapes.md)

And always:

  progress     every state is `not started`, `started` or `done`
  private      if content/profile/private.md exists, .gitignore lists it
  preferences  content/setup/preferences.md names a level: lite, standard
               or full (a warning when the file is missing)

A section that is not done yet prints an OPEN line, which is information,
not a failure. A sitting that did only "who" passes when "who" is right.

USAGE

    python3 .claude/skills/creator-profile/scripts/profile_check.py content/profile
    python3 .claude/skills/creator-profile/scripts/profile_check.py content/profile --all
    python3 .claude/skills/creator-profile/scripts/profile_check.py --preferences content/setup/preferences.md
    python3 .claude/skills/creator-profile/scripts/profile_check.py --selftest

Exit 0 when every checked part passes, 1 when something needs another few
minutes in the same conversation. Standard library only; no network, no key.

IT IS A FLOOR, NOT A JUDGE

It counts structure. It cannot tell whether the profile sounds like the
person. Reading summary.md with them is still the real check.
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

SECTIONS = [
    ("Who", "who.md"),
    ("Business", "business.md"),
    ("Objectives", "objectives.md"),
    ("Style", "style.md"),
    ("Inspirations", "inspirations.md"),
    ("Platforms", "platforms.md"),
    ("Summary", "summary.md"),
]
STATES = {"not started", "started", "done"}
LEVELS = {"lite", "standard", "full"}
MIN_QUOTE_CHARS = 8

UPDATED = re.compile(r"^updated:\s*\d{4}-\d{2}-\d{2}\s*$", re.M)
CONFIRMED = re.compile(r"^confirmed:\s*\d{4}-\d{2}-\d{2}\s*$", re.M)
QUOTED = re.compile(r"[\"“]([^\"“”\n]{%d,400})[\"”]" % MIN_QUOTE_CHARS)
# <placeholder like this>, but not an HTML tag such as <br> or </div>.
PLACEHOLDER = re.compile(r"<(?!/)(?!br\b|hr\b|img\b|a\b|div\b|span\b|p\b)[A-Za-z][^<>\n]{3,}>")
LEVEL_LINE = re.compile(r"^level:\s*(\S+)\s*$", re.M)


def section_body(text: str, heading_words: str) -> str:
    """The text under the first heading containing heading_words, up to the next heading of the same or higher level."""
    lines = text.splitlines()
    out: list[str] = []
    level = None
    for line in lines:
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            if level is not None and len(m.group(1)) <= level:
                break
            if level is None and heading_words.lower() in m.group(2).lower():
                level = len(m.group(1))
                continue
        if level is not None:
            out.append(line)
    return "\n".join(out) if level is not None else ""


def table_rows(body: str) -> int:
    rows = 0
    for line in body.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        if re.match(r"^\|[\s:|-]+\|?$", s):
            continue
        rows += 1
    # The first table line is the header.
    return max(rows - 1, 0)


def items(body: str) -> int:
    return sum(1 for line in body.splitlines() if re.match(r"^\s*(?:[-*+]|\d+[.)])\s+\S", line))


def subheadings(body: str) -> int:
    return sum(1 for line in body.splitlines() if re.match(r"^#{3,6}\s+\S", line))


def has_text(body: str) -> bool:
    return any(line.strip() and not line.strip().startswith(">") for line in body.splitlines())


# Each returns a list of (ok, label, detail, say_back).
def fields_who(t):
    return []


def fields_business(t):
    out = []
    no_offer = "no offer yet" in t.lower()
    sell = section_body(t, "What I sell")
    out.append((no_offer or has_text(sell), "what they sell",
                "a 'What I sell' section, or 'no offer yet' in their words",
                "Ask me what I sell today, all of it, and write it under 'What I sell'."))
    worth = section_body(t, "worth")
    ok = bool(re.search(r"\S", worth)) and (
        "UNKNOWN" in worth or "private" in worth.lower() or re.search(r"\d", worth) is not None
    )
    out.append((ok, "customer worth",
                "a value, UNKNOWN (asked date) or private under 'What one customer is worth'",
                "Ask me what one customer is worth to me. If I do not know, write UNKNOWN with today's date. Never guess it."))
    return out


def fields_objectives(t):
    ninety = section_body(t, "90 days")
    metric = section_body(t, "one metric")
    return [
        (table_rows(ninety) >= 1 or items(ninety) >= 1, "the 90-day number",
         "a row under 'Specific, the next 90 days'",
         "Ask me the one number I will measure in the next 90 days, where I read it, and my target."),
        (has_text(metric), "the one metric",
         "something under 'The one metric this system moves'",
         "Propose the one metric this system moves, once, then write mine."),
    ]


def fields_style(t):
    read = section_body(t, "pieces read")
    confirmed = section_body(t, "Confirmed")
    return [
        (table_rows(read) >= 3, "pieces read", "3 or more rows under 'The pieces read'",
         "Read at least 3 of my own pieces before you tell me my style."),
        (items(confirmed) >= 1, "confirmed", "1 or more lines under 'Confirmed'",
         "Play back one observation about my style and ask me to confirm or correct it."),
    ]


def fields_inspirations(t):
    loved = section_body(t, "Loved")
    disliked = section_body(t, "Disliked")

    def entries(body):
        # One sub-heading per creator when the file uses them; otherwise one bullet each.
        return subheadings(body) if subheadings(body) else items(body)

    return [
        (entries(loved) >= 3, "loved", f"{entries(loved)} under 'Loved', 3 wanted",
         "Ask me for 3 creators or pieces I love, and why, one at a time."),
        (entries(disliked) >= 1, "disliked", "1 or more under 'Disliked'",
         "Ask me for the creators or pieces that put me off, and why."),
    ]


def fields_platforms(t):
    now = section_body(t, "Now")
    wanted = section_body(t, "Wanted")
    time_b = section_body(t, "Time")
    return [
        (table_rows(now) >= 1 or items(wanted) >= 1 or table_rows(wanted) >= 1, "platforms",
         "a row under 'Now' or 'Wanted'", "Ask me where I post now and where I want to post."),
        (table_rows(time_b) >= 1 or re.search(r"\d+(\.\d+)?\s*h", time_b) is not None, "time",
         "a total under 'Time, in a real week'",
         "Ask me how many hours a real week gives content, split into recording, editing, writing and posting."),
    ]


def fields_summary(t):
    rec = section_body(t, "Recommended level")
    level_ok = any(re.search(r"\b%s\b" % lv, rec.lower()) for lv in LEVELS)
    return [
        (CONFIRMED.search(t) is not None, "confirmed",
         "a 'confirmed: YYYY-MM-DD' line, written only after I said yes",
         "Show me the whole summary and ask me if it is me. Write confirmed only after I say yes."),
        (level_ok, "recommended level", "a 'Recommended level' naming lite, standard or full, with the reason",
         "Recommend my install level with the reason, from my own answers."),
    ]


FIELDS = {
    "who.md": fields_who,
    "business.md": fields_business,
    "objectives.md": fields_objectives,
    "style.md": fields_style,
    "inspirations.md": fields_inspirations,
    "platforms.md": fields_platforms,
    "summary.md": fields_summary,
}


def read_progress(profile: Path):
    """Return ({file: state}, problems). Empty dict when there is no progress.md."""
    p = profile / "progress.md"
    if not p.is_file():
        return {}, []
    states: dict[str, str] = {}
    problems = []
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 3 and cells[1].endswith(".md"):
            state = cells[2].lower()
            states[cells[1]] = state
            if state not in STATES:
                problems.append(f"{cells[1]} has state '{cells[2]}'")
    return states, problems


def check_file(path: Path, name: str):
    results = []
    if not path.is_file() or not path.read_text(encoding="utf-8", errors="replace").strip():
        results.append((False, "exists", f"{path} is missing or empty",
                        f"Write {name} now, from what I already told you, before the next question."))
        return results
    t = path.read_text(encoding="utf-8", errors="replace")
    results.append((True, "exists", "", ""))
    results.append((UPDATED.search(t) is not None, "updated", "an 'updated: YYYY-MM-DD' line",
                    f"Put today's date on the updated line of {name}."))
    q = len(QUOTED.findall(t))
    results.append((q >= 1, "your words", f"{q} quoted passages, 1 wanted",
                    f"Those are your words in {name}, not mine. Put my own sentences in, in quotation marks."))
    ph = PLACEHOLDER.findall(t)
    results.append((not ph, "filled in", f"placeholder left: {ph[0] if ph else ''}",
                    f"Replace the template placeholders in {name} with my answer, or with OPEN and the question."))
    results.extend(FIELDS[name](t))
    return results


def check_private(profile: Path):
    priv = profile / "private.md"
    if not priv.is_file():
        return None
    root = profile.parent.parent
    gi = root / ".gitignore"
    listed = False
    if gi.is_file():
        for line in gi.read_text(encoding="utf-8", errors="replace").splitlines():
            s = line.strip().lstrip("/")
            if s in ("content/profile/private.md", "private.md", "content/profile/", "content/profile/*"):
                listed = True
    return (listed, "private", "content/profile/private.md exists and .gitignore does not list it",
            "Add content/profile/private.md to .gitignore now, then run git check-ignore on it.")


def check_preferences(path: Path):
    if not path.is_file():
        return None
    t = path.read_text(encoding="utf-8", errors="replace")
    m = LEVEL_LINE.search(t)
    ok = bool(m) and m.group(1).strip().lower() in LEVELS
    got = m.group(1) if m else "no level line"
    return (ok, "preferences", f"level is '{got}', want lite, standard or full",
            "Write my level into content/setup/preferences.md as 'level: lite', 'level: standard' or 'level: full'.")


def run(profile: Path | None, prefs: Path | None, check_all: bool, out=print) -> int:
    failed = 0

    def line(ok, label, detail, say):
        nonlocal failed
        if ok:
            out(f"PASS     {label}")
        else:
            failed += 1
            out(f"MISSING  {label}   {detail}")
            if say:
                out(f"         say: \"{say}\"")

    if profile is not None:
        if not profile.is_dir():
            line(False, "profile folder", f"{profile} does not exist",
                 "Create content/profile/ and progress.md, then start the first sitting.")
            return 1
        states, problems = read_progress(profile)
        has_progress = (profile / "progress.md").is_file()
        started = has_progress or any((profile / n).is_file() for _, n in SECTIONS)
        to_check = SECTIONS
        if not started and not check_all:
            # Nothing has run yet: one line, not 7 identical ones.
            line(False, "first sitting", "content/profile/ has no progress.md and no section files yet",
                 "Start my profile.")
            to_check = []
        if has_progress:
            line(not problems, "progress", "; ".join(problems) or "",
                 "Fix the states in progress.md: each is 'not started', 'started' or 'done'.")
        for section, name in to_check:
            # With no progress.md, every section is checked as if done.
            state = "done" if (check_all or not states) else states.get(name, "not started")
            if state != "done":
                out(f"OPEN     {section.lower()}   {state}")
                continue
            out(f"-- {name}")
            for ok, label, detail, say in check_file(profile / name, name):
                line(ok, f"{section.lower()}: {label}", detail, say)
        pr = check_private(profile)
        if pr:
            line(*pr)
        if prefs is None:
            guess = profile.parent / "setup" / "preferences.md"
            prefs = guess if guess.is_file() else None
            if prefs is None:
                out("WARN     preferences   content/setup/preferences.md not found (SETUP.md writes it)")
    if prefs is not None:
        pc = check_preferences(prefs)
        if pc:
            line(*pc)
        else:
            line(False, "preferences", f"{prefs} not found", "Run the preference questions at the top of SETUP.md.")
    out("result: PASS" if failed == 0 else f"result: {failed} to fix")
    return 0 if failed == 0 else 1


# ---------------------------------------------------------------- self-test

GOOD = {
    "progress.md": """> progress
updated: 2026-01-12

| Section | File | State | Last asked |
|---|---|---|---|
| Who | who.md | done | |
| Business | business.md | done | |
| Objectives | objectives.md | done | |
| Style | style.md | done | |
| Inspirations | inspirations.md | done | |
| Platforms | platforms.md | done | |
| Summary | summary.md | done | |
""",
    "who.md": """> who
updated: 2026-01-12

## In one breath
"I help small bakeries stop guessing what to bake." (2026-01-12)
""",
    "business.md": """> business
updated: 2026-01-12

## What I sell
| Offer | In their words | Buyer | Price band |
|---|---|---|---|
| A course | "the waste course" | owners of small bakeries | 100 to 1,000 |

## What one customer is worth
UNKNOWN (asked 2026-01-12). "I've never added it up."
""",
    "objectives.md": """> objectives
updated: 2026-01-12

## Broad, the next 12 months
"The course is what people recommend without me asking." (2026-01-12)

## Specific, the next 90 days
| The number | Where | Today | Target | By |
|---|---|---|---|---|
| sign-ups | the tool | UNKNOWN | proposed: 150 | 2026-04-12 |

## The one metric this system moves
Pieces shipped a week with the next step in them.
""",
    "style.md": """> style
updated: 2026-01-12

## The pieces read
| # | Piece | How | Label |
|---|---|---|---|
| 1 | a | watch | proud |
| 2 | b | text | typical |
| 3 | c | pasted | dislike |

## Confirmed
- Opens with a question. Their words: "Yes, always, at the counter too." (2026-01-12)
""",
    "inspirations.md": """> inspirations
updated: 2026-01-12

## Loved
### Creator A
- Why: "She shows the mess first." (2026-01-12)
### Creator B
- Why: "He never wastes the first line." (2026-01-12)
### Creator C
- Why: "Quiet, and it still pulls me in." (2026-01-12)

## Disliked
### Creator D
- Why: "Every title is a fake fight." (2026-01-12)
""",
    "platforms.md": """> platforms
updated: 2026-01-12

## Now
| Platform | How often | Format | Working | Number |
|---|---|---|---|---|
| a video platform | weekly | long | "the tutorials" | UNKNOWN |

## Time, in a real week
| Recording | Editing | Writing | Posting | Total |
|---|---|---|---|---|
| 2 h | 3 h | 1 h | 0.5 h | 6.5 h |
""",
    "summary.md": """> summary
updated: 2026-01-12
confirmed: 2026-01-12

**Who:** "I help small bakeries stop guessing what to bake."

## Recommended level
**lite**, because: 6.5 hours a week and posting by hand.
""",
}


def build(root: Path, files: dict, prefs: str | None = "level: lite\n", gitignore: str | None = None) -> Path:
    prof = root / "content" / "profile"
    prof.mkdir(parents=True)
    for name, body in files.items():
        (prof / name).write_text(body, encoding="utf-8")
    if prefs is not None:
        (root / "content" / "setup").mkdir(parents=True)
        (root / "content" / "setup" / "preferences.md").write_text(prefs, encoding="utf-8")
    if gitignore is not None:
        (root / ".gitignore").write_text(gitignore, encoding="utf-8")
    return prof


def selftest() -> int:
    def variant(**changes):
        d = dict(GOOD)
        for k, v in changes.items():
            if v is None:
                d.pop(k, None)
            else:
                d[k] = v
        return d

    only_who = GOOD["progress.md"].replace("| Business | business.md | done |", "| Business | business.md | started |")
    for name in ("objectives.md", "style.md", "inspirations.md", "platforms.md", "summary.md"):
        only_who = only_who.replace(f"| {name} | done |", f"| {name} | not started |")

    cases = [
        ("a complete profile passes", variant(), "level: lite\n", None, False, 0),
        ("no updated line fails", variant(**{"who.md": GOOD["who.md"].replace("updated: 2026-01-12\n", "")}), "level: lite\n", None, False, 1),
        ("a template placeholder fails", variant(**{"who.md": GOOD["who.md"] + "\n<your sentence here>\n"}), "level: lite\n", None, False, 1),
        ("no quoted words fails", variant(**{"who.md": "> who\nupdated: 2026-01-12\n\n## In one breath\nI help bakeries.\n"}), "level: lite\n", None, False, 1),
        ("a blank customer worth fails", variant(**{"business.md": GOOD["business.md"].replace('UNKNOWN (asked 2026-01-12). "I\'ve never added it up."', "")}), "level: lite\n", None, False, 1),
        ("'no offer yet' with UNKNOWN worth passes", variant(**{"business.md": '> b\nupdated: 2026-01-12\n\n"no offer yet, the content is the point for now"\n\n## What one customer is worth\nUNKNOWN (asked 2026-01-12)\n'}), "level: lite\n", None, False, 0),
        ("a summary never confirmed fails", variant(**{"summary.md": GOOD["summary.md"].replace("confirmed: 2026-01-12\n", "")}), "level: lite\n", None, False, 1),
        ("style with 0 confirmed fails", variant(**{"style.md": GOOD["style.md"].split("## Confirmed")[0] + '## Confirmed\n\n## Heard, not confirmed\n- "here\'s the thing" maybe\n'}), "level: lite\n", None, False, 1),
        ("only 'who' done: the rest are OPEN and it passes", variant(**{"progress.md": only_who, "business.md": None, "summary.md": None}), "level: lite\n", None, False, 0),
        ("--all on a partial profile fails", variant(**{"progress.md": only_who, "business.md": None}), "level: lite\n", None, True, 1),
        ("a bad state in progress fails", variant(**{"progress.md": GOOD["progress.md"].replace("| who.md | done |", "| who.md | finished |")}), "level: lite\n", None, False, 1),
        ("an invalid level fails", variant(), "level: medium\n", None, False, 1),
        ("an empty profile folder fails once, asking to start", {}, "level: lite\n", None, False, 1),
        ("private.md not in .gitignore fails", variant(**{"private.md": "> private\nupdated: 2026-01-12\n"}), "level: lite\n", "", False, 1),
        ("private.md listed in .gitignore passes", variant(**{"private.md": "> private\nupdated: 2026-01-12\n"}), "level: lite\n", ".env\ncontent/profile/private.md\n", False, 0),
    ]
    passed = 0
    with tempfile.TemporaryDirectory(prefix="profile-check-selftest-") as tmp:
        for i, (label, files, prefs, gi, all_flag, want) in enumerate(cases):
            root = Path(tmp) / f"case{i}"
            prof = build(root, files, prefs, gi)
            got = run(prof, None, all_flag, out=lambda *_: None)
            ok = got == want
            passed += ok
            print(f"{'ok  ' if ok else 'FAIL'} {label} (exit {got}, want {want})")
        # The preferences-only mode.
        root = Path(tmp) / "prefs-only"
        (root / "content" / "setup").mkdir(parents=True)
        p = root / "content" / "setup" / "preferences.md"
        p.write_text("updated: 2026-01-12\nlevel: standard\n", encoding="utf-8")
        got = run(None, p, False, out=lambda *_: None)
        ok = got == 0
        passed += ok
        print(f"{'ok  ' if ok else 'FAIL'} --preferences alone on a valid file passes (exit {got}, want 0)")
    total = len(cases) + 1
    print(f"selftest: {passed}/{total} cases pass" + ("" if passed == total else ", FAILED"))
    return 0 if passed == total else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Check content/profile/ after a creator-profile sitting.")
    ap.add_argument("profile", nargs="?", help="the profile folder, usually content/profile")
    ap.add_argument("--preferences", help="check this preferences.md (default: content/setup/preferences.md beside the profile)")
    ap.add_argument("--all", action="store_true", help="check every section, whatever progress.md says")
    ap.add_argument("--selftest", "--self-test", action="store_true", help="run the offline self-test")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.profile and not a.preferences:
        ap.print_help()
        return 1
    return run(Path(a.profile) if a.profile else None, Path(a.preferences) if a.preferences else None, a.all)


if __name__ == "__main__":
    sys.exit(main())
