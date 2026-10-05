#!/usr/bin/env bash
#
# render_queue.sh, run several long jobs overnight, unattended, one at a time.
#
# WHAT IT IS FOR
# You have 3 videos to render and you want to go to bed. Starting all 3 is how
# you wake up to 3 dead jobs: 2 full encodes at once on a laptop is how the
# kernel ends up choosing which one to kill, and it always picks the biggest,
# which is always the encoder. So the queue is serial on purpose. One job runs,
# finishes, and only then does the next one start.
#
# Each job goes through render_detached.sh with the strict memory gate, so a job
# waits for headroom rather than starting into a swapping machine. Everything
# that wrapper does, every job here gets: its own process session, the keep
# awake, one retry, the 60 second status trail, the runaway guard.
#
# USAGE
#   render_queue.sh add <name> --watch <dir> -- <command...>   queue one job
#   render_queue.sh run                                        start, detached
#   render_queue.sh status                                     one line per job
#   render_queue.sh clear                                      empty the queue
#
#   render_queue.sh add ep-01 --watch out/ep-01 -- "python3 build.py ep-01"
#   render_queue.sh add ep-02 --watch out/ep-02 -- "python3 build.py ep-02"
#   render_queue.sh run
#
# BEFORE YOU RUN IT
# Close what you can spare. No script can clear the machine for you, and a
# machine left loaded is still the most common reason an overnight run is 3
# jobs in the morning instead of 3 finished files.
#
# ENV
#   RENDER_DIR         state and logs.   default ./.renders
#   RENDER_ROOT        job working dir.  default the current directory
#   RENDER_MIN_DISK_GB refuse below this. default 25
#   RENDER_LINT_GLOBS  pipeline scripts render_preflight.sh lints
#   RENDER_PREFLIGHT   optional command run before each job. Non-zero skips
#                      that job and says so in the log. Put your own checks
#                      here, the ones that would have caught your last dead
#                      render
#
# Before each job, render_preflight.sh runs (disk first, ffmpeg present, the
# -loop without -t lint, then RENDER_PREFLIGHT). A failed preflight skips that
# job and the queue moves on.
#
# FILES
#   $RENDER_DIR/queue/{jobs.tsv,done.txt,queue.log}
#
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
DETACHED="$HERE/render_detached.sh"
RENDER_DIR="${RENDER_DIR:-$PWD/.renders}"
RENDER_ROOT="${RENDER_ROOT:-$PWD}"
RENDER_MIN_DISK_GB="${RENDER_MIN_DISK_GB:-25}"
Q="$RENDER_DIR/queue"
mkdir -p "$Q"

usage() { sed -n '3,47p' "$0"; }

preflight() {  # 0 means go
  RENDER_ROOT="$RENDER_ROOT" RENDER_MIN_DISK_GB="$RENDER_MIN_DISK_GB" \
    "$HERE/render_preflight.sh" < /dev/null
}

is_done() { [ -f "$Q/done.txt" ] && grep -qxF "$1" "$Q/done.txt"; }

case "${1:-}" in
  add)
    shift
    name="${1:-}"; [ -z "$name" ] && { usage; exit 1; }
    shift
    printf '%s\t%s\n' "$name" "$*" >> "$Q/jobs.tsv"
    echo "queued $name"
    ;;

  run)
    [ -s "$Q/jobs.tsv" ] || { echo "queue is empty"; exit 1; }
    RENDER_DIR="$RENDER_DIR" RENDER_ROOT="$RENDER_ROOT" \
      "$DETACHED" start queue-runner --watch "$Q" -- "RENDER_GATE=strict '$HERE/render_queue.sh' _drain"
    ;;

  _drain)
    while IFS=$'\t' read -r name args; do
      [ -z "$name" ] && continue
      is_done "$name" && continue
      echo "$(date '+%F %T') preflight $name" >> "$Q/queue.log"
      if ! preflight >> "$Q/queue.log" 2>&1; then
        echo "$(date '+%F %T') $name SKIPPED, preflight failed" >> "$Q/queue.log"
        continue
      fi
      echo "$(date '+%F %T') start $name" >> "$Q/queue.log"
      # shellcheck disable=SC2086
      RENDER_GATE=strict RENDER_DIR="$RENDER_DIR" RENDER_ROOT="$RENDER_ROOT" \
        "$DETACHED" start "$name" $args < /dev/null >> "$Q/queue.log" 2>&1
      # stdin is taken off jobs.tsv above, or a job can eat the rest of the list
      # Serial by waiting on the exit file the wrapper writes. Waiting on a
      # process name instead is how 3 supervisors once matched each other and
      # each other's shells, and ran a stale job nobody asked for.
      while [ ! -s "$RENDER_DIR/$name/exit" ]; do sleep 60; done
      echo "$(date '+%F %T') $name finished exit=$(cat "$RENDER_DIR/$name/exit")" >> "$Q/queue.log"
      echo "$name" >> "$Q/done.txt"
    done < "$Q/jobs.tsv"
    echo "$(date '+%F %T') queue drained" >> "$Q/queue.log"
    if command -v osascript >/dev/null 2>&1; then
      osascript -e "display notification \"Overnight queue finished. See $Q/queue.log\" with title \"render\"" 2>/dev/null
    elif command -v notify-send >/dev/null 2>&1; then
      notify-send "render" "Overnight queue finished. See $Q/queue.log" 2>/dev/null
    fi
    ;;

  status)
    [ -s "$Q/jobs.tsv" ] || { echo "queue is empty"; exit 0; }
    while IFS=$'\t' read -r name args; do
      [ -z "$name" ] && continue
      if [ -s "$RENDER_DIR/$name/exit" ]; then
        echo "$name: exit $(cat "$RENDER_DIR/$name/exit")"
      elif [ -f "$RENDER_DIR/$name/pid" ] && kill -0 "$(cat "$RENDER_DIR/$name/pid")" 2>/dev/null; then
        echo "$name: RUNNING"
      else
        echo "$name: queued"
      fi
    done < "$Q/jobs.tsv"
    tail -3 "$Q/queue.log" 2>/dev/null
    ;;

  clear)
    : > "$Q/jobs.tsv"; : > "$Q/done.txt"
    echo "queue cleared, logs kept"
    ;;

  *) usage; exit 1 ;;
esac
