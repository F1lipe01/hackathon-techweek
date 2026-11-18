#!/bin/zsh
# Replace single bad frames of a rendered film with stills of the same frames (tools/glitch_check.py finds them).
#   video/tools/heavy.sh video/tools/patch_frames.sh <composition> <video.mp4> <frame> [<frame> ...]
# Run from video/. The picture is re-encoded (H.264, CRF 18); the sound is copied untouched.
emulate -L zsh
set -eu
comp=$1 video=$2; shift 2
tmp=$(mktemp -d)
node tools/stills.mjs "$comp" "$tmp" "$@" >/dev/null
inputs=(-i "$video")
chain="[0:v]"
n=1
for f in "$@"; do
  png=$(printf "%s/%s-%05d.png" "$tmp" "$comp" "$f")
  inputs+=(-i "$png")
  next="v$n"
  chain+="[$n:v]overlay=enable='eq(n\\,$f)'[$next];[$next]"
  n=$((n + 1))
done
chain=${chain%;\[$next\]}
out="${video%.mp4}.patched.mp4"
ffmpeg -v error -y "${inputs[@]}" -filter_complex "$chain" -map "[$next]" -map 0:a -c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p -c:a copy -movflags +faststart "$out"
mv "$out" "$video"
rm -rf "$tmp"
echo "patched $# frame(s) in $video"
