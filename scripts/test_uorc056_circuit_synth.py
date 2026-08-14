#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

import uorc056_circuit_synth as synth


class CircuitSynthTests(unittest.TestCase):
    def test_known_minimum_and_nontransfer(self) -> None:
        result = synth.run(Path("experiments/uorc056/circuit_grammar.json"))
        self.assertEqual(result["minimum_exact_seed"]["weight"], 4)
        self.assertEqual(result["decision"], "finite_nontransfer_seed")
        self.assertLess(
            sum(row["exact"] for row in result["unchanged_integer_formula_transfer"]),
            3,
        )

    def test_semantic_quotient_reduces_forms(self) -> None:
        p, n, generator = synth.FROZEN_CURVES[0]
        valid, reps = synth.semantic_quotient(p, synth.orbit(generator, n, p))
        self.assertLess(len(reps), valid)


if __name__ == "__main__":
    unittest.main()
