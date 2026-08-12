from __future__ import annotations

import json
import unittest
from dataclasses import replace
from pathlib import Path

from experiments.ecdlp_lab.methods.python.bsgs import (
    BsgsTable,
    prepare_bsgs,
    solve_bsgs,
    solve_bsgs_cold,
)
from experiments.ecdlp_lab.methods.python.model import (
    MethodBudgets,
    PhaseCounters,
    SolverOutcome,
)
from experiments.framework.ec_oracle import Curve as OracleCurve
from experiments.ml_structure_probe.p1_toy_scaling.curve_math import Curve

ROOT = Path(__file__).resolve().parents[3]


def budgets(**changes: int) -> MethodBudgets:
    values = {
        "max_subgroup_order_bits": 32,
        "max_field_bits": 32,
        "max_group_law_invocations": 1_000_000,
        "max_table_entries": 100_000,
        "max_steps": 1_000_000,
        "timeout_ns": 1,
        "max_memory_bytes": 100_000_000,
        "workers": 1,
    }
    values.update(changes)
    return MethodBudgets(**values)


class SpyCurve:
    def __init__(self, p: int, a: int, b: int) -> None:
        self.inner = Curve(p, a, b)
        self.p, self.a, self.b = p, a, b
        self.add_calls = 0

    def is_on_curve(self, point):
        return self.inner.is_on_curve(point)

    def add(self, left, right):
        self.add_calls += 1
        return self.inner.add(left, right)

    def negate(self, point):
        return self.inner.negate(point)


class AdversarialBabySteps(dict):
    def get(self, *_args, **_kwargs):
        raise RuntimeError("must not escape")


class BsgsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        path = ROOT / "experiments/ecdlp_lab/fixtures/curves/ci_curve_catalog_v1.json"
        cls.fixtures = json.loads(path.read_text())["fixtures"]

    def test_known_scalars_across_all_six_ci_fixtures(self) -> None:
        for entry in self.fixtures:
            with self.subTest(entry=entry["fixture_id"]):
                p, a, b = entry["field_p"], entry["curve_a"], entry["curve_b"]
                ell = entry["subgroup_order"]
                generator = tuple(entry["generator"])
                scalar = 17 % ell
                target = OracleCurve(p, a, b).scalar_mul(scalar, generator)
                outcome = solve_bsgs_cold(
                    Curve(p, a, b), generator, target, ell, budgets()
                )
                self.assertTrue(outcome.success)
                self.assertEqual(outcome.candidate_scalar, scalar)
                self.assertEqual(
                    OracleCurve(p, a, b).scalar_mul(outcome.candidate_scalar, generator),
                    target,
                )

    def test_exact_p1_compatibility_count_for_fixture_request(self) -> None:
        outcome = solve_bsgs_cold(
            Curve(5923, 0, 7),
            (3665, 430),
            (3665, 430),
            5827,
            budgets(),
        )
        self.assertEqual(outcome.candidate_scalar, 1)
        self.assertEqual(outcome.counters.table_entries, 77)
        self.assertEqual(outcome.counters.estimated_algorithmic_table_bytes, 4928)
        self.assertEqual(outcome.counters.offline_setup.group_law_invocations, 88)
        self.assertEqual(outcome.counters.online_target.group_law_invocations, 0)
        self.assertEqual(outcome.counters.legacy_p1_group_operations, 88)
        self.assertEqual(outcome.counters.method_self_check.group_law_invocations, 2)

    def test_table_and_memory_limits_fail_before_allocation_or_backend_call(self) -> None:
        generator = (863, 955)
        for limited in (
            budgets(max_table_entries=1),
            budgets(max_memory_bytes=63),
            budgets(max_steps=1),
            budgets(max_group_law_invocations=1),
        ):
            backend = SpyCurve(1051, 0, 7)
            outcome = prepare_bsgs(backend, generator, 1093, limited)
            self.assertIsInstance(outcome, SolverOutcome)
            self.assertFalse(outcome.success)
            self.assertEqual(backend.add_calls, 0)

    def test_reusable_table_preserves_online_and_offline_separation(self) -> None:
        backend = Curve(1051, 0, 7)
        generator = (863, 955)
        target = OracleCurve(1051, 0, 7).scalar_mul(31, generator)
        prepared = prepare_bsgs(backend, generator, 1093, budgets())
        self.assertIsInstance(prepared, BsgsTable)
        first = solve_bsgs(prepared, target, budgets())
        second = solve_bsgs(prepared, target, budgets())
        self.assertEqual(first.candidate_scalar, 31)
        self.assertEqual(first, second)
        self.assertGreater(first.counters.offline_setup.group_law_invocations, 0)
        self.assertGreaterEqual(first.counters.online_target.group_law_invocations, 0)

    def test_cancelled_cold_setup_has_no_backend_calls(self) -> None:
        backend = SpyCurve(1051, 0, 7)
        outcome = prepare_bsgs(
            backend, (863, 955), 1093, budgets(), cancelled=lambda: True
        )
        self.assertIsInstance(outcome, SolverOutcome)
        self.assertEqual(outcome.failure.code, "process_timeout")
        self.assertEqual(backend.add_calls, 0)

    def test_forged_zero_cost_table_cannot_bypass_cumulative_budget(self) -> None:
        prepared = prepare_bsgs(Curve(1051, 0, 7), (863, 955), 1093, budgets())
        self.assertIsInstance(prepared, BsgsTable)
        forged = replace(
            prepared,
            offline_setup=PhaseCounters(),
            offline_steps=0,
        )
        outcome = solve_bsgs(
            forged,
            (863, 955),
            budgets(max_group_law_invocations=1, max_steps=1),
        )
        self.assertFalse(outcome.success)
        self.assertEqual(outcome.failure.code, "invalid_public_input")

    def test_adversarial_table_mapping_exception_fails_closed(self) -> None:
        prepared = prepare_bsgs(Curve(1051, 0, 7), (863, 955), 1093, budgets())
        self.assertIsInstance(prepared, BsgsTable)
        forged = replace(
            prepared,
            baby_steps=AdversarialBabySteps(prepared.baby_steps),
        )
        outcome = solve_bsgs(forged, (863, 955), budgets())
        self.assertEqual(outcome.failure.code, "invalid_public_input")

    def test_bool_order_is_rejected(self) -> None:
        outcome = prepare_bsgs(Curve(1051, 0, 7), (863, 955), True, budgets())
        self.assertIsInstance(outcome, SolverOutcome)
        self.assertEqual(outcome.failure.code, "invalid_public_input")

    def test_33_bit_order_is_rejected_before_capacity_math(self) -> None:
        outcome = prepare_bsgs(
            Curve(1051, 0, 7), (863, 955), 1 << 32, budgets()
        )
        self.assertIsInstance(outcome, SolverOutcome)
        self.assertEqual(outcome.failure.code, "invalid_public_input")


if __name__ == "__main__":
    unittest.main()
