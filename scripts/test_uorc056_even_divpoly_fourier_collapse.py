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

    def test_seventeen_of_eighteen_curves_close_by_fourier_bound(self) -> None:
        corpus = self.result["corpus"]
        self.assertEqual(corpus["curve_count"], 18)
        self.assertEqual(
            corpus["curves_closed_by_certified_fourier_inequality"], 17
        )
        self.assertEqual(
            corpus["curves_closed_by_complete_multiplier_scan_only"], 1
        )

    def test_every_multiplier_class_is_exact_negative(self) -> None:
        for row in self.result["corpus"]["records"]:
            self.assertEqual(row["exact_candidates"], [])
            self.assertEqual(row["multiplier_classes_tested"], row["n"] - 1)

    def test_small_exception_is_p43(self) -> None:
        exceptions = [
            row
            for row in self.result["corpus"]["records"]
            if not row["certified_fourier_closed"]
        ]
        self.assertEqual(len(exceptions), 1)
        self.assertEqual(exceptions[0]["p"], 43)
        self.assertEqual(exceptions[0]["n"], 31)
        self.assertEqual(exceptions[0]["best"]["matches"], 24)
        self.assertEqual(exceptions[0]["best"]["u"], 8)

    def test_chain_collapse_replay_is_nontrivial(self) -> None:
        replay = self.result["chain_rule_replay"]
        self.assertEqual(replay["maximum_even_index"], 256)
        self.assertGreater(replay["point_index_checks"], 10000)

    def test_secp256k1_is_certified_closed(self) -> None:
        secp = self.result["secp256k1"]
        self.assertTrue(secp["certified_fourier_closed"])
        self.assertGreater(float(secp["peak_over_four_sqrt_p_log2"]), 125.0)

    def test_integer_certificate(self) -> None:
        self.assertFalse(v10.certified_peak_exceeds_four_sqrt(43, 31))
        self.assertTrue(v10.certified_peak_exceeds_four_sqrt(67, 79))
        self.assertTrue(
            v10.certified_peak_exceeds_four_sqrt(
                v10.SECP256K1_P, v10.SECP256K1_N
            )
        )

    def test_canonical_json(self) -> None:
        parsed = json.loads(v10.stable_json(self.result))
        self.assertEqual(parsed["experiment"], v10.PROFILE_ID)


if __name__ == "__main__":
    unittest.main()
