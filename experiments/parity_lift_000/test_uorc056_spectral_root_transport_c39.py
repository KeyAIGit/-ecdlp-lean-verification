#!/usr/bin/env python3
import unittest

from uorc056_spectral_root_transport_c39 import build_payload


class SpectralRootTransportC39Tests(unittest.TestCase):
    def test_full_replay(self) -> None:
        payload = build_payload()
        aggregate = payload["aggregate"]
        self.assertEqual(aggregate["curves"], 5)
        self.assertEqual(aggregate["query_cases"], 438)
        self.assertEqual(aggregate["inversion_checks"], 438)
        self.assertTrue(aggregate["all_square_root_congruences"])
        self.assertTrue(aggregate["all_reciprocal_orbit_identities"])
        self.assertTrue(aggregate["all_corrections_dense"])
        self.assertEqual(aggregate["direct_character_survivors"], 0)
        self.assertEqual(aggregate["errors"], 0)
        for row in payload["curves"]:
            r = row["pair_components"]
            self.assertEqual(row["correction_degree"], r - 1)
            self.assertEqual(row["correction_nonzero_coefficients"], r)
        decision = payload["decision"]
        self.assertTrue(decision["spectral_factor_reduced_to_oriented_square_root"])
        self.assertFalse(decision["cheap_parity_decoder_found"])
        self.assertFalse(decision["parity_oracle_found"])


if __name__ == "__main__":
    unittest.main()
