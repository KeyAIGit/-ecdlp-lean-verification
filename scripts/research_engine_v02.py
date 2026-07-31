#!/usr/bin/env python3
"""Deterministic Research Engine v0.2 lifecycle and portfolio core.

This module is deliberately side-effect free. It does not write repository
state, authorize work, execute experiments, or infer route promotion.
"""

from __future__ import annotations

import copy
import hashlib
import itertools
import json
import math
import re
from datetime import datetime
from typing import Any, Iterable

from scientific_provenance import scientific_source_commit_allowed
from research_contract_binding import scientific_contract_digests


PRIMARY_THREAT_MODEL = "classical-single-target-plain"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")

LANES = {
    "literature_applicability",
    "structural",
    "mechanism",
    "validator",
    "bounded_experiment",
    "formalization",
}

STATES = (
    "idea",
    "screened",
    "mechanism_specified",
    "validator_ready",
    "admissible",
    "recommended",
    "authorized",
    "running",
    "terminal",
    "superseded",
)

NORMAL_TRANSITIONS = {
    None: {"idea"},
    "idea": {"screened", "superseded"},
    "screened": {"mechanism_specified", "terminal", "superseded"},
    "mechanism_specified": {"validator_ready", "terminal", "superseded"},
    "validator_ready": {"admissible", "terminal", "superseded"},
    "admissible": {"recommended", "terminal", "superseded"},
    "recommended": {"authorized", "superseded"},
    "authorized": {"running", "superseded"},
    "running": {"terminal"},
    "terminal": set(),
    "superseded": set(),
}

SUCCESSFUL_PREREQUISITE_OUTCOMES = {
    "proved",
    "confirmed",
    "supported",
    "completed",
}

CALIBRATION_EXCLUDED_CLASSES = {
    "structural",
    "historical_migration",
    "literature",
}

GENERATION_REVIEW_ROLES = {
    "algebra",
    "cryptanalysis_skeptic",
    "prior_art",
    "cost_model",
    "validator_design",
}

MECHANISM_ASSURANCE_TOPICS = (
    "relation_equivalence",
    "exceptional_locus",
    "recovery_map",
    "cost_changing_bridge",
)

MECHANISM_ASSURANCE_STATUSES = {
    "lean_kernel",
    "certificate_replayed",
    "independent_reproduction",
    "empirical_native",
    "historical_migration",
    "literature_only",
    "specified_unproved",
}

ADDITIVE_COSTS = (
    "compute_hours",
    "storage_gb",
    "money_usd",
    "implementation_hours",
    "reviewer_hours",
)

PEAK_COSTS = (
    "wall_time_hours",
    "peak_memory_gb",
    "workers",
)


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("ascii")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def snapshot_digest(snapshot: dict[str, Any]) -> str:
    payload = copy.deepcopy(snapshot)
    payload.pop("snapshot_digest", None)
    return sha256_json(payload)


def bind_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    bound = copy.deepcopy(snapshot)
    if "authorization" in bound or "authorized" in bound:
        raise ValueError("authorization is lifecycle state, not snapshot data")
    bound["snapshot_digest"] = snapshot_digest(bound)
    return bound


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and SHA256_RE.fullmatch(value) is not None


def _is_iso_datetime(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return (
        "T" in value
        and parsed.tzinfo is not None
        and parsed.utcoffset() is not None
    )


def _require_keys(
    value: Any,
    required: Iterable[str],
    label: str,
) -> list[str]:
    if not isinstance(value, dict):
        return [f"{label}: expected object"]
    return [
        f"{label}: missing {key}"
        for key in required
        if key not in value
    ]


def _reject_extra_keys(
    value: Any,
    allowed: Iterable[str],
    label: str,
) -> list[str]:
    if not isinstance(value, dict):
        return []
    extra = sorted(set(value) - set(allowed))
    return [f"{label}: unexpected {key}" for key in extra]


def _validate_string_list(
    value: Any,
    label: str,
    *,
    nonempty: bool = False,
) -> list[str]:
    if not isinstance(value, list):
        return [f"{label}: expected array"]
    problems: list[str] = []
    if nonempty and not value:
        problems.append(f"{label}: must not be empty")
    if any(not _is_nonempty_string(item) for item in value):
        problems.append(f"{label}: entries must be nonempty strings")
    if len(value) != len(set(value)) if all(isinstance(x, str) for x in value) else False:
        problems.append(f"{label}: duplicate entries")
    return problems


def mechanism_assurance_claims(contract: Any) -> dict[str, str]:
    """Digest the exact claim payload covered by each assurance binding."""
    if not isinstance(contract, dict):
        return {}
    payloads = {
        "relation_equivalence": {
            "transformation": contract.get("transformation"),
            "fixed_target_semantics": contract.get("fixed_target_semantics"),
            "relation_semantics": contract.get("relation_semantics"),
        },
        "exceptional_locus": contract.get("exceptional_locus"),
        "recovery_map": contract.get("recovery_map"),
        "cost_changing_bridge": {
            "orbit_stabilizer": contract.get("orbit_stabilizer"),
            "cost_changing_mechanism": contract.get(
                "cost_changing_mechanism"
            ),
        },
    }
    return {
        topic: sha256_json(payload)
        for topic, payload in payloads.items()
    }


def validate_mechanism_contract(
    contract: Any,
    *,
    require_assured: bool = False,
    evidence_registry: list[dict[str, Any]] | None = None,
) -> list[str]:
    label = "mechanism_contract"
    required = (
        "source_objects",
        "target_objects",
        "transformation",
        "fixed_target_semantics",
        "exceptional_locus",
        "orbit_stabilizer",
        "relation_semantics",
        "recovery_map",
        "implementation_identity",
        "cost_changing_mechanism",
        "source_ids",
        "assurance_bindings",
    )
    problems = _require_keys(contract, required, label)
    if not isinstance(contract, dict):
        return problems
    problems += _reject_extra_keys(contract, required, label)

    problems += _validate_string_list(
        contract.get("source_objects"), f"{label}.source_objects", nonempty=True
    )
    problems += _validate_string_list(
        contract.get("target_objects"), f"{label}.target_objects", nonempty=True
    )
    problems += _validate_string_list(
        contract.get("source_ids"), f"{label}.source_ids", nonempty=True
    )

    transformation = contract.get("transformation")
    transformation_keys = ("kind", "exact_map", "domain", "codomain")
    problems += _require_keys(
        transformation, transformation_keys,
        f"{label}.transformation",
    )
    problems += _reject_extra_keys(
        transformation, transformation_keys, f"{label}.transformation"
    )
    if isinstance(transformation, dict):
        for key in ("kind", "exact_map", "domain", "codomain"):
            if not _is_nonempty_string(transformation.get(key)):
                problems.append(f"{label}.transformation.{key}: empty")

    fixed = contract.get("fixed_target_semantics")
    fixed_keys = ("target_slot", "target_action", "same_target_preserved")
    problems += _require_keys(
        fixed, fixed_keys,
        f"{label}.fixed_target_semantics",
    )
    problems += _reject_extra_keys(
        fixed, fixed_keys, f"{label}.fixed_target_semantics"
    )
    if isinstance(fixed, dict):
        for key in ("target_slot", "target_action"):
            if not _is_nonempty_string(fixed.get(key)):
                problems.append(f"{label}.fixed_target_semantics.{key}: empty")
        if not isinstance(fixed.get("same_target_preserved"), bool):
            problems.append(
                f"{label}.fixed_target_semantics.same_target_preserved: expected bool"
            )

    exceptional = contract.get("exceptional_locus")
    exceptional_keys = ("definition", "treatment")
    problems += _require_keys(
        exceptional, exceptional_keys,
        f"{label}.exceptional_locus",
    )
    problems += _reject_extra_keys(
        exceptional, exceptional_keys, f"{label}.exceptional_locus"
    )
    if isinstance(exceptional, dict):
        if not _is_nonempty_string(exceptional.get("definition")):
            problems.append(f"{label}.exceptional_locus.definition: empty")
        if exceptional.get("treatment") not in {
            "excluded",
            "separately_recovered",
            "proved_empty",
            "unresolved",
        }:
            problems.append(f"{label}.exceptional_locus.treatment: invalid")

    orbit = contract.get("orbit_stabilizer")
    orbit_keys = ("acting_group", "stabilizer", "orbit_size_law")
    problems += _require_keys(
        orbit, orbit_keys,
        f"{label}.orbit_stabilizer",
    )
    problems += _reject_extra_keys(
        orbit, orbit_keys, f"{label}.orbit_stabilizer"
    )
    if isinstance(orbit, dict):
        for key in ("acting_group", "stabilizer", "orbit_size_law"):
            if not _is_nonempty_string(orbit.get(key)):
                problems.append(f"{label}.orbit_stabilizer.{key}: empty")

    semantics = contract.get("relation_semantics")
    semantics_keys = (
        "source_relation",
        "target_relation",
        "equivalence_status",
    )
    problems += _require_keys(
        semantics, semantics_keys,
        f"{label}.relation_semantics",
    )
    problems += _reject_extra_keys(
        semantics, semantics_keys, f"{label}.relation_semantics"
    )
    if isinstance(semantics, dict):
        for key in ("source_relation", "target_relation"):
            if not _is_nonempty_string(semantics.get(key)):
                problems.append(f"{label}.relation_semantics.{key}: empty")
        if semantics.get("equivalence_status") not in {
            "proved",
            "certificate_replayed",
            "specified_unproved",
        }:
            problems.append(
                f"{label}.relation_semantics.equivalence_status: invalid"
            )
        elif (
            require_assured
            and semantics.get("equivalence_status") == "specified_unproved"
        ):
            problems.append(
                f"{label}.relation_semantics.equivalence_status: "
                "unproved specification cannot clear the exact-mechanism gate"
            )

    recovery = contract.get("recovery_map")
    recovery_keys = (
        "forward",
        "inverse",
        "excluded_components",
        "spurious_solution_policy",
    )
    problems += _require_keys(
        recovery,
        recovery_keys,
        f"{label}.recovery_map",
    )
    problems += _reject_extra_keys(
        recovery, recovery_keys, f"{label}.recovery_map"
    )
    if isinstance(recovery, dict):
        for key in ("forward", "inverse", "spurious_solution_policy"):
            if not _is_nonempty_string(recovery.get(key)):
                problems.append(f"{label}.recovery_map.{key}: empty")
        problems += _validate_string_list(
            recovery.get("excluded_components"),
            f"{label}.recovery_map.excluded_components",
        )

    implementation = contract.get("implementation_identity")
    implementation_keys = ("implementation_path", "sha256")
    problems += _require_keys(
        implementation, implementation_keys,
        f"{label}.implementation_identity",
    )
    problems += _reject_extra_keys(
        implementation,
        implementation_keys,
        f"{label}.implementation_identity",
    )
    if isinstance(implementation, dict):
        if not _is_nonempty_string(implementation.get("implementation_path")):
            problems.append(
                f"{label}.implementation_identity.implementation_path: empty"
            )
        if not _is_sha256(implementation.get("sha256")):
            problems.append(f"{label}.implementation_identity.sha256: invalid")

    bridge = contract.get("cost_changing_mechanism")
    bridge_keys = (
        "quantity",
        "causal_bridge",
        "growth_law",
        "non_orbit_lever",
    )
    problems += _require_keys(
        bridge, bridge_keys,
        f"{label}.cost_changing_mechanism",
    )
    problems += _reject_extra_keys(
        bridge, bridge_keys, f"{label}.cost_changing_mechanism"
    )
    if isinstance(bridge, dict):
        for key in ("quantity", "causal_bridge", "growth_law"):
            if not _is_nonempty_string(bridge.get(key)):
                problems.append(f"{label}.cost_changing_mechanism.{key}: empty")
        lever = bridge.get("non_orbit_lever")
        if lever is not None and not _is_nonempty_string(lever):
            problems.append(
                f"{label}.cost_changing_mechanism.non_orbit_lever: invalid"
            )

    bindings = contract.get("assurance_bindings")
    problems += _require_keys(
        bindings, MECHANISM_ASSURANCE_TOPICS, f"{label}.assurance_bindings"
    )
    problems += _reject_extra_keys(
        bindings, MECHANISM_ASSURANCE_TOPICS, f"{label}.assurance_bindings"
    )
    claim_digests = mechanism_assurance_claims(contract)
    registry_by_id = {
        item.get("evidence_id"): item
        for item in (evidence_registry or [])
        if isinstance(item, dict)
        and _is_nonempty_string(item.get("evidence_id"))
    }
    if isinstance(bindings, dict):
        for topic in MECHANISM_ASSURANCE_TOPICS:
            item = bindings.get(topic)
            item_label = f"{label}.assurance_bindings.{topic}"
            item_keys = ("assurance", "evidence_id", "claim_sha256")
            problems += _require_keys(item, item_keys, item_label)
            problems += _reject_extra_keys(item, item_keys, item_label)
            if not isinstance(item, dict):
                continue
            assurance = item.get("assurance")
            evidence_id = item.get("evidence_id")
            claim_sha = item.get("claim_sha256")
            if assurance not in MECHANISM_ASSURANCE_STATUSES:
                problems.append(f"{item_label}.assurance: invalid")
                continue
            if assurance == "specified_unproved":
                if evidence_id is not None or claim_sha is not None:
                    problems.append(
                        f"{item_label}: unproved binding must not claim evidence"
                    )
                if require_assured:
                    problems.append(
                        f"{item_label}: assured evidence is required"
                    )
                continue
            if not _is_nonempty_string(evidence_id):
                problems.append(f"{item_label}.evidence_id: empty")
                continue
            if not _is_sha256(claim_sha):
                problems.append(f"{item_label}.claim_sha256: invalid")
                continue
            if claim_sha != claim_digests.get(topic):
                problems.append(f"{item_label}.claim_sha256: claim mismatch")
            registry_item = registry_by_id.get(evidence_id)
            if registry_item is None:
                problems.append(f"{item_label}: evidence_id is not registered")
                continue
            for key, expected in (
                ("topic", topic),
                ("assurance", assurance),
                ("claim_sha256", claim_sha),
            ):
                if registry_item.get(key) != expected:
                    problems.append(f"{item_label}: registry {key} does not match")

        relation_binding = bindings.get("relation_equivalence")
        if isinstance(relation_binding, dict) and isinstance(semantics, dict):
            expected_relation_assurance = {
                "proved": "lean_kernel",
                "certificate_replayed": "certificate_replayed",
                "specified_unproved": "specified_unproved",
            }.get(semantics.get("equivalence_status"))
            if relation_binding.get("assurance") != expected_relation_assurance:
                problems.append(
                    f"{label}.relation_semantics.equivalence_status: "
                    "does not match the relation assurance binding"
                )
    return sorted(set(problems))


def validate_prediction_contract(contract: Any) -> list[str]:
    label = "prediction_contract"
    required = (
        "metric",
        "matched_baseline",
        "tested_sizes",
        "expected_direction",
        "minimum_material_effect",
        "decision_threshold",
        "stop_rule",
        "falsifying_outcomes",
    )
    problems = _require_keys(contract, required, label)
    if not isinstance(contract, dict):
        return problems
    problems += _reject_extra_keys(contract, required, label)

    metric = contract.get("metric")
    metric_keys = ("name", "unit", "recomputation")
    problems += _require_keys(
        metric, metric_keys, f"{label}.metric"
    )
    problems += _reject_extra_keys(metric, metric_keys, f"{label}.metric")
    if isinstance(metric, dict):
        for key in ("name", "unit", "recomputation"):
            if not _is_nonempty_string(metric.get(key)):
                problems.append(f"{label}.metric.{key}: empty")

    baseline = contract.get("matched_baseline")
    baseline_keys = (
        "baseline_id",
        "implementation_digest",
        "matching_variables",
    )
    problems += _require_keys(
        baseline,
        baseline_keys,
        f"{label}.matched_baseline",
    )
    problems += _reject_extra_keys(
        baseline, baseline_keys, f"{label}.matched_baseline"
    )
    if isinstance(baseline, dict):
        if not _is_nonempty_string(baseline.get("baseline_id")):
            problems.append(f"{label}.matched_baseline.baseline_id: empty")
        if not _is_sha256(baseline.get("implementation_digest")):
            problems.append(
                f"{label}.matched_baseline.implementation_digest: invalid"
            )
        problems += _validate_string_list(
            baseline.get("matching_variables"),
            f"{label}.matched_baseline.matching_variables",
            nonempty=True,
        )

    sizes = contract.get("tested_sizes")
    if not isinstance(sizes, list) or not sizes:
        problems.append(f"{label}.tested_sizes: expected nonempty array")
    elif any(not isinstance(size, int) or isinstance(size, bool) or size < 1 for size in sizes):
        problems.append(f"{label}.tested_sizes: positive integers required")
    elif len(sizes) != len(set(sizes)):
        problems.append(f"{label}.tested_sizes: duplicate entries")
    elif sizes != sorted(sizes):
        problems.append(f"{label}.tested_sizes: must be strictly increasing")

    if contract.get("expected_direction") not in {
        "increase",
        "decrease",
        "different_law",
    }:
        problems.append(f"{label}.expected_direction: invalid")
    effect = contract.get("minimum_material_effect")
    if not isinstance(effect, (int, float)) or isinstance(effect, bool) or effect <= 0:
        problems.append(f"{label}.minimum_material_effect: must be positive")

    threshold = contract.get("decision_threshold")
    threshold_keys = ("operator", "value")
    problems += _require_keys(
        threshold, threshold_keys, f"{label}.decision_threshold"
    )
    problems += _reject_extra_keys(
        threshold, threshold_keys, f"{label}.decision_threshold"
    )
    if isinstance(threshold, dict):
        operator = threshold.get("operator")
        value = threshold.get("value")
        if operator not in {"lt", "le", "gt", "ge", "outside_interval"}:
            problems.append(f"{label}.decision_threshold.operator: invalid")
        elif operator == "outside_interval":
            if (
                not isinstance(value, list)
                or len(value) != 2
                or any(not _number_at_least(item, -math.inf) for item in value)
                or not value[0] < value[1]
            ):
                problems.append(
                    f"{label}.decision_threshold.value: "
                    "ordered numeric interval required"
                )
        elif not _number_at_least(value, -math.inf):
            problems.append(
                f"{label}.decision_threshold.value: finite number required"
            )

    stop = contract.get("stop_rule")
    stop_keys = ("condition", "maximum_instances")
    problems += _require_keys(
        stop, stop_keys, f"{label}.stop_rule"
    )
    problems += _reject_extra_keys(stop, stop_keys, f"{label}.stop_rule")
    if isinstance(stop, dict):
        if not _is_nonempty_string(stop.get("condition")):
            problems.append(f"{label}.stop_rule.condition: empty")
        maximum = stop.get("maximum_instances")
        if not isinstance(maximum, int) or isinstance(maximum, bool) or maximum < 1:
            problems.append(f"{label}.stop_rule.maximum_instances: invalid")

    problems += _validate_string_list(
        contract.get("falsifying_outcomes"),
        f"{label}.falsifying_outcomes",
        nonempty=True,
    )
    return sorted(set(problems))


def _number_at_least(value: Any, minimum: float) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and value >= minimum
    )


