from __future__ import annotations

import ast
import copy
import json
import unittest
from dataclasses import fields
from pathlib import Path
from unittest.mock import patch

from experiments.ecdlp_lab.core.catalog_registry import resolve_curve_fixture
from experiments.ecdlp_lab.methods.python.dispatch import (
    run_method,
    sanitize_method_request,
)
from experiments.ecdlp_lab.methods.python.model import (
    PublicMethodInput,
    SolverOutcome,
)

ROOT = Path(__file__).resolve().parents[3]
METHOD_ROOT = ROOT / "experiments/ecdlp_lab/methods/python"


class MethodSecretBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(
            (
                ROOT
                / "experiments/ecdlp_lab/fixtures/contracts/valid/method_request_v1.json"
            ).read_text()
        )
        cls.fixture = resolve_curve_fixture(
            cls.record["curve_catalog_sha256"], cls.record["curve_fixture_id"]
        )

    def test_public_input_has_an_explicit_secret_free_field_set(self) -> None:
        names = {item.name for item in fields(PublicMethodInput)}
        forbidden = {
            "expected_scalar",
            "derivation_seed",
            "private_payload",
            "private_target",
            "source_record",
            "candidate_scalar",
            "answer",
            "secret",
        }
        self.assertTrue(names.isdisjoint(forbidden))
        self.assertEqual(
            names,
            {
                "method_id",
                "algorithm_seed",
                "p",
                "a",
                "b",
                "G",
                "Q",
                "ell",
                "budgets",
            },
        )

    def test_nested_secret_keys_are_rejected_before_projection(self) -> None:
        for container in ("provenance", "public_scalar_interval", "public_precomputation"):
            changed = copy.deepcopy(self.record)
            if changed[container] is None:
                changed[container] = {}
            changed[container]["expected_scalar"] = 1
            result = sanitize_method_request(changed, resolved_fixture=self.fixture)
            self.assertFalse(result.passed)

    def test_dispatch_passes_only_explicit_public_arguments_to_solver(self) -> None:
        public = sanitize_method_request(
            self.record, resolved_fixture=self.fixture
        ).public_input
        captured = {}

        def fake_solver(backend, generator, target, order, budgets, **kwargs):
            captured.update(
                {
                    "backend": backend,
                    "generator": generator,
                    "target": target,
                    "order": order,
                    "budgets": budgets,
                    "kwargs": kwargs,
                }
            )
            return SolverOutcome.failed("no_solution")

        with patch(
            "experiments.ecdlp_lab.methods.python.dispatch.solve_bsgs_cold",
            side_effect=fake_solver,
        ):
            run_method(public)
        rendered = repr(captured)
        self.assertNotIn("expected_scalar", rendered)
        self.assertNotIn("source_record", rendered)
        self.assertNotIn("private_payload", rendered)
        self.assertEqual(captured["target"], public.Q)

    def test_method_modules_do_not_import_legacy_runner_heavy_deps_or_oracle(self) -> None:
        forbidden_fragments = {
            "run_assay",
            "numpy",
            "scipy",
            "sklearn",
            "experiments.framework.ec_oracle",
        }
        for path in METHOD_ROOT.glob("*.py"):
            tree = ast.parse(path.read_text(), filename=str(path))
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom):
                    imports.append(node.module or "")
            for imported in imports:
                self.assertFalse(
                    any(fragment in imported for fragment in forbidden_fragments),
                    f"{path.name} imports forbidden dependency {imported}",
                )


if __name__ == "__main__":
    unittest.main()
