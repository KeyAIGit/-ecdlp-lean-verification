"""Sequential, resumable P04 campaign coordinator.

The coordinator selects no executable from data.  It expands a byte-bound
campaign, invokes exactly two code-owned worker modules through the fixed
process boundary, retains canonical create-only artifacts, and publishes one
independently validated receipt per work identity.  Private target material is
used only while constructing the receipt and never enters the event log or the
public analysis handoff.
"""

from __future__ import annotations

import tempfile
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from experiments.ecdlp_lab.core.canonical import canonical_json_bytes, sha256_json
from experiments.ecdlp_lab.core.contracts import validate_contract
from experiments.ecdlp_lab.core.target_registry import TargetPair, load_target_pairs
from experiments.ecdlp_lab.methods.python.model import SolverOutcome

from .events import (
    EventLogError,
    EventLogReplay,
    make_event,
    replay_event_bytes,
)
from .method_worker import make_method_worker_request, solver_outcome_from_dict
from .model import CampaignPlan, OrchestrationError
from .process import (
    ProcessBoundaryError,
    ProcessLimits,
    ProcessResult,
    WorkerCodeEntry,
    WorkerModules,
    run_worker,
)
from .provenance import method_execution_manifest, validator_execution_manifest
from .records import (
    build_method_request,
    build_method_result,
    build_validation_receipt,
    expand_campaign,
    retry_work_unit,
)
from .storage import (
    ArtifactCorrupt,
    ArtifactExists,
    ArtifactStore,
    StorageError,
    StoredArtifact,
    WriterLockBusy,
)
from .validator_worker import make_validator_request

EVENT_LOG_PATH = "events.jsonl"
PUBLIC_ANALYSIS_INDEX_PATH = "public_analysis_index.json"
METHOD_WORKER_MODULE = "experiments.ecdlp_lab.orchestration.method_worker"
VALIDATOR_WORKER_MODULE = "experiments.ecdlp_lab.orchestration.validator_worker"
DEFAULT_MAX_RETRIES = 1


class RunnerError(ValueError):
    """The coordinator could not produce a validated deterministic outcome."""

    def __init__(self, code: str, message: str) -> None:
        if not isinstance(code, str) or not code or not isinstance(message, str) or not message:
            raise TypeError("runner error fields must be non-empty strings")
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


@dataclass(frozen=True)
class RunSummary:
    campaign_id: str
    completed_work_unit_ids: tuple[str, ...]
    validation_receipt_sha256s: tuple[str, ...]
    public_analysis_index_sha256: str
    event_chain_head_sha256: str

    @property
    def passed(self) -> bool:
        return bool(self.completed_work_unit_ids)

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "summary_kind": "ecdlp_lab_campaign_run_summary_v1",
            "campaign_id": self.campaign_id,
            "completed_work_unit_ids": list(self.completed_work_unit_ids),
            "validation_receipt_sha256s": list(
                self.validation_receipt_sha256s
            ),
            "public_analysis_index_sha256": self.public_analysis_index_sha256,
            "event_chain_head_sha256": self.event_chain_head_sha256,
            "passed": self.passed,
        }


def _receipt_path(work_unit_id: str) -> str:
    return f"receipts/{work_unit_id}.json"


def _work_path(work_unit_id: str) -> str:
    return f"work_units/{work_unit_id}.json"


def _attempt_path(work_unit_id: str, attempt_id: str, filename: str) -> str:
    return f"attempts/{work_unit_id}/{attempt_id}/{filename}"


def _path_exists(store: ArtifactStore, relative_path: str) -> bool:
    return store.exists(relative_path)


def _read_optional_json(store: ArtifactStore, relative_path: str) -> Any | None:
    try:
        return store.read_json(relative_path)
    except StorageError:
        if not _path_exists(store, relative_path):
            return None
        raise


def _create_or_verify_json(
    store: ArtifactStore, relative_path: str, value: Any
) -> StoredArtifact:
    payload = canonical_json_bytes(value)
    expected_sha256 = sha256_json(value)
    try:
        artifact = store.create_json(relative_path, value)
    except ArtifactExists:
        existing = store.read_json(relative_path, expected_sha256=expected_sha256)
        if existing != value:
            raise RunnerError(
                "orchestration.resume.conflict",
                f"existing create-only artifact differs: {relative_path}",
            )
        return StoredArtifact(relative_path, expected_sha256, len(payload))
    if artifact.sha256 != expected_sha256 or artifact.size_bytes != len(payload):
        raise RunnerError(
            "orchestration.storage.identity",
            f"stored artifact identity drifted: {relative_path}",
        )
    return artifact


