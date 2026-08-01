#!/usr/bin/env python3
"""Stream and screen 100,000 non-executable research-question signatures.

The bulk layer deliberately emits no prose hypotheses, candidates,
authorizations, route promotions, or experiment events. It binds a compact
replay artifact to a frozen input pool and policy.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import itertools
import json
import sqlite3
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parent.parent
POLICY_PATH = ROOT / "repo" / "HYPOTHESIS_FUNNEL_V1.json"
STATE_PATH = ROOT / "data" / "hypothesis_funnel_state.json"


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


def canonical_lf_bytes(path: Path) -> bytes:
    text = path.read_text(encoding="utf-8")
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def canonical_lf_sha256(path: Path) -> str:
    return hashlib.sha256(canonical_lf_bytes(path)).hexdigest()


def normalized_text(value: str) -> str:
    return " ".join(value.strip().lower().split())


class StreamingMerkle:
    """RFC6962-style Merkle accumulator using O(log N) memory."""

    def __init__(self) -> None:
        self.frontier: list[bytes | None] = []
        self.count = 0

    @staticmethod
    def leaf_hash(payload: bytes) -> bytes:
        return hashlib.sha256(b"\x00" + payload).digest()

    @staticmethod
    def node_hash(left: bytes, right: bytes) -> bytes:
        return hashlib.sha256(b"\x01" + left + right).digest()

    def add_payload(self, payload: bytes) -> str:
        leaf = self.leaf_hash(payload)
        node = leaf
        level = 0
        while level < len(self.frontier) and self.frontier[level] is not None:
            node = self.node_hash(self.frontier[level], node)  # type: ignore[arg-type]
            self.frontier[level] = None
            level += 1
        if level == len(self.frontier):
            self.frontier.append(node)
        else:
            self.frontier[level] = node
        self.count += 1
        return leaf.hex()

    def root(self) -> str:
        root: bytes | None = None
        for node in self.frontier:
            if node is None:
                continue
            root = node if root is None else self.node_hash(node, root)
        return root.hex() if root is not None else hashlib.sha256(b"").hexdigest()


@dataclass(frozen=True)
class Operator:
    id: str
    label: str
    compatible_types: tuple[str, ...]
    capabilities: tuple[str, ...]
    dimensions: dict[str, int]


def load_policy(path: Path = POLICY_PATH) -> dict[str, Any]:
    policy = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "schema_version",
        "funnel_id",
        "status",
        "baseline_commit",
        "constitution",
        "input_pool",
        "evidence_snapshot",
        "expansion",
        "safety",
        "mechanism_obligations",
        "cost_bridges",
        "decisive_tests",
        "screening",
        "portfolio",
        "review_decisions",
    }
    missing = sorted(required - set(policy))
    if missing:
        raise ValueError(f"policy missing keys: {missing}")
    if policy["status"] != "shadow_non_executing":
        raise ValueError("funnel status must remain shadow_non_executing")
    safety = policy["safety"]
    if (
        safety.get("all_outputs_executable") is not False
        or safety.get("experiments_authorized") is not False
        or safety.get("route_promotions") != 0
    ):
        raise ValueError("policy crosses the non-execution boundary")
    constitution = policy["constitution"]
    constitution_path = ROOT / constitution["path"]
    if canonical_lf_sha256(constitution_path) != constitution["canonical_lf_sha256"]:
        raise ValueError("hypothesis-selection constitution digest mismatch")
    return policy


def load_operators(raw: list[dict[str, Any]], label: str) -> list[Operator]:
    if len(raw) != 10:
        raise ValueError(f"{label}: expected exactly 10 operators, got {len(raw)}")
    operators = [
        Operator(
            id=item["id"],
            label=item["label"],
            compatible_types=tuple(sorted(item["compatible_types"])),
            capabilities=tuple(sorted(item.get("capabilities", []))),
            dimensions={key: int(value) for key, value in item["dimensions"].items()},
        )
        for item in raw
    ]
    operators.sort(key=lambda item: item.id)
    if len({item.id for item in operators}) != len(operators):
        raise ValueError(f"{label}: duplicate operator id")
    return operators


def load_base_questions(policy: dict[str, Any]) -> list[dict[str, str]]:
    spec = policy["input_pool"]
    path = ROOT / spec["path"]
    if not path.exists():
        raise ValueError(f"input pool missing: {spec['path']}")
    actual_sha = canonical_lf_sha256(path)
    if actual_sha != spec["sha256"]:
        raise ValueError(
            f"input pool digest mismatch: expected {spec['sha256']}, got {actual_sha}"
        )
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    expected_columns = {
        "id",
        "family",
        "type",
        "hard_gate",
        "portfolio",
        "canonical",
        "short_claim",
    }
    if not rows or set(rows[0]) != expected_columns:
        raise ValueError("input pool columns do not match the frozen contract")
    if len(rows) != spec["expected_rows"]:
        raise ValueError(
            f"input pool row count mismatch: expected {spec['expected_rows']}, "
            f"got {len(rows)}"
        )
    if len({row["id"] for row in rows}) != len(rows):
        raise ValueError("input pool contains duplicate ids")
    if any(not all(value.strip() for value in row.values()) for row in rows):
        raise ValueError("input pool contains an empty field")
    return sorted(rows, key=lambda row: row["id"])


def canonical_generation_policy(policy: dict[str, Any]) -> dict[str, Any]:
    frozen = copy.deepcopy(policy)
    frozen["review_decisions"] = []
    for key in ("mechanism_obligations", "cost_bridges", "decisive_tests"):
        for item in frozen[key]:
            item["compatible_types"] = sorted(item["compatible_types"])
            item["capabilities"] = sorted(item.get("capabilities", []))
        frozen[key] = sorted(frozen[key], key=lambda item: item["id"])
    return frozen


def generation_policy_digest(policy: dict[str, Any]) -> str:
    return sha256_json(canonical_generation_policy(policy))


def evidence_snapshot(policy: dict[str, Any]) -> tuple[dict[str, str], str]:
    hashes: dict[str, str] = {}
    for relative in sorted(policy["evidence_snapshot"]["paths"]):
        path = ROOT / relative
        if not path.exists() or not path.is_file():
            raise ValueError(f"evidence snapshot path missing: {relative}")
        hashes[relative] = canonical_lf_sha256(path)
    return hashes, sha256_json(hashes)


def semantic_anchor(base: dict[str, str]) -> dict[str, str]:
    return {
        "kind": "brainstorm_family",
        "value": base["family"],
        "claim": normalized_text(base["short_claim"]),
        "type": base["type"],
    }


def metric_vector(
    mechanism: Operator,
    cost: Operator,
    test: Operator,
    names: list[str],
) -> dict[str, int]:
    combined = {}
    combined.update(mechanism.dimensions)
    combined.update(cost.dimensions)
    combined.update(test.dimensions)
    missing = [name for name in names if name not in combined]
    if missing:
        raise ValueError(f"operator combination missing dimensions: {missing}")
    return {name: combined[name] for name in names}


def generated_scope(policy: dict[str, Any]) -> dict[str, Any]:
    safety = policy["safety"]
    return {
        "lane": "research_question_seed",
        "threat_model": safety["primary_threat_model"],
        "execution_target": None,
        "field_bits": None,
        "executable": False,
    }


def unsafe_scope_rejections(
    scope: dict[str, Any], policy: dict[str, Any]
) -> list[str]:
    safety = policy["safety"]
    target = scope.get("execution_target")
    field_bits = scope.get("field_bits")
    unsafe = (
        scope.get("lane") != "research_question_seed"
        or scope.get("threat_model") != safety["primary_threat_model"]
        or scope.get("executable") is not False
        or target in set(safety["forbidden_targets"])
        or (field_bits is not None and field_bits > safety["max_toy_field_bits"])
    )
    return ["unsafe_or_exact_target_scope"] if unsafe else []


def known_pattern_rejections(
    base: dict[str, str],
    mechanism: Operator,
    policy: dict[str, Any],
) -> list[str]:
    text = normalized_text(f"{base['family']} {base['short_claim']}")
    reasons: list[str] = []
    for pattern in policy["screening"]["known_closed_patterns"]:
        terms = [normalized_text(term) for term in pattern["family_terms"]]
        family_match = base["family"] in pattern.get("base_families", [])
        lexical_match = all(term in text for term in terms)
        if family_match or lexical_match:
            if mechanism.id not in pattern["reopening_mechanisms"]:
                reasons.append("known_closed_pattern_unreopened")
    return reasons


def derive_rejections(
    base: dict[str, str],
    mechanism: Operator,
    cost: Operator,
    test: Operator,
    policy: dict[str, Any],
    scope: dict[str, Any] | None = None,
) -> list[str]:
    kind = base["type"]
    reasons: list[str] = []
    safety = policy["safety"]
    if kind not in safety["allowed_types"] or kind in safety["forbidden_types"]:
        reasons.append("forbidden_type")
    if kind not in mechanism.compatible_types:
        reasons.append("mechanism_type_mismatch")
    if kind not in cost.compatible_types:
        reasons.append("cost_type_mismatch")
    if kind not in test.compatible_types:
        reasons.append("test_type_mismatch")

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

    reasons.extend(unsafe_scope_rejections(scope or generated_scope(policy), policy))
    reasons.extend(known_pattern_rejections(base, mechanism, policy))
    return sorted(set(reasons))


def derive_warnings(base: dict[str, str]) -> list[str]:
    warnings = [
        "novelty_unverified",
        "exact_mechanism_missing",
        "source_independence_unestablished",
    ]
    if base["hard_gate"] == "KILL":
        warnings.append("historical_kill_label")
    elif base["hard_gate"] == "REFORMULATE":
        warnings.append("historical_reformulate_label")
    if base["portfolio"] == "SHORTLIST":
        warnings.append("historical_shortlist_label")
    if base["canonical"] != "-":
        warnings.append("historical_canonical_cluster")
    return sorted(warnings)


def dominates(left: dict[str, Any], right: dict[str, Any], names: list[str]) -> bool:
    left_values = left["dimensions"]
    right_values = right["dimensions"]
    return all(left_values[name] >= right_values[name] for name in names) and any(
        left_values[name] > right_values[name] for name in names
    )


def insert_pareto(
    archive: list[dict[str, Any]],
    record: dict[str, Any],
    names: list[str],
    *,
    equal_limit: int = 4,
) -> None:
    if any(dominates(existing, record, names) for existing in archive):
        return
    kept = [
        existing
        for existing in archive
        if not dominates(record, existing, names)
    ]
    same = [
        existing
        for existing in kept
        if existing["dimensions"] == record["dimensions"]
    ]
    if len(same) >= equal_limit:
        worst = max(same, key=stable_record_key)
        if stable_record_key(record) >= stable_record_key(worst):
            archive[:] = kept
            return
        kept.remove(worst)
    kept.append(record)
    archive[:] = kept


def sample_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "seed_id": record["seed_id"],
        "base_id": record["base_id"],
        "family": record["family"],
        "type": record["type"],
        "mechanism_obligation_id": record["mechanism_obligation_id"],
        "cost_bridge_id": record["cost_bridge_id"],
        "decisive_test_id": record["decisive_test_id"],
    }


def retain_smallest_sample(
    samples: dict[str, list[dict[str, Any]]],
    bucket: str,
    record: dict[str, Any],
    *,
    limit: int = 3,
) -> None:
    values = samples[bucket]
    values.append(sample_record(record))
    values.sort(key=lambda item: item["seed_id"])
    del values[limit:]


def stable_record_key(record: dict[str, Any]) -> str:
    return record["semantic_signature_sha256"]


def review_priority(record: dict[str, Any]) -> tuple[Any, ...]:
    dimensions = record["dimensions"]
    return (
        -min(dimensions.values()),
        tuple(-dimensions[key] for key in sorted(dimensions)),
        stable_record_key(record),
    )


def choose_review_queue(
    candidates: list[dict[str, Any]],
    policy: dict[str, Any],
) -> list[dict[str, Any]]:
    config = policy["portfolio"]
    names = config["dimension_names"]
    per_type: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for candidate in candidates:
        insert_pareto(per_type[candidate["type"]], candidate, names, equal_limit=512)

    ordered: list[dict[str, Any]] = []
    types = [
        kind
        for kind in config["required_types_if_available"]
        if per_type.get(kind)
    ]
    for kind in sorted(per_type):
        if kind not in types:
            types.append(kind)
    for kind in types:
        ordered.extend(sorted(per_type[kind], key=review_priority))

    queue: list[dict[str, Any]] = []
    base_counts: Counter[str] = Counter()
    family_counts: Counter[str] = Counter()
    mechanism_counts: Counter[str] = Counter()
    for candidate in ordered:
        if base_counts[candidate["base_id"]] >= config["max_per_base_question"]:
            continue
        if family_counts[candidate["family"]] >= config["max_per_family"]:
            continue
        if (
            mechanism_counts[candidate["mechanism_obligation_id"]]
            >= config["max_per_mechanism_obligation"]
        ):
            continue
        queue.append(candidate)
        base_counts[candidate["base_id"]] += 1
        family_counts[candidate["family"]] += 1
        mechanism_counts[candidate["mechanism_obligation_id"]] += 1
        if len(queue) >= config["max_review_queue"]:
            break
    return queue


def compile_review_decisions(
    queue: list[dict[str, Any]],
    policy: dict[str, Any],
) -> list[dict[str, Any]]:
    queue_by_signature = {
        item["semantic_signature_sha256"]: item for item in queue
    }
    decisions = policy["review_decisions"]
    signatures = [item.get("semantic_signature_sha256") for item in decisions]
    if len(set(signatures)) != len(decisions):
        raise ValueError("review_decisions contains duplicate semantic signatures")
    review_ids = [item.get("review_id") for item in decisions]
    if len(set(review_ids)) != len(decisions):
        raise ValueError("review_decisions contains duplicate review ids")
    if not set(signatures).issubset(queue_by_signature):
        extra = sorted(set(signatures) - set(queue_by_signature))
        raise ValueError(
            "review_decisions references signatures outside the review queue: "
            f"extra={extra}"
        )

    retained: list[dict[str, Any]] = []
    for decision in decisions:
        required = {
            "review_id",
            "semantic_signature_sha256",
            "verdict",
            "portfolio_role",
            "reviewed_at",
            "reviewer",
            "independence",
            "canonical_binding",
            "decision_protocol",
            "limitations",
        }
        missing = sorted(required - set(decision))
        if missing:
            raise ValueError(f"review decision missing keys: {missing}")
        if not isinstance(decision["review_id"], str) or not decision[
            "review_id"
        ].strip():
            raise ValueError("review decision has an empty review_id")
        reviewer = decision["reviewer"]
        if set(reviewer) != {"actor_id", "role"} or not all(
            isinstance(value, str) and value.strip() for value in reviewer.values()
        ):
            raise ValueError("review decision has invalid reviewer provenance")
        independence = decision["independence"]
        if set(independence) != {"source", "model_family", "context"} or not all(
            isinstance(value, bool) for value in independence.values()
        ):
            raise ValueError("review decision has invalid independence record")
        protocol = decision["decision_protocol"]
        protocol_keys = {
            "claim",
            "basis",
            "counterargument",
            "decisive_test",
            "verdict",
        }
        if set(protocol) != protocol_keys or not all(
            isinstance(value, str) and value.strip() for value in protocol.values()
        ):
            raise ValueError("review decision has an incomplete decision_protocol")
        limitations = decision["limitations"]
        if not isinstance(limitations, list) or not limitations or not all(
            isinstance(value, str) and value.strip() for value in limitations
        ):
            raise ValueError("review decision must retain nonempty limitations")
        validate_canonical_binding(decision["canonical_binding"])

        allowed_verdicts = {
            "retain_non_executable_research_bet",
            "merge_into_retained",
            "defer_insufficient_evidence",
            "reject_known_or_unsupported",
        }
        if decision["verdict"] not in allowed_verdicts:
            raise ValueError(f"unknown review verdict: {decision['verdict']}")
        if decision["verdict"] != "retain_non_executable_research_bet":
            continue
        if canonical_binding_lifecycle(decision["canonical_binding"]) == (
            "historical_only"
        ):
            continue
        record = copy.deepcopy(
            queue_by_signature[decision["semantic_signature_sha256"]]
        )
        record["review_decision"] = copy.deepcopy(decision)
        record["review_decision"]["resolved_seed_id"] = record["seed_id"]
        record["review_record_sha256"] = sha256_json(decision)
        record["scientific_identity"] = "non_executable_research_bet"
        record["executable"] = False
        record["admissible"] = False
        record["recommended"] = False
        record["authorized"] = False
        record["route_promotion"] = False
        retained.append(record)
    if len(retained) > policy["portfolio"]["max_final_research_bets"]:
        raise ValueError("retained review decisions exceed max_final_research_bets")
    return retained


def validate_canonical_binding(binding: dict[str, Any]) -> None:
    kind = binding.get("kind")
    if kind == "none":
        if not isinstance(binding.get("reason"), str) or not binding["reason"].strip():
            raise ValueError("unbound review decision requires a reason")
        return
    if kind == "typed_evidence_desk_decision":
        required = {"kind", "cell_id", "decision_id", "route_id"}
        if set(binding) != required:
            raise ValueError("desk-decision binding fields do not match the contract")
        state = json.loads(
            (ROOT / "data" / "typed_evidence_state.json").read_text(
                encoding="utf-8"
            )
        )
        cell = next(
            (
                item
                for item in state.get("cells", [])
                if item.get("cell_id") == binding["cell_id"]
            ),
            None,
        )
        decision = next(
            (
                item
                for item in state.get("desk_decisions", [])
                if item.get("decision_id") == binding["decision_id"]
            ),
            None,
        )
        if cell is None or decision is None:
            raise ValueError("canonical desk-decision binding is unknown")
        for key in ("cell_id", "route_id"):
            if decision.get(key) != binding[key]:
                raise ValueError(f"canonical desk-decision binding mismatch: {key}")
        if cell.get("route_id") != binding["route_id"]:
            raise ValueError("canonical desk-decision binding mismatch: route_id")
        return
    if kind != "research_engine_proposal":
        raise ValueError(f"unknown canonical binding kind: {kind}")
    required = {"kind", "proposal_id", "proposal_sha256", "cell_id", "route_id"}
    if set(binding) != required:
        raise ValueError("proposal binding fields do not match the contract")
    state = json.loads(
        (ROOT / "data" / "research_engine_state.json").read_text(encoding="utf-8")
    )
    proposals = state.get("hypothesis_generation", {}).get("proposal_intake", [])
    match = next(
        (item for item in proposals if item.get("proposal_id") == binding["proposal_id"]),
        None,
    )
    if match is None:
        raise ValueError(f"canonical proposal is unknown: {binding['proposal_id']}")
    for key in ("proposal_sha256", "cell_id", "route_id"):
        if match.get(key) != binding[key]:
            raise ValueError(f"canonical proposal binding mismatch: {key}")


def canonical_binding_lifecycle(binding: dict[str, Any]) -> str:
    """Classify whether a valid review binding still names current science."""
    if binding.get("kind") != "research_engine_proposal":
        return "not_applicable"
    state = json.loads(
        (ROOT / "data" / "research_engine_state.json").read_text(
            encoding="utf-8"
        )
    )
    proposals = state.get("hypothesis_generation", {}).get(
        "proposal_intake", []
    )
    match = next(
        (
            item
            for item in proposals
            if item.get("proposal_id") == binding.get("proposal_id")
        ),
        None,
    )
    if match is None:
        return "missing"
    if (
        match.get("seed_resolution") == "frozen_historical_only"
        or "stale_seed_snapshot" in match.get("blockers", [])
    ):
        return "historical_only"
    return "current_non_executable"


def public_candidate(record: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "seed_id",
        "semantic_signature_sha256",
        "signature_instance_sha256",
        "base_id",
        "family",
        "type",
        "short_claim",
        "mechanism_obligation_id",
        "mechanism_obligation",
        "cost_bridge_id",
        "cost_bridge",
        "decisive_test_id",
        "decisive_test",
        "dimensions",
        "source_hard_gate",
        "source_portfolio",
        "source_canonical",
        "scope",
        "warnings",
    )
    return {key: copy.deepcopy(record[key]) for key in keys}


def challenge_indices(root: str, attempts: int, count: int = 16) -> list[int]:
    values: set[int] = set()
    nonce = 0
    while len(values) < min(count, attempts):
        digest = hashlib.sha256(f"{root}:{nonce}".encode("ascii")).digest()
        values.add(int.from_bytes(digest, "big") % attempts)
        nonce += 1
    return sorted(values)


def run_funnel(
    policy: dict[str, Any] | None = None,
    *,
    attempt_limit: int | None = None,
    compile_reviews: bool = True,
) -> dict[str, Any]:
    policy = copy.deepcopy(policy or load_policy())
    bases = load_base_questions(policy)
    mechanisms = load_operators(policy["mechanism_obligations"], "mechanisms")
    costs = load_operators(policy["cost_bridges"], "cost bridges")
    tests = load_operators(policy["decisive_tests"], "decisive tests")
    expected = len(bases) * len(mechanisms) * len(costs) * len(tests)
    if expected != policy["expansion"]["expected_signatures"]:
        raise ValueError(
            f"typed universe mismatch: expected policy "
            f"{policy['expansion']['expected_signatures']}, got {expected}"
        )
    limit = expected if attempt_limit is None else attempt_limit
    if limit < 0 or limit > expected:
        raise ValueError("attempt_limit outside the typed universe")

    input_path = ROOT / policy["input_pool"]["path"]
    input_sha = canonical_lf_sha256(input_path)
    evidence_hashes, evidence_snapshot_sha = evidence_snapshot(policy)
    frozen_policy_sha = generation_policy_digest(policy)
    dimensions = policy["portfolio"]["dimension_names"]
    merkle = StreamingMerkle()
    disposition_counts: Counter[str] = Counter()
    rejection_counts: Counter[str] = Counter()
    warning_counts: Counter[str] = Counter()
    type_counts: Counter[str] = Counter()
    samples: dict[str, list[dict[str, Any]]] = defaultdict(list)
    per_base_fronts: dict[str, list[dict[str, Any]]] = defaultdict(list)
    semantic_unique = 0

    with tempfile.TemporaryDirectory(prefix="hyp-funnel-") as temporary:
        db_path = Path(temporary) / "semantic-index.sqlite3"
        database = sqlite3.connect(db_path)
        database.execute("PRAGMA journal_mode=OFF")
        database.execute("PRAGMA synchronous=OFF")
        database.execute(
            "CREATE TABLE signatures "
            "(digest TEXT PRIMARY KEY, first_attempt INTEGER NOT NULL)"
        )

        attempt_index = 0
        product = itertools.product(bases, mechanisms, costs, tests)
        for base, mechanism, cost, test in itertools.islice(product, limit):
            semantic_payload = {
                "schema": "research-question-signature-v1",
                "anchor": semantic_anchor(base),
                "type": base["type"],
                "mechanism_obligation_id": mechanism.id,
                "cost_bridge_id": cost.id,
                "decisive_test_id": test.id,
                "threat_model": policy["safety"]["primary_threat_model"],
            }
            semantic_digest = sha256_json(semantic_payload)
            instance_payload = {
                "semantic_signature_sha256": semantic_digest,
                "baseline_commit": policy["baseline_commit"],
                "input_pool_sha256": input_sha,
                "evidence_snapshot_sha256": evidence_snapshot_sha,
                "generation_policy_sha256": frozen_policy_sha,
                "attempt_index": attempt_index,
            }
            instance_digest = sha256_json(instance_payload)
            seed_id = f"HQS1-{instance_digest[:32].upper()}"
            record = {
                "seed_id": seed_id,
                "semantic_signature_sha256": semantic_digest,
                "signature_instance_sha256": instance_digest,
                "attempt_index": attempt_index,
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
                "dimensions": metric_vector(
                    mechanism, cost, test, dimensions
                ),
                "source_hard_gate": base["hard_gate"],
                "source_portfolio": base["portfolio"],
                "source_canonical": base["canonical"],
                "scope": generated_scope(policy),
            }

            rejections = derive_rejections(
                base, mechanism, cost, test, policy, record["scope"]
            )
            cursor = database.execute(
                "INSERT OR IGNORE INTO signatures(digest, first_attempt) VALUES (?, ?)",
                (semantic_digest, attempt_index),
            )
            if cursor.rowcount == 0:
                rejections.append("duplicate_semantic_signature")
            else:
                semantic_unique += 1
            rejections = sorted(set(rejections))
            warnings = derive_warnings(base)
            record["warnings"] = warnings
            disposition = (
                "structurally_retained" if not rejections else "rejected"
            )
            primary_rejection = rejections[0] if rejections else None
            leaf = {
                "attempt_index": attempt_index,
                "semantic_signature_sha256": semantic_digest,
                "signature_instance_sha256": instance_digest,
                "disposition": disposition,
                "primary_rejection": primary_rejection,
                "all_rejections": rejections,
                "dimension_vector": [
                    record["dimensions"][name] for name in dimensions
                ],
                "diversity_tags": [
                    base["type"],
                    base["family"],
                    mechanism.id,
                    cost.id,
                    test.id,
                ],
            }
            merkle.add_payload(canonical_json_bytes(leaf))
            disposition_counts[disposition] += 1
            type_counts[base["type"]] += 1
            for reason in rejections:
                rejection_counts[reason] += 1
                retain_smallest_sample(samples, reason, record)
            for warning in warnings:
                warning_counts[warning] += 1

            if disposition == "structurally_retained":
                insert_pareto(
                    per_base_fronts[base["id"]],
                    record,
                    dimensions,
                    equal_limit=4,
                )
            attempt_index += 1

        database.commit()
        bounded_sqlite_rows = database.execute(
            "SELECT COUNT(*) FROM signatures"
        ).fetchone()[0]
        database.close()

    if attempt_index != limit or merkle.count != limit:
        raise AssertionError("attempt coverage mismatch")
    candidates = [
        candidate
        for base_id in sorted(per_base_fronts)
        for candidate in per_base_fronts[base_id]
    ]
    queue = choose_review_queue(candidates, policy)
    public_queue = [public_candidate(item) for item in queue]
    reviews_compiled = compile_reviews and attempt_limit is None
    final_bets = compile_review_decisions(queue, policy) if reviews_compiled else []
    review_records = policy["review_decisions"] if reviews_compiled else []
    review_binding_statuses = (
        [
            {
                "review_id": record["review_id"],
                "canonical_binding_kind": record["canonical_binding"]["kind"],
                "lifecycle": canonical_binding_lifecycle(
                    record["canonical_binding"]
                ),
            }
            for record in review_records
        ]
        if reviews_compiled
        else []
    )
    independent_review_records = sum(
        all(record["independence"].values()) for record in review_records
    )
    root = merkle.root()

    state = {
        "schema_version": "1.0-generated",
        "funnel_id": policy["funnel_id"],
        "status": "shadow_non_executing",
        "scientific_identity": "research_question_signature_funnel",
        "baseline_commit": policy["baseline_commit"],
        "source_bindings": {
            "input_pool_path": policy["input_pool"]["path"],
            "input_pool_sha256": input_sha,
            "evidence_snapshot_sha256": evidence_snapshot_sha,
            "evidence_input_sha256": evidence_hashes,
            "generation_policy_path": str(
                POLICY_PATH.relative_to(ROOT)
            ).replace("\\", "/"),
            "generation_policy_sha256": frozen_policy_sha,
            "constitution_sha256": policy["constitution"]["canonical_lf_sha256"],
        },
        "bulk_contract": {
            "attempt_count": limit,
            "full_universe_count": expected,
            "raw_signatures_materialized": False,
            "language_model_calls": 0,
            "authorization": "none",
            "route_promotion": False,
            "exact_target_execution": False,
            "stream_digest_version": policy["expansion"][
                "stream_digest_version"
            ],
            "merkle_root_sha256": root,
            "challenge_indices": challenge_indices(root, limit),
        },
        "counts": {
            "attempts": attempt_index,
            "semantic_normal_forms": semantic_unique,
            "semantic_index_rows": bounded_sqlite_rows,
            "structurally_retained": disposition_counts[
                "structurally_retained"
            ],
            "rejected": disposition_counts["rejected"],
            "pareto_records_before_review_queue": len(candidates),
            "review_queue": len(public_queue),
            "review_records": len(review_records),
            "historical_only_review_bindings": sum(
                item["lifecycle"] == "historical_only"
                for item in review_binding_statuses
            ),
            "independent_review_records": independent_review_records,
            "unreviewed_queue_items": len(public_queue) - len(review_records),
            "final_research_bets": len(final_bets),
            "admissible": 0,
            "recommended": 0,
            "authorized": 0,
            "route_promotions": 0,
            "experiment_events": 0,
        },
        "counts_by_type": dict(sorted(type_counts.items())),
        "rejection_histogram": dict(sorted(rejection_counts.items())),
        "warning_histogram": dict(sorted(warning_counts.items())),
        "rejection_samples": {
            key: values for key, values in sorted(samples.items())
        },
        "review_queue": public_queue,
        "review_binding_statuses": review_binding_statuses,
        "final_research_bets": final_bets,
        "memory_contract": {
            "raw_record_retention": 0,
            "merkle_frontier_max_nodes": len(merkle.frontier),
            "sqlite_semantic_index_on_disk": True,
            "per_rejection_samples": 3,
            "review_queue_limit": policy["portfolio"]["max_review_queue"],
            "final_bet_limit": policy["portfolio"][
                "max_final_research_bets"
            ],
        },
        "boundaries": [
            "A structurally retained signature is still only a research-question seed.",
            "The historical source labels are advisory and are not scientific gates.",
            "No lexical or typed digest proves semantic novelty.",
            "A portfolio review record is not independent unless source, model-family, and context independence are all recorded true.",
            "A historical-only canonical proposal binding remains audit evidence but cannot enter current final_research_bets.",
            "Every retained item still lacks an assured exact mechanism and independent source review.",
            "No output is executable, admissible, recommended, authorized, or route-promoting."
        ],
    }
    return state


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if the committed aggregate differs from a fresh replay",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="print only the compact count/root summary",
    )
    args = parser.parse_args()

    state = run_funnel()
    payload = json.dumps(
        state,
        ensure_ascii=True,
        indent=2,
        sort_keys=False,
        allow_nan=False,
    ) + "\n"
    if args.check:
        if not STATE_PATH.exists():
            print(f"hypothesis funnel check failed: missing {STATE_PATH}")
            return 1
        if STATE_PATH.read_text(encoding="utf-8") != payload:
            print("hypothesis funnel check failed: generated state is stale")
            return 1
    else:
        STATE_PATH.write_text(payload, encoding="utf-8", newline="\n")

    if args.summary or args.check:
        counts = state["counts"]
        print(
            "HYP_FUNNEL_OK "
            f"attempts={counts['attempts']} "
            f"retained={counts['structurally_retained']} "
            f"review_queue={counts['review_queue']} "
            f"final_bets={counts['final_research_bets']} "
            f"root={state['bulk_contract']['merkle_root_sha256']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
