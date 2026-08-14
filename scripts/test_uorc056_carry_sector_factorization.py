#!/usr/bin/env python3
"""Unit tests for the UORC-056 V15 carry/sector factorization."""
from __future__ import annotations

import unittest

from uorc056_carry_sector_factorization import run, truth_table
from uorc056_toy_factory import DEFAULT_INSTANCES


class CarrySectorFactorizationTests(unittest.TestCase):
    def test_truth_table_on_every_frozen_field(self) -> None:
        for instance in DEFAULT_INSTANCES:
            with self.subTest(instance=instance.instance_id):
                rows = truth_table(int(instance.cm_beta), instance.curve.p)
                self.assertEqual(
                    [row["branch"] for row in rows],
                    ["uniform", "minority_0", "minority_1", "minority_2"],
                )
                self.assertTrue(
                    all(row["kappas"][0] * row["kappas"][1] * row["kappas"][2] == 1
                        for row in rows)
                )

    def test_full_frozen_replay(self) -> None:
        result = run()
        replay = result["exact_replay"]
        self.assertEqual(replay["curves"], 5)
        self.assertEqual(replay["marked_roots"], 438)
        self.assertEqual(replay["scalar_evaluations"], 46260)
        self.assertEqual(
            replay["branch_counts"],
            {
                "uniform": 12096,
                "minority_0": 11388,
                "minority_1": 11388,
                "minority_2": 11388,
            },
        )
        self.assertEqual(replay["carry_counts"], {"+1": 23130, "-1": 23130})
        self.assertEqual(
            replay["sector_bit_counts"], {"+1": 23484, "-1": 22776}
        )
        self.assertIn(
            "factors_exactly",
            result["decision"],
        )


if __name__ == "__main__":
    unittest.main()
