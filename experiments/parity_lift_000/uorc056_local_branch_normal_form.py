#!/usr/bin/env python3
"""Exact C30 replay for local quadratic-branch certificates in UORC-056.

Every regular rational expression in public branch-even data and one branch Y
of Y^2=F reduces to E+O*Y.  The replay checks the rank-two compiler, unit-gauge
recovery through K_H', singular branch collisions, and a declared four-atom
kernel-derivative character screen on frozen toy curves.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Sequence

Point = Optional[tuple[int, int]]
Vector = tuple[int, ...]
PROFILE_ID = "UORC-056-LOCAL-BRANCH-NORMAL-FORM-C30"
DEFAULT_OUTPUT = Path("/tmp/uorc056_local_branch_normal_form_result.json")


def stable_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def payload_digest(payload: dict[str, Any]) -> str:
    body = dict(payload)
    body.pop("digest", None)
    raw = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class Curve:
    p: int
    a: int
    b: int

    def rhs(self, x: int) -> int:
        return (x**3 + self.a * x + self.b) % self.p

    def add(self, P: Point, Q: Point) -> Point:
        if P is None:
            return Q
        if Q is None:
            return P
        p = self.p
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2 and (y1 + y2) % p == 0:
            return None
        if P == Q:
            if y1 == 0:
                return None
            slope = (3 * x1 * x1 + self.a) * pow(2 * y1, -1, p) % p
        else:
            slope = (y2 - y1) * pow(x2 - x1, -1, p) % p
        x3 = (slope * slope - x1 - x2) % p
        y3 = (slope * (x1 - x3) - y1) % p
        return x3, y3

    def mul(self, k: int, P: Point) -> Point:
        if k < 0:
            return self.mul(-k, None if P is None else (P[0], -P[1] % self.p))
        out: Point = None
        addend = P
        while k:
            if k & 1:
                out = self.add(out, addend)
            addend = self.add(addend, addend)
            k >>= 1
        return out


@dataclass(frozen=True)
class Instance:
    name: str
    curve: Curve
    n: int
    G: tuple[int, int]
    beta: int
    lam: int


INSTANCES = (
    Instance("E7-P43-N31", Curve(43, 0, 7), 31, (2, 12), 6, 5),
    Instance("E7-P67-N79", Curve(67, 0, 7), 79, (2, 22), 29, 23),
    Instance("E7-P79-N67", Curve(79, 0, 7), 67, (1, 18), 23, 29),
    Instance("E7-P127-N127", Curve(127, 0, 7), 127, (1, 32), 19, 107),
    Instance("E7-P163-N139", Curve(163, 0, 7), 139, (2, 34), 58, 96),
)


def poly_trim(poly: Sequence[int], p: int) -> list[int]:
    out = [int(c) % p for c in poly]
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out or [0]


def poly_mul(a: Sequence[int], b: Sequence[int], p: int) -> list[int]:
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] = (out[i + j] + x * y) % p
    return poly_trim(out, p)


def poly_eval(poly: Sequence[int], x: int, p: int) -> int:
    out = 0
    for c in reversed(poly):
        out = (out * x + c) % p
    return out


def poly_derivative(poly: Sequence[int], p: int) -> list[int]:
    return poly_trim([i * poly[i] % p for i in range(1, len(poly))] or [0], p)


def half_points(instance: Instance) -> list[tuple[int, int]]:
    points = []
    for j in range(1, (instance.n - 1) // 2 + 1):
        P = instance.curve.mul(j, instance.G)
        if P is None:
            raise AssertionError("half-orbit point became infinity")
        points.append(P)
    if len({P[0] for P in points}) != len(points):
        raise AssertionError("half-orbit x collision")
    return points


def kernel_poly(instance: Instance, points: Sequence[tuple[int, int]]) -> list[int]:
    out = [1]
    for x, _ in points:
        out = poly_mul(out, [(-x) % instance.curve.p, 1], instance.curve.p)
    return out


def marked_Y(instance: Instance, marker: int, points: Sequence[tuple[int, int]]) -> Vector:
    inv_marker = pow(marker, -1, instance.n)
    return tuple(
        ((-1 if (j * inv_marker % instance.n) & 1 else 1) * y) % instance.curve.p
        for j, (_, y) in enumerate(points, start=1)
    )


def vconst(value: int, size: int, p: int) -> Vector:
    return tuple(value % p for _ in range(size))


def vadd(a: Vector, b: Vector, p: int) -> Vector:
    return tuple((x + y) % p for x, y in zip(a, b))


def vsub(a: Vector, b: Vector, p: int) -> Vector:
    return tuple((x - y) % p for x, y in zip(a, b))


def vmul(a: Vector, b: Vector, p: int) -> Vector:
    return tuple(x * y % p for x, y in zip(a, b))


def vneg(a: Vector, p: int) -> Vector:
    return tuple(-x % p for x in a)


def vis_unit(a: Vector, p: int) -> bool:
    return all(x % p != 0 for x in a)


def vinv(a: Vector, p: int) -> Vector:
    if not vis_unit(a, p):
        raise ZeroDivisionError("nonunit vector")
    return tuple(pow(x, -1, p) for x in a)


@dataclass(frozen=True)
class QuadraticPair:
    even: Vector
    odd: Vector

    def add(self, other: "QuadraticPair", p: int) -> "QuadraticPair":
        return QuadraticPair(vadd(self.even, other.even, p), vadd(self.odd, other.odd, p))

    def mul(self, other: "QuadraticPair", F: Vector, p: int) -> "QuadraticPair":
        return QuadraticPair(
            vadd(vmul(self.even, other.even, p), vmul(vmul(self.odd, other.odd, p), F, p), p),
            vadd(vmul(self.even, other.odd, p), vmul(self.odd, other.even, p), p),
        )

    def norm(self, F: Vector, p: int) -> Vector:
        return vsub(vmul(self.even, self.even, p), vmul(vmul(self.odd, self.odd, p), F, p), p)

    def inverse(self, F: Vector, p: int) -> "QuadraticPair":
        inv_norm = vinv(self.norm(F, p), p)
        return QuadraticPair(vmul(self.even, inv_norm, p), vmul(vneg(self.odd, p), inv_norm, p))

    def evaluate(self, Y: Vector, p: int) -> Vector:
        return vadd(self.even, vmul(self.odd, Y, p), p)


def public_pair(value: Vector) -> QuadraticPair:
    return QuadraticPair(value, tuple(0 for _ in value))


def branch_pair(size: int) -> QuadraticPair:
    return QuadraticPair(tuple(0 for _ in range(size)), tuple(1 for _ in range(size)))


def legendre(value: int, p: int) -> int:
    value %= p
    if value == 0:
        return 0
    return 1 if pow(value, (p - 1) // 2, p) == 1 else -1


def character_equations(instance: Instance) -> tuple[list[tuple[list[int], int]], int]:
    p, n = instance.curve.p, instance.n
    points = half_points(instance)
    Kp = poly_derivative(kernel_poly(instance, points), p)
    beta, beta2 = instance.beta % p, instance.beta * instance.beta % p
    equations: list[tuple[list[int], int]] = []
    checks = 0
    for marker in range(1, n):
        Gm = instance.curve.mul(marker, instance.G)
        if Gm is None:
            raise AssertionError("marked generator became infinity")
        xg, yg = Gm
        base = (yg, poly_eval(Kp, xg, p), poly_eval(Kp, beta*xg % p, p), poly_eval(Kp, beta2*xg % p, p))
        if any(v == 0 for v in base):
            raise AssertionError("zero character anchor")
        for k in range(1, n):
            Q = instance.curve.mul(k, Gm)
            if Q is None:
                raise AssertionError("query became infinity")
            x, y = Q
            values = (y, poly_eval(Kp, x, p), poly_eval(Kp, beta*x % p, p), poly_eval(Kp, beta2*x % p, p))
            bits = []
            for value, anchor in zip(values, base):
                sign = legendre(value * pow(anchor, -1, p), p)
                if sign == 0:
                    raise AssertionError("zero character value")
                bits.append(0 if sign == 1 else 1)
            target = 1 if (k + 1) & 1 else 0
            equations.append((bits, target))
            checks += 1
    return equations, checks


def exact_character_masks(equations: Sequence[tuple[list[int], int]]) -> list[int]:
    out = []
    for mask in range(16):
        if all(
            (sum(bit for i, bit in enumerate(bits) if (mask >> i) & 1) & 1) == target
            for bits, target in equations
        ):
            out.append(mask)
    return out


def curve_record(instance: Instance) -> dict[str, Any]:
    p, n = instance.curve.p, instance.n
    points = half_points(instance)
    m = len(points)
    xs = tuple(x for x, _ in points)
    F = tuple(instance.curve.rhs(x) for x in xs)
    Kp_poly = poly_derivative(kernel_poly(instance, points), p)
    Kp = tuple(poly_eval(Kp_poly, x, p) for x in xs)
    if not vis_unit(Kp, p):
        raise AssertionError("K_H' is not a unit")

    one, zero = vconst(1, m, p), vconst(0, m, p)
    symbol = branch_pair(m)
    expression = public_pair(xs).add(symbol.mul(public_pair(Kp), F, p), p)
    branch_components = gauge_checks = circuit_checks = unit_recoveries = 0
    singular_collisions = 0

    for marker in range(1, n):
        Y = marked_Y(instance, marker, points)
        if tuple(y*y % p for y in Y) != F:
            raise AssertionError("Y^2 != F")
        minus_Y = vneg(Y, p)
        gauged = vmul(Kp, Y, p)
        if vmul(vinv(Kp, p), gauged, p) != Y:
            raise AssertionError("unit gauge recovery failed")
        gauge_checks += m

        plus, minus = expression.evaluate(Y, p), expression.evaluate(minus_Y, p)
        if plus != vadd(xs, vmul(Kp, Y, p), p):
            raise AssertionError("rank-two plus evaluation failed")
        if minus != vadd(xs, vmul(Kp, minus_Y, p), p):
            raise AssertionError("rank-two minus evaluation failed")
        recovered = vmul(vsub(plus, expression.even, p), vinv(expression.odd, p), p)
        if recovered != Y:
            raise AssertionError("unit odd coefficient recovery failed")
        circuit_checks += 2*m
        unit_recoveries += m

        odd = list(one)
        index = marker % m
        odd[index] = 0
        singular = QuadraticPair(one, tuple(odd))
        if singular.evaluate(Y, p)[index] != singular.evaluate(minus_Y, p)[index]:
            raise AssertionError("singular coefficient did not collide")
        singular_collisions += 1
        branch_components += m

        denominator = QuadraticPair(vadd(Kp, one, p), zero)
        identity = denominator.mul(denominator.inverse(F, p), F, p)
        if identity.even != one or identity.odd != zero:
            raise AssertionError("rank-two inverse failed")

    equations, char_checks = character_equations(instance)
    survivors = exact_character_masks(equations)
    if survivors:
        raise AssertionError(f"unexpected character survivors: {survivors}")
    return {
        "id": instance.name,
        "p": p,
        "n": n,
        "kernel_degree": m,
        "marked_generators": n-1,
        "oriented_branch_components_checked": branch_components,
        "kernel_derivative_gauge_checks": gauge_checks,
        "quadratic_circuit_component_checks": circuit_checks,
        "unit_certificate_recovery_checks": unit_recoveries,
        "singular_component_collision_checks": singular_collisions,
        "local_character_scalar_checks": char_checks,
        "local_character_masks_tested": 16,
        "local_character_exact_survivors": 0,
    }


def run() -> dict[str, Any]:
    rows = [curve_record(instance) for instance in INSTANCES]
    totals = {
        "curves": len(rows),
        "marked_generators": sum(r["marked_generators"] for r in rows),
        "oriented_branch_components_checked": sum(r["oriented_branch_components_checked"] for r in rows),
        "kernel_derivative_gauge_checks": sum(r["kernel_derivative_gauge_checks"] for r in rows),
        "quadratic_circuit_component_checks": sum(r["quadratic_circuit_component_checks"] for r in rows),
        "unit_certificate_recovery_checks": sum(r["unit_certificate_recovery_checks"] for r in rows),
        "singular_component_collision_checks": sum(r["singular_component_collision_checks"] for r in rows),
        "local_character_scalar_checks": sum(r["local_character_scalar_checks"] for r in rows),
        "local_character_masks_tested_per_global_grammar": 16,
        "local_character_exact_survivors": 0,
        "errors": 0,
    }
    assert totals["marked_generators"] == 438
    assert totals["kernel_derivative_gauge_checks"] == 23130
    assert totals["local_character_scalar_checks"] == 46260
    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "profile_id": PROFILE_ID,
        "central_target": "Y_G(x([k]G))/y([k]G)=(-1)^k",
        "quadratic_branch_normal_form": {
            "algebra": "B=A[Y]/(Y^2-F), A a finite product of odd-characteristic fields, F a unit",
            "normal_form": "Every regular rational expression in public A-data and Y reduces to E+O*Y",
            "branch_difference": "C(Y)-C(-Y)=2*O*Y",
            "unit_case": "Y=O^(-1)*(C-E)",
            "nonunit_case": "O vanishes on a component and the two branches collide there",
        },
        "kernel_derivative_gauge": {
            "premise": "K_H squarefree implies K_H' is a unit modulo K_H",
            "transform": "Z=K_H'*Y_G",
            "inverse": "Y_G=(K_H')^(-1)*Z",
            "decision": "K_H' is a public unit gauge, not a separate compression mechanism",
        },
        "local_character_grammar": {
            "atoms": [
                "chi(y(Q)/y(G))",
                "chi(K_H'(x(Q))/K_H'(x(G)))",
                "chi(K_H'(beta*x(Q))/K_H'(beta*x(G)))",
                "chi(K_H'(beta^2*x(Q))/K_H'(beta^2*x(G)))",
            ],
            "products_tested": 16,
            "exact_survivors": 0,
            "scope": "finite exact all-point frozen-corpus screen",
        },
        "exact_replay": {**totals, "curve_rows": rows},
        "decision": {
            "quadratic_branch_normal_form_compiler_built": True,
            "branch_even_rational_circuit_creates_orientation": False,
            "everywhere_branch_separating_local_certificate_is_unit_equivalent": True,
            "kernel_derivative_is_unit_gauge": True,
            "kernel_derivative_gauge_reduces_to_oriented_root": True,
            "local_kernel_derivative_character_candidate_found": False,
            "public_oriented_seed_found": False,
            "target_dependent_nonlocal_compiler_found": False,
            "exact_parity_extraction_found": False,
            "complete_cost_gate_passed": False,
            "compact_branch_odd_evaluator_found": False,
            "sub_sqrt_evaluator_found": False,
            "parity_oracle_found": False,
            "sub_sqrt_ecdlp_found": False,
        },
        "closed_class": [
            "everywhere-regular one-point rational postprocessing of one quadratic branch",
            "public unit gauges including multiplication or division by K_H'",
            "local certificates with a nonunit odd coefficient",
            "the declared four-atom kernel-derivative character grammar on the frozen corpus",
        ],
        "remaining_frontier": [
            "generation of the first public branch-sensitive seed",
            "nonlocal target-dependent product-tree or modular-composition evaluation",
            "transposed oriented functionals whose source is generated rather than supplied",
            "continuation with an independently public branch normalization",
        ],
        "scientific_boundary": "No unrestricted nonlocal circuit, parity, or ECDLP lower bound is claimed.",
        "successor": "NONLOCAL-ORIENTED-SEED-GENERATION-081",
    }
    payload["digest"] = payload_digest(payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = run()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(stable_json(payload), encoding="utf-8")
    print(stable_json(payload), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
