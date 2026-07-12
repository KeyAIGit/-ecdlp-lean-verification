#!/usr/bin/env python3
"""GLV phi-invariant-coordinate m=2 Semaev harness for HYP_GLV_SEMAEV_001 (variant: invariant-u).

This is a MODIFICATION of the plain baseline in ``semaev_core.py``. It reruns the same m=2
relation search, but keyed on the phi-INVARIANT coordinate

    u(P) = x(P)^3   (mod p)

instead of the raw x-coordinate. On a j=0 curve the GLV automorphism phi(x, y) = (beta*x, y)
has order 3 with beta^3 = 1, so the GLV orbit of x is  {x, beta*x, beta^2*x}  and cubing
collapses it to a single value:  (beta^m x)^3 = beta^(3m) x^3 = x^3 = u.  So u is invariant
under phi, and (since y is untouched by cubing of x) also under negation P -> -P.

What that buys us
-----------------
The plain harness stores x(P_i +- P_j) and a target R=k*G is a hit iff x(R) is a stored key.
Here we store u(P_i +- P_j). A single u-key now matches R whenever

    x(R) in { x(S), beta*x(S), beta^2*x(S) }      (S = P_i +- P_j)

i.e. whenever R in { +-S, +-phi(S), +-phi^2(S) }.  Because phi is a group homomorphism,
phi^m(S) = phi^m(P_i) +- phi^m(P_j), so a u-hit is a GENUINE m=2 relation over the GLV-extended
base { phi^m(P_i) = [lambda^m] P_i }.  Each u-key therefore covers 3x as many targets as the
corresponding x-key: the order-3 GLV symmetry, which the x-coordinate does not see.

Base collapse (the "B/3" claim)
-------------------------------
u is constant on GLV orbits, so a factor base that is CLOSED under phi (contains whole orbits)
has exactly |base|/3 distinct u-values: the u-base auto-dedupes the orbit.  ``glv_closed_base``
+ ``distinct_u`` demonstrate this 3:1 collapse directly.  For the smallest-x base used in the
comparison grid the B seeds already lie in distinct orbits (beta*x_small is large, not small),
so B_eff = B there; the collapse is a property of the coordinate, shown separately.

GROUND TRUTH
------------
Every claimed relation is re-verified with actual ``ec_add``: for the matching twist exponent m
we recompute phi^m(P_i) +- phi^m(P_j) and check it equals +R or -R in the group. Only
EC-verified relations are counted. A u-hit that fails to EC-verify (should not happen, by the
homomorphism argument) is discarded.

Quantity of interest
--------------------
    yield = (EC-verified relations) / trials   vs base size B_eff and field size p.
    Fit  yield ~ c * B_eff^2 / p  and the B-exponent, to decide whether GLV symmetry changes
    the EXPONENT of the yield law or only the CONSTANT c.  (Expectation: constant factor ~3.)

Reuses ``semaev_core``: build_base (identical base), ec_verify primitives, and fit_law.
"""
from __future__ import annotations

import random
import time
from datetime import datetime, timezone
from math import isqrt

import sympy

from toy_curves import ToyCurve, ec_add, ec_mul, find_toy_curve
from semaev_core import build_base, neg, fit_law
from manifest import Manifest

Point = tuple  # (x, y) or None


# ------------------------------------------------------------------ invariant coordinate

def u_of_x(x: int, p: int) -> int:
    """The phi-invariant coordinate u = x^3 mod p (constant on the GLV orbit {x,beta x,beta^2 x})."""
    return (x * x * x) % p


def distinct_u(base: list, p: int) -> int:
    """Number of distinct invariant coordinates u = x^3 among the base points (= #GLV orbits)."""
    return len({u_of_x(P[0], p) for P in base})


def glv_closed_base(curve: ToyCurve, n_orbits: int) -> list:
    """A GLV-CLOSED base: n_orbits smallest-x seeds together with their full phi-orbits.

    Returns 3*n_orbits points (each seed x, beta*x, beta^2*x with the same y). Used only to
    demonstrate the 3:1 collapse in u:  len == 3*n_orbits  but  distinct_u == n_orbits.
    """
    p = curve.p
    seeds = build_base(curve, n_orbits)
    out = []
    for (x, y) in seeds:
        for m in range(3):
            out.append(((pow(curve.beta, m, p) * x) % p, y))
    return out


# ------------------------------------------------------------------ pair dict in u

def build_dict_u(base: list, curve: ToyCurve):
    """Map u(P_i +- P_j) -> (i, j, sign) over all pairs i < j (sign +1 sum, -1 difference).

    Keyed on the invariant u = x^3 rather than x. On a u-collision the first pair stored wins;
    this is harmless for yield because u determines the point up to the 6-element group
    <phi, negation>, and any such pair EC-verifies a relation for the same target.
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
            Sminus = ec_add(nPi, Pj, a, p)   # -(P_i - P_j) = P_j - P_i; same x, same u as P_i - P_j
            if Sminus is not None:
                D.setdefault(u_of_x(Sminus[0], p), (i, j, -1))
            n_pairs += 1
    return D, n_pairs


def ec_verify_relation_u(curve: ToyCurve, base: list, entry, R):
    """Re-verify a u-matched relation with actual ec_add over the GLV-extended base. GROUND TRUTH.

    entry = (i, j, sign). A u-match means x(R) = beta^m x(S) for some m in {0,1,2}, i.e.
    R = +- phi^m(S) = +-( phi^m(P_i) +- phi^m(P_j) ).  Try every m and every consistent sign of
    the pair; return (True, e_i, e_j, m) iff phi^m(P_i) [+-] phi^m(P_j) equals +R or -R exactly.
    e_i, e_j are the signs; the actual base elements used are [lambda^m] P_i and [lambda^m] P_j.
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
    """Run T random targets R=k*G; count EC-VERIFIED m=2 relations found via u-lookup; time it."""
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
                    "twist_m": m,           # relation uses [lambda^m]P_i, [lambda^m]P_j
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

