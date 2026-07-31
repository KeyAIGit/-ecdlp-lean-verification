#!/usr/bin/env python3
"""Fault-injection tests for the 100k research-question funnel."""

from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
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
    load_base_questions,
    load_operators,
    load_policy,
    run_funnel,
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
        self.assertEqual(self.state["counts"]["final_research_bets"], 9)
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
        exemplar = {
            "verdict": "retain_non_executable_research_bet",
            "portfolio_role": "unallocated",
            "decision_protocol": {
                "claim": "fixture",
                "basis": "fixture",
                "counterargument": "fixture",
                "decisive_test": "fixture",
                "verdict": "fixture",
            },
            "limitations": ["fixture"],
        }
        decisions = []
        for index in range(11):
            decision = copy.deepcopy(exemplar)
            decision["seed_id"] = queue[index % len(queue)]["seed_id"]
            if index >= len(queue):
                decision["seed_id"] = f"HQS1-{'F' * 31}{index:X}"
            decisions.append(decision)
        policy["review_decisions"] = decisions
        with self.assertRaisesRegex(ValueError, "exceeds"):
            compile_review_decisions(queue, policy)

    def test_review_binding_cannot_reference_an_outside_seed(self) -> None:
        policy = copy.deepcopy(self.policy)
        policy["review_decisions"] = [
            {
                "seed_id": f"HQS1-{'F' * 32}",
                "verdict": "retain_non_executable_research_bet",
                "portfolio_role": "unallocated",
                "decision_protocol": {
                    "claim": "fixture",
                    "basis": "fixture",
                    "counterargument": "fixture",
                    "decisive_test": "fixture",
                    "verdict": "fixture",
                },
                "limitations": ["fixture"],
            }
        ]
        with self.assertRaisesRegex(ValueError, "outside the review queue"):
            compile_review_decisions(self.state["review_queue"], policy)

    def test_instance_ids_use_at_least_128_bits(self) -> None:
        ids = [item["seed_id"] for item in self.state["review_queue"]]
        self.assertTrue(ids)
        self.assertEqual(len(ids), len(set(ids)))
        for seed_id in ids:
            self.assertRegex(seed_id, r"^HQS1-[0-9A-F]{32}$")


if __name__ == "__main__":
    unittest.main()
