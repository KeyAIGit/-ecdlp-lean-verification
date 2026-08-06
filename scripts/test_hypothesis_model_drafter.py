#!/usr/bin/env python3
"""Regression tests for the non-executing model-assisted draft layer."""

from __future__ import annotations

import copy
import base64
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
import urllib.error
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from hypothesis_model_drafter import (
    ABSTENTION_SENTINEL,
    EVIDENCE_MAPPED_FIELDS,
    POLICY_PATH,
    ProviderHTTPFailure,
    acquire_output_lease,
    atomic_write_output,
    bounded_error_message,
    build_api_payload,
    build_context_documents,
    build_repository_snapshot,
    build_request_packets,
    call_openai_compatible,
    canonical_research_engine_snapshot,
    classify_http_error,
    classify_provider_failure_message,
    inspect_git_source_state,
    load_json,
    main,
    parse_fragment,
    parse_provider_response_body,
    provider_error_record,
    provider_metadata_problems,
    prepare_inference_packets,
    release_output_lease,
    validate_policy,
)


def fragment_fixture(fields: list[str]) -> dict[str, object]:
    value: dict[str, object] = {
        field: (
            ["fixture"]
            if field == "missing_evidence"
            else []
            if field == "evidence_claim_ids"
            else {}
            if field == "field_evidence_claim_ids"
            else "fixture"
        )
        for field in fields
    }
    value["field_evidence_claim_ids"] = {
        field: [] for field in EVIDENCE_MAPPED_FIELDS
    }
    return value


class FakeHTTPResponse:
    def __init__(self, body: bytes) -> None:
        self.body = body

    def __enter__(self) -> "FakeHTTPResponse":
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def read(self, size: int = -1) -> bytes:
        return self.body if size < 0 else self.body[:size]


class HypothesisModelDrafterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy = load_json(POLICY_PATH)
        validate_policy(cls.policy)
        root = POLICY_PATH.parents[1]
        brainstorm = cls.policy["lanes"]["brainstorm_queue"]
        typed = cls.policy["lanes"]["typed_evidence"]
        cls.brainstorm_state = load_json(root / brainstorm["source_state"])
        cls.engine_state = load_json(root / typed["source_state"])
        cls.typed_evidence_state = load_json(
            root / typed["typed_evidence_state"]
        )
        cls.decision_state = load_json(root / typed["decision_state"])

    def test_dry_request_plan_is_deterministic_and_non_executable(self) -> None:
        left = build_request_packets(
            self.policy,
            self.brainstorm_state,
            limit=10,
            lane_id="brainstorm_queue",
        )
        right = build_request_packets(
            self.policy,
            self.brainstorm_state,
            limit=10,
            lane_id="brainstorm_queue",
        )
        self.assertEqual(left, right)
        self.assertEqual(10, len(left))
        self.assertTrue(all(item["lane"] == "brainstorm_queue" for item in left))
        self.assertTrue(
            all(item["input_provenance_bound"] is False for item in left)
        )
        self.assertTrue(all(item["allowed_evidence_claim_ids"] == [] for item in left))
        self.assertTrue(all(item["authorization"] == "none" for item in left))
        self.assertTrue(all(item["executable"] is False for item in left))
        self.assertEqual(
            10, len({item["scientific_packet_sha256"] for item in left})
        )

    def test_inference_identity_binds_provider_model_envelope_and_commit(self) -> None:
        packets = build_request_packets(
            self.policy,
            self.brainstorm_state,
            limit=1,
            lane_id="brainstorm_queue",
        )
        source_commit = "a" * 40
        flash = prepare_inference_packets(
            self.policy,
            packets,
            provider_id="featherless",
            provider=self.policy["providers"]["featherless"],
            model="deepseek-ai/DeepSeek-V4-Flash",
            source_commit=source_commit,
            source_tree_clean=True,
            source_main_ancestor=True,
        )[0]
        pro = prepare_inference_packets(
            self.policy,
            packets,
            provider_id="featherless",
            provider=self.policy["providers"]["featherless"],
            model="deepseek-ai/DeepSeek-V4-Pro",
            source_commit=source_commit,
            source_tree_clean=True,
            source_main_ancestor=True,
        )[0]
        direct = prepare_inference_packets(
            self.policy,
            packets,
            provider_id="deepseek_direct",
            provider=self.policy["providers"]["deepseek_direct"],
            model="deepseek-chat",
            source_commit=source_commit,
            source_tree_clean=True,
            source_main_ancestor=True,
        )[0]
        self.assertEqual(
            flash["scientific_packet_sha256"],
            pro["scientific_packet_sha256"],
        )
        self.assertEqual(
            flash["scientific_packet_sha256"],
            direct["scientific_packet_sha256"],
        )
        self.assertNotEqual(
            flash["inference_request_sha256"],
            pro["inference_request_sha256"],
        )
        self.assertNotEqual(
            flash["inference_request_sha256"],
            direct["inference_request_sha256"],
        )
        self.assertEqual(source_commit, flash["source_commit"])
        self.assertRegex(flash["drafter_source_sha256"], r"^[0-9a-f]{64}$")

    def test_provider_response_retains_replayable_metadata(self) -> None:
        body = json.dumps(
            {
                "id": "resp-1",
                "created": 123,
                "model": "model-reported",
                "system_fingerprint": "fp-1",
                "usage": {"prompt_tokens": 10, "completion_tokens": 2},
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {"content": "{\"abstain\":true}"},
                    }
                ],
            },
            separators=(",", ":"),
        ).encode("utf-8")
        payload = build_api_payload(
            model="deepseek-chat", prompt="fixture", max_tokens=10
        )
        with patch(
            "hypothesis_model_drafter.urllib.request.urlopen",
            return_value=FakeHTTPResponse(body),
        ):
            response = call_openai_compatible(
                base_url="https://api.deepseek.com",
                api_key="not-a-real-secret",
                payload=payload,
                max_response_bytes=4096,
            )
        self.assertEqual('{"abstain":true}', response["content"])
        self.assertEqual("resp-1", response["metadata"]["response_id"])
        self.assertEqual("model-reported", response["metadata"]["reported_model"])
        self.assertEqual("stop", response["metadata"]["finish_reason"])
        self.assertEqual(body.decode("utf-8"), response["body"])
        self.assertEqual(
            hashlib.sha256(body).hexdigest(),
            response["provider_response_sha256"],
        )
        content, metadata = parse_provider_response_body(body.decode("utf-8"))
        self.assertEqual(response["content"], content)
        self.assertEqual(response["metadata"], metadata)
        self.assertEqual(
            [],
            provider_metadata_problems(metadata, requested_model="model-reported"),
        )
        self.assertEqual(
            ["provider_reported_model_mismatch"],
            provider_metadata_problems(metadata, requested_model="other-model"),
        )
        truncated = dict(metadata)
        truncated["finish_reason"] = "length"
        self.assertIn(
            "provider_completion_not_complete",
            provider_metadata_problems(
                truncated, requested_model="model-reported"
            ),
        )

    def test_provider_response_size_and_shape_fail_closed(self) -> None:
        with patch(
            "hypothesis_model_drafter.urllib.request.urlopen",
            return_value=FakeHTTPResponse(b"x" * 12),
        ):
            with self.assertRaisesRegex(RuntimeError, "byte bound"):
                call_openai_compatible(
                    base_url="https://api.deepseek.com",
                    api_key="not-a-real-secret",
                    payload={},
                    max_response_bytes=10,
                )
        with self.assertRaisesRegex(RuntimeError, "pinned shape"):
            parse_provider_response_body('{"choices":[]}')

    def test_http_failure_retains_replayable_status_body_and_digest(self) -> None:
        body = b'{"error":"model not available on plan"}'
        failure = urllib.error.HTTPError(
            "https://api.featherless.ai/v1/chat/completions",
            403,
            "Forbidden",
            {},
            io.BytesIO(body),
        )
        with patch(
            "hypothesis_model_drafter.urllib.request.urlopen",
            side_effect=failure,
        ):
            with self.assertRaises(ProviderHTTPFailure) as caught:
                call_openai_compatible(
                    base_url="https://api.featherless.ai/v1",
                    api_key="not-a-real-secret",
                    payload={},
                    max_response_bytes=4096,
                )
        error = caught.exception
        self.assertEqual(403, error.status)
        self.assertEqual("authentication_or_plan_rejected", error.classification)
        self.assertEqual(body.decode("utf-8"), error.body)
        self.assertEqual(base64.b64encode(body).decode("ascii"), error.body_base64)
        self.assertEqual(hashlib.sha256(body).hexdigest(), error.body_sha256)
        self.assertEqual(len(body), error.body_size_bytes)
        self.assertFalse(error.body_truncated)
        record = provider_error_record(
            {
                "scientific_packet_sha256": "a" * 64,
                "inference_request_sha256": "b" * 64,
            },
            attempted=True,
            classification=error.classification,
            error_type=type(error).__name__,
            provider_error=error,
        )
        self.assertEqual(403, record["http_status"])
        self.assertEqual(body.decode("utf-8"), record["error_body"])
        self.assertEqual(
            base64.b64encode(body).decode("ascii"), record["error_body_base64"]
        )
        self.assertEqual(hashlib.sha256(body).hexdigest(), record["error_body_sha256"])
        self.assertEqual(len(body), record["error_body_size_bytes"])
        self.assertFalse(record["error_body_truncated"])

    def test_invalid_utf8_http_bodies_retain_distinct_raw_evidence(self) -> None:
        records = []
        for raw_body in (b"\xff", b"\xfe"):
            failure = ProviderHTTPFailure(
                status=500,
                classification="provider_unavailable",
                raw_body=raw_body,
                body_truncated=False,
            )
            records.append(
                provider_error_record(
                    {
                        "scientific_packet_sha256": "a" * 64,
                        "inference_request_sha256": "b" * 64,
                    },
                    attempted=True,
                    classification=failure.classification,
                    error_type=type(failure).__name__,
                    provider_error=failure,
                )
            )
        self.assertEqual(records[0]["error_body"], records[1]["error_body"])
        self.assertNotEqual(
            records[0]["error_body_base64"], records[1]["error_body_base64"]
        )
        self.assertNotEqual(
            records[0]["error_body_sha256"], records[1]["error_body_sha256"]
        )

    def test_non_http_failure_classification_replays_from_stored_message(self) -> None:
        failure = RuntimeError("provider response does not match the pinned shape")
        message = bounded_error_message(failure)
        self.assertEqual(
            "provider_response_malformed",
            classify_provider_failure_message(message),
        )

    def test_source_commit_must_match_checked_out_head(self) -> None:
        head = "b" * 40
        clean = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=head + "\n", stderr=""
        )
        status = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        ancestry = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        with patch(
            "hypothesis_model_drafter.subprocess.run",
            side_effect=[clean, status, ancestry],
        ):
            self.assertEqual(
                {
                    "source_commit": head,
                    "source_tree_clean": True,
                    "source_main_ancestor": True,
                },
                inspect_git_source_state(head),
            )
        with patch(
            "hypothesis_model_drafter.subprocess.run",
            side_effect=[clean, status],
        ):
            with self.assertRaisesRegex(ValueError, "does not match"):
                inspect_git_source_state("a" * 40)

    def test_ancestry_nonmember_is_false_but_git_error_is_rejected(self) -> None:
        head = "b" * 40
        clean = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=head + "\n", stderr=""
        )
        status = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        nonmember = subprocess.CompletedProcess(
            args=[], returncode=1, stdout="", stderr=""
        )
        with patch(
            "hypothesis_model_drafter.subprocess.run",
            side_effect=[clean, status, nonmember],
        ):
            self.assertFalse(inspect_git_source_state(head)["source_main_ancestor"])
        git_error = subprocess.CompletedProcess(
            args=[], returncode=128, stdout="", stderr="fatal"
        )
        with patch(
            "hypothesis_model_drafter.subprocess.run",
            side_effect=[clean, status, git_error],
        ):
            with self.assertRaisesRegex(ValueError, "protected-main ancestry"):
                inspect_git_source_state(head)

    def test_canonical_snapshot_cache_cannot_be_poisoned_by_mutation(self) -> None:
        fixture = {
            "hypothesis_generation": {
                "source_hashes": {"typed_evidence_state_sha256": "a" * 64}
            }
        }
        canonical_research_engine_snapshot.cache_clear()
        try:
            with patch(
                "hypothesis_model_drafter.rebuild_research_engine_state",
                return_value=([], fixture),
            ):
                before = canonical_research_engine_snapshot()
                fixture["mutated"] = True
                after = canonical_research_engine_snapshot()
            self.assertEqual(before, after)
            self.assertNotIn(b"mutated", after[0])
        finally:
            canonical_research_engine_snapshot.cache_clear()

    def test_full_cli_dry_run_is_commit_bound_and_non_executable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "drafts.json"
            argv = [
                "hypothesis_model_drafter.py",
                "--lane",
                "brainstorm_queue",
                "--limit",
                "1",
                "--source-commit",
                "a" * 40,
                "--output",
                str(output),
            ]
            with (
                patch.object(sys, "argv", argv),
                patch(
                    "hypothesis_model_drafter.inspect_git_source_state",
                    return_value={
                        "source_commit": "a" * 40,
                        "source_tree_clean": True,
                        "source_main_ancestor": True,
                    },
                ),
                patch(
                    "hypothesis_model_drafter.load_json_from_source_commit",
                    side_effect=lambda _commit, path: load_json(
                        POLICY_PATH.parents[1] / path
                    ),
                ),
                redirect_stdout(io.StringIO()),
            ):
                self.assertEqual(0, main())
            batch = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual("a" * 40, batch["source_commit"])
        self.assertEqual(1, batch["request_count"])
        self.assertFalse(batch["live"])
        self.assertTrue(batch["source_tree_clean"])
        self.assertTrue(batch["source_main_ancestor"])
        self.assertFalse(batch["provider_transport_attested"])
        self.assertEqual(0, batch["scientific_outcomes"])
        self.assertEqual(0, batch["ranker_labels"])
        self.assertEqual(0, batch["route_promotions"])
        self.assertFalse(batch["exact_target_execution"])
        self.assertFalse(batch["any_output_executable"])
        self.assertRegex(
            batch["requests"][0]["inference_request_sha256"],
            r"^[0-9a-f]{64}$",
        )

    def test_cli_rejects_source_state_change_during_packet_build(self) -> None:
        before = {
            "source_commit": "a" * 40,
            "source_tree_clean": True,
            "source_main_ancestor": True,
        }
        after = dict(before)
        after["source_tree_clean"] = False
        with tempfile.TemporaryDirectory() as directory:
            argv = [
                "hypothesis_model_drafter.py",
                "--lane",
                "brainstorm_queue",
                "--limit",
                "1",
                "--output",
                str(Path(directory) / "drafts.json"),
            ]
            with (
                patch.object(sys, "argv", argv),
                patch(
                    "hypothesis_model_drafter.inspect_git_source_state",
                    side_effect=[before, after],
                ),
                patch(
                    "hypothesis_model_drafter.load_json_from_source_commit",
                    side_effect=lambda _commit, path: load_json(
                        POLICY_PATH.parents[1] / path
                    ),
                ),
            ):
                with self.assertRaisesRegex(SystemExit, "changed while building"):
                    main()

    def test_live_batch_checkpoints_before_later_provider_failure(self) -> None:
        fields = self.policy["output_contract"]["required_fields"]
        fragment = fragment_fixture(fields)
        fragment["abstain"] = False
        raw = json.dumps(fragment, separators=(",", ":"))
        model = self.policy["providers"]["featherless"][
            "preferred_models"
        ][0]
        body = json.dumps(
            {
                "id": "resp-first",
                "model": model,
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {"content": raw},
                    }
                ],
            },
            separators=(",", ":"),
        )
        first = {
            "content": raw,
            "body": body,
            "provider_response_sha256": hashlib.sha256(
                body.encode("utf-8")
            ).hexdigest(),
            "metadata": {
                "response_id": "resp-first",
                "created": None,
                "reported_model": model,
                "system_fingerprint": None,
                "finish_reason": "stop",
                "usage": None,
            },
        }
        source_state = {
            "source_commit": "a" * 40,
            "source_tree_clean": True,
            "source_main_ancestor": True,
        }
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "drafts.json"
            argv = [
                "hypothesis_model_drafter.py",
                "--lane",
                "brainstorm_queue",
                "--limit",
                "3",
                "--source-commit",
                "a" * 40,
                "--live",
                "--output",
                str(output),
            ]
            with (
                patch.object(sys, "argv", argv),
                patch.dict(
                    os.environ,
                    {
                        "HYPOTHESIS_DRAFTER_LIVE": "1",
                        "FEATHERLESS_API_KEY": "fixture-secret",
                    },
                    clear=False,
                ),
                patch(
                    "hypothesis_model_drafter.inspect_git_source_state",
                    return_value=source_state,
                ),
                patch(
                    "hypothesis_model_drafter.load_json_from_source_commit",
                    side_effect=lambda _commit, path: load_json(
                        POLICY_PATH.parents[1] / path
                    ),
                ),
                patch(
                    "hypothesis_model_drafter.call_openai_compatible",
                    side_effect=[first, RuntimeError("provider unavailable")],
                ),
                redirect_stdout(io.StringIO()),
            ):
                self.assertEqual(2, main())
            batch = json.loads(output.read_text(encoding="utf-8"))
            self.assertFalse(Path(str(output) + ".lock").exists())
            self.assertEqual([], list(output.parent.glob(f".{output.name}.*.tmp")))
        self.assertEqual("partial_provider_failure", batch["completion_status"])
        self.assertEqual(1, batch["completed_response_count"])
        self.assertEqual(2, batch["error_count"])
        self.assertEqual("resp-first", batch["responses"][0]["provider_metadata"]["response_id"])
        self.assertTrue(batch["errors"][0]["attempted"])
        self.assertFalse(batch["errors"][1]["attempted"])
        self.assertEqual(
            "not_attempted_after_prior_failure",
            batch["errors"][1]["classification"],
        )
        self.assertEqual("none", batch["errors"][0]["authorization"])
        self.assertFalse(batch["errors"][0]["executable"])
        self.assertEqual("provider unavailable", batch["errors"][0]["error_message"])
        self.assertRegex(batch["errors"][0]["error_message_sha256"], r"^[0-9a-f]{64}$")
        self.assertIsNone(batch["errors"][0]["http_status"])
        self.assertIsNone(batch["errors"][0]["error_body"])
        self.assertFalse(batch["errors"][0]["error_body_truncated"])

    def test_typed_evidence_is_default_and_refreshes_stale_seed(self) -> None:
        packets = build_request_packets(
            self.policy,
            self.engine_state,
            limit=10,
            typed_evidence_state=self.typed_evidence_state,
        )
        self.assertEqual(1, len(packets))
        self.assertEqual("HGS-3266E42A729C", packets[0]["seed_id"])
        self.assertEqual([], packets[0]["existing_proposal_ids"])

    def test_historical_proposal_is_not_compatible_with_current_seed(self) -> None:
        packets = build_request_packets(
            self.policy,
            self.engine_state,
            limit=10,
            typed_evidence_state=self.typed_evidence_state,
            include_submitted=True,
        )
        self.assertEqual(1, len(packets))
        packet = packets[0]
        self.assertEqual("typed_evidence", packet["lane"])
        self.assertTrue(packet["input_provenance_bound"])
        self.assertEqual("HGS-3266E42A729C", packet["seed_id"])
        self.assertEqual([], packet["existing_proposal_ids"])
        self.assertTrue(packet["allowed_evidence_claim_ids"])
        self.assertTrue(packet["evidence_manifest"])
        self.assertEqual("none", packet["authorization"])
        self.assertFalse(packet["executable"])

    def test_source_claim_mutation_is_rejected_as_noncanonical(self) -> None:
        changed = copy.deepcopy(self.typed_evidence_state)
        claim_id = next(
            item
            for item in changed["cells"]
            if item["cell_id"] == "CELL-M-PKC-SMOOTH-M16"
        )["source_claim_ids"][0]
        claim = next(item for item in changed["source_claims"] if item["id"] == claim_id)
        claim["statement"] += " Changed fixture."
        with self.assertRaises(ValueError):
            build_request_packets(
                self.policy,
                self.engine_state,
                limit=10,
                typed_evidence_state=changed,
                include_submitted=True,
            )

    def test_numeric_type_drift_is_rejected_as_noncanonical(self) -> None:
        changed = copy.deepcopy(self.engine_state)
        changed["counts"]["normalized_hypotheses"] = float(
            changed["counts"]["normalized_hypotheses"]
        )
        with self.assertRaises(ValueError):
            build_request_packets(
                self.policy,
                changed,
                limit=10,
                typed_evidence_state=self.typed_evidence_state,
                include_submitted=True,
            )

    def test_policy_mutation_invalidates_request_identity(self) -> None:
        baseline = build_request_packets(
            self.policy,
            self.engine_state,
            limit=10,
            typed_evidence_state=self.typed_evidence_state,
            include_submitted=True,
        )[0]
        changed = copy.deepcopy(self.policy)
        changed["lanes"]["typed_evidence"]["boundary"] += " Fixture."
        mutated = build_request_packets(
            changed,
            self.engine_state,
            limit=10,
            typed_evidence_state=self.typed_evidence_state,
            include_submitted=True,
        )[0]
        self.assertNotEqual(baseline["policy_sha256"], mutated["policy_sha256"])
        self.assertNotEqual(
            baseline["scientific_packet_sha256"],
            mutated["scientific_packet_sha256"],
        )

    def test_decision_binding_fails_closed(self) -> None:
        wrong_mode = copy.deepcopy(self.decision_state)
        wrong_mode["next_phase_gate"]["current_mode"] = "wrong-mode"
        with self.assertRaises(ValueError):
            build_request_packets(
                self.policy,
                self.engine_state,
                limit=10,
                typed_evidence_state=self.typed_evidence_state,
                decision_state=wrong_mode,
                include_submitted=True,
            )
        changed = copy.deepcopy(self.decision_state)
        changed["next_phase_gate"]["final_review"] += " Fixture."
        with self.assertRaises(ValueError):
            build_request_packets(
                self.policy,
                self.engine_state,
                limit=10,
                typed_evidence_state=self.typed_evidence_state,
                decision_state=changed,
                include_submitted=True,
            )

    def test_missing_claim_and_cell_digest_drift_fail_closed(self) -> None:
        missing = copy.deepcopy(self.typed_evidence_state)
        m16_cell = next(
            item
            for item in missing["cells"]
            if item["cell_id"] == "CELL-M-PKC-SMOOTH-M16"
        )
        removed_claim_id = m16_cell["source_claim_ids"][0]
        missing["source_claims"] = [
            item
            for item in missing["source_claims"]
            if item["id"] != removed_claim_id
        ]
        with self.assertRaises(ValueError):
            build_request_packets(
                self.policy,
                self.engine_state,
                limit=10,
                typed_evidence_state=missing,
                include_submitted=True,
            )
        drifted = copy.deepcopy(self.typed_evidence_state)
        cell = next(
            item
            for item in drifted["cells"]
            if item["cell_id"] == "CELL-M-PKC-SMOOTH-M16"
        )
        cell["evidence_digest"] = "0" * 64
        with self.assertRaises(ValueError):
            build_request_packets(
                self.policy,
                self.engine_state,
                limit=10,
                typed_evidence_state=drifted,
                include_submitted=True,
            )
        route_drift = copy.deepcopy(self.engine_state)
        seed = next(
            item
            for item in route_drift["hypothesis_generation"]["generated_seeds"]
            if item["seed_id"] == "HGS-3266E42A729C"
        )
        seed["route_id"] = "R-WRONG"
        with self.assertRaises(ValueError):
            build_request_packets(
                self.policy,
                route_drift,
                limit=10,
                typed_evidence_state=self.typed_evidence_state,
                include_submitted=True,
            )
        semantic_drift = copy.deepcopy(self.engine_state)
        seed = next(
            item
            for item in semantic_drift["hypothesis_generation"]["generated_seeds"]
            if item["seed_id"] == "HGS-3266E42A729C"
        )
        seed["research_question"] = (
            "Use nonce leakage and multi-target amortization under a false plain tag."
        )
        with self.assertRaises(ValueError):
            build_request_packets(
                self.policy,
                semantic_drift,
                limit=10,
                typed_evidence_state=self.typed_evidence_state,
                include_submitted=True,
            )

    def test_evidence_manifest_binds_repository_bytes(self) -> None:
        packet = build_request_packets(
            self.policy,
            self.engine_state,
            limit=10,
            typed_evidence_state=self.typed_evidence_state,
            include_submitted=True,
        )[0]
        root = POLICY_PATH.parents[1]
        seed = next(
            item
            for item in self.engine_state["hypothesis_generation"][
                "generated_seeds"
            ]
            if item["seed_id"] == "HGS-3266E42A729C"
        )
        manifest_paths = {entry["path"] for entry in packet["evidence_manifest"]}
        self.assertTrue(set(seed["evidence_inputs"]) <= manifest_paths)
        self.assertEqual(
            set(seed["evidence_inputs"]),
            {
                entry["path"]
                for entry in packet["context_document_manifest"]
            },
        )
        manifest_by_path = {
            entry["path"]: entry for entry in packet["evidence_manifest"]
        }
        for entry in packet["context_document_manifest"]:
            self.assertEqual(
                manifest_by_path[entry["path"]]["sha256"], entry["sha256"]
            )
        for entry in packet["evidence_manifest"]:
            actual = hashlib.sha256(
                (root / Path(entry["path"])).read_bytes()
            ).hexdigest()
            self.assertEqual(actual, entry["sha256"])

    def test_commit_snapshot_reads_the_immutable_git_blob(self) -> None:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=POLICY_PATH.parents[1],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        path = "experiments/p1_petit/README.md"
        with patch.object(
            Path,
            "open",
            side_effect=AssertionError("commit-bound evidence must not use worktree bytes"),
        ):
            snapshot = build_repository_snapshot(
                [path],
                max_file_bytes=1024 * 1024,
                max_total_bytes=1024 * 1024,
                source_commit=head,
            )
        expected = subprocess.run(
            ["git", "cat-file", "blob", f"{head}:{path}"],
            cwd=POLICY_PATH.parents[1],
            check=True,
            capture_output=True,
        ).stdout
        self.assertEqual(expected, snapshot[path]["raw"])
        self.assertEqual(hashlib.sha256(expected).hexdigest(), snapshot[path]["sha256"])

    def test_evidence_digest_changes_the_scientific_packet_identity(self) -> None:
        left = build_request_packets(
            self.policy,
            self.engine_state,
            limit=10,
            typed_evidence_state=self.typed_evidence_state,
            include_submitted=True,
        )[0]
        paths = [entry["path"] for entry in left["evidence_manifest"]]
        changed_snapshot = build_repository_snapshot(
            paths,
            max_file_bytes=self.policy["limits"]["max_evidence_file_bytes"],
            max_total_bytes=self.policy["limits"]["max_evidence_total_bytes"],
        )
        changed_snapshot[paths[0]] = dict(changed_snapshot[paths[0]])
        changed_snapshot[paths[0]]["sha256"] = "1" * 64
        with patch(
            "hypothesis_model_drafter.build_repository_snapshot",
            return_value=changed_snapshot,
        ):
            right = build_request_packets(
                self.policy,
                self.engine_state,
                limit=10,
                typed_evidence_state=self.typed_evidence_state,
                include_submitted=True,
            )[0]
        self.assertNotEqual(
            left["evidence_manifest_sha256"],
            right["evidence_manifest_sha256"],
        )
        self.assertNotEqual(
            left["scientific_packet_sha256"],
            right["scientific_packet_sha256"],
        )

    def test_evidence_manifest_must_cover_each_source_claim(self) -> None:
        changed = copy.deepcopy(self.typed_evidence_state)
        cell = next(
            item
            for item in changed["cells"]
            if item["cell_id"] == "CELL-M-PKC-SMOOTH-M16"
        )
        cell["evidence_paths"] = []
        with self.assertRaises(ValueError):
            build_request_packets(
                self.policy,
                self.engine_state,
                limit=10,
                typed_evidence_state=changed,
                include_submitted=True,
            )

    def test_source_packet_capacity_bounds_fail_closed(self) -> None:
        claim_bound = copy.deepcopy(self.policy)
        claim_bound["limits"]["max_source_claims_per_request"] = 2
        with self.assertRaises(ValueError):
            build_request_packets(
                claim_bound,
                self.engine_state,
                limit=10,
                typed_evidence_state=self.typed_evidence_state,
                include_submitted=True,
            )
        context_bound = copy.deepcopy(self.policy)
        context_bound["limits"]["max_context_bytes_per_request"] = 4096
        with self.assertRaises(ValueError):
            build_request_packets(
                context_bound,
                self.engine_state,
                limit=10,
                typed_evidence_state=self.typed_evidence_state,
                include_submitted=True,
            )
        prompt_bound = copy.deepcopy(self.policy)
        prompt_bound["limits"]["max_prompt_bytes"] = 4096
        with self.assertRaises(ValueError):
            build_request_packets(
                prompt_bound,
                self.engine_state,
                limit=10,
                typed_evidence_state=self.typed_evidence_state,
                include_submitted=True,
            )

    def test_context_byte_bound_is_checked_before_file_read(self) -> None:
        with patch.object(
            Path,
            "read_bytes",
            side_effect=AssertionError("bounded context should not be read"),
        ):
            with self.assertRaisesRegex(ValueError, "byte bound"):
                build_context_documents(
                    ["experiments/p1_petit/README.md"], max_total_bytes=1
                )

    def test_evidence_byte_bound_is_checked_before_hashing(self) -> None:
        with patch.object(
            Path,
            "open",
            side_effect=AssertionError("oversized evidence should not be read"),
        ):
            with self.assertRaisesRegex(ValueError, "policy bound"):
                build_repository_snapshot(
                    ["experiments/p1_petit/README.md"],
                    max_file_bytes=1,
                    max_total_bytes=1,
                )

    def test_output_lease_rejects_a_second_writer(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "drafts.json"
            descriptor, lease_path = acquire_output_lease(output)
            try:
                with self.assertRaisesRegex(RuntimeError, "writer lease"):
                    acquire_output_lease(output)
            finally:
                release_output_lease(descriptor, lease_path)
            self.assertFalse(lease_path.exists())

    def test_output_lease_cleans_up_when_metadata_write_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "drafts.json"
            lease_path = Path(str(output) + ".lock")
            with patch(
                "hypothesis_model_drafter.os.write",
                side_effect=OSError("injected lease metadata failure"),
            ):
                with self.assertRaisesRegex(OSError, "lease metadata failure"):
                    acquire_output_lease(output)
            self.assertFalse(lease_path.exists())
            descriptor, acquired_path = acquire_output_lease(output)
            release_output_lease(descriptor, acquired_path)

    def test_atomic_output_cleans_unique_temp_after_replace_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "drafts.json"
            with patch(
                "hypothesis_model_drafter.os.replace",
                side_effect=OSError("injected replace failure"),
            ):
                with self.assertRaisesRegex(OSError, "injected replace failure"):
                    atomic_write_output(output, {"status": "fixture"})
            self.assertEqual([], list(output.parent.glob(f".{output.name}.*.tmp")))
            self.assertFalse(output.exists())

    def test_drafter_policy_cannot_cross_authorization_boundary(self) -> None:
        changed = copy.deepcopy(self.policy)
        changed["safety"]["authorized_count"] = 1
        with self.assertRaises(ValueError):
            validate_policy(changed)
        changed = copy.deepcopy(self.policy)
        changed["safety"]["recommended_count"] = 1
        with self.assertRaises(ValueError):
            validate_policy(changed)
        changed = copy.deepcopy(self.policy)
        changed["safety"]["ranker_label_count"] = 1
        with self.assertRaises(ValueError):
            validate_policy(changed)
        changed = copy.deepcopy(self.policy)
        changed["safety"]["submitted_seed_live_replay"] = True
        with self.assertRaises(ValueError):
            validate_policy(changed)
        changed = copy.deepcopy(self.policy)
        changed["limits"]["max_concurrency"] = 2
        with self.assertRaises(ValueError):
            validate_policy(changed)
        changed = copy.deepcopy(self.policy)
        changed["default_lane"] = "brainstorm_queue"
        with self.assertRaises(ValueError):
            validate_policy(changed)
        changed = copy.deepcopy(self.policy)
        changed["lanes"]["brainstorm_queue"]["input_provenance_bound"] = True
        with self.assertRaises(ValueError):
            validate_policy(changed)

    def test_provider_secret_cannot_be_redirected(self) -> None:
        changed = copy.deepcopy(self.policy)
        changed["providers"]["featherless"]["base_url"] = (
            "https://attacker.invalid/v1"
        )
        with self.assertRaises(ValueError):
            validate_policy(changed)
        changed = copy.deepcopy(self.policy)
        changed["providers"]["featherless"]["secret_env"] = "GH_TOKEN"
        with self.assertRaises(ValueError):
            validate_policy(changed)
        changed = copy.deepcopy(self.policy)
        changed["providers"]["featherless"]["preferred_models"] = [{}]
        with self.assertRaises(ValueError):
            validate_policy(changed)

    def test_fragment_requires_exact_fields_and_boolean_abstention(self) -> None:
        fields = self.policy["output_contract"]["required_fields"]
        value = fragment_fixture(fields)
        value["abstain"] = True
        for field in EVIDENCE_MAPPED_FIELDS:
            value[field] = ABSTENTION_SENTINEL
        fragment, problems = parse_fragment(
            json.dumps(value),
            fields,
            self.policy["output_contract"]["prohibited_claims"],
        )
        self.assertEqual([], problems)
        self.assertEqual(value, fragment)
        value["decorative_confidence"] = 0.99
        _, problems = parse_fragment(
            json.dumps(value),
            fields,
            self.policy["output_contract"]["prohibited_claims"],
        )
        self.assertIn("response_fields_do_not_match_contract", problems)

    def test_fragment_flags_prohibited_claims_and_invalid_missing_evidence(self) -> None:
        fields = self.policy["output_contract"]["required_fields"]
        value = fragment_fixture(fields)
        value["abstain"] = False
        value["exact_map"] = "This is proved."
        value["missing_evidence"] = ["source", "source"]
        _, problems = parse_fragment(
            json.dumps(value),
            fields,
            self.policy["output_contract"]["prohibited_claims"],
        )
        self.assertIn("prohibited_claim:proved", problems)
        self.assertIn("missing_evidence_items_are_invalid", problems)
        value["missing_evidence"] = [{}]
        _, problems = parse_fragment(json.dumps(value), fields)
        self.assertIn("missing_evidence_items_are_invalid", problems)

    def test_provenance_bound_fragment_cites_only_supplied_claims(self) -> None:
        fields = self.policy["output_contract"]["required_fields"]
        value = fragment_fixture(fields)
        value["abstain"] = False
        value["evidence_claim_ids"] = ["SC-ONE"]
        value["field_evidence_claim_ids"] = {
            field: ["SC-ONE"] for field in EVIDENCE_MAPPED_FIELDS
        }
        _, problems = parse_fragment(
            json.dumps(value),
            fields,
            allowed_evidence_claim_ids=["SC-ONE"],
            provenance_bound=True,
        )
        self.assertEqual([], problems)
        value["evidence_claim_ids"] = ["SC-INVENTED"]
        value["field_evidence_claim_ids"] = {
            field: ["SC-INVENTED"] for field in EVIDENCE_MAPPED_FIELDS
        }
        _, problems = parse_fragment(
            json.dumps(value),
            fields,
            allowed_evidence_claim_ids=["SC-ONE"],
            provenance_bound=True,
        )
        self.assertIn("evidence_claim_ids_not_supplied", problems)
        value["evidence_claim_ids"] = []
        value["field_evidence_claim_ids"] = {
            field: [] for field in EVIDENCE_MAPPED_FIELDS
        }
        _, problems = parse_fragment(
            json.dumps(value),
            fields,
            allowed_evidence_claim_ids=["SC-ONE"],
            provenance_bound=True,
        )
        self.assertIn(
            "provenance_bound_fragment_has_no_evidence_claim_ids", problems
        )

    def test_honest_abstention_does_not_require_false_evidence_links(self) -> None:
        fields = self.policy["output_contract"]["required_fields"]
        value = fragment_fixture(fields)
        value["abstain"] = True
        for field in EVIDENCE_MAPPED_FIELDS:
            value[field] = ABSTENTION_SENTINEL
        value["evidence_claim_ids"] = []
        value["field_evidence_claim_ids"] = {
            field: [] for field in EVIDENCE_MAPPED_FIELDS
        }
        _, problems = parse_fragment(
            json.dumps(value),
            fields,
            allowed_evidence_claim_ids=["SC-ONE"],
            provenance_bound=True,
        )
        self.assertEqual([], problems)
        value["missing_evidence"] = []
        _, problems = parse_fragment(
            json.dumps(value),
            fields,
            allowed_evidence_claim_ids=["SC-ONE"],
            provenance_bound=True,
        )
        self.assertIn("abstention_requires_missing_evidence", problems)
        value["missing_evidence"] = ["exact algebraic map"]
        value["exact_map"] = "A substantive but uncited map"
        _, problems = parse_fragment(
            json.dumps(value),
            fields,
            allowed_evidence_claim_ids=["SC-ONE"],
            provenance_bound=True,
        )
        self.assertIn("uncited_abstention_text:exact_map", problems)

    def test_strict_json_rejects_duplicate_nonfinite_deep_and_surrogate(self) -> None:
        fields = self.policy["output_contract"]["required_fields"]
        value = fragment_fixture(fields)
        value["abstain"] = False
        raw = json.dumps(value)[:-1] + ',"exact_map":"duplicate"}'
        _, problems = parse_fragment(raw, fields)
        self.assertEqual(["response_is_not_strict_json"], problems)
        _, problems = parse_fragment('{"value":NaN}', fields)
        self.assertEqual(["response_is_not_strict_json"], problems)
        nested: object = "leaf"
        for _ in range(70):
            nested = [nested]
        value["exact_map"] = nested
        _, problems = parse_fragment(json.dumps(value), fields)
        self.assertEqual(["response_is_not_strict_json"], problems)
        _, problems = parse_fragment('{"value":"\\ud800"}', fields)
        self.assertEqual(["response_is_not_strict_json"], problems)
        _, problems = parse_fragment('{"value":' + "9" * 5000 + "}", fields)
        self.assertEqual(["response_is_not_strict_json"], problems)

    def test_negated_prohibited_phrases_do_not_create_false_positive(self) -> None:
        fields = self.policy["output_contract"]["required_fields"]
        value = fragment_fixture(fields)
        value["abstain"] = False
        value["exact_map"] = (
            "This remains unproved and gives no experiment authorization."
        )
        _, problems = parse_fragment(
            json.dumps(value),
            fields,
            self.policy["output_contract"]["prohibited_claims"],
        )
        self.assertFalse(
            any(problem.startswith("prohibited_claim:") for problem in problems)
        )

    def test_brainstorm_fragment_cannot_claim_source_grounding(self) -> None:
        fields = self.policy["output_contract"]["required_fields"]
        value = fragment_fixture(fields)
        value["abstain"] = False
        value["evidence_claim_ids"] = ["SC-ONE"]
        value["field_evidence_claim_ids"] = {
            field: ["SC-ONE"] for field in EVIDENCE_MAPPED_FIELDS
        }
        _, problems = parse_fragment(
            json.dumps(value),
            fields,
            allowed_evidence_claim_ids=[],
            provenance_bound=False,
        )
        self.assertIn("evidence_claim_ids_not_supplied", problems)
        self.assertIn("brainstorm_fragment_claims_source_grounding", problems)
        self.assertIn(
            "brainstorm_field_claims_source_grounding:new_premise", problems
        )

    def test_per_field_evidence_map_is_exact_and_nonempty(self) -> None:
        fields = self.policy["output_contract"]["required_fields"]
        value = fragment_fixture(fields)
        value["abstain"] = False
        value["evidence_claim_ids"] = ["SC-ONE"]
        value["field_evidence_claim_ids"] = {
            field: ["SC-ONE"] for field in EVIDENCE_MAPPED_FIELDS
        }
        value["field_evidence_claim_ids"]["recovery_map"] = []
        _, problems = parse_fragment(
            json.dumps(value),
            fields,
            allowed_evidence_claim_ids=["SC-ONE"],
            provenance_bound=True,
        )
        self.assertIn(
            "provenance_bound_field_has_no_claim_link:recovery_map", problems
        )
        value["field_evidence_claim_ids"]["recovery_map"] = ["SC-ONE"]
        value["evidence_claim_ids"] = ["SC-ONE", "SC-TWO"]
        _, problems = parse_fragment(
            json.dumps(value),
            fields,
            allowed_evidence_claim_ids=["SC-ONE", "SC-TWO"],
            provenance_bound=True,
        )
        self.assertIn("evidence_claim_ids_do_not_match_field_union", problems)

    def test_cloudflare_1010_is_not_misreported_as_a_bad_secret(self) -> None:
        self.assertEqual(
            "network_policy_blocked",
            classify_http_error(403, "error code: 1010"),
        )
        self.assertEqual(
            "authentication_or_plan_rejected",
            classify_http_error(403, "model not available on plan"),
        )

    def test_featherless_is_drafter_only_with_direct_fallbacks(self) -> None:
        providers = self.policy["providers"]
        self.assertIn("deepseek-ai/DeepSeek-V4-Flash", providers["featherless"]["preferred_models"])
        self.assertEqual("DEEPSEEK_API_KEY", providers["deepseek_direct"]["secret_env"])
        self.assertEqual("KIMI_API_KEY", providers["moonshot_direct"]["secret_env"])
        self.assertFalse(self.policy["safety"]["self_review_satisfies_independence"])


if __name__ == "__main__":
    unittest.main()
