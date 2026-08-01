#!/usr/bin/env python3
"""Adversarial regression tests for finite unique-coverage campaigns."""

from __future__ import annotations

import copy
import json
import os
import subprocess
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import hypothesis_space_campaign as campaign
from hypothesis_funnel import Operator
from hypothesis_space_run_ledger import payload_digest, sha256_bytes


class HypothesisSpaceCampaignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.canonical_policy = campaign.load_policy()
        cls.policy = copy.deepcopy(cls.canonical_policy)
        cls.policy["immutable_record_anchors"] = []
        cls.universe = campaign.prepare_universe()
        cls.source_commit = subprocess.run(
            ["git", "merge-base", "HEAD", "origin/main"],
            cwd=campaign.ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        ).stdout.strip()
        cls.original_record_dir = campaign.RECORD_DIR
        cls.temporary = tempfile.TemporaryDirectory(
            prefix=".hyp-campaign-test-", dir=campaign.ROOT
        )
        campaign.RECORD_DIR = Path(cls.temporary.name)
        cls.checkout_patch = patch.object(
            campaign, "checkout_matches_subject", return_value=None
        )
        cls.checkout_patch.start()
        source_dependencies: dict[str, str] = {}
        for relative in campaign.EVALUATOR_DEPENDENCY_PATHS:
            try:
                payload = campaign.git_file_bytes(cls.source_commit, relative)
            except ValueError:
                payload = (campaign.ROOT / relative).read_bytes()
            source_dependencies[relative] = sha256_bytes(payload)
        cls.dependency_patch = patch.object(
            campaign,
            "source_evaluator_dependency_digests",
            return_value=source_dependencies,
        )
        cls.dependency_patch.start()
        date = datetime.now(timezone.utc).date().isoformat()
        cls.campaign_id = f"HSC-{date}-900"
        cls.error_campaign_id = f"HSC-{date}-901"

        with patch.object(campaign, "protected_base_anchors", return_value=[]):
            cls.first_work = campaign.work_receipts(
                cls.policy,
                campaign_id=cls.campaign_id,
                source_commit=cls.source_commit,
                time_budget_seconds=60,
                shard_size=131_072,
                max_new_shards=2,
            )
            first_paths = sorted(
                (campaign.campaign_directory(cls.campaign_id) / "shards").glob(
                    "*.json"
                )
            )
            cls.first_receipt_digests = {
                path.name: sha256_bytes(path.read_bytes()) for path in first_paths
            }
            cls.second_work = campaign.work_receipts(
                cls.policy,
                campaign_id=cls.campaign_id,
                source_commit=cls.source_commit,
                time_budget_seconds=60,
                shard_size=131_072,
            )
            with patch.object(
                campaign,
                "scan_shard",
                side_effect=AssertionError("finalization must consume receipts"),
            ):
                cls.record = campaign.create_record(
                    cls.policy,
                    campaign_id=cls.campaign_id,
                    source_commit=cls.source_commit,
                    time_budget_seconds=600,
                    shard_size=131_072,
                )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.dependency_patch.stop()
        cls.checkout_patch.stop()
        campaign.RECORD_DIR = cls.original_record_dir
        cls.temporary.cleanup()

    def test_committed_campaign_memory_matches_generated_state(self) -> None:
        with patch.object(campaign, "RECORD_DIR", self.original_record_dir):
            records, problems = campaign.load_records(self.canonical_policy)
        self.assertEqual(problems, [])
        expected = campaign.build_state(self.canonical_policy, records)
        actual = json.loads(campaign.STATE_PATH.read_text(encoding="utf-8"))
        self.assertEqual(expected, actual)

    def test_frozen_universe_is_exactly_one_million_cells(self) -> None:
        self.assertEqual(self.universe.expected, 1_000_000)
        self.assertEqual(self.universe.combinations_per_base, 10_000)
        self.assertEqual(len(self.universe.bases), 100)

    def test_universe_identity_precedes_evaluation_and_sharding(self) -> None:
        manifest = campaign.universe_manifest(self.universe)
        self.assertNotIn("evidence_snapshot_sha256", manifest)
        self.assertNotIn("shard_size", manifest)
        self.assertEqual(manifest["cardinality"], 1_000_000)
        self.assertEqual(
            manifest["universe_id_sha256"],
            campaign.universe_manifest(self.universe)["universe_id_sha256"],
        )

    def test_evidence_change_changes_evaluation_not_universe(self) -> None:
        state = json.loads(
            campaign.git_file_bytes(
                self.source_commit, self.policy["subject"]["space_state_path"]
            )
        )
        universe_id = campaign.universe_manifest(self.universe)[
            "universe_id_sha256"
        ]
        kwargs = {
            "dependency_sha256": self.record["evaluation"]["dependency_sha256"]
        }
        original = campaign.evaluation_manifest(universe_id, state, **kwargs)
        changed = copy.deepcopy(state)
        changed["source_bindings"]["evidence_snapshot_sha256"] = "f" * 64
        reevaluated = campaign.evaluation_manifest(universe_id, changed, **kwargs)
        self.assertEqual(
            original["universe_id_sha256"], reevaluated["universe_id_sha256"]
        )
        self.assertNotEqual(
            original["evaluation_id_sha256"], reevaluated["evaluation_id_sha256"]
        )

    def test_fixed_ranges_partition_without_gaps(self) -> None:
        ranges = campaign.fixed_shard_ranges(1_000_000, 131_072)
        self.assertEqual(ranges[0], (0, 131_072))
        self.assertEqual(ranges[-1][1], 1_000_000)
        self.assertEqual(
            sum(end - start for start, end in ranges), 1_000_000
        )
        self.assertTrue(
            all(left[1] == right[0] for left, right in zip(ranges, ranges[1:]))
        )
        with self.assertRaisesRegex(ValueError, "power of two"):
            campaign.fixed_shard_ranges(1_000_000, 100_000)

    def test_resume_reuses_immutable_receipts(self) -> None:
        self.assertEqual(self.first_work["status"], "PARTIAL")
        self.assertEqual(self.first_work["new_shards"], 2)
        self.assertEqual(self.second_work["status"], "READY_TO_FINALIZE")
        paths = sorted(
            (campaign.campaign_directory(self.campaign_id) / "shards").glob(
                "*.json"
            )
        )
        for path in paths[:2]:
            self.assertEqual(
                sha256_bytes(path.read_bytes()),
                self.first_receipt_digests[path.name],
            )

    def test_finalization_is_receipt_derived_without_rescan(self) -> None:
        self.assertEqual(campaign.validate_record(self.record, self.policy), [])
        coverage = self.record["coverage"]
        self.assertEqual(coverage["physical_evaluations"], 1_000_000)
        self.assertEqual(coverage["unique_universe_cells_added"], 1_000_000)
        self.assertEqual(coverage["unique_evaluation_cells_added"], 1_000_000)
        self.assertEqual(coverage["duplicate_evaluations"], 0)
        self.assertEqual(
            coverage["coverage_merkle_root_sha256"],
            self.record["subject"]["coverage_merkle_root_sha256"],
        )

    def test_historical_replay_uses_frozen_source_not_current_scanner(self) -> None:
        source_state = json.loads(
            campaign.git_file_bytes(
                self.source_commit, self.policy["subject"]["space_state_path"]
            )
        )
        with patch.object(
            campaign,
            "scan_shard",
            side_effect=AssertionError("replay must not call the producer scanner"),
        ), patch.object(
            campaign, "prepare_universe", side_effect=AssertionError("historical replay must not use current grammar")
        ), patch.object(
            campaign, "run_frozen_source_projection", return_value=source_state
        ):
            self.assertEqual(campaign.replay_record(self.record), [])

    def test_frozen_source_projection_executes_in_isolated_archive(self) -> None:
        state = campaign.run_frozen_source_projection(self.source_commit)
        self.assertEqual(
            state["bulk_contract"]["coverage_merkle_root_sha256"],
            self.record["coverage"]["coverage_merkle_root_sha256"],
        )

    def test_self_rehashed_receipt_cannot_change_the_anchored_record(self) -> None:
        anchor = self.record["coverage"]["receipt_anchors"][0]
        receipt = campaign.read_json(campaign.ROOT / anchor["path"])
        changed = copy.deepcopy(receipt)
        changed["aggregates"]["cold"] += 1
        changed["aggregates"]["warm"] -= 1
        changed["receipt_payload_sha256"] = campaign.receipt_payload_digest(changed)
        identity = {
            "campaign_id": self.campaign_id,
            "shard_index": 0,
            "start": anchor["start_ordinal"],
            "end": anchor["end_ordinal_exclusive"],
            "previous_receipt_file_sha256": None,
        }
        self.assertEqual(
            campaign.validate_shard_receipt(
                changed,
                self.record["universe"],
                self.record["evaluation"],
                **identity,
            ),
            [],
        )
        changed_record = copy.deepcopy(self.record)
        changed_record["screening_snapshot"]["cold"] += 1
        changed_record["screening_snapshot"]["warm"] -= 1
        source_state = json.loads(
            campaign.git_file_bytes(
                self.source_commit, self.policy["subject"]["space_state_path"]
            )
        )
        with patch.object(
            campaign, "run_frozen_source_projection", return_value=source_state
        ):
            replay_problems = campaign.replay_record(changed_record)
        self.assertTrue(any("count disagrees" in item for item in replay_problems))

    def test_receipt_cannot_substitute_an_unrelated_real_harness(self) -> None:
        anchor = self.record["coverage"]["receipt_anchors"][0]
        receipt = campaign.read_json(campaign.ROOT / anchor["path"])
        changed = copy.deepcopy(receipt)
        changed["harness"]["path"] = "README.md"
        changed["harness"]["sha256"] = sha256_bytes(
            (campaign.ROOT / "README.md").read_bytes()
        )
        changed["receipt_payload_sha256"] = campaign.receipt_payload_digest(changed)
        problems = campaign.validate_shard_receipt(
            changed,
            self.record["universe"],
            self.record["evaluation"],
            campaign_id=self.campaign_id,
            shard_index=0,
            start=anchor["start_ordinal"],
            end=anchor["end_ordinal_exclusive"],
            previous_receipt_file_sha256=None,
        )
        self.assertTrue(any("does not bind" in item for item in problems))

    def test_frozen_replay_drops_ambient_python_import_paths(self) -> None:
        with patch.dict(
            os.environ,
            {
                "PYTHONPATH": "C:/poison",
                "PYTHONHOME": "C:/poison-home",
                "PYTHONSTARTUP": "C:/poison-startup.py",
            },
        ):
            environment = campaign.frozen_replay_environment()
        self.assertNotIn("PYTHONPATH", environment)
        self.assertNotIn("PYTHONHOME", environment)
        self.assertNotIn("PYTHONSTARTUP", environment)
        self.assertEqual(campaign.FROZEN_REPLAY_PYTHON_FLAGS, ("-I", "-S"))

    def test_manifest_snapshot_cannot_override_receipts(self) -> None:
        changed = copy.deepcopy(self.record)
        changed["screening_snapshot"]["cold"] += 1
        changed["screening_snapshot"]["warm"] -= 1
        changed["record_payload_sha256"] = payload_digest(changed)
        problems = campaign.validate_record(changed, self.policy)
        self.assertTrue(any("not receipt-derived" in item for item in problems))

    def test_completed_evaluation_refuses_more_work(self) -> None:
        with patch.object(
            campaign, "load_records", return_value=([self.record], [])
        ), patch.object(
            campaign,
            "scan_shard",
            side_effect=AssertionError("exhausted evaluation must not run"),
        ):
            result = campaign.work_receipts(
                self.policy,
                campaign_id=self.error_campaign_id,
                source_commit=self.source_commit,
                time_budget_seconds=600,
                shard_size=131_072,
            )
        self.assertEqual(result["status"], "EXHAUSTED")
        self.assertEqual(result["physical_evaluations"], 0)

    def test_operational_error_survives_successful_retry(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix=".hyp-campaign-error-test-", dir=campaign.ROOT
        ) as raw, patch.object(campaign, "RECORD_DIR", Path(raw)):
            with patch.object(
                campaign, "load_records", return_value=([], [])
            ), patch.object(
                campaign,
                "create_shard_receipt",
                side_effect=RuntimeError("fault injection"),
            ):
                with self.assertRaisesRegex(RuntimeError, "fault injection"):
                    campaign.work_receipts(
                        self.policy,
                        campaign_id=self.error_campaign_id,
                        source_commit=self.source_commit,
                        time_budget_seconds=60,
                        shard_size=131_072,
                        max_new_shards=1,
                    )
            error_path = (
                campaign.campaign_directory(self.error_campaign_id)
                / "errors"
                / "0001.json"
            )
            before = sha256_bytes(error_path.read_bytes())
            event = campaign.read_json(error_path)
            self.assertIn("fault injection", event["message_excerpt"])
            self.assertIn("RuntimeError", event["traceback_excerpt"])
            self.assertFalse(event["message_truncated"])
            self.assertFalse(event["traceback_truncated"])
            self.assertEqual(event["retry_class"], "unclassified_retry_once")
            with patch.object(campaign, "load_records", return_value=([], [])):
                result = campaign.work_receipts(
                    self.policy,
                    campaign_id=self.error_campaign_id,
                    source_commit=self.source_commit,
                    time_budget_seconds=60,
                    shard_size=131_072,
                    max_new_shards=1,
                )
            self.assertEqual(result["new_shards"], 1)
            self.assertEqual(before, sha256_bytes(error_path.read_bytes()))
            _, problems = campaign.validate_campaign_error_chain(
                self.error_campaign_id,
                self.record["universe"]["universe_id_sha256"],
                self.record["evaluation"]["evaluation_id_sha256"],
            )
            self.assertEqual(problems, [])

    def test_second_evaluation_adds_no_new_universe_cells(self) -> None:
        second = copy.deepcopy(self.record)
        second["campaign_id"] = self.error_campaign_id
        second["evaluation"]["evidence_snapshot_sha256"] = "e" * 64
        projection = copy.deepcopy(second["evaluation"])
        projection.pop("evaluation_id_sha256")
        second["evaluation"]["evaluation_id_sha256"] = campaign.sha256_json(
            projection
        )
        second["coverage"]["unique_universe_cells_added"] = 0
        state = campaign.build_state(self.policy, [self.record, second])
        self.assertEqual(state["counts"]["distinct_universes"], 1)
        self.assertEqual(state["counts"]["distinct_evaluations"], 2)
        self.assertEqual(state["counts"]["unique_universe_cells"], 1_000_000)
        self.assertEqual(state["counts"]["unique_evaluation_cells"], 2_000_000)
        self.assertEqual(state["counts"]["repeated_cells_processed"], 1_000_000)
        self.assertEqual(state["counts"]["duplicate_evaluations"], 0)

    def test_exact_semantic_axis_duplicate_fails_preflight(self) -> None:
        first = self.universe.mechanisms[0]
        duplicate = Operator(
            id="DIFFERENT-ID",
            label=first.label,
            compatible_types=first.compatible_types,
            capabilities=first.capabilities,
            dimensions=first.dimensions,
        )
        with self.assertRaisesRegex(ValueError, "semantic duplicates"):
            campaign.assert_semantic_axis_uniqueness(
                [first, duplicate],
                self.universe.costs,
                self.universe.tests,
                self.universe.challenges,
            )

    def test_stale_or_unreachable_source_commit_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "ancestor"):
            campaign.work_receipts(
                self.policy,
                campaign_id=self.error_campaign_id,
                source_commit="0" * 40,
                time_budget_seconds=60,
                shard_size=131_072,
                max_new_shards=0,
            )

    def test_campaign_cannot_be_relabelled_or_authorize(self) -> None:
        changed = copy.deepcopy(self.record)
        changed["knowledge_effect"]["scientific_outcome"] = "falsified"
        changed["knowledge_effect"]["experiment_authorized"] = True
        changed["record_payload_sha256"] = payload_digest(changed)
        problems = campaign.validate_record(changed, self.policy)
        self.assertTrue(any("scientific-memory boundary" in item for item in problems))

    def test_schema_rejects_additional_scientific_boundary_fields(self) -> None:
        changed = copy.deepcopy(self.record)
        changed["knowledge_effect"]["campaign_proves_attack"] = True
        changed["record_payload_sha256"] = payload_digest(changed)
        problems = campaign.validate_record(changed, self.policy)
        self.assertTrue(any("unexpected property" in item for item in problems))

    def test_schema_validates_dynamic_map_values(self) -> None:
        changed = copy.deepcopy(self.record)
        changed["evaluation"]["dependency_sha256"][
            "scripts/hypothesis_funnel.py"
        ] = "not-a-digest"
        problems = campaign.schema_problems(changed, campaign.SCHEMA_PATH)
        self.assertTrue(any("schema pattern" in item for item in problems))

    def test_local_schema_validator_fails_closed_on_unknown_keywords(self) -> None:
        problems = campaign.schema_definition_problems(
            {"type": "object", "maxProperties": 1}
        )
        self.assertTrue(any("unsupported schema keyword" in item for item in problems))

    def test_schema_requires_timezone_qualified_timestamps(self) -> None:
        changed = copy.deepcopy(self.record)
        changed["recorded_at_utc"] = "2026-08-01T12:00:00"
        problems = campaign.schema_problems(changed, campaign.SCHEMA_PATH)
        self.assertTrue(any("RFC3339 date-time" in item for item in problems))

    def test_policy_cannot_redirect_protected_main(self) -> None:
        changed = copy.deepcopy(self.policy)
        changed["protected_base_ref"] = "HEAD"
        self.assertTrue(
            any("canonical origin/main" in item for item in campaign.validate_policy(changed))
        )

    def test_dependency_change_creates_a_new_evaluation_identity(self) -> None:
        state = json.loads(
            campaign.git_file_bytes(
                self.source_commit, self.policy["subject"]["space_state_path"]
            )
        )
        universe_id = self.record["universe"]["universe_id_sha256"]
        dependencies = copy.deepcopy(self.record["evaluation"]["dependency_sha256"])
        original = campaign.evaluation_manifest(
            universe_id, state, dependency_sha256=dependencies
        )
        dependencies["scripts/hypothesis_funnel.py"] = "f" * 64
        changed = campaign.evaluation_manifest(
            universe_id, state, dependency_sha256=dependencies
        )
        self.assertNotEqual(
            original["evaluation_id_sha256"], changed["evaluation_id_sha256"]
        )

    def test_evaluation_reservation_rejects_second_campaign(self) -> None:
        evaluation_id = self.record["evaluation"]["evaluation_id_sha256"]
        with self.assertRaisesRegex(ValueError, "reserved by another campaign"):
            campaign.ensure_evaluation_claim(
                campaign_id=self.error_campaign_id,
                source_commit=self.source_commit,
                universe_id=self.record["universe"]["universe_id_sha256"],
                evaluation_id=evaluation_id,
            )

    def test_same_campaign_writer_lock_prevents_duplicate_physical_work(self) -> None:
        lock_path = campaign.campaign_directory(self.error_campaign_id) / ".writer.lock"
        campaign.immutable_create_json(lock_path, {"fault": "concurrent writer"})
        try:
            with patch.object(
                campaign,
                "scan_shard",
                side_effect=AssertionError("locked writer must not scan"),
            ), self.assertRaisesRegex(ValueError, "writer lock"):
                campaign.work_receipts(
                    self.policy,
                    campaign_id=self.error_campaign_id,
                    source_commit=self.source_commit,
                    time_budget_seconds=60,
                    shard_size=131_072,
                    max_new_shards=1,
                )
        finally:
            lock_path.unlink(missing_ok=True)

    def test_campaign_timing_is_explicitly_self_reported(self) -> None:
        self.assertEqual(
            self.record["performance"]["timing_assurance"],
            "producer_self_timed_untrusted",
        )
        self.assertFalse(
            self.record["performance"]["throughput_is_coverage_evidence"]
        )
        self.assertTrue(
            self.record["performance"]["runtime_fingerprint"]["python_version"]
        )

    def test_schemas_hard_code_operational_boundary(self) -> None:
        schema = json.loads(campaign.SCHEMA_PATH.read_text(encoding="utf-8"))
        effect = schema["properties"]["knowledge_effect"]["properties"]
        self.assertEqual(effect["scientific_outcome"], {"const": "none"})
        self.assertEqual(effect["experiment_authorized"], {"const": False})
        self.assertEqual(effect["route_promotion"], {"const": False})
        self.assertIn("universe", schema["required"])
        self.assertIn("evaluation", schema["required"])
        json.loads(campaign.RECEIPT_SCHEMA_PATH.read_text(encoding="utf-8"))
        json.loads(campaign.ERROR_SCHEMA_PATH.read_text(encoding="utf-8"))

    def test_campaign_memory_is_not_scientific_screening_input(self) -> None:
        space_policy = json.loads(
            (campaign.POLICY_PATH.parent / "HYPOTHESIS_SPACE_V2.json").read_text(
                encoding="utf-8"
            )
        )
        joined = " ".join(space_policy["evidence_snapshot"]["paths"])
        self.assertNotIn("hypothesis_space_campaign", joined.lower())


if __name__ == "__main__":
    unittest.main()
