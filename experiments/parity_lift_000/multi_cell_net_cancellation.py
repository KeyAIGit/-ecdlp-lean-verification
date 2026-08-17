#!/usr/bin/env python3
"""Exact replay for MULTI-CELL-NET-CANCELLATION-048.

Package 047 closed determinants consisting of one Ward/elliptic-net recurrence
cell.  This package moves to genuinely multi-cell rank-one EDS constructions.

Write

    R(j) = W(j)^2,
    V(j) = W(j+1)W(j-1),
    A(a,b) = W(a+b)W(a-b).

Ward's recurrence is exactly

    A(a,b) = V(a)R(b) - V(b)R(a).

Thus every Ward product A(a,b) is a 2x2 minor of the two-row array whose j-th
column is (V(j), R(j)).  Consequences checked here include:

1. the shared-middle two-cell determinant

   A(m,r)R(s) - A(m,s)R(r) = R(m)A(s,r);

2. every natural 3x3 determinant with columns (A(m,t), R(t), V(t)) vanishes;

3. all four-index Ward products satisfy the Grassmann-Pluecker relation

   A(a,b)A(c,d) - A(a,c)A(b,d) + A(a,d)A(b,c) = 0.

So the first multi-cell Ward grammar has rank-two determinantal structure rather
than a new independent absolute-orientation equation.

Only frozen toy subgroups are used.  No external point, key, wallet, or
production-sized discrete-log target is accepted.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

from nonlocal_odd_anchor_screen import division_polynomial_evaluator, orbit

SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

FROZEN_CASES = (
    (151, 19, (70, 122)),
    (43, 31, (2, 12)),
    (79, 67, (1, 18)),
    (1087, 271, (1017, 688)),
    (2851, 397, (2276, 1015)),
    (1663, 433, (126, 1375)),
)


def r_value(psi, p: int, index: int) -> int:
    return pow(psi(index), 2, p)


def v_value(psi, p: int, index: int) -> int:
    return psi(index + 1) * psi(index - 1) % p


def a_value(psi, p: int, left: int, right: int) -> int:
    return psi(left + right) * psi(left - right) % p


def ward_minor(psi, p: int, left: int, right: int) -> int:
    return (
        v_value(psi, p, left) * r_value(psi, p, right)
        - v_value(psi, p, right) * r_value(psi, p, left)
    ) % p


def two_cell_identity(psi, field_prime: int, m: int, r: int, s: int) -> tuple[int, int]:
    left = (
        a_value(psi, field_prime, m, r) * r_value(psi, field_prime, s)
        - a_value(psi, field_prime, m, s) * r_value(psi, field_prime, r)
    ) % field_prime
    right = r_value(psi, field_prime, m) * a_value(psi, field_prime, s, r) % field_prime
    return left, right


def three_by_three_det(psi, p: int, m: int, r: int, s: int, t: int) -> int:
    # Rows are indexed by r,s,t and columns are A(m,u), R(u), V(u).
    ar, ass, at = (a_value(psi, p, m, u) for u in (r, s, t))
    rr, rs, rt = (r_value(psi, p, u) for u in (r, s, t))
    vr, vs, vt = (v_value(psi, p, u) for u in (r, s, t))
    return (
        ar * (rs * vt - rt * vs)
        - rr * (ass * vt - at * vs)
        + vr * (ass * rt - at * rs)
    ) % p


def run_case(field_prime: int, order: int, generator: tuple[int, int]) -> dict[str, object]:
    points = orbit(generator, order, field_prime)
    base = points[1]
    if base is None:
        raise AssertionError("generator was the identity")
    psi = division_polynomial_evaluator(base, field_prime)

    limit = min(order - 1, 18)

    # First verify the determinantal form of Ward recurrence itself.
    minor_checks = 0
    for a in range(1, limit + 1):
        for b in range(1, limit + 1):
            if a_value(psi, field_prime, a, b) != ward_minor(psi, field_prime, a, b):
                raise AssertionError("Ward product was not its rank-two minor")
            minor_checks += 1

    # Exhaustive bounded shared-middle two-cell screen.
    bounded_checks = 0
    for m in range(1, limit + 1):
        for r in range(1, limit + 1):
            for s in range(1, limit + 1):
                left, right = two_cell_identity(psi, field_prime, m, r, s)
                if left != right:
                    raise AssertionError("two-cell Ward determinant did not collapse")
                bounded_checks += 1

    # Stress public n-dependent indices around and beyond the subgroup period.
    high_m = (order - 2, order - 1, order + 1, order + 2, 2 * order - 1)
    high_rs = ((1, 2), (2, 3), (3, 5), (5, 8), (7, 11), (order - 2, order + 1))
    high_index_checks = 0
    for m in high_m:
        for r, s in high_rs:
            left, right = two_cell_identity(psi, field_prime, m, r, s)
            if left != right:
                raise AssertionError("high-index two-cell identity failed")
            high_index_checks += 1

    # Adjacent specialization A(m,r)R(r+1)-A(m,r+1)R(r)=R(m)W(2r+1).
    adjacent_special_checks = 0
    for m in range(1, limit + 1):
        for r in range(1, limit):
            s = r + 1
            left, _ = two_cell_identity(psi, field_prime, m, r, s)
            expected = r_value(psi, field_prime, m) * psi(2 * r + 1) % field_prime
            if left != expected:
                raise AssertionError("adjacent two-cell collapse failed")
            adjacent_special_checks += 1

    # Three rows live in a two-dimensional column span because
    # A(m,u)=V(m)R(u)-R(m)V(u). Hence the 3x3 determinant is zero.
    grammar_limit = min(limit, 12)
    three_cell_checks = 0
    for m in range(1, grammar_limit + 1):
        for r, s, t in itertools.combinations(range(1, grammar_limit + 1), 3):
            if three_by_three_det(psi, field_prime, m, r, s, t) != 0:
                raise AssertionError("three-cell rank-two determinant did not vanish")
            three_cell_checks += 1

    # Four-index Grassmann-Pluecker relation for 2x2 minors.
    pluecker_checks = 0
    for a, b, c, d in itertools.combinations(range(1, grammar_limit + 1), 4):
        pab = a_value(psi, field_prime, a, b)
        pac = a_value(psi, field_prime, a, c)
        pad = a_value(psi, field_prime, a, d)
        pbc = a_value(psi, field_prime, b, c)
        pbd = a_value(psi, field_prime, b, d)
        pcd = a_value(psi, field_prime, c, d)
        relation = (pab * pcd - pac * pbd + pad * pbc) % field_prime
        if relation != 0:
            raise AssertionError("Ward minors violated the Pluecker relation")
        pluecker_checks += 1

    return {
        "field_prime": field_prime,
        "order": order,
        "generator": generator,
        "bounded_limit": limit,
        "grammar_limit": grammar_limit,
        "ward_minor_checks": minor_checks,
        "bounded_two_cell_checks": bounded_checks,
        "high_index_two_cell_checks": high_index_checks,
        "adjacent_special_checks": adjacent_special_checks,
        "three_cell_rank_two_determinant_checks": three_cell_checks,
        "four_index_pluecker_checks": pluecker_checks,
        "all_ward_products_are_rank_two_minors": True,
        "all_two_cell_determinants_factor": True,
        "all_three_cell_determinants_vanish": True,
        "all_pluecker_relations_hold": True,
        "factor_form": "W(m)^2*W(r+s)*W(s-r)",
    }


def secp256k1_certificate() -> dict[str, object]:
    n = SECP_N
    return {
        "n": n,
        "bit_length": n.bit_length(),
        "identity_is_index_symbolic": True,
        "valid_for_public_n_dependent_indices": True,
        "ward_product_representation": "A(a,b)=det((V(a),R(a)),(V(b),R(b)))",
        "two_cell_determinant_output": "W(m)^2*W(r+s)*W(s-r)",
        "natural_three_cell_determinant": "identically zero",
        "four_index_syzygy": "Grassmann-Pluecker relation",
        "does_rank_one_ward_minor_grammar_select_oriented_sqrt": False,
        "remaining_live_class": "non-Ward rank-two-net minors / independently normalized theta-sigma determinants / p-adic branch selection / unrestricted short nonlinear circuit",
        "selected_successor": "RANK-TWO-NET-MULTI-CELL-049",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("multi_cell_net_cancellation_results.json"),
    )
    args = parser.parse_args()

    cases = [run_case(*case) for case in FROZEN_CASES]
    payload = {
        "package": "MULTI-CELL-NET-CANCELLATION-048",
        "cases": cases,
        "aggregate": {
            "cases": len(cases),
            "total_ward_minor_checks": sum(case["ward_minor_checks"] for case in cases),
            "total_bounded_two_cell_checks": sum(case["bounded_two_cell_checks"] for case in cases),
            "total_high_index_two_cell_checks": sum(case["high_index_two_cell_checks"] for case in cases),
            "total_adjacent_special_checks": sum(case["adjacent_special_checks"] for case in cases),
            "total_three_cell_rank_two_determinant_checks": sum(case["three_cell_rank_two_determinant_checks"] for case in cases),
            "total_four_index_pluecker_checks": sum(case["four_index_pluecker_checks"] for case in cases),
            "all_ward_products_are_rank_two_minors": all(case["all_ward_products_are_rank_two_minors"] for case in cases),
            "all_two_cell_determinants_factor": all(case["all_two_cell_determinants_factor"] for case in cases),
            "all_three_cell_determinants_vanish": all(case["all_three_cell_determinants_vanish"] for case in cases),
            "all_pluecker_relations_hold": all(case["all_pluecker_relations_hold"] for case in cases),
        },
        "secp256k1": secp256k1_certificate(),
        "decision": (
            "Rank-one Ward multi-cell products have an exact rank-two determinantal "
            "model: A(a,b)=V(a)R(b)-V(b)R(a). The natural shared-middle two-cell "
            "determinant factors to W(m)^2 W(r+s) W(s-r), every corresponding 3x3 "
            "determinant vanishes, and the four-index products obey the Pluecker "
            "syzygy. This closes the first rank-one Ward minor grammar as a source "
            "of an independent generator-oriented square-root equation."
        ),
        "claim_boundary": [
            "The displayed Ward-minor, two-cell, 3x3-rank, and Pluecker identities are exact consequences of Ward recurrence.",
            "The finite replay checks frozen toy subgroups and public high-index patterns only.",
            "The result closes the declared rank-one Ward minor grammar, not arbitrary polynomial functions of EDS terms.",
            "It does not close genuinely rank-two elliptic-net minors, independent theta/sigma normalizations, or p-adic branch selection.",
            "No parity oracle, absolute EDS-residue oracle, or ECDLP improvement is obtained.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["aggregate"], indent=2))
    print(json.dumps(payload["secp256k1"], indent=2))


if __name__ == "__main__":
    main()
