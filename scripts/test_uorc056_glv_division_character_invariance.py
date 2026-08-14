import unittest

import uorc056_glv_division_character_invariance as module


class GlvDivisionCharacterInvarianceTests(unittest.TestCase):
    def test_public_glv_and_monomial_closure(self):
        result = module.run()
        self.assertEqual(
            result["decision"],
            "all_multiplicative_division_polynomial_character_monomials_are_glv_invariant_and_cannot_equal_secp_parity",
        )
        cert = result["public_certificates"]
        self.assertTrue(cert["beta_cube_root"])
        self.assertEqual(cert["chi_beta"], 1)
        self.assertTrue(cert["lambda_even"])
        self.assertTrue(cert["alpha_G_equals_lambda_G"])
        self.assertEqual(result["target_mismatch"]["sigma_G_G"], -1)
        self.assertEqual(result["target_mismatch"]["sigma_G_alpha_G"], 1)
        for row in result["multiplicative_monomial_replay"]["rows"]:
            self.assertTrue(row["invariant"])

    def test_cm_weight_recurrence_cases(self):
        result = module.verify_weight_recurrence()
        self.assertEqual(len(result["odd_residue_cases"]), 3)
        self.assertEqual(len(result["even_residue_cases"]), 3)
        for row in result["odd_residue_cases"] + result["even_residue_cases"]:
            self.assertEqual(row["term1_weight"], row["target"])
            self.assertEqual(row["term2_weight"], row["target"])


if __name__ == "__main__":
    unittest.main()
