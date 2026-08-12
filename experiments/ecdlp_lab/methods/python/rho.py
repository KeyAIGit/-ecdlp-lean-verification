"""Frozen seeded ordinary Pollard rho walk ``ordinary_rho_xmod3_v1``."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from math import gcd, isqrt
from typing import Callable

from .counting import BudgetExceeded, CountingCurve, CurveBackend
from .model import (
    MAX_U64,
    MethodBudgets,
    MethodCounters,
    PhaseCounters,
    Point,
    SolverDiagnostics,
    SolverOutcome,
)

FROZEN_ATTEMPTS = 4
ALGORITHMIC_MEMORY_ESTIMATE_BYTES = 1024


@dataclass(frozen=True)
class RhoState:
    point: Point
    left: int
    right: int


def _ceil_sqrt(value: int) -> int:
    root = isqrt(value)
    return root + (root * root < value)


def initial_coefficients(seed: int, restart: int, subgroup_order: int) -> tuple[int, int]:
    """Return the exact big-endian P1 coefficient pair for one attempt."""

    if type(seed) is not int or not 0 <= seed <= MAX_U64:
        raise ValueError("seed must be a u64 exact integer")
    if type(restart) is not int or not 0 <= restart < FROZEN_ATTEMPTS:
        raise ValueError("restart index is outside the frozen attempt range")
    if type(subgroup_order) is not int or subgroup_order < 2:
        raise ValueError("subgroup order must be an integer >= 2")
    digest = hashlib.sha256(
        f"keyai/p1-rho/{seed}/{restart}".encode("ascii")
    ).digest()
    left = 1 + int.from_bytes(digest[:8], "big") % (subgroup_order - 1)
    right = 1 + int.from_bytes(digest[8:16], "big") % (subgroup_order - 1)
    return left, right


def rho_step(
    curve: CountingCurve,
    state: RhoState,
    generator: Point,
    target: Point,
    subgroup_order: int,
) -> RhoState:
    """Apply the frozen x-mod-3 transition and count one online group call."""

    partition = 0 if state.point is None else state.point[0] % 3
    if partition == 0:
        return RhoState(
            curve.add(state.point, generator, phase="online_target"),
            (state.left + 1) % subgroup_order,
            state.right,
        )
    if partition == 1:
        return RhoState(
            curve.add(state.point, state.point, phase="online_target"),
            2 * state.left % subgroup_order,
            2 * state.right % subgroup_order,
        )
    return RhoState(
        curve.add(state.point, target, phase="online_target"),
        state.left,
        (state.right + 1) % subgroup_order,
    )


def _point_valid(backend: CurveBackend, point: Point) -> bool:
    if (
        point is None
        or not isinstance(point, tuple)
        or len(point) != 2
        or any(type(coordinate) is not int for coordinate in point)
    ):
        return False
    try:
        return backend.is_on_curve(point) is True
    except Exception:
        return False


def _counters(
    curve: CountingCurve | None,
    *,
    restarts: int,
    collisions: int,
    noninvertible: int,
    legacy: int | None,
) -> MethodCounters:
    online = curve.phase("online_target") if curve is not None else PhaseCounters()
    self_check = (
        curve.phase("method_self_check") if curve is not None else PhaseCounters()
    )
    return MethodCounters(
        online_target=online,
        method_self_check=self_check,
        table_entries=0,
        estimated_algorithmic_table_bytes=ALGORITHMIC_MEMORY_ESTIMATE_BYTES,
        restarts=restarts,
        collisions=collisions,
        noninvertible_collisions=noninvertible,
        distinguished_points=0,
        legacy_p1_group_operations=legacy,
    )


def _diagnostics(
    curve: CountingCurve | None,
    *,
    invalid_candidates: int,
    attempts: int,
) -> SolverDiagnostics:
    steps = curve.total_steps if curve is not None else 0
    return SolverDiagnostics(
        deterministic_steps=steps,
        floyd_iterations=steps,
        invalid_candidate_collisions=invalid_candidates,
        attempts=attempts,
    )


def solve_ordinary_rho(
    backend: CurveBackend,
    generator: Point,
    target: Point,
    subgroup_order: int,
    seed: int,
    budgets: MethodBudgets,
    *,
    self_check: bool = True,
    cancelled: Callable[[], bool] | None = None,
) -> SolverOutcome:
    """Run the exact four-attempt P1 walk with deterministic budget guards."""

    if (
        type(subgroup_order) is not int
        or subgroup_order < 2
        or type(seed) is not int
        or not 0 <= seed <= MAX_U64
        or type(self_check) is not bool
        or not isinstance(budgets, MethodBudgets)
        or subgroup_order.bit_length() > budgets.max_subgroup_order_bits
        or subgroup_order.bit_length() > 32
        or type(getattr(backend, "p", None)) is not int
        or backend.p.bit_length() > budgets.max_field_bits
        or backend.p.bit_length() > 32
        or not _point_valid(backend, generator)
        or not _point_valid(backend, target)
    ):
        return SolverOutcome.failed("invalid_public_input")
    if ALGORITHMIC_MEMORY_ESTIMATE_BYTES > budgets.max_memory_bytes:
        return SolverOutcome.failed("memory_budget_exhausted")

    curve: CountingCurve | None = None
    restarts = 0
    collisions = 0
    noninvertible = 0
    invalid_candidates = 0
    attempts = 0
    maximum_floyd_iterations = 8 * _ceil_sqrt(subgroup_order)
    try:
        curve = CountingCurve(backend, budgets, cancelled=cancelled)
        curve.guard.check_cancelled()
        for restart in range(FROZEN_ATTEMPTS):
            attempts += 1
            left, right = initial_coefficients(seed, restart, subgroup_order)
            left_point = curve.scalar_mul(
                left, generator, phase="online_target"
            )
            right_point = curve.scalar_mul(
                right, target, phase="online_target"
            )
            start = RhoState(
                curve.add(left_point, right_point, phase="online_target"),
                left,
                right,
            )
            tortoise = rho_step(curve, start, generator, target, subgroup_order)
            hare = rho_step(
                curve,
                rho_step(curve, start, generator, target, subgroup_order),
                generator,
                target,
                subgroup_order,
            )
            for _ in range(maximum_floyd_iterations):
                curve.consume_step()
                if tortoise.point == hare.point:
                    collisions += 1
                    numerator = (tortoise.left - hare.left) % subgroup_order
                    denominator = (hare.right - tortoise.right) % subgroup_order
                    if denominator == 0 or gcd(denominator, subgroup_order) != 1:
                        noninvertible += 1
                        break
                    candidate = (
                        numerator * pow(denominator, -1, subgroup_order)
                    ) % subgroup_order
                    valid = True
                    if self_check:
                        valid = (
                            curve.scalar_mul(
                                candidate,
                                generator,
                                phase="method_self_check",
                            )
                            == target
                        )
                    if valid:
                        online = curve.phase("online_target")
                        return SolverOutcome.succeeded(
                            candidate,
                            _counters(
                                curve,
                                restarts=restarts,
                                collisions=collisions,
                                noninvertible=noninvertible,
                                legacy=online.group_law_invocations,
                            ),
                            _diagnostics(
                                curve,
                                invalid_candidates=invalid_candidates,
                                attempts=attempts,
                            ),
                        )
                    invalid_candidates += 1
                    break
                tortoise = rho_step(
                    curve, tortoise, generator, target, subgroup_order
                )
                hare = rho_step(
                    curve,
                    rho_step(curve, hare, generator, target, subgroup_order),
                    generator,
                    target,
                    subgroup_order,
                )
            if restart + 1 < FROZEN_ATTEMPTS:
                # ``restarts`` counts actual transitions to a subsequent
                # attempt.  Thus first-attempt success is 0 and four exhausted
                # attempts report 3, while diagnostics.attempts reports 4.
                restarts += 1
    except BudgetExceeded as error:
        return SolverOutcome.failed(
            error.code,
            _counters(
                curve,
                restarts=restarts,
                collisions=collisions,
                noninvertible=noninvertible,
                legacy=None,
            ),
            diagnostics=_diagnostics(
                curve,
                invalid_candidates=invalid_candidates,
                attempts=attempts,
            ),
        )
    except Exception:
        return SolverOutcome.failed(
            "backend_error",
            _counters(
                curve,
                restarts=restarts,
                collisions=collisions,
                noninvertible=noninvertible,
                legacy=None,
            ),
            diagnostics=_diagnostics(
                curve,
                invalid_candidates=invalid_candidates,
                attempts=attempts,
            ),
        )

    online = curve.phase("online_target")
    return SolverOutcome.failed(
        "restart_budget_exhausted",
        _counters(
            curve,
            restarts=restarts,
            collisions=collisions,
            noninvertible=noninvertible,
            legacy=online.group_law_invocations,
        ),
        diagnostics=_diagnostics(
            curve,
            invalid_candidates=invalid_candidates,
            attempts=attempts,
        ),
    )


__all__ = [
    "ALGORITHMIC_MEMORY_ESTIMATE_BYTES",
    "FROZEN_ATTEMPTS",
    "RhoState",
    "initial_coefficients",
    "rho_step",
    "solve_ordinary_rho",
]
