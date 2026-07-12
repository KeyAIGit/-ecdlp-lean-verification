#!/usr/bin/env python3
"""Plain m=2 Semaev relation harness for HYP_GLV_SEMAEV_001 (variant: plain).

This is the BASELINE against which the GLV / invariant-coordinate variants are compared.
It measures the empirical RELATION-YIELD LAW for a standard (no-symmetry) Semaev m=2 factor
base in the x-coordinate.

Setup
-----
Curve  E_b : y^2 = x^3 + b  over F_p  (p = 1 mod 3, j = 0), from ``toy_curves.find_toy_curve``.
Factor base  F = the B curve-points with the SMALLEST x-coordinates on E_b (deterministic).
For each unordered pair (i, j), i < j, the two "combination" points
    S+ = P_i + P_j     and     S- = P_i - P_j
are precomputed and their x-coordinates stored in a dict  D : x  ->  (i, j, sign).

An m=2 relation is  R = e_i P_i + e_j P_j  with e in {+1, -1}.  Because a point is determined
by its x-coordinate up to sign, x(R) = x(S+) forces  R = +-S+  (i.e. e = (+,+) or (-,-)), and
x(R) = x(S-) forces  R = +-S-  (i.e. e = (+,-) or (-,+)).  So:

    a relation for a target R = k*G exists  <=>  x(R) is a key of D.

GROUND TRUTH: every claimed relation is INDEPENDENTLY re-verified by actual ``ec_add`` — we
recompute e_i P_i + e_j P_j and check it equals +R or -R in the group. Only EC-verified
relations are counted. (For these curves the lookup and the EC-check agree by construction,
but the EC-check is performed regardless and is the sole thing that lets a relation be counted.)

Quantity of interest
--------------------
    yield = (EC-verified relations) / (trials)   as a function of base size B and field size p.
Honest expectation:  yield ~ c * B^2 / p  (the number of distinct combination x-values, ~B^2,
divided by the ~p/2 possible x-coordinates). B ~ sqrt(p) relations for ~sqrt(p) work: generic.

Reusable module-scope functions (imported by the variant agents):
    build_base(curve, B)                -> list[Point]
    build_dict(base, curve, ...)        -> (dict, n_pairs)
    run_trials(curve, base, D, T, seed) -> dict of metrics + an EC-verified example
"""
from __future__ import annotations

import random
import time
from datetime import datetime, timezone
from math import isqrt

import sympy

from toy_curves import ToyCurve, ec_add, ec_mul, find_toy_curve
from manifest import Manifest

Point = tuple  # (x, y) or None


# ------------------------------------------------------------------ helpers

def neg(P, p: int):
    """The group inverse -P = (x, -y)."""
    if P is None:
        return None
    x, y = P
    return (x, (-y) % p)


def build_base(curve: ToyCurve, B: int) -> list:
    """The B on-curve points with the smallest x-coordinates (deterministic).

    Scans x = 0, 1, 2, ... and, whenever x^3 + b is a quadratic residue mod p, takes the
    point (x, y) with the canonical root y = sqrt_mod(...) (its negative -P is implied and
    never a separate base element — a Semaev x-base already identifies P and -P).
    """
    if curve.cofactor != 1:
        raise ValueError(
            "the x-coordinate factor base is sampled from all E(F_p), but the DLP "
            f"target lives in <G>; cofactor={curve.cofactor} would include points "
            "whose logarithms to G are undefined. Use a cofactor-one toy curve."
        )
    p, b = curve.p, curve.b
    base = []
    x = 0
    while len(base) < B and x < p:
        rhs = (x * x * x + b) % p
        y = sympy.sqrt_mod(rhs, p)
        if y is not None:
            base.append((x % p, int(y) % p))
        x += 1
    if len(base) < B:
        raise RuntimeError(f"only found {len(base)} points < requested B={B} (p={p})")
    return base


def build_dict(base: list, curve: ToyCurve, include_doubling: bool = False):
    """Map x( P_i +- P_j ) -> (i, j, sign) over all pairs i < j (sign: +1 sum, -1 difference).

    Doubling (i == j, the point 2*P_i) is EXCLUDED by default: a doubling is a degenerate
    "m=2" relation e_i P_i + e_i P_i using a single base element, not two. It can be included
    (as sign 0) for completeness via ``include_doubling=True``. On an x-collision the first
    stored pair wins — this is harmless for yield because x determines the point up to sign,
    so any pair sharing that x yields an EC-verifiable relation for the same target.
    """
    p, a = curve.p, 0
    D: dict = {}
    n_pairs = 0
    B = len(base)
    for i in range(B):
        Pi = base[i]
        for j in range(i + 1, B):
            Pj = base[j]
            Splus = ec_add(Pi, Pj, a, p)
            if Splus is not None:
                D.setdefault(Splus[0], (i, j, +1))
            Sminus = ec_add(Pi, neg(Pj, p), a, p)
            if Sminus is not None:
                D.setdefault(Sminus[0], (i, j, -1))
            n_pairs += 1
        if include_doubling:
            Dbl = ec_add(Pi, Pi, a, p)
            if Dbl is not None:
                D.setdefault(Dbl[0], (i, i, 0))
    return D, n_pairs


