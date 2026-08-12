"""Independent candidate-validation subprocess with a minimal public boundary."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Any, Mapping

from experiments.ecdlp_lab.core.candidate_validation import (
    validate_candidate,
    validate_public_input,
)
from experiments.ecdlp_lab.core.canonical import (
    canonical_json_bytes,
    is_sha256,
    sha256_json,
    strict_loads,
)

MAX_STDIN_BYTES = 64 * 1024
REQUEST_KIND = "ecdlp_lab_validator_worker_request_v1"
_REQUEST_KEYS = frozenset(
    {
        "schema_version",
        "worker_request_kind",
        "p",
        "a",
        "b",
        "G",
        "Q",
        "ell",
        "candidate_scalar",
    }
)
_NON_SUCCESS_REQUEST_KEYS = frozenset(
    {
        *_REQUEST_KEYS,
        "subject_status",
        "method_failure",
        "method_failure_sha256",
        "method_counters",
        "method_counters_sha256",
        "method_budgets",
        "method_budgets_sha256",
        "subject_sha256",
    }
)
_NON_SUCCESS_STATUSES = frozenset(
    {"bounded_failure", "invalid_request", "internal_error"}
)
_FAILURE_STATUS = {
    "invalid_public_input": "invalid_request",
    "backend_error": "internal_error",
    "group_operation_budget_exhausted": "bounded_failure",
    "table_budget_exhausted": "bounded_failure",
    "step_budget_exhausted": "bounded_failure",
    "restart_budget_exhausted": "bounded_failure",
    "memory_budget_exhausted": "bounded_failure",
    "process_timeout": "bounded_failure",
    "process_terminated": "bounded_failure",
    "no_solution": "bounded_failure",
}
_FAILURE_DETAILS = {
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
_COUNTER_KEYS = frozenset(
    {
        "counter_semantics_id",
        "field_counter_semantics",
        "offline_setup",
        "online_target",
        "method_self_check",
        "table_entries",
        "estimated_algorithmic_table_bytes",
        "restarts",
        "collisions",
        "noninvertible_collisions",
        "distinguished_points",
        "legacy_p1_group_operations",
    }
)
_PHASE_KEYS = frozenset(
    {
        "group_law_invocations",
        "nontrivial_additions",
        "doublings",
        "negations",
        "field_inversions",
        "field_multiplications",
        "field_squarings",
    }
)
_BUDGET_KEYS = frozenset(
    {
        "max_subgroup_order_bits",
        "max_field_bits",
        "max_group_law_invocations",
        "max_table_entries",
        "max_steps",
        "timeout_ns",
        "max_memory_bytes",
        "workers",
    }
)


@dataclass(frozen=True)
class _PublicInput:
    p: Any
    a: Any
    b: Any
    G: Any
    Q: Any
    ell: Any


def make_validator_request(
    method_request: Mapping[str, Any], candidate_or_result: Any
) -> dict[str, Any]:
    curve = method_request.get("curve")
    if not isinstance(curve, Mapping):
        raise ValueError("method request curve must be an object")
    if isinstance(candidate_or_result, Mapping):
        status = candidate_or_result.get("status")
        candidate = candidate_or_result.get("candidate_scalar")
    else:
        status = "success"
        candidate = candidate_or_result
    request = {
        "schema_version": 1,
        "worker_request_kind": REQUEST_KIND,
        "p": curve.get("field_p"),
        "a": curve.get("curve_a"),
        "b": curve.get("curve_b"),
        "G": method_request.get("generator"),
        "Q": method_request.get("target"),
        "ell": method_request.get("subgroup_order"),
        "candidate_scalar": candidate,
    }
    if status in _NON_SUCCESS_STATUSES and isinstance(candidate_or_result, Mapping):
        counters = candidate_or_result.get("counters")
        if not isinstance(counters, Mapping):
            raise ValueError("non-success method result counters must be an object")
        counters = dict(counters)
        request.update(
            {
                "subject_status": status,
                "method_failure": candidate_or_result.get("failure"),
                "method_failure_sha256": sha256_json(
                    candidate_or_result.get("failure")
                ),
                "method_counters": counters,
                "method_counters_sha256": sha256_json(counters),
                "method_budgets": dict(method_request.get("budgets", {})),
                "method_budgets_sha256": sha256_json(
                    dict(method_request.get("budgets", {}))
                ),
                "subject_sha256": sha256_json(dict(candidate_or_result)),
            }
        )
    elif status != "success":
        raise ValueError("validator request has an unknown method-result status")
    return request


def _nonnegative_exact(value: Any) -> bool:
    return type(value) is int and value >= 0


def _method_counters_valid(counters: Any, budgets: Any) -> bool:
    if (
        not isinstance(counters, Mapping)
        or frozenset(counters) != _COUNTER_KEYS
        or not isinstance(budgets, Mapping)
        or frozenset(budgets) != _BUDGET_KEYS
    ):
        return False
    if counters.get("counter_semantics_id") != "affine_group_calls_v1":
        return False
    field_semantics = counters.get("field_counter_semantics")
    if field_semantics != "not_instrumented":
        return False
    phases = []
    for name in ("offline_setup", "online_target", "method_self_check"):
        phase = counters.get(name)
        if not isinstance(phase, Mapping) or frozenset(phase) != _PHASE_KEYS:
            return False
        if any(
            not _nonnegative_exact(phase.get(field))
            for field in (
                "group_law_invocations",
                "nontrivial_additions",
                "doublings",
                "negations",
            )
        ):
            return False
        if (
            phase["nontrivial_additions"] + phase["doublings"]
            > phase["group_law_invocations"]
        ):
            return False
        field_values = tuple(
            phase.get(field)
            for field in (
                "field_inversions",
                "field_multiplications",
                "field_squarings",
            )
        )
        if any(value is not None for value in field_values):
            return False
        phases.append(phase)
    for name in (
        "table_entries",
        "estimated_algorithmic_table_bytes",
        "restarts",
        "collisions",
        "noninvertible_collisions",
        "distinguished_points",
    ):
        if not _nonnegative_exact(counters.get(name)):
            return False
    legacy = counters.get("legacy_p1_group_operations")
    if legacy is not None and not _nonnegative_exact(legacy):
        return False
    if any(not _nonnegative_exact(value) or value < 1 for value in budgets.values()):
        return False
    if (
        budgets["max_field_bits"] > 32
        or budgets["max_subgroup_order_bits"] > 32
        or budgets["workers"] != 1
        or counters["noninvertible_collisions"] > counters["collisions"]
    ):
        return False
    total_group_calls = sum(phase["group_law_invocations"] for phase in phases)
    return (
        total_group_calls <= budgets["max_group_law_invocations"]
        and counters["table_entries"] <= budgets["max_table_entries"]
        and counters["estimated_algorithmic_table_bytes"]
        <= budgets["max_memory_bytes"]
    )


def execute_request(request: Any) -> dict[str, Any]:
    if not isinstance(request, Mapping):
        return validate_candidate(object(), None).to_dict()
    keys = set(request)
    if keys not in {_REQUEST_KEYS, _NON_SUCCESS_REQUEST_KEYS}:
        return validate_candidate(object(), None).to_dict()
    if request.get("schema_version") != 1 or request.get("worker_request_kind") != REQUEST_KIND:
        return validate_candidate(object(), None).to_dict()
    public = _PublicInput(
        p=request.get("p"),
        a=request.get("a"),
        b=request.get("b"),
        G=tuple(request["G"]) if type(request.get("G")) is list else request.get("G"),
        Q=tuple(request["Q"]) if type(request.get("Q")) is list else request.get("Q"),
        ell=request.get("ell"),
    )
    if keys == _REQUEST_KEYS:
        return validate_candidate(public, request.get("candidate_scalar")).to_dict()

    status = request.get("subject_status")
    failure = request.get("method_failure")
    counters = request.get("method_counters")
    counters_sha256 = request.get("method_counters_sha256")
    budgets = request.get("method_budgets")
    budgets_sha256 = request.get("method_budgets_sha256")
    subject_sha256 = request.get("subject_sha256")
    failure_sha256 = request.get("method_failure_sha256")
    status_binding_valid = (
        isinstance(failure, Mapping)
        and frozenset(failure) == {"code", "detail"}
        and isinstance(failure.get("detail"), str)
        and failure.get("detail") == _FAILURE_DETAILS.get(failure.get("code"))
        and _FAILURE_STATUS.get(failure.get("code")) == status
        and is_sha256(failure_sha256)
        and sha256_json(dict(failure)) == failure_sha256
        and is_sha256(subject_sha256)
    )
    counters_binding_valid = False
    if (
        status in _NON_SUCCESS_STATUSES
        and request.get("candidate_scalar") is None
        and isinstance(counters, Mapping)
        and is_sha256(counters_sha256)
        and isinstance(budgets, Mapping)
        and is_sha256(budgets_sha256)
    ):
        try:
            counters_binding_valid = (
                sha256_json(dict(counters)) == counters_sha256
                and sha256_json(dict(budgets)) == budgets_sha256
                and _method_counters_valid(counters, budgets)
            )
        except (TypeError, ValueError):
            counters_binding_valid = False
    validation = validate_public_input(public)
    report = validation.to_dict()
    issues = list(report["issues"])
    if not counters_binding_valid:
        issues.append(
            {
                "code": "candidate.method_counters.binding",
                "path": "$.method_counters_sha256",
                "message": "method counters do not match their canonical digest",
            }
        )
    if not status_binding_valid:
        issues.append(
            {
                "code": "candidate.subject_status.binding",
                "path": "$.subject_status",
                "message": "method failure and status do not match the fixed mapping",
            }
        )
    passed = validation.passed and counters_binding_valid and status_binding_valid
    return {
        "schema_version": 1,
        "report_kind": "ecdlp_lab_non_success_validation_v1",
        "subject_status": status,
        "subject_sha256": subject_sha256,
        "candidate": None,
        "public_input_valid": validation.passed,
        "relation_verified": None,
        "method_failure_sha256": failure_sha256,
        "method_counters_sha256": counters_sha256,
        "method_budgets_sha256": budgets_sha256,
        "status_binding_valid": status_binding_valid,
        "counters_binding_valid": counters_binding_valid,
        "passed": passed,
        "validator_counters": report["validator_counters"],
        "issues": issues,
    }


def _read_canonical_stdin() -> Any:
    raw = sys.stdin.buffer.read(MAX_STDIN_BYTES + 1)
    if not raw or len(raw) > MAX_STDIN_BYTES:
        raise ValueError("validator worker stdin is empty or oversized")
    value = strict_loads(raw, label="validator worker stdin")
    if canonical_json_bytes(value) != raw:
        raise ValueError("validator worker stdin must be exact canonical JSON")
    return value


def main() -> int:
    try:
        report = execute_request(_read_canonical_stdin())
    except Exception:
        report = validate_candidate(object(), None).to_dict()
    sys.stdout.buffer.write(canonical_json_bytes(report))
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised through subprocess tests
    raise SystemExit(main())


__all__ = [
    "MAX_STDIN_BYTES",
    "REQUEST_KIND",
    "execute_request",
    "main",
    "make_validator_request",
]
