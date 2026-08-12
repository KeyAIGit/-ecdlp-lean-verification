#!/usr/bin/env python3
"""Normalization-aware toy identity for the pi-1 kernel derivative.

For a frozen curve let s be the point-scale character determined by

    rho(-k) = chi(-1) * s * rho(k).

The normalized GLV orbit character is then s^gamma * R3.  On secp256k1,
s=-1 and this is g*R3.  The invariant derivative of the horizontal kernel
polynomial is predicted to equal that character up to one fixed global sign.

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


def gamma_value(k: int, lam: int, order: int) -> int:
    k1 = lam * k % order
    k2 = lam * k1 % order
    total = k + k1 + k2
    if total == order:
        return 1
    if total == 2 * order:
        return 2
    raise AssertionError("GLV carry identity failed")


@dataclass(frozen=True)
class CaseResult:
    p: int
    order: int
    generator: tuple[int, int]
    beta: int
    lam: int
    point_scale_character: int
    rho_kummer_invariant: bool
    orbit_polynomial_degree: int
    derivative_checks: int
    exact_raw_derivative_up_to_sign: bool
    raw_global_sign: int
    exact_invariant_derivative_up_to_sign: bool
    invariant_global_sign: int
    secp_style_gR3_class: bool


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
    chi_minus_one = quadratic_character(-1, p)
    point_scale = rho[order - 1] * rho[1] * chi_minus_one
    if point_scale not in (-1, 1):
        raise AssertionError("point-scale character was not binary")
    if any(
        rho[order - k] != chi_minus_one * point_scale * rho[k]
        for k in range(1, order)
    ):
        raise AssertionError("residue negation law did not have a fixed scale")
    rho_kummer = all(rho[order - k] == rho[k] for k in range(1, order))

    raw_match = 0
    raw_negated = 0
    invariant_match = 0
    invariant_negated = 0

    for k in range(1, order):
        point = points[k]
        assert point is not None
        x, y = point
        value = poly_eval(derivative, y, p)
        if value == 0:
            raise AssertionError("kernel derivative vanished")
        k1 = lam * k % order
        k2 = lam2 * k % order
        gamma = gamma_value(k, lam, order)
        r3 = rho[k] * rho[k1] * rho[k2]
        normalized_orbit = (point_scale if gamma & 1 else 1) * r3

        raw = quadratic_character(value, p)
        invariant = quadratic_character(3 * x * x * value, p)
        raw_match += raw == normalized_orbit
        raw_negated += raw == -normalized_orbit
        invariant_match += invariant == normalized_orbit
        invariant_negated += invariant == -normalized_orbit

    total = order - 1
    raw_exact = raw_match == total or raw_negated == total
    invariant_exact = invariant_match == total or invariant_negated == total
    return CaseResult(
        p=p,
        order=order,
        generator=generator,
        beta=beta,
        lam=lam,
        point_scale_character=point_scale,
        rho_kummer_invariant=rho_kummer,
        orbit_polynomial_degree=len(polynomial) - 1,
        derivative_checks=total,
        exact_raw_derivative_up_to_sign=raw_exact,
        raw_global_sign=1 if raw_match == total else (-1 if raw_negated == total else 0),
        exact_invariant_derivative_up_to_sign=invariant_exact,
        invariant_global_sign=(
            1 if invariant_match == total else (-1 if invariant_negated == total else 0)
        ),
        secp_style_gR3_class=point_scale == -1,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "frobenius_kernel_derivative_identity_v2_results.json"
        ),
    )
    args = parser.parse_args()

    cases = [run_case(*case) for case in FROZEN_CASES]
    payload = {
        "scope": (
            "fifteen frozen j=0 prime-order toy subgroups; "
            "no external point, key, wallet, or production target"
        ),
        "package": "FROBENIUS-KERNEL-DERIVATIVE-013-V2",
        "identity": "chi(D P(y([k]G))) = constant * s^gamma(k) * R3(k)",
        "secp256k1_specialization": "s=-1, hence s^gamma*R3=g*R3",
        "cases": [asdict(case) for case in cases],
        "aggregate": {
            "cases": len(cases),
            "total_checks": sum(case.derivative_checks for case in cases),
            "exact_raw_identities": sum(
                case.exact_raw_derivative_up_to_sign for case in cases
            ),
            "exact_invariant_identities": sum(
                case.exact_invariant_derivative_up_to_sign for case in cases
            ),
            "secp_style_gR3_cases": sum(case.secp_style_gR3_class for case in cases),
            "kummer_residue_cases": sum(case.rho_kummer_invariant for case in cases),
            "largest_order": max(case.order for case in cases),
        },
        "decision": (
            "Exact agreement means the canonical Frobenius kernel derivative "
            "replays the normalized public orbit character. It is not an "
            "independent carry or R3 decoder."
        ),
        "claim_boundary": [
            "The script verifies the finite character identity; it does not formalize the generalized isogeny sigma construction.",
            "Higher weight-zero jet ratios remain a separate search class.",
            "No external or production-sized input is accepted.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