def _verify_existing_json(
    store: ArtifactStore, relative_path: str, expected: Any
) -> StoredArtifact:
    payload = canonical_json_bytes(expected)
    expected_sha256 = sha256_json(expected)
    existing = store.read_json(relative_path, expected_sha256=expected_sha256)
    if existing != expected:
        raise RunnerError(
            "orchestration.resume.conflict",
            f"existing create-only artifact differs: {relative_path}",
        )
    return StoredArtifact(relative_path, expected_sha256, len(payload))


def _load_event_state(
    store: ArtifactStore, source_snapshot_sha256: str
) -> EventLogReplay:
    try:
        raw = store.read_bytes(EVENT_LOG_PATH)
    except StorageError:
        if not _path_exists(store, EVENT_LOG_PATH):
            raw = b""
        else:
            raise
    return replay_event_bytes(
        raw, expected_source_snapshot_sha256=source_snapshot_sha256
    )


def _append_event(
    store: ArtifactStore,
    state: EventLogReplay,
    source_snapshot_sha256: str,
    event_type: str,
    *,
    work_unit_id: str | None = None,
    attempt_id: str | None = None,
    payload: Mapping[str, Any] | None = None,
) -> EventLogReplay:
    if event_type == "work_finalized" and work_unit_id in state.finalized_work_unit_ids:
        raise RunnerError(
            "orchestration.final.duplicate", "work identity is already finalized"
        )
    event = make_event(
        sequence=len(state.events),
        previous_event_sha256=state.head_sha256,
        source_snapshot_sha256=source_snapshot_sha256,
        event_type=event_type,
        work_unit_id=work_unit_id,
        attempt_id=attempt_id,
        payload=payload,
    )
    store.append_jsonl(EVENT_LOG_PATH, event, lock_name="events")
    return EventLogReplay(
        state.events + (event,), event["event_sha256"], source_snapshot_sha256
    )


def _process_limits(work_unit: Mapping[str, Any]) -> ProcessLimits:
    identity = work_unit.get("identity")
    budgets = identity.get("budgets") if isinstance(identity, Mapping) else None
    if not isinstance(budgets, Mapping):
        raise RunnerError("orchestration.budgets", "work unit lacks budgets")
    timeout_ns = budgets.get("timeout_ns")
    memory_bytes = budgets.get("max_memory_bytes")
    grace = min(250_000_000, timeout_ns) if type(timeout_ns) is int else 0
    try:
        return ProcessLimits(
            memory_bytes=memory_bytes,
            timeout_ns=timeout_ns,
            term_grace_ns=grace,
        )
    except (TypeError, ValueError) as error:
        raise RunnerError("orchestration.budgets", str(error)) from error


def _worker_modules(repo_root: Path) -> WorkerModules:
    method_files = tuple(
        WorkerCodeEntry(entry.path, entry.sha256, entry.size_bytes)
        for entry in method_execution_manifest(repo_root=repo_root).entries
    )
    validator_files = tuple(
        WorkerCodeEntry(entry.path, entry.sha256, entry.size_bytes)
        for entry in validator_execution_manifest(repo_root=repo_root).entries
    )
    return WorkerModules(
        method=METHOD_WORKER_MODULE,
        validator=VALIDATOR_WORKER_MODULE,
        python_path=repo_root,
        method_files=method_files,
        validator_files=validator_files,
    )


