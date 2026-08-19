import json
import os
import unittest
from pathlib import Path

from uorc056_c53_connection_core import (
    ALL_CURVES, curve_rows, charged_columns, defect,
    recover_multiplier_from_defect,
)
from uorc056_connection_defect_moduli_decoder_c53 import build_payload


class ConnectionDefectModuliDecoderC53Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        path = os.environ.get("UORC056_C53_PAYLOAD")
        if path:
            cls.payload = json.loads(Path(path).read_text())
        else:
            cls.payload = build_payload()

    def test_exact_replay_counts(self) -> None:
        a = self.payload["aggregate"]
        self.assertEqual(a["curves"], 16)
        self.assertEqual(a["frozen"], 4)
        self.assertEqual(a["c52_heldout"], 8)
        self.assertEqual(a["new_c53_heldout"], 4)
        self.assertEqual(a["rows"], 9726)
        self.assertEqual(a["connection_recovery_checks"], 9726)
        self.assertEqual(a["anchor_zero_checks"], 9726)
        self.assertEqual(a["gauge_coboundary_checks"], 9726)
        self.assertEqual(a["connection_cocycle_checks"], 29178)
        self.assertEqual(a["quotient_invariance_checks"], 29178)
        self.assertEqual(a["charged_neutral_factorization_checks"], 19452)
        self.assertTrue(a["all_quotient_states_have_opposite_parity_collisions"])
        self.assertEqual(a["complete_p43_nonlinear_atoms"], 569800)
        self.assertEqual(a["complete_p43_exact_single_survivors"], 0)
        self.assertEqual(a["errors"], 0)

    def test_connection_trichotomy(self) -> None:
        d = self.payload["decision"]
        self.assertFalse(d["connection_defect_is_independent_parity_mechanism"])
        self.assertTrue(d["functorial_connection_defect_zero"])
        self.assertTrue(d["anchor_zero_defect_is_direct_public_state"])
        self.assertTrue(d["nonzero_anchor_defect_oracle_reveals_full_scalar"])
        self.assertFalse(d["arbitrary_decoder_from_glv_quotient_state_possible"])
        self.assertTrue(d["charged_neutral_factorization_found"])
        self.assertTrue(d["declared_bounded_nonlinear_grammar_closed"])
        self.assertFalse(d["cheap_parity_decoder_found"])
        self.assertFalse(d["parity_oracle_found"])
        self.assertFalse(d["sub_sqrt_ecdlp_found"])

    def test_bounded_decoder_status(self) -> None:
        uniform = self.payload["uniform_nonlinear_character_screen"]
        self.assertEqual(uniform["curves"], 16)
        self.assertEqual(uniform["rows"], 9726)
        self.assertEqual(uniform["declared_atoms"], 777)
        self.assertEqual(uniform["valid_atoms"], 3)
        self.assertEqual(uniform["span_rank"], 3)
        self.assertFalse(uniform["target_in_arbitrary_product_span"])
        self.assertEqual(uniform["exact_single_atoms"], [])

        complete = self.payload["complete_p43_nonlinear_screen"]
        self.assertEqual(complete["declared_atoms"], 569800)
        self.assertEqual(complete["valid_atoms"], 338986)
        self.assertEqual(complete["span_rank"], 29)
        self.assertEqual(complete["exact_single_survivors"], [])

        first = self.payload["curves"][0]["polynomial_decoder"]
        self.assertEqual(first["U|V"]["first_degree_at_most_bound"], 7)
        self.assertEqual(first["OA|OB"]["first_degree_at_most_bound"], 7)
        fourth = self.payload["curves"][3]["polynomial_decoder"]
        self.assertEqual(fourth["U|V"]["first_degree_at_most_bound"], 16)
        self.assertEqual(fourth["OA|OB"]["first_degree_at_most_bound"], 15)

    def test_small_connection_identity_directly(self) -> None:
        rows, context = curve_rows(ALL_CURVES[0])
        cG = rows[0].omega_a
        p = context["p"]
        for row in rows:
            delta = defect(row.omega_a, row.k, cG, p)
            self.assertEqual(
                recover_multiplier_from_defect(row.omega_a, delta, cG, p),
                row.k,
            )

    def test_small_charged_neutral_identity_directly(self) -> None:
        rows, context = curve_rows(ALL_CURVES[0])
        columns = charged_columns(rows, context)
        anchor = rows[0]
        p = context["p"]
        for index, row in enumerate(rows):
            neutral = (
                row.cm_r * pow(anchor.cm_r, -1, p)
                * (anchor.cm_t + 7) * pow(row.cm_t + 7, -1, p)
            ) % p
            self.assertEqual(columns["OA"][index] * columns["OB"][index] % p, neutral)
            neg = rows[(context["n"] - row.k) - 1]
            self.assertEqual((row.cm_t, row.cm_r, row.cm_s), (neg.cm_t, neg.cm_r, neg.cm_s))
            self.assertNotEqual(row.k & 1, neg.k & 1)

    def test_secp_certificate(self) -> None:
        secp = self.payload["secp256k1"]
        self.assertTrue(secp["p_greater_than_n"])
        self.assertEqual(secp["public_samples"], 14)
        self.assertEqual(secp["full_scalar_connection_recovery_checks"], 14)
        self.assertEqual(secp["charged_neutral_factorization_checks"], 14)
        self.assertEqual(secp["cm_covariance_checks"], 14)
        self.assertEqual(len(self.payload["digest"]), 64)


if __name__ == "__main__":
    unittest.main()
