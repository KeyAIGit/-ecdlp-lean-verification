
#!/usr/bin/env python3
"""Exact frozen replay for the oriented principal half-divisor/Pell boundary.

No external curve, point, key, wallet, unknown scalar, or production-sized
discrete-log target is accepted.  Production-size constants are used only for
integer cost and congruence certificates.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Optional

Point = Optional[tuple[int, int]]
B_CURVE = 7
SECP_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

FROZEN_CASES = (
    (13, 7, (7, 5)),
    (43, 31, (2, 12)),
    (61, 61, (2, 25)),
    (67, 79, (2, 22)),
    (79, 67, (1, 18)),
    (97, 79, (1, 28)),
    (127, 127, (1, 32)),
    (163, 139, (2, 34)),
    (211, 199, (3, 33)),
    (349, 313, (2, 109)),
)


def inv(value: int, modulus: int) -> int:
    return pow(value % modulus, -1, modulus)


def quadratic_character(value: int, p: int) -> int:
    value %= p
    if value == 0:
        return 0
    residue = pow(value, (p - 1) // 2, p)
    if residue == 1:
        return 1
    if residue == p - 1:
        return -1
    raise AssertionError("Euler criterion returned an invalid value")


def ec_add(left: Point, right: Point, p: int) -> Point:
    if left is None:
        return right
    if right is None:
        return left
    x_left, y_left = left
    x_right, y_right = right
    if x_left == x_right and (y_left + y_right) % p == 0:
        return None
    if left == right:
        slope = 3 * x_left * x_left * inv(2 * y_left, p) % p
    else:
        slope = (y_right - y_left) * inv(x_right - x_left, p) % p
    x_sum = (slope * slope - x_left - x_right) % p
    y_sum = (slope * (x_left - x_sum) - y_left) % p
    return x_sum, y_sum


def scalar_mul(scalar: int, point: Point, p: int) -> Point:
    result: Point = None
    addend = point
    while scalar:
        if scalar & 1:
            result = ec_add(result, addend, p)
        addend = ec_add(addend, addend, p)
        scalar >>= 1
    return result


def orbit(generator: tuple[int, int], order: int, p: int) -> list[Point]:
    points: list[Point] = [None]
    current: Point = None
    for _ in range(1, order):
        current = ec_add(current, generator, p)
        points.append(current)
    if ec_add(current, generator, p) is not None:
        raise AssertionError("generator does not have the declared order")
    return points


def trim(polynomial: list[int], p: int) -> list[int]:
    result = [coefficient % p for coefficient in polynomial]
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def poly_add(left: list[int], right: list[int], p: int) -> list[int]:
    size = max(len(left), len(right))
    return trim(
        [
            (left[index] if index < len(left) else 0)
            + (right[index] if index < len(right) else 0)
            for index in range(size)
        ],
        p,
    )


def poly_sub(left: list[int], right: list[int], p: int) -> list[int]:
    return poly_add(left, [(-value) % p for value in right], p)


def poly_mul(left: list[int], right: list[int], p: int) -> list[int]:
    result = [0] * (len(left) + len(right) - 1)
    for left_index, left_value in enumerate(left):
        for right_index, right_value in enumerate(right):
            result[left_index + right_index] = (
                result[left_index + right_index] + left_value * right_value
            ) % p
    return trim(result, p)


def poly_eval(polynomial: list[int], value: int, p: int) -> int:
    result = 0
    for coefficient in reversed(polynomial):
        result = (result * value + coefficient) % p
    return result


def poly_divmod(
    numerator: list[int], denominator: list[int], p: int
) -> tuple[list[int], list[int]]:
    numerator = trim(numerator.copy(), p)
    denominator = trim(denominator.copy(), p)
    if denominator == [0]:
        raise ZeroDivisionError("zero polynomial")
    if len(numerator) < len(denominator):
        return [0], numerator
    quotient = [0] * (len(numerator) - len(denominator) + 1)
    inverse_lead = inv(denominator[-1], p)
    while numerator != [0] and len(numerator) >= len(denominator):
        shift = len(numerator) - len(denominator)
        coefficient = numerator[-1] * inverse_lead % p
        quotient[shift] = coefficient
        for index, value in enumerate(denominator):
            numerator[index + shift] = (
                numerator[index + shift] - coefficient * value
            ) % p
        numerator = trim(numerator, p)
    return trim(quotient, p), numerator


def nullspace_mod(matrix: list[list[int]], p: int) -> list[list[int]]:
    if not matrix:
        return []
    work = [[entry % p for entry in row] for row in matrix]
    row_count = len(work)
    column_count = len(work[0])
    pivots: list[int] = []
    pivot_row = 0
    for column in range(column_count):
        selected = next(
            (
                row
                for row in range(pivot_row, row_count)
                if work[row][column] % p != 0
            ),
            None,
        )
        if selected is None:
            continue
        work[pivot_row], work[selected] = work[selected], work[pivot_row]
        scale = inv(work[pivot_row][column], p)
        work[pivot_row] = [
            (value * scale) % p for value in work[pivot_row]
        ]
        for row in range(row_count):
            if row == pivot_row or work[row][column] == 0:
                continue
            factor = work[row][column]
            work[row] = [
                (work[row][index] - factor * work[pivot_row][index]) % p
                for index in range(column_count)
            ]
        pivots.append(column)
        pivot_row += 1
        if pivot_row == row_count:
            break
    free_columns = [
        column for column in range(column_count) if column not in pivots
    ]
    basis: list[list[int]] = []
    for free_column in free_columns:
        vector = [0] * column_count
        vector[free_column] = 1
        for row, pivot_column in enumerate(pivots):
            vector[pivot_column] = (-work[row][free_column]) % p
        basis.append(vector)
    return basis


def kernel_polynomial(points: list[Point], order: int, p: int) -> list[int]:
    half = (order - 1) // 2
    kernel = [1]
    for scalar in range(1, half + 1):
        point = points[scalar]
        if point is None:
            raise AssertionError("unexpected identity in kernel support")
        kernel = poly_mul(kernel, [(-point[0]) % p, 1], p)
    return kernel


def normalize_vector(vector: list[int], p: int) -> list[int]:
    last = max(index for index, value in enumerate(vector) if value % p != 0)
    scale = inv(vector[last], p)
    return [(value * scale) % p for value in vector]


def proportional(
    left: list[int], right: list[int], p: int
) -> bool:
    pivot = next(
        (
            index
            for index, (left_value, right_value) in enumerate(zip(left, right))
            if left_value % p != 0 or right_value % p != 0
        ),
        None,
    )
    if pivot is None:
        return True
    if left[pivot] % p == 0 or right[pivot] % p == 0:
        return False
    ratio = left[pivot] * inv(right[pivot], p) % p
    return all(
        (left[index] - ratio * right[index]) % p == 0
        for index in range(len(left))
    )