def _validate_replay_semantics(
    state: EventLogReplay, plan: CampaignPlan, campaign_id: str
) -> None:
    if not state.events:
        return
    if state.events[0]["event_type"] != "campaign_started":
        raise RunnerError(
            "orchestration.resume.event", "campaign_started must be the first event"
        )
    work_by_id = {work["work_unit_id"]: work for work in plan.work_units}
    schedules: dict[str, list[str]] = {work_id: [] for work_id in work_by_id}
    finalized: set[str] = set()
    for event in state.events:
        event_type = event["event_type"]
        work_id = event["work_unit_id"]
        attempt_id = event["attempt_id"]
        payload = event["payload"]
        if event_type in {"campaign_started", "resume_started", "campaign_finished"}:
            if work_id is not None or attempt_id is not None:
                raise RunnerError(
                    "orchestration.resume.event",
                    "campaign events cannot bind a work or attempt",
                )
            if payload.get("campaign_id", campaign_id) != campaign_id:
                raise RunnerError(
                    "orchestration.resume.campaign", "campaign event identity drifted"
                )
            if event_type == "resume_started" and payload.get(
                "existing_event_count"
            ) != event["sequence"]:
                raise RunnerError(
                    "orchestration.resume.event", "resume event count drifted"
                )
            continue
        if work_id not in work_by_id:
            raise RunnerError(
                "orchestration.resume.event", "event references an unknown work identity"
            )
        if work_id in finalized:
            raise RunnerError(
                "orchestration.resume.event", "work event appears after finalization"
            )
        if event_type == "work_scheduled":
            retry = payload.get("retry_ordinal")
            expected_retry = len(schedules[work_id])
            if retry != expected_retry:
                raise RunnerError(
                    "orchestration.resume.event", "retry ordinals are not contiguous"
                )
            expected_attempt = retry_work_unit(
                work_by_id[work_id], expected_retry
            )["attempt_id"]
            if attempt_id != expected_attempt:
                raise RunnerError(
                    "orchestration.resume.event", "scheduled attempt identity drifted"
                )
            schedules[work_id].append(expected_attempt)
            continue
        if not isinstance(attempt_id, str) or attempt_id not in schedules[work_id]:
            raise RunnerError(
                "orchestration.resume.event",
                "work event has no matching scheduled attempt",
            )
        if event_type in {"work_failed", "work_finalized"}:
            retry = payload.get("retry_ordinal")
            if (
                type(retry) is not int
                or retry < 0
                or retry >= len(schedules[work_id])
                or schedules[work_id][retry] != attempt_id
            ):
                raise RunnerError(
                    "orchestration.resume.event", "terminal work retry binding drifted"
                )
        if event_type == "work_finalized":
            finalized.add(work_id)


def _last_scheduled_retry(
    state: EventLogReplay, work_unit_id: str
) -> tuple[int, str] | None:
    scheduled = [
        event
        for event in state.events
        if event["event_type"] == "work_scheduled"
        and event["work_unit_id"] == work_unit_id
    ]
    if not scheduled:
        return None
    event = scheduled[-1]
    retry = event["payload"].get("retry_ordinal")
    attempt = event.get("attempt_id")
    if type(retry) is not int or retry < 0 or not isinstance(attempt, str):
        raise RunnerError(
            "orchestration.resume.event", "scheduled attempt metadata is malformed"
        )
    return retry, attempt


