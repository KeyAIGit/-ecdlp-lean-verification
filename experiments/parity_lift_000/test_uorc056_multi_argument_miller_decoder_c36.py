from __future__ import annotations

import unittest

from uorc056_multi_argument_miller_decoder_c36 import build_payload, validate_payload


class MultiArgumentMillerDecoderC36Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_payload()
        validate_payload(cls.payload)

    def test_all_shift_joint_state_is_injective(self) -> None:
        aggregate = self.payload["aggregate"]
        self.assertEqual(aggregate["twist_shifts"], 520)
        self.assertEqual(aggregate["joint_injective_shifts"], 520)
        self.assertEqual(aggregate["joint_mixed_parity_shifts"], 0)

    def test_field_defect_cocycle(self) -> None:
        self.assertEqual(self.payload["aggregate"]["defect_cocycle_checks"], 54192)

    def test_low_degree_grammars_are_closed(self) -> None:
        aggregate = self.payload["aggregate"]
        self.assertEqual(aggregate["polynomial_degree_le_3_survivors"], 0)
        self.assertEqual(aggregate["rational_degree_le_2_nonzero_relations"], 0)
        for row in self.payload["curve_results"]:
            screen = row["all_shift_low_degree_screen"]
            self.assertEqual(screen["minimum_rank_in_both_declared_matrices"], 20)

    def test_canonical_polynomial_thresholds_are_generic(self) -> None:
        expected = {
            "E7-P43-N31": (7, 4),
            "E7-P67-N79": (11, 6),
            "E7-P79-N67": (10, 6),
            "E7-P127-N127": (15, 8),
            "E7-P163-N139": (16, 8),
        }
        for row in self.payload["curve_results"]:
            pair, triple = expected[row["instance"]]
            canonical = row["canonical_shift"]
            self.assertEqual(
                canonical["two_coordinate_polynomial_threshold"]["degree"], pair
            )
            self.assertEqual(
                canonical["three_coordinate_polynomial_threshold"]["degree"], triple
            )

    def test_canonical_rational_relations_start_at_dimension_threshold(self) -> None:
        expected = {
            "E7-P43-N31": (5, 3),
            "E7-P67-N79": (8, 5),
            "E7-P79-N67": (7, 4),
            "E7-P127-N127": (10, 6),
            "E7-P163-N139": (11, 6),
        }
        for row in self.payload["curve_results"]:
            pair, triple = expected[row["instance"]]
            canonical = row["canonical_shift"]
            self.assertEqual(
                canonical["two_coordinate_first_rational_relation"]["degree"], pair
            )
            self.assertEqual(
                canonical["three_coordinate_first_rational_relation"]["degree"], triple
            )

    def test_lookup_is_not_mislabeled_as_algorithm(self) -> None:
        decision = self.payload["decision"]
        self.assertTrue(decision["arbitrary_lookup_decoder_exists_on_frozen_curves"])
        self.assertFalse(decision["lookup_decoder_is_cost_acceptable"])
        self.assertFalse(decision["parity_oracle_found"])
        self.assertFalse(decision["sub_sqrt_ecdlp_found"])

    def test_digest(self) -> None:
        self.assertEqual(len(self.payload["digest"]), 64)


if __name__ == "__main__":
    unittest.main()
