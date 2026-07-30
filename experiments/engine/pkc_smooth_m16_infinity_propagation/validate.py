#!/usr/bin/env python3
"""Independent validator for the TASK-025 infinity-propagation certificate."""

from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARTIFACT_PATH = HERE / "artifact.json"
SIDECAR_PATH = HERE / "artifact.sha256"

ARTIFACT_ID = "PKC-SMOOTH-M16-INFINITY-PROPAGATION-001"
SOURCE_PATH = "Ecdlp/Proved/FrozenProjectiveInfinityPropagation.lean"
SOURCE_SHA256 = (
    "7f868aab5b946a55a213ce26a461477321d6387830eed218c414f1e62853b4b4"
)

EXPECTED_DEPENDENCIES = [
    {
        "digest_match": True,
        "path": "experiments/engine/pkc_smooth_m16_infinity_strata/artifact.json",
        "required_sha256": (
            "54b0f3c5f2f1880b1f805911df21b72e5427b18871f14907ac17a1d8b48bdd39"
        ),
    },
    {
        "digest_match": True,
        "path": "Ecdlp/Proved/FrozenProjectiveInfinityStrata.lean",
        "required_sha256": (
            "1314477f9821da87d2017837abca4fec957ae9998390a231e93532230129a22c"
        ),
    },
    {
        "digest_match": True,
        "path": "Ecdlp/Proved/FrozenRecursiveProjectiveWitness.lean",
        "required_sha256": (
            "5cffb444d95f7691f92bfbd094d945be7e97069edb244d5234fa06f359a852b9"
        ),
    },
]

EXPECTED_TOP_LEVEL = {
    "artifact_id",
    "binding_state",
    "depends_on",
    "downstream_open_boundary",
    "kind",
    "local_propagation_fixture",
    "mask_propagation_contract",
    "prefix_suffix_contract",
    "producer_checks",
    "proof_status",
    "schema_version",
    "scope",
    "terminal_disposition",
    "theorem_bindings",
}

EXPECTED_FIXTURE = {
    "antecedent_witness_counts": {
        "5": {
            "boundary_prefix": 20,
            "boundary_suffix": 25,
            "distance_three": 20,
            "distance_two": 5,
            "prefix_stage_one": 105,
            "suffix_stage_one": 125,
        },
        "7": {
            "boundary_prefix": 49,
            "boundary_suffix": 56,
            "distance_three": 49,
            "distance_two": 7,
            "prefix_stage_one": 434,
            "suffix_stage_one": 483,
        },
        "11": {
            "boundary_prefix": 110,
            "boundary_suffix": 121,
            "distance_three": 110,
            "distance_two": 11,
            "prefix_stage_one": 1221,
            "suffix_stage_one": 1331,
        },
    },
    "balanced_prefix_slots": [1, 2, 3, 4, 5, 6],
    "balanced_suffix_slots": [7, 8, 9, 10, 11, 12],
    "field_roles": {
        "5": "nonsingular finite-field structural fixture",
        "7": (
            "raw HValue polynomial identity fixture only; characteristic 7 "
            "is singular for y^2=x^3+7"
        ),
        "11": "nonsingular finite-field structural and nonvacuity fixture",
    },
    "fields": [5, 7, 11],
    "fixture_scope": (
        "bounded structural implications only; frozen resultants and "
        "production masks are not enumerated"
    ),
    "full_production_mask_enumeration_executed": False,
    "hvalue_first_third_symmetry_exhaustive": True,
    "mask_counts_derived_by_gap_recurrence": True,
    "maximum_balanced_frozen_stage": 5,
    "projective_points": "all [u:1] plus [1:0]",
    "projective_zero_pair_admitted": False,
}

