#!/usr/bin/env python3
"""Exact toy-only search for a nested two-addition GLV-carry coordinate class.

Target on the C6 quotient:
    H(z) = 1 + c1*z^a
    F(z) = kappa*z^u*H(z)^eps*(1 + c2*z^b*H(z)^t)
    chi_p(F(z(Q))) = h_G(z(Q)) = g_G(Q)*chi_p(y(Q)).

All c2 values are tested exactly with Python integer bitsets. No external point,
key, wallet, or production target is accepted.
"""
from __future__ import annotations
import argparse, json, time
from dataclasses import dataclass
from typing import Optional

Point = Optional[tuple[int, int]]
FROZEN_CASES = {
    271: (1087, 271, (1017, 688)),
    433: (1663, 433, (126, 1375)),
    967: (907, 967, (2, 165)),
}

def ec_add(left: Point, right: Point, p: int) -> Point:
    if left is None: return right
    if right is None: return left
    x1,y1=left; x2,y2=right
    if x1==x2 and (y1+y2)%p==0: return None
    if left==right:
        if y1%p==0: return None
        slope=3*x1*x1*pow(2*y1,-1,p)%p
    else:
        slope=(y2-y1)*pow((x2-x1)%p,-1,p)%p
    x3=(slope*slope-x1-x2)%p
    y3=(slope*(x1-x3)-y1)%p
    return x3,y3

def orbit(generator, order, p):
    points=[None]; point=None
    for _ in range(1,order):
        point=ec_add(point,generator,p); points.append(point)
    if ec_add(point,generator,p) is not None or len(set(points))!=order:
        raise AssertionError("bad subgroup orbit")
    return points

