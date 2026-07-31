#!/usr/bin/env python3
"""Deterministic Research Engine v0 validation and selection helpers."""
from __future__ import annotations

import ast
import copy
import hashlib
import json
import math
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any

from hypothesis_generation_lib import (
    GENERATION_POLICY_PATH,
    PROPOSALS_DIR,
    REVIEWS_DIR,
    build_generation_state,
    load_json_records as load_hypothesis_generation_records,
)
from scientific_provenance import (
    git_commit_exists,
    git_file_bytes,
    scientific_source_commit_allowed,
    validation_problems as scientific_provenance_problems,
)

ROOT = Path(__file__).resolve().parent.parent
POLICY_PATH = ROOT / "repo" / "RESEARCH_ENGINE_V0.json"
DECISION_PATH = ROOT / "repo" / "ECDLP_DECISION_SUBSTRATE.json"
HYPOTHESES_PATH = ROOT / "experiments" / "HYPOTHESES.yaml"
OUTCOMES_DIR = ROOT / "experiments" / "engine" / "outcomes"
RUNS_DIR = ROOT / "experiments" / "engine" / "runs"
SCIENTIFIC_VALIDATORS_DIR = ROOT / "experiments" / "engine" / "validators"
STATE_PATH = ROOT / "data" / "research_engine_state.json"

