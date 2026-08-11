#!/usr/bin/env python3
"""Generate deterministic positive and adversarial P01 contract fixtures."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.ecdlp_lab.core.canonical_json import dumps_canonical, sha256_hex
from experiments.ecdlp_lab.core.contract_validation import build_record


ROOT = Path(__file__).resolve().parent
ZERO = "0" * 64
A = "a" * 64
B = "b" * 64
C = "c" * 64
D = "d" * 64
E = "e" * 64
F = "f" * 64


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    catalog_meta = {
        "catalog_id": "p01-fixture-catalog-v1",
        "catalog_kind": "synthetic_contract_fixture",
        "max_subgroup_bits": 5,
    }
    catalog_sha = sha256_hex(catalog_meta)

    target_vector = build_record(
        "target_vector",
        {
            "catalog_sha256": catalog_sha,
            "curve_id": "fixture-j0-p43",
            "field_p": 43,
            "curve_a": 0,
            "curve_b": 7,
            "base_point": {"x": 2, "y": 12},
            "target_point": {"x": 12, "y": 12},
            "subgroup_order": 31,
            "field_bits": 6,
            "subgroup_order_bits": 5,
            "public_interval": None,
            "private_receipt_sha256": A,
        },
    )
    vector_sha = target_vector["record_sha256"]

    registry = {
        "schema_version": "1.0",
        "catalogs": {catalog_sha: catalog_meta},
        "target_vectors": {
            vector_sha: {
                "target_vector_id": target_vector["payload"]["target_vector_id"],
                "catalog_sha256": catalog_sha,
                "curve_id": "fixture-j0-p43",
                "field_p": 43,
                "curve_a": 0,
                "curve_b": 7,
                "base_point": {"x": 2, "y": 12},
                "target_point": {"x": 12, "y": 12},
                "subgroup_order": 31,
            }
        },
        "allowed_method_ids": ["bsgs_reference_v1", "rho_reference_v1"],
    }

    budgets = {
        "timeout_ns": 5_000_000_000,
        "max_rss_bytes": 268_435_456,
        "max_group_operations": 1_000_000,
        "parallel_workers": 1,
    }
    campaign = build_record(
        "campaign_config",
        {
            "catalog_sha256": catalog_sha,
            "target_vector_sha256s": [vector_sha],
            "method_ids": ["bsgs_reference_v1", "rho_reference_v1"],
            "algorithm_seeds": [101, 202],
            "budgets": budgets,
            "output_subdir": "artifacts/p01-fixture-campaign",
            "reusable_setup": False,
            "amortization_target_count": 1,
        },
    )
    campaign_id = campaign["payload"]["campaign_id"]

    work_unit = build_record(
        "work_unit",
        {
            "retry_index": 0,
            "campaign_id": campaign_id,
            "target_vector_sha256": vector_sha,
            "method_id": "bsgs_reference_v1",
            "algorithm_seed": 101,
            "source": {
                "commit": "1" * 40,
                "clean_tree": True,
                "source_snapshot_sha256": B,
                "diff_sha256": None,
                "producer_dependency_sha256s": [C],
                "validator_dependency_sha256s": [D],
            },
        },
    )
    work_unit_id = work_unit["payload"]["work_unit_id"]
    attempt_id = work_unit["payload"]["attempt_id"]

    method_request = build_record(
        "method_request",
        {
            "work_unit_id": work_unit_id,
            "target_vector_sha256": vector_sha,
            "method_id": "bsgs_reference_v1",
            "algorithm_seed": 101,
            "curve": {
                "curve_id": "fixture-j0-p43",
                "field_p": 43,
                "curve_a": 0,
                "curve_b": 7,
            },
            "base_point": {"x": 2, "y": 12},
            "target_point": {"x": 12, "y": 12},
            "subgroup_order": 31,
            "public_interval": None,
            "budgets": budgets,
        },
    )

    artifact = build_record(
        "artifact_ref",
        {
            "sha256": E,
            "size_bytes": 321,
            "media_type": "application/json",
            "role": "method-result",
            "location": "artifacts/p01-fixture-campaign/result.json",
        },
    )

    method_result = build_record(
        "method_result",
        {
            "work_unit_id": work_unit_id,
            "method_id": "bsgs_reference_v1",
            "status": "solved",
            "claimed_scalar": 5,
            "counters": {
                "group_law_invocations": 12,
                "additions": 8,
                "doublings": 4,
                "inversions": 12,
                "multiplications": 60,
                "squarings": 12,
                "negations": 0,
                "table_entries": 6,
                "estimated_table_bytes": 384,
                "restarts": 0,
                "collisions": 0,
                "noninvertible_collisions": 0,
                "distinguished_points": 0,
            },
            "artifact_sha256s": [artifact["record_sha256"]],
            "message": None,
        },
    )

    telemetry = build_record(
        "telemetry",
        {
            "attempt_id": attempt_id,
            "wall_time_ns": 10_000_000,
            "cpu_time_ns": 9_000_000,
            "max_rss_bytes": 12_000_000,
            "exit_code": 0,
            "parallel_workers": 1,
            "platform": "fixture-linux-x86_64",
            "python_version": "3.12.0",
            "tool_versions": {"fixture-method": "1.0"},
        },
    )

    validation = build_record(
        "validation_receipt",
        {
            "work_unit_id": work_unit_id,
            "method_result_sha256": method_result["record_sha256"],
            "method_id": "bsgs_reference_v1",
            "producer_source_sha256": C,
            "validator_id": "ec_oracle_validator_v1",
            "validator_source_sha256": D,
            "independent_implementation": True,
            "shares_decisive_logic": False,
            "passed": True,
            "recomputed_scalar": 5,
            "private_receipt_sha256": A,
            "validator_output_sha256": F,
        },
    )

    analysis = build_record(
        "analysis_summary",
        {
            "campaign_id": campaign_id,
            "validation_receipt_sha256s": [validation["record_sha256"]],
            "normalized_metrics": {
                "validated_work_units": 1,
                "median_group_operations": "12.0",
                "success_probability": "1.0",
            },
            "warnings": ["P01 fixture only; no scientific outcome."],
            "claims": {
                "asymptotic_claim": None,
                "secp256k1_break": False,
                "route_promotion": False,
                "scientific_outcome": False,
            },
        },
    )

    valid = {
        "target_vector": target_vector,
        "campaign_config": campaign,
        "work_unit": work_unit,
        "method_request": method_request,
        "artifact_ref": artifact,
        "method_result": method_result,
        "telemetry": telemetry,
        "validation_receipt": validation,
        "analysis_summary": analysis,
    }

    invalid = []

    def add(name: str, base: str, mutate, expected: str) -> None:
        record = copy.deepcopy(valid[base])
        mutate(record)
        invalid.append({"name": name, "record": record, "expected_error": expected})

    add("unknown_top_field", "campaign_config", lambda r: r.__setitem__("surprise", 1), "unknown fields")
    add("malformed_digest", "artifact_ref", lambda r: r["payload"].__setitem__("sha256", "abc"), "SHA-256")
    add("absolute_path", "artifact_ref", lambda r: r["payload"].__setitem__("location", "/tmp/out"), "absolute")
    add("parent_path", "artifact_ref", lambda r: r["payload"].__setitem__("location", "artifacts/../escape"), "parent")
    add("engine_path", "artifact_ref", lambda r: r["payload"].__setitem__("location", "experiments/engine/runs/bad.json"), "Engine")
    add("missing_provenance", "work_unit", lambda r: r["payload"].pop("source"), "missing fields")
    add("dirty_marked_retainable", "work_unit", lambda r: (r["payload"]["source"].__setitem__("clean_tree", False), r["payload"]["source"].__setitem__("diff_sha256", E)), "dirty")
    add("self_validation", "validation_receipt", lambda r: r["payload"].__setitem__("validator_id", "bsgs_reference_v1"), "self-validation")
    add("shared_validator_source", "validation_receipt", lambda r: r["payload"].__setitem__("validator_source_sha256", C), "producer source")
    add("hidden_precomputation", "method_request", lambda r: r["payload"].__setitem__("hidden_precomputation", True), "unknown fields")
    add("target_scalar_in_request", "method_request", lambda r: r["payload"].__setitem__("expected_scalar", 5), "unknown fields")
    add("shared_target_seed", "method_request", lambda r: r["payload"].__setitem__("target_generation_seed", 101), "unknown fields")
    add("candidate_id", "campaign_config", lambda r: r.__setitem__("candidate_id", "candidate-1"), "scientific IDs")
    add("hypothesis_id", "campaign_config", lambda r: r.__setitem__("hypothesis_id", "HYP-1"), "scientific IDs")
    add("authorization_id", "campaign_config", lambda r: r.__setitem__("authorization_id", "AUTH-1"), "scientific IDs")
    add("engine_record_kind", "campaign_config", lambda r: r.__setitem__("record_kind", "candidate_run"), "Engine/candidate")
    add("unknown_catalog", "campaign_config", lambda r: r["payload"].__setitem__("catalog_sha256", ZERO), "unknown catalog")
    add("unknown_vector", "campaign_config", lambda r: r["payload"].__setitem__("target_vector_sha256s", [ZERO]), "unknown target-vector")
    add("external_target_point", "method_request", lambda r: r["payload"].__setitem__("target_point", {"x": 13, "y": 21}), "does not match")
    add("secp_field", "method_request", lambda r: r["payload"]["curve"].__setitem__("field_p", 2**256 - 2**32 - 977), "forbidden or oversized")
    add("subgroup_33_bits", "method_request", lambda r: r["payload"].__setitem__("subgroup_order", 2**32 + 15), "forbidden or oversized")
    add("dirty_record_hash", "analysis_summary", lambda r: r.__setitem__("record_sha256", ZERO), "record digest mismatch")
    add("freely_supplied_work_unit_id", "work_unit", lambda r: r["payload"].__setitem__("work_unit_id", ZERO), "does not derive")

    raw_json_cases = [
        {"name": "duplicate_key", "text": '{"a":1,"a":2}', "expected_error": "duplicate JSON key"},
        {"name": "nan", "text": '{"value":NaN}', "expected_error": "non-finite"},
        {"name": "infinity", "text": '{"value":Infinity}', "expected_error": "non-finite"},
        {"name": "negative_zero_integer", "text": '{"value":-0}', "expected_error": "negative zero"},
        {"name": "negative_zero_decimal", "text": '{"value":-0.000e+12}', "expected_error": "negative zero"},
        {"name": "float_literal", "text": '{"value":0.5}', "expected_error": "floating-point"},
    ]

    write_json(ROOT / "registry.json", registry)
    write_json(ROOT / "valid_records.json", valid)
    write_json(ROOT / "invalid_records.json", invalid)
    write_json(ROOT / "invalid_raw_json.json", raw_json_cases)

    manifest = {
        "schema_version": "1.0",
        "files": {
            name: sha256_hex(json.loads((ROOT / name).read_text(encoding="utf-8")))
            for name in ("registry.json", "valid_records.json", "invalid_records.json", "invalid_raw_json.json")
        },
    }
    write_json(ROOT / "manifest.json", manifest)
    print(dumps_canonical(manifest))


if __name__ == "__main__":
    main()
