#!/usr/bin/env bash
# deploy-verify — the deploy hop is no longer trusted, it is VERIFIED (RCA-022).
#
# Why: on 2026-07-15 the GitHub->Vercel webhook died silently. Pushes "succeeded",
# the site served a stale build for ~36h, and nothing alarmed — the writer was green,
# the reader was stale (the RCA-010/021 shape, one hop further out). So after every
# publish push, this script confirms production actually caught up; if it didn't,
# it self-heals with an explicit CLI deploy and re-verifies. Silence is impossible:
# every path ends in a loud log line, and failure exits non-zero into launchd .err.
#
# Outbound endpoints (justified per network policy): the production site itself and
# api.vercel.com via the vercel CLI (TLS, authed locally, no secrets in repo).
#
#   deploy-verify.sh <local-json> <prod-url> [wait-min]
#   deploy-verify.sh --selftest        # hermetic: drives the comparison logic
set -euo pipefail

VERCEL="${VERCEL_BIN:-/opt/homebrew/bin/vercel}"

# newer_or_equal <prod_iso> <local_iso> -> 0 if prod has caught up
newer_or_equal() {
  python3 - "$1" "$2" <<'PY'
import sys
from datetime import datetime
def p(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))
sys.exit(0 if p(sys.argv[1]) >= p(sys.argv[2]) else 1)
PY
}

prod_stamp() { # <url> -> generated_at or empty
  curl -sL --max-time 15 "$1" 2>/dev/null \
    | python3 -c "import sys,json;print(json.load(sys.stdin).get('generated_at',''))" 2>/dev/null || true
}

if [ "${1:-}" = "--selftest" ]; then
  newer_or_equal "2026-01-02T00:00:00Z" "2026-01-01T00:00:00Z" || { echo "selftest FAIL: newer not accepted" >&2; exit 1; }
  newer_or_equal "2026-01-01T00:00:00+00:00" "2026-01-01T00:00:00Z" || { echo "selftest FAIL: equal not accepted" >&2; exit 1; }
  if newer_or_equal "2026-01-01T00:00:00Z" "2026-01-02T00:00:00Z"; then echo "selftest FAIL: lag not detected" >&2; exit 1; fi
  echo "deploy-verify selftest: comparison logic sound (newer/equal pass, lag detected)"
  exit 0
fi

LOCAL_JSON="${1:?usage: deploy-verify.sh <local-json> <prod-url> [wait-min]}"
PROD_URL="${2:?usage: deploy-verify.sh <local-json> <prod-url> [wait-min]}"
WAIT_MIN="${3:-5}"
LOCAL_GEN="$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['generated_at'])" "$LOCAL_JSON")"

check_caught_up() {
  local deadline=$((SECONDS + $1 * 60)) stamp
  while [ $SECONDS -lt $deadline ]; do
    stamp="$(prod_stamp "$PROD_URL")"
    if [ -n "$stamp" ] && newer_or_equal "$stamp" "$LOCAL_GEN"; then return 0; fi
    sleep 20
  done
  return 1
}

if check_caught_up "$WAIT_MIN"; then
  echo "deploy-verify: prod caught up ($PROD_URL >= $LOCAL_GEN) — webhook path healthy."
  exit 0
fi

echo "deploy-verify: prod did NOT catch up within ${WAIT_MIN}m — webhook presumed dead; self-healing with explicit CLI deploy." >&2
cd "$(dirname "$0")/.."
"$VERCEL" deploy --prod --yes >/dev/null 2>&1 || { echo "deploy-verify: CLI deploy FAILED" >&2; exit 1; }

if check_caught_up 4; then
  echo "deploy-verify: self-heal SUCCEEDED — prod current after explicit deploy (webhook still needs fixing)."
  exit 0
fi
echo "deploy-verify: self-heal deploy ran but prod STILL stale — manual intervention required." >&2
exit 1