def ec_verify_relation(curve: ToyCurve, base: list, entry, R):
    """Re-verify a claimed relation with actual ec_add. GROUND TRUTH.

    Given a dict entry (i, j, sign) and the target point R, recompute the combination
    e_i P_i + e_j P_j for the sign choices consistent with `sign`, and return
    (True, e_i, e_j) iff one of them equals R exactly in the group; else (False, 0, 0).

    sign = +1 : R should be +-(P_i + P_j)  -> e = (+1,+1) [==R] or (-1,-1) [==-R]
    sign = -1 : R should be +-(P_i - P_j)  -> e = (+1,-1) [==R] or (-1,+1) [==-R]
    sign =  0 : doubling, R should be +-2 P_i -> e_i = e_j = +-1
    """
    p, a = curve.p, 0
    i, j, sign = entry
    Pi = base[i]
    Pj = base[j]
    negR = neg(R, p)
    if sign == +1:
        S = ec_add(Pi, Pj, a, p)
        if S == R:
            return True, +1, +1
        if S == negR:
            return True, -1, -1
    elif sign == -1:
        S = ec_add(Pi, neg(Pj, p), a, p)
        if S == R:
            return True, +1, -1
        if S == negR:
            return True, -1, +1
    else:  # doubling
        S = ec_add(Pi, Pi, a, p)
        if S == R:
            return True, +1, +1
        if S == negR:
            return True, -1, -1
    return False, 0, 0


def run_trials(curve: ToyCurve, base: list, D: dict, T: int, seed: int = 12345) -> dict:
    """Run T random targets R = k*G; count EC-VERIFIED m=2 relations; time it.

    For each trial a fresh k in [1, ell) is drawn, R = k*G computed, and x(R) looked up in D.
    If present, the candidate relation is re-verified by ec_add (ground truth). Only verified
    hits are counted. Returns yield = verified / trials plus one concrete verified example.
    """
    p = curve.p
    G = curve.gen
    ell = curve.ell
    rng = random.Random(seed)
    hits = 0            # x(R) found as a key
    verified = 0        # and EC-re-verified
    example = None
    t0 = time.time()
    for _ in range(T):
        k = rng.randrange(1, ell)
        R = ec_mul(k, G, 0, p)
        if R is None:
            continue
        entry = D.get(R[0])
        if entry is None:
            continue
        hits += 1
        ok, ei, ej = ec_verify_relation(curve, base, entry, R)
        if ok:
            verified += 1
            if example is None:
                i, j, _sign = entry
                example = {
                    "k": k,
                    "i": i,
                    "j": j,
                    "e_i": ei,
                    "e_j": ej,
                    "P_i": list(base[i]),
                    "P_j": list(base[j]),
                    "R": [R[0], R[1]],
                }
    dt = time.time() - t0
    return {
        "trials": T,
        "hits": hits,
        "verified_relations": verified,
        "yield": verified / T if T else 0.0,
        "trials_time_s": dt,
        "example_relation": example,
    }


# ------------------------------------------------------------------ experiment driver

def run_setting(bits: int, B: int, T: int, seed: int = 1) -> dict:
    """One (bits, B) measurement: build curve, base, dict, run T trials, collect metrics."""
    C = find_toy_curve(bits, seed=seed, require_cofactor_one=True)
    t0 = time.time()
    base = build_base(C, B)
    t1 = time.time()
    D, n_pairs = build_dict(base, C)
    t2 = time.time()
    res = run_trials(C, base, D, T, seed=1000 + bits * 7 + B)
    sqrt_p = isqrt(C.p)
    return {
        "bits": bits,
        "p": C.p,
        "b": C.b,
        "order": C.order,
        "ell": C.ell,
        "cofactor": C.cofactor,
        "generator": list(C.gen),
        "beta": C.beta,
        "lambda": C.lam,
        "sqrt_p": sqrt_p,
        "base_size": B,
        "n_pairs": n_pairs,
        "n_keys": len(D),
        "trials": T,
        "verified_relations": res["verified_relations"],
        "hits": res["hits"],
        "yield": res["yield"],
        "yield_over_B2_over_p": (res["yield"] * C.p / (B * B)) if B else 0.0,
        "base_time_s": round(t1 - t0, 4),
        "dict_time_s": round(t2 - t1, 4),
        "trials_time_s": round(res["trials_time_s"], 4),
        "example_relation": res["example_relation"],
    }


