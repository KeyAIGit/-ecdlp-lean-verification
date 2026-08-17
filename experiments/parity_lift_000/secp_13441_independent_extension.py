#!/usr/bin/env python3
"""Independent extension for the preselected package-025 candidate.

SECP-13441-INDEPENDENT-EXTENSION-026 is a confirmatory toy-only screen.
Package 025 selected exactly one borderline construction before these cases
were evaluated:

    target = carry * half_y
    model  = public HistGradientBoostingClassifier of maximum depth three
    input  = the full frozen 50-dimensional public feature vector

No model, target, feature, threshold, or sign is selected on the extension
cases. The six cases below are the first later deterministic candidates in the
search progression satisfying only public arithmetic criteria:

* p = 80647 modulo 161292, hence p is 3 mod 4, 1 mod 3, and 13441 divides p-1;
* p is prime;
* y^2 = x^3 + 7 contains a prime GLV subgroup with
  200000 <= n <= 2000000, n = 1 mod 3, and gcd(n, p-1) = 1;
* the subgroup generator and its prime order are frozen before model replay.

Each curve uses a new deterministic five-fold partition of complete C6 scalar
orbits. Cross-fitted predictions are compared with 512 fold-preserving label
permutations. The acceptance rule is frozen before execution: at least three
of six curves must exceed their q99 null envelope, and the two largest curves
must each retain at least 0.2 percent balanced advantage.

No external curve, point, key, wallet, or production-sized target is accepted.
"""
from __future__ import annotations

import argparse
import gc
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from sklearn.metrics import balanced_accuracy_score
from sympy import isprime

import secp_13441_character_screen as frozen
import secp_13441_within_curve_cv as lookup
import secp_13441_canonical_orbit_ml_cv as nonlinear

PACKAGE = "SECP-13441-INDEPENDENT-EXTENSION-026"
FOLDS = 5
NULL_TRIALS = 512
MODEL_NAME = "public_hist_gb_depth3"
TARGET = "carry_half_y"
REQUIRED_Q99_EXCEEDANCES = 3
MIN_LARGEST_TWO_ADVANTAGE = 0.002

# (p, subgroup order n, generator, full-curve cofactor, Frobenius trace)
# Full curve order is p + 1 - trace = cofactor * n.
FROZEN_EXTENSION_CASES = (
    (14113051, 1085431, (275359, 6864305), 13, 2449),
    (14919511, 414259, (2608752, 2664509), 36, 6188),
    (28468039, 451837, (17305150, 18762615), 63, 2309),
    (48468247, 932101, (32417074, 5168005), 52, -1004),
    (49435999, 1765741, (7239915, 2924703), 28, -4748),
    (54919927, 677947, (28863717, 33322957), 81, 6221),
)


def robust_is_prime(value: int) -> bool:
    return bool(isprime(value))


def validate_case_metadata(
    p: int,
    order: int,
    generator: tuple[int, int],
    cofactor: int,
    trace: int,
) -> None:
    if not robust_is_prime(p) or not robust_is_prime(order):
        raise AssertionError("frozen field or subgroup order lost primality")
    if p % 4 != 3 or p % 3 != 1 or (p - 1) % frozen.PHASE_ORDER:
        raise AssertionError("frozen field congruence changed")
    if order % 3 != 1 or math.gcd(order, p - 1) != 1:
        raise AssertionError("frozen subgroup no longer satisfies GLV/normalization scope")
    if not (200_000 <= order <= 2_000_000):
        raise AssertionError("frozen extension order left its predeclared interval")
    if p + 1 - trace != cofactor * order:
        raise AssertionError("frozen trace/cofactor certificate changed")
    x, y = generator
    if (y * y - x * x * x - 7) % p != 0:
        raise AssertionError("frozen generator left the curve")
    if frozen.ec_mul(order, generator, p) is not None:
        raise AssertionError("frozen generator order certificate failed")


def fold_preserving_null(
    labels: np.ndarray,
    predictions: np.ndarray,
    folds: np.ndarray,
    seed: int,
) -> list[float]:
    rng = np.random.default_rng(seed)
    fold_indices = [np.flatnonzero(folds == fold) for fold in range(FOLDS)]
    distribution: list[float] = []
    shuffled = np.empty_like(labels)
    for _ in range(NULL_TRIALS):
        for indices in fold_indices:
            shuffled[indices] = labels[indices][rng.permutation(len(indices))]
        distribution.append(
            float(balanced_accuracy_score(shuffled, predictions))
        )
    distribution.sort()
    return distribution


@dataclass(frozen=True)
class Evaluation:
    p: int
    order: int
    generator: tuple[int, int]
    full_curve_order: int
    cofactor: int
    trace: int
    point_scale_character: int
    orbit_count: int
    public_feature_count: int
    phase_feature_count: int
    folds: int
    target: str
    model: str
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


