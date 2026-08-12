#!/usr/bin/env python3
"""Toy-only screen for a non-algebraic CM coordinate carry decoder.

This package tests a public integer-lift observable that lies outside the
homogeneous quadratic-normalization category.  On a j=0 GLV orbit, the three
x-coordinates are x, beta*x, beta^2*x.  Their canonical integer representatives
sum to p or 2p, producing a public field-coordinate carry.  Multiplication by an
anti-Kummer y-orientation gives the same C3 and negation symmetries as the
hidden scalar GLV carry.

The script accepts no external curve, point, key, wallet, or production-sized
target.  It uses only the frozen toy subgroups already committed for
PARITY-LIFT-000.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
from dataclasses import asdict, dataclass
from pathlib import Path

from nonlocal_odd_anchor_screen import (
    FROZEN_CASES,
    division_polynomial_evaluator,
    orbit,
    primitive_cube_root,
    quadratic_character,
)

NULL_TRIALS = 400


def best_accuracy(candidates: dict[str, list[int]], target: list[int]) -> tuple[float, str, int]:
    total = len(target)
    best = (0.5, "", total // 2)
    for name, values in candidates.items():
        raw = sum(left == right for left, right in zip(values, target))
        matches = max(raw, total - raw)
        accuracy = matches / total
        if accuracy > best[0] or (accuracy == best[0] and name < best[1]):
            best = (accuracy, name, matches)
    return best


def scalar_carry_sign(k: int, lam: int, order: int) -> int:
    first = lam * k % order
    second = lam * first % order
    total = k + first + second
    if total == order:
        return -1
    if total == 2 * order:
        return 1
    raise AssertionError("canonical scalar GLV representatives did not sum to n or 2n")


def coordinate_carry_sign(x: int, beta: int, p: int) -> int:
    first = beta * x % p
    second = beta * first % p
    total = x + first + second
    if total == p:
        return -1
    if total == 2 * p:
        return 1
    raise AssertionError("canonical field GLV representatives did not sum to p or 2p")


def half_sign(value: int, modulus: int) -> int:
    value %= modulus
    if value == 0:
        raise AssertionError("half orientation is undefined at zero")
    return 1 if 2 * value < modulus else -1


def permutation_orientation(values: tuple[int, int, int]) -> int:
    left, middle, right = values
    product = (left - middle) * (middle - right) * (right - left)
    if product == 0:
        raise AssertionError("GLV coordinate orbit collided")
    return 1 if product > 0 else -1


def random_anti_c6(order: int, lam: int, rng: random.Random) -> list[int]:
    values = [0] * order
    visited: set[int] = set()
    lam2 = lam * lam % order
    for scalar in range(1, order):
        if scalar in visited:
            continue
        positive = {scalar, lam * scalar % order, lam2 * scalar % order}
        negative = {order - member for member in positive}
        sign = -1 if rng.getrandbits(1) else 1
        for member in positive:
            values[member] = sign
        for member in negative:
            values[member] = -sign
        visited.update(positive | negative)
    return values[1:]


def random_kummer_c6(order: int, lam: int, rng: random.Random) -> list[int]:
    values = [0] * order
    visited: set[int] = set()
    lam2 = lam * lam % order
    for scalar in range(1, order):
        if scalar in visited:
            continue
        orbit6 = {
            scalar,
            order - scalar,
            lam * scalar % order,
            order - (lam * scalar % order),
            lam2 * scalar % order,
            order - (lam2 * scalar % order),
        }
        sign = -1 if rng.getrandbits(1) else 1
        for member in orbit6:
            values[member] = sign
        visited.update(orbit6)
    return values[1:]


@dataclass(frozen=True)
class CaseResult:
    p: int
    order: int
    generator: tuple[int, int]
    beta: int
    lam: int
    rho_kummer_invariant: bool
    scalar_carry_checks: int
    coordinate_carry_checks: int
    carry_candidate_count: int
    carry_best_accuracy: float
    carry_best_candidate: str
    carry_best_matches: int
    carry_exact_decoder: bool
    carry_null_trials: int
    carry_null_median: float
    carry_null_q95: float
    carry_empirical_null_percentile: float
    r3_candidate_count: int
    r3_best_accuracy: float
    r3_best_candidate: str
    r3_best_matches: int
    r3_exact_decoder: bool
    r3_null_trials: int
    r3_null_median: float
    r3_null_q95: float
    r3_empirical_null_percentile: float


def run_case(p: int, order: int, generator: tuple[int, int]) -> CaseResult:
    points = orbit(generator, order, p)
    beta = primitive_cube_root(p)
    point_to_scalar = {point: scalar for scalar, point in enumerate(points)}
    lam = point_to_scalar[(beta * generator[0] % p, generator[1])]
    lam2 = lam * lam % order

    psi = division_polynomial_evaluator(generator, p)
    rho = [0] + [quadratic_character(psi(k), p) for k in range(1, order)]
    if any(value not in (-1, 1) for value in rho[1:]):
        raise AssertionError("EDS residue vanished off the identity")
    rho_kummer = all(rho[k] == rho[order - k] for k in range(1, order))

    target_carry: list[int] = []
    target_r3: list[int] = []
    field_carry: list[int] = []
    field_permutation: list[int] = []
    y_half: list[int] = []
    y_character: list[int] = []
    x_half_orbit_product: list[int] = []

    for k in range(1, order):
        point = points[k]
        assert point is not None
        x, y = point

        target_carry.append(scalar_carry_sign(k, lam, order))
        target_r3.append(rho[k] * rho[lam * k % order] * rho[lam2 * k % order])

        x1 = beta * x % p
        x2 = beta * x1 % p
        field_carry.append(coordinate_carry_sign(x, beta, p))
        field_permutation.append(permutation_orientation((x, x1, x2)))
        y_half.append(half_sign(y, p))
        y_character.append(quadratic_character(y, p))
        x_half_orbit_product.append(half_sign(x, p) * half_sign(x1, p) * half_sign(x2, p))

    carry_candidates = {
        "half_y": y_half,
        "chi_y": y_character,
        "field_carry*half_y": [a * b for a, b in zip(field_carry, y_half)],
        "field_carry*chi_y": [a * b for a, b in zip(field_carry, y_character)],
        "field_permutation*half_y": [a * b for a, b in zip(field_permutation, y_half)],
        "field_permutation*chi_y": [a * b for a, b in zip(field_permutation, y_character)],
        "field_carry*field_permutation*half_y": [
            a * b * c for a, b, c in zip(field_carry, field_permutation, y_half)
        ],
        "field_carry*field_permutation*chi_y": [
            a * b * c for a, b, c in zip(field_carry, field_permutation, y_character)
        ],
        "x_half_orbit_product*half_y": [
            a * b for a, b in zip(x_half_orbit_product, y_half)
        ],
        "x_half_orbit_product*chi_y": [
            a * b for a, b in zip(x_half_orbit_product, y_character)
        ],
    }

    r3_candidates = {
        "field_carry": field_carry,
        "field_permutation": field_permutation,
        "x_half_orbit_product": x_half_orbit_product,
        "field_carry*field_permutation": [
            a * b for a, b in zip(field_carry, field_permutation)
        ],
        "field_carry*x_half_orbit_product": [
            a * b for a, b in zip(field_carry, x_half_orbit_product)
        ],
        "field_permutation*x_half_orbit_product": [
            a * b for a, b in zip(field_permutation, x_half_orbit_product)
        ],
    }

    carry_observed = best_accuracy(carry_candidates, target_carry)
    r3_observed = best_accuracy(r3_candidates, target_r3)

    rng = random.Random(20260812 + 17 * p + order)
    carry_null = sorted(
        best_accuracy(carry_candidates, random_anti_c6(order, lam, rng))[0]
        for _ in range(NULL_TRIALS)
    )
    carry_q95 = carry_null[math.ceil(0.95 * NULL_TRIALS) - 1]

    if rho_kummer:
        r3_null = sorted(
            best_accuracy(r3_candidates, random_kummer_c6(order, lam, rng))[0]
            for _ in range(NULL_TRIALS)
        )
        r3_q95 = r3_null[math.ceil(0.95 * NULL_TRIALS) - 1]
        r3_median = statistics.median(r3_null)
        r3_percentile = sum(value <= r3_observed[0] for value in r3_null) / NULL_TRIALS
    else:
        r3_null = []
        r3_q95 = 0.0
        r3_median = 0.0
        r3_percentile = 0.0

    return CaseResult(
        p=p,
        order=order,
        generator=generator,
        beta=beta,
        lam=lam,
        rho_kummer_invariant=rho_kummer,
        scalar_carry_checks=order - 1,
        coordinate_carry_checks=order - 1,
        carry_candidate_count=len(carry_candidates),
        carry_best_accuracy=carry_observed[0],
        carry_best_candidate=carry_observed[1],
        carry_best_matches=carry_observed[2],
        carry_exact_decoder=carry_observed[0] == 1.0,
        carry_null_trials=NULL_TRIALS,
        carry_null_median=statistics.median(carry_null),
        carry_null_q95=carry_q95,
        carry_empirical_null_percentile=(
            sum(value <= carry_observed[0] for value in carry_null) / NULL_TRIALS
        ),
        r3_candidate_count=len(r3_candidates),
        r3_best_accuracy=r3_observed[0],
        r3_best_candidate=r3_observed[1],
        r3_best_matches=r3_observed[2],
        r3_exact_decoder=r3_observed[0] == 1.0,
        r3_null_trials=NULL_TRIALS if rho_kummer else 0,
        r3_null_median=r3_median,
        r3_null_q95=r3_q95,
        r3_empirical_null_percentile=r3_percentile,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("cm_coordinate_carry_results.json"),
    )
    args = parser.parse_args()

    cases = [run_case(*case) for case in FROZEN_CASES]
    large = [case for case in cases if case.order >= 500]
    kummer = [case for case in cases if case.rho_kummer_invariant]

    payload = {
        "scope": (
            "fifteen frozen j=0 prime-order toy subgroups; "
            "no external point, key, wallet, or production target"
        ),
        "package": "CM-COORDINATE-CARRY-010",
        "public_field_carry": (
            "delta_x(Q)=(rep(x)+rep(beta*x)+rep(beta^2*x))/p in {1,2}"
        ),
        "target_scalar_carry": (
            "gamma(k)=(k+rep(lambda*k)+rep(lambda^2*k))/n in {1,2}"
        ),
        "cases": [asdict(case) for case in cases],
        "aggregate": {
            "cases": len(cases),
            "scalar_carry_checks": sum(case.scalar_carry_checks for case in cases),
            "coordinate_carry_checks": sum(case.coordinate_carry_checks for case in cases),
            "exact_carry_decoders": sum(case.carry_exact_decoder for case in cases),
            "carry_cases_strictly_above_matched_null_q95": sum(
                case.carry_best_accuracy > case.carry_null_q95 for case in cases
            ),
            "large_order_mean_carry_accuracy": sum(
                case.carry_best_accuracy for case in large
            ) / len(large),
            "large_order_max_carry_excess_times_sqrt_order": max(
                (case.carry_best_accuracy - 0.5) * math.sqrt(case.order)
                for case in large
            ),
            "kummer_cases": len(kummer),
            "exact_r3_decoders_on_kummer_cases": sum(
                case.r3_exact_decoder for case in kummer
            ),
            "r3_cases_strictly_above_matched_null_q95": sum(
                case.r3_best_accuracy > case.r3_null_q95 for case in kummer
            ),
            "largest_order": max(case.order for case in cases),
        },
        "decision_rule": (
            "A scaling signal requires either an exact family identity or repeated "
            "strict exceedance of the matched 95% null envelope as order grows."
        ),
        "claim_boundary": [
            "Integer representative comparisons are public but model-dependent and non-algebraic.",
            "The screen is bounded cross-order evidence, not an asymptotic theorem.",
            "No external or production-sized input is accepted.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
