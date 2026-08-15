#!/usr/bin/env python3
"""Unit tests for UORC-056 C30 local branch normal form."""
from __future__ import annotations

import unittest

from uorc056_local_branch_normal_form import (
    INSTANCES,
    QuadraticPair,
    exact_character_masks,
    half_points,
    kernel_poly,
    marked_Y,
    poly_derivative,
    poly_eval,
    run,
    vconst,
    vinv,
    vis_unit,
    vmul,
    vneg,
    vsub,
)


class LocalBranchNormalFormTests(unittest.TestCase):
    def test_pair_multiplication(self) -> None:
        p = 43
        F = (4, 9, 16)
        branch = (2, 3, 4)
        left = QuadraticPair((1, 5, 7), (2, 4, 6))
        right = QuadraticPair((8, 3, 9), (5, 1, 2))
        product = left.mul(right, F, p)
        expected = vmul(left.evaluate(branch, p), right.evaluate(branch, p), p)
        self.assertEqual(product.evaluate(branch, p), expected)

    def test_pair_inverse(self) -> None:
        p = 43
        F = (4, 9, 16)
        one = vconst(1, 3, p)
        zero = vconst(0, 3, p)
        value = QuadraticPair((5, 6, 7), zero)
        inverse = value.inverse(F, p)
        product = value.mul(inverse, F, p)
        self.assertEqual(product.even, one)
        self.assertEqual(product.odd, zero)

    def test_unit_odd_coefficient_recovers_branch(self) -> None:
        p = 43
        branch = (2, 3, 4)
        even = (8, 9, 10)
        odd = (5, 6, 7)
        certificate = QuadraticPair(even, odd).evaluate(branch, p)
        recovered = vmul(vsub(certificate, even, p), vinv(odd, p), p)
        self.assertEqual(recovered, branch)

    def test_nonunit_odd_coefficient_collides(self) -> None:
        p = 43
        branch = (2, 3, 4)
        opposite = vneg(branch, p)
        pair = QuadraticPair((8, 9, 10), (5, 0, 7))
        plus = pair.evaluate(branch, p)
        minus = pair.evaluate(opposite, p)
        self.assertEqual(plus[1], minus[1])
        self.assertNotEqual(plus[0], minus[0])

    def test_kernel_derivative_unit_gauge(self) -> None:
        for instance in INSTANCES:
            points = half_points(instance)
            derivative = poly_derivative(kernel_poly(instance, points), instance.curve.p)
            values = tuple(poly_eval(derivative, x, instance.curve.p) for x, _ in points)
            self.assertTrue(vis_unit(values, instance.curve.p))
            inverse = vinv(values, instance.curve.p)
            for marker in (1, 2, instance.n - 1):
                branch = marked_Y(instance, marker, points)
                self.assertEqual(vmul(inverse, vmul(values, branch, instance.curve.p), instance.curve.p), branch)

    def test_character_mask_solver(self) -> None:
        equations = [([0, 0, 0, 0], 0), ([1, 0, 0, 0], 1)]
        self.assertIn(1, exact_character_masks(equations))
        self.assertEqual(exact_character_masks(equations + [([1, 0, 0, 0], 0)]), [])

    def test_full_replay(self) -> None:
        result = run()
        replay = result["exact_replay"]
        self.assertEqual(replay["curves"], 5)
        self.assertEqual(replay["marked_generators"], 438)
        self.assertEqual(replay["kernel_derivative_gauge_checks"], 23130)
        self.assertEqual(replay["local_character_scalar_checks"], 46260)
        self.assertEqual(replay["local_character_exact_survivors"], 0)
        decision = result["decision"]
        self.assertTrue(decision["quadratic_branch_normal_form_compiler_built"])
        self.assertTrue(decision["kernel_derivative_is_unit_gauge"])
        self.assertFalse(decision["public_oriented_seed_found"])
        self.assertFalse(decision["parity_oracle_found"])


if __name__ == "__main__":
    unittest.main()
