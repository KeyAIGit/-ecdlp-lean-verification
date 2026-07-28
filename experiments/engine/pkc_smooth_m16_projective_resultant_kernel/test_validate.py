#!/usr/bin/env python3
"""Rehashed semantic fault tests for the independent TASK-019 validator."""

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
    "task019_independent_validator", VALIDATOR_PATH
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load TASK-019 validator")
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)

Document = dict[str, Any]
Mutation = Callable[[Document], None]


def wrong_artifact_id(document: Document) -> None:
    document["artifact_id"] = "PKC-SMOOTH-M16-PROJECTIVE-RESULTANT-001"


def broaden_kind(document: Document) -> None:
    document["kind"] = "kernel_and_recursive_success_certificate"


def remove_positive_degrees(document: Document) -> None:
    document["assumption_contract"]["formal_degrees"] = "m,n arbitrary"


def remove_degree_bounds(document: Document) -> None:
    document["assumption_contract"]["degree_bounds"] = "none"


def exclude_zero_forms(document: Document) -> None:
    document["assumption_contract"]["zero_forms"] = "f!=0 and g!=0"


def accept_irrelevant_pair(document: Document) -> None:
    document["assumption_contract"]["projective_domain"] = (
        "all pairs, including [0:0]"
    )


def replace_projective_or_by_and(document: Document) -> None:
    document["assumption_contract"]["projective_domain"] = (
        "a witness pair (U,V) satisfies U!=0 and V!=0"
    )


def reduce_formal_degree(document: Document) -> None:
    document["literal_convention_binding"][
        "formal_degree_reduction"
    ] = "allowed"


def allow_content_normalization(document: Document) -> None:
    document["literal_convention_binding"][
        "primitive_part_or_content_division"
    ] = "allowed"


def allow_monic_normalization(document: Document) -> None:
    document["literal_convention_binding"]["monic_normalization"] = (
        "allowed"
    )


def reverse_coefficient_order(document: Document) -> None:
    document["literal_convention_binding"]["task_coefficient_order"] = (
        "ascending U degree"
    )


def swap_arguments(document: Document) -> None:
    document["literal_convention_binding"]["argument_order"] = (
        "(g,f,n,m)"
    )


def swap_row_blocks(document: Document) -> None:
    document["literal_convention_binding"]["task_row_order"] = (
        "first m shifted rows of g, then n shifted rows of f"
    )


def drop_axis_reversal(document: Document) -> None:
    document["literal_convention_binding"]["mathlib_relation"] = (
        "taskSylvester=transpose(Polynomial.sylvester)"
    )


def change_unit(document: Document) -> None:
    document["literal_convention_binding"]["literal_coefficient_unit"] = -1


def corrupt_source_digest(document: Document) -> None:
    document["depends_on"][2]["required_sha256"] = "0" * 64
    document["depends_on"][2]["observed_sha256"] = "0" * 64


def add_dependency_metadata(document: Document) -> None:
    document["depends_on"][0]["trusted_without_digest"] = True


def rename_main_theorem(document: Document) -> None:
    document["theorem_bindings"]["fixed_degree_common_root"][
        "declaration"
    ] += "_approx"


def rename_end_to_end_theorem(document: Document) -> None:
    document["theorem_bindings"]["literal_end_to_end_common_root"][
        "declaration"
    ] += "_missing"


def inject_sorry_axiom(document: Document) -> None:
    document["kernel_contract"]["allowed_axioms"].append("sorryAx")
    document["kernel_contract"]["forbidden_axioms"] = []


def mark_kernel_unchecked(document: Document) -> None:
    document["kernel_contract"]["build_status"] = "source_present_unchecked"


def mutate_infinity_resultant(document: Document) -> None:
    document["fixtures"]["F5_degree_drop_infinity"][
        "fixed_resultant_mod_p"
    ] = 1


def delete_infinity_witness(document: Document) -> None:
    document["fixtures"]["F5_degree_drop_infinity"][
        "distinguished_witness"
    ] = [0, 0]


def reduce_infinity_fixture_degrees(document: Document) -> None:
    fixture = document["fixtures"]["F5_degree_drop_infinity"]
    fixture["formal_degrees"] = [1, 1]
    fixture["left_coefficients_descending"] = [2, 0]
    fixture["right_coefficients_descending"] = [4, 3]


def mutate_reduced_resultant(document: Document) -> None:
    document["fixtures"]["F5_degree_drop_infinity"][
        "reduced_affine_control"
    ]["resultant_mod_5"] = 0


def promote_one_sided_drop_to_zero(document: Document) -> None:
    document["fixtures"]["F5_one_sided_drop_no_root"][
        "fixed_resultant_mod_p"
    ] = 0


def remove_zero_left(document: Document) -> None:
    document["fixtures"].pop("F5_zero_left")


def remove_zero_right(document: Document) -> None:
    document["fixtures"].pop("F5_zero_right")


def remove_zero_both(document: Document) -> None:
    document["fixtures"].pop("F5_zero_both")


def move_affine_witness_to_infinity(document: Document) -> None:
    document["fixtures"]["F5_affine_output"][
        "distinguished_witness"
    ] = [1, 0]


def corrupt_affine_coefficients(document: Document) -> None:
    document["fixtures"]["F5_affine_output"][
        "right_coefficients_descending"
    ][1] = 2


def row_fixture_checks_only_determinant(document: Document) -> None:
    fixture = document["fixtures"]["F5_recurrence_row_order"]
    fixture["row_order_check"] = "determinant_only"


