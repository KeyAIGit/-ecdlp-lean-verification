#!/usr/bin/env python3
"""Frozen toy replay for POINT-FUNCTION-COBOUNDARY-005A."""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from eisenstein_root_phase_screen import (
    FROZEN_CASES,
    division_polynomial_evaluator as dpe,
    orbit,
    quadratic_character as qc,
)

SINGLE_RADIUS = 12
PERIOD_MULTIPLIER_RADIUS = 4
PERIOD_OFFSET_RADIUS = 7
PRODUCT_TRIALS = 1200
GLV_PRODUCT_TRIALS = 500


def raw_from_evaluator(evaluate, p: int, n: int) -> int:
    numerator = evaluate(p - 1)
    denominator = evaluate(p - 1 + n)
    if (
        not numerator
        or not denominator
        or math.gcd(n, p - 1) != 1
    ):
        raise AssertionError("raw point-function precondition failed")
    ratio = numerator * pow(denominator, -1, p) % p
    exponent = pow(n * n % (p - 1), -1, p - 1)
    value = pow(ratio, exponent, p)
    if pow(value, n * n, p) != ratio:
        raise AssertionError("raw point-function root check failed")
    return value


def index_family(n: int) -> tuple[int, ...]:
    indices = set(range(-SINGLE_RADIUS, SINGLE_RADIUS + 1))
    for period_multiplier in range(
        -PERIOD_MULTIPLIER_RADIUS,
        PERIOD_MULTIPLIER_RADIUS + 1,
    ):
        for offset in range(
            -PERIOD_OFFSET_RADIUS,
            PERIOD_OFFSET_RADIUS + 1,
        ):
            indices.add(period_multiplier * n + offset)
    return tuple(sorted(index for index in indices if index % n))


def glv_parameters(points, p: int, n: int) -> tuple[int, int]:
    cube_roots = [
        value
        for value in range(2, p)
        if (value * value + value + 1) % p == 0
    ]
    if len(cube_roots) != 2:
        raise AssertionError("primitive cube-root classification failed")
    beta = min(cube_roots)
    generator = points[1]
    image = (beta * generator[0] % p, generator[1])
    scalar_by_point = {point: scalar for scalar, point in enumerate(points)}
    if image not in scalar_by_point:
        raise AssertionError("GLV image left the declared subgroup")
    eigenvalue = scalar_by_point[image]
    if not eigenvalue or (eigenvalue * eigenvalue + eigenvalue + 1) % n:
        raise AssertionError("GLV eigenvalue equation failed")
    return beta, eigenvalue