def validate_cost_contract(
    contract: Any,
    *,
    require_execution: bool = False,
) -> list[str]:
    label = "cost_contract"
    required = (
        "online",
        "offline",
        "wall_time_hours",
        "peak_memory_gb",
        "storage_gb",
        "workers",
        "money_usd",
        "implementation_hours",
        "reviewer_hours",
        "preprocessing",
        "amortization",
        "success_probability",
        "shared_setup",
    )
    problems = _require_keys(contract, required, label)
    if not isinstance(contract, dict):
        return problems
    problems += _reject_extra_keys(contract, required, label)

    for phase in ("online", "offline"):
        item = contract.get(phase)
        compute_keys = ("cpu_hours", "gpu_hours")
        problems += _require_keys(
            item, compute_keys, f"{label}.{phase}"
        )
        problems += _reject_extra_keys(item, compute_keys, f"{label}.{phase}")
        if isinstance(item, dict):
            for key in ("cpu_hours", "gpu_hours"):
                if not _number_at_least(item.get(key), 0):
                    problems.append(f"{label}.{phase}.{key}: invalid")

    for key in (
        "wall_time_hours",
        "peak_memory_gb",
        "storage_gb",
        "money_usd",
        "implementation_hours",
        "reviewer_hours",
    ):
        if not _number_at_least(contract.get(key), 0):
            problems.append(f"{label}.{key}: invalid")
    workers = contract.get("workers")
    if not isinstance(workers, int) or isinstance(workers, bool) or workers < 1:
        problems.append(f"{label}.workers: invalid")
    probability = contract.get("success_probability")
    if (
        not isinstance(probability, (int, float))
        or isinstance(probability, bool)
        or not 0 < probability <= 1
    ):
        problems.append(f"{label}.success_probability: invalid")

    preprocessing = contract.get("preprocessing")
    preprocessing_keys = ("included_in_totals", "description")
    problems += _require_keys(
        preprocessing, preprocessing_keys,
        f"{label}.preprocessing",
    )
    problems += _reject_extra_keys(
        preprocessing, preprocessing_keys, f"{label}.preprocessing"
    )
    if isinstance(preprocessing, dict):
        if preprocessing.get("included_in_totals") is not True:
            problems.append(
                f"{label}.preprocessing.included_in_totals: must be true"
            )
        if not _is_nonempty_string(preprocessing.get("description")):
            problems.append(f"{label}.preprocessing.description: empty")

    amortization = contract.get("amortization")
    amortization_keys = ("class", "target_count", "per_target_cost_included")
    problems += _require_keys(
        amortization, amortization_keys,
        f"{label}.amortization",
    )
    problems += _reject_extra_keys(
        amortization, amortization_keys, f"{label}.amortization"
    )
    if isinstance(amortization, dict):
        amortization_class = amortization.get("class")
        if amortization_class not in {
            "none_single_target",
            "fixed_batch",
            "multi_target",
            "reusable_setup",
        }:
            problems.append(f"{label}.amortization.class: invalid")
        count = amortization.get("target_count")
        if not isinstance(count, int) or isinstance(count, bool) or count < 1:
            problems.append(f"{label}.amortization.target_count: invalid")
        elif amortization_class == "none_single_target" and count != 1:
            problems.append(
                f"{label}.amortization.target_count: "
                "single-target work must use exactly one target"
            )
        elif amortization_class in {"fixed_batch", "multi_target"} and count < 2:
            problems.append(
                f"{label}.amortization.target_count: "
                "batch or multi-target work requires at least two targets"
            )
        if not isinstance(amortization.get("per_target_cost_included"), bool):
            problems.append(
                f"{label}.amortization.per_target_cost_included: expected bool"
            )
        elif require_execution and amortization.get("per_target_cost_included") is not True:
            problems.append(
                f"{label}.amortization.per_target_cost_included: "
                "must be true for execution"
            )

    shared = contract.get("shared_setup")
    shared_keys = ("setup_id", "hours", "expected_reuse")
    problems += _require_keys(
        shared, shared_keys, f"{label}.shared_setup"
    )
    problems += _reject_extra_keys(shared, shared_keys, f"{label}.shared_setup")
    if isinstance(shared, dict):
        setup_id = shared.get("setup_id")
        if setup_id is not None and not _is_nonempty_string(setup_id):
            problems.append(f"{label}.shared_setup.setup_id: invalid")
        if not _number_at_least(shared.get("hours"), 0):
            problems.append(f"{label}.shared_setup.hours: invalid")
        reuse = shared.get("expected_reuse")
        if not isinstance(reuse, int) or isinstance(reuse, bool) or reuse < 1:
            problems.append(f"{label}.shared_setup.expected_reuse: invalid")

    if require_execution:
        compute_total = 0.0
        for phase in ("online", "offline"):
            item = contract.get(phase)
            if isinstance(item, dict):
                for key in ("cpu_hours", "gpu_hours"):
                    value = item.get(key)
                    if _number_at_least(value, 0):
                        compute_total += float(value)
        if compute_total <= 0:
            problems.append(
                f"{label}: bounded execution must price positive compute"
            )
        for key in ("wall_time_hours", "peak_memory_gb", "storage_gb"):
            if not _number_at_least(contract.get(key), 0) or contract.get(key) <= 0:
                problems.append(
                    f"{label}.{key}: must be positive for execution"
                )
    return sorted(set(problems))


