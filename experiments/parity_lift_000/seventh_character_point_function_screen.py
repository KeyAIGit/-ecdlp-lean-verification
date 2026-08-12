#!/usr/bin/env python3
"""Toy-only held-out screen for the seventh character of the raw point function.

The secp256k1 field satisfies 7 | p-1.  For a seventh-power character, the
order-three GLV multiplier is invisible, so the phase is a public function on
C3 orbits.  This package generates a deterministic j=0 toy family with

    p = 43 mod 84,

so that p is 3 mod 4 and 1 mod 3 and 7.  It learns the best seven-entry binary
lookup table on smaller curves and evaluates it on larger unseen curves for
R3 and for carry after multiplication by public anti-Kummer orientations.
Matched null labels preserve the same C6 symmetries.

No external curve, point, key, wallet, or production-sized target is accepted.
"""
from __future__ import annotations

import argparse
import json
import math
import random
from dataclasses import asdict, dataclass
from pathlib import Path

from nonlocal_odd_anchor_screen import (
    division_polynomial_evaluator,
    orbit,
    primitive_cube_root,
    quadratic_character,
)

B = 7
TARGET_CASES = 14
SEARCH_LIMIT = 120_000
HELD_OUT = 4
NULL_TRIALS = 200


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


def point_count(p: int) -> int:
    total = 1
    for x in range(p):
        rhs = (x*x*x + B) % p
        total += 1 + quadratic_character(rhs, p)
    return total


