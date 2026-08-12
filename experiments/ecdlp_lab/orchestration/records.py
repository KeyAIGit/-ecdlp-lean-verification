"""Deterministic P04 campaign expansion and contract-record builders."""

from __future__ import annotations

from copy import deepcopy
from itertools import product
from pathlib import Path
from typing import Any, Mapping

from experiments.ecdlp_lab.core.canonical import is_sha256, load_json, sha256_json
from experiments.ecdlp_lab.core.catalog_registry import trusted_catalog_sha256s
from experiments.ecdlp_lab.core.contracts import (
    ValidationContext,
    derive_campaign_id,
    validate_contract,
    validate_cross_record_bundle,
)
from experiments.ecdlp_lab.core.paths import PathSafetyError, resolve_artifact_path
from experiments.ecdlp_lab.core.target_registry import TargetPair, load_target_pair
from experiments.ecdlp_lab.methods.python.model import (
    MAX_U64,
    MethodBudgets,
    SolverOutcome,
)

from .allowlist import allowed_method_ids, resolve_method
from .model import CampaignPlan, OrchestrationError
from .provenance import (
    P04_BASE_SOURCE_COMMIT,
    development_diff_sha256,
    method_implementation_sha256,
    source_snapshot_manifest,
    validator_implementation_sha256,
)
from .validator_worker import make_validator_request


LAB_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPO_ROOT = LAB_ROOT.parents[1]
SMOKE_CAMPAIGN_PATH = "experiments/ecdlp_lab/fixtures/smoke.json"
MAX_P04_WORK_UNITS = 128
_P04_BUDGET_CEILINGS = {
    "max_group_law_invocations": 100_000,
    "max_table_entries": 65_536,
    "max_steps": 100_000,
    "timeout_ns": 5_000_000_000,
    "max_memory_bytes": 67_108_864,
}

_COMMON_BOUNDARY: dict[str, Any] = {
    "schema_version": 1,
    "record_kind": "lab_engineering_fixture",
    "internal_classification": "engineering_only",
    "framework_authorization_class": "fixture",
    "hypothesis_id": None,
    "candidate_id": None,
    "authorization_id": None,
    "native_research_outcome": False,
    "route_effect": "none",
    "retention_class": "engineering_only",
}


def _error(code: str, path: str, message: str) -> OrchestrationError:
    return OrchestrationError(code, path, message)


def _context(pair: TargetPair, repo_root: Path | str) -> ValidationContext:
    public = pair.public_record
    private = pair.private_record
    return ValidationContext.from_records(
        (public, private),
        repo_root=repo_root,
        known_catalog_sha256s=trusted_catalog_sha256s(repo_root=repo_root),
        known_target_vector_sha256s=(pair.public_target_vector_sha256,),
        verify_artifacts=False,
    )


def _raise_contract(issues: list[Any], label: str) -> None:
    if issues:
        first = issues[0]
        raise _error(
            "orchestration.contract",
            first.path,
            f"{label}: {first.code}: {first.message}",
        )


def load_smoke_campaign(
    *, repo_root: Path | str = DEFAULT_REPO_ROOT
) -> dict[str, Any]:
    """Load the strict-JSON smoke campaign from its fixed repository locator."""

    try:
        path = resolve_artifact_path(repo_root, SMOKE_CAMPAIGN_PATH, must_exist=True)
        if not path.is_file():
            raise _error(
                "orchestration.config.file", "$.config", "must be a regular file"
            )
        campaign = load_json(path)
    except OrchestrationError:
        raise
    except (OSError, PathSafetyError, TypeError, ValueError) as error:
        raise _error(
            "orchestration.config.load", "$.config", f"cannot load smoke campaign: {error}"
        ) from error
    if not isinstance(campaign, dict):
        raise _error("orchestration.config.type", "$", "campaign must be an object")
    return campaign


def derive_attempt_id(work_unit_id: str, retry_ordinal: int) -> str:
    if not is_sha256(work_unit_id):
        raise _error("orchestration.identity", "$.work_unit_id", "must be a SHA-256 string")
    if type(retry_ordinal) is not int or retry_ordinal < 0:
        raise _error("orchestration.identity", "$.retry_ordinal", "must be a nonnegative integer")
    return sha256_json(
        {"retry_ordinal": retry_ordinal, "work_unit_id": work_unit_id}
    )


