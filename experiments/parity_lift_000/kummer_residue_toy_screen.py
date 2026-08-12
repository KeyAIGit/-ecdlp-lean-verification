#!/usr/bin/env python3
"""Frozen toy screen for the Kummer form of the EDS Residue bit.

The program accepts no external curves, points, keys, wallets, or
production-sized instances. It reuses the frozen arithmetic helpers from
`structured_char_parity_screen.py`.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

from structured_char_parity_screen import (
    FROZEN_CURVES,
    bit_vector,
    division_polynomial_evaluator,
    exact_xor_weight_at_most_four,
    orbit,
    quadratic_character,
)

MAX_X_LINEAR_PRODUCT_WEIGHT = 4


@dataclass(frozen=True)
class CurveResult:
    p: int
    order: int
    generator: tuple[int, int]
    chi_minus_one: int
    phi_raw_g: int
    chi_phi_raw_g: int
    predicted_rho_negation_multiplier: int
    negation_checks: int
    all_negation_checks_passed: bool
    rho_kummer_invariant: bool
    valid_x_linear_character_vectors: int | None
    exact_x_linear_product_up_to_weight_four: bool | None
    best_single_matches: int | None
    best_single_total: int | None
    best_single_accuracy: float | None
    smallest_best_shift: int | None
    smallest_best_global_sign: int | None


def raw_point_scale(point: tuple[int, int], p: int, order: int) -> int:
    """Compute the ratio-root point function on one frozen toy curve."""
    if math.gcd(order, p - 1) != 1:
        raise AssertionError("frozen point order is not coprime to p-1")
    psi = division_polynomial_evaluator(point, p)
    numerator = psi(p - 1)
    denominator = psi(p - 1 + order)
    if numerator == 0 or denominator == 0:
        raise AssertionError("raw point scale has a zero numerator or denominator")
    ratio = numerator * pow(denominator, -1, p) % p
    inverse_order_squared = pow(order * order % (p - 1), -1, p - 1)
    value = pow(ratio, inverse_order_squared, p)
    if pow(value, order * order, p) != ratio:
        raise AssertionError("raw point-scale root check failed")
    return value


def x_linear_character_vectors(
    points: list[tuple[int, int] | None], p: int
) -> dict[int, int]:
    """Distinct character vectors chi(x+c) with no zero on the orbit."""
    representatives: dict[int, int] = {}
    for shift in range(p):
        signs: list[int] = []
        for point in points[1:]:
            assert point is not None
            sign = quadratic_character(point[0] + shift, p)
            if sign == 0:
                break
            signs.append(sign)
        else:
            representatives.setdefault(bit_vector(signs), shift)
    return representatives


def run_curve(p: int, order: int, generator: tuple[int, int]) -> CurveResult:
    points = orbit(generator, order, p)
    psi_g = division_polynomial_evaluator(generator, p)
    phi_raw_g = raw_point_scale(generator, p, order)
    chi_phi_raw_g = quadratic_character(phi_raw_g, p)
    chi_minus_one = quadratic_character(-1, p)
    predicted_multiplier = chi_minus_one * chi_phi_raw_g

    rho = [quadratic_character(psi_g(k), p) for k in range(1, order)]
    if any(sign == 0 for sign in rho):
        raise AssertionError("EDS residue vanished on a nonzero prime-order scalar")

    negation_checks = 0
    for k in range(1, order):
        if rho[order - k - 1] != predicted_multiplier * rho[k - 1]:
            raise AssertionError("EDS-residue negation law failed")
        negation_checks += 1

    kummer_invariant = predicted_multiplier == 1
    if not kummer_invariant:
        return CurveResult(
            p=p,
            order=order,
            generator=generator,
            chi_minus_one=chi_minus_one,
            phi_raw_g=phi_raw_g,
            chi_phi_raw_g=chi_phi_raw_g,
            predicted_rho_negation_multiplier=predicted_multiplier,
            negation_checks=negation_checks,
            all_negation_checks_passed=True,
            rho_kummer_invariant=False,
            valid_x_linear_character_vectors=None,
            exact_x_linear_product_up_to_weight_four=None,
            best_single_matches=None,
            best_single_total=None,
            best_single_accuracy=None,
            smallest_best_shift=None,
            smallest_best_global_sign=None,
        )

    representatives = x_linear_character_vectors(points, p)
    target = bit_vector(rho)
    complement_mask = (1 << (order - 1)) - 1
    exact = exact_xor_weight_at_most_four(representatives, target)
    exact = exact or exact_xor_weight_at_most_four(
        representatives, target ^ complement_mask
    )

    best_matches = -1
    best_shift = -1
    best_global_sign = 1
    for vector, shift in representatives.items():
        matches = order - 1 - (vector ^ target).bit_count()
        global_sign = 1
        if order - 1 - matches > matches:
            matches = order - 1 - matches
            global_sign = -1
        candidate = (matches, -shift, global_sign)
        incumbent = (best_matches, -best_shift, best_global_sign)
        if candidate > incumbent:
            best_matches = matches
            best_shift = shift
            best_global_sign = global_sign

    return CurveResult(
        p=p,
        order=order,
        generator=generator,
        chi_minus_one=chi_minus_one,
        phi_raw_g=phi_raw_g,
        chi_phi_raw_g=chi_phi_raw_g,
        predicted_rho_negation_multiplier=predicted_multiplier,
        negation_checks=negation_checks,
        all_negation_checks_passed=True,
        rho_kummer_invariant=True,
        valid_x_linear_character_vectors=len(representatives),
        exact_x_linear_product_up_to_weight_four=exact,
        best_single_matches=best_matches,
        best_single_total=order - 1,
        best_single_accuracy=best_matches / (order - 1),
        smallest_best_shift=best_shift,
        smallest_best_global_sign=best_global_sign,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("kummer_residue_toy_results.json"),
    )
    args = parser.parse_args()

    results = [run_curve(*curve) for curve in FROZEN_CURVES]
    payload = {
        "scope": "five frozen prime-order toy curves y^2=x^3+7 only",
        "target": "rho_G([k]G)=chi(psi_k(G))",
        "negation_law": (
            "rho_G(-Q)=chi(-1)*chi(phi_raw(G))*rho_G(Q)"
        ),
        "maximum_x_linear_product_weight": MAX_X_LINEAR_PRODUCT_WEIGHT,
        "curves": [asdict(result) for result in results],
        "aggregate": {
            "all_negation_checks_passed": all(
                result.all_negation_checks_passed for result in results
            ),
            "kummer_invariant_curves": sum(
                result.rho_kummer_invariant for result in results
            ),
            "kummer_anti_invariant_curves": sum(
                not result.rho_kummer_invariant for result in results
            ),
            "exact_x_linear_products_found_on_invariant_curves": sum(
                bool(result.exact_x_linear_product_up_to_weight_four)
                for result in results
                if result.rho_kummer_invariant
            ),
        },
        "claim_boundary": [
            "This is a frozen toy structural screen, not an asymptotic theorem.",
            "Kummer invariance depends on chi(-1)*chi(phi_raw(G)), not on p mod 4 alone.",
            "The x-linear product search is applied only when the target residue bit is Kummer-invariant.",
            "No external curve, public key, wallet, or production-sized target is accepted.",
            "Failure up to weight four does not rule out higher-degree or fast-recursive theta/EDS observables.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
