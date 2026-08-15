#!/usr/bin/env python3
"""Unit tests for UORC-056 C31A secp source defect."""
from __future__ import annotations

import unittest

from uorc056_secp_source_defect import (
    SECP_N,
    SECP_P,
    exact_order_prime_modulus,
    rank_mod,
    run,
    secp_certificate,
    sign_matrix,
    small_witnesses,
)


class SecpSourceDefectTests(unittest.TestCase):
    def test_exact_secp_orders(self) -> None:
        half = (SECP_N - 1) // 2
        order_n, _ = exact_order_prime_modulus(2, SECP_N)
        order_p, _ = exact_order_prime_modulus(2, SECP_P)
        self.assertEqual(order_n, half)
        self.assertEqual(order_p, half)

    def test_quarter_power_is_minus_one(self) -> None:
        quarter = (SECP_N - 1) // 4
        self.assertEqual(pow(2, quarter, SECP_N), SECP_N - 1)
        self.assertEqual(pow(2, quarter, SECP_P), SECP_P - 1)

    def test_small_forced_defect(self) -> None:
        for row in small_witnesses():
            self.assertGreaterEqual(row["nullity"], 2)

    def test_direct_small_matrix(self) -> None:
        matrix = sign_matrix(11)
        self.assertEqual(len(matrix), 5)
        self.assertEqual(rank_mod(matrix, 23), 3)

    def test_secp_certificate(self) -> None:
        row = secp_certificate()
        self.assertTrue(row["orders_equal_half_dimension"])
        self.assertEqual(row["evaluation_map_kernel_size"], 2)
        self.assertEqual(row["forced_zero_eigenvalues"], 2)
        self.assertEqual(row["half_source_nullity_lower_bound"], 2)
        self.assertFalse(row["exact_nullity_proved"])

    def test_full_replay(self) -> None:
        result = run()
        decision = result["decision"]
        self.assertTrue(decision["secp_base_field_rank_defect_proved"])
        self.assertFalse(decision["secp_base_field_full_rank"])
        self.assertFalse(decision["secp_base_field_exact_rank_proved"])
        self.assertEqual(decision["fixed_dictionary_dimension_reduction_found"], 2)
        self.assertFalse(decision["subroot_fixed_dictionary_found"])
        self.assertFalse(decision["parity_oracle_found"])


if __name__ == "__main__":
    unittest.main()
