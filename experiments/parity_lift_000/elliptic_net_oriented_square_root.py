#!/usr/bin/env python3
"""Exact replay for ELLIPTIC-NET-ORIENTED-SQUARE-ROOT-047.

Package 046 identified canonical scalar parity with a generator-oriented square
root Y_G modulo the subgroup Kummer kernel polynomial.  This package tests the
first additive elliptic-net escape: determinants and discrete Wronskians built
from a single elliptic-net recurrence cell.

Two exact collapses are checked:

1. Ward's rank-one EDS recurrence rewrites every adjacent high-index
   determinant as W(m+r)W(m-r), a multiplicative section.
2. The first normalized rank-two determinant

       W(0,2)W(2,1) - W(2,0)W(1,2)

   equals W(2,2)W(1,-1), and on y^2=x^3+7 equals

       2 y(P+Q) (x(Q)-x(P)).

Thus one-cell additive cancellation does not construct the oriented Kummer
square root.  It collapses back to the multiplicative/public net algebra already
audited in earlier packages.

Only frozen toy subgroups are used.  No external point, key, wallet, or
production-sized discrete-log target is accepted.
"""
from __future__ import annotations

import argparse
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


def ward_cell(
    psi, field_prime: int, middle_index: int, shift_index: int
) -> tuple[int, int]:
    left = psi(middle_index + shift_index) * psi(
        middle_index - shift_index
    ) % field_prime
    right = (
        psi(middle_index + 1)
        * psi(middle_index - 1)
        * pow(psi(shift_index), 2, field_prime)
        - psi(shift_index + 1)
        * psi(shift_index - 1)
        * pow(psi(middle_index), 2, field_prime)
    ) % field_prime
    return left, right


def run_case(
    field_prime: int, order: int, generator: tuple[int, int]
) -> dict[str, object]:
    points = orbit(generator, order, field_prime)
    base = points[1]
    if base is None:
        raise AssertionError("generator was the identity")
    x_base, y_base = base
    psi = division_polynomial_evaluator(base, field_prime)

    # Exhaustive bounded Ward cells.  The index range is independent of hidden
    # data and includes negative m-r through the evaluator's exact sign law.
    ward_limit = min(order - 1, 32)
    ward_checks = 0
    for middle_index in range(1, ward_limit + 1):
        for shift_index in range(1, ward_limit + 1):
            left, right = ward_cell(
                psi, field_prime, middle_index, shift_index
            )
            if left != right:
                raise AssertionError("Ward determinant cell did not factor")
            ward_checks += 1

    # Public near-period and beyond-period indices verify that the same collapse
    # survives n-dependent high indices rather than only small fixed indices.
    near_period_middle = (
        order - 3,
        order - 2,
        order - 1,
        order + 1,
        order + 2,
        2 * order - 1,
    )
    near_period_shift = (1, 2, 3, 5, 7)
    near_period_checks = 0
    for middle_index in near_period_middle:
        for shift_index in near_period_shift:
            left, right = ward_cell(
                psi, field_prime, middle_index, shift_index
            )
            if left != right:
                raise AssertionError("near-period Ward cell did not factor")
            near_period_checks += 1

    determinant_checks = 0
    determinant_character_matches = 0
    determinant_character_mismatches = 0

    # Exclude Q=G and Q=-G, exactly the points where the displayed normalized
    # rank-two coordinate chart is degenerate.
    for scalar in range(2, order - 1):
        query = points[scalar]
        if query is None:
            raise AssertionError("nonzero scalar produced the identity")
        x_query, y_query = query
        if x_query == x_base:
            raise AssertionError("unexpected Kummer collision in retained chart")

        point_sum = ec_add(base, query, field_prime)
        if point_sum is None:
            raise AssertionError("retained point sum was the identity")
        x_sum, y_sum = point_sum

        # Explicit normalized rank-two net polynomials on a short Weierstrass
        # model.  Stange's formulas give W(2,1)=x(P)-x(P+Q) and
        # W(1,2)=x(Q)-x(P+Q).
        w20 = 2 * y_base % field_prime
        w02 = 2 * y_query % field_prime
        w1m1 = (x_query - x_base) % field_prime
        w21 = (x_base - x_sum) % field_prime
        w12 = (x_query - x_sum) % field_prime
        w22 = 2 * y_sum % field_prime

        determinant = (w02 * w21 - w20 * w12) % field_prime
        recurrence_product = w22 * w1m1 % field_prime
        coordinate_product = (
            2 * y_sum * (x_query - x_base)
        ) % field_prime

        if determinant != recurrence_product:
            raise AssertionError("rank-two determinant did not collapse")
        if determinant != coordinate_product:
            raise AssertionError("coordinate form of determinant failed")
        if (w12 - w21) % field_prime != w1m1:
            raise AssertionError("rank-two additive difference failed")
        if determinant == 0:
            raise AssertionError("retained determinant unexpectedly vanished")

        determinant_character = quadratic_character(determinant, field_prime)
        parity = 1 if scalar % 2 == 0 else -1
        if determinant_character == parity:
            determinant_character_matches += 1
        else:
            determinant_character_mismatches += 1
        determinant_checks += 1

    if determinant_character_matches in (0, determinant_checks):
        raise AssertionError("determinant accidentally matched parity up to sign")

    return {
        "field_prime": field_prime,
        "order": order,
        "generator": generator,
        "ward_limit": ward_limit,
        "ward_cell_checks": ward_checks,
        "near_period_ward_checks": near_period_checks,
        "rank_two_determinant_checks": determinant_checks,
        "determinant_character_matches_parity": determinant_character_matches,
        "determinant_character_mismatches_parity": determinant_character_mismatches,
        "determinant_exactly_factors": True,
        "coordinate_formula_exact": True,
        "determinant_is_not_parity_up_to_global_sign": True,
    }


