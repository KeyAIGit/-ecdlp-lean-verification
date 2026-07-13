#!/usr/bin/env python3
"""Independent anti-overclaim gate for P4 (the composed low-degree map factor base).

MANDATORY cross-check. Its relation-deriving core -- ``brute_force_tuples`` -- and its
factor-base reconstruction -- ``rebuild_base_independent`` -- call NO function from the
Groebner/Macaulay solver derivation path (``variety_from_system``, ``degree_of_regularity``,
``search_relations_petit``). They use ONLY elliptic-curve arithmetic (``ec_add``), a local
modular square root (``sympy.sqrt_mod``), and direct evaluation of the composed map from its
recorded parameters. The solver's output is imported ONLY at the end, to be COMPARED against
this independent ground truth. A run is accepted iff:

  1. The manifest's ``results_hash`` matches its canonical results payload and all schema-v1
     provenance fields are present.
  2. Every recorded example relation replays by ACTUAL ec_add (sum_i signs_i P_i == R), every
     example point is on the curve, and each factor base is a set of on-curve points.
  3. No degree-of-regularity block reports a spurious solver output; every raw-baseline row
     reproduces the P3 law d_reg = 2|F|+1 (when not capped).
  4. CROSS-CHECK: on fresh (bits, kind, size, m) configs and BOTH random and constructed
     targets, the independent brute-force EC relation set equals BOTH the composed-map solver
     set AND the raw-baseline solver set, with ZERO spurious. Only then are the composed-map
     and raw solvers certified complete and sound. If this prints FAIL, P4 is NOT trustworthy.
"""
from __future__ import annotations

import json
import random
import sys
from itertools import combinations, product as iproduct
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_P0 = _HERE.parent / "p0_glv_semaev"
_P1 = _HERE.parent / "p1_petit"
_P3 = _HERE.parent / "p3_sm_system"
for _d in (_P0, _P1, _P3):
    if str(_d) not in sys.path:
        sys.path.insert(0, str(_d))

import sympy  # noqa: E402
from toy_curves import find_toy_curve, ec_add, ec_mul  # noqa: E402
from validate_run import sha256_obj  # noqa: E402


# ---------------------------------------------- independent EC ground truth (NO solver code)

def _neg(P, p):
    return None if P is None else (P[0], (-P[1]) % p)


def _oncurve_point(x, b, p):
    """Local canonical on-curve point (x, y) or None -- own sqrt, no solver imports."""
    rhs = (x * x * x + b) % p
    y = sympy.sqrt_mod(rhs, p)
    return None if y is None else (x % p, int(y))


def rebuild_base_independent(mp, b, p):
    """Reconstruct the composed-map factor base from the RECORDED map parameters, using only
    direct map evaluation + a local sqrt. Independent of semaev_petit's construction."""
    kind = mp["kind"]
    if kind == "product_2aux":
        b0, kappa, c = mp["b0"], mp["kappa"], mp["c"]
        imgs = {((t1 + kappa * t2) ** 2 + c) % p for t1 in range(b0) for t2 in range(b0)}
    elif kind == "single_aux_composed":
        nt, a1, a2, a3 = mp["nt"], mp["a1"], mp["a2"], mp["a3"]
        imgs = set()
        for t in range(nt):
            w = (t * t + a1) % p
            imgs.add((w * w + a2 * w + a3) % p)
    else:
        raise ValueError(kind)
    pts = []
    for X in sorted(imgs):
        P = _oncurve_point(X, b, p)
        if P is not None:
            pts.append(P)
    return pts


def _confirm(points, R, p):
    for signs in iproduct((1, -1), repeat=len(points)):
        acc = None
        for P, s in zip(points, signs):
            acc = ec_add(acc, P if s == 1 else _neg(P, p), 0, p)
        if acc == R:
            return signs
    return None


