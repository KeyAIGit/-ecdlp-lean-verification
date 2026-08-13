#!/usr/bin/env python3
"""Exact toy-only screen for the first two-anchor circulant resultant.

The public operator template is

    D_(a,b,c)(k) = det(a I + b T_G + c T_Q),  Q=[k]G,

with T_Q=T_G^k. The script checks exact binomial blindness and six affine
exponent symmetries, then screens a bounded integer coefficient grammar.
Only frozen subgroup orders and the public secp256k1 order are used.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path

FROZEN_CASES = (
    (151, 19),
    (43, 31),
    (79, 67),
    (1087, 271),
    (2851, 397),
    (1663, 433),
)
SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def trim(poly: list[int], p: int) -> list[int]:
    result = [value % p for value in poly]
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def poly_divmod(
    numerator: list[int], denominator: list[int], p: int
) -> tuple[list[int], list[int]]:
    numerator = trim(numerator, p)
    denominator = trim(denominator, p)
    if denominator == [0]:
        raise ZeroDivisionError
    denominator_degree = len(denominator) - 1
    inverse_lead = pow(denominator[-1], -1, p)
    quotient = [0] * max(1, len(numerator) - len(denominator) + 1)
    remainder = numerator[:]
    while len(remainder) - 1 >= denominator_degree and remainder != [0]:
        shift = len(remainder) - 1 - denominator_degree
        scale = remainder[-1] * inverse_lead % p
        quotient[shift] = scale
        for index, coefficient in enumerate(denominator):
            remainder[index + shift] = (
                remainder[index + shift] - scale * coefficient
            ) % p
        remainder = trim(remainder, p)
    return trim(quotient, p), remainder


def resultant(numerator: list[int], denominator: list[int], p: int) -> int:
    numerator = trim(numerator, p)
    denominator = trim(denominator, p)
    m = len(numerator) - 1
    n = len(denominator) - 1
    if denominator == [0]:
        return 0
    if n == 0:
        return pow(denominator[0], m, p)
    if m < n:
        sign = p - 1 if (m * n) % 2 else 1
        return sign * resultant(denominator, numerator, p) % p
    _, remainder = poly_divmod(numerator, denominator, p)
    if remainder == [0]:
        return 0
    remainder_degree = len(remainder) - 1
    sign = p - 1 if (m * n) % 2 else 1
    factor = pow(denominator[-1], m - remainder_degree, p)
    return sign * factor * resultant(denominator, remainder, p) % p


def trinomial_determinant(
    p: int, n: int, k: int, a: int, b: int, c: int
) -> int:
    polynomial = [0] * (max(1, k) + 1)
    polynomial[0] = a % p
    polynomial[1] = (polynomial[1] + b) % p
    polynomial[k] = (polynomial[k] + c) % p
    cycle_polynomial = [p - 1] + [0] * (n - 1) + [1]
    return resultant(cycle_polynomial, polynomial, p)


def quadratic_character(value: int, p: int) -> int:
    value %= p
    if value == 0:
        return 0
    return 1 if pow(value, (p - 1) // 2, p) == 1 else -1


def normalized_templates(bound: int) -> list[tuple[int, int, int]]:
    templates: list[tuple[int, int, int]] = []
    for template in itertools.product(range(-bound, bound + 1), repeat=3):
        if template == (0, 0, 0):
            continue
        gcd_value = math.gcd(
            math.gcd(abs(template[0]), abs(template[1])), abs(template[2])
        )
        if gcd_value > 1:
            continue
        first_nonzero = next(value for value in template if value)
        if first_nonzero < 0:
            continue
        templates.append(template)
    return templates


def parity_mismatch_witness(
    n: int, transform: str
) -> tuple[int, int] | None:
    for k in range(2, min(n, 10000)):
        if transform == "inverse":
            transformed = pow(k, -1, n)
        elif transform == "k_over_k_minus_one":
            transformed = k * pow(k - 1, -1, n) % n
        else:
            raise AssertionError("unknown transform")
        if (k & 1) != (transformed & 1):
            return k, transformed
    return None


def check_case(p: int, n: int) -> dict[str, object]:
    binomial_checks = 0
    symmetry_checks = 0
    for shift in range(1, n):
        determinant = trinomial_determinant(p, n, shift, 2, 3, 0)
        expected = (pow(2, n, p) + pow(3, n, p)) % p
        if determinant != expected:
            raise AssertionError("binomial determinant formula failed")
        binomial_checks += 1

    a, b, c = 2, 3, 5
    for k in range(2, n):
        inverse_k = pow(k, -1, n)
        inverse_one_minus_k = pow((1 - k) % n, -1, n)
        inverse_k_minus_one = pow((k - 1) % n, -1, n)
        values = {
            trinomial_determinant(p, n, k, a, b, c),
            trinomial_determinant(p, n, inverse_k, a, c, b),
            trinomial_determinant(p, n, (1 - k) % n, b, a, c),
            trinomial_determinant(p, n, inverse_one_minus_k, b, c, a),
            trinomial_determinant(
                p, n, (k - 1) * inverse_k % n, c, a, b
            ),
            trinomial_determinant(
                p, n, k * inverse_k_minus_one % n, c, b, a
            ),
        }
        if len(values) != 1:
            raise AssertionError("affine exponent symmetry failed")
        symmetry_checks += 5

    return {
        "p": p,
        "n": n,
        "binomial_checks": binomial_checks,
        "affine_symmetry_checks": symmetry_checks,
        "b_equals_c_parity_mismatch": parity_mismatch_witness(n, "inverse"),
        "a_equals_c_parity_mismatch": parity_mismatch_witness(
            n, "k_over_k_minus_one"
        ),
    }


def screen_templates(bound: int) -> dict[str, object]:
    templates = normalized_templates(bound)
    direct_matches: list[tuple[int, int, int]] = []
    character_matches: list[tuple[int, int, int]] = []
    best: list[tuple[float, tuple[int, int, int], list[float]]] = []

    for template in templates:
        direct_all = True
        character_all = True
        accuracies: list[float] = []
        for p, n in FROZEN_CASES[:3]:
            values = [
                trinomial_determinant(p, n, k, *template)
                for k in range(1, n)
            ]
            target = [-1 if k % 2 else 1 for k in range(1, n)]
            even_values = {values[k - 1] for k in range(2, n, 2)}
            odd_values = {values[k - 1] for k in range(1, n, 2)}
            if not (
                len(even_values) == 1
                and len(odd_values) == 1
                and even_values != odd_values
            ):
                direct_all = False

            characters = [quadratic_character(value, p) for value in values]
            character_match = (
                0 not in characters
                and (
                    characters == target
                    or characters == [-value for value in target]
                )
            )
            if not character_match:
                character_all = False
            if 0 in characters:
                accuracy = 0.0
            else:
                accuracy = max(
                    sum(left == right for left, right in zip(characters, target)),
                    sum(left == -right for left, right in zip(characters, target)),
                ) / (n - 1)
            accuracies.append(accuracy)

        if direct_all:
            direct_matches.append(template)
        if character_all:
            character_matches.append(template)
        best.append((min(accuracies), template, accuracies))

    best.sort(reverse=True)
    return {
        "coefficient_bound": bound,
        "normalized_template_count": len(templates),
        "screen_orders": [n for _, n in FROZEN_CASES[:3]],
        "direct_two_value_matches": direct_matches,
        "quadratic_character_matches": character_matches,
        "best_min_accuracy": best[0][0] if best else None,
        "best_template": list(best[0][1]) if best else None,
        "best_case_accuracies": best[0][2] if best else None,
        "screen_is_bounded_evidence_only": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coefficient-bound", type=int, default=3)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    cases = [check_case(p, n) for p, n in FROZEN_CASES]
    secp_witnesses = {
        "n_mod_4": SECP_N % 4,
        "b_equals_c_inverse_witness": parity_mismatch_witness(
            SECP_N, "inverse"
        ),
        "a_equals_c_fractional_witness": parity_mismatch_witness(
            SECP_N, "k_over_k_minus_one"
        ),
    }
    screen = screen_templates(args.coefficient_bound)
    payload = {
        "experiment": "UORC056_SPARSE_TWO_TRANSLATION_RESULTANT_C5",
        "scope": "frozen toy subgroup orders and public secp256k1 order",
        "cases": cases,
        "secp256k1_public_order_witnesses": secp_witnesses,
        "bounded_template_screen": screen,
        "aggregate": {
            "binomial_two_shift_norm_blind": True,
            "six_affine_trinomial_symmetries_verified": True,
            "b_equals_c_class_rejected_for_secp256k1": (
                secp_witnesses["b_equals_c_inverse_witness"] is not None
            ),
            "a_equals_c_class_rejected_for_secp256k1": (
                secp_witnesses["a_equals_c_fractional_witness"] is not None
            ),
            "bounded_direct_decoder_found": bool(
                screen["direct_two_value_matches"]
            ),
            "bounded_character_decoder_found": bool(
                screen["quadratic_character_matches"]
            ),
            "general_asymmetric_trinomial_resultant": "open",
            "evaluator_found": False,
            "parity_oracle_found": False,
            "sub_sqrt_ecdlp_found": False,
        },
    }
    encoded = json.dumps(payload, indent=2, sort_keys=True)
    print(encoded)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(encoded + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
