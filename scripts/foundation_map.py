#!/usr/bin/env python3
"""Foundation dependency map: corpus claim -> missing Lean object that unlocks it.

Turns the read-only claim corpus into a *prioritized foundation roadmap*
(`notes/FOUNDATION_ROADMAP.md`): instead of asking "which claims are directly
provable" (few), it asks "which missing Lean object, if built, unlocks the most
claims" (high leverage). A claim may depend on more than one object.

Run: python3 scripts/foundation_map.py
"""
from __future__ import annotations
import csv, collections, re
from pathlib import Path

CSV = Path("data/KG_CLAIM_FORMALIZATION_v1.csv")

# (missing Lean object, regex signature over formal_statement+label+area)
FOUND = [
    ("Weil/Tate pairing eₙ",                  r"pairing|weil|tate|e_n|frey|embedding degree|mov"),
    ("Elliptic nets / EDS (Stange)",          r"elliptic net|\beds\b|net polynomial|stange|lauter"),
    ("p-adic log / formal group (Smart/Satoh)", r"p-adic|padic|formal group|anomalous|satoh|smart|lift|trace.*one|qp\b"),
    ("Semaev summation polynomials",          r"semaev|summation polynomial|index calculus"),
    ("Isogeny / endomorphism theory",         r"isogeny|endomorphism|glv|frobenius|characteristic polynomial"),
    ("Point counting / #E structure",         r"#e|cardinality|order of the group|schoof|point count"),
    ("Divisor / function field",              r"divisor|function field|riemann|principal"),
    ("Transfer / CRT / Cheon",                r"cheon|crt|multidivisor|ghs|transfer"),
]
DROP = {"informal_only", "scope_meta"}


def main() -> int:
    rows = list(csv.DictReader(CSV.open(encoding="utf-8")))
    buckets: dict[str, list[str]] = collections.defaultdict(list)
    n = 0
    for r in rows:
        if (r.get("formal_status") or "") in DROP:
            continue
        txt = " ".join([r.get("formal_statement") or "", r.get("label") or "",
                        r.get("mathlib_area") or ""]).lower()
        if not txt.strip():
            continue
        n += 1
        hits = [name for name, pat in FOUND if re.search(pat, txt)]
        for h in (hits or ["(no missing object — formalizable now)"]):
            buckets[h].append(r.get("claim_id"))

    print(f"formalizable-ish claims: {n}\n")
    order = [name for name, _ in FOUND] + ["(no missing object — formalizable now)"]
    for name in order:
        ids = buckets.get(name, [])
        if ids:
            print(f"{name}: unlocks {len(ids)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
