#!/usr/bin/env python3
"""Exact replay for FROBENIUS-STICKELBERGER-DETERMINANT-050.

The classical Frobenius-Stickelberger evaluation determinant for m points
factors into

    public_constant
      * sigma(sum points)
      * product sigma(pair differences)
      / product sigma(point)^m.

After pullback to a normalized rank-two elliptic net W_(G,Q), every preferred-
basis sigma scale cancels by the quadratic identity

    q(sum u_i) + sum_(i<j) q(u_i-u_j) = m sum_i q(u_i).

Therefore the standard coordinate determinant ladder has the net normal form

    D_m(u_1,...,u_m)
      = c_m W(sum u_i) product_(i<j) W(u_i-u_j)
            / product_i W(u_i)^m.

On the retained short-Weierstrass normalization, this replay verifies c_m=1
for the pole-ordered bases of L(mO) at m=3,4,5,6.

Only frozen toy subgroups and public integer vectors are used. No external
point, key, wallet, or production-sized discrete-log target is accepted.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

from nonlocal_odd_anchor_screen import (
    division_polynomial_evaluator,
    orbit,
    quadratic_character,
)
from rank_two_net_multi_cell import (
    FROZEN_CASES,
    rank_two_value,
    scalar_label,
    vector_sub,
)

SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

SMALL_VECTORS = (
    (1, 0),
    (0, 1),
    (1, 1),
    (1, -1),
    (2, 1),
    (1, 2),
    (2, -1),
    (-1, 2),
    (2, 2),
)

FIXED_FOUR_POINT_CANDIDATES = (
    ((1, 0), (0, 1), (1, 1), (1, -1)),
    ((1, 0), (0, 1), (2, 1), (1, 2)),
    ((1, 0), (1, 1), (2, -1), (-1, 2)),
)

ZERO_SUM_FOUR_TUPLES = (
    ((1, 0), (0, 1), (1, -1), (-2, 0)),
    ((1, 0), (0, 1), (-1, 2), (0, -3)),
)


def vector_sum(vectors: tuple[tuple[int, int], ...]) -> tuple[int, int]:
    return (
        sum(vector[0] for vector in vectors),
        sum(vector[1] for vector in vectors),
    )


def determinant_mod(matrix: list[list[int]], field_prime: int) -> int:
    """Exact Gaussian-elimination determinant over F_p."""
    size = len(matrix)
    work = [[value % field_prime for value in row] for row in matrix]
    determinant = 1
    for column in range(size):
        pivot = next(
            (
                row
                for row in range(column, size)
                if work[row][column] % field_prime
            ),
            None,
        )
        if pivot is None:
            return 0
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            determinant = -determinant
        pivot_value = work[column][column] % field_prime
        determinant = determinant * pivot_value % field_prime
        pivot_inverse = pow(pivot_value, -1, field_prime)
        for row in range(column + 1, size):
            factor = work[row][column] * pivot_inverse % field_prime
            if factor == 0:
                continue
            for index in range(column, size):
                work[row][index] = (
                    work[row][index] - factor * work[column][index]
                ) % field_prime
    return determinant % field_prime


def pole_order_basis_row(
    point: tuple[int, int],
    dimension: int,
    field_prime: int,
) -> list[int]:
    """Basis 1,x,y,x^2,xy,x^3,... through pole order dimension."""
    x_coordinate, y_coordinate = point
    row = [1]
    for pole_order in range(2, dimension + 1):
        if pole_order % 2 == 0:
            row.append(pow(x_coordinate, pole_order // 2, field_prime))
        else:
            row.append(
                pow(x_coordinate, (pole_order - 3) // 2, field_prime)
                * y_coordinate
                % field_prime
            )
    if len(row) != dimension:
        raise AssertionError("pole-order basis has incorrect dimension")
    return row


def net_factor(
    rank_two,
    vectors: tuple[tuple[int, int], ...],
    field_prime: int,
) -> int:
    dimension = len(vectors)
    numerator = rank_two(vector_sum(vectors))
    for left_index, right_index in itertools.combinations(
        range(dimension), 2
    ):
        numerator = (
            numerator
            * rank_two(
                vector_sub(vectors[left_index], vectors[right_index])
            )
        ) % field_prime
    denominator = 1
    for vector in vectors:
        denominator = (
            denominator
            * pow(rank_two(vector), dimension, field_prime)
        ) % field_prime
    return numerator * pow(denominator, -1, field_prime) % field_prime


def admissible_points(
    points,
    vectors: tuple[tuple[int, int], ...],
    hidden_scalar: int,
    order: int,
):
    labels = [
        scalar_label(vector, hidden_scalar, order) for vector in vectors
    ]
    if 0 in labels:
        return None
    selected = [points[label] for label in labels]
    if any(point is None for point in selected):
        return None
    if len(set(selected)) != len(selected):
        return None
    return selected


def run_case(
    field_prime: int,
    order: int,
    generator: tuple[int, int],
) -> dict[str, object]:
    points = orbit(generator, order, field_prime)
    psi = division_polynomial_evaluator(generator, field_prime)

    determinant_checks = {dimension: 0 for dimension in range(3, 7)}
    observed_constants = {dimension: set() for dimension in range(3, 7)}
    high_index_checks = 0
    zero_sum_checks = 0

    for hidden_scalar in range(2, min(order - 1, 9)):
        def rank_two(vector: tuple[int, int]) -> int:
            return rank_two_value(
                psi,
                hidden_scalar,
                vector,
                field_prime,
            )

        for dimension in range(3, 7):
            for vectors_raw in itertools.combinations(
                SMALL_VECTORS, dimension
            ):
                vectors = tuple(vectors_raw)
                selected = admissible_points(
                    points, vectors, hidden_scalar, order
                )
                if selected is None:
                    continue
                determinant = determinant_mod(
                    [
                        pole_order_basis_row(
                            point, dimension, field_prime
                        )
                        for point in selected
                    ],
                    field_prime,
                )
                factor = net_factor(rank_two, vectors, field_prime)
                if factor == 0:
                    if determinant != 0:
                        raise AssertionError(
                            "Frobenius-Stickelberger zero factor mismatch"
                        )
                else:
                    observed_constants[dimension].add(
                        determinant * pow(factor, -1, field_prime)
                        % field_prime
                    )
                    if len(observed_constants[dimension]) != 1:
                        raise AssertionError(
                            "determinant normalization constant varied"
                        )
                determinant_checks[dimension] += 1

        high_tuples = (
            (
                (order + 1, 0),
                (0, order + 1),
                (1, 1),
                (1, -1),
            ),
            (
                (2 * order + 1, 0),
                (0, order + 2),
                (1, -1),
                (2, 1),
            ),
            (
                (order + 2, 1),
                (1, order + 2),
                (2, -1),
                (-1, 2),
            ),
        )
        for vectors in high_tuples:
            selected = admissible_points(
                points, vectors, hidden_scalar, order
            )
            if selected is None:
                continue
            determinant = determinant_mod(
                [
                    pole_order_basis_row(point, 4, field_prime)
                    for point in selected
                ],
                field_prime,
            )
            factor = net_factor(rank_two, vectors, field_prime)
            if determinant != factor:
                raise AssertionError(
                    "public high-index four-point factorization failed"
                )
            high_index_checks += 1

        for vectors in ZERO_SUM_FOUR_TUPLES:
            selected = admissible_points(
                points, vectors, hidden_scalar, order
            )
            if selected is None:
                continue
            if vector_sum(vectors) != (0, 0):
                raise AssertionError("declared zero-sum tuple is not zero")
            determinant = determinant_mod(
                [
                    pole_order_basis_row(point, 4, field_prime)
                    for point in selected
                ],
                field_prime,
            )
            factor = net_factor(rank_two, vectors, field_prime)
            if determinant != 0 or factor != 0:
                raise AssertionError("zero-sum determinant did not vanish")
            zero_sum_checks += 1

    character_results: list[dict[str, object]] = []
    for vectors in FIXED_FOUR_POINT_CANDIDATES:
        matches = 0
        mismatches = 0
        zeros_or_exceptions = 0
        for hidden_scalar in range(1, order):
            selected = admissible_points(
                points, vectors, hidden_scalar, order
            )
            if selected is None:
                zeros_or_exceptions += 1
                continue
            determinant = determinant_mod(
                [
                    pole_order_basis_row(point, 4, field_prime)
                    for point in selected
                ],
                field_prime,
            )
            character = quadratic_character(determinant, field_prime)
            if character == 0:
                zeros_or_exceptions += 1
                continue
            parity = 1 if hidden_scalar % 2 == 0 else -1
            if character == parity:
                matches += 1
            else:
                mismatches += 1
        if matches == 0 or mismatches == 0:
            raise AssertionError(
                "fixed Frobenius-Stickelberger determinant matched parity"
            )
        character_results.append(
            {
                "vectors": vectors,
                "matches": matches,
                "mismatches": mismatches,
                "zeros_or_exceptions": zeros_or_exceptions,
                "not_parity_up_to_global_sign": True,
            }
        )

    normalized_constants = {
        str(dimension): sorted(observed_constants[dimension])
        for dimension in range(3, 7)
    }
    if any(values != [1] for values in normalized_constants.values()):
        raise AssertionError("unexpected finite-field determinant constant")

    return {
        "field_prime": field_prime,
        "order": order,
        "generator": generator,
        "determinant_checks": {
            str(dimension): determinant_checks[dimension]
            for dimension in range(3, 7)
        },
        "observed_standard_basis_constants": normalized_constants,
        "high_index_four_point_checks": high_index_checks,
        "zero_sum_four_point_checks": zero_sum_checks,
        "fixed_character_results": character_results,
        "all_standard_determinants_factor": True,
        "all_fixed_characters_reject_parity": True,
    }


def secp256k1_certificate() -> dict[str, object]:
    return {
        "n": SECP_N,
        "bit_length": SECP_N.bit_length(),
        "general_factorization": (
            "c_m*W(sum_i u_i)*product_(i<j)W(u_i-u_j)"
            "/product_i W(u_i)^m"
        ),
        "preferred_basis_scale_cancellation": (
            "q(sum u_i)+sum_(i<j)q(u_i-u_j)=m*sum_i q(u_i)"
        ),
        "valid_for_public_n_dependent_vectors": True,
        "does_standard_determinant_ladder_select_oriented_sqrt": False,
        "selected_successor": "INDEPENDENT-THETA-ROW-NORMALIZATION-051",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "frobenius_stickelberger_determinant_results.json"
        ),
    )
    args = parser.parse_args()

    cases = [run_case(*case) for case in FROZEN_CASES]
    payload = {
        "package": "FROBENIUS-STICKELBERGER-DETERMINANT-050",
        "cases": cases,
        "aggregate": {
            "cases": len(cases),
            "total_m3_checks": sum(
                case["determinant_checks"]["3"] for case in cases
            ),
            "total_m4_checks": sum(
                case["determinant_checks"]["4"] for case in cases
            ),
            "total_m5_checks": sum(
                case["determinant_checks"]["5"] for case in cases
            ),
            "total_m6_checks": sum(
                case["determinant_checks"]["6"] for case in cases
            ),
            "total_high_index_four_point_checks": sum(
                case["high_index_four_point_checks"] for case in cases
            ),
            "total_zero_sum_four_point_checks": sum(
                case["zero_sum_four_point_checks"] for case in cases
            ),
            "total_fixed_character_candidates": sum(
                len(case["fixed_character_results"]) for case in cases
            ),
            "all_standard_determinants_factor": all(
                case["all_standard_determinants_factor"] for case in cases
            ),
            "all_standard_basis_constants_are_one": all(
                all(
                    values == [1]
                    for values in case[
                        "observed_standard_basis_constants"
                    ].values()
                )
                for case in cases
            ),
            "all_fixed_characters_reject_parity": all(
                case["all_fixed_characters_reject_parity"]
                for case in cases
            ),
        },
        "secp256k1": secp256k1_certificate(),
        "decision": (
            "The full standard Frobenius-Stickelberger evaluation-determinant "
            "ladder factors, after normalized rank-two pullback, into one "
            "public constant times a multiplicative net ratio. Quadratic "
            "preferred-basis sigma scales cancel exactly. The common-basis "
            "determinant class therefore supplies no independent equation for "
            "the generator-oriented Kummer root Y_G."
        ),
        "claim_boundary": [
            "The classical general factorization is source-pinned to the Frobenius-Stickelberger sigma determinant.",
            "The finite replay verifies the declared short-Weierstrass bases only for m=3 through m=6.",
            "The package closes common-basis evaluation determinants and their public rank-two pullbacks.",
            "It does not close independently normalized theta rows, twisted characteristics, or p-adic branch selection.",
            "No parity oracle, absolute EDS-residue oracle, or ECDLP improvement is obtained.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["aggregate"], indent=2))
    print(json.dumps(payload["secp256k1"], indent=2))


if __name__ == "__main__":
    main()
