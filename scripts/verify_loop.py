#!/usr/bin/env python3
"""Render, check, repair, render again, until the cut is right or it cannot be.

The economics this exists for, in one line: overnight, machine time is free and
abundant and tokens are neither. So the checking and most of the repairing are a
script, and a model is woken only for what the script cannot settle.

Three tiers, and the loop never lets one pretend to be another.

  auto    the check battery found it and the repair table can fix it. The loop
          applies the repair, rebuilds only what changed, and goes round again.
          Costs machine time and zero tokens.
  model   the loop cannot repair it safely. It stops and leaves a verdict small
          enough that a waking session reads it in a few thousand tokens rather
          than re-reading a night of logs.
  human   taste, or a claim about the content. Neither tier below rules on it.
          It goes on the morning queue.

Green is not done. Green means the file is worth a person's watch.

Convention over configuration, so somebody who is not the author can use it.
Point it at a piece folder holding build/{build_cut,finalize,verify,autofix}.py
and it runs them in that order:

  python3 scripts/verify_loop.py content/videos/<slug> --max-iterations 4 --deep
  python3 scripts/verify_loop.py content/videos/<slug> --deadline 07:00
  python3 scripts/verify_loop.py content/videos/<slug> --status
  python3 scripts/verify_loop.py content/videos/<slug> --scaffold   write stub files
  python3 scripts/verify_loop.py --selftest                         offline proof

The contract each file keeps (content/reference/verify-loop.md has the detail):

  build_cut.py   builds the cut. Never rewrites unchanged output.
  finalize.py    burns captions and audio into the finished file in <edit-dir>.
  verify.py      takes --iteration N [--deep], writes <edit-dir>/verify/verdict.json:
                   {"status": "green"|"red",
                    "tiers": {"auto": n, "model": n, "human": n},
                    "loudness_lufs": -14.1,
                    "findings": [{"check", "tier", "detail", "fix", "args", "rebuild"}]}
  autofix.py     exposes apply(findings, iteration) -> (scope or None, [changes])
                 and prepare_rebuild(scope) -> [removed]. Repairs are DATA written
                 to build/overrides.json, never edits to a build script.

State lives in <edit-dir>/verify/loop-state.json and is deliberately small: a
waking session should read that file and the verdict, nothing else. The edit
dir defaults to raw/edit inside the piece folder; change it with --edit-dir.

Paths are resolved from the current working directory (your project root),
and every build step runs from there, so write build scripts with paths
relative to the project root or to their own file.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path

FREE_MB_FLOOR = 900          # do not start an encode into a thrashing machine
PRESSURE_FREE_FLOOR = 20.0   # macOS's own free-percentage figure, trusted first
AVAILABLE_PCT_FLOOR = 20.0   # Linux MemAvailable as a percentage, same role
LOAD_CEILING = 24.0          # a quiet machine is quiet whatever free pages say
MEMORY_WAIT_MAX = int(os.environ.get("VERIFY_LOOP_MEMORY_WAIT_MAX", "900"))
BUILD_FILES = ("build_cut.py", "finalize.py", "verify.py", "autofix.py")


def now():
    return datetime.now().strftime("%H:%M:%S")


def log(state_dir, msg):
    line = f"{now()} {msg}"
    print(line, flush=True)
    with open(state_dir / "loop.log", "a") as fh:
        fh.write(line + "\n")


# ---------------------------------------------------------------------------
# The memory gate. Every reading here fails open: a gate that cannot measure
# must never block the night.
# ---------------------------------------------------------------------------

def free_mb():
    """Free plus speculative pages on macOS (vm_stat). The least trusted signal."""
    try:
        out = subprocess.run(["vm_stat"], capture_output=True, text=True).stdout
        page = 16384
        free = spec = 0
        for line in out.splitlines():
            if "page size of" in line:
                page = int(line.split("page size of")[1].split()[0])
            if line.startswith("Pages free"):
                free = int(line.split()[-1].rstrip("."))
            if line.startswith("Pages speculative"):
                spec = int(line.split()[-1].rstrip("."))
        return (free + spec) * page // (1024 * 1024)
    except Exception:
        return FREE_MB_FLOOR


def pressure_free_pct():
    """The operating system's own reading of available memory, the honest one.

    Measured once with 2 renders competing: vm_stat reported 66MB of free pages
    while macOS's `memory_pressure` reported 56% free system-wide. Free pages
    counts only what has been handed back to the OS, and the OS holds the rest
    as cache, so on a busy machine it reads near zero permanently and any gate
    built on it is a stopwatch rather than a check. On Linux the equivalent is
    MemAvailable in /proc/meminfo.
    """
    try:
        out = subprocess.run(["memory_pressure"], capture_output=True,
                             text=True, timeout=15).stdout
        for line in out.splitlines():
            if "free percentage" in line.lower():
                return float(line.rsplit(":", 1)[1].strip().rstrip("%"))
    except Exception:
        pass
    try:
        info = {}
        for line in Path("/proc/meminfo").read_text().splitlines():
            k, v = line.split(":", 1)
            info[k] = int(v.split()[0])
        if info.get("MemTotal"):
            return 100.0 * info.get("MemAvailable", 0) / info["MemTotal"]
    except Exception:
        pass
    return None


def load_avg():
    try:
        return os.getloadavg()[0]
    except Exception:
        return 0.0


def gate_open():
    """Any one signal is enough, in order of trust: the OS's own available
    figure, then a quiet load, then free pages as a last resort."""
    pct = pressure_free_pct()
    if pct is not None:
        return pct >= PRESSURE_FREE_FLOOR
    return free_mb() >= FREE_MB_FLOOR or load_avg() <= LOAD_CEILING


def wait_for_memory(state_dir):
    """A render started into a thrashing machine takes all night and finishes wrong.

    One measured night: dozens of resident sessions, almost no free memory, a
    load average over 200, and a 15 minute encode took 30. The gate waits,
    then goes anyway rather than stalling the whole night.
    """
    waited = 0
    while not gate_open() and waited < MEMORY_WAIT_MAX:
        if waited == 0:
            log(state_dir, f"gate: {pressure_free_pct()}% available, "
                           f"{free_mb()}MB pages free, load {load_avg():.1f}")
        time.sleep(30)
        waited += 30
    log(state_dir, f"gate passed after {waited}s: {pressure_free_pct()}% available, "
                   f"load {load_avg():.1f}")


# ---------------------------------------------------------------------------

def run_step(state_dir, label, cmd, cwd):
    log(state_dir, f"{label}: starting")
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd))
    dt = time.time() - t0
    with open(state_dir / "loop.log", "a") as fh:
        fh.write(p.stdout[-6000:] + "\n" + p.stderr[-4000:] + "\n")
    log(state_dir, f"{label}: exit {p.returncode} in {dt:.0f}s")
    return p.returncode, dt


def newest_output(edit, master_name):
    """The finished cut, whatever the piece chose to call it.

    Found rather than named, so the loop stays a convention and a piece is free
    to name its own deliverable.
    """
    cands = [p for p in edit.glob("*.mp4") if p.name != master_name]
    return max(cands, key=lambda p: p.stat().st_mtime) if cands else None


def write_state(state_dir, state):
    (state_dir / "loop-state.json").write_text(json.dumps(state, indent=2))


# ---------------------------------------------------------------------------
# --scaffold: stub files that satisfy the contract, for a piece to fill in.
# Never overwrites a file that exists.
# ---------------------------------------------------------------------------

SCAFFOLD = {
    "build_cut.py": '''"""Build the cut: the edit list, the segment renders, the concat, the captions.

