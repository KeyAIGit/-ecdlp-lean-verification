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
        self.assertEqual(
            ["R-GLV-SEMAEV", "R-PETIT-COMPOSED-MAPS"],
            state["open_routes"],
        )
        self.assertEqual(2, state["counts"]["closed_child_claims"])
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

    def test_m16_regime_screen_does_not_close_mechanism_or_route(self) -> None:
        problems, state = self.build()
        self.assertEqual([], problems)
        claims = {item["claim_id"]: item for item in state["claims"]}
        census = claims["CLM-PKC-M16-SECP-FACTOR-BASE-CENSUS"]
        regime = claims["CLM-PKC-M16-CURRENT-MAX24-REGIME"]
        self.assertEqual("confirmed", census["claim_disposition"])
        self.assertEqual("inapplicable", regime["claim_disposition"])
        self.assertIn("frozen in HGP-M16", regime["scope"])
        reopening = " ".join(regime["reopening_conditions"])
        self.assertIn("new claim ID", reopening)
        self.assertIn("scoped truth", reopening)
        self.assertIn("R-PETIT-COMPOSED-MAPS", state["open_routes"])
        variant = next(
            item
            for item in state["mechanism_variants"]
            if item["mechanism_variant_id"]
            == "MV-PKC-PMINUS1-M16-SOLVER-SLOPE"
        )
        self.assertFalse(variant["proposal_seed_eligible"])

    def test_m16_source_mechanism_is_confirmed_but_non_executable(self) -> None:
        problems, state = self.build()
        self.assertEqual([], problems)
        variant = next(
            item
            for item in state["mechanism_variants"]
            if item["mechanism_variant_id"]
            == "MV-PKC-PMINUS1-M16-PUBLISHED-SYSTEM4"
        )
        self.assertEqual(
            "mechanism_specified_cost_unresolved",
            variant["mechanism_status"],
        )
        self.assertFalse(variant["proposal_seed_eligible"])
        claim = next(
            item
            for item in state["claims"]
            if item["claim_id"]
            == "CLM-PKC-M16-SOURCE-MECHANISM-RECOVERY"
        )
        self.assertEqual("confirmed", claim["claim_disposition"])
        self.assertIn("against the sampled target", claim["statement"])
        event = next(
            item
            for item in state["evidence_events"]
            if item["evidence_event_id"]
            == "CEV-PKC-M16-SOURCE-MECHANISM-RECOVERY"
        )
        self.assertEqual("structural", event["event_class"])
        self.assertFalse(event["calibration_eligible"])
        self.assertEqual("none", event["authorization"])
        self.assertIn("R-PETIT-COMPOSED-MAPS", state["open_routes"])

    def test_m16_structural_events_cannot_enter_brier_calibration(self) -> None:
        policy = copy.deepcopy(self.policy)
        event = next(
            item
            for item in policy["evidence_events"]
            if item["evidence_event_id"]
            == "CEV-PKC-M16-SECP-FACTOR-BASE-CENSUS"
        )
        event["calibration_eligible"] = True
        problems, _ = self.build(policy=policy)
        self.assertTrue(
            any("calibration_eligible contradicts" in item for item in problems)
        )

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
