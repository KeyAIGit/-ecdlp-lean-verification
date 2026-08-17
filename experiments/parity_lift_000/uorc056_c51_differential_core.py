#!/usr/bin/env python3
"""UORC-056 C51: anchor-normalized differential/Fay gauge boundary.

This package uses only fixed public toy curves and public secp256k1 constants.
It accepts no external target, unknown scalar, private key, wallet, or user
supplied branch value.

The exact positive result is a differential normal form.  The first logarithmic
derivative of a period-shifted rank-two sigma/net section does not expose the
integer lift of Q=[k]G.  Its quasiperiod term cancels and the result is a linear
combination of periodic regularized torsion jets H(P).  Higher logarithmic
derivatives are ordinary elliptic coordinate functions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

Point = Optional[tuple[int, int]]

SECP_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
SECP_G = (
    55066263022277343669578718895168534326250603453777594175500187360389116729240,
    32670510020758816978083085130507043184471273380659243275938904335757337482424,
)

# Prime-to-characteristic exact corpus.  The p=n anomalous controls are listed
# separately and are deliberately excluded from the separable torsion-jet claim.
FROZEN = (
    (43, 31, (2, 12), 6, 5),
    (67, 79, (2, 22), 29, 23),
    (79, 67, (1, 18), 23, 29),
    (163, 139, (2, 34), 58, 96),
)
HELD_OUT = (
    (97, 79, (1, 28), 35, 55),
    (211, 199, (3, 33), 14, 106),
    (349, 313, (2, 109), 122, 214),
    (433, 397, (1, 21), 198, 362),
    (577, 613, (1, 68), 213, 65),
    (733, 691, (6, 174), 307, 253),
    (823, 829, (1, 255), 174, 125),
    (907, 967, (2, 165), 384, 824),
)
ANOMALOUS_CONTROLS = (
    (127, 127, (1, 32)),
    (61, 61, (2, 25)),
)


@dataclass(frozen=True)
class Curve:
    p: int
    b: int = 7

    def neg(self, point: Point) -> Point:
        return None if point is None else (point[0], (-point[1]) % self.p)

    def add(self, left: Point, right: Point) -> Point:
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
            if y1 == 0:
                return None
            slope = 3 * x1 * x1 * pow(2 * y1, -1, p) % p
        else:
            slope = (y2 - y1) * pow(x2 - x1, -1, p) % p
        x3 = (slope * slope - x1 - x2) % p
        y3 = (slope * (x1 - x3) - y1) % p
        return x3, y3

    def mul(self, scalar: int, point: Point, order: int | None = None) -> Point:
        if order is not None:
            scalar %= order
        if scalar < 0:
            return self.mul(-scalar, self.neg(point), order)
        out = None
        addend = point
        while scalar:
            if scalar & 1:
                out = self.add(out, addend)
            addend = self.add(addend, addend)
            scalar >>= 1
        return out


def quadratic_character(value: int, prime: int) -> int:
    value %= prime
    if value == 0:
        return 0
    return 1 if pow(value, (prime - 1) // 2, prime) == 1 else -1


def is_prime(value: int) -> bool:
    if value < 2:
        return False
    if value % 2 == 0:
        return value == 2
    divisor = 3
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += 2
    return True


def point_count(curve: Curve) -> int:
    total = 1
    for x in range(curve.p):
        rhs = (x * x * x + curve.b) % curve.p
        symbol = quadratic_character(rhs, curve.p)
        total += 1 if symbol == 0 else 2 if symbol == 1 else 0
    return total


class Series:
    """Truncated power series over F_p in ascending coefficient order."""

    __slots__ = ("coefficients", "p", "length")

    def __init__(self, coefficients, prime: int, length: int):
        raw = list(coefficients) + [0] * length
        self.p = prime
        self.length = length
        self.coefficients = tuple(raw[index] % prime for index in range(length))

    @classmethod
    def constant(cls, value: int, prime: int, length: int) -> "Series":
        return cls([value], prime, length)

    def coerce(self, other) -> "Series":
        if isinstance(other, Series):
            if other.p != self.p or other.length != self.length:
                raise ValueError("incompatible series")
            return other
        return Series.constant(int(other), self.p, self.length)

    def __add__(self, other):
        other = self.coerce(other)
        return Series(
            [a + b for a, b in zip(self.coefficients, other.coefficients)],
            self.p,
            self.length,
        )

    __radd__ = __add__

    def __neg__(self):
        return Series([-value for value in self.coefficients], self.p, self.length)

    def __sub__(self, other):
        return self + (-self.coerce(other))

    def __rsub__(self, other):
        return self.coerce(other) - self

    def __mul__(self, other):
        other = self.coerce(other)
        out = [0] * self.length
        for i, left in enumerate(self.coefficients):
            for j, right in enumerate(other.coefficients):
                if i + j < self.length:
                    out[i + j] = (out[i + j] + left * right) % self.p
        return Series(out, self.p, self.length)

    __rmul__ = __mul__

    def inverse(self):
        if self.coefficients[0] == 0:
            raise ZeroDivisionError("series is not a unit")
        out = [0] * self.length
        out[0] = pow(self.coefficients[0], -1, self.p)
        for degree in range(1, self.length):
            out[degree] = (
                -out[0]
                * sum(
                    self.coefficients[index] * out[degree - index]
                    for index in range(1, degree + 1)
                )
            ) % self.p
        return Series(out, self.p, self.length)

    def __truediv__(self, other):
        return self * self.coerce(other).inverse()

    def __rtruediv__(self, other):
        return self.coerce(other) * self.inverse()

    def __pow__(self, exponent: int):
        if exponent < 0:
            return self.inverse() ** (-exponent)
        result = Series.constant(1, self.p, self.length)
        base = self
        while exponent:
            if exponent & 1:
                result = result * base
            base = base * base
            exponent >>= 1
        return result


class DivisionSeries:
    """Division-polynomial recurrence in the local x-chart at one point."""

    def __init__(self, prime: int, x0: int, y0: int, length: int = 4):
        self.p = prime
        self.length = length
        x = Series([x0, 1], prime, length)
        inverse_two_y = pow(2 * y0, -1, prime)
        y1 = 3 * x0 * x0 * inverse_two_y % prime
        y2 = (3 * x0 - y1 * y1) * inverse_two_y % prime
        y3 = (1 - 2 * y1 * y2) * inverse_two_y % prime
        self.x = x
        self.y = Series([y0, y1, y2, y3], prime, length)
        self.inverse_two_y = (2 * self.y).inverse()
        self.cache: dict[int, Series] = {
            0: Series.constant(0, prime, length),
            1: Series.constant(1, prime, length),
            2: 2 * self.y,
        }
        self.cache[3] = 3 * x**4 + 84 * x
        self.cache[4] = 4 * self.y * (x**6 + 140 * x**3 - 392)

    def psi(self, index: int) -> Series:
        if index < 0:
            return -self.psi(-index)
        if index in self.cache:
            return self.cache[index]
        if index & 1:
            middle = (index - 1) // 2
            value = (
                self.psi(middle + 2) * self.psi(middle) ** 3
                - self.psi(middle - 1) * self.psi(middle + 1) ** 3
            )
        else:
            middle = index // 2
            value = (
                self.psi(middle)
                * self.inverse_two_y
                * (
                    self.psi(middle + 2) * self.psi(middle - 1) ** 2
                    - self.psi(middle - 2) * self.psi(middle + 1) ** 2
                )
            )
        self.cache[index] = value
        return value


class SeriesCurve:
    def __init__(self, prime: int, length: int):
        self.p = prime
        self.length = length

    def constant(self, value: int) -> Series:
        return Series.constant(value, self.p, self.length)

    def neg(self, point):
        return None if point is None else (point[0], -point[1])

    def add(self, left, right):
        if left is None:
            return right
        if right is None:
            return left
        x1, y1 = left
        x2, y2 = right
        if x1.coefficients == x2.coefficients:
            if all(
                (a + b) % self.p == 0
                for a, b in zip(y1.coefficients, y2.coefficients)
            ):
                return None
            slope = 3 * x1 * x1 / (2 * y1)
        else:
            slope = (y2 - y1) / (x2 - x1)
        x3 = slope * slope - x1 - x2
        y3 = slope * (x1 - x3) - y1
        return x3, y3


class NetLineSeries:
    """Local series for A_m(P,Q)=Psi_(1,m)(P,Q)."""

    def __init__(self, prime: int, source: tuple[int, int], target: tuple[int, int], length: int = 4):
        self.p = prime
        self.length = length
        self.curve = SeriesCurve(prime, length)
        self.source = (
            self.curve.constant(source[0]),
            self.curve.constant(source[1]),
        )
        x0, y0 = target
        inverse_two_y = pow(2 * y0, -1, prime)
        y1 = 3 * x0 * x0 * inverse_two_y % prime
        y2 = (3 * x0 - y1 * y1) * inverse_two_y % prime
        y3 = (1 - 2 * y1 * y2) * inverse_two_y % prime
        self.target = (
            Series([x0, 1], prime, length),
            Series([y0, y1, y2, y3], prime, length),
        )
        self.division = DivisionSeries(prime, x0, y0, length)
        plus = self.curve.add(self.source, self.target)
        minus = self.curve.add(self.source, self.curve.neg(self.target))
        if plus is None or minus is None:
            raise ZeroDivisionError("exceptional net seed")
        delta_x = self.target[0] - self.source[0]
        self.delta_x = delta_x
        self.cache: dict[int, Series] = {
            0: self.curve.constant(1),
            1: self.curve.constant(1),
            -1: delta_x,
            2: self.target[0] - plus[0],
            -2: self.target[0] - minus[0],
        }
        self.cache[3] = (
            delta_x * self.cache[2] ** 2 + 4 * plus[1] * self.target[1]
        )
        negative_target = self.curve.neg(self.target)
        self.cache[-3] = (
            delta_x * self.cache[-2] ** 2
            + 4 * minus[1] * negative_target[1]
        )

    def value(self, index: int) -> Series:
        if index in self.cache:
            return self.cache[index]
        if index & 1:
            middle = (index - 1) // 2
            numerator = (
                self.value(middle + 2)
                * self.value(middle - 1)
                * self.division.psi(middle + 1)
                * self.division.psi(middle)
                - self.division.psi(middle + 2)
                * self.division.psi(middle - 1)
                * self.value(middle + 1)
                * self.value(middle)
            )
            value = numerator / self.division.psi(2)
        else:
            middle = index // 2
            numerator = (
                self.value(middle + 1)
                * self.value(middle - 2)
                * self.division.psi(middle + 1)
                * self.division.psi(middle)
                - self.division.psi(middle + 2)
                * self.division.psi(middle - 1)
                * self.value(middle)
                * self.value(middle - 1)
            )
            value = numerator / (self.delta_x * self.division.psi(2))
        self.cache[index] = value
        return value


def regularized_torsion_jet(
    prime: int, order: int, point: tuple[int, int]
) -> tuple[int, int, int, int]:
    """Return H_n(P), x-chart ratio, and first three local coefficients.

    If psi_n(x(P)+T)=c1*T+c2*T^2+..., the invariant-parameter finite part is

        R_n(P)=3*x(P)^2/(2*y(P)) + 2*y(P)*c2/c1,
        H_n(P)=R_n(P)/n.
    """
    x, y = point
    series = DivisionSeries(prime, x, y, 4).psi(order)
    c0, c1, c2, c3 = series.coefficients
    if c0 != 0 or c1 == 0:
        raise AssertionError("the declared torsion jet is not simple")
    x_ratio = c2 * pow(c1, -1, prime) % prime
    invariant_finite_part = (
        3 * x * x * pow(2 * y, -1, prime) + 2 * y * x_ratio
    ) % prime
    h_value = invariant_finite_part * pow(order % prime, -1, prime) % prime
    return h_value, x_ratio, c1, c3


def logarithmic_derivatives(
    prime: int, point: tuple[int, int], series: Series
) -> tuple[int, int, int]:
    """First three invariant-parameter derivatives of log(series)."""
    x, y = point
    c0, c1, c2, c3 = series.coefficients
    if c0 == 0:
        raise ZeroDivisionError("logarithm of a vanishing series")
    inverse = pow(c0, -1, prime)
    first_numerator = 2 * y * c1 % prime
    second_numerator = (6 * x * x * c1 + 8 * y * y * c2) % prime
    third_numerator = (
        24 * x * y * c1
        + 72 * x * x * y * c2
        + 48 * y * y * y * c3
    ) % prime
    first = first_numerator * inverse % prime
    second = (
        second_numerator * inverse
        - first_numerator * first_numerator * inverse * inverse
    ) % prime
    third = (
        third_numerator * inverse
        - 3 * second_numerator * first_numerator * inverse * inverse
        + 2 * pow(first_numerator * inverse % prime, 3, prime)
    ) % prime
    return first, second, third


def period_shift_coefficients(
    a: int, b: int, r: int, s: int, order: int
) -> tuple[int, int]:
    first = 2 * b * s - a * s - r * b + order * (s * s - r * s)
    second = a * s + r * b + order * r * s
    return first, second


def period_shift_eta_coefficient(
    a: int, b: int, r: int, s: int, order: int, scalar: int
) -> int:
    """Coefficient of the quasiperiod eta after substituting periodic H states."""
    first, second = period_shift_coefficients(a, b, r, s, order)
    target = a + b * scalar
    return (
        s * target
        - first * scalar
        - second * (scalar + 1)
        + (b + s * order) * (r + s * scalar)
    )

