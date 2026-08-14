#!/usr/bin/env python3
"""Shared exact finite-field utilities for UORC-056 divisor-aware toy screens."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TypeAlias

Point: TypeAlias = tuple[int, int] | None
SparseValuation: TypeAlias = tuple[tuple[int, int], ...]

DISCOVERY_CURVES = (
    (43, 31, (2, 12)),
    (67, 79, (2, 22)),
    (79, 67, (1, 18)),
    (127, 127, (1, 32)),
    (163, 139, (2, 34)),
)


@dataclass(frozen=True)
class CurveData:
    p: int
    n: int
    generator: tuple[int, int]
    points: tuple[Point, ...]
    coefficients: dict[str, int]
    offset: int


def inv(value: int, p: int) -> int:
    value %= p
    if not value:
        raise ZeroDivisionError("zero has no inverse")
    return pow(value, -1, p)


def ec_add(left: Point, right: Point, p: int) -> Point:
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
        slope = 3 * x1 * x1 * inv(2 * y1, p) % p
    else:
        slope = (y2 - y1) * inv(x2 - x1, p) % p
    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    return x3, y3


def orbit(generator: tuple[int, int], order: int, p: int) -> tuple[Point, ...]:
    points: list[Point] = [None]
    point: Point = None
    for _ in range(1, order):
        point = ec_add(point, generator, p)
        if point is None:
            raise AssertionError("generator returned to infinity too early")
        points.append(point)
    if ec_add(points[-1], generator, p) is not None:
        raise AssertionError("declared generator order is wrong")
    if len(set(points)) != order:
        raise AssertionError("orbit is not simple")
    for affine in points[1:]:
        assert affine is not None
        x, y = affine
        if (y * y - x * x * x - 7) % p:
            raise AssertionError("point is not on y^2=x^3+7")
    return tuple(points)


def quadratic_character(value: int, p: int) -> int:
    value %= p
    if value == 0:
        return 0
    symbol = pow(value, (p - 1) // 2, p)
    if symbol == 1:
        return 1
    if symbol == p - 1:
        return -1
    raise AssertionError("Euler criterion returned a non-sign")


def beta_roots(p: int) -> tuple[int, int]:
    roots = sorted(z for z in range(p) if z != 1 and (z * z + z + 1) % p == 0)
    if len(roots) != 2:
        raise AssertionError(f"F_{p} lacks the declared nontrivial cube roots")
    return roots[0], roots[1]


def coefficient_table(p: int, generator: tuple[int, int]) -> dict[str, int]:
    beta_lo, beta_hi = beta_roots(p)
    xg, yg = generator
    return {
        "zero": 0,
        "one": 1,
        "neg_one": -1 % p,
        "two": 2,
        "neg_two": -2 % p,
        "curve_b": 7 % p,
        "neg_curve_b": -7 % p,
        "x_G": xg % p,
        "neg_x_G": -xg % p,
        "y_G": yg % p,
        "neg_y_G": -yg % p,
        "beta_lo": beta_lo,
        "beta_hi": beta_hi,
        "x_G_plus_y_G": (xg + yg) % p,
        "x_G_minus_y_G": (xg - yg) % p,
    }


def build_discovery_corpus() -> tuple[
    tuple[CurveData, ...], int, int, list[dict[str, object]]
]:
    curves: list[CurveData] = []
    public: list[dict[str, object]] = []
    target_bits = 0
    offset = 0
    for p, n, generator in DISCOVERY_CURVES:
        points = orbit(generator, n, p)
        coefficients = coefficient_table(p, generator)
        curves.append(CurveData(p, n, generator, points, coefficients, offset))
        for k in range(1, n):
            if k & 1:
                target_bits |= 1 << (offset + k - 1)
        public.append({
            "p": p,
            "n": n,
            "G": list(generator),
            "beta_lo": coefficients["beta_lo"],
            "beta_hi": coefficients["beta_hi"],
        })
        offset += n - 1
    return tuple(curves), target_bits, offset, public


def local_line_order_and_coefficient(
    point: tuple[int, int], a: int, b: int, c: int, p: int
) -> tuple[int, int]:
    """Return ord_t(a*x+b*y+c) and its leading coefficient for t=x-x(P)."""
    x0, y0 = point
    y1 = 3 * x0 * x0 * inv(2 * y0, p) % p
    y2 = (3 * x0 - y1 * y1) * inv(2 * y0, p) % p
    y3 = (1 - 2 * y1 * y2) * inv(2 * y0, p) % p
    coefficients = (
        (a * x0 + b * y0 + c) % p,
        (a + b * y1) % p,
        (b * y2) % p,
        (b * y3) % p,
    )
    for order, coefficient in enumerate(coefficients):
        if coefficient:
            return order, coefficient
    raise AssertionError("nonzero line has contact order greater than three")


def pulled_line_local_data(
    curve: CurveData,
    scalar_index: int,
    multiplier: int,
    line: tuple[int, int, int],
) -> tuple[int, int]:
    point = curve.points[scalar_index]
    image = curve.points[(multiplier * scalar_index) % curve.n]
    assert point is not None and image is not None
    order, leading = local_line_order_and_coefficient(image, *line, curve.p)
    if order == 0:
        return 0, leading
    alpha = multiplier * image[1] * inv(point[1], curve.p) % curve.p
    if alpha == 0:
        raise AssertionError("declared multiplication map is not etale")
    return order, leading * pow(alpha, order, curve.p) % curve.p


def add_sparse(left: SparseValuation, right: SparseValuation) -> SparseValuation:
    output: list[tuple[int, int]] = []
    i = j = 0
    while i < len(left) or j < len(right):
        if j == len(right) or (i < len(left) and left[i][0] < right[j][0]):
            output.append(left[i])
            i += 1
        elif i == len(left) or right[j][0] < left[i][0]:
            output.append(right[j])
            j += 1
        else:
            total = left[i][1] + right[j][1]
            if total:
                output.append((left[i][0], total))
            i += 1
            j += 1
    return tuple(output)


def negate_sparse(value: SparseValuation) -> SparseValuation:
    return tuple((index, -order) for index, order in value)


def stable_json(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"
