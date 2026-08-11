from __future__ import annotations

import ast
import unittest
from pathlib import Path
from unittest.mock import patch

from experiments.ecdlp_lab.core.canonical import load_json
from experiments.ecdlp_lab.curves import validate_catalog
from experiments.framework.ec_oracle import Curve as OracleCurve


REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_PATH = (
    REPO_ROOT / "experiments/ecdlp_lab/curves/validate_catalog.py"
)
CI_CATALOG = (
    REPO_ROOT
    / "experiments/ecdlp_lab/fixtures/curves/ci_curve_catalog_v1.json"
)


class CurveValidatorIndependenceTests(unittest.TestCase):
    def test_validator_import_graph_has_no_producer_arithmetic(self) -> None:
        source = VALIDATOR_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(VALIDATOR_PATH))
        imports: set[str] = set()
        imported_names: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.add(node.module or "")
                imported_names.update(alias.name for alias in node.names)

        self.assertIn("experiments.framework.ec_oracle", imports)
        forbidden_modules = (
            "experiments.ml_structure_probe",
            "experiments.ecdlp_lab.curves.producer_adapter",
            "experiments.ecdlp_lab.curves.generate_ci_catalog",
        )
        for forbidden in forbidden_modules:
            self.assertFalse(
                any(name == forbidden or name.startswith(forbidden + ".") for name in imports),
                (forbidden, sorted(imports)),
            )
        self.assertTrue(
            {
                "Curve",
                "is_prime",
                "prime_divisors",
            }.issubset(imported_names)
        )
        self.assertTrue(
            {
                "candidate_orders_from_hasse_bsgs",
                "certified_prime_full_order",
                "glv_parameters",
                "tonelli_shanks",
            }.isdisjoint(imported_names)
        )

    def test_decisive_curve_operations_are_dispatched_to_framework_oracle(self) -> None:
        catalog = load_json(CI_CATALOG)
        fixture = catalog["fixtures"][0]
        original_scalar_mul = OracleCurve.scalar_mul
        calls: list[tuple[int, object]] = []

        def observed_scalar_mul(curve: OracleCurve, scalar: int, point: object) -> object:
            calls.append((scalar, point))
            return original_scalar_mul(curve, scalar, point)

        with patch.object(OracleCurve, "scalar_mul", new=observed_scalar_mul):
            result = validate_catalog.validate_fixture(fixture)
        self.assertTrue(result.passed, result.issues)
        self.assertGreaterEqual(len(calls), 2)
        self.assertIn(fixture["subgroup_order"], {scalar for scalar, _point in calls})
        self.assertIn(
            fixture["endomorphism"]["lambda"],
            {scalar for scalar, _point in calls},
        )

    def test_dispatcher_is_closed_to_exactly_three_certificate_types(self) -> None:
        self.assertEqual(
            set(validate_catalog._CERTIFICATE_VALIDATORS),
            {
                "prime_order_hasse_unique_v1",
                "exact_legendre_sum_v1",
                "j0_p_plus_one_v1",
            },
        )
        with self.assertRaises(TypeError):
            validate_catalog._CERTIFICATE_VALIDATORS["unregistered_v1"] = object()


if __name__ == "__main__":
    unittest.main()
