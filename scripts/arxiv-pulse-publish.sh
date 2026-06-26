#!/usr/bin/env bash
# arxiv-pulse publish — run the engine, then commit + push data/arxiv.json IF it changed.
# Invoked by the launchd job (see com.anandsureshworks.arxiv-pulse.plist).
# The push to main is the deploy: Vercel rebuilds the static site from the data file.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

python3 scripts/arxiv-pulse.py

if git diff --quiet -- data/arxiv.json; then
  echo "arxiv-pulse: no change — nothing to publish."
  exit 0
fi

git add data/arxiv.json
git commit -m "chore(data): refresh arxiv-pulse $(date -u +%Y-%m-%d)" \
           -m "Automated daily refresh by the arxiv-pulse launchd engine."
git push origin main
echo "arxiv-pulse: published + pushed."
