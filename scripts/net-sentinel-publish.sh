#!/usr/bin/env bash
# net-sentinel publish — sanitize the engine's canonical output to the curated public
# posture and commit+push it. The sanitizer (net-sentinel-sanitize.py) is the single
# trust boundary: only aggregate posture is ever published, never raw connections.
#
# Same guards as arxiv-pulse-publish.sh (RCA-021): publish only from main, ff-only before
# push — so a feature branch checked out can never capture the commit and the push can
# never stale-no-op.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"
SRC="$HOME/.net-sentinel.json"

[ -f "$SRC" ] || { echo "net-sentinel: engine output $SRC missing — is the engine loaded?" >&2; exit 1; }

# Guard 1 — publish only from main (loud non-zero exit -> launchd .err).
BRANCH="$(git symbolic-ref --quiet --short HEAD || echo DETACHED)"
if [ "$BRANCH" != "main" ]; then
  echo "net-sentinel: REFUSING to publish — HEAD is '$BRANCH', not main." >&2
  exit 1
fi

# Guard 2 — start from current origin/main so the push is a true fast-forward.
git fetch --quiet origin main
if ! git merge --ff-only --quiet origin/main; then
  echo "net-sentinel: ERROR local main diverged from origin/main — aborting." >&2
  exit 1
fi

python3 scripts/net-sentinel-sanitize.py "$SRC" data/net-sentinel.json

if git diff --quiet -- data/net-sentinel.json; then
  echo "net-sentinel: no change — nothing to publish."
  exit 0
fi

git add data/net-sentinel.json
git commit -m "chore(data): refresh net-sentinel posture $(date -u +%Y-%m-%d)" \
           -m "Automated curated-posture refresh (aggregate-only) by the net-sentinel publish job."
git push origin main
echo "net-sentinel: published + pushed."
