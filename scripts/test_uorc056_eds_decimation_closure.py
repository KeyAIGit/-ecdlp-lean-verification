import unittest
from pathlib import Path

import uorc056_eds_decimation_closure as module


class EdsDecimationAuditTests(unittest.TestCase):
    def test_exact_small_curve_witnesses_and_secp_status(self):
        result = module.run(
            Path("experiments/uorc056/divisor_aware_rational_grammar.json")
        )
        self.assertEqual(
            result["decision"],
            "even_eds_decimation_exists_on_small_curves_but_is_excluded_for_"
            "secp256k1_by_fourier_and_paley_bounds",
        )
        self.assertEqual(result["schema_version"], "1.3")
        witnesses = result["exact_small_curve_witnesses"]
        self.assertEqual(len(witnesses), 2)
        for row in witnesses:
            self.assertEqual(row["p_mod_4"], 3)
            self.assertEqual(row["chi_minus_one"], -1)
            self.assertEqual(row["rho_m_at_G"], -1)
            self.assertTrue(row["exact_parity_decimation"])
            self.assertEqual(row["decimation_outputs"], row["target_parity"])
            self.assertTrue(row["remarked_row_all_residue"])
            self.assertEqual(row["ward_at_remarked_generator"]["chi_a"], 1)
            self.assertEqual(row["ward_at_remarked_generator"]["chi_b"], -1)
            self.assertTrue(row["specialized_recurrence_exact"])
        self.assertEqual(
            result["bounded_base_discovery_screen"]["exact_candidates"],
            0,
        )
        secp = result["secp256k1_status"]
        self.assertTrue(secp["pure_single_factor_closed"])
        self.assertEqual(
            secp["published_fourier_necessary_condition"],
            "cot(pi/(2n)) <= 6*sqrt(p)",
        )
        self.assertEqual(
            secp["paley_necessary_condition"],
            "((n-1)/2)^2 <= 3p+1",
        )

    def test_secp_congruence_class(self):
        secp_p = int(
            "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F",
            16,
        )
        self.assertEqual(secp_p % 4, 3)
        self.assertEqual(module.quadratic_character(-1, secp_p), -1)


if __name__ == "__main__":
    unittest.main()
