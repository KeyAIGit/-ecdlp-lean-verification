#!/usr/bin/env python3
"""Within-curve held-out audit for SECP-13441-WITHIN-CURVE-CV-024.

A secp256k1 algorithm is allowed to generate labeled known multiples on the
same curve before receiving an unknown point. Cross-curve package 022 therefore
does not exclude a curve-specific phase lookup. This screen trains and tests on
disjoint C6 scalar orbits of each frozen curve.

The order-13441 phase is Kummer invariant, while carry is anti-invariant under
negation. Carry is therefore tested only after multiplication by a public odd
orientation, half_y or chi_y. Hard-branch R3 is already Kummer invariant and is
tested directly on point-scale s=-1 cases.

Models are a raw phase-bin majority lookup and fixed circular low-pass lookups.
Matched null labels are permutations of the observed orbit labels, preserving
class balance and all train/test sizes. No test-label calibration is used.

No external curve, point, key, wallet, or production-sized target is accepted.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from sympy import isprime

import secp_13441_character_screen as frozen

FOLDS = 5
NULL_TRIALS = 32
LOWPASS_BANDWIDTHS: tuple[int | None, ...] = (None, 8, 32, 128, 512)
LARGE_ORDER_FLOOR = 500
REQUIRED_EXCEEDANCES = 3


def robust_is_prime(value: int) -> bool:
    return bool(isprime(value))


def lookup_name(bandwidth: int | None) -> str:
    return "raw" if bandwidth is None else f"lowpass_{bandwidth}"


def orbit_representatives(curve: frozen.CurveData) -> np.ndarray:
    _, indices = np.unique(curve.orbit_ids, return_index=True)
    if len(indices) != curve.orbit_count:
        raise AssertionError("C6 orbit representative count changed")
    return indices.astype(np.int64)


def invariant_orbit_data(
    curve: frozen.CurveData, target: str
) -> tuple[np.ndarray, np.ndarray]:
    representatives = orbit_representatives(curve)
    phases = curve.phases[representatives].astype(np.int32)
    if target == "carry_half_y":
        scalar_labels = (curve.carry * curve.half_y).astype(np.int8)
    elif target == "carry_chi_y":
        scalar_labels = (curve.carry * curve.chi_y).astype(np.int8)
    elif target == "r3":
        if curve.point_scale_character != -1:
            raise AssertionError("R3 target requested outside the hard branch")
        scalar_labels = curve.r3.astype(np.int8)
    else:
        raise ValueError(target)

    labels = scalar_labels[representatives]
    if not np.all(scalar_labels == labels[curve.orbit_ids]):
        raise AssertionError(f"target {target} was not C6 invariant")
    if not np.all(curve.phases == phases[curve.orbit_ids]):
        raise AssertionError("phase was not C6 invariant")
    return phases, labels


def fold_assignment(count: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    permutation = rng.permutation(count)
    folds = np.empty(count, dtype=np.int8)
    folds[permutation] = np.arange(count, dtype=np.int64) % FOLDS
    return folds


def lookups_from_scores(scores: np.ndarray, fallback: int) -> dict[int | None, np.ndarray]:
    raw = np.where(scores > 0, 1, np.where(scores < 0, -1, fallback)).astype(
        np.int8
    )
    result: dict[int | None, np.ndarray] = {None: raw}
    transform = np.fft.fft(scores)
    for bandwidth in LOWPASS_BANDWIDTHS:
        if bandwidth is None:
            continue
        filtered = transform.copy()
        mask = np.zeros(frozen.PHASE_ORDER, dtype=bool)
        mask[: bandwidth + 1] = True
        mask[-bandwidth:] = True
        filtered[~mask] = 0
        values = np.fft.ifft(filtered).real
        result[bandwidth] = np.where(values >= 0, 1, -1).astype(np.int8)
    return result


def cross_validated_accuracies(
    phases: np.ndarray, labels: np.ndarray, folds: np.ndarray
) -> tuple[dict[int | None, float], float]:
    correct = {bandwidth: 0 for bandwidth in LOWPASS_BANDWIDTHS}
    total = 0
    unseen = 0
    for fold in range(FOLDS):
        train = folds != fold
        test = ~train
        if not np.any(train) or not np.any(test):
            raise AssertionError("empty cross-validation fold")
        scores = np.bincount(
            phases[train],
            weights=labels[train].astype(np.float64),
            minlength=frozen.PHASE_ORDER,
        )
        counts = np.bincount(
            phases[train], minlength=frozen.PHASE_ORDER
        )
        fallback = 1 if int(np.sum(labels[train])) >= 0 else -1
        lookups = lookups_from_scores(scores, fallback)
        for bandwidth, lookup in lookups.items():
            correct[bandwidth] += int(
                np.sum(lookup[phases[test]] == labels[test])
            )
        unseen += int(np.sum(counts[phases[test]] == 0))
        total += int(np.sum(test))
    return (
        {bandwidth: value / total for bandwidth, value in correct.items()},
        unseen / total,
    )


@dataclass(frozen=True)
class Evaluation:
    target: str
    lookup: str
    p: int
    order: int
    point_scale_character: int
    orbit_count: int
    phase_bins_seen: int
    folds: int
    test_unseen_phase_fraction: float
    observed_accuracy: float
    observed_advantage: float
    null_trials: int
    null_median_accuracy: float
    null_q95_accuracy: float
    empirical_null_percentile: float
    strictly_above_null_q95: bool


def evaluate_target(
    curve: frozen.CurveData, target: str
) -> list[Evaluation]:
    phases, labels = invariant_orbit_data(curve, target)
    folds = fold_assignment(len(labels), seed=20260812 + curve.p + sum(map(ord, target)))
    observed, unseen_fraction = cross_validated_accuracies(phases, labels, folds)

    null: dict[int | None, list[float]] = {
        bandwidth: [] for bandwidth in LOWPASS_BANDWIDTHS
    }
    rng = np.random.default_rng(20260812 + curve.order + 17 * sum(map(ord, target)))
    for _ in range(NULL_TRIALS):
        shuffled = labels[rng.permutation(len(labels))]
        accuracies, _ = cross_validated_accuracies(phases, shuffled, folds)
        for bandwidth, value in accuracies.items():
            null[bandwidth].append(value)

    rows: list[Evaluation] = []
    for bandwidth in LOWPASS_BANDWIDTHS:
        distribution = sorted(null[bandwidth])
        q95 = distribution[math.ceil(0.95 * NULL_TRIALS) - 1]
        value = observed[bandwidth]
        rows.append(
            Evaluation(
                target=target,
                lookup=lookup_name(bandwidth),
                p=curve.p,
                order=curve.order,
                point_scale_character=curve.point_scale_character,
                orbit_count=curve.orbit_count,
                phase_bins_seen=curve.phase_bins_seen,
                folds=FOLDS,
                test_unseen_phase_fraction=unseen_fraction,
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "secp_13441_within_curve_cv_results.json"
        ),
    )
    args = parser.parse_args()

    frozen.is_prime = robust_is_prime
    curves = sorted(
        [frozen.build_case(*case) for case in frozen.FROZEN_CASES],
        key=lambda curve: curve.order,
    )

    evaluations: list[Evaluation] = []
    for curve in curves:
        evaluations.extend(evaluate_target(curve, "carry_half_y"))
        evaluations.extend(evaluate_target(curve, "carry_chi_y"))
        if curve.point_scale_character == -1:
            evaluations.extend(evaluate_target(curve, "r3"))

    variant_keys = sorted(
        {(row.target, row.lookup) for row in evaluations}
    )
    variant_summary: dict[str, dict[str, object]] = {}
    admitted: list[str] = []
    for target, lookup in variant_keys:
        rows = [
            row
            for row in evaluations
            if row.target == target
            and row.lookup == lookup
            and row.order >= LARGE_ORDER_FLOOR
        ]
        rows.sort(key=lambda row: row.order)
        exceedances = sum(row.strictly_above_null_q95 for row in rows)
        largest_two = rows[-2:]
        largest_two_min_advantage = min(
            row.observed_advantage for row in largest_two
        )
        is_admitted = (
            exceedances >= REQUIRED_EXCEEDANCES
            and largest_two_min_advantage >= 0.02
        )
        key = f"{target}:{lookup}"
        if is_admitted:
            admitted.append(key)
        variant_summary[key] = {
            "large_cases": len(rows),
            "strict_null_q95_exceedances": exceedances,
            "mean_accuracy": sum(row.observed_accuracy for row in rows) / len(rows),
            "largest_order_accuracy": rows[-1].observed_accuracy,
            "largest_two_minimum_advantage": largest_two_min_advantage,
            "maximum_unseen_phase_fraction": max(
                row.test_unseen_phase_fraction for row in rows
            ),
            "admitted_signal": is_admitted,
        }

    payload = {
        "scope": (
            "within-curve five-fold C6-orbit cross-validation on sixteen frozen "
            "toy subgroups with 13441 dividing p-1; no external point, key, "
            "wallet, or production target"
        ),
        "package": "SECP-13441-WITHIN-CURVE-CV-024",
        "features": (
            "canonical order-13441 phase bin; carry is first multiplied by "
            "half_y or chi_y so that the residual target is C6 invariant"
        ),
        "lookups": [lookup_name(value) for value in LOWPASS_BANDWIDTHS],
        "folds": FOLDS,
        "null_trials": NULL_TRIALS,
        "evaluations": [asdict(row) for row in evaluations],
        "variant_summary": variant_summary,
        "aggregate": {
            "curves": len(curves),
            "evaluations": len(evaluations),
            "admitted_variants": admitted,
            "strict_null_q95_exceedances": sum(
                row.strictly_above_null_q95 for row in evaluations
            ),
            "largest_subgroup_order": max(curve.order for curve in curves),
            "hard_r3_curves": sum(
                curve.point_scale_character == -1 for curve in curves
            ),
        },
        "acceptance_rule": (
            "the same target and lookup must exceed its balance-preserving "
            "permutation null 95% envelope on at least three large curves and "
            "retain at least 2% advantage on both largest eligible curves"
        ),
        "decision": (
            "No curve-specific phase lookup is admitted."
            if not admitted
            else "At least one curve-specific phase lookup requires manual review."
        ),
        "claim_boundary": [
            "Train and test C6 orbits are disjoint and no test-label sign calibration is used.",
            "The permutation null preserves each observed target's class balance.",
            "Only raw and four fixed low-pass lookup families are tested.",
            "A negative toy cross-validation result is not a lower bound for all secp256k1-specific models.",
            "No external or production-sized input is accepted.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
