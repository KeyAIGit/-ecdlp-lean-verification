import unittest
from pathlib import Path

import uorc056_ward_point_scale_collapse as module


class WardPointScaleCollapseTests(unittest.TestCase):
    def test_frozen_and_secp_replay(self):
        result = module.run(
            Path("experiments/uorc056/divisor_aware_rational_grammar.json")
        )
        self.assertEqual(
            result["decision"],
            "ward_quasiperiod_constants_collapse_to_public_point_scale",
        )
        corpus = result["frozen_corpus"]
        self.assertEqual(corpus["curves"], 18)
        self.assertEqual(corpus["points_checked"], 7434)
        for row in corpus["rows"]:
            self.assertEqual(row["gcd_n_p_minus_one"], 1)
            self.assertEqual(row["chi_a_values"], [1])
        secp = result["secp256k1"]
        self.assertEqual(secp["gcd_n_p_minus_one"], 1)
        self.assertEqual(secp["chi_phi_raw_G"], -1)
        self.assertEqual(len(secp["fixed_samples"]), 8)
        for row in secp["fixed_samples"]:
            self.assertTrue(row["a_power_identity"])
            self.assertTrue(row["b_power_identity"])
            self.assertTrue(row["phi_recovered_from_b"])
            self.assertEqual(row["ward_b_times_eds_residue"], row["parity"])

    def test_public_secp_coprimality(self):
        self.assertEqual(math_gcd(module.SECP_N, module.SECP_P - 1), 1)


def math_gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a


if __name__ == "__main__":
    unittest.main()
