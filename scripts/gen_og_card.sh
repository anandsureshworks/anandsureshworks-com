#!/usr/bin/env bash
# Render scripts/og-card.html -> /og-card.png (1200x630) with headless Chrome.
set -euo pipefail
cd "$(dirname "$0")/.."
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
# Chrome's --headless=new reserves ~85px of the window canvas below the viewport
# (band at the bottom of the screenshot). Render at 715 so the 630px body fills the
# true viewport, then sips-crop the top 1200x630. NOTE: --cropOffset must come AFTER
# -c or sips silently center-crops (which beheads the card).
"$CHROME" --headless=new --disable-gpu --force-device-scale-factor=1 \
  --window-size=1200,715 --screenshot="og-card.png" \
  "file://$PWD/scripts/og-card.html" >/dev/null 2>&1
sips -c 630 1200 --cropOffset 0 0 og-card.png >/dev/null 2>&1
FINAL_H=$(sips -g pixelHeight og-card.png | awk '/pixelHeight/{print $2}')
[ "$FINAL_H" = "630" ] || { echo "og-card height $FINAL_H != 630"; exit 1; }
echo "og-card.png: $(file og-card.png | cut -d: -f2) — EYEBALL THE PNG before committing; geometry bugs don't error"
