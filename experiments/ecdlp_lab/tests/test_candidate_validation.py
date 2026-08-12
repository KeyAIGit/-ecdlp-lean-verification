from __future__ import annotations

import ast
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from experiments.ecdlp_lab.core.candidate_validation import validate_candidate
from experiments.ecdlp_lab.core.canonical import load_json
from experiments.framework.ec_oracle import Curve as OracleCurve


REPO_ROOT = Path(__file__).resolve().parents[3]
CATALOG_PATH = (
    REPO_ROOT
    / "experiments/ecdlp_lab/fixtures/curves/ci_curve_catalog_v1.json"
)
VALIDATOR_PATH = (
    REPO_ROOT / "experiments/ecdlp_lab/core/candidate_validation.py"
)
SECP256K1_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
SECP256K1_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


class CandidateValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        catalog = load_json(CATALOG_PATH)
        cls.fixture = catalog["fixtures"][0]
        curve = OracleCurve(
            cls.fixture["field_p"],
            cls.fixture["curve_a"],
            cls.fixture["curve_b"],
        )
        cls.candidate = 37
        cls.public_input = SimpleNamespace(
            p=cls.fixture["field_p"],
            a=cls.fixture["curve_a"],
            b=cls.fixture["curve_b"],
            G=tuple(cls.fixture["generator"]),
            Q=curve.scalar_mul(cls.candidate, tuple(cls.fixture["generator"])),
            ell=cls.fixture["subgroup_order"],
        )

    def test_valid_candidate_is_checked_by_the_independent_oracle(self) -> None:
        original = OracleCurve.scalar_mul
        calls: list[int] = []

        def observed(curve: OracleCurve, scalar: int, point: object) -> object:
            calls.append(scalar)
            return original(curve, scalar, point)

        with patch.object(OracleCurve, "scalar_mul", new=observed):
            result = validate_candidate(self.public_input, self.candidate)
        self.assertTrue(result.passed, result.issues)
        self.assertTrue(result.relation_verified)
        self.assertIn(self.candidate, calls)
        self.assertGreaterEqual(calls.count(self.public_input.ell), 2)
        report = result.to_dict()
        self.assertEqual(report["candidate"], self.candidate)
        self.assertEqual(
            result.counters.generator_subgroup_check,
            self.public_input.ell.bit_length() + self.public_input.ell.bit_count(),
        )
        self.assertEqual(
            result.counters.target_subgroup_check,
            self.public_input.ell.bit_length() + self.public_input.ell.bit_count(),
        )
        self.assertEqual(
            result.counters.candidate_relation_check,
            self.candidate.bit_length() + self.candidate.bit_count(),
        )
        self.assertEqual(result.counters.total_group_law_invocations, 39)
        self.assertEqual(
            report["validator_counters"]["total_group_law_invocations"], 39
        )
        self.assertNotIn("offline_setup", repr(report))
        self.assertNotIn("online_target", repr(report))

        outcome = SimpleNamespace(status="success", candidate_scalar=self.candidate)
        self.assertTrue(validate_candidate(self.public_input, outcome).passed)
        failed = SimpleNamespace(status="bounded_failure", candidate_scalar=None)
        failed_validation = validate_candidate(self.public_input, failed)
        self.assertEqual(
            {issue.code for issue in failed_validation.issues},
            {"candidate.outcome.status"},
        )

    def test_wrong_candidate_and_wrong_order_fail_closed(self) -> None:
        wrong = validate_candidate(self.public_input, self.candidate + 1)
        self.assertFalse(wrong.passed)
        self.assertIn("candidate.relation", {issue.code for issue in wrong.issues})

        wrong_order = SimpleNamespace(**vars(self.public_input))
        wrong_order.ell = 2
        result = validate_candidate(wrong_order, 1)
        self.assertFalse(result.passed)
        self.assertIn("candidate.order.generator", {issue.code for issue in result.issues})

    def test_scalar_aliases_are_rejected_before_any_oracle_multiplication(self) -> None:
        aliases = (True, -1, self.public_input.ell, self.public_input.ell + 1)
        for alias in aliases:
            with self.subTest(alias=alias):
                with patch.object(
                    OracleCurve,
                    "scalar_mul",
                    side_effect=AssertionError("oracle must not run"),
                ) as scalar_mul:
                    result = validate_candidate(self.public_input, alias)
                self.assertFalse(result.passed)
                scalar_mul.assert_not_called()

    def test_malformed_points_and_structural_aliases_are_rejected(self) -> None:
        off_curve = SimpleNamespace(**vars(self.public_input))
        off_curve.Q = (0, 0)
        self.assertIn(
            "candidate.point.off_curve",
            {issue.code for issue in validate_candidate(off_curve, 1).issues},
        )

        list_point = SimpleNamespace(**vars(self.public_input))
        list_point.G = list(list_point.G)
        self.assertIn(
            "candidate.input.point",
            {issue.code for issue in validate_candidate(list_point, 1).issues},
        )

        for malformed in (
            {"p": self.public_input.p},
            SimpleNamespace(
                field_p=self.public_input.p,
                curve_a=self.public_input.a,
                curve_b=self.public_input.b,
                generator=self.public_input.G,
                target=self.public_input.Q,
                subgroup_order=self.public_input.ell,
            ),
        ):
            with self.subTest(malformed=type(malformed).__name__):
                result = validate_candidate(malformed, self.candidate)
                self.assertEqual(
                    {issue.code for issue in result.issues},
                    {"candidate.input.shape"},
                )

        class ExplodingInput:
            @property
            def p(self) -> int:
                raise RuntimeError("untrusted property")

        result = validate_candidate(ExplodingInput(), self.candidate)
        self.assertEqual(
            {issue.code for issue in result.issues},
            {"candidate.input.shape"},
        )

    def test_non_toy_and_exact_secp256k1_values_are_rejected(self) -> None:
        oversized_field = SimpleNamespace(**vars(self.public_input))
        oversized_field.p = SECP256K1_P
        result = validate_candidate(oversized_field, 1)
        self.assertFalse(result.passed)
        self.assertIn("candidate.input.range", {issue.code for issue in result.issues})

        oversized_order = SimpleNamespace(**vars(self.public_input))
        oversized_order.ell = SECP256K1_N
        result = validate_candidate(oversized_order, 1)
        self.assertFalse(result.passed)
        self.assertIn("candidate.input.range", {issue.code for issue in result.issues})

    def test_validator_import_graph_is_independent_of_methods_and_producers(self) -> None:
        tree = ast.parse(
            VALIDATOR_PATH.read_text(encoding="utf-8"),
            filename=str(VALIDATOR_PATH),
        )
        imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.add(node.module or "")
        self.assertIn("experiments.framework.ec_oracle", imports)
        forbidden = (
            "experiments.ecdlp_lab.methods",
            "experiments.ecdlp_lab.curves.producer_adapter",
            "experiments.ecdlp_lab.core.legacy_solver_replay",
            "experiments.ml_structure_probe",
        )
        for prefix in forbidden:
            self.assertFalse(
                any(name == prefix or name.startswith(prefix + ".") for name in imports),
                (prefix, sorted(imports)),
            )


if __name__ == "__main__":
    unittest.main()
