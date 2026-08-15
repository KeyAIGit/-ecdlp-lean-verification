#!/usr/bin/env python3
"""Unit tests for UORC-056 autonomous state rigidity C29."""
from __future__ import annotations

import unittest

from uorc056_autonomous_state_rigidity import (
    INTERPOLATION_ORDERS,
    SECP_N,
    SECP_P,
    autonomous_state_orbit,
    finite_cycle_interpolation,
    parity_minimal_cyclic_period,
    parity_shift_collision,
    pgl2_order,
    run,
    state_decoder_conflict,
)


class AutonomousStateRigidityTests(unittest.TestCase):
    def test_parity_has_full_cyclic_period(self) -> None:
        for order in INTERPOLATION_ORDERS:
            self.assertEqual(parity_minimal_cyclic_period(order), order)
            for shift in range(1, order):
                self.assertIsNotNone(parity_shift_collision(order, shift))

    def test_two_state_parity_update_conflicts(self) -> None:
        for order in INTERPOLATION_ORDERS:
            values = [1 if index % 2 == 0 else -1 for index in range(order)]
            successors = {1: set(), -1: set()}
            for index, value in enumerate(values):
                successors[value].add(values[(index + 1) % order])
            self.assertEqual(successors[1], {-1, 1})
            self.assertEqual(successors[-1], {1})

    def test_faithful_cycle_has_n_states(self) -> None:
        for order in INTERPOLATION_ORDERS:
            transition = [(index + 1) % order for index in range(order)]
            orbit = autonomous_state_orbit(transition, 0, order)
            self.assertEqual(len(set(orbit)), order)
            outputs = [1 if index % 2 == 0 else -1 for index in orbit]
            self.assertIsNone(state_decoder_conflict(orbit, outputs))

    def test_finite_cycle_interpolation(self) -> None:
        for order in INTERPOLATION_ORDERS:
            row = finite_cycle_interpolation(order)
            self.assertTrue(row["all_cycle_edges_verified"])
            self.assertLessEqual(row["interpolated_degree"], order - 1)
            self.assertGreaterEqual(row["coefficient_slots"], order - 1)

    def test_secp_pgl2_coprime(self) -> None:
        self.assertEqual(math_gcd(SECP_N, pgl2_order(SECP_P)), 1)

    def test_full_replay(self) -> None:
        result = run()
        self.assertTrue(
            result["decision"]["faithful_n_phase_required_for_autonomous_state"]
        )
        self.assertTrue(
            result["decision"]["global_genus_zero_autonomous_state_excluded"]
        )
        self.assertFalse(result["decision"]["parity_oracle_found"])
        self.assertFalse(result["decision"]["sub_sqrt_ecdlp_found"])


def math_gcd(left: int, right: int) -> int:
    while right:
        left, right = right, left % right
    return abs(left)


if __name__ == "__main__":
    unittest.main()