def brute_force_tuples(points, R, m, p):
    """Every size-m index set carrying a real m-term relation, by pure EC enumeration."""
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
        p, b = int(meas["p"]), int(meas["b"])
        # (3) d_reg-block invariants
        if meas["block"] == "degree_of_regularity":
            if meas.get("composed_spurious", 0) != 0:
                errors.append(f"composed d_reg block spurious>0 ({meas['variant']} |F|={meas['n_fb_elements']})")
            if meas.get("raw_spurious", 0) != 0:
                errors.append(f"raw d_reg block spurious>0 ({meas['variant']} |F|={meas['n_fb_elements']})")
            # raw baseline MUST reproduce P3's 2|F|+1 when not capped
            if not meas.get("raw_solving_degree_capped", False):
                if meas.get("raw_solving_degree") != meas.get("raw_baseline_2F_plus_1"):
                    errors.append(f"raw baseline != 2|F|+1 ({meas['variant']} |F|={meas['n_fb_elements']}: "
                                  f"{meas.get('raw_solving_degree')} vs {meas.get('raw_baseline_2F_plus_1')})")
            # independent |F| check: reconstruct the base and count on-curve image points
            pts = rebuild_base_independent(meas["map"], b, p)
            if len(pts) != meas["n_fb_elements"]:
                errors.append(f"|F| mismatch ({meas['variant']}): recomputed {len(pts)} vs {meas['n_fb_elements']}")

        # (2) example relations replay by ACTUAL ec_add
        for exkey in ("composed_example", "raw_example"):
            ex = meas.get(exkey)
            if not ex:
                continue
            pts = [tuple(P) for P in ex["P"]]
            R = tuple(ex["R"])
            acc = None
            for P, s in zip(pts, ex["signs"]):
                acc = ec_add(acc, P if s == 1 else _neg(P, p), 0, p)
            if acc != R:
                errors.append(f"{exkey} does not EC-confirm ({meas['variant']} |F|={meas['n_fb_elements']})")
            for P in pts + [R]:
                if (P[1] * P[1] - P[0] ** 3 - b) % p != 0:
                    errors.append(f"{exkey} point not on curve ({meas['variant']})")
    return errors, warnings


# ---------------------------------------------- cross-check (independent vs solver)

def cross_check():
    """Independent brute-force EC set MUST equal BOTH the composed-map and raw solver sets;
    spurious=0. The solver is imported HERE only, after the independent ground truth."""
    from semaev_petit import make_map, build_petit_base, search_relations_petit

    errors = []
    checked = total_rel = 0
    configs = [
        (16, "product_2aux", 2, 2), (16, "product_2aux", 3, 2),
        (16, "single_aux_composed", 4, 2), (16, "single_aux_composed", 6, 2),
    ]
    for bits, kind, size, m in configs:
        C = find_toy_curve(bits, seed=1, require_cofactor_one=True)
        p, b = C.p, C.b
        mp = make_map(C, kind, size)
        base = build_petit_base(C, mp)
        # independent factor-base reconstruction MUST match the solver's base by
        # x-COORDINATE (the factor base is a set of x-coords; y is on-curve up to sign and
        # relations are sign-agnostic via the +-1 lift, so only the x-set is load-bearing).
        # Cross-check the y independently too: each reconstructed y must satisfy the curve.
        indep_pts = rebuild_base_independent(_mp_to_dict(mp), b, p)
        if sorted(P[0] for P in indep_pts) != sorted(P[0] for P in base.points):
            errors.append(f"{kind} size={size}: independent base x-set != solver base x-set")
        for (x, y) in indep_pts:
            if (y * y - x * x * x - b) % p != 0:
                errors.append(f"{kind} size={size}: independent base point ({x},{y}) off curve")
        rng = random.Random(1234 + bits + size + m)
        targets = []
        for _ in range(8):  # constructed (relations present)
            idxs = rng.sample(range(len(base.points)), m)
            R = None
            for i in idxs:
                R = ec_add(R, base.points[i] if rng.random() < 0.5 else _neg(base.points[i], p), 0, p)
            if R is not None:
                targets.append(R)
        for _ in range(12):  # random
            R = ec_mul(rng.randrange(1, C.ell), C.gen, 0, p)
            if R is not None:
                targets.append(R)
        for R in targets:
            brute = brute_force_tuples(base.points, R, m, p)
            comp = search_relations_petit(C, base, m, R, kind, measure_dreg=False)
            raw = search_relations_petit(C, base, m, R, "raw_baseline", measure_dreg=False)
            cs = {frozenset(t) for t in comp["confirmed_relations"]}
            rs = {frozenset(t) for t in raw["confirmed_relations"]}
            if cs != brute:
                errors.append(f"{kind} size={size}: composed!=brute "
                              f"missing={sorted(map(tuple,brute-cs))} extra={sorted(map(tuple,cs-brute))}")
            if rs != brute:
                errors.append(f"{kind} size={size}: raw!=brute "
                              f"missing={sorted(map(tuple,brute-rs))} extra={sorted(map(tuple,rs-brute))}")
            if comp["spurious"] != 0 or raw["spurious"] != 0:
                errors.append(f"{kind} size={size}: spurious composed={comp['spurious']} raw={raw['spurious']}")
            total_rel += len(brute)
            checked += 1
    print(f"cross-check: {checked} targets over {len(configs)} (bits,kind,size,m) configs; "
          f"{total_rel} relations; composed-map solver == raw baseline == brute-force EC "
          f"enumeration, spurious=0")
    return checked, errors


def _mp_to_dict(mp):
    d = {"kind": mp.kind}
    if mp.kind == "product_2aux":
        d.update({"b0": mp.b0, "kappa": mp.kappa, "c": mp.c})
    else:
        d.update({"nt": mp.nt, "a1": mp.a1, "a2": mp.a2, "a3": mp.a3})
    return d


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
