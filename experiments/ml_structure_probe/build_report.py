#!/usr/bin/env python3
"""Build a compact qualification report from retained P0 result artifacts."""
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


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build(
    manifest_path: Path,
    validation_path: Path,
    probe_path: Path,
    automl_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    manifest = load(manifest_path)
    validation = load(validation_path)
    probe = load(probe_path)
    automl = load(automl_path)
    ledger_path = automl_path.with_name("run_ledger.jsonl")
    ledger = [
        json.loads(line)
        for line in ledger_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    manifest_sha256 = sha256_file(manifest_path)
    errors: list[str] = []
    if validation.get("manifest_sha256") != manifest_sha256:
        errors.append("validation does not bind the supplied manifest")
    if probe.get("manifest_sha256") != manifest_sha256:
        errors.append("linear probe does not bind the supplied manifest")
    if automl.get("dataset", {}).get("manifest_sha256") != manifest_sha256:
        errors.append("AutoML result does not bind the supplied manifest")
    if validation.get("status") != "pass":
        errors.append("dataset validation did not pass")
    if probe.get("pipeline_status") != "pass":
        errors.append("linear probe pipeline did not pass")
    if automl.get("pipeline_status") != "pass":
        errors.append("AutoML pipeline did not pass")
    expected_run_ids = {
        item["run_id"] for item in automl["runs"]
    } | {
        item["run_id"] for item in automl["finalists"].values()
    } | {
        item["run_id"] for item in automl["controls"]["tasks"].values()
    }
    ledger_run_ids = [item["run_id"] for item in ledger]
    if len(ledger_run_ids) != len(set(ledger_run_ids)):
        errors.append("AutoML ledger contains duplicate run ids")
    if set(ledger_run_ids) != expected_run_ids:
        missing = sorted(expected_run_ids - set(ledger_run_ids))
        extra = sorted(set(ledger_run_ids) - expected_run_ids)
        errors.append(f"AutoML ledger mismatch: missing={missing}, extra={extra}")
    if errors:
        raise ValueError("; ".join(errors))

    baseline = {
        task: {
            "validation": item["validation"],
            "test": item["test"],
            "threshold_crossed_both_splits": item[
                "threshold_crossed_both_splits"
            ],
        }
        for task, item in probe["tasks"].items()
    }
    result = {
        "schema_version": 1,
        "experiment_id": automl["experiment_id"],
        "result_role": "retained_ml_structure_probe_qualification",
        "scientific_evidence": False,
        "route_promotion_authorized": False,
        "status": "pass",
        "dataset": {
            "records": manifest["total_records"],
            "bytes": manifest["total_bytes"],
            "root_sha256": manifest["dataset_root_sha256"],
            "manifest_sha256": manifest_sha256,
            "source_state": manifest["source_state"],
            "generation": manifest["generation"],
            "splits": manifest["splits"],
        },
        "validation": {
            "unique_scalars": validation["unique_scalars"],
            "spot_checks": validation["spot_checks"],
            "distribution_checks": validation["distribution_checks"],
            "errors": validation["errors"],
        },
        "linear_probe": {
            "model": probe["model"],
            "canaries_pass": probe["canaries_pass"],
            "permuted_null_pass": probe["permuted_null_pass"],
            "signals": probe["representation_signals_requiring_new_candidate"],
            "tasks": baseline,
        },
        "automl": {
            "source_state": automl["source_state"],
            "selection_protocol": automl["selection_protocol"],
            "run_summary": automl["run_summary"],
            "method_coverage": automl["method_coverage"],
            "controls": {
                "canaries_pass": automl["controls"]["canaries_pass"],
                "permuted_null_pass": automl["controls"]["permuted_null_pass"],
            },
            "finalists": automl["finalists"],
            "signals": automl[
                "representation_signals_requiring_replication"
            ],
            "interpretation": automl["interpretation"],
        },
        "artifact_hashes": {
            "dataset_manifest.json": manifest_sha256,
            "dataset_validation.json": sha256_file(validation_path),
            "linear_probe_result.json": sha256_file(probe_path),
            "automl_result.json": sha256_file(automl_path),
            "run_ledger.jsonl": sha256_file(ledger_path),
        },
        "scope": automl["scope"],
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    for source, retained_name in (
        (manifest_path, "dataset_manifest.json"),
        (validation_path, "dataset_validation.json"),
        (probe_path, "linear_probe_result.json"),
    ):
        (output_dir / retained_name).write_bytes(source.read_bytes())
    (output_dir / "qualification_summary.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output_dir / "qualification_report.md").write_text(
        render_markdown(result), encoding="utf-8"
    )
    return result


def render_markdown(result: dict[str, Any]) -> str:
    dataset = result["dataset"]
    validation = result["validation"]
    automl = result["automl"]
    lines = [
        f"# {result['experiment_id']} retained qualification",
        "",
        "## Result",
        "",
        "- Status: `pass`",
        f"- Records: `{dataset['records']:,}`",
        f"- Dataset root SHA-256: `{dataset['root_sha256']}`",
        f"- Clean source commit: `{dataset['source_state']['commit']}`",
        f"- Generation: `{dataset['generation']['records_per_second']:,.1f}` "
        f"records/s in `{dataset['generation']['elapsed_seconds']:.3f}` s",
        f"- Unique scalars: `{validation['unique_scalars']:,}`",
        f"- Independent arithmetic spots: "
        f"`{validation['spot_checks']['requested_and_found']:,}`",
        f"- AutoML attempts: `{automl['run_summary']['completed']}` completed, "
        f"`{automl['run_summary']['failed']}` failed",
        f"- Linear signals: "
        f"`{', '.join(result['linear_probe']['signals']) or 'none'}`",
        f"- AutoML signals: `{', '.join(automl['signals']) or 'none'}`",
        "",
        "## Data checks",
        "",
        "| check | observed | threshold |",
        "|---|---:|---:|",
    ]
    distributions = validation["distribution_checks"]
    for label, key in (
        ("scalar bits max |z|", "scalar_bits"),
        ("public x bits max |z|", "public_x_bits"),
        ("public y parity |z|", "public_y_parity"),
    ):
        item = distributions[key]
        lines.append(
            f"| {label} | {item['max_abs_z']:.6g} | {item['threshold']} |"
        )
    lines.extend(
        [
            "",
            "## Linear baseline",
            "",
            "| task | validation info gain | test info gain | test lift | test z | signal |",
            "|---|---:|---:|---:|---:|---|",
        ]
    )
    for task, item in result["linear_probe"]["tasks"].items():
        lines.append(
            f"| {task} | "
            f"{item['validation']['information_gain_bits_per_record']:.6g} | "
            f"{item['test']['information_gain_bits_per_record']:.6g} | "
            f"{item['test']['accuracy_lift']:.6g} | "
            f"{item['test']['accuracy_z']:.4f} | "
            f"{item['threshold_crossed_both_splits']} |"
        )
    lines.extend(
        [
            "",
            "## AutoML finalists",
            "",
            "| task | recipe | train records | validation info gain | test info gain | test lift | test z | signal |",
            "|---|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for task, item in automl["finalists"].items():
        lines.append(
            f"| {task} | {item['recipe_id']} | {item['train_records']:,} | "
            f"{item['validation']['information_gain_bits_per_record']:.6g} | "
            f"{item['test']['information_gain_bits_per_record']:.6g} | "
            f"{item['test']['accuracy_lift']:.6g} | "
            f"{item['test']['accuracy_z']:.4f} | "
            f"{item['threshold_crossed_both_splits']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            automl["interpretation"],
            "",
            "This is an engineering qualification and a bounded representation "
            "assay. It is not evidence of a secp256k1 discrete-log shortcut, and "
            "it does not establish unlearnability outside the recorded tasks, "
            "representations, methods, and budgets.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--validation", type=Path, required=True)
    parser.add_argument("--probe", type=Path, required=True)
    parser.add_argument("--automl", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = build(
        args.manifest.resolve(),
        args.validation.resolve(),
        args.probe.resolve(),
        args.automl.resolve(),
        args.output_dir.resolve(),
    )
    print(
        json.dumps(
            {
                "status": result["status"],
                "records": result["dataset"]["records"],
                "automl_attempts": result["automl"]["run_summary"]["completed"],
                "signals": result["automl"]["signals"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
