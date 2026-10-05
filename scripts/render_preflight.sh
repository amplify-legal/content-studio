#!/usr/bin/env bash
#
# render_preflight.sh, the checks that would have prevented every documented
# dead render, run before a long job starts. Exit 0 means go.
#
#   scripts/render_preflight.sh            run every check
#   RENDER_MIN_DISK_GB=40 scripts/render_preflight.sh
#
# What it checks, and why each one is here:
#   disk        a 25 minute 1080p pipeline needs about 20GB of scratch, and a
#               full disk plus memory pressure is what took the machine down
#               (a kernel panic, twice) during overnight renders. Free disk is
#               checked FIRST, because on a full disk the OS cannot even swap.
#   ffmpeg      present on PATH.
#   loop lint   any ffmpeg command with a "-loop" image input must carry an
#               output "-t". Without it ffmpeg encodes duplicate frames after
#               the video ends, forever, until the disk fills. This bug cost 13
#               hours of a night twice before it was a lint.
#   memory      informational. The render itself waits at its own memory gate,
#               but a queue should know what it is walking into.
#   custom      RENDER_PREFLIGHT, your own command. Non-zero refuses. Put the
#               check here that would have caught YOUR last dead render.
#
# ENV
#   RENDER_ROOT         project root the globs resolve from. default $PWD
#   RENDER_MIN_DISK_GB  refuse below this. default 25
#   RENDER_LINT_GLOBS   space separated globs of pipeline scripts to lint.
#                       default "content/videos/*/build/*.py
#                       .claude/skills/*/scripts/*.py scripts/*.py"
#   RENDER_PREFLIGHT    optional extra command
#
set -uo pipefail

RENDER_ROOT="${RENDER_ROOT:-$PWD}"
RENDER_MIN_DISK_GB="${RENDER_MIN_DISK_GB:-25}"
RENDER_LINT_GLOBS="${RENDER_LINT_GLOBS:-content/videos/*/build/*.py .claude/skills/*/scripts/*.py scripts/*.py}"
fail=0
say() { echo "preflight: $*"; }

# disk, first
free=$(df -Pk "$RENDER_ROOT" 2>/dev/null | awk 'NR==2{printf "%d", $4/1048576}')
if [ -z "$free" ]; then
  say "info could not read free disk for $RENDER_ROOT"
elif [ "$free" -lt "$RENDER_MIN_DISK_GB" ]; then
  say "FAIL disk ${free}GB free, below ${RENDER_MIN_DISK_GB}GB"
  say "     clear space before rendering. On macOS a local Time Machine snapshot"
  say "     can hold deleted files: check 'tmutil listlocalsnapshots /'"
  fail=1
else
  say "ok disk ${free}GB free"
fi

# ffmpeg
if command -v ffmpeg >/dev/null 2>&1; then say "ok ffmpeg present"
else say "FAIL ffmpeg not on PATH"; fail=1; fi

# memory, informational
if command -v memory_pressure >/dev/null 2>&1; then
  fp=$(memory_pressure 2>/dev/null | awk '/free percentage/{gsub(/%/,"",$5); print $5}')
  say "info memory ${fp:-?}% free (macOS memory_pressure)"
elif [ -r /proc/meminfo ]; then
  fp=$(awk '/^MemTotal/{t=$2} /^MemAvailable/{a=$2} END{if(t>0) printf "%d", a*100/t}' /proc/meminfo)
  say "info memory ${fp:-?}% available"
fi

# the runaway-tail lint
( cd "$RENDER_ROOT" && python3 - $RENDER_LINT_GLOBS ) <<'PY' || fail=1
import glob, re, sys
files = sorted({f for g in sys.argv[1:] for f in glob.glob(g)})
bad = []
for f in files:
    try:
        s = open(f, encoding="utf8", errors="replace").read()
    except OSError:
        continue
    # list-style commands: ["ffmpeg", ..., "-loop", "1", ...]
    for m in re.finditer(r'\[\s*["\']ffmpeg["\'].*?\]', s, re.S):
        blk = m.group(0)
        if re.search(r'["\']-loop["\']', blk) and not re.search(r'["\']-t["\']', blk) \
           and not re.search(r'["\']-t["\']', s[m.end():m.end() + 400]):
            bad.append(f)
    # string-style commands: "ffmpeg ... -loop 1 ..."
    for line in s.splitlines():
        if "ffmpeg" in line and re.search(r"-loop\s+1\b", line) and not re.search(r"\s-t\s", line):
            bad.append(f)
if bad:
    print("preflight: FAIL -loop input without an output -t in:")
    for f in sorted(set(bad)):
        print("     ", f)
    sys.exit(1)
print(f"preflight: ok no -loop input without -t ({len(files)} scripts linted)")
PY

# custom
if [ -n "${RENDER_PREFLIGHT:-}" ]; then
  if bash -c "$RENDER_PREFLIGHT"; then say "ok custom check"
  else say "FAIL custom check"; fail=1; fi
fi

[ "$fail" -eq 0 ] && say "PASS" || say "REFUSED"
exit "$fail"
