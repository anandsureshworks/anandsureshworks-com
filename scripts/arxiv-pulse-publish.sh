#!/usr/bin/env bash
# arxiv-pulse publish — run the engine, then commit + push data/arxiv.json IF it changed.
# Invoked by the launchd job (see com.anandsureshworks.arxiv-pulse.plist).
# The push to main is the deploy: Vercel rebuilds the static site from the data file.
#
# GUARDRAILS (why they exist — RCA 2026-07-11 "silent-staleness"):
#   The engine commits to whatever branch is checked out. When a feature branch was
#   left checked out, every refresh committed onto THAT branch while `git push origin
#   main` pushed an unchanged main ref — a silent no-op. The published card froze for
#   ~2 weeks with no error. So this script now:
#     1. refuses to run unless HEAD is main, and exits non-zero so launchd's .err logs
#        it (stale is now a LOUD, logged incident — never silent);
#     2. fast-forwards local main to origin/main before committing, so the push can
#        never be a stale no-op and can never be rejected as non-fast-forward.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

# Guard 1 — publish only from main. A feature branch checked out must NOT capture
# the data commit. Loud, non-zero exit -> surfaces in /tmp/arxiv-pulse.err.
BRANCH="$(git symbolic-ref --quiet --short HEAD || echo DETACHED)"
if [ "$BRANCH" != "main" ]; then
  echo "arxiv-pulse: REFUSING to publish — HEAD is '$BRANCH', not main." >&2
  echo "arxiv-pulse: data will go stale until 'git checkout main'. This is an incident." >&2
  exit 1
fi

# Guard 2 — start from current origin/main so the eventual push is a true fast-forward.
git fetch --quiet origin main
if ! git merge --ff-only --quiet origin/main; then
  echo "arxiv-pulse: ERROR local main diverged from origin/main — aborting to avoid a bad push." >&2
  exit 1
fi

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

# RCA-022: never trust the deploy hop — verify prod caught up; self-heal via CLI deploy if not.
"$(dirname "$0")/deploy-verify.sh" data/arxiv.json "https://www.anandsureshworks.com/data/arxiv.json" 5
