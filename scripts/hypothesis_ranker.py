#!/usr/bin/env python3
"""Build the non-authorizing shadow state for the hypothesis ranker."""

from __future__ import annotations

import argparse
import json
import math
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


SPEC_PATH = ROOT / "repo" / "HYPOTHESIS_RANKER_V0.json"
STATE_PATH = ROOT / "data" / "hypothesis_ranker_state.json"
ENGINE_STATE_PATH = ROOT / "data" / "research_engine_state.json"
REVIEW_LEDGER_PATH = ROOT / "data" / "hypothesis_review_ledger.jsonl"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def feature_vector(candidate: dict[str, Any], spec: dict[str, Any]) -> dict[str, float]:
    names = spec["feature_contract"]["numeric"]
    dimensions = candidate["dimensions"]
    if set(names) - set(dimensions):
        raise ValueError("candidate is missing a ranker feature")
    return {name: float(dimensions[name]) for name in names}


def load_review_ledger(path: Path = REVIEW_LEDGER_PATH) -> list[dict[str, Any]]:
    records = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
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
        digest = sha256_json(review)
        if item.get("review_record_sha256") != digest:
            raise ValueError("review ledger record digest mismatch")
        if item.get("label_id") != f"HRL-{digest[:24].upper()}":
            raise ValueError("review ledger label identity mismatch")
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
) -> None:
    current_reviews = {
        item["review_id"]: item for item in policy["review_decisions"]
    }
    current_ledger = {
        item["review_record"]["review_id"]: item
        for item in ledger
        if item["funnel_id"] == policy["funnel_id"]
        and item["batch_merkle_root_sha256"]
        == funnel_state["bulk_contract"]["merkle_root_sha256"]
    }
    if set(current_reviews) != set(current_ledger):
        raise ValueError("current funnel reviews and persistent ledger have drifted")
    queue = {
        item["semantic_signature_sha256"]: item
        for item in funnel_state["review_queue"]
    }
    for review_id, review in current_reviews.items():
        entry = current_ledger[review_id]
        if entry["review_record"] != review:
            raise ValueError("persistent review record differs from current policy")
        candidate = queue.get(review["semantic_signature_sha256"])
        if candidate is None:
            raise ValueError("current review is outside the current queue")
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


def review_labels(
    ledger: list[dict[str, Any]],
    spec: dict[str, Any],
) -> list[dict[str, Any]]:
    positives = set(spec["label_contract"]["positive"])
    negatives = set(spec["label_contract"]["negative"])
    required_axes = set(spec["label_contract"]["required_independence_axes"])
    labels: list[dict[str, Any]] = []
    for entry in ledger:
        review = entry["review_record"]
        signature = entry["semantic_signature_sha256"]
        verdict = review["verdict"]
        exclusion_reasons: list[str] = []
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
        if "migration" in review["reviewer"]["role"]:
            exclusion_reasons.append("historical_migration")

        candidate = entry["candidate_snapshot"]
        record_sha = entry["review_record_sha256"]
        labels.append(
            {
                "label_id": entry["label_id"],
                "review_id": review["review_id"],
                "review_record_sha256": record_sha,
                "semantic_signature_sha256": signature,
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


def activation_report(
    labels: list[dict[str, Any]],
    native_outcomes: int,
    spec: dict[str, Any],
) -> dict[str, Any]:
    gate = spec["activation_gate"]
    eligible = [item for item in labels if item["training_eligible"]]
    positives = sum(item["binary_label"] == 1 for item in eligible)
    negatives = sum(item["binary_label"] == 0 for item in eligible)
    families = len({item["family"] for item in eligible})
    reviewers = len({item["reviewer_actor_id"] for item in eligible})
    observed = {
        "eligible_labels": len(eligible),
        "positive_labels": positives,
        "negative_labels": negatives,
        "distinct_families": families,
        "distinct_reviewers": reviewers,
        "native_outcomes": native_outcomes,
    }
    required = {
        "eligible_labels": gate["minimum_eligible_labels"],
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
    validate_current_review_bindings(ledger, policy, funnel_state)
    labels = review_labels(ledger, spec)
    engine_state = load_json(ENGINE_STATE_PATH)
    native_outcomes = len(engine_state.get("native_outcomes", []))
    activation = activation_report(labels, native_outcomes, spec)

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
        },
        "activation": activation,
        "labels": labels,
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
        f"eligible_labels={observed['eligible_labels']} "
        f"queue={len(state['shadow_ranking'])} "
        "selection_influence=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
