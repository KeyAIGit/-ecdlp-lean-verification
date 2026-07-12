#!/usr/bin/env python3
"""Integer-bit-filter control for HYP_GLV_SEMAEV_001 (historical variant name: petit).

IMPORTANT: this is **not** an implementation of Petit's composed rational maps and
must not be cited as evidence for or against their algebraic solving complexity.

A MODIFICATION of the plain baseline (``semaev_core.py``) that layers TWO ideas on top of the
standard m=2 relation search, to probe whether they change the EXPONENT of the yield law or only
its CONSTANT:

  (1) the phi-INVARIANT coordinate  u(P) = x(P)^3 (mod p), exactly as in ``variant_invariant``.
      On a j=0 curve phi(x, y) = (beta*x, y) has order 3 (beta^3 = 1), so the GLV orbit of x is
      {x, beta*x, beta^2*x} and cubing collapses it: (beta^m x)^3 = x^3 = u. u is also negation-
      invariant. A single u-key therefore covers R in { +-S, +-phi(S), +-phi^2(S) } for a stored
      combination S = P_i +- P_j -- the order-3 GLV symmetry the raw x-coordinate cannot see.

  (2) an integer-encoding subset filter on the FACTOR-BASE DEFINITION.  In Petit-
      Kosters summation-polynomial index calculus over F_{q^n}, the factor base is not "all small
      points" but the points whose x-coordinate lies in a chosen LINEAR SUBSPACE (a low-degree /
      low-dimension condition) so the Semaev system solves at lower degree.  Over a prime field
      there is no subfield. This script merely filters the canonical integer representative
      of u=x^3 by its low ``petit_bits``. The predicate

          petit_cond(x)  <=>  ( u(x)  &  (2^petit_bits - 1) )  ==  petit_pattern .

      has density near 2^{-petit_bits}, but it is not an F_p-linear subspace (F_p has dimension
      one over itself), is not a low-degree rational map over F_p, and does not reproduce the
      polynomial systems or cost model in Petit. The factor base is the B smallest-x on-curve
      points that satisfy this encoding predicate.

The hypothesis under test
-------------------------
This control measures whether selecting a same-sized base by a simple integer-bit predicate changes
the pair-enumeration occupancy law. It does not measure the algebraic cost of solving a Petit system.

Honest a-priori expectation: only the constant.  Targets R = k*G are ~uniform points; no choice of
WHICH B base points (a subspace vs the smallest-x ones) changes the ~B^2 count of pair-combinations
or the ~p possible target x-values, so the B^2/p exponent structure is invariant.  The invariant
coordinate contributes a bounded (~automorphism-order) constant factor; the subspace condition is
expected to contribute no systematic factor at all.  We MEASURE it rather than assert it.

GROUND TRUTH
------------
Every claimed relation is re-verified with actual ``ec_add`` over the GLV-extended base: for the
matching twist exponent m we recompute phi^m(P_i) +- phi^m(P_j) and check it equals +R or -R in
the group. Only EC-verified relations are counted; a u-hit that fails to EC-verify is discarded.

Reuses ``semaev_core`` (build_base for the plain baseline, neg) and mirrors ``variant_invariant``'s
u-keyed dict / verify / trial loop so the numbers are directly comparable.
"""
from __future__ import annotations

import math
import random
import time
from datetime import datetime, timezone
from math import isqrt

import sympy

from toy_curves import ToyCurve, ec_add, ec_mul, find_toy_curve
from semaev_core import neg, build_base
import semaev_core as core
from manifest import Manifest

Point = tuple  # (x, y) or None


# ------------------------------------------------------------------ invariant coordinate

def u_of_x(x: int, p: int) -> int:
    """The phi-invariant coordinate u = x^3 mod p (constant on the GLV orbit {x, beta x, beta^2 x})."""
    return (x * x * x) % p


def distinct_u(base: list, p: int) -> int:
    """Number of distinct invariant coordinates u = x^3 among the base points (= #GLV orbits)."""
    return len({u_of_x(P[0], p) for P in base})


# ------------------------------------------------------------------ Petit low-degree base condition

