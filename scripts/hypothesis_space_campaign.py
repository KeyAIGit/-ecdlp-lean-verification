#!/usr/bin/env python3
"""Resumable, unique-coverage campaigns for the finite hypothesis space.

This module is deliberately operational.  It scans typed research-question
cells exactly once, retains bounded shard receipts, and refuses to interpret a
screening result as scientific evidence.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import os
import platform
import re
import statistics
import struct
import subprocess
import sys
import tarfile
import tempfile
import time
import traceback
from collections import Counter
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from hypothesis_funnel import (
    Operator,
    canonical_json_bytes,
    derive_warnings,
    known_pattern_rejections,
    load_base_questions,
    load_operators,
    metric_vector,
    normalized_text,
    sha256_json,
)
from hypothesis_space_funnel import (
    Challenge,
    FastStreamingMerkle,
    load_challenges,
    load_parent,
    load_policy as load_space_policy,
    reasons_to_mask,
    rejection_reasons,
    typed_anchor_digest,
    validate_injective_axes,
)
from hypothesis_space_run_ledger import (
    commit_is_ancestor_of_head,
    commit_is_ancestor_of_ref,
    git_file_bytes,
    github_push_before_sha,
    harness_digest_resolves,
    payload_digest,
    sha256_bytes,
)


ROOT = Path(__file__).resolve().parent.parent
POLICY_PATH = ROOT / "repo" / "HYPOTHESIS_SPACE_CAMPAIGN_V1.json"
STATE_PATH = ROOT / "data" / "hypothesis_space_campaign_state.json"
RECORD_DIR = ROOT / "experiments" / "engine" / "hypothesis_space_campaigns"
SCHEMA_PATH = ROOT / "experiments" / "engine" / "hypothesis_space_campaign.schema.json"
RECEIPT_SCHEMA_PATH = (
    ROOT / "experiments" / "engine" / "hypothesis_space_campaign_receipt.schema.json"
)
ERROR_SCHEMA_PATH = (
    ROOT / "experiments" / "engine" / "hypothesis_space_campaign_error.schema.json"
)
PROTECTED_BASE_REF = "refs/remotes/origin/main"
EVALUATOR_DEPENDENCY_PATHS = (
    "scripts/hypothesis_funnel.py",
    "scripts/hypothesis_space_funnel.py",
    "scripts/hypothesis_space_run_ledger.py",
    "scripts/hypothesis_space_campaign.py",
    "experiments/engine/hypothesis_space_campaign.schema.json",
    "experiments/engine/hypothesis_space_campaign_receipt.schema.json",
    "experiments/engine/hypothesis_space_campaign_error.schema.json",
)
HEX40_RE = re.compile(r"^[0-9a-f]{40}$")
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
CAMPAIGN_ID_RE = re.compile(r"^HSC-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{3}$")
HARNESS_RESOLUTION_RULE = (
    "The recorded SHA-256 must match the current path or the same path in "
    "reachable Git history."
)
FROZEN_REPLAY_PYTHON_FLAGS = ("-I", "-S")
LEAF_PREFIX = b"HQS-CELL-V2\x00"
PACKER = struct.Struct(">4BII7B")
SUPPORTED_SCHEMA_KEYWORDS = {
    "$schema",
    "$id",
    "$defs",
    "$ref",
    "title",
    "type",
    "const",
    "oneOf",
    "properties",
    "required",
    "additionalProperties",
    "items",
    "pattern",
    "format",
    "minLength",
    "minimum",
    "exclusiveMinimum",
    "minItems",
}


@dataclass(frozen=True)
class Universe:
    policy: dict[str, Any]
    parent_policy: dict[str, Any]
    bases: list[dict[str, str]]
    mechanisms: list[Operator]
    costs: list[Operator]
    tests: list[Operator]
    challenges: list[Challenge]
    anchor_digests: list[bytes]
    base_warning_masks: list[int]
    base_pattern_masks: list[list[int]]
    type_combos: dict[str, list[tuple[int, int, int, int, int, tuple[int, ...]]]]
    ordered_reasons: list[str]
    expected: int
    combinations_per_base: int


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected an object")
    return value


def rendered_json(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=True, indent=2, allow_nan=False) + "\n"


def _schema_type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    raise ValueError(f"unsupported local JSON Schema type: {expected}")


def schema_definition_problems(
    schema: dict[str, Any], *, location: str = "$"
) -> list[str]:
    problems = [
        f"{location}: unsupported schema keyword {key}"
        for key in sorted(set(schema) - SUPPORTED_SCHEMA_KEYWORDS)
    ]
    for container in ("$defs", "properties"):
        children = schema.get(container, {})
        if isinstance(children, dict):
            for key, child in children.items():
                if isinstance(child, dict):
                    problems.extend(
                        schema_definition_problems(
                            child, location=f"{location}.{container}.{key}"
                        )
                    )
    branches = schema.get("oneOf", [])
    if isinstance(branches, list):
        for index, branch in enumerate(branches):
            if isinstance(branch, dict):
                problems.extend(
                    schema_definition_problems(
                        branch, location=f"{location}.oneOf[{index}]"
                    )
                )
    for key in ("items", "additionalProperties"):
        child = schema.get(key)
        if isinstance(child, dict):
            problems.extend(
                schema_definition_problems(child, location=f"{location}.{key}")
            )
    return problems


def validate_schema_value(
    value: Any,
    schema: dict[str, Any],
    *,
    root_schema: dict[str, Any] | None = None,
    location: str = "$",
) -> list[str]:
    """Validate the strict subset used by the three campaign schemas.

    Keeping this validator local avoids an undeclared CI dependency while making
    `additionalProperties: false` and the epistemic constants executable gates.
    """

    root = schema if root_schema is None else root_schema
    if "$ref" in schema:
        reference = schema["$ref"]
        if not isinstance(reference, str) or not reference.startswith("#/"):
            return [f"{location}: unsupported schema reference"]
        target: Any = root
        for component in reference[2:].split("/"):
            if not isinstance(target, dict) or component not in target:
                return [f"{location}: unresolved schema reference {reference}"]
            target = target[component]
        if not isinstance(target, dict):
            return [f"{location}: schema reference is not an object"]
        return validate_schema_value(
            value, target, root_schema=root, location=location
        )

    if "oneOf" in schema:
        branches = [
            validate_schema_value(value, branch, root_schema=root, location=location)
            for branch in schema["oneOf"]
        ]
        if sum(not branch for branch in branches) != 1:
            return [f"{location}: value does not match exactly one schema branch"]
        return []

    expected_type = schema.get("type")
    if expected_type is not None:
        expected_types = [expected_type] if isinstance(expected_type, str) else expected_type
        if not isinstance(expected_types, list) or not any(
            isinstance(item, str) and _schema_type_matches(value, item)
            for item in expected_types
        ):
            return [f"{location}: expected schema type {expected_type}"]

    problems: list[str] = []
    if "const" in schema and value != schema["const"]:
        problems.append(f"{location}: value differs from schema constant")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            problems.append(f"{location}: string is too short")
        pattern = schema.get("pattern")
        if isinstance(pattern, str) and re.fullmatch(pattern, value) is None:
            problems.append(f"{location}: string does not match schema pattern")
        value_format = schema.get("format")
        if value_format == "date-time":
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
                if parsed.tzinfo is None:
                    raise ValueError("timezone is required")
            except ValueError:
                problems.append(f"{location}: string is not an RFC3339 date-time")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            problems.append(f"{location}: number is below schema minimum")
        if "exclusiveMinimum" in schema and value <= schema["exclusiveMinimum"]:
            problems.append(f"{location}: number is not above schema minimum")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            problems.append(f"{location}: array has too few items")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                problems.extend(
                    validate_schema_value(
                        item,
                        item_schema,
                        root_schema=root,
                        location=f"{location}[{index}]",
                    )
                )
    if isinstance(value, dict):
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        if isinstance(required, list):
            for key in required:
                if key not in value:
                    problems.append(f"{location}: missing required property {key}")
        if schema.get("additionalProperties") is False and isinstance(properties, dict):
            for key in value:
                if key not in properties:
                    problems.append(f"{location}: unexpected property {key}")
        additional_schema = schema.get("additionalProperties")
        if isinstance(additional_schema, dict) and isinstance(properties, dict):
            for key, child in value.items():
                if key not in properties:
                    problems.extend(
                        validate_schema_value(
                            child,
                            additional_schema,
                            root_schema=root,
                            location=f"{location}.{key}",
                        )
                    )
        if isinstance(properties, dict):
            for key, child_schema in properties.items():
                if key in value and isinstance(child_schema, dict):
                    problems.extend(
                        validate_schema_value(
                            value[key],
                            child_schema,
                            root_schema=root,
                            location=f"{location}.{key}",
                        )
                    )
    return problems


def schema_problems(value: Any, path: Path) -> list[str]:
    schema = read_json(path)
    return schema_definition_problems(schema) + validate_schema_value(value, schema)


def validate_policy(policy: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    required_policy = {
        "schema_version",
        "ledger_id",
        "status",
        "constitution_source",
        "protected_base_ref",
        "subject",
        "campaign_contract",
        "retention_contract",
        "epistemic_contract",
        "immutable_record_anchors",
    }
    if set(policy) != required_policy:
        problems.append("campaign policy top-level shape drifted")
    if policy.get("schema_version") != "1.0":
        problems.append("unsupported campaign policy schema")
    if policy.get("status") != "accepted_non_scientific_operational_memory":
        problems.append("campaign policy status drifted")
    if policy.get("protected_base_ref") != PROTECTED_BASE_REF:
        problems.append("protected_base_ref must be the canonical origin/main ref")
    subject = policy.get("subject", {})
    required_subject = {
        "space_policy_path",
        "space_state_path",
        "space_map_path",
        "runner_path",
    }
    if not isinstance(subject, dict) or set(subject) != required_subject:
        problems.append("campaign subject shape drifted")
    contract = policy.get("campaign_contract", {})
    if not isinstance(contract, dict):
        problems.append("campaign_contract must be an object")
    else:
        shard_size = contract.get("default_shard_size")
        if (
            not isinstance(shard_size, int)
            or shard_size < 1
            or shard_size & (shard_size - 1)
        ):
            problems.append("default_shard_size must be a power of two")
        if contract.get("repeat_policy") != "stop_at_finite_universe_exhaustion":
            problems.append("repeat_policy must stop at finite-universe exhaustion")
        if contract.get("identity") != "contiguous_mixed_radix_ordinal_v1":
            problems.append("campaign identity contract drifted")
    boundary = policy.get("epistemic_contract", {})
    required_false = {
        "screening_rejection_is_falsification": False,
        "campaign_is_scientific_outcome": False,
        "campaign_is_ranker_training_data": False,
        "campaign_is_brier_calibration_data": False,
        "campaign_can_authorize": False,
        "campaign_can_recommend": False,
        "campaign_can_promote_route": False,
    }
    required_boundary_keys = set(required_false) | {
        "cold_cell",
        "warm_cell",
        "scientific_feedback_paths",
    }
    if (
        not isinstance(boundary, dict)
        or set(boundary) != required_boundary_keys
        or any(boundary.get(key) is not value for key, value in required_false.items())
    ):
        problems.append("campaign epistemic boundary drifted")
    anchors = policy.get("immutable_record_anchors")
    if not isinstance(anchors, list):
        problems.append("immutable_record_anchors must be an array")
    else:
        ids: set[str] = set()
        paths: set[str] = set()
        for index, anchor in enumerate(anchors):
            if not isinstance(anchor, dict) or set(anchor) != {
                "campaign_id",
                "path",
                "sha256",
            }:
                problems.append(f"campaign anchor {index} has invalid shape")
                continue
            if anchor["campaign_id"] in ids or anchor["path"] in paths:
                problems.append("campaign anchors must be unique")
            ids.add(anchor["campaign_id"])
            paths.add(anchor["path"])
            if not HEX64_RE.fullmatch(str(anchor["sha256"])):
                problems.append(f"campaign anchor {index} has invalid SHA-256")
    return problems


def load_policy() -> dict[str, Any]:
    policy = read_json(POLICY_PATH)
    problems = validate_policy(policy)
    if problems:
        raise ValueError("; ".join(problems))
    return policy


def operator_semantic_digest(role: str, operator: Operator) -> str:
    return sha256_json(
        {
            "role": role,
            "label": normalized_text(operator.label),
            "compatible_types": sorted(operator.compatible_types),
            "capabilities": sorted(operator.capabilities),
            "dimensions": dict(sorted(operator.dimensions.items())),
        }
    )


def challenge_semantic_digest(challenge: Challenge) -> str:
    return sha256_json(
        {
            "role": "challenge",
            "label": normalized_text(challenge.label),
            "compatible_types": sorted(challenge.compatible_types),
        }
    )


def assert_semantic_axis_uniqueness(
    mechanisms: list[Operator],
    costs: list[Operator],
    tests: list[Operator],
    challenges: list[Challenge],
) -> None:
    collections = {
        "mechanism": [operator_semantic_digest("mechanism", item) for item in mechanisms],
        "cost": [operator_semantic_digest("cost", item) for item in costs],
        "test": [operator_semantic_digest("test", item) for item in tests],
        "challenge": [challenge_semantic_digest(item) for item in challenges],
    }
    for name, digests in collections.items():
        if len(digests) != len(set(digests)):
            raise ValueError(f"{name} axis contains exact semantic duplicates")


def prepare_universe() -> Universe:
    space_policy = load_space_policy()
    parent_policy, _ = load_parent(space_policy)
    bases = sorted(load_base_questions(parent_policy), key=lambda item: item["id"])
    mechanisms = sorted(
        load_operators(parent_policy["mechanism_obligations"], "mechanisms"),
        key=lambda item: item.id,
    )
    costs = sorted(
        load_operators(parent_policy["cost_bridges"], "cost bridges"),
        key=lambda item: item.id,
    )
    tests = sorted(
        load_operators(parent_policy["decisive_tests"], "decisive tests"),
        key=lambda item: item.id,
    )
    challenges = load_challenges(space_policy)
    anchor_digests = validate_injective_axes(
        bases, mechanisms, costs, tests, challenges
    )
    assert_semantic_axis_uniqueness(mechanisms, costs, tests, challenges)
    dimensions = space_policy["portfolio"]["dimension_names"]
    if dimensions != parent_policy["portfolio"]["dimension_names"]:
        raise ValueError("campaign dimensions drifted from the frozen space")
    expected = (
        len(bases) * len(mechanisms) * len(costs) * len(tests) * len(challenges)
    )
    if expected != space_policy["expansion"]["expected_signatures"]:
        raise ValueError("campaign universe count drifted from the frozen space")

    ordered_reasons = space_policy["screening"]["hard_rejections"]
    reason_bits = {reason: index for index, reason in enumerate(ordered_reasons)}
    warning_names = space_policy["screening"]["warnings"]
    warning_bits = {warning: index for index, warning in enumerate(warning_names)}
    base_warning_masks: list[int] = []
    base_pattern_masks: list[list[int]] = []
    for base in bases:
        warnings = set(derive_warnings(base)) | {
            "challenge_unresolved",
            "typed_identity_not_semantic_novelty",
        }
        unknown = warnings - set(warning_bits)
        if unknown:
            raise ValueError(f"unregistered campaign warnings: {sorted(unknown)}")
        base_warning_masks.append(sum(1 << warning_bits[item] for item in warnings))
        base_pattern_masks.append(
            [
                reasons_to_mask(
                    known_pattern_rejections(base, mechanism, parent_policy),
                    reason_bits,
                )
                for mechanism in mechanisms
            ]
        )

    type_combos: dict[
        str, list[tuple[int, int, int, int, int, tuple[int, ...]]]
    ] = {}
    for kind in sorted({base["type"] for base in bases}):
        combos: list[tuple[int, int, int, int, int, tuple[int, ...]]] = []
        for mi, mechanism in enumerate(mechanisms):
            for ci, cost in enumerate(costs):
                for ti, test in enumerate(tests):
                    vector = metric_vector(mechanism, cost, test, dimensions)
                    dims = tuple(vector[name] for name in dimensions)
                    if any(not 0 <= value <= 255 for value in dims):
                        raise ValueError("campaign dimension exceeds binary leaf format")
                    for gi, challenge in enumerate(challenges):
                        static_mask = reasons_to_mask(
                            rejection_reasons(
                                kind,
                                mechanism,
                                cost,
                                test,
                                challenge,
                                parent_policy,
                            ),
                            reason_bits,
                        )
                        combos.append((mi, ci, ti, gi, static_mask, dims))
        type_combos[kind] = combos

    combinations_per_base = (
        len(mechanisms) * len(costs) * len(tests) * len(challenges)
    )
    return Universe(
        policy=space_policy,
        parent_policy=parent_policy,
        bases=bases,
        mechanisms=mechanisms,
        costs=costs,
        tests=tests,
        challenges=challenges,
        anchor_digests=anchor_digests,
        base_warning_masks=base_warning_masks,
        base_pattern_masks=base_pattern_masks,
        type_combos=type_combos,
        ordered_reasons=ordered_reasons,
        expected=expected,
        combinations_per_base=combinations_per_base,
    )


def universe_manifest(universe: Universe) -> dict[str, Any]:
    """Return the pre-evaluation identity of the finite typed grammar."""
    axis_items: list[dict[str, Any]] = [
        {
            "name": "base_question",
            "radix": len(universe.bases),
            "ordered_item_ids": [item["id"] for item in universe.bases],
            "ordered_semantic_sha256": [
                typed_anchor_digest(item).hex() for item in universe.bases
            ],
        },
        {
            "name": "mechanism_obligation",
            "radix": len(universe.mechanisms),
            "ordered_item_ids": [item.id for item in universe.mechanisms],
            "ordered_semantic_sha256": [
                operator_semantic_digest("mechanism", item)
                for item in universe.mechanisms
            ],
        },
        {
            "name": "cost_bridge",
            "radix": len(universe.costs),
            "ordered_item_ids": [item.id for item in universe.costs],
            "ordered_semantic_sha256": [
                operator_semantic_digest("cost", item) for item in universe.costs
            ],
        },
        {
            "name": "decisive_test",
            "radix": len(universe.tests),
            "ordered_item_ids": [item.id for item in universe.tests],
            "ordered_semantic_sha256": [
                operator_semantic_digest("test", item) for item in universe.tests
            ],
        },
        {
            "name": "adversarial_challenge",
            "radix": len(universe.challenges),
            "ordered_item_ids": [item.id for item in universe.challenges],
            "ordered_semantic_sha256": [
                challenge_semantic_digest(item) for item in universe.challenges
            ],
        },
    ]
    projection = {
        "schema_version": "1.0-universe",
        "space_id": universe.policy["space_id"],
        "axis_order": universe.policy["expansion"]["axis_order"],
        "axes": axis_items,
        "cardinality": universe.expected,
        "ordinal_codec": "zero-based-big-endian-mixed-radix-v1",
        "cell_leaf_codec": "HQS-CELL-V2+struct->4BII7B",
        "ordered_rejection_reasons": universe.ordered_reasons,
        "threat_model": universe.parent_policy["safety"]["primary_threat_model"],
        "input_pool_path": universe.parent_policy["input_pool"]["path"],
        "input_pool_canonical_lf_sha256": universe.parent_policy["input_pool"][
            "sha256"
        ],
        "exact_semantic_axis_duplicate_count": 0,
        "semantic_novelty_proved": False,
    }
    return {
        **projection,
        "universe_id_sha256": sha256_json(projection),
    }


def evaluation_manifest(
    universe_id: str,
    canonical_state: dict[str, Any],
    *,
    dependency_sha256: dict[str, str],
) -> dict[str, Any]:
    bindings = canonical_state["source_bindings"]
    if set(dependency_sha256) != set(EVALUATOR_DEPENDENCY_PATHS):
        raise ValueError("evaluation dependency closure is incomplete")
    if not all(HEX64_RE.fullmatch(value) for value in dependency_sha256.values()):
        raise ValueError("evaluation dependency closure contains an invalid digest")
    ordered_dependencies = dict(sorted(dependency_sha256.items()))
    projection = {
        "schema_version": "1.0-evaluation",
        "universe_id_sha256": universe_id,
        "generation_policy_sha256": bindings["generation_policy_sha256"],
        "evidence_snapshot_sha256": bindings["evidence_snapshot_sha256"],
        "parent_generation_policy_sha256": bindings[
            "parent_generation_policy_sha256"
        ],
        "parent_merkle_root_sha256": bindings["parent_merkle_root_sha256"],
        "evaluator_contract": "hypothesis-space-structural-screen-v2",
        "source_runner_sha256": ordered_dependencies[
            "scripts/hypothesis_space_funnel.py"
        ],
        "campaign_evaluator_sha256": ordered_dependencies[
            "scripts/hypothesis_space_campaign.py"
        ],
        "dependency_sha256": ordered_dependencies,
        "dependency_closure_sha256": sha256_json(ordered_dependencies),
    }
    return {
        **projection,
        "evaluation_id_sha256": sha256_json(projection),
    }


def current_evaluator_dependency_digests() -> dict[str, str]:
    return {
        relative: sha256_bytes((ROOT / relative).read_bytes())
        for relative in EVALUATOR_DEPENDENCY_PATHS
    }


def source_evaluator_dependency_digests(source_commit: str) -> dict[str, str]:
    return {
        relative: sha256_bytes(git_file_bytes(source_commit, relative))
        for relative in EVALUATOR_DEPENDENCY_PATHS
    }


def fixed_shard_ranges(cardinality: int, shard_size: int) -> list[tuple[int, int]]:
    if shard_size < 1 or shard_size & (shard_size - 1):
        raise ValueError("official campaign shard size must be a power of two")
    return [
        (start, min(start + shard_size, cardinality))
        for start in range(0, cardinality, shard_size)
    ]


def rejection_histograms_from_masks(
    mask_counts: dict[str, int] | Counter[str], ordered_reasons: list[str]
) -> tuple[dict[str, int], dict[str, int]]:
    all_reasons: Counter[str] = Counter()
    primary: Counter[str] = Counter()
    for raw_mask, count in mask_counts.items():
        mask = int(raw_mask)
        if mask == 0:
            continue
        first: str | None = None
        for bit, reason in enumerate(ordered_reasons):
            if mask & (1 << bit):
                all_reasons[reason] += count
                first = first or reason
        if first is not None:
            primary[first] += count
    return dict(sorted(all_reasons.items())), dict(sorted(primary.items()))


def restore_merkle(raw: list[str | None], count: int) -> FastStreamingMerkle:
    if not isinstance(count, int) or count < 0:
        raise ValueError("checkpoint Merkle count is invalid")
    merkle = FastStreamingMerkle()
    merkle.frontier = [None if item is None else bytes.fromhex(item) for item in raw]
    merkle.count = count
    for height, item in enumerate(merkle.frontier):
        expected_present = bool(count & (1 << height))
        if (item is not None) != expected_present:
            raise ValueError("checkpoint Merkle frontier is inconsistent with count")
        if item is not None and len(item) != 32:
            raise ValueError("checkpoint Merkle node has invalid width")
    if count and len(merkle.frontier) != count.bit_length():
        raise ValueError("checkpoint Merkle frontier has invalid height")
    return merkle


def scan_shard(
    universe: Universe,
    start: int,
    end: int,
    global_merkle: FastStreamingMerkle | None = None,
) -> tuple[dict[str, Any], Counter[int], Counter[str]]:
    if not 0 <= start < end <= universe.expected:
        raise ValueError("campaign shard range is invalid")
    if global_merkle is not None and global_merkle.count != start:
        raise ValueError("campaign shard is not contiguous with the global frontier")
    local_merkle = FastStreamingMerkle()
    mask_counts: Counter[int] = Counter()
    type_counts: Counter[str] = Counter()
    cold = 0
    warm = 0
    first_leaf: str | None = None
    last_leaf: str | None = None
    started = time.perf_counter_ns()
    for ordinal in range(start, end):
        bi, combo_index = divmod(ordinal, universe.combinations_per_base)
        base = universe.bases[bi]
        mi, ci, ti, gi, static_mask, dims = universe.type_combos[
            base["type"]
        ][combo_index]
        mask = static_mask | universe.base_pattern_masks[bi][mi]
        cell = (
            LEAF_PREFIX
            + universe.anchor_digests[bi]
            + PACKER.pack(
                mi,
                ci,
                ti,
                gi,
                mask,
                universe.base_warning_masks[bi],
                *dims,
            )
        )
        leaf_hash = hashlib.sha256(b"\x00" + cell).digest()
        local_merkle.add_leaf_hash(leaf_hash)
        if global_merkle is not None:
            global_merkle.add_leaf_hash(leaf_hash)
        leaf_hex = leaf_hash.hex()
        first_leaf = first_leaf or leaf_hex
        last_leaf = leaf_hex
        mask_counts[mask] += 1
        type_counts[base["type"]] += 1
        if mask:
            cold += 1
        else:
            warm += 1
    elapsed_ns = time.perf_counter_ns() - started
    count = end - start
    receipt = {
        "shard_ordinal": 0,
        "start_ordinal": start,
        "end_ordinal_exclusive": end,
        "unique_cells": count,
        "cold": cold,
        "warm": warm,
        "typed_duplicates": 0,
        "pipeline_errors": 0,
        "range_merkle_root_sha256": local_merkle.root_bytes().hex(),
        "range_frontier": [
            {
                "height": height,
                "leaf_count": 1 << height,
                "sha256": item.hex(),
            }
            for height, item in reversed(list(enumerate(local_merkle.frontier)))
            if item is not None
        ],
        "first_leaf_sha256": first_leaf,
        "last_leaf_sha256": last_leaf,
        "elapsed_ns": elapsed_ns,
        "signatures_per_minute": round(count * 60_000_000_000 / elapsed_ns),
    }
    return receipt, mask_counts, type_counts


def append_perfect_subtree(
    merkle: FastStreamingMerkle, node_hash: bytes, height: int
) -> None:
    leaf_count = 1 << height
    if merkle.count % leaf_count:
        raise ValueError("range frontier is not aligned to the global ordinal")
    index = merkle.count >> height
    carry = node_hash
    level = height
    while index & 1:
        if level >= len(merkle.frontier) or merkle.frontier[level] is None:
            raise ValueError("range frontier cannot attach to the global frontier")
        carry = FastStreamingMerkle.node_hash(merkle.frontier[level], carry)
        merkle.frontier[level] = None
        index >>= 1
        level += 1
    while len(merkle.frontier) <= level:
        merkle.frontier.append(None)
    if merkle.frontier[level] is not None:
        raise ValueError("range frontier collides with an occupied node")
    merkle.frontier[level] = carry
    merkle.count += leaf_count


def merkle_from_range_receipts(receipts: list[dict[str, Any]]) -> FastStreamingMerkle:
    merkle = FastStreamingMerkle()
    for receipt in receipts:
        if receipt["start_ordinal"] != merkle.count:
            raise ValueError("receipt ranges overlap or contain a gap")
        for node in receipt["range_frontier"]:
            append_perfect_subtree(
                merkle, bytes.fromhex(node["sha256"]), node["height"]
            )
        if merkle.count != receipt["end_ordinal_exclusive"]:
            raise ValueError("receipt range frontier has the wrong leaf count")
    return merkle


def immutable_create_json(path: Path, value: dict[str, Any]) -> None:
    """Create one durable JSON object without ever replacing an existing path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    payload = rendered_json(value).encode("utf-8")
    try:
        with temporary.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def campaign_directory(campaign_id: str) -> Path:
    return RECORD_DIR / campaign_id


