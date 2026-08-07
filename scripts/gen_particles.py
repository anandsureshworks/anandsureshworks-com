#!/usr/bin/env python3
"""gen_particles.py — single owner of the /particles/ chart state.

Class decision (2026-08-07): chart state is EDITORIAL content (a slot lights when an
instrument ships, roughly quarterly) — so it follows the gen_notes precedent (committed
generator -> data JSON -> widgets read), not the launchd-engine pattern. A daemon that
polls nothing would be a fake sensor.

Widgets that read data/particles.json: /particles/ (chart + counts) and the homepage
Cosmos card (7/17 stat). Neither may hardcode state — this file is the only owner.

Usage:
  python3 scripts/gen_particles.py          # regenerate data/particles.json
  python3 scripts/gen_particles.py --check  # validate committed JSON matches manifest (CI)
"""
import json, sys, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "particles.json"

# ---- the manifest: 17 slots. state: lit | work | queued | never ----
# gen: 1/2/3 for fermion generations, 0 for bosons. col: chart column (1..3 fermions, 4 bosons).
SLOTS = [
    dict(id="u",     sym="u",      name="up",       gen=1, col=1, row=1, state="queued"),
    dict(id="c",     sym="c",      name="charm",    gen=2, col=2, row=1, state="never"),
    dict(id="t",     sym="t",      name="top",      gen=3, col=3, row=1, state="never"),
    dict(id="gamma", sym="γ",      name="photon",   gen=0, col=4, row=1, state="lit", inst="inst-gamma"),
    dict(id="d",     sym="d",      name="down",     gen=1, col=1, row=2, state="queued"),
    dict(id="s",     sym="s",      name="strange",  gen=2, col=2, row=2, state="never"),
    dict(id="b",     sym="b",      name="bottom",   gen=3, col=3, row=2, state="never"),
    dict(id="g",     sym="g",      name="gluon",    gen=0, col=4, row=2, state="lit", inst="inst-g"),
    dict(id="e",     sym="e",      name="electron", gen=1, col=1, row=3, state="lit", inst="inst-e", ring=True),
    dict(id="mu",    sym="μ",      name="muon",     gen=2, col=2, row=3, state="lit", inst="inst-mu", ring=True),
    dict(id="tau",   sym="τ",      name="tau",      gen=3, col=3, row=3, state="never"),
    dict(id="W",     sym="W",      name="W",        gen=0, col=4, row=3, state="work"),
    dict(id="nue",   sym="ν<sub>e</sub>", name="ν-e", gen=1, col=1, row=4, state="lit", inst="inst-nu", ring=True),
    dict(id="numu",  sym="ν<sub>μ</sub>", name="ν-μ", gen=2, col=2, row=4, state="lit", inst="inst-nu", ring=True),
    dict(id="nutau", sym="ν<sub>τ</sub>", name="ν-τ", gen=3, col=3, row=4, state="lit", inst="inst-nu", ring=True),
    dict(id="Z",     sym="Z",      name="Z",        gen=0, col=4, row=4, state="work"),
    dict(id="H",     sym="H",      name="Higgs",    gen=0, col=4, row=5, state="work"),
]
CADENCE = "one instrument per quarter"
LAST_LIT = "2026-08-07"  # this build: the first five instruments ship together

VALID = {"lit", "work", "queued", "never"}

def build():
    assert len(SLOTS) == 17, f"{len(SLOTS)} slots != 17"
    counts = {}
    for s in SLOTS:
        assert s["state"] in VALID, s
        counts[s["state"]] = counts.get(s["state"], 0) + 1
    return {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "cadence": CADENCE,
        "last_lit": LAST_LIT,
        "counts": counts,
        "slots": SLOTS,
    }

def main():
    data = build()
    if "--check" in sys.argv:
        try:
            on_disk = json.loads(OUT.read_text())
        except Exception as e:
            print(f"particles --check: cannot read {OUT}: {e}"); return 1
        a, b = dict(on_disk), dict(data)
        a.pop("generated_at", None); b.pop("generated_at", None)
        if a != b:
            print("particles --check: data/particles.json does not match the manifest — rerun gen_particles.py")
            return 1
        if sum(on_disk["counts"].values()) != 17:
            print("particles --check: counts do not sum to 17"); return 1
        print("particles --check: OK (17 slots, counts consistent)")
        return 0
    tmp = OUT.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")
    tmp.rename(OUT)  # atomic
    print(f"wrote {OUT.relative_to(ROOT)} — counts {data['counts']}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
