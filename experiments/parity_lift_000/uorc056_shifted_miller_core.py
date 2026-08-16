#!/usr/bin/env python3
"""Exact C35 replay for anchor-mixed shifted Miller states.

Frozen toy curves only. No external point, key, wallet, or production target is
accepted by this program.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from math import comb, gcd
from pathlib import Path
from typing import Iterable, Optional

BasePoint = Optional[tuple[int, int]]
Ext = tuple[int, int]
ExtPoint = Optional[tuple[Ext, Ext]]

SECP_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


@dataclass(frozen=True)
class Curve:
    p: int
    a: int
    b: int

    def add(self, left: BasePoint, right: BasePoint) -> BasePoint:
        p = self.p
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
            slope = (3 * x1 * x1 + self.a) * pow(2 * y1, -1, p) % p
        else:
            slope = (y2 - y1) * pow(x2 - x1, -1, p) % p
        x3 = (slope * slope - x1 - x2) % p
        y3 = (slope * (x1 - x3) - y1) % p
        return x3, y3

    def neg(self, point: BasePoint) -> BasePoint:
        if point is None:
            return None
        return point[0], (-point[1]) % self.p

    def mul(self, scalar: int, point: BasePoint) -> BasePoint:
        if scalar < 0:
            return self.mul(-scalar, self.neg(point))
        out: BasePoint = None
        addend = point
        value = scalar
        while value:
            if value & 1:
                out = self.add(out, addend)
            addend = self.add(addend, addend)
            value >>= 1
        return out


@dataclass(frozen=True)
class Instance:
    name: str
    curve: Curve
    n: int
    G: tuple[int, int]


INSTANCES = (
    Instance("E7-P43-N31", Curve(43, 0, 7), 31, (2, 12)),
    Instance("E7-P67-N79", Curve(67, 0, 7), 79, (2, 22)),
    Instance("E7-P79-N67", Curve(79, 0, 7), 67, (1, 18)),
    Instance("E7-P127-N127", Curve(127, 0, 7), 127, (1, 32)),
    Instance("E7-P163-N139", Curve(163, 0, 7), 139, (2, 34)),
)

COMMON_CHARACTER_ORDERS = (2, 3, 4, 6, 8, 12, 24)


def legendre(value: int, p: int) -> int:
    value %= p
    if value == 0:
        return 0
    return 1 if pow(value, (p - 1) // 2, p) == 1 else -1


def factor_integer(value: int) -> dict[int, int]:
    out: dict[int, int] = {}
    divisor = 2
    remaining = value
    while divisor * divisor <= remaining:
        while remaining % divisor == 0:
            out[divisor] = out.get(divisor, 0) + 1
            remaining //= divisor
        divisor = 3 if divisor == 2 else divisor + 2
    if remaining > 1:
        out[remaining] = out.get(remaining, 0) + 1
    return out


def divisors_from_factorization(factors: dict[int, int]) -> list[int]:
    values = [1]
    for prime, exponent in sorted(factors.items()):
        current = []
        power = 1
        for _ in range(exponent + 1):
            current.extend(value * power for value in values)
            power *= prime
        values = current
    return sorted(values)


class Fp2Field:
    __slots__ = ("p", "d", "zero", "one")

    def __init__(self, p: int, d: int):
        if legendre(d, p) != -1:
            raise ValueError("d must be a quadratic nonsquare")
        self.p = p
        self.d = d % p
        self.zero = (0, 0)
        self.one = (1, 0)

    def e(self, value: int) -> Ext:
        return value % self.p, 0

    def add(self, x: Ext, y: Ext) -> Ext:
        return (x[0] + y[0]) % self.p, (x[1] + y[1]) % self.p

    def neg(self, x: Ext) -> Ext:
        return (-x[0]) % self.p, (-x[1]) % self.p

    def sub(self, x: Ext, y: Ext) -> Ext:
        return (x[0] - y[0]) % self.p, (x[1] - y[1]) % self.p

    def mul(self, x: Ext, y: Ext) -> Ext:
        return (
            (x[0] * y[0] + self.d * x[1] * y[1]) % self.p,
            (x[0] * y[1] + x[1] * y[0]) % self.p,
        )

    def inv(self, x: Ext) -> Ext:
        denominator = (x[0] * x[0] - self.d * x[1] * x[1]) % self.p
        if denominator == 0:
            raise ZeroDivisionError("zero in Fp2")
        inverse = pow(denominator, -1, self.p)
        return x[0] * inverse % self.p, -x[1] * inverse % self.p

    def div(self, x: Ext, y: Ext) -> Ext:
        return self.mul(x, self.inv(y))

    def pow(self, x: Ext, exponent: int) -> Ext:
        if exponent < 0:
            return self.pow(self.inv(x), -exponent)
        out = self.one
        base = x
        value = exponent
        while value:
            if value & 1:
                out = self.mul(out, base)
            base = self.mul(base, base)
            value >>= 1
        return out

    def conj(self, x: Ext) -> Ext:
        return x[0], (-x[1]) % self.p

    def scale(self, scalar: int, x: Ext) -> Ext:
        return scalar * x[0] % self.p, scalar * x[1] % self.p


@dataclass(frozen=True)
class ExtCurve:
    base: Curve
    field: Fp2Field

    def embed(self, point: BasePoint) -> ExtPoint:
        if point is None:
            return None
        return self.field.e(point[0]), self.field.e(point[1])

    def neg(self, point: ExtPoint) -> ExtPoint:
        if point is None:
            return None
        return point[0], self.field.neg(point[1])

    def add(self, left: ExtPoint, right: ExtPoint) -> ExtPoint:
        F = self.field
        if left is None:
            return right
        if right is None:
            return left
        x1, y1 = left
        x2, y2 = right
        if x1 == x2 and F.add(y1, y2) == F.zero:
            return None
        if left == right:
            if y1 == F.zero:
                return None
            numerator = F.add(F.scale(3, F.mul(x1, x1)), F.e(self.base.a))
            slope = F.div(numerator, F.scale(2, y1))
        else:
            slope = F.div(F.sub(y2, y1), F.sub(x2, x1))
        x3 = F.sub(F.sub(F.mul(slope, slope), x1), x2)
        y3 = F.sub(F.mul(slope, F.sub(x1, x3)), y1)
        return x3, y3

    def mul(self, scalar: int, point: ExtPoint) -> ExtPoint:
        if scalar < 0:
            return self.mul(-scalar, self.neg(point))
        out: ExtPoint = None
        addend = point
        value = scalar
        while value:
            if value & 1:
                out = self.add(out, addend)
            addend = self.add(addend, addend)
            value >>= 1
        return out


def poly_eval_base(coefficients: list[int], x: int, p: int) -> int:
    out = 0
    for coefficient in reversed(coefficients):
        out = (out * x + coefficient) % p
    return out


def poly_eval_ext(coefficients: list[int], x: Ext, field: Fp2Field) -> Ext:
    out = field.zero
    for coefficient in reversed(coefficients):
        out = field.add(field.mul(out, x), field.e(coefficient))
    return out


def local_y_series(curve: Curve, point: tuple[int, int], order: int) -> list[int]:
    """Expansion y(x0+t) to t^order using x-x0 as local parameter."""
    p = curve.p
    x0, y0 = point
    rhs = [0] * (order + 1)
    rhs[0] = (x0 * x0 * x0 + curve.a * x0 + curve.b) % p
    if order >= 1:
        rhs[1] = (3 * x0 * x0 + curve.a) % p
    if order >= 2:
        rhs[2] = 3 * x0 % p
    if order >= 3:
        rhs[3] = 1
    series = [0] * (order + 1)
    series[0] = y0 % p
    inverse_two_y = pow(2 * y0, -1, p)
    for degree in range(1, order + 1):
        cross = sum(series[i] * series[degree - i] for i in range(1, degree)) % p
        series[degree] = (rhs[degree] - cross) * inverse_two_y % p
    return series


def x_power_series(x0: int, exponent: int, order: int, p: int) -> list[int]:
    coefficients = [0] * (order + 1)
    for degree in range(min(exponent, order) + 1):
        coefficients[degree] = comb(exponent, degree) * pow(x0, exponent - degree, p) % p
    return coefficients


def convolve_truncated(left: list[int], right: list[int], order: int, p: int) -> list[int]:
    out = [0] * (order + 1)
    for i, x in enumerate(left):
        if x == 0:
            continue
        for j, y in enumerate(right[: order + 1 - i]):
            out[i + j] = (out[i + j] + x * y) % p
    return out


def nullspace_vector(matrix: list[list[int]], p: int) -> list[int]:
    work = [[value % p for value in row] for row in matrix]
    rows = len(work)
    cols = len(work[0]) if rows else 0
    pivot_cols: list[int] = []
    pivot_row = 0
    for col in range(cols):
        pivot = next((row for row in range(pivot_row, rows) if work[row][col]), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        inverse = pow(work[pivot_row][col], -1, p)
        work[pivot_row] = [value * inverse % p for value in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row or work[row][col] == 0:
                continue
            factor = work[row][col]
            work[row] = [
                (left - factor * right) % p
                for left, right in zip(work[row], work[pivot_row])
            ]
        pivot_cols.append(col)
        pivot_row += 1
        if pivot_row == rows:
            break
    free_cols = [col for col in range(cols) if col not in pivot_cols]
    if len(free_cols) != 1:
        raise AssertionError(f"expected one-dimensional nullspace, found {len(free_cols)}")
    free = free_cols[0]
    vector = [0] * cols
    vector[free] = 1
    for row, col in reversed(list(enumerate(pivot_cols))):
        vector[col] = -work[row][free] % p
    first = next(value for value in vector if value)
    inverse = pow(first, -1, p)
    return [value * inverse % p for value in vector]


@dataclass(frozen=True)
class MillerSection:
    curve: Curve
    n: int
    A: tuple[int, ...]
    B: tuple[int, ...]
    leading_local_coefficient: int

    def eval_base(self, point: BasePoint) -> int:
        if point is None:
            raise ValueError("section has a pole at O")
        x, y = point
        p = self.curve.p
        return (poly_eval_base(list(self.A), x, p) + y * poly_eval_base(list(self.B), x, p)) % p

    def eval_ext(self, point: ExtPoint, field: Fp2Field) -> Ext:
        if point is None:
            raise ValueError("section has a pole at O")
        x, y = point
        return field.add(
            poly_eval_ext(list(self.A), x, field),
            field.mul(y, poly_eval_ext(list(self.B), x, field)),
        )


def build_miller_section(instance: Instance) -> MillerSection:
    curve, n, G = instance.curve, instance.n, instance.G
    p = curve.p
    half = (n - 1) // 2
    y_series = local_y_series(curve, G, n)
    basis_series: list[list[int]] = []
    for exponent in range(half + 1):
        basis_series.append(x_power_series(G[0], exponent, n, p))
    for exponent in range(half):
        basis_series.append(convolve_truncated(
            y_series, x_power_series(G[0], exponent, n, p), n, p
        ))
    matrix = [[basis_series[col][row] for col in range(n)] for row in range(n)]
    vector = nullspace_vector(matrix, p)
    leading = sum(vector[col] * basis_series[col][n] for col in range(n)) % p
    if leading == 0:
        raise AssertionError("section vanishes beyond declared order")
    section = MillerSection(curve, n, tuple(vector[: half + 1]), tuple(vector[half + 1 :]), leading)
    table = [curve.mul(k, G) for k in range(n)]
    zeros = [k for k in range(1, n) if section.eval_base(table[k]) == 0]
    if zeros != [1]:
        raise AssertionError(f"unexpected rational zeros: {zeros}")
    return section


def smallest_nonsquare(p: int) -> int:
    return next(value for value in range(2, p) if legendre(value, p) == -1)


def twist_points(instance: Instance, field: Fp2Field) -> list[ExtPoint]:
    p = instance.curve.p
    inverse_d = pow(field.d, -1, p)
    points: list[ExtPoint] = []
    for x in range(p):
        scaled = (x * x * x + instance.curve.a * x + instance.curve.b) * inverse_d % p
        if scaled == 0 or legendre(scaled, p) != 1:
            continue
        root = pow(scaled, (p + 1) // 4, p)
        for y in sorted({root, (-root) % p}):
            points.append(((x, 0), (0, y)))
    return points
