#!/usr/bin/env python3
"""Unit tests for UORC-056 V19 direct shared parity Cauchy barriers."""
from __future__ import annotations

import unittest

from uorc056_shared_parity_cauchy_barrier import (
    EXHAUSTIVE_CAUCHY_ORDERS,
    FROZEN_INSTANCES,
    SECP256K1_N,
    bilinear_leaf_sum_bound,
    cycle_record,
    pair_sum_cover_bound,
    run,
    secp256k1_record,
    verify_exhaustive_cauchy_minors,
)


class SharedParityCauchyBarrierTests(unittest.TestCase):
    def test_pair_sum_cover_bound_is_minimal(self) -> None:
        for target in (1, 2, 3, 4, 5, 30, 66, 78, 126, 138, 251):
            bound = pair_sum_cover_bound(target)
            self.assertGreaterEqual(bound * (bound + 1) // 2, target)
            if bound > 0:
                self.assertLess((bound - 1) * bound // 2, target)

    def test_bilinear_leaf_sum_bound_is_minimal(self) -> None:
        for target in (1, 2, 3, 5, 7, 30, 66, 78, 126, 138, 251):
            bound = bilinear_leaf_sum_bound(target)
            self.assertGreaterEqual(
                (bound // 2) * ((bound + 1) // 2), target
            )
            if bound > 0:
                previous = bound - 1
                self.assertLess(
                    (previous // 2) * ((previous + 1) // 2), target
                )

    def test_exhaustive_cauchy_full_spark_replay(self) -> None:
        expected = {5: 461, 7: 6434}
        for order in EXHAUSTIVE_CAUCHY_ORDERS:
            row = verify_exhaustive_cauchy_minors(order)
            self.assertEqual(row["minors_checked"], expected[order])
            self.assertEqual(row["failures"], 0)

    def test_frozen_cycle_exact_witnesses(self) -> None:
        for instance_id, field_prime, order in FROZEN_INSTANCES:
            row = cycle_record(instance_id, field_prime, order)
            self.assertEqual(row["canonical_parity_spectrum_support"], order)
            self.assertEqual(row["free_identity_parity_support"], order - 1)
            self.assertEqual(row["extremal_rational_total_support"], order)
            self.assertEqual(
                row["direct_rational_shared_union_lower_bound"],
                (order + 1) // 2,
            )
            self.assertEqual(row["sampled_cauchy"]["failures"], 0)

    def test_fixed_secp256k1_bounds(self) -> None:
        row = secp256k1_record()
        self.assertEqual(row["n"], SECP256K1_N)
        self.assertEqual(
            row["direct_parity_spectrum_support_with_free_identity_lower_bound"],
            SECP256K1_N - 1,
        )
        self.assertEqual(
            row["direct_sparse_rational_separate_support_lower_bound"],
            SECP256K1_N,
        )
        self.assertEqual(
            row["direct_sparse_rational_shared_union_lower_bound"],
            57896044618658097711785492504343953926418782139537452191302581570759080747169,
        )
        self.assertEqual(
            row["bilinear_leaf_sum_lower_bound"],
            680564733841876926926749214863536422911,
        )
        self.assertEqual(
            row["bilinear_shared_dictionary_lower_bound"],
            481231938336009023090067544955250113853,
        )
        self.assertEqual(row["bilinear_leaf_sum_gap_below_2_pow_129"], 1)
        self.assertEqual(
            row["direct_sparse_rational_shared_union_lower_bound_bit_length"],
            255,
        )

    def test_full_result_contract(self) -> None:
        result = run()
        replay = result["finite_field_replay"]
        self.assertEqual(result["profile_id"], "UORC-056-SHARED-PARITY-CAUCHY-BARRIER-V19")
        self.assertEqual(replay["exhaustive_cauchy_minors"], 6895)
        self.assertEqual(replay["sampled_cauchy_minors_on_frozen_orders"], 160)
        self.assertEqual(replay["canonical_and_free_identity_DFT_checks"], 5)
        self.assertEqual(replay["failures"], 0)
        self.assertEqual(len(result["closed_classes"]), 2)


if __name__ == "__main__":
    unittest.main()
