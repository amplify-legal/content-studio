#!/usr/bin/env bash
#
# render_status.sh, "is the render actually working?" in one command.
#
# Working means the output file is growing. Never the CPU meter, which is high
# both when ffmpeg is encoding and when it is spinning on a stall, and never a
# guess. This script answers from the files.
#
# What it reads, in order:
#   1. _finalize.pid files under <dir>: is the render process alive
#   2. the newest _render.status under <dir>: a heartbeat your pipeline writes
#      every ~30s (elapsed, bytes, growth, ETA, PASS or STALLED). This is the
#      real answer when present, and STALE when not written in 2 minutes
#   3. any .mp4/.mov/.m4a touched in the last 30 minutes, sampled twice 3s apart:
#      GROWING, static, or nothing
#   4. the tail of _finalize.log, because the cause usually says itself there
#
# The three filenames are a convention, not a requirement. A pipeline that
# writes none of them still gets step 3, which answers the same question.
#
# USAGE
#   scripts/render_status.sh [dir] [--watch [secs]]
#   dir defaults to the current directory
#
set -uo pipefail

DIR="${1:-.}"
[ "${DIR#-}" != "$DIR" ] && DIR="."   # first arg was a flag
WATCH=0
INTERVAL=30
for a in "$@"; do
  case "$a" in
    --watch) WATCH=1 ;;
    [0-9]*) [ "$WATCH" = 1 ] && INTERVAL="$a" ;;
  esac
done

if [ ! -d "$DIR" ]; then
  echo "render_status: no such directory: $DIR"
  exit 1
fi

human() { # bytes -> human
  awk -v b="${1:-0}" 'BEGIN{u="B";s=b;
    if(s>=1073741824){s=s/1073741824;u="GB"} else if(s>=1048576){s=s/1048576;u="MB"}
    else if(s>=1024){s=s/1024;u="KB"};printf "%.1f%s", s, u}'
}

fsize() { stat -f %z "$1" 2>/dev/null || stat -c %s "$1" 2>/dev/null || echo 0; }
fmtime() { stat -f %m "$1" 2>/dev/null || stat -c %Y "$1" 2>/dev/null || echo 0; }

report() {
  local now; now=$(date +%s)
  echo "=== render status @ $(date '+%Y-%m-%d %H:%M:%S') ==="
  echo "dir: $DIR"

  # 1. live PID handles (detached renders leave _finalize.pid beside the output)
  local anypid=0
  while IFS= read -r pf; do
    [ -z "$pf" ] && continue
    local pid; pid=$(tr -dc '0-9' < "$pf")
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
      echo "pid: $pid ALIVE  ($pf)"
      anypid=1
    else
      echo "pid: ${pid:-?} not running  ($pf, stale handle)"
    fi
  done < <(find "$DIR" -name '_finalize.pid' -type f 2>/dev/null)

  # 2. the status files, newest first; this is the real answer when present
  local statuses
  statuses=$(find "$DIR" -name '_render.status' -type f 2>/dev/null)
  if [ -n "$statuses" ]; then
    local newest="" newest_t=0
    while IFS= read -r s; do
      local t; t=$(fmtime "$s")
      if [ "$t" -gt "$newest_t" ]; then newest_t=$t; newest=$s; fi
    done <<< "$statuses"
    local age=$(( now - newest_t ))
    echo "--- $newest (updated ${age}s ago) ---"
    cat "$newest"
    if [ "$age" -gt 120 ]; then
      echo "VERDICT: STALE, status not written in ${age}s; the writer is gone or wedged."
    fi
    echo
  else
    echo "(no _render.status found, falling back to file growth)"
  fi

  # 3. fallback / corroboration: is any output file actually growing?
  local cands
  cands=$(find "$DIR" -type f \( -name '*.mp4' -o -name '*.mov' -o -name '*.m4a' \) \
            -newermt '-30 minutes' 2>/dev/null | head -20)
  if [ -z "$cands" ]; then
    echo "growth: no output touched in the last 30 minutes."
  else
    echo "growth (3s sample):"
    local -a files=() before=()
    while IFS= read -r f; do files+=("$f"); before+=("$(fsize "$f")"); done <<< "$cands"
    sleep 3
    local i=0 growing=0
    for f in "${files[@]}"; do
      local a="${before[$i]}" b; b=$(fsize "$f")
      local d=$(( b - a ))
      if [ "$d" -gt 0 ]; then
        growing=1
        echo "  GROWING  $(human "$b")  +$(human "$d")/3s  ~$(human $(( d * 20 )))/min  ${f#"$DIR"/}"
      else
        echo "  static   $(human "$b")  ${f#"$DIR"/}"
      fi
      i=$((i+1))
    done
    if [ "$growing" = 1 ]; then
      echo "VERDICT: PASS, output is growing."
    elif [ "$anypid" = 1 ]; then
      echo "VERDICT: STALLED? a render process is alive but nothing grew in 3s."
      echo "         (normal during the audio pass or a concat; re-check in 60s before concluding.)"
    else
      echo "VERDICT: IDLE, no live render process and nothing growing."
    fi
  fi

  # 4. the log tail, because the cause usually says itself there
  local logs; logs=$(find "$DIR" -name '_finalize.log' -type f 2>/dev/null | head -3)
  if [ -n "$logs" ]; then
    while IFS= read -r l; do
      echo "--- tail $l ---"
      tail -n 6 "$l"
    done <<< "$logs"
  fi
}

if [ "$WATCH" = 1 ]; then
  while true; do report; echo; sleep "$INTERVAL"; done
else
  report
fi
