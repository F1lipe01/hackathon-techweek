#!/bin/zsh
# Plates for video 2 (run through tools/heavy.sh): a bright, warm, defocused home background; the 3 phone passages upscaled 2x; the kit clip upscaled.
set -e
V="$(cd "$(dirname "$0")/.." && pwd)"
cd $V
WARM="eq=brightness=0.035:contrast=1.02:saturation=1.06,colorbalance=rs=0.035:gs=0.01:bs=-0.035:rm=0.025:bm=-0.025"
ffmpeg -v error -y -i public/stock/establishing-1.mp4 -an \
  -vf "scale=1920:1080:flags=lanczos,setpts=2.0*PTS,fps=30,$WARM,gblur=sigma=5" \
  -c:v libx264 -crf 20 -preset medium -g 15 -bf 0 -pix_fmt yuv420p -movflags +faststart public/real/bg-home.mp4
ffmpeg -v error -y -i public/footage/phone-photos.mp4 -an -filter_complex \
  "[0:v]trim=start_frame=12:end_frame=69,setpts=PTS-STARTPTS[a];[0:v]trim=start_frame=667:end_frame=720,setpts=PTS-STARTPTS[b];[0:v]trim=start_frame=1059:end_frame=1167,setpts=PTS-STARTPTS[c];[a][b][c]concat=n=3:v=1:a=0,scale=784:1700:flags=lanczos,unsharp=5:5:0.5[o]" \
  -map "[o]" -r 30 -c:v libx264 -crf 17 -preset medium -g 15 -bf 0 -pix_fmt yuv420p -movflags +faststart public/real/phone-3seg-2x.mp4
ffmpeg -v error -y -i public/real/kit-desk-6s.mp4 -an \
  -vf "scale=3840:2160:flags=lanczos,unsharp=5:5:0.6,$WARM" \
  -c:v libx264 -crf 19 -preset medium -g 15 -bf 0 -pix_fmt yuv420p -movflags +faststart public/real/kit-desk-6s-uhd.mp4
ls -la public/real/*.mp4
