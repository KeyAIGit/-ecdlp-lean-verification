#!/usr/bin/env python3
"""Streaming preregistered linear probes over synthetic secp256k1 pairs.

The probe is intentionally weak and interpretable.  Its purpose is to detect
gross representation leakage and qualify the measurement pipeline before any
neural or program-synthesis search.  A null result is only a null result for
these features and this model class.  A positive result is only a signal that
must be replicated and converted into an explicit mechanism.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import numpy as np
import sklearn
from sklearn.linear_model import SGDClassifier


RECORD_SIZE = 65


@dataclass(frozen=True)
class Batch:
    scalars: np.ndarray
    public: np.ndarray
    global_start: int


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def iter_batches(
    manifest: dict,
    dataset_root: Path,
    split: str,
    batch_records: int,
) -> Iterator[Batch]:
    shards = sorted(
        (item for item in manifest["shards"] if item["split"] == split),
        key=lambda item: item["part"],
    )
    for shard in shards:
        path = dataset_root / shard["relative_path"]
        raw = np.fromfile(path, dtype=np.uint8).reshape((-1, RECORD_SIZE))
        start = int(shard["start_index"])
        for offset in range(0, len(raw), batch_records):
            chunk = raw[offset : offset + batch_records]
            yield Batch(
                scalars=chunk[:, :32],
                public=chunk[:, 32:],
                global_start=start + offset,
            )


def public_features(public: np.ndarray) -> np.ndarray:
    return np.unpackbits(public, axis=1, bitorder="big").astype(np.float32)


def scalar_bit(scalars: np.ndarray, bit: int) -> np.ndarray:
    byte_index = 31 - bit // 8
    shift = bit % 8
    return ((scalars[:, byte_index] >> shift) & 1).astype(np.int64)


def scalar_mod(scalars: np.ndarray, modulus: int) -> np.ndarray:
    values = np.zeros(len(scalars), dtype=np.int64)
    for column in range(32):
        values = (values * 256 + scalars[:, column].astype(np.int64)) % modulus
    return values


def deterministic_null_labels(split: str, start: int, count: int) -> np.ndarray:
    split_tag = int.from_bytes(hashlib.sha256(split.encode("ascii")).digest()[:8], "big")
    indices = np.arange(start, start + count, dtype=np.uint64)
    values = indices ^ np.uint64(split_tag)
    values ^= values >> np.uint64(12)
    values ^= values << np.uint64(25)
    values ^= values >> np.uint64(27)
    values *= np.uint64(2685821657736338717)
    return (values & np.uint64(1)).astype(np.int64)


def labels_for_task(task: str, batch: Batch) -> np.ndarray:
    if task == "d_bit_0" or task == "canary_scalar_leak":
        return scalar_bit(batch.scalars, 0)
    if task == "d_bit_127":
        return scalar_bit(batch.scalars, 127)
    if task == "d_mod_3":
        return scalar_mod(batch.scalars, 3)
    if task == "canary_public_y_parity":
        return (batch.public[:, 0] - 2).astype(np.int64)
    if task == "permuted_d_bit_0":
        return deterministic_null_labels(
            "null", batch.global_start, len(batch.scalars)
        )
    raise ValueError(f"unknown task: {task}")


def classes_for_task(task: str) -> np.ndarray:
    return np.array([0, 1, 2], dtype=np.int64) if task == "d_mod_3" else np.array([0, 1])


def features_for_task(task: str, batch: Batch) -> np.ndarray:
    features = public_features(batch.public)
    if task == "canary_scalar_leak":
        leak = scalar_bit(batch.scalars, 0).astype(np.float32).reshape((-1, 1))
        features = np.concatenate((features, leak), axis=1)
    return features


def fit_task(
    task: str,
    config: dict,
    manifest: dict,
    dataset_root: Path,
) -> tuple[SGDClassifier, np.ndarray]:
    probe = config["probe"]
    model = SGDClassifier(
        loss="log_loss",
        penalty="l2",
        alpha=float(probe["alpha"]),
        fit_intercept=True,
        learning_rate="constant",
        eta0=float(probe["eta0"]),
        average=True,
        random_state=int(probe["random_state"]),
        shuffle=False,
    )
    classes = classes_for_task(task)
    class_counts = np.zeros(len(classes), dtype=np.int64)
    first = True
    for _epoch in range(int(probe["epochs"])):
        for batch in iter_batches(
            manifest,
            dataset_root,
            "train",
            int(probe["batch_records"]),
        ):
            labels = labels_for_task(task, batch)
            if _epoch == 0:
                class_counts += np.bincount(labels, minlength=len(classes))
            features = features_for_task(task, batch)
            if first:
                model.partial_fit(features, labels, classes=classes)
                first = False
            else:
                model.partial_fit(features, labels)
    return model, class_counts


def evaluate_task(
    model: SGDClassifier,
    task: str,
    split: str,
    config: dict,
    manifest: dict,
    dataset_root: Path,
    train_class_counts: np.ndarray,
) -> dict:
    classes = classes_for_task(task)
    priors = (train_class_counts + 1.0) / (
        train_class_counts.sum() + len(train_class_counts)
    )
    correct = 0
    total = 0
    model_log_loss_sum = 0.0
    null_log_loss_sum = 0.0
    observed_counts = np.zeros(len(classes), dtype=np.int64)

    for batch in iter_batches(
        manifest,
        dataset_root,
        split,
        int(config["probe"]["batch_records"]),
    ):
        labels = labels_for_task(task, batch)
        features = features_for_task(task, batch)
        probabilities = model.predict_proba(features)
        if not np.isfinite(probabilities).all():
            raise FloatingPointError(f"non-finite probability for task {task}")
        probabilities = np.clip(probabilities, 1e-12, 1.0)
        probabilities /= probabilities.sum(axis=1, keepdims=True)
        predictions = classes[np.argmax(probabilities, axis=1)]
        correct += int(np.count_nonzero(predictions == labels))
        total += len(labels)
        observed_counts += np.bincount(labels, minlength=len(classes))
        model_log_loss_sum += float(
            -np.log(probabilities[np.arange(len(labels)), labels]).sum()
        )
        null_log_loss_sum += float(-np.log(priors[labels]).sum())

    accuracy = correct / total
    observed_priors = observed_counts / total
    null_accuracy = float(np.max(observed_priors))
    null_variance = max(null_accuracy * (1 - null_accuracy), 1e-12)
    accuracy_z = (accuracy - null_accuracy) / math.sqrt(null_variance / total)
    model_log_loss = model_log_loss_sum / total
    null_log_loss = null_log_loss_sum / total
    information_gain_bits = (null_log_loss - model_log_loss) / math.log(2)
    return {
        "records": total,
        "class_counts": [int(value) for value in observed_counts],
        "accuracy": accuracy,
        "null_accuracy": null_accuracy,
        "accuracy_lift": accuracy - null_accuracy,
        "accuracy_z": accuracy_z,
        "log_loss_nats": model_log_loss,
        "null_log_loss_nats": null_log_loss,
        "information_gain_bits_per_record": information_gain_bits,
    }


def crossed_threshold(result: dict, probe: dict) -> bool:
    return (
        result["information_gain_bits_per_record"]
        >= float(probe["minimum_information_gain_bits"])
        and result["accuracy_lift"] >= float(probe["minimum_accuracy_lift"])
        and result["accuracy_z"] >= float(probe["minimum_accuracy_z"])
    )


def run_probe(config_path: Path, manifest_path: Path) -> dict:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    dataset_root = manifest_path.parent
    tasks = list(config["probe"]["tasks"])
    task_results = {}

    for task in tasks:
        model, train_counts = fit_task(task, config, manifest, dataset_root)
        validation = evaluate_task(
            model,
            task,
            "validation",
            config,
            manifest,
            dataset_root,
            train_counts,
        )
        test = evaluate_task(
            model,
            task,
            "test",
            config,
            manifest,
            dataset_root,
            train_counts,
        )
        task_results[task] = {
            "classes": [int(value) for value in classes_for_task(task)],
            "train_class_counts": [int(value) for value in train_counts],
            "feature_count": int(model.coef_.shape[1]),
            "coefficient_l2": float(np.linalg.norm(model.coef_)),
            "validation": validation,
            "test": test,
            "threshold_crossed_both_splits": crossed_threshold(
                validation, config["probe"]
            )
            and crossed_threshold(test, config["probe"]),
        }

    canaries = ("canary_public_y_parity", "canary_scalar_leak")
    canaries_pass = all(
        task_results[name]["threshold_crossed_both_splits"] for name in canaries
    )
    null_pass = not task_results["permuted_d_bit_0"]["threshold_crossed_both_splits"]
    scientific_tasks = ("d_bit_0", "d_bit_127", "d_mod_3")
    signals = [
        name
        for name in scientific_tasks
        if task_results[name]["threshold_crossed_both_splits"]
    ]
    return {
        "schema_version": 1,
        "experiment_id": config["experiment_id"],
        "result_role": "engineering_qualification_and_linear_representation_screen",
        "scientific_evidence": False,
        "manifest_sha256": sha256_file(manifest_path),
        "config_sha256": sha256_file(config_path),
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scikit_learn": sklearn.__version__,
        },
        "model": {
            "family": "streaming linear logistic probe",
            "implementation": "sklearn.linear_model.SGDClassifier",
            "features": config["probe"]["feature_mode"],
            "epochs": config["probe"]["epochs"],
            "alpha": config["probe"]["alpha"],
            "eta0": config["probe"]["eta0"],
            "random_state": config["probe"]["random_state"],
        },
        "thresholds": {
            "information_gain_bits_per_record": config["probe"][
                "minimum_information_gain_bits"
            ],
            "accuracy_lift": config["probe"]["minimum_accuracy_lift"],
            "accuracy_z": config["probe"]["minimum_accuracy_z"],
            "must_replicate_on": ["validation", "test"],
        },
        "pipeline_status": "pass" if canaries_pass and null_pass else "fail",
        "canaries_pass": canaries_pass,
        "permuted_null_pass": null_pass,
        "representation_signals_requiring_new_candidate": signals,
        "interpretation": (
            "signal_requires_replication_symbolic_extraction_and_candidate_gates"
            if signals
            else "no_material_linear_signal_at_preregistered_threshold"
        ),
        "scope": [
            "No claim about nonlinear, neural, gradient-free, or program-synthesis models.",
            "No claim that ECDLP is learnable or unlearnable.",
            "No route promotion, exact-target recovery attempt, or asymptotic inference.",
            "Canaries deliberately contain direct information and are not scientific tasks.",
        ],
        "tasks": task_results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run_probe(args.config.resolve(), args.manifest.resolve())
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["pipeline_status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