def first_point(p: int) -> tuple[int, int]:
    for x in range(p):
        rhs = (x*x*x + B) % p
        if rhs == 0:
            return x, 0
        if quadratic_character(rhs, p) == 1:
            y = pow(rhs, (p+1)//4, p)
            if y*y % p != rhs:
                raise AssertionError("sqrt formula failed")
            return x, y
    raise AssertionError("curve had no affine point")


def generate_cases() -> tuple[tuple[int, int, tuple[int, int]], ...]:
    cases = []
    for p in range(43, SEARCH_LIMIT+1, 84):
        if not is_prime(p):
            continue
        order = point_count(p)
        if order < 19 or not is_prime(order):
            continue
        generator = first_point(p)
        if generator[1] == 0:
            continue
        points = orbit(generator, order, p)
        if len(points) != order:
            raise AssertionError("prime-order orbit failed")
        cases.append((p, order, generator))
        if len(cases) == TARGET_CASES:
            break
    if len(cases) != TARGET_CASES:
        raise AssertionError("insufficient deterministic seventh-character cases")
    return tuple(cases)


def raw_point_function(point: tuple[int, int], order: int, p: int) -> int:
    evaluator = division_polynomial_evaluator(point, p)
    numerator = evaluator(p-1)
    denominator = evaluator(p-1+order)
    if numerator == 0 or denominator == 0:
        raise AssertionError("point-function defining ratio vanished")
    if math.gcd(order*order, p-1) != 1:
        raise AssertionError("point-function root was not unique")
    exponent = pow((order*order) % (p-1), -1, p-1)
    return pow(numerator * pow(denominator, -1, p) % p, exponent, p)


def canonical_mu7_root(p: int) -> int:
    for seed in range(2, p):
        root = pow(seed, (p-1)//7, p)
        if root != 1 and pow(root, 7, p) == 1:
            return min(pow(root, exponent, p) for exponent in range(1, 7))
    raise AssertionError("primitive seventh root not found")


def phase_index(value: int, root: int, p: int) -> int:
    phase = pow(value, (p-1)//7, p)
    current = 1
    for exponent in range(7):
        if current == phase:
            return exponent
        current = current * root % p
    raise AssertionError("seventh phase left mu_7")


def half_sign(value: int, modulus: int) -> int:
    value %= modulus
    if value == 0:
        return 0
    return 1 if 2*value < modulus else -1


def carry_sign(k: int, lam: int, order: int) -> int:
    k1 = lam*k % order
    k2 = lam*k1 % order
    total = k+k1+k2
    if total == order:
        return -1
    if total == 2*order:
        return 1
    raise AssertionError("carry identity failed")


@dataclass(frozen=True)
class CurveData:
    p: int
    order: int
    generator: tuple[int, int]
    beta: int
    lam: int
    root7: int
    point_scale_character: int
    rho_kummer_invariant: bool
    phases: tuple[int, ...]
    half_y: tuple[int, ...]
    chi_y: tuple[int, ...]
    carry: tuple[int, ...]
    r3: tuple[int, ...]
    orbit_ids: tuple[int, ...]
    orbit_positive: tuple[bool, ...]


def build_case(p: int, order: int, generator: tuple[int, int]) -> CurveData:
    points = orbit(generator, order, p)
    beta = primitive_cube_root(p)
    point_to_scalar = {point: scalar for scalar, point in enumerate(points)}
    lam = point_to_scalar[(beta*generator[0] % p, generator[1])]
    lam2 = lam*lam % order
    root7 = canonical_mu7_root(p)

    phi_g = raw_point_function(generator, order, p)
    psi_g = division_polynomial_evaluator(generator, p)
    rho = [0] + [quadratic_character(psi_g(k), p) for k in range(1, order)]
    chi_minus_one = quadratic_character(-1, p)
    point_scale = rho[order-1] * rho[1] * chi_minus_one
    rho_kummer = all(rho[order-k] == rho[k] for k in range(1, order))

    phases = []
    half_y_values = []
    chi_y_values = []
    carry_values = []
    r3_values = []
    orbit_ids = []
    orbit_positive = []
    orbit_key_to_id: dict[tuple[int, ...], int] = {}

    for k in range(1, order):
        phi_value = pow(phi_g, k*k, p) * psi_g(k) % p
        phases.append(phase_index(phi_value, root7, p))
        point = points[k]
        assert point is not None
        half_y_values.append(half_sign(point[1], p))
        chi_y_values.append(quadratic_character(point[1], p))
        carry_values.append(carry_sign(k, lam, order))
        r3_values.append(rho[k]*rho[lam*k % order]*rho[lam2*k % order])

        c3 = {k, lam*k % order, lam2*k % order}
        negative = {order-member for member in c3}
        key = tuple(sorted(c3 | negative))
        orbit_id = orbit_key_to_id.setdefault(key, len(orbit_key_to_id))
        canonical_positive = c3 if min(key) in c3 else negative
        orbit_ids.append(orbit_id)
        orbit_positive.append(k in canonical_positive)

    # The seventh phase must be C3 invariant because beta is a seventh power.
    if any(
        phases[k-1] != phases[(lam*k % order)-1]
        for k in range(1, order)
    ):
        raise AssertionError("seventh point-function phase was not GLV invariant")

    return CurveData(
        p=p,
        order=order,
        generator=generator,
        beta=beta,
        lam=lam,
        root7=root7,
        point_scale_character=point_scale,
        rho_kummer_invariant=rho_kummer,
        phases=tuple(phases),
        half_y=tuple(half_y_values),
        chi_y=tuple(chi_y_values),
        carry=tuple(carry_values),
        r3=tuple(r3_values),
        orbit_ids=tuple(orbit_ids),
        orbit_positive=tuple(orbit_positive),
    )


def train_lookup(curves: list[CurveData], target: str, orientation: str) -> tuple[int, ...]:
    scores = [0]*7
    for curve in curves:
        labels = getattr(curve, target)
        orient = getattr(curve, orientation) if orientation != "none" else (1,)*len(labels)
        for phase, label, multiplier in zip(curve.phases, labels, orient):
            scores[phase] += label*multiplier
    return tuple(1 if score >= 0 else -1 for score in scores)


def calibrated_accuracy(
    curve: CurveData, lookup: tuple[int, ...], target: str, orientation: str
) -> float:
    labels = getattr(curve, target)
    orient = getattr(curve, orientation) if orientation != "none" else (1,)*len(labels)
    predictions = [lookup[phase]*multiplier for phase, multiplier in zip(curve.phases, orient)]
    if predictions[0] != labels[0]:
        predictions = [-value for value in predictions]
    return sum(left == right for left, right in zip(predictions, labels))/len(labels)


def random_labels(curve: CurveData, kind: str, rng: random.Random) -> tuple[int, ...]:
    values = [0]*len(curve.orbit_ids)
    signs = {orbit_id: (-1 if rng.getrandbits(1) else 1) for orbit_id in set(curve.orbit_ids)}
    for index, (orbit_id, positive) in enumerate(zip(curve.orbit_ids, curve.orbit_positive)):
        sign = signs[orbit_id]
        if kind == "carry":
            values[index] = sign if positive else -sign
        else:
            values[index] = sign
    return tuple(values)


def train_lookup_from_labels(
    curves: list[CurveData], labels_by_curve: list[tuple[int, ...]], orientation: str
) -> tuple[int, ...]:
    scores = [0]*7
    for curve, labels in zip(curves, labels_by_curve):
        orient = getattr(curve, orientation) if orientation != "none" else (1,)*len(labels)
        for phase, label, multiplier in zip(curve.phases, labels, orient):
            scores[phase] += label*multiplier
    return tuple(1 if score >= 0 else -1 for score in scores)


def accuracy_from_labels(
    curve: CurveData,
    labels: tuple[int, ...],
    lookup: tuple[int, ...],
    orientation: str,
) -> float:
    orient = getattr(curve, orientation) if orientation != "none" else (1,)*len(labels)
    predictions = [lookup[phase]*multiplier for phase, multiplier in zip(curve.phases, orient)]
    if predictions[0] != labels[0]:
        predictions = [-value for value in predictions]
    return sum(left == right for left, right in zip(predictions, labels))/len(labels)


@dataclass(frozen=True)
class Evaluation:
    target: str
    orientation: str
    test_p: int
    test_order: int
    training_curves: int
    lookup: tuple[int, ...]
    observed_accuracy: float
    observed_advantage: float
    null_trials: int
    null_median_accuracy: float
    null_q95_accuracy: float
    empirical_null_percentile: float
    strictly_above_null_q95: bool


def evaluate(
    train_curves: list[CurveData],
    test_curve: CurveData,
    target: str,
    orientation: str,
    seed: int,
) -> Evaluation:
    lookup = train_lookup(train_curves, target, orientation)
    observed = calibrated_accuracy(test_curve, lookup, target, orientation)
    rng = random.Random(seed)
    null = []
    for _ in range(NULL_TRIALS):
        train_labels = [random_labels(curve, target, rng) for curve in train_curves]
        test_labels = random_labels(test_curve, target, rng)
        null_lookup = train_lookup_from_labels(train_curves, train_labels, orientation)
        null.append(accuracy_from_labels(test_curve, test_labels, null_lookup, orientation))
    null.sort()
    q95 = null[math.ceil(0.95*NULL_TRIALS)-1]
    return Evaluation(
        target=target,
        orientation=orientation,
        test_p=test_curve.p,
        test_order=test_curve.order,
        training_curves=len(train_curves),
        lookup=lookup,
        observed_accuracy=observed,
        observed_advantage=observed-0.5,
        null_trials=NULL_TRIALS,
        null_median_accuracy=null[len(null)//2],
        null_q95_accuracy=q95,
        empirical_null_percentile=sum(value <= observed for value in null)/NULL_TRIALS,
        strictly_above_null_q95=observed > q95,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "seventh_character_point_function_results.json"
        ),
    )
    args = parser.parse_args()

    generated = generate_cases()
    curves = sorted([build_case(*case) for case in generated], key=lambda curve: curve.order)
    tests = curves[-HELD_OUT:]
    evaluations = []
    variants = (
        ("r3", "none"),
        ("carry", "half_y"),
        ("carry", "chi_y"),
    )
    for test_index, test_curve in enumerate(tests):
        train_curves = [curve for curve in curves if curve.order < test_curve.order]
        for target, orientation in variants:
            evaluations.append(evaluate(
                train_curves,
                test_curve,
                target,
                orientation,
                seed=20260812 + test_index*1000 + len(evaluations),
            ))

    summary = {}
    for target, orientation in variants:
        key = f"{target}:{orientation}"
        rows = [row for row in evaluations if row.target == target and row.orientation == orientation]
        largest_two = sorted(rows, key=lambda row: row.test_order)[-2:]
        summary[key] = {
            "evaluations": len(rows),
            "strict_null_q95_exceedances": sum(row.strictly_above_null_q95 for row in rows),
            "mean_accuracy": sum(row.observed_accuracy for row in rows)/len(rows),
            "largest_order_accuracy": max(rows, key=lambda row: row.test_order).observed_accuracy,
            "largest_two_minimum_advantage": min(row.observed_advantage for row in largest_two),
            "admitted_signal": (
                sum(row.strictly_above_null_q95 for row in rows) >= 3
                and min(row.observed_advantage for row in largest_two) >= 0.02
            ),
        }

    payload = {
        "scope": (
            "deterministic generated j=0 prime-order toy curves with p=43 mod 84; "
            "smaller curves train a seven-entry lookup and larger unseen curves test it; "
            "no external point, key, wallet, or production target"
        ),
        "package": "SEVENTH-CHARACTER-POINT-FUNCTION-020",
        "generated_cases": [
            {"p": curve.p, "order": curve.order, "generator": curve.generator}
            for curve in curves
        ],
        "public_phase": "Phi(Q)^((p-1)/7) in canonical mu_7",
        "evaluations": [asdict(row) for row in evaluations],
        "variant_summary": summary,
        "aggregate": {
            "cases": len(curves),
            "held_out_cases": len(tests),
            "admitted_variants": [key for key, value in summary.items() if value["admitted_signal"]],
            "largest_order": max(curve.order for curve in curves),
        },
        "acceptance_rule": (
            "the same seven-entry lookup variant must exceed matched null 95% on "
            "at least three held-out curves and retain at least 2% advantage on "
            "both largest curves"
        ),
        "claim_boundary": [
            "A passed toy lookup still requires an exact arithmetic characterization before secp256k1 use.",
            "The canonical mu_7 root is selected by the least nontrivial integer representative.",
            "Failure of the seventh quotient is not a lower bound for the 13441st quotient or all p-1 characters.",
            "No external or production-sized input is accepted.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
