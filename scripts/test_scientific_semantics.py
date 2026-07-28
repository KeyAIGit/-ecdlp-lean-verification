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

    def test_wcc_cannot_be_silently_downgraded_or_conflated(self) -> None:
        sources = copy.deepcopy(self.sources)
        wcc = next(
            item
            for item in sources["sources"]
            if item["id"] == "yokota_kudo_yasuda2017_wcc"
        )
        kudo = next(
            item
            for item in sources["sources"]
            if item["id"] == "kudo_yokota_takahashi_yasuda2018"
        )
        wcc["full_text_status"] = "full_text_unread"
        wcc["title"] = kudo["title"]
        problems = self.validate(sources=sources)
        self.assertIn(
            "WCC 2017 must retain its inspected full-text status",
            problems,
        )
        self.assertIn(
            "WCC 2017 and CANS 2018 must remain distinct sources",
            problems,
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

    def test_m16_scoped_blocker_cannot_be_promoted_to_closure(self) -> None:
        typed = copy.deepcopy(self.typed)
        cell = next(
            item
            for item in typed["cells"]
            if item["cell_id"] == "CELL-M-PKC-SMOOTH-M16"
        )
        cell["status"] = "decided_closed"
        cell["seed_eligible"] = False
        cell["cost_quantity_status"] = "defined"
        cell["authorization"] = "experiment"
        problems = self.validate(typed=typed)
        self.assertIn(
            "M16 scoped blocker must leave the cell open", problems
        )
        self.assertIn(
            "M16 scoped blocker must leave the cell seed-eligible", problems
        )
        self.assertIn(
            "M16 semantic result must leave cost status partial", problems
        )
        self.assertIn(
            "M16 semantic result cannot authorize execution", problems
        )

    def test_m16_semantic_certificate_cannot_be_detached(self) -> None:
        typed = copy.deepcopy(self.typed)
        claim_id = "SC-PKC-M16-SEMANTIC-BRIDGE-RESULT"
        cell = next(
            item
            for item in typed["cells"]
            if item["cell_id"] == "CELL-M-PKC-SMOOTH-M16"
        )
        cell["source_claim_ids"].remove(claim_id)
        cell["cost_quantity"]["source_claim_ids"].remove(claim_id)
        barrier = next(
            item
            for item in typed["barriers"]
            if item["id"] == "B-PKC-M16-COMPLETE-COST-BRIDGE"
        )
        barrier["source_claim_ids"].remove(claim_id)
        claim = next(
            item
            for item in typed["source_claims"]
            if item["id"] == claim_id
        )
        claim["artifact_sha256"] = "0" * 64
        problems = self.validate(typed=typed)
        self.assertIn(
            "M16 cell must retain its semantic bridge certificate",
            problems,
        )
        self.assertIn(
            "M16 cost quantity must retain its semantic bridge certificate",
            problems,
        )
        self.assertIn(
            "M16 complete-cost barrier must retain its semantic bridge certificate",
            problems,
        )
        self.assertIn("M16 semantic bridge artifact hash drifted", problems)

    def test_m16_exceptional_certificate_boundaries_cannot_drift(self) -> None:
        typed = copy.deepcopy(self.typed)
        claim_id = "SC-PKC-M16-EXCEPTIONAL-FIBER-RESULT"
        cell = next(
            item
            for item in typed["cells"]
            if item["cell_id"] == "CELL-M-PKC-SMOOTH-M16"
        )
        cell["source_claim_ids"].remove(claim_id)
        cell["cost_quantity"]["source_claim_ids"].remove(claim_id)
        barrier = next(
            item
            for item in typed["barriers"]
            if item["id"] == "B-PKC-M16-COMPLETE-COST-BRIDGE"
        )
        barrier["source_claim_ids"].remove(claim_id)
        claim = next(
            item
            for item in typed["source_claims"]
            if item["id"] == claim_id
        )
        claim["artifact_sha256"] = "0" * 64
        claim["statement"] = "Unscoped projective equivalence."
        claim["boundary"] = "Fully independent and fully priced."
        problems = self.validate(typed=typed)
        self.assertIn(
            "M16 cell must retain its exceptional-fiber certificate",
            problems,
        )
        self.assertIn(
            "M16 cost quantity must retain its exceptional-fiber certificate",
            problems,
        )
        self.assertIn(
            "M16 complete-cost barrier must retain its exceptional-fiber certificate",
            problems,
        )
        self.assertIn("M16 exceptional-fiber artifact hash drifted", problems)
        self.assertIn(
            "M16 exceptional-fiber claim must retain its nonsingular "
            "characteristic boundary",
            problems,
        )
        self.assertTrue(
            any(
                "M16 exceptional-fiber claim must retain" in problem
                and "source independence" in problem
                for problem in problems
            )
        )

    def test_m16_projective_certificate_boundaries_cannot_drift(self) -> None:
        typed = copy.deepcopy(self.typed)
        claim_id = "SC-PKC-M16-PROJECTIVE-S17-BRIDGE-RESULT"
        cell = next(
            item
            for item in typed["cells"]
            if item["cell_id"] == "CELL-M-PKC-SMOOTH-M16"
        )
        cell["source_claim_ids"].remove(claim_id)
        cell["cost_quantity"]["source_claim_ids"].remove(claim_id)
        barrier = next(
            item
            for item in typed["barriers"]
            if item["id"] == "B-PKC-M16-COMPLETE-COST-BRIDGE"
        )
        barrier["source_claim_ids"].remove(claim_id)
        claim = next(
            item
            for item in typed["source_claims"]
            if item["id"] == claim_id
        )
        claim["artifact_sha256"] = "0" * 64
        claim["statement"] = "An unspecified polynomial was checked."
        claim["boundary"] = "Fully independent, priced, and executable."
        problems = self.validate(typed=typed)
        self.assertIn(
            "M16 cell must retain its projective-S17 bridge certificate",
            problems,
        )
        self.assertIn(
            "M16 cost quantity must retain its projective-S17 certificate",
            problems,
        )
        self.assertIn(
            "M16 complete-cost barrier must retain its projective-S17 certificate",
            problems,
        )
        self.assertIn("M16 projective-S17 artifact hash drifted", problems)
        for boundary in (
            "source independence",
            "calibration",
            "partial cost quantity",
            "unpriced solving cost",
            "unpriced rank",
            "unpriced yield",
            "generic-forward assurance boundary",
            "narrowed-open barrier",
            "no-authorization boundary",
        ):
            self.assertTrue(
                any(
                    "M16 projective-S17 claim must retain" in problem
                    and boundary in problem
                    for problem in problems
                )
            )

    def test_m16_resultant_kernel_certificate_and_blocker_cannot_drift(
        self,
    ) -> None:
        typed = copy.deepcopy(self.typed)
        claim_id = "SC-PKC-M16-PROJECTIVE-RESULTANT-KERNEL-RESULT"
        cell = next(
            item
            for item in typed["cells"]
            if item["cell_id"] == "CELL-M-PKC-SMOOTH-M16"
        )
        cell["source_claim_ids"].remove(claim_id)
        cell["cost_quantity"]["source_claim_ids"].remove(claim_id)
        cell["relation_action"] = (
            "The already proved fixed-degree theorem is still pending."
        )
        cell["boundary"] = "Executable with retained hypotheses."
        barrier = next(
            item
            for item in typed["barriers"]
            if item["id"] == "B-PKC-M16-COMPLETE-COST-BRIDGE"
        )
        barrier["source_claim_ids"].remove(claim_id)
        barrier["exact_scope"] = (
            "The barrier is pending a kernel-checked fixed-degree "
            "projective resultant common-root theorem."
        )
        barrier["reopening_conditions"] = [
            "Kernel-check a fixed-degree projective resultant "
            "common-root theorem."
        ]
        claim = next(
            item
            for item in typed["source_claims"]
            if item["id"] == claim_id
        )
        claim["artifact_sha256"] = "0" * 64
        claim["statement"] = "An unspecified determinant was checked."
        claim["boundary"] = "Fully independent, priced, and executable."
        problems = self.validate(typed=typed)
        self.assertIn(
            "M16 cell must retain its projective-resultant kernel certificate",
            problems,
        )
        self.assertIn(
            "M16 cost quantity must retain its projective-resultant "
            "kernel certificate",
            problems,
        )
        self.assertIn(
            "M16 complete-cost barrier must retain its projective-resultant "
            "kernel certificate",
            problems,
        )
        self.assertIn(
            "M16 projective-resultant artifact hash drifted",
            problems,
        )
        for boundary in (
            "fixed-degree theorem",
            "literal matrix bridge",
            "unit-one convention",
            "zero-form coverage",
            "projective-infinity coverage",
            "kernel-bound non-run assurance",
            "recursive-specialization blocker",
            "universal-induction blocker",
            "zero retention",
            "no-authorization boundary",
            "no-promotion boundary",
        ):
            self.assertTrue(
                any(
                    "M16 projective-resultant claim must retain" in problem
                    and boundary in problem
                    for problem in problems
                )
            )
        self.assertIn(
            "M16 complete-cost barrier cannot reopen the kernel-checked "
            "fixed-degree theorem",
            problems,
        )
        self.assertIn(
            "M16 complete-cost reopening must require recursive "
            "specialization and universal induction",
            problems,
        )
        for boundary in (
            "narrowed mechanism gap",
            "recursive specialization",
            "universal induction",
            "zero retention",
            "no hypothesis retention",
            "no experiment authorization",
            "no route promotion",
        ):
            self.assertIn(f"M16 cell must retain {boundary}", problems)

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

    def test_task016_phase_cannot_reopen_sanitation_or_authorization(self) -> None:
        decisions = copy.deepcopy(self.decisions)
        decisions["phase_policy"]["phase"] = "research-engine-v0.2-sanitation"
        decisions["phase_policy"]["bounded_exploration_authorized"] = True
        decisions["maintenance_cycle"]["status"] = "active_remediation_draft"
        problems = self.validate(decisions=decisions)
        self.assertIn(
            "current phase must remain evidence-bounded desk priority",
            problems,
        )
        self.assertIn(
            "current phase must authorize zero bounded experiments",
            problems,
        )
        self.assertIn("TASK-010 maintenance cycle boundary drifted", problems)


if __name__ == "__main__":
    unittest.main()
