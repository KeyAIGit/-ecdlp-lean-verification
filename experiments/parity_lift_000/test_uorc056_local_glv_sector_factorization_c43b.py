from __future__ import annotations

import json
import os
import unittest
from pathlib import Path

from uorc056_local_glv_sector_factorization_c43b import SECP_N, build_payload


class LocalGlvSectorFactorizationC43BTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        payload_path = os.environ.get("UORC056_C43B_PAYLOAD")
        cls.payload = (
            json.loads(Path(payload_path).read_text(encoding="utf-8"))
            if payload_path
            else build_payload()
        )

    def test_exact_replay(self) -> None:
        aggregate = self.payload["aggregate"]
        self.assertEqual(aggregate["curves"], 9)
        self.assertEqual(aggregate["frozen"], 5)
        self.assertEqual(aggregate["heldout"], 4)
        self.assertEqual(aggregate["carry_value_checks"], 1923)
        self.assertEqual(aggregate["errors"], 0)
        for row in self.payload["curves"]:
            self.assertTrue(all(row["identities"].values()), row["label"])

    def test_heldout_fixture_orders(self) -> None:
        heldout = [
            row
            for row in self.payload["curves"]
            if row["label"].startswith("heldout")
        ]
        self.assertEqual(
            [(row["p"], row["n"]) for row in heldout],
            [(61, 61), (211, 199), (991, 1009), (2089, 2143)],
        )

    def test_boundary(self) -> None:
        decision = self.payload["decision"]
        self.assertTrue(decision["exact_glv_carry_root_found"])
        self.assertTrue(decision["exact_sector_root_found"])
        self.assertTrue(decision["exact_oriented_root_reconstruction_found"])
        self.assertTrue(decision["residual_klein_four_gauge_survives"])
        self.assertFalse(decision["ordered_sector_transport_evaluator_found"])
        self.assertFalse(decision["cheap_parity_decoder_found"])
        self.assertFalse(decision["parity_oracle_found"])
        self.assertFalse(decision["sub_sqrt_ecdlp_found"])

    def test_secp_frontier(self) -> None:
        frontier = self.payload["secp256k1_frontier"]
        self.assertEqual(frontier["n"], SECP_N)
        self.assertEqual(frontier["half_kernel_degree"], (SECP_N - 1) // 2)
        self.assertEqual(frontier["glv_orbits"], (SECP_N - 1) // 6)
        self.assertEqual(frontier["glv_orbits_bit_length"], 254)
        self.assertEqual(len(self.payload["digest"]), 64)


if __name__ == "__main__":
    unittest.main()
