#!/usr/bin/env python3
"""Product-graph and nested-norm certificates for UORC056 C20."""
from __future__ import annotations

from uorc056_negation_paired_core import *

def graph_certificate(n: int) -> dict[str, object]:
    if n % 2 == 0:
        raise ValueError("the endpoint cycle order must be odd")
    m = (n - 1) // 2
    odd_edges = list(range(1, n, 2))
    if len(odd_edges) != m:
        raise AssertionError("odd-edge reconstruction support mismatch")
    covered = []
    for j in odd_edges:
        covered.extend((j, (j + 1) % n))
    if sorted(covered) != list(range(1, n)):
        raise AssertionError("tight Laurent reconstruction certificate failed")
    return {
        "graph": "odd prism C_n square K_2",
        "vertices": 2 * n,
        "edges": 3 * n,
        "connected_components": 1,
        "cycle_rank": n + 1,
        "bipartite": False,
        "shortest_odd_cycle_length": n,
        "minimum_edges_for_generic_finite_reconstruction_up_to_sign": 2 * n,
        "generic_solution_fibre": "{(u,v),(-u,-v)}",
        "all_edge_products_global_sign_invariant": True,
        "telescoping_constraints": ["product_k u_k=1", "product_k v_k=1"],
        "tight_laurent_edge_support_for_u0": m,
        "tight_witness": "u_0=(product_{j odd} A^+_j)^(-1)",
        "matching_K_edges_improve_laurent_support": False,
        "lower_bound_scope": "Laurent monomials in prism edge products, modulo both telescoping products",
    }

def compact_norm_pair(C, Z, K, points, compact_even_norm=None) -> dict[str, object]:
    n = len(points)
    cubic_norm = norm3(C, Z)
    cubic_norm_neg = rf_neg(C, cubic_norm)
    compact_even_norm = compact_even_norm if compact_even_norm is not None else norm3(C, K)
    if not rf_eq(C, C.rf_mul(cubic_norm, cubic_norm_neg), compact_even_norm):
        raise AssertionError("nested GLV/negation norm identity failed")

    if n % 4 == 3:
        r = (n + 1) // 4
        class_index = r * (2 * r - 1) % n
    else:
        r = (n - 1) // 4
        class_index = r * (2 * r + 1) % n
    m = (n - 1) // 2
    factor_indices = [(class_index - 1) % n, 1, class_index, m]
    factor_y = [points[index][1] for index in factor_indices]

    def y_minus(value: int):
        return ([(-value) % C.p], [1], [1])

    compact_factor = C.rf_div(
        y_minus(factor_y[0]),
        C.rf_mul(
            C.rf_mul(y_minus(factor_y[1]), y_minus(factor_y[2])),
            y_minus(factor_y[3]),
        ),
    )
    if not rf_eq(C, C.rf_mul(compact_factor, rf_neg(C, compact_factor)), compact_even_norm):
        raise AssertionError("public compact Hilbert-90 factor has wrong norm")
    norm_one_twist = C.rf_div(cubic_norm, compact_factor)
    if not rf_eq(C, C.rf_mul(norm_one_twist, rf_neg(C, norm_one_twist)), c19.rf_one(C)):
        raise AssertionError("norm-one twist identity failed")

    norm_sum = C.rf_add(cubic_norm, cubic_norm_neg)
    norm_difference = C.rf_add(cubic_norm, C.rf_scale(cubic_norm_neg, -1))
    return {
        "identity": "N_phi(Z)(P)*N_phi(Z)(-P)=N_phi(K)(P)",
        "cubic_norm_signature": c19.rf_signature(cubic_norm),
        "compact_even_norm_signature": c19.rf_signature(compact_even_norm),
        "paired_norm_sum_signature": c19.rf_signature(norm_sum),
        "paired_norm_difference_signature": c19.rf_signature(norm_difference),
        "cubic_norm_profile": support_profile(C, cubic_norm, points),
        "compact_even_norm_profile": support_profile(C, compact_even_norm, points),
        "paired_norm_sum_profile": support_profile(C, norm_sum, points),
        "paired_norm_difference_profile": support_profile(C, norm_difference, points),
        "public_compact_factor": {
            "formula": "(y-y([a-1]G))/((y-y(G))(y-y([a]G))(y-y([m]G)))",
            "indices": factor_indices,
            "y_values": factor_y,
            "signature": c19.rf_signature(compact_factor),
            "profile": support_profile(C, compact_factor, points),
            "norm_identity": "C0(P)*C0(-P)=N_phi(K)(P)",
        },
        "norm_one_twist": {
            "definition": "R=N_phi(Z)/C0",
            "identity": "R(P)*R(-P)=1",
            "signature": c19.rf_signature(norm_one_twist),
            "profile": support_profile(C, norm_one_twist, points),
            "branch_parity": "odd",
        },
        "interpretation": "compact quadratic norm plus a dense norm-one Hilbert-90 twist",
    }