def validate_validator_contract(
    contract: Any,
    *,
    require_ready: bool = True,
    evidence_registry: list[dict[str, Any]] | None = None,
    implementation_registry: list[dict[str, Any]] | None = None,
) -> list[str]:
    label = "validator_contract"
    required = (
        "status",
        "raw_artifact_format",
        "recomputed_decisive_claim",
        "implementation",
        "prohibited_producer_fields",
        "independence",
        "independence_evidence",
        "source_review_requirements",
    )
    problems = _require_keys(contract, required, label)
    if not isinstance(contract, dict):
        return problems
    problems += _reject_extra_keys(contract, required, label)
    status = contract.get("status")
    if status not in {
        "design_only_unverified",
        "ready_evidence_bound",
    }:
        problems.append(f"{label}.status: invalid")
    if require_ready and status != "ready_evidence_bound":
        problems.append(f"{label}.status: validator is not evidence-bound ready")

    artifact = contract.get("raw_artifact_format")
    artifact_keys = ("media_type", "schema_id")
    problems += _require_keys(
        artifact, artifact_keys, f"{label}.raw_artifact_format"
    )
    problems += _reject_extra_keys(
        artifact, artifact_keys, f"{label}.raw_artifact_format"
    )
    if isinstance(artifact, dict):
        for key in ("media_type", "schema_id"):
            if not _is_nonempty_string(artifact.get(key)):
                problems.append(f"{label}.raw_artifact_format.{key}: empty")

    claim = contract.get("recomputed_decisive_claim")
    claim_keys = ("claim_id", "procedure")
    problems += _require_keys(
        claim, claim_keys,
        f"{label}.recomputed_decisive_claim",
    )
    problems += _reject_extra_keys(
        claim, claim_keys, f"{label}.recomputed_decisive_claim"
    )
    if isinstance(claim, dict):
        for key in ("claim_id", "procedure"):
            if not _is_nonempty_string(claim.get(key)):
                problems.append(
                    f"{label}.recomputed_decisive_claim.{key}: empty"
                )

    implementation = contract.get("implementation")
    implementation_keys = ("path", "sha256")
    problems += _require_keys(
        implementation, implementation_keys, f"{label}.implementation"
    )
    problems += _reject_extra_keys(
        implementation, implementation_keys, f"{label}.implementation"
    )
    if isinstance(implementation, dict):
        if not _is_nonempty_string(implementation.get("path")):
            problems.append(f"{label}.implementation.path: empty")
        if not _is_sha256(implementation.get("sha256")):
            problems.append(f"{label}.implementation.sha256: invalid")
        if status == "ready_evidence_bound":
            registered = any(
                isinstance(item, dict)
                and item.get("path") == implementation.get("path")
                and item.get("sha256") == implementation.get("sha256")
                for item in (implementation_registry or [])
            )
            if not registered:
                problems.append(
                    f"{label}.implementation: implementation is not registered"
                )

    problems += _validate_string_list(
        contract.get("prohibited_producer_fields"),
        f"{label}.prohibited_producer_fields",
        nonempty=True,
    )
    problems += _validate_string_list(
        contract.get("source_review_requirements"),
        f"{label}.source_review_requirements",
        nonempty=True,
    )

    independence = contract.get("independence")
    independence_keys = (
        "path_independent",
        "artifact_independent",
        "source_independent",
        "producer_identity",
        "validator_identity",
        "same_model",
        "same_session",
        "shared_context",
    )
    problems += _require_keys(
        independence, independence_keys, f"{label}.independence"
    )
    problems += _reject_extra_keys(
        independence, independence_keys, f"{label}.independence"
    )
    if isinstance(independence, dict):
        producer = independence.get("producer_identity")
        validator = independence.get("validator_identity")
        if not _is_nonempty_string(producer):
            problems.append(
                f"{label}.independence.producer_identity: empty"
            )
        if not _is_nonempty_string(validator):
            problems.append(
                f"{label}.independence.validator_identity: empty"
            )
        if producer == validator and _is_nonempty_string(producer):
            problems.append(
                f"{label}.independence: producer and validator identities match"
            )

        if status == "ready_evidence_bound":
            for key in (
                "path_independent",
                "artifact_independent",
                "source_independent",
            ):
                if independence.get(key) is not True:
                    problems.append(
                        f"{label}.independence.{key}: must be true"
                    )
            for key in ("same_model", "same_session", "shared_context"):
                if independence.get(key) is not False:
                    problems.append(
                        f"{label}.independence.{key}: must be false"
                    )
        elif status == "design_only_unverified":
            for key in (
                "path_independent",
                "artifact_independent",
                "source_independent",
            ):
                if independence.get(key) is not False:
                    problems.append(
                        f"{label}.independence.{key}: design may not claim independence"
                    )
            for key in ("same_model", "same_session", "shared_context"):
                if independence.get(key) is not None:
                    problems.append(
                        f"{label}.independence.{key}: design status must remain unknown"
                    )

    axis_evidence = contract.get("independence_evidence")
    problems += _require_keys(
        axis_evidence,
        ("path", "artifact", "source"),
        f"{label}.independence_evidence",
    )
    problems += _reject_extra_keys(
        axis_evidence,
        ("path", "artifact", "source"),
        f"{label}.independence_evidence",
    )
    registry_by_id = {
        item.get("evidence_id"): item
        for item in (evidence_registry or [])
        if isinstance(item, dict)
        and _is_nonempty_string(item.get("evidence_id"))
    }
    expected_assessment = {
        "path": "verified",
        "artifact": "verified",
        "source": "human_attested",
    }
    if isinstance(axis_evidence, dict):
        for axis in ("path", "artifact", "source"):
            item = axis_evidence.get(axis)
            item_label = f"{label}.independence_evidence.{axis}"
            problems += _require_keys(
                item,
                ("status", "evidence_id", "sha256"),
                item_label,
            )
            problems += _reject_extra_keys(
                item, ("status", "evidence_id", "sha256"), item_label
            )
            if not isinstance(item, dict):
                continue
            if status == "design_only_unverified":
                if item.get("status") != "planned":
                    problems.append(f"{item_label}.status: must be planned")
                if item.get("evidence_id") is not None:
                    problems.append(f"{item_label}.evidence_id: must be null")
                if item.get("sha256") is not None:
                    problems.append(f"{item_label}.sha256: must be null")
                continue

            assessment = expected_assessment[axis]
            if item.get("status") != assessment:
                problems.append(
                    f"{item_label}.status: expected {assessment}"
                )
            evidence_id = item.get("evidence_id")
            digest = item.get("sha256")
            if not _is_nonempty_string(evidence_id):
                problems.append(f"{item_label}.evidence_id: empty")
                continue
            if not _is_sha256(digest):
                problems.append(f"{item_label}.sha256: invalid")
                continue
            registry_item = registry_by_id.get(evidence_id)
            if registry_item is None:
                problems.append(
                    f"{item_label}: evidence_id is not registered"
                )
                continue
            for key, expected in (
                ("axis", axis),
                ("assessment", assessment),
                ("sha256", digest),
            ):
                if registry_item.get(key) != expected:
                    problems.append(
                        f"{item_label}: registry {key} does not match"
                    )
            if isinstance(independence, dict):
                for key in (
                    "producer_identity",
                    "validator_identity",
                    "same_model",
                    "same_session",
                    "shared_context",
                ):
                    if registry_item.get(key) != independence.get(key):
                        problems.append(
                            f"{item_label}: registry {key} does not match"
                        )
            if axis == "source":
                attested_by = registry_item.get("attested_by")
                if not _is_nonempty_string(attested_by):
                    problems.append(
                        f"{item_label}: human attester is missing"
                    )
                elif isinstance(independence, dict) and attested_by in {
                    independence.get("producer_identity"),
                    independence.get("validator_identity"),
                }:
                    problems.append(
                        f"{item_label}: source attester is not independent"
                    )
    return sorted(set(problems))


def validate_lane(lane: Any) -> list[str]:
    label = "lane"
    required = (
        "lane",
        "target_kind",
        "direct_target_property_computation",
        "attack_execution",
        "deliverable",
    )
    problems = _require_keys(lane, required, label)
    if not isinstance(lane, dict):
        return problems
    lane_id = lane.get("lane")
    if lane_id not in LANES:
        problems.append(f"{label}.lane: invalid")
        return sorted(set(problems))
    if not _is_nonempty_string(lane.get("deliverable")):
        problems.append(f"{label}.deliverable: empty")
    if not isinstance(lane.get("direct_target_property_computation"), bool):
        problems.append(
            f"{label}.direct_target_property_computation: expected bool"
        )
    if not isinstance(lane.get("attack_execution"), bool):
        problems.append(f"{label}.attack_execution: expected bool")
    if lane.get("target_kind") not in {
        "none",
        "public_parameters",
        "toy",
        "formal_model",
    }:
        problems.append(f"{label}.target_kind: invalid")

    if lane.get("direct_target_property_computation"):
        if lane_id not in {"literature_applicability", "structural"}:
            problems.append(
                f"{label}: direct target properties only in applicability/structural"
            )
        if lane.get("attack_execution"):
            problems.append(
                f"{label}: direct target property work cannot execute an attack"
            )
        if lane.get("target_kind") != "public_parameters":
            problems.append(
                f"{label}: direct target property work requires public_parameters"
            )

    lane_requirements = {
        "literature_applicability": "source_review_contract",
        "structural": "structural_contract",
        "mechanism": "mechanism_goal",
        "validator": "validator_goal",
        "bounded_experiment": "experiment_scope",
        "formalization": "formalization_contract",
    }
    required_key = lane_requirements[lane_id]
    if required_key not in lane:
        problems.append(f"{label}.{required_key}: missing for {lane_id}")

    if lane_id == "bounded_experiment":
        if lane.get("target_kind") != "toy":
            problems.append(f"{label}: bounded experiment target must be toy")
        if lane.get("direct_target_property_computation"):
            problems.append(
                f"{label}: bounded experiment cannot compute direct target properties"
            )
        if lane.get("attack_execution") is not True:
            problems.append(
                f"{label}: bounded experiment must declare attack_execution"
            )
        scope = lane.get("experiment_scope")
        if not isinstance(scope, dict):
            problems.append(f"{label}.experiment_scope: expected object")
        else:
            bits = scope.get("max_field_bits")
            if not isinstance(bits, int) or isinstance(bits, bool) or not 1 <= bits <= 24:
                problems.append(
                    f"{label}.experiment_scope.max_field_bits: outside 1..24"
                )
            forbidden = scope.get("forbidden_targets")
            if not isinstance(forbidden, list) or "secp256k1" not in forbidden:
                problems.append(
                    f"{label}.experiment_scope.forbidden_targets: secp256k1 required"
                )
    elif lane.get("attack_execution"):
        problems.append(f"{label}: attack execution only in bounded_experiment")
    return sorted(set(problems))


