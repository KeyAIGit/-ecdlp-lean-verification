#!/usr/bin/env python3
"""Held-out toy screen for the secp256k1 field factor 13441.

The secp256k1 field satisfies

    p - 1 = 2 * 3 * 7 * 13441 * q,

with q prime.  This script studies the order-13441 multiplicative phase of the
public perfectly-periodic point function Phi(Q).  It uses only frozen j=0 toy
subgroups in fields for which 13441 divides p-1.

The phase is invariant under the order-three GLV multiplier because
3 divides (p-1)/13441.  A universal binary decoder is trained on smaller
curves and tested on larger unseen curves.  To avoid treating unseen phase
bins as automatic failure, the screen evaluates both a raw 13441-entry lookup
and fixed circular low-pass Fourier lookups.

No external curve, point, key, wallet, or production-sized target is accepted.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional

import numpy as np

Point = Optional[tuple[int, int]]
B = 7
PHASE_ORDER = 13441
NULL_TRIALS = 64
LOWPASS_BANDWIDTHS: tuple[int | None, ...] = (None, 8, 32, 128, 512)
HELD_OUT_CARRY = 4
HELD_OUT_HARD_R3 = 4

SECP256K1_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
SECP_LARGE_FACTOR = 205115282021455665897114700593932402728804164701536103180137503955397371

# Frozen prime-order subgroups on y^2=x^3+7.  Every field prime is 3 mod 4,
# 1 mod 3, and 1 mod 13441.  The listed point has the listed prime order.
FROZEN_CASES = (
    (241939, 1279, (50134, 166328)),
    (564523, 3463, (555781, 547362)),
    (1854859, 367, (1180089, 908594)),
    (2177443, 77689, (961893, 2148613)),
    (2500027, 1489, (1519285, 1141904)),
    (4274239, 82153, (1087088, 1568154)),
    (5403283, 52489, (3505050, 1702964)),
    (6532327, 853, (2066392, 419359)),
    (7338787, 571, (2252788, 3855441)),
    (8629123, 34231, (32910, 2721332)),
    (9435583, 9439, (3633309, 7218162)),
    (10725919, 206197, (7791123, 8062963)),
    (11532379, 549481, (6260015, 8186014)),
    (12177547, 811, (11439012, 9498314)),
    (12984007, 683737, (7972153, 4741966)),
    (13145299, 11299, (555422, 11734518)),
)


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


def ec_mul(scalar: int, point: Point, p: int) -> Point:
    result: Point = None
    addend = point
    while scalar:
        if scalar & 1:
            result = ec_add(result, addend, p)
        addend = ec_add(addend, addend, p)
        scalar >>= 1
    return result


def quadratic_character(value: int, p: int) -> int:
    value %= p
    if value == 0:
        return 0
    return 1 if pow(value, (p - 1) // 2, p) == 1 else -1


def half_sign(value: int, p: int) -> int:
    value %= p
    if value == 0:
        return 0
    return 1 if 2 * value < p else -1


def division_polynomial_evaluator(point: tuple[int, int], p: int):
    x, y = point
    inverse_two_y = pow(2 * y, -1, p)

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
            * inverse_two_y
            * (
                psi(m + 2) * pow(psi(m - 1), 2, p)
                - psi(m - 2) * pow(psi(m + 1), 2, p)
            )
        ) % p

    return psi


def raw_point_function_generator(
    generator: tuple[int, int], order: int, p: int
) -> tuple[int, object]:
    psi = division_polynomial_evaluator(generator, p)
    numerator = psi(p - 1)
    denominator = psi(p - 1 + order)
    if numerator == 0 or denominator == 0:
        raise AssertionError("point-function defining ratio vanished")
    if math.gcd(order * order, p - 1) != 1:
        raise AssertionError("point-function root was not unique")
    exponent = pow((order * order) % (p - 1), -1, p - 1)
    value = pow(numerator * pow(denominator, -1, p) % p, exponent, p)
    return value, psi


def primitive_root_of_order(p: int, order: int) -> int:
    if (p - 1) % order:
        raise AssertionError("requested root order did not divide p-1")
    for seed in range(2, 1000):
        root = pow(seed, (p - 1) // order, p)
        if root != 1 and pow(root, order, p) == 1:
            return root
    raise AssertionError("primitive root not found")


def canonical_phase_root(p: int) -> tuple[int, dict[int, int]]:
    root = primitive_root_of_order(p, PHASE_ORDER)
    powers = []
    current = 1
    for _ in range(PHASE_ORDER):
        powers.append(current)
        current = current * root % p
    if current != 1 or len(set(powers)) != PHASE_ORDER:
        raise AssertionError("phase root did not have exact order 13441")
    canonical = min(powers[1:])
    phase_map: dict[int, int] = {}
    current = 1
    for exponent in range(PHASE_ORDER):
        phase_map[current] = exponent
        current = current * canonical % p
    if len(phase_map) != PHASE_ORDER:
        raise AssertionError("canonical phase root lost primitivity")
    return canonical, phase_map


def subgroup_glv_scalar(
    p: int, order: int, generator: tuple[int, int], beta: int
) -> int:
    candidate = primitive_root_of_order(order, 3)
    glv_point = (beta * generator[0] % p, generator[1])
    if ec_mul(candidate, generator, p) == glv_point:
        return candidate
    candidate_squared = candidate * candidate % order
    if ec_mul(candidate_squared, generator, p) == glv_point:
        return candidate_squared
    raise AssertionError("field GLV automorphism did not act by an order-three scalar")


def carry_signs(order: int, lam: int) -> np.ndarray:
    scalars = np.arange(1, order, dtype=np.int64)
    first = lam * scalars % order
    second = lam * first % order
    total = scalars + first + second
    if not np.all((total == order) | (total == 2 * order)):
        raise AssertionError("canonical scalar carry identity failed")
    return np.where(total == order, -1, 1).astype(np.int8)


def orbit_partition(order: int, lam: int) -> tuple[np.ndarray, np.ndarray, int]:
    scalars = np.arange(1, order, dtype=np.int64)
    first = lam * scalars % order
    second = lam * first % order
    min_positive = np.minimum(np.minimum(scalars, first), second)
    min_negative = np.minimum(
        np.minimum(order - scalars, order - first), order - second
    )
    canonical = np.minimum(min_positive, min_negative)
    _, inverse = np.unique(canonical, return_inverse=True)
    positive = min_positive < min_negative
    return inverse.astype(np.int32), positive, int(inverse.max()) + 1


@dataclass
class CurveData:
    p: int
    order: int
    generator: tuple[int, int]
    beta: int
    lam: int
    phase_root: int
    point_scale_character: int
    rho_kummer_invariant: bool
    phase_bins_seen: int
    phases: np.ndarray
    half_y: np.ndarray
    chi_y: np.ndarray
    carry: np.ndarray
    r3: np.ndarray
    orbit_ids: np.ndarray
    orbit_positive: np.ndarray
    orbit_count: int


def build_case(p: int, order: int, generator: tuple[int, int]) -> CurveData:
    if not is_prime(p) or not is_prime(order):
        raise AssertionError("frozen field or subgroup order was not prime")
    if p % 4 != 3 or p % 3 != 1 or (p - 1) % PHASE_ORDER:
        raise AssertionError("frozen field congruence changed")
    if order % 3 != 1:
        raise AssertionError("subgroup did not admit nontrivial GLV eigenvalue")
    if ec_mul(order, generator, p) is not None:
        raise AssertionError("frozen generator order failed")

    beta = primitive_root_of_order(p, 3)
    lam = subgroup_glv_scalar(p, order, generator, beta)
    lam_squared = lam * lam % order
    phase_root, phase_map = canonical_phase_root(p)
    phi_generator, psi = raw_point_function_generator(generator, order, p)

    phases = np.empty(order - 1, dtype=np.int32)
    half_y_values = np.empty(order - 1, dtype=np.int8)
    chi_y_values = np.empty(order - 1, dtype=np.int8)
    rho = np.empty(order, dtype=np.int8)
    rho[0] = 0

    point: Point = None
    phi_power = phi_generator
    phi_step = pow(phi_generator, 3, p)
    phi_step_increment = pow(phi_generator, 2, p)
    phase_exponent = (p - 1) // PHASE_ORDER

    for index, scalar in enumerate(range(1, order)):
        point = ec_add(point, generator, p)
        if point is None:
            raise AssertionError("subgroup orbit closed early")
        psi_value = psi(scalar)
        rho_value = quadratic_character(psi_value, p)
        if rho_value == 0:
            raise AssertionError("EDS residue vanished off the identity")
        rho[scalar] = rho_value

        phi_value = phi_power * psi_value % p
        phase = pow(phi_value, phase_exponent, p)
        try:
            phases[index] = phase_map[phase]
        except KeyError as exc:
            raise AssertionError("point-function phase left mu_13441") from exc
        half_y_values[index] = half_sign(point[1], p)
        chi_y_values[index] = quadratic_character(point[1], p)

        phi_power = phi_power * phi_step % p
        phi_step = phi_step * phi_step_increment % p

    if ec_add(point, generator, p) is not None:
        raise AssertionError("subgroup orbit did not close at declared order")

    carry = carry_signs(order, lam)
    scalars = np.arange(1, order, dtype=np.int64)
    first = lam * scalars % order
    second = lam_squared * scalars % order
    r3 = (rho[scalars] * rho[first] * rho[second]).astype(np.int8)

    chi_minus_one = quadratic_character(-1, p)
    point_scale = int(rho[order - 1] * rho[1] * chi_minus_one)
    if point_scale not in (-1, 1):
        raise AssertionError("point-scale character was not binary")
    rho_kummer = bool(np.all(rho[order - scalars] == rho[scalars]))

    if not np.all(phases == phases[(first - 1).astype(np.int64)]):
        raise AssertionError("13441st phase was not GLV invariant")
    if not np.all(phases == phases[(order - scalars - 1).astype(np.int64)]):
        raise AssertionError("13441st phase was not Kummer invariant")

    orbit_ids, orbit_positive, orbit_count = orbit_partition(order, lam)
    return CurveData(
        p=p,
        order=order,
        generator=generator,
        beta=beta,
        lam=lam,
        phase_root=phase_root,
        point_scale_character=point_scale,
        rho_kummer_invariant=rho_kummer,
        phase_bins_seen=int(np.unique(phases).size),
        phases=phases,
        half_y=half_y_values,
        chi_y=chi_y_values,
        carry=carry,
        r3=r3,
        orbit_ids=orbit_ids,
        orbit_positive=orbit_positive,
        orbit_count=orbit_count,
    )


def orientation_values(curve: CurveData, name: str) -> np.ndarray:
    if name == "none":
        return np.ones(curve.order - 1, dtype=np.int8)
    return getattr(curve, name)


def training_scores(
    curves: list[CurveData],
    labels_by_curve: list[np.ndarray],
    orientation: str,
) -> np.ndarray:
    scores = np.zeros(PHASE_ORDER, dtype=np.float64)
    for curve, labels in zip(curves, labels_by_curve):
        weights = labels.astype(np.float64) * orientation_values(
            curve, orientation
        )
        scores += np.bincount(
            curve.phases, weights=weights, minlength=PHASE_ORDER
        )
    return scores


def lookup_from_scores(scores: np.ndarray, bandwidth: int | None) -> np.ndarray:
    if bandwidth is None:
        filtered = scores
    else:
        transform = np.fft.fft(scores)
        mask = np.zeros(PHASE_ORDER, dtype=bool)
        mask[: bandwidth + 1] = True
        mask[-bandwidth:] = True
        transform[~mask] = 0
        filtered = np.fft.ifft(transform).real
    return np.where(filtered >= 0, 1, -1).astype(np.int8)


def calibrated_accuracy(
    curve: CurveData,
    labels: np.ndarray,
    lookup: np.ndarray,
    orientation: str,
) -> float:
    predictions = lookup[curve.phases] * orientation_values(curve, orientation)
    if predictions[0] != labels[0]:
        predictions = -predictions
    return float(np.mean(predictions == labels))


def random_labels(
    curve: CurveData, target: str, rng: np.random.Generator
) -> np.ndarray:
    orbit_signs = rng.choice(
        np.asarray([-1, 1], dtype=np.int8), size=curve.orbit_count
    )
    labels = orbit_signs[curve.orbit_ids]
    if target == "carry":
        labels = labels * np.where(curve.orbit_positive, 1, -1)
    return labels.astype(np.int8)


def lookup_name(bandwidth: int | None) -> str:
    return "raw" if bandwidth is None else f"lowpass_{bandwidth}"


@dataclass(frozen=True)
class Evaluation:
    target: str
    orientation: str
    lookup: str
    test_p: int
    test_order: int
    point_scale_character: int
    training_curves: int
    training_samples: int
    training_phase_bins_seen: int
    test_phase_bins_seen: int
    test_phase_bins_unseen: int
    observed_accuracy: float
    observed_advantage: float
    null_trials: int
    null_median_accuracy: float
    null_q95_accuracy: float
    empirical_null_percentile: float
    strictly_above_null_q95: bool


def evaluate_block(
    train_curves: list[CurveData],
    test_curve: CurveData,
    target: str,
    orientation: str,
    seed: int,
) -> list[Evaluation]:
    observed_labels = [getattr(curve, target) for curve in train_curves]
    observed_scores = training_scores(
        train_curves, observed_labels, orientation
    )
    observed_lookups = {
        bandwidth: lookup_from_scores(observed_scores, bandwidth)
        for bandwidth in LOWPASS_BANDWIDTHS
    }
    observed = {
        bandwidth: calibrated_accuracy(
            test_curve,
            getattr(test_curve, target),
            lookup,
            orientation,
        )
        for bandwidth, lookup in observed_lookups.items()
    }

    null: dict[int | None, list[float]] = {
        bandwidth: [] for bandwidth in LOWPASS_BANDWIDTHS
    }
    rng = np.random.default_rng(seed)
    for _ in range(NULL_TRIALS):
        train_labels = [
            random_labels(curve, target, rng) for curve in train_curves
        ]
        test_labels = random_labels(test_curve, target, rng)
        scores = training_scores(train_curves, train_labels, orientation)
        for bandwidth in LOWPASS_BANDWIDTHS:
            lookup = lookup_from_scores(scores, bandwidth)
            null[bandwidth].append(
                calibrated_accuracy(
                    test_curve, test_labels, lookup, orientation
                )
            )

    training_bins: set[int] = set()
    for curve in train_curves:
        training_bins.update(int(value) for value in np.unique(curve.phases))
    test_bins = {int(value) for value in np.unique(test_curve.phases)}

    rows: list[Evaluation] = []
    for bandwidth in LOWPASS_BANDWIDTHS:
        distribution = sorted(null[bandwidth])
        q95 = distribution[math.ceil(0.95 * NULL_TRIALS) - 1]
        value = observed[bandwidth]
        rows.append(
            Evaluation(
                target=target,
                orientation=orientation,
                lookup=lookup_name(bandwidth),
                test_p=test_curve.p,
                test_order=test_curve.order,
                point_scale_character=test_curve.point_scale_character,
                training_curves=len(train_curves),
                training_samples=sum(curve.order - 1 for curve in train_curves),
                training_phase_bins_seen=len(training_bins),
                test_phase_bins_seen=len(test_bins),
                test_phase_bins_unseen=len(test_bins - training_bins),
                observed_accuracy=value,
                observed_advantage=value - 0.5,
                null_trials=NULL_TRIALS,
                null_median_accuracy=float(np.median(distribution)),
                null_q95_accuracy=q95,
                empirical_null_percentile=(
                    sum(item <= value for item in distribution) / NULL_TRIALS
                ),
                strictly_above_null_q95=value > q95,
            )
        )
    return rows


def curve_metadata(curve: CurveData) -> dict[str, object]:
    return {
        "p": curve.p,
        "order": curve.order,
        "generator": curve.generator,
        "beta": curve.beta,
        "lambda": curve.lam,
        "phase_root": curve.phase_root,
        "point_scale_character": curve.point_scale_character,
        "rho_kummer_invariant": curve.rho_kummer_invariant,
        "phase_bins_seen": curve.phase_bins_seen,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "secp_13441_character_results.json"
        ),
    )
    args = parser.parse_args()

    if SECP256K1_P - 1 != (
        2 * 3 * 7 * PHASE_ORDER * SECP_LARGE_FACTOR
    ):
        raise AssertionError("secp256k1 p-1 factorization changed")
    if not is_prime(PHASE_ORDER) or not is_prime(SECP_LARGE_FACTOR):
        raise AssertionError("secp256k1 field factors were not prime")
    if ((SECP256K1_P - 1) // PHASE_ORDER) % 3:
        raise AssertionError("secp256k1 13441 quotient lost GLV invariance")

    curves = sorted([build_case(*case) for case in FROZEN_CASES], key=lambda c: c.order)
    carry_tests = curves[-HELD_OUT_CARRY:]
    hard_curves = [curve for curve in curves if curve.point_scale_character == -1]
    hard_tests = hard_curves[-HELD_OUT_HARD_R3:]

    evaluations: list[Evaluation] = []
    block = 0
    for test_curve in carry_tests:
        train_curves = [curve for curve in curves if curve.order < test_curve.order]
        for orientation in ("half_y", "chi_y"):
            evaluations.extend(
                evaluate_block(
                    train_curves,
                    test_curve,
                    "carry",
                    orientation,
                    seed=20260812 + block * 1009,
                )
            )
            block += 1

    for test_curve in hard_tests:
        train_curves = [
            curve
            for curve in hard_curves
            if curve.order < test_curve.order
        ]
        evaluations.extend(
            evaluate_block(
                train_curves,
                test_curve,
                "r3",
                "none",
                seed=20260812 + block * 1009,
            )
        )
        block += 1

    variant_summary: dict[str, dict[str, object]] = {}
    variant_keys = sorted(
        {
            f"{row.target}:{row.orientation}:{row.lookup}"
            for row in evaluations
        }
    )
    for key in variant_keys:
        target, orientation, lookup = key.split(":")
        rows = [
            row
            for row in evaluations
            if row.target == target
            and row.orientation == orientation
            and row.lookup == lookup
        ]
        rows = sorted(rows, key=lambda row: row.test_order)
        largest_two = rows[-2:]
        exceedances = sum(row.strictly_above_null_q95 for row in rows)
        admitted = (
            exceedances >= 3
            and min(row.observed_advantage for row in largest_two) >= 0.02
        )
        variant_summary[key] = {
            "evaluations": len(rows),
            "strict_null_q95_exceedances": exceedances,
            "mean_accuracy": sum(row.observed_accuracy for row in rows) / len(rows),
            "largest_order_accuracy": rows[-1].observed_accuracy,
            "largest_two_minimum_advantage": min(
                row.observed_advantage for row in largest_two
            ),
            "maximum_unseen_test_phase_bins": max(
                row.test_phase_bins_unseen for row in rows
            ),
            "admitted_signal": admitted,
        }

    admitted = [
        key for key, value in variant_summary.items() if value["admitted_signal"]
    ]
    payload = {
        "scope": (
            "sixteen frozen j=0 prime-order toy subgroups in fields with "
            "13441 dividing p-1; rolling smaller-curve training and larger unseen "
            "testing; no external point, key, wallet, or production target"
        ),
        "package": "SECP-13441-CHARACTER-HELDOUT-022",
        "secp256k1_field_factorization": {
            "p_hex": hex(SECP256K1_P),
            "p_minus_one": str(SECP256K1_P - 1),
            "factorization": (
                "2 * 3 * 7 * 13441 * " + str(SECP_LARGE_FACTOR)
            ),
            "phase_order": PHASE_ORDER,
            "three_divides_character_exponent": True,
        },
        "public_phase": "Phi(Q)^((p-1)/13441) in canonical mu_13441",
        "lookup_families": [lookup_name(value) for value in LOWPASS_BANDWIDTHS],
        "frozen_cases": [curve_metadata(curve) for curve in curves],
        "carry_test_orders": [curve.order for curve in carry_tests],
        "hard_r3_test_orders": [curve.order for curve in hard_tests],
        "evaluations": [asdict(row) for row in evaluations],
        "variant_summary": variant_summary,
        "aggregate": {
            "cases": len(curves),
            "carry_held_out_cases": len(carry_tests),
            "hard_r3_held_out_cases": len(hard_tests),
            "evaluations": len(evaluations),
            "admitted_variants": admitted,
            "strict_null_q95_exceedances": sum(
                row.strictly_above_null_q95 for row in evaluations
            ),
            "largest_subgroup_order": max(curve.order for curve in curves),
            "largest_field_prime": max(curve.p for curve in curves),
        },
        "acceptance_rule": (
            "the same target/orientation/lookup variant must exceed matched null "
            "95% on at least three rolling held-out curves and retain at least "
            "2% advantage on both largest tests"
        ),
        "decision": (
            "No universal raw or low-pass 13441st-character lookup is admitted."
            if not admitted
            else "At least one 13441st-character lookup requires manual review."
        ),
        "claim_boundary": [
            "The exact secp256k1 field factorization and GLV phase invariance are arithmetic facts.",
            "The toy screen tests universal cross-curve lookup structure, not a secp256k1-specific lookup table.",
            "A failed binary lookup does not rule out richer use of the full 13441st-root phase.",
            "Failure is not a lower bound for the remaining large prime factor or all public point-function circuits.",
            "No external or production-sized input is accepted.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
