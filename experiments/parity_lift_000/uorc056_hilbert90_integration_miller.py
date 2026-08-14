#!/usr/bin/env python3
"""Compact Miller representative for UORC056 Hilbert-90 integration B13."""
from __future__ import annotations

from uorc056_oriented_principal_pell_core import Point, ec_add, inv


def line_value(left: Point, right: Point, query: Point, p: int) -> int:
    if left is None or right is None or query is None:
        raise ZeroDivisionError("line evaluation at O")
    x1, y1 = left
    x2, y2 = right
    x, y = query
    if x1 == x2 and (y1 + y2) % p == 0:
        return (x - x1) % p
    slope = (
        3 * x1 * x1 * inv(2 * y1, p)
        if left == right
        else (y2 - y1) * inv(x2 - x1, p)
    ) % p
    return (y - y1 - slope * (x - x1)) % p


def g_value(left: Point, right: Point, query: Point, p: int) -> int:
    if left is None or right is None:
        return 1
    numerator = line_value(left, right, query, p)
    point_sum = ec_add(left, right, p)
    if point_sum is None:
        return numerator
    if query is None:
        raise ZeroDivisionError("vertical denominator at O")
    denominator = (query[0] - point_sum[0]) % p
    if denominator == 0:
        raise ZeroDivisionError("vertical denominator vanished")
    return numerator * inv(denominator, p) % p


def miller_value(multiplier: int, base: Point, query: Point, p: int) -> tuple[int, int]:
    if multiplier <= 0 or base is None:
        raise ValueError("positive multiplier and finite base required")
    accumulator = 1
    running = base
    steps = 0
    for bit in bin(multiplier)[3:]:
        accumulator = accumulator * accumulator % p
        accumulator = accumulator * g_value(running, running, query, p) % p
        running = ec_add(running, running, p)
        steps += 1
        if bit == "1":
            accumulator = accumulator * g_value(running, base, query, p) % p
            running = ec_add(running, base, p)
            steps += 1
    return accumulator, steps


def projective_cocycle(
    query: Point, p: int, order: int, points: list[Point], anchor_scalar: int
) -> tuple[int, int]:
    """h0 = g_(A-T,T)/(ell_(-G,-G) F_((n+1)/2,-T))."""
    translation = points[2]
    minus_translation = points[order - 2]
    minus_generator = points[order - 1]
    anchor = points[anchor_scalar]
    anchor_minus_translation = ec_add(anchor, minus_translation, p)
    numerator = g_value(anchor_minus_translation, translation, query, p)
    tangent = line_value(minus_generator, minus_generator, query, p)
    miller, steps = miller_value((order + 1) // 2, minus_translation, query, p)
    denominator = tangent * miller % p
    if denominator == 0:
        raise ZeroDivisionError("projective cocycle denominator vanished")
    return numerator * inv(denominator, p) % p, steps + 2
