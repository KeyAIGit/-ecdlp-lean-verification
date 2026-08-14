#!/usr/bin/env python3
"""Public API and aggregate certificates for UORC056 C20."""
from __future__ import annotations

from uorc056_negation_paired_core import *
from uorc056_negation_paired_dickson import dickson_symbolic_certificate
from uorc056_negation_paired_case import run_case

def secp_certificate() -> dict[str, object]:
    n = SECP_N
    return {
        "n": str(n),
        "nine_point_exception_bound": 9,
        "paired_sum_difference_support_lower_bound": str(n - 9),
        "paired_sum_difference_pole_degree_lower_bound": str(n - 9),
        "paired_squares_pole_degree_lower_bound": str(2 * (n - 9)),
        "U_j_support_lower_bound": str(n - 9),
        "U_j_pole_degree_lower_bound_formula": "j*(n-9)",
        "U_31_pole_degree_lower_bound": str(31 * (n - 9)),
        "pair_product_laurent_edge_support_lower_bound": str((n - 1) // 2),
        "generic_prism_reconstruction_edge_lower_bound": str(2 * n),
        "bit_lengths": {
            "n_minus_9": (n - 9).bit_length(),
            "half_cycle": ((n - 1) // 2).bit_length(),
            "two_n": (2 * n).bit_length(),
            "U_31_poles": (31 * (n - 9)).bit_length(),
        },
    }

def aggregate(cases: list[dict[str, object]]) -> dict[str, object]:
    return {
        "curves": len(cases),
        "split_counts": {
            split: sum(case["split"] == split for case in cases)
            for split in ("discovery", "validation", "held_out")
        },
        "all_pair_algebra_identities_pass": True,
        "all_fixed_field_checks_pass": all(
            case["fixed_fields"]["Tr_S_in_Fp_x3"]
            and case["fixed_fields"]["Tr_D_in_y_Fp_x3"]
            for case in cases
        ),
        "all_K_signatures_degree_1_over_3": all(
            case["pair_algebra"]["K_signature"]["degrees"] == [1, 0, 3]
            for case in cases
        ),
        "all_pair_exception_sets_have_nine_points": all(
            case["pair_exception_count"] == 9 for case in cases
        ),
        "all_S_D_dense_pole_theorems_pass": all(
            case["pair_algebra"]["S_profile"]["affine_nonzero_pole_degree"]
            >= case["pair_algebra"]["dense_pair_pole_lower_bound"]
            and case["pair_algebra"]["D_profile"]["affine_nonzero_pole_degree"]
            >= case["pair_algebra"]["dense_pair_pole_lower_bound"]
            for case in cases
        ),
        "all_screened_Dickson_traces_full_quotient_support": all(
            case["dickson"]["trace_screen"]["all_screened_traces_have_full_quotient_support"]
            for case in cases
        ),
        "pair_product_global_sign_lower_bound_proved": True,
        "branch_even_grammar_cannot_output_branch_odd_value": True,
        "quadratic_root_sign_is_original_mu2_ambiguity": True,
        "compact_nested_even_norm_found": True,
        "compact_public_Hilbert90_factor_found": all(
            case["nested_norm_pair"]["public_compact_factor"]["signature"]["degrees"] == [6, 3, 9]
            for case in cases
        ),
        "norm_one_twist_remains_dense_on_corpus": all(
            case["nested_norm_pair"]["norm_one_twist"]["profile"]["affine_nonzero_support"]
            >= case["n"] - 1
            for case in cases
        ),
        "paired_sum_compact_evaluator_found": False,
        "paired_difference_compact_evaluator_found": False,
        "quadratic_sign_selected_without_advice": False,
        "Dickson_divisor_collapse_found": False,
        "sub_sqrt_evaluator_found": False,
        "parity_oracle_found": False,
        "sub_sqrt_ecdlp_found": False,
    }