def derive_request_id(work_unit_id: str, attempt_id: str) -> str:
    if not is_sha256(work_unit_id) or not is_sha256(attempt_id):
        raise _error("orchestration.identity", "$", "work and attempt IDs must be SHA-256")
    return sha256_json(
        {
            "attempt_id": attempt_id,
            "contract_kind": "method_request_v1",
            "work_unit_id": work_unit_id,
        }
    )


def derive_result_id(
    work_unit_id: str, attempt_id: str, method_request_sha256: str
) -> str:
    if not all(
        is_sha256(value)
        for value in (work_unit_id, attempt_id, method_request_sha256)
    ):
        raise _error("orchestration.identity", "$", "result identity inputs must be SHA-256")
    return sha256_json(
        {
            "attempt_id": attempt_id,
            "contract_kind": "method_result_v1",
            "method_request_sha256": method_request_sha256,
            "work_unit_id": work_unit_id,
        }
    )


def derive_validation_id(
    subject_sha256: str,
    validator_request_sha256: str,
    validator_output_sha256: str,
) -> str:
    if not all(
        is_sha256(value)
        for value in (
            subject_sha256,
            validator_request_sha256,
            validator_output_sha256,
        )
    ):
        raise _error("orchestration.identity", "$", "validation identity inputs must be SHA-256")
    return sha256_json(
        {
            "subject_sha256": subject_sha256,
            "validator_id": "lab_ec_oracle_v1",
            "validator_output_sha256": validator_output_sha256,
            "validator_request_sha256": validator_request_sha256,
        }
    )


def _matrix_guard(campaign: Mapping[str, Any], pair: TargetPair) -> dict[str, Any]:
    matrix = campaign.get("matrix")
    if not isinstance(matrix, dict):
        raise _error("orchestration.matrix.shape", "$.matrix", "must be an object")
    axes = (
        "curve_catalog_sha256s",
        "curve_fixture_ids",
        "target_vector_sha256s",
        "method_ids",
        "algorithm_seeds",
    )
    if any(not isinstance(matrix.get(name), list) for name in axes):
        raise _error("orchestration.matrix.shape", "$.matrix", "all matrix axes must be arrays")

    # campaign_config_v1 is Cartesian.  Until a pair-aware contract revision,
    # accepting multiple catalogs/fixtures/targets would manufacture invalid
    # combinations.  Reject before any work request or process can be created.
    for name in ("curve_catalog_sha256s", "curve_fixture_ids", "target_vector_sha256s"):
        if len(matrix[name]) != 1:
            raise _error(
                "orchestration.matrix.incompatible_cartesian",
                f"$.matrix.{name}",
                "P04 requires one authorized catalog/fixture/target tuple",
            )

    public = pair.public_payload
    expected_singletons = {
        "curve_catalog_sha256s": public["curve_catalog_sha256"],
        "curve_fixture_ids": public["curve_fixture_id"],
        "target_vector_sha256s": pair.public_target_vector_sha256,
    }
    for name, expected in expected_singletons.items():
        if matrix[name][0] != expected:
            raise _error(
                "orchestration.matrix.target_binding",
                f"$.matrix.{name}[0]",
                "matrix tuple differs from the fixed target authority",
            )
    return matrix


def _verify_campaign_provenance(
    campaign: Mapping[str, Any], method_ids: tuple[str, ...], repo_root: Path | str
) -> None:
    provenance = campaign.get("provenance")
    if not isinstance(provenance, dict):
        raise _error("orchestration.provenance", "$.provenance", "must be an object")
    if provenance.get("source_commit") != P04_BASE_SOURCE_COMMIT:
        raise _error(
            "orchestration.provenance",
            "$.provenance.source_commit",
            "campaign must anchor the fixed merged-P03 base commit",
        )
    if provenance.get("source_tree_clean") is not False:
        raise _error(
            "orchestration.provenance",
            "$.provenance.source_tree_clean",
            "P04 is a nonretainable development snapshot, never a clean tree claim",
        )
    expected_producers = sorted(
        {
            method_implementation_sha256(method, repo_root=repo_root)
            for method in method_ids
        }
    )
    if provenance.get("producer_dependency_sha256s") != expected_producers:
        raise _error(
            "orchestration.provenance",
            "$.provenance.producer_dependency_sha256s",
            "campaign does not bind the exact selected method manifests",
        )
    expected_validator = [validator_implementation_sha256(repo_root=repo_root)]
    if provenance.get("validator_dependency_sha256s") != expected_validator:
        raise _error(
            "orchestration.provenance",
            "$.provenance.validator_dependency_sha256s",
            "campaign does not bind the independent validator manifest",
        )
    expected_snapshot = source_snapshot_manifest(repo_root=repo_root).sha256
    if provenance.get("source_snapshot_sha256") != expected_snapshot:
        raise _error(
            "orchestration.provenance",
            "$.provenance.source_snapshot_sha256",
            "campaign source snapshot manifest drifted",
        )
    expected_diff = development_diff_sha256(expected_snapshot)
    if provenance.get("diff_sha256") != expected_diff:
        raise _error(
            "orchestration.provenance",
            "$.provenance.diff_sha256",
            "development diff must bind the fixed base and current source snapshot",
        )


