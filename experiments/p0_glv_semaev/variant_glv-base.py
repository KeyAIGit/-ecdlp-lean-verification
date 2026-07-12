#!/usr/bin/env python3
"""GLV-orbit m=2 Semaev relation harness for HYP_GLV_SEMAEV_001 (variant: glv-base).

A MODIFICATION of the plain harness (`semaev_core.py`) whose factor base is CLOSED under the
GLV automorphism orbit  phi(x, y) = (beta*x, y)  (order 3, phi^s(x, y) = (beta^s * x, y)) and
under +- (the y-sign, already implicit in a Semaev x-base).

Why the orbit is "free"
-----------------------
phi is a group homomorphism, so for any base pair

    phi^s(P_i +- P_j) = phi^s(P_i) +- phi^s(P_j)              (s = 0, 1, 2).

Hence ONE base-pair sum  S = P_i +- P_j  already witnesses its whole phi-orbit
{S, phi(S), phi^2(S)} whose x-coordinates are { x(S), beta*x(S), beta^2*x(S) }.  We compute the
B^2/2 base-pair sums exactly ONCE (same work as plain) and register all three orbit x-values as
dict keys pointing to (i, j, sign, s).  So B physically-stored points expose an EFFECTIVE factor
base of ~3B distinct x-coordinates ( ~6B group points counting +- ) at NO extra pair work:
effective base per unit storage ~ 6 (i.e. storage ~ /6).

A target R = k*G hits iff x(R) is a key.  A key beta^s * x(S) means  R = +-phi^s(P_i +- P_j),
i.e.  R = e_i * phi^s(P_i) + e_j * phi^s(P_j)  -- an m=2 relation over the ORBIT-CLOSED base.

GROUND TRUTH: every claimed relation is re-verified by actual ec_add on the real orbit points
phi^s(P_i), phi^s(P_j).  Only EC-verified relations are counted.

Quantity of interest
--------------------
yield vs the EFFECTIVE (orbit-reduced) base size  B_eff = #{ distinct x in the orbit closure }.
We fit  yield ~ c * B_eff^2 / p  and compare c (and the B_eff-exponent) to plain, to decide
whether GLV changes only the CONSTANT of the B/p law or its EXPONENT.

Self-test / run:  python3 experiments/p0_glv_semaev/variant_glv-base.py
"""
from __future__ import annotations

import math
import random
import time
from datetime import datetime, timezone
from math import isqrt

from toy_curves import ToyCurve, ec_add, ec_mul, find_toy_curve
from manifest import Manifest
import semaev_core as core
from semaev_core import neg, build_base


# ------------------------------------------------------------------ GLV helpers

def phi_pow(curve: ToyCurve, P, s: int):
    """phi^s(P) = (beta^s * x, y).  Applies the order-3 automorphism s times."""
    for _ in range(s % 3):
        P = curve.phi(P)
    return P


def effective_base(base: list, curve: ToyCurve):
    """Distinct x-coordinates of the orbit-closed factor base { phi^s(P_i) }.

    Returns (B_eff, orbit_x_count) where B_eff = number of distinct x-coords (the Semaev
    base unit, +- folded) and orbit_x_count is the multiset size 3*B before dedup, so their
    ratio exposes any orbit collisions (e.g. x = 0 whose whole orbit is {0})."""
    p, beta = curve.p, curve.beta
    betas = [1, beta % p, (beta * beta) % p]
    xs = set()
    for (x, _y) in base:
        for bpow in betas:
            xs.add((bpow * x) % p)
    return len(xs), 3 * len(base)


def build_glv_dict(base: list, curve: ToyCurve):
    """Free-orbit dict:  x( phi^s(P_i +- P_j) ) -> (i, j, sign, s)  over pairs i<j, s in {0,1,2}.

    Same B^2/2 base-pair sums as plain; each sum registers its whole 3-element phi-orbit of
    x-values.  On an x-collision the first stored entry wins (harmless: any colliding entry is
    independently EC-verifiable for the same target)."""
    p, a, beta = curve.p, 0, curve.beta
    betas = [1, beta % p, (beta * beta) % p]
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
                xs = Splus[0]
                for s in range(3):
                    D.setdefault((betas[s] * xs) % p, (i, j, +1, s))
            Sminus = ec_add(Pi, neg(Pj, p), a, p)
            if Sminus is not None:
                xs = Sminus[0]
                for s in range(3):
                    D.setdefault((betas[s] * xs) % p, (i, j, -1, s))
            n_pairs += 1
    return D, n_pairs


