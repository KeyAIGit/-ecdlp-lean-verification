#!/usr/bin/env python3
from __future__ import annotations

import cmath
import json
import math
import unittest
from pathlib import Path

import uorc056_regularized_fourier_divisor_barrier as barrier


class RegularizedFourierDivisorBarrierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.grammar = Path(
            "experiments/uorc056/divisor_aware_rational_grammar.json"
        )
        cls.result = barrier.run(cls.grammar)

    def test_peak_identity(self) -> None:
        for n in (3, 5, 7, 31, 67, 79, 127, 139):
            barrier.verify_peak_identity(n)

    def test_exact_radical_floor(self) -> None:
        for q in (3, 5, 7, 9, 11, 43, 127):
            for numerator in (1, 7, 99, 1000):
                for denominator in (1, 2, 9):
                    exact = barrier.floor_rational_over_sqrt_plus_one(
                        numerator, denominator, q
                    )
                    floating = math.floor(
                        numerator / (denominator * (math.sqrt(q) + 1.0))
                    )
                    self.assertEqual(exact, floating)

    def test_subgroup_character_extension_average(self) -> None:
        # A=Z/15Z, H=<3> has order five.  An arbitrary trace vector on A
        # verifies the exact annihilator expansion of the H-restricted sum.
        order_a = 15
        step = 3
        order_h = 5
        frequency = 2
        values = [complex((x * x + 2 * x + 3) % 7, x % 3) for x in range(order_a)]
        lhs = sum(
            cmath.exp(2j * math.pi * frequency * k / order_h)
            * values[(step * k) % order_a]
            for k in range(order_h)
        )
        # Extension theta(x)=exp(2*pi*i*frequency*x/15) restricts correctly
        # because theta(3k)=exp(2*pi*i*frequency*k/5).  H^perp consists of
        # psi_j(x)=exp(2*pi*i*j*x/3), j=0,1,2.
        rhs = 0j
        for j in range(3):
            rhs += sum(
                cmath.exp(2j * math.pi * frequency * x / order_a)
                * cmath.exp(2j * math.pi * j * x / 3)
                * values[x]
                for x in range(order_a)
            )
        rhs /= 3
        self.assertAlmostEqual(lhs.real, rhs.real, places=10)
        self.assertAlmostEqual(lhs.imag, rhs.imag, places=10)

    def test_certified_bounds_are_not_stronger_than_float_replay(self) -> None:
        for row in self.result["records"][:-1]:
            certified = int(
                row["certified_odd_divisor_support_lower_bound"]
            )
            sharp = int(row["floating_point_sharp_support_lower_bound"])
            self.assertLessEqual(certified, sharp)

    def test_secp256k1_bound(self) -> None:
        secp = self.result["records"][-1]
        self.assertEqual(secp["label"], "secp256k1")
        self.assertEqual(
            secp["certified_odd_divisor_support_lower_bound"],
            "216543324404233567658511113820216134562",
        )
        self.assertGreater(
            int(secp["certified_rational_map_degree_lower_bound"]),
            1 << 126,
        )

    def test_canonical_json(self) -> None:
        parsed = json.loads(barrier.stable_json(self.result))
        self.assertEqual(parsed["experiment"], barrier.PROFILE_ID)


if __name__ == "__main__":
    unittest.main()
