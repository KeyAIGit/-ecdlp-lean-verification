"""Semantic validation and cross-record binding for lab engineering fixtures."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from itertools import product
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .canonical import sha256_file, sha256_json
from .issues import Issue
from .paths import PathSafetyError, resolve_artifact_path, validate_repo_relative
from .safety import CONTRACT_KINDS, validate_safety
from .schema import load_and_validate_schema

ContractIssue = Issue

LAB_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SCHEMA_ROOT = LAB_ROOT / "contracts"
DEFAULT_REPO_ROOT = LAB_ROOT.parents[1]

PRIMARY_ID_FIELDS = {
    "campaign_config_v1": "campaign_id",
    "target_vector_v1": "target_vector_id",
    "work_unit_v1": "work_unit_id",
    "method_request_v1": "request_id",
    "method_result_v1": "result_id",
    "telemetry_v1": "telemetry_id",
    "validation_receipt_v1": "validation_id",
    "analysis_summary_v1": "analysis_id",
    "artifact_ref_v1": "artifact_id",
}


@dataclass(frozen=True)
class ValidationContext:
    """Immutable external facts needed by fail-closed semantic validation.

    Digest allowlists are authority inputs, never facts inferred from a bundle
    being validated.  Empty defaults therefore fail closed for any record that
    references a catalog or public target vector.
    """

    repo_root: Path = field(default_factory=lambda: DEFAULT_REPO_ROOT)
    schema_root: Path = field(default_factory=lambda: DEFAULT_SCHEMA_ROOT)
    known_catalog_sha256s: frozenset[str] = field(default_factory=frozenset)
    known_target_vector_sha256s: frozenset[str] = field(default_factory=frozenset)
    public_target_payloads: Mapping[str, Mapping[str, Any]] = field(
        default_factory=dict
    )
    record_sha256s_by_id: Mapping[str, str] = field(default_factory=dict)
    verify_artifacts: bool = True

    @classmethod
    def from_records(
        cls,
        records: Iterable[Any],
        *,
        repo_root: Path | str | None = None,
        schema_root: Path | str | None = None,
        known_catalog_sha256s: Iterable[str] = (),
        known_target_vector_sha256s: Iterable[str] = (),
        record_sha256s_by_id: Mapping[str, str] | None = None,
        verify_artifacts: bool = True,
    ) -> "ValidationContext":
        catalogs = frozenset(known_catalog_sha256s)
        vectors = frozenset(known_target_vector_sha256s)
        payloads: dict[str, Mapping[str, Any]] = {}
        for record in records:
            if not isinstance(record, dict):
                continue
            kind = record.get("contract_kind")
            if kind == "target_vector_v1" and record.get("branch") == "public":
                payload = record.get("public_payload")
                if isinstance(payload, dict):
                    vector_id = record.get("target_vector_id")
                    if isinstance(vector_id, str) and vector_id in vectors:
                        payloads[vector_id] = dict(payload)
        return cls(
            repo_root=Path(repo_root) if repo_root is not None else DEFAULT_REPO_ROOT,
            schema_root=(
                Path(schema_root) if schema_root is not None else DEFAULT_SCHEMA_ROOT
            ),
            known_catalog_sha256s=catalogs,
            known_target_vector_sha256s=vectors,
            public_target_payloads=payloads,
            record_sha256s_by_id=dict(record_sha256s_by_id or {}),
            verify_artifacts=verify_artifacts,
        )


def derive_campaign_id(record: Mapping[str, Any]) -> str:
    """Derive the campaign semantic identity from its stable projection."""

    projection = {
        key: value
        for key, value in record.items()
        if key not in {"campaign_id", "provenance", "retainable"}
    }
    return sha256_json(projection)


def derive_target_vector_id(record: Mapping[str, Any]) -> str:
    """Derive a target identity from exactly its public or private payload."""

    branch = record.get("branch")
    field_name = (
        "public_payload" if branch == "public" else "private_payload"
        if branch == "private_validator_only"
        else None
    )
    if field_name is None or not isinstance(record.get(field_name), dict):
        raise ValueError("target vector requires one branch-appropriate payload")
    return sha256_json(record[field_name])


def _walk(value: Any, path: str = "$") -> Iterable[tuple[str, str, Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            yield child_path, key, child
            yield from _walk(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, f"{path}[{index}]")


def _known_digest_issues(
    record: dict[str, Any], context: ValidationContext
) -> list[Issue]:
    issues: list[Issue] = []
    catalog_refs: list[tuple[str, Any]] = []
    vector_refs: list[tuple[str, Any]] = []
    matrix = record.get("matrix")
    if isinstance(matrix, dict):
        catalog_refs.extend(
            (f"$.matrix.curve_catalog_sha256s[{index}]", value)
            for index, value in enumerate(matrix.get("curve_catalog_sha256s", []))
        )
        vector_refs.extend(
            (f"$.matrix.target_vector_sha256s[{index}]", value)
            for index, value in enumerate(matrix.get("target_vector_sha256s", []))
        )
    public = record.get("public_payload")
    if isinstance(public, dict):
        catalog_refs.append(
            ("$.public_payload.curve_catalog_sha256", public.get("curve_catalog_sha256"))
        )
        if record.get("branch") == "public":
            vector_refs.append(("$.target_vector_id", record.get("target_vector_id")))
    private = record.get("private_payload")
    if isinstance(private, dict):
        vector_refs.append(
            (
                "$.private_payload.public_target_vector_sha256",
                private.get("public_target_vector_sha256"),
            )
        )
    identity = record.get("identity")
    if isinstance(identity, dict):
        catalog_refs.append(
            ("$.identity.curve_catalog_sha256", identity.get("curve_catalog_sha256"))
        )
        vector_refs.append(
            (
                "$.identity.public_target_vector_sha256",
                identity.get("public_target_vector_sha256"),
            )
        )
    if "curve_catalog_sha256" in record:
        catalog_refs.append(
            ("$.curve_catalog_sha256", record.get("curve_catalog_sha256"))
        )
    if "public_target_vector_sha256" in record:
        vector_refs.append(
            (
                "$.public_target_vector_sha256",
                record.get("public_target_vector_sha256"),
            )
        )

    for path, digest in catalog_refs:
        if not isinstance(digest, str) or digest not in context.known_catalog_sha256s:
            issues.append(
                Issue(
                    "contract.catalog.unknown",
                    path,
                    "catalog digest is not present in the trusted registry",
                )
            )
    for path, digest in vector_refs:
        if not isinstance(digest, str) or digest not in context.known_target_vector_sha256s:
            issues.append(
                Issue(
                    "contract.target_vector.unknown",
                    path,
                    "public target-vector digest is not in the trusted manifest",
                )
            )
    return issues


def _campaign_identity_issues(record: dict[str, Any]) -> list[Issue]:
    try:
        expected = derive_campaign_id(record)
    except ValueError as error:
        return [Issue("contract.campaign.digest", "$", str(error))]
    issues: list[Issue] = []
    if record.get("campaign_id") != expected:
        issues.append(
            Issue(
                "contract.campaign.digest",
                "$.campaign_id",
                "campaign_id must equal the canonical campaign projection digest",
            )
        )
    provenance = record.get("provenance")
    if isinstance(provenance, dict) and provenance.get("config_sha256") != expected:
        issues.append(
            Issue(
                "contract.campaign.provenance",
                "$.provenance.config_sha256",
                "campaign provenance must bind its semantic campaign identity",
            )
        )
    return issues


def _target_identity_issues(record: dict[str, Any]) -> list[Issue]:
    try:
        expected = derive_target_vector_id(record)
    except ValueError as error:
        return [Issue("contract.target.digest", "$", str(error))]
    if record.get("target_vector_id") != expected:
        return [
            Issue(
                "contract.target.digest",
                "$.target_vector_id",
                "target_vector_id must equal its canonical branch payload digest",
            )
        ]
    return []


def _work_identity_issues(record: dict[str, Any]) -> list[Issue]:
    issues: list[Issue] = []
    identity = record.get("identity")
    if isinstance(identity, dict):
        try:
            expected_work = sha256_json(identity)
        except ValueError as error:
            issues.append(Issue("contract.work.digest", "$.identity", str(error)))
        else:
            if record.get("work_unit_id") != expected_work:
                issues.append(
                    Issue(
                        "contract.work.digest",
                        "$.work_unit_id",
                        "work_unit_id must equal sha256(canonical identity)",
                    )
                )
        method_hash = identity.get("method_implementation_sha256")
        validator_hash = identity.get("validator_implementation_sha256")
        if isinstance(method_hash, str) and method_hash == validator_hash:
            issues.append(
                Issue(
                    "contract.work.self_validator",
                    "$.identity.validator_implementation_sha256",
                    "method and validator implementations must differ",
                )
            )
    if isinstance(record.get("work_unit_id"), str) and isinstance(
        record.get("retry_ordinal"), int
    ):
        expected_attempt = sha256_json(
            {
                "retry_ordinal": record["retry_ordinal"],
                "work_unit_id": record["work_unit_id"],
            }
        )
        if record.get("attempt_id") != expected_attempt:
            issues.append(
                Issue(
                    "contract.attempt.digest",
                    "$.attempt_id",
                    "attempt_id must bind work_unit_id and retry_ordinal",
                )
            )
    return issues


def _campaign_issues(record: dict[str, Any]) -> list[Issue]:
    matrix = record.get("matrix")
    if not isinstance(matrix, dict):
        return []
    count = 1
    for key in (
        "curve_catalog_sha256s",
        "curve_fixture_ids",
        "target_vector_sha256s",
        "method_ids",
        "algorithm_seeds",
    ):
        axis = matrix.get(key)
        if not isinstance(axis, list):
            return []
        count *= len(axis)
    repetitions = matrix.get("repetitions")
    if not isinstance(repetitions, int) or isinstance(repetitions, bool):
        return []
    count *= repetitions
    issues = _campaign_identity_issues(record)
    if record.get("expected_work_unit_count") != count:
        issues.append(
            Issue(
                "contract.campaign.work_count",
                "$.expected_work_unit_count",
                "expected count must equal the full matrix product times repetitions",
            )
        )
    return issues


_PRIVATE_METHOD_KEYS = frozenset(
    {
        "expected_scalar",
        "target_derivation_seed",
        "private_payload",
        "private_target_receipt",
        "private_target_receipt_sha256",
        "generation_receipt_sha256",
        "target_answer",
        "answer_file",
        "dlp_oracle",
        "lookup_table",
    }
)


def _method_request_issues(
    record: dict[str, Any], context: ValidationContext
) -> list[Issue]:
    issues: list[Issue] = []
    for path, key, _value in _walk(record):
        if key in _PRIVATE_METHOD_KEYS:
            issues.append(
                Issue(
                    "contract.method_request.private_target",
                    path,
                    "method request contains validator-only target material",
                )
            )
    precomputation = record.get("public_precomputation")
    if isinstance(precomputation, dict) and precomputation.get(
        "priced_in_offline_cost"
    ) is not True:
        issues.append(
            Issue(
                "contract.method_request.hidden_precomputation",
                "$.public_precomputation.priced_in_offline_cost",
                "all public precomputation must be priced in offline cost",
            )
        )

    vector_id = record.get("public_target_vector_sha256")
    expected = context.public_target_payloads.get(vector_id)
    if isinstance(vector_id, str) and vector_id in context.known_target_vector_sha256s:
        if expected is None:
            issues.append(
                Issue(
                    "contract.target_vector.payload_missing",
                    "$.public_target_vector_sha256",
                    "trusted vector digest has no matching committed public payload",
                )
            )
            return issues
        comparisons = {
            "curve_catalog_sha256": expected.get("curve_catalog_sha256"),
            "curve_fixture_id": expected.get("curve_fixture_id"),
            "generator": expected.get("generator"),
            "target": expected.get("target"),
            "subgroup_order": expected.get("subgroup_order"),
            "subgroup_order_bits": expected.get("subgroup_order_bits"),
            "public_scalar_interval": expected.get("public_scalar_interval"),
        }
        for key, required in comparisons.items():
            if record.get(key) != required:
                issues.append(
                    Issue(
                        "contract.method_request.target_binding",
                        f"$.{key}",
                        "public method input differs from its digest-bound target vector",
                    )
                )
        curve = record.get("curve")
        if isinstance(curve, dict):
            for key in ("curve_id", "field_bits", "field_p", "curve_a", "curve_b"):
                if curve.get(key) != expected.get(key):
                    issues.append(
                        Issue(
                            "contract.method_request.target_binding",
                            f"$.curve.{key}",
                            "curve differs from its digest-bound target vector",
                        )
                    )
    return issues


def _receipt_issues(record: dict[str, Any]) -> list[Issue]:
    issues: list[Issue] = []
    if (
        isinstance(record.get("producer_implementation_sha256"), str)
        and record.get("producer_implementation_sha256")
        == record.get("validator_implementation_sha256")
    ):
        issues.append(
            Issue(
                "contract.validation.self_validator",
                "$.validator_implementation_sha256",
                "validator implementation must differ from the producer",
            )
        )
    if record.get("independent_implementation") is not True:
        issues.append(
            Issue(
                "contract.validation.independence",
                "$.independent_implementation",
                "validation must use an independent implementation",
            )
        )
    if record.get("shares_decisive_logic") is not False:
        issues.append(
            Issue(
                "contract.validation.shared_logic",
                "$.shares_decisive_logic",
                "producer and validator cannot share decisive logic",
            )
        )
    checks = record.get("checks")
    all_checks_passed = isinstance(checks, list) and bool(checks) and all(
        isinstance(check, dict) and check.get("status") == "passed"
        for check in checks
    )
    passed = record.get("passed") is True
    if passed and record.get("provenance_valid") is not True:
        issues.append(
            Issue(
                "contract.validation.provenance",
                "$.provenance_valid",
                "a passed receipt requires valid provenance",
            )
        )
    if passed and not all_checks_passed:
        issues.append(
            Issue(
                "contract.validation.checks",
                "$.checks",
                "a passed receipt requires every recorded check to pass",
            )
        )
    if (
        passed
        and record.get("subject_contract_kind") == "method_result_v1"
        and record.get("candidate_relation_valid") is not True
    ):
        issues.append(
            Issue(
                "contract.validation.relation",
                "$.candidate_relation_valid",
                "a passed method-result receipt requires a valid candidate relation",
            )
        )
    if record.get("subject_contract_kind") != "method_result_v1":
        for field_name in (
            "candidate_scalar",
            "candidate_relation_valid",
            "private_target_receipt_sha256",
        ):
            if record.get(field_name) is not None:
                issues.append(
                    Issue(
                        "contract.validation.non_method_candidate",
                        f"$.{field_name}",
                        "non-method validation receipts cannot carry candidate material",
                    )
                )
    retaining = record.get("retention_decision") == "retain"
    if retaining and not passed:
        issues.append(
            Issue(
                "contract.validation.retention",
                "$.retention_decision",
                "retention requires a passed receipt",
            )
        )
    if record.get("retainable") is True and not retaining:
        issues.append(
            Issue(
                "contract.validation.retention",
                "$.retainable",
                "a retainable receipt must carry the retain decision",
            )
        )
    if retaining and record.get("retainable") is not True:
        issues.append(
            Issue(
                "contract.validation.retention",
                "$.retainable",
                "a retain decision must mark the receipt retainable",
            )
        )
    return issues


def _method_result_issues(record: dict[str, Any]) -> list[Issue]:
    if record.get("retainable") is True:
        return [
            Issue(
                "contract.result.retainable",
                "$.retainable",
                "method results are never directly retainable; retain a validated artifact",
            )
        ]
    return []


def _artifact_issues(
    record: dict[str, Any], context: ValidationContext
) -> list[Issue]:
    issues: list[Issue] = []
    digest = record.get("sha256")
    if isinstance(digest, str) and record.get("artifact_id") != digest:
        issues.append(
            Issue(
                "contract.artifact.identity",
                "$.artifact_id",
                "artifact_id must equal the content digest",
            )
        )
    location = record.get("location")
    if location is None:
        return issues
    try:
        validate_repo_relative(location)
        resolved = resolve_artifact_path(
            context.repo_root,
            location,
            must_exist=context.verify_artifacts,
        )
    except (PathSafetyError, TypeError, OSError) as error:
        issues.append(Issue("contract.artifact.path", "$.location", str(error)))
        return issues
    if not context.verify_artifacts:
        return issues
    if not resolved.is_file():
        issues.append(
            Issue("contract.artifact.file", "$.location", "artifact must be a regular file")
        )
        return issues
    try:
        actual_size = resolved.stat().st_size
        actual_digest = sha256_file(resolved)
    except OSError as error:
        issues.append(Issue("contract.artifact.read", "$.location", str(error)))
        return issues
    if record.get("size_bytes") != actual_size:
        issues.append(
            Issue(
                "contract.artifact.size",
                "$.size_bytes",
                f"declared size does not match {actual_size} bytes",
            )
        )
    if digest != actual_digest:
        issues.append(
            Issue(
                "contract.artifact.hash",
                "$.sha256",
                "declared digest does not match artifact bytes",
            )
        )
    return issues


def validate_contract(
    record: Any,
    context: ValidationContext | None = None,
    *,
    expected_kind: str | None = None,
) -> list[ContractIssue]:
    """Validate one record against schema, immutable safety, and semantics."""

    active = context or ValidationContext()
    issues: list[Issue] = list(validate_safety(record, expected_kind=expected_kind))
    if not isinstance(record, dict):
        return sorted(set(issues))
    kind = record.get("contract_kind")
    if kind not in CONTRACT_KINDS:
        return sorted(set(issues))
    try:
        _schema, schema_issues = load_and_validate_schema(
            record, active.schema_root / f"{kind}.schema.json"
        )
    except (OSError, ValueError) as error:
        issues.append(Issue("contract.schema.load", "$", str(error)))
    else:
        issues.extend(schema_issues)

    issues.extend(_known_digest_issues(record, active))
    if kind == "campaign_config_v1":
        issues.extend(_campaign_issues(record))
    elif kind == "target_vector_v1":
        issues.extend(_target_identity_issues(record))
    elif kind == "work_unit_v1":
        issues.extend(_work_identity_issues(record))
    elif kind == "method_request_v1":
        issues.extend(_method_request_issues(record, active))
    elif kind == "method_result_v1":
        issues.extend(_method_result_issues(record))
    elif kind == "validation_receipt_v1":
        issues.extend(_receipt_issues(record))
    elif kind == "artifact_ref_v1":
        issues.extend(_artifact_issues(record, active))
    return sorted(set(issues))


def _primary_id(record: Mapping[str, Any]) -> str | None:
    field_name = PRIMARY_ID_FIELDS.get(record.get("contract_kind"))
    value = record.get(field_name) if field_name is not None else None
    return value if isinstance(value, str) else None


def _by_id(
    records: Sequence[dict[str, Any]], kind: str, issues: list[Issue]
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for record in records:
        if record.get("contract_kind") != kind:
            continue
        identifier = _primary_id(record)
        if identifier is None:
            continue
        if identifier in result:
            issues.append(
                Issue(
                    "cross.duplicate_id",
                    f"$.{kind}.{identifier}",
                    "duplicate primary identifier in bundle",
                )
            )
        else:
            result[identifier] = record
    return result


def _context_for_bundle(
    records: Sequence[dict[str, Any]], context: ValidationContext | None
) -> ValidationContext:
    active = context or ValidationContext()
    # Payload lookup may be reconstructed from a bundle only after its full
    # canonical record digest has already been authorized by trusted context.
    # This supplies content, never authority.
    payloads = dict(active.public_target_payloads)
    for record in records:
        if record.get("contract_kind") != "target_vector_v1" or record.get("branch") != "public":
            continue
        payload = record.get("public_payload")
        if not isinstance(payload, dict):
            continue
        vector_id = record.get("target_vector_id")
        if (
            isinstance(vector_id, str)
            and vector_id in active.known_target_vector_sha256s
            and vector_id == sha256_json(payload)
        ):
            payloads[vector_id] = dict(payload)
    return replace(active, public_target_payloads=payloads)


def _link_issue(code: str, path: str, message: str) -> Issue:
    return Issue(code, path, message)


def validate_cross_record_bundle(
    records: Iterable[Any], context: ValidationContext | None = None
) -> list[ContractIssue]:
    """Validate a coherent lab bundle without granting scientific authority."""

    materialized = list(records)
    issues: list[Issue] = []
    typed: list[dict[str, Any]] = []
    for index, record in enumerate(materialized):
        if not isinstance(record, dict):
            issues.append(
                Issue("cross.record.type", f"$[{index}]", "bundle member must be an object")
            )
        else:
            typed.append(record)
    active = _context_for_bundle(typed, context)
    for record in typed:
        issues.extend(validate_contract(record, active))

    campaigns = _by_id(typed, "campaign_config_v1", issues)
    works = _by_id(typed, "work_unit_v1", issues)
    requests = _by_id(typed, "method_request_v1", issues)
    results = _by_id(typed, "method_result_v1", issues)
    receipts = _by_id(typed, "validation_receipt_v1", issues)
    _by_id(typed, "telemetry_v1", issues)
    _by_id(typed, "analysis_summary_v1", issues)
    _by_id(typed, "artifact_ref_v1", issues)

    public_vectors: dict[str, dict[str, Any]] = {}
    private_vectors: list[dict[str, Any]] = []
    for record in typed:
        if record.get("contract_kind") != "target_vector_v1":
            continue
        if record.get("branch") == "public" and isinstance(
            record.get("target_vector_id"), str
        ):
            if record["target_vector_id"] in public_vectors:
                issues.append(
                    _link_issue(
                        "cross.target.duplicate_public",
                        "$.target_vector_id",
                        "duplicate public target-vector identifier in bundle",
                    )
                )
            public_vectors[record["target_vector_id"]] = record
        elif record.get("branch") == "private_validator_only":
            private_vectors.append(record)

    for private in private_vectors:
        payload = private.get("private_payload")
        public_id = payload.get("public_target_vector_sha256") if isinstance(payload, dict) else None
        if public_id not in public_vectors:
            issues.append(
                _link_issue(
                    "cross.target.private_public",
                    "$.private_payload.public_target_vector_sha256",
                    "private target receipt does not bind a public target in the bundle",
                )
            )

    for campaign_id, campaign in campaigns.items():
        campaign_works = [work for work in works.values() if work.get("campaign_id") == campaign_id]
        if campaign.get("expected_work_unit_count") != len(campaign_works):
            issues.append(
                _link_issue(
                    "cross.campaign.work_count",
                    "$.expected_work_unit_count",
                    "expanded work-unit count differs from campaign declaration",
                )
            )

        matrix = campaign.get("matrix")
        if not isinstance(matrix, dict):
            continue
        repetitions = matrix.get("repetitions")
        axes = [
            matrix.get("curve_catalog_sha256s"),
            matrix.get("curve_fixture_ids"),
            matrix.get("target_vector_sha256s"),
            matrix.get("method_ids"),
            matrix.get("algorithm_seeds"),
        ]
        if not all(isinstance(axis, list) for axis in axes) or not isinstance(
            repetitions, int
        ):
            continue
        try:
            expected_tuples = set(product(*axes, range(repetitions)))
        except (TypeError, ValueError):
            issues.append(
                _link_issue(
                    "cross.campaign.coverage_type",
                    "$.matrix",
                    "campaign axes must contain hashable scalar values",
                )
            )
            continue
        actual_tuples: set[tuple[Any, ...]] = set()
        for work in campaign_works:
            identity = work.get("identity")
            if not isinstance(identity, dict):
                continue
            try:
                actual_tuples.add(
                    (
                        identity.get("curve_catalog_sha256"),
                        identity.get("curve_fixture_id"),
                        identity.get("public_target_vector_sha256"),
                        identity.get("method_id"),
                        identity.get("algorithm_seed"),
                        identity.get("repetition_ordinal"),
                    )
                )
            except TypeError:
                issues.append(
                    _link_issue(
                        "cross.campaign.coverage_type",
                        "$.identity",
                        "work identity tuple must contain hashable scalar values",
                    )
                )
        if actual_tuples != expected_tuples:
            issues.append(
                _link_issue(
                    "cross.campaign.coverage",
                    "$.matrix",
                    "work units do not cover the complete campaign Cartesian product",
                )
            )

    for work_id, work in works.items():
        campaign = campaigns.get(work.get("campaign_id"))
        if campaign is None:
            issues.append(
                _link_issue(
                    "cross.work.campaign",
                    "$.campaign_id",
                    "work unit references a missing campaign",
                )
            )
            continue
        identity = work.get("identity")
        matrix = campaign.get("matrix")
        if isinstance(identity, dict) and isinstance(matrix, dict):
            membership = (
                ("curve_catalog_sha256", "curve_catalog_sha256s"),
                ("curve_fixture_id", "curve_fixture_ids"),
                ("public_target_vector_sha256", "target_vector_sha256s"),
                ("method_id", "method_ids"),
                ("algorithm_seed", "algorithm_seeds"),
            )
            for identity_key, matrix_key in membership:
                if identity.get(identity_key) not in matrix.get(matrix_key, []):
                    issues.append(
                        _link_issue(
                            "cross.work.matrix",
                            f"$.identity.{identity_key}",
                            "work identity is outside the campaign matrix",
                        )
                    )
            repetition = identity.get("repetition_ordinal")
            repetitions = matrix.get("repetitions")
            if (
                not isinstance(repetition, int)
                or isinstance(repetition, bool)
                or not isinstance(repetitions, int)
                or not 0 <= repetition < repetitions
            ):
                issues.append(
                    _link_issue(
                        "cross.work.repetition",
                        "$.identity.repetition_ordinal",
                        "repetition ordinal is outside the campaign matrix",
                    )
                )
            if identity.get("method_id") not in campaign.get("allowed_method_ids", []):
                issues.append(
                    _link_issue(
                        "cross.work.method",
                        "$.identity.method_id",
                        "method is not allowed by the campaign",
                    )
                )
            if identity.get("campaign_config_sha256") != sha256_json(campaign):
                issues.append(
                    _link_issue(
                        "cross.work.campaign_hash",
                        "$.identity.campaign_config_sha256",
                        "work identity does not bind canonical campaign JSON",
                    )
                )
            if identity.get("budgets") != campaign.get("budgets"):
                issues.append(
                    _link_issue(
                        "cross.work.budgets",
                        "$.identity.budgets",
                        "work budgets must exactly equal campaign budgets",
                    )
                )

    request_by_attempt: dict[tuple[Any, Any], dict[str, Any]] = {}
    for request in requests.values():
        key = (request.get("work_unit_id"), request.get("attempt_id"))
        if key in request_by_attempt:
            issues.append(
                _link_issue(
                    "cross.request.duplicate_attempt",
                    "$.attempt_id",
                    "more than one method request binds the same attempt",
                )
            )
        request_by_attempt[key] = request
        work = works.get(request.get("work_unit_id"))
        if work is None:
            issues.append(
                _link_issue(
                    "cross.request.work", "$.work_unit_id", "request references missing work"
                )
            )
            continue
        if request.get("attempt_id") != work.get("attempt_id"):
            issues.append(
                _link_issue(
                    "cross.request.attempt",
                    "$.attempt_id",
                    "request attempt differs from its work unit",
                )
            )
        identity = work.get("identity")
        if isinstance(identity, dict):
            for key_name in (
                "method_id",
                "algorithm_seed",
                "curve_catalog_sha256",
                "curve_fixture_id",
                "public_target_vector_sha256",
                "budgets",
            ):
                if request.get(key_name) != identity.get(key_name):
                    issues.append(
                        _link_issue(
                            "cross.request.identity",
                            f"$.{key_name}",
                            "request differs from its work identity",
                        )
                    )

    for result in results.values():
        key = (result.get("work_unit_id"), result.get("attempt_id"))
        request = request_by_attempt.get(key)
        if request is None:
            issues.append(
                _link_issue(
                    "cross.result.request",
                    "$.method_request_sha256",
                    "result has no matching method request",
                )
            )
            continue
        if result.get("method_id") != request.get("method_id"):
            issues.append(
                _link_issue(
                    "cross.result.method",
                    "$.method_id",
                    "result method differs from request method",
                )
            )
        expected_hash = sha256_json(request)
        if result.get("method_request_sha256") != expected_hash:
            issues.append(
                _link_issue(
                    "cross.result.request_hash",
                    "$.method_request_sha256",
                    "result does not bind canonical method-request JSON",
                )
            )
        if result.get("status") == "success":
            scalar = result.get("candidate_scalar")
            subgroup_order = request.get("subgroup_order")
            if (
                not isinstance(scalar, int)
                or isinstance(scalar, bool)
                or not isinstance(subgroup_order, int)
                or isinstance(subgroup_order, bool)
                or not 0 <= scalar < subgroup_order
            ):
                issues.append(
                    _link_issue(
                        "cross.result.scalar_range",
                        "$.candidate_scalar",
                        "successful scalar must be the canonical representative in [0,n)",
                    )
                )

    for telemetry in (
        record for record in typed if record.get("contract_kind") == "telemetry_v1"
    ):
        key = (telemetry.get("work_unit_id"), telemetry.get("attempt_id"))
        if key not in request_by_attempt:
            issues.append(
                _link_issue(
                    "cross.telemetry.attempt",
                    "$.attempt_id",
                    "telemetry has no matching method attempt",
                )
            )

    private_hashes = {
        record.get("target_vector_id")
        for record in private_vectors
        if isinstance(record.get("target_vector_id"), str)
    }
    subjects: dict[tuple[Any, Any], dict[str, Any]] = {}
    for record in typed:
        identifier = _primary_id(record)
        kind = record.get("contract_kind")
        if identifier is not None and kind != "validation_receipt_v1":
            subjects[(kind, identifier)] = record
    retained_subjects_with_receipt: set[tuple[Any, Any, str]] = set()
    for receipt in receipts.values():
        subject_key = (
            receipt.get("subject_contract_kind"),
            receipt.get("subject_id"),
        )
        subject = subjects.get(subject_key)
        receipt_valid = not _receipt_issues(receipt)
        if subject is None:
            issues.append(
                _link_issue(
                    "cross.receipt.subject",
                    "$.subject_id",
                    "validation receipt subject is not present in the bundle",
                )
            )
            continue
        expected_hash = sha256_json(subject)
        if receipt.get("subject_sha256") != expected_hash:
            receipt_valid = False
            issues.append(
                _link_issue(
                    "cross.receipt.subject_hash",
                    "$.subject_sha256",
                    "receipt subject digest differs from canonical subject JSON",
                )
            )
        if subject.get("contract_kind") == "method_result_v1":
            if receipt.get("candidate_scalar") != subject.get("candidate_scalar"):
                receipt_valid = False
                issues.append(
                    _link_issue(
                        "cross.receipt.scalar",
                        "$.candidate_scalar",
                        "validator scalar differs from producer result",
                    )
                )
            if receipt.get("private_target_receipt_sha256") not in private_hashes:
                receipt_valid = False
                issues.append(
                    _link_issue(
                        "cross.receipt.private_target",
                        "$.private_target_receipt_sha256",
                        "receipt does not bind the private target semantic ID",
                    )
                )
            work = works.get(subject.get("work_unit_id"))
            identity = work.get("identity") if isinstance(work, dict) else None
            if not isinstance(identity, dict):
                receipt_valid = False
                issues.append(
                    _link_issue(
                        "cross.receipt.work",
                        "$.subject_id",
                        "method-result receipt has no bound work identity",
                    )
                )
            else:
                if receipt.get("producer_implementation_sha256") != identity.get(
                    "method_implementation_sha256"
                ):
                    receipt_valid = False
                    issues.append(
                        _link_issue(
                            "cross.receipt.producer",
                            "$.producer_implementation_sha256",
                            "receipt producer does not match the work method implementation",
                        )
                    )
                if receipt.get("validator_implementation_sha256") != identity.get(
                    "validator_implementation_sha256"
                ):
                    receipt_valid = False
                    issues.append(
                        _link_issue(
                            "cross.receipt.validator",
                            "$.validator_implementation_sha256",
                            "receipt validator does not match the work validator implementation",
                        )
                    )
        if (
            receipt_valid
            and receipt.get("passed") is True
            and receipt.get("retention_decision") == "retain"
            and receipt.get("retainable") is True
        ):
            retained_subjects_with_receipt.add(
                (subject_key[0], subject_key[1], expected_hash)
            )

    receipt_hashes = {sha256_json(receipt) for receipt in receipts.values()}
    for analysis in (
        record for record in typed if record.get("contract_kind") == "analysis_summary_v1"
    ):
        if analysis.get("campaign_id") not in campaigns:
            issues.append(
                _link_issue(
                    "cross.analysis.campaign",
                    "$.campaign_id",
                    "analysis references a missing campaign",
                )
            )
        linked = set(analysis.get("input_validation_receipt_sha256s", []))
        if not linked.issubset(receipt_hashes):
            issues.append(
                _link_issue(
                    "cross.analysis.receipts",
                    "$.input_validation_receipt_sha256s",
                    "analysis contains an unknown validation receipt digest",
                )
            )

    artifacts = [
        record for record in typed if record.get("contract_kind") == "artifact_ref_v1"
    ]
    for artifact in artifacts:
        producer_kind = artifact.get("producer_contract_kind")
        if isinstance(producer_kind, str):
            producers = [
                record for record in typed if record.get("contract_kind") == producer_kind
            ]
            producer_hashes = [
                active.record_sha256s_by_id.get(_primary_id(record))
                for record in producers
            ]
            if not producers:
                issues.append(
                    _link_issue(
                        "cross.artifact.producer",
                        "$.producer_contract_kind",
                        "artifact producer is not present in the bundle",
                    )
                )
            elif any(digest is None for digest in producer_hashes):
                issues.append(
                    _link_issue(
                        "cross.artifact.hash_context",
                        "$.sha256",
                        "raw producer artifact hashes are required for artifact_ref validation",
                    )
                )
            elif artifact.get("sha256") not in producer_hashes:
                issues.append(
                    _link_issue(
                        "cross.artifact.producer",
                        "$.sha256",
                        "artifact digest is not a method result in this bundle",
                    )
                )

    for subject in [*results.values(), *artifacts]:
        if subject.get("retainable") is not True:
            continue
        key = (
            subject.get("contract_kind"),
            _primary_id(subject),
            sha256_json(subject),
        )
        if key not in retained_subjects_with_receipt:
            issues.append(
                _link_issue(
                    "cross.retention.receipt",
                    "$.retainable",
                    "retainable result/artifact requires a passed independent receipt",
                )
            )

    return sorted(set(issues))


__all__ = [
    "ContractIssue",
    "ValidationContext",
    "derive_campaign_id",
    "derive_target_vector_id",
    "validate_contract",
    "validate_cross_record_bundle",
]
