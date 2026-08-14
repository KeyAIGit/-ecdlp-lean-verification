#!/usr/bin/env python3
from __future__ import annotations

import json
import unittest
from pathlib import Path

import uorc056_divisor_aware_rational as rational


class DivisorAwareRationalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.grammar_path = Path(
            "experiments/uorc056/divisor_aware_rational_grammar.json"
        )
        cls.grammar = json.loads(cls.grammar_path.read_text(encoding="utf-8"))
        cls.result = rational.run(cls.grammar_path)

    def test_exact_bounded_negative(self) -> None:
        self.assertFalse(
            self.result["discovery_exact_search"]["candidate_found"]
        )
        self.assertFalse(
            self.result["full_corpus_exact_search"]["candidate_found"]
        )
        self.assertEqual(
            self.result["decision"],
            "no_exact_divisor_aware_line_ratio_circuit_weight_le_4",
        )

    def test_frozen_catalog_counts(self) -> None:
        discovery = self.result["discovery_catalog"]
        self.assertEqual(discovery["line_templates"], 360)
        self.assertEqual(discovery["valuation_signatures"], 250)
        self.assertEqual(discovery["admissible_unordered_ratios"], 673)
        self.assertEqual(discovery["ratios_with_canceled_orbit_zero"], 463)
        self.assertEqual(discovery["unique_sign_vectors"], 103)
        self.assertEqual(discovery["novel_exceptional_sign_vectors"], 6)

        full = self.result["full_corpus_catalog"]
        self.assertEqual(full["valuation_signatures"], 260)
        self.assertEqual(full["admissible_unordered_ratios"], 541)
        self.assertEqual(full["ratios_with_canceled_orbit_zero"], 463)
        self.assertEqual(full["unique_sign_vectors"], 21)
        self.assertEqual(full["novel_exceptional_sign_vectors"], 0)

    def test_local_parameter_and_tangent_orders(self) -> None:
        p = 43
        point = (2, 12)
        local = rational.local_y_series(point, p)
        x, y, slope, _, _ = local

        vertical_order, _ = rational.line_order_and_lead(
            1,
            0,
            -x % p,
            local,
            p,
        )
        self.assertEqual(vertical_order, 1)

        tangent_order, _ = rational.line_order_and_lead(
            -slope % p,
            1,
            (slope * x - y) % p,
            local,
            p,
        )
        self.assertEqual(tangent_order, 2)

    def test_self_ratio_regularizes_to_one_at_zeros(self) -> None:
        discovery_curves = tuple(
            rational.parse_curve(row)
            for row in self.grammar["discovery_corpus"]
        )
        curve_contexts, _ = rational.contexts(discovery_curves)
        for line in rational.line_templates(self.grammar):
            profile = rational.line_profile(line, curve_contexts)
            if profile.zero_count:
                bits = rational.ratio_sign_bits(
                    line,
                    line,
                    {line: profile},
                )
                self.assertEqual(bits, 0)
                return
        self.fail("expected at least one line meeting the frozen subgroup corpus")

    def test_weight_four_search_is_complete_on_tiny_fixture(self) -> None:
        lines = [
            ("one", "zero", "zero"),
            ("zero", "one", "zero"),
            ("one", "one", "zero"),
            ("one", "neg_one", "zero"),
        ]
        representatives = {
            1 << index: rational.RatioMeta(line, line, False, 0)
            for index, line in enumerate(lines)
        }
        candidate = rational.exact_search(
            representatives,
            target=15,
            total=4,
            maximum_weight=4,
        )
        self.assertIsNotNone(candidate)
        assert candidate is not None
        self.assertEqual(candidate["weight"], 4)
        self.assertEqual(candidate["output_phase"], 1)

    def test_best_full_corpus_signal_is_near_chance(self) -> None:
        best = self.result["best_full_corpus_correlations"]["weight_two"]
        self.assertEqual(best["matches"], 3790)
        self.assertEqual(best["total"], 7434)
        self.assertLess(float(best["accuracy"]), 0.51)


if __name__ == "__main__":
    unittest.main()