def evaluate_case(
    p: int,
    order: int,
    generator: tuple[int, int],
    cofactor: int,
    trace: int,
) -> Evaluation:
    validate_case_metadata(p, order, generator, cofactor, trace)
    curve = frozen.build_case(p, order, generator)
    features, phase_feature_count = nonlinear.public_orbit_features(curve)
    _phases, labels = lookup.invariant_orbit_data(curve, TARGET)
    if len(labels) != curve.orbit_count or len(features) != len(labels):
        raise AssertionError("extension feature/label/orbit counts diverged")

    folds = nonlinear.fold_assignment(
        len(labels), seed=20260826 + 97 * p + order
    )
    predictions = nonlinear.cross_fitted_predictions(
        features,
        labels,
        folds,
        MODEL_NAME,
        phase_feature_count,
        seed=20260826 + p + 10_000 * order,
    )
    observed_accuracy = float(np.mean(predictions == labels))
    observed_balanced = float(
        balanced_accuracy_score(labels, predictions)
    )
    null = fold_preserving_null(
        labels,
        predictions,
        folds,
        seed=20260826 + order + 13 * p,
    )
    q95 = null[math.ceil(0.95 * NULL_TRIALS) - 1]
    q99 = null[math.ceil(0.99 * NULL_TRIALS) - 1]
    null_mean = float(np.mean(null))
    null_std = float(np.std(null, ddof=1))
    z_score = (
        (observed_balanced - null_mean) / null_std
        if null_std > 0.0
        else math.inf
    )
    empirical_upper_p = (
        1 + sum(value >= observed_balanced for value in null)
    ) / (NULL_TRIALS + 1)

    evaluation = Evaluation(
        p=p,
        order=order,
        generator=generator,
        full_curve_order=cofactor * order,
        cofactor=cofactor,
        trace=trace,
        point_scale_character=curve.point_scale_character,
        orbit_count=curve.orbit_count,
        public_feature_count=features.shape[1],
        phase_feature_count=phase_feature_count,
        folds=FOLDS,
        target=TARGET,
        model=MODEL_NAME,
        positive_fraction=float(np.mean(labels == 1)),
        observed_accuracy=observed_accuracy,
        observed_balanced_accuracy=observed_balanced,
        observed_balanced_advantage=observed_balanced - 0.5,
        null_trials=NULL_TRIALS,
        null_mean_balanced_accuracy=null_mean,
        null_std_balanced_accuracy=null_std,
        null_q95_balanced_accuracy=q95,
        null_q99_balanced_accuracy=q99,
        empirical_upper_p=empirical_upper_p,
        z_score=z_score,
        strictly_above_null_q95=observed_balanced > q95,
        strictly_above_null_q99=observed_balanced > q99,
    )

    del curve, features, labels, predictions, folds, null
    gc.collect()
    return evaluation


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "secp_13441_independent_extension_results.json"
        ),
    )
    args = parser.parse_args()

    frozen.is_prime = robust_is_prime
    evaluations = [
        evaluate_case(p, order, generator, cofactor, trace)
        for p, order, generator, cofactor, trace in FROZEN_EXTENSION_CASES
    ]
    evaluations.sort(key=lambda row: row.order)

    q95_exceedances = sum(
        row.strictly_above_null_q95 for row in evaluations
    )
    q99_exceedances = sum(
        row.strictly_above_null_q99 for row in evaluations
    )
    largest_two = evaluations[-2:]
    largest_two_min_advantage = min(
        row.observed_balanced_advantage for row in largest_two
    )
    admitted = (
        q99_exceedances >= REQUIRED_Q99_EXCEEDANCES
        and largest_two_min_advantage >= MIN_LARGEST_TWO_ADVANTAGE
    )

    payload = {
        "scope": (
            "six independent frozen j=0 prime-order toy subgroups selected "
            "by public arithmetic criteria before replay of the preselected "
            "package-025 classifier; no external point, key, wallet, or "
            "production-sized target"
        ),
        "package": PACKAGE,
        "preselected_candidate": {
            "target": TARGET,
            "model": MODEL_NAME,
            "feature_family": "all fifty frozen public C6-invariant features",
            "source_package": "SECP-13441-CANONICAL-ORBIT-ML-025",
        },
        "extension_selection_rule": (
            "first six later deterministic search cases with p=80647 mod "
            "161292 and a prime GLV subgroup between 200000 and 2000000, "
            "without inspecting model predictions or target correlation"
        ),
        "frozen_cases": [
            {
                "p": p,
                "order": order,
                "generator": generator,
                "cofactor": cofactor,
                "trace": trace,
                "full_curve_order": cofactor * order,
            }
            for p, order, generator, cofactor, trace in FROZEN_EXTENSION_CASES
        ],
        "evaluations": [asdict(row) for row in evaluations],
        "aggregate": {
            "cases": len(evaluations),
            "q95_exceedances": q95_exceedances,
            "q99_exceedances": q99_exceedances,
            "z_ge_3_exceedances": sum(row.z_score >= 3.0 for row in evaluations),
            "mean_balanced_accuracy": sum(
                row.observed_balanced_accuracy for row in evaluations
            ) / len(evaluations),
            "minimum_balanced_accuracy": min(
                row.observed_balanced_accuracy for row in evaluations
            ),
            "largest_order": evaluations[-1].order,
            "largest_order_balanced_accuracy": (
                evaluations[-1].observed_balanced_accuracy
            ),
            "largest_two_minimum_balanced_advantage": (
                largest_two_min_advantage
            ),
            "minimum_empirical_upper_p": min(
                row.empirical_upper_p for row in evaluations
            ),
            "admitted_signal": admitted,
        },
        "acceptance_rule": (
            "the one preselected target/model/feature construction must exceed "
            "its fold-preserving permutation-null q99 envelope on at least "
            "three of six independent curves and retain at least 0.2 percent "
            "balanced advantage on both largest extension curves"
        ),
        "decision": (
            "Independent extension gate passed; exact ablation and fixed-circuit follow-up are required."
            if admitted
            else "Independent extension gate did not pass."
        ),
        "claim_boundary": [
            "The extension cases were selected by field and subgroup arithmetic, not by classifier performance.",
            "Exactly one target, model, feature family, sign convention, and gate were carried forward from package 025.",
            "Each test partition is a disjoint union of complete C6 scalar orbits.",
            "Cross-fitted predictions are frozen before the fold-preserving permutation null is generated.",
            "A passed toy extension is not a secp256k1 theorem and still needs a scaling law and recovery proof.",
            "A failed extension does not prove a lower bound against arbitrary public circuits.",
            "No external or production-sized input is accepted.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
