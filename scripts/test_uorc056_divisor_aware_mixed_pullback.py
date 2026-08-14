#!/usr/bin/env python3
from __future__ import annotations

import json
import unittest
from pathlib import Path

import uorc056_circuit_synth as base
import uorc056_divisor_aware_mixed_pullback as mixed
import uorc056_divisor_aware_rational as rational

Dual = tuple[int, int]
DualPoint = tuple[Dual, Dual]


def d_add(left: Dual, right: Dual, p: int) -> Dual:
    return (left[0] + right[0]) % p, (left[1] + right[1]) % p


def d_sub(left: Dual, right: Dual, p: int) -> Dual:
    return (left[0] - right[0]) % p, (left[1] - right[1]) % p


def d_mul(left: Dual, right: Dual, p: int) -> Dual:
    return (
        left[0] * right[0] % p,
        (left[0] * right[1] + left[1] * right[0]) % p,
    )


def d_inv(value: Dual, p: int) -> Dual:
    inverse = pow(value[0], -1, p)
    return inverse, (-value[1] * inverse * inverse) % p


def d_div(left: Dual, right: Dual, p: int) -> Dual:
    return d_mul(left, d_inv(right, p), p)


def d_scale(value: Dual, scalar: int, p: int) -> Dual:
    return value[0] * scalar % p, value[1] * scalar % p


def dual_double(point: DualPoint, p: int) -> DualPoint:
    x, y = point
    slope = d_div(
        d_scale(d_mul(x, x, p), 3, p),
        d_scale(y, 2, p),
        p,
    )
    x3 = d_sub(d_mul(slope, slope, p), d_scale(x, 2, p), p)
    y3 = d_sub(d_mul(slope, d_sub(x, x3, p), p), y, p)
    return x3, y3


def dual_add(left: DualPoint, right: DualPoint, p: int) -> DualPoint:
    x1, y1 = left
    x2, y2 = right
    slope = d_div(d_sub(y2, y1, p), d_sub(x2, x1, p), p)
    x3 = d_sub(d_sub(d_mul(slope, slope, p), x1, p), x2, p)
    y3 = d_sub(d_mul(slope, d_sub(x1, x3, p), p), y1, p)
    return x3, y3


def dual_mul_small(point: DualPoint, multiplier: int, p: int) -> DualPoint:
    if multiplier == 1:
        return point
    if multiplier == 2:
        return dual_double(point, p)
    if multiplier == 3:
        return dual_add(dual_double(point, p), point, p)
    if multiplier == 4:
        return dual_double(dual_double(point, p), p)
    raise AssertionError("test supports multipliers one through four")


class DivisorAwareMixedPullbackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.grammar_path = Path(
            "experiments/uorc056/divisor_aware_mixed_pullback_grammar.json"
        )
        cls.grammar = json.loads(cls.grammar_path.read_text(encoding="utf-8"))
        cls.base_grammar = json.loads(
            Path(cls.grammar["base_ratio_grammar"]).read_text(encoding="utf-8")
        )
        cls.result = mixed.run(cls.grammar_path)

    def test_exact_bounded_negative(self) -> None:
        self.assertFalse(
            self.result["discovery_exact_search"]["candidate_found"]
        )
        self.assertFalse(
            self.result["full_corpus_exact_search"]["candidate_found"]
        )
        self.assertEqual(
            self.result["decision"],
            "no_exact_mixed_pullback_divisor_circuit_weight_le_4",
        )

    def test_frozen_catalog_counts(self) -> None:
        discovery = self.result["discovery_catalog"]
        self.assertEqual(discovery["pulled_line_templates"], 1440)
        self.assertEqual(discovery["valuation_signatures"], 982)
        self.assertEqual(
            discovery["admissible_unordered_mixed_ratios"], 5149
        )
        self.assertEqual(discovery["unique_sign_vectors"], 1693)
        self.assertEqual(discovery["novel_exceptional_sign_vectors"], 75)

        full = self.result["full_corpus_catalog"]
        self.assertEqual(full["valuation_signatures"], 1037)
        self.assertEqual(full["admissible_unordered_mixed_ratios"], 3028)
        self.assertEqual(full["unique_sign_vectors"], 354)
        self.assertEqual(full["novel_exceptional_sign_vectors"], 0)

    def test_exhaustive_pair_index_counts(self) -> None:
        discovery = self.result["discovery_exact_search"]
        self.assertEqual(discovery["pair_count"], 1432278)
        self.assertEqual(discovery["pair_xor_classes"], 345626)
        self.assertEqual(discovery["maximum_pair_xor_multiplicity"], 701)

        full = self.result["full_corpus_exact_search"]
        self.assertEqual(full["pair_count"], 62481)
        self.assertEqual(full["pair_xor_classes"], 10001)
        self.assertEqual(full["maximum_pair_xor_multiplicity"], 163)

    def test_best_correlations_remain_nonexact(self) -> None:
        discovery = self.result["best_discovery_correlations"]["weight_two"]
        self.assertEqual(discovery["matches"], 280)
        self.assertEqual(discovery["total"], 438)

        full = self.result["best_full_corpus_correlations"]["weight_two"]
        self.assertEqual(full["matches"], 3888)
        self.assertEqual(full["total"], 7434)
        self.assertLess(float(full["accuracy"]), 0.524)

    def test_invariant_differential_derivative_formula(self) -> None:
        curve = rational.parse_curve(self.base_grammar["discovery_corpus"][0])
        p, order, generator = curve
        points = base.orbit(generator, order, p)
        point = points[1]
        self.assertIsNotNone(point)
        assert point is not None
        x, y = point
        _, _, d1, _, _ = rational.local_y_series(point, p)
        dual_point: DualPoint = ((x, 1), (y, d1))

        for multiplier in (1, 2, 3, 4):
            dual_image = dual_mul_small(dual_point, multiplier, p)
            image = points[multiplier % order]
            self.assertIsNotNone(image)
            assert image is not None
            expected = multiplier * image[1] * pow(y, -1, p) % p
            self.assertEqual(dual_image[0][0], image[0])
            self.assertEqual(dual_image[0][1], expected)

    def test_weight_four_search_is_complete_on_tiny_fixture(self) -> None:
        lines = [
            ("one", "zero", "zero"),
            ("zero", "one", "zero"),
            ("one", "one", "zero"),
            ("one", "neg_one", "zero"),
        ]
        representatives = {
            1 << index: mixed.MixedRatioMeta(
                (1, line),
                (index + 1, line),
                False,
                0,
            )
            for index, line in enumerate(lines)
        }
        candidate, stats = mixed.exact_search(
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
