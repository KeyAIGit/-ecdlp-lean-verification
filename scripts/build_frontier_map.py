#!/usr/bin/env python3
"""Build data/frontier_map.json — the machine-actionable frontier map (Track A).

Turns the corpus + barriers prose into structured, queryable data: for every one of the
486 atomic claims, an explicit status and (if blocked) the *named missing Mathlib
foundation* that blocks it; plus a foundation registry saying what each missing foundation
would unlock. A future reasoning agent ingests this to see the whole problem and where the
frontier is — which is the single most valuable layer of the environment (see
ROADMAP.md; the frontier map is the L2 layer).

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
# Adversarially-verified coverage overrides (see the file's _meta for provenance): each maps a
# corpus claim to verified/partial via a named kernel-verified theorem, confirmed by a skeptic pass.
OVERRIDES = ROOT / "data" / "corpus_coverage_overrides.json"
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

# Content keyword heuristics for claims the corpus left mathlib_area-unassigned. Ordered by
# priority. Each -> (status, blocking_foundation | None). Marked confidence="heuristic".
HEURISTICS = [
    # empirical / survey / commentary prose — not a formal math statement
    (("the authors", "the paper", "the study", "recovered", "reports ", "no evidence",
      "we survey", "in practice", "real-world", "dataset", "bitcoin", "ethereum", "ripple",
      "https", "ssh", "hundreds of", "database"), "informal", None),
    # quantum resource estimates
    (("quantum", "shor", "qubit", "circuit"), "blocked", "quantum_cost"),
    # lattice / HNP / biased-nonce
    (("lattice", "lll", "bkz", " cvp", "hidden number", "biased nonce", "nonce reuse",
      "bounded error term", "modular equation", "short vector"), "blocked", "lattice_reduction"),
    # index calculus / Semaev summation polynomials
    (("semaev", "summation polynomial", "index calculus", "relation step", "relation search",
      "smooth", "factor base"), "blocked", "semaev_polynomials"),
    # pairing / transfer / isogeny depth
    (("weil", "tate pairing", " pairing", "mov", "frey", "embedding degree", "isogeny",
      "supersingular"), "blocked", "weil_pairing"),
    # complexity / cost statements
    (("running time", "time complexity", "subexponential", "operations", "queries",
      "oracle", "cost ", "parity", "number of group"), "blocked", "cost_model"),
    # curve / torsion / division-polynomial / EDS / GLV depth (partly tractable, Track B)
    (("torsion", "division polynomial", "elliptic divisibility", " eds", "endomorphism",
      "lambda", "glv", "decomposition", "j-invariant", "trace of frobenius"), "partial", "curve_depth"),
    # in-Mathlib group theory (order / subgroup / generic prime-order group facts)
    (("prime order", "generic group", "order of", "subgroup", "cyclic", "lagrange",
      "pohlig", "discrete log"), "tractable", None),
]


def classify(formal_status: str, area: str, statement: str = "") -> tuple[str, str | None, str]:
    """Return (status, blocking_foundation|None, confidence). confidence in {corpus, heuristic}."""
    if formal_status in ("informal_only", "scope_meta"):
        return "informal", None, "corpus"
    a = area.lower()
    if "cost model" in a and "quantum" not in a:
        return "blocked", "cost_model", "corpus"
    if "quantum" in a:
        return "blocked", "quantum_cost", "corpus"
    if "lattice" in a:
        return "blocked", "lattice_reduction", "corpus"
    if "mvpolynomial" in a:
        return "blocked", "semaev_polynomials", "corpus"
    if "isogeny" in a:
        return "blocked", "weil_pairing", "corpus"
    if "ellipticcurve" in a:
        return "partial", "curve_depth", "corpus"
    if "orderofelement" in a or "subgroup" in a:
        return "tractable", None, "corpus"
    if not ("unassigned" in a or not a):
        return "tractable", None, "corpus"
    # mathlib_area unassigned by the corpus — fall back to content heuristics.
    s = statement.lower()
    for keys, status, foundation in HEURISTICS:
        if any(k in s for k in keys):
            return status, foundation, "heuristic"
    return "unassigned", None, "heuristic"


def main(argv: list[str]) -> int:
    rows = list(csv.DictReader(CORPUS.open(encoding="utf-8")))
    vtext = VERIFIED.read_text(encoding="utf-8")
    overrides = {}
    if OVERRIDES.exists():
        overrides = (json.loads(OVERRIDES.read_text(encoding="utf-8")) or {}).get("overrides", {})
    # Headline ledger-row count comes from the ONE canonical source (stats.json → VERIFIED.md's
    # canonical figure), never re-tallied here, so this map can't disagree with STATUS.md.
    # Fall back to the regex tally only if stats.json is absent (first-run bootstrap).
    stats_path = ROOT / "data" / "stats.json"
    stats = json.loads(stats_path.read_text(encoding="utf-8")) if stats_path.exists() else {}
    verified_rows = int(stats.get("ledger_rows") or
                        len(re.findall(r"^\|.*\| (?:proved|proved[¹²]| ?proved.*)\|?\s*$", vtext, re.M)))

    claims = []
    status_ct: Counter = Counter()
    foundation_ct: Counter = Counter()
    conf_ct: Counter = Counter()
    for r in rows:
        cid = (r.get("claim_id", "") or "").strip()
        fs = (r.get("formal_status", "") or "").strip()
        area = (r.get("mathlib_area", "") or "").strip()
        stmt = (r.get("formal_statement", "") or r.get("label", "") or "").strip()
        status, foundation, confidence = classify(fs, area, stmt)
        verified = bool(cid and cid in vtext)
        if verified:
            status, confidence = "verified", "corpus"
        # adversarially-verified coverage overrides win (verified/partial via a named theorem)
        discharged_by = None
        ov = overrides.get(cid)
        if ov:
            status = ov.get("status", status)
            discharged_by = ov.get("theorem") or None
            confidence = "verified-remap"
            verified = (status == "verified")
        status_ct[status] += 1
        conf_ct[confidence] += 1
        if foundation:
            foundation_ct[foundation] += 1
        claims.append({
            "id": cid, "formal_status": fs, "status": status,
            "blocking_foundation": foundation, "confidence": confidence,
            "mathlib_area": area, "verified": verified,
            "discharged_by": discharged_by,
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
        "confidence_summary": dict(conf_ct.most_common()),
        "foundations": foundations,
        "claims": claims,
    }
    OUT.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} — {total} claims, "
          f"frontier completeness {doc['meta']['frontier_completeness_pct']}% "
          f"(assigned status; {status_ct.get('unassigned',0)} still unassigned)")
    print("status:", dict(status_ct.most_common()))
    print("confidence:", dict(conf_ct.most_common()))
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
