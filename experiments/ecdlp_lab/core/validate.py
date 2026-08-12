"""One-command offline validation for the ECDLP lab contract boundary."""

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
    sha256_file,
    sha256_json,
    strict_loads,
)
from .catalog_registry import (
    CI_CATALOG_ID,
    LEGACY_CATALOG_ID,
    CatalogAuthority,
    CatalogRegistryError,
    load_catalog_registry,
    resolve_curve_fixture,
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


def _catalog_authorities() -> tuple[tuple[CatalogAuthority, ...], list[Issue]]:
    """Return entries only after the complete P02 registry verifies."""

    try:
        return load_catalog_registry(repo_root=REPO_ROOT), []
    except (CatalogRegistryError, OSError, TypeError, ValueError) as error:
        return (), [
            _problem("catalog_registry", str(REPO_ROOT), str(error))
        ]


def _trusted_catalog_sha256s() -> tuple[frozenset[str], list[Issue]]:
    """Compatibility helper returning only fully verified raw digests."""

    authorities, issues = _catalog_authorities()
    return frozenset(authority.sha256 for authority in authorities), issues


def _catalog_result_issues(
    authority: CatalogAuthority, result: Any
) -> list[Issue]:
    issues: list[Issue] = []
    result_issues = getattr(result, "issues", None)
    if not isinstance(result_issues, tuple) or any(
        not isinstance(issue, Issue) for issue in result_issues
    ):
        return [
            _problem(
                "catalog_validator.shape",
                authority.path,
                "validator issues must be a tuple of Issue values",
            )
        ]
    issues.extend(result_issues)
    if getattr(result, "passed", None) is not True:
        issues.append(
            _problem(
                "catalog_validator.failed",
                authority.path,
                "independent catalog validation did not pass",
            )
        )
    if getattr(result, "catalog_sha256", None) != authority.sha256:
        issues.append(
            _problem(
                "catalog_validator.digest",
                authority.path,
                "validator result does not bind the registry-authorized raw digest",
            )
        )
    fixture_count = getattr(result, "fixture_count", None)
    if type(fixture_count) is not int or fixture_count != authority.curve_count:
        issues.append(
            _problem(
                "catalog_validator.count",
                authority.path,
                "validator fixture count differs from registry authority",
            )
        )
    fixture_results = getattr(result, "fixture_results", None)
    if not isinstance(fixture_results, tuple) or len(fixture_results) != authority.curve_count:
        issues.append(
            _problem(
                "catalog_validator.results",
                authority.path,
                "validator must return one immutable result per curve fixture",
            )
        )
    if getattr(result, "passed", None) is True and result_issues:
        issues.append(
            _problem(
                "catalog_validator.contradiction",
                authority.path,
                "validator cannot pass while reporting issues",
            )
        )
    return issues


def _catalog_schema_issues(authority: CatalogAuthority) -> list[Issue]:
    schema_location = "experiments/ecdlp_lab/curves/catalog_schema.json"
    try:
        schema_path = resolve_artifact_path(
            REPO_ROOT, schema_location, must_exist=True
        )
        schema = load_json(schema_path)
        catalog = load_json(authority.resolved_path)
    except (OSError, PathSafetyError, TypeError, ValueError) as error:
        return [_problem("catalog_schema.load", schema_location, str(error))]
    if not isinstance(schema, dict):
        return [_problem("catalog_schema.type", schema_location, "schema is not an object")]
    issues = [
        _problem(
            "catalog_schema.definition",
            f"{schema_location}:{issue.path}",
            str(issue),
        )
        for issue in schema_definition_issues(schema)
    ]
    issues.extend(
        _problem(
            "catalog_schema.validation",
            f"{authority.path}:{issue.path}",
            str(issue),
        )
        for issue in validate_schema(catalog, schema)
    )
    return issues


def _registered_catalog_issues(
    authorities: tuple[CatalogAuthority, ...],
) -> list[Issue]:
    """Exercise generation, legacy projection, and independent validation."""

    if not authorities:
        return []
    by_id = {authority.catalog_id: authority for authority in authorities}
    if set(by_id) != {CI_CATALOG_ID, LEGACY_CATALOG_ID}:
        return [
            _problem(
                "catalog_registry.coverage",
                str(REPO_ROOT),
                "verified registry lacks the exact CI/legacy authority pair",
            )
        ]
    try:
        from experiments.ecdlp_lab.curves.generate_ci_catalog import (
            check_committed_catalog,
        )
        from experiments.ecdlp_lab.curves.p1_adapter import load_legacy_catalog
        from experiments.ecdlp_lab.curves.validate_catalog import (
            validate_catalog_bytes,
            validate_legacy_catalog_bytes,
        )
    except ImportError as error:
        return [
            _problem(
                "catalog_validator.import",
                str(LAB_ROOT / "curves"),
                str(error),
            )
        ]

    issues: list[Issue] = []
    ci_authority = by_id[CI_CATALOG_ID]
    legacy_authority = by_id[LEGACY_CATALOG_ID]
    issues.extend(_catalog_schema_issues(ci_authority))
    try:
        generated_ok, generated_detail = check_committed_catalog()
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        issues.append(_problem("catalog_fixpoint", ci_authority.path, str(error)))
    else:
        if not generated_ok:
            issues.append(
                _problem("catalog_fixpoint", ci_authority.path, generated_detail)
            )
        elif generated_detail != ci_authority.sha256:
            issues.append(
                _problem(
                    "catalog_fixpoint.digest",
                    ci_authority.path,
                    "fresh generation digest differs from registry authority",
                )
            )

    try:
        ci_raw = ci_authority.resolved_path.read_bytes()
        ci_result = validate_catalog_bytes(
            ci_raw,
            expected_spec_sha256=ci_authority.spec_sha256,
            exact_count_authorized=True,
        )
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        issues.append(_problem("catalog_validator.ci", ci_authority.path, str(error)))
    else:
        issues.extend(_catalog_result_issues(ci_authority, ci_result))

    try:
        legacy_raw = legacy_authority.resolved_path.read_bytes()
        legacy = load_legacy_catalog(
            catalog_path=legacy_authority.path,
            catalog_sha256=legacy_authority.sha256,
            repo_root=REPO_ROOT,
        )
        if legacy.raw_sha256 != legacy_authority.sha256:
            raise ValueError("legacy projection lost its raw registry binding")
        if len(legacy.curves) != legacy_authority.curve_count:
            raise ValueError("legacy projection curve count drifted")
        legacy_result = validate_legacy_catalog_bytes(
            legacy_raw,
            expected_catalog_sha256=legacy_authority.sha256,
        )
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        issues.append(
            _problem("catalog_validator.legacy", legacy_authority.path, str(error))
        )
    else:
        issues.extend(_catalog_result_issues(legacy_authority, legacy_result))
    return issues


def _p03_replay_issues() -> list[Issue]:
    """Execute all authenticated P1 rows through the neutral P03 methods.

    Replay secrets remain inside ``LegacyReplayCase.validator_only``.  The
    method sees only a newly constructed ``PublicMethodInput``; candidate
    verification happens afterwards through the independent framework oracle.
    """

    try:
        from experiments.ecdlp_lab.methods.python.dispatch import run_method
        from experiments.ecdlp_lab.methods.python.model import (
            MethodBudgets,
            PublicMethodInput,
            SolverOutcome,
        )

        from .candidate_validation import ValidatorCounters, validate_candidate
        from .legacy_solver_replay import (
            LOCATOR_RAW_SHA256,
            LOCATOR_SEMANTIC_SHA256,
            LegacyReplayError,
            load_legacy_replay,
            validate_legacy_replay,
        )
    except ImportError as error:
        return [_problem("p03.import", str(LAB_ROOT), str(error))]

    try:
        report = validate_legacy_replay(repo_root=REPO_ROOT)
        cases = load_legacy_replay(repo_root=REPO_ROOT)
    except (LegacyReplayError, OSError, RuntimeError, TypeError, ValueError) as error:
        return [_problem("p03.authority", str(REPO_ROOT), str(error))]

    issues: list[Issue] = []
    report_issues = getattr(report, "issues", None)
    if not isinstance(report_issues, tuple) or any(
        not isinstance(issue, Issue) for issue in report_issues
    ):
        return [
            _problem(
                "p03.report.shape",
                "$.p03_replay.issues",
                "replay issues must be an immutable tuple of Issue values",
            )
        ]
    issues.extend(report_issues)
    expected_report_values = {
        "passed": True,
        "fixture_kind": "legacy_p1_solver_replay_locator_v1",
        "locator_raw_sha256": LOCATOR_RAW_SHA256,
        "locator_semantic_sha256": LOCATOR_SEMANTIC_SHA256,
        "case_count": 64,
        "success_count": 64,
        "bsgs_case_count": 32,
        "rho_case_count": 32,
        "schema_only_quarantine_verified": True,
    }
    for name, expected in expected_report_values.items():
        actual = getattr(report, name, None)
        if type(actual) is not type(expected) or actual != expected:
            issues.append(
                _problem(
                    "p03.report.anchor",
                    f"$.p03_replay.{name}",
                    f"expected {expected!r}, got {actual!r}",
                )
            )
    if report.passed is True and report_issues:
        issues.append(
            _problem(
                "p03.report.contradiction",
                "$.p03_replay",
                "a passing replay report cannot contain issues",
            )
        )
    if not isinstance(cases, tuple) or len(cases) != 64:
        issues.append(
            _problem(
                "p03.cases",
                "$.p03_replay.cases",
                "loader must return exactly 64 immutable replay cases",
            )
        )
    if issues:
        return sorted(set(issues))

    case_ids = [getattr(case, "case_id", None) for case in cases]
    if any(not isinstance(case_id, str) or not case_id for case_id in case_ids):
        return [
            _problem(
                "p03.case_id",
                "$.p03_replay.cases",
                "every replay case requires a non-empty public identity",
            )
        ]
    if len(set(case_ids)) != len(case_ids):
        return [
            _problem(
                "p03.case_id",
                "$.p03_replay.cases",
                "replay case identities must be unique",
            )
        ]

    budgets = MethodBudgets(
        max_subgroup_order_bits=32,
        max_field_bits=32,
        max_group_law_invocations=1_000_000,
        max_table_entries=65_536,
        max_steps=1_000_000,
        timeout_ns=5_000_000_000,
        max_memory_bytes=64 * 1024 * 1024,
        workers=1,
    )
    resolved_fixtures: dict[tuple[str, str], Any] = {}
    outcomes: list[tuple[Any, Any]] = []
    validator_group_law_invocations = 0
    for case in cases:
        case_path = f"$.p03_replay.cases[{case.case_id}]"
        try:
            replay_input = case.to_public_input()
        except (AttributeError, RuntimeError, TypeError, ValueError) as error:
            issues.append(_problem("p03.projection", case_path, str(error)))
            continue
        fixture_key = (
            replay_input.curve_catalog_sha256,
            replay_input.curve_fixture_id,
        )
        try:
            fixture = resolved_fixtures.get(fixture_key)
            if fixture is None:
                fixture = resolve_curve_fixture(
                    replay_input.curve_catalog_sha256,
                    replay_input.curve_fixture_id,
                    repo_root=REPO_ROOT,
                )
                resolved_fixtures[fixture_key] = fixture
        except (
            CatalogRegistryError,
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as error:
            issues.append(_problem("p03.fixture", case_path, str(error)))
            continue
        fixture_binding = (
            fixture.curve_id,
            fixture.field_bits,
            fixture.field_p,
            fixture.curve_a,
            fixture.curve_b,
            fixture.generator,
            fixture.subgroup_order,
            fixture.subgroup_order_bits,
        )
        replay_binding = (
            replay_input.curve_id,
            replay_input.field_bits,
            replay_input.p,
            replay_input.a,
            replay_input.b,
            replay_input.G,
            replay_input.ell,
            replay_input.subgroup_order_bits,
        )
        if fixture_binding != replay_binding:
            issues.append(
                _problem(
                    "p03.fixture_binding",
                    case_path,
                    "public replay input differs from its registry-resolved fixture",
                )
            )
            continue

        try:
            public_input = PublicMethodInput(
                method_id=replay_input.method_id,
                algorithm_seed=replay_input.seed,
                p=replay_input.p,
                a=replay_input.a,
                b=replay_input.b,
                G=replay_input.G,
                Q=replay_input.Q,
                ell=replay_input.ell,
                budgets=budgets,
            )
            outcome = run_method(public_input, self_check=True)
        except (OSError, RuntimeError, TypeError, ValueError) as error:
            issues.append(_problem("p03.method", case_path, str(error)))
            continue
        if not isinstance(outcome, SolverOutcome):
            issues.append(
                _problem(
                    "p03.method.shape",
                    case_path,
                    "method must return the immutable SolverOutcome model",
                )
            )
            continue
        outcomes.append((case, outcome))
        expectation = case.validator_only
        if getattr(outcome, "status", None) != "success":
            issues.append(
                _problem(
                    "p03.method.status",
                    case_path,
                    f"method returned {getattr(outcome, 'status', None)!r}",
                )
            )
            continue
        if outcome.candidate_scalar != expectation.legacy_candidate_scalar:
            issues.append(
                _problem(
                    "p03.method.candidate",
                    case_path,
                    "candidate differs from the authenticated legacy baseline",
                )
            )
        independent = validate_candidate(public_input, outcome.candidate_scalar)
        if not isinstance(independent.counters, ValidatorCounters):
            issues.append(
                _problem(
                    "p03.candidate.counters",
                    case_path,
                    "independent validator must return its own counter bucket",
                )
            )
        else:
            validator_group_law_invocations += (
                independent.counters.total_group_law_invocations
            )
            if independent.counters.total_group_law_invocations <= 0:
                issues.append(
                    _problem(
                        "p03.candidate.counters",
                        case_path,
                        "successful validation must record independent oracle work",
                    )
                )
        if independent.passed is not True:
            if not independent.issues:
                issues.append(
                    _problem(
                        "p03.candidate",
                        case_path,
                        "independent candidate validator failed without an issue",
                    )
                )
            for issue in independent.issues:
                issues.append(
                    _problem(
                        f"p03.{issue.code}",
                        f"{case_path}:{issue.path}",
                        issue.message,
                    )
                )
        counters = outcome.counters
        if (
            counters.legacy_p1_group_operations
            != expectation.legacy_group_operations
        ):
            issues.append(
                _problem(
                    "p03.method.operations",
                    case_path,
                    "group-operation count differs from the legacy baseline",
                )
            )
        if counters.legacy_p1_group_operations != (
            counters.offline_setup.group_law_invocations
            + counters.online_target.group_law_invocations
        ):
            issues.append(
                _problem(
                    "p03.method.phase_sum",
                    case_path,
                    "legacy operation count must exclude self-check and equal setup plus online",
                )
            )
        if case.legacy_method == "bsgs":
            observed = (
                counters.offline_setup.group_law_invocations,
                counters.online_target.group_law_invocations,
                counters.table_entries,
                counters.estimated_algorithmic_table_bytes,
            )
            expected = (
                expectation.bsgs_offline_setup_group_law_invocations,
                expectation.bsgs_online_target_group_law_invocations,
                expectation.bsgs_table_entries,
                expectation.legacy_memory_bytes,
            )
            if observed != expected:
                issues.append(
                    _problem(
                        "p03.method.bsgs_phases",
                        case_path,
                        "cold BSGS setup/online/table estimates differ from legacy",
                    )
                )
        elif case.legacy_method == "pollard_rho":
            if (
                counters.offline_setup.group_law_invocations != 0
                or counters.table_entries != 0
                or counters.estimated_algorithmic_table_bytes
                != expectation.legacy_memory_bytes
                or counters.distinguished_points != 0
                or outcome.diagnostics.deterministic_steps
                != outcome.diagnostics.floyd_iterations
            ):
                issues.append(
                    _problem(
                        "p03.method.rho_semantics",
                        case_path,
                        "ordinary rho counter/estimate semantics drifted",
                    )
                )
        else:
            issues.append(
                _problem(
                    "p03.method.mapping",
                    case_path,
                    f"unknown legacy method {case.legacy_method!r}",
                )
            )

    if len(outcomes) != 64:
        issues.append(
            _problem(
                "p03.method.coverage",
                "$.p03_replay.cases",
                f"expected 64 method outcomes, got {len(outcomes)}",
            )
        )
        return sorted(set(issues))
    if validator_group_law_invocations <= 0:
        issues.append(
            _problem(
                "p03.candidate.counters",
                "$.p03_replay.validator_work",
                "independent validator work must remain separate and nonzero",
            )
        )

    bsgs = tuple(outcome for case, outcome in outcomes if case.legacy_method == "bsgs")
    rho = tuple(
        outcome for case, outcome in outcomes if case.legacy_method == "pollard_rho"
    )
    aggregate_checks = {
        "bsgs_legacy_group_operations": sum(
            outcome.counters.legacy_p1_group_operations or 0 for outcome in bsgs
        ),
        "bsgs_offline_setup_group_law_invocations": sum(
            outcome.counters.offline_setup.group_law_invocations for outcome in bsgs
        ),
        "bsgs_online_target_group_law_invocations": sum(
            outcome.counters.online_target.group_law_invocations for outcome in bsgs
        ),
        "bsgs_table_entries": sum(
            outcome.counters.table_entries for outcome in bsgs
        ),
        "bsgs_estimated_algorithmic_table_bytes": sum(
            outcome.counters.estimated_algorithmic_table_bytes for outcome in bsgs
        ),
        "rho_legacy_group_operations": sum(
            outcome.counters.legacy_p1_group_operations or 0 for outcome in rho
        ),
        "expected_rho_floyd_iterations": sum(
            outcome.diagnostics.floyd_iterations for outcome in rho
        ),
        "expected_rho_restarts": sum(
            outcome.counters.restarts for outcome in rho
        ),
        "expected_rho_collisions": sum(
            outcome.counters.collisions for outcome in rho
        ),
        "expected_rho_noninvertible_collisions": sum(
            outcome.counters.noninvertible_collisions for outcome in rho
        ),
        "expected_rho_invalid_candidate_collisions": sum(
            outcome.diagnostics.invalid_candidate_collisions for outcome in rho
        ),
    }
    for report_field, observed in aggregate_checks.items():
        expected = getattr(report, report_field, None)
        if type(expected) is not int or observed != expected:
            issues.append(
                _problem(
                    "p03.method.aggregate",
                    f"$.p03_replay.{report_field}",
                    f"expected {expected!r}, got {observed!r}",
                )
            )
    rho_attempts = sum(outcome.diagnostics.attempts for outcome in rho)
    if rho_attempts != report.rho_case_count + report.expected_rho_restarts:
        issues.append(
            _problem(
                "p03.method.rho_attempts",
                "$.p03_replay.rho_attempts",
                "rho attempts must equal cases plus actual restart transitions",
            )
        )
    return sorted(set(issues))


def _p04c_target_issues() -> list[Issue]:
    """Verify the committed split targets and sole target-registry authority."""

    try:
        from experiments.ecdlp_lab.core.target_registry import (
            TARGET_REGISTRY_RAW_SHA256,
            load_target_pairs,
            load_target_registry,
        )
        from experiments.ecdlp_lab.orchestration.generate_ci_targets import (
            REGISTRY_PATH,
            generate,
        )
    except ImportError as error:
        return [_problem("p04c.import", str(LAB_ROOT), str(error))]

    issues: list[Issue] = []
    try:
        outputs = generate(repo_root=REPO_ROOT)
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        return [_problem("p04c.generate", str(REPO_ROOT), str(error))]
    for relative_path, expected in sorted(outputs.items()):
        path = REPO_ROOT / relative_path
        try:
            actual = path.read_bytes()
        except OSError as error:
            issues.append(_problem("p04c.fixture", relative_path, str(error)))
            continue
        if actual != expected:
            issues.append(
                _problem(
                    "p04c.fixture_fixpoint",
                    relative_path,
                    "committed target bytes differ from deterministic generation",
                )
            )
    registry_bytes = outputs.get(REGISTRY_PATH)
    try:
        from .canonical import sha256_bytes

        if registry_bytes is None or sha256_bytes(registry_bytes) != TARGET_REGISTRY_RAW_SHA256:
            issues.append(
                _problem(
                    "p04c.registry_raw",
                    REGISTRY_PATH,
                    "target registry raw trust root drifted",
                )
            )
        authorities = load_target_registry(repo_root=REPO_ROOT)
        pairs = load_target_pairs(
            [authority.public_target_vector_sha256 for authority in authorities],
            repo_root=REPO_ROOT,
        )
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        issues.append(_problem("p04c.registry", REGISTRY_PATH, str(error)))
        return sorted(set(issues))
    if len(authorities) != 7 or len(pairs) != 7:
        issues.append(
            _problem(
                "p04c.registry_count",
                REGISTRY_PATH,
                "target registry must authorize one legacy and six CI pairs",
            )
        )
    return sorted(set(issues))


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
    """Run every dependency-free lab validation and return a stable report."""

    schemas, issues = _schema_issues()
    records, record_hashes, fixture_issues = _load_valid_bundle()
    issues.extend(fixture_issues)
    catalog_authorities, registry_issues = _catalog_authorities()
    issues.extend(registry_issues)
    trusted_catalogs = frozenset(
        authority.sha256 for authority in catalog_authorities
    )
    issues.extend(_registered_catalog_issues(catalog_authorities))
    issues.extend(_p03_replay_issues())
    issues.extend(_p04c_target_issues())
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
    parser = argparse.ArgumentParser(description="Validate the ECDLP lab offline.")
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
