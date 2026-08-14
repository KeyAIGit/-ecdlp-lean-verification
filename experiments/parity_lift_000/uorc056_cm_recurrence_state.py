#!/usr/bin/env python3
"""Exact finite-field replay for UORC056 CM RECURRENCE STATE B7.

The script works only with frozen public prime orders. It constructs small
auxiliary fields containing the required roots of unity and evaluates no curve
point or unknown scalar.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
FROZEN_ORDERS = (7, 31, 61, 79, 67, 79, 127, 139, 199, 313)
PUBLIC_UNITS = (2, 3, 5, 7)


def is_prime(value: int) -> bool:
    if value < 2:
        return False
    if value % 2 == 0:
        return value == 2
    divisor = 3
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += 2
    return True


def prime_factors(value: int) -> list[int]:
    factors: list[int] = []
    divisor = 2
    remaining = value
    while divisor * divisor <= remaining:
        if remaining % divisor == 0:
            factors.append(divisor)
            while remaining % divisor == 0:
                remaining //= divisor
        divisor += 1 if divisor == 2 else 2
    if remaining > 1:
        factors.append(remaining)
    return factors


def auxiliary_prime(order: int) -> int:
    multiplier = 1
    while True:
        candidate = multiplier * order + 1
        if is_prime(candidate):
            return candidate
        multiplier += 1


def primitive_root(prime: int) -> int:
    factors = prime_factors(prime - 1)
    for candidate in range(2, prime):
        if all(
            pow(candidate, (prime - 1) // factor, prime) != 1
            for factor in factors
        ):
            return candidate
    raise AssertionError("primitive root not found")


def run_case(order: int) -> dict[str, object]:
    if not is_prime(order) or order % 2 == 0:
        raise AssertionError("frozen order must be an odd prime")
    field_prime = auxiliary_prime(order)
    generator = primitive_root(field_prime)
    omega = pow(generator, (field_prime - 1) // order, field_prime)
    if pow(omega, order, field_prime) != 1 or omega == 1:
        raise AssertionError("auxiliary root does not have order n")

    character_order_checks = 0
    binary_character_rejections = 0
    for exponent in range(1, order):
        value = pow(omega, exponent, field_prime)
        if value == 1 or pow(value, order, field_prime) != 1:
            raise AssertionError("nonzero dual exponent lost full order")
        character_order_checks += 1
        if value in (1, field_prime - 1):
            raise AssertionError("nontrivial odd-order character became binary")
        binary_character_rejections += 1

    parity = [1 if scalar % 2 == 0 else field_prime - 1 for scalar in range(order)]
    fourier_nonzero = 0
    closed_form_checks = 0
    for frequency in range(order):
        direct = 0
        for scalar, sign in enumerate(parity):
            phase = pow(omega, (-frequency * scalar) % order, field_prime)
            direct = (direct + sign * phase) % field_prime
        inverse_phase = pow(omega, (-frequency) % order, field_prime)
        denominator = (1 + inverse_phase) % field_prime
        if denominator == 0:
            raise AssertionError("odd-order root produced -1")
        closed = 2 * pow(denominator, -1, field_prime) % field_prime
        if direct != closed:
            raise AssertionError("parity Fourier closed form failed")
        if direct == 0:
            raise AssertionError("parity Fourier coefficient vanished")
        fourier_nonzero += 1
        closed_form_checks += 1

    frequency_permutation_checks = 0
    base_frequencies = set(range(order))
    for unit in PUBLIC_UNITS:
        reduced = unit % order
        if reduced == 0:
            continue
        permuted = {(frequency * reduced) % order for frequency in range(order)}
        if permuted != base_frequencies:
            raise AssertionError("public scalar did not permute dual frequencies")
        frequency_permutation_checks += order

    parity_homomorphism_counterexample = (
        parity[0]
        != parity[order - 1] * parity[1] % field_prime
    )
    if not parity_homomorphism_counterexample:
        raise AssertionError("canonical parity accidentally became a character")

    return {
        "order": order,
        "auxiliary_field_prime": field_prime,
        "primitive_order_n_root": omega,
        "character_order_checks": character_order_checks,
        "binary_character_rejections": binary_character_rejections,
        "nonzero_parity_fourier_coefficients": fourier_nonzero,
        "fourier_closed_form_checks": closed_form_checks,
        "frequency_permutation_checks": frequency_permutation_checks,
        "canonical_parity_is_not_character": True,
        "exact_fourier_support": order,
    }


def secp256k1_certificate() -> dict[str, object]:
    extension_degree = (SECP_N - 1) // 6
    return {
        "n": SECP_N,
        "bit_length": SECP_N.bit_length(),
        "one_dimensional_nontrivial_character_order": SECP_N,
        "nontrivial_binary_characters": 0,
        "exact_parity_fourier_support": SECP_N,
        "standard_linear_state_dimension_lower_bound": SECP_N,
        "dual_extension_degree": extension_degree,
        "does_bounded_linear_cm_state_select_oriented_root": False,
        "central_target": "UNIFORM-ORIENTED-ROOT-CIRCUIT-056",
        "selected_successor": "UORC056-NONLINEAR-CM-STATE-B8",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "uorc056_cm_recurrence_state_results.json"
        ),
    )
    args = parser.parse_args()

    cases = [run_case(order) for order in FROZEN_ORDERS]
    payload = {
        "package": "UNIFORM-ORIENTED-ROOT-CIRCUIT-056-CM-RECURRENCE-STATE-B7",
        "cases": cases,
        "aggregate": {
            "cases": len(cases),
            "character_order_checks": sum(
                case["character_order_checks"] for case in cases
            ),
            "binary_character_rejections": sum(
                case["binary_character_rejections"] for case in cases
            ),
            "nonzero_parity_fourier_coefficients": sum(
                case["nonzero_parity_fourier_coefficients"] for case in cases
            ),
            "fourier_closed_form_checks": sum(
                case["fourier_closed_form_checks"] for case in cases
            ),
            "frequency_permutation_checks": sum(
                case["frequency_permutation_checks"] for case in cases
            ),
            "all_parity_spectra_full": all(
                case["exact_fourier_support"] == case["order"]
                for case in cases
            ),
            "all_parity_targets_noncharacters": all(
                case["canonical_parity_is_not_character"] for case in cases
            ),
        },
        "secp256k1": secp256k1_certificate(),
        "decision": (
            "Compact CM descent does not provide a nonconstant kernel state "
            "without a chosen H-linearization. Every nontrivial one-dimensional "
            "linearization is a full order-n dual character, while exact "
            "canonical parity has nonzero Fourier coefficient at every one of "
            "the n dual frequencies. A bounded-state standard linear CM "
            "recurrence therefore cannot evaluate the oriented root."
        ),
        "claim_boundary": [
            "Character orders and parity Fourier support are checked exactly in auxiliary finite fields.",
            "The line-bundle descent interpretation is a scoped standard-linearization statement.",
            "The result does not exclude nonlinear finite-state recurrences or arbitrary arithmetic circuits.",
            "No parity oracle, EDS-residue oracle, or ECDLP improvement is obtained.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["aggregate"], indent=2))
    print(json.dumps(payload["secp256k1"], indent=2))


if __name__ == "__main__":
    main()
