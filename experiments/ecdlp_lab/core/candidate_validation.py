"""Independent validation of one public ECDLP candidate.

The validator deliberately depends only on the small framework oracle.  It
does not import a method implementation, a catalog producer, or replay data.
Callers pass the structural public method input (``p``, ``a``, ``b``, ``G``,
``Q``, and ``ell``) and the scalar returned by a method. Oracle work stays
private to this module and is reported in a separate validator-only counter
bucket; it is never folded into method counters.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from experiments.framework.ec_oracle import (
    MAX_TOY_FIELD,
    Curve as OracleCurve,
    is_prime,
)

from .issues import Issue


Point = tuple[int, int] | None


class PublicCandidateInput(Protocol):
    """Structural boundary consumed by :func:`validate_candidate`."""

    p: int
    a: int
    b: int
    G: Point
    Q: Point
    ell: int


@dataclass(frozen=True)
class ValidatorCounters:
    """Completed framework-oracle group calls, separated by validation phase."""

    counter_semantics_id: str = "framework_oracle_group_calls_v1"
    generator_subgroup_check: int = 0
    target_subgroup_check: int = 0
    candidate_relation_check: int = 0

    def __post_init__(self) -> None:
        if self.counter_semantics_id != "framework_oracle_group_calls_v1":
            raise ValueError("unknown validator counter semantics")
        for name in (
            "generator_subgroup_check",
            "target_subgroup_check",
            "candidate_relation_check",
        ):
            value = getattr(self, name)
            if type(value) is not int or value < 0:
                raise ValueError(f"{name} must be a nonnegative exact integer")

    @property
    def total_group_law_invocations(self) -> int:
        return (
            self.generator_subgroup_check
            + self.target_subgroup_check
            + self.candidate_relation_check
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "counter_semantics_id": self.counter_semantics_id,
            "generator_subgroup_check": self.generator_subgroup_check,
            "target_subgroup_check": self.target_subgroup_check,
            "candidate_relation_check": self.candidate_relation_check,
            "total_group_law_invocations": self.total_group_law_invocations,
        }


_VALIDATOR_PHASES = (
    "generator_subgroup_check",
    "target_subgroup_check",
    "candidate_relation_check",
)


class _CountingOracleCurve(OracleCurve):
    """Instrument the independent oracle without replacing its point results."""

    def __post_init__(self) -> None:
        super().__post_init__()
        object.__setattr__(
            self,
            "_validator_counter_state",
            {
                "phase": None,
                "counts": {phase: 0 for phase in _VALIDATOR_PHASES},
            },
        )

    def add(self, left: Point, right: Point) -> Point:
        result = super().add(left, right)
        phase = self._validator_counter_state["phase"]
        if phase is not None:
            self._validator_counter_state["counts"][phase] += 1
        return result

    def scalar_mul_counted(self, phase: str, scalar: int, point: Point) -> Point:
        if phase not in _VALIDATOR_PHASES:
            raise ValueError("unknown validator counter phase")
        if self._validator_counter_state["phase"] is not None:
            raise RuntimeError("validator counter phases cannot be nested")
        self._validator_counter_state["phase"] = phase
        try:
            return super().scalar_mul(scalar, point)
        finally:
            self._validator_counter_state["phase"] = None

    def validator_counters(self) -> ValidatorCounters:
        counts = self._validator_counter_state["counts"]
        return ValidatorCounters(
            generator_subgroup_check=counts["generator_subgroup_check"],
            target_subgroup_check=counts["target_subgroup_check"],
            candidate_relation_check=counts["candidate_relation_check"],
        )


@dataclass(frozen=True)
class CandidateValidation:
    """Timing-free independent validation result with separate oracle counters."""

    candidate: int | None
    relation_verified: bool
    issues: tuple[Issue, ...]
    counters: ValidatorCounters = ValidatorCounters()

    @property
    def passed(self) -> bool:
        return self.relation_verified and not self.issues

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "report_kind": "ecdlp_lab_candidate_validation_v1",
            "candidate": self.candidate,
            "relation_verified": self.relation_verified,
            "passed": self.passed,
            "validator_counters": self.counters.to_dict(),
            "issues": [
                {"code": issue.code, "path": issue.path, "message": issue.message}
                for issue in self.issues
            ],
        }


@dataclass(frozen=True)
class PublicInputValidation:
    """Independent subgroup validation when a method returns no candidate."""

    issues: tuple[Issue, ...]
    counters: ValidatorCounters = ValidatorCounters()

    @property
    def passed(self) -> bool:
        return not self.issues

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "report_kind": "ecdlp_lab_public_input_validation_v1",
            "public_input_valid": self.passed,
            "passed": self.passed,
            "validator_counters": self.counters.to_dict(),
            "issues": [
                {"code": issue.code, "path": issue.path, "message": issue.message}
                for issue in self.issues
            ],
        }


def _problem(code: str, path: str, message: str) -> Issue:
    return Issue(f"candidate.{code}", path, message)


def _integer(
    value: Any,
    *,
    path: str,
    minimum: int,
    maximum: int,
    issues: list[Issue],
) -> int | None:
    if type(value) is not int:
        issues.append(
            _problem("input.integer", path, "must be an integer (booleans are forbidden)")
        )
        return None
    if not minimum <= value <= maximum:
        issues.append(
            _problem(
                "input.range",
                path,
                f"must be in the inclusive range [{minimum}, {maximum}]",
            )
        )
        return None
    return value


def _point(
    value: Any,
    *,
    path: str,
    p: int,
    allow_infinity: bool,
    issues: list[Issue],
) -> Point | object:
    if value is None:
        if allow_infinity:
            return None
        issues.append(_problem("input.point", path, "must not be the point at infinity"))
        return _INVALID
    if (
        type(value) is not tuple
        or len(value) != 2
        or any(type(coordinate) is not int for coordinate in value)
    ):
        issues.append(
            _problem(
                "input.point",
                path,
                "must be a canonical two-integer tuple or an authorized infinity",
            )
        )
        return _INVALID
    if any(not 0 <= coordinate < p for coordinate in value):
        issues.append(
            _problem("input.point", path, "coordinates must be canonical field elements")
        )
        return _INVALID
    return value


_INVALID = object()


def _public_fields(
    public_input: PublicCandidateInput | Any,
) -> tuple[Any, Any, Any, Any, Any, Any] | None:
    try:
        return (
            getattr(public_input, "p"),
            getattr(public_input, "a"),
            getattr(public_input, "b"),
            getattr(public_input, "G"),
            getattr(public_input, "Q"),
            getattr(public_input, "ell"),
        )
    except (AttributeError, RuntimeError, TypeError, ValueError):
        return None


def _candidate_value(value: Any, issues: list[Issue]) -> Any:
    """Accept an exact scalar or the structural successful solver outcome."""

    if type(value) is int:
        return value
    try:
        status = getattr(value, "status")
        candidate_scalar = getattr(value, "candidate_scalar")
    except (AttributeError, RuntimeError, TypeError, ValueError):
        return value
    if status != "success":
        issues.append(
            _problem(
                "outcome.status",
                "$.outcome.status",
                "only a successful solver outcome contains a candidate to validate",
            )
        )
        return _INVALID
    return candidate_scalar


def validate_candidate(
    public_input: PublicCandidateInput | Any,
    candidate: Any,
) -> CandidateValidation:
    """Validate ``0 <= candidate < ell`` and ``[candidate]G == Q``.

    Malformed public inputs and scalar aliases fail closed before the oracle
    performs candidate multiplication.  Subgroup membership is checked
    independently as part of the same boundary.
    """

    issues: list[Issue] = []
    fields = _public_fields(public_input)
    if fields is None:
        issues.append(
            _problem(
                "input.shape",
                "$",
                "public input must expose exactly the structural p/a/b/G/Q/ell boundary",
            )
        )
        return CandidateValidation(None, False, tuple(issues))
    raw_p, raw_a, raw_b, raw_g, raw_q, raw_ell = fields

    p = _integer(
        raw_p,
        path="$.p",
        minimum=5,
        maximum=MAX_TOY_FIELD,
        issues=issues,
    )
    if p is None:
        return CandidateValidation(None, False, tuple(sorted(set(issues))))
    a = _integer(raw_a, path="$.a", minimum=0, maximum=p - 1, issues=issues)
    b = _integer(raw_b, path="$.b", minimum=0, maximum=p - 1, issues=issues)
    ell = _integer(
        raw_ell,
        path="$.ell",
        minimum=2,
        maximum=MAX_TOY_FIELD,
        issues=issues,
    )
    raw_candidate = _candidate_value(candidate, issues)
    if raw_candidate is _INVALID:
        return CandidateValidation(None, False, tuple(sorted(set(issues))))
    normalized_candidate = _integer(
        raw_candidate,
        path="$.candidate",
        minimum=0,
        maximum=ell - 1 if ell is not None else 0,
        issues=issues,
    )
    g = _point(
        raw_g,
        path="$.G",
        p=p,
        allow_infinity=False,
        issues=issues,
    )
    q = _point(
        raw_q,
        path="$.Q",
        p=p,
        allow_infinity=True,
        issues=issues,
    )
    if (
        a is None
        or b is None
        or ell is None
        or normalized_candidate is None
        or g is _INVALID
        or q is _INVALID
    ):
        return CandidateValidation(
            normalized_candidate, False, tuple(sorted(set(issues)))
        )
    if not is_prime(ell):
        issues.append(_problem("order.prime", "$.ell", "subgroup order must be prime"))

    try:
        curve = _CountingOracleCurve(p=p, a=a, b=b)
    except (TypeError, ValueError) as error:
        issues.append(_problem("curve", "$", str(error)))
        return CandidateValidation(
            normalized_candidate, False, tuple(sorted(set(issues)))
        )

    if not curve.is_on_curve(g):
        issues.append(_problem("point.off_curve", "$.G", "generator is not on the curve"))
    if not curve.is_on_curve(q):
        issues.append(_problem("point.off_curve", "$.Q", "target is not on the curve"))
    if issues:
        return CandidateValidation(
            normalized_candidate, False, tuple(sorted(set(issues)))
        )

    try:
        if curve.scalar_mul_counted("generator_subgroup_check", ell, g) is not None:
            issues.append(
                _problem(
                    "order.generator",
                    "$.ell",
                    "declared subgroup order does not annihilate the generator",
                )
            )
        if curve.scalar_mul_counted("target_subgroup_check", ell, q) is not None:
            issues.append(
                _problem(
                    "order.target",
                    "$.Q",
                    "target is not in the declared subgroup",
                )
            )
    except (TypeError, ValueError, ArithmeticError) as error:
        issues.append(_problem("oracle", "$", f"subgroup check failed: {error}"))

    relation_verified = False
    if not issues and normalized_candidate is not None:
        try:
            relation_verified = (
                curve.scalar_mul_counted(
                    "candidate_relation_check", normalized_candidate, g
                )
                == q
            )
        except (TypeError, ValueError, ArithmeticError) as error:
            issues.append(_problem("oracle", "$", f"candidate check failed: {error}"))
        if not relation_verified and not issues:
            issues.append(
                _problem(
                    "relation",
                    "$.candidate",
                    "candidate does not satisfy [candidate]G = Q",
                )
            )
    return CandidateValidation(
        normalized_candidate,
        relation_verified,
        tuple(sorted(set(issues))),
        curve.validator_counters(),
    )


def validate_public_input(
    public_input: PublicCandidateInput | Any,
) -> PublicInputValidation:
    """Validate curve, points, and subgroup without inventing a scalar check.

    This is the validator path for a bounded/non-success method result.  It
    deliberately performs no candidate multiplication, so its independent
    ``candidate_relation_check`` counter is exactly zero.
    """

    issues: list[Issue] = []
    fields = _public_fields(public_input)
    if fields is None:
        issues.append(
            _problem(
                "input.shape",
                "$",
                "public input must expose exactly the structural p/a/b/G/Q/ell boundary",
            )
        )
        return PublicInputValidation(tuple(issues))
    raw_p, raw_a, raw_b, raw_g, raw_q, raw_ell = fields
    p = _integer(raw_p, path="$.p", minimum=5, maximum=MAX_TOY_FIELD, issues=issues)
    if p is None:
        return PublicInputValidation(tuple(sorted(set(issues))))
    a = _integer(raw_a, path="$.a", minimum=0, maximum=p - 1, issues=issues)
    b = _integer(raw_b, path="$.b", minimum=0, maximum=p - 1, issues=issues)
    ell = _integer(
        raw_ell,
        path="$.ell",
        minimum=2,
        maximum=MAX_TOY_FIELD,
        issues=issues,
    )
    g = _point(raw_g, path="$.G", p=p, allow_infinity=False, issues=issues)
    q = _point(raw_q, path="$.Q", p=p, allow_infinity=True, issues=issues)
    if a is None or b is None or ell is None or g is _INVALID or q is _INVALID:
        return PublicInputValidation(tuple(sorted(set(issues))))
    if not is_prime(ell):
        issues.append(_problem("order.prime", "$.ell", "subgroup order must be prime"))
    try:
        curve = _CountingOracleCurve(p=p, a=a, b=b)
    except (TypeError, ValueError) as error:
        issues.append(_problem("curve", "$", str(error)))
        return PublicInputValidation(tuple(sorted(set(issues))))
    if not curve.is_on_curve(g):
        issues.append(_problem("point.off_curve", "$.G", "generator is not on the curve"))
    if not curve.is_on_curve(q):
        issues.append(_problem("point.off_curve", "$.Q", "target is not on the curve"))
    if issues:
        return PublicInputValidation(tuple(sorted(set(issues))), curve.validator_counters())
    try:
        if curve.scalar_mul_counted("generator_subgroup_check", ell, g) is not None:
            issues.append(
                _problem(
                    "order.generator",
                    "$.ell",
                    "declared subgroup order does not annihilate the generator",
                )
            )
        if curve.scalar_mul_counted("target_subgroup_check", ell, q) is not None:
            issues.append(
                _problem(
                    "order.target",
                    "$.Q",
                    "target is not in the declared subgroup",
                )
            )
    except (TypeError, ValueError, ArithmeticError) as error:
        issues.append(_problem("oracle", "$", f"subgroup check failed: {error}"))
    return PublicInputValidation(
        tuple(sorted(set(issues))), curve.validator_counters()
    )


__all__ = [
    "CandidateValidation",
    "PublicInputValidation",
    "PublicCandidateInput",
    "ValidatorCounters",
    "validate_candidate",
    "validate_public_input",
]
