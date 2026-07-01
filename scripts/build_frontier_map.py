#!/usr/bin/env python3
"""Build data/frontier_map.json — the machine-actionable frontier map (Track A).

Turns the corpus + barriers prose into structured, queryable data: for every one of the
486 atomic claims, an explicit status and (if blocked) the *named missing Mathlib
foundation* that blocks it; plus a foundation registry saying what each missing foundation
would unlock. A future reasoning agent ingests this to see the whole problem and where the
frontier is — which is the single most valuable layer of the environment (see
ENVIRONMENT_PLAN.md, L2 / Track A).

This asserts NO solution to ECDLP; it is a rigorous map of known-vs-blocked, honest about
the barriers being possibly permanent.

Run: python3 scripts/build_frontier_map.py            # writes data/frontier_map.json
     python3 scripts/build_frontier_map.py --query weil_pairing   # ask what a foundation unlocks
"""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "data" / "KG_CLAIM_FORMALIZATION_v1.csv"
VERIFIED = ROOT / "VERIFIED.md"
OUT = ROOT / "data" / "frontier_map.json"

# The missing-foundation registry: what Mathlib lacks, and what it would unlock. `key` is
# matched from a claim's mathlib_area (below). Descriptions are the honest gap statements.
FOUNDATIONS = {
    "weil_pairing": {
        "status": "missing_from_mathlib",
        "mathlib_gap": "No Weil/Tate pairing eₙ. Needs divisors, function fields, Miller's "
                       "algorithm. Gates the MOV/Frey-Rück transfer reduction itself.",
        "leverage": "highest",
        "effort": "months (research-grade)",
    },
    "point_counting": {
        "status": "missing_from_mathlib",
        "mathlib_gap": "No Schoof / point-counting; #E(𝔽_p)=n cannot be computed (native_decide "
                       "can't enumerate 2^256 points). Gates the GLV [λ]-eigenvalue claim and "
                       "the ℤ/n-module structure needed to instantiate the protocol algebra.",
        "leverage": "high",
        "effort": "months (research-grade)",
    },
    "cost_model": {
        "status": "missing_from_mathlib",
        "mathlib_gap": "No group-operation / oracle-query cost model, so exact Θ running times "
                       "(index calculus, distinguished points) can't be stated. The generic "
                       "Ω(√p) core was formalized by sidestepping this.",
        "leverage": "medium",
        "effort": "weeks-months",
    },
    "lattice_reduction": {
        "status": "missing_from_mathlib",
        "mathlib_gap": "No LLL/BKZ/CVP. Blocks HNP / biased-nonce ECDSA attack formalizations.",
        "leverage": "medium",
        "effort": "months",
    },
    "semaev_polynomials": {
        "status": "partial_in_mathlib",
        "mathlib_gap": "MvPolynomial exists but not the elliptic summation polynomials Sₙ "
                       "(index calculus over extension fields).",
        "leverage": "medium",
        "effort": "weeks-months",
    },
    "quantum_cost": {
        "status": "out_of_scope",
        "mathlib_gap": "No quantum circuit cost model (Shor-style resource estimates). Out of "
                       "scope for Mathlib.",
        "leverage": "low (out of scope)",
        "effort": "n/a",
    },
    "curve_depth": {
        "status": "partial_in_mathlib",
        "mathlib_gap": "Mathlib has EllipticCurve + group law, but not the deeper ECDLP "
                       "constructions (higher division polynomials, torsion structure "
                       "E[n]≅(ℤ/n)², isogeny depth). Partly tractable — the active Track-B DAG.",
        "leverage": "medium",
        "effort": "weeks each rung",
    },
}

# map a corpus mathlib_area string -> (status, blocking_foundation | None)
def classify(formal_status: str, area: str) -> tuple[str, str | None]:
    if formal_status in ("informal_only", "scope_meta"):
        return "informal", None
    a = area.lower()
    if "cost model" in a and "quantum" not in a:
        return "blocked", "cost_model"
    if "quantum" in a:
        return "blocked", "quantum_cost"
    if "lattice" in a:
        return "blocked", "lattice_reduction"
    if "mvpolynomial" in a:
        return "blocked", "semaev_polynomials"
    if "isogeny" in a:
        return "blocked", "weil_pairing"
    if "ellipticcurve" in a:
        return "partial", "curve_depth"
    if "orderofelement" in a or "subgroup" in a:
        return "tractable", None
    if "unassigned" in a or not a:
        return "unassigned", None
    return "tractable", None


def main(argv: list[str]) -> int:
    rows = list(csv.DictReader(CORPUS.open(encoding="utf-8")))
    vtext = VERIFIED.read_text(encoding="utf-8")
    verified_rows = len(re.findall(r"^\|.*\| (?:proved|proved[¹²]| ?proved.*)\|?\s*$", vtext, re.M))

    claims = []
    status_ct: Counter = Counter()
    foundation_ct: Counter = Counter()
    for r in rows:
        cid = (r.get("claim_id", "") or "").strip()
        fs = (r.get("formal_status", "") or "").strip()
        area = (r.get("mathlib_area", "") or "").strip()
        status, foundation = classify(fs, area)
        verified = bool(cid and cid in vtext)
        if verified:
            status = "verified"
        status_ct[status] += 1
        if foundation:
            foundation_ct[foundation] += 1
        claims.append({
            "id": cid, "formal_status": fs, "status": status,
            "blocking_foundation": foundation, "mathlib_area": area,
            "verified": verified,
        })

    # attach unlock counts to the foundation registry
    foundations = {}
    for k, v in FOUNDATIONS.items():
        foundations[k] = {**v, "blocks_corpus_claims": foundation_ct.get(k, 0)}

    total = len(rows)
    assigned = total - status_ct.get("unassigned", 0)
    doc = {
        "meta": {
            "purpose": "Machine-actionable frontier map of ECDLP formalization. Verified "
                       "facts + precisely-mapped barriers. Asserts NO solution to ECDLP.",
            "corpus_claims": total,
            "verified_ledger_rows": verified_rows,
            "frontier_completeness_pct": round(100 * assigned / total, 1),
            "regenerate": "python3 scripts/build_frontier_map.py",
        },
        "status_summary": dict(status_ct.most_common()),
        "foundations": foundations,
        "claims": claims,
    }
    OUT.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} — {total} claims, "
          f"frontier completeness {doc['meta']['frontier_completeness_pct']}% "
          f"(assigned status; {status_ct.get('unassigned',0)} still unassigned)")
    print("status:", dict(status_ct.most_common()))
    print("blocked-by-foundation:", dict(foundation_ct.most_common()))
    return 0


def query(foundation: str) -> int:
    doc = json.loads(OUT.read_text(encoding="utf-8"))
    f = doc["foundations"].get(foundation)
    if not f:
        print(f"unknown foundation {foundation!r}. Known: {list(doc['foundations'])}")
        return 1
    print(f"# {foundation}\nstatus: {f['status']}\ngap: {f['mathlib_gap']}\n"
          f"leverage: {f['leverage']}  effort: {f['effort']}\n"
          f"blocks {f['blocks_corpus_claims']} corpus claims")
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--query":
        raise SystemExit(query(sys.argv[2]))
    raise SystemExit(main(sys.argv))
