#!/usr/bin/env python3
"""Compare a selected AutoML assay with a fresh-seed frozen replication."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compare(
    primary_path: Path,
    replica_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    primary = json.loads(primary_path.read_text(encoding="utf-8"))
    replica = json.loads(replica_path.read_text(encoding="utf-8"))
    if primary["dataset"]["dataset_root_sha256"] == replica["dataset"][
        "dataset_root_sha256"
    ]:
        raise ValueError("replication must use a different dataset root")
    tasks = sorted(primary["finalists"])
    if tasks != sorted(replica["finalists"]):
        raise ValueError("primary and replica task sets differ")
    comparisons: dict[str, Any] = {}
    for task in tasks:
        first = primary["finalists"][task]
        second = replica["finalists"][task]
        if first["recipe_id"] != second["recipe_id"]:
            raise ValueError(f"replica recipe drift for {task}")
        comparisons[task] = {
            "recipe_id": first["recipe_id"],
            "primary": {
                "validation": first["validation"],
                "test": first["test"],
                "threshold_crossed_both_splits": first[
                    "threshold_crossed_both_splits"
                ],
            },
            "replica": {
                "validation": second["validation"],
                "test": second["test"],
                "threshold_crossed_both_splits": second[
                    "threshold_crossed_both_splits"
                ],
            },
            "replicated_signal": (
                first["threshold_crossed_both_splits"]
                and second["threshold_crossed_both_splits"]
            ),
        }
    replicated_signals = [
        task for task, item in comparisons.items() if item["replicated_signal"]
    ]
    result = {
        "schema_version": 1,
        "result_role": "fresh_seed_frozen_model_replication",
        "scientific_evidence": False,
        "route_promotion_authorized": False,
        "status": "pass",
        "primary": {
            "experiment_id": primary["experiment_id"],
            "result_sha256": sha256_file(primary_path),
            "dataset_root_sha256": primary["dataset"]["dataset_root_sha256"],
            "source_state": primary["source_state"],
        },
        "replica": {
            "experiment_id": replica["experiment_id"],
            "result_sha256": sha256_file(replica_path),
            "dataset_root_sha256": replica["dataset"]["dataset_root_sha256"],
            "source_state": replica["source_state"],
        },
        "comparisons": comparisons,
        "replicated_signals": replicated_signals,
        "interpretation": (
            "At least one frozen model crossed the threshold in both complete "
            "assays; independent implementation and mechanism extraction are required."
            if replicated_signals
            else "No frozen model produced a threshold-crossing signal in both "
            "fresh-seed assays. This is a replicated bounded null for the recorded "
            "models, representations, tasks, curve, and budgets."
        ),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "replication_summary.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output_dir / "replication_report.md").write_text(
        render_markdown(result), encoding="utf-8"
    )
    return result


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# P0 fresh-seed frozen-model replication",
        "",
        f"- Primary dataset: `{result['primary']['dataset_root_sha256']}`",
        f"- Replica dataset: `{result['replica']['dataset_root_sha256']}`",
        f"- Replicated signals: "
        f"`{', '.join(result['replicated_signals']) or 'none'}`",
        "",
        "| task | frozen recipe | primary test info gain | primary test z | "
        "replica test info gain | replica test z | replicated signal |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for task, item in result["comparisons"].items():
        first = item["primary"]["test"]
        second = item["replica"]["test"]
        lines.append(
            f"| {task} | {item['recipe_id']} | "
            f"{first['information_gain_bits_per_record']:.6g} | "
            f"{first['accuracy_z']:.4f} | "
            f"{second['information_gain_bits_per_record']:.6g} | "
            f"{second['accuracy_z']:.4f} | "
            f"{item['replicated_signal']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            result["interpretation"],
            "",
            "The model recipes were selected on the primary validation split and "
            "frozen before the second synthetic seed was generated. Both runs use "
            "separate train, validation, and test derivation domains. This does not "
            "support any inference beyond the explicitly recorded scope.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--primary", type=Path, required=True)
    parser.add_argument("--replica", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = compare(
        args.primary.resolve(),
        args.replica.resolve(),
        args.output_dir.resolve(),
    )
    print(
        json.dumps(
            {
                "status": result["status"],
                "replicated_signals": result["replicated_signals"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
