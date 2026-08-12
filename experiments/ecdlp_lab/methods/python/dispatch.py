"""Fail-closed public request projection and P03 method dispatch."""

from __future__ import annotations

from typing import Any, Callable, Mapping

from experiments.ecdlp_lab.curves.model import ResolvedCurveFixture
from experiments.ml_structure_probe.p1_toy_scaling.curve_math import (
    Curve,
    is_prime,
)

from .bsgs import solve_bsgs_cold
from .counting import CurveBackend
from .model import (
    METHOD_IDS,
    MethodBudgets,
    MethodFailure,
    PublicMethodInput,
    SanitizationResult,
    SolverOutcome,
)
from .rho import solve_ordinary_rho

_REQUEST_KEYS = frozenset(
    {
        "schema_version",
        "record_kind",
        "contract_kind",
        "internal_classification",
        "framework_authorization_class",
        "hypothesis_id",
        "candidate_id",
        "authorization_id",
        "native_research_outcome",
        "route_effect",
        "retention_class",
        "retainable",
        "provenance",
        "request_id",
        "work_unit_id",
        "attempt_id",
        "method_id",
        "algorithm_seed",
        "curve_catalog_sha256",
        "curve_fixture_id",
        "public_target_vector_sha256",
        "curve",
        "generator",
        "target",
        "subgroup_order",
        "subgroup_order_bits",
        "budgets",
        "public_scalar_interval",
        "public_precomputation",
    }
)
_CURVE_KEYS = frozenset(
    {"curve_id", "field_bits", "field_p", "curve_a", "curve_b"}
)
_FORBIDDEN_KEYS = frozenset(
    {
        "answer",
        "candidate_scalar",
        "derivation_seed",
        "expected_scalar",
        "legacy_source_record",
        "private_payload",
        "private_target",
        "scalar",
        "secret",
        "source_record",
        "target_generation_seed",
    }
)


