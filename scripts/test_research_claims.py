#!/usr/bin/env python3
"""Regression tests for claim-level Research Engine semantics."""

from __future__ import annotations

import copy
import unittest

from research_claims import (
    DECISIONS_PATH,
    POLICY_PATH,
    load_json,
    validate_and_build,
)


class ResearchClaimTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy = load_json(POLICY_PATH)
        cls.decisions = load_json(DECISIONS_PATH)

    def build(self, policy: dict | None = None, decisions: dict | None = None):
        return validate_and_build(
            copy.deepcopy(policy or self.policy),
            copy.deepcopy(decisions or self.decisions),
        )

    def test_canonical_claim_state_is_non_authorizing(self) -> None:
        problems, state = self.build()
        self.assertEqual([], problems)
        self.assertEqual(["R-GLV-SEMAEV"], state["open_routes"])
        self.assertEqual(1, state["counts"]["closed_child_claims"])
        self.assertEqual(0, state["counts"]["proposal_seed_eligible_variants"])
        self.assertEqual(0, state["counts"]["calibration_eligible_events"])
        self.assertEqual(
            {
                "experiments": 0,
                "route_promotions": 0,
                "exact_target_runs": 0,
            },
            state["authorization"],
        )

    def test_broad_glv_route_stays_open_when_child_is_closed(self) -> None:
        problems, state = self.build()
        self.assertEqual([], problems)
        child = next(
            claim
            for claim in state["claims"]
            if claim["claim_id"]
            == "CLM-GLV-INDEPENDENT-CUBES-FIXED-TARGET"
        )
        self.assertEqual("bounded_negative", child["claim_disposition"])
        self.assertIn("R-GLV-SEMAEV", state["open_routes"])

    def test_certificate_claim_cannot_be_relabelled_lean_kernel(self) -> None:
        policy = copy.deepcopy(self.policy)
        claim = next(
            item
            for item in policy["claims"]
            if item["claim_id"]
            == "CLM-GLV-SEMAEV-COORDINATEWISE-STABILIZER"
        )
        claim["assurance"] = ["lean_kernel"]
        problems, _ = self.build(policy=policy)
        self.assertTrue(
            any("assurance lacks matching evidence" in item for item in problems)
        )

    def test_structural_event_updates_truth_not_brier(self) -> None:
        policy = copy.deepcopy(self.policy)
        event = next(
            item
            for item in policy["evidence_events"]
            if item["evidence_event_id"]
            == "CEV-GLV-SEMAEV-LEAN-COVARIANCE"
        )
        event["calibration_eligible"] = True
        problems, _ = self.build(policy=policy)
        self.assertTrue(
            any("calibration_eligible contradicts" in item for item in problems)
        )

    def test_desired_property_cannot_become_a_seed(self) -> None:
        policy = copy.deepcopy(self.policy)
        variant = next(
            item
            for item in policy["mechanism_variants"]
            if item["kind"] == "desired_property_only"
        )
        variant["proposal_seed_eligible"] = True
        problems, _ = self.build(policy=policy)
        self.assertTrue(
            any("desired properties cannot become proposal seeds" in item
                for item in problems)
        )

    def test_question_status_is_derived_from_route(self) -> None:
        policy = copy.deepcopy(self.policy)
        policy["research_questions"][0]["status"] = "closed"
        problems, _ = self.build(policy=policy)
        self.assertTrue(
            any("derived from the canonical route" in item for item in problems)
        )

    def test_historical_outcome_semantics_are_bound(self) -> None:
        policy = copy.deepcopy(self.policy)
        event = next(
            item
            for item in policy["evidence_events"]
            if item["evidence_event_id"] == "REO-2026-07-24-004"
        )
        event["outcome"] = "bounded_negative"
        problems, _ = self.build(policy=policy)
        self.assertTrue(
            any("historical outcome mismatch" in item for item in problems)
        )


if __name__ == "__main__":
    unittest.main()
