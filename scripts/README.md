# scripts

Build/engine tooling for anandsureshworks.com. Dependency-free (Python stdlib + bash).

## `gen_mark.py`
Single source of truth for the woven **AS** brand mark. Regenerates the SVGs
(`as-logo.svg`, `icon.svg`). Green is one token; never hand-edit the marks.

## `arxiv-pulse.py` — the "read today" engine
Fetches the day's arXiv firehose, scores each paper against a transparent interest
model (`INTERESTS` in the script), and writes the top few to JSON. The website
widget is **read-only** — the engine owns the API call.

- **Outbound endpoint (the only one):** `export.arxiv.org/api/query` — public, no
  auth, no secret, no PII. Add to `~/.net-sentinel.json` if you enforce an allowlist.
- **Outputs (atomic tmp+rename):**
  - `~/.arxiv-pulse.json` — canonical engine output (per the `~/.<engine>.json` convention)
  - `data/arxiv.json` — the publish target the widget fetches
- **Freshness contract:** refreshed daily; `generated_at` is ISO-8601 UTC; **stale if
  age > 48h** (2× interval) — the footer shows the stamp so staleness is visible.
- **Network:** 15s timeout, 3 tries with exponential backoff, never fire-and-forget.

```sh
python3 scripts/arxiv-pulse.py --dry-run   # fetch + score + print JSON, write nothing
python3 scripts/arxiv-pulse.py             # write both outputs
```

## Scheduling (manual refresh is a bug)
`arxiv-pulse-publish.sh` runs the engine, then commits + pushes `data/arxiv.json`
only if it changed (the push is the deploy). `com.anandsureshworks.arxiv-pulse.plist`
runs it daily at 07:20 local.

```sh
cp scripts/com.anandsureshworks.arxiv-pulse.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.anandsureshworks.arxiv-pulse.plist
# logs: /tmp/arxiv-pulse.log, /tmp/arxiv-pulse.err
```