Contract: never rewrite unchanged output. Write to a temp file and replace the
real one only when the bytes differ, or every freshness check downstream lies.
"""
print("build_cut: nothing to build yet, fill this in")
''',
    "finalize.py": '''"""Burn the captions and the audio into the finished file in the edit dir.

Read build/overrides.json for loudness and quality repairs the loop recorded.
Any -loop 1 image input carries an explicit -t.
"""
print("finalize: nothing to render yet, fill this in")
''',
    "verify.py": '''"""The check battery. Writes <edit-dir>/verify/verdict.json.

Each finding names its own tier (auto, model, human), a rebuild scope (burn,
captions+burn, segments+burn), and for auto findings a fix the repair table
knows plus its args. --deep re-reads the finished artifact (re-transcribe it).
"""
import argparse, json
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--iteration", type=int, default=1)
ap.add_argument("--deep", action="store_true")
args = ap.parse_args()

VERIFY = Path(__file__).resolve().parent.parent / "raw/edit/verify"
VERIFY.mkdir(parents=True, exist_ok=True)
findings = []   # append {"check", "tier", "detail", "fix", "args", "rebuild"}
tiers = {t: sum(f["tier"] == t for f in findings) for t in ("auto", "model", "human")}
(VERIFY / "verdict.json").write_text(json.dumps({
    "status": "green" if not findings else "red",
    "tiers": tiers, "loudness_lufs": None, "findings": findings}, indent=2))
''',
    "autofix.py": '''"""The bounded repair table. What the loop may change on its own, as DATA.

