"""Frozen affine group-operation accounting for Python reference methods."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

from experiments.ecdlp_lab.curves.producer_adapter import Curve

Point: TypeAlias = tuple[int, int] | None


class BudgetExceeded(RuntimeError):
    """Raised before a counted operation would exceed a frozen method budget."""


@dataclass
class InvocationBudget:
    """Shared group-law budget across setup, online work, and restarts."""

    maximum: int
    used: int = 0

    def consume(self) -> None:
        if self.used >= self.maximum:
            raise BudgetExceeded("max_group_law_invocations exceeded")
        self.used += 1


@dataclass(frozen=True)
class OperationSnapshot:
    group_law_invocations: int = 0
    nontrivial_additions: int = 0
    doublings: int = 0
    negations: int = 0

    def __sub__(self, other: "OperationSnapshot") -> "OperationSnapshot":
        return OperationSnapshot(
            group_law_invocations=(
                self.group_law_invocations - other.group_law_invocations
            ),
            nontrivial_additions=(
                self.nontrivial_additions - other.nontrivial_additions
            ),
            doublings=self.doublings - other.doublings,
            negations=self.negations - other.negations,
        )

    def to_contract_dict(self) -> dict[str, int | None]:
        return {
            "group_law_invocations": self.group_law_invocations,
            "nontrivial_additions": self.nontrivial_additions,
            "doublings": self.doublings,
            "negations": self.negations,
            "field_inversions": None,
            "field_multiplications": None,
            "field_squarings": None,
        }


class CountingCurve:
    """Delegate point results to the frozen producer arithmetic and count calls.

    A ``group_law_invocation`` is one call to ``Curve.add``.  Identity handling,
    ordinary additions, doublings, and cancellations therefore remain charged
    exactly as they are in the historical P1 implementation.  Field-operation
    counts are deliberately unavailable because Python's modular inverse and
    multiplication internals are not instrumented.
    """

    def __init__(
        self,
        curve: Curve,
        *,
        invocation_budget: InvocationBudget | None = None,
    ) -> None:
        self.curve = curve
        self.invocation_budget = invocation_budget
        self.group_law_invocations = 0
        self.nontrivial_additions = 0
        self.doublings = 0
        self.negations = 0

    def snapshot(self) -> OperationSnapshot:
        return OperationSnapshot(
            group_law_invocations=self.group_law_invocations,
            nontrivial_additions=self.nontrivial_additions,
            doublings=self.doublings,
            negations=self.negations,
        )

    def add(self, left: Point, right: Point) -> Point:
        if self.invocation_budget is not None:
            self.invocation_budget.consume()
        self.group_law_invocations += 1
        if left is not None and right is not None:
            if left == right:
                self.doublings += 1
            else:
                self.nontrivial_additions += 1
        return self.curve.add(left, right)

    def negate(self, point: Point) -> Point:
        self.negations += 1
        return self.curve.negate(point)

    def scalar_mul(self, scalar: int, point: Point) -> Point:
        """Double-and-add with the exact historical call-count convention."""

        if not isinstance(scalar, int):
            raise TypeError("scalar must be an integer")
        if scalar < 0:
            return self.scalar_mul(-scalar, self.negate(point))
        if not self.curve.is_on_curve(point):
            raise ValueError("point is not on the curve")

        result: Point = None
        addend = point
        remaining = scalar
        while remaining:
            if remaining & 1:
                result = self.add(result, addend)
            addend = self.add(addend, addend)
            remaining >>= 1
        return result


__all__ = [
    "BudgetExceeded",
    "CountingCurve",
    "InvocationBudget",
    "OperationSnapshot",
    "Point",
]
