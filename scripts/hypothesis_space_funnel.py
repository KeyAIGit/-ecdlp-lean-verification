#!/usr/bin/env python3
"""High-throughput, non-executing screening of typed research-question cells."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import struct
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from hypothesis_funnel import (
    Operator,
    canonical_json_bytes,
    canonical_lf_sha256,
    challenge_indices,
    derive_warnings,
    generated_scope,
    generation_policy_digest,
    known_pattern_rejections,
    load_base_questions,
    load_operators,
    load_policy as load_parent_policy_file,
    metric_vector,
    normalized_text,
    semantic_anchor,
    sha256_json,
    unsafe_scope_rejections,
)


ROOT = Path(__file__).resolve().parent.parent
POLICY_PATH = ROOT / "repo" / "HYPOTHESIS_SPACE_V2.json"
STATE_PATH = ROOT / "data" / "hypothesis_space_state.json"
MAP_PATH = ROOT / "data" / "hypothesis_space_map.json"


@dataclass(frozen=True)
class Challenge:
    id: str
    label: str
    compatible_types: frozenset[str]


@dataclass(frozen=True)
class LiteCandidate:
    base_index: int
    mechanism_index: int
    cost_index: int
    test_index: int
    challenge_index: int
    dimensions: tuple[int, ...]

    @property
    def stable_key(self) -> tuple[int, ...]:
        return (
            self.base_index,
            self.challenge_index,
            self.mechanism_index,
            self.cost_index,
            self.test_index,
        )


class FastStreamingMerkle:
    """RFC6962 frontier accepting leaf hashes that already include the 0x00 prefix."""

    def __init__(self) -> None:
        self.frontier: list[bytes | None] = []
        self.count = 0

    @staticmethod
    def node_hash(left: bytes, right: bytes) -> bytes:
        return hashlib.sha256(b"\x01" + left + right).digest()

    def add_leaf_hash(self, leaf_hash: bytes) -> None:
        if len(leaf_hash) != 32:
            raise ValueError("leaf hash must contain 32 bytes")
        height = 0
        carry = leaf_hash
        index = self.count
        while index & 1:
            carry = self.node_hash(self.frontier[height], carry)  # type: ignore[arg-type]
            self.frontier[height] = None
            index >>= 1
            height += 1
        if height == len(self.frontier):
            self.frontier.append(carry)
        else:
            self.frontier[height] = carry
        self.count += 1

    def root_bytes(self) -> bytes:
        root: bytes | None = None
        for item in self.frontier:
            if item is not None:
                root = item if root is None else self.node_hash(item, root)
        return root if root is not None else hashlib.sha256(b"").digest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected an object")
    return value


def validate_policy(policy: dict[str, Any]) -> None:
    if policy.get("status") != "shadow_non_executing":
        raise ValueError("million-scale space must remain shadow_non_executing")
    if policy.get("schema_version") != "2.0":
        raise ValueError("unsupported hypothesis-space schema")
    safety = policy.get("safety", {})
    if (
        safety.get("all_outputs_executable") is not False
        or safety.get("experiments_authorized") is not False
        or safety.get("admissible") != 0
        or safety.get("recommended") != 0
        or safety.get("authorized") != 0
        or safety.get("route_promotions") != 0
        or safety.get("exact_target_execution") is not False
        or safety.get("language_model_calls") != 0
    ):
        raise ValueError("hypothesis-space safety boundary drifted")
    challenges = policy.get("adversarial_challenges")
    if not isinstance(challenges, list) or len(challenges) != 10:
        raise ValueError("expected exactly ten adversarial challenges")
    challenge_ids = [item.get("id") for item in challenges if isinstance(item, dict)]
    if len(challenge_ids) != len(challenges) or len(set(challenge_ids)) != len(challenges):
        raise ValueError("adversarial challenge IDs must be unique")
    if challenge_ids != sorted(challenge_ids):
        raise ValueError("adversarial challenges must be sorted by stable ID")
    reasons = policy.get("screening", {}).get("hard_rejections")
    if not isinstance(reasons, list) or not reasons or len(reasons) != len(set(reasons)):
        raise ValueError("hard rejection registry must be nonempty and unique")


def load_policy(path: Path = POLICY_PATH) -> dict[str, Any]:
    policy = load_json(path)
    validate_policy(policy)
    return policy


def load_parent(policy: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    binding = policy["parent_funnel"]
    parent_policy_path = ROOT / binding["policy_path"]
    parent_state_path = ROOT / binding["state_path"]
    parent_policy = load_parent_policy_file(parent_policy_path)
    parent_state = load_json(parent_state_path)
    if parent_policy.get("funnel_id") != binding["expected_funnel_id"]:
        raise ValueError("parent funnel ID drifted")
    if parent_state.get("funnel_id") != binding["expected_funnel_id"]:
        raise ValueError("parent state funnel ID drifted")
    if parent_state.get("counts", {}).get("attempts") != binding["expected_attempts"]:
        raise ValueError("parent funnel attempt count drifted")
    if (
        parent_state.get("bulk_contract", {}).get("merkle_root_sha256")
        != binding["expected_merkle_root_sha256"]
    ):
        raise ValueError("parent funnel root drifted")
    return parent_policy, parent_state


def load_challenges(policy: dict[str, Any]) -> list[Challenge]:
    challenges: list[Challenge] = []
    allowed = {"ATTACK", "BARRIER", "ENABLING"}
    for raw in policy["adversarial_challenges"]:
        if set(raw) != {"id", "label", "compatible_types"}:
            raise ValueError(f"challenge {raw.get('id')}: unexpected fields")
        compatible = raw["compatible_types"]
        if (
            not isinstance(compatible, list)
            or not compatible
            or not set(compatible) <= allowed
            or len(compatible) != len(set(compatible))
        ):
            raise ValueError(f"challenge {raw['id']}: invalid compatible types")
        challenges.append(
            Challenge(raw["id"], raw["label"], frozenset(compatible))
        )
    return challenges


def typed_anchor_digest(base: dict[str, str]) -> bytes:
    payload = {
        "schema": "research-question-base-v2",
        "anchor": semantic_anchor(base),
        "type": base["type"],
    }
    return hashlib.sha256(canonical_json_bytes(payload)).digest()


def validate_injective_axes(
    bases: list[dict[str, str]],
    mechanisms: list[Operator],
    costs: list[Operator],
    tests: list[Operator],
    challenges: list[Challenge],
) -> list[bytes]:
    collections: list[tuple[str, list[str]]] = [
        ("base IDs", [item["id"] for item in bases]),
        ("mechanism IDs", [item.id for item in mechanisms]),
        ("cost IDs", [item.id for item in costs]),
        ("test IDs", [item.id for item in tests]),
        ("challenge IDs", [item.id for item in challenges]),
    ]
    for label, values in collections:
        if len(values) != len(set(values)):
            raise ValueError(f"{label} are not unique")
    anchors = [typed_anchor_digest(base) for base in bases]
    if len(anchors) != len(set(anchors)):
        raise ValueError("typed base semantic anchors are not unique")
    return anchors


def canonical_space_policy(
    policy: dict[str, Any], parent_policy: dict[str, Any]
) -> dict[str, Any]:
    frozen = copy.deepcopy(policy)
    frozen["adversarial_challenges"] = sorted(
        frozen["adversarial_challenges"], key=lambda item: item["id"]
    )
    frozen["parent_generation_policy"] = generation_policy_digest(parent_policy)
    return frozen


def source_bindings(
    policy: dict[str, Any], parent_policy: dict[str, Any], parent_state: dict[str, Any]
) -> dict[str, Any]:
    parent_policy_path = ROOT / policy["parent_funnel"]["policy_path"]
    parent_state_path = ROOT / policy["parent_funnel"]["state_path"]
    policy_sha = sha256_json(canonical_space_policy(policy, parent_policy))
    evidence_inputs = {
        relative: canonical_lf_sha256(ROOT / relative)
        for relative in sorted(policy["evidence_snapshot"]["paths"])
    }
    evidence = {
        "parent_policy_sha256": canonical_lf_sha256(parent_policy_path),
        "parent_state_sha256": canonical_lf_sha256(parent_state_path),
        "parent_generation_policy_sha256": generation_policy_digest(parent_policy),
        "parent_merkle_root_sha256": parent_state["bulk_contract"]["merkle_root_sha256"],
        "evidence_input_sha256": evidence_inputs,
    }
    evidence_sha = sha256_json(evidence)
    return {
        "generation_policy_path": str(POLICY_PATH.relative_to(ROOT)).replace("\\", "/"),
        "generation_policy_sha256": policy_sha,
        "evidence_snapshot_sha256": evidence_sha,
        **evidence,
    }


def load_feedback_context(policy: dict[str, Any]) -> dict[str, Any]:
    ledger_path = ROOT / "data" / "hypothesis_review_ledger.jsonl"
    reviews: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        ledger_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"review ledger line {line_number} is not an object")
        reviews.append(value)
    label_ids = [item.get("label_id") for item in reviews]
    if len(label_ids) != len(set(label_ids)):
        raise ValueError("review ledger contains duplicate label IDs")
    by_base: dict[str, Counter[str]] = defaultdict(Counter)
    independent = 0
    for item in reviews:
        snapshot = item.get("candidate_snapshot", {})
        review = item.get("review_record", {})
        base_id = snapshot.get("base_id")
        axes = review.get("independence", {})
        is_independent = (
            isinstance(axes, dict)
            and axes.get("source") is True
            and axes.get("model_family") is True
            and axes.get("context") is True
        )
        if isinstance(base_id, str):
            by_base[base_id]["review_records"] += 1
            if is_independent:
                by_base[base_id]["independent_review_records"] += 1
        independent += int(is_independent)
    engine = load_json(ROOT / "data" / "research_engine_state.json")
    counts = engine.get("counts", {})
    return {
        "review_records": len(reviews),
        "independent_review_records": independent,
        "review_records_by_base": {
            key: dict(value) for key, value in sorted(by_base.items())
        },
        "outcome_events": counts.get("outcome_events", 0),
        "historical_migration_outcomes": counts.get("outcomes_by_source", {}).get(
            "historical_migration", 0
        ),
        "native_engine_outcomes": counts.get("outcomes_by_source", {}).get(
            "native_engine_run", 0
        ),
        "external_bounded_outcomes": counts.get("outcomes_by_source", {}).get(
            "external_bounded_decision_run", 0
        ),
        "automatic_hot_promotions": 0,
        "binding_rule": policy["evidence_snapshot"]["feedback_rule"],
    }
def rejection_reasons(
    kind: str,
    mechanism: Operator,
    cost: Operator,
    test: Operator,
    challenge: Challenge,
    parent_policy: dict[str, Any],
) -> list[str]:
    safety = parent_policy["safety"]
    reasons: list[str] = []
    if kind not in safety["allowed_types"] or kind in safety["forbidden_types"]:
        reasons.append("forbidden_type")
    if kind not in mechanism.compatible_types:
        reasons.append("mechanism_type_mismatch")
    if kind not in cost.compatible_types:
        reasons.append("cost_type_mismatch")
    if kind not in test.compatible_types:
        reasons.append("test_type_mismatch")
    if kind not in challenge.compatible_types:
        reasons.append("challenge_type_mismatch")
    if kind == "ATTACK":
        if "attack_scaling_obligation" not in cost.capabilities:
            reasons.append("attack_without_scaling_bridge")
        if "attack_discriminating_test" not in test.capabilities:
            reasons.append("attack_without_discriminating_test")
    elif kind == "BARRIER":
        if "barrier_mechanism" not in mechanism.capabilities:
            reasons.append("barrier_without_scoped_mechanism")
    elif kind == "ENABLING":
        if "enabling_mechanism" not in mechanism.capabilities:
            reasons.append("enabling_without_dependency_bridge")
    reasons.extend(unsafe_scope_rejections(generated_scope(parent_policy), parent_policy))
    return reasons


def reasons_to_mask(reasons: list[str], reason_bits: dict[str, int]) -> int:
    mask = 0
    for reason in reasons:
        if reason not in reason_bits:
            raise ValueError(f"unregistered rejection reason: {reason}")
        mask |= 1 << reason_bits[reason]
    return mask


def mask_reasons(mask: int, ordered_reasons: list[str]) -> list[str]:
    return [reason for index, reason in enumerate(ordered_reasons) if mask & (1 << index)]


def dominates(left: tuple[int, ...], right: tuple[int, ...]) -> bool:
    return all(a >= b for a, b in zip(left, right)) and any(
        a > b for a, b in zip(left, right)
    )


def insert_front(front: list[LiteCandidate], candidate: LiteCandidate) -> None:
    for existing in front:
        if dominates(existing.dimensions, candidate.dimensions):
            return
    front[:] = [
        existing
        for existing in front
        if not dominates(candidate.dimensions, existing.dimensions)
    ]
    equal = [item for item in front if item.dimensions == candidate.dimensions]
    if len(equal) >= 2:
        worst = max(equal, key=lambda item: item.stable_key)
        if candidate.stable_key >= worst.stable_key:
            return
        front.remove(worst)
    front.append(candidate)
    front.sort(key=lambda item: item.stable_key)


def semantic_signature(
    base: dict[str, str],
    mechanism: Operator,
    cost: Operator,
    test: Operator,
    challenge: Challenge,
    threat_model: str,
) -> str:
    def operator_content(role: str, operator: Operator) -> dict[str, Any]:
        return {
            "role": role,
            "label": normalized_text(operator.label),
            "compatible_types": sorted(operator.compatible_types),
            "capabilities": sorted(operator.capabilities),
            "dimensions": dict(sorted(operator.dimensions.items())),
        }

    return sha256_json(
        {
            "schema": "research-question-challenge-cell-v2",
            "anchor": semantic_anchor(base),
            "type": base["type"],
            "mechanism_obligation": operator_content("mechanism", mechanism),
            "cost_bridge": operator_content("cost", cost),
            "decisive_test": operator_content("test", test),
            "adversarial_challenge": {
                "label": normalized_text(challenge.label),
                "compatible_types": sorted(challenge.compatible_types),
            },
            "threat_model": threat_model,
        }
    )


def public_candidate(
    candidate: LiteCandidate,
    bases: list[dict[str, str]],
    mechanisms: list[Operator],
    costs: list[Operator],
    tests: list[Operator],
    challenges: list[Challenge],
    dimensions: list[str],
    parent_policy: dict[str, Any],
    instance_root: str,
) -> dict[str, Any]:
    base = bases[candidate.base_index]
    mechanism = mechanisms[candidate.mechanism_index]
    cost = costs[candidate.cost_index]
    test = tests[candidate.test_index]
    challenge = challenges[candidate.challenge_index]
    signature = semantic_signature(
        base,
        mechanism,
        cost,
        test,
        challenge,
        parent_policy["safety"]["primary_threat_model"],
    )
    instance = sha256_json(
        {
            "semantic_signature_sha256": signature,
            "space_instance_root_sha256": instance_root,
        }
    )
    ordinal = (
        (
            (
                candidate.base_index * len(mechanisms)
                + candidate.mechanism_index
            )
            * len(costs)
            + candidate.cost_index
        )
        * len(tests)
        + candidate.test_index
    ) * len(challenges) + candidate.challenge_index
    return {
        "seed_id": f"HQS2-{instance[:32].upper()}",
        "scientific_signature_sha256": signature,
        "semantic_signature_sha256": signature,
        "evaluation_instance_sha256": instance,
        "batch_occurrence_ordinal": ordinal,
        "space_instance_root_sha256": instance_root,
        "scientific_identity": "research_question_challenge_cell",
        "base_id": base["id"],
        "family": base["family"],
        "type": base["type"],
        "short_claim": base["short_claim"],
        "mechanism_obligation_id": mechanism.id,
        "mechanism_obligation": mechanism.label,
        "cost_bridge_id": cost.id,
        "cost_bridge": cost.label,
        "decisive_test_id": test.id,
        "decisive_test": test.label,
        "adversarial_challenge_id": challenge.id,
        "adversarial_challenge": challenge.label,
        "dimensions": dict(zip(dimensions, candidate.dimensions)),
        "scope": generated_scope(parent_policy),
        "warnings": sorted(
            set(derive_warnings(base))
            | {"challenge_unresolved", "typed_identity_not_semantic_novelty"}
        ),
        "source_hard_gate": base["hard_gate"],
        "source_portfolio": base["portfolio"],
        "source_canonical": base["canonical"],
        "executable": False,
        "admissible": False,
        "recommended": False,
        "authorized": False,
        "route_promotion": False,
    }


def review_key(candidate: LiteCandidate) -> tuple[Any, ...]:
    minimum = min(candidate.dimensions)
    total = sum(candidate.dimensions)
    return (
        -minimum,
        -total,
        tuple(-value for value in candidate.dimensions),
        candidate.stable_key,
    )


def choose_review_queue(
    candidates: list[LiteCandidate],
    bases: list[dict[str, str]],
    mechanisms: list[Operator],
    challenges: list[Challenge],
    policy: dict[str, Any],
) -> list[LiteCandidate]:
    config = policy["portfolio"]
    ordered = sorted(candidates, key=review_key)
    queue: list[LiteCandidate] = []
    base_counts: Counter[str] = Counter()
    family_counts: Counter[str] = Counter()
    challenge_counts: Counter[str] = Counter()
    mechanism_counts: Counter[str] = Counter()

    def add(candidate: LiteCandidate) -> bool:
        base = bases[candidate.base_index]
        challenge = challenges[candidate.challenge_index]
        mechanism = mechanisms[candidate.mechanism_index]
        if base_counts[base["id"]] >= config["max_per_base_question"]:
            return False
        if family_counts[base["family"]] >= config["max_per_family"]:
            return False
        if challenge_counts[challenge.id] >= config["max_per_challenge"]:
            return False
        if mechanism_counts[mechanism.id] >= config["max_per_mechanism_obligation"]:
            return False
        queue.append(candidate)
        base_counts[base["id"]] += 1
        family_counts[base["family"]] += 1
        challenge_counts[challenge.id] += 1
        mechanism_counts[mechanism.id] += 1
        return True

    for kind in config["required_types_if_available"]:
        for candidate in ordered:
            if bases[candidate.base_index]["type"] == kind and add(candidate):
                break
    for candidate in ordered:
        if len(queue) >= config["max_review_queue"]:
            break
        if candidate not in queue:
            add(candidate)
    return queue


def sample_record(
    base: dict[str, str],
    mechanism: Operator,
    cost: Operator,
    test: Operator,
    challenge: Challenge,
) -> dict[str, Any]:
    return {
        "base_id": base["id"],
        "family": base["family"],
        "type": base["type"],
        "mechanism_obligation_id": mechanism.id,
        "cost_bridge_id": cost.id,
        "decisive_test_id": test.id,
        "adversarial_challenge_id": challenge.id,
    }


def run_space(
    policy: dict[str, Any] | None = None,
    *,
    attempt_limit: int | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    policy = copy.deepcopy(policy or load_policy())
    validate_policy(policy)
    parent_policy, parent_state = load_parent(policy)
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
    challenges = load_challenges(policy)
    anchor_digests = validate_injective_axes(
        bases, mechanisms, costs, tests, challenges
    )
    dimensions = policy["portfolio"]["dimension_names"]
    if dimensions != parent_policy["portfolio"]["dimension_names"]:
        raise ValueError("portfolio dimensions drifted from the parent funnel")
    expected = (
        len(bases) * len(mechanisms) * len(costs) * len(tests) * len(challenges)
    )
    if expected != policy["expansion"]["expected_signatures"]:
        raise ValueError(
            f"typed universe mismatch: policy expects "
            f"{policy['expansion']['expected_signatures']}, got {expected}"
        )
    limit = expected if attempt_limit is None else attempt_limit
    if limit < 0 or limit > expected:
        raise ValueError("attempt_limit outside the typed universe")

    bindings = source_bindings(policy, parent_policy, parent_state)
    feedback = load_feedback_context(policy)
    ordered_reasons = policy["screening"]["hard_rejections"]
    reason_bits = {reason: index for index, reason in enumerate(ordered_reasons)}
    warning_names = policy["screening"]["warnings"]
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
            raise ValueError(f"unregistered warnings: {sorted(unknown)}")
        base_warning_masks.append(
            sum(1 << warning_bits[warning] for warning in warnings)
        )
        base_pattern_masks.append(
            [
                reasons_to_mask(
                    known_pattern_rejections(base, mechanism, parent_policy),
                    reason_bits,
                )
                for mechanism in mechanisms
            ]
        )

    type_combos: dict[str, list[tuple[int, int, int, int, int, tuple[int, ...]]]] = {}
    for kind in sorted({base["type"] for base in bases}):
        combos: list[tuple[int, int, int, int, int, tuple[int, ...]]] = []
        for mi, mechanism in enumerate(mechanisms):
            for ci, cost in enumerate(costs):
                for ti, test in enumerate(tests):
                    vector = metric_vector(mechanism, cost, test, dimensions)
                    dims = tuple(vector[name] for name in dimensions)
                    if any(not 0 <= value <= 255 for value in dims):
                        raise ValueError("dimension value does not fit the binary leaf format")
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

    merkle = FastStreamingMerkle()
    mask_counts: Counter[int] = Counter()
    type_counts: Counter[str] = Counter()
    challenge_counts: dict[str, Counter[str]] = {
        challenge.id: Counter() for challenge in challenges
    }
    region_counts: dict[str, dict[str, Any]] = {}
    samples: dict[str, list[dict[str, Any]]] = defaultdict(list)
    fronts: dict[tuple[int, int], list[LiteCandidate]] = defaultdict(list)
    attempts = 0
    warm = 0
    cold = 0
    leaf_prefix = b"HQS-CELL-V2\x00"
    packer = struct.Struct(">4BII7B")

    for bi, base in enumerate(bases):
        family = base["family"]
        region = region_counts.setdefault(
            family,
            {
                "type": base["type"],
                "base_ids": [],
                "cells": 0,
                "cold": 0,
                "warm": 0,
                "hot": 0,
                "retained_by_challenge": Counter(),
                "primary_rejections": Counter(),
                "review_records": 0,
                "independent_review_records": 0,
            },
        )
        region["base_ids"].append(base["id"])
        base_feedback = feedback["review_records_by_base"].get(base["id"], {})
        region["review_records"] += base_feedback.get("review_records", 0)
        region["independent_review_records"] += base_feedback.get(
            "independent_review_records", 0
        )
        warning_mask = base_warning_masks[bi]
        combos = type_combos[base["type"]]
        for mi, ci, ti, gi, static_mask, dims in combos:
            if attempts >= limit:
                break
            mask = static_mask | base_pattern_masks[bi][mi]
            cell = (
                leaf_prefix
                + anchor_digests[bi]
                + packer.pack(mi, ci, ti, gi, mask, warning_mask, *dims)
            )
            merkle.add_leaf_hash(hashlib.sha256(b"\x00" + cell).digest())
            mask_counts[mask] += 1
            type_counts[base["type"]] += 1
            challenge = challenges[gi]
            challenge_counts[challenge.id]["attempts"] += 1
            region["cells"] += 1
            if mask:
                cold += 1
                challenge_counts[challenge.id]["cold"] += 1
                region["cold"] += 1
                reasons = mask_reasons(mask, ordered_reasons)
                region["primary_rejections"][reasons[0]] += 1
                for reason in reasons:
                    if len(samples[reason]) < 3:
                        samples[reason].append(
                            sample_record(
                                base,
                                mechanisms[mi],
                                costs[ci],
                                tests[ti],
                                challenge,
                            )
                        )
            else:
                warm += 1
                challenge_counts[challenge.id]["warm"] += 1
                region["warm"] += 1
                region["retained_by_challenge"][challenge.id] += 1
                insert_front(
                    fronts[(bi, gi)],
                    LiteCandidate(bi, mi, ci, ti, gi, dims),
                )
            attempts += 1
        if attempts >= limit:
            break

    if attempts != limit or merkle.count != limit:
        raise AssertionError("attempt coverage mismatch")
    coverage_root = merkle.root_bytes().hex()
    context = (
        b"HYPOTHESIS-SPACE-INSTANCE-V2\x00"
        + bytes.fromhex(bindings["generation_policy_sha256"])
        + bytes.fromhex(bindings["evidence_snapshot_sha256"])
        + bytes.fromhex(bindings["parent_merkle_root_sha256"])
        + bytes.fromhex(coverage_root)
        + attempts.to_bytes(8, "big")
    )
    instance_root = hashlib.sha256(context).hexdigest()
    candidates = [item for key in sorted(fronts) for item in fronts[key]]
    queue_lite = choose_review_queue(
        candidates, bases, mechanisms, challenges, policy
    )
    queue = [
        public_candidate(
            candidate,
            bases,
            mechanisms,
            costs,
            tests,
            challenges,
            dimensions,
            parent_policy,
            instance_root,
        )
        for candidate in queue_lite
    ]

    rejection_histogram: Counter[str] = Counter()
    primary_histogram: Counter[str] = Counter()
    for mask, count in mask_counts.items():
        reasons = mask_reasons(mask, ordered_reasons)
        for reason in reasons:
            rejection_histogram[reason] += count
        if reasons:
            primary_histogram[reasons[0]] += count
    warning_histogram: Counter[str] = Counter()
    combinations_per_base = len(mechanisms) * len(costs) * len(tests) * len(challenges)
    completed_bases, remainder = divmod(attempts, combinations_per_base)
    for bi, base in enumerate(bases[: completed_bases + (1 if remainder else 0)]):
        count = combinations_per_base if bi < completed_bases else remainder
        for warning in derive_warnings(base):
            warning_histogram[warning] += count
        warning_histogram["challenge_unresolved"] += count
        warning_histogram["typed_identity_not_semantic_novelty"] += count

    full_run = attempt_limit is None
    state = {
        "schema_version": "2.0-generated",
        "space_id": policy["space_id"],
        "status": "shadow_non_executing",
        "scientific_identity": "evidence_bounded_research_question_space",
        "baseline_commit": policy["baseline_commit"],
        "source_bindings": bindings,
        "bulk_contract": {
            "attempt_count": attempts,
            "full_universe_count": expected,
            "raw_signatures_materialized": False,
            "typed_tuple_uniqueness_checked": True,
            "semantic_novelty_proved": False,
            "language_model_calls": 0,
            "authorization": "none",
            "route_promotion": False,
            "exact_target_execution": False,
            "stream_digest_version": policy["expansion"]["stream_digest_version"],
            "coverage_merkle_root_sha256": coverage_root,
            "instance_root_sha256": instance_root,
            "challenge_indices": challenge_indices(instance_root, attempts),
        },
        "counts": {
            "attempts": attempts,
            "typed_cells": attempts,
            "cold": cold,
            "warm": warm,
            "hot": 0,
            "pareto_records_before_review_queue": len(candidates),
            "review_queue": len(queue),
            "admissible": 0,
            "recommended": 0,
            "authorized": 0,
            "route_promotions": 0,
            "experiment_events": 0,
        },
        "counts_by_type": dict(sorted(type_counts.items())),
        "challenge_coverage": {
            key: dict(sorted(value.items()))
            for key, value in sorted(challenge_counts.items())
        },
        "rejection_histogram": dict(sorted(rejection_histogram.items())),
        "primary_rejection_histogram": dict(sorted(primary_histogram.items())),
        "warning_histogram": dict(sorted(warning_histogram.items())),
        "rejection_samples": {key: value for key, value in sorted(samples.items())},
        "review_queue": queue if full_run else [],
        "memory_contract": {
            "raw_record_retention": 0,
            "sqlite_rows": 0,
            "merkle_frontier_max_nodes": len(merkle.frontier),
            "review_queue_limit": policy["portfolio"]["max_review_queue"],
            "region_map_is_aggregate_only": True,
        },
        "performance_contract": policy["performance_contract"],
        "feedback_context": feedback,
        "boundaries": [
            "One million cells are typed combinations, not one million independently invented hypotheses.",
            "The map is complete only for the frozen finite projection and does not cover all ECDLP ideas or literature.",
            "Typed tuple uniqueness is not semantic novelty or mathematical correctness.",
            "Warm cells still lack an assured exact mechanism, cost bridge, and independent source review.",
            "This generator cannot create hot, admissible, recommended, authorized, executable, or route-promoting state."
        ],
    }

    regions: list[dict[str, Any]] = []
    for family, raw in sorted(region_counts.items()):
        regions.append(
            {
                "family": family,
                "type": raw["type"],
                "base_ids": sorted(set(raw["base_ids"])),
                "cells": raw["cells"],
                "cold": raw["cold"],
                "warm": raw["warm"],
                "hot": 0,
                "retained_by_challenge": dict(
                    sorted(raw["retained_by_challenge"].items())
                ),
                "primary_rejections": dict(
                    sorted(raw["primary_rejections"].items())
                ),
                "review_records": raw["review_records"],
                "independent_review_records": raw[
                    "independent_review_records"
                ],
            }
        )
    map_state = {
        "schema_version": "2.0-generated",
        "space_id": policy["space_id"],
        "status": "evidence_bounded_projection",
        "instance_root_sha256": instance_root,
        "coverage_boundary": policy["map_contract"]["coverage_boundary"],
        "temperature_legend": {
            "cold": policy["map_contract"]["cold"],
            "warm": policy["map_contract"]["warm"],
            "hot": policy["map_contract"]["hot"],
        },
        "counts": state["counts"],
        "regions": regions,
        "review_queue_seed_ids": [item["seed_id"] for item in state["review_queue"]],
        "feedback_context": feedback,
        "authorization": "none",
    }
    return state, map_state


def json_payload(value: dict[str, Any]) -> str:
    return json.dumps(
        value,
        ensure_ascii=True,
        indent=2,
        sort_keys=False,
        allow_nan=False,
    ) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--benchmark", action="store_true")
    args = parser.parse_args()

    started = time.perf_counter()
    state, map_state = run_space()
    elapsed = time.perf_counter() - started
    outputs = ((STATE_PATH, state), (MAP_PATH, map_state))
    for path, value in outputs:
        payload = json_payload(value)
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != payload:
                print(f"hypothesis space check failed: stale {path}", file=sys.stderr)
                return 1
        else:
            path.write_text(payload, encoding="utf-8", newline="\n")

    if args.summary or args.check or args.benchmark:
        counts = state["counts"]
        print(
            "HYP_SPACE_OK "
            f"attempts={counts['attempts']} cold={counts['cold']} "
            f"warm={counts['warm']} hot={counts['hot']} "
            f"review_queue={counts['review_queue']} "
            f"root={state['bulk_contract']['instance_root_sha256']}"
        )
    if args.benchmark:
        rate = state["counts"]["attempts"] / elapsed
        target = state["performance_contract"]["target_signatures_per_minute"] / 60
        verdict = "target_met" if rate >= target else "target_not_met"
        print(
            f"HYP_SPACE_BENCH elapsed_seconds={elapsed:.6f} "
            f"signatures_per_second={rate:.2f} "
            f"signatures_per_minute={rate * 60:.0f} verdict={verdict}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
