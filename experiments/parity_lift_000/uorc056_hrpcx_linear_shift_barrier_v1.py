#!/usr/bin/env python3
"""Exact replay for the UORC-056 H-RPCX linear-shift barrier.

For odd n, the cyclic parity word a_j = (-1)^j defines a circulant
convolution operator P.  In the group algebra,

    (1 + z) * (1 - z + ... + z^(n-1)) = 1 + z^n = 2

modulo z^n - 1.  Therefore P has explicit inverse (I + S)/2 over every
field of characteristic different from two.  Its n cyclic shifts are
linearly independent.

This script checks the identity and full rank on the frozen UORC-056 toy
orders and on additional synthetic odd orders.  The general result is the
symbolic identity above; finite replay is only a deterministic guardrail.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable


PROFILE_ID = "UORC-056-HRPCX-LINEAR-SHIFT-BARRIER-V1"


@dataclass(frozen=True)
class Instance:
    name: str
    n: int
    modulus: int


FROZEN = (
    Instance("toy-p43-n31", 31, 43),
    Instance("toy-p67-n79", 79, 67),
    Instance("toy-p79-n67", 67, 79),
    Instance("toy-p127-n127", 127, 127),
    Instance("toy-p163-n139", 139, 163),
)

SYNTHETIC = tuple(
    Instance(f"synthetic-n{n}", n, 1_000_003)
    for n in (1, 3, 5, 7, 9, 15, 21, 33, 65)
)


def mod_inv(value: int, modulus: int) -> int:
    return pow(value % modulus, -1, modulus)


def identity_matrix(n: int) -> list[list[int]]:
    return [[1 if row == col else 0 for col in range(n)] for row in range(n)]


def shift_matrix(n: int) -> list[list[int]]:
    """Return S with S e_j = e_(j+1 mod n)."""
    matrix = [[0 for _ in range(n)] for _ in range(n)]
    for col in range(n):
        matrix[(col + 1) % n][col] = 1
    return matrix


def parity_circulant(n: int, modulus: int) -> list[list[int]]:
    coefficients = [1 if index % 2 == 0 else modulus - 1 for index in range(n)]
    return [
        [coefficients[(row - col) % n] for col in range(n)]
        for row in range(n)
    ]


def explicit_inverse(n: int, modulus: int) -> list[list[int]]:
    inv_two = mod_inv(2, modulus)
    shift = shift_matrix(n)
    return [
        [inv_two * ((1 if row == col else 0) + shift[row][col]) % modulus
         for col in range(n)]
        for row in range(n)
    ]


def matrix_product(left: list[list[int]], right: list[list[int]], modulus: int) -> list[list[int]]:
    n = len(left)
    out = [[0 for _ in range(n)] for _ in range(n)]
    for row in range(n):
        for pivot in range(n):
            coefficient = left[row][pivot]
            if coefficient == 0:
                continue
            right_row = right[pivot]
            out_row = out[row]
            for col in range(n):
                out_row[col] = (out_row[col] + coefficient * right_row[col]) % modulus
    return out


def matrix_rank(matrix: list[list[int]], modulus: int) -> int:
    work = [row[:] for row in matrix]
    row_count = len(work)
    col_count = len(work[0]) if work else 0
    pivot_row = 0
    for col in range(col_count):
        pivot = next((row for row in range(pivot_row, row_count) if work[row][col] % modulus), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = mod_inv(work[pivot_row][col], modulus)
        work[pivot_row] = [(entry * scale) % modulus for entry in work[pivot_row]]
        for row in range(row_count):
            if row == pivot_row:
                continue
            factor = work[row][col] % modulus
            if factor:
                work[row] = [
                    (work[row][index] - factor * work[pivot_row][index]) % modulus
                    for index in range(col_count)
                ]
        pivot_row += 1
        if pivot_row == row_count:
            break
    return pivot_row


def cyclic_convolution(left: list[int], right: list[int], modulus: int) -> list[int]:
    n = len(left)
    out = [0] * n
    for i, left_value in enumerate(left):
        for j, right_value in enumerate(right):
            out[(i + j) % n] = (out[(i + j) % n] + left_value * right_value) % modulus
    return out


def check_instance(instance: Instance) -> dict[str, object]:
    n = instance.n
    modulus = instance.modulus
    if n % 2 != 1:
        raise ValueError(f"order must be odd: {instance}")
    if modulus == 2:
        raise ValueError("characteristic two is excluded")

    parity = [1 if index % 2 == 0 else modulus - 1 for index in range(n)]
    inverse_kernel = [0] * n
    inverse_kernel[0] = mod_inv(2, modulus)
    inverse_kernel[1 % n] = (inverse_kernel[1 % n] + mod_inv(2, modulus)) % modulus
    expected_identity = [1] + [0] * (n - 1)

    convolution = cyclic_convolution(inverse_kernel, parity, modulus)
    if convolution != expected_identity:
        raise AssertionError((instance, "group-algebra inverse failed", convolution))

    circulant = parity_circulant(n, modulus)
    inverse = explicit_inverse(n, modulus)
    identity = identity_matrix(n)
    if matrix_product(inverse, circulant, modulus) != identity:
        raise AssertionError((instance, "left inverse failed"))
    if matrix_product(circulant, inverse, modulus) != identity:
        raise AssertionError((instance, "right inverse failed"))

    rank = matrix_rank(circulant, modulus)
    if rank != n:
        raise AssertionError((instance, "rank defect", rank, n))

    return {
        **asdict(instance),
        "rank": rank,
        "expected_rank": n,
        "explicit_inverse_verified": True,
        "cyclic_linear_complexity": n,
    }


def run(instances: Iterable[Instance]) -> dict[str, object]:
    checks = [check_instance(instance) for instance in instances]
    return {
        "profile_id": PROFILE_ID,
        "theorem": {
            "hypotheses": [
                "n is odd",
                "the coefficient field has 2 != 0",
                "the feature space is linear and stable under cyclic translation",
                "exact parity belongs to the feature space",
            ],
            "identity": "(1+z)(1-z+...+z^(n-1)) = 2 mod (z^n-1)",
            "explicit_inverse": "(1+z)/2",
            "conclusion": "dimension is at least n",
        },
        "checks": checks,
        "aggregate": {
            "instances": len(checks),
            "largest_order": max(check["n"] for check in checks),
            "rank_defects": sum(check["rank"] != check["expected_rank"] for check in checks),
            "inverse_failures": sum(not check["explicit_inverse_verified"] for check in checks),
        },
        "decision": {
            "polylog_dim_translation_stable_linear_module_contains_parity": False,
            "linear_recurrence_width_polylog_generates_exact_cyclic_parity": False,
            "minimum_linear_dimension": "n",
            "general_hrpcx_refuted": False,
            "nonlinear_state_update_open": True,
            "nonlinear_readout_open": True,
            "high_degree_low_circuit_open": True,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    result = run((*FROZEN, *SYNTHETIC))
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
