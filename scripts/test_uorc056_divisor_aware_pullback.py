#!/usr/bin/env python3
from __future__ import annotations

import json
import unittest
from pathlib import Path

import uorc056_divisor_aware_pullback as pullback
import uorc056_divisor_aware_rational as rational


class DivisorAwarePullbackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.grammar_path = Path(
            "experiments/uorc056/divisor_aware_pullback_grammar.json"
        )
        cls.grammar = json.loads(cls.grammar_path.read_text(encoding="utf-8"))
        cls.base_grammar = json.loads(
            Path(cls.grammar["base_ratio_grammar"]).read_text(encoding="utf-8")
        )
        cls.result = pullback.run(cls.grammar_path)

    def test_exact_bounded_negative(self) -> None:
        self.assertFalse(
            self.result["discovery_exact_search"]["candidate_found"]
        )
        self.assertFalse(
            self.result["full_corpus_exact_search"]["candidate_found"]
        )
        self.assertEqual(
            self.result["decision"],
            "no_exact_divisor_aware_pullback_circuit_weight_le_4",
        )

    def test_frozen_pullback_catalog_counts(self) -> None:
        discovery = self.result["discovery_catalog"]
        self.assertEqual(discovery["raw_pullback_asts"], 2692)
        self.assertEqual(discovery["raw_exceptional_pullback_asts"], 1852)
        self.assertEqual(
            discovery["semantic_pullback_atoms_before_quotient"], 412
        )
        self.assertEqual(discovery["unique_pullback_sign_vectors"], 406)
        self.assertEqual(discovery["novel_pullback_exceptional_vectors"], 24)

        full = self.result["full_corpus_catalog"]
        self.assertEqual(full["raw_pullback_asts"], 2164)
        self.assertEqual(full["semantic_pullback_atoms_before_quotient"], 84)
        self.assertEqual(full["unique_pullback_sign_vectors"], 78)
        self.assertEqual(full["novel_pullback_exceptional_vectors"], 0)

    def test_best_discovery_pair_is_not_exact(self) -> None:
        best = self.result["best_discovery_correlations"]["weight_two"]
        self.assertEqual(best["matches"], 278)
        self.assertEqual(best["total"], 438)
        self.assertLess(best["matches"], best["total"])

    def test_best_full_pair_remains_weak(self) -> None:
        best = self.result["best_full_corpus_correlations"]["weight_two"]
        self.assertEqual(best["matches"], 3874)
        self.assertEqual(best["total"], 7434)
        self.assertLess(float(best["accuracy"]), 0.522)

    def test_pullback_is_a_blockwise_permutation(self) -> None:
        curves = tuple(
            rational.parse_curve(row)
            for row in self.base_grammar["discovery_corpus"]
        )
        curve_contexts, _ = rational.contexts(curves)
        lines = rational.line_templates(self.base_grammar)
        representatives, _, _, _ = pullback.base_ratio_details(
            lines, curve_contexts
        )
        vector = next(iter(representatives))
        transformed = pullback.pullback_bits(vector, curves, 4)

        offset = 0
        for _, order, _ in curves:
            mask = (1 << (order - 1)) - 1
            original_weight = ((vector >> offset) & mask).bit_count()
            transformed_weight = ((transformed >> offset) & mask).bit_count()
            self.assertEqual(original_weight, transformed_weight)
            offset += order - 1

    def test_weight_four_search_is_complete_on_tiny_fixture(self) -> None:
        lines = [
            ("one", "zero", "zero"),
            ("zero", "one", "zero"),
            ("one", "one", "zero"),
            ("one", "neg_one", "zero"),
        ]
        representatives = {
            1 << index: pullback.PullbackMeta(
                index + 1,
                rational.RatioMeta(line, line, False, 0),
            )
            for index, line in enumerate(lines)
        }
        candidate = pullback.exact_search(
            representatives,
            target=15,
            total=4,
            maximum_weight=4,
        )
        self.assertIsNotNone(candidate)
        assert candidate is not None
        self.assertEqual(candidate["weight"], 4)
        self.assertEqual(candidate["output_phase"], 1)


if __name__ == "__main__":
    unittest.main()
