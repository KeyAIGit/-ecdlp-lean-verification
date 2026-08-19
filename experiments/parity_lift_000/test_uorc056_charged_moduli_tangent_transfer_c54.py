import json
import os
import unittest
from pathlib import Path

from uorc056_c54_transfer_core import (
    Curve,
    B_direct,
    state,
    tangent_add,
)
from uorc056_c54_transfer_analysis import FROZEN, build_payload


class ChargedModuliTangentTransferC54Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        payload_path = os.environ.get("UORC056_C54_PAYLOAD")
        if payload_path:
            cls.payload = json.loads(Path(payload_path).read_text())
        else:
            cls.payload = build_payload()

    def test_exact_replay_counts(self) -> None:
        a = self.payload["aggregate"]
        self.assertEqual(a["curves"], 16)
        self.assertEqual(a["rows"], 13128)
        self.assertEqual(a["doubling_transfer_checks"], 13098)
        self.assertEqual(a["addition_transfer_checks"], 13112)
        self.assertEqual(a["tangent_addition_checks"], 52480)
        self.assertEqual(a["charged_module_checks"], 13128)
        self.assertEqual(a["covariance_checks"], 13128)
        self.assertEqual(a["secp_public_samples"], 14)
        self.assertEqual(a["secp_doubling_transfer_checks"], 14)
        self.assertEqual(a["secp_GLV_covariance_checks"], 14)
        self.assertEqual(a["errors"], 0)

    def test_decoder_boundaries(self) -> None:
        a = self.payload["aggregate"]
        self.assertEqual(a["uniform_declared_character_atoms"], 157)
        self.assertEqual(a["uniform_valid_character_atoms"], 25)
        self.assertEqual(a["uniform_character_span_rank"], 12)
        self.assertFalse(a["uniform_target_in_span"])
        self.assertEqual(a["complete_p43_affine_atoms"], 39753)
        self.assertEqual(a["complete_p43_valid_affine_atoms"], 24052)
        self.assertEqual(a["complete_p43_survivors"], 0)
        self.assertEqual(a["p43_power_affine_atoms"], 5418)
        self.assertEqual(a["p43_power_affine_survivors"], 0)
        self.assertEqual(a["p43_power_representation_survivors"], 0)

    def test_orbit_and_cycle_boundary(self) -> None:
        a = self.payload["aggregate"]
        self.assertTrue(a["all_orbit_sign_relations"])
        self.assertLessEqual(a["max_even_factor_zero_coefficients"], 4)
        self.assertTrue(a["all_factor_BM_complexities_generic_half_window"])
        secp = self.payload["secp256k1_cycle_certificate"]
        self.assertTrue(secp["order_is_odd"])
        self.assertFalse(secp["minus_one_in_doubling_subgroup"])
        self.assertTrue(secp["lambda_in_doubling_subgroup"])
        self.assertEqual(secp["pair_quotient_cycles"], 32)
        self.assertEqual(secp["independent_pair_cycle_signs_after_one_anchor"], 31)

    def test_decision(self) -> None:
        d = self.payload["decision"]
        self.assertTrue(d["exact_differentiated_group_law_found"])
        self.assertTrue(d["exact_addition_transfer_found"])
        self.assertTrue(d["exact_doubling_transfer_found"])
        self.assertTrue(d["charged_state_module_rank_one_over_neutral_field"])
        self.assertFalse(d["moduli_tangent_adds_new_charge_generator"])
        self.assertTrue(d["declared_transfer_character_grammar_closed"])
        self.assertFalse(d["cheap_parity_decoder_found"])
        self.assertFalse(d["parity_oracle_found"])
        self.assertFalse(d["sub_sqrt_ecdlp_found"])
        self.assertEqual(len(self.payload["digest"]), 64)

    def test_small_curve_differentiated_group_law_directly(self) -> None:
        p, n, G, _beta, _lam = FROZEN[0]
        E = Curve(p)
        states = {
            k: state(E, n, G, E.mul(k, G, n))
            for k in range(1, n)
        }
        for k in range(1, n - 1):
            current = states[k]
            target = states[k + 1]
            for suffix, da, db in (("a", 1, 0), ("b", 0, 1)):
                point, tangent = tangent_add(
                    E,
                    current["P"],
                    G,
                    (current["u" + suffix], current["v" + suffix]),
                    (states[1]["u" + suffix], states[1]["v" + suffix]),
                    da,
                    db,
                )
                self.assertEqual(point, target["P"])
                self.assertEqual(
                    tangent,
                    (target["u" + suffix], target["v" + suffix]),
                )
            self.assertEqual(current["B"], B_direct(G, current["P"], p))
            self.assertEqual(
                current["A"],
                current["N"] * pow(current["B"], -1, p) % p,
            )


if __name__ == "__main__":
    unittest.main()
