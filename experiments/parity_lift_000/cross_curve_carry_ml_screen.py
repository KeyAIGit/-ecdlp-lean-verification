#!/usr/bin/env python3
"""Toy-only held-out search for a fixed public carry predicate.

A fixed small classifier is trained on public coordinate features from smaller
frozen j=0 toy curves and evaluated on strictly larger unseen curves.  The
labels are the scalar GLV carry.  Matched null trials preserve C3 invariance and
negation anti-invariance on every curve.  The global output sign is calibrated
at the public generator G, whose carry class is known.

A stable held-out advantage would define an efficiently evaluable public
predicate and justify a Fourier/local-SFT follow-up.  This package accepts no
external curve, point, key, wallet, or production-sized target.
"""
from __future__ import annotations

import argparse
import json
import math
import random
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from nonlocal_odd_anchor_screen import (
    FROZEN_CASES,
    division_polynomial_evaluator,
    orbit,
    primitive_cube_root,
    quadratic_character,
)

SMALL_INDICES = (2, 3, 4, 5, 7, 8, 11, 13)
NULL_TRIALS = 30
MIN_TRAIN_CURVES = 8
TEST_CASES = 5


def half_sign(value: int, modulus: int) -> int:
    value %= modulus
    if value == 0:
        return 0
    return 1 if 2 * value < modulus else -1


def carry_sign(k: int, lam: int, order: int) -> int:
    k1 = lam * k % order
    k2 = lam * k1 % order
    total = k + k1 + k2
    if total == order:
        return -1
    if total == 2 * order:
        return 1
    raise AssertionError("GLV carry identity failed")


def coordinate_features(
    point: tuple[int, int], p: int, order: int, beta: int, trace: int
) -> list[float]:
    x, y = point
    x1 = beta * x % p
    x2 = beta * x1 % p
    xs = sorted((x, x1, x2))
    gaps = (xs[1] - xs[0], xs[2] - xs[1], p + xs[0] - xs[2])
    u = pow(x, 3, p)
    xy = x * y % p
    permutation = (x - x1) * (x1 - x2) * (x2 - x)
    field_sum = x + x1 + x2
    field_carry = -1.0 if field_sum == p else 1.0

    evaluator = division_polynomial_evaluator(point, p)
    division_characters = []
    for index in SMALL_INDICES:
        value = quadratic_character(evaluator(index), p)
        if value == 0:
            raise AssertionError("fixed-index division feature vanished")
        division_characters.append(float(value))

    scale = float(p)
    return [
        x / scale,
        y / scale,
        (2 * y - p) / scale,
        u / scale,
        xy / scale,
        xs[0] / scale,
        xs[1] / scale,
        xs[2] / scale,
        gaps[0] / scale,
        gaps[1] / scale,
        gaps[2] / scale,
        float(half_sign(x, p)),
        float(half_sign(y, p)),
        float(quadratic_character(x, p)),
        float(quadratic_character(y, p)),
        float(quadratic_character(x * y, p)),
        field_carry,
        1.0 if permutation > 0 else -1.0,
        trace / math.sqrt(p),
        order / scale,
        *division_characters,
    ]


@dataclass(frozen=True)
class CurveDataset:
    p: int
    order: int
    generator: tuple[int, int]
    beta: int
    lam: int
    trace: int
    features: np.ndarray
    labels: np.ndarray
    orbit_ids: tuple[int, ...]
    orbit_positive: tuple[bool, ...]


