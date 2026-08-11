from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


def run_module(*arguments: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONHASHSEED"] = "0"
    return subprocess.run(
        [sys.executable, *arguments],
        cwd=REPO_ROOT,
        env=environment,
        text=True,
        capture_output=True,
        timeout=20,
        check=False,
    )


class StableCommandLineTests(unittest.TestCase):
    def test_capability_json_is_truthful_and_deterministic(self) -> None:
        command = ("-m", "experiments.ecdlp_lab.core.capabilities", "--json")
        first = run_module(*command)
        second = run_module(*command)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(first.stdout, second.stdout)
        report = json.loads(first.stdout)
        self.assertEqual(report["schema_version"], 1)
        self.assertEqual(report["report_kind"], "ecdlp_lab_capability_report")
        rows = report["capabilities"]
        self.assertEqual(
            {row["name"] for row in rows},
            {"python", "sage", "cargo", "rustc", "nvcc", "nvidia-smi", "docker"},
        )
        self.assertEqual(len(rows), len({row["name"] for row in rows}))
        for row in rows:
            self.assertIn(
                row["capability_state"],
                {"available", "unavailable", "error", "untested"},
            )
            self.assertIn(
                row["verification_state"],
                {"passed", "failed", "skipped_missing_capability", "untested"},
            )
            if row["capability_state"] == "unavailable":
                self.assertEqual(
                    row["verification_state"], "skipped_missing_capability"
                )
            if row["name"] != "python" and row["capability_state"] == "available":
                self.assertEqual(row["verification_state"], "untested")
        python = next(row for row in rows if row["name"] == "python")
        self.assertEqual(python["capability_state"], "available")
        self.assertEqual(python["verification_state"], "passed")

    def test_offline_validator_reports_the_complete_clean_corpus(self) -> None:
        completed = run_module(
            "-m", "experiments.ecdlp_lab.core.validate", "--offline", "--json"
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertTrue(report["passed"])
        self.assertEqual(report["issues"], [])
        self.assertEqual(
            report["summary"],
            {
                "adversarial_cases": 24,
                "issues": 0,
                "schemas": 9,
                "valid_records": 10,
            },
        )


if __name__ == "__main__":
    unittest.main()
