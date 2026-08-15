#!/usr/bin/env python3
"""Unit tests for UORC-056 C28 nonlinear pole-budget boundary."""
from __future__ import annotations

import unittest

from uorc056_nonlinear_pole_budget import (
    INTERPOLATION_CASES,
    SECP_AB_POLY_DEGREE_LOWER,
    SECP_AB_STATE_POLE_LOWER,
    SECP_HALF,
    RationalFunction,
    build_result,
    compiled_ab_decoder_budget,
    minimum_binary_gate_count,
    parity_interpolation_case,
    rational_budget_controls,
)


class NonlinearPoleBudgetTests(unittest.TestCase):
    def test_finite_parity_controls(self) -> None:
        for field_prime, order in INTERPOLATION_CASES:
            row = parity_interpolation_case(field_prime, order)
            self.assertEqual(row["square_residual_marked_roots"], order - 1)
            self.assertEqual(row["translation_defect_marked_roots"], order - 2)
            self.assertGreaterEqual(
                row["parity_function_pole_degree"], (order - 1) // 2
            )
            self.assertGreaterEqual(row["translation_defect_pole_degree"], order - 2)

    def test_rational_budget_controls(self) -> None:
        row = rational_budget_controls()
        self.assertTrue(row["all_checks_passed"])
        self.assertEqual(row["fields"], 3)
        self.assertEqual(row["exact_budget_checks"], 204)

    def test_ab_decoder_compilation(self) -> None:
        for a, b in ((0, 0), (1, 1), (2, 3), (17, 29)):
            row = compiled_ab_decoder_budget(a, b)
            self.assertEqual(row["decoder_budget"], 4 * a + 3 * b + 9)

    def test_exact_ab_state_threshold(self) -> None:
        delta = SECP_AB_STATE_POLE_LOWER
        self.assertLess(7 * (delta - 1) + 9, SECP_HALF)
        self.assertGreaterEqual(7 * delta + 9, SECP_HALF)
        self.assertEqual(delta.bit_length(), 253)

    def test_exact_ab_polynomial_threshold(self) -> None:
        degree = SECP_AB_POLY_DEGREE_LOWER
        self.assertLess(42 * (degree - 1) + 9, SECP_HALF)
        self.assertGreaterEqual(42 * degree + 9, SECP_HALF)
        self.assertEqual(degree.bit_length(), 250)

    def test_gate_count_boundary(self) -> None:
        expected = {1: 255, 5: 253, 7: 253, 10: 252, 100: 249, 256: 247}
        for initial, gates in expected.items():
            self.assertEqual(minimum_binary_gate_count(SECP_HALF, initial), gates)
            self.assertLess((2 ** (gates - 1)) * initial, SECP_HALF)
            self.assertGreaterEqual((2**gates) * initial, SECP_HALF)

    def test_rational_reduction(self) -> None:
        p = 101
        f = RationalFunction.make([0, 1, 1], [0, 1], p)
        self.assertEqual(list(f.numerator), [1, 1])
        self.assertEqual(list(f.denominator), [1])
        self.assertEqual(f.pole_degree, 1)

    def test_full_result(self) -> None:
        result = build_result()
        self.assertEqual(result["profile_id"], "UORC-056-NONLINEAR-POLE-BUDGET-C28")
        self.assertEqual(len(result["finite_controls"]["cases"]), 5)
        self.assertTrue(result["decision"]["pole_budget_tool_built"])
        self.assertTrue(result["decision"]["translation_defect_bound_proved"])
        self.assertTrue(result["decision"]["low_degree_algebraic_state_blocked"])
        self.assertFalse(result["decision"]["high_degree_low_size_state_blocked"])
        self.assertFalse(result["decision"]["parity_oracle_found"])
        self.assertEqual(len(result["digest"]), 64)


if __name__ == "__main__":
    unittest.main()
