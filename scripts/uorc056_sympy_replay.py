#!/usr/bin/env python3
"""Independent SymPy replay for generated UORC-056 toy fixtures.

This verifier does not import producer code. It reconstructs finite-field
elliptic-curve arithmetic, the kernel, every marked root, every half-point and
every parity ratio independently, with SymPy as a second polynomial backend.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

import sympy as sp

Point = Optional[tuple[int, int]]


def ec_neg(point: Point, p: int) -> Point:
    if point is None:
        return None
    return point[0] % p, (-point[1]) % p


def ec_add(left: Point, right: Point, p: int, a: int) -> Point:
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
        slope = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        slope = (y2 - y1) * pow((x2 - x1) % p, -1, p) % p
    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    return x3, y3


def ec_mul(scalar: int, point: Point, p: int, a: int) -> Point:
    if scalar < 0:
        return ec_mul(-scalar, ec_neg(point, p), p, a)
    result: Point = None
    addend = point
    k = scalar
    while k:
        if k & 1:
            result = ec_add(result, addend, p, a)
        addend = ec_add(addend, addend, p, a)
        k >>= 1
    return result


def on_curve(point: Point, p: int, a: int, b: int) -> bool:
    if point is None:
        return True
    x, y = point
    return (y * y - x * x * x - a * x - b) % p == 0


def eval_mod(poly: sp.Poly, value: int, p: int) -> int:
    return int(poly.eval(value)) % p


def replay_fixture(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    instance = data["instance"]
    p = int(instance["field_prime"])
    n = int(instance["subgroup_order"])
    a = int(instance["curve"]["a"])
    b = int(instance["curve"]["b"])
    generator = tuple(map(int, instance["base_generator"]))
    if not on_curve(generator, p, a, b):
        raise AssertionError(f"{path}: generator is off curve")
    if ec_mul(n, generator, p, a) is not None:
        raise AssertionError(f"{path}: declared generator order failed")

    x = sp.symbols("x")
    kernel_coeffs = [int(c) for c in data["kernel_coefficients_low_to_high"]]
    kernel = sp.Poly(sum(c * x**i for i, c in enumerate(kernel_coeffs)), x, modulus=p)
    expected_degree = (n - 1) // 2
    if kernel.degree() != expected_degree:
        raise AssertionError(f"{path}: kernel degree mismatch")

    expected_half = [ec_mul(j, generator, p, a) for j in range(1, expected_degree + 1)]
    if any(point is None for point in expected_half):
        raise AssertionError(f"{path}: infinity in canonical half")
    stored_half = [tuple(map(int, point)) for point in data["base_half_points"]]
    if stored_half != expected_half:
        raise AssertionError(f"{path}: stored half-points are not independently reproduced")
    expected_kernel = sp.Poly(1, x, modulus=p)
    for point in expected_half:
        assert point is not None
        expected_kernel *= sp.Poly(x - point[0], x, modulus=p)
    if kernel.monic() != expected_kernel.monic():
        raise AssertionError(f"{path}: kernel roots mismatch")

    curve_poly = sp.Poly(x**3 + a * x + b, x, modulus=p)
    roots: dict[int, sp.Poly] = {}
    for marker_text, row in data["marked_roots"].items():
        marker = int(marker_text)
        marked_generator = ec_mul(marker, generator, p, a)
        if marked_generator is None:
            raise AssertionError(f"{path}: zero marked generator")
        if list(marked_generator) != [int(v) for v in row["marked_generator"]]:
            raise AssertionError(f"{path}: marked generator mismatch for {marker}")

        coeffs = [int(c) for c in row["coefficients_low_to_high"]]
        root = sp.Poly(sum(c * x**i for i, c in enumerate(coeffs)), x, modulus=p)
        roots[marker] = root
        if root.degree() >= expected_degree:
            raise AssertionError(f"{path}: noncanonical root degree for marker {marker}")
        if (root * root - curve_poly).rem(kernel) != 0:
            raise AssertionError(f"{path}: square congruence failed for marker {marker}")

        values = [int(v) % p for v in row["values_on_base_half"]]
        replayed = [eval_mod(root, point[0], p) for point in stored_half]
        if replayed != values:
            raise AssertionError(f"{path}: interpolation replay failed for marker {marker}")

        for k in range(1, n):
            q = ec_mul(k, marked_generator, p, a)
            if q is None or not on_curve(q, p, a, b):
                raise AssertionError(f"{path}: invalid multiple marker={marker}, k={k}")
            ratio = eval_mod(root, q[0], p) * pow(q[1], -1, p) % p
            expected = p - 1 if k & 1 else 1
            if ratio != expected:
                raise AssertionError(
                    f"{path}: parity ratio failed marker={marker}, k={k}: {ratio} != {expected}"
                )

    if set(roots) != set(range(1, n)):
        raise AssertionError(f"{path}: incomplete marked-root family")
    if (roots[1] + roots[n - 1]).rem(kernel) != 0:
        raise AssertionError(f"{path}: Y_-G != -Y_G")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture_dir", nargs="?", type=Path, default=Path("experiments/uorc056/fixtures"))
    args = parser.parse_args()
    paths = sorted(path for path in args.fixture_dir.glob("*.json") if path.name != "manifest.json")
    if not paths:
        raise SystemExit(f"no fixtures found in {args.fixture_dir}")
    for path in paths:
        replay_fixture(path)
    print(f"UORC056_SYMPY_REPLAY_OK count={len(paths)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
