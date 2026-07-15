#!/usr/bin/env python3
"""net-sentinel-sanitize — project the SAFE, aggregate-only posture from the engine's
canonical output (~/.net-sentinel.json) into the public JSON the website reads.

This is the single trust boundary for the net-sentinel showcase. It is an ALLOWLIST,
not a filter: the output is built field-by-field from named safe aggregates, so nothing
new the engine adds can ever leak. It NEVER emits raw connections, addresses, processes,
ports, alert detail, tiered counts, or the local firewall stack (posture.checks / LuLu / pf).

    python3 net-sentinel-sanitize.py <source.json> <out.json>
"""
from __future__ import annotations
import json, os, sys, tempfile


def sanitize(src: dict) -> dict:
    ss = src.get("scan_summary", {}) or {}
    plaintext = int(ss.get("plaintext_http_count", 0) or 0)
    # Built explicitly from safe aggregates — never spread/passthrough of the source.
    return {
        "generated_at": src.get("generated_at"),
        "policy": "deny-by-default",
        "tls_only": plaintext == 0,
        "plaintext_http": plaintext,
        "endpoints_managed": int(ss.get("whitelist_size", 0) or 0),
        "engine_live": bool(ss.get("liveness_healthy", False)),
        "note": "Curated aggregate posture only — no addresses, processes, ports, or connection detail is ever published.",
    }


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit("usage: net-sentinel-sanitize.py <source.json> <out.json>")
    src_path, out_path = sys.argv[1], sys.argv[2]
    pub = sanitize(json.loads(open(src_path).read()))
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(out_path) or ".")
    with os.fdopen(fd, "w") as f:
        json.dump(pub, f, indent=2)
        f.write("\n")
    os.replace(tmp, out_path)  # atomic
    print(f"net-sentinel-sanitize: {out_path} — plaintext {pub['plaintext_http']}, "
          f"endpoints {pub['endpoints_managed']}, live {pub['engine_live']}")


if __name__ == "__main__":
    main()
