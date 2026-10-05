#!/bin/zsh
# Download a YouTube video (or a slice of one) reliably.
#
# WHY THIS EXISTS. yt-dlp breaks against YouTube roughly monthly, and the failure
# looks like "HTTP Error 403: Forbidden" rather than anything that says "I am out
# of date". A seven-week-old build once blocked a simple check on a published
# video, so the fix is not a one-time upgrade, it is a wrapper that heals itself
# when YouTube moves.
#
# The ladder, in order, stopping at the first that works:
#   1. Straight download.
#   2. Upgrade yt-dlp, then retry. This is what fixes it almost every time.
#   3. Retry with cookies, which reaches members-only, age-gated and unlisted
#      video the anonymous route cannot. Prefers a cookies file at
#      .claude/skills/watch/credentials/youtube-cookies.txt and falls back to reading Chrome
#      directly. NOTE, the Chrome route only works with Chrome fully quit,
#      because Chrome locks its cookie database while it runs. So if you ever
#      genuinely need cookies, export them once to that file instead: install a
#      cookies.txt browser extension, save the file there, and this picks it up.
#      Keep that file out of any repo you push.
#
# USAGE
#   yt_download.sh <url> [--section 00:01:00-00:01:10] [--audio]
#                        [--quality 1080|720|480|best] [--out DIR]
#                        [--name BASENAME] [--codec h264]
#
#   --section  slice instead of the whole video, much faster for a spot check
#   --audio    m4a only, for transcription
#   --quality  capped height, default 1080
#   --out      destination directory, default the current directory
#   --codec h264  prefer avc1 over AV1. YouTube defaults to AV1, which most Macs
#              cannot hardware-decode, so anything that reads the file frame by
#              frame afterwards (the watch skill, ffmpeg filters) pays roughly
#              10x. Falls back to whatever exists when h264 is not offered.
#
# Prints the path of the finished file on the last line, so it can be captured:
#   f=$(yt_download.sh "$url" --section 00:00:00-00:00:10 | tail -1)
#
# Downloads land wherever --out says. Keep them out of any repo: they are large,
# and git has already choked once on a 636MB source file.

set -o pipefail
emulate -L zsh
setopt no_nomatch

PY="${YT_PYTHON:-}"
[[ -x "$PY" ]] || PY="$(command -v python3)"
YTDLP="$(command -v yt-dlp)"
if [[ -z "$YTDLP" ]]; then
  echo "yt-dlp is not installed. Installing it now." >&2
  "$PY" -m pip install --quiet --upgrade yt-dlp >&2 || { echo "Could not install yt-dlp." >&2; exit 1; }
  YTDLP="$(command -v yt-dlp)"
fi

URL=""; SECTION=""; AUDIO=0; QUALITY="1080"; OUTDIR="."; NAME=""; CODEC=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --section) SECTION="$2"; shift 2 ;;
    --audio)   AUDIO=1; shift ;;
    --quality) QUALITY="$2"; shift 2 ;;
    --out)     OUTDIR="$2"; shift 2 ;;
    --name)    NAME="$2"; shift 2 ;;
    --codec)   CODEC="$2"; shift 2 ;;
    -h|--help) sed -n '2,30p' "$0"; exit 0 ;;
    *)         URL="$1"; shift ;;
  esac
done
[[ -n "$URL" ]] || { echo "Need a URL. Try --help." >&2; exit 1; }
mkdir -p "$OUTDIR"

if (( AUDIO )); then
  FORMAT="bestaudio[ext=m4a]/bestaudio"
elif [[ "$CODEC" == "h264" ]]; then
  # Ask YouTube for h264 first. It matters more than it sounds: YouTube serves
  # AV1 by default at these heights, and most Macs have no hardware decode path
  # for AV1, so anything that later reads the file frame by frame pays for it.
  # A 20-minute AV1 download cost 21 minutes of CPU in one ffmpeg scene pass
  # where the same video as h264 cost 34 seconds. The fallbacks keep the old
  # behaviour when h264 is not offered.
  if [[ "$QUALITY" == "best" ]]; then
    FORMAT="bv*[vcodec^=avc1]+ba/b[vcodec^=avc1]/bv*+ba/b"
  else
    FORMAT="bv*[vcodec^=avc1][height<=${QUALITY}]+ba/b[vcodec^=avc1][height<=${QUALITY}]/bv*[height<=${QUALITY}]+ba/b[height<=${QUALITY}]"
  fi
elif [[ "$QUALITY" == "best" ]]; then
  FORMAT="bv*+ba/b"
else
  FORMAT="bv*[height<=${QUALITY}]+ba/b[height<=${QUALITY}]"
fi

TEMPLATE="${NAME:-%(title).80B [%(id)s]}.%(ext)s"

args=( --no-warnings --no-playlist -f "$FORMAT" -o "${OUTDIR%/}/${TEMPLATE}" --print after_move:filepath )
[[ -n "$SECTION" ]] && args+=( --download-sections "*${SECTION}" --force-keyframes-at-cuts )

attempt() {  # $1 = label, rest = extra yt-dlp flags
  local label="$1"; shift
  local log out rc
  log="$(mktemp)"
  "$YTDLP" "${args[@]}" "$@" "$URL" > "$log" 2>&1
  rc=$?
  out="$(grep -E '^/' "$log" | tail -1)"
  if (( rc == 0 )) && [[ -n "$out" && -s "$out" ]]; then
    print -r -- "$out"; rm -f "$log"; return 0
  fi
  echo "  ${label} failed:" >&2
  grep -Ei 'error|forbidden|sign in|unavailable|private' "$log" | tail -2 >&2
  rm -f "$log"; return 1
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

COOKIEFILE="$(cd "$(dirname "$0")/.." && pwd)/credentials/youtube-cookies.txt"
if [[ -f "$COOKIEFILE" ]]; then
  echo "Retrying with the saved cookies file." >&2
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
     export cookies once with a cookies.txt browser extension and save them at
     .claude/skills/watch/credentials/youtube-cookies.txt, which the script prefers. Keep
     that file out of any repo you push.
  3. YouTube changed something yt-dlp has not caught up with yet. Check
     github.com/yt-dlp/yt-dlp/issues for the last day or two, it is usually
     already reported and fixed within a day.
MSG
exit 1
