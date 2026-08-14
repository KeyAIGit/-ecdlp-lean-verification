#!/usr/bin/env python3
"""Shared frozen arithmetic for UORC056 Hilbert-90 integration B13."""
from __future__ import annotations

from uorc056_oriented_principal_pell_core import (
    B_CURVE,
    Point,
    ec_add,
    normalize_vector,
    nullspace_mod,
    orbit,
    poly_eval,
    trim,
)

COSET_CASES = (
    (31, 7, (27, 6), (0, 10), 21),
    (37, 13, (8, 36), (0, 9), 39),
    (101, 17, (62, 50), (4, 24), 102),
    (103, 37, (38, 17), (0, 25), 111),
    (109, 43, (4, 17), (0, 15), 129),
)


def neg(point: Point, p: int) -> Point:
    return None if point is None else (point[0], (-point[1]) % p)


def scalar_mul(scalar: int, point: Point, p: int) -> Point:
    result: Point = None
    addend = point
    while scalar:
        if scalar & 1:
            result = ec_add(result, addend, p)
        addend = ec_add(addend, addend, p)
        scalar >>= 1
    return result


def affine_point_count(p: int) -> int:
    return sum(
        y * y % p == (x**3 + B_CURVE) % p
        for x in range(p)
        for y in range(p)
    )


def construct_factor(
    p: int, order: int, generator: tuple[int, int]
) -> tuple[list[Point], list[int], list[int], int, int]:
    points = orbit(generator, order, p)
    half = (order - 1) // 2
    pole_order = half + 1
    sum_scalar = (-pow(4, -1, order)) % order
    anchor_scalar = (-sum_scalar) % order
    support = [points[scalar] for scalar in range(2, order, 2)]
    anchor = points[anchor_scalar]

    support_sum: Point = None
    for point in support:
        support_sum = ec_add(support_sum, point, p)
    if support_sum != points[sum_scalar] or ec_add(support_sum, anchor, p) is not None:
        raise AssertionError("canonical principal divisor identity failed")

    count_a = pole_order // 2 + 1
    count_b = max(0, (pole_order - 3) // 2 + 1)
    rows: list[list[int]] = []
    for point in support + [anchor]:
        if point is None:
            raise AssertionError("principal zero divisor contains the identity")
        x, y = point
        row = [pow(x, degree, p) for degree in range(count_a)]
        row.extend(y * pow(x, degree, p) % p for degree in range(count_b))
        rows.append(row)
    basis = nullspace_mod(rows, p)
    if len(basis) != 1:
        raise AssertionError(f"Riemann-Roch nullspace dimension is {len(basis)}")
    vector = normalize_vector(basis[0], p)
    polynomial_a = trim(vector[:count_a], p)
    polynomial_b = trim(vector[count_a:], p) if count_b else [0]
    return points, polynomial_a, polynomial_b, sum_scalar, anchor_scalar


def factor_value(
    polynomial_a: list[int], polynomial_b: list[int], point: Point, p: int
) -> int:
    if point is None:
        raise ZeroDivisionError("principal factor has a pole at O")
    x, y = point
    return (poly_eval(polynomial_a, x, p) + y * poly_eval(polynomial_b, x, p)) % p
