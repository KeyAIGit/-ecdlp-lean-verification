"""Exact differential replay of all retained P1 BSGS/rho rows."""

from __future__ import annotations

import unittest

from experiments.ecdlp_lab.methods.python.legacy_replay import (
    EXPECTED_REPLAY_ROWS,
    replay_summary,
    run_legacy_replay,
)


class LegacySolverReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = run_legacy_replay()
        cls.summary = replay_summary(cls.rows)

    def test_all_64_rows_are_present(self) -> None:
        self.assertEqual(len(self.rows), EXPECTED_REPLAY_ROWS)
        self.assertEqual(self.summary["observed_rows"], EXPECTED_REPLAY_ROWS)

    def test_candidates_and_operation_counts_match_exactly(self) -> None:
        failures = [row for row in self.rows if not row.passed]
        self.assertEqual(failures, [])
        self.assertEqual(self.summary["passed_rows"], EXPECTED_REPLAY_ROWS)
        self.assertEqual(self.summary["candidate_mismatches"], 0)
        self.assertEqual(self.summary["operation_count_mismatches"], 0)
        self.assertEqual(self.summary["validation_failures"], 0)

    def test_both_methods_and_all_field_rungs_are_covered(self) -> None:
        self.assertEqual(
            {row.legacy_method for row in self.rows},
            {"bsgs", "pollard_rho"},
        )
        self.assertEqual({row.field_bits for row in self.rows}, {13, 16, 20, 24})

    def test_historical_timing_is_not_current_telemetry(self) -> None:
        self.assertTrue(
            all(
                row.timing_comparison
                == "historical_descriptive_only_not_current_telemetry"
                for row in self.rows
            )
        )
        self.assertTrue(all(row.legacy_memory_is_estimate for row in self.rows))


if __name__ == "__main__":
    unittest.main()
