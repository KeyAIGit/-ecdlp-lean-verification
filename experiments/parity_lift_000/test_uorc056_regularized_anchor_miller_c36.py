#!/usr/bin/env python3
from __future__ import annotations

import math
import unittest

from uorc056_regularized_anchor_miller_c36 import (
    INSTANCES,
    SECP_N,
    SECP_P,
    Curve,
    Fp2,
    base_point,
    build_payload,
    least_nonsquare,
    miller,
    mobius_root_from_kummer,
    trace_zero_twist_point,
    translation_line_gauge,
)


class RegularizedAnchorMillerC36Tests(unittest.TestCase):
    def test_quadratic_field_frobenius(self) -> None:
        p = 43
        d = least_nonsquare(p)
        value = Fp2(7, 11, p, d)
        self.assertEqual(value.frobenius(), value ** p)
        self.assertEqual(value * value.inverse(), Fp2(1, 0, p, d))

    def test_trace_zero_twist(self) -> None:
        instance = INSTANCES[0]
        curve = Curve(instance.p, 0, 7, least_nonsquare(instance.p))
        twist = trace_zero_twist_point(curve)
        self.assertEqual(
            (twist[0].frobenius(), twist[1].frobenius()), curve.neg(twist)
        )
        self.assertTrue(curve.on_curve(twist))

    def test_one_translation_identity(self) -> None:
        instance = INSTANCES[0]
        curve = Curve(instance.p, 0, 7, least_nonsquare(instance.p))
        source = base_point(curve, instance.generator)
        twist = trace_zero_twist_point(curve)
        translation = curve.mul(7, source)
        self.assertIsNotNone(translation)
        shifted = curve.add(twist, translation)
        self.assertIsNotNone(shifted)
        quotient = miller(curve, instance.n, source, shifted) / miller(
            curve, instance.n, source, twist
        )
        gauge = translation_line_gauge(curve, source, translation, twist)
        self.assertEqual(quotient, gauge ** instance.n)

    def test_vertical_boundary_identity(self) -> None:
        instance = INSTANCES[0]
        curve = Curve(instance.p, 0, 7, least_nonsquare(instance.p))
        source = base_point(curve, instance.generator)
        twist = trace_zero_twist_point(curve)
        quotient = miller(curve, instance.n, source, curve.add(twist, source)) / miller(
            curve, instance.n, source, twist
        )
        gauge = translation_line_gauge(curve, source, source, twist)
        self.assertEqual(quotient, gauge ** instance.n)

    def test_mobius_kummer_root(self) -> None:
        instance = INSTANCES[0]
        curve = Curve(instance.p, 0, 7, least_nonsquare(instance.p))
        source = base_point(curve, instance.generator)
        twist = trace_zero_twist_point(curve)
        negative_twist = curve.neg(twist)
        self.assertIsNotNone(negative_twist)
        for scalar in range(1, instance.n):
            translation = curve.mul(scalar, source)
            self.assertIsNotNone(translation)
            direct = translation_line_gauge(
                curve, source, translation, twist
            ) / translation_line_gauge(curve, source, translation, negative_twist)
            closed = mobius_root_from_kummer(
                curve, source, translation, twist, instance.n
            )
            self.assertEqual(direct, closed)

    def test_secp_quadratic_power_map_is_bijective(self) -> None:
        self.assertEqual(math.gcd(SECP_N, SECP_P * SECP_P - 1), 1)
        inverse = pow(SECP_N, -1, SECP_P * SECP_P - 1)
        self.assertEqual((SECP_N * inverse) % (SECP_P * SECP_P - 1), 1)

    def test_full_replay(self) -> None:
        payload = build_payload()
        aggregate = payload["aggregate"]
        self.assertEqual(aggregate["curves"], 5)
        self.assertEqual(aggregate["marked_generators"], 438)
        self.assertEqual(aggregate["public_query_cases"], 46260)
        self.assertEqual(aggregate["shifted_miller_checks"], 46260)
        self.assertEqual(aggregate["unique_root_checks"], 46260)
        self.assertEqual(aggregate["norm_one_checks"], 46260)
        self.assertEqual(aggregate["mobius_kummer_checks"], 46260)
        self.assertEqual(aggregate["errors"], 0)
        decision = payload["decision"]
        self.assertTrue(decision["regularized_shifted_n_miller_evaluator_built"])
        self.assertTrue(
            decision["full_shifted_miller_value_reduced_to_public_line_gauge_power"]
        )
        self.assertTrue(
            decision["twist_norm_one_root_reduced_to_mobius_kummer_coordinate"]
        )
        self.assertFalse(decision["three_carry_field_evaluator_found"])
        self.assertFalse(decision["parity_oracle_found"])


if __name__ == "__main__":
    unittest.main()
