#!/usr/bin/env python3
from __future__ import annotations

import json
import unittest
from pathlib import Path

import uorc056_divisor_aware_balanced_product as balanced
import uorc056_divisor_aware_rational as rational


class DivisorAwareBalancedProductTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.grammar_path = Path(
            "experiments/uorc056/"
            "divisor_aware_balanced_product_grammar.json"
        )
        cls.grammar = json.loads(
            cls.grammar_path.read_text(encoding="utf-8")
        )
        cls.result = balanced.run(cls.grammar_path)

    def test_exact_bounded_negative(self) -> None:
        self.assertFalse(
            self.result["discovery_exact_search"]["candidate_found"]
        )
        self.assertFalse(
            self.result["full_corpus_exact_search"]["candidate_found"]
        )
        self.assertEqual(
            self.result["decision"],
            "no_exact_balanced_line_product_divisor_circuit_weight_le_4",
        )

    def test_frozen_catalog_counts(self) -> None:
        discovery = self.result["discovery_catalog"]
        self.assertEqual(discovery["line_templates"], 360)
        self.assertEqual(discovery["unordered_line_products"], 64980)
        self.assertEqual(discovery["valuation_signatures"], 31375)
        self.assertEqual(discovery["semantic_product_profiles"], 48204)
        self.assertEqual(
            discovery["admissible_unordered_product_ratios"],
            104855,
        )
        self.assertEqual(discovery["unique_sign_vectors"], 1186)
        self.assertEqual(
            discovery["novel_exceptional_sign_vectors"],
            429,
        )

        full = self.result["full_corpus_catalog"]
        self.assertEqual(full["valuation_signatures"], 33930)
        self.assertEqual(full["semantic_product_profiles"], 48218)
        self.assertEqual(
            full["admissible_unordered_product_ratios"],
            68930,
        )
        self.assertEqual(full["unique_sign_vectors"], 32)
        self.assertEqual(full["novel_exceptional_sign_vectors"], 0)

    def test_exhaustive_weight_four_pair_index_counts(self) -> None:
        discovery = self.result["discovery_exact_search"]
        self.assertEqual(discovery["pair_count"], 702705)
        self.assertEqual(discovery["pair_xor_classes"], 13874)
        self.assertEqual(
            discovery["maximum_pair_xor_multiplicity"],
            570,
        )

        full = self.result["full_corpus_exact_search"]
        self.assertEqual(full["pair_count"], 496)
        self.assertEqual(full["pair_xor_classes"], 31)
        self.assertEqual(
            full["maximum_pair_xor_multiplicity"],
            16,
        )

    def test_best_correlations_remain_nonexact(self) -> None:
        discovery = self.result[
            "best_discovery_correlations"
        ]["weight_two"]
        self.assertEqual(discovery["matches"], 260)
        self.assertEqual(discovery["total"], 438)

        full = self.result[
            "best_full_corpus_correlations"
        ]["weight_two"]
        self.assertEqual(full["matches"], 3790)
        self.assertEqual(full["total"], 7434)
        self.assertLess(float(full["accuracy"]), 0.510)

    def test_cross_factor_cancellation_is_admitted(self) -> None:
        profiles = [
            balanced.SparseLineProfile(((0, 1),), 0),
            balanced.SparseLineProfile((), 1),
            balanced.SparseLineProfile((), 2),
            balanced.SparseLineProfile(((0, 1),), 4),
        ]
        classes = balanced.product_classes(profiles)
        signature = ((0, 1),)
        semantic_products = classes[signature]
        self.assertIn(1, semantic_products)
        self.assertIn(6, semantic_products)
        self.assertEqual(semantic_products[1], (0, 1))
        self.assertEqual(semantic_products[6], (2, 3))

    def test_product_leading_sign_xor_matches_direct_value(self) -> None:
        base_grammar = json.loads(
            Path(self.grammar["base_ratio_grammar"]).read_text(
                encoding="utf-8"
            )
        )
        curve = rational.parse_curve(base_grammar["discovery_corpus"][0])
        contexts, _ = rational.contexts((curve,))
        lines = rational.line_templates(base_grammar)
        profiles = balanced.sparse_line_profiles(lines[:2], contexts)

        p, _, _ = curve
        local_point = contexts[0][1][0]
        direct_sign = 1
        for line in lines[:2]:
            a = rational.symbol(line[0], curve)
            b = rational.symbol(line[1], curve)
            c = rational.symbol(line[2], curve)
            _, lead = rational.line_order_and_lead(
                a,
                b,
                c,
                local_point,
                p,
            )
            direct_sign *= (
                1 if pow(lead, (p - 1) // 2, p) == 1 else -1
            )

        product_bits = (
            profiles[0].lead_sign_bits
            ^ profiles[1].lead_sign_bits
        )
        encoded_sign = -1 if product_bits & 1 else 1
        self.assertEqual(encoded_sign, direct_sign)

    def test_weight_four_search_is_complete_on_tiny_fixture(self) -> None:
        line = ("one", "zero", "zero")
        representatives = {
            1 << index: balanced.ProductRatioMeta(
                (line, line),
                (line, line),
                False,
                0,
            )
            for index in range(4)
        }
        candidate, stats = balanced.exact_search(
            representatives,
            target=15,
            total=4,
            maximum_weight=4,
        )
        self.assertIsNotNone(candidate)
        assert candidate is not None
        self.assertEqual(candidate["weight"], 4)
        self.assertEqual(candidate["output_phase"], 1)
        self.assertEqual(stats["pair_count"], 6)


if __name__ == "__main__":
    unittest.main()
