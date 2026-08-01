#!/usr/bin/env python3
"""Build the non-authorizing shadow state for the hypothesis ranker."""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import math
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hypothesis_funnel import (
    POLICY_PATH,
    ROOT,
    STATE_PATH as FUNNEL_STATE_PATH,
    canonical_lf_sha256,
    load_policy,
    sha256_json,
)
from hypothesis_generation_lib import proposal_sha256, validate_reviews


SPEC_PATH = ROOT / "repo" / "HYPOTHESIS_RANKER_V0.json"
STATE_PATH = ROOT / "data" / "hypothesis_ranker_state.json"
ENGINE_STATE_PATH = ROOT / "data" / "research_engine_state.json"
REVIEW_LEDGER_PATH = ROOT / "data" / "hypothesis_review_ledger.jsonl"
REVIEW_REGISTRY_PATH = ROOT / "repo" / "HYPOTHESIS_REVIEW_REGISTRY_V1.json"
GENERATION_POLICY_PATH = ROOT / "repo" / "HYPOTHESIS_GENERATION_V0.json"
PROPOSAL_DIR = ROOT / "experiments" / "engine" / "proposals"
PROPOSAL_REVIEW_DIR = ROOT / "experiments" / "engine" / "proposal_reviews"
REVIEW_SCHEMA_PATH = ROOT / "experiments" / "engine" / "hypothesis_review.schema.json"
PROTECTED_REVIEW_LEDGER_REF = "refs/remotes/origin/main"
REVIEW_REGISTRY_BOOTSTRAP_COMMIT = "8c10a868fed71ef9a28820aed78d85098b678f96"
REVIEW_CONTRACT_PATHS = (
    GENERATION_POLICY_PATH,
    REVIEW_SCHEMA_PATH,
    ROOT / "scripts" / "hypothesis_generation_lib.py",
    ROOT / "scripts" / "hypothesis_ranker.py",
)
EVIDENCE_CLOSURE_FILES = (
    ROOT / "repo" / "RESEARCH_ENGINE_V0.json",
    ROOT / "repo" / "ECDLP_DECISION_SUBSTRATE.json",
    REVIEW_REGISTRY_PATH,
    ROOT / "data" / "research_claim_state.json",
    ROOT / "data" / "typed_evidence_state.json",
)
EVIDENCE_CLOSURE_DIRECTORIES = (
    ROOT / "experiments" / "engine" / "proposals",
    ROOT / "experiments" / "engine" / "proposal_reviews",
    ROOT / "experiments" / "engine" / "desk_decisions",
    ROOT / "experiments" / "engine" / "outcomes",
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def reviewed_evidence_closure_sha256() -> str:
    paths = list(EVIDENCE_CLOSURE_FILES)
    for directory in EVIDENCE_CLOSURE_DIRECTORIES:
        paths.extend(sorted(directory.glob("*.json")))
    anchors = [
        {
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "sha256": canonical_lf_sha256(path),
        }
        for path in sorted(set(paths))
        if path.is_file()
    ]
    if not anchors:
        raise ValueError("reviewed evidence closure is empty")
    return sha256_json(anchors)


def candidate_evidence_manifest(review: dict[str, Any]) -> list[dict[str, str]]:
    """Resolve the exact candidate-specific evidence named by a review."""

    binding = review.get("canonical_binding", {})
    kind = binding.get("kind")
    if kind == "none":
        return []
    if kind == "research_engine_proposal":
        identifier = binding.get("proposal_id")
        id_field = "proposal_id"
        directory = ROOT / "experiments" / "engine" / "proposals"
    elif kind == "typed_evidence_desk_decision":
        identifier = binding.get("decision_id")
        id_field = "decision_id"
        directory = ROOT / "experiments" / "engine" / "desk_decisions"
    else:
        raise ValueError(f"unsupported review canonical binding kind: {kind}")
    if not isinstance(identifier, str) or not identifier:
        raise ValueError("review canonical binding is missing its identifier")
    path = directory / f"{identifier}.json"
    if not path.is_file() or load_json(path).get(id_field) != identifier:
        raise ValueError(f"review evidence artifact does not resolve: {identifier}")
    paths = [path, *REVIEW_CONTRACT_PATHS]
    if kind == "research_engine_proposal":
        for review_path in sorted(PROPOSAL_REVIEW_DIR.glob("*.json")):
            review_document = load_json(review_path)
            if review_document.get("proposal_id") == identifier:
                paths.append(review_path)
                for relative in review_document.get("evidence_inputs", []):
                    if not isinstance(relative, str) or not relative:
                        raise ValueError("review evidence input path is invalid")
                    candidate = (ROOT / relative).resolve()
                    try:
                        candidate.relative_to(ROOT.resolve())
                    except ValueError:
                        raise ValueError(
                            "review evidence input escapes the repository"
                        ) from None
                    if not candidate.is_file():
                        raise ValueError(
                            f"review evidence input does not resolve: {relative}"
                        )
                    paths.append(candidate)
    return [
        {
            "path": str(item.relative_to(ROOT)).replace("\\", "/"),
            "sha256": canonical_lf_sha256(item),
        }
        for item in sorted(set(paths))
    ]


def load_review_registry(path: Path = REVIEW_REGISTRY_PATH) -> dict[str, dict[str, Any]]:
    document = load_json(path)
    required = {
        "schema_version",
        "registry_id",
        "status",
        "protected_base_ref",
        "bootstrap_base_commit",
        "append_only_contract",
        "registrations",
    }
    if set(document) != required or document.get("schema_version") != "1.0":
        raise ValueError("scientific review registry has invalid shape")
    if document.get("registry_id") != "HYPOTHESIS-SCIENTIFIC-REVIEW-REGISTRY-V1":
        raise ValueError("scientific review registry identity drifted")
    if document.get("protected_base_ref") != PROTECTED_REVIEW_LEDGER_REF:
        raise ValueError("scientific review registry protected ref drifted")
    if document.get("bootstrap_base_commit") != REVIEW_REGISTRY_BOOTSTRAP_COMMIT:
        raise ValueError("scientific review registry bootstrap commit drifted")
    registrations = document.get("registrations")
    if not isinstance(registrations, list):
        raise ValueError("scientific review registrations must be an array")
    expected_status = "active_empty" if not registrations else "active"
    if document.get("status") != expected_status:
        raise ValueError("scientific review registry status is inconsistent")
    if not isinstance(document.get("append_only_contract"), str) or not document[
        "append_only_contract"
    ].strip():
        raise ValueError("scientific review registry contract is empty")
    expected_fields = {
        "registration_id",
        "label_id",
        "ledger_entry_sha256",
        "candidate_version_sha256",
        "registered_on",
        "owner_decision_id",
    }
    index: dict[str, dict[str, Any]] = {}
    registration_ids: set[str] = set()
    for item in registrations:
        if not isinstance(item, dict) or set(item) != expected_fields:
            raise ValueError("scientific review registration has invalid shape")
        if not all(
            isinstance(item.get(field), str) and item[field]
            for field in ("registration_id", "label_id", "owner_decision_id")
        ):
            raise ValueError("scientific review registration identity is invalid")
        for field in ("ledger_entry_sha256", "candidate_version_sha256"):
            if not isinstance(item.get(field), str) or not re_full_hash(item[field]):
                raise ValueError(f"scientific review registration {field} is invalid")
        try:
            registered_on = datetime.date.fromisoformat(item["registered_on"])
        except (TypeError, ValueError):
            raise ValueError("scientific review registration date is invalid") from None
        if registered_on.isoformat() != item["registered_on"]:
            raise ValueError("scientific review registration date is not canonical")
        if item["registration_id"] in registration_ids or item["label_id"] in index:
            raise ValueError("scientific review registry contains duplicates")
        registration_ids.add(item["registration_id"])
        index[item["label_id"]] = item

    if path.resolve() == REVIEW_REGISTRY_PATH.resolve():
        protected_ref = subprocess.run(
            ["git", "rev-parse", "--verify", f"{PROTECTED_REVIEW_LEDGER_REF}^{{commit}}"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if protected_ref.returncode:
            raise ValueError("scientific review registry protected ref cannot resolve")
        protected = subprocess.run(
            [
                "git",
                "show",
                f"{PROTECTED_REVIEW_LEDGER_REF}:repo/HYPOTHESIS_REVIEW_REGISTRY_V1.json",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if protected.returncode == 0:
            prior = json.loads(protected.stdout)
            prior_registrations = prior.get("registrations", [])
            if registrations[: len(prior_registrations)] != prior_registrations:
                raise ValueError(
                    "scientific review registry is not an append-only extension of protected main"
                )
        else:
            if registrations:
                raise ValueError(
                    "scientific review registry bootstrap must use the empty genesis"
                )
            bootstrap_ancestor = subprocess.run(
                [
                    "git",
                    "merge-base",
                    "--is-ancestor",
                    REVIEW_REGISTRY_BOOTSTRAP_COMMIT,
                    PROTECTED_REVIEW_LEDGER_REF,
                ],
                cwd=ROOT,
                capture_output=True,
            )
            bootstrap_path = subprocess.run(
                [
                    "git",
                    "cat-file",
                    "-e",
                    f"{REVIEW_REGISTRY_BOOTSTRAP_COMMIT}:repo/HYPOTHESIS_REVIEW_REGISTRY_V1.json",
                ],
                cwd=ROOT,
                capture_output=True,
            )
            protected_path = subprocess.run(
                [
                    "git",
                    "cat-file",
                    "-e",
                    f"{PROTECTED_REVIEW_LEDGER_REF}:repo/HYPOTHESIS_REVIEW_REGISTRY_V1.json",
                ],
                cwd=ROOT,
                capture_output=True,
            )
            if (
                bootstrap_ancestor.returncode != 0
                or bootstrap_path.returncode == 0
                or protected_path.returncode == 0
            ):
                raise ValueError(
                    "scientific review registry bootstrap absence cannot be proved"
                )
    return index


def re_full_hash(value: str) -> bool:
    return len(value) == 64 and all(
        character in "0123456789abcdef" for character in value
    )


def proposal_review_bundle(review: dict[str, Any]) -> tuple[list[str], str]:
    """Validate the manifest-bound five-role bundle and derive its binary direction."""

    binding = review.get("canonical_binding", {})
    if binding.get("kind") != "research_engine_proposal":
        return ["review is not bound to a research-engine proposal"], "nonbinary"
    proposal_id = binding.get("proposal_id")
    proposal_path = PROPOSAL_DIR / f"{proposal_id}.json"
    if not proposal_path.is_file():
        return ["review proposal does not resolve"], "nonbinary"
    proposal = load_json(proposal_path)
    if (
        proposal.get("proposal_id") != proposal_id
        or proposal_sha256(proposal) != binding.get("proposal_sha256")
    ):
        return ["review proposal digest is stale"], "nonbinary"
    review_records: list[tuple[Path, dict[str, Any]]] = []
    for path in sorted(PROPOSAL_REVIEW_DIR.glob("*.json")):
        document = load_json(path)
        if document.get("proposal_id") == proposal_id:
            review_records.append((path, document))
    generation_policy = load_json(GENERATION_POLICY_PATH)
    problems, grouped = validate_reviews(
        review_records, [(proposal_path, proposal)], generation_policy
    )
    bundle = grouped.get(proposal_id, [])
    required_roles = set(generation_policy["quality_gate"]["required_review_roles"])
    independent_roles = set(
        generation_policy["quality_gate"]["required_independent_roles"]
    )
    roles = [item.get("reviewer_role") for item in bundle]
    if len(bundle) != len(required_roles) or set(roles) != required_roles:
        problems.append("five-role proposal review bundle is incomplete")
    proposer = proposal.get("provenance", {})
    proposer_family = proposer.get("generator_family")
    proposer_session = proposer.get("session_id")
    proposer_context = proposer.get("context_sha256")
    reviewers = [item.get("reviewer_id") for item in bundle]
    contexts = [item.get("reviewer_provenance", {}).get("context_sha256") for item in bundle]
    families = {item.get("reviewer_provenance", {}).get("family") for item in bundle}
    if len(reviewers) != len(set(reviewers)):
        problems.append("proposal review identities are not distinct")
    if len(contexts) != len(set(contexts)):
        problems.append("proposal review contexts are not distinct")
    if len(families) < 2:
        problems.append("proposal review bundle needs at least two model families")
    for item in bundle:
        provenance = item.get("reviewer_provenance", {})
        if provenance.get("blind_to_other_reviews") is not True:
            problems.append("proposal review is not blind to peer reviews")
        if item.get("reviewer_role") in independent_roles and (
            item.get("source_independence") != "declared_independent"
            or provenance.get("family") == proposer_family
            or provenance.get("session_id") == proposer_session
            or provenance.get("context_sha256") == proposer_context
        ):
            problems.append("required proposal review independence is not established")
    if problems:
        return sorted(set(problems)), "nonbinary"
    if any(item.get("verdict") == "block" for item in bundle):
        return [], "negative"
    if bundle and all(item.get("verdict") == "pass" for item in bundle):
        return [], "positive"
    return [], "nonbinary"


def evidence_manifest_problems(manifest: Any) -> list[str]:
    if not isinstance(manifest, list):
        return ["reviewed evidence manifest is not an array"]
    problems: list[str] = []
    paths: set[str] = set()
    for index, anchor in enumerate(manifest):
        if not isinstance(anchor, dict) or set(anchor) != {"path", "sha256"}:
            problems.append(f"reviewed evidence anchor {index} has invalid shape")
            continue
        relative = anchor.get("path")
        digest = anchor.get("sha256")
        if (
            not isinstance(relative, str)
            or not relative
            or relative in paths
            or Path(relative).is_absolute()
            or ".." in Path(relative).parts
        ):
            problems.append(f"reviewed evidence anchor {index} path is invalid")
            continue
        paths.add(relative)
        if (
            not isinstance(digest, str)
            or len(digest) != 64
            or any(character not in "0123456789abcdef" for character in digest)
        ):
            problems.append(f"reviewed evidence anchor {index} digest is invalid")
    return problems


def review_ledger_entry_digest(entry: dict[str, Any]) -> str:
    payload = {
        key: value
        for key, value in entry.items()
        if key not in {"label_id", "ledger_entry_sha256"}
    }
    return sha256_json(payload)


def feature_vector(candidate: dict[str, Any], spec: dict[str, Any]) -> dict[str, float]:
    names = spec["feature_contract"]["numeric"]
    dimensions = candidate["dimensions"]
    if set(names) - set(dimensions):
        raise ValueError("candidate is missing a ranker feature")
    return {name: float(dimensions[name]) for name in names}


def load_review_ledger(path: Path = REVIEW_LEDGER_PATH) -> list[dict[str, Any]]:
    raw = path.read_bytes()
    if path.resolve() == REVIEW_LEDGER_PATH.resolve():
        spec = load_json(SPEC_PATH)
        contract = spec["label_contract"]
        if contract.get("protected_prefix_ref") != PROTECTED_REVIEW_LEDGER_REF:
            raise ValueError("ranker protected ledger ref drifted")
        if contract.get("current_entry_schema") != "2.0":
            raise ValueError("ranker current review-entry schema drifted")
        baseline = contract["legacy_prefix"]
        lines = raw.splitlines(keepends=True)
        line_count = baseline["line_count"]
        if len(lines) < line_count or hashlib.sha256(
            b"".join(lines[:line_count])
        ).hexdigest() != baseline["raw_sha256"]:
            raise ValueError("review ledger legacy byte prefix changed")
        protected = subprocess.run(
            [
                "git",
                "show",
                f"{PROTECTED_REVIEW_LEDGER_REF}:data/hypothesis_review_ledger.jsonl",
            ],
            cwd=ROOT,
            capture_output=True,
        )
        if protected.returncode:
            raise ValueError("protected review-ledger prefix cannot be resolved")
        if not raw.startswith(protected.stdout):
            raise ValueError("review ledger is not an append-only extension of protected main")
    records = [
        json.loads(line)
        for line in raw.decode("utf-8").splitlines()
        if line.strip()
    ]
    if len({item.get("label_id") for item in records}) != len(records):
        raise ValueError("review ledger contains duplicate label ids")
    if len(
        {item.get("review_record", {}).get("review_id") for item in records}
    ) != len(records):
        raise ValueError("review ledger contains duplicate review ids")
    for item in records:
        review = item.get("review_record")
        snapshot = item.get("candidate_snapshot")
        if not isinstance(review, dict) or not isinstance(snapshot, dict):
            raise ValueError("review ledger record is incomplete")
        review_digest = sha256_json(review)
        if item.get("review_record_sha256") != review_digest:
            raise ValueError("review ledger record digest mismatch")
        schema_version = item.get("schema_version")
        if schema_version == "1.0":
            if "reviewed_evidence_closure_sha256" in item:
                raise ValueError("legacy review row cannot claim an evidence closure")
            if item.get("label_id") != f"HRL-{review_digest[:24].upper()}":
                raise ValueError("legacy review ledger label identity mismatch")
        elif schema_version == "2.0":
            required = {
                "schema_version",
                "funnel_id",
                "batch_merkle_root_sha256",
                "global_evidence_closure_sha256",
                "reviewed_evidence_manifest",
                "reviewed_evidence_closure_sha256",
                "semantic_signature_sha256",
                "candidate_snapshot",
                "review_record",
                "review_record_sha256",
                "label_id",
                "ledger_entry_sha256",
            }
            if set(item) != required:
                raise ValueError("current review ledger row has unexpected shape")
            for field in (
                "batch_merkle_root_sha256",
                "global_evidence_closure_sha256",
                "reviewed_evidence_closure_sha256",
                "review_record_sha256",
                "semantic_signature_sha256",
                "ledger_entry_sha256",
            ):
                digest_value = item.get(field)
                if (
                    not isinstance(digest_value, str)
                    or len(digest_value) != 64
                    or any(character not in "0123456789abcdef" for character in digest_value)
                ):
                    raise ValueError(f"review ledger {field} is invalid")
            manifest = item["reviewed_evidence_manifest"]
            if evidence_manifest_problems(manifest):
                raise ValueError("current review ledger evidence manifest is stale")
            if item.get("reviewed_evidence_closure_sha256") != sha256_json(manifest):
                raise ValueError("review ledger candidate evidence closure mismatch")
            entry_digest = review_ledger_entry_digest(item)
            if item.get("ledger_entry_sha256") != entry_digest:
                raise ValueError("review ledger entry digest mismatch")
            if item.get("label_id") != f"HRL-{entry_digest[:24].upper()}":
                raise ValueError("review ledger entry identity mismatch")
        else:
            raise ValueError("review ledger schema version is unsupported")
        signature = item.get("semantic_signature_sha256")
        if (
            review.get("semantic_signature_sha256") != signature
            or snapshot.get("semantic_signature_sha256") != signature
        ):
            raise ValueError("review ledger semantic identity mismatch")
    return records


def validate_current_review_bindings(
    ledger: list[dict[str, Any]],
    policy: dict[str, Any],
    funnel_state: dict[str, Any],
) -> list[dict[str, Any]]:
    current_reviews = {
        item["review_id"]: item for item in policy["review_decisions"]
    }
    ledger_by_review = {
        item["review_record"]["review_id"]: item
        for item in ledger
    }
    if not set(current_reviews).issubset(ledger_by_review):
        raise ValueError("current funnel reviews and persistent ledger have drifted")
    queue = {
        item["semantic_signature_sha256"]: item
        for item in funnel_state["review_queue"]
    }
    bindings: list[dict[str, Any]] = []
    current_root = funnel_state["bulk_contract"]["merkle_root_sha256"]
    current_global_closure = reviewed_evidence_closure_sha256()
    for review_id, review in current_reviews.items():
        entry = ledger_by_review[review_id]
        if entry["funnel_id"] != policy["funnel_id"]:
            raise ValueError("persistent review belongs to a different funnel")
        if entry["review_record"] != review:
            raise ValueError("persistent review record differs from current policy")
        candidate = queue.get(review["semantic_signature_sha256"])
        if candidate is None:
            raise ValueError("current review is outside the current queue")
        current_manifest = candidate_evidence_manifest(review)
        current_closure = sha256_json(current_manifest)
        snapshot = entry["candidate_snapshot"]
        for key in (
            "semantic_signature_sha256",
            "base_id",
            "family",
            "type",
            "mechanism_obligation_id",
            "cost_bridge_id",
            "decisive_test_id",
            "dimensions",
        ):
            if snapshot.get(key) != candidate.get(key):
                raise ValueError(f"persistent review candidate snapshot mismatch: {key}")
        bindings.append(
            {
                "review_id": review_id,
                "label_id": entry["label_id"],
                "source_batch_merkle_root_sha256": entry[
                    "batch_merkle_root_sha256"
                ],
                "current_batch_merkle_root_sha256": current_root,
                "reused_across_evidence_snapshot": entry[
                    "batch_merkle_root_sha256"
                ]
                != current_root,
                "reviewed_evidence_closure_sha256": entry.get(
                    "reviewed_evidence_closure_sha256"
                ),
                "reviewed_evidence_manifest": entry.get(
                    "reviewed_evidence_manifest", []
                ),
                "current_evidence_closure_sha256": current_closure,
                "evidence_closure_current": entry.get(
                    "reviewed_evidence_closure_sha256"
                )
                == current_closure,
                "global_evidence_snapshot_current": entry.get(
                    "global_evidence_closure_sha256"
                )
                == current_global_closure,
            }
        )
    return bindings


def review_labels(
    ledger: list[dict[str, Any]],
    spec: dict[str, Any],
    *,
    review_registry: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    if review_registry is None:
        review_registry = load_review_registry()
    positives = set(spec["label_contract"]["positive"])
    negatives = set(spec["label_contract"]["negative"])
    required_axes = set(spec["label_contract"]["required_independence_axes"])
    labels: list[dict[str, Any]] = []
    for entry in ledger:
        review = entry["review_record"]
        signature = entry["semantic_signature_sha256"]
        verdict = review["verdict"]
        exclusion_reasons: list[str] = []
        if entry.get("schema_version") != "2.0":
            exclusion_reasons.append("legacy_review_schema")
        if verdict in positives:
            value: int | None = 1
        elif verdict in negatives:
            value = 0
        else:
            value = None
            exclusion_reasons.append("non_binary_review_disposition")

        independence = review["independence"]
        if set(independence) != required_axes or not all(independence.values()):
            exclusion_reasons.append("independence_not_established")
        else:
            bundle_problems, bundle_direction = proposal_review_bundle(review)
            if bundle_problems:
                exclusion_reasons.append("independence_provenance_unverified")
            elif (value == 1 and bundle_direction != "positive") or (
                value == 0 and bundle_direction != "negative"
            ):
                exclusion_reasons.append("review_bundle_verdict_mismatch")
        if "migration" in review["reviewer"]["role"]:
            exclusion_reasons.append("historical_migration")

        candidate = entry["candidate_snapshot"]
        reviewed_closure = entry.get("reviewed_evidence_closure_sha256")
        if reviewed_closure is None:
            exclusion_reasons.append("reviewed_evidence_closure_unbound")
        else:
            try:
                expected_manifest = candidate_evidence_manifest(review)
            except ValueError:
                expected_manifest = []
                exclusion_reasons.append("reviewed_evidence_cannot_resolve")
            if not expected_manifest:
                exclusion_reasons.append("candidate_evidence_manifest_empty")
            if (
                entry.get("reviewed_evidence_manifest") != expected_manifest
                or reviewed_closure != sha256_json(expected_manifest)
            ):
                exclusion_reasons.append("reviewed_evidence_closure_stale")
        candidate_version = sha256_json(
            {
                "candidate_snapshot": candidate,
                "reviewed_evidence_closure_sha256": reviewed_closure,
            }
        )
        registered = review_registry.get(entry["label_id"])
        if registered is None:
            exclusion_reasons.append("unregistered_review_artifact")
        elif (
            entry.get("ledger_entry_sha256")
            != registered["ledger_entry_sha256"]
            or candidate_version != registered["candidate_version_sha256"]
        ):
            exclusion_reasons.append("scientific_review_registration_mismatch")
        record_sha = entry["review_record_sha256"]
        labels.append(
            {
                "label_id": entry["label_id"],
                "review_id": review["review_id"],
                "review_record_sha256": record_sha,
                "semantic_signature_sha256": signature,
                "candidate_version_sha256": candidate_version,
                "reviewed_evidence_closure_sha256": reviewed_closure,
                "funnel_id": entry["funnel_id"],
                "batch_merkle_root_sha256": entry["batch_merkle_root_sha256"],
                "family": candidate["family"],
                "reviewer_actor_id": review["reviewer"]["actor_id"],
                "verdict": verdict,
                "binary_label": value,
                "training_eligible": value is not None and not exclusion_reasons,
                "exclusion_reasons": sorted(set(exclusion_reasons)),
                "features": feature_vector(candidate, spec),
            }
        )
    return sorted(labels, key=lambda item: item["label_id"])


def aggregate_training_examples(labels: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for label in labels:
        grouped.setdefault(label["candidate_version_sha256"], []).append(label)
    examples: list[dict[str, Any]] = []
    for candidate_version, reviews in sorted(grouped.items()):
        eligible = [item for item in reviews if item["training_eligible"]]
        values = {item["binary_label"] for item in eligible}
        disagreement = len(values) > 1
        representative = reviews[0]
        examples.append(
            {
                "candidate_version_sha256": candidate_version,
                "semantic_signature_sha256": representative[
                    "semantic_signature_sha256"
                ],
                "family": representative["family"],
                "features": representative["features"],
                "review_ids": sorted(item["review_id"] for item in reviews),
                "label_ids": sorted(item["label_id"] for item in reviews),
                "review_count": len(reviews),
                "eligible_review_count": len(eligible),
                "reviewer_actor_ids": sorted(
                    {item["reviewer_actor_id"] for item in eligible}
                ),
                "binary_label": None
                if not eligible or disagreement
                else eligible[0]["binary_label"],
                "training_eligible": bool(eligible) and not disagreement,
                "consensus": "disagreement"
                if disagreement
                else "unlabelled"
                if not eligible
                else "consensus",
            }
        )
    return examples


def activation_report(
    examples: list[dict[str, Any]],
    native_outcomes: int,
    spec: dict[str, Any],
) -> dict[str, Any]:
    gate = spec["activation_gate"]
    eligible = [item for item in examples if item["training_eligible"]]
    positives = sum(item["binary_label"] == 1 for item in eligible)
    negatives = sum(item["binary_label"] == 0 for item in eligible)
    families = len({item["family"] for item in eligible})
    reviewers = len(
        {
            reviewer
            for item in eligible
            for reviewer in item["reviewer_actor_ids"]
        }
    )
    observed = {
        "eligible_candidate_versions": len(eligible),
        "positive_labels": positives,
        "negative_labels": negatives,
        "distinct_families": families,
        "distinct_reviewers": reviewers,
        "native_outcomes": native_outcomes,
    }
    required = {
        "eligible_candidate_versions": gate[
            "minimum_eligible_candidate_versions"
        ],
        "positive_labels": gate["minimum_positive_labels"],
        "negative_labels": gate["minimum_negative_labels"],
        "distinct_families": gate["minimum_distinct_families"],
        "distinct_reviewers": gate["minimum_distinct_reviewers"],
        "native_outcomes": gate["minimum_native_outcomes"],
    }
    unmet = [key for key, minimum in required.items() if observed[key] < minimum]
    return {
        "ready_for_training": not unmet,
        "observed": observed,
        "required": required,
        "unmet": unmet,
        "required_validation": gate["required_validation"],
    }


def validate_model(model: dict[str, Any], spec: dict[str, Any], path: Path) -> None:
    names = spec["feature_contract"]["numeric"]
    if model.get("feature_names") != names:
        raise ValueError("ranker model feature order does not match the specification")
    if path.stat().st_size > spec["model_artifact"]["maximum_git_bytes"]:
        raise ValueError("ranker model exceeds the Git artifact size limit")
    if model.get("selection_influence") is not False:
        raise ValueError("shadow ranker cannot influence selection")
    if model.get("authorization_capability") is not False:
        raise ValueError("ranker cannot authorize research")
    if model.get("trained") is False:
        if any(model.get(key) is not None for key in ("weights", "bias", "normalization")):
            raise ValueError("untrained ranker must not contain active parameters")
        return
    if model.get("trained") is not True:
        raise ValueError("ranker trained flag must be boolean")
    weights = model.get("weights")
    if not isinstance(weights, dict) or set(weights) != set(names):
        raise ValueError("trained ranker has invalid weights")
    if not all(isinstance(weights[name], (int, float)) for name in names):
        raise ValueError("trained ranker weights must be numeric")
    if not isinstance(model.get("bias"), (int, float)):
        raise ValueError("trained ranker bias must be numeric")


def learned_score(
    features: dict[str, float], model: dict[str, Any]
) -> float | None:
    if not model["trained"]:
        return None
    normalization = model["normalization"]
    if not isinstance(normalization, dict):
        raise ValueError("trained ranker requires normalization metadata")
    z = float(model["bias"])
    for name in model["feature_names"]:
        stats = normalization[name]
        scale = float(stats["scale"])
        if scale <= 0:
            raise ValueError("ranker feature scale must be positive")
        normalized = (features[name] - float(stats["mean"])) / scale
        z += float(model["weights"][name]) * normalized
    return 1.0 / (1.0 + math.exp(-max(-60.0, min(60.0, z))))


def build_state() -> dict[str, Any]:
    policy = load_policy()
    funnel_state = load_json(FUNNEL_STATE_PATH)
    spec = load_json(SPEC_PATH)
    model_path = ROOT / spec["model_artifact"]["path"]
    model = load_json(model_path)
    validate_model(model, spec, model_path)
    ledger = load_review_ledger()
    current_review_bindings = validate_current_review_bindings(
        ledger, policy, funnel_state
    )
    labels = review_labels(
        ledger,
        spec,
        review_registry=load_review_registry(),
    )
    training_examples = aggregate_training_examples(labels)
    engine_state = load_json(ENGINE_STATE_PATH)
    native_outcomes = len(engine_state.get("native_outcomes", []))
    activation = activation_report(training_examples, native_outcomes, spec)

    if model["trained"] and activation["ready_for_training"]:
        status = "shadow_scoring"
    elif activation["ready_for_training"]:
        status = "ready_for_training"
    else:
        status = "inactive_insufficient_independent_labels"

    ranked: list[dict[str, Any]] = []
    for candidate in funnel_state["review_queue"]:
        features = feature_vector(candidate, spec)
        ranked.append(
            {
                "semantic_signature_sha256": candidate[
                    "semantic_signature_sha256"
                ],
                "seed_id": candidate["seed_id"],
                "base_id": candidate["base_id"],
                "family": candidate["family"],
                "type": candidate["type"],
                "features": features,
                "learned_score": learned_score(features, model),
            }
        )
    if model["trained"]:
        ranked.sort(
            key=lambda item: (
                -float(item["learned_score"]),
                item["semantic_signature_sha256"],
            )
        )

    exclusion_histogram = Counter(
        reason for label in labels for reason in label["exclusion_reasons"]
    )
    return {
        "schema_version": "0.1-generated",
        "ranker_id": spec["ranker_id"],
        "status": status,
        "selection_influence": False,
        "authorization_capability": False,
        "route_promotion_capability": False,
        "source_bindings": {
            "ranker_spec_path": str(SPEC_PATH.relative_to(ROOT)).replace("\\", "/"),
            "ranker_spec_sha256": canonical_lf_sha256(SPEC_PATH),
            "model_path": str(model_path.relative_to(ROOT)).replace("\\", "/"),
            "model_sha256": canonical_lf_sha256(model_path),
            "funnel_state_path": str(FUNNEL_STATE_PATH.relative_to(ROOT)).replace(
                "\\", "/"
            ),
            "funnel_state_sha256": canonical_lf_sha256(FUNNEL_STATE_PATH),
            "current_review_policy_path": str(POLICY_PATH.relative_to(ROOT)).replace(
                "\\", "/"
            ),
            "current_review_records_sha256": sha256_json(
                policy["review_decisions"]
            ),
            "persistent_review_ledger_path": str(
                REVIEW_LEDGER_PATH.relative_to(ROOT)
            ).replace("\\", "/"),
            "persistent_review_ledger_sha256": canonical_lf_sha256(
                REVIEW_LEDGER_PATH
            ),
            "scientific_review_registry_path": str(
                REVIEW_REGISTRY_PATH.relative_to(ROOT)
            ).replace("\\", "/"),
            "scientific_review_registry_sha256": canonical_lf_sha256(
                REVIEW_REGISTRY_PATH
            ),
        },
        "activation": activation,
        "current_review_bindings": current_review_bindings,
        "labels": labels,
        "training_examples": training_examples,
        "label_exclusion_histogram": dict(sorted(exclusion_histogram.items())),
        "shadow_ranking": ranked,
        "storage_contract": {
            "model_bytes": model_path.stat().st_size,
            "model_in_git": True,
            "language_model_weights_in_git": False,
            "large_checkpoint_location": "external_object_storage_or_model_registry",
            "git_retains": [
                "model specification",
                "small ranker parameters",
                "training and validation digests",
                "external artifact URI and SHA-256 when applicable"
            ]
        },
        "boundaries": [
            "Deterministic screening labels are not scientific ranker labels.",
            "A migrated or non-independent review cannot train the ranker.",
            "A scientific review is reusable only while its candidate version and reviewed evidence closure remain unchanged.",
            "Multiple reviews of one immutable candidate version aggregate to one consensus or disagreement training example.",
            "An untrained model emits no learned score.",
            "Even a trained v0 model remains shadow-only and cannot select, authorize, or promote research."
        ]
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if the committed ranker state differs from a fresh replay",
    )
    args = parser.parse_args()
    state = build_state()
    payload = json.dumps(
        state,
        ensure_ascii=True,
        indent=2,
        sort_keys=False,
        allow_nan=False,
    ) + "\n"
    if args.check:
        if not STATE_PATH.exists() or STATE_PATH.read_text(encoding="utf-8") != payload:
            print("hypothesis ranker check failed: generated state is stale")
            return 1
    else:
        STATE_PATH.write_text(payload, encoding="utf-8", newline="\n")
    observed = state["activation"]["observed"]
    print(
        "HYP_RANKER_OK "
        f"status={state['status']} "
        f"eligible_candidate_versions={observed['eligible_candidate_versions']} "
        f"queue={len(state['shadow_ranking'])} "
        "selection_influence=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