def validate_generation_binding(
    binding: Any,
    policy: dict[str, Any] | None,
) -> list[str]:
    label = "generation_binding"
    required = (
        "draft_id",
        "draft_sha256",
        "proposal_id",
        "proposal_sha256",
        "source_commit",
        "review_artifacts",
        "cell_id",
        "typed_evidence_digest",
        "toy_scope",
        "route_id",
        "threat_model",
        "contract_digests",
    )
    problems = _require_keys(binding, required, label)
    if not isinstance(binding, dict):
        return problems
    for key in ("draft_id", "proposal_id", "cell_id", "route_id"):
        if not _is_nonempty_string(binding.get(key)):
            problems.append(f"{label}.{key}: empty")
    for key in (
        "draft_sha256",
        "proposal_sha256",
        "typed_evidence_digest",
    ):
        if not _is_sha256(binding.get(key)):
            problems.append(f"{label}.{key}: invalid")
    if binding.get("threat_model") != PRIMARY_THREAT_MODEL:
        problems.append(f"{label}.threat_model: drift")
    toy_scope = binding.get("toy_scope")
    problems += _require_keys(
        toy_scope,
        ("curve_family", "max_field_bits", "forbidden_targets"),
        f"{label}.toy_scope",
    )
    if isinstance(toy_scope, dict):
        if not _is_nonempty_string(toy_scope.get("curve_family")):
            problems.append(f"{label}.toy_scope.curve_family: invalid")
        maximum = toy_scope.get("max_field_bits")
        if (
            not isinstance(maximum, int)
            or isinstance(maximum, bool)
            or not 1 <= maximum <= 24
        ):
            problems.append(f"{label}.toy_scope.max_field_bits: invalid")
        problems += _validate_string_list(
            toy_scope.get("forbidden_targets"),
            f"{label}.toy_scope.forbidden_targets",
            nonempty=True,
        )
    digests = binding.get("contract_digests")
    digest_keys = (
        "mechanism_contract_sha256",
        "prediction_contract_sha256",
        "cost_contract_sha256",
        "validator_design_contract_sha256",
    )
    problems += _require_keys(
        digests, digest_keys, f"{label}.contract_digests"
    )
    if isinstance(digests, dict):
        for key in digest_keys:
            if not _is_sha256(digests.get(key)):
                problems.append(
                    f"{label}.contract_digests.{key}: invalid"
                )
    if (
        not isinstance(binding.get("source_commit"), str)
        or not COMMIT_RE.fullmatch(binding["source_commit"])
    ):
        problems.append(f"{label}.source_commit: invalid")

    reviews = binding.get("review_artifacts")
    roles: list[str] = []
    review_ids: list[str] = []
    if not isinstance(reviews, list) or len(reviews) != len(
        GENERATION_REVIEW_ROLES
    ):
        problems.append(
            f"{label}.review_artifacts: exactly five reviews required"
        )
    else:
        for index, review in enumerate(reviews):
            item_label = f"{label}.review_artifacts[{index}]"
            problems += _require_keys(
                review,
                ("review_id", "reviewer_role", "review_sha256"),
                item_label,
            )
            if not isinstance(review, dict):
                continue
            review_id = review.get("review_id")
            role = review.get("reviewer_role")
            if not _is_nonempty_string(review_id):
                problems.append(f"{item_label}.review_id: empty")
            else:
                review_ids.append(review_id)
            if role not in GENERATION_REVIEW_ROLES:
                problems.append(f"{item_label}.reviewer_role: invalid")
            else:
                roles.append(role)
            if not _is_sha256(review.get("review_sha256")):
                problems.append(f"{item_label}.review_sha256: invalid")
    if set(roles) != GENERATION_REVIEW_ROLES or len(roles) != len(set(roles)):
        problems.append(f"{label}.review_artifacts: review roles incomplete")
    if len(review_ids) != len(set(review_ids)):
        problems.append(f"{label}.review_artifacts: duplicate review ids")

    registry = (
        policy.get("quality_cleared_draft_bindings", [])
        if isinstance(policy, dict)
        else []
    )
    registered = next(
        (
            item
            for item in registry
            if isinstance(item, dict)
            and item.get("draft_id") == binding.get("draft_id")
            and item.get("draft_sha256") == binding.get("draft_sha256")
        ),
        None,
    )
    if registered is None:
        problems.append(f"{label}: draft is not quality-cleared")
    else:
        expected = {
            key: registered.get(key)
            for key in required
        }
        if expected != binding:
            problems.append(f"{label}: registered draft binding mismatch")
    return sorted(set(problems))


def _validate_scenario(scenario: Any, label: str) -> list[str]:
    problems = _require_keys(scenario, ("prior_live", "outcomes"), label)
    if not isinstance(scenario, dict):
        return problems
    prior = scenario.get("prior_live")
    if (
        not isinstance(prior, (int, float))
        or isinstance(prior, bool)
        or not 0 <= prior <= 1
    ):
        problems.append(f"{label}.prior_live: invalid")
    outcomes = scenario.get("outcomes")
    if not isinstance(outcomes, list) or len(outcomes) < 2:
        problems.append(f"{label}.outcomes: at least two outcomes required")
        return problems
    names: list[str] = []
    live_sum = 0.0
    dead_sum = 0.0
    for index, outcome in enumerate(outcomes):
        item_label = f"{label}.outcomes[{index}]"
        problems += _require_keys(
            outcome, ("outcome", "p_if_live", "p_if_dead"), item_label
        )
        if not isinstance(outcome, dict):
            continue
        name = outcome.get("outcome")
        if not _is_nonempty_string(name):
            problems.append(f"{item_label}.outcome: empty")
        else:
            names.append(name)
        for key in ("p_if_live", "p_if_dead"):
            probability = outcome.get(key)
            if (
                not isinstance(probability, (int, float))
                or isinstance(probability, bool)
                or not 0 <= probability <= 1
            ):
                problems.append(f"{item_label}.{key}: invalid")
        if _number_at_least(outcome.get("p_if_live"), 0):
            live_sum += float(outcome["p_if_live"])
        if _number_at_least(outcome.get("p_if_dead"), 0):
            dead_sum += float(outcome["p_if_dead"])
    if len(names) != len(set(names)):
        problems.append(f"{label}.outcomes: duplicate names")
    if not math.isclose(live_sum, 1.0, abs_tol=1e-9):
        problems.append(f"{label}.outcomes: p_if_live must sum to 1")
    if not math.isclose(dead_sum, 1.0, abs_tol=1e-9):
        problems.append(f"{label}.outcomes: p_if_dead must sum to 1")
    return problems


