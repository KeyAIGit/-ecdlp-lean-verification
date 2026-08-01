#!/usr/bin/env python3
"""Regression tests for Research Engine v0."""
from __future__ import annotations

import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gen_status import render_engine_queue_summary
from hypothesis_generation_lib import (
    GENERATION_POLICY_PATH,
    PROPOSAL_FIELDS,
    PROPOSALS_DIR,
    REVIEW_FIELDS,
    REVIEWS_DIR,
    build_generation_state,
    _frozen_seed_records,
    generate_seeds,
    git_file_sha256,
    mechanism_signature,
    premise_fingerprint,
    proposal_integrity_problems,
    proposal_sha256,
    sha256_json,
    validate_proposals,
)
from typed_evidence_lib import load_and_build as load_typed_evidence_state
from research_claims import load_and_build as load_research_claim_state
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
    content_sha256,
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
    validate_historical_scope_corrections,
    validate_historical_outcome_baseline,
    validate_external_bounded_sequence,
    validate_retrospective,
    effective_event_scope,
)
from scientific_provenance import (
    repository_text_sha256,
    scientific_source_commit_allowed,
    validation_problems as scientific_provenance_validation_problems,
)
from research_engine_v02 import mechanism_assurance_claims


class ResearchEngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy = load_json(POLICY_PATH)
        cls.generation_policy = load_json(GENERATION_POLICY_PATH)
        cls.decisions = load_json(DECISION_PATH)
        cls.hypotheses = parse_hypotheses()
        cls.outcomes = load_outcomes()
        root = POLICY_PATH.parents[1]
        validator_dir = root / "experiments" / "engine" / "validators"
        fixture_payload = (
            root
            / "experiments"
            / "framework"
            / "fixtures"
            / "pure_engine_validator.py"
        ).read_bytes()
        with tempfile.NamedTemporaryFile(
            prefix=".protocol-regression-",
            suffix=".py",
            dir=validator_dir,
            delete=False,
        ) as handle:
            handle.write(fixture_payload)
            cls.test_validator_path = Path(handle.name)
        cls.test_validator_relative = cls.test_validator_path.relative_to(
            root
        ).as_posix()
        cls.addClassCleanup(cls.test_validator_path.unlink, missing_ok=True)

    def test_repository_text_hash_is_checkout_eol_independent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            lf = root / "lf.txt"
            crlf = root / "crlf.txt"
            lf.write_bytes(b"first\nsecond\n")
            crlf.write_bytes(b"first\r\nsecond\r\n")
            self.assertEqual(
                repository_text_sha256(lf),
                repository_text_sha256(crlf),
            )

    def test_authorization_text_hash_is_checkout_eol_independent(self) -> None:
        self.assertEqual(
            content_sha256(b'{"status":"frozen"}\n'),
            content_sha256(b'{"status":"frozen"}\r\n'),
        )

    def generation_proposal(self, seed: dict, proposal_id: str) -> dict:
        premise = (
            "Character-graded syzygy sparsity persists after target tags and "
            "all relative GLV phases are retained in the relation ideal."
        )
        source_commit = "fed55d84675fd96e5f40204b9f5f49baa8c01172"
        evidence_inputs = seed["evidence_inputs"][:2]
        source_id = seed["route_source_ids"][0]
        proposal = {
            "schema_version": "0.1",
            "proposal_id": proposal_id,
            "seed_id": seed["seed_id"],
            "cell_id": seed["cell_id"],
            "typed_evidence_digest": seed["typed_evidence_digest"],
            "created_on": "2026-07-25",
            "proposer_id": "fixture-proposer",
            "route_id": seed["route_id"],
            "threat_model": seed["threat_model"],
            "title": "Digest-bound synthetic hypothesis-generation fixture",
            "hypothesis_statement": (
                "A faithful character-graded relation presentation reduces a "
                "preregistered decisive cost metric on increasing toy fields."
            ),
            "new_premise": premise,
            "premise_counterfactual": (
                "Without graded sparsity beyond the known diagonal symmetry, "
                "the presentation reduces to a faithful but cost-neutral "
                "re-encoding and must lose to the plain baseline."
            ),
            "premise_fingerprint": premise_fingerprint(premise),
            "mechanism_identity": {
                "transformation_class": "character-graded-target-ideal",
                "information_source_class": "explicit-j0-coordinate-action",
                "target_semantics_class": "single-target-tag-preserving",
                "recovery_class": "phase-tuple-point-sum-replay",
                "changed_cost_term": "validated-f4-nonzeros-per-relation",
                "precomputation_class": "fully-priced-target-independent",
                "amortization_class": "none-single-target",
            },
            "mechanism_signature": "",
            "mechanism_contract": {
                "source_objects": [
                    "fixed-target tagged Semaev toy relations"
                ],
                "target_objects": [
                    "recoverable character-graded relation records"
                ],
                "transformation": {
                    "kind": "character_graded_target_ideal",
                    "exact_map": (
                        "(relation, relative phases, target tag) maps to the "
                        "corresponding tagged character component"
                    ),
                    "domain": (
                        "complete fixed-target relation tuples with every "
                        "relative GLV phase retained"
                    ),
                    "codomain": (
                        "tagged character components carrying a reversible "
                        "phase tuple"
                    ),
                },
                "fixed_target_semantics": {
                    "target_slot": "the final relation coordinate",
                    "target_action": (
                        "the explicit target tag is preserved and replayed"
                    ),
                    "same_target_preserved": True,
                },
                "exceptional_locus": {
                    "definition": (
                        "zero coordinates, singular fibers, and failed "
                        "recovery components"
                    ),
                    "treatment": "separately_recovered",
                },
                "orbit_stabilizer": {
                    "acting_group": "diagonal C3 with retained relative phases",
                    "stabilizer": (
                        "the exact fixed-target stabilizer represented by tags"
                    ),
                    "orbit_size_law": (
                        "computed per registered toy size; no asymptotic "
                        "claim is inferred from group order"
                    ),
                },
                "relation_semantics": {
                    "source_relation": (
                        "the source tuple satisfies the fixed-target point sum"
                    ),
                    "target_relation": (
                        "the tagged component replays the same point sum"
                    ),
                    "equivalence_status": "specified_unproved",
                },
                "recovery_map": {
                    "forward": (
                        "retain relative phases and the target tag in the "
                        "character component"
                    ),
                    "inverse": (
                        "recover the phase tuple and replay independent "
                        "elliptic-curve arithmetic"
                    ),
                    "excluded_components": [
                        "singular fibers",
                        "failed target-tag recovery",
                    ],
                    "spurious_solution_policy": (
                        "reject every tuple whose recovered point sum fails"
                    ),
                },
                "implementation_identity": {
                    "implementation_path": (
                        "planned/hypothesis-generation-fixture-producer.py"
                    ),
                    "sha256": "4" * 64,
                },
                "cost_changing_mechanism": {
                    "quantity": (
                        "validated F4 nonzero matrix entries per relation"
                    ),
                    "causal_bridge": (
                        "character-graded sparsity reduces the registered "
                        "elimination matrix while exact phase recovery remains"
                    ),
                    "growth_law": (
                        "the matched ratio must improve over three increasing "
                        "toy field sizes"
                    ),
                    "non_orbit_lever": (
                        "graded syzygy sparsity rather than finite orbit size"
                    ),
                },
                "source_ids": [source_id],
            },
            "prediction_contract": {
                "metric": {
                    "name": "validated_f4_nonzeros_per_relation",
                    "unit": "matrix_nonzeros/relation",
                    "recomputation": (
                        "sum raw sparse-matrix entries and divide by "
                        "independently recovered relations"
                    ),
                },
                "matched_baseline": {
                    "baseline_id": "plain-semaev-matched-toy-baseline",
                    "implementation_digest": "5" * 64,
                    "matching_variables": [
                        "curve",
                        "field_bits",
                        "factor_base_size",
                        "seed",
                        "solver_version",
                    ],
                },
                "tested_sizes": [8, 12, 16],
                "expected_direction": "decrease",
                "minimum_material_effect": 0.1,
                "decision_threshold": {
                    "operator": "le",
                    "value": 0.9,
                },
                "stop_rule": {
                    "condition": (
                        "stop after all frozen sizes classify or after one "
                        "exact recovery failure"
                    ),
                    "maximum_instances": 9,
                },
                "falsifying_outcomes": [
                    "exact recovery fails",
                    "the matched cost ratio does not improve",
                ],
            },
            "cost_contract": {
                "online": {"cpu_hours": 3, "gpu_hours": 0},
                "offline": {"cpu_hours": 1, "gpu_hours": 0},
                "wall_time_hours": 4,
                "peak_memory_gb": 4,
                "storage_gb": 2,
                "workers": 1,
                "money_usd": 10,
                "implementation_hours": 8,
                "reviewer_hours": 2,
                "preprocessing": {
                    "included_in_totals": True,
                    "description": (
                        "Presentation construction and every reusable "
                        "decomposition are included."
                    ),
                },
                "amortization": {
                    "class": "none_single_target",
                    "target_count": 1,
                    "per_target_cost_included": True,
                },
                "success_probability": 0.25,
                "shared_setup": {
                    "setup_id": None,
                    "hours": 0,
                    "expected_reuse": 1,
                },
            },
            "validator_contract": {
                "status": "design_only_unverified",
                "raw_artifact_format": {
                    "media_type": "application/json",
                    "schema_id": "planned-glv-tagged-relation-artifacts-v1",
                },
                "recomputed_decisive_claim": {
                    "claim_id": "planned-tagged-cost-ratio",
                    "procedure": (
                        "recompute exact relation recovery and the cost ratio "
                        "from primitive raw artifacts"
                    ),
                },
                "implementation": {
                    "path": (
                        "planned/hypothesis-generation-fixture-validator.py"
                    ),
                    "sha256": "6" * 64,
                },
                "prohibited_producer_fields": [
                    "claimed_outcome",
                    "claimed_cost_ratio",
                ],
                "independence": {
                    "path_independent": False,
                    "artifact_independent": False,
                    "source_independent": False,
                    "producer_identity": "fixture-producer",
                    "validator_identity": "planned-fixture-validator",
                    "same_model": None,
                    "same_session": None,
                    "shared_context": None,
                },
                "independence_evidence": {
                    "path": {
                        "status": "planned",
                        "evidence_id": None,
                        "sha256": None,
                    },
                    "artifact": {
                        "status": "planned",
                        "evidence_id": None,
                        "sha256": None,
                    },
                    "source": {
                        "status": "planned",
                        "evidence_id": None,
                        "sha256": None,
                    },
                },
                "source_review_requirements": [
                    "one digest-bound human source-independence attestation"
                ],
            },
            "novelty_scope": {
                "new_to_repository": True,
                "new_to_reviewed_corpus": True,
                "global_novelty": "unverified",
                "rationale": (
                    "The exact tagged character presentation is absent from "
                    "the reviewed repository corpus; global novelty is not claimed."
                ),
            },
            "nearest_prior_art": [
                {
                    "source_id": source_id,
                    "primary": True,
                    "reference": "Repository GLV-Semaev obstruction baseline",
                    "locator": "README section on faithful quotient boundaries",
                    "overlap": (
                        "Both study the exact GLV action on fixed-target "
                        "Semaev relation systems."
                    ),
                    "difference": (
                        "The fixture retains target tags and relative phases "
                        "instead of quotienting every coordinate cube."
                    ),
                    "evidence_file": (
                        evidence_inputs[0]
                    ),
                }
            ],
            "exact_mechanism": {
                "map": (
                    "Map each relation into a character-graded component while "
                    "retaining an explicit diagonal-orbit tag."
                ),
                "domain": (
                    "The complete fixed-target Semaev relation ideal over a "
                    "cofactor-one toy j=0 curve."
                ),
                "codomain": (
                    "A tagged direct sum of character components with all "
                    "relative phases represented."
                ),
                "relation_semantics": (
                    "Membership represents exactly the same point-sum relation "
                    "as the source ideal."
                ),
                "fixed_target_semantics": (
                    "The target-orbit tag is transported explicitly and never "
                    "identified with the original fixed target."
                ),
                "exceptional_locus": (
                    "Zero coordinates, singular fibers, and failed recovery "
                    "components are enumerated and priced separately."
                ),
                "recovery_map": (
                    "Recover the source phase tuple and verify the point sum "
                    "using independent elliptic-curve arithmetic."
                ),
                "implementation_identity": (
                    "The producer emits canonical tagged generators and a "
                    "versioned transformation manifest."
                ),
            },
            "non_generic_information_source": (
                "The mechanism consumes explicit j=0 coordinate action and "
                "character grading, information absent from a generic oracle."
            ),
            "null_model": (
                "The same systems are solved after a bookkeeping-only tagged "
                "change of basis, so any observed difference is constant noise "
                "or implementation variance rather than mechanism evidence."
            ),
            "competing_mechanism": (
                "A matched sparse elimination ordering on the plain Semaev "
                "presentation may explain the same matrix reduction without "
                "using GLV character structure."
            ),
            "cost_bridge": {
                "baseline": (
                    "Matched plain Semaev relation generation on identical toy "
                    "curves, targets, seeds, and factor-base sizes."
                ),
                "changed_term": (
                    "Total nonzero F4 matrix entries per independently validated "
                    "recovered relation."
                ),
                "online_cost": (
                    "Count field operations for solving, recovery, rejection, "
                    "and target-tag verification."
                ),
                "offline_cost": (
                    "Charge presentation construction and every reusable "
                    "character decomposition."
                ),
                "memory_cost": (
                    "Record peak matrix storage and retained relation artifacts "
                    "for both presentations."
                ),
                "parallelism": (
                    "Use the same worker count and report aggregate as well as "
                    "critical-path work."
                ),
                "precomputation": (
                    "All target-independent and target-dependent preprocessing "
                    "is timed and included."
                ),
                "amortization_scope": (
                    "No multi-target amortization is credited in the plain "
                    "single-target comparison."
                ),
                "scaling_claim": (
                    "The decisive ratio must improve across three increasing "
                    "field sizes; one constant toy win is inconclusive."
                ),
            },
            "falsifiable_prediction": (
                "The tagged presentation lowers the decisive cost metric on "
                "each of three increasing preregistered toy sizes."
            ),
            "matched_baseline": (
                "The plain presentation uses the same curves, targets, seeds, "
                "factor-base sizes, solver version, and resource limits."
            ),
            "stop_condition": (
                "Stop and retain a bounded negative if any size loses exact "
                "recovery or the cost ratio fails to improve."
            ),
            "outcome_matrix": {
                "supported": (
                    "Every preregistered size preserves recovery and improves "
                    "the decisive ratio under the matched baseline."
                ),
                "falsified": (
                    "The exact transformation or fixed-target relation fails "
                    "on an independently checked instance."
                ),
                "bounded_negative": (
                    "The mechanism is exact but the decisive ratio does not "
                    "improve across the bounded size ladder."
                ),
                "inapplicable": (
                    "The required character decomposition is absent on a "
                    "preregistered curve family member."
                ),
                "inconclusive": (
                    "Measurements pass validation but do not separate the "
                    "mechanism from the matched baseline."
                ),
                "resource_exhausted": (
                    "The frozen resource budget ends before every decisive "
                    "instance receives a validated classification."
                ),
            },
            "validator_plan": {
                "decisive_claim": (
                    "Recompute recovered relations and the full decisive cost "
                    "ratio from raw producer artifacts."
                ),
                "raw_artifacts": (
                    "Canonical systems, target tags, solver traces, recovered "
                    "points, operation counts, and resource records."
                ),
                "independent_method": (
                    "Use separately authored point arithmetic and sparse-matrix "
                    "parsing without importing producer transformation code."
                ),
                "failure_labels": (
                    "Classify exact failure as falsified, bounded_negative, "
                    "inconclusive, inapplicable, or resource_exhausted."
                ),
            },
            "toy_scope": {
                "curve_family": "cofactor-one toy j=0 curves",
                "max_field_bits": 20,
                "forbidden_targets": ["secp256k1"],
            },
            "claim_boundary": (
                "This toy structural test does not establish an asymptotic "
                "speedup, an exact-target algorithm, or a secp256k1 break."
            ),
            "evidence_inputs": evidence_inputs,
            "evidence_manifest": [
                {
                    "path": path,
                    "sha256": git_file_sha256(source_commit, path),
                    "relation": "bounds" if index == 0 else "supports",
                    "locator": (
                        "Repository-pinned route evidence used by the synthetic "
                        "generation regression fixture."
                    ),
                    "source_id": source_id,
                    "primary": index == 0,
                }
                for index, path in enumerate(evidence_inputs)
            ],
            "provenance": {
                "generation_method": "model_assisted",
                "generator": "synthetic-regression-fixture",
                "generator_family": "codex-fixture",
                "generator_version": "v0",
                "session_id": f"proposal-session-{proposal_id}",
                "context_sha256": "a" * 64,
                "source_commit": source_commit,
                "prompt_sha256": "0" * 64,
            },
        }
        mechanism = proposal["mechanism_contract"]
        mechanism["relation_semantics"][
            "equivalence_status"
        ] = "certificate_replayed"
        claims = mechanism_assurance_claims(mechanism)
        mechanism["assurance_bindings"] = {
            "relation_equivalence": {
                "assurance": "certificate_replayed",
                "evidence_id": "ME-FIXTURE-RELATION",
                "claim_sha256": claims["relation_equivalence"],
            },
            "exceptional_locus": {
                "assurance": "certificate_replayed",
                "evidence_id": "ME-FIXTURE-EXCEPTIONAL",
                "claim_sha256": claims["exceptional_locus"],
            },
            "recovery_map": {
                "assurance": "independent_reproduction",
                "evidence_id": "ME-FIXTURE-RECOVERY",
                "claim_sha256": claims["recovery_map"],
            },
            "cost_changing_bridge": {
                "assurance": "independent_reproduction",
                "evidence_id": "ME-FIXTURE-COST",
                "claim_sha256": claims["cost_changing_bridge"],
            },
        }
        proposal["mechanism_signature"] = mechanism_signature(proposal)
        return proposal

    def generation_policy_with_assurance(
        self, proposal: dict
    ) -> dict:
        policy = copy.deepcopy(self.generation_policy)
        bindings = proposal["mechanism_contract"]["assurance_bindings"]
        policy["mechanism_assurance_evidence"] = [
            {
                "evidence_id": item["evidence_id"],
                "topic": topic,
                "assurance": item["assurance"],
                "claim_sha256": item["claim_sha256"],
            }
            for topic, item in bindings.items()
        ]
        return policy

    def test_deleted_pre_squash_source_commit_is_not_reproducible(self) -> None:
        with tempfile.TemporaryDirectory(prefix="engine-provenance-") as tmp:
            root = Path(tmp)

            def git(*args: str) -> str:
                result = subprocess.run(
                    ["git", *args],
                    cwd=root,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                return result.stdout.strip()

            git("init", "-q", "-b", "main")
            git("config", "user.name", "Research Engine Test")
            git("config", "user.email", "engine-test@example.invalid")
            (root / "fixture.txt").write_text("baseline\n", encoding="utf-8")
            git("add", "fixture.txt")
            git("commit", "-q", "-m", "baseline")
            git("switch", "-q", "-c", "source-branch")
            (root / "fixture.txt").write_text("proposal\n", encoding="utf-8")
            git("commit", "-q", "-am", "branch-only source")
            branch_only = git("rev-parse", "HEAD")
            git("switch", "-q", "main")
            (root / "fixture.txt").write_text("proposal\n", encoding="utf-8")
            git("commit", "-q", "-am", "squash merge")
            protected_main = git("rev-parse", "HEAD")
            git("branch", "-D", "source-branch")
            self.assertEqual(
                0,
                subprocess.run(
                    ["git", "cat-file", "-e", f"{branch_only}^{{commit}}"],
                    cwd=root,
                    check=False,
                ).returncode,
            )
            policy = {
                "schema_version": "0.1",
                "protected_main": {
                    "recorded_ref": "refs/heads/main",
                    "commit": protected_main,
                    "recorded_on": "2026-07-25",
                },
                "immutable_evidence_refs": [],
            }
            self.assertFalse(
                scientific_source_commit_allowed(
                    branch_only, policy, root=root
                )
            )
            self.assertTrue(
                scientific_source_commit_allowed(
                    protected_main, policy, root=root
                )
            )

            bad_policy = {
                **policy,
                "protected_main": {
                    **policy["protected_main"],
                    "recorded_ref": "main",
                },
            }
            self.assertTrue(
                any(
                    "protected_main recorded_ref must be a ref name"
                    in problem
                    for problem in scientific_provenance_validation_problems(
                        bad_policy, root=root
                    )
                )
            )
            self.assertTrue(
                scientific_source_commit_allowed(
                    protected_main, bad_policy, root=root
                )
            )

    def test_materialized_proposal_integrity_bindings_reject_mutations(self) -> None:
        proposal_path = (
            PROPOSALS_DIR / "HGP-M16-SOLVER-SLOPE-001.json"
        )
        proposal = json.loads(proposal_path.read_text(encoding="utf-8"))
        self.assertEqual([], proposal_integrity_problems(proposal))

        mutations = []
        for path in (
            ("mechanism_contract", "implementation_identity", "sha256"),
            ("validator_contract", "implementation", "sha256"),
            ("prediction_contract", "matched_baseline", "implementation_digest"),
            ("provenance", "context_sha256"),
            ("provenance", "prompt_sha256"),
        ):
            changed = copy.deepcopy(proposal)
            target = changed
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = "0" * 64
            mutations.append(changed)

        for changed in mutations:
            self.assertTrue(proposal_integrity_problems(changed))

    def generation_reviews(self, proposal: dict) -> list[tuple[Path, dict]]:
        roles = self.generation_policy["quality_gate"][
            "required_review_roles"
        ]
        digest = proposal_sha256(proposal)
        records = []
        review_prefix = proposal["proposal_id"].removeprefix("HGP-")
        for index, role in enumerate(roles, start=1):
            records.append(
                (
                    REVIEWS_DIR / f"HGR-{review_prefix}-{index}.json",
                    {
                        "schema_version": "0.1",
                        "review_id": f"HGR-{review_prefix}-{index}",
                        "proposal_id": proposal["proposal_id"],
                        "proposal_sha256": digest,
                        "reviewed_on": "2026-07-25",
                        "reviewer_id": f"fixture-reviewer-{index}",
                        "reviewer_role": role,
                        "source_independence": (
                            "declared_independent"
                            if role
                            in self.generation_policy["quality_gate"][
                                "required_independent_roles"
                            ]
                            else "shared_context"
                        ),
                        "reviewer_provenance": {
                            "family": (
                                "external-review-fixture"
                                if role
                                in self.generation_policy["quality_gate"][
                                    "required_independent_roles"
                                ]
                                else (
                                    "internal-review-fixture-a"
                                    if index % 2
                                    else "internal-review-fixture-b"
                                )
                            ),
                            "version": "v0",
                            "session_id": (
                                f"review-session-{proposal['proposal_id']}-{index}"
                            ),
                            "context_sha256": f"{index + 5:x}" * 64,
                            "prompt_sha256": f"{index}" * 64,
                            "blind_to_other_reviews": True,
                        },
                        "verdict": "pass",
                        "blocker_codes": [],
                        "summary": (
                            "Synthetic review confirms the fixture contains "
                            "every field required for deterministic gate tests."
                        ),
                        "evidence_inputs": [
                            "experiments/glv_diagonal_obstruction/README.md"
                        ],
                    },
                )
            )
        return records

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
                "field_bits": sorted(
                    {
                        curve["field_p"].bit_length()
                        for curve in candidate["preregistration"]["curves"]
                    }
                ),
                "threat_model": candidate["scope"]["threat_model"],
                "claim_boundary": "Synthetic regression fixture only.",
            },
            "summary": "Synthetic native event for a deterministic gate fixture.",
            "evidence_files": ["experiments/p3_sm_system/RESULTS.md"],
            "validation": {
                "status": "passed",
                "independence": {
                    "path": "verified_distinct",
                    "artifact": "raw_recomputed",
                    "source": "reviewed_independent",
                    "source_review_id": "synthetic-regression-review",
                },
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
        fixture_contract = {
            "status": "implemented",
            "protocol": VALIDATOR_PROTOCOL,
            "entrypoint": self.test_validator_relative,
            "entrypoint_sha256": file_sha256(self.test_validator_path),
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
        fixture_preregistration = {
            "status": "frozen",
            "solver": {
                "name": "Synthetic protocol solver",
                "versions": {
                    "SageMath": "10.6",
                    "Singular": "4.4.1",
                },
                "algorithm": "Deterministic regression fixture only",
            },
            "seeds": [1],
            "curves": [
                {
                    "id": "toy-j0-16-p65539-b11",
                    "field_p": 65539,
                    "curve_a": 0,
                    "curve_b": 11,
                    "base_order": 65287,
                    "base_point": [7825, 6727],
                    "cofactor": 1,
                }
            ],
            "instances": [
                {
                    "curve_id": "toy-j0-16-p65539-b11",
                    "m": 2,
                    "factor_base_sizes": [4],
                    "presentations": ["plain"],
                }
            ],
            "target_rule": "Use the frozen synthetic fixture target.",
            "primary_metric": "Exact canonical fixture outcome.",
            "validator_contract": fixture_contract,
            "success_rule": "The pure protocol fixture returns its frozen outcome.",
            "stop_rule": "Stop after the one frozen fixture instance.",
        }
        fixture_information_model = {
            "latent_question": "Does the synthetic protocol fixture pass?",
            "prior_live": 0.5,
            "prior_rationale": "Synthetic distribution for gate tests only.",
            "likelihoods": {
                "proved": {"live": 0.0, "dead": 0.0},
                "supported": {"live": 0.55, "dead": 0.05},
                "falsified": {"live": 0.05, "dead": 0.45},
                "bounded_negative": {"live": 0.1, "dead": 0.25},
                "inapplicable": {"live": 0.05, "dead": 0.05},
                "inconclusive": {"live": 0.15, "dead": 0.15},
                "resource_exhausted": {"live": 0.1, "dead": 0.05},
            },
        }
        fixture_result_updates = {
            outcome: "Synthetic protocol update only."
            for outcome in (
                "proved",
                "supported",
                "falsified",
                "bounded_negative",
                "inapplicable",
                "inconclusive",
                "resource_exhausted",
            )
        }
        for index, candidate in enumerate(policy["candidate_proposals"][:3]):
            candidate["authorization"] = "exploration"
            candidate["preregistration"] = copy.deepcopy(
                fixture_preregistration
            )
            candidate["information_model"] = copy.deepcopy(
                fixture_information_model
            )
            candidate["result_updates"] = copy.deepcopy(
                fixture_result_updates
            )
            candidate["scope"] = {
                "curve_family": "cofactor-1 toy j=0 curves",
                "max_field_bits": 21,
                "forbidden_targets": ["secp256k1"],
                "threat_model": "classical-single-target-plain",
            }
            candidate["hard_rejections"] = {
                key: False for key in candidate["hard_rejections"]
            }
            if index == 0:
                candidate["downstream_research_window"] = (
                    "RE0-002-NONREDUNDANT-INVARIANT-QUOTIENT"
                )
                candidate["dependencies"] = []
                candidate["dependency_requirements"] = {}
            elif index == 1:
                candidate["gap_class"] = "mechanism_bearing_open_window"
                candidate["dependencies"] = [
                    "RE0-001-EXTERNAL-SOLVER-CALIBRATION"
                ]
                candidate["dependency_requirements"] = {
                    "RE0-001-EXTERNAL-SOLVER-CALIBRATION": ["supported"]
                }
            else:
                candidate["gap_class"] = "mechanism_bearing_open_window"
                candidate["dependencies"] = [
                    "RE0-001-EXTERNAL-SOLVER-CALIBRATION",
                    "RE0-002-NONREDUNDANT-INVARIANT-QUOTIENT",
                ]
                candidate["dependency_requirements"] = {
                    "RE0-001-EXTERNAL-SOLVER-CALIBRATION": ["supported"],
                    "RE0-002-NONREDUNDANT-INVARIANT-QUOTIENT": ["supported"],
                }
        return policy

    def test_policy_covers_all_ten_hypotheses(self) -> None:
        self.assertEqual(
            [],
            validate_policy(self.policy, self.decisions, self.hypotheses),
        )
        self.assertEqual(10, len(self.policy["hypothesis_normalization"]))

    def test_external_singleton_is_not_a_native_engine_candidate(self) -> None:
        hypothesis_id = "HYP-M16-FIXED-TARGET-YIELD-001"
        self.assertIn(hypothesis_id, self.hypotheses)
        normalized = next(
            item
            for item in self.policy["hypothesis_normalization"]
            if item["id"] == hypothesis_id
        )
        self.assertEqual(
            "external_bounded_terminal_not_native_candidate",
            normalized["engine_state"],
        )
        self.assertEqual("supported", normalized["normalized_outcome"])
        self.assertEqual(
            ["R-PETIT-COMPOSED-MAPS"],
            normalized["route_ids"],
        )
        self.assertFalse(
            any(
                candidate["hypothesis_id"] == hypothesis_id
                for candidate in self.policy["candidate_proposals"]
            )
        )
        self.assertEqual(
            0,
            sum(
                candidate["authorization"] == "intake"
                for candidate in self.policy["candidate_proposals"]
            ),
        )
        self.assertEqual(
            0,
            sum(
                candidate["authorization"] == "exploration"
                for candidate in self.policy["candidate_proposals"]
            ),
        )
        self.assertEqual(
            24,
            self.policy["gates"]["exploration"]["limits"]["max_field_bits"],
        )
        selection = select_candidates(self.policy)
        self.assertEqual([], selection["selected_sequence"])

        policy = copy.deepcopy(self.policy)
        external = next(
            item
            for item in policy["hypothesis_normalization"]
            if item["id"] == hypothesis_id
        )
        external["normalized_outcome"] = "bounded_negative"
        problems = validate_policy(policy, self.decisions, self.hypotheses)
        self.assertIn(
            f"{hypothesis_id}: consumed external singleton outcome must "
            "match its terminal authorization",
            problems,
        )

    def test_external_bounded_outcome_is_exactly_authorization_bound(self) -> None:
        path, event = next(
            item
            for item in self.outcomes
            if item[1].get("provenance", {}).get("source_kind")
            == "external_bounded_decision_run"
        )
        self.assertEqual("supported", event["outcome"])
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

        wrong_identity = copy.deepcopy(event)
        wrong_identity["hypothesis_id"] = "HYP_GLV_SEMAEV_001"
        problems = validate_outcome(
            path,
            wrong_identity,
            self.policy,
            self.decisions,
            self.hypotheses,
        )
        self.assertTrue(
            any("hypothesis_id differs from bounded authorization" in item
                for item in problems),
            msg=problems,
        )

        wrong_manifest = copy.deepcopy(event)
        wrong_manifest["provenance"]["run_manifest_sha256"] = "0" * 64
        problems = validate_outcome(
            path,
            wrong_manifest,
            self.policy,
            self.decisions,
            self.hypotheses,
        )
        self.assertTrue(
            any("run_manifest_sha256 mismatch" in item for item in problems),
            msg=problems,
        )

        wrong_bindings = copy.deepcopy(self.decisions)
        wrong_bindings["bounded_experiment_authorization"][
            "sha256_bindings"
        ]["run_py"] = "0" * 64
        problems = validate_outcome(
            path,
            event,
            self.policy,
            wrong_bindings,
            self.hypotheses,
        )
        self.assertTrue(
            any("run_manifest bindings differ from authorization" in item
                for item in problems),
            msg=problems,
        )

        with patch(
            "research_engine_lib.git_commit_exists",
            return_value=False,
        ):
            problems = validate_outcome(
                path,
                event,
                self.policy,
                self.decisions,
                self.hypotheses,
            )
        self.assertTrue(
            any("source_commit is not reproducible" in item for item in problems),
            msg=problems,
        )

    def test_external_bounded_outcome_is_scope_budget_and_stop_bound(self) -> None:
        path, source_event = next(
            item
            for item in self.outcomes
            if item[1].get("provenance", {}).get("source_kind")
            == "external_bounded_decision_run"
        )
        cases = [
            (
                "field_bits",
                lambda event: event["scope"].update({"field_bits": [19]}),
                "field_bits differ from authorized curve table",
            ),
            (
                "target_kind",
                lambda event: event["scope"].update(
                    {"target_kind": "operational"}
                ),
                "must have toy target_kind",
            ),
            (
                "wall_budget",
                lambda event: event["budget"].update(
                    {"wall_time_seconds": 25 * 3600}
                ),
                "exceeds wall-time budget",
            ),
            (
                "stop",
                lambda event: event["stop_condition"].update(
                    {"triggered": False}
                ),
                "must consume its stop condition",
            ),
        ]
        for name, mutate, expected in cases:
            with self.subTest(name=name):
                event = copy.deepcopy(source_event)
                mutate(event)
                problems = validate_outcome(
                    path,
                    event,
                    self.policy,
                    self.decisions,
                    self.hypotheses,
                )
                self.assertTrue(
                    any(expected in item for item in problems),
                    msg=problems,
                )

    def test_external_bounded_outcome_is_not_native_or_calibrated(self) -> None:
        state = build_state(
            self.policy,
            self.decisions,
            self.hypotheses,
            self.outcomes,
        )
        event = state["external_bounded_outcomes"][0]
        self.assertEqual(
            "external_bounded_decision_run",
            event["source_kind"],
        )
        self.assertEqual([], state["native_outcomes"])
        self.assertEqual(0, state["calibration"]["scored_native_outcomes"])
        self.assertEqual(
            1,
            state["calibration"]["external_bounded_outcomes_excluded"],
        )
        self.assertIn(
            "not native selected Engine candidates",
            state["calibration"]["note"],
        )
        self.assertEqual(
            1,
            state["counts"]["outcomes_by_source"][
                "external_bounded_decision_run"
            ],
        )
        self.assertEqual(
            "external_bounded_result_retained",
            event["decision_delta"]["effect"],
        )
        route = next(
            item
            for item in state["route_evidence_state"]
            if item["route_id"] == event["route_id"]
        )
        self.assertEqual([], route["route_review_trigger_event_ids"])
        self.assertFalse(state["gate_status"]["promotion_authorized"])

    def test_external_bounded_authorization_is_single_use(self) -> None:
        path, event = next(
            item
            for item in self.outcomes
            if item[1].get("provenance", {}).get("source_kind")
            == "external_bounded_decision_run"
        )
        duplicate = copy.deepcopy(event)
        duplicate["event_id"] = "REO-2026-07-31-002"
        duplicate["recorded_on"] = "2026-07-31"
        problems = validate_external_bounded_sequence(
            self.decisions,
            [
                (path, event),
                (Path("REO-2026-07-31-002.json"), duplicate),
            ],
        )
        self.assertTrue(
            any("singleton authorization is already consumed" in item
                for item in problems),
            msg=problems,
        )

    def test_hypothesis_parser_accepts_hyphenated_ids(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            registry = Path(directory) / "HYPOTHESES.yaml"
            registry.write_text(
                "hypotheses:\n"
                "  - id: HYP-ONE-001\n"
                "    title: \"First\"\n"
                "    direction: \"experiment\"\n"
                "    status: \"active\"\n"
                "  - id: HYP_TWO_002\n"
                "    title: \"Second\"\n"
                "    direction: \"formalization\"\n"
                "    status: \"parked\"\n",
                encoding="utf-8",
            )
            parsed = parse_hypotheses(registry)
        self.assertEqual(
            {"HYP-ONE-001", "HYP_TWO_002"},
            set(parsed),
        )
        self.assertEqual("active", parsed["HYP-ONE-001"]["status"])

    def test_legacy_candidate_gates_cannot_be_self_cleared(self) -> None:
        policy = copy.deepcopy(self.policy)
        candidate = policy["candidate_proposals"][0]
        candidate["hard_rejections"] = {
            key: False for key in candidate["hard_rejections"]
        }
        policy["candidate_intake_contract"][
            "legacy_candidate_set_sha256"
        ] = sha256_json(policy["candidate_proposals"])
        problems = validate_policy(policy, self.decisions, self.hypotheses)
        self.assertTrue(
            any("reviewed code anchor" in item for item in problems),
            msg=problems,
        )
        self.assertTrue(
            any("typed proposal compiler" in item for item in problems),
            msg=problems,
        )

    def test_selector_selects_nothing_before_scientific_gates_clear(self) -> None:
        selection = select_candidates(self.policy)
        self.assertEqual([], selection["selected_sequence"])
        rejected = {
            item["candidate_id"]: set(item["reasons"])
            for item in selection["hard_rejected"]
        }
        self.assertEqual(
            {
                "missing_independent_validator",
                "no_new_premise_after_resolution",
            },
            rejected["RE0-001-EXTERNAL-SOLVER-CALIBRATION"],
        )
        self.assertEqual(
            {
                "missing_independent_validator",
                "no_new_premise_after_resolution",
            },
            rejected["RE0-002-NONREDUNDANT-INVARIANT-QUOTIENT"],
        )
        self.assertEqual(
            {
                "missing_independent_validator",
                "no_new_premise_after_resolution",
            },
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

    def test_framework_fixture_cannot_clear_scientific_validator_gate(self) -> None:
        policy = self.executable_policy()
        candidate = policy["candidate_proposals"][0]
        fixture_relative = (
            "experiments/framework/fixtures/pure_engine_validator.py"
        )
        fixture_path = POLICY_PATH.parents[1] / fixture_relative
        validator = candidate["preregistration"]["validator_contract"]
        validator["entrypoint"] = fixture_relative
        validator["entrypoint_sha256"] = file_sha256(fixture_path)

        problems = validate_policy(
            policy,
            self.decisions,
            self.hypotheses,
        )
        self.assertTrue(
            any(
                "framework fixtures are never scientific validators" in item
                for item in problems
            ),
            msg=problems,
        )
        rejected = {
            item["candidate_id"]: set(item["reasons"])
            for item in select_candidates(policy)["hard_rejected"]
        }
        self.assertIn(
            "missing_independent_validator",
            rejected[candidate["id"]],
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
        self.assertEqual(9, state["counts"]["outcome_events"])
        self.assertEqual(
            1, state["counts"]["outcomes_by_taxonomy"]["resource_exhausted"]
        )
        self.assertEqual(1, state["counts"]["outcomes_by_taxonomy"]["inapplicable"])
        self.assertEqual(1, state["counts"]["outcomes_by_taxonomy"]["supported"])
        self.assertEqual(
            1,
            state["counts"]["outcomes_by_taxonomy"][
                "historical_structural_confirmation"
            ],
        )
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
            "historical_structural_confirmation_retained",
            ward["evidence_axis"]["engine_disposition"],
        )

    def test_historical_supported_is_rejected(self) -> None:
        path, source_event = next(
            item
            for item in self.outcomes
            if item[1]["event_id"] == "REO-2026-07-24-004"
        )
        event = copy.deepcopy(source_event)
        event["outcome"] = "supported"
        problems = validate_outcome(
            path,
            event,
            self.policy,
            self.decisions,
            self.hypotheses,
        )
        self.assertTrue(
            any("supported is reserved for preregistered native runs" in item
                for item in problems),
            msg=problems,
        )

    def test_004_is_structural_confirmation_not_attack_evidence(self) -> None:
        event = next(
            event
            for _, event in self.outcomes
            if event["event_id"] == "REO-2026-07-24-004"
        )
        self.assertEqual(
            "historical_structural_confirmation",
            event["outcome"],
        )
        self.assertIn("known torsion identity", event["summary"])
        self.assertIn("no attack mechanism", event["summary"])

        state = build_state(
            self.policy, self.decisions, self.hypotheses, self.outcomes
        )
        ward = next(
            route
            for route in state["route_evidence_state"]
            if route["route_id"] == "R-EDS-DIVISION-POLYNOMIAL"
        )
        self.assertEqual([], ward["route_review_trigger_event_ids"])
        self.assertEqual(
            "historical_structural_confirmation_retained",
            ward["evidence_axis"]["engine_disposition"],
        )
        self.assertEqual(0, state["calibration"]["scored_native_outcomes"])

    def test_native_supported_requires_reviewed_source_independence(self) -> None:
        policy = self.executable_policy()
        event = self.native_event(
            0,
            "REO-2026-07-25-001",
            "supported",
            policy,
        )
        event["validation"]["independence"]["source"] = "shared_components"
        event["validation"]["independence"]["source_review_id"] = None
        problems = validate_outcome(
            Path(f"{event['event_id']}.json"),
            event,
            policy,
            self.decisions,
            self.hypotheses,
        )
        self.assertTrue(
            any("requires reviewed source independence" in item
                for item in problems),
            msg=problems,
        )

    def test_native_source_review_id_must_resolve(self) -> None:
        policy = self.executable_policy()
        event = self.native_event(
            0,
            "REO-2026-07-25-001",
            "supported",
            policy,
        )
        problems = validate_outcome(
            Path(f"{event['event_id']}.json"),
            event,
            policy,
            self.decisions,
            self.hypotheses,
            source_reviews={},
        )
        self.assertTrue(
            any("source_review_id does not resolve" in item for item in problems),
            msg=problems,
        )

    def test_007_is_mechanically_forced_to_inconclusive(self) -> None:
        path, source_event = next(
            item
            for item in self.outcomes
            if item[1]["event_id"] == "REO-2026-07-24-007"
        )
        self.assertEqual(
            [],
            validate_outcome(
                path,
                source_event,
                self.policy,
                self.decisions,
                self.hypotheses,
            ),
        )
        for alternate in (
            "proved",
            "supported",
            "historical_structural_confirmation",
            "falsified",
            "bounded_negative",
            "inapplicable",
            "resource_exhausted",
        ):
            with self.subTest(alternate=alternate):
                event = copy.deepcopy(source_event)
                event["outcome"] = alternate
                problems = validate_outcome(
                    path,
                    event,
                    self.policy,
                    self.decisions,
                    self.hypotheses,
                )
                self.assertNotEqual([], problems)

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

    def test_p3_m3_scope_correction_preserves_event_bytes(self) -> None:
        outcomes = [event for _, event in self.outcomes]
        self.assertEqual(
            [], validate_historical_scope_corrections(self.policy, outcomes)
        )
        event = next(
            item for item in outcomes if item["event_id"] == "REO-2026-07-24-006"
        )
        self.assertEqual(event["scope"]["field_bits"], [16, 20])
        effective, correction_id = effective_event_scope(self.policy, event)
        self.assertEqual(effective["field_bits"], [16])
        self.assertEqual(correction_id, "HSCORR-2026-08-01-P3-M3-BITS")

    def test_p3_m3_scope_correction_is_machine_checked(self) -> None:
        policy = copy.deepcopy(self.policy)
        correction = policy["historical_scope_corrections"][0]
        correction["effective_field_bits"] = [16, 20]
        correction["excluded_field_bits"] = [20]
        problems = validate_historical_scope_corrections(
            policy, [event for _, event in self.outcomes]
        )
        self.assertTrue(
            any("effective and excluded" in item for item in problems),
            msg=problems,
        )
        self.assertTrue(
            any("planned machine-check rows imply [16]" in item for item in problems),
            msg=problems,
        )

    def test_p3_m3_scope_correction_uses_actual_measurements(self) -> None:
        policy = copy.deepcopy(self.policy)
        correction = policy["historical_scope_corrections"][0]
        source_path = POLICY_PATH.parent.parent / correction["machine_check"]["path"]
        manifest = json.loads(source_path.read_text(encoding="utf-8"))
        injected = copy.deepcopy(manifest["results"]["measurements"][0])
        injected["m"] = 3
        injected["bits"] = 20
        manifest["results"]["measurements"].append(injected)
        with tempfile.TemporaryDirectory(
            prefix=".p3-scope-fault-", dir=POLICY_PATH.parent.parent
        ) as raw:
            path = Path(raw) / "manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            correction["machine_check"]["path"] = str(
                path.relative_to(POLICY_PATH.parent.parent)
            ).replace("\\", "/")
            correction["machine_check"]["sha256"] = file_sha256(path)
            problems = validate_historical_scope_corrections(
                policy, [event for _, event in self.outcomes]
            )
        self.assertTrue(
            any("actual measurements imply [16, 20]" in item for item in problems),
            msg=problems,
        )

    def test_scope_corrections_allow_only_one_overlay_per_event(self) -> None:
        policy = copy.deepcopy(self.policy)
        duplicate = copy.deepcopy(policy["historical_scope_corrections"][0])
        duplicate["correction_id"] += "-DUP"
        policy["historical_scope_corrections"].append(duplicate)
        problems = validate_policy(policy, self.decisions, self.hypotheses)
        self.assertTrue(
            any("at most one overlay per event" in item for item in problems),
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

    def test_coordinated_metadata_relabel_cannot_move_reviewed_baseline(self) -> None:
        policy = copy.deepcopy(self.policy)
        outcomes = [copy.deepcopy(event) for _, event in self.outcomes]
        event = next(
            item
            for item in outcomes
            if item["event_id"] == "REO-2026-07-24-002"
        )
        event["outcome"] = "inconclusive"
        baseline = next(
            item
            for item in policy["historical_outcome_baseline"]["events"]
            if item["event_id"] == event["event_id"]
        )
        baseline["event_sha256"] = sha256_json(event)

        problems = validate_historical_outcome_baseline(policy, outcomes)
        self.assertTrue(
            any("reviewed v0 root changed" in item for item in problems),
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
        model = self.executable_policy()["candidate_proposals"][0][
            "information_model"
        ]
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
        policy = self.executable_policy()
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
        owner_decisions = copy.deepcopy(self.decisions)
        owner_decisions["execution_gates"]["exploration"][
            "authorized"
        ] = True
        owner_decisions["phase_policy"][
            "bounded_exploration_authorized"
        ] = True
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
                    owner_decisions,
                    self.hypotheses,
                ),
            )
            without_commit_anchor = validate_native_sequence(
                policy,
                owner_decisions,
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
                        owner_decisions,
                        [(Path("REO-2026-07-25-001.json"), calibration)],
                    ),
                )
                relabelled = copy.deepcopy(calibration)
                relabelled["outcome"] = "bounded_negative"
                relabelled_problems = validate_native_sequence(
                    policy,
                    owner_decisions,
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

    def test_hypothesis_generator_builds_typed_non_executable_seeds(self) -> None:
        seeds = generate_seeds(
            self.generation_policy, self.decisions, self.policy
        )
        self.assertEqual(2, len(seeds))
        self.assertEqual(
            {
                "R-PETIT-COMPOSED-MAPS",
            },
            {seed["route_id"] for seed in seeds},
        )
        self.assertTrue(
            all(seed["authorization"] == "none" for seed in seeds)
        )
        self.assertEqual(
            {
                "desk_cost_bridge_required",
                "property_resolution_required",
            },
            {seed["status"] for seed in seeds},
        )
        self.assertTrue(all(seed["cell_id"].startswith("CELL-") for seed in seeds))
        m16 = next(
            seed
            for seed in seeds
            if seed["cell_id"] == "CELL-M-PKC-SMOOTH-M16"
        )
        instruction = m16["proposal_packet"]["instruction"]
        self.assertIn("complete desk bridge is unresolved", instruction)
        self.assertNotIn("desk quantity is missing", instruction)

    def test_hypothesis_seed_generation_is_order_independent(self) -> None:
        reordered = copy.deepcopy(self.generation_policy)
        for axis in reordered["axes"].values():
            axis.reverse()
        expected = generate_seeds(
            self.generation_policy, self.decisions, self.policy
        )
        observed = generate_seeds(reordered, self.decisions, self.policy)
        self.assertEqual(expected, observed)

    def test_unrelated_claim_change_preserves_scoped_seed_identity(self) -> None:
        claim_problems, claim_state = load_research_claim_state()
        self.assertEqual([], claim_problems)
        expected = generate_seeds(
            self.generation_policy,
            self.decisions,
            self.policy,
            claim_state=claim_state,
        )
        changed = copy.deepcopy(claim_state)
        changed["claims"][0]["statement"] += " Changed canonical fixture."
        observed = generate_seeds(
            self.generation_policy,
            self.decisions,
            self.policy,
            claim_state=changed,
        )
        self.assertEqual(
            [seed["seed_id"] for seed in expected],
            [seed["seed_id"] for seed in observed],
        )
        self.assertNotEqual(
            [seed["claim_state_digest"] for seed in expected],
            [seed["claim_state_digest"] for seed in observed],
        )

    def test_scoped_cell_change_invalidates_only_that_seed_identity(self) -> None:
        typed_problems, typed_state = load_typed_evidence_state()
        self.assertEqual([], typed_problems)
        expected = generate_seeds(
            self.generation_policy,
            self.decisions,
            self.policy,
            typed_evidence_state=typed_state,
        )
        changed = copy.deepcopy(typed_state)
        target = next(
            item
            for item in changed["cells"]
            if item["cell_id"] == "CELL-M-PKC-SMOOTH-M16"
        )
        target["evidence_digest"] = "f" * 64
        observed = generate_seeds(
            self.generation_policy,
            self.decisions,
            self.policy,
            typed_evidence_state=changed,
        )
        expected_ids = {item["cell_id"]: item["seed_id"] for item in expected}
        observed_ids = {item["cell_id"]: item["seed_id"] for item in observed}
        self.assertNotEqual(
            expected_ids["CELL-M-PKC-SMOOTH-M16"],
            observed_ids["CELL-M-PKC-SMOOTH-M16"],
        )
        self.assertEqual(
            expected_ids["CELL-M-PKC-AUXILIARY-CURVE"],
            observed_ids["CELL-M-PKC-AUXILIARY-CURVE"],
        )

    def test_frozen_seed_alias_is_historical_after_scoped_evidence_change(
        self,
    ) -> None:
        proposal = load_json(
            PROPOSALS_DIR / "HGP-M16-SOLVER-SLOPE-001.json"
        )
        records = [
            (PROPOSALS_DIR / "HGP-M16-SOLVER-SLOPE-001.json", proposal)
        ]
        problems, state = build_generation_state(
            self.generation_policy,
            self.decisions,
            self.policy,
            records,
            [],
        )
        self.assertEqual([], problems)
        intake = state["proposal_intake"][0]
        self.assertEqual("frozen_historical_only", intake["seed_resolution"])
        self.assertIn("stale_seed_snapshot", intake["blockers"])
        self.assertEqual("hard_rejected", intake["disposition"])
        self.assertEqual(
            "provenance_only_not_seed_identity",
            state["seed_lifecycle"]["claim_state_digest_role"],
        )

    def test_frozen_alias_can_resolve_only_for_exact_scoped_snapshot(self) -> None:
        proposal = load_json(
            PROPOSALS_DIR / "HGP-M16-SOLVER-SLOPE-001.json"
        )
        records = [
            (PROPOSALS_DIR / "HGP-M16-SOLVER-SLOPE-001.json", proposal)
        ]
        frozen_problems: list[str] = []
        frozen_seeds = _frozen_seed_records(
            self.generation_policy, frozen_problems
        )
        self.assertEqual([], frozen_problems)
        self.assertEqual(1, len(frozen_seeds))
        problems, blockers, resolutions = validate_proposals(
            records,
            frozen_seeds,
            self.generation_policy,
        )
        self.assertEqual([], problems)
        self.assertEqual(
            "frozen_alias_current_scoped_identity",
            resolutions["HGP-M16-SOLVER-SLOPE-001"],
        )
        self.assertNotIn(
            "stale_seed_snapshot",
            blockers["HGP-M16-SOLVER-SLOPE-001"],
        )

    def test_frozen_seed_snapshot_hash_is_verified(self) -> None:
        policy = copy.deepcopy(self.generation_policy)
        policy["frozen_seed_bindings"][0]["source_sha256"] = "0" * 64
        problems, _ = build_generation_state(
            policy,
            self.decisions,
            self.policy,
            [],
            [],
        )
        self.assertTrue(
            any("source snapshot hash mismatch" in item for item in problems)
        )

    def test_decided_typed_cells_never_generate_seeds(self) -> None:
        typed_problems, typed_state = load_typed_evidence_state()
        self.assertEqual([], typed_problems)
        seeds = generate_seeds(
            self.generation_policy,
            self.decisions,
            self.policy,
            typed_state,
        )
        seeded_cells = {seed["cell_id"] for seed in seeds}
        decided_cells = {
            cell["cell_id"]
            for cell in typed_state["cells"]
            if cell["status"] in {
                "decided_inapplicable",
                "decided_closed",
            }
        }
        self.assertTrue(seeded_cells.isdisjoint(decided_cells))

    def test_seed_overflow_produces_coverage_artifact(self) -> None:
        typed_problems, typed_state = load_typed_evidence_state()
        self.assertEqual([], typed_problems)
        template = next(
            cell for cell in typed_state["cells"] if cell["seed_eligible"]
        )
        overflow_state = copy.deepcopy(typed_state)
        overflow_state["cells"] = []
        for index in range(13):
            cell = copy.deepcopy(template)
            cell["cell_id"] = f"CELL-OVERFLOW-{index:02d}"
            cell["mechanism_id"] = f"M-OVERFLOW-{index:02d}"
            cell["evidence_digest"] = f"{index + 1:064x}"
            overflow_state["cells"].append(cell)
        overflow_state["counts"] = {
            **typed_state["counts"],
            "cells": 13,
            "seed_eligible_cells": 13,
        }
        problems, state = build_generation_state(
            self.generation_policy,
            self.decisions,
            self.policy,
            [],
            [],
            typed_evidence_state=overflow_state,
        )
        self.assertEqual([], problems)
        self.assertEqual(13, state["seed_coverage"]["eligible_seed_count"])
        self.assertTrue(state["seed_coverage"]["overflow_triggered"])
        self.assertEqual(
            "coverage_review_required_non_executable",
            state["seed_coverage"]["disposition"],
        )
        self.assertEqual(13, len(state["seed_coverage"]["represented_cell_ids"]))
        self.assertEqual(13, len(state["generated_seeds"]))

    def test_violated_typed_property_fails_closed_before_generation(
        self,
    ) -> None:
        typed_problems, typed_state = load_typed_evidence_state()
        self.assertEqual([], typed_problems)
        tampered = copy.deepcopy(typed_state)
        cell = next(
            item
            for item in tampered["cells"]
            if item["cell_id"] == "CELL-M-FHJRV-DIRECT-TWO-TORSION"
        )
        cell["seed_eligible"] = True
        cell["status"] = "open"
        seeds = generate_seeds(
            self.generation_policy,
            self.decisions,
            self.policy,
            tampered,
        )
        self.assertNotIn(cell["cell_id"], {seed["cell_id"] for seed in seeds})

    def test_proposal_cannot_change_typed_evidence_binding(self) -> None:
        seed = generate_seeds(
            self.generation_policy, self.decisions, self.policy
        )[0]
        proposal = self.generation_proposal(seed, "HGP-FIXTURE-015")
        proposal["typed_evidence_digest"] = "f" * 64
        problems, state = build_generation_state(
            self.generation_policy,
            self.decisions,
            self.policy,
            [(PROPOSALS_DIR / "HGP-FIXTURE-015.json", proposal)],
            [],
        )
        self.assertEqual([], problems)
        self.assertIn(
            "typed_evidence_mismatch",
            state["proposal_intake"][0]["blockers"],
        )
        self.assertEqual(
            "hard_rejected", state["proposal_intake"][0]["disposition"]
        )

    def test_complete_adversarial_packet_only_creates_non_authorized_draft(
        self,
    ) -> None:
        seed = generate_seeds(
            self.generation_policy, self.decisions, self.policy
        )[0]
        proposal = self.generation_proposal(seed, "HGP-FIXTURE-001")
        proposal_records = [
            (PROPOSALS_DIR / "HGP-FIXTURE-001.json", proposal)
        ]
        generation_policy = self.generation_policy_with_assurance(proposal)
        problems, state = build_generation_state(
            generation_policy,
            self.decisions,
            self.policy,
            proposal_records,
            self.generation_reviews(proposal),
        )
        self.assertEqual([], problems)
        self.assertEqual(1, state["counts"]["quality_cleared_proposals"])
        self.assertEqual(1, state["counts"]["retained_hypothesis_drafts"])
        draft = state["retained_hypothesis_drafts"][0]
        self.assertEqual(
            "quality_cleared_not_authorized",
            draft["status"],
        )
        self.assertEqual(proposal_sha256(proposal), draft["proposal_sha256"])
        self.assertEqual(5, len(draft["review_artifacts"]))
        self.assertEqual(
            {
                "algebra",
                "cryptanalysis_skeptic",
                "prior_art",
                "cost_model",
                "validator_design",
            },
            {
                review["reviewer_role"]
                for review in draft["review_artifacts"]
            },
        )
        draft_payload = copy.deepcopy(draft)
        draft_digest = draft_payload.pop("draft_sha256")
        self.assertEqual(sha256_json(draft_payload), draft_digest)
        self.assertEqual(
            "none", state["proposal_intake"][0]["authorization"]
        )

    def test_known_premise_cannot_reopen_by_relabeling_itself(self) -> None:
        seed = generate_seeds(
            self.generation_policy, self.decisions, self.policy
        )[0]
        proposal = self.generation_proposal(seed, "HGP-FIXTURE-002")
        premise = self.generation_policy["known_premises"][0]["basis"]
        proposal["new_premise"] = premise
        proposal["premise_fingerprint"] = premise_fingerprint(premise)
        problems, state = build_generation_state(
            self.generation_policy,
            self.decisions,
            self.policy,
            [(PROPOSALS_DIR / "HGP-FIXTURE-002.json", proposal)],
            self.generation_reviews(proposal),
        )
        self.assertEqual([], problems)
        self.assertIn(
            "duplicate_or_reencoding",
            state["proposal_intake"][0]["blockers"],
        )
        self.assertEqual(
            "hard_rejected", state["proposal_intake"][0]["disposition"]
        )
        self.assertEqual([], state["retained_hypothesis_drafts"])

    def test_semantic_glv_reencoding_is_blocked_by_adversarial_review(
        self,
    ) -> None:
        seed = generate_seeds(
            self.generation_policy, self.decisions, self.policy
        )[0]
        proposal = self.generation_proposal(
            seed, "HGP-FIXTURE-SEMANTIC-GLV"
        )
        proposal["new_premise"] = (
            "Represent every free coordinate only by its cubic-residue class "
            "and identify all choices inside each class while retaining the "
            "same fixed relation target."
        )
        proposal["premise_fingerprint"] = premise_fingerprint(
            proposal["new_premise"]
        )
        proposal["mechanism_identity"].update(
            {
                "transformation_class": "coordinatewise-cubic-residue-classes",
                "information_source_class": "glv-coordinate-orbits",
                "target_semantics_class": "same-fixed-target",
                "recovery_class": "discard-relative-phase",
                "changed_cost_term": "coordinate-domain-size",
                "precomputation_class": "none",
                "amortization_class": "single-target",
            }
        )
        proposal["mechanism_signature"] = mechanism_signature(proposal)
        reviews = self.generation_reviews(proposal)
        skeptic = next(
            review
            for _, review in reviews
            if review["reviewer_role"] == "cryptanalysis_skeptic"
        )
        skeptic["verdict"] = "block"
        skeptic["blocker_codes"] = ["semantic_reencoding_risk"]
        problems, state = build_generation_state(
            self.generation_policy,
            self.decisions,
            self.policy,
            [
                (
                    PROPOSALS_DIR / "HGP-FIXTURE-SEMANTIC-GLV.json",
                    proposal,
                )
            ],
            reviews,
        )
        self.assertEqual([], problems)
        intake = state["proposal_intake"][0]
        self.assertNotEqual(
            proposal["premise_fingerprint"],
            premise_fingerprint(
                self.generation_policy["known_premises"][0]["basis"]
            ),
        )
        self.assertIn("adversarial_review_blocked", intake["blockers"])
        self.assertEqual("hard_rejected", intake["disposition"])
        self.assertEqual([], state["retained_hypothesis_drafts"])

    def test_review_digest_invalidates_after_proposal_change(self) -> None:
        seed = generate_seeds(
            self.generation_policy, self.decisions, self.policy
        )[0]
        proposal = self.generation_proposal(seed, "HGP-FIXTURE-003")
        reviews = self.generation_reviews(proposal)
        proposal["title"] = "Changed after reviews were written"
        problems, _ = build_generation_state(
            self.generation_policy,
            self.decisions,
            self.policy,
            [(PROPOSALS_DIR / "HGP-FIXTURE-003.json", proposal)],
            reviews,
        )
        self.assertTrue(
            any("proposal_sha256 is stale" in problem for problem in problems)
        )

    def test_one_blocking_review_prevents_quality_clearance(self) -> None:
        seed = generate_seeds(
            self.generation_policy, self.decisions, self.policy
        )[0]
        proposal = self.generation_proposal(seed, "HGP-FIXTURE-004")
        reviews = self.generation_reviews(proposal)
        reviews[0][1]["verdict"] = "block"
        reviews[0][1]["blocker_codes"] = ["missing_exact_mechanism"]
        problems, state = build_generation_state(
            self.generation_policy,
            self.decisions,
            self.policy,
            [(PROPOSALS_DIR / "HGP-FIXTURE-004.json", proposal)],
            reviews,
        )
        self.assertEqual([], problems)
        self.assertIn(
            "adversarial_review_blocked",
            state["proposal_intake"][0]["blockers"],
        )
        self.assertEqual(
            "hard_rejected", state["proposal_intake"][0]["disposition"]
        )

    def test_missing_review_role_is_never_averaged_away(self) -> None:
        seed = generate_seeds(
            self.generation_policy, self.decisions, self.policy
        )[0]
        proposal = self.generation_proposal(seed, "HGP-FIXTURE-005")
        reviews = self.generation_reviews(proposal)[:-1]
        problems, state = build_generation_state(
            self.generation_policy,
            self.decisions,
            self.policy,
            [(PROPOSALS_DIR / "HGP-FIXTURE-005.json", proposal)],
            reviews,
        )
        self.assertEqual([], problems)
        self.assertIn(
            "adversarial_review_incomplete",
            state["proposal_intake"][0]["blockers"],
        )
        self.assertEqual(
            "needs_revision", state["proposal_intake"][0]["disposition"]
        )

    def test_duplicate_mechanism_signature_is_rejected_across_proposals(
        self,
    ) -> None:
        seed = generate_seeds(
            self.generation_policy, self.decisions, self.policy
        )[0]
        first = self.generation_proposal(seed, "HGP-FIXTURE-006")
        second = self.generation_proposal(seed, "HGP-FIXTURE-007")
        second["new_premise"] = (
            "A differently worded premise leaves the exact same declared "
            "algorithmic transformation and complete cost contract unchanged."
        )
        second["premise_fingerprint"] = premise_fingerprint(
            second["new_premise"]
        )
        problems, state = build_generation_state(
            self.generation_policy,
            self.decisions,
            self.policy,
            [
                (PROPOSALS_DIR / "HGP-FIXTURE-006.json", first),
                (PROPOSALS_DIR / "HGP-FIXTURE-007.json", second),
            ],
            [],
        )
        self.assertEqual([], problems)
        for proposal_state in state["proposal_intake"]:
            self.assertIn(
                "duplicate_mechanism_signature",
                proposal_state["blockers"],
            )
            self.assertEqual("hard_rejected", proposal_state["disposition"])
        self.assertEqual(
            1, len(state["collision_groups"]["mechanism_signatures"])
        )

    def test_global_novelty_cannot_be_self_certified(self) -> None:
        seed = generate_seeds(
            self.generation_policy, self.decisions, self.policy
        )[0]
        proposal = self.generation_proposal(seed, "HGP-FIXTURE-008")
        proposal["novelty_scope"][
            "global_novelty"
        ] = "verified_by_primary_review"
        proposal["mechanism_signature"] = mechanism_signature(proposal)
        problems, state = build_generation_state(
            self.generation_policy,
            self.decisions,
            self.policy,
            [(PROPOSALS_DIR / "HGP-FIXTURE-008.json", proposal)],
            self.generation_reviews(proposal),
        )
        self.assertEqual([], problems)
        self.assertIn(
            "novelty_scope_overclaimed",
            state["proposal_intake"][0]["blockers"],
        )
        self.assertEqual([], state["retained_hypothesis_drafts"])

    def test_generation_schema_required_fields_match_manual_validator(
        self,
    ) -> None:
        root = POLICY_PATH.parents[1]
        proposal_schema = load_json(
            root / "experiments" / "engine" / "hypothesis_proposal.schema.json"
        )
        review_schema = load_json(
            root / "experiments" / "engine" / "hypothesis_review.schema.json"
        )
        seed_schema = load_json(
            root / "experiments" / "engine" / "hypothesis_seed.schema.json"
        )
        self.assertEqual(PROPOSAL_FIELDS, set(proposal_schema["required"]))
        self.assertEqual(REVIEW_FIELDS, set(review_schema["required"]))
        seed = generate_seeds(
            self.generation_policy, self.decisions, self.policy
        )[0]
        self.assertEqual(set(seed), set(seed_schema["required"]))

    def test_evidence_manifest_is_bound_to_source_commit(self) -> None:
        seed = generate_seeds(
            self.generation_policy, self.decisions, self.policy
        )[0]
        proposal = self.generation_proposal(seed, "HGP-FIXTURE-009")
        proposal["evidence_manifest"][0]["sha256"] = "f" * 64
        problems, _ = build_generation_state(
            self.generation_policy,
            self.decisions,
            self.policy,
            [(PROPOSALS_DIR / "HGP-FIXTURE-009.json", proposal)],
            [],
        )
        self.assertTrue(
            any(
                "evidence digest does not match source_commit" in problem
                for problem in problems
            )
        )

    def test_same_model_family_cannot_self_certify_independence(self) -> None:
        seed = generate_seeds(
            self.generation_policy, self.decisions, self.policy
        )[0]
        proposal = self.generation_proposal(seed, "HGP-FIXTURE-010")
        reviews = self.generation_reviews(proposal)
        for _, review in reviews:
            review["reviewer_provenance"]["family"] = proposal["provenance"][
                "generator_family"
            ]
        problems, state = build_generation_state(
            self.generation_policy,
            self.decisions,
            self.policy,
            [(PROPOSALS_DIR / "HGP-FIXTURE-010.json", proposal)],
            reviews,
        )
        self.assertEqual([], problems)
        self.assertIn(
            "review_independence_unestablished",
            state["proposal_intake"][0]["blockers"],
        )
        self.assertEqual([], state["retained_hypothesis_drafts"])

    def test_shared_context_cannot_self_certify_independence(self) -> None:
        seed = generate_seeds(
            self.generation_policy, self.decisions, self.policy
        )[0]
        proposal = self.generation_proposal(seed, "HGP-FIXTURE-CTX")
        reviews = self.generation_reviews(proposal)
        required_role = self.generation_policy["quality_gate"][
            "required_independent_roles"
        ][0]
        review = next(
            item
            for _, item in reviews
            if item["reviewer_role"] == required_role
        )
        review["reviewer_provenance"]["context_sha256"] = proposal[
            "provenance"
        ]["context_sha256"]
        problems, state = build_generation_state(
            self.generation_policy,
            self.decisions,
            self.policy,
            [(PROPOSALS_DIR / "HGP-FIXTURE-CTX.json", proposal)],
            reviews,
        )
        self.assertEqual([], problems)
        self.assertIn(
            "review_independence_unestablished",
            state["proposal_intake"][0]["blockers"],
        )
        self.assertEqual([], state["retained_hypothesis_drafts"])

    def test_proposer_cannot_review_its_own_proposal(self) -> None:
        seed = generate_seeds(
            self.generation_policy, self.decisions, self.policy
        )[0]
        proposal = self.generation_proposal(seed, "HGP-FIXTURE-013")
        reviews = self.generation_reviews(proposal)
        reviews[0][1]["reviewer_id"] = proposal["proposer_id"]
        problems, _ = build_generation_state(
            self.generation_policy,
            self.decisions,
            self.policy,
            [(PROPOSALS_DIR / "HGP-FIXTURE-013.json", proposal)],
            reviews,
        )
        self.assertTrue(
            any("proposer cannot review" in problem for problem in problems)
        )

    def test_missing_recovery_precomputation_and_target_semantics_block(
        self,
    ) -> None:
        seed = generate_seeds(
            self.generation_policy, self.decisions, self.policy
        )[0]
        proposal = self.generation_proposal(seed, "HGP-FIXTURE-014")
        proposal["exact_mechanism"]["recovery_map"] = "TBD"
        proposal["exact_mechanism"]["fixed_target_semantics"] = "unknown"
        proposal["cost_bridge"]["precomputation"] = "not specified"
        proposal["mechanism_signature"] = mechanism_signature(proposal)
        problems, state = build_generation_state(
            self.generation_policy,
            self.decisions,
            self.policy,
            [(PROPOSALS_DIR / "HGP-FIXTURE-014.json", proposal)],
            self.generation_reviews(proposal),
        )
        self.assertEqual([], problems)
        blockers = state["proposal_intake"][0]["blockers"]
        self.assertIn("missing_exact_mechanism", blockers)
        self.assertIn("missing_fixed_target_semantics", blockers)
        self.assertIn("hidden_or_unpriced_precomputation", blockers)

    def test_prose_only_packet_cannot_clear_structured_scientific_gates(
        self,
    ) -> None:
        seed = generate_seeds(
            self.generation_policy, self.decisions, self.policy
        )[0]
        proposal = self.generation_proposal(
            seed, "HGP-FIXTURE-STRUCTURED-GATES"
        )
        proposal["mechanism_contract"]["recovery_map"]["inverse"] = ""
        proposal["prediction_contract"]["metric"]["recomputation"] = ""
        proposal["cost_contract"]["online"]["cpu_hours"] = "unpriced"
        proposal["validator_contract"]["independence"][
            "path_independent"
        ] = True
        problems, state = build_generation_state(
            self.generation_policy,
            self.decisions,
            self.policy,
            [
                (
                    PROPOSALS_DIR
                    / "HGP-FIXTURE-STRUCTURED-GATES.json",
                    proposal,
                )
            ],
            self.generation_reviews(proposal),
        )
        self.assertEqual([], problems)
        blockers = state["proposal_intake"][0]["blockers"]
        self.assertIn("missing_exact_mechanism", blockers)
        self.assertIn("missing_falsifiable_prediction", blockers)
        self.assertIn("missing_cost_changing_bridge", blockers)
        self.assertIn("missing_independent_validator_plan", blockers)
        self.assertEqual([], state["retained_hypothesis_drafts"])

    def test_structured_scope_derives_threat_and_toy_ceiling_gates(
        self,
    ) -> None:
        seed = generate_seeds(
            self.generation_policy, self.decisions, self.policy
        )[0]
        proposal = self.generation_proposal(
            seed, "HGP-FIXTURE-STRUCTURED-SCOPE"
        )
        proposal["cost_contract"]["amortization"] = {
            "class": "multi_target",
            "target_count": 16,
            "per_target_cost_included": True,
        }
        proposal["prediction_contract"]["tested_sizes"] = [8, 16, 25]
        problems, state = build_generation_state(
            self.generation_policy,
            self.decisions,
            self.policy,
            [
                (
                    PROPOSALS_DIR
                    / "HGP-FIXTURE-STRUCTURED-SCOPE.json",
                    proposal,
                )
            ],
            self.generation_reviews(proposal),
        )
        self.assertEqual([], problems)
        blockers = state["proposal_intake"][0]["blockers"]
        self.assertIn("threat_model_drift", blockers)
        self.assertIn("targets_secp256k1_directly", blockers)
        self.assertEqual("hard_rejected", state["proposal_intake"][0]["disposition"])

    def test_incompatible_axis_does_not_generate_a_seed(self) -> None:
        policy = copy.deepcopy(self.generation_policy)
        glv_uncertainty = next(
            item
            for item in policy["axes"]["unresolved_questions"]
            if item["id"] == "U-GLV-SOLVING-COST"
        )
        glv_uncertainty["compatibility_tags"] = ["deliberately-incompatible"]
        seeds = generate_seeds(policy, self.decisions, self.policy)
        self.assertEqual(2, len(seeds))
        self.assertNotIn("R-GLV-SEMAEV", {seed["route_id"] for seed in seeds})

    def test_near_duplicate_pair_is_visible_and_not_silently_accepted(
        self,
    ) -> None:
        seed = generate_seeds(
            self.generation_policy, self.decisions, self.policy
        )[0]
        first = self.generation_proposal(seed, "HGP-FIXTURE-011")
        second = self.generation_proposal(seed, "HGP-FIXTURE-012")
        second["new_premise"] = first["new_premise"].replace(
            "persists", "remains"
        )
        second["premise_fingerprint"] = premise_fingerprint(
            second["new_premise"]
        )
        second["mechanism_identity"][
            "transformation_class"
        ] = "character-graded-target-ideal-variant"
        second["mechanism_signature"] = mechanism_signature(second)
        problems, state = build_generation_state(
            self.generation_policy,
            self.decisions,
            self.policy,
            [
                (PROPOSALS_DIR / "HGP-FIXTURE-011.json", first),
                (PROPOSALS_DIR / "HGP-FIXTURE-012.json", second),
            ],
            [],
        )
        self.assertEqual([], problems)
        self.assertEqual(
            1, len(state["collision_groups"]["near_duplicate_pairs"])
        )
        self.assertTrue(
            all(
                "semantic_reencoding_risk" in item["blockers"]
                for item in state["proposal_intake"]
            )
        )

    def test_portfolio_overflow_retains_zero_drafts(self) -> None:
        seed = generate_seeds(
            self.generation_policy, self.decisions, self.policy
        )[0]
        distinct_premises = [
            "A character grading creates stable sparse syzygies across the toy-size ladder.",
            "A recovery-first elimination order removes exceptional fibers before matrix growth.",
            "A target-tag decomposition separates relation validity from orbit bookkeeping costs.",
            "A canonical fiber basis lowers independently replayed recovery work at each size.",
        ]
        proposal_records = []
        review_records = []
        for index, premise in enumerate(distinct_premises, start=20):
            proposal_id = f"HGP-FIXTURE-{index}"
            proposal = self.generation_proposal(seed, proposal_id)
            proposal["new_premise"] = premise
            proposal["premise_fingerprint"] = premise_fingerprint(premise)
            proposal["mechanism_identity"][
                "transformation_class"
            ] = f"fixture-distinct-transform-{index}"
            proposal["mechanism_signature"] = mechanism_signature(proposal)
            proposal_records.append(
                (PROPOSALS_DIR / f"{proposal_id}.json", proposal)
            )
            review_records.extend(self.generation_reviews(proposal))
        generation_policy = self.generation_policy_with_assurance(
            proposal_records[0][1]
        )
        problems, state = build_generation_state(
            generation_policy,
            self.decisions,
            self.policy,
            proposal_records,
            review_records,
        )
        self.assertEqual([], problems)
        self.assertEqual(4, state["counts"]["quality_cleared_proposals"])
        self.assertTrue(state["portfolio_overflow"]["triggered"])
        self.assertEqual([], state["retained_hypothesis_drafts"])


if __name__ == "__main__":
    unittest.main()
