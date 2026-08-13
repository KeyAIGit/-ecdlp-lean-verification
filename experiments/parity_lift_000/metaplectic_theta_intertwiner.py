#!/usr/bin/env python3
"""Exact toy-only characteristic-root and Heisenberg-minor replay.

This script accepts only predeclared frozen j=0 toy subgroups. It constructs
canonical square roots of the three nontrivial theta-characteristic functions
in F_(p^3), descends their C3 Fourier components cubically to F_p, and checks
natural affine/multiplicative binary readouts. It accepts no external point,
key, wallet, or production-sized target.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from typing import Optional

import numpy as np

Point = Optional[tuple[int, int]]
B = 7
CASES = {
    547: (547, 547, (2, 62)),
    967: (907, 967, (2, 165)),
    1093: (1051, 1093, (3, 385)),
    1249: (1303, 1249, (1, 201)),
    367: (2671, 367, (83, 2009)),
    397: (2851, 397, (2276, 1015)),
    3469: (3571, 3469, (4, 1706)),
    4021: (3931, 4021, (4, 1427)),
}


def quadratic_character(value: int, p: int) -> int:
    value %= p
    if value == 0:
        return 0
    return 1 if pow(value, (p - 1) // 2, p) == 1 else -1


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
        slope = 3 * x1 * x1 * pow(2 * y1, -1, p) % p
    else:
        slope = (y2 - y1) * pow((x2 - x1) % p, -1, p) % p
    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    return x3, y3


def subgroup_orbit(generator: tuple[int, int], order: int, p: int) -> list[Point]:
    points: list[Point] = [None] * order
    point: Point = None
    for scalar in range(1, order):
        point = ec_add(point, generator, p)
        points[scalar] = point
    if ec_add(point, generator, p) is not None:
        raise AssertionError("declared subgroup order failed")
    if len(set(points)) != order:
        raise AssertionError("early subgroup collision")
    return points


def primitive_cube_root(p: int) -> int:
    if (p - 1) % 3:
        raise AssertionError("field lacks a primitive cube root")
    for seed in range(2, p):
        beta = pow(seed, (p - 1) // 3, p)
        if beta != 1 and pow(beta, 3, p) == 1:
            return beta
    raise AssertionError("primitive cube root not found")


@dataclass(frozen=True)
class Fp3:
    """F_p[u]/(u^3+B), used only when u^3+B is irreducible."""

    a: int
    b: int
    c: int
    p: int

    def _coerce(self, other: object) -> "Fp3":
        if isinstance(other, Fp3):
            if other.p != self.p:
                raise ValueError("field mismatch")
            return other
        if isinstance(other, int):
            return Fp3(other % self.p, 0, 0, self.p)
        return NotImplemented

    def __add__(self, other: object) -> "Fp3":
        rhs = self._coerce(other)
        if rhs is NotImplemented:
            return NotImplemented
        return Fp3((self.a + rhs.a) % self.p,
                   (self.b + rhs.b) % self.p,
                   (self.c + rhs.c) % self.p,
                   self.p)

    __radd__ = __add__

    def __neg__(self) -> "Fp3":
        return Fp3(-self.a % self.p, -self.b % self.p, -self.c % self.p, self.p)

    def __sub__(self, other: object) -> "Fp3":
        rhs = self._coerce(other)
        if rhs is NotImplemented:
            return NotImplemented
        return self + (-rhs)

    def __rsub__(self, other: object) -> "Fp3":
        return (-self) + other

    def __mul__(self, other: object) -> "Fp3":
        rhs = self._coerce(other)
        if rhs is NotImplemented:
            return NotImplemented
        p = self.p
        a0, a1, a2 = self.a, self.b, self.c
        b0, b1, b2 = rhs.a, rhs.b, rhs.c
        return Fp3(
            (a0 * b0 - B * (a1 * b2 + a2 * b1)) % p,
            (a0 * b1 + a1 * b0 - B * a2 * b2) % p,
            (a0 * b2 + a1 * b1 + a2 * b0) % p,
            p,
        )

    __rmul__ = __mul__

    def __pow__(self, exponent: int) -> "Fp3":
        if exponent < 0:
            return self.inverse() ** (-exponent)
        out = Fp3(1, 0, 0, self.p)
        base = self
        while exponent:
            if exponent & 1:
                out = out * base
            base = base * base
            exponent >>= 1
        return out

    def inverse(self) -> "Fp3":
        if self == Fp3(0, 0, 0, self.p):
            raise ZeroDivisionError
        return self ** (self.p**3 - 2)

    def __truediv__(self, other: object) -> "Fp3":
        rhs = self._coerce(other)
        if rhs is NotImplemented:
            return NotImplemented
        return self * rhs.inverse()

    def is_base_field(self) -> bool:
        return self.b % self.p == 0 and self.c % self.p == 0

    def base_value(self) -> int:
        if not self.is_base_field():
            raise AssertionError(f"not in base field: {self}")
        return self.a % self.p


def characteristic_features(x: int, p: int, beta: int) -> dict[str, object]:
    q = p**3
    if q % 4 != 3:
        raise AssertionError("canonical square-root exponent requires q=3 mod 4")
    alpha = Fp3(0, 1, 0, p)
    alphas = [alpha, beta * alpha, (beta * beta % p) * alpha]
    exponent = (q + 1) // 4
    roots: list[Fp3] = []
    for alpha_j in alphas:
        value = Fp3(x, 0, 0, p) - alpha_j
        root = value**exponent
        if root * root != value:
            raise AssertionError("canonical characteristic root failed")
        roots.append(root)

    theta: list[Fp3] = []
    for weight in range(3):
        component = Fp3(0, 0, 0, p)
        for j, root in enumerate(roots):
            component += pow(beta, weight * j, p) * root
        theta.append(component)

    cubes = [component**3 for component in theta]
    if not all(value.is_base_field() for value in cubes):
        raise AssertionError("cubic Fourier descent failed")
    product = theta[0] * theta[1] * theta[2]
    vandermonde = (roots[0] - roots[1]) * (roots[1] - roots[2]) * (roots[2] - roots[0])
    if not product.is_base_field() or not vandermonde.is_base_field():
        raise AssertionError("base-field resolvent descent failed")

    a_values = [value.base_value() for value in cubes]
    d_value = vandermonde.base_value()
    expected = (-3 * (beta - beta * beta) * d_value) % p
    if (a_values[1] - a_values[2]) % p != expected:
        raise AssertionError("anti-Fourier/Vandermonde identity failed")

    return {
        "roots": roots,
        "theta": theta,
        "A0": a_values[0],
        "A1": a_values[1],
        "A2": a_values[2],
        "B": product.base_value(),
        "D": d_value,
    }


def build_case(p: int, n: int, generator: tuple[int, int]):
    points = subgroup_orbit(generator, n, p)
    beta = primitive_cube_root(p)
    scalar_of = {point: scalar for scalar, point in enumerate(points)}
    phi_g = (beta * generator[0] % p, generator[1])
    lam = scalar_of[phi_g]
    lam2 = lam * lam % n
    if (1 + lam + lam2) % n:
        raise AssertionError("invalid GLV eigenvalue")
    carry: list[Optional[int]] = [None] * n
    for scalar in range(1, n):
        total = scalar + lam * scalar % n + lam2 * scalar % n
        if total not in (n, 2 * n):
            raise AssertionError("invalid GLV carry")
        carry[scalar] = 1 if total == 2 * n else -1
    return points, beta, lam, carry


def quotient_data(p: int, n: int, generator: tuple[int, int]):
    points, beta, lam, carry = build_case(p, n, generator)
    lam2 = lam * lam % n
    visited: set[int] = set()
    rows: list[tuple[int, int]] = []
    for scalar in range(1, n):
        if scalar in visited:
            continue
        positive = {scalar, lam * scalar % n, lam2 * scalar % n}
        orbit6 = positive | {n - member for member in positive}
        if len(orbit6) != 6:
            raise AssertionError("non-free C6 orbit")
        visited.update(orbit6)
        representative = min(positive)
        point = points[representative]
        if point is None:
            raise AssertionError("unexpected infinity")
        x, y = point
        target = int(carry[representative]) * quadratic_character(y, p)
        z = pow(x, 3, p)
        for member in orbit6:
            xm, ym = points[member]
            if pow(xm, 3, p) != z:
                raise AssertionError("quotient coordinate mismatch")
            if int(carry[member]) * quadratic_character(ym, p) != target:
                raise AssertionError("quotient label mismatch")
        rows.append((representative, target))
    if len(rows) != (n - 1) // 6:
        raise AssertionError("wrong quotient size")
    return points, beta, lam, carry, rows


def legendre_table(p: int) -> np.ndarray:
    out = np.zeros(p, dtype=np.int8)
    for value in range(1, p):
        out[value] = 1 if pow(value, (p - 1) // 2, p) == 1 else -1
    return out


def affine_pencil_screen(
    p: int,
    values: dict[str, np.ndarray],
    targets: dict[str, np.ndarray],
) -> tuple[int, list[dict], dict[str, float]]:
    names = list(values)
    characters = legendre_table(p)
    coefficients = np.arange(p, dtype=np.int64)[:, None]
    formulas = 0
    exact: list[dict] = []
    best = {name: 0.0 for name in targets}
    for left_index in range(len(names)):
        for right_index in range(left_index, len(names)):
            left_name = names[left_index]
            right_name = names[right_index]
            evaluated = (
                values[left_name][None, :]
                + coefficients * values[right_name][None, :]
            ) % p
            signs = characters[evaluated]
            for target_name, target in targets.items():
                positive = (signs == target[None, :]).sum(axis=1)
                negative = ((-signs) == target[None, :]).sum(axis=1)
                formulas += 2 * p
                best[target_name] = max(
                    best[target_name],
                    float(positive.max() / len(target)),
                    float(negative.max() / len(target)),
                )
                for coefficient in np.nonzero(positive == len(target))[0]:
                    exact.append({
                        "target": target_name,
                        "left": left_name,
                        "right": right_name,
                        "coefficient": int(coefficient),
                        "global_sign": 1,
                    })
                for coefficient in np.nonzero(negative == len(target))[0]:
                    exact.append({
                        "target": target_name,
                        "left": left_name,
                        "right": right_name,
                        "coefficient": int(coefficient),
                        "global_sign": -1,
                    })
    return formulas, exact, best


def screen_unshifted(p: int, n: int, generator: tuple[int, int]) -> dict:
    points, beta, _lam, _carry, rows = quotient_data(p, n, generator)
    feature_names = ["A0", "A1", "A2", "B", "D", "1"]
    values = {name: [] for name in feature_names}
    targets: list[int] = []
    cache: dict[int, dict[str, object]] = {}
    for scalar, target in rows:
        point = points[scalar]
        if point is None:
            raise AssertionError
        x, _y = point
        if x not in cache:
            cache[x] = characteristic_features(x, p, beta)
        features = cache[x]
        for name in feature_names[:-1]:
            values[name].append(int(features[name]))
        values["1"].append(1)
        targets.append(target)
    value_arrays = {name: np.array(data, dtype=np.int64) for name, data in values.items()}
    target_arrays = {"h": np.array(targets, dtype=np.int8)}
    formulas, exact, best = affine_pencil_screen(p, value_arrays, target_arrays)
    return {
        "p": p,
        "n": n,
        "quotient_points": len(rows),
        "nominal_formula_instances": formulas,
        "exact_decoders": exact,
        "best_accuracy": best["h"],
    }


def screen_heisenberg(p: int, n: int, generator: tuple[int, int]) -> dict:
    points, beta, _lam, carry = build_case(p, n, generator)
    names = ["N01", "N02", "N12", "1"]
    values: dict[str, list[int]] = {name: [] for name in names}
    targets: dict[str, list[int]] = {"g": [], "h": [], "edge": []}
    cache: dict[int, dict[str, object]] = {}
    exceptions: list[dict] = []
    zero_counts = {name: 0 for name in names[:-1]}

    for scalar in range(1, n):
        next_scalar = (scalar + 1) % n
        if next_scalar == 0 or points[next_scalar] is None:
            exceptions.append({"scalar": scalar, "reason": "QplusG=O"})
            continue
        point = points[scalar]
        next_point = points[next_scalar]
        if point is None or next_point is None:
            raise AssertionError
        x, y = point
        x_next, _y_next = next_point
        difference = (x_next - x) % p
        if difference == 0:
            exceptions.append({"scalar": scalar, "reason": "x_equal"})
            continue
        if x not in cache:
            cache[x] = characteristic_features(x, p, beta)
        if x_next not in cache:
            cache[x_next] = characteristic_features(x_next, p, beta)
        theta = cache[x]["theta"]
        theta_next = cache[x_next]["theta"]
        for a, b, name in ((0, 1, "N01"), (0, 2, "N02"), (1, 2, "N12")):
            minor = theta[a] * theta_next[b] - theta[b] * theta_next[a]
            descended = (minor / Fp3(difference, 0, 0, p)) ** 3
            value = descended.base_value()
            values[name].append(value)
            zero_counts[name] += int(value == 0)
        values["1"].append(1)
        targets["g"].append(int(carry[scalar]))
        targets["h"].append(int(carry[scalar]) * quadratic_character(y, p))
        targets["edge"].append(int(carry[scalar]) * int(carry[next_scalar]))

    if len(exceptions) != 2:
        raise AssertionError(f"expected two public exceptions, got {exceptions}")
    if any(zero_counts.values()):
        raise AssertionError(f"unexpected zero minor: {zero_counts}")

    value_arrays = {name: np.array(data, dtype=np.int64) for name, data in values.items()}
    target_arrays = {name: np.array(data, dtype=np.int8) for name, data in targets.items()}
    formulas, exact, best = affine_pencil_screen(p, value_arrays, target_arrays)

    characters = legendre_table(p)
    multiplicative_exact: list[dict] = []
    for mask in range(1, 1 << 3):
        evaluated = np.ones(len(values["1"]), dtype=np.int64)
        subset: list[str] = []
        for index, name in enumerate(names[:-1]):
            if (mask >> index) & 1:
                evaluated = evaluated * value_arrays[name] % p
                subset.append(name)
        signs = characters[evaluated]
        for target_name, target in target_arrays.items():
            for global_sign in (1, -1):
                if np.all(global_sign * signs == target):
                    multiplicative_exact.append({
                        "target": target_name,
                        "features": subset,
                        "global_sign": global_sign,
                    })

    return {
        "p": p,
        "n": n,
        "screened_points": len(values["1"]),
        "public_exceptions": exceptions,
        "feature_zero_counts": zero_counts,
        "nominal_formula_instances": formulas,
        "exact_decoders": exact,
        "multiplicative_subset_exact_decoders": multiplicative_exact,
        "best_accuracy": best,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--orders",
        nargs="*",
        type=int,
        default=list(CASES),
        help="predeclared subgroup orders to replay",
    )
    parser.add_argument("--out")
    args = parser.parse_args()
    unknown = sorted(set(args.orders) - set(CASES))
    if unknown:
        raise SystemExit(f"orders are not in the frozen corpus: {unknown}")

    unshifted = []
    heisenberg = []
    for order in args.orders:
        case = CASES[order]
        unshifted.append(screen_unshifted(*case))
        heisenberg.append(screen_heisenberg(*case))

    result = {
        "schema_version": 1,
        "scope": (
            "toy-only exact characteristic-root and Heisenberg-minor screen; "
            "no external target and no production-sized claim"
        ),
        "unshifted_resolvent": {
            "features": ["A0", "A1", "A2", "B", "D", "1"],
            "identity": "A1-A2=-3*(beta-beta^2)*D",
            "cases": unshifted,
            "aggregate_nominal_formula_instances": sum(
                row["nominal_formula_instances"] for row in unshifted
            ),
            "aggregate_exact_decoders": sum(
                len(row["exact_decoders"]) for row in unshifted
            ),
        },
        "generator_sensitive_heisenberg_minor": {
            "features": ["N01", "N02", "N12", "1"],
            "targets": ["g", "h", "edge"],
            "cases": heisenberg,
            "aggregate_nominal_formula_instances": sum(
                row["nominal_formula_instances"] for row in heisenberg
            ),
            "aggregate_exact_decoders": sum(
                len(row["exact_decoders"]) for row in heisenberg
            ),
            "aggregate_multiplicative_subset_exact_decoders": sum(
                len(row["multiplicative_subset_exact_decoders"]) for row in heisenberg
            ),
        },
        "claim_boundary": (
            "No exact binary-orientation or scalar-recovery construction was obtained. "
            "Finite toy screens are not a secp256k1 impossibility theorem."
        ),
    }
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
