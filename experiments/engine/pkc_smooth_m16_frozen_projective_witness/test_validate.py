#!/usr/bin/env python3
"""Rehashed semantic fault tests for the TASK-021 certificate."""

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
    "task021_independent_validator", VALIDATOR_PATH
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load TASK-021 validator")
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
    ("wrong artifact id", set_value(("artifact_id",), "TASK021-APPROX")),
    ("wrong schema", set_value(("schema_version",), 2)),
    ("solver kind", set_value(("kind",), "kernel_and_solver_certificate")),
    (
        "removed algebraic closure",
        set_value(("assumption_contract", "main_target"), "any Field K"),
    ),
    (
        "claimed base-field descent",
        set_value(
            ("assumption_contract", "witness_field"),
            "all witnesses descend to k",
        ),
    ),
    (
        "accepted zero pair",
        set_value(
            ("assumption_contract", "projective_domain"),
            "[0:0] is accepted",
        ),
    ),
    (
        "removed infinity",
        set_value(
            ("witness_chain_contract", "infinity_point_allowed"), False
        ),
    ),
    (
        "changed infinity point",
        set_value(("witness_chain_contract", "infinity_point"), "[0:1]"),
    ),
    (
        "allowed zero pair",
        set_value(("witness_chain_contract", "zero_pair_excluded"), False),
    ),
    (
        "changed C16 stage",
        set_value(("witness_chain_contract", "C16_stage"), 15),
    ),
    (
        "too few witnesses",
        set_value(
            (
                "witness_chain_contract",
                "internal_projective_witness_count_at_C16",
            ),
            13,
        ),
    ),
    (
        "too many witnesses",
        set_value(
            (
                "witness_chain_contract",
                "internal_projective_witness_count_at_C16",
            ),
            15,
        ),
    ),
    (
        "wrong last leaf",
        set_value(("witness_chain_contract", "leaf_index_end_at_C16"), 16),
    ),
    (
        "wrong successor index",
        set_value(
            ("witness_chain_contract", "successor_equation"),
            "exists z, Chain q s z and HValue z (q (s+3)) y = 0",
        ),
    ),
    (
        "wrong predecessor degree",
        set_value(
            (
                "projective_evaluation_contract",
                "predecessor_declared_degree",
            ),
            "2^s",
        ),
    ),
    (
        "deleted infinity fixture",
        delete_value(
            ("projective_evaluation_contract", "infinity_fixture_theorems", 1)
        ),
    ),
    (
        "wrong all-stage theorem",
        set_value(
            ("theorem_bindings", "all_stage_chain", "declaration"),
            "Ecdlp.FrozenProjectiveSemaev.approximate_chain",
        ),
    ),
    (
        "wrong C16 theorem source",
        set_value(
            ("theorem_bindings", "C16_chain", "source_path"),
            "Ecdlp/Proved/FrozenRecursiveProjectiveSemaev.lean",
        ),
    ),
    (
        "changed source digest",
        set_value(("depends_on", 2, "required_sha256"), "0" * 64),
    ),
    (
        "trusted digest mismatch",
        set_value(("depends_on", 2, "digest_match"), False),
    ),
    (
        "enabled solver",
        set_value(("producer_checks", "solver_executed"), True),
    ),
    (
        "enabled experiment",
        set_value(("producer_checks", "experiment_authorized"), True),
    ),
    (
        "materialized S17",
        set_value(("producer_checks", "S17_materialized"), True),
    ),
    (
        "promoted cost",
        set_value(("terminal_disposition", "cost_quantity_status"), "complete"),
    ),
    (
        "priced rank",
        set_value(("terminal_disposition", "rank_status"), "priced"),
    ),
    (
        "retained hypothesis",
        set_value(
            ("terminal_disposition", "retention_disposition"),
            "retained_for_execution",
        ),
    ),
    (
        "promoted route",
        set_value(("terminal_disposition", "route_effect"), "promoted"),
    ),
    (
        "claimed direct S17",
        set_value(("proof_status", "direct_S17_equivalence"), "kernel_checked"),
    ),
    (
        "claimed solving cost",
        set_value(
            ("proof_status", "solving_rank_yield_cost_claim"),
            "kernel_checked",
        ),
    ),
]


class SemanticFaultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))

    def test_canonical_document(self) -> None:
        validator.validate_document(copy.deepcopy(self.document))

    def test_all_semantic_faults_are_rejected(self) -> None:
        for name, mutation in SEMANTIC_FAULTS:
            with self.subTest(name=name):
                document = copy.deepcopy(self.document)
                mutation(document)
                with self.assertRaises(validator.ValidationError):
                    validator.validate_document(document)


if __name__ == "__main__":
    unittest.main(verbosity=2)