def secp256k1_certificate() -> dict[str, object]:
    n = SECP_N
    return {
        "n": n,
        "bit_length": n.bit_length(),
        "ward_cell_identity_valid_for_public_high_indices": True,
        "single_recurrence_cell_output": "multiplicative net monomial",
        "minimal_rank_two_determinant_output": "W(2,2)*W(1,-1)",
        "minimal_coordinate_output": "2*y(P+Q)*(x(Q)-x(P))",
        "does_single_cell_select_oriented_sqrt": False,
        "selected_successor": "MULTI-CELL-NET-CANCELLATION-048",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "elliptic_net_oriented_square_root_results.json"
        ),
    )
    args = parser.parse_args()

    cases = [run_case(*case) for case in FROZEN_CASES]
    payload = {
        "package": "ELLIPTIC-NET-ORIENTED-SQUARE-ROOT-047",
        "cases": cases,
        "aggregate": {
            "cases": len(cases),
            "total_ward_cell_checks": sum(
                case["ward_cell_checks"] for case in cases
            ),
            "total_near_period_ward_checks": sum(
                case["near_period_ward_checks"] for case in cases
            ),
            "total_rank_two_determinant_checks": sum(
                case["rank_two_determinant_checks"] for case in cases
            ),
            "total_determinant_character_matches": sum(
                case["determinant_character_matches_parity"] for case in cases
            ),
            "total_determinant_character_mismatches": sum(
                case["determinant_character_mismatches_parity"] for case in cases
            ),
            "all_ward_cells_factor": all(
                case["determinant_exactly_factors"] for case in cases
            ),
            "all_coordinate_formulas_exact": all(
                case["coordinate_formula_exact"] for case in cases
            ),
            "all_minimal_determinants_reject_parity": all(
                case["determinant_is_not_parity_up_to_global_sign"]
                for case in cases
            ),
        },
        "secp256k1": secp256k1_certificate(),
        "decision": (
            "Every determinant that is exactly one Ward or elliptic-net "
            "recurrence cell factors into a multiplicative net monomial. The "
            "minimal normalized rank-two determinant is W(2,2)W(1,-1), or "
            "2*y(P+Q)*(x(Q)-x(P)) in coordinates. It therefore does not "
            "construct the generator-oriented Kummer square root Y_G. The "
            "remaining additive route must combine multiple recurrence cells "
            "in a way that does not reduce to a single Plucker/Ward factor."
        ),
        "claim_boundary": [
            "The Ward and minimal rank-two determinant identities are exact.",
            "The package closes one-recurrence-cell determinants at arbitrary public indices.",
            "It does not close sums of several recurrence cells or arbitrary determinants.",
            "Toy character mismatch is not promoted to a secp256k1 character-sum theorem.",
            "No oriented square-root evaluator, parity oracle, or ECDLP improvement is obtained.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["aggregate"], indent=2))
    print(json.dumps(payload["secp256k1"], indent=2))


if __name__ == "__main__":
    main()
