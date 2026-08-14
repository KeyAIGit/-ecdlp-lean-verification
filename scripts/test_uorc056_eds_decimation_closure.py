import unittest
from pathlib import Path

import uorc056_eds_decimation_closure as module


class EdsDecimationAuditTests(unittest.TestCase):
    def test_corrected_audit_and_counterexamples(self):
        result = module.run(
            Path("experiments/uorc056/divisor_aware_rational_grammar.json")
        )
        self.assertEqual(result["decision"], "even_eds_decimation_frontier_remains_open")
        self.assertEqual(len(result["counterexamples"]), 2)
        for row in result["counterexamples"]:
            self.assertEqual(row["p_mod_4"], 3)
            self.assertEqual(row["chi_minus_one"], -1)
            self.assertTrue(row["all_nonzero_terms_are_residues"])
            self.assertEqual(row["ward"]["chi_a"], 1)
            self.assertEqual(row["ward"]["chi_b"], -1)
            self.assertTrue(row["specialized_recurrence_exact"])
        bounded = result["bounded_discovery_even_decimation_screen"]
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
