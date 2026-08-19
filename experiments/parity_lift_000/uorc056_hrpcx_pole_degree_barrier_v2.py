#!/usr/bin/env python3
"""Exact toy replay for the H-RPCX pole-degree barrier.

For each frozen toy curve y^2=x^3+7, this script computes the smallest
Riemann-Roch pole budget D for which canonical parity on the nonzero subgroup
lies in the evaluation span of L(D*O).

The general lower bound is theorem-level and does not depend on the replay:
if a nonconstant rational function takes only +/-1 on N regular points, then
its pole divisor has degree at least N/2, because f^2-1 has N zeros and at
most twice the pole degree of f.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional


PROFILE_ID = "UORC-056-HRPCX-POLE-DEGREE-BARRIER-V2"
Point = Optional[tuple[int, int]]


@dataclass(frozen=True)
class CurveInstance:
    name: str
    p: int
    n: int
    gx: int
    gy: int


FROZEN = (
    CurveInstance("toy-p43-n31", 43, 31, 2, 12),
    CurveInstance("toy-p67-n79", 67, 79, 2, 22),
    CurveInstance("toy-p79-n67", 79, 67, 1, 18),
    CurveInstance("toy-p127-n127", 127, 127, 1, 32),
    CurveInstance("toy-p163-n139", 163, 139, 2, 34),
)


def inv(value: int, p: int) -> int:
    return pow(value % p, -1, p)


def point_add(left: Point, right: Point, p: int) -> Point:
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if left == right:
        if y1 % p == 0:
            return None
        slope = (3 * x1 * x1) * inv(2 * y1, p) % p
    else:
        slope = (y2 - y1) * inv(x2 - x1, p) % p
    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    return x3, y3


def scalar_mul(k: int, point: Point, p: int) -> Point:
    out: Point = None
    addend = point
    while k:
        if k & 1:
            out = point_add(out, addend, p)
        addend = point_add(addend, addend, p)
        k >>= 1
    return out


def matrix_rank(matrix: list[list[int]], p: int) -> int:
    if not matrix:
        return 0
    work = [row[:] for row in matrix]
    rows = len(work)
    cols = len(work[0])
    pivot_row = 0
    for col in range(cols):
        pivot = next((row for row in range(pivot_row, rows) if work[row][col] % p), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = inv(work[pivot_row][col], p)
        work[pivot_row] = [(entry * scale) % p for entry in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row:
                continue
            factor = work[row][col] % p
            if factor:
                work[row] = [
                    (work[row][index] - factor * work[pivot_row][index]) % p
                    for index in range(cols)
                ]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def basis_descriptors(pole_budget: int) -> list[tuple[str, int]]:
    """Basis of L(D*O) for y^2=x^3+7.

    x has pole order 2 at O and y has pole order 3.  The function-field
    relation reduces every element to A(x)+y*B(x).
    """
    basis: list[tuple[str, int]] = []
    for exponent in range(pole_budget // 2 + 1):
        if 2 * exponent <= pole_budget:
            basis.append(("x", exponent))
    exponent = 0
    while 3 + 2 * exponent <= pole_budget:
        basis.append(("yx", exponent))
        exponent += 1
    return basis


def evaluate_basis(point: tuple[int, int], descriptor: tuple[str, int], p: int) -> int:
    x, y = point
    kind, exponent = descriptor
    value = pow(x, exponent, p)
    return value if kind == "x" else y * value % p


def parity_in_span(points: list[tuple[int, int]], target: list[int], pole_budget: int, p: int) -> tuple[bool, int]:
    basis = basis_descriptors(pole_budget)
    rows = [
        [evaluate_basis(point, descriptor, p) for descriptor in basis]
        for point in points
    ]
    rank = matrix_rank(rows, p)
    augmented = [row + [target[index]] for index, row in enumerate(rows)]
    augmented_rank = matrix_rank(augmented, p)
    return rank == augmented_rank, rank


def minimal_pole_budget(points: list[tuple[int, int]], target: list[int], p: int, upper: int) -> tuple[int, int]:
    possible, _ = parity_in_span(points, target, upper, p)
    if not possible:
        raise AssertionError(f"parity not in L({upper}O) evaluation span")
    low = 0
    high = upper
    while low < high:
        middle = (low + high) // 2
        possible, _ = parity_in_span(points, target, middle, p)
        if possible:
            high = middle
        else:
            low = middle + 1
    possible, rank = parity_in_span(points, target, low, p)
    if not possible:
        raise AssertionError("binary search inconsistency")
    if low > 0:
        previous, _ = parity_in_span(points, target, low - 1, p)
        if previous:
            raise AssertionError("minimality check failed")
    return low, rank


def check_curve(curve: CurveInstance) -> dict[str, object]:
    p, n = curve.p, curve.n
    generator = (curve.gx, curve.gy)
    if (curve.gy * curve.gy - curve.gx**3 - 7) % p:
        raise AssertionError((curve.name, "generator is not on curve"))
    if scalar_mul(n, generator, p) is not None:
        raise AssertionError((curve.name, "declared order failed"))

    points: list[tuple[int, int]] = []
    target: list[int] = []
    current: Point = None
    for k in range(1, n):
        current = point_add(current, generator, p)
        if current is None:
            raise AssertionError((curve.name, "early orbit closure", k))
        points.append(current)
        target.append(1 if k % 2 == 0 else p - 1)
    if point_add(current, generator, p) is not None:
        raise AssertionError((curve.name, "orbit did not close"))

    lower_bound = (len(points) + 1) // 2
    minimum, rank = minimal_pole_budget(points, target, p, upper=2 * n)
    if minimum < lower_bound:
        raise AssertionError((curve.name, "divisor lower bound violated", minimum, lower_bound))

    return {
        **asdict(curve),
        "nonzero_points": len(points),
        "theorem_lower_bound": lower_bound,
        "exact_minimum_pole_budget_in_L_D_O": minimum,
        "rank_at_minimum": rank,
        "minimum_is_exponential_in_bitlength_on_family": True,
    }


def run() -> dict[str, object]:
    checks = [check_curve(curve) for curve in FROZEN]
    return {
        "profile_id": PROFILE_ID,
        "theorem": {
            "statement": "a nonconstant +/-1 rational decoder regular on N points has pole degree at least N/2",
            "proof_object": "f^2-1 has N zeros and pole degree at most twice that of f",
            "subgroup_specialization": "N=n-1",
        },
        "checks": checks,
        "aggregate": {
            "curves": len(checks),
            "points": sum(check["nonzero_points"] for check in checks),
            "lower_bound_violations": sum(
                check["exact_minimum_pole_budget_in_L_D_O"] < check["theorem_lower_bound"]
                for check in checks
            ),
        },
        "decision": {
            "low_pole_state_low_degree_decoder_can_realize_exact_parity": False,
            "required_composite_pole_budget": "at least (n-1)/2",
            "general_arithmetic_circuit_lower_bound_proved": False,
            "high_degree_low_size_circuit_open": True,
            "nonrational_branch_transport_open": True,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = run()
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
