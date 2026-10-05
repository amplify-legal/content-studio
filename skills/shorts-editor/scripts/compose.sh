#!/bin/bash
# Final composite: talking-head (bottom) + cards (top band) + subtitles + music.
# Usage: compose.sh <cut.mp4> <cards.mp4> <capt_dir> <out.mp4> [crop_y=420]
# crop_y = vertical offset of the face crop: TUNE it on the clip (a test frame) until
#          head+shoulders are well framed in the bottom band.
# Fixed layout: face in the bottom ~55% (overlay y=864), top band 0-864 black for the cards.
# The card's top band is opaque black => only the 1080x864 crop overlaps (no alpha needed).
set -e
CUT="$1"; CARDS="$2"; CAPT="$3"; OUT="$4"; CY="${5:-420}"

usage() {
  echo "compose.sh <cut.mp4> <cards.mp4> <capt_dir> <out.mp4> [crop_y=420]" >&2
  echo "  cut.mp4    the finished cut, step 6 of the pipeline" >&2
  echo "  cards.mp4  the rendered card track, step 10" >&2
  echo "  capt_dir   the folder of caption PNGs, step 11" >&2
  echo "  out.mp4    where the finished short goes" >&2
  echo "  crop_y     face crop offset, tune it on a test frame (roughly 120-300)" >&2
}
if [ $# -lt 4 ]; then
  echo "Missing arguments. This needs 4; it got $#." >&2
  usage; exit 2
fi
for pair in "cut video:$CUT" "cards video:$CARDS"; do
  label="${pair%%:*}"; path="${pair#*:}"
  if [ ! -f "$path" ]; then
    echo "Cannot find the $label: $path" >&2
    echo "Check the path. Nothing here creates it for you." >&2
    usage; exit 2
  fi
done
if [ ! -d "$CAPT" ]; then
  echo "Cannot find the captions folder: $CAPT" >&2
  echo "That is the PNG sequence captions_brand.py writes at step 11." >&2
  usage; exit 2
fi
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
# No music ships with this skill. Point MUSIC at your own licensed track, or drop one at
# assets/bg-music.m4a to make it the default. See assets/README.md.
MUSIC="${MUSIC:-$SKILL_DIR/assets/bg-music.m4a}"
MUSIC_VOL="${MUSIC_VOL:-0.02}"   # music at 2% by default. 6% was called way too loud on review;
                                 # 0.06 is the RETIRED legacy default, do not reinstate it.
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$CUT")
FOUT=$(python3 -c "print(max(0,$DUR-2))")

ffmpeg -y -i "$CUT" -i "$CARDS" -framerate 12 -i "$CAPT/%05d.png" -filter_complex \
"[0:v]scale=1080:-2,crop=1080:1056:0:$CY[v];color=c=black:s=1080x1920[bg];[bg][v]overlay=0:864:shortest=1[stage];[1:v]crop=1080:864:0:0[ctop];[stage][ctop]overlay=0:0[wc];[wc][2:v]overlay=0:78[final]" \
-map "[final]" -map 0:a -c:v libx264 -preset medium -crf 21 -pix_fmt yuv420p -c:a aac -b:a 160k -shortest "$OUT.noaudio.mp4"

# Audio: VOICE normalized to dialog level (loudnorm I=-16, robust for loud or quiet voice),
# MUSIC low (default 2%; 6% is the retired legacy default), the track from its 0:04 second, fade in/out.
# +faststart => moov atom up front: the file opens in QuickTime/Preview and streams online instantly.
# With no track present we keep the voice pass and skip the bed, rather than failing the render.
if [ -f "$MUSIC" ]; then
  ffmpeg -y -i "$OUT.noaudio.mp4" -i "$MUSIC" -filter_complex \
  "[0:a]loudnorm=I=-16:TP=-1.5:LRA=11[vo];[1:a]atrim=start=4,asetpts=PTS-STARTPTS,volume=$MUSIC_VOL,afade=in:st=0:d=0.5,afade=out:st=$FOUT:d=2[m];[vo][m]amix=inputs=2:duration=first:normalize=0[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -movflags +faststart "$OUT"
else
  echo "note: no music track at $MUSIC. Set MUSIC=/path/to/track.m4a or see assets/README.md. Rendering voice only."
  ffmpeg -y -i "$OUT.noaudio.mp4" -filter_complex \
  "[0:a]loudnorm=I=-16:TP=-1.5:LRA=11[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -movflags +faststart "$OUT"
fi
rm -f "$OUT.noaudio.mp4"
echo "DONE -> $OUT"
