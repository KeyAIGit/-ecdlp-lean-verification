#!/usr/bin/env python3
"""Quarantine and index an external evidence atlas without granting authority."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CONTRACT_PATH = ROOT / "repo" / "UNTRUSTED_EVIDENCE_INTAKE_V0.json"

CONTRACT_FIELDS = {
    "schema_version",
    "contract_id",
    "intake_id",
    "status",
    "source_directory",
    "output_path",
    "sources",
    "expected_observations",
    "parsing_contract",
    "authority_ceiling",
    "canonical_write_prohibited",
    "protected_main_receipt",
    "required_state",
    "regenerate",
    "check",
    "test",
}
SOURCE_FIELDS = {"path", "media_type", "sha256", "git_blob_sha1"}
PARSING_CONTRACT = {
    "duplicate_json_keys": "reject",
    "non_finite_numbers": "reject",
    "property_values": "retain_as_raw_strings_without_type_coercion",
    "boolean_lexemes_for_parseability_only": ["false", "true"],
    "tp_like_reference_pattern": (
        r"(?<![A-Za-z0-9_-])(TP-[A-Z0-9][A-Z0-9-]*)(?![A-Za-z0-9_-])"
    ),
    "join_rule": (
        "A verified join requires typed requirement IDs that resolve to property "
        "IDs and a machine-readable verdict matrix. This snapshot has neither."
    ),
    "source_status_rule": (
        "source_verified is an untrusted source-authored annotation, not evidence "
        "that a primary artifact was obtained or read."
    ),
}
EXPECTED_OBSERVATION_FIELDS = {
    "mechanisms",
    "properties",
    "requirement_strings",
    "free_text_requirement_strings",
    "tp_like_requirement_strings",
    "tp_like_reference_occurrences",
    "unique_tp_like_references",
    "unique_orphan_tp_like_references",
    "declared_integer_values",
    "declared_boolean_values",
    "declared_integer_parse_violations",
    "declared_boolean_parse_violations",
    "declared_type_parse_violations",
    "mechanism_full_text_read_rows",
    "report_claimed_full_text_read_rows",
    "verified_join_rows",
}
REQUIRED_STATE_FIELDS = {
    "intake_status",
    "join_status",
    "verified_join",
    "safe_for_scientific_selection",
    "safe_for_calibration",
    "safe_for_authorization",
}
PROTECTED_RECEIPT_FIELDS = {
    "mode",
    "protected_ref",
    "contract_path",
    "frozen_fields",
}
PROTECTED_FROZEN_FIELDS = (
    "intake_id",
    "status",
    "source_directory",
    "output_path",
    "sources",
    "expected_observations",
    "parsing_contract",
    "authority_ceiling",
    "canonical_write_prohibited",
    "required_state",
    "protected_main_receipt",
)
QUARANTINE_REFERENCE_TOKENS = {
    "archive/untrusted_intake",
    "data/untrusted_evidence_intake",
    "untrusted_evidence_intake",
    "build_untrusted_evidence_intake",
    "opus-ecdlp-screen-atlas-2026-07-26",
    "all_mechanisms.json",
    "all_properties.json",
    "ecdlp_screen_atlas_report.md",
}
QUARANTINE_REFERENCE_SCAN_ROOTS = (
    "scripts",
    "repo",
    "data",
    "experiments",
    ".github/workflows",
)
QUARANTINE_REFERENCE_SCAN_SUFFIXES = {
    ".bat",
    ".c",
    ".cmd",
    ".cpp",
    ".go",
    ".h",
    ".ipynb",
    ".js",
    ".json",
    ".jsx",
    ".lean",
    ".ps1",
    ".py",
    ".rs",
    ".sh",
    ".toml",
    ".ts",
    ".tsx",
    ".yaml",
    ".yml",
}
QUARANTINE_REFERENCE_ALLOWLIST = {
    ".github/workflows/ci.yml",
    ".github/workflows/docs-sync.yml",
    "data/untrusted_evidence_intake/OPUS-ECDLP-SCREEN-ATLAS-2026-07-26.json",
    "repo/ARTIFACTS.yaml",
    "repo/UNTRUSTED_EVIDENCE_INTAKE_V0.json",
    "scripts/build_untrusted_evidence_intake.py",
    "scripts/check_generated_fixpoint.py",
    "scripts/test_untrusted_evidence_intake.py",
}

MECHANISM_FIELDS = {
    "id",
    "family",
    "source",
    "source_verified",
    "requires",
    "changed_quantity",
    "growth_lever",
}
PROPERTY_FIELDS = {
    "id",
    "statement",
    "value",
    "value_type",
    "status",
    "how_obtained",
}
PROPERTY_TYPES = {"integer", "boolean", "string", "unknown"}
SOURCE_STATUSES = {"full_text_read", "abstract_only", "secondhand", "not_obtained"}
AUTHORITY_KEYS = {
    "direct_canonical_imports",
    "scientific_outcomes",
    "ranker_labels",
    "route_closures",
    "authorization",
    "typed_evidence_updates",
    "attack_registry_updates",
    "decision_updates",
    "claim_updates",
    "outcome_updates",
}
CANONICAL_WRITE_PROHIBITED = {
    "data/attack_registry.json",
    "repo/ECDLP_TYPED_EVIDENCE_V0.json",
    "repo/ECDLP_DECISION_SUBSTRATE.json",
    "repo/RESEARCH_CLAIMS_V0.json",
    "repo/RESEARCH_ENGINE_V0.json",
    "experiments/engine/outcomes",
}


class IntakeError(ValueError):
    """Raised when an untrusted snapshot violates the quarantine contract."""


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_json(value: Any) -> str:
    return sha256_bytes(canonical_json(value).encode("ascii"))


def git_blob_sha1(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def _git_file_bytes(root: Path, ref: str, relative: str) -> bytes | None:
    result = subprocess.run(
        ["git", "show", f"{ref}:{relative}"],
        cwd=root,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    return result.stdout if result.returncode == 0 else None


def append_only_receipt_problems(
    contract: dict[str, Any], baseline: dict[str, Any] | None
) -> list[str]:
    """Compare one intake with its first protected-main receipt."""
    if baseline is None:
        return []
    receipt = contract["protected_main_receipt"]
    problems: list[str] = []
    if baseline.get("intake_id") != contract.get("intake_id"):
        return ["protected main already contains a different intake receipt"]
    for field in receipt["frozen_fields"]:
        if baseline.get(field) != contract.get(field):
            problems.append(f"protected-main receipt drifted: {field}")
    return problems


def validate_protected_main_receipt(
    contract: dict[str, Any], *, root: Path = ROOT
) -> None:
    receipt = contract["protected_main_receipt"]
    payload = _git_file_bytes(
        root, receipt["protected_ref"], receipt["contract_path"]
    )
    baseline = None
    if payload is not None:
        try:
            baseline = loads_strict(
                payload.decode("utf-8"), label="protected-main intake receipt"
            )
        except UnicodeError as error:
            raise IntakeError(
                f"protected-main intake receipt is not UTF-8: {error}"
            ) from error
        _require(
            isinstance(baseline, dict),
            "protected-main intake receipt must be an object",
        )
    problems = append_only_receipt_problems(contract, baseline)
    _require(not problems, "; ".join(problems))


def forbidden_consumer_references(
    documents: dict[str, str],
    *,
    allowlist: set[str] = QUARANTINE_REFERENCE_ALLOWLIST,
    reference_tokens: set[str] = QUARANTINE_REFERENCE_TOKENS,
) -> list[str]:
    """Find quarantine references outside the intake implementation surface."""
    problems: list[str] = []
    for relative, content in sorted(documents.items()):
        normalized = relative.replace("\\", "/")
        if normalized in allowlist:
            continue
        folded = content.casefold().replace("\\", "/")
        if any(token.casefold() in folded for token in reference_tokens):
            problems.append(normalized)
    return problems


def quarantine_reference_tokens(contract: dict[str, Any]) -> set[str]:
    """Bind the lexical guard to this receipt as well as known path classes."""
    tokens = set(QUARANTINE_REFERENCE_TOKENS)
    for field in ("intake_id", "source_directory", "output_path"):
        value = contract.get(field)
        if isinstance(value, str) and value:
            tokens.add(value.casefold().replace("\\", "/"))
    for source in contract.get("sources", []):
        if isinstance(source, dict):
            value = source.get("path")
            if isinstance(value, str) and value:
                tokens.add(value.casefold().replace("\\", "/"))
    return tokens


def scan_forbidden_consumers(
    *, root: Path = ROOT, contract: dict[str, Any] | None = None
) -> list[str]:
    documents: dict[str, str] = {}
    for scan_root in QUARANTINE_REFERENCE_SCAN_ROOTS:
        directory = root / scan_root
        if not directory.is_dir():
            continue
        for path in directory.rglob("*"):
            if (
                not path.is_file()
                or path.suffix.lower() not in QUARANTINE_REFERENCE_SCAN_SUFFIXES
            ):
                continue
            relative = path.relative_to(root).as_posix()
            try:
                documents[relative] = path.read_text(encoding="utf-8")
            except UnicodeError as error:
                raise IntakeError(
                    f"consumer scan cannot decode UTF-8 file {relative}: {error}"
                ) from error
    reference_tokens = (
        QUARANTINE_REFERENCE_TOKENS
        if contract is None
        else quarantine_reference_tokens(contract)
    )
    return forbidden_consumer_references(
        documents, reference_tokens=reference_tokens
    )


def _reject_constant(value: str) -> None:
    raise IntakeError(f"non-finite JSON number is forbidden: {value}")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise IntakeError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def loads_strict(payload: str, *, label: str) -> Any:
    try:
        return json.loads(
            payload,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except IntakeError:
        raise
    except (json.JSONDecodeError, UnicodeError) as error:
        raise IntakeError(f"{label}: invalid JSON: {error}") from error


def load_json_strict(path: Path) -> Any:
    try:
        payload = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise IntakeError(f"{path}: cannot read UTF-8 JSON: {error}") from error
    return loads_strict(payload, label=str(path))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise IntakeError(message)


def _safe_relative_path(value: Any) -> bool:
    if not isinstance(value, str) or not value or value.strip() != value:
        return False
    path = Path(value)
    return (
        not path.is_absolute()
        and ":" not in value
        and "\\" not in value
        and ".." not in path.parts
    )


def validate_contract(contract: Any) -> dict[str, Any]:
    _require(isinstance(contract, dict), "intake contract must be an object")
    _require(set(contract) == CONTRACT_FIELDS, "intake contract fields drifted")
    _require(contract.get("schema_version") == "0.1", "unsupported contract schema")
    _require(
        contract.get("contract_id") == "untrusted-evidence-intake-v0",
        "contract_id drifted",
    )
    _require(
        contract.get("status") == "quarantined_untrusted_snapshot",
        "contract status must remain quarantined",
    )
    intake_id = contract.get("intake_id")
    source_directory = contract.get("source_directory")
    output_path = contract.get("output_path")
    _require(
        isinstance(intake_id, str) and re.fullmatch(r"[A-Z0-9-]+", intake_id) is not None,
        "intake_id is invalid",
    )
    _require(
        _safe_relative_path(source_directory)
        and source_directory == f"archive/untrusted_intake/{intake_id}",
        "source_directory must be the intake's quarantined archive path",
    )
    _require(
        _safe_relative_path(output_path)
        and output_path == f"data/untrusted_evidence_intake/{intake_id}.json",
        "output_path must be the intake's generated-data path",
    )
    sources = contract.get("sources")
    _require(isinstance(sources, list) and len(sources) == 3, "contract needs 3 sources")
    seen_paths: set[str] = set()
    for index, source in enumerate(sources):
        _require(isinstance(source, dict), f"sources[{index}] must be an object")
        _require(
            set(source) == SOURCE_FIELDS,
            f"sources[{index}] has invalid fields",
        )
        path = source["path"]
        digest = source["sha256"]
        blob_digest = source["git_blob_sha1"]
        _require(
            isinstance(path, str)
            and path not in seen_paths
            and Path(path).name == path
            and "/" not in path
            and "\\" not in path
            and path not in {".", ".."},
            f"sources[{index}].path is unsafe or duplicated",
        )
        seen_paths.add(path)
        _require(
            source["media_type"] in {"application/json", "text/markdown"},
            f"sources[{index}].media_type is unsupported",
        )
        _require(
            isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest) is not None,
            f"sources[{index}].sha256 is invalid",
        )
        _require(
            isinstance(blob_digest, str)
            and re.fullmatch(r"[0-9a-f]{40}", blob_digest) is not None,
            f"sources[{index}].git_blob_sha1 is invalid",
        )
    parsing = contract.get("parsing_contract")
    _require(
        parsing == PARSING_CONTRACT,
        "parsing_contract semantics drifted",
    )
    authority = contract.get("authority_ceiling")
    _require(isinstance(authority, dict), "authority_ceiling must be an object")
    _require(set(authority) == AUTHORITY_KEYS, "authority_ceiling fields drifted")
    _require(
        all(type(value) is int and value == 0 for value in authority.values()),
        "all authority ceilings must remain integer zero",
    )
    prohibited = contract.get("canonical_write_prohibited")
    _require(
        isinstance(prohibited, list)
        and len(prohibited) == len(set(prohibited))
        and set(prohibited) == CANONICAL_WRITE_PROHIBITED,
        "canonical_write_prohibited drifted",
    )
    required = contract.get("required_state")
    _require(isinstance(required, dict), "required_state must be an object")
    _require(set(required) == REQUIRED_STATE_FIELDS, "required_state fields drifted")
    _require(required.get("intake_status") == contract["status"], "status binding drifted")
    _require(required.get("join_status") == "not_present", "join must remain absent")
    _require(required.get("verified_join") is False, "verified_join must remain false")
    for key in (
        "safe_for_scientific_selection",
        "safe_for_calibration",
        "safe_for_authorization",
    ):
        _require(required.get(key) is False, f"{key} must remain false")
    observations = contract.get("expected_observations")
    _require(isinstance(observations, dict), "expected_observations must be an object")
    _require(
        set(observations) == EXPECTED_OBSERVATION_FIELDS,
        "expected_observations fields drifted",
    )
    _require(
        all(type(value) is int and value >= 0 for value in observations.values()),
        "expected observations must be non-negative integers",
    )
    receipt = contract.get("protected_main_receipt")
    _require(isinstance(receipt, dict), "protected_main_receipt must be an object")
    _require(
        set(receipt) == PROTECTED_RECEIPT_FIELDS,
        "protected_main_receipt fields drifted",
    )
    _require(
        receipt.get("mode") == "freeze_after_first_protected_main_acceptance",
        "protected_main_receipt mode drifted",
    )
    _require(
        receipt.get("protected_ref") == "origin/main",
        "protected_main_receipt ref must remain origin/main",
    )
    _require(
        receipt.get("contract_path")
        == "repo/UNTRUSTED_EVIDENCE_INTAKE_V0.json",
        "protected_main_receipt path drifted",
    )
    _require(
        receipt.get("frozen_fields") == list(PROTECTED_FROZEN_FIELDS),
        "protected_main_receipt frozen fields drifted",
    )
    _require(
        contract.get("regenerate")
        == "python3 scripts/build_untrusted_evidence_intake.py",
        "regenerate command drifted",
    )
    _require(
        contract.get("check")
        == "python3 scripts/build_untrusted_evidence_intake.py --check",
        "check command drifted",
    )
    _require(
        contract.get("test")
        == "python3 scripts/test_untrusted_evidence_intake.py",
        "test command drifted",
    )
    return contract


def _json_pointer_token(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def _type_parseable(value: str, declared_type: str) -> bool:
    if declared_type == "integer":
        return re.fullmatch(r"-?(0|[1-9][0-9]*)", value) is not None
    if declared_type == "boolean":
        return value.lower() in {"true", "false"}
    return declared_type in {"string", "unknown"}


def analyze_atlas(
    mechanisms: Any,
    properties: Any,
    report_bytes: bytes,
    *,
    tp_pattern: str,
) -> dict[str, Any]:
    _require(isinstance(mechanisms, list), "all_mechanisms.json must contain an array")
    _require(isinstance(properties, dict), "all_properties.json must contain an object")
    try:
        report_text = report_bytes.decode("utf-8")
    except UnicodeError as error:
        raise IntakeError(f"report is not UTF-8: {error}") from error
    reference_pattern = re.compile(tp_pattern)

    mechanism_ids: set[str] = set()
    mechanism_records: list[dict[str, Any]] = []
    requirement_records: list[dict[str, Any]] = []
    source_status_counts: Counter[str] = Counter()
    verdict_fields: list[str] = []
    for index, mechanism in enumerate(mechanisms):
        label = f"mechanisms[{index}]"
        _require(isinstance(mechanism, dict), f"{label} must be an object")
        _require(set(mechanism) == MECHANISM_FIELDS, f"{label} fields drifted")
        mechanism_id = mechanism.get("id")
        _require(
            isinstance(mechanism_id, str) and mechanism_id.strip(),
            f"{label}.id must be a nonempty string",
        )
        _require(mechanism_id not in mechanism_ids, f"duplicate mechanism id: {mechanism_id}")
        mechanism_ids.add(mechanism_id)
        for key in MECHANISM_FIELDS - {"requires"}:
            _require(isinstance(mechanism.get(key), str), f"{label}.{key} must be a string")
        status = mechanism["source_verified"]
        _require(status in SOURCE_STATUSES, f"{label}.source_verified is unsupported")
        source_status_counts[status] += 1
        requirements = mechanism.get("requires")
        _require(isinstance(requirements, list), f"{label}.requires must be an array")
        all_refs: list[str] = []
        for requirement_index, requirement in enumerate(requirements):
            _require(
                isinstance(requirement, str) and requirement.strip(),
                f"{label}.requires[{requirement_index}] must be a nonempty string",
            )
            refs = reference_pattern.findall(requirement)
            all_refs.extend(refs)
            requirement_records.append(
                {
                    "mechanism_id": mechanism_id,
                    "json_pointer": f"/{index}/requires/{requirement_index}",
                    "raw_sha256": sha256_bytes(requirement.encode("utf-8")),
                    "tp_like_references": refs,
                    "classification": "untrusted_free_text_requirement",
                }
            )
        if "verdict" in mechanism or "screen_matrix" in mechanism:
            verdict_fields.append(mechanism_id)
        mechanism_records.append(
            {
                "mechanism_id": mechanism_id,
                "json_pointer": f"/{index}",
                "canonical_record_sha256": sha256_json(mechanism),
                "source_status_annotation": status,
                "requirement_count": len(requirements),
                "tp_like_references": sorted(set(all_refs)),
                "classification": "untrusted_mechanism_envelope",
                "judgment_fields": [
                    "family",
                    "source",
                    "source_verified",
                    "requires",
                    "changed_quantity",
                    "growth_lever",
                ],
            }
        )

    property_records: list[dict[str, Any]] = []
    type_counts: Counter[str] = Counter()
    type_violations: list[dict[str, Any]] = []
    for key, prop in properties.items():
        label = f"properties[{key!r}]"
        _require(isinstance(key, str) and key.strip(), "property keys must be nonempty strings")
        _require(isinstance(prop, dict), f"{label} must be an object")
        _require(set(prop) == PROPERTY_FIELDS, f"{label} fields drifted")
        _require(prop.get("id") == key, f"{label}.id does not match its object key")
        for field in PROPERTY_FIELDS:
            _require(isinstance(prop.get(field), str), f"{label}.{field} must remain a raw string")
        declared_type = prop["value_type"]
        _require(declared_type in PROPERTY_TYPES, f"{label}.value_type is unsupported")
        type_counts[declared_type] += 1
        parseable = _type_parseable(prop["value"], declared_type)
        pointer = f"/{_json_pointer_token(key)}"
        if not parseable:
            type_violations.append(
                {
                    "property_id": key,
                    "json_pointer": f"{pointer}/value",
                    "declared_type": declared_type,
                    "raw_value": prop["value"],
                    "reason": "raw string is not a standalone lexical value of the declared type",
                }
            )
        property_records.append(
            {
                "property_id": key,
                "json_pointer": pointer,
                "canonical_record_sha256": sha256_json(prop),
                "declared_type": declared_type,
                "declared_type_parseable": parseable,
                "source_status_annotation": prop["status"],
                "classification": "untrusted_property_candidate",
            }
        )

    tp_requirement_records = [
        record for record in requirement_records if record["tp_like_references"]
    ]
    all_refs = [
        ref
        for record in requirement_records
        for ref in record["tp_like_references"]
    ]
    unique_refs = sorted(set(all_refs))
    orphan_refs = sorted(ref for ref in unique_refs if ref not in properties)
    resolved_occurrences = sum(1 for ref in all_refs if ref in properties)
    integer_violations = sum(
        item["declared_type"] == "integer" for item in type_violations
    )
    boolean_violations = sum(
        item["declared_type"] == "boolean" for item in type_violations
    )
    report_claim_match = re.search(
        r"прочитанные первоисточники\s*\((\d+)\s+из\s+35\s+механизмов",
        report_text,
    )
    report_claim = int(report_claim_match.group(1)) if report_claim_match else None

    observations = {
        "mechanisms": len(mechanism_records),
        "properties": len(property_records),
        "requirement_strings": len(requirement_records),
        "free_text_requirement_strings": len(requirement_records) - len(tp_requirement_records),
        "tp_like_requirement_strings": len(tp_requirement_records),
        "tp_like_reference_occurrences": len(all_refs),
        "unique_tp_like_references": len(unique_refs),
        "unique_orphan_tp_like_references": len(orphan_refs),
        "declared_integer_values": type_counts["integer"],
        "declared_boolean_values": type_counts["boolean"],
        "declared_integer_parse_violations": integer_violations,
        "declared_boolean_parse_violations": boolean_violations,
        "declared_type_parse_violations": len(type_violations),
        "mechanism_full_text_read_rows": source_status_counts["full_text_read"],
        "report_claimed_full_text_read_rows": report_claim,
        "verified_join_rows": 0,
    }
    return {
        "observations": observations,
        "mechanism_records": sorted(mechanism_records, key=lambda item: item["mechanism_id"]),
        "property_records": sorted(property_records, key=lambda item: item["property_id"]),
        "requirement_records": requirement_records,
        "type_violations": sorted(type_violations, key=lambda item: item["property_id"]),
        "unique_tp_like_references": unique_refs,
        "unique_orphan_tp_like_references": orphan_refs,
        "resolved_tp_like_reference_occurrences": resolved_occurrences,
        "source_status_counts": dict(sorted(source_status_counts.items())),
        "unexpected_verdict_fields": verdict_fields,
        "report": {
            "bytes": len(report_bytes),
            "lines": len(report_text.splitlines()),
            "claimed_full_text_read_rows": report_claim,
        },
    }


def build_state(contract: dict[str, Any], *, root: Path = ROOT) -> dict[str, Any]:
    validate_contract(contract)
    validate_protected_main_receipt(contract, root=root)
    consumer_references = scan_forbidden_consumers(root=root, contract=contract)
    _require(
        not consumer_references,
        "quarantine referenced by prohibited consumer: "
        + ", ".join(consumer_references),
    )
    source_dir = root / contract["source_directory"]
    source_artifacts: list[dict[str, Any]] = []
    payloads: dict[str, bytes] = {}
    for source in contract["sources"]:
        relative = source["path"]
        path = source_dir / relative
        _require(path.is_file(), f"missing source artifact: {path}")
        payload = path.read_bytes()
        digest = sha256_bytes(payload)
        _require(digest == source["sha256"], f"source hash mismatch: {relative}")
        blob_digest = git_blob_sha1(payload)
        _require(
            blob_digest == source["git_blob_sha1"],
            f"source Git blob hash mismatch: {relative}",
        )
        payloads[relative] = payload
        source_artifacts.append(
            {
                "path": f"{contract['source_directory']}/{relative}",
                "media_type": source["media_type"],
                "sha256": digest,
                "git_blob_sha1": blob_digest,
                "bytes": len(payload),
            }
        )
    mechanisms = loads_strict(
        payloads["all_mechanisms.json"].decode("utf-8"),
        label="all_mechanisms.json",
    )
    properties = loads_strict(
        payloads["all_properties.json"].decode("utf-8"),
        label="all_properties.json",
    )
    analysis = analyze_atlas(
        mechanisms,
        properties,
        payloads["ECDLP_SCREEN_ATLAS_REPORT.md"],
        tp_pattern=contract["parsing_contract"]["tp_like_reference_pattern"],
    )
    _require(
        analysis["observations"] == contract["expected_observations"],
        "observed atlas counts drifted from the reviewed snapshot",
    )
    _require(
        not analysis["unexpected_verdict_fields"],
        "source unexpectedly contains machine verdict or screen-matrix fields",
    )
    _require(
        analysis["resolved_tp_like_reference_occurrences"] == 0,
        "snapshot unexpectedly resolves a TP-like requirement reference",
    )
    required = contract["required_state"]
    return {
        "schema_version": "0.1-generated",
        "intake_id": contract["intake_id"],
        "intake_status": required["intake_status"],
        "source_assurance": "untrusted_external_snapshot",
        "source_artifacts": source_artifacts,
        "source_set_sha256": sha256_json(source_artifacts),
        "observations": analysis["observations"],
        "join_assessment": {
            "join_status": required["join_status"],
            "verified_join": required["verified_join"],
            "reason": (
                "Only 12 of 122 requirement strings contain TP-like references; "
                "all six unique references are orphaned, and the source has no "
                "machine-readable verdict matrix."
            ),
            "resolved_reference_occurrences": analysis[
                "resolved_tp_like_reference_occurrences"
            ],
            "unique_orphan_references": analysis["unique_orphan_tp_like_references"],
            "screen_matrix_present": False,
            "verdict_field_present": False,
        },
        "source_read_status_assessment": {
            "source_authored_counts": analysis["source_status_counts"],
            "report_claimed_full_text_read_rows": analysis["report"][
                "claimed_full_text_read_rows"
            ],
            "mechanism_rows_marked_full_text_read": analysis["source_status_counts"].get(
                "full_text_read", 0
            ),
            "artifact_bound_primary_reading_verified": 0,
            "boundary": (
                "The source_verified field is retained as an untrusted annotation; "
                "it is not upgraded to source assurance."
            ),
        },
        "validation_findings": {
            "declared_type_parse_violations": analysis["type_violations"],
            "orphan_tp_like_references": analysis["unique_orphan_tp_like_references"],
            "unsupported_coercions_performed": 0,
        },
        "authority": dict(contract["authority_ceiling"]),
        "safety": {
            "safe_for_scientific_selection": required["safe_for_scientific_selection"],
            "safe_for_calibration": required["safe_for_calibration"],
            "safe_for_authorization": required["safe_for_authorization"],
            "canonical_write_prohibited": contract["canonical_write_prohibited"],
            "negative_dependency_scan": {
                "status": "passed",
                "prohibited_consumer_references": consumer_references,
                "scan_roots": list(QUARANTINE_REFERENCE_SCAN_ROOTS),
                "scan_suffixes": sorted(QUARANTINE_REFERENCE_SCAN_SUFFIXES),
                "reference_tokens": sorted(quarantine_reference_tokens(contract)),
                "boundary": (
                    "This is a repository-wide lexical path guard over executable "
                    "and configuration files, not a proof of information-flow "
                    "noninterference."
                ),
            },
            "boundary": (
                "Every mechanism, property, requirement, heat label, source status, "
                "and conclusion remains an untrusted annotation pending a separate "
                "producer, independent replay, and canonical review."
            ),
        },
        "mechanism_envelopes": analysis["mechanism_records"],
        "property_candidates": analysis["property_records"],
        "requirement_annotations": analysis["requirement_records"],
        "report_envelope": analysis["report"],
        "canonical_import_plan": {
            "direct_imports": 0,
            "scientific_outcomes": 0,
            "ranker_labels": 0,
            "route_closures": 0,
            "authorization": 0,
            "next_step": (
                "Replay individual public properties or extract claim-level source "
                "anchors in separate reviewed work; never bulk-promote this snapshot."
            ),
        },
    }


def validation_problems(state: Any, contract: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    if not isinstance(state, dict):
        return ["generated intake must be an object"]
    if state.get("intake_id") != contract.get("intake_id"):
        problems.append("intake_id drifted")
    if state.get("intake_status") != "quarantined_untrusted_snapshot":
        problems.append("intake is not quarantined")
    if state.get("authority") != contract.get("authority_ceiling"):
        problems.append("authority ceiling drifted")
    authority = state.get("authority", {})
    if not isinstance(authority, dict) or any(
        type(value) is not int or value != 0 for value in authority.values()
    ):
        problems.append("untrusted intake acquired nonzero authority")
    artifacts = state.get("source_artifacts")
    expected_sources = {
        f"{contract['source_directory']}/{item['path']}": item
        for item in contract["sources"]
    }
    if not isinstance(artifacts, list) or len(artifacts) != len(expected_sources):
        problems.append("source artifact set drifted")
    else:
        for artifact in artifacts:
            expected = expected_sources.get(artifact.get("path")) if isinstance(artifact, dict) else None
            if (
                expected is None
                or artifact.get("sha256") != expected["sha256"]
                or artifact.get("git_blob_sha1") != expected["git_blob_sha1"]
                or artifact.get("media_type") != expected["media_type"]
                or type(artifact.get("bytes")) is not int
                or artifact["bytes"] <= 0
            ):
                problems.append("source artifact binding drifted")
                break
        if state.get("source_set_sha256") != sha256_json(artifacts):
            problems.append("source artifact set digest drifted")
    join = state.get("join_assessment", {})
    if join.get("join_status") != "not_present" or join.get("verified_join") is not False:
        problems.append("untrusted atlas was treated as a verified join")
    if join.get("resolved_reference_occurrences") != 0:
        problems.append("untrusted atlas claims resolved typed requirements")
    safety = state.get("safety", {})
    for key in (
        "safe_for_scientific_selection",
        "safe_for_calibration",
        "safe_for_authorization",
    ):
        if safety.get(key) is not False:
            problems.append(f"{key} must remain false")
    dependency_scan = safety.get("negative_dependency_scan", {})
    if (
        dependency_scan.get("status") != "passed"
        or dependency_scan.get("prohibited_consumer_references") != []
        or dependency_scan.get("scan_roots")
        != list(QUARANTINE_REFERENCE_SCAN_ROOTS)
        or dependency_scan.get("scan_suffixes")
        != sorted(QUARANTINE_REFERENCE_SCAN_SUFFIXES)
        or dependency_scan.get("reference_tokens")
        != sorted(quarantine_reference_tokens(contract))
    ):
        problems.append("negative dependency scan drifted")
    if state.get("observations") != contract.get("expected_observations"):
        problems.append("reviewed observations drifted")
    plan = state.get("canonical_import_plan", {})
    for key in (
        "direct_imports",
        "scientific_outcomes",
        "ranker_labels",
        "route_closures",
        "authorization",
    ):
        if type(plan.get(key)) is not int or plan.get(key) != 0:
            problems.append(f"canonical_import_plan.{key} must remain zero")
    return problems


def render(state: dict[str, Any]) -> str:
    return json.dumps(state, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def main() -> int:
    try:
        contract = validate_contract(load_json_strict(CONTRACT_PATH))
        state = build_state(contract)
        problems = validation_problems(state, contract)
        if problems:
            raise IntakeError("; ".join(problems))
        output_path = ROOT / contract["output_path"]
        expected = render(state)
        if "--check" in sys.argv:
            if not output_path.is_file():
                raise IntakeError(f"generated intake is missing: {output_path}")
            actual = output_path.read_text(encoding="utf-8")
            if actual != expected:
                raise IntakeError(
                    "generated intake is stale; run scripts/build_untrusted_evidence_intake.py"
                )
            print(
                "untrusted atlas intake passed: "
                f"{state['observations']['mechanisms']} mechanisms, "
                f"{state['observations']['properties']} properties, "
                "0 canonical imports, 0 scientific outcomes, 0 authorization."
            )
            return 0
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(expected, encoding="utf-8", newline="\n")
        print(f"wrote {output_path.relative_to(ROOT)}")
        return 0
    except (IntakeError, OSError, UnicodeError, KeyError, TypeError) as error:
        print(f"untrusted atlas intake FAILED: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
