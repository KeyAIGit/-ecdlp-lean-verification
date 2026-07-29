#!/usr/bin/env python3
"""Semantic fault injections for the TASK-024 certificate."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest
from typing import Any, Callable


HERE = Path(__file__).resolve().parent
ARTIFACT_PATH = HERE / "artifact.json"
VALIDATOR_PATH = HERE / "validate.py"
SPEC = importlib.util.spec_from_file_location("task024_validator", VALIDATOR_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load TASK-024 validator")
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)

Document = dict[str, Any]
Mutation = Callable[[Document], None]
PathPart = str | int


def set_value(path: tuple[PathPart, ...], value: Any) -> Mutation:
    def mutate(document: Document) -> None:
        node: Any = document
        for part in path[:-1]:
            node = node[part]
        node[path[-1]] = copy.deepcopy(value)
    return mutate


def delete_value(path: tuple[PathPart, ...]) -> Mutation:
    def mutate(document: Document) -> None:
        node: Any = document
        for part in path[:-1]:
            node = node[part]
        del node[path[-1]]
    return mutate


FAULTS: list[tuple[str, Mutation]] = [
    ("artifact id", set_value(("artifact_id",), "TASK024-APPROX")),
    ("schema", set_value(("schema_version",), 2)),
    ("kind", set_value(("kind",), "experiment")),
    ("source status", set_value(("binding_state", "source_status"), "draft")),
    ("source path", set_value(("binding_state", "source_path"), "wrong.lean")),
    ("source sha", set_value(("binding_state", "source_sha256"), "0" * 64)),
    ("sidecar", set_value(("binding_state", "artifact_sidecar"), "wrong.sha")),
    ("digest match", set_value(("binding_state", "digest_match"), False)),
    ("dependency path", set_value(("depends_on", 0, "path"), "wrong.json")),
    ("dependency sha", set_value(("depends_on", 0, "required_sha256"), "1" * 64)),
    ("source dependency", set_value(("depends_on", 1, "required_sha256"), "2" * 64)),
    ("stage", set_value(("mask_pruning_contract", "stage"), 13)),
    ("slots", set_value(("mask_pruning_contract", "projective_slot_count"), 13)),
    ("full count", set_value(("mask_pruning_contract", "full_mask_count"), 8192)),
    ("formula", set_value(("mask_pruning_contract", "full_mask_count_formula"), "2^13")),
    ("separated", set_value(("mask_pruning_contract", "separated_mask_count"), 986)),
    ("interior", set_value(("mask_pruning_contract", "interior_separated_mask_count"), 376)),
    ("interior slots", set_value(("mask_pruning_contract", "interior_slot_count"), 11)),
    ("affine assumption", set_value(("mask_pruning_contract", "affine_input_assumption"), "none")),
    ("adjacent consequence", set_value(("mask_pruning_contract", "adjacent_infinity_consequence"), "0=0")),
    ("separation", set_value(("mask_pruning_contract", "separated_mask_definition"), "arbitrary")),
    ("boundary zero", set_value(("mask_pruning_contract", "boundary_conditions", "slot_0_infinity_implies"), "none")),
    ("boundary last", set_value(("mask_pruning_contract", "boundary_conditions", "slot_13_infinity_implies"), "none")),
    ("endpoint assumptions", set_value(("mask_pruning_contract", "endpoint_nonzero_assumptions_required_for_377"), False)),
    ("neighbor forcing", set_value(("mask_pruning_contract", "neighbor_forcing"), "unconstrained")),
    ("materialization", set_value(("mask_pruning_contract", "production_mask_family_materialized"), True)),
    ("fixture fields", set_value(("local_identity_fixture", "fields"), [5])),
    ("fixture enumeration", set_value(("local_identity_fixture", "full_production_mask_enumeration_executed"), True)),
    ("fixture recurrence", set_value(("local_identity_fixture", "mask_counts_derived_by_path_recurrence"), False)),
    ("fixture neighbor", set_value(("local_identity_fixture", "neighbor_coordinate_fixture_exhaustive"), False)),
    ("fixture zero", set_value(("local_identity_fixture", "projective_zero_pair_admitted"), True)),
    ("producer solver", set_value(("producer_checks", "solver_executed"), True)),
    ("producer rank", set_value(("producer_checks", "rank_estimated"), True)),
    ("producer yield", set_value(("producer_checks", "relation_yield_estimated"), True)),
    ("producer auth", set_value(("producer_checks", "experiment_authorized"), True)),
    ("proof count", set_value(("proof_status", "card_separatedInfinityMask"), "kernel_checked")),
    ("proof cover", set_value(("proof_status", "cover_equivalences"), "informal")),
    ("proof cost", set_value(("proof_status", "solver_rank_yield_cost_claim"), "proved")),
    ("scope task", set_value(("scope", "task"), "TASK-025")),
    ("scope barrier", set_value(("scope", "barrier"), "closed")),
    ("terminal auth", set_value(("terminal_disposition", "authorization"), "approved")),
    ("terminal effect", set_value(("terminal_disposition", "barrier_effect"), "cost_closed")),
    ("terminal orchestration", set_value(("terminal_disposition", "mask_orchestration_status"), "complete")),
    ("terminal route", set_value(("terminal_disposition", "route_status"), "promoted")),
    ("binding deleted", delete_value(("theorem_bindings", "HValue_third_infinity"))),
    ("binding renamed", set_value(("theorem_bindings", "card_infinityMask"), "wrong")),
    ("closed list", set_value(("downstream_open_boundary", "closed_here"), [])),
    ("nonclaim list", set_value(("downstream_open_boundary", "not_claimed"), [])),
    ("blocker", set_value(("downstream_open_boundary", "remaining_blocker"), "none")),
]


class CertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.canonical = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))

    def test_canonical_document(self) -> None:
        validator.validate_document(self.canonical)

    def test_artifact_sidecar(self) -> None:
        validator.validate_sidecar()

    def test_exactly_49_semantic_faults(self) -> None:
        self.assertEqual(len(FAULTS), 49)

    def test_all_semantic_faults_are_rejected(self) -> None:
        for name, mutation in FAULTS:
            with self.subTest(name=name):
                candidate = copy.deepcopy(self.canonical)
                mutation(candidate)
                with self.assertRaises(validator.ValidationError):
                    validator.validate_document(candidate)

    def test_path_counts(self) -> None:
        self.assertEqual(validator.path_independent_set_count(14), 987)
        self.assertEqual(validator.path_independent_set_count(12), 377)

    def test_local_identity_fixture(self) -> None:
        validator.validate_local_fixture()

    def test_final_source_gate(self) -> None:
        validator.validate_source(validator.ROOT)


if __name__ == "__main__":
    unittest.main(verbosity=2)
