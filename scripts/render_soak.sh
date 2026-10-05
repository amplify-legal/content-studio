#!/usr/bin/env bash
#
# render_soak.sh, an evidence run for "my renders never finish".
#
# Before you change anything in a pipeline that keeps dying overnight, measure
# it. This runs the long-render shapes that historically hang, each one bounded
# by a hard time limit, each with a memory sample every 10 seconds, so a hang
# leaves a timestamped trail instead of a mystery.
#
#   A. monolithic finalize: ONE ffmpeg over the full master, captions burned,
#      optional speed change. The shape most people blame first.
#   B. your own parallel finalize, once per worker count you pass, so you can
#      compare widths on THIS machine under THIS load.
#
# What a real soak found, and why it is worth running before you rewrite
# anything: the monolithic render did not hang by itself (21 minute master,
# 16.6 minutes wall, peak ffmpeg memory 851MB). The deaths had been a runaway
# -loop tail plus a loaded machine. And width 4 beat width 8 on a 16GB laptop
# (2.12x realtime against 1.25x), the opposite of a benchmark taken on an idle
# machine. Measure, then change one thing.
#
# USAGE
#   scripts/render_soak.sh <master.mp4> [captions.ass]
#
# ENV
#   SOAK_OUT          results folder.               default ./.renders/soak
#   SOAK_FONTS_DIR    fonts dir for the caption burn (optional)
#   SOAK_SPEED        playback speed for pass A, e.g. 1.1. default 1.0
#   SOAK_MONO_LIMIT   seconds before pass A is killed. default 14400 (4h)
#   SOAK_BENCH_CMD    your parallel finalize, with {N} where the worker count
#                     goes, e.g. "python3 build/finalize.py --bench {N}".
#                     Unset skips pass B
#   SOAK_WIDTHS       worker counts for pass B.      default "4 8"
#   SOAK_BENCH_LIMIT  seconds before each pass B run is killed. default 1800
#
# Run it detached (scripts/render_detached.sh start soak -- "...") on a machine
# you have cleared, and read $SOAK_OUT/summary.txt in the morning.
#
# macOS ships no `timeout` command, which is why the limits use a perl alarm:
# an earlier soak written with `timeout` exited 127 on every step and measured
# nothing.
#
set -uo pipefail

MASTER="${1:-}"; CAPS="${2:-}"
[ -z "$MASTER" ] && { sed -n '3,43p' "$0"; exit 1; }
[ -f "$MASTER" ] || { echo "no such master: $MASTER"; exit 1; }

S="${SOAK_OUT:-$PWD/.renders/soak}"; mkdir -p "$S"; SUM="$S/summary.txt"
SPEED="${SOAK_SPEED:-1.0}"
MONO_LIMIT="${SOAK_MONO_LIMIT:-14400}"
BENCH_LIMIT="${SOAK_BENCH_LIMIT:-1800}"
WIDTHS="${SOAK_WIDTHS:-4 8}"

log() { echo "$(date '+%F %T') $*" | tee -a "$SUM"; }
fsize() { stat -f %z "$1" 2>/dev/null || stat -c %s "$1" 2>/dev/null || echo 0; }
limit() { local secs="$1"; shift; perl -e 'alarm shift; exec @ARGV' "$secs" "$@"; }

avail() {
  if command -v memory_pressure >/dev/null 2>&1; then
    memory_pressure 2>/dev/null | awk '/free percentage/{gsub(/%/,"",$5); print $5"%"}'
  elif [ -r /proc/meminfo ]; then
    awk '/^MemTotal/{t=$2} /^MemAvailable/{a=$2} END{if(t>0) printf "%d%%", a*100/t}' /proc/meminfo
  else echo "?"; fi
}

peak() {  # sample the summed ffmpeg RSS (MB) while pid $1 runs; print the peak
  local pid=$1 mx=0 cur
  while kill -0 "$pid" 2>/dev/null; do
    cur=$(ps -axo rss,command 2>/dev/null | awk '/ffmpeg/ && !/awk/{s+=$1} END{printf "%d", s/1024}')
    [ "${cur:-0}" -gt "$mx" ] && mx=$cur
    echo "$(date +%T) ffmpegRSS=${cur}MB available=$(avail) load=$(uptime | awk -F'load average[s]*: ' '{print $2}')" >> "$S/mem.log"
    sleep 10
  done
  echo "$mx"
}

log "soak start: master=$(fsize "$MASTER") bytes captions=${CAPS:-none} speed=$SPEED"

# A. monolithic
VF="setpts=PTS/$SPEED"
if [ -n "$CAPS" ]; then
  if [ -n "${SOAK_FONTS_DIR:-}" ]; then VF="subtitles='$CAPS':fontsdir='$SOAK_FONTS_DIR',$VF"
  else VF="subtitles='$CAPS',$VF"; fi
fi
log "A monolithic start"; t0=$(date +%s)
limit "$MONO_LIMIT" ffmpeg -nostdin -y -v error -i "$MASTER" -vf "$VF" -af "atempo=$SPEED" \
  -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -ar 48000 \
  "$S/A-mono.mp4" &
P=$!; mx=$(peak "$P"); wait "$P"; rc=$?
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$S/A-mono.mp4" 2>/dev/null)
log "A monolithic exit=$rc wall=$(( $(date +%s) - t0 ))s peakFfmpegRSS=${mx}MB size=$(fsize "$S/A-mono.mp4") dur=${dur:-?}"

# B. parallel, at each width
if [ -n "${SOAK_BENCH_CMD:-}" ]; then
  for w in $WIDTHS; do
    cmd="${SOAK_BENCH_CMD//\{N\}/$w}"
    log "B width $w start: $cmd"; t0=$(date +%s)
    limit "$BENCH_LIMIT" bash -c "$cmd" >> "$S/bench-$w.log" 2>&1 &
    P=$!; mx=$(peak "$P"); wait "$P"; rc=$?
    log "B width $w exit=$rc wall=$(( $(date +%s) - t0 ))s peakFfmpegRSS=${mx}MB"
  done
else
  log "B skipped: set SOAK_BENCH_CMD to compare worker counts"
fi
log "soak done. Exit 142 means the time limit fired, which is itself the finding."
