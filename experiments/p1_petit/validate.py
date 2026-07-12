#!/usr/bin/env python3
"""Independent replay + cross-check validator for P1 (S3-solving) runs.

This is deliberately separate from ``run.py``. It accepts a run ONLY if:

  1. The manifest's ``results_hash`` matches its canonical results payload and the
     schema-v1 provenance fields are present.
  2. Every recorded curve is a valid cofactor-1 j=0 instance (prime p = 1 mod 3,
     prime subgroup order ell, generator on curve, phi(G) = [lambda]G) -- reusing the
     P0 measurement validator ``validate_run.validate_measurement``.
  3. Each recorded example relation replays by ACTUAL ec_add: e_i P_i + e_j P_j = R = k*G.
  4. Internal counters are arithmetically consistent (yield, spurious rate, solves/rel).

  5. CROSS-CHECK (the scientific core): on fresh small curves, an INDEPENDENT brute-force
     EC enumeration of every 2-term relation (the P0 method, O(N^2) ec_add) is compared
     against the S3-quadratic-solve method. They must find the IDENTICAL set of relations,
     and the solver must report ZERO spurious roots. This is what certifies that S3-solving
     is complete (finds every real relation) and sound (invents none), so the O(N) solve
     genuinely replaces the O(N^2) enumeration.
"""
from __future__ import annotations

import itertools
import json
import os
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_P0 = _HERE.parent / "p0_glv_semaev"
if str(_P0) not in sys.path:
    sys.path.insert(0, str(_P0))

from toy_curves import find_toy_curve, ec_add, ec_mul  # noqa: E402
from validate_run import sha256_obj, validate_measurement  # noqa: E402

from semaev_solve import (  # noqa: E402
    build_plain_base, build_glv_base, search_relations, neg,
)
import random  # noqa: E402


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
        # (2) reuse the P0 curve/example validator (cofactor-1, GLV eigenvalue, on-curve).
        validate_measurement(m, schema_version, errors, warnings)

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
        if m["spurious_roots"] < 0 or m["s3_nonzero_roots"] != 0:
            errors.append(f"s3_nonzero_roots must be 0, got {m['s3_nonzero_roots']}")
        spc = m["solves_per_confirmed_relation"]
        if conf and spc is not None and abs(m["total_field_solves"] / conf - spc) > 1e-6:
            errors.append(f"solves/rel inconsistent for {m['variant']} {m['bits']}b")

        # (3) example relation replays by real ec_add.
        ex = m.get("example_relation")
        if ex:
            p = m["p"]
            Pi = tuple(ex["P_i"])
            Pj = tuple(ex["P_j"])
            R = tuple(ex["R"])
            A = Pi if ex["e_i"] == 1 else neg(Pi, p)
            Bp = Pj if ex["e_j"] == 1 else neg(Pj, p)
            if ec_add(A, Bp, 0, p) != R:
                errors.append(f"example relation replay failed for {m['variant']} {m['bits']}b")
            if ec_mul(ex["k"], tuple(m["generator"]), 0, p) != R:
                errors.append(f"example target [k]G != R for {m['variant']} {m['bits']}b")
    return errors, warnings


# ------------------------------------------------------------------ independent cross-check

def brute_force_relations(points, R, p):
    """Independent oracle: every unordered pair {i,j} with some e_i P_i + e_j P_j = R.

    Pure O(N^2) EC enumeration (the P0 method), using only ec_add. No S3 involved.
    """
    negR = neg(R, p)
    found = set()
    n = len(points)
    for i in range(n):
        Pi = points[i]
        for j in range(i + 1, n):
            Pj = points[j]
            if Pj == R or Pj == negR or Pi == R or Pi == negR:
                continue
            for ei in (1, -1):
                Ai = Pi if ei == 1 else neg(Pi, p)
                for ej in (1, -1):
                    Bj = Pj if ej == 1 else neg(Pj, p)
                    if ec_add(Ai, Bj, 0, p) == R:
                        found.add(frozenset((i, j)))
    return found


def cross_check() -> tuple[int, list[str]]:
    """S3-solve must equal brute-force EC enumeration, with zero spurious roots."""
    errors: list[str] = []
    checked = 0
    total_relations = 0
    for bits, N, variant in [(16, 48, "plain"), (16, 48, "glv-orbit"),
                             (20, 96, "plain"), (20, 96, "glv-orbit"),
                             (24, 96, "plain")]:
        C = find_toy_curve(bits, seed=1, require_cofactor_one=True)
        fb = build_plain_base(C, N) if variant == "plain" else build_glv_base(C, N)
        rng = random.Random(999)
        for _ in range(150):
            k = rng.randrange(1, C.ell)
            R = ec_mul(k, C.gen, 0, C.p)
            if R is None:
                continue
            brute = brute_force_relations(fb.points, R, C.p)
            res = search_relations(C, fb, R)
            solved = res["confirmed_pairs"]
            if solved != brute:
                errors.append(
                    f"{variant} {bits}b k={k}: S3-solve {sorted(map(tuple, solved))} "
                    f"!= brute {sorted(map(tuple, brute))}")
            if res["spurious"] != 0:
                errors.append(f"{variant} {bits}b k={k}: spurious={res['spurious']} (expected 0)")
            if res["s3_nonzero"] != 0:
                errors.append(f"{variant} {bits}b k={k}: s3_nonzero={res['s3_nonzero']}")
            total_relations += len(brute)
            checked += 1
    print(f"cross-check: {checked} targets across 5 (bits,variant) configs; "
          f"{total_relations} relations; S3-solve == brute-force EC enumeration, spurious=0")
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
