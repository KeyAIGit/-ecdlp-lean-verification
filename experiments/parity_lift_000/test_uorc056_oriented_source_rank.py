#!/usr/bin/env python3
"""Unit tests for UORC-056 C31 oriented source rank."""
from __future__ import annotations

import unittest

from uorc056_oriented_source_rank import (
    INSTANCES,
    SECP_N,
    auxiliary_fourier_certificate,
    full_sign_source_matrix,
    oriented_source_matrix,
    parity_sign,
    rank_mod,
    run,
    secp_record,
    sign_source_matrix,
)


class OrientedSourceRankTests(unittest.TestCase):
    def test_parity_negation(self) -> None:
        for n in (5, 7, 11, 31):
            for value in range(1, n):
                self.assertEqual(parity_sign(n - value, n), -parity_sign(value, n))

    def test_small_matrix_rank(self) -> None:
        matrix = sign_source_matrix(7)
        self.assertEqual(rank_mod(matrix, 43), 3)
        self.assertEqual(len(matrix), 3)
        self.assertEqual(len(matrix[0]), 3)

    def test_full_rows_have_same_rank(self) -> None:
        for n, modulus in ((7, 43), (11, 47), (13, 53)):
            m = (n - 1) // 2
            self.assertEqual(rank_mod(sign_source_matrix(n), modulus), m)
            self.assertEqual(rank_mod(full_sign_source_matrix(n), modulus), m)

    def test_column_scaling_preserves_frozen_rank(self) -> None:
        for instance in INSTANCES:
            m = (instance.n - 1) // 2
            self.assertEqual(rank_mod(sign_source_matrix(instance.n), instance.curve.p), m)
            self.assertEqual(rank_mod(oriented_source_matrix(instance), instance.curve.p), m)

    def test_auxiliary_fourier_support(self) -> None:
        for n in (7, 11, 13, 19):
            row = auxiliary_fourier_certificate(n)
            self.assertTrue(row["support_pattern_exact"])
            self.assertEqual(row["zero_even_character_frequencies"], (n - 1) // 2)
            self.assertEqual(row["nonzero_odd_character_frequencies"], (n - 1) // 2)

    def test_secp_arithmetic(self) -> None:
        row = secp_record()
        self.assertEqual(row["n"], SECP_N)
        self.assertEqual(row["half_kernel_dimension"], (SECP_N - 1) // 2)
        self.assertTrue(row["characteristic_zero_fixed_dictionary_lower_bound_exceeds_2_pow_254"])
        self.assertTrue(row["characteristic_zero_fixed_dictionary_lower_bound_below_2_pow_255"])
        self.assertFalse(row["secp_base_field_source_rank_certified_by_this_package"])

    def test_full_replay(self) -> None:
        result = run()
        replay = result["exact_replay"]
        self.assertEqual(replay["curves"], 5)
        self.assertEqual(replay["half_kernel_dimensions_sum"], 219)
        self.assertEqual(replay["half_source_entries_checked"], 11565)
        self.assertEqual(replay["all_marker_source_entries_checked"], 23130)
        self.assertEqual(replay["full_rank_curves"], 5)
        decision = result["decision"]
        self.assertTrue(decision["characteristic_zero_half_source_rank_exact"])
        self.assertTrue(decision["frozen_base_field_half_source_rank_full"])
        self.assertFalse(decision["secp_base_field_half_source_rank_proved"])
        self.assertFalse(decision["parity_oracle_found"])


if __name__ == "__main__":
    unittest.main()
