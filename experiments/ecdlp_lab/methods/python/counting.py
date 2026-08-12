"""Frozen affine group-call counting and deterministic budget guards."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol

from .model import MethodBudgets, PHASE_NAMES, PhaseCounters, Point


class CurveBackend(Protocol):
    p: int
    a: int
    b: int

    def is_on_curve(self, point: Point) -> bool: ...

    def add(self, left: Point, right: Point) -> Point: ...

    def negate(self, point: Point) -> Point: ...


class BudgetExceeded(RuntimeError):
    """A deterministic guard rejected an operation before it was performed."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


@dataclass
class _MutablePhase:
    group_law_invocations: int = 0
    nontrivial_additions: int = 0
    doublings: int = 0
    negations: int = 0

    def freeze(self) -> PhaseCounters:
        return PhaseCounters(
            group_law_invocations=self.group_law_invocations,
            nontrivial_additions=self.nontrivial_additions,
            doublings=self.doublings,
            negations=self.negations,
        )


class BudgetGuard:
    """One request-wide group/step guard with optional cooperative cancellation."""

    def __init__(
        self,
        budgets: MethodBudgets,
        *,
        cancelled: Callable[[], bool] | None = None,
        initial_group_law_invocations: int = 0,
        initial_steps: int = 0,
    ) -> None:
        if not isinstance(budgets, MethodBudgets):
            raise TypeError("budgets must be MethodBudgets")
        if type(initial_group_law_invocations) is not int or initial_group_law_invocations < 0:
            raise ValueError("initial group count must be a nonnegative integer")
        if type(initial_steps) is not int or initial_steps < 0:
            raise ValueError("initial step count must be a nonnegative integer")
        if initial_group_law_invocations > budgets.max_group_law_invocations:
            raise BudgetExceeded("group_operation_budget_exhausted")
        if initial_steps > budgets.max_steps:
            raise BudgetExceeded("step_budget_exhausted")
        self.budgets = budgets
        self.cancelled = cancelled or (lambda: False)
        self.group_law_invocations = initial_group_law_invocations
        self.steps = initial_steps

    def check_cancelled(self) -> None:
        try:
            is_cancelled = self.cancelled()
        except Exception as error:  # a broken controller is a backend boundary error
            raise RuntimeError("cancellation controller failed") from error
        if type(is_cancelled) is not bool:
            raise RuntimeError("cancellation controller must return bool")
        if is_cancelled:
            raise BudgetExceeded("process_timeout")

    def before_group_call(self) -> None:
        self.check_cancelled()
        if self.group_law_invocations >= self.budgets.max_group_law_invocations:
            raise BudgetExceeded("group_operation_budget_exhausted")

    def completed_group_call(self) -> None:
        self.group_law_invocations += 1

    def consume_step(self) -> None:
        self.check_cancelled()
        if self.steps >= self.budgets.max_steps:
            raise BudgetExceeded("step_budget_exhausted")
        self.steps += 1


class CountingCurve:
    """Delegate curve results while counting only completed wrapper calls.

    Every successful ``add`` is one group-law invocation.  A call with two
    equal, non-infinity operands is a doubling; a call with two unequal,
    non-infinity operands is a nontrivial addition.  Identity calls count as
    group-law invocations but as neither category.  Negation is separate.
    """

    def __init__(
        self,
        backend: CurveBackend,
        budgets: MethodBudgets,
        *,
        cancelled: Callable[[], bool] | None = None,
        initial_group_law_invocations: int = 0,
        initial_steps: int = 0,
    ) -> None:
        if not all(
            callable(getattr(backend, name, None))
            for name in ("is_on_curve", "add", "negate")
        ) or any(not hasattr(backend, name) for name in ("p", "a", "b")):
            raise TypeError("backend does not implement the curve protocol")
        self.backend = backend
        self.guard = BudgetGuard(
            budgets,
            cancelled=cancelled,
            initial_group_law_invocations=initial_group_law_invocations,
            initial_steps=initial_steps,
        )
        self._phases = {name: _MutablePhase() for name in PHASE_NAMES}

    @property
    def total_group_law_invocations(self) -> int:
        return self.guard.group_law_invocations

    @property
    def total_steps(self) -> int:
        return self.guard.steps

    def _phase(self, phase: str) -> _MutablePhase:
        if phase not in self._phases:
            raise ValueError("unknown counter phase")
        return self._phases[phase]

    def add(self, left: Point, right: Point, *, phase: str) -> Point:
        counters = self._phase(phase)
        self.guard.before_group_call()
        result = self.backend.add(left, right)
        self.guard.completed_group_call()
        counters.group_law_invocations += 1
        if left is not None and right is not None:
            if left == right:
                counters.doublings += 1
            else:
                counters.nontrivial_additions += 1
        return result

    def negate(self, point: Point, *, phase: str) -> Point:
        counters = self._phase(phase)
        self.guard.check_cancelled()
        result = self.backend.negate(point)
        counters.negations += 1
        return result

    def consume_step(self) -> None:
        self.guard.consume_step()

    def scalar_mul(self, scalar: int, point: Point, *, phase: str) -> Point:
        """Historical right-to-left walk, including the final unused double."""

        if type(scalar) is not int or scalar < 0:
            raise ValueError("scalar must be a nonnegative exact integer")
        result: Point = None
        addend = point
        remaining = scalar
        while remaining:
            if remaining & 1:
                result = self.add(result, addend, phase=phase)
            addend = self.add(addend, addend, phase=phase)
            remaining >>= 1
        return result

    def phase(self, phase: str) -> PhaseCounters:
        return self._phase(phase).freeze()


def counted_scalar_mul(
    curve: CountingCurve, scalar: int, point: Point, *, phase: str
) -> Point:
    return curve.scalar_mul(scalar, point, phase=phase)


def scalar_mul_group_calls(scalar: int) -> int:
    """Return the exact historical call count without performing arithmetic."""

    if type(scalar) is not int or scalar < 0:
        raise ValueError("scalar must be a nonnegative exact integer")
    return scalar.bit_length() + scalar.bit_count()


__all__ = [
    "BudgetExceeded",
    "BudgetGuard",
    "CountingCurve",
    "CurveBackend",
    "counted_scalar_mul",
    "scalar_mul_group_calls",
]