def _attempt_records(
    store: ArtifactStore, work_unit_id: str, attempt_id: str
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for filename in (
        "method_request.json",
        "method_result.json",
        "validator_request.json",
        "validator_output.json",
    ):
        value = store.read_json(_attempt_path(work_unit_id, attempt_id, filename))
        if not isinstance(value, dict):
            raise RunnerError(
                "orchestration.resume.artifact",
                f"attempt artifact is not an object: {filename}",
            )
        records.append(value)
    return records[0], records[1], records[2], records[3]


def _validate_final_receipt(
    store: ArtifactStore,
    base_work: Mapping[str, Any],
    retry_ordinal: int,
    attempt_id: str,
    target_pair: TargetPair,
    worker_modules: WorkerModules,
    scratch_root: Path,
    *,
    repo_root: Path,
) -> tuple[dict[str, Any], str]:
    work = retry_work_unit(base_work, retry_ordinal)
    if work.get("attempt_id") != attempt_id:
        raise RunnerError(
            "orchestration.resume.attempt", "attempt ID differs from retry identity"
        )
    request, result, validator_request, validator_output = _attempt_records(
        store, work["work_unit_id"], attempt_id
    )
    if not _validator_replay_matches(
        validator_request,
        validator_output,
        work,
        worker_modules,
        scratch_root,
    ):
        raise RunnerError(
            "orchestration.resume.validator",
            "retained validator output differs from independent replay",
        )
    expected = build_validation_receipt(
        work,
        request,
        result,
        validator_request,
        validator_output,
        target_pair,
        repo_root=repo_root,
    )
    receipt = store.read_json(_receipt_path(work["work_unit_id"]))
    if receipt != expected or receipt.get("passed") is not True:
        raise RunnerError(
            "orchestration.resume.receipt",
            "existing final validation receipt is invalid or drifted",
        )
    issues = validate_contract(receipt)
    if issues:
        raise RunnerError(
            "orchestration.resume.receipt",
            f"existing receipt fails contract validation: {issues[0]}",
        )
    return receipt, sha256_json(receipt)


def _final_event_for(
    state: EventLogReplay, work_unit_id: str
) -> dict[str, Any] | None:
    events = [
        event
        for event in state.events
        if event["event_type"] == "work_finalized"
        and event["work_unit_id"] == work_unit_id
    ]
    if len(events) > 1:
        raise RunnerError(
            "orchestration.final.duplicate", "multiple final events for one work"
        )
    return events[0] if events else None


def _resume_receipt(
    store: ArtifactStore,
    state: EventLogReplay,
    base_work: Mapping[str, Any],
    target_pair: TargetPair,
    source_snapshot_sha256: str,
    worker_modules: WorkerModules,
    scratch_root: Path,
    *,
    repo_root: Path,
) -> tuple[dict[str, Any], str, EventLogReplay] | None:
    work_id = base_work["work_unit_id"]
    final_event = _final_event_for(state, work_id)
    receipt_exists = _path_exists(store, _receipt_path(work_id))
    if final_event is None and not receipt_exists:
        return None
    scheduled = _last_scheduled_retry(state, work_id)
    if scheduled is None:
        raise RunnerError(
            "orchestration.resume.receipt", "final receipt has no scheduled attempt"
        )
    retry_ordinal, attempt_id = scheduled
    if final_event is not None:
        retry = final_event["payload"].get("retry_ordinal")
        if retry != retry_ordinal or final_event.get("attempt_id") != attempt_id:
            raise RunnerError(
                "orchestration.resume.event", "final event differs from scheduled attempt"
            )
    receipt, receipt_hash = _validate_final_receipt(
        store,
        base_work,
        retry_ordinal,
        attempt_id,
        target_pair,
        worker_modules,
        scratch_root,
        repo_root=repo_root,
    )
    if final_event is None:
        state = _append_event(
            store,
            state,
            source_snapshot_sha256,
            "work_finalized",
            work_unit_id=work_id,
            attempt_id=attempt_id,
            payload={
                "retry_ordinal": retry_ordinal,
                "validation_id": receipt["validation_id"],
                "validation_receipt_sha256": receipt_hash,
            },
        )
    else:
        payload = final_event["payload"]
        if payload.get("validation_id") != receipt.get("validation_id") or payload.get(
            "validation_receipt_sha256"
        ) != receipt_hash:
            raise RunnerError(
                "orchestration.resume.event", "final event receipt binding drifted"
            )
    return receipt, receipt_hash, state


def _process_failure_outcome(result: ProcessResult) -> SolverOutcome:
    code = "process_timeout" if result.timed_out else "process_terminated"
    return SolverOutcome.failed(code)


def _validator_replay_matches(
    validator_request: Mapping[str, Any],
    expected_output: Mapping[str, Any],
    work: Mapping[str, Any],
    worker_modules: WorkerModules,
    scratch_root: Path,
) -> bool:
    expected_bytes = canonical_json_bytes(dict(expected_output))
    replay = run_worker(
        "validator",
        validator_request,
        worker_modules=worker_modules,
        limits=_process_limits(work),
        scratch_root=scratch_root,
    )
    return (
        replay.passed
        and not replay.timed_out
        and replay.stderr_bytes == 0
        and replay.output == expected_output
        and replay.stdout_bytes == len(expected_bytes)
        and replay.stdout_sha256 == sha256_json(dict(expected_output))
    )


def _run_attempt(
    store: ArtifactStore,
    state: EventLogReplay,
    work: Mapping[str, Any],
    target_pair: TargetPair,
    source_snapshot_sha256: str,
    worker_modules: WorkerModules,
    scratch_root: Path,
    *,
    repo_root: Path,
) -> tuple[dict[str, Any] | None, str | None, EventLogReplay, str | None]:
    work_id = work["work_unit_id"]
    attempt_id = work["attempt_id"]
    retry_ordinal = work["retry_ordinal"]
    request = build_method_request(work, target_pair, repo_root=repo_root)
    request_artifact = _create_or_verify_json(
        store, _attempt_path(work_id, attempt_id, "method_request.json"), request
    )
    method_worker_request = make_method_worker_request(request)
    state = _append_event(
        store,
        state,
        source_snapshot_sha256,
        "method_started",
        work_unit_id=work_id,
        attempt_id=attempt_id,
        payload={
            "method_request_sha256": request_artifact.sha256,
            "method_worker_request_sha256": sha256_json(method_worker_request),
        },
    )
    limits = _process_limits(work)
    method_process = run_worker(
        "method",
        method_worker_request,
        worker_modules=worker_modules,
        limits=limits,
        scratch_root=scratch_root,
    )
    if method_process.timed_out:
        state = _append_event(
            store,
            state,
            source_snapshot_sha256,
            "method_timeout",
            work_unit_id=work_id,
            attempt_id=attempt_id,
            payload={"retry_ordinal": retry_ordinal},
        )
        if method_process.output is not None:
            state = _append_event(
                store,
                state,
                source_snapshot_sha256,
                "late_result_discarded",
                work_unit_id=work_id,
                attempt_id=attempt_id,
                payload={"phase": "method"},
            )
    if method_process.passed and not method_process.timed_out:
        try:
            outcome = solver_outcome_from_dict(method_process.output)
        except (TypeError, ValueError) as error:
            return None, None, state, f"invalid_method_output:{error}"
    else:
        outcome = _process_failure_outcome(method_process)
    result = build_method_result(work, request, outcome, repo_root=repo_root)
    result_artifact = _create_or_verify_json(
        store, _attempt_path(work_id, attempt_id, "method_result.json"), result
    )
    state = _append_event(
        store,
        state,
        source_snapshot_sha256,
        "method_finished",
        work_unit_id=work_id,
        attempt_id=attempt_id,
        payload={
            "method_result_sha256": result_artifact.sha256,
            "process_status": method_process.status,
            "stderr_sha256": method_process.stderr_sha256,
            "stdout_sha256": method_process.stdout_sha256,
        },
    )
    # A bounded/non-success method outcome is still a scientific observation.
    # Validate its public input, status, failure mapping, and counter/budget
    # binding independently instead of conflating it with validator failure.
    validator_request = make_validator_request(request, result)
    validator_request_artifact = _create_or_verify_json(
        store,
        _attempt_path(work_id, attempt_id, "validator_request.json"),
        validator_request,
    )
    state = _append_event(
        store,
        state,
        source_snapshot_sha256,
        "validator_started",
        work_unit_id=work_id,
        attempt_id=attempt_id,
        payload={"validator_request_sha256": validator_request_artifact.sha256},
    )
    validator_process = run_worker(
        "validator",
        validator_request,
        worker_modules=worker_modules,
        limits=limits,
        scratch_root=scratch_root,
    )
    if not validator_process.passed or validator_process.timed_out:
        if validator_process.timed_out and validator_process.output is not None:
            state = _append_event(
                store,
                state,
                source_snapshot_sha256,
                "late_result_discarded",
                work_unit_id=work_id,
                attempt_id=attempt_id,
                payload={"phase": "validator"},
            )
        return None, None, state, f"validator_process_{validator_process.status}"
    validator_output = validator_process.output
    if not isinstance(validator_output, dict):
        return None, None, state, "invalid_validator_output"
    validator_output_artifact = _create_or_verify_json(
        store,
        _attempt_path(work_id, attempt_id, "validator_output.json"),
        validator_output,
    )
    if not _validator_replay_matches(
        validator_request,
        validator_output,
        work,
        worker_modules,
        scratch_root,
    ):
        return None, None, state, "validator_replay_mismatch"
    state = _append_event(
        store,
        state,
        source_snapshot_sha256,
        "validator_finished",
        work_unit_id=work_id,
        attempt_id=attempt_id,
        payload={
            "passed": validator_output.get("passed") is True,
            "stderr_sha256": validator_process.stderr_sha256,
            "stdout_sha256": validator_process.stdout_sha256,
            "validator_output_sha256": validator_output_artifact.sha256,
        },
    )
    receipt = build_validation_receipt(
        work,
        request,
        result,
        validator_request,
        validator_output,
        target_pair,
        repo_root=repo_root,
    )
    if receipt.get("passed") is not True:
        _create_or_verify_json(
            store,
            _attempt_path(work_id, attempt_id, "validation_receipt.json"),
            receipt,
        )
        return None, None, state, "validator_disagreement"
    receipt_artifact = _create_or_verify_json(store, _receipt_path(work_id), receipt)
    return receipt, receipt_artifact.sha256, state, None


def _analysis_index(
    campaign_id: str,
    receipts: Mapping[str, tuple[dict[str, Any], str]],
    plan: CampaignPlan,
    target_pairs: Mapping[str, TargetPair],
    store: ArtifactStore,
    state: EventLogReplay,
) -> dict[str, Any]:
    work_by_id = {work["work_unit_id"]: work for work in plan.work_units}
    entries: list[dict[str, Any]] = []
    for work_id, (receipt, digest) in sorted(receipts.items()):
        work = work_by_id.get(work_id)
        identity = work.get("identity") if isinstance(work, Mapping) else None
        if not isinstance(identity, Mapping):
            raise RunnerError(
                "orchestration.analysis_index", "receipt has no campaign work identity"
            )
        target_id = identity.get("public_target_vector_sha256")
        pair = target_pairs.get(target_id)
        if pair is None:
            raise RunnerError(
                "orchestration.analysis_index", "work target has no public authority"
            )
        public = pair.public_payload
        final_event = _final_event_for(state, work_id)
        if final_event is None or not isinstance(final_event.get("attempt_id"), str):
            raise RunnerError(
                "orchestration.analysis_index",
                "final receipt has no authenticated final attempt",
            )
        attempt_id = final_event["attempt_id"]
        request_value = store.read_json(
            _attempt_path(work_id, attempt_id, "method_request.json")
        )
        result_value = store.read_json(
            _attempt_path(work_id, attempt_id, "method_result.json")
        )
        if not isinstance(request_value, dict) or not isinstance(result_value, dict):
            raise RunnerError(
                "orchestration.analysis_index",
                "final method request/result must be canonical objects",
            )
        if (
            result_value.get("result_id") != receipt.get("subject_id")
            or sha256_json(result_value) != receipt.get("subject_sha256")
            or result_value.get("status") != receipt.get("subject_status")
            or result_value.get("method_request_sha256") != sha256_json(request_value)
            or request_value.get("work_unit_id") != work_id
            or request_value.get("attempt_id") != attempt_id
            or request_value.get("budgets") != identity.get("budgets")
        ):
            raise RunnerError(
                "orchestration.analysis_index",
                "final public observation differs from its authenticated chain",
            )
        counters = result_value.get("counters")
        failure = result_value.get("failure")
        if not isinstance(counters, dict) or not (
            failure is None or isinstance(failure, dict)
        ):
            raise RunnerError(
                "orchestration.analysis_index",
                "final public status payload is malformed",
            )
        entries.append(
            {
                "work_unit_id": work_id,
                "validation_id": receipt["validation_id"],
                "validation_receipt_sha256": digest,
                "method_result_id": receipt["subject_id"],
                "method_result_sha256": receipt["subject_sha256"],
                "subject_status": receipt.get("subject_status"),
                "public_target_vector_sha256": target_id,
                "curve_catalog_sha256": identity["curve_catalog_sha256"],
                "curve_fixture_id": identity["curve_fixture_id"],
                "field_bits": public["field_bits"],
                "subgroup_order": public["subgroup_order"],
                "subgroup_order_bits": public["subgroup_order_bits"],
                "method_id": identity["method_id"],
                "algorithm_seed": identity["algorithm_seed"],
                "repetition_ordinal": identity["repetition_ordinal"],
                "method_budgets": deepcopy(request_value["budgets"]),
                "method_status": result_value["status"],
                "method_failure": deepcopy(failure),
                "method_counters": deepcopy(counters),
            }
        )
    return {
        "schema_version": 1,
        "index_kind": "ecdlp_lab_public_analysis_index_v2",
        "campaign_id": campaign_id,
        "entries": entries,
    }


def _validate_plan(plan: CampaignPlan, max_parallel: int, max_retries: int) -> None:
    if type(max_parallel) is not int or max_parallel != 1:
        raise RunnerError(
            "orchestration.parallelism", "P04 smoke requires max_parallel=1"
        )
    if type(max_retries) is not int or not 0 <= max_retries <= 8:
        raise RunnerError(
            "orchestration.retries", "max_retries must be an exact integer in [0,8]"
        )
    ids = [work.get("work_unit_id") for work in plan.work_units]
    if len(ids) != len(set(ids)):
        raise RunnerError(
            "orchestration.work.duplicate", "campaign contains duplicate work identity"
        )
    if plan.campaign.get("expected_work_unit_count") != len(plan.work_units):
        raise RunnerError(
            "orchestration.work.count", "campaign expansion count drifted"
        )


def run_campaign(
    campaign: Mapping[str, Any],
    artifact_root: Path | str,
    *,
    repo_root: Path | str,
    max_parallel: int = 1,
    max_retries: int = DEFAULT_MAX_RETRIES,
) -> RunSummary:
    """Run or resume one fixed, secret-free engineering campaign."""

    root = Path(repo_root)
    if root.is_symlink() or not root.is_dir():
        raise RunnerError("orchestration.repo_root", "repo_root must be a real directory")
    root = root.resolve(strict=True)
    try:
        store = ArtifactStore(artifact_root, forbidden_root=root)
    except StorageError as error:
        raise RunnerError("orchestration.artifact_root", str(error)) from error
    scratch_context: tempfile.TemporaryDirectory[str] | None = None
    try:
        matrix = campaign.get("matrix")
        target_ids = (
            matrix.get("target_vector_sha256s")
            if isinstance(matrix, Mapping)
            else None
        )
        if not isinstance(target_ids, list):
            raise RunnerError(
                "orchestration.target", "campaign target axis must be an array"
            )
        target_pair_values = load_target_pairs(target_ids, repo_root=root)
        target_pairs = {
            pair.public_target_vector_sha256: pair for pair in target_pair_values
        }
        plan = expand_campaign(
            campaign, target_pairs=target_pair_values, repo_root=root
        )
        _validate_plan(plan, max_parallel, max_retries)
        source_snapshot = plan.campaign["provenance"]["source_snapshot_sha256"]
        campaign_id = plan.campaign["campaign_id"]
        scratch_context = tempfile.TemporaryDirectory(prefix="ecdlp-p04-worker-")
        worker_modules = _worker_modules(root)
        scratch_root = Path(scratch_context.name)
        receipts: dict[str, tuple[dict[str, Any], str]] = {}
        lock = store.writer_lock("campaign")
        with lock:
            state = _load_event_state(store, source_snapshot)
            _validate_replay_semantics(state, plan, campaign_id)
            started = [
                event for event in state.events if event["event_type"] == "campaign_started"
            ]
            finished_at_start = [
                event for event in state.events if event["event_type"] == "campaign_finished"
            ]
            if len(finished_at_start) > 1 or (
                finished_at_start and state.events[-1] is not finished_at_start[0]
            ):
                raise RunnerError(
                    "orchestration.resume.finish",
                    "campaign_finished must be the unique terminal event",
                )
            completed_replay = bool(finished_at_start)
            if not started:
                if completed_replay:
                    raise RunnerError(
                        "orchestration.resume.campaign",
                        "completed event log lacks campaign_started",
                    )
                state = _append_event(
                    store,
                    state,
                    source_snapshot,
                    "campaign_started",
                    payload={
                        "campaign_id": campaign_id,
                        "expected_work_unit_count": len(plan.work_units),
                    },
                )
            elif len(started) != 1 or started[0]["payload"].get("campaign_id") != campaign_id:
                raise RunnerError(
                    "orchestration.resume.campaign", "event log belongs to another campaign"
                )
            elif not completed_replay:
                state = _append_event(
                    store,
                    state,
                    source_snapshot,
                    "resume_started",
                    payload={"campaign_id": campaign_id, "existing_event_count": len(state.events)},
                )

            campaign_writer = (
                _verify_existing_json if completed_replay else _create_or_verify_json
            )
            campaign_writer(store, "campaign.json", plan.campaign)
            for base_work in plan.work_units:
                work_id = base_work["work_unit_id"]
                target_id = base_work["identity"]["public_target_vector_sha256"]
                target_pair = target_pairs.get(target_id)
                if target_pair is None:
                    raise RunnerError(
                        "orchestration.target", "work target is not campaign-authorized"
                    )
                campaign_writer(store, _work_path(work_id), base_work)
                recovered = _resume_receipt(
                    store,
                    state,
                    base_work,
                    target_pair,
                    source_snapshot,
                    worker_modules,
                    scratch_root,
                    repo_root=root,
                )
                if recovered is not None:
                    receipt, receipt_hash, state = recovered
                    receipts[work_id] = (receipt, receipt_hash)
                    continue
                if completed_replay:
                    raise RunnerError(
                        "orchestration.resume.finish",
                        "completed campaign lacks a final validated work receipt",
                    )

                last = _last_scheduled_retry(state, work_id)
                next_retry = 0 if last is None else last[0] + 1
                completed = False
                while next_retry <= max_retries:
                    work = retry_work_unit(base_work, next_retry)
                    state = _append_event(
                        store,
                        state,
                        source_snapshot,
                        "work_scheduled",
                        work_unit_id=work_id,
                        attempt_id=work["attempt_id"],
                        payload={"retry_ordinal": next_retry},
                    )
                    receipt, receipt_hash, state, failure = _run_attempt(
                        store,
                        state,
                        work,
                        target_pair,
                        source_snapshot,
                        worker_modules,
                        scratch_root,
                        repo_root=root,
                    )
                    if receipt is not None and receipt_hash is not None:
                        state = _append_event(
                            store,
                            state,
                            source_snapshot,
                            "work_finalized",
                            work_unit_id=work_id,
                            attempt_id=work["attempt_id"],
                            payload={
                                "retry_ordinal": next_retry,
                                "validation_id": receipt["validation_id"],
                                "validation_receipt_sha256": receipt_hash,
                            },
                        )
                        receipts[work_id] = (receipt, receipt_hash)
                        completed = True
                        break
                    state = _append_event(
                        store,
                        state,
                        source_snapshot,
                        "work_failed",
                        work_unit_id=work_id,
                        attempt_id=work["attempt_id"],
                        payload={
                            "failure_code": failure or "unknown_failure",
                            "retry_ordinal": next_retry,
                        },
                    )
                    next_retry += 1
                if not completed:
                    raise RunnerError(
                        "orchestration.work.exhausted",
                        f"work {work_id} exhausted its retry budget",
                    )

            index = _analysis_index(
                campaign_id, receipts, plan, target_pairs, store, state
            )
            index_artifact = campaign_writer(store, PUBLIC_ANALYSIS_INDEX_PATH, index)
            finished = [
                event for event in state.events if event["event_type"] == "campaign_finished"
            ]
            finish_payload = {
                "public_analysis_index_sha256": index_artifact.sha256,
                "validation_receipt_sha256s": sorted(
                    digest for _receipt, digest in receipts.values()
                ),
            }
            if not finished:
                state = _append_event(
                    store,
                    state,
                    source_snapshot,
                    "campaign_finished",
                    payload=finish_payload,
                )
            elif len(finished) != 1 or finished[0]["payload"] != finish_payload:
                raise RunnerError(
                    "orchestration.resume.finish", "campaign completion binding drifted"
                )
    except (
        ArtifactCorrupt,
        EventLogError,
        OrchestrationError,
        OSError,
        ProcessBoundaryError,
        StorageError,
        WriterLockBusy,
    ) as error:
        raise RunnerError("orchestration.boundary", str(error)) from error
    finally:
        store.close()
        if scratch_context is not None:
            scratch_context.cleanup()

    if state.head_sha256 is None:
        raise RunnerError("orchestration.events", "completed campaign has no event head")
    return RunSummary(
        campaign_id=campaign_id,
        completed_work_unit_ids=tuple(sorted(receipts)),
        validation_receipt_sha256s=tuple(
            sorted(digest for _receipt, digest in receipts.values())
        ),
        public_analysis_index_sha256=index_artifact.sha256,
        event_chain_head_sha256=state.head_sha256,
    )


__all__ = [
    "DEFAULT_MAX_RETRIES",
    "EVENT_LOG_PATH",
    "METHOD_WORKER_MODULE",
    "PUBLIC_ANALYSIS_INDEX_PATH",
    "RunSummary",
    "RunnerError",
    "VALIDATOR_WORKER_MODULE",
    "run_campaign",
]
