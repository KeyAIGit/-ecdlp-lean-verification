from __future__ import annotations

from copy import deepcopy
import tempfile
import unittest
from pathlib import Path

from experiments.ecdlp_lab.core.canonical import canonical_json_bytes, load_json
from experiments.ecdlp_lab.orchestration.events import make_event, replay_event_bytes
from experiments.ecdlp_lab.orchestration.provenance import (
    P04_BASE_SOURCE_COMMIT,
    build_campaign_provenance,
)
from experiments.ecdlp_lab.orchestration.public_handoff import (
    PublicHandoffError,
    load_verified_public_analysis_handoff,
)
from experiments.ecdlp_lab.orchestration.records import SMOKE_CAMPAIGN_PATH
from experiments.ecdlp_lab.orchestration.runner import run_campaign


REPO_ROOT = Path(__file__).resolve().parents[3]


def current_campaign() -> dict[str, object]:
    campaign = load_json(REPO_ROOT / SMOKE_CAMPAIGN_PATH)
    campaign["provenance"] = build_campaign_provenance(
        config_sha256=campaign["campaign_id"],
        source_commit=P04_BASE_SOURCE_COMMIT,
        source_tree_clean=False,
        diff_sha256=campaign["provenance"]["diff_sha256"],
        method_ids=campaign["matrix"]["method_ids"],
        repo_root=REPO_ROOT,
    )
    return campaign


class P04CPublicHandoffTests(unittest.TestCase):
    def _completed(self, raw: str):
        campaign = current_campaign()
        output = Path(raw) / "artifacts"
        summary = run_campaign(campaign, output, repo_root=REPO_ROOT)
        return campaign, output, summary

    def test_verified_handoff_is_exact_public_copy_out(self) -> None:
        with tempfile.TemporaryDirectory(prefix="p04c-handoff-") as raw:
            campaign, output, summary = self._completed(raw)
            handoff = load_verified_public_analysis_handoff(
                output,
                campaign,
                repo_root=REPO_ROOT,
                expected_summary=summary,
            )
            self.assertEqual(handoff.campaign_id, summary.campaign_id)
            self.assertEqual(len(handoff.entries), 2)
            self.assertEqual(
                handoff.validation_receipt_sha256s,
                frozenset(summary.validation_receipt_sha256s),
            )
            forbidden = {
                "candidate_scalar",
                "derivation_seed",
                "expected_scalar",
                "generator",
                "private_payload",
                "private_target_receipt_sha256",
                "private_target_vector_sha256",
                "target",
            }
            for entry in handoff.entries:
                self.assertFalse(forbidden & set(entry))
                self.assertIn(entry["method_status"], {"success", "bounded_failure"})
            changed = handoff.entries[0]
            changed["method_budgets"]["max_steps"] = 1
            self.assertNotEqual(changed, handoff.entries[0])

    def test_out_of_band_summary_is_required_and_exact(self) -> None:
        with tempfile.TemporaryDirectory(prefix="p04c-summary-") as raw:
            campaign, output, summary = self._completed(raw)
            forged = summary.as_dict()
            forged["event_chain_head_sha256"] = "0" * 64
            with self.assertRaisesRegex(PublicHandoffError, "out-of-band"):
                load_verified_public_analysis_handoff(
                    output,
                    campaign,
                    repo_root=REPO_ROOT,
                    expected_summary=forged,
                )

    def test_result_or_index_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="p04c-drift-") as raw:
            campaign, output, summary = self._completed(raw)
            result_path = next(output.glob("attempts/*/*/method_result.json"))
            result = load_json(result_path)
            result["counters"]["restarts"] += 1
            result_path.write_bytes(canonical_json_bytes(result))
            with self.assertRaises(PublicHandoffError):
                load_verified_public_analysis_handoff(
                    output,
                    campaign,
                    repo_root=REPO_ROOT,
                    expected_summary=summary,
                )

        with tempfile.TemporaryDirectory(prefix="p04c-index-") as raw:
            campaign, output, summary = self._completed(raw)
            index_path = output / "public_analysis_index.json"
            index = load_json(index_path)
            index["entries"][0]["private_target_vector_sha256"] = "0" * 64
            index_path.write_bytes(canonical_json_bytes(index))
            with self.assertRaises(PublicHandoffError):
                load_verified_public_analysis_handoff(
                    output,
                    campaign,
                    repo_root=REPO_ROOT,
                    expected_summary=summary,
                )

    def test_missing_artifact_root_is_not_created(self) -> None:
        with tempfile.TemporaryDirectory(prefix="p04c-missing-") as raw:
            missing = Path(raw) / "missing"
            with self.assertRaises(PublicHandoffError):
                load_verified_public_analysis_handoff(
                    missing,
                    current_campaign(),
                    repo_root=REPO_ROOT,
                    expected_summary={},
                )
            self.assertFalse(missing.exists())

    def test_event_protocol_rejects_finish_first_post_finish_and_extra_payload(self) -> None:
        def rewrite(output: Path, source_events: list[dict[str, object]]) -> None:
            previous = None
            rebuilt = []
            for sequence, source_event in enumerate(source_events):
                event = make_event(
                    sequence=sequence,
                    previous_event_sha256=previous,
                    source_snapshot_sha256=source_event["source_snapshot_sha256"],
                    event_type=source_event["event_type"],
                    work_unit_id=source_event["work_unit_id"],
                    attempt_id=source_event["attempt_id"],
                    payload=source_event["payload"],
                )
                rebuilt.append(event)
                previous = event["event_sha256"]
            (output / "events.jsonl").write_bytes(
                b"".join(canonical_json_bytes(event) + b"\n" for event in rebuilt)
            )

        with tempfile.TemporaryDirectory(prefix="p04c-events-") as raw:
            campaign, output, summary = self._completed(raw)
            events = list(
                replay_event_bytes((output / "events.jsonl").read_bytes()).events
            )
            finish = deepcopy(events[-1])
            rewrite(output, [finish])
            with self.assertRaises(PublicHandoffError):
                load_verified_public_analysis_handoff(
                    output, campaign, repo_root=REPO_ROOT, expected_summary=summary
                )

        with tempfile.TemporaryDirectory(prefix="p04c-events-") as raw:
            campaign, output, summary = self._completed(raw)
            events = list(
                replay_event_bytes((output / "events.jsonl").read_bytes()).events
            )
            events.append(
                {
                    **events[0],
                    "event_type": "resume_started",
                    "work_unit_id": None,
                    "attempt_id": None,
                    "payload": {
                        "campaign_id": campaign["campaign_id"],
                        "existing_event_count": len(events),
                    },
                }
            )
            rewrite(output, events)
            with self.assertRaises(PublicHandoffError):
                load_verified_public_analysis_handoff(
                    output, campaign, repo_root=REPO_ROOT, expected_summary=summary
                )

        with tempfile.TemporaryDirectory(prefix="p04c-events-") as raw:
            campaign, output, summary = self._completed(raw)
            events = list(
                replay_event_bytes((output / "events.jsonl").read_bytes()).events
            )
            event = next(item for item in events if item["event_type"] == "method_started")
            event["payload"] = {**event["payload"], "unexpected": "covert"}
            rewrite(output, events)
            with self.assertRaisesRegex(PublicHandoffError, "payload key set"):
                load_verified_public_analysis_handoff(
                    output, campaign, repo_root=REPO_ROOT, expected_summary=summary
                )


if __name__ == "__main__":
    unittest.main()
