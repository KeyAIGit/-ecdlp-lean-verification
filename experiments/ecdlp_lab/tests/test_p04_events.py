from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from experiments.ecdlp_lab.core.canonical import canonical_json_bytes
from experiments.ecdlp_lab.orchestration import events
from experiments.ecdlp_lab.orchestration.events import (
    EventLogError,
    make_event,
    replay_event_bytes,
)
from experiments.ecdlp_lab.orchestration.storage import ArtifactStore


SOURCE = "1" * 64
WORK = "2" * 64
ATTEMPT = "3" * 64


def encoded(*records: dict[str, object]) -> bytes:
    return b"".join(canonical_json_bytes(record) + b"\n" for record in records)


class P04EventLogTests(unittest.TestCase):
    def test_artifact_store_round_trip_and_resume_head(self) -> None:
        with tempfile.TemporaryDirectory() as directory, ArtifactStore(directory) as store:
            first = make_event(
                sequence=0,
                previous_event_sha256=None,
                source_snapshot_sha256=SOURCE,
                event_type="campaign_started",
                payload={"campaign_id": "4" * 64},
            )
            store.append_jsonl("events.jsonl", first, lock_name="events")
            second = make_event(
                sequence=1,
                previous_event_sha256=first["event_sha256"],
                source_snapshot_sha256=SOURCE,
                event_type="method_started",
                work_unit_id=WORK,
                attempt_id=ATTEMPT,
                payload={"request_sha256": "5" * 64},
            )
            store.append_jsonl("events.jsonl", second, lock_name="events")
            replay = replay_event_bytes(
                store.read_bytes("events.jsonl"),
                expected_source_snapshot_sha256=SOURCE,
            )
            self.assertEqual(len(replay.events), 2)
            self.assertEqual(replay.head_sha256, second["event_sha256"])
            third = make_event(
                sequence=2,
                previous_event_sha256=replay.head_sha256,
                source_snapshot_sha256=SOURCE,
                event_type="campaign_finished",
                payload={"completed": 0},
            )
            store.append_jsonl("events.jsonl", third, lock_name="events")
            self.assertEqual(
                replay_event_bytes(store.read_bytes("events.jsonl")).head_sha256,
                third["event_sha256"],
            )

    def test_torn_tampered_and_stale_bytes_fail_closed(self) -> None:
        event = make_event(
            sequence=0,
            previous_event_sha256=None,
            source_snapshot_sha256=SOURCE,
            event_type="campaign_started",
        )
        original = encoded(event)
        with self.assertRaisesRegex(EventLogError, "torn"):
            replay_event_bytes(original[:-1])

        tampered = dict(event)
        tampered["payload"] = {"changed": True}
        with self.assertRaisesRegex(EventLogError, "event_sha256"):
            replay_event_bytes(encoded(tampered))

        with self.assertRaisesRegex(EventLogError, "trusted source"):
            replay_event_bytes(
                original, expected_source_snapshot_sha256="9" * 64
            )

    def test_noncanonical_json_and_private_payload_are_rejected(self) -> None:
        for payload in (
            {"nested": {"expected_scalar": 7}},
            {"private_target_receipt_sha256": "8" * 64},
        ):
            with self.subTest(payload=payload), self.assertRaisesRegex(
                EventLogError, "private"
            ):
                make_event(
                    sequence=0,
                    previous_event_sha256=None,
                    source_snapshot_sha256=SOURCE,
                    event_type="method_started",
                    work_unit_id=WORK,
                    attempt_id=ATTEMPT,
                    payload=payload,
                )

        event = make_event(
            sequence=0,
            previous_event_sha256=None,
            source_snapshot_sha256=SOURCE,
            event_type="campaign_started",
        )
        noncanonical = json.dumps(event, sort_keys=True).encode("utf-8") + b"\n"
        with self.assertRaisesRegex(EventLogError, "canonical"):
            replay_event_bytes(noncanonical)

    def test_duplicate_finalization_is_rejected_on_pure_replay(self) -> None:
        first = make_event(
            sequence=0,
            previous_event_sha256=None,
            source_snapshot_sha256=SOURCE,
            event_type="work_finalized",
            work_unit_id=WORK,
        )
        second = make_event(
            sequence=1,
            previous_event_sha256=first["event_sha256"],
            source_snapshot_sha256=SOURCE,
            event_type="work_finalized",
            work_unit_id=WORK,
        )
        with self.assertRaisesRegex(EventLogError, "more than one"):
            replay_event_bytes(encoded(first, second))

    def test_replay_limits_are_exact_and_bounded(self) -> None:
        event = make_event(
            sequence=0,
            previous_event_sha256=None,
            source_snapshot_sha256=SOURCE,
            event_type="campaign_started",
        )
        raw = encoded(event)
        with self.assertRaisesRegex(EventLogError, "byte limit"):
            replay_event_bytes(raw, max_bytes=len(raw) - 1)
        for invalid in (0, True):
            with self.subTest(invalid=invalid), self.assertRaises(EventLogError):
                replay_event_bytes(raw, max_events=invalid)

    def test_events_exports_no_direct_filesystem_writer(self) -> None:
        for name in (
            "HashChainEventLog",
            "atomic_create_bytes",
            "atomic_create_json",
            "replay_event_log",
        ):
            self.assertFalse(hasattr(events, name), name)


if __name__ == "__main__":
    unittest.main()