def ensure_evaluation_claim(
    *,
    campaign_id: str,
    source_commit: str,
    universe_id: str,
    evaluation_id: str,
) -> Path:
    """Reserve one evaluation for one campaign before any shard is processed."""

    claim = {
        "schema_version": "1.0-evaluation-claim",
        "record_kind": "pre_anchor_evaluation_reservation",
        "campaign_id": campaign_id,
        "source_commit": source_commit,
        "universe_id_sha256": universe_id,
        "evaluation_id_sha256": evaluation_id,
        "assurance": "create_only_local_reservation_until_git_anchored",
        "pre_anchor_deletion_resistant": False,
    }
    claim["claim_payload_sha256"] = sha256_json(claim)
    path = RECORD_DIR / "_evaluation_claims" / f"{evaluation_id}.json"
    if path.exists():
        existing = read_json(path)
        if existing != claim:
            raise ValueError("evaluation is already reserved by another campaign")
        return path
    try:
        immutable_create_json(path, claim)
    except FileExistsError:
        existing = read_json(path)
        if existing != claim:
            raise ValueError("evaluation is already reserved by another campaign")
    return path


def receipt_payload_digest(receipt: dict[str, Any]) -> str:
    payload = copy.deepcopy(receipt)
    payload.pop("receipt_payload_sha256", None)
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def create_shard_receipt(
    universe: Universe,
    universe_meta: dict[str, Any],
    evaluation_meta: dict[str, Any],
    *,
    campaign_id: str,
    shard_index: int,
    start: int,
    end: int,
    previous_receipt_file_sha256: str | None,
) -> dict[str, Any]:
    scanned, mask_counts, type_counts = scan_shard(universe, start, end)
    scanned["shard_ordinal"] = shard_index
    receipt: dict[str, Any] = {
        "schema_version": "1.0-receipt",
        "record_kind": "finite_unique_coverage_shard",
        "campaign_id": campaign_id,
        "universe_id_sha256": universe_meta["universe_id_sha256"],
        "evaluation_id_sha256": evaluation_meta["evaluation_id_sha256"],
        "shard_index": shard_index,
        "start_ordinal": start,
        "end_ordinal_exclusive": end,
        "previous_receipt_file_sha256": previous_receipt_file_sha256,
        "range_merkle_root_sha256": scanned["range_merkle_root_sha256"],
        "range_frontier": scanned["range_frontier"],
        "first_leaf_sha256": scanned["first_leaf_sha256"],
        "last_leaf_sha256": scanned["last_leaf_sha256"],
        "aggregates": {
            "cold": scanned["cold"],
            "warm": scanned["warm"],
            "type_counts": dict(sorted(type_counts.items())),
            "mask_counts": {
                str(key): value for key, value in sorted(mask_counts.items())
            },
        },
        "physical_evaluations": end - start,
        "unique_evaluation_cells_added": end - start,
        "duplicate_evaluations": 0,
        "elapsed_ns": scanned["elapsed_ns"],
        "signatures_per_minute": scanned["signatures_per_minute"],
        "harness": {
            "path": "scripts/hypothesis_space_campaign.py",
            "sha256": sha256_bytes(Path(__file__).read_bytes()),
            "resolution_rule": HARNESS_RESOLUTION_RULE,
        },
    }
    receipt["receipt_payload_sha256"] = receipt_payload_digest(receipt)
    return receipt


