#!/usr/bin/env python3
"""Typed evidence and zero-compute applicability screens for Research Engine v0.

The evidence graph is deliberately small and strict. It does not infer mathematics
from prose. It evaluates typed requirements against provenance-bound target
properties, materializes one cell per mechanism, and retains desk decisions without
pretending that a literature or arithmetic screen was an experiment.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
POLICY_PATH = ROOT / "repo" / "ECDLP_TYPED_EVIDENCE_V0.json"
STATE_PATH = ROOT / "data" / "typed_evidence_state.json"
DECISIONS_PATH = ROOT / "repo" / "ECDLP_DECISION_SUBSTRATE.json"
SOURCE_REGISTRY_PATH = ROOT / "data" / "source_registry.json"
DESK_DECISIONS_DIR = ROOT / "experiments" / "engine" / "desk_decisions"

POLICY_FIELDS = {
    "schema_version",
    "evidence_id",
    "status",
    "purpose",
    "target_id",
    "trust_boundary",
    "source_claims",
    "target_properties",
    "cost_quantities",
    "barriers",
    "mechanisms",
}
TRUST_FIELDS = {
    "claim_acceptance",
    "unknown_policy",
    "screen_scope",
    "authorization_boundary",
}
CLAIM_FIELDS = {
    "id",
    "source_id",
    "source_type",
    "citation",
    "read_status",
    "url",
    "artifact_sha256",
    "locator",
    "statement",
    "boundary",
    "evidence_path",
}
CLAIM_EXTRACT_FIELDS = {
    "schema_version",
    "source_id",
    "source_title",
    "source_url",
    "source_artifact_sha256",
    "acquired_on",
    "review_status",
    "review_provenance",
    "claims",
}
CLAIM_EXTRACT_REVIEW_FIELDS = {
    "method",
    "source_independence",
    "boundary",
}
CLAIM_EXTRACT_ENTRY_FIELDS = {
    "claim_id",
    "locator",
    "paraphrase",
    "boundary",
}
LOCATOR_FIELDS = {"kind", "value"}
PROPERTY_FIELDS = {
    "id",
    "label",
    "value_type",
    "value",
    "status",
    "statement",
    "scope",
    "source_claim_ids",
}
COST_FIELDS = {
    "id",
    "label",
    "definition",
    "baseline",
    "measurement",
    "status",
    "source_claim_ids",
}
BARRIER_FIELDS = {
    "id",
    "route_id",
    "disposition",
    "exact_scope",
    "source_claim_ids",
    "reopening_conditions",
}
MECHANISM_FIELDS = {
    "id",
    "label",
    "route_id",
    "threat_model",
    "status",
    "scope",
    "construction",
    "relation_action",
    "changed_quantity",
    "cost_quantity_id",
    "source_claim_ids",
    "requires_all",
    "barrier_ids",
    "intake_mode",
    "seed_axes",
    "boundary",
}
REQUIREMENT_FIELDS = {"property_id", "operator", "expected", "rationale"}
SEED_AXIS_FIELDS = {
    "target_feature_id",
    "mechanism_primitive_id",
    "uncertainty_id",
}
DESK_DECISION_FIELDS = {
    "schema_version",
    "decision_id",
    "decided_on",
    "cell_id",
    "route_id",
    "classification",
    "scope",
    "rationale",
    "evidence_claim_ids",
    "property_verdicts",
    "route_effect",
    "authorization",
    "calibration",
    "reopening_conditions",
}
PROPERTY_VERDICT_FIELDS = {
    "property_id",
    "operator",
    "expected",
    "actual",
    "verdict",
}

ID_RE = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
DECISION_ID_RE = re.compile(r"^EDD-\d{4}-\d{2}-\d{2}-\d{3}$")
DECISIVE_READ_STATUSES = {
    "kernel_verified",
    "certificate_replayed",
    "full_text_obtained",
    "public_constant_recomputed",
}
OPERATORS = {"eq", "ne", "gte", "lte", "contains"}
SECP256K1_P = (
    0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
)
PKC_SMOOTH_ARITY = {
    "M-PKC-SMOOTH-M4": 4,
    "M-PKC-SMOOTH-M14": 14,
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_records(directory: Path) -> list[tuple[Path, dict[str, Any]]]:
    if not directory.exists():
        return []
    return [
        (path, load_json(path))
        for path in sorted(directory.glob("*.json"))
        if not path.name.endswith(".schema.json")
    ]


def sha256_json(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ceil_nth_root(value: int, exponent: int) -> int:
    """Return the least integer r with r**exponent >= value."""
    low = 0
    high = 1
    while high**exponent < value:
        high *= 2
    while low + 1 < high:
        middle = (low + high) // 2
        if middle**exponent < value:
            low = middle
        else:
            high = middle
    return high


def _exact_keys(
    value: Any, expected: set[str], label: str, problems: list[str]
) -> bool:
    if not isinstance(value, dict):
        problems.append(f"{label} must be an object")
        return False
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        problems.append(f"{label} keys differ: missing={missing}, extra={extra}")
        return False
    return True


def _text(value: Any, minimum: int = 1) -> bool:
    return isinstance(value, str) and len(value.strip()) >= minimum


def _unique_texts(value: Any, *, allow_empty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (allow_empty or bool(value))
        and all(_text(item) for item in value)
        and len(value) == len(set(value))
    )


def _valid_date(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def _corpus_source_ids() -> set[str]:
    ids: set[str] = set()
    for path in sorted(
        (ROOT / "domains" / "ecdlp" / "corpus_snapshots").glob("*.json")
    ):
        snapshot = load_json(path)
        ids.update(snapshot.get("source_ids", []))
    return ids


def _source_ids(source_registry: dict[str, Any]) -> set[str]:
    return {
        item["id"]
        for item in source_registry.get("sources", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    } | _corpus_source_ids() | {"repo:kernel", "repo:certificate"}


def _value_matches_type(value_type: str, value: Any) -> bool:
    if value_type == "boolean":
        return isinstance(value, bool)
    if value_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if value_type == "string":
        return isinstance(value, str) and bool(value)
    return False


def validate_policy(
    policy: dict[str, Any],
    decisions: dict[str, Any],
    source_registry: dict[str, Any],
) -> list[str]:
    problems: list[str] = []
    if not _exact_keys(policy, POLICY_FIELDS, "typed evidence policy", problems):
        return problems
    if policy.get("schema_version") != "0.1":
        problems.append("typed evidence schema_version must be 0.1")
    if policy.get("status") != "active":
        problems.append("typed evidence policy must be active")
    for field in ("evidence_id", "purpose", "target_id"):
        if not _text(policy.get(field), 8):
            problems.append(f"typed evidence {field} must be substantive")
    trust = policy.get("trust_boundary")
    if _exact_keys(trust, TRUST_FIELDS, "trust_boundary", problems):
        for field in TRUST_FIELDS:
            if not _text(trust.get(field), 20):
                problems.append(f"trust_boundary.{field} must be substantive")

    allowed_sources = _source_ids(source_registry)
    claims = policy.get("source_claims")
    if not isinstance(claims, list) or not claims:
        problems.append("source_claims must be a nonempty array")
        claims = []
    claim_ids: list[str] = []
    for index, claim in enumerate(claims):
        label = f"source_claims[{index}]"
        if not _exact_keys(claim, CLAIM_FIELDS, label, problems):
            continue
        claim_id = claim.get("id")
        if not isinstance(claim_id, str) or ID_RE.fullmatch(claim_id) is None:
            problems.append(f"{label}.id is invalid")
        else:
            claim_ids.append(claim_id)
        source_id = claim.get("source_id")
        if (
            source_id not in allowed_sources
            and not (
                isinstance(source_id, str)
                and source_id.startswith("external:")
            )
        ):
            problems.append(f"{label}.source_id does not resolve")
        if claim.get("source_type") not in {
            "primary_literature",
            "kernel_theorem",
            "certificate",
            "public_constant",
        }:
            problems.append(f"{label}.source_type is invalid")
        if claim.get("read_status") not in {
            *DECISIVE_READ_STATUSES,
            "metadata_only",
            "unread",
        }:
            problems.append(f"{label}.read_status is invalid")
        for field in ("citation", "statement", "boundary"):
            if not _text(claim.get(field), 20):
                problems.append(f"{label}.{field} must be substantive")
        locator = claim.get("locator")
        if _exact_keys(locator, LOCATOR_FIELDS, f"{label}.locator", problems):
            if locator.get("kind") not in {
                "theorem",
                "section",
                "page",
                "equation",
                "certificate_field",
            }:
                problems.append(f"{label}.locator.kind is invalid")
            if not _text(locator.get("value")):
                problems.append(f"{label}.locator.value must be nonempty")
        artifact_sha = claim.get("artifact_sha256")
        if artifact_sha is not None and (
            not isinstance(artifact_sha, str)
            or SHA256_RE.fullmatch(artifact_sha) is None
        ):
            problems.append(f"{label}.artifact_sha256 is invalid")
        evidence_path = claim.get("evidence_path")
        if evidence_path is not None:
            resolved_evidence = ROOT / evidence_path
            if not _text(evidence_path) or not resolved_evidence.is_file():
                problems.append(f"{label}.evidence_path does not resolve")
            else:
                if (
                    artifact_sha is not None
                    and claim.get("source_type") != "primary_literature"
                    and sha256_file(resolved_evidence) != artifact_sha
                ):
                    problems.append(
                        f"{label}.artifact_sha256 does not match evidence_path"
                    )
                if (
                    claim.get("source_type") == "kernel_theorem"
                    and isinstance(locator, dict)
                    and locator.get("kind") == "theorem"
                ):
                    theorem_name = str(locator.get("value", "")).split(".")[-1]
                    source = resolved_evidence.read_text(
                        encoding="utf-8", errors="replace"
                    )
                    declaration = re.compile(
                        rf"(?m)^\s*(?:theorem|lemma|def)\s+"
                        rf"{re.escape(theorem_name)}(?:\s|\()"
                    )
                    if declaration.search(source) is None:
                        problems.append(
                            f"{label}.locator theorem is absent from evidence_path"
                        )
        if claim.get("source_type") in {"kernel_theorem", "certificate"}:
            if evidence_path is None:
                problems.append(f"{label} requires an evidence_path")
        if claim.get("source_type") == "primary_literature":
            if not _text(claim.get("url")):
                problems.append(f"{label} primary source requires a URL")
            if (
                claim.get("read_status") == "full_text_obtained"
                and artifact_sha is None
            ):
                problems.append(
                    f"{label} full-text primary source requires an artifact hash"
                )
            if claim.get("read_status") == "full_text_obtained":
                if evidence_path is None:
                    problems.append(
                        f"{label} full-text primary source requires a "
                        "claim-extract evidence_path"
                    )
                elif resolved_evidence.is_file():
                    extract_root = (ROOT / "data" / "source_claim_extracts").resolve()
                    if not resolved_evidence.resolve().is_relative_to(extract_root):
                        problems.append(
                            f"{label}.evidence_path must be under "
                            "data/source_claim_extracts/"
                        )
                    try:
                        extraction = load_json(resolved_evidence)
                    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                        problems.append(
                            f"{label}.evidence_path must contain valid JSON"
                        )
                    else:
                        if _exact_keys(
                            extraction,
                            CLAIM_EXTRACT_FIELDS,
                            f"{label}.claim_extract",
                            problems,
                        ):
                            if extraction.get("schema_version") != "0.1":
                                problems.append(
                                    f"{label}.claim_extract schema_version is invalid"
                                )
                            if extraction.get("source_id") != claim.get("source_id"):
                                problems.append(
                                    f"{label}.claim_extract source_id differs"
                                )
                            if extraction.get("source_url") != claim.get("url"):
                                problems.append(
                                    f"{label}.claim_extract source_url differs"
                                )
                            if (
                                extraction.get("source_artifact_sha256")
                                != artifact_sha
                            ):
                                problems.append(
                                    f"{label}.claim_extract source artifact hash differs"
                                )
                            if (
                                extraction.get("review_status")
                                != "full_text_obtained"
                            ):
                                problems.append(
                                    f"{label}.claim_extract review status is invalid"
                                )
                            review = extraction.get("review_provenance")
                            if _exact_keys(
                                review,
                                CLAIM_EXTRACT_REVIEW_FIELDS,
                                f"{label}.claim_extract.review_provenance",
                                problems,
                            ):
                                if review.get("source_independence") not in {
                                    "established",
                                    "not_established",
                                }:
                                    problems.append(
                                        f"{label}.claim_extract source independence "
                                        "is invalid"
                                    )
                                for field in ("method", "boundary"):
                                    if not _text(review.get(field), 12):
                                        problems.append(
                                            f"{label}.claim_extract.review_provenance."
                                            f"{field} must be substantive"
                                        )
                            entries = extraction.get("claims")
                            if not isinstance(entries, list):
                                problems.append(
                                    f"{label}.claim_extract claims must be an array"
                                )
                                entries = []
                            matching_entries = [
                                entry
                                for entry in entries
                                if isinstance(entry, dict)
                                and entry.get("claim_id") == claim.get("id")
                            ]
                            if len(matching_entries) != 1:
                                problems.append(
                                    f"{label}.claim_extract must bind exactly one "
                                    "matching claim"
                                )
                            else:
                                entry = matching_entries[0]
                                if _exact_keys(
                                    entry,
                                    CLAIM_EXTRACT_ENTRY_FIELDS,
                                    f"{label}.claim_extract.claim",
                                    problems,
                                ):
                                    if entry.get("locator") != locator:
                                        problems.append(
                                            f"{label}.claim_extract locator differs"
                                        )
                                    for field in ("paraphrase", "boundary"):
                                        if not _text(entry.get(field), 20):
                                            problems.append(
                                                f"{label}.claim_extract.claim.{field} "
                                                "must be substantive"
                                            )
    if len(claim_ids) != len(set(claim_ids)):
        problems.append("source claim ids must be unique")
    claim_id_set = set(claim_ids)

    properties = policy.get("target_properties")
    if not isinstance(properties, list) or not properties:
        problems.append("target_properties must be a nonempty array")
        properties = []
    property_ids: list[str] = []
    for index, prop in enumerate(properties):
        label = f"target_properties[{index}]"
        if not _exact_keys(prop, PROPERTY_FIELDS, label, problems):
            continue
        prop_id = prop.get("id")
        if not isinstance(prop_id, str) or ID_RE.fullmatch(prop_id) is None:
            problems.append(f"{label}.id is invalid")
        else:
            property_ids.append(prop_id)
        if prop.get("status") not in {
            "kernel_verified",
            "kernel_derived",
            "certificate_replayed",
            "public_constant_recomputed",
            "unknown",
        }:
            problems.append(f"{label}.status is invalid")
        value = prop.get("value")
        if prop.get("status") == "unknown":
            if value is not None:
                problems.append(f"{label}.value must be null when unknown")
        elif not _value_matches_type(prop.get("value_type"), value):
            problems.append(f"{label}.value does not match value_type")
        for field in ("label", "statement", "scope"):
            if not _text(prop.get(field), 12):
                problems.append(f"{label}.{field} must be substantive")
        refs = prop.get("source_claim_ids")
        if not _unique_texts(refs) or not set(refs) <= claim_id_set:
            problems.append(f"{label}.source_claim_ids do not resolve")
        elif prop.get("status") != "unknown" and any(
            next(
                item for item in claims if item.get("id") == ref
            ).get("read_status")
            not in DECISIVE_READ_STATUSES
            for ref in refs
        ):
            problems.append(f"{label} uses non-decisive source claims")
    if len(property_ids) != len(set(property_ids)):
        problems.append("target property ids must be unique")
    property_id_set = set(property_ids)

    costs = policy.get("cost_quantities")
    if not isinstance(costs, list) or not costs:
        problems.append("cost_quantities must be a nonempty array")
        costs = []
    cost_ids: list[str] = []
    for index, cost in enumerate(costs):
        label = f"cost_quantities[{index}]"
        if not _exact_keys(cost, COST_FIELDS, label, problems):
            continue
        cost_id = cost.get("id")
        if not isinstance(cost_id, str) or ID_RE.fullmatch(cost_id) is None:
            problems.append(f"{label}.id is invalid")
        else:
            cost_ids.append(cost_id)
        for field in ("label", "definition", "baseline", "measurement"):
            if not _text(cost.get(field), 12):
                problems.append(f"{label}.{field} must be substantive")
        if cost.get("status") not in {"defined", "partial", "missing"}:
            problems.append(f"{label}.status is invalid")
        refs = cost.get("source_claim_ids")
        if not _unique_texts(refs) or not set(refs) <= claim_id_set:
            problems.append(f"{label}.source_claim_ids do not resolve")
    if len(cost_ids) != len(set(cost_ids)):
        problems.append("cost quantity ids must be unique")
    cost_id_set = set(cost_ids)

    route_ids = {
        route["id"]
        for route in decisions.get("routes", [])
        if isinstance(route, dict) and isinstance(route.get("id"), str)
    }
    barriers = policy.get("barriers")
    if not isinstance(barriers, list):
        problems.append("barriers must be an array")
        barriers = []
    barrier_ids: list[str] = []
    for index, barrier in enumerate(barriers):
        label = f"barriers[{index}]"
        if not _exact_keys(barrier, BARRIER_FIELDS, label, problems):
            continue
        barrier_id = barrier.get("id")
        if not isinstance(barrier_id, str) or ID_RE.fullmatch(barrier_id) is None:
            problems.append(f"{label}.id is invalid")
        else:
            barrier_ids.append(barrier_id)
        if barrier.get("route_id") not in route_ids:
            problems.append(f"{label}.route_id does not resolve")
        if barrier.get("disposition") not in {
            "closed",
            "scoped_negative",
            "open",
        }:
            problems.append(f"{label}.disposition is invalid")
        if not _text(barrier.get("exact_scope"), 20):
            problems.append(f"{label}.exact_scope must be substantive")
        refs = barrier.get("source_claim_ids")
        if not _unique_texts(refs) or not set(refs) <= claim_id_set:
            problems.append(f"{label}.source_claim_ids do not resolve")
        if not _unique_texts(barrier.get("reopening_conditions")):
            problems.append(f"{label}.reopening_conditions must be nonempty")
    if len(barrier_ids) != len(set(barrier_ids)):
        problems.append("barrier ids must be unique")
    barrier_id_set = set(barrier_ids)

    mechanisms = policy.get("mechanisms")
    if not isinstance(mechanisms, list) or not mechanisms:
        problems.append("mechanisms must be a nonempty array")
        mechanisms = []
    mechanism_ids: list[str] = []
    for index, mechanism in enumerate(mechanisms):
        label = f"mechanisms[{index}]"
        if not _exact_keys(mechanism, MECHANISM_FIELDS, label, problems):
            continue
        mechanism_id = mechanism.get("id")
        if (
            not isinstance(mechanism_id, str)
            or ID_RE.fullmatch(mechanism_id) is None
        ):
            problems.append(f"{label}.id is invalid")
        else:
            mechanism_ids.append(mechanism_id)
        if mechanism.get("route_id") not in route_ids:
            problems.append(f"{label}.route_id does not resolve")
        if mechanism.get("status") not in {
            "published",
            "speculative",
            "closed",
        }:
            problems.append(f"{label}.status is invalid")
        if mechanism.get("intake_mode") not in {
            "proposal",
            "desk_cost_bridge",
            "property_resolution",
            "none",
        }:
            problems.append(f"{label}.intake_mode is invalid")
        for field in (
            "label",
            "threat_model",
            "scope",
            "construction",
            "relation_action",
            "changed_quantity",
            "boundary",
        ):
            if not _text(mechanism.get(field), 8):
                problems.append(f"{label}.{field} must be substantive")
        if mechanism.get("cost_quantity_id") not in cost_id_set:
            problems.append(f"{label}.cost_quantity_id does not resolve")
        refs = mechanism.get("source_claim_ids")
        if not _unique_texts(refs) or not set(refs) <= claim_id_set:
            problems.append(f"{label}.source_claim_ids do not resolve")
        mechanism_barriers = mechanism.get("barrier_ids")
        if not _unique_texts(mechanism_barriers, allow_empty=True) or not set(
            mechanism_barriers
        ) <= barrier_id_set:
            problems.append(f"{label}.barrier_ids do not resolve")
        requirements = mechanism.get("requires_all")
        if not isinstance(requirements, list) or not requirements:
            problems.append(f"{label}.requires_all must be nonempty")
            requirements = []
        requirement_properties: list[str] = []
        for req_index, requirement in enumerate(requirements):
            req_label = f"{label}.requires_all[{req_index}]"
            if not _exact_keys(
                requirement, REQUIREMENT_FIELDS, req_label, problems
            ):
                continue
            property_id = requirement.get("property_id")
            requirement_properties.append(property_id)
            if property_id not in property_id_set:
                problems.append(f"{req_label}.property_id does not resolve")
            if requirement.get("operator") not in OPERATORS:
                problems.append(f"{req_label}.operator is invalid")
            if not _text(requirement.get("rationale"), 12):
                problems.append(f"{req_label}.rationale must be substantive")
        if len(requirement_properties) != len(set(requirement_properties)):
            problems.append(f"{label}.requires_all repeats a property")
        if mechanism_id in PKC_SMOOTH_ARITY and len(requirements) == 1:
            arity = PKC_SMOOTH_ARITY[mechanism_id]
            expected_threshold = ceil_nth_root(SECP256K1_P, arity)
            requirement = requirements[0]
            if (
                requirement.get("property_id")
                != "TP-SECP-PMINUS1-SMOOTH-DIVISOR"
                or requirement.get("operator") != "gte"
                or requirement.get("expected") != expected_threshold
            ):
                problems.append(
                    f"{label} must use the recomputed ceil(p^(1/{arity})) "
                    f"threshold {expected_threshold}"
                )
        seed_axes = mechanism.get("seed_axes")
        if _exact_keys(seed_axes, SEED_AXIS_FIELDS, f"{label}.seed_axes", problems):
            for field in SEED_AXIS_FIELDS:
                if not _text(seed_axes.get(field)):
                    problems.append(f"{label}.seed_axes.{field} is invalid")
    if len(mechanism_ids) != len(set(mechanism_ids)):
        problems.append("mechanism ids must be unique")
    return problems


def _evaluate(operator: str, actual: Any, expected: Any) -> bool:
    if operator == "eq":
        return actual == expected
    if operator == "ne":
        return actual != expected
    if operator == "gte":
        return actual >= expected
    if operator == "lte":
        return actual <= expected
    if operator == "contains":
        return expected in actual
    raise ValueError(f"unsupported operator: {operator}")


def materialize_cells(policy: dict[str, Any]) -> list[dict[str, Any]]:
    claims = {item["id"]: item for item in policy["source_claims"]}
    properties = {item["id"]: item for item in policy["target_properties"]}
    costs = {item["id"]: item for item in policy["cost_quantities"]}
    barriers = {item["id"]: item for item in policy["barriers"]}
    cells: list[dict[str, Any]] = []
    for mechanism in sorted(policy["mechanisms"], key=lambda item: item["id"]):
        requirement_results: list[dict[str, Any]] = []
        for requirement in mechanism["requires_all"]:
            prop = properties[requirement["property_id"]]
            if prop["status"] == "unknown":
                verdict = "unknown"
            else:
                verdict = (
                    "satisfied"
                    if _evaluate(
                        requirement["operator"],
                        prop["value"],
                        requirement["expected"],
                    )
                    else "violated"
                )
            requirement_results.append(
                {
                    "property_id": prop["id"],
                    "property_status": prop["status"],
                    "operator": requirement["operator"],
                    "expected": requirement["expected"],
                    "actual": prop["value"],
                    "verdict": verdict,
                    "source_claim_ids": prop["source_claim_ids"],
                    "rationale": requirement["rationale"],
                }
            )
        mechanism_barriers = [
            barriers[barrier_id] for barrier_id in mechanism["barrier_ids"]
        ]
        if any(item["verdict"] == "violated" for item in requirement_results):
            status = "decided_inapplicable"
        elif mechanism["status"] == "closed" or any(
            item["disposition"] == "closed" for item in mechanism_barriers
        ):
            status = "decided_closed"
        elif any(item["verdict"] == "unknown" for item in requirement_results):
            status = "property_resolution_required"
        else:
            status = "open"
        source_claim_ids = sorted(
            set(mechanism["source_claim_ids"])
            | {
                claim_id
                for result in requirement_results
                for claim_id in result["source_claim_ids"]
            }
            | {
                claim_id
                for barrier in mechanism_barriers
                for claim_id in barrier["source_claim_ids"]
            }
            | set(costs[mechanism["cost_quantity_id"]]["source_claim_ids"])
        )
        source_ids = sorted(
            {
                claims[claim_id]["source_id"]
                for claim_id in source_claim_ids
            }
        )
        evidence_paths = sorted(
            {
                claims[claim_id]["evidence_path"]
                for claim_id in source_claim_ids
                if claims[claim_id]["evidence_path"] is not None
            }
        )
        evidence_packet = {
            "claims": [claims[claim_id] for claim_id in source_claim_ids],
            "requirements": requirement_results,
            "cost_quantity": costs[mechanism["cost_quantity_id"]],
            "barriers": mechanism_barriers,
        }
        cells.append(
            {
                "cell_id": f"CELL-{mechanism['id']}",
                "mechanism_id": mechanism["id"],
                "route_id": mechanism["route_id"],
                "threat_model": mechanism["threat_model"],
                "status": status,
                "scope": mechanism["scope"],
                "construction": mechanism["construction"],
                "relation_action": mechanism["relation_action"],
                "changed_quantity": mechanism["changed_quantity"],
                "cost_quantity_id": mechanism["cost_quantity_id"],
                "cost_quantity_status": costs[
                    mechanism["cost_quantity_id"]
                ]["status"],
                "cost_quantity": costs[mechanism["cost_quantity_id"]],
                "requirement_results": requirement_results,
                "barrier_ids": mechanism["barrier_ids"],
                "source_claim_ids": source_claim_ids,
                "source_ids": source_ids,
                "evidence_paths": evidence_paths,
                "evidence_digest": sha256_json(evidence_packet),
                "seed_axes": mechanism["seed_axes"],
                "intake_mode": mechanism["intake_mode"],
                "seed_eligible": status
                in {"open", "property_resolution_required"}
                and mechanism["intake_mode"] != "none",
                "boundary": mechanism["boundary"],
                "authorization": "none",
            }
        )
    return cells


def validate_desk_decisions(
    records: list[tuple[Path, dict[str, Any]]],
    cells: list[dict[str, Any]],
    policy: dict[str, Any],
) -> tuple[list[str], list[dict[str, Any]]]:
    problems: list[str] = []
    cell_index = {cell["cell_id"]: cell for cell in cells}
    claim_index = {claim["id"]: claim for claim in policy["source_claims"]}
    ids: list[str] = []
    decided_cells: list[str] = []
    normalized: list[dict[str, Any]] = []
    for path, record in records:
        label = path.relative_to(ROOT).as_posix()
        if not _exact_keys(record, DESK_DECISION_FIELDS, label, problems):
            continue
        decision_id = record.get("decision_id")
        if (
            not isinstance(decision_id, str)
            or DECISION_ID_RE.fullmatch(decision_id) is None
        ):
            problems.append(f"{label}.decision_id is invalid")
        else:
            ids.append(decision_id)
        if record.get("schema_version") != "0.1":
            problems.append(f"{label}.schema_version must be 0.1")
        if not _valid_date(record.get("decided_on")):
            problems.append(f"{label}.decided_on must be YYYY-MM-DD")
        cell = cell_index.get(record.get("cell_id"))
        if cell is None:
            problems.append(f"{label}.cell_id does not resolve")
            continue
        decided_cells.append(cell["cell_id"])
        if record.get("route_id") != cell["route_id"]:
            problems.append(f"{label}.route_id differs from the cell")
        expected_class = {
            "decided_inapplicable": "inapplicable",
            "decided_closed": "bounded_negative",
        }.get(cell["status"])
        if record.get("classification") != expected_class:
            problems.append(
                f"{label}.classification must be {expected_class!r}"
            )
        if record.get("scope") not in {
            "mechanism_instance_only",
            "mechanism_only",
        }:
            problems.append(f"{label}.scope is too broad")
        if not _text(record.get("rationale"), 20):
            problems.append(f"{label}.rationale must be substantive")
        evidence_claim_ids = record.get("evidence_claim_ids")
        if (
            not _unique_texts(evidence_claim_ids)
            or not set(evidence_claim_ids) <= set(cell["source_claim_ids"])
        ):
            problems.append(f"{label}.evidence_claim_ids do not resolve")
        else:
            for claim_id in evidence_claim_ids:
                if (
                    claim_index[claim_id]["read_status"]
                    not in DECISIVE_READ_STATUSES
                ):
                    problems.append(
                        f"{label} uses non-decisive claim {claim_id}"
                    )
        verdicts = record.get("property_verdicts")
        if not isinstance(verdicts, list) or not verdicts:
            problems.append(f"{label}.property_verdicts must be nonempty")
            verdicts = []
        expected_verdicts = {
            result["property_id"]: result
            for result in cell["requirement_results"]
        }
        seen_properties: list[str] = []
        for index, verdict in enumerate(verdicts):
            verdict_label = f"{label}.property_verdicts[{index}]"
            if not _exact_keys(
                verdict, PROPERTY_VERDICT_FIELDS, verdict_label, problems
            ):
                continue
            property_id = verdict.get("property_id")
            seen_properties.append(property_id)
            expected = expected_verdicts.get(property_id)
            if expected is None or any(
                verdict.get(field) != expected.get(field)
                for field in (
                    "operator",
                    "expected",
                    "actual",
                    "verdict",
                )
            ):
                problems.append(
                    f"{verdict_label} differs from the materialized cell"
                )
        if len(seen_properties) != len(set(seen_properties)):
            problems.append(f"{label}.property_verdicts repeat a property")
        if record.get("route_effect") != "none":
            problems.append(f"{label}.route_effect must remain none")
        if record.get("authorization") != "none":
            problems.append(f"{label}.authorization must remain none")
        if record.get("calibration") != "excluded_nonexperimental":
            problems.append(
                f"{label}.calibration must be excluded_nonexperimental"
            )
        if not _unique_texts(record.get("reopening_conditions")):
            problems.append(f"{label}.reopening_conditions must be nonempty")
        normalized.append(record)
    if len(ids) != len(set(ids)):
        problems.append("desk decision ids must be unique")
    if len(decided_cells) != len(set(decided_cells)):
        problems.append("a typed evidence cell has multiple desk decisions")
    required_decisions = {
        cell["cell_id"]
        for cell in cells
        if cell["status"] in {"decided_inapplicable", "decided_closed"}
    }
    missing = sorted(required_decisions - set(decided_cells))
    if missing:
        problems.append(f"decided cells lack desk decisions: {missing}")
    return problems, sorted(normalized, key=lambda item: item["decision_id"])


def build_state(
    policy: dict[str, Any],
    decisions: dict[str, Any],
    source_registry: dict[str, Any],
    desk_records: list[tuple[Path, dict[str, Any]]],
) -> tuple[list[str], dict[str, Any]]:
    problems = validate_policy(policy, decisions, source_registry)
    if problems:
        return problems, {}
    cells = materialize_cells(policy)
    desk_problems, desk_decisions = validate_desk_decisions(
        desk_records, cells, policy
    )
    problems.extend(desk_problems)
    counts = {
        "source_claims": len(policy["source_claims"]),
        "target_properties": len(policy["target_properties"]),
        "mechanisms": len(policy["mechanisms"]),
        "cells": len(cells),
        "open_cells": sum(cell["status"] == "open" for cell in cells),
        "property_resolution_cells": sum(
            cell["status"] == "property_resolution_required"
            for cell in cells
        ),
        "decided_inapplicable_cells": sum(
            cell["status"] == "decided_inapplicable" for cell in cells
        ),
        "decided_closed_cells": sum(
            cell["status"] == "decided_closed" for cell in cells
        ),
        "seed_eligible_cells": sum(cell["seed_eligible"] for cell in cells),
        "desk_decisions": len(desk_decisions),
    }
    literature_source_ids = {
        claim["source_id"]
        for claim in policy["source_claims"]
        if not claim["source_id"].startswith("repo:")
    }
    source_registry_identity = [
        {
            field: source.get(field)
            for field in (
                "id",
                "title",
                "authors",
                "year",
                "venue",
                "url",
                "doi",
            )
        }
        for source in source_registry.get("sources", [])
        if source.get("id") in literature_source_ids
    ]
    source_registry_identity.sort(key=lambda item: item["id"])
    state = {
        "schema_version": "0.1-generated",
        "evidence_id": policy["evidence_id"],
        "target_id": policy["target_id"],
        "source_hashes": {
            "policy_sha256": sha256_json(policy),
            "decision_substrate_sha256": sha256_json(decisions),
            "source_registry_identity_sha256": sha256_json(
                source_registry_identity
            ),
            "evidence_files_sha256": sha256_json(
                {
                    claim["evidence_path"]: sha256_file(
                        ROOT / claim["evidence_path"]
                    )
                    for claim in policy["source_claims"]
                    if claim["evidence_path"] is not None
                }
            ),
            "desk_decisions_sha256": sha256_json(desk_decisions),
        },
        "trust_boundary": policy["trust_boundary"],
        "counts": counts,
        "source_claims": sorted(
            policy["source_claims"], key=lambda item: item["id"]
        ),
        "target_properties": sorted(
            policy["target_properties"], key=lambda item: item["id"]
        ),
        "cost_quantities": sorted(
            policy["cost_quantities"], key=lambda item: item["id"]
        ),
        "barriers": sorted(policy["barriers"], key=lambda item: item["id"]),
        "cells": cells,
        "desk_decisions": desk_decisions,
        "authorization_boundary": (
            "Typed cells and desk decisions authorize nothing. Only an open "
            "cell may seed an untrusted proposal, and every later experiment "
            "and promotion gate remains separate."
        ),
    }
    return problems, state


def load_and_build() -> tuple[list[str], dict[str, Any]]:
    return build_state(
        load_json(POLICY_PATH),
        load_json(DECISIONS_PATH),
        load_json(SOURCE_REGISTRY_PATH),
        load_records(DESK_DECISIONS_DIR),
    )


def render_state(state: dict[str, Any]) -> str:
    return json.dumps(state, indent=2, ensure_ascii=False) + "\n"
