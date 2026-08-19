from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from itertools import combinations
from typing import Any

from uorc056_c54_transfer_core import (
    Curve, state, chi, point_count, is_prime, B_direct,
    t_double, r_double, a_transfer_double, b_transfer_double,
    addition_cocycle_B, multiplier_cocycle, generate_rows,
    poly_from_roots, berlekamp_massey, tangent_add,
)

FROZEN = (
    (43,31,(2,12),6,5),
    (67,79,(2,22),29,23),
    (79,67,(1,18),23,29),
    (163,139,(2,34),58,96),
)
HELD_OUT = (
    (97,79,(1,28),35,55),
    (211,199,(3,33),14,106),
    (349,313,(2,109),122,214),
    (433,397,(1,21),198,362),
    (577,613,(1,68),213,65),
    (733,691,(6,174),307,253),
    (823,829,(1,255),174,125),
    (907,967,(2,165),384,824),
)
NEW = (
    (1831,1753,(1,639),1158,1570),
    (2143,2089,(1,505),1793,1262),
    (2251,2341,(3,1084),1542,1234),
    (2503,2557,(1,343),1276,1721),
)
ALL = FROZEN + HELD_OUT + NEW

SECP_P=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
SECP_N=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
SECP_G=(
    55066263022277343669578718895168534326250603453777594175500187360389116729240,
    32670510020758816978083085130507043184471273380659243275938904335757337482424,
)
SECP_BETA=int("7AE96A2B657C07106E64479EAC3434E99CF0497512F58995C1396C28719501EE",16)
SECP_LAMBDA=int("5363AD4CC05C30E0A5261C028812645A122E22EA20816678DF02967C1B23BD72",16)
SECP_ORD2=(SECP_N-1)//64


class XorBasis:
    def __init__(self):
        self.rows: dict[int,int] = {}
    def add(self,v:int):
        x=v
        while x:
            p=x.bit_length()-1
            if p in self.rows: x ^= self.rows[p]
            else:
                self.rows[p]=x; return
    def contains(self,v:int)->bool:
        x=v
        while x:
            p=x.bit_length()-1
            if p not in self.rows:return False
            x ^= self.rows[p]
        return True
    @property
    def rank(self):return len(self.rows)


def normalize_bits(signs:list[int], targets:list[int])->tuple[int,int]:
    if not signs or 0 in signs:
        raise ValueError
    base=signs[0]
    tbase=targets[0]
    sv=tv=0
    for i,(s,t) in enumerate(zip(signs,targets)):
        if s!=base: sv |= 1<<i
        if t!=tbase: tv |= 1<<i
    return sv,tv


def curve_context(row):
    p,n,G,beta,lam=row
    E=Curve(p)
    if point_count(E)!=n or not is_prime(n) or E.mul(n,G) is not None:
        raise AssertionError(f"fixture failed {row}")
    if pow(beta,3,p)!=1 or beta==1 or (lam*lam+lam+1)%n:
        raise AssertionError("CM constants")
    if E.mul(lam,G,n)!=(beta*G[0]%p,G[1]):
        raise AssertionError("GLV")
    states={}
    for k in range(1,n):
        P=E.mul(k,G,n)
        if P is None: raise AssertionError
        states[k]=state(E,n,G,P)
    return E,p,n,G,beta,lam,states


