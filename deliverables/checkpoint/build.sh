#!/bin/zsh
# Render checkpoint-brief.md to PDF (pandoc + headless Chrome). Run from anywhere.
set -e
cd "$(dirname "$0")"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
pandoc checkpoint-brief.md -f markdown -t html5 -s --embed-resources \
  --css ../use-case-report/report.css --css checkpoint.css \
  --metadata title="IT-Porto · Mentor checkpoint" --metadata lang=en -o checkpoint-brief.html
"$CHROME" --headless=new --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$PWD/checkpoint-brief.pdf" "file://$PWD/checkpoint-brief.html" 2>/dev/null
rm -f checkpoint-brief.html
echo "built $PWD/checkpoint-brief.pdf"
