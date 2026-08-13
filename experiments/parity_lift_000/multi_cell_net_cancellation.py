#!/usr/bin/env python3
"""Exact replay for MULTI-CELL-NET-CANCELLATION-048.

Package 047 closed determinants consisting of one Ward/elliptic-net recurrence
cell.  The first genuinely multi-cell family is obtained by taking two Ward
cells with the same middle index m and different shifts r,s, then eliminating
the common coefficient W(m+1)W(m-1).

For an elliptic divisibility sequence W, Ward's recurrence is

    W(m+t)W(m-t)
      = W(m+1)W(m-1)W(t)^2
        - W(t+1)W(t-1)W(m)^2.

Eliminating the common first coefficient from the t=r and t=s cells gives the
exact 2x2 determinant identity

    W(m+r)W(m-r)W(s)^2 - W(m+s)W(m-s)W(r)^2
      = W(m)^2 W(r+s)W(s-r).

The right side is again one multiplicative EDS monomial.  Thus this entire
natural two-cell Pluecker/Wronskian family does not create a new additive
absolute-orientation equation.

Only frozen toy subgroups are used.  No external point, key, wallet, or
production-sized discrete-log target is accepted.
"""
from __future__ import annotations

import argparse
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


def two_cell_identity(psi, field_prime: int, m: int, r: int, s: int) -> tuple[int, int]:
    left = (
        psi(m + r) * psi(m - r) * pow(psi(s), 2, field_prime)
        - psi(m + s) * psi(m - s) * pow(psi(r), 2, field_prime)
    ) % field_prime
    right = (
        pow(psi(m), 2, field_prime)
        * psi(r + s)
        * psi(s - r)
    ) % field_prime
    return left, right


def run_case(field_prime: int, order: int, generator: tuple[int, int]) -> dict[str, object]:
    points = orbit(generator, order, field_prime)
    base = points[1]
    if base is None:
        raise AssertionError("generator was the identity")
    psi = division_polynomial_evaluator(base, field_prime)

    # Exhaustive bounded three-index screen.  This is exact finite-field
    # arithmetic, not numerical fitting.
    limit = min(order - 1, 18)
    bounded_checks = 0
    adjacent_checks = 0
    for m in range(1, limit + 1):
        for r in range(1, limit + 1):
            for s in range(1, limit + 1):
                left, right = two_cell_identity(psi, field_prime, m, r, s)
                if left != right:
                    raise AssertionError("two-cell Ward determinant did not collapse")
                bounded_checks += 1
                if s == r + 1:
                    adjacent_checks += 1

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

    # Special adjacent identity: the determinant becomes W(m)^2 W(2r+1)
    # because W(1)=1.
    adjacent_special_checks = 0
    for m in range(1, limit + 1):
        for r in range(1, limit):
            s = r + 1
            left, _ = two_cell_identity(psi, field_prime, m, r, s)
            expected = pow(psi(m), 2, field_prime) * psi(2 * r + 1) % field_prime
            if left != expected:
                raise AssertionError("adjacent two-cell collapse failed")
            adjacent_special_checks += 1

    return {
        "field_prime": field_prime,
        "order": order,
        "generator": generator,
        "bounded_limit": limit,
        "bounded_two_cell_checks": bounded_checks,
        "adjacent_triplets_inside_bounded_screen": adjacent_checks,
        "high_index_two_cell_checks": high_index_checks,
        "adjacent_special_checks": adjacent_special_checks,
        "all_two_cell_determinants_factor": True,
        "factor_form": "W(m)^2*W(r+s)*W(s-r)",
    }


def secp256k1_certificate() -> dict[str, object]:
    n = SECP_N
    return {
        "n": n,
        "bit_length": n.bit_length(),
        "identity_is_index_symbolic": True,
        "valid_for_public_n_dependent_indices": True,
        "two_cell_determinant_output": "W(m)^2*W(r+s)*W(s-r)",
        "does_two_cell_ward_family_select_oriented_sqrt": False,
        "remaining_live_class": "three-or-more independent cells / non-Ward minors / theta-sigma or p-adic branch selection",
        "selected_successor": "MULTI-CELL-NET-CANCELLATION-048B",
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
            "total_bounded_two_cell_checks": sum(case["bounded_two_cell_checks"] for case in cases),
            "total_high_index_two_cell_checks": sum(case["high_index_two_cell_checks"] for case in cases),
            "total_adjacent_special_checks": sum(case["adjacent_special_checks"] for case in cases),
            "all_two_cell_determinants_factor": all(case["all_two_cell_determinants_factor"] for case in cases),
        },
        "secp256k1": secp256k1_certificate(),
        "decision": (
            "The natural two-cell Ward determinant obtained by eliminating the common "
            "W(m+1)W(m-1) coefficient collapses exactly to the multiplicative monomial "
            "W(m)^2 W(r+s) W(s-r), for arbitrary indices.  Therefore moving from one "
            "recurrence cell to this full two-cell Pluecker family does not yet create "
            "an independent generator-oriented square-root equation."
        ),
        "claim_boundary": [
            "The displayed two-cell determinant identity is exact for every EDS where Ward recurrence holds.",
            "The finite replay checks frozen toy subgroups and public high-index patterns only.",
            "The result closes this elimination/determinant grammar, not arbitrary sums of two unrelated net cells.",
            "It does not close three-or-more-cell syzygies, non-Ward minors, theta/sigma determinants, or p-adic branch selection.",
            "No parity oracle, absolute EDS-residue oracle, or ECDLP improvement is obtained.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["aggregate"], indent=2))
    print(json.dumps(payload["secp256k1"], indent=2))


if __name__ == "__main__":
    main()
