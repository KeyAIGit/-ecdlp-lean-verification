#!/usr/bin/env python3
"""Regression tests for the million-scale typed screening space."""

from __future__ import annotations

import copy
import hashlib
import json
import unittest
from dataclasses import replace

from hypothesis_space_funnel import (
    FastStreamingMerkle,
    LiteCandidate,
    MAP_PATH,
    POLICY_PATH,
    STATE_PATH,
    load_base_questions,
    load_challenges,
    load_operators,
    load_parent,
    load_policy,
    public_candidate,
    run_space,
    semantic_signature,
)


def reference_merkle_root(leaves: list[bytes]) -> bytes:
    """Small independent RFC6962 implementation used only by regression tests."""
    if not leaves:
        return hashlib.sha256(b"").digest()
    if len(leaves) == 1:
        return leaves[0]
    split = 1 << ((len(leaves) - 1).bit_length() - 1)
    left = reference_merkle_root(leaves[:split])
    right = reference_merkle_root(leaves[split:])
    return hashlib.sha256(b"\x01" + left + right).digest()


class HypothesisSpaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy = load_policy()
        cls.state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        cls.map_state = json.loads(MAP_PATH.read_text(encoding="utf-8"))
        cls.parent_policy, _ = load_parent(cls.policy)
        cls.bases = load_base_questions(cls.parent_policy)
        cls.mechanisms = sorted(
            load_operators(
                cls.parent_policy["mechanism_obligations"], "mechanism obligations"
            ),
            key=lambda item: item.id,
        )
        cls.costs = sorted(
            load_operators(cls.parent_policy["cost_bridges"], "cost bridges"),
            key=lambda item: item.id,
        )
        cls.tests = sorted(
            load_operators(cls.parent_policy["decisive_tests"], "decisive tests"),
            key=lambda item: item.id,
        )
        cls.challenges = load_challenges(cls.policy)

    def test_frozen_universe_is_exactly_one_million(self) -> None:
        self.assertEqual(self.policy["expansion"]["expected_signatures"], 1_000_000)
        self.assertEqual(self.state["counts"]["attempts"], 1_000_000)
        self.assertEqual(self.state["counts"]["typed_cells"], 1_000_000)

    def test_temperature_partition_is_total(self) -> None:
        counts = self.state["counts"]
        self.assertEqual(counts["cold"] + counts["warm"] + counts["hot"], 1_000_000)
        self.assertEqual(counts["hot"], 0)

    def test_raw_million_rows_are_not_materialized(self) -> None:
        self.assertFalse(self.state["bulk_contract"]["raw_signatures_materialized"])
        self.assertEqual(self.state["memory_contract"]["raw_record_retention"], 0)
        self.assertEqual(self.state["memory_contract"]["sqlite_rows"], 0)
        self.assertLess(STATE_PATH.stat().st_size, 250_000)
        self.assertLess(MAP_PATH.stat().st_size, 350_000)

    def test_parent_funnel_root_is_frozen(self) -> None:
        expected = self.policy["parent_funnel"]["expected_merkle_root_sha256"]
        self.assertEqual(
            self.state["source_bindings"]["parent_merkle_root_sha256"], expected
        )

    def test_partial_replay_is_deterministic(self) -> None:
        first, first_map = run_space(attempt_limit=5_000)
        second, second_map = run_space(attempt_limit=5_000)
        self.assertEqual(
            first["bulk_contract"]["instance_root_sha256"],
            second["bulk_contract"]["instance_root_sha256"],
        )
        self.assertEqual(first["rejection_histogram"], second["rejection_histogram"])
        self.assertEqual(first_map["regions"], second_map["regions"])

    def test_streaming_merkle_matches_independent_rfc6962_reference(self) -> None:
        leaves = [
            hashlib.sha256(b"\x00" + index.to_bytes(4, "big")).digest()
            for index in range(33)
        ]
        for count in (0, 1, 2, 3, 4, 5, 7, 8, 9, 15, 16, 17, 31, 32, 33):
            streaming = FastStreamingMerkle()
            for leaf in leaves[:count]:
                streaming.add_leaf_hash(leaf)
            self.assertEqual(streaming.root_bytes(), reference_merkle_root(leaves[:count]))

    def test_operator_content_change_invalidates_scientific_signature(self) -> None:
        original = semantic_signature(
            self.bases[0],
            self.mechanisms[0],
            self.costs[0],
            self.tests[0],
            self.challenges[0],
            self.parent_policy["safety"]["primary_threat_model"],
        )
        changed = semantic_signature(
            self.bases[0],
            replace(self.mechanisms[0], label=self.mechanisms[0].label + " changed"),
            self.costs[0],
            self.tests[0],
            self.challenges[0],
            self.parent_policy["safety"]["primary_threat_model"],
        )
        self.assertNotEqual(original, changed)

    def test_scientific_and_evaluation_identities_are_separate(self) -> None:
        candidate = LiteCandidate(0, 0, 0, 0, 0, (0,) * 7)
        first = public_candidate(
            candidate,
            self.bases,
            self.mechanisms,
            self.costs,
            self.tests,
            self.challenges,
            self.policy["portfolio"]["dimension_names"],
            self.parent_policy,
            "0" * 64,
        )
        second = public_candidate(
            candidate,
            self.bases,
            self.mechanisms,
            self.costs,
            self.tests,
            self.challenges,
            self.policy["portfolio"]["dimension_names"],
            self.parent_policy,
            "1" * 64,
        )
        self.assertEqual(
            first["scientific_signature_sha256"],
            second["scientific_signature_sha256"],
        )
        self.assertNotEqual(
            first["evaluation_instance_sha256"],
            second["evaluation_instance_sha256"],
        )
        self.assertEqual(first["batch_occurrence_ordinal"], 0)

    def test_review_queue_has_three_noninterchangeable_identities(self) -> None:
        ordinals: set[int] = set()
        for item in self.state["review_queue"]:
            self.assertEqual(
                item["scientific_signature_sha256"],
                item["semantic_signature_sha256"],
            )
            self.assertTrue(item["seed_id"].endswith(
                item["evaluation_instance_sha256"][:32].upper()
            ))
            self.assertEqual(
                item["space_instance_root_sha256"],
                self.state["bulk_contract"]["instance_root_sha256"],
            )
            ordinal = item["batch_occurrence_ordinal"]
            self.assertIsInstance(ordinal, int)
            self.assertGreaterEqual(ordinal, 0)
            self.assertLess(ordinal, 1_000_000)
            ordinals.add(ordinal)
        self.assertEqual(len(ordinals), len(self.state["review_queue"]))

    def test_changed_challenge_invalidates_root(self) -> None:
        changed = copy.deepcopy(self.policy)
        changed["adversarial_challenges"][0]["label"] += " changed"
        original, _ = run_space(attempt_limit=2_000)
        mutated, _ = run_space(changed, attempt_limit=2_000)
        self.assertNotEqual(
            original["bulk_contract"]["instance_root_sha256"],
            mutated["bulk_contract"]["instance_root_sha256"],
        )

    def test_duplicate_challenge_id_fails_closed(self) -> None:
        changed = copy.deepcopy(self.policy)
        changed["adversarial_challenges"][1]["id"] = changed[
            "adversarial_challenges"
        ][0]["id"]
        with self.assertRaisesRegex(ValueError, "challenge IDs"):
            run_space(changed, attempt_limit=10)

    def test_safety_drift_fails_closed(self) -> None:
        changed = copy.deepcopy(self.policy)
        changed["safety"]["authorized"] = 1
        with self.assertRaisesRegex(ValueError, "safety boundary"):
            run_space(changed, attempt_limit=10)

    def test_challenge_axis_has_complete_coverage(self) -> None:
        coverage = self.state["challenge_coverage"]
        self.assertEqual(len(coverage), 10)
        self.assertEqual(sum(item["attempts"] for item in coverage.values()), 1_000_000)
        for item in coverage.values():
            self.assertEqual(item["attempts"], 100_000)
            self.assertEqual(item.get("cold", 0) + item.get("warm", 0), 100_000)

    def test_review_queue_is_small_and_non_executable(self) -> None:
        queue = self.state["review_queue"]
        self.assertLessEqual(len(queue), self.policy["portfolio"]["max_review_queue"])
        self.assertGreater(len(queue), 0)
        for item in queue:
            self.assertFalse(item["executable"])
            self.assertFalse(item["admissible"])
            self.assertFalse(item["recommended"])
            self.assertFalse(item["authorized"])
            self.assertFalse(item["route_promotion"])

    def test_queue_respects_diversity_caps(self) -> None:
        queue = self.state["review_queue"]
        bases = [item["base_id"] for item in queue]
        families = [item["family"] for item in queue]
        self.assertEqual(len(bases), len(set(bases)))
        self.assertEqual(len(families), len(set(families)))
        challenge_counts: dict[str, int] = {}
        for item in queue:
            key = item["adversarial_challenge_id"]
            challenge_counts[key] = challenge_counts.get(key, 0) + 1
        self.assertLessEqual(
            max(challenge_counts.values()), self.policy["portfolio"]["max_per_challenge"]
        )

    def test_map_and_state_share_one_identity(self) -> None:
        self.assertEqual(
            self.map_state["instance_root_sha256"],
            self.state["bulk_contract"]["instance_root_sha256"],
        )
        self.assertEqual(self.map_state["counts"], self.state["counts"])

    def test_feedback_is_bound_but_cannot_promote(self) -> None:
        feedback = self.state["feedback_context"]
        self.assertGreaterEqual(feedback["review_records"], 3)
        self.assertEqual(feedback["independent_review_records"], 0)
        self.assertEqual(feedback["native_engine_outcomes"], 0)
        self.assertEqual(feedback["automatic_hot_promotions"], 0)
        self.assertEqual(feedback, self.map_state["feedback_context"])

    def test_region_map_is_an_exact_aggregate(self) -> None:
        regions = self.map_state["regions"]
        self.assertEqual(sum(item["cells"] for item in regions), 1_000_000)
        self.assertEqual(sum(item["cold"] for item in regions), self.state["counts"]["cold"])
        self.assertEqual(sum(item["warm"] for item in regions), self.state["counts"]["warm"])
        self.assertTrue(all(item["hot"] == 0 for item in regions))

    def test_no_authorization_path_exists(self) -> None:
        counts = self.state["counts"]
        for key in ("admissible", "recommended", "authorized", "route_promotions", "experiment_events"):
            self.assertEqual(counts[key], 0)
        self.assertEqual(self.map_state["authorization"], "none")

    def test_typed_identity_is_not_called_novelty(self) -> None:
        self.assertTrue(self.state["bulk_contract"]["typed_tuple_uniqueness_checked"])
        self.assertFalse(self.state["bulk_contract"]["semantic_novelty_proved"])
        joined = " ".join(self.state["boundaries"]).lower()
        self.assertIn("not semantic novelty", joined)

    def test_policy_remains_zero_model_and_zero_execution(self) -> None:
        safety = self.policy["safety"]
        self.assertEqual(safety["language_model_calls"], 0)
        self.assertFalse(safety["all_outputs_executable"])
        self.assertFalse(safety["experiments_authorized"])
        self.assertFalse(safety["exact_target_execution"])

    def test_source_file_is_registered(self) -> None:
        self.assertTrue(POLICY_PATH.exists())
        self.assertTrue(STATE_PATH.exists())
        self.assertTrue(MAP_PATH.exists())


if __name__ == "__main__":
    unittest.main()