def expand_campaign(
    campaign_record: Mapping[str, Any],
    *,
    target_pair: TargetPair | None = None,
    repo_root: Path | str = DEFAULT_REPO_ROOT,
) -> CampaignPlan:
    """Validate and fully expand one P01-schema campaign without spawning."""

    if not isinstance(campaign_record, Mapping):
        raise _error("orchestration.config.type", "$", "campaign must be an object")
    campaign = deepcopy(dict(campaign_record))
    pair = target_pair if target_pair is not None else load_target_pair(repo_root=repo_root)
    if not isinstance(pair, TargetPair):
        raise _error("orchestration.target.type", "$.target", "must be a TargetPair authority")
    matrix = _matrix_guard(campaign, pair)

    authority_ids = allowed_method_ids(repo_root=repo_root)
    allowed = campaign.get("allowed_method_ids")
    if allowed != sorted(authority_ids):
        raise _error(
            "orchestration.allowlist.binding",
            "$.allowed_method_ids",
            "campaign must bind the complete sorted fixed allowlist",
        )
    methods = tuple(matrix["method_ids"])
    if (
        not methods
        or any(not isinstance(method, str) for method in methods)
        or len(methods) != len(set(methods))
    ):
        raise _error(
            "orchestration.matrix.methods",
            "$.matrix.method_ids",
            "must be non-empty and unique",
        )
    for index, method_id in enumerate(methods):
        resolve_method(method_id, repo_root=repo_root)
        if method_id not in authority_ids:
            raise _error(
                "orchestration.matrix.methods",
                f"$.matrix.method_ids[{index}]",
                "method is not allowlisted",
            )
    if list(methods) != sorted(methods):
        raise _error("orchestration.matrix.methods", "$.matrix.method_ids", "must be sorted")
    for index, seed in enumerate(matrix["algorithm_seeds"]):
        if type(seed) is not int or not 0 <= seed <= MAX_U64:
            raise _error(
                "orchestration.matrix.seed",
                f"$.matrix.algorithm_seeds[{index}]",
                "seed must be a uint64 exact integer",
            )
    try:
        budgets = MethodBudgets.from_mapping(campaign.get("budgets"))
    except ValueError as error:
        raise _error("orchestration.budgets", "$.budgets", str(error)) from error
    for name, ceiling in _P04_BUDGET_CEILINGS.items():
        if getattr(budgets, name) > ceiling:
            raise _error(
                "orchestration.budgets.ceiling",
                f"$.budgets.{name}",
                "exceeds the fixed P04 container-safe ceiling",
            )
    if campaign.get("retainable") is not False:
        raise _error(
            "orchestration.retention",
            "$.retainable",
            "campaign fixtures are non-retainable",
        )

    repetitions = matrix.get("repetitions")
    if type(repetitions) is not int or repetitions < 1:
        raise _error(
            "orchestration.matrix.repetitions",
            "$.matrix.repetitions",
            "must be positive",
        )
    calculated_count = (
        len(matrix["curve_catalog_sha256s"])
        * len(matrix["curve_fixture_ids"])
        * len(matrix["target_vector_sha256s"])
        * len(methods)
        * len(matrix["algorithm_seeds"])
        * repetitions
    )
    if campaign.get("expected_work_unit_count") != calculated_count:
        raise _error(
            "orchestration.matrix.count",
            "$.expected_work_unit_count",
            "does not equal the complete Cartesian expansion",
        )
    if calculated_count > MAX_P04_WORK_UNITS:
        raise _error(
            "orchestration.matrix.ceiling",
            "$.expected_work_unit_count",
            "campaign exceeds the fixed P04 expansion ceiling",
        )
    try:
        expected_campaign_id = derive_campaign_id(campaign)
    except (TypeError, ValueError) as error:
        raise _error("orchestration.identity", "$", str(error)) from error
    if campaign.get("campaign_id") != expected_campaign_id:
        raise _error("orchestration.identity", "$.campaign_id", "campaign semantic ID drifted")
    _verify_campaign_provenance(campaign, methods, repo_root)

    context = _context(pair, repo_root)
    _raise_contract(validate_contract(campaign, context), "campaign")
    campaign_hash = sha256_json(campaign)
    validator_hash = validator_implementation_sha256(repo_root=repo_root)
    works: list[dict[str, Any]] = []
    for catalog, fixture_id, target_id, method, seed, repetition in product(
        matrix["curve_catalog_sha256s"],
        matrix["curve_fixture_ids"],
        matrix["target_vector_sha256s"],
        methods,
        matrix["algorithm_seeds"],
        range(repetitions),
    ):
        identity = {
            "campaign_config_sha256": campaign_hash,
            "curve_catalog_sha256": catalog,
            "curve_fixture_id": fixture_id,
            "public_target_vector_sha256": target_id,
            "method_id": method,
            "algorithm_seed": seed,
            "method_implementation_sha256": method_implementation_sha256(
                method, repo_root=repo_root
            ),
            "validator_implementation_sha256": validator_hash,
            "budgets": deepcopy(campaign["budgets"]),
            "repetition_ordinal": repetition,
        }
        work_id = sha256_json(identity)
        work = {
            **deepcopy(_COMMON_BOUNDARY),
            "contract_kind": "work_unit_v1",
            "retainable": False,
            "provenance": deepcopy(campaign["provenance"]),
            "work_unit_id": work_id,
            "campaign_id": campaign["campaign_id"],
            "attempt_id": derive_attempt_id(work_id, 0),
            "retry_ordinal": 0,
            "identity": identity,
        }
        _raise_contract(validate_contract(work, context), "work unit")
        works.append(work)

    works.sort(key=lambda value: value["work_unit_id"])
    bundle = [campaign, pair.public_record, pair.private_record, *works]
    _raise_contract(validate_cross_record_bundle(bundle, context), "campaign expansion")
    return CampaignPlan(campaign=campaign, work_units=tuple(works))


