from __future__ import annotations

import unittest

from experiments.ecdlp_lab.methods.python.counting import (
    BudgetExceeded,
    CountingCurve,
    scalar_mul_group_calls,
)
from experiments.ecdlp_lab.methods.python.model import MethodBudgets
from experiments.ml_structure_probe.p1_toy_scaling.curve_math import Curve


def budgets(**changes: int) -> MethodBudgets:
    values = {
        "max_subgroup_order_bits": 32,
        "max_field_bits": 32,
        "max_group_law_invocations": 1000,
        "max_table_entries": 1000,
        "max_steps": 1000,
        "timeout_ns": 1,
        "max_memory_bytes": 1_000_000,
        "workers": 1,
    }
    values.update(changes)
    return MethodBudgets(**values)


class SpyCurve:
    def __init__(self) -> None:
        self.inner = Curve(1051, 0, 7)
        self.p, self.a, self.b = self.inner.p, self.inner.a, self.inner.b
        self.calls = 0

    def is_on_curve(self, point):
        return self.inner.is_on_curve(point)

    def add(self, left, right):
        self.calls += 1
        return self.inner.add(left, right)

    def negate(self, point):
        return self.inner.negate(point)


class MethodCountingTests(unittest.TestCase):
    G = (863, 955)

    def test_historical_scalar_walk_includes_final_double(self) -> None:
        backend = SpyCurve()
        counted = CountingCurve(backend, budgets())
        self.assertEqual(counted.scalar_mul(1, self.G, phase="online_target"), self.G)
        phase = counted.phase("online_target")
        self.assertEqual(phase.group_law_invocations, 2)
        self.assertEqual(phase.doublings, 1)
        self.assertEqual(phase.nontrivial_additions, 0)
        self.assertEqual(scalar_mul_group_calls(77), 11)
        self.assertIsNone(phase.field_inversions)

    def test_bool_scalar_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            CountingCurve(SpyCurve(), budgets()).scalar_mul(
                True, self.G, phase="online_target"
            )

    def test_budget_guard_prevents_over_budget_backend_call(self) -> None:
        backend = SpyCurve()
        counted = CountingCurve(
            backend, budgets(max_group_law_invocations=1)
        )
        with self.assertRaises(BudgetExceeded) as raised:
            counted.scalar_mul(1, self.G, phase="online_target")
        self.assertEqual(raised.exception.code, "group_operation_budget_exhausted")
        self.assertEqual(backend.calls, 1)
        self.assertEqual(counted.phase("online_target").group_law_invocations, 1)

    def test_cooperative_cancellation_precedes_backend_call(self) -> None:
        backend = SpyCurve()
        counted = CountingCurve(backend, budgets(), cancelled=lambda: True)
        with self.assertRaises(BudgetExceeded) as raised:
            counted.add(None, self.G, phase="online_target")
        self.assertEqual(raised.exception.code, "process_timeout")
        self.assertEqual(backend.calls, 0)

    def test_negation_is_separate_from_group_calls(self) -> None:
        counted = CountingCurve(SpyCurve(), budgets())
        counted.negate(self.G, phase="offline_setup")
        phase = counted.phase("offline_setup")
        self.assertEqual(phase.negations, 1)
        self.assertEqual(phase.group_law_invocations, 0)


if __name__ == "__main__":
    unittest.main()
