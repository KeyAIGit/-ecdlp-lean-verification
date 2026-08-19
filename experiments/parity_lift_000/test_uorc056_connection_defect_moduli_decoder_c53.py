import json
import os
import unittest
from pathlib import Path

from uorc056_c53_connection_core import (
    connection_defect,
    gauge_changed_defect,
    recover_scalar_from_known_defect,
)
from uorc056_connection_defect_moduli_decoder_c53 import build_payload


class ConnectionDefectModuliDecoderC53Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        path = os.environ.get("UORC056_C53_PAYLOAD")
        cls.payload = json.loads(Path(path).read_text()) if path else build_payload()

    def test_exact_aggregate(self) -> None:
        aggregate = self.payload["aggregate"]
        self.assertEqual(aggregate["curves"], 12)
        self.assertEqual(aggregate["frozen"], 4)
        self.assertEqual(aggregate["heldout"], 8)
        self.assertEqual(aggregate["torsion_rows"], 4392)
        self.assertEqual(aggregate["c52_first_jet_cross_checks"], 4392)
        self.assertEqual(aggregate["derivative_negation_rows"], 4392)
        self.assertEqual(aggregate["derivative_glv_rows"], 4392)
        self.assertEqual(aggregate["full_state_injective_rows"], 4392)
        self.assertEqual(aggregate["uv_distinct_states"], 1464)
        self.assertEqual(aggregate["marked_generator_rows"], 30384)
        self.assertEqual(aggregate["marked_generator_distinct_states"], 3376)
        self.assertEqual(aggregate["marked_generator_mixed_collisions"], 0)
        self.assertEqual(aggregate["connection_classification_checks"], 112)
        self.assertEqual(aggregate["errors"], 0)

    def test_state_and_decoder_boundaries(self) -> None:
        analysis = self.payload["analysis"]
        for curve in analysis["curves"]:
            self.assertTrue(all(curve["identities"].values()))
            self.assertEqual(curve["full_state_R_D1_distinct"], curve["rows"])
            self.assertEqual(curve["uv_state_distinct"], curve["uv_expected_glv_orbits"])
            self.assertEqual(curve["uv_mixed_collisions"]["g"], 0)
        for marked in analysis["marked_generator_uv_state"]:
            self.assertEqual(marked["mixed_collisions"], 0)

        structural = analysis["structural_character_screen"]
        self.assertEqual(structural["declared_atoms"], 20880)
        self.assertEqual(structural["valid_atoms"], 545)
        self.assertEqual(structural["span_rank"]["parity"], 374)
        self.assertFalse(any(structural["target_in_arbitrary_product_span"].values()))

        carry = analysis["field_carry_screen"]
        self.assertEqual(carry["declared_atoms"], 2088)
        self.assertEqual(carry["valid_atoms"], 450)
        self.assertEqual(carry["span_rank"]["g"], 219)
        self.assertFalse(any(carry["target_in_arbitrary_product_span"].values()))

        discrete = analysis["discrete_phase_screen"]
        self.assertEqual(discrete["binary_atoms"], 2142)
        self.assertEqual(discrete["binary_span_rank"]["J"], 687)
        self.assertEqual(discrete["mu6_states"], 170)
        self.assertEqual(discrete["mu6_pairs_tested"], 14365)
        self.assertFalse(any(discrete["binary_target_in_arbitrary_product_span"].values()))
        self.assertEqual(set(discrete["mu6_exact_pair_state_counts"].values()), {0})

        nonlinear = analysis["nonlinear_anchor_screen"]
        self.assertEqual(nonlinear["declared_atoms"], 6292)
        self.assertEqual(nonlinear["valid_atoms"], 313)
        self.assertEqual(nonlinear["span_rank"]["parity"], 25)
        self.assertFalse(any(nonlinear["target_in_arbitrary_product_span"].values()))

    def test_interpolation_thresholds(self) -> None:
        analysis = self.payload["analysis"]
        self.assertEqual(
            [row["degree"] for row in analysis["g_polynomial_decoder_threshold"]],
            [4, 7, 6, 9, 7, 11, 14, 16, 20, 21, 23, 25],
        )
        self.assertEqual(
            [row["degree"] for row in analysis["g_rational_decoder_threshold"]],
            [3, 4, 4, 6, 4, 7, 9, 11, 13, 14, 16, 17],
        )
        self.assertTrue(all(
            row["nonzero_denominator_witness_verified"]
            for row in analysis["g_rational_decoder_threshold"]
        ))

    def test_connection_trichotomy(self) -> None:
        p = 101
        self.assertEqual(connection_defect(35, 5, 7, p), 0)
        old = 9
        changed = gauge_changed_defect(old, 17, 5, 3, p)
        self.assertEqual(changed, (old + 17 - 15) % p)
        defect = 23
        query = (19 * 7 + defect) % p
        self.assertEqual(recover_scalar_from_known_defect(query, defect, 7, p), 19)

        decision = self.payload["decision"]
        self.assertTrue(decision["functorial_connection_defect_is_zero"])
        self.assertTrue(decision["connection_defect_is_gauge_coboundary_without_extra_normalization"])
        self.assertTrue(decision["known_nonzero_anchor_defect_reveals_full_scalar"])
        self.assertTrue(decision["public_covariant_derivative_state_found"])
        self.assertTrue(decision["anchor_query_uv_state_determines_g_set_theoretically"])
        self.assertFalse(decision["cheap_g_decoder_found"])
        self.assertFalse(decision["cheap_J_decoder_found"])
        self.assertFalse(decision["cheap_parity_decoder_found"])
        self.assertFalse(decision["parity_oracle_found"])
        self.assertFalse(decision["sub_sqrt_ecdlp_found"])

    def test_secp_certificate(self) -> None:
        secp = self.payload["secp256k1"]
        self.assertEqual(secp["samples"], 8)
        self.assertEqual(secp["negation_checks"], 8)
        self.assertEqual(secp["glv_checks"], 8)
        self.assertGreaterEqual(secp["distinct_evaluations"], 20)
        self.assertEqual(len(self.payload["digest"]), 64)


if __name__ == "__main__":
    unittest.main()
