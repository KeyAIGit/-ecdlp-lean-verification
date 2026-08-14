import unittest
from pathlib import Path

import uorc056_eds_decimation_closure as module


class EdsDecimationClosureTests(unittest.TestCase):
    def test_exact_theorem_replay(self):
        result = module.run(
            Path("experiments/uorc056/divisor_aware_rational_grammar.json")
        )
        self.assertEqual(
            result["decision"],
            "pure_single_division_polynomial_character_route_closed_for_all_indices",
        )
        replay = result["exact_replay"]
        self.assertGreater(replay["generator_rows_checked"], 0)
        self.assertGreater(replay["q3_generator_rows_checked"], 0)
        self.assertEqual(replay["q3_three_sign_obstruction_violations"], 0)
        bounded = result["bounded_discovery_even_decimation_screen"]
        self.assertGreater(bounded["total_even_classes_tested"], 0)
        self.assertEqual(bounded["exact_candidates"], 0)

    def test_secp_congruence_class(self):
        secp_p = int(
            "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F",
            16,
        )
        self.assertEqual(secp_p % 4, 3)
        self.assertEqual(module.quadratic_character(-1, secp_p), -1)


if __name__ == "__main__":
    unittest.main()
