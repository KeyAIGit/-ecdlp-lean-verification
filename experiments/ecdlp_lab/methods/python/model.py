"""Public, secret-free values shared by the P03 Python reference methods.

The solver boundary is deliberately narrower than ``method_request_v1``.  It
contains only public curve data, public target data, deterministic budgets and
the selected method/seed.  It has no opaque record identifiers,
target-generation scalar, derivation seed, private receipt or legacy source
row.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

Point = tuple[int, int] | None
FinitePoint = tuple[int, int]

METHOD_IDS = frozenset({"bsgs_v1", "ordinary_rho_xmod3_v1"})
PHASE_NAMES = frozenset({"offline_setup", "online_target", "method_self_check"})
MAX_U64 = (1 << 64) - 1
MAX_TOY_INTEGER = (1 << 32) - 1

FAILURE_DETAILS = {
    "group_operation_budget_exhausted": "group-operation budget exhausted",
    "table_budget_exhausted": "table-entry budget exhausted",
    "step_budget_exhausted": "deterministic step budget exhausted",
    "restart_budget_exhausted": "frozen restart budget exhausted",
    "memory_budget_exhausted": "algorithmic memory-estimate budget exhausted",
    "process_timeout": "cooperative cancellation requested",
    "process_terminated": "method process terminated",
    "no_solution": "no discrete logarithm found within the frozen walk",
    "invalid_public_input": "public method input rejected",
    "backend_error": "curve backend failed",
}


def _exact_int(value: Any, name: str, *, minimum: int = 0, maximum: int | None = None) -> int:
    if type(value) is not int or value < minimum or (
        maximum is not None and value > maximum
    ):
        upper = "" if maximum is None else f" and <= {maximum}"
        raise ValueError(f"{name} must be an integer >= {minimum}{upper}")
    return value


def _finite_point(value: Any, name: str, modulus: int) -> FinitePoint:
    if (
        not isinstance(value, (tuple, list))
        or len(value) != 2
        or any(type(coordinate) is not int for coordinate in value)
    ):
        raise ValueError(f"{name} must contain exactly two integers")
    point = (value[0], value[1])
    if any(coordinate < 0 or coordinate >= modulus for coordinate in point):
        raise ValueError(f"{name} coordinates must be canonical field elements")
    return point


@dataclass(frozen=True)
class MethodBudgets:
    """Deterministic P03 budgets copied exactly from a method request."""

    max_subgroup_order_bits: int
    max_field_bits: int
    max_group_law_invocations: int
    max_table_entries: int
    max_steps: int
    timeout_ns: int
    max_memory_bytes: int
    workers: int

    def __post_init__(self) -> None:
        for name in (
            "max_subgroup_order_bits",
            "max_field_bits",
            "max_group_law_invocations",
            "max_table_entries",
            "max_steps",
            "timeout_ns",
            "max_memory_bytes",
            "workers",
        ):
            _exact_int(getattr(self, name), name, minimum=1)
        if self.max_subgroup_order_bits > 32 or self.max_field_bits > 32:
            raise ValueError("P03 budgets cannot authorize fields or subgroups above 32 bits")
        if self.workers != 1:
            raise ValueError("P03 reference methods require exactly one worker")

    @classmethod
    def from_mapping(cls, value: Any) -> "MethodBudgets":
        names = tuple(cls.__dataclass_fields__)
        if not isinstance(value, Mapping) or set(value) != set(names):
            raise ValueError("budgets must contain exactly the eight frozen budget fields")
        return cls(**{name: value[name] for name in names})

    def as_dict(self) -> dict[str, int]:
        return {name: getattr(self, name) for name in self.__dataclass_fields__}


@dataclass(frozen=True)
class PhaseCounters:
    group_law_invocations: int = 0
    nontrivial_additions: int = 0
    doublings: int = 0
    negations: int = 0
    field_inversions: int | None = None
    field_multiplications: int | None = None
    field_squarings: int | None = None

    def __post_init__(self) -> None:
        for name in (
            "group_law_invocations",
            "nontrivial_additions",
            "doublings",
            "negations",
        ):
            _exact_int(getattr(self, name), name)
        if self.nontrivial_additions + self.doublings > self.group_law_invocations:
            raise ValueError("addition/doubling counters exceed group-law invocations")
        for name in (
            "field_inversions",
            "field_multiplications",
            "field_squarings",
        ):
            value = getattr(self, name)
            if value is not None:
                _exact_int(value, name)

    def as_dict(self) -> dict[str, int | None]:
        return {name: getattr(self, name) for name in self.__dataclass_fields__}


@dataclass(frozen=True)
class MethodCounters:
    counter_semantics_id: str = "affine_group_calls_v1"
    field_counter_semantics: str = "not_instrumented"
    offline_setup: PhaseCounters = field(default_factory=PhaseCounters)
    online_target: PhaseCounters = field(default_factory=PhaseCounters)
    method_self_check: PhaseCounters = field(default_factory=PhaseCounters)
    table_entries: int = 0
    estimated_algorithmic_table_bytes: int = 0
    restarts: int = 0
    collisions: int = 0
    noninvertible_collisions: int = 0
    distinguished_points: int = 0
    legacy_p1_group_operations: int | None = None

    def __post_init__(self) -> None:
        if self.counter_semantics_id != "affine_group_calls_v1":
            raise ValueError("unknown counter semantics")
        if self.field_counter_semantics != "not_instrumented":
            raise ValueError("P03 does not instrument field-operation counters")
        for name in (
            "table_entries",
            "estimated_algorithmic_table_bytes",
            "restarts",
            "collisions",
            "noninvertible_collisions",
            "distinguished_points",
        ):
            _exact_int(getattr(self, name), name)
        if self.noninvertible_collisions > self.collisions:
            raise ValueError("noninvertible collisions must be a collision subset")
        if self.legacy_p1_group_operations is not None:
            _exact_int(self.legacy_p1_group_operations, "legacy_p1_group_operations")

    def as_dict(self) -> dict[str, Any]:
        return {
            "counter_semantics_id": self.counter_semantics_id,
            "field_counter_semantics": self.field_counter_semantics,
            "offline_setup": self.offline_setup.as_dict(),
            "online_target": self.online_target.as_dict(),
            "method_self_check": self.method_self_check.as_dict(),
            "table_entries": self.table_entries,
            "estimated_algorithmic_table_bytes": self.estimated_algorithmic_table_bytes,
            "restarts": self.restarts,
            "collisions": self.collisions,
            "noninvertible_collisions": self.noninvertible_collisions,
            "distinguished_points": self.distinguished_points,
            "legacy_p1_group_operations": self.legacy_p1_group_operations,
        }


@dataclass(frozen=True)
class MethodFailure:
    code: str
    detail: str

    def __post_init__(self) -> None:
        if self.code not in FAILURE_DETAILS:
            raise ValueError("unknown method failure code")
        if self.detail != FAILURE_DETAILS[self.code]:
            raise ValueError("failure detail must use the fixed public message")

    @classmethod
    def fixed(cls, code: str) -> "MethodFailure":
        return cls(code=code, detail=FAILURE_DETAILS[code])

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "detail": self.detail}


@dataclass(frozen=True)
class SolverDiagnostics:
    """Non-contract replay diagnostics; never serialized into method counters."""

    deterministic_steps: int = 0
    floyd_iterations: int = 0
    invalid_candidate_collisions: int = 0
    attempts: int = 0

    def __post_init__(self) -> None:
        for name in self.__dataclass_fields__:
            _exact_int(getattr(self, name), name)


@dataclass(frozen=True)
class SolverOutcome:
    status: str
    candidate_scalar: int | None
    failure: MethodFailure | None
    counters: MethodCounters = field(default_factory=MethodCounters)
    diagnostics: SolverDiagnostics = field(default_factory=SolverDiagnostics)

    def __post_init__(self) -> None:
        if self.status not in {"success", "bounded_failure", "invalid_request", "internal_error"}:
            raise ValueError("unknown method status")
        if self.status == "success":
            _exact_int(
                self.candidate_scalar,
                "candidate_scalar",
                maximum=MAX_TOY_INTEGER,
            )
            if self.failure is not None:
                raise ValueError("successful outcome cannot contain a failure")
        elif self.candidate_scalar is not None or self.failure is None:
            raise ValueError("failed outcome requires null candidate and a failure")

    @property
    def success(self) -> bool:
        return self.status == "success"

    @property
    def passed(self) -> bool:
        return self.success

    @property
    def candidate(self) -> int | None:
        return self.candidate_scalar

    @classmethod
    def succeeded(
        cls,
        candidate: int,
        counters: MethodCounters,
        diagnostics: SolverDiagnostics | None = None,
    ) -> "SolverOutcome":
        return cls(
            "success", candidate, None, counters, diagnostics or SolverDiagnostics()
        )

    @classmethod
    def failed(
        cls,
        code: str,
        counters: MethodCounters | None = None,
        *,
        status: str | None = None,
        diagnostics: SolverDiagnostics | None = None,
    ) -> "SolverOutcome":
        if status is None:
            status = (
                "invalid_request"
                if code == "invalid_public_input"
                else "internal_error"
                if code == "backend_error"
                else "bounded_failure"
            )
        return cls(
            status,
            None,
            MethodFailure.fixed(code),
            counters or MethodCounters(),
            diagnostics or SolverDiagnostics(),
        )


@dataclass(frozen=True)
class PublicMethodInput:
    """Minimal solver projection with no metadata or identifier channels."""

    method_id: str
    algorithm_seed: int
    p: int
    a: int
    b: int
    G: FinitePoint
    Q: FinitePoint
    ell: int
    budgets: MethodBudgets

    def __post_init__(self) -> None:
        if self.method_id not in METHOD_IDS:
            raise ValueError("method_id is not a frozen P03 method")
        _exact_int(self.algorithm_seed, "algorithm_seed", maximum=MAX_U64)
        if not isinstance(self.budgets, MethodBudgets):
            raise ValueError("budgets must be MethodBudgets")
        _exact_int(self.p, "p", minimum=5, maximum=MAX_TOY_INTEGER)
        for name in ("a", "b"):
            _exact_int(getattr(self, name), name, maximum=self.p - 1)
        object.__setattr__(self, "G", _finite_point(self.G, "G", self.p))
        object.__setattr__(self, "Q", _finite_point(self.Q, "Q", self.p))
        _exact_int(self.ell, "ell", minimum=2, maximum=MAX_TOY_INTEGER)
        if self.p.bit_length() > self.budgets.max_field_bits or (
            self.ell.bit_length() > self.budgets.max_subgroup_order_bits
        ):
            raise ValueError("public curve exceeds its declared bit budgets")

    @property
    def field_p(self) -> int:
        return self.p

    @property
    def curve_a(self) -> int:
        return self.a

    @property
    def curve_b(self) -> int:
        return self.b

    @property
    def generator(self) -> FinitePoint:
        return self.G

    @property
    def target(self) -> FinitePoint:
        return self.Q

    @property
    def subgroup_order(self) -> int:
        return self.ell

    @property
    def seed(self) -> int:
        return self.algorithm_seed


@dataclass(frozen=True)
class SanitizationResult:
    public_input: PublicMethodInput | None
    failure: MethodFailure | None

    def __post_init__(self) -> None:
        if (self.public_input is None) == (self.failure is None):
            raise ValueError("sanitization returns exactly one of input or failure")

    @property
    def passed(self) -> bool:
        return self.public_input is not None


__all__ = [
    "FAILURE_DETAILS",
    "METHOD_IDS",
    "MAX_U64",
    "FinitePoint",
    "MethodBudgets",
    "MethodCounters",
    "MethodFailure",
    "PhaseCounters",
    "Point",
    "PublicMethodInput",
    "SanitizationResult",
    "SolverDiagnostics",
    "SolverOutcome",
]
