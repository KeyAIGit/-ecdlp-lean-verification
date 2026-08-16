import unittest

from uorc056_oriented_transposed_resultant_c42 import (
    SECP_N,
    build_payload,
    ceil_sqrt,
)


class OrientedTransposedResultantC42Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_payload()

    def test_exact_replay(self) -> None:
        aggregate = self.payload["aggregate"]
        self.assertEqual(aggregate["curves"], 6)
        self.assertEqual(aggregate["frozen_curves"], 5)
        self.assertEqual(aggregate["heldout_curves"], 1)
        self.assertEqual(aggregate["relative_norm_targets"], 498)
        self.assertEqual(aggregate["localized_branch_checks"], 498)
        self.assertEqual(aggregate["antifrobenius_character_candidates"], 59544)
        self.assertEqual(aggregate["antifrobenius_character_survivors"], 0)
        self.assertEqual(aggregate["errors"], 0)

        glv = self.payload["glv_relative_norm"]["aggregate"]
        self.assertTrue(glv["all_outer_norm_identities"])
        self.assertTrue(glv["all_zero_branches_match_parity"])
        self.assertTrue(glv["all_localized_decoders_return_parity"])
        self.assertTrue(glv["all_kappa_dense"])

        decision = self.payload["decision"]
        self.assertTrue(decision["exact_query_root_localization_found"])
        self.assertTrue(decision["exact_glv_cubic_relative_norm_found"])
        self.assertTrue(decision["antifrobenius_minor_affine_character_grammar_closed"])
        self.assertFalse(decision["cheap_parity_decoder_found"])
        self.assertFalse(decision["parity_oracle_found"])
        self.assertFalse(decision["sub_sqrt_ecdlp_found"])
        self.assertEqual(len(self.payload["digest"]), 64)

    def test_secp256k1_arithmetic(self) -> None:
        frontier = self.payload["secp256k1_cost_frontier"]
        expected_half = (
            57896044618658097711785492504343953926418782139537452191302581570759080747168
        )
        expected_block = (
            19298681539552699237261830834781317975472927379845817397100860523586360249056
        )
        expected_sqrt_block = 138919694570470098040331481282401564370
        expected_width = 277839389140940196080662962564803128739
        self.assertEqual(frontier["n"], SECP_N)
        self.assertEqual(frontier["n_mod_6"], 1)
        self.assertEqual(frontier["half_degree"], expected_half)
        self.assertEqual(frontier["glv_block_degree"], expected_block)
        self.assertTrue(frontier["half_degree_equals_three_blocks"])
        self.assertEqual(ceil_sqrt(expected_block), expected_sqrt_block)
        self.assertEqual(
            frontier["exact_two_level_product_frontier"]["minimum_width"],
            expected_width,
        )
        self.assertEqual(frontier["glv_block_degree_bit_length"], 254)
        self.assertEqual(frontier["ceil_sqrt_glv_block_bit_length"], 127)


if __name__ == "__main__":
    unittest.main()
