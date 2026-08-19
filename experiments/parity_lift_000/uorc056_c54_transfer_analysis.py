from __future__ import annotations

import hashlib
import json

from uorc056_c54_curve_analysis import *


def uniform_character_span(curves):
    common=set(curves[0]["signals"])
    for c in curves[1:]:common &= set(c["signals"])
    names=sorted(common)
    target_vec=0; offset=0
    curve_offsets=[]
    for c in curves:
        n=c["n"]
        curve_offsets.append(offset)
        for k in range(1,n):
            if ((-1 if k&1 else 1) != (-1)):
                target_vec |= 1<<(offset+k-1)
        offset += n-1
    basis=XorBasis(); valid=[]; exact=[]
    for name in names:
        vec=0; ok=True; pos=0
        for c in curves:
            vals=c["signals"][name]; n=c["n"]; p=c["p"]
            if len(vals)!=n-1:ok=False;break
            signs=[chi(vals[k],p) for k in range(1,n)]
            if 0 in signs:ok=False;break
            base=signs[0]
            for i,s in enumerate(signs):
                if s!=base:vec |= 1<<(pos+i)
            pos += n-1
        if ok:
            valid.append(name); basis.add(vec)
            if vec==target_vec:exact.append(name)
    return {
        "declared":len(names),"valid":len(valid),"rank":basis.rank,
        "target_in_span":basis.contains(target_vec),"exact_single":exact,
        "valid_names":valid,
    }


def structural_pair_screen_p43(curve):
    p=curve["p"]; n=curve["n"]
    if p!=43:return None
    preferred=[
        "B","A","co_B_2","co_A_2","tr_B_2","tr_A_2",
        "shiftco_B_1","shiftco_A_1","shifttr_B_1","shifttr_A_1",
        "co_B_3","co_A_3","co_B_5","co_A_5",
    ]
    preferred=[x for x in preferred if x in curve["signals"] and len(curve["signals"][x])==n-1]
    target=[-1 if k&1 else 1 for k in range(1,n)]
    survivors=[]; declared=valid=0
    for i,name1 in enumerate(preferred):
        X=curve["signals"][name1]
        for name2 in preferred[i:]:
            Y=curve["signals"][name2]
            for a in range(p):
                for b in range(p):
                    for c in range(p):
                        if a==b==c==0:continue
                        first=a or b or c
                        if first!=1:continue
                        declared += 1
                        signs=[];ok=True
                        for k in range(1,n):
                            z=(a*X[k]+b*Y[k]+c)%p
                            s=chi(z,p)
                            if s==0:ok=False;break
                            signs.append(s)
                        if not ok:continue
                        valid += 1
                        if all(s==t for s,t in zip(signs,target)) or all(s==-t for s,t in zip(signs,target)):
                            survivors.append((name1,name2,a,b,c))
                            if len(survivors)>=20:return {"states":preferred,"declared":declared,"valid":valid,"survivors":survivors}
    return {"states":preferred,"declared":declared,"valid":valid,"survivors":survivors}


