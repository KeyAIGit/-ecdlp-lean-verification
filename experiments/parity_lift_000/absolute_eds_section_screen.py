#!/usr/bin/env python3
"""Toy-only replay for ABSOLUTE-EDS-SECTION-003."""
from __future__ import annotations
import argparse,itertools,json,math,random,statistics
from functools import lru_cache
from pathlib import Path
from eisenstein_root_phase_screen import (
    B,FROZEN_CASES,orbit,quadratic_character as qc,
    division_polynomial_evaluator as dpe,
)

JMAX=4
ARAD=4
WMAX=4
GMAX=60
NULLS=200

class S:
    __slots__=("c","p","N")
    def __init__(self,c,p,N):
        c=list(c[:N])+[0]*max(0,N-len(c))
        self.c=tuple(v%p for v in c[:N]);self.p=p;self.N=N
    @classmethod
    def k(cls,v,p,N): return cls([v],p,N)
    @classmethod
    def x(cls,v,p,N): return cls([v,1],p,N)
    def C(self,o): return o if isinstance(o,S) else S.k(o,self.p,self.N)
    def __add__(self,o):
        o=self.C(o);return S([self.c[i]+o.c[i] for i in range(self.N)],self.p,self.N)
    __radd__=__add__
    def __neg__(self): return S([-v for v in self.c],self.p,self.N)
    def __sub__(self,o): return self+(-self.C(o))
    def __rsub__(self,o): return self.C(o)-self
    def __mul__(self,o):
        o=self.C(o);z=[0]*self.N
        for i,a in enumerate(self.c):
            for j,b in enumerate(o.c[:self.N-i]):z[i+j]=(z[i+j]+a*b)%self.p
        return S(z,self.p,self.N)
    __rmul__=__mul__
    def __pow__(self,e):
        if e<0:return self.inv()**(-e)
        r=S.k(1,self.p,self.N);a=self
        while e:
            if e&1:r=r*a
            a=a*a;e>>=1
        return r
    def inv(self):
        if self.c[0]==0:raise ZeroDivisionError
        z=[0]*self.N;z[0]=pow(self.c[0],-1,self.p)
        for n in range(1,self.N):
            z[n]=-z[0]*sum(self.c[i]*z[n-i] for i in range(1,n+1))%self.p
        return S(z,self.p,self.N)
    def __truediv__(self,o):return self*self.C(o).inv()
    def __eq__(self,o):
        o=self.C(o);return self.c==o.c

def sy(rhs,y0):
    p,N=rhs.p,rhs.N;z=[0]*N;z[0]=y0%p;h=pow(2*y0,-1,p)
    for n in range(1,N):
        z[n]=(rhs.c[n]-sum(z[i]*z[n-i] for i in range(1,n)))*h%p
    y=S(z,p,N)
    if y*y!=rhs:raise AssertionError("sqrt series")
    return y

def dps(P,p,N):
    x0,y0=P;x=S.x(x0,p,N);y=sy(x**3+B,y0)
    @lru_cache(None)
    def q(n):
        if n<0:return -q(-n)
        if n==0:return S.k(0,p,N)
        if n==1:return S.k(1,p,N)
        if n==2:return 2*y
        if n==3:return 3*x**4+84*x
        if n==4:return 4*y*(x**6+140*x**3-392)
        if n&1:
            m=(n-1)//2
            return q(m+2)*q(m)**3-q(m-1)*q(m+1)**3
        m=n//2
        return q(m)/(2*y)*(q(m+2)*q(m-1)**2-q(m-2)*q(m+1)**2)
    return q

def raw(P,p,n):
    q=dpe(P,p);a=q(p-1);b=q(p-1+n)
    if not a or not b or math.gcd(n,p-1)!=1:raise AssertionError("raw")
    r=a*pow(b,-1,p)%p;e=pow(n*n%(p-1),-1,p-1);v=pow(r,e,p)
    if pow(v,n*n,p)!=r:raise AssertionError("root")
    return v

def bits(v):
    z=0
    for i,s in enumerate(v):
        if s==-1:z|=1<<i
        elif s!=1:raise AssertionError("non-binary")
    return z