def retry_work_unit(work_unit: Mapping[str, Any], retry_ordinal: int) -> dict[str, Any]:
    """Return the same semantic work identity with a new deterministic attempt."""

    if not isinstance(work_unit, Mapping):
        raise _error("orchestration.work.type", "$", "work unit must be an object")
    work = deepcopy(dict(work_unit))
    if work.get("contract_kind") != "work_unit_v1":
        raise _error("orchestration.work.kind", "$.contract_kind", "must be work_unit_v1")
    work["retry_ordinal"] = retry_ordinal
    work["attempt_id"] = derive_attempt_id(work.get("work_unit_id"), retry_ordinal)
    return work


def build_method_request(
    work_unit: Mapping[str, Any],
    target_pair: TargetPair,
    *,
    repo_root: Path | str = DEFAULT_REPO_ROOT,
) -> dict[str, Any]:
    """Project a work unit and only the public half of its target into a request."""

    if not isinstance(work_unit, Mapping) or not isinstance(target_pair, TargetPair):
        raise _error("orchestration.request.input", "$", "requires a work unit and TargetPair")
    work = deepcopy(dict(work_unit))
    identity = work.get("identity")
    if not isinstance(identity, dict):
        raise _error("orchestration.request.identity", "$.identity", "must be an object")
    public = target_pair.public_payload
    if identity.get("public_target_vector_sha256") != target_pair.public_target_vector_sha256:
        raise _error(
            "orchestration.request.target",
            "$.identity.public_target_vector_sha256",
            "work targets another vector",
        )
    if identity.get("curve_catalog_sha256") != public.get("curve_catalog_sha256") or identity.get(
        "curve_fixture_id"
    ) != public.get("curve_fixture_id"):
        raise _error(
            "orchestration.request.target",
            "$.identity",
            "work curve differs from target",
        )
    method_id = identity.get("method_id")
    resolve_method(method_id, repo_root=repo_root)
    if identity.get("method_implementation_sha256") != method_implementation_sha256(
        method_id, repo_root=repo_root
    ):
        raise _error(
            "orchestration.request.provenance",
            "$.identity.method_implementation_sha256",
            "method manifest drifted",
        )
    if identity.get("validator_implementation_sha256") != validator_implementation_sha256(
        repo_root=repo_root
    ):
        raise _error(
            "orchestration.request.provenance",
            "$.identity.validator_implementation_sha256",
            "validator manifest drifted",
        )

    work_id = work.get("work_unit_id")
    attempt_id = work.get("attempt_id")
    request = {
        **deepcopy(_COMMON_BOUNDARY),
        "contract_kind": "method_request_v1",
        "retainable": False,
        "provenance": deepcopy(work.get("provenance")),
        "request_id": derive_request_id(work_id, attempt_id),
        "work_unit_id": work_id,
        "attempt_id": attempt_id,
        "method_id": method_id,
        "algorithm_seed": identity.get("algorithm_seed"),
        "curve_catalog_sha256": public["curve_catalog_sha256"],
        "curve_fixture_id": public["curve_fixture_id"],
        "public_target_vector_sha256": target_pair.public_target_vector_sha256,
        "curve": {
            "curve_id": public["curve_id"],
            "field_bits": public["field_bits"],
            "field_p": public["field_p"],
            "curve_a": public["curve_a"],
            "curve_b": public["curve_b"],
        },
        "generator": deepcopy(public["generator"]),
        "target": deepcopy(public["target"]),
        "subgroup_order": public["subgroup_order"],
        "subgroup_order_bits": public["subgroup_order_bits"],
        "budgets": deepcopy(identity.get("budgets")),
        "public_scalar_interval": deepcopy(public.get("public_scalar_interval")),
        "public_precomputation": None,
    }
    _raise_contract(validate_contract(request, _context(target_pair, repo_root)), "method request")
    return request


