#!/usr/bin/env python3
"""Toy-only identity check for the pi-1 kernel derivative.

The horizontal C3-orbit polynomial P(y) has divisor equal to the nonzero
subgroup points minus (n-1)O.  Its invariant derivative is 3*x^2*P'(y), whose
quadratic character differs from chi(P'(y)) by the fixed character chi(3).
The predicted identity is therefore

    chi(P'(y([k]G))) = constant * g(k) * R3(k).

No external or production-sized input is accepted.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from nonlocal_odd_anchor_screen import (
    FROZEN_CASES,
    division_polynomial_evaluator,
    orbit,
    primitive_cube_root,
    quadratic_character,
)


def poly_mul(left: list[int], right: list[int], p: int) -> list[int]:
    out = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            out[i + j] = (out[i + j] + a * b) % p
    return out


def poly_from_roots(roots: list[int], p: int) -> list[int]:
    out = [1]
    for root in roots:
        out = poly_mul(out, [(-root) % p, 1], p)
    return out


def poly_derivative(coefficients: list[int], p: int) -> list[int]:
    return [(i * coefficients[i]) % p for i in range(1, len(coefficients))]


def poly_eval(coefficients: list[int], value: int, p: int) -> int:
    out = 0
    for coefficient in reversed(coefficients):
        out = (out * value + coefficient) % p
    return out


def carry(k: int, lam: int, order: int) -> int:
    k1 = lam * k % order
    k2 = lam * k1 % order
    total = k + k1 + k2
    if total == order:
        return -1
    if total == 2 * order:
        return 1
    raise AssertionError("carry identity failed")


@dataclass(frozen=True)
class CaseResult:
    p: int
    order: int
    generator: tuple[int, int]
    beta: int
    lam: int
    orbit_polynomial_degree: int
    derivative_checks: int
    raw_matches: int
    negated_matches: int
    exact_up_to_global_sign: bool
    global_sign: int
    invariant_derivative_matches: int
    invariant_derivative_exact_up_to_global_sign: bool
    invariant_derivative_global_sign: int


def run_case(p: int, order: int, generator: tuple[int, int]) -> CaseResult:
    points = orbit(generator, order, p)
    beta = primitive_cube_root(p)
    point_to_scalar = {point: scalar for scalar, point in enumerate(points)}
    lam = point_to_scalar[(beta * generator[0] % p, generator[1])]
    lam2 = lam * lam % order

    visited: set[int] = set()
    roots: list[int] = []
    for k in range(1, order):
        if k in visited:
            continue
        c3 = {k, lam * k % order, lam2 * k % order}
        if len(c3) != 3:
            raise AssertionError("C3 orbit had wrong size")
        point = points[k]
        assert point is not None
        y = point[1]
        if any(points[member][1] != y for member in c3):
            raise AssertionError("C3 orbit did not share y")
        roots.append(y)
        visited.update(c3)

    polynomial = poly_from_roots(roots, p)
    derivative = poly_derivative(polynomial, p)
    if len(polynomial) - 1 != (order - 1) // 3:
        raise AssertionError("orbit polynomial degree failed")

    psi = division_polynomial_evaluator(generator, p)
    rho = [0] + [quadratic_character(psi(k), p) for k in range(1, order)]

    raw_matches = 0
    negated_matches = 0
    inv_raw_matches = 0
    inv_negated_matches = 0

    for k in range(1, order):
        point = points[k]
        assert point is not None
        x, y = point
        value = poly_eval(derivative, y, p)
        if value == 0:
            raise AssertionError("orbit polynomial derivative vanished at a root")

        k1 = lam * k % order
        k2 = lam2 * k % order
        public_c3 = carry(k, lam, order) * rho[k] * rho[k1] * rho[k2]
        derivative_character = quadratic_character(value, p)
        invariant_derivative_character = quadratic_character(3 * x * x * value, p)

        raw_matches += derivative_character == public_c3
        negated_matches += derivative_character == -public_c3
        inv_raw_matches += invariant_derivative_character == public_c3
        inv_negated_matches += invariant_derivative_character == -public_c3

    total = order - 1
    exact = raw_matches == total or negated_matches == total
    inv_exact = inv_raw_matches == total or inv_negated_matches == total
    return CaseResult(
        p=p,
        order=order,
        generator=generator,
        beta=beta,
        lam=lam,
        orbit_polynomial_degree=len(polynomial) - 1,
        derivative_checks=total,
        raw_matches=raw_matches,
        negated_matches=negated_matches,
        exact_up_to_global_sign=exact,
        global_sign=1 if raw_matches == total else (-1 if negated_matches == total else 0),
        invariant_derivative_matches=max(inv_raw_matches, inv_negated_matches),
        invariant_derivative_exact_up_to_global_sign=inv_exact,
        invariant_derivative_global_sign=(
            1 if inv_raw_matches == total else (-1 if inv_negated_matches == total else 0)
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "frobenius_kernel_derivative_identity_results.json"
        ),
    )
    args = parser.parse_args()

    cases = [run_case(*case) for case in FROZEN_CASES]
    payload = {
        "scope": (
            "fifteen frozen j=0 prime-order toy subgroups; "
            "no external point, key, wallet, or production target"
        ),
        "package": "FROBENIUS-KERNEL-DERIVATIVE-013",
        "predicted_identity": (
            "chi(P'(y([k]G))) = constant * g(k) * "
            "rho(k)rho(lambda*k)rho(lambda^2*k)"
        ),
        "invariant_derivative": "D(P(y))=3*x^2*P'(y)",
        "cases": [asdict(case) for case in cases],
        "aggregate": {
            "cases": len(cases),
            "total_derivative_checks": sum(case.derivative_checks for case in cases),
            "exact_raw_identities_up_to_global_sign": sum(
                case.exact_up_to_global_sign for case in cases
            ),
            "exact_invariant_derivative_identities_up_to_global_sign": sum(
                case.invariant_derivative_exact_up_to_global_sign for case in cases
            ),
            "largest_order": max(case.order for case in cases),
        },
        "decision": (
            "If exact across the frozen family, the canonical pi-1 kernel "
            "derivative reproduces the already-public C3 character rather than "
            "a separate carry or R3 decoder."
        ),
        "claim_boundary": [
            "The divisor identification is mathematical; the cross-order script is a finite replay of its quadratic-character consequence.",
            "A different higher jet or weight-zero ratio is not ruled out by this identity alone.",
            "No external or production-sized input is accepted.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
