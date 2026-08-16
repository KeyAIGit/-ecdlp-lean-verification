#!/usr/bin/env python3
import unittest

from uorc056_equivariant_transfer_gauge_c40 import build_payload


class EquivariantTransferGaugeC40Tests(unittest.TestCase):
    def test_full_replay(self) -> None:
        payload = build_payload()
        aggregate = payload["aggregate"]
        self.assertEqual(aggregate["curves"], 5)
        self.assertEqual(aggregate["pair_components"], 219)
        self.assertGreater(aggregate["deterministic_gauge_checks"], 0)
        self.assertTrue(aggregate["all_coordinate_maps_dense"])
        self.assertTrue(aggregate["all_transfer_polynomials_dense"])
        self.assertEqual(aggregate["errors"], 0)
        for curve in payload["curves"]:
            r = curve["pair_components"]
            self.assertEqual(curve["anchored_gauge_choices"], f"2^{r - 1}")
            for row in curve["multipliers"]:
                self.assertEqual(row["coordinate_map_degree"], r - 1)
                self.assertEqual(row["coordinate_map_support"], r)
                self.assertEqual(row["transfer_degree"], r - 1)
                self.assertEqual(row["transfer_support"], r)
        secp = payload["secp256k1"]
        self.assertEqual(
            secp["order_of_two_on_pair_quotient"],
            secp["pair_components"],
        )
        self.assertTrue(secp["doubling_action_transitive"])
        decision = payload["decision"]
        self.assertFalse(decision["public_action_coherence_selects_orientation"])
        self.assertFalse(decision["cheap_parity_decoder_found"])
        self.assertFalse(decision["parity_oracle_found"])


if __name__ == "__main__":
    unittest.main()
