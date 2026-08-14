#!/usr/bin/env python3
"""Exact toric-shadow replay for UORC056 cyclic factorial boundary B15.

The script studies the closest multiplicative root-of-unity analogue of the
alternating elliptic factorial. It proves exact density, local q-difference,
full Fourier support, and the two-level square-root frontier on frozen small
prime orders. No external point, key, wallet, unknown scalar, or production
DLP target is accepted.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

TORIC_CASES = (
    (29, 7),
    (53, 13),
    (103, 17),
    (191, 19),
    (311, 31),
)

SECP_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def inv(value: int, modulus: int) -> int:
    return pow(value, -1, modulus)


def primitive_n_root(modulus: int, order: int) -> int:
    if (modulus - 1) % order != 0:
        raise AssertionError("order does not divide multiplicative group")
    exponent = (modulus - 1) // order
    for candidate in range(2, modulus):
        root = pow(candidate, exponent, modulus)
        if root != 1 and pow(root, order, modulus) == 1:
            return root
    raise AssertionError("primitive root not found")


def poly_mul(left: list[int], right: list[int], modulus: int) -> list[int]:
    result = [0] * (len(left) + len(right) - 1)
    for i, left_value in enumerate(left):
        for j, right_value in enumerate(right):
            result[i + j] = (
                result[i + j] + left_value * right_value
            ) % modulus
    return result


def poly_eval(poly: list[int], value: int, modulus: int) -> int:
    result = 0
    for coefficient in reversed(poly):
        result = (result * value + coefficient) % modulus
    return result


def product_polynomial(roots: list[int], modulus: int) -> list[int]:
    """Return product(1-root*X)."""
    result = [1]
    for root in roots:
        result = poly_mul(result, [1, (-root) % modulus], modulus)
    return result


def minimum_two_level_cost(length: int) -> tuple[int, int]:
    best_width = 1
    best_cost = length + 1
    for width in range(1, length + 1):
        cost = width + math.ceil(length / width)
        if cost < best_cost:
            best_width = width
            best_cost = cost
    return best_width, best_cost


def build_case(modulus: int, order: int) -> dict[str, object]:
    q = primitive_n_root(modulus, order)
    middle = (order - 1) // 2

    odd_roots = [pow(q, 2 * index + 1, modulus) for index in range(middle)]
    even_roots = [pow(q, 2 * index, modulus) for index in range(1, middle + 1)]
    odd_poly = product_polynomial(odd_roots, modulus)
    even_poly = product_polynomial(even_roots, modulus)
    full_poly = poly_mul(odd_poly, even_poly, modulus)
    if full_poly != [1] * order:
        raise AssertionError("half products did not multiply to (1-X^n)/(1-X)")
    if not all(odd_poly) or not all(even_poly):
        raise AssertionError("frozen half factorial polynomial was not dense")

    q_difference_checks = 0
    for x_value in range(modulus):
        odd_value = poly_eval(odd_poly, x_value, modulus)
        even_value = poly_eval(even_poly, x_value, modulus)
        shifted = q * q * x_value % modulus
        shifted_odd = poly_eval(odd_poly, shifted, modulus)
        shifted_even = poly_eval(even_poly, shifted, modulus)
        if 0 in (odd_value, even_value, shifted_odd, shifted_even):
            continue
        denominator = (1 - q * x_value) % modulus
        if denominator == 0:
            continue
        left = (
            shifted_odd
            * inv(shifted_even, modulus)
            * even_value
            * inv(odd_value, modulus)
        ) % modulus
        right = (
            (1 - x_value)
            * (1 - q * q * x_value)
            * inv(denominator * denominator % modulus, modulus)
        ) % modulus
        if left != right:
            raise AssertionError("local q-difference identity failed")
        q_difference_checks += 1

    exponent_signs = [0] + [
        1 if residue % 2 else -1 for residue in range(1, order)
    ]
    fourier_values: list[int] = []
    for frequency in range(order):
        root = pow(q, frequency, modulus)
        coefficient = sum(
            exponent_signs[residue] * pow(root, residue, modulus)
            for residue in range(order)
        ) % modulus
        fourier_values.append(coefficient)
    if fourier_values[0] != 0:
        raise AssertionError("balanced exponent vector had nonzero mean")
    if any(value == 0 for value in fourier_values[1:]):
        raise AssertionError("alternating exponent vector lost a frequency")

    closed_form_checks = 0
    for frequency in range(1, order):
        z = pow(q, frequency, modulus)
        if (z + 1) % modulus == 0:
            raise AssertionError("odd-order root unexpectedly equalled -1")
        expected = (z - 1) * inv(z + 1, modulus) % modulus
        if fourier_values[frequency] != expected:
            raise AssertionError("Fourier closed form failed")
        closed_form_checks += 1

    block_width, block_cost = minimum_two_level_cost(middle)
    if block_cost * block_cost < 4 * middle:
        raise AssertionError("two-level factorial cost violated AM-GM")

    return {
        "field_prime": modulus,
        "order": order,
        "primitive_root": q,
        "half_length": middle,
        "odd_polynomial_degree": len(odd_poly) - 1,
        "even_polynomial_degree": len(even_poly) - 1,
        "odd_nonzero_coefficients": sum(value != 0 for value in odd_poly),
        "even_nonzero_coefficients": sum(value != 0 for value in even_poly),
        "full_product_degree": len(full_poly) - 1,
        "q_difference_checks": q_difference_checks,
        "nonzero_fourier_frequencies": sum(value != 0 for value in fourier_values),
        "fourier_closed_form_checks": closed_form_checks,
        "best_two_level_block_width": block_width,
        "best_two_level_charged_cost": block_cost,
        "four_length_le_cost_square": 4 * middle <= block_cost * block_cost,
    }


def secp_certificate() -> dict[str, object]:
    middle = (SECP_N - 1) // 2
    extension_degree = (SECP_N - 1) // 6
    lower = math.isqrt(4 * middle)
    if lower * lower < 4 * middle:
        lower += 1
    return {
        "p": SECP_P,
        "n": SECP_N,
        "bit_length": SECP_N.bit_length(),
        "gcd_n_p_minus_one": math.gcd(SECP_N, SECP_P - 1),
        "half_factorial_length": middle,
        "standard_two_level_cost_lower_bound": lower,
        "standard_two_level_cost_lower_bound_bit_length": lower.bit_length(),
        "explicit_dual_root_extension_degree": extension_degree,
        "extension_degree_bit_length": extension_degree.bit_length(),
        "base_field_contains_nontrivial_nth_root": False,
        "toric_half_factorial_has_full_linearized_frequency_support": True,
        "known_q_holonomic_cost_class": "quasi-linear in sqrt(N)",
        "known_q_holonomic_method_meets_fixed_epsilon_subroot_gate": False,
        "endpoint_index_or_full_dual_phase_still_required": True,
        "public_parity_evaluator_found": False,
        "central_target": "UNIFORM-ORIENTED-ROOT-CIRCUIT-056",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    cases = [build_case(*case) for case in TORIC_CASES]
    aggregate = {
        "cases": len(cases),
        "q_difference_checks": sum(case["q_difference_checks"] for case in cases),
        "fourier_closed_form_checks": sum(
            case["fourier_closed_form_checks"] for case in cases
        ),
        "all_half_polynomials_dense": all(
            case["odd_nonzero_coefficients"] == case["half_length"] + 1
            and case["even_nonzero_coefficients"] == case["half_length"] + 1
            for case in cases
        ),
        "all_nonzero_frequencies_present": all(
            case["nonzero_fourier_frequencies"] == case["order"] - 1
            for case in cases
        ),
        "all_two_level_bounds_hold": all(
            case["four_length_le_cost_square"] for case in cases
        ),
    }
    payload = {
        "package": "UORC056-CYCLIC-FACTORIAL-STANDARD-BOUNDARY-B15",
        "cases": cases,
        "aggregate": aggregate,
        "secp256k1": secp_certificate(),
        "decision": (
            "The exact root-of-unity shadow has a constant-size local "
            "q-difference but dense half-factor polynomials and full nonzero "
            "Fourier support. Standard q-holonomic and baby-step/giant-step "
            "evaluation reaches the square-root frontier and additionally "
            "requires the hidden endpoint index or a full dual phase. No strict "
            "sub-square-root finite-field cyclic-factorial evaluator is obtained."
        ),
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(aggregate, indent=2))
    print(json.dumps(payload["secp256k1"], indent=2))


if __name__ == "__main__":
    main()
