#!/usr/bin/env python3
"""Unit tests for UORC-056 V17 sparse spectral sector barrier."""
from __future__ import annotations

import unittest

from uorc056_sector_sparse_spectral_barrier import (
    SECP256K1_N,
    additive_basis,
    pair_sum_cover_lower_bound,
    run,
    secp256k1_record,
    sumset,
)


class SectorSparseSpectralBarrierTests(unittest.TestCase):
    def test_pair_cover_bound_is_minimal(self) -> None:
        for order in (3, 5, 7, 31, 67, 79, 127, 139):
            bound = pair_sum_cover_lower_bound(order)
            self.assertGreaterEqual(
                bound * (bound + 1) // 2, order - 1
            )
            if bound > 0:
                self.assertLess(
                    (bound - 1) * bound // 2, order - 1
                )

    def test_deterministic_pair_basis(self) -> None:
        for order in (3, 5, 7, 31, 67, 79, 127, 139, 251):
            basis = additive_basis(order)
            self.assertEqual(len(sumset(basis, order)), order)

    def test_fixed_secp256k1_bound(self) -> None:
        record = secp256k1_record()
        lower_bound = (
            481231938336009023090067544955250113853
        )
        self.assertEqual(record["n"], SECP256K1_N)
        self.assertEqual(
            record["nonzero_domain_sparse_frequency_lower_bound"],
            lower_bound,
        )
        self.assertEqual(record["canonical_binary_extension_dc_sum"], 209)
        self.assertEqual(
            record["canonical_binary_extension_fourier_support"],
            SECP256K1_N,
        )
        self.assertEqual(record["lower_bound_bit_length"], 129)
        self.assertTrue(record["lower_bound_exceeds_2_pow_128"])
        self.assertTrue(record["lower_bound_below_2_pow_129"])
        self.assertEqual(
            record["support_only_pair_basis_block"], 2**128
        )
        self.assertEqual(
            record["support_only_pair_basis_size_upper_bound"],
            2**129 - 1,
        )
        self.assertGreaterEqual(
            lower_bound * (lower_bound + 1) // 2,
            SECP256K1_N - 1,
        )
        self.assertLess(
            (lower_bound - 1) * lower_bound // 2,
            SECP256K1_N - 1,
        )

    def test_full_frozen_replay(self) -> None:
        result = run()
        replay = result["exact_toy_replay"]
        self.assertEqual(replay["curves"], 5)
        self.assertEqual(replay["nonzero_scalars"], 438)
        self.assertTrue(
            replay["all_sequences_binary_even_nonconstant"]
        )
        self.assertTrue(
            replay["all_canonical_circulants_full_rank_mod_prime"]
        )
        self.assertTrue(
            replay["all_pair_basis_constructions_cover"]
        )
        for row in replay["curve_rows"]:
            self.assertEqual(row["rank_certificate_gcd_degree"], 0)
            self.assertTrue(row["pair_basis_covers_group"])
            self.assertGreater(row["nonzero_plus_count"], 0)
            self.assertGreater(row["nonzero_minus_count"], 0)
            self.assertEqual(
                row["canonical_full_cycle_sum"],
                1 + row["nonzero_sector_sum"],
            )


if __name__ == "__main__":
    unittest.main()
