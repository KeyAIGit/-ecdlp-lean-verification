#!/usr/bin/env python3
"""Independently validate the PKC smooth-subgroup desk-screen artifact.

The validator intentionally imports neither ``generate.py`` nor any producer
function.  It independently replays decisive integer arithmetic and verifies
the committed artifact hash.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Any


EXPECTED_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
EXPECTED_D = 564_522
EXPECTED_Q = (
    205115282021455665897114700593932402728804164701536103180137503955397371
)
EXPECTED_SMALL_FACTORS = (2, 3, 7, 13_441)
EXPECTED_B_CAP = 13_440
EXPECTED_M_VALUES = tuple(range(10, 21))
HERE = Path(__file__).resolve().parent


class Replay:
    def __init__(self) -> None:
        self.failures: list[str] = []

    def expect(self, path: str, actual: Any, expected: Any) -> None:
        if actual != expected:
            self.failures.append(
                f"{path}: expected {expected!r}, observed {actual!r}"
            )

    def require_dict(self, path: str, value: Any) -> dict[str, Any]:
        if not isinstance(value, dict):
            self.failures.append(f"{path}: expected object")
            return {}
        return value

    def require_list(self, path: str, value: Any) -> list[Any]:
        if not isinstance(value, list):
            self.failures.append(f"{path}: expected array")
            return []
        return value


def integer_factorial(value: int) -> int:
    accumulator = 1
    counter = value
    while counter > 1:
        accumulator *= counter
        counter -= 1
    return accumulator


def ceil_ratio(numerator: int, denominator: int) -> int:
    quotient, remainder = divmod(numerator, denominator)
    return quotient + (1 if remainder else 0)


def ceil_root_newton(value: int, exponent: int) -> int:
    """Independent nth-root replay using integer Newton iteration."""
    if value <= 1:
        return value
    estimate = 1 << ((value.bit_length() + exponent - 1) // exponent)
    while True:
        denominator = estimate ** (exponent - 1)
        updated = ((exponent - 1) * estimate + value // denominator) // exponent
        if updated >= estimate:
            break
        estimate = updated
    while (estimate + 1) ** exponent <= value:
        estimate += 1
    while estimate**exponent > value:
        estimate -= 1
    return estimate if estimate**exponent == value else estimate + 1


def reduced_pair(numerator: int, denominator: int) -> tuple[int, int]:
    common = math.gcd(numerator, denominator)
    return numerator // common, denominator // common


def independent_divisor_enumeration(primes: tuple[int, ...]) -> list[int]:
    products: set[int] = set()
    for mask in range(1 << len(primes)):
        product = 1
        for index, prime in enumerate(primes):
            if mask & (1 << index):
                product *= prime
        products.add(product)
    return sorted(products)


def is_prime_by_trial_division(value: int) -> bool:
    if value < 2:
        return False
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor = 3 if divisor == 2 else divisor + 2
    return True


def get(mapping: dict[str, Any], key: str, path: str, replay: Replay) -> Any:
    if key not in mapping:
        replay.failures.append(f"{path}.{key}: missing")
        return None
    return mapping[key]


def check_hash(
    artifact_path: Path, hash_path: Path, artifact_bytes: bytes, replay: Replay
) -> None:
    try:
        hash_text = hash_path.read_text(encoding="ascii")
    except (FileNotFoundError, UnicodeDecodeError) as error:
        replay.failures.append(f"hash file unreadable: {error}")
        return
    match = re.fullmatch(r"([0-9a-f]{64})  artifact\.json\n", hash_text)
    if match is None:
        replay.failures.append(
            "artifact.sha256: expected '<64 lowercase hex>  artifact.json\\n'"
        )
        return
    observed_digest = hashlib.sha256(artifact_bytes).hexdigest()
    replay.expect("artifact.sha256.digest", match.group(1), observed_digest)


def check_metadata(document: dict[str, Any], replay: Replay) -> None:
    replay.expect("schema_version", document.get("schema_version"), "1.0")
    replay.expect(
        "artifact_id", document.get("artifact_id"), "PKC-SMOOTH-DESK-SCREEN-001"
    )
    replay.expect("kind", document.get("kind"), "deterministic_desk_arithmetic")

    inputs = replay.require_dict("inputs", document.get("inputs"))
    replay.expect("inputs.p", inputs.get("p"), str(EXPECTED_P))
    replay.expect("inputs.D", inputs.get("D"), EXPECTED_D)
    replay.expect("inputs.m_min", inputs.get("m_min"), 10)
    replay.expect("inputs.m_max", inputs.get("m_max"), 20)

    scope = replay.require_dict("scope", document.get("scope"))
    excluded = replay.require_list("scope.excluded", scope.get("excluded"))
    for required_exclusion in (
        "solver execution",
        "exact-target relation search",
        "solving-degree estimates",
        "Macaulay-size estimates",
        "recovery-cost estimates",
        "ECDLP complexity or security claims",
    ):
        if required_exclusion not in excluded:
            replay.failures.append(
                f"scope.excluded: missing {required_exclusion!r}"
            )

    assessment = replay.require_dict("assessment", document.get("assessment"))
    replay.expect(
        "assessment.overall_direct_mechanism_label",
        assessment.get("overall_direct_mechanism_label"),
        "inconclusive",
    )
    scoped_labels = replay.require_list(
        "assessment.exact_scoped_bounded_negative_labels",
        assessment.get("exact_scoped_bounded_negative_labels"),
    )
    replay.expect(
        "assessment.condition_1_failure_set",
        scoped_labels[0].get("m_values")
        if len(scoped_labels) > 0 and isinstance(scoped_labels[0], dict)
        else None,
        [10, 11, 12, 13],
    )
    replay.expect(
        "assessment.paper_balance_failure_set",
        scoped_labels[1].get("m_values")
        if len(scoped_labels) > 1 and isinstance(scoped_labels[1], dict)
        else None,
        [10, 11, 12, 13, 14, 15],
    )
    replay.expect(
        "assessment.B_smooth_bound",
        (
            scoped_labels[2].get("B_max"),
            scoped_labels[2].get("coordinate_factor_base_cardinality_upper_bound"),
        )
        if len(scoped_labels) > 2 and isinstance(scoped_labels[2], dict)
        else None,
        (EXPECTED_B_CAP, 42),
    )

    source_scope = replay.require_dict(
        "source_scope", document.get("source_scope")
    )
    p_source = replay.require_dict(
        "source_scope.p_and_factorization",
        source_scope.get("p_and_factorization"),
    )
    replay.expect(
        "source_scope.p_and_factorization.arithmetic_claim_id",
        p_source.get("arithmetic_claim_id"),
        "SC-SECP-PMINUS1-FACTORIZATION",
    )
    replay.expect(
        "source_scope.p_and_factorization.arithmetic_artifact_path",
        p_source.get("arithmetic_artifact_path"),
        "experiments/engine/pkc_smooth_desk_screen/artifact.json",
    )
    replay.expect(
        "source_scope.p_and_factorization.large_cofactor_prime_claim_id",
        p_source.get("large_cofactor_prime_claim_id"),
        "SC-SECP-PMINUS1-LARGE-COFACTOR-PRIME",
    )
    replay.expect(
        "source_scope.p_and_factorization.repository_path",
        p_source.get("repository_path"),
        "Ecdlp/Proved/Secp256k1PrimeP.lean",
    )
    yield_source = replay.require_dict(
        "source_scope.yield_and_balance",
        source_scope.get("yield_and_balance"),
    )
    replay.expect(
        "source_scope.yield_and_balance.claim_id",
        yield_source.get("claim_id"),
        "SC-PKC-RELATION-YIELD",
    )
    replay.expect(
        "source_scope.yield_and_balance.repository_path",
        yield_source.get("repository_path"),
        "data/source_claim_extracts/petit_kosters_messeng2016.json",
    )


def check_factorization(document: dict[str, Any], replay: Replay) -> None:
    section = replay.require_dict(
        "p_minus_one_factorization", document.get("p_minus_one_factorization")
    )
    replay.expect(
        "p_minus_one_factorization.large_cofactor",
        section.get("large_cofactor"),
        str(EXPECTED_Q),
    )
    replay.expect(
        "p_minus_one_factorization.small_prime_factors",
        section.get("small_prime_factors"),
        list(EXPECTED_SMALL_FACTORS),
    )

    for prime in EXPECTED_SMALL_FACTORS:
        replay.expect(
            f"small_factor_primality[{prime}]",
            is_prime_by_trial_division(prime),
            True,
        )

    product = math.prod(EXPECTED_SMALL_FACTORS)
    replay.expect("small_factor_product", product, EXPECTED_D)
    replay.expect(
        "p_minus_one_factorization.small_factor_product_D",
        section.get("small_factor_product_D"),
        product,
    )
    replay.expect(
        "factorization_identity",
        product * EXPECTED_Q,
        EXPECTED_P - 1,
    )
    replay.expect("large_cofactor_gt_D", EXPECTED_Q > EXPECTED_D, True)

    expected_divisors = independent_divisor_enumeration(EXPECTED_SMALL_FACTORS)
    replay.expect(
        "p_minus_one_factorization."
        "all_divisors_strictly_below_large_cofactor_given_prime_factorization",
        section.get(
            "all_divisors_strictly_below_large_cofactor_given_prime_factorization"
        ),
        expected_divisors,
    )
    replay.expect(
        "p_minus_one_factorization.large_cofactor_prime_status",
        section.get("large_cofactor_prime_status"),
        "repository_Lean_certificate_not_replayed_here",
    )


def check_b_smooth_bound(document: dict[str, Any], replay: Replay) -> None:
    section = replay.require_dict(
        "b_smooth_counting_bound", document.get("b_smooth_counting_bound")
    )
    replay.expect(
        "b_smooth_counting_bound.B_max_inclusive",
        section.get("B_max_inclusive"),
        EXPECTED_B_CAP,
    )
    eligible = [
        factor for factor in EXPECTED_SMALL_FACTORS if factor <= EXPECTED_B_CAP
    ]
    replay.expect(
        "b_smooth_counting_bound.eligible_prime_factors_of_p_minus_one",
        section.get("eligible_prime_factors_of_p_minus_one"),
        eligible,
    )
    largest = math.prod(eligible)
    replay.expect(
        "b_smooth_counting_bound.largest_B_smooth_divisor_of_p_minus_one",
        section.get("largest_B_smooth_divisor_of_p_minus_one"),
        largest,
    )
    replay.expect(
        "b_smooth_counting_bound.coordinate_factor_base_cardinality_upper_bound",
        section.get("coordinate_factor_base_cardinality_upper_bound"),
        42,
    )
    replay.expect(
        "b_smooth_counting_bound."
        "signed_curve_point_lifts_upper_bound_if_both_y_signs_are_counted",
        section.get(
            "signed_curve_point_lifts_upper_bound_if_both_y_signs_are_counted"
        ),
        84,
    )


def check_exponentiation(document: dict[str, Any], replay: Replay) -> tuple[int, int, int]:
    section = replay.require_dict(
        "square_and_multiply_model", document.get("square_and_multiply_model")
    )
    binary = bin(EXPECTED_D)[2:]
    bit_length = EXPECTED_D.bit_length()
    popcount = EXPECTED_D.bit_count()
    squarings = bit_length - 1
    nonsquare = popcount - 1
    total = squarings + nonsquare
    replay.expect("square_and_multiply_model.exponent", section.get("exponent"), EXPECTED_D)
    replay.expect(
        "square_and_multiply_model.binary_exponent",
        section.get("binary_exponent"),
        binary,
    )
    replay.expect(
        "square_and_multiply_model.bit_length",
        section.get("bit_length"),
        bit_length,
    )
    replay.expect(
        "square_and_multiply_model.popcount", section.get("popcount"), popcount
    )
    replay.expect(
        "square_and_multiply_model.squarings_upper_bound_per_membership_constraint",
        section.get("squarings_upper_bound_per_membership_constraint"),
        squarings,
    )
    replay.expect(
        "square_and_multiply_model."
        "nonsquare_multiplications_upper_bound_per_membership_constraint",
        section.get(
            "nonsquare_multiplications_upper_bound_per_membership_constraint"
        ),
        nonsquare,
    )
    replay.expect(
        "square_and_multiply_model."
        "multiplication_gates_upper_bound_per_membership_constraint",
        section.get("multiplication_gates_upper_bound_per_membership_constraint"),
        total,
    )
    return squarings, nonsquare, total


def check_row(
    row: dict[str, Any],
    m: int,
    squarings: int,
    nonsquare: int,
    gates: int,
    replay: Replay,
) -> None:
    prefix = f"rows[m={m}]"
    replay.expect(f"{prefix}.m", row.get("m"), m)

    m_factorial = integer_factorial(m)
    raw_numerator = EXPECTED_D**m
    raw_denominator = m_factorial * EXPECTED_P
    reduced_numerator, reduced_denominator = reduced_pair(
        raw_numerator, raw_denominator
    )
    condition_threshold = ceil_root_newton(EXPECTED_P, m)
    balance_threshold = ceil_root_newton(raw_denominator, m)
    condition_pass = EXPECTED_D >= condition_threshold
    balance_pass = EXPECTED_D >= balance_threshold
    yield_below_one = raw_numerator < raw_denominator

    condition = replay.require_dict(
        f"{prefix}.condition_1", row.get("condition_1")
    )
    replay.expect(
        f"{prefix}.condition_1.exact_threshold_ceil_p_to_1_over_m",
        condition.get("exact_threshold_ceil_p_to_1_over_m"),
        condition_threshold,
    )
    replay.expect(
        f"{prefix}.condition_1.D_meets_threshold",
        condition.get("D_meets_threshold"),
        condition_pass,
    )
    replay.expect(
        f"{prefix}.condition_1.scoped_label",
        condition.get("scoped_label"),
        (
            "not_rejected_by_condition_1"
            if condition_pass
            else "bounded_negative_condition_1_for_fixed_D_and_m"
        ),
    )

    balance = replay.require_dict(
        f"{prefix}.paper_balance_and_yield", row.get("paper_balance_and_yield")
    )
    replay.expect(
        f"{prefix}.paper_balance_and_yield."
        "balance_threshold_ceil_m_factorial_p_to_1_over_m",
        balance.get("balance_threshold_ceil_m_factorial_p_to_1_over_m"),
        balance_threshold,
    )
    replay.expect(
        f"{prefix}.paper_balance_and_yield.D_meets_balance_threshold",
        balance.get("D_meets_balance_threshold"),
        balance_pass,
    )
    exact_yield = replay.require_dict(
        f"{prefix}.paper_balance_and_yield.exact_yield_reduced",
        balance.get("exact_yield_reduced"),
    )
    replay.expect(
        f"{prefix}.paper_balance_and_yield.exact_yield_reduced.numerator",
        exact_yield.get("numerator"),
        str(reduced_numerator),
    )
    replay.expect(
        f"{prefix}.paper_balance_and_yield.exact_yield_reduced.denominator",
        exact_yield.get("denominator"),
        str(reduced_denominator),
    )
    replay.expect(
        f"{prefix}.paper_balance_and_yield.yield_below_one",
        balance.get("yield_below_one"),
        yield_below_one,
    )
    expected_trials = (
        str(ceil_ratio(raw_denominator, raw_numerator))
        if yield_below_one
        else None
    )
    replay.expect(
        f"{prefix}.paper_balance_and_yield."
        "expected_trials_for_one_decomposition_ceiling_when_yield_below_one",
        balance.get(
            "expected_trials_for_one_decomposition_ceiling_when_yield_below_one"
        ),
        expected_trials,
    )
    replay.expect(
        f"{prefix}.paper_balance_and_yield.scoped_label",
        balance.get("scoped_label"),
        (
            "not_rejected_by_paper_balance_predicate"
            if balance_pass
            else "bounded_negative_paper_balance_for_fixed_D_and_m"
        ),
    )

    direct = replay.require_dict(
        f"{prefix}.direct_semaev", row.get("direct_semaev")
    )
    per_variable_degree = 2 ** (m - 1)
    replay.expect(f"{prefix}.direct_semaev.polynomial", direct.get("polynomial"), f"S_{m + 1}")
    replay.expect(
        f"{prefix}.direct_semaev.per_variable_degree",
        direct.get("per_variable_degree"),
        per_variable_degree,
    )
    replay.expect(
        f"{prefix}.direct_semaev.total_degree",
        direct.get("total_degree"),
        m * per_variable_degree,
    )

    recursive = replay.require_dict(
        f"{prefix}.recursive_s3", row.get("recursive_s3")
    )
    for representation in ("sequential", "balanced"):
        counts = replay.require_dict(
            f"{prefix}.recursive_s3.{representation}",
            recursive.get(representation),
        )
        replay.expect(
            f"{prefix}.recursive_s3.{representation}.equation_count",
            counts.get("equation_count"),
            m - 1,
        )
        replay.expect(
            f"{prefix}.recursive_s3.{representation}.internal_variable_count",
            counts.get("internal_variable_count"),
            m - 2,
        )
        replay.expect(
            f"{prefix}.recursive_s3.{representation}.total_nonconstant_x_variables",
            counts.get("total_nonconstant_x_variables"),
            2 * m - 2,
        )

    exponent_counts = replay.require_dict(
        f"{prefix}.square_and_multiply_for_m_membership_constraints",
        row.get("square_and_multiply_for_m_membership_constraints"),
    )
    replay.expect(
        f"{prefix}.square_and_multiply.squarings",
        exponent_counts.get("squarings_upper_bound"),
        m * squarings,
    )
    replay.expect(
        f"{prefix}.square_and_multiply.nonsquare_multiplications",
        exponent_counts.get("nonsquare_multiplications_upper_bound"),
        m * nonsquare,
    )
    replay.expect(
        f"{prefix}.square_and_multiply.multiplication_gates",
        exponent_counts.get("multiplication_gates_upper_bound"),
        m * gates,
    )

    linear_algebra = replay.require_dict(
        f"{prefix}.conditional_linear_algebra_minima",
        row.get("conditional_linear_algebra_minima"),
    )
    for key in (
        "nominal_coordinate_factor_base_size",
        "matrix_unknown_columns",
        "independent_relation_rows_for_full_rank",
    ):
        replay.expect(
            f"{prefix}.conditional_linear_algebra_minima.{key}",
            linear_algebra.get(key),
            EXPECTED_D,
        )
    replay.expect(
        f"{prefix}.conditional_linear_algebra_minima."
        "target_samples_ceiling_under_exact_paper_yield",
        linear_algebra.get("target_samples_ceiling_under_exact_paper_yield"),
        str(ceil_ratio(EXPECTED_D * raw_denominator, raw_numerator)),
    )

    unresolved = replay.require_dict(
        f"{prefix}.unresolved", row.get("unresolved")
    )
    required_unresolved = {
        "actual_usable_factor_base_cardinality",
        "exceptional_components",
        "independent_relation_probability",
        "macaulay_matrix_columns",
        "macaulay_matrix_memory_bytes",
        "macaulay_matrix_rows",
        "recovery_branch_count",
        "solving_degree",
        "total_relation_generation_work",
    }
    replay.expect(
        f"{prefix}.unresolved.keys", set(unresolved), required_unresolved
    )
    for key in required_unresolved:
        replay.expect(f"{prefix}.unresolved.{key}", unresolved.get(key), None)


def check_rows(document: dict[str, Any], replay: Replay) -> None:
    squarings, nonsquare, gates = check_exponentiation(document, replay)
    raw_rows = replay.require_list("rows", document.get("rows"))
    replay.expect("rows.length", len(raw_rows), len(EXPECTED_M_VALUES))
    rows_by_m: dict[int, dict[str, Any]] = {}
    for index, raw_row in enumerate(raw_rows):
        row = replay.require_dict(f"rows[{index}]", raw_row)
        m = row.get("m")
        if not isinstance(m, int):
            replay.failures.append(f"rows[{index}].m: expected integer")
            continue
        if m in rows_by_m:
            replay.failures.append(f"rows: duplicate m={m}")
        rows_by_m[m] = row
    replay.expect("rows.m_values", sorted(rows_by_m), list(EXPECTED_M_VALUES))
    for m in EXPECTED_M_VALUES:
        if m in rows_by_m:
            check_row(rows_by_m[m], m, squarings, nonsquare, gates, replay)


def validate(artifact_path: Path, hash_path: Path) -> int:
    replay = Replay()
    try:
        artifact_bytes = artifact_path.read_bytes()
    except FileNotFoundError as error:
        print(f"VALIDATION_FAIL: {error}", file=sys.stderr)
        return 1

    check_hash(artifact_path, hash_path, artifact_bytes, replay)
    try:
        document = json.loads(artifact_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        print(f"VALIDATION_FAIL: artifact JSON unreadable: {error}", file=sys.stderr)
        return 1
    if not isinstance(document, dict):
        print("VALIDATION_FAIL: artifact root must be an object", file=sys.stderr)
        return 1

    canonical = (
        json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    replay.expect("artifact canonical JSON bytes", artifact_bytes, canonical)

    check_metadata(document, replay)
    check_factorization(document, replay)
    check_b_smooth_bound(document, replay)
    check_rows(document, replay)

    if replay.failures:
        for failure in replay.failures:
            print(f"VALIDATION_FAIL: {failure}", file=sys.stderr)
        return 1
    print("VALIDATION_OK")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--artifact",
        type=Path,
        default=HERE / "artifact.json",
        help="artifact to validate (supports fault-injection copies)",
    )
    parser.add_argument(
        "--hash-file",
        type=Path,
        default=HERE / "artifact.sha256",
        help="hash sidecar to validate",
    )
    args = parser.parse_args()
    return validate(args.artifact, args.hash_file)


if __name__ == "__main__":
    raise SystemExit(main())