Repairs land in build/overrides.json, never as edits to a build script. Every
entry is deterministic and bounded; anything needing judgment escalates.
"""
import json
from pathlib import Path

BUILD = Path(__file__).resolve().parent
OVERRIDES = BUILD / "overrides.json"
MAX_APPLICATIONS = 3          # the same repair is never tried a fourth time
ORDER = ["burn", "captions+burn", "segments+burn"]


def load():
    if OVERRIDES.exists():
        return json.loads(OVERRIDES.read_text())
    return {"applied": {}, "log": []}


def apply(findings, iteration):
    """Apply every auto-tier finding. Returns (widest rebuild or None, changes)."""
    o, changed, rebuilds = load(), [], set()
    for f in findings:
        if f.get("tier") != "auto" or not f.get("fix"):
            continue
        key = f"{f['fix']}:{json.dumps(f.get('args', {}), sort_keys=True)}"
        if o["applied"].get(key, 0) >= MAX_APPLICATIONS:
            f["tier"] = "model"
            f["detail"] += " (repair applied 3 times and the check still fails)"
            continue
        # if f["fix"] == "reloudnorm": o["loudnorm"] = {"two_pass": True, **f["args"]}
        # ... one bounded branch per fix your verify.py can name ...
        continue
    if changed:
        o["log"].append({"iteration": iteration, "changed": changed})
        OVERRIDES.write_text(json.dumps(o, indent=2))
    widest = max(rebuilds, key=ORDER.index) if rebuilds else None
    return widest, changed


def prepare_rebuild(scope):
    """Remove only what the scope names, so only that is made again."""
    return []
''',
}


def scaffold(ep):
    build = ep / "build"
    build.mkdir(parents=True, exist_ok=True)
    for name, body in SCAFFOLD.items():
        p = build / name
        if p.exists():
            print(f"kept      {p}")
        else:
            p.write_text(body)
            print(f"wrote     {p}")
    return 0


# ---------------------------------------------------------------------------

def run_loop(ep, args, cwd):
    build = ep / "build"
    edit = (ep / args.edit_dir).resolve()
    state_dir = edit / "verify"
    state_dir.mkdir(parents=True, exist_ok=True)

    if args.status:
        p = state_dir / "loop-state.json"
        print(p.read_text() if p.exists() else "no loop has run on this piece")
        return 0

    for name in BUILD_FILES:
        if not (build / name).exists():
            print(f"{ep.name} has no build/{name}. The loop needs all four. "
                  f"--scaffold writes stubs.")
            return 2

    sys.path.insert(0, str(build))
    sys.modules.pop("autofix", None)
    import autofix

    deadline = None
    if args.deadline:
        h, m = (int(x) for x in args.deadline.split(":"))
        deadline = datetime.now().replace(hour=h, minute=m, second=0, microsecond=0)
        if deadline < datetime.now():
            # timedelta, not day+1, which throws on the last day of a month
            deadline += timedelta(days=1)

    state = {
        "piece": ep.name,
        "started": datetime.now().isoformat(timespec="seconds"),
        "max_iterations": args.max_iterations,
        "deadline": args.deadline,
        "deep": args.deep,
        "iterations": [],
        "outcome": "running",
        "for_the_model": [],
        "for_the_human": [],
    }
    write_state(state_dir, state)
    log(state_dir, f"=== verify loop on {ep.name}, "
                   f"max {args.max_iterations} iterations, deep={args.deep}")

    for i in range(1, args.max_iterations + 1):
        if deadline and datetime.now() >= deadline:
            state["outcome"] = "deadline"
            log(state_dir, f"deadline {args.deadline} reached, stopping before iteration {i}")
            break

        if not args.no_gate:
            wait_for_memory(state_dir)
        it = {"n": i, "started": now()}

        rc, dt = run_step(state_dir, f"[{i}] build",
                          [sys.executable, str(build / "build_cut.py")], cwd)
        it["build_s"] = round(dt)
        if rc != 0:
            it["outcome"] = "build failed"
            state["iterations"].append(it)
            state["outcome"] = "build_failed"
            state["for_the_model"].append("build_cut.py exited non-zero, see loop.log")
            break

        # Do not re-encode a file that is already newer than everything that
        # makes it. On the first iteration the finished file usually exists
        # because a detached render just made it, and burning it again is a
        # whole pass spent to arrive at the same bytes.
        final = newest_output(edit, args.master)
        inputs = [edit / args.master, edit / args.captions, build / "overrides.json"]
        fresh = (final and final.exists() and
                 all(not p.exists() or p.stat().st_mtime <= final.stat().st_mtime
                     for p in inputs))
        if fresh:
            log(state_dir, f"[{i}] render: skipped, {final.name} is newer than "
                           f"the master, the captions and the overrides")
            it["render_s"] = 0
            it["render"] = "skipped, already current"
        else:
            rc, dt = run_step(state_dir, f"[{i}] render",
                              [sys.executable, str(build / "finalize.py")], cwd)
            it["render_s"] = round(dt)

        verdict_path = state_dir / "verdict.json"
        if verdict_path.exists():
            # A stale verdict from the last iteration must never pass for this one.
            verdict_path.replace(state_dir / "verdict.previous.json")
        vcmd = [sys.executable, str(build / "verify.py"), "--iteration", str(i)]
        if args.deep:
            vcmd.append("--deep")
        rc, dt = run_step(state_dir, f"[{i}] verify", vcmd, cwd)
        it["verify_s"] = round(dt)

        if not verdict_path.exists():
            it["outcome"] = "no verdict"
            state["iterations"].append(it)
            state["outcome"] = "verify_failed"
            state["for_the_model"].append("verify.py wrote no verdict, see loop.log")
            break

        verdict = json.loads(verdict_path.read_text())
        findings = verdict.get("findings", [])
        it["status"] = verdict.get("status")
        it["tiers"] = verdict.get("tiers")
        it["loudness_lufs"] = verdict.get("loudness_lufs")

        if verdict.get("status") == "green":
            it["outcome"] = "green"
            state["iterations"].append(it)
            state["outcome"] = "green"
            log(state_dir, f"[{i}] GREEN. The cut passed every check. "
                           f"Green is not done: it is now worth a watch.")
            break

        scope, changed = autofix.apply(findings, i)
        it["repairs"] = changed
        it["rebuild"] = scope

        if not scope:
            # Nothing in the repair table applies, so every finding is above
            # the loop's tier. Stop rather than burn a night re-rendering the
            # same file.
            it["outcome"] = "escalated"
            state["iterations"].append(it)
            state["outcome"] = "escalated"
            state["for_the_model"] = [
                f"{f['check']}: {f['detail']}" for f in findings if f.get("tier") == "model"]
            state["for_the_human"] = [
                f"{f['check']}: {f['detail']}" for f in findings if f.get("tier") == "human"]
            log(state_dir, f"[{i}] escalating: {len(state['for_the_model'])} for the model, "
                           f"{len(state['for_the_human'])} for the human")
            break

        removed = autofix.prepare_rebuild(scope)
        it["outcome"] = f"repaired, rebuilding {scope}"
        it["removed"] = len(removed)
        log(state_dir, f"[{i}] repaired: {'; '.join(changed)}. Rebuilding {scope} "
                       f"({len(removed)} files removed)")
        state["iterations"].append(it)
        write_state(state_dir, state)
    else:
        state["outcome"] = "iterations_exhausted"

    state["finished"] = datetime.now().isoformat(timespec="seconds")
    write_state(state_dir, state)
    log(state_dir, f"=== loop finished: {state['outcome']}")
    print(json.dumps({k: v for k, v in state.items() if k != "iterations"}, indent=2))
    return 0 if state["outcome"] == "green" else 1


# ---------------------------------------------------------------------------
# --selftest: a fake piece in a temp folder, no ffmpeg, no network. Proves the
# 3 outcomes that matter: green, an auto repair then green, and an escalation
# that stops instead of looping.
# ---------------------------------------------------------------------------

_FAKE_VERIFY = '''
import argparse, json
from pathlib import Path
ap = argparse.ArgumentParser(); ap.add_argument("--iteration", type=int); ap.add_argument("--deep", action="store_true")
a = ap.parse_args()
B = Path(__file__).resolve().parent
V = B.parent / "raw/edit/verify"; V.mkdir(parents=True, exist_ok=True)
mode = (B / "MODE").read_text().strip()
o = json.loads((B / "overrides.json").read_text()) if (B / "overrides.json").exists() else {}
findings = []
if mode == "repair" and not o.get("loudnorm"):
    findings.append({"check": "loudness", "tier": "auto", "detail": "-16.4 LUFS against -14",
                     "fix": "reloudnorm", "args": {"measured": -16.4}, "rebuild": "burn"})
if mode == "escalate":
    findings.append({"check": "join", "tier": "human", "detail": "does the join at 12.3s sound right", "rebuild": "burn"})
    findings.append({"check": "av_drift", "tier": "model", "detail": "0.11s drift", "rebuild": "segments+burn"})
tiers = {t: sum(f["tier"] == t for f in findings) for t in ("auto", "model", "human")}
(V / "verdict.json").write_text(json.dumps({"status": "green" if not findings else "red",
    "tiers": tiers, "loudness_lufs": -14.0, "findings": findings}))
'''

_FAKE_AUTOFIX = '''
import json
from pathlib import Path
B = Path(__file__).resolve().parent
OV = B / "overrides.json"
def apply(findings, iteration):
    o = json.loads(OV.read_text()) if OV.exists() else {"applied": {}, "log": []}
    changed, rebuilds = [], set()
    for f in findings:
        if f["tier"] == "auto" and f.get("fix") == "reloudnorm":
            o["loudnorm"] = {"two_pass": True, **f["args"]}
            changed.append("loudnorm set to a measured two-pass"); rebuilds.add(f["rebuild"])
    if changed:
        o["log"].append({"iteration": iteration, "changed": changed}); OV.write_text(json.dumps(o))
    return (max(rebuilds, key=["burn", "captions+burn", "segments+burn"].index) if rebuilds else None), changed
def prepare_rebuild(scope):
    f = B.parent / "raw/edit/final.mp4"
    if f.exists():
        f.unlink(); return [f.name]
    return []
'''

_FAKE_FINALIZE = '''
from pathlib import Path
E = Path(__file__).resolve().parent.parent / "raw/edit"; E.mkdir(parents=True, exist_ok=True)
(E / "final.mp4").write_bytes(b"not really a video")
'''


def selftest():
    class A:
        max_iterations = 4
        deadline = None
        deep = False
        status = False
        no_gate = True
        edit_dir = "raw/edit"
        master = "master-nosubs.mp4"
        captions = "captions.ass"

    want = {"green": ("green", 0), "repair": ("green", 0), "escalate": ("escalated", 1)}
    ok = True
    with tempfile.TemporaryDirectory() as td:
        for mode, (outcome, rc_want) in want.items():
            ep = Path(td) / f"piece-{mode}"
            b = ep / "build"
            b.mkdir(parents=True)
            (b / "build_cut.py").write_text("print('built')\n")
            (b / "finalize.py").write_text(_FAKE_FINALIZE)
            (b / "verify.py").write_text(_FAKE_VERIFY)
            (b / "autofix.py").write_text(_FAKE_AUTOFIX)
            (b / "MODE").write_text(mode)
            sys.path[:] = [p for p in sys.path if not p.endswith("/build")]
            rc = run_loop(ep, A, cwd=Path(td))
            state = json.loads((ep / "raw/edit/verify/loop-state.json").read_text())
            good = state["outcome"] == outcome and rc == rc_want
            if mode == "repair":
                good = good and len(state["iterations"]) == 2
            if mode == "escalate":
                good = good and state["for_the_human"] and state["for_the_model"]
            print(f"{'PASS' if good else 'FAIL'}  {mode}: outcome {state['outcome']}, "
                  f"{len(state['iterations'])} iteration(s), exit {rc}")
            ok = ok and good
    print("\nselftest:", "all pass" if ok else "FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("piece", nargs="?", help="path to the piece folder")
    ap.add_argument("--max-iterations", type=int, default=4)
    ap.add_argument("--deadline", default=None,
                    help="HH:MM local. The loop starts no new iteration past it")
    ap.add_argument("--deep", action="store_true",
                    help="ask verify.py to re-read the finished file each iteration")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--scaffold", action="store_true",
                    help="write stub build files that satisfy the contract")
    ap.add_argument("--edit-dir", default="raw/edit",
                    help="where the master, captions and finished file live, "
                         "relative to the piece folder (default raw/edit)")
    ap.add_argument("--master", default="master-nosubs.mp4",
                    help="the captionless master's filename inside the edit dir")
    ap.add_argument("--captions", default="captions.ass",
                    help="the caption file's name inside the edit dir")
    ap.add_argument("--no-gate", action="store_true", help="skip the memory gate")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    if not args.piece:
        ap.error("give a piece folder, or --selftest")

    cwd = Path.cwd()
    ep = (cwd / args.piece).resolve()
    if args.scaffold:
        return scaffold(ep)
    return run_loop(ep, args, cwd)


if __name__ == "__main__":
    sys.exit(main())
