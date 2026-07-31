#!/usr/bin/env python3
"""Fault-injection tests for Research Engine v0.2 lifecycle and portfolio."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from research_engine_v02 import (
    bind_snapshot,
    build_calibration,
    build_recommendation_binding,
    cost_vector,
    derive_gates,
    expected_information_gain,
    mechanism_assurance_claims,
    optimize_portfolio,
    run_engine,
    score_snapshot,
    snapshot_digest,
    validate_owner_decisions,
    validate_snapshot,
)
from build_research_engine_v02_state import (
    V0_RAW_FILE_SHA256,
    V0_REVIEWED_ROOT,
    historical_boundary,
)
from check_research_engine_v02_acceptance import source_binding_problems
from research_contract_binding import scientific_contract_digests, sha256_json


ROOT = Path(__file__).resolve().parent.parent
DIGEST_ANCHOR_PATH = (
    ROOT
    / "experiments"
    / "engine"
    / "fixtures"
    / "research_engine_v02_snapshot_digest_anchors.json"
)


def generation_binding(
    mechanism: dict | None = None,
    prediction: dict | None = None,
    cost: dict | None = None,
    validator: dict | None = None,
    toy_scope: dict | None = None,
) -> dict:
    mechanism = mechanism or mechanism_contract()
    prediction = prediction or prediction_contract()
    cost = cost or cost_contract()
    validator = validator or validator_contract()
    toy_scope = toy_scope or {
        "curve_family": "toy-j0-curves",
        "max_field_bits": 16,
        "forbidden_targets": ["secp256k1"],
    }
    contract_digests = scientific_contract_digests(
        mechanism,
        prediction,
        cost,
        validator,
    )
    binding_digest = sha256_json(
        {
            "cell_id": "CELL-FIXTURE",
            "route_id": "R-FIXTURE",
            "threat_model": "classical-single-target-plain",
            "toy_scope": toy_scope,
            "contract_digests": contract_digests,
        }
    )
    roles = (
        "algebra",
        "cryptanalysis_skeptic",
        "prior_art",
        "cost_model",
        "validator_design",
    )
    return {
        "draft_id": f"HYP_DRAFT_FIXTURE_{binding_digest[:12].upper()}",
        "draft_sha256": binding_digest,
        "proposal_id": f"HGP-FIXTURE-{binding_digest[:12].upper()}",
        "proposal_sha256": sha256_json(
            {"proposal_binding": binding_digest}
        ),
        "source_commit": "fed55d84675fd96e5f40204b9f5f49baa8c01172",
        "cell_id": "CELL-FIXTURE",
        "typed_evidence_digest": "f" * 64,
        "toy_scope": toy_scope,
        "route_id": "R-FIXTURE",
        "threat_model": "classical-single-target-plain",
        "contract_digests": contract_digests,
        "review_artifacts": [
            {
                "review_id": f"HGR-FIXTURE-{index}",
                "reviewer_role": role,
                "review_sha256": f"{index}" * 64,
            }
            for index, role in enumerate(roles, start=1)
        ],
    }


def policy(
    *,
    max_selected: int = 3,
    quality_bindings: list[dict] | None = None,
) -> dict:
    return {
        "primary_threat_model": "classical-single-target-plain",
        "authorized_owner_roles": ["project_owner"],
        "source_review_ids": ["SR-INDEPENDENT-001"],
        "mechanism_assurance_evidence": mechanism_assurance_registry(),
        "validator_independence_evidence": [
            {
                "evidence_id": "VE-PATH-001",
                "axis": "path",
                "assessment": "verified",
                "sha256": "a" * 64,
                "producer_identity": "fixture-producer",
                "validator_identity": "fixture-validator",
                "same_model": False,
                "same_session": False,
                "shared_context": False,
                "attested_by": "fixture-callgraph-checker",
            },
            {
                "evidence_id": "VE-ARTIFACT-001",
                "axis": "artifact",
                "assessment": "verified",
                "sha256": "b" * 64,
                "producer_identity": "fixture-producer",
                "validator_identity": "fixture-validator",
                "same_model": False,
                "same_session": False,
                "shared_context": False,
                "attested_by": "fixture-replay-checker",
            },
            {
                "evidence_id": "VE-SOURCE-001",
                "axis": "source",
                "assessment": "human_attested",
                "sha256": "c" * 64,
                "producer_identity": "fixture-producer",
                "validator_identity": "fixture-validator",
                "same_model": False,
                "same_session": False,
                "shared_context": False,
                "attested_by": "independent-human-reviewer",
            },
        ],
        "validator_implementation_evidence": [
            {
                "path": "fixtures/independent-validator.py",
                "sha256": "3" * 64,
            }
        ],
        "quality_cleared_draft_bindings": (
            quality_bindings
            if quality_bindings is not None
            else [generation_binding()]
        ),
        "portfolio_max_candidates": 12,
        "max_selected_per_cycle": max_selected,
        "portfolio_budget": {
            "compute_hours": 100,
            "storage_gb": 100,
            "money_usd": 100,
            "implementation_hours": 100,
            "reviewer_hours": 100,
            "wall_time_hours": 100,
            "peak_memory_gb": 100,
            "workers": 10,
            "shared_setup_hours": 100
        },
        "correlation_max_per_group": {},
        "default_correlation_cap": 3,
        "minimum_diversity_tags": 0,
        "required_diversity_tags": [],
        "calibration_min_native_n": 5
    }


def scenario(q: float) -> dict:
    return {
        "prior_live": 0.5,
        "outcomes": [
            {
                "outcome": "signal",
                "p_if_live": q,
                "p_if_dead": 1.0 - q
            },
            {
                "outcome": "no_signal",
                "p_if_live": 1.0 - q,
                "p_if_dead": q
            }
        ]
    }


def mechanism_contract() -> dict:
    contract = {
        "source_objects": ["toy relations"],
        "target_objects": ["validated relation records"],
        "transformation": {
            "kind": "fixture_exact_map",
            "exact_map": "(x, tag) maps to (x, tag, checksum)",
            "domain": "tagged toy relation tuples",
            "codomain": "recoverable toy relation tuples"
        },
        "fixed_target_semantics": {
            "target_slot": "the final relation coordinate",
            "target_action": "the target tag is preserved exactly",
            "same_target_preserved": True
        },
        "exceptional_locus": {
            "definition": "empty in the fixture domain",
            "treatment": "proved_empty"
        },
        "orbit_stabilizer": {
            "acting_group": "the trivial fixture group",
            "stabilizer": "the full trivial group",
            "orbit_size_law": "one for every tested size"
        },
        "relation_semantics": {
            "source_relation": "the raw tuple satisfies the toy relation",
            "target_relation": "the mapped tuple replays the same relation",
            "equivalence_status": "certificate_replayed"
        },
        "recovery_map": {
            "forward": "append the deterministic checksum",
            "inverse": "drop and independently verify the checksum",
            "excluded_components": [],
            "spurious_solution_policy": "reject every checksum mismatch"
        },
        "implementation_identity": {
            "implementation_path": "fixtures/nonexistent-unexecuted.py",
            "sha256": "1" * 64
        },
        "cost_changing_mechanism": {
            "quantity": "validated records per CPU hour",
            "causal_bridge": "the fixture predicts fewer replay operations",
            "growth_law": "a preregistered size-dependent separation",
            "non_orbit_lever": "deterministic checksum sparsity"
        },
        "source_ids": ["fixture-source"]
    }
    claims = mechanism_assurance_claims(contract)
    contract["assurance_bindings"] = {
        "relation_equivalence": {
            "assurance": "certificate_replayed",
            "evidence_id": "ME-RELATION-001",
            "claim_sha256": claims["relation_equivalence"],
        },
        "exceptional_locus": {
            "assurance": "certificate_replayed",
            "evidence_id": "ME-EXCEPTIONAL-001",
            "claim_sha256": claims["exceptional_locus"],
        },
        "recovery_map": {
            "assurance": "independent_reproduction",
            "evidence_id": "ME-RECOVERY-001",
            "claim_sha256": claims["recovery_map"],
        },
        "cost_changing_bridge": {
            "assurance": "independent_reproduction",
            "evidence_id": "ME-COST-001",
            "claim_sha256": claims["cost_changing_bridge"],
        },
    }
    return contract


def mechanism_assurance_registry() -> list[dict]:
    bindings = mechanism_contract()["assurance_bindings"]
    return [
        {
            "evidence_id": item["evidence_id"],
            "topic": topic,
            "assurance": item["assurance"],
            "claim_sha256": item["claim_sha256"],
        }
        for topic, item in bindings.items()
    ]


def prediction_contract(q: float = 0.8) -> dict:
    return {
        "metric": {
            "name": "validated_records_per_hour",
            "unit": "records/hour",
            "recomputation": "count raw accepted rows and divide by measured time"
        },
        "matched_baseline": {
            "baseline_id": "fixture-baseline",
            "implementation_digest": "2" * 64,
            "matching_variables": ["field_bits", "seed", "relation_count"]
        },
        "tested_sizes": [8, 12, 16],
        "expected_direction": "increase",
        "minimum_material_effect": q,
        "decision_threshold": {
            "operator": "ge",
            "value": q
        },
        "stop_rule": {
            "condition": "all frozen fixture sizes have a terminal result",
            "maximum_instances": 9
        },
        "falsifying_outcomes": [
            "matched baseline is equal or faster",
            "the recovery validator rejects a decisive row"
        ]
    }


def cost_contract(*, money: float = 1.0, compute: float = 1.0) -> dict:
    return {
        "online": {"cpu_hours": compute, "gpu_hours": 0},
        "offline": {"cpu_hours": 0, "gpu_hours": 0},
        "wall_time_hours": compute,
        "peak_memory_gb": 1,
        "storage_gb": 1,
        "workers": 1,
        "money_usd": money,
        "implementation_hours": 1,
        "reviewer_hours": 1,
        "preprocessing": {
            "included_in_totals": True,
            "description": "No hidden fixture preprocessing."
        },
        "amortization": {
            "class": "none_single_target",
            "target_count": 1,
            "per_target_cost_included": True
        },
        "success_probability": 0.5,
        "shared_setup": {
            "setup_id": None,
            "hours": 0,
            "expected_reuse": 1
        }
    }


def validator_contract() -> dict:
    return {
        "status": "ready_evidence_bound",
        "raw_artifact_format": {
            "media_type": "application/json",
            "schema_id": "fixture-raw-v1"
        },
        "recomputed_decisive_claim": {
            "claim_id": "fixture-throughput",
            "procedure": "recompute every accepted row from primitive inputs"
        },
        "implementation": {
            "path": "fixtures/independent-validator.py",
            "sha256": "3" * 64
        },
        "prohibited_producer_fields": [
            "claimed_outcome",
            "claimed_metric"
        ],
        "independence": {
            "path_independent": True,
            "artifact_independent": True,
            "source_independent": True,
            "producer_identity": "fixture-producer",
            "validator_identity": "fixture-validator",
            "same_model": False,
            "same_session": False,
            "shared_context": False
        },
        "independence_evidence": {
            "path": {
                "status": "verified",
                "evidence_id": "VE-PATH-001",
                "sha256": "a" * 64,
            },
            "artifact": {
                "status": "verified",
                "evidence_id": "VE-ARTIFACT-001",
                "sha256": "b" * 64,
            },
            "source": {
                "status": "human_attested",
                "evidence_id": "VE-SOURCE-001",
                "sha256": "c" * 64,
            },
        },
        "source_review_requirements": [
            "one digest-bound independent prior-art review"
        ]
    }


def candidate(
    candidate_id: str,
    *,
    version: int = 1,
    q: float = 0.8,
    money: float = 1.0,
    compute: float = 1.0,
    dependencies: list[dict] | None = None,
    curve_family: str = "toy-j0-curves"
) -> dict:
    mechanism = mechanism_contract()
    prediction = prediction_contract(q)
    cost = cost_contract(money=money, compute=compute)
    validator = validator_contract()
    raw = {
        "candidate_id": candidate_id,
        "version": version,
        "created_at": "2026-07-25T00:00:00Z",
        "route_id": "R-FIXTURE",
        "cell_id": "CELL-FIXTURE",
        "typed_evidence_digest": "f" * 64,
        "lane": {
            "lane": "bounded_experiment",
            "target_kind": "toy",
            "direct_target_property_computation": False,
            "attack_execution": True,
            "deliverable": "A non-scientific lifecycle regression result.",
            "experiment_scope": {
                "max_field_bits": 16,
                "forbidden_targets": ["secp256k1"]
            }
        },
        "threat_model": "classical-single-target-plain",
        "target_scope": {
            "kind": "toy",
            "curve_family": curve_family,
            "field_bits": 16,
            "forbidden_targets": ["secp256k1"]
        },
        "source_commit": "fed55d84675fd96e5f40204b9f5f49baa8c01172",
        "source_review_ids": ["SR-INDEPENDENT-001"],
        "generation_binding": generation_binding(
            mechanism,
            prediction,
            cost,
            validator,
            {
                "curve_family": curve_family,
                "max_field_bits": 16,
                "forbidden_targets": ["secp256k1"],
            },
        ),
        "dependencies": dependencies or [],
        "correlation_groups": [],
        "diversity_tags": [f"tag-{candidate_id}"],
        "mechanism_contract": mechanism,
        "prediction_contract": prediction,
        "cost_contract": cost,
        "validator_contract": validator,
        "scoring_contract": {
            "elicitation_ids": [
                f"ELICIT-{candidate_id}-A",
                f"ELICIT-{candidate_id}-B"
            ],
            "scenarios": {
                "low": scenario(max(0.51, q - 0.1)),
                "base": scenario(q),
                "high": scenario(min(0.99, q + 0.1))
            }
        }
    }
    return bind_snapshot(raw)


def bind_as_quality_reviewed(snapshot: dict) -> tuple[dict, dict]:
    rebound = copy.deepcopy(snapshot)
    binding = generation_binding(
        rebound["mechanism_contract"],
        rebound["prediction_contract"],
        rebound["cost_contract"],
        rebound["validator_contract"],
        rebound["generation_binding"]["toy_scope"],
    )
    rebound["generation_binding"] = binding
    rebound = bind_snapshot(rebound)
    return rebound, policy(quality_bindings=[binding])


def lifecycle_to_validator_ready(snapshot: dict) -> list[dict]:
    states = [
        (None, "idea", "migration"),
        ("idea", "screened", "engine"),
        ("screened", "mechanism_specified", "engine"),
        ("mechanism_specified", "validator_ready", "engine")
    ]
    return [
        {
            "event_id": f"REL-2026-07-25-{snapshot['candidate_id']}-{index}",
            "candidate_id": snapshot["candidate_id"],
            "candidate_version": snapshot["version"],
            "candidate_digest": snapshot["snapshot_digest"],
            "occurred_at": f"2026-07-25T00:0{index}:00Z",
            "from_state": source,
            "to_state": target,
            "actor_class": actor,
            "reason": "Deterministic regression-fixture lifecycle transition."
        }
        for index, (source, target, actor) in enumerate(states)
    ]


def desk_complete(snapshot: dict) -> list[dict]:
    events = lifecycle_to_validator_ready(snapshot)
    events.append(
        {
            "event_id": f"REL-2026-07-25-{snapshot['candidate_id']}-4",
            "candidate_id": snapshot["candidate_id"],
            "candidate_version": snapshot["version"],
            "candidate_digest": snapshot["snapshot_digest"],
            "occurred_at": "2026-07-25T00:04:00Z",
            "from_state": "validator_ready",
            "to_state": "terminal",
            "actor_class": "engine",
            "reason": "A non-experimental prerequisite fixture completed.",
            "outcome": "completed"
        }
    )
    return events


def owner_decision(
    snapshot: dict,
    *,
    decision_id: str = "OWNER-AUTH-001",
    status: str = "approved",
    decided_at: str = "2026-07-25T00:05:30Z",
    owner_role: str = "project_owner",
) -> dict:
    return {
        "decision_id": decision_id,
        "decision_type": "owner_authorization",
        "decided_at": decided_at,
        "owner_role": owner_role,
        "candidate_id": snapshot["candidate_id"],
        "candidate_version": snapshot["version"],
        "candidate_digest": snapshot["snapshot_digest"],
        "status": status,
    }


def lifecycle_to_authorized(
    snapshot: dict,
    decision_id: str,
    *,
    engine_policy: dict | None = None,
) -> list[dict]:
    engine_policy = engine_policy or policy()
    events = lifecycle_to_validator_ready(snapshot)
    events.append(
        {
            "event_id": f"REL-2026-07-25-{snapshot['candidate_id']}-4",
            "candidate_id": snapshot["candidate_id"],
            "candidate_version": snapshot["version"],
            "candidate_digest": snapshot["snapshot_digest"],
            "occurred_at": "2026-07-25T00:04:00Z",
            "from_state": "validator_ready",
            "to_state": "admissible",
            "actor_class": "engine",
            "reason": "The fixture passed all derived gates.",
        }
    )
    events.append(
        {
            "event_id": f"REL-2026-07-25-{snapshot['candidate_id']}-5",
            "candidate_id": snapshot["candidate_id"],
            "candidate_version": snapshot["version"],
            "candidate_digest": snapshot["snapshot_digest"],
            "occurred_at": "2026-07-25T00:05:00Z",
            "from_state": "admissible",
            "to_state": "recommended",
            "actor_class": "engine",
            "recommendation_binding": build_recommendation_binding(
                engine_policy,
                [snapshot],
                events,
                "2026-07-25T00:05:00Z",
            ),
            "reason": "The fixture entered the selected portfolio.",
        }
    )
    events.append(
        {
            "event_id": f"REL-2026-07-25-{snapshot['candidate_id']}-6",
            "candidate_id": snapshot["candidate_id"],
            "candidate_version": snapshot["version"],
            "candidate_digest": snapshot["snapshot_digest"],
            "occurred_at": "2026-07-25T00:06:00Z",
            "from_state": "recommended",
            "to_state": "authorized",
            "actor_class": "owner",
            "owner_decision_id": decision_id,
            "reason": "A dated owner decision authorized the frozen fixture.",
        }
    )
    return events


def lifecycle_to_terminal(
    snapshot: dict,
    decision_id: str,
    outcome: str,
    *,
    engine_policy: dict | None = None,
) -> list[dict]:
    events = lifecycle_to_authorized(
        snapshot,
        decision_id,
        engine_policy=engine_policy,
    )
    events.extend(
        [
            {
                "event_id": (
                    f"REL-2026-07-25-{snapshot['candidate_id']}-7"
                ),
                "candidate_id": snapshot["candidate_id"],
                "candidate_version": snapshot["version"],
                "candidate_digest": snapshot["snapshot_digest"],
                "occurred_at": "2026-07-25T00:07:00Z",
                "from_state": "authorized",
                "to_state": "running",
                "actor_class": "engine",
                "reason": "The authorized regression fixture began execution.",
            },
            {
                "event_id": (
                    f"REL-2026-07-25-{snapshot['candidate_id']}-8"
                ),
                "candidate_id": snapshot["candidate_id"],
                "candidate_version": snapshot["version"],
                "candidate_digest": snapshot["snapshot_digest"],
                "occurred_at": "2026-07-25T00:08:00Z",
                "from_state": "running",
                "to_state": "terminal",
                "actor_class": "engine",
                "reason": "The regression fixture reached a terminal outcome.",
                "outcome": outcome,
            },
        ]
    )
    return events


class ResearchEngineV02Tests(unittest.TestCase):
    def test_snapshot_digest_matches_external_committed_anchors(self) -> None:
        fixture = json.loads(DIGEST_ANCHOR_PATH.read_text(encoding="utf-8"))
        expected = (
            "8e91653cf90a1a2b104ee43a94ff5aa2aee91ed22d0c0e1c38d3f4b239a201dc",
            "3eab7d538545b04b00d7b81c23fd55f537430020ca9e2138be2a8d0b637775eb",
        )
        anchors = fixture["anchors"]
        self.assertEqual(
            expected,
            tuple(
                anchor["expected_snapshot_sha256"] for anchor in anchors
            ),
        )
        computed = tuple(
            snapshot_digest(anchor["snapshot"]) for anchor in anchors
        )
        self.assertEqual(expected, computed)
        self.assertNotEqual(computed[0], computed[1])
        for anchor in anchors:
            self.assertEqual(
                anchor["expected_snapshot_sha256"],
                bind_snapshot(anchor["snapshot"])["snapshot_digest"],
            )

    def test_self_declared_validator_without_registered_evidence_is_rejected(
        self,
    ) -> None:
        snapshot = candidate("UNREGISTERED-VALIDATOR")
        untrusted_policy = policy()
        untrusted_policy["validator_independence_evidence"] = []
        problems = validate_snapshot(snapshot, untrusted_policy)
        self.assertTrue(
            any(
                "evidence_id is not registered" in problem
                for problem in problems
            )
        )
        self.assertIn(
            "missing_independent_validator",
            derive_gates(snapshot, untrusted_policy),
        )

    def test_source_independence_requires_third_party_human_attestation(
        self,
    ) -> None:
        snapshot = candidate("SELF-ATTESTED-SOURCE")
        self_attested_policy = policy()
        source = next(
            item
            for item in self_attested_policy[
                "validator_independence_evidence"
            ]
            if item["axis"] == "source"
        )
        source["attested_by"] = "fixture-producer"
        problems = validate_snapshot(snapshot, self_attested_policy)
        self.assertTrue(
            any(
                "source attester is not independent" in problem
                for problem in problems
            )
        )

    def test_design_only_validator_never_becomes_admissible(self) -> None:
        snapshot = candidate("DESIGN-ONLY-VALIDATOR")
        contract = snapshot["validator_contract"]
        contract["status"] = "design_only_unverified"
        for key in (
            "path_independent",
            "artifact_independent",
            "source_independent",
        ):
            contract["independence"][key] = False
        for key in ("same_model", "same_session", "shared_context"):
            contract["independence"][key] = None
        for axis in ("path", "artifact", "source"):
            contract["independence_evidence"][axis] = {
                "status": "planned",
                "evidence_id": None,
                "sha256": None,
            }
        snapshot = bind_snapshot(snapshot)
        self.assertIn(
            "missing_independent_validator",
            derive_gates(snapshot, policy()),
        )

    def test_candidate_requires_registered_quality_cleared_draft(
        self,
    ) -> None:
        snapshot = candidate("UNBOUND-DRAFT")
        snapshot["generation_binding"]["draft_sha256"] = "f" * 64
        snapshot = bind_snapshot(snapshot)
        self.assertIn(
            "missing_quality_cleared_generation_binding",
            derive_gates(snapshot, policy()),
        )

    def test_candidate_source_commit_must_match_generation_binding(
        self,
    ) -> None:
        snapshot = candidate("MISMATCHED-SOURCE")
        snapshot["source_commit"] = "e1dfd77d9c6bfe28936fb54df1437829fcf3c355"
        snapshot = bind_snapshot(snapshot)
        problems = validate_snapshot(snapshot, policy())
        self.assertTrue(
            any(
                "source_commit: generation binding mismatch" in problem
                for problem in problems
            )
        )
        self.assertIn(
            "invalid_candidate_snapshot",
            derive_gates(snapshot, policy()),
        )

    def test_post_review_contract_mutation_invalidates_generation_binding(
        self,
    ) -> None:
        snapshot = candidate("POST-REVIEW-MUTATION")
        snapshot["cost_contract"]["amortization"] = {
            "class": "multi_target",
            "target_count": 1000,
            "per_target_cost_included": True,
        }
        snapshot = bind_snapshot(snapshot)
        problems = validate_snapshot(snapshot, policy())
        self.assertTrue(
            any(
                "cost_contract_sha256: reviewed contract digest mismatch"
                in problem
                for problem in problems
            )
        )
        self.assertIn(
            "missing_quality_cleared_generation_binding",
            derive_gates(snapshot, policy()),
        )

    def test_reviewed_multi_target_cost_derives_threat_model_drift(
        self,
    ) -> None:
        snapshot = candidate("MULTI-TARGET-LAUNDERING")
        snapshot["cost_contract"]["offline"] = {
            "cpu_hours": 10**6,
            "gpu_hours": 0,
        }
        snapshot["cost_contract"]["amortization"] = {
            "class": "multi_target",
            "target_count": 10**6,
            "per_target_cost_included": True,
        }
        snapshot, reviewed_policy = bind_as_quality_reviewed(snapshot)
        self.assertEqual([], validate_snapshot(snapshot, reviewed_policy))
        self.assertIn(
            "changes_threat_model",
            derive_gates(snapshot, reviewed_policy),
        )
        state = run_engine(
            reviewed_policy,
            [snapshot],
            {
                "lifecycle_events": lifecycle_to_validator_ready(snapshot),
                "outcomes": [],
            },
            [],
        )
        self.assertEqual([], state["admissible"])
        self.assertEqual([], state["recommended"])

    def test_every_prediction_size_respects_reviewed_toy_ceiling(
        self,
    ) -> None:
        snapshot = candidate("MATRIX-CEILING")
        snapshot["prediction_contract"]["tested_sizes"] = [8, 16, 2048]
        snapshot, reviewed_policy = bind_as_quality_reviewed(snapshot)
        problems = validate_snapshot(snapshot, reviewed_policy)
        self.assertTrue(
            any("exceeds bounded lane ceiling" in problem for problem in problems)
        )
        gates = derive_gates(snapshot, reviewed_policy)
        self.assertIn("toy_scope_exceeded", gates)
        self.assertIn("invalid_candidate_snapshot", gates)

    def test_schema_complete_unproved_prose_cannot_clear_mechanism_gate(
        self,
    ) -> None:
        snapshot = candidate("SCHEMA-COMPLETE-PROSE")
        mechanism = snapshot["mechanism_contract"]
        mechanism["source_objects"] = ["x"]
        mechanism["target_objects"] = ["x"]
        mechanism["source_ids"] = ["x"]
        for group, keys in {
            "transformation": ("kind", "exact_map", "domain", "codomain"),
            "fixed_target_semantics": ("target_slot", "target_action"),
            "orbit_stabilizer": (
                "acting_group",
                "stabilizer",
                "orbit_size_law",
            ),
            "relation_semantics": ("source_relation", "target_relation"),
            "recovery_map": (
                "forward",
                "inverse",
                "spurious_solution_policy",
            ),
            "cost_changing_mechanism": (
                "quantity",
                "causal_bridge",
                "growth_law",
                "non_orbit_lever",
            ),
        }.items():
            for key in keys:
                mechanism[group][key] = "x"
        mechanism["exceptional_locus"]["definition"] = "x"
        mechanism["relation_semantics"][
            "equivalence_status"
        ] = "specified_unproved"
        snapshot, reviewed_policy = bind_as_quality_reviewed(snapshot)
        self.assertIn(
            "missing_exact_mechanism",
            derive_gates(snapshot, reviewed_policy),
        )

    def test_self_asserted_proved_prose_without_registered_claim_is_rejected(
        self,
    ) -> None:
        snapshot = candidate("FORGED-PROVED-PROSE")
        relation = snapshot["mechanism_contract"]["relation_semantics"]
        relation["source_relation"] = "x"
        relation["target_relation"] = "x"
        relation["equivalence_status"] = "proved"
        binding = snapshot["mechanism_contract"]["assurance_bindings"][
            "relation_equivalence"
        ]
        binding["assurance"] = "lean_kernel"
        binding["evidence_id"] = "ME-FORGED-LEAN-001"
        binding["claim_sha256"] = "f" * 64
        snapshot, reviewed_policy = bind_as_quality_reviewed(snapshot)
        self.assertIn(
            "missing_exact_mechanism",
            derive_gates(snapshot, reviewed_policy),
        )

    def test_prediction_threshold_requires_a_numeric_value(self) -> None:
        snapshot = candidate("BANANA-THRESHOLD")
        snapshot["prediction_contract"]["decision_threshold"][
            "value"
        ] = "banana"
        snapshot, reviewed_policy = bind_as_quality_reviewed(snapshot)
        self.assertIn(
            "missing_falsifiable_prediction",
            derive_gates(snapshot, reviewed_policy),
        )

    def test_prediction_rejects_duplicate_sizes_and_extra_fields(self) -> None:
        snapshot = candidate("PREDICTION-SCHEMA-DRIFT")
        snapshot["prediction_contract"]["tested_sizes"] = [8, 8, 16]
        snapshot["prediction_contract"]["metric"]["decorative"] = "x"
        snapshot, reviewed_policy = bind_as_quality_reviewed(snapshot)
        problems = validate_snapshot(snapshot, reviewed_policy)
        self.assertTrue(any("duplicate entries" in problem for problem in problems))
        self.assertTrue(any("unexpected decorative" in problem for problem in problems))

    def test_ready_validator_requires_registered_implementation(self) -> None:
        snapshot = candidate("FAKE-VALIDATOR-HASH")
        snapshot["validator_contract"]["implementation"]["sha256"] = "9" * 64
        snapshot, reviewed_policy = bind_as_quality_reviewed(snapshot)
        self.assertIn(
            "missing_independent_validator",
            derive_gates(snapshot, reviewed_policy),
        )

    def test_bounded_experiment_cannot_claim_zero_execution_cost(self) -> None:
        snapshot = candidate("ZERO-EXECUTION-COST")
        snapshot["cost_contract"].update(
            {
                "online": {"cpu_hours": 0, "gpu_hours": 0},
                "offline": {"cpu_hours": 0, "gpu_hours": 0},
                "wall_time_hours": 0,
                "peak_memory_gb": 0,
                "storage_gb": 0,
            }
        )
        snapshot, reviewed_policy = bind_as_quality_reviewed(snapshot)
        self.assertIn(
            "missing_full_cost_contract",
            derive_gates(snapshot, reviewed_policy),
        )

    def test_candidate_route_cannot_drift_from_reviewed_draft(self) -> None:
        snapshot = candidate("ROUTE-RETARGET")
        snapshot["route_id"] = "R-OTHER"
        snapshot = bind_snapshot(snapshot)
        problems = validate_snapshot(snapshot, policy())
        self.assertTrue(
            any(
                "route_id: generation binding mismatch" in problem
                for problem in problems
            )
        )

    def test_generated_lifecycle_state_binds_both_canonical_inputs(
        self,
    ) -> None:
        lifecycle_state = json.loads(
            (ROOT / "data" / "research_engine_v02_state.json").read_text(
                encoding="utf-8"
            )
        )
        lifecycle_policy = json.loads(
            (ROOT / "repo" / "RESEARCH_ENGINE_LIFECYCLE_V0.json").read_text(
                encoding="utf-8"
            )
        )
        generation_state = json.loads(
            (ROOT / "data" / "research_engine_state.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            [],
            source_binding_problems(
                lifecycle_state,
                lifecycle_policy,
                generation_state,
            ),
        )
        changed_policy = copy.deepcopy(lifecycle_policy)
        changed_policy["max_selected_per_cycle"] += 1
        self.assertTrue(
            source_binding_problems(
                lifecycle_state,
                changed_policy,
                generation_state,
            )
        )
        changed_generation = copy.deepcopy(generation_state)
        changed_generation["status"] = "fabricated-idempotent-output"
        self.assertTrue(
            source_binding_problems(
                lifecycle_state,
                lifecycle_policy,
                changed_generation,
            )
        )

    def test_terminal_candidates_release_selection_slots(self) -> None:
        candidates = [candidate(name) for name in ("A", "B", "C", "D")]
        events = []
        for item in candidates[:3]:
            events.extend(desk_complete(item))
        events.extend(lifecycle_to_validator_ready(candidates[3]))
        state = run_engine(
            policy(
                max_selected=3,
                quality_bindings=[
                    item["generation_binding"] for item in candidates
                ],
            ),
            candidates,
            {"lifecycle_events": events, "outcomes": []},
            []
        )
        self.assertEqual(["D"], state["recommended"])
        self.assertTrue(state["terminal_candidates_release_slots"])

    def test_completed_prerequisite_unlocks_without_consuming_slot(self) -> None:
        prerequisite = candidate("A")
        dependent = candidate(
            "B",
            dependencies=[
                {
                    "candidate_id": "A",
                    "minimum_version": 1,
                    "accepted_outcomes": ["completed"]
                }
            ]
        )
        events = desk_complete(prerequisite)
        events.extend(lifecycle_to_validator_ready(dependent))
        state = run_engine(
            policy(max_selected=1),
            [prerequisite, dependent],
            {"lifecycle_events": events, "outcomes": []},
            []
        )
        self.assertEqual(["B"], state["recommended"])
        self.assertIn("A", state["completed_prerequisites"])

    def test_uncompleted_prerequisite_cannot_be_co_selected(self) -> None:
        prerequisite = candidate("A")
        dependent = candidate(
            "B",
            dependencies=[
                {
                    "candidate_id": "A",
                    "minimum_version": 1,
                    "accepted_outcomes": ["completed"],
                }
            ],
        )
        state = run_engine(
            policy(max_selected=2),
            [prerequisite, dependent],
            {
                "lifecycle_events": (
                    lifecycle_to_validator_ready(prerequisite)
                    + lifecycle_to_validator_ready(dependent)
                ),
                "outcomes": [],
            },
            [],
        )
        self.assertEqual(["A"], state["recommended"])
        self.assertIn(
            "unsatisfied_dependency",
            next(
                item["gates"]
                for item in state["candidates"]
                if item["candidate_id"] == "B"
            ),
        )

    def test_completed_prerequisite_must_meet_minimum_version(self) -> None:
        prerequisite = candidate("A", version=1)
        dependent = candidate(
            "B",
            dependencies=[
                {
                    "candidate_id": "A",
                    "minimum_version": 2,
                    "accepted_outcomes": ["completed"],
                }
            ],
        )
        state = run_engine(
            policy(max_selected=2),
            [prerequisite, dependent],
            {
                "lifecycle_events": (
                    desk_complete(prerequisite)
                    + lifecycle_to_validator_ready(dependent)
                ),
                "outcomes": [],
            },
            [],
        )
        self.assertEqual([], state["recommended"])
        self.assertIn(
            "unsatisfied_dependency",
            next(
                item["gates"]
                for item in state["candidates"]
                if item["candidate_id"] == "B"
            ),
        )

    def test_invalid_terminal_event_cannot_unlock_dependency(self) -> None:
        prerequisite = candidate("A")
        dependent = candidate(
            "B",
            dependencies=[
                {
                    "candidate_id": "A",
                    "minimum_version": 1,
                    "accepted_outcomes": ["completed"],
                }
            ],
        )
        forged_terminal = {
            "event_id": "REL-2026-07-25-A-FORGED",
            "candidate_id": prerequisite["candidate_id"],
            "candidate_version": prerequisite["version"],
            "candidate_digest": prerequisite["snapshot_digest"],
            "occurred_at": "2026-07-25T00:00:00Z",
            "from_state": None,
            "to_state": "terminal",
            "actor_class": "engine",
            "reason": "Fault injection: skip the required lifecycle.",
            "outcome": "completed",
        }
        state = run_engine(
            policy(max_selected=1),
            [prerequisite, dependent],
            {
                "lifecycle_events": (
                    [forged_terminal]
                    + lifecycle_to_validator_ready(dependent)
                ),
                "outcomes": [],
            },
            [],
        )
        self.assertEqual([], state["recommended"])
        self.assertTrue(state["lifecycle_problems"])
        self.assertIn(
            "invalid_lifecycle_state",
            next(
                item["gates"]
                for item in state["candidates"]
                if item["candidate_id"] == "B"
            ),
        )

    def test_calibration_outcome_cannot_unlock_dependency(self) -> None:
        prerequisite = candidate("A")
        dependent = candidate(
            "B",
            dependencies=[
                {
                    "candidate_id": "A",
                    "minimum_version": 1,
                    "accepted_outcomes": ["completed"],
                }
            ],
        )
        injected_outcome = {
            "event_id": "NATIVE-DEPENDENCY-INJECTION",
            "event_class": "native_empirical",
            "candidate_digest": prerequisite["snapshot_digest"],
            "outcome": "completed",
            "frozen_prediction": {"prior_live": 0.5},
            "actual_live": True,
        }
        state = run_engine(
            policy(max_selected=1),
            [prerequisite, dependent],
            {
                "lifecycle_events": lifecycle_to_validator_ready(dependent),
                "outcomes": [injected_outcome],
            },
            [],
        )
        self.assertEqual([], state["recommended"])
        self.assertIn(
            "unsatisfied_dependency",
            next(
                item["gates"]
                for item in state["candidates"]
                if item["candidate_id"] == "B"
            ),
        )

    def test_unsuccessful_terminal_outcomes_do_not_unlock_dependency(
        self,
    ) -> None:
        for outcome in ("falsified", "inconclusive"):
            with self.subTest(outcome=outcome):
                prerequisite = candidate(f"A-{outcome.upper()}")
                dependent = candidate(
                    f"B-{outcome.upper()}",
                    dependencies=[
                        {
                            "candidate_id": prerequisite["candidate_id"],
                            "minimum_version": 1,
                            "accepted_outcomes": ["completed"],
                        }
                    ],
                )
                decision_id = f"OWNER-AUTH-{outcome.upper()}"
                state = run_engine(
                    policy(max_selected=1),
                    [prerequisite, dependent],
                    {
                        "lifecycle_events": (
                            lifecycle_to_terminal(
                                prerequisite,
                                decision_id,
                                outcome,
                                engine_policy=policy(max_selected=1),
                            )
                            + lifecycle_to_validator_ready(dependent)
                        ),
                        "outcomes": [],
                    },
                    [
                        owner_decision(
                            prerequisite,
                            decision_id=decision_id,
                        )
                    ],
                )
                self.assertEqual([], state["lifecycle_problems"])
                self.assertIn(
                    "unsatisfied_dependency",
                    next(
                        item["gates"]
                        for item in state["candidates"]
                        if item["candidate_id"] == dependent["candidate_id"]
                    ),
                )

    def test_successful_but_unaccepted_outcome_does_not_unlock_dependency(
        self,
    ) -> None:
        prerequisite = candidate("A-SUPPORTED")
        dependent = candidate(
            "B-REQUIRES-COMPLETED",
            dependencies=[
                {
                    "candidate_id": prerequisite["candidate_id"],
                    "minimum_version": 1,
                    "accepted_outcomes": ["completed"],
                }
            ],
        )
        decision_id = "OWNER-AUTH-SUPPORTED"
        state = run_engine(
            policy(max_selected=1),
            [prerequisite, dependent],
            {
                "lifecycle_events": (
                    lifecycle_to_terminal(
                        prerequisite,
                        decision_id,
                        "supported",
                        engine_policy=policy(max_selected=1),
                    )
                    + lifecycle_to_validator_ready(dependent)
                ),
                "outcomes": [],
            },
            [
                owner_decision(
                    prerequisite,
                    decision_id=decision_id,
                )
            ],
        )
        self.assertEqual([], state["lifecycle_problems"])
        self.assertIn(
            "unsatisfied_dependency",
            next(
                item["gates"]
                for item in state["candidates"]
                if item["candidate_id"] == dependent["candidate_id"]
            ),
        )

    def test_nonterminal_outcome_field_cannot_unlock_dependency(self) -> None:
        prerequisite = candidate("A-NONTERMINAL")
        dependent = candidate(
            "B-NONTERMINAL",
            dependencies=[
                {
                    "candidate_id": prerequisite["candidate_id"],
                    "minimum_version": 1,
                    "accepted_outcomes": ["completed"],
                }
            ],
        )
        prerequisite_events = lifecycle_to_validator_ready(prerequisite)[:2]
        prerequisite_events[-1]["outcome"] = "completed"
        state = run_engine(
            policy(max_selected=1),
            [prerequisite, dependent],
            {
                "lifecycle_events": (
                    prerequisite_events
                    + lifecycle_to_validator_ready(dependent)
                ),
                "outcomes": [],
            },
            [],
        )
        self.assertEqual([], state["lifecycle_problems"])
        self.assertIn(
            "unsatisfied_dependency",
            next(
                item["gates"]
                for item in state["candidates"]
                if item["candidate_id"] == dependent["candidate_id"]
            ),
        )

    def test_current_policy_cannot_rewrite_frozen_calibration(self) -> None:
        snapshot = candidate("A")
        outcome = {
            "event_id": "NATIVE-001",
            "event_class": "native_empirical",
            "candidate_digest": snapshot["snapshot_digest"],
            "frozen_prediction": {"prior_live": 0.7},
            "actual_live": False
        }
        first = build_calibration([snapshot], [outcome])
        changed_policy = policy()
        changed_policy["portfolio_budget"]["money_usd"] = 0.01
        second = run_engine(
            changed_policy,
            [snapshot],
            {"lifecycle_events": [], "outcomes": [outcome]},
            []
        )["calibration"]
        self.assertEqual(first, second)
        self.assertEqual((0.7 - 0.0) ** 2, first["scores"][0]["brier"])

    def test_duplicate_outcome_event_is_not_double_counted(self) -> None:
        snapshot = candidate("A")
        outcome = {
            "event_id": "NATIVE-001",
            "event_class": "native_empirical",
            "candidate_digest": snapshot["snapshot_digest"],
            "frozen_prediction": {"prior_live": 0.7},
            "actual_live": False,
        }
        calibration = build_calibration(
            [snapshot],
            [outcome, copy.deepcopy(outcome)],
        )
        self.assertEqual(1, calibration["calibration_n"])
        self.assertEqual(1, len(calibration["scores"]))
        self.assertTrue(
            any(
                "duplicate event_id NATIVE-001" in problem
                for problem in calibration["rejected_events"]
            )
        )

    def test_structural_results_do_not_enter_brier_calibration(self) -> None:
        snapshot = candidate("A")
        events = [
            {
                "event_id": "STRUCTURAL-001",
                "event_class": "structural",
                "candidate_digest": snapshot["snapshot_digest"],
                "frozen_prediction": {"prior_live": 1.0},
                "actual_live": True,
            },
            {
                "event_id": "HISTORICAL-001",
                "event_class": "historical_migration",
                "candidate_digest": snapshot["snapshot_digest"],
                "frozen_prediction": {"prior_live": 1.0},
                "actual_live": True,
            },
            {
                "event_id": "NATIVE-001",
                "event_class": "native_empirical",
                "candidate_digest": snapshot["snapshot_digest"],
                "frozen_prediction": {"prior_live": 0.7},
                "actual_live": False,
            },
        ]
        calibration = build_calibration([snapshot], events)
        self.assertEqual(1, calibration["calibration_n"])
        self.assertAlmostEqual(0.49, calibration["mean_brier"])
        self.assertEqual(1, calibration["excluded_event_classes"]["structural"])
        self.assertEqual(
            1,
            calibration["excluded_event_classes"]["historical_migration"],
        )
        empty = build_calibration(
            [snapshot],
            events[:2],
        )
        self.assertEqual(0, empty["calibration_n"])
        self.assertIsNone(empty["mean_brier"])

    def test_prose_only_mechanism_packet_does_not_clear_gate(self) -> None:
        snapshot = candidate("A")
        snapshot["mechanism_contract"] = {
            "description": "This prose sounds precise but defines no map."
        }
        snapshot = bind_snapshot(snapshot)
        self.assertIn("missing_exact_mechanism", derive_gates(snapshot, policy()))

    def test_exhaustive_portfolio_beats_greedy_ratio_counterexample(self) -> None:
        def entry(name: str, value: float, money: float) -> dict:
            return {
                "candidate_id": name,
                "snapshot": {
                    "dependencies": [],
                    "correlation_groups": [],
                    "diversity_tags": [name]
                },
                "score": {
                    "eig_bits": {
                        "low": value,
                        "base": value,
                        "high": value
                    }
                },
                "cost_vector": {
                    "compute_hours": 0,
                    "storage_gb": 0,
                    "money_usd": money,
                    "implementation_hours": 0,
                    "reviewer_hours": 0,
                    "wall_time_hours": 0,
                    "peak_memory_gb": 0,
                    "workers": 1,
                    "shared_setup_id": None,
                    "shared_setup_hours": 0
                }
            }

        entries = [
            entry("A", 10.0, 6.0),
            entry("B", 8.0, 5.0),
            entry("C", 8.0, 5.0)
        ]
        comparison_policy = policy(max_selected=2)
        comparison_policy["portfolio_budget"]["money_usd"] = 10.0
        result = optimize_portfolio(entries, comparison_policy)
        self.assertEqual(["B", "C"], result["selected_ids"])
        self.assertEqual(16.0, result["objective_eig_bits"])

    def test_eig_matches_external_numeric_anchor(self) -> None:
        self.assertAlmostEqual(
            0.2780719051126377,
            expected_information_gain(scenario(0.8)),
            places=15,
        )

    def test_shared_setup_is_charged_once_per_portfolio(self) -> None:
        def entry(name: str) -> dict:
            return {
                "candidate_id": name,
                "snapshot": {
                    "dependencies": [],
                    "correlation_groups": [],
                    "diversity_tags": [name],
                },
                "score": {
                    "eig_bits": {"low": 1.0, "base": 1.0, "high": 1.0}
                },
                "cost_vector": {
                    "compute_hours": 0,
                    "storage_gb": 0,
                    "money_usd": 0,
                    "implementation_hours": 0,
                    "reviewer_hours": 0,
                    "wall_time_hours": 1,
                    "peak_memory_gb": 1,
                    "workers": 1,
                    "shared_setup_id": "SHARED-ALGEBRA-STACK",
                    "shared_setup_hours": 6,
                },
            }

        comparison_policy = policy(max_selected=2)
        comparison_policy["portfolio_budget"]["shared_setup_hours"] = 6
        result = optimize_portfolio(
            [entry("A"), entry("B")],
            comparison_policy,
        )
        self.assertEqual(["A", "B"], result["selected_ids"])
        self.assertEqual(6.0, result["costs"]["shared_setup_hours"])

    def test_peak_resources_use_maximum_not_sum(self) -> None:
        def entry(
            name: str,
            wall_time: float,
            memory: float,
            workers: int,
        ) -> dict:
            return {
                "candidate_id": name,
                "snapshot": {
                    "dependencies": [],
                    "correlation_groups": [],
                    "diversity_tags": [name],
                },
                "score": {
                    "eig_bits": {"low": 1.0, "base": 1.0, "high": 1.0}
                },
                "cost_vector": {
                    "compute_hours": 0,
                    "storage_gb": 0,
                    "money_usd": 0,
                    "implementation_hours": 0,
                    "reviewer_hours": 0,
                    "wall_time_hours": wall_time,
                    "peak_memory_gb": memory,
                    "workers": workers,
                    "shared_setup_id": None,
                    "shared_setup_hours": 0,
                },
            }

        comparison_policy = policy(max_selected=2)
        comparison_policy["portfolio_budget"].update(
            {
                "wall_time_hours": 8,
                "peak_memory_gb": 6,
                "workers": 3,
            }
        )
        result = optimize_portfolio(
            [entry("A", 8, 6, 3), entry("B", 7, 5, 2)],
            comparison_policy,
        )
        self.assertEqual(["A", "B"], result["selected_ids"])
        self.assertEqual(8.0, result["costs"]["wall_time_hours"])
        self.assertEqual(6.0, result["costs"]["peak_memory_gb"])
        self.assertEqual(3.0, result["costs"]["workers"])

    def test_portfolio_rejects_two_active_versions_with_one_candidate_id(
        self,
    ) -> None:
        snapshots = [candidate("A", version=1), candidate("A", version=2)]
        entries = [
            {
                "candidate_id": snapshot["candidate_id"],
                "snapshot": snapshot,
                "score": score_snapshot(snapshot),
                "cost_vector": cost_vector(snapshot),
            }
            for snapshot in snapshots
        ]
        result = optimize_portfolio(entries, policy(max_selected=2))
        self.assertEqual(
            "invalid_duplicate_candidate_ids",
            result["status"],
        )
        self.assertEqual(["A"], result["duplicate_candidate_ids"])
        self.assertEqual([], result["selected_ids"])

    def test_more_than_three_candidates_receive_real_portfolio_comparison(self) -> None:
        candidates = [
            candidate(name, q=0.65 + index * 0.05)
            for index, name in enumerate(("A", "B", "C", "D"))
        ]
        events = [
            event
            for item in candidates
            for event in lifecycle_to_validator_ready(item)
        ]
        state = run_engine(
            policy(
                max_selected=3,
                quality_bindings=[
                    item["generation_binding"] for item in candidates
                ],
            ),
            candidates,
            {"lifecycle_events": events, "outcomes": []},
            []
        )
        comparison = state["portfolio"]["base"]
        self.assertEqual("compared", comparison["status"])
        self.assertEqual(4, comparison["candidate_count"])
        self.assertEqual(16, comparison["combination_count"])
        self.assertEqual(3, len(comparison["selected_ids"]))
        self.assertEqual(1, len(state["deferred"]))
        deferred = state["deferred"][0]
        self.assertIn(deferred["candidate_id"], {"A", "B", "C", "D"})
        self.assertEqual(
            next(
                item["snapshot_digest"]
                for item in candidates
                if item["candidate_id"] == deferred["candidate_id"]
            ),
            deferred["candidate_digest"],
        )
        self.assertEqual([], state["authorized"])

    def test_zero_retention_is_a_success_not_a_fallback(self) -> None:
        gated = candidate("A", curve_family="secp256k1")
        state = run_engine(
            policy(),
            [gated],
            {"lifecycle_events": lifecycle_to_validator_ready(gated), "outcomes": []},
            [],
        )
        self.assertEqual("zero_retention_success", state["selection_status"])
        self.assertEqual([], state["admissible"])
        self.assertEqual([], state["recommended"])
        self.assertEqual([], state["authorized"])

    def test_owner_decision_must_postdate_immutable_snapshot(self) -> None:
        snapshot = candidate("A")
        decision = {
            "decision_id": "OWNER-PREDATE-001",
            "decision_type": "owner_authorization",
            "decided_at": "2026-07-24T23:59:59Z",
            "owner_role": "project_owner",
            "candidate_id": snapshot["candidate_id"],
            "candidate_version": snapshot["version"],
            "candidate_digest": snapshot["snapshot_digest"],
            "status": "approved",
        }
        problems = validate_owner_decisions(
            [decision],
            {(snapshot["candidate_id"], snapshot["version"]): snapshot},
        )
        self.assertTrue(any("predates" in problem for problem in problems))
        state = run_engine(
            policy(),
            [snapshot],
            {
                "lifecycle_events": lifecycle_to_validator_ready(snapshot),
                "outcomes": [],
            },
            [decision],
        )
        self.assertEqual([], state["authorized"])

    def test_owner_decision_without_authorized_lifecycle_event_does_not_authorize(
        self,
    ) -> None:
        snapshot = candidate("DECISION-ONLY")
        decision = owner_decision(snapshot)
        state = run_engine(
            policy(),
            [snapshot],
            {
                "lifecycle_events": lifecycle_to_validator_ready(snapshot),
                "outcomes": [],
            },
            [decision],
        )
        self.assertEqual(["DECISION-ONLY"], state["recommended"])
        self.assertEqual([], state["authorized"])

    def test_recommended_event_must_match_recomputed_portfolio(self) -> None:
        low = candidate("LOW", q=0.55)
        high = candidate("HIGH", q=0.95)
        engine_policy = policy(
            max_selected=1,
            quality_bindings=[
                low["generation_binding"],
                high["generation_binding"],
            ],
        )
        decision = owner_decision(low, decision_id="OWNER-FORGED-REC-001")
        events = (
            lifecycle_to_authorized(
                low,
                decision["decision_id"],
                engine_policy=engine_policy,
            )
            + lifecycle_to_validator_ready(high)
        )
        recommended_event = next(
            event
            for event in events
            if event.get("to_state") == "recommended"
        )
        recommended_event["recommendation_binding"] = (
            build_recommendation_binding(
                engine_policy,
                [low],
                events,
                "2026-07-25T00:05:00Z",
            )
        )
        expected = build_recommendation_binding(
            engine_policy,
            [low, high],
            events,
            "2026-07-25T00:05:00Z",
        )
        self.assertEqual(
            ["HIGH"],
            [
                item["candidate_id"]
                for item in expected["selected_snapshots"]
            ],
        )
        state = run_engine(
            engine_policy,
            [low, high],
            {"lifecycle_events": events, "outcomes": []},
            [decision],
        )
        self.assertEqual([], state["authorized"])
        self.assertTrue(
            any(
                "recomputed base portfolio" in problem
                or "candidate was not selected" in problem
                for problem in state["lifecycle_problems"]
            )
        )

    def test_authorized_state_remains_visible_after_recommendation_slot_release(
        self,
    ) -> None:
        snapshot = candidate("AUTHORIZED")
        decision = owner_decision(snapshot)
        state = run_engine(
            policy(),
            [snapshot],
            {
                "lifecycle_events": lifecycle_to_authorized(
                    snapshot, decision["decision_id"]
                ),
                "outcomes": [],
            },
            [decision],
        )
        self.assertEqual([], state["recommended"])
        self.assertEqual(["AUTHORIZED"], state["authorized"])
        self.assertEqual([], state["lifecycle_problems"])

    def test_latest_owner_revocation_removes_current_authorization(self) -> None:
        snapshot = candidate("REVOKED")
        approved = owner_decision(snapshot)
        revoked = owner_decision(
            snapshot,
            decision_id="OWNER-REVOKE-001",
            status="revoked",
            decided_at="2026-07-25T00:05:30Z",
        )
        state = run_engine(
            policy(),
            [snapshot],
            {
                "lifecycle_events": lifecycle_to_authorized(
                    snapshot, approved["decision_id"]
                ),
                "outcomes": [],
            },
            [approved, revoked],
        )
        self.assertEqual([], state["authorized"])
        self.assertTrue(
            any(
                "no effective approved owner decision" in problem
                for problem in state["lifecycle_problems"]
            )
        )

    def test_unrecognized_owner_role_cannot_authorize(self) -> None:
        snapshot = candidate("WRONG-OWNER")
        decision = owner_decision(snapshot, owner_role="automation")
        state = run_engine(
            policy(),
            [snapshot],
            {
                "lifecycle_events": lifecycle_to_authorized(
                    snapshot, decision["decision_id"]
                ),
                "outcomes": [],
            },
            [decision],
        )
        self.assertEqual([], state["authorized"])
        self.assertTrue(
            any(
                "owner_role: not authorized by policy" in problem
                for problem in state["lifecycle_problems"]
            )
        )

    def test_owner_decision_requires_timezone(self) -> None:
        snapshot = candidate("NAIVE-TIME")
        decision = owner_decision(
            snapshot, decided_at="2026-07-25T00:05:30"
        )
        problems = validate_owner_decisions(
            [decision],
            {(snapshot["candidate_id"], snapshot["version"]): snapshot},
            ["project_owner"],
        )
        self.assertTrue(any("decided_at: invalid" in problem for problem in problems))

    def test_authorization_event_cannot_predate_owner_decision(self) -> None:
        snapshot = candidate("FUTURE-DECISION")
        decision = owner_decision(
            snapshot, decided_at="2026-07-25T00:07:00Z"
        )
        state = run_engine(
            policy(),
            [snapshot],
            {
                "lifecycle_events": lifecycle_to_authorized(
                    snapshot, decision["decision_id"]
                ),
                "outcomes": [],
            },
            [decision],
        )
        self.assertEqual([], state["authorized"])
        self.assertTrue(
            any(
                "authorization predates owner decision" in problem
                for problem in state["lifecycle_problems"]
            )
        )

    def test_owner_decision_cannot_bypass_exact_target_gate(self) -> None:
        snapshot = candidate("EXACT", curve_family="secp256k1")
        events = lifecycle_to_validator_ready(snapshot)
        decision = {
            "decision_id": "OWNER-EXACT-001",
            "decision_type": "owner_authorization",
            "decided_at": "2026-07-25T01:00:00Z",
            "owner_role": "project_owner",
            "candidate_id": snapshot["candidate_id"],
            "candidate_version": snapshot["version"],
            "candidate_digest": snapshot["snapshot_digest"],
            "status": "approved"
        }
        state = run_engine(
            policy(),
            [snapshot],
            {"lifecycle_events": events, "outcomes": []},
            [decision]
        )
        self.assertIn(
            "targets_secp256k1_directly",
            state["candidates"][0]["gates"]
        )
        self.assertEqual([], state["recommended"])
        self.assertEqual([], state["authorized"])
        self.assertEqual([], state["route_promotions"])
        self.assertEqual([], state["direct_target_executions"])

    def test_target_scope_cannot_exceed_bounded_lane_ceiling(self) -> None:
        snapshot = candidate("OVERSIZED-TOY")
        snapshot["target_scope"]["field_bits"] = 32
        snapshot = bind_snapshot(snapshot)
        problems = validate_snapshot(snapshot, policy())
        self.assertTrue(
            any(
                "field_bits: exceeds bounded lane ceiling" in problem
                for problem in problems
            )
        )
        self.assertIn("invalid_candidate_snapshot", derive_gates(snapshot, policy()))

    def test_portfolio_overflow_is_explicit_coverage_artifact(self) -> None:
        entries = []
        for index in range(13):
            entries.append(
                {
                    "candidate_id": f"C{index:02d}",
                    "snapshot": {
                        "dependencies": [],
                        "correlation_groups": [],
                        "diversity_tags": [f"tag-{index}"]
                    },
                    "score": {
                        "eig_bits": {"low": 0.1, "base": 0.1, "high": 0.1}
                    },
                    "cost_vector": {
                        "compute_hours": 0,
                        "storage_gb": 0,
                        "money_usd": 0,
                        "implementation_hours": 0,
                        "reviewer_hours": 0,
                        "wall_time_hours": 0,
                        "peak_memory_gb": 0,
                        "workers": 1,
                        "shared_setup_id": None,
                        "shared_setup_hours": 0
                    }
                }
            )
        result = optimize_portfolio(entries, policy())
        self.assertEqual("coverage_overflow", result["status"])
        self.assertEqual(13, result["candidate_count"])
        self.assertEqual(8192, result["combination_count"])
        self.assertEqual([], result["selected_ids"])

    def test_historical_semantic_root_and_raw_bytes_are_both_pinned(self) -> None:
        records, reviewed_root, _ = historical_boundary()
        self.assertEqual(V0_REVIEWED_ROOT, reviewed_root)
        self.assertEqual(
            V0_RAW_FILE_SHA256,
            {
                record["event_id"]: record["raw_file_sha256"]
                for record in records
            },
        )


if __name__ == "__main__":
    unittest.main()