def build_dataset(p: int, order: int, generator: tuple[int, int]) -> CurveDataset:
    points = orbit(generator, order, p)
    beta = primitive_cube_root(p)
    point_to_scalar = {point: scalar for scalar, point in enumerate(points)}
    lam = point_to_scalar[(beta * generator[0] % p, generator[1])]
    lam2 = lam * lam % order
    trace = p + 1 - order

    orbit_key_to_id: dict[tuple[int, ...], int] = {}
    features = []
    labels = []
    orbit_ids = []
    orbit_positive = []

    for k in range(1, order):
        point = points[k]
        assert point is not None
        c3 = {k, lam * k % order, lam2 * k % order}
        negative = {order - member for member in c3}
        key = tuple(sorted(c3 | negative))
        orbit_id = orbit_key_to_id.setdefault(key, len(orbit_key_to_id))
        positive_half = k in c3 if min(key) in c3 else k in negative
        # Canonicalize which C3 half is called positive using the smallest
        # scalar in the C6 orbit.  Random null labels use this orientation only
        # to assign opposite signs to the two halves.
        canonical_positive = set(c3 if min(key) in c3 else negative)

        features.append(coordinate_features(point, p, order, beta, trace))
        labels.append(1 if carry_sign(k, lam, order) == 1 else 0)
        orbit_ids.append(orbit_id)
        orbit_positive.append(k in canonical_positive)

    return CurveDataset(
        p=p,
        order=order,
        generator=generator,
        beta=beta,
        lam=lam,
        trace=trace,
        features=np.asarray(features, dtype=np.float64),
        labels=np.asarray(labels, dtype=np.int8),
        orbit_ids=tuple(orbit_ids),
        orbit_positive=tuple(orbit_positive),
    )


def random_symmetric_labels(dataset: CurveDataset, rng: random.Random) -> np.ndarray:
    signs = {
        orbit_id: rng.getrandbits(1)
        for orbit_id in set(dataset.orbit_ids)
    }
    labels = np.empty(len(dataset.orbit_ids), dtype=np.int8)
    for index, (orbit_id, positive) in enumerate(
        zip(dataset.orbit_ids, dataset.orbit_positive)
    ):
        bit = signs[orbit_id]
        labels[index] = bit if positive else 1 - bit
    return labels


def models(seed: int):
    return {
        "logistic": make_pipeline(
            StandardScaler(),
            LogisticRegression(
                C=1.0,
                max_iter=3000,
                class_weight="balanced",
                random_state=seed,
            ),
        ),
        "hist_gb_depth3": HistGradientBoostingClassifier(
            max_depth=3,
            max_iter=120,
            learning_rate=0.05,
            l2_regularization=1.0,
            min_samples_leaf=20,
            random_state=seed,
        ),
        "random_forest_depth6": RandomForestClassifier(
            n_estimators=160,
            max_depth=6,
            min_samples_leaf=20,
            max_features="sqrt",
            class_weight="balanced",
            n_jobs=-1,
            random_state=seed,
        ),
    }


def calibrated_accuracy(model, dataset: CurveDataset, labels: np.ndarray) -> float:
    predictions = model.predict(dataset.features).astype(np.int8)
    # The public generator is row zero (k=1).  Its true carry class calibrates
    # an otherwise harmless curve-global sign ambiguity.
    if predictions[0] != labels[0]:
        predictions = 1 - predictions
    return float(np.mean(predictions == labels))


@dataclass(frozen=True)
class EvaluationResult:
    model: str
    test_p: int
    test_order: int
    training_curves: int
    training_points: int
    observed_accuracy: float
    observed_advantage: float
    null_trials: int
    null_median_accuracy: float
    null_q95_accuracy: float
    empirical_null_percentile: float
    strictly_above_null_q95: bool