def rho(G,p,n):
    q=dpe(G,p);return [qc(q(k),p) for k in range(1,n)]

def rho_u(r,u,n):
    ru=r[u-1]
    return [r[(u*k)%n-1]*(ru if k&1 else 1) for k in range(1,n)]

def kinv(r,n):return all(r[k-1]==r[n-k-1] for k in range(1,n))

def table(p,n,G):
    P=orbit(G,n,p)
    names=["x"]+[f"jet{j}" for j in range(1,JMAX+1)]
    names += [f"psi_n_minus_{a}" for a in range(1,ARAD+1)]
    names += [f"psi_n_plus_{a}" for a in range(1,ARAD+1)]
    V={s:[None]*n for s in names};ok={s:True for s in names}
    J=[None]*n;JF=[None]*n
    for k,Q in enumerate(P[1:],1):
        x,y=Q;V["x"][k]=qc(x,p);q=dps(Q,p,JMAX+1);f=q(n)
        if f.c[0]:raise AssertionError("torsion root")
        for j in range(1,JMAX+1):
            z=qc(f.c[j],p);V[f"jet{j}"][k]=z
            if not z:ok[f"jet{j}"]=False
        JF[k]=2*y*f.c[1]%p;J[k]=qc(JF[k],p)
        for a in range(1,ARAD+1):
            for pre,m in (("psi_n_minus",n-a),("psi_n_plus",n+a)):
                s=f"{pre}_{a}";z=qc(q(m).c[0],p);V[s][k]=z
                if not z:ok[s]=False
    return P,{s:v for s,v in V.items() if ok[s]},J,JF,[s for s in names if not ok[s]]

def pbits(v,u,n):return bits([v[u*k%n] for k in range(1,n)])

def products(B):
    I=list(B.items());R={0:"1"}
    for w in range(1,min(WMAX,len(I))+1):
        for C in itertools.combinations(I,w):
            z=0;N=[]
            for s,v in C:z^=v;N.append(s)
            R.setdefault(z,"*".join(N))
    return R

def best(V,t,L):
    z=(-1,"",1,-1)
    for v,s in V.items():
        d=(v^t).bit_count();m=L-d;sg=1
        if d>m:m=d;sg=-1
        if m>z[0] or (m==z[0] and s<z[1]):z=(m,s,sg,d)
    return z[0]/L,z[1],z[2],z[0]

