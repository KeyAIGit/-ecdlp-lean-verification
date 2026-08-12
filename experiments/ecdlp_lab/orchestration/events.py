"""Pure validation for deterministic hash-chained orchestration events.

The chain is a tamper-evident replay structure.  It does not pretend that an
ordinary filesystem is append-only.  Filesystem access belongs exclusively to
``ArtifactStore``; this module accepts bytes and returns validated state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from experiments.ecdlp_lab.core.canonical import (
    canonical_json_bytes,
    is_sha256,
    sha256_json,
    strict_loads,
)
EVENT_SCHEMA_VERSION = 1
EVENT_KIND = "ecdlp_lab_orchestration_event_v1"
DEFAULT_EVENT_LOG = "events.jsonl"
MAX_EVENT_LOG_BYTES = 8 * 1024 * 1024
MAX_EVENT_BYTES = 256 * 1024
MAX_EVENTS = 100_000

EVENT_TYPES = frozenset(
    {
        "campaign_started",
        "resume_started",
        "work_scheduled",
        "method_started",
        "method_finished",
        "method_timeout",
        "validator_started",
        "validator_finished",
        "work_finalized",
        "work_failed",
        "late_result_discarded",
        "campaign_finished",
    }
)

_EVENT_KEYS = frozenset(
    {
        "schema_version",
        "event_kind",
        "sequence",
        "previous_event_sha256",
        "source_snapshot_sha256",
        "event_type",
        "work_unit_id",
        "attempt_id",
        "payload",
        "event_sha256",
    }
)

_FORBIDDEN_EVENT_KEYS = frozenset(
    {
        "credential",
        "derivation_seed",
        "expected_scalar",
        "private_payload",
        "private_target",
        "private_target_path",
        "secret",
        "target_derivation_seed",
    }
)


def _is_forbidden_event_key(key: str) -> bool:
    folded = key.casefold()
    return folded in _FORBIDDEN_EVENT_KEYS or folded.startswith("private_target")


class EventLogError(ValueError):
    """A log, lock, or create-only artifact violated the replay contract."""


@dataclass(frozen=True)
class EventLogReplay:
    events: tuple[dict[str, Any], ...]
    head_sha256: str | None
    source_snapshot_sha256: str | None

    @property
    def finalized_work_unit_ids(self) -> frozenset[str]:
        return frozenset(
            event["work_unit_id"]
            for event in self.events
            if event["event_type"] == "work_finalized"
            and isinstance(event["work_unit_id"], str)
        )

    @property
    def failed_work_unit_ids(self) -> frozenset[str]:
        return frozenset(
            event["work_unit_id"]
            for event in self.events
            if event["event_type"] == "work_failed"
            and isinstance(event["work_unit_id"], str)
        )


def _exact_nonnegative(value: Any, name: str) -> int:
    if type(value) is not int or value < 0:
        raise EventLogError(f"{name} must be a nonnegative exact integer")
    return value


def _optional_sha256(value: Any, name: str) -> str | None:
    if value is None:
        return None
    if not is_sha256(value):
        raise EventLogError(f"{name} must be null or a lowercase SHA-256")
    return value


def _json_object(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise EventLogError(f"{name} must be a JSON object")
    # Canonical encoding is also the strict-domain check: no floats, custom
    # objects, non-string keys, or non-JSON containers can enter the chain.
    canonical_json_bytes(value)
    stack: list[Any] = [value]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            for key, child in current.items():
                if _is_forbidden_event_key(key):
                    raise EventLogError(f"{name} contains a private or credential field")
                stack.append(child)
        elif isinstance(current, list):
            stack.extend(current)
    return dict(value)


def _event_projection(event: Mapping[str, Any]) -> dict[str, Any]:
    return {key: event[key] for key in _EVENT_KEYS if key != "event_sha256"}


def validate_event(
    event: Any,
    *,
    expected_sequence: int | None = None,
    expected_previous: str | None | object = ...,
    expected_source_snapshot_sha256: str | None = None,
) -> dict[str, Any]:
    if not isinstance(event, dict) or set(event) != _EVENT_KEYS:
        raise EventLogError("event must contain exactly the frozen event fields")
    if event.get("schema_version") != EVENT_SCHEMA_VERSION:
        raise EventLogError("event schema_version must be 1")
    if event.get("event_kind") != EVENT_KIND:
        raise EventLogError("unknown event_kind")
    sequence = _exact_nonnegative(event.get("sequence"), "event sequence")
    if expected_sequence is not None and sequence != expected_sequence:
        raise EventLogError("event sequence is not contiguous")
    previous = _optional_sha256(
        event.get("previous_event_sha256"), "previous_event_sha256"
    )
    if expected_previous is not ... and previous != expected_previous:
        raise EventLogError("event previous digest does not match the chain head")
    source = event.get("source_snapshot_sha256")
    if not is_sha256(source):
        raise EventLogError("source_snapshot_sha256 must be a lowercase SHA-256")
    if (
        expected_source_snapshot_sha256 is not None
        and source != expected_source_snapshot_sha256
    ):
        raise EventLogError("event source snapshot differs from the trusted source")
    if event.get("event_type") not in EVENT_TYPES:
        raise EventLogError("unknown event_type")
    work_unit_id = _optional_sha256(event.get("work_unit_id"), "work_unit_id")
    attempt_id = _optional_sha256(event.get("attempt_id"), "attempt_id")
    if event["event_type"] in {
        "work_scheduled",
        "method_started",
        "method_finished",
        "method_timeout",
        "validator_started",
        "validator_finished",
        "work_finalized",
        "work_failed",
        "late_result_discarded",
    } and work_unit_id is None:
        raise EventLogError("work event requires work_unit_id")
    if event["event_type"] in {
        "method_started",
        "method_finished",
        "method_timeout",
        "validator_started",
        "validator_finished",
        "late_result_discarded",
    } and attempt_id is None:
        raise EventLogError("attempt event requires attempt_id")
    _json_object(event.get("payload"), "event payload")
    digest = event.get("event_sha256")
    if not is_sha256(digest) or digest != sha256_json(_event_projection(event)):
        raise EventLogError("event_sha256 does not match the canonical event projection")
    return dict(event)


def make_event(
    *,
    sequence: int,
    previous_event_sha256: str | None,
    source_snapshot_sha256: str,
    event_type: str,
    work_unit_id: str | None = None,
    attempt_id: str | None = None,
    payload: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    event = {
        "schema_version": EVENT_SCHEMA_VERSION,
        "event_kind": EVENT_KIND,
        "sequence": sequence,
        "previous_event_sha256": previous_event_sha256,
        "source_snapshot_sha256": source_snapshot_sha256,
        "event_type": event_type,
        "work_unit_id": work_unit_id,
        "attempt_id": attempt_id,
        "payload": dict(payload or {}),
    }
    event["event_sha256"] = sha256_json(event)
    return validate_event(
        event,
        expected_sequence=sequence,
        expected_previous=previous_event_sha256,
        expected_source_snapshot_sha256=source_snapshot_sha256,
    )


def replay_event_bytes(
    raw: bytes,
    *,
    expected_source_snapshot_sha256: str | None = None,
    max_bytes: int = MAX_EVENT_LOG_BYTES,
    max_events: int = MAX_EVENTS,
) -> EventLogReplay:
    """Replay already-confined bytes, for use with :class:`ArtifactStore`."""

    if not isinstance(raw, bytes):
        raise EventLogError("event log payload must be bytes")
    if type(max_bytes) is not int or max_bytes < 1:
        raise EventLogError("max_bytes must be a positive exact integer")
    if type(max_events) is not int or max_events < 1:
        raise EventLogError("max_events must be a positive exact integer")
    if len(raw) > max_bytes:
        raise EventLogError("event log exceeds the replay byte limit")
    if not raw:
        return EventLogReplay((), None, expected_source_snapshot_sha256)
    if not raw.endswith(b"\n"):
        raise EventLogError("event log has a torn final JSONL record")
    lines = raw.splitlines()
    if len(lines) > max_events:
        raise EventLogError("event log exceeds the replay event limit")
    events: list[dict[str, Any]] = []
    previous: str | None = None
    source = expected_source_snapshot_sha256
    finalized: set[str] = set()
    for sequence, line in enumerate(lines):
        if not line or len(line) > MAX_EVENT_BYTES:
            raise EventLogError("event log contains an empty or oversized record")
        try:
            parsed = strict_loads(line, label=f"event log line {sequence + 1}")
        except (TypeError, ValueError) as error:
            raise EventLogError(str(error)) from error
        if canonical_json_bytes(parsed) != line:
            raise EventLogError("event log records must use exact canonical JSON bytes")
        event = validate_event(
            parsed,
            expected_sequence=sequence,
            expected_previous=previous,
            expected_source_snapshot_sha256=source,
        )
        if source is None:
            source = event["source_snapshot_sha256"]
        if event["event_type"] == "work_finalized":
            work_unit_id = event["work_unit_id"]
            if work_unit_id in finalized:
                raise EventLogError("work unit has more than one finalization event")
            finalized.add(work_unit_id)
        previous = event["event_sha256"]
        events.append(event)
    return EventLogReplay(tuple(events), previous, source)


def event_types(events: Iterable[Mapping[str, Any]]) -> tuple[str, ...]:
    return tuple(str(event.get("event_type")) for event in events)


__all__ = [
    "DEFAULT_EVENT_LOG",
    "EVENT_KIND",
    "EVENT_TYPES",
    "EventLogError",
    "EventLogReplay",
    "event_types",
    "make_event",
    "replay_event_bytes",
    "validate_event",
]
