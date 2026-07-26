#!/usr/bin/env python3
"""Fault-injection tests for deterministic, non-executing shadow intake."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from build_research_shadow_intake import build_state

ROOT = Path(__file__).resolve().parent.parent


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class ResearchShadowIntakeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sources = load("data/source_registry.json")
        self.typed = load("data/typed_evidence_state.json")
        self.claims = load("data/research_claim_state.json")

    def build(self) -> dict:
        return build_state(self.sources, self.typed, self.claims)

    def test_canonical_shadow_intake_is_non_executable(self) -> None:
        state = self.build()
        self.assertEqual(4, state["counts"]["proposal_stubs"])
        self.assertEqual(1, state["counts"]["parked_ideas"])
        self.assertEqual(0, state["counts"]["admissible"])
        self.assertEqual(0, state["counts"]["recommended"])
        self.assertEqual(0, state["counts"]["authorized"])
        for stub in state["proposal_stubs"]:
            self.assertFalse(stub["executable"])
            self.assertFalse(stub["authorized"])
            self.assertEqual("research_question_seed", stub["scientific_identity"])

    def test_kudo_full_text_status_controls_literature_stub(self) -> None:
        before = self.build()
        kudo = next(
            source
            for source in self.sources["sources"]
            if source["id"] == "kudo_yokota_takahashi_yasuda2018"
        )
        self.assertTrue(
            any(stub["anchor_id"] == kudo["id"] for stub in before["proposal_stubs"])
        )
        kudo["full_text_status"] = "full_text_inspected"
        after = self.build()
        self.assertFalse(
            any(stub["anchor_id"] == kudo["id"] for stub in after["proposal_stubs"])
        )

    def test_petit_constructions_and_cost_are_separate_stubs(self) -> None:
        state = self.build()
        by_anchor: dict[str, list[str]] = {}
        for stub in state["proposal_stubs"]:
            by_anchor.setdefault(stub["anchor_id"], []).append(stub["stub_kind"])
        self.assertEqual(
            ["desk_cost_contract"],
            by_anchor["CELL-M-PKC-SMOOTH-M14"],
        )
        self.assertEqual(
            ["full_cost_contract", "structural_applicability"],
            sorted(by_anchor["CELL-M-PKC-AUXILIARY-CURVE"]),
        )

    def test_closed_and_inapplicable_cells_never_create_stubs(self) -> None:
        state = self.build()
        anchors = {stub["anchor_id"] for stub in state["proposal_stubs"]}
        self.assertNotIn("CELL-M-GLV-INDEPENDENT-CUBES", anchors)
        self.assertNotIn("CELL-M-PKC-SMOOTH-M4", anchors)
        self.assertNotIn("CELL-M-FHJRV-DIRECT-TWO-TORSION", anchors)

    def test_desired_glv_properties_remain_parked_without_exact_map(self) -> None:
        state = self.build()
        parked = state["parked_ideas"]
        self.assertEqual(
            ["PARKED-M-GLV-FAITHFUL-PHASE-QUOTIENT"],
            [item["parked_id"] for item in parked],
        )
        self.assertFalse(parked[0]["seed_eligible"])
        self.assertIn(
            "exact phase-preserving map",
            parked[0]["missing_before_intake"],
        )

    def test_output_is_order_independent(self) -> None:
        first = self.build()
        shuffled_sources = copy.deepcopy(self.sources)
        shuffled_sources["sources"].reverse()
        shuffled_typed = copy.deepcopy(self.typed)
        shuffled_typed["cells"].reverse()
        second = build_state(shuffled_sources, shuffled_typed, self.claims)
        self.assertEqual(
            first["proposal_stubs"],
            second["proposal_stubs"],
        )


if __name__ == "__main__":
    unittest.main()
