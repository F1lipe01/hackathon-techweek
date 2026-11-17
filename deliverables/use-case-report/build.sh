#!/bin/zsh
# Render top5-use-cases.md -> top5-use-cases.pdf (pandoc + headless Chrome). Run from anywhere.
set -e
cd "$(dirname "$0")"
pandoc top5-use-cases.md -f markdown+lists_without_preceding_blankline -t html5 -s --embed-resources --css report.css \
  --metadata title="IT-Porto · Top 5 use cases" --metadata lang=en -o top5-use-cases.html
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu \
  --no-pdf-header-footer --print-to-pdf="$PWD/top5-use-cases.pdf" "file://$PWD/top5-use-cases.html" 2>/dev/null
rm -f top5-use-cases.html
echo "built $PWD/top5-use-cases.pdf"
