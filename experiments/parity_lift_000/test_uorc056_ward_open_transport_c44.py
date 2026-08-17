import unittest

from uorc056_ward_open_transport_c44 import build_payload


class WardOpenTransportC44Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_payload()

    def test_four_class_closure(self) -> None:
        ward = self.payload["ward_character_normal_form"]
        self.assertEqual(ward["chi_A"], 1)
        self.assertEqual(ward["chi_B"], -1)
        self.assertTrue(ward["finite_products_stay_in_four_classes"])
        self.assertEqual(len(ward["classes"]), 4)
        for row in ward["classes"]:
            self.assertTrue(row["neither_global_phase_is_parity"])
            self.assertEqual(set(row["phase_mismatch_witnesses"]), {"-1", "1"})

    def test_corrected_multiplier_arithmetic(self) -> None:
        transport = self.payload["multiplier_transport"]
        self.assertTrue(transport["lambda_equals_power_of_two"])
        self.assertEqual(transport["doubling_glv_cycles"], 32)
        self.assertEqual(transport["one_public_anchor_leaves_free_cycle_signs"], 31)
        self.assertEqual(transport["number_of_residual_anchor_assignments"], 2**31)
        self.assertTrue(transport["seven_pair_action_transitive"])

    def test_claim_boundary(self) -> None:
        decision = self.payload["decision"]
        self.assertTrue(
            decision["ward_period_lattice_multiplicative_character_class_closed"]
        )
        self.assertFalse(
            decision["ward_period_lattice_multiplicative_character_algorithm_found"]
        )
        self.assertFalse(decision["public_ordered_sector_evaluator_found"])
        self.assertFalse(decision["parity_oracle_found"])
        self.assertFalse(decision["sub_sqrt_ecdlp_found"])
        self.assertEqual(len(self.payload["digest"]), 64)


if __name__ == "__main__":
    unittest.main()