def run_case(p: int, n: int, generator: tuple[int, int]) -> dict[str, object]:
    points = orbit(generator, n, p)
    evaluators = [None] + [
        dpe(points[scalar], p) for scalar in range(1, n)
    ]
    raw_values = [0] + [
        raw_from_evaluator(evaluators[scalar], p, n)
        for scalar in range(1, n)
    ]
    point_characters = [0] + [
        qc(raw_values[scalar], p) for scalar in range(1, n)
    ]
    if any(value not in (-1, 1) for value in point_characters[1:]):
        raise AssertionError("point-function character was not binary")

    indices = index_family(n)
    raw_field_checks = 0
    single_factor_checks = 0
    for scalar in range(1, n):
        evaluate = evaluators[scalar]
        for index in indices:
            field_left = raw_values[(index * scalar) % n]
            field_right = (
                pow(raw_values[scalar], index * index, p)
                * evaluate(index)
                % p
            )
            if field_left != field_right:
                raise AssertionError(
                    (
                        "raw_field",
                        p,
                        n,
                        scalar,
                        index,
                        field_left,
                        field_right,
                    )
                )
            raw_field_checks += 1

            left = qc(evaluate(index), p)
            right = point_characters[(index * scalar) % n]
            if index & 1:
                right *= point_characters[scalar]
            if left != right:
                raise AssertionError(
                    ("single", p, n, scalar, index, left, right)
                )
            single_factor_checks += 1

    rng = random.Random(20260812 + p + n)
    multiplicative_section_checks = 0
    for _ in range(PRODUCT_TRIALS):
        hidden_scalar = rng.randrange(1, n)
        left = 1
        right = 1
        valid = True
        for _ in range(rng.randrange(1, 7)):
            coefficient = rng.randrange(-5, 6)
            translation = rng.randrange(-5, 6)
            point_scalar = (
                coefficient * hidden_scalar + translation
            ) % n
            index = rng.choice(indices)
            exponent = rng.randrange(-3, 4)
            if not point_scalar:
                valid = False
                break
            value = evaluators[point_scalar](index)
            if not value:
                valid = False
                break
            if exponent & 1:
                left *= qc(value, p)
                right *= point_characters[(index * point_scalar) % n]
                if index & 1:
                    right *= point_characters[point_scalar]
        if valid:
            if left != right:
                raise AssertionError(
                    ("product", p, n, hidden_scalar, left, right)
                )
            multiplicative_section_checks += 1

    beta, eigenvalue = glv_parameters(points, p, n)

    def orbit_character(scalar: int) -> int:
        return (
            point_characters[scalar % n]
            * point_characters[(eigenvalue * scalar) % n]
            * point_characters[(eigenvalue * eigenvalue * scalar) % n]
        )

    glv_orbit_checks = 0
    for scalar in range(1, n):
        orbit_scalars = (
            scalar,
            eigenvalue * scalar % n,
            eigenvalue * eigenvalue * scalar % n,
        )
        for index in indices:
            left = 1
            for orbit_scalar in orbit_scalars:
                left *= qc(evaluators[orbit_scalar](index), p)
            right = orbit_character(index * scalar % n)
            if index & 1:
                right *= orbit_character(scalar)
            if left != right:
                raise AssertionError(
                    ("glv", p, n, scalar, index, left, right)
                )
            glv_orbit_checks += 1

    glv_multiplicative_section_checks = 0
    for _ in range(GLV_PRODUCT_TRIALS):
        hidden_scalar = rng.randrange(1, n)
        left = 1
        right = 1
        orbit_scalars = (
            hidden_scalar,
            eigenvalue * hidden_scalar % n,
            eigenvalue * eigenvalue * hidden_scalar % n,
        )
        for _ in range(rng.randrange(1, 6)):
            pullback = rng.randrange(1, n)
            index = rng.choice(indices)
            exponent = rng.randrange(-3, 4)
            if not (exponent & 1):
                continue
            for orbit_scalar in orbit_scalars:
                left *= qc(
                    evaluators[(pullback * orbit_scalar) % n](index),
                    p,
                )
            right *= orbit_character(index * pullback * hidden_scalar % n)
            if index & 1:
                right *= orbit_character(pullback * hidden_scalar % n)
        if left != right:
            raise AssertionError(
                ("glv_product", p, n, hidden_scalar, left, right)
            )
        glv_multiplicative_section_checks += 1

    return {
        "p": p,
        "order": n,
        "generator": list(generator),
        "beta": beta,
        "lambda": eigenvalue,
        "indices_tested": len(indices),
        "raw_field_checks": raw_field_checks,
        "single_factor_checks": single_factor_checks,
        "multiplicative_section_checks": multiplicative_section_checks,
        "glv_orbit_checks": glv_orbit_checks,
        "glv_multiplicative_section_checks": (
            glv_multiplicative_section_checks
        ),
        "all_passed": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "point_function_coboundary_results.json"
        ),
    )
    args = parser.parse_args()

    cases = [run_case(*case) for case in FROZEN_CASES]
    result = {
        "scope": (
            "fifteen frozen prime-order j=0 toy subgroups on "
            "y^2=x^3+7 only"
        ),
        "package": "POINT-FUNCTION-COBOUNDARY-005A",
        "point_character": "C(P)=chi(phi_raw(P))",
        "raw_field_identity": (
            "phi_raw([m]P)=phi_raw(P)^(m^2)*psi_m(P), "
            "for P != O and n not dividing m"
        ),
        "single_factor_identity": (
            "chi(psi_m(P))=C([m]P)*C(P)^(m mod 2), "
            "for P != O and n not dividing m"
        ),
        "product_identity": (
            "chi(prod_i psi_(m_i)(T_i(Q))^(e_i))="
            "prod_i C([m_i]T_i(Q))^(e_i)*"
            "C(T_i(Q))^(e_i*m_i^2)"
        ),
        "near_period_corollary": (
            "chi(psi_(r*n+a)(Q))="
            "C([a]Q)*C(Q)^((r+a) mod 2)"
        ),
        "glv_orbit_identity": (
            "prod_(j=0)^2 chi(psi_m(phi^j Q))="
            "C3([m]Q)*C3(Q)^(m mod 2)"
        ),
        "protocol": {
            "single_radius": SINGLE_RADIUS,
            "period_multiplier_radius": PERIOD_MULTIPLIER_RADIUS,
            "period_offset_radius": PERIOD_OFFSET_RADIUS,
            "product_trials_per_case": PRODUCT_TRIALS,
            "glv_product_trials_per_case": GLV_PRODUCT_TRIALS,
            "deterministic_seed": "20260812+p+n",
        },
        "cases": cases,
        "aggregate": {
            "cases": len(cases),
            "raw_field_checks": sum(
                case["raw_field_checks"] for case in cases
            ),
            "single_factor_checks": sum(
                case["single_factor_checks"] for case in cases
            ),
            "multiplicative_section_checks": sum(
                case["multiplicative_section_checks"] for case in cases
            ),
            "glv_orbit_checks": sum(
                case["glv_orbit_checks"] for case in cases
            ),
            "glv_multiplicative_section_checks": sum(
                case["glv_multiplicative_section_checks"]
                for case in cases
            ),
            "all_passed": all(case["all_passed"] for case in cases),
        },
        "claim_boundary": [
            (
                "The frozen full-field replay supports the raw transport "
                "law, but its source-normalization discrepancy remains under "
                "independent review."
            ),
            (
                "Zeros are excluded: P and [m]P must be nonidentity so the "
                "quadratic character is binary."
            ),
            (
                "This closes finite multiplicative products and ratios of "
                "ordinary division-polynomial values as a source of a new "
                "character equation; it does not close sums, derivatives, "
                "determinants, theta/sigma monodromy, or algorithms using "
                "the public C-values themselves."
            ),
            (
                "No external point, key, wallet, or production-sized target "
                "is accepted."
            ),
        ],
    }
    args.out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
