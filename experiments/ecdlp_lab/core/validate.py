"""One-command offline validation for the P01 lab contract boundary."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from typing import Any, Sequence

from .canonical import (
    StrictJSONError,
    canonical_json_bytes,
    load_json,
    is_sha256,
    sha256_file,
    sha256_json,
    strict_loads,
)
from .contracts import (
    PRIMARY_ID_FIELDS,
    ValidationContext,
    validate_contract,
    validate_cross_record_bundle,
)
from .issues import Issue
from .paths import PathSafetyError, resolve_artifact_path
from .safety import CONTRACT_KINDS
from .schema import schema_definition_issues, validate_schema

LAB_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = LAB_ROOT.parents[1]
SCHEMA_ROOT = LAB_ROOT / "contracts"
FIXTURE_ROOT = LAB_ROOT / "fixtures" / "contracts"
VALID_MANIFEST = FIXTURE_ROOT / "valid_manifest_v1.json"
INVALID_MANIFEST = FIXTURE_ROOT / "invalid_cases_v1.json"
REUSE_INVENTORY = REPO_ROOT / "tasks" / "ECDLP_LAB_REUSE_INVENTORY.json"
LEGACY_CATALOG_ID = "p1_curve_catalog"
LEGACY_CATALOG_PATH = (
    "experiments/ml_structure_probe/reports/p1_toy_scaling/curve_catalog.json"
)

SEMANTIC_CASE_CODES = {
    "self_validation": "contract.validation.self_validator",
    "external_target_point": "contract.method_request.target_binding",
    "unknown_catalog_digest": "contract.catalog.unknown",
    "unknown_vector_digest": "contract.target_vector.unknown",
    "symlink_escape": "contract.artifact.path",
}


def _problem(code: str, path: str, message: str) -> Issue:
    return Issue(f"offline.{code}", path, message)


def _parts(pointer: str) -> list[str]:
    if pointer in ("", "/"):
        return []
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise ValueError(f"invalid JSON pointer: {pointer!r}")
    return [
        part.replace("~1", "/").replace("~0", "~")
        for part in pointer[1:].split("/")
    ]


def _lookup(document: Any, pointer: str) -> Any:
    current = document
    for part in _parts(pointer):
        current = current[int(part)] if isinstance(current, list) else current[part]
    return current


def _assign(document: Any, pointer: str, value: Any) -> None:
    parts = _parts(pointer)
    if not parts:
        if not isinstance(document, dict) or not isinstance(value, dict):
            raise ValueError("root mutation requires object merge")
        document.update(value)
        return
    parent = document
    for part in parts[:-1]:
        parent = parent[int(part)] if isinstance(parent, list) else parent[part]
    if isinstance(parent, list):
        parent[int(parts[-1])] = value
    else:
        parent[parts[-1]] = value


def _mutate(document: dict[str, Any], mutation: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(document)
    operation = mutation.get("operation")
    pointer = mutation.get("pointer")
    if operation in {"add", "replace"}:
        _assign(result, pointer, mutation.get("value"))
    elif operation == "replace_many":
        target = _lookup(result, pointer)
        value = mutation.get("value")
        if not isinstance(target, dict) or not isinstance(value, dict):
            raise ValueError("replace_many requires object target and value")
        target.update(value)
    elif operation == "copy":
        source = mutation.get("value")
        _assign(result, pointer, deepcopy(_lookup(result, source)))
    elif operation == "remove":
        parts = _parts(pointer)
        if not parts:
            raise ValueError("cannot remove the fixture root")
        parent: Any = result
        for part in parts[:-1]:
            parent = parent[int(part)] if isinstance(parent, list) else parent[part]
        if isinstance(parent, list):
            del parent[int(parts[-1])]
        else:
            del parent[parts[-1]]
    else:
        raise ValueError(f"unsupported pure mutation operation: {operation!r}")
    return result


def _load_valid_bundle() -> tuple[list[dict[str, Any]], dict[str, str], list[Issue]]:
    issues: list[Issue] = []
    try:
        manifest = load_json(VALID_MANIFEST)
    except (OSError, ValueError) as error:
        return [], {}, [_problem("manifest", str(VALID_MANIFEST), str(error))]
    if not isinstance(manifest, dict) or not isinstance(manifest.get("records"), list):
        return [], {}, [
            _problem("manifest", str(VALID_MANIFEST), "records must be an array")
        ]

    records: list[dict[str, Any]] = []
    hashes: dict[str, str] = {}
    for index, row in enumerate(manifest["records"]):
        path_label = f"{VALID_MANIFEST}:records[{index}]"
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            issues.append(_problem("manifest.row", path_label, "invalid record row"))
            continue
        try:
            path = resolve_artifact_path(REPO_ROOT, row["path"], must_exist=True)
            record = load_json(path)
        except (OSError, ValueError, PathSafetyError) as error:
            issues.append(_problem("fixture.load", path_label, str(error)))
            continue
        if not isinstance(record, dict):
            issues.append(_problem("fixture.type", str(path), "record is not an object"))
            continue
        if row.get("contract_kind") != record.get("contract_kind"):
            issues.append(
                _problem(
                    "fixture.kind",
                    str(path),
                    "manifest contract_kind differs from record",
                )
            )
        canonical = canonical_json_bytes(record)
        if canonical_json_bytes(strict_loads(canonical)) != canonical:
            issues.append(_problem("fixture.fixpoint", str(path), "canonical drift"))
        records.append(record)
        kind = record.get("contract_kind")
        primary_field = PRIMARY_ID_FIELDS.get(kind)
        primary = record.get(primary_field) if primary_field is not None else None
        if isinstance(primary, str):
            hashes[primary] = sha256_file(path)
    return records, hashes, issues


def _schema_issues() -> tuple[dict[str, dict[str, Any]], list[Issue]]:
    schemas: dict[str, dict[str, Any]] = {}
    issues: list[Issue] = []
    actual = {
        path.name.removesuffix(".schema.json"): path
        for path in SCHEMA_ROOT.glob("*_v1.schema.json")
    }
    if set(actual) != set(CONTRACT_KINDS):
        issues.append(
            _problem(
                "schema.corpus",
                str(SCHEMA_ROOT),
                f"expected {sorted(CONTRACT_KINDS)!r}, found {sorted(actual)!r}",
            )
        )
    for kind, path in sorted(actual.items()):
        try:
            schema = load_json(path)
        except (OSError, ValueError) as error:
            issues.append(_problem("schema.load", str(path), str(error)))
            continue
        if not isinstance(schema, dict):
            issues.append(_problem("schema.type", str(path), "schema is not an object"))
            continue
        schemas[kind] = schema
        for issue in schema_definition_issues(schema):
            issues.append(
                _problem("schema.definition", f"{path}:{issue.path}", str(issue))
            )
    return schemas, issues


def _trusted_catalog_sha256s() -> tuple[frozenset[str], list[Issue]]:
    """Load and verify the one P01 catalog authority from the frozen inventory."""

    try:
        inventory = load_json(REUSE_INVENTORY)
    except (OSError, ValueError) as error:
        return frozenset(), [
            _problem("inventory.load", str(REUSE_INVENTORY), str(error))
        ]
    if (
        not isinstance(inventory, dict)
        or inventory.get("inventory_id") != "ECDLP-LAB-REUSE-INVENTORY-V1"
        or not isinstance(inventory.get("entries"), list)
    ):
        return frozenset(), [
            _problem("inventory.shape", str(REUSE_INVENTORY), "unexpected inventory")
        ]
    matches = [
        row
        for row in inventory["entries"]
        if isinstance(row, dict) and row.get("id") == LEGACY_CATALOG_ID
    ]
    if len(matches) != 1:
        return frozenset(), [
            _problem(
                "inventory.catalog",
                str(REUSE_INVENTORY),
                "expected exactly one frozen P1 catalog entry",
            )
        ]
    row = matches[0]
    digest = row.get("sha256")
    if row.get("path") != LEGACY_CATALOG_PATH or not is_sha256(digest):
        return frozenset(), [
            _problem(
                "inventory.catalog",
                str(REUSE_INVENTORY),
                "frozen P1 catalog path/digest declaration drifted",
            )
        ]
    try:
        path = resolve_artifact_path(REPO_ROOT, LEGACY_CATALOG_PATH, must_exist=True)
        actual = sha256_file(path)
    except (OSError, ValueError, PathSafetyError) as error:
        return frozenset(), [
            _problem("inventory.catalog", LEGACY_CATALOG_PATH, str(error))
        ]
    if actual != digest:
        return frozenset(), [
            _problem(
                "inventory.catalog_hash",
                LEGACY_CATALOG_PATH,
                "catalog bytes differ from the frozen P00 inventory",
            )
        ]
    return frozenset({digest}), []


def _symlink_case(
    base: dict[str, Any], mutation: dict[str, Any], context: ValidationContext
) -> list[Issue]:
    mutated = deepcopy(base)
    _assign(mutated, mutation["pointer"], mutation["value"])
    try:
        with tempfile.TemporaryDirectory() as root_name, tempfile.TemporaryDirectory() as outside_name:
            root = Path(root_name)
            link = (
                root
                / "experiments"
                / "ecdlp_lab"
                / "fixtures"
                / "contracts"
                / "link"
            )
            link.parent.mkdir(parents=True)
            link.symlink_to(Path(outside_name), target_is_directory=True)
            return validate_contract(
                mutated,
                replace(context, repo_root=root, verify_artifacts=True),
            )
    except (NotImplementedError, OSError) as error:
        return [
            _problem(
                "adversarial.symlink_unavailable",
                "symlink_escape",
                f"cannot execute required symlink adversary: {error}",
            )
        ]


def _adversarial_issues(
    schemas: dict[str, dict[str, Any]], context: ValidationContext
) -> tuple[int, list[Issue]]:
    failures: list[Issue] = []
    try:
        manifest = load_json(INVALID_MANIFEST)
    except (OSError, ValueError) as error:
        return 0, [_problem("adversarial.manifest", str(INVALID_MANIFEST), str(error))]
    cases = manifest.get("cases") if isinstance(manifest, dict) else None
    if not isinstance(cases, list):
        return 0, [
            _problem("adversarial.manifest", str(INVALID_MANIFEST), "cases must be an array")
        ]

    semantic_context = replace(context, verify_artifacts=False)
    seen: set[str] = set()
    for index, case in enumerate(cases):
        label = f"{INVALID_MANIFEST}:cases[{index}]"
        if not isinstance(case, dict) or not isinstance(case.get("case_id"), str):
            failures.append(_problem("adversarial.case", label, "invalid case object"))
            continue
        case_id = case["case_id"]
        if case_id in seen:
            failures.append(_problem("adversarial.duplicate", label, case_id))
        seen.add(case_id)
        mutation = case.get("mutation")
        if not isinstance(mutation, dict):
            failures.append(_problem("adversarial.mutation", label, "missing mutation"))
            continue
        operation = mutation.get("operation")
        if operation == "parse_raw_json":
            try:
                strict_loads(mutation.get("value"), label=case_id)
            except StrictJSONError:
                continue
            failures.append(
                _problem("adversarial.accepted", case_id, "strict parser accepted adversary")
            )
            continue

        base_path = case.get("base_fixture")
        kind = case.get("contract_kind")
        if not isinstance(base_path, str) or kind not in schemas:
            failures.append(_problem("adversarial.base", case_id, "invalid base/schema"))
            continue
        try:
            base = load_json(resolve_artifact_path(REPO_ROOT, base_path, must_exist=True))
        except (OSError, ValueError, PathSafetyError) as error:
            failures.append(_problem("adversarial.base", case_id, str(error)))
            continue
        if not isinstance(base, dict):
            failures.append(_problem("adversarial.base", case_id, "base is not an object"))
            continue
        if validate_contract(base, semantic_context):
            failures.append(
                _problem("adversarial.base_invalid", case_id, "base fixture is not valid")
            )
            continue

        if operation == "ephemeral_symlink_escape":
            contract_issues = _symlink_case(base, mutation, semantic_context)
            expected_code = SEMANTIC_CASE_CODES.get(case_id)
            if expected_code not in {issue.code for issue in contract_issues}:
                failures.append(
                    _problem(
                        "adversarial.accepted",
                        case_id,
                        f"missing expected semantic issue {expected_code!r}",
                    )
                )
            continue
        try:
            mutated = _mutate(base, mutation)
        except (KeyError, TypeError, ValueError, IndexError) as error:
            failures.append(_problem("adversarial.mutation", case_id, str(error)))
            continue
        schema_result = validate_schema(mutated, schemas[kind])
        contract_result = validate_contract(mutated, semantic_context)
        stage = case.get("expected_stage")
        if stage == "schema" and not schema_result:
            failures.append(
                _problem("adversarial.accepted", case_id, "schema accepted mutation")
            )
        elif stage == "schema_or_semantic" and not (schema_result or contract_result):
            failures.append(
                _problem("adversarial.accepted", case_id, "all validators accepted mutation")
            )
        elif stage == "semantic":
            expected_code = SEMANTIC_CASE_CODES.get(case_id)
            codes = {issue.code for issue in contract_result}
            if expected_code is None or expected_code not in codes:
                failures.append(
                    _problem(
                        "adversarial.accepted",
                        case_id,
                        f"missing expected semantic issue {expected_code!r}; got {sorted(codes)!r}",
                    )
                )
        elif stage not in {"schema", "schema_or_semantic", "semantic"}:
            failures.append(_problem("adversarial.stage", case_id, repr(stage)))
    return len(cases), failures


def validate_offline() -> tuple[dict[str, int], list[Issue]]:
    """Run every dependency-free P01 validation and return a stable report."""

    schemas, issues = _schema_issues()
    records, record_hashes, fixture_issues = _load_valid_bundle()
    issues.extend(fixture_issues)
    trusted_catalogs, inventory_issues = _trusted_catalog_sha256s()
    issues.extend(inventory_issues)
    trusted_targets = frozenset(
        record["target_vector_id"]
        for record in records
        if record.get("contract_kind") == "target_vector_v1"
        and record.get("branch") == "public"
        and isinstance(record.get("target_vector_id"), str)
        and isinstance(record.get("public_payload"), dict)
        and record.get("target_vector_id") == sha256_json(record["public_payload"])
    )
    if not trusted_targets:
        issues.append(
            _problem(
                "manifest.target",
                str(VALID_MANIFEST),
                "trusted manifest contains no public target vector",
            )
        )
    context = ValidationContext.from_records(
        records,
        repo_root=REPO_ROOT,
        schema_root=SCHEMA_ROOT,
        known_catalog_sha256s=trusted_catalogs,
        known_target_vector_sha256s=trusted_targets,
        record_sha256s_by_id=record_hashes,
        verify_artifacts=True,
    )
    if schemas:
        for record in records:
            issues.extend(validate_contract(record, context))
        issues.extend(validate_cross_record_bundle(records, context))
    adversarial_count, adversarial = _adversarial_issues(schemas, context)
    issues.extend(adversarial)
    summary = {
        "schemas": len(schemas),
        "valid_records": len(records),
        "adversarial_cases": adversarial_count,
        "issues": len(set(issues)),
    }
    return summary, sorted(set(issues))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate ECDLP lab P01 offline.")
    parser.add_argument(
        "--offline",
        action="store_true",
        help="run only dependency-free local contract checks",
    )
    parser.add_argument("--json", action="store_true", help="emit compact JSON")
    args = parser.parse_args(argv)
    if not args.offline:
        parser.error("--offline is required; no implicit backend execution is allowed")
    summary, issues = validate_offline()
    if args.json:
        payload = {
            "schema_version": 1,
            "report_kind": "ecdlp_lab_offline_validation",
            "passed": not issues,
            "summary": summary,
            "issues": [
                {"code": issue.code, "path": issue.path, "message": issue.message}
                for issue in issues
            ],
        }
        print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    elif issues:
        print("ECDLP lab offline validation FAILED:", file=sys.stderr)
        for issue in issues:
            print(f"- {issue}", file=sys.stderr)
    else:
        print(
            "ECDLP lab offline validation OK: "
            f"{summary['schemas']} schemas, {summary['valid_records']} valid records, "
            f"{summary['adversarial_cases']} adversarial cases"
        )
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