def validate_shard_receipt(
    receipt: dict[str, Any],
    universe_meta: dict[str, Any],
    evaluation_meta: dict[str, Any],
    *,
    campaign_id: str,
    shard_index: int,
    start: int,
    end: int,
    previous_receipt_file_sha256: str | None,
) -> list[str]:
    problems: list[str] = [
        f"receipt schema: {item}"
        for item in schema_problems(receipt, RECEIPT_SCHEMA_PATH)
    ]
    required = {
        "schema_version",
        "record_kind",
        "campaign_id",
        "universe_id_sha256",
        "evaluation_id_sha256",
        "shard_index",
        "start_ordinal",
        "end_ordinal_exclusive",
        "previous_receipt_file_sha256",
        "range_merkle_root_sha256",
        "range_frontier",
        "first_leaf_sha256",
        "last_leaf_sha256",
        "aggregates",
        "physical_evaluations",
        "unique_evaluation_cells_added",
        "duplicate_evaluations",
        "elapsed_ns",
        "signatures_per_minute",
        "harness",
        "receipt_payload_sha256",
    }
    if set(receipt) != required:
        problems.append("receipt has unexpected top-level shape")
        return problems
    expected_identity = {
        "schema_version": "1.0-receipt",
        "record_kind": "finite_unique_coverage_shard",
        "campaign_id": campaign_id,
        "universe_id_sha256": universe_meta["universe_id_sha256"],
        "evaluation_id_sha256": evaluation_meta["evaluation_id_sha256"],
        "shard_index": shard_index,
        "start_ordinal": start,
        "end_ordinal_exclusive": end,
        "previous_receipt_file_sha256": previous_receipt_file_sha256,
    }
    for key, expected in expected_identity.items():
        if receipt.get(key) != expected:
            problems.append(f"receipt {key} drifted")
    if receipt.get("receipt_payload_sha256") != receipt_payload_digest(receipt):
        problems.append("receipt payload digest mismatch")
    count = end - start
    aggregates = receipt.get("aggregates", {})
    if not isinstance(aggregates, dict) or set(aggregates) != {
        "cold",
        "warm",
        "type_counts",
        "mask_counts",
    }:
        problems.append("receipt aggregates have invalid shape")
    else:
        if aggregates.get("cold", 0) + aggregates.get("warm", 0) != count:
            problems.append("receipt cold/warm counts do not cover its range")
        if sum(aggregates.get("type_counts", {}).values()) != count:
            problems.append("receipt type counts do not cover its range")
        if sum(aggregates.get("mask_counts", {}).values()) != count:
            problems.append("receipt mask counts do not cover its range")
    if (
        receipt.get("physical_evaluations") != count
        or receipt.get("unique_evaluation_cells_added") != count
        or receipt.get("duplicate_evaluations") != 0
    ):
        problems.append("receipt evaluation counts are invalid")
    elapsed_ns = receipt.get("elapsed_ns")
    if not isinstance(elapsed_ns, int) or elapsed_ns <= 0:
        problems.append("receipt elapsed_ns is invalid")
    elif receipt.get("signatures_per_minute") != round(
        count * 60_000_000_000 / elapsed_ns
    ):
        problems.append("receipt throughput does not match elapsed time")
    frontier = receipt.get("range_frontier")
    if not isinstance(frontier, list) or not frontier:
        problems.append("receipt range frontier is missing")
    else:
        raw: list[str | None] = [None] * count.bit_length()
        total = 0
        prior_height = count.bit_length()
        for node in frontier:
            if not isinstance(node, dict) or set(node) != {
                "height",
                "leaf_count",
                "sha256",
            }:
                problems.append("receipt range frontier node is invalid")
                continue
            height = node["height"]
            if (
                not isinstance(height, int)
                or not 0 <= height < len(raw)
                or height >= prior_height
                or node["leaf_count"] != 1 << height
                or not isinstance(node["sha256"], str)
                or not HEX64_RE.fullmatch(node["sha256"])
            ):
                problems.append("receipt range frontier node is inconsistent")
                continue
            prior_height = height
            raw[height] = node["sha256"]
            total += 1 << height
        if total != count:
            problems.append("receipt range frontier leaf count drifted")
        else:
            try:
                local = restore_merkle(raw, count)
                if local.root_bytes().hex() != receipt.get(
                    "range_merkle_root_sha256"
                ):
                    problems.append("receipt range root does not match its frontier")
            except ValueError as exc:
                problems.append(f"receipt range frontier is invalid: {exc}")
    for key in ("range_merkle_root_sha256", "first_leaf_sha256", "last_leaf_sha256"):
        if not isinstance(receipt.get(key), str) or not HEX64_RE.fullmatch(receipt[key]):
            problems.append(f"receipt {key} is invalid")
    harness = receipt.get("harness", {})
    if not isinstance(harness, dict) or set(harness) != {
        "path",
        "sha256",
        "resolution_rule",
    }:
        problems.append("receipt harness has invalid shape")
    else:
        harness_path = harness.get("path")
        harness_sha = harness.get("sha256")
        if (
            harness.get("resolution_rule") != HARNESS_RESOLUTION_RULE
            or not isinstance(harness_path, str)
            or not isinstance(harness_sha, str)
            or not HEX64_RE.fullmatch(harness_sha)
            or not harness_digest_resolves(harness_path, harness_sha)
        ):
            problems.append("receipt harness digest does not resolve")
        if harness_path != "scripts/hypothesis_space_campaign.py":
            problems.append("receipt harness path does not bind the campaign evaluator")
        if harness_sha != evaluation_meta.get("campaign_evaluator_sha256"):
            problems.append("receipt harness digest does not bind the evaluation")
    return problems


