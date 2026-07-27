#!/usr/bin/env python3
"""Fault-injection tests for cross-registry scientific semantics."""

from __future__ import annotations

import copy
import unittest

from check_scientific_semantics import load_json, validate_semantics
from research_claims import validate_and_build as validate_claim_policy


class ScientificSemanticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.decisions = load_json("repo/ECDLP_DECISION_SUBSTRATE.json")
        cls.attacks = load_json("data/attack_registry.json")
        cls.sources = load_json("data/source_registry.json")
        cls.typed = load_json("data/typed_evidence_state.json")
        cls.claims = load_json("data/research_claim_state.json")
        cls.engine = load_json("data/research_engine_state.json")
        cls.lifecycle = load_json("data/research_engine_v02_state.json")
        cls.shadow = load_json("data/research_engine_shadow_intake.json")

    def validate(self, **replacements):
        return validate_semantics(
            replacements.get("decisions", copy.deepcopy(self.decisions)),
            replacements.get("attacks", copy.deepcopy(self.attacks)),
            replacements.get("sources", copy.deepcopy(self.sources)),
            replacements.get("typed", copy.deepcopy(self.typed)),
            replacements.get("claims", copy.deepcopy(self.claims)),
            replacements.get("engine", copy.deepcopy(self.engine)),
            replacements.get("lifecycle", copy.deepcopy(self.lifecycle)),
            replacements.get("shadow", copy.deepcopy(self.shadow)),
        )

    def test_canonical_semantics_agree(self) -> None:
        self.assertEqual([], self.validate())

    def test_petit_weil_contradiction_fails_gate(self) -> None:
        attacks = copy.deepcopy(self.attacks)
        petit = next(
            item
            for item in attacks["attacks"]
            if item["id"] == "IC-4-petit-composed-map"
        )
        petit["secp256k1_constants"] += (
            " "
            "Faithful Petit fails structurally because Weil descent is absent."
        )
        self.assertTrue(
            any("cannot be rejected" in item
                for item in self.validate(attacks=attacks))
        )

    def test_closed_child_cannot_close_broad_glv_route(self) -> None:
        decisions = copy.deepcopy(self.decisions)
        route = next(
            item
            for item in decisions["routes"]
            if item["id"] == "R-GLV-SEMAEV"
        )
        route["status"] = "closed"
        self.assertIn(
            "R-GLV-SEMAEV must remain open_parked",
            self.validate(decisions=decisions),
        )

    def test_invalid_claim_disposition_fails_canonical_gate(self) -> None:
        policy = load_json("repo/RESEARCH_CLAIMS_V0.json")
        claim = next(
            item
            for item in policy["claims"]
            if item["claim_id"]
            == "CLM-GLV-INDEPENDENT-CUBES-FIXED-TARGET"
        )
        claim["claim_disposition"] = "totally_made_up_value"
        problems, _ = validate_claim_policy(
            policy,
            copy.deepcopy(self.decisions),
        )
        self.assertTrue(
            any("claim_disposition is invalid" in problem
                for problem in problems)
        )

    def test_certificate_cannot_be_relabelled_as_lean(self) -> None:
        claims = copy.deepcopy(self.claims)
        claim = next(
            item
            for item in claims["claims"]
            if item["claim_id"]
            == "CLM-GLV-SEMAEV-COORDINATEWISE-STABILIZER"
        )
        claim["assurance"] = ["lean_kernel"]
        self.assertTrue(
            any("certificate-backed" in item
                for item in self.validate(claims=claims))
        )

    def test_kudo_cannot_be_silently_marked_read(self) -> None:
        sources = copy.deepcopy(self.sources)
        source = next(
            item
            for item in sources["sources"]
            if item["id"] == "kudo_yokota_takahashi_yasuda2018"
        )
        source["full_text_status"] = "full_text_inspected"
        self.assertIn(
            "Kudo CANS 2018 must remain full_text_unread",
            self.validate(sources=sources),
        )

    def test_desired_glv_properties_cannot_open_intake(self) -> None:
        typed = copy.deepcopy(self.typed)
        cell = next(
            item
            for item in typed["cells"]
            if item["cell_id"]
            == "CELL-M-GLV-FAITHFUL-PHASE-QUOTIENT"
        )
        cell["seed_eligible"] = True
        self.assertTrue(
            any("cannot be emitted" in item
                for item in self.validate(typed=typed))
        )

    def test_shadow_intake_cannot_authorize_or_activate_glv(self) -> None:
        shadow = copy.deepcopy(self.shadow)
        shadow["proposal_stubs"][0]["route_id"] = "R-GLV-SEMAEV"
        shadow["proposal_stubs"][0]["authorized"] = True
        shadow["counts"]["authorized"] = 1
        problems = self.validate(shadow=shadow)
        self.assertIn("shadow intake must remain non-executable", problems)
        self.assertIn(
            "unspecified phase-preserving GLV properties cannot enter intake",
            problems,
        )


if __name__ == "__main__":
    unittest.main()
