#!/usr/bin/env python3
"""
anim_variants.py (27 Oct 2026, the night conductor): the keepers' animation-direction variants, mixed by moment (the
creator's pick: no one direction for every short), with the title-stays and title-goes variants side by side, and light
and dark side by side where the moment is a reveal or a number.

    PYTHONDONTWRITEBYTECODE=1 python3 anim_variants.py [--apply] [--queue] [--queue-file PATH]

For every spec with `card_only_moving` (a keeper) that is not itself a variant: a spec copy per variant,
<specs>/<slug>/<id>-anim<X><suffix>.json with id <id>-anim<X><suffix>, `anim` X (A status cards, B one object that
changes state, C the blend, by the moment, the reason in DIRECTION below and in the spec's `anim_why`), `anim_title`
"stays" or "goes", `anim_dark` true or false.
Variants: <X> (title stays, light), <X>t (title goes, light), and <X>d (title stays, dark) only where the moment is
a reveal or a number. Queue lines carry `--page <this folder>/anim_looks.html` so the overlay renders from the animation
page. Without --apply it only prints what it would write. Nothing is deleted; an existing variant spec is rewritten.
"""
import argparse
import glob
import json
from pathlib import Path

import os as _os, sys as _sys  # noqa: E401
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import paths as PATHS  # noqa: E402
SPECS = PATHS.SPECS
QUEUE = PATHS.BUILD / "queue-podcast.txt"   # the podcast lane's queue (lane_runner.sh podcast); --queue-file names another
PAGE = PATHS.BUILD / "anim_looks.html"

# The direction per keeper, by the moment, and whether the moment is a reveal or a number (which also gets a dark variant).
# The rule for choosing:
#   A (status cards: each item lands with a lift, a bloom and a ping) where many items land one after another or a number
#     counts up and stops (figures said one by one, many reduced to one);
#   B (one object changes state, no glow) where a single thing flips: an order ticket whose steps are stamped as they are said, a
#     value masked and then shown, one issue splitting into 2 lanes;
#   C (the blend: one white panel, A's landing on the active row) where a short sequence sits inside a talking moment and
#     the face should stay big, or a sequence plus a number.
# A keeper with no row gets C. The ids and readings below are an EXAMPLE: write your own per keeper.
DIRECTION = {
    "podcast-guest-a-M1": ("B", False, "one order ticket on screen, each step stamped as it is said: one object changes state"),
    "podcast-guest-a-M2": ("A", True, "4 figures landing as they are said: count-ups that stop on the number"),
    "podcast-guest-o-M1": ("C", True, "steps dropping onto a timeline and a day counter landing: a sequence plus a number, the blend keeps the held title"),
    "podcast-guest-p-M1": ("B", True, "a number masked, then shown: the same element flips state (a reveal)"),
    "podcast-guest-q-M1": ("C", False, "4 words that turn a calm message into a fight: a short sequence inside a talking moment, the blend keeps the face big"),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--queue", action="store_true")
    ap.add_argument("--queue-file", type=Path, default=QUEUE)
    a = ap.parse_args()
    queue = a.queue_file
    have = set(queue.read_text().splitlines()) if queue.exists() else set()
    lines, n = [], 0
    for f in sorted(glob.glob(str(SPECS / "*/*.json"))):
        # read as written (no remap): the variant is a copy of the spec and keeps its spelling
        S = json.loads(Path(f).read_text())
        sid = S["id"]
        if not S.get("card_only_moving") or "-anim" in sid or "-hook2" in sid or sid.endswith("-cardtest"):
            continue
        x, number, why = DIRECTION.get(sid, ("C", False, "no reading written for this keeper: the blend by default"))
        variants = [(x, "stays", False), (x + "t", "goes", False)] + ([(x + "d", "stays", True)] if number else [])
        for suffix, title, dark in variants:
            V = json.loads(json.dumps(S))
            V["id"] = f"{sid}-anim{suffix}"
            V["anim"], V["anim_title"], V["anim_dark"] = x, title, dark
            V["anim_why"] = why
            V["base_id"] = sid
            vp = SPECS / S["slug"] / f"{V['id']}.json"
            print(f"{V['id']}: direction {x}, title {title}, {'dark' if dark else 'light'}")
            if a.apply:
                vp.write_text(json.dumps(V, indent=2, ensure_ascii=False))
                n += 1
            lines.append(f"--page {PAGE} {vp}")
    if a.apply and a.queue:
        with queue.open("a") as q:
            for ln in lines:
                if ln not in have:
                    q.write(ln + "\n")
        print("queued", len(lines))
    print("variant specs written:", n)


if __name__ == "__main__":
    main()
