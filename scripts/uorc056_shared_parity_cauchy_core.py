#!/usr/bin/env python3
"""Exact Cauchy full-spark replays for UORC-056 V19."""
from __future__ import annotations

import itertools
import math
from collections.abc import Sequence
from typing import Any

from uorc056_shared_parity_fourier import find_root_field


def mod_determinant(matrix: Sequence[Sequence[int]], modulus: int) -> int:
    size = len(matrix)
    if any(len(row) != size for row in matrix):
        raise ValueError("square matrix required")
    work = [[entry % modulus for entry in row] for row in matrix]
    determinant = 1
    for column in range(size):
        pivot = next((r for r in range(column, size) if work[r][column]), None)
        if pivot is None:
            return 0
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            determinant = -determinant % modulus
        value = work[column][column]
        determinant = determinant * value % modulus
        inverse = pow(value, -1, modulus)
        for row in range(column + 1, size):
            factor = work[row][column] * inverse % modulus
            for inner in range(column, size):
                work[row][inner] = (
                    work[row][inner] - factor * work[column][inner]
                ) % modulus
    return determinant


def cauchy_matrix(
    xs: Sequence[int], ys: Sequence[int], modulus: int
) -> list[list[int]]:
    if len(set(xs)) != len(xs) or len(set(ys)) != len(ys):
        raise ValueError("Cauchy nodes must be distinct")
    out: list[list[int]] = []
    for x in xs:
        row = []
        for y in ys:
            denominator = (1 + x * y) % modulus
            if denominator == 0:
                raise ValueError("Cauchy denominator vanished")
            row.append(pow(denominator, -1, modulus))
        out.append(row)
    return out


def cauchy_determinant_formula(
    xs: Sequence[int], ys: Sequence[int], modulus: int
) -> int:
    if len(xs) != len(ys):
        raise ValueError("equal node counts required")
    if len(set(xs)) != len(xs) or len(set(ys)) != len(ys):
        return 0
    numerator = 1
    for left in range(len(xs)):
        for right in range(left + 1, len(xs)):
            numerator = numerator * (xs[left] - xs[right]) % modulus
            numerator = numerator * (ys[right] - ys[left]) % modulus
    denominator = 1
    for x in xs:
        for y in ys:
            term = (1 + x * y) % modulus
            if term == 0:
                raise ValueError("Cauchy denominator vanished")
            denominator = denominator * term % modulus
    return numerator * pow(denominator, -1, modulus) % modulus


def row_nodes(order: int, root: int, modulus: int) -> list[int]:
    return [pow(root, (-r) % order, modulus) for r in range(order)]


def column_nodes(order: int, root: int, modulus: int) -> list[int]:
    return [0] + [pow(root, s, modulus) for s in range(order)]


def check_minor(xs: list[int], ys: list[int], modulus: int) -> None:
    determinant = mod_determinant(cauchy_matrix(xs, ys, modulus), modulus)
    formula = cauchy_determinant_formula(xs, ys, modulus)
    if determinant == 0 or determinant != formula:
        raise AssertionError("Cauchy full-spark identity failed")


def verify_exhaustive_cauchy_minors(order: int) -> dict[str, Any]:
    modulus, root = find_root_field(order)
    rows = row_nodes(order, root, modulus)
    columns = column_nodes(order, root, modulus)
    checked = 0
    size_counts: dict[str, int] = {}
    for size in range(1, order + 1):
        local = 0
        for row_indices in itertools.combinations(range(order), size):
            xs = [rows[i] for i in row_indices]
            for column_indices in itertools.combinations(range(order + 1), size):
                check_minor(xs, [columns[i] for i in column_indices], modulus)
                checked += 1
                local += 1
        size_counts[str(size)] = local
    expected = math.comb(2 * order + 1, order) - 1
    if checked != expected:
        raise AssertionError("minor count drifted")
    return {
        "n": order,
        "field_prime": modulus,
        "root": root,
        "minors_checked": checked,
        "expected_minors": expected,
        "size_counts": size_counts,
        "failures": 0,
    }


def sample_indices(universe: int, size: int, shift: int) -> list[int]:
    if size > universe:
        raise ValueError("sample exceeds universe")
    step = universe - 1 if math.gcd(universe - 1, universe) == 1 else 1
    out: list[int] = []
    cursor = shift % universe
    while len(out) < size:
        if cursor not in out:
            out.append(cursor)
        cursor = (cursor + step) % universe
    return out


def verify_sampled_cauchy_minors(order: int) -> dict[str, Any]:
    modulus, root = find_root_field(order)
    rows = row_nodes(order, root, modulus)
    columns = column_nodes(order, root, modulus)
    checked = 0
    max_size = min(8, order)
    for size in range(1, max_size + 1):
        for shift in range(4):
            xs = [rows[i] for i in sample_indices(order, size, shift)]
            ys = [
                columns[i]
                for i in sample_indices(order + 1, size, 2 * shift + 1)
            ]
            check_minor(xs, ys, modulus)
            checked += 1
    return {
        "n": order,
        "field_prime": modulus,
        "root": root,
        "sampled_minors": checked,
        "max_minor_size": max_size,
        "failures": 0,
    }
