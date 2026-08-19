#!/usr/bin/env python3
"""Exact arithmetic core for UORC-056 C52.

The module uses only fixed public toy curves and public secp256k1 constants.
It accepts no external target, hidden scalar, private key, wallet, or branch
advice.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

Point = Optional[tuple[int, int]]

SECP_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
SECP_G = (
    55066263022277343669578718895168534326250603453777594175500187360389116729240,
    32670510020758816978083085130507043184471273380659243275938904335757337482424,
)

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
ALL_CURVES = FROZEN + HELD_OUT


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
    d = 3
    while d * d <= value:
        if value % d == 0:
            return False
        d += 2
    return True


@dataclass(frozen=True)
class Curve:
    p: int
    a: int = 0
    b: int = 7

    def on_curve(self, point: Point) -> bool:
        if point is None:
            return True
        x, y = point
        return (y * y - (x * x * x + self.a * x + self.b)) % self.p == 0

    def neg(self, point: Point) -> Point:
        return None if point is None else (point[0], (-point[1]) % self.p)

    def add(self, left: Point, right: Point) -> Point:
        if left is None:
            return right
        if right is None:
            return left
        p = self.p
        x1, y1 = left
        x2, y2 = right
        if x1 == x2 and (y1 + y2) % p == 0:
            return None
        if left == right:
            if y1 == 0:
                return None
            slope = (3 * x1 * x1 + self.a) * pow(2 * y1, -1, p) % p
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


def point_count(curve: Curve) -> int:
    total = 1
    for x in range(curve.p):
        rhs = (x * x * x + curve.a * x + curve.b) % curve.p
        symbol = quadratic_character(rhs, curve.p)
        total += 1 if symbol == 0 else 2 if symbol == 1 else 0
    return total


@dataclass(frozen=True)
class Jet:
    """Value plus partial derivatives with respect to x, a and b."""

    value: int
    dx: int
    da: int
    db: int
    p: int

    @classmethod
    def constant(cls, value: int, p: int) -> "Jet":
        return cls(value % p, 0, 0, 0, p)

    def _coerce(self, other: int | "Jet") -> "Jet":
        if isinstance(other, Jet):
            if other.p != self.p:
                raise ValueError("incompatible jets")
            return other
        return Jet.constant(int(other), self.p)

    def __add__(self, other):
        other = self._coerce(other)
        p = self.p
        return Jet(
            (self.value + other.value) % p,
            (self.dx + other.dx) % p,
            (self.da + other.da) % p,
            (self.db + other.db) % p,
            p,
        )

    __radd__ = __add__

    def __neg__(self):
        p = self.p
        return Jet(-self.value % p, -self.dx % p, -self.da % p, -self.db % p, p)

    def __sub__(self, other):
        return self + (-self._coerce(other))

    def __rsub__(self, other):
        return self._coerce(other) - self

    def __mul__(self, other):
        other = self._coerce(other)
        p = self.p
        return Jet(
            self.value * other.value % p,
            (self.dx * other.value + self.value * other.dx) % p,
            (self.da * other.value + self.value * other.da) % p,
            (self.db * other.value + self.value * other.db) % p,
            p,
        )

    __rmul__ = __mul__

    def inverse(self):
        if self.value == 0:
            raise ZeroDivisionError("jet is not a unit")
        p = self.p
        inverse = pow(self.value, -1, p)
        scale = -inverse * inverse % p
        return Jet(
            inverse,
            scale * self.dx % p,
            scale * self.da % p,
            scale * self.db % p,
            p,
        )

    def __truediv__(self, other):
        return self * self._coerce(other).inverse()

    def __rtruediv__(self, other):
        return self._coerce(other) * self.inverse()

    def __pow__(self, exponent: int):
        if exponent < 0:
            return self.inverse() ** (-exponent)
        result = Jet.constant(1, self.p)
        base = self
        while exponent:
            if exponent & 1:
                result = result * base
            base = base * base
            exponent >>= 1
        return result


class DivisionJet:
    """Division-polynomial recurrence with first partial derivatives."""

    def __init__(self, curve: Curve, point: tuple[int, int]):
        p = curve.p
        x0, y0 = point
        if y0 == 0:
            raise ZeroDivisionError("2-torsion chart is unsupported")
        self.x = Jet(x0, 1, 0, 0, p)
        self.a = Jet(curve.a, 0, 1, 0, p)
        self.b = Jet(curve.b, 0, 0, 1, p)
        inverse_2y = pow(2 * y0, -1, p)
        self.y = Jet(
            y0,
            (3 * x0 * x0 + curve.a) * inverse_2y % p,
            x0 * inverse_2y % p,
            inverse_2y,
            p,
        )
        self.inverse_2y = (2 * self.y).inverse()
        x, a, b, y = self.x, self.a, self.b, self.y
        self.cache: dict[int, Jet] = {
            0: Jet.constant(0, p),
            1: Jet.constant(1, p),
            2: 2 * y,
        }
        self.cache[3] = 3 * x**4 + 6 * a * x**2 + 12 * b * x - a**2
        self.cache[4] = 4 * y * (
            x**6 + 5 * a * x**4 + 20 * b * x**3
            - 5 * a**2 * x**2 - 4 * a * b * x - 8 * b**2 - a**3
        )

    def psi(self, index: int) -> Jet:
        if index < 0:
            return -self.psi(-index)
        if index in self.cache:
            return self.cache[index]
        if index & 1:
            m = (index - 1) // 2
            value = (
                self.psi(m + 2) * self.psi(m) ** 3
                - self.psi(m - 1) * self.psi(m + 1) ** 3
            )
        else:
            m = index // 2
            value = self.psi(m) * self.inverse_2y * (
                self.psi(m + 2) * self.psi(m - 1) ** 2
                - self.psi(m - 2) * self.psi(m + 1) ** 2
            )
        self.cache[index] = value
        return value


def torsion_lift_basis(
    curve: Curve,
    order: int,
    point: tuple[int, int],
) -> tuple[tuple[int, int], tuple[int, int], Jet]:
    """Basis lift tangents for (dot a,dot b)=(1,0) and (0,1)."""
    p = curve.p
    jet = DivisionJet(curve, point).psi(order)
    if jet.value != 0:
        raise AssertionError("point is not n-torsion")
    if jet.dx == 0:
        raise AssertionError("inseparable torsion root")
    inverse_dx = pow(jet.dx, -1, p)
    x, y = point
    inverse_2y = pow(2 * y, -1, p)
    ua = -jet.da * inverse_dx % p
    ub = -jet.db * inverse_dx % p
    va = ((3 * x * x + curve.a) * ua + x) * inverse_2y % p
    vb = ((3 * x * x + curve.a) * ub + 1) * inverse_2y % p
    return (ua, va), (ub, vb), jet


def torsion_lift_tangent(
    curve: Curve,
    order: int,
    point: tuple[int, int],
    da: int,
    db: int,
) -> tuple[int, int]:
    tangent_a, tangent_b, _ = torsion_lift_basis(curve, order, point)
    p = curve.p
    return (
        (da * tangent_a[0] + db * tangent_b[0]) % p,
        (da * tangent_a[1] + db * tangent_b[1]) % p,
    )


@dataclass(frozen=True)
class Dual:
    value: int
    epsilon: int
    p: int

    @classmethod
    def constant(cls, value: int, p: int) -> "Dual":
        return cls(value % p, 0, p)

    def _coerce(self, other: int | "Dual") -> "Dual":
        if isinstance(other, Dual):
            if other.p != self.p:
                raise ValueError("incompatible duals")
            return other
        return Dual.constant(int(other), self.p)

    def __add__(self, other):
        other = self._coerce(other)
        return Dual(
            (self.value + other.value) % self.p,
            (self.epsilon + other.epsilon) % self.p,
            self.p,
        )

    __radd__ = __add__

    def __neg__(self):
        return Dual(-self.value % self.p, -self.epsilon % self.p, self.p)

    def __sub__(self, other):
        return self + (-self._coerce(other))

    def __rsub__(self, other):
        return self._coerce(other) - self

    def __mul__(self, other):
        other = self._coerce(other)
        return Dual(
            self.value * other.value % self.p,
            (self.value * other.epsilon + self.epsilon * other.value) % self.p,
            self.p,
        )

    __rmul__ = __mul__

    def inverse(self):
        if self.value == 0:
            raise ZeroDivisionError("dual is not a unit")
        inverse = pow(self.value, -1, self.p)
        return Dual(inverse, -self.epsilon * inverse * inverse % self.p, self.p)

    def __truediv__(self, other):
        return self * self._coerce(other).inverse()

    def __rtruediv__(self, other):
        return self._coerce(other) * self.inverse()


DualPoint = Optional[tuple[Dual, Dual]]


class DualCurve:
    def __init__(self, curve: Curve, da: int = 0, db: int = 0):
        self.p = curve.p
        self.a = Dual(curve.a, da, curve.p)
        self.b = Dual(curve.b, db, curve.p)

    def neg(self, point: DualPoint) -> DualPoint:
        return None if point is None else (point[0], -point[1])

    def add(self, left: DualPoint, right: DualPoint) -> DualPoint:
        if left is None:
            return right
        if right is None:
            return left
        x1, y1 = left
        x2, y2 = right
        if x1.value == x2.value and (y1.value + y2.value) % self.p == 0:
            return None
        if left == right:
            slope = (3 * x1 * x1 + self.a) / (2 * y1)
        else:
            slope = (y2 - y1) / (x2 - x1)
        x3 = slope * slope - x1 - x2
        y3 = slope * (x1 - x3) - y1
        return x3, y3

    def mul(self, scalar: int, point: DualPoint, order: int | None = None) -> DualPoint:
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


def lift_point(
    curve: Curve,
    order: int,
    point: tuple[int, int],
    da: int,
    db: int,
) -> tuple[Dual, Dual]:
    dx, dy = torsion_lift_tangent(curve, order, point, da, db)
    return Dual(point[0], dx, curve.p), Dual(point[1], dy, curve.p)


def vertical_tangent_point(
    curve: Curve,
    point: tuple[int, int],
    invariant_scalar: int,
) -> tuple[Dual, Dual]:
    """A tangent on the fixed curve with dx/(2y)=invariant_scalar."""
    p = curve.p
    x, y = point
    dx = 2 * y * invariant_scalar % p
    dy = (3 * x * x + curve.a) * invariant_scalar % p
    return Dual(x, dx, p), Dual(y, dy, p)


def invariant_tangent_scalar(point: tuple[Dual, Dual]) -> int:
    x, y = point
    return x.epsilon * pow(2 * y.value, -1, x.p) % x.p


def interpolation_polynomial(xs: list[int], ys: list[int], p: int) -> list[int]:
    out = [0] * len(xs)
    for i, (xi, yi) in enumerate(zip(xs, ys)):
        basis = [1]
        denominator = 1
        for j, xj in enumerate(xs):
            if i == j:
                continue
            next_basis = [0] * (len(basis) + 1)
            for degree, coefficient in enumerate(basis):
                next_basis[degree] = (next_basis[degree] - coefficient * xj) % p
                next_basis[degree + 1] = (next_basis[degree + 1] + coefficient) % p
            basis = next_basis
            denominator = denominator * (xi - xj) % p
        scale = yi * pow(denominator, -1, p) % p
        for degree, coefficient in enumerate(basis):
            out[degree] = (out[degree] + scale * coefficient) % p
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out


def polynomial_stats(poly: list[int]) -> dict[str, int | bool]:
    nonzero = sum(value != 0 for value in poly)
    return {
        "degree": len(poly) - 1,
        "coefficients": len(poly),
        "nonzero": nonzero,
        "zeros": len(poly) - nonzero,
        "dense": nonzero == len(poly),
    }
