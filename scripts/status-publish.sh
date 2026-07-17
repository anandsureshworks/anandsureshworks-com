#!/usr/bin/env bash
# status publish — re-run the deterministic gates, sanitize their outputs to the public
# aggregate-only status JSON, and commit+push it. Daily publish = daily verification:
# the public page never shows a fresher timestamp than the gates actually ran.
#
# Same guards as arxiv-pulse/net-sentinel publish (RCA-021): main-only, ff-only.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

BRANCH="$(git symbolic-ref --quiet --short HEAD || echo DETACHED)"
if [ "$BRANCH" != "main" ]; then
  echo "status: REFUSING to publish — HEAD is '$BRANCH', not main." >&2
  exit 1
fi
git fetch --quiet origin main
if ! git merge --ff-only --quiet origin/main; then
  echo "status: ERROR local main diverged from origin/main — aborting." >&2
  exit 1
fi

# Run the gates fresh so the published aggregates are verified-today, not stale reads.
"$HOME/bin/yantra-dirty-tree-audit.sh" >/dev/null 2>&1 || true   # writes ~/.dirty-tree-audit.json
"$HOME/bin/yantra-rca-health.sh"        >/dev/null 2>&1 || true   # writes ~/.rca-health.json

python3 scripts/status-sanitize.py data/status.json

if git diff --quiet -- data/status.json; then
  echo "status: no change — nothing to publish."
  exit 0
fi

git add data/status.json
git commit -m "chore(data): refresh status $(date -u +%Y-%m-%d)" \
           -m "Automated aggregate-only fleet-status refresh by the status publish job."
git push origin main
echo "status: published + pushed."

# RCA-022: never trust the deploy hop — verify prod caught up; self-heal via CLI deploy if not.
"$(dirname "$0")/deploy-verify.sh" data/status.json "https://www.anandsureshworks.com/data/status.json" 5
