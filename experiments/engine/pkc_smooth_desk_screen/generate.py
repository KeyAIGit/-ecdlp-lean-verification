#!/usr/bin/env python3
"""Generate the deterministic PKC smooth-subgroup desk-screen artifact.

This program deliberately uses only Python's standard library.  It performs
integer arithmetic and representation counting; it does not construct or run
an ECDLP solver.
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
D = 564_522
LARGE_COFACTOR = (
    205115282021455665897114700593932402728804164701536103180137503955397371
)
SMALL_PRIME_FACTORS = (2, 3, 7, 13_441)
B_CAP = 13_440
M_VALUES = range(10, 21)

HERE = Path(__file__).resolve().parent
ARTIFACT_PATH = HERE / "artifact.json"
HASH_PATH = HERE / "artifact.sha256"


def ceil_div(numerator: int, denominator: int) -> int:
    if numerator < 0 or denominator <= 0:
        raise ValueError("ceil_div expects a nonnegative numerator and positive denominator")
    return (numerator + denominator - 1) // denominator


def ceil_nth_root(value: int, exponent: int) -> int:
    """Return the least integer r such that r**exponent >= value."""
    if value < 0 or exponent <= 0:
        raise ValueError("invalid root arguments")
    if value <= 1:
        return value

    low = 0
    high = 1 << ceil_div(value.bit_length(), exponent)
    while high**exponent < value:
        high <<= 1
    while low + 1 < high:
        middle = (low + high) // 2
        if middle**exponent >= value:
            high = middle
        else:
            low = middle
    return high


def factorial(value: int) -> int:
    result = 1
    for factor in range(2, value + 1):
        result *= factor
    return result


def squarefree_divisors(primes: tuple[int, ...]) -> list[int]:
    divisors = [1]
    for prime in primes:
        divisors += [divisor * prime for divisor in divisors]
    return sorted(divisors)


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def build_row(m: int) -> dict[str, Any]:
    m_factorial = factorial(m)
    yield_unreduced_numerator = D**m
    yield_unreduced_denominator = m_factorial * P
    exact_yield = Fraction(yield_unreduced_numerator, yield_unreduced_denominator)
    yield_below_one = yield_unreduced_numerator < yield_unreduced_denominator

    condition_1_threshold = ceil_nth_root(P, m)
    balance_threshold = ceil_nth_root(yield_unreduced_denominator, m)

    exponent_binary = format(D, "b")
    squarings = len(exponent_binary) - 1
    nonsquare_multiplications = exponent_binary.count("1") - 1
    multiplication_gates = squarings + nonsquare_multiplications

    direct_per_variable_degree = 1 << (m - 1)
    direct_total_degree = m * direct_per_variable_degree
    recursive_equations = m - 1
    recursive_internal_variables = m - 2

    return {
        "condition_1": {
            "D_meets_threshold": D >= condition_1_threshold,
            "exact_threshold_ceil_p_to_1_over_m": condition_1_threshold,
            "scoped_label": (
                "not_rejected_by_condition_1"
                if D >= condition_1_threshold
                else "bounded_negative_condition_1_for_fixed_D_and_m"
            ),
        },
        "conditional_linear_algebra_minima": {
            "independent_relation_rows_for_full_rank": D,
            "matrix_unknown_columns": D,
            "nominal_coordinate_factor_base_size": D,
            "target_samples_ceiling_under_exact_paper_yield": str(
                ceil_div(D * yield_unreduced_denominator, yield_unreduced_numerator)
            ),
        },
        "direct_semaev": {
            "per_variable_degree": direct_per_variable_degree,
            "polynomial": f"S_{m + 1}",
            "total_degree": direct_total_degree,
        },
        "m": m,
        "paper_balance_and_yield": {
            "D_meets_balance_threshold": D >= balance_threshold,
            "balance_threshold_ceil_m_factorial_p_to_1_over_m": balance_threshold,
            "exact_yield_reduced": {
                "denominator": str(exact_yield.denominator),
                "numerator": str(exact_yield.numerator),
            },
            "expected_trials_for_one_decomposition_ceiling_when_yield_below_one": (
                str(ceil_div(yield_unreduced_denominator, yield_unreduced_numerator))
                if yield_below_one
                else None
            ),
            "scoped_label": (
                "not_rejected_by_paper_balance_predicate"
                if D >= balance_threshold
                else "bounded_negative_paper_balance_for_fixed_D_and_m"
            ),
            "yield_below_one": yield_below_one,
        },
        "recursive_s3": {
            "balanced": {
                "equation_count": recursive_equations,
                "internal_variable_count": recursive_internal_variables,
                "total_nonconstant_x_variables": m + recursive_internal_variables,
            },
            "sequential": {
                "equation_count": recursive_equations,
                "internal_variable_count": recursive_internal_variables,
                "total_nonconstant_x_variables": m + recursive_internal_variables,
            },
        },
        "square_and_multiply_for_m_membership_constraints": {
            "multiplication_gates_upper_bound": m * multiplication_gates,
            "nonsquare_multiplications_upper_bound": m * nonsquare_multiplications,
            "squarings_upper_bound": m * squarings,
        },
        "unresolved": {
            "actual_usable_factor_base_cardinality": None,
            "exceptional_components": None,
            "independent_relation_probability": None,
            "macaulay_matrix_columns": None,
            "macaulay_matrix_memory_bytes": None,
            "macaulay_matrix_rows": None,
            "recovery_branch_count": None,
            "solving_degree": None,
            "total_relation_generation_work": None,
        },
    }


def build_artifact() -> dict[str, Any]:
    divisors = squarefree_divisors(SMALL_PRIME_FACTORS)
    exponent_binary = format(D, "b")
    exponent_squarings = len(exponent_binary) - 1
    exponent_nonsquare_multiplications = exponent_binary.count("1") - 1

    rows = [build_row(m) for m in M_VALUES]
    condition_1_failures = [
        row["m"] for row in rows if not row["condition_1"]["D_meets_threshold"]
    ]
    balance_failures = [
        row["m"]
        for row in rows
        if not row["paper_balance_and_yield"]["D_meets_balance_threshold"]
    ]

    return {
        "artifact_id": "PKC-SMOOTH-DESK-SCREEN-001",
        "assessment": {
            "exact_scoped_bounded_negative_labels": [
                {
                    "label": "condition_1_fails_for_fixed_D_and_m",
                    "m_values": condition_1_failures,
                    "meaning": "D is strictly below ceil(p^(1/m)).",
                },
                {
                    "label": "paper_balance_predicate_fails_for_fixed_D_and_m",
                    "m_values": balance_failures,
                    "meaning": "D^m is strictly below m! p, so the paper's exact yield rational is below one.",
                },
                {
                    "B_max": B_CAP,
                    "coordinate_factor_base_cardinality_upper_bound": 42,
                    "label": "B_smooth_coordinate_root_bound",
                    "meaning": "For B <= 13440, a B-smooth divisor of p-1 divides 2*3*7=42.",
                },
            ],
            "overall_direct_mechanism_label": "inconclusive",
            "reason": (
                "The exact threshold and counting predicates do not determine solving "
                "degree, Macaulay size, recovery, relation independence, or total work."
            ),
        },
        "b_smooth_counting_bound": {
            "B_max_inclusive": B_CAP,
            "coordinate_factor_base_cardinality_upper_bound": 42,
            "eligible_prime_factors_of_p_minus_one": [2, 3, 7],
            "largest_B_smooth_divisor_of_p_minus_one": 42,
            "signed_curve_point_lifts_upper_bound_if_both_y_signs_are_counted": 84,
            "scope": (
                "#F counts roots in the multiplicative subgroup/coset used as "
                "x-coordinate candidates. It does not assert that every root lifts "
                "to a usable curve point or an independent logarithm."
            ),
        },
        "inputs": {
            "D": D,
            "m_max": 20,
            "m_min": 10,
            "p": str(P),
            "p_formula": "2^256 - 2^32 - 977",
        },
        "kind": "deterministic_desk_arithmetic",
        "linear_algebra_scope": {
            "conditional_model": (
                "If the full D-element coordinate root set supplies D active "
                "unknown logarithms, a full-column-rank solve needs at least D "
                "independent rows and D columns."
            ),
            "limitation": (
                "The artifact does not establish usable factor-base cardinality, "
                "row independence, coefficient sparsity, rank, or storage cost."
            ),
        },
        "p_minus_one_factorization": {
            "all_divisors_strictly_below_large_cofactor_given_prime_factorization": divisors,
            "identity": (
                "p - 1 = 2 * 3 * 7 * 13441 * "
                "205115282021455665897114700593932402728804164701536103180137503955397371"
            ),
            "large_cofactor": str(LARGE_COFACTOR),
            "large_cofactor_prime_status": "repository_Lean_certificate_not_replayed_here",
            "small_factor_product_D": D,
            "small_prime_factors": list(SMALL_PRIME_FACTORS),
        },
        "rows": rows,
        "scope": {
            "excluded": [
                "solver execution",
                "toy-field experiments",
                "exact-target relation search",
                "solving-degree estimates",
                "Macaulay-size estimates",
                "recovery-cost estimates",
                "ECDLP complexity or security claims",
            ],
            "included": [
                "exact integer thresholds",
                "exact rational yield arithmetic",
                "degree-formula replay",
                "recursive S3 representation counts",
                "binary square-and-multiply gate upper bounds",
                "conditional factor-base and linear-algebra counts",
            ],
            "threat_model": "classical_single_target_plain_secp256k1",
        },
        "schema_version": "1.0",
        "source_scope": {
            "direct_semaev_degrees": {
                "formula": (
                    "For direct S_(m+1), degree 2^(m-1) in each variable "
                    "and total degree m*2^(m-1)."
                ),
                "scope": (
                    "Formula replay only; no S_(m+1) polynomial is materialized "
                    "and no solving-degree consequence is inferred."
                ),
            },
            "p_and_factorization": {
                "arithmetic_artifact_path": (
                    "experiments/engine/pkc_smooth_desk_screen/artifact.json"
                ),
                "arithmetic_claim_id": "SC-SECP-PMINUS1-FACTORIZATION",
                "large_cofactor_prime_claim_id": (
                    "SC-SECP-PMINUS1-LARGE-COFACTOR-PRIME"
                ),
                "repository_path": "Ecdlp/Proved/Secp256k1PrimeP.lean",
                "scope": (
                    "The arithmetic certificate replays the exact product identity. "
                    "Primality of the 237-bit cofactor remains a separate repository "
                    "Lean theorem and is not reproved by this stdlib artifact."
                ),
            },
            "yield_and_balance": {
                "claim_id": "SC-PKC-RELATION-YIELD",
                "repository_path": (
                    "data/source_claim_extracts/petit_kosters_messeng2016.json"
                ),
                "scope": (
                    "D^m/(m!p) is the paper's heuristic expected decomposition "
                    "yield, not a theorem about independent relations or total cost."
                ),
            },
        },
        "square_and_multiply_model": {
            "algorithm": "left_to_right_binary_from_leading_one",
            "binary_exponent": exponent_binary,
            "bit_length": len(exponent_binary),
            "exponent": D,
            "multiplication_gates_upper_bound_per_membership_constraint": (
                exponent_squarings + exponent_nonsquare_multiplications
            ),
            "nonsquare_multiplications_upper_bound_per_membership_constraint": (
                exponent_nonsquare_multiplications
            ),
            "popcount": exponent_binary.count("1"),
            "scope": (
                "An explicit standard square-and-multiply upper bound. It is not "
                "claimed to be a shortest addition chain or a solving-cost bound."
            ),
            "squarings_upper_bound_per_membership_constraint": exponent_squarings,
        },
    }


def expected_files() -> tuple[bytes, bytes]:
    artifact_bytes = canonical_bytes(build_artifact())
    digest = hashlib.sha256(artifact_bytes).hexdigest()
    hash_bytes = f"{digest}  artifact.json\n".encode("ascii")
    return artifact_bytes, hash_bytes


def check_files() -> int:
    expected_artifact, expected_hash = expected_files()
    failures: list[str] = []
    for path, expected in (
        (ARTIFACT_PATH, expected_artifact),
        (HASH_PATH, expected_hash),
    ):
        try:
            actual = path.read_bytes()
        except FileNotFoundError:
            failures.append(f"missing: {path.name}")
            continue
        if actual != expected:
            failures.append(f"stale or noncanonical: {path.name}")
    if failures:
        for failure in failures:
            print(f"CHECK_FAIL: {failure}", file=sys.stderr)
        return 1
    print("GENERATOR_CHECK_OK")
    return 0


def write_files() -> int:
    artifact_bytes, hash_bytes = expected_files()
    ARTIFACT_PATH.write_bytes(artifact_bytes)
    HASH_PATH.write_bytes(hash_bytes)
    print(f"WROTE {ARTIFACT_PATH.name}")
    print(f"WROTE {HASH_PATH.name}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="check committed outputs")
    mode.add_argument("--stdout", action="store_true", help="print canonical artifact JSON")
    mode.add_argument("--write", action="store_true", help="write artifact and hash")
    args = parser.parse_args()

    if args.check:
        return check_files()
    if args.stdout:
        sys.stdout.buffer.write(expected_files()[0])
        return 0
    return write_files()


if __name__ == "__main__":
    raise SystemExit(main())
