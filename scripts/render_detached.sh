#!/usr/bin/env bash
#
# render_detached.sh, run a long job OUTSIDE the conversation so nothing your
# session does can kill it.
#
# WHAT IT IS FOR
# A render that takes 40 minutes does not survive being a child of a chat. The
# session ends, you press stop by accident, the harness restarts, the laptop
# sleeps, and the job dies silently with a partial file and no error. You find
# out in the morning. This wrapper gives the job its own process session, keeps
# the machine awake, watches it, retries once, and leaves a log and a status
# trail you can read from any other session.
#
# Every behaviour in here exists because a render died of it:
#   own process session   a job owned by a conversation dies with the conversation
#   keep-awake            a sleeping laptop stops the encode and does not resume it
#   memory gate           a render started into a swapping machine is the one the
#                         kernel picks to kill. Wait for headroom, then go
#   runaway guard         a still image looped into ffmpeg with no output length
#                         encodes duplicate frames forever, growing until the
#                         machine dies. Any watched file past the size ceiling
#                         gets its writer an interrupt so the file closes valid
#   status every 60s      "is it working" is answered by the output file growing,
#                         never by the CPU meter
#   one retry             pipeline steps are idempotent, so a transient failure
#                         is worth one more attempt before you lose the night
#
# USAGE
#   render_detached.sh start <name> --watch <dir> -- <command...>
#   render_detached.sh status <name>
#   render_detached.sh stop <name>      stops the whole process group
#   render_detached.sh tail <name>
#   render_detached.sh list
#
#   render_detached.sh start myvideo --watch out -- "python3 build.py"
#
# <dir> is the folder the job writes into. It is watched for growth and for the
# runaway guard. The command runs from RENDER_ROOT, so write it with paths
# relative to that, the same way every time.
#
# STOPPING A JOB
# Always `stop <name>`, never a kill of the pid in the folder. The pid file is
# the supervisor; the encoder is a grandchild in the same process group. Killing
# only the supervisor once left 3 encoders alive, all writing one output file,
# and the pass crawled at a tenth of its speed. `stop` kills the group and
# writes the exit file, so anything waiting on that file ends too.
#
# STARTED FROM A SCHEDULER
# If a scheduler (launchd, systemd, cron wrapper) starts this script and exits
# within a second, some schedulers kill every process left in the job's group
# before python reaches setsid. On macOS launchd the fix is
# <key>AbandonProcessGroup</key><true/> in the agent's plist. Either way, check
# 15 seconds later that the runner pid is alive and that its status file exists.
#
# ENV
#   RENDER_DIR         state and logs.      default ./.renders
#   RENDER_ROOT        job working dir.     default the current directory
#   RENDER_GATE        strict = wait for memory however long it takes
#   RENDER_GATE_MAX    minutes to wait.     default 30
#   RENDER_MAX_BYTES   runaway ceiling.     default 4294967296 (4GB)
#   RENDER_GUARD_PROC  encoder to interrupt on a runaway. default ffmpeg
#   RENDER_PREHOOK     command run once before the job (a cleanup, a reap)
#   RENDER_PAUSE_CHECK optional command. Exit 0 means "renders must wait now"
#                      (a screen recording is live, a memory brake is on), and
#                      start refuses with exit 75. Unset means never pause
#
# FILES
#   $RENDER_DIR/<name>/{job,watch,run.log,status,pid,exit}
#
set -uo pipefail

RENDER_DIR="${RENDER_DIR:-$PWD/.renders}"
RENDER_ROOT="${RENDER_ROOT:-$PWD}"
RENDER_GATE_MAX="${RENDER_GATE_MAX:-30}"
RENDER_MAX_BYTES="${RENDER_MAX_BYTES:-4294967296}"
RENDER_GUARD_PROC="${RENDER_GUARD_PROC:-ffmpeg}"
SELF="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"

usage() { sed -n '3,66p' "$0"; }

# ---------------------------------------------------------------------------
# Portability helpers. macOS and Linux disagree about every one of these, and a
# render script that only runs on one of them is half a script.
# ---------------------------------------------------------------------------

filesize() {  # bytes of $1, or 0
  if stat -f %z "$1" >/dev/null 2>&1; then stat -f %z "$1"
  elif stat -c %s "$1" >/dev/null 2>&1; then stat -c %s "$1"
  else echo 0; fi
}

