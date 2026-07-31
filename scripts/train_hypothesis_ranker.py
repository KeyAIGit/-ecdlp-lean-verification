#!/usr/bin/env python3
"""Train the small shadow ranker after its independent-label gate is met."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hypothesis_funnel import STATE_PATH as FUNNEL_STATE_PATH, load_policy, sha256_json
from hypothesis_ranker import (
    ENGINE_STATE_PATH,
    ROOT,
    SPEC_PATH,
    STATE_PATH,
    activation_report,
    build_state,
    load_json,
    load_review_ledger,
    review_labels,
    validate_current_review_bindings,
)


def sigmoid(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-max(-60.0, min(60.0, value))))


def normalization(
    rows: list[dict[str, Any]], names: list[str]
) -> dict[str, dict[str, float]]:
    result: dict[str, dict[str, float]] = {}
    for name in names:
        values = [float(row["features"][name]) for row in rows]
        mean = sum(values) / len(values)
        variance = sum((value - mean) ** 2 for value in values) / len(values)
        result[name] = {"mean": mean, "scale": max(1.0, math.sqrt(variance))}
    return result


def fit_logistic(
    rows: list[dict[str, Any]],
    names: list[str],
    algorithm: dict[str, Any],
) -> tuple[float, dict[str, float], dict[str, dict[str, float]]]:
    if not rows or {row["binary_label"] for row in rows} != {0, 1}:
        raise ValueError("ranker training requires both binary classes")
    stats = normalization(rows, names)
    weights = {name: 0.0 for name in names}
    bias = 0.0
    rate = float(algorithm["learning_rate"])
    penalty = float(algorithm["l2_penalty"])
    for _ in range(int(algorithm["iterations"])):
        gradient = {name: 0.0 for name in names}
        bias_gradient = 0.0
        for row in rows:
            values = {
                name: (
                    float(row["features"][name]) - stats[name]["mean"]
                )
                / stats[name]["scale"]
                for name in names
            }
            score = bias + sum(weights[name] * values[name] for name in names)
            error = sigmoid(score) - float(row["binary_label"])
            bias_gradient += error
            for name in names:
                gradient[name] += error * values[name]
        count = float(len(rows))
        bias -= rate * bias_gradient / count
        for name in names:
            regularized = gradient[name] / count + penalty * weights[name]
            weights[name] -= rate * regularized
    return bias, weights, stats


def predict(
    row: dict[str, Any],
    names: list[str],
    bias: float,
    weights: dict[str, float],
    stats: dict[str, dict[str, float]],
) -> float:
    score = bias
    for name in names:
        value = (float(row["features"][name]) - stats[name]["mean"]) / stats[
            name
        ]["scale"]
        score += weights[name] * value
    return sigmoid(score)


def balanced_accuracy(pairs: list[tuple[int, float]]) -> float:
    positives = [score >= 0.5 for label, score in pairs if label == 1]
    negatives = [score < 0.5 for label, score in pairs if label == 0]
    if not positives or not negatives:
        raise ValueError("balanced accuracy requires both classes")
    return 0.5 * (
        sum(positives) / len(positives) + sum(negatives) / len(negatives)
    )


def auc(pairs: list[tuple[int, float]]) -> float:
    positive = [score for label, score in pairs if label == 1]
    negative = [score for label, score in pairs if label == 0]
    if not positive or not negative:
        raise ValueError("AUC requires both classes")
    wins = 0.0
    for pos in positive:
        for neg in negative:
            wins += 1.0 if pos > neg else 0.5 if pos == neg else 0.0
    return wins / (len(positive) * len(negative))


def family_holdout_validation(
    rows: list[dict[str, Any]],
    names: list[str],
    algorithm: dict[str, Any],
) -> dict[str, Any]:
    predictions: list[tuple[int, float]] = []
    evaluated_families: list[str] = []
    skipped_families: list[str] = []
    for family in sorted({row["family"] for row in rows}):
        training = [row for row in rows if row["family"] != family]
        holdout = [row for row in rows if row["family"] == family]
        if {row["binary_label"] for row in training} != {0, 1}:
            skipped_families.append(family)
            continue
        bias, weights, stats = fit_logistic(training, names, algorithm)
        predictions.extend(
            (
                int(row["binary_label"]),
                predict(row, names, bias, weights, stats),
            )
            for row in holdout
        )
        evaluated_families.append(family)
    coverage = len(predictions) / len(rows) if rows else 0.0
    return {
        "protocol": "leave_one_family_out",
        "holdout_coverage": coverage,
        "balanced_accuracy": balanced_accuracy(predictions) if predictions else 0.0,
        "auc": auc(predictions) if predictions else 0.0,
        "evaluated_families": evaluated_families,
        "skipped_families": skipped_families,
        "prediction_count": len(predictions),
    }


def train_model(labels: list[dict[str, Any]], spec: dict[str, Any]) -> dict[str, Any]:
    rows = [row for row in labels if row["training_eligible"]]
    names = spec["feature_contract"]["numeric"]
    algorithm = spec["training_algorithm"]
    validation = family_holdout_validation(rows, names, algorithm)
    gate = spec["validation_gate"]
    failures = []
    if validation["holdout_coverage"] < gate["minimum_holdout_coverage"]:
        failures.append("holdout_coverage")
    if validation["balanced_accuracy"] < gate["minimum_balanced_accuracy"]:
        failures.append("balanced_accuracy")
    if validation["auc"] < gate["minimum_auc"]:
        failures.append("auc")
    validation["passed"] = not failures
    validation["failed_metrics"] = failures
    if failures:
        raise ValueError(f"ranker validation gate failed: {failures}")

    bias, weights, stats = fit_logistic(rows, names, algorithm)
    snapshot = [
        {
            "label_id": row["label_id"],
            "review_record_sha256": row["review_record_sha256"],
            "semantic_signature_sha256": row["semantic_signature_sha256"],
            "binary_label": row["binary_label"],
            "features": row["features"],
        }
        for row in sorted(rows, key=lambda item: item["label_id"])
    ]
    root = sha256_json(snapshot)
    return {
        "schema_version": "1.0",
        "model_id": f"HYPOTHESIS-RANKER-SHADOW-V0-{root[:16].upper()}",
        "model_kind": "linear_logistic_ranker",
        "status": "trained_shadow_validated",
        "trained": True,
        "feature_names": names,
        "normalization": stats,
        "bias": bias,
        "weights": weights,
        "training_snapshot": {
            "eligible_label_count": len(rows),
            "label_snapshot_sha256": root,
            "label_ids": [row["label_id"] for row in snapshot],
            "algorithm": algorithm,
        },
        "validation": validation,
        "selection_influence": False,
        "authorization_capability": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check-ready",
        action="store_true",
        help="report the activation gate without modifying the model",
    )
    args = parser.parse_args()
    spec = load_json(SPEC_PATH)
    policy = load_policy()
    funnel_state = load_json(FUNNEL_STATE_PATH)
    ledger = load_review_ledger()
    validate_current_review_bindings(ledger, policy, funnel_state)
    labels = review_labels(ledger, spec)
    native_outcomes = len(load_json(ENGINE_STATE_PATH).get("native_outcomes", []))
    activation = activation_report(labels, native_outcomes, spec)
    if not activation["ready_for_training"]:
        print(
            "HYP_RANKER_TRAIN_BLOCKED "
            f"unmet={','.join(activation['unmet'])}"
        )
        return 0 if args.check_ready else 2
    if args.check_ready:
        print("HYP_RANKER_TRAIN_READY")
        return 0

    model = train_model(labels, spec)
    model_path = ROOT / spec["model_artifact"]["path"]
    model_path.write_text(
        json.dumps(model, ensure_ascii=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    state = build_state()
    STATE_PATH.write_text(
        json.dumps(state, ensure_ascii=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        "HYP_RANKER_TRAINED "
        f"labels={model['training_snapshot']['eligible_label_count']} "
        f"auc={model['validation']['auc']:.3f} "
        "selection_influence=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
