#!/usr/bin/env python3
"""Rehashed semantic fault tests for the independent TASK-018 validator."""

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
    "task018_independent_validator", VALIDATOR_PATH
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load TASK-018 validator")
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)

Document = dict[str, Any]
Mutation = Callable[[Document], None]


def wrong_artifact_id(document: Document) -> None:
    document["artifact_id"] = "PKC-SMOOTH-M16-PROJECTIVE-BRIDGE-001"


def broaden_artifact_kind(document: Document) -> None:
    document["kind"] += "_experimentally_validated"


def mutate_h(document: Document) -> None:
    document["frozen_definition"]["H_polynomial"] = (
        document["frozen_definition"]["H_polynomial"].replace("28*(", "27*(")
    )


def reduce_final_degree(document: Document) -> None:
    document["degree_schedule"]["rows"][-1][
        "output_projective_degree"
    ] = 16_384
    document["degree_schedule"]["C16_multidegree_each_external_pair"] = 16_384


def allow_formal_degree_reduction(document: Document) -> None:
    document["coefficient_and_sylvester_convention"][
        "formal_degree_reduction"
    ] = "allowed"


def allow_content_division(document: Document) -> None:
    document["coefficient_and_sylvester_convention"][
        "primitive_part_or_content_division"
    ] = "allowed"


def reverse_binary_coefficient_order(document: Document) -> None:
    document["coefficient_and_sylvester_convention"][
        "binary_form_coefficients"
    ] = (
        "F(U,V) is stored in ascending U degree as "
        "[f_m,...,f_0]"
    )


def swap_sylvester_row_blocks(document: Document) -> None:
    document["coefficient_and_sylvester_convention"]["sylvester_rows"] = (
        "rows 0..m-1 are shifted copies of G; remaining rows are F"
    )


def swap_resultant_arguments(document: Document) -> None:
    document["coefficient_and_sylvester_convention"]["hRes_definition"] = (
        "hRes_T^(m,n)(F,G)=det(Syl_(n,m)(G(t,1),F(t,1)))"
    )


def corrupt_swap_rule(document: Document) -> None:
    document["coefficient_and_sylvester_convention"]["swap_rule"] = (
        "hRes(F,G)=hRes(G,F)"
    )


def wrong_final_formal_degrees(document: Document) -> None:
    document["degree_schedule"]["rows"][-1][
        "previous_formal_degree_in_T"
    ] = 8_192
    document["degree_schedule"]["rows"][-1][
        "resultant_formal_degrees"
    ] = [8_192, 2]
    document["degree_schedule"][
        "C16_final_resultant_formal_degrees"
    ] = [8_192, 2]


def wrong_external_pair_count(document: Document) -> None:
    document["degree_schedule"]["C16_external_coordinate_pair_count"] = 18


def allow_monic_normalization(document: Document) -> None:
    document["coefficient_and_sylvester_convention"][
        "monic_normalization"
    ] = "allowed"


def change_literal_coefficient_unit(document: Document) -> None:
    document["coefficient_and_sylvester_convention"][
        "literal_coefficient_unit"
    ] = -1


def broaden_literal_unit_scope(document: Document) -> None:
    document["coefficient_and_sylvester_convention"][
        "literal_unit_scope"
    ] = "coefficient unit 1 under every ordering and normalization"


def erase_projective_rescaling_degree(document: Document) -> None:
    document["coefficient_and_sylvester_convention"][
        "projective_rescaling_rule"
    ] = "projective rescaling leaves every coefficient unchanged"


def allow_coordinate_difference_saturation(document: Document) -> None:
    irrelevant = document["frozen_definition"][
        "irrelevant_ideal_exclusion"
    ]
    irrelevant["forbidden_extra_saturands"].remove(
        "coordinate differences"
    )
    irrelevant["only_allowed_set_theoretic_saturation"] += (
        " times all coordinate differences"
    )


def replace_only_allowed_saturation(document: Document) -> None:
    document["frozen_definition"]["irrelevant_ideal_exclusion"][
        "only_allowed_set_theoretic_saturation"
    ] = "coordinate differences"


def reverse_first_coordinate_pair(document: Document) -> None:
    document["frozen_definition"]["coordinate_order"][0] = "Q1=[Z1:X1]"


def erase_recs17_definition(document: Document) -> None:
    document["predicate_boundaries"]["RecS17_k"]["definition"] = "1=0"


def append_contradictory_unconditional_recover(document: Document) -> None:
    document["predicate_boundaries"]["base_field_relations"][
        "unconditional"
    ] = ["RecS17_Fp implies Recover_Fp"]


