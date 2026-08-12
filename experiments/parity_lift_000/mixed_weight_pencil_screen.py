#!/usr/bin/env python3
"""Toy-only mixed-weight section screen for GLOBAL-MONODROMY-SECTION-009.

Products and ratios of fixed division-polynomial sections preserve the
quadratic EDS gauge.  This script tests the smallest nonlinear class not covered
by that multiplicative no-go: every quadratic character in a public two-section
pencil

    chi(psi_a(Q) + c*psi_b(Q)),  c in F_p union {infinity}.

Odd/odd pencils are Kummer invariant and are tested against the residual EDS
bit.  Even/even pencils are anti-Kummer and are tested against the GLV carry.
A smaller structured odd/odd family is also normed over the order-three GLV
orbit and tested directly against R3.

The coefficient c is exhaustively optimized in every retained pencil.  Matched
random controls use the identical candidate selection procedure, so the large
look-elsewhere effect is included.  No external curve, point, key, wallet, or
production-sized target is accepted.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional

import numpy as np

Point = Optional[tuple[int, int]]
B = 7
NULL_TRIALS = 64
R3_NULL_TRIALS = 32
SMALL_INDEX_MAX = 12
NEAR_ORDER_RADIUS = 4
R3_CORE_LIMIT = 18

FROZEN_CASES = (
    (43, 31, (2, 12)),
    (79, 67, (1, 18)),
    (151, 19, (70, 122)),
    (547, 547, (2, 62)),
    (907, 967, (2, 165)),
    (1051, 1093, (3, 385)),
    (1087, 271, (1017, 688)),
    (1303, 1249, (1, 201)),
    (1663, 433, (126, 1375)),
    (2347, 571, (2107, 1535)),
    (2671, 367, (83, 2009)),
    (2851, 397, (2276, 1015)),
    (3319, 811, (177, 298)),
    (3571, 3469, (4, 1706)),
    (3931, 4021, (4, 1427)),
)


def ec_add(left: Point, right: Point, p: int) -> Point:
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if left == right:
        if y1 % p == 0:
            return None
        slope = 3 * x1 * x1 * pow(2 * y1, -1, p) % p
    else:
        slope = (y2 - y1) * pow((x2 - x1) % p, -1, p) % p
    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    return x3, y3


def orbit(generator: tuple[int, int], order: int, p: int) -> list[Point]:
    points: list[Point] = [None]
    point: Point = None
    for _ in range(1, order):
        point = ec_add(point, generator, p)
        points.append(point)
    if ec_add(point, generator, p) is not None:
        raise AssertionError("declared order failed")
    if len(set(points)) != order:
        raise AssertionError("early orbit collision")
    return points


def quadratic_character(value: int, p: int) -> int:
    value %= p
    if value == 0:
        return 0
    return 1 if pow(value, (p - 1) // 2, p) == 1 else -1


def division_polynomial_evaluator(point: tuple[int, int], p: int):
    x, y = point

    @lru_cache(maxsize=None)
    def psi(index: int) -> int:
        if index < 0:
            return -psi(-index) % p
        if index == 0:
            return 0
        if index == 1:
            return 1
        if index == 2:
            return 2 * y % p
        if index == 3:
            return (3 * x**4 + 84 * x) % p
        if index == 4:
            return 4 * y * (x**6 + 140 * x**3 - 392) % p
        if index & 1:
            m = (index - 1) // 2
            return (
                psi(m + 2) * pow(psi(m), 3, p)
                - psi(m - 1) * pow(psi(m + 1), 3, p)
            ) % p
        m = index // 2
        return (
            psi(m)
            * pow(2 * y, -1, p)
            * (
                psi(m + 2) * pow(psi(m - 1), 2, p)
                - psi(m - 2) * pow(psi(m + 1), 2, p)
            )
        ) % p

    return psi


def primitive_cube_root(p: int) -> int:
    if (p - 1) % 3:
        raise AssertionError("field has no primitive cube root")
    for seed in range(2, p):
        beta = pow(seed, (p - 1) // 3, p)
        if beta != 1 and pow(beta, 3, p) == 1:
            return beta
    raise AssertionError("primitive cube root not found")


def structured_indices(p: int, order: int, lam: int) -> list[int]:
    values = set(range(1, min(SMALL_INDEX_MAX, order - 1) + 1))
    for delta in range(1, NEAR_ORDER_RADIUS + 1):
        for value in (order - delta, order + delta):
            if value > 0 and value % order:
                values.add(value)

    lam2 = lam * lam % order
    for centre in (lam, lam2, order - lam, order - lam2):
        for delta in range(-2, 3):
            value = centre + delta
            if value > 0 and value % order:
                values.add(value)

    special = (
        (order - 1) // 2,
        (order + 1) // 2,
        (order - 1) // 3,
        (2 * order + 1) // 3,
        math.isqrt(order),
        math.isqrt(order) + 1,
        abs(p - order),
        p % order,
        (p - 1) % order,
        (p + 1) % order,
        p - 1,
        p,
        p + 1,
    )
    for value in special:
        if value > 0 and value % order:
            values.add(value)
    return sorted(values)


def nearest_odd_nonmultiple(value: int, order: int) -> int:
    value = max(1, value)
    if value % 2 == 0:
        value += 1
    if value % order == 0:
        value += 2
    return value


def r3_core_indices(p: int, order: int, lam: int) -> list[int]:
    lam2 = lam * lam % order
    seeds = [
        1,
        3,
        5,
        7,
        9,
        11,
        order - 4,
        order - 2,
        order + 2,
        order + 4,
        (order - 1) // 2,
        (order + 1) // 2,
        (2 * order + 1) // 3,
        p,
        abs(p - order) + 1,
        math.isqrt(order),
        lam,
        lam2,
    ]
    result: list[int] = []
    seen: set[int] = set()
    for seed in seeds:
        value = nearest_odd_nonmultiple(seed, order)
        if value not in seen:
            seen.add(value)
            result.append(value)
        if len(result) >= R3_CORE_LIMIT:
            break
    return result


def legendre_table(p: int) -> np.ndarray:
    return np.array(
        [quadratic_character(value, p) for value in range(p)],
        dtype=np.int16,
    )


def random_kummer_targets(
    order: int, trials: int, rng: random.Random
) -> np.ndarray:
    targets = np.ones((trials, order - 1), dtype=np.int16)
    for trial in range(trials):
        for scalar in range(1, (order + 1) // 2):
            sign = -1 if rng.getrandbits(1) else 1
            targets[trial, scalar - 1] = sign
            targets[trial, order - scalar - 1] = sign
    return targets


def random_anti_c6_targets(
    order: int, lam: int, trials: int, rng: random.Random
) -> np.ndarray:
    targets = np.zeros((trials, order - 1), dtype=np.int16)
    lam2 = lam * lam % order
    for trial in range(trials):
        visited: set[int] = set()
        for scalar in range(1, order):
            if scalar in visited:
                continue
            positive = {
                scalar,
                lam * scalar % order,
                lam2 * scalar % order,
            }
            negative = {order - member for member in positive}
            sign = -1 if rng.getrandbits(1) else 1
            for member in positive:
                targets[trial, member - 1] = sign
            for member in negative:
                targets[trial, member - 1] = -sign
            visited.update(positive)
            visited.update(negative)
    return targets


def q95(values: list[float]) -> float:
    ordered = sorted(values)
    return ordered[math.ceil(0.95 * len(ordered)) - 1]


@dataclass(frozen=True)
class PencilScore:
    status: str
    section_parity: str
    indices: int
    pencils: int
    exact_decoder: bool
    best_accuracy: float
    best_a: int | None
    best_b: int | None
    best_c: int | None
    best_global_sign: int | None
    null_trials: int
    null_median: float
    null_q95: float
    empirical_null_percentile: float


def evaluate_direct_pencils(
    values: np.ndarray,
    indices: list[int],
    observed_target: np.ndarray,
    controls: np.ndarray,
    p: int,
    parity: int,
) -> PencilScore:
    targets = np.vstack((observed_target.astype(np.int16), controls))
    trials, length = targets.shape
    legendre = legendre_table(p)
    legendre_fft = np.fft.fft(legendre)
    best_correlation = np.zeros(trials, dtype=np.int64)
    best_metadata: list[tuple[int, int, int | None, int] | None] = [
        None
    ] * trials
    pencils = 0

    row_index = np.repeat(np.arange(trials), length)

    for left_index, a in enumerate(indices):
        if a % 2 != parity:
            continue
        for right_index in range(left_index + 1, len(indices)):
            b = indices[right_index]
            if b % 2 != parity:
                continue
            left = values[left_index]
            right = values[right_index]
            if np.any(right == 0):
                continue

            inverse_right = np.array(
                [pow(int(value), -1, p) for value in right],
                dtype=np.int64,
            )
            roots = (-left * inverse_right) % p
            base_sign = np.array(
                [quadratic_character(int(value), p) for value in right],
                dtype=np.int16,
            )
            weights = targets * base_sign[None, :]

            histogram = np.zeros((trials, p), dtype=np.int32)
            column_index = np.tile(roots, trials)
            np.add.at(
                histogram,
                (row_index, column_index),
                weights.ravel(),
            )
            correlations = np.rint(
                np.fft.ifft(
                    np.fft.fft(histogram, axis=1) * legendre_fft[None, :],
                    axis=1,
                ).real
            ).astype(np.int64)

            root_counts = np.bincount(roots, minlength=p)
            valid_coefficients = np.where(root_counts == 0)[0]
            if valid_coefficients.size:
                valid_correlations = np.abs(
                    correlations[:, valid_coefficients]
                )
                argmax = np.argmax(valid_correlations, axis=1)
                candidate_values = valid_correlations[
                    np.arange(trials), argmax
                ]
                for trial in np.where(
                    candidate_values > best_correlation
                )[0]:
                    coefficient = int(valid_coefficients[argmax[trial]])
                    raw = int(correlations[trial, coefficient])
                    best_correlation[trial] = abs(raw)
                    best_metadata[trial] = (
                        a,
                        b,
                        coefficient,
                        1 if raw >= 0 else -1,
                    )

            infinity_raw = weights.sum(axis=1, dtype=np.int64)
            infinity_abs = np.abs(infinity_raw)
            for trial in np.where(infinity_abs > best_correlation)[0]:
                raw = int(infinity_raw[trial])
                best_correlation[trial] = abs(raw)
                best_metadata[trial] = (
                    a,
                    b,
                    None,
                    1 if raw >= 0 else -1,
                )
            pencils += 1

    accuracies = (length + best_correlation) / (2 * length)
    observed_accuracy = float(accuracies[0])
    null = [float(value) for value in accuracies[1:]]
    metadata = best_metadata[0]
    if metadata is None:
        return PencilScore(
            status="no_admissible_pencil",
            section_parity="odd" if parity else "even",
            indices=len(indices),
            pencils=0,
            exact_decoder=False,
            best_accuracy=0.5,
            best_a=None,
            best_b=None,
            best_c=None,
            best_global_sign=None,
            null_trials=len(null),
            null_median=statistics.median(null) if null else 0.5,
            null_q95=q95(null) if null else 0.5,
            empirical_null_percentile=0.0,
        )
    a, b, coefficient, global_sign = metadata
    return PencilScore(
        status="screened",
        section_parity="odd" if parity else "even",
        indices=len(indices),
        pencils=pencils,
        exact_decoder=best_correlation[0] == length,
        best_accuracy=observed_accuracy,
        best_a=a,
        best_b=b,
        best_c=coefficient,
        best_global_sign=global_sign,
        null_trials=len(null),
        null_median=statistics.median(null),
        null_q95=q95(null),
        empirical_null_percentile=(
            sum(value <= observed_accuracy for value in null) / len(null)
        ),
    )


def c6_representatives(order: int, lam: int) -> list[tuple[int, int, int]]:
    lam2 = lam * lam % order
    visited: set[int] = set()
    representatives: list[tuple[int, int, int]] = []
    for scalar in range(1, order):
        if scalar in visited:
            continue
        positive = (
            scalar,
            lam * scalar % order,
            lam2 * scalar % order,
        )
        orbit6 = set(positive) | {order - member for member in positive}
        visited.update(orbit6)
        representatives.append(positive)
    return representatives


def evaluate_r3_orbit_pencils(
    values: np.ndarray,
    indices: list[int],
    observed_r3: np.ndarray,
    p: int,
    order: int,
    lam: int,
    rng: random.Random,
) -> PencilScore:
    representatives = c6_representatives(order, lam)
    orbit_target = np.array(
        [observed_r3[triple[0] - 1] for triple in representatives],
        dtype=np.int32,
    )
    controls = np.array(
        [
            [-1 if rng.getrandbits(1) else 1 for _ in representatives]
            for _ in range(R3_NULL_TRIALS)
        ],
        dtype=np.int32,
    )
    targets = np.vstack((orbit_target[None, :], controls))
    trials = targets.shape[0]
    legendre = legendre_table(p).astype(np.int32)
    best_correlation = np.zeros(trials, dtype=np.int64)
    best_metadata: list[tuple[int, int, int | None, int] | None] = [
        None
    ] * trials
    pencils = 0

    first = np.array([triple[0] - 1 for triple in representatives])
    second = np.array([triple[1] - 1 for triple in representatives])
    third = np.array([triple[2] - 1 for triple in representatives])

    for left_index, a in enumerate(indices):
        for right_index in range(left_index + 1, len(indices)):
            b = indices[right_index]
            left = values[left_index]
            right = values[right_index]
            if np.any(right == 0):
                continue
            inverse_right = np.array(
                [pow(int(value), -1, p) for value in right],
                dtype=np.int64,
            )
            roots = (-left * inverse_right) % p
            base = np.array(
                [quadratic_character(int(value), p) for value in right],
                dtype=np.int32,
            )
            base_orbit = base[first] * base[second] * base[third]
            root_counts = np.bincount(roots, minlength=p)
            valid = np.where(root_counts == 0)[0]

            for start in range(0, valid.size, 384):
                coefficients = valid[start : start + 384]
                if not coefficients.size:
                    continue
                column = coefficients[:, None]
                signs = (
                    legendre[(column - roots[first]) % p]
                    * legendre[(column - roots[second]) % p]
                    * legendre[(column - roots[third]) % p]
                    * base_orbit[None, :]
                )
                correlations = 6 * (targets @ signs.T)
                absolute = np.abs(correlations)
                argmax = np.argmax(absolute, axis=1)
                candidate_values = absolute[np.arange(trials), argmax]
                for trial in np.where(
                    candidate_values > best_correlation
                )[0]:
                    local = int(argmax[trial])
                    raw = int(correlations[trial, local])
                    best_correlation[trial] = abs(raw)
                    best_metadata[trial] = (
                        a,
                        b,
                        int(coefficients[local]),
                        1 if raw >= 0 else -1,
                    )

            infinity_sign = base_orbit
            infinity_raw = 6 * (targets @ infinity_sign)
            infinity_abs = np.abs(infinity_raw)
            for trial in np.where(infinity_abs > best_correlation)[0]:
                raw = int(infinity_raw[trial])
                best_correlation[trial] = abs(raw)
                best_metadata[trial] = (
                    a,
                    b,
                    None,
                    1 if raw >= 0 else -1,
                )
            pencils += 1

    length = order - 1
    accuracies = (length + best_correlation) / (2 * length)
    observed_accuracy = float(accuracies[0])
    null = [float(value) for value in accuracies[1:]]
    metadata = best_metadata[0]
    if metadata is None:
        return PencilScore(
            status="no_admissible_pencil",
            section_parity="odd_C3_orbit_norm",
            indices=len(indices),
            pencils=0,
            exact_decoder=False,
            best_accuracy=0.5,
            best_a=None,
            best_b=None,
            best_c=None,
            best_global_sign=None,
            null_trials=len(null),
            null_median=statistics.median(null) if null else 0.5,
            null_q95=q95(null) if null else 0.5,
            empirical_null_percentile=0.0,
        )
    a, b, coefficient, global_sign = metadata
    return PencilScore(
        status="screened",
        section_parity="odd_C3_orbit_norm",
        indices=len(indices),
        pencils=pencils,
        exact_decoder=best_correlation[0] == length,
        best_accuracy=observed_accuracy,
        best_a=a,
        best_b=b,
        best_c=coefficient,
        best_global_sign=global_sign,
        null_trials=len(null),
        null_median=statistics.median(null),
        null_q95=q95(null),
        empirical_null_percentile=(
            sum(value <= observed_accuracy for value in null) / len(null)
        ),
    )


@dataclass(frozen=True)
class CaseResult:
    p: int
    order: int
    generator: tuple[int, int]
    beta: int
    lam: int
    rho_kummer_invariant: bool
    structured_indices: list[int]
    carry: PencilScore
    rho: PencilScore
    r3: PencilScore


def run_case(p: int, order: int, generator: tuple[int, int]) -> CaseResult:
    points = orbit(generator, order, p)
    beta = primitive_cube_root(p)
    point_to_scalar = {point: scalar for scalar, point in enumerate(points)}
    lam = point_to_scalar[(beta * generator[0] % p, generator[1])]
    lam2 = lam * lam % order

    indices = structured_indices(p, order, lam)
    value_table = np.empty((len(indices), order - 1), dtype=np.int64)
    for scalar, point in enumerate(points[1:], 1):
        assert point is not None
        evaluator = division_polynomial_evaluator(point, p)
        for index_position, section_index in enumerate(indices):
            value = evaluator(section_index) % p
            if value == 0:
                raise AssertionError(
                    "admissible section vanished on a nonzero prime-order orbit"
                )
            value_table[index_position, scalar - 1] = value

    base_psi = division_polynomial_evaluator(generator, p)
    rho = np.array(
        [quadratic_character(base_psi(k), p) for k in range(1, order)],
        dtype=np.int16,
    )
    rho_kummer = all(
        rho[k - 1] == rho[order - k - 1] for k in range(1, order)
    )

    carry_signs: list[int] = []
    r3_signs: list[int] = []
    for scalar in range(1, order):
        first = lam * scalar % order
        second = lam2 * scalar % order
        total = scalar + first + second
        if total not in (order, 2 * order):
            raise AssertionError("GLV representatives have invalid carry")
        carry_signs.append(1 if total == 2 * order else -1)
        r3_signs.append(
            int(rho[scalar - 1] * rho[first - 1] * rho[second - 1])
        )
    carry = np.array(carry_signs, dtype=np.int16)
    r3 = np.array(r3_signs, dtype=np.int16)

    rng = random.Random(20260812 + p + order + 9)
    carry_controls = random_anti_c6_targets(
        order, lam, NULL_TRIALS, rng
    )
    carry_score = evaluate_direct_pencils(
        value_table,
        indices,
        carry,
        carry_controls,
        p,
        parity=0,
    )

    if rho_kummer:
        rho_controls = random_kummer_targets(order, NULL_TRIALS, rng)
        rho_score = evaluate_direct_pencils(
            value_table,
            indices,
            rho,
            rho_controls,
            p,
            parity=1,
        )

        core = r3_core_indices(p, order, lam)
        core_values = np.empty((len(core), order - 1), dtype=np.int64)
        for scalar, point in enumerate(points[1:], 1):
            assert point is not None
            evaluator = division_polynomial_evaluator(point, p)
            for position, section_index in enumerate(core):
                value = evaluator(section_index) % p
                if value == 0:
                    raise AssertionError("R3 core section vanished")
                core_values[position, scalar - 1] = value
        r3_score = evaluate_r3_orbit_pencils(
            core_values,
            core,
            r3,
            p,
            order,
            lam,
            rng,
        )
    else:
        rho_score = PencilScore(
            status="excluded_non_kummer_residue",
            section_parity="odd",
            indices=len(indices),
            pencils=0,
            exact_decoder=False,
            best_accuracy=0.5,
            best_a=None,
            best_b=None,
            best_c=None,
            best_global_sign=None,
            null_trials=0,
            null_median=0.5,
            null_q95=0.5,
            empirical_null_percentile=0.0,
        )
        r3_score = PencilScore(
            status="excluded_non_kummer_residue",
            section_parity="odd_C3_orbit_norm",
            indices=0,
            pencils=0,
            exact_decoder=False,
            best_accuracy=0.5,
            best_a=None,
            best_b=None,
            best_c=None,
            best_global_sign=None,
            null_trials=0,
            null_median=0.5,
            null_q95=0.5,
            empirical_null_percentile=0.0,
        )

    return CaseResult(
        p=p,
        order=order,
        generator=generator,
        beta=beta,
        lam=lam,
        rho_kummer_invariant=rho_kummer,
        structured_indices=indices,
        carry=carry_score,
        rho=rho_score,
        r3=r3_score,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "mixed_weight_pencil_results.json"
        ),
    )
    args = parser.parse_args()

    cases = [run_case(*case) for case in FROZEN_CASES]
    screened_rho = [case for case in cases if case.rho.status == "screened"]
    screened_r3 = [case for case in cases if case.r3.status == "screened"]

    payload = {
        "scope": (
            "fifteen frozen j=0 prime-order toy subgroups; no external or "
            "production target"
        ),
        "package": "GLOBAL-MONODROMY-SECTION-009",
        "candidate": (
            "chi(psi_a(Q)+c*psi_b(Q)); exhaustive c in F_p plus infinity"
        ),
        "protocol": {
            "small_index_max": SMALL_INDEX_MAX,
            "near_order_radius": NEAR_ORDER_RADIUS,
            "matched_null_trials_direct": NULL_TRIALS,
            "matched_null_trials_R3": R3_NULL_TRIALS,
            "same_parity_sections_only": True,
            "global_sign_allowed": True,
        },
        "cases": [asdict(case) for case in cases],
        "aggregate": {
            "cases": len(cases),
            "rho_kummer_cases": len(screened_rho),
            "exact_carry_decoders": sum(
                case.carry.exact_decoder for case in cases
            ),
            "exact_carry_decoders_order_at_least_271": sum(
                case.carry.exact_decoder and case.order >= 271
                for case in cases
            ),
            "carry_cases_strictly_above_matched_null_q95": sum(
                case.carry.best_accuracy > case.carry.null_q95
                for case in cases
            ),
            "exact_rho_decoders": sum(
                case.rho.exact_decoder for case in screened_rho
            ),
            "exact_rho_decoders_order_at_least_271": sum(
                case.rho.exact_decoder and case.order >= 271
                for case in screened_rho
            ),
            "rho_cases_strictly_above_matched_null_q95": sum(
                case.rho.best_accuracy > case.rho.null_q95
                for case in screened_rho
            ),
            "exact_R3_decoders": sum(
                case.r3.exact_decoder for case in screened_r3
            ),
            "exact_R3_decoders_order_at_least_271": sum(
                case.r3.exact_decoder and case.order >= 271
                for case in screened_r3
            ),
            "R3_cases_strictly_above_matched_null_q95": sum(
                case.r3.best_accuracy > case.r3.null_q95
                for case in screened_r3
            ),
            "largest_order": max(case.order for case in cases),
        },
        "claim_boundary": [
            "This is bounded toy evidence, not an asymptotic lower bound.",
            "The screen covers two-section linear pencils, not arbitrary circuits.",
            "Matched controls include coefficient and pencil selection.",
            "No secp256k1 unknown target is evaluated.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