def build_method_result(
    work_unit: Mapping[str, Any],
    method_request: Mapping[str, Any],
    outcome: SolverOutcome,
    *,
    repo_root: Path | str = DEFAULT_REPO_ROOT,
) -> dict[str, Any]:
    """Serialize one exact P03 outcome, excluding non-contract diagnostics."""

    if not isinstance(work_unit, Mapping) or not isinstance(method_request, Mapping):
        raise _error("orchestration.result.input", "$", "work and request must be objects")
    if not isinstance(outcome, SolverOutcome):
        raise _error("orchestration.result.input", "$.outcome", "must be SolverOutcome")
    work = deepcopy(dict(work_unit))
    request = deepcopy(dict(method_request))
    if request.get("work_unit_id") != work.get("work_unit_id") or request.get(
        "attempt_id"
    ) != work.get("attempt_id"):
        raise _error(
            "orchestration.result.binding",
            "$",
            "request does not bind this work attempt",
        )
    identity = work.get("identity")
    if not isinstance(identity, dict) or request.get("method_id") != identity.get("method_id"):
        raise _error(
            "orchestration.result.binding",
            "$.method_id",
            "request method differs from work",
        )
    method_id = request["method_id"]
    resolve_method(method_id, repo_root=repo_root)
    for field_name in (
        "algorithm_seed",
        "curve_catalog_sha256",
        "curve_fixture_id",
        "public_target_vector_sha256",
        "budgets",
    ):
        if request.get(field_name) != identity.get(field_name):
            raise _error(
                "orchestration.result.binding",
                f"$.{field_name}",
                "request differs from its work identity",
            )
    expected_request_id = derive_request_id(work["work_unit_id"], work["attempt_id"])
    if request.get("request_id") != expected_request_id:
        raise _error("orchestration.result.binding", "$.request_id", "request ID drifted")
    request_hash = sha256_json(request)
    work_id = work["work_unit_id"]
    attempt_id = work["attempt_id"]
    result = {
        **deepcopy(_COMMON_BOUNDARY),
        "contract_kind": "method_result_v1",
        "retainable": False,
        "provenance": deepcopy(work.get("provenance")),
        "result_id": derive_result_id(work_id, attempt_id, request_hash),
        "work_unit_id": work_id,
        "attempt_id": attempt_id,
        "method_request_sha256": request_hash,
        "method_id": method_id,
        "status": outcome.status,
        "candidate_scalar": outcome.candidate_scalar,
        "failure": outcome.failure.as_dict() if outcome.failure is not None else None,
        "counters": outcome.counters.as_dict(),
    }
    _raise_contract(validate_contract(result), "method result")
    return result


