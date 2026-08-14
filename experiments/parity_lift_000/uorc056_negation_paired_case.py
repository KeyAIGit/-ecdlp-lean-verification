#!/usr/bin/env python3
"""One-curve C20 exact replay."""
from __future__ import annotations

from uorc056_negation_paired_core import *
from uorc056_negation_paired_dickson import dickson_trace_screen
from uorc056_negation_paired_structures import graph_certificate, compact_norm_pair

def run_case(core: dict[str, object], split: str) -> dict[str, object]:
    p, n = int(core["p"]), int(core["n"])
    G = tuple(core["G"])
    beta, lam = int(core["beta"]), int(core["lambda"])
    points = c17.subgroup_points(p, n, G)
    if c17.ec_mul(lam, G, p) != c17.phi(G, beta, p):
        raise AssertionError("lambda covariance failed")
    C = c19.RFContext(p, beta)
    Z, _divisor, reciprocity = c19.build_z(C, points)
    Zneg = rf_neg(C, Z)
    K = C.rf_mul(Z, Zneg)
    compact_K = c19.build_compact_K(C, points, reciprocity["class_index"])
    if not rf_eq(C, K, compact_K):
        raise AssertionError("compact K identity failed")

    S = C.rf_add(Z, Zneg)
    D = C.rf_add(Z, C.rf_scale(Zneg, -1))
    S2 = C.rf_mul(S, S)
    D2 = C.rf_mul(D, D)
    four_K = C.rf_scale(K, 4)
    if not rf_eq(C, C.rf_add(D2, four_K), S2):
        raise AssertionError("S^2-D^2=4K failed")
    if not rf_eq(C, C.rf_div(K, Z), Zneg):
        raise AssertionError("Z(-P)=K/Z failed")

    endpoint = list(C.result.valuations)
    exceptions = pair_exception_indices(endpoint)
    expected_exceptions = sorted({
        0, 1, n - 1,
        reciprocity["class_index"], (-reciprocity["class_index"]) % n,
        (reciprocity["class_index"] - 1) % n,
        (1 - reciprocity["class_index"]) % n,
        (n - 1) // 2, (n + 1) // 2,
    })
    if exceptions != expected_exceptions:
        raise AssertionError("nine-point pair exception set mismatch")

    lower_bound = n - len(exceptions)
    for k in range(1, n):
        if k in exceptions:
            continue
        pair = sorted((endpoint[k], endpoint[-k % n]))
        if pair != [-1, 1]:
            raise AssertionError("nonexceptional negation pair is not zero/pole")

    S_profile = support_profile(C, S, points)
    D_profile = support_profile(C, D, points)
    S2_profile = support_profile(C, S2, points)
    D2_profile = support_profile(C, D2, points)
    if S_profile["affine_nonzero_pole_degree"] < lower_bound:
        raise AssertionError("paired sum lost a mandatory pole")
    if D_profile["affine_nonzero_pole_degree"] < lower_bound:
        raise AssertionError("paired difference lost a mandatory pole")
    if S2_profile["affine_nonzero_pole_degree"] < 2 * lower_bound:
        raise AssertionError("paired sum square lost mandatory double poles")
    if D2_profile["affine_nonzero_pole_degree"] < 2 * lower_bound:
        raise AssertionError("paired difference square lost mandatory double poles")

    trace_S = trace3(C, S)
    trace_D = trace3(C, D)
    if not rf_eq(C, C.rf_phi(trace_S), trace_S):
        raise AssertionError("Tr_phi(S) is not phi-invariant")
    if not rf_eq(C, C.rf_phi(trace_D), trace_D):
        raise AssertionError("Tr_phi(D) is not phi-invariant")
    if not rf_eq(C, rf_neg(C, trace_S), trace_S):
        raise AssertionError("Tr_phi(S) is not point-negation even")
    if not rf_eq(C, rf_neg(C, trace_D), C.rf_scale(trace_D, -1)):
        raise AssertionError("Tr_phi(D) is not point-negation odd")

    trace_S_signature = c19.rf_signature(trace_S)
    trace_D_signature = c19.rf_signature(trace_D)
    trace_S_norm = C.rf_norm(trace_S)
    trace_D_norm = C.rf_norm(trace_D)
    trace_S_A, trace_S_B, trace_S_C = trace_S_norm
    trace_D_A, trace_D_B, trace_D_C = trace_D_norm
    trace_S_in_x3 = (
        not any(trace_S_B)
        and all(i % 3 == 0 for i, coeff in enumerate(trace_S_A) if coeff)
        and all(i % 3 == 0 for i, coeff in enumerate(trace_S_C) if coeff)
    )
    trace_D_in_yx3 = (
        not any(trace_D_A)
        and all(i % 3 == 0 for i, coeff in enumerate(trace_D_B) if coeff)
        and all(i % 3 == 0 for i, coeff in enumerate(trace_D_C) if coeff)
    )
    if not trace_S_in_x3 or not trace_D_in_yx3:
        raise AssertionError("fixed-field exponent certificate failed")

    trace_screen = dickson_trace_screen(C, points, Z, Zneg, endpoint, lam)
    branch_even_leaves = {
        "K": K,
        "Tr_K": trace3(C, K),
        "Norm_K": norm3(C, K),
        "S2": S2,
        "D2": D2,
        "S2_over_K": C.rf_div(S2, K),
        "D2_over_K": C.rf_div(D2, K),
        "Tr_S2": trace3(C, S2),
        "Tr_D2": trace3(C, D2),
    }
    leaf_profiles = {
        name: {
            "signature": c19.rf_signature(value),
            "profile": support_profile(C, value, points),
            "branch_parity": "even",
        }
        for name, value in branch_even_leaves.items()
    }

    return {
        "p": p,
        "n": n,
        "G": list(G),
        "beta": beta,
        "lambda": lam,
        "split": split,
        "pair_exception_indices": exceptions,
        "pair_exception_count": len(exceptions),
        "pair_algebra": {
            "identities": ["S^2-D^2=4K", "Z(-P)=K/Z", "Z=(S+D)/2", "Z(-P)=(S-D)/2"],
            "K_signature": c19.rf_signature(K),
            "S_signature": c19.rf_signature(S),
            "D_signature": c19.rf_signature(D),
            "S_profile": S_profile,
            "D_profile": D_profile,
            "S2_profile": S2_profile,
            "D2_profile": D2_profile,
            "dense_pair_support_lower_bound": lower_bound,
            "dense_pair_pole_lower_bound": lower_bound,
            "dense_pair_square_pole_lower_bound": 2 * lower_bound,
        },
        "fixed_fields": {
            "Tr_S_signature": trace_S_signature,
            "Tr_D_signature": trace_D_signature,
            "Tr_S_profile": support_profile(C, trace_S, points),
            "Tr_D_profile": support_profile(C, trace_D, points),
            "Tr_S_phi_invariant": True,
            "Tr_D_phi_invariant": True,
            "Tr_S_point_negation_even": True,
            "Tr_D_point_negation_odd": True,
            "Tr_S_in_Fp_x3": trace_S_in_x3,
            "Tr_D_in_y_Fp_x3": trace_D_in_yx3,
            "Tr_S_nonzero_exponents": {
                "A": [i for i, coeff in enumerate(trace_S_A) if coeff],
                "B": [i for i, coeff in enumerate(trace_S_B) if coeff],
                "C": [i for i, coeff in enumerate(trace_S_C) if coeff],
            },
            "Tr_D_nonzero_exponents": {
                "A": [i for i, coeff in enumerate(trace_D_A) if coeff],
                "B": [i for i, coeff in enumerate(trace_D_B) if coeff],
                "C": [i for i, coeff in enumerate(trace_D_C) if coeff],
            },
        },
        "dickson": {
            "all_index_local_theorem": {
                "outside_pair_exceptions": "ord(U_j)=-j",
                "support_lower_bound": lower_bound,
                "pole_degree_lower_bound_formula": f"j*{lower_bound}",
            },
            "trace_screen": trace_screen,
        },
        "quadratic_extraction": {
            "equation": "X^2-SX+K=0",
            "discriminant": "D^2=S^2-4K",
            "branch_even_data": ["K", "S^2", "D^2"],
            "global_branch_action": "(S,D)->(-S,-D)",
            "root_swap_action": "D->-D swaps Z(P) and Z(-P)",
            "sign_selected_without_advice": False,
            "canonical_field_sqrt_is_not_an_orientation_proof": True,
        },
        "branch_even_grammar": {
            "leaves": leaf_profiles,
            "closure": "rational operations, trace, norm, deterministic tests preserve sigma-invariance",
            "branch_odd_output_possible": False,
        },
        "graph": graph_certificate(n),
        "nested_norm_pair": compact_norm_pair(C, Z, K, points, branch_even_leaves["Norm_K"]),
    }