def validate_snapshot(
    snapshot: Any,
    policy: dict[str, Any] | None = None,
) -> list[str]:
    label = "candidate_snapshot"
    required = (
        "candidate_id",
        "version",
        "created_at",
        "route_id",
        "cell_id",
        "typed_evidence_digest",
        "lane",
        "threat_model",
        "target_scope",
        "source_commit",
        "source_review_ids",
        "dependencies",
        "correlation_groups",
        "diversity_tags",
        "scoring_contract",
        "snapshot_digest",
    )
    problems = _require_keys(snapshot, required, label)
    if not isinstance(snapshot, dict):
        return problems
    if "authorization" in snapshot or "authorized" in snapshot:
        problems.append(f"{label}: authorization fields are forbidden")
    if not _is_nonempty_string(snapshot.get("candidate_id")):
        problems.append(f"{label}.candidate_id: invalid")
    version = snapshot.get("version")
    if not isinstance(version, int) or isinstance(version, bool) or version < 1:
        problems.append(f"{label}.version: invalid")
    if not _is_iso_datetime(snapshot.get("created_at")):
        problems.append(f"{label}.created_at: invalid")
    if not _is_nonempty_string(snapshot.get("route_id")):
        problems.append(f"{label}.route_id: invalid")
    if not _is_nonempty_string(snapshot.get("cell_id")):
        problems.append(f"{label}.cell_id: invalid")
    if not _is_sha256(snapshot.get("typed_evidence_digest")):
        problems.append(f"{label}.typed_evidence_digest: invalid")
    problems += validate_lane(snapshot.get("lane"))
    if snapshot.get("threat_model") != PRIMARY_THREAT_MODEL:
        problems.append(f"{label}.threat_model: drift")
    if not isinstance(snapshot.get("source_commit"), str) or not COMMIT_RE.fullmatch(
        snapshot["source_commit"]
    ):
        problems.append(f"{label}.source_commit: invalid")
    elif not scientific_source_commit_allowed(snapshot["source_commit"]):
        problems.append(
            f"{label}.source_commit: not reproducible from protected provenance"
        )
    if not _is_sha256(snapshot.get("snapshot_digest")):
        problems.append(f"{label}.snapshot_digest: invalid")
    elif snapshot_digest(snapshot) != snapshot["snapshot_digest"]:
        problems.append(f"{label}.snapshot_digest: mismatch")

    target = snapshot.get("target_scope")
    problems += _require_keys(
        target, ("kind", "curve_family", "field_bits", "forbidden_targets"),
        f"{label}.target_scope",
    )
    if isinstance(target, dict):
        problems += _validate_string_list(
            target.get("forbidden_targets"),
            f"{label}.target_scope.forbidden_targets",
        )
        if not _is_nonempty_string(target.get("curve_family")):
            problems.append(f"{label}.target_scope.curve_family: invalid")
        field_bits = target.get("field_bits")
        if (
            not isinstance(field_bits, int)
            or isinstance(field_bits, bool)
            or field_bits < 1
        ):
            problems.append(f"{label}.target_scope.field_bits: invalid")
        lane = snapshot.get("lane")
        if isinstance(lane, dict) and target.get("kind") != lane.get("target_kind"):
            problems.append(
                f"{label}.target_scope.kind: does not match lane.target_kind"
            )
        if (
            isinstance(lane, dict)
            and lane.get("lane") == "bounded_experiment"
            and "secp256k1" not in target.get("forbidden_targets", [])
        ):
            problems.append(
                f"{label}.target_scope: bounded experiment must forbid secp256k1"
            )
        if (
            isinstance(lane, dict)
            and lane.get("lane") == "bounded_experiment"
            and isinstance(field_bits, int)
            and not isinstance(field_bits, bool)
        ):
            experiment_scope = lane.get("experiment_scope")
            max_field_bits = (
                experiment_scope.get("max_field_bits")
                if isinstance(experiment_scope, dict)
                else None
            )
            if field_bits > 24 or (
                isinstance(max_field_bits, int)
                and not isinstance(max_field_bits, bool)
                and field_bits > max_field_bits
            ):
                problems.append(
                    f"{label}.target_scope.field_bits: exceeds bounded lane ceiling"
                )

    source_reviews = snapshot.get("source_review_ids")
    problems += _validate_string_list(
        source_reviews, f"{label}.source_review_ids"
    )
    if policy and isinstance(source_reviews, list):
        known = set(policy.get("source_review_ids", []))
        missing = sorted(set(source_reviews) - known)
        for review_id in missing:
            problems.append(
                f"{label}.source_review_ids: unknown {review_id}"
            )

    dependencies = snapshot.get("dependencies")
    if not isinstance(dependencies, list):
        problems.append(f"{label}.dependencies: expected array")
    else:
        dep_keys: set[tuple[Any, Any]] = set()
        for index, dependency in enumerate(dependencies):
            dep_label = f"{label}.dependencies[{index}]"
            problems += _require_keys(
                dependency,
                ("candidate_id", "minimum_version", "accepted_outcomes"),
                dep_label,
            )
            if not isinstance(dependency, dict):
                continue
            dep_key = (
                dependency.get("candidate_id"),
                dependency.get("minimum_version"),
            )
            if dep_key in dep_keys:
                problems.append(f"{dep_label}: duplicate")
            dep_keys.add(dep_key)
            if not _is_nonempty_string(dependency.get("candidate_id")):
                problems.append(f"{dep_label}.candidate_id: invalid")
            minimum = dependency.get("minimum_version")
            if not isinstance(minimum, int) or isinstance(minimum, bool) or minimum < 1:
                problems.append(f"{dep_label}.minimum_version: invalid")
            accepted = dependency.get("accepted_outcomes")
            if (
                not isinstance(accepted, list)
                or not accepted
                or any(item not in SUCCESSFUL_PREREQUISITE_OUTCOMES for item in accepted)
            ):
                problems.append(f"{dep_label}.accepted_outcomes: invalid")

    problems += _validate_string_list(
        snapshot.get("correlation_groups"),
        f"{label}.correlation_groups",
    )
    problems += _validate_string_list(
        snapshot.get("diversity_tags"),
        f"{label}.diversity_tags",
        nonempty=True,
    )

    scoring = snapshot.get("scoring_contract")
    problems += _require_keys(
        scoring, ("elicitation_ids", "scenarios"), f"{label}.scoring_contract"
    )
    if isinstance(scoring, dict):
        problems += _validate_string_list(
            scoring.get("elicitation_ids"),
            f"{label}.scoring_contract.elicitation_ids",
            nonempty=True,
        )
        if (
            isinstance(scoring.get("elicitation_ids"), list)
            and len(scoring["elicitation_ids"]) < 2
        ):
            problems.append(
                f"{label}.scoring_contract.elicitation_ids: two independent elicitations required"
            )
        scenarios = scoring.get("scenarios")
        problems += _require_keys(
            scenarios, ("low", "base", "high"),
            f"{label}.scoring_contract.scenarios",
        )
        if isinstance(scenarios, dict):
            for scenario_name in ("low", "base", "high"):
                problems += _validate_scenario(
                    scenarios.get(scenario_name),
                    f"{label}.scoring_contract.scenarios.{scenario_name}",
                )

    lane_id = (
        snapshot.get("lane", {}).get("lane")
        if isinstance(snapshot.get("lane"), dict)
        else None
    )
    generation_lanes = {"mechanism", "validator", "bounded_experiment"}
    if lane_id in generation_lanes:
        problems += validate_generation_binding(
            snapshot.get("generation_binding"), policy
        )
        if (
            isinstance(snapshot.get("generation_binding"), dict)
            and snapshot["generation_binding"].get("source_commit")
            != snapshot.get("source_commit")
        ):
            problems.append(
                f"{label}.source_commit: generation binding mismatch"
            )
        if isinstance(snapshot.get("generation_binding"), dict):
            binding = snapshot["generation_binding"]
            for key in (
                "cell_id",
                "typed_evidence_digest",
                "route_id",
                "threat_model",
            ):
                if binding.get(key) != snapshot.get(key):
                    problems.append(
                        f"{label}.{key}: generation binding mismatch"
                    )
            bound_scope = binding.get("toy_scope", {})
            target_scope = snapshot.get("target_scope", {})
            if (
                isinstance(bound_scope, dict)
                and isinstance(target_scope, dict)
            ):
                if (
                    bound_scope.get("curve_family")
                    != target_scope.get("curve_family")
                ):
                    problems.append(
                        f"{label}.target_scope.curve_family: "
                        "generation binding mismatch"
                    )
                field_bits = target_scope.get("field_bits")
                maximum = bound_scope.get("max_field_bits")
                if (
                    isinstance(field_bits, int)
                    and not isinstance(field_bits, bool)
                    and isinstance(maximum, int)
                    and field_bits > maximum
                ):
                    problems.append(
                        f"{label}.target_scope.field_bits: "
                        "exceeds reviewed toy scope"
                    )
                if not set(bound_scope.get("forbidden_targets", [])).issubset(
                    set(target_scope.get("forbidden_targets", []))
                ):
                    problems.append(
                        f"{label}.target_scope.forbidden_targets: "
                        "generation binding mismatch"
                    )
            current_digests = scientific_contract_digests(
                snapshot.get("mechanism_contract"),
                snapshot.get("prediction_contract"),
                snapshot.get("cost_contract"),
                snapshot.get("validator_contract"),
            )
            bound_digests = binding.get("contract_digests", {})
            digest_keys: tuple[str, ...] = ()
            if lane_id in {"mechanism", "bounded_experiment"}:
                digest_keys += ("mechanism_contract_sha256",)
            if lane_id == "bounded_experiment":
                digest_keys += (
                    "prediction_contract_sha256",
                    "cost_contract_sha256",
                )
            if lane_id in {"validator", "bounded_experiment"}:
                digest_keys += ("validator_design_contract_sha256",)
            for key in digest_keys:
                if bound_digests.get(key) != current_digests.get(key):
                    problems.append(
                        f"{label}.{key}: reviewed contract digest mismatch"
                    )
    if lane_id in {"mechanism", "bounded_experiment"}:
        problems += validate_mechanism_contract(
            snapshot.get("mechanism_contract"),
            require_assured=True,
            evidence_registry=(
                policy.get("mechanism_assurance_evidence", [])
                if isinstance(policy, dict)
                else []
            ),
        )
    if lane_id == "validator":
        problems += validate_validator_contract(
            snapshot.get("validator_contract"),
            evidence_registry=(
                policy.get("validator_independence_evidence", [])
                if isinstance(policy, dict)
                else []
            ),
            implementation_registry=(
                policy.get("validator_implementation_evidence", [])
                if isinstance(policy, dict)
                else []
            ),
        )
    if lane_id == "bounded_experiment":
        problems += validate_prediction_contract(
            snapshot.get("prediction_contract")
        )
        problems += validate_cost_contract(
            snapshot.get("cost_contract"), require_execution=True
        )
        problems += validate_validator_contract(
            snapshot.get("validator_contract"),
            evidence_registry=(
                policy.get("validator_independence_evidence", [])
                if isinstance(policy, dict)
                else []
            ),
            implementation_registry=(
                policy.get("validator_implementation_evidence", [])
                if isinstance(policy, dict)
                else []
            ),
        )
        sizes = snapshot.get("prediction_contract", {}).get("tested_sizes")
        lane_scope = (
            snapshot.get("lane", {}).get("experiment_scope", {})
            if isinstance(snapshot.get("lane"), dict)
            else {}
        )
        max_field_bits = lane_scope.get("max_field_bits")
        if isinstance(sizes, list) and isinstance(max_field_bits, int):
            if any(
                isinstance(size, int)
                and not isinstance(size, bool)
                and size > min(24, max_field_bits)
                for size in sizes
            ):
                problems.append(
                    f"{label}.prediction_contract.tested_sizes: "
                    "exceeds bounded lane ceiling"
                )
    return sorted(set(problems))


def derive_gates(
    snapshot: dict[str, Any],
    policy: dict[str, Any],
) -> list[str]:
    gates: set[str] = set()
    validation = validate_snapshot(snapshot, policy)
    if validation:
        gates.add("invalid_candidate_snapshot")
    if snapshot.get("threat_model") != policy.get(
        "primary_threat_model", PRIMARY_THREAT_MODEL
    ):
        gates.add("changes_threat_model")

    lane = snapshot.get("lane", {})
    lane_id = lane.get("lane") if isinstance(lane, dict) else None
    target = snapshot.get("target_scope", {})
    if isinstance(target, dict):
        exact_target = (
            target.get("curve_family") == "secp256k1"
            and lane_id == "bounded_experiment"
        )
        if exact_target or (
            lane_id == "bounded_experiment"
            and "secp256k1" not in target.get("forbidden_targets", [])
        ):
            gates.add("targets_secp256k1_directly")
    if (
        isinstance(lane, dict)
        and lane.get("direct_target_property_computation")
        and (
            lane_id not in {"literature_applicability", "structural"}
            or lane.get("attack_execution")
        )
    ):
        gates.add("direct_target_property_lane_violation")

    mechanism_problems = validate_mechanism_contract(
        snapshot.get("mechanism_contract"),
        require_assured=True,
        evidence_registry=policy.get("mechanism_assurance_evidence", []),
    )
    if lane_id in {"mechanism", "bounded_experiment"} and mechanism_problems:
        gates.add("missing_exact_mechanism")
    if lane_id in {"mechanism", "validator", "bounded_experiment"} and (
        validate_generation_binding(
            snapshot.get("generation_binding"), policy
        )
    ):
        gates.add("missing_quality_cleared_generation_binding")
    if lane_id in {"mechanism", "validator", "bounded_experiment"} and any(
        "generation binding mismatch" in problem
        or "reviewed contract digest mismatch" in problem
        for problem in validation
    ):
        gates.add("missing_quality_cleared_generation_binding")
    prediction_problems = validate_prediction_contract(
        snapshot.get("prediction_contract")
    )
    if lane_id == "bounded_experiment" and prediction_problems:
        gates.add("missing_falsifiable_prediction")
    cost_problems = validate_cost_contract(
        snapshot.get("cost_contract"), require_execution=True
    )
    if lane_id == "bounded_experiment" and cost_problems:
        gates.add("missing_full_cost_contract")
    validator_problems = validate_validator_contract(
        snapshot.get("validator_contract"),
        evidence_registry=policy.get(
            "validator_independence_evidence", []
        ),
        implementation_registry=policy.get(
            "validator_implementation_evidence", []
        ),
    )
    if lane_id in {"validator", "bounded_experiment"} and validator_problems:
        gates.add("missing_independent_validator")
    cost = snapshot.get("cost_contract")
    if lane_id == "bounded_experiment" and isinstance(cost, dict):
        amortization = cost.get("amortization")
        if isinstance(amortization, dict) and (
            amortization.get("class") != "none_single_target"
            or amortization.get("target_count") != 1
        ):
            gates.add("changes_threat_model")
    if (
        lane_id == "bounded_experiment"
        and isinstance(cost, dict)
        and isinstance(cost.get("preprocessing"), dict)
        and cost["preprocessing"].get("included_in_totals") is not True
    ):
        gates.add("hidden_or_unpriced_precomputation")
    prediction = snapshot.get("prediction_contract")
    if lane_id == "bounded_experiment" and isinstance(prediction, dict):
        sizes = prediction.get("tested_sizes")
        experiment_scope = (
            lane.get("experiment_scope", {})
            if isinstance(lane, dict)
            else {}
        )
        max_field_bits = experiment_scope.get("max_field_bits")
        if isinstance(sizes, list) and isinstance(max_field_bits, int) and any(
            isinstance(size, int)
            and not isinstance(size, bool)
            and size > min(24, max_field_bits)
            for size in sizes
        ):
            gates.add("toy_scope_exceeded")
    return sorted(gates)


