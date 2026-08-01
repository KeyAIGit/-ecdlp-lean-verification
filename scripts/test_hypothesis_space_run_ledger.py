#!/usr/bin/env python3
"""Regression tests for hypothesis-space operational run memory."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from hypothesis_space_run_ledger import (
    POLICY_PATH,
    STATE_PATH,
    build_state,
    create_run_record,
    github_push_before_sha,
    load_anchored_records,
    load_policy,
    main as ledger_main,
    payload_digest,
    validate_record,
)

SCHEMA_PATH = POLICY_PATH.parent.parent / "experiments" / "engine" / "hypothesis_space_run.schema.json"


class HypothesisSpaceRunLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy = load_policy()
        cls.records, cls.problems = load_anchored_records(cls.policy)
        cls.state = json.loads(STATE_PATH.read_text(encoding="utf-8"))

    def test_committed_ledger_is_valid(self) -> None:
        self.assertEqual(self.problems, [])
        self.assertEqual(build_state(self.policy, self.records), self.state)

    def test_all_records_are_immutably_anchored(self) -> None:
        self.assertEqual(len(self.records), len(self.policy["immutable_record_anchors"]))
        self.assertEqual(self.state["immutable_record_count"], len(self.records))

    def test_operational_memory_cannot_be_scientific_evidence(self) -> None:
        counts = self.state["counts"]
        self.assertEqual(counts["scientific_outcomes"], 0)
        self.assertEqual(counts["ranker_training_labels"], 0)
        self.assertEqual(counts["brier_calibration_records"], 0)
        self.assertEqual(counts["authorizations"], 0)
        self.assertEqual(counts["route_promotions"], 0)
        for record in self.records:
            effect = record["knowledge_effect"]
            self.assertEqual(effect["scientific_outcome"], "none")
            self.assertEqual(effect["claim_disposition"], "none")
            self.assertFalse(any(
                effect[key]
                for key in (
                    "ranker_training_eligible",
                    "brier_calibration_eligible",
                    "candidate_admissible",
                    "candidate_recommended",
                    "experiment_authorized",
                    "route_promotion",
                )
            ))

    def test_repeated_root_is_not_a_new_map_revision(self) -> None:
        if not self.records:
            self.skipTest("no anchored run yet")
        repeated = copy.deepcopy(self.records[-1])
        repeated["run_id"] = "HSR-2099-01-01-999"
        repeated["sequence"] += 1
        repeated["recorded_at_utc"] = "2099-01-01T00:00:00Z"
        repeated["record_payload_sha256"] = payload_digest(repeated)
        state = build_state(self.policy, self.records + [repeated])
        self.assertEqual(
            state["counts"]["distinct_instance_roots"],
            self.state["counts"]["distinct_instance_roots"],
        )

    def test_nonconsecutive_repeated_root_is_not_a_new_map_revision(self) -> None:
        if not self.records:
            self.skipTest("no anchored run yet")
        first = copy.deepcopy(self.records[-1])
        second = copy.deepcopy(first)
        second["run_id"] = "HSR-2099-01-01-998"
        second["subject"]["instance_root_sha256"] = "1" * 64
        third = copy.deepcopy(first)
        third["run_id"] = "HSR-2099-01-01-999"
        state = build_state(self.policy, [first, second, third])
        self.assertEqual(state["counts"]["distinct_instance_roots"], 2)
        self.assertEqual(len(state["map_revisions"]), 2)

    def test_replayed_root_does_not_replace_distinct_revision_delta_baseline(self) -> None:
        if not self.records:
            self.skipTest("no anchored run yet")
        first = copy.deepcopy(self.records[-1])
        first["subject"]["instance_root_sha256"] = "a" * 64
        first["screening_snapshot"]["counts"]["warm"] = 10
        second = copy.deepcopy(first)
        second["subject"]["instance_root_sha256"] = "b" * 64
        second["screening_snapshot"]["counts"]["warm"] = 20
        replay = copy.deepcopy(first)
        replay["screening_snapshot"]["counts"]["warm"] = 10
        fourth = copy.deepcopy(first)
        fourth["subject"]["instance_root_sha256"] = "c" * 64
        fourth["screening_snapshot"]["counts"]["warm"] = 25
        state = build_state(self.policy, [first, second, replay, fourth])
        self.assertEqual(
            state["map_revisions"][-1]["delta_from_previous_distinct_root"]["counts"]["warm"],
            5,
        )

    def test_tampered_elapsed_time_is_rejected(self) -> None:
        if not self.records:
            self.skipTest("no anchored run yet")
        changed = copy.deepcopy(self.records[-1])
        changed["execution"]["elapsed_ns"][0] += 100_000_000
        changed["record_payload_sha256"] = payload_digest(changed)
        problems = validate_record(changed, self.policy)
        self.assertTrue(any("signatures_per_minute" in problem for problem in problems))

    def test_tampered_instance_root_is_rejected(self) -> None:
        if not self.records:
            self.skipTest("no anchored run yet")
        changed = copy.deepcopy(self.records[-1])
        changed["subject"]["instance_root_sha256"] = "0" * 64
        changed["record_payload_sha256"] = payload_digest(changed)
        problems = validate_record(changed, self.policy)
        self.assertTrue(any("instance root" in problem for problem in problems))

    def test_scientific_outcome_injection_is_rejected(self) -> None:
        if not self.records:
            self.skipTest("no anchored run yet")
        changed = copy.deepcopy(self.records[-1])
        changed["knowledge_effect"]["scientific_outcome"] = "falsified"
        changed["record_payload_sha256"] = payload_digest(changed)
        problems = validate_record(changed, self.policy, verify_git=False)
        self.assertTrue(any("scientific outcomes" in problem for problem in problems))

    def test_training_or_authorization_injection_is_rejected(self) -> None:
        if not self.records:
            self.skipTest("no anchored run yet")
        for key in ("ranker_training_eligible", "brier_calibration_eligible", "experiment_authorized", "route_promotion"):
            changed = copy.deepcopy(self.records[-1])
            changed["knowledge_effect"][key] = True
            changed["record_payload_sha256"] = payload_digest(changed)
            problems = validate_record(changed, self.policy, verify_git=False)
            self.assertTrue(any(key in problem for problem in problems), key)

    def test_payload_digest_binds_every_record_field(self) -> None:
        if not self.records:
            self.skipTest("no anchored run yet")
        changed = copy.deepcopy(self.records[-1])
        changed["knowledge_effect"]["interpretation"] += " altered"
        problems = validate_record(changed, self.policy, verify_git=False)
        self.assertTrue(any("record_payload_sha256" in problem for problem in problems))

    def test_failed_run_is_retained_as_operational_only(self) -> None:
        if not self.records:
            self.skipTest("no anchored run yet")
        run_date = datetime.now(timezone.utc).date().isoformat()
        with patch(
            "hypothesis_space_run_ledger.run_space",
            side_effect=RuntimeError("fault injection"),
        ):
            record = create_run_record(
                self.policy,
                run_id=f"HSR-{run_date}-999",
                sequence=999,
                source_commit=self.records[-1]["subject"]["source_commit"],
                repetitions=3,
                warmups=1,
                previous_record_sha256=None,
            )
        self.assertEqual(record["status"], "failed")
        self.assertEqual(record["operational_diagnostics"]["pipeline_errors"], 1)
        self.assertEqual(record["knowledge_effect"]["scientific_outcome"], "none")
        self.assertFalse(record["knowledge_effect"]["ranker_training_eligible"])
        self.assertEqual(validate_record(record, self.policy), [])

    def test_execution_method_mutation_is_rejected(self) -> None:
        if not self.records:
            self.skipTest("no anchored run yet")
        changed = copy.deepcopy(self.records[-1])
        changed["execution"]["method"] = "invented"
        changed["record_payload_sha256"] = payload_digest(changed)
        problems = validate_record(changed, self.policy)
        self.assertTrue(any("execution.method" in problem for problem in problems))

    def test_policy_cannot_relabel_structural_rejection_as_falsification(self) -> None:
        changed = copy.deepcopy(self.policy)
        changed["epistemic_contract"]["cold_cell"] = "scientifically falsified"
        from hypothesis_space_run_ledger import validate_policy

        problems = validate_policy(changed)
        self.assertTrue(any("epistemic_contract" in problem for problem in problems))

    def test_protected_base_history_cannot_be_rewritten(self) -> None:
        base = [
            {
                "run_id": "HSR-2099-01-01-001",
                "path": "experiments/engine/hypothesis_space_runs/HSR-2099-01-01-001.json",
                "sha256": "0" * 64,
            }
        ]
        changed = copy.deepcopy(self.policy)
        changed["immutable_record_anchors"] = []
        with patch(
            "hypothesis_space_run_ledger.protected_base_anchors",
            return_value=base,
        ):
            _, problems = load_anchored_records(changed)
        self.assertTrue(any("rewrite or truncate" in problem for problem in problems))

    def test_github_push_uses_event_before_commit(self) -> None:
        before = "1" * 40
        with tempfile.TemporaryDirectory() as directory:
            event_path = os.path.join(directory, "event.json")
            with open(event_path, "w", encoding="utf-8") as handle:
                json.dump({"before": before}, handle)
            with patch.dict(
                os.environ,
                {"GITHUB_EVENT_NAME": "push", "GITHUB_EVENT_PATH": event_path},
                clear=False,
            ):
                self.assertEqual(github_push_before_sha(), before)

    def test_recording_refuses_invalid_existing_ledger(self) -> None:
        with (
            patch(
                "hypothesis_space_run_ledger.load_anchored_records",
                return_value=([], ["corrupt predecessor"]),
            ),
            patch("hypothesis_space_run_ledger.create_run_record") as create,
            patch(
                "sys.argv",
                [
                    "hypothesis_space_run_ledger.py",
                    "--record",
                    "--run-id",
                    "HSR-2099-01-01-001",
                    "--source-commit",
                    "1" * 40,
                ],
            ),
        ):
            self.assertEqual(ledger_main(), 1)
        create.assert_not_called()

    def test_run_memory_is_not_an_input_to_the_screening_space(self) -> None:
        space_policy = json.loads(
            (POLICY_PATH.parent / "HYPOTHESIS_SPACE_V2.json").read_text(
                encoding="utf-8"
            )
        )
        evidence_paths = space_policy.get("evidence_snapshot", {}).get("paths", [])
        joined = " ".join(evidence_paths)
        self.assertNotIn("HYPOTHESIS_SPACE_RUN_LEDGER", joined)
        self.assertNotIn("hypothesis_space_run_state", joined)

    def test_schema_and_policy_files_exist(self) -> None:
        self.assertTrue(POLICY_PATH.is_file())
        self.assertTrue(STATE_PATH.is_file())
        self.assertTrue(SCHEMA_PATH.is_file())
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        effect = schema["$defs"]["knowledgeEffect"]["properties"]
        for key in (
            "ranker_training_eligible",
            "brier_calibration_eligible",
            "candidate_admissible",
            "candidate_recommended",
            "experiment_authorized",
            "route_promotion",
        ):
            self.assertEqual(effect[key], {"const": False})


if __name__ == "__main__":
    unittest.main()
