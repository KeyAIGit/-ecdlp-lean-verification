#!/usr/bin/env python3
"""Same-curve nonlinear public-circuit screen for the order-13441 phase.

Package SECP-13441-CANONICAL-ORBIT-ML-025 tests a realistic preprocessing
scenario: on a fixed curve, an algorithm may generate labeled known multiples
of the public generator before receiving an unknown point. Train and test data
are split by complete C6 scalar orbits, and every feature is invariant on those
orbits. Thus no scalar representative, GLV copy, or negation copy leaks across
folds.

The public feature vector combines the complete order-13441 phase, fixed
circular harmonics, and bounded coordinate-orbit invariants. Three fixed small
models are cross-fitted: phase-only logistic regression, depth-three histogram
gradient boosting, and bounded-depth extremely randomized trees. The test
statistic is balanced accuracy. Its matched null permutes held-out labels
inside each fold after predictions have been frozen, preserving fold sizes and
class balance without retraining on test labels.

Carry is tested only after multiplication by the public odd orientations
half_y or chi_y, making the residual C6 invariant. Hard-branch R3 is tested
only when the point-scale character is -1. No external curve, point, key,
wallet, or production-sized target is accepted.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sympy import isprime

import secp_13441_character_screen as frozen
import secp_13441_within_curve_cv as prior

FOLDS = 5
NULL_TRIALS = 256
LARGE_ORDER_FLOOR = 9_000
MAX_ORBITS = 120_000
HARMONICS = (1, 2, 3, 5, 7, 11, 13, 17, 23, 31, 47, 63, 95, 127, 191, 255)
MODEL_NAMES = (
    "phase_logistic_l2",
    "public_hist_gb_depth3",
    "public_extra_trees_depth10",
)
SCREEN_MIN_ADVANTAGE = 0.002
STRONG_MIN_ADVANTAGE = 0.02
REQUIRED_Q99_EXCEEDANCES = 3


def robust_is_prime(value: int) -> bool:
    return bool(isprime(value))


def fold_assignment(count: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    permutation = rng.permutation(count)
    folds = np.empty(count, dtype=np.int8)
    folds[permutation] = np.arange(count, dtype=np.int64) % FOLDS
    return folds


def coordinate_arrays(curve: frozen.CurveData) -> tuple[np.ndarray, np.ndarray]:
    xs = np.empty(curve.order - 1, dtype=np.int64)
    ys = np.empty(curve.order - 1, dtype=np.int64)
    point = None
    for index in range(curve.order - 1):
        point = frozen.ec_add(point, curve.generator, curve.p)
        if point is None:
            raise AssertionError("subgroup orbit closed before its declared order")
        xs[index], ys[index] = point
    if frozen.ec_add(point, curve.generator, curve.p) is not None:
        raise AssertionError("subgroup orbit failed to close at its declared order")
    return xs, ys


def half_sign_array(values: np.ndarray, modulus: int) -> np.ndarray:
    return np.where(values == 0, 0.0, np.where(2 * values < modulus, 1.0, -1.0))


def phase_features(phases: np.ndarray) -> np.ndarray:
    normalized = phases.astype(np.float64) / frozen.PHASE_ORDER
    columns = [normalized, normalized * normalized]
    angles = 2.0 * math.pi * normalized
    for harmonic in HARMONICS:
        columns.append(np.sin(harmonic * angles))
        columns.append(np.cos(harmonic * angles))
    return np.column_stack(columns).astype(np.float64, copy=False)


def public_orbit_features(curve: frozen.CurveData) -> tuple[np.ndarray, int]:
    representatives = prior.orbit_representatives(curve)
    xs, _ys = coordinate_arrays(curve)
    x0 = xs[representatives]
    p = curve.p
    beta = curve.beta
    x1 = beta * x0 % p
    x2 = beta * x1 % p

    sorted_x = np.sort(np.column_stack((x0, x1, x2)), axis=1)
    gaps = np.column_stack(
        (
            sorted_x[:, 1] - sorted_x[:, 0],
            sorted_x[:, 2] - sorted_x[:, 1],
            p + sorted_x[:, 0] - sorted_x[:, 2],
        )
    )
    sorted_gaps = np.sort(gaps, axis=1)
    sums = x0 + x1 + x2
    if not np.all((sums == p) | (sums == 2 * p)):
        raise AssertionError("field GLV coordinate carry left its binary support")
    field_carry = np.where(sums == p, -1.0, 1.0)

    positive_orientation = (
        ((x0 < x1) & (x1 < x2))
        | ((x1 < x2) & (x2 < x0))
        | ((x2 < x0) & (x0 < x1))
    )
    permutation_orientation = np.where(positive_orientation, 1.0, -1.0)

    x_cube = np.fromiter(
        (pow(int(value), 3, p) for value in x0),
        dtype=np.int64,
        count=len(x0),
    )
    chi_x = np.fromiter(
        (frozen.quadratic_character(int(value), p) for value in x0),
        dtype=np.int8,
        count=len(x0),
    ).astype(np.float64)

    scale = float(p)
    sorted_x_float = sorted_x.astype(np.float64) / scale
    sorted_gaps_float = sorted_gaps.astype(np.float64) / scale
    s2 = (
        x0.astype(np.float64) * x1
        + x1.astype(np.float64) * x2
        + x2.astype(np.float64) * x0
    ) / (scale * scale)
    gap_pair_sum = (
        sorted_gaps_float[:, 0] * sorted_gaps_float[:, 1]
        + sorted_gaps_float[:, 1] * sorted_gaps_float[:, 2]
        + sorted_gaps_float[:, 2] * sorted_gaps_float[:, 0]
    )
    gap_product = np.prod(sorted_gaps_float, axis=1)

    phase_block = phase_features(curve.phases[representatives])
    phase_feature_count = phase_block.shape[1]
    coordinate_block = np.column_stack(
        (
            sorted_x_float,
            sorted_gaps_float,
            x_cube.astype(np.float64) / scale,
            half_sign_array(x_cube, p),
            chi_x,
            field_carry,
            permutation_orientation,
            sums.astype(np.float64) / scale,
            s2,
            gap_pair_sum,
            gap_product,
            np.max(sorted_gaps_float, axis=1) - np.min(sorted_gaps_float, axis=1),
        )
    )
    features = np.column_stack((phase_block, coordinate_block))
    if not np.all(np.isfinite(features)):
        raise AssertionError("public feature matrix contained a non-finite value")
    return features.astype(np.float64, copy=False), phase_feature_count


def model_for(name: str, seed: int):
    if name == "phase_logistic_l2":
        return make_pipeline(
            StandardScaler(),
            LogisticRegression(
                C=0.5,
                max_iter=2_000,
                class_weight="balanced",
                solver="lbfgs",
                random_state=seed,
            ),
        )
    if name == "public_hist_gb_depth3":
        return HistGradientBoostingClassifier(
            max_depth=3,
            max_iter=120,
            learning_rate=0.05,
            l2_regularization=1.0,
            min_samples_leaf=40,
            random_state=seed,
        )
    if name == "public_extra_trees_depth10":
        return ExtraTreesClassifier(
            n_estimators=96,
            max_depth=10,
            min_samples_leaf=20,
            max_features="sqrt",
            class_weight="balanced",
            n_jobs=-1,
            random_state=seed,
        )
    raise ValueError(name)


def model_features(
    name: str, features: np.ndarray, phase_feature_count: int
) -> np.ndarray:
    if name == "phase_logistic_l2":
        return features[:, :phase_feature_count]
    return features


def cross_fitted_predictions(
    features: np.ndarray,
    labels: np.ndarray,
    folds: np.ndarray,
    model_name: str,
    phase_feature_count: int,
    seed: int,
) -> np.ndarray:
    selected = model_features(model_name, features, phase_feature_count)
    predictions = np.empty_like(labels)
    for fold in range(FOLDS):
        train = folds != fold
        test = ~train
        if not np.any(train) or not np.any(test):
            raise AssertionError("empty cross-validation fold")
        if len(np.unique(labels[train])) != 2:
            raise AssertionError("training fold lost one target class")
        model = model_for(model_name, seed + fold)
        model.fit(selected[train], labels[train])
        predictions[test] = model.predict(selected[test]).astype(np.int8)
    if not np.all((predictions == -1) | (predictions == 1)):
        raise AssertionError("model prediction left the binary target space")
    return predictions


def fold_preserving_null(
    labels: np.ndarray,
    predictions: np.ndarray,
    folds: np.ndarray,
    seed: int,
) -> list[float]:
    rng = np.random.default_rng(seed)
    fold_indices = [np.flatnonzero(folds == fold) for fold in range(FOLDS)]
    values: list[float] = []
    for _ in range(NULL_TRIALS):
        shuffled = labels.copy()
        for indices in fold_indices:
            shuffled[indices] = labels[indices][rng.permutation(len(indices))]
        values.append(float(balanced_accuracy_score(shuffled, predictions)))
    values.sort()
    return values


@dataclass(frozen=True)
class Evaluation:
    target: str
    model: str
    p: int
    order: int
    point_scale_character: int
    available_orbits: int
    sampled_orbits: int
    public_feature_count: int
    phase_feature_count: int
    folds: int
    positive_fraction: float
    observed_accuracy: float
    observed_balanced_accuracy: float
    observed_balanced_advantage: float
    null_trials: int
    null_mean_balanced_accuracy: float
    null_std_balanced_accuracy: float
    null_q95_balanced_accuracy: float
    null_q99_balanced_accuracy: float
    empirical_upper_p: float
    z_score: float
    strictly_above_null_q95: bool
    strictly_above_null_q99: bool


def evaluate(
    curve: frozen.CurveData,
    target: str,
    features: np.ndarray,
    phase_feature_count: int,
) -> list[Evaluation]:
    _phases, labels_all = prior.invariant_orbit_data(curve, target)
    available = len(labels_all)
    if len(features) != available:
        raise AssertionError("feature and orbit-label counts diverged")

    if available > MAX_ORBITS:
        rng = np.random.default_rng(20260812 + curve.p + sum(map(ord, target)))
        selected_indices = np.sort(
            rng.choice(available, size=MAX_ORBITS, replace=False)
        )
        features = features[selected_indices]
        labels = labels_all[selected_indices]
    else:
        labels = labels_all

    folds = fold_assignment(
        len(labels), seed=20260812 + curve.order + 31 * sum(map(ord, target))
    )
    rows: list[Evaluation] = []
    for model_index, model_name in enumerate(MODEL_NAMES):
        predictions = cross_fitted_predictions(
            features,
            labels,
            folds,
            model_name,
            phase_feature_count,
            seed=20260812 + curve.p + 10_000 * model_index,
        )
        accuracy = float(np.mean(predictions == labels))
        balanced = float(balanced_accuracy_score(labels, predictions))
        null = fold_preserving_null(
            labels,
            predictions,
            folds,
            seed=20260812 + curve.order + 100_000 * model_index + sum(map(ord, target)),
        )
        q95 = null[math.ceil(0.95 * NULL_TRIALS) - 1]
        q99 = null[math.ceil(0.99 * NULL_TRIALS) - 1]
        null_mean = float(np.mean(null))
        null_std = float(np.std(null, ddof=1))
        z_score = (
            (balanced - null_mean) / null_std if null_std > 0.0 else math.inf
        )
        upper_p = (
            1 + sum(value >= balanced for value in null)
        ) / (NULL_TRIALS + 1)
        rows.append(
            Evaluation(
                target=target,
                model=model_name,
                p=curve.p,
                order=curve.order,
                point_scale_character=curve.point_scale_character,
                available_orbits=available,
                sampled_orbits=len(labels),
                public_feature_count=features.shape[1],
                phase_feature_count=phase_feature_count,
                folds=FOLDS,
                positive_fraction=float(np.mean(labels == 1)),
                observed_accuracy=accuracy,
                observed_balanced_accuracy=balanced,
                observed_balanced_advantage=balanced - 0.5,
                null_trials=NULL_TRIALS,
                null_mean_balanced_accuracy=null_mean,
                null_std_balanced_accuracy=null_std,
                null_q95_balanced_accuracy=q95,
                null_q99_balanced_accuracy=q99,
                empirical_upper_p=upper_p,
                z_score=z_score,
                strictly_above_null_q95=balanced > q95,
                strictly_above_null_q99=balanced > q99,
            )
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "secp_13441_canonical_orbit_ml_cv_results.json"
        ),
    )
    args = parser.parse_args()

    frozen.is_prime = robust_is_prime
    curves = sorted(
        [
            frozen.build_case(*case)
            for case in frozen.FROZEN_CASES
            if case[1] >= LARGE_ORDER_FLOOR
        ],
        key=lambda curve: curve.order,
    )

    evaluations: list[Evaluation] = []
    curve_feature_counts: dict[str, int] = {}
    for curve in curves:
        if curve.order < LARGE_ORDER_FLOOR:
            continue
        features, phase_feature_count = public_orbit_features(curve)
        curve_feature_counts[str(curve.order)] = features.shape[1]
        evaluations.extend(
            evaluate(curve, "carry_half_y", features, phase_feature_count)
        )
        evaluations.extend(
            evaluate(curve, "carry_chi_y", features, phase_feature_count)
        )
        if curve.point_scale_character == -1:
            evaluations.extend(evaluate(curve, "r3", features, phase_feature_count))

    variant_keys = sorted({(row.target, row.model) for row in evaluations})
    variant_summary: dict[str, dict[str, object]] = {}
    screen_admitted: list[str] = []
    strong_admitted: list[str] = []
    for target, model_name in variant_keys:
        rows = sorted(
            [
                row
                for row in evaluations
                if row.target == target and row.model == model_name
            ],
            key=lambda row: row.order,
        )
        if len(rows) < 2:
            continue
        q99_exceedances = sum(row.strictly_above_null_q99 for row in rows)
        q95_exceedances = sum(row.strictly_above_null_q95 for row in rows)
        z3_exceedances = sum(row.z_score >= 3.0 for row in rows)
        largest_two_min_advantage = min(
            row.observed_balanced_advantage for row in rows[-2:]
        )
        screen_signal = (
            q99_exceedances >= REQUIRED_Q99_EXCEEDANCES
            and largest_two_min_advantage >= SCREEN_MIN_ADVANTAGE
        )
        strong_signal = (
            q99_exceedances >= REQUIRED_Q99_EXCEEDANCES
            and largest_two_min_advantage >= STRONG_MIN_ADVANTAGE
        )
        key = f"{target}:{model_name}"
        if screen_signal:
            screen_admitted.append(key)
        if strong_signal:
            strong_admitted.append(key)
        variant_summary[key] = {
            "eligible_curves": len(rows),
            "q95_exceedances": q95_exceedances,
            "q99_exceedances": q99_exceedances,
            "z_ge_3_exceedances": z3_exceedances,
            "mean_balanced_accuracy": sum(
                row.observed_balanced_accuracy for row in rows
            ) / len(rows),
            "largest_order_balanced_accuracy": rows[-1].observed_balanced_accuracy,
            "largest_two_minimum_balanced_advantage": largest_two_min_advantage,
            "minimum_empirical_upper_p": min(row.empirical_upper_p for row in rows),
            "screen_admitted_signal": screen_signal,
            "strong_admitted_signal": strong_signal,
        }

    payload = {
        "scope": (
            "same-curve five-fold cross-fitting on complete disjoint C6 scalar "
            "orbits of frozen j=0 toy subgroups with 13441 dividing p-1; no "
            "external point, key, wallet, or production-sized target"
        ),
        "package": "SECP-13441-CANONICAL-ORBIT-ML-025",
        "public_features": (
            "complete order-13441 phase, sixteen fixed circular harmonics, "
            "sorted GLV x-orbit representatives and gaps, x^3, field carry, "
            "field permutation orientation, and bounded symmetric statistics"
        ),
        "models": list(MODEL_NAMES),
        "folds": FOLDS,
        "null_trials": NULL_TRIALS,
        "maximum_sampled_orbits_per_curve": MAX_ORBITS,
        "phase_harmonics": list(HARMONICS),
        "curve_feature_counts": curve_feature_counts,
        "evaluations": [asdict(row) for row in evaluations],
        "variant_summary": variant_summary,
        "aggregate": {
            "eligible_curves": len(
                {row.order for row in evaluations}
            ),
            "evaluations": len(evaluations),
            "screen_admitted_variants": screen_admitted,
            "strong_admitted_variants": strong_admitted,
            "q99_exceedances": sum(
                row.strictly_above_null_q99 for row in evaluations
            ),
            "largest_subgroup_order": max(row.order for row in evaluations),
            "hard_r3_eligible_curves": len(
                {
                    row.order
                    for row in evaluations
                    if row.target == "r3"
                }
            ),
        },
        "screen_acceptance_rule": (
            "the same target and fixed model must exceed its fold-preserving "
            "permutation-null 99% envelope on at least three eligible curves "
            "and retain at least 0.2% balanced advantage on both largest curves"
        ),
        "strong_acceptance_rule": (
            "the screen rule with at least 2% balanced advantage on both "
            "largest curves"
        ),
        "decision": (
            "At least one nonlinear same-curve public circuit requires exact follow-up."
            if screen_admitted
            else "No tested nonlinear same-curve public circuit passed the frozen screen gate."
        ),
        "claim_boundary": [
            "All train and test partitions are disjoint unions of complete C6 scalar orbits.",
            "Every public feature is invariant on a C6 orbit; no scalar representative is exposed.",
            "Cross-fitted predictions are frozen before the fold-preserving permutation null is generated.",
            "No test-label sign calibration or hyperparameter search is performed.",
            "The screen covers three fixed bounded-capacity models, not arbitrary nonlinear circuits.",
            "A positive toy gate is not a secp256k1 theorem; a negative gate is not a lower bound.",
            "No external or production-sized input is accepted.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
