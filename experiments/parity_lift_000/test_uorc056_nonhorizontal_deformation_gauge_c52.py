import json
import os
import unittest
from pathlib import Path

from uorc056_c52_deformation_core import (
    Curve, FROZEN, torsion_lift_basis, vertical_tangent_point,
    invariant_tangent_scalar, DualCurve,
)
from uorc056_nonhorizontal_deformation_gauge_c52 import build_payload


class NonhorizontalDeformationGaugeC52Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        payload_path = os.environ.get("UORC056_C52_PAYLOAD")
        if payload_path:
            cls.payload = json.loads(Path(payload_path).read_text())
        else:
            cls.payload = build_payload()

    def test_exact_replay_counts(self) -> None:
        aggregate = self.payload["aggregate"]
        self.assertEqual(aggregate["curves"], 12)
        self.assertEqual(aggregate["frozen"], 4)
        self.assertEqual(aggregate["heldout"], 8)
        self.assertEqual(aggregate["torsion_rows"], 4392)
        self.assertEqual(aggregate["horizontal_transport_checks"], 13176)
        self.assertEqual(aggregate["weierstrass_scaling_checks"], 8784)
        self.assertEqual(aggregate["vertical_scalar_recovery_checks"], 4392)
        self.assertEqual(aggregate["negation_covariance_checks"], 4392)
        self.assertEqual(aggregate["cm_covariance_checks"], 4392)
        self.assertEqual(aggregate["uniform_structural_atoms"], 3872)
        self.assertEqual(aggregate["uniform_structural_valid_atoms"], 89)
        self.assertEqual(aggregate["uniform_structural_span_rank"], 83)
        self.assertFalse(aggregate["uniform_structural_target_in_span"])
        self.assertEqual(aggregate["complete_p43_pair_affine_atoms"], 13251)
        self.assertEqual(aggregate["complete_p43_single_survivors"], 0)
        self.assertEqual(aggregate["errors"], 0)

    def test_all_declared_identities(self) -> None:
        for curve in self.payload["analysis"]["curves"]:
            self.assertTrue(all(curve["identities"].values()))
            self.assertEqual(curve["errors"], 0)
            self.assertEqual(
                curve["projective_direction_character_survivors"], []
            )
            for status in curve["feature_status"].values():
                self.assertEqual(status["affine_character_survivors"], [])

    def test_deformation_trichotomy(self) -> None:
        decision = self.payload["decision"]
        self.assertTrue(decision["public_finite_etale_torsion_lift_compiler_found"])
        self.assertTrue(
            decision["functorial_curve_deformation_is_horizontal_on_torsion_labels"]
        )
        self.assertTrue(
            decision["nonzero_fixed_curve_vertical_deformation_reveals_full_scalar"]
        )
        self.assertFalse(decision["weierstrass_scaling_breaks_quadratic_gauge"])
        self.assertTrue(decision["genuine_moduli_tangent_state_found"])
        self.assertTrue(decision["declared_deformation_character_grammar_closed"])
        self.assertFalse(
            decision["nonhorizontal_public_deformation_with_endpoint_charge_found"]
        )
        self.assertFalse(decision["cheap_parity_decoder_found"])
        self.assertFalse(decision["parity_oracle_found"])
        self.assertFalse(decision["sub_sqrt_ecdlp_found"])

    def test_secp_certificate(self) -> None:
        secp = self.payload["secp256k1"]
        self.assertTrue(secp["p_greater_than_n"])
        self.assertEqual(secp["public_samples"], 14)
        self.assertEqual(secp["horizontal_transport_checks"], 42)
        self.assertEqual(secp["weierstrass_scaling_checks"], 28)
        self.assertEqual(secp["vertical_scalar_recovery_checks"], 14)
        self.assertEqual(secp["cm_covariance_checks"], 14)

    def test_small_fixed_curve_vertical_identity(self) -> None:
        p, n, generator, _beta, _lam = FROZEN[0]
        curve = Curve(p)
        lifted = vertical_tangent_point(curve, generator, 1)
        dual_curve = DualCurve(curve)
        for scalar in range(1, n):
            image = dual_curve.mul(scalar, lifted, n)
            self.assertIsNotNone(image)
            self.assertEqual(invariant_tangent_scalar(image), scalar % p)

    def test_scaling_basis_formula(self) -> None:
        p, n, generator, _beta, _lam = FROZEN[0]
        curve = Curve(p)
        for scalar in range(1, n):
            point = curve.mul(scalar, generator, n)
            tangent_a, tangent_b, _ = torsion_lift_basis(curve, n, point)
            del tangent_a
            inverse_6b = pow(6 * curve.b, -1, p)
            self.assertEqual(
                tangent_b,
                (
                    2 * inverse_6b * point[0] % p,
                    3 * inverse_6b * point[1] % p,
                ),
            )


if __name__ == "__main__":
    unittest.main()