HARD_REJECTIONS = {
    "changes_threat_model",
    "hidden_or_unpriced_precomputation",
    "missing_exact_mechanism",
    "missing_falsifiable_prediction",
    "missing_independent_validator",
    "targets_secp256k1_directly",
    "no_new_premise_after_resolution",
}
CANDIDATE_FIELDS = {
    "id",
    "title",
    "route_id",
    "hypothesis_id",
    "kind",
    "gap_class",
    "downstream_research_window",
    "mechanism",
    "prediction",
    "baseline",
    "stop_condition",
    "validator",
    "scope",
    "budget",
    "preregistration",
    "evidence_inputs",
    "dependencies",
    "dependency_requirements",
    "information_model",
    "hard_rejections",
    "authorization",
    "result_updates",
}
TARGET_CONTRACT_FIELDS = {
    "primary_threat_model",
    "selection_rule",
    "claim_boundary",
}
INFORMATION_MODEL_FIELDS = {
    "latent_question",
    "prior_live",
    "prior_rationale",
    "likelihoods",
}
LIKELIHOOD_FIELDS = {"live", "dead"}
CANDIDATE_SCOPE_FIELDS = {
    "curve_family",
    "max_field_bits",
    "forbidden_targets",
    "threat_model",
}
CANDIDATE_BUDGET_FIELDS = {
    "wall_time_seconds",
    "peak_memory_bytes",
    "parallel_workers",
}
CANDIDATE_INTAKE_CONTRACT_FIELDS = {
    "legacy_candidate_set_status",
    "legacy_candidate_set_sha256",
    "authoritative_new_candidate_source",
    "compiler_status",
    "compiled_candidate_count",
    "authorization_rule",
}
PREREGISTRATION_FIELDS = {
    "status",
    "solver",
    "seeds",
    "curves",
    "instances",
    "target_rule",
    "primary_metric",
    "validator_contract",
    "success_rule",
    "stop_rule",
}
VALIDATOR_CONTRACT_FIELDS = {
    "status",
    "protocol",
    "entrypoint",
    "entrypoint_sha256",
    "measurement_contract",
    "outcome_classifier",
    "required_artifact_roles",
}
MEASUREMENT_CONTRACT_FIELDS = {
    "name",
    "unit",
    "value_type",
    "supported_value",
}
OUTCOME_CLASSIFIER_FIELDS = {
    "protocol",
    "allowed_instance_outcomes",
    "precedence",
}
PREREGISTRATION_SOLVER_FIELDS = {"name", "versions", "algorithm"}
PREREGISTRATION_CURVE_FIELDS = {
    "id",
    "field_p",
    "curve_a",
    "curve_b",
    "base_order",
    "base_point",
    "cofactor",
}
PREREGISTRATION_INSTANCE_FIELDS = {
    "curve_id",
    "m",
    "factor_base_sizes",
    "presentations",
}
OUTCOME_FIELDS = {
    "schema_version",
    "event_id",
    "recorded_on",
    "candidate_id",
    "hypothesis_id",
    "route_id",
    "outcome",
    "scope",
    "summary",
    "evidence_files",
    "validation",
    "budget",
    "stop_condition",
    "residual_uncertainty",
    "reopening_condition",
    "provenance",
}
SCOPE_FIELDS = {
    "target_kind",
    "curve_family",
    "field_bits",
    "threat_model",
    "claim_boundary",
}
VALIDATION_FIELDS = {
    "status",
    "independence",
    "decisive_claim_validated",
    "evidence_files",
}
INDEPENDENCE_FIELDS = {
    "path",
    "artifact",
    "source",
    "source_review_id",
}
BUDGET_FIELDS = {
    "status",
    "wall_time_seconds",
    "peak_memory_bytes",
    "parallel_workers",
}
STOP_FIELDS = {"triggered", "statement"}
PROVENANCE_FIELDS = {
    "source_kind",
    "source_commit",
    "migration_note",
    "run_manifest",
    "run_manifest_sha256",
}
RETROSPECTIVE_FIELDS = {
    "id",
    "outcome_event_id",
    "candidate_id",
    "hypothesis_id",
    "route_id",
    "event_sha256",
    "known_outcome",
    "hard_rejections",
    "expected_selector_disposition",
}
RUN_MANIFEST_FIELDS = {
    "schema_version",
    "run_id",
    "candidate_id",
    "source_commit",
    "candidate_policy_sha256",
    "preregistration_sha256",
    "candidate_run_manifest",
    "candidate_run_manifest_sha256",
    "executed_instances",
    "completion",
    "result_artifacts",
    "validation_artifacts",
}
RUN_INSTANCE_KEY_FIELDS = {
    "curve_id",
    "m",
    "factor_base_size",
    "presentation",
    "seed",
}
RUN_INSTANCE_FIELDS = RUN_INSTANCE_KEY_FIELDS | {
    "result_record",
    "result_sha256",
    "validation_record",
    "validation_sha256",
}
RUN_COMPLETION_FIELDS = {"status", "reason"}
RUN_ARTIFACT_FIELDS = {"path", "sha256", "role"}
RUN_VALIDATION_ARTIFACT_FIELDS = {
    "path",
    "sha256",
    "role",
    "validator_id",
    "independent",
    "decisive_claim",
}
EXTERNAL_BOUNDED_MANIFEST_FIELDS = {
    "schema_version",
    "run_id",
    "authorization_id",
    "authorization_source_commit",
    "hypothesis_id",
    "bindings",
    "chronology",
}
EXTERNAL_BOUNDED_BINDING_FILES = {
    "preregistration": "PREREGISTRATION.md",
    "curve_table": "curve_table.json",
    "experiment_config": "experiment_config.json",
    "run_py": "run.py",
    "validate_py": "validate.py",
}
INSTANCE_RESULT_FIELDS = {
    "schema_version",
    "result_id",
    "run_id",
    "candidate_id",
    "source_commit",
    "instance",
    "status",
    "decisive_measurement",
    "artifacts",
}
DECISIVE_MEASUREMENT_FIELDS = {"name", "value", "unit"}
INSTANCE_VALIDATION_FIELDS = {
    "schema_version",
    "validation_id",
    "run_id",
    "candidate_id",
    "source_commit",
    "result_record",
    "result_sha256",
    "validator_entrypoint",
    "validator_entrypoint_sha256",
    "validator_protocol",
    "validator_request",
    "validator_request_sha256",
    "validator_output",
    "validator_output_sha256",
    "independent",
    "shares_decisive_logic",
    "passed",
    "recomputed_measurement",
    "artifacts",
}
VALIDATOR_REQUEST_FIELDS = {
    "schema_version",
    "run_id",
    "candidate_id",
    "source_commit",
    "instance",
    "measurement_contract",
    "artifacts",
}
VALIDATOR_REQUEST_MEASUREMENT_FIELDS = {"name", "unit", "value_type"}
VALIDATOR_OUTPUT_FIELDS = {
    "schema_version",
    "validator_request_sha256",
    "passed",
    "recomputed_measurement",
}
HISTORICAL_SCOPE_GUARD_FIELDS = {
    "event_id",
    "event_sha256",
    "outcome",
    "curve_family",
    "field_bits",
    "forbidden_field_bits",
}
HISTORICAL_BASELINE_FIELDS = {"status", "anchor_sha256", "events"}
HISTORICAL_BASELINE_EVENT_FIELDS = {"event_id", "event_sha256"}
HISTORICAL_BASELINE_EVENT_IDS = {
    f"REO-2026-07-24-{index:03d}" for index in range(1, 9)
}
# This code anchor makes a historical relabel require an explicit validator-code
# change, rather than a coordinated metadata edit to an event and its policy digest.
V0_REVIEWED_HISTORICAL_ROOT_SHA256 = (
    "d9de2351a499d395d09005199aac73744c1bf212ff9759ceed5d229d076ca7a3"
)
# The original six candidates are retained only as reviewed regression fixtures.
# This code anchor prevents an author from editing their self-declared scientific
# gates and updating the adjacent policy digest in the same metadata-only change.
V0_REVIEWED_CANDIDATE_SET_SHA256 = (
    "65f795672caddeab1a19073beaabfd31dcad55fc85e623dcacea0570fc49c182"
)
RETROSPECTIVE_CASE_IDS = {
    "RET-P0-PAIR-ENUMERATION",
    "RET-P2-WARD-EDS",
    "RET-P3-M3-PROXY",
    "RET-P4-COMPOSED-APPROXIMATION",
}
HISTORICAL_SCOPE_GUARD_EVENT_IDS = {
    "REO-2026-07-24-001",
    "REO-2026-07-24-008",
}
EVENT_ID = re.compile(r"^REO-\d{4}-\d{2}-\d{2}-\d{3}$")
RUN_ID = re.compile(r"^RER-\d{4}-\d{2}-\d{2}-\d{3}$")
COMMIT_ID = re.compile(r"^[0-9a-f]{40}$")
HASH_ID = re.compile(r"^[0-9a-f]{64}$")
VALIDATOR_ARTIFACT_PATH = re.compile(
    r"^inputs/artifact-\d{3}(?:\.[A-Za-z0-9]+)?$"
)
VALIDATOR_PROTOCOL = "python-pure-json-v3"
OUTCOME_CLASSIFIER_PROTOCOL = "exact-instance-outcome-v1"
EMPIRICAL_OUTCOMES = {
    "supported",
    "falsified",
    "bounded_negative",
    "inapplicable",
    "inconclusive",
    "resource_exhausted",
}
PREDICTIVE_OUTCOMES = EMPIRICAL_OUTCOMES | {"proved"}
HISTORICAL_ONLY_OUTCOMES = {"historical_structural_confirmation"}
PURE_VALIDATOR_MAX_SOURCE_BYTES = 65_536
PURE_VALIDATOR_MAX_ARTIFACT_BYTES = 4 * 1024 * 1024
PURE_VALIDATOR_MAX_ARTIFACT_ROLES = 8
PURE_VALIDATOR_BUILTINS = {
    "abs": abs,
    "bool": bool,
    "float": float,
    "int": int,
    "len": len,
    "max": max,
    "min": min,
    "round": round,
    "str": str,
}
PURE_VALIDATOR_ALLOWED_NODES = {
    ast.Module,
    ast.FunctionDef,
    ast.arguments,
    ast.arg,
    ast.Return,
    ast.Assign,
    ast.AnnAssign,
    ast.If,
    ast.Expr,
    ast.Pass,
    ast.Name,
    ast.Load,
    ast.Store,
    ast.Constant,
    ast.Dict,
    ast.List,
    ast.Tuple,
    ast.Set,
    ast.Subscript,
    ast.Slice,
    ast.Compare,
    ast.BoolOp,
    ast.BinOp,
    ast.UnaryOp,
    ast.IfExp,
    ast.Call,
    ast.keyword,
    ast.And,
    ast.Or,
    ast.Not,
    ast.UAdd,
    ast.USub,
    ast.Add,
    ast.Sub,
    ast.Div,
    ast.FloorDiv,
    ast.Mod,
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
    ast.In,
    ast.NotIn,
    ast.Is,
    ast.IsNot,
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_json(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("ascii")).hexdigest()


def git_json(commit: str, relative: str) -> dict[str, Any] | None:
    payload = git_file_bytes(commit, relative)
    if payload is None:
        return None
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def authorized_git_file_bytes(commit: Any, relative: Any) -> bytes | None:
    """Read a file from an exact decision-authorized commit.

    External bounded decision runs are deliberately outside the native Engine
    provenance policy.  Their source commit is instead pinned by the decision
    substrate, so reproducibility here means that the pinned commit resolves
    and contains the exact authorization-bound bytes.
    """

    if (
        not isinstance(commit, str)
        or not COMMIT_ID.fullmatch(commit)
        or not git_commit_exists(commit)
        or not isinstance(relative, str)
        or not relative
    ):
        return None
    relative_path = Path(relative)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        return None
    completed = subprocess.run(
        ["git", "show", f"{commit}:{relative_path.as_posix()}"],
        cwd=ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    return completed.stdout if completed.returncode == 0 else None


def repo_file(relative: Any) -> Path | None:
    if not isinstance(relative, str) or not relative:
        return None
    candidate = (ROOT / relative).resolve()
    try:
        candidate.relative_to(ROOT.resolve())
    except ValueError:
        return None
    return candidate if candidate.is_file() else None


def scientific_validator_entrypoint(relative: Any) -> Path | None:
    """Resolve only native scientific validators, never framework fixtures."""
    candidate = repo_file(relative)
    if candidate is None or candidate.suffix.lower() != ".py":
        return None
    try:
        candidate.relative_to(SCIENTIFIC_VALIDATORS_DIR.resolve())
    except ValueError:
        return None
    return candidate


def content_sha256(payload: bytes) -> str:
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError:
        canonical = payload
    else:
        canonical = text.replace("\r\n", "\n").replace("\r", "\n").encode(
            "utf-8"
        )
    return hashlib.sha256(canonical).hexdigest()


def file_sha256(path: Path) -> str:
    return content_sha256(path.read_bytes())


def exact_file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expanded_preregistration_matrix(candidate: dict[str, Any]) -> list[dict[str, Any]]:
    """Expand the frozen matrix in deterministic policy order."""
    preregistration = candidate["preregistration"]
    return [
        {
            "curve_id": instance["curve_id"],
            "m": instance["m"],
            "factor_base_size": factor_base_size,
            "presentation": presentation,
            "seed": seed,
        }
        for instance in preregistration["instances"]
        for factor_base_size in instance["factor_base_sizes"]
        for presentation in instance["presentations"]
        for seed in preregistration["seeds"]
    ]


def build_validator_request(
    result_record: dict[str, Any],
    validator_contract: dict[str, Any],
) -> dict[str, Any]:
    """Build a replay request only from preregistered metric and artifact roles."""
    required_roles = set(validator_contract["required_artifact_roles"])
    measurement_contract = validator_contract["measurement_contract"]
    artifacts = []
    selected_artifacts = [
        artifact
        for artifact in result_record["artifacts"]
        if artifact["role"] in required_roles
    ]
    for index, artifact in enumerate(selected_artifacts):
        suffix = Path(artifact["path"]).suffix.lower()
        artifacts.append(
            {
                "path": f"inputs/artifact-{index:03d}{suffix}",
                "sha256": artifact["sha256"],
                "role": artifact["role"],
            }
        )
    return {
        "schema_version": 1,
        "run_id": result_record["run_id"],
        "candidate_id": result_record["candidate_id"],
        "source_commit": result_record["source_commit"],
        "instance": result_record["instance"],
        "measurement_contract": {
            "name": measurement_contract["name"],
            "unit": measurement_contract["unit"],
            "value_type": measurement_contract["value_type"],
        },
        "artifacts": artifacts,
    }


def validate_pure_validator_source(payload: bytes) -> list[str]:
    """Reject every capability outside the small deterministic v3 language."""
    if len(payload) > PURE_VALIDATOR_MAX_SOURCE_BYTES:
        return [
            "pure validator source exceeds "
            f"{PURE_VALIDATOR_MAX_SOURCE_BYTES} bytes"
        ]
    try:
        source = payload.decode("utf-8")
    except UnicodeDecodeError:
        return ["pure validator source must be UTF-8"]
    try:
        tree = ast.parse(source, mode="exec")
    except SyntaxError as error:
        return [f"pure validator source is invalid Python: {error}"]

    problems: list[str] = []
    functions = [
        node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
    ]
    if len(tree.body) != 1 or len(functions) != 1:
        problems.append("pure validator must contain exactly one function")
        return problems
    function = functions[0]
    if function.name != "validate":
        problems.append("pure validator function must be named validate")
    if function.decorator_list:
        problems.append("pure validator cannot use decorators")
    arguments = function.args
    if (
        [argument.arg for argument in arguments.args] != ["request", "artifacts"]
        or arguments.posonlyargs
        or arguments.kwonlyargs
        or arguments.vararg is not None
        or arguments.kwarg is not None
        or arguments.defaults
        or arguments.kw_defaults
    ):
        problems.append(
            "pure validator signature must be validate(request, artifacts)"
        )

    loaded_names = {
        node.id
        for node in ast.walk(function)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
    }
    for required_name in ("request", "artifacts"):
        if required_name not in loaded_names:
            problems.append(
                f"pure validator must inspect {required_name}"
            )
    if not any(isinstance(node, ast.Compare) for node in ast.walk(function)):
        problems.append("pure validator must contain a comparison")

    for node in ast.walk(tree):
        if type(node) not in PURE_VALIDATOR_ALLOWED_NODES:
            problems.append(
                f"pure validator syntax {type(node).__name__} is forbidden"
            )
            continue
        if isinstance(node, ast.Call):
            if (
                not isinstance(node.func, ast.Name)
                or node.func.id not in PURE_VALIDATOR_BUILTINS
            ):
                problems.append("pure validator call target is forbidden")
        if isinstance(node, ast.Name) and node.id.startswith("__"):
            problems.append("pure validator dunder names are forbidden")
    return sorted(set(problems))


def execute_pure_validator(
    payload: bytes,
    request: dict[str, Any],
    artifacts: dict[str, list[Any]],
) -> tuple[Any | None, list[str]]:
    problems = validate_pure_validator_source(payload)
    if problems:
        return None, problems
    namespace: dict[str, Any] = {
        "__builtins__": dict(PURE_VALIDATOR_BUILTINS),
    }
    try:
        exec(
            compile(payload.decode("utf-8"), "<pure-validator>", "exec"),
            namespace,
            namespace,
        )
        value = namespace["validate"](
            copy.deepcopy(request),
            copy.deepcopy(artifacts),
        )
    except Exception as error:
        return None, [f"pure validator execution failed: {error}"]
    return value, []


def measurement_value_matches_type(value: Any, value_type: Any) -> bool:
    if value_type == "boolean":
        return isinstance(value, bool)
    if value_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if value_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if value_type == "string":
        return isinstance(value, str)
    return False


def aggregate_instance_outcomes(
    values: list[Any],
    outcome_classifier: dict[str, Any],
) -> str | None:
    """Derive one terminal outcome from the frozen per-instance classifications."""
    allowed = set(outcome_classifier.get("allowed_instance_outcomes", []))
    if not values or any(value not in allowed for value in values):
        return None
    for outcome in outcome_classifier.get("precedence", []):
        if outcome in values:
            return outcome
    return None


def validate_engine_run_manifest(
    manifest_path: Path,
    event: dict[str, Any],
    candidate: dict[str, Any],
    policy: dict[str, Any],
    decisions: dict[str, Any],
    ready_candidate_ids: set[str],
) -> list[str]:
    """Bind one terminal event to its exact run matrix and artifact digests."""
    problems: list[str] = []
    label = manifest_path.name
    try:
        manifest_path.resolve().relative_to(RUNS_DIR.resolve())
    except ValueError:
        problems.append(f"{label}: native run manifest must live under experiments/engine/runs")
    try:
        manifest = load_json(manifest_path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return [f"{label}: invalid native run manifest: {error}"]
    if not _exact_keys(manifest, RUN_MANIFEST_FIELDS, label, problems):
        return problems
    if manifest.get("schema_version") != 1:
        problems.append(f"{label}: schema_version must be 1")
    run_id = manifest.get("run_id")
    if not isinstance(run_id, str) or not RUN_ID.fullmatch(run_id):
        problems.append(f"{label}: invalid run_id")
    else:
        if manifest_path.stem != run_id:
            problems.append(f"{label}: filename must equal run_id")
        if run_id[4:14] != event.get("recorded_on"):
            problems.append(f"{label}: run date must equal outcome event date")
    if manifest.get("candidate_id") != event.get("candidate_id"):
        problems.append(f"{label}: candidate_id differs from outcome event")
    source_commit = manifest.get("source_commit")
    if source_commit != event.get("provenance", {}).get("source_commit"):
        problems.append(f"{label}: source_commit differs from outcome event")
    if not scientific_source_commit_allowed(source_commit):
        problems.append(
            f"{label}: source_commit is not reproducible from protected main "
            "or a registered immutable evidence ref"
        )
    expected_candidate_hash = sha256_json(candidate)
    if manifest.get("candidate_policy_sha256") != expected_candidate_hash:
        problems.append(f"{label}: candidate_policy_sha256 is stale or incorrect")
    expected_preregistration_hash = sha256_json(candidate["preregistration"])
    if manifest.get("preregistration_sha256") != expected_preregistration_hash:
        problems.append(f"{label}: preregistration_sha256 is stale or incorrect")
    source_policy = git_json(source_commit, "repo/RESEARCH_ENGINE_V0.json")
    if source_policy is None:
        problems.append(
            f"{label}: source_commit does not contain RESEARCH_ENGINE_V0.json"
        )
    else:
        source_candidate = next(
            (
                item
                for item in source_policy.get("candidate_proposals", [])
                if item.get("id") == event.get("candidate_id")
            ),
            None,
        )
        if source_candidate is None:
            problems.append(
                f"{label}: source_commit does not contain the candidate policy"
            )
        else:
            if sha256_json(source_candidate) != manifest.get(
                "candidate_policy_sha256"
            ):
                problems.append(
                    f"{label}: source_commit candidate policy differs from run envelope"
                )
            if sha256_json(source_candidate.get("preregistration")) != (
                manifest.get("preregistration_sha256")
            ):
                problems.append(
                    f"{label}: source_commit preregistration differs from run envelope"
                )

    expected_matrix = expanded_preregistration_matrix(candidate)
    executed = manifest.get("executed_instances")
    if (
        not isinstance(executed, list)
        or not executed
        or len(executed) > len(expected_matrix)
    ):
        problems.append(f"{label}: executed_instances must be a nonempty matrix prefix")
        executed = []
    else:
        for index, instance in enumerate(executed):
            _exact_keys(
                instance,
                RUN_INSTANCE_FIELDS,
                f"{label}.executed_instances[{index}]",
                problems,
            )
        executed_keys = [
            {
                key: instance.get(key)
                for key in RUN_INSTANCE_KEY_FIELDS
            }
            for instance in executed
        ]
        if executed_keys != expected_matrix[: len(executed)]:
            problems.append(
                f"{label}: executed_instances must be the exact frozen matrix prefix"
            )
    completion = manifest.get("completion")
    completion_map = completion if isinstance(completion, dict) else {}
    if _exact_keys(
        completion, RUN_COMPLETION_FIELDS, f"{label}.completion", problems
    ):
        status = completion_map.get("status")
        if status not in {"complete", "stopped_early"}:
            problems.append(f"{label}: invalid completion status")
        if not _nonempty_text(completion_map.get("reason")):
            problems.append(f"{label}: completion reason must be nonempty")
        if status == "complete" and (
            len(executed) != len(expected_matrix)
            or [
                {key: instance.get(key) for key in RUN_INSTANCE_KEY_FIELDS}
                for instance in executed
            ]
            != expected_matrix
        ):
            problems.append(f"{label}: complete run must execute the full frozen matrix")
        if status == "stopped_early" and len(executed) >= len(expected_matrix):
            problems.append(f"{label}: stopped_early must be a strict matrix prefix")
        if event.get("outcome") in {
            "proved",
            "supported",
            "bounded_negative",
        } and status != "complete":
            problems.append(
                f"{label}: {event.get('outcome')} requires the complete frozen matrix"
            )

    def validate_artifacts(
        artifacts: Any,
        expected_fields: set[str],
        context: str,
    ) -> list[dict[str, Any]]:
        if not isinstance(artifacts, list) or not artifacts:
            problems.append(f"{label}.{context} must be nonempty")
            return []
        validated: list[dict[str, Any]] = []
        for index, artifact in enumerate(artifacts):
            artifact_label = f"{label}.{context}[{index}]"
            if not _exact_keys(artifact, expected_fields, artifact_label, problems):
                continue
            artifact_path = repo_file(artifact.get("path"))
            if artifact_path is None:
                problems.append(f"{artifact_label}: artifact path is missing")
                continue
            digest = artifact.get("sha256")
            if not isinstance(digest, str) or not HASH_ID.fullmatch(digest):
                problems.append(f"{artifact_label}: invalid sha256")
            elif file_sha256(artifact_path) != digest:
                problems.append(f"{artifact_label}: sha256 mismatch")
            if not _nonempty_text(artifact.get("role")):
                problems.append(f"{artifact_label}: role must be nonempty")
            validated.append(artifact)
        return validated

    instance_result_paths: set[str] = set()
    instance_validation_paths: set[str] = set()
    instance_validation_request_paths: set[str] = set()
    instance_validation_output_paths: set[str] = set()
    result_ids: set[str] = set()
    validation_ids: set[str] = set()
    validator_contract = candidate["preregistration"]["validator_contract"]
    measurement_contract = validator_contract["measurement_contract"]
    outcome_classifier = validator_contract["outcome_classifier"]
    recomputed_values: list[Any] = []
    if validator_contract.get("status") != "implemented":
        problems.append(
            f"{label}: native run requires an implemented preregistered validator"
        )
    for index, instance in enumerate(executed):
        instance_label = f"{label}.executed_instances[{index}]"
        result_relative = instance.get("result_record")
        result_path = repo_file(result_relative)
        if result_path is None:
            problems.append(f"{instance_label}: result_record is missing")
            continue
        try:
            result_path.resolve().relative_to(RUNS_DIR.resolve())
        except ValueError:
            problems.append(
                f"{instance_label}: result_record must live under experiments/engine/runs"
            )
        result_digest = instance.get("result_sha256")
        if (
            not isinstance(result_digest, str)
            or not HASH_ID.fullmatch(result_digest)
            or file_sha256(result_path) != result_digest
        ):
            problems.append(f"{instance_label}: result_sha256 mismatch")
        try:
            result_record = load_json(result_path)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            problems.append(f"{instance_label}: invalid result_record: {error}")
            continue
        if not _exact_keys(
            result_record,
            INSTANCE_RESULT_FIELDS,
            f"{instance_label}.result",
            problems,
        ):
            continue
        result_id = result_record.get("result_id")
        if not _nonempty_text(result_id) or result_id in result_ids:
            problems.append(f"{instance_label}: result_id must be unique and nonempty")
        else:
            result_ids.add(result_id)
        expected_instance = {
            key: instance.get(key) for key in RUN_INSTANCE_KEY_FIELDS
        }
        for field, expected in (
            ("schema_version", 1),
            ("run_id", run_id),
            ("candidate_id", event.get("candidate_id")),
            ("source_commit", source_commit),
            ("instance", expected_instance),
        ):
            if result_record.get(field) != expected:
                problems.append(
                    f"{instance_label}: result {field} differs from run envelope"
                )
        if result_record.get("status") not in {
            "completed",
            "resource_exhausted",
            "inapplicable",
        }:
            problems.append(f"{instance_label}: invalid result status")
        if (
            completion_map.get("status") == "complete"
            and result_record.get("status") != "completed"
        ):
            problems.append(
                f"{instance_label}: complete matrix requires completed results"
            )
        measurement = result_record.get("decisive_measurement")
        measurement_valid = _exact_keys(
            measurement,
            DECISIVE_MEASUREMENT_FIELDS,
            f"{instance_label}.decisive_measurement",
            problems,
        )
        if measurement_valid:
            if not _nonempty_text(measurement.get("name")) or not _nonempty_text(
                measurement.get("unit")
            ):
                problems.append(
                    f"{instance_label}: decisive measurement name/unit must be nonempty"
                )
            if isinstance(measurement.get("value"), (dict, list)):
                problems.append(
                    f"{instance_label}: decisive measurement value must be scalar"
                )
            for field in ("name", "unit"):
                if measurement.get(field) != measurement_contract.get(field):
                    problems.append(
                        f"{instance_label}: decisive measurement {field} differs "
                        "from preregistration"
                    )
            if not measurement_value_matches_type(
                measurement.get("value"),
                measurement_contract.get("value_type"),
            ):
                problems.append(
                    f"{instance_label}: decisive measurement value does not match "
                    "the preregistered type"
                )
        validated_result_artifacts = validate_artifacts(
            result_record.get("artifacts"),
            RUN_ARTIFACT_FIELDS,
            f"instance_result[{index}].artifacts",
        )

        validation_relative = instance.get("validation_record")
        validation_path = repo_file(validation_relative)
        if validation_path is None:
            problems.append(f"{instance_label}: validation_record is missing")
            continue
        try:
            validation_path.resolve().relative_to(RUNS_DIR.resolve())
        except ValueError:
            problems.append(
                f"{instance_label}: validation_record must live under experiments/engine/runs"
            )
        validation_digest = instance.get("validation_sha256")
        if (
            not isinstance(validation_digest, str)
            or not HASH_ID.fullmatch(validation_digest)
            or file_sha256(validation_path) != validation_digest
        ):
            problems.append(f"{instance_label}: validation_sha256 mismatch")
        try:
            validation_record = load_json(validation_path)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            problems.append(f"{instance_label}: invalid validation_record: {error}")
            continue
        if not _exact_keys(
            validation_record,
            INSTANCE_VALIDATION_FIELDS,
            f"{instance_label}.validation",
            problems,
        ):
            continue
        validation_id = validation_record.get("validation_id")
        if not _nonempty_text(validation_id) or validation_id in validation_ids:
            problems.append(
                f"{instance_label}: validation_id must be unique and nonempty"
            )
        else:
            validation_ids.add(validation_id)
        for field, expected in (
            ("schema_version", 1),
            ("run_id", run_id),
            ("candidate_id", event.get("candidate_id")),
            ("source_commit", source_commit),
            ("result_record", result_relative),
            ("result_sha256", result_digest),
        ):
            if validation_record.get(field) != expected:
                problems.append(
                    f"{instance_label}: validation {field} differs from result/run"
                )
        validator_entrypoint = validation_record.get("validator_entrypoint")
        expected_validator_entrypoint = validator_contract.get("entrypoint")
        if validator_entrypoint != expected_validator_entrypoint:
            problems.append(
                f"{instance_label}: validator_entrypoint differs from "
                "preregistration"
            )
        validator_path = scientific_validator_entrypoint(validator_entrypoint)
        source_validator = (
            git_file_bytes(source_commit, validator_entrypoint)
            if _nonempty_text(validator_entrypoint)
            else None
        )
        if source_validator is None:
            problems.append(
                f"{instance_label}: validator_entrypoint is absent at source_commit"
            )
        validator_entrypoint_digest = validation_record.get(
            "validator_entrypoint_sha256"
        )
        if validator_entrypoint_digest != validator_contract.get(
            "entrypoint_sha256"
        ):
            problems.append(
                f"{instance_label}: validator_entrypoint_sha256 differs from "
                "preregistration"
            )
        if (
            not isinstance(validator_entrypoint_digest, str)
            or not HASH_ID.fullmatch(validator_entrypoint_digest)
        ):
            problems.append(
                f"{instance_label}: validator_entrypoint_sha256 is invalid"
            )
        elif (
            source_validator is not None
            and content_sha256(source_validator) != validator_entrypoint_digest
        ):
            problems.append(
                f"{instance_label}: validator_entrypoint_sha256 differs from "
                "source_commit"
            )
        validator_path_matches_source = (
            validator_path is not None
            and validator_path.suffix.lower() == ".py"
            and isinstance(validator_entrypoint_digest, str)
            and HASH_ID.fullmatch(validator_entrypoint_digest) is not None
            and file_sha256(validator_path) == validator_entrypoint_digest
        )
        if not validator_path_matches_source:
            problems.append(
                f"{instance_label}: replayed validator must be the exact "
                "preregistered pure entrypoint from source_commit under "
                "experiments/engine/validators/"
            )
        if source_validator is not None:
            for validator_problem in validate_pure_validator_source(
                source_validator
            ):
                problems.append(
                    f"{instance_label}: {validator_problem}"
                )
        if validation_record.get("validator_protocol") != VALIDATOR_PROTOCOL:
            problems.append(
                f"{instance_label}: validator_protocol must be {VALIDATOR_PROTOCOL}"
            )

        expected_validator_request: dict[str, Any] | None = None
        result_artifacts = result_record.get("artifacts")
        required_artifact_roles = set(
            validator_contract.get("required_artifact_roles", [])
        )
        observed_required_role_counts = Counter(
            artifact.get("role")
            for artifact in validated_result_artifacts
            if artifact.get("role") in required_artifact_roles
        )
        if (
            set(observed_required_role_counts) != required_artifact_roles
            or any(
                count != 1
                for count in observed_required_role_counts.values()
            )
        ):
            problems.append(
                f"{instance_label}: result artifacts must contain exactly one "
                "JSON document for each preregistered validator role"
            )
        for artifact in validated_result_artifacts:
            if (
                artifact.get("role") in required_artifact_roles
                and Path(artifact["path"]).suffix.lower() != ".json"
            ):
                problems.append(
                    f"{instance_label}: pure validator inputs must be JSON artifacts"
                )
        if (
            measurement_valid
            and isinstance(result_digest, str)
            and HASH_ID.fullmatch(result_digest)
            and isinstance(result_artifacts, list)
            and len(validated_result_artifacts) == len(result_artifacts)
        ):
            expected_validator_request = build_validator_request(
                result_record,
                validator_contract,
            )

        validator_request_relative = validation_record.get("validator_request")
        validator_request_path = repo_file(validator_request_relative)
        stored_validator_request: dict[str, Any] | None = None
        if validator_request_path is None:
            problems.append(f"{instance_label}: validator_request is missing")
        else:
            try:
                validator_request_path.resolve().relative_to(RUNS_DIR.resolve())
            except ValueError:
                problems.append(
                    f"{instance_label}: validator_request must live under "
                    "experiments/engine/runs"
                )
            validator_request_digest = validation_record.get(
                "validator_request_sha256"
            )
            if (
                not isinstance(validator_request_digest, str)
                or not HASH_ID.fullmatch(validator_request_digest)
                or file_sha256(validator_request_path) != validator_request_digest
            ):
                problems.append(
                    f"{instance_label}: validator_request_sha256 mismatch"
                )
            try:
                stored_validator_request = load_json(validator_request_path)
            except (OSError, ValueError, json.JSONDecodeError) as error:
                problems.append(
                    f"{instance_label}: invalid validator_request: {error}"
                )
            if stored_validator_request is not None and _exact_keys(
                stored_validator_request,
                VALIDATOR_REQUEST_FIELDS,
                f"{instance_label}.validator_request",
                problems,
            ):
                _exact_keys(
                    stored_validator_request.get("measurement_contract"),
                    VALIDATOR_REQUEST_MEASUREMENT_FIELDS,
                    f"{instance_label}.validator_request.measurement_contract",
                    problems,
                )
                request_artifacts = stored_validator_request.get("artifacts")
                if not isinstance(request_artifacts, list) or not request_artifacts:
                    problems.append(
                        f"{instance_label}: validator_request.artifacts must "
                        "be nonempty"
                    )
                else:
                    for artifact_index, artifact in enumerate(request_artifacts):
                        if _exact_keys(
                            artifact,
                            RUN_ARTIFACT_FIELDS,
                            f"{instance_label}.validator_request.artifacts"
                            f"[{artifact_index}]",
                            problems,
                        ) and (
                            not isinstance(artifact.get("path"), str)
                            or VALIDATOR_ARTIFACT_PATH.fullmatch(
                                artifact["path"]
                            )
                            is None
                        ):
                            problems.append(
                                f"{instance_label}: validator request artifact "
                                f"path {artifact.get('path')!r} is not isolated"
                            )
                if (
                    expected_validator_request is not None
                    and stored_validator_request != expected_validator_request
                ):
                    problems.append(
                        f"{instance_label}: validator_request must be the exact "
                        "sanitized request derived from result metadata"
                    )

        validator_output_relative = validation_record.get("validator_output")
        validator_output_path = repo_file(validator_output_relative)
        stored_validator_output: dict[str, Any] | None = None
        if validator_output_path is None:
            problems.append(f"{instance_label}: validator_output is missing")
        else:
            try:
                validator_output_path.resolve().relative_to(RUNS_DIR.resolve())
            except ValueError:
                problems.append(
                    f"{instance_label}: validator_output must live under "
                    "experiments/engine/runs"
                )
            validator_output_digest = validation_record.get(
                "validator_output_sha256"
            )
            if (
                not isinstance(validator_output_digest, str)
                or not HASH_ID.fullmatch(validator_output_digest)
                or file_sha256(validator_output_path) != validator_output_digest
            ):
                problems.append(
                    f"{instance_label}: validator_output_sha256 mismatch"
                )
            try:
                stored_validator_output = load_json(validator_output_path)
            except (OSError, ValueError, json.JSONDecodeError) as error:
                problems.append(
                    f"{instance_label}: invalid validator_output: {error}"
                )
            if stored_validator_output is not None and _exact_keys(
                stored_validator_output,
                VALIDATOR_OUTPUT_FIELDS,
                f"{instance_label}.validator_output",
                problems,
            ):
                for field, expected in (
                    ("schema_version", 1),
                    (
                        "validator_request_sha256",
                        validation_record.get("validator_request_sha256"),
                    ),
                    ("passed", True),
                    ("recomputed_measurement", measurement),
                ):
                    if stored_validator_output.get(field) != expected:
                        problems.append(
                            f"{instance_label}: stored validator output {field} "
                            "differs from the result"
                        )

        replayed_validator_output: dict[str, Any] | None = None
        source_validator_matches = (
            source_validator is not None
            and isinstance(validator_entrypoint_digest, str)
            and HASH_ID.fullmatch(validator_entrypoint_digest) is not None
            and content_sha256(source_validator) == validator_entrypoint_digest
        )
        if (
            validator_path_matches_source
            and source_validator_matches
            and stored_validator_request is not None
            and stored_validator_request == expected_validator_request
            and validation_record.get("validator_protocol")
            == VALIDATOR_PROTOCOL
        ):
            artifact_documents: dict[str, list[Any]] = defaultdict(list)
            replay_inputs_ready = True
            for source_artifact in result_artifacts:
                role = source_artifact.get("role")
                if role not in required_artifact_roles:
                    continue
                source_artifact_path = repo_file(source_artifact.get("path"))
                if source_artifact_path is None:
                    problems.append(
                        f"{instance_label}: validator replay source artifact "
                        "is missing"
                    )
                    replay_inputs_ready = False
                    continue
                if (
                    source_artifact_path.stat().st_size
                    > PURE_VALIDATOR_MAX_ARTIFACT_BYTES
                ):
                    problems.append(
                        f"{instance_label}: validator input exceeds "
                        f"{PURE_VALIDATOR_MAX_ARTIFACT_BYTES} bytes"
                    )
                    replay_inputs_ready = False
                    continue
                try:
                    artifact_document = load_json(source_artifact_path)
                except (OSError, ValueError, json.JSONDecodeError) as error:
                    problems.append(
                        f"{instance_label}: validator input is not valid JSON: "
                        f"{error}"
                    )
                    replay_inputs_ready = False
                    continue
                artifact_documents[role].append(artifact_document)

            if replay_inputs_ready:
                recomputed_value, replay_problems = execute_pure_validator(
                    source_validator,
                    stored_validator_request,
                    dict(artifact_documents),
                )
                for replay_problem in replay_problems:
                    problems.append(
                        f"{instance_label}: {replay_problem}"
                    )
                if not replay_problems:
                    if not measurement_value_matches_type(
                        recomputed_value,
                        measurement_contract["value_type"],
                    ):
                        problems.append(
                            f"{instance_label}: pure validator returned the wrong "
                            "measurement type"
                        )
                    else:
                        recomputed_values.append(recomputed_value)
                        if recomputed_value not in set(
                            outcome_classifier["allowed_instance_outcomes"]
                        ):
                            problems.append(
                                f"{instance_label}: pure validator returned a "
                                "classification outside the preregistered taxonomy"
                            )
                        result_status = result_record.get("status")
                        if (
                            result_status in {"resource_exhausted", "inapplicable"}
                            and recomputed_value != result_status
                        ):
                            problems.append(
                                f"{instance_label}: result status {result_status!r} "
                                "differs from the recomputed classification"
                            )
                        if (
                            result_status == "completed"
                            and recomputed_value
                            in {"resource_exhausted", "inapplicable"}
                        ):
                            problems.append(
                                f"{instance_label}: completed result conflicts with "
                                f"recomputed {recomputed_value!r}"
                            )
                        replayed_validator_output = {
                            "schema_version": 1,
                            "validator_request_sha256": validation_record.get(
                                "validator_request_sha256"
                            ),
                            "passed": True,
                            "recomputed_measurement": {
                                "name": measurement_contract["name"],
                                "value": recomputed_value,
                                "unit": measurement_contract["unit"],
                            },
                        }
        if (
            stored_validator_output is not None
            and replayed_validator_output is not None
            and stored_validator_output != replayed_validator_output
        ):
            problems.append(
                f"{instance_label}: stored validator output differs from replay"
            )
        if replayed_validator_output is not None:
            for field, expected in (
                ("schema_version", 1),
                (
                    "validator_request_sha256",
                    validation_record.get("validator_request_sha256"),
                ),
                ("passed", True),
                ("recomputed_measurement", measurement),
            ):
                if replayed_validator_output.get(field) != expected:
                    problems.append(
                        f"{instance_label}: replayed validator output {field} "
                        "differs from the result"
                    )
        if validation_record.get("independent") is not True:
            problems.append(
                f"{instance_label}: validation must be independently implemented"
            )
        if validation_record.get("shares_decisive_logic") is not False:
            problems.append(
                f"{instance_label}: validator must not share decisive logic"
            )
        if validation_record.get("passed") is not True:
            problems.append(f"{instance_label}: per-instance validation must pass")
        if validation_record.get("recomputed_measurement") != measurement:
            problems.append(
                f"{instance_label}: validator measurement differs from result"
            )
        validate_artifacts(
            validation_record.get("artifacts"),
            RUN_ARTIFACT_FIELDS,
            f"instance_validation[{index}].artifacts",
        )
        instance_result_paths.add(result_relative)
        instance_validation_paths.add(validation_relative)
        if validator_request_path is not None:
            instance_validation_request_paths.add(validator_request_relative)
        if validator_output_path is not None:
            instance_validation_output_paths.add(validator_output_relative)

    if len(recomputed_values) == len(executed) and recomputed_values:
        classified_outcome = aggregate_instance_outcomes(
            recomputed_values,
            outcome_classifier,
        )
        if classified_outcome is None:
            problems.append(
                f"{label}: preregistered aggregate classifier could not classify "
                "the recomputed instance outcomes"
            )
        elif event.get("outcome") != classified_outcome:
            problems.append(
                f"{label}: event outcome {event.get('outcome')!r} differs from "
                "the preregistered aggregate classifier result "
                f"{classified_outcome!r}"
            )

    if not instance_result_paths <= set(event.get("evidence_files", [])):
        problems.append(
            f"{label}: every per-instance result must be cited by the outcome"
        )
    if not instance_validation_paths <= set(
        event.get("validation", {}).get("evidence_files", [])
    ):
        problems.append(
            f"{label}: every per-instance validation must be cited by the outcome"
        )
    if not instance_validation_request_paths <= set(
        event.get("validation", {}).get("evidence_files", [])
    ):
        problems.append(
            f"{label}: every sanitized validator request must be cited by the outcome"
        )
    if not instance_validation_output_paths <= set(
        event.get("validation", {}).get("evidence_files", [])
    ):
        problems.append(
            f"{label}: every replayed validator output must be cited by the outcome"
        )

    result_artifacts = validate_artifacts(
        manifest.get("result_artifacts"),
        RUN_ARTIFACT_FIELDS,
        "result_artifacts",
    )
    validation_artifacts = validate_artifacts(
        manifest.get("validation_artifacts"),
        RUN_VALIDATION_ARTIFACT_FIELDS,
        "validation_artifacts",
    )
    for artifact in validation_artifacts:
        if not _nonempty_text(artifact.get("validator_id")):
            problems.append(f"{label}: validation artifact needs validator_id")
        for field in ("independent", "decisive_claim"):
            if not isinstance(artifact.get(field), bool):
                problems.append(
                    f"{label}: validation artifact {field} must be boolean"
                )
    decisive_paths = {
        artifact["path"]
        for artifact in validation_artifacts
        if artifact.get("independent") is True
        and artifact.get("decisive_claim") is True
    }
    if event.get("outcome") in {
        "proved",
        "supported",
        "falsified",
        "bounded_negative",
    } and not decisive_paths:
        problems.append(
            f"{label}: terminal scientific outcome needs an independent decisive artifact"
        )
    if not {artifact["path"] for artifact in result_artifacts} <= set(
        event.get("evidence_files", [])
    ):
        problems.append(f"{label}: result artifacts must be cited by the outcome event")
    if not decisive_paths <= set(
        event.get("validation", {}).get("evidence_files", [])
    ):
        problems.append(
            f"{label}: decisive artifacts must be cited by outcome validation"
        )

    candidate_manifest_relative = manifest.get("candidate_run_manifest")
    candidate_manifest_path = repo_file(candidate_manifest_relative)
    if candidate_manifest_path is None:
        problems.append(f"{label}: candidate_run_manifest is missing")
        return problems
    try:
        candidate_manifest_path.resolve().relative_to(RUNS_DIR.resolve())
    except ValueError:
        problems.append(
            f"{label}: candidate_run_manifest must live under experiments/engine/runs"
        )
    candidate_manifest_hash = manifest.get("candidate_run_manifest_sha256")
    if (
        not isinstance(candidate_manifest_hash, str)
        or not HASH_ID.fullmatch(candidate_manifest_hash)
        or file_sha256(candidate_manifest_path) != candidate_manifest_hash
    ):
        problems.append(f"{label}: candidate_run_manifest_sha256 mismatch")
    framework_dir = ROOT / "experiments" / "framework"
    if str(framework_dir) not in sys.path:
        sys.path.insert(0, str(framework_dir))
    from candidate_contract import load_record, validate_record

    try:
        candidate_record = load_record(candidate_manifest_path)
    except (OSError, ValueError) as error:
        problems.append(f"{label}: invalid candidate run manifest: {error}")
        return problems
    for error in validate_record(
        candidate_record,
        decisions,
        engine_policy=policy,
        engine_state={
            "execution_queue": {
                "ready_candidate_ids": sorted(ready_candidate_ids),
                "terminal_candidate_ids": [],
            }
        },
        authorized_candidate_ids=ready_candidate_ids,
    ):
        problems.append(f"{label}: candidate run: {error}")
    record_candidate = candidate_record.get("candidate", {})
    if record_candidate.get("id") != event.get("candidate_id"):
        problems.append(f"{label}: candidate run id differs from outcome")
    if record_candidate.get("code_commit") != source_commit:
        problems.append(f"{label}: candidate run commit differs from run envelope")
    producer_entrypoint = record_candidate.get("entrypoint")
    validator_entrypoint = validator_contract.get("entrypoint")
    if producer_entrypoint == validator_entrypoint:
        problems.append(
            f"{label}: producer and validator entrypoints must be distinct"
        )
    producer_source = (
        git_file_bytes(source_commit, producer_entrypoint)
        if _nonempty_text(producer_entrypoint)
        else None
    )
    if producer_source is None:
        problems.append(
            f"{label}: candidate producer entrypoint is absent at source_commit"
        )
    elif (
        isinstance(validator_contract.get("entrypoint_sha256"), str)
        and content_sha256(producer_source)
        == validator_contract["entrypoint_sha256"]
    ):
        problems.append(
            f"{label}: producer and validator source must be independently "
            "implemented"
        )
    if executed:
        record_target = candidate_record.get("target", {})
        record_provenance = candidate_record.get("provenance", {})
        if record_target.get("curve_id") != executed[0].get("curve_id"):
            problems.append(
                f"{label}: candidate run target must match the first executed instance"
            )
        if record_provenance.get("seed") != executed[0].get("seed"):
            problems.append(
                f"{label}: candidate run seed must match the first executed instance"
            )
        curve_index = {
            curve["id"]: curve
            for curve in candidate["preregistration"]["curves"]
        }
        actual_bits = sorted(
            {
                curve_index[instance["curve_id"]]["field_p"].bit_length()
                for instance in executed
                if instance.get("curve_id") in curve_index
            }
        )
        if event.get("scope", {}).get("field_bits") != actual_bits:
            problems.append(
                f"{label}: outcome field_bits must equal executed target bit lengths"
            )
    expected_tool_versions = candidate["preregistration"]["solver"]["versions"]
    observed_tool_versions = candidate_record.get("environment", {}).get(
        "tool_versions"
    )
    if observed_tool_versions != expected_tool_versions:
        problems.append(
            f"{label}: candidate run tool versions differ from preregistration"
        )
    cost_record = candidate_record.get("cost", {})
    online = cost_record.get("online", {})
    offline = cost_record.get("offline", {})
    actual_budget = {
        "wall_time_seconds": online.get("wall_time_seconds", 0)
        + offline.get("wall_time_seconds", 0),
        "peak_memory_bytes": max(
            online.get("peak_memory_bytes", 0),
            offline.get("peak_memory_bytes", 0),
        ),
        "parallel_workers": cost_record.get("parallel_workers"),
    }
    for field, actual in actual_budget.items():
        if event.get("budget", {}).get(field) != actual:
            problems.append(
                f"{label}: outcome budget.{field} differs from candidate run"
            )
    return problems


def parse_hypotheses(path: Path = HYPOTHESES_PATH) -> dict[str, dict[str, str]]:
    """Parse only the stable top-level fields needed for cross-registry checks."""
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(
        r"^  - id: (?P<id>[A-Z0-9][A-Z0-9_-]*)\s*$"
        r"(?P<body>.*?)(?=^  - id: [A-Z0-9][A-Z0-9_-]*\s*$|\Z)",
        flags=re.MULTILINE | re.DOTALL,
    )
    parsed: dict[str, dict[str, str]] = {}
    for match in pattern.finditer(text):
        fields: dict[str, str] = {}
        for name in ("title", "direction", "status", "resume_after"):
            field = re.search(
                rf"^    {name}:\s*(?:\"(?P<quoted>[^\"]*)\"|(?P<plain>.+))$",
                match.group("body"),
                flags=re.MULTILINE,
            )
            if field:
                fields[name] = (field.group("quoted") or field.group("plain")).strip()
        parsed[match.group("id")] = fields
    return parsed


def entropy_bits(probability: float) -> float:
    if probability <= 0.0 or probability >= 1.0:
        return 0.0
    return -(
        probability * math.log2(probability)
        + (1.0 - probability) * math.log2(1.0 - probability)
    )


def expected_information_gain(
    prior_live: float, likelihoods: dict[str, dict[str, float]]
) -> float:
    prior_entropy = entropy_bits(prior_live)
    expected_posterior_entropy = 0.0
    for likelihood in likelihoods.values():
        marginal = (
            prior_live * likelihood["live"]
            + (1.0 - prior_live) * likelihood["dead"]
        )
        if marginal <= 0.0:
            continue
        posterior_live = prior_live * likelihood["live"] / marginal
        expected_posterior_entropy += marginal * entropy_bits(posterior_live)
    return max(0.0, prior_entropy - expected_posterior_entropy)


def predicted_marginal(
    prior_live: float, likelihoods: dict[str, dict[str, float]]
) -> dict[str, float]:
    return {
        outcome: (
            prior_live * likelihood["live"]
            + (1.0 - prior_live) * likelihood["dead"]
        )
        for outcome, likelihood in likelihoods.items()
    }


def brier_score(predicted: dict[str, float], actual_outcome: str) -> float:
    return sum(
        (
            probability
            - (1.0 if outcome == actual_outcome else 0.0)
        )
        ** 2
        for outcome, probability in predicted.items()
    )


def normalized_budget_cost(
    candidate: dict[str, Any], exploration_limits: dict[str, int]
) -> float:
    budget = candidate["budget"]
    return (
        budget["wall_time_seconds"]
        / exploration_limits["max_wall_time_seconds"]
        + budget["peak_memory_bytes"]
        / exploration_limits["max_peak_memory_bytes"]
        + budget["parallel_workers"]
        / exploration_limits["max_parallel_workers"]
    )


def candidate_value(
    candidate: dict[str, Any], exploration_limits: dict[str, int]
) -> dict[str, float]:
    information_model = candidate["information_model"]
    information_gain = expected_information_gain(
        information_model["prior_live"],
        information_model["likelihoods"],
    )
    budget_cost = normalized_budget_cost(candidate, exploration_limits)
    return {
        "expected_information_gain_bits": round(information_gain, 8),
        "normalized_budget_cost": round(budget_cost, 8),
        "priority_bits_per_cost": round(information_gain / budget_cost, 8),
    }


def rejection_reasons(
    candidate: dict[str, Any],
    primary_threat_model: str | None = None,
) -> list[str]:
    reasons = {
        key for key, value in candidate["hard_rejections"].items() if value is True
    }
    if (
        primary_threat_model is not None
        and candidate.get("scope", {}).get("threat_model")
        != primary_threat_model
    ):
        reasons.add("changes_threat_model")
    validator = candidate.get("preregistration", {}).get(
        "validator_contract", {}
    )
    validator_path = scientific_validator_entrypoint(
        validator.get("entrypoint")
    )
    validator_digest = validator.get("entrypoint_sha256")
    if (
        validator.get("status") != "implemented"
        or validator_path is None
        or not isinstance(validator_digest, str)
        or HASH_ID.fullmatch(validator_digest) is None
        or file_sha256(validator_path) != validator_digest
        or validate_pure_validator_source(validator_path.read_bytes())
    ):
        reasons.add("missing_independent_validator")
    return sorted(reasons)


def _exact_keys(
    value: Any, expected: set[str], label: str, problems: list[str]
) -> bool:
    if not isinstance(value, dict):
        problems.append(f"{label} must be an object")
        return False
    missing = expected - set(value)
    extra = set(value) - expected
    if missing:
        problems.append(f"{label}: missing fields {sorted(missing)}")
    if extra:
        problems.append(f"{label}: unknown fields {sorted(extra)}")
    return not missing and not extra


def _nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _existing_files(
    paths: Any, label: str, problems: list[str], *, allow_empty: bool = False
) -> None:
    if not isinstance(paths, list) or (
        not allow_empty and not paths
    ) or not all(_nonempty_text(path) for path in paths):
        problems.append(f"{label} must be an array of repository paths")
        return
    for relative in paths:
        if not (ROOT / relative).is_file():
            problems.append(f"{label}: missing repository file {relative}")


def load_outcomes() -> list[tuple[Path, dict[str, Any]]]:
    return [
        (path, load_json(path))
        for path in sorted(OUTCOMES_DIR.glob("*.json"))
    ]


def validate_policy(
    policy: dict[str, Any],
    decisions: dict[str, Any],
    hypotheses: dict[str, dict[str, str]],
) -> list[str]:
    problems: list[str] = []
    if policy.get("schema_version") != "0.1":
        problems.append("policy.schema_version must be 0.1")
    if policy.get("status") not in {"implementation", "active", "retired"}:
        problems.append("policy.status is invalid")
    if not _nonempty_text(policy.get("engine_id")):
        problems.append("policy.engine_id must be nonempty")
    ownership = policy.get("canonical_ownership", {})
    generation_ownership = {
        "typed_evidence_policy": "repo/ECDLP_TYPED_EVIDENCE_V0.json",
        "typed_evidence_state": "data/typed_evidence_state.json",
        "research_claim_policy": "repo/RESEARCH_CLAIMS_V0.json",
        "research_claim_state": "data/research_claim_state.json",
        "desk_decisions": "experiments/engine/desk_decisions/",
        "hypothesis_generation_policy": "repo/HYPOTHESIS_GENERATION_V0.json",
        "hypothesis_proposals": "experiments/engine/proposals/",
        "hypothesis_proposal_reviews": (
            "experiments/engine/proposal_reviews/"
        ),
    }
    for field, expected in generation_ownership.items():
        if ownership.get(field) != expected:
            problems.append(
                f"canonical_ownership.{field} must be {expected}"
            )

    policy_gates = policy.get("gates", {})
    exploration_gate = policy_gates.get("exploration", {})
    promotion_gate = policy_gates.get("promotion", {})
    if exploration_gate.get("authorized") is not True:
        problems.append("Research Engine v0 exploration gate must be authorized")
    if promotion_gate.get("authorized") is not False:
        problems.append("Research Engine v0 promotion gate must remain closed")
    phase_policy = decisions.get("phase_policy", {})
    execution_gates = decisions.get("execution_gates", {})
    structural_gate = execution_gates.get("structural", {})
    structural_pause = (
        structural_gate.get("authorized") is True
        and structural_gate.get("kind") == "non_experiment"
        and structural_gate.get("authorizes_experiment") is False
    )
    current_exploration_pause = decisions.get("next_phase_gate", {}).get(
        "current_mode"
    ) in {
        "proposal_intake_promotion_closed",
        "evidence_bounded_desk_priority_promotion_closed",
        "post_task026_proposal_only_promotion_closed",
    }
    bounded_authorization = decisions.get("bounded_experiment_authorization")
    external_bounded_singleton = (
        isinstance(bounded_authorization, dict)
        and bounded_authorization.get("status") in {"approved", "consumed"}
    )
    bounded_authorization_status = (
        bounded_authorization.get("status")
        if isinstance(bounded_authorization, dict)
        else None
    )
    expected_current_exploration = not (
        structural_pause
        or current_exploration_pause
        or external_bounded_singleton
    )
    if (
        phase_policy.get("bounded_exploration_authorized")
        is not expected_current_exploration
    ):
        problems.append(
            "decision substrate current exploration authorization does not "
            "match the current decision mode"
        )
    if phase_policy.get("promotion_experiments_authorized") is not False:
        problems.append("decision substrate must keep promotion experiments closed")
    if (
        execution_gates.get("exploration", {}).get("authorized")
        is not expected_current_exploration
    ):
        problems.append(
            "decision execution gate current authorization does not match "
            "the current decision mode"
        )
    if execution_gates.get("promotion", {}).get("authorized") is not False:
        problems.append("decision execution gate must keep promotion closed")

    route_ids = {route["id"] for route in decisions["routes"]}
    threat_ids = {model["id"] for model in decisions["threat_models"]}
    primary_threat_models = [
        model["id"]
        for model in decisions["threat_models"]
        if model.get("primary") is True
    ]
    if primary_threat_models != ["classical-single-target-plain"]:
        problems.append(
            "decision substrate must define exactly the plain single-target "
            "model as primary"
        )
    target_contract = policy.get("target_contract")
    if _exact_keys(
        target_contract,
        TARGET_CONTRACT_FIELDS,
        "target_contract",
        problems,
    ):
        for field in TARGET_CONTRACT_FIELDS:
            if not _nonempty_text(target_contract.get(field)):
                problems.append(f"target_contract.{field} must be nonempty")
        if target_contract.get("primary_threat_model") != (
            primary_threat_models[0] if len(primary_threat_models) == 1 else None
        ):
            problems.append(
                "target_contract.primary_threat_model must match the unique "
                "decision-substrate primary model"
            )
    primary_threat_model = (
        target_contract.get("primary_threat_model")
        if isinstance(target_contract, dict)
        else None
    )
    outcome_ids = [item.get("id") for item in policy.get("outcome_taxonomy", [])]
    gap_ids = [item.get("id") for item in policy.get("gap_taxonomy", [])]
    if len(outcome_ids) != len(set(outcome_ids)) or None in outcome_ids:
        problems.append("outcome taxonomy ids must be present and unique")
    if len(gap_ids) != len(set(gap_ids)) or None in gap_ids:
        problems.append("gap taxonomy ids must be present and unique")
    if set(outcome_ids) != PREDICTIVE_OUTCOMES | HISTORICAL_ONLY_OUTCOMES:
        problems.append(
            "outcome taxonomy must contain the seven predictive outcomes and "
            "the historical-only structural-confirmation label"
        )
    research_windows = {
        item["id"]
        for item in policy["gap_taxonomy"]
        if item.get("research_window") is True
    }
    if research_windows != {"mechanism_bearing_open_window"}:
        problems.append("only mechanism_bearing_open_window may be a research window")

    queues = policy.get("queue_separation", {})
    if set(queues) != {"ecdlp_research", "keyai_product", "anti_conflation_rules"}:
        problems.append("queue separation must define research, product, and anti-conflation")
    for queue_id in ("ecdlp_research", "keyai_product"):
        queue = queues.get(queue_id, {})
        if not (ROOT / str(queue.get("source", ""))).is_file():
            problems.append(f"{queue_id}: queue source does not exist")
        if not isinstance(queue.get("kpis"), list) or not queue.get("kpis"):
            problems.append(f"{queue_id}: kpis must be nonempty")

    normalized = policy.get("hypothesis_normalization", [])
    normalized_ids = [item.get("id") for item in normalized]
    if len(normalized_ids) != len(set(normalized_ids)):
        problems.append("hypothesis normalization ids must be unique")
    if set(normalized_ids) != set(hypotheses):
        problems.append(
            "hypothesis normalization must cover exactly the hypotheses registry; "
            f"missing={sorted(set(hypotheses) - set(normalized_ids))}, "
            f"extra={sorted(set(normalized_ids) - set(hypotheses))}"
        )
    for item in normalized:
        hypothesis_id = item.get("id", "?")
        source = hypotheses.get(hypothesis_id, {})
        if item.get("source_status") != source.get("status"):
            problems.append(f"{hypothesis_id}: source_status differs from HYPOTHESES.yaml")
        if item.get("direction") != source.get("direction"):
            problems.append(f"{hypothesis_id}: direction differs from HYPOTHESES.yaml")
        is_external_authorized_not_run = (
            bounded_authorization_status == "approved"
            and hypothesis_id == bounded_authorization.get("hypothesis_id")
            and item.get("engine_state")
            == "external_bounded_authorization_not_native_candidate"
        )
        is_external_consumed_terminal = (
            bounded_authorization_status == "consumed"
            and hypothesis_id == bounded_authorization.get("hypothesis_id")
            and item.get("engine_state")
            == "external_bounded_terminal_not_native_candidate"
        )
        if (
            is_external_authorized_not_run
            and item.get("normalized_outcome") is not None
        ):
            problems.append(
                f"{hypothesis_id}: authorized but unexecuted singleton must "
                "have no normalized outcome"
            )
        elif (
            is_external_consumed_terminal
            and item.get("normalized_outcome")
            != bounded_authorization.get("normalized_outcome")
        ):
            problems.append(
                f"{hypothesis_id}: consumed external singleton outcome must "
                "match its terminal authorization"
            )
        elif (
            not is_external_authorized_not_run
            and not is_external_consumed_terminal
            and item.get("normalized_outcome") not in outcome_ids
        ):
            problems.append(f"{hypothesis_id}: invalid normalized outcome")
        if not set(item.get("route_ids", [])) <= route_ids:
            problems.append(f"{hypothesis_id}: unknown route id")
        for field in (
            "verifier_scope",
            "engine_state",
            "rationale",
            "reopening_condition",
        ):
            if not _nonempty_text(item.get(field)):
                problems.append(f"{hypothesis_id}: {field} must be nonempty")

    candidates = policy.get("candidate_proposals", [])
    candidate_intake = policy.get("candidate_intake_contract")
    if _exact_keys(
        candidate_intake,
        CANDIDATE_INTAKE_CONTRACT_FIELDS,
        "candidate_intake_contract",
        problems,
    ):
        if (
            candidate_intake.get("legacy_candidate_set_status")
            != "frozen_non_executable_fixture"
        ):
            problems.append(
                "candidate_intake_contract must freeze the legacy candidates "
                "as non-executable fixtures"
            )
        if (
            candidate_intake.get("legacy_candidate_set_sha256")
            != V0_REVIEWED_CANDIDATE_SET_SHA256
        ):
            problems.append(
                "candidate_intake_contract legacy digest differs from the "
                "reviewed code anchor"
            )
        if sha256_json(candidates) != V0_REVIEWED_CANDIDATE_SET_SHA256:
            problems.append(
                "legacy candidate set changed; new candidates must enter through "
                "the typed proposal compiler"
            )
        if (
            candidate_intake.get("authoritative_new_candidate_source")
            != "quality_cleared_hypothesis_proposals"
        ):
            problems.append(
                "candidate_intake_contract must source new candidates from "
                "quality-cleared proposals"
            )
        if (
            candidate_intake.get("compiler_status") != "not_implemented"
            or candidate_intake.get("compiled_candidate_count") != 0
        ):
            problems.append(
                "candidate compiler is not implemented; compiled count must stay zero"
            )
        if not _nonempty_text(candidate_intake.get("authorization_rule")):
            problems.append(
                "candidate_intake_contract.authorization_rule must be nonempty"
            )
    candidate_ids = [candidate.get("id") for candidate in candidates]
    if len(candidate_ids) != len(set(candidate_ids)) or None in candidate_ids:
        problems.append("candidate ids must be present and unique")
    candidate_id_set = set(candidate_ids)
    if external_bounded_singleton:
        external_hypothesis_id = bounded_authorization.get("hypothesis_id")
        external_engine_state = (
            "external_bounded_terminal_not_native_candidate"
            if bounded_authorization_status == "consumed"
            else "external_bounded_authorization_not_native_candidate"
        )
        external_normalization = [
            item
            for item in normalized
            if item.get("id") == external_hypothesis_id
        ]
        if len(external_normalization) != 1 or external_normalization[0].get(
            "engine_state"
        ) != external_engine_state:
            problems.append(
                "external bounded authorization must map to exactly one "
                f"{external_engine_state} hypothesis normalization"
            )
        if any(
            candidate.get("hypothesis_id") == external_hypothesis_id
            for candidate in candidates
        ):
            problems.append(
                "external bounded authorization must not create a native "
                "Research Engine candidate"
            )
    selection_value = policy.get("selection_value")
    if not isinstance(selection_value, dict) or set(selection_value) != {
        "admissibility",
        "information_gain_formula",
        "priority_formula",
        "normalized_budget_cost",
        "commitment",
        "calibration",
        "tie_breakers",
    }:
        problems.append("selection_value contract is incomplete")
    exploration = policy["gates"]["exploration"]
    limits = exploration["limits"]
    if set(exploration.get("hard_rejections", [])) != HARD_REJECTIONS:
        problems.append("exploration gate must declare every hard rejection")
    max_selected = exploration.get("max_selected_per_cycle")
    if (
        not isinstance(max_selected, int)
        or isinstance(max_selected, bool)
        or not 1 <= max_selected <= 3
    ):
        problems.append("exploration max_selected_per_cycle must be in [1,3]")
    for field, value in limits.items():
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            problems.append(f"exploration limit {field} must be a positive integer")
    for candidate in candidates:
        candidate_id = candidate.get("id", "?")
        if not _exact_keys(
            candidate, CANDIDATE_FIELDS, f"{candidate_id}", problems
        ):
            continue
        if candidate.get("route_id") not in route_ids:
            problems.append(f"{candidate_id}: unknown route")
        if candidate.get("hypothesis_id") not in hypotheses:
            problems.append(f"{candidate_id}: unknown hypothesis")
        if candidate.get("gap_class") not in gap_ids:
            problems.append(f"{candidate_id}: unknown gap class")
        if candidate.get("scope", {}).get("threat_model") not in threat_ids:
            problems.append(f"{candidate_id}: unknown threat model")
        _existing_files(
            candidate.get("evidence_inputs"),
            f"{candidate_id}.evidence_inputs",
            problems,
        )
        for field in (
            "title",
            "mechanism",
            "prediction",
            "baseline",
            "stop_condition",
            "validator",
        ):
            if not _nonempty_text(candidate.get(field)):
                problems.append(f"{candidate_id}.{field} must be nonempty")
        scope = candidate.get("scope")
        if _exact_keys(
            scope, CANDIDATE_SCOPE_FIELDS, f"{candidate_id}.scope", problems
        ):
            if (
                not isinstance(scope.get("max_field_bits"), int)
                or isinstance(scope.get("max_field_bits"), bool)
                or scope["max_field_bits"] < 2
            ):
                problems.append(
                    f"{candidate_id}.scope.max_field_bits must be an integer >= 2"
                )
            if (
                not isinstance(scope.get("forbidden_targets"), list)
                or not all(
                    _nonempty_text(target)
                    for target in scope.get("forbidden_targets", [])
                )
            ):
                problems.append(
                    f"{candidate_id}.scope.forbidden_targets must be a string array"
                )
        budget = candidate.get("budget")
        if _exact_keys(
            budget, CANDIDATE_BUDGET_FIELDS, f"{candidate_id}.budget", problems
        ):
            for field in CANDIDATE_BUDGET_FIELDS:
                value = budget.get(field)
                if (
                    not isinstance(value, int)
                    or isinstance(value, bool)
                    or value <= 0
                ):
                    problems.append(
                        f"{candidate_id}.budget.{field} must be a positive integer"
                    )
        preregistration = candidate.get("preregistration")
        authorization = candidate.get("authorization")
        if authorization == "none":
            if preregistration != {}:
                problems.append(
                    f"{candidate_id}: closed candidates must not be preregistered"
                )
        elif _exact_keys(
            preregistration,
            PREREGISTRATION_FIELDS,
            f"{candidate_id}.preregistration",
            problems,
        ):
            expected_preregistration_status = (
                "frozen" if authorization == "exploration" else "draft"
            )
            if preregistration.get("status") != expected_preregistration_status:
                problems.append(
                    f"{candidate_id}: {authorization} preregistration must be "
                    f"{expected_preregistration_status}"
                )
            solver = preregistration.get("solver")
            if _exact_keys(
                solver,
                PREREGISTRATION_SOLVER_FIELDS,
                f"{candidate_id}.preregistration.solver",
                problems,
            ):
                if not _nonempty_text(solver.get("name")) or not _nonempty_text(
                    solver.get("algorithm")
                ):
                    problems.append(
                        f"{candidate_id}: solver name and algorithm must be nonempty"
                    )
                versions = solver.get("versions")
                if (
                    not isinstance(versions, dict)
                    or not versions
                    or not all(
                        _nonempty_text(name) and _nonempty_text(version)
                        for name, version in versions.items()
                    )
                ):
                    problems.append(
                        f"{candidate_id}: solver versions must be a nonempty string map"
                    )
            seeds = preregistration.get("seeds")
            if (
                not isinstance(seeds, list)
                or not seeds
                or len(seeds) != len(set(seeds))
                or not all(
                    isinstance(seed, int) and not isinstance(seed, bool)
                    for seed in seeds
                )
            ):
                problems.append(
                    f"{candidate_id}: preregistration seeds must be unique integers"
                )
            curves = preregistration.get("curves")
            curve_ids: list[str] = []
            if not isinstance(curves, list) or not curves:
                problems.append(
                    f"{candidate_id}: preregistration curves must be nonempty"
                )
                curves = []
            for index, curve in enumerate(curves):
                curve_label = f"{candidate_id}.preregistration.curves[{index}]"
                if not _exact_keys(
                    curve,
                    PREREGISTRATION_CURVE_FIELDS,
                    curve_label,
                    problems,
                ):
                    continue
                curve_id = curve.get("id")
                if not _nonempty_text(curve_id):
                    problems.append(f"{curve_label}.id must be nonempty")
                else:
                    curve_ids.append(curve_id)
                for field in (
                    "field_p",
                    "curve_a",
                    "curve_b",
                    "base_order",
                    "cofactor",
                ):
                    value = curve.get(field)
                    if (
                        not isinstance(value, int)
                        or isinstance(value, bool)
                        or value < (2 if field in {"field_p", "base_order"} else 0)
                    ):
                        problems.append(f"{curve_label}.{field} is invalid")
                base_point = curve.get("base_point")
                if (
                    not isinstance(base_point, list)
                    or len(base_point) != 2
                    or not all(
                        isinstance(value, int) and not isinstance(value, bool)
                        for value in base_point
                    )
                ):
                    problems.append(f"{curve_label}.base_point must be [x,y]")
                field_p = curve.get("field_p")
                if (
                    isinstance(field_p, int)
                    and not isinstance(field_p, bool)
                    and field_p.bit_length() > candidate.get("scope", {}).get(
                        "max_field_bits", -1
                    )
                ):
                    problems.append(
                        f"{curve_label} exceeds candidate field-size budget"
                    )
                if curve.get("cofactor") != 1:
                    problems.append(
                        f"{curve_label} must use a cofactor-1 exploration curve"
                    )
            if len(curve_ids) != len(set(curve_ids)):
                problems.append(
                    f"{candidate_id}: preregistered curve ids must be unique"
                )
            instances = preregistration.get("instances")
            if not isinstance(instances, list) or not instances:
                problems.append(
                    f"{candidate_id}: preregistration instances must be nonempty"
                )
                instances = []
            for index, instance in enumerate(instances):
                instance_label = (
                    f"{candidate_id}.preregistration.instances[{index}]"
                )
                if not _exact_keys(
                    instance,
                    PREREGISTRATION_INSTANCE_FIELDS,
                    instance_label,
                    problems,
                ):
                    continue
                if instance.get("curve_id") not in set(curve_ids):
                    problems.append(f"{instance_label}: unknown curve_id")
                m_value = instance.get("m")
                if (
                    not isinstance(m_value, int)
                    or isinstance(m_value, bool)
                    or m_value < 2
                ):
                    problems.append(f"{instance_label}.m must be an integer >= 2")
                sizes = instance.get("factor_base_sizes")
                if (
                    not isinstance(sizes, list)
                    or not sizes
                    or len(sizes) != len(set(sizes))
                    or not all(
                        isinstance(size, int)
                        and not isinstance(size, bool)
                        and size >= 2
                        for size in sizes
                    )
                ):
                    problems.append(
                        f"{instance_label}.factor_base_sizes must be unique integers >= 2"
                    )
                presentations = instance.get("presentations")
                if (
                    not isinstance(presentations, list)
                    or not presentations
                    or len(presentations) != len(set(presentations))
                    or not all(_nonempty_text(item) for item in presentations)
                ):
                    problems.append(
                        f"{instance_label}.presentations must be unique strings"
                    )
            validator_contract = preregistration.get("validator_contract")
            if _exact_keys(
                validator_contract,
                VALIDATOR_CONTRACT_FIELDS,
                f"{candidate_id}.preregistration.validator_contract",
                problems,
            ):
                validator_status = validator_contract.get("status")
                if validator_status not in {"implemented", "pending"}:
                    problems.append(
                        f"{candidate_id}: validator status must be implemented "
                        "or pending"
                    )
                if validator_contract.get("protocol") != VALIDATOR_PROTOCOL:
                    problems.append(
                        f"{candidate_id}: validator protocol must be "
                        f"{VALIDATOR_PROTOCOL}"
                    )
                measurement_contract = validator_contract.get(
                    "measurement_contract"
                )
                if _exact_keys(
                    measurement_contract,
                    MEASUREMENT_CONTRACT_FIELDS,
                    f"{candidate_id}.validator.measurement_contract",
                    problems,
                ):
                    for field in ("name", "unit"):
                        if not _nonempty_text(measurement_contract.get(field)):
                            problems.append(
                                f"{candidate_id}: measurement {field} must be "
                                "nonempty"
                            )
                    value_type = measurement_contract.get("value_type")
                    if value_type not in {
                        "boolean",
                        "integer",
                        "number",
                        "string",
                    }:
                        problems.append(
                            f"{candidate_id}: invalid measurement value_type"
                        )
                    elif not measurement_value_matches_type(
                        measurement_contract.get("supported_value"),
                        value_type,
                    ):
                        problems.append(
                            f"{candidate_id}: supported_value does not match "
                            "measurement value_type"
                        )
                    if (
                        value_type != "string"
                        or measurement_contract.get("supported_value")
                        != "supported"
                    ):
                        problems.append(
                            f"{candidate_id}: validator measurement must emit "
                            "canonical per-instance outcome strings"
                        )
                outcome_classifier = validator_contract.get(
                    "outcome_classifier"
                )
                if _exact_keys(
                    outcome_classifier,
                    OUTCOME_CLASSIFIER_FIELDS,
                    f"{candidate_id}.validator.outcome_classifier",
                    problems,
                ):
                    if outcome_classifier.get("protocol") != (
                        OUTCOME_CLASSIFIER_PROTOCOL
                    ):
                        problems.append(
                            f"{candidate_id}: outcome classifier protocol must be "
                            f"{OUTCOME_CLASSIFIER_PROTOCOL}"
                        )
                    allowed_instance_outcomes = outcome_classifier.get(
                        "allowed_instance_outcomes"
                    )
                    precedence = outcome_classifier.get("precedence")
                    if (
                        not isinstance(allowed_instance_outcomes, list)
                        or len(allowed_instance_outcomes)
                        != len(set(allowed_instance_outcomes))
                        or set(allowed_instance_outcomes)
                        != EMPIRICAL_OUTCOMES
                    ):
                        problems.append(
                            f"{candidate_id}: outcome classifier must allow exactly "
                            "the six empirical outcomes"
                        )
                    if (
                        not isinstance(precedence, list)
                        or len(precedence) != len(set(precedence))
                        or set(precedence) != EMPIRICAL_OUTCOMES
                    ):
                        problems.append(
                            f"{candidate_id}: outcome classifier precedence must be "
                            "an exhaustive permutation of the empirical outcomes"
                        )
                required_roles = validator_contract.get(
                    "required_artifact_roles"
                )
                if (
                    not isinstance(required_roles, list)
                    or not required_roles
                    or len(required_roles) > PURE_VALIDATOR_MAX_ARTIFACT_ROLES
                    or len(required_roles) != len(set(required_roles))
                    or not all(_nonempty_text(role) for role in required_roles)
                ):
                    problems.append(
                        f"{candidate_id}: validator artifact roles must be a "
                        "unique nonempty string array with at most "
                        f"{PURE_VALIDATOR_MAX_ARTIFACT_ROLES} entries"
                    )
                entrypoint = validator_contract.get("entrypoint")
                entrypoint_sha256 = validator_contract.get(
                    "entrypoint_sha256"
                )
                if validator_status == "pending":
                    if entrypoint is not None or entrypoint_sha256 is not None:
                        problems.append(
                            f"{candidate_id}: pending validator cannot name an "
                            "entrypoint or digest"
                        )
                    if candidate.get("hard_rejections", {}).get(
                        "missing_independent_validator"
                    ) is not True:
                        problems.append(
                            f"{candidate_id}: pending validator must set "
                            "missing_independent_validator=true"
                        )
                elif validator_status == "implemented":
                    entrypoint_path = scientific_validator_entrypoint(
                        entrypoint
                    )
                    if entrypoint_path is None:
                        problems.append(
                            f"{candidate_id}: implemented validator entrypoint "
                            "must be a Python file under "
                            "experiments/engine/validators/; framework fixtures "
                            "are never scientific validators"
                        )
                    if (
                        not isinstance(entrypoint_sha256, str)
                        or HASH_ID.fullmatch(entrypoint_sha256) is None
                        or entrypoint_path is None
                        or file_sha256(entrypoint_path) != entrypoint_sha256
                    ):
                        problems.append(
                            f"{candidate_id}: implemented validator digest "
                            "does not match"
                        )
                    elif entrypoint_path is not None:
                        for validator_problem in validate_pure_validator_source(
                            entrypoint_path.read_bytes()
                        ):
                            problems.append(
                                f"{candidate_id}: {validator_problem}"
                            )
            for field in (
                "target_rule",
                "primary_metric",
                "success_rule",
                "stop_rule",
            ):
                if not _nonempty_text(preregistration.get(field)):
                    problems.append(
                        f"{candidate_id}.preregistration.{field} must be nonempty"
                    )
        information_model = candidate.get("information_model")
        if candidate.get("authorization") == "exploration" and information_model == {}:
            problems.append(
                f"{candidate_id}: exploration candidates need an information model"
            )
        if information_model != {} and _exact_keys(
            information_model,
            INFORMATION_MODEL_FIELDS,
            f"{candidate_id}.information_model",
            problems,
        ):
            for field in ("latent_question", "prior_rationale"):
                if not _nonempty_text(information_model.get(field)):
                    problems.append(
                        f"{candidate_id}.information_model.{field} must be nonempty"
                    )
            prior_live = information_model.get("prior_live")
            if (
                not isinstance(prior_live, (int, float))
                or isinstance(prior_live, bool)
                or not 0.0 < prior_live < 1.0
            ):
                problems.append(
                    f"{candidate_id}.information_model.prior_live must be in (0,1)"
                )
            likelihoods = information_model.get("likelihoods")
            if not isinstance(likelihoods, dict) or set(likelihoods) != (
                PREDICTIVE_OUTCOMES
            ):
                problems.append(
                    f"{candidate_id}: likelihoods must cover exactly the seven "
                    "native predictive outcomes"
                )
                likelihoods = {}
            for outcome, likelihood in likelihoods.items():
                if not _exact_keys(
                    likelihood,
                    LIKELIHOOD_FIELDS,
                    f"{candidate_id}.likelihoods.{outcome}",
                    problems,
                ):
                    continue
                for latent_state, probability in likelihood.items():
                    if (
                        not isinstance(probability, (int, float))
                        or isinstance(probability, bool)
                        or not 0.0 <= probability <= 1.0
                    ):
                        problems.append(
                            f"{candidate_id}.likelihoods.{outcome}.{latent_state} "
                            "must be in [0,1]"
                        )
            for latent_state in ("live", "dead"):
                total = sum(
                    likelihood.get(latent_state, 0.0)
                    for likelihood in likelihoods.values()
                    if isinstance(likelihood, dict)
                )
                if abs(total - 1.0) > 1e-9:
                    problems.append(
                        f"{candidate_id}: P(outcome|{latent_state}) sums to {total}"
                    )
            if (
                candidate.get("authorization") == "exploration"
                and not any(
                    value is True
                    for value in candidate.get("hard_rejections", {}).values()
                )
                and candidate.get("scope", {}).get("threat_model")
                == primary_threat_model
                and isinstance(prior_live, (int, float))
                and not isinstance(prior_live, bool)
                and likelihoods
                and expected_information_gain(prior_live, likelihoods) <= 0.0
            ):
                problems.append(
                    f"{candidate_id}: information model has zero discriminating value"
                )
        hard = candidate.get("hard_rejections")
        if _exact_keys(
            hard, HARD_REJECTIONS, f"{candidate_id}.hard_rejections", problems
        ):
            for field, value in hard.items():
                if not isinstance(value, bool):
                    problems.append(
                        f"{candidate_id}.hard_rejections.{field} must be boolean"
                    )
            if (
                candidate.get("gap_class") == "mechanism_bearing_open_window"
                and hard.get("missing_exact_mechanism") is True
            ):
                problems.append(
                    f"{candidate_id}: a mechanism-bearing window cannot declare "
                    "its exact mechanism missing"
                )
        dependencies = candidate.get("dependencies")
        if not isinstance(dependencies, list) or len(dependencies) != len(
            set(dependencies)
        ):
            problems.append(f"{candidate_id}: dependencies must be a unique array")
            dependencies = []
        unknown_dependencies = set(dependencies) - candidate_id_set
        if unknown_dependencies:
            problems.append(
                f"{candidate_id}: unknown dependencies {sorted(unknown_dependencies)}"
            )
        if candidate_id in dependencies:
            problems.append(f"{candidate_id}: candidate cannot depend on itself")
        dependency_requirements = candidate.get("dependency_requirements")
        if not isinstance(dependency_requirements, dict):
            problems.append(
                f"{candidate_id}: dependency_requirements must be an object"
            )
            dependency_requirements = {}
        if set(dependency_requirements) != set(dependencies):
            problems.append(
                f"{candidate_id}: dependency_requirements must cover exactly "
                "the declared dependencies"
            )
        for dependency, allowed_outcomes in dependency_requirements.items():
            if (
                not isinstance(allowed_outcomes, list)
                or not allowed_outcomes
                or len(allowed_outcomes) != len(set(allowed_outcomes))
                or not set(allowed_outcomes) <= PREDICTIVE_OUTCOMES
            ):
                problems.append(
                    f"{candidate_id}: dependency {dependency} must name a unique, "
                    "nonempty set of native predictive outcomes"
                )

        reasons = (
            rejection_reasons(candidate, primary_threat_model)
            if isinstance(hard, dict)
            else []
        )
        threat_model_mismatch = (
            primary_threat_model is not None
            and candidate.get("scope", {}).get("threat_model")
            != primary_threat_model
        )
        if (
            threat_model_mismatch
            and isinstance(hard, dict)
            and hard.get("changes_threat_model") is not True
        ):
            problems.append(
                f"{candidate_id}: non-primary threat model must set "
                "changes_threat_model=true"
            )
        if authorization == "exploration" and reasons:
            problems.append(
                f"{candidate_id}: exploration authorization conflicts with hard "
                f"rejections {reasons}"
            )
        if authorization == "none" and not reasons:
            problems.append(
                f"{candidate_id}: authorization=none needs an explicit hard rejection"
            )
        if authorization == "intake" and not reasons:
            problems.append(
                f"{candidate_id}: authorization=intake needs an unresolved hard gate"
            )
        if authorization not in {"exploration", "intake", "none"}:
            problems.append(f"{candidate_id}: invalid authorization")
        result_updates = candidate.get("result_updates")
        result_updates_valid = (
            isinstance(result_updates, dict)
            and (
                result_updates == {}
                or (
                    set(result_updates) == PREDICTIVE_OUTCOMES
                    and all(
                        _nonempty_text(value)
                        for value in result_updates.values()
                    )
                )
            )
        )
        if not result_updates_valid:
            problems.append(
                f"{candidate_id}: result_updates must be empty or cover all "
                "native predictive outcomes"
            )
        if authorization == "exploration" and result_updates == {}:
            problems.append(
                f"{candidate_id}: exploration result_updates must cover all "
                "native predictive outcomes"
            )
        if authorization == "exploration":
            scope = candidate.get("scope", {})
            budget = candidate.get("budget", {})
            if scope.get("max_field_bits", 10**9) > limits["max_field_bits"]:
                problems.append(f"{candidate_id}: field budget exceeds exploration gate")
            if "secp256k1" not in scope.get("forbidden_targets", []):
                problems.append(f"{candidate_id}: exploration must forbid secp256k1")
            if budget.get("wall_time_seconds", 10**18) > limits[
                "max_wall_time_seconds"
            ]:
                problems.append(f"{candidate_id}: time budget exceeds exploration gate")
            if budget.get("peak_memory_bytes", 10**30) > limits[
                "max_peak_memory_bytes"
            ]:
                problems.append(f"{candidate_id}: memory budget exceeds exploration gate")
            if budget.get("parallel_workers", 10**9) > limits[
                "max_parallel_workers"
            ]:
                problems.append(f"{candidate_id}: worker budget exceeds exploration gate")
            if (
                candidate.get("gap_class") != "mechanism_bearing_open_window"
                and candidate.get("kind") != "validator_prerequisite"
            ):
                problems.append(
                    f"{candidate_id}: exploration must be a research window or its "
                    "named validator prerequisite"
                )
            if candidate.get("kind") == "validator_prerequisite":
                downstream = candidate.get("downstream_research_window")
                downstream_candidate = next(
                    (item for item in candidates if item.get("id") == downstream), None
                )
                if (
                    downstream_candidate is None
                    or downstream_candidate.get("gap_class")
                    != "mechanism_bearing_open_window"
                ):
                    problems.append(
                        f"{candidate_id}: validator prerequisite needs a downstream "
                        "mechanism-bearing candidate"
                    )

    # Explicit cycle check, independent of selector truncation.
    graph = {
        candidate["id"]: candidate.get("dependencies", []) for candidate in candidates
    }
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(candidate_id: str) -> None:
        if candidate_id in visited:
            return
        if candidate_id in visiting:
            problems.append(f"candidate dependency cycle includes {candidate_id}")
            return
        visiting.add(candidate_id)
        for dependency in graph.get(candidate_id, []):
            visit(dependency)
        visiting.remove(candidate_id)
        visited.add(candidate_id)

    for candidate_id in graph:
        visit(candidate_id)

    retrospective_cases = policy.get("retrospective_cases")
    if not isinstance(retrospective_cases, list):
        problems.append("retrospective_cases must be an array")
        retrospective_cases = []
    retrospective_ids = [case.get("id") for case in retrospective_cases]
    if set(retrospective_ids) != RETROSPECTIVE_CASE_IDS or len(
        retrospective_ids
    ) != len(RETROSPECTIVE_CASE_IDS):
        problems.append(
            "retrospective_cases must retain exactly the four frozen v0 cases"
        )
    for case in retrospective_cases:
        case_id = case.get("id", "?")
        _exact_keys(case, RETROSPECTIVE_FIELDS, case_id, problems)
        if not isinstance(case.get("outcome_event_id"), str) or not EVENT_ID.fullmatch(
            case["outcome_event_id"]
        ):
            problems.append(f"{case_id}: invalid outcome_event_id")
        if not isinstance(case.get("event_sha256"), str) or not HASH_ID.fullmatch(
            case["event_sha256"]
        ):
            problems.append(f"{case_id}: invalid event_sha256")
        for field in ("candidate_id", "hypothesis_id", "route_id"):
            if not _nonempty_text(case.get(field)):
                problems.append(f"{case_id}: {field} must be nonempty")
        if case.get("known_outcome") not in outcome_ids:
            problems.append(f"{case_id}: invalid known outcome")
        _exact_keys(
            case.get("hard_rejections"),
            HARD_REJECTIONS,
            f"{case_id}.hard_rejections",
            problems,
        )
        if case.get("expected_selector_disposition") != "hard_rejected":
            problems.append(f"{case_id}: invalid retrospective disposition")
    retrospective_method = policy.get("retrospective_method")
    if not isinstance(retrospective_method, dict) or set(retrospective_method) != {
        "method",
        "claim",
        "limitation",
    }:
        problems.append("retrospective_method must declare method, claim, limitation")
    elif not all(_nonempty_text(value) for value in retrospective_method.values()):
        problems.append("retrospective_method fields must be nonempty")
    scope_guards = policy.get("historical_scope_guards")
    if not isinstance(scope_guards, list) or not scope_guards:
        problems.append("historical_scope_guards must be nonempty")
    else:
        guard_event_ids = [guard.get("event_id") for guard in scope_guards]
        if set(guard_event_ids) != HISTORICAL_SCOPE_GUARD_EVENT_IDS or len(
            guard_event_ids
        ) != len(HISTORICAL_SCOPE_GUARD_EVENT_IDS):
            problems.append(
                "historical_scope_guards must retain the cofactor-1/cofactor-3 split"
            )
        for index, guard in enumerate(scope_guards):
            label = f"historical_scope_guards[{index}]"
            if not _exact_keys(
                guard, HISTORICAL_SCOPE_GUARD_FIELDS, label, problems
            ):
                continue
            if not isinstance(guard.get("event_id"), str) or not EVENT_ID.fullmatch(
                guard["event_id"]
            ):
                problems.append(f"{label}: invalid event_id")
            if not isinstance(guard.get("event_sha256"), str) or not HASH_ID.fullmatch(
                guard["event_sha256"]
            ):
                problems.append(f"{label}: invalid event_sha256")
            for field in ("field_bits", "forbidden_field_bits"):
                values = guard.get(field)
                if (
                    not isinstance(values, list)
                    or not values
                    or len(values) != len(set(values))
                    or not all(
                        isinstance(value, int)
                        and not isinstance(value, bool)
                        and value >= 2
                        for value in values
                    )
                ):
                    problems.append(f"{label}.{field} must be unique bit sizes")
    baseline = policy.get("historical_outcome_baseline")
    if not _exact_keys(
        baseline,
        HISTORICAL_BASELINE_FIELDS,
        "historical_outcome_baseline",
        problems,
    ):
        baseline = {}
    if baseline.get("status") != "review_anchored_v0":
        problems.append(
            "historical_outcome_baseline.status must be review_anchored_v0"
        )
    if (
        baseline.get("anchor_sha256")
        != V0_REVIEWED_HISTORICAL_ROOT_SHA256
    ):
        problems.append(
            "historical_outcome_baseline.anchor_sha256 must match the "
            "validator-code v0 anchor"
        )
    baseline_events = baseline.get("events")
    if not isinstance(baseline_events, list):
        problems.append("historical_outcome_baseline.events must be an array")
        baseline_events = []
    baseline_event_ids = [event.get("event_id") for event in baseline_events]
    if set(baseline_event_ids) != HISTORICAL_BASELINE_EVENT_IDS or len(
        baseline_event_ids
    ) != len(HISTORICAL_BASELINE_EVENT_IDS):
        problems.append(
            "historical_outcome_baseline must retain exactly the eight v0 events"
        )
    for index, event in enumerate(baseline_events):
        label = f"historical_outcome_baseline.events[{index}]"
        if not _exact_keys(
            event, HISTORICAL_BASELINE_EVENT_FIELDS, label, problems
        ):
            continue
        if not isinstance(event.get("event_id"), str) or not EVENT_ID.fullmatch(
            event["event_id"]
        ):
            problems.append(f"{label}: invalid event_id")
        if not isinstance(event.get("event_sha256"), str) or not HASH_ID.fullmatch(
            event["event_sha256"]
        ):
            problems.append(f"{label}: invalid event_sha256")
    return problems


def validate_external_bounded_outcome(
    event: dict[str, Any],
    policy: dict[str, Any],
    decisions: dict[str, Any],
    scope: dict[str, Any],
    budget: dict[str, Any],
    stop: dict[str, Any],
    provenance: dict[str, Any],
    label: str,
) -> list[str]:
    """Validate a decision-authorized receipt without making it native."""

    problems: list[str] = []
    authorization = decisions.get("bounded_experiment_authorization")
    if not isinstance(authorization, dict):
        return [
            f"{label}: external bounded event needs a decision authorization"
        ]
    authorization_status = authorization.get("status")
    if authorization_status not in {"approved", "consumed"}:
        problems.append(
            f"{label}: bounded experiment authorization is neither approved "
            "nor consumed"
        )
    if authorization_status == "consumed":
        if authorization.get("terminal_event_id") != event.get("event_id"):
            problems.append(
                f"{label}: consumed authorization terminal_event_id differs"
            )
        if authorization.get("normalized_outcome") != event.get("outcome"):
            problems.append(
                f"{label}: consumed authorization normalized_outcome differs"
            )
        if authorization.get("rerun_authorized") is not False:
            problems.append(
                f"{label}: consumed authorization must forbid reruns"
            )
    if authorization.get("promotion_authorized") is not False:
        problems.append(
            f"{label}: bounded experiment authorization must not authorize promotion"
        )

    for event_field, authorization_field in {
        "candidate_id": "authorization_id",
        "hypothesis_id": "hypothesis_id",
        "route_id": "route_id",
    }.items():
        if event.get(event_field) != authorization.get(authorization_field):
            problems.append(
                f"{label}: {event_field} differs from bounded authorization"
            )

    candidate_ids = {
        candidate.get("id") for candidate in policy.get("candidate_proposals", [])
    }
    if event.get("candidate_id") in candidate_ids:
        problems.append(
            f"{label}: external bounded authorization must not be a native candidate"
        )

    source_commit = provenance.get("source_commit")
    if source_commit != authorization.get("source_commit"):
        problems.append(
            f"{label}: source_commit differs from bounded authorization"
        )
    source_reproducible = git_commit_exists(source_commit)
    if not source_reproducible:
        problems.append(
            f"{label}: bounded authorization source_commit is not reproducible"
        )

    authorization_scope = authorization.get("scope")
    if not isinstance(authorization_scope, dict):
        authorization_scope = {}
        problems.append(f"{label}: bounded authorization scope must be an object")
    if authorization_scope.get("kind") != "synthetic_toy_only":
        problems.append(
            f"{label}: bounded authorization must remain synthetic-toy-only"
        )
    if authorization_scope.get("real_world_targets_forbidden") is not True:
        problems.append(
            f"{label}: bounded authorization must forbid real-world targets"
        )
    if authorization_scope.get("secp256k1_targets_forbidden") is not True:
        problems.append(
            f"{label}: bounded authorization must forbid secp256k1 targets"
        )
    if scope.get("target_kind") != "toy":
        problems.append(f"{label}: external bounded event must have toy target_kind")
    authorized_family = authorization_scope.get("curve_family")
    event_family = scope.get("curve_family")
    if (
        not _nonempty_text(authorized_family)
        or not _nonempty_text(event_family)
        or str(authorized_family).casefold() not in str(event_family).casefold()
    ):
        problems.append(
            f"{label}: outcome curve family does not identify the authorized family"
        )
    if "secp256k1" in str(event_family).casefold():
        problems.append(
            f"{label}: external bounded event cannot target secp256k1"
        )

    route = next(
        (
            item
            for item in decisions.get("routes", [])
            if item.get("id") == event.get("route_id")
        ),
        {},
    )
    if scope.get("threat_model") not in route.get("threat_models", []):
        problems.append(
            f"{label}: outcome threat model is not declared by its route"
        )

    manifest_relative = provenance.get("run_manifest")
    manifest_path = repo_file(manifest_relative)
    manifest: dict[str, Any] = {}
    if manifest_path is None:
        problems.append(
            f"{label}: external bounded event needs an existing run_manifest"
        )
    else:
        try:
            manifest_path.relative_to(
                (ROOT / "experiments" / "engine").resolve()
            )
        except ValueError:
            problems.append(
                f"{label}: external bounded run_manifest must live under "
                "experiments/engine"
            )
        if manifest_path.name != "run_manifest.json":
            problems.append(
                f"{label}: external bounded run_manifest must be run_manifest.json"
            )
        manifest_hash = provenance.get("run_manifest_sha256")
        if (
            not isinstance(manifest_hash, str)
            or not HASH_ID.fullmatch(manifest_hash)
        ):
            problems.append(
                f"{label}: external bounded event needs run_manifest_sha256"
            )
        elif exact_file_sha256(manifest_path) != manifest_hash:
            problems.append(f"{label}: run_manifest_sha256 mismatch")
        try:
            loaded_manifest = load_json(manifest_path)
        except (OSError, json.JSONDecodeError):
            problems.append(f"{label}: external bounded run_manifest is malformed")
        else:
            if isinstance(loaded_manifest, dict):
                manifest = loaded_manifest
            else:
                problems.append(
                    f"{label}: external bounded run_manifest must be an object"
                )

    authorization_bindings = authorization.get("sha256_bindings")
    if not isinstance(authorization_bindings, dict):
        authorization_bindings = {}
        problems.append(
            f"{label}: authorization sha256_bindings must be an object"
        )
    expected_bindings = {
        f"{key}_sha256": digest
        for key, digest in authorization_bindings.items()
    }
    approved_authorization_snapshot = {
        key: authorization.get(key)
        for key in (
            "hypothesis_id",
            "task_id",
            "route_id",
            "cell_id",
            "promotion_authorized",
            "authorization_id",
            "source_commit",
            "authorized_utc",
            "sha256_bindings",
            "resource_budget",
            "scope",
        )
    }
    approved_authorization_snapshot["status"] = "approved"
    if manifest:
        _exact_keys(
            manifest,
            EXTERNAL_BOUNDED_MANIFEST_FIELDS,
            f"{label}.run_manifest",
            problems,
        )
        for field, expected in {
            "authorization_id": authorization.get("authorization_id"),
            "run_id": authorization.get("authorization_id"),
            "authorization_source_commit": source_commit,
            "hypothesis_id": authorization.get("hypothesis_id"),
        }.items():
            if manifest.get(field) != expected:
                problems.append(
                    f"{label}: run_manifest.{field} differs from authorization"
                )
        if manifest.get("bindings") != expected_bindings:
            problems.append(
                f"{label}: run_manifest bindings differ from authorization"
            )

    bundle_dir = manifest_path.parent if manifest_path is not None else None
    curve_table: dict[str, Any] = {}
    if bundle_dir is not None:
        try:
            bundle_relative = bundle_dir.resolve().relative_to(ROOT.resolve())
        except ValueError:
            bundle_relative = None
        for binding, filename in EXTERNAL_BOUNDED_BINDING_FILES.items():
            expected = authorization_bindings.get(binding)
            if not isinstance(expected, str) or not HASH_ID.fullmatch(expected):
                problems.append(
                    f"{label}: authorization has invalid {binding} binding"
                )
                continue
            source_path = bundle_dir / filename
            if not source_path.is_file():
                problems.append(
                    f"{label}: authorization-bound file is absent: {filename}"
                )
            elif exact_file_sha256(source_path) != expected:
                problems.append(
                    f"{label}: authorization-bound working-tree hash drifted: "
                    f"{binding}"
                )
            if bundle_relative is None:
                continue
            git_relative = (bundle_relative / filename).as_posix()
            payload = (
                authorized_git_file_bytes(source_commit, git_relative)
                if source_reproducible
                else None
            )
            if payload is None and source_reproducible:
                problems.append(
                    f"{label}: source_commit lacks bound file: {git_relative}"
                )
            elif (
                payload is not None
                and hashlib.sha256(payload).hexdigest() != expected
            ):
                problems.append(
                    f"{label}: source-commit hash drifted: {binding}"
                )
        curve_path = bundle_dir / EXTERNAL_BOUNDED_BINDING_FILES["curve_table"]
        if curve_path.is_file():
            try:
                loaded_curves = load_json(curve_path)
            except (OSError, json.JSONDecodeError):
                problems.append(f"{label}: authorized curve table is malformed")
            else:
                if isinstance(loaded_curves, dict):
                    curve_table = loaded_curves

    curves = curve_table.get("curves") if curve_table else None
    if not isinstance(curves, list) or not curves:
        problems.append(f"{label}: authorized curve table has no curves")
    else:
        curve_ids = [
            item.get("curve_id") for item in curves if isinstance(item, dict)
        ]
        if curve_ids != authorization_scope.get("curve_ids"):
            problems.append(
                f"{label}: curve table ids differ from bounded authorization"
            )
        table_bits = sorted(
            {
                item.get("field_bits")
                for item in curves
                if isinstance(item, dict)
                and isinstance(item.get("field_bits"), int)
                and not isinstance(item.get("field_bits"), bool)
            }
        )
        if scope.get("field_bits") != table_bits:
            problems.append(
                f"{label}: outcome field_bits differ from authorized curve table"
            )
        max_bits = authorization_scope.get("max_field_bits")
        if (
            not isinstance(max_bits, int)
            or isinstance(max_bits, bool)
            or not table_bits
            or max(table_bits) > max_bits
        ):
            problems.append(
                f"{label}: authorized curve table exceeds field-size budget"
            )

    authorization_budget = authorization.get("resource_budget")
    if not isinstance(authorization_budget, dict):
        authorization_budget = {}
        problems.append(f"{label}: authorization resource budget must be an object")
    wall_seconds = budget.get("wall_time_seconds")
    peak_bytes = budget.get("peak_memory_bytes")
    max_wall_hours = authorization_budget.get("max_wall_hours")
    max_peak_gib = authorization_budget.get("max_peak_rss_gib")
    if (
        isinstance(wall_seconds, (int, float))
        and not isinstance(wall_seconds, bool)
        and isinstance(max_wall_hours, (int, float))
        and wall_seconds > max_wall_hours * 3600
    ):
        problems.append(f"{label}: external run exceeds wall-time budget")
    if (
        isinstance(peak_bytes, int)
        and not isinstance(peak_bytes, bool)
        and isinstance(max_peak_gib, (int, float))
        and peak_bytes > max_peak_gib * 1024**3
    ):
        problems.append(f"{label}: external run exceeds peak-memory budget")
    if budget.get("parallel_workers") != 1:
        problems.append(
            f"{label}: external singleton must record one parallel worker"
        )
    if budget.get("status") == "historical_not_recorded":
        problems.append(
            f"{label}: external bounded event must record resource use"
        )
    if stop.get("triggered") is not True:
        problems.append(
            f"{label}: external bounded terminal must consume its stop condition"
        )

    artifact: dict[str, Any] = {}
    summary: dict[str, Any] = {}
    if bundle_dir is not None:
        for filename, destination in (
            ("artifact.json", "artifact"),
            ("summary.json", "summary"),
        ):
            bundle_path = bundle_dir / filename
            if not bundle_path.is_file():
                problems.append(
                    f"{label}: external bounded bundle is missing {filename}"
                )
                continue
            try:
                value = load_json(bundle_path)
            except (OSError, json.JSONDecodeError):
                problems.append(
                    f"{label}: external bounded {filename} is malformed"
                )
                continue
            if not isinstance(value, dict):
                problems.append(
                    f"{label}: external bounded {filename} must be an object"
                )
            elif destination == "artifact":
                artifact = value
            else:
                summary = value

        artifact_path = bundle_dir / "artifact.json"
        sidecar_path = bundle_dir / "artifact.sha256"
        if artifact_path.is_file():
            if not sidecar_path.is_file():
                problems.append(
                    f"{label}: external bounded artifact sidecar is missing"
                )
            else:
                sidecar = sidecar_path.read_text(encoding="utf-8").strip().split()
                if sidecar != [exact_file_sha256(artifact_path), "artifact.json"]:
                    problems.append(
                        f"{label}: external bounded artifact sidecar mismatch"
                    )

    if artifact:
        for field, expected in {
            "hypothesis_id": event.get("hypothesis_id"),
            "route_id": event.get("route_id"),
            "run_id": event.get("candidate_id"),
        }.items():
            if artifact.get(field) != expected:
                problems.append(
                    f"{label}: artifact.{field} differs from outcome"
                )
        artifact_bindings = artifact.get("bindings", {})
        if artifact_bindings.get("authorization") != (
            approved_authorization_snapshot
        ):
            problems.append(
                f"{label}: artifact authorization differs from decision substrate"
            )
        if artifact_bindings.get("producer_inputs") != expected_bindings:
            problems.append(
                f"{label}: artifact producer bindings differ from authorization"
            )
        if artifact.get("validation", {}).get("status") != "PASS":
            problems.append(
                f"{label}: external bounded artifact is not independently valid"
            )
        claim_boundary = artifact.get("claim_boundary", {})
        for field in (
            "promotion_authorized",
            "real_world_targets_used",
            "secp256k1_targets_used",
            "secp256k1_attack_claim",
            "secp256k1_key_recovery_claim",
            "asymptotic_improvement_claim",
        ):
            if claim_boundary.get(field) is not False:
                problems.append(
                    f"{label}: artifact claim boundary must keep {field}=false"
                )
        if artifact.get("h_new_retained") is not False:
            problems.append(f"{label}: external bounded artifact retained H_NEW")
        if event.get("outcome") == "supported" and (
            artifact.get("terminal_status")
            != "CLASSIFY_AS_KNOWN_LOCAL_SIMPLIFICATION"
            or artifact.get("opens_solver_slope_proposal") is not True
            or artifact.get("decision_metrics", {}).get(
                "primary_promotion_gates_pass"
            )
            is not True
        ):
            problems.append(
                f"{label}: supported external outcome lacks its exact enabling "
                "terminal"
            )
        if authorization_status == "consumed":
            if authorization.get("terminal_status") != artifact.get(
                "terminal_status"
            ):
                problems.append(
                    f"{label}: consumed authorization terminal_status differs"
                )
            artifact_digest = (
                exact_file_sha256(bundle_dir / "artifact.json")
                if bundle_dir is not None
                and (bundle_dir / "artifact.json").is_file()
                else None
            )
            if authorization.get("validated_artifact_sha256") != artifact_digest:
                problems.append(
                    f"{label}: consumed authorization artifact digest differs"
                )

    if summary:
        if summary.get("hypothesis_id") != event.get("hypothesis_id"):
            problems.append(
                f"{label}: summary hypothesis differs from outcome"
            )
        if summary.get("run_id") != event.get("candidate_id"):
            problems.append(f"{label}: summary run_id differs from outcome")
        if summary.get("bindings") != expected_bindings:
            problems.append(
                f"{label}: summary bindings differ from authorization"
            )
        trials = summary.get("totals", {}).get("primary_trials")
        max_trials = authorization_budget.get("max_primary_trials")
        if (
            not isinstance(trials, int)
            or isinstance(trials, bool)
            or not isinstance(max_trials, int)
            or trials > max_trials
        ):
            problems.append(
                f"{label}: external run exceeds or omits primary-trial budget"
            )
        usage = summary.get("resource_usage", {})
        for field, limit in {
            "cpu_hours": authorization_budget.get("max_cpu_hours"),
            "peak_rss_gib": authorization_budget.get("max_peak_rss_gib"),
            "wall_hours": authorization_budget.get("max_wall_hours"),
        }.items():
            value = usage.get(field)
            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or not isinstance(limit, (int, float))
                or value < 0
                or value > limit
            ):
                problems.append(
                    f"{label}: external run exceeds or omits {field} budget"
                )
        if (
            isinstance(wall_seconds, (int, float))
            and not isinstance(wall_seconds, bool)
            and isinstance(usage.get("wall_hours"), (int, float))
            and not math.isclose(
                wall_seconds,
                usage["wall_hours"] * 3600,
                rel_tol=1e-9,
                abs_tol=1e-6,
            )
        ):
            problems.append(
                f"{label}: outcome wall time differs from producer summary"
            )
        if (
            isinstance(peak_bytes, int)
            and not isinstance(peak_bytes, bool)
            and isinstance(usage.get("peak_rss_gib"), (int, float))
            and peak_bytes != round(usage["peak_rss_gib"] * 1024**3)
        ):
            problems.append(
                f"{label}: outcome peak memory differs from producer summary"
            )
        if artifact and artifact.get("resource_usage") != usage:
            problems.append(
                f"{label}: artifact resource usage differs from summary"
            )

    return problems


def validate_outcome(
    path: Path,
    event: dict[str, Any],
    policy: dict[str, Any],
    decisions: dict[str, Any],
    hypotheses: dict[str, dict[str, str]],
    source_reviews: dict[str, dict[str, Any]] | None = None,
) -> list[str]:
    problems: list[str] = []
    label = path.name
    if not _exact_keys(event, OUTCOME_FIELDS, label, problems):
        return problems
    if event.get("schema_version") != 1:
        problems.append(f"{label}: schema_version must be 1")
    event_id = event.get("event_id")
    if not isinstance(event_id, str) or not EVENT_ID.fullmatch(event_id):
        problems.append(f"{label}: invalid event id")
    elif path.stem != event_id:
        problems.append(f"{label}: filename must equal event_id")
    try:
        date.fromisoformat(str(event.get("recorded_on")))
    except ValueError:
        problems.append(f"{label}: recorded_on must be YYYY-MM-DD")
    if (
        isinstance(event_id, str)
        and EVENT_ID.fullmatch(event_id)
        and event_id[4:14] != event.get("recorded_on")
    ):
        problems.append(f"{label}: event id date must match recorded_on")

    outcome_ids = {item["id"] for item in policy["outcome_taxonomy"]}
    route_ids = {route["id"] for route in decisions["routes"]}
    threat_ids = {model["id"] for model in decisions["threat_models"]}
    candidate_index = {
        candidate["id"]: candidate for candidate in policy["candidate_proposals"]
    }
    if event.get("outcome") not in outcome_ids:
        problems.append(f"{label}: unknown outcome")
    if event.get("hypothesis_id") not in hypotheses:
        problems.append(f"{label}: unknown hypothesis")
    if event.get("route_id") not in route_ids:
        problems.append(f"{label}: unknown route")
    for field in ("candidate_id", "summary", "reopening_condition"):
        if not _nonempty_text(event.get(field)):
            problems.append(f"{label}: {field} must be nonempty")

    _existing_files(event.get("evidence_files"), f"{label}.evidence_files", problems)
    scope = event.get("scope")
    if _exact_keys(scope, SCOPE_FIELDS, f"{label}.scope", problems):
        if scope.get("target_kind") not in {
            "toy",
            "validator_calibration",
            "formal",
            "operational",
        }:
            problems.append(f"{label}: invalid target_kind")
        if scope.get("threat_model") not in threat_ids:
            problems.append(f"{label}: unknown threat model")
        if (
            event.get("outcome") == "proved"
            and scope.get("target_kind") != "formal"
        ):
            problems.append(
                f"{label}: proved is reserved for formal target_kind; "
                "positive empirical evidence must use supported"
            )
        bits = scope.get("field_bits")
        if bits is not None and (
            not isinstance(bits, list)
            or not bits
            or not all(
                isinstance(item, int) and not isinstance(item, bool) and item >= 2
                for item in bits
            )
        ):
            problems.append(f"{label}: field_bits must be null or integer array")

    validation = event.get("validation")
    if _exact_keys(
        validation, VALIDATION_FIELDS, f"{label}.validation", problems
    ):
        if validation.get("status") not in {
            "passed",
            "partial",
            "failed",
            "not_available",
        }:
            problems.append(f"{label}: invalid validation status")
        if not isinstance(validation.get("decisive_claim_validated"), bool):
            problems.append(
                f"{label}: validation.decisive_claim_validated must be boolean"
            )
        _existing_files(
            validation.get("evidence_files"),
            f"{label}.validation.evidence_files",
            problems,
            allow_empty=True,
        )
        independence = validation.get("independence")
        if _exact_keys(
            independence,
            INDEPENDENCE_FIELDS,
            f"{label}.validation.independence",
            problems,
        ):
            if independence.get("path") not in {
                "verified_distinct",
                "not_verified",
            }:
                problems.append(f"{label}: invalid validation independence path")
            if independence.get("artifact") not in {
                "raw_recomputed",
                "fresh_cross_check",
                "producer_summary_only",
                "not_verified",
            }:
                problems.append(
                    f"{label}: invalid validation independence artifact"
                )
            if independence.get("source") not in {
                "reviewed_independent",
                "shared_components",
                "not_reviewed",
            }:
                problems.append(
                    f"{label}: invalid validation independence source"
                )
            source_review_id = independence.get("source_review_id")
            if source_review_id is not None and not _nonempty_text(
                source_review_id
            ):
                problems.append(
                    f"{label}: source_review_id must be null or nonempty"
                )
            if (
                independence.get("source") == "reviewed_independent"
                and not _nonempty_text(source_review_id)
            ):
                problems.append(
                    f"{label}: reviewed source independence needs source_review_id"
                )
            if (
                independence.get("source") == "reviewed_independent"
                and _nonempty_text(source_review_id)
                and source_reviews is not None
            ):
                source_review = source_reviews.get(str(source_review_id))
                if source_review is None:
                    problems.append(
                        f"{label}: source_review_id does not resolve to a "
                        "prior-art review"
                    )
                elif (
                    source_review.get("reviewer_role") != "prior_art"
                    or source_review.get("verdict") != "pass"
                    or source_review.get("source_independence")
                    != "declared_independent"
                ):
                    problems.append(
                        f"{label}: source_review_id must reference a passing, "
                        "independent prior-art review"
                    )
        else:
            independence = {}
        path_verified = independence.get("path") == "verified_distinct"
        artifact_recomputed = independence.get("artifact") in {
            "raw_recomputed",
            "fresh_cross_check",
        }
        source_reviewed = (
            independence.get("source") == "reviewed_independent"
        )
        if validation.get("decisive_claim_validated") and not (
            path_verified and artifact_recomputed
        ):
            problems.append(
                f"{label}: decisive validation requires a verified distinct path "
                "and recomputed or fresh-cross-check artifact evidence"
            )
        if validation.get("decisive_claim_validated") and validation.get(
            "status"
        ) != "passed":
            problems.append(
                f"{label}: decisive validation requires validation.status=passed"
            )
        decisive_outcomes = {
            "proved",
            "supported",
            "falsified",
            "bounded_negative",
            "inapplicable",
            "historical_structural_confirmation",
        }
        if event.get("outcome") in decisive_outcomes and (
            validation.get("status") != "passed"
            or not path_verified
            or not artifact_recomputed
            or not validation.get("decisive_claim_validated")
        ):
            problems.append(
                f"{label}: {event.get('outcome')} requires passed, "
                "path-distinct, artifact-recomputed, decisive validation"
            )
        source_kind = event.get("provenance", {}).get("source_kind")
        if event.get("outcome") == "supported" and source_kind not in {
            "native_engine_run",
            "external_bounded_decision_run",
        }:
            problems.append(
                f"{label}: supported is reserved for preregistered native runs "
                "or decision-authorized bounded runs"
            )
        if event.get("outcome") == "historical_structural_confirmation" and (
            source_kind != "historical_migration"
        ):
            problems.append(
                f"{label}: historical_structural_confirmation is reserved for "
                "historical migrations"
            )
        if (
            source_kind == "native_engine_run"
            and event.get("outcome") in decisive_outcomes
            and not source_reviewed
        ):
            problems.append(
                f"{label}: native decisive outcome requires reviewed source "
                "independence"
            )

    budget = event.get("budget")
    if _exact_keys(budget, BUDGET_FIELDS, f"{label}.budget", problems):
        if budget.get("status") not in {
            "within_budget",
            "limit_reached",
            "historical_not_recorded",
        }:
            problems.append(f"{label}: invalid budget status")
        for field in (
            "wall_time_seconds",
            "peak_memory_bytes",
            "parallel_workers",
        ):
            value = budget.get(field)
            if value is not None and (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or value < 0
                or field in {"peak_memory_bytes", "parallel_workers"}
                and not isinstance(value, int)
                or field == "parallel_workers"
                and isinstance(value, int)
                and value < 1
            ):
                problems.append(f"{label}: budget.{field} has an invalid value")
        if event.get("outcome") == "resource_exhausted" and budget.get(
            "status"
        ) != "limit_reached":
            problems.append(
                f"{label}: resource_exhausted requires budget.status=limit_reached"
            )

    stop = event.get("stop_condition")
    if _exact_keys(stop, STOP_FIELDS, f"{label}.stop_condition", problems):
        if not isinstance(stop.get("triggered"), bool):
            problems.append(f"{label}: stop_condition.triggered must be boolean")
        if not _nonempty_text(stop.get("statement")):
            problems.append(f"{label}: stop_condition.statement must be nonempty")
    residual = event.get("residual_uncertainty")
    if not isinstance(residual, list) or not all(_nonempty_text(item) for item in residual):
        problems.append(f"{label}: residual_uncertainty must be a string array")

    provenance = event.get("provenance")
    if _exact_keys(
        provenance, PROVENANCE_FIELDS, f"{label}.provenance", problems
    ):
        if provenance.get("source_kind") not in {
            "historical_migration",
            "native_engine_run",
            "external_bounded_decision_run",
        }:
            problems.append(f"{label}: invalid provenance source_kind")
        commit = provenance.get("source_commit")
        if not isinstance(commit, str) or not COMMIT_ID.fullmatch(commit):
            problems.append(f"{label}: source_commit must be lowercase 40-hex")
        source_kind = provenance.get("source_kind")
        run_manifest = provenance.get("run_manifest")
        run_manifest_hash = provenance.get("run_manifest_sha256")
        if source_kind == "historical_migration":
            if run_manifest is not None or run_manifest_hash is not None:
                problems.append(
                    f"{label}: historical migration must not claim a native run manifest"
                )
        if source_kind == "native_engine_run":
            if commit == "0" * 40:
                problems.append(f"{label}: native event needs a real source commit")
            elif not scientific_source_commit_allowed(commit):
                problems.append(
                    f"{label}: native source_commit is not reproducible from "
                    "protected main or a registered immutable evidence ref"
                )
            manifest_path = repo_file(run_manifest)
            if manifest_path is None:
                problems.append(
                    f"{label}: native event needs an existing repository run_manifest"
                )
            if (
                not isinstance(run_manifest_hash, str)
                or not HASH_ID.fullmatch(run_manifest_hash)
            ):
                problems.append(
                    f"{label}: native event needs run_manifest_sha256"
                )
            elif manifest_path is not None and file_sha256(
                manifest_path
            ) != run_manifest_hash:
                problems.append(f"{label}: run_manifest_sha256 mismatch")
            candidate = candidate_index.get(event.get("candidate_id"))
            selected_ids = {
                item["candidate_id"]
                for item in select_candidates(policy)["selected_sequence"]
            }
            if candidate is None:
                problems.append(f"{label}: native event has unknown candidate")
                candidate = {}
            elif event.get("candidate_id") not in selected_ids:
                problems.append(f"{label}: native event candidate is not selected")
            elif candidate.get("authorization") != "exploration":
                problems.append(f"{label}: native event candidate is not authorized")
            if event.get("route_id") != candidate.get("route_id"):
                problems.append(f"{label}: native event route differs from candidate")
            if event.get("hypothesis_id") != candidate.get("hypothesis_id"):
                problems.append(
                    f"{label}: native event hypothesis differs from candidate"
                )
            if scope.get("target_kind") not in {"toy", "validator_calibration"}:
                problems.append(f"{label}: native exploration must remain toy/calibration")
            bits = scope.get("field_bits") or []
            if not bits:
                problems.append(
                    f"{label}: native event must record at least one field bit size"
                )
            max_bits = policy["gates"]["exploration"]["limits"]["max_field_bits"]
            if bits and max(bits) > max_bits:
                problems.append(f"{label}: native event exceeds field-size budget")
            if bits and max(bits) > candidate.get("scope", {}).get(
                "max_field_bits", -1
            ):
                problems.append(
                    f"{label}: native event exceeds candidate field-size budget"
                )
            if scope.get("threat_model") != candidate.get("scope", {}).get(
                "threat_model"
            ):
                problems.append(
                    f"{label}: native event threat model differs from candidate"
                )
            if scope.get("curve_family") != candidate.get("scope", {}).get(
                "curve_family"
            ):
                problems.append(
                    f"{label}: native event curve family differs from candidate"
                )
            if "secp256k1" in scope.get("curve_family", "").lower():
                problems.append(f"{label}: native exploration cannot target secp256k1")
            if budget.get("status") == "historical_not_recorded":
                problems.append(
                    f"{label}: native event must record its actual resource use"
                )
            for field in (
                "wall_time_seconds",
                "peak_memory_bytes",
                "parallel_workers",
            ):
                value = budget.get(field)
                candidate_limit = candidate.get("budget", {}).get(field, -1)
                gate_field = {
                    "wall_time_seconds": "max_wall_time_seconds",
                    "peak_memory_bytes": "max_peak_memory_bytes",
                    "parallel_workers": "max_parallel_workers",
                }[field]
                gate_limit = policy["gates"]["exploration"]["limits"][gate_field]
                if (
                    not isinstance(value, (int, float))
                    or isinstance(value, bool)
                    or value <= 0
                ):
                    problems.append(
                        f"{label}: native event must record positive budget.{field}"
                    )
                elif value > candidate_limit or value > gate_limit:
                    problems.append(
                        f"{label}: native event exceeds {field} budget"
                    )
            if stop.get("triggered") is not True:
                problems.append(
                    f"{label}: native terminal event must trigger its stop condition"
                )
        if source_kind == "external_bounded_decision_run":
            problems.extend(
                validate_external_bounded_outcome(
                    event,
                    policy,
                    decisions,
                    scope if isinstance(scope, dict) else {},
                    budget if isinstance(budget, dict) else {},
                    stop if isinstance(stop, dict) else {},
                    provenance,
                    label,
                )
            )
    return problems


def select_candidates(policy: dict[str, Any]) -> dict[str, Any]:
    candidates = {
        candidate["id"]: copy.deepcopy(candidate)
        for candidate in policy["candidate_proposals"]
    }
    rejected = []
    eligible = {}
    limits = policy["gates"]["exploration"]["limits"]
    primary_threat_model = policy["target_contract"]["primary_threat_model"]
    for candidate_id, candidate in candidates.items():
        reasons = rejection_reasons(candidate, primary_threat_model)
        if candidate.get("authorization") != "exploration" or reasons:
            rejected.append(
                {
                    "candidate_id": candidate_id,
                    "title": candidate["title"],
                    "authorization": candidate.get("authorization"),
                    "disposition": (
                        "intake_blocked"
                        if candidate.get("authorization") == "intake"
                        else "closed"
                    ),
                    "reasons": reasons or ["not_authorized"],
                }
            )
            continue
        candidate.update(candidate_value(candidate, limits))
        eligible[candidate_id] = candidate

    selected: list[dict[str, Any]] = []
    selected_ids: set[str] = set()
    limit = policy["gates"]["exploration"]["max_selected_per_cycle"]
    while len(selected) < limit:
        available = [
            candidate
            for candidate in eligible.values()
            if candidate["id"] not in selected_ids
            and set(candidate.get("dependencies", [])) <= selected_ids
        ]
        if not available:
            break
        available.sort(
            key=lambda candidate: (
                -candidate["priority_bits_per_cost"],
                -candidate["expected_information_gain_bits"],
                candidate["normalized_budget_cost"],
                candidate["id"],
            )
        )
        chosen = available[0]
        selected_ids.add(chosen["id"])
        selected.append(
            {
                "position": len(selected) + 1,
                "candidate_id": chosen["id"],
                "title": chosen["title"],
                "route_id": chosen["route_id"],
                "hypothesis_id": chosen["hypothesis_id"],
                "kind": chosen["kind"],
                "gap_class": chosen["gap_class"],
                "expected_information_gain_bits": chosen[
                    "expected_information_gain_bits"
                ],
                "normalized_budget_cost": chosen["normalized_budget_cost"],
                "priority_bits_per_cost": chosen["priority_bits_per_cost"],
                "dependencies": chosen["dependencies"],
                "validator_status": chosen["preregistration"][
                    "validator_contract"
                ]["status"],
                "execution_state": (
                    "ready"
                    if not chosen["dependencies"]
                    else "conditional_on_prior_selected_outcomes"
                ),
                "budget": chosen["budget"],
                "stop_condition": chosen["stop_condition"],
            }
        )
    blocked = sorted(
        set(eligible) - selected_ids
    )
    return {
        "selected_sequence": selected,
        "hard_rejected": sorted(rejected, key=lambda item: item["candidate_id"]),
        "eligible_not_selected": blocked,
    }


def apply_execution_feedback(
    policy: dict[str, Any],
    selection: dict[str, Any],
    outcomes: list[dict[str, Any]],
) -> dict[str, Any]:
    """Resolve the selected portfolio into a dependency-gated execution queue."""
    candidate_index = {
        candidate["id"]: candidate for candidate in policy["candidate_proposals"]
    }
    native_by_candidate = {
        event["candidate_id"]: event
        for event in outcomes
        if event["provenance"]["source_kind"] == "native_engine_run"
    }
    sequence = copy.deepcopy(selection["selected_sequence"])
    ready: list[str] = []
    awaiting: list[str] = []
    awaiting_validator: list[str] = []
    blocked: list[str] = []
    terminal: list[str] = []
    for item in sequence:
        candidate_id = item["candidate_id"]
        candidate = candidate_index[candidate_id]
        dependency_status = []
        dependency_blocked = False
        dependency_waiting = False
        for dependency in candidate["dependencies"]:
            dependency_event = native_by_candidate.get(dependency)
            allowed = candidate["dependency_requirements"][dependency]
            if dependency_event is None:
                status = "awaiting_outcome"
                dependency_waiting = True
                observed = None
            elif dependency_event["outcome"] not in allowed:
                status = "outcome_blocks_execution"
                dependency_blocked = True
                observed = dependency_event["outcome"]
            else:
                status = "satisfied"
                observed = dependency_event["outcome"]
            dependency_status.append(
                {
                    "candidate_id": dependency,
                    "allowed_outcomes": allowed,
                    "observed_outcome": observed,
                    "status": status,
                }
            )

        own_event = native_by_candidate.get(candidate_id)
        if own_event is not None:
            item["execution_state"] = "terminal"
            item["terminal_event_id"] = own_event["event_id"]
            item["terminal_outcome"] = own_event["outcome"]
            terminal.append(candidate_id)
        elif dependency_blocked:
            item["execution_state"] = "blocked_by_dependency_outcome"
            blocked.append(candidate_id)
        elif dependency_waiting:
            item["execution_state"] = "awaiting_dependency_outcome"
            awaiting.append(candidate_id)
        elif (
            candidate["preregistration"]["validator_contract"]["status"]
            != "implemented"
        ):
            item["execution_state"] = "awaiting_validator_implementation"
            awaiting_validator.append(candidate_id)
        else:
            item["execution_state"] = "ready"
            ready.append(candidate_id)
        item["dependency_status"] = dependency_status

    return {
        **selection,
        "selected_sequence": sequence,
        "execution_queue": {
            "ready_candidate_ids": ready,
            "awaiting_dependency_candidate_ids": awaiting,
            "awaiting_validator_candidate_ids": awaiting_validator,
            "blocked_candidate_ids": blocked,
            "terminal_candidate_ids": terminal,
        },
    }


def validate_native_sequence(
    policy: dict[str, Any],
    decisions: dict[str, Any],
    outcomes: list[tuple[Path, dict[str, Any]]],
) -> list[str]:
    """Reject duplicate, unauthorized, or unbound native terminal outcomes."""
    problems: list[str] = []
    candidate_index = {
        candidate["id"]: candidate for candidate in policy["candidate_proposals"]
    }
    native = [
        (path, event)
        for path, event in outcomes
        if event.get("provenance", {}).get("source_kind") == "native_engine_run"
    ]
    by_candidate: dict[str, list[tuple[Path, dict[str, Any]]]] = defaultdict(list)
    for path, event in native:
        by_candidate[event.get("candidate_id")].append((path, event))
    for candidate_id, events in by_candidate.items():
        if len(events) > 1:
            problems.append(
                f"{candidate_id}: multiple native terminal events; create a new "
                "candidate id for a reopened run"
            )

    selection = select_candidates(policy)
    prior_native: list[dict[str, Any]] = []
    for path, event in sorted(native, key=lambda item: item[1].get("event_id", "")):
        queue = apply_execution_feedback(policy, selection, prior_native)[
            "execution_queue"
        ]
        ready_ids = set(queue["ready_candidate_ids"])
        manifest_relative = event.get("provenance", {}).get("run_manifest")
        manifest_path = repo_file(manifest_relative)
        if manifest_path is None:
            continue
        candidate = candidate_index.get(event.get("candidate_id"))
        if candidate is not None:
            for error in validate_engine_run_manifest(
                manifest_path,
                event,
                candidate,
                policy,
                decisions,
                ready_ids,
            ):
                problems.append(f"{path.name}: run envelope: {error}")
        prior_native.append(event)

    single_events = {
        candidate_id: events[0][1]
        for candidate_id, events in by_candidate.items()
        if len(events) == 1
    }
    for path, event in native:
        candidate = candidate_index.get(event.get("candidate_id"))
        if candidate is None:
            continue
        for dependency in candidate["dependencies"]:
            dependency_event = single_events.get(dependency)
            allowed = candidate["dependency_requirements"][dependency]
            if dependency_event is None:
                problems.append(
                    f"{path.name}: dependency {dependency} has no native outcome"
                )
            elif dependency_event.get("outcome") not in allowed:
                problems.append(
                    f"{path.name}: dependency {dependency} outcome "
                    f"{dependency_event.get('outcome')!r} does not unlock execution"
                )
            elif dependency_event.get("event_id", "") >= event.get("event_id", ""):
                problems.append(
                    f"{path.name}: dependency {dependency} outcome must precede "
                    "the dependent event"
                )
    return problems


def validate_external_bounded_sequence(
    decisions: dict[str, Any],
    outcomes: list[tuple[Path, dict[str, Any]]],
) -> list[str]:
    """Consume an approved bounded authorization at most once."""

    problems: list[str] = []
    external = [
        (path, event)
        for path, event in outcomes
        if event.get("provenance", {}).get("source_kind")
        == "external_bounded_decision_run"
    ]
    authorization = decisions.get("bounded_experiment_authorization", {})
    authorization_id = authorization.get("authorization_id")
    if len(external) > 1:
        problems.append(
            f"{authorization_id}: multiple external bounded terminal events; "
            "the singleton authorization is already consumed"
        )
    for path, event in external:
        if event.get("candidate_id") != authorization_id:
            problems.append(
                f"{path.name}: external event does not consume the approved "
                "bounded authorization"
            )
    return problems


def validate_retrospective(
    policy: dict[str, Any],
    outcomes: list[dict[str, Any]],
) -> dict[str, Any]:
    event_index = {event["event_id"]: event for event in outcomes}
    results = []
    passed = True
    for case in policy["retrospective_cases"]:
        event = event_index.get(case["outcome_event_id"])
        reasons = sorted(
            key for key, value in case["hard_rejections"].items() if value is True
        )
        observed = "hard_rejected" if reasons else "would_reopen_without_new_premise"
        evidence_matches = (
            event is not None
            and event.get("outcome") == case["known_outcome"]
            and event.get("candidate_id") == case["candidate_id"]
            and event.get("hypothesis_id") == case["hypothesis_id"]
            and event.get("route_id") == case["route_id"]
            and sha256_json(event) == case["event_sha256"]
        )
        case_passed = (
            observed == case["expected_selector_disposition"] and evidence_matches
        )
        passed = passed and case_passed
        results.append(
            {
                "case_id": case["id"],
                "outcome_event_id": case["outcome_event_id"],
                "known_outcome": case["known_outcome"],
                "observed_outcome": event.get("outcome") if event else None,
                "evidence_matches": evidence_matches,
                "rejection_reasons": reasons,
                "expected": case["expected_selector_disposition"],
                "observed": observed,
                "passed": case_passed,
            }
        )
    return {
        "passed": passed,
        "method": policy["retrospective_method"],
        "cases": results,
    }


def build_calibration(
    policy: dict[str, Any], outcomes: list[dict[str, Any]]
) -> dict[str, Any]:
    candidate_index = {
        candidate["id"]: candidate for candidate in policy["candidate_proposals"]
    }
    records = []
    for event in outcomes:
        if event["provenance"]["source_kind"] != "native_engine_run":
            continue
        candidate = candidate_index.get(event["candidate_id"])
        if candidate is None or not candidate.get("information_model"):
            continue
        information_model = candidate["information_model"]
        predicted = predicted_marginal(
            information_model["prior_live"],
            information_model["likelihoods"],
        )
        records.append(
            {
                "candidate_id": candidate["id"],
                "event_id": event["event_id"],
                "actual_outcome": event["outcome"],
                "predicted_marginal": {
                    key: round(value, 8)
                    for key, value in sorted(predicted.items())
                },
                "brier_score": round(
                    brier_score(predicted, event["outcome"]), 8
                ),
            }
        )
    return {
        "historical_outcomes_excluded": sum(
            event["provenance"]["source_kind"] == "historical_migration"
            for event in outcomes
        ),
        "external_bounded_outcomes_excluded": sum(
            event["provenance"]["source_kind"]
            == "external_bounded_decision_run"
            for event in outcomes
        ),
        "scored_native_outcomes": len(records),
        "mean_brier_score": (
            round(
                sum(record["brier_score"] for record in records) / len(records),
                8,
            )
            if records
            else None
        ),
        "records": records,
        "note": (
            "Historical migrations are excluded because their priors and "
            "likelihoods were not frozen before observation. External bounded "
            "decision runs are excluded because they are not native selected "
            "Engine candidates."
        ),
    }


def decision_delta_for_event(
    event: dict[str, Any],
    candidate: dict[str, Any] | None,
) -> dict[str, str]:
    source_kind = event["provenance"]["source_kind"]
    if source_kind == "historical_migration":
        return {
            "effect": "retained_history",
            "statement": (
                "Retain the scoped historical evidence; no automatic route "
                "decision follows."
            ),
        }
    if source_kind == "external_bounded_decision_run":
        return {
            "effect": "external_bounded_result_retained",
            "statement": (
                "Retain the exact decision-authorized result outside native "
                "selection and calibration; no automatic promotion follows."
            ),
        }
    outcome = event["outcome"]
    if outcome == "supported":
        effect = (
            "dependency_unlock"
            if candidate is not None
            and candidate.get("kind") == "validator_prerequisite"
            else "decision_review_required"
        )
    else:
        effect = {
            "proved": "formal_record_only",
            "falsified": "close_or_revise",
            "bounded_negative": "park_scoped_negative",
            "inapplicable": "reject_for_scope",
            "inconclusive": "no_change",
            "resource_exhausted": "no_change",
        }[outcome]
    statement = (
        candidate.get("result_updates", {}).get(outcome)
        if candidate is not None
        else None
    )
    return {
        "effect": effect,
        "statement": statement
        or "Retain the event and require an explicit policy revision.",
    }


def build_state(
    policy: dict[str, Any],
    decisions: dict[str, Any],
    hypotheses: dict[str, dict[str, str]],
    outcomes: list[tuple[Path, dict[str, Any]]],
    hypothesis_generation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if hypothesis_generation is None:
        _, hypothesis_generation = build_generation_state(
            load_json(GENERATION_POLICY_PATH),
            decisions,
            policy,
            load_hypothesis_generation_records(PROPOSALS_DIR),
            load_hypothesis_generation_records(REVIEWS_DIR),
        )
    event_values = [event for _, event in outcomes]
    selection = apply_execution_feedback(
        policy, select_candidates(policy), event_values
    )
    retrospective = validate_retrospective(policy, event_values)
    calibration = build_calibration(policy, event_values)
    candidate_index = {
        candidate["id"]: candidate for candidate in policy["candidate_proposals"]
    }
    by_hypothesis: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_route: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in event_values:
        candidate = candidate_index.get(event["candidate_id"])
        summary = {
            "event_id": event["event_id"],
            "candidate_id": event["candidate_id"],
            "outcome": event["outcome"],
            "summary": event["summary"],
            "claim_boundary": event["scope"]["claim_boundary"],
            "reopening_condition": event["reopening_condition"],
            "decision_delta": decision_delta_for_event(event, candidate),
        }
        by_hypothesis[event["hypothesis_id"]].append(summary)
        by_route[event["route_id"]].append(summary)

    normalized_hypotheses = []
    for item in policy["hypothesis_normalization"]:
        events = by_hypothesis.get(item["id"], [])
        normalized_hypotheses.append(
            {
                **item,
                "outcome_event_count": len(events),
                "outcome_counts": dict(
                    sorted(Counter(event["outcome"] for event in events).items())
                ),
                "outcome_event_ids": [event["event_id"] for event in events],
            }
        )

    decision_index = {route["id"]: route for route in decisions["routes"]}
    primary_threat_model = policy["target_contract"]["primary_threat_model"]
    route_states = []
    for route_id, route in sorted(decision_index.items()):
        events = by_route.get(route_id, [])
        outcomes_for_route = Counter(event["outcome"] for event in events)
        route_review_trigger_event_ids = [
            event["event_id"]
            for event in event_values
            if event["route_id"] == route_id
            and event["provenance"]["source_kind"] == "native_engine_run"
            and candidate_index.get(event["candidate_id"], {}).get("kind")
            in {"mechanism_probe", "scaling_probe"}
            and event["outcome"] in {"proved", "supported", "falsified"}
        ]
        if route_review_trigger_event_ids:
            engine_disposition = "decision_review_required"
        elif outcomes_for_route["inconclusive"] or outcomes_for_route[
            "resource_exhausted"
        ]:
            engine_disposition = "open_with_scoped_uncertainty"
        elif outcomes_for_route["bounded_negative"] or outcomes_for_route[
            "inapplicable"
        ]:
            engine_disposition = "bounded_negative_retained"
        elif outcomes_for_route["supported"]:
            engine_disposition = "supported_structural_evidence_retained"
        elif outcomes_for_route["historical_structural_confirmation"]:
            engine_disposition = "historical_structural_confirmation_retained"
        else:
            engine_disposition = "no_engine_evidence"
        declared_threat_models = route["threat_models"]
        if declared_threat_models == [primary_threat_model]:
            threat_model_scope = "primary"
        elif primary_threat_model in declared_threat_models:
            threat_model_scope = "mixed_with_primary"
        else:
            threat_model_scope = "separate"
        route_states.append(
            {
                "route_id": route_id,
                "threat_model_axis": {
                    "primary_model": primary_threat_model,
                    "declared_models": declared_threat_models,
                    "scope": threat_model_scope,
                },
                "decision_axis": {
                    "substrate_disposition": route["status"],
                    "authorized_experiment": route["authorized_experiment"],
                },
                "evidence_axis": {
                    "engine_disposition": engine_disposition,
                    "outcome_counts": dict(sorted(outcomes_for_route.items())),
                },
                "event_ids": [event["event_id"] for event in events],
                "route_review_trigger_event_ids": route_review_trigger_event_ids,
                "reopening_conditions": [
                    event["reopening_condition"] for event in events
                ],
            }
        )

    outcome_counts = Counter(event["outcome"] for event in event_values)
    event_summaries = sorted(
        [
            {
                "event_id": event["event_id"],
                "candidate_id": event["candidate_id"],
                "hypothesis_id": event["hypothesis_id"],
                "route_id": event["route_id"],
                "outcome": event["outcome"],
                "source_kind": event["provenance"]["source_kind"],
                "claim_boundary": event["scope"]["claim_boundary"],
                "evidence_files": event["evidence_files"],
                "reopening_condition": event["reopening_condition"],
                "decision_delta": decision_delta_for_event(
                    event,
                    candidate_index.get(event["candidate_id"]),
                ),
            }
            for event in event_values
        ],
        key=lambda item: item["event_id"],
    )
    source_counts = Counter(
        event["provenance"]["source_kind"] for event in event_values
    )
    execution_queue = selection["execution_queue"]
    return {
        "schema_version": "0.1-generated",
        "engine_id": policy["engine_id"],
        "source_hashes": {
            "policy_sha256": sha256_json(policy),
            "hypothesis_generation_policy_sha256": hypothesis_generation[
                "source_hashes"
            ]["generation_policy_sha256"],
            "typed_evidence_state_sha256": hypothesis_generation[
                "source_hashes"
            ]["typed_evidence_state_sha256"],
            "research_claim_state_sha256": hypothesis_generation[
                "source_hashes"
            ]["research_claim_state_sha256"],
            "decision_substrate_sha256": sha256_json(decisions),
            "hypotheses_sha256": file_sha256(HYPOTHESES_PATH),
            "outcome_events_sha256": sha256_json(event_values),
            "historical_baseline_anchor_sha256": (
                V0_REVIEWED_HISTORICAL_ROOT_SHA256
            ),
        },
        "gate_status": {
            "exploration_authorized": policy["gates"]["exploration"]["authorized"],
            "promotion_authorized": policy["gates"]["promotion"]["authorized"],
            "current_decision_experiment_authorized": decisions["phase_policy"][
                "experiments_authorized"
            ],
            "current_decision_bounded_exploration_authorized": decisions[
                "phase_policy"
            ]["bounded_exploration_authorized"],
            "structural_work_authorized": decisions.get(
                "execution_gates", {}
            ).get("structural", {}).get("authorized", False),
            "exploration_limits": policy["gates"]["exploration"]["limits"],
            "promotion_boundary": policy["feedback_contract"]["promotion_boundary"],
        },
        "queue_separation": policy["queue_separation"],
        "counts": {
            "normalized_hypotheses": len(normalized_hypotheses),
            "outcome_events": len(event_values),
            "candidate_proposals": len(policy["candidate_proposals"]),
            "generated_hypothesis_seeds": hypothesis_generation["counts"][
                "generated_seeds"
            ],
            "submitted_hypothesis_proposals": hypothesis_generation["counts"][
                "submitted_proposals"
            ],
            "quality_cleared_hypothesis_proposals": hypothesis_generation[
                "counts"
            ]["quality_cleared_proposals"],
            "retained_hypothesis_drafts": hypothesis_generation["counts"][
                "retained_hypothesis_drafts"
            ],
            "typed_evidence_cells": hypothesis_generation["counts"][
                "typed_evidence_cells"
            ],
            "typed_seed_eligible_cells": hypothesis_generation["counts"][
                "typed_seed_eligible_cells"
            ],
            "typed_desk_decisions": hypothesis_generation[
                "typed_evidence"
            ]["counts"].get("desk_decisions", 0),
            "typed_decided_cells": (
                hypothesis_generation["typed_evidence"]["counts"].get(
                    "decided_inapplicable_cells", 0
                )
                + hypothesis_generation["typed_evidence"]["counts"].get(
                    "decided_closed_cells", 0
                )
            ),
            "intake_candidates": sum(
                candidate.get("authorization") == "intake"
                for candidate in policy["candidate_proposals"]
            ),
            "authorized_exploration_candidates": sum(
                candidate.get("authorization") == "exploration"
                for candidate in policy["candidate_proposals"]
            ),
            "closed_candidates": sum(
                candidate.get("authorization") == "none"
                for candidate in policy["candidate_proposals"]
            ),
            "selected_explorations": len(selection["selected_sequence"]),
            "ready_explorations": len(execution_queue["ready_candidate_ids"]),
            "terminal_native_outcomes": len(
                execution_queue["terminal_candidate_ids"]
            ),
            "blocked_selected_explorations": len(
                execution_queue["blocked_candidate_ids"]
            ),
            "hard_rejected_candidates": len(selection["hard_rejected"]),
            "outcomes_by_source": {
                "historical_migration": source_counts.get(
                    "historical_migration", 0
                ),
                "native_engine_run": source_counts.get("native_engine_run", 0),
                "external_bounded_decision_run": source_counts.get(
                    "external_bounded_decision_run", 0
                ),
            },
            "outcomes_by_taxonomy": {
                outcome["id"]: outcome_counts.get(outcome["id"], 0)
                for outcome in policy["outcome_taxonomy"]
            },
        },
        "selected_sequence": selection["selected_sequence"],
        "execution_queue": execution_queue,
        "hard_rejected_candidates": selection["hard_rejected"],
        "eligible_not_selected": selection["eligible_not_selected"],
        "retrospective_validation": retrospective,
        "calibration": calibration,
        "normalized_hypotheses": normalized_hypotheses,
        "outcome_events": event_summaries,
        "historical_outcomes": [
            event
            for event in event_summaries
            if event["source_kind"] == "historical_migration"
        ],
        "native_outcomes": [
            event
            for event in event_summaries
            if event["source_kind"] == "native_engine_run"
        ],
        "external_bounded_outcomes": [
            event
            for event in event_summaries
            if event["source_kind"] == "external_bounded_decision_run"
        ],
        "route_evidence_state": route_states,
        "route_axis_contract": {
            "primary_threat_model": primary_threat_model,
            "rule": (
                "Threat-model scope, substrate decision disposition, and "
                "Engine evidence are independent axes."
            ),
            "route_count": len(route_states),
        },
        "hypothesis_generation": hypothesis_generation,
        "feedback_contract": policy["feedback_contract"],
    }


def render_state(state: dict[str, Any]) -> str:
    return json.dumps(state, indent=2, ensure_ascii=False) + "\n"


def validate_historical_outcome_baseline(
    policy: dict[str, Any], outcomes: list[dict[str, Any]]
) -> list[str]:
    problems: list[str] = []
    historical_events = {
        event.get("event_id"): event
        for event in outcomes
        if event.get("provenance", {}).get("source_kind")
        == "historical_migration"
    }
    baseline_events = {
        event.get("event_id"): event
        for event in policy.get("historical_outcome_baseline", {}).get(
            "events", []
        )
    }
    if set(historical_events) != set(baseline_events):
        problems.append(
            "historical outcome files must match the review-anchored v0 baseline; "
            f"missing={sorted(set(baseline_events) - set(historical_events))}, "
            f"extra={sorted(set(historical_events) - set(baseline_events))}"
        )
    for event_id, baseline in baseline_events.items():
        event = historical_events.get(event_id)
        if event is None:
            continue
        if sha256_json(event) != baseline.get("event_sha256"):
            problems.append(f"historical outcome baseline {event_id}: digest changed")
    if (
        baseline_events
        and set(historical_events) == HISTORICAL_BASELINE_EVENT_IDS
        and sha256_json(
            [
                historical_events[event_id]
                for event_id in sorted(HISTORICAL_BASELINE_EVENT_IDS)
            ]
        )
        != V0_REVIEWED_HISTORICAL_ROOT_SHA256
    ):
        problems.append(
            "historical outcome baseline: reviewed v0 root changed; "
            "re-baselining requires an explicit validator-code anchor change"
        )
    return problems


def validate_historical_scope_guards(
    policy: dict[str, Any], outcomes: list[dict[str, Any]]
) -> list[str]:
    problems: list[str] = []
    event_index = {event.get("event_id"): event for event in outcomes}
    for guard in policy.get("historical_scope_guards", []):
        event = event_index.get(guard.get("event_id"))
        label = f"historical scope guard {guard.get('event_id')}"
        if event is None:
            problems.append(f"{label}: event is missing")
            continue
        if sha256_json(event) != guard.get("event_sha256"):
            problems.append(f"{label}: event digest changed")
        if event.get("outcome") != guard.get("outcome"):
            problems.append(f"{label}: outcome changed")
        if event.get("scope", {}).get("curve_family") != guard.get(
            "curve_family"
        ):
            problems.append(f"{label}: curve family changed")
        observed_bits = event.get("scope", {}).get("field_bits")
        if observed_bits != guard.get("field_bits"):
            problems.append(f"{label}: field-bit scope changed")
        if set(observed_bits or []) & set(guard.get("forbidden_field_bits", [])):
            problems.append(f"{label}: forbidden field-bit scope reappeared")
    return problems


def validate_all() -> tuple[list[str], dict[str, Any]]:
    problems: list[str] = []
    problems.extend(scientific_provenance_problems())
    policy = load_json(POLICY_PATH)
    decisions = load_json(DECISION_PATH)
    hypotheses = parse_hypotheses()
    outcomes = load_outcomes()
    generation_policy = load_json(GENERATION_POLICY_PATH)
    generation_proposals = load_hypothesis_generation_records(PROPOSALS_DIR)
    generation_reviews = load_hypothesis_generation_records(REVIEWS_DIR)
    problems.extend(validate_policy(policy, decisions, hypotheses))
    generation_problems, generation_state = build_generation_state(
        generation_policy,
        decisions,
        policy,
        generation_proposals,
        generation_reviews,
    )
    problems.extend(generation_problems)
    source_reviews = {
        review["review_id"]: review
        for _, review in generation_reviews
        if isinstance(review, dict)
        and isinstance(review.get("review_id"), str)
        and review.get("reviewer_role") == "prior_art"
    }
    event_ids: list[str] = []
    for path, event in outcomes:
        problems.extend(
            validate_outcome(
                path,
                event,
                policy,
                decisions,
                hypotheses,
                source_reviews,
            )
        )
        if isinstance(event, dict) and isinstance(event.get("event_id"), str):
            event_ids.append(event["event_id"])
    if len(event_ids) != len(set(event_ids)):
        problems.append("outcome event ids must be unique")
    problems.extend(
        validate_historical_outcome_baseline(
            policy, [event for _, event in outcomes]
        )
    )
    problems.extend(
        validate_historical_scope_guards(
            policy, [event for _, event in outcomes]
        )
    )
    problems.extend(validate_native_sequence(policy, decisions, outcomes))
    problems.extend(validate_external_bounded_sequence(decisions, outcomes))
    state = build_state(
        policy,
        decisions,
        hypotheses,
        outcomes,
        generation_state,
    )
    if not state["retrospective_validation"]["passed"]:
        problems.append("historical no-reopen validation failed")
    return problems, state
