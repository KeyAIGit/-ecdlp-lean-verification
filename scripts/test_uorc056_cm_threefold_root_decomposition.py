import unittest

import uorc056_cm_threefold_root_decomposition as module


class CmThreefoldRootDecompositionTests(unittest.TestCase):
    def test_exact_full_replay(self):
        result = module.run()
        self.assertEqual(
            result["decision"],
            "central_oriented_root_has_exact_threefold_CM_branch_decomposition_but_short_branch_evaluator_remains_open",
        )
        replay = result["exact_replay"]
        self.assertEqual(replay["curves"], 5)
        self.assertEqual(replay["marked_roots"], 438)
        self.assertEqual(replay["scalar_evaluations"], 46260)
        self.assertEqual(sum(replay["branch_counts"].values()), 46260)
        self.assertEqual(sum(replay["gamma_counts"].values()), 46260)
        for row in replay["curve_rows"]:
            self.assertEqual(row["kernel_degree"], 3 * row["kappa_degree"])
            self.assertEqual(row["marked_roots"], row["n"] - 1)
            for component in ("A", "B", "C"):
                self.assertLess(row["max_component_degrees"][component], row["kappa_degree"])

    def test_selector_branch_partition(self):
        result = module.run()
        counts = result["exact_replay"]["branch_counts"]
        self.assertGreater(counts["uniform"], 0)
        self.assertEqual(counts["minority_0"], counts["minority_1"])
        self.assertEqual(counts["minority_1"], counts["minority_2"])


if __name__ == "__main__":
    unittest.main()