def evaluate_model(
    model_name: str,
    train_sets: list[CurveDataset],
    test_set: CurveDataset,
    seed: int,
) -> EvaluationResult:
    train_x = np.concatenate([dataset.features for dataset in train_sets], axis=0)
    train_y = np.concatenate([dataset.labels for dataset in train_sets], axis=0)
    model = models(seed)[model_name]
    model.fit(train_x, train_y)
    observed = calibrated_accuracy(model, test_set, test_set.labels)

    rng = random.Random(seed + 991)
    null: list[float] = []
    for trial in range(NULL_TRIALS):
        null_train_y = np.concatenate(
            [random_symmetric_labels(dataset, rng) for dataset in train_sets],
            axis=0,
        )
        null_test_y = random_symmetric_labels(test_set, rng)
        null_model = models(seed + trial + 1)[model_name]
        null_model.fit(train_x, null_train_y)
        null.append(calibrated_accuracy(null_model, test_set, null_test_y))
    null.sort()
    q95 = null[math.ceil(0.95 * NULL_TRIALS) - 1]

    return EvaluationResult(
        model=model_name,
        test_p=test_set.p,
        test_order=test_set.order,
        training_curves=len(train_sets),
        training_points=sum(len(dataset.labels) for dataset in train_sets),
        observed_accuracy=observed,
        observed_advantage=observed - 0.5,
        null_trials=NULL_TRIALS,
        null_median_accuracy=float(np.median(null)),
        null_q95_accuracy=q95,
        empirical_null_percentile=(
            sum(value <= observed for value in null) / NULL_TRIALS
        ),
        strictly_above_null_q95=observed > q95,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("cross_curve_carry_ml_results.json"),
    )
    args = parser.parse_args()

    datasets = sorted(
        [build_dataset(*case) for case in FROZEN_CASES],
        key=lambda dataset: dataset.order,
    )
    test_sets = datasets[-TEST_CASES:]
    results: list[EvaluationResult] = []

    for test_index, test_set in enumerate(test_sets):
        train_sets = [dataset for dataset in datasets if dataset.order < test_set.order]
        if len(train_sets) < MIN_TRAIN_CURVES:
            continue
        for model_name in models(20260812):
            results.append(
                evaluate_model(
                    model_name,
                    train_sets,
                    test_set,
                    seed=20260812 + test_index * 1000,
                )
            )

    by_model: dict[str, list[EvaluationResult]] = {}
    for result in results:
        by_model.setdefault(result.model, []).append(result)

    model_summary = {}
    for model_name, rows in sorted(by_model.items()):
        largest_two = sorted(rows, key=lambda row: row.test_order)[-2:]
        model_summary[model_name] = {
            "evaluations": len(rows),
            "strict_null_q95_exceedances": sum(
                row.strictly_above_null_q95 for row in rows
            ),
            "mean_accuracy": sum(row.observed_accuracy for row in rows) / len(rows),
            "minimum_accuracy": min(row.observed_accuracy for row in rows),
            "largest_order_accuracy": max(rows, key=lambda row: row.test_order).observed_accuracy,
            "largest_two_minimum_advantage": min(
                row.observed_advantage for row in largest_two
            ),
            "admitted_signal": (
                sum(row.strictly_above_null_q95 for row in rows) >= 3
                and min(row.observed_advantage for row in largest_two) >= 0.02
            ),
        }

    payload = {
        "scope": (
            "fifteen frozen j=0 prime-order toy subgroups; smaller curves for "
            "training and strictly larger unseen curves for testing; no external "
            "point, key, wallet, or production target"
        ),
        "package": "CROSS-CURVE-CARRY-ML-018",
        "public_features": (
            "normalized coordinates, GLV coordinate orbit/gaps, Hasse trace, "
            "small fixed division characters; no scalar-derived feature"
        ),
        "models": list(models(20260812)),
        "global_sign_calibration": "prediction at public G, whose carry is known",
        "null_model": "independent random anti-Kummer/C3-invariant labels per curve",
        "evaluations": [asdict(result) for result in results],
        "model_summary": model_summary,
        "aggregate": {
            "curve_datasets": len(datasets),
            "held_out_test_curves": len(test_sets),
            "evaluation_rows": len(results),
            "admitted_models": [
                name for name, row in model_summary.items() if row["admitted_signal"]
            ],
            "largest_order": max(dataset.order for dataset in datasets),
        },
        "acceptance_rule": (
            "the same fixed model must exceed its matched null 95% envelope on "
            "at least three rolling held-out curves and retain at least 2% "
            "advantage on each of the two largest curves"
        ),
        "claim_boundary": [
            "A passed toy gate is only a candidate public predicate and still needs a symbolic formula or fixed circuit export.",
            "No extrapolation to secp256k1 is made without a cross-order scaling law and recovery proof.",
            "A failed gate is not a lower bound against all machine-learned predicates.",
            "No external or production-sized input is accepted.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
