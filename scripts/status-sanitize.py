#!/usr/bin/env python3
"""status-sanitize — project the fleet's deterministic gate outputs into the public
aggregate-only status JSON the /status/ page reads.

ALLOWLIST, not a filter (same trust boundary pattern as net-sentinel-sanitize): the
output is built field-by-field from named aggregates — counts and booleans only.
Repo names, engine labels, check descriptions, and paths are NEVER published.

Sources (each owned by its own gate, read here, never recomputed):
    ~/.rca-health.json        — RCA mechanism health (pass/total)
    ~/.dirty-tree-audit.json  — fleet dirty-tree audit (dirty/total)
    yantra-plist-loaded-audit — engine liveness (live/total, parsed from its stdout)

    python3 status-sanitize.py <out.json>
"""
from __future__ import annotations
import json, os, re, subprocess, sys, tempfile
from datetime import datetime, timezone

HOME = os.path.expanduser("~")


def engines_live() -> dict:
    """Parse 'N/M in-scope plists loaded' from the fleet plist audit."""
    try:
        out = subprocess.run(
            [os.path.join(HOME, "bin", "yantra-plist-loaded-audit.py")],
            capture_output=True, text=True, timeout=60,
        ).stdout
        m = re.search(r"(\d+)/(\d+) in-scope plists loaded", out)
        if m:
            return {"live": int(m.group(1)), "total": int(m.group(2))}
    except Exception:
        pass
    return {"live": 0, "total": 0}  # honest zero — the page will show it red


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("usage: status-sanitize.py <out.json>")
    rca = json.loads(open(f"{HOME}/.rca-health.json").read())
    dirty = json.loads(open(f"{HOME}/.dirty-tree-audit.json").read())

    pub = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "rca_mechanisms": {
                "pass": int(rca.get("pass", 0)),
                "total": int(rca.get("total", 0)),
                "verified_at": rca.get("generated_at"),
            },
            "dirty_trees": {
                "dirty": int(dirty.get("dirty_count", -1)),
                "total": int(dirty.get("total_count", 0)),
                "verified_at": dirty.get("generated_at"),
            },
            "engines": engines_live(),
        },
        "note": "Aggregate-only: counts and booleans from deterministic gates. No repo names, engine labels, or check detail is ever published.",
    }
    out = sys.argv[1]
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(out) or ".")
    with os.fdopen(fd, "w") as f:
        json.dump(pub, f, indent=2)
        f.write("\n")
    os.replace(tmp, out)
    c = pub["checks"]
    print(f"status-sanitize: {out} — rca {c['rca_mechanisms']['pass']}/{c['rca_mechanisms']['total']}, "
          f"dirty {c['dirty_trees']['dirty']}/{c['dirty_trees']['total']}, "
          f"engines {c['engines']['live']}/{c['engines']['total']}")


if __name__ == "__main__":
    main()
