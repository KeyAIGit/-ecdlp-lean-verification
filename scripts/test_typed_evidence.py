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
                "source_claims": 12,
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

    def test_m4_screen_does_not_close_the_m14_cost_cell(self) -> None:
        problems, state = self.build()
        self.assertEqual([], problems)
        cells = {item["cell_id"]: item for item in state["cells"]}
        self.assertEqual(
            "decided_inapplicable", cells["CELL-M-PKC-SMOOTH-M4"]["status"]
        )
        self.assertEqual("open", cells["CELL-M-PKC-SMOOTH-M14"]["status"])
        self.assertTrue(cells["CELL-M-PKC-SMOOTH-M14"]["seed_eligible"])

    def test_pkc_smooth_threshold_is_recomputed_from_p_and_arity(self) -> None:
        policy = copy.deepcopy(self.policy)
        mechanism = next(
            item
            for item in policy["mechanisms"]
            if item["id"] == "M-PKC-SMOOTH-M14"
        )
        mechanism["requires_all"][0]["expected"] -= 1
        problems, _ = self.build(policy=policy)
        self.assertTrue(
            any("recomputed ceil(p^(1/14))" in item for item in problems)
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


if __name__ == "__main__":
    unittest.main()
