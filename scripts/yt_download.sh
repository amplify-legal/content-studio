#!/usr/bin/env bash
#
# yt_download.sh, download a YouTube video (or a slice of one) reliably.
#
# WHY THIS EXISTS. yt-dlp breaks against YouTube roughly monthly, and the
# failure looks like "HTTP Error 403: Forbidden" rather than anything that says
# "I am out of date". A seven-week-old build once blocked a simple check on a
# published video. So the fix is not a one-time upgrade, it is a wrapper that
# heals itself when YouTube moves.
#
# The ladder, in order, stopping at the first that works:
#   1. Straight download.
#   2. Upgrade yt-dlp, then retry. This fixes it almost every time.
#   3. Retry with cookies, which reaches members-only, age-gated and unlisted
#      video the anonymous route cannot. Prefers a cookies file (YT_COOKIES, or
#      credentials/youtube-cookies.txt under the current directory) and falls
#      back to reading Chrome directly. The Chrome route only works with Chrome
#      fully quit, because Chrome locks its cookie database while running. If
#      you need cookies more than once, export them to a file with a
#      cookies.txt browser extension and keep that file out of git.
#
# USAGE
#   scripts/yt_download.sh <url> [--section 00:01:00-00:01:10] [--audio]
#                                [--quality 1080|720|480|best] [--codec h264]
#                                [--out DIR] [--name BASENAME]
#
#   --section  slice instead of the whole video, much faster for a spot check
#   --audio    m4a only, for transcription
#   --quality  capped height, default 1080
#   --codec h264  prefer avc1 over AV1. YouTube serves AV1 by default at these
#             heights, and many laptops have no hardware AV1 decode, so anything
#             that reads the file frame by frame afterwards (a frame sampler,
#             ffmpeg filters) pays roughly 10x. One 20 minute AV1 download cost
#             21 minutes of CPU in a single ffmpeg scene pass. Falls back to
#             whatever exists when h264 is not offered.
#   --out      destination directory, default the current directory
#
# Prints the path of the finished file on the last line, so it can be captured:
#   f=$(scripts/yt_download.sh "$url" --section 00:00:00-00:00:10 | tail -1)
#
# Keep downloads out of your git repo: they are large, and a single 600MB
# source file is enough to make a repo refuse to push.
#
# ENV
#   PYTHON       the python used to install or upgrade yt-dlp. default python3
#   YT_COOKIES   path to a cookies.txt file
#
set -o pipefail

PY="${PYTHON:-$(command -v python3)}"
YTDLP="$(command -v yt-dlp)"
if [ -z "$YTDLP" ]; then
  echo "yt-dlp is not installed. Installing it now." >&2
  "$PY" -m pip install --quiet --upgrade yt-dlp >&2 || { echo "Could not install yt-dlp." >&2; exit 1; }
  YTDLP="$(command -v yt-dlp)"
  [ -n "$YTDLP" ] || { echo "yt-dlp installed but not on PATH. Add your python's bin folder to PATH." >&2; exit 1; }
fi

URL=""; SECTION=""; AUDIO=0; QUALITY="1080"; OUTDIR="."; NAME=""; CODEC=""
while [ $# -gt 0 ]; do
  case "$1" in
    --section) SECTION="$2"; shift 2 ;;
    --audio)   AUDIO=1; shift ;;
    --quality) QUALITY="$2"; shift 2 ;;
    --codec)   CODEC="$2"; shift 2 ;;
    --out)     OUTDIR="$2"; shift 2 ;;
    --name)    NAME="$2"; shift 2 ;;
    -h|--help) sed -n '3,46p' "$0"; exit 0 ;;
    *)         URL="$1"; shift ;;
  esac
done
[ -n "$URL" ] || { echo "Need a URL. Try --help." >&2; exit 1; }
mkdir -p "$OUTDIR"

if [ "$AUDIO" -eq 1 ]; then
  FORMAT="bestaudio[ext=m4a]/bestaudio"
elif [ "$CODEC" = "h264" ]; then
  if [ "$QUALITY" = "best" ]; then
    FORMAT="bv*[vcodec^=avc1]+ba/b[vcodec^=avc1]/bv*+ba/b"
  else
    FORMAT="bv*[vcodec^=avc1][height<=${QUALITY}]+ba/b[vcodec^=avc1][height<=${QUALITY}]/bv*[height<=${QUALITY}]+ba/b[height<=${QUALITY}]"
  fi
elif [ "$QUALITY" = "best" ]; then
  FORMAT="bv*+ba/b"
else
  FORMAT="bv*[height<=${QUALITY}]+ba/b[height<=${QUALITY}]"
fi

TEMPLATE="${NAME:-%(title).80B [%(id)s]}.%(ext)s"

ARGS=( --no-warnings --no-playlist -f "$FORMAT" -o "${OUTDIR%/}/${TEMPLATE}" --print after_move:filepath )
[ -n "$SECTION" ] && ARGS+=( --download-sections "*${SECTION}" --force-keyframes-at-cuts )

# One log file per run, overwritten by each attempt. Nothing is deleted.
LOG="${TMPDIR:-/tmp}/yt_download.$$.log"

attempt() {  # $1 = label, rest = extra yt-dlp flags
  local label="$1"; shift
  local out rc
  "$YTDLP" "${ARGS[@]}" "$@" "$URL" > "$LOG" 2>&1
  rc=$?
  out="$(grep -E '^/' "$LOG" | tail -1)"
  if [ "$rc" -eq 0 ] && [ -n "$out" ] && [ -s "$out" ]; then
    printf '%s\n' "$out"; return 0
  fi
  echo "  ${label} failed:" >&2
  grep -Ei 'error|forbidden|sign in|unavailable|private' "$LOG" | tail -2 >&2
  return 1
}

echo "Downloading. If this is the first failure in a while it is probably a stale yt-dlp, which step 2 fixes." >&2

if result="$(attempt 'direct')"; then
  echo "$result"; exit 0
fi

echo "Upgrading yt-dlp and retrying." >&2
"$PY" -m pip install --quiet --upgrade yt-dlp >&2
YTDLP="$(command -v yt-dlp)"
if result="$(attempt 'after upgrade')"; then
  echo "yt-dlp was out of date. Upgraded to $("$YTDLP" --version) and the download went through." >&2
  echo "$result"; exit 0
fi

COOKIEFILE="${YT_COOKIES:-$PWD/credentials/youtube-cookies.txt}"
if [ -f "$COOKIEFILE" ]; then
  echo "Retrying with the cookies file." >&2
  if result="$(attempt 'with cookie file' --cookies "$COOKIEFILE")"; then
    echo "$result"; exit 0
  fi
else
  echo "Retrying by reading Chrome's cookies. This only works if Chrome is fully quit." >&2
  if result="$(attempt 'with Chrome cookies' --cookies-from-browser chrome)"; then
    echo "$result"; exit 0
  fi
fi

cat >&2 <<'MSG'

All three routes failed. What that usually means, most likely first:
  1. The video is private, deleted, or region blocked. Open the URL and check.
  2. It needs a signed-in session. Quit Chrome and run this again, or better,
     export cookies once to a cookies.txt file and point YT_COOKIES at it.
  3. YouTube changed something yt-dlp has not caught up with yet. Check the
     yt-dlp issue tracker for the last day or two; it is usually already
     reported and fixed within a day.
MSG
exit 1
