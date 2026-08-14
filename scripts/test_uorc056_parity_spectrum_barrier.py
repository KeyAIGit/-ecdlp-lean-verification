#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import unittest
from pathlib import Path

import uorc056_parity_spectrum_barrier as barrier


class ParitySpectrumBarrierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.grammar = Path(
            "experiments/uorc056/divisor_aware_rational_grammar.json"
        )
        cls.result = barrier.run(cls.grammar)

    def test_exact_peak_identity_on_small_odd_orders(self) -> None:
        for n in (3, 5, 7, 31, 67, 79, 127, 139):
            barrier.verify_peak_identity(n)

    def test_peak_closed_form(self) -> None:
        n = 31
        r = (n - 1) // 2
        direct = abs(barrier.direct_nonzero_fourier_sum(n, r))
        self.assertAlmostEqual(
            direct,
            1.0 / math.tan(math.pi / (2.0 * n)),
            places=10,
        )

    def test_certified_bound_never_exceeds_sharp_float_bound(self) -> None:
        for row in self.result["records"][:-1]:
            certified = int(
                row["certified_odd_divisor_support_lower_bound"]
            )
            sharp = int(row["floating_point_sharp_support_lower_bound"])
            self.assertLessEqual(certified, sharp)

    def test_frozen_corpus_and_secp_recorded(self) -> None:
        self.assertEqual(len(self.result["records"]), 19)
        secp = self.result["records"][-1]
        self.assertEqual(secp["label"], "secp256k1")
        self.assertGreaterEqual(
            secp["certified_odd_divisor_support_lower_bound_bits"],
            127,
        )
        self.assertGreater(
            int(secp["certified_rational_map_degree_lower_bound"]),
            1 << 126,
        )

    def test_result_artifact_is_canonical_json(self) -> None:
        text = barrier.stable_json(self.result)
        parsed = json.loads(text)
        self.assertEqual(parsed["experiment"], barrier.PROFILE_ID)


if __name__ == "__main__":
    unittest.main()
