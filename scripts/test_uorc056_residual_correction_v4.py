#!/usr/bin/env python3
from __future__ import annotations

import unittest

import uorc056_residual_correction_v4 as residual
import uorc056_transfer_synth_v2 as base


class ResidualCorrectionV4Tests(unittest.TestCase):
    def test_sign_atom_indices_cancel_modulo_two(self) -> None:
        self.assertEqual(
            residual.symmetric_difference_indices((1, 2, 3), (2, 4), (4, 5)),
            (1, 3, 5),
        )

    def test_exact_single_and_pair_corrections_are_found(self) -> None:
        pool = (
            base.PoolEntry(atom_index=10, vector=0b0011),
            base.PoolEntry(atom_index=11, vector=0b0101),
            base.PoolEntry(atom_index=12, vector=0b1001),
        )
        single = residual.search_corrections(pool, 0b0011)
        self.assertIn((10,), single.exact)
        pair = residual.search_corrections(pool, 0b1100)
        self.assertIn((11, 12), pair.exact)

    def test_action_disagreement_is_zero_for_invariant_pattern(self) -> None:
        order = 7
        all_zero = 0
        self.assertEqual(residual.action_disagreement(all_zero, -1, order), 0)
        self.assertEqual(residual.action_disagreement(all_zero, 2, order), 0)

    def test_action_disagreement_detects_noninvariance(self) -> None:
        # Error only at k=1 in an order-7 group.
        bits = 1 << 0
        self.assertGreater(residual.action_disagreement(bits, -1, 7), 0)
        self.assertGreater(residual.action_disagreement(bits, 2, 7), 0)

    def test_modular_predictor_reports_a_valid_accuracy(self) -> None:
        row = residual.residue_class_predictor(0b001010, order=7)
        self.assertGreaterEqual(row["accuracy"], 0.0)
        self.assertLessEqual(row["accuracy"], 1.0)
        self.assertGreaterEqual(row["modulus"], 2)
        self.assertLessEqual(row["modulus"], 16)

    def test_frozen_glv_lambda_is_nonzero(self) -> None:
        for curve in base.FROZEN_CURVES:
            context = base.build_context(*curve)
            value = residual.glv_lambda(context)
            self.assertGreater(value, 0)
            self.assertLess(value, context.order)


if __name__ == "__main__":
    unittest.main()
