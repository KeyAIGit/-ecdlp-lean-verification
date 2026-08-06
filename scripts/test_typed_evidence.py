#!/usr/bin/env python3
"""Regression fixtures for the typed evidence and desk-decision layer."""
from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from typed_evidence_lib import (
    DECISIONS_PATH,
    DESK_DECISIONS_DIR,
    POLICY_PATH,
    SOURCE_REGISTRY_PATH,
    build_state,
    load_json,
    load_records,
    sha256_file,
)


class TypedEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy = load_json(POLICY_PATH)
        cls.decisions = load_json(DECISIONS_PATH)
        cls.source_registry = load_json(SOURCE_REGISTRY_PATH)
        cls.desk_records = load_records(DESK_DECISIONS_DIR)

    def build(
        self,
        *,
        policy: dict | None = None,
        desk_records: list | None = None,
    ) -> tuple[list[str], dict]:
        return build_state(
            policy or copy.deepcopy(self.policy),
            copy.deepcopy(self.decisions),
            copy.deepcopy(self.source_registry),
            desk_records
            if desk_records is not None
            else copy.deepcopy(self.desk_records),
        )

    def test_text_artifact_hash_is_line_ending_independent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            lf = root / "lf.json"
            crlf = root / "crlf.json"
            lf.write_bytes(b'{\n  "value": 1\n}\n')
            crlf.write_bytes(b'{\r\n  "value": 1\r\n}\r\n')
            self.assertEqual(sha256_file(lf), sha256_file(crlf))

    def test_canonical_state_is_valid_and_non_authorizing(self) -> None:
        problems, state = self.build()
        self.assertEqual([], problems)
        self.assertEqual(
            {
                "source_claims": 36,
                "target_properties": 11,
                "mechanisms": 8,
                "cells": 8,
                "open_cells": 3,
                "property_resolution_cells": 1,
                "decided_inapplicable_cells": 3,
                "decided_closed_cells": 1,
                "seed_eligible_cells": 2,
                "desk_decisions": 4,
            },
            state["counts"],
        )
        self.assertTrue(
            all(cell["authorization"] == "none" for cell in state["cells"])
        )
        self.assertTrue(
            all(
                decision["authorization"] == "none"
                for decision in state["desk_decisions"]
            )
        )

    def test_smooth_divisor_property_preserves_independent_replay(self) -> None:
        property_record = next(
            item
            for item in self.policy["target_properties"]
            if item["id"] == "TP-SECP-PMINUS1-SMOOTH-DIVISOR"
        )
        self.assertEqual("kernel_verified", property_record["status"])
        self.assertIn(
            "SC-SECP-PMINUS1-SMOOTH-DIVISOR-CEILING",
            property_record["source_claim_ids"],
        )
        self.assertIn(
            "SC-SECP-PMINUS1-FACTORIZATION",
            property_record["source_claim_ids"],
        )
        claims = {
            item["id"]: item for item in self.policy["source_claims"]
        }
        self.assertEqual(
            "kernel_verified",
            claims["SC-SECP-PMINUS1-SMOOTH-DIVISOR-CEILING"]["read_status"],
        )
        self.assertEqual(
            "certificate_replayed",
            claims["SC-SECP-PMINUS1-FACTORIZATION"]["read_status"],
        )

    def test_m16_census_is_exact_but_does_not_rewrite_the_open_cell(self) -> None:
        problems, state = self.build()
        self.assertEqual([], problems)
        properties = {
            item["id"]: item for item in self.policy["target_properties"]
        }
        expected = {
            "TP-SECP-PKC-M16-CHARACTER-SUM": 2532,
            "TP-SECP-PKC-M16-LIFTABLE-X": 283527,
            "TP-SECP-PKC-M16-SIGNED-POINTS": 567054,
            "TP-SECP-PKC-M16-GLV-ORBIT-CLASSES": 94509,
            "TP-SECP-PKC-M16-ZERO-RHS-X": 0,
        }
        for property_id, value in expected.items():
            self.assertEqual(value, properties[property_id]["value"])
            self.assertEqual(
                "certificate_replayed", properties[property_id]["status"]
            )
        cell = next(
            item
            for item in state["cells"]
            if item["cell_id"] == "CELL-M-PKC-SMOOTH-M16"
        )
        self.assertEqual("open", cell["status"])
        self.assertTrue(cell["seed_eligible"])
        self.assertIn(
            "SC-PKC-M16-SECP-FACTOR-BASE-CENSUS",
            cell["source_claim_ids"],
        )

    def test_evidence_file_hash_is_recomputed(self) -> None:
        policy = copy.deepcopy(self.policy)
        claim = next(
            item
            for item in policy["source_claims"]
            if item["id"] == "SC-GLV-SEMAEV-CLASSIFICATION"
        )
        claim["artifact_sha256"] = "0" * 64
        problems, _ = self.build(policy=policy)
        self.assertTrue(
            any("does not match evidence_path" in item for item in problems)
        )

    def test_kernel_locator_must_exist_in_the_bound_file(self) -> None:
        policy = copy.deepcopy(self.policy)
        claim = next(
            item
            for item in policy["source_claims"]
            if item["id"] == "SC-SECP-NO-TWO-TORSION"
        )
        claim["locator"]["value"] = "not_a_real_theorem"
        problems, _ = self.build(policy=policy)
        self.assertTrue(
            any("locator theorem is absent" in item for item in problems)
        )

    def test_full_text_claim_requires_a_bound_extract(self) -> None:
        policy = copy.deepcopy(self.policy)
        claim = next(
            item
            for item in policy["source_claims"]
            if item["id"] == "SC-FHJRV-TORSION-ACTION"
        )
        claim["evidence_path"] = None
        problems, _ = self.build(policy=policy)
        self.assertTrue(
            any("claim-extract evidence_path" in item for item in problems)
        )

    def test_primary_source_hash_and_locator_are_bound_to_extract(self) -> None:
        policy = copy.deepcopy(self.policy)
        claim = next(
            item
            for item in policy["source_claims"]
            if item["id"] == "SC-PKC-SMOOTH-SUBGROUP"
        )
        claim["artifact_sha256"] = "0" * 64
        claim["locator"]["value"] = "Section 1"
        problems, _ = self.build(policy=policy)
        self.assertTrue(
            any("source artifact hash differs" in item for item in problems)
        )
        self.assertTrue(any("locator differs" in item for item in problems))

    def test_metadata_only_claim_cannot_decide_a_property(self) -> None:
        policy = copy.deepcopy(self.policy)
        claim = next(
            item
            for item in policy["source_claims"]
            if item["id"] == "SC-AMADORI-PRIME-FIELD-VARIANT"
        )
        claim["read_status"] = "metadata_only"
        prop = next(
            item
            for item in policy["target_properties"]
            if item["id"] == "TP-SECP-PRIME-FIELD-COORDINATES"
        )
        prop["source_claim_ids"] = ["SC-AMADORI-PRIME-FIELD-VARIANT"]
        problems, _ = self.build(policy=policy)
        self.assertTrue(
            any("uses non-decisive source claims" in item for item in problems)
        )

    def test_unread_source_registry_status_blocks_full_text_claim(self) -> None:
        policy = copy.deepcopy(self.policy)
        claim = copy.deepcopy(
            next(
                item
                for item in policy["source_claims"]
                if item["id"] == "SC-AMADORI-PRIME-FIELD-VARIANT"
            )
        )
        claim["id"] = "SC-KUDO-CONTRADICTION-FIXTURE"
        claim["source_id"] = "kudo_yokota_takahashi_yasuda2018"
        claim["read_status"] = "full_text_obtained"
        policy["source_claims"].append(claim)
        problems, _ = self.build(policy=policy)
        self.assertTrue(
            any(
                "contradicts source registry full_text_unread" in item
                for item in problems
            )
        )

    def test_inspected_source_registry_requires_a_full_text_claim(self) -> None:
        policy = copy.deepcopy(self.policy)
        claim = next(
            item
            for item in policy["source_claims"]
            if item["id"] == "SC-AMADORI-PRIME-FIELD-VARIANT"
        )
        claim["read_status"] = "metadata_only"
        claim["artifact_sha256"] = None
        claim["locator"] = {
            "kind": "section",
            "value": "Bibliographic record and abstract only",
        }
        claim["evidence_path"] = None
        problems, _ = self.build(policy=policy)
        self.assertTrue(
            any(
                "full_text_inspected but its typed evidence has no "
                "full_text_obtained claim" in item
                for item in problems
            )
        )

    def test_false_target_property_blocks_only_the_bound_mechanism(self) -> None:
        problems, state = self.build()
        self.assertEqual([], problems)
        cells = {item["cell_id"]: item for item in state["cells"]}
        self.assertEqual(
            "decided_inapplicable",
            cells["CELL-M-FHJRV-DIRECT-TWO-TORSION"]["status"],
        )
        self.assertFalse(
            cells["CELL-M-FHJRV-DIRECT-TWO-TORSION"]["seed_eligible"]
        )
        self.assertEqual(
            "open",
            cells["CELL-M-GLV-FAITHFUL-PHASE-QUOTIENT"]["status"],
        )
        self.assertFalse(
            cells["CELL-M-GLV-FAITHFUL-PHASE-QUOTIENT"]["seed_eligible"]
        )

    def test_desired_properties_are_not_treated_as_mechanisms(self) -> None:
        problems, state = self.build()
        self.assertEqual([], problems)
        cells = {item["cell_id"]: item for item in state["cells"]}
        self.assertFalse(
            cells["CELL-M-GLV-FAITHFUL-PHASE-QUOTIENT"]["seed_eligible"]
        )
        self.assertFalse(
            cells["CELL-M-PRIME-FIELD-SEMAEV-ENDTOEND"]["seed_eligible"]
        )

    def test_m16_symbolic_blocker_keeps_cell_open_and_non_authorizing(
        self,
    ) -> None:
        problems, state = self.build()
        self.assertEqual([], problems)
        cells = {item["cell_id"]: item for item in state["cells"]}
        self.assertEqual(
            "decided_inapplicable", cells["CELL-M-PKC-SMOOTH-M4"]["status"]
        )
        m16 = cells["CELL-M-PKC-SMOOTH-M16"]
        self.assertEqual("open", m16["status"])
        self.assertTrue(m16["seed_eligible"])
        self.assertEqual("none", m16["authorization"])
        self.assertEqual("partial", m16["cost_quantity_status"])
        self.assertEqual(
            ["B-PKC-M16-COMPLETE-COST-BRIDGE"], m16["barrier_ids"]
        )
        for claim_id in (
            "SC-PKC-SYSTEM4-EXACT",
            "SC-PKC-PMINUS1-MAP-EXACT",
            "SC-PKC-PARTIAL-COST-EXACT",
            "SC-PKC-M16-SOURCE-MECHANISM-RECOVERY",
        ):
            self.assertIn(claim_id, m16["source_claim_ids"])
            self.assertIn(claim_id, m16["cost_quantity"]["source_claim_ids"])
        self.assertIn(
            "SC-PKC-M16-SYMBOLIC-DESK-RESULT",
            m16["source_claim_ids"],
        )
        self.assertIn(
            "SC-PKC-M16-SEMANTIC-BRIDGE-RESULT",
            m16["source_claim_ids"],
        )
        self.assertIn(
            "SC-PKC-M16-SEMANTIC-BRIDGE-RESULT",
            m16["cost_quantity"]["source_claim_ids"],
        )
        self.assertIn(
            "SC-PKC-M16-EXCEPTIONAL-FIBER-RESULT",
            m16["source_claim_ids"],
        )
        self.assertIn(
            "SC-PKC-M16-EXCEPTIONAL-FIBER-RESULT",
            m16["cost_quantity"]["source_claim_ids"],
        )
        self.assertIn(
            "SC-PKC-M16-PROJECTIVE-S17-BRIDGE-RESULT",
            m16["source_claim_ids"],
        )
        self.assertIn(
            "SC-PKC-M16-PROJECTIVE-S17-BRIDGE-RESULT",
            m16["cost_quantity"]["source_claim_ids"],
        )
        self.assertIn(
            "SC-PKC-M16-PROJECTIVE-RESULTANT-KERNEL-RESULT",
            m16["source_claim_ids"],
        )
        self.assertIn(
            "SC-PKC-M16-PROJECTIVE-RESULTANT-KERNEL-RESULT",
            m16["cost_quantity"]["source_claim_ids"],
        )
        self.assertIn(
            "SC-PKC-M16-FROZEN-CR-SPECIALIZATION-RESULT",
            m16["source_claim_ids"],
        )
        self.assertIn(
            "SC-PKC-M16-FROZEN-CR-SPECIALIZATION-RESULT",
            m16["cost_quantity"]["source_claim_ids"],
        )
        self.assertIn(
            "SC-PKC-M16-FROZEN-PROJECTIVE-WITNESS-RESULT",
            m16["source_claim_ids"],
        )
        self.assertIn(
            "SC-PKC-M16-FROZEN-PROJECTIVE-WITNESS-RESULT",
            m16["cost_quantity"]["source_claim_ids"],
        )
        self.assertIn(
            "SC-PKC-M16-GUARDED-PROJECTIVE-SYSTEM-RESULT",
            m16["source_claim_ids"],
        )
        self.assertIn(
            "SC-PKC-M16-GUARDED-PROJECTIVE-SYSTEM-RESULT",
            m16["cost_quantity"]["source_claim_ids"],
        )
        self.assertIn(
            "SC-PKC-M16-EXACT-CHART-COVER-RESULT",
            m16["source_claim_ids"],
        )
        self.assertIn(
            "SC-PKC-M16-EXACT-CHART-COVER-RESULT",
            m16["cost_quantity"]["source_claim_ids"],
        )
        self.assertIn(
            "SC-PKC-M16-INFINITY-STRATA-RESULT",
            m16["source_claim_ids"],
        )
        self.assertIn(
            "SC-PKC-M16-INFINITY-STRATA-RESULT",
            m16["cost_quantity"]["source_claim_ids"],
        )
        self.assertIn(
            "SC-PKC-M16-INFINITY-PROPAGATION-RESULT",
            m16["source_claim_ids"],
        )
        self.assertIn(
            "SC-PKC-M16-INFINITY-PROPAGATION-RESULT",
            m16["cost_quantity"]["source_claim_ids"],
        )
        self.assertFalse(
            any(
                decision["cell_id"] == "CELL-M-PKC-SMOOTH-M16"
                for decision in state["desk_decisions"]
            )
        )
        claims = {
            item["id"]: item for item in state["source_claims"]
        }
        source_mechanism_claim = claims[
            "SC-PKC-M16-SOURCE-MECHANISM-RECOVERY"
        ]
        self.assertEqual(
            "experiments/engine/"
            "pkc_smooth_m16_source_faithful_mechanism/artifact.json",
            source_mechanism_claim["evidence_path"],
        )
        self.assertEqual(
            "79ee65104cfbd45ee902fbf59524a705e6db8590c8d5845a6a20cd63239c774c",
            source_mechanism_claim["artifact_sha256"],
        )
        self.assertIn("repository completion", source_mechanism_claim["boundary"])
        self.assertIn("source independence is not established", source_mechanism_claim["boundary"])
        self.assertIn("no solver", source_mechanism_claim["boundary"])
        self.assertEqual(
            "experiments/engine/pkc_smooth_m16_symbolic_desk/artifact.json",
            claims["SC-PKC-M16-SYMBOLIC-DESK-RESULT"]["evidence_path"],
        )
        semantic_claim = claims["SC-PKC-M16-SEMANTIC-BRIDGE-RESULT"]
        self.assertEqual(
            "experiments/engine/pkc_smooth_m16_semantic_bridge/artifact.json",
            semantic_claim["evidence_path"],
        )
        self.assertEqual(
            "963eea60097807ae0aa66a5d881b0c34bf0497ade53ed4d37d38861a73887c19",
            semantic_claim["artifact_sha256"],
        )
        exceptional_claim = claims["SC-PKC-M16-EXCEPTIONAL-FIBER-RESULT"]
        self.assertEqual(
            "experiments/engine/pkc_smooth_m16_exceptional_fibers/artifact.json",
            exceptional_claim["evidence_path"],
        )
        self.assertEqual(
            "578db732807a452e26de03dcd338d62c25a7d90490a62bbf427b1f96c3a869cf",
            exceptional_claim["artifact_sha256"],
        )
        self.assertEqual(
            "certificate_replayed",
            exceptional_claim["read_status"],
        )
        self.assertIn(
            "characteristic not in {2,3,7}",
            exceptional_claim["statement"],
        )
        self.assertIn(
            "source_independence is not_established",
            exceptional_claim["boundary"],
        )
        self.assertIn(
            "calibration is excluded_nonexperimental",
            exceptional_claim["boundary"],
        )
        self.assertIn(
            "solving cost is unpriced",
            exceptional_claim["boundary"],
        )
        projective_claim = claims[
            "SC-PKC-M16-PROJECTIVE-S17-BRIDGE-RESULT"
        ]
        self.assertEqual(
            "experiments/engine/pkc_smooth_m16_projective_bridge/artifact.json",
            projective_claim["evidence_path"],
        )
        self.assertEqual(
            "3164cb89adac7622b4d08d781061ea386dc64e754236e48c838a3dac23040715",
            projective_claim["artifact_sha256"],
        )
        self.assertEqual(
            "certificate_replayed",
            projective_claim["read_status"],
        )
        self.assertIn(
            "recursive projective S17",
            projective_claim["statement"],
        )
        self.assertIn(
            "fixed-degree",
            projective_claim["statement"],
        )
        self.assertIn(
            "reverse projection",
            projective_claim["statement"],
        )
        self.assertIn(
            "source_independence is not_established",
            projective_claim["boundary"],
        )
        self.assertIn(
            "calibration is excluded_nonexperimental",
            projective_claim["boundary"],
        )
        self.assertIn(
            "rank is unpriced",
            projective_claim["boundary"],
        )
        self.assertIn(
            "yield is unpriced",
            projective_claim["boundary"],
        )
        self.assertIn(
            "no experiment authorization",
            projective_claim["boundary"],
        )
        resultant_claim = claims[
            "SC-PKC-M16-PROJECTIVE-RESULTANT-KERNEL-RESULT"
        ]
        self.assertEqual(
            "experiments/engine/"
            "pkc_smooth_m16_projective_resultant_kernel/artifact.json",
            resultant_claim["evidence_path"],
        )
        self.assertEqual(
            "0b9d8b48953aae2defa28ade67992084"
            "cecca3a01b43490bc338a0fd5ce97c5a",
            resultant_claim["artifact_sha256"],
        )
        self.assertEqual(
            "certificate_replayed",
            resultant_claim["read_status"],
        )
        for token in (
            "fixed-degree resultant",
            "literal TASK-018 Sylvester matrix",
            "coefficient unit 1",
            "zero forms",
            "output [1:0]",
        ):
            self.assertIn(token, resultant_claim["statement"])
        for token in (
            "kernel_bound_non_run_certificate",
            "source_independence is not_established",
            "calibration is excluded_nonexperimental",
            "recursive frozen C_r specialization",
            "formal degrees (2^(r-2),2)",
            "universal C16-to-C2 induction",
            "open_exact_blocker",
            "solving cost is unpriced",
            "rank is unpriced",
            "yield is unpriced",
            "zero_retention_success",
            "experiment authorization",
            "route promotion",
        ):
            self.assertIn(token, resultant_claim["boundary"])
        frozen_cr_claim = claims[
            "SC-PKC-M16-FROZEN-CR-SPECIALIZATION-RESULT"
        ]
        self.assertEqual(
            "experiments/engine/"
            "pkc_smooth_m16_frozen_cr_specialization/artifact.json",
            frozen_cr_claim["evidence_path"],
        )
        self.assertEqual(
            "d025053b9f882c88086fd5f04bcbd962"
            "7c72987e263e9b55af6024794305acbe",
            frozen_cr_claim["artifact_sha256"],
        )
        self.assertEqual(
            "certificate_replayed",
            frozen_cr_claim["read_status"],
        )
        for token in (
            "actual frozenC",
            "explicit coefficient map",
            "formal degrees (2^(s+1),2)",
            "coefficient unit 1",
            "affine output [y:1]",
            "infinity output [1:0]",
            "uniformly at most 2^(s+1)",
            "without a residual degree hypothesis",
        ):
            self.assertIn(token, frozen_cr_claim["statement"])
        for token in (
            "kernel_bound_non_run_certificate",
            "source_independence is not_established",
            "calibration is excluded_nonexperimental",
            "universal C16-to-C2 projective witness extraction",
            "full fourteen-node internal projective tree",
            "open_exact_blocker",
            "CQ-SEMAEV-S17-SYSTEM-COST remains partial",
            "solving cost is unpriced",
            "rank is unpriced",
            "yield is unpriced",
            "zero_retention_success",
            "experiment authorization",
            "route promotion",
        ):
            self.assertIn(token, frozen_cr_claim["boundary"])
        witness_claim = claims[
            "SC-PKC-M16-FROZEN-PROJECTIVE-WITNESS-RESULT"
        ]
        self.assertEqual(
            "experiments/engine/"
            "pkc_smooth_m16_frozen_projective_witness/artifact.json",
            witness_claim["evidence_path"],
        )
        self.assertEqual(
            "89c645545d89334473d51654a41ff7ec"
            "2364857d034c64ce08d505337fa1e2d4",
            witness_claim["artifact_sha256"],
        )
        self.assertEqual(
            "certificate_replayed",
            witness_claim["read_status"],
        )
        for token in (
            "declared-degree output homogeneity",
            "projective homogenization/evaluation bridges",
            "every explicit coefficient map",
            "FrozenProjectiveChain",
            "stage 14",
            "fourteen valid intermediate projective slots",
            "[1:0] is allowed",
            "[0:0] is excluded",
        ):
            self.assertIn(token, witness_claim["statement"])
        for token in (
            "kernel_bound_non_run_certificate",
            "source_independence is not_established",
            "calibration is excluded_nonexperimental",
            "algebraically closed target",
            "no descent",
            "no direct RecS17 iff GeoCat",
            "CQ-SEMAEV-S17-SYSTEM-COST remains partial",
            "solving cost, rank, and yield remain unpriced",
            "zero_retention_success",
            "experiment authorization",
            "route promotion",
        ):
            self.assertIn(token, witness_claim["boundary"])
        guarded_claim = claims[
            "SC-PKC-M16-GUARDED-PROJECTIVE-SYSTEM-RESULT"
        ]
        self.assertEqual(
            "experiments/engine/"
            "pkc_smooth_m16_guarded_projective_system/artifact.json",
            guarded_claim["evidence_path"],
        )
        self.assertEqual(
            "3445da55b44a71d0f40ee60206c90f2e"
            "f1798c28abd125542ce3acbeeb8e1d46",
            guarded_claim["artifact_sha256"],
        )
        self.assertEqual(
            "certificate_replayed",
            guarded_claim["read_status"],
        )
        for token in (
            "exact literal finite MvPolynomial family",
            "frozen stage-14 predicate",
            "injective coefficient map",
            "source Field k",
            "algebraically closed target Field K",
            "∃ assignment : GuardVar → K",
            "∀ e : GuardedEquation",
            "MvPolynomial.eval assignment",
            "Four raw scalars U,V,A,B",
            "fourteen projective witness slots",
            "56 variables",
            "fifteen literal H equations",
            "fourteen guards",
            "29 equation-family members",
            "total degree at most four",
            "exclude [0:0]",
            "retain [1:0]",
        ):
            self.assertIn(token, guarded_claim["statement"])
        for token in (
            "kernel_bound_non_run_certificate",
            "source_independence is not_established",
            "calibration is excluded_nonexperimental",
            "not a parallel recursive syntax",
            "no base-field descent",
            "raw representation counts",
            "not independent dimensions or relations",
            "upper bound, not an exact-degree claim",
            "compiler_trusted_native_decide",
            "Lean.ofReduceBool",
            "open_non_executable",
            "CQ-SEMAEV-S17-SYSTEM-COST remains partial",
            "solving cost, rank, and yield remain unpriced",
            "no expanded direct S17 polynomial",
            "solver input or run",
            "chart/gauge reduction",
            "relation independence",
            "recovery or total-cost result",
            "hypothesis retention",
            "exact-target search",
            "experiment authorization",
            "route promotion",
            "zero_retention_success",
        ):
            self.assertIn(token, guarded_claim["boundary"])
        chart_claim = claims["SC-PKC-M16-EXACT-CHART-COVER-RESULT"]
        self.assertEqual(
            "experiments/engine/"
            "pkc_smooth_m16_exact_chart_cover/artifact.json",
            chart_claim["evidence_path"],
        )
        self.assertEqual(
            "934809fabbb8c98c5ed9356a0a1f3367"
            "a23f8fbc1bc86239069942537fd678ed",
            chart_claim["artifact_sha256"],
        )
        self.assertEqual(
            "certificate_replayed",
            chart_claim["read_status"],
        )
        for token in (
            "exact affine/infinity chart-polynomial cover",
            "frozen stage-14 predicate",
            "injective coefficient map",
            "source Field k",
            "algebraically closed target Field K",
            "InfinityMask : Finset (Fin 14)",
            "[1:0]",
            "[X_i:1]",
            "14 - I.card variables",
            "exactly fifteen literal H equations",
            "one base equation",
            "thirteen internal step equations",
            "one final equation",
            "degree at most two",
            "degree at most four",
            "FrozenProjectiveChain",
            "prior guarded projective system",
            "never introduces [0:0]",
        ):
            self.assertIn(token, chart_claim["statement"])
        for token in (
            "kernel_bound_non_run_certificate",
            "source_independence is not_established",
            "calibration is excluded_nonexperimental",
            "no base-field descent",
            "2^14 logical masks are not enumerated or materialized",
            "representation inventory",
            "not independent dimensions or relations",
            "upper bounds rather than exact-degree claims",
            "card_chartEquation is compiler_trusted_native_decide",
            "Lean.ofReduceBool",
            "card_chartVar",
            "open_non_executable",
            "CQ-SEMAEV-S17-SYSTEM-COST remains partial",
            "solving cost, rank, and yield remain unpriced",
            "no expanded direct S17 polynomial",
            "production mask sweep",
            "solver input or run",
            "relation independence",
            "recovery or total-cost result",
            "hypothesis retention",
            "exact-target search",
            "experiment authorization",
            "route rejection",
            "route promotion",
            "zero_retention_success",
        ):
            self.assertIn(token, chart_claim["boundary"])
        strata_claim = claims["SC-PKC-M16-INFINITY-STRATA-RESULT"]
        self.assertEqual(
            "experiments/engine/"
            "pkc_smooth_m16_infinity_strata/artifact.json",
            strata_claim["evidence_path"],
        )
        self.assertEqual(
            "54b0f3c5f2f1880b1f805911df21b72"
            "e5427b18871f14907ac17a1d8b48bdd39",
            strata_claim["artifact_sha256"],
        )
        self.assertEqual("certificate_replayed", strata_claim["read_status"])
        for token in (
            "TASK-023 stage-14 chart cover",
            "squared projective determinants",
            "H([1:0],b,[1:0]) = b.v^2",
            "AffineInputFamily",
            "adjacent infinity slots are impossible",
            "endpoint determinant equations",
            "q.u / q.v",
            "AdmissibleInfinityMask",
            "16384 total masks",
            "987 separated masks",
            "both endpoint determinants are nonzero",
            "377 masks",
        ):
            self.assertIn(token, strata_claim["statement"])
        for token in (
            "kernel_bound_non_run_certificate",
            "source_independence is not_established",
            "calibration is excluded_nonexperimental",
            "requires affine external inputs",
            "additionally requires both endpoint determinants",
            "necessary, not sufficient or unique",
            "not enumerated or materialized",
            "logical cover inventory",
            "card_infinityMask",
            "card_separatedInfinityMask",
            "card_interiorSeparatedInfinityMask",
            "compiler_trusted_native_decide",
            "Lean.ofReduceBool",
            "open_non_executable",
            "CQ-SEMAEV-S17-SYSTEM-COST remains partial",
            "sufficient mask orchestration",
            "no sufficient mask-selection algorithm",
            "production mask sweep",
            "solver input or run",
            "relation independence",
            "recovery or total-cost result",
            "hypothesis retention",
            "exact-target search",
            "experiment authorization",
            "route rejection",
            "route promotion",
            "zero_retention_success",
        ):
            self.assertIn(token, strata_claim["boundary"])
        propagation_claim = claims[
            "SC-PKC-M16-INFINITY-PROPAGATION-RESULT"
        ]
        self.assertEqual(
            "experiments/engine/"
            "pkc_smooth_m16_infinity_propagation/artifact.json",
            propagation_claim["evidence_path"],
        )
        self.assertEqual(
            "9330603ba1f0af9ee4902c263200709e2"
            "ec6f8c50d8d7eaab3b55bcba78e388f",
            propagation_claim["artifact_sha256"],
        )
        self.assertEqual(
            "certificate_replayed",
            propagation_claim["read_status"],
        )
        for token in (
            "TASK-025 propagation",
            "377 interior separated masks to 129",
            "nested family to 69",
            "leaves 36",
            "boundary-near obstructions to the 129-mask",
            "leaves 60",
            "60 is not the distance-three count",
            "over any Field",
            "six prefix and six suffix values",
            "maximum frozen stage five",
            "BalancedPropagatedRegular",
            "single empty-mask affine chart",
            "injective base change into an algebraically closed target",
            "mapped target inputs and target",
        ):
            self.assertIn(token, propagation_claim["statement"])
        for token in (
            "kernel_bound_non_run_certificate",
            "source_independence is not_established",
            "calibration is excluded_nonexperimental",
            "card_gapTwoInteriorInfinityMask",
            "card_gapThreeInteriorInfinityMask",
            "card_boundaryPropagatedInfinityMask",
            "card_boundaryGapThreeInfinityMask",
            "compiler_trusted_native_decide",
            "Lean.ofReduceBool",
            "require no algebraic closure",
            "source-stage bridge still requires",
            "Mapped-target balanced regularity",
            "not established automatically by source-field computation",
            "Symbolic nonzeroness, nonemptiness, density, probability, and genericity",
            "does not prove uniqueness",
            "realizability of any nonempty propagated mask",
            "descent of target witnesses",
            "not enumerated or materialized",
            "open_non_executable",
            "CQ-SEMAEV-S17-SYSTEM-COST remains partial",
            "relation independence, yield, rank, solving, recovery, and total cost",
            "no solver input or run",
            "experiment authorization",
            "route rejection",
            "route promotion",
            "zero_retention_success",
        ):
            self.assertIn(token, propagation_claim["boundary"])
        barriers = {
            item["id"]: item for item in state["barriers"]
        }
        m16_barrier = barriers["B-PKC-M16-COMPLETE-COST-BRIDGE"]
        self.assertEqual("open", m16_barrier["disposition"])
        self.assertIn(
            "SC-PKC-M16-SEMANTIC-BRIDGE-RESULT",
            m16_barrier["source_claim_ids"],
        )
        self.assertIn(
            "SC-PKC-M16-EXCEPTIONAL-FIBER-RESULT",
            m16_barrier["source_claim_ids"],
        )
        self.assertIn(
            "SC-PKC-M16-PROJECTIVE-S17-BRIDGE-RESULT",
            m16_barrier["source_claim_ids"],
        )
        self.assertIn(
            "SC-PKC-M16-PROJECTIVE-RESULTANT-KERNEL-RESULT",
            m16_barrier["source_claim_ids"],
        )
        self.assertIn(
            "SC-PKC-M16-FROZEN-CR-SPECIALIZATION-RESULT",
            m16_barrier["source_claim_ids"],
        )
        self.assertIn(
            "SC-PKC-M16-FROZEN-PROJECTIVE-WITNESS-RESULT",
            m16_barrier["source_claim_ids"],
        )
        self.assertIn(
            "SC-PKC-M16-GUARDED-PROJECTIVE-SYSTEM-RESULT",
            m16_barrier["source_claim_ids"],
        )
        self.assertIn(
            "SC-PKC-M16-EXACT-CHART-COVER-RESULT",
            m16_barrier["source_claim_ids"],
        )
        self.assertIn(
            "SC-PKC-M16-INFINITY-STRATA-RESULT",
            m16_barrier["source_claim_ids"],
        )
        self.assertIn(
            "SC-PKC-M16-INFINITY-PROPAGATION-RESULT",
            m16_barrier["source_claim_ids"],
        )
        for token in (
            "TASK-019 kernel-checks",
            "zero forms",
            "TASK-020 kernel-checks",
            "actual frozenC family",
            "formal degrees (2^(s+1),2)",
            "universal output-degree bound",
            "unconditional one-step common-projective-root equivalence",
            "TASK-021 kernel-checks",
            "all-stage frozen projective witness-chain equivalence",
            "fourteen intermediate projective slots",
            "TASK-022 kernel-checks",
            "56 scalar variables",
            "29 equation-family members",
            "total degree at most four",
            "counts do not establish dimension",
            "TASK-023 kernel-checks",
            "exact affine/infinity chart-polynomial cover",
            "14 - I.card variables",
            "fifteen H equations",
            "degree ceilings 2, 4, and 2",
            "2^14 logical masks are not enumerated or materialized",
            "TASK-024 kernel-checks",
            "necessary infinity-stratum pruning",
            "16384 masks to 987 separated masks",
            "377 interior masks",
            "necessary, not sufficient or unique",
            "TASK-025 kernel-checks",
            "377 to 129 after distance two",
            "to 69 after distance three",
            "to 36 after also excluding",
            "separate boundary-only refinement contracts 129 to 60",
            "Six prefix and six suffix",
            "single affine chart",
            "source-stage bridge still requires",
            "source-field computation does not automatically establish",
            "Symbolic nonzeroness, nonemptiness",
            "usable regular locus or orchestrating its exceptional complement",
        ):
            self.assertIn(token, m16_barrier["exact_scope"])
        self.assertNotIn(
            "pending a kernel-checked fixed-degree projective resultant "
            "common-root theorem",
            m16_barrier["exact_scope"],
        )
        self.assertNotIn(
            "open only on the exact recursive frozen C_r specialization",
            m16_barrier["exact_scope"],
        )
        reopening = " ".join(m16_barrier["reopening_conditions"])
        for token in (
            "exact TASK-023 affine/infinity chart-polynomial cover",
            "completed TASK-024 necessary infinity-stratum filter",
            "completed TASK-025 conditional single-affine-chart theorem",
            "symbolic nonzeroness and nonemptiness",
            "mapped-target balanced regular locus",
            "orchestration of its exceptional complement",
            "without enumerating all 2^14 masks",
            "987, 377, 129, 69, 60, or 36",
            "usable yield and rank",
            "solving, recovery, and sparse-linear-algebra costs",
            "matched generic baseline",
        ):
            self.assertIn(token, reopening)
        self.assertNotIn(
            "Kernel-check the exact recursive frozen C_r specialization",
            reopening,
        )
        self.assertNotIn(
            "Kernel-check a fixed-degree projective resultant common-root "
            "theorem",
            reopening,
        )
        self.assertIn("remaining mechanism gap", m16["relation_action"])
        self.assertIn(
            "TASK-020 kernel-checks",
            m16["relation_action"],
        )
        self.assertIn(
            "actual frozenC family",
            m16["relation_action"],
        )
        self.assertIn(
            "universal all-stage frozen witness-chain equivalence",
            m16["relation_action"],
        )
        self.assertIn("TASK-022 kernel-checks", m16["relation_action"])
        self.assertIn("56 scalar variables", m16["relation_action"])
        self.assertIn(
            "TASK-023 kernel-checks",
            m16["relation_action"],
        )
        self.assertIn("14 - I.card affine scalar variables", m16["relation_action"])
        self.assertIn("degree ceilings 2/4/2", m16["relation_action"])
        self.assertIn("TASK-024 kernel-checks", m16["relation_action"])
        self.assertIn(
            "16384 masks to 987 separated masks",
            m16["relation_action"],
        )
        self.assertIn("377 interior masks", m16["relation_action"])
        self.assertIn("TASK-025 kernel-checks", m16["relation_action"])
        self.assertIn("377 to 129 to 69 to 36", m16["relation_action"])
        self.assertIn(
            "independent boundary-only branch 129 to 60",
            m16["relation_action"],
        )
        self.assertIn("over any field", m16["relation_action"])
        self.assertIn("BalancedPropagatedRegular", m16["relation_action"])
        self.assertIn("single affine chart", m16["relation_action"])
        self.assertIn(
            "injective base change into an algebraically closed target",
            m16["relation_action"],
        )
        self.assertIn(
            "balanced regularity for the mapped target data",
            m16["relation_action"],
        )
        self.assertIn(
            "symbolic nonzeroness and nonemptiness of a usable regular locus",
            m16["relation_action"],
        )
        self.assertIn(
            "orchestration of its exceptional complement",
            m16["relation_action"],
        )
        self.assertIn(
            "all-stage frozen projective witness chain",
            m16["boundary"],
        )
        self.assertIn(
            "exact literal finite MvPolynomial family",
            m16["boundary"],
        )
        self.assertIn(
            "not an expanded direct S17 polynomial",
            m16["boundary"],
        )
        self.assertIn(
            "exact affine/infinity chart-polynomial cover",
            m16["boundary"],
        )
        self.assertIn(
            "2^14 logical masks are not enumerated or materialized",
            m16["boundary"],
        )
        self.assertIn("exact necessary infinity-stratum pruning", m16["boundary"])
        self.assertIn("16384 masks to 987 separated masks", m16["boundary"])
        self.assertIn("377 interior masks", m16["boundary"])
        self.assertIn("exact conditional infinity propagation", m16["boundary"])
        self.assertIn(
            "nested local reductions 377 to 129 to 69 to 36",
            m16["boundary"],
        )
        self.assertIn(
            "independent boundary-only branch 129 to 60",
            m16["boundary"],
        )
        self.assertIn(
            "exact single empty-mask affine chart",
            m16["boundary"],
        )
        self.assertIn(
            "not a unique witness",
            m16["boundary"],
        )
        self.assertIn(
            "direct propagation applies over any field",
            m16["boundary"],
        )
        self.assertIn(
            "source-stage bridge still requires injective base change",
            m16["boundary"],
        )
        self.assertIn(
            "separately assumed mapped-target regularity",
            m16["boundary"],
        )
        self.assertIn(
            "Symbolic nonzeroness, nonemptiness, density, probability, and genericity",
            m16["boundary"],
        )
        self.assertIn(
            "source-field computation does not automatically establish mapped regularity",
            m16["boundary"],
        )
        self.assertIn(
            "not an expanded direct S17 polynomial",
            m16["boundary"],
        )
        self.assertIn(
            "evidence of independent dimensions or relations",
            m16["boundary"],
        )
        self.assertIn("zero_retention_success", m16["boundary"])

    def test_wcc_precursor_is_bounded_and_does_not_replace_cans(self) -> None:
        sources = {
            item["id"]: item for item in self.source_registry["sources"]
        }
        self.assertEqual(
            "full_text_inspected",
            sources["yokota_kudo_yasuda2017_wcc"]["full_text_status"],
        )
        self.assertEqual(
            "full_text_unread",
            sources["kudo_yokota_takahashi_yasuda2018"]["full_text_status"],
        )

        claim_ids = {
            item["id"]
            for item in self.policy["source_claims"]
            if item["source_id"] == "yokota_kudo_yasuda2017_wcc"
        }
        expected = {
            "SC-WCC2017-PMINUS1-M2-PRACTICAL-LIMIT",
            "SC-WCC2017-PPLUS1-TRACE-EXTENSION",
        }
        self.assertEqual(expected, claim_ids)

        costs = {
            item["id"]: set(item["source_claim_ids"])
            for item in self.policy["cost_quantities"]
        }
        self.assertTrue(
            expected <= costs["CQ-PRIME-FIELD-RELATION-TOTAL"]
        )
        self.assertTrue(
            expected.isdisjoint(costs["CQ-SEMAEV-S17-SYSTEM-COST"])
        )
        self.assertTrue(
            expected.isdisjoint(costs["CQ-PKC-GENERALIZED-ROOT-COST"])
        )

        problems, state = self.build()
        self.assertEqual([], problems)
        cells = {item["cell_id"]: item for item in state["cells"]}
        self.assertEqual("open", cells["CELL-M-PKC-SMOOTH-M16"]["status"])
        self.assertEqual(
            "property_resolution_required",
            cells["CELL-M-PKC-AUXILIARY-CURVE"]["status"],
        )
        self.assertTrue(
            expected.isdisjoint(
                cells["CELL-M-PKC-SMOOTH-M16"]["source_claim_ids"]
            )
        )
        self.assertTrue(
            expected.isdisjoint(
                cells["CELL-M-PKC-AUXILIARY-CURVE"]["source_claim_ids"]
            )
        )

    def test_wcc_pplus1_m67_is_a_scoped_desk_rejection(self) -> None:
        problems, state = self.build()
        self.assertEqual([], problems)
        cells = {item["cell_id"]: item for item in state["cells"]}
        cell = cells["CELL-M-WCC-PPLUS1-TRACE-M67"]
        self.assertEqual("decided_inapplicable", cell["status"])
        self.assertFalse(cell["seed_eligible"])
        self.assertEqual("none", cell["authorization"])
        requirement = cell["requirement_results"][0]
        self.assertEqual(
            {
                "property_id": "TP-SECP-PPLUS1-TRACE-ROOT-CEILING",
                "property_status": "certificate_replayed",
                "operator": "gte",
                "expected": 345156162942,
                "actual": 9,
                "verdict": "violated",
                "source_claim_ids": [
                    "SC-SECP-PPLUS1-TORUS-DESK-SCREEN"
                ],
                "rationale": requirement["rationale"],
            },
            requirement,
        )
        decision = next(
            item
            for item in state["desk_decisions"]
            if item["cell_id"] == cell["cell_id"]
        )
        self.assertEqual("inapplicable", decision["classification"])
        self.assertEqual("none", decision["route_effect"])
        self.assertIn("route remains open_parked", cell["boundary"])

    def test_wcc_pplus1_threshold_is_recomputed(self) -> None:
        policy = copy.deepcopy(self.policy)
        mechanism = next(
            item
            for item in policy["mechanisms"]
            if item["id"] == "M-WCC-PPLUS1-TRACE-M67"
        )
        mechanism["requires_all"][0]["expected"] -= 1
        problems, _ = self.build(policy=policy)
        self.assertTrue(
            any(
                "must use the recomputed arity-7 relation-yield threshold"
                in item
                for item in problems
            )
        )

    def test_wcc_pplus1_property_is_bound_to_certificate(self) -> None:
        policy = copy.deepcopy(self.policy)
        property_record = next(
            item
            for item in policy["target_properties"]
            if item["id"] == "TP-SECP-PPLUS1-TRACE-ROOT-CEILING"
        )
        property_record["value"] = 10
        problems, _ = self.build(policy=policy)
        self.assertTrue(
            any(
                ".value differs from the replayed certificate" in item
                for item in problems
            )
        )

    def test_pkc_smooth_thresholds_are_recomputed_from_p_and_arity(self) -> None:
        policy = copy.deepcopy(self.policy)
        mechanism = next(
            item
            for item in policy["mechanisms"]
            if item["id"] == "M-PKC-SMOOTH-M16"
        )
        mechanism["requires_all"][0]["expected"] -= 1
        problems, _ = self.build(policy=policy)
        self.assertTrue(
            any("must use both recomputed thresholds" in item for item in problems)
        )

    def test_unknown_target_property_creates_resolution_work(self) -> None:
        problems, state = self.build()
        self.assertEqual([], problems)
        cell = next(
            item
            for item in state["cells"]
            if item["cell_id"] == "CELL-M-PKC-AUXILIARY-CURVE"
        )
        self.assertEqual("property_resolution_required", cell["status"])
        self.assertEqual("property_resolution", cell["intake_mode"])
        self.assertTrue(cell["seed_eligible"])

    def test_desk_decision_cannot_close_a_route(self) -> None:
        records = copy.deepcopy(self.desk_records)
        records[0][1]["route_effect"] = "closed"
        problems, _ = self.build(desk_records=records)
        self.assertTrue(
            any("route_effect must remain none" in item for item in problems)
        )

    def test_desk_decision_cannot_authorize_work(self) -> None:
        records = copy.deepcopy(self.desk_records)
        records[0][1]["authorization"] = "exploration"
        problems, _ = self.build(desk_records=records)
        self.assertTrue(
            any("authorization must remain none" in item for item in problems)
        )

    def test_desk_decision_scope_cannot_be_route_wide(self) -> None:
        records = copy.deepcopy(self.desk_records)
        records[0][1]["scope"] = "route"
        problems, _ = self.build(desk_records=records)
        self.assertTrue(any("scope is too broad" in item for item in problems))

    def test_decided_cell_requires_exactly_one_desk_decision(self) -> None:
        records = copy.deepcopy(self.desk_records)[1:]
        problems, _ = self.build(desk_records=records)
        self.assertTrue(
            any("decided cells lack desk decisions" in item for item in problems)
        )

    def test_property_verdict_is_recomputed_not_authored(self) -> None:
        records = copy.deepcopy(self.desk_records)
        records[1][1]["property_verdicts"][0]["actual"] = True
        records[1][1]["property_verdicts"][0]["verdict"] = "satisfied"
        problems, _ = self.build(desk_records=records)
        self.assertTrue(
            any("differs from the materialized cell" in item for item in problems)
        )

    def test_desk_decision_covers_repeated_property_requirements(self) -> None:
        records = copy.deepcopy(self.desk_records)
        decision = next(
            record
            for _, record in records
            if record["cell_id"] == "CELL-M-PKC-SMOOTH-M4"
        )
        decision["property_verdicts"].pop()
        problems, _ = self.build(desk_records=records)
        self.assertTrue(
            any(
                "property_verdicts do not cover every cell requirement" in item
                for item in problems
            )
        )


if __name__ == "__main__":
    unittest.main()
