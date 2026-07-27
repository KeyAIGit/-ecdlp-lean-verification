#!/usr/bin/env python3
"""Frozen full-key ensemble evaluation on untouched blind dataset halves.

Frozen recipe schema version 1
================================

The recipe is selected by ``full_key_search.py`` before this program is run:

.. code-block:: json

    {
      "schema_version": 1,
      "experiment_id": "ML-FULL-KEY-BLIND-...",
      "recipe_id": "selected-recipe-id",
      "feature_mode": "compressed_bits_257",
      "architecture": {
        "family": "mlp",
        "params": {
          "hidden_layers": [128, 128],
          "activation": "relu",
          "alpha": 0.0001,
          "batch_size": 2048,
          "learning_rate_init": 0.001,
          "epochs": 8
        },
        "max_train_records": 2000000
      },
      "ensemble_seeds": [101, 202, 303, 404, 505],
      "train_records_per_manifest": 1000000,
      "dev_records_per_manifest": 200000,
      "development_splits": ["train", "validation", "test"],
      "jobs": 8,
      "feature_workers": 8,
      "prediction_batch_records": 25000,
      "thresholds": {
        "minimum_information_bits_per_key": 0.01,
        "minimum_bit_accuracy_lift": 0.001,
        "minimum_paired_z": 5.0
      },
      "frozen_from": {
        "search_result_sha256": "<64 lowercase hexadecimal characters>"
      }
    }

``development_splits`` declares the ordered, already-used development pool.
After recipe selection, ``train_records_per_manifest`` records are taken
across those splits and pooled for the final fit.  ``dev_records_per_manifest``
is retained as provenance for the search-time holdout size; it is not added a
second time.  ``architecture.max_train_records`` is then applied to the
balanced, interleaved pool from exactly two development manifests.

The program fits exactly five independently seeded models, constructs one
``ProbabilityEnsemble``, and only then opens ``blind_a`` and ``blind_b`` from a
third dataset.  It never selects, refits, early-stops, calibrates, or otherwise
changes the frozen ensemble using either blind half.  A signal decision
requires the same frozen ensemble to cross every point threshold and have
positive lower 95% confidence bounds for information and accuracy lift on
both halves.
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import platform
import time
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import sklearn

from full_key_common import (
    RECORD_SIZE,
    FeatureStore,
    ProbabilityEnsemble,
    build_model,
    evaluate_model,
    scalar_bits,
    signal_threshold_crossed,
)


HERE = Path(__file__).resolve().parent
REQUIRED_THRESHOLD_FIELDS = {
    "minimum_information_bits_per_key",
    "minimum_bit_accuracy_lift",
    "minimum_paired_z",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object: {path}")
    return value


def _positive_integer(recipe: dict[str, Any], field: str) -> int:
    value = recipe.get(field)
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"frozen recipe {field} must be a positive integer")
    return value


def load_frozen_recipe(path: Path) -> dict[str, Any]:
    recipe = load_json(path)
    required = {
        "schema_version",
        "experiment_id",
        "recipe_id",
        "feature_mode",
        "architecture",
        "ensemble_seeds",
        "train_records_per_manifest",
        "dev_records_per_manifest",
        "development_splits",
        "jobs",
        "feature_workers",
        "prediction_batch_records",
        "thresholds",
        "frozen_from",
    }
    missing = sorted(required - set(recipe))
    if missing:
        raise ValueError(f"frozen recipe missing fields: {missing}")
    if recipe["schema_version"] != 1:
        raise ValueError("unsupported frozen recipe schema_version")
    for field in ("experiment_id", "recipe_id", "feature_mode"):
        if not isinstance(recipe[field], str) or not recipe[field].strip():
            raise ValueError(f"frozen recipe {field} must be a nonempty string")

    architecture = recipe["architecture"]
    if not isinstance(architecture, dict):
        raise ValueError("frozen recipe architecture must be an object")
    if not isinstance(architecture.get("family"), str):
        raise ValueError("frozen architecture family must be a string")
    if not isinstance(architecture.get("params"), dict):
        raise ValueError("frozen architecture params must be an object")
    max_train = architecture.get("max_train_records")
    if isinstance(max_train, bool) or not isinstance(max_train, int) or max_train <= 0:
        raise ValueError(
            "frozen architecture max_train_records must be a positive integer"
        )

    seeds = recipe["ensemble_seeds"]
    if (
        not isinstance(seeds, list)
        or len(seeds) != 5
        or len(set(seeds)) != 5
        or any(isinstance(seed, bool) or not isinstance(seed, int) for seed in seeds)
    ):
        raise ValueError("ensemble_seeds must contain exactly five unique integers")

    for field in (
        "train_records_per_manifest",
        "dev_records_per_manifest",
        "jobs",
        "feature_workers",
        "prediction_batch_records",
    ):
        _positive_integer(recipe, field)

    development_splits = recipe["development_splits"]
    if (
        not isinstance(development_splits, list)
        or not development_splits
        or len(development_splits) != len(set(development_splits))
        or any(not isinstance(value, str) or not value for value in development_splits)
    ):
        raise ValueError(
            "development_splits must contain unique nonempty split names"
        )
    if any(value in ("blind_a", "blind_b") for value in development_splits):
        raise ValueError("development_splits must not include blind splits")

    thresholds = recipe["thresholds"]
    if not isinstance(thresholds, dict):
        raise ValueError("frozen recipe thresholds must be an object")
    missing_thresholds = sorted(REQUIRED_THRESHOLD_FIELDS - set(thresholds))
    if missing_thresholds:
        raise ValueError(
            f"frozen recipe thresholds missing fields: {missing_thresholds}"
        )
    for field in REQUIRED_THRESHOLD_FIELDS:
        value = thresholds[field]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"threshold {field} must be numeric")
        if not np.isfinite(value):
            raise ValueError(f"threshold {field} must be finite")

    frozen_from = recipe["frozen_from"]
    if not isinstance(frozen_from, dict):
        raise ValueError("frozen_from must be an object")
    search_hash = frozen_from.get("search_result_sha256")
    if (
        not isinstance(search_hash, str)
        or len(search_hash) != 64
        or any(character not in "0123456789abcdef" for character in search_hash)
    ):
        raise ValueError(
            "frozen_from.search_result_sha256 must be 64 lowercase hex characters"
        )
    return recipe


def validate_manifest(manifest: dict[str, Any], path: Path) -> None:
    if manifest.get("curve") != "secp256k1":
        raise ValueError(f"manifest is not secp256k1: {path}")
    if int(manifest.get("record_size_bytes", -1)) != RECORD_SIZE:
        raise ValueError(f"manifest has an unexpected record size: {path}")
    if not isinstance(manifest.get("splits"), dict):
        raise ValueError(f"manifest has no split map: {path}")
    if not isinstance(manifest.get("shards"), list):
        raise ValueError(f"manifest has no shard list: {path}")
    root_hash = manifest.get("dataset_root_sha256")
    if not isinstance(root_hash, str) or len(root_hash) != 64:
        raise ValueError(f"manifest has no valid dataset root hash: {path}")


def load_split(
    manifest: dict[str, Any],
    dataset_root: Path,
    split: str,
    limit: int,
) -> np.ndarray:
    available = int(manifest["splits"].get(split, 0))
    if available < limit:
        raise ValueError(
            f"split {split} has {available} records, but frozen recipe requires {limit}"
        )
    shards = sorted(
        (item for item in manifest["shards"] if item["split"] == split),
        key=lambda item: int(item["part"]),
    )
    pieces: list[np.ndarray] = []
    remaining = limit
    for shard in shards:
        if remaining <= 0:
            break
        path = dataset_root / shard["relative_path"]
        expected_bytes = int(shard["byte_count"])
        if path.stat().st_size != expected_bytes:
            raise ValueError(f"shard byte count mismatch: {path}")
        expected_hash = shard.get("sha256")
        if not isinstance(expected_hash, str) or sha256_file(path) != expected_hash:
            raise ValueError(f"shard SHA-256 mismatch: {path}")
        records = np.fromfile(path, dtype=np.uint8)
        if len(records) % RECORD_SIZE:
            raise ValueError(f"shard is not record aligned: {path}")
        records = records.reshape((-1, RECORD_SIZE))
        expected_records = int(shard["record_count"])
        if len(records) != expected_records:
            raise ValueError(f"shard record count mismatch: {path}")
        take = min(remaining, len(records))
        pieces.append(records[:take])
        remaining -= take
    if remaining:
        raise ValueError(f"split {split} is short by {remaining} records")
    return np.concatenate(pieces, axis=0)


def load_development_pool(
    manifest: dict[str, Any],
    dataset_root: Path,
    splits: list[str],
    limit: int,
) -> tuple[np.ndarray, dict[str, int]]:
    available = sum(int(manifest["splits"].get(split, 0)) for split in splits)
    if available < limit:
        raise ValueError(
            f"development pool has {available} records, but frozen recipe "
            f"requires {limit}"
        )
    pieces: list[np.ndarray] = []
    used: dict[str, int] = {}
    remaining = limit
    for split in splits:
        if remaining <= 0:
            break
        take = min(remaining, int(manifest["splits"].get(split, 0)))
        if take:
            pieces.append(load_split(manifest, dataset_root, split, take))
            used[split] = take
            remaining -= take
    if remaining:
        raise ValueError(f"development pool is short by {remaining} records")
    return np.concatenate(pieces, axis=0), used


def append_ledger(path: Path, entry: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(
            json.dumps(
                entry,
                sort_keys=True,
                ensure_ascii=True,
                allow_nan=False,
            )
            + "\n"
        )
        handle.flush()


def threshold_crossed(
    metrics: dict[str, Any], thresholds: dict[str, Any]
) -> bool:
    return signal_threshold_crossed(
        metrics,
        minimum_information_bits_per_key=float(
            thresholds["minimum_information_bits_per_key"]
        ),
        minimum_bit_accuracy_lift=float(
            thresholds["minimum_bit_accuracy_lift"]
        ),
        minimum_paired_z=float(thresholds["minimum_paired_z"]),
    )


def _balanced_interleave(pools: list[np.ndarray]) -> np.ndarray:
    if len(pools) != 2 or len(pools[0]) != len(pools[1]):
        raise ValueError("blind runner requires two equal-size development pools")
    return np.stack(pools, axis=1).reshape((-1, RECORD_SIZE))


def render_markdown(result: dict[str, Any]) -> str:
    decision = result["decision"]
    lines = [
        f"# {result['experiment_id']} frozen blind evaluation",
        "",
        "## Decision",
        "",
        f"- Pipeline status: `{result['pipeline_status']}`",
        f"- Both blind halves crossed: `{decision['crossed_both_blind_halves']}`",
        f"- Interpretation: {result['interpretation']}",
        "",
        "The five model seeds, feature representation, architecture, training "
        "budget, and thresholds were frozen before either blind split was "
        "loaded. One probability-averaging ensemble was evaluated unchanged "
        "on both halves. No blind metric was used for fitting or selection.",
        "",
        "## Dataset separation",
        "",
        "| role | dataset root SHA-256 | manifest SHA-256 | records used |",
        "|---|---|---|---:|",
    ]
    for item in result["datasets"]["development"]:
        lines.append(
            f"| development | `{item['dataset_root_sha256']}` | "
            f"`{item['manifest_sha256']}` | {item['records_used']:,} |"
        )
    blind = result["datasets"]["blind"]
    lines.append(
        f"| blind_a + blind_b | `{blind['dataset_root_sha256']}` | "
        f"`{blind['manifest_sha256']}` | {blind['records_used']:,} |"
    )
    lines.extend(
        [
            "",
            "## Frozen ensemble",
            "",
            f"- Recipe: `{result['frozen_recipe']['recipe_id']}`",
            f"- Recipe SHA-256: `{result['frozen_recipe_sha256']}`",
            f"- Feature mode: `{result['frozen_recipe']['feature_mode']}`",
            f"- Family: `{result['frozen_recipe']['architecture']['family']}`",
            "- Seeds: `"
            + ", ".join(
                str(value)
                for value in result["frozen_recipe"]["ensemble_seeds"]
            )
            + "`",
            f"- Actual fit records: `{result['training']['fit_records']:,}`",
            f"- Models fitted: `{result['training']['models_fitted']}`",
            f"- Total fit time: "
            f"`{result['training']['total_fit_seconds']:.3f}` seconds",
            "",
            "## Blind metrics",
            "",
            "| half | records | info bits/key | info 95% low | bit lift | "
            "lift 95% low | paired z | mean Hamming | exact keys | threshold |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for split in ("blind_a", "blind_b"):
        item = result["blind_evaluations"][split]
        metrics = item["metrics"]
        lines.append(
            f"| {split} | {metrics['records']:,} | "
            f"{metrics['information_gain_bits_per_key']:.8g} | "
            f"{metrics['information_gain_95ci_bits_per_key'][0]:.8g} | "
            f"{metrics['bit_accuracy_lift']:.8g} | "
            f"{metrics['bit_accuracy_lift_95ci'][0]:.8g} | "
            f"{metrics['paired_accuracy_z']:.5g} | "
            f"{metrics['mean_hamming_distance']:.6g} | "
            f"{metrics['exact_key_matches']} | "
            f"{item['threshold_crossed']} |"
        )
    lines.extend(
        [
            "",
            "## Frozen thresholds",
            "",
            "| metric | minimum |",
            "|---|---:|",
            f"| information gain, bits/key | "
            f"{decision['thresholds']['minimum_information_bits_per_key']} |",
            f"| bit accuracy lift | "
            f"{decision['thresholds']['minimum_bit_accuracy_lift']} |",
            f"| paired accuracy z | "
            f"{decision['thresholds']['minimum_paired_z']} |",
            "| lower 95% CI, information gain | > 0 |",
            "| lower 95% CI, bit accuracy lift | > 0 |",
            "",
            "## Frozen recipe schema and value",
            "",
            "Schema version 1 requires the exact recipe fields shown below. "
            "`development_splits` declares the ordered development pool and "
            "`train_records_per_manifest` is the total taken across it. "
            "`dev_records_per_manifest` records the search-time holdout size "
            "for provenance and is not counted twice. Exactly five unique "
            "ensemble seeds are required. The two blind portions are "
            "evaluation-only.",
            "",
            "```json",
            json.dumps(
                result["frozen_recipe"],
                indent=2,
                sort_keys=True,
                ensure_ascii=True,
                allow_nan=False,
            ),
            "```",
            "",
            "## Scope",
            "",
            "This is a bounded synthetic secp256k1 representation assay. A "
            "threshold crossing is not a discrete-log solution or a complexity "
            "claim. It requires independent leakage review, reproduction, and "
            "mechanism extraction before any research-route consideration.",
            "",
        ]
    )
    return "\n".join(lines)


def run_blind(
    recipe_path: Path,
    development_manifest_paths: list[Path],
    development_roots: list[Path],
    blind_manifest_path: Path,
    blind_root: Path,
    output_dir: Path,
    search_result_path: Path | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    if len(development_manifest_paths) != 2 or len(development_roots) != 2:
        raise ValueError(
            "exactly two development manifests and two paired roots are required"
        )
    recipe = load_frozen_recipe(recipe_path)
    recipe_hash = sha256_file(recipe_path)
    if search_result_path is not None:
        observed_search_hash = sha256_file(search_result_path)
        expected_search_hash = recipe["frozen_from"]["search_result_sha256"]
        if observed_search_hash != expected_search_hash:
            raise ValueError("frozen recipe does not bind the supplied search result")

    output_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = output_dir / "blind_run_ledger.jsonl"
    result_path = output_dir / "blind_result.json"
    report_path = output_dir / "blind_report.md"
    existing = [
        path
        for path in (ledger_path, result_path, report_path)
        if path.exists()
    ]
    if existing and not overwrite:
        raise FileExistsError(
            "blind outputs already exist; use --overwrite only for an intentional rerun"
        )
    ledger_path.write_text("", encoding="utf-8")

    development_manifests = [
        load_json(path) for path in development_manifest_paths
    ]
    blind_manifest = load_json(blind_manifest_path)
    for manifest, path in zip(
        development_manifests, development_manifest_paths, strict=True
    ):
        validate_manifest(manifest, path)
    validate_manifest(blind_manifest, blind_manifest_path)
    root_hashes = [
        manifest["dataset_root_sha256"] for manifest in development_manifests
    ] + [blind_manifest["dataset_root_sha256"]]
    if len(set(root_hashes)) != 3:
        raise ValueError(
            "both development datasets and the blind dataset must have distinct roots"
        )
    for split in ("blind_a", "blind_b"):
        if int(blind_manifest["splits"].get(split, 0)) <= 0:
            raise ValueError(f"blind manifest is missing a nonempty {split} split")

    train_count = int(recipe["train_records_per_manifest"])
    dev_count = int(recipe["dev_records_per_manifest"])
    development_splits = list(recipe["development_splits"])
    development_pools: list[np.ndarray] = []
    development_dataset_results: list[dict[str, Any]] = []
    for index, (manifest, manifest_path, dataset_root) in enumerate(
        zip(
            development_manifests,
            development_manifest_paths,
            development_roots,
            strict=True,
        )
    ):
        pool, split_records = load_development_pool(
            manifest,
            dataset_root,
            development_splits,
            train_count,
        )
        development_pools.append(pool)
        development_dataset_results.append(
            {
                "index": index,
                "dataset_root_sha256": manifest["dataset_root_sha256"],
                "manifest_sha256": sha256_file(manifest_path),
                "dataset_root": str(dataset_root),
                "development_splits": development_splits,
                "split_records": split_records,
                "search_dev_records_provenance": dev_count,
                "records_used": len(pool),
            }
        )

    all_fit_records = _balanced_interleave(development_pools)
    max_train_records = int(recipe["architecture"]["max_train_records"])
    fit_records = all_fit_records[: min(len(all_fit_records), max_train_records)]
    fit_labels = scalar_bits(fit_records)
    train_priors = (fit_labels.sum(axis=0, dtype=np.float64) + 1.0) / (
        len(fit_labels) + 2.0
    )
    feature_store = FeatureStore(
        fit_records, workers=int(recipe["feature_workers"])
    )
    fit_features = feature_store.get(recipe["feature_mode"])

    models: list[Any] = []
    fit_entries: list[dict[str, Any]] = []
    for seed in recipe["ensemble_seeds"]:
        run_id = f"fit/seed-{seed}"
        started = time.perf_counter()
        try:
            model = build_model(
                recipe["architecture"],
                int(seed),
                int(recipe["jobs"]),
            )
            with warnings.catch_warnings(record=True) as captured:
                warnings.simplefilter("always")
                model.fit(fit_features, fit_labels)
            fit_seconds = time.perf_counter() - started
            entry = {
                "run_id": run_id,
                "stage": "frozen_fit",
                "status": "completed",
                "recipe_sha256": recipe_hash,
                "recipe_id": recipe["recipe_id"],
                "model_seed": seed,
                "feature_mode": recipe["feature_mode"],
                "architecture": recipe["architecture"],
                "fit_records": len(fit_records),
                "fit_seconds": fit_seconds,
                "train_loss_curve": [
                    float(value) for value in getattr(model, "loss_curve_", [])
                ],
                "warnings": [
                    f"{item.category.__name__}: {str(item.message)[:300]}"
                    for item in captured
                ],
            }
            models.append(model)
        except Exception as error:
            entry = {
                "run_id": run_id,
                "stage": "frozen_fit",
                "status": "failed",
                "recipe_sha256": recipe_hash,
                "recipe_id": recipe["recipe_id"],
                "model_seed": seed,
                "fit_records": len(fit_records),
                "elapsed_seconds": time.perf_counter() - started,
                "error_type": type(error).__name__,
                "error": str(error)[:500],
            }
            append_ledger(ledger_path, entry)
            raise
        append_ledger(ledger_path, entry)
        fit_entries.append(entry)

    if len(models) != 5:
        raise RuntimeError("frozen ensemble did not fit exactly five models")
    ensemble = ProbabilityEnsemble(models)

    # Blind records are intentionally not opened until every frozen model is fit.
    del all_fit_records, development_pools, fit_features, fit_labels, feature_store
    gc.collect()

    blind_evaluations: dict[str, Any] = {}
    blind_records_total = 0
    for split in ("blind_a", "blind_b"):
        split_count = int(blind_manifest["splits"][split])
        records = load_split(blind_manifest, blind_root, split, split_count)
        labels = scalar_bits(records)
        features = FeatureStore(
            records, workers=int(recipe["feature_workers"])
        ).get(recipe["feature_mode"])
        started = time.perf_counter()
        metrics = evaluate_model(
            ensemble,
            features,
            labels,
            train_priors,
            int(recipe["prediction_batch_records"]),
            detailed=True,
        )
        evaluation_seconds = time.perf_counter() - started
        crossed = threshold_crossed(metrics, recipe["thresholds"])
        entry = {
            "run_id": f"blind_evaluation/{split}",
            "stage": "blind_evaluation",
            "status": "completed",
            "recipe_sha256": recipe_hash,
            "dataset_root_sha256": blind_manifest["dataset_root_sha256"],
            "split": split,
            "ensemble_seeds": recipe["ensemble_seeds"],
            "records": len(records),
            "evaluation_seconds": evaluation_seconds,
            "threshold_crossed": crossed,
            "metrics": metrics,
        }
        append_ledger(ledger_path, entry)
        blind_evaluations[split] = {
            "evaluation_seconds": evaluation_seconds,
            "threshold_crossed": crossed,
            "metrics": metrics,
        }
        blind_records_total += len(records)
        del records, labels, features
        gc.collect()

    crossed_both = all(
        blind_evaluations[split]["threshold_crossed"]
        for split in ("blind_a", "blind_b")
    )
    decision_entry = {
        "run_id": "decision/both_blind_halves",
        "stage": "frozen_decision",
        "status": "completed",
        "thresholds": recipe["thresholds"],
        "confidence_requirements": {
            "information_gain_95ci_lower_greater_than": 0.0,
            "bit_accuracy_lift_95ci_lower_greater_than": 0.0,
        },
        "blind_a_crossed": blind_evaluations["blind_a"]["threshold_crossed"],
        "blind_b_crossed": blind_evaluations["blind_b"]["threshold_crossed"],
        "crossed_both_blind_halves": crossed_both,
    }
    append_ledger(ledger_path, decision_entry)

    result = {
        "schema_version": 1,
        "experiment_id": recipe["experiment_id"],
        "result_role": "frozen_full_key_ensemble_blind_evaluation",
        "scientific_evidence": False,
        "route_promotion_authorized": False,
        "pipeline_status": "pass",
        "frozen_recipe": recipe,
        "frozen_recipe_sha256": recipe_hash,
        "frozen_from_search_verified": search_result_path is not None,
        "source": {
            "full_key_blind_sha256": sha256_file(Path(__file__)),
            "full_key_common_sha256": sha256_file(HERE / "full_key_common.py"),
        },
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scikit_learn": sklearn.__version__,
            "platform": platform.platform(),
        },
        "datasets": {
            "development": development_dataset_results,
            "blind": {
                "dataset_root_sha256": blind_manifest["dataset_root_sha256"],
                "manifest_sha256": sha256_file(blind_manifest_path),
                "dataset_root": str(blind_root),
                "splits": ["blind_a", "blind_b"],
                "records_used": blind_records_total,
            },
        },
        "training": {
            "models_fitted": len(models),
            "fit_records": len(fit_records),
            "available_development_records": 2 * train_count,
            "max_train_records": max_train_records,
            "search_dev_records_per_manifest_provenance": dev_count,
            "total_fit_seconds": sum(
                float(entry["fit_seconds"]) for entry in fit_entries
            ),
            "model_runs": [
                {
                    "run_id": entry["run_id"],
                    "model_seed": entry["model_seed"],
                    "fit_seconds": entry["fit_seconds"],
                    "warnings": entry["warnings"],
                    "train_loss_curve": entry["train_loss_curve"],
                }
                for entry in fit_entries
            ],
            "train_priors": [float(value) for value in train_priors],
        },
        "blind_evaluations": blind_evaluations,
        "decision": {
            "rule": (
                "all frozen point thresholds and both positive lower 95% "
                "confidence bounds must be satisfied independently on blind_a "
                "and blind_b by the same unchanged ensemble"
            ),
            "thresholds": recipe["thresholds"],
            "confidence_requirements": {
                "information_gain_95ci_lower_greater_than": 0.0,
                "bit_accuracy_lift_95ci_lower_greater_than": 0.0,
            },
            "blind_a_crossed": blind_evaluations["blind_a"][
                "threshold_crossed"
            ],
            "blind_b_crossed": blind_evaluations["blind_b"][
                "threshold_crossed"
            ],
            "crossed_both_blind_halves": crossed_both,
        },
        "interpretation": (
            "The same frozen five-seed ensemble crossed every preregistered "
            "threshold on both untouched blind halves. This requires independent "
            "leakage review, reproduction, and mechanism extraction."
            if crossed_both
            else "The frozen five-seed ensemble did not cross every preregistered "
            "threshold on both untouched blind halves. This is a bounded blind "
            "null for the recorded data, representation, model, and compute budget."
        ),
        "ledger": {
            "path": ledger_path.name,
            "sha256": sha256_file(ledger_path),
            "entries": len(fit_entries) + 3,
        },
        "scope": [
            "Synthetic secp256k1 pairs only; no wallet or target key data.",
            (
                "No model, hyperparameter, threshold, calibration, or stopping "
                "decision used blind data."
            ),
            (
                "One unchanged probability-averaging ensemble evaluated both "
                "blind halves."
            ),
            (
                "A positive threshold decision is not a discrete-log solution "
                "or complexity claim."
            ),
        ],
    }
    result_path.write_text(
        json.dumps(
            result,
            indent=2,
            sort_keys=True,
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n",
        encoding="utf-8",
    )
    report_path.write_text(render_markdown(result), encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fit one frozen five-seed ensemble and evaluate blind halves."
    )
    parser.add_argument("--recipe", type=Path, required=True)
    parser.add_argument(
        "--development-manifest",
        type=Path,
        action="append",
        required=True,
        help="Repeat exactly twice, in the same order as --development-root.",
    )
    parser.add_argument(
        "--development-root",
        type=Path,
        action="append",
        help=(
            "Optional dataset root paired with --development-manifest. "
            "Repeat exactly twice or omit to use each manifest parent."
        ),
    )
    parser.add_argument("--blind-manifest", type=Path, required=True)
    parser.add_argument(
        "--blind-root",
        type=Path,
        help="Optional blind dataset root; defaults to the blind manifest parent.",
    )
    parser.add_argument(
        "--search-result",
        type=Path,
        help="Optional search result whose SHA-256 must match frozen_from.",
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    development_manifest_paths = [
        path.resolve() for path in args.development_manifest
    ]
    if len(development_manifest_paths) != 2:
        parser.error("--development-manifest must be supplied exactly twice")
    if args.development_root:
        if len(args.development_root) != 2:
            parser.error("--development-root must be supplied exactly twice")
        development_roots = [path.resolve() for path in args.development_root]
    else:
        development_roots = [
            path.parent for path in development_manifest_paths
        ]
    blind_manifest_path = args.blind_manifest.resolve()
    blind_root = (
        args.blind_root.resolve()
        if args.blind_root
        else blind_manifest_path.parent
    )
    result = run_blind(
        args.recipe.resolve(),
        development_manifest_paths,
        development_roots,
        blind_manifest_path,
        blind_root,
        args.output_dir.resolve(),
        args.search_result.resolve() if args.search_result else None,
        overwrite=args.overwrite,
    )
    print(
        json.dumps(
            {
                "pipeline_status": result["pipeline_status"],
                "crossed_both_blind_halves": result["decision"][
                    "crossed_both_blind_halves"
                ],
                "result": str(args.output_dir.resolve() / "blind_result.json"),
                "report": str(args.output_dir.resolve() / "blind_report.md"),
                "ledger": str(
                    args.output_dir.resolve() / "blind_run_ledger.jsonl"
                ),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
