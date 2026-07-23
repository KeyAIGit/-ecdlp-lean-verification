#!/usr/bin/env python3
"""Validate the canonical pre-pilot portability rehearsal and its evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path, PurePosixPath

from lean_portability import (
    PortabilityError,
    canonical_json_bytes,
    classify_path,
    is_safe_relative,
    module_for_path,
    normalized_source_sha256,
)

ROOT = Path(__file__).resolve().parent.parent
CONTRACT_PATH = ROOT / "repo" / "PORTABILITY_REHEARSAL.json"
PILOT_PATH = ROOT / "repo" / "PILOT_PROTOCOL.json"
PRODUCT_MODEL_PATH = ROOT / "repo" / "PRODUCT_MODEL.json"
TASKS_PATH = ROOT / "tasks" / "NEXT.md"

FINAL_STATUSES = {"completed", "stopped"}
ALLOWED_STATUSES = {
    "selection_in_progress",
    "baseline_in_progress",
    "adapter_in_progress",
    "completed",
    "stopped",
}
ALLOWED_RESULTS = {"pending", "pass", "fail", "not_applicable"}
ALLOWED_DISPOSITIONS = {"build", "change", "stop"}
SNAPSHOT_CLASSIFICATIONS = {
    "build_configuration",
    "ci",
    "documentation",
    "explicitly_excluded",
    "gitlink",
    "lean_out_of_scope",
    "lean_source",
    "license",
    "other",
    "repository_internal",
    "symlink",
}
EXPECTED_ALLOWED_AXIOM_PROVENANCE = {
    "Classical.choice": {
        "kind": "axiom",
        "module": "Init.Prelude",
        "private": False,
    },
    "Quot.sound": {
        "kind": "axiom",
        "module": "Init.Core",
        "private": False,
    },
    "propext": {
        "kind": "axiom",
        "module": "Init.Core",
        "private": False,
    },
}
EXPECTED_ACCEPTED_AXIOM_GROUP = {
    "id": "lean-native-decide-generated",
    "trust_class": "compiler_generated_native_decide",
    "axioms": [
        "_private.Cedar.Data.Int64.0.Int64.toInt_neg_of_not_ge_zero._native.native_decide.ax_1_2",
        "_private.Cedar.Data.Int64.0.Int64.toInt_nonneg_of_ge_zero._native.native_decide.ax_1_1",
        "_private.Cedar.Thm.SymCC.Data.Ext.0.Cedar.Thm.msPerDay_eq._native.native_decide.ax_1_1",
        "_private.Cedar.Thm.SymCC.Data.Ext.0.Cedar.Thm.msPerDay_toInt._native.native_decide.ax_1_1",
        "_private.Cedar.Thm.SymCC.Data.Ext.0.Cedar.Thm.toDate_eq_smod._native.native_decide.ax_1_6",
        "_private.Cedar.Thm.SymCC.Data.Ext.0.Cedar.Thm.toDate_eq_smod._native.native_decide.ax_1_8",
        "_private.Cedar.Thm.SymCC.Data.Ext.0.Cedar.Thm.toInt_div_msPerDay._native.native_decide.ax_1_1",
        "_private.Cedar.Thm.SymCC.Data.Ext.0.Cedar.Thm.toInt_div_msPerDay._native.native_decide.ax_1_3",
        "_private.Cedar.Thm.SymCC.Data.Ext.0.Cedar.Thm.toInt_div_msPerDay._native.native_decide.ax_1_6",
    ],
}
EXPECTED_BASELINE_COMMANDS = [
    "cd cedar-lean && lake -R -Kenv=dev update",
    "cd cedar-lean && LEAN_NUM_THREADS=1 lake build Cedar SymCC",
    "cd cedar-lean && LEAN_NUM_THREADS=1 lake lint",
    "python scripts/lean_compiled_probe.py --source <disposable-built-checkout>",
]
EXPECTED_COMPILED_COMMANDS = {
    "write": (
        "python scripts/lean_compiled_probe.py "
        "--source <disposable-built-checkout>"
    ),
    "check": (
        "python scripts/lean_compiled_probe.py "
        "--source <disposable-built-checkout> --check"
    ),
}
EXPECTED_DEPENDENCY_REVISIONS = {
    "leanprover-community/batteries": "fa08db58b30eb033edcdab331bba000827f9f785",
    "leanprover/doc-gen4": "0bc516c1b9db83658d6475c40d9b1ed71219b921",
    "leanprover/leansqlite": "0be4df908d1a8e75b58961041e2b4973692623df",
    "leanprover/lean4-cli": "92564e5770e4d09f2d86dfbf8ada1e9c715b384c",
    "fgdorais/lean4-unicode-basic": "a2e430a4c9d3ad24078b8581fe0162fc5b0c9a6c",
    "dupuisf/BibtexQuery": "5d31b64fb703c5d77f6ef4d1fb958f9bdf1ea539",
    "acmepjz/md4lean": "6a3fb240133bcb7e1a066fdc784b3fdc304e3fc5",
}
EXPECTED_WORKSPACE_EFFECT = {
    "path": "cedar-lean/lake-manifest.json",
    "canonical_git_blob_sha256": (
        "60bb72ecf8014c3b3ea5bb9f8f3cd73633374430a31fc52a75912a163c51a986"
    ),
    "resolved_worktree_sha256": (
        "de4da87c83d920b3a13241f5cbf67d4bf46953769b398e9f0bb733939aaef51f"
    ),
    "reason": (
        "The env=dev branch adds documentation dependencies in the disposable "
        "build workspace. No canonical source or KeyAI-owned external source "
        "copy was changed."
    ),
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def safe_file(path: object) -> bool:
    return (
        isinstance(path, str)
        and is_safe_relative(path)
        and (ROOT / path).is_file()
    )


def expected_weighted_score(candidate: dict, weights: dict[str, int]) -> float | None:
    scores = candidate.get("scores")
    if not isinstance(scores, dict) or set(scores) != set(weights):
        return None
    if not all(isinstance(value, int) and 0 <= value <= 5 for value in scores.values()):
        return None
    return round(
        sum(scores[dimension] * weight / 5 for dimension, weight in weights.items()),
        2,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the canonical portability rehearsal and evidence."
    )
    parser.add_argument(
        "--require-final",
        action="store_true",
        help="Reject an in-progress contract. Intended for merge-blocking CI.",
    )
    return parser.parse_args()


def main(*, require_final: bool = False) -> int:
    errors: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    try:
        contract = load_json(CONTRACT_PATH)
        pilot = load_json(PILOT_PATH)
        product_model = load_json(PRODUCT_MODEL_PATH)
        tasks_text = TASKS_PATH.read_text(encoding="utf-8")
    except (OSError, ValueError) as exc:
        print(f"portability rehearsal check FAILED: {exc}", file=sys.stderr)
        return 1

    check(contract.get("schema_version") == "1.0", "schema_version must be 1.0")
    check(contract.get("id") == "KEYAI-PORTABILITY-001", "unexpected rehearsal id")
    check(contract.get("task_id") == "TASK-011", "rehearsal must belong to TASK-011")
    check(
        contract.get("stage") == "pre_pilot_technical_rehearsal",
        "unexpected rehearsal stage",
    )
    status = contract.get("status")
    check(status in ALLOWED_STATUSES, f"unsupported rehearsal status: {status!r}")
    if require_final:
        check(
            status in FINAL_STATUSES,
            "--require-final rejects an in-progress portability rehearsal",
        )

    boundary = contract.get("evidence_boundary", {})
    for key in (
        "external_participant",
        "customer_evidence",
        "external_pilot_evidence",
        "unlocks_task_012",
        "may_change_customer_hypothesis_status",
    ):
        check(
            boundary.get(key) is False,
            f"evidence_boundary.{key} must remain false",
        )
    check(
        boundary.get("class") == "internal_technical_rehearsal",
        "rehearsal evidence class must remain internal_technical_rehearsal",
    )

    authority = contract.get("authority", {})
    prohibited = " ".join(authority.get("prohibited", []))
    check(
        "Insert this rehearsal into repo/PILOT_PROTOCOL.json evidence_log" in prohibited,
        "authority must forbid inserting rehearsal evidence into the pilot log",
    )
    check(
        "Unlock TASK-012" in prohibited,
        "authority must explicitly forbid unlocking TASK-012",
    )

    rubric = contract.get("selection_rubric", {})
    dimensions = rubric.get("scored_dimensions", [])
    weights = {
        item.get("id"): item.get("weight")
        for item in dimensions
        if isinstance(item, dict)
    }
    check(
        len(weights) == len(dimensions) and None not in weights,
        "selection dimensions need unique ids",
    )
    check(
        all(isinstance(weight, int) and weight > 0 for weight in weights.values())
        and sum(weights.values()) == 100,
        "selection weights must be positive integers summing to 100",
    )
    candidates = rubric.get("candidates", [])
    check(isinstance(candidates, list), "selection candidates must be a list")
    candidate_ids: list[str] = []
    repositories: list[str] = []
    for candidate in candidates if isinstance(candidates, list) else []:
        candidate_id = candidate.get("id")
        candidate_ids.append(candidate_id)
        repository = candidate.get("repository")
        repositories.append(repository)
        check(
            isinstance(candidate_id, str)
            and re.fullmatch(r"CAND-[A-Z0-9-]{3,40}", candidate_id) is not None,
            f"candidate has invalid id: {candidate_id!r}",
        )
        check(
            isinstance(repository, str)
            and re.fullmatch(r"https://github\.com/[^/]+/[^/]+", repository) is not None,
            f"{candidate_id}: repository must be a GitHub repository URL",
        )
        check(
            re.fullmatch(r"[0-9a-f]{40}", candidate.get("commit_sha", "")) is not None,
            f"{candidate_id}: commit_sha must be a full Git SHA",
        )
        for key in (
            "license_spdx",
            "license_file",
            "lean_toolchain",
            "build_command",
            "activity_signal",
            "approximate_scale",
            "selection_notes",
        ):
            check(bool(candidate.get(key)), f"{candidate_id}: missing {key}")
        check(
            candidate.get("required_criteria_met") is True,
            f"{candidate_id}: every required selection criterion must pass",
        )
        expected = expected_weighted_score(candidate, weights)
        check(expected is not None, f"{candidate_id}: score dimensions are invalid")
        check(
            candidate.get("weighted_score") == expected,
            f"{candidate_id}: weighted_score must be {expected}",
        )
    check(len(candidate_ids) == len(set(candidate_ids)), "candidate ids must be unique")
    check(
        len(repositories) == len(set(repositories)),
        "candidate repositories must be unique",
    )

    selected_id = rubric.get("selected_candidate_id")
    reserve_id = rubric.get("reserve_candidate_id")
    selected = contract.get("selected_source")
    final = status in FINAL_STATUSES
    if final:
        target = rubric.get("candidate_count_target", {})
        check(
            target.get("minimum", 0) <= len(candidates) <= target.get("maximum", 0),
            "final rehearsal must retain the required candidate scorecard",
        )
        check(selected_id in candidate_ids, "selected candidate must exist in scorecard")
        check(reserve_id in candidate_ids, "reserve candidate must exist in scorecard")
        check(selected_id != reserve_id, "selected and reserve candidates must differ")
        check(isinstance(selected, dict), "final rehearsal needs selected_source")

    by_id = {
        candidate.get("id"): candidate
        for candidate in candidates
        if isinstance(candidate, dict)
    }
    if isinstance(selected, dict):
        candidate = by_id.get(selected.get("candidate_id"))
        check(
            selected.get("candidate_id") == selected_id and candidate is not None,
            "selected_source must match selected_candidate_id",
        )
        if candidate:
            for key in (
                "repository",
                "commit_sha",
                "license_spdx",
                "license_file",
                "lean_toolchain",
                "build_command",
            ):
                check(
                    selected.get(key) == candidate.get(key),
                    f"selected_source.{key} must match the scorecard",
                )
        adapter = selected.get("adapter", {})
        roots = adapter.get("module_roots", [])
        check(
            isinstance(roots, list) and bool(roots),
            "selected source needs at least one module root",
        )
        for root in roots if isinstance(roots, list) else []:
            check(
                isinstance(root, dict)
                and isinstance(root.get("path"), str)
                and is_safe_relative(root["path"]),
                "module roots must be safe relative paths",
            )
        check(
            isinstance(adapter.get("entrypoints"), list)
            and bool(adapter.get("entrypoints")),
            "adapter.entrypoints must be a non-empty list",
        )
        check(
            isinstance(adapter.get("owned_module_prefixes"), list)
            and bool(adapter.get("owned_module_prefixes")),
            "adapter.owned_module_prefixes must be a non-empty list",
        )
        check(
            isinstance(adapter.get("explicit_exclusions"), list),
            "adapter.explicit_exclusions must be a list",
        )
        check(
            re.fullmatch(r"[0-9a-f]{64}", selected.get("license_sha256", ""))
            is not None,
            "selected_source.license_sha256 must be a SHA-256",
        )
        check(
            re.fullmatch(r"[0-9a-f]{40}", selected.get("tree_sha", ""))
            is not None,
            "selected_source.tree_sha must be a full Git tree SHA",
        )
        check(
            isinstance(selected.get("toolchain_file"), str)
            and is_safe_relative(selected["toolchain_file"]),
            "selected_source.toolchain_file must be a safe relative path",
        )
        baseline_adapter = selected.get("baseline_adapter", {})
        check(
            isinstance(baseline_adapter.get("project_root"), str)
            and is_safe_relative(baseline_adapter["project_root"]),
            "baseline_adapter.project_root must be a safe relative path",
        )
        compiled_entrypoints = baseline_adapter.get("compiled_entrypoints")
        check(
            isinstance(compiled_entrypoints, list)
            and bool(compiled_entrypoints)
            and all(
                isinstance(value, str)
                and re.fullmatch(r"[A-Za-z0-9_'.]+", value) is not None
                for value in compiled_entrypoints
            ),
            "baseline_adapter.compiled_entrypoints must be Lean module names",
        )
        check(
            isinstance(compiled_entrypoints, list)
            and set(compiled_entrypoints).issubset(set(adapter.get("entrypoints", []))),
            "compiled entrypoints must be declared source entrypoints",
        )
        allowed_changes = baseline_adapter.get("allowed_workspace_changes")
        check(
            isinstance(allowed_changes, list)
            and allowed_changes == ["cedar-lean/lake-manifest.json"]
            and all(
                isinstance(value, str) and is_safe_relative(value)
                for value in allowed_changes
            ),
            "baseline_adapter.allowed_workspace_changes must be safe paths",
        )
        dependency_revisions = baseline_adapter.get(
            "resolved_dependency_revisions", {}
        )
        check(
            dependency_revisions == EXPECTED_DEPENDENCY_REVISIONS,
            "baseline_adapter must retain the exact resolved dependency revisions",
        )
        documented_effect = baseline_adapter.get("documented_workspace_effect", {})
        check(
            documented_effect == EXPECTED_WORKSPACE_EFFECT
            and documented_effect.get("path") in set(allowed_changes or []),
            "baseline_adapter must retain the exact documented workspace effect",
        )
        check(
            isinstance(baseline_adapter.get("lean_num_threads"), int)
            and baseline_adapter["lean_num_threads"] > 0,
            "baseline_adapter.lean_num_threads must be a positive integer",
        )
        execution_profile = baseline_adapter.get("execution_profile", {})
        check(
            execution_profile.get("source_trust") == "reviewed_public_source"
            and execution_profile.get("baseline_environment_policy")
            == "inherited_host_environment"
            and execution_profile.get("compiled_probe_environment_policy")
            == "fixed_allowlist"
            and execution_profile.get("compiled_probe_launcher")
            == "project_lake_env"
            and execution_profile.get("compiled_probe_output_authentication")
            == "not_independent_of_project_launcher"
            and execution_profile.get("canonical_checkout")
            == "read_only_git_object_inspection"
            and execution_profile.get("build_checkout")
            == "disposable_writable_workspace"
            and execution_profile.get("network_isolation") == "not_os_enforced"
            and execution_profile.get("filesystem_isolation") == "not_os_enforced",
            "baseline_adapter must state the exact external-execution boundary",
        )

    probe_policy = contract.get("compiled_probe_policy", {})
    allowed_axioms = probe_policy.get("allowed_axioms")
    allowed_axiom_provenance = probe_policy.get("allowed_axiom_provenance")
    forbidden_axioms = probe_policy.get("forbidden_axioms")
    check(
        isinstance(allowed_axioms, list)
        and isinstance(forbidden_axioms, list)
        and all(isinstance(value, str) and value for value in allowed_axioms)
        and all(isinstance(value, str) and value for value in forbidden_axioms)
        and not set(allowed_axioms) & set(forbidden_axioms),
        "compiled probe exact axiom policy is invalid",
    )
    check(
        allowed_axioms == sorted(EXPECTED_ALLOWED_AXIOM_PROVENANCE)
        and allowed_axiom_provenance == EXPECTED_ALLOWED_AXIOM_PROVENANCE,
        "compiled probe allowed axioms require the exact trusted base provenance",
    )
    check(
        isinstance(forbidden_axioms, list) and "sorryAx" in forbidden_axioms,
        "compiled probe policy must forbid sorryAx",
    )
    accepted_groups = probe_policy.get("accepted_axiom_groups", [])
    accepted_group_ids: list[str] = []
    accepted_group_axioms: list[str] = []
    for group in accepted_groups if isinstance(accepted_groups, list) else []:
        accepted_group_ids.append(group.get("id"))
        group_axioms = group.get("axioms", [])
        if isinstance(group_axioms, list):
            accepted_group_axioms.extend(group_axioms)
        check(
            bool(group.get("id"))
            and bool(group.get("trust_class"))
            and bool(group.get("rationale"))
            and isinstance(group_axioms, list)
            and bool(group_axioms)
            and all(isinstance(value, str) and value for value in group_axioms),
            "accepted axiom groups need id, trust_class, exact axioms, and rationale",
        )
    check(
        isinstance(accepted_groups, list)
        and len(accepted_group_ids) == len(set(accepted_group_ids))
        and len(accepted_group_axioms) == len(set(accepted_group_axioms))
        and not set(accepted_group_axioms) & set(allowed_axioms or [])
        and not set(accepted_group_axioms) & set(forbidden_axioms or []),
        "accepted axiom group ids and exact axiom names must be unique and disjoint",
    )
    check(
        isinstance(accepted_groups, list)
        and len(accepted_groups) == 1
        and {
            key: accepted_groups[0].get(key)
            for key in ("id", "trust_class", "axioms")
        }
        == EXPECTED_ACCEPTED_AXIOM_GROUP,
        "compiled probe must retain the exact native_decide trust group",
    )
    check(
        probe_policy.get("unexpected_axioms_fail") is True,
        "unexpected compiled axioms must fail the probe",
    )

    artifacts = contract.get("artifacts", {})
    artifact_paths = {
        value for value in artifacts.values() if isinstance(value, str)
    }
    check(
        len(artifact_paths) == len(artifacts)
        and all(is_safe_relative(path) for path in artifact_paths),
        "artifact paths must be unique safe repository-relative paths",
    )
    check(
        artifacts.get("snapshot")
        == f"rehearsals/{contract.get('id', '').lower()}/snapshot.json",
        "snapshot artifact must be owned by the rehearsal directory",
    )
    for key, filename in (
        ("compiled_probe", "compiled-probe.json"),
        ("baseline_evidence", "baseline.json"),
    ):
        check(
            artifacts.get(key)
            == f"rehearsals/{contract.get('id', '').lower()}/{filename}",
            f"{key} artifact must be owned by the rehearsal directory",
        )
    check(
        artifacts.get("report") == "notes/reviews/PORTABILITY_REHEARSAL_001.md",
        "report artifact must use the canonical review-packet path",
    )
    pilot_evidence_paths = {
        path
        for record in pilot.get("evidence_log", [])
        if isinstance(record, dict)
        for path in record.get("evidence_files", [])
        if isinstance(path, str)
    }
    check(
        not artifact_paths & pilot_evidence_paths,
        "rehearsal artifacts must not appear in the external pilot evidence log",
    )
    boundary_tokens = {
        str(contract.get("id", "")).lower(),
        str(contract.get("selected_source", {}).get("commit_sha", "")).lower(),
        str(contract.get("selected_source", {}).get("tree_sha", "")).lower(),
        str(contract.get("selected_source", {}).get("license_sha256", "")).lower(),
        str(contract.get("selected_source", {}).get("candidate_id", "")).lower(),
        str(contract.get("selected_source", {}).get("repository", "")).lower(),
        *(path.lower() for path in artifact_paths),
    }
    for candidate in candidates if isinstance(candidates, list) else []:
        if not isinstance(candidate, dict):
            continue
        for key in ("id", "repository", "commit_sha"):
            value = candidate.get(key)
            if isinstance(value, str) and value:
                boundary_tokens.add(value.lower())
        candidate_slug = (
            str(candidate.get("repository", "")).rstrip("/").split("/")[-1].lower()
        )
        if len(candidate_slug) >= 5:
            boundary_tokens.add(candidate_slug)

    def collect_contract_hashes(value: object) -> None:
        if isinstance(value, dict):
            for nested in value.values():
                collect_contract_hashes(nested)
        elif isinstance(value, list):
            for nested in value:
                collect_contract_hashes(nested)
        elif isinstance(value, str) and re.fullmatch(
            r"(?:[0-9a-f]{40}|[0-9a-f]{64})", value.lower()
        ):
            boundary_tokens.add(value.lower())

    collect_contract_hashes(contract)
    artifact_digest_paths = [
        artifacts.get("snapshot"),
        artifacts.get("compiled_probe"),
        artifacts.get("baseline_evidence"),
    ]
    for artifact_path in artifact_digest_paths:
        if not isinstance(artifact_path, str) or not safe_file(artifact_path):
            continue
        try:
            evidence = load_json(ROOT / artifact_path)
        except ValueError:
            continue
        targeted_values = [
            evidence.get("snapshot_sha256"),
            evidence.get("content_manifest_sha256"),
            evidence.get("probe_sha256"),
            evidence.get("evidence_sha256"),
            evidence.get("generator", {}).get("sha256"),
            evidence.get("source", {})
            .get("compiled_artifact_manifest", {})
            .get("manifest_sha256"),
            evidence.get("environment", {})
            .get("execution_profile", {})
            .get("lake_launcher_sha256"),
        ]
        for value in targeted_values:
            if isinstance(value, str) and value:
                boundary_tokens.add(value.lower())
    repository_slug = (
        str(contract.get("selected_source", {}).get("repository", ""))
        .rstrip("/")
        .split("/")[-1]
        .lower()
    )
    if repository_slug:
        boundary_tokens.add(repository_slug)
        boundary_tokens.add(repository_slug.split("-")[0])
    boundary_tokens = {token for token in boundary_tokens if token}
    public_paths = [
        ROOT / "index.html",
        ROOT / "dashboard.html",
        ROOT / "explore.html",
        ROOT / "pilot.html",
        ROOT / "assets" / "site.css",
        ROOT / "assets" / "site.js",
        ROOT / "CNAME",
        ROOT / "README.md",
        ROOT / "ROADMAP.md",
        ROOT / "STATUS.md",
        ROOT / "COVERAGE.md",
        ROOT / "VERIFIED.md",
        ROOT / "TRUST_REPORT.md",
        ROOT / "ABSTRACT_SCOPE.md",
        ROOT / "BARRIERS.md",
        ROOT / "notes" / "SECURITY_SCOPE.md",
    ]
    optional_public_paths = [
        ROOT / "scripts" / "site_generator.py",
        ROOT / "domains" / "registry.json",
        *sorted((ROOT / "domains").glob("*/README.md")),
    ]
    public_paths.extend(path for path in optional_public_paths if path.is_file())
    for path in public_paths:
        try:
            public_text = path.read_text(encoding="utf-8").lower()
        except OSError as exc:
            errors.append(f"cannot inspect public surface {path.name}: {exc}")
            continue
        leaked = sorted(token for token in boundary_tokens if token in public_text)
        check(
            not leaked,
            f"{path.name} contains internal portability rehearsal evidence: {leaked}",
        )
    control_surface_text = (
        json.dumps(pilot, sort_keys=True).lower()
        + json.dumps(product_model, sort_keys=True).lower()
        + tasks_text.lower()
    )
    leaked_controls = sorted(
        token for token in boundary_tokens if token in control_surface_text
    )
    check(
        not leaked_controls,
        "rehearsal evidence leaked into pilot, product, or task control surfaces: "
        f"{leaked_controls}",
    )

    metrics = contract.get("metrics", [])
    metric_ids = [item.get("id") for item in metrics if isinstance(item, dict)]
    check(len(metric_ids) == len(set(metric_ids)), "metric ids must be unique")
    required_metrics = {
        "tracked-file-classification",
        "lean-module-coverage",
        "deterministic-snapshot",
        "source-worktree-drift",
        "project-specific-core-branches",
        "silent-unsupported-loss",
        "baseline-build",
        "keyai-non-regression",
        "manual-generator-edits",
        "compiled-declaration-trust",
        "external-execution-isolation",
        "compiled-evidence-authenticity",
    }
    check(
        set(metric_ids) == required_metrics,
        "rehearsal metrics must preserve the complete fixed gate set",
    )
    for metric in metrics if isinstance(metrics, list) else []:
        result = metric.get("result")
        check(
            metric.get("required_for_build") is True,
            f"{metric.get('id')}: every fixed rehearsal metric must remain required",
        )
        check(
            result in ALLOWED_RESULTS,
            f"{metric.get('id')}: unsupported metric result {result!r}",
        )
        evidence = metric.get("evidence")
        check(
            isinstance(evidence, list),
            f"{metric.get('id')}: evidence must be a list",
        )
        if final and result != "pending":
            check(
                bool(evidence) and all(safe_file(path) for path in evidence),
                f"{metric.get('id')}: final metric needs existing evidence files",
            )
    if final:
        check(
            all(metric.get("result") != "pending" for metric in metrics),
            "a final rehearsal cannot retain pending metrics",
        )
    metrics_by_id = {
        metric.get("id"): metric
        for metric in metrics
        if isinstance(metric, dict)
    }
    check(
        metrics_by_id.get("external-execution-isolation", {}).get("result")
        == "fail",
        "this host must not claim OS-enforced external execution isolation",
    )
    check(
        metrics_by_id.get("compiled-evidence-authenticity", {}).get("result")
        == "fail",
        "project-launched compiled evidence must not claim independent authenticity",
    )

    decision_rules = contract.get("decision_rules", {})
    change_plan = decision_rules.get("change_plan", {})
    change_gaps = change_plan.get("gaps", [])
    change_gaps_by_id = {
        gap.get("metric_id"): gap
        for gap in change_gaps
        if isinstance(gap, dict) and isinstance(gap.get("metric_id"), str)
    }
    isolation_gap = change_gaps_by_id.get("external-execution-isolation", {})
    authenticity_gap = change_gaps_by_id.get(
        "compiled-evidence-authenticity", {}
    )
    check(
        change_plan.get("owner") == "architecture_validation"
        and isinstance(change_gaps, list)
        and len(change_gaps) == 2
        and len(change_gaps_by_id) == 2
        and set(change_gaps_by_id)
        == {
            "external-execution-isolation",
            "compiled-evidence-authenticity",
        }
        and all(
            gap.get("owner") == "architecture_validation"
            and bool(gap.get("smallest_next_test"))
            and bool(gap.get("stop_condition"))
            for gap in change_gaps
            if isinstance(gap, dict)
        )
        and "secret" in isolation_gap.get("smallest_next_test", "").lower()
        and "network" in isolation_gap.get("smallest_next_test", "").lower()
        and "forged KEYAI output"
        in authenticity_gap.get("smallest_next_test", "")
        and "shadow"
        in authenticity_gap.get("smallest_next_test", "").lower()
        and bool(change_plan.get("scope_guard"))
        and "TASK-012" in change_plan.get("scope_guard", ""),
        "CHANGE disposition needs one owned hostile test and stop condition per failed gap",
    )

    baseline = contract.get("baseline", {})
    if final:
        check(
            baseline.get("status") in {"passed", "failed"},
            "final baseline status must be passed or failed",
        )
        check(bool(baseline.get("performed_on")), "final baseline needs a date")
        check(bool(baseline.get("environment")), "final baseline needs environment")
        check(
            baseline.get("commands") == EXPECTED_BASELINE_COMMANDS,
            "final baseline must retain the exact documented commands",
        )
        check(
            baseline.get("source_clean_before") is True
            and baseline.get("source_clean_after") is True,
            "source checkout must be clean before and after the baseline",
        )
        check(
            bool(baseline.get("evidence_files"))
            and all(safe_file(path) for path in baseline.get("evidence_files", [])),
            "final baseline needs existing evidence files",
        )

    runs = contract.get("runs", [])
    check(isinstance(runs, list), "runs must be a list")
    run_ids: list[str] = []
    expected_commands = {
        "write": "python scripts/lean_portability.py --source <canonical-checkout>",
        "check": (
            "python scripts/lean_portability.py --source <canonical-checkout> --check"
        ),
    }
    for run in runs if isinstance(runs, list) else []:
        run_ids.append(run.get("id"))
        check(
            re.fullmatch(r"RUN-[A-Z0-9-]{3,40}", run.get("id", "")) is not None,
            f"invalid run id: {run.get('id')!r}",
        )
        check(
            re.fullmatch(r"\d{4}-\d{2}-\d{2}", run.get("performed_on", "")) is not None,
            f"{run.get('id')}: performed_on must be an ISO date",
        )
        check(
            re.fullmatch(r"[0-9a-f]{64}", run.get("snapshot_sha256", "")) is not None,
            f"{run.get('id')}: invalid snapshot digest",
        )
        check(
            re.fullmatch(r"[0-9a-f]{64}", run.get("generator_sha256", "")) is not None,
            f"{run.get('id')}: invalid generator digest",
        )
        mode = run.get("mode")
        check(
            mode in expected_commands
            and run.get("command") == expected_commands.get(mode),
            f"{run.get('id')}: snapshot command or mode is invalid",
        )
        check(
            re.fullmatch(r"[0-9a-f]{40}", run.get("source_tree_sha", ""))
            is not None,
            f"{run.get('id')}: invalid source tree digest",
        )
        check(
            run.get("source_status_sha256")
            == hashlib.sha256(b"").hexdigest(),
            f"{run.get('id')}: source status must attest to an empty porcelain record",
        )
        check(
            run.get("source_clean_before") is True
            and run.get("source_clean_after") is True,
            f"{run.get('id')}: source must remain clean",
        )
    check(len(run_ids) == len(set(run_ids)), "run ids must be unique")
    check(len(runs) == 2, "rehearsal must retain exactly two snapshot runs")
    check(
        {run.get("mode") for run in runs if isinstance(run, dict)}
        == {"write", "check"},
        "snapshot runs must retain one write and one independent check mode",
    )
    check(
        len(
            {
                (
                    run.get("source_commit_sha"),
                    run.get("source_tree_sha"),
                    run.get("snapshot_sha256"),
                    run.get("generator_sha256"),
                )
                for run in runs
                if isinstance(run, dict)
            }
        )
        == 1,
        "snapshot runs must bind the same commit, tree, artifact, and generator",
    )

    decision = contract.get("decision", {})
    if not final:
        check(
            decision.get("status") == "pending"
            and decision.get("disposition") is None
            and decision.get("performed_on") is None
            and decision.get("summary") is None
            and decision.get("evidence_files") == [],
            "an in-progress rehearsal must retain a fully pending decision",
        )
    if final:
        disposition = decision.get("disposition")
        check(
            disposition in ALLOWED_DISPOSITIONS,
            "final decision must be build, change, or stop",
        )
        check(decision.get("status") == "completed", "final decision must be completed")
        check(bool(decision.get("performed_on")), "final decision needs a date")
        check(bool(decision.get("summary")), "final decision needs a summary")
        check(
            bool(decision.get("evidence_files"))
            and all(safe_file(path) for path in decision.get("evidence_files", [])),
            "final decision needs existing evidence files",
        )
        check(
            (status == "stopped") == (disposition == "stop"),
            "stopped status and stop disposition must agree",
        )
        required_results = {
            metric.get("result")
            for metric in metrics
            if metric.get("required_for_build")
        }
        if disposition == "build":
            check(
                required_results == {"pass"},
                "build disposition requires every required metric to pass",
            )
            check(
                baseline.get("status") == "passed",
                "build disposition requires a passing baseline",
            )
            check(len(runs) >= 2, "build disposition requires two clean snapshot runs")
            check(
                len({run.get("snapshot_sha256") for run in runs}) == 1,
                "build disposition requires identical snapshot digests",
            )
        if disposition == "change":
            check(
                "fail" in required_results,
                "change disposition requires at least one failed required metric",
            )
            failed_metric_ids = {
                metric.get("id")
                for metric in metrics
                if isinstance(metric, dict) and metric.get("result") == "fail"
            }
            check(
                failed_metric_ids
                == {
                    "external-execution-isolation",
                    "compiled-evidence-authenticity",
                }
                and baseline.get("status") == "passed",
                "CHANGE must be explained exactly by the two execution-boundary failures",
            )

    snapshot_path = artifacts.get("snapshot")
    snapshot: dict = {}
    if isinstance(snapshot_path, str):
        check(not final or safe_file(snapshot_path), "final snapshot artifact is missing")
        if safe_file(snapshot_path):
            try:
                snapshot = load_json(ROOT / snapshot_path)
            except ValueError as exc:
                errors.append(f"snapshot is invalid JSON: {exc}")
                snapshot = {}
            digest = snapshot.get("snapshot_sha256")
            unsigned = dict(snapshot)
            unsigned.pop("snapshot_sha256", None)
            expected_digest = hashlib.sha256(canonical_json_bytes(unsigned)).hexdigest()
            check(digest == expected_digest, "snapshot_sha256 does not match snapshot content")
            file_digest = hashlib.sha256(
                canonical_json_bytes(snapshot.get("files", []))
            ).hexdigest()
            check(
                snapshot.get("content_manifest_sha256") == file_digest,
                "content manifest digest does not match snapshot files",
            )
            check(
                snapshot.get("external_evidence") is False
                and snapshot.get("unlocks_task_012") is False,
                "snapshot must remain internal and unable to unlock TASK-012",
            )
            check(
                snapshot.get("rehearsal_id") == contract.get("id")
                and snapshot.get("task_id") == contract.get("task_id")
                and snapshot.get("evidence_class") == boundary.get("class"),
                "snapshot identity or evidence class does not match the contract",
            )
            check(
                snapshot.get("generator")
                == {
                    "id": "keyai-lean-portability",
                    "version": "1.0",
                    "path": "scripts/lean_portability.py",
                },
                "snapshot generator identity is invalid",
            )
            if isinstance(selected, dict):
                source = snapshot.get("source", {})
                for key in (
                    "repository",
                    "commit_sha",
                    "tree_sha",
                    "license_spdx",
                    "license_file",
                    "license_sha256",
                    "toolchain_file",
                    "lean_toolchain",
                ):
                    check(
                        source.get(key) == selected.get(key),
                        f"snapshot source {key} must match selected_source",
                    )
                check(
                    snapshot.get("adapter") == selected.get("adapter"),
                    "snapshot adapter must match the declarative selected-source adapter",
                )
                check(
                    snapshot.get("entrypoints")
                    == selected.get("adapter", {}).get("entrypoints"),
                    "snapshot entrypoints must match the declarative adapter",
                )
            summary = snapshot.get("summary", {})
            check(
                summary.get("tracked_files") == summary.get("classified_files"),
                "snapshot must classify every tracked file",
            )
            check(
                summary.get("lean_modules") == len(snapshot.get("modules", []))
                and summary.get("source_declarations")
                == len(snapshot.get("declarations", []))
                and summary.get("tracked_files") == len(snapshot.get("files", [])),
                "snapshot summary counts do not match snapshot records",
            )
            file_records = snapshot.get("files", [])
            valid_file_records = (
                file_records
                if isinstance(file_records, list)
                and all(isinstance(item, dict) for item in file_records)
                else []
            )
            file_paths = [
                item.get("path")
                for item in valid_file_records
                if isinstance(item.get("path"), str)
            ]
            check(
                len(valid_file_records) == len(file_records)
                and len(file_paths) == len(file_records)
                and all(is_safe_relative(path) for path in file_paths)
                and file_paths == sorted(set(file_paths)),
                "snapshot file paths must be safe, unique, and canonically sorted",
            )
            classifications = [
                item.get("classification") for item in valid_file_records
            ]
            classification_types_valid = all(
                isinstance(label, str) for label in classifications
            )
            derived_classification_counts = (
                dict(sorted(Counter(classifications).items()))
                if classification_types_valid
                else {}
            )
            check(
                classification_types_valid
                and all(label in SNAPSHOT_CLASSIFICATIONS for label in classifications)
                and summary.get("classification_counts")
                == derived_classification_counts
                and summary.get("classified_files") == len(file_records)
                and summary.get("tracked_files") == len(file_records),
                "snapshot classifications and counts must derive from file records",
            )
            check(
                all(
                    isinstance(item.get("bytes"), int)
                    and item.get("bytes") >= 0
                    and (
                        item.get("sha256") is None
                        if item.get("classification") == "gitlink"
                        else isinstance(item.get("sha256"), str)
                        and re.fullmatch(
                            r"[0-9a-f]{64}", item.get("sha256", "")
                        )
                        is not None
                    )
                    and isinstance(item.get("git_object_id"), str)
                    and re.fullmatch(
                        r"[0-9a-f]{40}", item.get("git_object_id", "")
                    )
                    is not None
                    for item in valid_file_records
                ),
                "snapshot file records need valid sizes and object digests",
            )
            structural_adapter = (
                selected.get("adapter", {})
                if isinstance(selected, dict)
                else {}
            )
            structural_roots = structural_adapter.get("module_roots", [])
            derived_modules_by_path: dict[str, str | None] = {}
            mode_type_classification_valid = True
            for item in valid_file_records:
                path = item.get("path")
                if not isinstance(path, str):
                    mode_type_classification_valid = False
                    continue
                try:
                    derived_module = module_for_path(path, structural_roots)
                except (PortabilityError, TypeError, ValueError):
                    mode_type_classification_valid = False
                    continue
                derived_modules_by_path[path] = derived_module
                mode = item.get("git_mode")
                object_type = item.get("git_object_type")
                classification = item.get("classification")
                if mode == "160000" or object_type == "commit":
                    valid = (
                        mode == "160000"
                        and object_type == "commit"
                        and classification == "gitlink"
                        and item.get("bytes") == 0
                        and item.get("sha256") is None
                        and "module" not in item
                    )
                elif mode == "120000":
                    valid = (
                        object_type == "blob"
                        and classification == "symlink"
                        and "module" not in item
                    )
                elif mode in {"100644", "100755"}:
                    expected_classification = classify_path(
                        path,
                        derived_module,
                        structural_adapter,
                    )
                    valid = (
                        object_type == "blob"
                        and classification == expected_classification
                        and (
                            item.get("module") == derived_module
                            if classification == "lean_source"
                            else "module" not in item
                        )
                    )
                else:
                    valid = False
                if not valid:
                    mode_type_classification_valid = False
            check(
                mode_type_classification_valid,
                "snapshot Git mode, object type, classification, and file module must derive from the adapter",
            )
            lean_file_records = [
                item
                for item in valid_file_records
                if item.get("classification") == "lean_source"
            ]
            lean_file_paths = {
                item.get("path")
                for item in lean_file_records
                if isinstance(item.get("path"), str)
            }
            check(
                len(lean_file_paths) == len(lean_file_records)
                and all(
                    isinstance(item.get("module"), str)
                    and bool(item.get("module"))
                    and isinstance(item.get("imports"), list)
                    and all(
                        isinstance(value, str) and bool(value)
                        for value in item.get("imports", [])
                    )
                    and item.get("imports")
                    == sorted(set(item.get("imports", [])))
                    and all(
                        isinstance(item.get(key), int) and item.get(key) >= 0
                        for key in (
                            "declaration_count",
                            "anonymous_instance_count",
                            "sorry_token_count",
                            "admit_token_count",
                        )
                    )
                    for item in lean_file_records
                ),
                "snapshot Lean file records are invalid",
            )
            module_records = snapshot.get("modules", [])
            valid_module_records = (
                module_records
                if isinstance(module_records, list)
                and all(isinstance(item, dict) for item in module_records)
                else []
            )
            module_names = [
                item.get("module")
                for item in valid_module_records
                if isinstance(item.get("module"), str)
            ]
            module_files = [
                item.get("file")
                for item in valid_module_records
                if isinstance(item.get("file"), str)
            ]
            check(
                len(valid_module_records) == len(module_records)
                and len(module_names) == len(module_records)
                and module_names == sorted(set(module_names))
                and len(module_files) == len(module_records)
                and len(module_files) == len(set(module_files))
                and set(module_files) == lean_file_paths,
                "snapshot modules must form a sorted module-to-file bijection",
            )
            check(
                all(
                    derived_modules_by_path.get(module.get("file"))
                    == module.get("module")
                    for module in valid_module_records
                ),
                "snapshot module names must derive from file paths and module roots",
            )
            module_name_set = set(module_names)
            lean_file_by_path = {
                item["path"]: item
                for item in lean_file_records
                if isinstance(item.get("path"), str)
            }
            module_partitions_valid = True
            for module in valid_module_records:
                imports = module.get("imports")
                internal = module.get("internal_imports")
                external = module.get("external_imports")
                file_record = lean_file_by_path.get(module.get("file"))
                if (
                    not isinstance(imports, list)
                    or not isinstance(internal, list)
                    or not isinstance(external, list)
                    or not all(isinstance(value, str) for value in imports)
                    or not all(isinstance(value, str) for value in internal)
                    or not all(isinstance(value, str) for value in external)
                    or imports != sorted(set(imports))
                    or internal != sorted(set(internal))
                    or external != sorted(set(external))
                    or set(internal) & set(external)
                    or set(internal) | set(external) != set(imports)
                    or internal
                    != sorted(value for value in imports if value in module_name_set)
                    or external
                    != sorted(value for value in imports if value not in module_name_set)
                    or file_record is None
                    or file_record.get("module") != module.get("module")
                    or file_record.get("imports") != imports
                ):
                    module_partitions_valid = False
                    break
            check(
                module_partitions_valid,
                "snapshot module imports must exactly partition internal and external dependencies",
            )
            declaration_records = snapshot.get("declarations", [])
            valid_declaration_records = (
                declaration_records
                if isinstance(declaration_records, list)
                and all(isinstance(item, dict) for item in declaration_records)
                else []
            )
            declaration_keys = [
                (
                    item.get("file"),
                    item.get("line"),
                    item.get("qualified_name"),
                )
                for item in valid_declaration_records
            ]
            declaration_key_types_valid = all(
                isinstance(file, str)
                and isinstance(line, int)
                and isinstance(name, str)
                for file, line, name in declaration_keys
            )
            check(
                len(valid_declaration_records) == len(declaration_records)
                and declaration_key_types_valid
                and declaration_keys == sorted(set(declaration_keys))
                and all(
                    item.get("file") in lean_file_paths
                    and isinstance(item.get("line"), int)
                    and item.get("line") > 0
                    and isinstance(item.get("qualified_name"), str)
                    and bool(item.get("qualified_name"))
                    and isinstance(item.get("name"), str)
                    and bool(item.get("name"))
                    and isinstance(item.get("kind"), str)
                    and bool(item.get("kind"))
                    and item.get("visibility")
                    in {"public", "private", "module_private"}
                    for item in valid_declaration_records
                ),
                "snapshot declarations must be valid, unique, and canonically sorted",
            )
            declarations_per_file = Counter(
                item.get("file") for item in valid_declaration_records
            )
            check(
                all(
                    item.get("declaration_count")
                    == declarations_per_file[item.get("path")]
                    for item in lean_file_records
                )
                and summary.get("source_declarations")
                == len(declaration_records)
                and summary.get("public_source_declarations")
                == sum(
                    item.get("visibility") == "public"
                    for item in valid_declaration_records
                )
                and summary.get("anonymous_instances")
                == sum(
                    item.get("anonymous_instance_count", 0)
                    for item in lean_file_records
                )
                and summary.get("sorry_tokens")
                == sum(item.get("sorry_token_count", 0) for item in lean_file_records)
                and summary.get("admit_tokens")
                == sum(item.get("admit_token_count", 0) for item in lean_file_records),
                "snapshot declaration and trust-token summaries must derive from file records",
            )
            derived_axiom_headings = sorted(
                item.get("qualified_name")
                for item in valid_declaration_records
                if item.get("kind") in {"axiom", "constant"}
                and isinstance(item.get("qualified_name"), str)
            )
            derived_unsupported = sorted(
                item.get("path")
                for item in valid_file_records
                if isinstance(item.get("path"), str)
                and (
                    item.get("classification") == "lean_out_of_scope"
                    or (
                        item.get("path", "").lower().endswith(".lean")
                        and item.get("classification") in {"symlink", "gitlink"}
                    )
                )
            )
            check(
                snapshot.get("axiom_or_constant_declarations")
                == derived_axiom_headings
                and summary.get("axiom_or_constant_declarations")
                == len(derived_axiom_headings)
                and snapshot.get("unsupported_lean_files") == derived_unsupported
                and summary.get("unsupported_lean_files")
                == len(derived_unsupported),
                "snapshot unsupported and axiom-heading records must be independently derivable",
            )
            expected_generator_digest = normalized_source_sha256(
                ROOT / "scripts" / "lean_portability.py"
            )
            for run in runs if isinstance(runs, list) else []:
                check(
                    run.get("source_commit_sha") == selected.get("commit_sha"),
                    f"{run.get('id')}: source commit does not match selected source",
                )
                check(
                    run.get("source_tree_sha") == selected.get("tree_sha"),
                    f"{run.get('id')}: source tree does not match selected source",
                )
                check(
                    run.get("snapshot_sha256") == digest,
                    f"{run.get('id')}: snapshot digest does not match the artifact",
                )
                check(
                    run.get("generator_sha256") == expected_generator_digest,
                    f"{run.get('id')}: generator digest does not match current code",
                )
            if decision.get("disposition") == "build":
                check(
                    summary.get("unsupported_lean_files") == 0,
                    "build disposition requires zero unsupported Lean files",
                )

    compiled_probe_path = artifacts.get("compiled_probe")
    compiled_probe: dict = {}
    if isinstance(compiled_probe_path, str):
        check(
            not final or safe_file(compiled_probe_path),
            "final compiled probe is missing",
        )
        if safe_file(compiled_probe_path):
            try:
                compiled_probe = load_json(ROOT / compiled_probe_path)
            except ValueError as exc:
                errors.append(f"compiled probe is invalid JSON: {exc}")
                compiled_probe = {}
            digest = compiled_probe.get("probe_sha256")
            unsigned = dict(compiled_probe)
            unsigned.pop("probe_sha256", None)
            check(
                digest == hashlib.sha256(canonical_json_bytes(unsigned)).hexdigest(),
                "compiled probe digest does not match its content",
            )
            check(
                compiled_probe.get("rehearsal_id") == contract.get("id")
                and compiled_probe.get("task_id") == contract.get("task_id")
                and compiled_probe.get("evidence_class") == boundary.get("class")
                and compiled_probe.get("external_evidence") is False
                and compiled_probe.get("unlocks_task_012") is False,
                "compiled probe identity or evidence boundary is invalid",
            )
            check(
                compiled_probe.get("generator")
                == {
                    "id": "keyai-lean-compiled-probe",
                    "version": "1.0",
                    "path": "scripts/lean_compiled_probe.py",
                    "sha256": normalized_source_sha256(
                        ROOT / "scripts" / "lean_compiled_probe.py"
                    ),
                },
                "compiled probe generator identity is invalid",
            )
            source = compiled_probe.get("source", {})
            if isinstance(selected, dict):
                baseline_adapter = selected.get("baseline_adapter", {})
                check(
                    source.get("repository") == selected.get("repository")
                    and source.get("commit_sha") == selected.get("commit_sha")
                    and source.get("tree_sha") == selected.get("tree_sha")
                    and source.get("snapshot_sha256")
                    == snapshot.get("snapshot_sha256"),
                    "compiled probe source does not match selected source",
                )
                check(
                    source.get("project_root")
                    == baseline_adapter.get("project_root")
                    and source.get("compiled_entrypoints")
                    == baseline_adapter.get("compiled_entrypoints")
                    and source.get("allowed_workspace_changes")
                    == baseline_adapter.get("allowed_workspace_changes"),
                    "compiled probe build adapter does not match selected_source",
                )
                check(
                    source.get("observed_workspace_changes")
                    == baseline_adapter.get("allowed_workspace_changes"),
                    "compiled probe workspace changes must exactly match the documented effect",
                )
                compiled_modules = source.get("compiled_modules", [])
                lexical_modules = source.get("lexical_closure_modules", [])
                snapshot_modules = {
                    module.get("module")
                    for module in snapshot.get("modules", [])
                    if isinstance(module, dict)
                }
                check(
                    isinstance(compiled_modules, list)
                    and compiled_modules == sorted(set(compiled_modules))
                    and set(compiled_modules) <= snapshot_modules
                    and set(baseline_adapter.get("compiled_entrypoints", []))
                    <= set(compiled_modules),
                    "compiled probe module closure is invalid",
                )
                check(
                    isinstance(lexical_modules, list)
                    and lexical_modules == sorted(set(lexical_modules))
                    and set(lexical_modules) <= snapshot_modules,
                    "compiled probe lexical closure is invalid",
                )
                difference = source.get("closure_difference", {})
                check(
                    difference.get("compiled_only")
                    == sorted(set(compiled_modules) - set(lexical_modules))
                    and difference.get("lexical_only")
                    == sorted(set(lexical_modules) - set(compiled_modules)),
                    "compiled and lexical closure difference is inconsistent",
                )
                build_manifest = source.get("compiled_artifact_manifest", {})
                manifest_records = build_manifest.get("records", [])
                manifest_modules = [
                    record.get("module")
                    for record in manifest_records
                    if isinstance(record, dict)
                ]
                check(
                    build_manifest.get("module_oleans") == len(compiled_modules)
                    == len(manifest_records)
                    and manifest_modules == sorted(compiled_modules)
                    and all(
                        isinstance(record.get("module"), str)
                        and record.get("path")
                        == (
                            ".lake/build/lib/lean/"
                            + record["module"].replace(".", "/")
                            + ".olean"
                        )
                        and isinstance(record.get("bytes"), int)
                        and record.get("bytes") > 0
                        and re.fullmatch(
                            r"[0-9a-f]{64}",
                            record.get("sha256", ""),
                        )
                        is not None
                        for record in manifest_records
                        if isinstance(record, dict)
                    )
                    and re.fullmatch(
                        r"[0-9a-f]{64}",
                        build_manifest.get("manifest_sha256", ""),
                    )
                    is not None
                    and build_manifest.get("manifest_sha256")
                    == hashlib.sha256(
                        canonical_json_bytes(manifest_records)
                    ).hexdigest(),
                    "compiled artifact manifest is invalid",
                )
                check(
                    compiled_probe.get("environment", {}).get("lean_num_threads")
                    == baseline_adapter.get("lean_num_threads"),
                    "compiled probe thread constraint does not match selected_source",
                )
                execution = compiled_probe.get("environment", {}).get(
                    "execution_profile", {}
                )
                inherited_environment_keys = execution.get(
                    "inherited_environment_keys", []
                )
                check(
                    execution.get("environment_policy")
                    == baseline_adapter.get("execution_profile", {}).get(
                        "compiled_probe_environment_policy"
                    )
                    and isinstance(inherited_environment_keys, list)
                    and inherited_environment_keys
                    == sorted(set(inherited_environment_keys))
                    and set(inherited_environment_keys)
                    <= {
                        "COMSPEC",
                        "ELAN_HOME",
                        "NUMBER_OF_PROCESSORS",
                        "PATHEXT",
                        "PROCESSOR_ARCHITECTURE",
                        "SYSTEMROOT",
                        "WINDIR",
                    }
                    and execution.get("secret_like_environment_keys_inherited") == []
                    and execution.get("elan_home_source")
                    in {"parent_environment", "derived_from_lake_launcher"}
                    and execution.get("lake_discovery")
                    == "host_path_or_elan_fallback"
                    and re.fullmatch(
                        r"[0-9a-f]{64}",
                        execution.get("lake_launcher_sha256", ""),
                    )
                    is not None
                    and execution.get("compiled_probe_launcher")
                    == "project_lake_env"
                    and execution.get("compiled_probe_output_authentication")
                    == "not_independent_of_project_launcher"
                    and execution.get("isolated_home_and_temp") is True
                    and execution.get("git_optional_locks") is False
                    and execution.get("network_isolation") == "not_os_enforced"
                    and execution.get("filesystem_isolation") == "not_os_enforced"
                    and execution.get("source_workspace")
                    == "disposable_checkout",
                    "compiled probe execution profile is invalid",
                )
                check(
                    any(
                        isinstance(item, str)
                        and "not independently authenticated" in item
                        for item in compiled_probe.get("limitations", [])
                    ),
                    "compiled probe must disclose its unauthenticated project launcher and output channel",
                )
            check(
                compiled_probe.get("trust_policy") == probe_policy,
                "compiled probe trust policy does not exactly match the contract",
            )
            declaration_records = compiled_probe.get("declarations", [])
            compiled_modules_set = set(source.get("compiled_modules", []))
            compiled_names = [
                record.get("name")
                for record in declaration_records
                if isinstance(record, dict)
            ]
            check(
                isinstance(declaration_records, list)
                and bool(declaration_records)
                and len(compiled_names) == len(declaration_records)
                and all(isinstance(name, str) and name for name in compiled_names)
                and compiled_names == sorted(set(compiled_names))
                and all(
                    record.get("visibility") == "public"
                    and record.get("status") == "found"
                    and record.get("module") in compiled_modules_set
                    and isinstance(record.get("axioms"), list)
                    and record.get("axioms")
                    == sorted(set(record.get("axioms", [])))
                    and all(
                        isinstance(axiom, str) and axiom
                        for axiom in record.get("axioms", [])
                    )
                    for record in declaration_records
                    if isinstance(record, dict)
                ),
                "compiled declaration ledger is invalid",
            )
            snapshot_files_in_closure = {
                module.get("file")
                for module in snapshot.get("modules", [])
                if isinstance(module, dict)
                and module.get("module") in compiled_modules_set
            }
            expected_source_names = {
                declaration.get("qualified_name")
                for declaration in snapshot.get("declarations", [])
                if isinstance(declaration, dict)
                and declaration.get("visibility") == "public"
                and declaration.get("file") in snapshot_files_in_closure
            }
            check(
                None not in expected_source_names
                and len(expected_source_names)
                == sum(
                    1
                    for declaration in snapshot.get("declarations", [])
                    if isinstance(declaration, dict)
                    and declaration.get("visibility") == "public"
                    and declaration.get("file") in snapshot_files_in_closure
                ),
                "source snapshot has duplicate or unnamed public closure declarations",
            )
            expected_missing = sorted(expected_source_names - set(compiled_names))
            check(
                compiled_probe.get("missing_declarations") == expected_missing == [],
                "compiled declaration ledger does not resolve the source inventory",
            )
            coverage = compiled_probe.get("coverage", {})
            check(
                coverage.get("compiled_public_constants")
                == coverage.get("probed_public_declarations")
                == coverage.get("found_public_declarations")
                == len(declaration_records)
                and coverage.get("missing_public_declarations") == 0,
                "compiled probe must resolve every probed public declaration",
            )
            check(
                compiled_probe.get("missing_declarations") == [],
                "compiled probe missing-declaration records must be empty",
            )
            check(
                coverage.get("snapshot_modules")
                == snapshot.get("summary", {}).get("lean_modules")
                and coverage.get("snapshot_public_declarations")
                == snapshot.get("summary", {}).get("public_source_declarations")
                and 0
                <= coverage.get("compiled_closure_modules", -1)
                <= coverage.get("snapshot_modules", -1)
                and 0
                <= coverage.get("source_public_declarations_in_compiled_closure", -1)
                <= coverage.get("snapshot_public_declarations", -1)
                and coverage.get("source_public_declarations_in_compiled_closure")
                == len(expected_source_names)
                and coverage.get("resolved_source_public_declarations")
                == len(expected_source_names & set(compiled_names))
                and coverage.get("compiled_closure_modules")
                == len(source.get("compiled_modules", []))
                and coverage.get("lexical_closure_modules")
                == len(source.get("lexical_closure_modules", [])),
                "compiled probe coverage does not match the source snapshot",
            )
            trust = compiled_probe.get("trust_result", {})
            all_axioms = trust.get("all", [])
            declaration_axioms = sorted(
                {
                    axiom
                    for declaration in declaration_records
                    if isinstance(declaration, dict)
                    for axiom in declaration.get("axioms", [])
                }
            )
            check(
                isinstance(all_axioms, list)
                and all(isinstance(value, str) and value for value in all_axioms)
                and all_axioms == sorted(set(all_axioms)),
                "compiled probe all-axiom list must be sorted and unique",
            )
            check(
                all_axioms == declaration_axioms,
                "compiled probe trust result does not match declaration dependencies",
            )
            all_axiom_set = set(all_axioms) if isinstance(all_axioms, list) else set()
            expected_allowed = sorted(all_axiom_set & set(allowed_axioms or []))
            expected_forbidden = sorted(all_axiom_set & set(forbidden_axioms or []))
            remaining = all_axiom_set - set(expected_allowed) - set(expected_forbidden)
            expected_accepted: list[dict] = []
            provenance_list = compiled_probe.get("axiom_provenance", [])
            provenance = {
                item.get("name"): item
                for item in provenance_list
                if isinstance(item, dict) and isinstance(item.get("name"), str)
            }
            check(
                isinstance(provenance_list, list)
                and len(provenance) == len(provenance_list)
                and set(provenance) == all_axiom_set,
                "compiled probe must retain unique provenance for every axiom",
            )
            invalid_allowed_provenance: list[dict] = []
            for axiom in expected_allowed:
                item = provenance.get(axiom)
                expected = (allowed_axiom_provenance or {}).get(axiom, {})
                reasons: list[str] = []
                if item is None:
                    reasons.append("missing_provenance")
                else:
                    if item.get("kind") != expected.get("kind"):
                        reasons.append("unexpected_kind")
                    if item.get("module") != expected.get("module"):
                        reasons.append("unexpected_module")
                    if item.get("private") is not expected.get("private"):
                        reasons.append("unexpected_privacy")
                if reasons:
                    invalid_allowed_provenance.append(
                        {"axiom": axiom, "reasons": reasons}
                    )
            invalid_provenance: list[dict] = []
            missing_accepted: list[str] = []
            for group in accepted_groups if isinstance(accepted_groups, list) else []:
                exact = set(group.get("axioms", []))
                missing_accepted.extend(sorted(exact - all_axiom_set))
                accepted = sorted(exact & remaining)
                valid: list[str] = []
                for axiom in accepted:
                    item = provenance.get(axiom, {})
                    reasons: list[str] = []
                    if item.get("kind") != "axiom":
                        reasons.append("not_axiom_info")
                    if item.get("private") is not True:
                        reasons.append("not_private")
                    if item.get("module") not in set(
                        source.get("compiled_modules", [])
                    ):
                        reasons.append("module_outside_compiled_closure")
                    if reasons:
                        invalid_provenance.append(
                            {"axiom": axiom, "reasons": reasons}
                        )
                    else:
                        valid.append(axiom)
                remaining -= set(valid)
                if accepted:
                    expected_accepted.append(
                        {
                            "id": group["id"],
                            "trust_class": group["trust_class"],
                            "axioms": accepted,
                        }
                    )
            expected_unexpected = sorted(remaining)
            check(
                trust.get("policy_pass") is True
                and trust.get("allowed") == expected_allowed
                and trust.get("invalid_allowed_provenance")
                == invalid_allowed_provenance
                == []
                and trust.get("accepted_by_group") == expected_accepted
                and trust.get("forbidden") == expected_forbidden == []
                and trust.get("unexpected") == expected_unexpected == []
                and trust.get("missing_accepted_axioms")
                == sorted(set(missing_accepted))
                == []
                and trust.get("invalid_accepted_provenance")
                == sorted(invalid_provenance, key=lambda item: item["axiom"])
                == [],
                "compiled probe trust policy must pass without forbidden or unexpected axioms",
            )
            observed_group_ids = {
                item.get("id")
                for item in trust.get("accepted_by_group", [])
                if isinstance(item, dict)
            }
            check(
                observed_group_ids == set(accepted_group_ids),
                "compiled probe accepted-axiom groups do not match the contract",
            )
            grouped: dict[tuple[str, ...], list[str]] = {}
            for declaration in declaration_records:
                if (
                    isinstance(declaration, dict)
                    and isinstance(declaration.get("name"), str)
                    and isinstance(declaration.get("axioms"), list)
                    and all(
                        isinstance(axiom, str)
                        for axiom in declaration.get("axioms", [])
                    )
                ):
                    key = tuple(declaration.get("axioms", []))
                    grouped.setdefault(key, []).append(declaration.get("name"))
            expected_groups = [
                {
                    "axioms": list(axioms),
                    "declarations": sorted(names),
                }
                for axioms, names in sorted(grouped.items())
            ]
            check(
                compiled_probe.get("axiom_dependency_groups") == expected_groups,
                "compiled probe dependency groups do not match declaration records",
            )

    compiled_runs = contract.get("compiled_runs", [])
    check(
        isinstance(compiled_runs, list) and len(compiled_runs) == 2,
        "rehearsal must retain exactly two structured compiled-probe runs",
    )
    compiled_run_ids: list[str] = []
    for run in compiled_runs if isinstance(compiled_runs, list) else []:
        if not isinstance(run, dict):
            check(False, "compiled-probe run records must be objects")
            continue
        compiled_run_ids.append(run.get("id"))
        mode = run.get("mode")
        check(
            run.get("id") in {"RUN-COMPILED-01", "RUN-COMPILED-02"}
            and mode in EXPECTED_COMPILED_COMMANDS
            and run.get("command") == EXPECTED_COMPILED_COMMANDS.get(mode),
            f"{run.get('id')}: compiled-probe command or mode is invalid",
        )
        check(
            re.fullmatch(r"\d{4}-\d{2}-\d{2}", run.get("performed_on", ""))
            is not None,
            f"{run.get('id')}: performed_on must be an ISO date",
        )
        selected_baseline_adapter = (
            selected.get("baseline_adapter", {})
            if isinstance(selected, dict)
            else {}
        )
        probe_manifest_sha = (
            compiled_probe.get("source", {})
            .get("compiled_artifact_manifest", {})
            .get("manifest_sha256")
        )
        probe_execution = compiled_probe.get("environment", {}).get(
            "execution_profile", {}
        )
        check(
            isinstance(selected, dict)
            and run.get("source_commit_sha") == selected.get("commit_sha")
            and run.get("source_tree_sha") == selected.get("tree_sha")
            and run.get("source_tree_sha")
            in {
                item.get("source_tree_sha")
                for item in runs
                if isinstance(item, dict)
            }
            and run.get("source_status_sha256") == hashlib.sha256(b"").hexdigest()
            and run.get("snapshot_sha256") == snapshot.get("snapshot_sha256")
            and run.get("probe_sha256") == compiled_probe.get("probe_sha256")
            and run.get("generator_sha256")
            == normalized_source_sha256(ROOT / "scripts" / "lean_compiled_probe.py")
            and run.get("compiled_artifact_manifest_sha256")
            == probe_manifest_sha
            and run.get("lake_launcher_sha256")
            == probe_execution.get("lake_launcher_sha256")
            and run.get("elan_home_source")
            == probe_execution.get("elan_home_source")
            and run.get("observed_workspace_changes")
            == compiled_probe.get("source", {}).get(
                "observed_workspace_changes"
            )
            == selected_baseline_adapter.get("allowed_workspace_changes")
            and run.get("canonical_source_clean_before") is True
            and run.get("canonical_source_clean_after") is True,
            f"{run.get('id')}: compiled-probe run is not bound to current evidence",
        )
    check(
        len(compiled_run_ids) == len(set(compiled_run_ids))
        and set(compiled_run_ids) == {"RUN-COMPILED-01", "RUN-COMPILED-02"}
        and {
            run.get("mode")
            for run in compiled_runs
            if isinstance(run, dict)
        }
        == {"write", "check"},
        "compiled-probe runs must retain unique write and check records",
    )
    check(
        len(
            {
                (
                    run.get("source_commit_sha"),
                    run.get("source_tree_sha"),
                    run.get("snapshot_sha256"),
                    run.get("probe_sha256"),
                    run.get("generator_sha256"),
                    run.get("compiled_artifact_manifest_sha256"),
                    run.get("lake_launcher_sha256"),
                    run.get("elan_home_source"),
                )
                for run in compiled_runs
                if isinstance(run, dict)
            }
        )
        == 1,
        "compiled-probe runs must bind the same source, snapshot, artifact, and generator",
    )

    baseline_evidence_path = artifacts.get("baseline_evidence")
    if isinstance(baseline_evidence_path, str):
        check(
            not final or safe_file(baseline_evidence_path),
            "final baseline evidence is missing",
        )
        if safe_file(baseline_evidence_path):
            try:
                baseline_evidence = load_json(ROOT / baseline_evidence_path)
            except ValueError as exc:
                errors.append(f"baseline evidence is invalid JSON: {exc}")
                baseline_evidence = {}
            digest = baseline_evidence.get("evidence_sha256")
            unsigned = dict(baseline_evidence)
            unsigned.pop("evidence_sha256", None)
            selected_baseline_adapter = (
                selected.get("baseline_adapter", {})
                if isinstance(selected, dict)
                else {}
            )
            check(
                digest == hashlib.sha256(canonical_json_bytes(unsigned)).hexdigest(),
                "baseline evidence digest does not match its content",
            )
            source = baseline_evidence.get("source", {})
            check(
                baseline_evidence.get("schema_version") == "1.0"
                and baseline_evidence.get("rehearsal_id") == contract.get("id")
                and baseline_evidence.get("task_id") == contract.get("task_id")
                and baseline_evidence.get("evidence_class") == boundary.get("class")
                and baseline_evidence.get("external_evidence") is False
                and baseline_evidence.get("unlocks_task_012") is False,
                "baseline evidence identity or evidence boundary is invalid",
            )
            if isinstance(selected, dict):
                check(
                    source.get("repository") == selected.get("repository")
                    and source.get("commit_sha") == selected.get("commit_sha")
                    and source.get("tree_sha") == selected.get("tree_sha")
                    and source.get("tree_sha")
                    in {
                        run.get("source_tree_sha")
                        for run in runs
                        if isinstance(run, dict)
                    },
                    "baseline evidence source does not match selected source",
                )
                check(
                    baseline_evidence.get("execution_boundary")
                    == selected.get("baseline_adapter", {}).get("execution_profile"),
                    "baseline evidence execution boundary does not match selected source",
                )
            check(
                source.get("canonical_checkout_clean_before") is True
                and source.get("canonical_checkout_clean_after") is True,
                "baseline evidence must preserve the canonical source checkout",
            )
            check(
                source.get("canonical_snapshot_sha256")
                == snapshot.get("snapshot_sha256"),
                "baseline evidence snapshot digest does not match the snapshot",
            )
            check(
                baseline_evidence.get("result", {}).get("status") == "passed",
                "baseline evidence result must be passed",
            )
            check(
                baseline_evidence.get("dependency_resolution", {}).get("exit_code")
                == 0
                and baseline_evidence.get("dependency_resolution", {}).get("command")
                == EXPECTED_BASELINE_COMMANDS[0]
                and baseline_evidence.get("dependency_resolution", {}).get(
                    "resolved_revisions"
                )
                == selected_baseline_adapter.get("resolved_dependency_revisions")
                and baseline_evidence.get("dependency_resolution", {}).get(
                    "documented_workspace_effect"
                )
                == selected_baseline_adapter.get("documented_workspace_effect"),
                "baseline dependency resolution must match the exact contract command, revisions, and workspace effect",
            )
            build_attempts = baseline_evidence.get("build_attempts", [])
            build_attempts_by_id = {
                attempt.get("id"): attempt
                for attempt in build_attempts
                if isinstance(attempt, dict)
            }
            default_build = build_attempts_by_id.get(
                "BUILD-DEFAULT-PARALLELISM", {}
            )
            bounded_build = build_attempts_by_id.get(
                "BUILD-BOUNDED-PARALLELISM", {}
            )
            check(
                isinstance(build_attempts, list)
                and len(build_attempts) == 2
                and set(build_attempts_by_id)
                == {
                    "BUILD-DEFAULT-PARALLELISM",
                    "BUILD-BOUNDED-PARALLELISM",
                }
                and default_build.get("command")
                == "cd cedar-lean && lake build Cedar SymCC"
                and default_build.get("environment_overrides") == {}
                and default_build.get("exit_code") == 1
                and default_build.get("classification")
                == "host_resource_exhaustion"
                and bounded_build.get("command") == EXPECTED_BASELINE_COMMANDS[1]
                and bounded_build.get("environment_overrides")
                == {"LEAN_NUM_THREADS": "1"}
                and bounded_build.get("exit_code") == 0
                and bounded_build.get("classification") == "pass",
                "baseline evidence must retain the exact failed and bounded build attempts",
            )
            check(
                any(
                    attempt.get("classification") == "pass"
                    and attempt.get("exit_code") == 0
                    and attempt.get("command") == EXPECTED_BASELINE_COMMANDS[1]
                    and attempt.get("environment_overrides")
                    == {"LEAN_NUM_THREADS": "1"}
                    for attempt in baseline_evidence.get("build_attempts", [])
                    if isinstance(attempt, dict)
                ),
                "baseline evidence needs the exact passing bounded build attempt",
            )
            lint_attempts = baseline_evidence.get("lint_attempts", [])
            lint_attempts_by_id = {
                attempt.get("id"): attempt
                for attempt in lint_attempts
                if isinstance(attempt, dict)
            }
            windows_lint = lint_attempts_by_id.get("LINT-WINDOWS-CRLF", {})
            canonical_lint = lint_attempts_by_id.get("LINT-CANONICAL-LF", {})
            check(
                isinstance(lint_attempts, list)
                and len(lint_attempts) == 2
                and set(lint_attempts_by_id)
                == {"LINT-WINDOWS-CRLF", "LINT-CANONICAL-LF"}
                and windows_lint.get("command") == EXPECTED_BASELINE_COMMANDS[2]
                and windows_lint.get("checkout_policy")
                == "Windows default line-ending conversion"
                and windows_lint.get("exit_code") == 1
                and windows_lint.get("missing_import_diagnostics") == 119
                and windows_lint.get("other_diagnostics") == 0
                and windows_lint.get("classification")
                == "upstream_platform_assumption"
                and canonical_lint.get("command") == EXPECTED_BASELINE_COMMANDS[2]
                and canonical_lint.get("checkout_policy")
                == "core.autocrlf=false, matching committed Git blobs and upstream Linux CI"
                and canonical_lint.get("exit_code") == 0
                and canonical_lint.get("classification") == "pass",
                "baseline evidence must retain the exact CRLF failure and canonical-LF pass",
            )
            check(
                any(
                    attempt.get("classification") == "pass"
                    and attempt.get("exit_code") == 0
                    and attempt.get("command") == EXPECTED_BASELINE_COMMANDS[2]
                    and attempt.get("checkout_policy")
                    == "core.autocrlf=false, matching committed Git blobs and upstream Linux CI"
                    for attempt in baseline_evidence.get("lint_attempts", [])
                    if isinstance(attempt, dict)
                ),
                "baseline evidence needs the exact passing canonical-LF lint attempt",
            )
            if compiled_probe:
                baseline_probe = baseline_evidence.get("compiled_probe", {})
                check(
                    baseline_probe.get("probe_sha256")
                    == compiled_probe.get("probe_sha256")
                    and baseline_probe.get("generator_sha256")
                    == compiled_probe.get("generator", {}).get("sha256")
                    and baseline_probe.get("compiled_closure_modules")
                    == compiled_probe.get("coverage", {}).get(
                        "compiled_closure_modules"
                    )
                    and baseline_probe.get("lexical_closure_modules")
                    == compiled_probe.get("coverage", {}).get(
                        "lexical_closure_modules"
                    )
                    and baseline_probe.get(
                        "source_public_declarations_in_compiled_closure"
                    )
                    == compiled_probe.get("coverage", {}).get(
                        "source_public_declarations_in_compiled_closure"
                    )
                    and baseline_probe.get("found_public_declarations")
                    == compiled_probe.get("coverage", {}).get(
                        "found_public_declarations"
                    )
                    and baseline_probe.get("missing_public_declarations")
                    == compiled_probe.get("coverage", {}).get(
                        "missing_public_declarations"
                    )
                    and baseline_probe.get("forbidden_axioms")
                    == compiled_probe.get("trust_result", {}).get("forbidden")
                    and baseline_probe.get("unexpected_axioms")
                    == compiled_probe.get("trust_result", {}).get("unexpected")
                    and baseline_probe.get("compiled_artifact_manifest_sha256")
                    == compiled_probe.get("source", {})
                    .get("compiled_artifact_manifest", {})
                    .get("manifest_sha256")
                    and baseline_probe.get("lake_launcher_sha256")
                    == compiled_probe.get("environment", {})
                    .get("execution_profile", {})
                    .get("lake_launcher_sha256")
                    and baseline_probe.get("elan_home_source")
                    == compiled_probe.get("environment", {})
                    .get("execution_profile", {})
                    .get("elan_home_source")
                    and baseline_probe.get("compiled_probe_launcher")
                    == compiled_probe.get("environment", {})
                    .get("execution_profile", {})
                    .get("compiled_probe_launcher")
                    and baseline_probe.get(
                        "compiled_probe_output_authentication"
                    )
                    == compiled_probe.get("environment", {})
                    .get("execution_profile", {})
                    .get("compiled_probe_output_authentication")
                    and baseline_probe.get(
                        "invalid_allowed_axiom_provenance"
                    )
                    == compiled_probe.get("trust_result", {}).get(
                        "invalid_allowed_provenance"
                    )
                    and baseline_probe.get(
                        "compiler_generated_native_decide_axioms"
                    )
                    == sum(
                        len(group.get("axioms", []))
                        for group in compiled_probe.get("trust_result", {}).get(
                            "accepted_by_group", []
                        )
                        if isinstance(group, dict)
                    )
                    and baseline_probe.get("policy_pass")
                    == compiled_probe.get("trust_result", {}).get("policy_pass"),
                    "baseline evidence must reference the committed compiled probe",
                )

    report_path = artifacts.get("report")
    if final and isinstance(report_path, str):
        check(safe_file(report_path), "final rehearsal report is missing")
        if safe_file(report_path):
            try:
                report_text = (ROOT / report_path).read_text(encoding="utf-8")
            except OSError as exc:
                errors.append(f"cannot inspect final rehearsal report: {exc}")
                report_text = ""
            disposition = decision.get("disposition")
            expected_decision = (
                f"Decision: **{disposition.upper()}**"
                if isinstance(disposition, str)
                else ""
            )
            check(
                "Status: FINAL" in report_text,
                "final rehearsal report must declare Status: FINAL",
            )
            check(
                bool(expected_decision) and expected_decision in report_text,
                "final rehearsal report decision does not match the contract",
            )
            check(
                "## Adversarial review packet" in report_text,
                "final rehearsal report must retain the adversarial review packet",
            )
            check(
                "`TASK-012` remains locked" in report_text,
                "final rehearsal report must keep TASK-012 locked",
            )
            check(
                "Owner: `architecture_validation`." in report_text
                and "`compiled-evidence-authenticity`" in report_text,
                "final rehearsal report must retain the exact CHANGE owner and failed authenticity gate",
            )
            check(
                "PENDING" not in report_text.upper(),
                "final rehearsal report must not contain pending results",
            )

    if isinstance(selected, dict):
        repository_name = selected.get("repository", "").rstrip("/").split("/")[-1]
        selected_tokens = {
            repository_name.lower(),
            repository_name.lower().replace("-", "_"),
            repository_name.lower().split("-")[0],
            "ecdlp",
            "secp256k1",
            "researchos",
        }
        selected_tokens = {token for token in selected_tokens if len(token) >= 5}
        for path in (
            ROOT / "scripts" / "lean_portability.py",
            ROOT / "scripts" / "lean_compiled_probe.py",
        ):
            try:
                generic_source = path.read_text(encoding="utf-8").lower()
            except OSError as exc:
                errors.append(f"cannot inspect generic portability core: {exc}")
                continue
            leaked = sorted(
                token for token in selected_tokens if token in generic_source
            )
            check(
                not leaked,
                f"{path.name} contains project/domain-specific tokens: {leaked}",
            )

    if errors:
        print("portability rehearsal check FAILED:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(
        "portability rehearsal check OK: "
        f"{status}, {len(candidates)} candidates, "
        f"{decision.get('disposition') or 'decision pending'}"
    )
    return 0


if __name__ == "__main__":
    args = parse_args()
    raise SystemExit(main(require_final=args.require_final))
