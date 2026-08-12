from __future__ import annotations

import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from experiments.ecdlp_lab.core import legacy_solver_replay
from experiments.ecdlp_lab.core.candidate_validation import validate_candidate
from experiments.ecdlp_lab.core.canonical import load_json, sha256_file, sha256_json
from experiments.ecdlp_lab.core.validate import _p03_replay_issues, validate_offline
from experiments.ecdlp_lab.methods.python import dispatch


REPO_ROOT = Path(__file__).resolve().parents[3]
LOCATOR_PATH = REPO_ROOT / legacy_solver_replay.LOCATOR_PATH


class P03OfflineIntegrationTests(unittest.TestCase):
    def test_all_64_methods_and_independent_candidates_replay_exactly(self) -> None:
        self.assertEqual(_p03_replay_issues(), [])
        report = legacy_solver_replay.validate_legacy_replay()
        self.assertTrue(report.passed, report.issues)
        self.assertEqual(report.case_count, 64)
        self.assertEqual((report.bsgs_case_count, report.rho_case_count), (32, 32))
        self.assertEqual(report.success_count, 64)
        self.assertEqual(report.bsgs_legacy_group_operations, 61_574)
        self.assertEqual(report.rho_legacy_group_operations, 173_236)
        self.assertEqual(report.expected_rho_floyd_iterations, 57_193)
        self.assertEqual(report.expected_rho_collisions, 32)
        self.assertEqual(report.expected_rho_restarts, 0)
        self.assertEqual(report.expected_rho_noninvertible_collisions, 0)
        self.assertEqual(report.expected_rho_invalid_candidate_collisions, 0)

        validator_counters = [
            validate_candidate(
                case.to_public_input(), case.validator_only.expected_scalar
            ).counters
            for case in legacy_solver_replay.load_legacy_replay()
        ]
        self.assertEqual(
            (
                sum(row.generator_subgroup_check for row in validator_counters),
                sum(row.target_subgroup_check for row in validator_counters),
                sum(row.candidate_relation_check for row in validator_counters),
                sum(row.total_group_law_invocations for row in validator_counters),
            ),
            (1736, 1736, 1654, 5126),
        )

    def test_offline_summary_remains_the_frozen_p01_contract_summary(self) -> None:
        summary, issues = validate_offline()
        self.assertEqual(issues, [])
        self.assertEqual(
            summary,
            {
                "schemas": 9,
                "valid_records": 10,
                "adversarial_cases": 24,
                "issues": 0,
            },
        )

    def test_schema_example_is_authenticated_but_never_conformance_evidence(self) -> None:
        locator = load_json(LOCATOR_PATH)
        quarantine = locator["schema_only_quarantine"]
        self.assertFalse(quarantine["eligible_for_conformance"])
        self.assertEqual(
            quarantine["reason"],
            "schema_example_counter_values_do_not_match_frozen_p1_bsgs",
        )
        path = REPO_ROOT.joinpath(*quarantine["path"].split("/"))
        self.assertEqual(sha256_file(path), quarantine["sha256"])
        result = load_json(path)
        counters = result["counters"]
        self.assertEqual(counters["legacy_p1_group_operations"], 101)
        self.assertEqual(
            quarantine["p03_expected_counters"],
            {
                "estimated_algorithmic_table_bytes": 4928,
                "legacy_p1_group_operations": 88,
                "method_self_check_group_law_invocations": 2,
                "offline_setup_group_law_invocations": 88,
                "online_target_group_law_invocations": 0,
                "table_entries": 77,
            },
        )
        self.assertNotEqual(
            counters["legacy_p1_group_operations"],
            quarantine["p03_expected_counters"]["legacy_p1_group_operations"],
        )
        report = legacy_solver_replay.validate_legacy_replay()
        self.assertTrue(report.schema_only_quarantine_verified)
        self.assertEqual(
            sha256_file(LOCATOR_PATH), legacy_solver_replay.LOCATOR_RAW_SHA256
        )
        self.assertEqual(
            sha256_json(locator), legacy_solver_replay.LOCATOR_SEMANTIC_SHA256
        )

    def test_offline_fails_closed_on_quarantine_or_method_drift(self) -> None:
        report = legacy_solver_replay.validate_legacy_replay()
        with patch.object(
            legacy_solver_replay,
            "validate_legacy_replay",
            return_value=replace(report, schema_only_quarantine_verified=False),
        ):
            issues = _p03_replay_issues()
        self.assertIn("offline.p03.report.anchor", {issue.code for issue in issues})

        original_run_method = dispatch.run_method
        drifted = False

        def corrupt_first_candidate(public_input: object, **kwargs: object) -> object:
            nonlocal drifted
            outcome = original_run_method(public_input, **kwargs)
            if not drifted and outcome.status == "success":
                drifted = True
                return replace(
                    outcome,
                    candidate_scalar=(outcome.candidate_scalar + 1)
                    % public_input.subgroup_order,
                )
            return outcome

        with patch.object(
            dispatch, "run_method", side_effect=corrupt_first_candidate
        ):
            issues = _p03_replay_issues()
        codes = {issue.code for issue in issues}
        self.assertIn("offline.p03.method.candidate", codes)
        self.assertIn("offline.p03.candidate.relation", codes)


if __name__ == "__main__":
    unittest.main()