def krand(n,R):
    z=0
    for k in range(1,(n+1)//2):
        if R.getrandbits(1):z|=(1<<(k-1))|(1<<(n-k-1))
    return z

def case(p,n,G):
    if p==n:return {"p":p,"order":n,"base_generator":list(G),
        "status":"excluded_anomalous_p_equals_order",
        "reason":"psi_n is inseparable in characteristic n; first torsion jet vanishes"}
    P,V,J,JF,bad=table(p,n,G);R=rho(G,p,n);qG=dpe(G,p)
    jG=JF[1];b=qc(jG,p);a=qc(-n*jG,p);ap=qc(raw(G,p,n),p)
    field=char=near=True
    for k,Q in enumerate(P[1:],1):
        e=(-1 if (k-1)&1 else 1)*pow(n%p,1-k*k,p)*pow(jG,k*k,p)*pow(qG(k),-n*n,p)%p
        field &= JF[k]==e
        char &= J[k]==b*(a if (k-1)&1 else 1)*R[k-1]
        c=(a if k&1 else 1)*R[k-1]
        near &= V["psi_n_plus_1"][k]==c and V["psi_n_minus_1"][k]==qc(-1,p)*c
    L=n-1;groups=[];obs=(-1.0,0,"",1,0);exact=0
    for u in range(1,n):
        T=rho_u(R,u,n)
        if not kinv(T,n):continue
        target=bits(T);PV=products({s:pbits(v,u,n) for s,v in V.items()})
        ac,nm,sg,mt=best(PV,target,L);exact+=ac==1
        if ac>obs[0] or (ac==obs[0] and u<obs[1]):obs=(ac,u,nm,sg,mt)
        groups.append(list(PV))
        if len(groups)>=GMAX:break
    rng=random.Random(20260812+p+n);null=[]
    for _ in range(NULLS):
        M=.5
        for VV in groups:
            t=krand(n,rng)
            for v in VV:
                d=(v^t).bit_count();M=max(M,max(L-d,d)/L)
        null.append(M)
    null.sort();q95=null[math.ceil(.95*NULLS)-1]
    return {"p":p,"order":n,"base_generator":list(G),"status":"screened",
      "base_rho_kummer_invariant":kinv(R,n),
      "first_jet":{"b_G":b,"a_G":a,"chi_phi_raw_G":ap,"field_identity":field,
        "character_identity":char,"a_alignment":a==ap,"checks":L},
      "near_period_one":{"passed":near,"checks":2*L},
      "valid_candidates":len(V),"invalid_candidates":bad,
      "invariant_generators_tested":len(groups),"exact_decoders":exact,
      "best_candidate":obs[2],"best_generator_multiplier":obs[1],
      "best_global_sign":obs[3],"best_matches":obs[4],"total":L,
      "best_accuracy":obs[0],"best_excess_times_sqrt_order":(obs[0]-.5)*math.sqrt(n),
      "null_trials":NULLS,"null_median":statistics.median(null),"null_q95":q95,
      "empirical_null_percentile":sum(v<=obs[0] for v in null)/NULLS}

def main():
    A=argparse.ArgumentParser();A.add_argument("--out",type=Path,
      default=Path(__file__).with_name("absolute_eds_section_results.json"));a=A.parse_args()
    C=[case(*x) for x in FROZEN_CASES];S=[x for x in C if x["status"]=="screened"]
    O={"scope":"fifteen frozen j=0 toy subgroups on y^2=x^3+7; no secp256k1 target",
      "package":"ABSOLUTE-EDS-SECTION-003","target":"rho_G([k]G)=chi(psi_k(G))",
      "identities":{
       "first_jet_field":"J_n([k]G)=(-1)^(k-1)*n^(1-k^2)*J_n(G)^(k^2)*psi_k(G)^(-n^2)",
       "first_jet_character":"chi(J_n([k]G))=b_G*a_G^(k-1)*rho_G(k)",
       "J_n":"D_omega psi_n=2*y*d(psi_n)/dx",
       "a_G":"chi(-n*J_n(G))=chi(phi_raw(G))",
       "near_plus_one":"chi(psi_(n+1)([k]G))=chi(phi_raw(G))^k*rho_G(k)",
       "near_minus_one":"chi(psi_(n-1)([k]G))=chi(-1)*chi(phi_raw(G))^k*rho_G(k)"},
      "protocol":{"maximum_kummer_invariant_generators_per_case":GMAX,
       "null_trials_per_case":NULLS,"maximum_product_weight":WMAX,
       "global_sign_allowed":True,"anomalous_p_equals_order_excluded":True},
      "cases":C,"aggregate":{"cases_total":len(C),"cases_screened":len(S),
       "anomalous_cases_excluded":len(C)-len(S),
       "first_jet_checks":sum(x["first_jet"]["checks"] for x in S),
       "all_exact_first_jet_field_identities_passed":all(x["first_jet"]["field_identity"] for x in S),
       "all_first_jet_character_identities_passed":all(x["first_jet"]["character_identity"] for x in S),
       "all_a_G_equal_chi_phi_raw_G":all(x["first_jet"]["a_alignment"] for x in S),
       "near_period_one_checks":sum(x["near_period_one"]["checks"] for x in S),
       "all_near_period_one_identities_passed":all(x["near_period_one"]["passed"] for x in S),
       "exact_decoders_found":sum(x["exact_decoders"] for x in S),
       "cases_above_matched_null_q95":sum(x["best_accuracy"]>x["null_q95"] for x in S),
       "maximum_empirical_null_percentile":max(x["empirical_null_percentile"] for x in S)},
      "claim_boundary":["Bounded toy structural evidence, not an asymptotic lower bound.",
       "No external point, key, wallet, or production-sized target is accepted."]}
    a.out.write_text(json.dumps(O,indent=2),encoding="utf-8");print(json.dumps(O,indent=2))
if __name__=="__main__":main()
