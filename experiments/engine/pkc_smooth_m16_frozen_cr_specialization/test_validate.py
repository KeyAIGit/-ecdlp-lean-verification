#!/usr/bin/env python3
"""Rehashed semantic fault tests for the TASK-020 certificate."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from typing import Any, Callable


HERE = Path(__file__).resolve().parent
ARTIFACT_PATH = HERE / "artifact.json"
VALIDATOR_PATH = HERE / "validate.py"

SPEC = importlib.util.spec_from_file_location(
    "task020_independent_validator", VALIDATOR_PATH
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load TASK-020 validator")
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)

Document = dict[str, Any]
Mutation = Callable[[Document], None]
PathPart = str | int


def set_value(
    path: tuple[PathPart, ...], value: Any
) -> Mutation:
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


def append_value(
    path: tuple[PathPart, ...], value: Any
) -> Mutation:
    def mutate(document: Document) -> None:
        node: Any = document
        for part in path:
            node = node[part]
        node.append(copy.deepcopy(value))

    return mutate


def add_dependency_metadata(document: Document) -> None:
    document["depends_on"][0]["trusted_without_digest"] = True


def reorder_h_terms(document: Document) -> None:
    terms = document["h_literal"]["terms"]
    terms[0], terms[1] = terms[1], terms[0]


def reorder_matrix_with_same_determinant(document: Document) -> None:
    matrix = document["fixtures"]["F5_affine_intermediate_root"][
        "task_sylvester_matrix_over_Z"
    ]
    matrix[0], matrix[1] = matrix[1], matrix[0]
    matrix[2], matrix[3] = matrix[3], matrix[2]


SEMANTIC_FAULTS: list[tuple[str, Mutation]] = [
    (
        "wrong artifact id",
        set_value(
            ("artifact_id",),
            "PKC-SMOOTH-M16-FROZEN-CR-SPECIALIZATION-APPROX",
        ),
    ),
    ("changed schema", set_value(("schema_version",), 2)),
    (
        "broadened kind",
        set_value(("kind",), "kernel_and_solver_certificate"),
    ),
    (
        "deleted assumption contract",
        delete_value(("assumption_contract",)),
    ),
    (
        "removed explicit coefficient map",
        set_value(
            ("assumption_contract", "coefficient_map"),
            "an implicit map may be inferred",
        ),
    ),
    (
        "accepted irrelevant pair",
        set_value(
            ("assumption_contract", "projective_domain"),
            "all pairs including [0:0]",
        ),
    ),
    (
        "removed algebraic closure",
        set_value(
            ("assumption_contract", "common_root_target"),
            "any commutative ring",
        ),
    ),
    (
        "removed infinity branch",
        set_value(
            ("assumption_contract", "infinity_output"),
            "affine chart only",
        ),
    ),
    (
        "allowed degree reduction",
        set_value(
            ("assumption_contract", "normalization"),
            "actual degrees may replace formal degrees",
        ),
    ),
    (
        "shifted family index",
        set_value(
            ("frozen_family_contract", "family_index"),
            "frozenC R s = C_(s+3)",
        ),
    ),
    (
        "changed C16 index",
        set_value(
            ("frozen_family_contract", "C16_binding"),
            "frozenC R 15 = C16",
        ),
    ),
    (
        "changed base form",
        set_value(
            ("frozen_family_contract", "base"),
            "frozenC R 0 = C3",
        ),
    ),
    (
        "changed successor formula",
        set_value(
            ("frozen_family_contract", "successor"),
            "use actual-degree resultant",
        ),
    ),
    (
        "changed formal degrees",
        set_value(
            ("frozen_family_contract", "formal_degrees"),
            ["2^s", "2"],
        ),
    ),
    (
        "balanced topology",
        set_value(
            ("frozen_family_contract", "topology"),
            "balanced_tree",
        ),
    ),
    (
        "changed family unit",
        set_value(
            ("frozen_family_contract", "coefficient_unit"), -1
        ),
    ),
    (
        "dropped family infinity output",
        set_value(
            ("frozen_family_contract", "output_branches"), ["[y:1]"]
        ),
    ),
    (
        "changed minus 28 coefficient",
        set_value(
            ("h_literal", "terms", 8, "coefficient"), -27
        ),
    ),
    ("reordered H terms", reorder_h_terms),
    (
        "changed H monomial",
        set_value(
            ("h_literal", "terms", 6, "exponents"),
            [1, 1, 0, 2, 1, 1],
        ),
    ),
    (
        "changed H multidegree",
        set_value(("h_literal", "multidegree"), [2, 2, 3]),
    ),
    (
        "changed H term count",
        set_value(("h_literal", "term_count"), 8),
    ),
    (
        "swapped Sylvester arguments",
        set_value(
            ("literal_sylvester_contract", "argument_order"),
            "(right,left,2,m)",
        ),
    ),
    (
        "reversed coefficient order",
        set_value(
            ("literal_sylvester_contract", "coefficient_order"),
            "ascending eliminated-coordinate degree",
        ),
    ),
    (
        "swapped row blocks",
        set_value(
            ("literal_sylvester_contract", "row_order"),
            "right rows then left rows",
        ),
    ),
    (
        "allowed formal degree reduction",
        set_value(
            (
                "literal_sylvester_contract",
                "formal_degree_reduction",
            ),
            "allowed",
        ),
    ),
    (
        "allowed content normalization",
        set_value(
            (
                "literal_sylvester_contract",
                "primitive_part_or_content_division",
            ),
            "allowed",
        ),
    ),
    (
        "allowed monic normalization",
        set_value(
            ("literal_sylvester_contract", "monic_normalization"),
            "allowed",
        ),
    ),
    (
        "changed literal determinant unit",
        set_value(
            (
                "literal_sylvester_contract",
                "literal_coefficient_unit",
            ),
            -1,
        ),
    ),
    (
        "corrupted frozen source digest",
        set_value(
            ("depends_on", 2, "required_sha256"), "0" * 64
        ),
    ),
    ("added dependency metadata", add_dependency_metadata),
    (
        "renamed frozen family definition",
        set_value(
            (
                "theorem_bindings",
                "actual_frozen_family",
                "declaration",
            ),
            "Ecdlp.FrozenProjectiveSemaev.frozenCApprox",
        ),
    ),
    (
        "renamed degree theorem",
        set_value(
            (
                "theorem_bindings",
                "universal_output_degree_bound",
                "declaration",
            ),
            "Ecdlp.FrozenProjectiveSemaev."
            "previousSliceAtOver_frozenC_natDegree_lt",
        ),
    ),
    (
        "renamed common-root theorem",
        set_value(
            (
                "theorem_bindings",
                "unconditional_mapped_one_step_common_root",
                "declaration",
            ),
            "Ecdlp.FrozenProjectiveSemaev."
            "specialize_frozenC_succ_over_eq_zero_implies_root",
        ),
    ),
    (
        "changed theorem source shape",
        set_value(
            (
                "theorem_bindings",
                "coefficient_map_specialization",
                "source_shape",
            ),
            "def",
        ),
    ),
    (
        "marked build unchecked",
        set_value(
            ("kernel_contract", "build_status"),
            "source_present_unchecked",
        ),
    ),
    (
        "allowed sorry axiom",
        append_value(
            ("kernel_contract", "allowed_axioms"), "sorryAx"
        ),
    ),
    (
        "cleared forbidden axioms",
        set_value(("kernel_contract", "forbidden_axioms"), []),
    ),
    (
        "validator invokes Lean",
        set_value(("kernel_contract", "validator_invokes_lean"), True),
    ),
    (
        "specialization made conditional",
        set_value(
            ("proof_status", "coefficient_map_specialization"),
            "conditional",
        ),
    ),
    (
        "degree bound made conditional",
        set_value(
            ("proof_status", "universal_output_degree_bound"),
            "conditional",
        ),
    ),
    (
        "one-step root made conditional",
        set_value(
            (
                "proof_status",
                "unconditional_one_step_common_projective_root",
            ),
            "conditional_on_degree_bound",
        ),
    ),
    (
        "claimed direct S17 equivalence",
        set_value(
            ("proof_status", "direct_S17_equivalence"),
            "kernel_checked",
        ),
    ),
    (
        "closed reverse induction",
        set_value(
            (
                "proof_status",
                "universal_C16_to_C2_reverse_induction",
            ),
            "kernel_checked",
        ),
    ),
    (
        "changed C16 output bound",
        set_value(
            (
                "recurrence_schedule",
                "stage_rows",
                14,
                "output_degree_bound",
            ),
            32767,
        ),
    ),
    (
        "deleted a stage",
        delete_value(("recurrence_schedule", "stage_rows", 7)),
    ),
    (
        "changed final left degree",
        set_value(
            (
                "recurrence_schedule",
                "successor_rows",
                13,
                "left_formal_degree",
            ),
            8192,
        ),
    ),
    (
        "changed final Sylvester size",
        set_value(
            (
                "recurrence_schedule",
                "successor_rows",
                13,
                "sylvester_size",
            ),
            16385,
        ),
    ),
    (
        "changed constant row count",
        set_value(
            (
                "recurrence_schedule",
                "successor_rows",
                5,
                "weight_zero_row_count",
            ),
            1,
        ),
    ),
    (
        "changed quadratic row count",
        set_value(
            (
                "recurrence_schedule",
                "successor_rows",
                5,
                "weight_two_row_count",
            ),
            63,
        ),
    ),
    (
        "changed degree row sum",
        set_value(
            (
                "recurrence_schedule",
                "successor_rows",
                5,
                "row_degree_sum",
            ),
            127,
        ),
    ),
    (
        "corrupted affine coefficients",
        set_value(
            (
                "fixtures",
                "F5_affine_intermediate_root",
                "right_coefficients_descending_over_Z",
                1,
            ),
            -39,
        ),
    ),
    (
        "moved affine witness to infinity",
        set_value(
            (
                "fixtures",
                "F5_affine_intermediate_root",
                "distinguished_witness",
            ),
            [1, 0],
        ),
    ),
    (
        "deleted infinity root",
        set_value(
            (
                "fixtures",
                "F5_infinity_intermediate_root",
                "common_projective_roots_mod_5",
            ),
            [],
        ),
    ),
    (
        "reduced infinity formal degrees",
        set_value(
            (
                "fixtures",
                "F5_infinity_intermediate_root",
                "formal_degrees",
            ),
            [1, 1],
        ),
    ),
    (
        "reordered matrix with same determinant",
        reorder_matrix_with_same_determinant,
    ),
    (
        "zeroed nonzero control",
        set_value(
            (
                "fixtures",
                "F5_minus_28_nonzero_control",
                "mapped_resultant_mod_5",
            ),
            0,
        ),
    ),
    (
        "corrupted minus 28 counterfactual",
        set_value(
            (
                "fixtures",
                "F5_minus_28_nonzero_control",
                "zeroed_minus_28_resultant_mod_5",
            ),
            3,
        ),
    ),
    (
        "removed infinity fixture",
        delete_value(("fixtures", "F5_infinity_intermediate_root")),
    ),
    (
        "closed exact blocker",
        set_value(("open_exact_blocker", "status"), "closed"),
    ),
    (
        "removed reverse downstream blocker",
        set_value(
            ("open_exact_blocker", "downstream_open"),
            ["RecS17_iff_GeoCat"],
        ),
    ),
    (
        "materialized S17",
        set_value(("producer_checks", "S17_materialized"), True),
    ),
    (
        "expanded C16",
        set_value(("producer_checks", "C16_expanded"), True),
    ),
    (
        "executed normalization",
        set_value(
            ("producer_checks", "normalization_executed"), True
        ),
    ),
    (
        "executed solver",
        set_value(("producer_checks", "solver_executed"), True),
    ),
    (
        "authorized experiment",
        set_value(
            ("producer_checks", "experiment_authorized"), True
        ),
    ),
    (
        "allowed characteristic seven",
        set_value(
            ("scope", "characteristic_seven_transfer"), "allowed"
        ),
    ),
    (
        "removed solver exclusion",
        delete_value(("scope", "excluded", 5)),
    ),
    (
        "granted terminal authorization",
        set_value(("terminal_disposition", "authorization"), "execute"),
    ),
    (
        "closed barrier",
        set_value(
            ("terminal_disposition", "barrier_effect"), "closed"
        ),
    ),
    (
        "promoted route",
        set_value(("terminal_disposition", "route_effect"), "promote"),
    ),
    (
        "completed cost",
        set_value(
            ("terminal_disposition", "cost_quantity_status"),
            "complete",
        ),
    ),
    (
        "removed remaining blocker",
        set_value(
            ("terminal_disposition", "remaining_blocker"), "none"
        ),
    ),
]


def canonical_bytes(document: Document) -> bytes:
    return (
        json.dumps(
            document, ensure_ascii=False, indent=2, sort_keys=True
        )
        + "\n"
    ).encode("utf-8")


def write_case(
    directory: Path, document: Document, stale_hash: bool = False
) -> tuple[Path, Path]:
    artifact_path = directory / "artifact.json"
    hash_path = directory / "artifact.sha256"
    payload = canonical_bytes(document)
    artifact_path.write_bytes(payload)
    digest = "0" * 64 if stale_hash else hashlib.sha256(payload).hexdigest()
    hash_path.write_text(
        f"{digest}  artifact.json\n", encoding="ascii"
    )
    return artifact_path, hash_path


class ValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.base_document = json.loads(
            ARTIFACT_PATH.read_text(encoding="utf-8")
        )

    def test_base_certificate(self) -> None:
        failures = validator.validate(
            ARTIFACT_PATH, HERE / "artifact.sha256"
        )
        self.assertEqual(failures, [])

    def test_stale_sidecar_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            artifact, digest = write_case(
                Path(temporary), self.base_document, stale_hash=True
            )
            failures = validator.validate(artifact, digest)
        self.assertTrue(
            any("artifact.sha256" in failure for failure in failures)
        )

    def test_all_rehashed_semantic_faults_are_rejected(self) -> None:
        for name, mutate in SEMANTIC_FAULTS:
            with self.subTest(name=name):
                document = copy.deepcopy(self.base_document)
                mutate(document)
                with tempfile.TemporaryDirectory() as temporary:
                    artifact, digest = write_case(
                        Path(temporary), document
                    )
                    failures = validator.validate(artifact, digest)
                self.assertTrue(
                    failures,
                    f"validator accepted semantic fault: {name}",
                )


if __name__ == "__main__":
    unittest.main()