def error_payload_digest(event: dict[str, Any]) -> str:
    payload = copy.deepcopy(event)
    payload.pop("error_payload_sha256", None)
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def validate_error_event(
    event: dict[str, Any],
    *,
    campaign_id: str,
    universe_id: str,
    evaluation_id: str,
    sequence: int,
    previous_error_file_sha256: str | None,
) -> list[str]:
    problems: list[str] = [
        f"error schema: {item}" for item in schema_problems(event, ERROR_SCHEMA_PATH)
    ]
    required = {
        "schema_version",
        "record_kind",
        "error_id",
        "campaign_id",
        "universe_id_sha256",
        "evaluation_id_sha256",
        "shard_index",
        "start_ordinal",
        "stage",
        "exception_class",
        "message_excerpt",
        "traceback_excerpt",
        "message_truncated",
        "traceback_truncated",
        "message_sha256",
        "traceback_sha256",
        "occurred_at_utc",
        "retryable",
        "retry_class",
        "disposition",
        "previous_error_file_sha256",
        "error_payload_sha256",
    }
    if set(event) != required:
        return ["error event has unexpected top-level shape"]
    expected = {
        "schema_version": "1.0-error",
        "record_kind": "hypothesis_space_campaign_error",
        "error_id": f"{campaign_id}-ERR-{sequence:04d}",
        "campaign_id": campaign_id,
        "universe_id_sha256": universe_id,
        "evaluation_id_sha256": evaluation_id,
        "disposition": "retained_operational_failure",
        "previous_error_file_sha256": previous_error_file_sha256,
    }
    for key, value in expected.items():
        if event.get(key) != value:
            problems.append(f"error event {key} drifted")
    for key in ("message_sha256", "traceback_sha256", "error_payload_sha256"):
        if not isinstance(event.get(key), str) or not HEX64_RE.fullmatch(event[key]):
            problems.append(f"error event {key} is invalid")
    for key in ("shard_index", "start_ordinal"):
        value = event.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            problems.append(f"error event {key} is invalid")
    for key in (
        "stage",
        "exception_class",
        "retry_class",
    ):
        if not isinstance(event.get(key), str) or not event[key].strip():
            problems.append(f"error event {key} is invalid")
    if not isinstance(event.get("retryable"), bool):
        problems.append("error event retryable flag is invalid")
    for key in ("message_truncated", "traceback_truncated"):
        if not isinstance(event.get(key), bool):
            problems.append(f"error event {key} flag is invalid")
    for key in ("message_excerpt", "traceback_excerpt"):
        if not isinstance(event.get(key), str):
            problems.append(f"error event {key} is invalid")
    if event.get("message_sha256") != hashlib.sha256(
        event.get("message_excerpt", "").encode("utf-8")
    ).hexdigest() and event.get("message_truncated") is False:
        problems.append("untruncated error message digest mismatch")
    if event.get("traceback_sha256") != hashlib.sha256(
        event.get("traceback_excerpt", "").encode("utf-8")
    ).hexdigest() and event.get("traceback_truncated") is False:
        problems.append("untruncated traceback digest mismatch")
    try:
        datetime.fromisoformat(str(event.get("occurred_at_utc")).replace("Z", "+00:00"))
    except ValueError:
        problems.append("error event timestamp is invalid")
    if event.get("error_payload_sha256") != error_payload_digest(event):
        problems.append("error event payload digest mismatch")
    return problems


def validate_campaign_error_chain(
    campaign_id: str, universe_id: str, evaluation_id: str
) -> tuple[list[Path], list[str]]:
    directory = campaign_directory(campaign_id) / "errors"
    paths = sorted(directory.glob("*.json")) if directory.exists() else []
    problems: list[str] = []
    previous: str | None = None
    for sequence, path in enumerate(paths, start=1):
        if path.name != f"{sequence:04d}.json":
            problems.append("campaign error files are not a contiguous sequence")
            continue
        try:
            event = read_json(path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            problems.append(f"campaign error {sequence} cannot be read: {exc}")
            continue
        problems.extend(
            f"campaign error {sequence}: {item}"
            for item in validate_error_event(
                event,
                campaign_id=campaign_id,
                universe_id=universe_id,
                evaluation_id=evaluation_id,
                sequence=sequence,
                previous_error_file_sha256=previous,
            )
        )
        previous = sha256_bytes(path.read_bytes())
    return paths, problems


def retain_error_event(
    campaign_id: str,
    evaluation_id: str,
    universe_id: str,
    *,
    shard_index: int,
    start_ordinal: int,
    stage: str,
    error: BaseException,
) -> Path:
    directory = campaign_directory(campaign_id) / "errors"
    existing = sorted(directory.glob("*.json")) if directory.exists() else []
    sequence = len(existing) + 1
    prior = sha256_bytes(existing[-1].read_bytes()) if existing else None
    message = str(error)
    trace = "".join(traceback.format_exception(error))
    message_limit = 4096
    trace_limit = 16384
    if isinstance(error, (MemoryError, TimeoutError, OSError)):
        retryable = True
        retry_class = "transient_resource_or_io"
    elif isinstance(error, ValueError):
        retryable = False
        retry_class = "deterministic_invariant"
    else:
        retryable = True
        retry_class = "unclassified_retry_once"
    event: dict[str, Any] = {
        "schema_version": "1.0-error",
        "record_kind": "hypothesis_space_campaign_error",
        "error_id": f"{campaign_id}-ERR-{sequence:04d}",
        "campaign_id": campaign_id,
        "universe_id_sha256": universe_id,
        "evaluation_id_sha256": evaluation_id,
        "shard_index": shard_index,
        "start_ordinal": start_ordinal,
        "stage": stage,
        "exception_class": type(error).__name__,
        "message_excerpt": message[:message_limit],
        "traceback_excerpt": trace[:trace_limit],
        "message_truncated": len(message) > message_limit,
        "traceback_truncated": len(trace) > trace_limit,
        "message_sha256": hashlib.sha256(message.encode("utf-8")).hexdigest(),
        "traceback_sha256": hashlib.sha256(trace.encode("utf-8")).hexdigest(),
        "occurred_at_utc": datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        ).replace("+00:00", "Z"),
        "retryable": retryable,
        "retry_class": retry_class,
        "disposition": "retained_operational_failure",
        "previous_error_file_sha256": prior,
    }
    event["error_payload_sha256"] = error_payload_digest(event)
    path = directory / f"{sequence:04d}.json"
    immutable_create_json(path, event)
    return path


@contextmanager
def campaign_writer_lock(campaign_id: str):
    """Prevent two local writers from evaluating the same campaign concurrently."""

    path = campaign_directory(campaign_id) / ".writer.lock"
    claim = {
        "schema_version": "1.0-writer-lock",
        "campaign_id": campaign_id,
        "process_id": os.getpid(),
        "acquired_at_utc": datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        ).replace("+00:00", "Z"),
        "recovery": "Inspect the owning process; remove only after a confirmed crash.",
    }
    try:
        immutable_create_json(path, claim)
    except FileExistsError as exc:
        raise ValueError(
            f"campaign writer lock already exists: {path.relative_to(ROOT)}"
        ) from exc
    claimed_sha256 = sha256_bytes(path.read_bytes())
    try:
        yield
    finally:
        if path.is_file() and sha256_bytes(path.read_bytes()) == claimed_sha256:
            path.unlink()


def _work_receipts_unlocked(
    policy: dict[str, Any],
    *,
    campaign_id: str,
    source_commit: str,
    time_budget_seconds: float,
    shard_size: int,
    max_new_shards: int | None = None,
) -> dict[str, Any]:
    if not CAMPAIGN_ID_RE.fullmatch(campaign_id):
        raise ValueError("campaign_id is invalid")
    if not HEX40_RE.fullmatch(source_commit):
        raise ValueError("source_commit must be lowercase 40-hex")
    if time_budget_seconds <= 0:
        raise ValueError("time budget must be positive")
    if max_new_shards is not None and max_new_shards < 0:
        raise ValueError("max_new_shards cannot be negative")
    if not commit_is_ancestor_of_head(source_commit):
        raise ValueError("source_commit must be an ancestor of HEAD")
    if not commit_is_ancestor_of_ref(source_commit, policy["protected_base_ref"]):
        raise ValueError("source_commit must be an ancestor of protected main")
    checkout_matches_subject(policy, source_commit)
    universe = prepare_universe()
    universe_meta = universe_manifest(universe)
    canonical_state = json.loads(
        git_file_bytes(source_commit, policy["subject"]["space_state_path"])
    )
    evaluation_meta = evaluation_manifest(
        universe_meta["universe_id_sha256"],
        canonical_state,
        dependency_sha256=source_evaluator_dependency_digests(source_commit),
    )
    _, error_problems = validate_campaign_error_chain(
        campaign_id,
        universe_meta["universe_id_sha256"],
        evaluation_meta["evaluation_id_sha256"],
    )
    if error_problems:
        raise ValueError("; ".join(error_problems))
    prior_records, prior_problems = load_records(policy)
    if prior_problems:
        raise ValueError("; ".join(prior_problems))
    if any(
        item.get("evaluation", {}).get("evaluation_id_sha256")
        == evaluation_meta["evaluation_id_sha256"]
        for item in prior_records
    ):
        return {
            "status": "EXHAUSTED",
            "new_shards": 0,
            "next_missing_shard": None,
            "physical_evaluations": 0,
        }
    ensure_evaluation_claim(
        campaign_id=campaign_id,
        source_commit=source_commit,
        universe_id=universe_meta["universe_id_sha256"],
        evaluation_id=evaluation_meta["evaluation_id_sha256"],
    )
    directory = campaign_directory(campaign_id)
    manifest_path = directory / "manifest.json"
    if manifest_path.exists():
        manifest = read_json(manifest_path)
        if manifest.get("evaluation", {}).get("evaluation_id_sha256") != evaluation_meta[
            "evaluation_id_sha256"
        ]:
            raise ValueError("campaign ID already belongs to another evaluation")
        return {
            "status": "EXHAUSTED",
            "new_shards": 0,
            "next_missing_shard": None,
            "physical_evaluations": 0,
        }
    ranges = fixed_shard_ranges(universe.expected, shard_size)
    shard_dir = directory / "shards"
    start_time = time.perf_counter_ns()
    deadline = start_time + round(time_budget_seconds * 1_000_000_000)
    previous_digest: str | None = None
    new_shards = 0
    physical = 0
    for index, (start, end) in enumerate(ranges):
        path = shard_dir / f"{index:06d}.json"
        if path.exists():
            receipt = read_json(path)
            problems = validate_shard_receipt(
                receipt,
                universe_meta,
                evaluation_meta,
                campaign_id=campaign_id,
                shard_index=index,
                start=start,
                end=end,
                previous_receipt_file_sha256=previous_digest,
            )
            if problems:
                error = ValueError("; ".join(problems))
                retain_error_event(
                    campaign_id,
                    evaluation_meta["evaluation_id_sha256"],
                    universe_meta["universe_id_sha256"],
                    shard_index=index,
                    start_ordinal=start,
                    stage="existing_receipt_validation",
                    error=error,
                )
                raise error
            previous_digest = sha256_bytes(path.read_bytes())
            continue
        if any((shard_dir / f"{later:06d}.json").exists() for later in range(index + 1, len(ranges))):
            error = ValueError("receipt set contains a gap")
            retain_error_event(
                campaign_id,
                evaluation_meta["evaluation_id_sha256"],
                universe_meta["universe_id_sha256"],
                shard_index=index,
                start_ordinal=start,
                stage="work_acquisition",
                error=error,
            )
            raise error
        if time.perf_counter_ns() >= deadline or (
            max_new_shards is not None and new_shards >= max_new_shards
        ):
            return {
                "status": "PARTIAL",
                "new_shards": new_shards,
                "next_missing_shard": index,
                "physical_evaluations": physical,
            }
        try:
            receipt = create_shard_receipt(
                universe,
                universe_meta,
                evaluation_meta,
                campaign_id=campaign_id,
                shard_index=index,
                start=start,
                end=end,
                previous_receipt_file_sha256=previous_digest,
            )
            problems = validate_shard_receipt(
                receipt,
                universe_meta,
                evaluation_meta,
                campaign_id=campaign_id,
                shard_index=index,
                start=start,
                end=end,
                previous_receipt_file_sha256=previous_digest,
            )
            if problems:
                raise ValueError("; ".join(problems))
            immutable_create_json(path, receipt)
        except BaseException as exc:
            retain_error_event(
                campaign_id,
                evaluation_meta["evaluation_id_sha256"],
                universe_meta["universe_id_sha256"],
                shard_index=index,
                start_ordinal=start,
                stage="shard_evaluation",
                error=exc,
            )
            raise
        previous_digest = sha256_bytes(path.read_bytes())
        new_shards += 1
        physical += end - start
    return {
        "status": "READY_TO_FINALIZE",
        "new_shards": new_shards,
        "next_missing_shard": None,
        "physical_evaluations": physical,
    }


