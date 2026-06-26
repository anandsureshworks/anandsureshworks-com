#!/usr/bin/env python3
"""arxiv-pulse — the engine behind the .com "What should I read today?" card.

It fetches the day's arXiv firehose, scores each paper against a transparent
interest model, and writes the top few to JSON. The website widget only *reads*
that JSON — the engine owns the API call (widgets read JSON; engines own calls).

- Endpoint (justified, documented): export.arxiv.org/api/query — public, no auth,
  no secret, no PII. The ONLY outbound call. Add it to ~/.net-sentinel.json if you
  enforce an allowlist.
- Dependencies: none (Python stdlib only).
- Output (atomic tmp+rename), both stamped with an ISO-8601 UTC `generated_at`:
    ~/.arxiv-pulse.json                 — canonical engine output (per convention)
    <repo>/data/arxiv.json              — the publish target the widget reads
- Freshness contract: refreshed daily by launchd; stale if generated_at age > 48h.
- Network calls time out at 15s with exponential backoff; never fire-and-forget.

Usage:
    python3 arxiv-pulse.py            # fetch, score, write both outputs
    python3 arxiv-pulse.py --dry-run  # fetch, score, print JSON; write nothing
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ENDPOINT = "http://export.arxiv.org/api/query"   # upgraded to https by arXiv
CATS = ["cs.AI", "cs.LG", "cs.CL", "cs.CR"]
MAX_FETCH = 60          # the firehose to score
TOP_N = 3               # surfaced on the card
TIMEOUT = 15            # seconds, per outbound call
SCORE_CAP = 18.0        # soft cap that maps raw keyword weight -> 0..0.99
ATOM = "{http://www.w3.org/2005/Atom}"

# Interest model — the "scoring". Transparent, reproducible: a paper's raw score is
# the sum of the weights of the interest phrases that appear in its title/abstract.
INTERESTS = {
    "agent": 3, "autonomous": 3, "agentic": 3, "scheduler": 2, "cron": 2,
    "reliability": 3, "liveness": 3, "monitoring": 2, "observability": 2,
    "failure": 2, "fault": 2, "anomaly": 2, "detection": 2, "robustness": 2,
    "evaluation": 2, "benchmark": 1, "calibration": 2, "uncertainty": 2,
    "llm": 2, "language model": 2, "reasoning": 2, "planning": 2, "tool use": 2,
    "retrieval": 1, "rag": 2, "hallucination": 2,
    "security": 3, "adversarial": 2, "jailbreak": 2, "prompt injection": 3,
    "prompt": 1, "alignment": 2, "safety": 2,
}


def fetch(cats: list[str], n: int) -> bytes:
    query = " OR ".join(f"cat:{c}" for c in cats)
    url = f"{ENDPOINT}?" + urllib.parse.urlencode({
        "search_query": query,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": n,
    })
    last_err: Exception | None = None
    for attempt in range(3):                      # 3 tries, exponential backoff
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "arxiv-pulse/1.0"})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                return resp.read()
        except Exception as err:                  # any transport error -> back off
            last_err = err
            time.sleep(2 ** attempt)
    raise SystemExit(f"arxiv-pulse: fetch failed after 3 tries: {last_err}")


def parse(xml_bytes: bytes) -> list[dict]:
    root = ET.fromstring(xml_bytes)
    papers = []
    for entry in root.findall(f"{ATOM}entry"):
        title = " ".join((entry.findtext(f"{ATOM}title") or "").split())
        summary = " ".join((entry.findtext(f"{ATOM}summary") or "").split())
        raw_id = (entry.findtext(f"{ATOM}id") or "").replace("http://", "https://")
        url = re.sub(r"v\d+$", "", raw_id)        # stable link, no version suffix
        cat_el = entry.find(f"{ATOM}category")
        cat = cat_el.get("term") if cat_el is not None else ""
        if title and url:
            papers.append({"t": title, "url": url, "summary": summary, "c": cat})
    return papers


def score(paper: dict) -> int:
    text = (paper["t"] + " " + paper["summary"]).lower()
    return sum(w for phrase, w in INTERESTS.items() if phrase in text)


def build(papers: list[dict]) -> dict:
    ranked = sorted(((score(p), p) for p in papers), key=lambda x: x[0], reverse=True)
    top = [{
        "t": p["t"],
        "url": p["url"],
        "c": p["c"],
        "s": round(min(0.99, raw / SCORE_CAP), 2),
    } for raw, p in ranked[:TOP_N]]
    now = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    return {
        "source": "arxiv-pulse",
        "generated_at": now,
        "scored": len(papers),
        "_contract": {
            "owner": "arxiv-pulse (this engine) — owns the arXiv fetch + relevance scoring",
            "widget": "read-only; renders this file, computes nothing",
            "interval": "daily; stale if generated_at age > 48h",
        },
        "papers": top,
    }


def atomic_write(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")
    os.replace(tmp, path)                          # atomic on POSIX


def main() -> int:
    data = build(parse(fetch(CATS, MAX_FETCH)))
    if "--dry-run" in sys.argv:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return 0
    home_out = Path.home() / ".arxiv-pulse.json"
    repo_out = Path(__file__).resolve().parent.parent / "data" / "arxiv.json"
    atomic_write(home_out, data)
    atomic_write(repo_out, data)
    print(f"arxiv-pulse: scored {data['scored']}, wrote top {len(data['papers'])} "
          f"-> {home_out} + {repo_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
