#!/usr/bin/env python3
"""gen_circle.py — single owner of data/circle.json (the homepage competence card).

Reads the private ~/.circle-of-competence.json and publishes ONLY whitelisted public
fields: five family rows (id, label, score, updated, prev_score, prev_updated), the
brush-up threshold, and generated_at. Rationale text and branch detail never leave the
source file. The homepage widget reads data/circle.json; it never hardcodes scores.

Trend: if a family's score differs from the previously committed data/circle.json, the
old score/date are recorded as prev_score/prev_updated; otherwise the previous file's
prev_* values carry forward, so a delta persists until the next change.

Refreshed daily by scripts/status-publish.sh (the existing launchd job).

Usage:
  python3 scripts/gen_circle.py          # regenerate data/circle.json (atomic tmp+rename)
  python3 scripts/gen_circle.py --check  # validate committed JSON (CI): exists, generated_at, 5 rows
"""
import json, sys, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "circle.json"
SRC = pathlib.Path.home() / ".circle-of-competence.json"

# public rows: family id -> label shown on the page
PUBLIC = [
    ("ai_llm", "AI & LLM"),
    ("infra_security", "Infra & Security"),
    ("engineering", "Engineering"),
    ("research_learning", "Research & Learning"),
    ("leadership", "Leadership"),
]
ROW_KEYS = {"id", "label", "score", "updated", "prev_score", "prev_updated"}


def load_prev():
    try:
        return {r["id"]: r for r in json.loads(OUT.read_text()).get("rows", [])}
    except Exception:
        return {}


def build(src):
    fams = {f["id"]: f for f in src["families"]}
    prev = load_prev()
    rows = []
    for fid, label in PUBLIC:
        branches = fams[fid]["branches"]
        scores = [b["score"] for b in branches]
        score = round(sum(scores) / len(scores) + 1e-9, 1)
        dates = [b["updated"] for b in branches if b.get("updated")]
        updated = max(dates) if dates else None
        p = prev.get(fid)
        if p is not None and p.get("score") is not None and p["score"] != score:
            prev_score, prev_updated = p["score"], p.get("updated")
        elif p is not None:
            prev_score, prev_updated = p.get("prev_score"), p.get("prev_updated")
        else:
            prev_score, prev_updated = None, None
        rows.append({"id": fid, "label": label, "score": score, "updated": updated,
                     "prev_score": prev_score, "prev_updated": prev_updated})
    return {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "threshold": src["brush_up_threshold"],
        "rows": rows,
    }


def check():
    try:
        d = json.loads(OUT.read_text())
    except Exception as e:
        print(f"circle --check: cannot read {OUT}: {e}"); return 1
    if not d.get("generated_at"):
        print("circle --check: generated_at missing"); return 1
    rows = d.get("rows")
    if not isinstance(rows, list) or len(rows) != 5:
        print(f"circle --check: expected 5 rows, got {len(rows) if isinstance(rows, list) else rows!r}"); return 1
    for r in rows:
        if set(r) != ROW_KEYS:
            print(f"circle --check: row {r.get('id')} has non-whitelisted keys {sorted(set(r) ^ ROW_KEYS)}"); return 1
    print("circle --check: OK (5 rows, whitelisted fields only)")
    return 0


def main():
    if "--check" in sys.argv:
        return check()
    try:
        src = json.loads(SRC.read_text())
        data = build(src)
    except Exception as e:
        print(f"circle: cannot build from {SRC}: {e} — leaving {OUT.name} untouched", file=sys.stderr)
        return 1
    tmp = OUT.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")
    tmp.rename(OUT)  # atomic
    print(f"wrote {OUT.relative_to(ROOT)} — " + ", ".join(f"{r['id']} {r['score']}" for r in data["rows"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