def run_setting(bits: int, B: int, T: int, seed: int = 1) -> dict:
    """One (bits, B) measurement in u-coordinates: same base as core, dict+trials keyed on u."""
    C = find_toy_curve(bits, seed=seed, require_cofactor_one=True)
    t0 = time.time()
    base = build_base(C, B)
    t1 = time.time()
    D, n_pairs = build_dict_u(base, C)
    t2 = time.time()
    res = run_trials_u(C, base, D, T, seed=1000 + bits * 7 + B)
    B_eff = distinct_u(base, C.p)     # #distinct GLV orbits represented in the base
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
        "B_eff_distinct_u": B_eff,
        "n_pairs": n_pairs,
        "n_keys": len(D),
        "trials": T,
        "verified_relations": res["verified_relations"],
        "hits": res["hits"],
        "yield": res["yield"],
        # fit constant against the EFFECTIVE (orbit) base size B_eff, as requested
        "yield_over_Beff2_over_p": (res["yield"] * C.p / (B_eff * B_eff)) if B_eff else 0.0,
        "yield_over_B2_over_p": (res["yield"] * C.p / (B * B)) if B else 0.0,
        "base_time_s": round(t1 - t0, 4),
        "dict_time_s": round(t2 - t1, 4),
        "trials_time_s": round(res["trials_time_s"], 4),
        "example_relation": res["example_relation"],
    }


def fit_law_u(measurements: list) -> dict:
    """Fit yield ~ c * B_eff^2 / p on unsaturated points, and the B_eff-exponent at fixed bits."""
    import math
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
    measurements = []

    # SAME (bits, B, T) grid as semaev_core.main() for a like-for-like comparison.
    C20 = find_toy_curve(20, seed=seed, require_cofactor_one=True)
    s = isqrt(C20.p)
    for B in (s // 4, s // 2, s, 2 * s):
        if B * B // 2 > 20_000_000:
            continue
        measurements.append(run_setting(20, B, T=4000, seed=seed))

    for bits in (16, 24):
        C = find_toy_curve(bits, seed=seed, require_cofactor_one=True)
        sp = isqrt(C.p)
        B = min(sp, 2000)
        measurements.append(run_setting(bits, B, T=4000, seed=seed))

    for bits in (16, 24):
        C = find_toy_curve(bits, seed=seed, require_cofactor_one=True)
        sp = isqrt(C.p)
        measurements.append(run_setting(bits, max(sp // 4, 8), T=4000, seed=seed))

    # Dedicated fixed-bits B-sweep at 24 bits (p ~ 1.7e7 keeps every point unsaturated),
    # to measure the B_eff-EXPONENT of the u-variant directly and compare it to plain's ~2.
    for B in (128, 256, 512, 1024):
        measurements.append(run_setting(24, B, T=8000, seed=seed))

    law = fit_law_u(measurements)

    # Demonstrate the 3:1 base collapse in u on a GLV-closed base (the "B/3 automatically" claim).
    collapse_demo = []
    for bits in (16, 20):
        C = find_toy_curve(bits, seed=seed, require_cofactor_one=True)
        for n_orbits in (8, 32):
            gb = glv_closed_base(C, n_orbits)
            collapse_demo.append({
                "bits": bits, "n_orbits": n_orbits,
                "closed_base_size": len(gb),
                "distinct_u": distinct_u(gb, C.p),
                "ratio": len(gb) / distinct_u(gb, C.p),
            })

    m = Manifest(
        hypothesis="HYP_GLV_SEMAEV_001",
        variant="invariant-u",
        params={"seed": seed, "coord": "u=x^3",
                "settings": [(mm["bits"], mm["base_size"]) for mm in measurements]},
        code_files=[__file__, "semaev_core.py", "toy_curves.py", "manifest.py"],
    )
    m.record({"measurements": measurements, "law_fit": law, "base_collapse_demo": collapse_demo})
    path = m.write(timestamp)

    print(f"manifest: {path}")
    print(f"{'bits':>4} {'p':>10} {'cof':>3} {'B':>6} {'Beff':>6} {'pairs':>9} {'keys':>9} "
          f"{'ver':>5} {'yield':>8} {'y*p/Beff2':>10} {'dictS':>7} {'trialS':>7}")
    for mm in measurements:
        print(f"{mm['bits']:>4} {mm['p']:>10} {mm['cofactor']:>3} {mm['base_size']:>6} "
              f"{mm['B_eff_distinct_u']:>6} {mm['n_pairs']:>9} {mm['n_keys']:>9} "
              f"{mm['verified_relations']:>5} {mm['yield']:>8.4f} "
              f"{mm['yield_over_Beff2_over_p']:>10.3f} "
              f"{mm['dict_time_s']:>7.2f} {mm['trials_time_s']:>7.2f}")
    print(f"\nlaw fit (u): c ~ {law['c']} over {law['n_unsaturated']} unsaturated pts; "
          f"B_eff-exponents (fixed bits): {law['Beff_exponents_by_bits']}")
    print(f"base collapse demo (GLV-closed base -> distinct u): {collapse_demo}")
    ex = next((mm['example_relation'] for mm in measurements if mm['example_relation']), None)
    print(f"example EC-verified u-relation: {ex}")
    return measurements, law, path


if __name__ == "__main__":
    main()
