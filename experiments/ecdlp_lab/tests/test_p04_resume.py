from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from experiments.ecdlp_lab.core.canonical import canonical_json_bytes, load_json, sha256_json
from experiments.ecdlp_lab.orchestration.events import make_event, replay_event_bytes
from experiments.ecdlp_lab.orchestration.process import ProcessResult
from experiments.ecdlp_lab.orchestration.provenance import build_campaign_provenance
from experiments.ecdlp_lab.orchestration.records import (
    SMOKE_CAMPAIGN_PATH,
    expand_campaign,
    retry_work_unit,
)
from experiments.ecdlp_lab.orchestration.runner import (
    EVENT_LOG_PATH,
    RunnerError,
    run_campaign,
)
from experiments.ecdlp_lab.orchestration.storage import ArtifactStore
import experiments.ecdlp_lab.orchestration.runner as runner_module


REPO_ROOT = Path(__file__).resolve().parents[3]


def current_campaign() -> dict[str, object]:
    """Keep runner fault tests usable while the committed fixture is regenerated."""

    campaign = load_json(REPO_ROOT / SMOKE_CAMPAIGN_PATH)
    provenance = campaign["provenance"]
    campaign["provenance"] = build_campaign_provenance(
        config_sha256=campaign["campaign_id"],
        source_commit=provenance["source_commit"],
        source_tree_clean=True,
        diff_sha256=None,
        method_ids=campaign["matrix"]["method_ids"],
        repo_root=REPO_ROOT,
    )
    return campaign


def failed_process(role: str, *, timed_out: bool = False, late: bool = False) -> ProcessResult:
    output = {"late": True} if late else None
    encoded = canonical_json_bytes(output) if output is not None else b""
    return ProcessResult(
        role=role,
        status="timeout" if timed_out else "worker_error",
        returncode=1,
        output=output,
        timed_out=timed_out,
        terminated=True,
        stdout_bytes=len(encoded),
        stderr_bytes=0,
        stdout_sha256=sha256_json(output) if output is not None else "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        stderr_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        stderr_excerpt="",
    )


def read_event_bytes(output: Path) -> bytes:
    with ArtifactStore(output) as store:
        return store.read_bytes(EVENT_LOG_PATH)


def replay_output(output: Path):
    return replay_event_bytes(read_event_bytes(output))


