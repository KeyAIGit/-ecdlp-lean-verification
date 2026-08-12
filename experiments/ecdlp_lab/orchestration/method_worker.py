"""Fixed method subprocess: one canonical request on stdin, one outcome on stdout."""

from __future__ import annotations

import sys
from typing import Any, Mapping

from experiments.ecdlp_lab.core.canonical import canonical_json_bytes, strict_loads
from experiments.ecdlp_lab.methods.python.dispatch import run_method
from experiments.ecdlp_lab.methods.python.model import (
    MethodCounters,
    MethodBudgets,
    MethodFailure,
    PhaseCounters,
    PublicMethodInput,
    SolverDiagnostics,
    SolverOutcome,
)

MAX_STDIN_BYTES = 256 * 1024
OUTPUT_KIND = "ecdlp_lab_method_worker_output_v1"
WORKER_INPUT_KEYS = frozenset(
    {"method_id", "algorithm_seed", "p", "a", "b", "G", "Q", "ell", "budgets"}
)
_OUTPUT_KEYS = frozenset(
    {
        "schema_version",
        "worker_output_kind",
        "status",
        "candidate_scalar",
        "failure",
        "counters",
        "diagnostics",
    }
)


def solver_outcome_to_dict(outcome: SolverOutcome) -> dict[str, Any]:
    if not isinstance(outcome, SolverOutcome):
        raise TypeError("outcome must be SolverOutcome")
    return {
        "schema_version": 1,
        "worker_output_kind": OUTPUT_KIND,
        "status": outcome.status,
        "candidate_scalar": outcome.candidate_scalar,
        "failure": outcome.failure.as_dict() if outcome.failure is not None else None,
        "counters": outcome.counters.as_dict(),
        "diagnostics": {
            name: getattr(outcome.diagnostics, name)
            for name in outcome.diagnostics.__dataclass_fields__
        },
    }


def _phase_from_mapping(value: Any) -> PhaseCounters:
    names = tuple(PhaseCounters.__dataclass_fields__)
    if not isinstance(value, Mapping) or set(value) != set(names):
        raise ValueError("phase counters contain unexpected fields")
    return PhaseCounters(**{name: value[name] for name in names})


def solver_outcome_from_dict(value: Any) -> SolverOutcome:
    if not isinstance(value, Mapping) or set(value) != _OUTPUT_KEYS:
        raise ValueError("method worker output contains unexpected fields")
    if value.get("schema_version") != 1 or value.get("worker_output_kind") != OUTPUT_KIND:
        raise ValueError("method worker output protocol mismatch")
    raw_counters = value.get("counters")
    counter_names = tuple(MethodCounters.__dataclass_fields__)
    if not isinstance(raw_counters, Mapping) or set(raw_counters) != set(counter_names):
        raise ValueError("method counters contain unexpected fields")
    counters = MethodCounters(
        counter_semantics_id=raw_counters["counter_semantics_id"],
        field_counter_semantics=raw_counters["field_counter_semantics"],
        offline_setup=_phase_from_mapping(raw_counters["offline_setup"]),
        online_target=_phase_from_mapping(raw_counters["online_target"]),
        method_self_check=_phase_from_mapping(raw_counters["method_self_check"]),
        table_entries=raw_counters["table_entries"],
        estimated_algorithmic_table_bytes=raw_counters[
            "estimated_algorithmic_table_bytes"
        ],
        restarts=raw_counters["restarts"],
        collisions=raw_counters["collisions"],
        noninvertible_collisions=raw_counters["noninvertible_collisions"],
        distinguished_points=raw_counters["distinguished_points"],
        legacy_p1_group_operations=raw_counters["legacy_p1_group_operations"],
    )
    raw_failure = value.get("failure")
    failure: MethodFailure | None
    if raw_failure is None:
        failure = None
    elif isinstance(raw_failure, Mapping) and set(raw_failure) == {"code", "detail"}:
        failure = MethodFailure(code=raw_failure["code"], detail=raw_failure["detail"])
    else:
        raise ValueError("method failure contains unexpected fields")
    raw_diagnostics = value.get("diagnostics")
    diagnostic_names = tuple(SolverDiagnostics.__dataclass_fields__)
    if not isinstance(raw_diagnostics, Mapping) or set(raw_diagnostics) != set(
        diagnostic_names
    ):
        raise ValueError("method diagnostics contain unexpected fields")
    diagnostics = SolverDiagnostics(
        **{name: raw_diagnostics[name] for name in diagnostic_names}
    )
    return SolverOutcome(
        status=value["status"],
        candidate_scalar=value["candidate_scalar"],
        failure=failure,
        counters=counters,
        diagnostics=diagnostics,
    )


def make_method_worker_request(method_request: Mapping[str, Any]) -> dict[str, Any]:
    """Project a retained P01 request onto the exact nine-field child boundary."""

    if not isinstance(method_request, Mapping):
        raise ValueError("method request must be an object")
    curve = method_request.get("curve")
    if not isinstance(curve, Mapping):
        raise ValueError("method request curve must be an object")
    return {
        "method_id": method_request.get("method_id"),
        "algorithm_seed": method_request.get("algorithm_seed"),
        "p": curve.get("field_p"),
        "a": curve.get("curve_a"),
        "b": curve.get("curve_b"),
        "G": method_request.get("generator"),
        "Q": method_request.get("target"),
        "ell": method_request.get("subgroup_order"),
        "budgets": method_request.get("budgets"),
    }


def execute_request(request: Any) -> SolverOutcome:
    if not isinstance(request, Mapping) or set(request) != WORKER_INPUT_KEYS:
        return SolverOutcome.failed("invalid_public_input")
    try:
        public_input = PublicMethodInput(
            method_id=request["method_id"],
            algorithm_seed=request["algorithm_seed"],
            p=request["p"],
            a=request["a"],
            b=request["b"],
            G=request["G"],
            Q=request["Q"],
            ell=request["ell"],
            budgets=MethodBudgets.from_mapping(request["budgets"]),
        )
    except (KeyError, TypeError, ValueError):
        return SolverOutcome.failed("invalid_public_input")
    return run_method(public_input)


def _read_canonical_stdin() -> Any:
    raw = sys.stdin.buffer.read(MAX_STDIN_BYTES + 1)
    if not raw or len(raw) > MAX_STDIN_BYTES:
        raise ValueError("method worker stdin is empty or oversized")
    value = strict_loads(raw, label="method worker stdin")
    if canonical_json_bytes(value) != raw:
        raise ValueError("method worker stdin must be exact canonical JSON")
    return value


def main() -> int:
    try:
        outcome = execute_request(_read_canonical_stdin())
    except Exception:
        outcome = SolverOutcome.failed("invalid_public_input")
    sys.stdout.buffer.write(canonical_json_bytes(solver_outcome_to_dict(outcome)))
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised through subprocess tests
    raise SystemExit(main())


__all__ = [
    "MAX_STDIN_BYTES",
    "OUTPUT_KIND",
    "WORKER_INPUT_KEYS",
    "execute_request",
    "main",
    "make_method_worker_request",
    "solver_outcome_from_dict",
    "solver_outcome_to_dict",
]