newest_file() {  # most recently touched file directly inside $1, or empty
  local f newest=""
  for f in "$1"/*; do
    [ -f "$f" ] || continue
    if [ -z "$newest" ] || [ "$f" -nt "$newest" ]; then newest="$f"; fi
  done
  printf '%s' "$newest"
}

loadavg1() {  # 1-minute load average
  if [ -r /proc/loadavg ]; then cut -d' ' -f1 /proc/loadavg
  elif command -v sysctl >/dev/null 2>&1; then
    sysctl -n vm.loadavg 2>/dev/null | tr -d '{}' | awk '{print $1}'
  else echo "?"; fi
}

free_pct() {  # percent of memory actually available, or empty when unknown
  if command -v memory_pressure >/dev/null 2>&1; then
    memory_pressure 2>/dev/null | awk '/free percentage/{gsub(/%/,"",$5); print $5}'
  elif [ -r /proc/meminfo ]; then
    awk '/^MemTotal/{t=$2} /^MemAvailable/{a=$2} END{if(t>0) printf "%d", a*100/t}' /proc/meminfo
  fi
}

swap_pct() {  # percent of swap in use, or empty when unknown
  if command -v sysctl >/dev/null 2>&1 && sysctl -n vm.swapusage >/dev/null 2>&1; then
    sysctl -n vm.swapusage | awk '{gsub(/M/,"",$3); gsub(/M/,"",$6); if($3>0) printf "%d", $6*100/$3}'
  elif [ -r /proc/meminfo ]; then
    awk '/^SwapTotal/{t=$2} /^SwapFree/{f=$2} END{if(t>0) printf "%d", (t-f)*100/t; else print 0}' /proc/meminfo
  fi
}

notify() {  # best effort desktop notice, silent when there is no way to send one
  if command -v osascript >/dev/null 2>&1; then
    osascript -e "display notification \"$1\" with title \"render\"" 2>/dev/null
  elif command -v notify-send >/dev/null 2>&1; then
    notify-send "render" "$1" 2>/dev/null
  fi
  return 0
}

# ---------------------------------------------------------------------------
# The monitor. Runs beside the job, writes one status line a minute, and kills
# a runaway before it fills the disk.
# ---------------------------------------------------------------------------

monitor() {
  local D="$1" WATCH="$2" start newest sz
  start=$(date +%s)
  while :; do
    newest="$(newest_file "$WATCH")"
    sz=0
    [ -n "$newest" ] && sz=$(filesize "$newest")
    printf '%s elapsed=%ss load=%s free=%s%% swap=%s%% newest=%s bytes=%s\n' \
      "$(date '+%H:%M:%S')" "$(( $(date +%s) - start ))" "$(loadavg1)" \
      "$(free_pct)" "$(swap_pct)" "$(basename "${newest:-none}")" "$sz" >> "$D/status"

    # Runaway guard. Nothing this pipeline makes is legitimately this big. A
    # file past the ceiling is an encoder looping a still frame with no output
    # length set. Interrupt rather than kill, so the container closes valid.
    if [ "${sz:-0}" -gt "$RENDER_MAX_BYTES" ] && command -v lsof >/dev/null 2>&1; then
      for p in $(pgrep -x "$RENDER_GUARD_PROC" 2>/dev/null); do
        if lsof -p "$p" 2>/dev/null | grep -qF "$(basename "$newest")"; then
          echo "$(date '+%H:%M:%S') RUNAWAY: $newest at $sz bytes, interrupting $RENDER_GUARD_PROC $p" >> "$D/status"
          kill -INT "$p" 2>/dev/null
        fi
      done
    fi
    sleep 60
  done
}

# ---------------------------------------------------------------------------
# The supervised run. Started detached by `start`; never called by hand.
# ---------------------------------------------------------------------------

supervised_run() {
  local D="$1" WATCH JOB rc attempt i sw fp waited
  WATCH="$(cat "$D/watch")"
  JOB="$(cat "$D/job")"
  cd "$RENDER_ROOT" || exit 1

  monitor "$D" "$WATCH" &
  local MON=$!
  # shellcheck disable=SC2064
  trap "kill $MON 2>/dev/null" EXIT

  if [ -n "${RENDER_PREHOOK:-}" ]; then
    echo "=== prehook $(date)" >> "$D/run.log"
    bash -c "$RENDER_PREHOOK" >> "$D/run.log" 2>&1 || true
  fi

  # Memory gate. A long encode started into a machine that is already swapping
  # is the process the kernel kills first, so wait for headroom instead. Free
  # memory is the signal, not swap used: an operating system keeps swap
  # allocated long after the pressure is gone, so swap alone holds the gate
  # shut on a machine that is actually fine.
  local MAXW="$RENDER_GATE_MAX"
  [ "${RENDER_GATE:-}" = "strict" ] && MAXW=100000
  i=0; waited=0
  while [ "$i" -lt "$MAXW" ]; do
    i=$((i+1))
    fp="$(free_pct)"; sw="$(swap_pct)"
    [ -z "$fp" ] && [ -z "$sw" ] && break          # cannot measure, do not block
    [ "${fp:-0}" -ge 25 ] && break
    [ -n "$sw" ] && [ "${sw:-100}" -lt 85 ] && break
    waited=1
    echo "$(date +%T) memory gate: free ${fp:-?}% below 25% and swap ${sw:-?}% at or above 85%, waiting ($i/$MAXW)" >> "$D/run.log"
    [ $((i % 15)) -eq 1 ] && notify "$(basename "$D") is waiting on memory. Close what you can spare."
    sleep 60
  done
  [ "$waited" -eq 1 ] && echo "$(date +%T) memory gate released or timed out: free $(free_pct)%, swap $(swap_pct)%" >> "$D/run.log"

  local CAFF=""
  command -v caffeinate >/dev/null 2>&1 && CAFF="caffeinate -i -s"

  rc=1
  attempt=1
  while [ "$attempt" -le 2 ]; do
    echo "=== attempt $attempt $(date)" >> "$D/run.log"
    # shellcheck disable=SC2086
    $CAFF bash -c "$JOB" >> "$D/run.log" 2>&1
    rc=$?
    echo "=== exit $rc $(date)" >> "$D/run.log"
    [ "$rc" -eq 0 ] && break
    attempt=$((attempt+1))
    [ "$attempt" -le 2 ] && sleep 60
  done

  kill "$MON" 2>/dev/null
  echo "$rc" > "$D/exit"
  notify "$(basename "$D") finished with exit $rc"
}

# ---------------------------------------------------------------------------

cmd="${1:-}"
case "$cmd" in
  start)
    name="${2:-}"; [ -z "$name" ] && { usage; exit 1; }
    if [ -n "${RENDER_PAUSE_CHECK:-}" ] && bash -c "$RENDER_PAUSE_CHECK" >/dev/null 2>&1; then
      echo "renders are paused (RENDER_PAUSE_CHECK says so). Start again when it clears."
      exit 75
    fi
    shift 2
    WATCH="."
    [ "${1:-}" = "--watch" ] && { WATCH="$2"; shift 2; }
    [ "${1:-}" = "--" ] && shift
    JOB="$*"
    [ -z "$JOB" ] && { echo "no command given"; exit 1; }

    D="$RENDER_DIR/$name"; mkdir -p "$D"
    if [ -f "$D/pid" ] && kill -0 "$(cat "$D/pid")" 2>/dev/null; then
      echo "already running: pid $(cat "$D/pid")"; exit 0
    fi
    : > "$D/exit"    # emptied, not deleted: an empty exit file means "not finished"
    printf '%s' "$JOB" > "$D/job"
    printf '%s' "$WATCH" > "$D/watch"

    # nohup survives the parent exiting; setsid puts the job in its own process
    # session so nothing that signals the conversation's process group reaches
    # it. macOS ships no setsid binary, so python does it in one line.
    RENDER_DIR="$RENDER_DIR" RENDER_ROOT="$RENDER_ROOT" \
    RENDER_GATE="${RENDER_GATE:-}" RENDER_GATE_MAX="$RENDER_GATE_MAX" \
    RENDER_MAX_BYTES="$RENDER_MAX_BYTES" RENDER_GUARD_PROC="$RENDER_GUARD_PROC" \
    RENDER_PREHOOK="${RENDER_PREHOOK:-}" \
    nohup python3 -c 'import os,sys; os.setsid(); os.execv(sys.argv[1], sys.argv[1:])' \
      "$SELF" _run "$name" > /dev/null 2>&1 &
    echo $! > "$D/pid"
    disown 2>/dev/null || true
    echo "started $name (pid $(cat "$D/pid"))"
    echo "log $D/run.log"
    ;;

  _run)
    name="${2:-}"; [ -z "$name" ] && exit 1
    supervised_run "$RENDER_DIR/$name"
    ;;

  status)
    name="${2:-}"; D="$RENDER_DIR/$name"
    if [ ! -d "$D" ]; then echo "$name: unknown"; exit 1; fi
    if [ -s "$D/exit" ]; then
      echo "$name: FINISHED exit=$(cat "$D/exit")"
    elif [ -f "$D/pid" ] && kill -0 "$(cat "$D/pid")" 2>/dev/null; then
      echo "$name: RUNNING pid $(cat "$D/pid")"
    else
      echo "$name: NOT RUNNING and no exit file, so something killed it"
    fi
    tail -3 "$D/status" 2>/dev/null
    tail -3 "$D/run.log" 2>/dev/null
    ;;

  stop)
    name="${2:-}"; D="$RENDER_DIR/$name"
    [ -d "$D" ] || { echo "$name: unknown"; exit 1; }
    P=""
    if [ -f "$D/pid" ]; then
      P="$(cat "$D/pid")"
      # The job runs in its own session, so the supervisor, keep-awake, the
      # job and its encoder children all share the pid's process group.
      kill -TERM -- -"$P" 2>/dev/null; sleep 2; kill -KILL -- -"$P" 2>/dev/null
    fi
    echo "stopped by hand $(date '+%Y-%m-%d %H:%M')" > "$D/exit"
    echo "$name: stopped (process group ${P:-?})"
    ;;

  tail)
    name="${2:-}"; tail -40 "$RENDER_DIR/$name/run.log" ;;

  list)
    for d in "$RENDER_DIR"/*/; do
      [ -d "$d" ] || continue
      n="$(basename "$d")"
      if [ -s "$d/exit" ]; then echo "$n: exit $(cat "$d/exit")"
      elif [ -f "$d/pid" ] && kill -0 "$(cat "$d/pid")" 2>/dev/null; then echo "$n: RUNNING"
      else echo "$n: stopped"; fi
    done ;;

  *) usage; exit 1 ;;
esac
