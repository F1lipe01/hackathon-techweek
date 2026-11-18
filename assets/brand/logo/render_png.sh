#!/bin/zsh
# Export every SVG in this folder to a transparent PNG with Chrome (lockups 2400 px wide, marks 1024 px).
set -e
cd "$(dirname "$0")"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
TMP=$(mktemp -d)
for svg in *.svg; do
  vb=$(sed -E 's/.*viewBox="([^"]+)".*/\1/;q' "$svg")
  read -r _ _ w h <<< "$vb"
  case "$svg" in *mark*) W=1024 ;; *) W=2400 ;; esac
  H=$(python3 -c "print(round($W*$h/$w))")
  print "<!doctype html><style>html,body{margin:0;background:transparent}img{display:block;width:${W}px;height:${H}px}</style><img src=\"file://$PWD/$svg\">" > "$TMP/p.html"
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --default-background-color=00000000 \
    --window-size=$W,$H --screenshot="$PWD/${svg%.svg}.png" "file://$TMP/p.html" 2>/dev/null
  echo "${svg%.svg}.png  ${W}x${H}"
done
rm -rf "$TMP"
