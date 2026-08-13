#!/usr/bin/env python3
"""Toy-only exact/analytic replay for NORMALIZED-PERIOD-LINEAR-STATE-BARRIER-035.

The normalized Gaussian-period resolvent

    U_m = A_m / A_1,
    A_m = sum_{a in {1,lambda,lambda^2}} (zeta_n^(a*m)-zeta_n^(-a*m))

has a degree-six linear recurrence over the splitting coefficient field.
This replay verifies that recurrence on the frozen j=0 toy corpus and computes
the exact finite-field rank/extension-degree tradeoff for every coefficient
field F_(p^e) compatible with the cyclotomic phase.

No external point, key, wallet, or production-sized target is accepted.
The secp256k1 block performs public-parameter integer arithmetic only.
"""
from __future__ import annotations

import argparse
import cmath
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

from anti_frobenius_orientation_seed import eta, scalar_lambda
from nonlocal_odd_anchor_screen import FROZEN_CASES

SECP256K1_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
SECP256K1_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
SECP256K1_LAMBDA = 0x5363AD4CC05C30E0A5261C028812645A122E22EA20816678DF02967C1B23BD72
TOLERANCE = 1.0e-8


def multiplicative_order(a: int, modulus: int) -> int:
    if math.gcd(a, modulus) != 1:
        raise ValueError("multiplicative order requires a unit")
    value = 1
    for order in range(1, modulus):
        value = value * a % modulus
        if value == 1:
            return order
    raise AssertionError("order search exhausted")


def c6_subgroup(lam: int, order: int) -> set[int]:
    lam2 = lam * lam % order
    return {
        1,
        lam,
        lam2,
        (-1) % order,
        (-lam) % order,
        (-lam2) % order,
    }


def subgroup_generated_by(value: int, modulus: int) -> set[int]:
    current = 1
    out: set[int] = set()
    while current not in out:
        out.add(current)
        current = current * value % modulus
    if current != 1:
        raise AssertionError("generated unit set did not close at one")
    return out


def normalized_values(lam: int, order: int) -> list[complex]:
    seed_eta = eta(1, lam, order)
    seed = seed_eta - seed_eta.conjugate()
    if abs(seed) <= TOLERANCE:
        raise AssertionError("normalized seed vanished")
    out: list[complex] = []
    for index in range(order):
        value = eta(index, lam, order)
        out.append((value - value.conjugate()) / seed)
    return out


def recurrence_coefficients(lam: int, order: int) -> tuple[complex, ...]:
    lam2 = lam * lam % order
    roots = [
        cmath.exp(2j * math.pi * exponent / order)
        for exponent in (1, lam, lam2)
    ]
    s = sum(roots)
    t = sum(1 / root for root in roots)
    return (
        1.0 + 0.0j,
        -(s + t),
        s * t + s + t,
        -(s * s + t * t + 2),
        s * t + s + t,
        -(s + t),
        1.0 + 0.0j,
    )


@dataclass(frozen=True)
class CaseResult:
    p: int
    order: int
    generator: tuple[int, int]
    beta: int
    lam: int
    recurrence_checks: int
    maximum_recurrence_residual: float
    maximum_coefficient_imaginary_residual: float
    coefficient_palindromic: bool
    cyclotomic_compatible: bool
    frobenius_order: int | None
    characteristic_roots_frobenius_stable_over_base: bool | None
    tradeoff_formula_checks: int
    minimum_linear_output_base_field_words: int | None
    minimum_translation_linear_state_base_field_words: int | None
    minimum_linear_output_witness_e: int | None
    minimum_linear_output_witness_rank: int | None
    minimum_state_witness_e: int | None
    minimum_state_witness_rank: int | None


