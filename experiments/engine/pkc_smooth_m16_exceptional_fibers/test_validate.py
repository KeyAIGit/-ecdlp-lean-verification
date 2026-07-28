#!/usr/bin/env python3
"""Semantic fault-injection tests for the independent TASK-017 validator."""

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
VALIDATOR_SPEC = importlib.util.spec_from_file_location(
    "task017_independent_validator",
    VALIDATOR_PATH,
)
if VALIDATOR_SPEC is None or VALIDATOR_SPEC.loader is None:
    raise RuntimeError("could not load the independent validator")
validator = importlib.util.module_from_spec(VALIDATOR_SPEC)
VALIDATOR_SPEC.loader.exec_module(validator)

Document = dict[str, Any]
Mutation = Callable[[Document], None]


def find_by_id(records: list[dict[str, Any]], identifier: str) -> dict[str, Any]:
    for record in records:
        if record.get("id") == identifier:
            return record
    raise AssertionError(f"missing fixture row {identifier}")


def missing_leaf_stratum(document: Document) -> None:
    document["leaf_lift_types"]["types"] = [
        row
        for row in document["leaf_lift_types"]["types"]
        if row["id"] != "finite_extension_pair"
    ]


def overlapping_leaf_stratum(document: Document) -> None:
    rows = document["leaf_lift_types"]["types"]
    find_by_id(rows, "finite_extension_pair")["condition"] = find_by_id(
        rows, "finite_base_pair"
    )["condition"]


def accept_external_nonlift(document: Document) -> None:
    find_by_id(
        document["recovery_dispositions"]["rows"],
        "EXTERNAL_NONLIFT",
    )["base_recovery"] = "accept and emit a row"


def accept_internal_extension_only(document: Document) -> None:
    find_by_id(
        document["local_transition_types"]["types"],
        "distinct_extension_only",
    )["disposition"] = "retain as an F_p point branch"


def drop_identity_prefix(document: Document) -> None:
    row = find_by_id(
        document["recovery_dispositions"]["rows"],
        "IDENTITY_PREFIX",
    )
    row["fp_projective"] = "reject"
    row["base_recovery"] = "drop O"


def accept_invalid_projective_zero(document: Document) -> None:
    row = find_by_id(
        document["recovery_dispositions"]["rows"],
        "INVALID_PROJECTIVE",
    )
    row["fp_projective"] = "accept"
    row["base_recovery"] = "accept"


def saturate_coordinate_differences(document: Document) -> None:
    document["claim_boundaries"][
        "coordinate_difference_saturation"
    ] = "allowed"
    saturation = document["projective_s3"][
        "irrelevant_ideal_saturation"
    ]
    saturation["coordinate_pair_ideals"].append(
        "<X_1*Z_2-X_2*Z_1>"
    )
    saturation["forbidden_extra_saturands"] = []


def claim_global_s17_equivalence(document: Document) -> None:
    document["claim_boundaries"]["global_s17_equivalence"] = "proved"
    document["bridge_theorem"]["direct_S17_bridge"] = (
        "global_equivalence_proved"
    )
    document["frozen_predicates"]["direct_S17"].update(
        {
            "predicate_defined": True,
            "polynomial_frozen": True,
            "status": "frozen",
        }
    )


def claim_scheme_equivalence(document: Document) -> None:
    document["claim_boundaries"]["scheme_equivalence"] = "proved"
    document["claim_boundaries"]["radicality"] = "proved"
    document["projective_s3"]["scheme_claim"] = (
        "scheme-theoretic equality proved"
    )


def break_topology_multiplicity(document: Document) -> None:
    accounting = document["control_recovery_replay"][
        "fiber_accounting"
    ]
    accounting["projective_fibers"] = 240
    accounting["fiber_preimage_multiplicity_profile"] = {
        "1": 240
    }


def remove_eta_transport(document: Document) -> None:
    document["secp256k1_glv_replay"]["signed_lift_rows"][1].pop(
        "eta"
    )
    document["secp256k1_glv_replay"]["coefficient_replay"][
        "eta_minus_one_rows"
    ] = 2