EXPECTED_MASK_CONTRACT = {
    "affine_input_assumption": "forall n, (q n).v != 0",
    "boundary_near_forced_conditions": {
        "slot_1_infinity_implies": "HValue(q0,q1,q2)=0",
        "slot_12_infinity_implies": "HValue(q14,q15,y)=0",
    },
    "boundary_propagated_mask_count": 60,
    "boundary_propagated_mask_definition": (
        "GapTwoInteriorInfinityMask and slots 1 and 12 absent"
    ),
    "boundary_regular_assumption": (
        "both boundary-near HValue expressions are nonzero"
    ),
    "combined_boundary_gap_three_mask_count": 36,
    "distance_three_forced_condition": (
        "slots i and i+3 infinity imply "
        "HValue(q(i+2),q(i+3),q(i+4))=0"
    ),
    "distance_three_input_range": "i : Fin 11",
    "distance_three_regular_assumption": (
        "forall i : Fin 11, HValue(q(i+2),q(i+3),q(i+4)) != 0"
    ),
    "distance_two_forced_condition": (
        "slots i and i+2 infinity imply projectiveDet(q(i+2),q(i+3))=0"
    ),
    "distance_two_input_range": "i : Fin 12",
    "distance_two_regular_assumption": (
        "forall i : Fin 12, projectiveDet(q(i+2),q(i+3)) != 0"
    ),
    "endpoint_nonzero_assumptions": {
        "slot_0": "projectiveDet(q0,q1) != 0",
        "slot_13": "projectiveDet(q15,y) != 0",
    },
    "gap_three_mask_count": 69,
    "gap_three_mask_definition": (
        "slots 0 and 13 absent and selected interior slots have mutual "
        "distance at least four"
    ),
    "gap_two_mask_count": 129,
    "gap_two_mask_definition": (
        "slots 0 and 13 absent and selected interior slots have mutual "
        "distance at least three"
    ),
    "interior_slot_count": 12,
    "production_mask_family_materialized": False,
    "projective_slot_count": 14,
    "stage": 14,
    "starting_interior_separated_mask_count": 377,
}

EXPECTED_PREFIX_SUFFIX = {
    "affine_chart_variable_count": 14,
    "balanced_obstruction_count": 12,
    "balanced_prefix_count": 6,
    "balanced_suffix_count": 6,
    "balanced_suffix_value": (
        "specializeOver(id,reverseFrozenInputs(q,y),q(14-j),frozenC(j))"
    ),
    "empty_mask_conclusion": "I = empty",
    "endpoint_guards_required": True,
    "generic_locus_claimed": False,
    "maximum_balanced_frozen_stage": 5,
    "one_way_resultant_direction": (
        "FrozenProjectiveChain implies specializeOver(frozenC)=0 over any field"
    ),
    "prefix_stage_zero_identity": (
        "propagatedPrefixValue(q,0)=HValue(q0,q1,q2)"
    ),
    "prefix_obstruction_count": 12,
    "prefix_obstruction_value": (
        "specializeOver(id,q,q(j+2),frozenC(j))"
    ),
    "propagation_algebraic_closure_required": False,
    "regular_locus_nonempty_proved": False,
    "selected_internal_slot_consequence": (
        "selected internal slot forces its corresponding prefix or suffix "
        "obstruction value to vanish"
    ),
    "single_chart_mask": "empty",
    "source_field_computation_establishes_mapped_regularity": False,
    "source_stage_bridge": (
        "specialize(q,y,frozenC(k,14))=0 iff mapped target "
        "FrozenAffineChartPolynomialCover"
    ),
    "source_stage_bridge_algebraic_closure_required": True,
    "source_stage_bridge_map_required_injective": True,
    "source_stage_regular_assumptions_location": "mapped inputs and target in K",
    "suffix_stage_zero_identity": (
        "balancedSuffixValue(q,y,0)=HValue(q14,q15,y)"
    ),
    "symbolic_polynomial_nonzeroness_proved": False,
    "target_witness_descent_claimed": False,
    "unique_witness_claimed": False,
}

EXPECTED_PRODUCER = {
    "discrete_log_executed": False,
    "exact_target_search_executed": False,
    "experiment_authorized": False,
    "full_production_mask_family_enumerated": False,
    "parameter_sweep_executed": False,
    "rank_estimated": False,
    "relation_yield_estimated": False,
    "solver_executed": False,
}

EXPECTED_PROOF_STATUS = {
    "balanced_prefix_suffix_propagation": "kernel_checked",
    "card_boundaryGapThreeInfinityMask": "compiler_trusted_native_decide",
    "card_boundaryPropagatedInfinityMask": "compiler_trusted_native_decide",
    "card_gapThreeInteriorInfinityMask": "compiler_trusted_native_decide",
    "card_gapTwoInteriorInfinityMask": "compiler_trusted_native_decide",
    "distance_three_propagation": "kernel_checked",
    "distance_two_propagation": "kernel_checked",
    "generic_or_nonempty_regular_locus": "not_claimed",
    "one_way_base_field_resultant_propagation": "kernel_checked",
    "single_affine_chart_equivalences": "kernel_checked",
    "source_stage_affine_bridge": "kernel_checked",
    "solver_rank_yield_cost_claim": "not_claimed",
}

