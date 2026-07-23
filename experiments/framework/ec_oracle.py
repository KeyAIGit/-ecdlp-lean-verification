#!/usr/bin/env python3
"""Small independent affine-curve oracle used only to validate claimed outputs.

This module deliberately exposes no discrete-log search. A candidate may submit
a scalar; the oracle checks that scalar against independently implemented curve
arithmetic. It is suitable for deterministic toy fixtures, not performance work.
"""
from __future__ import annotations

from dataclasses import dataclass

Point = tuple[int, int] | None
MAX_TOY_FIELD = (1 << 32) - 1


def is_prime(value: int) -> bool:
    """Deterministic trial-division primality for the v1 toy-field range."""
    if value < 2:
        return False
    for small in (2, 3, 5):
        if value == small:
            return True
        if value % small == 0:
            return False
    divisor = 7
    step = 4
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += step
        step = 6 - step
    return True


def prime_divisors(value: int) -> set[int]:
    """Return the distinct prime divisors of a positive toy-size integer."""
    if value < 1:
        raise ValueError("value must be positive")
    factors: set[int] = set()
    remainder = value
    divisor = 2
    while divisor * divisor <= remainder:
        if remainder % divisor == 0:
            factors.add(divisor)
            while remainder % divisor == 0:
                remainder //= divisor
        divisor = 3 if divisor == 2 else divisor + 2
    if remainder > 1:
        factors.add(remainder)
    return factors


@dataclass(frozen=True)
class Curve:
    p: int
    a: int
    b: int

    def __post_init__(self) -> None:
        if self.p > MAX_TOY_FIELD:
            raise ValueError("v1 oracle is restricted to at most 32-bit toy fields")
        if self.p <= 3 or not is_prime(self.p):
            raise ValueError("the oracle requires a prime field with p > 3")
        if (4 * pow(self.a, 3, self.p) + 27 * pow(self.b, 2, self.p)) % self.p == 0:
            raise ValueError("singular curve")

    def is_on_curve(self, point: Point) -> bool:
        if point is None:
            return True
        x, y = point
        if not (0 <= x < self.p and 0 <= y < self.p):
            return False
        return (y * y - (x * x * x + self.a * x + self.b)) % self.p == 0

    def negate(self, point: Point) -> Point:
        if point is None:
            return None
        return point[0], (-point[1]) % self.p

    def add(self, left: Point, right: Point) -> Point:
        if not self.is_on_curve(left) or not self.is_on_curve(right):
            raise ValueError("point is not on the curve")
        if left is None:
            return right
        if right is None:
            return left

        x1, y1 = left
        x2, y2 = right
        if x1 == x2 and (y1 + y2) % self.p == 0:
            return None
        if left == right:
            numerator = (3 * x1 * x1 + self.a) % self.p
            denominator = (2 * y1) % self.p
        else:
            numerator = (y2 - y1) % self.p
            denominator = (x2 - x1) % self.p
        if denominator == 0:
            return None

        slope = numerator * pow(denominator, -1, self.p) % self.p
        x3 = (slope * slope - x1 - x2) % self.p
        y3 = (slope * (x1 - x3) - y1) % self.p
        result = (x3, y3)
        if not self.is_on_curve(result):
            raise AssertionError("oracle arithmetic produced an off-curve point")
        return result

    def scalar_mul(self, scalar: int, point: Point) -> Point:
        if not isinstance(scalar, int):
            raise TypeError("scalar must be an integer")
        if not self.is_on_curve(point):
            raise ValueError("point is not on the curve")
        if scalar < 0:
            return self.scalar_mul(-scalar, self.negate(point))

        result: Point = None
        addend = point
        remaining = scalar
        while remaining:
            if remaining & 1:
                result = self.add(result, addend)
            addend = self.add(addend, addend)
            remaining >>= 1
        return result


def parse_point(value: object, name: str) -> Point:
    if value is None:
        return None
    if (
        not isinstance(value, list)
        or len(value) != 2
        or any(not isinstance(coordinate, int) for coordinate in value)
    ):
        raise ValueError(f"{name} must be null or a two-integer array")
    return value[0], value[1]


def validate_scalar(curve: Curve, base: Point, target: Point, scalar: int) -> bool:
    """Return whether [scalar]base equals target."""
    return curve.scalar_mul(scalar, base) == target
