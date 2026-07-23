#!/usr/bin/env python3
"""Dependency-free semantic validator for ECDLP candidate run records."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

try:
    from .ec_oracle import Curve, parse_point, prime_divisors, validate_scalar
except ImportError:
    from ec_oracle import Curve, parse_point, prime_divisors, validate_scalar

HEX_64 = re.compile(r"^[0-9a-f]{64}$")
HEX_40 = re.compile(r"^[0-9a-f]{40}$")
REQUIRED_TOP_LEVEL = {
    "schema_version",
    "record_kind",
    "candidate",
    "target",
    "result",
    "cost",
    "environment",
    "provenance",
    "validation",
    "claims",
}
REQUIRED_COST_METRICS = {
    "wall_time_seconds",
    "group_operations",
    "field_operations",
    "peak_memory_bytes",
}
REQUIRED_FIELDS = {
    "candidate": {
        "id",
        "route_id",
        "hypothesis_id",
        "implementation",
        "code_commit",
        "entrypoint",
    },
    "target": {
        "curve_id",
        "threat_model",
        "field_p",
        "curve_a",
        "curve_b",
        "base_point",
        "target_point",
        "base_order",
        "target_count",
        "auxiliary_inputs",
        "scalar_interval",
    },
    "result": {"claimed_scalar"},
    "cost": {
        "online",
        "offline",
        "reusable_precomputation",
        "amortization_target_count",
        "parallel_workers",
        "success_probability",
    },
    "environment": {"python", "platform", "tool_versions"},
    "provenance": {
        "seed",
        "command",
        "dirty_worktree",
        "input_sha256",
        "output_sha256",
        "environment_sha256",
        "record_sha256",
    },
    "validation": {
        "validator_id",
        "independent_implementation",
        "shares_decisive_logic",
        "passed",
        "validator_output_sha256",
    },
    "claims": {
        "success_level",
        "asymptotic_claim",
        "secp256k1_break",
        "disclosure_gate_acknowledged",
    },
}


def canonical_hash(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def record_payload(record: dict) -> dict:
    """Return the immutable research payload covered by record_sha256."""
    payload = {
        key: record.get(key)
        for key in (
            "schema_version",
            "record_kind",
            "candidate",
            "target",
            "result",
            "cost",
            "environment",
            "validation",
            "claims",
        )
    }
    provenance = record.get("provenance")
    payload["provenance"] = (
        {
            key: value
            for key, value in provenance.items()
            if key != "record_sha256"
        }
        if isinstance(provenance, dict)
        else provenance
    )
    return payload


def load_record(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("candidate record must be a JSON object")
    return value


def _require_mapping(
    parent: dict, key: str, errors: list[str], context: str = "record"
) -> dict:
    value = parent.get(key)
    if not isinstance(value, dict):
        errors.append(f"{context}.{key} must be an object")
        return {}
    return value


def _check_exact_keys(
    value: dict, expected: set[str], context: str, errors: list[str]
) -> None:
    missing = expected - set(value)
    extra = set(value) - expected
    if missing:
        errors.append(f"{context} missing fields: {sorted(missing)}")
    if extra:
        errors.append(f"{context} has unknown fields: {sorted(extra)}")


def _check_nonempty_text(value: object, context: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value:
        errors.append(f"{context} must be a nonempty string")


def _check_nonnegative_metrics(
    value: dict, context: str, errors: list[str]
) -> None:
    _check_exact_keys(value, REQUIRED_COST_METRICS, context, errors)
    wall_time = value.get("wall_time_seconds")
    if (
        not isinstance(wall_time, (int, float))
        or isinstance(wall_time, bool)
        or wall_time < 0
    ):
        errors.append(f"{context}.wall_time_seconds must be a nonnegative number")
    for key in ("group_operations", "field_operations", "peak_memory_bytes"):
        metric = value.get(key)
        if not isinstance(metric, int) or isinstance(metric, bool) or metric < 0:
            errors.append(f"{context}.{key} must be a nonnegative integer")


def _route_index(decisions: dict) -> dict[str, dict]:
    return {route["id"]: route for route in decisions["routes"]}


def _validate_hash(
    actual: object, expected: str, name: str, errors: list[str]
) -> None:
    if not isinstance(actual, str) or not HEX_64.fullmatch(actual):
        errors.append(f"{name} must be a lowercase SHA-256 hex digest")
    elif actual != expected:
        errors.append(f"{name} does not match the canonical payload")


def validate_record(record: dict, decisions: dict) -> list[str]:
    errors: list[str] = []
    _check_exact_keys(record, REQUIRED_TOP_LEVEL, "record", errors)
    if record.get("schema_version") != 1:
        errors.append("schema_version must be 1")

    kind = record.get("record_kind")
    if kind not in {"framework_fixture", "candidate_run"}:
        errors.append("record_kind must be framework_fixture or candidate_run")

    candidate = _require_mapping(record, "candidate", errors)
    target = _require_mapping(record, "target", errors)
    result = _require_mapping(record, "result", errors)
    cost = _require_mapping(record, "cost", errors)
    environment = _require_mapping(record, "environment", errors)
    provenance = _require_mapping(record, "provenance", errors)
    validation = _require_mapping(record, "validation", errors)
    claims = _require_mapping(record, "claims", errors)
    for name, value in (
        ("candidate", candidate),
        ("target", target),
        ("result", result),
        ("cost", cost),
        ("environment", environment),
        ("provenance", provenance),
        ("validation", validation),
        ("claims", claims),
    ):
        _check_exact_keys(value, REQUIRED_FIELDS[name], name, errors)

    routes = _route_index(decisions)
    route_id = candidate.get("route_id")
    route = routes.get(route_id)
    if route is None:
        errors.append(f"candidate.route_id is unknown: {route_id!r}")
    elif kind == "candidate_run" and not route.get("authorized_experiment"):
        errors.append(f"route {route_id} does not authorize a candidate run")

    candidate_id = candidate.get("id")
    _check_nonempty_text(candidate_id, "candidate.id", errors)
    if kind == "framework_fixture" and not str(candidate_id).startswith("fixture-"):
        errors.append("framework fixture candidate ids must start with fixture-")
    _check_nonempty_text(route_id, "candidate.route_id", errors)
    hypothesis_id = candidate.get("hypothesis_id")
    if hypothesis_id is not None and (
        not isinstance(hypothesis_id, str) or not hypothesis_id
    ):
        errors.append("candidate.hypothesis_id must be null or a nonempty string")
    if route is not None and hypothesis_id is not None:
        if hypothesis_id not in route.get("hypothesis_ids", []):
            errors.append(
                f"candidate.hypothesis_id {hypothesis_id!r} is not bound to route {route_id}"
            )
    _check_nonempty_text(candidate.get("implementation"), "candidate.implementation", errors)
    commit = candidate.get("code_commit")
    if not isinstance(commit, str) or not HEX_40.fullmatch(commit):
        errors.append("candidate.code_commit must be a lowercase 40-hex commit")
    elif kind == "candidate_run" and commit == "0" * 40:
        errors.append("candidate runs must reference a real code commit")
    _check_nonempty_text(candidate.get("entrypoint"), "candidate.entrypoint", errors)

    threat_models = {model["id"] for model in decisions["threat_models"]}
    threat_model = target.get("threat_model")
    if threat_model not in threat_models:
        errors.append(f"target.threat_model is unknown: {threat_model!r}")
    elif route is not None and threat_model not in route.get("threat_models", []):
        errors.append(
            f"target.threat_model {threat_model!r} is not declared for route {route_id}"
        )
    curve_id = target.get("curve_id")
    _check_nonempty_text(curve_id, "target.curve_id", errors)
    if kind == "framework_fixture" and not str(curve_id).startswith("toy-"):
        errors.append("framework fixtures must use a toy-* curve")
    if kind == "framework_fixture" and claims.get("secp256k1_break") is not False:
        errors.append("framework fixtures must set claims.secp256k1_break=false")

    auxiliary_inputs = target.get("auxiliary_inputs")
    if not isinstance(auxiliary_inputs, list) or not all(
        isinstance(item, str) and item for item in auxiliary_inputs
    ):
        errors.append("target.auxiliary_inputs must be an array of nonempty strings")
        auxiliary_inputs = []
    target_count = target.get("target_count")
    if (
        not isinstance(target_count, int)
        or isinstance(target_count, bool)
        or target_count < 1
    ):
        errors.append("target.target_count must be a positive integer")
    scalar_interval = target.get("scalar_interval")
    if scalar_interval is not None:
        if (
            not isinstance(scalar_interval, list)
            or len(scalar_interval) != 2
            or any(
                not isinstance(endpoint, int) or isinstance(endpoint, bool)
                for endpoint in scalar_interval
            )
        ):
            errors.append("target.scalar_interval must be null or [lower, upper]")
        elif scalar_interval[0] > scalar_interval[1]:
            errors.append("target.scalar_interval lower bound exceeds upper bound")
    if threat_model == "classical-single-target-plain":
        if auxiliary_inputs:
            errors.append("plain threat model forbids auxiliary inputs")
        if target_count != 1:
            errors.append("plain threat model requires target_count=1")
        if target.get("scalar_interval") is not None:
            errors.append("plain threat model forbids a scalar interval promise")

    online = _require_mapping(cost, "online", errors, "cost")
    offline = _require_mapping(cost, "offline", errors, "cost")
    _check_nonnegative_metrics(online, "cost.online", errors)
    _check_nonnegative_metrics(offline, "cost.offline", errors)
    reusable = cost.get("reusable_precomputation")
    if not isinstance(reusable, bool):
        errors.append("cost.reusable_precomputation must be boolean")
    amortization = cost.get("amortization_target_count")
    if (
        not isinstance(amortization, int)
        or isinstance(amortization, bool)
        or amortization < 1
    ):
        errors.append("cost.amortization_target_count must be a positive integer")
    workers = cost.get("parallel_workers")
    if not isinstance(workers, int) or isinstance(workers, bool) or workers < 1:
        errors.append("cost.parallel_workers must be a positive integer")
    probability = cost.get("success_probability")
    if (
        not isinstance(probability, (int, float))
        or isinstance(probability, bool)
        or not 0 <= probability <= 1
    ):
        errors.append("cost.success_probability must be in [0,1]")
    if reusable and all(offline.get(key, 0) == 0 for key in REQUIRED_COST_METRICS):
        errors.append("reusable precomputation must report nonzero offline cost")
    if reusable is False and amortization != 1:
        errors.append("non-reusable work must use amortization_target_count=1")
    if threat_model == "classical-single-target-plain" and reusable:
        errors.append("plain threat model forbids reusable precomputation")

    _check_nonempty_text(environment.get("python"), "environment.python", errors)
    _check_nonempty_text(environment.get("platform"), "environment.platform", errors)
    tool_versions = environment.get("tool_versions")
    if not isinstance(tool_versions, dict) or not all(
        isinstance(key, str)
        and key
        and isinstance(value, str)
        and value
        for key, value in getattr(tool_versions, "items", lambda: [])()
    ):
        errors.append(
            "environment.tool_versions must map nonempty tool names to nonempty versions"
        )

    if validation.get("validator_id") != "framework.ec_oracle.v1":
        errors.append("validation.validator_id must be framework.ec_oracle.v1")
    if validation.get("independent_implementation") is not True:
        errors.append("validator must be marked as an independent implementation")
    if validation.get("shares_decisive_logic") is not False:
        errors.append("validator must not share decisive candidate logic")

    computed_pass = False
    try:
        field_p = target["field_p"]
        curve_a = target["curve_a"]
        curve_b = target["curve_b"]
        order = target["base_order"]
        scalar = result["claimed_scalar"]
        if any(
            not isinstance(value, int) or isinstance(value, bool)
            for value in (field_p, curve_a, curve_b, order, scalar)
        ):
            raise ValueError("curve parameters, order, and scalar must be integers")
        if not 0 <= curve_a < field_p or not 0 <= curve_b < field_p:
            raise ValueError("curve coefficients must be canonical field elements")
        curve = Curve(field_p, curve_a, curve_b)
        base = parse_point(target["base_point"], "target.base_point")
        target_point = parse_point(target["target_point"], "target.target_point")
        if base is None:
            raise ValueError("base point must not be infinity")
        if not curve.is_on_curve(base) or not curve.is_on_curve(target_point):
            raise ValueError("base and target points must lie on the curve")
        if order <= 1 or curve.scalar_mul(order, base) is not None:
            raise ValueError("target.base_order does not annihilate the base point")
        if any(
            curve.scalar_mul(order // prime, base) is None
            for prime in prime_divisors(order)
        ):
            raise ValueError("target.base_order is not the exact base-point order")
        if not 0 <= scalar < order:
            raise ValueError("result.claimed_scalar must be canonical modulo base_order")
        if (
            isinstance(scalar_interval, list)
            and len(scalar_interval) == 2
            and all(isinstance(endpoint, int) for endpoint in scalar_interval)
            and not scalar_interval[0] <= scalar <= scalar_interval[1]
        ):
            raise ValueError("claimed scalar lies outside target.scalar_interval")
        computed_pass = validate_scalar(curve, base, target_point, scalar)
    except (KeyError, TypeError, ValueError) as error:
        errors.append(f"oracle input invalid: {error}")

    if validation.get("passed") is not computed_pass:
        errors.append("validation.passed disagrees with the independent EC oracle")
    if not computed_pass:
        errors.append("claimed scalar does not reproduce the target point")

    success_levels = {level["id"] for level in decisions["success_levels"]}
    success_level = claims.get("success_level")
    if success_level not in success_levels:
        errors.append(f"claims.success_level is unknown: {success_level!r}")
    if success_level in {"subgeneric", "practical-secp256k1"} and not claims.get(
        "asymptotic_claim"
    ):
        errors.append(f"{success_level} requires claims.asymptotic_claim")
    if claims.get("secp256k1_break") and success_level != "practical-secp256k1":
        errors.append("a secp256k1 break claim requires practical-secp256k1 level")
    if claims.get("secp256k1_break") and not claims.get(
        "disclosure_gate_acknowledged"
    ):
        errors.append("a secp256k1 break claim requires disclosure-gate acknowledgement")
    if claims.get("asymptotic_claim") is not None and (
        not isinstance(claims.get("asymptotic_claim"), str)
        or not claims.get("asymptotic_claim")
    ):
        errors.append("claims.asymptotic_claim must be null or a nonempty string")
    for name in ("secp256k1_break", "disclosure_gate_acknowledged"):
        if not isinstance(claims.get(name), bool):
            errors.append(f"claims.{name} must be boolean")

    if candidate and target and result and environment and provenance:
        _validate_hash(
            provenance.get("input_sha256"),
            canonical_hash(target),
            "provenance.input_sha256",
            errors,
        )
        _validate_hash(
            provenance.get("output_sha256"),
            canonical_hash(result),
            "provenance.output_sha256",
            errors,
        )
        _validate_hash(
            provenance.get("environment_sha256"),
            canonical_hash(environment),
            "provenance.environment_sha256",
            errors,
        )
        _validate_hash(
            provenance.get("record_sha256"),
            canonical_hash(record_payload(record)),
            "provenance.record_sha256",
            errors,
        )
    validator_payload = {
        "validator_id": validation.get("validator_id"),
        "computed_pass": computed_pass,
        "curve_id": curve_id,
        "claimed_scalar": result.get("claimed_scalar"),
    }
    _validate_hash(
        validation.get("validator_output_sha256"),
        canonical_hash(validator_payload),
        "validation.validator_output_sha256",
        errors,
    )

    if (
        not isinstance(provenance.get("command"), list)
        or not provenance.get("command")
        or not all(
            isinstance(item, str) and item for item in provenance.get("command", [])
        )
    ):
        errors.append("provenance.command must be a nonempty string array")
    if not isinstance(provenance.get("seed"), int) or isinstance(
        provenance.get("seed"), bool
    ):
        errors.append("provenance.seed must be an integer")
    if provenance.get("dirty_worktree") is not False:
        errors.append("accepted runs must record dirty_worktree=false")

    return errors


def load_decisions(root: Path) -> dict:
    return json.loads(
        (root / "repo" / "ECDLP_DECISION_SUBSTRATE.json").read_text(
            encoding="utf-8"
        )
    )