def run_case(
    p: int, order: int, generator: tuple[int, int]
) -> CaseResult:
    beta, lam = scalar_lambda(p, order, generator)
    values = normalized_values(lam, order)
    coefficients = recurrence_coefficients(lam, order)

    max_imag = max(abs(coefficient.imag) for coefficient in coefficients)
    if max_imag > TOLERANCE:
        raise AssertionError("recurrence coefficient left conjugation-fixed line")
    palindromic = all(
        abs(coefficients[index] - coefficients[-1 - index]) <= TOLERANCE
        for index in range(len(coefficients))
    )
    if not palindromic:
        raise AssertionError("reciprocal characteristic polynomial lost symmetry")

    max_residual = 0.0
    for index in range(order):
        residual = sum(
            coefficients[offset] * values[(index + offset) % order]
            for offset in range(7)
        )
        max_residual = max(max_residual, abs(residual))
        if abs(residual) > TOLERANCE:
            raise AssertionError(
                f"degree-six recurrence failed: p={p}, n={order}, "
                f"index={index}, residual={residual}"
            )

    if math.gcd(p, order) != 1:
        return CaseResult(
            p=p,
            order=order,
            generator=generator,
            beta=beta,
            lam=lam,
            recurrence_checks=order,
            maximum_recurrence_residual=max_residual,
            maximum_coefficient_imaginary_residual=max_imag,
            coefficient_palindromic=palindromic,
            cyclotomic_compatible=False,
            frobenius_order=None,
            characteristic_roots_frobenius_stable_over_base=None,
            tradeoff_formula_checks=0,
            minimum_linear_output_base_field_words=None,
            minimum_translation_linear_state_base_field_words=None,
            minimum_linear_output_witness_e=None,
            minimum_linear_output_witness_rank=None,
            minimum_state_witness_e=None,
            minimum_state_witness_rank=None,
        )

    d = multiplicative_order(p % order, order)
    c6 = c6_subgroup(lam, order)
    base_stable = p % order in c6

    best_linear: tuple[int, int, int] | None = None
    best_state: tuple[int, int, int] | None = None
    formula_checks = 0
    for e in range(1, d + 1):
        q_step = pow(p, e, order)
        h = subgroup_generated_by(q_step, order)
        m_e = len(h)
        intersection = len(c6 & h)
        closure = {left * right % order for left in c6 for right in h}
        exact_rank = 6 * m_e // intersection
        if exact_rank != len(closure):
            raise AssertionError("subgroup product cardinality formula failed")
        if m_e != d // math.gcd(d, e):
            raise AssertionError("Frobenius orbit order formula failed")

        linear_words = e * exact_rank
        state_rank = m_e
        state_words = e * state_rank
        if best_linear is None or linear_words < best_linear[0]:
            best_linear = (linear_words, e, exact_rank)
        if best_state is None or state_words < best_state[0]:
            best_state = (state_words, e, state_rank)
        formula_checks += 1

    assert best_linear is not None and best_state is not None
    return CaseResult(
        p=p,
        order=order,
        generator=generator,
        beta=beta,
        lam=lam,
        recurrence_checks=order,
        maximum_recurrence_residual=max_residual,
        maximum_coefficient_imaginary_residual=max_imag,
        coefficient_palindromic=palindromic,
        cyclotomic_compatible=True,
        frobenius_order=d,
        characteristic_roots_frobenius_stable_over_base=base_stable,
        tradeoff_formula_checks=formula_checks,
        minimum_linear_output_base_field_words=best_linear[0],
        minimum_translation_linear_state_base_field_words=best_state[0],
        minimum_linear_output_witness_e=best_linear[1],
        minimum_linear_output_witness_rank=best_linear[2],
        minimum_state_witness_e=best_state[1],
        minimum_state_witness_rank=best_state[2],
    )