def remove_subgroup_proof(document: Document) -> None:
    document["secp256k1_glv_replay"]["theorem_bindings"].pop(
        "whole_group_membership"
    )


def remove_eigenvalue_proof(document: Document) -> None:
    document["secp256k1_glv_replay"]["theorem_bindings"].pop(
        "glv_eigenvalue"
    )


def remove_no_two_torsion_proof(document: Document) -> None:
    document["secp256k1_glv_replay"]["theorem_bindings"].pop(
        "no_nonzero_two_torsion"
    )


def remove_raw_group_check(document: Document) -> None:
    document["secp256k1_glv_replay"]["exact_group_checks"].pop(
        "raw_relation_sum"
    )


def remove_compressed_group_check(document: Document) -> None:
    document["secp256k1_glv_replay"]["exact_group_checks"].pop(
        "compressed_relation_sum"
    )


def remove_target_normalization_check(document: Document) -> None:
    document["control_recovery_replay"]["exact_group_checks"].pop(
        "all_240_target_normalized_leaf_sums_equal_R"
    )


def broaden_domain_to_characteristic_greater_than_three(
    document: Document,
) -> None:
    projective = document["projective_s3"]
    projective["curve"] = (
        "E:y^2=x^3+7 over k with char(k) greater than 3"
    )
    projective["field_scope"] = "char(k) greater than 3"
    document["bridge_theorem"]["assumptions"] = [
        "char(k) greater than 3"
    ]
    document["producer_checks"]["excluded_characteristics"] = [2, 3]


def mutate_local_formula(document: Document) -> None:
    document["projective_s3"]["exact_local_formulas"][
        "identity"
    ] = "H([1:0],[X:Z],[U:V])=X*V-Z*U"


def remove_primary_provenance(document: Document) -> None:
    source = document["source_scope"]
    for field in (
        "primary_claim_extract",
        "primary_claim_extract_sha256",
        "primary_claim_extract_observed_sha256",
        "primary_claim_extract_digest_match",
    ):
        source.pop(field)


def mismatch_primary_provenance_digest(document: Document) -> None:
    source = document["source_scope"]
    source["primary_claim_extract_observed_sha256"] = "0" * 64
    source["primary_claim_extract_digest_match"] = False


def remove_source_claim_id(document: Document) -> None:
    document["source_scope"]["source_claim_ids"].pop()


def change_task_contract_anchor(document: Document) -> None:
    document["source_scope"]["task_contract_anchor"] = (
        "tasks/ECDLP_RESEARCH.md#task-016"
    )


def degrade_assurance(document: Document) -> None:
    document["terminal_disposition"]["assurance"] = "self_asserted"


def overclaim_source_independence(document: Document) -> None:
    document["terminal_disposition"]["source_independence"] = (
        "established"
    )


def misstate_calibration(document: Document) -> None:
    document["terminal_disposition"]["calibration"] = (
        "experimental_generalization"
    )


def price_rank_yield_and_cost(document: Document) -> None:
    terminal = document["terminal_disposition"]
    terminal["rank_status"] = "priced"
    terminal["yield_status"] = "priced"
    terminal["cost_quantity_status"] = "complete"
    terminal["solving_cost_status"] = "priced"
    terminal["cost_quantity_transition"] = "partial_to_complete"


def restore_obsolete_cost_status(document: Document) -> None:
    document["terminal_disposition"]["cost_status"] = "unpriced"


def close_barrier_and_cell(document: Document) -> None:
    terminal = document["terminal_disposition"]
    terminal["barrier_transition"] = "open_to_closed"
    terminal["barrier_effect"] = "closed"
    terminal["cell_transition"] = "open_to_closed"
    terminal["cell_status"] = "closed"


def authorize_execution(document: Document) -> None:
    terminal = document["terminal_disposition"]
    terminal["authorization"] = "granted"
    terminal["experiment_permission"] = "authorized"