def work_receipts(
    policy: dict[str, Any],
    *,
    campaign_id: str,
    source_commit: str,
    time_budget_seconds: float,
    shard_size: int,
    max_new_shards: int | None = None,
) -> dict[str, Any]:
    if not CAMPAIGN_ID_RE.fullmatch(campaign_id):
        raise ValueError("campaign_id is invalid")
    with campaign_writer_lock(campaign_id):
        return _work_receipts_unlocked(
            policy,
            campaign_id=campaign_id,
            source_commit=source_commit,
            time_budget_seconds=time_budget_seconds,
            shard_size=shard_size,
            max_new_shards=max_new_shards,
        )


def subject_at_commit(policy: dict[str, Any], source_commit: str) -> dict[str, Any]:
    subject_paths = policy["subject"]
    digests = {
        key: sha256_bytes(git_file_bytes(source_commit, relative))
        for key, relative in subject_paths.items()
    }
    state = json.loads(
        git_file_bytes(source_commit, subject_paths["space_state_path"])
    )
    return {
        "source_commit": source_commit,
        "space_id": state["space_id"],
        "space_instance_root_sha256": state["bulk_contract"][
            "instance_root_sha256"
        ],
        "coverage_merkle_root_sha256": state["bulk_contract"][
            "coverage_merkle_root_sha256"
        ],
        "full_universe_count": state["counts"]["attempts"],
        "path_sha256": digests,
    }


def checkout_matches_subject(policy: dict[str, Any], source_commit: str) -> None:
    paths = set(policy["subject"].values()) | set(EVALUATOR_DEPENDENCY_PATHS)
    for relative in sorted(paths):
        current = (ROOT / relative).read_bytes()
        historical = git_file_bytes(source_commit, relative)
        if current != historical:
            raise ValueError(f"current {relative} differs from source_commit")


