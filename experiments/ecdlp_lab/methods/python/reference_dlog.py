"""Neutral BSGS and frozen ordinary-rho baselines for toy ECDLP fixtures.

The algorithms deliberately mirror the historical P1 implementation while
separating setup, online, and self-check counters. Returned scalars are checked
again through ``experiments.framework.ec_oracle``, which shares no method
arithmetic.

Scope: digest-authorized synthetic subgroups of at most 32 bits. No interval
promise, hidden precomputation, real key material, or secp256k1-sized target is
accepted.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from typing import Any, Callable, Mapping

from experiments.ecdlp_lab.curves.producer_adapter import Curve

from .counting import (
    BudgetExceeded,
    CountingCurve,
    InvocationBudget,
    OperationSnapshot,
    Point,
)
from .validation import validate_candidate_independently

BSGS_METHOD_ID = "bsgs_v1"
RHO_METHOD_ID = "ordinary_rho_xmod3_v1"

DERIVED_FROM = {
    BSGS_METHOD_ID: {
        "path": "experiments/ml_structure_probe/p1_toy_scaling/run_assay.py",
        "symbol": "bsgs_solve",
        "relationship": "independent_lab_reimplementation_with_exact_legacy_counter",
    },
    RHO_METHOD_ID: {
        "path": "experiments/ml_structure_probe/p1_toy_scaling/run_assay.py",
        "symbol": "pollard_rho_solve",
        "relationship": "frozen_walk_reimplementation_with_exact_legacy_counter",
    },
}

RHO_SPEC = {
    "partition": "infinity->0; finite point->x mod 3",
    "partition_0": "X <- X+G; a <- a+1",
    "partition_1": "X <- 2X; a <- 2a; b <- 2b",
    "partition_2": "X <- X+Q; b <- b+1",
    "cycle_detection": "Floyd tortoise/hare",
    "restart_domain": "SHA256(keyai/p1-rho/{seed}/{restart})",
    "restart_count": 4,
    "steps_per_restart": "8*ceil(sqrt(subgroup_order))",
    "collision_equation": "d=(a_t-a_h)/(b_h-b_t) mod subgroup_order",
}


@dataclass(frozen=True)
class MethodBudget:
    max_group_law_invocations: int = 1_000_000
    max_steps: int = 1_000_000
    max_table_entries: int = 65_536
    max_memory_bytes: int = 64 * 1024 * 1024

    def __post_init__(self) -> None:
        for name in (
            "max_group_law_invocations",
            "max_steps",
            "max_table_entries",
            "max_memory_bytes",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{name} must be a positive integer")

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "MethodBudget":
        return cls(
            max_group_law_invocations=int(value["max_group_law_invocations"]),
            max_steps=int(value["max_steps"]),
            max_table_entries=int(value["max_table_entries"]),
            max_memory_bytes=int(value["max_memory_bytes"]),
        )


@dataclass(frozen=True)
class ReferenceResult:
    method_id: str
    status: str
    candidate_scalar: int | None
    failure_code: str | None
    offline_setup: OperationSnapshot
    online_target: OperationSnapshot
    method_self_check: OperationSnapshot
    table_entries: int
    estimated_algorithmic_table_bytes: int
    legacy_p1_group_operations: int
    restarts: int
    collisions: int
    noninvertible_collisions: int
    distinguished_points: int
    state_steps: int
    independently_validated: bool
    algorithm_spec: Mapping[str, Any]
    memory_semantics: str

    def to_counter_dict(self) -> dict[str, Any]:
        return {
            "counter_semantics_id": "affine_group_calls_v1",
            "field_counter_semantics": "not_instrumented",
            "offline_setup": self.offline_setup.to_contract_dict(),
            "online_target": self.online_target.to_contract_dict(),
            "method_self_check": self.method_self_check.to_contract_dict(),
            "table_entries": self.table_entries,
            "estimated_algorithmic_table_bytes": self.estimated_algorithmic_table_bytes,
            "legacy_p1_group_operations": self.legacy_p1_group_operations,
            "restarts": self.restarts,
            "collisions": self.collisions,
            "noninvertible_collisions": self.noninvertible_collisions,
            "distinguished_points": self.distinguished_points,
        }


def _empty_snapshot() -> OperationSnapshot:
    return OperationSnapshot()


def _validate_instance(
    curve: Curve,
    order: int,
    generator: Point,
    target: Point,
) -> None:
    if isinstance(order, bool) or not isinstance(order, int) or not 2 <= order < 2**32:
        raise ValueError("subgroup_order must be an integer in [2, 2^32)")
    if generator is None or not curve.is_on_curve(generator):
        raise ValueError("generator must be a finite point on the curve")
    if not curve.is_on_curve(target):
        raise ValueError("target must be on the curve")
    if curve.scalar_mul(order, generator) is not None:
        raise ValueError("generator is not annihilated by subgroup_order")
    if curve.scalar_mul(order, target) is not None:
        raise ValueError("target is outside the declared subgroup")


def _self_check(
    curve: Curve,
    candidate: int,
    generator: tuple[int, int],
    target: Point,
) -> tuple[OperationSnapshot, bool]:
    counter = CountingCurve(curve)
    matched = counter.scalar_mul(candidate, generator) == target
    return counter.snapshot(), matched


def _failure(
    method_id: str,
    failure_code: str,
    *,
    offline: OperationSnapshot = OperationSnapshot(),
    online: OperationSnapshot = OperationSnapshot(),
    self_check: OperationSnapshot = OperationSnapshot(),
    table_entries: int = 0,
    table_bytes: int = 0,
    legacy_operations: int = 0,
    restarts: int = 0,
    collisions: int = 0,
    noninvertible_collisions: int = 0,
    state_steps: int = 0,
    algorithm_spec: Mapping[str, Any] | None = None,
    memory_semantics: str = "explicit_estimate_not_rss",
) -> ReferenceResult:
    return ReferenceResult(
        method_id=method_id,
        status="failure",
        candidate_scalar=None,
        failure_code=failure_code,
        offline_setup=offline,
        online_target=online,
        method_self_check=self_check,
        table_entries=table_entries,
        estimated_algorithmic_table_bytes=table_bytes,
        legacy_p1_group_operations=legacy_operations,
        restarts=restarts,
        collisions=collisions,
        noninvertible_collisions=noninvertible_collisions,
        distinguished_points=0,
        state_steps=state_steps,
        independently_validated=False,
        algorithm_spec=dict(algorithm_spec or {}),
        memory_semantics=memory_semantics,
    )


def solve_bsgs(
    curve: Curve,
    order: int,
    generator: tuple[int, int],
    target: Point,
    *,
    budget: MethodBudget | None = None,
) -> ReferenceResult:
    """Cold-start BSGS with reusable setup counters separated from online work."""

    budget = budget or MethodBudget()
    _validate_instance(curve, order, generator, target)
    width = math.isqrt(order)
    if width * width < order:
        width += 1
    if width > budget.max_table_entries:
        return _failure(
            BSGS_METHOD_ID,
            "table_entry_budget_exhausted",
            table_bytes=width * 64,
            algorithm_spec={"width": width, **DERIVED_FROM[BSGS_METHOD_ID]},
        )
    estimated_bytes = width * 64
    if estimated_bytes > budget.max_memory_bytes:
        return _failure(
            BSGS_METHOD_ID,
            "algorithmic_memory_budget_exhausted",
            table_bytes=estimated_bytes,
            algorithm_spec={"width": width, **DERIVED_FROM[BSGS_METHOD_ID]},
        )

    shared = InvocationBudget(budget.max_group_law_invocations)
    offline_curve = CountingCurve(curve, invocation_budget=shared)
    table: dict[Point, int] = {}
    current: Point = None
    try:
        for value in range(width):
            table.setdefault(current, value)
            current = offline_curve.add(current, generator)
        stride = offline_curve.scalar_mul(width, generator)
        negative_stride = offline_curve.negate(stride)
    except BudgetExceeded:
        snapshot = offline_curve.snapshot()
        return _failure(
            BSGS_METHOD_ID,
            "group_law_budget_exhausted",
            offline=snapshot,
            table_entries=len(table),
            table_bytes=len(table) * 64,
            legacy_operations=snapshot.group_law_invocations,
            algorithm_spec={"width": width, **DERIVED_FROM[BSGS_METHOD_ID]},
        )

    online_curve = CountingCurve(curve, invocation_budget=shared)
    current = target
    candidate: int | None = None
    try:
        for giant in range(width + 1):
            baby = table.get(current)
            if baby is not None:
                proposed = giant * width + baby
                if proposed < order and curve.scalar_mul(proposed, generator) == target:
                    candidate = proposed
                    break
            current = online_curve.add(current, negative_stride)
    except BudgetExceeded:
        offline = offline_curve.snapshot()
        online = online_curve.snapshot()
        return _failure(
            BSGS_METHOD_ID,
            "group_law_budget_exhausted",
            offline=offline,
            online=online,
            table_entries=len(table),
            table_bytes=len(table) * 64,
            legacy_operations=offline.group_law_invocations + online.group_law_invocations,
            algorithm_spec={"width": width, **DERIVED_FROM[BSGS_METHOD_ID]},
        )

    offline = offline_curve.snapshot()
    online = online_curve.snapshot()
    legacy_operations = offline.group_law_invocations + online.group_law_invocations
    if candidate is None:
        return _failure(
            BSGS_METHOD_ID,
            "no_solution_found",
            offline=offline,
            online=online,
            table_entries=len(table),
            table_bytes=len(table) * 64,
            legacy_operations=legacy_operations,
            algorithm_spec={"width": width, **DERIVED_FROM[BSGS_METHOD_ID]},
        )

    self_check, matched = _self_check(curve, candidate, generator, target)
    independently_validated = validate_candidate_independently(
        field_p=curve.p,
        curve_a=curve.a,
        curve_b=curve.b,
        generator=generator,
        target=target,
        subgroup_order=order,
        candidate_scalar=candidate,
    )
    if not matched or not independently_validated:
        return _failure(
            BSGS_METHOD_ID,
            "candidate_validation_failed",
            offline=offline,
            online=online,
            self_check=self_check,
            table_entries=len(table),
            table_bytes=len(table) * 64,
            legacy_operations=legacy_operations,
            algorithm_spec={"width": width, **DERIVED_FROM[BSGS_METHOD_ID]},
        )

    return ReferenceResult(
        method_id=BSGS_METHOD_ID,
        status="success",
        candidate_scalar=candidate,
        failure_code=None,
        offline_setup=offline,
        online_target=online,
        method_self_check=self_check,
        table_entries=len(table),
        estimated_algorithmic_table_bytes=len(table) * 64,
        legacy_p1_group_operations=legacy_operations,
        restarts=0,
        collisions=0,
        noninvertible_collisions=0,
        distinguished_points=0,
        state_steps=0,
        independently_validated=True,
        algorithm_spec={"width": width, **DERIVED_FROM[BSGS_METHOD_ID]},
        memory_semantics="historical_64_bytes_per_table_entry_estimate",
    )


def solve_ordinary_rho(
    curve: Curve,
    order: int,
    generator: tuple[int, int],
    target: Point,
    *,
    seed: int,
    budget: MethodBudget | None = None,
    partitioner: Callable[[Point], int] | None = None,
) -> ReferenceResult:
    """Frozen ordinary 3-partition Pollard rho with Floyd cycle detection."""

    budget = budget or MethodBudget()
    _validate_instance(curve, order, generator, target)
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise ValueError("algorithm seed must be a non-negative integer")
    partitioner = partitioner or (lambda point: 0 if point is None else point[0] % 3)

    maximum_steps = 8 * math.ceil(math.sqrt(order))
    shared = InvocationBudget(budget.max_group_law_invocations)
    online_curve = CountingCurve(curve, invocation_budget=shared)
    state_steps = 0
    collisions = 0
    noninvertible = 0
    completed_restarts = 0
    candidate: int | None = None

    def step(state: tuple[Point, int, int]) -> tuple[Point, int, int]:
        nonlocal state_steps
        if state_steps >= budget.max_steps:
            raise BudgetExceeded("max_steps exceeded")
        point, left, right = state
        partition = partitioner(point)
        if partition not in (0, 1, 2):
            raise ValueError("partitioner must return 0, 1, or 2")
        if partition == 0:
            point = online_curve.add(point, generator)
            left = (left + 1) % order
        elif partition == 1:
            point = online_curve.add(point, point)
            left = 2 * left % order
            right = 2 * right % order
        else:
            point = online_curve.add(point, target)
            right = (right + 1) % order
        state_steps += 1
        return point, left, right

    failure_code = "no_solution_within_frozen_restarts"
    try:
        for restart in range(int(RHO_SPEC["restart_count"])):
            completed_restarts = restart
            digest = hashlib.sha256(
                f"keyai/p1-rho/{seed}/{restart}".encode("ascii")
            ).digest()
            left = 1 + int.from_bytes(digest[:8], "big") % (order - 1)
            right = 1 + int.from_bytes(digest[8:16], "big") % (order - 1)
            left_point = online_curve.scalar_mul(left, generator)
            right_point = online_curve.scalar_mul(right, target)
            start = (online_curve.add(left_point, right_point), left, right)
            tortoise = step(start)
            hare = step(step(start))
            for _ in range(maximum_steps):
                if tortoise[0] == hare[0]:
                    collisions += 1
                    numerator = (tortoise[1] - hare[1]) % order
                    denominator = (hare[2] - tortoise[2]) % order
                    if denominator == 0:
                        noninvertible += 1
                        break
                    try:
                        inverse = pow(denominator, -1, order)
                    except ValueError:
                        noninvertible += 1
                        break
                    proposed = numerator * inverse % order
                    if curve.scalar_mul(proposed, generator) == target:
                        candidate = proposed
                    break
                tortoise = step(tortoise)
                hare = step(step(hare))
            if candidate is not None:
                break
    except BudgetExceeded as error:
        failure_code = (
            "step_budget_exhausted"
            if "max_steps" in str(error)
            else "group_law_budget_exhausted"
        )

    online = online_curve.snapshot()
    if candidate is None:
        return _failure(
            RHO_METHOD_ID,
            failure_code,
            online=online,
            table_bytes=1024,
            legacy_operations=online.group_law_invocations,
            restarts=completed_restarts,
            collisions=collisions,
            noninvertible_collisions=noninvertible,
            state_steps=state_steps,
            algorithm_spec={**RHO_SPEC, **DERIVED_FROM[RHO_METHOD_ID]},
            memory_semantics="historical_constant_1024_byte_estimate",
        )

    self_check, matched = _self_check(curve, candidate, generator, target)
    independently_validated = validate_candidate_independently(
        field_p=curve.p,
        curve_a=curve.a,
        curve_b=curve.b,
        generator=generator,
        target=target,
        subgroup_order=order,
        candidate_scalar=candidate,
    )
    if not matched or not independently_validated:
        return _failure(
            RHO_METHOD_ID,
            "candidate_validation_failed",
            online=online,
            self_check=self_check,
            table_bytes=1024,
            legacy_operations=online.group_law_invocations,
            restarts=completed_restarts,
            collisions=collisions,
            noninvertible_collisions=noninvertible,
            state_steps=state_steps,
            algorithm_spec={**RHO_SPEC, **DERIVED_FROM[RHO_METHOD_ID]},
            memory_semantics="historical_constant_1024_byte_estimate",
        )

    return ReferenceResult(
        method_id=RHO_METHOD_ID,
        status="success",
        candidate_scalar=candidate,
        failure_code=None,
        offline_setup=_empty_snapshot(),
        online_target=online,
        method_self_check=self_check,
        table_entries=0,
        estimated_algorithmic_table_bytes=1024,
        legacy_p1_group_operations=online.group_law_invocations,
        restarts=completed_restarts,
        collisions=collisions,
        noninvertible_collisions=noninvertible,
        distinguished_points=0,
        state_steps=state_steps,
        independently_validated=True,
        algorithm_spec={**RHO_SPEC, **DERIVED_FROM[RHO_METHOD_ID]},
        memory_semantics="historical_constant_1024_byte_estimate",
    )


def solve_reference(
    method_id: str,
    curve: Curve,
    order: int,
    generator: tuple[int, int],
    target: Point,
    *,
    seed: int = 0,
    budget: MethodBudget | None = None,
) -> ReferenceResult:
    if method_id == BSGS_METHOD_ID:
        return solve_bsgs(curve, order, generator, target, budget=budget)
    if method_id in {RHO_METHOD_ID, "pollard_rho"}:
        return solve_ordinary_rho(
            curve,
            order,
            generator,
            target,
            seed=seed,
            budget=budget,
        )
    raise ValueError(f"unsupported reference method: {method_id}")


def _contains_secret_field(value: Any) -> bool:
    forbidden = {
        "scalar",
        "expected_scalar",
        "target_scalar",
        "private_seed",
        "target_generation_seed",
    }
    if isinstance(value, Mapping):
        return any(
            key in forbidden or _contains_secret_field(child)
            for key, child in value.items()
        )
    if isinstance(value, list):
        return any(_contains_secret_field(child) for child in value)
    return False


def solve_method_request(request: Mapping[str, Any]) -> ReferenceResult:
    """Execute one sanitized P01 ``method_request_v1`` mapping."""

    if request.get("contract_kind") != "method_request_v1":
        raise ValueError("expected method_request_v1")
    if _contains_secret_field(request):
        raise ValueError("method request contains target-secret material")
    if any(
        request.get(name) is not None
        for name in ("candidate_id", "hypothesis_id", "authorization_id")
    ):
        raise ValueError("lab reference methods accept no scientific identifiers")
    if request.get("native_research_outcome") is not False:
        raise ValueError("lab method request cannot be a native research outcome")

    curve_data = request["curve"]
    curve = Curve(
        int(curve_data["field_p"]),
        int(curve_data["curve_a"]),
        int(curve_data["curve_b"]),
    )
    generator_raw = request["generator"]
    target_raw = request["target"]
    generator = (int(generator_raw[0]), int(generator_raw[1]))
    target: Point = (
        None if target_raw is None else (int(target_raw[0]), int(target_raw[1]))
    )
    budget = MethodBudget.from_mapping(request["budgets"])
    return solve_reference(
        str(request["method_id"]),
        curve,
        int(request["subgroup_order"]),
        generator,
        target,
        seed=int(request["algorithm_seed"]),
        budget=budget,
    )


__all__ = [
    "BSGS_METHOD_ID",
    "DERIVED_FROM",
    "MethodBudget",
    "RHO_METHOD_ID",
    "RHO_SPEC",
    "ReferenceResult",
    "solve_bsgs",
    "solve_method_request",
    "solve_ordinary_rho",
    "solve_reference",
]
