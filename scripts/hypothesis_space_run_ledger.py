#!/usr/bin/env python3
"""Record and validate operational runs of the million-cell screening space.

This ledger is deliberately separate from scientific outcome events. It proves
which frozen projection was processed, records performance and pipeline errors,
and tracks deltas between distinct map roots. It cannot falsify a hypothesis,
train the ranker, calibrate EIG, authorize execution, or promote a route.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import platform
import re
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from hypothesis_space_funnel import run_space


ROOT = Path(__file__).resolve().parent.parent
POLICY_PATH = ROOT / "repo" / "HYPOTHESIS_SPACE_RUN_LEDGER_V1.json"
RUN_DIR = ROOT / "experiments" / "engine" / "hypothesis_space_runs"
STATE_PATH = ROOT / "data" / "hypothesis_space_run_state.json"
RUN_ID_RE = re.compile(r"^HSR-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{3}$")
HEX40_RE = re.compile(r"^[0-9a-f]{40}$")
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_EPISTEMIC_CONTRACT = {
    "cold_cell": "A typed combination failed one or more deterministic screening rules; it is not a falsified mathematical hypothesis.",
    "warm_cell": "A typed combination survived structural screening but still lacks the evidence needed to be a hypothesis candidate.",
    "hot_cell": "Reserved for a mechanism-assured and independently reviewed proposal; this ledger cannot create one.",
    "completed_run": "Engineering evidence that one frozen finite projection was processed reproducibly.",
    "failed_run": "Operational evidence about the pipeline, not evidence for or against an ECDLP claim.",
    "scientific_outcome_source": "experiments/engine/outcomes and typed desk decisions, never this run ledger",
}
EXPECTED_PROHIBITED_INFERENCES = [
    "typed combinations are not independently generated hypotheses",
    "screening rejection is not falsification",
    "throughput is not research progress",
    "repeating an unchanged instance root is not new map coverage",
    "a benchmark record is not ranker training data or Brier calibration data",
    "this ledger cannot authorize execution, recommend a candidate, promote a route, or change the threat model",
]
EXPECTED_RETENTION_CONTRACT = {
    "raw_cells_retained": False,
    "whole_space_identity": "RFC6962 coverage root plus instance root",
    "screening_diagnostics": "exact aggregate histograms plus bounded witnesses in the subject state",
    "run_history": "SHA-256-anchored append-only records",
    "map_history": "one delta per distinct instance root; repeated benchmarks do not create knowledge revisions",
    "preflight_failures": "invalid provenance or source mismatch fails closed before a run record exists; only failures after provenance preflight enter operational history",
}
HARNESS_RESOLUTION_RULE = (
    "current checkout or reachable Git history contains matching path bytes"
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def rendered_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=True,
        indent=2,
        sort_keys=False,
        allow_nan=False,
    ) + "\n"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def payload_digest(record: dict[str, Any]) -> str:
    payload = copy.deepcopy(record)
    payload.pop("record_payload_sha256", None)
    return sha256_bytes(canonical_bytes(payload))


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def git_file_bytes(commit: str, relative_path: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{commit}:{relative_path}"],
        cwd=ROOT,
        capture_output=True,
    )
    if result.returncode:
        raise ValueError(f"{commit}:{relative_path}: unavailable in Git")
    return result.stdout


def git_json(commit: str, relative_path: str) -> dict[str, Any]:
    value = json.loads(git_file_bytes(commit, relative_path).decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{commit}:{relative_path}: expected a JSON object")
    return value


def commit_is_ancestor_of_ref(commit: str, reference: str) -> bool:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit, reference],
        cwd=ROOT,
        capture_output=True,
    )
    return result.returncode == 0


def commit_is_ancestor_of_head(commit: str) -> bool:
    return commit_is_ancestor_of_ref(commit, "HEAD")


def git_revision_file_digest(commit: str, relative_path: str) -> str | None:
    try:
        return sha256_bytes(git_file_bytes(commit, relative_path))
    except ValueError:
        return None


def harness_digest_resolves(relative_path: str, digest: str) -> bool:
    current = ROOT / relative_path
    if current.is_file() and sha256_file(current) == digest:
        return True
    history = subprocess.run(
        ["git", "log", "--format=%H", "HEAD", "--", relative_path],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if history.returncode:
        return False
    return any(
        git_revision_file_digest(commit, relative_path) == digest
        for commit in history.stdout.splitlines()
        if HEX40_RE.fullmatch(commit)
    )


def github_push_before_sha() -> str | None:
    """Return the immutable pre-push commit from a GitHub push event."""
    if os.environ.get("GITHUB_EVENT_NAME") != "push":
        return None
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        raise ValueError("GitHub push event is missing GITHUB_EVENT_PATH")
    try:
        event = json.loads(Path(event_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read GitHub push event: {exc}") from exc
    before = event.get("before")
    if not isinstance(before, str) or not HEX40_RE.fullmatch(before) or before == "0" * 40:
        raise ValueError("GitHub push event has no valid before commit")
    return before


def protected_base_anchors(policy: dict[str, Any]) -> list[dict[str, str]]:
    """Read the ledger anchors at the merge base to forbid rewrite/truncation."""
    protected_ref = policy["protected_base_ref"]
    merge_base = subprocess.run(
        ["git", "merge-base", "HEAD", protected_ref],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if merge_base.returncode:
        raise ValueError(f"cannot resolve protected base ref {protected_ref}")
    commit = merge_base.stdout.strip()
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    ).stdout.strip()
    if commit == head:
        push_before = github_push_before_sha()
        if push_before is not None:
            ancestor = subprocess.run(
                ["git", "merge-base", "--is-ancestor", push_before, head],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            if ancestor.returncode:
                raise ValueError("GitHub push before commit is not an ancestor of HEAD")
            commit = push_before
        else:
            parent = subprocess.run(
                ["git", "rev-parse", "HEAD^1"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            if parent.returncode:
                return []
            commit = parent.stdout.strip()
    result = subprocess.run(
        ["git", "show", f"{commit}:repo/HYPOTHESIS_SPACE_RUN_LEDGER_V1.json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode:
        return []
    value = json.loads(result.stdout)
    anchors = value.get("immutable_record_anchors", [])
    if not isinstance(anchors, list):
        raise ValueError("protected-base run anchors are invalid")
    return anchors


def load_policy() -> dict[str, Any]:
    return read_json(POLICY_PATH)


def validate_policy(policy: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    if policy.get("schema_version") != "1.0":
        problems.append("policy.schema_version must be 1.0")
    if policy.get("status") != "accepted_non_scientific_operational_memory":
        problems.append("policy status must preserve the non-scientific boundary")
    if policy.get("constitution_source") != "repo/HYPOTHESIS_SELECTION_CONSTITUTION_V3.md":
        problems.append("policy must bind the selection constitution")
    if policy.get("protected_base_ref") != "refs/remotes/origin/main":
        problems.append("policy must bind refs/remotes/origin/main as protected base")
    harness = policy.get("harness")
    if harness != {
        "path": "scripts/hypothesis_space_run_ledger.py",
        "resolution_rule": "The recorded SHA-256 must match the current path or the same path in reachable Git history.",
    }:
        problems.append("policy.harness must preserve the frozen resolution rule")
    if policy.get("epistemic_contract") != EXPECTED_EPISTEMIC_CONTRACT:
        problems.append("policy.epistemic_contract differs from the enforced scientific boundary")
    if policy.get("prohibited_inferences") != EXPECTED_PROHIBITED_INFERENCES:
        problems.append("policy.prohibited_inferences differs from the enforced scientific boundary")
    subject = policy.get("subject", {})
    required_paths = {
        "space_policy_path",
        "state_path",
        "map_path",
        "runner_path",
        "shared_funnel_path",
    }
    if set(subject) != required_paths:
        problems.append("policy.subject has an unexpected shape")
    for relative in subject.values() if isinstance(subject, dict) else []:
        if not isinstance(relative, str) or not (ROOT / relative).is_file():
            problems.append(f"policy subject path does not resolve: {relative!r}")
    benchmark = policy.get("benchmark_contract", {})
    minimum = benchmark.get("minimum_measured_repetitions")
    maximum = benchmark.get("maximum_measured_repetitions")
    if not isinstance(minimum, int) or not isinstance(maximum, int) or not 1 <= minimum <= maximum:
        problems.append("policy benchmark repetition range is invalid")
    if benchmark.get("performance_is_hardware_and_load_dependent") is not True:
        problems.append("policy must mark performance as environment-dependent")
    if benchmark.get("method") != "in_process_run_space_core_plus_output_equality_v1":
        problems.append("policy benchmark method is invalid")
    if benchmark.get("timing_clock") != "time.perf_counter_ns":
        problems.append("policy benchmark timing clock is invalid")
    if benchmark.get("recorded_at_utc_semantics") != "benchmark start time":
        problems.append("policy benchmark timestamp semantics are invalid")
    if benchmark.get("target_source") != "subject data/hypothesis_space_state.json performance_contract":
        problems.append("policy benchmark target source is invalid")
    if policy.get("retention_contract") != EXPECTED_RETENTION_CONTRACT:
        problems.append("policy.retention_contract differs from the enforced memory boundary")
    anchors = policy.get("immutable_record_anchors")
    if not isinstance(anchors, list):
        problems.append("policy.immutable_record_anchors must be an array")
        return problems
    if not anchors:
        problems.append("accepted run ledger must retain at least one immutable record")
    seen_ids: set[str] = set()
    seen_files: set[str] = set()
    for index, anchor in enumerate(anchors):
        label = f"policy.immutable_record_anchors[{index}]"
        if not isinstance(anchor, dict) or set(anchor) != {"run_id", "path", "sha256"}:
            problems.append(f"{label}: unexpected shape")
            continue
        run_id = anchor.get("run_id")
        path = anchor.get("path")
        digest = anchor.get("sha256")
        if not isinstance(run_id, str) or not RUN_ID_RE.fullmatch(run_id):
            problems.append(f"{label}.run_id: invalid")
        elif run_id in seen_ids:
            problems.append(f"{label}.run_id: duplicate")
        else:
            seen_ids.add(run_id)
        expected_path = f"experiments/engine/hypothesis_space_runs/{run_id}.json"
        if path != expected_path:
            problems.append(f"{label}.path: must be {expected_path}")
        elif path in seen_files:
            problems.append(f"{label}.path: duplicate")
        else:
            seen_files.add(path)
        if not isinstance(digest, str) or not HEX64_RE.fullmatch(digest):
            problems.append(f"{label}.sha256: invalid")
    return problems


def screening_snapshot(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "counts": state["counts"],
        "counts_by_type": state["counts_by_type"],
        "challenge_coverage": state["challenge_coverage"],
        "rejection_histogram": state["rejection_histogram"],
        "primary_rejection_histogram": state["primary_rejection_histogram"],
        "warning_histogram": state["warning_histogram"],
        "review_queue_seed_ids": [item["seed_id"] for item in state["review_queue"]],
    }


def historical_subject(
    policy: dict[str, Any], source_commit: str
) -> tuple[dict[str, Any], dict[str, Any], dict[str, str]]:
    subject = policy["subject"]
    state = git_json(source_commit, subject["state_path"])
    map_state = git_json(source_commit, subject["map_path"])
    digests = {
        key: sha256_bytes(git_file_bytes(source_commit, relative))
        for key, relative in sorted(subject.items())
    }
    return state, map_state, digests


def rate_per_minute(attempts: int, elapsed_ns: int) -> int:
    if elapsed_ns <= 0:
        raise ValueError("elapsed_ns must be positive")
    return round(attempts * 60_000_000_000 / elapsed_ns)


def expected_performance_summary(rates: list[int]) -> dict[str, int]:
    if not rates:
        raise ValueError("at least one measured rate is required")
    return {
        "minimum_signatures_per_minute": min(rates),
        "median_signatures_per_minute": round(statistics.median(rates)),
        "maximum_signatures_per_minute": max(rates),
    }


def environment_shape_valid(environment: Any) -> bool:
    return (
        isinstance(environment, dict)
        and set(environment)
        == {
            "python_version",
            "python_implementation",
            "platform_system",
            "platform_machine",
            "logical_cpu_count",
        }
        and all(
            isinstance(environment.get(key), str) and bool(environment[key])
            for key in (
                "python_version",
                "python_implementation",
                "platform_system",
                "platform_machine",
            )
        )
        and (
            environment.get("logical_cpu_count") is None
            or (
                isinstance(environment["logical_cpu_count"], int)
                and environment["logical_cpu_count"] > 0
            )
        )
    )


def validate_record(
    record: dict[str, Any],
    policy: dict[str, Any],
    *,
    verify_git: bool = True,
) -> list[str]:
    problems: list[str] = []
    required = {
        "schema_version",
        "run_id",
        "sequence",
        "recorded_at_utc",
        "record_kind",
        "status",
        "harness",
        "subject",
        "screening_snapshot",
        "execution",
        "operational_diagnostics",
        "knowledge_effect",
        "previous_record_sha256",
        "record_payload_sha256",
    }
    if set(record) != required:
        problems.append("record has an unexpected top-level shape")
        return problems
    run_id = record.get("run_id")
    if not isinstance(run_id, str) or not RUN_ID_RE.fullmatch(run_id):
        problems.append("run_id is invalid")
    if not isinstance(record.get("sequence"), int) or record["sequence"] < 1:
        problems.append("sequence must be a positive integer")
    if record.get("schema_version") != "1.0":
        problems.append("schema_version must be 1.0")
    if record.get("record_kind") != "deterministic_screening_benchmark":
        problems.append("record_kind is invalid")
    if record.get("status") not in {"completed", "failed"}:
        problems.append("status must be completed or failed")
    try:
        recorded_at = record.get("recorded_at_utc", "")
        parsed_at = datetime.fromisoformat(recorded_at.replace("Z", "+00:00"))
        if parsed_at.tzinfo is None or parsed_at.utcoffset() != timezone.utc.utcoffset(parsed_at):
            raise ValueError
        if isinstance(run_id, str) and run_id[4:14] != parsed_at.date().isoformat():
            problems.append("run_id date must match recorded_at_utc")
    except (TypeError, ValueError):
        problems.append("recorded_at_utc must be an ISO UTC timestamp")
    previous = record.get("previous_record_sha256")
    if previous is not None and (not isinstance(previous, str) or not HEX64_RE.fullmatch(previous)):
        problems.append("previous_record_sha256 is invalid")
    digest = record.get("record_payload_sha256")
    if not isinstance(digest, str) or digest != payload_digest(record):
        problems.append("record_payload_sha256 does not match the canonical payload")

    harness = record.get("harness")
    expected_harness_keys = {"path", "sha256", "resolution_rule"}
    if not isinstance(harness, dict) or set(harness) != expected_harness_keys:
        problems.append("harness has an unexpected shape")
    else:
        harness_path = policy.get("harness", {}).get("path")
        if not isinstance(harness_path, str):
            problems.append("policy harness path is invalid")
        elif harness.get("path") != harness_path:
            problems.append("harness.path differs from policy")
        harness_digest = harness.get("sha256")
        if not isinstance(harness_digest, str) or not HEX64_RE.fullmatch(harness_digest):
            problems.append("harness.sha256 is invalid")
        elif isinstance(harness_path, str) and not harness_digest_resolves(
            harness_path, harness_digest
        ):
            problems.append("harness SHA-256 does not resolve in checkout or Git history")
        if harness.get("resolution_rule") != HARNESS_RESOLUTION_RULE:
            problems.append("harness.resolution_rule is invalid")

    subject = record.get("subject")
    expected_subject_keys = {
        "source_commit",
        "space_id",
        "source_paths_sha256",
        "source_bindings",
        "instance_root_sha256",
        "coverage_merkle_root_sha256",
        "attempts",
    }
    if not isinstance(subject, dict) or set(subject) != expected_subject_keys:
        problems.append("subject has an unexpected shape")
        return problems
    source_commit = subject.get("source_commit")
    if not isinstance(source_commit, str) or not HEX40_RE.fullmatch(source_commit):
        problems.append("subject.source_commit is invalid")
        return problems
    if verify_git and not commit_is_ancestor_of_head(source_commit):
        problems.append("subject.source_commit is not an ancestor of HEAD")
        return problems
    if verify_git and not commit_is_ancestor_of_ref(
        source_commit, policy["protected_base_ref"]
    ):
        problems.append("subject.source_commit is not an ancestor of protected main")
        return problems
    try:
        source_state, source_map, source_digests = historical_subject(policy, source_commit)
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        problems.append(str(exc))
        return problems
    if subject.get("source_paths_sha256") != source_digests:
        problems.append("subject source path digests do not match source_commit")
    if subject.get("space_id") != source_state.get("space_id"):
        problems.append("subject.space_id differs from the source state")
    if subject.get("source_bindings") != source_state.get("source_bindings"):
        problems.append("subject.source_bindings differ from the source state")
    if subject.get("instance_root_sha256") != source_state.get("bulk_contract", {}).get("instance_root_sha256"):
        problems.append("subject instance root differs from the source state")
    if subject.get("coverage_merkle_root_sha256") != source_state.get("bulk_contract", {}).get("coverage_merkle_root_sha256"):
        problems.append("subject coverage root differs from the source state")
    if subject.get("attempts") != source_state.get("counts", {}).get("attempts"):
        problems.append("subject attempt count differs from the source state")
    if source_map.get("instance_root_sha256") != subject.get("instance_root_sha256"):
        problems.append("source state and map do not share one instance root")

    diagnostics = record.get("operational_diagnostics")
    expected_diagnostic_keys = {"pipeline_errors", "invariant_violations", "error_classes"}
    if not isinstance(diagnostics, dict) or set(diagnostics) != expected_diagnostic_keys:
        problems.append("operational_diagnostics has an unexpected shape")
        return problems
    for key in ("pipeline_errors", "invariant_violations"):
        if not isinstance(diagnostics.get(key), int) or diagnostics[key] < 0:
            problems.append(f"operational_diagnostics.{key} must be a nonnegative integer")
    if not isinstance(diagnostics.get("error_classes"), list) or not all(
        isinstance(item, str) and item for item in diagnostics.get("error_classes", [])
    ):
        problems.append("operational_diagnostics.error_classes is invalid")

    effect = record.get("knowledge_effect")
    expected_effect = {
        "scientific_outcome",
        "claim_disposition",
        "ranker_training_eligible",
        "brier_calibration_eligible",
        "candidate_admissible",
        "candidate_recommended",
        "experiment_authorized",
        "route_promotion",
        "evidence_class",
        "operational_calibration_scope",
        "scientific_exclusion_reasons",
        "interpretation",
    }
    if not isinstance(effect, dict) or set(effect) != expected_effect:
        problems.append("knowledge_effect has an unexpected shape")
    else:
        if effect.get("scientific_outcome") != "none" or effect.get("claim_disposition") != "none":
            problems.append("screening runs cannot create scientific outcomes or claim dispositions")
        if effect.get("evidence_class") != "operational":
            problems.append("knowledge_effect.evidence_class must be operational")
        if effect.get("operational_calibration_scope") != "throughput_only":
            problems.append("knowledge_effect.operational_calibration_scope must be throughput_only")
        if effect.get("scientific_exclusion_reasons") != [
            "deterministic_hard_gate",
            "nonexperimental_benchmark",
        ]:
            problems.append("knowledge_effect scientific exclusions are invalid")
        for key in (
            "ranker_training_eligible",
            "brier_calibration_eligible",
            "candidate_admissible",
            "candidate_recommended",
            "experiment_authorized",
            "route_promotion",
        ):
            if effect.get(key) is not False:
                problems.append(f"knowledge_effect.{key} must be false")
        if not isinstance(effect.get("interpretation"), str) or not effect["interpretation"]:
            problems.append("knowledge_effect.interpretation is required")

    execution = record.get("execution")
    if not isinstance(execution, dict):
        problems.append("execution must be an object")
        return problems
    completed = record.get("status") == "completed"
    if completed:
        if record.get("screening_snapshot") != screening_snapshot(source_state):
            problems.append("screening_snapshot differs from the source state")
        snapshot = record.get("screening_snapshot")
        if isinstance(snapshot, dict):
            counts = snapshot.get("counts", {})
            attempts = subject.get("attempts")
            if (
                counts.get("cold", 0)
                + counts.get("warm", 0)
                + counts.get("hot", 0)
                != attempts
            ):
                problems.append("cold/warm/hot do not partition the attempted space")
            if counts.get("hot") != 0:
                problems.append("operational screening record cannot contain hot cells")
            if sum(snapshot.get("primary_rejection_histogram", {}).values()) != counts.get("cold"):
                problems.append("primary rejection histogram does not partition cold cells")
            for key in (
                "admissible",
                "recommended",
                "authorized",
                "route_promotions",
                "experiment_events",
            ):
                if counts.get(key) != 0:
                    problems.append(f"screening snapshot counts.{key} must be zero")
        if diagnostics.get("pipeline_errors") != 0 or diagnostics.get("invariant_violations") != 0 or diagnostics.get("error_classes"):
            problems.append("completed run cannot retain operational errors")
        expected_execution_keys = {
            "method",
            "warmup_repetitions",
            "measured_repetitions",
            "elapsed_ns",
            "signatures_per_minute",
            "performance_summary",
            "target_signatures_per_minute",
            "performance_target_status",
            "timing_scope",
            "canonical_argv",
            "subject_files_match_source_commit",
            "environment",
        }
        if set(execution) != expected_execution_keys:
            problems.append("completed execution has an unexpected shape")
            return problems
        contract = policy["benchmark_contract"]
        if execution.get("method") != contract["method"]:
            problems.append("execution.method differs from the benchmark contract")
        measured = execution.get("measured_repetitions")
        elapsed = execution.get("elapsed_ns")
        rates = execution.get("signatures_per_minute")
        if not isinstance(measured, int) or not contract["minimum_measured_repetitions"] <= measured <= contract["maximum_measured_repetitions"]:
            problems.append("measured_repetitions is outside the policy range")
        if not isinstance(execution.get("warmup_repetitions"), int) or execution["warmup_repetitions"] < contract["minimum_warmup_repetitions"]:
            problems.append("warmup_repetitions is below the policy minimum")
        if not isinstance(elapsed, list) or len(elapsed) != measured or not all(isinstance(item, int) and item > 0 for item in elapsed):
            problems.append("elapsed_ns does not match measured_repetitions")
        elif not isinstance(rates, list) or rates != [rate_per_minute(subject["attempts"], item) for item in elapsed]:
            problems.append("signatures_per_minute is not derived from elapsed_ns")
        elif execution.get("performance_summary") != expected_performance_summary(rates):
            problems.append("performance_summary is not derived from measured rates")
        target = source_state.get("performance_contract", {}).get("target_signatures_per_minute")
        if execution.get("target_signatures_per_minute") != target:
            problems.append("benchmark target differs from the source state")
        if isinstance(rates, list) and rates:
            expected_verdict = "target_met" if statistics.median(rates) >= target else "target_not_met"
            if execution.get("performance_target_status") != expected_verdict:
                problems.append("performance_target_status differs from the median measured rate")
        if execution.get("timing_scope") != "run_space core plus exact output equality check; excludes process startup and JSON rendering":
            problems.append("timing_scope is not the frozen benchmark boundary")
        if execution.get("canonical_argv") != [
            "scripts/hypothesis_space_run_ledger.py",
            "--record",
            "--run-id",
            record["run_id"],
            "--source-commit",
            source_commit,
            "--repetitions",
            str(measured),
            "--warmups",
            str(execution.get("warmup_repetitions")),
        ]:
            problems.append("canonical_argv does not bind the benchmark invocation")
        if execution.get("subject_files_match_source_commit") is not True:
            problems.append("subject files must match source_commit before timing")
        environment = execution.get("environment")
        if not environment_shape_valid(environment):
            problems.append("benchmark environment has an unexpected shape")
    else:
        if record.get("screening_snapshot") is not None:
            problems.append("failed run cannot publish a screening snapshot")
        if diagnostics.get("pipeline_errors", 0) + diagnostics.get("invariant_violations", 0) < 1:
            problems.append("failed run must retain at least one operational error")
        if set(execution) != {
            "method",
            "warmup_repetitions",
            "measured_repetitions",
            "elapsed_ns",
            "timing_scope",
            "canonical_argv",
            "subject_files_match_source_commit",
            "environment",
        }:
            problems.append("failed execution has an unexpected shape")
        elif (
            not isinstance(execution.get("measured_repetitions"), int)
            or not isinstance(execution.get("elapsed_ns"), list)
            or execution["measured_repetitions"] != len(execution["elapsed_ns"])
        ):
            problems.append("failed execution must retain the completed timing prefix")
        failed_argv = execution.get("canonical_argv")
        contract = policy["benchmark_contract"]
        if execution.get("method") != contract["method"]:
            problems.append("failed execution.method differs from the benchmark contract")
        if (
            not isinstance(failed_argv, list)
            or len(failed_argv) != 10
            or failed_argv[:7] != [
                "scripts/hypothesis_space_run_ledger.py",
                "--record",
                "--run-id",
                record["run_id"],
                "--source-commit",
                source_commit,
                "--repetitions",
            ]
            or failed_argv[8] != "--warmups"
            or failed_argv[9] != str(execution.get("warmup_repetitions"))
        ):
            problems.append("failed execution canonical_argv is invalid")
        else:
            try:
                requested = int(failed_argv[7])
            except (TypeError, ValueError):
                problems.append("failed execution requested repetitions are invalid")
            else:
                if not contract["minimum_measured_repetitions"] <= requested <= contract["maximum_measured_repetitions"]:
                    problems.append("failed execution requested repetitions are outside policy")
                if execution.get("measured_repetitions", 0) > requested:
                    problems.append("failed execution timing prefix exceeds requested repetitions")
        elapsed = execution.get("elapsed_ns")
        if isinstance(elapsed, list) and not all(
            isinstance(item, int) and item > 0 for item in elapsed
        ):
            problems.append("failed execution elapsed_ns must contain positive integers")
        if (
            not isinstance(execution.get("warmup_repetitions"), int)
            or execution["warmup_repetitions"]
            < contract["minimum_warmup_repetitions"]
        ):
            problems.append("failed execution warmups are below policy")
        if execution.get("timing_scope") != "run_space core plus exact output equality check; excludes process startup and JSON rendering":
            problems.append("failed execution timing_scope is invalid")
        if execution.get("subject_files_match_source_commit") is not True:
            problems.append("failed execution must bind source-matching subject files")
        if not environment_shape_valid(execution.get("environment")):
            problems.append("failed benchmark environment has an unexpected shape")
    return problems


def load_anchored_records(
    policy: dict[str, Any], *, verify_git: bool = True
) -> tuple[list[dict[str, Any]], list[str]]:
    problems = validate_policy(policy)
    records: list[dict[str, Any]] = []
    anchors = policy.get("immutable_record_anchors", [])
    try:
        base_anchors = protected_base_anchors(policy)
        if anchors[: len(base_anchors)] != base_anchors:
            problems.append("immutable_record_anchors rewrite or truncate protected-base history")
    except (ValueError, json.JSONDecodeError) as exc:
        problems.append(str(exc))
    anchored_paths = {anchor.get("path") for anchor in anchors if isinstance(anchor, dict)}
    actual_paths = {
        path.relative_to(ROOT).as_posix()
        for path in RUN_DIR.glob("*.json")
    } if RUN_DIR.exists() else set()
    for extra in sorted(actual_paths - anchored_paths):
        problems.append(f"unanchored run record: {extra}")
    for missing in sorted(anchored_paths - actual_paths):
        problems.append(f"missing anchored run record: {missing}")

    previous_file_digest: str | None = None
    for index, anchor in enumerate(anchors):
        if not isinstance(anchor, dict) or set(anchor) != {"run_id", "path", "sha256"}:
            continue
        path = ROOT / anchor["path"]
        if not path.is_file():
            continue
        file_digest = sha256_file(path)
        if file_digest != anchor["sha256"]:
            problems.append(f"{anchor['run_id']}: file digest differs from immutable anchor")
            continue
        try:
            record = read_json(path)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            problems.append(f"{anchor['run_id']}: cannot parse: {exc}")
            continue
        if record.get("run_id") != anchor["run_id"]:
            problems.append(f"{anchor['run_id']}: run id differs from anchor")
        if record.get("sequence") != index + 1:
            problems.append(f"{anchor['run_id']}: sequence does not match anchor order")
        if record.get("previous_record_sha256") != previous_file_digest:
            problems.append(f"{anchor['run_id']}: append-only predecessor digest mismatch")
        problems.extend(
            f"{anchor['run_id']}: {problem}"
            for problem in validate_record(record, policy, verify_git=verify_git)
        )
        records.append(record)
        previous_file_digest = file_digest
    return records, problems


def histogram_delta(current: dict[str, int], previous: dict[str, int]) -> dict[str, int]:
    keys = sorted(set(current) | set(previous))
    return {key: current.get(key, 0) - previous.get(key, 0) for key in keys if current.get(key, 0) != previous.get(key, 0)}


def build_state(policy: dict[str, Any], records: list[dict[str, Any]]) -> dict[str, Any]:
    completed = [record for record in records if record["status"] == "completed"]
    failed = [record for record in records if record["status"] == "failed"]
    performance_history = [
        {
            "run_id": record["run_id"],
            "recorded_at_utc": record["recorded_at_utc"],
            "source_commit": record["subject"]["source_commit"],
            "instance_root_sha256": record["subject"]["instance_root_sha256"],
            **record["execution"]["performance_summary"],
            "target_signatures_per_minute": record["execution"]["target_signatures_per_minute"],
            "performance_target_status": record["execution"]["performance_target_status"],
        }
        for record in completed
    ]
    revisions: list[dict[str, Any]] = []
    previous_snapshot: dict[str, Any] | None = None
    seen_roots: set[str] = set()
    for record in completed:
        root = record["subject"]["instance_root_sha256"]
        snapshot = record["screening_snapshot"]
        if root in seen_roots:
            continue
        counts = snapshot["counts"]
        revision: dict[str, Any] = {
            "run_id": record["run_id"],
            "instance_root_sha256": root,
            "counts": counts,
            "delta_from_previous_distinct_root": None,
        }
        if previous_snapshot is not None:
            previous_counts = previous_snapshot["counts"]
            revision["delta_from_previous_distinct_root"] = {
                "counts": histogram_delta(counts, previous_counts),
                "rejections": histogram_delta(
                    snapshot["rejection_histogram"],
                    previous_snapshot["rejection_histogram"],
                ),
                "warnings": histogram_delta(
                    snapshot["warning_histogram"],
                    previous_snapshot["warning_histogram"],
                ),
                "review_queue_added": sorted(
                    set(snapshot["review_queue_seed_ids"])
                    - set(previous_snapshot["review_queue_seed_ids"])
                ),
                "review_queue_removed": sorted(
                    set(previous_snapshot["review_queue_seed_ids"])
                    - set(snapshot["review_queue_seed_ids"])
                ),
            }
        revisions.append(revision)
        seen_roots.add(root)
        previous_snapshot = snapshot

    latest = performance_history[-1] if performance_history else None
    anchor_stream = b"".join(
        bytes.fromhex(anchor["sha256"])
        for anchor in policy["immutable_record_anchors"]
    )
    return {
        "schema_version": "1.0-generated",
        "ledger_id": policy["ledger_id"],
        "status": "operational_memory_non_scientific",
        "immutable_record_count": len(records),
        "immutable_record_root_sha256": sha256_bytes(anchor_stream),
        "counts": {
            "runs": len(records),
            "completed_runs": len(completed),
            "failed_runs": len(failed),
            "pipeline_errors": sum(record["operational_diagnostics"]["pipeline_errors"] for record in records),
            "invariant_violations": sum(record["operational_diagnostics"]["invariant_violations"] for record in records),
            "distinct_instance_roots": len(revisions),
            "scientific_outcomes": 0,
            "ranker_training_labels": 0,
            "brier_calibration_records": 0,
            "authorizations": 0,
            "route_promotions": 0,
        },
        "latest_completed_run": latest,
        "performance_history": performance_history,
        "map_revisions": revisions,
        "operational_failures": [
            {
                "run_id": record["run_id"],
                "recorded_at_utc": record["recorded_at_utc"],
                **record["operational_diagnostics"],
            }
            for record in failed
        ],
        "retention_contract": policy["retention_contract"],
        "epistemic_contract": policy["epistemic_contract"],
        "scientific_memory_boundary": {
            "screening_rejections_are_falsifications": False,
            "repeated_root_is_new_knowledge": False,
            "outcome_events_path": "experiments/engine/outcomes",
            "typed_desk_decisions_path": "experiments/engine/desk_decisions",
            "claim_state_path": "data/research_claim_state.json",
        },
    }


def current_environment() -> dict[str, Any]:
    return {
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "platform_system": platform.system(),
        "platform_machine": platform.machine(),
        "logical_cpu_count": os.cpu_count(),
    }


def assert_checkout_matches_source(policy: dict[str, Any], source_commit: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, str]]:
    state, map_state, digests = historical_subject(policy, source_commit)
    for key, relative in policy["subject"].items():
        current = ROOT / relative
        if sha256_file(current) != digests[key]:
            raise ValueError(f"current {relative} differs from source_commit; refusing benchmark attribution")
    return state, map_state, digests


def create_run_record(
    policy: dict[str, Any],
    *,
    run_id: str,
    sequence: int,
    source_commit: str,
    repetitions: int,
    warmups: int,
    previous_record_sha256: str | None,
) -> dict[str, Any]:
    if not RUN_ID_RE.fullmatch(run_id):
        raise ValueError("run_id must match HSR-YYYY-MM-DD-NNN")
    recorded_at_utc = datetime.now(timezone.utc).isoformat(
        timespec="seconds"
    ).replace("+00:00", "Z")
    if run_id[4:14] != recorded_at_utc[:10]:
        raise ValueError("run_id date must match the UTC benchmark start date")
    if sequence < 1:
        raise ValueError("sequence must be positive")
    if not HEX40_RE.fullmatch(source_commit):
        raise ValueError("source_commit must be lowercase 40-hex")
    if not commit_is_ancestor_of_head(source_commit):
        raise ValueError("source_commit must be an ancestor of HEAD")
    if not commit_is_ancestor_of_ref(source_commit, policy["protected_base_ref"]):
        raise ValueError("source_commit must be an ancestor of protected main")
    contract = policy["benchmark_contract"]
    if not contract["minimum_measured_repetitions"] <= repetitions <= contract["maximum_measured_repetitions"]:
        raise ValueError("repetitions outside the benchmark contract")
    if warmups < contract["minimum_warmup_repetitions"]:
        raise ValueError("warmups below the benchmark contract")
    source_state, source_map, source_digests = assert_checkout_matches_source(policy, source_commit)
    expected_snapshot = screening_snapshot(source_state)
    harness = {
        "path": policy["harness"]["path"],
        "sha256": sha256_file(ROOT / policy["harness"]["path"]),
        "resolution_rule": HARNESS_RESOLUTION_RULE,
    }

    def checked_run() -> None:
        state, map_state = run_space()
        if state != source_state or map_state != source_map:
            raise AssertionError("run_space output differs from the source-commit state")

    argv = [
        "scripts/hypothesis_space_run_ledger.py",
        "--record",
        "--run-id",
        run_id,
        "--source-commit",
        source_commit,
        "--repetitions",
        str(repetitions),
        "--warmups",
        str(warmups),
    ]
    elapsed_ns: list[int] = []
    attempts = source_state["counts"]["attempts"]
    failure: Exception | None = None
    try:
        for _ in range(warmups):
            checked_run()
        for _ in range(repetitions):
            started = time.perf_counter_ns()
            checked_run()
            elapsed_ns.append(time.perf_counter_ns() - started)
    except Exception as exc:  # Retain the operational failure without scientific meaning.
        failure = exc

    effect = {
        "scientific_outcome": "none",
        "claim_disposition": "none",
        "ranker_training_eligible": False,
        "brier_calibration_eligible": False,
        "candidate_admissible": False,
        "candidate_recommended": False,
        "experiment_authorized": False,
        "route_promotion": False,
        "evidence_class": "operational",
        "operational_calibration_scope": "throughput_only",
        "scientific_exclusion_reasons": [
            "deterministic_hard_gate",
            "nonexperimental_benchmark",
        ],
        "interpretation": "This is a reproducible engineering benchmark and structural-screen snapshot, not an ECDLP result.",
    }
    subject = {
        "source_commit": source_commit,
        "space_id": source_state["space_id"],
        "source_paths_sha256": source_digests,
        "source_bindings": source_state["source_bindings"],
        "instance_root_sha256": source_state["bulk_contract"]["instance_root_sha256"],
        "coverage_merkle_root_sha256": source_state["bulk_contract"]["coverage_merkle_root_sha256"],
        "attempts": attempts,
    }
    if failure is not None:
        invariant = isinstance(failure, (AssertionError, ValueError))
        record = {
            "schema_version": "1.0",
            "run_id": run_id,
            "sequence": sequence,
            "recorded_at_utc": recorded_at_utc,
            "record_kind": "deterministic_screening_benchmark",
            "status": "failed",
            "harness": harness,
            "subject": subject,
            "screening_snapshot": None,
            "execution": {
                "method": contract["method"],
                "warmup_repetitions": warmups,
                "measured_repetitions": len(elapsed_ns),
                "elapsed_ns": elapsed_ns,
                "timing_scope": "run_space core plus exact output equality check; excludes process startup and JSON rendering",
                "canonical_argv": argv,
                "subject_files_match_source_commit": True,
                "environment": current_environment(),
            },
            "operational_diagnostics": {
                "pipeline_errors": 0 if invariant else 1,
                "invariant_violations": 1 if invariant else 0,
                "error_classes": [type(failure).__name__],
            },
            "knowledge_effect": effect,
            "previous_record_sha256": previous_record_sha256,
        }
        record["record_payload_sha256"] = payload_digest(record)
        return record

    rates = [rate_per_minute(attempts, elapsed) for elapsed in elapsed_ns]
    target = source_state["performance_contract"]["target_signatures_per_minute"]
    record: dict[str, Any] = {
        "schema_version": "1.0",
        "run_id": run_id,
        "sequence": sequence,
        "recorded_at_utc": recorded_at_utc,
        "record_kind": "deterministic_screening_benchmark",
        "status": "completed",
        "harness": harness,
        "subject": subject,
        "screening_snapshot": expected_snapshot,
        "execution": {
            "method": contract["method"],
            "warmup_repetitions": warmups,
            "measured_repetitions": repetitions,
            "elapsed_ns": elapsed_ns,
            "signatures_per_minute": rates,
            "performance_summary": expected_performance_summary(rates),
            "target_signatures_per_minute": target,
            "performance_target_status": "target_met" if statistics.median(rates) >= target else "target_not_met",
            "timing_scope": "run_space core plus exact output equality check; excludes process startup and JSON rendering",
            "canonical_argv": argv,
            "subject_files_match_source_commit": True,
            "environment": current_environment(),
        },
        "operational_diagnostics": {
            "pipeline_errors": 0,
            "invariant_violations": 0,
            "error_classes": [],
        },
        "knowledge_effect": effect,
        "previous_record_sha256": previous_record_sha256,
    }
    record["record_payload_sha256"] = payload_digest(record)
    return record


def write_record(record: dict[str, Any]) -> Path:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    path = RUN_DIR / f"{record['run_id']}.json"
    if path.exists():
        raise ValueError(f"refusing to overwrite {path.relative_to(ROOT)}")
    path.write_text(rendered_json(record), encoding="utf-8", newline="\n")
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--record", action="store_true")
    parser.add_argument("--run-id")
    parser.add_argument("--source-commit")
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--warmups", type=int, default=1)
    args = parser.parse_args()
    policy = load_policy()

    if args.record:
        if not args.run_id or not args.source_commit:
            parser.error("--record requires --run-id and --source-commit")
        _, preflight_problems = load_anchored_records(policy)
        if not policy.get("immutable_record_anchors") and not any(RUN_DIR.glob("*.json")):
            preflight_problems = [
                problem
                for problem in preflight_problems
                if problem != "accepted run ledger must retain at least one immutable record"
            ]
        if preflight_problems:
            print("refusing to record against an invalid run ledger:", file=sys.stderr)
            for problem in preflight_problems:
                print(f"- {problem}", file=sys.stderr)
            return 1
        anchors = policy.get("immutable_record_anchors", [])
        previous = anchors[-1]["sha256"] if anchors else None
        record = create_run_record(
            policy,
            run_id=args.run_id,
            sequence=len(anchors) + 1,
            source_commit=args.source_commit,
            repetitions=args.repetitions,
            warmups=args.warmups,
            previous_record_sha256=previous,
        )
        record_problems = validate_record(record, policy)
        if record_problems:
            print("refusing to write invalid run record:", file=sys.stderr)
            for problem in record_problems:
                print(f"- {problem}", file=sys.stderr)
            return 1
        path = write_record(record)
        digest = sha256_file(path)
        print(f"recorded {path.relative_to(ROOT)} sha256={digest}")
        print("Add this exact path and digest to immutable_record_anchors, then regenerate the ledger state.")
        return 0 if record["status"] == "completed" else 2

    records, problems = load_anchored_records(policy)
    state = build_state(policy, records)
    payload = rendered_json(state)
    if args.check:
        if not STATE_PATH.is_file() or STATE_PATH.read_text(encoding="utf-8") != payload:
            problems.append("data/hypothesis_space_run_state.json is stale")
    if problems:
        print("hypothesis-space run ledger check failed:", file=sys.stderr)
        for problem in problems:
            print(f"- {problem}", file=sys.stderr)
        return 1
    if not args.check:
        STATE_PATH.write_text(payload, encoding="utf-8", newline="\n")
    print(
        "HYP_SPACE_RUN_LEDGER_OK "
        f"records={len(records)} completed={state['counts']['completed_runs']} "
        f"failed={state['counts']['failed_runs']} roots={state['counts']['distinct_instance_roots']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