def _contains_forbidden_key(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if not isinstance(key, str) or key.lower() in _FORBIDDEN_KEYS:
                return True
            if _contains_forbidden_key(child):
                return True
    elif isinstance(value, (list, tuple)):
        return any(_contains_forbidden_key(child) for child in value)
    return False


def _point(value: Any) -> tuple[int, int]:
    if (
        not isinstance(value, (list, tuple))
        or len(value) != 2
        or any(type(coordinate) is not int for coordinate in value)
    ):
        raise ValueError("point must contain exactly two exact integers")
    return value[0], value[1]


def _fixture_matches(record: Mapping[str, Any], fixture: ResolvedCurveFixture) -> bool:
    curve = record.get("curve")
    if not isinstance(curve, Mapping) or set(curve) != _CURVE_KEYS:
        return False
    try:
        generator = _point(record.get("generator"))
    except ValueError:
        return False
    return (
        record.get("curve_catalog_sha256") == fixture.catalog_sha256
        and record.get("curve_fixture_id") == fixture.fixture_id
        and curve.get("curve_id") == fixture.curve_id
        and curve.get("field_bits") == fixture.field_bits
        and curve.get("field_p") == fixture.field_p
        and curve.get("curve_a") == fixture.curve_a
        and curve.get("curve_b") == fixture.curve_b
        and generator == fixture.generator
        and record.get("subgroup_order") == fixture.subgroup_order
        and record.get("subgroup_order_bits") == fixture.subgroup_order_bits
    )


def _public_curve_valid(public_input: PublicMethodInput) -> bool:
    """Method-side validation, independent from the decisive output oracle."""

    try:
        if not is_prime(public_input.ell):
            return False
        curve = Curve(public_input.p, public_input.a, public_input.b)
        return curve.is_on_curve(public_input.G) and curve.is_on_curve(public_input.Q)
    except (TypeError, ValueError, ArithmeticError):
        return False


def sanitize_method_request(
    record: Mapping[str, Any],
    *,
    resolved_fixture: ResolvedCurveFixture,
) -> SanitizationResult:
    """Project one fully public contract record onto the method-only boundary."""

    invalid = SanitizationResult(None, MethodFailure.fixed("invalid_public_input"))
    if not isinstance(record, Mapping) or not isinstance(
        resolved_fixture, ResolvedCurveFixture
    ):
        return invalid
    if set(record) != _REQUEST_KEYS or _contains_forbidden_key(record):
        return invalid
    if (
        record.get("schema_version") != 1
        or record.get("record_kind") != "lab_engineering_fixture"
        or record.get("contract_kind") != "method_request_v1"
        or record.get("internal_classification") != "engineering_only"
        or record.get("framework_authorization_class") != "fixture"
        or record.get("hypothesis_id") is not None
        or record.get("candidate_id") is not None
        or record.get("authorization_id") is not None
        or record.get("native_research_outcome") is not False
        or record.get("route_effect") != "none"
        or record.get("retention_class") != "engineering_only"
        or record.get("retainable") is not False
        or record.get("method_id") not in METHOD_IDS
        or record.get("public_scalar_interval") is not None
        or record.get("public_precomputation") is not None
        or not _fixture_matches(record, resolved_fixture)
    ):
        return invalid
    curve = record.get("curve")
    try:
        public_input = PublicMethodInput(
            method_id=record["method_id"],
            algorithm_seed=record["algorithm_seed"],
            p=curve["field_p"],
            a=curve["curve_a"],
            b=curve["curve_b"],
            G=_point(record["generator"]),
            Q=_point(record["target"]),
            ell=record["subgroup_order"],
            budgets=MethodBudgets.from_mapping(record["budgets"]),
        )
    except (KeyError, TypeError, ValueError):
        return invalid
    if not _public_curve_valid(public_input):
        return invalid
    return SanitizationResult(public_input, None)


def _backend_matches(backend: CurveBackend, public_input: PublicMethodInput) -> bool:
    return (
        getattr(backend, "p", None) == public_input.p
        and getattr(backend, "a", None) == public_input.a
        and getattr(backend, "b", None) == public_input.b
    )


def run_method(
    public_input: PublicMethodInput,
    *,
    backend: CurveBackend | None = None,
    cancelled: Callable[[], bool] | None = None,
    self_check: bool = True,
) -> SolverOutcome:
    """Dispatch exactly one sanitized public input to an allowlisted method."""

    if (
        not isinstance(public_input, PublicMethodInput)
        or type(self_check) is not bool
        or not _public_curve_valid(public_input)
    ):
        return SolverOutcome.failed("invalid_public_input")
    try:
        selected_backend = (
            backend
            if backend is not None
            else Curve(public_input.p, public_input.a, public_input.b)
        )
        if not _backend_matches(selected_backend, public_input):
            return SolverOutcome.failed("invalid_public_input")
        if public_input.method_id == "bsgs_v1":
            return solve_bsgs_cold(
                selected_backend,
                public_input.G,
                public_input.Q,
                public_input.ell,
                public_input.budgets,
                self_check=self_check,
                cancelled=cancelled,
            )
        if public_input.method_id == "ordinary_rho_xmod3_v1":
            return solve_ordinary_rho(
                selected_backend,
                public_input.G,
                public_input.Q,
                public_input.ell,
                public_input.algorithm_seed,
                public_input.budgets,
                self_check=self_check,
                cancelled=cancelled,
            )
    except Exception:
        return SolverOutcome.failed("backend_error")
    return SolverOutcome.failed("invalid_public_input")


def dispatch_method_request(
    record: Mapping[str, Any],
    *,
    resolved_fixture: ResolvedCurveFixture,
    cancelled: Callable[[], bool] | None = None,
    self_check: bool = True,
) -> SolverOutcome:
    sanitized = sanitize_method_request(record, resolved_fixture=resolved_fixture)
    if sanitized.public_input is None:
        return SolverOutcome.failed("invalid_public_input")
    return run_method(
        sanitized.public_input, cancelled=cancelled, self_check=self_check
    )


__all__ = [
    "dispatch_method_request",
    "run_method",
    "sanitize_method_request",
]