def overclaim_scope_equivalence(document: Document) -> None:
    document["scope"]["included"].append(
        "exact universal RecS17_k iff GeoCat_kbar equivalence"
    )


def grant_experiment_in_scope_exclusion(document: Document) -> None:
    document["scope"]["excluded"][-1] = "experiment authorization granted"


def remove_tangent_stratum(document: Document) -> None:
    document["predicate_boundaries"]["strata"].pop(
        "tangent_or_repeated_input"
    )


def remove_duplicate_stratum(document: Document) -> None:
    document["predicate_boundaries"]["strata"].pop(
        "duplicate_coordinates_or_roots"
    )


def remove_two_torsion_stratum(document: Document) -> None:
    document["predicate_boundaries"]["strata"].pop(
        "rational_two_torsion"
    )


def mutate_infinity_resultant(document: Document) -> None:
    fixture = document["fixtures"]["F5_fixed_vs_reduced_infinity"]
    fixture["fixed_resultant_mod_5"] = 1


def delete_identity_infinity(document: Document) -> None:
    fixture = document["fixtures"]["F5_fixed_vs_reduced_infinity"]
    fixture["required_disposition"] = "discard_leading_zero"


def mutate_extension_coefficients(document: Document) -> None:
    fixture = document["fixtures"]["F5_F25_extension_only_nonlift"]
    fixture["left_C3_S4_coefficients_descending_T"][2] = 1


def mutate_fixture_formal_degree(document: Document) -> None:
    document["fixtures"]["F5_F25_extension_only_nonlift"][
        "C4_S5_formal_resultant_degrees"
    ] = [3, 2]


def mutate_exact_division_remainder(document: Document) -> None:
    document["fixtures"]["F5_F25_extension_only_nonlift"][
        "exact_division_remainder"
    ] = [1]


def mark_f5_quadratic_reducible(document: Document) -> None:
    document["fixtures"]["F5_F25_extension_only_nonlift"][
        "right_quadratic_irreducible_over_F5"
    ] = False


def misclassify_combined_nonlift(document: Document) -> None:
    fixture = document["fixtures"]["F5_F25_extension_only_nonlift"]
    fixture["required_disposition"] = "INTERNAL_EXTENSION_ONLY"
    fixture["combined_boundary"] = "all external coordinates lift"


def promote_recover_fixture(document: Document) -> None:
    document["fixtures"]["F5_F25_extension_only_nonlift"][
        "predicate_values"
    ]["Recover_F5"] = True


def mutate_f25_tree_witness(document: Document) -> None:
    witness = document["fixtures"]["F5_F25_extension_only_nonlift"][
        "chosen_tree_witness"
    ]
    witness["W3"]["U"] = {"constant": 1, "alpha": 0}
    witness["vertex_values"]["H_W2_Q3_W3"] = {
        "constant": 1,
        "alpha": 0,
    }


def mutate_exhaustive_count(document: Document) -> None:
    document["fixtures"]["bounded_exhaustive_S5"]["F11"]["counts"][
        "recursive_zero_count"
    ] += 1


def mutate_exhaustive_stream(document: Document) -> None:
    document["fixtures"]["bounded_exhaustive_S5"]["F13"][
        "enumeration_stream_sha256"
    ] = "0" * 64


def claim_generic_forward_computational_replay(document: Document) -> None:
    document["producer_checks"][
        "generic_C16_forward_computationally_replayed"
    ] = True


def claim_generic_forward_kernel_check(document: Document) -> None:
    document["producer_checks"]["generic_C16_forward_kernel_checked"] = True


def mutate_producer_f13_mismatch_summary(document: Document) -> None:
    document["producer_checks"]["F13_base_lift_mismatch_count"] = 1


def claim_universal_reverse(document: Document) -> None:
    contract = document["predicate_boundaries"][
        "algebraic_closure_projection_contract"
    ]
    contract["reverse_status"] = "proved"
    contract["equivalence"] = "RecS17_k iff GeoCat_kbar"
    contract["claim_level"] = "exact_set_theoretic"


def relabel_universal_forward_as_replayed(document: Document) -> None:
    contract = document["predicate_boundaries"][
        "algebraic_closure_projection_contract"
    ]
    contract["forward_status"] = "frozen_and_replayed"
    contract["forward"] = "generic C16 forward implication replayed exactly"


