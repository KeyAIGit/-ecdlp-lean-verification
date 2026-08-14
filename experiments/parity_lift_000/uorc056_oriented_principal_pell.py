#!/usr/bin/env python3
"""Exact frozen replay for UORC056 B7A."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from uorc056_oriented_principal_pell_core import FROZEN_CASES, SECP_N, SECP_P
from uorc056_oriented_principal_pell_factor import build_principal_factor

def lower_width_from_inequality(half: int) -> int:
    candidate = max(0, math.isqrt(2 * half + 1) - 1)
    while candidate * (candidate + 2) < 2 * half:
        candidate += 1
    while candidate > 0 and (candidate - 1) * (candidate + 1) >= 2 * half:
        candidate -= 1
    return candidate


def secp256k1_certificate() -> dict[str, object]:
    order = SECP_N
    half = (order - 1) // 2
    pole_order = half + 1
    sum_scalar = (-pow(4, -1, order)) % order
    anchor_scalar = (-sum_scalar) % order
    if order % 4 == 1:
        closed_sum = (order - 1) // 4
        if sum_scalar != closed_sum:
            raise AssertionError("secp256k1 quarter-scalar formula failed")
    lower_width = lower_width_from_inequality(half)
    baby = math.isqrt((half + 1) // 2)
    if baby == 0:
        baby = 1
    while 2 * baby * baby < half:
        baby += 1
    giant = (half + 2 * baby - 1) // (2 * baby)
    width_witness = baby + giant
    return {
        "p": SECP_P,
        "n": order,
        "n_mod_8": order % 8,
        "p_mod_4": SECP_P % 4,
        "half_size": half,
        "principal_pole_order": pole_order,
        "sum_scalar": sum_scalar,
        "sum_scalar_formula": "(n-1)/4",
        "anchor_scalar": anchor_scalar,
        "anchor_is_already_even": anchor_scalar % 2 == 0,
        "selector_exception_scalars": (
            [] if anchor_scalar % 2 == 0 else [sum_scalar, anchor_scalar]
        ),
        "degree_bound_a": pole_order // 2,
        "degree_bound_b": (pole_order - 3) // 2,
        "norm_equation": (
            "A_G(X)^2-(X^3+7)B_G(X)^2="
            "c_G*K_H(X)*(X-x(S_G))"
        ),
        "norm_constant_character": -1,
        "norm_constant_character_reason": (
            "n=1 mod 4 gives odd pole order; p=3 mod 4 makes "
            "the leading norm constant -lc(B_G)^2 a nonsquare"
        ),
        "binary_generalized_miller_leaves": pole_order,
        "binary_generalized_miller_merges": pole_order - 1,
        "one_level_index_width_lower_bound": lower_width,
        "one_level_index_width_lower_bound_bits": lower_width.bit_length(),
        "one_level_index_width_witness": {
            "baby": baby,
            "giant": giant,
            "leftover": 0,
            "width": width_witness,
            "covers_at_least_half": 2 * baby * giant >= half,
        },
        "central_target": "UNIFORM-ORIENTED-ROOT-CIRCUIT-056",
        "compact_sub_sqrt_evaluator_found": False,
        "parity_oracle_found": False,
        "sub_sqrt_ecdlp_found": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    cases = [build_principal_factor(*case) for case in FROZEN_CASES]
    aggregate = {
        "cases": len(cases),
        "point_ratio_checks": sum(case["ratio_checks"] for case in cases),
        "exceptional_point_checks": sum(
            case["exceptional_point_checks"] for case in cases
        ),
        "total_selector_checks": sum(
            case["total_selector_checks"] for case in cases
        ),
        "all_support_sum_identities_exact": all(
            case["support_sum_identity_exact"] for case in cases
        ),
        "all_principal_divisors_exact": all(
            case["principal_divisor_exact"] for case in cases
        ),
        "all_pell_identities_exact": all(
            case["pell_identity_exact"] for case in cases
        ),
        "all_zero_sets_exact": all(case["zero_set_exact"] for case in cases),
        "all_selector_exceptions_public": all(
            case["selector_exceptions_are_public"] for case in cases
        ),
        "all_negation_covariance_exact": all(
            case["generator_negation_is_quadratic_conjugation"]
            for case in cases
        ),
        "all_one_level_width_checks_exact": all(
            case["one_level_width_inequality_exact"] for case in cases
        ),
        "max_pole_order": max(case["pole_order"] for case in cases),
    }
    payload = {
        "package": "UORC056-ORIENTED-PRINCIPAL-PELL-B7A",
        "cases": cases,
        "aggregate": aggregate,
        "secp256k1": secp256k1_certificate(),
        "decision": (
            "The parity half admits an exact generator-oriented principal "
            "factor and a polynomial-Pell norm equation. A generalized Miller "
            "tree evaluates the declared divisor exactly but has linear leaves; "
            "every explicit one-level plus/minus index system has charged width "
            "Omega(sqrt(n)). No strict sub-square-root evaluator is obtained."
        ),
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(aggregate, indent=2))
    print(json.dumps(payload["secp256k1"], indent=2))


if __name__ == "__main__":
    main()
