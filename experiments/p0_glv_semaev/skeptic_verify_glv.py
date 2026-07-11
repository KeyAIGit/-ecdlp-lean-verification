#!/usr/bin/env python3
"""Independent skeptic re-check of variant glv-base. Does NOT import the variant's
run functions for the yield measurement -- reimplements from scratch on the same
toy curves so an artifact in the variant code cannot leak in. Reuses ONLY the
trusted primitives ec_add/ec_mul/find_toy_curve/build_base."""
import math, random
from math import isqrt
from toy_curves import find_toy_curve, ec_add, ec_mul
from semaev_core import build_base, neg

# ---------------------------------------------------------------- 1. reconstruct reported example
def reconstruct_reported_example():
    # from report: bits=20 p=1048609
    C = find_toy_curve(20, seed=1)
    p = C.p
    Pi = (148, 315555); Pj = (515, 340607)
    # apply phi^2
    def phi2(P):
        b2 = (C.beta*C.beta) % p
        return ((b2*P[0]) % p, P[1])
    ph_i = phi2(Pi); ph_j = phi2(Pj)
    R_reported = (386276, 771641)
    k = 215561
    checks = {}
    checks["Pi_on_curve"] = C.on_curve(Pi)
    checks["Pj_on_curve"] = C.on_curve(Pj)
    checks["phi2Pi_matches_report"] = ph_i == (844265, 315555)
    checks["phi2Pj_matches_report"] = ph_j == (876022, 340607)
    checks["phi2Pi_on_curve"] = C.on_curve(ph_i)
    checks["phi2Pj_on_curve"] = C.on_curve(ph_j)
    S = ec_add(ph_i, neg(ph_j, p), 0, p)  # phi2(Pi) - phi2(Pj)
    R_from_k = ec_mul(k, C.gen, 0, p)
    checks["R=k*G_matches_report"] = (R_from_k == R_reported)
    checks["phi2Pi - phi2Pj == R (or -R)"] = (S == R_reported or S == neg(R_reported, p))
    checks["S_value"] = S
    checks["R_reported"] = R_reported
    return checks

# ---------------------------------------------------------------- 2. independent glv yield
def glv_dict_independent(base, C):
    """Rebuild the free-orbit dict independently: for each pair, register x, beta*x, beta^2*x."""
    p = C.p; beta = C.beta
    betas = [1, beta % p, (beta*beta) % p]
    D = {}
    npairs = 0
    B = len(base)
    for i in range(B):
        Pi = base[i]; nPj_base = None
        for j in range(i+1, B):
            Pj = base[j]
            Sp = ec_add(Pi, Pj, 0, p)
            if Sp is not None:
                for s in range(3):
                    D.setdefault((betas[s]*Sp[0]) % p, (i, j, +1, s))
            Sm = ec_add(Pi, neg(Pj, p), 0, p)
            if Sm is not None:
                for s in range(3):
                    D.setdefault((betas[s]*Sm[0]) % p, (i, j, -1, s))
            npairs += 1
    return D, npairs

def phi_pow(C, P, s):
    for _ in range(s % 3):
        P = C.phi(P)
    return P

def ec_verify_glv(C, base, entry, R):
    p = C.p
    i, j, sign, s = entry
    Pi = phi_pow(C, base[i], s); Pj = phi_pow(C, base[j], s)
    negR = neg(R, p)
    if sign == +1:
        S = ec_add(Pi, Pj, 0, p)
    else:
        S = ec_add(Pi, neg(Pj, p), 0, p)
    return S == R or S == negR

def run_glv(bits, store_B, T=4000, seed=1):
    C = find_toy_curve(bits, seed=seed)
    p = C.p
    base = build_base(C, store_B)
    D, npairs = glv_dict_independent(base, C)
    # B_eff = distinct x in orbit closure
    betas = [1, C.beta % p, (C.beta*C.beta) % p]
    xs = set()
    for (x,_y) in base:
        for bb in betas:
            xs.add((bb*x) % p)
    B_eff = len(xs)
    rng = random.Random(1000 + bits*7 + store_B)
    hits = 0; verified = 0; false_pos = 0
    for _ in range(T):
        k = rng.randrange(1, C.ell)
        R = ec_mul(k, C.gen, 0, p)
        if R is None: continue
        e = D.get(R[0])
        if e is None: continue
        hits += 1
        if ec_verify_glv(C, base, e, R):
            verified += 1
        else:
            false_pos += 1
    y = verified / T
    return dict(bits=bits, p=p, store_B=store_B, B_eff=B_eff, npairs=npairs,
               nkeys=len(D), verified=verified, hits=hits, false_pos=false_pos,
               yield_=y, c_eff=y*p/(B_eff*B_eff), c_store=y*p/(store_B*store_B))