def validate_owner_decisions(
    owner_decisions: list[dict[str, Any]],
    candidate_index: dict[tuple[str, int], dict[str, Any]],
    authorized_owner_roles: Iterable[str] | None = None,
) -> list[str]:
    problems: list[str] = []
    seen: set[str] = set()
    allowed_roles = (
        set(authorized_owner_roles)
        if authorized_owner_roles is not None
        else None
    )
    for index, decision in enumerate(owner_decisions):
        label = f"owner_decisions[{index}]"
        required = (
            "decision_id",
            "decision_type",
            "decided_at",
            "owner_role",
            "candidate_id",
            "candidate_version",
            "candidate_digest",
            "status",
        )
        problems += _require_keys(decision, required, label)
        if not isinstance(decision, dict):
            continue
        decision_id = decision.get("decision_id")
        if not _is_nonempty_string(decision_id):
            problems.append(f"{label}.decision_id: invalid")
        elif decision_id in seen:
            problems.append(f"{label}.decision_id: duplicate")
        else:
            seen.add(decision_id)
        if decision.get("decision_type") != "owner_authorization":
            problems.append(f"{label}.decision_type: invalid")
        if not _is_iso_datetime(decision.get("decided_at")):
            problems.append(f"{label}.decided_at: invalid")
        owner_role = decision.get("owner_role")
        if not _is_nonempty_string(owner_role):
            problems.append(f"{label}.owner_role: invalid")
        elif allowed_roles is not None and owner_role not in allowed_roles:
            problems.append(f"{label}.owner_role: not authorized by policy")
        if decision.get("status") not in {"approved", "denied", "revoked"}:
            problems.append(f"{label}.status: invalid")
        key = (decision.get("candidate_id"), decision.get("candidate_version"))
        candidate = candidate_index.get(key)
        if candidate is None:
            problems.append(f"{label}: unknown candidate/version")
        elif candidate.get("snapshot_digest") != decision.get("candidate_digest"):
            problems.append(f"{label}.candidate_digest: mismatch")
        elif _is_iso_datetime(decision.get("decided_at")) and _is_iso_datetime(
            candidate.get("created_at")
        ):
            decided_at = datetime.fromisoformat(
                decision["decided_at"].replace("Z", "+00:00")
            )
            created_at = datetime.fromisoformat(
                candidate["created_at"].replace("Z", "+00:00")
            )
            if decided_at < created_at:
                problems.append(
                    f"{label}.decided_at: predates immutable candidate snapshot"
                )
    return sorted(set(problems))


def validate_lifecycle_events(
    events: list[dict[str, Any]],
    candidate_index: dict[tuple[str, int], dict[str, Any]],
    owner_decisions: list[dict[str, Any]],
    authorized_owner_roles: Iterable[str] | None = None,
) -> tuple[list[str], dict[tuple[str, int], str]]:
    problems = validate_owner_decisions(
        owner_decisions,
        candidate_index,
        authorized_owner_roles,
    )
    allowed_roles = (
        set(authorized_owner_roles)
        if authorized_owner_roles is not None
        else None
    )
    decision_index = {
        decision.get("decision_id"): decision
        for decision in owner_decisions
        if isinstance(decision, dict)
    }
    states: dict[tuple[str, int], str] = {}
    last_time: dict[tuple[str, int], datetime] = {}
    seen_event_ids: set[str] = set()

    for index, event in enumerate(events):
        label = f"lifecycle_events[{index}]"
        required = (
            "event_id",
            "candidate_id",
            "candidate_version",
            "candidate_digest",
            "occurred_at",
            "from_state",
            "to_state",
            "actor_class",
            "reason",
        )
        problems += _require_keys(event, required, label)
        if not isinstance(event, dict):
            continue
        event_id = event.get("event_id")
        if not _is_nonempty_string(event_id):
            problems.append(f"{label}.event_id: invalid")
        elif event_id in seen_event_ids:
            problems.append(f"{label}.event_id: duplicate")
        else:
            seen_event_ids.add(event_id)

        key = (event.get("candidate_id"), event.get("candidate_version"))
        candidate = candidate_index.get(key)
        if candidate is None:
            problems.append(f"{label}: unknown candidate/version")
            continue
        if candidate.get("snapshot_digest") != event.get("candidate_digest"):
            problems.append(f"{label}.candidate_digest: mismatch")

        current = states.get(key)
        if event.get("from_state") != current:
            problems.append(
                f"{label}.from_state: expected {current!r}, got {event.get('from_state')!r}"
            )
        target = event.get("to_state")
        if target not in NORMAL_TRANSITIONS.get(current, set()):
            problems.append(
                f"{label}: invalid transition {current!r} -> {target!r}"
            )

        occurred_at = event.get("occurred_at")
        if _is_iso_datetime(occurred_at):
            timestamp = datetime.fromisoformat(occurred_at.replace("Z", "+00:00"))
            previous = last_time.get(key)
            if previous is not None and timestamp < previous:
                problems.append(f"{label}.occurred_at: append order regressed")
            last_time[key] = timestamp
        else:
            problems.append(f"{label}.occurred_at: invalid")

        if target in {"admissible", "recommended"} and event.get("actor_class") != "engine":
            problems.append(f"{label}: {target} must be computed by engine")
        if target == "authorized":
            if event.get("actor_class") != "owner":
                problems.append(f"{label}: authorization actor must be owner")
            decision = decision_index.get(event.get("owner_decision_id"))
            if decision is None:
                problems.append(f"{label}: missing owner authorization decision")
            elif (
                decision.get("status") != "approved"
                or decision.get("candidate_digest")
                != candidate.get("snapshot_digest")
                or (
                    allowed_roles is not None
                    and decision.get("owner_role") not in allowed_roles
                )
            ):
                problems.append(f"{label}: owner decision does not authorize snapshot")
            elif (
                _is_iso_datetime(decision.get("decided_at"))
                and _is_iso_datetime(occurred_at)
                and datetime.fromisoformat(
                    decision["decided_at"].replace("Z", "+00:00")
                )
                > datetime.fromisoformat(
                    occurred_at.replace("Z", "+00:00")
                )
            ):
                problems.append(f"{label}: authorization predates owner decision")
        if target == "running" and current != "authorized":
            problems.append(f"{label}: running requires authorization")
        if target == "terminal":
            outcome = event.get("outcome")
            if not _is_nonempty_string(outcome):
                problems.append(f"{label}.outcome: required")
            if current != "running" and outcome not in {"inapplicable", "completed"}:
                problems.append(
                    f"{label}: desk terminal may only be inapplicable/completed"
                )
        if target in STATES:
            states[key] = target
    return sorted(set(problems)), states


def binary_entropy(probability: float) -> float:
    if probability <= 0.0 or probability >= 1.0:
        return 0.0
    return -probability * math.log2(probability) - (
        1.0 - probability
    ) * math.log2(1.0 - probability)


def expected_information_gain(scenario: dict[str, Any]) -> float:
    problems = _validate_scenario(scenario, "scenario")
    if problems:
        raise ValueError("; ".join(problems))
    prior = float(scenario["prior_live"])
    expected_posterior_entropy = 0.0
    for outcome in scenario["outcomes"]:
        probability = (
            prior * float(outcome["p_if_live"])
            + (1.0 - prior) * float(outcome["p_if_dead"])
        )
        if probability == 0:
            continue
        posterior_live = (
            prior * float(outcome["p_if_live"]) / probability
        )
        expected_posterior_entropy += (
            probability * binary_entropy(posterior_live)
        )
    return max(0.0, binary_entropy(prior) - expected_posterior_entropy)


def score_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    scenarios = snapshot["scoring_contract"]["scenarios"]
    eig = {
        name: expected_information_gain(scenarios[name])
        for name in ("low", "base", "high")
    }
    return {
        "eig_bits": eig,
        "worst_eig_bits": min(eig.values()),
        "base_eig_bits": eig["base"],
        "best_eig_bits": max(eig.values()),
        "elicitation_count": len(
            snapshot["scoring_contract"]["elicitation_ids"]
        ),
    }


def cost_vector(snapshot: dict[str, Any]) -> dict[str, Any]:
    cost = snapshot.get("cost_contract")
    if not isinstance(cost, dict):
        return {
            "compute_hours": 0.0,
            "storage_gb": 0.0,
            "money_usd": 0.0,
            "implementation_hours": 0.0,
            "reviewer_hours": 0.0,
            "wall_time_hours": 0.0,
            "peak_memory_gb": 0.0,
            "workers": 1,
            "shared_setup_id": None,
            "shared_setup_hours": 0.0,
        }
    online = cost["online"]
    offline = cost["offline"]
    shared = cost["shared_setup"]
    return {
        "compute_hours": float(
            online["cpu_hours"]
            + online["gpu_hours"]
            + offline["cpu_hours"]
            + offline["gpu_hours"]
        ),
        "storage_gb": float(cost["storage_gb"]),
        "money_usd": float(cost["money_usd"]),
        "implementation_hours": float(cost["implementation_hours"]),
        "reviewer_hours": float(cost["reviewer_hours"]),
        "wall_time_hours": float(cost["wall_time_hours"]),
        "peak_memory_gb": float(cost["peak_memory_gb"]),
        "workers": int(cost["workers"]),
        "shared_setup_id": shared["setup_id"],
        "shared_setup_hours": float(shared["hours"]),
    }


def normalized_cost(
    vector: dict[str, Any],
    budgets: dict[str, float],
) -> float:
    terms: list[float] = []
    for key in ADDITIVE_COSTS + PEAK_COSTS:
        budget = float(budgets.get(key, 0))
        value = float(vector.get(key, 0))
        if budget > 0:
            terms.append(value / budget)
        elif value > 0:
            terms.append(math.inf)
    setup_budget = float(budgets.get("shared_setup_hours", 0))
    setup_value = float(vector.get("shared_setup_hours", 0))
    if setup_budget > 0:
        terms.append(setup_value / setup_budget)
    elif setup_value > 0:
        terms.append(math.inf)
    return sum(terms) if terms else 1.0


def _completed_dependencies(
    lifecycle_events: list[dict[str, Any]],
) -> dict[str, list[tuple[int, str]]]:
    completed: dict[str, list[tuple[int, str]]] = {}
    for event in lifecycle_events:
        if event.get("to_state") != "terminal":
            continue
        outcome = event.get("outcome")
        if outcome not in SUCCESSFUL_PREREQUISITE_OUTCOMES:
            continue
        completed.setdefault(event["candidate_id"], []).append(
            (event["candidate_version"], outcome)
        )
    return completed


def dependency_satisfied(
    dependency: dict[str, Any],
    completed: dict[str, list[tuple[int, str]]],
) -> bool:
    accepted = set(dependency["accepted_outcomes"])
    return any(
        version >= dependency["minimum_version"] and outcome in accepted
        for version, outcome in completed.get(dependency["candidate_id"], [])
    )


def _portfolio_cost(entries: list[dict[str, Any]]) -> dict[str, float]:
    result = {key: 0.0 for key in ADDITIVE_COSTS}
    result.update({key: 0.0 for key in PEAK_COSTS})
    result["shared_setup_hours"] = 0.0
    seen_setup: set[str] = set()
    for entry in entries:
        vector = entry["cost_vector"]
        for key in ADDITIVE_COSTS:
            result[key] += float(vector[key])
        for key in PEAK_COSTS:
            result[key] = max(result[key], float(vector[key]))
        setup_id = vector.get("shared_setup_id")
        if setup_id is None:
            result["shared_setup_hours"] += float(
                vector["shared_setup_hours"]
            )
        elif setup_id not in seen_setup:
            seen_setup.add(setup_id)
            result["shared_setup_hours"] += float(
                vector["shared_setup_hours"]
            )
    return result


