#!/usr/bin/env python3
"""Independent skeptic re-check of variant 'petit'.

Reimplements the petit u=x^3 invariant search and the plain baseline FROM SCRATCH
using only trusted primitives (ec_add/ec_mul/find_toy_curve). Does NOT call the
variant's run functions, so a bug in variant_petit.py cannot leak into the check.
"""
import math, random
from math import isqrt
from toy_curves import find_toy_curve, ec_add, ec_mul
import sympy


def neg(P, p):
    if P is None:
        return None
    x, y = P
    return (x, (-y) % p)


def u_of(x, p):
    return (x * x * x) % p


def petit_cond(x, p, petit_bits, patt=0):
    if petit_bits <= 0:
        return True
    mask = (1 << petit_bits) - 1
    return (u_of(x, p) & mask) == (patt & mask)


def build_base_petit(C, B, petit_bits):
    p, b = C.p, C.b
    base = []
    x = 0
    scanned = 0
    while len(base) < B and x < p:
        scanned += 1
        if petit_cond(x, p, petit_bits):
            rhs = (x * x * x + b) % p
            y = sympy.sqrt_mod(rhs, p)
            if y is not None:
                base.append((x % p, int(y) % p))
        x += 1
    return base, scanned


def build_base_plain(C, B):
    p, b = C.p, C.b
    base = []
    x = 0
    while len(base) < B and x < p:
        rhs = (x * x * x + b) % p
        y = sympy.sqrt_mod(rhs, p)
        if y is not None:
            base.append((x % p, int(y) % p))
        x += 1
    return base


# ---------------- petit (u-keyed) run, reimplemented ----------------

def run_petit(bits, B, petit_bits=1, T=4000, seed=1):
    C = find_toy_curve(bits, seed=seed)
    p = C.p
    base, scanned = build_base_petit(C, B, petit_bits)
    assert len(base) == B, f"short base {len(base)}<{B}"
    # dict keyed on u = x^3
    D = {}
    npairs = 0
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
            npairs += 1
    # distinct u in base = B_eff
    B_eff = len({u_of(P[0], p) for P in base})
    rng = random.Random(1000 + bits * 7 + B)
    hits = verified = false_pos = 0
    for _ in range(T):
        k = rng.randrange(1, C.ell)
        R = ec_mul(k, C.gen, 0, p)
        if R is None:
            continue
        e = D.get(u_of(R[0], p))
        if e is None:
            continue
        hits += 1
        # GROUND TRUTH re-verify by ec_add over phi^m extended base
        i, j, sign = e
        negR = neg(R, p)
        ok = False
        for m in range(3):
            bm = pow(C.beta, m, p)
            Pi = ((bm * base[i][0]) % p, base[i][1])
            Pj = ((bm * base[j][0]) % p, base[j][1])
            if sign == +1:
                S = ec_add(Pi, Pj, 0, p)
            else:
                S = ec_add(Pi, neg(Pj, p), 0, p)
            if S == R or S == negR:
                ok = True
                break
        if ok:
            verified += 1
        else:
            false_pos += 1
    y = verified / T
    return dict(bits=bits, p=p, B=B, B_eff=B_eff, scanned=scanned, npairs=npairs,
                nkeys=len(D), verified=verified, hits=hits, false_pos=false_pos,
                yield_=y, c=y * p / (B * B))


def run_plain(bits, B, T=4000, seed=1):
    C = find_toy_curve(bits, seed=seed)
    p = C.p
    base = build_base_plain(C, B)
    D = {}
    for i in range(len(base)):
        Pi = base[i]
        nPi = neg(Pi, p)
        for j in range(i + 1, len(base)):
            Pj = base[j]
            Sp = ec_add(Pi, Pj, 0, p)
            if Sp is not None:
                D.setdefault(Sp[0], (i, j, +1))
            Sm = ec_add(nPi, Pj, 0, p)
            if Sm is not None:
                D.setdefault(Sm[0], (i, j, -1))
    rng = random.Random(1000 + bits * 7 + B)
    verified = false_pos = 0
    for _ in range(T):
        k = rng.randrange(1, C.ell)
        R = ec_mul(k, C.gen, 0, p)
        if R is None:
            continue
        e = D.get(R[0])
        if e is None:
            continue
        i, j, sign = e
        Pi, Pj = base[i], base[j]
        S = ec_add(Pi, Pj, 0, p) if sign == +1 else ec_add(Pi, neg(Pj, p), 0, p)
        if S == R or S == neg(R, p):
            verified += 1
        else:
            false_pos += 1
    y = verified / T
    return dict(bits=bits, B=B, p=p, verified=verified, false_pos=false_pos,
                yield_=y, c=y * p / (B * B))


