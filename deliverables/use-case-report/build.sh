#!/bin/zsh
# Render the reports to PDF (pandoc + headless Chrome). Run from anywhere.
#   top5-use-cases.md -> top5-use-cases.pdf   (full report)
#   top5-summary.md   -> top5-summary.pdf     (short version)
set -e
cd "$(dirname "$0")"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
build() {
  local name=$1 title=$2
  pandoc "$name.md" -f markdown+lists_without_preceding_blankline -t html5 -s --embed-resources --css report.css \
    --metadata title="$title" --metadata lang=en -o "$name.html"
  "$CHROME" --headless=new --disable-gpu --no-pdf-header-footer \
    --print-to-pdf="$PWD/$name.pdf" "file://$PWD/$name.html" 2>/dev/null
  rm -f "$name.html"
  echo "built $PWD/$name.pdf"
}
build top5-use-cases "IT-Porto · Top 5 use cases"
build top5-summary "IT-Porto · Top 5 use cases (short)"
