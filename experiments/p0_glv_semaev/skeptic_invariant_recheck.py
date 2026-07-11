#!/usr/bin/env python3
"""Independent adversarial recheck of the invariant-u variant.

Does NOT import the variant's verify code. Rebuilds base/dict/trials from scratch
using only toy_curves primitives (the SAME curves), and independently:
  (1) reconstructs several claimed relations and checks by ec_add that
      +-(phi^m(P_i) +- phi^m(P_j)) == +-R = +-k*G.
  (2) re-measures yield over a grid and fits log(yield) vs log(B^2/p).
  (3) compares c_u vs c_plain (both fit against B^2/p on the SAME base).
"""
from __future__ import annotations
import math
import random
from math import isqrt

import sympy
from toy_curves import find_toy_curve, ec_add, ec_mul


def neg(P, p):
    if P is None:
        return None
    return (P[0], (-P[1]) % p)


def build_base(curve, B):
    p, b = curve.p, curve.b
    base = []
    x = 0
    while len(base) < B and x < p:
        rhs = (x * x * x + b) % p
        y = sympy.sqrt_mod(rhs, p)
        if y is not None:
            base.append((x % p, int(y) % p))
        x += 1
    return base


def u_of(x, p):
    return (x * x * x) % p


def build_dict_x(base, p):
    """plain: key x(P_i +- P_j)."""
    D = {}
    B = len(base)
    for i in range(B):
        Pi = base[i]
        nPi = neg(Pi, p)
        for j in range(i + 1, B):
            Pj = base[j]
            Sp = ec_add(Pi, Pj, 0, p)
            if Sp is not None:
                D.setdefault(Sp[0], (i, j, +1))
            Sm = ec_add(nPi, Pj, 0, p)
            if Sm is not None:
                D.setdefault(Sm[0], (i, j, -1))
    return D


def build_dict_u(base, p):
    """u-variant: key u(P_i +- P_j) = x^3."""
    D = {}
    B = len(base)
    for i in range(B):
        Pi = base[i]
        nPi = neg(Pi, p)
        for j in range(i + 1, B):
            Pj = base[j]
            Sp = ec_add(Pi, Pj, 0, p)
            if Sp is not None:
                D.setdefault(u_of(Sp[0], p), (i, j, +1))
            Sm = ec_add(nPi, Pj, 0, p)
            if Sm is not None:
                D.setdefault(u_of(Sm[0], p), (i, j, -1))
    return D


def verify_x(curve, base, entry, R):
    p = curve.p
    i, j, sign = entry
    Pi, Pj = base[i], base[j]
    nR = neg(R, p)
    if sign == +1:
        S = ec_add(Pi, Pj, 0, p)
        if S == R: return (+1, +1, 0)
        if S == nR: return (-1, -1, 0)
    else:
        S = ec_add(Pi, neg(Pj, p), 0, p)
        if S == R: return (+1, -1, 0)
        if S == nR: return (-1, +1, 0)
    return None


def verify_u(curve, base, entry, R):
    """INDEPENDENT ground truth: try all 3 twists m and both signs, require exact ec_add match."""
    p = curve.p
    i, j, sign = entry
    Pi0, Pj0 = base[i], base[j]
    nR = neg(R, p)
    for m in range(3):
        bm = pow(curve.beta, m, p)
        Pi = ((bm * Pi0[0]) % p, Pi0[1])
        Pj = ((bm * Pj0[0]) % p, Pj0[1])
        if sign == +1:
            S = ec_add(Pi, Pj, 0, p)
            if S == R: return (+1, +1, m)
            if S == nR: return (-1, -1, m)
        else:
            S = ec_add(Pi, neg(Pj, p), 0, p)
            if S == R: return (+1, -1, m)
            if S == nR: return (-1, +1, m)
    return None


def measure(curve, base, D, verify, use_u, T, seed):
    p, G, ell = curve.p, curve.gen, curve.ell
    rng = random.Random(seed)
    hits = verified = 0
    examples = []
    for _ in range(T):
        k = rng.randrange(1, ell)
        R = ec_mul(k, G, 0, p)
        if R is None:
            continue
        key = u_of(R[0], p) if use_u else R[0]
        entry = D.get(key)
        if entry is None:
            continue
        hits += 1
        res = verify(curve, base, entry, R)
        if res is not None:
            verified += 1
            if len(examples) < 5:
                examples.append((k, entry, res, R))
    return hits, verified, examples


