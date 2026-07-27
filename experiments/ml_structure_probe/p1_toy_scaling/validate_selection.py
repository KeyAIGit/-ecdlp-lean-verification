#!/usr/bin/env python3
"""Independent pre-blind validation of the P1E selection freeze.

This validator imports only the independent helpers in ``validate_results``.
It never imports the selection producer or its representation implementation.
The report is intended to be generated from a clean commit containing the
selection ledger, selection result, and frozen recipe, then committed before
any blind evaluation starts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from validate_results import (
    ROOT,
    RUNNER_RELATIVE_PATH,
    SOURCE_DEPENDENCY_RELATIVE_PATHS,
    Findings,
    git_blob,
    git_commit_exists,
    is_ancestor,
    load_json,
    load_ledger,
    payload_hash,
    require_committed_file,
    sha256_file,
    validate_input_validation_reports,
    validate_selection,
)


VALIDATOR_RELATIVE_PATH = (
    "experiments/ml_structure_probe/p1_toy_scaling/validate_selection.py"
)
RESULT_VALIDATOR_RELATIVE_PATH = (
    "experiments/ml_structure_probe/p1_toy_scaling/validate_results.py"
)
CURVE_VALIDATOR_RELATIVE_PATH = (
    "experiments/ml_structure_probe/p1_toy_scaling/validate_curves.py"
)
DATASET_VALIDATOR_RELATIVE_PATH = (
    "experiments/ml_structure_probe/p1_toy_scaling/validate_dataset.py"
)
ORACLE_RELATIVE_PATH = "experiments/framework/ec_oracle.py"
EXPECTED_FIELD_BITS = [13, 16, 20, 24]
EXPECTED_DEFERRED_BITS = [28, 32]
EXPECTED_TRAINING_PROTOCOL = (
    "architecture frozen after 13/16 selection; retrained independently "
    "at each size; no cross-size weight transfer"
)
SHARED_SELECTION_FIELDS = (
    "source_commit",
    "source_worktree_dirty_before_run",
    "producer_sha256",
    "config_sha256",
    "preregistration_sha256",
    "catalog_sha256",
    "manifest_sha256",
    "curve_validation_sha256",
    "dataset_validation_sha256",
    "selection_ledger_sha256",
    "metric_baseline",
    "dataset_records",
    "source_dependency_sha256",
    "runtime_versions",
)


def git_text(*args: str) -> str | None:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else None


def file_hashes(
    paths: dict[str, Path], findings: Findings
) -> dict[str, str | None]:
    hashes: dict[str, str | None] = {}
    for label, path in paths.items():
        try:
            hashes[label] = sha256_file(path)
        except OSError as error:
            findings.error(f"{label}: cannot hash input: {error}")
            hashes[label] = None
    return hashes


def load_documents(
    paths: dict[str, Path], findings: Findings
) -> dict[str, dict[str, Any]]:
    documents: dict[str, dict[str, Any]] = {}
    for label, path in paths.items():
        try:
            documents[label] = load_json(path)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
            findings.error(f"{label}: cannot load JSON object: {error}")
            documents[label] = {}
    return documents


def validate_scope_and_bindings(
    documents: dict[str, dict[str, Any]],
    hashes: dict[str, str | None],
    findings: Findings,
) -> None:
    config = documents["config"]
    preregistration = documents["preregistration"]
    catalog = documents["catalog"]
    manifest = documents["manifest"]
    selection_result = documents["selection_result"]
    recipe = documents["recipe"]
    experiment_id = config.get("experiment_id")

    for label, document in documents.items():
        if document.get("experiment_id") != experiment_id:
            findings.error(f"{label}: experiment id mismatch")

    if preregistration.get("native_research_engine_run") is not False:
        findings.error("preregistration does not preserve non-native scope")
    if preregistration.get("native_outcome_prohibited") is not True:
        findings.error("preregistration does not prohibit native outcomes")
    if config.get("native_research_engine_outcome") is not False:
        findings.error("configuration claims a native Research Engine outcome")
    if catalog.get("native_research_engine_outcome") is not False:
        findings.error("catalog claims a native Research Engine outcome")
    if selection_result.get("native_research_engine_outcome") is not False:
        findings.error("selection result claims a native Research Engine outcome")

    configured_bits = config.get("field_bits")
    if configured_bits != EXPECTED_FIELD_BITS:
        findings.error("configured field ladder differs from 13/16/20/24")
    if preregistration.get("authorized_field_bits") != configured_bits:
        findings.error("preregistration/config field ladder mismatch")
    if config.get("deferred_field_bits") != EXPECTED_DEFERRED_BITS:
        findings.error("configuration does not keep 28/32 deferred")

    selection_policy = config.get("selection")
    if not isinstance(selection_policy, dict):
        findings.error("configuration selection policy is not an object")
        selection_policy = {}
    if (
        selection_policy.get("top_confirmation_recipes") != 1
        or selection_policy.get("confirmation_may_reselect_architecture")
        is not False
        or selection_policy.get(
            "architecture_identity_frozen_after_selection_sizes"
        )
        is not True
    ):
        findings.error("configuration architecture-freeze policy mismatch")

    config_sha = hashes["config"]
    catalog_sha = hashes["catalog"]
    if catalog.get("config_sha256") != config_sha:
        findings.error("catalog/config file hash mismatch")
    if catalog.get("catalog_sha256") != payload_hash(
        catalog, "catalog_sha256"
    ):
        findings.error("catalog payload hash mismatch")
    if manifest.get("config_sha256") != config_sha:
        findings.error("manifest/config file hash mismatch")
    if manifest.get("catalog_sha256") != catalog_sha:
        findings.error("manifest/catalog file hash mismatch")
    if manifest.get("catalog_payload_sha256") != catalog.get("catalog_sha256"):
        findings.error("manifest/catalog payload hash mismatch")
    if manifest.get("manifest_sha256") != payload_hash(
        manifest, "manifest_sha256"
    ):
        findings.error("manifest payload hash mismatch")

    expected_records = manifest.get("records")
    expected_baseline = selection_policy.get("baseline")
    for label, document in (
        ("selection result", selection_result),
        ("frozen recipe", recipe),
    ):
        if document.get("dataset_records") != expected_records:
            findings.error(f"{label}: dataset record count mismatch")
        if document.get("metric_baseline") != expected_baseline:
            findings.error(f"{label}: metric baseline mismatch")
    if recipe.get("training_protocol") != EXPECTED_TRAINING_PROTOCOL:
        findings.error("frozen recipe training protocol mismatch")


def validate_provenance(
    *,
    documents: dict[str, dict[str, Any]],
    paths: dict[str, Path],
    artifact_commit: str | None,
    worktree_dirty: bool,
    findings: Findings,
) -> dict[str, Any]:
    catalog = documents["catalog"]
    selection_result = documents["selection_result"]
    recipe = documents["recipe"]
    selection_commit = recipe.get("source_commit")
    catalog_commit = catalog.get("source_commit")

    for field in SHARED_SELECTION_FIELDS:
        if selection_result.get(field) != recipe.get(field):
            findings.error(
                f"selection result and frozen recipe differ on {field}"
            )
    if recipe.get("source_worktree_dirty_before_run") is not False:
        findings.error("selection recipe records a dirty starting worktree")
    if selection_result.get("source_worktree_dirty_before_run") is not False:
        findings.error("selection result records a dirty starting worktree")
    if worktree_dirty:
        findings.error("pre-blind validation started from a dirty worktree")

    selection_commit_exists = git_commit_exists(selection_commit)
    artifact_commit_exists = git_commit_exists(artifact_commit)
    catalog_commit_exists = git_commit_exists(catalog_commit)
    if not selection_commit_exists:
        findings.error("selection source commit does not resolve")
    if not artifact_commit_exists:
        findings.error("pre-blind validation HEAD does not resolve")
    if not catalog_commit_exists:
        findings.error("catalog source commit does not resolve")

    selection_is_ancestor = bool(
        selection_commit_exists
        and artifact_commit_exists
        and is_ancestor(selection_commit, artifact_commit)
    )
    if not selection_is_ancestor:
        findings.error(
            "selection source commit is not an ancestor of validation HEAD"
        )
    catalog_is_ancestor = bool(
        catalog_commit_exists
        and selection_commit_exists
        and is_ancestor(catalog_commit, selection_commit)
    )
    if not catalog_is_ancestor:
        findings.error(
            "catalog source commit is not an ancestor of selection source"
        )

    if selection_commit_exists:
        runner_blob = git_blob(
            str(selection_commit), ROOT / RUNNER_RELATIVE_PATH
        )
        if runner_blob is None:
            findings.error("run_assay.py is absent at selection source commit")
        elif hashlib.sha256(runner_blob).hexdigest() != recipe.get(
            "producer_sha256"
        ):
            findings.error(
                "recipe producer hash differs from selection source commit"
            )

        recorded_dependencies = recipe.get("source_dependency_sha256")
        if not isinstance(recorded_dependencies, dict):
            findings.error("recipe source dependency hashes are missing")
            recorded_dependencies = {}
        if set(recorded_dependencies) != set(
            SOURCE_DEPENDENCY_RELATIVE_PATHS
        ):
            findings.error("recipe source dependency hash set is unexpected")
        for name, relative in SOURCE_DEPENDENCY_RELATIVE_PATHS.items():
            for label, commit in (
                ("selection", selection_commit),
                ("validation", artifact_commit),
            ):
                if not git_commit_exists(commit):
                    continue
                blob = git_blob(str(commit), ROOT / relative)
                if blob is None:
                    findings.error(
                        f"{name} is absent at {label} source commit"
                    )
                elif hashlib.sha256(blob).hexdigest() != (
                    recorded_dependencies.get(name)
                ):
                    findings.error(
                        f"{name} differs from frozen dependency at "
                        f"{label} source commit"
                    )

        for path, label in (
            (paths["preregistration"], "preregistration"),
            (paths["config"], "configuration"),
            (paths["catalog"], "curve catalog"),
            (paths["manifest"], "dataset manifest"),
            (paths["curve_validation"], "curve validation"),
            (paths["dataset_validation"], "dataset validation"),
            (ROOT / CURVE_VALIDATOR_RELATIVE_PATH, "curve validator source"),
            (
                ROOT / DATASET_VALIDATOR_RELATIVE_PATH,
                "dataset validator source",
            ),
            (ROOT / ORACLE_RELATIVE_PATH, "framework EC oracle"),
            (ROOT / VALIDATOR_RELATIVE_PATH, "pre-blind validator source"),
            (
                ROOT / RESULT_VALIDATOR_RELATIVE_PATH,
                "result validator helper source",
            ),
        ):
            require_committed_file(
                findings, selection_commit, path, label
            )

    if artifact_commit_exists:
        for path, label in (
            (paths["selection_result"], "selection result"),
            (paths["selection_ledger"], "selection ledger"),
            (paths["recipe"], "frozen recipe"),
            (ROOT / VALIDATOR_RELATIVE_PATH, "pre-blind validator source"),
            (
                ROOT / RESULT_VALIDATOR_RELATIVE_PATH,
                "result validator helper source",
            ),
        ):
            require_committed_file(findings, artifact_commit, path, label)

    return {
        "selection_source_commit": selection_commit,
        "catalog_source_commit": catalog_commit,
        "validation_artifact_commit": artifact_commit,
        "selection_source_is_ancestor": selection_is_ancestor,
        "catalog_source_is_ancestor": catalog_is_ancestor,
        "worktree_clean_before_validation": not worktree_dirty,
    }


def stable_selection_summary(
    selection_validation: dict[str, Any],
    hashes: dict[str, str | None],
) -> dict[str, Any]:
    return {
        "selection_result_sha256": hashes["selection_result"],
        "selection_ledger_sha256": hashes["selection_ledger"],
        "recipe_sha256": hashes["recipe"],
        "run_counts": selection_validation.get("run_counts"),
        "blind_evaluation_authorized": selection_validation.get(
            "blind_evaluation_authorized", False
        ),
    }


def validate(
    *,
    config_path: Path,
    preregistration_path: Path,
    catalog_path: Path,
    manifest_path: Path,
    curve_validation_path: Path,
    dataset_validation_path: Path,
    selection_result_path: Path,
    selection_ledger_path: Path,
    recipe_path: Path,
) -> dict[str, Any]:
    started = time.perf_counter()
    findings = Findings(maximum_messages=100)
    artifact_commit = git_text("rev-parse", "HEAD")
    status_output = git_text("status", "--porcelain")
    worktree_dirty = status_output is None or bool(status_output)
    if status_output is None:
        findings.error("cannot determine pre-blind validation worktree state")

    paths = {
        "config": config_path,
        "preregistration": preregistration_path,
        "catalog": catalog_path,
        "manifest": manifest_path,
        "curve_validation": curve_validation_path,
        "dataset_validation": dataset_validation_path,
        "selection_result": selection_result_path,
        "selection_ledger": selection_ledger_path,
        "recipe": recipe_path,
    }
    hashes = file_hashes(paths, findings)
    json_paths = {
        key: value
        for key, value in paths.items()
        if key != "selection_ledger"
    }
    documents = load_documents(json_paths, findings)

    selection_entries: list[dict[str, Any]] = []
    try:
        selection_entries, _ = load_ledger(
            selection_ledger_path, findings, "selection ledger"
        )
    except OSError as error:
        findings.error(f"selection ledger: cannot read input: {error}")

    input_validation: dict[str, Any] = {}
    selection_validation: dict[str, Any] = {}
    provenance: dict[str, Any] = {}
    try:
        validate_scope_and_bindings(documents, hashes, findings)
    except (KeyError, TypeError, ValueError) as error:
        findings.error(
            f"scope and binding validation could not complete: {error}"
        )
    try:
        input_validation = validate_input_validation_reports(
            documents["config"],
            documents["preregistration"],
            documents["catalog"],
            documents["manifest"],
            documents["curve_validation"],
            documents["dataset_validation"],
            config_path,
            catalog_path,
            manifest_path,
            curve_validation_path,
            dataset_validation_path,
            findings,
        )
    except (KeyError, OSError, TypeError, ValueError) as error:
        findings.error(f"input validation replay could not complete: {error}")
    try:
        selection_validation = validate_selection(
            documents["config"],
            documents["manifest"],
            documents["recipe"],
            documents["selection_result"],
            selection_entries,
            selection_ledger_path,
            selection_result_path,
            recipe_path,
            config_path,
            preregistration_path,
            catalog_path,
            manifest_path,
            curve_validation_path,
            dataset_validation_path,
            findings,
        )
    except (KeyError, OSError, TypeError, ValueError) as error:
        findings.error(f"selection replay could not complete: {error}")
    try:
        provenance = validate_provenance(
            documents=documents,
            paths=paths,
            artifact_commit=artifact_commit,
            worktree_dirty=worktree_dirty,
            findings=findings,
        )
    except (KeyError, OSError, TypeError, ValueError) as error:
        findings.error(f"provenance validation could not complete: {error}")

    unexpected_modules = sorted(
        name
        for name in sys.modules
        if name.endswith(".run_assay")
        or name.endswith(".representations")
        or name in {"run_assay", "representations"}
    )
    if unexpected_modules:
        findings.error(
            "producer modules were imported: "
            + ", ".join(unexpected_modules)
        )

    validator_path = Path(__file__).resolve()
    result_validator_path = ROOT / RESULT_VALIDATOR_RELATIVE_PATH
    curve_validator_path = ROOT / CURVE_VALIDATOR_RELATIVE_PATH
    dataset_validator_path = ROOT / DATASET_VALIDATOR_RELATIVE_PATH
    oracle_path = ROOT / ORACLE_RELATIVE_PATH
    selection_summary = stable_selection_summary(
        selection_validation, hashes
    )
    status = "pass" if findings.error_count == 0 else "fail"
    if status != "pass":
        selection_summary["blind_evaluation_authorized"] = False

    result: dict[str, Any] = {
        "schema_version": 1,
        "experiment_id": documents["config"].get("experiment_id"),
        "validation_role": "independent pre-blind selection authorization",
        "status": status,
        "error_count": findings.error_count,
        "errors": findings.errors,
        "errors_truncated": findings.error_count > len(findings.errors),
        "warnings": findings.warnings,
        "selection": selection_summary,
        "bindings": {
            "config_sha256": hashes["config"],
            "preregistration_sha256": hashes["preregistration"],
            "catalog_sha256": hashes["catalog"],
            "manifest_sha256": hashes["manifest"],
            "curve_validation_sha256": hashes["curve_validation"],
            "dataset_validation_sha256": hashes["dataset_validation"],
        },
        "validator_sha256": sha256_file(validator_path),
        "source_commit": artifact_commit,
        "source_worktree_dirty_before_run": worktree_dirty,
        "dataset_files_opened": [],
        "producer_modules_imported": bool(unexpected_modules),
        "validator_hashes": {
            "validate_selection_sha256": sha256_file(validator_path),
            "validate_results_sha256": sha256_file(result_validator_path),
            "validate_curves_sha256": sha256_file(curve_validator_path),
            "validate_dataset_sha256": sha256_file(dataset_validator_path),
            "framework_oracle_sha256": sha256_file(oracle_path),
        },
        "input_validation": input_validation,
        "provenance": provenance,
        "wall_time_seconds": time.perf_counter() - started,
    }
    result["report_payload_sha256"] = payload_hash(
        result, "report_payload_sha256"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Independently validate the committed P1E selection freeze "
            "before any blind evaluation."
        )
    )
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--curve-validation", type=Path, required=True)
    parser.add_argument("--dataset-validation", type=Path, required=True)
    parser.add_argument("--selection-result", type=Path, required=True)
    parser.add_argument("--selection-ledger", type=Path, required=True)
    parser.add_argument("--recipe", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    result = validate(
        config_path=args.config.resolve(),
        preregistration_path=args.preregistration.resolve(),
        catalog_path=args.catalog.resolve(),
        manifest_path=args.manifest.resolve(),
        curve_validation_path=args.curve_validation.resolve(),
        dataset_validation_path=args.dataset_validation.resolve(),
        selection_result_path=args.selection_result.resolve(),
        selection_ledger_path=args.selection_ledger.resolve(),
        recipe_path=args.recipe.resolve(),
    )
    output_path = args.output.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        f"P1E pre-blind selection validation {result['status']}: "
        f"{result['error_count']} errors"
    )
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