EXPECTED_SCOPE = {
    "barrier": "B-PKC-M16-COMPLETE-COST-BRIDGE",
    "cell": "CELL-M-PKC-SMOOTH-M16",
    "cost_quantity": "CQ-SEMAEV-S17-SYSTEM-COST",
    "task": "TASK-025",
}

EXPECTED_TERMINAL = {
    "assurance": "kernel_bound_non_run_certificate",
    "authorization": "none",
    "barrier_effect": "conditional_infinity_propagation_closed_only",
    "cell_status": "open_non_executable",
    "cost_quantity_status": "partial",
    "experiment_permission": "none",
    "generic_locus_status": "not_proved",
    "hypothesis_effect": "none",
    "mask_orchestration_status": (
        "conditional_necessary_filter_and_empty_mask_equivalence_only"
    ),
    "rank_status": "unpriced",
    "representation_status": "conditional_single_affine_chart_exact",
    "retention_disposition": "zero_retention_success",
    "route_effect": "none",
    "route_status": "open_parked",
    "solving_cost_status": "unpriced",
    "source_stage_bridge_status": (
        "conditional_injective_algebraically_closed_target"
    ),
    "yield_status": "unpriced",
}

EXPECTED_BOUNDARY = {
    "closed_here": [
        (
            "distance-two infinity pairs force explicit consecutive-input "
            "projective determinant equations"
        ),
        (
            "distance-three infinity pairs force explicit three-input "
            "HValue equations"
        ),
        (
            "the exact conditional local mask counts are 129 after distance "
            "two, 69 after distance three, 60 for the independent "
            "boundary-only refinement, and 36 after the combined refinement"
        ),
        (
            "infinity at slot one or twelve forces its explicit "
            "boundary-near HValue equation"
        ),
        (
            "a projective frozen chain forces the corresponding frozen "
            "specialization to vanish over the original base field"
        ),
        (
            "each internal infinity slot forces an explicit frozen prefix "
            "obstruction to vanish"
        ),
        (
            "six prefix and six suffix obstructions cover all twelve "
            "internal slots with maximum frozen stage five"
        ),
        (
            "endpoint and balanced-obstruction nonvanishing force the "
            "infinity mask to be empty"
        ),
        (
            "under the named assumptions, both the chart cover and literal "
            "chart-polynomial cover are exactly equivalent to the single "
            "empty-mask affine chart"
        ),
        (
            "after an injective base change into an algebraically closed "
            "target, the source stage-14 equation is equivalent to the target "
            "empty-mask affine chart under balanced regularity assumptions "
            "stated in that target"
        ),
    ],
    "not_claimed": [
        (
            "symbolic nonzeroness, nonemptiness, density, probability, or "
            "genericity of any regular locus"
        ),
        "sufficiency or realizability of any nonempty propagated mask",
        "uniqueness of an affine-chart witness or uniqueness of a relation",
        "enumeration or materialization of the production mask family",
        (
            "relation independence, yield, rank, solving degree, fill-in, "
            "memory, recovery, runtime, or total cost"
        ),
        (
            "a solver run, parameter sweep, exact-target search, "
            "discrete-log execution, or ECDLP shortcut"
        ),
        (
            "experiment authorization, hypothesis retention, route "
            "promotion, route rejection, or reduced ECDLP complexity"
        ),
        (
            "automatic establishment of mapped balanced regularity from "
            "source-field computation"
        ),
        "descent of target affine-chart witnesses to the source field",
    ],
    "remaining_blocker": (
        "the regular loci are conditional because symbolic nonzeroness and "
        "nonemptiness are not proved; relation yield and rank, solving, "
        "recovery, and complete cost also remain open"
    ),
}