def candidate_multipliers(n:int,lam:int)->list[tuple[str,int]]:
    raw=[
        ("2",2),("3",3),("4",4),("5",5),("7",7),("8",8),("16",16),
        ("lambda",lam),("lambda2",lam*lam%n),
        ("halfminus",(n-1)//2),("halfplus",(n+1)//2),
        ("n-2",n-2),("n-3",n-3),
    ]
    out=[]; seen=set()
    for name,m in raw:
        m%=n
        if m not in (0,1) and m not in seen:
            seen.add(m); out.append((name,m))
    return out


def signal_table(E,p,n,G,beta,lam,states):
    """Uniform public field-valued states keyed by structural label."""
    signals: dict[str,dict[int,int]]={}
    base_names=("A","B","N","T","R","S")
    for name in base_names:
        signals[name]={k:states[k][name] for k in states}
    signals["A_over_B"]={k:states[k]["A"]*pow(states[k]["B"],-1,p)%p for k in states if states[k]["B"]}
    signals["B2"]={k:states[k]["B"]**2%p for k in states}
    signals["A2"]={k:states[k]["A"]**2%p for k in states}
    signals["A_plus_B"]={k:(states[k]["A"]+states[k]["B"])%p for k in states}
    signals["A_minus_B"]={k:(states[k]["A"]-states[k]["B"])%p for k in states}

    for mname,m in candidate_multipliers(n,lam):
        for X in ("A","B","N"):
            vals={k:states[k][X] for k in states}
            transfer={}
            cocycle={}
            for k in states:
                mk=m*k%n
                if mk==0 or vals[k]==0 or vals[mk]==0:continue
                transfer[k]=vals[mk]*pow(vals[k],-1,p)%p
                cocycle[k]=multiplier_cocycle(vals,m,k,n,p)
            signals[f"tr_{X}_{mname}"]=transfer
            signals[f"co_{X}_{mname}"]=cocycle
        for prefix in ("tr","co"):
            a=signals[f"{prefix}_A_{mname}"]; b=signals[f"{prefix}_B_{mname}"]
            domain=set(a)&set(b)
            signals[f"{prefix}_ABprod_{mname}"]={k:a[k]*b[k]%p for k in domain}
            signals[f"{prefix}_AoverB_{mname}"]={k:a[k]*pow(b[k],-1,p)%p for k in domain if b[k]}

    shifts=[("1",1),("2",2),("3",3),("5",5),("lambda",lam),("lambda2",lam*lam%n)]
    for rname,r in shifts:
        r%=n
        for X in ("A","B","N"):
            vals={k:states[k][X] for k in states}
            if vals.get(r,0)==0:continue
            tr={}; co={}
            for k in states:
                kr=(k+r)%n
                if kr==0 or vals[k]==0 or vals[kr]==0:continue
                tr[k]=vals[kr]*pow(vals[k],-1,p)%p
                co[k]=vals[kr]*pow(vals[k]*vals[r]%p,-1,p)%p
            signals[f"shifttr_{X}_{rname}"]=tr
            signals[f"shiftco_{X}_{rname}"]=co
    return signals


def generated_subgroup(n:int, generators:list[int])->set[int]:
    subgroup={1}
    frontier=[1]
    gens=[g%n for g in generators]
    while frontier:
        x=frontier.pop()
        for g in gens:
            y=x*g%n
            if y not in subgroup:
                subgroup.add(y); frontier.append(y)
    return subgroup


def analyze_curve(row,label):
    E,p,n,G,beta,lam,states=curve_context(row)
    transfer_checks=addition_checks=cov_checks=0
    tangent_addition_checks=charged_module_checks=0
    exceptions=0
    for k,s in states.items():
        P=s["P"]
        sn=states[n-k]
        if sn["A"] != -s["A"]%p or sn["B"] != -s["B"]%p:
            raise AssertionError("negation charge")
        if any(sn[x]!=s[x] for x in ("N","T","R","S")):
            raise AssertionError("neutral negation")
        sf=states[lam*k%n]
        if sf["A"]!=beta*beta%p*s["A"]%p or sf["B"]!=beta*s["B"]%p:
            raise AssertionError("GLV charge")
        if any(sf[x]!=s[x] for x in ("N","T","R","S")):
            raise AssertionError("GLV neutral")
        cov_checks += 1

        if s["B"] != B_direct(G, P, p):
            raise AssertionError("B is not the public endpoint coordinate ratio")
        if s["B"] == 0 or s["A"] != s["N"] * pow(s["B"], -1, p) % p:
            raise AssertionError("charged module factorization A=N/B failed")
        charged_module_checks += 1

        k2=2*k%n
        s2=states[k2]
        for tangent_name, da, db in (("a",1,0),("b",0,1)):
            tangent=(s["u"+tangent_name], s["v"+tangent_name])
            point2,tangent2=tangent_add(E,P,P,tangent,tangent,da,db)
            if point2 != s2["P"] or tangent2 != (s2["u"+tangent_name],s2["v"+tangent_name]):
                raise AssertionError("differentiated doubling law")
            tangent_addition_checks += 1

        D=(s["T"]*s["T"]+140*s["T"]-392)%p
        if 0 in ((s["T"]+7)%p,D,s["R"]%p):
            exceptions += 1
        else:
            if s2["T"]!=t_double(s["T"],p):raise AssertionError("T2")
            if s2["R"]!=r_double(s["T"],s["R"],p):raise AssertionError("R2")
            if s2["B"]!=s["B"]*b_transfer_double(s["T"],p)%p:raise AssertionError("B2")
            if s2["A"]!=s["A"]*a_transfer_double(s["T"],s["R"],p)%p:raise AssertionError("A2")
            transfer_checks += 1

        kp=(k+1)%n
        if kp and all(states[j]["x"] and states[j]["y"] for j in (k,1,kp)):
            for tangent_name, da, db in (("a",1,0),("b",0,1)):
                point_sum,tangent_sum=tangent_add(
                    E,P,G,
                    (s["u"+tangent_name],s["v"+tangent_name]),
                    (states[1]["u"+tangent_name],states[1]["v"+tangent_name]),
                    da,db,
                )
                if point_sum != states[kp]["P"] or tangent_sum != (states[kp]["u"+tangent_name],states[kp]["v"+tangent_name]):
                    raise AssertionError("differentiated addition law")
                tangent_addition_checks += 1
            cb=addition_cocycle_B(E,G,P,G)
            if states[kp]["B"] != cb*states[k]["B"]%p:
                raise AssertionError("B addition")
            for X in ("A","N"):
                if states[k][X] and states[1][X]:
                    cx=states[kp][X]*pow(states[k][X]*states[1][X]%p,-1,p)%p
                    if states[kp][X] != cx*states[k][X]*states[1][X]%p:
                        raise AssertionError("cochain addition")
            addition_checks += 1

    signals=signal_table(E,p,n,G,beta,lam,states)
    parity={k:(-1 if k&1 else 1) for k in states}
    char_single=[]; raw_separators=[]; bit_single=[]
    for name,vals in signals.items():
        domain=sorted(set(vals)&set(parity))
        if len(domain)!=n-1:continue
        raw_seen={}; mixed=False
        for k in domain:
            v=vals[k]
            bit=k&1
            if v in raw_seen and raw_seen[v]!=bit:mixed=True
            raw_seen[v]=bit
        if not mixed: raw_separators.append(name)
        signs=[chi(vals[k],p) for k in domain]
        targets=[parity[k] for k in domain]
        if 0 not in signs:
            if all(s==t for s,t in zip(signs,targets)) or all(s==-t for s,t in zip(signs,targets)):
                char_single.append(name)
        for mode in ("lsb","half","quartile"):
            bits=[]
            for k in domain:
                v=vals[k]%p
                b=(v&1) if mode=="lsb" else (1 if v>(p-1)//2 else 0) if mode=="half" else ((4*v)//p)&1
                bits.append(b)
            target_bits=[k&1 for k in domain]
            if bits==target_bits or [1-b for b in bits]==target_bits:
                bit_single.append((name,mode))

    orbit={}
    r=(n-1)//2
    for X in ("A","B"):
        even=[states[k][X] for k in range(2,n,2)]
        odd=[states[k][X] for k in range(1,n,2)]
        relation=sorted(odd)==sorted((-v)%p for v in even)
        sq_even=[v*v%p for v in even]
        pe=poly_from_roots(even,p)
        po=poly_from_roots(odd,p)
        predicted=[((-1)**r * ((-1)**i) * pe[i])%p for i in range(len(pe))]
        if po != predicted:
            raise AssertionError("odd/even orbit polynomial relation")
        bm=berlekamp_massey(pe,p)
        orbit[X]={
            "degree_each":r,
            "odd_is_negative_even_multiset":relation,
            "odd_polynomial_equals_signed_even_at_minus_X":True,
            "distinct_even_values":len(set(even)),
            "distinct_squared_pair_values":len(set(sq_even)),
            "pair_square_collisions":r-len(set(sq_even)),
            "even_factor_nonzero_coefficients":sum(1 for c in pe if c),
            "even_factor_zero_coefficients":sum(1 for c in pe if not c),
            "even_factor_dense":all(c!=0 for c in pe),
            "coefficient_BM_complexity":bm,
            "coefficient_window_length":len(pe),
        }

    subgroup=generated_subgroup(n,[2,lam,n-1])
    multiplier_cycles=(n-1)//len(subgroup)
    return {
        "label":label,"p":p,"n":n,"beta":beta,"lambda":lam,
        "rows":n-1,"transfer_checks":transfer_checks,"addition_checks":addition_checks,
        "tangent_addition_checks":tangent_addition_checks,
        "charged_module_checks":charged_module_checks,
        "covariance_checks":cov_checks,"exceptions":exceptions,
        "multiplier_transfer_group":{
            "generated_by":"2, lambda, -1",
            "subgroup_size":len(subgroup),
            "pair_cycle_count":multiplier_cycles,
            "independent_cycle_signs_after_anchor":max(0,multiplier_cycles-1),
            "lambda_in_doubling_subgroup":lam in generated_subgroup(n,[2]),
        },
        "signals":signals,"parity":parity,
        "single_character_survivors":char_single,
        "raw_state_separators":raw_separators,
        "representation_bit_survivors":bit_single,
        "orbit":orbit,
        "states":states,
    }