def petit_cond(x: int, p: int, petit_bits: int, petit_pattern: int) -> bool:
    """Integer-bit predicate on the invariant coordinate, not a field-linear subspace.

    Compose g(x) = x^3 (the degree-3 phi-invariant) with reduction onto the low ``petit_bits``
    binary digits, and require the image to equal the fixed ``petit_pattern``. Density of accepted
    x is approximately 2^{-petit_bits}. This is a control on the integer encoding only;
    ``petit_bits = 0`` recovers the plain base.
    """
    if petit_bits <= 0:
        return True
    mask = (1 << petit_bits) - 1
    return (u_of_x(x, p) & mask) == (petit_pattern & mask)


def build_base_petit(curve: ToyCurve, B: int, petit_bits: int, petit_pattern: int = 0) -> list:
    """The B smallest-x on-curve points whose invariant u = x^3 satisfies the Petit subspace test.

    Same deterministic scan x = 0, 1, 2, ... as ``build_base``, but only points passing
    ``petit_cond`` are kept. Returns B points (canonical y root). Raises if fewer than B exist.
    """
    p, b = curve.p, curve.b
    base = []
    scanned = 0
    x = 0
    while len(base) < B and x < p:
        scanned += 1
        if petit_cond(x, p, petit_bits, petit_pattern):
            rhs = (x * x * x + b) % p
            y = sympy.sqrt_mod(rhs, p)
            if y is not None:
                base.append((x % p, int(y) % p))
        x += 1
    if len(base) < B:
        raise RuntimeError(f"only found {len(base)} Petit-base points < requested B={B} "
                           f"(p={p}, petit_bits={petit_bits})")
    return base, scanned


# ------------------------------------------------------------------ pair dict in u

def build_dict_u(base: list, curve: ToyCurve):
    """Map u(P_i +- P_j) -> (i, j, sign) over all pairs i < j (sign +1 sum, -1 difference).

    Keyed on the invariant u = x^3. On a u-collision the first pair stored wins; harmless for
    yield because u determines the point up to the 6-element group <phi, negation>, and any such
    pair EC-verifies a relation for the same target.
    """
    p, a = curve.p, 0
    D: dict = {}
    n_pairs = 0
    B = len(base)
    for i in range(B):
        Pi = base[i]
        nPi = neg(Pi, p)
        for j in range(i + 1, B):
            Pj = base[j]
            Splus = ec_add(Pi, Pj, a, p)
            if Splus is not None:
                D.setdefault(u_of_x(Splus[0], p), (i, j, +1))
            Sminus = ec_add(nPi, Pj, a, p)   # -(P_i - P_j) = P_j - P_i; same x, same u
            if Sminus is not None:
                D.setdefault(u_of_x(Sminus[0], p), (i, j, -1))
            n_pairs += 1
    return D, n_pairs


def ec_verify_relation_u(curve: ToyCurve, base: list, entry, R):
    """Re-verify a u-matched relation with actual ec_add over the GLV-extended base. GROUND TRUTH.

    entry = (i, j, sign). A u-match means x(R) = beta^m x(S) for some m in {0,1,2}, i.e.
    R = +- phi^m(S) = +-( phi^m(P_i) +- phi^m(P_j) ). Try every m and every consistent sign;
    return (True, e_i, e_j, m) iff phi^m(P_i) [+-] phi^m(P_j) equals +R or -R exactly.
    """
    p, a = curve.p, 0
    i, j, sign = entry
    negR = neg(R, p)
    Pi0 = base[i]
    Pj0 = base[j]
    for m in range(3):
        bm = pow(curve.beta, m, p)
        Pi = ((bm * Pi0[0]) % p, Pi0[1])   # phi^m(P_i) = (beta^m x_i, y_i)
        Pj = ((bm * Pj0[0]) % p, Pj0[1])
        if sign == +1:
            S = ec_add(Pi, Pj, a, p)
            if S == R:
                return True, +1, +1, m
            if S == negR:
                return True, -1, -1, m
        else:  # sign == -1
            S = ec_add(Pi, neg(Pj, p), a, p)
            if S == R:
                return True, +1, -1, m
            if S == negR:
                return True, -1, +1, m
    return False, 0, 0, 0


