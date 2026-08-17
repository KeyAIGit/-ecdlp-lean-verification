#!/usr/bin/env python3
"""Toy-only boundary screen for GLV-NORMALIZATION-RIGIDITY-008.

The theorem-first part of the package shows that a homogeneous algebraic
net/theta section with quadratic normalization exponent

    q(k) = a*k^2 + b*k + c

has C3 carry coefficient a+b mod 2.  This script exhaustively replays that
parity identity on the frozen j=0 toy groups and checks the smallest
weight-zero anti-Kummer escape family

    chi(y(Q) * (x(Q)^3 + shift)).

No external curve, point, key, wallet, or production-sized target is accepted.
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
    orbit,
    primitive_cube_root,
    quadratic_character,
    sign_vector_to_bits,
)

NULL_TRIALS = 200


@dataclass(frozen=True)
class CaseResult:
    p: int
    order: int
    generator: tuple[int, int]
    beta: int
    lam: int
    quadratic_orbit_parity_checks: int
    invariant_linear_factors: int
    single_anti_kummer_candidates: int
    y_only_accuracy: float
    best_single_accuracy: float
    best_single_candidate: str
    best_single_matches: int
    exact_single_decoder: str | None
    exact_degree_two_decoder: tuple[int, int, int] | None
    null_trials: int
    null_median: float
    null_q95: float
    empirical_null_percentile: float


def random_anti_c6_target(order: int, lam: int, rng: random.Random) -> int:
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
        visited.update(positive)
        visited.update(negative)
    return sign_vector_to_bits(values[1:])


def best_accuracy(candidates: dict[int, str], target: int, length: int):
    best = (0.5, "", 0)
    for vector, name in candidates.items():
        distance = (vector ^ target).bit_count()
        matches = max(distance, length - distance)
        accuracy = matches / length
        if accuracy > best[0] or (accuracy == best[0] and name < best[1]):
            best = (accuracy, name, matches)
    return best


def run_case(p: int, order: int, generator: tuple[int, int]) -> CaseResult:
    points = orbit(generator, order, p)
    beta = primitive_cube_root(p)
    point_to_scalar = {point: scalar for scalar, point in enumerate(points)}
    lam = point_to_scalar[(beta * generator[0] % p, generator[1])]
    lam2 = lam * lam % order

    carry_signs: list[int] = []
    y_signs: list[int] = []
    invariant_coordinates: list[int] = []
    parity_checks = 0

    for scalar in range(1, order):
        first = lam * scalar % order
        second = lam2 * scalar % order
        total = scalar + first + second
        if total not in (order, 2 * order):
            raise AssertionError("GLV representatives do not sum to n or 2n")
        gamma = total // order

        if (scalar * scalar + first * first + second * second - gamma) % 2:
            raise AssertionError("square-orbit carry parity failed")

        for a in range(-2, 3):
            for b in range(-2, 3):
                for c in range(-1, 2):
                    lhs = (
                        a * scalar * scalar + b * scalar + c
                        + a * first * first + b * first + c
                        + a * second * second + b * second + c
                    )
                    rhs = (a + b) * gamma + c
                    if (lhs - rhs) % 2:
                        raise AssertionError("quadratic normalization parity failed")
                    parity_checks += 1

        carry_signs.append(1 if gamma == 2 else -1)
        point = points[scalar]
        assert point is not None
        x, y = point
        y_signs.append(quadratic_character(y, p))
        invariant_coordinates.append(pow(x, 3, p))

    target = sign_vector_to_bits(carry_signs)
    y_vector = sign_vector_to_bits(y_signs)
    length = order - 1
    complement = (1 << length) - 1

    invariant_factors: dict[int, int] = {}
    for shift in range(p):
        signs: list[int] = []
        for coordinate in invariant_coordinates:
            sign = quadratic_character(coordinate + shift, p)
            if sign == 0:
                break
            signs.append(sign)
        else:
            invariant_factors.setdefault(sign_vector_to_bits(signs), shift)

    candidates: dict[int, str] = {y_vector: "y"}
    for vector, shift in invariant_factors.items():
        candidates.setdefault(y_vector ^ vector, f"y*(u+{shift})")

    observed = best_accuracy(candidates, target, length)
    y_distance = (y_vector ^ target).bit_count()
    y_accuracy = max(y_distance, length - y_distance) / length

    exact_single: str | None = None
    for vector, name in candidates.items():
        if vector == target or vector ^ complement == target:
            exact_single = name
            break

    # An exact non-degenerate weight-two candidate can be detected without
    # enumerating all O(p^2) pairs. Repeating the same factor is excluded:
    # its quadratic character squares to the constant +1 on the admitted
    # nonvanishing domain and therefore does not constitute a second factor.
    desired = target ^ y_vector
    exact_pair: tuple[int, int, int] | None = None
    for vector, first_shift in invariant_factors.items():
        positive = desired ^ vector
        if positive != vector and positive in invariant_factors:
            exact_pair = (first_shift, invariant_factors[positive], 1)
            break
        negative = desired ^ complement ^ vector
        if negative != vector and negative in invariant_factors:
            exact_pair = (first_shift, invariant_factors[negative], -1)
            break

    rng = random.Random(20260812 + p + order + 808)
    null = [
        best_accuracy(
            candidates,
            random_anti_c6_target(order, lam, rng),
            length,
        )[0]
        for _ in range(NULL_TRIALS)
    ]
    null.sort()
    q95 = null[math.ceil(0.95 * NULL_TRIALS) - 1]

    return CaseResult(
        p=p,
        order=order,
        generator=generator,
        beta=beta,
        lam=lam,
        quadratic_orbit_parity_checks=parity_checks,
        invariant_linear_factors=len(invariant_factors),
        single_anti_kummer_candidates=len(candidates),
        y_only_accuracy=y_accuracy,
        best_single_accuracy=observed[0],
        best_single_candidate=observed[1],
        best_single_matches=observed[2],
        exact_single_decoder=exact_single,
        exact_degree_two_decoder=exact_pair,
        null_trials=NULL_TRIALS,
        null_median=statistics.median(null),
        null_q95=q95,
        empirical_null_percentile=(
            sum(value <= observed[0] for value in null) / NULL_TRIALS
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "glv_normalization_rigidity_results.json"
        ),
    )
    args = parser.parse_args()

    cases = [run_case(*case) for case in FROZEN_CASES]
    payload = {
        "scope": (
            "fifteen frozen j=0 prime-order toy subgroups; "
            "no external or production target"
        ),
        "package": "GLV-NORMALIZATION-RIGIDITY-008",
        "theorem_replayed": (
            "sum_i q(k_i) = (a+b)*gamma+c mod 2 for "
            "q(k)=a*k^2+b*k+c"
        ),
        "weight_zero_boundary_family": (
            "chi(y(Q)) and chi(y(Q)*(x(Q)^3+shift))"
        ),
        "cases": [asdict(case) for case in cases],
        "aggregate": {
            "cases": len(cases),
            "quadratic_orbit_parity_checks": sum(
                case.quadratic_orbit_parity_checks for case in cases
            ),
            "exact_single_decoders": sum(
                case.exact_single_decoder is not None for case in cases
            ),
            "exact_degree_two_decoders": sum(
                case.exact_degree_two_decoder is not None for case in cases
            ),
            "exact_decoders_order_at_least_271": sum(
                (
                    case.exact_single_decoder is not None
                    or case.exact_degree_two_decoder is not None
                )
                and case.order >= 271
                for case in cases
            ),
            "cases_strictly_above_matched_null_q95": sum(
                case.best_single_accuracy > case.null_q95 for case in cases
            ),
            "largest_order": max(case.order for case in cases),
        },
        "conclusion": (
            "The quadratic normalization identity held exactly. The smallest "
            "weight-zero anti-Kummer escape family produced finite small-order "
            "resonances only: no exact decoder at order >=271 and no case "
            "strictly above the matched 95% null envelope."
        ),
        "claim_boundary": [
            "The parity identity is exact; the coordinate screen is bounded toy evidence.",
            "The rigidity theorem covers homogeneous quadratic-normalized net/theta sections, not arbitrary mixed-weight rational circuits.",
            "No external point, key, wallet, or production-sized target is accepted.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
