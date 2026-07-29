#!/usr/bin/env python3
"""Semantic fault injections for the TASK-023 chart-cover certificate."""

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

SPEC = importlib.util.spec_from_file_location(
    "task023_independent_validator", VALIDATOR_PATH
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load TASK-023 validator")
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


SEMANTIC_FAULTS: list[tuple[str, Mutation]] = [
    ("wrong artifact id", set_value(("artifact_id",), "TASK023-APPROX")),
    ("wrong schema version", set_value(("schema_version",), 2)),
    (
        "downgraded artifact kind",
        set_value(("kind",), "source_bound_non_run_certificate_template"),
    ),
    (
        "downgraded source status",
        set_value(("binding_state", "source_status"), "draft"),
    ),
    (
        "invented source digest",
        set_value(("binding_state", "source_sha256"), "0" * 64),
    ),
    (
        "wrong artifact sidecar",
        set_value(
            ("binding_state", "artifact_sidecar"),
            "artifact.sha256.template",
        ),
    ),
    (
        "changed TASK022 artifact digest",
        set_value(("depends_on", 0, "required_sha256"), "1" * 64),
    ),
    (
        "changed TASK022 source digest",
        set_value(("depends_on", 1, "observed_sha256"), "2" * 64),
    ),
    (
        "changed final source dependency digest",
        set_value(
            ("depends_on", 2, "required_sha256"),
            "3" * 64,
        ),
    ),
    (
        "cleared final source digest match",
        set_value(("depends_on", 2, "digest_match"), False),
    ),
    (
        "changed stage",
        set_value(("chart_cover_contract", "stage"), 15),
    ),
    (
        "changed projective slot count",
        set_value(("chart_cover_contract", "projective_slot_count"), 13),
    ),
    (
        "changed infinity mask type",
        set_value(
            ("chart_cover_contract", "infinity_mask_type"),
            "Finset (Fin 13)",
        ),
    ),
    (
        "reversed mask membership semantics",
        set_value(
            ("chart_cover_contract", "mask_membership_semantics"),
            "i in I iff slot i is affine",
        ),
    ),
    (
        "broadened chart variable type",
        set_value(
            ("chart_cover_contract", "fixed_mask_variable_index_type"),
            "Fin 14",
        ),
    ),
    (
        "changed chart variable formula",
        set_value(
            ("chart_cover_contract", "fixed_mask_variable_count_formula"),
            "14",
        ),
    ),
    (
        "changed chart variable range",
        set_value(
            ("chart_cover_contract", "fixed_mask_variable_count_range"),
            [1, 14],
        ),
    ),
    (
        "added infinity variable",
        set_value(
            ("chart_cover_contract", "variables_per_infinity_slot"),
            1,
        ),
    ),
    (
        "changed fixed-mask equation total",
        set_value(
            ("chart_cover_contract", "total_equation_count_per_fixed_mask"),
            14,
        ),
    ),
    (
        "changed base equation count",
        set_value(
            (
                "chart_cover_contract",
                "equation_families",
                "base",
                "count",
            ),
            2,
        ),
    ),
    (
        "changed step equation count",
        set_value(
            (
                "chart_cover_contract",
                "equation_families",
                "step",
                "count",
            ),
            12,
        ),
    ),
    (
        "changed final equation count",
        set_value(
            (
                "chart_cover_contract",
                "equation_families",
                "final",
                "count",
            ),
            2,
        ),
    ),
    (
        "reintroduced guard equation",
        set_value(
            (
                "chart_cover_contract",
                "equation_families",
                "guard",
                "count",
            ),
            1,
        ),
    ),
    (
        "raised base degree",
        set_value(
            (
                "chart_cover_contract",
                "equation_families",
                "base",
                "degree_upper_bound",
            ),
            4,
        ),
    ),
    (
        "raised step degree",
        set_value(
            (
                "chart_cover_contract",
                "equation_families",
                "step",
                "degree_upper_bound",
            ),
            6,
        ),
    ),
    (
        "raised final degree",
        set_value(
            (
                "chart_cover_contract",
                "equation_families",
                "final",
                "degree_upper_bound",
            ),
            4,
        ),
    ),
    (
        "claimed exact total degree",
        set_value(
            ("chart_cover_contract", "exact_total_degree_claimed"),
            True,
        ),
    ),
    (
        "lowered overall degree ceiling",
        set_value(
            ("chart_cover_contract", "overall_degree_upper_bound"),
            3,
        ),
    ),
    (
        "changed logical mask count",
        set_value(("chart_cover_contract", "logical_mask_count"), 8192),
    ),
    (
        "required production enumeration",
        set_value(
            (
                "chart_cover_contract",
                "production_mask_enumeration_required",
            ),
            True,
        ),
    ),
    (
        "materialized production masks",
        set_value(
            ("chart_cover_contract", "production_mask_materialized"),
            True,
        ),
    ),
    (
        "weakened equivalence to one way",
        set_value(("exactness_contract", "equivalence_direction"), "forward"),
    ),
    (
        "changed prior chain stage",
        set_value(
            ("exactness_contract", "prior_chain"),
            "FrozenProjectiveChain q 13 y",
        ),
    ),
    (
        "removed guarded-system bridge",
        set_value(
            ("exactness_contract", "guarded_system_bridge"),
            "not_claimed",
        ),
    ),
    (
        "rejected infinity",
        set_value(("exactness_contract", "infinity_retained"), False),
    ),
    (
        "admitted projective zero",
        set_value(
            ("exactness_contract", "projective_zero_pair_admitted"),
            True,
        ),
    ),
    (
        "changed raw F5 pair count",
        set_value(("finite_field_fixture", "raw_nonzero_pair_count"), 23),
    ),
    (
        "changed F5 projective point count",
        set_value(("finite_field_fixture", "projective_point_count"), 5),
    ),
    (
        "changed F5 class size",
        set_value(
            ("finite_field_fixture", "scalar_multiples_per_projective_point"),
            5,
        ),
    ),
    (
        "changed reduced chain count",
        set_value(("finite_field_fixture", "normalized_chain_count"), 215),
    ),
    (
        "changed reduced mask count",
        set_value(
            ("finite_field_fixture", "observed_reduced_mask_count"),
            7,
        ),
    ),
    (
        "changed mask-cardinality distribution",
        set_value(
            (
                "finite_field_fixture",
                "mask_cardinality_chain_distribution",
                "1",
            ),
            74,
        ),
    ),
    (
        "claimed production fixture enumeration",
        set_value(
            (
                "finite_field_fixture",
                "production_mask_enumeration_executed",
            ),
            True,
        ),
    ),
    (
        "changed literal H monomial count",
        set_value(("degree_fixture", "literal_h_monomial_count"), 8),
    ),
    (
        "changed independently derived base degree",
        set_value(
            (
                "degree_fixture",
                "derived_family_degree_ceilings",
                "base",
            ),
            4,
        ),
    ),
    (
        "changed theorem declaration",
        set_value(
            (
                "theorem_bindings",
                "frozenProjectiveChain_iff_chartPolynomialCover",
                "declaration",
            ),
            "Ecdlp.FrozenProjectiveSemaev.approximate_chart_cover",
        ),
    ),
    (
        "claimed proof before source exists",
        set_value(
            (
                "proof_status",
                "frozenProjectiveChain_iff_chartPolynomialCover",
            ),
            "not_claimed",
        ),
    ),
    (
        "enabled solver",
        set_value(("producer_checks", "solver_executed"), True),
    ),
    (
        "estimated rank",
        set_value(("producer_checks", "rank_estimated"), True),
    ),
    (
        "authorized experiment",
        set_value(("producer_checks", "experiment_authorized"), True),
    ),
    (
        "promoted route",
        set_value(("terminal_disposition", "route_effect"), "promoted"),
    ),
    (
        "deleted final-source closure obligation",
        delete_value(("downstream_open_boundary", "closed_here", 3)),
    ),
    (
        "deleted nonclaim",
        delete_value(("downstream_open_boundary", "not_claimed", 2)),
    ),
    (
        "changed remaining blocker",
        set_value(
            ("downstream_open_boundary", "remaining_blocker"),
            "none",
        ),
    ),
    (
        "changed task scope",
        set_value(("scope", "task"), "TASK-022"),
    ),
    (
        "changed three-infinity variable count",
        set_value(
            (
                "finite_field_fixture",
                "sample_production_variable_counts",
                "I.card=3",
            ),
            12,
        ),
    ),
    (
        "changed affine representative",
        set_value(
            ("chart_cover_contract", "affine_chart_representative"),
            "[1:X_i]",
        ),
    ),
    (
        "changed infinity representative",
        set_value(
            ("chart_cover_contract", "infinity_chart_representative"),
            "[0:1]",
        ),
    ),
    (
        "claimed producer enumerated masks",
        set_value(
            ("producer_checks", "full_production_mask_family_enumerated"),
            True,
        ),
    ),
    (
        "downgraded kernel assurance",
        set_value(
            ("terminal_disposition", "assurance"),
            "draft_contract",
        ),
    ),
]


class SemanticFaultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))

    def test_canonical_document(self) -> None:
        validator.validate_document(copy.deepcopy(self.document))

    def test_exactly_60_semantic_faults(self) -> None:
        self.assertEqual(len(SEMANTIC_FAULTS), 60)
        self.assertEqual(len({name for name, _ in SEMANTIC_FAULTS}), 60)

    def test_reduced_f5_chart_fixture(self) -> None:
        observed = validator.enumerate_f5_reduced_chart_fixture()
        self.assertEqual(observed["raw_nonzero_pairs"], 24)
        self.assertEqual(observed["projective_points"], 6)
        self.assertEqual(observed["fiber_sizes"], {4})
        self.assertEqual(observed["affine_points"], 5)
        self.assertEqual(observed["infinity_points"], 1)
        self.assertTrue(observed["zero_rejected"])
        self.assertEqual(observed["chain_count"], 216)
        self.assertEqual(observed["mask_count"], 8)
        self.assertEqual(
            observed["mask_cardinality_distribution"],
            {0: 125, 1: 75, 2: 15, 3: 1},
        )
        self.assertEqual(observed["infinity_chart"], ("infinity", None))
        self.assertFalse(observed["production_masks_enumerated"])

    def test_literal_h_degree_fixture(self) -> None:
        observed = validator.derive_literal_h_degree_fixture()
        self.assertEqual(observed["literal_h_monomials"], 9)
        self.assertEqual(observed["argument_multidegrees"], [2, 2, 2])
        self.assertEqual(
            observed["family_ceilings"],
            {"base": 2, "step": 4, "final": 2},
        )

    def test_production_cardinality_arithmetic_without_powerset(self) -> None:
        self.assertEqual(
            validator.production_variable_count_samples(),
            {
                "I.card=0": 14,
                "I.card=1": 13,
                "I.card=3": 11,
                "I.card=14": 0,
            },
        )

    def test_final_source_gate(self) -> None:
        validator.validate_document(
            copy.deepcopy(self.document),
            require_final_source_binding=True,
        )

    def test_artifact_sidecar(self) -> None:
        validator.validate_artifact_sidecar()

    def test_all_semantic_faults_are_rejected(self) -> None:
        for name, mutation in SEMANTIC_FAULTS:
            with self.subTest(name=name):
                document = copy.deepcopy(self.document)
                before = copy.deepcopy(document)
                mutation(document)
                self.assertNotEqual(document, before)
                with self.assertRaises(validator.ValidationError):
                    validator.validate_document(document)


if __name__ == "__main__":
    unittest.main(verbosity=2)
