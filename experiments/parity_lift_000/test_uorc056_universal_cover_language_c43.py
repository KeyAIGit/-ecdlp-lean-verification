from __future__ import annotations

import unittest

from uorc056_universal_cover_language_c43 import (
    SECP_N,
    build_payload,
    carry,
    doubling_row,
    parity_sign,
    secp_doubling_certificate,
    transfer_charge,
    verify_fourier_formula,
    verify_gauge_type_system,
)


class UniversalCoverLanguageTests(unittest.TestCase):
    def test_carry_identity(self) -> None:
        for order in (5, 7, 11, 31):
            for a in range(order):
                for b in range(order):
                    expected = (
                        parity_sign(a, order)
                        * parity_sign(b, order)
                        * ((-1) ** carry(a, b, order))
                    )
                    self.assertEqual(parity_sign(a + b, order), expected)

    def test_secp_doubling_correction(self) -> None:
        row = secp_doubling_certificate()
        self.assertEqual(row["order_of_two_mod_n"], (SECP_N - 1) // 64)
        self.assertEqual(row["pair_action_cycles"], 32)
        self.assertFalse(row["pair_action_transitive"])

    def test_frozen_pair_actions(self) -> None:
        self.assertEqual(doubling_row(79)["pair_action_cycles"], 1)
        self.assertEqual(doubling_row(31)["pair_action_cycles"], 3)
        self.assertEqual(doubling_row(127)["pair_action_cycles"], 9)

    def test_fourier_peak(self) -> None:
        for order in (5, 7, 11, 31):
            row = verify_fourier_formula(order)
            self.assertTrue(row["formula_verified"])
            self.assertGreater(float(row["cotangent_peak"]), 0)

    def test_gauge_types(self) -> None:
        row = verify_gauge_type_system(11)
        self.assertTrue(row["closed_loop_neutral"])
        self.assertFalse(row["neutral_grammar_can_build_parity_charge"])
        self.assertNotEqual(transfer_charge(1, 9).mask, 0)

    def test_full_payload(self) -> None:
        payload = build_payload()
        self.assertEqual(payload["aggregate"]["hypotheses"], 7)
        self.assertEqual(payload["aggregate"]["secp_pair_cycles"], 32)
        self.assertEqual(payload["aggregate"]["errors"], 0)
        self.assertFalse(payload["decision"]["cheap_parity_decoder_found"])
        self.assertEqual(len(payload["digest"]), 64)


if __name__ == "__main__":
    unittest.main()
