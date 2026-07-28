#!/usr/bin/env python3
"""Budgeted AutoML assay for synthetic secp256k1 representation probes.

The search is deliberately narrower than a general AutoML service.  It uses
successive halving on the training and validation splits, records every
attempt, and evaluates exactly one selected model per scientific task on the
test split.  The output is an engineering observation, never a key-recovery
claim or a Research Engine candidate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import subprocess
import time
import warnings
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import sklearn
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier
from sklearn.kernel_approximation import RBFSampler
from sklearn.linear_model import SGDClassifier
from sklearn.naive_bayes import BernoulliNB
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RECORD_SIZE = 65
SCIENTIFIC_TASKS = ("d_bit_0", "d_bit_127", "d_mod_3")
CONTROL_TASKS = (
    "canary_public_y_parity",
    "canary_scalar_leak",
    "permuted_d_bit_0",
)


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_state() -> dict[str, Any]:
    def run(*args: str) -> str:
        completed = subprocess.run(
            args,
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return completed.stdout.strip()

    try:
        return {
            "commit": run("git", "rev-parse", "HEAD"),
            "tracked_files_dirty": bool(
                run("git", "status", "--porcelain", "--untracked-files=no")
            ),
        }
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "tracked_files_dirty": None}


def load_config(path: Path) -> dict[str, Any]:
    config = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "schema_version",
        "experiment_id",
        "random_state",
        "scientific_tasks",
        "rounds",
        "recipes",
        "controls",
        "thresholds",
    }
    missing = sorted(required - set(config))
    if missing:
        raise ValueError(f"AutoML config missing fields: {missing}")
    if config["schema_version"] != 1:
        raise ValueError("unsupported AutoML config schema_version")
    tasks = tuple(config["scientific_tasks"])
    if not tasks or any(task not in SCIENTIFIC_TASKS for task in tasks):
        raise ValueError(f"scientific_tasks must be selected from {SCIENTIFIC_TASKS}")
    round_names = [item["name"] for item in config["rounds"]]
    if len(round_names) != len(set(round_names)) or not round_names:
        raise ValueError("round names must be unique and nonempty")
    recipe_ids = [item["id"] for item in config["recipes"]]
    if len(recipe_ids) != len(set(recipe_ids)) or not recipe_ids:
        raise ValueError("recipe ids must be unique and nonempty")
    for recipe in config["recipes"]:
        recipe_tasks = recipe.get("tasks", tasks)
        if not recipe_tasks or any(task not in tasks for task in recipe_tasks):
            raise ValueError(
                f"recipe {recipe['id']} has tasks outside scientific_tasks"
            )
    for round_config in config["rounds"]:
        for field in ("train_records", "validation_records", "survivors_per_task"):
            if int(round_config[field]) <= 0:
                raise ValueError(f"round {round_config['name']} has invalid {field}")
    return config


def load_split(
    manifest: dict[str, Any],
    dataset_root: Path,
    split: str,
    limit: int,
) -> np.ndarray:
    split_total = int(manifest["splits"][split])
    requested = min(int(limit), split_total)
    pieces: list[np.ndarray] = []
    remaining = requested
    shards = sorted(
        (item for item in manifest["shards"] if item["split"] == split),
        key=lambda item: int(item["part"]),
    )
    for shard in shards:
        if remaining <= 0:
            break
        path = dataset_root / shard["relative_path"]
        records = np.fromfile(path, dtype=np.uint8).reshape((-1, RECORD_SIZE))
        take = min(remaining, len(records))
        pieces.append(records[:take])
        remaining -= take
    if remaining:
        raise ValueError(
            f"split {split} is short: requested {requested}, missing {remaining}"
        )
    return np.concatenate(pieces, axis=0) if pieces else np.empty((0, RECORD_SIZE))


def scalar_bit(scalars: np.ndarray, bit: int) -> np.ndarray:
    byte_index = 31 - bit // 8
    shift = bit % 8
    return ((scalars[:, byte_index] >> shift) & 1).astype(np.int64)


def scalar_mod(scalars: np.ndarray, modulus: int) -> np.ndarray:
    values = np.zeros(len(scalars), dtype=np.int64)
    for column in range(32):
        values = (values * 256 + scalars[:, column].astype(np.int64)) % modulus
    return values


def null_labels(start: int, count: int) -> np.ndarray:
    tag = int.from_bytes(hashlib.sha256(b"automl-null-v1").digest()[:8], "big")
    indices = np.arange(start, start + count, dtype=np.uint64)
    values = indices ^ np.uint64(tag)
    values ^= values >> np.uint64(12)
    values ^= values << np.uint64(25)
    values ^= values >> np.uint64(27)
    values *= np.uint64(2685821657736338717)
    return (values & np.uint64(1)).astype(np.int64)


def labels_for_task(task: str, records: np.ndarray) -> np.ndarray:
    scalars = records[:, :32]
    public = records[:, 32:]
    if task in ("d_bit_0", "canary_scalar_leak"):
        return scalar_bit(scalars, 0)
    if task == "d_bit_127":
        return scalar_bit(scalars, 127)
    if task == "d_mod_3":
        return scalar_mod(scalars, 3)
    if task == "canary_public_y_parity":
        return (public[:, 0] - 2).astype(np.int64)
    if task == "permuted_d_bit_0":
        return null_labels(0, len(records))
    raise ValueError(f"unknown task: {task}")


def classes_for_task(task: str) -> np.ndarray:
    if task == "d_mod_3":
        return np.array([0, 1, 2], dtype=np.int64)
    return np.array([0, 1], dtype=np.int64)


def transform_features(mode: str, records: np.ndarray) -> np.ndarray:
    public = records[:, 32:]
    if mode == "compressed_bits":
        return np.unpackbits(public, axis=1, bitorder="big").astype(np.float32)
    if mode == "compressed_bytes":
        return public.astype(np.float32) / np.float32(255.0)
    if mode == "x_limbs16":
        x = public[:, 1:].astype(np.uint16)
        limbs = (x[:, 0::2] << 8) | x[:, 1::2]
        parity = (public[:, 0] - 2).astype(np.float32).reshape((-1, 1))
        return np.concatenate(
            (parity, limbs.astype(np.float32) / np.float32(65535.0)), axis=1
        )
    if mode == "byte_popcounts":
        bits = np.unpackbits(public, axis=1, bitorder="big").reshape((-1, 33, 8))
        counts = bits.sum(axis=2, dtype=np.uint8).astype(np.float32) / 8.0
        return counts
    raise ValueError(f"unknown feature mode: {mode}")


def build_estimator(
    recipe: dict[str, Any],
    random_state: int,
    jobs: int,
) -> Any:
    family = recipe["family"]
    params = dict(recipe.get("params", {}))
    if family == "sgd_logistic":
        return SGDClassifier(
            loss="log_loss",
            penalty=params.get("penalty", "l2"),
            alpha=float(params["alpha"]),
            learning_rate="constant",
            eta0=float(params["eta0"]),
            max_iter=int(params.get("epochs", 3)),
            tol=None,
            average=True,
            fit_intercept=True,
            shuffle=True,
            random_state=random_state,
        )
    if family == "bernoulli_nb":
        return BernoulliNB(
            alpha=float(params["alpha"]),
            fit_prior=True,
            force_alpha=True,
        )
    if family == "extra_trees":
        return ExtraTreesClassifier(
            n_estimators=int(params.get("n_estimators", 64)),
            max_depth=(
                None if params.get("max_depth") is None else int(params["max_depth"])
            ),
            min_samples_leaf=int(params.get("min_samples_leaf", 1)),
            max_features=params.get("max_features", "sqrt"),
            criterion="log_loss",
            n_jobs=jobs,
            random_state=random_state,
        )
    if family == "hist_gbdt":
        return HistGradientBoostingClassifier(
            learning_rate=float(params["learning_rate"]),
            max_iter=int(params["max_iter"]),
            max_leaf_nodes=int(params["max_leaf_nodes"]),
            min_samples_leaf=int(params.get("min_samples_leaf", 20)),
            l2_regularization=float(params.get("l2_regularization", 0.0)),
            early_stopping=False,
            random_state=random_state,
        )
    if family == "mlp":
        return MLPClassifier(
            hidden_layer_sizes=tuple(int(value) for value in params["hidden_layers"]),
            activation=params.get("activation", "relu"),
            solver="adam",
            alpha=float(params["alpha"]),
            batch_size=int(params.get("batch_size", 1024)),
            learning_rate_init=float(params.get("learning_rate_init", 0.001)),
            max_iter=int(params.get("epochs", 5)),
            tol=0.0,
            n_iter_no_change=int(params.get("epochs", 5)) + 1,
            early_stopping=False,
            shuffle=True,
            random_state=random_state,
        )
    if family == "rbf_sgd":
        return make_pipeline(
            RBFSampler(
                gamma=float(params["gamma"]),
                n_components=int(params.get("n_components", 128)),
                random_state=random_state,
            ),
            SGDClassifier(
                loss="log_loss",
                penalty="l2",
                alpha=float(params["alpha"]),
                learning_rate="constant",
                eta0=float(params["eta0"]),
                max_iter=int(params.get("epochs", 3)),
                tol=None,
                average=True,
                shuffle=True,
                random_state=random_state,
            ),
        )
    raise ValueError(f"unknown estimator family: {family}")


def evaluate_model(
    model: Any,
    features: np.ndarray,
    labels: np.ndarray,
    train_counts: np.ndarray,
    classes: np.ndarray,
    batch_records: int,
) -> dict[str, Any]:
    model_classes = np.asarray(model.classes_, dtype=np.int64)
    class_to_column = {int(value): index for index, value in enumerate(classes)}
    probabilities_sum = 0.0
    correct = 0
    total = 0
    observed_counts = np.zeros(len(classes), dtype=np.int64)
    priors = (train_counts + 1.0) / (train_counts.sum() + len(classes))
    null_log_loss_sum = 0.0

    for start in range(0, len(labels), batch_records):
        stop = min(start + batch_records, len(labels))
        batch_labels = labels[start:stop]
        raw_probabilities = np.asarray(
            model.predict_proba(features[start:stop]), dtype=np.float64
        )
        probabilities = np.zeros((len(batch_labels), len(classes)), dtype=np.float64)
        for model_column, class_value in enumerate(model_classes):
            probabilities[:, class_to_column[int(class_value)]] = raw_probabilities[
                :, model_column
            ]
        if not np.isfinite(probabilities).all():
            raise FloatingPointError("model emitted a non-finite probability")
        probabilities = np.clip(probabilities, 1e-12, 1.0)
        probabilities /= probabilities.sum(axis=1, keepdims=True)
        label_columns = np.fromiter(
            (class_to_column[int(value)] for value in batch_labels),
            dtype=np.int64,
            count=len(batch_labels),
        )
        predictions = classes[np.argmax(probabilities, axis=1)]
        correct += int(np.count_nonzero(predictions == batch_labels))
        probabilities_sum += float(
            -np.log(probabilities[np.arange(len(batch_labels)), label_columns]).sum()
        )
        null_log_loss_sum += float(-np.log(priors[label_columns]).sum())
        observed_counts += np.bincount(batch_labels, minlength=len(classes))
        total += len(batch_labels)

    accuracy = correct / total
    null_accuracy = float(np.max(observed_counts / total))
    variance = max(null_accuracy * (1.0 - null_accuracy), 1e-12)
    accuracy_z = (accuracy - null_accuracy) / math.sqrt(variance / total)
    log_loss_nats = probabilities_sum / total
    null_log_loss_nats = null_log_loss_sum / total
    return {
        "records": total,
        "class_counts": [int(value) for value in observed_counts],
        "accuracy": accuracy,
        "null_accuracy": null_accuracy,
        "accuracy_lift": accuracy - null_accuracy,
        "accuracy_z": accuracy_z,
        "log_loss_nats": log_loss_nats,
        "null_log_loss_nats": null_log_loss_nats,
        "information_gain_bits_per_record": (
            null_log_loss_nats - log_loss_nats
        )
        / math.log(2),
    }


def fit_and_evaluate(
    recipe: dict[str, Any],
    task: str,
    train_records: np.ndarray,
    validation_records: np.ndarray,
    feature_cache: dict[tuple[str, str], np.ndarray],
    random_state: int,
    jobs: int,
    batch_records: int,
) -> tuple[Any, dict[str, Any]]:
    feature_mode = recipe["feature_mode"]
    train_limit = min(
        len(train_records),
        int(recipe.get("max_train_records", len(train_records))),
    )
    train_features = feature_cache[("train", feature_mode)][:train_limit]
    validation_features = feature_cache[("validation", feature_mode)]
    train_labels = labels_for_task(task, train_records[:train_limit])
    validation_labels = labels_for_task(task, validation_records)
    classes = classes_for_task(task)
    train_counts = np.bincount(train_labels, minlength=len(classes))
    model = build_estimator(recipe, random_state, jobs)

    started = time.perf_counter()
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        model.fit(train_features, train_labels)
    fit_seconds = time.perf_counter() - started
    started = time.perf_counter()
    metrics = evaluate_model(
        model,
        validation_features,
        validation_labels,
        train_counts,
        classes,
        batch_records,
    )
    evaluation_seconds = time.perf_counter() - started
    warning_messages = [
        f"{item.category.__name__}: {str(item.message)[:240]}" for item in captured
    ]
    return model, {
        "train_records": train_limit,
        "validation_records": len(validation_records),
        "train_class_counts": [int(value) for value in train_counts],
        "fit_seconds": fit_seconds,
        "evaluation_seconds": evaluation_seconds,
        "warnings": warning_messages,
        "validation": metrics,
    }


def crossed_threshold(metrics: dict[str, Any], thresholds: dict[str, Any]) -> bool:
    return (
        metrics["information_gain_bits_per_record"]
        >= float(thresholds["minimum_information_gain_bits"])
        and metrics["accuracy_lift"] >= float(thresholds["minimum_accuracy_lift"])
        and metrics["accuracy_z"] >= float(thresholds["minimum_accuracy_z"])
    )


def select_survivors(
    entries: list[dict[str, Any]],
    count: int,
    preserve_family_diversity: bool,
) -> list[dict[str, Any]]:
    completed = [item for item in entries if item["status"] == "completed"]
    ranked = sorted(
        completed,
        key=lambda item: (
            item["validation"]["information_gain_bits_per_record"],
            item["validation"]["accuracy_lift"],
            -item["fit_seconds"],
            item["recipe_id"],
        ),
        reverse=True,
    )
    if not preserve_family_diversity:
        return ranked[:count]
    selected: list[dict[str, Any]] = []
    seen_families: set[str] = set()
    for item in ranked:
        if item["family"] not in seen_families:
            selected.append(item)
            seen_families.add(item["family"])
            if len(selected) == count:
                return selected
    selected_ids = {item["recipe_id"] for item in selected}
    for item in ranked:
        if item["recipe_id"] not in selected_ids:
            selected.append(item)
            if len(selected) == count:
                break
    return selected


def append_ledger(path: Path, entry: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")
        handle.flush()


def run_controls(
    config: dict[str, Any],
    manifest: dict[str, Any],
    dataset_root: Path,
    ledger_path: Path,
) -> dict[str, Any]:
    control_config = config["controls"]
    train_records = load_split(
        manifest,
        dataset_root,
        "train",
        int(control_config["train_records"]),
    )
    validation_records = load_split(
        manifest,
        dataset_root,
        "validation",
        int(control_config["validation_records"]),
    )
    test_records = load_split(
        manifest,
        dataset_root,
        "test",
        int(control_config["test_records"]),
    )
    base_recipe = {
        "id": "fixed_control_logistic",
        "family": "sgd_logistic",
        "feature_mode": "compressed_bits",
        "params": {
            "alpha": control_config["alpha"],
            "eta0": control_config["eta0"],
            "epochs": control_config["epochs"],
        },
    }
    public_features = {
        split: transform_features("compressed_bits", records)
        for split, records in (
            ("train", train_records),
            ("validation", validation_records),
            ("test", test_records),
        )
    }
    output: dict[str, Any] = {}
    for task in CONTROL_TASKS:
        train_labels = labels_for_task(task, train_records)
        validation_labels = labels_for_task(task, validation_records)
        test_labels = labels_for_task(task, test_records)
        train_features = public_features["train"]
        validation_features = public_features["validation"]
        test_features = public_features["test"]
        if task == "canary_scalar_leak":
            train_features = np.concatenate(
                (train_features, train_labels.astype(np.float32).reshape((-1, 1))),
                axis=1,
            )
            validation_features = np.concatenate(
                (
                    validation_features,
                    validation_labels.astype(np.float32).reshape((-1, 1)),
                ),
                axis=1,
            )
            test_features = np.concatenate(
                (test_features, test_labels.astype(np.float32).reshape((-1, 1))),
                axis=1,
            )
        model = build_estimator(
            base_recipe,
            int(config["random_state"]),
            int(config.get("jobs", 1)),
        )
        classes = classes_for_task(task)
        counts = np.bincount(train_labels, minlength=len(classes))
        started = time.perf_counter()
        with warnings.catch_warnings(record=True) as captured:
            warnings.simplefilter("always")
            model.fit(train_features, train_labels)
        fit_seconds = time.perf_counter() - started
        validation = evaluate_model(
            model,
            validation_features,
            validation_labels,
            counts,
            classes,
            int(config["prediction_batch_records"]),
        )
        test = evaluate_model(
            model,
            test_features,
            test_labels,
            counts,
            classes,
            int(config["prediction_batch_records"]),
        )
        entry = {
            "run_id": f"control/{task}/fixed_control_logistic",
            "stage": "control",
            "task": task,
            "recipe_id": "fixed_control_logistic",
            "family": "sgd_logistic",
            "feature_mode": (
                "compressed_bits_plus_deliberate_scalar_leak"
                if task == "canary_scalar_leak"
                else "compressed_bits"
            ),
            "status": "completed",
            "fit_seconds": fit_seconds,
            "warnings": [
                f"{item.category.__name__}: {str(item.message)[:240]}"
                for item in captured
            ],
            "validation": validation,
            "test": test,
        }
        append_ledger(ledger_path, entry)
        output[task] = entry
    thresholds = config["thresholds"]
    canaries_pass = all(
        crossed_threshold(output[task]["validation"], thresholds)
        and crossed_threshold(output[task]["test"], thresholds)
        for task in ("canary_public_y_parity", "canary_scalar_leak")
    )
    null_pass = not (
        crossed_threshold(output["permuted_d_bit_0"]["validation"], thresholds)
        and crossed_threshold(output["permuted_d_bit_0"]["test"], thresholds)
    )
    return {
        "canaries_pass": canaries_pass,
        "permuted_null_pass": null_pass,
        "tasks": output,
    }


def markdown_report(result: dict[str, Any]) -> str:
    lines = [
        f"# {result['experiment_id']} AutoML qualification",
        "",
        "This report is a route-neutral engineering observation. It is not a "
        "discrete-log solution, a complexity claim, or a Research Engine candidate.",
        "",
        "## Outcome",
        "",
        f"- Pipeline status: `{result['pipeline_status']}`",
        f"- Dataset records: `{result['dataset']['total_records']:,}`",
        f"- AutoML attempts completed: `{result['run_summary']['completed']}`",
        f"- AutoML attempts failed: `{result['run_summary']['failed']}`",
        f"- Controls pass: `{result['controls']['canaries_pass'] and result['controls']['permuted_null_pass']}`",
        f"- Representation signals: `{', '.join(result['representation_signals_requiring_replication']) or 'none'}`",
        "",
        "## Method coverage",
        "",
        "| family | feature modes | completed runs | failed runs |",
        "|---|---|---:|---:|",
    ]
    for family, item in sorted(result["method_coverage"].items()):
        lines.append(
            f"| {family} | {', '.join(item['feature_modes'])} | "
            f"{item['completed']} | {item['failed']} |"
        )
    lines.extend(
        [
            "",
            "## Adaptive selection",
            "",
            "| task | round | selected recipes for next round |",
            "|---|---|---|",
        ]
    )
    for round_item in result["rounds"]:
        for task, selected in round_item["selected"].items():
            lines.append(
                f"| {task} | {round_item['name']} | "
                f"{', '.join(selected) if selected else 'none'} |"
            )
    lines.extend(
        [
            "",
            "## Final untouched-test evaluation",
            "",
            "| task | selected model | validation info gain | test info gain | "
            "test accuracy lift | test z | threshold |",
            "|---|---|---:|---:|---:|---:|---|",
        ]
    )
    for task, item in result["finalists"].items():
        validation = item["validation"]
        test = item["test"]
        lines.append(
            f"| {task} | {item['recipe_id']} | "
            f"{validation['information_gain_bits_per_record']:.6g} | "
            f"{test['information_gain_bits_per_record']:.6g} | "
            f"{test['accuracy_lift']:.6g} | {test['accuracy_z']:.4f} | "
            f"{'crossed' if item['threshold_crossed_both_splits'] else 'not crossed'} |"
        )
    lines.extend(
        [
            "",
            "## Controls",
            "",
            "| task | validation info gain | test info gain | test accuracy lift | test z |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for task, item in result["controls"]["tasks"].items():
        lines.append(
            f"| {task} | "
            f"{item['validation']['information_gain_bits_per_record']:.6g} | "
            f"{item['test']['information_gain_bits_per_record']:.6g} | "
            f"{item['test']['accuracy_lift']:.6g} | "
            f"{item['test']['accuracy_z']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            result["interpretation"],
            "",
            "Validation was used for adaptive model and hyperparameter selection. "
            "Exactly one selected recipe per scientific task was then evaluated on "
            "the test split. The JSONL ledger contains every completed and failed "
            "attempt, its budget, parameters, warnings, metrics, and timing.",
            "",
            "A threshold crossing would still require fresh seeds, fresh curves and "
            "generators, mechanism extraction, cost accounting, and the repository's "
            "normal candidate gates. A null result is bounded to the tested "
            "representations, models, budgets, and tasks.",
            "",
        ]
    )
    return "\n".join(lines)


def run_automl(
    config_path: Path,
    manifest_path: Path,
    output_dir: Path,
    overwrite: bool = False,
) -> dict[str, Any]:
    config = load_config(config_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    dataset_root = manifest_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = output_dir / "run_ledger.jsonl"
    if ledger_path.exists() and not overwrite:
        raise FileExistsError(f"ledger already exists: {ledger_path}")
    ledger_path.write_text("", encoding="utf-8")

    recipes = {item["id"]: item for item in config["recipes"]}
    active = {
        task: [
            recipe_id
            for recipe_id, recipe in recipes.items()
            if task in recipe.get("tasks", config["scientific_tasks"])
        ]
        for task in config["scientific_tasks"]
    }
    if any(not recipe_ids for recipe_ids in active.values()):
        missing = sorted(task for task, recipe_ids in active.items() if not recipe_ids)
        raise ValueError(f"no eligible recipes for tasks: {missing}")
    all_entries: list[dict[str, Any]] = []
    round_summaries: list[dict[str, Any]] = []
    finalist_models: dict[str, Any] = {}
    finalist_entries: dict[str, dict[str, Any]] = {}

    for round_index, round_config in enumerate(config["rounds"]):
        train_records = load_split(
            manifest,
            dataset_root,
            "train",
            int(round_config["train_records"]),
        )
        validation_records = load_split(
            manifest,
            dataset_root,
            "validation",
            int(round_config["validation_records"]),
        )
        modes = {
            recipes[recipe_id]["feature_mode"]
            for recipe_ids in active.values()
            for recipe_id in recipe_ids
        }
        feature_cache: dict[tuple[str, str], np.ndarray] = {}
        for mode in sorted(modes):
            feature_cache[("train", mode)] = transform_features(mode, train_records)
            feature_cache[("validation", mode)] = transform_features(
                mode, validation_records
            )
        selected_for_round: dict[str, list[str]] = {}
        final_round = round_index == len(config["rounds"]) - 1

        for task in config["scientific_tasks"]:
            task_entries: list[dict[str, Any]] = []
            task_models: dict[str, Any] = {}
            for recipe_id in active[task]:
                recipe = recipes[recipe_id]
                entry: dict[str, Any] = {
                    "run_id": f"{round_config['name']}/{task}/{recipe_id}",
                    "stage": "automl",
                    "round": round_config["name"],
                    "task": task,
                    "recipe_id": recipe_id,
                    "family": recipe["family"],
                    "feature_mode": recipe["feature_mode"],
                    "parameters": recipe.get("params", {}),
                    "configured_train_records": int(round_config["train_records"]),
                    "configured_validation_records": int(
                        round_config["validation_records"]
                    ),
                    "max_train_records": recipe.get("max_train_records"),
                }
                try:
                    model, measurements = fit_and_evaluate(
                        recipe,
                        task,
                        train_records,
                        validation_records,
                        feature_cache,
                        int(config["random_state"]) + round_index,
                        int(config.get("jobs", 1)),
                        int(config["prediction_batch_records"]),
                    )
                    entry.update({"status": "completed", **measurements})
                    task_models[recipe_id] = model
                except Exception as exc:
                    entry.update(
                        {
                            "status": "failed",
                            "error_type": type(exc).__name__,
                            "error": str(exc)[:500],
                        }
                    )
                append_ledger(ledger_path, entry)
                task_entries.append(entry)
                all_entries.append(entry)

            selected = select_survivors(
                task_entries,
                int(round_config["survivors_per_task"]),
                bool(round_config.get("preserve_family_diversity", False)),
            )
            selected_ids = [item["recipe_id"] for item in selected]
            selected_for_round[task] = selected_ids
            active[task] = selected_ids
            if not selected_ids:
                raise RuntimeError(
                    f"every recipe failed for task {task} in {round_config['name']}"
                )
            if final_round:
                winner = selected[0]
                finalist_entries[task] = winner
                finalist_models[task] = task_models[winner["recipe_id"]]

        round_summaries.append(
            {
                "name": round_config["name"],
                "train_records": len(train_records),
                "validation_records": len(validation_records),
                "attempts": sum(
                    1 for item in all_entries if item.get("round") == round_config["name"]
                ),
                "selected": selected_for_round,
            }
        )

    test_records = load_split(
        manifest,
        dataset_root,
        "test",
        int(config["final_test_records"]),
    )
    test_feature_cache = {
        mode: transform_features(mode, test_records)
        for mode in {
            recipes[item["recipe_id"]]["feature_mode"]
            for item in finalist_entries.values()
        }
    }
    finalists: dict[str, Any] = {}
    for task in config["scientific_tasks"]:
        entry = finalist_entries[task]
        recipe = recipes[entry["recipe_id"]]
        train_counts = np.asarray(entry["train_class_counts"], dtype=np.int64)
        test_labels = labels_for_task(task, test_records)
        test_metrics = evaluate_model(
            finalist_models[task],
            test_feature_cache[recipe["feature_mode"]],
            test_labels,
            train_counts,
            classes_for_task(task),
            int(config["prediction_batch_records"]),
        )
        final_entry = {
            "run_id": f"final_test/{task}/{entry['recipe_id']}",
            "stage": "final_test",
            "task": task,
            "recipe_id": entry["recipe_id"],
            "family": entry["family"],
            "feature_mode": entry["feature_mode"],
            "parameters": entry["parameters"],
            "train_records": entry["train_records"],
            "validation": entry["validation"],
            "test": test_metrics,
            "threshold_crossed_both_splits": crossed_threshold(
                entry["validation"], config["thresholds"]
            )
            and crossed_threshold(test_metrics, config["thresholds"]),
            "status": "completed",
        }
        append_ledger(ledger_path, final_entry)
        finalists[task] = final_entry

    controls = run_controls(config, manifest, dataset_root, ledger_path)
    completed = sum(item["status"] == "completed" for item in all_entries)
    failed = len(all_entries) - completed
    coverage: dict[str, dict[str, Any]] = {}
    family_entries: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in all_entries:
        family_entries[item["family"]].append(item)
    for family, entries in family_entries.items():
        coverage[family] = {
            "feature_modes": sorted({item["feature_mode"] for item in entries}),
            "completed": sum(item["status"] == "completed" for item in entries),
            "failed": sum(item["status"] == "failed" for item in entries),
        }
    signals = [
        task
        for task, item in finalists.items()
        if item["threshold_crossed_both_splits"]
    ]
    controls_pass = controls["canaries_pass"] and controls["permuted_null_pass"]
    pipeline_status = "pass" if controls_pass and completed else "fail"
    interpretation = (
        "One or more preregistered representation thresholds crossed on both "
        "validation and the one-shot test. Retain these only as untrusted signals "
        "requiring independent replication and explicit mechanism extraction."
        if signals
        else "No selected model crossed the preregistered representation threshold "
        "on both validation and the one-shot test. This is a bounded null for the "
        "tested model, feature, task, and compute budgets."
    )
    result = {
        "schema_version": 1,
        "experiment_id": config["experiment_id"],
        "result_role": "budgeted_automl_representation_assay",
        "scientific_evidence": False,
        "route_promotion_authorized": False,
        "pipeline_status": pipeline_status,
        "dataset": {
            "experiment_id": manifest["experiment_id"],
            "total_records": int(manifest["total_records"]),
            "manifest_sha256": sha256_file(manifest_path),
            "dataset_root_sha256": manifest["dataset_root_sha256"],
        },
        "automl_config_sha256": sha256_file(config_path),
        "source_hashes": {
            "experiments/ml_structure_probe/automl.py": sha256_file(HERE / "automl.py"),
            config_path.relative_to(ROOT).as_posix(): sha256_file(config_path),
        },
        "source_state": git_state(),
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scikit_learn": sklearn.__version__,
            "platform": platform.platform(),
            "jobs": int(config.get("jobs", 1)),
        },
        "selection_protocol": {
            "selection_split": "validation",
            "final_split": "test",
            "test_models_per_scientific_task": 1,
            "selection_metric": "information_gain_bits_per_record",
            "strategy": "successive_halving_with_optional_family_diversity",
            "thresholds": config["thresholds"],
        },
        "rounds": round_summaries,
        "run_summary": {
            "attempted": len(all_entries),
            "completed": completed,
            "failed": failed,
            "warning_counts": dict(
                Counter(
                    warning.split(":", 1)[0]
                    for item in all_entries
                    for warning in item.get("warnings", [])
                )
            ),
        },
        "method_coverage": coverage,
        "finalists": finalists,
        "controls": controls,
        "representation_signals_requiring_replication": signals,
        "interpretation": interpretation,
        "scope": [
            "Synthetic secp256k1 pairs only; no wallet or target key data.",
            "No claim about models, representations, or tasks outside the ledger.",
            "No asymptotic inference and no comparison claiming better-than-generic work.",
            "No hypothesis registration, route promotion, or target recovery attempt.",
        ],
        "runs": all_entries,
    }
    result_path = output_dir / "automl_result.json"
    report_path = output_dir / "automl_report.md"
    result_path.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    report_path.write_text(markdown_report(result), encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    result = run_automl(
        args.config.resolve(),
        args.manifest.resolve(),
        args.output_dir.resolve(),
        args.overwrite,
    )
    print(
        json.dumps(
            {
                "pipeline_status": result["pipeline_status"],
                "attempted": result["run_summary"]["attempted"],
                "completed": result["run_summary"]["completed"],
                "failed": result["run_summary"]["failed"],
                "signals": result[
                    "representation_signals_requiring_replication"
                ],
                "output_dir": str(args.output_dir.resolve()),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if result["pipeline_status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