EXPECTED_THEOREMS = {
    "HValue_swap_first_third",
    "card_boundaryGapThreeInfinityMask",
    "card_boundaryPropagatedInfinityMask",
    "card_gapThreeInteriorInfinityMask",
    "card_gapTwoInteriorInfinityMask",
    "frozenChainVector_prefix",
    "frozenChainVector_suffix",
    "frozenChartCover_iff_affineChartCover_of_balancedPropagatedRegular",
    "frozenChartCover_iff_affineChartCover_of_propagatedPrefixRegular",
    "frozenChartCover_iff_boundaryGapThreeChartCover",
    "frozenChartCover_iff_boundaryPropagatedChartCover",
    "frozenChartCover_iff_gapThreeInteriorChartCover",
    "frozenChartCover_iff_gapTwoInteriorChartCover",
    "frozenChartPolynomialCover_iff_affine_of_balancedPropagatedRegular",
    "frozenChartPolynomialCover_iff_affine_of_propagatedPrefixRegular",
    "frozenRecS17_iff_affineChartPolynomialCover_over_of_balancedPropagatedRegular",
    "frozenChartSystem_balancedPropagatedRegular_mask_eq_empty",
    "frozenChartSystem_balancedSuffixInfinity_forces_zero",
    "frozenChartSystem_boundaryGapThreeInfinityMask",
    "frozenChartSystem_boundaryPropagatedInfinityMask",
    "frozenChartSystem_gapThreeInfinity_forces_HValue_zero",
    "frozenChartSystem_gapThreeInteriorInfinityMask",
    "frozenChartSystem_gapTwoInfinity_forces_det_zero",
    "frozenChartSystem_gapTwoInteriorInfinityMask",
    "frozenChartSystem_internalInfinity_forces_prefix_zero",
    "frozenChartSystem_propagatedPrefixRegular_mask_eq_empty",
    "frozenChartSystem_slotOneInfinity_forces_HValue_zero",
    "frozenChartSystem_slotTwelveInfinity_forces_HValue_zero",
    "frozenProjectiveChain_normalize_output_iff",
    "balancedSuffixValue_zero",
    "propagatedPrefixValue_zero",
    "specializeOver_frozenC_eq_zero_of_projectiveChain",
    "taskSylvester_det_eq_zero_of_common_projective_root",
}

EXPECTED_DEFINITIONS = {
    "BalancedPropagatedRegular",
    "BoundaryGapThreeInfinityMask",
    "BoundaryHRegular",
    "BoundaryPropagatedInfinityMask",
    "FrozenAffineChartCover",
    "FrozenAffineChartPolynomialCover",
    "GapThreeHRegular",
    "GapThreeInteriorInfinityMask",
    "GapTwoDetRegular",
    "GapTwoInteriorInfinityMask",
    "PropagatedPrefixRegular",
    "balancedSuffixInfinitySlot",
    "balancedSuffixValue",
    "internalInfinitySlot",
    "propagatedPrefixValue",
    "reverseFrozenInputs",
}


class ValidationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def spaced_subset_count(length: int, minimum_gap: int) -> int:
    """Count subsets of a path whose chosen indices differ by minimum_gap."""
    require(length >= 0, "negative path length")
    require(minimum_gap >= 1, "invalid minimum gap")
    counts = [1]
    for current_length in range(1, length + 1):
        without_last = counts[current_length - 1]
        with_last = (
            counts[current_length - minimum_gap]
            if current_length >= minimum_gap
            else 1
        )
        counts.append(without_last + with_last)
    return counts[length]


def det(a: tuple[int, int], b: tuple[int, int], p: int) -> int:
    return (a[0] * b[1] - a[1] * b[0]) % p


def h_value(
    a: tuple[int, int],
    b: tuple[int, int],
    c: tuple[int, int],
    p: int,
) -> int:
    au, av = a
    bu, bv = b
    cu, cv = c
    return (
        au**2 * bu**2 * cv**2
        + au**2 * bv**2 * cu**2
        + av**2 * bu**2 * cu**2
        - 2 * au**2 * bu * bv * cu * cv
        - 2 * au * av * bu**2 * cu * cv
        - 2 * au * av * bu * bv * cu**2
        - 28
        * (
            au * av * bv**2 * cv**2
            + av**2 * bu * bv * cv**2
            + av**2 * bv**2 * cu * cv
        )
    ) % p