def run_plain(bits, B, T=4000, seed=1):
    C = find_toy_curve(bits, seed=seed)
    p = C.p
    base = build_base(C, B)
    D = {}
    for i in range(len(base)):
        Pi = base[i]
        for j in range(i+1, len(base)):
            Pj = base[j]
            Sp = ec_add(Pi, Pj, 0, p)
            if Sp is not None: D.setdefault(Sp[0], (i,j,+1))
            Sm = ec_add(Pi, neg(Pj,p), 0, p)
            if Sm is not None: D.setdefault(Sm[0], (i,j,-1))
    rng = random.Random(1000 + bits*7 + B)
    verified = 0; false_pos = 0
    for _ in range(T):
        k = rng.randrange(1, C.ell)
        R = ec_mul(k, C.gen, 0, p)
        if R is None: continue
        e = D.get(R[0])
        if e is None: continue
        i,j,sign = e
        Pi, Pj = base[i], base[j]
        if sign==+1: S = ec_add(Pi,Pj,0,p)
        else: S = ec_add(Pi, neg(Pj,p),0,p)
        if S==R or S==neg(R,p): verified += 1
        else: false_pos += 1
    y = verified/T
    return dict(bits=bits, B=B, p=p, verified=verified, false_pos=false_pos,
                yield_=y, c=y*p/(B*B))

if __name__ == "__main__":
    print("=== 1. Reconstruct reported example ===")
    for k,v in reconstruct_reported_example().items():
        print(f"  {k}: {v}")

    print("\n=== 2. Independent GLV yield (subset of grid: 16 and 20 bit) ===")
    # store_B = base_size_eff/3 from report rows
    glv_settings = [(16,64),(16,253),(20,256),(20,512),(20,1022)]
    glv_rows = []
    for bits,sB in glv_settings:
        r = run_glv(bits, sB)
        glv_rows.append(r)
        print(f"  bits={bits} store_B={sB} B_eff={r['B_eff']} eff/store={r['B_eff']/sB:.3f} "
              f"ver={r['verified']} yield={r['yield_']:.4f} c_eff={r['c_eff']:.4f} "
              f"c_store={r['c_store']:.4f} false_pos={r['false_pos']}")

    print("\n=== 3. Independent plain yield at SAME store_B ===")
    plain_rows = []
    for bits,sB in glv_settings:
        r = run_plain(bits, sB)
        plain_rows.append(r)
        print(f"  bits={bits} B={sB} ver={r['verified']} yield={r['yield_']:.4f} "
              f"c={r['c']:.4f} false_pos={r['false_pos']}")

    print("\n=== 4. Yield-law fit: log(yield) vs log(B_eff^2/p), slope should be ~1 ===")
    unsat = [r for r in glv_rows if 0.0 < r['yield_'] < 0.6]
    xs = [math.log(r['B_eff']**2 / r['p']) for r in unsat]
    ys = [math.log(r['yield_']) for r in unsat]
    n = len(xs); mx=sum(xs)/n; my=sum(ys)/n
    num = sum((x-mx)*(y-my) for x,y in zip(xs,ys)); den = sum((x-mx)**2 for x in xs)
    slope = num/den
    intercept = my - slope*mx
    print(f"  n_unsat={n} slope={slope:.4f} intercept(=ln c)={intercept:.4f} c=exp={math.exp(intercept):.4f}")

    # plain fit vs B^2/p
    unsatp = [r for r in plain_rows if 0.0 < r['yield_'] < 0.6]
    xsp = [math.log(r['B']**2 / r['p']) for r in unsatp]
    ysp = [math.log(r['yield_']) for r in unsatp]
    if len(xsp) >= 2:
        n2=len(xsp); mxp=sum(xsp)/n2; myp=sum(ysp)/n2
        slopep=sum((x-mxp)*(y-myp) for x,y in zip(xsp,ysp))/sum((x-mxp)**2 for x in xsp)
        print(f"  plain slope={slopep:.4f}")

    print("\n=== 5. Constant ratios ===")
    c_eff_mean = sum(r['c_eff'] for r in unsat)/len(unsat)
    c_store_mean = sum(r['c_store'] for r in unsat)/len(unsat)
    c_plain_mean = sum(r['c'] for r in unsatp)/len(unsatp) if unsatp else float('nan')
    print(f"  mean c_eff (GLV vs B_eff) = {c_eff_mean:.4f}")
    print(f"  mean c_store (GLV vs store_B) = {c_store_mean:.4f}")
    print(f"  mean c_plain (plain vs B) = {c_plain_mean:.4f}")
    print(f"  ratio c_eff/c_plain = {c_eff_mean/c_plain_mean:.4f}")
    print(f"  ratio c_store/c_plain = {c_store_mean/c_plain_mean:.4f}")
    print(f"  per-storage yield ratio GLV/plain:")
    for g,pl in zip(glv_rows, plain_rows):
        if 0<pl['yield_']<0.6:
            print(f"    bits={g['bits']} store_B={g['store_B']}: {g['yield_']/pl['yield_']:.3f}")
