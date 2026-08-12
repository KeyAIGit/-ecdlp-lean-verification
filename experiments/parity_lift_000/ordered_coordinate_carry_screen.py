#!/usr/bin/env python3
"""Toy-only ordered-coordinate escape screen for GLOBAL-MONODROMY-SECTION-009.

The global cyclotomic carry is an Archimedean sign. This script tests the
closest directly public finite-field analogue outside the algebraic C_quad
category: signs of centered integer representatives

    sgn_p(y(Q))
    sgn_p(y(Q) * (x(Q)^3 + a)), a in F_p.

The family is evaluated against matched random anti-Kummer/C3-invariant labels.
No external point, key, wallet, or production target is accepted.
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
    sign_vector_to_bits,
)

NULL_TRIALS = 200


def centered_sign(value: int, p: int) -> int:
    value %= p
    if value == 0:
        return 0
    return 1 if value <= (p - 1) // 2 else -1


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


@dataclass(frozen=True)
class CaseResult:
    p: int
    order: int
    generator: tuple[int, int]
    lam: int
    candidate_vectors: int
    y_centered_accuracy: float
    best_accuracy: float
    best_candidate: str
    exact_decoder: str | None
    null_trials: int
    null_median: float
    null_q95: float
    empirical_null_percentile: float


def run_case(p: int, order: int, generator: tuple[int, int]) -> CaseResult:
    points = orbit(generator, order, p)
    beta = primitive_cube_root(p)
    point_to_scalar = {point: scalar for scalar, point in enumerate(points)}
    lam = point_to_scalar[(beta * generator[0] % p, generator[1])]
    lam2 = lam * lam % order

    carry = []
    y_center = []
    coordinates = []
    for scalar in range(1, order):
        total = scalar + lam * scalar % order + lam2 * scalar % order
        if total not in (order, 2 * order):
            raise AssertionError("invalid GLV carry")
        carry.append(1 if total == 2 * order else -1)
        point = points[scalar]
        assert point is not None
        x, y = point
        y_center.append(centered_sign(y, p))
        coordinates.append((pow(x, 3, p), y))

    target = sign_vector_to_bits(carry)
    length = order - 1
    complement = (1 << length) - 1
    y_vector = sign_vector_to_bits(y_center)

    candidates: dict[int, str] = {y_vector: "centered(y)"}
    for shift in range(p):
        signs = []
        for u, y in coordinates:
            sign = centered_sign(y * ((u + shift) % p), p)
            if sign == 0:
                break
            signs.append(sign)
        else:
            candidates.setdefault(
                sign_vector_to_bits(signs),
                f"centered(y*(u+{shift}))",
            )

    observed = best_accuracy(candidates, target, length)
    y_distance = (y_vector ^ target).bit_count()
    y_accuracy = max(y_distance, length - y_distance) / length

    exact = None
    for vector, name in candidates.items():
        if vector == target or vector ^ complement == target:
            exact = name
            break

    rng = random.Random(20260812 + p + order + 909)
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
        lam=lam,
        candidate_vectors=len(candidates),
        y_centered_accuracy=y_accuracy,
        best_accuracy=observed[0],
        best_candidate=observed[1],
        exact_decoder=exact,
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
        default=Path(__file__).with_name("ordered_coordinate_carry_results.json"),
    )
    args = parser.parse_args()
    cases = [run_case(*case) for case in FROZEN_CASES]
    payload = {
        "package": "GLOBAL-MONODROMY-SECTION-009",
        "subscreen": "ordered-coordinate carry escape",
        "scope": "fifteen frozen toy j=0 prime-order subgroups only",
        "family": "centered(y) and centered(y*(x^3+shift))",
        "cases": [asdict(case) for case in cases],
        "aggregate": {
            "cases": len(cases),
            "exact_decoders": sum(
                case.exact_decoder is not None for case in cases
            ),
            "exact_decoders_order_at_least_271": sum(
                case.exact_decoder is not None and case.order >= 271
                for case in cases
            ),
            "cases_strictly_above_matched_null_q95": sum(
                case.best_accuracy > case.null_q95 for case in cases
            ),
            "largest_order": max(case.order for case in cases),
        },
        "conclusion": (
            "The centered-coordinate family escapes algebraic quadratic-character "
            "rigidity but shows no stable scaling law and no exact decoder at order >=271."
        ),
        "claim_boundary": [
            "The screen is bounded toy evidence, not a no-go theorem.",
            "The shift is fitted over the full toy field and is not a sub-sqrt construction.",
            "No external or production target is accepted.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
