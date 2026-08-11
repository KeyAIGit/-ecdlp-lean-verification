"""Dependency-free semantic validation for ECDLP lab engineering fixtures.

This module is deliberately separate from the Research Engine. It accepts only
bounded synthetic lab records and never converts them to candidate or Engine
records.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any, Mapping

from .canonical_json import is_sha256, load_strict, sha256_hex
from .path_policy import PathPolicyError, validate_relative_posix_path


class ContractValidationError(ValueError):
    """Raised when a lab contract violates syntax, semantics, or safety policy."""


RECORD_KIND = "lab_engineering_fixture"
SCHEMA_VERSION = "1.0"
CONTRACT_KINDS = {
    "campaign_config",
    "target_vector",
    "work_unit",
    "method_request",
    "method_result",
    "telemetry",
    "validation_receipt",
    "analysis_summary",
    "artifact_ref",
}
COMMON_KEYS = {
    "schema_version",
    "record_kind",
    "contract_kind",
    "hypothesis_id",
    "candidate_id",
    "authorization_id",
    "native_research_outcome",
    "route_effect",
    "retention_class",
    "retainable",
    "payload",
    "record_sha256",
}
HEX40 = re.compile(r"^[0-9a-f]{40}$")
DECIMAL_STRING = re.compile(r"^(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$")
METHOD_ID = re.compile(r"^[a-z][a-z0-9_]{2,63}$")
IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")

SECP256K1_P = 2**256 - 2**32 - 977
SECP256K1_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
MAX_SUBGROUP_ORDER = 2**32 - 1

FORBIDDEN_FIELD_NAMES = {
    "expected_scalar",
    "target_scalar",
    "secret_scalar",
    "private_scalar",
    "private_key",
    "wallet",
    "wallet_material",
    "target_generation_seed",
    "target_seed",
    "answer",
    "dlp_oracle",
    "submit",
    "promote",
    "register_hypothesis",
    "compile_candidate",
    "hidden_precomputation",
}

PAYLOAD_KEYS: dict[str, set[str]] = {
    "campaign_config": {
        "campaign_id",
        "catalog_sha256",
        "target_vector_sha256s",
        "method_ids",
        "algorithm_seeds",
        "budgets",
        "output_subdir",
        "reusable_setup",
        "amortization_target_count",
    },
    "target_vector": {
        "target_vector_id",
        "catalog_sha256",
        "curve_id",
        "field_p",
        "curve_a",
        "curve_b",
        "base_point",
        "target_point",
        "subgroup_order",
        "field_bits",
        "subgroup_order_bits",
        "public_interval",
        "private_receipt_sha256",
    },
    "work_unit": {
        "work_unit_id",
        "attempt_id",
        "retry_index",
        "campaign_id",
        "target_vector_sha256",
        "method_id",
        "algorithm_seed",
        "source",
    },
    "method_request": {
        "request_id",
        "work_unit_id",
        "target_vector_sha256",
        "method_id",
        "algorithm_seed",
        "curve",
        "base_point",
        "target_point",
        "subgroup_order",
        "public_interval",
        "budgets",
    },
    "method_result": {
        "result_id",
        "work_unit_id",
        "method_id",
        "status",
        "claimed_scalar",
        "counters",
        "artifact_sha256s",
        "message",
    },
    "telemetry": {
        "telemetry_id",
        "attempt_id",
        "wall_time_ns",
        "cpu_time_ns",
        "max_rss_bytes",
        "exit_code",
        "parallel_workers",
        "platform",
        "python_version",
        "tool_versions",
    },
    "validation_receipt": {
        "validation_receipt_id",
        "work_unit_id",
        "method_result_sha256",
        "method_id",
        "producer_source_sha256",
        "validator_id",
        "validator_source_sha256",
        "independent_implementation",
        "shares_decisive_logic",
        "passed",
        "recomputed_scalar",
        "private_receipt_sha256",
        "validator_output_sha256",
    },
    "analysis_summary": {
        "analysis_summary_id",
        "campaign_id",
        "validation_receipt_sha256s",
        "normalized_metrics",
        "warnings",
        "claims",
    },
    "artifact_ref": {
        "artifact_ref_id",
        "sha256",
        "size_bytes",
        "media_type",
        "role",
        "location",
    },
}

IDENTITY_FIELD = {
    "campaign_config": "campaign_id",
    "target_vector": "target_vector_id",
    "work_unit": "work_unit_id",
    "method_request": "request_id",
    "method_result": "result_id",
    "telemetry": "telemetry_id",
    "validation_receipt": "validation_receipt_id",
    "analysis_summary": "analysis_summary_id",
    "artifact_ref": "artifact_ref_id",
}


def _error(path: str, message: str) -> ContractValidationError:
    return ContractValidationError(f"{path}: {message}")


def _require(condition: bool, path: str, message: str) -> None:
    if not condition:
        raise _error(path, message)


def _exact_keys(value: Mapping[str, Any], allowed: set[str], path: str) -> None:
    actual = set(value)
    unknown = actual - allowed
    missing = allowed - actual
    if unknown:
        raise _error(path, f"unknown fields: {sorted(unknown)}")
    if missing:
        raise _error(path, f"missing fields: {sorted(missing)}")


def _walk_forbidden(value: Any, path: str = "$.payload") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key.lower() in FORBIDDEN_FIELD_NAMES:
                raise _error(f"{path}.{key}", "forbidden secret, oracle, or promotion field")
            _walk_forbidden(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _walk_forbidden(item, f"{path}[{index}]")


def _require_sha(value: Any, path: str) -> str:
    _require(is_sha256(value), path, "expected lowercase SHA-256 hex")
    return value


def _require_id(value: Any, path: str) -> str:
    _require(isinstance(value, str) and IDENTIFIER.fullmatch(value) is not None, path, "invalid identifier")
    return value


def _require_method(value: Any, path: str) -> str:
    _require(isinstance(value, str) and METHOD_ID.fullmatch(value) is not None, path, "invalid method identifier")
    return value


def _require_nonnegative_int(value: Any, path: str) -> int:
    _require(isinstance(value, int) and not isinstance(value, bool) and value >= 0, path, "expected nonnegative integer")
    return value


def _require_positive_int(value: Any, path: str) -> int:
    _require(isinstance(value, int) and not isinstance(value, bool) and value > 0, path, "expected positive integer")
    return value


def _validate_point(value: Any, field_p: int, path: str) -> None:
    _require(isinstance(value, dict), path, "point must be an object")
    _exact_keys(value, {"x", "y"}, path)
    x = _require_nonnegative_int(value["x"], f"{path}.x")
    y = _require_nonnegative_int(value["y"], f"{path}.y")
    _require(x < field_p and y < field_p, path, "point coordinates must lie in the declared field")


def _validate_interval(value: Any, order: int, path: str) -> None:
    if value is None:
        return
    _require(isinstance(value, list) and len(value) == 2, path, "interval must be null or [lower, upper]")
    lower = _require_nonnegative_int(value[0], f"{path}[0]")
    upper = _require_nonnegative_int(value[1], f"{path}[1]")
    _require(lower <= upper < order, path, "interval must satisfy 0 <= lower <= upper < subgroup order")


def _validate_budgets(value: Any, path: str) -> None:
    _require(isinstance(value, dict), path, "budgets must be an object")
    _exact_keys(value, {"timeout_ns", "max_rss_bytes", "max_group_operations", "parallel_workers"}, path)
    _require_positive_int(value["timeout_ns"], f"{path}.timeout_ns")
    _require_positive_int(value["max_rss_bytes"], f"{path}.max_rss_bytes")
    _require_positive_int(value["max_group_operations"], f"{path}.max_group_operations")
    workers = _require_positive_int(value["parallel_workers"], f"{path}.parallel_workers")
    _require(workers <= 64, f"{path}.parallel_workers", "lab fixture worker cap is 64")


def _registry_sets(registry: Mapping[str, Any]) -> tuple[set[str], set[str], set[str]]:
    catalogs = set(registry.get("catalogs", {}))
    vectors = set(registry.get("target_vectors", {}))
    methods = set(registry.get("allowed_method_ids", []))
    return catalogs, vectors, methods


def load_registry(path: Path) -> dict[str, Any]:
    registry = load_strict(path)
    _require(isinstance(registry, dict), "$registry", "registry must be an object")
    _exact_keys(registry, {"schema_version", "catalogs", "target_vectors", "allowed_method_ids"}, "$registry")
    _require(registry["schema_version"] == SCHEMA_VERSION, "$registry.schema_version", "unsupported registry version")
    _require(isinstance(registry["catalogs"], dict), "$registry.catalogs", "expected object")
    _require(isinstance(registry["target_vectors"], dict), "$registry.target_vectors", "expected object")
    _require(isinstance(registry["allowed_method_ids"], list), "$registry.allowed_method_ids", "expected array")
    for digest in registry["catalogs"]:
        _require_sha(digest, "$registry.catalogs key")
    for digest in registry["target_vectors"]:
        _require_sha(digest, "$registry.target_vectors key")
    for method in registry["allowed_method_ids"]:
        _require_method(method, "$registry.allowed_method_ids")
    return registry


def _identity_material(record: Mapping[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(dict(record))
    result.pop("record_sha256", None)
    payload = result["payload"]
    kind = result["contract_kind"]
    payload.pop(IDENTITY_FIELD[kind], None)
    if kind == "work_unit":
        payload.pop("attempt_id", None)
        payload.pop("retry_index", None)
    return result


def compute_identity(record: Mapping[str, Any]) -> str:
    return sha256_hex(_identity_material(record))


def compute_attempt_id(work_unit_id: str, retry_index: int) -> str:
    return sha256_hex({"work_unit_id": work_unit_id, "retry_index": retry_index})


def compute_record_sha256(record: Mapping[str, Any]) -> str:
    material = copy.deepcopy(dict(record))
    material.pop("record_sha256", None)
    return sha256_hex(material)


def build_record(
    contract_kind: str,
    payload: Mapping[str, Any],
    *,
    retainable: bool = True,
    hypothesis_id: None = None,
    candidate_id: None = None,
    authorization_id: None = None,
) -> dict[str, Any]:
    if contract_kind not in CONTRACT_KINDS:
        raise ContractValidationError(f"unknown contract kind: {contract_kind}")
    record: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "record_kind": RECORD_KIND,
        "contract_kind": contract_kind,
        "hypothesis_id": hypothesis_id,
        "candidate_id": candidate_id,
        "authorization_id": authorization_id,
        "native_research_outcome": False,
        "route_effect": "none",
        "retention_class": "engineering_only",
        "retainable": retainable,
        "payload": copy.deepcopy(dict(payload)),
        "record_sha256": "0" * 64,
    }
    identity_field = IDENTITY_FIELD[contract_kind]
    record["payload"][identity_field] = compute_identity(record)
    if contract_kind == "work_unit":
        retry = record["payload"].get("retry_index")
        if not isinstance(retry, int) or isinstance(retry, bool) or retry < 0:
            raise ContractValidationError("work_unit retry_index must be a nonnegative integer")
        record["payload"]["attempt_id"] = compute_attempt_id(
            record["payload"][identity_field], retry
        )
    record["record_sha256"] = compute_record_sha256(record)
    return record


def _validate_common(record: Any) -> tuple[str, dict[str, Any]]:
    _require(isinstance(record, dict), "$", "record must be an object")
    _exact_keys(record, COMMON_KEYS, "$")
    _require(record["schema_version"] == SCHEMA_VERSION, "$.schema_version", "unsupported version")
    _require(record["record_kind"] == RECORD_KIND, "$.record_kind", "Engine/candidate records are forbidden")
    kind = record["contract_kind"]
    _require(kind in CONTRACT_KINDS, "$.contract_kind", "unknown lab contract family")
    for field in ("hypothesis_id", "candidate_id", "authorization_id"):
        _require(record[field] is None, f"$.{field}", "lab fixtures cannot carry scientific IDs")
    _require(record["native_research_outcome"] is False, "$.native_research_outcome", "must be false")
    _require(record["route_effect"] == "none", "$.route_effect", "must be none")
    _require(record["retention_class"] == "engineering_only", "$.retention_class", "must be engineering_only")
    _require(isinstance(record["retainable"], bool), "$.retainable", "must be boolean")
    _require(isinstance(record["payload"], dict), "$.payload", "must be object")
    _exact_keys(record["payload"], PAYLOAD_KEYS[kind], "$.payload")
    _walk_forbidden(record["payload"])
    _require_sha(record["record_sha256"], "$.record_sha256")
    return kind, record["payload"]


def _validate_campaign(payload: dict[str, Any], registry: Mapping[str, Any]) -> None:
    catalogs, vectors, methods = _registry_sets(registry)
    catalog = _require_sha(payload["catalog_sha256"], "$.payload.catalog_sha256")
    _require(catalog in catalogs, "$.payload.catalog_sha256", "unknown catalog digest")
    _require(isinstance(payload["target_vector_sha256s"], list) and payload["target_vector_sha256s"], "$.payload.target_vector_sha256s", "expected nonempty array")
    for index, digest in enumerate(payload["target_vector_sha256s"]):
        digest = _require_sha(digest, f"$.payload.target_vector_sha256s[{index}]")
        _require(digest in vectors, f"$.payload.target_vector_sha256s[{index}]", "unknown target-vector digest")
        target_meta = registry["target_vectors"][digest]
        _require(target_meta["catalog_sha256"] == catalog, f"$.payload.target_vector_sha256s[{index}]", "target vector belongs to another catalog")
    _require(isinstance(payload["method_ids"], list) and payload["method_ids"], "$.payload.method_ids", "expected nonempty array")
    for index, method in enumerate(payload["method_ids"]):
        method = _require_method(method, f"$.payload.method_ids[{index}]")
        _require(method in methods, f"$.payload.method_ids[{index}]", "method is not allowlisted")
    _require(len(set(payload["method_ids"])) == len(payload["method_ids"]), "$.payload.method_ids", "duplicate method IDs")
    _require(isinstance(payload["algorithm_seeds"], list) and payload["algorithm_seeds"], "$.payload.algorithm_seeds", "expected nonempty array")
    for index, seed in enumerate(payload["algorithm_seeds"]):
        _require_nonnegative_int(seed, f"$.payload.algorithm_seeds[{index}]")
    _validate_budgets(payload["budgets"], "$.payload.budgets")
    try:
        validate_relative_posix_path(payload["output_subdir"])
    except PathPolicyError as exc:
        raise _error("$.payload.output_subdir", str(exc)) from exc
    _require(isinstance(payload["reusable_setup"], bool), "$.payload.reusable_setup", "must be boolean")
    amortization = _require_positive_int(payload["amortization_target_count"], "$.payload.amortization_target_count")
    if not payload["reusable_setup"]:
        _require(amortization == 1, "$.payload.amortization_target_count", "nonreusable setup must amortize over one target")


def _validate_target_vector(payload: dict[str, Any], registry: Mapping[str, Any]) -> None:
    catalogs, _, _ = _registry_sets(registry)
    catalog = _require_sha(payload["catalog_sha256"], "$.payload.catalog_sha256")
    _require(catalog in catalogs, "$.payload.catalog_sha256", "unknown catalog digest")
    _require_id(payload["curve_id"], "$.payload.curve_id")
    p = _require_positive_int(payload["field_p"], "$.payload.field_p")
    _require(p != SECP256K1_P, "$.payload.field_p", "exact secp256k1 parameters are forbidden")
    _require(p.bit_length() <= 32, "$.payload.field_p", "field exceeds 32-bit engineering ceiling")
    for field in ("curve_a", "curve_b"):
        value = _require_nonnegative_int(payload[field], f"$.payload.{field}")
        _require(value < p, f"$.payload.{field}", "coefficient outside field")
    order = _require_positive_int(payload["subgroup_order"], "$.payload.subgroup_order")
    _require(order != SECP256K1_N, "$.payload.subgroup_order", "exact secp256k1 order is forbidden")
    _require(order <= MAX_SUBGROUP_ORDER, "$.payload.subgroup_order", "subgroup exceeds 32-bit ceiling")
    _require(payload["field_bits"] == p.bit_length(), "$.payload.field_bits", "does not match field prime")
    _require(payload["subgroup_order_bits"] == order.bit_length(), "$.payload.subgroup_order_bits", "does not match subgroup order")
    _validate_point(payload["base_point"], p, "$.payload.base_point")
    _validate_point(payload["target_point"], p, "$.payload.target_point")
    _validate_interval(payload["public_interval"], order, "$.payload.public_interval")
    _require_sha(payload["private_receipt_sha256"], "$.payload.private_receipt_sha256")


def _validate_source(source: Any, retainable: bool) -> None:
    _require(isinstance(source, dict), "$.payload.source", "source must be object")
    _exact_keys(source, {"commit", "clean_tree", "source_snapshot_sha256", "diff_sha256", "producer_dependency_sha256s", "validator_dependency_sha256s"}, "$.payload.source")
    _require(isinstance(source["commit"], str) and HEX40.fullmatch(source["commit"]) is not None, "$.payload.source.commit", "expected 40 lowercase hex characters")
    _require(isinstance(source["clean_tree"], bool), "$.payload.source.clean_tree", "must be boolean")
    _require_sha(source["source_snapshot_sha256"], "$.payload.source.source_snapshot_sha256")
    if source["clean_tree"]:
        _require(source["diff_sha256"] is None, "$.payload.source.diff_sha256", "clean source must not carry a diff digest")
    else:
        _require_sha(source["diff_sha256"], "$.payload.source.diff_sha256")
        _require(not retainable, "$.retainable", "dirty development records cannot be retainable")
    for key in ("producer_dependency_sha256s", "validator_dependency_sha256s"):
        values = source[key]
        _require(isinstance(values, list) and values, f"$.payload.source.{key}", "expected nonempty array")
        for index, digest in enumerate(values):
            _require_sha(digest, f"$.payload.source.{key}[{index}]")
    _require(set(source["producer_dependency_sha256s"]).isdisjoint(source["validator_dependency_sha256s"]), "$.payload.source", "producer and validator dependency sets must be disjoint")


def _validate_work_unit(payload: dict[str, Any], registry: Mapping[str, Any], retainable: bool) -> None:
    _, vectors, methods = _registry_sets(registry)
    _require_sha(payload["campaign_id"], "$.payload.campaign_id")
    vector = _require_sha(payload["target_vector_sha256"], "$.payload.target_vector_sha256")
    _require(vector in vectors, "$.payload.target_vector_sha256", "unknown target-vector digest")
    method = _require_method(payload["method_id"], "$.payload.method_id")
    _require(method in methods, "$.payload.method_id", "method is not allowlisted")
    _require_nonnegative_int(payload["algorithm_seed"], "$.payload.algorithm_seed")
    retry = _require_nonnegative_int(payload["retry_index"], "$.payload.retry_index")
    _require_sha(payload["attempt_id"], "$.payload.attempt_id")
    _validate_source(payload["source"], retainable)
    _require(payload["attempt_id"] == compute_attempt_id(payload["work_unit_id"], retry), "$.payload.attempt_id", "does not derive from work_unit_id and retry_index")


def _validate_method_request(payload: dict[str, Any], registry: Mapping[str, Any]) -> None:
    _, vectors, methods = _registry_sets(registry)
    _require_sha(payload["work_unit_id"], "$.payload.work_unit_id")
    vector_digest = _require_sha(payload["target_vector_sha256"], "$.payload.target_vector_sha256")
    _require(vector_digest in vectors, "$.payload.target_vector_sha256", "unknown target-vector digest")
    method = _require_method(payload["method_id"], "$.payload.method_id")
    _require(method in methods, "$.payload.method_id", "method is not allowlisted")
    _require_nonnegative_int(payload["algorithm_seed"], "$.payload.algorithm_seed")
    curve = payload["curve"]
    _require(isinstance(curve, dict), "$.payload.curve", "curve must be object")
    _exact_keys(curve, {"curve_id", "field_p", "curve_a", "curve_b"}, "$.payload.curve")
    _require_id(curve["curve_id"], "$.payload.curve.curve_id")
    p = _require_positive_int(curve["field_p"], "$.payload.curve.field_p")
    _require(p != SECP256K1_P and p.bit_length() <= 32, "$.payload.curve.field_p", "forbidden or oversized field")
    for key in ("curve_a", "curve_b"):
        coefficient = _require_nonnegative_int(curve[key], f"$.payload.curve.{key}")
        _require(coefficient < p, f"$.payload.curve.{key}", "coefficient outside field")
    order = _require_positive_int(payload["subgroup_order"], "$.payload.subgroup_order")
    _require(order != SECP256K1_N and order <= MAX_SUBGROUP_ORDER, "$.payload.subgroup_order", "forbidden or oversized subgroup")
    _validate_point(payload["base_point"], p, "$.payload.base_point")
    _validate_point(payload["target_point"], p, "$.payload.target_point")
    _validate_interval(payload["public_interval"], order, "$.payload.public_interval")
    _validate_budgets(payload["budgets"], "$.payload.budgets")
    expected = registry["target_vectors"][vector_digest]
    for key, actual in (
        ("curve_id", curve["curve_id"]),
        ("field_p", p),
        ("curve_a", curve["curve_a"]),
        ("curve_b", curve["curve_b"]),
        ("base_point", payload["base_point"]),
        ("target_point", payload["target_point"]),
        ("subgroup_order", order),
    ):
        _require(actual == expected[key], f"$.payload.{key}", "public request does not match digest-bound target vector")


def _validate_method_result(payload: dict[str, Any], registry: Mapping[str, Any]) -> None:
    _, _, methods = _registry_sets(registry)
    _require_sha(payload["work_unit_id"], "$.payload.work_unit_id")
    method = _require_method(payload["method_id"], "$.payload.method_id")
    _require(method in methods, "$.payload.method_id", "method is not allowlisted")
    status = payload["status"]
    _require(status in {"solved", "bounded_failure", "error", "resource_exhausted"}, "$.payload.status", "invalid result status")
    scalar = payload["claimed_scalar"]
    if status == "solved":
        _require_nonnegative_int(scalar, "$.payload.claimed_scalar")
    else:
        _require(scalar is None, "$.payload.claimed_scalar", "failure records cannot claim a scalar")
    counters = payload["counters"]
    _require(isinstance(counters, dict), "$.payload.counters", "expected object")
    allowed = {"group_law_invocations", "additions", "doublings", "inversions", "multiplications", "squarings", "negations", "table_entries", "estimated_table_bytes", "restarts", "collisions", "noninvertible_collisions", "distinguished_points"}
    _exact_keys(counters, allowed, "$.payload.counters")
    for key, value in counters.items():
        _require_nonnegative_int(value, f"$.payload.counters.{key}")
    _require(isinstance(payload["artifact_sha256s"], list), "$.payload.artifact_sha256s", "expected array")
    for index, digest in enumerate(payload["artifact_sha256s"]):
        _require_sha(digest, f"$.payload.artifact_sha256s[{index}]")
    _require(payload["message"] is None or isinstance(payload["message"], str), "$.payload.message", "must be string or null")


def _validate_telemetry(payload: dict[str, Any]) -> None:
    _require_sha(payload["attempt_id"], "$.payload.attempt_id")
    for key in ("wall_time_ns", "cpu_time_ns", "max_rss_bytes"):
        _require_nonnegative_int(payload[key], f"$.payload.{key}")
    _require(isinstance(payload["exit_code"], int) and not isinstance(payload["exit_code"], bool), "$.payload.exit_code", "expected integer")
    workers = _require_positive_int(payload["parallel_workers"], "$.payload.parallel_workers")
    _require(workers <= 64, "$.payload.parallel_workers", "worker cap is 64")
    for key in ("platform", "python_version"):
        _require(isinstance(payload[key], str) and payload[key], f"$.payload.{key}", "expected nonempty string")
    tools = payload["tool_versions"]
    _require(isinstance(tools, dict), "$.payload.tool_versions", "expected object")
    for key, value in tools.items():
        _require(isinstance(key, str) and key and isinstance(value, str) and value, "$.payload.tool_versions", "tool names and versions must be nonempty strings")


def _validate_validation_receipt(payload: dict[str, Any], registry: Mapping[str, Any]) -> None:
    _, _, methods = _registry_sets(registry)
    _require_sha(payload["work_unit_id"], "$.payload.work_unit_id")
    _require_sha(payload["method_result_sha256"], "$.payload.method_result_sha256")
    method = _require_method(payload["method_id"], "$.payload.method_id")
    _require(method in methods, "$.payload.method_id", "method is not allowlisted")
    _require_sha(payload["producer_source_sha256"], "$.payload.producer_source_sha256")
    validator = _require_method(payload["validator_id"], "$.payload.validator_id")
    _require(validator != method, "$.payload.validator_id", "self-validation is forbidden")
    _require_sha(payload["validator_source_sha256"], "$.payload.validator_source_sha256")
    _require(payload["producer_source_sha256"] != payload["validator_source_sha256"], "$.payload.validator_source_sha256", "validator must not share the producer source digest")
    _require(payload["independent_implementation"] is True, "$.payload.independent_implementation", "must be true")
    _require(payload["shares_decisive_logic"] is False, "$.payload.shares_decisive_logic", "must be false")
    _require(isinstance(payload["passed"], bool), "$.payload.passed", "must be boolean")
    if payload["passed"]:
        _require_nonnegative_int(payload["recomputed_scalar"], "$.payload.recomputed_scalar")
    else:
        _require(payload["recomputed_scalar"] is None, "$.payload.recomputed_scalar", "failed validation cannot expose a recomputed scalar")
    _require_sha(payload["private_receipt_sha256"], "$.payload.private_receipt_sha256")
    _require_sha(payload["validator_output_sha256"], "$.payload.validator_output_sha256")


def _validate_analysis(payload: dict[str, Any]) -> None:
    _require_sha(payload["campaign_id"], "$.payload.campaign_id")
    _require(isinstance(payload["validation_receipt_sha256s"], list) and payload["validation_receipt_sha256s"], "$.payload.validation_receipt_sha256s", "expected nonempty array")
    for index, digest in enumerate(payload["validation_receipt_sha256s"]):
        _require_sha(digest, f"$.payload.validation_receipt_sha256s[{index}]")
    metrics = payload["normalized_metrics"]
    _require(isinstance(metrics, dict), "$.payload.normalized_metrics", "expected object")
    for key, value in metrics.items():
        _require(isinstance(key, str) and key, "$.payload.normalized_metrics", "metric name must be nonempty")
        if isinstance(value, str):
            _require(DECIMAL_STRING.fullmatch(value) is not None, f"$.payload.normalized_metrics.{key}", "string metric must be an unsigned decimal string")
        else:
            _require_nonnegative_int(value, f"$.payload.normalized_metrics.{key}")
    _require(isinstance(payload["warnings"], list), "$.payload.warnings", "expected array")
    for index, warning in enumerate(payload["warnings"]):
        _require(isinstance(warning, str) and warning, f"$.payload.warnings[{index}]", "expected nonempty string")
    claims = payload["claims"]
    _require(isinstance(claims, dict), "$.payload.claims", "expected object")
    _exact_keys(claims, {"asymptotic_claim", "secp256k1_break", "route_promotion", "scientific_outcome"}, "$.payload.claims")
    _require(claims["asymptotic_claim"] is None, "$.payload.claims.asymptotic_claim", "lab analysis cannot make an asymptotic claim")
    for key in ("secp256k1_break", "route_promotion", "scientific_outcome"):
        _require(claims[key] is False, f"$.payload.claims.{key}", "must be false")


def _validate_artifact(payload: dict[str, Any]) -> None:
    _require_sha(payload["sha256"], "$.payload.sha256")
    _require_nonnegative_int(payload["size_bytes"], "$.payload.size_bytes")
    _require(isinstance(payload["media_type"], str) and "/" in payload["media_type"], "$.payload.media_type", "expected media type")
    _require_id(payload["role"], "$.payload.role")
    if payload["location"] is not None:
        try:
            validate_relative_posix_path(payload["location"])
        except PathPolicyError as exc:
            raise _error("$.payload.location", str(exc)) from exc
        _require(not payload["location"].startswith("experiments/engine/"), "$.payload.location", "lab artifacts cannot target Engine state")


def validate_record(record: Any, registry: Mapping[str, Any]) -> None:
    kind, payload = _validate_common(record)
    dispatch = {
        "campaign_config": lambda: _validate_campaign(payload, registry),
        "target_vector": lambda: _validate_target_vector(payload, registry),
        "work_unit": lambda: _validate_work_unit(payload, registry, record["retainable"]),
        "method_request": lambda: _validate_method_request(payload, registry),
        "method_result": lambda: _validate_method_result(payload, registry),
        "telemetry": lambda: _validate_telemetry(payload),
        "validation_receipt": lambda: _validate_validation_receipt(payload, registry),
        "analysis_summary": lambda: _validate_analysis(payload),
        "artifact_ref": lambda: _validate_artifact(payload),
    }
    dispatch[kind]()

    identity_field = IDENTITY_FIELD[kind]
    _require_sha(payload[identity_field], f"$.payload.{identity_field}")
    expected_identity = compute_identity(record)
    _require(payload[identity_field] == expected_identity, f"$.payload.{identity_field}", "identity is not derived from canonical semantics")

    expected_record = compute_record_sha256(record)
    _require(record["record_sha256"] == expected_record, "$.record_sha256", "record digest mismatch")


def validate_record_file(path: Path, registry: Mapping[str, Any]) -> dict[str, Any]:
    record = load_strict(path)
    validate_record(record, registry)
    return record
