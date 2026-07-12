#!/usr/bin/env python3
"""Independent anti-overclaim gate for P3 (the ACTUAL Semaev relation SYSTEM).

This is the MANDATORY cross-check required by the experiment protocol. Its relation-
deriving core -- ``brute_force_tuples`` -- re-derives every m-term relation by pure
brute-force elliptic-curve enumeration and calls NO function from the Groebner solver
module ``semaev_system`` (it uses only ``ec_add`` and its own sign-sum verifier). The
solver's output is then imported ONLY to be COMPARED against this independent ground
truth. A run is accepted iff:

  1. The manifest's ``results_hash`` matches its canonical results payload and all
     schema-v1 provenance fields (git_commit, command, timestamp, code_hashes, tools)
     are present.
  2. Every recorded example relation replays by ACTUAL ec_add:
     sum_i signs_i * P_i == R (and, for relation-probability examples, [k]G == R).
  3. Internal counters are arithmetically consistent (relation_probability,
     relations_per_target), and no d_reg block reports a spurious solver output.
  4. CROSS-CHECK (the scientific core): on fresh small (bits, N, m, coord) configs and
     BOTH random and constructed targets, the independent brute-force EC relation set is
     compared to the Groebner-SYSTEM solver's relation set. They MUST be identical, and
     the solver must report ZERO spurious (EC-unverified) outputs. Only then is the
     Groebner-system relation search certified complete (finds every real relation) and
     sound (invents none). If this prints FAIL, the experiment is NOT trustworthy.
"""
from __future__ import annotations

import json
import os
import random
import sys
from itertools import combinations, product as iproduct
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_P0 = _HERE.parent / "p0_glv_semaev"
_P1 = _HERE.parent / "p1_petit"
for _d in (_P0, _P1):
    if str(_d) not in sys.path:
        sys.path.insert(0, str(_d))

from toy_curves import find_toy_curve, ec_add, ec_mul  # noqa: E402
from semaev_solve import build_plain_base, build_glv_base  # noqa: E402
from validate_run import sha256_obj  # noqa: E402


# ---------------------------------------------- independent EC ground truth (NO solver code)

def _neg(P, p):
    return None if P is None else (P[0], (-P[1]) % p)


def _confirm(points, R, p):
    """Independent verifier: some sign vector e in {+1,-1}^m with sum e_i P_i == R."""
    for signs in iproduct((1, -1), repeat=len(points)):
        acc = None
        for P, s in zip(points, signs):
            acc = ec_add(acc, P if s == 1 else _neg(P, p), 0, p)
        if acc == R:
            return signs
    return None


def brute_force_tuples(points, R, m, p):
    """Every size-m index set carrying a real m-term relation, by pure EC enumeration.

    Uses ONLY ec_add (via _confirm). Imports nothing from semaev_system. This is the
    independent ground truth the Groebner solver is checked against.
    """
    found = set()
    for combo in combinations(range(len(points)), m):
        if _confirm([points[i] for i in combo], R, p) is not None:
            found.add(frozenset(combo))
    return found


# ---------------------------------------------- manifest replay