@lru_cache(maxsize=1)
def validate_local_fixture() -> None:
    require(spaced_subset_count(12, 2) == 377, "377 count drift")
    require(spaced_subset_count(12, 3) == 129, "129 count drift")
    require(spaced_subset_count(12, 4) == 69, "69 count drift")
    require(spaced_subset_count(10, 3) == 60, "60 count drift")
    require(spaced_subset_count(10, 4) == 36, "36 count drift")

    prefix_slots = [j + 1 for j in range(6)]
    suffix_slots = [12 - j for j in range(6)]
    require(prefix_slots == [1, 2, 3, 4, 5, 6], "prefix slots drift")
    require(suffix_slots == [12, 11, 10, 9, 8, 7], "suffix slots drift")
    require(
        sorted(prefix_slots + suffix_slots) == list(range(1, 13)),
        "balanced slot coverage drift",
    )
    require(max(range(6)) == 5, "balanced stage bound drift")

    infinity = (1, 0)
    observed: dict[str, dict[str, int]] = {}
    for p in (5, 7, 11):
        affine = [(u, 1) for u in range(p)]
        points = affine + [infinity]
        counts = {
            "boundary_prefix": 0,
            "boundary_suffix": 0,
            "distance_three": 0,
            "distance_two": 0,
            "prefix_stage_one": 0,
            "suffix_stage_one": 0,
        }

        for a in points:
            for b in points:
                for c in points:
                    require(
                        h_value(a, b, c, p) == h_value(c, b, a, p),
                        f"first/third symmetry failed over F{p}",
                    )

        for a in affine:
            for b in affine:
                for middle in affine:
                    if (
                        h_value(infinity, a, middle, p) == 0
                        and h_value(middle, b, infinity, p) == 0
                    ):
                        counts["distance_two"] += 1
                        require(
                            det(a, b, p) == 0,
                            f"distance-two implication failed over F{p}",
                        )

        for a in affine:
            for b in affine:
                for c in affine:
                    for left_neighbor in affine:
                        for right_neighbor in affine:
                            if (
                                h_value(
                                    infinity, a, left_neighbor, p
                                )
                                == 0
                                and h_value(
                                    left_neighbor, b, right_neighbor, p
                                )
                                == 0
                                and h_value(
                                    right_neighbor, c, infinity, p
                                )
                                == 0
                            ):
                                counts["distance_three"] += 1
                                require(
                                    h_value(a, b, c, p) == 0,
                                    (
                                        "distance-three implication failed "
                                        f"over F{p}"
                                    ),
                                )

        for q0 in affine:
            for q1 in affine:
                for q2 in affine:
                    for z0 in affine:
                        if (
                            h_value(q0, q1, z0, p) == 0
                            and h_value(z0, q2, infinity, p) == 0
                        ):
                            counts["boundary_prefix"] += 1
                            require(
                                h_value(q0, q1, q2, p) == 0,
                                f"boundary-prefix implication failed over F{p}",
                            )

        for q14 in affine:
            for q15 in affine:
                for y in points:
                    for z13 in affine:
                        if (
                            h_value(infinity, q14, z13, p) == 0
                            and h_value(z13, q15, y, p) == 0
                        ):
                            counts["boundary_suffix"] += 1
                            require(
                                h_value(q14, q15, y, p) == 0,
                                f"boundary-suffix implication failed over F{p}",
                            )

        # Reduced stage-one prefix implication.  The conclusion checks the
        # same concrete witness z0 after the forced endpoint z1 is replaced
        # by q3.  This does not enumerate frozen resultants.
        for q0 in affine:
            for q1 in affine:
                for q2 in affine:
                    for q3 in affine:
                        for z0 in points:
                            if h_value(q0, q1, z0, p) != 0:
                                continue
                            for z1 in affine:
                                if (
                                    h_value(z0, q2, z1, p) == 0
                                    and h_value(z1, q3, infinity, p) == 0
                                ):
                                    counts["prefix_stage_one"] += 1
                                    require(
                                        h_value(z0, q2, q3, p) == 0,
                                        (
                                            "stage-one prefix implication "
                                            f"failed over F{p}"
                                        ),
                                    )

        # Reduced stage-one suffix implication.  The original final and
        # penultimate equations are read in reverse after the forced z12=q13
        # substitution.  This checks only the bounded chain structure.
        for q15 in affine:
            for y in points:
                for q14 in affine:
                    for q13 in affine:
                        for z13 in points:
                            if h_value(z13, q15, y, p) != 0:
                                continue
                            for z12 in affine:
                                if (
                                    h_value(z12, q14, z13, p) == 0
                                    and h_value(
                                        infinity, q13, z12, p
                                    )
                                    == 0
                                ):
                                    counts["suffix_stage_one"] += 1
                                    require(
                                        h_value(q15, y, z13, p) == 0,
                                        (
                                            "stage-one suffix base failed "
                                            f"over F{p}"
                                        ),
                                    )
                                    require(
                                        h_value(z13, q14, q13, p) == 0,
                                        (
                                            "stage-one suffix step failed "
                                            f"over F{p}"
                                        ),
                                    )

        observed[str(p)] = counts

    require(
        observed == EXPECTED_FIXTURE["antecedent_witness_counts"],
        "finite-field antecedent witness counts drift",
    )


