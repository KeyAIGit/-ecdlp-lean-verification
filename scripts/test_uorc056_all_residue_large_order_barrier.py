import unittest

import uorc056_all_residue_large_order_barrier as module


class AllResidueLargeOrderBarrierTests(unittest.TestCase):
    def test_exact_secp_certificate(self):
        result = module.run()
        self.assertEqual(
            result["decision"],
            "secp256k1_has_no_all_residue_generator_of_order_n",
        )
        secp = result["secp256k1"]
        self.assertTrue(secp["certificate_holds"])
        self.assertEqual(secp["coarse_completion_constant"], 2064)
        self.assertEqual(secp["constant_square"], 4260096)
        self.assertEqual(secp["psi3_function_degree"], 4)
        self.assertGreater(int(secp["squared_ratio_floor"]), 1)

    def test_small_exact_witnesses_are_consistent(self):
        result = module.run()
        rows = result["small_exact_witness_consistency"]
        self.assertEqual(len(rows), 2)
        for row in rows:
            self.assertTrue(row["exact_parity_decimation"])
            self.assertTrue(row["necessary_bound_holds"])

    def test_exact_integer_inequality_without_floats(self):
        p = module.SECP256K1_P
        n = module.SECP256K1_N
        N = module.necessary_block_length(n)
        C = module.COARSE_COMPLETION_CONSTANT
        self.assertGreater(N * N, C * C * p)


if __name__ == "__main__":
    unittest.main()
