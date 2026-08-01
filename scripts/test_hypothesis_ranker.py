#!/usr/bin/env python3
"""Fault-injection tests for the shadow hypothesis ranker."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import hypothesis_ranker as ranker
from hypothesis_funnel import STATE_PATH as FUNNEL_STATE_PATH, load_policy
from hypothesis_ranker import (
    ENGINE_STATE_PATH,
    REVIEW_LEDGER_PATH,
    SPEC_PATH,
    STATE_PATH,
    activation_report,
    aggregate_training_examples,
    build_state,
    candidate_evidence_manifest,
    feature_vector,
    learned_score,
    load_json,
    load_review_ledger,
    load_review_registry,
    proposal_review_bundle,
    review_ledger_entry_digest,
    review_labels,
    sha256_json,
    validate_current_review_bindings,
    validate_model,
)
from sync_hypothesis_review_ledger import (
    append_missing as append_missing_reviews,
    check as check_review_sync,
    current_entries as current_review_entries,
    load_existing_reviews,
)


class HypothesisRankerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy = load_policy()
        cls.funnel = load_json(FUNNEL_STATE_PATH)
        cls.spec = load_json(SPEC_PATH)
        cls.state = load_json(STATE_PATH)
        cls.ledger = load_review_ledger()

    @staticmethod
    def registered_fixture(ledger: list[dict]) -> dict[str, dict]:
        registry = {}
        for entry in ledger:
            candidate_version = sha256_json(
                {
                    "candidate_snapshot": entry["candidate_snapshot"],
                    "reviewed_evidence_closure_sha256": entry.get(
                        "reviewed_evidence_closure_sha256"
                    ),
                }
            )
            registry[entry["label_id"]] = {
                "ledger_entry_sha256": entry.get("ledger_entry_sha256"),
                "candidate_version_sha256": candidate_version,
            }
        return registry

    def test_ranker_is_inactive_and_non_authorizing(self) -> None:
        self.assertEqual(
            self.state["status"], "inactive_insufficient_independent_labels"
        )
        self.assertFalse(self.state["selection_influence"])
        self.assertFalse(self.state["authorization_capability"])
        self.assertFalse(self.state["route_promotion_capability"])
        self.assertEqual(
            self.state["activation"]["observed"]["eligible_candidate_versions"], 0
        )

    def test_migrated_reviews_are_not_training_labels(self) -> None:
        self.assertEqual(len(self.state["labels"]), 6)
        for label in self.state["labels"]:
            self.assertFalse(label["training_eligible"])
            self.assertIn("independence_not_established", label["exclusion_reasons"])
            self.assertIn("historical_migration", label["exclusion_reasons"])
            self.assertIn(
                "reviewed_evidence_closure_unbound", label["exclusion_reasons"]
            )

    def test_scientific_reviews_rebind_without_duplicate_labels(self) -> None:
        current_root = self.funnel["bulk_contract"]["merkle_root_sha256"]
        current = [
            item
            for item in self.ledger
            if item["batch_merkle_root_sha256"] == current_root
        ]
        self.assertEqual(0, len(current))
        self.assertEqual(6, len(self.ledger))
        bindings = validate_current_review_bindings(
            self.ledger, self.policy, self.funnel
        )
        self.assertEqual(3, len(bindings))
        self.assertTrue(
            all(item["reused_across_evidence_snapshot"] for item in bindings)
        )
        self.assertTrue(
            all(not item["evidence_closure_current"] for item in bindings)
        )
        self.assertEqual(
            {
                "HFR-2026-07-31-004",
                "HFR-2026-07-31-005",
                "HFR-2026-07-31-006",
            },
            {item["review_id"] for item in bindings},
        )

    def test_review_sync_does_not_duplicate_labels_after_evidence_refresh(self) -> None:
        expected = current_review_entries()
        self.assertEqual([], check_review_sync(self.ledger, expected))
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "ledger.jsonl"
            original = "".join(
                json.dumps(item, sort_keys=True, separators=(",", ":")) + "\n"
                for item in self.ledger
            )
            path.write_text(original, encoding="ascii")
            self.assertEqual(
                0, append_missing_reviews(path, self.ledger, expected)
            )
            self.assertEqual(original, path.read_text(encoding="ascii"))

    def test_untrained_model_emits_no_scores_or_reordering(self) -> None:
        self.assertTrue(
            all(item["learned_score"] is None for item in self.state["shadow_ranking"])
        )
        self.assertEqual(
            [item["semantic_signature_sha256"] for item in self.state["shadow_ranking"]],
            [item["semantic_signature_sha256"] for item in self.funnel["review_queue"]],
        )

    def test_forbidden_historical_fields_do_not_enter_features(self) -> None:
        candidate = copy.deepcopy(self.funnel["review_queue"][0])
        original = feature_vector(candidate, self.spec)
        candidate["source_hard_gate"] = "KILL"
        candidate["source_portfolio"] = "KILLED"
        candidate["source_canonical"] = "fabricated"
        candidate["seed_id"] = "HQS1-" + "F" * 32
        self.assertEqual(original, feature_vector(candidate, self.spec))
        self.assertTrue(
            set(original).isdisjoint(self.spec["feature_contract"]["forbidden_features"])
        )

    def test_independence_is_required_but_not_sufficient_for_activation(self) -> None:
        ledger = copy.deepcopy(current_review_entries())
        fallback_binding = copy.deepcopy(
            next(
                entry["review_record"]["canonical_binding"]
                for entry in ledger
                if entry["review_record"]["canonical_binding"]["kind"]
                == "research_engine_proposal"
            )
        )
        for entry in ledger:
            review = entry["review_record"]
            review["independence"] = {
                "source": True,
                "model_family": True,
                "context": True,
            }
            review["reviewer"]["role"] = "independent-scientific-review"
            review["canonical_binding"] = copy.deepcopy(fallback_binding)
            manifest = candidate_evidence_manifest(review)
            entry["reviewed_evidence_manifest"] = manifest
            entry["reviewed_evidence_closure_sha256"] = sha256_json(manifest)
            entry["review_record_sha256"] = "fixture"
        with patch.object(
            ranker,
            "proposal_review_bundle",
            side_effect=lambda review: (
                [],
                "negative"
                if review["verdict"] == "reject_known_or_unsupported"
                else "positive",
            ),
        ):
            labels = review_labels(
                ledger,
                self.spec,
                review_registry=self.registered_fixture(ledger),
            )
        self.assertEqual(sum(item["training_eligible"] for item in labels), 3)
        examples = aggregate_training_examples(labels)
        self.assertEqual(len(examples), 3)
        self.assertEqual(sum(item["training_eligible"] for item in examples), 3)
        native_outcomes = len(load_json(ENGINE_STATE_PATH).get("native_outcomes", []))
        activation = activation_report(examples, native_outcomes, self.spec)
        self.assertFalse(activation["ready_for_training"])
        self.assertIn("eligible_candidate_versions", activation["unmet"])
        self.assertIn("negative_labels", activation["unmet"])

    def test_evidence_change_invalidates_review_binding(self) -> None:
        ledger = copy.deepcopy(self.ledger)
        for entry in ledger:
            entry["reviewed_evidence_closure_sha256"] = "f" * 64
        labels = review_labels(ledger, self.spec)
        self.assertTrue(
            all(
                "reviewed_evidence_closure_stale" in item["exclusion_reasons"]
                for item in labels
            )
        )

    def test_unregistered_digest_valid_review_cannot_train(self) -> None:
        entry = copy.deepcopy(current_review_entries()[0])
        review = entry["review_record"]
        review["review_id"] = "HFR-FABRICATED-INDEPENDENT-001"
        review["reviewer"]["actor_id"] = "invented-reviewer"
        review["reviewer"]["role"] = "independent-scientific-review"
        review["independence"] = {
            "source": True,
            "model_family": True,
            "context": True,
        }
        entry["review_record_sha256"] = sha256_json(review)
        digest = review_ledger_entry_digest(entry)
        entry["ledger_entry_sha256"] = digest
        entry["label_id"] = f"HRL-{digest[:24].upper()}"
        labels = review_labels(
            [entry],
            self.spec,
        )
        self.assertFalse(labels[0]["training_eligible"])
        self.assertIn(
            "unregistered_review_artifact", labels[0]["exclusion_reasons"]
        )

    def test_self_declared_independence_needs_generation_provenance(self) -> None:
        entry = copy.deepcopy(current_review_entries()[0])
        entry["review_record"]["independence"] = {
            "source": True,
            "model_family": True,
            "context": True,
        }
        entry["review_record"]["reviewer"]["role"] = (
            "independent-scientific-review"
        )
        labels = review_labels(
            [entry],
            self.spec,
            review_registry=self.registered_fixture([entry]),
        )
        self.assertFalse(labels[0]["training_eligible"])
        self.assertIn(
            "independence_provenance_unverified",
            labels[0]["exclusion_reasons"],
        )

    def test_five_role_bundle_is_checked_from_actual_review_artifacts(self) -> None:
        entry = copy.deepcopy(current_review_entries()[0])
        review = entry["review_record"]
        proposal_id = review["canonical_binding"]["proposal_id"]
        proposal_path = ranker.PROPOSAL_DIR / f"{proposal_id}.json"
        proposal = load_json(proposal_path)
        policy = load_json(ranker.GENERATION_POLICY_PATH)
        roles = policy["quality_gate"]["required_review_roles"]
        independent_roles = set(
            policy["quality_gate"]["required_independent_roles"]
        )
        with tempfile.TemporaryDirectory(
            prefix=".ranker-review-bundle-", dir=ranker.ROOT
        ) as temporary:
            review_dir = Path(temporary)
            evidence_path = review_dir / "evidence.md"
            evidence_path.write_text("frozen evidence\n", encoding="utf-8")
            evidence_relative = evidence_path.relative_to(ranker.ROOT).as_posix()
            documents = []
            for index, role in enumerate(roles):
                document = {
                    "schema_version": "0.1",
                    "review_id": (
                        f"HGR-FIXTURE-{index:02d}-{role.upper().replace('_', '-')}"
                    ),
                    "proposal_id": proposal_id,
                    "proposal_sha256": ranker.proposal_sha256(proposal),
                    "reviewed_on": "2026-08-01",
                    "reviewer_id": f"fixture-reviewer-{index}",
                    "reviewer_role": role,
                    "source_independence": "declared_independent"
                    if role in independent_roles
                    else "unknown",
                    "reviewer_provenance": {
                        "family": f"fixture-family-{index % 2}",
                        "version": "1",
                        "session_id": f"fixture-session-{index}",
                        "context_sha256": sha256_json(
                            {"fixture_context": index}
                        ),
                        "prompt_sha256": sha256_json({"fixture_prompt": index}),
                        "blind_to_other_reviews": True,
                    },
                    "verdict": "pass",
                    "blocker_codes": [],
                    "summary": "Independent fixture review.",
                    "evidence_inputs": [evidence_relative],
                }
                documents.append(document)
                (review_dir / f"{document['review_id']}.json").write_text(
                    json.dumps(document), encoding="utf-8"
                )
            with patch.object(ranker, "PROPOSAL_REVIEW_DIR", review_dir):
                problems, direction = proposal_review_bundle(review)
                manifest = candidate_evidence_manifest(review)
            self.assertEqual(problems, [])
            self.assertEqual(direction, "positive")
            self.assertEqual(len(manifest), 11)
            self.assertIn(
                evidence_relative,
                {item["path"] for item in manifest},
            )
            self.assertTrue(
                {
                    path.relative_to(ranker.ROOT).as_posix()
                    for path in ranker.REVIEW_CONTRACT_PATHS
                }.issubset({item["path"] for item in manifest})
            )
            evidence_path.write_text("changed evidence\n", encoding="utf-8")
            with patch.object(ranker, "PROPOSAL_REVIEW_DIR", review_dir):
                changed_manifest = candidate_evidence_manifest(review)
            self.assertNotEqual(manifest, changed_manifest)

            independent_role = next(iter(independent_roles))
            mutated = next(
                item for item in documents if item["reviewer_role"] == independent_role
            )
            mutated["reviewer_provenance"]["context_sha256"] = proposal[
                "provenance"
            ]["context_sha256"]
            (review_dir / f"{mutated['review_id']}.json").write_text(
                json.dumps(mutated), encoding="utf-8"
            )
            with patch.object(ranker, "PROPOSAL_REVIEW_DIR", review_dir):
                problems, direction = proposal_review_bundle(review)
            self.assertIn(
                "required proposal review independence is not established",
                problems,
            )
            self.assertEqual(direction, "nonbinary")

    def test_scientific_review_registry_starts_empty_and_separate(self) -> None:
        self.assertEqual(load_review_registry(), {})
        self.assertNotEqual(
            ranker.REVIEW_REGISTRY_PATH,
            Path(ranker.POLICY_PATH),
        )

    def test_scientific_review_registry_fails_closed_without_protected_ref(self) -> None:
        failed = subprocess.CompletedProcess(
            args=["git", "rev-parse"], returncode=1, stdout="", stderr="missing"
        )
        with patch.object(ranker.subprocess, "run", return_value=failed):
            with self.assertRaisesRegex(ValueError, "protected ref cannot resolve"):
                load_review_registry()

    def test_scientific_review_registry_bootstrap_requires_empty_genesis(self) -> None:
        document = load_json(ranker.REVIEW_REGISTRY_PATH)
        document["status"] = "active"
        document["registrations"] = [
            {
                "registration_id": "HSRR-FABRICATED-001",
                "label_id": "HRL-FABRICATED",
                "ledger_entry_sha256": "a" * 64,
                "candidate_version_sha256": "b" * 64,
                "registered_on": "2026-08-01",
                "owner_decision_id": "RS-FABRICATED-001",
            }
        ]
        with patch.object(ranker, "load_json", return_value=document):
            with self.assertRaisesRegex(ValueError, "empty genesis"):
                load_review_registry()

    def test_registered_label_survives_current_queue_rotation(self) -> None:
        entry = copy.deepcopy(current_review_entries()[0])
        entry["review_record"]["independence"] = {
            "source": True,
            "model_family": True,
            "context": True,
        }
        entry["review_record"]["reviewer"]["role"] = "independent-review"
        entry["review_record_sha256"] = sha256_json(entry["review_record"])
        digest = review_ledger_entry_digest(entry)
        entry["ledger_entry_sha256"] = digest
        entry["label_id"] = f"HRL-{digest[:24].upper()}"
        with patch.object(
            ranker,
            "load_policy",
            side_effect=AssertionError("training labels must not read the current queue"),
        ), patch.object(
            ranker, "proposal_review_bundle", return_value=([], "positive")
        ):
            labels = review_labels(
                [entry],
                self.spec,
                review_registry=self.registered_fixture([entry]),
            )
        self.assertTrue(labels[0]["training_eligible"])

    def test_multiple_reviews_are_one_training_example(self) -> None:
        base = current_review_entries()[0]
        ledger = [copy.deepcopy(base), copy.deepcopy(base)]
        ledger[1]["review_record"]["review_id"] += "-SECOND"
        ledger[1]["review_record"]["reviewer"]["actor_id"] += "-second"
        for entry in ledger:
            entry["review_record"]["independence"] = {
                "source": True,
                "model_family": True,
                "context": True,
            }
            entry["review_record"]["reviewer"]["role"] = "independent-review"
            entry["review_record_sha256"] = sha256_json(entry["review_record"])
            digest = review_ledger_entry_digest(entry)
            entry["ledger_entry_sha256"] = digest
            entry["label_id"] = f"HRL-{digest[:24].upper()}"
        with patch.object(
            ranker, "proposal_review_bundle", return_value=([], "positive")
        ):
            examples = aggregate_training_examples(
                review_labels(
                    ledger,
                    self.spec,
                    review_registry=self.registered_fixture(ledger),
                )
            )
        self.assertEqual(len(examples), 1)
        self.assertEqual(examples[0]["review_count"], 2)
        self.assertTrue(examples[0]["training_eligible"])

    def test_disagreement_blocks_candidate_version_training(self) -> None:
        base = current_review_entries()[0]
        ledger = [copy.deepcopy(base), copy.deepcopy(base)]
        ledger[1]["review_record"]["review_id"] += "-DISSENT"
        ledger[1]["review_record"]["reviewer"]["actor_id"] += "-dissent"
        ledger[1]["review_record"]["verdict"] = "reject_known_or_unsupported"
        for entry in ledger:
            entry["review_record"]["independence"] = {
                "source": True,
                "model_family": True,
                "context": True,
            }
            entry["review_record"]["reviewer"]["role"] = "independent-review"
            entry["review_record_sha256"] = sha256_json(entry["review_record"])
            digest = review_ledger_entry_digest(entry)
            entry["ledger_entry_sha256"] = digest
            entry["label_id"] = f"HRL-{digest[:24].upper()}"
        with patch.object(
            ranker,
            "proposal_review_bundle",
            side_effect=lambda review: (
                [],
                "negative"
                if review["verdict"] == "reject_known_or_unsupported"
                else "positive",
            ),
        ):
            examples = aggregate_training_examples(
                review_labels(
                    ledger,
                    self.spec,
                    review_registry=self.registered_fixture(ledger),
                )
            )
        self.assertEqual(len(examples), 1)
        self.assertEqual(examples[0]["consensus"], "disagreement")
        self.assertFalse(examples[0]["training_eligible"])

    def test_selection_influence_fault_is_rejected(self) -> None:
        model_path = Path(self.state["source_bindings"]["model_path"])
        model = load_json(Path(__file__).resolve().parent.parent / model_path)
        model["selection_influence"] = True
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "model.json"
            path.write_text(json.dumps(model), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "cannot influence selection"):
                validate_model(model, self.spec, path)

    def test_persistent_review_ledger_is_digest_bound(self) -> None:
        ledger = copy.deepcopy(self.ledger)
        ledger[0]["review_record"]["limitations"].append("post-hoc mutation")
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "ledger.jsonl"
            path.write_text(
                "\n".join(json.dumps(item, sort_keys=True) for item in ledger) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "digest mismatch"):
                load_review_ledger(path)

    def test_sync_diagnostics_reject_corrupt_ledger_before_comparison(self) -> None:
        entry = copy.deepcopy(current_review_entries()[0])
        entry["ledger_entry_sha256"] = "f" * 64
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "ledger.jsonl"
            path.write_text(json.dumps(entry) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "entry digest mismatch"):
                load_existing_reviews(path)

    def test_legacy_review_prefix_is_byte_anchored(self) -> None:
        baseline = self.spec["label_contract"]["legacy_prefix"]
        lines = REVIEW_LEDGER_PATH.read_bytes().splitlines(keepends=True)
        self.assertEqual(
            hashlib.sha256(b"".join(lines[: baseline["line_count"]])).hexdigest(),
            baseline["raw_sha256"],
        )

    def test_current_entry_digest_binds_candidate_snapshot_and_evidence(self) -> None:
        for field in ("candidate", "evidence"):
            with self.subTest(field=field):
                entry = copy.deepcopy(current_review_entries()[0])
                if field == "candidate":
                    entry["candidate_snapshot"]["dimensions"]["exactness"] = 0
                else:
                    entry["reviewed_evidence_closure_sha256"] = "f" * 64
                with tempfile.TemporaryDirectory() as temporary:
                    path = Path(temporary) / "ledger.jsonl"
                    path.write_text(json.dumps(entry) + "\n", encoding="utf-8")
                    expected = (
                        "entry digest mismatch"
                        if field == "candidate"
                        else "candidate evidence closure mismatch"
                    )
                    with self.assertRaisesRegex(ValueError, expected):
                        load_review_ledger(path)

    def test_shadow_scoring_math_is_deterministic(self) -> None:
        names = self.spec["feature_contract"]["numeric"]
        model = {
            "trained": True,
            "feature_names": names,
            "bias": 0.0,
            "weights": {name: 0.1 for name in names},
            "normalization": {
                name: {"mean": 0.0, "scale": 1.0} for name in names
            },
        }
        features = {name: 1.0 for name in names}
        self.assertEqual(learned_score(features, model), learned_score(features, model))
        self.assertGreater(learned_score(features, model), 0.5)

    def test_generated_state_replays_exactly(self) -> None:
        self.assertEqual(build_state(), self.state)


if __name__ == "__main__":
    unittest.main()