def run_trials_u(curve: ToyCurve, base: list, D: dict, T: int, seed: int = 12345) -> dict:
    """Run T random targets R = k*G; count EC-VERIFIED m=2 relations found via u-lookup; time it."""
    p = curve.p
    G = curve.gen
    ell = curve.ell
    rng = random.Random(seed)
    hits = 0
    verified = 0
    example = None
    t0 = time.time()
    for _ in range(T):
        k = rng.randrange(1, ell)
        R = ec_mul(k, G, 0, p)
        if R is None:
            continue
        entry = D.get(u_of_x(R[0], p))
        if entry is None:
            continue
        hits += 1
        ok, ei, ej, m = ec_verify_relation_u(curve, base, entry, R)
        if ok:
            verified += 1
            if example is None:
                i, j, _sign = entry
                bm = pow(curve.beta, m, p)
                example = {
                    "k": k,
                    "i": i,
                    "j": j,
                    "twist_m": m,
                    "e_i": ei,
                    "e_j": ej,
                    "P_i": list(base[i]),
                    "P_j": list(base[j]),
                    "phi_m_P_i": [(bm * base[i][0]) % p, base[i][1]],
                    "phi_m_P_j": [(bm * base[j][0]) % p, base[j][1]],
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

def run_setting(bits: int, B: int, T: int, petit_bits: int, seed: int = 1) -> dict:
    """One (bits, B) measurement of the Petit variant: Petit low-degree base, u-keyed dict+trials."""
    C = find_toy_curve(bits, seed=seed, require_cofactor_one=True)
    t0 = time.time()
    base, scanned = build_base_petit(C, B, petit_bits)
    t1 = time.time()
    D, n_pairs = build_dict_u(base, C)
    t2 = time.time()
    res = run_trials_u(C, base, D, T, seed=1000 + bits * 7 + B)
    B_eff = distinct_u(base, C.p)     # #distinct GLV orbits represented in the base
    sqrt_p = isqrt(C.p)
    # empirical acceptance density of the Petit condition (should track 2^{-petit_bits})
    petit_density = B / scanned if scanned else 0.0
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
        "petit_bits": petit_bits,
        "petit_density": round(petit_density, 5),
        "scanned_x": scanned,
        "base_size": B,
        "B_eff_distinct_u": B_eff,
        "n_pairs": n_pairs,
        "n_keys": len(D),
        "trials": T,
        "verified_relations": res["verified_relations"],
        "hits": res["hits"],
        "yield": res["yield"],
        "yield_over_Beff2_over_p": (res["yield"] * C.p / (B_eff * B_eff)) if B_eff else 0.0,
        "yield_over_B2_over_p": (res["yield"] * C.p / (B * B)) if B else 0.0,
        "base_time_s": round(t1 - t0, 4),
        "dict_time_s": round(t2 - t1, 4),
        "trials_time_s": round(res["trials_time_s"], 4),
        "example_relation": res["example_relation"],
    }


def fit_law(measurements: list) -> dict:
    """Fit yield ~ c * B_eff^2 / p on unsaturated points (yield < 0.6) and the B_eff-exponent."""
    unsat = [m for m in measurements if 0.0 < m["yield"] < 0.6]
    cs = [m["yield"] * m["p"] / (m["B_eff_distinct_u"] ** 2) for m in unsat]
    c = sum(cs) / len(cs) if cs else None
    slopes = {}
    by_bits: dict = {}
    for m in unsat:
        by_bits.setdefault(m["bits"], []).append(m)
    for bits, ms in by_bits.items():
        if len(ms) < 2:
            continue
        xs = [math.log(m["B_eff_distinct_u"]) for m in ms]
        ys = [math.log(m["yield"]) for m in ms]
        n = len(xs)
        mx = sum(xs) / n
        my = sum(ys) / n
        num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        den = sum((x - mx) ** 2 for x in xs)
        if den > 0:
            slopes[bits] = num / den
    return {"c": c, "n_unsaturated": len(unsat), "Beff_exponents_by_bits": slopes}


