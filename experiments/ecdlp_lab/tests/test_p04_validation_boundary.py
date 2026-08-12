from __future__ import annotations

import ast
import subprocess
import sys
import unittest
from pathlib import Path

from experiments.ecdlp_lab.core.canonical import (
    canonical_json_bytes,
    load_json,
    strict_loads,
)
from experiments.ecdlp_lab.orchestration.method_worker import (
    execute_request as execute_method,
    make_method_worker_request,
    solver_outcome_from_dict,
    solver_outcome_to_dict,
)
from experiments.ecdlp_lab.orchestration.validator_worker import (
    execute_request as execute_validator,
    make_validator_request,
)


ROOT = Path(__file__).resolve().parents[3]
REQUEST_PATH = (
    ROOT
    / "experiments"
    / "ecdlp_lab"
    / "fixtures"
    / "contracts"
    / "valid"
    / "method_request_v1.json"
)


class P04ValidationBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.request = load_json(REQUEST_PATH)

    def test_method_and_validator_round_trip(self) -> None:
        outcome = execute_method(make_method_worker_request(self.request))
        self.assertEqual((outcome.status, outcome.candidate_scalar), ("success", 1))
        reconstructed = solver_outcome_from_dict(solver_outcome_to_dict(outcome))
        self.assertEqual(reconstructed, outcome)
        validation = execute_validator(
            make_validator_request(self.request, outcome.candidate_scalar)
        )
        self.assertTrue(validation["passed"])
        self.assertTrue(validation["relation_verified"])
        self.assertEqual(validation["candidate"], 1)

    def test_wrong_candidate_and_private_injection_fail(self) -> None:
        wrong = execute_validator(make_validator_request(self.request, 2))
        self.assertFalse(wrong["passed"])
        self.assertFalse(wrong["relation_verified"])

        poisoned = make_method_worker_request(self.request)
        poisoned["expected_scalar"] = 1
        outcome = execute_method(poisoned)
        self.assertEqual(outcome.status, "invalid_request")
        self.assertIsNone(outcome.candidate_scalar)

        validator_request = make_validator_request(self.request, 1)
        validator_request["expected_scalar"] = 1
        rejected = execute_validator(validator_request)
        self.assertFalse(rejected["passed"])

    def test_workers_accept_only_exact_canonical_stdin(self) -> None:
        command = [
            sys.executable,
            "-B",
            "-m",
            "experiments.ecdlp_lab.orchestration.validator_worker",
        ]
        request = make_validator_request(self.request, 1)
        good = subprocess.run(
            command,
            input=canonical_json_bytes(request),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=ROOT,
            check=False,
        )
        self.assertEqual(good.returncode, 0, good.stderr.decode(errors="replace"))
        self.assertEqual(canonical_json_bytes(strict_loads(good.stdout)), good.stdout)
        self.assertTrue(strict_loads(good.stdout)["passed"])

        noncanonical = subprocess.run(
            command,
            input=canonical_json_bytes(request) + b"\n",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=ROOT,
            check=False,
        )
        self.assertEqual(noncanonical.returncode, 0)
        self.assertFalse(strict_loads(noncanonical.stdout)["passed"])

        method_command = [
            sys.executable,
            "-B",
            "-m",
            "experiments.ecdlp_lab.orchestration.method_worker",
        ]
        method_request = make_method_worker_request(self.request)
        method = subprocess.run(
            method_command,
            input=canonical_json_bytes(method_request),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=ROOT,
            check=False,
        )
        self.assertEqual(method.returncode, 0, method.stderr.decode(errors="replace"))
        self.assertEqual(canonical_json_bytes(strict_loads(method.stdout)), method.stdout)
        self.assertEqual(strict_loads(method.stdout)["candidate_scalar"], 1)

    def test_validator_source_has_no_method_or_engine_dependency(self) -> None:
        source_path = (
            ROOT
            / "experiments"
            / "ecdlp_lab"
            / "orchestration"
            / "validator_worker.py"
        )
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
        self.assertFalse(
            any(
                name.startswith("experiments.ecdlp_lab.methods")
                or name.startswith("experiments.engine")
                for name in imported
            ),
            imported,
        )
        self.assertIn("experiments.ecdlp_lab.core.candidate_validation", imported)


if __name__ == "__main__":
    unittest.main()
