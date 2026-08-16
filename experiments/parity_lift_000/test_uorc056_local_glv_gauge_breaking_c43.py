import unittest

from uorc056_local_glv_gauge_breaking_c43 import SECP_N, build_payload


class LocalGlvGaugeBreakingC43Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_payload()

    def test_exact_replay_and_boundary(self) -> None:
        aggregate = self.payload["aggregate"]
        self.assertEqual(aggregate["curves"], 9)
        self.assertEqual(aggregate["frozen_curves"], 5)
        self.assertEqual(aggregate["heldout_curves"], 4)
        self.assertEqual(aggregate["carry_value_checks"], 1929)
        self.assertEqual(aggregate["declared_character_atoms"], 22329)
        self.assertEqual(aggregate["valid_character_atoms"], 13145)
        self.assertTrue(aggregate["decisive_p2137_all_targets_absent"])
        self.assertTrue(aggregate["quartic_fits_p229"])
        self.assertTrue(aggregate["quartic_fits_p997"])
        self.assertTrue(aggregate["quartic_fails_p2137"])
        self.assertEqual(aggregate["errors"], 0)

        branch = self.payload["local_glv_branch_factorization"]["aggregate"]
        self.assertTrue(branch["all_kappa_dense"])
        self.assertTrue(branch["all_carry_roots_dense"])

        decision = self.payload["decision"]
        self.assertTrue(decision["exact_glv_carry_root_found"])
        self.assertTrue(decision["exact_sector_root_found"])
        self.assertTrue(decision["exact_oriented_root_reconstruction_found"])
        self.assertTrue(decision["residual_klein_four_gauge_survives"])
        self.assertTrue(decision["declared_structural_glv_dft_character_grammar_closed"])
        self.assertFalse(decision["local_glv_gauge_breaking_evaluator_found"])
        self.assertFalse(decision["cheap_parity_decoder_found"])
        self.assertFalse(decision["parity_oracle_found"])
        self.assertFalse(decision["sub_sqrt_ecdlp_found"])
        self.assertEqual(len(self.payload["digest"]), 64)

    def test_secp256k1_arithmetic(self) -> None:
        frontier = self.payload["secp256k1_frontier"]
        expected_half = (
            57896044618658097711785492504343953926418782139537452191302581570759080747168
        )
        expected_orbits = (
            19298681539552699237261830834781317975472927379845817397100860523586360249056
        )
        self.assertEqual(frontier["n"], SECP_N)
        self.assertEqual(frontier["half_kernel_degree"], expected_half)
        self.assertEqual(frontier["glv_orbits"], expected_orbits)
        self.assertEqual(frontier["glv_orbits_bit_length"], 254)
        self.assertTrue(frontier["half_kernel_equals_three_glv_orbits"])


if __name__ == "__main__":
    unittest.main()