def remove_specialization_obligation(document: Document) -> None:
    contract = document["predicate_boundaries"][
        "algebraic_closure_projection_contract"
    ]
    contract["missing_lemma"] = "none"
    contract["reverse"] = "proved by the finite fixtures"


def promote_base_field_reverse(document: Document) -> None:
    relations = document["predicate_boundaries"]["base_field_relations"]
    relations["unconditional"] = ["RecS17_Fp implies RatCat_Fp"]


def drop_identity_stratum(document: Document) -> None:
    document["predicate_boundaries"]["strata"][
        "identity_or_infinity"
    ] = "discard"


def accept_invalid_projective_pair(document: Document) -> None:
    document["predicate_boundaries"]["strata"][
        "invalid_projective_pair_0_0"
    ] = "retain"


def degrade_assurance(document: Document) -> None:
    document["terminal_disposition"]["assurance"] = "self_asserted"


def overclaim_source_independence(document: Document) -> None:
    document["terminal_disposition"]["source_independence"] = "established"


def claim_experimental_calibration(document: Document) -> None:
    document["terminal_disposition"]["calibration"] = "experimental"


def price_cost_rank_and_yield(document: Document) -> None:
    terminal = document["terminal_disposition"]
    terminal["cost_quantity_status"] = "complete"
    terminal["solving_cost_status"] = "priced"
    terminal["rank_status"] = "priced"
    terminal["yield_status"] = "priced"


def authorize_execution(document: Document) -> None:
    terminal = document["terminal_disposition"]
    terminal["authorization"] = "experiment"
    terminal["experiment_permission"] = "granted"
    document["producer_checks"]["experiment_authorized"] = True


def promote_route_and_hypothesis(document: Document) -> None:
    terminal = document["terminal_disposition"]
    terminal["route_effect"] = "promoted"
    terminal["hypothesis_effect"] = "retained"
    terminal["retention_disposition"] = "one_retained"


def materialize_s17(document: Document) -> None:
    document["frozen_definition"]["literal_materialization"][
        "C16_expanded"
    ] = True
    document["producer_checks"]["C16_expanded"] = True
    document["producer_checks"]["S17_materialized"] = True


def remove_kernel_obligation(document: Document) -> None:
    document["unresolved_fields"] = [
        value
        for value in document["unresolved_fields"]
        if "kernel-checked fixed-degree projective resultant" not in value
    ]


def corrupt_dependency_digest(document: Document) -> None:
    dependency = document["depends_on"][0]
    dependency["observed_sha256"] = "0" * 64
    dependency["digest_match"] = False


def add_dependency_metadata(document: Document) -> None:
    document["depends_on"][0]["trusted_without_digest"] = True


def add_unregistered_bounded_field(document: Document) -> None:
    document["fixtures"]["bounded_exhaustive_S5"]["F17"] = copy.deepcopy(
        document["fixtures"]["bounded_exhaustive_S5"]["F13"]
    )