def create_record(
    policy: dict[str, Any],
    *,
    campaign_id: str,
    source_commit: str,
    time_budget_seconds: float,
    shard_size: int,
) -> dict[str, Any]:
    if not HEX40_RE.fullmatch(source_commit):
        raise ValueError("source_commit must be lowercase 40-hex")
    if not commit_is_ancestor_of_head(source_commit):
        raise ValueError("source_commit must be an ancestor of HEAD")
    if not commit_is_ancestor_of_ref(source_commit, policy["protected_base_ref"]):
        raise ValueError("source_commit must be an ancestor of protected main")
    checkout_matches_subject(policy, source_commit)
    work = work_receipts(
        policy,
        campaign_id=campaign_id,
        source_commit=source_commit,
        time_budget_seconds=time_budget_seconds,
        shard_size=shard_size,
    )
    if work["status"] != "READY_TO_FINALIZE":
        raise ValueError(f"campaign cannot finalize from work status {work['status']}")
    recorded_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )
    universe = prepare_universe()
    universe_meta = universe_manifest(universe)
    source_state = json.loads(
        git_file_bytes(source_commit, policy["subject"]["space_state_path"])
    )
    evaluation_meta = evaluation_manifest(
        universe_meta["universe_id_sha256"],
        source_state,
        dependency_sha256=source_evaluator_dependency_digests(source_commit),
    )
    claim_path = ensure_evaluation_claim(
        campaign_id=campaign_id,
        source_commit=source_commit,
        universe_id=universe_meta["universe_id_sha256"],
        evaluation_id=evaluation_meta["evaluation_id_sha256"],
    )
    ranges = fixed_shard_ranges(universe.expected, shard_size)
    receipt_anchors: list[dict[str, Any]] = []
    receipts: list[dict[str, Any]] = []
    previous_digest: str | None = None
    for index, (start, end) in enumerate(ranges):
        path = campaign_directory(campaign_id) / "shards" / f"{index:06d}.json"
        if not path.is_file():
            raise ValueError(f"campaign receipt is missing: {path}")
        receipt = read_json(path)
        problems = validate_shard_receipt(
            receipt,
            universe_meta,
            evaluation_meta,
            campaign_id=campaign_id,
            shard_index=index,
            start=start,
            end=end,
            previous_receipt_file_sha256=previous_digest,
        )
        if problems:
            raise ValueError("; ".join(problems))
        file_digest = sha256_bytes(path.read_bytes())
        receipt_anchors.append(
            {
                "shard_index": index,
                "start_ordinal": start,
                "end_ordinal_exclusive": end,
                "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "sha256": file_digest,
            }
        )
        receipts.append(receipt)
        previous_digest = file_digest
    global_merkle = merkle_from_range_receipts(receipts)
    if global_merkle.count != universe.expected:
        raise ValueError("receipt set does not exhaust the finite universe")
    if global_merkle.root_bytes().hex() != source_state["bulk_contract"][
        "coverage_merkle_root_sha256"
    ]:
        raise ValueError("receipt root disagrees with the frozen source state")
    cold = sum(item["aggregates"]["cold"] for item in receipts)
    warm = sum(item["aggregates"]["warm"] for item in receipts)
    type_counts: Counter[str] = Counter()
    mask_counts: Counter[str] = Counter()
    for receipt in receipts:
        type_counts.update(receipt["aggregates"]["type_counts"])
        mask_counts.update(receipt["aggregates"]["mask_counts"])
    if cold != source_state["counts"]["cold"] or warm != source_state["counts"]["warm"]:
        raise ValueError("receipt screening totals disagree with source state")
    if dict(sorted(type_counts.items())) != source_state["counts_by_type"]:
        raise ValueError("receipt type totals disagree with source state")
    rejection_histogram, primary_rejection_histogram = rejection_histograms_from_masks(
        mask_counts, universe.ordered_reasons
    )
    if rejection_histogram != source_state["rejection_histogram"]:
        raise ValueError("receipt rejection totals disagree with source state")
    if primary_rejection_histogram != source_state["primary_rejection_histogram"]:
        raise ValueError("receipt primary-rejection totals disagree with source state")
    shard_rates = [item["signatures_per_minute"] for item in receipts]
    prior_records, prior_problems = load_records(policy)
    if prior_problems:
        raise ValueError("; ".join(prior_problems))
    universe_seen = any(
        item.get("universe", {}).get("universe_id_sha256")
        == universe_meta["universe_id_sha256"]
        for item in prior_records
    )
    evaluation_seen = any(
        item.get("evaluation", {}).get("evaluation_id_sha256")
        == evaluation_meta["evaluation_id_sha256"]
        for item in prior_records
    )
    if evaluation_seen:
        raise ValueError("this evaluation is already exhausted by an anchored campaign")
    error_paths, error_problems = validate_campaign_error_chain(
        campaign_id,
        universe_meta["universe_id_sha256"],
        evaluation_meta["evaluation_id_sha256"],
    )
    if error_problems:
        raise ValueError("; ".join(error_problems))
    error_anchors = [
        {
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256_bytes(path.read_bytes()),
        }
        for path in error_paths
    ]
    receipt_anchor_root = sha256_bytes(
        b"".join(canonical_json_bytes(item) for item in receipt_anchors)
    )
    error_anchor_root = sha256_bytes(
        b"".join(canonical_json_bytes(item) for item in error_anchors)
    )
    physical_evaluations = sum(item["physical_evaluations"] for item in receipts)
    unique_universe_added = 0 if universe_seen else universe.expected
    unique_evaluation_added = universe.expected
    record: dict[str, Any] = {
        "schema_version": "1.0",
        "campaign_id": campaign_id,
        "record_kind": "finite_unique_coverage_campaign",
        "status": "completed_exhausted",
        "recorded_at_utc": recorded_at,
        "subject": subject_at_commit(policy, source_commit),
        "universe": universe_meta,
        "evaluation": evaluation_meta,
        "evaluation_claim": {
            "path": str(claim_path.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256_bytes(claim_path.read_bytes()),
        },
        "harness": {
            "path": "scripts/hypothesis_space_campaign.py",
            "sha256": sha256_bytes(Path(__file__).read_bytes()),
            "resolution_rule": HARNESS_RESOLUTION_RULE,
            "schema_path": str(SCHEMA_PATH.relative_to(ROOT)).replace("\\", "/"),
            "schema_sha256": sha256_bytes(SCHEMA_PATH.read_bytes()),
            "receipt_schema_path": str(RECEIPT_SCHEMA_PATH.relative_to(ROOT)).replace(
                "\\", "/"
            ),
            "receipt_schema_sha256": sha256_bytes(RECEIPT_SCHEMA_PATH.read_bytes()),
            "error_schema_path": str(ERROR_SCHEMA_PATH.relative_to(ROOT)).replace(
                "\\", "/"
            ),
            "error_schema_sha256": sha256_bytes(ERROR_SCHEMA_PATH.read_bytes()),
        },
        "budget": {
            "finalization_invocation_budget_seconds": time_budget_seconds,
            "termination_reason": "finite_universe_exhausted",
            "retained_shard_elapsed_ns": sum(item["elapsed_ns"] for item in receipts),
            "stopped_early_because_universe_exhausted": True,
        },
        "coverage": {
            "ordinal_start": 0,
            "ordinal_end_exclusive": universe.expected,
            "full_universe_count": universe.expected,
            "physical_evaluations": physical_evaluations,
            "unique_universe_cells_added": unique_universe_added,
            "unique_evaluation_cells_added": unique_evaluation_added,
            "duplicate_evaluations": physical_evaluations - unique_evaluation_added,
            "typed_duplicates": 0,
            "exact_semantic_axis_duplicates": 0,
            "exhausted": True,
            "coverage_fraction": 1.0,
            "coverage_merkle_root_sha256": global_merkle.root_bytes().hex(),
            "shard_size": shard_size,
            "shard_count": len(receipts),
            "receipt_anchor_root_sha256": receipt_anchor_root,
            "receipt_anchors": receipt_anchors,
        },
        "screening_snapshot": {
            "cold": cold,
            "warm": warm,
            "hot": 0,
            "type_counts": dict(sorted(type_counts.items())),
            "mask_counts": dict(sorted(mask_counts.items())),
        },
        "performance": {
            "minimum_shard_signatures_per_minute": min(shard_rates),
            "median_shard_signatures_per_minute": round(statistics.median(shard_rates)),
            "maximum_shard_signatures_per_minute": max(shard_rates),
            "performance_is_operational_only": True,
            "timing_assurance": "producer_self_timed_untrusted",
            "throughput_is_coverage_evidence": False,
            "runtime_fingerprint": {
                "python_implementation": sys.implementation.name,
                "python_version": platform.python_version(),
                "operating_system": platform.system(),
                "machine": platform.machine() or "unknown",
            },
        },
        "operational_diagnostics": {
            "pipeline_errors": len(error_anchors),
            "invariant_violations": 0,
            "error_anchor_root_sha256": error_anchor_root,
            "error_anchors": error_anchors,
        },
        "knowledge_effect": {
            "scientific_outcome": "none",
            "claim_disposition": "none",
            "ranker_training_eligible": False,
            "brier_calibration_eligible": False,
            "candidate_admissible": False,
            "candidate_recommended": False,
            "experiment_authorized": False,
            "route_promotion": False,
            "interpretation": "The frozen finite typed universe was exhausted exactly once. Cold cells are structural screening rejects, not falsified hypotheses; warm cells remain proposal seeds without assured mechanisms.",
        },
    }
    record["record_payload_sha256"] = payload_digest(record)
    return record


def validate_record(
    record: dict[str, Any], policy: dict[str, Any], *, verify_git: bool = True
) -> list[str]:
    problems: list[str] = [
        f"record schema: {item}" for item in schema_problems(record, SCHEMA_PATH)
    ]
    required = {
        "schema_version",
        "campaign_id",
        "record_kind",
        "status",
        "recorded_at_utc",
        "subject",
        "universe",
        "evaluation",
        "evaluation_claim",
        "harness",
        "budget",
        "coverage",
        "screening_snapshot",
        "performance",
        "operational_diagnostics",
        "knowledge_effect",
        "record_payload_sha256",
    }
    if set(record) != required:
        problems.append("campaign record has unexpected top-level shape")
    if record.get("schema_version") != "1.0":
        problems.append("campaign record schema is invalid")
    if record.get("record_kind") != "finite_unique_coverage_campaign":
        problems.append("campaign record kind is invalid")
    if record.get("status") != "completed_exhausted":
        problems.append("anchored campaign must be completed and exhausted")
    campaign_id = record.get("campaign_id")
    if not isinstance(campaign_id, str) or not CAMPAIGN_ID_RE.fullmatch(campaign_id):
        problems.append("campaign_id is invalid")
    recorded_at = record.get("recorded_at_utc")
    try:
        parsed_at = datetime.fromisoformat(str(recorded_at).replace("Z", "+00:00"))
        if campaign_id and campaign_id[4:14] != parsed_at.date().isoformat():
            problems.append("campaign_id date does not match recorded_at_utc")
    except ValueError:
        problems.append("recorded_at_utc is not an ISO timestamp")
    if record.get("record_payload_sha256") != payload_digest(record):
        problems.append("campaign record payload digest mismatch")
    harness = record.get("harness", {})
    expected_harness_keys = {
        "path",
        "sha256",
        "resolution_rule",
        "schema_path",
        "schema_sha256",
        "receipt_schema_path",
        "receipt_schema_sha256",
        "error_schema_path",
        "error_schema_sha256",
    }
    if not isinstance(harness, dict) or set(harness) != expected_harness_keys:
        problems.append("campaign harness has unexpected shape")
    else:
        if harness.get("resolution_rule") != HARNESS_RESOLUTION_RULE:
            problems.append("campaign harness resolution rule drifted")
        for path_key, digest_key in (
            ("path", "sha256"),
            ("schema_path", "schema_sha256"),
            ("receipt_schema_path", "receipt_schema_sha256"),
            ("error_schema_path", "error_schema_sha256"),
        ):
            relative = harness.get(path_key)
            digest = harness.get(digest_key)
            if (
                not isinstance(relative, str)
                or not isinstance(digest, str)
                or not HEX64_RE.fullmatch(digest)
                or not harness_digest_resolves(relative, digest)
            ):
                problems.append(f"campaign {path_key} digest does not resolve")
    subject = record.get("subject", {})
    source_commit = subject.get("source_commit") if isinstance(subject, dict) else None
    if not isinstance(source_commit, str) or not HEX40_RE.fullmatch(source_commit):
        problems.append("campaign source_commit is invalid")
    elif verify_git:
        if not commit_is_ancestor_of_head(source_commit):
            problems.append("campaign source_commit is not an ancestor of HEAD")
        if not commit_is_ancestor_of_ref(source_commit, policy["protected_base_ref"]):
            problems.append("campaign source_commit is not an ancestor of protected main")
        try:
            expected_subject = subject_at_commit(policy, source_commit)
            if subject != expected_subject:
                problems.append("campaign subject does not match source_commit")
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            problems.append(f"campaign subject could not be reconstructed: {exc}")
    universe_meta = record.get("universe", {})
    evaluation_meta = record.get("evaluation", {})
    if not isinstance(universe_meta, dict) or not isinstance(evaluation_meta, dict):
        problems.append("campaign universe/evaluation manifests are invalid")
    else:
        frozen_universe = copy.deepcopy(universe_meta)
        universe_id = frozen_universe.pop("universe_id_sha256", None)
        if universe_id != sha256_json(frozen_universe):
            problems.append("campaign universe identity is invalid")
        frozen_evaluation = copy.deepcopy(evaluation_meta)
        evaluation_id = frozen_evaluation.pop("evaluation_id_sha256", None)
        if evaluation_id != sha256_json(frozen_evaluation):
            problems.append("campaign evaluation identity is invalid")
        if evaluation_meta.get("universe_id_sha256") != universe_id:
            problems.append("campaign evaluation does not bind its universe")
        dependencies = evaluation_meta.get("dependency_sha256")
        if not isinstance(dependencies, dict) or set(dependencies) != set(
            EVALUATOR_DEPENDENCY_PATHS
        ):
            problems.append("campaign evaluation dependency closure is incomplete")
        elif evaluation_meta.get("dependency_closure_sha256") != sha256_json(
            dict(sorted(dependencies.items()))
        ):
            problems.append("campaign evaluation dependency closure digest mismatch")
        elif verify_git and isinstance(source_commit, str) and HEX40_RE.fullmatch(
            source_commit
        ):
            try:
                if dependencies != source_evaluator_dependency_digests(source_commit):
                    problems.append(
                        "campaign evaluation dependencies do not match source_commit"
                    )
            except (OSError, ValueError) as exc:
                problems.append(
                    f"campaign dependency closure could not be reconstructed: {exc}"
                )
        if isinstance(subject, dict) and isinstance(harness, dict):
            if evaluation_meta.get("source_runner_sha256") != subject.get(
                "path_sha256", {}
            ).get("runner_path"):
                problems.append("campaign evaluation does not bind its source runner")
            if evaluation_meta.get("campaign_evaluator_sha256") != harness.get(
                "sha256"
            ):
                problems.append("campaign evaluation does not bind its evaluator")
        if subject and universe_meta.get("cardinality") != subject.get(
            "full_universe_count"
        ):
            problems.append("campaign universe cardinality disagrees with subject")
    claim_anchor = record.get("evaluation_claim")
    if not isinstance(claim_anchor, dict) or set(claim_anchor) != {"path", "sha256"}:
        problems.append("campaign evaluation claim anchor is invalid")
    else:
        claim_path = ROOT / str(claim_anchor.get("path", ""))
        if (
            not claim_path.is_file()
            or sha256_bytes(claim_path.read_bytes()) != claim_anchor.get("sha256")
        ):
            problems.append("campaign evaluation claim anchor digest mismatch")
        else:
            try:
                claim = read_json(claim_path)
                claim_projection = copy.deepcopy(claim)
                claim_digest = claim_projection.pop("claim_payload_sha256", None)
                if set(claim_projection) != {
                    "schema_version",
                    "record_kind",
                    "campaign_id",
                    "source_commit",
                    "universe_id_sha256",
                    "evaluation_id_sha256",
                    "assurance",
                    "pre_anchor_deletion_resistant",
                }:
                    problems.append("campaign evaluation claim shape drifted")
                if claim_digest != sha256_json(claim_projection):
                    problems.append("campaign evaluation claim payload mismatch")
                if (
                    claim.get("campaign_id") != campaign_id
                    or claim.get("source_commit") != source_commit
                    or claim.get("universe_id_sha256")
                    != universe_meta.get("universe_id_sha256")
                    or claim.get("evaluation_id_sha256")
                    != evaluation_meta.get("evaluation_id_sha256")
                    or claim.get("pre_anchor_deletion_resistant") is not False
                ):
                    problems.append("campaign evaluation claim identity drifted")
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                problems.append(f"campaign evaluation claim cannot be read: {exc}")
    coverage = record.get("coverage", {})
    if not isinstance(coverage, dict):
        problems.append("campaign coverage is invalid")
    else:
        full = coverage.get("full_universe_count")
        if (
            coverage.get("ordinal_start") != 0
            or coverage.get("ordinal_end_exclusive") != full
            or coverage.get("physical_evaluations") != full
            or coverage.get("unique_evaluation_cells_added") != full
            or coverage.get("unique_universe_cells_added") not in {0, full}
            or coverage.get("duplicate_evaluations") != 0
            or coverage.get("typed_duplicates") != 0
            or coverage.get("exact_semantic_axis_duplicates") != 0
            or coverage.get("exhausted") is not True
            or coverage.get("coverage_fraction") != 1.0
        ):
            problems.append("campaign did not retain exact unique exhaustion")
        shard_size = coverage.get("shard_size")
        try:
            ranges = fixed_shard_ranges(full, shard_size)
        except (TypeError, ValueError) as exc:
            ranges = []
            problems.append(f"campaign shard layout is invalid: {exc}")
        anchors = coverage.get("receipt_anchors")
        receipts: list[dict[str, Any]] = []
        previous_digest: str | None = None
        if not isinstance(anchors, list) or len(anchors) != len(ranges):
            problems.append("campaign receipt anchors do not cover fixed shard ranges")
        else:
            for index, ((start, end), anchor) in enumerate(zip(ranges, anchors)):
                expected_anchor_keys = {
                    "shard_index",
                    "start_ordinal",
                    "end_ordinal_exclusive",
                    "path",
                    "sha256",
                }
                if not isinstance(anchor, dict) or set(anchor) != expected_anchor_keys:
                    problems.append(f"campaign receipt anchor {index} has invalid shape")
                    continue
                if (
                    anchor.get("shard_index") != index
                    or anchor.get("start_ordinal") != start
                    or anchor.get("end_ordinal_exclusive") != end
                ):
                    problems.append(f"campaign receipt anchor {index} range drifted")
                    continue
                path = ROOT / anchor["path"]
                if not path.is_file() or sha256_bytes(path.read_bytes()) != anchor.get(
                    "sha256"
                ):
                    problems.append(f"campaign receipt anchor {index} digest mismatch")
                    continue
                try:
                    receipt = read_json(path)
                except (OSError, ValueError, json.JSONDecodeError) as exc:
                    problems.append(f"campaign receipt {index} cannot be read: {exc}")
                    continue
                receipt_problems = validate_shard_receipt(
                    receipt,
                    universe_meta,
                    evaluation_meta,
                    campaign_id=campaign_id,
                    shard_index=index,
                    start=start,
                    end=end,
                    previous_receipt_file_sha256=previous_digest,
                )
                problems.extend(
                    f"campaign receipt {index}: {item}" for item in receipt_problems
                )
                receipts.append(receipt)
                previous_digest = anchor["sha256"]
            expected_anchor_root = sha256_bytes(
                b"".join(canonical_json_bytes(item) for item in anchors)
            )
            if coverage.get("receipt_anchor_root_sha256") != expected_anchor_root:
                problems.append("campaign receipt anchor root mismatch")
        if len(receipts) == len(ranges) and ranges:
            try:
                reconstructed = merkle_from_range_receipts(receipts)
                if reconstructed.count != full:
                    problems.append("campaign receipt frontiers do not exhaust the universe")
                if reconstructed.root_bytes().hex() != coverage.get(
                    "coverage_merkle_root_sha256"
                ):
                    problems.append("campaign receipt frontiers disagree with coverage root")
            except (KeyError, TypeError, ValueError) as exc:
                problems.append(f"campaign receipt frontier reconstruction failed: {exc}")
            aggregate_cold = sum(item["aggregates"]["cold"] for item in receipts)
            aggregate_warm = sum(item["aggregates"]["warm"] for item in receipts)
            aggregate_types: Counter[str] = Counter()
            aggregate_masks: Counter[str] = Counter()
            for item in receipts:
                aggregate_types.update(item["aggregates"]["type_counts"])
                aggregate_masks.update(item["aggregates"]["mask_counts"])
            snapshot = record.get("screening_snapshot", {})
            if snapshot != {
                "cold": aggregate_cold,
                "warm": aggregate_warm,
                "hot": 0,
                "type_counts": dict(sorted(aggregate_types.items())),
                "mask_counts": dict(sorted(aggregate_masks.items())),
            }:
                problems.append("campaign screening snapshot is not receipt-derived")
            rates = [item["signatures_per_minute"] for item in receipts]
            expected_performance = {
                "minimum_shard_signatures_per_minute": min(rates),
                "median_shard_signatures_per_minute": round(statistics.median(rates)),
                "maximum_shard_signatures_per_minute": max(rates),
                "performance_is_operational_only": True,
                "timing_assurance": "producer_self_timed_untrusted",
                "throughput_is_coverage_evidence": False,
            }
            observed_performance = record.get("performance", {})
            if not isinstance(observed_performance, dict) or any(
                observed_performance.get(key) != value
                for key, value in expected_performance.items()
            ):
                problems.append("campaign performance is not receipt-derived")
            if record.get("budget", {}).get("retained_shard_elapsed_ns") != sum(
                item["elapsed_ns"] for item in receipts
            ):
                problems.append("campaign elapsed time is not receipt-derived")
        if subject and coverage.get("coverage_merkle_root_sha256") != subject.get(
            "coverage_merkle_root_sha256"
        ):
            problems.append("campaign root does not match its frozen subject")
    budget = record.get("budget", {})
    if (
        not isinstance(budget, dict)
        or budget.get("termination_reason") != "finite_universe_exhausted"
        or budget.get("stopped_early_because_universe_exhausted") is not True
    ):
        problems.append("campaign exhaustion termination is invalid")
    diagnostics = record.get("operational_diagnostics", {})
    if not isinstance(diagnostics, dict) or set(diagnostics) != {
        "pipeline_errors",
        "invariant_violations",
        "error_anchor_root_sha256",
        "error_anchors",
    }:
        problems.append("campaign operational diagnostics have invalid shape")
    else:
        error_anchors = diagnostics.get("error_anchors")
        if not isinstance(error_anchors, list):
            problems.append("campaign error anchors must be an array")
        else:
            if diagnostics.get("pipeline_errors") != len(error_anchors):
                problems.append("campaign error count drifted")
            expected_error_root = sha256_bytes(
                b"".join(canonical_json_bytes(item) for item in error_anchors)
            )
            if diagnostics.get("error_anchor_root_sha256") != expected_error_root:
                problems.append("campaign error anchor root mismatch")
            prior_error: str | None = None
            for index, anchor in enumerate(error_anchors):
                if not isinstance(anchor, dict) or set(anchor) != {"path", "sha256"}:
                    problems.append(f"campaign error anchor {index} has invalid shape")
                    continue
                path = ROOT / anchor["path"]
                if not path.is_file() or sha256_bytes(path.read_bytes()) != anchor["sha256"]:
                    problems.append(f"campaign error anchor {index} digest mismatch")
                    continue
                try:
                    event = read_json(path)
                except (OSError, ValueError, json.JSONDecodeError) as exc:
                    problems.append(f"campaign error event {index} cannot be read: {exc}")
                    continue
                if isinstance(campaign_id, str):
                    problems.extend(
                        f"campaign error event {index}: {item}"
                        for item in validate_error_event(
                            event,
                            campaign_id=campaign_id,
                            universe_id=str(universe_meta.get("universe_id_sha256")),
                            evaluation_id=str(
                                evaluation_meta.get("evaluation_id_sha256")
                            ),
                            sequence=index + 1,
                            previous_error_file_sha256=prior_error,
                        )
                    )
                prior_error = anchor["sha256"]
        if diagnostics.get("invariant_violations") != 0:
            problems.append("completed campaign retains unresolved invariant violations")
    effect = record.get("knowledge_effect", {})
    required_false = (
        "ranker_training_eligible",
        "brier_calibration_eligible",
        "candidate_admissible",
        "candidate_recommended",
        "experiment_authorized",
        "route_promotion",
    )
    required_effect_keys = {
        "scientific_outcome",
        "claim_disposition",
        *required_false,
        "interpretation",
    }
    if (
        not isinstance(effect, dict)
        or set(effect) != required_effect_keys
        or effect.get("scientific_outcome") != "none"
        or effect.get("claim_disposition") != "none"
        or any(effect.get(key) is not False for key in required_false)
    ):
        problems.append("campaign crossed the scientific-memory boundary")
    return problems


def protected_base_anchors(policy: dict[str, Any]) -> list[dict[str, str]]:
    """Read campaign anchors at the protected merge base to forbid rewrites."""
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
            if not commit_is_ancestor_of_head(push_before):
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
        ["git", "show", f"{commit}:repo/HYPOTHESIS_SPACE_CAMPAIGN_V1.json"],
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
        raise ValueError("protected campaign anchors are malformed")
    return anchors


def load_records(policy: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    problems: list[str] = []
    anchors = policy.get("immutable_record_anchors", [])
    try:
        protected = protected_base_anchors(policy)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        protected = []
        problems.append(f"cannot load protected campaign history: {exc}")
    if anchors[: len(protected)] != protected:
        problems.append("immutable campaign anchors rewrite or truncate protected history")
    anchored_paths = {anchor["path"] for anchor in anchors if isinstance(anchor, dict)}
    actual_paths = {
        str(path.relative_to(ROOT)).replace("\\", "/")
        for path in RECORD_DIR.glob("*/manifest.json")
    }
    for extra in sorted(actual_paths - anchored_paths):
        problems.append(f"unanchored campaign record: {extra}")
    for missing in sorted(anchored_paths - actual_paths):
        problems.append(f"missing campaign record: {missing}")
    for anchor in anchors:
        path = ROOT / anchor["path"]
        if not path.is_file():
            continue
        if sha256_bytes(path.read_bytes()) != anchor["sha256"]:
            problems.append(f"campaign anchor digest mismatch: {anchor['path']}")
            continue
        try:
            record = read_json(path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            problems.append(f"campaign record cannot be read: {anchor['path']}: {exc}")
            continue
        if record.get("campaign_id") != anchor["campaign_id"]:
            problems.append(f"campaign anchor ID mismatch: {anchor['path']}")
        record_problems = [
            f"{anchor['campaign_id']}: {problem}"
            for problem in validate_record(record, policy)
        ]
        problems.extend(record_problems)
        if not record_problems:
            records.append(record)

    seen_universes: set[str] = set()
    seen_evaluations: set[str] = set()
    for record in records:
        universe_id = record["universe"]["universe_id_sha256"]
        evaluation_id = record["evaluation"]["evaluation_id_sha256"]
        full = record["universe"]["cardinality"]
        expected_universe_added = 0 if universe_id in seen_universes else full
        if record["coverage"]["unique_universe_cells_added"] != expected_universe_added:
            problems.append(
                f"{record['campaign_id']}: unique-universe accounting disagrees with history"
            )
        if evaluation_id in seen_evaluations:
            problems.append(
                f"{record['campaign_id']}: evaluation was already exhausted"
            )
        seen_universes.add(universe_id)
        seen_evaluations.add(evaluation_id)
    return records, problems


def build_state(policy: dict[str, Any], records: list[dict[str, Any]]) -> dict[str, Any]:
    current_universe = universe_manifest(prepare_universe())
    current_space_state = read_json(ROOT / policy["subject"]["space_state_path"])
    current_evaluation = evaluation_manifest(
        current_universe["universe_id_sha256"],
        current_space_state,
        dependency_sha256=current_evaluator_dependency_digests(),
    )
    current_universe_id = current_universe["universe_id_sha256"]
    current_evaluation_id = current_evaluation["evaluation_id_sha256"]
    roots: set[str] = set()
    universes: dict[str, int] = {}
    evaluations: dict[str, int] = {}
    coverage_history: list[dict[str, Any]] = []
    for record in records:
        root = record["subject"]["space_instance_root_sha256"]
        roots.add(root)
        universe_id = record["universe"]["universe_id_sha256"]
        evaluation_id = record["evaluation"]["evaluation_id_sha256"]
        universes.setdefault(universe_id, record["universe"]["cardinality"])
        evaluations.setdefault(evaluation_id, record["universe"]["cardinality"])
        coverage_history.append(
            {
                "campaign_id": record["campaign_id"],
                "recorded_at_utc": record["recorded_at_utc"],
                "source_commit": record["subject"]["source_commit"],
                "universe_id_sha256": universe_id,
                "evaluation_id_sha256": evaluation_id,
                "space_instance_root_sha256": root,
                "physical_evaluations": record["coverage"][
                    "physical_evaluations"
                ],
                "unique_universe_cells_added": record["coverage"][
                    "unique_universe_cells_added"
                ],
                "unique_evaluation_cells_added": record["coverage"][
                    "unique_evaluation_cells_added"
                ],
                "duplicate_evaluations": record["coverage"][
                    "duplicate_evaluations"
                ],
                "cold": record["screening_snapshot"]["cold"],
                "warm": record["screening_snapshot"]["warm"],
                "exhausted": True,
                "is_current_universe": universe_id == current_universe_id,
                "is_current_evaluation": evaluation_id == current_evaluation_id,
            }
        )
    physical_evaluations = sum(
        record["coverage"]["physical_evaluations"] for record in records
    )
    unique_evaluation_cells = sum(evaluations.values())
    anchor_stream = b"".join(
        canonical_json_bytes(anchor) for anchor in policy["immutable_record_anchors"]
    )
    return {
        "schema_version": "1.0-generated",
        "ledger_id": policy["ledger_id"],
        "status": "operational_unique_coverage_memory_non_scientific",
        "immutable_record_count": len(records),
        "immutable_record_root_sha256": sha256_bytes(anchor_stream),
        "counts": {
            "campaign_records": len(records),
            "completed_exhausted_campaigns": len(records),
            "distinct_universes": len(universes),
            "distinct_evaluations": len(evaluations),
            "distinct_space_instance_roots": len(roots),
            "physical_evaluations": physical_evaluations,
            "unique_universe_cells": sum(universes.values()),
            "unique_evaluation_cells": unique_evaluation_cells,
            "repeated_cells_processed": physical_evaluations
            - sum(universes.values()),
            "duplicate_evaluations": physical_evaluations
            - unique_evaluation_cells,
            "pipeline_errors": sum(
                item["operational_diagnostics"]["pipeline_errors"] for item in records
            ),
            "invariant_violations": sum(
                item["operational_diagnostics"]["invariant_violations"] for item in records
            ),
            "scientific_outcomes": 0,
            "ranker_training_labels": 0,
            "brier_calibration_records": 0,
            "admissible": 0,
            "recommended": 0,
            "authorized": 0,
            "route_promotions": 0,
        },
        "latest_campaign": None
        if not records
        else {
            "campaign_id": records[-1]["campaign_id"],
            "recorded_at_utc": records[-1]["recorded_at_utc"],
            "source_commit": records[-1]["subject"]["source_commit"],
            "space_instance_root_sha256": records[-1]["subject"][
                "space_instance_root_sha256"
            ],
            "universe_id_sha256": records[-1]["universe"][
                "universe_id_sha256"
            ],
            "evaluation_id_sha256": records[-1]["evaluation"][
                "evaluation_id_sha256"
            ],
            "unique_cells": records[-1]["universe"]["cardinality"],
            "finalization_invocation_budget_seconds": records[-1]["budget"][
                "finalization_invocation_budget_seconds"
            ],
            "retained_shard_elapsed_ns": records[-1]["budget"][
                "retained_shard_elapsed_ns"
            ],
            "termination_reason": records[-1]["budget"]["termination_reason"],
        },
        "coverage_history": coverage_history,
        "current_identity": {
            "universe_id_sha256": current_universe_id,
            "evaluation_id_sha256": current_evaluation_id,
            "universe_cardinality": current_universe["cardinality"],
            "universe_covered": current_universe_id in universes,
            "evaluation_exhausted": current_evaluation_id in evaluations,
        },
        "interpretation": {
            "current_finite_universe_exhausted": current_evaluation_id
            in evaluations,
            "current_finite_universe_size": current_universe["cardinality"],
            "current_universe_covered_under_any_evaluation": current_universe_id
            in universes,
            "current_evaluation_pending": current_evaluation_id not in evaluations,
            "additional_repetitions_add_unique_coverage": False,
            "larger_campaign_requires_new_evidence_bounded_grammar": True,
            "cold_is_structural_rejection_not_falsification": True,
            "warm_is_seed_not_hypothesis": True,
        },
        "epistemic_contract": policy["epistemic_contract"],
    }


def write_record(record: dict[str, Any]) -> Path:
    path = campaign_directory(record["campaign_id"]) / "manifest.json"
    if path.exists():
        raise ValueError(f"campaign record already exists: {path}")
    immutable_create_json(path, record)
    return path


def frozen_replay_environment() -> dict[str, str]:
    environment = dict(os.environ)
    for key in (
        "PYTHONHOME",
        "PYTHONINSPECT",
        "PYTHONPATH",
        "PYTHONSTARTUP",
        "PYTHONUSERBASE",
    ):
        environment.pop(key, None)
    environment["PYTHONIOENCODING"] = "utf-8"
    return environment


def run_frozen_source_projection(source_commit: str) -> dict[str, Any]:
    """Execute the recorded source runner from an isolated Git archive.

    This replay path does not import or call the campaign scanner. It remains
    reproducible after the current grammar changes because every file comes from
    the campaign's reachable protected-main commit.
    """

    archived = subprocess.run(
        ["git", "archive", "--format=tar", source_commit],
        cwd=ROOT,
        capture_output=True,
        check=True,
    ).stdout
    with tempfile.TemporaryDirectory(prefix="keyai-hyp-campaign-replay-") as raw:
        checkout = Path(raw)
        with tarfile.open(fileobj=io.BytesIO(archived), mode="r:") as bundle:
            root = checkout.resolve()
            for member in bundle.getmembers():
                destination = (checkout / member.name).resolve()
                if destination != root and root not in destination.parents:
                    raise ValueError("Git archive contains an unsafe path")
            bundle.extractall(checkout, filter="fully_trusted")
        runner = checkout / "scripts" / "hypothesis_space_funnel.py"
        environment = frozen_replay_environment()
        bootstrap = (
            "import runpy,sys;"
            "scripts,runner,*args=sys.argv[1:];"
            "sys.path.insert(0,scripts);"
            "sys.argv=[runner,*args];"
            "runpy.run_path(runner,run_name='__main__')"
        )
        completed = subprocess.run(
            [
                sys.executable,
                *FROZEN_REPLAY_PYTHON_FLAGS,
                "-c",
                bootstrap,
                str(checkout / "scripts"),
                str(runner),
                "--check",
                "--summary",
            ],
            cwd=checkout,
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=300,
        )
        if completed.returncode:
            raise ValueError(
                "frozen source runner failed: "
                + (completed.stderr or completed.stdout).strip()[:2000]
            )
        return read_json(checkout / "data" / "hypothesis_space_state.json")


def replay_record(record: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    source_commit = record.get("subject", {}).get("source_commit")
    if not isinstance(source_commit, str) or not HEX40_RE.fullmatch(source_commit):
        return ["campaign source commit is invalid for frozen replay"]
    try:
        state = run_frozen_source_projection(source_commit)
    except (OSError, ValueError, subprocess.SubprocessError, tarfile.TarError) as exc:
        return [f"frozen source replay failed: {exc}"]
    coverage = record["coverage"]
    snapshot = record["screening_snapshot"]
    if state["bulk_contract"]["coverage_merkle_root_sha256"] != coverage[
        "coverage_merkle_root_sha256"
    ]:
        problems.append("frozen source replay coverage root disagrees")
    if state["bulk_contract"]["instance_root_sha256"] != record["subject"][
        "space_instance_root_sha256"
    ]:
        problems.append("frozen source replay instance root disagrees")
    expected_counts = state["counts"]
    for key in ("cold", "warm", "hot"):
        if snapshot[key] != expected_counts[key]:
            problems.append(f"frozen source replay {key} count disagrees")
    if snapshot["type_counts"] != state["counts_by_type"]:
        problems.append("frozen source replay type counts disagree")
    rejection_histogram, primary_histogram = rejection_histograms_from_masks(
        snapshot["mask_counts"], record["universe"]["ordered_rejection_reasons"]
    )
    if rejection_histogram != state["rejection_histogram"]:
        problems.append("frozen source replay rejection histogram disagrees")
    if primary_histogram != state["primary_rejection_histogram"]:
        problems.append("frozen source replay primary rejection histogram disagrees")
    return problems


def retain_finalization_error_if_identifiable(
    policy: dict[str, Any],
    *,
    campaign_id: str,
    source_commit: str,
    shard_size: int,
    error: BaseException,
) -> None:
    """Retain post-shard finalization failures without masking the root error."""

    try:
        universe = prepare_universe()
        ranges = fixed_shard_ranges(universe.expected, shard_size)
        if not all(
            (campaign_directory(campaign_id) / "shards" / f"{index:06d}.json").is_file()
            for index in range(len(ranges))
        ):
            return
        state = json.loads(
            git_file_bytes(source_commit, policy["subject"]["space_state_path"])
        )
        universe_meta = universe_manifest(universe)
        evaluation_meta = evaluation_manifest(
            universe_meta["universe_id_sha256"],
            state,
            dependency_sha256=source_evaluator_dependency_digests(source_commit),
        )
        retain_error_event(
            campaign_id,
            evaluation_meta["evaluation_id_sha256"],
            universe_meta["universe_id_sha256"],
            shard_index=len(ranges),
            start_ordinal=universe.expected,
            stage="record_finalization",
            error=error,
        )
    except BaseException as retention_error:
        print(
            "WARNING: campaign finalization failed and its secondary error "
            f"record could not be retained: {type(retention_error).__name__}: "
            f"{retention_error}",
            file=sys.stderr,
        )
        return


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--record", action="store_true")
    parser.add_argument("--work", action="store_true")
    parser.add_argument("--replay", action="store_true")
    parser.add_argument("--campaign-id")
    parser.add_argument("--source-commit")
    parser.add_argument("--time-budget-seconds", type=float, default=600.0)
    parser.add_argument("--shard-size", type=int)
    parser.add_argument("--max-new-shards", type=int)
    args = parser.parse_args()

    policy = load_policy()
    shard_size = args.shard_size or policy["campaign_contract"][
        "default_shard_size"
    ]
    if args.work:
        if not args.campaign_id or not args.source_commit:
            parser.error("--work requires --campaign-id and --source-commit")
        result = work_receipts(
            policy,
            campaign_id=args.campaign_id,
            source_commit=args.source_commit,
            time_budget_seconds=args.time_budget_seconds,
            shard_size=shard_size,
            max_new_shards=args.max_new_shards,
        )
        print(
            "HYP_CAMPAIGN_WORK "
            f"status={result['status']} new_shards={result['new_shards']} "
            f"physical_evaluations={result['physical_evaluations']}"
        )
        return 0
    if args.record:
        if not args.campaign_id or not args.source_commit:
            parser.error("--record requires --campaign-id and --source-commit")
        records, problems = load_records(policy)
        if problems:
            print("refusing to record against invalid campaign memory:", file=sys.stderr)
            for problem in problems:
                print(f"- {problem}", file=sys.stderr)
            return 1
        try:
            record = create_record(
                policy,
                campaign_id=args.campaign_id,
                source_commit=args.source_commit,
                time_budget_seconds=args.time_budget_seconds,
                shard_size=shard_size,
            )
        except BaseException as exc:
            retain_finalization_error_if_identifiable(
                policy,
                campaign_id=args.campaign_id,
                source_commit=args.source_commit,
                shard_size=shard_size,
                error=exc,
            )
            raise
        problems = validate_record(record, policy)
        if problems:
            error = ValueError("; ".join(problems))
            retain_finalization_error_if_identifiable(
                policy,
                campaign_id=args.campaign_id,
                source_commit=args.source_commit,
                shard_size=shard_size,
                error=error,
            )
            print("refusing to write invalid campaign record:", file=sys.stderr)
            for problem in problems:
                print(f"- {problem}", file=sys.stderr)
            return 1
        path = write_record(record)
        digest = sha256_bytes(path.read_bytes())
        print(f"recorded {path.relative_to(ROOT)} sha256={digest}")
        print("Anchor this exact record in the campaign policy, then regenerate state.")
        return 0

    records, problems = load_records(policy)
    if args.replay and not problems:
        for record in records:
            problems.extend(
                f"{record['campaign_id']}: {item}"
                for item in replay_record(record)
            )
    state = build_state(policy, records)
    payload = rendered_json(state)
    if args.check:
        if problems:
            for problem in problems:
                print(problem, file=sys.stderr)
            return 1
        if not STATE_PATH.exists() or STATE_PATH.read_text(encoding="utf-8") != payload:
            print(f"hypothesis campaign check failed: stale {STATE_PATH}", file=sys.stderr)
            return 1
    else:
        if problems:
            for problem in problems:
                print(problem, file=sys.stderr)
            return 1
        STATE_PATH.write_text(payload, encoding="utf-8", newline="\n")
    if args.summary or args.check:
        counts = state["counts"]
        print(
            "HYP_CAMPAIGN_OK "
            f"records={counts['campaign_records']} "
            f"distinct_roots={counts['distinct_space_instance_roots']} "
            f"unique_cells={counts['unique_universe_cells']} "
            f"repeated={counts['repeated_cells_processed']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
