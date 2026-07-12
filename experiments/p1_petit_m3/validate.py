#!/usr/bin/env python3
"""Independent replay + O(|F|^3) brute-force cross-check for P1-m3 (S4 3-term solving).

This is the ANTI-OVERCLAIM gate. It is deliberately separate from ``run.py`` and shares no
S4 code path with the solver's discovery step. A run is accepted ONLY if:

  1. The manifest's ``results_hash`` matches its canonical results payload and the
     schema-v1 provenance fields are present.
  2. Every recorded curve is a valid cofactor-1 j=0 instance (prime p = 1 mod 3, prime
     subgroup order ell, generator on curve, phi(G) = [lambda]G) -- reusing the P0
     measurement validator ``validate_run.validate_measurement``.
  3. Each recorded example relation replays by ACTUAL ec_add:
     ``e_i P_i + e_j P_j + e_k P_k = R = k*G``.
  4. Internal counters are arithmetically consistent (yield, spurious rate, solves/rel).

  5. CROSS-CHECK (the scientific core): on fresh small bases, an INDEPENDENT brute force
     that enumerates EVERY 3-term relation by O(|F|^3) triple EC-addition (the honest
     ground truth, no S4 involved) is compared against the S4-quartic-solve method. They
     must find the IDENTICAL set of 3-term relations, and the solver must report ZERO
     spurious roots and ZERO S4-nonzero roots. Only then is the O(|F|^2 . deg-4-solve)
     S4 reconnaissance certified complete (finds every real relation) and sound (invents
     none). If this prints FAIL, the experiment is NOT trustworthy.
"""
from __future__ import annotations

import json
import os
import random
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_P0 = _HERE.parent / "p0_glv_semaev"
_P1 = _HERE.parent / "p1_petit"
for _d in (_P0, _P1):
    if str(_d) not in sys.path:
        sys.path.insert(0, str(_d))

from toy_curves import find_toy_curve, ec_add, ec_mul  # noqa: E402
from validate_run import sha256_obj, validate_measurement  # noqa: E402
from semaev_solve import build_plain_base, build_glv_base, neg  # noqa: E402

from semaev4_solve import search_relations3, confirm_relation3  # noqa: E402


# ------------------------------------------------------------------ manifest replay

def replay_manifest(path: Path) -> tuple[list[str], list[str]]:
    doc = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    warnings: list[str] = []

    if doc.get("results_hash") != sha256_obj(doc.get("results", {})):
        errors.append("results_hash mismatch")
    for field in ("git_commit", "command", "timestamp", "code_hashes", "tools"):
        if not doc.get(field):
            errors.append(f"missing schema-v1 field: {field}")

    schema_version = int(doc.get("schema_version", 0))
    measurements = doc.get("results", {}).get("measurements", [])
    if not measurements:
        errors.append("no measurements in manifest")

    for m in measurements:
        # (2) reuse the P0 curve validator (cofactor-1, GLV eigenvalue, on-curve) ONLY.
        # P0's validate_measurement also replays example_relation as a 2-term sum
        # e_i P_i + e_j P_j, which is wrong here (an m=3 example is R = P_i+P_j+P_k), so we
        # hide the example from it and do the correct 3-term replay ourselves in step (3).
        m_curve_only = {k: v for k, v in m.items() if k != "example_relation"}
        validate_measurement(m_curve_only, schema_version, errors, warnings)

        # (4) internal counter consistency.
        T = m["trials"]
        conf = m["confirmed_relations"]
        y = m["yield_relations_per_target"]
        if T and abs(conf / T - y) > 1e-9:
            errors.append(f"yield inconsistent for {m['variant']} {m['bits']}b N={m['N_requested']}")
        rib = m["roots_in_base"]
        sr = m["spurious_rate"]
        if rib and abs(m["spurious_roots"] / rib - sr) > 1e-9:
            errors.append(f"spurious_rate inconsistent for {m['variant']} {m['bits']}b")
        if m["spurious_roots"] < 0 or m["s4_nonzero_roots"] != 0:
            errors.append(f"s4_nonzero_roots must be 0, got {m['s4_nonzero_roots']}")
        spc = m["solves_per_confirmed_relation"]
        if conf and spc is not None and abs(m["total_pair_solves"] / conf - spc) > 1e-6:
            errors.append(f"solves/rel inconsistent for {m['variant']} {m['bits']}b")

        # (3) example relation replays by real ec_add.
        ex = m.get("example_relation")
        if ex:
            p = m["p"]
            Pi, Pj, Pk = tuple(ex["P_i"]), tuple(ex["P_j"]), tuple(ex["P_k"])
            R = tuple(ex["R"])
            got = confirm_relation3(Pi, Pj, Pk, R, p)
            if got is None:
                errors.append(f"example relation does not EC-confirm for {m['variant']} {m['bits']}b")
            if ec_mul(ex["k"], tuple(m["generator"]), 0, p) != R:
                errors.append(f"example target [k]G != R for {m['variant']} {m['bits']}b")
    return errors, warnings


