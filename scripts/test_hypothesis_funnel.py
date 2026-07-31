#!/usr/bin/env python3
"""Fault-injection tests for the 100k research-question funnel."""

from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from hypothesis_funnel import (
    POLICY_PATH,
    ROOT,
    STATE_PATH,
    StreamingMerkle,
    canonical_json_bytes,
    canonical_lf_sha256,
    compile_review_decisions,
    derive_rejections,
    generation_policy_digest,
    generated_scope,
    load_base_questions,
    load_operators,
    load_policy,
    review_priority,
    run_funnel,
    unsafe_scope_rejections,
)


def naive_merkle(payloads: list[bytes]) -> str:
    def leaf(payload: bytes) -> bytes:
        return hashlib.sha256(b"\x00" + payload).digest()

    def node(left: bytes, right: bytes) -> bytes:
        return hashlib.sha256(b"\x01" + left + right).digest()

    def tree(items: list[bytes]) -> bytes:
        if len(items) == 1:
            return leaf(items[0])
        split = 1 << ((len(items) - 1).bit_length() - 1)
        return node(tree(items[:split]), tree(items[split:]))

    return tree(payloads).hex() if payloads else hashlib.sha256(b"").hexdigest()


def valid_review(
    item: dict[str, object], index: int, *, verdict: str = "retain_non_executable_research_bet"
) -> dict[str, object]:
    return {
        "review_id": f"TEST-REVIEW-{index:03d}",
        "semantic_signature_sha256": item["semantic_signature_sha256"],
        "verdict": verdict,
        "portfolio_role": "fixture",
        "reviewed_at": "2026-07-31",
        "reviewer": {"actor_id": "test-reviewer", "role": "fixture"},
        "independence": {"source": False, "model_family": False, "context": False},
        "canonical_binding": {"kind": "none", "reason": "test fixture"},
        "decision_protocol": {
            "claim": "fixture claim",
            "basis": "fixture basis",
            "counterargument": "fixture counterargument",
            "decisive_test": "fixture decisive test",
            "verdict": "fixture verdict",
        },
        "limitations": ["fixture limitation"],
    }


class FunnelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy = load_policy()
        cls.state = json.loads(STATE_PATH.read_text(encoding="utf-8"))

    def test_frozen_universe_is_exactly_100000(self) -> None:
        expected = (
            self.policy["input_pool"]["expected_rows"]
            * len(self.policy["mechanism_obligations"])
            * len(self.policy["cost_bridges"])
            * len(self.policy["decisive_tests"])
        )
        self.assertEqual(expected, 100000)
        self.assertEqual(self.state["counts"]["attempts"], 100000)
        self.assertEqual(self.state["bulk_contract"]["full_universe_count"], 100000)

    def test_raw_signatures_are_not_materialized(self) -> None:
        self.assertFalse(self.state["bulk_contract"]["raw_signatures_materialized"])
        self.assertEqual(self.state["memory_contract"]["raw_record_retention"], 0)
        self.assertLess(STATE_PATH.stat().st_size, 100_000)
        self.assertLessEqual(len(self.state["review_queue"]), 60)

    def test_streaming_merkle_matches_recursive_definition(self) -> None:
        for count in (1, 2, 3, 4, 5, 7, 8, 9, 31):
            payloads = [canonical_json_bytes({"i": index}) for index in range(count)]
            stream = StreamingMerkle()
            for payload in payloads:
                stream.add_payload(payload)
            self.assertEqual(stream.root(), naive_merkle(payloads))

    def test_one_bit_mutation_changes_merkle_root(self) -> None:
        original = [b"a", b"b", b"c", b"d"]
        mutated = [b"a", b"b", b"C", b"d"]
        self.assertNotEqual(naive_merkle(original), naive_merkle(mutated))

    def test_partial_replay_is_deterministic(self) -> None:
        first = run_funnel(attempt_limit=2500)
        second = run_funnel(attempt_limit=2500)
        self.assertEqual(
            first["bulk_contract"]["merkle_root_sha256"],
            second["bulk_contract"]["merkle_root_sha256"],
        )
        self.assertEqual(first["rejection_histogram"], second["rejection_histogram"])
        self.assertEqual(first["review_queue"], second["review_queue"])

    def test_changed_operator_invalidates_instance_root(self) -> None:
        changed = copy.deepcopy(self.policy)
        changed["mechanism_obligations"][0]["label"] += " (changed)"
        original = run_funnel(self.policy, attempt_limit=1000)
        mutated = run_funnel(changed, attempt_limit=1000)
        self.assertNotEqual(
            original["source_bindings"]["generation_policy_sha256"],
            mutated["source_bindings"]["generation_policy_sha256"],
        )
        self.assertNotEqual(
            original["bulk_contract"]["merkle_root_sha256"],
            mutated["bulk_contract"]["merkle_root_sha256"],
        )

    def test_universe_underflow_fails_closed(self) -> None:
        changed = copy.deepcopy(self.policy)
        changed["mechanism_obligations"].pop()
        with self.assertRaisesRegex(ValueError, "expected exactly 10"):
            run_funnel(changed, attempt_limit=100)

    def test_lf_and_crlf_have_the_same_frozen_input_hash(self) -> None:
        source = ROOT / self.policy["input_pool"]["path"]
        canonical = source.read_text(encoding="utf-8").replace("\r\n", "\n")
        with tempfile.TemporaryDirectory() as temporary:
            lf = Path(temporary) / "lf.tsv"
            crlf = Path(temporary) / "crlf.tsv"
            lf.write_bytes(canonical.encode("utf-8"))
            crlf.write_bytes(canonical.replace("\n", "\r\n").encode("utf-8"))
            self.assertEqual(canonical_lf_sha256(lf), canonical_lf_sha256(crlf))

    def test_source_pool_is_advisory_and_digest_bound(self) -> None:
        rows = load_base_questions(self.policy)
        self.assertEqual(len(rows), 100)
        self.assertTrue(self.policy["input_pool"]["source_assessment_is_advisory"])
        self.assertGreater(
            sum(row["hard_gate"] == "KILL" for row in rows),
            0,
        )
        self.assertEqual(
            set(self.state["source_bindings"]["evidence_input_sha256"]),
            set(self.policy["evidence_snapshot"]["paths"]),
        )

    def test_known_glv_reencoding_requires_new_mechanism_class(self) -> None:
        rows = load_base_questions(self.policy)
        base = next(row for row in rows if row["family"] == "glv-trace-norm")
        mechanisms = {
            item.id: item
            for item in load_operators(
                self.policy["mechanism_obligations"], "mechanisms"
            )
        }
        costs = {
            item.id: item
            for item in load_operators(self.policy["cost_bridges"], "costs")
        }
        tests = {
            item.id: item
            for item in load_operators(self.policy["decisive_tests"], "tests")
        }
        blocked = derive_rejections(
            base,
            mechanisms["M04-NONGENERIC-SOURCE"],
            costs["C08-END-TO-END"],
            tests["T06-CAUSAL-CONTROLS"],
            self.policy,
        )
        reopened_for_review = derive_rejections(
            base,
            mechanisms["M06-REDUCTION"],
            costs["C08-END-TO-END"],
            tests["T06-CAUSAL-CONTROLS"],
            self.policy,
        )
        self.assertIn("known_closed_pattern_unreopened", blocked)
        self.assertNotIn("known_closed_pattern_unreopened", reopened_for_review)

    def test_prose_only_seeds_never_become_candidates(self) -> None:
        self.assertEqual(
            self.state["warning_histogram"]["exact_mechanism_missing"],
            100000,
        )
        self.assertEqual(self.state["counts"]["admissible"], 0)
        self.assertEqual(self.state["counts"]["recommended"], 0)

    def test_no_authorization_or_promotion_path_exists(self) -> None:
        self.assertEqual(self.state["bulk_contract"]["authorization"], "none")
        self.assertFalse(self.state["bulk_contract"]["route_promotion"])
        self.assertFalse(self.state["bulk_contract"]["exact_target_execution"])
        for key in ("authorized", "route_promotions", "experiment_events"):
            self.assertEqual(self.state["counts"][key], 0)
        self.assertEqual(self.state["counts"]["final_research_bets"], 2)
        self.assertEqual(self.state["counts"]["review_records"], 3)
        self.assertEqual(self.state["counts"]["independent_review_records"], 0)
        self.assertEqual(
            self.state["counts"]["unreviewed_queue_items"],
            self.state["counts"]["review_queue"] - 3,
        )
        self.assertLessEqual(
            len(self.state["final_research_bets"]),
            self.policy["portfolio"]["max_final_research_bets"],
        )
        for bet in self.state["final_research_bets"]:
            self.assertFalse(bet["executable"])
            self.assertFalse(bet["admissible"])
            self.assertFalse(bet["recommended"])
            self.assertFalse(bet["authorized"])
            self.assertFalse(bet["route_promotion"])

    def test_all_100000_normal_forms_are_unique(self) -> None:
        self.assertEqual(
            self.state["counts"]["semantic_normal_forms"],
            self.state["counts"]["attempts"],
        )
        self.assertEqual(
            self.state["rejection_histogram"].get(
                "duplicate_semantic_signature", 0
            ),
            0,
        )
        self.assertGreater(
            self.state["warning_histogram"]["historical_canonical_cluster"],
            0,
        )

    def test_final_bet_limit_fails_closed(self) -> None:
        queue = self.state["review_queue"]
        policy = copy.deepcopy(self.policy)
        policy["review_decisions"] = [
            valid_review(item, index) for index, item in enumerate(queue[:11])
        ]
        with self.assertRaisesRegex(ValueError, "exceed"):
            compile_review_decisions(queue, policy)

    def test_review_binding_cannot_reference_an_outside_signature(self) -> None:
        policy = copy.deepcopy(self.policy)
        decision = valid_review(self.state["review_queue"][0], 0)
        decision["semantic_signature_sha256"] = "f" * 64
        policy["review_decisions"] = [decision]
        with self.assertRaisesRegex(ValueError, "outside the review queue"):
            compile_review_decisions(self.state["review_queue"], policy)

    def test_operator_order_is_not_scientific_identity(self) -> None:
        changed = copy.deepcopy(self.policy)
        for key in ("mechanism_obligations", "cost_bridges", "decisive_tests"):
            changed[key].reverse()
            for operator in changed[key]:
                operator["compatible_types"].reverse()
                operator["capabilities"].reverse()
        self.assertEqual(
            generation_policy_digest(self.policy), generation_policy_digest(changed)
        )
        original = run_funnel(self.policy, attempt_limit=2500)
        reordered = run_funnel(changed, attempt_limit=2500)
        self.assertEqual(
            original["bulk_contract"]["merkle_root_sha256"],
            reordered["bulk_contract"]["merkle_root_sha256"],
        )
        self.assertEqual(original["review_queue"], reordered["review_queue"])

    def test_historical_labels_do_not_rank_the_queue(self) -> None:
        original = copy.deepcopy(self.state["review_queue"][0])
        changed = copy.deepcopy(original)
        changed["source_hard_gate"] = "KILL"
        changed["source_portfolio"] = "KILLED"
        changed["source_canonical"] = "fabricated-historical-label"
        self.assertEqual(review_priority(original), review_priority(changed))

    def test_unsafe_or_exact_target_scope_is_rejected(self) -> None:
        scope = generated_scope(self.policy)
        scope["execution_target"] = "secp256k1-private-key"
        self.assertEqual(
            unsafe_scope_rejections(scope, self.policy),
            ["unsafe_or_exact_target_scope"],
        )
        scope = generated_scope(self.policy)
        scope["field_bits"] = self.policy["safety"]["max_toy_field_bits"] + 1
        self.assertEqual(
            unsafe_scope_rejections(scope, self.policy),
            ["unsafe_or_exact_target_scope"],
        )

    def test_dimension_scores_cannot_clear_an_attack_gate(self) -> None:
        base = next(row for row in load_base_questions(self.policy) if row["type"] == "ATTACK")
        mechanisms = load_operators(self.policy["mechanism_obligations"], "mechanisms")
        costs = load_operators(self.policy["cost_bridges"], "costs")
        tests = load_operators(self.policy["decisive_tests"], "tests")
        mechanism = next(item for item in mechanisms if "ATTACK" in item.compatible_types)
        cost = next(item for item in costs if "attack_scaling_obligation" not in item.capabilities)
        test = next(item for item in tests if "attack_discriminating_test" in item.capabilities)
        inflated = replace(cost, dimensions={key: 99 for key in cost.dimensions})
        reasons = derive_rejections(base, mechanism, inflated, test, self.policy)
        self.assertIn("attack_without_scaling_bridge", reasons)

    def test_prose_only_review_record_fails_closed(self) -> None:
        policy = copy.deepcopy(self.policy)
        decision = valid_review(self.state["review_queue"][0], 0)
        decision["decision_protocol"] = {"claim": "plausible prose only"}
        policy["review_decisions"] = [decision]
        with self.assertRaisesRegex(ValueError, "incomplete decision_protocol"):
            compile_review_decisions(self.state["review_queue"], policy)

    def test_canonical_proposal_binding_is_digest_checked(self) -> None:
        queue_item = next(
            item for item in self.state["review_queue"] if item["base_id"] == "H4-E28"
        )
        policy = copy.deepcopy(self.policy)
        decision = valid_review(queue_item, 0)
        decision["canonical_binding"] = {
            "kind": "research_engine_proposal",
            "proposal_id": "HGP-M16-SOLVER-SLOPE-001",
            "proposal_sha256": "0" * 64,
            "cell_id": "CELL-M-PKC-SMOOTH-M16",
            "route_id": "R-PETIT-COMPOSED-MAPS",
        }
        policy["review_decisions"] = [decision]
        with self.assertRaisesRegex(ValueError, "proposal_sha256"):
            compile_review_decisions(self.state["review_queue"], policy)

    def test_typed_desk_decision_binding_is_checked(self) -> None:
        policy = copy.deepcopy(self.policy)
        decision = next(
            item
            for item in policy["review_decisions"]
            if item["review_id"] == "HFR-2026-07-31-006"
        )
        decision["canonical_binding"]["decision_id"] = "EDD-2099-01-01-999"
        policy["review_decisions"] = [decision]
        with self.assertRaisesRegex(ValueError, "binding is unknown"):
            compile_review_decisions(self.state["review_queue"], policy)

    def test_instance_ids_use_at_least_128_bits(self) -> None:
        ids = [item["seed_id"] for item in self.state["review_queue"]]
        self.assertTrue(ids)
        self.assertEqual(len(ids), len(set(ids)))
        for seed_id in ids:
            self.assertRegex(seed_id, r"^HQS1-[0-9A-F]{32}$")


if __name__ == "__main__":
    unittest.main()
