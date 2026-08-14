#!/usr/bin/env python3
"""Lightweight exact replay for UORC056 C21.

Reconstructs the C20 norm-one twist on the public seven-curve corpus and six
public generator replacements. It verifies the Hilbert-90 reciprocity,
minimum half-divisor lower bound, fixed-field gauge obstruction, and the
canonical infinity normalization. No external point or unknown scalar input
is accepted.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
SECP_N = int("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141", 16)
SPLITS = ("discovery",) * 3 + ("validation",) * 2 + ("held_out",) * 2


def load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


c17 = load("uorc056_c17_for_c21_light", "uorc056_odd_symmetric_glv_invariants.py")
c19 = load("uorc056_c19_for_c21_light", "uorc056_odd_rational_functional_boundary.py")


def rf_one(C): return ([1], [0], [1])
def rf_neg(C, f): return C.rf_norm((f[0], C.negp(f[1]), f[2]))
def rf_norm3(C, f):
    f1 = C.rf_phi(f); f2 = C.rf_phi(f1)
    return C.rf_mul(C.rf_mul(f, f1), f2)


def rf_eq(C, f, g) -> bool:
    f, g = C.rf_norm(f), C.rf_norm(g)
    return (C.subp(C.mulp(f[0], g[2]), C.mulp(g[0], f[2])) == [0]
            and C.subp(C.mulp(f[1], g[2]), C.mulp(g[1], f[2])) == [0])


def y_minus(C, y0): return ([-y0 % C.p], [1], [1])


def class_index(n: int) -> int:
    r = (n + 1) // 4 if n % 4 == 3 else (n - 1) // 4
    return r * (2 * r + (-1 if n % 4 == 3 else 1)) % n


def x3_component(C, P):
    residues = {i % 3 for i, c in enumerate(P) if c % C.p}
    if not residues: return [0]
    assert len(residues) == 1
    r = next(iter(residues))
    Q = [0] * ((len(P) - 1 - r) // 3 + 1)
    for i, c in enumerate(P):
        if c % C.p:
            assert i % 3 == r
            Q[(i-r)//3] = c % C.p
    return C.tr(Q)


def compose_y2_minus_7(C, Q):
    out, base = [0], [(-7) % C.p, 0, 1]
    for c in reversed(Q):
        out = C.mulp(out, base); out[0] = (out[0] + c) % C.p
    return C.tr(out)


def rf_to_y(C, f):
    A, B, D = C.rf_norm(f)
    N, Odd, Den = map(lambda P: compose_y2_minus_7(C, x3_component(C, P)), (A, B, D))
    N += [0] * max(0, len(Odd) + 1 - len(N))
    for i, c in enumerate(Odd): N[i+1] = (N[i+1] + c) % C.p
    N = C.tr(N)
    g = C.gcd(N, Den)
    if g != [1]: N, Den = C.exactdiv(N, g), C.exactdiv(Den, g)
    scale = pow(Den[-1], -1, C.p)
    return C.sc(N, scale), C.sc(Den, scale)


def neg_y(C, P): return C.tr([c * (-1 if i & 1 else 1) % C.p for i, c in enumerate(P)])
def yr_norm(C, f):
    N, D = map(C.tr, f); g = C.gcd(N, D)
    if g != [1]: N, D = C.exactdiv(N, g), C.exactdiv(D, g)
    s = pow(D[-1], -1, C.p)
    return C.sc(N, s), C.sc(D, s)
def yr_mul(C, f, g): return yr_norm(C, (C.mulp(f[0], g[0]), C.mulp(f[1], g[1])))
def yr_div(C, f, g): return yr_norm(C, (C.mulp(f[0], g[1]), C.mulp(f[1], g[0])))
def yr_tau(C, f): return yr_norm(C, (neg_y(C, f[0]), neg_y(C, f[1])))
def yr_eq(C, f, g): return C.subp(C.mulp(f[0], g[1]), C.mulp(g[0], f[1])) == [0]


def multiplicity(C, P, root):
    q, count, linear = P, 0, [(-root) % C.p, 1]
    while len(q) > 1 and C.ev(q, root) == 0:
        q = C.exactdiv(q, linear); count += 1
    return count


def divisor(C, f):
    N, D = yr_norm(C, f); finite = {}
    for y in range(C.p):
        v = multiplicity(C, N, y) - multiplicity(C, D, y)
        if v: finite[y] = v
    inf = len(D) - len(N)
    zeros = sum(max(v,0) for v in finite.values()) + max(inf,0)
    poles = sum(max(-v,0) for v in finite.values()) + max(-inf,0)
    assert zeros == poles and finite.get(0,0) == 0 and inf == 0
    return finite, poles


def half_bounds_and_witness(C, R, finite, poles):
    pairs, seen = [], {0}
    for y in range(1, C.p):
        if y in seen: continue
        yn = (-y) % C.p; seen |= {y, yn}
        s = finite.get(y,0); assert finite.get(yn,0) == -s
        if s: pairs.append((y,yn,s))
    support_lb = len(pairs); pole_lb = (poles + 1)//2
    R0 = C.ev(R[0],0) * pow(C.ev(R[1],0),-1,C.p) % C.p
    parity0 = 0 if R0 == 1 else 1
    dp = {0:(0,[])}; base_l1 = 0
    for y,yn,s in pairs:
        base_l1 += abs(s); new = {}
        lo, hi = (0,s) if s>0 else (s,0)
        opts = [(u+(u-s), int(u!=0)+int(u-s!=0), u, u-s) for u in range(lo,hi+1)]
        for total,(supp,wit) in dp.items():
            for q,ss,u,v in opts:
                cand=(supp+ss,wit+[(y,yn,u,v)]); key=total+q
                if key not in new or cand[0] < new[key][0]: new[key]=cand
        dp=new
    best = None
    for Q,(supp,wit) in dp.items():
        for hinf in range(-abs(Q)-6,abs(Q)+7):
            if hinf & 1: continue
            h0=-Q-hinf
            if h0 % 2 != parity0: continue
            metric=((base_l1+abs(h0)+abs(hinf))//2,supp+(h0!=0)+(hinf!=0))
            if best is None or metric < best: best=metric
    assert best and best[0] == pole_lb and best[1] >= support_lb
    return support_lb, best


def run_case(case, split):
    p,n,G,beta,lam = case; C = c17.RFContext(p,G,beta); points=C.points(n)
    Z,_ = c19.endpoint_function(C,n,points); M=rf_norm3(C,Z); a=class_index(n); m=(n-1)//2
    C0=C.rf_div(y_minus(C,points[(a-1)%n][1]),
                C.rf_mul(C.rf_mul(y_minus(C,points[1][1]),y_minus(C,points[a][1])),y_minus(C,points[m][1])))
    R=C.rf_div(M,C0); assert rf_eq(C,C.rf_mul(R,rf_neg(C,R)),rf_one(C))
    Ry=rf_to_y(C,R); assert yr_eq(C,yr_mul(C,Ry,yr_tau(C,Ry)),([1],[1]))
    transformed=neg_y(C,Ry[0]); transformed=C.sc(transformed,pow(transformed[-1],-1,p))
    assert transformed == Ry[1]
    finite,poles=divisor(C,Ry); pair_count,best=half_bounds_and_witness(C,Ry,finite,poles)
    Rinf=Ry[0][-1]*pow(Ry[1][-1],-1,p)%p; assert Rinf==1
    d=len(Ry[0])-1; H=Ry[0] if d%2==0 else C.mulp([0,1],Ry[0])
    assert yr_eq(C,yr_div(C,(H,[1]),yr_tau(C,(H,[1]))),Ry)
    return {"p":p,"n":n,"G":list(G),"split":split,"R_degrees":[len(Ry[0])-1,len(Ry[1])-1],
            "R_support":len(finite),"R_poles":poles,"tau_pairs":pair_count,
            "minimum_H_poles":best[0],"minimum_H_support":best[1],
            "canonical_H_degree":len(H)-1,"R_infinity":Rinf,
            "denominator_is_monic_tau_numerator":True}


def corpus(): return c17.public_extension_corpus(7)
def replacements():
    out=[]
    for p,n,G,beta,lam in corpus()[:2]:
        C=c17.RFContext(p,G,beta)
        for u in (2,3,5):
            P=None
            for _ in range(u): P=C.ec_add(P,G)
            out.append(((p,n,P,beta,lam),u,G))
    return out


def secp():
    _,_,counts=c19.glv_root_and_parity_orbit_counts(SECP_N); n0,n1,_,_=counts
    rp=3*n0+n1-12; rs=(SECP_N-1)//3-8
    return {"R_pole_lower_bound":str(rp),"R_support_lower_bound":str(rs),
            "H_pole_lower_bound":str((rp+1)//2),"H_support_lower_bound":str(rs//2)}


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--out',type=Path); args=parser.parse_args()
    cases=[run_case(c,s) for c,s in zip(corpus(),SPLITS)]
    reps=[]
    for c,u,G0 in replacements():
        row=run_case(c,'generator_replacement'); row['multiplier']=u; row['base_G']=list(G0); reps.append(row)
    payload={"experiment":"C21-HILBERT90-LIGHT","cases":cases,"generator_replacements":reps,"secp256k1":secp(),
             "aggregate":{"curves":7,"replacements":6,"all_norm_one":True,"all_half_bounds_exact":True,
                          "all_infinity_normalizations_one":True,"compact_public_H_found":False,
                          "sub_sqrt_evaluator_found":False,"parity_oracle_found":False}}
    raw=json.dumps(payload,sort_keys=True,separators=(',',':')); payload['digest']=hashlib.sha256(raw.encode()).hexdigest()
    text=json.dumps(payload,indent=2,sort_keys=True); print(text)
    if args.out: args.out.write_text(text+'\n')

if __name__=='__main__': main()