def ec_verify_glv(curve: ToyCurve, base: list, entry, R):
    """GROUND TRUTH re-verification with actual ec_add on the real orbit points.

    entry = (i, j, sign, s).  Recompute  e_i * phi^s(P_i) + e_j * phi^s(P_j)  for the sign
    choices consistent with `sign` and return (True, e_i, e_j) iff one equals R (or -R) in the
    group; else (False, 0, 0)."""
    p, a = curve.p, 0
    i, j, sign, s = entry
    Pi = phi_pow(curve, base[i], s)
    Pj = phi_pow(curve, base[j], s)
    negR = neg(R, p)
    if sign == +1:
        S = ec_add(Pi, Pj, a, p)
        if S == R:
            return True, +1, +1
        if S == negR:
            return True, -1, -1
    else:  # sign == -1
        S = ec_add(Pi, neg(Pj, p), a, p)
        if S == R:
            return True, +1, -1
        if S == negR:
            return True, -1, +1
    return False, 0, 0


def run_trials_glv(curve: ToyCurve, base: list, D: dict, T: int, seed: int) -> dict:
    """T random targets R = k*G; count EC-VERIFIED orbit-relations; time it."""
    p, G, ell = curve.p, curve.gen, curve.ell
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
        entry = D.get(R[0])
        if entry is None:
            continue
        hits += 1
        ok, ei, ej = ec_verify_glv(curve, base, entry, R)
        if ok:
            verified += 1
            if example is None:
                i, j, sign, s = entry
                example = {
                    "k": k,
                    "i": i, "j": j, "sign": sign, "phi_power_s": s,
                    "e_i": ei, "e_j": ej,
                    "P_i": list(base[i]), "P_j": list(base[j]),
                    "phi_s_P_i": list(phi_pow(curve, base[i], s)),
                    "phi_s_P_j": list(phi_pow(curve, base[j], s)),
                    "R": [R[0], R[1]],
                }
    dt = time.time() - t0
    return {
        "trials": T, "hits": hits, "verified_relations": verified,
        "yield": verified / T if T else 0.0, "trials_time_s": dt,
        "example_relation": example,
    }


# ------------------------------------------------------------------ experiment driver

def run_setting(bits: int, store_B: int, T: int, seed: int = 1) -> dict:
    """One (bits, store_B) GLV measurement.  store_B = physically stored points; the effective
    (orbit-reduced) base B_eff ~ 3*store_B is what the yield law is measured against."""
    C = find_toy_curve(bits, seed=seed, require_cofactor_one=True)
    t0 = time.time()
    base = build_base(C, store_B)
    t1 = time.time()
    D, n_pairs = build_glv_dict(base, C)
    t2 = time.time()
    B_eff, orbit_x_count = effective_base(base, C)
    trial_seed = 1000 + bits * 7 + store_B  # same formula the core uses, for comparability
    res = run_trials_glv(C, base, D, T, seed=trial_seed)
    return {
        "bits": bits, "p": C.p, "b": C.b, "order": C.order,
        "ell": C.ell, "cofactor": C.cofactor,
        "generator": list(C.gen), "beta": C.beta, "lambda": C.lam,
        "sqrt_p": isqrt(C.p),
        "store_B": store_B,
        "base_size_eff": B_eff,
        "orbit_x_count": orbit_x_count,
        "eff_per_storage": B_eff / store_B if store_B else 0.0,
        "n_pairs": n_pairs,
        "n_keys": len(D),
        "trials": T,
        "verified_relations": res["verified_relations"],
        "hits": res["hits"],
        "yield": res["yield"],
        "yield_over_Beff2_over_p": (res["yield"] * C.p / (B_eff * B_eff)) if B_eff else 0.0,
        "base_time_s": round(t1 - t0, 4),
        "dict_time_s": round(t2 - t1, 4),
        "trials_time_s": round(res["trials_time_s"], 4),
        "example_relation": res["example_relation"],
    }


