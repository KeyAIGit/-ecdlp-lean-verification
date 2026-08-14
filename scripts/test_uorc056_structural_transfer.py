#!/usr/bin/env python3
from __future__ import annotations

import json
import unittest
from pathlib import Path

import uorc056_structural_transfer as screen


class StructuralTransferTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.grammar_path = Path(
            "experiments/uorc056/structural_transfer_grammar.json"
        )
        cls.result = screen.run(cls.grammar_path)

    def test_exact_bounded_negative(self) -> None:
        self.assertFalse(
            self.result["discovery_exact_search"]["candidate_found"]
        )
        self.assertFalse(
            self.result["full_corpus_exact_search"]["candidate_found"]
        )
        self.assertEqual(
            self.result["decision"],
            "no_exact_structural_transfer_circuit_weight_le_4",
        )

    def test_frozen_enumeration_counts(self) -> None:
        enumeration = self.result["enumeration"]
        self.assertEqual(enumeration["raw_symbolic_templates"], 8174)
        self.assertEqual(enumeration["valid_on_discovery"], 723)
        self.assertEqual(enumeration["unique_discovery_sign_vectors"], 605)
        self.assertEqual(enumeration["valid_on_full_corpus"], 163)
        self.assertEqual(enumeration["unique_full_corpus_sign_vectors"], 129)

    def test_best_pair_remains_below_exactness(self) -> None:
        best = self.result["best_discovery_correlations"]["weight_two"]
        self.assertEqual(best["matches"], 272)
        self.assertEqual(best["total"], 438)
        self.assertLess(best["matches"], best["total"])

    def test_weight_four_search_is_complete_on_tiny_fixture(self) -> None:
        templates = (
            ("same", 1, "one", "zero", "zero"),
            ("same", 1, "zero", "one", "zero"),
            ("same", 2, "one", "zero", "zero"),
            ("same", 2, "zero", "one", "zero"),
        )
        representatives = {
            1: templates[0],
            2: templates[1],
            4: templates[2],
            8: templates[3],
        }
        candidate = screen.exact_search(
            representatives,
            target=15,
            total=4,
            maximum_weight=4,
        )
        self.assertIsNotNone(candidate)
        assert candidate is not None
        self.assertEqual(candidate["weight"], 4)
        self.assertEqual(candidate["output_phase"], 1)

    def test_beta_branches_are_exact(self) -> None:
        for row in json.loads(
            self.grammar_path.read_text(encoding="utf-8")
        )["discovery_corpus"]:
            spec = screen.parse_curve(row)
            beta_lo, beta_hi = screen.beta_pair(spec[0])
            self.assertNotEqual(beta_lo, beta_hi)
            for beta in (beta_lo, beta_hi):
                self.assertEqual(
                    (beta * beta + beta + 1) % spec[0],
                    0,
                )


if __name__ == "__main__":
    unittest.main()
