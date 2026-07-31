#!/usr/bin/env python3
"""Fault-injection tests for the shadow hypothesis ranker."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from hypothesis_funnel import STATE_PATH as FUNNEL_STATE_PATH, load_policy
from hypothesis_ranker import (
    ENGINE_STATE_PATH,
    SPEC_PATH,
    STATE_PATH,
    activation_report,
    build_state,
    feature_vector,
    learned_score,
    load_json,
    load_review_ledger,
    review_labels,
    validate_model,
)


class HypothesisRankerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy = load_policy()
        cls.funnel = load_json(FUNNEL_STATE_PATH)
        cls.spec = load_json(SPEC_PATH)
        cls.state = load_json(STATE_PATH)
        cls.ledger = load_review_ledger()

    def test_ranker_is_inactive_and_non_authorizing(self) -> None:
        self.assertEqual(
            self.state["status"], "inactive_insufficient_independent_labels"
        )
        self.assertFalse(self.state["selection_influence"])
        self.assertFalse(self.state["authorization_capability"])
        self.assertFalse(self.state["route_promotion_capability"])
        self.assertEqual(self.state["activation"]["observed"]["eligible_labels"], 0)

    def test_migrated_reviews_are_not_training_labels(self) -> None:
        self.assertEqual(len(self.state["labels"]), 6)
        for label in self.state["labels"]:
            self.assertFalse(label["training_eligible"])
            self.assertIn("independence_not_established", label["exclusion_reasons"])
            self.assertIn("historical_migration", label["exclusion_reasons"])

    def test_only_current_root_reviews_bind_current_selection(self) -> None:
        current_root = self.funnel["bulk_contract"]["merkle_root_sha256"]
        current = [
            item
            for item in self.ledger
            if item["batch_merkle_root_sha256"] == current_root
        ]
        historical = [
            item
            for item in self.ledger
            if item["batch_merkle_root_sha256"] != current_root
        ]
        self.assertEqual(3, len(current))
        self.assertEqual(3, len(historical))
        self.assertEqual(
            {
                "HFR-2026-07-31-004",
                "HFR-2026-07-31-005",
                "HFR-2026-07-31-006",
            },
            {
                item["review_record"]["review_id"] for item in current
            },
        )

    def test_untrained_model_emits_no_scores_or_reordering(self) -> None:
        self.assertTrue(
            all(item["learned_score"] is None for item in self.state["shadow_ranking"])
        )
        self.assertEqual(
            [item["semantic_signature_sha256"] for item in self.state["shadow_ranking"]],
            [item["semantic_signature_sha256"] for item in self.funnel["review_queue"]],
        )

    def test_forbidden_historical_fields_do_not_enter_features(self) -> None:
        candidate = copy.deepcopy(self.funnel["review_queue"][0])
        original = feature_vector(candidate, self.spec)
        candidate["source_hard_gate"] = "KILL"
        candidate["source_portfolio"] = "KILLED"
        candidate["source_canonical"] = "fabricated"
        candidate["seed_id"] = "HQS1-" + "F" * 32
        self.assertEqual(original, feature_vector(candidate, self.spec))
        self.assertTrue(
            set(original).isdisjoint(self.spec["feature_contract"]["forbidden_features"])
        )

    def test_independence_is_required_but_not_sufficient_for_activation(self) -> None:
        ledger = copy.deepcopy(self.ledger)
        for entry in ledger:
            review = entry["review_record"]
            review["independence"] = {
                "source": True,
                "model_family": True,
                "context": True,
            }
            review["reviewer"]["role"] = "independent-scientific-review"
            entry["review_record_sha256"] = "fixture"
        labels = review_labels(ledger, self.spec)
        self.assertEqual(sum(item["training_eligible"] for item in labels), 6)
        native_outcomes = len(load_json(ENGINE_STATE_PATH).get("native_outcomes", []))
        activation = activation_report(labels, native_outcomes, self.spec)
        self.assertFalse(activation["ready_for_training"])
        self.assertIn("eligible_labels", activation["unmet"])
        self.assertIn("negative_labels", activation["unmet"])

    def test_selection_influence_fault_is_rejected(self) -> None:
        model_path = Path(self.state["source_bindings"]["model_path"])
        model = load_json(Path(__file__).resolve().parent.parent / model_path)
        model["selection_influence"] = True
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "model.json"
            path.write_text(json.dumps(model), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "cannot influence selection"):
                validate_model(model, self.spec, path)

    def test_persistent_review_ledger_is_digest_bound(self) -> None:
        ledger = copy.deepcopy(self.ledger)
        ledger[0]["review_record"]["limitations"].append("post-hoc mutation")
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "ledger.jsonl"
            path.write_text(
                "\n".join(json.dumps(item, sort_keys=True) for item in ledger) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "digest mismatch"):
                load_review_ledger(path)

    def test_shadow_scoring_math_is_deterministic(self) -> None:
        names = self.spec["feature_contract"]["numeric"]
        model = {
            "trained": True,
            "feature_names": names,
            "bias": 0.0,
            "weights": {name: 0.1 for name in names},
            "normalization": {
                name: {"mean": 0.0, "scale": 1.0} for name in names
            },
        }
        features = {name: 1.0 for name in names}
        self.assertEqual(learned_score(features, model), learned_score(features, model))
        self.assertGreater(learned_score(features, model), 0.5)

    def test_generated_state_replays_exactly(self) -> None:
        self.assertEqual(build_state(), self.state)


if __name__ == "__main__":
    unittest.main()