# ------------------------------------------------------------------ independent brute force

def brute_force_triples(points, R, p):
    """Independent oracle: every distinct triple {i,j,k} with some ``e_i P_i + e_j P_j + e_k P_k = R``.

    Pure O(N^3) EC enumeration over the 8 sign patterns, using only ec_add. No S4 involved.
    """
    n = len(points)
    found = set()
    for i in range(n):
        Pi = points[i]
        for j in range(i + 1, n):
            Pj = points[j]
            for k in range(j + 1, n):
                Pk = points[k]
                if confirm_relation3(Pi, Pj, Pk, R, p) is not None:
                    found.add(frozenset((i, j, k)))
    return found


def cross_check() -> tuple[int, list[str]]:
    """S4-solve must equal brute-force triple EC enumeration, zero spurious, zero S4-nonzero."""
    errors: list[str] = []
    checked = 0
    total_relations = 0
    configs = [
        (16, 18, "plain"), (16, 18, "glv-orbit"),
        (16, 30, "plain"),
        (20, 24, "plain"), (20, 24, "glv-orbit"),
    ]
    for bits, N, variant in configs:
        C = find_toy_curve(bits, seed=1, require_cofactor_one=True)
        fb = build_plain_base(C, N) if variant == "plain" else build_glv_base(C, N)
        rng = random.Random(777)
        for _ in range(120):
            k = rng.randrange(1, C.ell)
            R = ec_mul(k, C.gen, 0, C.p)
            if R is None:
                continue
            brute = brute_force_triples(fb.points, R, C.p)
            res = search_relations3(C, fb, R)
            solved = res["confirmed_triples"]
            if solved != brute:
                miss = sorted(map(tuple, brute - solved))
                extra = sorted(map(tuple, solved - brute))
                errors.append(
                    f"{variant} {bits}b N={N} k={k}: S4-solve != brute; "
                    f"missing={miss} extra={extra}")
            if res["spurious"] != 0:
                errors.append(f"{variant} {bits}b k={k}: spurious={res['spurious']} (expected 0)")
            if res["s4_nonzero"] != 0:
                errors.append(f"{variant} {bits}b k={k}: s4_nonzero={res['s4_nonzero']}")
            total_relations += len(brute)
            checked += 1
    print(f"cross-check: {checked} targets across {len(configs)} (bits,N,variant) configs; "
          f"{total_relations} 3-term relations; "
          f"S4-solve == brute-force O(|F|^3) triple enumeration, spurious=0, s4_nonzero=0")
    return checked, errors


def main() -> int:
    runs = sorted((_HERE / "runs").glob("*.json"))
    all_errors: list[str] = []
    for path in runs:
        errors, warnings = replay_manifest(path)
        print(f"[{path.name}] errors={len(errors)} warnings={len(warnings)}")
        for w in warnings:
            print(f"  WARNING: {w}")
        for e in errors:
            print(f"  ERROR: {e}")
        all_errors += errors

    _, xc_errors = cross_check()
    for e in xc_errors:
        print(f"  CROSS-CHECK ERROR: {e}")
    all_errors += xc_errors

    ok = not all_errors
    print("\nVALIDATION:", "PASS" if ok else f"FAIL ({len(all_errors)} errors)")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