def build_validation_receipt(
    work_unit: Mapping[str, Any],
    method_request: Mapping[str, Any],
    method_result: Mapping[str, Any],
    validator_request: Mapping[str, Any],
    validator_output: Mapping[str, Any],
    target_pair: TargetPair,
    *,
    repo_root: Path | str = DEFAULT_REPO_ROOT,
) -> dict[str, Any]:
    """Bind the public oracle report and private fixture receipt to one result.

    The returned P01 ``validation_receipt_v1`` is the create-only per-work
    final artifact.  It reveals no expected scalar or derivation seed.
    """

    inputs = (work_unit, method_request, method_result, validator_request, validator_output)
    if any(not isinstance(value, Mapping) for value in inputs) or not isinstance(
        target_pair, TargetPair
    ):
        raise _error("orchestration.receipt.input", "$", "receipt inputs have invalid types")
    work = deepcopy(dict(work_unit))
    request = deepcopy(dict(method_request))
    result = deepcopy(dict(method_result))
    validation_request = deepcopy(dict(validator_request))
    validation_output = deepcopy(dict(validator_output))
    identity = work.get("identity")
    if not isinstance(identity, dict):
        raise _error("orchestration.receipt.binding", "$.identity", "work identity is missing")
    context = _context(target_pair, repo_root)
    _raise_contract(validate_contract(work, context), "receipt work unit")
    _raise_contract(validate_contract(request, context), "receipt method request")
    _raise_contract(validate_contract(result, context), "receipt method result")
    if (
        result.get("contract_kind") != "method_result_v1"
        or result.get("work_unit_id") != work.get("work_unit_id")
        or result.get("attempt_id") != work.get("attempt_id")
        or result.get("method_id") != identity.get("method_id")
    ):
        raise _error("orchestration.receipt.binding", "$.subject", "result does not bind the work")
    request_hash = sha256_json(request)
    if result.get("method_request_sha256") != request_hash:
        raise _error(
            "orchestration.receipt.binding",
            "$.method_request_sha256",
            "result does not bind the request",
        )
    expected_validator_request = make_validator_request(
        request, result.get("candidate_scalar")
    )
    if validation_request != expected_validator_request:
        raise _error(
            "orchestration.receipt.binding",
            "$.validator_request",
            "validator request drifted",
        )

    expected_output_keys = frozenset(
        {
            "schema_version",
            "report_kind",
            "candidate",
            "relation_verified",
            "passed",
            "validator_counters",
            "issues",
        }
    )
    if (
        frozenset(validation_output) != expected_output_keys
        or validation_output.get("schema_version") != 1
        or validation_output.get("report_kind") != "ecdlp_lab_candidate_validation_v1"
    ):
        raise _error(
            "orchestration.receipt.output",
            "$.validator_output",
            "validator output protocol drifted",
        )
    validator_counters = validation_output.get("validator_counters")
    counter_keys = frozenset(
        {
            "counter_semantics_id",
            "generator_subgroup_check",
            "target_subgroup_check",
            "candidate_relation_check",
            "total_group_law_invocations",
        }
    )
    if (
        not isinstance(validator_counters, dict)
        or frozenset(validator_counters) != counter_keys
    ):
        raise _error(
            "orchestration.receipt.output",
            "$.validator_output.validator_counters",
            "validator counters drifted",
        )
    if validator_counters.get("counter_semantics_id") != "framework_oracle_group_calls_v1":
        raise _error(
            "orchestration.receipt.output",
            "$.validator_output.validator_counters",
            "validator counter semantics drifted",
        )
    numeric_counters = tuple(
        validator_counters[name]
        for name in (
            "generator_subgroup_check",
            "target_subgroup_check",
            "candidate_relation_check",
        )
    )
    if any(
        type(value) is not int or value < 0 for value in numeric_counters
    ) or validator_counters.get("total_group_law_invocations") != sum(
        numeric_counters
    ):
        raise _error(
            "orchestration.receipt.output",
            "$.validator_output.validator_counters",
            "validator counter totals are invalid",
        )
    output_issues = validation_output.get("issues")
    if not isinstance(output_issues, list) or any(
        not isinstance(issue, dict)
        or set(issue) != {"code", "path", "message"}
        or any(not isinstance(issue[name], str) for name in ("code", "path", "message"))
        for issue in output_issues
    ):
        raise _error(
            "orchestration.receipt.output",
            "$.validator_output.issues",
            "validator issues drifted",
        )
    if type(validation_output.get("passed")) is not bool or type(
        validation_output.get("relation_verified")
    ) is not bool:
        raise _error(
            "orchestration.receipt.output",
            "$.validator_output",
            "validator booleans are invalid",
        )
    if validation_output["passed"] != (
        validation_output["relation_verified"] and not output_issues
    ):
        raise _error(
            "orchestration.receipt.output",
            "$.validator_output.passed",
            "validator pass invariant failed",
        )

    producer_hash = identity.get("method_implementation_sha256")
    validator_hash = identity.get("validator_implementation_sha256")
    provenance = work.get("provenance")
    provenance_valid = (
        isinstance(provenance, dict)
        and request.get("provenance") == provenance
        and result.get("provenance") == provenance
        and provenance.get("config_sha256") == work.get("campaign_id")
        and provenance.get("source_commit") == P04_BASE_SOURCE_COMMIT
        and provenance.get("source_tree_clean") is False
        and producer_hash
        == method_implementation_sha256(identity.get("method_id"), repo_root=repo_root)
        and validator_hash == validator_implementation_sha256(repo_root=repo_root)
        and producer_hash in provenance.get("producer_dependency_sha256s", [])
        and validator_hash in provenance.get("validator_dependency_sha256s", [])
        and provenance.get("source_snapshot_sha256")
        == source_snapshot_manifest(repo_root=repo_root).sha256
        and provenance.get("diff_sha256")
        == development_diff_sha256(provenance.get("source_snapshot_sha256"))
    )
    candidate = result.get("candidate_scalar")
    relation_valid = (
        result.get("status") == "success"
        and validation_output.get("passed") is True
        and validation_output.get("relation_verified") is True
        and validation_output.get("candidate") == candidate
    )
    private_binding_valid = (
        result.get("status") == "success"
        and candidate == target_pair.private_payload.get("expected_scalar")
        and identity.get("public_target_vector_sha256")
        == target_pair.public_target_vector_sha256
    )
    passed = bool(relation_valid and private_binding_valid and provenance_valid)
    checks = [
        {
            "check_id": "candidate_relation_v1",
            "status": "passed" if relation_valid else "failed",
            "detail": "Independent affine oracle recomputed the public candidate relation.",
        },
        {
            "check_id": "private_target_binding_v1",
            "status": "passed" if private_binding_valid else "failed",
            "detail": "Validator-only target receipt binds the canonical public fixture.",
        },
        {
            "check_id": "provenance_binding_v1",
            "status": "passed" if provenance_valid else "failed",
            "detail": (
                "Producer, validator, configuration, and source identities "
                "are digest-bound."
            ),
        },
    ]
    subject_hash = sha256_json(result)
    validator_request_hash = sha256_json(validation_request)
    validator_output_hash = sha256_json(validation_output)
    receipt = {
        **deepcopy(_COMMON_BOUNDARY),
        "contract_kind": "validation_receipt_v1",
        "retainable": False,
        "provenance": deepcopy(provenance),
        "validation_id": derive_validation_id(
            subject_hash, validator_request_hash, validator_output_hash
        ),
        "subject_contract_kind": "method_result_v1",
        "subject_id": result.get("result_id"),
        "subject_sha256": subject_hash,
        "validator_id": "lab_ec_oracle_v1",
        "producer_implementation_sha256": producer_hash,
        "validator_implementation_sha256": validator_hash,
        "validator_request_sha256": validator_request_hash,
        "validator_output_sha256": validator_output_hash,
        "private_target_receipt_sha256": target_pair.private_target_vector_sha256,
        "independent_implementation": True,
        "shares_decisive_logic": False,
        "passed": passed,
        "candidate_scalar": candidate,
        "candidate_relation_valid": bool(relation_valid),
        "provenance_valid": bool(provenance_valid),
        "checks": checks,
        "retention_decision": "development_only" if passed else "reject",
    }
    _raise_contract(validate_contract(receipt), "validation receipt")
    return receipt


__all__ = [
    "MAX_P04_WORK_UNITS",
    "SMOKE_CAMPAIGN_PATH",
    "build_method_request",
    "build_method_result",
    "build_validation_receipt",
    "derive_attempt_id",
    "derive_request_id",
    "derive_result_id",
    "derive_validation_id",
    "expand_campaign",
    "load_smoke_campaign",
    "retry_work_unit",
]
