#!/usr/bin/env python3
"""Regression tests for Research Engine v0."""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from gen_status import render_engine_queue_summary
from research_engine_lib import (
    DECISION_PATH,
    INSTANCE_VALIDATION_FIELDS,
    OUTCOME_CLASSIFIER_PROTOCOL,
    POLICY_PATH,
    RUNS_DIR,
    VALIDATOR_PROTOCOL,
    VALIDATOR_OUTPUT_FIELDS,
    VALIDATOR_REQUEST_FIELDS,
    aggregate_instance_outcomes,
    apply_execution_feedback,
    brier_score,
    build_validator_request,
    build_state,
    execute_pure_validator,
    expected_information_gain,
    expanded_preregistration_matrix,
    file_sha256,
    load_json,
    load_outcomes,
    parse_hypotheses,
    predicted_marginal,
    select_candidates,
    sha256_json,
    validate_native_sequence,
    validate_outcome,
    validate_policy,
    validate_pure_validator_source,
    validate_historical_scope_guards,
    validate_historical_outcome_baseline,
    validate_retrospective,
)


class ResearchEngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy = load_json(POLICY_PATH)
        cls.decisions = load_json(DECISION_PATH)
        cls.hypotheses = parse_hypotheses()
        cls.outcomes = load_outcomes()

    def native_event(
        self,
        candidate_index: int,
        event_id: str,
        outcome: str = "supported",
        policy: dict | None = None,
    ) -> dict:
        policy = policy or self.executable_policy()
        candidate = policy["candidate_proposals"][candidate_index]
        return {
            "schema_version": 1,
            "event_id": event_id,
            "recorded_on": event_id[4:14],
            "candidate_id": candidate["id"],
            "hypothesis_id": candidate["hypothesis_id"],
            "route_id": candidate["route_id"],
            "outcome": outcome,
            "scope": {
                "target_kind": (
                    "validator_calibration"
                    if candidate["kind"] == "validator_prerequisite"
                    else "toy"
                ),
                "curve_family": candidate["scope"]["curve_family"],
                "field_bits": [17, 21],
                "threat_model": candidate["scope"]["threat_model"],
                "claim_boundary": "Synthetic regression fixture only.",
            },
            "summary": "Synthetic native event for a deterministic gate fixture.",
            "evidence_files": ["experiments/p3_sm_system/RESULTS.md"],
            "validation": {
                "status": "passed",
                "independent": True,
                "decisive_claim_validated": True,
                "evidence_files": ["experiments/p3_sm_system/validate.py"],
            },
            "budget": {
                "status": "within_budget",
                "wall_time_seconds": 10,
                "peak_memory_bytes": 1024,
                "parallel_workers": 1,
            },
            "stop_condition": {
                "triggered": True,
                "statement": "The preregistered fixture condition was reached.",
            },
            "residual_uncertainty": ["Synthetic event; no research claim follows."],
            "reopening_condition": "Create a new candidate id.",
            "provenance": {
                "source_kind": "native_engine_run",
                "source_commit": "1a1b5ddba7e9a6e3d40f189892e83529f5bc6616",
                "migration_note": "Regression fixture.",
                "run_manifest": (
                    "experiments/framework/fixtures/valid_exploration.json"
                ),
                "run_manifest_sha256": (
                    "0c3582f2e45693fc095f7f507c10f8311a9f9bf07d76ba66dd7b4406679fefd6"
                ),
            },
        }

    def executable_policy(self) -> dict:
        """Build a scientific-claim-free policy used only for protocol tests."""
        policy = copy.deepcopy(self.policy)
        fixture_relative = (
            "experiments/framework/fixtures/pure_engine_validator.py"
        )
        fixture_path = POLICY_PATH.parents[1] / fixture_relative
        fixture_contract = {
            "status": "implemented",
            "protocol": VALIDATOR_PROTOCOL,
            "entrypoint": fixture_relative,
            "entrypoint_sha256": file_sha256(fixture_path),
            "measurement_contract": {
                "name": "fixture-instance-outcome",
                "unit": "canonical-outcome",
                "value_type": "string",
                "supported_value": "supported",
            },
            "outcome_classifier": {
                "protocol": OUTCOME_CLASSIFIER_PROTOCOL,
                "allowed_instance_outcomes": [
                    "supported",
                    "falsified",
                    "bounded_negative",
                    "inapplicable",
                    "inconclusive",
                    "resource_exhausted",
                ],
                "precedence": [
                    "inapplicable",
                    "falsified",
                    "bounded_negative",
                    "resource_exhausted",
                    "inconclusive",
                    "supported",
                ],
            },
            "required_artifact_roles": [
                "external-solver-calibration-record"
            ],
        }
        for index, candidate in enumerate(policy["candidate_proposals"][:3]):
            candidate["authorization"] = "exploration"
            candidate["preregistration"]["status"] = "frozen"
            candidate["preregistration"]["validator_contract"] = copy.deepcopy(
                fixture_contract
            )
            candidate["hard_rejections"] = {
                key: False for key in candidate["hard_rejections"]
            }
            if index > 0:
                candidate["gap_class"] = "mechanism_bearing_open_window"
        return policy

    def test_policy_covers_all_nine_hypotheses(self) -> None:
        self.assertEqual(
            [],
            validate_policy(self.policy, self.decisions, self.hypotheses),
        )
        self.assertEqual(9, len(self.policy["hypothesis_normalization"]))

    def test_selector_selects_nothing_before_scientific_gates_clear(self) -> None:
        selection = select_candidates(self.policy)
        self.assertEqual([], selection["selected_sequence"])
        rejected = {
            item["candidate_id"]: set(item["reasons"])
            for item in selection["hard_rejected"]
        }
        self.assertEqual(
            {"missing_independent_validator"},
            rejected["RE0-001-EXTERNAL-SOLVER-CALIBRATION"],
        )
        self.assertEqual(
            {"missing_exact_mechanism", "missing_independent_validator"},
            rejected["RE0-002-NONREDUNDANT-INVARIANT-QUOTIENT"],
        )
        self.assertEqual(
            {"missing_exact_mechanism", "missing_independent_validator"},
            rejected["RE0-003-M3-INVARIANT-F4-SCALING"],
        )
        reordered = copy.deepcopy(self.policy)
        reordered["candidate_proposals"].reverse()
        self.assertEqual(
            [item["candidate_id"] for item in selection["selected_sequence"]],
            [
                item["candidate_id"]
                for item in select_candidates(reordered)["selected_sequence"]
            ],
        )

    def test_status_distinguishes_selected_from_ready_ids(self) -> None:
        policy = self.executable_policy()
        selection = apply_execution_feedback(
            policy,
            select_candidates(policy),
            [],
        )
        summary = render_engine_queue_summary(
            {
                "selected_explorations": 3,
                "ready_explorations": 1,
                "intake_candidates": 0,
            },
            selection["selected_sequence"],
            selection["execution_queue"]["ready_candidate_ids"],
        )
        self.assertIn("Selected bounded explorations: **3**", summary)
        self.assertIn(
            "Ready now: **1** (`RE0-001-EXTERNAL-SOLVER-CALIBRATION`)",
            summary,
        )
        ready_clause = summary.split("Ready now:", maxsplit=1)[1]
        self.assertNotIn("RE0-002-NONREDUNDANT-INVARIANT-QUOTIENT", ready_clause)

    def test_known_dead_ends_are_hard_rejected(self) -> None:
        selection = select_candidates(self.policy)
        rejected = {
            item["candidate_id"]: set(item["reasons"])
            for item in selection["hard_rejected"]
        }
        self.assertIn(
            "missing_exact_mechanism",
            rejected["RE0-X01-WARD-EDS-ZERO-SEARCH"],
        )
        self.assertIn(
            "targets_secp256k1_directly",
            rejected["RE0-X02-DIRECT-SECP256K1-PROBE"],
        )
        canary = rejected["RE0-X03-MULTI-TARGET-PRECOMPUTATION-CANARY"]
        self.assertIn("changes_threat_model", canary)
        self.assertIn("hidden_or_unpriced_precomputation", canary)
        scored_ids = {
            item["candidate_id"] for item in selection["selected_sequence"]
        }
        scored_ids.update(selection["eligible_not_selected"])
        self.assertNotIn(
            "RE0-X03-MULTI-TARGET-PRECOMPUTATION-CANARY",
            scored_ids,
        )

    def test_threat_model_rejection_is_derived_before_scoring(self) -> None:
        policy = copy.deepcopy(self.policy)
        canary = next(
            candidate
            for candidate in policy["candidate_proposals"]
            if candidate["id"]
            == "RE0-X03-MULTI-TARGET-PRECOMPUTATION-CANARY"
        )
        canary["hard_rejections"]["changes_threat_model"] = False
        canary["hard_rejections"]["hidden_or_unpriced_precomputation"] = False
        selection = select_candidates(policy)
        rejected = {
            item["candidate_id"]: item["reasons"]
            for item in selection["hard_rejected"]
        }
        self.assertIn("changes_threat_model", rejected[canary["id"]])
        problems = validate_policy(policy, self.decisions, self.hypotheses)
        self.assertTrue(
            any("non-primary threat model" in item for item in problems),
            msg=problems,
        )

    def test_every_historical_event_is_valid_and_retained(self) -> None:
        for path, event in self.outcomes:
            with self.subTest(path=path.name):
                self.assertEqual(
                    [],
                    validate_outcome(
                        path,
                        event,
                        self.policy,
                        self.decisions,
                        self.hypotheses,
                    ),
                )
        state = build_state(
            self.policy, self.decisions, self.hypotheses, self.outcomes
        )
        self.assertEqual(8, state["counts"]["outcome_events"])
        self.assertEqual(
            1, state["counts"]["outcomes_by_taxonomy"]["resource_exhausted"]
        )
        self.assertEqual(1, state["counts"]["outcomes_by_taxonomy"]["inapplicable"])
        self.assertEqual(1, state["counts"]["outcomes_by_taxonomy"]["supported"])
        self.assertEqual(
            len(self.decisions["routes"]),
            state["route_axis_contract"]["route_count"],
        )
        multi_target = next(
            item
            for item in state["route_evidence_state"]
            if item["route_id"] == "R-MULTI-TARGET-PRECOMPUTATION"
        )
        self.assertEqual(
            "separate",
            multi_target["threat_model_axis"]["scope"],
        )
        self.assertEqual(
            "conditional_only",
            multi_target["decision_axis"]["substrate_disposition"],
        )
        self.assertEqual(
            "no_engine_evidence",
            multi_target["evidence_axis"]["engine_disposition"],
        )
        ward = next(
            item
            for item in state["route_evidence_state"]
            if item["route_id"] == "R-EDS-DIVISION-POLYNOMIAL"
        )
        self.assertEqual(
            "supported_structural_evidence_retained",
            ward["evidence_axis"]["engine_disposition"],
        )

    def test_outcome_budget_rejects_zero_parallel_workers(self) -> None:
        path, source_event = self.outcomes[0]
        event = copy.deepcopy(source_event)
        event["budget"]["parallel_workers"] = 0
        problems = validate_outcome(
            path,
            event,
            self.policy,
            self.decisions,
            self.hypotheses,
        )
        self.assertTrue(
            any("budget.parallel_workers has an invalid value" in item for item in problems),
            msg=problems,
        )

    def test_retrospective_gate_has_no_false_promotion(self) -> None:
        state = build_state(
            self.policy, self.decisions, self.hypotheses, self.outcomes
        )
        retrospective = state["retrospective_validation"]
        self.assertTrue(retrospective["passed"])
        self.assertTrue(all(case["passed"] for case in retrospective["cases"]))
        self.assertIn(
            "excluded from predictive calibration",
            retrospective["method"]["limitation"],
        )
        self.assertEqual(8, state["calibration"]["historical_outcomes_excluded"])
        self.assertEqual(0, state["calibration"]["scored_native_outcomes"])
        self.assertIsNone(state["calibration"]["mean_brier_score"])

    def test_retrospective_outcome_is_bound_to_an_event(self) -> None:
        policy = copy.deepcopy(self.policy)
        policy["retrospective_cases"][0]["known_outcome"] = "proved"
        result = validate_retrospective(
            policy,
            [event for _, event in self.outcomes],
        )
        self.assertFalse(result["passed"])
        self.assertFalse(result["cases"][0]["evidence_matches"])

    def test_historical_scope_cannot_absorb_the_legacy_24_bit_run(self) -> None:
        policy = copy.deepcopy(self.policy)
        outcomes = [copy.deepcopy(event) for _, event in self.outcomes]
        event = next(
            item for item in outcomes if item["event_id"] == "REO-2026-07-24-001"
        )
        event["scope"]["field_bits"].append(24)
        guard = next(
            item
            for item in policy["historical_scope_guards"]
            if item["event_id"] == event["event_id"]
        )
        guard["event_sha256"] = sha256_json(event)
        problems = validate_historical_scope_guards(policy, outcomes)
        self.assertTrue(
            any("field-bit scope changed" in item for item in problems),
            msg=problems,
        )
        self.assertTrue(
            any("forbidden field-bit scope reappeared" in item for item in problems),
            msg=problems,
        )

    def test_historical_baseline_cannot_drop_or_rewrite_an_event(self) -> None:
        outcomes = [copy.deepcopy(event) for _, event in self.outcomes]
        self.assertEqual(
            [],
            validate_historical_outcome_baseline(self.policy, outcomes),
        )
        outcomes = [
            event
            for event in outcomes
            if event["event_id"] != "REO-2026-07-24-002"
        ]
        problems = validate_historical_outcome_baseline(self.policy, outcomes)
        self.assertTrue(
            any("missing=['REO-2026-07-24-002']" in item for item in problems),
            msg=problems,
        )

    def test_frozen_retrospective_and_scope_guard_sets_cannot_be_vacuous(self) -> None:
        policy = copy.deepcopy(self.policy)
        policy["retrospective_cases"] = []
        policy["historical_scope_guards"] = policy[
            "historical_scope_guards"
        ][:1]
        problems = validate_policy(policy, self.decisions, self.hypotheses)
        self.assertTrue(
            any("four frozen v0 cases" in item for item in problems),
            msg=problems,
        )
        self.assertTrue(
            any("cofactor-1/cofactor-3 split" in item for item in problems),
            msg=problems,
        )

        rebound = copy.deepcopy(self.policy)
        rebound["retrospective_cases"][0][
            "outcome_event_id"
        ] = "REO-2026-07-24-004"
        result = validate_retrospective(
            rebound,
            [event for _, event in self.outcomes],
        )
        self.assertFalse(result["passed"])
        self.assertFalse(result["cases"][0]["evidence_matches"])

    def test_information_gain_is_computed_and_calibratable(self) -> None:
        independent = {
            "proved": {"live": 0.5, "dead": 0.5},
            "falsified": {"live": 0.5, "dead": 0.5},
        }
        self.assertAlmostEqual(
            0.0,
            expected_information_gain(0.1, independent),
            places=12,
        )
        model = self.policy["candidate_proposals"][0]["information_model"]
        eig = expected_information_gain(
            model["prior_live"], model["likelihoods"]
        )
        self.assertGreater(eig, 0.0)
        marginal = predicted_marginal(
            model["prior_live"], model["likelihoods"]
        )
        self.assertAlmostEqual(1.0, sum(marginal.values()), places=12)
        self.assertGreaterEqual(brier_score(marginal, "supported"), 0.0)

    def test_likelihoods_must_be_precommitted_distributions(self) -> None:
        policy = copy.deepcopy(self.policy)
        candidate = policy["candidate_proposals"][0]
        candidate["information_model"]["likelihoods"]["supported"]["live"] += 0.1
        problems = validate_policy(policy, self.decisions, self.hypotheses)
        self.assertTrue(
            any("P(outcome|live) sums to" in item for item in problems),
            msg=problems,
        )

    def test_hard_rejected_canary_is_not_scored(self) -> None:
        with patch(
            "research_engine_lib.expected_information_gain",
            wraps=expected_information_gain,
        ) as tracked:
            problems = validate_policy(
                self.policy,
                self.decisions,
                self.hypotheses,
            )
        self.assertEqual([], problems)
        self.assertEqual(0, tracked.call_count)

    def test_pure_validator_has_no_io_or_dynamic_capabilities(self) -> None:
        root = Path(__file__).resolve().parents[1]
        policy = self.executable_policy()
        validator_contract = policy["candidate_proposals"][0][
            "preregistration"
        ]["validator_contract"]
        payload = (root / validator_contract["entrypoint"]).read_bytes()
        self.assertEqual([], validate_pure_validator_source(payload))

        request = {
            "schema_version": 1,
            "run_id": "RER-2026-07-25-001",
            "candidate_id": "RE0-001-EXTERNAL-SOLVER-CALIBRATION",
            "source_commit": "1" * 40,
            "instance": {"seed": 1},
            "measurement_contract": {
                "name": "fixture-instance-outcome",
                "unit": "canonical-outcome",
                "value_type": "string",
            },
            "artifacts": [],
        }
        artifact = {
            "instance": {"seed": 1},
            "left_observation": 4,
            "right_observation": 4,
        }
        value, replay_problems = execute_pure_validator(
            payload,
            request,
            {"external-solver-calibration-record": [artifact]},
        )
        self.assertEqual([], replay_problems)
        self.assertEqual("supported", value)

        forbidden_sources = [
            b"import os\ndef validate(request, artifacts):\n    return True\n",
            b"def validate(request, artifacts):\n    return True\n",
            (
                b"def validate(request, artifacts):\n"
                b"    return open('postselected.json').read()\n"
            ),
            (
                b"def validate(request, artifacts):\n"
                b"    return request.__class__\n"
            ),
            (
                b"def validate(request, artifacts):\n"
                b"    while True:\n"
                b"        pass\n"
            ),
        ]
        for source in forbidden_sources:
            self.assertTrue(
                validate_pure_validator_source(source),
                msg=source.decode("utf-8"),
            )

    def test_validator_request_uses_only_frozen_metric_and_roles(self) -> None:
        policy = self.executable_policy()
        validator_contract = policy["candidate_proposals"][0][
            "preregistration"
        ]["validator_contract"]
        result_record = {
            "schema_version": 1,
            "result_id": "fixture",
            "run_id": "RER-2026-07-25-001",
            "candidate_id": "RE0-001-EXTERNAL-SOLVER-CALIBRATION",
            "source_commit": "1" * 40,
            "instance": {"seed": 1},
            "status": "completed",
            "decisive_measurement": {
                "name": "postselected-metric",
                "value": "producer-claim",
                "unit": "postselected-unit",
            },
            "artifacts": [
                {
                    "path": "ignored.json",
                    "sha256": "a" * 64,
                    "role": "producer-only-debug",
                },
                {
                    "path": "frozen.json",
                    "sha256": "b" * 64,
                    "role": "external-solver-calibration-record",
                },
            ],
        }
        request = build_validator_request(result_record, validator_contract)
        self.assertEqual(
            {
                "name": "fixture-instance-outcome",
                "unit": "canonical-outcome",
                "value_type": "string",
            },
            request["measurement_contract"],
        )
        self.assertEqual(
            ["external-solver-calibration-record"],
            [artifact["role"] for artifact in request["artifacts"]],
        )
        self.assertNotIn("value", request["measurement_contract"])
        self.assertNotIn("result_sha256", request)

    def test_outcome_classifier_is_exhaustive_and_deterministic(self) -> None:
        policy = self.executable_policy()
        classifier = policy["candidate_proposals"][0]["preregistration"][
            "validator_contract"
        ]["outcome_classifier"]
        self.assertEqual(
            "supported",
            aggregate_instance_outcomes(
                ["supported", "supported"],
                classifier,
            ),
        )
        self.assertEqual(
            "falsified",
            aggregate_instance_outcomes(
                ["supported", "falsified", "bounded_negative"],
                classifier,
            ),
        )
        self.assertEqual(
            "inapplicable",
            aggregate_instance_outcomes(
                ["falsified", "inapplicable"],
                classifier,
            ),
        )

        incomplete = copy.deepcopy(policy)
        incomplete_classifier = incomplete["candidate_proposals"][0][
            "preregistration"
        ]["validator_contract"]["outcome_classifier"]
        incomplete_classifier["allowed_instance_outcomes"].remove(
            "bounded_negative"
        )
        incomplete_classifier["precedence"].remove("bounded_negative")
        problems = validate_policy(
            incomplete,
            self.decisions,
            self.hypotheses,
        )
        self.assertTrue(
            any("six empirical outcomes" in item for item in problems),
            msg=problems,
        )

    def test_feedback_unlocks_only_declared_dependency_outcomes(self) -> None:
        policy = self.executable_policy()
        base = select_candidates(policy)
        calibration = self.native_event(
            0, "REO-2026-07-25-001", "supported", policy
        )
        after_calibration = apply_execution_feedback(
            policy, base, [calibration]
        )
        states = {
            item["candidate_id"]: item["execution_state"]
            for item in after_calibration["selected_sequence"]
        }
        self.assertEqual("terminal", states[calibration["candidate_id"]])
        self.assertEqual(
            "ready",
            states["RE0-002-NONREDUNDANT-INVARIANT-QUOTIENT"],
        )
        self.assertEqual(
            "awaiting_dependency_outcome",
            states["RE0-003-M3-INVARIANT-F4-SCALING"],
        )

        quotient = self.native_event(
            1, "REO-2026-07-25-002", "bounded_negative", policy
        )
        after_negative = apply_execution_feedback(
            policy, base, [calibration, quotient]
        )
        scaling = next(
            item
            for item in after_negative["selected_sequence"]
            if item["candidate_id"] == "RE0-003-M3-INVARIANT-F4-SCALING"
        )
        self.assertEqual(
            "blocked_by_dependency_outcome", scaling["execution_state"]
        )

    def test_native_event_cannot_bypass_scope_or_budget(self) -> None:
        policy = self.executable_policy()
        event = self.native_event(0, "REO-2026-07-25-001", policy=policy)
        self.assertEqual(
            [],
            validate_outcome(
                Path(f"{event['event_id']}.json"),
                event,
                policy,
                self.decisions,
                self.hypotheses,
            ),
        )
        event["route_id"] = "R-GENERIC-BASELINE"
        event["budget"]["wall_time_seconds"] = 999999
        problems = validate_outcome(
            Path(f"{event['event_id']}.json"),
            event,
            policy,
            self.decisions,
            self.hypotheses,
        )
        self.assertTrue(any("route differs from candidate" in item for item in problems))
        self.assertTrue(any("exceeds wall_time_seconds budget" in item for item in problems))

    def test_positive_toy_result_cannot_be_labelled_proved(self) -> None:
        policy = self.executable_policy()
        event = self.native_event(
            0,
            "REO-2026-07-25-001",
            "proved",
            policy,
        )
        problems = validate_outcome(
            Path(f"{event['event_id']}.json"),
            event,
            policy,
            self.decisions,
            self.hypotheses,
        )
        self.assertTrue(
            any("positive empirical evidence must use supported" in item for item in problems),
            msg=problems,
        )

    def test_native_dependency_event_must_precede_and_unlock(self) -> None:
        policy = self.executable_policy()
        calibration = self.native_event(
            0, "REO-2026-07-25-002", "falsified", policy
        )
        quotient = self.native_event(
            1, "REO-2026-07-25-001", "supported", policy
        )
        problems = validate_native_sequence(
            policy,
            self.decisions,
            [
                (Path("REO-2026-07-25-002.json"), calibration),
                (Path("REO-2026-07-25-001.json"), quotient),
            ],
        )
        self.assertTrue(any("does not unlock execution" in item for item in problems))

    def test_ready_native_event_is_bound_to_validated_run_manifest(self) -> None:
        policy = self.executable_policy()
        calibration = self.native_event(
            0, "REO-2026-07-25-001", "supported", policy
        )
        candidate_record_path = RUNS_DIR / "RER-2026-07-25-001.candidate.json"
        envelope_path = RUNS_DIR / "RER-2026-07-25-001.json"
        source_candidate_path = (
            Path(__file__).resolve().parents[1]
            / "experiments"
            / "framework"
            / "fixtures"
            / "valid_exploration.json"
        )
        result_path = (
            Path(__file__).resolve().parents[1]
            / "experiments"
            / "p3_sm_system"
            / "RESULTS.md"
        )
        validation_path = (
            Path(__file__).resolve().parents[1]
            / "experiments"
            / "p3_sm_system"
            / "validate.py"
        )
        validator_contract = policy["candidate_proposals"][0][
            "preregistration"
        ]["validator_contract"]
        measurement_contract = validator_contract["measurement_contract"]
        validator_relative = validator_contract["entrypoint"]
        validator_script_path = (
            Path(__file__).resolve().parents[1] / validator_relative
        )
        producer_relative = "experiments/framework/test_framework.py"
        producer_path = Path(__file__).resolve().parents[1] / producer_relative
        RUNS_DIR.mkdir(parents=True, exist_ok=True)
        source_validator_bytes = validator_script_path.read_bytes()
        source_producer_bytes = producer_path.read_bytes()

        def source_file_bytes(_commit: str, relative: str) -> bytes | None:
            if relative == validator_relative:
                return source_validator_bytes
            if relative == producer_relative:
                return source_producer_bytes
            return None

        source_file_patcher = patch(
            "research_engine_lib.git_file_bytes",
            side_effect=source_file_bytes,
        )
        source_file_patcher.start()
        generated_paths = [
            candidate_record_path,
            envelope_path,
        ]
        try:
            candidate_record_path.write_bytes(source_candidate_path.read_bytes())
            calibration["validation"]["evidence_files"].append(
                validator_relative
            )
            executed_instances = []
            for index, instance in enumerate(
                expanded_preregistration_matrix(
                    policy["candidate_proposals"][0]
                )
            ):
                result_relative = (
                    f"experiments/engine/runs/"
                    f"RER-2026-07-25-001.instance-{index:02d}.result.json"
                )
                validation_relative = (
                    f"experiments/engine/runs/"
                    f"RER-2026-07-25-001.instance-{index:02d}.validation.json"
                )
                validator_request_relative = (
                    f"experiments/engine/runs/"
                    f"RER-2026-07-25-001.instance-{index:02d}."
                    "validator-request.json"
                )
                validator_output_relative = (
                    f"experiments/engine/runs/"
                    f"RER-2026-07-25-001.instance-{index:02d}."
                    "validator-output.json"
                )
                result_record_path = (
                    Path(__file__).resolve().parents[1] / result_relative
                )
                validation_record_path = (
                    Path(__file__).resolve().parents[1] / validation_relative
                )
                validator_request_path = (
                    Path(__file__).resolve().parents[1]
                    / validator_request_relative
                )
                validator_output_path = (
                    Path(__file__).resolve().parents[1]
                    / validator_output_relative
                )
                calibration_artifact_relative = (
                    f"experiments/engine/runs/"
                    f"RER-2026-07-25-001.instance-{index:02d}."
                    "calibration.json"
                )
                calibration_artifact_path = (
                    Path(__file__).resolve().parents[1]
                    / calibration_artifact_relative
                )
                calibration_artifact = {
                    "instance": instance,
                    "left_observation": 4,
                    "right_observation": 4,
                }
                calibration_artifact_path.write_text(
                    json.dumps(calibration_artifact, indent=2) + "\n",
                    encoding="utf-8",
                )
                measurement = {
                    "name": measurement_contract["name"],
                    "value": measurement_contract["supported_value"],
                    "unit": measurement_contract["unit"],
                }
                result_record = {
                    "schema_version": 1,
                    "result_id": f"RER-2026-07-25-001-result-{index:02d}",
                    "run_id": "RER-2026-07-25-001",
                    "candidate_id": calibration["candidate_id"],
                    "source_commit": calibration["provenance"]["source_commit"],
                    "instance": instance,
                    "status": "completed",
                    "decisive_measurement": measurement,
                    "artifacts": [
                        {
                            "path": calibration_artifact_relative,
                            "sha256": file_sha256(calibration_artifact_path),
                            "role": "external-solver-calibration-record",
                        }
                    ],
                }
                result_record_path.write_text(
                    json.dumps(result_record, indent=2) + "\n",
                    encoding="utf-8",
                )
                validator_request = build_validator_request(
                    result_record,
                    validator_contract,
                )
                self.assertNotIn(
                    "value",
                    validator_request["measurement_contract"],
                )
                self.assertNotIn("result_sha256", validator_request)
                validator_request_path.write_text(
                    json.dumps(validator_request, indent=2) + "\n",
                    encoding="utf-8",
                )
                validator_output = {
                    "schema_version": 1,
                    "validator_request_sha256": file_sha256(
                        validator_request_path
                    ),
                    "passed": True,
                    "recomputed_measurement": measurement,
                }
                validator_output_path.write_text(
                    json.dumps(validator_output, indent=2) + "\n",
                    encoding="utf-8",
                )
                validation_record = {
                    "schema_version": 1,
                    "validation_id": (
                        f"RER-2026-07-25-001-validation-{index:02d}"
                    ),
                    "run_id": "RER-2026-07-25-001",
                    "candidate_id": calibration["candidate_id"],
                    "source_commit": calibration["provenance"]["source_commit"],
                    "result_record": result_relative,
                    "result_sha256": file_sha256(result_record_path),
                    "validator_entrypoint": validator_relative,
                    "validator_entrypoint_sha256": file_sha256(
                        validator_script_path
                    ),
                    "validator_protocol": VALIDATOR_PROTOCOL,
                    "validator_request": validator_request_relative,
                    "validator_request_sha256": file_sha256(
                        validator_request_path
                    ),
                    "validator_output": validator_output_relative,
                    "validator_output_sha256": file_sha256(
                        validator_output_path
                    ),
                    "independent": True,
                    "shares_decisive_logic": False,
                    "passed": True,
                    "recomputed_measurement": measurement,
                    "artifacts": [
                        {
                            "path": validator_relative,
                            "sha256": file_sha256(validator_script_path),
                            "role": "contract-regression-validation",
                        },
                        {
                            "path": validator_request_relative,
                            "sha256": file_sha256(validator_request_path),
                            "role": "contract-regression-validator-request",
                        },
                        {
                            "path": validator_output_relative,
                            "sha256": file_sha256(validator_output_path),
                            "role": "contract-regression-validator-output",
                        }
                    ],
                }
                validation_record_path.write_text(
                    json.dumps(validation_record, indent=2) + "\n",
                    encoding="utf-8",
                )
                executed_instances.append(
                    {
                        **instance,
                        "result_record": result_relative,
                        "result_sha256": file_sha256(result_record_path),
                        "validation_record": validation_relative,
                        "validation_sha256": file_sha256(
                            validation_record_path
                        ),
                    }
                )
                generated_paths.extend(
                    [
                        result_record_path,
                        validation_record_path,
                        validator_request_path,
                        validator_output_path,
                        calibration_artifact_path,
                    ]
                )
                calibration["evidence_files"].append(result_relative)
                calibration["validation"]["evidence_files"].append(
                    validation_relative
                )
                calibration["validation"]["evidence_files"].append(
                    validator_request_relative
                )
                calibration["validation"]["evidence_files"].append(
                    validator_output_relative
                )
            envelope = {
                "schema_version": 1,
                "run_id": "RER-2026-07-25-001",
                "candidate_id": calibration["candidate_id"],
                "source_commit": calibration["provenance"]["source_commit"],
                "candidate_policy_sha256": sha256_json(
                    policy["candidate_proposals"][0]
                ),
                "preregistration_sha256": sha256_json(
                    policy["candidate_proposals"][0]["preregistration"]
                ),
                "candidate_run_manifest": (
                    "experiments/engine/runs/"
                    "RER-2026-07-25-001.candidate.json"
                ),
                "candidate_run_manifest_sha256": file_sha256(
                    candidate_record_path
                ),
                "executed_instances": executed_instances,
                "completion": {
                    "status": "complete",
                    "reason": "Synthetic full-matrix contract regression.",
                },
                "result_artifacts": [
                    {
                        "path": "experiments/p3_sm_system/RESULTS.md",
                        "sha256": file_sha256(result_path),
                        "role": "contract-regression-result",
                    }
                ],
                "validation_artifacts": [
                    {
                        "path": validator_relative,
                        "sha256": file_sha256(validator_script_path),
                        "role": "contract-regression-validator",
                        "validator_id": "p3-independent-ec-replay",
                        "independent": True,
                        "decisive_claim": True,
                    }
                ],
            }
            envelope_path.write_text(
                json.dumps(envelope, indent=2) + "\n",
                encoding="utf-8",
            )
            calibration["provenance"]["run_manifest"] = (
                "experiments/engine/runs/RER-2026-07-25-001.json"
            )
            calibration["provenance"]["run_manifest_sha256"] = file_sha256(
                envelope_path
            )
            self.assertEqual(
                [],
                validate_outcome(
                    Path("REO-2026-07-25-001.json"),
                    calibration,
                    policy,
                    self.decisions,
                    self.hypotheses,
                ),
            )
            without_commit_anchor = validate_native_sequence(
                policy,
                self.decisions,
                [(Path("REO-2026-07-25-001.json"), calibration)],
            )
            self.assertTrue(
                any(
                    "source_commit does not contain RESEARCH_ENGINE_V0.json"
                    in item
                    for item in without_commit_anchor
                ),
                msg=without_commit_anchor,
            )
            with patch("research_engine_lib.git_json", return_value=policy):
                self.assertEqual(
                    [],
                    validate_native_sequence(
                        policy,
                        self.decisions,
                        [(Path("REO-2026-07-25-001.json"), calibration)],
                    ),
                )
                relabelled = copy.deepcopy(calibration)
                relabelled["outcome"] = "bounded_negative"
                relabelled_problems = validate_native_sequence(
                    policy,
                    self.decisions,
                    [(Path("REO-2026-07-25-001.json"), relabelled)],
                )
            self.assertTrue(
                any(
                    "differs from the preregistered aggregate classifier result "
                    "'supported'" in item
                    for item in relabelled_problems
                ),
                msg=relabelled_problems,
            )
            original_candidate_record = json.loads(
                candidate_record_path.read_text(encoding="utf-8")
            )
            altered_tool_versions = copy.deepcopy(original_candidate_record)
            altered_tool_versions["environment"]["tool_versions"][
                "SageMath"
            ] = "postselected"
            candidate_record_path.write_text(
                json.dumps(altered_tool_versions, indent=2) + "\n",
                encoding="utf-8",
            )
            envelope["candidate_run_manifest_sha256"] = file_sha256(
                candidate_record_path
            )
            envelope_path.write_text(
                json.dumps(envelope, indent=2) + "\n",
                encoding="utf-8",
            )
            calibration["provenance"]["run_manifest_sha256"] = file_sha256(
                envelope_path
            )
            with patch("research_engine_lib.git_json", return_value=policy):
                tool_version_problems = validate_native_sequence(
                    policy,
                    self.decisions,
                    [(Path("REO-2026-07-25-001.json"), calibration)],
                )
            self.assertTrue(
                any(
                    "tool versions differ from preregistration" in item
                    for item in tool_version_problems
                ),
                msg=tool_version_problems,
            )
            candidate_record_path.write_text(
                json.dumps(original_candidate_record, indent=2) + "\n",
                encoding="utf-8",
            )
            envelope["candidate_run_manifest_sha256"] = file_sha256(
                candidate_record_path
            )
            envelope_path.write_text(
                json.dumps(envelope, indent=2) + "\n",
                encoding="utf-8",
            )
            calibration["provenance"]["run_manifest_sha256"] = file_sha256(
                envelope_path
            )
            altered_source_policy = copy.deepcopy(policy)
            altered_source_policy["candidate_proposals"][0][
                "title"
            ] = "Post-commit candidate mutation"
            with patch(
                "research_engine_lib.git_json",
                return_value=altered_source_policy,
            ):
                problems = validate_native_sequence(
                    policy,
                    self.decisions,
                    [(Path("REO-2026-07-25-001.json"), calibration)],
                )
            self.assertTrue(
                any(
                    "source_commit candidate policy differs from run envelope"
                    in item
                    for item in problems
                ),
                msg=problems,
            )
            first_validation_relative = envelope["executed_instances"][0][
                "validation_record"
            ]
            first_validation_path = (
                Path(__file__).resolve().parents[1] / first_validation_relative
            )
            original_validation = json.loads(
                first_validation_path.read_text(encoding="utf-8")
            )
            mutated_validation = copy.deepcopy(original_validation)
            mutated_validation["recomputed_measurement"]["value"] = "falsified"
            first_validation_path.write_text(
                json.dumps(mutated_validation, indent=2) + "\n",
                encoding="utf-8",
            )
            envelope["executed_instances"][0]["validation_sha256"] = file_sha256(
                first_validation_path
            )
            envelope_path.write_text(
                json.dumps(envelope, indent=2) + "\n",
                encoding="utf-8",
            )
            calibration["provenance"]["run_manifest_sha256"] = file_sha256(
                envelope_path
            )
            with patch("research_engine_lib.git_json", return_value=policy):
                problems = validate_native_sequence(
                    policy,
                    self.decisions,
                    [(Path("REO-2026-07-25-001.json"), calibration)],
                )
            self.assertTrue(
                any(
                    "validator measurement differs from result" in item
                    for item in problems
                ),
                msg=problems,
            )
            first_validation_path.write_text(
                json.dumps(original_validation, indent=2) + "\n",
                encoding="utf-8",
            )
            envelope["executed_instances"][0]["validation_sha256"] = file_sha256(
                first_validation_path
            )
            first_result_relative = envelope["executed_instances"][0][
                "result_record"
            ]
            first_result_path = (
                Path(__file__).resolve().parents[1] / first_result_relative
            )
            first_validator_request_relative = original_validation[
                "validator_request"
            ]
            first_validator_request_path = (
                Path(__file__).resolve().parents[1]
                / first_validator_request_relative
            )
            first_validator_output_relative = original_validation[
                "validator_output"
            ]
            first_validator_output_path = (
                Path(__file__).resolve().parents[1]
                / first_validator_output_relative
            )
            original_result = json.loads(
                first_result_path.read_text(encoding="utf-8")
            )
            original_validator_request = json.loads(
                first_validator_request_path.read_text(encoding="utf-8")
            )
            original_validator_output = json.loads(
                first_validator_output_path.read_text(encoding="utf-8")
            )
            coordinated_result = copy.deepcopy(original_result)
            coordinated_result["decisive_measurement"]["value"] = "falsified"
            first_result_path.write_text(
                json.dumps(coordinated_result, indent=2) + "\n",
                encoding="utf-8",
            )
            coordinated_result_sha256 = file_sha256(first_result_path)
            coordinated_validator_request = build_validator_request(
                coordinated_result,
                validator_contract,
            )
            first_validator_request_path.write_text(
                json.dumps(coordinated_validator_request, indent=2) + "\n",
                encoding="utf-8",
            )
            coordinated_validator_output = copy.deepcopy(
                original_validator_output
            )
            coordinated_validator_output[
                "validator_request_sha256"
            ] = file_sha256(first_validator_request_path)
            coordinated_validator_output[
                "recomputed_measurement"
            ] = coordinated_result["decisive_measurement"]
            first_validator_output_path.write_text(
                json.dumps(coordinated_validator_output, indent=2) + "\n",
                encoding="utf-8",
            )
            coordinated_validation = copy.deepcopy(original_validation)
            coordinated_validation[
                "result_sha256"
            ] = coordinated_result_sha256
            coordinated_validation[
                "validator_request_sha256"
            ] = file_sha256(first_validator_request_path)
            coordinated_validation[
                "validator_output_sha256"
            ] = file_sha256(first_validator_output_path)
            coordinated_validation[
                "recomputed_measurement"
            ] = coordinated_result["decisive_measurement"]
            for artifact in coordinated_validation["artifacts"]:
                if artifact["path"] == first_validator_request_relative:
                    artifact["sha256"] = file_sha256(
                        first_validator_request_path
                    )
                elif artifact["path"] == first_validator_output_relative:
                    artifact["sha256"] = file_sha256(
                        first_validator_output_path
                    )
            first_validation_path.write_text(
                json.dumps(coordinated_validation, indent=2) + "\n",
                encoding="utf-8",
            )
            envelope["executed_instances"][0][
                "result_sha256"
            ] = coordinated_result_sha256
            envelope["executed_instances"][0][
                "validation_sha256"
            ] = file_sha256(first_validation_path)
            envelope_path.write_text(
                json.dumps(envelope, indent=2) + "\n",
                encoding="utf-8",
            )
            calibration["provenance"]["run_manifest_sha256"] = file_sha256(
                envelope_path
            )
            with patch("research_engine_lib.git_json", return_value=policy):
                problems = validate_native_sequence(
                    policy,
                    self.decisions,
                    [(Path("REO-2026-07-25-001.json"), calibration)],
                )
            self.assertTrue(
                any(
                    "stored validator output differs from replay" in item
                    for item in problems
                ),
                msg=problems,
            )
            first_result_path.write_text(
                json.dumps(original_result, indent=2) + "\n",
                encoding="utf-8",
            )
            first_validator_request_path.write_text(
                json.dumps(original_validator_request, indent=2) + "\n",
                encoding="utf-8",
            )
            first_validator_output_path.write_text(
                json.dumps(original_validator_output, indent=2) + "\n",
                encoding="utf-8",
            )
            first_validation_path.write_text(
                json.dumps(original_validation, indent=2) + "\n",
                encoding="utf-8",
            )
            envelope["executed_instances"][0]["result_sha256"] = file_sha256(
                first_result_path
            )
            envelope["executed_instances"][0][
                "validation_sha256"
            ] = file_sha256(first_validation_path)
            mutated_validator_digest = copy.deepcopy(original_validation)
            mutated_validator_digest["validator_entrypoint_sha256"] = "0" * 64
            first_validation_path.write_text(
                json.dumps(mutated_validator_digest, indent=2) + "\n",
                encoding="utf-8",
            )
            envelope["executed_instances"][0]["validation_sha256"] = file_sha256(
                first_validation_path
            )
            envelope_path.write_text(
                json.dumps(envelope, indent=2) + "\n",
                encoding="utf-8",
            )
            calibration["provenance"]["run_manifest_sha256"] = file_sha256(
                envelope_path
            )
            with patch("research_engine_lib.git_json", return_value=policy):
                problems = validate_native_sequence(
                    policy,
                    self.decisions,
                    [(Path("REO-2026-07-25-001.json"), calibration)],
                )
            self.assertTrue(
                any(
                    "validator_entrypoint_sha256 differs from source_commit"
                    in item
                    for item in problems
                ),
                msg=problems,
            )
            first_validation_path.write_text(
                json.dumps(original_validation, indent=2) + "\n",
                encoding="utf-8",
            )
            envelope["executed_instances"][0]["validation_sha256"] = file_sha256(
                first_validation_path
            )
            envelope["executed_instances"] = envelope["executed_instances"][:-1]
            envelope_path.write_text(
                json.dumps(envelope, indent=2) + "\n",
                encoding="utf-8",
            )
            calibration["provenance"]["run_manifest_sha256"] = file_sha256(
                envelope_path
            )
            with patch("research_engine_lib.git_json", return_value=policy):
                problems = validate_native_sequence(
                    policy,
                    self.decisions,
                    [(Path("REO-2026-07-25-001.json"), calibration)],
                )
            self.assertTrue(
                any(
                    "complete run must execute the full frozen matrix" in item
                    for item in problems
                ),
                msg=problems,
            )
        finally:
            source_file_patcher.stop()
            for path in generated_paths:
                path.unlink(missing_ok=True)

    def test_validator_schemas_match_semantic_contract(self) -> None:
        root = Path(__file__).resolve().parents[1]
        instance_validation_schema = load_json(
            root / "experiments" / "engine" / "instance_validation.schema.json"
        )
        validator_request_schema = load_json(
            root / "experiments" / "engine" / "validator_request.schema.json"
        )
        validator_output_schema = load_json(
            root / "experiments" / "engine" / "validator_output.schema.json"
        )
        outcome_schema = load_json(
            root / "experiments" / "engine" / "outcome.schema.json"
        )
        self.assertEqual(
            INSTANCE_VALIDATION_FIELDS,
            set(instance_validation_schema["required"]),
        )
        self.assertEqual(
            VALIDATOR_REQUEST_FIELDS,
            set(validator_request_schema["required"]),
        )
        self.assertEqual(
            VALIDATOR_OUTPUT_FIELDS,
            set(validator_output_schema["required"]),
        )
        self.assertEqual(
            VALIDATOR_PROTOCOL,
            instance_validation_schema["properties"]["validator_protocol"][
                "const"
            ],
        )
        request_measurement = validator_request_schema["properties"][
            "measurement_contract"
        ]
        self.assertEqual(
            {"name", "unit", "value_type"},
            set(request_measurement["required"]),
        )
        self.assertEqual(
            "string",
            request_measurement["properties"]["value_type"]["const"],
        )
        empirical_outcomes = {
            "supported",
            "falsified",
            "bounded_negative",
            "inapplicable",
            "inconclusive",
            "resource_exhausted",
        }
        self.assertEqual(
            empirical_outcomes,
            set(
                validator_output_schema["$defs"]["measurement"]["properties"][
                    "value"
                ]["enum"]
            ),
        )
        self.assertEqual(
            1,
            outcome_schema["properties"]["budget"]["properties"][
                "parallel_workers"
            ]["oneOf"][1]["minimum"],
        )
        self.assertFalse(instance_validation_schema["additionalProperties"])
        self.assertFalse(validator_request_schema["additionalProperties"])
        self.assertFalse(validator_output_schema["additionalProperties"])

    def test_native_outcome_updates_queue_hypothesis_and_route_state(self) -> None:
        policy = self.executable_policy()
        calibration = self.native_event(
            0, "REO-2026-07-25-001", "supported", policy
        )
        outcomes = self.outcomes + [
            (Path("REO-2026-07-25-001.json"), calibration)
        ]
        state = build_state(
            policy, self.decisions, self.hypotheses, outcomes
        )
        self.assertEqual(
            ["RE0-002-NONREDUNDANT-INVARIANT-QUOTIENT"],
            state["execution_queue"]["ready_candidate_ids"],
        )
        self.assertEqual(
            [],
            state["execution_queue"]["awaiting_validator_candidate_ids"],
        )
        hypothesis = next(
            item
            for item in state["normalized_hypotheses"]
            if item["id"] == "HYP_GLV_SEMAEV_001"
        )
        self.assertIn("REO-2026-07-25-001", hypothesis["outcome_event_ids"])
        route = next(
            item
            for item in state["route_evidence_state"]
            if item["route_id"] == "R-GLV-SEMAEV"
        )
        self.assertEqual(
            "open_with_scoped_uncertainty",
            route["evidence_axis"]["engine_disposition"],
        )
        self.assertEqual([], route["route_review_trigger_event_ids"])
        self.assertEqual(1, len(state["native_outcomes"]))

    def test_mechanism_result_opens_review_but_not_promotion(self) -> None:
        policy = self.executable_policy()
        calibration = self.native_event(
            0, "REO-2026-07-25-001", "supported", policy
        )
        quotient = self.native_event(
            1, "REO-2026-07-25-002", "supported", policy
        )
        state = build_state(
            policy,
            self.decisions,
            self.hypotheses,
            self.outcomes
            + [
                (Path("REO-2026-07-25-001.json"), calibration),
                (Path("REO-2026-07-25-002.json"), quotient),
            ],
        )
        route = next(
            item
            for item in state["route_evidence_state"]
            if item["route_id"] == "R-GLV-SEMAEV"
        )
        self.assertEqual(
            "decision_review_required",
            route["evidence_axis"]["engine_disposition"],
        )
        self.assertEqual(
            ["REO-2026-07-25-002"], route["route_review_trigger_event_ids"]
        )
        self.assertFalse(state["gate_status"]["promotion_authorized"])

    def test_promotion_gate_cannot_be_enabled_in_engine_policy(self) -> None:
        policy = copy.deepcopy(self.policy)
        policy["gates"]["promotion"]["authorized"] = True
        problems = validate_policy(policy, self.decisions, self.hypotheses)
        self.assertTrue(any("promotion gate must remain closed" in item for item in problems))

    def test_hard_rejection_cannot_be_authorized(self) -> None:
        policy = self.executable_policy()
        candidate = policy["candidate_proposals"][0]
        candidate["hard_rejections"]["hidden_or_unpriced_precomputation"] = True
        problems = validate_policy(policy, self.decisions, self.hypotheses)
        self.assertTrue(
            any("authorization conflicts with hard rejections" in item for item in problems)
        )

    def test_product_and_research_kpis_are_separate(self) -> None:
        queues = self.policy["queue_separation"]
        self.assertNotEqual(
            queues["ecdlp_research"]["source"],
            queues["keyai_product"]["source"],
        )
        self.assertTrue(queues["anti_conflation_rules"])


if __name__ == "__main__":
    unittest.main()
