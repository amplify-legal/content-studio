#!/bin/bash
# lane_runner.sh: one supervisor for one lane of shorts renders. It reads its queue file, renders each line once,
# PAR at a time, and picks up lines appended while it runs.
#
#   start (detached, so it survives the conversation):
#     scripts/render_detached.sh start shorts-lane-podcast -- bash <this folder>/lane_runner.sh podcast
#     scripts/render_detached.sh start shorts-lane-tutorial -- bash <this folder>/lane_runner.sh tutorial
#   queue file:  <this folder>/queue-<lane>.txt     done file: done-<lane>.txt     log: lane-<lane>.log
#   line shapes:
#     <spec path> [--look <look>]                      a podcast or animated short through pipeline.py
#     --page <html> <spec path> [--look <look>]        the overlay from another looks page (anim_looks.html)
#     tut <spec path> --layout <A|B|C>                 a tutorial short through tutorial_look.py
#   a line starting with # is skipped; a line is rendered once (it is written to the done file before it starts).
#
# The rules it keeps, each learned on a real multi-day build (the method notes are in README.md):
#   - ONE supervisor per lane, one render each by default. A machine-wide render guard counts supervisors across every
#     session, so 2 lanes, 1 render each, is the shape that held; a second supervisor on the same lane doubles the load.
#   - running() counts only THIS runner's own jobs, so a render on the other lane never stalls this one.
#   - before each start, the free disk is read; under HOLD_GB the runner writes HELD.md and polls every 5 minutes.
#     Nothing is ever deleted to make room.
#   - never stop this runner with `render_detached.sh stop` while builds are in flight: that kills the whole process
#     group, the builds with it. To stop it cleanly, kill this supervisor's own bash pid, let its renders finish, or
#     kill each render's python by its own pid.
#   - a job frozen by a disk guard (SIGSTOP) is not hung: never kill or SIGCONT it. The pipeline counts a timeout only
#     while its child runs.
#   - no rm anywhere: lock and done files are written and appended, never removed.
LANE="${1:-podcast}"
B="$(cd "$(dirname "$0")" && pwd)"
Q="$B/queue-$LANE.txt"; DONE="$B/done-$LANE.txt"; LOG="$B/lane-$LANE.log"; HELD="$B/HELD.md"
HOLD_GB="${HOLD_GB:-25}"
touch "$Q" "$DONE"
stamp() { date +%H:%M:%S; }
free_gb() { df -g "$B" 2>/dev/null | tail -1 | awk '{print $4}'; }
par() { echo "${LANE_PAR:-1}"; }
running() { jobs -rp | wc -l | tr -d ' '; }
one() {
  local page=""
  if [ "$1" = "tut" ]; then
    shift
    local spec="$1"; shift
    local tag; tag="$(basename "$spec" .json)-tut${2:-}"
    echo "$(stamp) start $tag" >> "$LOG"
    (cd "$B" && PYTHONDONTWRITEBYTECODE=1 python3 "$B/tutorial_look.py" --build "$spec" "$@" --force > "$B/lane-$LANE-$tag.log" 2>&1)
    echo "$(stamp) done $tag rc=$?" >> "$LOG"
    return
  fi
  if [ "${1:-}" = "--page" ]; then page="$2"; shift 2; fi
  local spec="$1"; shift
  local tag; tag="$(basename "$spec" .json)"
  if [ "${1:-}" = "--look" ]; then tag="$tag-cmp-$2"; fi
  echo "$(stamp) start $tag" >> "$LOG"
  (cd "$B" && SHORTS_LOOKS_HTML="$page" PYTHONDONTWRITEBYTECODE=1 python3 "$B/pipeline.py" --build "$spec" "$@" --force > "$B/lane-$LANE-$tag.log" 2>&1)
  echo "$(stamp) done $tag rc=$?" >> "$LOG"
}
echo "$(stamp) lane $LANE up, pid $$" >> "$LOG"
idle=0
while :; do
  line=""
  while IFS= read -r l; do
    [ -z "$l" ] && continue
    case "$l" in \#*) continue;; esac
    if ! grep -qxF -- "$l" "$DONE"; then line="$l"; break; fi
  done < "$Q"
  if [ -z "$line" ]; then
    idle=$((idle+1))
    if [ "$idle" -ge 160 ]; then echo "$(stamp) queue empty 2 h, lane $LANE down" >> "$LOG"; wait; exit 0; fi
    sleep 45; continue
  fi
  idle=0
  while [ "$(running)" -ge "$(par)" ]; do sleep 20; done
  while [ "$(free_gb)" -lt "$HOLD_GB" ]; do
    printf '# HELD %s: %s GB free, floor %s GB; lane %s, next line waiting: %s. Nothing is deleted; polled every 5 min.\n' "$(date '+%d %b %H:%M')" "$(free_gb)" "$HOLD_GB" "$LANE" "$line" >> "$HELD"
    echo "$(stamp) held: $(free_gb) GB free" >> "$LOG"
    sleep 300
  done
  echo "$line" >> "$DONE"
  # shellcheck disable=SC2086
  one $line &
  sleep 5
done
