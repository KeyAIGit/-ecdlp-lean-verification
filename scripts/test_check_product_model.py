#!/usr/bin/env python3
"""Regression fixtures for the TASK-011 evidence and hypothesis lifecycle gate."""
from __future__ import annotations

import contextlib
import copy
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

from pilot_evidence import task_012_unlocked

ROOT = Path(__file__).resolve().parent.parent
CHECK_PATH = ROOT / "scripts" / "check_product_model.py"
SPEC = importlib.util.spec_from_file_location("check_product_model_under_test", CHECK_PATH)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class ProductModelGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.model = json.loads(
            (ROOT / "repo" / "PRODUCT_MODEL.json").read_text(encoding="utf-8")
        )
        self.pilot = json.loads(
            (ROOT / "repo" / "PILOT_PROTOCOL.json").read_text(encoding="utf-8")
        )

    @staticmethod
    def record(
        *,
        record_id: str = "DISC-001",
        hypothesis_id: str = "CH-001",
        disposition: str = "build",
        evidence_files: list[str] | None = None,
        sequence: int = 1,
        case_id: str = "CASE-ALPHA",
        task_id: str = "TASK-011",
        stage: str = "discovery",
        performed_on: str = "2026-07-23",
    ) -> dict:
        return {
            "id": record_id,
            "sequence": sequence,
            "case_id": case_id,
            "task_id": task_id,
            "hypothesis_id": hypothesis_id,
            "external": True,
            "stage": stage,
            "status": "completed",
            "performed_on": performed_on,
            "disposition": disposition,
            "public_summary": "A participant-approved sanitized discovery summary.",
            "evidence_files": ["README.md"] if evidence_files is None else evidence_files,
        }

    def run_gate(self) -> tuple[int, str]:
        self.model["pilot"]["status"] = self.pilot["status"]
        self.model["pilot"]["evidence_summary"] = self.pilot["evidence_state"]
        with tempfile.TemporaryDirectory(prefix="keyai-product-gate-") as directory:
            root = Path(directory)
            model_path = root / "PRODUCT_MODEL.json"
            pilot_path = root / "PILOT_PROTOCOL.json"
            model_path.write_text(
                json.dumps(self.model, indent=2) + "\n",
                encoding="utf-8",
            )
            pilot_path.write_text(
                json.dumps(self.pilot, indent=2) + "\n",
                encoding="utf-8",
            )
            original_model_path = CHECK.MODEL_PATH
            original_pilot_path = CHECK.PILOT_PATH
            CHECK.MODEL_PATH = model_path
            CHECK.PILOT_PATH = pilot_path
            output = io.StringIO()
            try:
                with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                    result = CHECK.main()
            finally:
                CHECK.MODEL_PATH = original_model_path
                CHECK.PILOT_PATH = original_pilot_path
        return result, output.getvalue()

    def set_valid_primary_build(self) -> None:
        record = self.record()
        self.pilot["status"] = "discovery_complete"
        self.pilot["evidence_state"] = (
            "External CH-001 TASK-011 discovery DISC-001 sequence 1 for CASE-ALPHA "
            "completed on 2026-07-23 with build disposition."
        )
        self.pilot["evidence_log"] = [record]
        hypothesis = self.model["customer_hypotheses"][0]
        hypothesis["status"] = "testing"
        hypothesis["evidence"] = [
            {"performed_on": record["performed_on"], "source": "README.md"}
        ]

    def test_live_contract_is_valid(self) -> None:
        result, output = self.run_gate()
        self.assertEqual(result, 0, output)

    def test_valid_primary_build_enters_testing(self) -> None:
        self.set_valid_primary_build()
        result, output = self.run_gate()
        self.assertEqual(result, 0, output)

    def test_supported_requires_ordered_same_case_task_012_return(self) -> None:
        self.set_valid_primary_build()
        second_project = self.record(
            record_id="RUN-001",
            sequence=2,
            task_id="TASK-012",
            stage="second_project",
            disposition=None,
            performed_on="2026-07-24",
        )
        returned = self.record(
            record_id="RETURN-001",
            sequence=3,
            task_id="TASK-012",
            stage="return",
            disposition=None,
            performed_on="2026-07-25",
        )
        self.pilot["evidence_log"].extend([second_project, returned])
        self.pilot["status"] = "mvp_validated"
        self.pilot["evidence_state"] = (
            "External CH-001 TASK-012 return RETURN-001 sequence 3 for CASE-ALPHA "
            "completed on 2026-07-25."
        )
        hypothesis = self.model["customer_hypotheses"][0]
        hypothesis["status"] = "supported"
        hypothesis["evidence"] = [
            {"performed_on": returned["performed_on"], "source": "README.md"}
        ]
        result, output = self.run_gate()
        self.assertEqual(result, 0, output)

    def test_return_without_build_and_second_project_is_rejected(self) -> None:
        returned = self.record(
            record_id="RETURN-001",
            task_id="TASK-012",
            stage="return",
            disposition=None,
        )
        self.pilot["evidence_log"] = [returned]
        self.pilot["evidence_state"] = (
            "External CH-001 TASK-012 return RETURN-001 sequence 1 for CASE-ALPHA "
            "completed on 2026-07-23."
        )
        result, output = self.run_gate()
        self.assertNotEqual(result, 0)
        self.assertIn("requires an ordered same-case TASK-012 second_project", output)

    def test_secondary_hypothesis_cannot_close_discovery(self) -> None:
        self.pilot["status"] = "discovery_complete"
        self.pilot["evidence_log"] = [self.record(hypothesis_id="CH-002")]
        result, output = self.run_gate()
        self.assertNotEqual(result, 0)
        self.assertIn("closed discovery status requires", output)

    def test_completed_record_requires_evidence_file(self) -> None:
        self.set_valid_primary_build()
        self.pilot["evidence_log"][0]["evidence_files"] = []
        result, output = self.run_gate()
        self.assertNotEqual(result, 0)
        self.assertIn("needs at least one evidence file", output)

    def test_evidence_path_must_be_a_regular_repo_file(self) -> None:
        self.set_valid_primary_build()
        self.pilot["evidence_log"][0]["evidence_files"] = ["."]
        self.model["customer_hypotheses"][0]["evidence"][0]["source"] = "."
        result, output = self.run_gate()
        self.assertNotEqual(result, 0)
        self.assertIn("regular file inside the repository", output)

    def test_impossible_iso_date_is_rejected(self) -> None:
        self.set_valid_primary_build()
        self.pilot["evidence_log"][0]["performed_on"] = "2026-99-99"
        result, output = self.run_gate()
        self.assertNotEqual(result, 0)
        self.assertIn("needs a real ISO date", output)

    def test_primary_status_cannot_drift_from_evidence(self) -> None:
        self.set_valid_primary_build()
        self.model["customer_hypotheses"][0]["status"] = "unvalidated"
        result, output = self.run_gate()
        self.assertNotEqual(result, 0)
        self.assertIn("status must follow the canonical pilot evidence lifecycle", output)

    def test_evidence_state_cannot_claim_an_unrecorded_session(self) -> None:
        self.pilot["evidence_state"] = "Ten external pilots completed."
        result, output = self.run_gate()
        self.assertNotEqual(result, 0)
        self.assertIn("exact no-session state", output)

    def test_completed_evidence_state_cannot_retain_no_session_claim(self) -> None:
        self.set_valid_primary_build()
        self.pilot["evidence_state"] += (
            " No external pilot session has been completed or recorded."
        )
        result, output = self.run_gate()
        self.assertNotEqual(result, 0)
        self.assertIn("must not claim that no session exists", output)

    def test_record_ids_must_be_unique(self) -> None:
        self.set_valid_primary_build()
        self.pilot["evidence_log"].append(copy.deepcopy(self.pilot["evidence_log"][0]))
        result, output = self.run_gate()
        self.assertNotEqual(result, 0)
        self.assertIn("record ids must be unique", output)

    def test_latest_stop_relocks_task_012(self) -> None:
        self.set_valid_primary_build()
        stopped = self.record(
            record_id="DISC-002",
            sequence=2,
            disposition="stop",
            performed_on="2026-07-24",
        )
        self.pilot["evidence_log"].append(stopped)
        self.pilot["status"] = "stopped"
        self.pilot["evidence_state"] = (
            "External CH-001 TASK-011 discovery DISC-002 sequence 2 for CASE-ALPHA "
            "completed on 2026-07-24 with stop disposition."
        )
        hypothesis = self.model["customer_hypotheses"][0]
        hypothesis["status"] = "rejected"
        hypothesis["evidence"] = [
            {"performed_on": stopped["performed_on"], "source": "README.md"}
        ]
        result, output = self.run_gate()
        self.assertEqual(result, 0, output)
        self.assertFalse(task_012_unlocked(self.pilot))

    def test_any_later_non_build_disposition_relocks_task_012(self) -> None:
        for disposition in ("change", "stop", "pending"):
            with self.subTest(disposition=disposition):
                pilot = copy.deepcopy(self.pilot)
                pilot["evidence_log"] = [
                    self.record(),
                    self.record(
                        record_id="DISC-002",
                        sequence=2,
                        disposition=disposition,
                        performed_on="2026-07-24",
                    ),
                ]
                self.assertFalse(task_012_unlocked(pilot))


if __name__ == "__main__":
    unittest.main()