def reconstruct_example():
    # report: k=76221 R=76221*G decomposes as -phi(P_1)+phi(P_140), twist_m=1, 20-bit
    C = find_toy_curve(20, seed=1)
    p = C.p
    base, _ = build_base_petit(C, 256, 1)
    P1, P140 = base[1], base[140]
    R = ec_mul(76221, C.gen, 0, p)
    # -phi(P1) + phi(P140): sign=-1 means P_i - P_j family; e_i=-1,e_j=+1 -> -phi(P1)+phi(P140)
    phi = lambda P: ((C.beta * P[0]) % p, P[1])
    S = ec_add(neg(phi(P1), p), phi(P140), 0, p)
    return dict(
        P1=P1, P140=P140,
        P1_on_curve=C.on_curve(P1), P140_on_curve=C.on_curve(P140),
        R=R,
        S_eq_R=(S == R), S_eq_negR=(S == neg(R, p)),
        u_R=u_of(R[0], p), u_S=u_of(S[0], p) if S else None,
        u_match=(S is not None and u_of(R[0], p) == u_of(S[0], p)),
    )


if __name__ == "__main__":
    print("=== 1. Reconstruct reported example (k=76221) ===")
    for k, v in reconstruct_example().items():
        print(f"  {k}: {v}")

    # Reproduce a representative subset of the reported grid rows.
    print("\n=== 2. Reproduce reported petit rows independently ===")
    petit_settings = [(20, 256), (20, 512), (16, 64), (16, 256),
                      (24, 256), (24, 512), (24, 1024)]
    petit_T = {(24, 256): 8000, (24, 512): 8000, (24, 1024): 8000}
    petit_rows = []
    for bits, B in petit_settings:
        T = petit_T.get((bits, B), 4000)
        r = run_petit(bits, B, petit_bits=1, T=T)
        petit_rows.append(r)
        print(f"  bits={bits} B={B} T={T} B_eff={r['B_eff']} dens={B/r['scanned']:.3f} "
              f"ver={r['verified']} yield={r['yield_']:.4f} c={r['c']:.4f} "
              f"false_pos={r['false_pos']}")

    print("\n=== 3. Plain baseline at SAME (bits,B) ===")
    plain_rows = []
    for bits, B in petit_settings:
        T = petit_T.get((bits, B), 4000)
        r = run_plain(bits, B, T=T)
        plain_rows.append(r)
        print(f"  bits={bits} B={B} ver={r['verified']} yield={r['yield_']:.4f} c={r['c']:.4f}")

    print("\n=== 4. Yield-law fit: log(yield) vs log(B^2/p) ===")
    def fit(rows, key='B'):
        u = [r for r in rows if 0.0 < r['yield_'] < 0.6]
        xs = [math.log(r[key] ** 2 / r['p']) for r in u]
        ys = [math.log(r['yield_']) for r in u]
        n = len(xs)
        mx = sum(xs) / n; my = sum(ys) / n
        num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        den = sum((x - mx) ** 2 for x in xs)
        slope = num / den
        icpt = my - slope * mx
        return n, slope, math.exp(icpt), u
    n, sp, cfit, u_p = fit(petit_rows)
    print(f"  PETIT: n_unsat={n} slope={sp:.4f} c(exp intercept)={cfit:.4f}")
    n2, sp2, cfit2, u_pl = fit(plain_rows)
    print(f"  PLAIN: n_unsat={n2} slope={sp2:.4f} c(exp intercept)={cfit2:.4f}")

    print("\n=== 5. Constant c (mean of yield*p/B^2 on unsaturated) & ratio ===")
    c_petit = sum(r['c'] for r in u_p) / len(u_p)
    c_plain = sum(r['c'] for r in u_pl) / len(u_pl)
    print(f"  mean c_petit = {c_petit:.4f}")
    print(f"  mean c_plain = {c_plain:.4f}")
    print(f"  ratio c_petit/c_plain = {c_petit / c_plain:.4f}")
    print("\n  per-setting yield ratio petit/plain (unsaturated plain):")
    for pt, pl in zip(petit_rows, plain_rows):
        if 0 < pl['yield_'] < 0.6:
            print(f"    bits={pt['bits']} B={pt['B']}: {pt['yield_']/pl['yield_']:.3f}")
