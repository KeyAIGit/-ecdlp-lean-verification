#!/usr/bin/env python3
"""Unit tests for UORC-056 V16 sector-factor reconciliation."""
from __future__ import annotations

import math
import unittest

from uorc056_sector_factor_reconciliation import (
    SECP256K1_LAMBDA,
    SECP256K1_N,
    diagnostic_floor_sum_replay,
    parity_correlation_certificate,
    parity_correlation_direct,
    run,
    secp256k1_record,
)


class SectorFactorReconciliationTests(unittest.TestCase):
    def test_floor_sum_certificate_on_small_odd_moduli(self) -> None:
        diagnostic = diagnostic_floor_sum_replay(limit=63)
        self.assertTrue(diagnostic["all_passed"])
        for n in range(3, 64, 2):
            for multiplier in range(1, n):
                if math.gcd(n, multiplier) != 1:
                    continue
                self.assertEqual(
                    parity_correlation_certificate(n, multiplier)["correlation"],
                    parity_correlation_direct(n, multiplier),
                )

    def test_fixed_secp256k1_certificate(self) -> None:
        record = secp256k1_record()
        self.assertEqual(record["n"], SECP256K1_N)
        self.assertEqual(record["lambda"], SECP256K1_LAMBDA)
        self.assertEqual(
            record["sector_parity_correlation_all_nonzero_scalars"], 208
        )
        self.assertEqual(record["floor_sum_A1_euclidean_rounds"], 141)
        self.assertEqual(record["floor_sum_A2_euclidean_rounds"], 143)
        self.assertEqual(
            record["sector_plus_factor_degree"],
            28948022309329048855892746252171976963209391069768726095651290785379540373636,
        )
        self.assertEqual(
            record["sector_minus_factor_degree"],
            28948022309329048855892746252171976963209391069768726095651290785379540373532,
        )
        self.assertEqual(record["lower_bound_bit_length"], 254)
        self.assertEqual(
            record["direct_field_valued_rational_minimum_degree"],
            record["sector_plus_factor_degree"],
        )

    def test_full_frozen_replay(self) -> None:
        result = run()
        replay = result["exact_toy_replay"]
        self.assertEqual(replay["curves"], 5)
        self.assertEqual(replay["marked_roots"], 438)
        self.assertEqual(replay["kummer_evaluations"], 23130)
        self.assertEqual(replay["scalar_reconciliation_checks"], 46260)
        self.assertEqual(
            replay["aggregate_sector_plus_evaluations"], 11742
        )
        self.assertEqual(
            replay["aggregate_sector_minus_evaluations"], 11388
        )
        self.assertTrue(
            replay["all_canonical_sector_polynomial_degrees_maximal"]
        )
        for row in replay["curve_rows"]:
            self.assertEqual(
                row["canonical_sector_polynomial_degree"],
                row["kernel_degree"] - 1,
            )
            self.assertEqual(
                row["sector_plus_factor_degree"]
                + row["sector_minus_factor_degree"],
                row["kernel_degree"],
            )
            self.assertEqual(
                row["optimal_direct_rational_degree"],
                max(
                    row["sector_plus_factor_degree"],
                    row["sector_minus_factor_degree"],
                ),
            )


if __name__ == "__main__":
    unittest.main()