def secp256k1_certificate() -> dict[str, object]:
    p = SECP256K1_P
    n = SECP256K1_N
    lam = SECP256K1_LAMBDA
    d = (n - 1) // 6
    fixed_subfield_degree = d // 2
    linear_output_words = 3 * d
    translation_linear_state_words = d
    checks = {
        "n_minus_one_divisible_by_six": (n - 1) % 6 == 0,
        "d_mod_six_is_four": d % 6 == 4,
        "lambda_has_order_three": (
            pow(lam, 3, n) == 1 and lam % n not in (0, 1)
        ),
        "p_to_d_is_one": pow(p, d, n) == 1,
        "half_frobenius_is_negation": pow(p, d // 2, n) == n - 1,
        "linear_output_bound_is_half_n_minus_one": (
            linear_output_words == (n - 1) // 2
        ),
        "rank_six_fixed_subfield_product": (
            fixed_subfield_degree * 6 == linear_output_words
        ),
    }
    if not all(checks.values()):
        raise AssertionError(f"secp256k1 certificate failed: {checks}")
    return {
        "p": p,
        "order": n,
        "lambda": lam,
        "frobenius_order_d": d,
        "fixed_subfield_degree_d_over_2": fixed_subfield_degree,
        "normalized_period_linear_output_rank_over_fixed_subfield": 6,
        "linear_output_base_field_word_lower_bound": linear_output_words,
        "translation_linear_arbitrary_readout_base_field_word_lower_bound": (
            translation_linear_state_words
        ),
        "natural_orientation_pairs": d,
        "checks": checks,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "normalized_period_linear_state_barrier_results.json"
        ),
    )
    args = parser.parse_args()

    cases = [
        run_case(p, order, generator)
        for p, order, generator in FROZEN_CASES
    ]
    compatible = [case for case in cases if case.cyclotomic_compatible]
    payload = {
        "package": "NORMALIZED-PERIOD-LINEAR-STATE-BARRIER-035",
        "scope": (
            "frozen toy complex recurrence replay, exact finite-field "
            "Frobenius-closure arithmetic, and fixed public secp256k1 "
            "parameter certificates; no external point or production target"
        ),
        "recurrence": {
            "sequence": (
                "U_m=A_m/A_1, "
                "A_m=sum_(a in {1,lambda,lambda^2})"
                "(zeta^(a*m)-zeta^(-a*m))"
            ),
            "characteristic_polynomial": (
                "(X^3-sX^2+tX-1)(X^3-tX^2+sX-1)"
            ),
            "expanded_coefficients": [
                "1",
                "-(s+t)",
                "st+s+t",
                "-(s^2+t^2+2)",
                "st+s+t",
                "-(s+t)",
                "1",
            ],
        },
        "cases": [asdict(case) for case in cases],
        "aggregate": {
            "cases": len(cases),
            "cyclotomic_compatible_cases": len(compatible),
            "characteristic_divides_order_cases": sum(
                bool(case.characteristic_roots_frobenius_stable_over_base)
                for case in compatible
            ),
            "total_recurrence_checks": sum(
                case.recurrence_checks for case in cases
            ),
            "maximum_recurrence_residual": max(
                case.maximum_recurrence_residual for case in cases
            ),
            "maximum_coefficient_imaginary_residual": max(
                case.maximum_coefficient_imaginary_residual
                for case in cases
            ),
            "total_frobenius_tradeoff_formula_checks": sum(
                case.tradeoff_formula_checks for case in compatible
            ),
            "all_toy_linear_state_minima_positive": all(
                (case.minimum_translation_linear_state_base_field_words or 0)
                > 0
                for case in compatible
            ),
        },
        "secp256k1": secp256k1_certificate(),
        "theorem_summary": {
            "linear_output_exact_rank_over_F_p^e": (
                "|C6*<p^e>|=6*m_e/|C6 intersection <p^e>|, "
                "m_e=d/gcd(d,e)"
            ),
            "secp_linear_output_tradeoff": (
                "e*r_e >= 3*d = (n-1)/2 base-field words"
            ),
            "translation_linear_arbitrary_readout_tradeoff": (
                "e*r >= d = (n-1)/6 base-field words"
            ),
        },
        "decision": (
            "The normalized period has a short degree-six recurrence only "
            "after its coefficients are placed in a huge field. Across every "
            "explicit finite-field linear-output recurrence, rank times "
            "coefficient-field degree remains linear in n. More generally, "
            "any nonconstant translation-linear state with arbitrary readout "
            "requires at least d=(n-1)/6 base-field words. This closes the "
            "explicit finite-field translation-linear blackbox class, not "
            "arbitrary nonlinear coordinate circuits."
        ),
        "claim_boundary": [
            (
                "Complex replay verifies the recurrence identity and numerical "
                "sign conventions, not a public finite-field evaluator."
            ),
            (
                "The rank formulas concern exact linear recurrences or explicit "
                "translation-linear state over finite fields."
            ),
            (
                "No lower bound is claimed for arbitrary nonlinear coordinate, "
                "p-adic, analytic, symbolic, approximate, or noisy algorithms."
            ),
            "The secp256k1 subgroup is not enumerated.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