def mutate_row_fixture_matrix_same_det(document: Document) -> None:
    fixture = document["fixtures"]["F5_recurrence_row_order"]
    matrix = fixture["task_sylvester_matrix"]
    fixture["task_sylvester_matrix"] = matrix[2:] + matrix[:2]


def corrupt_odd_unit_control(document: Document) -> None:
    document["fixtures"]["F5_odd_convention_control"][
        "negative_unit_result_mod_5"
    ] = 1


def corrupt_specialization_polynomial(document: Document) -> None:
    document["fixtures"]["F5_specialization_to_infinity"][
        "resultant_polynomial_ascending_s_over_Z"
    ][1] = -11


def corrupt_specialization_value(document: Document) -> None:
    document["fixtures"]["F5_specialization_to_infinity"]["values"]["0"][
        "resultant_mod_5"
    ] = 1


def delete_specialization_infinity(document: Document) -> None:
    document["fixtures"]["F5_specialization_to_infinity"]["values"].pop(
        "0"
    )


def call_fixture_a_recursive_theorem(document: Document) -> None:
    document["fixtures"]["F5_specialization_to_infinity"][
        "recursive_claim_status"
    ] = "kernel_checked_Cr_specialization"


def close_recursive_specialization(document: Document) -> None:
    document["proof_status"]["recursive_Cr_specialization"] = (
        "kernel_checked"
    )


def close_universal_reverse(document: Document) -> None:
    document["proof_status"]["universal_reverse_C16_to_C2"] = (
        "kernel_checked"
    )


def close_exact_blocker(document: Document) -> None:
    document["open_exact_blocker"]["status"] = "closed"


def claim_generic_c16(document: Document) -> None:
    document["open_exact_blocker"]["downstream_open"].remove(
        "generic_C16_forward"
    )


def allow_characteristic_seven(document: Document) -> None:
    document["scope"]["characteristic_seven_transfer"] = "allowed"


def materialize_s17(document: Document) -> None:
    document["producer_checks"]["S17_materialized"] = True
    document["producer_checks"]["C16_expanded"] = True


def execute_solver(document: Document) -> None:
    document["producer_checks"]["solver_executed"] = True


def authorize_experiment(document: Document) -> None:
    document["producer_checks"]["experiment_authorized"] = True
    document["terminal_disposition"]["authorization"] = "experiment"


def complete_cost_and_promote(document: Document) -> None:
    terminal = document["terminal_disposition"]
    terminal["cost_quantity_status"] = "complete"
    terminal["rank_status"] = "priced"
    terminal["yield_status"] = "priced"
    terminal["solving_cost_status"] = "priced"
    terminal["route_effect"] = "promoted"


SEMANTIC_FAULTS: list[tuple[str, Mutation]] = [
    ("wrong artifact id", wrong_artifact_id),
    ("broadened kind", broaden_kind),
    ("removed positive degrees", remove_positive_degrees),
    ("removed degree bounds", remove_degree_bounds),
    ("excluded zero forms", exclude_zero_forms),
    ("accepted irrelevant pair", accept_irrelevant_pair),
    ("replaced projective or by and", replace_projective_or_by_and),
    ("reduced formal degree", reduce_formal_degree),
    ("allowed content normalization", allow_content_normalization),
    ("allowed monic normalization", allow_monic_normalization),
    ("reversed coefficient order", reverse_coefficient_order),
    ("swapped arguments", swap_arguments),
    ("swapped row blocks", swap_row_blocks),
    ("dropped axis reversal", drop_axis_reversal),
    ("changed literal unit", change_unit),
    ("corrupted source digest", corrupt_source_digest),
    ("added dependency metadata", add_dependency_metadata),
    ("renamed main theorem", rename_main_theorem),
    ("renamed end-to-end theorem", rename_end_to_end_theorem),
    ("injected sorry axiom", inject_sorry_axiom),
    ("marked kernel unchecked", mark_kernel_unchecked),
    ("mutated infinity resultant", mutate_infinity_resultant),
    ("deleted infinity witness", delete_infinity_witness),
    ("reduced infinity degrees", reduce_infinity_fixture_degrees),
    ("mutated reduced resultant", mutate_reduced_resultant),
    ("promoted one-sided drop", promote_one_sided_drop_to_zero),
    ("removed zero-left case", remove_zero_left),
    ("removed zero-right case", remove_zero_right),
    ("removed both-zero case", remove_zero_both),
    ("moved affine witness to infinity", move_affine_witness_to_infinity),
    ("corrupted affine coefficients", corrupt_affine_coefficients),
    ("row fixture determinant only", row_fixture_checks_only_determinant),
    ("mutated row matrix same det", mutate_row_fixture_matrix_same_det),
    ("corrupted odd unit control", corrupt_odd_unit_control),
    ("corrupted specialization polynomial", corrupt_specialization_polynomial),
    ("corrupted specialization value", corrupt_specialization_value),
    ("deleted infinity specialization", delete_specialization_infinity),
    ("called fixture recursive theorem", call_fixture_a_recursive_theorem),
    ("closed recursive specialization", close_recursive_specialization),
    ("closed universal reverse", close_universal_reverse),
    ("closed exact blocker", close_exact_blocker),
    ("claimed generic C16", claim_generic_c16),
    ("allowed characteristic seven", allow_characteristic_seven),
    ("materialized S17", materialize_s17),
    ("executed solver", execute_solver),
    ("authorized experiment", authorize_experiment),
    ("completed cost and promoted", complete_cost_and_promote),
]


def write_case(
    directory: Path, document: Document, stale_hash: bool = False
) -> tuple[Path, Path]:
    artifact_path = directory / "artifact.json"
    hash_path = directory / "artifact.sha256"
    payload = validator.canonical_bytes(document)
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
