#!/usr/bin/env python3
"""Exact replay for RANK-TWO-NET-MULTI-CELL-049.

Package 048 closed the rank-one Ward minor grammar. This package leaves that
geometry and studies the first genuinely rank-two, three-point additive
determinant.

For a normalized rank-two elliptic net W associated to marked points (G,Q),
write, for u in Z^2,

    P_u = [u_1]G + [u_2]Q,
    X_u = x(P_u),
    Y_u = y(P_u).

On the nondegenerate chart, the three-row coordinate determinant

    D(u,v,w)
      = Y_u (X_v-X_w) + Y_v (X_w-X_u) + Y_w (X_u-X_v)

is the numerator of the rank-three net polynomial Omega_(1,1,1) evaluated on
(P_u,P_v,P_w). Matrix pullback and the net x-difference identity give

    D(u,v,w)
      = - W(u+v+w) W(u-v) W(u-w) W(v-w)
          / (W(u)^3 W(v)^3 W(w)^3).

Thus the smallest coupled rank-two 3x3 determinant collapses exactly to a
multiplicative rank-two net ratio. It does not define a new additive equation
for the generator-oriented Kummer square root Y_G.

Only frozen toy subgroups and public integer indices are used. No external
point, key, wallet, or production-sized discrete-log target is accepted.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

from nonlocal_odd_anchor_screen import (
    division_polynomial_evaluator,
    ec_add,
    orbit,
    quadratic_character,
)

SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

FROZEN_CASES = (
    (151, 19, (70, 122)),
    (43, 31, (2, 12)),
    (79, 67, (1, 18)),
    (1087, 271, (1017, 688)),
    (2851, 397, (2276, 1015)),
    (1663, 433, (126, 1375)),
)

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

FIXED_CHARACTER_TRIPLES = (
    ((1, 0), (0, 1), (1, 1)),
    ((1, 0), (0, 1), (1, -1)),
    ((1, 0), (1, 1), (1, 2)),
    ((1, 0), (0, 1), (2, 1)),
)


def vector_add(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int]:
    return left[0] + right[0], left[1] + right[1]


def vector_sub(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int]:
    return left[0] - right[0], left[1] - right[1]


def vector_sum(
    first: tuple[int, int],
    second: tuple[int, int],
    third: tuple[int, int],
) -> tuple[int, int]:
    return first[0] + second[0] + third[0], first[1] + second[1] + third[1]


def scalar_label(vector: tuple[int, int], hidden_scalar: int, order: int) -> int:
    return (vector[0] + vector[1] * hidden_scalar) % order


def signed_power(value: int, exponent: int, field_prime: int) -> int:
    value %= field_prime
    if exponent >= 0:
        return pow(value, exponent, field_prime)
    return pow(pow(value, -1, field_prime), -exponent, field_prime)


def rank_two_value(
    psi,
    hidden_scalar: int,
    vector: tuple[int, int],
    field_prime: int,
) -> int:
    """Matrix-pullback normalization for W_(G,[k]G)(a,b)."""
    a, b = vector
    numerator = psi(a + b * hidden_scalar)
    exponent_k = b * b - a * b
    exponent_k_plus_one = a * b
    denominator = (
        signed_power(psi(hidden_scalar), exponent_k, field_prime)
        * signed_power(
            psi(hidden_scalar + 1),
            exponent_k_plus_one,
            field_prime,
        )
    ) % field_prime
    return numerator * pow(denominator, -1, field_prime) % field_prime


def coordinate_determinant(
    first: tuple[int, int],
    second: tuple[int, int],
    third: tuple[int, int],
    field_prime: int,
) -> int:
    x_first, y_first = first
    x_second, y_second = second
    x_third, y_third = third
    return (
        y_first * (x_second - x_third)
        + y_second * (x_third - x_first)
        + y_third * (x_first - x_second)
    ) % field_prime


def determinant_factor(
    rank_two,
    first: tuple[int, int],
    second: tuple[int, int],
    third: tuple[int, int],
    field_prime: int,
) -> int:
    denominator = (
        pow(rank_two(first), 3, field_prime)
        * pow(rank_two(second), 3, field_prime)
        * pow(rank_two(third), 3, field_prime)
    ) % field_prime
    numerator = (
        -rank_two(vector_sum(first, second, third))
        * rank_two(vector_sub(first, second))
        * rank_two(vector_sub(first, third))
        * rank_two(vector_sub(second, third))
    ) % field_prime
    return numerator * pow(denominator, -1, field_prime) % field_prime


def run_case(
    field_prime: int,
    order: int,
    generator: tuple[int, int],
) -> dict[str, object]:
    points = orbit(generator, order, field_prime)
    psi = division_polynomial_evaluator(generator, field_prime)

    normalization_checks = 0
    determinant_checks = 0
    zero_sum_collinearity_checks = 0
    high_index_checks = 0

    query_scalars = range(2, min(order - 1, 10))
    for hidden_scalar in query_scalars:
        query = points[hidden_scalar]
        if query is None:
            raise AssertionError("nonzero query scalar produced the identity")

        def rank_two(vector: tuple[int, int]) -> int:
            return rank_two_value(psi, hidden_scalar, vector, field_prime)

        point_sum = ec_add(generator, query, field_prime)
        if point_sum is None:
            raise AssertionError("retained G+Q was the identity")

        expected_values = (
            (rank_two((1, 0)), 1),
            (rank_two((0, 1)), 1),
            (rank_two((1, 1)), 1),
            (rank_two((2, 0)), 2 * generator[1] % field_prime),
            (rank_two((0, 2)), 2 * query[1] % field_prime),
            (rank_two((1, -1)), (query[0] - generator[0]) % field_prime),
            (rank_two((2, 1)), (generator[0] - point_sum[0]) % field_prime),
            (rank_two((1, 2)), (query[0] - point_sum[0]) % field_prime),
            (rank_two((2, 2)), 2 * point_sum[1] % field_prime),
        )
        for observed, expected in expected_values:
            if observed != expected:
                raise AssertionError("rank-two pullback normalization failed")
            normalization_checks += 1

        for first, second, third in itertools.combinations(SMALL_VECTORS, 3):
            required = (
                first,
                second,
                third,
                vector_add(first, second),
                vector_add(first, third),
                vector_add(second, third),
            )
            if any(
                scalar_label(vector, hidden_scalar, order) == 0
                for vector in required
            ):
                continue

            point_first, point_second, point_third = (
                points[scalar_label(vector, hidden_scalar, order)]
                for vector in (first, second, third)
            )
            if point_first is None or point_second is None or point_third is None:
                raise AssertionError("retained vector produced the identity")
            if len({point_first[0], point_second[0], point_third[0]}) < 3:
                continue
            if 0 in (rank_two(first), rank_two(second), rank_two(third)):
                continue

            determinant = coordinate_determinant(
                point_first, point_second, point_third, field_prime
            )
            factor = determinant_factor(
                rank_two, first, second, third, field_prime
            )
            if determinant != factor:
                raise AssertionError("rank-two three-point determinant failed")
            determinant_checks += 1

        first = (1, 0)
        second = (0, 1)
        third = (-1, -1)
        point_first, point_second, point_third = (
            points[scalar_label(vector, hidden_scalar, order)]
            for vector in (first, second, third)
        )
        if point_first is None or point_second is None or point_third is None:
            raise AssertionError("zero-sum triple had an identity point")
        if coordinate_determinant(
            point_first, point_second, point_third, field_prime
        ) != 0:
            raise AssertionError("zero-sum point triple was not collinear")
        if rank_two(vector_sum(first, second, third)) != 0:
            raise AssertionError("zero-sum net factor did not vanish")
        zero_sum_collinearity_checks += 1

        high_triples = (
            ((order + 1, 0), (0, order + 1), (1, 1)),
            ((2 * order + 1, 0), (0, order + 2), (1, -1)),
            ((order + 2, 1), (1, order + 2), (2, 1)),
        )
        for first, second, third in high_triples:
            required = (
                first,
                second,
                third,
                vector_add(first, second),
                vector_add(first, third),
                vector_add(second, third),
            )
            if any(
                scalar_label(vector, hidden_scalar, order) == 0
                for vector in required
            ):
                continue
            point_first, point_second, point_third = (
                points[scalar_label(vector, hidden_scalar, order)]
                for vector in (first, second, third)
            )
            if point_first is None or point_second is None or point_third is None:
                continue
            if len({point_first[0], point_second[0], point_third[0]}) < 3:
                continue
            if 0 in (rank_two(first), rank_two(second), rank_two(third)):
                continue
            determinant = coordinate_determinant(
                point_first, point_second, point_third, field_prime
            )
            factor = determinant_factor(
                rank_two, first, second, third, field_prime
            )
            if determinant != factor:
                raise AssertionError("high-index rank-two determinant failed")
            high_index_checks += 1

    character_results: list[dict[str, object]] = []
    for first, second, third in FIXED_CHARACTER_TRIPLES:
        matches = 0
        mismatches = 0
        zeros_or_exceptions = 0
        for hidden_scalar in range(1, order):
            scalar_values = [
                scalar_label(vector, hidden_scalar, order)
                for vector in (first, second, third)
            ]
            if 0 in scalar_values:
                zeros_or_exceptions += 1
                continue
            point_first, point_second, point_third = (
                points[value] for value in scalar_values
            )
            if point_first is None or point_second is None or point_third is None:
                zeros_or_exceptions += 1
                continue
            determinant = coordinate_determinant(
                point_first, point_second, point_third, field_prime
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
                "fixed rank-two determinant matched parity up to global sign"
            )
        character_results.append(
            {
                "vectors": (first, second, third),
                "matches": matches,
                "mismatches": mismatches,
                "zeros_or_exceptions": zeros_or_exceptions,
                "not_parity_up_to_global_sign": True,
            }
        )

    return {
        "field_prime": field_prime,
        "order": order,
        "generator": generator,
        "normalization_checks": normalization_checks,
        "three_point_determinant_checks": determinant_checks,
        "zero_sum_collinearity_checks": zero_sum_collinearity_checks,
        "high_index_determinant_checks": high_index_checks,
        "fixed_character_results": character_results,
        "all_rank_two_determinants_factor": True,
        "all_fixed_characters_reject_parity": True,
    }


def secp256k1_certificate() -> dict[str, object]:
    n = SECP_N
    return {
        "n": n,
        "bit_length": n.bit_length(),
        "identity_is_index_symbolic": True,
        "valid_for_public_n_dependent_vectors": True,
        "three_point_determinant_factor": (
            "-W(u+v+w)W(u-v)W(u-w)W(v-w)"
            "/(W(u)^3W(v)^3W(w)^3)"
        ),
        "zero_sum_specialization": "u+v+w=0 implies determinant=0",
        "does_smallest_rank_two_minor_select_oriented_sqrt": False,
        "selected_successor": "FROBENIUS-STICKELBERGER-DETERMINANT-050",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("rank_two_net_multi_cell_results.json"),
    )
    args = parser.parse_args()

    cases = [run_case(*case) for case in FROZEN_CASES]
    payload = {
        "package": "RANK-TWO-NET-MULTI-CELL-049",
        "cases": cases,
        "aggregate": {
            "cases": len(cases),
            "total_normalization_checks": sum(
                case["normalization_checks"] for case in cases
            ),
            "total_three_point_determinant_checks": sum(
                case["three_point_determinant_checks"] for case in cases
            ),
            "total_zero_sum_collinearity_checks": sum(
                case["zero_sum_collinearity_checks"] for case in cases
            ),
            "total_high_index_determinant_checks": sum(
                case["high_index_determinant_checks"] for case in cases
            ),
            "total_fixed_character_candidates": sum(
                len(case["fixed_character_results"]) for case in cases
            ),
            "all_rank_two_determinants_factor": all(
                case["all_rank_two_determinants_factor"] for case in cases
            ),
            "all_fixed_characters_reject_parity": all(
                case["all_fixed_characters_reject_parity"] for case in cases
            ),
        },
        "secp256k1": secp256k1_certificate(),
        "decision": (
            "The smallest genuinely rank-two three-point coordinate determinant "
            "is the pullback of Omega_(1,1,1) and factors exactly into a "
            "multiplicative rank-two net ratio. Public high-index vectors do not "
            "avoid the symbolic collapse. This determinant therefore does not "
            "construct the generator-oriented Kummer square root Y_G."
        ),
        "claim_boundary": [
            "The displayed determinant factorization is exact on the nondegenerate chart.",
            "The zero-sum specialization is the usual collinearity relation.",
            "The package closes this three-point determinant/pullback grammar, not arbitrary rank-two net polynomials.",
            "Fixed toy character mismatch is not promoted to a secp256k1 character-sum theorem.",
            "No parity oracle, absolute EDS-residue oracle, or ECDLP improvement is obtained.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["aggregate"], indent=2))
    print(json.dumps(payload["secp256k1"], indent=2))


if __name__ == "__main__":
    main()
