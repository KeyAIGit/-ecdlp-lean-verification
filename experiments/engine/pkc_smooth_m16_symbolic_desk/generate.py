#!/usr/bin/env python3
"""Generate the deterministic M16 symbolic desk-cost artifact.

This program uses only exact integer and rational arithmetic.  It counts
symbolic presentations and conditional matrix templates; it does not
materialize a Semaev system, run a solver, or compute a discrete logarithm.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any


P = (1 << 256) - (1 << 32) - 977
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
D = 564_522
M = 16
DELTA = 10
FACTOR_CHAIN = (2, 3, 7, 13_441)
S3_EQUATIONS = M - 1
S3_INTERNALS = M - 2
S3_VARIABLES = M + S3_INTERNALS
S3_TERMS_SYMBOLIC = 9
S3_TERMS_TARGET_ZERO = 3
BYTES_PER_FIELD_ELEMENT = 32

HERE = Path(__file__).resolve().parent
ARTIFACT_PATH = HERE / "artifact.json"
HASH_PATH = HERE / "artifact.sha256"


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def ceil_div(numerator: int, denominator: int) -> int:
    if numerator < 0 or denominator <= 0:
        raise ValueError("ceil_div expects nonnegative/positive arguments")
    return (numerator + denominator - 1) // denominator


def strict_integer_upper(numerator: int, denominator: int) -> int:
    """Largest integer t satisfying denominator * t < numerator."""
    if numerator <= 0 or denominator <= 0:
        raise ValueError("strict_integer_upper expects positive arguments")
    return (numerator - 1) // denominator


def binary_gate_count(exponent: int) -> dict[str, Any]:
    bits = format(exponent, "b")
    squarings = len(bits) - 1
    nonsquare_multiplications = bits.count("1") - 1
    return {
        "binary": bits,
        "bit_length": len(bits),
        "gate_count": squarings + nonsquare_multiplications,
        "nonsquare_multiplications": nonsquare_multiplications,
        "popcount": bits.count("1"),
        "squarings": squarings,
    }


def macaulay_envelope(
    variable_count: int,
    equation_degrees: list[int],
    cutoff: int,
    degree_profile_assumption: str,
) -> dict[str, Any]:
    columns = math.comb(variable_count + cutoff, variable_count)
    row_templates = sum(
        math.comb(variable_count + cutoff - degree, variable_count)
        for degree in equation_degrees
        if degree <= cutoff
    )
    dense_cells = columns * row_templates
    return {
        "bytes_per_dense_field_element": BYTES_PER_FIELD_ELEMENT,
        "column_monomials_through_cutoff": str(columns),
        "cutoff_total_degree": cutoff,
        "dense_byte_capacity_if_every_cell_is_stored": str(
            dense_cells * BYTES_PER_FIELD_ELEMENT
        ),
        "degree_profile_assumption": degree_profile_assumption,
        "equation_multiple_templates_before_deduplication": str(
            row_templates
        ),
        "interpretation": (
            "A raw total-degree template count at the stated cutoff. It is "
            "neither a solving-degree estimate nor a solver-memory bound."
        ),
        "variable_count": variable_count,
    }


def source_chain_profile() -> list[dict[str, Any]]:
    return [
        {
            "exponent": exponent,
            **binary_gate_count(exponent),
        }
        for exponent in FACTOR_CHAIN
    ]


def source_factor_addition_chain() -> list[int]:
    """Return exponents after every gate in the factored binary circuit."""
    exponents = [1]
    current = 1
    for factor in FACTOR_CHAIN:
        base = current
        value = current
        for bit in format(factor, "b")[1:]:
            value *= 2
            exponents.append(value)
            if bit == "1":
                value += base
                exponents.append(value)
        current = value
    if current != D:
        raise AssertionError("source-factor circuit does not reach D")
    return exponents


def build_artifact() -> dict[str, Any]:
    direct_relation_variables = M
    membership_chain_internals = M * (len(FACTOR_CHAIN) - 1)
    source_membership_equations = M * len(FACTOR_CHAIN)

    direct_variables = direct_relation_variables + membership_chain_internals
    direct_equation_degrees = [M * (1 << (M - 1))] + list(
        FACTOR_CHAIN
    ) * M

    recursive_source_variables = S3_VARIABLES + membership_chain_internals
    recursive_source_degrees = [4] * S3_EQUATIONS + list(FACTOR_CHAIN) * M

    chain_profile = source_chain_profile()
    addition_chain_exponents = source_factor_addition_chain()
    circuit_gates_per_coordinate = sum(
        item["gate_count"] for item in chain_profile
    )
    circuit_auxiliaries_per_coordinate = circuit_gates_per_coordinate - 1
    circuit_membership_equations = M * circuit_gates_per_coordinate
    circuit_membership_auxiliaries = M * circuit_auxiliaries_per_coordinate
    recursive_circuit_variables = S3_VARIABLES + circuit_membership_auxiliaries
    recursive_circuit_degrees = [4] * S3_EQUATIONS + [2] * (
        circuit_membership_equations
    )

    yield_rational = Fraction(D**M, math.factorial(M) * P)
    relation_multiplier = Fraction(math.factorial(M) * P, D ** (M - 1))
    generic_benchmark = math.isqrt(N)
    if generic_benchmark * generic_benchmark < N:
        generic_benchmark += 1
    optimistic_t_max = strict_integer_upper(
        generic_benchmark * relation_multiplier.denominator,
        relation_multiplier.numerator,
    )

    direct_box_capacity = ((1 << (M - 1)) + 1) ** M
    source_relation_rows = D + DELTA

    return {
        "artifact_id": "PKC-SMOOTH-M16-SYMBOLIC-DESK-001",
        "factor_base_and_linear_algebra": {
            "exact_membership_layer": {
                "denominator_components": 0,
                "group": "H = {x in F_p^* : x^D = 1}",
                "membership_polynomial": "x^D - 1",
                "root_count": D,
                "square_free": True,
                "square_free_reason": "D divides p-1, so p does not divide D.",
            },
            "glv_orbit_accounting": {
                "coordinate_log_columns_after_negation": "U",
                "glv_aware_factor_log_columns": "U/3",
                "justification": (
                    "Because 3 divides D, the order-three beta lies in H; "
                    "x, beta*x, beta^2*x have the same liftability and known "
                    "GLV-related logarithms."
                ),
                "scope": (
                    "This is an exact optional column relation, not the "
                    "source paper's linear-algebra model or a rank result."
                ),
            },
            "lift_count": {
                "character_sum": "S_H = sum_{x in H} chi(x^3 + 7)",
                "compressed_character_sum": (
                    "S_H = 3 * sum_{z in H^3} chi(z + 7)"
                ),
                "coordinate_roots_with_curve_lifts": "U = (D + S_H)/2",
                "rational_two_torsion_roots": 0,
                "signed_factor_base_points": "2U = D + S_H",
                "status": "unknown_without_character_sum_evaluation",
            },
            "source_nominal_sparse_model": {
                "delta_is_a_priori_not_a_rank_theorem": True,
                "factor_entries_per_relation_upper_bound": M,
                "nominal_relation_rows_D_plus_delta": source_relation_rows,
                "nominal_factor_entry_occurrences_upper_bound": (
                    source_relation_rows * M
                ),
                "nominal_unknown_columns_D": D,
                "warning": (
                    "D columns are conditional, not the exact factor-base "
                    "dimension. U, GLV relations, duplicate coordinates, "
                    "relation independence, and rank remain unresolved."
                ),
            },
        },
        "inputs": {
            "D": D,
            "bytes_per_field_element_for_conditional_dense_models": (
                BYTES_PER_FIELD_ELEMENT
            ),
            "delta_from_source": DELTA,
            "factor_chain": list(FACTOR_CHAIN),
            "m": M,
            "n": str(N),
            "p": str(P),
            "target_x_treated_as_fixed_constant": True,
        },
        "kind": "deterministic_nonexperimental_symbolic_desk",
        "recovery": {
            "coordinate_target_relative_sign_classes": 1 << (M - 1),
            "direct_presentation": {
                "meet_in_the_middle_list_sizes_after_fixing_one_global_sign": [
                    1 << 7,
                    1 << 8,
                ],
                "raw_factor_sign_assignments": 1 << M,
                "required_final_check": (
                    "Verify the recovered signed points and the full elliptic-"
                    "curve relation exactly; accept either sign of the fixed "
                    "target x-coordinate with the corresponding coefficient sign."
                ),
            },
            "recursive_presentation": {
                "status": "unresolved",
                "unresolved_items": [
                    "partial sums at the point at infinity",
                    "tangent and repeated-coordinate fibers",
                    "extension-field lifts rejected by F_p recovery",
                    "compatibility of local S3 sign choices across the tree",
                    "permutation and duplicate-root multiplicities",
                ],
            },
        },
        "representations": {
            "direct_s17_with_source_factor_chain": {
                "equation_count": 1 + source_membership_equations,
                "membership": {
                    "equation_count": source_membership_equations,
                    "intermediate_variable_count": membership_chain_internals,
                    "map_degrees": list(FACTOR_CHAIN),
                    "term_occurrences": 2 * source_membership_equations,
                },
                "macaulay_cutoff_envelope": macaulay_envelope(
                    direct_variables,
                    direct_equation_degrees,
                    max(direct_equation_degrees),
                    (
                        "Conditional on assigning the target-specialized S17 "
                        "relation total degree 524288. The committed evidence "
                        "provides this value as an upper bound; if specialization "
                        "lowers the degree, the row-template count changes and "
                        "this count is not a bound for that different profile."
                    ),
                ),
                "maximum_input_equation_degree": max(direct_equation_degrees),
                "relation": {
                    "actual_expanded_support": None,
                    "dense_box_support_capacity_upper_bound": str(
                        direct_box_capacity
                    ),
                    "per_leaf_variable_degree": 1 << (M - 1),
                    "polynomial": "S_17",
                    "target_specialized_total_degree_upper_bound": (
                        M * (1 << (M - 1))
                    ),
                },
                "variable_count": direct_variables,
            },
            "recursive_s3_with_quadratic_source_factor_circuit": {
                "equation_count": S3_EQUATIONS
                + circuit_membership_equations,
                "macaulay_cutoff_envelope": macaulay_envelope(
                    recursive_circuit_variables,
                    recursive_circuit_degrees,
                    max(recursive_circuit_degrees),
                    (
                        "Exact input-degree profile for 15 quartic S3 equations "
                        "and 384 quadratic circuit equations."
                    ),
                ),
                "maximum_input_equation_degree": max(
                    recursive_circuit_degrees
                ),
                "membership_circuit": {
                    "addition_chain_exponents_including_input_one": (
                        addition_chain_exponents
                    ),
                    "auxiliary_variable_count": (
                        circuit_membership_auxiliaries
                    ),
                    "equation_count": circuit_membership_equations,
                    "gate_count_per_coordinate": (
                        circuit_gates_per_coordinate
                    ),
                    "generic_multiplication_only_lower_bound_for_x_to_D": (
                        (D - 1).bit_length()
                    ),
                    "map_profile": chain_profile,
                    "pointwise_membership_equivalence": (
                        "The triangular circuit has unique intermediates and "
                        "terminates at x^D = 1."
                    ),
                    "term_occurrences": 2 * circuit_membership_equations,
                },
                "relation": {
                    "equation_count": S3_EQUATIONS,
                    "internal_variable_count": S3_INTERNALS,
                    "maximum_term_occurrences": (
                        S3_EQUATIONS * S3_TERMS_SYMBOLIC
                    ),
                    "nonconstant_x_variable_count": S3_VARIABLES,
                    "target_zero_term_occurrences": (
                        (S3_EQUATIONS - 1) * S3_TERMS_SYMBOLIC
                        + S3_TERMS_TARGET_ZERO
                    ),
                    "total_degree": 4,
                },
                "scope_boundary": (
                    "Pointwise membership is exact. Equivalence of the full "
                    "recursive S3 presentation to direct S17 after saturation, "
                    "including exceptional fibers, is not established."
                ),
                "term_occurrences": {
                    "target_nonzero_or_symbolic": (
                        2 * circuit_membership_equations
                        + S3_EQUATIONS * S3_TERMS_SYMBOLIC
                    ),
                    "target_zero": (
                        2 * circuit_membership_equations
                        + (S3_EQUATIONS - 1) * S3_TERMS_SYMBOLIC
                        + S3_TERMS_TARGET_ZERO
                    ),
                },
                "variable_count": recursive_circuit_variables,
            },
            "recursive_s3_with_source_factor_chain": {
                "equation_count": S3_EQUATIONS
                + source_membership_equations,
                "macaulay_cutoff_envelope": macaulay_envelope(
                    recursive_source_variables,
                    recursive_source_degrees,
                    max(recursive_source_degrees),
                    (
                        "Exact input-degree profile for 15 quartic S3 equations "
                        "and 16 copies of the degree-2, 3, 7, 13441 source chain."
                    ),
                ),
                "maximum_input_equation_degree": max(
                    recursive_source_degrees
                ),
                "membership": {
                    "equation_count": source_membership_equations,
                    "intermediate_variable_count": membership_chain_internals,
                    "map_degrees": list(FACTOR_CHAIN),
                    "term_occurrences": 2 * source_membership_equations,
                },
                "relation": {
                    "equation_count": S3_EQUATIONS,
                    "internal_variable_count": S3_INTERNALS,
                    "maximum_term_occurrences": (
                        S3_EQUATIONS * S3_TERMS_SYMBOLIC
                    ),
                    "nonconstant_x_variable_count": S3_VARIABLES,
                    "target_zero_term_occurrences": (
                        (S3_EQUATIONS - 1) * S3_TERMS_SYMBOLIC
                        + S3_TERMS_TARGET_ZERO
                    ),
                    "total_degree": 4,
                },
                "term_occurrences": {
                    "target_nonzero_or_symbolic": (
                        2 * source_membership_equations
                        + S3_EQUATIONS * S3_TERMS_SYMBOLIC
                    ),
                    "target_zero": (
                        2 * source_membership_equations
                        + (S3_EQUATIONS - 1) * S3_TERMS_SYMBOLIC
                        + S3_TERMS_TARGET_ZERO
                    ),
                },
                "variable_count": recursive_source_variables,
            },
        },
        "scope": {
            "excluded": [
                "materialized S17 or recursive polynomial system",
                "solver execution",
                "solving-degree estimate",
                "Macaulay fill-in estimate",
                "exact-target relation search",
                "discrete-log computation",
                "route promotion or experiment authorization",
                "asymptotic or security claim",
            ],
            "included": [
                "exact integer and rational arithmetic",
                "source-map equation and variable counts",
                "algorithm-specific multiplication-gate counts",
                "conditional total-degree matrix-template envelopes",
                "recovery and full-cost blockers",
            ],
        },
        "source_cost_model": {
            "uncalibrated_generic_reference_ceiling": {
                "ceil_sqrt_target_group_order": str(generic_benchmark),
                "scope": (
                    "Integer sqrt(n) reference only. T(E,16,L), field work, "
                    "group work, parallelism, and equal-success cost have not "
                    "been converted to common units, so this is not a matched "
                    "Pollard-rho baseline or a measured runtime."
                ),
            },
            "linear_algebra_term": {
                "D_cubed": str(D**3),
                "D_squared": str(D**2),
                "paper_model": "D^omega with 2 < omega <= 3",
            },
            "optimistic_necessary_per_system_cost": {
                "assumptions": [
                    "ignore all preprocessing cost P(p,16)",
                    "ignore all linear-algebra cost",
                    "treat the paper multiplier as the online-call multiplier",
                    (
                        "assume T, field operations, and group operations can "
                        "be compared in one common work unit"
                    ),
                    "ignore the equal-success probability conversion",
                    "require strict total work below ceil(sqrt(n))",
                ],
                "maximum_integer_T": str(optimistic_t_max),
                "meaning": (
                    "This uncalibrated optimistic threshold is arithmetic only. "
                    "It does not establish T(E,16,L), a matched generic "
                    "comparison, success rate, or complete cost."
                ),
            },
            "paper_relation_multiplier": {
                "ceiling": str(
                    ceil_div(
                        relation_multiplier.numerator,
                        relation_multiplier.denominator,
                    )
                ),
                "denominator": str(relation_multiplier.denominator),
                "formula": "16! * p / D^15",
                "numerator": str(relation_multiplier.numerator),
            },
            "paper_yield": {
                "denominator": str(yield_rational.denominator),
                "formula": "D^16 / (16! * p)",
                "interpretation": (
                    "Exact evaluation of the paper's heuristic expectation; "
                    "not a success probability or independent-relation rate."
                ),
                "numerator": str(yield_rational.numerator),
            },
            "total_cost_formula": (
                "P(p,16) + (16! * p / D^15) * T(E,16,L) + D^omega"
            ),
        },
        "source_scope": {
            "factorization_artifact": (
                "experiments/engine/pkc_smooth_desk_screen/artifact.json"
            ),
            "kernel_curve_cardinality": (
                "Ecdlp/Proved/CurveCardinalityExact.lean"
            ),
            "kernel_full_group": "Ecdlp/Proved/CurveFullGroup.lean",
            "kernel_glv_eigenvalue": (
                "Ecdlp/Proved/GlvSubgroupEigenvalue.lean"
            ),
            "kernel_glv_orbits": "Ecdlp/Proved/GlvOrbit.lean",
            "kernel_s3_definition": "Ecdlp/Proved/SemaevThree.lean",
            "kernel_theorems": {
                "curve_cardinality": (
                    "Ecdlp.Curve.secp256k1_card_point_eq_n"
                ),
                "full_group": "Ecdlp.Curve.secp256k1_grp_eq_top",
                "glv_eigenvalue_on_subgroup": (
                    "Ecdlp.Curve."
                    "secp256k1_glvPoint_eq_lam_on_zmultiples"
                ),
                "glv_nonfixed_orbit_size_three": (
                    "Ecdlp.Curve."
                    "secp256k1_glvPoint_orbit_three_distinct"
                ),
                "no_nonzero_two_torsion": (
                    "Ecdlp.Curve.secp256k1_no_nonzero_two_torsion"
                ),
                "semaev_three_semantics": (
                    "Ecdlp.Semaev.secp256k1_semaev_three_iff"
                ),
            },
            "primary_locators": {
                "delta_and_algorithm": (
                    "PKC 2016 Section 3.1, Algorithm 1 and paragraph after it"
                ),
                "source_maps": "PKC 2016 Section 3.3",
                "total_cost": "PKC 2016 Section 3.2",
            },
            "primary_claim_extract": (
                "data/source_claim_extracts/petit_kosters_messeng2016.json"
            ),
            "source_claim_ids": [
                "SC-GLV-ENDOMORPHISM",
                "SC-GLV-ENDOMORPHISM-NONTRIVIAL",
                "SC-PKC-SMOOTH-SUBGROUP",
                "SC-PKC-RELATION-YIELD",
                "SC-SECP-NO-TWO-TORSION",
                "SC-SECP-PMINUS1-FACTORIZATION",
                "SC-SECP-PRIME-FIELD",
                "SC-SEMAEV-RELATION-SEMANTICS",
            ],
        },
        "terminal_disposition": {
            "assurance": "certificate_replayed",
            "authorization": "none",
            "calibration": "excluded_nonexperimental",
            "cell_transition": "open_to_open",
            "cost_quantity_transition": "missing_to_partial",
            "hypothesis_effect": "none",
            "retention_disposition": "zero_retention_success",
            "reopening_conditions": [
                (
                    "Prove a source-faithful direct/recursive/circuit bridge "
                    "including saturation and exceptional fibers."
                ),
                (
                    "Determine usable F_p lifts, recovery multiplicities, and "
                    "independent-relation rank under negation and GLV orbits."
                ),
                (
                    "Bound solving degree, fill-in, online/offline work, memory, "
                    "preprocessing, sparse linear algebra, money, and review "
                    "effort against the matched generic baseline."
                ),
            ],
            "route_effect": "none",
            "scientific_disposition": "scoped_blocker",
            "source_independence": "not_established",
        },
        "unresolved_complete_cost_fields": [
            "actual expanded S17 support",
            "full recursive/direct equivalence after saturation",
            "exceptional components and extension-field fibers",
            "usable factor-base cardinality U",
            "solving degree and Macaulay fill-in",
            "recovery success and multiplicity distribution",
            "independent-relation probability and rank",
            "preprocessing and amortization",
            "sparse linear-algebra time and storage",
            "total online/offline work, memory, money, and reviewer effort",
        ],
        "schema_version": "1.0",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = parser.parse_args()

    artifact_bytes = canonical_bytes(build_artifact())
    digest = hashlib.sha256(artifact_bytes).hexdigest()
    hash_bytes = f"{digest}  artifact.json\n".encode("ascii")

    if args.write:
        ARTIFACT_PATH.write_bytes(artifact_bytes)
        HASH_PATH.write_bytes(hash_bytes)
        print(f"wrote {ARTIFACT_PATH.relative_to(HERE.parent.parent.parent)}")
        print(f"sha256 {digest}")
        return 0

    problems: list[str] = []
    try:
        committed_artifact = ARTIFACT_PATH.read_bytes()
    except FileNotFoundError:
        problems.append("artifact.json is missing")
    else:
        if committed_artifact != artifact_bytes:
            problems.append("artifact.json differs from deterministic output")
    try:
        committed_hash = HASH_PATH.read_bytes()
    except FileNotFoundError:
        problems.append("artifact.sha256 is missing")
    else:
        if committed_hash != hash_bytes:
            problems.append("artifact.sha256 differs from deterministic output")
    if problems:
        for problem in problems:
            print(f"ERROR: {problem}", file=sys.stderr)
        return 1
    print("M16 symbolic desk artifact matches deterministic output")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
