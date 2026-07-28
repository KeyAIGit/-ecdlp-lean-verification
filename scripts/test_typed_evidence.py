#!/usr/bin/env python3
"""Regression fixtures for the typed evidence and desk-decision layer."""
from __future__ import annotations

import copy
import unittest

from typed_evidence_lib import (
    DECISIONS_PATH,
    DESK_DECISIONS_DIR,
    POLICY_PATH,
    SOURCE_REGISTRY_PATH,
    build_state,
    load_json,
    load_records,
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

    def test_canonical_state_is_valid_and_non_authorizing(self) -> None:
        problems, state = self.build()
        self.assertEqual([], problems)
        self.assertEqual(
            {
                "source_claims": 23,
                "target_properties": 5,
                "mechanisms": 7,
                "cells": 7,
                "open_cells": 3,
                "property_resolution_cells": 1,
                "decided_inapplicable_cells": 2,
                "decided_closed_cells": 1,
                "seed_eligible_cells": 2,
                "desk_decisions": 3,
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
        self.assertFalse(
            any(
                decision["cell_id"] == "CELL-M-PKC-SMOOTH-M16"
                for decision in state["desk_decisions"]
            )
        )
        claims = {
            item["id"]: item for item in state["source_claims"]
        }
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
