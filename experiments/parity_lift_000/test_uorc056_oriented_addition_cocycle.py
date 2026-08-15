from __future__ import annotations

import unittest

from uorc056_oriented_addition_cocycle import (
    DIAGNOSTIC_ORDERS,
    GAUGE_ENUMERATION_ORDERS,
    INSTANCES,
    all_sign_gauges,
    build_payload,
    carry,
    carry_from_sigma,
    carry_matrix,
    expected_full_determinant,
    expected_nonzero_determinant,
    matrix_rank_mod,
    parity_linear_coefficients,
    selected_product_matches_parity,
    sigma,
)


class OrientedAdditionCocycleTests(unittest.TestCase):
    def test_carry_is_sigma_coboundary(self) -> None:
        for order in DIAGNOSTIC_ORDERS:
            for left in range(order):
                for right in range(order):
                    self.assertEqual(
                        carry(left, right, order),
                        carry_from_sigma(left, right, order),
                    )

    def test_public_halving_reduces_parity_to_diagonal_carry(self) -> None:
        for order in DIAGNOSTIC_ORDERS:
            inverse_two = pow(2, -1, order)
            for value in range(order):
                half = inverse_two * value % order
                self.assertEqual(carry(half, half, order), sigma(value, order))

    def test_cocycle_identity(self) -> None:
        for order in (3, 5, 7, 11):
            for left in range(order):
                for middle in range(order):
                    for right in range(order):
                        self.assertEqual(
                            carry(left, middle, order)
                            * carry(left + middle, right, order),
                            carry(middle, right, order)
                            * carry(left, middle + right, order),
                        )

    def test_binary_gauge_is_unique(self) -> None:
        for order in GAUGE_ENUMERATION_ORDERS:
            solutions = all_sign_gauges(order)
            expected = tuple(sigma(value, order) for value in range(order))
            self.assertEqual(solutions, [expected])

    def test_carry_matrix_has_full_rank(self) -> None:
        for instance in INSTANCES:
            full = carry_matrix(instance.n)
            nonzero = carry_matrix(instance.n, nonzero_only=True)
            self.assertEqual(matrix_rank_mod(full, instance.curve.p), instance.n)
            self.assertEqual(
                matrix_rank_mod(nonzero, instance.curve.p),
                instance.n - 1,
            )
            self.assertNotEqual(expected_full_determinant(instance.n) % instance.curve.p, 0)
            self.assertNotEqual(expected_nonzero_determinant(instance.n) % instance.curve.p, 0)

    def test_unique_linear_and_multiplicative_integrations(self) -> None:
        for order in DIAGNOSTIC_ORDERS:
            coefficients = parity_linear_coefficients(order)
            self.assertTrue(all(value != 0 for value in coefficients))
            for scalar in range(order):
                self.assertEqual(
                    sum(
                        coefficients[jump] * carry(scalar, jump, order)
                        for jump in range(order)
                    ),
                    sigma(scalar, order),
                )
            self.assertTrue(
                selected_product_matches_parity(order, range(1, order))
            )

    def test_full_replay(self) -> None:
        payload = build_payload()
        aggregate = payload["aggregate"]
        decision = payload["decision"]
        self.assertEqual(payload["profile_id"], "UORC-056-ORIENTED-ADDITION-COCYCLE-C33")
        self.assertEqual(aggregate["errors"], 0)
        self.assertEqual(aggregate["marked_generators"], 438)
        self.assertEqual(aggregate["query_halving_checks"], 46260)
        self.assertGreater(aggregate["frozen_oriented_addition_checks"], 5_000_000)
        self.assertTrue(aggregate["all_frozen_carry_matrices_full_rank"])
        self.assertTrue(decision["exact_lifted_addition_law_found"])
        self.assertTrue(decision["doubling_carry_is_parity_complete"])
        self.assertFalse(decision["nonlocal_propagation_law_found"])
        self.assertFalse(decision["parity_oracle_found"])
        self.assertFalse(decision["sub_sqrt_ecdlp_found"])
        self.assertEqual(len(payload["digest"]), 64)


if __name__ == "__main__":
    unittest.main()
