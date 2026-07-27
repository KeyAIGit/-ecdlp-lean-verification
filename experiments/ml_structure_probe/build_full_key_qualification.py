#!/usr/bin/env python3
"""Build the retained full-key qualification summary and report artifact."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _median(values: list[float]) -> float:
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2.0


def control_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    nulls = [
        row
        for row in rows
        if row["stage"] in ("control_random_labels", "control_permuted_keys")
    ]
    leak_one = [row for row in rows if row["stage"] == "control_label_leak_1"]
    leak_eight = [row for row in rows if row["stage"] == "control_label_leak_8"]
    leak_32 = [row for row in rows if row["stage"] == "control_label_leak_32"]
    if not (len(nulls) == 6 and len(leak_one) == len(leak_eight) == len(leak_32) == 2):
        raise ValueError("unexpected control ledger shape")

    null_pass = all(
        row["validation"]["information_gain_bits_per_key"] < 0.01
        and row["validation"]["paired_accuracy_z"] < 5.0
        for row in nulls
    )
    leak_one_pass = all(
        row["validation"]["best_information_bit"]["bit_big_endian"] == 0
        and row["validation"]["best_information_bit"]["information_gain_bits"] > 0.25
        and row["validation"]["best_information_bit"]["accuracy_lift"] > 0.45
        and row["validation"]["best_information_bit"]["paired_z"] > 20
        for row in leak_one
    )
    leak_eight_pass = all(
        row["validation"]["information_gain_bits_per_key"] > 1.0
        and row["validation"]["bit_accuracy_lift"] > 0.01
        for row in leak_eight
    )
    leak_32_pass = all(
        row["validation"]["information_gain_bits_per_key"] > 5.0
        and row["validation"]["bit_accuracy_lift"] > 0.05
        for row in leak_32
    )
    return {
        "pass": null_pass and leak_one_pass and leak_eight_pass and leak_32_pass,
        "negative_controls_pass": null_pass,
        "leak_1_pass": leak_one_pass,
        "leak_8_pass": leak_eight_pass,
        "leak_32_pass": leak_32_pass,
        "max_null_information_bits_per_key": max(
            row["validation"]["information_gain_bits_per_key"] for row in nulls
        ),
        "max_null_accuracy_z": max(
            row["validation"]["paired_accuracy_z"] for row in nulls
        ),
        "leak_1_target_bit_information_range": [
            min(
                row["validation"]["best_information_bit"]["information_gain_bits"]
                for row in leak_one
            ),
            max(
                row["validation"]["best_information_bit"]["information_gain_bits"]
                for row in leak_one
            ),
        ],
        "leak_8_information_range": [
            min(row["validation"]["information_gain_bits_per_key"] for row in leak_eight),
            max(row["validation"]["information_gain_bits_per_key"] for row in leak_eight),
        ],
        "leak_32_information_range": [
            min(row["validation"]["information_gain_bits_per_key"] for row in leak_32),
            max(row["validation"]["information_gain_bits_per_key"] for row in leak_32),
        ],
    }


def representation_rows(search: dict[str, Any]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in search["screen_ranking"]:
        grouped[item["architecture"]["feature_mode"]].append(item)
    independent = {
        "compressed_bits_264": 257,
        "compressed_bits_257": 257,
        "compressed_bytes": 257,
        "x_limbs16": 257,
        "byte_popcounts": 257,
        "affine_bytes": 257,
        "affine_bits_512": 257,
        "affine_limbs16": 257,
        "bit_interactions_64": 257,
    }
    physical = {
        "compressed_bits_264": 264,
        "compressed_bits_257": 257,
        "compressed_bytes": 264,
        "x_limbs16": 257,
        "byte_popcounts": 264,
        "affine_bytes": 512,
        "affine_bits_512": 512,
        "affine_limbs16": 512,
        "bit_interactions_64": 321,
    }
    output: list[dict[str, Any]] = []
    for mode, items in sorted(grouped.items()):
        best = max(items, key=lambda item: item["conservative_score"])
        output.append(
            {
                "representation": mode,
                "architectures": len(items),
                "physical_input_columns": physical[mode],
                "independent_public_bits": independent[mode],
                "best_architecture": best["architecture_id"],
                "best_family": best["architecture"]["family"],
                "best_median_information_bits_per_key": best[
                    "median_information_bits_per_key"
                ],
                "survived_screen": any(
                    survivor["architecture_id"] == best["architecture_id"]
                    for survivor in search["screen_survivors"]
                ),
            }
        )
    return output


def mlp_scaling_rows(ledger: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected = [
        row
        for row in ledger
        if row.get("architecture_id") == "arch-039"
        and row["stage"] in ("screen", "confirm", "cross_dataset")
    ]
    output: list[dict[str, Any]] = []
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in selected:
        grouped[(row["stage"], row.get("direction", "mixed"))].append(row)
    order = {
        ("screen", "mixed"): 1,
        ("confirm", "mixed"): 2,
        ("cross_dataset", "primary_to_replica"): 3,
        ("cross_dataset", "replica_to_primary"): 4,
    }
    for key, rows in sorted(grouped.items(), key=lambda item: order[item[0]]):
        stage, direction = key
        output.append(
            {
                "stage": stage,
                "direction": direction,
                "train_records": rows[0]["train_records"],
                "validation_records": rows[0]["validation_records"],
                "epochs": rows[0]["architecture"]["params"]["epochs"],
                "seeds": len(rows),
                "median_information_bits_per_key": _median(
                    [
                        row["validation"]["information_gain_bits_per_key"]
                        for row in rows
                    ]
                ),
                "median_bit_accuracy_lift": _median(
                    [row["validation"]["bit_accuracy_lift"] for row in rows]
                ),
                "median_final_train_loss_nats_per_key": _median(
                    [row["train_loss_curve"][-1] for row in rows]
                ),
            }
        )
    return output


def comparison_rows(
    search: dict[str, Any],
    ledger: list[dict[str, Any]],
    blind: dict[str, Any],
) -> list[dict[str, Any]]:
    screen_best = max(
        search["screen_ranking"],
        key=lambda item: item["conservative_score"],
    )
    confirm_best = max(
        search["confirm_ranking"],
        key=lambda item: item["conservative_score"],
    )
    cross = [
        row
        for row in ledger
        if row["stage"] == "cross_dataset"
        and row["architecture_id"] == search["winner"]["architecture_id"]
    ]
    rows = [
        {
            "order": 1,
            "evaluation": "Screen best",
            "role": "adaptive development",
            "model": screen_best["architecture_id"],
            "family": screen_best["architecture"]["family"],
            "feature_mode": screen_best["architecture"]["feature_mode"],
            "records": 100_000,
            "information_gain_bits_per_key": screen_best[
                "median_information_bits_per_key"
            ],
            "bit_accuracy_lift": screen_best["median_bit_accuracy_lift"],
            "exact_key_matches": None,
        },
        {
            "order": 2,
            "evaluation": "Confirm best",
            "role": "adaptive development",
            "model": confirm_best["architecture_id"],
            "family": confirm_best["architecture"]["family"],
            "feature_mode": confirm_best["architecture"]["feature_mode"],
            "records": 200_000,
            "information_gain_bits_per_key": confirm_best[
                "median_information_bits_per_key"
            ],
            "bit_accuracy_lift": confirm_best["median_bit_accuracy_lift"],
            "exact_key_matches": None,
        },
    ]
    for index, row in enumerate(cross, start=3):
        metrics = row["validation"]
        rows.append(
            {
                "order": index,
                "evaluation": row["direction"].replace("_", " "),
                "role": "cross-dataset development",
                "model": row["architecture_id"],
                "family": row["family"],
                "feature_mode": row["feature_mode"],
                "records": metrics["records"],
                "information_gain_bits_per_key": metrics[
                    "information_gain_bits_per_key"
                ],
                "bit_accuracy_lift": metrics["bit_accuracy_lift"],
                "exact_key_matches": metrics["exact_key_matches"],
            }
        )
    development = search["development_ensemble_metrics"]
    rows.append(
        {
            "order": 5,
            "evaluation": "Development ensemble",
            "role": "post-selection development",
            "model": search["winner"]["architecture_id"],
            "family": search["winner"]["architecture"]["family"],
            "feature_mode": search["winner"]["architecture"]["feature_mode"],
            "records": development["records"],
            "information_gain_bits_per_key": development[
                "information_gain_bits_per_key"
            ],
            "bit_accuracy_lift": development["bit_accuracy_lift"],
            "exact_key_matches": development["exact_key_matches"],
        }
    )
    for index, split in enumerate(("blind_a", "blind_b"), start=6):
        metrics = blind["blind_evaluations"][split]["metrics"]
        rows.append(
            {
                "order": index,
                "evaluation": split,
                "role": "frozen blind",
                "model": blind["frozen_recipe"]["recipe_id"],
                "family": blind["frozen_recipe"]["architecture"]["family"],
                "feature_mode": blind["frozen_recipe"]["feature_mode"],
                "records": metrics["records"],
                "information_gain_bits_per_key": metrics[
                    "information_gain_bits_per_key"
                ],
                "bit_accuracy_lift": metrics["bit_accuracy_lift"],
                "exact_key_matches": metrics["exact_key_matches"],
            }
        )
    return rows


def _sql_literal(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, float)):
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError("non-finite value cannot be represented in report SQL")
        return repr(value)
    escaped = str(value).replace("'", "''")
    return f"'{escaped}'"


def _values_sql(rows: list[dict[str, Any]], fields: list[str]) -> str:
    if not rows:
        raise ValueError("report source query requires at least one row")
    values = ",\n  ".join(
        "(" + ", ".join(_sql_literal(row.get(field)) for field in fields) + ")"
        for row in rows
    )
    columns = ", ".join(f'"{field}"' for field in fields)
    return f"SELECT * FROM (VALUES\n  {values}\n) AS report_rows({columns})"


def _artifact_source(
    source_id: str,
    label: str,
    path: str,
    rows: list[dict[str, Any]],
    fields: list[str],
    description: str,
    tables_used: list[str],
    filters: list[str],
    metric_definitions: list[str],
) -> dict[str, Any]:
    return {
        "id": source_id,
        "label": label,
        "path": path,
        "query": {
            "engine": "DuckDB",
            "language": "SQL",
            "sql": _values_sql(rows, fields),
            "description": description,
            "tables_used": tables_used,
            "filters": filters,
            "metric_definitions": metric_definitions,
        },
    }


def build_artifact(
    summary: dict[str, Any],
    search: dict[str, Any],
    blind: dict[str, Any],
    comparisons: list[dict[str, Any]],
    representations: list[dict[str, Any]],
    scaling: list[dict[str, Any]],
) -> dict[str, Any]:
    generated_at = summary["generated_at"]
    headline_rows = [
        {
            "attempts": summary["search"]["attempted"],
            "failures": summary["search"]["failed"],
            "synthetic_pairs": summary["datasets"]["total_unique_pairs"],
            "exact_blind_keys": summary["blind"]["exact_key_matches_total"],
            "blind_halves_crossed": int(summary["blind"]["crossed_both_halves"]),
        }
    ]
    blind_rows = []
    for split in ("blind_a", "blind_b"):
        metrics = blind["blind_evaluations"][split]["metrics"]
        blind_rows.append(
            {
                "half": split,
                "records": metrics["records"],
                "information_gain_bits_per_key": metrics[
                    "information_gain_bits_per_key"
                ],
                "info_ci_low": metrics["information_gain_95ci_bits_per_key"][0],
                "info_ci_high": metrics["information_gain_95ci_bits_per_key"][1],
                "bit_accuracy": metrics["bit_accuracy"],
                "null_bit_accuracy": metrics["null_bit_accuracy"],
                "bit_accuracy_lift": metrics["bit_accuracy_lift"],
                "lift_ci_low": metrics["bit_accuracy_lift_95ci"][0],
                "lift_ci_high": metrics["bit_accuracy_lift_95ci"][1],
                "clustered_accuracy_z": metrics["paired_accuracy_z"],
                "mean_hamming_distance": metrics["mean_hamming_distance"],
                "exact_key_matches": metrics["exact_key_matches"],
                "threshold_crossed": blind["blind_evaluations"][split][
                    "threshold_crossed"
                ],
            }
        )
    stage_rows = [
        {
            "stage": stage,
            "attempts": item["attempted"],
            "successful": item["successful"],
            "failed": item["failed"],
        }
        for stage, item in search["stage_summary"].items()
    ]
    control_rows = [
        {
            "control": "Random + permuted labels",
            "attempts": 6,
            "criterion": "No gain and z < 5",
            "observed": (
                f"max gain {summary['controls']['max_null_information_bits_per_key']:.4g}; "
                f"max z {summary['controls']['max_null_accuracy_z']:.3g}"
            ),
            "passed": summary["controls"]["negative_controls_pass"],
        },
        {
            "control": "1 leaked target bit",
            "attempts": 2,
            "criterion": "Target head gain > 0.25 bit",
            "observed": (
                f"{summary['controls']['leak_1_target_bit_information_range'][0]:.3f}"
                f" to {summary['controls']['leak_1_target_bit_information_range'][1]:.3f}"
            ),
            "passed": summary["controls"]["leak_1_pass"],
        },
        {
            "control": "8 leaked target bits",
            "attempts": 2,
            "criterion": "Whole-key gain > 1 bit",
            "observed": (
                f"{summary['controls']['leak_8_information_range'][0]:.3f}"
                f" to {summary['controls']['leak_8_information_range'][1]:.3f}"
            ),
            "passed": summary["controls"]["leak_8_pass"],
        },
        {
            "control": "32 leaked target bits",
            "attempts": 2,
            "criterion": "Whole-key gain > 5 bits",
            "observed": (
                f"{summary['controls']['leak_32_information_range'][0]:.3f}"
                f" to {summary['controls']['leak_32_information_range'][1]:.3f}"
            ),
            "passed": summary["controls"]["leak_32_pass"],
        },
    ]
    search_path = "experiments/ml_structure_probe/reports/full_key_search/"
    blind_path = "experiments/ml_structure_probe/reports/full_key_blind/"
    search_tables = [
        "full_key_search_result.json",
        "full_key_run_ledger.jsonl",
    ]
    search_filters = [
        "Synthetic secp256k1 pairs only",
        "Development datasets only for architecture selection",
    ]
    information_definition = (
        "Information gain = prior-null binary cross-entropy minus model binary "
        "cross-entropy, summed over 256 bits and divided by ln(2), averaged per "
        "complete key."
    )
    sources = [
        _artifact_source(
            "headline-source",
            "Qualification headline values",
            "experiments/ml_structure_probe/reports/full_key_qualification/",
            headline_rows,
            list(headline_rows[0]),
            "Materialize the reviewed headline counts.",
            [
                "qualification_summary.json",
                "full_key_search_result.json",
                "blind_result.json",
            ],
            ["All retained development and blind results"],
            [
                "Attempts count every JSONL fit record.",
                "Exact blind keys require equality of all 256 predicted bits.",
            ],
        ),
        _artifact_source(
            "comparison-source",
            "Information-gain comparison",
            search_path,
            comparisons,
            list(comparisons[0]),
            "Materialize the reviewed evaluation-stage comparison rows.",
            search_tables + ["blind_result.json"],
            search_filters + ["Frozen metrics for blind_a and blind_b"],
            [information_definition],
        ),
        _artifact_source(
            "blind-source",
            "Frozen blind ensemble result",
            blind_path,
            blind_rows,
            list(blind_rows[0]),
            "Materialize the two frozen blind evaluation rows.",
            [
                "blind_result.json",
                "blind_run_ledger.jsonl",
                "dataset_validation.json",
            ],
            [
                "500,000 records in blind_a",
                "500,000 records in blind_b",
                "No fit, calibration, model selection, or early stopping on blind data",
            ],
            [
                information_definition,
                (
                    "Signal gate: gain >= 0.01 bits/key, accuracy lift >= 0.001, "
                    "clustered z >= 5, and both lower 95% confidence bounds > 0."
                ),
            ],
        ),
        _artifact_source(
            "representation-source",
            "Public-key representation screen",
            search_path,
            representations,
            list(representations[0]),
            "Materialize representation coverage and best screen metrics.",
            search_tables,
            search_filters,
            [
                information_definition,
                "Independent public bits count x-coordinate bits plus y parity.",
            ],
        ),
        _artifact_source(
            "stage-source",
            "AutoML stage ledger counts",
            search_path,
            stage_rows,
            list(stage_rows[0]),
            "Materialize attempted, successful and failed run counts by stage.",
            search_tables,
            ["Every predeclared ledger row"],
            ["Attempt status is read directly from the append-only JSONL ledger."],
        ),
        _artifact_source(
            "control-source",
            "Leak and null control qualification",
            search_path,
            control_rows,
            list(control_rows[0]),
            "Materialize the four preregistered control classes.",
            search_tables,
            ["Random labels, whole-key permutations, and deliberate label leaks"],
            [
                "Leak-1 is evaluated on the deliberately exposed target head.",
                "Leak-8 and leak-32 are evaluated by whole-key information gain.",
            ],
        ),
        _artifact_source(
            "scaling-source",
            "MLP scaling diagnostic",
            search_path,
            scaling,
            list(scaling[0]),
            "Materialize the arch-039 data and epoch scaling rows.",
            search_tables,
            ["Architecture arch-039 only"],
            [
                information_definition,
                "Train size and epochs changed jointly; this is not a causal ablation.",
            ],
        ),
    ]
    manifest: dict[str, Any] = {
        "version": 1,
        "surface": "report",
        "title": "ML-инверсия secp256k1: полный 256-битный тест",
        "description": (
            "Технический отчёт по 301 AutoML fit и независимой проверке "
            "frozen ensemble на новом миллионе синтетических пар."
        ),
        "generatedAt": generated_at,
        "sources": sources,
        "cards": [
            {
                "id": "attempts-card",
                "description": "Все заранее заданные попытки завершены.",
                "dataset": "headline",
                "sourceId": "headline-source",
                "metrics": [
                    {
                        "label": "AutoML fit",
                        "field": "attempts",
                        "format": "number",
                    },
                    {"label": "Failures", "field": "failures", "format": "number"},
                ],
            },
            {
                "id": "pairs-card",
                "description": "Два development-миллиона и новый blind-миллион.",
                "dataset": "headline",
                "sourceId": "headline-source",
                "metrics": [
                    {
                        "label": "Синтетические пары",
                        "field": "synthetic_pairs",
                        "format": "compact",
                    }
                ],
            },
            {
                "id": "exact-card",
                "description": "Полное совпадение всех 256 битов.",
                "dataset": "headline",
                "sourceId": "headline-source",
                "metrics": [
                    {
                        "label": "Точные blind-ключи",
                        "field": "exact_blind_keys",
                        "format": "number",
                    },
                    {
                        "label": "Halves passed",
                        "field": "blind_halves_crossed",
                        "format": "number",
                    },
                ],
            },
        ],
        "charts": [
            {
                "id": "gain-chart",
                "title": "Информационный выигрыш по этапам оценки",
                "description": (
                    "Все значения ниже нулевой линии baseline; ранние этапы "
                    "используют адаптивно выбранных лидеров."
                ),
                "dataset": "comparisons",
                "sourceId": "comparison-source",
                "type": "bar",
                "encodings": {
                    "x": {"field": "evaluation", "type": "nominal"},
                    "y": {
                        "field": "information_gain_bits_per_key",
                        "type": "quantitative",
                    },
                },
                "options": {
                    "orientation": "vertical",
                    "grouping": "single",
                    "legend": False,
                    "valueLabels": True,
                    "baseline": 0,
                },
            }
        ],
        "tables": [
            {
                "id": "blind-table",
                "title": "Метрики двух blind-половин",
                "description": "500k ключей на строку; один неизменяемый ансамбль.",
                "dataset": "blind_metrics",
                "sourceId": "blind-source",
                "columns": [
                    {"field": "half", "label": "Half", "type": "text"},
                    {"field": "records", "label": "Keys", "type": "number"},
                    {
                        "field": "information_gain_bits_per_key",
                        "label": "Info bits/key",
                        "type": "number",
                    },
                    {
                        "field": "info_ci_low",
                        "label": "Info CI low",
                        "type": "number",
                    },
                    {
                        "field": "bit_accuracy_lift",
                        "label": "Bit lift",
                        "type": "number",
                    },
                    {
                        "field": "clustered_accuracy_z",
                        "label": "Clustered z",
                        "type": "number",
                    },
                    {
                        "field": "mean_hamming_distance",
                        "label": "Mean Hamming",
                        "type": "number",
                    },
                    {
                        "field": "exact_key_matches",
                        "label": "Exact keys",
                        "type": "number",
                    },
                    {
                        "field": "threshold_crossed",
                        "label": "Passed",
                        "type": "boolean",
                    },
                ],
                "defaultSort": {"field": "half", "direction": "asc"},
            },
            {
                "id": "representation-table",
                "title": "Покрытие представлений открытого ключа",
                "description": "264 физических, 257 информативных и 512 affine битов.",
                "dataset": "representations",
                "sourceId": "representation-source",
                "columns": [
                    {
                        "field": "representation",
                        "label": "Representation",
                        "type": "text",
                    },
                    {
                        "field": "architectures",
                        "label": "Architectures",
                        "type": "number",
                    },
                    {
                        "field": "physical_input_columns",
                        "label": "Input columns",
                        "type": "number",
                    },
                    {
                        "field": "independent_public_bits",
                        "label": "Independent bits",
                        "type": "number",
                    },
                    {
                        "field": "best_family",
                        "label": "Best family",
                        "type": "text",
                    },
                    {
                        "field": "best_median_information_bits_per_key",
                        "label": "Best median info",
                        "type": "number",
                    },
                ],
                "defaultSort": {
                    "field": "physical_input_columns",
                    "direction": "desc",
                },
            },
            {
                "id": "stage-table",
                "title": "Полнота AutoML-журнала",
                "description": "301 попытка, включая controls и пять ensemble members.",
                "dataset": "stages",
                "sourceId": "stage-source",
                "columns": [
                    {"field": "stage", "label": "Stage", "type": "text"},
                    {"field": "attempts", "label": "Attempts", "type": "number"},
                    {
                        "field": "successful",
                        "label": "Successful",
                        "type": "number",
                    },
                    {"field": "failed", "label": "Failed", "type": "number"},
                ],
                "defaultSort": {"field": "attempts", "direction": "desc"},
            },
            {
                "id": "control-table",
                "title": "Отрицательные и leak-контроли",
                "description": "Leak-1 оценивается по намеренно раскрытой голове.",
                "dataset": "controls",
                "sourceId": "control-source",
                "columns": [
                    {"field": "control", "label": "Control", "type": "text"},
                    {"field": "attempts", "label": "Attempts", "type": "number"},
                    {"field": "criterion", "label": "Criterion", "type": "text"},
                    {"field": "observed", "label": "Observed", "type": "text"},
                    {"field": "passed", "label": "Passed", "type": "boolean"},
                ],
                "defaultSort": {"field": "attempts", "direction": "desc"},
            },
            {
                "id": "scaling-table",
                "title": "MLP: данные, эпохи и held-out gain",
                "description": (
                    "Одна архитектура arch-039; размер и эпохи меняются вместе, "
                    "поэтому строки не являются чистым causal ablation."
                ),
                "dataset": "mlp_scaling",
                "sourceId": "scaling-source",
                "columns": [
                    {"field": "stage", "label": "Stage", "type": "text"},
                    {"field": "direction", "label": "Direction", "type": "text"},
                    {
                        "field": "train_records",
                        "label": "Train keys",
                        "type": "number",
                    },
                    {"field": "epochs", "label": "Epochs", "type": "number"},
                    {"field": "seeds", "label": "Seeds", "type": "number"},
                    {
                        "field": "median_information_bits_per_key",
                        "label": "Median info",
                        "type": "number",
                    },
                    {
                        "field": "median_bit_accuracy_lift",
                        "label": "Median lift",
                        "type": "number",
                    },
                ],
                "defaultSort": {"field": "train_records", "direction": "asc"},
            },
        ],
        "blocks": [
            {
                "id": "title",
                "type": "markdown",
                "body": "# ML-инверсия secp256k1: полный 256-битный тест",
            },
            {
                "id": "technical-summary",
                "type": "markdown",
                "body": (
                    "## Технический итог\n\n"
                    "**Проверенный прямой путь `Q → 256 бит d` не дал сигнала.** "
                    "Все 301 AutoML fit завершились, controls сработали, а один "
                    "frozen ensemble затем провалил заранее заданные пороги на "
                    "обеих независимых половинах нового миллиона. На blind_a и "
                    "blind_b информационный выигрыш был отрицательным, средняя "
                    "Hamming-дистанция осталась около 128, точных ключей не было.\n\n"
                    "Это ограниченный null для проверенных моделей, представлений "
                    "и CPU-бюджета. Он не доказывает невозможность ML-алгоритма и "
                    "не является доказательством сложности ECDLP."
                ),
            },
            {
                "id": "headline-strip",
                "type": "metric-strip",
                "cardIds": ["attempts-card", "pairs-card", "exact-card"],
            },
            {
                "id": "gain-finding",
                "type": "markdown",
                "body": (
                    "## Gain оставался ниже baseline на каждом строгом этапе\n\n"
                    "Информационный выигрыш измеряет улучшение factorized "
                    "256-битного log-loss относительно prior-only модели. Ноль "
                    "означает равенство baseline; положительное значение было бы "
                    "кандидатом на структуру. Все показанные значения ниже нуля. "
                    "Небольшие положительные accuracy-lift отдельных запусков не "
                    "сопровождались положительным log-loss и не повторились с "
                    "заданной силой на blind."
                ),
            },
            {"id": "gain-chart-block", "type": "chart", "chartId": "gain-chart"},
            {
                "id": "blind-finding",
                "type": "markdown",
                "body": (
                    "## Новый миллион подтвердил bounded null\n\n"
                    "Один и тот же probability-averaging ensemble оценивался "
                    "неизменным на двух половинах по 500k ключей. Для принятия "
                    "сигнала каждая половина должна была одновременно дать "
                    "≥0.01 bits/key, lift ≥0.001, clustered z ≥5 и положительные "
                    "нижние границы двух 95% интервалов. Ни одна половина не "
                    "прошла ни общий gain, ни полный gate."
                ),
            },
            {"id": "blind-table-block", "type": "table", "tableId": "blind-table"},
            {
                "id": "input-definition",
                "type": "markdown",
                "body": (
                    "## Почему вход бывает 264, 257 и 512 бит\n\n"
                    "SEC 1 compressed key занимает 33 байта, то есть 264 "
                    "физических бита. Однако в префиксе `02/03` семь битов "
                    "постоянны и только один кодирует чётность y, поэтому "
                    "информативное представление содержит 256 бит x + 1 parity. "
                    "Affine `x||y` содержит 512 координатных битов, но y "
                    "однозначно восстанавливается из x и parity на secp256k1. "
                    "Все три формы были включены; 512 бит не добавляют независимой "
                    "информации."
                ),
            },
            {
                "id": "representation-table-block",
                "type": "table",
                "tableId": "representation-table",
            },
            {
                "id": "search-design",
                "type": "markdown",
                "body": (
                    "## AutoML проверил ширину, глубину, эпохи и четыре семейства\n\n"
                    "Screen содержал 80 архитектур × 3 seed. Successive halving "
                    "оставил 12 confirm-рецептов, затем четыре cross-dataset "
                    "кандидата и один пятиseedовый ансамбль. Проверены MLP глубиной "
                    "0–3 скрытых слоя и шириной до 256, ridge, bounded ExtraTrees "
                    "и random Fourier heads, разные learning rates, batch sizes, "
                    "regularization и 1–16 эпох. Все попытки и warnings записаны "
                    "в JSONL."
                ),
            },
            {"id": "stage-table-block", "type": "table", "tableId": "stage-table"},
            {
                "id": "control-finding",
                "type": "markdown",
                "body": (
                    "## Controls обнаружили намеренную утечку и отвергли null-labels\n\n"
                    "Шесть random/permuted-label запусков не пересекли gate. "
                    "Намеренно добавленные 1, 8 и 32 целевых бита были найдены: "
                    "для одного бита оценивается именно раскрытая output-head, "
                    "поскольку ошибки остальных 255 голов могут оставить общий "
                    "bits/key отрицательным. Это подтверждает чувствительность "
                    "пайплайна к доступному предиктивному сигналу."
                ),
            },
            {
                "id": "control-table-block",
                "type": "table",
                "tableId": "control-table",
            },
            {
                "id": "scaling-finding",
                "type": "markdown",
                "body": (
                    "## Дополнительные эпохи снижали train loss, но не создавали обобщение\n\n"
                    "У лучшего MLP-представителя переход от 100k/2 эпох к "
                    "600k/5 эпох приблизил held-out gain к нулю. На 800k/10 "
                    "эпохах train loss продолжил снижаться, но cross-dataset gain "
                    "ухудшился до примерно -0.010…-0.012 bits/key. Это профиль "
                    "запоминания/калибровки, а не приближения к алгоритму. Размер "
                    "и число эпох менялись совместно, поэтому это диагностическая "
                    "learning curve, не чистая оценка causal effect эпох."
                ),
            },
            {
                "id": "scaling-table-block",
                "type": "table",
                "tableId": "scaling-table",
            },
            {
                "id": "scope-method",
                "type": "markdown",
                "body": (
                    "## Область, метрики и валидация\n\n"
                    "Данные состоят только из синтетических `(d,Q=[d]G)`; wallet "
                    "keys не использовались. Два development seed дали 2M пар, "
                    "третий заранее committed seed дал 1M blind-пар. Все 3M "
                    "scalars уникальны; новый набор прошёл 2,048 независимых "
                    "арифметических spot-checks. Output представлен 256 "
                    "Bernoulli heads, а не одним float. Неопределённость считается "
                    "по целым ключам, не по 256 зависимым битам."
                ),
            },
            {
                "id": "limitations",
                "type": "markdown",
                "body": (
                    "## Что этот результат не устанавливает\n\n"
                    "Проверено около 2.59×10^-71 scalar space. Не проверены GPU "
                    "CNN/Transformer/residual architectures, авторегрессионные "
                    "nibble/byte heads, differentiable field/group operations и "
                    "toy-order scaling. Финальный ExtraTrees был заранее ограничен "
                    "100k train records ради памяти, хотя selection использовал "
                    "оба development-миллиона и MLP доходил до 800k/10 эпох. "
                    "Поэтому вывод относится только к записанному model/compute "
                    "budget."
                ),
            },
            {
                "id": "next-steps",
                "type": "markdown",
                "body": (
                    "## Следующий полезный эксперимент\n\n"
                    "1. Перенести тот же 256-head protocol на группы порядка "
                    "12, 16, 20, 24, 28 и 32 бит и построить scaling law.\n"
                    "2. Реализовать streaming GPU baseline с residual bit/limb "
                    "mixers и фиксированным полным data budget.\n"
                    "3. Продолжать secp256k1 direct inversion только если toy "
                    "ladder показывает воспроизводимый алгоритмический режим; "
                    "иначе направить ML на генерацию явных программ и проверку "
                    "гипотез.\n"
                    "4. Для любой новой адаптивной версии заранее commit новый "
                    "blind seed; текущий blind больше нельзя считать нетронутым."
                ),
            },
            {
                "id": "further-questions",
                "type": "markdown",
                "body": (
                    "## Открытые вопросы\n\n"
                    "- Возникает ли signal на малых группах и как он масштабируется "
                    "с bit length?\n"
                    "- Сохраняется ли он при смене генератора и opaque coordinate "
                    "relabeling?\n"
                    "- Можно ли извлечь короткую field/group program, а не только "
                    "weight matrix?\n"
                    "- Улучшает ли GPU-модель cross-entropy, а не только train loss?"
                ),
            },
        ],
    }
    snapshot = {
        "version": 1,
        "status": "ready",
        "generatedAt": generated_at,
        "datasets": {
            "headline": headline_rows,
            "comparisons": comparisons,
            "blind_metrics": blind_rows,
            "representations": representations,
            "stages": stage_rows,
            "controls": control_rows,
            "mlp_scaling": scaling,
        },
    }
    return {
        "surface": "report",
        "manifest": manifest,
        "snapshot": snapshot,
        "sources": sources,
        "package_info": {
            "snapshot_label": "Full-key AutoML and blind results",
            "snapshot_generated_at": generated_at,
            "live_connection": False,
        },
    }


def markdown_report(
    summary: dict[str, Any],
    search: dict[str, Any],
    blind: dict[str, Any],
    comparisons: list[dict[str, Any]],
    representations: list[dict[str, Any]],
    scaling: list[dict[str, Any]],
) -> str:
    development = search["development_ensemble_metrics"]
    blind_a = blind["blind_evaluations"]["blind_a"]["metrics"]
    blind_b = blind["blind_evaluations"]["blind_b"]["metrics"]
    controls = summary["controls"]
    lines = [
        "# ML-инверсия secp256k1: полный 256-битный тест",
        "",
        "## Технический итог",
        "",
        (
            "**Проверенный прямой путь `Q → 256 бит d` не дал сигнала.** "
            "Все 301 AutoML fit завершились, controls прошли, а один frozen "
            "ensemble провалил gate на обеих независимых половинах нового "
            "миллиона."
        ),
        "",
        "| Результат | Development | blind_a | blind_b |",
        "|---|---:|---:|---:|",
        (
            f"| Information gain, bits/key | "
            f"{development['information_gain_bits_per_key']:.9g} | "
            f"{blind_a['information_gain_bits_per_key']:.9g} | "
            f"{blind_b['information_gain_bits_per_key']:.9g} |"
        ),
        (
            f"| Bit accuracy lift | {development['bit_accuracy_lift']:.9g} | "
            f"{blind_a['bit_accuracy_lift']:.9g} | "
            f"{blind_b['bit_accuracy_lift']:.9g} |"
        ),
        (
            f"| Clustered accuracy z | {development['paired_accuracy_z']:.6g} | "
            f"{blind_a['paired_accuracy_z']:.6g} | "
            f"{blind_b['paired_accuracy_z']:.6g} |"
        ),
        (
            f"| Mean Hamming | {development['mean_hamming_distance']:.6g} | "
            f"{blind_a['mean_hamming_distance']:.6g} | "
            f"{blind_b['mean_hamming_distance']:.6g} |"
        ),
        (
            f"| Exact 256-bit keys | {development['exact_key_matches']} | "
            f"{blind_a['exact_key_matches']} | {blind_b['exact_key_matches']} |"
        ),
        "",
        (
            "Это bounded null для записанных данных, моделей и CPU-бюджета. "
            "Он не доказывает невозможность ML и не доказывает сложность ECDLP."
        ),
        "",
        "## Почему 264, 257 и 512",
        "",
        (
            "Compressed SEC 1 key содержит 264 физических бита, но семь битов "
            "префикса постоянны. Информативны 256 бит x и один бит чётности y. "
            "Affine x||y содержит 512 бит, однако y восстанавливается из x и "
            "parity, поэтому независимой информации не добавляет."
        ),
        "",
        "| Представление | Архитектур | Входных колонок | Лучший median bits/key |",
        "|---|---:|---:|---:|",
    ]
    for row in sorted(
        representations,
        key=lambda item: item["best_median_information_bits_per_key"],
        reverse=True,
    ):
        lines.append(
            f"| `{row['representation']}` | {row['architectures']} | "
            f"{row['physical_input_columns']} | "
            f"{row['best_median_information_bits_per_key']:.8g} |"
        )
    lines.extend(
        [
            "",
            "## AutoML и controls",
            "",
            (
                f"Журнал содержит {summary['search']['attempted']} попытку, "
                f"{summary['search']['succeeded']} успешных и "
                f"{summary['search']['failed']} ошибок. Проверены MLP, ridge, "
                "bounded ExtraTrees и random Fourier heads, 1–16 эпох, глубина "
                "MLP 0–3, ширина до 256 и девять представлений."
            ),
            "",
            (
                f"Negative controls прошли: максимальный null gain "
                f"{controls['max_null_information_bits_per_key']:.6g}, "
                f"максимальный z {controls['max_null_accuracy_z']:.4g}. "
                "Leak controls 1/8/32 бит также прошли. Для leak-1 используется "
                "метрика намеренно раскрытой output-head, а не сумма по 256 "
                "головам."
            ),
            "",
            "## Эпохи и размер данных",
            "",
            "| Этап | Direction | Train | Epochs | Median info bits/key |",
            "|---|---|---:|---:|---:|",
        ]
    )
    for row in scaling:
        lines.append(
            f"| {row['stage']} | {row['direction']} | "
            f"{row['train_records']:,} | {row['epochs']} | "
            f"{row['median_information_bits_per_key']:.8g} |"
        )
    lines.extend(
        [
            "",
            (
                "У arch-039 увеличение до 600k/5 эпох приблизило gain к нулю, "
                "но 800k/10 эпох ухудшило cross-dataset gain, хотя train loss "
                "продолжал падать. Это согласуется с запоминанием/калибровкой, "
                "не с обнаружением алгоритма. Размер и эпохи менялись вместе, "
                "поэтому это не чистая causal ablation."
            ),
            "",
            "## Ограничения",
            "",
            (
                "Три миллиона уникальных пар покрывают около 2.59×10^-71 "
                "scalar space. Не проверены GPU CNN/Transformer/residual модели, "
                "авторегрессионные heads и differentiable group operations. "
                "Финальный ExtraTrees имел заранее заданный cap 100k, хотя MLP "
                "доходил до 800k/10 эпох и selection использовал оба development "
                "миллиона."
            ),
            "",
            "## Рекомендованный следующий шаг",
            "",
            (
                "Наиболее информативен toy-order scaling ladder 12–32 бит с тем "
                "же 256-head protocol, сменой генераторов и opaque coordinate "
                "relabeling. Если там нет масштабируемого режима, дальнейшее "
                "увеличение secp256k1 regressor следует остановить и использовать "
                "ML для предложения явных field/group программ и проверяемых "
                "гипотез."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def build(args: argparse.Namespace) -> dict[str, Any]:
    search = load_json(args.search_result)
    blind = load_json(args.blind_result)
    validation = load_json(args.blind_validation)
    blind_manifest = load_json(args.blind_manifest)
    search_ledger = load_jsonl(args.search_ledger)
    blind_ledger = load_jsonl(args.blind_ledger)

    if search["run_summary"]["attempted"] != 301:
        raise ValueError("search does not contain 301 attempts")
    if len(search_ledger) != 301:
        raise ValueError("search ledger is incomplete")
    if sha256_file(args.search_ledger) != search["ledger_sha256"]:
        raise ValueError("search ledger hash mismatch")
    if len(blind_ledger) != 8:
        raise ValueError("blind ledger must contain 5 fit, 2 evaluation and 1 decision")
    if validation["status"] != "pass" or validation["records_observed"] != 1_000_000:
        raise ValueError("blind dataset validation did not pass")
    if blind["datasets"]["blind"]["dataset_root_sha256"] != blind_manifest[
        "dataset_root_sha256"
    ]:
        raise ValueError("blind result and manifest root hashes differ")

    controls = control_summary(search_ledger)
    representations = representation_rows(search)
    scaling = mlp_scaling_rows(search_ledger)
    comparisons = comparison_rows(search, search_ledger, blind)
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    generated_at = generated_at.replace("+00:00", "Z")
    scalar_space_fraction = 3_000_000 / (
        int(
            "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141",
            16,
        )
        - 1
    )
    summary = {
        "schema_version": 1,
        "generated_at": generated_at,
        "status": "pass" if controls["pass"] else "fail",
        "scientific_evidence": False,
        "search": search["run_summary"],
        "controls": controls,
        "development": {
            "signal_threshold_crossed": search[
                "development_signal_threshold_crossed"
            ],
            "metrics": search["development_ensemble_metrics"],
        },
        "blind": {
            "crossed_both_halves": blind["decision"][
                "crossed_both_blind_halves"
            ],
            "exact_key_matches_total": sum(
                blind["blind_evaluations"][split]["metrics"]["exact_key_matches"]
                for split in ("blind_a", "blind_b")
            ),
            "metrics": {
                split: blind["blind_evaluations"][split]["metrics"]
                for split in ("blind_a", "blind_b")
            },
        },
        "datasets": {
            "total_unique_pairs": 3_000_000,
            "development_pairs": 2_000_000,
            "blind_pairs": 1_000_000,
            "scalar_space_fraction": scalar_space_fraction,
            "blind_dataset_root_sha256": blind_manifest["dataset_root_sha256"],
            "blind_validation_status": validation["status"],
        },
        "conclusion": (
            "No full-key representation signal met the frozen gate. Both blind "
            "halves are bounded nulls for the tested model and compute budget."
        ),
        "artifact_hashes": {
            "search_result.json": sha256_file(args.search_result),
            "search_ledger.jsonl": sha256_file(args.search_ledger),
            "blind_result.json": sha256_file(args.blind_result),
            "blind_ledger.jsonl": sha256_file(args.blind_ledger),
            "blind_validation.json": sha256_file(args.blind_validation),
            "blind_dataset_manifest.json": sha256_file(args.blind_manifest),
        },
    }
    if not controls["pass"]:
        raise RuntimeError("full-key control qualification failed")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "qualification_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "technical_report.md").write_text(
        markdown_report(
            summary,
            search,
            blind,
            comparisons,
            representations,
            scaling,
        ),
        encoding="utf-8",
    )
    artifact = build_artifact(
        summary,
        search,
        blind,
        comparisons,
        representations,
        scaling,
    )
    (args.output_dir / "artifact.json").write_text(
        json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "blind_dataset_manifest.json").write_text(
        json.dumps(blind_manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    report_plan = {
        "audience": "technical",
        "delivery_mode": "sites-app",
        "question": (
            "Can full-length secp256k1 public keys predict all 256 private-key bits "
            "under the recorded AutoML and data budgets?"
        ),
        "decision_useful_answer": summary["conclusion"],
        "required_structure_mapping": {
            "technical_summary": "Технический итог",
            "key_findings_with_visual_evidence": [
                "Gain оставался ниже baseline на каждом строгом этапе",
                "Новый миллион подтвердил bounded null",
            ],
            "scope_data_metric_definitions": [
                "Почему вход бывает 264, 257 и 512 бит",
                "Область, метрики и валидация",
            ],
            "methodology": [
                "AutoML проверил ширину, глубину, эпохи и четыре семейства",
                "Controls обнаружили намеренную утечку и отвергли null-labels",
            ],
            "limitations_uncertainty_robustness": [
                "Дополнительные эпохи снижали train loss, но не создавали обобщение",
                "Что этот результат не устанавливает",
            ],
            "recommended_next_steps": "Следующий полезный эксперимент",
            "further_questions": "Открытые вопросы",
        },
        "chart_map": [
            {
                "section": "Gain оставался ниже baseline на каждом строгом этапе",
                "question": "Did information gain cross the zero baseline at any evaluation stage?",
                "family": "comparison",
                "type": "bar",
                "x": "evaluation",
                "y": "information_gain_bits_per_key",
                "takeaway": "Every recorded stage remained below zero.",
                "palette_policy": "single-root preferred with a neutral zero reference",
            }
        ],
        "omissions": [
            (
                "Confidence intervals are kept in the exact blind table because "
                "the native bar chart does not expose interval marks."
            )
        ],
    }
    (args.output_dir / "report_plan.json").write_text(
        json.dumps(report_plan, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--search-result", required=True, type=Path)
    parser.add_argument("--search-ledger", required=True, type=Path)
    parser.add_argument("--blind-result", required=True, type=Path)
    parser.add_argument("--blind-ledger", required=True, type=Path)
    parser.add_argument("--blind-validation", required=True, type=Path)
    parser.add_argument("--blind-manifest", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    summary = build(parse_args())
    print(
        json.dumps(
            {
                "status": summary["status"],
                "controls_pass": summary["controls"]["pass"],
                "blind_crossed": summary["blind"]["crossed_both_halves"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
