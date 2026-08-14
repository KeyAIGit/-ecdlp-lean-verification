import unittest

import uorc056_global_divisor_balance as module


class GlobalDivisorBalanceTests(unittest.TestCase):
    def test_sparse_addition(self):
        self.assertEqual(
            module.add_sparse(((1, 1), (4, 2)), ((1, 2), (3, 1), (4, -2))),
            ((1, 3), (3, 1)),
        )

    def test_frozen_exact_result(self):
        grammar, result = module.run()
        self.assertEqual(grammar["profile_id"], "UORC-056-GLOBAL-DIVISOR-BALANCE-V5")
        self.assertEqual(result["corpus"]["nonzero_points"], 438)
        self.assertEqual(result["template_quotient"]["raw_pulled_line_templates"], 1440)
        self.assertEqual(result["template_quotient"]["unique_exact_local_semantics"], 1280)
        self.assertEqual(result["catalog"]["unordered_template_pairs_checked"], 819840)
        self.assertEqual(result["catalog"]["unique_pair_semantic_states"], 769563)
        self.assertFalse(result["exact_search"]["candidate_found"])


if __name__ == "__main__":
    unittest.main()
