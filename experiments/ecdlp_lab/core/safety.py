"""Non-configurable authorization and toy-domain safety boundary."""

from __future__ import annotations

from typing import Any, Iterator

from .issues import Issue

RECORD_KIND = "lab_engineering_fixture"
MAX_SUBGROUP_ORDER_BITS = 32
MAX_FIELD_BITS = 32

SECP256K1_FIELD_P = int(
    "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F", 16
)
SECP256K1_SUBGROUP_N = int(
    "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141", 16
)

CONTRACT_KINDS = (
    "campaign_config_v1",
    "target_vector_v1",
    "work_unit_v1",
    "method_request_v1",
    "method_result_v1",
    "telemetry_v1",
    "validation_receipt_v1",
    "analysis_summary_v1",
    "artifact_ref_v1",
)

SYNTHETIC_SOURCE_KINDS = frozenset(
    {"committed_lab_catalog", "read_only_legacy_catalog"}
)


def _walk(value: Any, path: str = "$") -> Iterator[tuple[str, str, Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            yield child_path, key, child
            yield from _walk(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, f"{path}[{index}]")


def _curve_payloads(record: dict[str, Any]) -> Iterator[tuple[str, dict[str, Any]]]:
    public = record.get("public_payload")
    if isinstance(public, dict):
        yield "$.public_payload", public
    curve = record.get("curve")
    if isinstance(curve, dict):
        bound = dict(curve)
        for key in ("generator", "target", "subgroup_order", "subgroup_order_bits"):
            if key in record:
                bound[key] = record[key]
        yield "$.curve", bound


def validate_safety(
    record: Any, *, expected_kind: str | None = None
) -> list[Issue]:
    """Return stable issues for any violation of the hard lab boundary.

    This validator is deliberately independent of JSON Schema so callers
    cannot bypass the authorization and size ceiling with a replacement
    schema.  It never mutates the record and does not raise for bad content.
    """

    if not isinstance(record, dict):
        return [Issue("safety.record.type", "$", "record must be an object")]

    issues: list[Issue] = []
    exact = {
        "schema_version": 1,
        "record_kind": RECORD_KIND,
        "internal_classification": "engineering_only",
        "framework_authorization_class": "fixture",
        "hypothesis_id": None,
        "candidate_id": None,
        "authorization_id": None,
        "native_research_outcome": False,
        "route_effect": "none",
        "retention_class": "engineering_only",
    }
    for key, required in exact.items():
        if record.get(key) != required:
            issues.append(
                Issue(
                    "safety.boundary",
                    f"$.{key}",
                    f"lab boundary requires {required!r}",
                )
            )

    kind = record.get("contract_kind")
    if kind not in CONTRACT_KINDS:
        issues.append(
            Issue("safety.contract_kind", "$.contract_kind", "unknown lab contract family")
        )
    if expected_kind is not None and kind != expected_kind:
        issues.append(
            Issue(
                "safety.contract_dispatch",
                "$.contract_kind",
                f"expected {expected_kind!r}",
            )
        )

    provenance = record.get("provenance")
    retainable = record.get("retainable")
    if isinstance(provenance, dict):
        clean = provenance.get("source_tree_clean")
        diff = provenance.get("diff_sha256")
        if clean is True and diff is not None:
            issues.append(
                Issue(
                    "safety.clean_diff",
                    "$.provenance.diff_sha256",
                    "a clean tree must not carry a diff digest",
                )
            )
        if clean is False and diff is None:
            issues.append(
                Issue(
                    "safety.dirty_diff",
                    "$.provenance.diff_sha256",
                    "a dirty tree must bind its exact diff digest",
                )
            )
        if clean is not True and retainable is True:
            issues.append(
                Issue(
                    "safety.dirty_retainable",
                    "$.retainable",
                    "dirty or unproven records cannot be retainable",
                )
            )
    elif retainable is True:
        issues.append(
            Issue(
                "safety.missing_provenance",
                "$.provenance",
                "retainable records require provenance",
            )
        )

    for path, key, value in _walk(record):
        if key in {"subgroup_order_bits", "max_subgroup_order_bits"}:
            if isinstance(value, int) and not isinstance(value, bool):
                if value > MAX_SUBGROUP_ORDER_BITS:
                    issues.append(
                        Issue(
                            "safety.subgroup_bits",
                            path,
                            "subgroup ceiling is 32 bits",
                        )
                    )
        if key in {"field_bits", "max_field_bits"}:
            if isinstance(value, int) and not isinstance(value, bool):
                if value > MAX_FIELD_BITS:
                    issues.append(
                        Issue("safety.field_bits", path, "field ceiling is 32 bits")
                    )
        if key in {"field_p", "p"} and value == SECP256K1_FIELD_P:
            issues.append(
                Issue("safety.secp256k1", path, "exact secp256k1 field is forbidden")
            )
        if key in {"subgroup_order", "n"} and value == SECP256K1_SUBGROUP_N:
            issues.append(
                Issue("safety.secp256k1", path, "exact secp256k1 order is forbidden")
            )

    for base, curve in _curve_payloads(record):
        order = curve.get("subgroup_order")
        order_bits = curve.get("subgroup_order_bits")
        if isinstance(order, int) and not isinstance(order, bool):
            if order.bit_length() > MAX_SUBGROUP_ORDER_BITS:
                issues.append(
                    Issue(
                        "safety.subgroup_bits",
                        f"{base}.subgroup_order",
                        "subgroup order exceeds the 32-bit ceiling",
                    )
                )
            if isinstance(order_bits, int) and order_bits != order.bit_length():
                issues.append(
                    Issue(
                        "safety.subgroup_bit_length",
                        f"{base}.subgroup_order_bits",
                        "declared bit length does not match subgroup order",
                    )
                )
        field_p = curve.get("field_p")
        field_bits = curve.get("field_bits")
        if isinstance(field_p, int) and not isinstance(field_p, bool):
            if field_p.bit_length() > MAX_FIELD_BITS:
                issues.append(
                    Issue(
                        "safety.field_bits",
                        f"{base}.field_p",
                        "field exceeds the 32-bit ceiling",
                    )
                )
            if isinstance(field_bits, int) and field_bits != field_p.bit_length():
                issues.append(
                    Issue(
                        "safety.field_bit_length",
                        f"{base}.field_bits",
                        "declared bit length does not match field modulus",
                    )
                )
            for name in ("curve_a", "curve_b"):
                coefficient = curve.get(name)
                if isinstance(coefficient, int) and not 0 <= coefficient < field_p:
                    issues.append(
                        Issue(
                            "safety.field_element",
                            f"{base}.{name}",
                            "curve coefficient is outside the field",
                        )
                    )
            for name in ("generator", "target"):
                point = curve.get(name)
                if isinstance(point, list):
                    for index, coordinate in enumerate(point):
                        if isinstance(coordinate, int) and not 0 <= coordinate < field_p:
                            issues.append(
                                Issue(
                                    "safety.external_point",
                                    f"{base}.{name}[{index}]",
                                    "point coordinate is outside the bound field",
                                )
                            )

    public = record.get("public_payload")
    if isinstance(public, dict) and public.get("source_kind") not in SYNTHETIC_SOURCE_KINDS:
        issues.append(
            Issue(
                "safety.synthetic_origin",
                "$.public_payload.source_kind",
                "target must originate in an approved synthetic catalog",
            )
        )
    return sorted(set(issues))
