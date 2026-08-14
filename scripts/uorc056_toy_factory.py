#!/usr/bin/env python3
"""Exact toy factory for UORC-056 oriented Kummer roots.

This module is deliberately dependency-free. It constructs ground-truth objects
for small odd prime-order subgroups on short Weierstrass curves over prime fields.
It is not an evaluator for unknown scalars and makes no complexity claim.
Polynomial coefficients are stored from low degree to high degree.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional, Sequence

Point = Optional[tuple[int, int]]
Polynomial = list[int]


class UORCError(ValueError):
    """Raised when a declared toy instance violates the UORC contract."""


def _trim(poly: Sequence[int], p: int) -> Polynomial:
    out = [int(c) % p for c in poly]
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out or [0]


def poly_add(left: Sequence[int], right: Sequence[int], p: int) -> Polynomial:
    size = max(len(left), len(right))
    return _trim([
        ((left[i] if i < len(left) else 0) + (right[i] if i < len(right) else 0)) % p
        for i in range(size)
    ], p)


def poly_sub(left: Sequence[int], right: Sequence[int], p: int) -> Polynomial:
    size = max(len(left), len(right))
    return _trim([
        ((left[i] if i < len(left) else 0) - (right[i] if i < len(right) else 0)) % p
        for i in range(size)
    ], p)


def poly_scale(poly: Sequence[int], scalar: int, p: int) -> Polynomial:
    return _trim([(scalar * c) % p for c in poly], p)


def poly_mul(left: Sequence[int], right: Sequence[int], p: int) -> Polynomial:
    out = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            out[i + j] = (out[i + j] + a * b) % p
    return _trim(out, p)


def poly_eval(poly: Sequence[int], x: int, p: int) -> int:
    acc = 0
    for coefficient in reversed(poly):
        acc = (acc * x + coefficient) % p
    return acc


def poly_divmod(numerator: Sequence[int], denominator: Sequence[int], p: int) -> tuple[Polynomial, Polynomial]:
    num = _trim(numerator, p)
    den = _trim(denominator, p)
    if den == [0]:
        raise ZeroDivisionError("polynomial division by zero")
    if len(num) < len(den):
        return [0], num
    quotient = [0] * (len(num) - len(den) + 1)
    den_lead_inv = pow(den[-1], -1, p)
    while num != [0] and len(num) >= len(den):
        shift = len(num) - len(den)
        factor = num[-1] * den_lead_inv % p
        quotient[shift] = factor
        for i, coefficient in enumerate(den):
            num[i + shift] = (num[i + shift] - factor * coefficient) % p
        num = _trim(num, p)
    return _trim(quotient, p), num


def poly_mod(numerator: Sequence[int], modulus: Sequence[int], p: int) -> Polynomial:
    return poly_divmod(numerator, modulus, p)[1]


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


@dataclass(frozen=True)
class Curve:
    p: int
    a: int
    b: int

    def __post_init__(self) -> None:
        if not is_prime(self.p):
            raise UORCError(f"field modulus p={self.p} is not prime")
        if (4 * self.a**3 + 27 * self.b**2) % self.p == 0:
            raise UORCError("singular short Weierstrass curve")

    def rhs(self, x: int) -> int:
        return (x**3 + self.a * x + self.b) % self.p

    def contains(self, point: Point) -> bool:
        if point is None:
            return True
        x, y = point
        return y * y % self.p == self.rhs(x)

    def neg(self, point: Point) -> Point:
        if point is None:
            return None
        x, y = point
        return x % self.p, (-y) % self.p

    def add(self, left: Point, right: Point) -> Point:
        if left is None:
            return right
        if right is None:
            return left
        if not self.contains(left) or not self.contains(right):
            raise UORCError("point outside curve")
        x1, y1 = left
        x2, y2 = right
        if x1 == x2 and (y1 + y2) % self.p == 0:
            return None
        if left == right:
            if y1 % self.p == 0:
                return None
            slope = (3 * x1 * x1 + self.a) * pow(2 * y1, -1, self.p) % self.p
        else:
            slope = (y2 - y1) * pow(x2 - x1, -1, self.p) % self.p
        x3 = (slope * slope - x1 - x2) % self.p
        y3 = (slope * (x1 - x3) - y1) % self.p
        result = (x3, y3)
        if not self.contains(result):
            raise AssertionError("elliptic-curve addition produced an invalid point")
        return result

    def mul(self, scalar: int, point: Point) -> Point:
        if scalar < 0:
            return self.mul(-scalar, self.neg(point))
        result: Point = None
        addend = point
        k = scalar
        while k:
            if k & 1:
                result = self.add(result, addend)
            addend = self.add(addend, addend)
            k >>= 1
        return result


@dataclass(frozen=True)
class ToyInstance:
    instance_id: str
    curve: Curve
    subgroup_order: int
    generator: tuple[int, int]
    cm_beta: int | None = None
    glv_lambda: int | None = None

    def validate(self) -> None:
        n = self.subgroup_order
        if n <= 2 or n % 2 == 0 or not is_prime(n):
            raise UORCError("subgroup order must be an odd prime")
        if not self.curve.contains(self.generator):
            raise UORCError("declared generator is not on the curve")
        if self.curve.mul(n, self.generator) is not None:
            raise UORCError("declared generator does not have order dividing n")
        if self.cm_beta is not None:
            if self.curve.a % self.curve.p != 0:
                raise UORCError("CM beta metadata is only supported for j=0 toys")
            beta = self.cm_beta % self.curve.p
            if beta == 1 or pow(beta, 3, self.curve.p) != 1:
                raise UORCError("cm_beta must be a nontrivial cube root of unity")
            phi_g = (beta * self.generator[0] % self.curve.p, self.generator[1])
            if not self.curve.contains(phi_g):
                raise UORCError("declared CM image is not on the curve")
            if self.glv_lambda is not None and self.curve.mul(self.glv_lambda, self.generator) != phi_g:
                raise UORCError("declared GLV lambda does not match beta action")


def product_linear_roots(roots: Iterable[int], p: int) -> Polynomial:
    product: Polynomial = [1]
    for root in roots:
        product = poly_mul(product, [(-root) % p, 1], p)
    return product


def lagrange_basis(nodes: Sequence[int], p: int) -> tuple[Polynomial, list[Polynomial]]:
    if len(set(x % p for x in nodes)) != len(nodes):
        raise UORCError("interpolation nodes are not distinct")
    kernel = product_linear_roots(nodes, p)
    basis: list[Polynomial] = []
    for x_i in nodes:
        quotient, remainder = poly_divmod(kernel, [(-x_i) % p, 1], p)
        if remainder != [0]:
            raise AssertionError("linear factor did not divide kernel")
        denominator = poly_eval(quotient, x_i, p)
        basis.append(poly_scale(quotient, pow(denominator, -1, p), p))
    return kernel, basis


def interpolate_from_basis(values: Sequence[int], basis: Sequence[Sequence[int]], p: int) -> Polynomial:
    if len(values) != len(basis):
        raise UORCError("value/basis length mismatch")
    result: Polynomial = [0]
    for value, basis_poly in zip(values, basis):
        result = poly_add(result, poly_scale(basis_poly, value, p), p)
    return _trim(result, p)


def canonical_half_points(instance: ToyInstance) -> list[tuple[int, int]]:
    instance.validate()
    m = (instance.subgroup_order - 1) // 2
    points = [instance.curve.mul(j, instance.generator) for j in range(1, m + 1)]
    if any(point is None for point in points):
        raise AssertionError("nonzero subgroup multiple unexpectedly equals infinity")
    typed = [point for point in points if point is not None]
    if len({point[0] for point in typed}) != m:
        raise UORCError("canonical half does not have distinct x-coordinates")
    return typed


def marked_root_values(instance: ToyInstance, marker: int, half_points: Sequence[tuple[int, int]]) -> list[int]:
    n = instance.subgroup_order
    u = marker % n
    if u == 0:
        raise UORCError("marked generator multiplier must be nonzero modulo n")
    inverse = pow(u, -1, n)
    values: list[int] = []
    for r, (_, y_r) in enumerate(half_points, start=1):
        scalar = r * inverse % n
        values.append((-1 if scalar % 2 else 1) * y_r % instance.curve.p)
    return values


def curve_polynomial(instance: ToyInstance) -> Polynomial:
    return _trim([instance.curve.b, instance.curve.a, 0, 1], instance.curve.p)


def polynomial_digest(poly: Sequence[int]) -> str:
    encoded = json.dumps(list(poly), separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def build_fixture(instance: ToyInstance, include_all_markers: bool = True) -> dict:
    instance.validate()
    p = instance.curve.p
    n = instance.subgroup_order
    half_points = canonical_half_points(instance)
    kernel, basis = lagrange_basis([point[0] for point in half_points], p)
    expected_degree = (n - 1) // 2
    if len(kernel) - 1 != expected_degree:
        raise AssertionError("kernel polynomial has the wrong degree")
    markers = range(1, n) if include_all_markers else (1, n - 1)
    roots: dict[str, dict] = {}
    curve_poly = curve_polynomial(instance)
    for marker in markers:
        values = marked_root_values(instance, marker, half_points)
        root = interpolate_from_basis(values, basis, p)
        residual = poly_mod(poly_sub(poly_mul(root, root, p), curve_poly, p), kernel, p)
        if residual != [0]:
            raise AssertionError(f"square-root congruence failed for marker {marker}")
        marked_generator = instance.curve.mul(marker, instance.generator)
        for k in range(1, n):
            q = instance.curve.mul(k, marked_generator)
            if q is None:
                raise AssertionError("nonzero marked multiple unexpectedly equals infinity")
            ratio = poly_eval(root, q[0], p) * pow(q[1], -1, p) % p
            expected_ratio = p - 1 if k % 2 else 1
            if ratio != expected_ratio:
                raise AssertionError(
                    f"parity contract failed for marker={marker}, k={k}: {ratio} != {expected_ratio}"
                )
        roots[str(marker)] = {
            "marked_generator": list(marked_generator),
            "coefficients_low_to_high": root,
            "values_on_base_half": values,
            "sha256": polynomial_digest(root),
        }
    if include_all_markers:
        if _trim(poly_add(roots["1"]["coefficients_low_to_high"], roots[str(n - 1)]["coefficients_low_to_high"], p), p) != [0]:
            raise AssertionError("G -> -G covariance failed: Y_-G != -Y_G")
    fixture = {
        "schema_version": "1.0",
        "object": "UORC-056 exact toy oriented Kummer root family",
        "status": "ground_truth_only_not_an_evaluator",
        "instance": {
            "id": instance.instance_id,
            "field_prime": p,
            "curve": {"a": instance.curve.a % p, "b": instance.curve.b % p},
            "subgroup_order": n,
            "base_generator": list(instance.generator),
            "cm_beta": instance.cm_beta,
            "glv_lambda": instance.glv_lambda,
        },
        "conventions": {
            "kernel_degree": expected_degree,
            "kernel_roots": "x([j]G), 1 <= j <= (n-1)/2",
            "root": "Y_[u]G(x([k][u]G)) = (-1)^k y([k][u]G), 1 <= k < n",
            "canonical_scalar_representative": "0 <= k < n",
            "polynomial_coefficients": "low_to_high_mod_p",
        },
        "base_half_points": [list(point) for point in half_points],
        "kernel_coefficients_low_to_high": kernel,
        "kernel_sha256": polynomial_digest(kernel),
        "marked_roots": roots,
        "checks": {
            "subgroup_order_prime": True,
            "kernel_degree_exact": True,
            "square_congruence_all_exported_markers": True,
            "parity_ratio_all_nonzero_scalars": True,
            "negated_generator_root_is_global_negative": include_all_markers,
        },
    }
    canonical = json.dumps(fixture, sort_keys=True, separators=(",", ":")).encode("utf-8")
    fixture["fixture_sha256_without_self_hash"] = hashlib.sha256(canonical).hexdigest()
    return fixture


DEFAULT_INSTANCES = (
    ToyInstance("E7-P43-N31", Curve(43, 0, 7), 31, (2, 12), cm_beta=6, glv_lambda=5),
    ToyInstance("E7-P67-N79", Curve(67, 0, 7), 79, (2, 22), cm_beta=29, glv_lambda=23),
    ToyInstance("E7-P79-N67", Curve(79, 0, 7), 67, (1, 18), cm_beta=23, glv_lambda=29),
    ToyInstance("E7-P127-N127", Curve(127, 0, 7), 127, (1, 32), cm_beta=19, glv_lambda=107),
    ToyInstance("E7-P163-N139", Curve(163, 0, 7), 139, (2, 34), cm_beta=58, glv_lambda=96),
)


def write_default_fixtures(output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    manifest_rows = []
    for instance in DEFAULT_INSTANCES:
        fixture = build_fixture(instance, include_all_markers=True)
        path = output_dir / f"{instance.instance_id}.json"
        text = json.dumps(fixture, indent=2, sort_keys=True) + "\n"
        path.write_text(text, encoding="utf-8")
        written.append(path)
        manifest_rows.append({
            "id": instance.instance_id,
            "path": path.name,
            "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "field_prime": instance.curve.p,
            "subgroup_order": instance.subgroup_order,
            "kernel_degree": (instance.subgroup_order - 1) // 2,
        })
    manifest = {"schema_version": "1.0", "generator": "scripts/uorc056_toy_factory.py", "fixtures": manifest_rows}
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    written.append(manifest_path)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("experiments/uorc056/fixtures"))
    parser.add_argument("--check", action="store_true", help="verify fixture files are byte-identical")
    args = parser.parse_args()
    if args.check:
        expected: dict[str, str] = {}
        for instance in DEFAULT_INSTANCES:
            fixture = build_fixture(instance, include_all_markers=True)
            expected[f"{instance.instance_id}.json"] = json.dumps(fixture, indent=2, sort_keys=True) + "\n"
        rows = []
        for instance in DEFAULT_INSTANCES:
            text = expected[f"{instance.instance_id}.json"]
            rows.append({
                "id": instance.instance_id,
                "path": f"{instance.instance_id}.json",
                "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                "field_prime": instance.curve.p,
                "subgroup_order": instance.subgroup_order,
                "kernel_degree": (instance.subgroup_order - 1) // 2,
            })
        expected["manifest.json"] = json.dumps(
            {"schema_version": "1.0", "generator": "scripts/uorc056_toy_factory.py", "fixtures": rows},
            indent=2,
            sort_keys=True,
        ) + "\n"
        failures = [
            name for name, text in expected.items()
            if not (args.output_dir / name).exists() or (args.output_dir / name).read_text(encoding="utf-8") != text
        ]
        if failures:
            raise SystemExit("fixture drift: " + ", ".join(failures))
        print(f"UORC056_FIXTURES_OK count={len(DEFAULT_INSTANCES)}")
        return 0
    print("\n".join(str(path) for path in write_default_fixtures(args.output_dir)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