SEMANTIC_FAULTS: list[tuple[str, Mutation]] = [
    ("wrong artifact id", wrong_artifact_id),
    ("broadened artifact kind", broaden_artifact_kind),
    ("mutated H", mutate_h),
    ("reduced final degree", reduce_final_degree),
    ("allowed formal-degree reduction", allow_formal_degree_reduction),
    ("allowed content division", allow_content_division),
    ("reversed binary coefficient order", reverse_binary_coefficient_order),
    ("swapped Sylvester row blocks", swap_sylvester_row_blocks),
    ("swapped resultant arguments", swap_resultant_arguments),
    ("corrupted resultant swap rule", corrupt_swap_rule),
    ("wrong final formal degrees", wrong_final_formal_degrees),
    ("wrong external pair count", wrong_external_pair_count),
    ("allowed monic normalization", allow_monic_normalization),
    ("changed literal coefficient unit", change_literal_coefficient_unit),
    ("broadened literal unit scope", broaden_literal_unit_scope),
    (
        "erased projective rescaling degree",
        erase_projective_rescaling_degree,
    ),
    (
        "allowed coordinate-difference saturation",
        allow_coordinate_difference_saturation,
    ),
    ("replaced only allowed saturation", replace_only_allowed_saturation),
    ("reversed first coordinate pair", reverse_first_coordinate_pair),
    ("erased RecS17 definition", erase_recs17_definition),
    (
        "appended contradictory unconditional Recover",
        append_contradictory_unconditional_recover,
    ),
    ("overclaimed scope equivalence", overclaim_scope_equivalence),
    (
        "granted experiment in scope exclusion",
        grant_experiment_in_scope_exclusion,
    ),
    ("removed tangent stratum", remove_tangent_stratum),
    ("removed duplicate stratum", remove_duplicate_stratum),
    ("removed two-torsion stratum", remove_two_torsion_stratum),
    ("mutated infinity resultant", mutate_infinity_resultant),
    ("deleted identity infinity", delete_identity_infinity),
    ("mutated extension coefficients", mutate_extension_coefficients),
    ("mutated fixture formal degree", mutate_fixture_formal_degree),
    ("mutated exact division remainder", mutate_exact_division_remainder),
    ("marked F5 quadratic reducible", mark_f5_quadratic_reducible),
    ("misclassified combined nonlift", misclassify_combined_nonlift),
    ("promoted Recover fixture", promote_recover_fixture),
    ("mutated F25 tree witness", mutate_f25_tree_witness),
    ("mutated exhaustive count", mutate_exhaustive_count),
    ("mutated exhaustive stream", mutate_exhaustive_stream),
    (
        "claimed generic forward computational replay",
        claim_generic_forward_computational_replay,
    ),
    (
        "claimed generic forward kernel check",
        claim_generic_forward_kernel_check,
    ),
    (
        "mutated producer F13 mismatch summary",
        mutate_producer_f13_mismatch_summary,
    ),
    ("claimed universal reverse", claim_universal_reverse),
    (
        "relabeled universal forward as replayed",
        relabel_universal_forward_as_replayed,
    ),
    ("removed specialization obligation", remove_specialization_obligation),
    ("promoted base-field reverse", promote_base_field_reverse),
    ("dropped identity stratum", drop_identity_stratum),
    ("accepted invalid projective pair", accept_invalid_projective_pair),
    ("degraded assurance", degrade_assurance),
    ("overclaimed source independence", overclaim_source_independence),
    ("claimed experimental calibration", claim_experimental_calibration),
    ("priced cost rank yield", price_cost_rank_and_yield),
    ("authorized execution", authorize_execution),
    ("promoted route and hypothesis", promote_route_and_hypothesis),
    ("materialized S17", materialize_s17),
    ("removed kernel obligation", remove_kernel_obligation),
    ("corrupted dependency digest", corrupt_dependency_digest),
    ("added dependency metadata", add_dependency_metadata),
    ("added unregistered bounded field", add_unregistered_bounded_field),
]


class ValidatorFaultInjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.baseline = json.loads(ARTIFACT_PATH.read_bytes())

    def validate_temporary(self, document: Document) -> list[str]:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = root / "artifact.json"
            sidecar = root / "artifact.sha256"
            payload = validator.canonical_bytes(document)
            artifact.write_bytes(payload)
            digest = hashlib.sha256(payload).hexdigest()
            sidecar.write_text(
                f"{digest}  artifact.json\n", encoding="ascii"
            )
            return validator.validate_document(
                json.loads(payload), payload, sidecar
            )

    def test_committed_artifact_passes(self) -> None:
        self.assertEqual([], self.validate_temporary(self.baseline))

    def test_fault_catalog_is_unique(self) -> None:
        names = [name for name, _ in SEMANTIC_FAULTS]
        self.assertEqual(57, len(names))
        self.assertEqual(len(names), len(set(names)))

    def test_stale_sidecar_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = validator.canonical_bytes(self.baseline)
            sidecar = root / "artifact.sha256"
            sidecar.write_text(
                f"{'0' * 64}  artifact.json\n", encoding="ascii"
            )
            failures = validator.validate_document(
                json.loads(payload), payload, sidecar
            )
            self.assertIn(
                (
                    "artifact.sha256: expected "
                    f"'{hashlib.sha256(payload).hexdigest()}  artifact.json\\n', "
                    f"observed '{'0' * 64}  artifact.json\\n'"
                ),
                failures,
            )

    def test_rehashed_semantic_faults_are_rejected(self) -> None:
        for name, mutation in SEMANTIC_FAULTS:
            with self.subTest(fault=name):
                document = copy.deepcopy(self.baseline)
                mutation(document)
                self.assertNotEqual(document, self.baseline)
                failures = self.validate_temporary(document)
                self.assertTrue(
                    failures,
                    f"semantic fault was accepted after rehash: {name}",
                )
                self.assertFalse(
                    any(
                        failure.startswith("artifact.sha256")
                        for failure in failures
                    ),
                    f"fault reached only checksum guard: {name}",
                )
                self.assertNotIn(
                    "artifact.json is not canonical JSON", failures
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
