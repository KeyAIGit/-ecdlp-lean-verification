#!/usr/bin/env python3
"""Unit tests for UORC-056 V18 sparse rational spectral barrier."""
from __future__ import annotations

import unittest

from uorc056_sector_sparse_rational_spectral_barrier import (
    SECP256K1_N,
    pair_sum_cover_bound,
    run,
    secp256k1_record,
    square_exact_uncertainty_bounds,
)


class SectorSparseRationalSpectralBarrierTests(unittest.TestCase):
    def test_pair_cover_bound_is_minimal(self) -> None:
        for target in (1, 2, 3, 31, 67, 79, 127, 139, 251):
            bound = pair_sum_cover_bound(target)
            self.assertGreaterEqual(
                bound * (bound + 1) // 2, target
            )
            if bound > 0:
                self.assertLess(
                    (bound - 1) * bound // 2, target
                )

    def test_square_exact_transfer(self) -> None:
        row = square_exact_uncertainty_bounds(31, 6)
        self.assertEqual(row["nonzero_plus_scalars"], 18)
        self.assertEqual(row["nonzero_minus_scalars"], 12)
        self.assertEqual(
            row["A_minus_B_frequency_union_lower_bound"], 19
        )
        self.assertEqual(
            row["A_plus_B_frequency_union_lower_bound"], 13
        )
        self.assertEqual(
            row["square_exact_frequency_union_lower_bound"], 19
        )

    def test_fixed_secp256k1_bounds(self) -> None:
        row = secp256k1_record()
        root_bound = (
            481231938336009023090067544955250113853
        )
        square_exact = (
            57896044618658097711785492504343953926418782139537452191302581570759080747273
        )
        self.assertEqual(row["n"], SECP256K1_N)
        self.assertEqual(
            row["H_nonzero_frequency_union_lower_bound"],
            root_bound,
        )
        self.assertEqual(
            row["universal_sparse_rational_frequency_union_lower_bound"],
            root_bound,
        )
        self.assertEqual(
            row["square_exact_frequency_union_lower_bound"],
            square_exact,
        )
        self.assertEqual(row["H_nonzero_lower_bound_bit_length"], 129)
        self.assertTrue(row["universal_lower_bound_exceeds_2_pow_128"])
        self.assertTrue(row["universal_lower_bound_below_2_pow_129"])
        self.assertGreaterEqual(
            root_bound * (root_bound + 1) // 2,
            SECP256K1_N,
        )
        self.assertLess(
            (root_bound - 1) * root_bound // 2,
            SECP256K1_N,
        )

    def test_full_frozen_arithmetic_replay(self) -> None:
        result = run()
        replay = result["exact_toy_arithmetic_replay"]
        self.assertEqual(replay["curves"], 5)
        self.assertTrue(replay["all_root_bounds_minimal"])
        self.assertTrue(replay["all_square_exact_bounds_stronger"])
        for row in replay["curve_rows"]:
            self.assertEqual(
                row["nonzero_plus_scalars"]
                + row["nonzero_minus_scalars"],
                row["n"] - 1,
            )
            self.assertGreater(
                row["square_exact_frequency_union_lower_bound"],
                row["H_nonzero_frequency_union_lower_bound"],
            )


if __name__ == "__main__":
    unittest.main()
