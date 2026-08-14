#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import uorc056_division_polynomial_frontier as frontier


DISCOVERY = [
    {"p": 43, "n": 31, "G": [2, 12]},
    {"p": 67, "n": 79, "G": [2, 22]},
    {"p": 79, "n": 67, "G": [1, 18]},
    {"p": 127, "n": 127, "G": [1, 32]},
    {"p": 163, "n": 139, "G": [2, 34]},
]
HOLDOUT = [
    {"p": 61, "n": 61, "G": [2, 25]},
    {"p": 211, "n": 199, "G": [3, 33]},
]


class DivisionPolynomialFrontierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.grammar = Path(cls.temporary.name) / "grammar.json"
        cls.grammar.write_text(
            json.dumps(
                {
                    "discovery_corpus": DISCOVERY,
                    "holdout_corpus": HOLDOUT,
                }
            ),
            encoding="utf-8",
        )
        cls.result = frontier.run(cls.grammar, 4096)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_division_support_formula(self) -> None:
        self.assertEqual(frontier.division_polynomial_odd_support(3), 8)
        self.assertEqual(frontier.division_polynomial_odd_support(4), 16)
        self.assertEqual(frontier.division_polynomial_odd_support(9), 80)

    def test_miller_support_never_exceeds_two(self) -> None:
        for index in range(1, 100):
            self.assertEqual(frontier.miller_odd_support_upper_bound(index), 2)

    def test_composition_and_negation_on_frozen_curves(self) -> None:
        for row in DISCOVERY:
            curve = frontier.parse_curve(row)
            frontier.verify_composition_identity(curve)
            frontier.verify_negation_law(curve)

    def test_exact_support_threshold_and_small_DAG(self) -> None:
        separation = self.result["support_to_cost_separation"]
        self.assertEqual(
            separation["minimum_even_division_index_meeting_support"],
            "14715411119103453974",
        )
        self.assertEqual(separation["minimum_even_index_bit_length"], 64)
        self.assertEqual(
            separation["recurrence_DAG"]["dependency_nodes"],
            483,
        )
        self.assertEqual(
            separation["recurrence_DAG"]["nonbase_recurrence_nodes"],
            479,
        )
        index = int(separation["minimum_even_division_index_meeting_support"])
        self.assertGreaterEqual(
            frontier.division_polynomial_odd_support(index),
            frontier.SECP_V8_SUPPORT_LOWER_BOUND,
        )

    def test_discovery_screen_is_frozen_negative(self) -> None:
        screen = self.result["bounded_discovery_screen"]
        self.assertEqual(screen["even_indices_tested"], 2048)
        self.assertEqual(screen["everywhere_defined_indices"], 1897)
        self.assertEqual(screen["total_nonzero_points"], 438)
        self.assertEqual(screen["exact_candidates"], [])
        self.assertEqual(screen["best"]["index"], 884)
        self.assertEqual(screen["best"]["matches"], 272)
        self.assertEqual(screen["best"]["output_phase"], 1)
        self.assertTrue(
            all(not row["exact_candidates"] for row in screen["per_curve"])
        )

    def test_radical_threshold_is_minimal_even(self) -> None:
        required = frontier.SECP_V8_SUPPORT_LOWER_BOUND
        index = frontier.minimum_even_index_for_support(required)
        self.assertEqual(index % 2, 0)
        self.assertGreaterEqual(index * index, required)
        self.assertLess((index - 2) * (index - 2), required)

    def test_mixed_mod_four_holdout(self) -> None:
        observation = self.result["holdout_observation"]
        self.assertTrue(observation["contains_q_1_mod_4"])
        self.assertTrue(observation["contains_q_3_mod_4"])

    def test_canonical_json(self) -> None:
        parsed = json.loads(frontier.stable_json(self.result))
        self.assertEqual(parsed["experiment"], frontier.PROFILE_ID)


if __name__ == "__main__":
    unittest.main()