def fit_law(measurements: list) -> dict:
    """Fit yield ~ c * (B_eff^2 / p) on unsaturated points (yield < 0.6) and the B_eff-exponent."""
    unsat = [m for m in measurements if 0.0 < m["yield"] < 0.6]
    cs = [m["yield"] * m["p"] / (m["base_size_eff"] ** 2) for m in unsat]
    c = sum(cs) / len(cs) if cs else None
    slopes = {}
    by_bits: dict = {}
    for m in unsat:
        by_bits.setdefault(m["bits"], []).append(m)
    for bits, ms in by_bits.items():
        if len(ms) < 2:
            continue
        xs = [math.log(m["base_size_eff"]) for m in ms]
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

    # SAME (bits, B, T) grid as semaev_core.main so results are directly comparable.
    C20 = find_toy_curve(20, seed=seed, require_cofactor_one=True)
    s20 = isqrt(C20.p)
    settings = []
    for B in (s20 // 4, s20 // 2, s20, 2 * s20):
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

    glv = [run_setting(bits, B, T=4000, seed=seed) for (bits, B) in settings]
    # plain baseline on the IDENTICAL storage settings, for a per-unit-storage comparison
    plain = [core.run_setting(bits, B, T=4000, seed=seed) for (bits, B) in settings]

    glv_law = fit_law(glv)
    plain_law = core.fit_law(plain)

    # per-storage yield ratios on unsaturated plain points (where the comparison is meaningful)
    ratios = []
    for g, pl in zip(glv, plain):
        if 0.0 < pl["yield"] < 0.6:
            ratios.append(g["yield"] / pl["yield"] if pl["yield"] else None)
    mean_ratio = sum(ratios) / len(ratios) if ratios else None

    m = Manifest(
        hypothesis="HYP_GLV_SEMAEV_001",
        variant="glv-base",
        params={"seed": seed, "settings": settings,
                "note": "store_B is physical storage; B_eff ~ 3*store_B is the orbit-reduced base"},
        code_files=[__file__, "semaev_core.py", "toy_curves.py", "manifest.py"],
    )
    m.record({
        "glv_measurements": glv,
        "plain_measurements": plain,
        "glv_law_fit": glv_law,
        "plain_law_fit": plain_law,
        "per_storage_yield_ratio_glv_over_plain": mean_ratio,
    })
    path = m.write(timestamp)

    print(f"manifest: {path}")
    print(f"{'bits':>4} {'p':>10} {'sB':>5} {'Beff':>5} {'e/s':>4} {'pairs':>9} {'keys':>9} "
          f"{'ver':>5} {'yGLV':>7} {'yPln':>7} {'ratio':>6} {'c_eff':>7} {'dS':>6}")
    for g, pl in zip(glv, plain):
        r = (g["yield"] / pl["yield"]) if pl["yield"] else float("nan")
        print(f"{g['bits']:>4} {g['p']:>10} {g['store_B']:>5} {g['base_size_eff']:>5} "
              f"{g['eff_per_storage']:>4.1f} {g['n_pairs']:>9} {g['n_keys']:>9} "
              f"{g['verified_relations']:>5} {g['yield']:>7.4f} {pl['yield']:>7.4f} "
              f"{r:>6.2f} {g['yield_over_Beff2_over_p']:>7.3f} {g['dict_time_s']:>6.2f}")
    print(f"\nGLV law:   c_eff ~ {glv_law['c']} over {glv_law['n_unsaturated']} unsat pts; "
          f"B_eff-exponents: {glv_law['Beff_exponents_by_bits']}")
    print(f"plain law: c ~ {plain_law['c']}; B-exponents: {plain_law['B_exponents_by_bits']}")
    print(f"mean per-storage yield ratio (GLV/plain, unsat): {mean_ratio}")
    ex = next((g['example_relation'] for g in glv if g['example_relation']), None)
    print(f"example EC-verified GLV relation: {ex}")
    return glv, plain, glv_law, plain_law, mean_ratio, path


if __name__ == "__main__":
    main()