def fit_law(measurements: list) -> dict:
    """Fit yield ~ c * (B^2 / p) on the NON-saturated points, and estimate the B-exponent.

    Returns the constant c (mean of yield / (B^2/p) over unsaturated points, yield < 0.6) and,
    at fixed bits, a log-log slope of yield vs B (expected ~2 if yield ~ B^2).
    """
    import math

    unsat = [m for m in measurements if 0.0 < m["yield"] < 0.6]
    cs = [m["yield"] * m["p"] / (m["base_size"] ** 2) for m in unsat]
    c = sum(cs) / len(cs) if cs else None

    # B-exponent at each fixed bits (needs >= 2 unsaturated points sharing bits)
    slopes = {}
    by_bits: dict = {}
    for m in unsat:
        by_bits.setdefault(m["bits"], []).append(m)
    for bits, ms in by_bits.items():
        if len(ms) < 2:
            continue
        xs = [math.log(m["base_size"]) for m in ms]
        ys = [math.log(m["yield"]) for m in ms]
        n = len(xs)
        mx = sum(xs) / n
        my = sum(ys) / n
        num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        den = sum((x - mx) ** 2 for x in xs)
        if den > 0:
            slopes[bits] = num / den
    return {"c": c, "n_unsaturated": len(unsat), "B_exponents_by_bits": slopes}


def main():
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    seed = 1
    measurements = []

    # (1) Fixed-bits B-sweep at 20 bits (cofactor 1, p ~ 1.05e6, sqrt_p ~ 1024):
    #     B in {sqrt/4, sqrt/2, sqrt, 2*sqrt} to expose the B^2 growth into saturation.
    C20 = find_toy_curve(20, seed=seed, require_cofactor_one=True)
    s = isqrt(C20.p)
    for B in (s // 4, s // 2, s, 2 * s):
        # cap so precompute stays well under ~2e7 pairs
        if B * B // 2 > 20_000_000:
            continue
        measurements.append(run_setting(20, B, T=4000, seed=seed))

    # (2) Cross-bits at B ~ sqrt_p (capped) to see the 1/p field-size dependence.
    for bits in (16, 24):
        C = find_toy_curve(bits, seed=seed, require_cofactor_one=True)
        sp = isqrt(C.p)
        B = min(sp, 2000)  # cap heavy 24-bit precompute
        measurements.append(run_setting(bits, B, T=4000, seed=seed))

    # Also a small-B (unsaturated) point at 16 and 24 bits for the exponent fit.
    for bits in (16, 24):
        C = find_toy_curve(bits, seed=seed, require_cofactor_one=True)
        sp = isqrt(C.p)
        measurements.append(run_setting(bits, max(sp // 4, 8), T=4000, seed=seed))

    law = fit_law(measurements)

    # write a run manifest recording everything (deterministic provenance)
    m = Manifest(
        hypothesis="HYP_GLV_SEMAEV_001",
        variant="plain-core",
        params={"seed": seed, "settings": [(mm["bits"], mm["base_size"]) for mm in measurements]},
        code_files=[__file__, "toy_curves.py", "manifest.py"],
    )
    m.record({"measurements": measurements, "law_fit": law})
    path = m.write(timestamp)

    # human-readable summary
    print(f"manifest: {path}")
    print(f"{'bits':>4} {'p':>10} {'cof':>3} {'B':>6} {'pairs':>9} {'keys':>9} "
          f"{'ver':>5} {'yield':>8} {'y*p/B^2':>9} {'dictS':>7} {'trialS':>7}")
    for mm in measurements:
        print(f"{mm['bits']:>4} {mm['p']:>10} {mm['cofactor']:>3} {mm['base_size']:>6} "
              f"{mm['n_pairs']:>9} {mm['n_keys']:>9} {mm['verified_relations']:>5} "
              f"{mm['yield']:>8.4f} {mm['yield_over_B2_over_p']:>9.3f} "
              f"{mm['dict_time_s']:>7.2f} {mm['trials_time_s']:>7.2f}")
    print(f"\nlaw fit: c ~ {law['c']} over {law['n_unsaturated']} unsaturated pts; "
          f"B-exponents (fixed bits): {law['B_exponents_by_bits']}")
    ex = next((mm['example_relation'] for mm in measurements if mm['example_relation']), None)
    print(f"example EC-verified relation: {ex}")
    return measurements, law, path


if __name__ == "__main__":
    main()
