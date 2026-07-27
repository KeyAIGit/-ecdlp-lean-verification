#!/usr/bin/env python3
"""Successive-halving AutoML assay for all 256 secp256k1 scalar bits.

The two existing million-record corpora are a development pool.  This script
searches on their train/validation partitions, treats the old test partitions
as development validation data, and exports one frozen five-seed recipe.  A
different script must evaluate that recipe once on a newly generated blind
million.  Nothing in this program reads a blind dataset.
"""
from __future__ import annotations

import argparse
import json
import platform
import time
import traceback
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import sklearn

import automl
from full_key_common import (
    FeatureStore,
    ProbabilityEnsemble,
    evaluate_model,
    fit_and_evaluate,
    scalar_bits,
    sha256_file,
    signal_threshold_crossed,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCHEMA_VERSION = 1


def canonical_json(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def load_config(path: Path) -> dict[str, Any]:
    config = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "schema_version",
        "experiment_id",
        "search_seed",
        "jobs",
        "feature_workers",
        "prediction_batch_records",
        "development_datasets",
        "stages",
        "architecture_space",
        "controls",
        "thresholds",
    }
    missing = sorted(required - set(config))
    if missing:
        raise ValueError(f"full-key config missing fields: {missing}")
    if config["schema_version"] != SCHEMA_VERSION:
        raise ValueError("unsupported full-key search schema_version")
    if len(config["development_datasets"]) != 2:
        raise ValueError("exactly two development datasets are required")
    stages = config["stages"]
    expected_attempts = (
        int(stages["screen"]["architecture_count"])
        * len(stages["screen"]["seeds"])
        + int(stages["screen"]["survivors"])
        * len(stages["confirm"]["seeds"])
        + int(stages["confirm"]["survivors"])
        * 2
        + len(stages["final_ensemble"]["seeds"])
        + len(config["controls"]["random_label_seeds"])
        + len(config["controls"]["permuted_label_seeds"])
        + len(config["controls"]["leak_widths"])
        * len(config["controls"]["leak_seeds"])
    )
    if expected_attempts < 100:
        raise ValueError("full-key search must retain a genuine hundreds-run budget")
    return config


def resolve_path(raw: str, config_path: Path) -> Path:
    candidate = Path(raw)
    if candidate.is_absolute():
        return candidate
    relative_to_here = HERE / candidate
    if relative_to_here.exists():
        return relative_to_here
    return config_path.parent / candidate


def interleave(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    """Interleave two equal-width record matrices without dataset-order bias."""
    if left.shape[1:] != right.shape[1:]:
        raise ValueError("cannot interleave differently shaped record arrays")
    count = min(len(left), len(right))
    output = np.empty((count * 2, *left.shape[1:]), dtype=left.dtype)
    output[0::2] = left[:count]
    output[1::2] = right[:count]
    if len(left) == len(right):
        return output
    tail = left[count:] if len(left) > count else right[count:]
    return np.concatenate((output, tail), axis=0)


def _sample_unique(
    generator: np.random.Generator,
    count: int,
    factory: Any,
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    seen: set[str] = set()
    while len(selected) < count:
        architecture = factory(generator)
        signature = canonical_json(
            {
                "family": architecture["family"],
                "feature_mode": architecture["feature_mode"],
                "epoch_fraction": architecture.get("epoch_fraction"),
                "params": architecture["params"],
                "max_train_records": architecture.get("max_train_records"),
            }
        )
        if signature not in seen:
            seen.add(signature)
            selected.append(architecture)
    return selected


def generate_architectures(config: dict[str, Any]) -> list[dict[str, Any]]:
    """Generate a deterministic, committed 80-recipe heterogeneous space."""
    space = config["architecture_space"]
    generator = np.random.default_rng(int(config["search_seed"]))
    modes = list(space["feature_modes"])

    hidden_options: list[list[int]] = [
        [],
        [32],
        [64],
        [128],
        [256],
        [64, 64],
        [128, 64],
        [128, 128],
        [256, 128],
        [64, 64, 64],
        [128, 128, 128],
        [256, 128, 64],
    ]

    def mlp_factory(rng: np.random.Generator) -> dict[str, Any]:
        return {
            "family": "mlp",
            "feature_mode": str(rng.choice(modes)),
            "epoch_fraction": float(rng.choice([0.5, 1.0])),
            "params": {
                "hidden_layers": hidden_options[int(rng.integers(len(hidden_options)))],
                "activation": str(rng.choice(["relu", "tanh"])),
                "alpha": float(rng.choice([0.0, 1e-6, 1e-5, 1e-4, 1e-3])),
                "batch_size": int(rng.choice([512, 2048, 8192])),
                "learning_rate_init": float(
                    rng.choice([1e-4, 3e-4, 1e-3, 3e-3])
                ),
            },
        }

    def ridge_factory(rng: np.random.Generator) -> dict[str, Any]:
        return {
            "family": "ridge",
            "feature_mode": str(rng.choice(modes)),
            "params": {
                "alpha": float(rng.choice([0.1, 1.0, 10.0, 100.0, 1000.0])),
                "max_iter": int(rng.choice([50, 100, 200])),
                "tol": float(rng.choice([1e-3, 3e-4])),
            },
        }

    def trees_factory(rng: np.random.Generator) -> dict[str, Any]:
        return {
            "family": "extra_trees",
            "feature_mode": str(rng.choice(modes)),
            "max_train_records": 100_000,
            "params": {
                "n_estimators": int(rng.choice([8, 12, 16])),
                "max_depth": int(rng.choice([6, 8, 10])),
                "min_samples_leaf": int(rng.choice([16, 64, 256])),
                "max_features": str(rng.choice(["sqrt", "log2"])),
            },
        }

    rbf_modes = [
        "compressed_bits_257",
        "compressed_bytes",
        "x_limbs16",
        "byte_popcounts",
        "affine_bytes",
        "affine_limbs16",
    ]

    def rbf_factory(rng: np.random.Generator) -> dict[str, Any]:
        return {
            "family": "rbf_logistic",
            "feature_mode": str(rng.choice(rbf_modes)),
            "max_train_records": 300_000,
            "epoch_fraction": float(rng.choice([0.5, 1.0])),
            "params": {
                "gamma": float(rng.choice([0.001, 0.003, 0.01, 0.03, 0.1])),
                "n_components": int(rng.choice([64, 128, 256])),
                "alpha": float(rng.choice([1e-6, 1e-5, 1e-4, 1e-3])),
                "batch_size": int(rng.choice([512, 2048, 8192])),
                "learning_rate_init": float(
                    rng.choice([1e-4, 3e-4, 1e-3, 3e-3])
                ),
            },
        }

    architectures: list[dict[str, Any]] = []
    architectures.extend(
        _sample_unique(generator, int(space["mlp_count"]), mlp_factory)
    )
    architectures.extend(
        _sample_unique(generator, int(space["ridge_count"]), ridge_factory)
    )
    architectures.extend(
        _sample_unique(generator, int(space["extra_trees_count"]), trees_factory)
    )
    architectures.extend(
        _sample_unique(generator, int(space["rbf_logistic_count"]), rbf_factory)
    )
    generator.shuffle(architectures)
    for index, architecture in enumerate(architectures):
        architecture["id"] = f"arch-{index:03d}"
    expected = int(config["stages"]["screen"]["architecture_count"])
    if len(architectures) != expected:
        raise ValueError(
            f"architecture space generated {len(architectures)}, expected {expected}"
        )
    return architectures


def materialize_architecture(
    architecture: dict[str, Any],
    max_epochs: int,
) -> dict[str, Any]:
    rendered = deepcopy(architecture)
    if rendered["family"] in ("mlp", "rbf_logistic"):
        fraction = float(rendered.get("epoch_fraction", 1.0))
        rendered["params"]["epochs"] = max(1, int(round(max_epochs * fraction)))
    return rendered


def _load_dataset(
    item: dict[str, Any],
    config_path: Path,
) -> dict[str, Any]:
    manifest_path = resolve_path(item["manifest"], config_path)
    dataset_root = resolve_path(item["dataset_root"], config_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for required_split, expected in (
        ("train", 600_000),
        ("validation", 200_000),
        ("test", 200_000),
    ):
        if int(manifest["splits"].get(required_split, 0)) < expected:
            raise ValueError(
                f"{item['id']} lacks {expected} records in {required_split}"
            )
    train = automl.load_split(manifest, dataset_root, "train", 600_000)
    validation = automl.load_split(
        manifest, dataset_root, "validation", 200_000
    )
    development = automl.load_split(manifest, dataset_root, "test", 200_000)
    return {
        "id": item["id"],
        "manifest_path": manifest_path,
        "dataset_root": dataset_root,
        "manifest": manifest,
        "train_pool": np.concatenate((train, validation), axis=0),
        "development": development,
    }


class Ledger:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.handle = path.open("w", encoding="utf-8")
        self.attempt = 0
        self.succeeded = 0
        self.failed = 0

    def append(self, record: dict[str, Any]) -> dict[str, Any]:
        self.attempt += 1
        record = {
            "attempt": self.attempt,
            "timestamp_unix": time.time(),
            **record,
        }
        self.handle.write(json.dumps(record, sort_keys=True) + "\n")
        self.handle.flush()
        if record["status"] == "success":
            self.succeeded += 1
        else:
            self.failed += 1
        return record

    def close(self) -> None:
        self.handle.close()


def _run_fit(
    ledger: Ledger,
    stage: str,
    architecture: dict[str, Any],
    seed: int,
    train_features: np.ndarray,
    train_labels: np.ndarray,
    validation_features: np.ndarray,
    validation_labels: np.ndarray,
    config: dict[str, Any],
    direction: str = "mixed",
    detailed: bool = False,
) -> tuple[Any | None, dict[str, Any]]:
    common = {
        "stage": stage,
        "direction": direction,
        "architecture_id": architecture["id"],
        "family": architecture["family"],
        "feature_mode": architecture["feature_mode"],
        "architecture": architecture,
        "seed": seed,
    }
    try:
        model, outcome = fit_and_evaluate(
            architecture,
            seed,
            train_features,
            train_labels,
            validation_features,
            validation_labels,
            int(config["jobs"]),
            int(config["prediction_batch_records"]),
            detailed=detailed,
            exploratory_metrics=detailed,
        )
        record = ledger.append({"status": "success", **common, **outcome})
        return model, record
    except Exception as error:  # Keep the predeclared budget auditable.
        record = ledger.append(
            {
                "status": "failed",
                **common,
                "error_type": type(error).__name__,
                "error": str(error),
                "traceback": traceback.format_exc(limit=8),
            }
        )
        return None, record


def architecture_summaries(
    records: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        if record["status"] == "success":
            grouped[record["architecture_id"]].append(record)
    summaries: list[dict[str, Any]] = []
    for architecture_id, items in grouped.items():
        information = np.asarray(
            [
                item["validation"]["information_gain_bits_per_key"]
                for item in items
            ],
            dtype=np.float64,
        )
        lift = np.asarray(
            [item["validation"]["bit_accuracy_lift"] for item in items],
            dtype=np.float64,
        )
        paired_z = np.asarray(
            [item["validation"]["paired_accuracy_z"] for item in items],
            dtype=np.float64,
        )
        conservative = float(np.median(information) - 0.25 * np.std(information))
        summaries.append(
            {
                "architecture_id": architecture_id,
                "architecture": items[0]["architecture"],
                "successful_seeds": len(items),
                "median_information_bits_per_key": float(np.median(information)),
                "information_std": float(np.std(information)),
                "median_bit_accuracy_lift": float(np.median(lift)),
                "median_paired_z": float(np.median(paired_z)),
                "worst_information_bits_per_key": float(np.min(information)),
                "conservative_score": conservative,
            }
        )
    return sorted(
        summaries,
        key=lambda item: (
            item["conservative_score"],
            item["median_bit_accuracy_lift"],
        ),
        reverse=True,
    )


def select_with_family_diversity(
    summaries: list[dict[str, Any]],
    count: int,
    required_successful_seeds: int,
) -> list[dict[str, Any]]:
    """Keep the ranking while reserving one slot per successful family."""
    summaries = [
        item
        for item in summaries
        if item["successful_seeds"] == required_successful_seeds
    ]
    selected: list[dict[str, Any]] = []
    selected_ids: set[str] = set()
    families = sorted(
        {item["architecture"]["family"] for item in summaries}
    )
    for family in families:
        candidate = next(
            (
                item
                for item in summaries
                if item["architecture"]["family"] == family
            ),
            None,
        )
        if candidate is not None:
            selected.append(candidate)
            selected_ids.add(candidate["architecture_id"])
    for item in summaries:
        if len(selected) >= count:
            break
        if item["architecture_id"] not in selected_ids:
            selected.append(item)
            selected_ids.add(item["architecture_id"])
    return sorted(
        selected[:count],
        key=lambda item: item["conservative_score"],
        reverse=True,
    )


def _records_for_stage(
    datasets: list[dict[str, Any]],
    train_per_dataset: int,
    validation_per_dataset: int,
) -> tuple[np.ndarray, np.ndarray]:
    train = interleave(
        datasets[0]["train_pool"][:train_per_dataset],
        datasets[1]["train_pool"][:train_per_dataset],
    )
    validation = interleave(
        datasets[0]["development"][:validation_per_dataset],
        datasets[1]["development"][:validation_per_dataset],
    )
    return train, validation


def _run_architecture_stage(
    stage: str,
    architecture_items: list[dict[str, Any]],
    seeds: list[int],
    max_epochs: int,
    train_records: np.ndarray,
    validation_records: np.ndarray,
    config: dict[str, Any],
    ledger: Ledger,
) -> list[dict[str, Any]]:
    labels_train = scalar_bits(train_records)
    labels_validation = scalar_bits(validation_records)
    records: list[dict[str, Any]] = []
    by_mode: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in architecture_items:
        architecture = item.get("architecture", item)
        by_mode[architecture["feature_mode"]].append(architecture)
    total = sum(len(items) * len(seeds) for items in by_mode.values())
    completed = 0
    for mode, mode_architectures in by_mode.items():
        train_store = FeatureStore(train_records, int(config["feature_workers"]))
        validation_store = FeatureStore(
            validation_records, int(config["feature_workers"])
        )
        train_features = train_store.get(mode)
        validation_features = validation_store.get(mode)
        for raw_architecture in mode_architectures:
            architecture = materialize_architecture(raw_architecture, max_epochs)
            for seed in seeds:
                _, record = _run_fit(
                    ledger,
                    stage,
                    architecture,
                    seed,
                    train_features,
                    labels_train,
                    validation_features,
                    labels_validation,
                    config,
                )
                records.append(record)
                completed += 1
                if completed % 10 == 0 or completed == total:
                    metric = (
                        record.get("validation", {})
                        .get("information_gain_bits_per_key")
                    )
                    print(
                        f"[{stage}] {completed}/{total} attempts; "
                        f"last info bits/key={metric}",
                        flush=True,
                    )
        del train_store, validation_store, train_features, validation_features
    return records


def _run_controls(
    config: dict[str, Any],
    ledger: Ledger,
    train_records: np.ndarray,
    validation_records: np.ndarray,
) -> list[dict[str, Any]]:
    controls = config["controls"]
    base_mode = "compressed_bits_257"
    train_features = FeatureStore(
        train_records, int(config["feature_workers"])
    ).get(base_mode)
    validation_features = FeatureStore(
        validation_records, int(config["feature_workers"])
    ).get(base_mode)
    true_train = scalar_bits(train_records)
    true_validation = scalar_bits(validation_records)
    architecture = {
        "id": "control-linear-head",
        "family": "mlp",
        "feature_mode": base_mode,
        "params": {
            "hidden_layers": [],
            "activation": "relu",
            "alpha": 1e-5,
            "batch_size": 2048,
            "learning_rate_init": 0.003,
            "epochs": 4,
        },
    }
    records: list[dict[str, Any]] = []

    for seed in controls["random_label_seeds"]:
        train_random = np.random.default_rng(seed).integers(
            0, 2, size=true_train.shape, dtype=np.uint8
        )
        validation_random = np.random.default_rng(seed + 1_000_003).integers(
            0, 2, size=true_validation.shape, dtype=np.uint8
        )
        _, record = _run_fit(
            ledger,
            "control_random_labels",
            architecture,
            int(seed),
            train_features,
            train_random,
            validation_features,
            validation_random,
            config,
        )
        records.append(record)

    for seed in controls["permuted_label_seeds"]:
        train_permutation = np.random.default_rng(seed).permutation(len(true_train))
        validation_permutation = np.random.default_rng(seed + 1_000_003).permutation(
            len(true_validation)
        )
        _, record = _run_fit(
            ledger,
            "control_permuted_keys",
            architecture,
            int(seed),
            train_features,
            true_train[train_permutation],
            validation_features,
            true_validation[validation_permutation],
            config,
        )
        records.append(record)

    for width in controls["leak_widths"]:
        for seed in controls["leak_seeds"]:
            leaked_architecture = deepcopy(architecture)
            leaked_architecture["id"] = f"control-leak-{width}"
            leaked_architecture["feature_mode"] = f"{base_mode}+label_leak_{width}"
            leaked_train = np.concatenate(
                (
                    train_features,
                    true_train[:, : int(width)].astype(np.float32) * 2.0 - 1.0,
                ),
                axis=1,
            )
            leaked_validation = np.concatenate(
                (
                    validation_features,
                    true_validation[:, : int(width)].astype(np.float32) * 2.0 - 1.0,
                ),
                axis=1,
            )
            _, record = _run_fit(
                ledger,
                f"control_label_leak_{width}",
                leaked_architecture,
                int(seed),
                leaked_train,
                true_train,
                leaked_validation,
                true_validation,
                config,
            )
            records.append(record)
    return records


def _cross_dataset(
    candidates: list[dict[str, Any]],
    config: dict[str, Any],
    ledger: Ledger,
    datasets: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    stage = config["stages"]["cross_dataset"]
    output: list[dict[str, Any]] = []
    directions = [
        (datasets[0], datasets[1], int(stage["seeds"][0])),
        (datasets[1], datasets[0], int(stage["seeds"][1])),
    ]
    total = len(candidates) * len(directions)
    completed = 0
    for candidate in candidates:
        raw_architecture = candidate["architecture"]
        architecture = materialize_architecture(
            raw_architecture, int(stage["max_epochs"])
        )
        mode = architecture["feature_mode"]
        for train_dataset, validation_dataset, seed in directions:
            train_records = train_dataset["train_pool"][: int(stage["train_records"])]
            validation_records = validation_dataset["development"][
                : int(stage["validation_records"])
            ]
            train_features = FeatureStore(
                train_records, int(config["feature_workers"])
            ).get(mode)
            validation_features = FeatureStore(
                validation_records, int(config["feature_workers"])
            ).get(mode)
            _, record = _run_fit(
                ledger,
                "cross_dataset",
                architecture,
                seed,
                train_features,
                scalar_bits(train_records),
                validation_features,
                scalar_bits(validation_records),
                config,
                direction=(
                    f"{train_dataset['id']}_to_{validation_dataset['id']}"
                ),
            )
            output.append(record)
            completed += 1
            print(f"[cross_dataset] {completed}/{total} attempts", flush=True)
            del train_features, validation_features
    return output


def _winner_from_cross(
    cross_records: list[dict[str, Any]],
) -> dict[str, Any]:
    summaries = [
        item
        for item in architecture_summaries(cross_records)
        if item["successful_seeds"] == 2
    ]
    if not summaries:
        raise RuntimeError("all cross-dataset candidates failed")
    return max(
        summaries,
        key=lambda item: (
            item["worst_information_bits_per_key"],
            item["conservative_score"],
        ),
    )


def _final_ensemble(
    winner: dict[str, Any],
    config: dict[str, Any],
    ledger: Ledger,
    datasets: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    stage = config["stages"]["final_ensemble"]
    train_records, validation_records = _records_for_stage(
        datasets,
        int(stage["train_records_per_dataset"]),
        int(stage["validation_records_per_dataset"]),
    )
    architecture = materialize_architecture(
        winner["architecture"], int(stage["max_epochs"])
    )
    architecture.setdefault("max_train_records", 2_000_000)
    mode = architecture["feature_mode"]
    train_features = FeatureStore(
        train_records, int(config["feature_workers"])
    ).get(mode)
    validation_features = FeatureStore(
        validation_records, int(config["feature_workers"])
    ).get(mode)
    train_labels = scalar_bits(train_records)
    validation_labels = scalar_bits(validation_records)
    models: list[Any] = []
    records: list[dict[str, Any]] = []
    for index, seed in enumerate(stage["seeds"], start=1):
        model, record = _run_fit(
            ledger,
            "final_ensemble_member",
            architecture,
            int(seed),
            train_features,
            train_labels,
            validation_features,
            validation_labels,
            config,
            detailed=True,
        )
        records.append(record)
        if model is not None:
            models.append(model)
        print(
            f"[final_ensemble] member {index}/{len(stage['seeds'])}",
            flush=True,
        )
    if len(models) != len(stage["seeds"]):
        raise RuntimeError("a frozen ensemble member failed to train")
    priors = (train_labels.sum(axis=0, dtype=np.float64) + 1.0) / (
        len(train_labels) + 2.0
    )
    ensemble_metrics = evaluate_model(
        ProbabilityEnsemble(models),
        validation_features,
        validation_labels,
        priors,
        int(config["prediction_batch_records"]),
        detailed=True,
    )
    return records, ensemble_metrics, architecture


def _expected_attempts(config: dict[str, Any]) -> int:
    stages = config["stages"]
    controls = config["controls"]
    return (
        int(stages["screen"]["architecture_count"])
        * len(stages["screen"]["seeds"])
        + int(stages["screen"]["survivors"])
        * len(stages["confirm"]["seeds"])
        + int(stages["confirm"]["survivors"]) * 2
        + len(stages["final_ensemble"]["seeds"])
        + len(controls["random_label_seeds"])
        + len(controls["permuted_label_seeds"])
        + len(controls["leak_widths"]) * len(controls["leak_seeds"])
    )


def _report_markdown(result: dict[str, Any]) -> str:
    ensemble = result["development_ensemble_metrics"]
    winner = result["winner"]
    controls = result["controls_summary"]
    lines = [
        "# Full-key secp256k1 AutoML development report",
        "",
        "## Verdict",
        "",
        (
            "This is a synthetic engineering representation assay. It is not a "
            "key-recovery result and it is not scientific evidence."
        ),
        "",
        (
            f"The search completed **{result['run_summary']['attempted']}** "
            f"predeclared training attempts. The frozen development ensemble "
            f"reached **{ensemble['information_gain_bits_per_key']:.6g} "
            "bits/key** information gain, "
            f"**{ensemble['bit_accuracy_lift']:.6g}** bit-accuracy lift, "
            f"and **{ensemble['exact_key_matches']}** exact 256-bit keys."
        ),
        "",
        (
            "A compressed secp256k1 key occupies 33 bytes (264 physical bits), "
            "but its independent public representation is 256 x-coordinate "
            "bits plus one y-parity bit (257 informative bits). The 512-bit "
            "x||y affine representation was also searched; y is deterministically "
            "recoverable from x and parity, so it adds no independent information."
        ),
        "",
        "## Frozen recipe",
        "",
        f"- Architecture: `{winner['architecture_id']}`",
        f"- Family: `{winner['architecture']['family']}`",
        f"- Input: `{winner['architecture']['feature_mode']}`",
        f"- Hidden/configuration: `{json.dumps(winner['architecture']['params'], sort_keys=True)}`",
        "- Output: 256 simultaneous Bernoulli probabilities, one per private-scalar bit",
        "- Selection: development data only; a new independent million remains blind",
        "",
        "## Development metrics",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Information gain, bits/key | {ensemble['information_gain_bits_per_key']:.9g} |",
        f"| Bit accuracy | {ensemble['bit_accuracy']:.9g} |",
        f"| Prior-null bit accuracy | {ensemble['null_bit_accuracy']:.9g} |",
        f"| Bit accuracy lift | {ensemble['bit_accuracy_lift']:.9g} |",
        f"| Paired accuracy z | {ensemble['paired_accuracy_z']:.6g} |",
        f"| Mean Hamming distance | {ensemble['mean_hamming_distance']:.6g} |",
        f"| Exact 256-bit matches | {ensemble['exact_key_matches']} |",
        "",
        "## Search stages",
        "",
        "| Stage | Attempts | Successful |",
        "|---|---:|---:|",
    ]
    for stage, item in result["stage_summary"].items():
        lines.append(
            f"| {stage} | {item['attempted']} | {item['successful']} |"
        )
    lines.extend(
        [
            "",
            "## Controls",
            "",
            f"- Random-label attempts: {controls['random_label_attempts']}",
            f"- Whole-key permutation attempts: {controls['permuted_key_attempts']}",
            f"- Deliberate label-leak attempts: {controls['label_leak_attempts']}",
            (
                f"- Maximum null information gain: "
                f"{controls['max_null_information_bits_per_key']:.6g} bits/key"
            ),
            (
                f"- One-bit target-head information gain: "
                f"{controls['minimum_leak_1_target_bit_information']:.6g} bits"
            ),
            (
                f"- Minimum 8-bit leak whole-key gain: "
                f"{controls['minimum_leak_8_information_bits_per_key']:.6g} bits/key"
            ),
            (
                f"- Minimum 32-bit leak whole-key gain: "
                f"{controls['minimum_leak_32_information_bits_per_key']:.6g} bits/key"
            ),
            f"- Control qualification passed: {controls['controls_pass']}",
            "",
            "## Interpretation boundary",
            "",
            (
                "Two million development pairs occupy a negligible fraction of "
                "the secp256k1 scalar space. A null result rejects only the tested "
                "model, representation and compute budgets. A positive development "
                "metric is only a candidate until the single frozen ensemble "
                "repeats it independently on both halves of the new blind million."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def run_search(
    config_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    config = load_config(config_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = output_dir / "full_key_run_ledger.jsonl"
    ledger = Ledger(ledger_path)
    started = time.perf_counter()
    try:
        print("[load] reading two million development records", flush=True)
        datasets = [
            _load_dataset(item, config_path)
            for item in config["development_datasets"]
        ]
        architectures = generate_architectures(config)
        screen_stage = config["stages"]["screen"]
        screen_train, screen_validation = _records_for_stage(
            datasets,
            int(screen_stage["train_records_per_dataset"]),
            int(screen_stage["validation_records_per_dataset"]),
        )
        print("[screen] starting 240 fits", flush=True)
        screen_records = _run_architecture_stage(
            "screen",
            architectures,
            [int(value) for value in screen_stage["seeds"]],
            int(screen_stage["max_epochs"]),
            screen_train,
            screen_validation,
            config,
            ledger,
        )
        screen_summaries = architecture_summaries(screen_records)
        screen_survivors = select_with_family_diversity(
            screen_summaries,
            int(screen_stage["survivors"]),
            len(screen_stage["seeds"]),
        )
        if len(screen_survivors) != int(screen_stage["survivors"]):
            raise RuntimeError("too few successful screen architectures")

        confirm_stage = config["stages"]["confirm"]
        confirm_train, confirm_validation = _records_for_stage(
            datasets,
            int(confirm_stage["train_records_per_dataset"]),
            int(confirm_stage["validation_records_per_dataset"]),
        )
        print("[confirm] starting 36 fits", flush=True)
        confirm_records = _run_architecture_stage(
            "confirm",
            screen_survivors,
            [int(value) for value in confirm_stage["seeds"]],
            int(confirm_stage["max_epochs"]),
            confirm_train,
            confirm_validation,
            config,
            ledger,
        )
        confirm_summaries = architecture_summaries(confirm_records)
        cross_candidates = select_with_family_diversity(
            confirm_summaries,
            int(confirm_stage["survivors"]),
            len(confirm_stage["seeds"]),
        )
        if len(cross_candidates) != int(confirm_stage["survivors"]):
            raise RuntimeError("too few successful confirm architectures")

        print("[cross_dataset] starting 8 fits", flush=True)
        cross_records = _cross_dataset(
            cross_candidates, config, ledger, datasets
        )
        winner = _winner_from_cross(cross_records)

        print("[controls] starting 12 fits", flush=True)
        control_records = _run_controls(
            config, ledger, screen_train, screen_validation
        )

        print("[final_ensemble] starting 5 full-data fits", flush=True)
        final_records, ensemble_metrics, final_architecture = _final_ensemble(
            winner, config, ledger, datasets
        )
    finally:
        ledger.close()

    attempts = ledger.attempt
    expected_attempts = _expected_attempts(config)
    if attempts != expected_attempts:
        raise RuntimeError(
            f"incomplete ledger: expected {expected_attempts}, got {attempts}"
        )
    stage_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    all_records = (
        screen_records
        + confirm_records
        + cross_records
        + control_records
        + final_records
    )
    for record in all_records:
        stage_groups[record["stage"]].append(record)
    stage_summary = {
        stage: {
            "attempted": len(items),
            "successful": sum(item["status"] == "success" for item in items),
            "failed": sum(item["status"] != "success" for item in items),
        }
        for stage, items in sorted(stage_groups.items())
    }
    null_controls = [
        item
        for item in control_records
        if item["status"] == "success"
        and item["stage"] in ("control_random_labels", "control_permuted_keys")
    ]
    leak_controls = [
        item
        for item in control_records
        if item["status"] == "success"
        and item["stage"].startswith("control_label_leak_")
    ]
    leak_1_controls = [
        item for item in leak_controls if item["stage"] == "control_label_leak_1"
    ]
    leak_8_controls = [
        item for item in leak_controls if item["stage"] == "control_label_leak_8"
    ]
    leak_32_controls = [
        item for item in leak_controls if item["stage"] == "control_label_leak_32"
    ]
    maximum_null_information = max(
        (
            item["validation"]["information_gain_bits_per_key"]
            for item in null_controls
        ),
        default=float("nan"),
    )
    maximum_null_z = max(
        (item["validation"]["paired_accuracy_z"] for item in null_controls),
        default=float("nan"),
    )
    minimum_leak_1_target_information = min(
        (
            item["validation"]["best_information_bit"]["information_gain_bits"]
            for item in leak_1_controls
        ),
        default=float("nan"),
    )
    minimum_leak_8_information = min(
        (
            item["validation"]["information_gain_bits_per_key"]
            for item in leak_8_controls
        ),
        default=float("nan"),
    )
    minimum_leak_32_information = min(
        (
            item["validation"]["information_gain_bits_per_key"]
            for item in leak_32_controls
        ),
        default=float("nan"),
    )
    controls_pass = (
        maximum_null_information < 0.01
        and maximum_null_z < 5.0
        and minimum_leak_1_target_information > 0.25
        and all(
            item["validation"]["best_information_bit"]["bit_big_endian"] == 0
            and item["validation"]["best_information_bit"]["accuracy_lift"] > 0.45
            for item in leak_1_controls
        )
        and minimum_leak_8_information > 1.0
        and minimum_leak_32_information > 5.0
    )
    controls_summary = {
        "random_label_attempts": sum(
            item["stage"] == "control_random_labels" for item in control_records
        ),
        "permuted_key_attempts": sum(
            item["stage"] == "control_permuted_keys" for item in control_records
        ),
        "label_leak_attempts": sum(
            item["stage"].startswith("control_label_leak_")
            for item in control_records
        ),
        "max_null_information_bits_per_key": maximum_null_information,
        "max_null_accuracy_z": maximum_null_z,
        "minimum_leak_1_target_bit_information": (
            minimum_leak_1_target_information
        ),
        "minimum_leak_8_information_bits_per_key": minimum_leak_8_information,
        "minimum_leak_32_information_bits_per_key": minimum_leak_32_information,
        "controls_pass": controls_pass,
    }
    result = {
        "schema_version": SCHEMA_VERSION,
        "experiment_id": config["experiment_id"],
        "status": "completed",
        "scientific_evidence": False,
        "purpose": config.get("purpose"),
        "source_state": automl.git_state(),
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "sklearn": sklearn.__version__,
            "elapsed_seconds": time.perf_counter() - started,
            "jobs": int(config["jobs"]),
        },
        "config_path": str(config_path),
        "config_sha256": sha256_file(config_path),
        "dataset_manifests": [
            {
                "id": dataset["id"],
                "path": str(dataset["manifest_path"]),
                "sha256": sha256_file(dataset["manifest_path"]),
                "dataset_root_sha256": dataset["manifest"][
                    "dataset_root_sha256"
                ],
            }
            for dataset in datasets
        ],
        "run_summary": {
            "attempted": attempts,
            "expected": expected_attempts,
            "succeeded": ledger.succeeded,
            "failed": ledger.failed,
        },
        "stage_summary": stage_summary,
        "screen_ranking": screen_summaries,
        "screen_survivors": screen_survivors,
        "confirm_ranking": confirm_summaries,
        "cross_candidates": cross_candidates,
        "cross_ranking": architecture_summaries(cross_records),
        "winner": {
            **winner,
            "architecture": final_architecture,
        },
        "development_ensemble_metrics": ensemble_metrics,
        "development_signal_threshold_crossed": signal_threshold_crossed(
            ensemble_metrics, **{
                "minimum_information_bits_per_key": float(
                    config["thresholds"]["minimum_information_bits_per_key"]
                ),
                "minimum_bit_accuracy_lift": float(
                    config["thresholds"]["minimum_bit_accuracy_lift"]
                ),
                "minimum_paired_z": float(
                    config["thresholds"]["minimum_paired_z"]
                ),
            }
        ),
        "controls_summary": controls_summary,
        "ledger_path": str(ledger_path),
        "ledger_sha256": sha256_file(ledger_path),
        "blind_dataset_accessed": False,
        "interpretation": (
            "Development-only engineering result. One frozen recipe must be "
            "tested without adaptation on a new independent million."
        ),
    }
    result_path = output_dir / "full_key_search_result.json"
    result_path.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    frozen_recipe = {
        "schema_version": SCHEMA_VERSION,
        "experiment_id": f"{config['experiment_id']}-BLIND",
        "recipe_id": winner["architecture_id"],
        "feature_mode": final_architecture["feature_mode"],
        "architecture": final_architecture,
        "ensemble_seeds": [
            int(value)
            for value in config["stages"]["final_ensemble"]["seeds"]
        ],
        "jobs": int(config["jobs"]),
        "feature_workers": int(config["feature_workers"]),
        "prediction_batch_records": int(config["prediction_batch_records"]),
        "train_records_per_manifest": 1_000_000,
        "development_splits": ["train", "validation", "test"],
        "dev_records_per_manifest": int(
            config["stages"]["final_ensemble"][
                "validation_records_per_dataset"
            ]
        ),
        "thresholds": config["thresholds"],
        "frozen_from": {
            "search_result_sha256": sha256_file(result_path),
            "ledger_sha256": sha256_file(ledger_path),
            "search_config_sha256": sha256_file(config_path),
            "source_commit": result["source_state"]["commit"],
        },
        "blind_policy": {
            "required_splits": ["blind_a", "blind_b"],
            "fit_on_blind": False,
            "selection_on_blind": False,
            "single_ensemble_evaluation": True,
            "require_thresholds_on_both_halves": True,
        },
        "scientific_evidence": False,
    }
    frozen_path = output_dir / "frozen_full_key_recipe.json"
    frozen_path.write_text(
        json.dumps(frozen_recipe, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    report_path = output_dir / "full_key_search_report.md"
    report_path.write_text(_report_markdown(result), encoding="utf-8")
    print(
        f"[complete] {attempts} attempts; "
        f"result={result_path}; frozen={frozen_path}",
        flush=True,
    )
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_search(args.config.resolve(), args.output_dir.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
