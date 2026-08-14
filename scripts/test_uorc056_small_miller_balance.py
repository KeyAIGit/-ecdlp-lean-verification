import unittest

import uorc056_small_miller_balance as module


class SmallMillerBalanceTests(unittest.TestCase):
    def test_template_count(self):
        self.assertEqual(len(list(module.templates())), 128)

    def test_sparse_inverse(self):
        value = ((2, 1), (9, -2))
        self.assertEqual(module.add_sparse(value, module.negate_sparse(value)), ())

    def test_frozen_exact_result(self):
        grammar, result = module.run()
        self.assertEqual(grammar["profile_id"], "UORC-056-SMALL-MILLER-DIVISOR-BALANCE-V6")
        self.assertEqual(result["corpus"]["nonzero_points"], 438)
        self.assertEqual(result["primitive_quotient"]["raw_primitives"], 128)
        self.assertEqual(result["catalog"]["signed_semantic_atoms"], 256)
        self.assertEqual(result["catalog"]["pair_states_enumerated"], 33152)
        self.assertFalse(result["exact_search"]["candidate_found"])


if __name__ == "__main__":
    unittest.main()