def promote_route_and_hypothesis(document: Document) -> None:
    terminal = document["terminal_disposition"]
    terminal["route_effect"] = "promoted"
    terminal["hypothesis_effect"] = "retained"
    terminal["retention_disposition"] = "one_retained"


SEMANTIC_FAULTS: list[tuple[str, Mutation]] = [
    ("missing leaf stratum", missing_leaf_stratum),
    ("overlapping leaf stratum", overlapping_leaf_stratum),
    ("accepted external nonlift", accept_external_nonlift),
    (
        "accepted internal extension-only root",
        accept_internal_extension_only,
    ),
    ("dropped identity prefix", drop_identity_prefix),
    ("accepted projective zero", accept_invalid_projective_zero),
    ("coordinate-difference saturation", saturate_coordinate_differences),
    ("global S17 overclaim", claim_global_s17_equivalence),
    ("scheme overclaim", claim_scheme_equivalence),
    ("broken topology multiplicity", break_topology_multiplicity),
    ("missing eta transport", remove_eta_transport),
    ("missing subgroup proof", remove_subgroup_proof),
    ("missing eigenvalue proof", remove_eigenvalue_proof),
    ("missing two-torsion proof", remove_no_two_torsion_proof),
    ("missing raw group check", remove_raw_group_check),
    ("missing compressed group check", remove_compressed_group_check),
    (
        "missing target normalization check",
        remove_target_normalization_check,
    ),
    (
        "domain broadened to characteristic greater than three",
        broaden_domain_to_characteristic_greater_than_three,
    ),
    ("mutated local formula", mutate_local_formula),
    ("removed primary provenance", remove_primary_provenance),
    (
        "primary provenance digest mismatch",
        mismatch_primary_provenance_digest,
    ),
    ("missing source claim id", remove_source_claim_id),
    ("wrong task contract anchor", change_task_contract_anchor),
    ("degraded assurance", degrade_assurance),
    (
        "overclaimed source independence",
        overclaim_source_independence,
    ),
    ("misstated calibration", misstate_calibration),
    ("priced rank yield cost", price_rank_yield_and_cost),
    ("obsolete cost status", restore_obsolete_cost_status),
    ("closed barrier and cell", close_barrier_and_cell),
    ("execution authorization", authorize_execution),
    ("route and hypothesis promotion", promote_route_and_hypothesis),
]


class ValidatorFaultInjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.baseline = json.loads(ARTIFACT_PATH.read_bytes())

    def validate_temporary(self, document: Document) -> list[str]:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = root / "artifact.json"
            checksum = root / "artifact.sha256"
            payload = validator.canonical_bytes(document)
            artifact.write_bytes(payload)
            actual_sha = hashlib.sha256(payload).hexdigest()
            checksum.write_text(
                f"{actual_sha}  artifact.json\n",
                encoding="ascii",
            )
            parsed = json.loads(artifact.read_bytes())
            return validator.validate_document(
                parsed,
                artifact.read_bytes(),
                checksum,
            )

    def test_committed_artifact_passes(self) -> None:
        self.assertEqual([], self.validate_temporary(self.baseline))

    def test_fault_catalog_has_31_unique_mutations(self) -> None:
        names = [name for name, _ in SEMANTIC_FAULTS]
        self.assertEqual(31, len(names))
        self.assertEqual(len(names), len(set(names)))

    def test_semantic_faults_rejected_after_rehash(self) -> None:
        for name, mutate in SEMANTIC_FAULTS:
            with self.subTest(fault=name):
                document = copy.deepcopy(self.baseline)
                mutate(document)
                self.assertNotEqual(document, self.baseline)
                failures = self.validate_temporary(document)
                self.assertTrue(
                    failures,
                    f"semantic fault was accepted: {name}",
                )
                self.assertFalse(
                    any(
                        failure.startswith("artifact.sha256")
                        for failure in failures
                    ),
                    f"fault reached only checksum guard: {name}",
                )
                self.assertNotIn(
                    "artifact.json is not canonical JSON",
                    failures,
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