def quadratic_character(value,p):
    value%=p
    if value==0: return 0
    return 1 if pow(value,(p-1)//2,p)==1 else -1

def primitive_cube_root(p):
    for seed in range(2,p):
        beta=pow(seed,(p-1)//3,p)
        if beta!=1 and pow(beta,3,p)==1: return beta
    raise AssertionError("cube root missing")

@dataclass(frozen=True)
class QuotientData:
    p:int; n:int; generator:tuple[int,int]; beta:int; lam:int
    z:tuple[int,...]; target:tuple[int,...]

def quotient_data(case):
    p,n,generator=case; points=orbit(generator,n,p); beta=primitive_cube_root(p)
    scalar_of={point:k for k,point in enumerate(points)}
    lam=scalar_of[(beta*generator[0]%p,generator[1])]; lam2=lam*lam%n
    if (1+lam+lam2)%n: raise AssertionError("bad GLV eigenvalue")
    visited=set(); z_values=[]; targets=[]
    for scalar in range(1,n):
        if scalar in visited: continue
        positive={scalar,lam*scalar%n,lam2*scalar%n}
        orbit6=positive|{n-member for member in positive}
        if len(orbit6)!=6: raise AssertionError("non-free C6 orbit")
        visited.update(orbit6); representative=min(positive)
        x,y=points[representative]
        total=representative+lam*representative%n+lam2*representative%n
        carry=1 if total==2*n else -1
        z_value=pow(x,3,p); target=carry*quadratic_character(y,p)
        for member in orbit6:
            xm,ym=points[member]
            member_total=member+lam*member%n+lam2*member%n
            member_carry=1 if member_total==2*n else -1
            if pow(xm,3,p)!=z_value or member_carry*quadratic_character(ym,p)!=target:
                raise AssertionError("quotient mismatch")
        z_values.append(z_value); targets.append(target)
    if len(z_values)!=(n-1)//6 or len(set(z_values))!=len(z_values):
        raise AssertionError("quotient separation failed")
    return QuotientData(p,n,generator,beta,lam,tuple(z_values),tuple(targets))

def core_exponents(data):
    modulus=data.p-1; values=set()
    add=lambda value: values.add(value%modulus)
    for value in range(-8,9): add(value)
    for value in (16,32,64,128,256,512,1024,2048): add(value); add(-value)
    for divisor in (2,3,4,6,8,12):
        if modulus%divisor==0: add(modulus//divisor); add(-(modulus//divisor))
    for value in (data.n,data.n-1,data.n+1,data.lam,data.lam-1,data.lam+1,
                  abs(data.p-data.n),(data.n-1)//2,(data.n+1)//2):
        add(value); add(-value)
    return sorted(values)

def core_constants(data):
    p=data.p; values=set(); add=lambda value: values.add(value%p)
    for value in range(-8,9): add(value)
    gx,gy=data.generator
    for value in (7,-7,data.beta,data.beta*data.beta,gx,gy,pow(gx,3,p),
                  data.n,data.lam,p-data.n):
        add(value); add(-value)
        if value%p: add(pow(value%p,-1,p)); add(-pow(value%p,-1,p))
    return sorted(values)

def c2_masks(p):
    positive=[0]*p; negative=[0]*p
    for w in range(1,p):
        pos=neg=0
        for c2 in range(p):
            sign=quadratic_character(1+c2*w,p)
            if sign==1: pos|=1<<c2
            elif sign==-1: neg|=1<<c2
        positive[w]=pos; negative[w]=neg
    return positive,negative

def pow_vector(values,exponent,p):
    exponent%=p-1
    return [pow(value,exponent,p) for value in values]

def exact_search(data,exponents,constants,t_values):
    p=data.p; z=data.z; target=data.target
    positive,negative=c2_masks(p); all_c2=(1<<p)-1
    z_powers={e:pow_vector(z,e,p) for e in exponents}
    z_character=tuple(quadratic_character(value,p) for value in z)
    tested_h=tested_w=0; exact=[]; started=time.time()
    for a in exponents:
        za=z_powers[a]
        for c1 in constants:
            c1%=p
            if c1==0: continue
            h_values=[(1+c1*value)%p for value in za]
            if 0 in h_values: continue
            tested_h+=1; h_character=tuple(quadratic_character(value,p) for value in h_values)
            variants=[]
            for u in (0,1):
                for epsilon in (0,1):
                    residual=tuple(target[i]*(z_character[i] if u else 1)*
                                   (h_character[i] if epsilon else 1) for i in range(len(z)))
                    variants.append((u,epsilon,1,residual))
                    variants.append((u,epsilon,-1,tuple(-x for x in residual)))
            for t in t_values:
                ht=pow_vector(h_values,t,p)
                for b in exponents:
                    w_values=[z_powers[b][i]*ht[i]%p for i in range(len(z))]
                    if 0 in w_values: continue
                    tested_w+=1
                    live=[[u,eps,sgn,res,all_c2] for u,eps,sgn,res in variants]
                    for i,w in enumerate(w_values):
                        pm,nm=positive[w],negative[w]; nxt=[]
                        for u,eps,sgn,res,mask in live:
                            mask&=pm if res[i]==1 else nm
                            if mask: nxt.append([u,eps,sgn,res,mask])
                        live=nxt
                        if not live: break
                    for u,eps,sgn,_,mask in live:
                        c2=(mask&-mask).bit_length()-1
                        exact.append({"a":a,"c1":c1,"t":t,"b":b,"c2":c2,
                                      "u":u,"epsilon":eps,"constant_sign":sgn})
    return {"p":p,"n":data.n,"quotient_points":len(z),"exponents":len(exponents),
            "constants_c1":len(constants),"t_values":len(t_values),
            "admissible_H":tested_h,"admissible_W":tested_w,
            "nominal_formula_evaluations":tested_w*p*8,
            "exact_decoders":exact,"seconds":time.time()-started}

def profile(order,name):
    data=quotient_data(FROZEN_CASES[order])
    if name=="core":
        exponents=core_exponents(data)
        return data,exponents,core_constants(data),[e for e in exponents if e%(data.p-1)]
    if name=="base":
        return data,core_exponents(data),core_constants(data),[-1,1,2,3,4,5,7,8,16]
    if name=="all-c1-small":
        return data,list(range(-8,9)),list(range(data.p)),[-1,1,2,3,4,5,7,8,16]
    raise ValueError(name)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--order",type=int,choices=sorted(FROZEN_CASES),default=271)
    parser.add_argument("--profile",choices=("core","base","all-c1-small"),default="base")
    parser.add_argument("--t-start",type=int,default=0); parser.add_argument("--t-stop",type=int)
    parser.add_argument("--out"); args=parser.parse_args()
    data,exponents,constants,t_values=profile(args.order,args.profile)
    t_values=t_values[args.t_start:args.t_stop]
    result=exact_search(data,exponents,constants,t_values)
    result["profile"]=args.profile; result["t_slice"]=[args.t_start,args.t_stop]
    text=json.dumps(result,indent=2,sort_keys=True)
    if args.out: open(args.out,"w",encoding="utf-8").write(text+"\n")
    print(text)

if __name__=="__main__": main()