class P04ResumeTests(unittest.TestCase):
    def test_completed_replay_is_byte_and_summary_idempotent(self) -> None:
        with tempfile.TemporaryDirectory(prefix="p04-resume-") as raw:
            output = Path(raw) / "artifacts"
            first = run_campaign(current_campaign(), output, repo_root=REPO_ROOT)
            event_bytes = read_event_bytes(output)
            index_bytes = (output / "public_analysis_index.json").read_bytes()
            receipt_bytes = {
                path.name: path.read_bytes()
                for path in (output / "receipts").glob("*.json")
            }

            second = run_campaign(current_campaign(), output, repo_root=REPO_ROOT)
            self.assertEqual(second, first)
            self.assertEqual(read_event_bytes(output), event_bytes)
            self.assertEqual((output / "public_analysis_index.json").read_bytes(), index_bytes)
            self.assertEqual(
                {path.name: path.read_bytes() for path in (output / "receipts").glob("*.json")},
                receipt_bytes,
            )
            replay = replay_output(output)
            self.assertEqual(
                sum(event["event_type"] == "campaign_finished" for event in replay.events),
                1,
            )
            self.assertEqual(
                sum(event["event_type"] == "work_finalized" for event in replay.events),
                2,
            )

    def test_interruption_retries_without_duplicate_final_receipt(self) -> None:
        with tempfile.TemporaryDirectory(prefix="p04-interrupt-") as raw:
            output = Path(raw) / "artifacts"
            with patch.object(runner_module, "_run_attempt", side_effect=KeyboardInterrupt):
                with self.assertRaises(KeyboardInterrupt):
                    run_campaign(current_campaign(), output, repo_root=REPO_ROOT)

            summary = run_campaign(current_campaign(), output, repo_root=REPO_ROOT)
            self.assertTrue(summary.passed)
            self.assertEqual(len(tuple((output / "receipts").glob("*.json"))), 2)
            replay = replay_output(output)
            first_work = replay.events[1]["work_unit_id"]
            attempts = [
                event
                for event in replay.events
                if event["event_type"] == "work_scheduled"
                and event["work_unit_id"] == first_work
            ]
            self.assertEqual([event["payload"]["retry_ordinal"] for event in attempts], [0, 1])

    def test_timeout_late_output_is_discarded_before_successful_retry(self) -> None:
        real_run_worker = runner_module.run_worker
        injected = False

        def flaky(role: str, payload: object, **kwargs: object) -> ProcessResult:
            nonlocal injected
            if role == "method" and not injected:
                injected = True
                return failed_process("method", timed_out=True, late=True)
            return real_run_worker(role, payload, **kwargs)

        with tempfile.TemporaryDirectory(prefix="p04-timeout-") as raw:
            output = Path(raw) / "artifacts"
            with patch.object(runner_module, "run_worker", side_effect=flaky):
                summary = run_campaign(current_campaign(), output, repo_root=REPO_ROOT)
            self.assertTrue(summary.passed)
            event_types = [
                event["event_type"] for event in replay_output(output).events
            ]
            self.assertIn("method_timeout", event_types)
            self.assertIn("late_result_discarded", event_types)
            self.assertIn("work_failed", event_types)

    def test_validator_disagreement_is_not_final_and_is_retried(self) -> None:
        real_run_worker = runner_module.run_worker
        injected = False

        def disagree_once(role: str, payload: object, **kwargs: object) -> ProcessResult:
            nonlocal injected
            result = real_run_worker(role, payload, **kwargs)
            if role != "validator" or injected or result.output is None:
                return result
            injected = True
            poisoned = deepcopy(result.output)
            poisoned["candidate"] = None
            poisoned["relation_verified"] = False
            poisoned["passed"] = False
            poisoned["issues"] = [
                {"code": "candidate.mismatch", "path": "$.candidate", "message": "candidate rejected"}
            ]
            encoded = canonical_json_bytes(poisoned)
            return replace(
                result,
                output=poisoned,
                stdout_bytes=len(encoded),
                stdout_sha256=sha256_json(poisoned),
            )

        with tempfile.TemporaryDirectory(prefix="p04-disagree-") as raw:
            output = Path(raw) / "artifacts"
            with patch.object(runner_module, "run_worker", side_effect=disagree_once):
                summary = run_campaign(current_campaign(), output, repo_root=REPO_ROOT)
            self.assertTrue(summary.passed)
            replay = replay_output(output)
            self.assertIn(
                "validator_replay_mismatch",
                [
                    event["payload"].get("failure_code")
                    for event in replay.events
                    if event["event_type"] == "work_failed"
                ],
            )
            self.assertEqual(len(tuple((output / "receipts").glob("*.json"))), 2)

    def test_corrupted_final_receipt_is_never_repaired_or_accepted(self) -> None:
        with tempfile.TemporaryDirectory(prefix="p04-corrupt-") as raw:
            output = Path(raw) / "artifacts"
            run_campaign(current_campaign(), output, repo_root=REPO_ROOT)
            receipt = next((output / "receipts").glob("*.json"))
            receipt.write_bytes(receipt.read_bytes() + b"\n")
            with self.assertRaises(RunnerError):
                run_campaign(current_campaign(), output, repo_root=REPO_ROOT)

    def test_missing_completed_receipt_is_not_recreated(self) -> None:
        with tempfile.TemporaryDirectory(prefix="p04-missing-") as raw:
            output = Path(raw) / "artifacts"
            run_campaign(current_campaign(), output, repo_root=REPO_ROOT)
            receipt = next((output / "receipts").glob("*.json"))
            receipt.unlink()
            with self.assertRaises(RunnerError):
                run_campaign(current_campaign(), output, repo_root=REPO_ROOT)
            self.assertFalse(receipt.exists())

    def test_resume_reruns_validator_and_rejects_forged_zero_counters(self) -> None:
        with tempfile.TemporaryDirectory(prefix="p04-validator-forge-") as raw:
            output = Path(raw) / "artifacts"
            run_campaign(current_campaign(), output, repo_root=REPO_ROOT)
            retained = next(output.glob("attempts/*/*/validator_output.json"))
            forged = load_json(retained)
            counters = forged["validator_counters"]
            counters["generator_subgroup_check"] = 0
            counters["target_subgroup_check"] = 0
            counters["candidate_relation_check"] = 0
            counters["total_group_law_invocations"] = 0
            forged["candidate"] = 1
            forged["relation_verified"] = True
            forged["passed"] = True
            forged["issues"] = []
            retained.write_bytes(canonical_json_bytes(forged))
            with self.assertRaisesRegex(RunnerError, "validator"):
                run_campaign(current_campaign(), output, repo_root=REPO_ROOT)

    def test_recomputed_chain_cannot_forge_a_noncontiguous_retry(self) -> None:
        campaign = current_campaign()
        plan = expand_campaign(campaign, repo_root=REPO_ROOT)
        work = plan.work_units[0]
        source = campaign["provenance"]["source_snapshot_sha256"]
        started = make_event(
            sequence=0,
            previous_event_sha256=None,
            source_snapshot_sha256=source,
            event_type="campaign_started",
            payload={
                "campaign_id": campaign["campaign_id"],
                "expected_work_unit_count": 2,
            },
        )
        retry = retry_work_unit(work, 1)
        forged = make_event(
            sequence=1,
            previous_event_sha256=started["event_sha256"],
            source_snapshot_sha256=source,
            event_type="work_scheduled",
            work_unit_id=work["work_unit_id"],
            attempt_id=retry["attempt_id"],
            payload={"retry_ordinal": 1},
        )
        with tempfile.TemporaryDirectory(prefix="p04-forged-") as raw:
            output = Path(raw) / "artifacts"
            with ArtifactStore(output) as store:
                store.append_jsonl(EVENT_LOG_PATH, started, lock_name="events")
                store.append_jsonl(EVENT_LOG_PATH, forged, lock_name="events")
            with self.assertRaisesRegex(RunnerError, "retry ordinals"):
                run_campaign(campaign, output, repo_root=REPO_ROOT)


if __name__ == "__main__":
    unittest.main()
