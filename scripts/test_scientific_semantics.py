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
            "M16 complete-cost reopening must require exact TASK-023 "
            "affine/infinity chart-polynomial cover",
            problems,
        )
        for boundary in (
            "narrowed mechanism gap",
            "TASK-020 specialization result",
            "actual frozen family",
            "universal witness extraction",
            "universal all-stage witness chain",
            "TASK-022 guarded representation",
            "TASK-023 chart-cover result",
            "raw variable count",
            "fixed-mask variable count",
            "chart degree ceilings",
            "open regular-locus blocker",
            "exact literal finite family",
            "exact chart-cover result",
            "no direct-S17 overclaim",
            "no production mask enumeration",
            "no genericity overclaim",
            "no witness-uniqueness overclaim",
            "no raw-count independence overclaim",
            "zero retention",
            "no hypothesis retention",
            "no experiment authorization",
            "no route promotion",
        ):
            self.assertIn(f"M16 cell must retain {boundary}", problems)

    def test_m16_frozen_cr_specialization_and_blocker_cannot_drift(
        self,
    ) -> None:
        typed = copy.deepcopy(self.typed)
        claim_id = "SC-PKC-M16-FROZEN-CR-SPECIALIZATION-RESULT"
        cell = next(
            item
            for item in typed["cells"]
            if item["cell_id"] == "CELL-M-PKC-SMOOTH-M16"
        )
        cell["source_claim_ids"].remove(claim_id)
        cell["cost_quantity"]["source_claim_ids"].remove(claim_id)
        cell["relation_action"] = (
            "The frozen specialization is still pending."
        )
        cell["boundary"] = "Executable with complete cost and promotion."
        barrier = next(
            item
            for item in typed["barriers"]
            if item["id"] == "B-PKC-M16-COMPLETE-COST-BRIDGE"
        )
        barrier["source_claim_ids"].remove(claim_id)
        barrier["exact_scope"] = (
            "The barrier is open only on the exact recursive frozen C_r "
            "specialization."
        )
        barrier["reopening_conditions"] = [
            "Kernel-check the exact recursive frozen C_r specialization."
        ]
        claim = next(
            item
            for item in typed["source_claims"]
            if item["id"] == claim_id
        )
        claim["artifact_sha256"] = "0" * 64
        claim["evidence_path"] = "wrong/artifact.json"
        claim["statement"] = "An arbitrary recursive polynomial was checked."
        claim["boundary"] = "The route is priced, executable, and promoted."
        problems = self.validate(typed=typed)
        self.assertIn(
            "M16 cell must retain its frozen-Cr specialization "
            "kernel certificate",
            problems,
        )
        self.assertIn(
            "M16 cost quantity must retain its frozen-Cr specialization "
            "kernel certificate",
            problems,
        )
        self.assertIn(
            "M16 complete-cost barrier must retain its frozen-Cr "
            "specialization kernel certificate",
            problems,
        )
        self.assertIn(
            "M16 frozen-Cr specialization artifact hash drifted",
            problems,
        )
        self.assertIn(
            "M16 frozen-Cr specialization evidence path drifted",
            problems,
        )
        for boundary in (
            "actual frozen family",
            "explicit coefficient map",
            "fixed formal degrees",
            "unit-one convention",
            "affine-output branch",
            "infinity-output branch",
            "universal output-degree bound",
            "unconditional one-step common-root interface",
            "kernel-bound non-run assurance",
            "universal witness-extraction blocker",
            "full witness tree",
            "partial cost quantity",
            "unpriced solving cost",
            "unpriced rank",
            "unpriced yield",
            "zero retention",
            "no-authorization boundary",
            "no-promotion boundary",
        ):
            self.assertTrue(
                any(
                    "M16 frozen-Cr specialization claim must retain"
                    in problem
                    and boundary in problem
                    for problem in problems
                )
            )
        self.assertIn(
            "M16 complete-cost barrier cannot reopen the kernel-checked "
            "frozen-Cr specialization",
            problems,
        )
        self.assertIn(
            "M16 complete-cost reopening must require exact TASK-023 "
            "affine/infinity chart-polynomial cover",
            problems,
        )
        self.assertIn(
            "M16 complete-cost reopening cannot require the already "
            "kernel-checked frozen-Cr specialization",
            problems,
        )
        for boundary in (
            "narrowed mechanism gap",
            "TASK-020 specialization result",
            "actual frozen family",
            "universal witness extraction",
            "universal all-stage witness chain",
            "TASK-022 guarded representation",
            "TASK-023 chart-cover result",
            "raw variable count",
            "fixed-mask variable count",
            "chart degree ceilings",
            "open regular-locus blocker",
            "exact literal finite family",
            "exact chart-cover result",
            "no direct-S17 overclaim",
            "no production mask enumeration",
            "no genericity overclaim",
            "no witness-uniqueness overclaim",
            "no raw-count independence overclaim",
            "zero retention",
            "no hypothesis retention",
            "no experiment authorization",
            "no route promotion",
        ):
            self.assertIn(f"M16 cell must retain {boundary}", problems)

    def test_m16_frozen_projective_witness_cannot_drift(self) -> None:
        typed = copy.deepcopy(self.typed)
        claim_id = "SC-PKC-M16-FROZEN-PROJECTIVE-WITNESS-RESULT"
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
        claim["evidence_path"] = "wrong/artifact.json"
        claim["statement"] = "An affine approximation was sampled."
        claim["boundary"] = "The route is priced, executable, and promoted."
        problems = self.validate(typed=typed)
        self.assertIn(
            "M16 cell must retain its frozen projective witness kernel "
            "certificate",
            problems,
        )
        self.assertIn(
            "M16 cost quantity must retain its frozen projective witness "
            "kernel certificate",
            problems,
        )
        self.assertIn(
            "M16 complete-cost barrier must retain its frozen projective "
            "witness kernel certificate",
            problems,
        )
        self.assertIn(
            "M16 frozen projective witness artifact hash drifted",
            problems,
        )
        self.assertIn(
            "M16 frozen projective witness evidence path drifted",
            problems,
        )
        for boundary in (
            "exact output homogeneity",
            "projective evaluation bridges",
            "explicit coefficient map",
            "minimal witness chain",
            "C16 stage",
            "fourteen intermediate slots",
            "projective infinity",
            "zero-pair exclusion",
            "kernel-bound non-run assurance",
            "target-field scope",
            "no base-field descent",
            "no direct-S17 claim",
            "partial cost quantity",
            "unpriced cost boundary",
            "zero retention",
            "no-authorization boundary",
            "no-promotion boundary",
        ):
            self.assertTrue(
                any(
                    "M16 frozen projective witness claim must retain"
                    in problem
                    and boundary in problem
                    for problem in problems
                )
            )

    def test_m16_guarded_projective_system_cannot_drift(self) -> None:
        typed = copy.deepcopy(self.typed)
        claim_id = "SC-PKC-M16-GUARDED-PROJECTIVE-SYSTEM-RESULT"
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
        claim["evidence_path"] = "wrong/artifact.json"
        claim["statement"] = "An affine sample was generated."
        claim["boundary"] = "The route is priced, executable, and promoted."
        problems = self.validate(typed=typed)
        self.assertIn(
            "M16 cell must retain its guarded projective-system kernel "
            "certificate",
            problems,
        )
        self.assertIn(
            "M16 cost quantity must retain its guarded projective-system "
            "kernel certificate",
            problems,
        )
        self.assertIn(
            "M16 complete-cost barrier must retain its guarded "
            "projective-system kernel certificate",
            problems,
        )
        self.assertIn(
            "M16 guarded projective-system artifact hash binding drifted",
            problems,
        )
        self.assertIn(
            "M16 guarded projective-system evidence path drifted",
            problems,
        )
        for boundary in (
            "exact finite family",
            "frozen stage-14 scope",
            "injective coefficient map",
            "source-field scope",
            "target-field scope",
            "one GuardVar assignment",
            "every guarded equation",
            "literal polynomial evaluation",
            "raw slot coordinates",
            "fourteen witness slots",
            "raw variable count",
            "literal H-equation count",
            "guard count",
            "raw equation-family count",
            "degree upper bound",
            "zero-pair exclusion",
            "projective infinity",
            "kernel-bound non-run assurance",
            "source independence",
            "calibration",
            "no parallel recursive syntax",
            "no base-field descent",
            "raw-count boundary",
            "no-independence boundary",
            "degree-bound scope",
            "native-decide disclosure",
            "compiler-trust marker",
            "open non-executable cell",
            "partial cost",
            "unpriced costs",
            "no direct-S17 claim",
            "no solver input or run",
            "no chart or gauge reduction",
            "no relation independence",
            "no recovery or total cost",
            "no hypothesis retention",
            "no exact-target search",
            "no experiment authorization",
            "no route promotion",
            "zero retention",
        ):
            self.assertTrue(
                any(
                    "M16 guarded projective-system claim must retain"
                    in problem
                    and boundary in problem
                    for problem in problems
                )
            )

    def test_m16_exact_chart_cover_cannot_drift(self) -> None:
        typed = copy.deepcopy(self.typed)
        claim_id = "SC-PKC-M16-EXACT-CHART-COVER-RESULT"
        cell = next(
            item
            for item in typed["cells"]
            if item["cell_id"] == "CELL-M-PKC-SMOOTH-M16"
        )
        cell["source_claim_ids"].remove(claim_id)
        cell["cost_quantity"]["source_claim_ids"].remove(claim_id)
        cell["relation_action"] = "The chart theorem is still pending."
        cell["boundary"] = "The route is executable and priced."
        barrier = next(
            item
            for item in typed["barriers"]
            if item["id"] == "B-PKC-M16-COMPLETE-COST-BRIDGE"
        )
        barrier["source_claim_ids"].remove(claim_id)
        barrier["exact_scope"] = "The guarded system is solver-ready."
        barrier["reopening_conditions"] = [
            "Enumerate every mask and launch a solver."
        ]
        claim = next(
            item
            for item in typed["source_claims"]
            if item["id"] == claim_id
        )
        claim["artifact_sha256"] = "0" * 64
        claim["evidence_path"] = "wrong/artifact.json"
        claim["statement"] = "One affine mask was sampled."
        claim["boundary"] = "The route is priced, executable, and promoted."
        problems = self.validate(typed=typed)
        self.assertIn(
            "M16 cell must retain its exact chart-cover kernel certificate",
            problems,
        )
        self.assertIn(
            "M16 cost quantity must retain its exact chart-cover "
            "kernel certificate",
            problems,
        )
        self.assertIn(
            "M16 complete-cost barrier must retain its exact chart-cover "
            "kernel certificate",
            problems,
        )
        self.assertIn(
            "M16 exact chart-cover artifact hash binding drifted",
            problems,
        )
        self.assertIn(
            "M16 exact chart-cover evidence path drifted",
            problems,
        )
        for boundary in (
            "exact chart cover",
            "frozen stage-14 scope",
            "injective coefficient map",
            "source-field scope",
            "target-field scope",
            "infinity-mask type",
            "projective infinity",
            "affine representative",
            "fixed-mask variable count",
            "fixed-mask equation count",
            "base family",
            "step family",
            "final family",
            "endpoint degree ceiling",
            "internal degree ceiling",
            "projective-chain equivalence",
            "guarded-system equivalence",
            "zero-pair exclusion",
            "kernel-bound non-run assurance",
            "source independence",
            "calibration",
            "no base-field descent",
            "no mask sweep",
            "representation-count boundary",
            "no-independence boundary",
            "degree-bound scope",
            "native trust",
            "compiler-trust marker",
            "ordinary variable-count proof",
            "open non-executable cell",
            "partial cost",
            "unpriced costs",
            "no direct-S17 claim",
            "no production mask sweep",
            "no solver input or run",
            "no relation independence",
            "no recovery or total cost",
            "no hypothesis retention",
            "no exact-target search",
            "no experiment authorization",
            "no route rejection",
            "no route promotion",
            "zero retention",
        ):
            self.assertTrue(
                any(
                    "M16 exact chart-cover claim must retain" in problem
                    and boundary in problem
                    for problem in problems
                )
            )
        for boundary in (
            "TASK-023 chart-cover result",
            "exact chart-cover representation",
            "fixed-mask variable count",
            "fixed-mask equation count",
            "family degree ceilings",
            "no production mask enumeration",
            "TASK-024 infinity-stratum result",
            "necessary mask pruning",
            "separated mask reduction",
            "conditional interior mask count",
            "necessity-only boundary",
            "TASK-025 propagation result",
            "distance-two propagated count",
            "distance-three propagated count",
            "combined propagated count",
            "independent boundary-only count",
            "balanced obstruction split",
            "conditional single-chart result",
            "source-stage algebraic-closure boundary",
            "mapped-target regularity boundary",
            "conditional-locus boundary",
            "remaining regular-locus blocker",
        ):
            self.assertIn(
                f"M16 complete-cost barrier must retain {boundary}",
                problems,
            )
        for boundary in (
            "TASK-023 chart-cover result",
            "fixed-mask variable count",
            "chart degree ceilings",
            "TASK-024 infinity-stratum result",
            "separated mask reduction",
            "conditional interior mask count",
            "TASK-025 propagation result",
            "nested local mask counts",
            "independent boundary-only count",
            "base-field propagation",
            "balanced regularity",
            "conditional single-chart result",
            "source-stage field boundary",
            "mapped-target regularity boundary",
            "open regular-locus blocker",
            "open exceptional-complement blocker",
            "exact chart-cover result",
            "no production mask enumeration",
            "exact infinity-stratum result",
            "exact propagation result",
            "no witness-uniqueness overclaim",
            "conditional regular-locus boundary",
            "no genericity overclaim",
            "no raw-count independence overclaim",
        ):
            self.assertIn(f"M16 cell must retain {boundary}", problems)

    def test_m16_infinity_strata_cannot_drift(self) -> None:
        typed = copy.deepcopy(self.typed)
        claim_id = "SC-PKC-M16-INFINITY-STRATA-RESULT"
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
        claim["evidence_path"] = "wrong/artifact.json"
        claim["statement"] = "One infinity mask was sampled."
        claim["boundary"] = "The filter is sufficient and authorizes a solver."
        problems = self.validate(typed=typed)
        self.assertIn(
            "M16 cell must retain its infinity-stratum kernel certificate",
            problems,
        )
        self.assertIn(
            "M16 cost quantity must retain its infinity-stratum "
            "kernel certificate",
            problems,
        )
        self.assertIn(
            "M16 complete-cost barrier must retain its infinity-stratum "
            "kernel certificate",
            problems,
        )
        self.assertIn(
            "M16 infinity-stratum artifact hash binding drifted",
            problems,
        )
        self.assertIn(
            "M16 infinity-stratum evidence path drifted",
            problems,
        )
        for boundary in (
            "upstream exact chart cover",
            "local infinity identities",
            "double-infinity identity",
            "affine-input assumption",
            "separation necessity",
            "endpoint conditions",
            "forced-neighbor coordinate",
            "necessary mask predicate",
            "full logical mask count",
            "separated mask count",
            "endpoint assumptions",
            "interior mask count",
            "kernel-bound assurance",
            "source independence",
            "calibration",
            "affine-input scope",
            "conditional endpoint scope",
            "necessity boundary",
            "no production enumeration",
            "logical-count boundary",
            "full-count trust disclosure",
            "separated-count trust disclosure",
            "interior-count trust disclosure",
            "native trust",
            "compiler-trust marker",
            "open non-executable cell",
            "partial cost",
            "remaining mask blocker",
            "no sufficiency overclaim",
            "no solver input or run",
            "no relation independence",
            "no recovery or total cost",
            "no hypothesis retention",
            "no exact-target search",
            "no experiment authorization",
            "no route rejection",
            "no route promotion",
            "zero retention",
        ):
            self.assertTrue(
                any(
                    "M16 infinity-stratum claim must retain" in problem
                    and boundary in problem
                    for problem in problems
                )
            )

    def test_m16_infinity_propagation_cannot_drift(self) -> None:
        typed = copy.deepcopy(self.typed)
        claim_id = "SC-PKC-M16-INFINITY-PROPAGATION-RESULT"
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
        claim["evidence_path"] = "wrong/artifact.json"
        claim["statement"] = (
            "The 60 masks are the distance-three family and one chart is unique."
        )
        claim["boundary"] = (
            "The regular locus is generic, source regularity transfers "
            "automatically, and a solver is authorized."
        )
        problems = self.validate(typed=typed)
        self.assertIn(
            "M16 cell must retain its infinity-propagation kernel certificate",
            problems,
        )
        self.assertIn(
            "M16 cost quantity must retain its infinity-propagation "
            "kernel certificate",
            problems,
        )
        self.assertIn(
            "M16 complete-cost barrier must retain its infinity-propagation "
            "kernel certificate",
            problems,
        )
        self.assertIn(
            "M16 infinity-propagation artifact hash binding drifted",
            problems,
        )
        self.assertIn(
            "M16 infinity-propagation evidence path drifted",
            problems,
        )
        for boundary in (
            "upstream propagation scope",
            "distance-two count",
            "distance-three obstruction",
            "distance-three count",
            "combined boundary count",
            "boundary-only count",
            "count-branch separation",
            "projective-chain premise",
            "base-field propagation",
            "balanced obstruction split",
            "balanced stage ceiling",
            "balanced regularity",
            "empty-mask conclusion",
            "single-chart conclusion",
            "source-stage injective map",
            "source-stage target field",
            "mapped-target regularity location",
            "kernel-bound assurance",
            "source independence",
            "calibration",
            "distance-two trust disclosure",
            "distance-three trust disclosure",
            "boundary-only trust disclosure",
            "combined-boundary trust disclosure",
            "native trust",
            "compiler-trust marker",
            "base-field scope",
            "source-stage field boundary",
            "mapped-target assumption",
            "no automatic regularity transfer",
            "no symbolic-nonzero overclaim",
            "no nonempty-locus overclaim",
            "no generic-locus overclaim",
            "no uniqueness overclaim",
            "no target-witness descent",
            "no production enumeration",
            "open non-executable cell",
            "partial cost",
            "no relation independence",
            "no yield claim",
            "no rank claim",
            "no solver input or run",
            "no complexity overclaim",
            "no hypothesis retention",
            "no experiment authorization",
            "no route rejection",
            "no route promotion",
            "zero retention",
        ):
            self.assertTrue(
                any(
                    "M16 infinity-propagation claim must retain" in problem
                    and boundary in problem
                    for problem in problems
                )
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

    def test_phase_cannot_reopen_sanitation_or_native_exploration(self) -> None:
        decisions = copy.deepcopy(self.decisions)
        decisions["phase_policy"]["phase"] = "research-engine-v0.2-sanitation"
        decisions["phase_policy"]["bounded_exploration_authorized"] = True
        decisions["maintenance_cycle"]["status"] = "active_remediation_draft"
        problems = self.validate(decisions=decisions)
        self.assertIn(
            "current phase must be post-task026-decision-review",
            problems,
        )
        self.assertIn(
            "native decision bounded exploration must remain unauthorized",
            problems,
        )
        self.assertIn("TASK-010 maintenance cycle boundary drifted", problems)

    def test_singleton_cannot_drift_or_authorize_promotion(self) -> None:
        decisions = copy.deepcopy(self.decisions)
        authorization = decisions["bounded_experiment_authorization"]
        authorization["scope"]["secp256k1_targets_forbidden"] = False
        authorization["resource_budget"]["max_primary_trials"] += 1
        authorization["sha256_bindings"]["run_py"] = "0" * 64
        authorization["promotion_authorized"] = True
        decisions["phase_policy"]["promotion_experiments_authorized"] = True
        problems = self.validate(decisions=decisions)
        self.assertIn(
            "bounded experiment authorization scope drifted", problems
        )
        self.assertIn(
            "bounded experiment authorization resource_budget drifted",
            problems,
        )
        self.assertIn(
            "bounded experiment authorization sha256_bindings drifted",
            problems,
        )
        self.assertIn(
            "bounded experiment authorization promotion_authorized drifted",
            problems,
        )
        self.assertIn(
            "decision promotion must remain unauthorized", problems
        )

    def test_singleton_route_must_match_typed_cell_parent(self) -> None:
        typed = copy.deepcopy(self.typed)
        cell = next(
            item
            for item in typed["cells"]
            if item["cell_id"] == "CELL-M-PKC-SMOOTH-M16"
        )
        cell["route_id"] = "R-GLV-SEMAEV"
        problems = self.validate(typed=typed)
        self.assertIn(
            "bounded experiment authorization route must match its canonical "
            "typed-evidence cell route",
            problems,
        )

    def test_singleton_does_not_open_native_route_claim_or_lifecycle_gates(
        self,
    ) -> None:
        decisions = copy.deepcopy(self.decisions)
        route = next(
            item
            for item in decisions["routes"]
            if item["id"] == "R-GLV-SEMAEV"
        )
        route["authorized_experiment"] = True
        claims = copy.deepcopy(self.claims)
        claims["authorization"]["experiments"] = 1
        lifecycle = copy.deepcopy(self.lifecycle)
        lifecycle["authorization"]["experiments"] = 1
        engine = copy.deepcopy(self.engine)
        engine["counts"]["selected_explorations"] = 1
        problems = self.validate(
            decisions=decisions,
            claims=claims,
            lifecycle=lifecycle,
            engine=engine,
        )
        self.assertIn(
            "no route may inherit the decision-level authorization", problems
        )
        self.assertIn("claim state authorization boundary drifted", problems)
        self.assertIn(
            "v0.2 lifecycle authorization boundary drifted", problems
        )
        self.assertTrue(
            any(
                "selected_explorations" in problem for problem in problems
            )
        )


if __name__ == "__main__":
    unittest.main()