def _within_budgets(
    costs: dict[str, float],
    budgets: dict[str, float],
) -> bool:
    return all(
        key not in budgets or costs[key] <= float(budgets[key]) + 1e-12
        for key in costs
    )


def optimize_portfolio(
    entries: list[dict[str, Any]],
    policy: dict[str, Any],
    completed: dict[str, list[tuple[int, str]]] | None = None,
    *,
    scenario: str = "base",
) -> dict[str, Any]:
    completed = completed or {}
    maximum = int(policy.get("portfolio_max_candidates", 12))
    if len(entries) > maximum:
        return {
            "status": "coverage_overflow",
            "candidate_count": len(entries),
            "maximum_supported": maximum,
            "combination_count": 2 ** len(entries),
            "candidate_ids": sorted(entry["candidate_id"] for entry in entries),
            "reason": (
                "Exhaustive comparison was not attempted because the declared "
                "coverage limit was exceeded; no opaque truncation occurred."
            ),
            "selected_ids": [],
        }

    entries = sorted(entries, key=lambda item: item["candidate_id"])
    candidate_ids = [entry["candidate_id"] for entry in entries]
    ids = set(candidate_ids)
    if len(ids) != len(candidate_ids):
        duplicates = sorted(
            candidate_id
            for candidate_id in ids
            if candidate_ids.count(candidate_id) > 1
        )
        return {
            "status": "invalid_duplicate_candidate_ids",
            "candidate_count": len(entries),
            "duplicate_candidate_ids": duplicates,
            "combination_count": 0,
            "selected_ids": [],
            "reason": (
                "At most one active immutable version of a candidate may "
                "enter one portfolio comparison."
            ),
        }
    max_selected = int(policy.get("max_selected_per_cycle", len(entries)))
    budgets = policy.get("portfolio_budget", {})
    correlation_caps = policy.get("correlation_max_per_group", {})
    default_correlation_cap = int(policy.get("default_correlation_cap", len(entries)))
    minimum_diversity = int(policy.get("minimum_diversity_tags", 0))
    required_tags = set(policy.get("required_diversity_tags", []))

    combinations_considered = 0
    feasible_combinations = 0
    best: tuple[Any, ...] | None = None
    best_payload: dict[str, Any] | None = None

    for size in range(0, min(max_selected, len(entries)) + 1):
        for subset_tuple in itertools.combinations(entries, size):
            subset = list(subset_tuple)
            combinations_considered += 1
            subset_ids = {entry["candidate_id"] for entry in subset}

            dependencies_ok = True
            for entry in subset:
                for dependency in entry["snapshot"].get("dependencies", []):
                    if not dependency_satisfied(dependency, completed):
                        dependencies_ok = False
                        break
                if not dependencies_ok:
                    break
            if not dependencies_ok:
                continue

            group_counts: dict[str, int] = {}
            for entry in subset:
                for group in entry["snapshot"].get("correlation_groups", []):
                    group_counts[group] = group_counts.get(group, 0) + 1
            if any(
                count
                > int(correlation_caps.get(group, default_correlation_cap))
                for group, count in group_counts.items()
            ):
                continue

            diversity = {
                tag
                for entry in subset
                for tag in entry["snapshot"].get("diversity_tags", [])
            }
            if subset and len(diversity) < minimum_diversity:
                continue
            if subset and not required_tags.issubset(diversity):
                continue

            costs = _portfolio_cost(subset)
            if not _within_budgets(costs, budgets):
                continue

            feasible_combinations += 1
            objective = sum(
                float(entry["score"]["eig_bits"][scenario])
                for entry in subset
            )
            selected_ids = tuple(sorted(subset_ids))
            tie_key = (
                objective,
                -costs["money_usd"],
                -costs["compute_hours"],
                tuple(reversed(selected_ids)),
            )
            if best is None or tie_key > best:
                best = tie_key
                best_payload = {
                    "selected_ids": list(selected_ids),
                    "objective_eig_bits": objective,
                    "costs": costs,
                    "diversity_tags": sorted(diversity),
                    "correlation_counts": dict(sorted(group_counts.items())),
                }

    if best_payload is None:
        best_payload = {
            "selected_ids": [],
            "objective_eig_bits": 0.0,
            "costs": _portfolio_cost([]),
            "diversity_tags": [],
            "correlation_counts": {},
        }
    return {
        "status": "compared",
        "scenario": scenario,
        "candidate_count": len(entries),
        "combination_count": 2 ** len(entries),
        "combinations_considered": combinations_considered,
        "feasible_combinations": feasible_combinations,
        **best_payload,
    }


def _events_before(
    lifecycle_events: list[dict[str, Any]],
    occurred_at: str,
) -> list[dict[str, Any]]:
    if not _is_iso_datetime(occurred_at):
        return []
    boundary = datetime.fromisoformat(occurred_at.replace("Z", "+00:00"))
    ordered: list[tuple[datetime, int, dict[str, Any]]] = []
    for index, event in enumerate(lifecycle_events):
        timestamp_value = event.get("occurred_at")
        if not _is_iso_datetime(timestamp_value):
            continue
        timestamp = datetime.fromisoformat(
            timestamp_value.replace("Z", "+00:00")
        )
        if timestamp < boundary:
            ordered.append((timestamp, index, event))
    return [
        event
        for _, _, event in sorted(
            ordered,
            key=lambda item: (item[0], item[1]),
        )
    ]


def build_recommendation_binding(
    policy: dict[str, Any],
    immutable_candidates: list[dict[str, Any]],
    lifecycle_events: list[dict[str, Any]],
    occurred_at: str,
) -> dict[str, Any]:
    """Bind a recommendation to a reproducible base-portfolio computation."""

    prior_events = _events_before(lifecycle_events, occurred_at)
    states: dict[tuple[str, int], str] = {}
    for event in prior_events:
        key = (event.get("candidate_id"), event.get("candidate_version"))
        target = event.get("to_state")
        if target in STATES:
            states[key] = target
    completed = _completed_dependencies(prior_events)
    boundary = (
        datetime.fromisoformat(occurred_at.replace("Z", "+00:00"))
        if _is_iso_datetime(occurred_at)
        else None
    )

    entries: list[dict[str, Any]] = []
    for candidate in immutable_candidates:
        created_at = candidate.get("created_at")
        if (
            boundary is None
            or not _is_iso_datetime(created_at)
            or datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            > boundary
        ):
            continue
        key = (candidate.get("candidate_id"), candidate.get("version"))
        if states.get(key, "idea") not in {
            "validator_ready",
            "admissible",
            "recommended",
        }:
            continue
        if validate_snapshot(candidate, policy) or derive_gates(candidate, policy):
            continue
        if not all(
            dependency_satisfied(dependency, completed)
            for dependency in candidate.get("dependencies", [])
        ):
            continue
        score = score_snapshot(candidate)
        vector = cost_vector(candidate)
        entries.append(
            {
                "candidate_id": candidate["candidate_id"],
                "snapshot": candidate,
                "score": score,
                "cost_vector": vector,
                "priority": {},
            }
        )

    portfolio = optimize_portfolio(
        entries,
        policy,
        completed,
        scenario="base",
    )
    selected = set(portfolio.get("selected_ids", []))
    payload = {
        "policy_digest": sha256_json(policy),
        "portfolio_status": portfolio.get("status"),
        "selected_snapshots": sorted(
            [
                {
                    "candidate_id": entry["snapshot"]["candidate_id"],
                    "candidate_version": entry["snapshot"]["version"],
                    "candidate_digest": entry["snapshot"]["snapshot_digest"],
                }
                for entry in entries
                if entry["candidate_id"] in selected
            ],
            key=lambda item: (
                item["candidate_id"],
                item["candidate_version"],
            ),
        ),
    }
    return {
        **payload,
        "selection_digest": sha256_json(payload),
    }


def validate_recommendation_bindings(
    policy: dict[str, Any],
    immutable_candidates: list[dict[str, Any]],
    lifecycle_events: list[dict[str, Any]],
) -> list[str]:
    problems: list[str] = []
    for index, event in enumerate(lifecycle_events):
        if event.get("to_state") != "recommended":
            continue
        label = f"lifecycle_events[{index}].recommendation_binding"
        expected = build_recommendation_binding(
            policy,
            immutable_candidates,
            lifecycle_events,
            event.get("occurred_at"),
        )
        actual = event.get("recommendation_binding")
        if actual != expected:
            problems.append(
                f"{label}: does not match the recomputed base portfolio"
            )
        selected_ids = {
            item["candidate_id"]
            for item in expected["selected_snapshots"]
        }
        if event.get("candidate_id") not in selected_ids:
            problems.append(
                f"{label}: candidate was not selected by the recomputed "
                "base portfolio"
            )
    return sorted(set(problems))


def build_calibration(
    candidates: list[dict[str, Any]],
    outcomes: list[dict[str, Any]],
    *,
    minimum_native_n: int = 5,
) -> dict[str, Any]:
    known_digests = {
        candidate["snapshot_digest"]
        for candidate in candidates
    }
    scores: list[dict[str, Any]] = []
    excluded: dict[str, int] = {}
    rejected: list[str] = []
    seen_event_ids: set[str] = set()
    for index, event in enumerate(outcomes):
        event_id = event.get("event_id")
        if not _is_nonempty_string(event_id):
            rejected.append(f"outcomes[{index}]: invalid event_id")
            continue
        if event_id in seen_event_ids:
            rejected.append(f"outcomes[{index}]: duplicate event_id {event_id}")
            continue
        seen_event_ids.add(event_id)
        event_class = event.get("event_class")
        if event_class in CALIBRATION_EXCLUDED_CLASSES:
            excluded[event_class] = excluded.get(event_class, 0) + 1
            continue
        if event_class != "native_empirical":
            excluded["other_non_native"] = excluded.get("other_non_native", 0) + 1
            continue
        digest = event.get("candidate_digest")
        frozen = event.get("frozen_prediction")
        actual = event.get("actual_live")
        if digest not in known_digests:
            rejected.append(f"outcomes[{index}]: unknown candidate digest")
            continue
        if (
            not isinstance(frozen, dict)
            or not isinstance(frozen.get("prior_live"), (int, float))
            or isinstance(frozen.get("prior_live"), bool)
            or not 0 <= frozen["prior_live"] <= 1
        ):
            rejected.append(f"outcomes[{index}]: invalid frozen prediction")
            continue
        if not isinstance(actual, bool):
            rejected.append(f"outcomes[{index}]: actual_live must be bool")
            continue
        prior = float(frozen["prior_live"])
        brier = (prior - float(actual)) ** 2
        scores.append(
            {
                "event_id": event_id,
                "candidate_digest": digest,
                "frozen_prior_live": prior,
                "actual_live": actual,
                "brier": brier,
            }
        )
    native_n = len(scores)
    return {
        "calibration_n": native_n,
        "status": (
            "calibrated"
            if native_n >= minimum_native_n
            else "uncalibrated"
        ),
        "minimum_native_n": minimum_native_n,
        "mean_brier": (
            sum(item["brier"] for item in scores) / native_n
            if native_n
            else None
        ),
        "scores": scores,
        "excluded_event_classes": dict(sorted(excluded.items())),
        "rejected_events": rejected,
        "policy_independence": (
            "Only outcome_event.frozen_prediction is read; current policy "
            "priors and likelihoods are ignored."
        ),
    }


