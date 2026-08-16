from __future__ import annotations

import unittest

from uorc056_anchor_mixed_miller_c35 import build_payload, validate_payload


class AnchorMixedMillerC35Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_payload()
        validate_payload(cls.payload)

    def test_exact_aggregate(self) -> None:
        aggregate = self.payload["aggregate"]
        self.assertEqual(aggregate["twist_shifts"], 520)
        self.assertEqual(aggregate["shift_query_cases"], 54192)
        self.assertEqual(aggregate["normalized_shift_gauge_checks"], 53672)
        self.assertEqual(aggregate["torus_kummer_checks"], 54192)
        self.assertEqual(aggregate["miller_loop_comparisons"], 438)
        self.assertEqual(aggregate["errors"], 0)

    def test_shift_family_character_boundary(self) -> None:
        aggregate = self.payload["aggregate"]
        self.assertEqual(aggregate["quadratic_character_shift_survivors"], 0)
        self.assertEqual(
            aggregate["curves_whose_entire_shift_family_requires_full_torus_order"], 4
        )

    def test_torus_is_centered_kummer(self) -> None:
        for row in self.payload["curve_results"]:
            canonical = row["canonical_shift"]
            self.assertEqual(canonical["distinct_torus_states"], (row["n"] + 1) // 2)
            for fibre in canonical["torus_fibres"]:
                self.assertIn(len(fibre), (1, 2))
                if len(fibre) == 2:
                    self.assertEqual((fibre[0] + fibre[1]) % row["n"], 1)
                    self.assertEqual(fibre[0] % 2, fibre[1] % 2)

    def test_full_state_decoder_is_dense_on_toys(self) -> None:
        for row in self.payload["curve_results"]:
            canonical = row["canonical_shift"]
            self.assertEqual(
                canonical["interpolation_degree"],
                canonical["distinct_full_states"] - 1,
            )
            self.assertEqual(
                canonical["interpolation_nonzero_coefficients"],
                canonical["distinct_full_states"],
            )
            self.assertGreaterEqual(
                canonical["rational_decoder_degree_lower_bound"],
                min(canonical["distinct_even_states"], canonical["distinct_odd_states"]),
            )

    def test_declared_character_grammars_have_no_survivor(self) -> None:
        self.assertEqual(
            self.payload["legacy_division_character_screen"]["exact_survivors"], 0
        )
        self.assertEqual(
            self.payload["aggregate"]["quadratic_subset_exact_survivors"], 0
        )
        self.assertEqual(
            self.payload["aggregate"]["low_order_three_carry_uniform_survivors"], 0
        )

    def test_secp_power_maps_are_automorphisms(self) -> None:
        secp = self.payload["secp256k1"]
        self.assertEqual(secp["gcd_n_p_minus_1"], 1)
        self.assertEqual(secp["gcd_n_p_plus_1"], 1)
        self.assertEqual(secp["gcd_n_p2_minus_1"], 1)
        self.assertTrue(secp["n_th_power_maps_are_automorphisms"])

    def test_no_algorithmic_overclaim(self) -> None:
        decision = self.payload["decision"]
        self.assertTrue(decision["compact_shifted_miller_state_found"])
        self.assertFalse(decision["independent_orientation_channels_from_twist_shifts_found"])
        self.assertTrue(decision["torus_component_collapses_to_centered_kummer"])
        self.assertFalse(decision["parity_oracle_found"])
        self.assertFalse(decision["sub_sqrt_ecdlp_found"])


if __name__ == "__main__":
    unittest.main()
