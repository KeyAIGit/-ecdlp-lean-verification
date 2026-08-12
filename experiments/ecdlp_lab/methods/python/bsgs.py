"""Neutral baby-step/giant-step with frozen P1 compatibility accounting."""

from __future__ import annotations

from dataclasses import dataclass
from math import isqrt
from types import MappingProxyType
from typing import Callable, Mapping

from .counting import (
    BudgetExceeded,
    CountingCurve,
    CurveBackend,
    scalar_mul_group_calls,
)
from .model import (
    MethodBudgets,
    MethodCounters,
    PhaseCounters,
    Point,
    SolverOutcome,
)

ALGORITHMIC_BYTES_PER_TABLE_ENTRY = 64


@dataclass(frozen=True)
class BsgsTable:
    """A target-independent table bound to one backend curve, base and order."""

    backend: CurveBackend
    field_p: int
    curve_a: int
    curve_b: int
    generator: Point
    subgroup_order: int
    width: int
    baby_steps: Mapping[Point, int]
    negative_stride: Point
    offline_setup: PhaseCounters
    offline_steps: int
    table_entries: int
    estimated_algorithmic_table_bytes: int


def _counters(
    *,
    offline: PhaseCounters = PhaseCounters(),
    online: PhaseCounters = PhaseCounters(),
    self_check: PhaseCounters = PhaseCounters(),
    entries: int = 0,
    estimate: int = 0,
    legacy: int | None = None,
) -> MethodCounters:
    return MethodCounters(
        offline_setup=offline,
        online_target=online,
        method_self_check=self_check,
        table_entries=entries,
        estimated_algorithmic_table_bytes=estimate,
        legacy_p1_group_operations=legacy,
    )


def _valid_point(backend: CurveBackend, point: Point) -> bool:
    if point is None:
        return False
    if (
        not isinstance(point, tuple)
        or len(point) != 2
        or any(type(coordinate) is not int for coordinate in point)
    ):
        return False
    try:
        return backend.is_on_curve(point) is True
    except Exception:
        return False


def prepare_bsgs(
    backend: CurveBackend,
    generator: Point,
    subgroup_order: int,
    budgets: MethodBudgets,
    *,
    cancelled: Callable[[], bool] | None = None,
) -> BsgsTable | SolverOutcome:
    """Build the cold-start table or return a bounded failure.

    All deterministic capacity checks occur before the table allocation and
    before the first backend call.  The table loop and stride multiplication
    deliberately reproduce the historical P1 call sequence, including its
    otherwise redundant final table advance and final scalar-multiplication
    double.
    """

    if (
        type(subgroup_order) is not int
        or subgroup_order < 2
        or not isinstance(budgets, MethodBudgets)
        or subgroup_order.bit_length() > budgets.max_subgroup_order_bits
        or subgroup_order.bit_length() > 32
        or type(getattr(backend, "p", None)) is not int
        or backend.p.bit_length() > budgets.max_field_bits
        or backend.p.bit_length() > 32
        or not _valid_point(backend, generator)
    ):
        return SolverOutcome.failed("invalid_public_input")
    width = isqrt(subgroup_order)
    if width * width < subgroup_order:
        width += 1
    estimate = width * ALGORITHMIC_BYTES_PER_TABLE_ENTRY
    if width > budgets.max_table_entries:
        return SolverOutcome.failed("table_budget_exhausted")
    if estimate > budgets.max_memory_bytes:
        return SolverOutcome.failed("memory_budget_exhausted")
    required_offline_group_calls = width + scalar_mul_group_calls(width)
    if required_offline_group_calls > budgets.max_group_law_invocations:
        return SolverOutcome.failed("group_operation_budget_exhausted")
    if width > budgets.max_steps:
        return SolverOutcome.failed("step_budget_exhausted")

    curve: CountingCurve | None = None
    table: dict[Point, int] = {}
    try:
        curve = CountingCurve(backend, budgets, cancelled=cancelled)
        curve.guard.check_cancelled()
        current: Point = None
        for value in range(width):
            curve.consume_step()
            table.setdefault(current, value)
            current = curve.add(current, generator, phase="offline_setup")
        stride = curve.scalar_mul(width, generator, phase="offline_setup")
        negative_stride = curve.negate(stride, phase="offline_setup")
    except BudgetExceeded as error:
        offline = curve.phase("offline_setup") if curve is not None else PhaseCounters()
        return SolverOutcome.failed(
            error.code,
            _counters(offline=offline, entries=len(table), estimate=len(table) * 64),
        )
    except Exception:
        offline = curve.phase("offline_setup") if curve is not None else PhaseCounters()
        return SolverOutcome.failed(
            "backend_error",
            _counters(offline=offline, entries=len(table), estimate=len(table) * 64),
        )

    offline = curve.phase("offline_setup")
    return BsgsTable(
        backend=backend,
        field_p=backend.p,
        curve_a=backend.a,
        curve_b=backend.b,
        generator=generator,
        subgroup_order=subgroup_order,
        width=width,
        baby_steps=MappingProxyType(dict(table)),
        negative_stride=negative_stride,
        offline_setup=offline,
        offline_steps=curve.total_steps,
        table_entries=len(table),
        estimated_algorithmic_table_bytes=len(table)
        * ALGORITHMIC_BYTES_PER_TABLE_ENTRY,
    )