def validate_source(root: Path) -> None:
    source = root / SOURCE_PATH
    require(source.is_file(), "bound Lean source missing")
    require(sha256(source) == SOURCE_SHA256, "bound Lean source SHA drift")
    text = source.read_text(encoding="utf-8")
    require(not re.search(r"\b(?:sorry|admit)\b", text), "proof placeholder")
    require(not re.search(r"(?m)^\s*axiom\b", text), "custom axiom")
    require(not re.search(r"(?m)^\s*unsafe\b", text), "unsafe declaration")
    for theorem in EXPECTED_THEOREMS:
        require(
            re.search(rf"\btheorem\s+{re.escape(theorem)}\b", text)
            is not None,
            f"missing theorem {theorem}",
        )
    for definition in EXPECTED_DEFINITIONS:
        require(
            re.search(
                rf"\b(?:noncomputable\s+)?def\s+{re.escape(definition)}\b",
                text,
            )
            is not None,
            f"missing definition {definition}",
        )


def validate_document(
    document: dict[str, Any],
    root: Path = ROOT,
    require_final_source_binding: bool = True,
) -> None:
    require(set(document) == EXPECTED_TOP_LEVEL, "top-level schema drift")
    require(document["schema_version"] == 1, "schema version drift")
    require(document["artifact_id"] == ARTIFACT_ID, "artifact id drift")
    require(
        document["kind"] == "source_bound_non_run_certificate",
        "artifact kind drift",
    )
    require(
        document["binding_state"]
        == {
            "artifact_sidecar": "artifact.sha256",
            "digest_match": True,
            "source_path": SOURCE_PATH,
            "source_sha256": SOURCE_SHA256,
            "source_status": "final",
        },
        "binding drift",
    )
    require(document["depends_on"] == EXPECTED_DEPENDENCIES, "dependency drift")
    require(
        document["downstream_open_boundary"] == EXPECTED_BOUNDARY,
        "downstream boundary drift",
    )
    require(
        document["local_propagation_fixture"] == EXPECTED_FIXTURE,
        "fixture contract drift",
    )
    require(
        document["mask_propagation_contract"] == EXPECTED_MASK_CONTRACT,
        "mask contract drift",
    )
    require(
        document["prefix_suffix_contract"] == EXPECTED_PREFIX_SUFFIX,
        "prefix/suffix contract drift",
    )
    require(document["producer_checks"] == EXPECTED_PRODUCER, "producer drift")
    require(
        document["proof_status"] == EXPECTED_PROOF_STATUS,
        "proof-status drift",
    )
    require(document["scope"] == EXPECTED_SCOPE, "scope drift")
    require(
        document["terminal_disposition"] == EXPECTED_TERMINAL,
        "terminal disposition drift",
    )

    bindings = document["theorem_bindings"]
    require(set(bindings) == EXPECTED_THEOREMS, "theorem binding set drift")
    for name, declaration in bindings.items():
        require(
            declaration == f"Ecdlp.FrozenProjectiveSemaev.{name}",
            f"declaration drift for {name}",
        )

    validate_local_fixture()
    for dependency in EXPECTED_DEPENDENCIES:
        path = root / dependency["path"]
        require(path.is_file(), f"dependency missing: {dependency['path']}")
        require(
            sha256(path) == dependency["required_sha256"],
            f"dependency SHA drift: {dependency['path']}",
        )
    if require_final_source_binding:
        validate_source(root)


def validate_sidecar() -> None:
    require(SIDECAR_PATH.is_file(), "artifact sidecar missing")
    expected = f"{sha256(ARTIFACT_PATH)}  artifact.json"
    require(
        SIDECAR_PATH.read_text(encoding="utf-8").strip() == expected,
        "artifact sidecar drift",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-final-source-binding", action="store_true")
    args = parser.parse_args()
    try:
        document = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
        validate_document(
            document,
            require_final_source_binding=args.require_final_source_binding,
        )
        validate_sidecar()
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        print(
            f"TASK-025 infinity-propagation certificate FAILED: {exc}",
            file=sys.stderr,
        )
        return 1
    print("TASK-025 infinity-propagation certificate PASSED")
    print("conditional mask counts: 377 -> 129 -> 69; 129 -> 60; combined=36")
    print("F5/F7/F11 local and reduced prefix/suffix fixtures: PASS")
    print("F7 is a raw polynomial fixture only; F5/F11 are nonsingular")
    print(
        "genericity, realizability, unique witnesses, solver, rank, yield, "
        "recovery, cost, and ECDLP-complexity claims remain absent"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
