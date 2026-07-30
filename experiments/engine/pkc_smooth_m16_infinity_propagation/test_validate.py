#!/usr/bin/env python3
"""Semantic fault injections for the TASK-025 certificate."""

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
SPEC = importlib.util.spec_from_file_location("task025_validator", VALIDATOR_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load TASK-025 validator")
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
    ("artifact id", set_value(("artifact_id",), "TASK025-APPROX")),
    ("schema", set_value(("schema_version",), 2)),
    ("kind", set_value(("kind",), "experiment")),
    ("source status", set_value(("binding_state", "source_status"), "draft")),
    ("source path", set_value(("binding_state", "source_path"), "wrong.lean")),
    ("source sha", set_value(("binding_state", "source_sha256"), "0" * 64)),
    ("sidecar", set_value(("binding_state", "artifact_sidecar"), "wrong.sha")),
    ("digest match", set_value(("binding_state", "digest_match"), False)),
    ("dependency path", set_value(("depends_on", 0, "path"), "wrong.json")),
    (
        "dependency artifact sha",
        set_value(("depends_on", 0, "required_sha256"), "1" * 64),
    ),
    (
        "dependency strata sha",
        set_value(("depends_on", 1, "required_sha256"), "2" * 64),
    ),
    (
        "dependency witness sha",
        set_value(("depends_on", 2, "required_sha256"), "3" * 64),
    ),
    ("stage", set_value(("mask_propagation_contract", "stage"), 13)),
    (
        "projective slots",
        set_value(("mask_propagation_contract", "projective_slot_count"), 13),
    ),
    (
        "interior slots",
        set_value(("mask_propagation_contract", "interior_slot_count"), 11),
    ),
    (
        "starting count",
        set_value(
            ("mask_propagation_contract", "starting_interior_separated_mask_count"),
            376,
        ),
    ),
    (
        "gap two count",
        set_value(("mask_propagation_contract", "gap_two_mask_count"), 128),
    ),
    (
        "gap three count",
        set_value(("mask_propagation_contract", "gap_three_mask_count"), 68),
    ),
    (
        "boundary count",
        set_value(
            ("mask_propagation_contract", "boundary_propagated_mask_count"),
            59,
        ),
    ),
    (
        "combined count",
        set_value(
            (
                "mask_propagation_contract",
                "combined_boundary_gap_three_mask_count",
            ),
            35,
        ),
    ),
    (
        "affine assumption",
        set_value(("mask_propagation_contract", "affine_input_assumption"), "none"),
    ),
    (
        "distance two condition",
        set_value(
            ("mask_propagation_contract", "distance_two_forced_condition"),
            "0=0",
        ),
    ),
    (
        "distance two range",
        set_value(
            ("mask_propagation_contract", "distance_two_input_range"),
            "i : Fin 11",
        ),
    ),
    (
        "distance two regular",
        set_value(
            ("mask_propagation_contract", "distance_two_regular_assumption"),
            "none",
        ),
    ),
    (
        "distance three condition",
        set_value(
            ("mask_propagation_contract", "distance_three_forced_condition"),
            "0=0",
        ),
    ),
    (
        "distance three range",
        set_value(
            ("mask_propagation_contract", "distance_three_input_range"),
            "i : Fin 10",
        ),
    ),
    (
        "distance three regular",
        set_value(
            ("mask_propagation_contract", "distance_three_regular_assumption"),
            "none",
        ),
    ),
    (
        "gap two definition",
        set_value(
            ("mask_propagation_contract", "gap_two_mask_definition"),
            "arbitrary",
        ),
    ),
    (
        "gap three definition",
        set_value(
            ("mask_propagation_contract", "gap_three_mask_definition"),
            "arbitrary",
        ),
    ),
    (
        "boundary definition",
        set_value(
            ("mask_propagation_contract", "boundary_propagated_mask_definition"),
            "arbitrary",
        ),
    ),
    (
        "boundary regular",
        set_value(
            ("mask_propagation_contract", "boundary_regular_assumption"),
            "none",
        ),
    ),
    (
        "boundary prefix",
        set_value(
            (
                "mask_propagation_contract",
                "boundary_near_forced_conditions",
                "slot_1_infinity_implies",
            ),
            "none",
        ),
    ),
    (
        "boundary suffix",
        set_value(
            (
                "mask_propagation_contract",
                "boundary_near_forced_conditions",
                "slot_12_infinity_implies",
            ),
            "none",
        ),
    ),
    (
        "endpoint zero",
        set_value(
            (
                "mask_propagation_contract",
                "endpoint_nonzero_assumptions",
                "slot_0",
            ),
            "none",
        ),
    ),
    (
        "endpoint last",
        set_value(
            (
                "mask_propagation_contract",
                "endpoint_nonzero_assumptions",
                "slot_13",
            ),
            "none",
        ),
    ),
    (
        "mask materialization",
        set_value(
            ("mask_propagation_contract", "production_mask_family_materialized"),
            True,
        ),
    ),
    (
        "fixture field",
        set_value(("local_propagation_fixture", "fields"), [5]),
    ),
    (
        "fixture field role",
        set_value(
            ("local_propagation_fixture", "field_roles", "7"),
            "curve applicability fixture",
        ),
    ),
    (
        "fixture count method",
        set_value(
            ("local_propagation_fixture", "mask_counts_derived_by_gap_recurrence"),
            False,
        ),
    ),
    (
        "fixture enumeration",
        set_value(
            (
                "local_propagation_fixture",
                "full_production_mask_enumeration_executed",
            ),
            True,
        ),
    ),
    (
        "fixture projective zero",
        set_value(
            ("local_propagation_fixture", "projective_zero_pair_admitted"),
            True,
        ),
    ),
    (
        "fixture symmetry",
        set_value(
            (
                "local_propagation_fixture",
                "hvalue_first_third_symmetry_exhaustive",
            ),
            False,
        ),
    ),
    (
        "fixture prefix slots",
        set_value(
            ("local_propagation_fixture", "balanced_prefix_slots"),
            [0, 1, 2, 3, 4, 5],
        ),
    ),
    (
        "fixture suffix slots",
        set_value(
            ("local_propagation_fixture", "balanced_suffix_slots"),
            [6, 7, 8, 9, 10, 11],
        ),
    ),
    (
        "fixture stage",
        set_value(
            ("local_propagation_fixture", "maximum_balanced_frozen_stage"),
            6,
        ),
    ),
    (
        "fixture witness count",
        set_value(
            (
                "local_propagation_fixture",
                "antecedent_witness_counts",
                "7",
                "distance_three",
            ),
            48,
        ),
    ),
    (
        "fixture scope",
        set_value(("local_propagation_fixture", "fixture_scope"), "full solver"),
    ),
    (
        "propagation algebraic closure",
        set_value(
            (
                "prefix_suffix_contract",
                "propagation_algebraic_closure_required",
            ),
            True,
        ),
    ),
    (
        "source bridge algebraic closure",
        set_value(
            (
                "prefix_suffix_contract",
                "source_stage_bridge_algebraic_closure_required",
            ),
            False,
        ),
    ),
    (
        "source bridge injectivity",
        set_value(
            (
                "prefix_suffix_contract",
                "source_stage_bridge_map_required_injective",
            ),
            False,
        ),
    ),
    (
        "source bridge regularity location",
        set_value(
            (
                "prefix_suffix_contract",
                "source_stage_regular_assumptions_location",
            ),
            "source field",
        ),
    ),
    (
        "source bridge statement",
        set_value(
            ("prefix_suffix_contract", "source_stage_bridge"),
            "unconditional source-field equivalence",
        ),
    ),
    (
        "source computation transfer",
        set_value(
            (
                "prefix_suffix_contract",
                "source_field_computation_establishes_mapped_regularity",
            ),
            True,
        ),
    ),
    (
        "target witness descent",
        set_value(
            ("prefix_suffix_contract", "target_witness_descent_claimed"),
            True,
        ),
    ),
    (
        "prefix obstruction count",
        set_value(("prefix_suffix_contract", "prefix_obstruction_count"), 11),
    ),
    (
        "balanced obstruction count",
        set_value(("prefix_suffix_contract", "balanced_obstruction_count"), 11),
    ),
    (
        "balanced prefix count",
        set_value(("prefix_suffix_contract", "balanced_prefix_count"), 5),
    ),
    (
        "balanced suffix count",
        set_value(("prefix_suffix_contract", "balanced_suffix_count"), 5),
    ),
    (
        "balanced max stage",
        set_value(("prefix_suffix_contract", "maximum_balanced_frozen_stage"), 6),
    ),
    (
        "prefix value",
        set_value(("prefix_suffix_contract", "prefix_obstruction_value"), "opaque"),
    ),
    (
        "prefix zero identity",
        set_value(
            ("prefix_suffix_contract", "prefix_stage_zero_identity"),
            "opaque",
        ),
    ),
    (
        "suffix value",
        set_value(("prefix_suffix_contract", "balanced_suffix_value"), "opaque"),
    ),
    (
        "suffix zero identity",
        set_value(
            ("prefix_suffix_contract", "suffix_stage_zero_identity"),
            "opaque",
        ),
    ),
    (
        "one-way direction",
        set_value(("prefix_suffix_contract", "one_way_resultant_direction"), "iff"),
    ),
    (
        "slot consequence",
        set_value(
            ("prefix_suffix_contract", "selected_internal_slot_consequence"),
            "none",
        ),
    ),
    (
        "endpoint guards",
        set_value(("prefix_suffix_contract", "endpoint_guards_required"), False),
    ),
    (
        "empty mask",
        set_value(("prefix_suffix_contract", "empty_mask_conclusion"), "arbitrary"),
    ),
    (
        "single chart mask",
        set_value(("prefix_suffix_contract", "single_chart_mask"), "unknown"),
    ),
    (
        "affine variables",
        set_value(("prefix_suffix_contract", "affine_chart_variable_count"), 13),
    ),
    (
        "generic claim",
        set_value(("prefix_suffix_contract", "generic_locus_claimed"), True),
    ),
    (
        "nonempty claim",
        set_value(
            ("prefix_suffix_contract", "regular_locus_nonempty_proved"),
            True,
        ),
    ),
    (
        "symbolic claim",
        set_value(
            (
                "prefix_suffix_contract",
                "symbolic_polynomial_nonzeroness_proved",
            ),
            True,
        ),
    ),
    (
        "unique witness",
        set_value(("prefix_suffix_contract", "unique_witness_claimed"), True),
    ),
    ("producer solver", set_value(("producer_checks", "solver_executed"), True)),
    ("producer rank", set_value(("producer_checks", "rank_estimated"), True)),
    (
        "producer yield",
        set_value(("producer_checks", "relation_yield_estimated"), True),
    ),
    (
        "producer search",
        set_value(("producer_checks", "exact_target_search_executed"), True),
    ),
    (
        "producer discrete log",
        set_value(("producer_checks", "discrete_log_executed"), True),
    ),
    (
        "producer enumeration",
        set_value(
            ("producer_checks", "full_production_mask_family_enumerated"),
            True,
        ),
    ),
    (
        "producer sweep",
        set_value(("producer_checks", "parameter_sweep_executed"), True),
    ),
    (
        "producer authorization",
        set_value(("producer_checks", "experiment_authorized"), True),
    ),
    (
        "proof distance two",
        set_value(("proof_status", "distance_two_propagation"), "informal"),
    ),
    (
        "proof distance three",
        set_value(("proof_status", "distance_three_propagation"), "informal"),
    ),
    (
        "proof count",
        set_value(
            ("proof_status", "card_gapThreeInteriorInfinityMask"),
            "kernel_checked",
        ),
    ),
    (
        "proof generic",
        set_value(("proof_status", "generic_or_nonempty_regular_locus"), "proved"),
    ),
    (
        "proof source bridge",
        set_value(("proof_status", "source_stage_affine_bridge"), "informal"),
    ),
    (
        "proof cost",
        set_value(("proof_status", "solver_rank_yield_cost_claim"), "proved"),
    ),
    ("scope task", set_value(("scope", "task"), "TASK-024")),
    ("scope barrier", set_value(("scope", "barrier"), "closed")),
    (
        "terminal generic",
        set_value(("terminal_disposition", "generic_locus_status"), "proved"),
    ),
    (
        "terminal effect",
        set_value(("terminal_disposition", "barrier_effect"), "cost_closed"),
    ),
    (
        "terminal orchestration",
        set_value(
            ("terminal_disposition", "mask_orchestration_status"),
            "complete solver",
        ),
    ),
    (
        "terminal representation",
        set_value(
            ("terminal_disposition", "representation_status"),
            "unique solution",
        ),
    ),
    (
        "terminal source bridge",
        set_value(
            ("terminal_disposition", "source_stage_bridge_status"),
            "unconditional source-field bridge",
        ),
    ),
    (
        "terminal route",
        set_value(("terminal_disposition", "route_status"), "promoted"),
    ),
    (
        "binding deleted",
        delete_value(
            (
                "theorem_bindings",
                "frozenChartSystem_gapThreeInfinity_forces_HValue_zero",
            )
        ),
    ),
    (
        "binding renamed",
        set_value(
            ("theorem_bindings", "card_gapTwoInteriorInfinityMask"),
            "wrong",
        ),
    ),
    (
        "source bridge binding renamed",
        set_value(
            (
                "theorem_bindings",
                "frozenRecS17_iff_affineChartPolynomialCover_over_of_balancedPropagatedRegular",
            ),
            "wrong",
        ),
    ),
    (
        "closed claims",
        set_value(("downstream_open_boundary", "closed_here"), []),
    ),
    (
        "nonclaims",
        set_value(("downstream_open_boundary", "not_claimed"), []),
    ),
    (
        "remaining blocker",
        set_value(("downstream_open_boundary", "remaining_blocker"), "none"),
    ),
]


class CertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.canonical = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))

    def test_canonical_document(self) -> None:
        validator.validate_document(self.canonical)

    def test_artifact_sidecar(self) -> None:
        validator.validate_sidecar()

    def test_fault_inventory_is_unique_and_broad(self) -> None:
        names = [name for name, _ in FAULTS]
        self.assertGreaterEqual(len(FAULTS), 80)
        self.assertEqual(len(names), len(set(names)))

    def test_all_semantic_faults_are_rejected(self) -> None:
        for name, mutation in FAULTS:
            with self.subTest(name=name):
                candidate = copy.deepcopy(self.canonical)
                mutation(candidate)
                with self.assertRaises(validator.ValidationError):
                    validator.validate_document(
                        candidate,
                        require_final_source_binding=False,
                    )

    def test_exact_gap_counts(self) -> None:
        self.assertEqual(validator.spaced_subset_count(12, 2), 377)
        self.assertEqual(validator.spaced_subset_count(12, 3), 129)
        self.assertEqual(validator.spaced_subset_count(12, 4), 69)
        self.assertEqual(validator.spaced_subset_count(10, 3), 60)
        self.assertEqual(validator.spaced_subset_count(10, 4), 36)

    def test_local_propagation_fixture(self) -> None:
        validator.validate_local_fixture()

    def test_final_source_gate(self) -> None:
        validator.validate_source(validator.ROOT)


if __name__ == "__main__":
    unittest.main(verbosity=2)
