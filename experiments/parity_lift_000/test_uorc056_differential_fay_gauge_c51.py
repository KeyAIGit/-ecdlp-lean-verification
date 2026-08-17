from __future__ import annotations

import json
import os
import unittest
from pathlib import Path

from uorc056_differential_fay_gauge_c51 import (
    SECP_N,
    SECP_P,
    build_payload,
    period_shift_coefficients,
    period_shift_eta_coefficient,
)


class DifferentialFayGaugeC51Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        payload_path = os.environ.get("UORC056_C51_PAYLOAD")
        if payload_path:
            cls.payload = json.loads(Path(payload_path).read_text(encoding="utf-8"))
        else:
            cls.payload = build_payload()

    def test_exact_replay_counts(self) -> None:
        aggregate = self.payload["aggregate"]
        self.assertEqual(aggregate["curves"], 12)
        self.assertEqual(aggregate["frozen"], 4)
        self.assertEqual(aggregate["heldout"], 8)
        self.assertEqual(aggregate["torsion_jet_rows"], 4392)
        self.assertEqual(aggregate["first_derivative_checks"], 4368)
        self.assertEqual(aggregate["second_derivative_checks"], 4368)
        self.assertEqual(aggregate["third_derivative_checks"], 4368)
        self.assertEqual(aggregate["eta_cancellation_checks"], 73500)
        self.assertTrue(aggregate["all_affine_character_survivors_zero"])
        self.assertTrue(aggregate["all_H_have_mixed_parity_collisions"])
        self.assertTrue(aggregate["all_cm_quotients_dense"])
        self.assertEqual(
            aggregate["max_cm_degree_deficit_from_interpolation_ceiling"], 9
        )
        self.assertEqual(aggregate["anomalous_controls"], 2)
        self.assertEqual(aggregate["errors"], 0)

    def test_all_declared_identities(self) -> None:
        for curve in self.payload["curves"]:
            with self.subTest(label=curve["label"]):
                self.assertTrue(all(curve["identities"].values()))
                self.assertGreater(curve["H_query_mixed_parity_collisions"], 0)
                self.assertTrue(curve["cm_quotient"]["dense"])
                self.assertLessEqual(
                    (curve["cm_quotient"]["roots"] - 1)
                    - curve["cm_quotient"]["degree"],
                    9,
                )
                self.assertTrue(
                    all(
                        value == 0
                        for value in curve["affine_character_survivors"].values()
                    )
                )

    def test_period_shift_eta_cancellation_is_symbolic(self) -> None:
        cases = (
            (1, 0, 0, 1, 31, 7),
            (-9, 11, 5, -4, 139, 83),
            (123, -77, -19, 31, 1009, 713),
            (2**70 + 3, -(2**65) + 5, 17, -23, SECP_N, 255),
        )
        for a, b, r, s, order, scalar in cases:
            with self.subTest(a=a, b=b, r=r, s=s, order=order, scalar=scalar):
                self.assertEqual(
                    period_shift_eta_coefficient(a, b, r, s, order, scalar), 0
                )

    def test_high_index_specialization_coefficients(self) -> None:
        first, second = period_shift_coefficients(1, 0, 0, 1, SECP_N)
        self.assertEqual(first, SECP_N - 1)
        self.assertEqual(second, 1)

    def test_secp256k1_certificate(self) -> None:
        secp = self.payload["secp256k1"]
        self.assertEqual(secp["p"], SECP_P)
        self.assertEqual(secp["n"], SECP_N)
        self.assertTrue(secp["p_not_equal_n"])
        self.assertTrue(secp["n_invertible_mod_p"])
        self.assertEqual(secp["chi_ward_a"], 1)
        self.assertEqual(secp["chi_ward_b"], -1)
        self.assertEqual(secp["public_H_samples"], 14)
        self.assertEqual(secp["first_differential_checks"], 9)
        self.assertEqual(secp["second_differential_checks"], 9)
        self.assertEqual(secp["third_differential_checks"], 9)

    def test_anomalous_controls_are_excluded(self) -> None:
        controls = self.payload["anomalous_controls"]
        self.assertEqual({row["p"] for row in controls}, {61, 127})
        for row in controls:
            self.assertEqual(row["p"], row["n"])
            self.assertFalse(row["separable_first_jet_available"])
            self.assertEqual(row["psi_n_local_coefficients"], [0, 0, 0, 0])

    def test_claim_boundary_and_decision(self) -> None:
        self.assertEqual(
            self.payload["profile_id"], "UORC-056-DIFFERENTIAL-FAY-GAUGE-C51"
        )
        decision = self.payload["decision"]
        self.assertTrue(decision["fast_regularized_torsion_jet_found"])
        self.assertTrue(decision["fast_anchor_mixed_net_derivative_found"])
        self.assertFalse(decision["first_differential_exposes_integer_lift"])
        self.assertFalse(decision["higher_differentials_break_section_gauge"])
        self.assertTrue(
            decision["declared_differential_fay_grammar_reduces_to_periodic_public_states"]
        )
        self.assertFalse(decision["cheap_parity_decoder_found"])
        self.assertFalse(decision["parity_oracle_found"])
        self.assertFalse(decision["sub_sqrt_ecdlp_found"])
        self.assertEqual(len(self.payload["digest"]), 64)


if __name__ == "__main__":
    unittest.main()
