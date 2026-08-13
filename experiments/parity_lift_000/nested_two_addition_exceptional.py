#!/usr/bin/env python3
"""Exact toy-only search of character-symmetric nested two-addition circuits.

H(Q)=1+c1*x(Q)^a*y(Q)^b
F(Q)=kappa*x(Q)^u*y(Q)^v*H(Q)^eps
     *(1+c2*x(Q)^r*y(Q)^s*H(Q)^t).

Intermediate functions need not descend to the C6 quotient. Exact carry
correctness is tested directly on every nonzero subgroup point.
"""
from __future__ import annotations
import argparse, json, time
from dataclasses import dataclass
from nested_two_addition_coordinate import (
    FROZEN_CASES, QuotientData, core_constants, c2_masks, orbit,
    primitive_cube_root, quadratic_character,
)

@dataclass(frozen=True)
class FullData:
    p:int; n:int; generator:tuple[int,int]; beta:int; lam:int
    x:tuple[int,...]; y:tuple[int,...]; target:tuple[int,...]

def full_data(case):
    p,n,generator=case; points=orbit(generator,n,p); beta=primitive_cube_root(p)
    scalar_of={point:k for k,point in enumerate(points)}
    lam=scalar_of[(beta*generator[0]%p,generator[1])]; lam2=lam*lam%n
    if (1+lam+lam2)%n: raise AssertionError("bad GLV eigenvalue")
    xs=[]; ys=[]; targets=[]
    for scalar in range(1,n):
        x,y=points[scalar]
        total=scalar+lam*scalar%n+lam2*scalar%n
        if total not in (n,2*n): raise AssertionError("bad carry")
        xs.append(x); ys.append(y); targets.append(1 if total==2*n else -1)
    if 0 in xs or 0 in ys: raise AssertionError("profile requires nonzero coordinates")
    return FullData(p,n,generator,beta,lam,tuple(xs),tuple(ys),tuple(targets))

def constants_for(data):
    return core_constants(QuotientData(data.p,data.n,data.generator,data.beta,data.lam,(),()))

def exact_search(data,exponents,constants,t_values):
    p=data.p; count=data.n-1; positive,negative=c2_masks(p); all_c2=(1<<p)-1
    xp={e:tuple(pow(value,e%(p-1),p) for value in data.x) for e in exponents}
    yp={e:tuple(pow(value,e%(p-1),p) for value in data.y) for e in exponents}
    monomials={(a,b):tuple(xp[a][i]*yp[b][i]%p for i in range(count))
               for a in exponents for b in exponents}
    xc=tuple(quadratic_character(value,p) for value in data.x)
    yc=tuple(quadratic_character(value,p) for value in data.y)
    outside=[]
    for u in (0,1):
        for v in (0,1):
            outside.append((u,v,tuple((xc[i] if u else 1)*(yc[i] if v else 1)
                                      for i in range(count))))
    exact=[]; tested_h=tested_w=0; started=time.time()
    for m1_key,m1 in monomials.items():
        for c1 in constants:
            c1%=p
            if c1==0: continue
            h=tuple((1+c1*value)%p for value in m1)
            if 0 in h: continue
            tested_h+=1; hc=tuple(quadratic_character(value,p) for value in h)
            variants=[]
            for u,v,out in outside:
                for eps in (0,1):
                    residual=tuple(data.target[i]*out[i]*(hc[i] if eps else 1)
                                   for i in range(count))
                    variants.append((u,v,eps,1,residual))
                    variants.append((u,v,eps,-1,tuple(-q for q in residual)))
            for t in t_values:
                ht=tuple(pow(value,t%(p-1),p) for value in h)
                for m2_key,m2 in monomials.items():
                    w=tuple(m2[i]*ht[i]%p for i in range(count)); tested_w+=1
                    live=[[u,v,eps,sgn,res,all_c2] for u,v,eps,sgn,res in variants]
                    for i,wv in enumerate(w):
                        pm,nm=positive[wv],negative[wv]; nxt=[]
                        for u,v,eps,sgn,res,mask in live:
                            mask&=pm if res[i]==1 else nm
                            if mask: nxt.append([u,v,eps,sgn,res,mask])
                        live=nxt
                        if not live: break
                    for u,v,eps,sgn,_,mask in live:
                        c2=(mask&-mask).bit_length()-1
                        exact.append({"m1":list(m1_key),"c1":c1,"t":t,
                                      "m2":list(m2_key),"c2":c2,"u":u,"v":v,
                                      "epsilon":eps,"constant_sign":sgn})
    return {"p":p,"n":data.n,"points":count,"monomial_exponent_values":len(exponents),
            "monomials":len(monomials),"constants_c1":len(constants),
            "t_values":len(t_values),"admissible_H":tested_h,"admissible_W":tested_w,
            "outside_square_classes":16,"nominal_formula_evaluations":tested_w*p*16,
            "exact_decoders":exact,"seconds":time.time()-started}

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--order",type=int,choices=(271,433),default=271)
    parser.add_argument("--t-start",type=int,default=0); parser.add_argument("--t-stop",type=int)
    parser.add_argument("--out"); args=parser.parse_args()
    data=full_data(FROZEN_CASES[args.order])
    exponents=list(range(-4,5)) if args.order==271 else list(range(-3,4))
    t_values=[-1,1,2,3,4,5,7,8,16][args.t_start:args.t_stop]
    result=exact_search(data,exponents,constants_for(data),t_values)
    result["t_slice"]=[args.t_start,args.t_stop]
    text=json.dumps(result,indent=2,sort_keys=True)
    if args.out: open(args.out,"w",encoding="utf-8").write(text+"\n")
    print(text)

if __name__=="__main__": main()
