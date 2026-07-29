#!/usr/bin/env python3
"""Exactly 26 semantic fault injections for the TASK-022 certificate."""

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
    "task022_independent_validator", VALIDATOR_PATH
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load TASK-022 validator")
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
    ("wrong artifact id", set_value(("artifact_id",), "TASK022-APPROX")),
    ("solver certificate kind",
     set_value(("kind",), "kernel_and_solver_certificate")),
    (
        "weakened source field",
        set_value(
            ("assumption_contract", "source_coefficients"),
            "the source uses a CommRing k",
        ),
    ),
    (
        "removed injectivity",
        set_value(
            ("assumption_contract", "coefficient_map"),
            "phi : k ->+* K is arbitrary",
        ),
    ),
    (
        "claimed base-field descent",
        set_value(
            ("assumption_contract", "no_base_field_descent"),
            "all witnesses descend to k",
        ),
    ),
    (
        "deleted a closed-here claim",
        delete_value(("downstream_open_boundary", "closed_here", 5)),
    ),
    (
        "changed stage",
        set_value(("guarded_system_contract", "stage"), 15),
    ),
    (
        "changed slot count",
        set_value(
            ("guarded_system_contract", "projective_slot_count"), 13
        ),
    ),
    (
        "changed variable count",
        set_value(("guarded_system_contract", "total_variable_count"), 52),
    ),
    (
        "changed H count",
        set_value(
            (
                "guarded_system_contract",
                "equation_families",
                "H",
                "count",
            ),
            14,
        ),
    ),
    (
        "changed guard count",
        set_value(
            (
                "guarded_system_contract",
                "equation_families",
                "guard",
                "count",
            ),
            13,
        ),
    ),
    (
        "changed total equation count",
        set_value(("guarded_system_contract", "total_equation_count"), 28),
    ),
    (
        "changed guard polynomial",
        set_value(
            ("guarded_system_contract", "guard_equation"),
            "A*U+B*V=0",
        ),
    ),
    (
        "claimed exact degree",
        set_value(
            ("guarded_system_contract", "exact_total_degree_claimed"), True
        ),
    ),
    (
        "lowered degree upper bound",
        set_value(
            ("guarded_system_contract", "total_degree_upper_bound"), 3
        ),
    ),
    (
        "rejected infinity",
        set_value(
            (
                "finite_field_fixture",
                "distinguished_infinity_pair_allowed",
            ),
            False,
        ),
    ),
    (
        "accepted zero pair",
        set_value(("finite_field_fixture", "zero_pair_rejected"), False),
    ),
    (
        "changed exhaustive assignment count",
        set_value(
            ("finite_field_fixture", "exhaustive_assignment_count"), 624
        ),
    ),
    (
        "changed guard solution count",
        set_value(("finite_field_fixture", "guard_solution_count"), 119),
    ),
    (
        "changed source digest",
        set_value(("depends_on", 1, "required_sha256"), "0" * 64),
    ),
    (
        "trusted source digest mismatch",
        set_value(("depends_on", 1, "digest_match"), False),
    ),
    (
        "changed main theorem declaration",
        set_value(
            (
                "theorem_bindings",
                "frozenRecS17_iff_guardedProjectiveSystem_over",
                "declaration",
            ),
            "Ecdlp.FrozenProjectiveSemaev.approximate_guarded_system",
        ),
    ),
    (
        "hid native_decide trust",
        set_value(
            ("proof_status", "card_guardVar_fourteen"),
            "pure_kernel_checked",
        ),
    ),
    (
        "enabled solver",
        set_value(("producer_checks", "solver_executed"), True),
    ),
    (
        "authorized experiment",
        set_value(("terminal_disposition", "authorization"), "approved"),
    ),
    (
        "promoted route",
        set_value(("terminal_disposition", "route_effect"), "promoted"),
    ),
]


class SemanticFaultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))

    def test_canonical_document(self) -> None:
        validator.validate_document(copy.deepcopy(self.document))

    def test_exactly_26_semantic_faults(self) -> None:
        self.assertEqual(len(SEMANTIC_FAULTS), 26)
        self.assertEqual(len({name for name, _ in SEMANTIC_FAULTS}), 26)

    def test_exhaustive_f5_fixture(self) -> None:
        observed = validator.enumerate_f5_guard()
        self.assertEqual(observed["assignments"], 625)
        self.assertEqual(observed["solutions"], 120)
        self.assertEqual(observed["nonzero_pairs"], 24)
        self.assertEqual(observed["completion_counts"], {5})
        self.assertTrue(observed["infinity_allowed"])
        self.assertTrue(observed["zero_rejected"])

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
