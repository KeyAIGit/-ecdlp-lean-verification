#!/usr/bin/env python3
"""Deterministic hypothesis-generation intake for Research Engine v0.

The creative proposer is deliberately outside the trust boundary. This module
builds source-grounded research seeds, validates model- or human-authored
proposals, binds adversarial reviews to exact proposal digests, and emits draft
hypotheses. It never authorizes an experiment or promotes a route.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any

from scientific_provenance import (
    git_file_bytes,
    scientific_source_commit_allowed,
)
from research_contract_binding import scientific_contract_digests
from research_claims import load_and_build as load_research_claim_state
from research_engine_v02 import (
    MECHANISM_ASSURANCE_STATUSES,
    MECHANISM_ASSURANCE_TOPICS,
    validate_cost_contract,
    validate_mechanism_contract,
    validate_prediction_contract,
    validate_validator_contract,
)
from typed_evidence_lib import (
    POLICY_PATH as TYPED_EVIDENCE_POLICY_PATH,
    STATE_PATH as TYPED_EVIDENCE_STATE_PATH,
    load_and_build as load_typed_evidence_state,
)

ROOT = Path(__file__).resolve().parent.parent
GENERATION_POLICY_PATH = ROOT / "repo" / "HYPOTHESIS_GENERATION_V0.json"
PROPOSALS_DIR = ROOT / "experiments" / "engine" / "proposals"
REVIEWS_DIR = ROOT / "experiments" / "engine" / "proposal_reviews"

GENERATION_POLICY_FIELDS = {
    "schema_version",
    "generator_id",
    "status",
    "purpose",
    "trust_boundary",
    "limits",
    "typed_evidence_contract",
    "synthesis_rules",
    "frozen_seed_bindings",
    "lifecycle",
    "fingerprint_contract",
    "compatibility_rule",
    "quality_gate",
    "mechanism_assurance_evidence",
    "known_premises",
    "axes",
}
TYPED_EVIDENCE_CONTRACT_FIELDS = {
    "policy_path",
    "state_path",
    "seedable_statuses",
    "required_authorization",
    "decision_rule",
}
SYNTHESIS_RULE_FIELDS = {
    "id",
    "version",
    "operator",
    "axis_order",
    "required_predicates",
    "seed_identity_fields",
    "status",
}
FROZEN_SEED_BINDING_FIELDS = {
    "seed_id",
    "identity_version",
    "source_commit",
    "source_path",
    "source_sha256",
    "recorded_on",
    "status",
    "reason",
}
FINGERPRINT_CONTRACT_FIELDS = {
    "premise_version",
    "premise_limitation",
    "mechanism_version",
    "mechanism_identity_fields",
    "near_duplicate_policy",
}
TRUST_BOUNDARY_FIELDS = {
    "creative_output",
    "deterministic_engine",
    "quality_claim",
    "authorization_boundary",
}
GENERATION_LIMIT_FIELDS = {
    "max_generated_seeds",
    "max_quality_cleared_per_cycle",
    "max_toy_field_bits",
}
COMPATIBILITY_FIELDS = {
    "eligible_route_statuses",
    "require_primary_threat_model",
    "require_shared_route",
    "require_shared_compatibility_tag",
}
QUALITY_GATE_FIELDS = {
    "required_sections",
    "required_review_roles",
    "required_independent_roles",
    "hard_rejections",
    "zero_retention_allowed",
    "overflow_rule",
}
AXES_FIELDS = {
    "target_features",
    "mechanism_primitives",
    "unresolved_questions",
}
AXIS_ITEM_FIELDS = {
    "id",
    "label",
    "statement",
    "boundary",
    "route_ids",
    "threat_models",
    "compatibility_tags",
    "evidence_inputs",
    "status",
}
KNOWN_PREMISE_FIELDS = {
    "id",
    "basis",
    "disposition",
    "evidence_inputs",
}

PROPOSAL_FIELDS = {
    "schema_version",
    "proposal_id",
    "seed_id",
    "cell_id",
    "typed_evidence_digest",
    "created_on",
    "proposer_id",
    "route_id",
    "threat_model",
    "title",
    "hypothesis_statement",
    "new_premise",
    "premise_counterfactual",
    "premise_fingerprint",
    "mechanism_identity",
    "mechanism_signature",
    "mechanism_contract",
    "prediction_contract",
    "cost_contract",
    "validator_contract",
    "novelty_scope",
    "nearest_prior_art",
    "exact_mechanism",
    "non_generic_information_source",
    "null_model",
    "competing_mechanism",
    "cost_bridge",
    "falsifiable_prediction",
    "matched_baseline",
    "stop_condition",
    "outcome_matrix",
    "validator_plan",
    "toy_scope",
    "claim_boundary",
    "evidence_inputs",
    "evidence_manifest",
    "provenance",
}
PRIOR_ART_FIELDS = {
    "source_id",
    "primary",
    "reference",
    "locator",
    "overlap",
    "difference",
    "evidence_file",
}
NOVELTY_SCOPE_FIELDS = {
    "new_to_repository",
    "new_to_reviewed_corpus",
    "global_novelty",
    "rationale",
}
MECHANISM_IDENTITY_FIELDS = {
    "transformation_class",
    "information_source_class",
    "target_semantics_class",
    "recovery_class",
    "changed_cost_term",
    "precomputation_class",
    "amortization_class",
}
EVIDENCE_MANIFEST_FIELDS = {
    "path",
    "sha256",
    "relation",
    "locator",
    "source_id",
    "primary",
}
EXACT_MECHANISM_FIELDS = {
    "map",
    "domain",
    "codomain",
    "relation_semantics",
    "fixed_target_semantics",
    "exceptional_locus",
    "recovery_map",
    "implementation_identity",
}
COST_BRIDGE_FIELDS = {
    "baseline",
    "changed_term",
    "online_cost",
    "offline_cost",
    "memory_cost",
    "parallelism",
    "precomputation",
    "amortization_scope",
    "scaling_claim",
}
VALIDATOR_PLAN_FIELDS = {
    "decisive_claim",
    "raw_artifacts",
    "independent_method",
    "failure_labels",
}
TOY_SCOPE_FIELDS = {
    "curve_family",
    "max_field_bits",
    "forbidden_targets",
}
PROPOSAL_PROVENANCE_FIELDS = {
    "generation_method",
    "generator",
    "generator_family",
    "generator_version",
    "session_id",
    "context_sha256",
    "source_commit",
    "prompt_sha256",
}
OUTCOME_MATRIX_FIELDS = {
    "supported",
    "falsified",
    "bounded_negative",
    "inapplicable",
    "inconclusive",
    "resource_exhausted",
}

REVIEW_FIELDS = {
    "schema_version",
    "review_id",
    "proposal_id",
    "proposal_sha256",
    "reviewed_on",
    "reviewer_id",
    "reviewer_role",
    "source_independence",
    "reviewer_provenance",
    "verdict",
    "blocker_codes",
    "summary",
    "evidence_inputs",
}
REVIEWER_PROVENANCE_FIELDS = {
    "family",
    "version",
    "session_id",
    "context_sha256",
    "prompt_sha256",
    "blind_to_other_reviews",
}

HYPOTHESIS_HARD_REJECTIONS = {
    "threat_model_drift",
    "seed_scope_mismatch",
    "duplicate_or_reencoding",
    "duplicate_mechanism_signature",
    "semantic_reencoding_risk",
    "missing_new_premise",
    "missing_exact_mechanism",
    "missing_fixed_target_semantics",
    "missing_non_generic_information_source",
    "missing_cost_changing_bridge",
    "hidden_or_unpriced_precomputation",
    "missing_falsifiable_prediction",
    "missing_primary_source_comparison",
    "missing_primary_source_anchor",
    "missing_independent_validator_plan",
    "proxy_not_decisive",
    "novelty_scope_overclaimed",
    "targets_secp256k1_directly",
    "adversarial_review_incomplete",
    "adversarial_review_blocked",
    "review_independence_unestablished",
    "typed_evidence_mismatch",
    "target_property_violated",
    "stale_seed_snapshot",
}

PROPOSAL_ID = re.compile(r"^HGP-[A-Z0-9][A-Z0-9-]{4,80}$")
REVIEW_ID = re.compile(r"^HGR-[A-Z0-9][A-Z0-9-]{4,80}$")
SEED_ID = re.compile(r"^HGS-[A-F0-9]{12}$")
HASH_ID = re.compile(r"^[0-9a-f]{64}$")
COMMIT_ID = re.compile(r"^[0-9a-f]{40}$")
IDENTITY_TOKEN = re.compile(r"^[a-z0-9][a-z0-9._-]{2,80}$")
PLACEHOLDER = re.compile(
    r"^(?:tbd|todo|unknown|none|n/?a|not specified|pending|placeholder)[.!]?$",
    flags=re.IGNORECASE,
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_json_records(directory: Path) -> list[tuple[Path, dict[str, Any]]]:
    return [(path, load_json(path)) for path in sorted(directory.glob("*.json"))]


def sha256_json(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


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


def _substantive_text(value: Any) -> bool:
    return (
        _nonempty_text(value)
        and len(value.strip()) >= 16
        and PLACEHOLDER.fullmatch(value.strip()) is None
    )


def _unique_text_array(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and len(value) == len(set(value))
        and all(_nonempty_text(item) for item in value)
    )


def _existing_files(
    values: Any, label: str, problems: list[str], *, allow_empty: bool = False
) -> None:
    if not isinstance(values, list) or (
        not allow_empty and not values
    ) or not all(_nonempty_text(value) for value in values):
        problems.append(f"{label} must be an array of repository paths")
        return
    for relative in values:
        if not (ROOT / relative).is_file():
            problems.append(f"{label}: missing repository file {relative}")


def _valid_date(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def git_file_sha256(commit: str, relative: str) -> str | None:
    payload = git_file_bytes(commit, relative)
    return hashlib.sha256(payload).hexdigest() if payload is not None else None


def _seed_scoped_identity(seed: dict[str, Any]) -> dict[str, Any]:
    """Return the policy-declared scientific identity of a generated seed."""
    return {
        "cell_id": seed["cell_id"],
        "typed_mechanism_id": seed["typed_cell"]["mechanism_id"],
        "feature_id": seed["target_feature"]["id"],
        "mechanism_primitive_id": seed["mechanism_primitive"]["id"],
        "uncertainty_id": seed["unresolved_question"]["id"],
        "route_id": seed["route_id"],
        "threat_model": seed["threat_model"],
        "evidence_digest": seed["typed_evidence_digest"],
        "synthesis_rule_id": seed["synthesis_rule"]["id"],
        "synthesis_rule_version": seed["synthesis_rule"]["version"],
    }


def _frozen_seed_records(
    policy: dict[str, Any], problems: list[str]
) -> list[dict[str, Any]]:
    """Load and authenticate legacy seeds from protected-main snapshots."""
    bindings = policy.get("frozen_seed_bindings")
    if not isinstance(bindings, list):
        problems.append("frozen_seed_bindings must be an array")
        return []
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, binding in enumerate(bindings):
        label = f"frozen_seed_bindings[{index}]"
        if not _exact_keys(
            binding, FROZEN_SEED_BINDING_FIELDS, label, problems
        ):
            continue
        seed_id = binding.get("seed_id")
        if not isinstance(seed_id, str) or SEED_ID.fullmatch(seed_id) is None:
            problems.append(f"{label}.seed_id is invalid")
            continue
        if seed_id in seen:
            problems.append(f"{label}.seed_id is duplicated")
            continue
        seen.add(seed_id)
        if binding.get("identity_version") != "legacy-global-claim-state-v0":
            problems.append(f"{label}.identity_version is unsupported")
        if binding.get("source_path") != "data/research_engine_state.json":
            problems.append(f"{label}.source_path is not canonical")
        source_commit = binding.get("source_commit")
        if (
            not isinstance(source_commit, str)
            or COMMIT_ID.fullmatch(source_commit) is None
        ):
            problems.append(f"{label}.source_commit is invalid")
            continue
        source_sha = binding.get("source_sha256")
        if not isinstance(source_sha, str) or HASH_ID.fullmatch(source_sha) is None:
            problems.append(f"{label}.source_sha256 is invalid")
            continue
        if not _valid_date(binding.get("recorded_on")):
            problems.append(f"{label}.recorded_on must be YYYY-MM-DD")
        if binding.get("status") != "frozen_alias":
            problems.append(f"{label}.status must be frozen_alias")
        if not _substantive_text(binding.get("reason")):
            problems.append(f"{label}.reason must be substantive")
        payload = git_file_bytes(source_commit, binding["source_path"])
        if payload is None:
            problems.append(
                f"{label}: source snapshot is not reproducible from protected main"
            )
            continue
        if hashlib.sha256(payload).hexdigest() != source_sha:
            problems.append(f"{label}: source snapshot hash mismatch")
            continue
        try:
            source_state = json.loads(payload)
            generated = source_state["hypothesis_generation"]["generated_seeds"]
        except (KeyError, TypeError, json.JSONDecodeError):
            problems.append(f"{label}: source snapshot has no generated seed set")
            continue
        matches = [item for item in generated if item.get("seed_id") == seed_id]
        if len(matches) != 1:
            problems.append(f"{label}: seed is not unique in source snapshot")
            continue
        seed = matches[0]
        claim_digest = seed.get("claim_state_digest")
        if (
            not isinstance(claim_digest, str)
            or HASH_ID.fullmatch(claim_digest) is None
        ):
            problems.append(f"{label}: legacy seed claim digest is invalid")
            continue
        try:
            legacy_identity = _seed_scoped_identity(seed)
        except (KeyError, TypeError):
            problems.append(f"{label}: legacy seed identity is malformed")
            continue
        legacy_identity["claim_state_digest"] = claim_digest
        expected_digest = sha256_json(legacy_identity)
        if seed.get("deduplication_key") != expected_digest or seed_id != (
            f"HGS-{expected_digest[:12].upper()}"
        ):
            problems.append(f"{label}: legacy seed identity does not replay")
            continue
        if seed.get("authorization") != "none":
            problems.append(f"{label}: frozen seed must authorize nothing")
            continue
        records.append(seed)
    return records


def _working_tree_text_sha256(relative: Any) -> str | None:
    if not isinstance(relative, str):
        return None
    path = ROOT / relative
    if not path.is_file():
        return None
    payload = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest()


def proposal_integrity_problems(
    proposal: dict[str, Any], label: str = "proposal"
) -> list[str]:
    """Bind a materialized proposal design to its local notes and provenance.

    Synthetic regression fixtures intentionally use non-materialized
    ``planned/`` paths; those remain shape tests. Once the declared mechanism
    path exists, every locally defined digest becomes executable rather than
    decorative.
    """
    problems: list[str] = []
    mechanism = proposal.get("mechanism_contract", {}).get(
        "implementation_identity", {}
    )
    mechanism_path = mechanism.get("implementation_path")
    mechanism_digest = _working_tree_text_sha256(mechanism_path)
    if mechanism_digest is None:
        return problems
    if mechanism.get("sha256") != mechanism_digest:
        problems.append(f"{label}: mechanism design digest is stale or invalid")

    validator = proposal.get("validator_contract", {}).get("implementation", {})
    validator_digest = _working_tree_text_sha256(validator.get("path"))
    if validator_digest is None:
        problems.append(f"{label}: materialized validator design is missing")
    elif validator.get("sha256") != validator_digest:
        problems.append(f"{label}: validator design digest is stale or invalid")

    prediction = proposal.get("prediction_contract", {})
    baseline = prediction.get("matched_baseline", {})
    baseline_id = baseline.get("baseline_id")
    sentinel_prefix = "UNIMPLEMENTED-DESIGN-ONLY-"
    if isinstance(baseline_id, str) and baseline_id.startswith(sentinel_prefix):
        sentinel = (
            "UNIMPLEMENTED-DESIGN-ONLY:"
            + baseline_id.removeprefix(sentinel_prefix)
        )
        expected = hashlib.sha256(sentinel.encode("utf-8")).hexdigest()
        if baseline.get("implementation_digest") != expected:
            problems.append(
                f"{label}: unimplemented baseline sentinel digest is invalid"
            )

    manifest = proposal.get("evidence_manifest", [])
    if isinstance(manifest, list) and all(isinstance(item, dict) for item in manifest):
        records = sorted(
            (
                f"{item.get('path')}:{item.get('sha256')}"
                for item in manifest
            )
        )
        context_digest = hashlib.sha256("\n".join(records).encode("utf-8")).hexdigest()
        provenance = proposal.get("provenance", {})
        if provenance.get("context_sha256") != context_digest:
            problems.append(f"{label}: context_sha256 is stale or invalid")

    context_path = (ROOT / str(mechanism_path)).parent / "PROPOSAL_CONTEXT.md"
    if not context_path.is_file():
        problems.append(f"{label}: materialized proposal context is missing")
    else:
        context_text = context_path.read_text(encoding="utf-8")
        proposal_id = proposal.get("proposal_id")
        if f"Proposal: `{proposal_id}`" not in context_text:
            problems.append(f"{label}: proposal context id does not match")
        quoted = [
            line[2:]
            for line in context_text.splitlines()
            if line.startswith("> ")
        ]
        if not quoted:
            problems.append(f"{label}: canonical proposal prompt is missing")
        else:
            prompt_digest = hashlib.sha256(
                " ".join(quoted).encode("utf-8")
            ).hexdigest()
            if (
                proposal.get("provenance", {}).get("prompt_sha256")
                != prompt_digest
            ):
                problems.append(f"{label}: prompt_sha256 is stale or invalid")
    return problems


def normalize_premise(value: str) -> str:
    return " ".join(value.casefold().split())


def premise_fingerprint(value: str) -> str:
    return hashlib.sha256(normalize_premise(value).encode("utf-8")).hexdigest()


def premise_similarity(left: str, right: str) -> float:
    left_tokens = {
        token
        for token in re.findall(r"[a-z0-9_]+", normalize_premise(left))
        if len(token) >= 4
    }
    right_tokens = {
        token
        for token in re.findall(r"[a-z0-9_]+", normalize_premise(right))
        if len(token) >= 4
    }
    union = left_tokens | right_tokens
    return len(left_tokens & right_tokens) / len(union) if union else 0.0


def proposal_sha256(proposal: dict[str, Any]) -> str:
    return sha256_json(proposal)


def mechanism_signature(proposal: dict[str, Any]) -> str:
    """Fingerprint the declared algorithmic mechanism, not its prose title."""
    return sha256_json(
        {
            "route_id": proposal.get("route_id"),
            "threat_model": proposal.get("threat_model"),
            "mechanism_identity": proposal.get("mechanism_identity"),
        }
    )


def validate_generation_policy(
    policy: dict[str, Any],
    decisions: dict[str, Any],
    engine_policy: dict[str, Any],
    typed_evidence_state: dict[str, Any] | None = None,
) -> list[str]:
    problems: list[str] = []
    if not _exact_keys(
        policy,
        GENERATION_POLICY_FIELDS,
        "hypothesis_generation_policy",
        problems,
    ):
        return problems
    if policy.get("schema_version") != "0.1":
        problems.append("hypothesis generation schema_version must be 0.1")
    if policy.get("status") != "active":
        problems.append("hypothesis generation policy must be active")
    for field in ("generator_id", "purpose"):
        if not _nonempty_text(policy.get(field)):
            problems.append(f"hypothesis generation {field} must be nonempty")

    trust = policy.get("trust_boundary")
    if _exact_keys(trust, TRUST_BOUNDARY_FIELDS, "trust_boundary", problems):
        for field, value in trust.items():
            if not _substantive_text(value):
                problems.append(f"trust_boundary.{field} must be substantive")
        if "never" not in trust.get("authorization_boundary", "").casefold():
            problems.append(
                "trust_boundary.authorization_boundary must explicitly say never"
            )

    limits = policy.get("limits")
    if _exact_keys(limits, GENERATION_LIMIT_FIELDS, "limits", problems):
        for field, value in limits.items():
            if (
                not isinstance(value, int)
                or isinstance(value, bool)
                or value <= 0
            ):
                problems.append(f"limits.{field} must be a positive integer")
        if limits.get("max_quality_cleared_per_cycle", 99) > 3:
            problems.append("at most three generated proposals may clear per cycle")
        if limits.get("max_toy_field_bits", 99) > 24:
            problems.append("hypothesis generation toy scope may not exceed 24 bits")

    assurance_records = policy.get("mechanism_assurance_evidence")
    if not isinstance(assurance_records, list):
        problems.append("mechanism_assurance_evidence must be an array")
        assurance_records = []
    assurance_ids: list[str] = []
    for index, record in enumerate(assurance_records):
        label = f"mechanism_assurance_evidence[{index}]"
        if not _exact_keys(
            record,
            {"evidence_id", "topic", "assurance", "claim_sha256"},
            label,
            problems,
        ):
            continue
        evidence_id = record.get("evidence_id")
        if not _nonempty_text(evidence_id):
            problems.append(f"{label}.evidence_id must be nonempty")
        else:
            assurance_ids.append(evidence_id)
        if record.get("topic") not in MECHANISM_ASSURANCE_TOPICS:
            problems.append(f"{label}.topic is invalid")
        if record.get("assurance") not in (
            MECHANISM_ASSURANCE_STATUSES - {"specified_unproved"}
        ):
            problems.append(f"{label}.assurance is not evidence-bearing")
        claim_sha = record.get("claim_sha256")
        if not isinstance(claim_sha, str) or HASH_ID.fullmatch(claim_sha) is None:
            problems.append(f"{label}.claim_sha256 is invalid")
    if len(assurance_ids) != len(set(assurance_ids)):
        problems.append("mechanism assurance evidence ids must be unique")

    typed_contract = policy.get("typed_evidence_contract")
    if _exact_keys(
        typed_contract,
        TYPED_EVIDENCE_CONTRACT_FIELDS,
        "typed_evidence_contract",
        problems,
    ):
        expected_policy_path = TYPED_EVIDENCE_POLICY_PATH.relative_to(
            ROOT
        ).as_posix()
        expected_state_path = TYPED_EVIDENCE_STATE_PATH.relative_to(
            ROOT
        ).as_posix()
        if typed_contract.get("policy_path") != expected_policy_path:
            problems.append("typed evidence policy path is not canonical")
        if typed_contract.get("state_path") != expected_state_path:
            problems.append("typed evidence state path is not canonical")
        if set(typed_contract.get("seedable_statuses", [])) != {
            "open",
            "property_resolution_required",
        }:
            problems.append("typed evidence seedable statuses are not canonical")
        if typed_contract.get("required_authorization") != "none":
            problems.append("typed evidence cannot authorize generation work")
        if not _substantive_text(typed_contract.get("decision_rule")):
            problems.append("typed evidence decision rule must be substantive")

    synthesis_rules = policy.get("synthesis_rules")
    if not isinstance(synthesis_rules, list) or not synthesis_rules:
        problems.append("synthesis_rules must be a nonempty array")
        synthesis_rules = []
    synthesis_ids: list[str] = []
    for index, rule in enumerate(synthesis_rules):
        label = f"synthesis_rules[{index}]"
        if not _exact_keys(rule, SYNTHESIS_RULE_FIELDS, label, problems):
            continue
        synthesis_ids.append(rule.get("id"))
        if rule.get("version") != "1.0":
            problems.append(f"{label}.version must be 1.0")
        if rule.get("operator") != "typed_open_cell":
            problems.append(f"{label}.operator is unsupported")
        if rule.get("axis_order") != [
            "target_features",
            "mechanism_primitives",
            "unresolved_questions",
        ]:
            problems.append(f"{label}.axis_order is not canonical")
        if set(rule.get("required_predicates", [])) != {
            "typed_cell_seed_eligible",
            "typed_cell_authorization_none",
            "primary_threat_model",
            "eligible_route_status",
            "resolved_axis_bindings",
        }:
            problems.append(f"{label}.required_predicates is incomplete")
        if rule.get("seed_identity_fields") != [
            "cell_id",
            "typed_mechanism_id",
            "feature_id",
            "mechanism_primitive_id",
            "uncertainty_id",
            "route_id",
            "threat_model",
            "evidence_digest",
            "synthesis_rule_id",
            "synthesis_rule_version",
        ]:
            problems.append(f"{label}.seed_identity_fields is not canonical")
        if rule.get("status") not in {"active", "retired"}:
            problems.append(f"{label}.status is invalid")
    if len(synthesis_ids) != len(set(synthesis_ids)):
        problems.append("synthesis rule ids must be unique")
    if sum(
        rule.get("status") == "active"
        for rule in synthesis_rules
        if isinstance(rule, dict)
    ) != 1:
        problems.append("exactly one v0.1 synthesis rule must be active")

    _frozen_seed_records(policy, problems)

    lifecycle = policy.get("lifecycle")
    if lifecycle != [
        "evidence_snapshot",
        "typed_evidence_cell",
        "generated_seed",
        "untrusted_proposal",
        "blind_adversarial_review",
        "quality_compilation",
        "non_executable_hypothesis_draft",
        "existing_candidate_gate",
    ]:
        problems.append("hypothesis generation lifecycle is not canonical")

    fingerprint_contract = policy.get("fingerprint_contract")
    if _exact_keys(
        fingerprint_contract,
        FINGERPRINT_CONTRACT_FIELDS,
        "fingerprint_contract",
        problems,
    ):
        if fingerprint_contract.get("premise_version") != "lexical-v1":
            problems.append("premise fingerprint version must be lexical-v1")
        if not _substantive_text(
            fingerprint_contract.get("premise_limitation")
        ):
            problems.append("premise fingerprint limitation must be substantive")
        if fingerprint_contract.get("mechanism_version") != (
            "structured-identity-v1"
        ):
            problems.append(
                "mechanism fingerprint version must be structured-identity-v1"
            )
        if fingerprint_contract.get("mechanism_identity_fields") != sorted(
            MECHANISM_IDENTITY_FIELDS
        ):
            problems.append("mechanism identity field list is not canonical")
        if not _substantive_text(
            fingerprint_contract.get("near_duplicate_policy")
        ):
            problems.append("near-duplicate policy must be substantive")

    compatibility = policy.get("compatibility_rule")
    if _exact_keys(
        compatibility, COMPATIBILITY_FIELDS, "compatibility_rule", problems
    ):
        if not _unique_text_array(
            compatibility.get("eligible_route_statuses")
        ):
            problems.append(
                "compatibility_rule.eligible_route_statuses must be unique"
            )
        for field in (
            "require_primary_threat_model",
            "require_shared_route",
            "require_shared_compatibility_tag",
        ):
            if compatibility.get(field) is not True:
                problems.append(f"compatibility_rule.{field} must remain true")

    gate = policy.get("quality_gate")
    if _exact_keys(gate, QUALITY_GATE_FIELDS, "quality_gate", problems):
        required_sections = gate.get("required_sections")
        if not _unique_text_array(required_sections):
            problems.append("quality_gate.required_sections must be unique")
        elif set(required_sections) != {
            "new_premise",
            "premise_counterfactual",
            "mechanism_signature",
            "mechanism_contract",
            "prediction_contract",
            "cost_contract",
            "validator_contract",
            "novelty_scope",
            "nearest_prior_art",
            "exact_mechanism",
            "fixed_target_semantics",
            "non_generic_information_source",
            "null_model",
            "competing_mechanism",
            "cost_bridge",
            "falsifiable_prediction",
            "matched_baseline",
            "stop_condition",
            "outcome_matrix",
            "independent_validator_plan",
            "claim_boundary",
            "evidence_manifest",
        }:
            problems.append("quality_gate.required_sections is incomplete")
        roles = gate.get("required_review_roles")
        independent_roles = gate.get("required_independent_roles")
        if not _unique_text_array(roles):
            problems.append("quality_gate.required_review_roles must be unique")
            roles = []
        if not _unique_text_array(independent_roles):
            problems.append(
                "quality_gate.required_independent_roles must be unique"
            )
            independent_roles = []
        if not set(independent_roles) <= set(roles):
            problems.append("independent review roles must be required roles")
        if set(gate.get("hard_rejections", [])) != HYPOTHESIS_HARD_REJECTIONS:
            problems.append("quality_gate must declare every hard rejection")
        if gate.get("zero_retention_allowed") is not True:
            problems.append("quality gate must permit zero retained proposals")
        if not _substantive_text(gate.get("overflow_rule")):
            problems.append("quality_gate.overflow_rule must be substantive")

    route_ids = {route["id"] for route in decisions.get("routes", [])}
    threat_ids = {item["id"] for item in decisions.get("threat_models", [])}
    primary_models = [
        item["id"]
        for item in decisions.get("threat_models", [])
        if item.get("primary") is True
    ]
    primary_model = (
        primary_models[0] if len(primary_models) == 1 else None
    )
    if primary_model != engine_policy.get("target_contract", {}).get(
        "primary_threat_model"
    ):
        problems.append(
            "hypothesis generator and Research Engine primary threat model differ"
        )

    axes = policy.get("axes")
    all_axis_ids: list[str] = []
    if _exact_keys(axes, AXES_FIELDS, "axes", problems):
        for axis_name in sorted(AXES_FIELDS):
            items = axes.get(axis_name)
            if not isinstance(items, list) or not items:
                problems.append(f"axes.{axis_name} must be a nonempty array")
                continue
            for index, item in enumerate(items):
                label = f"axes.{axis_name}[{index}]"
                if not _exact_keys(item, AXIS_ITEM_FIELDS, label, problems):
                    continue
                item_id = item.get("id")
                if not _nonempty_text(item_id):
                    problems.append(f"{label}.id must be nonempty")
                else:
                    all_axis_ids.append(item_id)
                for field in ("label", "statement", "boundary"):
                    if not _substantive_text(item.get(field)):
                        problems.append(f"{label}.{field} must be substantive")
                if item.get("status") not in {"active", "retired"}:
                    problems.append(f"{label}.status is invalid")
                for field, allowed in (
                    ("route_ids", route_ids),
                    ("threat_models", threat_ids),
                ):
                    values = item.get(field)
                    if not _unique_text_array(values):
                        problems.append(f"{label}.{field} must be unique")
                    elif not set(values) <= allowed:
                        problems.append(f"{label}.{field} contains unknown ids")
                if not _unique_text_array(item.get("compatibility_tags")):
                    problems.append(
                        f"{label}.compatibility_tags must be unique"
                    )
                _existing_files(
                    item.get("evidence_inputs"),
                    f"{label}.evidence_inputs",
                    problems,
                )
    if len(all_axis_ids) != len(set(all_axis_ids)):
        problems.append("hypothesis-generation axis ids must be globally unique")

    known_premises = policy.get("known_premises")
    if not isinstance(known_premises, list) or not known_premises:
        problems.append("known_premises must be a nonempty array")
        known_premises = []
    known_ids: list[str] = []
    known_fingerprints: list[str] = []
    for index, item in enumerate(known_premises):
        label = f"known_premises[{index}]"
        if not _exact_keys(item, KNOWN_PREMISE_FIELDS, label, problems):
            continue
        known_ids.append(item.get("id"))
        if not _substantive_text(item.get("basis")):
            problems.append(f"{label}.basis must be substantive")
        else:
            known_fingerprints.append(premise_fingerprint(item["basis"]))
        if item.get("disposition") not in {
            "closed",
            "retained_baseline",
            "superseded",
        }:
            problems.append(f"{label}.disposition is invalid")
        _existing_files(
            item.get("evidence_inputs"),
            f"{label}.evidence_inputs",
            problems,
        )
    if len(known_ids) != len(set(known_ids)):
        problems.append("known premise ids must be unique")
    if len(known_fingerprints) != len(set(known_fingerprints)):
        problems.append("known premise fingerprints must be unique")

    if typed_evidence_state is not None:
        cells = typed_evidence_state.get("cells")
        if not isinstance(cells, list):
            problems.append("typed evidence state cells must be an array")
            cells = []
        axis_index = {
            item["id"]: item
            for items in policy.get("axes", {}).values()
            if isinstance(items, list)
            for item in items
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
        route_index = {
            route["id"]: route
            for route in decisions.get("routes", [])
            if isinstance(route, dict) and isinstance(route.get("id"), str)
        }
        seedable_statuses = set(
            policy.get("typed_evidence_contract", {}).get(
                "seedable_statuses", []
            )
        )
        for index, cell in enumerate(cells):
            label = f"typed_evidence.cells[{index}]"
            if not isinstance(cell, dict):
                problems.append(f"{label} must be an object")
                continue
            seed_eligible = cell.get("seed_eligible") is True
            if seed_eligible and cell.get("status") not in seedable_statuses:
                problems.append(f"{label} seed eligibility conflicts with status")
            if seed_eligible and cell.get("authorization") != "none":
                problems.append(f"{label} seed eligibility carries authorization")
            if seed_eligible and any(
                result.get("verdict") == "violated"
                for result in cell.get("requirement_results", [])
                if isinstance(result, dict)
            ):
                problems.append(f"{label} violated target property reached synthesis")
            if not seed_eligible:
                continue
            route = route_index.get(cell.get("route_id"))
            if route is None:
                problems.append(f"{label}.route_id does not resolve")
            elif route.get("status") not in set(
                policy.get("compatibility_rule", {}).get(
                    "eligible_route_statuses", []
                )
            ):
                problems.append(f"{label} route is not eligible for generation")
            if cell.get("threat_model") != primary_model:
                problems.append(f"{label} differs from the primary threat model")
            digest = cell.get("evidence_digest")
            if not isinstance(digest, str) or HASH_ID.fullmatch(digest) is None:
                problems.append(f"{label}.evidence_digest is invalid")
            seed_axes = cell.get("seed_axes")
            if not isinstance(seed_axes, dict):
                problems.append(f"{label}.seed_axes must be an object")
                continue
            bound_axes = [
                axis_index.get(seed_axes.get("target_feature_id")),
                axis_index.get(seed_axes.get("mechanism_primitive_id")),
                axis_index.get(seed_axes.get("uncertainty_id")),
            ]
            if any(item is None for item in bound_axes):
                problems.append(f"{label}.seed_axes do not resolve")
                continue
            for axis in bound_axes:
                if axis.get("status") != "active":
                    problems.append(f"{label} binds a retired generation axis")
                if cell.get("route_id") not in axis.get("route_ids", []):
                    problems.append(f"{label} axis binding changes route")
                if primary_model not in axis.get("threat_models", []):
                    problems.append(f"{label} axis binding changes threat model")
            common_tags = set(bound_axes[0].get("compatibility_tags", []))
            for axis in bound_axes[1:]:
                common_tags &= set(axis.get("compatibility_tags", []))
            if not common_tags:
                problems.append(f"{label} axis bindings lack a common tag")
    return problems


def generate_seeds(
    policy: dict[str, Any],
    decisions: dict[str, Any],
    engine_policy: dict[str, Any],
    typed_evidence_state: dict[str, Any] | None = None,
    claim_state: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if typed_evidence_state is None:
        typed_problems, typed_evidence_state = load_typed_evidence_state()
        if typed_problems:
            return []
    if claim_state is None:
        claim_problems, claim_state = load_research_claim_state()
        if claim_problems:
            return []
    claim_state_digest = sha256_json(claim_state)
    primary = engine_policy["target_contract"]["primary_threat_model"]
    route_index = {route["id"]: route for route in decisions["routes"]}
    synthesis_rule = next(
        rule
        for rule in policy["synthesis_rules"]
        if rule["status"] == "active"
    )
    eligible_statuses = set(
        policy["compatibility_rule"]["eligible_route_statuses"]
    )
    axes = policy["axes"]
    feature_index = {
        item["id"]: item for item in axes["target_features"]
    }
    mechanism_index = {
        item["id"]: item for item in axes["mechanism_primitives"]
    }
    uncertainty_index = {
        item["id"]: item for item in axes["unresolved_questions"]
    }
    seedable_statuses = set(
        policy["typed_evidence_contract"]["seedable_statuses"]
    )
    seeds: list[dict[str, Any]] = []
    for cell in sorted(
        typed_evidence_state.get("cells", []),
        key=lambda item: item.get("cell_id", ""),
    ):
        if (
            cell.get("seed_eligible") is not True
            or cell.get("status") not in seedable_statuses
            or cell.get("authorization") != "none"
            or cell.get("threat_model") != primary
            or any(
                result.get("verdict") == "violated"
                for result in cell.get("requirement_results", [])
                if isinstance(result, dict)
            )
        ):
            continue
        route_id = cell.get("route_id")
        route = route_index.get(route_id)
        if route is None or route.get("status") not in eligible_statuses:
            continue
        seed_axes = cell.get("seed_axes", {})
        feature = feature_index.get(seed_axes.get("target_feature_id"))
        mechanism = mechanism_index.get(
            seed_axes.get("mechanism_primitive_id")
        )
        uncertainty = uncertainty_index.get(seed_axes.get("uncertainty_id"))
        if any(
            item is None for item in (feature, mechanism, uncertainty)
        ):
            continue
        bound_axes = [feature, mechanism, uncertainty]
        if any(item.get("status") != "active" for item in bound_axes):
            continue
        if any(route_id not in item.get("route_ids", []) for item in bound_axes):
            continue
        if any(primary not in item.get("threat_models", []) for item in bound_axes):
            continue
        common_tags = set(feature["compatibility_tags"])
        common_tags &= set(mechanism["compatibility_tags"])
        common_tags &= set(uncertainty["compatibility_tags"])
        if not common_tags:
            continue
        identity_values = {
            "cell_id": cell["cell_id"],
            "typed_mechanism_id": cell["mechanism_id"],
            "feature_id": feature["id"],
            "mechanism_primitive_id": mechanism["id"],
            "uncertainty_id": uncertainty["id"],
            "route_id": route_id,
            "threat_model": primary,
            "evidence_digest": cell["evidence_digest"],
            "synthesis_rule_id": synthesis_rule["id"],
            "synthesis_rule_version": synthesis_rule["version"],
        }
        identity = {
            field: identity_values[field]
            for field in synthesis_rule["seed_identity_fields"]
        }
        seed_id = f"HGS-{sha256_json(identity)[:12].upper()}"
        evidence_inputs = sorted(
            set(feature["evidence_inputs"])
            | set(mechanism["evidence_inputs"])
            | set(uncertainty["evidence_inputs"])
        )
        intake_mode = cell["intake_mode"]
        if intake_mode == "property_resolution":
            status = "property_resolution_required"
            research_question = (
                "Can this target-property cell be decided without an ECDLP run: "
                f"{cell['scope']} The answer must instantiate or refute the "
                "typed construction and price every named precomputation term."
            )
            instruction = (
                "Return a provenance-bound arithmetic construction, a scoped "
                "no-instance result, or the smallest exact blocker. Do not return "
                "an attack claim or experiment; unresolved conditions remain unknown."
            )
        elif intake_mode == "desk_cost_bridge":
            status = "desk_cost_bridge_required"
            research_question = (
                f"Can an exact desk derivation price {cell['changed_quantity']} "
                "against the declared baseline before any solver run?"
            )
            instruction = (
                "Return an exact symbolic size and cost bridge or a scoped "
                "blocker. Do not request compute while the complete desk "
                "bridge is unresolved."
            )
        else:
            status = "proposal_required"
            research_question = (
                f"Can {mechanism['label']} use {feature['label']} to resolve "
                f"{uncertainty['label']} while satisfying the typed cell "
                "requirements and changing the named audited cost quantity?"
            )
            instruction = (
                "Return no proposal unless a genuinely new premise, exact "
                "mechanism, recovery map, and cost-changing bridge can be "
                "stated. A renamed representation or finite batching "
                "observation fails."
            )
        route_source_ids = sorted(
            set(route.get("source_ids", []))
            | {
                source_id
                for source_id in cell.get("source_ids", [])
                if not source_id.startswith("repo:")
            }
        )
        seeds.append(
            {
                "seed_id": seed_id,
                "cell_id": cell["cell_id"],
                "typed_evidence_digest": cell["evidence_digest"],
                "claim_state_digest": claim_state_digest,
                "route_id": route_id,
                "route_source_ids": route_source_ids,
                "threat_model": primary,
                "status": status,
                "authorization": "none",
                "synthesis_rule": {
                    "id": synthesis_rule["id"],
                    "version": synthesis_rule["version"],
                    "operator": synthesis_rule["operator"],
                },
                "typed_cell": {
                    "mechanism_id": cell["mechanism_id"],
                    "status": cell["status"],
                    "intake_mode": intake_mode,
                    "construction": cell["construction"],
                    "relation_action": cell["relation_action"],
                    "changed_quantity": cell["changed_quantity"],
                    "cost_quantity": cell["cost_quantity"],
                    "requirement_results": cell["requirement_results"],
                    "source_claim_ids": cell["source_claim_ids"],
                    "boundary": cell["boundary"],
                },
                "target_feature": {
                    "id": feature["id"],
                    "statement": feature["statement"],
                    "boundary": feature["boundary"],
                },
                "mechanism_primitive": {
                    "id": mechanism["id"],
                    "statement": mechanism["statement"],
                    "boundary": mechanism["boundary"],
                },
                "unresolved_question": {
                    "id": uncertainty["id"],
                    "statement": uncertainty["statement"],
                    "boundary": uncertainty["boundary"],
                },
                "shared_compatibility_tags": sorted(common_tags),
                "research_question": research_question,
                "evidence_inputs": evidence_inputs,
                "deduplication_key": sha256_json(identity),
                "proposal_packet": {
                    "required_sections": policy["quality_gate"][
                        "required_sections"
                    ],
                    "required_review_roles": policy["quality_gate"][
                        "required_review_roles"
                    ],
                    "hard_rejections": policy["quality_gate"][
                        "hard_rejections"
                    ],
                    "instruction": instruction,
                },
            }
        )
    return sorted(seeds, key=lambda item: (item["cell_id"], item["seed_id"]))


def _proposal_blockers(
    proposal: dict[str, Any],
    seed: dict[str, Any],
    policy: dict[str, Any],
    duplicate_fingerprints: set[str],
    duplicate_mechanism_signatures: set[str],
) -> set[str]:
    blockers: set[str] = set()
    if seed.get("_seed_resolution") == "frozen_historical_only":
        blockers.add("stale_seed_snapshot")
    primary = seed["threat_model"]
    if proposal.get("threat_model") != primary:
        blockers.add("threat_model_drift")
    if proposal.get("route_id") != seed["route_id"]:
        blockers.add("seed_scope_mismatch")
    if (
        proposal.get("cell_id") != seed["cell_id"]
        or proposal.get("typed_evidence_digest")
        != seed["typed_evidence_digest"]
    ):
        blockers.add("typed_evidence_mismatch")
    if (
        seed.get("typed_cell", {}).get("status")
        not in {"open", "property_resolution_required"}
        or any(
            result.get("verdict") == "violated"
            for result in seed.get("typed_cell", {}).get(
                "requirement_results", []
            )
            if isinstance(result, dict)
        )
    ):
        blockers.add("target_property_violated")

    new_premise = proposal.get("new_premise")
    if not _substantive_text(new_premise) or not _substantive_text(
        proposal.get("premise_counterfactual")
    ):
        blockers.add("missing_new_premise")
    fingerprint = proposal.get("premise_fingerprint")
    if fingerprint in duplicate_fingerprints:
        blockers.add("duplicate_or_reencoding")
    if proposal.get("mechanism_signature") in duplicate_mechanism_signatures:
        blockers.add("duplicate_mechanism_signature")
    novelty = proposal.get("novelty_scope", {})
    if (
        not isinstance(novelty, dict)
        or novelty.get("new_to_repository") is not True
        or novelty.get("new_to_reviewed_corpus") is not True
        or novelty.get("global_novelty") != "unverified"
        or not _substantive_text(novelty.get("rationale"))
    ):
        blockers.add("novelty_scope_overclaimed")

    mechanism = proposal.get("exact_mechanism", {})
    mechanism_identity = proposal.get("mechanism_identity", {})
    if (
        not isinstance(mechanism_identity, dict)
        or any(
            not _nonempty_text(mechanism_identity.get(field))
            for field in MECHANISM_IDENTITY_FIELDS
        )
        or not isinstance(mechanism, dict)
        or any(
        not _substantive_text(mechanism.get(field))
        for field in EXACT_MECHANISM_FIELDS - {"fixed_target_semantics"}
        )
    ):
        blockers.add("missing_exact_mechanism")
    if not _substantive_text(mechanism.get("fixed_target_semantics")):
        blockers.add("missing_fixed_target_semantics")
    if not _substantive_text(proposal.get("non_generic_information_source")):
        blockers.add("missing_non_generic_information_source")
    structured_mechanism = proposal.get("mechanism_contract")
    if validate_mechanism_contract(
        structured_mechanism,
        require_assured=True,
        evidence_registry=policy.get("mechanism_assurance_evidence", []),
    ):
        blockers.add("missing_exact_mechanism")

    cost = proposal.get("cost_bridge", {})
    if not isinstance(cost, dict) or any(
        not _substantive_text(cost.get(field))
        for field in COST_BRIDGE_FIELDS - {"precomputation"}
    ):
        blockers.add("missing_cost_changing_bridge")
    if not _substantive_text(cost.get("precomputation")):
        blockers.add("hidden_or_unpriced_precomputation")
    structured_cost = proposal.get("cost_contract")
    if validate_cost_contract(structured_cost):
        blockers.add("missing_cost_changing_bridge")
    elif isinstance(structured_cost, dict):
        preprocessing = structured_cost.get("preprocessing", {})
        if (
            not isinstance(preprocessing, dict)
            or preprocessing.get("included_in_totals") is not True
        ):
            blockers.add("hidden_or_unpriced_precomputation")
        amortization = structured_cost.get("amortization", {})
        if (
            not isinstance(amortization, dict)
            or amortization.get("class") != "none_single_target"
            or amortization.get("target_count") != 1
            or amortization.get("per_target_cost_included") is not True
        ):
            blockers.add("threat_model_drift")

    if not _substantive_text(proposal.get("falsifiable_prediction")):
        blockers.add("missing_falsifiable_prediction")
    structured_prediction = proposal.get("prediction_contract")
    if validate_prediction_contract(structured_prediction):
        blockers.add("missing_falsifiable_prediction")
    if not _substantive_text(proposal.get("null_model")) or not _substantive_text(
        proposal.get("competing_mechanism")
    ):
        blockers.add("proxy_not_decisive")
    prior_art = proposal.get("nearest_prior_art")
    if not isinstance(prior_art, list) or not prior_art:
        blockers.add("missing_primary_source_comparison")
    else:
        primary_anchor = False
        for item in prior_art:
            if not isinstance(item, dict) or any(
                not _substantive_text(item.get(field))
                for field in PRIOR_ART_FIELDS
                - {"evidence_file", "primary", "source_id"}
            ):
                blockers.add("missing_primary_source_comparison")
                break
            if not _nonempty_text(item.get("source_id")):
                blockers.add("missing_primary_source_anchor")
            primary_anchor = primary_anchor or item.get("primary") is True
        if not primary_anchor:
            blockers.add("missing_primary_source_anchor")
    validator = proposal.get("validator_plan", {})
    if not isinstance(validator, dict) or any(
        not _substantive_text(validator.get(field))
        for field in VALIDATOR_PLAN_FIELDS
    ):
        blockers.add("missing_independent_validator_plan")
    if validate_validator_contract(
        proposal.get("validator_contract"),
        require_ready=False,
    ):
        blockers.add("missing_independent_validator_plan")
    outcome_matrix = proposal.get("outcome_matrix", {})
    if not isinstance(outcome_matrix, dict) or any(
        not _substantive_text(outcome_matrix.get(field))
        for field in OUTCOME_MATRIX_FIELDS
    ):
        blockers.add("missing_falsifiable_prediction")
    if not _substantive_text(proposal.get("claim_boundary")):
        blockers.add("novelty_scope_overclaimed")
    evidence_manifest = proposal.get("evidence_manifest")
    if (
        not isinstance(evidence_manifest, list)
        or not evidence_manifest
        or not any(
            isinstance(item, dict) and item.get("primary") is True
            for item in evidence_manifest
        )
    ):
        blockers.add("missing_primary_source_anchor")

    toy_scope = proposal.get("toy_scope", {})
    forbidden = toy_scope.get("forbidden_targets", [])
    if (
        "secp256k1" not in forbidden
        or "secp256k1" in str(toy_scope.get("curve_family", "")).casefold()
        or toy_scope.get("max_field_bits", 10**9)
        > policy["limits"]["max_toy_field_bits"]
    ):
        blockers.add("targets_secp256k1_directly")
    if isinstance(structured_prediction, dict):
        tested_sizes = structured_prediction.get("tested_sizes", [])
        if (
            not isinstance(tested_sizes, list)
            or any(
                not isinstance(size, int)
                or isinstance(size, bool)
                or size > policy["limits"]["max_toy_field_bits"]
                or size > toy_scope.get("max_field_bits", -1)
                for size in tested_sizes
            )
        ):
            blockers.add("targets_secp256k1_directly")
    return blockers


def _resolved_seed_index(
    seeds: list[dict[str, Any]], policy: dict[str, Any]
) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    """Resolve current IDs and authenticated legacy aliases.

    A frozen alias inherits current scientific state only when every scoped
    identity field still matches. Otherwise it remains readable as historical
    provenance but is forced behind ``stale_seed_snapshot``.
    """
    seed_index: dict[str, dict[str, Any]] = {}
    resolutions: dict[str, str] = {}
    current_by_scoped_digest: dict[str, dict[str, Any]] = {}
    for seed in seeds:
        current = dict(seed)
        current["_seed_resolution"] = "current_scoped_identity"
        seed_index[seed["seed_id"]] = current
        resolutions[seed["seed_id"]] = "current_scoped_identity"
        current_by_scoped_digest[sha256_json(_seed_scoped_identity(seed))] = seed

    frozen_problems: list[str] = []
    for frozen in _frozen_seed_records(policy, frozen_problems):
        scoped_digest = sha256_json(_seed_scoped_identity(frozen))
        current = current_by_scoped_digest.get(scoped_digest)
        if current is None:
            resolved = dict(frozen)
            resolution = "frozen_historical_only"
        else:
            resolved = dict(current)
            resolution = "frozen_alias_current_scoped_identity"
        resolved["seed_id"] = frozen["seed_id"]
        resolved["_seed_resolution"] = resolution
        seed_index[frozen["seed_id"]] = resolved
        resolutions[frozen["seed_id"]] = resolution
    return seed_index, resolutions


def validate_proposals(
    records: list[tuple[Path, dict[str, Any]]],
    seeds: list[dict[str, Any]],
    policy: dict[str, Any],
) -> tuple[list[str], dict[str, set[str]], dict[str, str]]:
    problems: list[str] = []
    blockers_by_proposal: dict[str, set[str]] = {}
    seed_resolution_by_proposal: dict[str, str] = {}
    seed_index, seed_resolutions = _resolved_seed_index(seeds, policy)
    known_fingerprints = {
        premise_fingerprint(item["basis"])
        for item in policy["known_premises"]
    }
    proposal_ids: list[str] = []
    fingerprint_counts = Counter(
        proposal.get("premise_fingerprint")
        for _, proposal in records
        if isinstance(proposal, dict)
        and isinstance(proposal.get("premise_fingerprint"), str)
    )
    mechanism_signature_counts = Counter(
        proposal.get("mechanism_signature")
        for _, proposal in records
        if isinstance(proposal, dict)
        and isinstance(proposal.get("mechanism_signature"), str)
    )
    near_duplicate_ids: set[str] = set()
    comparable = [
        proposal
        for _, proposal in records
        if isinstance(proposal, dict)
        and isinstance(proposal.get("proposal_id"), str)
        and isinstance(proposal.get("new_premise"), str)
    ]
    for left_index, left in enumerate(comparable):
        for right in comparable[left_index + 1 :]:
            if left.get("route_id") != right.get("route_id"):
                continue
            if premise_similarity(
                left["new_premise"], right["new_premise"]
            ) >= 0.85:
                near_duplicate_ids.update(
                    {left["proposal_id"], right["proposal_id"]}
                )
    for path, proposal in records:
        label = path.relative_to(ROOT).as_posix()
        if not _exact_keys(proposal, PROPOSAL_FIELDS, label, problems):
            continue
        proposal_id = proposal.get("proposal_id")
        proposal_ids.append(proposal_id)
        if not isinstance(proposal_id, str) or PROPOSAL_ID.fullmatch(
            proposal_id
        ) is None:
            problems.append(f"{label}: invalid proposal_id")
            continue
        if proposal.get("schema_version") != "0.1":
            problems.append(f"{label}: schema_version must be 0.1")
        if not _valid_date(proposal.get("created_on")):
            problems.append(f"{label}: created_on must be YYYY-MM-DD")
        if not _nonempty_text(proposal.get("proposer_id")):
            problems.append(f"{label}: proposer_id must be nonempty")
        for field in (
            "title",
            "hypothesis_statement",
            "new_premise",
            "premise_counterfactual",
            "non_generic_information_source",
            "null_model",
            "competing_mechanism",
            "falsifiable_prediction",
            "matched_baseline",
            "stop_condition",
            "claim_boundary",
        ):
            if not isinstance(proposal.get(field), str):
                problems.append(f"{label}.{field} must be text")

        seed = seed_index.get(proposal.get("seed_id"))
        if seed is None:
            problems.append(f"{label}: seed_id does not resolve")
            continue
        seed_resolution_by_proposal[proposal_id] = seed_resolutions[
            proposal["seed_id"]
        ]
        if not _nonempty_text(proposal.get("cell_id")):
            problems.append(f"{label}: cell_id must be nonempty")
        typed_digest = proposal.get("typed_evidence_digest")
        if (
            not isinstance(typed_digest, str)
            or HASH_ID.fullmatch(typed_digest) is None
        ):
            problems.append(
                f"{label}: typed_evidence_digest must be lowercase 64-hex"
            )
        expected_fingerprint = (
            premise_fingerprint(proposal["new_premise"])
            if isinstance(proposal.get("new_premise"), str)
            else None
        )
        if proposal.get("premise_fingerprint") != expected_fingerprint:
            problems.append(f"{label}: premise_fingerprint is stale or invalid")
        expected_mechanism_signature = mechanism_signature(proposal)
        if proposal.get("mechanism_signature") != expected_mechanism_signature:
            problems.append(f"{label}: mechanism_signature is stale or invalid")
        mechanism_identity = proposal.get("mechanism_identity")
        if _exact_keys(
            mechanism_identity,
            MECHANISM_IDENTITY_FIELDS,
            f"{label}.mechanism_identity",
            problems,
        ):
            for field, value in mechanism_identity.items():
                if not isinstance(value, str) or IDENTITY_TOKEN.fullmatch(
                    value
                ) is None:
                    problems.append(
                        f"{label}.mechanism_identity.{field} is invalid"
                    )
        novelty = proposal.get("novelty_scope")
        if _exact_keys(
            novelty,
            NOVELTY_SCOPE_FIELDS,
            f"{label}.novelty_scope",
            problems,
        ):
            for field in ("new_to_repository", "new_to_reviewed_corpus"):
                if not isinstance(novelty.get(field), bool):
                    problems.append(f"{label}.novelty_scope.{field} must be boolean")
            if novelty.get("global_novelty") not in {
                "unverified",
                "verified_by_primary_review",
            }:
                problems.append(f"{label}: invalid global_novelty status")
            if not isinstance(novelty.get("rationale"), str):
                problems.append(f"{label}.novelty_scope.rationale must be text")

        prior_art = proposal.get("nearest_prior_art")
        if not isinstance(prior_art, list):
            problems.append(f"{label}.nearest_prior_art must be an array")
            prior_art = []
        for index, item in enumerate(prior_art):
            item_label = f"{label}.nearest_prior_art[{index}]"
            if not _exact_keys(item, PRIOR_ART_FIELDS, item_label, problems):
                continue
            if not _nonempty_text(item.get("source_id")):
                problems.append(f"{item_label}.source_id must be nonempty")
            elif item.get("source_id") not in seed["route_source_ids"]:
                problems.append(
                    f"{item_label}.source_id is not route-pinned evidence"
                )
            if not isinstance(item.get("primary"), bool):
                problems.append(f"{item_label}.primary must be boolean")
            evidence_file = item.get("evidence_file")
            if not _nonempty_text(evidence_file) or not (
                ROOT / evidence_file
            ).is_file():
                problems.append(f"{item_label}.evidence_file does not resolve")

        _exact_keys(
            proposal.get("exact_mechanism"),
            EXACT_MECHANISM_FIELDS,
            f"{label}.exact_mechanism",
            problems,
        )
        _exact_keys(
            proposal.get("cost_bridge"),
            COST_BRIDGE_FIELDS,
            f"{label}.cost_bridge",
            problems,
        )
        validator_plan = proposal.get("validator_plan")
        if _exact_keys(
            validator_plan,
            VALIDATOR_PLAN_FIELDS,
            f"{label}.validator_plan",
            problems,
        ):
            for field in ("raw_artifacts", "failure_labels"):
                if not isinstance(validator_plan.get(field), str):
                    problems.append(f"{label}.validator_plan.{field} must be text")
        outcome_matrix = proposal.get("outcome_matrix")
        if _exact_keys(
            outcome_matrix,
            OUTCOME_MATRIX_FIELDS,
            f"{label}.outcome_matrix",
            problems,
        ):
            for field, value in outcome_matrix.items():
                if not isinstance(value, str):
                    problems.append(
                        f"{label}.outcome_matrix.{field} must be text"
                    )
        toy_scope = proposal.get("toy_scope")
        if _exact_keys(
            toy_scope, TOY_SCOPE_FIELDS, f"{label}.toy_scope", problems
        ):
            max_bits = toy_scope.get("max_field_bits")
            if (
                not isinstance(max_bits, int)
                or isinstance(max_bits, bool)
                or max_bits < 2
            ):
                problems.append(f"{label}.toy_scope.max_field_bits is invalid")
            if not _unique_text_array(toy_scope.get("forbidden_targets")):
                problems.append(
                    f"{label}.toy_scope.forbidden_targets must be unique"
                )
        _existing_files(
            proposal.get("evidence_inputs"),
            f"{label}.evidence_inputs",
            problems,
        )
        evidence_manifest = proposal.get("evidence_manifest")
        manifest_paths: list[str] = []
        source_commit = proposal.get("provenance", {}).get("source_commit")
        if not isinstance(evidence_manifest, list) or not evidence_manifest:
            problems.append(f"{label}.evidence_manifest must be nonempty")
            evidence_manifest = []
        for index, item in enumerate(evidence_manifest):
            item_label = f"{label}.evidence_manifest[{index}]"
            if not _exact_keys(
                item, EVIDENCE_MANIFEST_FIELDS, item_label, problems
            ):
                continue
            relative = item.get("path")
            if not _nonempty_text(relative):
                problems.append(f"{item_label}.path must be nonempty")
                continue
            manifest_paths.append(relative)
            if item.get("relation") not in {
                "supports",
                "contradicts",
                "bounds",
                "context",
            }:
                problems.append(f"{item_label}.relation is invalid")
            if not _substantive_text(item.get("locator")):
                problems.append(f"{item_label}.locator must be substantive")
            if item.get("source_id") not in seed["route_source_ids"]:
                problems.append(
                    f"{item_label}.source_id is not route-pinned evidence"
                )
            if not isinstance(item.get("primary"), bool):
                problems.append(f"{item_label}.primary must be boolean")
            digest = item.get("sha256")
            if not isinstance(digest, str) or HASH_ID.fullmatch(digest) is None:
                problems.append(f"{item_label}.sha256 is invalid")
            elif (
                not isinstance(source_commit, str)
                or git_file_sha256(source_commit, relative) != digest
            ):
                problems.append(
                    f"{item_label}: evidence digest does not match source_commit"
                )
        if len(manifest_paths) != len(set(manifest_paths)):
            problems.append(f"{label}.evidence_manifest paths must be unique")
        if sorted(manifest_paths) != sorted(proposal.get("evidence_inputs", [])):
            problems.append(
                f"{label}: evidence_manifest must cover exactly evidence_inputs"
            )
        provenance = proposal.get("provenance")
        if _exact_keys(
            provenance,
            PROPOSAL_PROVENANCE_FIELDS,
            f"{label}.provenance",
            problems,
        ):
            if provenance.get("generation_method") not in {
                "human",
                "model_assisted",
                "hybrid",
            }:
                problems.append(f"{label}: invalid generation_method")
            if not _nonempty_text(provenance.get("generator")):
                problems.append(f"{label}: generator must be nonempty")
            for field in (
                "generator_family",
                "generator_version",
                "session_id",
            ):
                if not _nonempty_text(provenance.get(field)):
                    problems.append(f"{label}: {field} must be nonempty")
            context_digest = provenance.get("context_sha256")
            if not isinstance(context_digest, str) or HASH_ID.fullmatch(
                context_digest
            ) is None:
                problems.append(
                    f"{label}: context_sha256 must be lowercase 64-hex"
                )
            if not scientific_source_commit_allowed(
                provenance.get("source_commit")
            ):
                problems.append(
                    f"{label}: source_commit is not reproducible from "
                    "protected main or a registered immutable evidence ref"
                )
            if not isinstance(
                provenance.get("prompt_sha256"), str
            ) or HASH_ID.fullmatch(provenance["prompt_sha256"]) is None:
                problems.append(f"{label}: prompt_sha256 must be lowercase 64-hex")

        problems.extend(proposal_integrity_problems(proposal, label))

        duplicate_fingerprints = set(known_fingerprints)
        fingerprint = proposal.get("premise_fingerprint")
        if fingerprint_counts.get(fingerprint, 0) > 1:
            duplicate_fingerprints.add(fingerprint)
        duplicate_signatures: set[str] = set()
        declared_signature = proposal.get("mechanism_signature")
        if mechanism_signature_counts.get(declared_signature, 0) > 1:
            duplicate_signatures.add(declared_signature)
        blockers = _proposal_blockers(
            proposal,
            seed,
            policy,
            duplicate_fingerprints,
            duplicate_signatures,
        )
        if proposal_id in near_duplicate_ids:
            blockers.add("semantic_reencoding_risk")
        blockers_by_proposal[proposal_id] = blockers
    if len(proposal_ids) != len(set(proposal_ids)):
        problems.append("hypothesis proposal ids must be unique")
    return problems, blockers_by_proposal, seed_resolution_by_proposal


def validate_reviews(
    records: list[tuple[Path, dict[str, Any]]],
    proposals: list[tuple[Path, dict[str, Any]]],
    policy: dict[str, Any],
) -> tuple[list[str], dict[str, list[dict[str, Any]]]]:
    problems: list[str] = []
    proposal_index = {
        proposal.get("proposal_id"): proposal for _, proposal in proposals
    }
    by_proposal: dict[str, list[dict[str, Any]]] = defaultdict(list)
    review_ids: list[str] = []
    for path, review in records:
        label = path.relative_to(ROOT).as_posix()
        if not _exact_keys(review, REVIEW_FIELDS, label, problems):
            continue
        review_id = review.get("review_id")
        review_ids.append(review_id)
        if not isinstance(review_id, str) or REVIEW_ID.fullmatch(review_id) is None:
            problems.append(f"{label}: invalid review_id")
        if review.get("schema_version") != "0.1":
            problems.append(f"{label}: schema_version must be 0.1")
        if not _valid_date(review.get("reviewed_on")):
            problems.append(f"{label}: reviewed_on must be YYYY-MM-DD")
        proposal = proposal_index.get(review.get("proposal_id"))
        if proposal is None:
            problems.append(f"{label}: proposal_id does not resolve")
            continue
        if review.get("proposal_sha256") != proposal_sha256(proposal):
            problems.append(f"{label}: proposal_sha256 is stale or invalid")
        if not _nonempty_text(review.get("reviewer_id")):
            problems.append(f"{label}: reviewer_id must be nonempty")
        if review.get("reviewer_id") == proposal.get("proposer_id"):
            problems.append(f"{label}: proposer cannot review its own proposal")
        if review.get("reviewer_role") not in policy["quality_gate"][
            "required_review_roles"
        ]:
            problems.append(f"{label}: invalid reviewer_role")
        if review.get("source_independence") not in {
            "declared_independent",
            "shared_context",
            "unknown",
        }:
            problems.append(f"{label}: invalid source_independence")
        reviewer_provenance = review.get("reviewer_provenance")
        if _exact_keys(
            reviewer_provenance,
            REVIEWER_PROVENANCE_FIELDS,
            f"{label}.reviewer_provenance",
            problems,
        ):
            for field in ("family", "version", "session_id"):
                if not _nonempty_text(reviewer_provenance.get(field)):
                    problems.append(
                        f"{label}.reviewer_provenance.{field} must be nonempty"
                    )
            context_digest = reviewer_provenance.get("context_sha256")
            if not isinstance(context_digest, str) or HASH_ID.fullmatch(
                context_digest
            ) is None:
                problems.append(
                    f"{label}.reviewer_provenance.context_sha256 is invalid"
                )
            prompt_digest = reviewer_provenance.get("prompt_sha256")
            if not isinstance(prompt_digest, str) or HASH_ID.fullmatch(
                prompt_digest
            ) is None:
                problems.append(
                    f"{label}.reviewer_provenance.prompt_sha256 is invalid"
                )
            if not isinstance(
                reviewer_provenance.get("blind_to_other_reviews"), bool
            ):
                problems.append(
                    f"{label}.reviewer_provenance.blind_to_other_reviews "
                    "must be boolean"
                )
        verdict = review.get("verdict")
        if verdict not in {"pass", "revise", "block"}:
            problems.append(f"{label}: invalid verdict")
        blocker_codes = review.get("blocker_codes")
        if (
            not isinstance(blocker_codes, list)
            or len(blocker_codes) != len(set(blocker_codes))
            or not set(blocker_codes) <= HYPOTHESIS_HARD_REJECTIONS
        ):
            problems.append(f"{label}: blocker_codes are invalid")
            blocker_codes = []
        if verdict == "pass" and blocker_codes:
            problems.append(f"{label}: passing review cannot retain blockers")
        if verdict in {"revise", "block"} and not blocker_codes:
            problems.append(f"{label}: non-passing review must name blockers")
        if not _substantive_text(review.get("summary")):
            problems.append(f"{label}: summary must be substantive")
        _existing_files(
            review.get("evidence_inputs"),
            f"{label}.evidence_inputs",
            problems,
        )
        by_proposal[review["proposal_id"]].append(review)
    if len(review_ids) != len(set(review_ids)):
        problems.append("hypothesis review ids must be unique")
    for proposal_id, proposal_reviews in by_proposal.items():
        roles = [review["reviewer_role"] for review in proposal_reviews]
        reviewers = [review["reviewer_id"] for review in proposal_reviews]
        sessions = [
            review.get("reviewer_provenance", {}).get("session_id")
            for review in proposal_reviews
        ]
        if len(roles) != len(set(roles)):
            problems.append(f"{proposal_id}: reviewer roles must be unique")
        if len(reviewers) != len(set(reviewers)):
            problems.append(f"{proposal_id}: reviewer identities must be unique")
        if len(sessions) != len(set(sessions)):
            problems.append(f"{proposal_id}: review sessions must be unique")
    return problems, by_proposal


def build_generation_state(
    policy: dict[str, Any],
    decisions: dict[str, Any],
    engine_policy: dict[str, Any],
    proposals: list[tuple[Path, dict[str, Any]]],
    reviews: list[tuple[Path, dict[str, Any]]],
    typed_evidence_state: dict[str, Any] | None = None,
    claim_state: dict[str, Any] | None = None,
) -> tuple[list[str], dict[str, Any]]:
    typed_problems: list[str] = []
    if typed_evidence_state is None:
        typed_problems, typed_evidence_state = load_typed_evidence_state()
    claim_problems: list[str] = []
    if claim_state is None:
        claim_problems, claim_state = load_research_claim_state()
    if typed_evidence_state is None:
        typed_evidence_state = {"cells": [], "counts": {}}
    if claim_state is None:
        claim_state = {"claims": [], "counts": {}}
    problems = list(typed_problems) + list(claim_problems)
    problems.extend(
        validate_generation_policy(
            policy,
            decisions,
            engine_policy,
            typed_evidence_state,
        )
    )
    seeds = generate_seeds(
        policy,
        decisions,
        engine_policy,
        typed_evidence_state,
        claim_state,
    )
    max_generated_seeds = policy.get("limits", {}).get(
        "max_generated_seeds", 0
    )
    seed_overflow = len(seeds) > max_generated_seeds
    (
        proposal_problems,
        blockers_by_proposal,
        seed_resolution_by_proposal,
    ) = validate_proposals(proposals, seeds, policy)
    problems.extend(proposal_problems)
    review_problems, reviews_by_proposal = validate_reviews(
        reviews, proposals, policy
    )
    problems.extend(review_problems)

    required_roles = set(policy["quality_gate"]["required_review_roles"])
    independent_roles = set(
        policy["quality_gate"]["required_independent_roles"]
    )
    proposal_states: list[dict[str, Any]] = []
    cleared: list[str] = []
    for _, proposal in sorted(
        proposals, key=lambda item: item[1].get("proposal_id", "")
    ):
        proposal_id = proposal.get("proposal_id")
        if proposal_id not in blockers_by_proposal:
            continue
        blockers = set(blockers_by_proposal[proposal_id])
        proposal_reviews = reviews_by_proposal.get(proposal_id, [])
        role_index = {
            review["reviewer_role"]: review for review in proposal_reviews
        }
        proposer_family = proposal.get("provenance", {}).get(
            "generator_family"
        )
        proposer_session = proposal.get("provenance", {}).get("session_id")
        proposer_context = proposal.get("provenance", {}).get(
            "context_sha256"
        )
        if set(role_index) != required_roles:
            blockers.add("adversarial_review_incomplete")
        for role in independent_roles:
            review = role_index.get(role, {})
            reviewer_family = review.get("reviewer_provenance", {}).get(
                "family"
            )
            reviewer_session = review.get("reviewer_provenance", {}).get(
                "session_id"
            )
            reviewer_context = review.get("reviewer_provenance", {}).get(
                "context_sha256"
            )
            if (
                review.get("source_independence") != "declared_independent"
                or reviewer_family == proposer_family
                or reviewer_session == proposer_session
                or reviewer_context == proposer_context
                or review.get("reviewer_provenance", {}).get(
                    "blind_to_other_reviews"
                )
                is not True
            ):
                blockers.add("review_independence_unestablished")
        if any(
            review.get("reviewer_provenance", {}).get(
                "blind_to_other_reviews"
            )
            is not True
            for review in proposal_reviews
        ):
            blockers.add("adversarial_review_incomplete")
        reviewer_families = {
            review.get("reviewer_provenance", {}).get("family")
            for review in proposal_reviews
        }
        if proposal_reviews and len(reviewer_families) < 2:
            blockers.add("review_independence_unestablished")
        reviewer_contexts = [
            review.get("reviewer_provenance", {}).get("context_sha256")
            for review in proposal_reviews
        ]
        if len(reviewer_contexts) != len(set(reviewer_contexts)):
            blockers.add("review_independence_unestablished")
        for review in proposal_reviews:
            blockers.update(review.get("blocker_codes", []))
            if review.get("verdict") == "block":
                blockers.add("adversarial_review_blocked")
            elif review.get("verdict") == "revise":
                blockers.add("adversarial_review_incomplete")
        if not blockers:
            disposition = "quality_cleared"
            cleared.append(proposal_id)
        elif blockers & {
            "threat_model_drift",
            "seed_scope_mismatch",
            "duplicate_or_reencoding",
            "duplicate_mechanism_signature",
            "targets_secp256k1_directly",
            "adversarial_review_blocked",
            "typed_evidence_mismatch",
            "target_property_violated",
            "stale_seed_snapshot",
        }:
            disposition = "hard_rejected"
        else:
            disposition = "needs_revision"
        proposal_states.append(
            {
                "proposal_id": proposal_id,
                "seed_id": proposal["seed_id"],
                "cell_id": proposal["cell_id"],
                "route_id": proposal["route_id"],
                "title": proposal["title"],
                "proposal_sha256": proposal_sha256(proposal),
                "seed_resolution": seed_resolution_by_proposal.get(
                    proposal_id, "unresolved"
                ),
                "review_roles_present": sorted(role_index),
                "review_independence": (
                    "cross_family_attested_not_mechanically_proved"
                    if proposal_reviews
                    else "not_reviewed"
                ),
                "blockers": sorted(blockers),
                "disposition": disposition,
                "authorization": "none",
            }
        )

    max_cleared = policy["limits"]["max_quality_cleared_per_cycle"]
    overflow = len(cleared) > max_cleared
    retained = [] if overflow else sorted(cleared)
    hypothesis_drafts = []
    proposal_index = {
        proposal["proposal_id"]: proposal for _, proposal in proposals
    }
    for proposal_id in retained:
        proposal = proposal_index[proposal_id]
        proposal_digest = proposal_sha256(proposal)
        review_artifacts = [
            {
                "review_id": review["review_id"],
                "reviewer_role": review["reviewer_role"],
                "review_sha256": sha256_json(review),
            }
            for review in sorted(
                reviews_by_proposal.get(proposal_id, []),
                key=lambda item: item["reviewer_role"],
            )
        ]
        draft = {
            "draft_id": (
                f"HYP_DRAFT_{proposal_digest[:12].upper()}"
            ),
            "proposal_id": proposal_id,
            "proposal_sha256": proposal_digest,
            "source_commit": proposal["provenance"]["source_commit"],
            "review_artifacts": review_artifacts,
            "cell_id": proposal["cell_id"],
            "typed_evidence_digest": proposal[
                "typed_evidence_digest"
            ],
            "toy_scope": proposal["toy_scope"],
            "route_id": proposal["route_id"],
            "threat_model": proposal["threat_model"],
            "statement": proposal["hypothesis_statement"],
            "new_premise": proposal["new_premise"],
            "contract_digests": scientific_contract_digests(
                proposal["mechanism_contract"],
                proposal["prediction_contract"],
                proposal["cost_contract"],
                proposal["validator_contract"],
            ),
            "status": "quality_cleared_not_authorized",
            "next_gate": (
                "Bind an immutable candidate snapshot to this exact draft, "
                "complete evidence-bound validator independence, and obtain "
                "a separate dated owner decision. This draft authorizes nothing."
            ),
        }
        draft["draft_sha256"] = sha256_json(draft)
        hypothesis_drafts.append(draft)
    premise_groups: dict[str, list[str]] = defaultdict(list)
    mechanism_groups: dict[str, list[str]] = defaultdict(list)
    proposal_values = [proposal for _, proposal in proposals]
    for proposal in proposal_values:
        proposal_id = proposal.get("proposal_id")
        if not isinstance(proposal_id, str):
            continue
        premise_groups[str(proposal.get("premise_fingerprint"))].append(
            proposal_id
        )
        mechanism_groups[str(proposal.get("mechanism_signature"))].append(
            proposal_id
        )
    near_duplicate_pairs = []
    for left_index, left in enumerate(proposal_values):
        for right in proposal_values[left_index + 1 :]:
            if (
                left.get("route_id") == right.get("route_id")
                and isinstance(left.get("new_premise"), str)
                and isinstance(right.get("new_premise"), str)
            ):
                similarity = premise_similarity(
                    left["new_premise"], right["new_premise"]
                )
                if similarity >= 0.85:
                    near_duplicate_pairs.append(
                        {
                            "proposal_ids": sorted(
                                [left["proposal_id"], right["proposal_id"]]
                            ),
                            "lexical_similarity": round(similarity, 6),
                            "disposition": "semantic_reencoding_review_required",
                        }
                    )
    return problems, {
        "schema_version": "0.1-generated",
        "generator_id": policy["generator_id"],
        "source_hashes": {
            "generation_policy_sha256": sha256_json(policy),
            "typed_evidence_state_sha256": sha256_json(
                typed_evidence_state
            ),
            "research_claim_state_sha256": sha256_json(claim_state),
            "proposals_sha256": sha256_json(
                [proposal for _, proposal in proposals]
            ),
            "reviews_sha256": sha256_json(
                [review for _, review in reviews]
            ),
        },
        "trust_boundary": policy["trust_boundary"],
        "counts": {
            "generated_seeds": len(seeds),
            "submitted_proposals": len(proposals),
            "adversarial_reviews": len(reviews),
            "quality_cleared_proposals": len(cleared),
            "retained_hypothesis_drafts": len(hypothesis_drafts),
            "typed_evidence_cells": typed_evidence_state.get(
                "counts", {}
            ).get("cells", 0),
            "typed_seed_eligible_cells": typed_evidence_state.get(
                "counts", {}
            ).get("seed_eligible_cells", 0),
        },
        "typed_evidence": {
            "evidence_id": typed_evidence_state.get("evidence_id"),
            "target_id": typed_evidence_state.get("target_id"),
            "counts": typed_evidence_state.get("counts", {}),
            "source_hashes": typed_evidence_state.get("source_hashes", {}),
            "authorization_boundary": typed_evidence_state.get(
                "authorization_boundary", {}
            ),
            "authorization": "none",
        },
        "research_claims": {
            "claim_model_id": claim_state.get("claim_model_id"),
            "counts": claim_state.get("counts", {}),
            "open_routes": claim_state.get("open_routes", []),
            "authorization": claim_state.get("authorization", {}),
            "state_sha256": sha256_json(claim_state),
        },
        "seed_coverage": {
            "threshold": max_generated_seeds,
            "eligible_seed_count": len(seeds),
            "overflow_triggered": seed_overflow,
            "represented_seed_ids": [
                seed["seed_id"] for seed in seeds
            ],
            "represented_cell_ids": [
                seed["cell_id"] for seed in seeds
            ],
            "disposition": (
                "coverage_review_required_non_executable"
                if seed_overflow
                else "within_declared_coverage"
            ),
            "rule": (
                "An overflow is materialized rather than hidden or treated as "
                "a generation failure. Every seed remains non-executable; the "
                "coverage artifact must be reviewed before a later cycle may "
                "change the threshold or synthesis partition."
            ),
        },
        "seed_lifecycle": {
            "identity_scope": policy["synthesis_rules"][0][
                "seed_identity_fields"
            ],
            "claim_state_digest_role": "provenance_only_not_seed_identity",
            "frozen_alias_ids": sorted(
                binding["seed_id"]
                for binding in policy["frozen_seed_bindings"]
            ),
            "rule": (
                "A frozen legacy id resolves to current state only while its "
                "scoped scientific identity is unchanged; otherwise it is a "
                "historical-only snapshot and cannot quality-clear."
            ),
        },
        "generated_seeds": seeds,
        "proposal_intake": proposal_states,
        "collision_groups": {
            "premise_fingerprints": [
                {
                    "fingerprint": fingerprint,
                    "proposal_ids": sorted(proposal_ids),
                }
                for fingerprint, proposal_ids in sorted(
                    premise_groups.items()
                )
                if len(proposal_ids) > 1
            ],
            "mechanism_signatures": [
                {
                    "signature": signature,
                    "proposal_ids": sorted(proposal_ids),
                }
                for signature, proposal_ids in sorted(
                    mechanism_groups.items()
                )
                if len(proposal_ids) > 1
            ],
            "near_duplicate_pairs": sorted(
                near_duplicate_pairs,
                key=lambda item: item["proposal_ids"],
            ),
        },
        "portfolio_overflow": {
            "triggered": overflow,
            "rule": policy["quality_gate"]["overflow_rule"],
            "quality_cleared_proposal_ids": sorted(cleared),
        },
        "retained_hypothesis_drafts": hypothesis_drafts,
        "authorization_boundary": (
            "Seeds, proposals, reviews, and generated drafts are all "
            "non-executable. Only the existing Research Engine exploration gate "
            "can authorize a preregistered toy run; promotion stays separately "
            "closed."
        ),
    }