def power_affine_screen_p43(curve):
    p=curve["p"]; n=curve["n"]
    if p!=43:return None
    target_sign=[-1 if k&1 else 1 for k in range(1,n)]
    target_bits=[k&1 for k in range(1,n)]
    declared=valid=0
    character_survivors=[]
    representation_survivors=[]
    for name in ("A","B","N"):
        vals=curve["signals"][name]
        for exponent in range(p-1):
            powers=[pow(vals[k],exponent,p) for k in range(1,n)]
            for shift in range(p):
                declared += 1
                signs=[chi((value+shift)%p,p) for value in powers]
                if 0 in signs:continue
                valid += 1
                if signs==target_sign or signs==[-value for value in target_sign]:
                    character_survivors.append((name,exponent,shift))
            for mode in ("lsb","half","quartile","octant"):
                bits=[]
                for value in powers:
                    if mode=="lsb":bit=value&1
                    elif mode=="half":bit=1 if value>(p-1)//2 else 0
                    elif mode=="quartile":bit=((4*value)//p)&1
                    else:bit=((8*value)//p)&1
                    bits.append(bit)
                if bits==target_bits or [1-bit for bit in bits]==target_bits:
                    representation_survivors.append((name,exponent,mode))
    return {
        "states":["A","B","N"],
        "exponents_per_state":p-1,
        "affine_character_atoms":declared,
        "valid_affine_character_atoms":valid,
        "character_survivors":character_survivors,
        "representation_bit_atoms":3*(p-1)*4,
        "representation_bit_survivors":representation_survivors,
    }


def secp_cycle_certificate():
    factors=(3,149,631,107361793816595537,174723607534414371449,341948486974166000522343609283189)
    if pow(2,SECP_ORD2,SECP_N)!=1:raise AssertionError
    minimal={str(q):pow(2,SECP_ORD2//q,SECP_N)!=1 for q in factors}
    if not all(minimal.values()):raise AssertionError
    lam2=pow(SECP_LAMBDA,2,SECP_N)
    witness=pow(2,SECP_ORD2//3,SECP_N)
    if witness!=lam2:raise AssertionError("lambda not in doubling subgroup certificate")
    return {
        "n":SECP_N,"ord_n_2":SECP_ORD2,"ord_n_2_bits":SECP_ORD2.bit_length(),
        "order_is_odd":SECP_ORD2%2==1,"minus_one_in_doubling_subgroup":False,
        "full_scalar_orbits":(SECP_N-1)//SECP_ORD2,
        "pair_quotient_cycles":(SECP_N-1)//(2*SECP_ORD2),
        "lambda_in_doubling_subgroup":True,
        "two_to_ord_over_3_equals_lambda_squared":witness==lam2,
        "minimality_checks":minimal,
        "independent_pair_cycle_signs_after_one_anchor":(SECP_N-1)//(2*SECP_ORD2)-1,
    }


def secp_state_certificate():
    E=Curve(SECP_P)
    if E.mul(SECP_N,SECP_G) is not None:
        raise AssertionError("secp generator order")
    if E.mul(SECP_LAMBDA,SECP_G,SECP_N)!=(SECP_BETA*SECP_G[0]%SECP_P,SECP_G[1]):
        raise AssertionError("secp GLV constants")
    samples=(
        1,2,3,5,7,8,17,31,127,255,
        (SECP_N-1)//2,(SECP_N+1)//2,SECP_N-2,SECP_N-1,
    )
    module_checks=doubling_checks=glv_checks=negation_checks=0
    for k in samples:
        P=E.mul(k,SECP_G,SECP_N)
        current=state(E,SECP_N,SECP_G,P)
        if current["B"]!=B_direct(SECP_G,P,SECP_P):
            raise AssertionError("secp B endpoint ratio")
        if current["A"]!=current["N"]*pow(current["B"],-1,SECP_P)%SECP_P:
            raise AssertionError("secp A=N/B")
        module_checks += 1
        doubled=state(E,SECP_N,SECP_G,E.mul(2*k,SECP_G,SECP_N))
        T,R=current["T"],current["R"]
        D=(T*T+140*T-392)%SECP_P
        if 0 in ((T+7)%SECP_P,D,R):
            raise AssertionError("unexpected secp doubling exceptional sample")
        if doubled["T"]!=t_double(T,SECP_P):raise AssertionError("secp T2")
        if doubled["R"]!=r_double(T,R,SECP_P):raise AssertionError("secp R2")
        if doubled["B"]!=current["B"]*b_transfer_double(T,SECP_P)%SECP_P:
            raise AssertionError("secp B2")
        if doubled["A"]!=current["A"]*a_transfer_double(T,R,SECP_P)%SECP_P:
            raise AssertionError("secp A2")
        doubling_checks += 1
        rotated=state(E,SECP_N,SECP_G,E.mul(SECP_LAMBDA*k,SECP_G,SECP_N))
        if rotated["A"]!=SECP_BETA*SECP_BETA%SECP_P*current["A"]%SECP_P:
            raise AssertionError("secp GLV A")
        if rotated["B"]!=SECP_BETA*current["B"]%SECP_P:
            raise AssertionError("secp GLV B")
        if any(rotated[name]!=current[name] for name in ("N","T","R","S")):
            raise AssertionError("secp GLV neutral")
        glv_checks += 1
        negated=state(E,SECP_N,SECP_G,E.neg(P))
        if negated["A"]!=-current["A"]%SECP_P or negated["B"]!=-current["B"]%SECP_P:
            raise AssertionError("secp negation charge")
        if any(negated[name]!=current[name] for name in ("N","T","R","S")):
            raise AssertionError("secp negation neutral")
        negation_checks += 1
    return {
        "public_samples":len(samples),
        "charged_module_checks":module_checks,
        "doubling_transfer_checks":doubling_checks,
        "GLV_covariance_checks":glv_checks,
        "negation_covariance_checks":negation_checks,
    }


def build_payload():
    curves=[]
    for i,row in enumerate(ALL):
        label=(f"frozen-{i+1}" if i<4 else f"heldout-c52-{i-3}" if i<12 else f"heldout-c54-{i-11}")
        curves.append(analyze_curve(row,label))
    uniform=uniform_character_span(curves)
    complete=structural_pair_screen_p43(curves[0])
    power_screen=power_affine_screen_p43(curves[0])
    secp=secp_cycle_certificate()
    secp_states=secp_state_certificate()
    aggregate={
        "curves":len(curves),"frozen":4,"c52_heldout":8,"new_c54_heldout":4,
        "rows":sum(c["rows"] for c in curves),
        "doubling_transfer_checks":sum(c["transfer_checks"] for c in curves),
        "addition_transfer_checks":sum(c["addition_checks"] for c in curves),
        "tangent_addition_checks":sum(c["tangent_addition_checks"] for c in curves),
        "charged_module_checks":sum(c["charged_module_checks"] for c in curves),
        "covariance_checks":sum(c["covariance_checks"] for c in curves),
        "secp_public_samples":secp_states["public_samples"],
        "secp_doubling_transfer_checks":secp_states["doubling_transfer_checks"],
        "secp_GLV_covariance_checks":secp_states["GLV_covariance_checks"],
        "uniform_declared_character_atoms":uniform["declared"],
        "uniform_valid_character_atoms":uniform["valid"],
        "uniform_character_span_rank":uniform["rank"],
        "uniform_target_in_span":uniform["target_in_span"],
        "complete_p43_affine_atoms":complete["declared"],
        "complete_p43_valid_affine_atoms":complete["valid"],
        "complete_p43_survivors":len(complete["survivors"]),
        "p43_power_affine_atoms":power_screen["affine_character_atoms"],
        "p43_power_affine_survivors":len(power_screen["character_survivors"]),
        "p43_power_representation_survivors":len(power_screen["representation_bit_survivors"]),
        "all_orbit_sign_relations":all(c["orbit"][X]["odd_is_negative_even_multiset"] for c in curves for X in ("A","B")),
        "max_even_factor_zero_coefficients":max(c["orbit"][X]["even_factor_zero_coefficients"] for c in curves for X in ("A","B")),
        "all_factor_BM_complexities_generic_half_window":all(
            c["orbit"][X]["coefficient_BM_complexity"] == (c["orbit"][X]["coefficient_window_length"]+1)//2
            for c in curves for X in ("A","B")
        ),
        "max_multiplier_pair_cycles":max(c["multiplier_transfer_group"]["pair_cycle_count"] for c in curves),
        "errors":0,
    }
    public_curves=[]
    for c in curves:
        public_curves.append({k:v for k,v in c.items() if k not in ("signals","parity","states")})
    payload={
        "profile_id":"UORC-056-CHARGED-MODULI-TANGENT-TRANSFER-C54",
        "schema_version":"1.0",
        "exact_transfer_laws":{
            "differentiated_addition":(
                "for slope m, dm=((dv2-dv1)(x2-x1)-(y2-y1)(du2-du1))/(x2-x1)^2; "
                "du3=2m*dm-du1-du2 and dv3=dm(x1-x3)+m(du1-du3)-dv1"
            ),
            "charged_module":"A=N/B; every charged Laurent-rational expression in A,B is B times a neutral expression in N and B^2",
            "B_addition":"B(P+Q)=C_B(P,Q)B(P)B(Q), C_B=e(G)e(P+Q)/(e(P)e(Q)), e=x/y",
            "N_addition":"N(P+Q)=C_N(P,Q)N(P)N(Q)",
            "A_addition":"C_A=C_N/C_B",
            "T_double":"T2=T(T-56)^3/(64(T+7)^3)",
            "R_double":"R2=(T-56)(R(T^2+140T-392)-3T^2+42T)/(16(T+7)^3)",
            "B_double":"B(2P)=B(P)*2(T-56)(T+7)/(T^2+140T-392)",
            "A_double":"A(2P)=A(P)*2(R(T^2+140T-392)-3T^2+42T)/(R(T^2+140T-392))",
            "GLV":"A(phi P)=beta^2 A(P), B(phi P)=beta B(P), N,T,R,S fixed",
        },
        "orbit_factor_boundary":{
            "relation":"P_odd(X)=(-1)^r P_even(-X), r=(n-1)/2",
            "full_factor":"P_even(X)P_odd(X) is a polynomial in X^2",
            "interpretation":"the public squared orbit does not choose one sign from each +/- pair",
            "secp_transfer_gauge":(
                "the multiplier graph generated by 2, lambda and -1 has 32 pair cycles; "
                "one anchor leaves 31 independent cycle signs before any open transport is supplied"
            ),
        },
        "secp256k1_cycle_certificate":secp,
        "secp256k1_state_certificate":secp_states,
        "uniform_character_screen":uniform,
        "complete_p43_pair_affine_screen":complete,
        "complete_p43_power_affine_screen":power_screen,
        "curves":public_curves,
        "aggregate":aggregate,
        "cost_ledger":{
            "state_builder":"O(log n) field operations at fixed jet order by division-polynomial automatic differentiation",
            "single_transfer_evaluation":"O(1) field operations once the public state and endpoint coordinates are present",
            "explicit_even_odd_factor_materialization":"Theta(n) coefficients or values and therefore rejected",
            "decoder_cost":"no accepted sub-square-root decoder found",
        },
        "claim_boundary":{
            "proved_or_replayed":[
                "exact differentiated addition and doubling laws",
                "rank-one charged-module factorization A=N/B",
                "GLV and negation covariance",
                "even/odd orbit polynomial sign relation",
                "secp256k1 32-cycle multiplier certificate",
                "closure of the declared character and p43 affine/power grammars",
            ],
            "not_claimed":[
                "an unrestricted nonlinear or arithmetic-circuit lower bound",
                "a parity oracle",
                "a sub-square-root ECDLP algorithm",
            ],
        },
        "decision":{
            "exact_differentiated_group_law_found":True,
            "exact_addition_transfer_found":True,
            "exact_doubling_transfer_found":True,
            "charged_state_module_rank_one_over_neutral_field":True,
            "moduli_tangent_adds_new_charge_generator":False,
            "secp_doubling_glv_pair_cycles":secp["pair_quotient_cycles"],
            "declared_transfer_character_grammar_closed":(
                not uniform["target_in_span"]
                and not complete["survivors"]
                and not power_screen["character_survivors"]
                and not power_screen["representation_bit_survivors"]
            ),
            "cheap_parity_decoder_found":False,
            "parity_oracle_found":False,
            "sub_sqrt_ecdlp_found":False,
        },
        "successor":{
            "id":"CYCLE-LABEL-OR-OPEN-TRANSLATION-C55",
            "target":"either construct a public label for the 32 secp doubling/GLV pair cycles or a compressed open-translation transport that avoids a scalar-labelled path",
        },
    }
    raw=json.dumps(payload,sort_keys=True,separators=(",",":"),default=str).encode()
    payload["digest"]=hashlib.sha256(raw).hexdigest()
    return payload


if __name__=="__main__":
    data=build_payload()
    print(json.dumps({"aggregate":data["aggregate"],"decision":data["decision"],"digest":data["digest"]},indent=2))