def _table_binding_valid(table: BsgsTable, target: Point) -> bool:
    if not isinstance(table, BsgsTable):
        return False
    try:
        if type(table.subgroup_order) is not int or not (
            2 <= table.subgroup_order <= (1 << 32) - 1
        ):
            return False
        root = isqrt(table.subgroup_order)
        expected_width = root + (root * root < table.subgroup_order)
        expected_group_calls = expected_width + scalar_mul_group_calls(
            expected_width
        )
        expected_bytes = expected_width * ALGORITHMIC_BYTES_PER_TABLE_ENTRY
        offline = table.offline_setup
        return (
            type(table.field_p) is int
            and table.field_p == table.backend.p
            and table.curve_a == table.backend.a
            and table.curve_b == table.backend.b
            and _valid_point(table.backend, table.generator)
            and _valid_point(table.backend, target)
            and _valid_point(table.backend, table.negative_stride)
            and type(table.width) is int
            and table.width == expected_width
            and type(table.offline_steps) is int
            and table.offline_steps == expected_width
            and type(table.table_entries) is int
            and table.table_entries == expected_width
            and len(table.baby_steps) == expected_width
            and table.baby_steps.get(None) == 0
            and all(type(value) is int for value in table.baby_steps.values())
            and set(table.baby_steps.values()) == set(range(expected_width))
            and type(table.estimated_algorithmic_table_bytes) is int
            and table.estimated_algorithmic_table_bytes == expected_bytes
            and isinstance(offline, PhaseCounters)
            and offline.group_law_invocations == expected_group_calls
            and offline.negations == 1
            and offline.field_inversions is None
            and offline.field_multiplications is None
            and offline.field_squarings is None
        )
    except Exception:
        # A serialized/prepared mapping is untrusted at this boundary.  Any
        # adversarial Mapping implementation must become a public-input
        # rejection, never escape into the runner.
        return False


def solve_bsgs(
    table: BsgsTable,
    target: Point,
    budgets: MethodBudgets,
    *,
    self_check: bool = True,
    cancelled: Callable[[], bool] | None = None,
) -> SolverOutcome:
    """Solve one target using a previously prepared, target-independent table."""

    if (
        not isinstance(budgets, MethodBudgets)
        or type(self_check) is not bool
        or not _table_binding_valid(table, target)
    ):
        return SolverOutcome.failed("invalid_public_input")
    if table.table_entries > budgets.max_table_entries:
        return SolverOutcome.failed("table_budget_exhausted")
    if table.estimated_algorithmic_table_bytes > budgets.max_memory_bytes:
        return SolverOutcome.failed("memory_budget_exhausted")

    expected_setup_group_calls = table.width + scalar_mul_group_calls(table.width)
    expected_setup_steps = table.width

    try:
        curve = CountingCurve(
            table.backend,
            budgets,
            cancelled=cancelled,
            initial_group_law_invocations=expected_setup_group_calls,
            initial_steps=expected_setup_steps,
        )
    except BudgetExceeded as error:
        return SolverOutcome.failed(
            error.code,
            _counters(
                offline=table.offline_setup,
                entries=table.table_entries,
                estimate=table.estimated_algorithmic_table_bytes,
            ),
        )

    current = target
    try:
        for giant in range(table.width + 1):
            curve.consume_step()
            baby = table.baby_steps.get(current)
            if baby is not None:
                candidate = giant * table.width + baby
                if candidate < table.subgroup_order:
                    valid = True
                    if self_check:
                        valid = (
                            curve.scalar_mul(
                                candidate,
                                table.generator,
                                phase="method_self_check",
                            )
                            == target
                        )
                    if valid:
                        online = curve.phase("online_target")
                        counters = _counters(
                            offline=table.offline_setup,
                            online=online,
                            self_check=curve.phase("method_self_check"),
                            entries=table.table_entries,
                            estimate=table.estimated_algorithmic_table_bytes,
                            legacy=(
                                table.offline_setup.group_law_invocations
                                + online.group_law_invocations
                            ),
                        )
                        return SolverOutcome.succeeded(candidate, counters)
            # The historical implementation advances even after the final
            # unsuccessful probe.  Preserve that otherwise-unused call.
            current = curve.add(
                current, table.negative_stride, phase="online_target"
            )
    except BudgetExceeded as error:
        return SolverOutcome.failed(
            error.code,
            _counters(
                offline=table.offline_setup,
                online=curve.phase("online_target"),
                self_check=curve.phase("method_self_check"),
                entries=table.table_entries,
                estimate=table.estimated_algorithmic_table_bytes,
            ),
        )
    except Exception:
        return SolverOutcome.failed(
            "backend_error",
            _counters(
                offline=table.offline_setup,
                online=curve.phase("online_target"),
                self_check=curve.phase("method_self_check"),
                entries=table.table_entries,
                estimate=table.estimated_algorithmic_table_bytes,
            ),
        )

    online = curve.phase("online_target")
    return SolverOutcome.failed(
        "no_solution",
        _counters(
            offline=table.offline_setup,
            online=online,
            self_check=curve.phase("method_self_check"),
            entries=table.table_entries,
            estimate=table.estimated_algorithmic_table_bytes,
            legacy=(
                table.offline_setup.group_law_invocations
                + online.group_law_invocations
            ),
        ),
    )


def solve_bsgs_cold(
    backend: CurveBackend,
    generator: Point,
    target: Point,
    subgroup_order: int,
    budgets: MethodBudgets,
    *,
    self_check: bool = True,
    cancelled: Callable[[], bool] | None = None,
) -> SolverOutcome:
    prepared = prepare_bsgs(
        backend, generator, subgroup_order, budgets, cancelled=cancelled
    )
    if isinstance(prepared, SolverOutcome):
        return prepared
    return solve_bsgs(
        prepared,
        target,
        budgets,
        self_check=self_check,
        cancelled=cancelled,
    )


__all__ = [
    "ALGORITHMIC_BYTES_PER_TABLE_ENTRY",
    "BsgsTable",
    "prepare_bsgs",
    "solve_bsgs",
    "solve_bsgs_cold",
]
