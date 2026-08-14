#!/usr/bin/env python3
"""Unit tests for the exact UORC-056 toy factory."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import uorc056_toy_factory as u


class PolynomialTests(unittest.TestCase):
    def test_division_round_trip(self) -> None:
        p = 31
        left = [3, 4, 5]
        right = [7, 1]
        product = u.poly_mul(left, right, p)
        quotient, remainder = u.poly_divmod(product, right, p)
        self.assertEqual(quotient, left)
        self.assertEqual(remainder, [0])

    def test_lagrange_basis(self) -> None:
        p = 31
        nodes = [1, 2, 4, 8]
        _, basis = u.lagrange_basis(nodes, p)
        for i, polynomial in enumerate(basis):
            values = [u.poly_eval(polynomial, x, p) for x in nodes]
            self.assertEqual(values, [1 if i == j else 0 for j in range(len(nodes))])


class CurveTests(unittest.TestCase):
    def test_default_instances(self) -> None:
        for instance in u.DEFAULT_INSTANCES:
            instance.validate()
            self.assertIsNone(instance.curve.mul(instance.subgroup_order, instance.generator))


class FixtureTests(unittest.TestCase):
    def test_full_marker_families(self) -> None:
        for instance in u.DEFAULT_INSTANCES:
            fixture = u.build_fixture(instance, include_all_markers=True)
            self.assertEqual(len(fixture["marked_roots"]), instance.subgroup_order - 1)
            self.assertEqual(
                len(fixture["kernel_coefficients_low_to_high"]) - 1,
                (instance.subgroup_order - 1) // 2,
            )
            self.assertTrue(fixture["checks"]["parity_ratio_all_nonzero_scalars"])

    def test_generator_negation_is_global_sign(self) -> None:
        for instance in u.DEFAULT_INSTANCES:
            fixture = u.build_fixture(instance, include_all_markers=True)
            p = instance.curve.p
            root = fixture["marked_roots"]["1"]["coefficients_low_to_high"]
            neg_root = fixture["marked_roots"][str(instance.subgroup_order - 1)]["coefficients_low_to_high"]
            self.assertEqual(u.poly_add(root, neg_root, p), [0])

    def test_deterministic_export_and_check(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            paths = u.write_default_fixtures(directory)
            self.assertEqual(len(paths), len(u.DEFAULT_INSTANCES) + 1)
            manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(len(manifest["fixtures"]), len(u.DEFAULT_INSTANCES))
            first = paths[0].read_text(encoding="utf-8")
            u.write_default_fixtures(directory)
            self.assertEqual(paths[0].read_text(encoding="utf-8"), first)


if __name__ == "__main__":
    unittest.main()
