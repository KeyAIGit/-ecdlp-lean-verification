#!/usr/bin/env python3
from __future__ import annotations

import json
import unittest
from pathlib import Path

import uorc056_even_divpoly_fourier_collapse as v10


class EvenDivisionPolynomialFourierCollapseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.grammar = Path(
            "experiments/uorc056/divisor_aware_rational_grammar.json"
        )
        cls.result = v10.run(cls.grammar)

    def test_published_bound_closes_fourteen_curves(self) -> None:
        corpus = self.result["corpus"]
        self.assertEqual(corpus["curve_count"], 18)
        self.assertEqual(
            corpus["curves_closed_by_published_six_sqrt_inequality"], 14
        )
        self.assertEqual(
            corpus[
                "curves_requiring_complete_multiplier_scan_under_published_bound"
            ],
            4,
        )

    def test_sharp_provisional_bound_closes_seventeen_curves(self) -> None:
        corpus = self.result["corpus"]
        self.assertEqual(
            corpus["curves_closed_by_sharp_four_sqrt_inequality"], 17
        )
        self.assertEqual(
            corpus[
                "curves_requiring_complete_multiplier_scan_under_sharp_bound"
            ],
            1,
        )

    def test_every_multiplier_class_is_exact_negative(self) -> None:
        for row in self.result["corpus"]["records"]:
            self.assertEqual(row["exact_candidates"], [])
            self.assertEqual(row["multiplier_classes_tested"], row["n"] - 1)

    def test_published_bound_exceptions_are_exactly_four_small_curves(self) -> None:
        exceptions = [
            (row["p"], row["n"])
            for row in self.result["corpus"]["records"]
            if not row["certified_published_fourier_closed"]
        ]
        self.assertEqual(
            exceptions,
            [(43, 31), (79, 67), (61, 61), (97, 79)],
        )
        first = self.result["corpus"]["records"][0]
        self.assertEqual(first["best"]["matches"], 24)
        self.assertEqual(first["best"]["u"], 8)

    def test_chain_collapse_replay_is_nontrivial(self) -> None:
        replay = self.result["chain_rule_replay"]
        self.assertEqual(replay["maximum_even_index"], 256)
        self.assertGreater(replay["point_index_checks"], 10000)

    def test_secp256k1_is_closed_by_published_bound(self) -> None:
        secp = self.result["secp256k1"]
        self.assertTrue(secp["certified_published_six_sqrt_closed"])
        self.assertGreater(
            float(secp["peak_over_six_sqrt_p_log2"]),
            124.0,
        )
        self.assertTrue(secp["certified_sharp_four_sqrt_closed"])

    def test_integer_certificates(self) -> None:
        self.assertFalse(v10.certified_peak_exceeds_six_sqrt(43, 31))
        self.assertTrue(v10.certified_peak_exceeds_six_sqrt(67, 79))
        self.assertFalse(v10.certified_peak_exceeds_six_sqrt(79, 67))
        self.assertTrue(
            v10.certified_peak_exceeds_six_sqrt(
                v10.SECP256K1_P,
                v10.SECP256K1_N,
            )
        )
        self.assertFalse(v10.certified_peak_exceeds_four_sqrt(43, 31))
        self.assertTrue(v10.certified_peak_exceeds_four_sqrt(79, 67))

    def test_canonical_json(self) -> None:
        parsed = json.loads(v10.stable_json(self.result))
        self.assertEqual(parsed["experiment"], v10.PROFILE_ID)
        self.assertEqual(parsed["schema_version"], "1.1")


if __name__ == "__main__":
    unittest.main()
