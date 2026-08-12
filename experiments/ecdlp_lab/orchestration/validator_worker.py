"""Independent candidate-validation subprocess with a minimal public boundary."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Any, Mapping

from experiments.ecdlp_lab.core.candidate_validation import validate_candidate
from experiments.ecdlp_lab.core.canonical import canonical_json_bytes, strict_loads

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


@dataclass(frozen=True)
class _PublicInput:
    p: Any
    a: Any
    b: Any
    G: Any
    Q: Any
    ell: Any


def make_validator_request(method_request: Mapping[str, Any], candidate: Any) -> dict[str, Any]:
    curve = method_request.get("curve")
    if not isinstance(curve, Mapping):
        raise ValueError("method request curve must be an object")
    return {
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


def execute_request(request: Any) -> dict[str, Any]:
    if not isinstance(request, Mapping) or set(request) != _REQUEST_KEYS:
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
    return validate_candidate(public, request.get("candidate_scalar")).to_dict()


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