def _split_prior_events(
    prior_events: Any,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if isinstance(prior_events, dict):
        lifecycle = prior_events.get("lifecycle_events", [])
        outcomes = prior_events.get("outcomes", [])
        return list(lifecycle), list(outcomes)
    lifecycle: list[dict[str, Any]] = []
    outcomes: list[dict[str, Any]] = []
    for event in prior_events or []:
        if event.get("event_type") == "lifecycle":
            lifecycle.append(event["event"])
        elif event.get("event_type") == "outcome":
            outcomes.append(event["event"])
    return lifecycle, outcomes


def _rank_sensitivity(entries: list[dict[str, Any]]) -> dict[str, Any]:
    ranks: dict[str, dict[str, int]] = {
        entry["candidate_id"]: {} for entry in entries
    }
    for scenario in ("low", "base", "high"):
        ordered = sorted(
            entries,
            key=lambda entry: (
                -entry["priority"][scenario],
                entry["candidate_id"],
            ),
        )
        for rank, entry in enumerate(ordered, start=1):
            ranks[entry["candidate_id"]][scenario] = rank
    return {
        candidate_id: {
            "ranks": scenario_ranks,
            "rank_range": (
                max(scenario_ranks.values()) - min(scenario_ranks.values())
            ),
            "robustness_flag": (
                "stable"
                if len(set(scenario_ranks.values())) == 1
                else "sensitive"
            ),
        }
        for candidate_id, scenario_ranks in sorted(ranks.items())
    }


def run_engine(
    policy: dict[str, Any],
    immutable_candidates: list[dict[str, Any]],
    prior_events: Any,
    owner_decisions: list[dict[str, Any]],
) -> dict[str, Any]:
    """Evaluate snapshots without mutating them or authorizing execution."""

    policy = copy.deepcopy(policy)
    candidates = copy.deepcopy(immutable_candidates)
    lifecycle_events, outcomes = _split_prior_events(prior_events)
    candidate_index: dict[tuple[str, int], dict[str, Any]] = {}
    duplicate_keys: list[tuple[str, int]] = []
    for candidate in candidates:
        key = (candidate.get("candidate_id"), candidate.get("version"))
        if key in candidate_index:
            duplicate_keys.append(key)
        candidate_index[key] = candidate

    authorized_owner_roles = policy.get(
        "authorized_owner_roles", ["project_owner"]
    )
    lifecycle_problems, states = validate_lifecycle_events(
        lifecycle_events,
        candidate_index,
        owner_decisions,
        authorized_owner_roles,
    )
    lifecycle_problems += validate_recommendation_bindings(
        policy,
        candidates,
        lifecycle_events,
    )
    lifecycle_problems = sorted(set(lifecycle_problems))
    completed = _completed_dependencies(lifecycle_events)
    budgets = policy.get("portfolio_budget", {})

    summaries: list[dict[str, Any]] = []
    portfolio_entries: list[dict[str, Any]] = []
    for candidate in candidates:
        key = (candidate.get("candidate_id"), candidate.get("version"))
        validation = validate_snapshot(candidate, policy)
        gates = derive_gates(candidate, policy)
        if lifecycle_problems:
            gates = sorted(set(gates) | {"invalid_lifecycle_state"})
        if duplicate_keys:
            gates = sorted(set(gates) | {"invalid_candidate_identity_set"})
        state = states.get(key, "idea")
        dependencies = candidate.get("dependencies", [])
        dependency_ready = all(
            dependency_satisfied(dependency, completed)
            for dependency in dependencies
        )
        if not dependency_ready:
            gates = sorted(set(gates) | {"unsatisfied_dependency"})
        inactive = state in {
            "terminal",
            "superseded",
            "authorized",
            "running",
        }
        computed_admissible = (
            not gates
            and not inactive
            and state in {"validator_ready", "admissible", "recommended"}
        )
        score = None
        vector = None
        priority = None
        if not validation:
            score = score_snapshot(candidate)
            vector = cost_vector(candidate)
            denominator = normalized_cost(vector, budgets)
            priority = {
                scenario: (
                    score["eig_bits"][scenario] / denominator
                    if denominator > 0 and math.isfinite(denominator)
                    else 0.0
                )
                for scenario in ("low", "base", "high")
            }
        summary = {
            "candidate_id": candidate.get("candidate_id"),
            "version": candidate.get("version"),
            "candidate_digest": candidate.get("snapshot_digest"),
            "current_state": state,
            "computed_admissible": computed_admissible,
            "gates": gates,
            "validation_problems": validation,
            "dependencies_satisfied": dependency_ready,
            "score": score,
            "priority": priority,
        }
        summaries.append(summary)
        if computed_admissible and score is not None and vector is not None:
            portfolio_entries.append(
                {
                    "candidate_id": candidate["candidate_id"],
                    "snapshot": candidate,
                    "score": score,
                    "cost_vector": vector,
                    "priority": priority,
                }
            )

    rank_sensitivity = _rank_sensitivity(portfolio_entries)
    portfolios = {
        scenario: optimize_portfolio(
            portfolio_entries,
            policy,
            completed,
            scenario=scenario,
        )
        for scenario in ("low", "base", "high")
    }
    base_portfolio = portfolios["base"]
    recommended = (
        base_portfolio["selected_ids"]
        if base_portfolio["status"] == "compared"
        else []
    )
    admissible_ids = sorted(
        entry["candidate_id"] for entry in portfolio_entries
    )
    deferred = sorted(set(admissible_ids) - set(recommended))
    scenario_selections = {
        scenario: portfolio["selected_ids"]
        for scenario, portfolio in portfolios.items()
    }
    portfolio_robustness = (
        "stable"
        if len(
            {
                tuple(selection)
                for selection in scenario_selections.values()
            }
        )
        == 1
        else "sensitive"
    )

    decision_id_counts: dict[str, int] = {}
    for decision in owner_decisions:
        decision_id = decision.get("decision_id")
        if isinstance(decision_id, str):
            decision_id_counts[decision_id] = (
                decision_id_counts.get(decision_id, 0) + 1
            )

    latest_decisions: dict[
        tuple[str, int, str], tuple[datetime, int, str]
    ] = {}
    allowed_owner_roles = set(authorized_owner_roles)
    for decision_index, decision in enumerate(owner_decisions):
        candidate_key = (
            decision.get("candidate_id"),
            decision.get("candidate_version"),
        )
        candidate = candidate_index.get(candidate_key)
        decision_id = decision.get("decision_id")
        decided_at = decision.get("decided_at")
        if (
            candidate is None
            or not isinstance(decision_id, str)
            or decision_id_counts.get(decision_id) != 1
            or decision.get("decision_type") != "owner_authorization"
            or decision.get("owner_role") not in allowed_owner_roles
            or decision.get("status") not in {"approved", "denied", "revoked"}
            or not _is_iso_datetime(decided_at)
            or candidate.get("snapshot_digest")
            != decision.get("candidate_digest")
            or not _is_iso_datetime(candidate.get("created_at"))
        ):
            continue
        decision_time = datetime.fromisoformat(
            decided_at.replace("Z", "+00:00")
        )
        created_at = datetime.fromisoformat(
            candidate["created_at"].replace("Z", "+00:00")
        )
        if decision_time < created_at:
            continue
        key = (
            candidate["candidate_id"],
            candidate["version"],
            candidate["snapshot_digest"],
        )
        record = (decision_time, decision_index, decision["status"])
        if key not in latest_decisions or record[:2] > latest_decisions[key][:2]:
            latest_decisions[key] = record

    valid_decisions = {
        key
        for key, (_, _, status) in latest_decisions.items()
        if status == "approved"
    }
    summary_index = {
        (summary["candidate_id"], summary["version"]): summary
        for summary in summaries
    }
    for key, state in states.items():
        candidate = candidate_index[key]
        decision_key = (
            candidate["candidate_id"],
            candidate["version"],
            candidate["snapshot_digest"],
        )
        if state in {"authorized", "running"} and decision_key not in valid_decisions:
            lifecycle_problems.append(
                f"{candidate['candidate_id']}@{candidate['version']}: "
                "current authorized lifecycle state has no effective approved "
                "owner decision"
            )
    lifecycle_problems = sorted(set(lifecycle_problems))

    authorized: list[str] = []
    for candidate in candidates:
        candidate_id = candidate["candidate_id"]
        summary = summary_index[(candidate_id, candidate["version"])]
        decision_key = (
            candidate["candidate_id"],
            candidate["version"],
            candidate["snapshot_digest"],
        )
        authorization_is_current = summary["current_state"] in {
            "authorized",
            "running",
        }
        if (
            authorization_is_current
            and decision_key in valid_decisions
            and not summary["validation_problems"]
            and not summary["gates"]
            and not lifecycle_problems
        ):
            authorized.append(candidate_id)

    calibration = build_calibration(
        candidates,
        outcomes,
        minimum_native_n=int(policy.get("calibration_min_native_n", 5)),
    )
    return {
        "schema_version": "0.2",
        "engine_status": "evaluated_non_executing",
        "input_candidate_count": len(candidates),
        "duplicate_candidate_versions": [
            {"candidate_id": key[0], "version": key[1]}
            for key in duplicate_keys
        ],
        "lifecycle_problems": lifecycle_problems,
        "candidates": summaries,
        "rank_sensitivity": rank_sensitivity,
        "portfolio": {
            "base": base_portfolio,
            "scenarios": portfolios,
            "scenario_selections": scenario_selections,
            "robustness_flag": portfolio_robustness,
        },
        "admissible": admissible_ids,
        "recommended": sorted(recommended),
        "deferred": [
            {
                "candidate_id": candidate_id,
                "candidate_digest": next(
                    candidate["snapshot_digest"]
                    for candidate in candidates
                    if candidate["candidate_id"] == candidate_id
                ),
                "reason": (
                    "quality_cleared_not_selected_in_current_portfolio"
                    if base_portfolio["status"] == "compared"
                    else "portfolio_coverage_overflow"
                ),
                "review_reuse_rule": (
                    "A later cycle may reuse digest-bound clearance only while "
                    "the immutable candidate digest is unchanged."
                ),
            }
            for candidate_id in deferred
        ],
        "authorized": sorted(authorized),
        "authorization_boundary": {
            "separate_owner_decision_required": true_value(),
            "proposal_or_reviews_authorize": False,
            "engine_authorizes": False,
        },
        "terminal_candidates_release_slots": True,
        "selection_status": (
            "zero_retention_success"
            if not recommended
            else "portfolio_recommendation_available"
        ),
        "completed_prerequisites": {
            key: [
                {"version": version, "outcome": outcome}
                for version, outcome in values
            ]
            for key, values in sorted(completed.items())
        },
        "calibration": calibration,
        "route_promotions": [],
        "direct_target_executions": [],
    }


def true_value() -> bool:
    """Keep the serialized authorization assertion explicit and testable."""

    return True


__all__ = [
    "bind_snapshot",
    "build_calibration",
    "build_recommendation_binding",
    "canonical_json_bytes",
    "cost_vector",
    "dependency_satisfied",
    "derive_gates",
    "expected_information_gain",
    "normalized_cost",
    "optimize_portfolio",
    "run_engine",
    "score_snapshot",
    "sha256_json",
    "snapshot_digest",
    "validate_cost_contract",
    "validate_generation_binding",
    "validate_lane",
    "validate_lifecycle_events",
    "validate_mechanism_contract",
    "validate_owner_decisions",
    "validate_prediction_contract",
    "validate_recommendation_bindings",
    "validate_snapshot",
    "validate_validator_contract",
]
