"""P03 correctness and failure tests for the neutral Python baselines."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from experiments.ecdlp_lab.curves.producer_adapter import Curve, tonelli_shanks
from experiments.ecdlp_lab.methods.python.reference_dlog import (
    BSGS_METHOD_ID,
    MethodBudget,
    solve_bsgs,
    solve_method_request,
    solve_ordinary_rho,
)
from experiments.ecdlp_lab.methods.python.validation import (
    validate_candidate_independently,
)

ROOT = Path(__file__).resolve().parents[3]
CATALOG = ROOT / "experiments/ecdlp_lab/fixtures/curves/ci_curve_catalog_v1.json"


class ReferenceMethodTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixtures = json.loads(CATALOG.read_text(encoding="utf-8"))["fixtures"]

    def _instance(self, fixture: dict, scalar: int = 17):
        curve = Curve(
            int(fixture["field_p"]),
            int(fixture["curve_a"]),
            int(fixture["curve_b"]),
        )
        generator = tuple(fixture["generator"])
        order = int(fixture["subgroup_order"])
        scalar %= order
        target = curve.scalar_mul(scalar, generator)
        return curve, order, generator, target, scalar

    def test_bsgs_all_six_catalog_fixtures(self) -> None:
        for fixture in self.fixtures:
            with self.subTest(fixture=fixture["fixture_id"]):
                curve, order, generator, target, scalar = self._instance(fixture)
                result = solve_bsgs(curve, order, generator, target)
                self.assertEqual(result.status, "success")
                self.assertEqual(result.candidate_scalar, scalar)
                self.assertTrue(result.independently_validated)
                self.assertGreater(result.table_entries, 0)
                self.assertEqual(
                    result.legacy_p1_group_operations,
                    result.offline_setup.group_law_invocations
                    + result.online_target.group_law_invocations,
                )

    def test_rho_across_all_three_families(self) -> None:
        by_family = {}
        for fixture in self.fixtures:
            by_family.setdefault(fixture["family"], fixture)
        self.assertEqual(len(by_family), 3)
        for family, fixture in sorted(by_family.items()):
            with self.subTest(family=family):
                curve, order, generator, target, scalar = self._instance(
                    fixture, scalar=23
                )
                result = solve_ordinary_rho(
                    curve,
                    order,
                    generator,
                    target,
                    seed=1000 + order,
                )
                self.assertEqual(result.status, "success")
                self.assertEqual(result.candidate_scalar, scalar)
                self.assertTrue(result.independently_validated)
                self.assertGreaterEqual(result.collisions, 1)

    def test_identity_target_returns_canonical_zero(self) -> None:
        curve, order, generator, _, _ = self._instance(self.fixtures[0])
        result = solve_bsgs(curve, order, generator, None)
        self.assertEqual(result.candidate_scalar, 0)
        self.assertTrue(result.independently_validated)

    def test_bsgs_budget_failure_is_explicit(self) -> None:
        curve, order, generator, target, _ = self._instance(self.fixtures[0])
        result = solve_bsgs(
            curve,
            order,
            generator,
            target,
            budget=MethodBudget(max_table_entries=1),
        )
        self.assertEqual(result.status, "failure")
        self.assertEqual(result.failure_code, "table_entry_budget_exhausted")
        self.assertIsNone(result.candidate_scalar)

    def test_rho_step_budget_failure_is_explicit(self) -> None:
        curve, order, generator, target, _ = self._instance(self.fixtures[0])
        result = solve_ordinary_rho(
            curve,
            order,
            generator,
            target,
            seed=1,
            budget=MethodBudget(max_steps=1),
        )
        self.assertEqual(result.status, "failure")
        self.assertEqual(result.failure_code, "step_budget_exhausted")

    def test_forced_rho_cycle_is_counted(self) -> None:
        curve, order, generator, target, _ = self._instance(self.fixtures[0])
        result = solve_ordinary_rho(
            curve,
            order,
            generator,
            target,
            seed=3,
            budget=MethodBudget(max_steps=10_000),
            partitioner=lambda _point: 1,
        )
        self.assertEqual(result.status, "failure")
        self.assertGreaterEqual(result.collisions, 1)
        self.assertGreaterEqual(result.noninvertible_collisions, 1)

    def test_off_curve_target_is_rejected(self) -> None:
        curve, order, generator, _, _ = self._instance(self.fixtures[0])
        with self.assertRaisesRegex(ValueError, "target must be on the curve"):
            solve_bsgs(curve, order, generator, (0, 0))

    def test_target_outside_declared_subgroup_is_rejected(self) -> None:
        fixture = next(item for item in self.fixtures if int(item["cofactor"]) > 1)
        curve, order, generator, _, _ = self._instance(fixture)
        outsider = None
        for x in range(curve.p):
            rhs = (x**3 + curve.a * x + curve.b) % curve.p
            y = tonelli_shanks(rhs, curve.p)
            if y is None:
                continue
            point = (x, y)
            if curve.scalar_mul(order, point) is not None:
                outsider = point
                break
        self.assertIsNotNone(outsider)
        with self.assertRaisesRegex(ValueError, "outside the declared subgroup"):
            solve_bsgs(curve, order, generator, outsider)

    def test_independent_oracle_rejects_wrong_and_noncanonical_scalars(self) -> None:
        curve, order, generator, target, scalar = self._instance(self.fixtures[0])
        kwargs = {
            "field_p": curve.p,
            "curve_a": curve.a,
            "curve_b": curve.b,
            "generator": generator,
            "target": target,
            "subgroup_order": order,
        }
        self.assertTrue(
            validate_candidate_independently(**kwargs, candidate_scalar=scalar)
        )
        self.assertFalse(
            validate_candidate_independently(
                **kwargs, candidate_scalar=(scalar + 1) % order
            )
        )
        self.assertFalse(
            validate_candidate_independently(**kwargs, candidate_scalar=order)
        )

    def test_method_request_contains_no_secret(self) -> None:
        fixture = self.fixtures[0]
        curve, order, generator, target, scalar = self._instance(fixture)
        request = {
            "contract_kind": "method_request_v1",
            "candidate_id": None,
            "hypothesis_id": None,
            "authorization_id": None,
            "native_research_outcome": False,
            "method_id": BSGS_METHOD_ID,
            "algorithm_seed": 7,
            "curve": {
                "field_p": curve.p,
                "curve_a": curve.a,
                "curve_b": curve.b,
            },
            "generator": list(generator),
            "target": list(target),
            "subgroup_order": order,
            "budgets": {
                "max_group_law_invocations": 100_000,
                "max_steps": 100_000,
                "max_table_entries": 65_536,
                "max_memory_bytes": 64 * 1024 * 1024,
            },
        }
        result = solve_method_request(request)
        self.assertEqual(result.candidate_scalar, scalar)
        poisoned = dict(request)
        poisoned["expected_scalar"] = scalar
        with self.assertRaisesRegex(ValueError, "target-secret"):
            solve_method_request(poisoned)


if __name__ == "__main__":
    unittest.main()
