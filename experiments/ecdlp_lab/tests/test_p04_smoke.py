from __future__ import annotations

from copy import deepcopy
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from experiments.ecdlp_lab.core.canonical import canonical_json_bytes, load_json, strict_loads
from experiments.ecdlp_lab.orchestration.events import replay_event_bytes
from experiments.ecdlp_lab.orchestration.provenance import build_campaign_provenance
from experiments.ecdlp_lab.orchestration.records import SMOKE_CAMPAIGN_PATH
from experiments.ecdlp_lab.orchestration.runner import EVENT_LOG_PATH, run_campaign
from experiments.ecdlp_lab.orchestration.storage import ArtifactStore
import experiments.ecdlp_lab.orchestration.runner as runner_module


REPO_ROOT = Path(__file__).resolve().parents[3]
PRIVATE_PUBLICATION_KEYS = {
    "derivation_seed",
    "expected_scalar",
    "private_payload",
    "private_target",
    "private_target_id",
    "private_target_path",
    "private_target_receipt_sha256",
    "private_target_vector_sha256",
}


def current_campaign() -> dict[str, object]:
    campaign = load_json(REPO_ROOT / SMOKE_CAMPAIGN_PATH)
    old = campaign["provenance"]
    campaign["provenance"] = build_campaign_provenance(
        config_sha256=campaign["campaign_id"],
        source_commit=old["source_commit"],
        source_tree_clean=True,
        diff_sha256=None,
        method_ids=campaign["matrix"]["method_ids"],
        repo_root=REPO_ROOT,
    )
    return campaign


def walked_keys(value: object) -> set[str]:
    keys: set[str] = set()
    stack = [value]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            keys.update(current)
            stack.extend(current.values())
        elif isinstance(current, list):
            stack.extend(current)
    return keys


class P04SmokeTests(unittest.TestCase):
    def test_two_method_smoke_publishes_only_validated_receipt_index(self) -> None:
        with tempfile.TemporaryDirectory(prefix="p04-smoke-") as raw:
            output = Path(raw) / "artifacts"
            summary = run_campaign(current_campaign(), output, repo_root=REPO_ROOT)
            self.assertTrue(summary.passed)
            self.assertEqual(len(summary.completed_work_unit_ids), 2)

            work_records = [load_json(path) for path in (output / "work_units").glob("*.json")]
            self.assertEqual(
                {record["identity"]["method_id"] for record in work_records},
                {"bsgs_v1", "ordinary_rho_xmod3_v1"},
            )
            self.assertEqual(
                {record["identity"]["algorithm_seed"] for record in work_records},
                {7},
            )
            receipts = [load_json(path) for path in (output / "receipts").glob("*.json")]
            self.assertEqual(len(receipts), 2)
            self.assertTrue(all(receipt["passed"] is True for receipt in receipts))
            self.assertTrue(all(receipt["candidate_scalar"] == 1 for receipt in receipts))

            index = load_json(output / "public_analysis_index.json")
            self.assertEqual(index["campaign_id"], summary.campaign_id)
            self.assertEqual(
                [entry["work_unit_id"] for entry in index["entries"]],
                sorted(summary.completed_work_unit_ids),
            )
            self.assertFalse(PRIVATE_PUBLICATION_KEYS & walked_keys(index))
            with ArtifactStore(output) as store:
                replay = replay_event_bytes(store.read_bytes(EVENT_LOG_PATH))
            self.assertFalse(
                PRIVATE_PUBLICATION_KEYS
                & walked_keys([event["payload"] for event in replay.events])
            )
            self.assertEqual(
                replay.events[-1]["payload"]["public_analysis_index_sha256"],
                summary.public_analysis_index_sha256,
            )

    def test_method_child_stdin_is_exact_nine_field_public_projection(self) -> None:
        captured: list[dict[str, object]] = []
        real_run_worker = runner_module.run_worker

        def capture(role: str, payload: object, **kwargs: object):
            if role == "method":
                captured.append(deepcopy(dict(payload)))
            return real_run_worker(role, payload, **kwargs)

        with tempfile.TemporaryDirectory(prefix="p04-captured-stdin-") as raw:
            with patch.object(runner_module, "run_worker", side_effect=capture):
                run_campaign(
                    current_campaign(), Path(raw) / "artifacts", repo_root=REPO_ROOT
                )
        expected = {
            "method_id",
            "algorithm_seed",
            "p",
            "a",
            "b",
            "G",
            "Q",
            "ell",
            "budgets",
        }
        forbidden = {
            "attempt_id",
            "authorization_id",
            "candidate_id",
            "curve_catalog_sha256",
            "curve_fixture_id",
            "curve_id",
            "derivation_seed",
            "expected_scalar",
            "private_payload",
            "private_target_receipt_sha256",
            "provenance",
            "public_target_vector_sha256",
            "request_id",
            "source_snapshot_sha256",
            "work_unit_id",
        }
        self.assertEqual(len(captured), 2)
        for payload in captured:
            self.assertEqual(set(payload), expected)
            self.assertFalse(forbidden & walked_keys(payload))

    def test_stable_cli_emits_one_canonical_summary(self) -> None:
        with tempfile.TemporaryDirectory(prefix="p04-cli-") as raw:
            output = Path(raw) / "artifacts"
            environment = dict(os.environ)
            environment["PYTHONDONTWRITEBYTECODE"] = "1"
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    "-m",
                    "experiments.ecdlp_lab.orchestration.run_smoke",
                    "--config",
                    SMOKE_CAMPAIGN_PATH,
                    "--output",
                    str(output),
                ],
                cwd=REPO_ROOT,
                env=environment,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=20,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr.decode("utf-8"))
            self.assertEqual(completed.stderr, b"")
            summary = strict_loads(completed.stdout, label="smoke CLI stdout")
            self.assertEqual(completed.stdout, canonical_json_bytes(summary) + b"\n")
            self.assertTrue(summary["passed"])
            self.assertEqual(len(summary["completed_work_unit_ids"]), 2)


if __name__ == "__main__":
    unittest.main()
