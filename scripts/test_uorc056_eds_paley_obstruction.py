from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import uorc056_eds_paley_obstruction as v10


class EDSPaleyObstructionTests(unittest.TestCase):
    def test_phase_normalization(self) -> None:
        rows = v10.phase_normalization_truth_table()
        self.assertEqual(len(rows), 4)
        self.assertTrue(
            all(row["chi_psi_k_at_phase_normalized_R"] == 1 for row in rows)
        )

    def test_small_curve_difference_and_paley_replays(self) -> None:
        curve = (43, 31, (2, 12))
        self.assertEqual(v10.verify_composition_identity(curve), 63)
        self.assertEqual(v10.verify_difference_identity(curve), 105)
        self.assertEqual(v10.verify_paley_correlation(43), -1)

    def test_frozen_result(self) -> None:
        grammar = Path("experiments/uorc056/eds_paley_obstruction_grammar.json")
        result = v10.run(grammar)
        self.assertEqual(
            result["decision"],
            "all_single_pure_division_polynomial_character_evaluators_closed_"
            "on_the_18_curve_corpus_and_secp256k1",
        )
        self.assertEqual(result["corpus"]["total_curves"], 18)
        self.assertEqual(result["corpus"]["unresolved_curves"], 0)
        self.assertTrue(result["secp256k1"]["excluded"])
        self.assertGreater(
            int(result["secp256k1"]["strict_margin"]),
            0,
        )

    def test_committed_artifact_matches(self) -> None:
        grammar = Path("experiments/uorc056/eds_paley_obstruction_grammar.json")
        artifact = Path("experiments/uorc056/eds_paley_obstruction_results.json")
        expected = v10.stable_json(v10.run(grammar))
        self.assertEqual(artifact.read_text(encoding="utf-8"), expected)
        parsed = json.loads(expected)
        self.assertEqual(parsed["corpus"]["q_3_mod_4_closed_by_paley"], 11)


if __name__ == "__main__":
    unittest.main()