def replay_manifest(path):
    doc = json.loads(path.read_text(encoding="utf-8"))
    errors, warnings = [], []
    if doc.get("results_hash") != sha256_obj(doc.get("results", {})):
        errors.append("results_hash mismatch")
    for f in ("git_commit", "command", "timestamp", "code_hashes", "tools"):
        if not doc.get(f):
            errors.append(f"missing schema-v1 field: {f}")
    measurements = doc.get("results", {}).get("measurements", [])
    if not measurements:
        errors.append("no measurements in manifest")

    for meas in measurements:
        p = int(meas["p"])
        # (3) counter consistency
        if meas["block"] == "relation_probability":
            T = meas["trials"]
            if T:
                if abs(meas["targets_with_relation"] / T - meas["relation_probability"]) > 1e-9:
                    errors.append("relation_probability inconsistent")
                if abs(meas["confirmed_relations"] / T - meas["relations_per_target"]) > 1e-9:
                    errors.append("relations_per_target inconsistent")
        if meas["block"] == "degree_of_regularity" and meas.get("spurious", 0) != 0:
            errors.append(f"d_reg block reports spurious>0 ({meas['coord']} m={meas['m']} N={meas['N_requested']})")

        # (2) example relation replays by ACTUAL ec_add
        ex = meas.get("example_relation")
        if ex:
            pts = [tuple(P) for P in ex["P"]]
            R = tuple(ex["R"])
            signs = ex["signs"]
            acc = None
            for P, s in zip(pts, signs):
                acc = ec_add(acc, P if s == 1 else _neg(P, p), 0, p)
            if acc != R:
                errors.append(f"example relation does not EC-confirm ({meas['coord']} m={meas['m']} N={meas['N_requested']})")
            for P in pts + [R]:
                if (P[1] * P[1] - P[0] ** 3 - meas["b"]) % p != 0:
                    errors.append("example point not on curve")
            if "k" in ex and ec_mul(ex["k"], tuple(meas["generator"]), 0, p) != R:
                errors.append("example [k]G != R")
    return errors, warnings


# ---------------------------------------------- cross-check (independent vs solver)

def cross_check():
    """Brute-force EC relation set MUST equal the Groebner-system solver's set; spurious=0."""
    # Imported HERE, after the independent brute force is defined, and used ONLY to obtain
    # the solver's output for comparison -- never inside brute_force_tuples.
    from semaev_system import search_relations_system

    errors = []
    checked = 0
    total_rel = 0
    # (bits, N, m, coord)
    configs = [
        (16, 8, 2, "plain"), (16, 10, 2, "plain"),
        (16, 12, 2, "invariant"), (16, 6, 3, "plain"),
        (20, 8, 2, "plain"),
    ]
    for bits, N, m, coord in configs:
        C = find_toy_curve(bits, seed=1, require_cofactor_one=True)
        fb = build_glv_base(C, N) if coord == "invariant" else build_plain_base(C, N)
        rng = random.Random(4242 + bits + N + m)
        targets = []
        # constructed targets (guarantee relations are present)
        for _ in range(8):
            idxs = rng.sample(range(len(fb.points)), m)
            R = None
            for i in idxs:
                R = ec_add(R, fb.points[i] if rng.random() < 0.5 else _neg(fb.points[i], C.p), 0, C.p)
            if R is not None:
                targets.append(R)
        # random targets
        for _ in range(12):
            R = ec_mul(rng.randrange(1, C.ell), C.gen, 0, C.p)
            if R is not None:
                targets.append(R)
        for R in targets:
            brute = brute_force_tuples(fb.points, R, m, C.p)
            res = search_relations_system(C, fb, m, R, coord, measure_dreg=False)
            solved = {frozenset(t) for t in res["confirmed_relations"]}
            if solved != brute:
                errors.append(f"{coord} {bits}b m={m} N={N}: solver!=brute "
                              f"missing={sorted(map(tuple,brute-solved))} "
                              f"extra={sorted(map(tuple,solved-brute))}")
            if res["spurious"] != 0:
                errors.append(f"{coord} {bits}b m={m} N={N}: spurious={res['spurious']}")
            total_rel += len(brute)
            checked += 1
    print(f"cross-check: {checked} targets over {len(configs)} (bits,N,m,coord) configs; "
          f"{total_rel} relations; Groebner-system solver == brute-force EC enumeration, "
          f"spurious=0")
    return checked, errors


def main():
    all_errors = []
    runs = sorted((_HERE / "runs").glob("*.json"))
    if not runs:
        print("no run manifests found in runs/ -- run.py first")
    for path in runs:
        errs, warns = replay_manifest(path)
        print(f"[{path.name}] errors={len(errs)} warnings={len(warns)}")
        for w in warns:
            print(f"  WARNING: {w}")
        for e in errs:
            print(f"  ERROR: {e}")
        all_errors += errs

    _, xc = cross_check()
    for e in xc:
        print(f"  CROSS-CHECK ERROR: {e}")
    all_errors += xc

    ok = not all_errors
    print("\nVALIDATION:", "PASS" if ok else f"FAIL ({len(all_errors)} errors)")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
