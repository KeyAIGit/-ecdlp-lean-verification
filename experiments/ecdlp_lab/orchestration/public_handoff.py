"""Fail-closed public P04C -> P05 analysis trust handoff.

The loader may inspect the trusted coordinator artifacts and committed target
authority while verifying the chain.  It returns only the exact public
observation projection retained in ``public_analysis_index.json``.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping

from experiments.ecdlp_lab.core.canonical import is_sha256, sha256_json
from experiments.ecdlp_lab.core.catalog_registry import trusted_catalog_sha256s
from experiments.ecdlp_lab.core.contracts import (
    ContractIssue,
    ValidationContext,
    validate_cross_record_bundle,
)
from experiments.ecdlp_lab.core.target_registry import TargetPair, load_target_pairs

from .events import EventLogError, replay_event_bytes
from .model import OrchestrationError
from .records import build_validation_receipt, expand_campaign, retry_work_unit
from .storage import ArtifactStore, StorageError


EVENT_LOG_PATH = "events.jsonl"
PUBLIC_ANALYSIS_INDEX_PATH = "public_analysis_index.json"
INDEX_KIND = "ecdlp_lab_public_analysis_index_v2"

_INDEX_KEYS = frozenset({"schema_version", "index_kind", "campaign_id", "entries"})
_ENTRY_KEYS = frozenset(
    {
        "work_unit_id",
        "validation_id",
        "validation_receipt_sha256",
        "method_result_id",
        "method_result_sha256",
        "subject_status",
        "public_target_vector_sha256",
        "curve_catalog_sha256",
        "curve_fixture_id",
        "field_bits",
        "subgroup_order",
        "subgroup_order_bits",
        "method_id",
        "algorithm_seed",
        "repetition_ordinal",
        "method_budgets",
        "method_status",
        "method_failure",
        "method_counters",
    }
)
_FORBIDDEN_KEYS = frozenset(
    {
        "candidate_scalar",
        "derivation_seed",
        "expected_scalar",
        "generator",
        "private_payload",
        "private_target",
        "private_target_id",
        "private_target_path",
        "private_target_receipt_sha256",
        "private_target_vector_sha256",
        "target",
    }
)
_EVENT_PAYLOAD_KEYS = {
    "campaign_started": frozenset({"campaign_id", "expected_work_unit_count"}),
    "resume_started": frozenset({"campaign_id", "existing_event_count"}),
    "work_scheduled": frozenset({"retry_ordinal"}),
    "method_started": frozenset(
        {"method_request_sha256", "method_worker_request_sha256"}
    ),
    "method_finished": frozenset(
        {"method_result_sha256", "process_status", "stderr_sha256", "stdout_sha256"}
    ),
    "method_timeout": frozenset({"retry_ordinal"}),
    "validator_started": frozenset({"validator_request_sha256"}),
    "validator_finished": frozenset(
        {"passed", "stderr_sha256", "stdout_sha256", "validator_output_sha256"}
    ),
    "work_finalized": frozenset(
        {"retry_ordinal", "validation_id", "validation_receipt_sha256"}
    ),
    "work_failed": frozenset({"failure_code", "retry_ordinal"}),
    "late_result_discarded": frozenset({"phase"}),
    "campaign_finished": frozenset(
        {"public_analysis_index_sha256", "validation_receipt_sha256s"}
    ),
}


class PublicHandoffError(ValueError):
    """The retained campaign cannot authorize a public analysis input."""


@dataclass(frozen=True)
class VerifiedPublicAnalysisHandoff:
    campaign_id: str
    _campaign_provenance: dict[str, Any] = field(repr=False)
    _entries: tuple[dict[str, Any], ...] = field(repr=False)
    _validation_records: tuple[dict[str, Any], ...] = field(repr=False)
    _known_catalog_sha256s: frozenset[str] = field(repr=False)
    _known_target_vector_sha256s: frozenset[str] = field(repr=False)
    validation_receipt_sha256s: frozenset[str]
    index_sha256: str
    event_head_sha256: str

    @property
    def entries(self) -> tuple[dict[str, Any], ...]:
        return tuple(deepcopy(entry) for entry in self._entries)

    @property
    def campaign_provenance(self) -> dict[str, Any]:
        return deepcopy(self._campaign_provenance)

    def as_analysis_process_payload(self) -> dict[str, Any]:
        """Return the only payload authorized to cross into P05 analysis."""

        return {
            "schema_version": 1,
            "handoff_kind": "ecdlp_lab_verified_public_analysis_handoff_v1",
            "campaign_id": self.campaign_id,
            "campaign_provenance": self.campaign_provenance,
            "validation_receipt_sha256s": sorted(
                self.validation_receipt_sha256s
            ),
            "public_analysis_index_sha256": self.index_sha256,
            "event_chain_head_sha256": self.event_head_sha256,
            "entries": list(self.entries),
        }

    def validate_analysis_summary(
        self,
        summary: Mapping[str, Any],
        *,
        repo_root: Path | str,
    ) -> tuple[ContractIssue, ...]:
        """Validate a P05 result without exposing decisive retained records."""

        if not isinstance(summary, Mapping):
            raise PublicHandoffError("analysis summary must be an object")
        record = deepcopy(dict(summary))
        linked = record.get("input_validation_receipt_sha256s")
        if (
            record.get("campaign_id") != self.campaign_id
            or record.get("provenance") != self._campaign_provenance
            or not isinstance(linked, list)
            or linked != sorted(self.validation_receipt_sha256s)
        ):
            raise PublicHandoffError(
                "analysis must bind the exact campaign provenance and complete receipt set"
            )
        context = ValidationContext.from_records(
            self._validation_records,
            repo_root=repo_root,
            known_catalog_sha256s=self._known_catalog_sha256s,
            known_target_vector_sha256s=self._known_target_vector_sha256s,
            known_validation_receipt_sha256s=self.validation_receipt_sha256s,
            verify_artifacts=False,
        )
        issues = validate_cross_record_bundle(
            (*self._validation_records, record), context
        )
        return tuple(issues)


def _object(value: Any, keys: frozenset[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or frozenset(value) != keys:
        raise PublicHandoffError(f"{label} key set drifted")
    return value


def _attempt_path(work_id: str, attempt_id: str, filename: str) -> str:
    return f"attempts/{work_id}/{attempt_id}/{filename}"


def _attempt_event(
    events: tuple[dict[str, Any], ...],
    event_type: str,
    work_id: str,
    attempt_id: str,
) -> dict[str, Any]:
    matches = [
        event
        for event in events
        if event["event_type"] == event_type
        and event.get("work_unit_id") == work_id
        and event.get("attempt_id") == attempt_id
    ]
    if len(matches) != 1:
        raise PublicHandoffError(f"final attempt requires exactly one {event_type} event")
    return matches[0]


def _walk_forbidden(value: Any) -> None:
    stack = [value]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            for key, child in current.items():
                folded = key.casefold()
                if folded in _FORBIDDEN_KEYS or folded.startswith("private_target"):
                    raise PublicHandoffError("public handoff contains a private field")
                stack.append(child)
        elif isinstance(current, list):
            stack.extend(current)


def _final_events(events: Iterable[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    finals: dict[str, dict[str, Any]] = {}
    for event in events:
        if event["event_type"] != "work_finalized":
            continue
        work_id = event.get("work_unit_id")
        if not is_sha256(work_id) or work_id in finals:
            raise PublicHandoffError("work finalization is missing or duplicated")
        finals[work_id] = event
    return finals


def _validate_event_semantics(
    events: tuple[dict[str, Any], ...],
    plan_by_work: Mapping[str, Mapping[str, Any]],
    campaign_id: str,
) -> dict[str, dict[str, Any]]:
    scheduled: dict[str, list[str]] = {work_id: [] for work_id in plan_by_work}
    finalized: set[str] = set()
    for event in events:
        event_type = event["event_type"]
        payload = event["payload"]
        if frozenset(payload) != _EVENT_PAYLOAD_KEYS[event_type]:
            raise PublicHandoffError(f"{event_type} payload key set drifted")
        work_id = event.get("work_unit_id")
        attempt_id = event.get("attempt_id")
        if event_type in {"campaign_started", "resume_started", "campaign_finished"}:
            if work_id is not None or attempt_id is not None:
                raise PublicHandoffError("campaign event binds a work or attempt")
            if event_type != "campaign_finished" and payload.get("campaign_id") != campaign_id:
                raise PublicHandoffError("campaign event identity drifted")
            if event_type == "resume_started" and payload.get("existing_event_count") != event["sequence"]:
                raise PublicHandoffError("resume event count drifted")
            continue
        if work_id not in plan_by_work or work_id in finalized:
            raise PublicHandoffError("work event is unknown or follows finalization")
        if event_type == "work_scheduled":
            retry = payload.get("retry_ordinal")
            if type(retry) is not int or retry != len(scheduled[work_id]):
                raise PublicHandoffError("scheduled retry ordinal is not contiguous")
            expected = retry_work_unit(plan_by_work[work_id], retry)["attempt_id"]
            if attempt_id != expected:
                raise PublicHandoffError("scheduled attempt identity drifted")
            scheduled[work_id].append(expected)
            continue
        if not is_sha256(attempt_id) or attempt_id not in scheduled[work_id]:
            raise PublicHandoffError("work event has no authenticated schedule")
        if event_type in {"work_finalized", "work_failed"}:
            retry = payload.get("retry_ordinal")
            if (
                type(retry) is not int
                or retry < 0
                or retry >= len(scheduled[work_id])
                or scheduled[work_id][retry] != attempt_id
            ):
                raise PublicHandoffError("terminal work retry binding drifted")
        if event_type == "work_finalized":
            finalized.add(work_id)
    finals = _final_events(events)
    if set(finals) != set(plan_by_work):
        raise PublicHandoffError("final events do not exactly cover campaign work")
    return finals


def _expected_entry(
    work: Mapping[str, Any],
    request: Mapping[str, Any],
    result: Mapping[str, Any],
    receipt: Mapping[str, Any],
    receipt_sha256: str,
    pair: TargetPair,
) -> dict[str, Any]:
    identity = work["identity"]
    public = pair.public_payload
    return {
        "work_unit_id": work["work_unit_id"],
        "validation_id": receipt["validation_id"],
        "validation_receipt_sha256": receipt_sha256,
        "method_result_id": result["result_id"],
        "method_result_sha256": sha256_json(dict(result)),
        "subject_status": receipt.get("subject_status"),
        "public_target_vector_sha256": identity["public_target_vector_sha256"],
        "curve_catalog_sha256": identity["curve_catalog_sha256"],
        "curve_fixture_id": identity["curve_fixture_id"],
        "field_bits": public["field_bits"],
        "subgroup_order": public["subgroup_order"],
        "subgroup_order_bits": public["subgroup_order_bits"],
        "method_id": identity["method_id"],
        "algorithm_seed": identity["algorithm_seed"],
        "repetition_ordinal": identity["repetition_ordinal"],
        "method_budgets": deepcopy(request["budgets"]),
        "method_status": result["status"],
        "method_failure": deepcopy(result["failure"]),
        "method_counters": deepcopy(result["counters"]),
    }


def load_verified_public_analysis_handoff(
    artifact_root: Path | str,
    campaign: Mapping[str, Any],
    *,
    repo_root: Path | str,
    expected_summary: Mapping[str, Any] | Any,
) -> VerifiedPublicAnalysisHandoff:
    """Verify a completed P04C campaign and expose only public observations.

    ``expected_summary`` is the out-of-band value returned by ``run_campaign``
    (or its exact ``as_dict()`` form).  Requiring it prevents a writable
    artifact root from self-authorizing a recomputed event chain.
    """

    root = Path(repo_root)
    artifacts = Path(artifact_root)
    if hasattr(expected_summary, "as_dict"):
        expected_summary = expected_summary.as_dict()
    if not isinstance(expected_summary, Mapping):
        raise PublicHandoffError("expected run summary authority is required")
    if (
        not root.is_dir()
        or root.is_symlink()
        or not artifacts.is_absolute()
        or not artifacts.is_dir()
        or artifacts.is_symlink()
    ):
        raise PublicHandoffError("repository and artifact roots must be existing real directories")
    root = root.resolve(strict=True)
    matrix = campaign.get("matrix")
    target_ids = matrix.get("target_vector_sha256s") if isinstance(matrix, Mapping) else None
    if not isinstance(target_ids, list):
        raise PublicHandoffError("campaign target axis is malformed")
    try:
        pairs = load_target_pairs(target_ids, repo_root=root)
        pair_by_id = {pair.public_target_vector_sha256: pair for pair in pairs}
        plan = expand_campaign(campaign, target_pairs=pairs, repo_root=root)
        source = plan.campaign["provenance"]["source_snapshot_sha256"]
        campaign_id = plan.campaign["campaign_id"]
        with ArtifactStore(
            artifacts, forbidden_root=root, create_root=False
        ) as store:
            event_bytes = store.read_bytes(EVENT_LOG_PATH)
            replay = replay_event_bytes(
                event_bytes,
                expected_source_snapshot_sha256=source,
            )
            if not replay.events or replay.head_sha256 is None:
                raise PublicHandoffError("campaign event chain is empty")
            plan_by_work = {work["work_unit_id"]: work for work in plan.work_units}
            starts = [event for event in replay.events if event["event_type"] == "campaign_started"]
            finishes = [event for event in replay.events if event["event_type"] == "campaign_finished"]
            if (
                len(starts) != 1
                or replay.events[0] is not starts[0]
                or starts[0]["payload"].get("campaign_id") != campaign_id
                or starts[0]["payload"].get("expected_work_unit_count") != len(plan.work_units)
                or len(finishes) != 1
                or replay.events[-1] is not finishes[0]
            ):
                raise PublicHandoffError("campaign start/finish event binding drifted")
            final_by_work = _validate_event_semantics(
                replay.events, plan_by_work, campaign_id
            )
            index = _object(
                store.read_json(PUBLIC_ANALYSIS_INDEX_PATH), _INDEX_KEYS, "public index"
            )
            if (
                index["schema_version"] != 1
                or index["index_kind"] != INDEX_KIND
                or index["campaign_id"] != campaign_id
            ):
                raise PublicHandoffError("public index protocol or campaign drifted")
            index_sha256 = sha256_json(index)
            finish_payload = finishes[0]["payload"]
            if finish_payload.get("public_analysis_index_sha256") != index_sha256:
                raise PublicHandoffError("terminal event does not bind the public index")

            index_entries = index.get("entries")
            if not isinstance(index_entries, list):
                raise PublicHandoffError("public index entries must be an array")
            for entry in index_entries:
                _object(entry, _ENTRY_KEYS, "public index entry")
            if [entry["work_unit_id"] for entry in index_entries] != sorted(
                entry["work_unit_id"] for entry in index_entries
            ):
                raise PublicHandoffError("public index entries must be sorted")
            _walk_forbidden(index)

            if len(index_entries) != len(plan_by_work):
                raise PublicHandoffError("public index does not exactly cover campaign work")

            bundle_records: list[dict[str, Any]] = [dict(plan.campaign)]
            bundle_records.extend(
                record for pair in pairs for record in (pair.public_record, pair.private_record)
            )
            expected_entries: list[dict[str, Any]] = []
            receipt_digests: list[str] = []
            for work_id in sorted(plan_by_work):
                base_work = plan_by_work[work_id]
                final = final_by_work[work_id]
                retry = final["payload"].get("retry_ordinal")
                attempt_id = final.get("attempt_id")
                if type(retry) is not int or retry < 0 or not is_sha256(attempt_id):
                    raise PublicHandoffError("final event retry/attempt binding is malformed")
                work = retry_work_unit(base_work, retry)
                if work["attempt_id"] != attempt_id:
                    raise PublicHandoffError("final attempt identity drifted")
                retained_work = store.read_json(f"work_units/{work_id}.json")
                if retained_work != base_work:
                    raise PublicHandoffError("retained base work drifted")
                request = store.read_json(_attempt_path(work_id, attempt_id, "method_request.json"))
                result = store.read_json(_attempt_path(work_id, attempt_id, "method_result.json"))
                validator_request = store.read_json(
                    _attempt_path(work_id, attempt_id, "validator_request.json")
                )
                validator_output = store.read_json(
                    _attempt_path(work_id, attempt_id, "validator_output.json")
                )
                receipt = store.read_json(f"receipts/{work_id}.json")
                if not all(
                    isinstance(item, dict)
                    for item in (
                        request,
                        result,
                        validator_request,
                        validator_output,
                        receipt,
                    )
                ):
                    raise PublicHandoffError("retained public records must be objects")
                receipt_sha256 = sha256_json(receipt)
                method_started = _attempt_event(
                    replay.events, "method_started", work_id, attempt_id
                )
                method_finished = _attempt_event(
                    replay.events, "method_finished", work_id, attempt_id
                )
                validator_started = _attempt_event(
                    replay.events, "validator_started", work_id, attempt_id
                )
                validator_finished = _attempt_event(
                    replay.events, "validator_finished", work_id, attempt_id
                )
                if (
                    final["payload"].get("validation_id") != receipt.get("validation_id")
                    or final["payload"].get("validation_receipt_sha256") != receipt_sha256
                    or result.get("method_request_sha256") != sha256_json(request)
                    or receipt.get("subject_id") != result.get("result_id")
                    or receipt.get("subject_sha256") != sha256_json(result)
                    or receipt.get("subject_status") != result.get("status")
                    or receipt.get("passed") is not True
                    or request.get("work_unit_id") != work_id
                    or request.get("attempt_id") != attempt_id
                    or request.get("budgets") != work["identity"]["budgets"]
                    or method_started["payload"].get("method_request_sha256")
                    != sha256_json(request)
                    or method_finished["payload"].get("method_result_sha256")
                    != sha256_json(result)
                    or validator_started["payload"].get("validator_request_sha256")
                    != sha256_json(validator_request)
                    or validator_finished["payload"].get("validator_output_sha256")
                    != sha256_json(validator_output)
                ):
                    raise PublicHandoffError("retained result/receipt chain drifted")
                pair = pair_by_id.get(work["identity"]["public_target_vector_sha256"])
                if pair is None:
                    raise PublicHandoffError("work target lacks committed authority")
                expected_receipt = build_validation_receipt(
                    work,
                    request,
                    result,
                    validator_request,
                    validator_output,
                    pair,
                    repo_root=root,
                )
                if receipt != expected_receipt:
                    raise PublicHandoffError(
                        "retained validation receipt differs from independent reconstruction"
                    )
                expected_entries.append(
                    _expected_entry(work, request, result, receipt, receipt_sha256, pair)
                )
                receipt_digests.append(receipt_sha256)
                bundle_records.extend((work, request, result, receipt))

            if index_entries != expected_entries:
                raise PublicHandoffError("public index differs from retained authenticated records")
            if finish_payload.get("validation_receipt_sha256s") != sorted(receipt_digests):
                raise PublicHandoffError("terminal event receipt set drifted")
            known_catalogs = trusted_catalog_sha256s(repo_root=root)
            context = ValidationContext.from_records(
                bundle_records,
                repo_root=root,
                known_catalog_sha256s=known_catalogs,
                known_target_vector_sha256s=target_ids,
                known_validation_receipt_sha256s=receipt_digests,
                verify_artifacts=False,
            )
            issues = validate_cross_record_bundle(bundle_records, context)
            if issues:
                first = issues[0]
                raise PublicHandoffError(
                    f"retained bundle failed contract validation: {first.code} {first.path}"
                )
            expected_summary_projection = {
                "schema_version": 1,
                "summary_kind": "ecdlp_lab_campaign_run_summary_v1",
                "campaign_id": campaign_id,
                "completed_work_unit_ids": sorted(plan_by_work),
                "validation_receipt_sha256s": sorted(receipt_digests),
                "public_analysis_index_sha256": index_sha256,
                "event_chain_head_sha256": replay.head_sha256,
                "passed": True,
            }
            if dict(expected_summary) != expected_summary_projection:
                raise PublicHandoffError("out-of-band run summary authority drifted")
            if store.read_bytes(EVENT_LOG_PATH) != event_bytes:
                raise PublicHandoffError("event log changed during handoff verification")
    except PublicHandoffError:
        raise
    except (
        EventLogError,
        MemoryError,
        OrchestrationError,
        RecursionError,
        StorageError,
        OSError,
        TypeError,
        ValueError,
    ) as error:
        raise PublicHandoffError(f"public handoff verification failed: {error}") from error

    assert replay.head_sha256 is not None
    return VerifiedPublicAnalysisHandoff(
        campaign_id=campaign_id,
        _campaign_provenance=deepcopy(plan.campaign["provenance"]),
        _entries=tuple(deepcopy(index_entries)),
        _validation_records=tuple(deepcopy(bundle_records)),
        _known_catalog_sha256s=frozenset(known_catalogs),
        _known_target_vector_sha256s=frozenset(target_ids),
        validation_receipt_sha256s=frozenset(receipt_digests),
        index_sha256=index_sha256,
        event_head_sha256=replay.head_sha256,
    )


__all__ = [
    "INDEX_KIND",
    "PublicHandoffError",
    "VerifiedPublicAnalysisHandoff",
    "load_verified_public_analysis_handoff",
]
