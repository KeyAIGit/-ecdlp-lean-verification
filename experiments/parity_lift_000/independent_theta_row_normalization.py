#!/usr/bin/env python3
"""Exact replay for INDEPENDENT-THETA-ROW-NORMALIZATION-051.

For one common section basis, changing the local trivialization at evaluation
point P_i multiplies every entry in row i by one scalar r_i.  A public common
basis change multiplies on the right by one matrix C.  Hence

    det(diag(r) A C) = product(r_i) det(A) det(C).

The determinant adds no new cross-row orientation: after removing the common
Frobenius-Stickelberger factor, the complete residual is the product of the row
factors.  This script verifies the identity on the actual pole-ordered
finite-field evaluation matrices used by package 050.

Only frozen toy subgroups and public points are used. No external point, key,
wallet, or production-sized discrete-log target is accepted.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

from frobenius_stickelberger_determinant import (
    FROZEN_CASES,
    SMALL_VECTORS,
    admissible_points,
    determinant_mod,
    pole_order_basis_row,
)
from nonlocal_odd_anchor_screen import orbit, quadratic_character

SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def matrix_multiply(
    left: list[list[int]],
    right: list[list[int]],
    field_prime: int,
) -> list[list[int]]:
    if len(left[0]) != len(right):
        raise AssertionError("matrix dimensions do not match")
    return [
        [
            sum(
                left[row][inner] * right[inner][column]
                for inner in range(len(right))
            )
            % field_prime
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def diagonal_matrix(values: list[int]) -> list[list[int]]:
    size = len(values)
    return [
        [values[row] if row == column else 0 for column in range(size)]
        for row in range(size)
    ]


def common_basis_change(
    dimension: int,
    field_prime: int,
) -> list[list[int]]:
    """A fixed invertible upper-triangular public basis change."""
    matrix = [[0] * dimension for _ in range(dimension)]
    for row in range(dimension):
        matrix[row][row] = row + 1
        for column in range(row + 1, dimension):
            matrix[row][column] = (row + column + 1) % field_prime
    return matrix


def row_factor_families(
    points: list[tuple[int, int]],
    field_prime: int,
) -> tuple[list[int], ...]:
    return (
        [point[1] % field_prime for point in points],
        [
            (point[0] + row + 1) % field_prime
            for row, point in enumerate(points)
        ],
        [
            (pow(point[0], 3, field_prime) + 2 * row + 1)
            % field_prime
            for row, point in enumerate(points)
        ],
    )


def product(values: list[int], field_prime: int) -> int:
    result = 1
    for value in values:
        result = result * value % field_prime
    return result


def run_case(
    field_prime: int,
    order: int,
    generator: tuple[int, int],
) -> dict[str, object]:
    points = orbit(generator, order, field_prime)

    determinant_factorization_checks = 0
    character_quotient_checks = 0
    same_product_sign_checks = 0
    one_flip_sign_checks = 0

    for hidden_scalar in range(2, min(order - 1, 9)):
        for dimension in range(3, 7):
            basis_change = common_basis_change(dimension, field_prime)
            basis_change_determinant = determinant_mod(
                basis_change, field_prime
            )
            if basis_change_determinant == 0:
                raise AssertionError("declared basis change is singular")

            vector_tuples = itertools.islice(
                itertools.combinations(SMALL_VECTORS, dimension),
                30,
            )
            for vectors_raw in vector_tuples:
                vectors = tuple(vectors_raw)
                selected = admissible_points(
                    points, vectors, hidden_scalar, order
                )
                if selected is None:
                    continue
                base_matrix = [
                    pole_order_basis_row(
                        point, dimension, field_prime
                    )
                    for point in selected
                ]
                base_determinant = determinant_mod(
                    base_matrix, field_prime
                )

                for row_factors in row_factor_families(
                    selected, field_prime
                ):
                    if 0 in row_factors:
                        continue
                    transformed = matrix_multiply(
                        matrix_multiply(
                            diagonal_matrix(row_factors),
                            base_matrix,
                            field_prime,
                        ),
                        basis_change,
                        field_prime,
                    )
                    transformed_determinant = determinant_mod(
                        transformed, field_prime
                    )
                    expected = (
                        product(row_factors, field_prime)
                        * base_determinant
                        * basis_change_determinant
                    ) % field_prime
                    if transformed_determinant != expected:
                        raise AssertionError(
                            "row-trivialization determinant factorization failed"
                        )
                    determinant_factorization_checks += 1

                    if (
                        transformed_determinant != 0
                        and base_determinant != 0
                    ):
                        observed_character = quadratic_character(
                            transformed_determinant, field_prime
                        )
                        expected_character = (
                            quadratic_character(
                                product(row_factors, field_prime),
                                field_prime,
                            )
                            * quadratic_character(
                                base_determinant, field_prime
                            )
                            * quadratic_character(
                                basis_change_determinant,
                                field_prime,
                            )
                        )
                        if observed_character != expected_character:
                            raise AssertionError(
                                "quadratic-character quotient failed"
                            )
                        character_quotient_checks += 1

                    two_flip = [
                        field_prime - 1,
                        field_prime - 1,
                        *([1] * (dimension - 2)),
                    ]
                    same_product_matrix = matrix_multiply(
                        diagonal_matrix(two_flip),
                        transformed,
                        field_prime,
                    )
                    if determinant_mod(
                        same_product_matrix, field_prime
                    ) != transformed_determinant:
                        raise AssertionError(
                            "same-product sign vector changed determinant"
                        )
                    same_product_sign_checks += 1

                    one_flip = [
                        field_prime - 1,
                        *([1] * (dimension - 1)),
                    ]
                    one_flip_matrix = matrix_multiply(
                        diagonal_matrix(one_flip),
                        transformed,
                        field_prime,
                    )
                    if determinant_mod(
                        one_flip_matrix, field_prime
                    ) != (-transformed_determinant) % field_prime:
                        raise AssertionError(
                            "single sign flip did not negate determinant"
                        )
                    one_flip_sign_checks += 1

    return {
        "field_prime": field_prime,
        "order": order,
        "generator": generator,
        "determinant_factorization_checks": determinant_factorization_checks,
        "character_quotient_checks": character_quotient_checks,
        "same_product_sign_checks": same_product_sign_checks,
        "one_flip_sign_checks": one_flip_sign_checks,
        "all_row_trivializations_factor": True,
        "all_character_quotients_exact": True,
        "determinant_sees_only_sign_product": True,
    }


def secp256k1_certificate() -> dict[str, object]:
    return {
        "n": SECP_N,
        "bit_length": SECP_N.bit_length(),
        "general_factorization": (
            "det(diag(r) A C)=product_i(r_i)*det(A)*det(C)"
        ),
        "residual_after_common_determinant": "product_i(r_i)",
        "same_product_sign_multiplicity": "2^(m-1)",
        "does_scalar_row_normalization_select_oriented_sqrt": False,
        "selected_successor": "TWISTED-THETA-CHARACTERISTIC-052",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "independent_theta_row_normalization_results.json"
        ),
    )
    args = parser.parse_args()

    cases = [run_case(*case) for case in FROZEN_CASES]
    payload = {
        "package": "INDEPENDENT-THETA-ROW-NORMALIZATION-051",
        "cases": cases,
        "aggregate": {
            "cases": len(cases),
            "total_determinant_factorization_checks": sum(
                case["determinant_factorization_checks"] for case in cases
            ),
            "total_character_quotient_checks": sum(
                case["character_quotient_checks"] for case in cases
            ),
            "total_same_product_sign_checks": sum(
                case["same_product_sign_checks"] for case in cases
            ),
            "total_one_flip_sign_checks": sum(
                case["one_flip_sign_checks"] for case in cases
            ),
            "all_row_trivializations_factor": all(
                case["all_row_trivializations_factor"] for case in cases
            ),
            "all_character_quotients_exact": all(
                case["all_character_quotients_exact"] for case in cases
            ),
            "determinant_sees_only_sign_product": all(
                case["determinant_sees_only_sign_product"]
                for case in cases
            ),
        },
        "secp256k1": secp256k1_certificate(),
        "decision": (
            "Independent scalar local trivializations and a common public "
            "basis change factor completely out of the determinant. After "
            "removing the package-050 common determinant, the entire residual "
            "is product_i r_i. Any target bit in this class is already present "
            "in that explicit product; the determinant creates no new "
            "cross-row generator orientation."
        ),
        "claim_boundary": [
            "The determinant factorization is exact ordinary linear algebra.",
            "The replay checks the identity on actual package-050 evaluation matrices.",
            "The package closes scalar row trivializations and one common basis change only.",
            "It does not close different theta characteristics or row-dependent section spaces.",
            "No parity oracle, absolute EDS-residue oracle, or ECDLP improvement is obtained.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["aggregate"], indent=2))
    print(json.dumps(payload["secp256k1"], indent=2))


if __name__ == "__main__":
    main()