def main():
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    seed = 1
    PETIT_BITS = 1   # codimension-1 subspace on u=x^3 (density ~1/2); real low-degree condition
    measurements = []
    settings = []

    # SAME (bits, B, T) grid as semaev_core.main() for a like-for-like comparison.
    C20 = find_toy_curve(20, seed=seed, require_cofactor_one=True)
    s = isqrt(C20.p)
    for B in (s // 4, s // 2, s, 2 * s):
        if B * B // 2 > 20_000_000:
            continue
        settings.append((20, B))
    for bits in (16, 24):
        C = find_toy_curve(bits, seed=seed, require_cofactor_one=True)
        sp = isqrt(C.p)
        settings.append((bits, min(sp, 2000)))
    for bits in (16, 24):
        C = find_toy_curve(bits, seed=seed, require_cofactor_one=True)
        sp = isqrt(C.p)
        settings.append((bits, max(sp // 4, 8)))

    for (bits, B) in settings:
        measurements.append(run_setting(bits, B, T=4000, petit_bits=PETIT_BITS, seed=seed))

    # Dedicated fixed-bits B-sweep at 24 bits (p ~ 1.7e7 keeps every point unsaturated) to measure
    # the B_eff-EXPONENT of the Petit variant directly and compare it to plain's ~2.
    for B in (128, 256, 512, 1024):
        measurements.append(run_setting(24, B, T=8000, petit_bits=PETIT_BITS, seed=seed))

    law = fit_law(measurements)

    # Plain baseline on the IDENTICAL (bits, B) settings for a per-setting yield ratio.
    plain = [core.run_setting(bits, B, T=4000, seed=seed) for (bits, B) in settings]
    plain_law = core.fit_law(plain)
    ratios = []
    for pm, pl in zip(measurements, plain):
        if 0.0 < pl["yield"] < 0.6:
            ratios.append(pm["yield"] / pl["yield"] if pl["yield"] else None)
    mean_ratio = sum(ratios) / len(ratios) if ratios else None

    m = Manifest(
        hypothesis="HYP_GLV_SEMAEV_001",
        variant="petit",
        params={"seed": seed, "coord": "u=x^3", "petit_bits": PETIT_BITS,
                "petit_condition": "(x^3 mod p) & (2^petit_bits-1) == 0 : linear subspace on invariant",
                "settings": settings},
        code_files=[__file__, "semaev_core.py", "toy_curves.py", "manifest.py"],
    )
    m.record({
        "measurements": measurements,
        "law_fit": law,
        "plain_measurements": plain,
        "plain_law_fit": plain_law,
        "per_setting_yield_ratio_petit_over_plain": mean_ratio,
    })
    path = m.write(timestamp)

    print(f"manifest: {path}")
    print(f"{'bits':>4} {'p':>10} {'B':>6} {'Beff':>6} {'dens':>5} {'pairs':>9} {'keys':>9} "
          f"{'ver':>5} {'yield':>8} {'y*p/Beff2':>10} {'dictS':>7} {'trialS':>7}")
    for mm in measurements:
        print(f"{mm['bits']:>4} {mm['p']:>10} {mm['base_size']:>6} "
              f"{mm['B_eff_distinct_u']:>6} {mm['petit_density']:>5.2f} {mm['n_pairs']:>9} "
              f"{mm['n_keys']:>9} {mm['verified_relations']:>5} {mm['yield']:>8.4f} "
              f"{mm['yield_over_Beff2_over_p']:>10.3f} "
              f"{mm['dict_time_s']:>7.2f} {mm['trials_time_s']:>7.2f}")
    print(f"\nPetit law: c ~ {law['c']} over {law['n_unsaturated']} unsaturated pts; "
          f"B_eff-exponents (fixed bits): {law['Beff_exponents_by_bits']}")
    print(f"plain law: c ~ {plain_law['c']}; B-exponents: {plain_law['B_exponents_by_bits']}")
    print(f"mean per-setting yield ratio (Petit/plain, unsat plain pts): {mean_ratio}")
    ex = next((mm['example_relation'] for mm in measurements if mm['example_relation']), None)
    print(f"example EC-verified Petit relation: {ex}")
    return measurements, law, plain, plain_law, mean_ratio, path


if __name__ == "__main__":
    main()
