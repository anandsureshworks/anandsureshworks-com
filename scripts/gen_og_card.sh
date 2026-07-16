#!/usr/bin/env bash
# Render scripts/og-card.html -> /og-card.png (1200x630) with headless Chrome.
set -euo pipefail
cd "$(dirname "$0")/.."
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu \
  --force-device-scale-factor=1 --window-size=1200,630 --screenshot="og-card.png" \
  "file://$PWD/scripts/og-card.html" >/dev/null 2>&1
echo "og-card.png: $(file og-card.png | cut -d: -f2)"