def main():
    print("=== PART 1: reconstruct & EC-verify claimed relations (24-bit, B=512) ===")
    C = find_toy_curve(24, seed=1)
    p = C.p
    base = build_base(C, 512)
    Du = build_dict_u(base, p)
    hits, ver, examples = measure(C, base, Du, verify_u, True, 8000, seed=1000 + 24 * 7 + 512)
    print(f"24b B=512: hits={hits} verified={ver} yield={ver/8000:.4f}")
    # Independently reconstruct each example fully from scratch
    used_m = set()
    for (k, entry, res, R) in examples:
        i, j, sign = entry
        ei, ej, m = res
        bm = pow(C.beta, m, p)
        Pi = ((bm * base[i][0]) % p, base[i][1])
        Pj = ((bm * base[j][0]) % p, base[j][1])
        # recompute R independently from k
        R_check = ec_mul(k, C.gen, 0, p)
        # build the claimed combination ei*Pi + ej*Pj
        comb = ec_add(Pi if ei == +1 else neg(Pi, p),
                      Pj if ej == +1 else neg(Pj, p), 0, p)
        onc = C.on_curve(Pi) and C.on_curve(Pj)
        # phi^m(P) must be in subgroup -> ell*phi^m(P)=inf
        insub = ec_mul(C.ell, Pi, 0, p) is None and ec_mul(C.ell, Pj, 0, p) is None
        ok = (comb == R_check) and (R == R_check) and onc and insub
        used_m.add(m)
        print(f"  k={k} pair(i={i},j={j}) sign={sign} e=({ei:+d},{ej:+d}) twist_m={m} "
              f"comb==R:{comb==R_check} on_curve:{onc} in_subgrp:{insub} -> {'OK' if ok else 'FAIL'}")
    print(f"  twist exponents m used in examples: {sorted(used_m)} (m>0 => genuine GLV twist)")

    print("\n=== PART 2 & 3: independent yield grid, plain vs u, fit c*B^2/p ===")
    grid = [(24, B) for B in (128, 256, 512, 1024)] + [(20, B) for B in (256, 512)]
    rows = []
    for bits, B in grid:
        Cc = find_toy_curve(bits, seed=1)
        pp = Cc.p
        bb = build_base(Cc, B)
        # confirm B_eff (distinct u) == B for smallest-x base
        beff = len({u_of(P[0], pp) for P in bb})
        Dx = build_dict_x(bb, pp)
        Duu = build_dict_u(bb, pp)
        T = 8000
        hx, vx, _ = measure(Cc, bb, Dx, verify_x, False, T, seed=1000 + bits * 7 + B)
        hu, vu, _ = measure(Cc, bb, Duu, verify_u, True, T, seed=1000 + bits * 7 + B)
        yx, yu = vx / T, vu / T
        cx = yx * pp / (B * B) if yx > 0 else None
        cu = yu * pp / (B * B) if yu > 0 else None
        rows.append((bits, pp, B, beff, vx, yx, cx, vu, yu, cu))
        print(f"  {bits}b p={pp} B={B} Beff={beff} | plain ver={vx} y={yx:.4f} c={cx if cx is None else round(cx,3)} "
              f"| u ver={vu} y={yu:.4f} c={cu if cu is None else round(cu,3)} "
              f"| ratio_c={(cu/cx) if (cx and cu) else 'NA'}")

    # fit slope log(yield) vs log(B^2/p) for u-variant, unsaturated only
    def fit(rows, idx_y):
        xs, ys = [], []
        for r in rows:
            bits, pp, B, beff, vx, yx, cx, vu, yu, cu = r
            y = r[idx_y]
            if 0.0 < y < 0.6:
                xs.append(math.log(B * B / pp))
                ys.append(math.log(y))
        if len(xs) < 2:
            return None, len(xs)
        n = len(xs); mx = sum(xs)/n; my = sum(ys)/n
        num = sum((x-mx)*(yy-my) for x, yy in zip(xs, ys))
        den = sum((x-mx)**2 for x in xs)
        return num/den, len(xs)

    su, nu = fit(rows, 8)   # yu index
    sx, nx = fit(rows, 5)   # yx index
    print(f"\nfit slope log(yield) vs log(B^2/p): plain={sx} (n={nx}) u={su} (n={nu}) [~1 expected]")

    # mean constant ratio over unsaturated well-populated points
    ratios = []
    cus, cxs = [], []
    for r in rows:
        bits, pp, B, beff, vx, yx, cx, vu, yu, cu = r
        if cx and cu and yu < 0.6 and vx >= 30:
            ratios.append(cu / cx)
            cus.append(cu); cxs.append(cx)
    print(f"mean c_u = {sum(cus)/len(cus):.3f}  mean c_plain = {sum(cxs)/len(cxs):.3f}")
    print(f"mean c_u/c_plain ratio (unsat, vx>=30) = {sum(ratios)/len(ratios):.3f} over {len(ratios)} pts")
    print(f"per-point ratios: {[round(x,2) for x in ratios]}")


if __name__ == "__main__":
    main()
