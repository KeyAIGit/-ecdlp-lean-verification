from __future__ import annotations

import json
import unittest
from pathlib import Path
from unittest.mock import patch

from experiments.ecdlp_lab.curves.p1_adapter import load_legacy_catalog
from experiments.ecdlp_lab.methods.python.model import MethodBudgets
from experiments.ecdlp_lab.methods.python.rho import (
    RhoState,
    initial_coefficients,
    solve_ordinary_rho,
)
from experiments.framework.ec_oracle import Curve as OracleCurve
from experiments.ml_structure_probe.p1_toy_scaling.curve_math import Curve

ROOT = Path(__file__).resolve().parents[3]


def budgets(**changes: int) -> MethodBudgets:
    values = {
        "max_subgroup_order_bits": 32,
        "max_field_bits": 32,
        "max_group_law_invocations": 2_000_000,
        "max_table_entries": 100_000,
        "max_steps": 2_000_000,
        "timeout_ns": 1,
        "max_memory_bytes": 100_000_000,
        "workers": 1,
    }
    values.update(changes)
    return MethodBudgets(**values)


class SpyCurve:
    def __init__(self) -> None:
        self.inner = Curve(1051, 0, 7)
        self.p, self.a, self.b = 1051, 0, 7
        self.add_calls = 0

    def is_on_curve(self, point):
        return self.inner.is_on_curve(point)

    def add(self, left, right):
        self.add_calls += 1
        return self.inner.add(left, right)

    def negate(self, point):
        return self.inner.negate(point)


class PollardRhoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        path = ROOT / "experiments/ecdlp_lab/fixtures/curves/ci_curve_catalog_v1.json"
        cls.fixtures = json.loads(path.read_text())["fixtures"]

    def test_frozen_coefficient_vectors_are_big_endian(self) -> None:
        self.assertEqual(initial_coefficients(13000, 0, 1093), (813, 564))
        self.assertEqual(initial_coefficients(13000, 3, 1093), (639, 799))
        with self.assertRaises(ValueError):
            initial_coefficients(True, 0, 1093)

    def test_known_scalars_across_all_six_ci_fixtures_and_repeat(self) -> None:
        for ordinal, entry in enumerate(self.fixtures):
            with self.subTest(entry=entry["fixture_id"]):
                p, a, b = entry["field_p"], entry["curve_a"], entry["curve_b"]
                generator = tuple(entry["generator"])
                target = OracleCurve(p, a, b).scalar_mul(17, generator)
                args = (
                    Curve(p, a, b),
                    generator,
                    target,
                    entry["subgroup_order"],
                    ordinal,
                    budgets(),
                )
                first = solve_ordinary_rho(*args)
                second = solve_ordinary_rho(*args)
                self.assertEqual(first, second)
                self.assertEqual(first.candidate_scalar, 17)
                self.assertEqual(first.counters.collisions, 1)
                self.assertEqual(first.counters.restarts, 0)
                self.assertEqual(first.counters.estimated_algorithmic_table_bytes, 1024)

    def test_one_frozen_legacy_row_matches_exact_candidate_and_operations(self) -> None:
        catalog = load_legacy_catalog(
            catalog_path=(
                "experiments/ml_structure_probe/reports/p1_toy_scaling/curve_catalog.json"
            ),
            catalog_sha256=(
                "d293afa7e5b614f39ed00356e35ee81a400b57ee9656907170193cb3aca0bbd7"
            ),
            repo_root=ROOT,
        )
        curve_row = catalog.curve_by_key(13, 7)
        generator = curve_row.generators[5].point
        ell = curve_row.full_order // curve_row.cofactor
        target = OracleCurve(
            curve_row.field_p, curve_row.curve_a, curve_row.curve_b
        ).scalar_mul(5838, generator)
        outcome = solve_ordinary_rho(
            Curve(curve_row.field_p, curve_row.curve_a, curve_row.curve_b),
            generator,
            target,
            ell,
            13000,
            budgets(),
        )
        self.assertEqual(outcome.candidate_scalar, 5838)
        self.assertEqual(outcome.counters.legacy_p1_group_operations, 319)

    def test_zero_denominator_restarts_four_attempts(self) -> None:
        fixed = RhoState(None, 0, 0)
        with patch(
            "experiments.ecdlp_lab.methods.python.rho.rho_step",
            return_value=fixed,
        ):
            outcome = solve_ordinary_rho(
                Curve(1051, 0, 7),
                (863, 955),
                (863, 955),
                1093,
                0,
                budgets(),
            )
        self.assertEqual(outcome.failure.code, "restart_budget_exhausted")
        self.assertEqual(outcome.counters.collisions, 4)
        self.assertEqual(outcome.counters.noninvertible_collisions, 4)
        self.assertEqual(outcome.counters.restarts, 3)
        self.assertEqual(outcome.diagnostics.attempts, 4)

    def test_invalid_collision_candidate_is_not_accepted(self) -> None:
        calls = 0

        def forced_step(*_args):
            nonlocal calls
            calls += 1
            # Each attempt initializes tortoise, inner hare, then outer hare.
            return RhoState(None, 0, 1 if calls % 3 == 0 else 0)

        with patch(
            "experiments.ecdlp_lab.methods.python.rho.rho_step",
            side_effect=forced_step,
        ):
            outcome = solve_ordinary_rho(
                Curve(1051, 0, 7),
                (863, 955),
                (863, 955),
                1093,
                0,
                budgets(),
            )
        self.assertFalse(outcome.success)
        self.assertEqual(outcome.diagnostics.invalid_candidate_collisions, 4)

    def test_memory_and_cancellation_fail_before_backend_calls(self) -> None:
        for limited, cancelled, code in (
            (budgets(max_memory_bytes=1023), None, "memory_budget_exhausted"),
            (budgets(), lambda: True, "process_timeout"),
        ):
            backend = SpyCurve()
            outcome = solve_ordinary_rho(
                backend,
                (863, 955),
                (863, 955),
                1093,
                0,
                limited,
                cancelled=cancelled,
            )
            self.assertEqual(outcome.failure.code, code)
            self.assertEqual(backend.add_calls, 0)

    def test_step_budget_is_atomic(self) -> None:
        outcome = solve_ordinary_rho(
            Curve(1051, 0, 7),
            (863, 955),
            (863, 955),
            1093,
            0,
            budgets(max_steps=1),
        )
        self.assertEqual(outcome.failure.code, "step_budget_exhausted")
        self.assertEqual(outcome.diagnostics.floyd_iterations, 1)

    def test_bool_seed_and_33_bit_order_are_rejected(self) -> None:
        for order, seed in ((1093, True), (1 << 32, 0)):
            outcome = solve_ordinary_rho(
                Curve(1051, 0, 7),
                (863, 955),
                (863, 955),
                order,
                seed,
                budgets(),
            )
            self.assertEqual(outcome.failure.code, "invalid_public_input")


if __name__ == "__main__":
    unittest.main()
