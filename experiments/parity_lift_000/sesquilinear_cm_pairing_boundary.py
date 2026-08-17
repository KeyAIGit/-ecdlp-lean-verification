#!/usr/bin/env python3
"""Exact secp256k1 arithmetic for SESQUILINEAR-CM-PAIRING-011.

The script classifies the two natural sesquilinear pairing choices:

1. alpha = lambda - omega, whose kernel contains the rational subgroup H;
2. alpha = n, the central multiplication endomorphism.

No external point, key, wallet, or production DLP target is accepted.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

P = int("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F", 16)
N = int("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141", 16)
LAMBDA = int(
    "5363AD4CC05C30E0A5261C028812645A122E22EA20816678DF02967C1B23BD72",
    16,
)
EMBEDDING_DEGREE = (N - 1) // 6


def build_payload() -> dict[str, object]:
    if (LAMBDA * LAMBDA + LAMBDA + 1) % N:
        raise AssertionError("lambda is not an order-three subgroup eigenvalue")

    annihilator_norm = LAMBDA * LAMBDA + LAMBDA + 1
    if annihilator_norm % N:
        raise AssertionError("CM annihilator norm is not divisible by n")
    norm_cofactor = annihilator_norm // N

    conjugate_action = (LAMBDA - LAMBDA * LAMBDA) % N
    if conjugate_action != (2 * LAMBDA + 1) % N:
        raise AssertionError("conjugate action formula failed")
    conjugate_inverse = pow(conjugate_action, -1, N)
    if conjugate_action * conjugate_inverse % N != 1:
        raise AssertionError("conjugate action is not invertible")

    if math.gcd(N, P - 1) != 1:
        raise AssertionError("base-field n-th power map is not bijective")
    if pow(P, EMBEDDING_DEGREE, N) != 1:
        raise AssertionError("embedding degree certificate failed")

    return {
        "package": "SESQUILINEAR-CM-PAIRING-011",
        "scope": (
            "fixed secp256k1 constants and source-level pairing domains only; "
            "no external or production target"
        ),
        "constants": {
            "p": P,
            "n": N,
            "lambda": LAMBDA,
            "lambda_relation_mod_n": 0,
        },
        "order_dependent_annihilator": {
            "alpha": "lambda-omega",
            "norm": annihilator_norm,
            "norm_bits": annihilator_norm.bit_length(),
            "norm_over_n": norm_cofactor,
            "norm_over_n_bits": norm_cofactor.bit_length(),
            "action_on_H": 0,
            "conjugate_action_on_H": conjugate_action,
            "conjugate_action_inverse_mod_n": conjugate_inverse,
            "conjugate_kernel_intersection_H": "{O}",
            "tate_quotient_for_conjugate_alpha_on_H": "zero because the conjugate action is a unit",
        },
        "integer_alpha_n": {
            "weil_pairing_on_H_times_H": (
                "trivial: every classical Weil factor pairs dependent scalar multiples "
                "on one cyclic line"
            ),
            "base_field_tate_target": "trivial",
            "gcd_n_p_minus_1": math.gcd(N, P - 1),
            "reason": "x -> x^n is a bijection of F_p^*",
            "nondegenerate_field_requires_mu_n": True,
            "minimum_mu_n_extension_degree": EMBEDDING_DEGREE,
            "minimum_mu_n_extension_degree_log2": math.log2(EMBEDDING_DEGREE),
            "explicit_degree_minus_sqrt_n_bits": (
                math.log2(EMBEDDING_DEGREE) - math.log2(N) / 2
            ),
            "odd_order_output_has_binary_character": False,
        },
        "route_decision": {
            "W_hat_lambda_minus_omega": (
                "Q can occupy only the alpha-kernel input; no nonzero rational-line "
                "point occupies the conjugate-kernel input"
            ),
            "T_hat_lambda_minus_omega": (
                "same missing conjugate-kernel first input"
            ),
            "T_hat_conjugate_alpha": (
                "G is admissible in the first input, but every Q in H is zero in "
                "E/[conjugate_alpha]E"
            ),
            "W_hat_n": "identically trivial on H x H",
            "T_hat_n_over_F_p": "identically trivial in the base-field quotient",
            "T_hat_n_over_extension": (
                "potentially nondegenerate but requires the same enormous mu_n extension; "
                "evaluation gives an odd-order target character, not a binary carry"
            ),
        },
        "public_carry_decoder_found": False,
        "public_R3_decoder_found": False,
        "unconditional_sub_sqrt_algorithm_found": False,
        "claim_boundary": [
            "The fixed scalar and divisibility statements are exact.",
            "The pairing domain and nondegeneracy requirements are source-level inputs.",
            "This closes the natural sesquilinear Weil/Tate constructions on the rational line, not arbitrary pairings.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("sesquilinear_cm_pairing_results.json"),
    )
    args = parser.parse_args()
    payload = build_payload()
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
