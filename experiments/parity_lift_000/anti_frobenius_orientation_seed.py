#!/usr/bin/env python3
"""Toy-only replay for ANTI-FROBENIUS-ORIENTATION-SEED-031.

For every frozen j=0 prime-order subgroup, define

    A(k) = eta(k) - conjugate(eta(k)),
    U(k) = A(k) / A(1).

The replay verifies that U is real in the fixed complex subfield, U(1)=1,
U(lambda*k)=U(k), U(-k)=-U(k), and

    carry(k) = carry(1) * sign(U(k)).

This validates the normalization and sign convention. It does not provide a
public evaluation of U from elliptic-curve point coordinates.

No external point, key, wallet, or production-sized target is accepted.
"""
from __future__ import annotations

import argparse
import cmath
import json
import math
from pathlib import Path

from nonlocal_odd_anchor_screen import (
    FROZEN_CASES,
    orbit,
    primitive_cube_root,
)

SECP256K1_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
TOLERANCE = 3.0e-10


def carry_sign(k: int, lam: int, order: int) -> int:
    if k % order == 0:
        return 0
    k %= order
    k1 = lam * k % order
    k2 = lam * k1 % order
    total = k + k1 + k2
    if total == order:
        return -1
    if total == 2 * order:
        return 1
    raise AssertionError("GLV carry representatives did not sum to n or 2n")


def scalar_lambda(
    p: int, order: int, generator: tuple[int, int]
) -> tuple[int, int]:
    points = orbit(generator, order, p)
    beta = primitive_cube_root(p)
    point_to_scalar = {point: scalar for scalar, point in enumerate(points)}
    lam = point_to_scalar[(beta * generator[0] % p, generator[1])]
    if lam in (0, 1) or pow(lam, 3, order) != 1:
        raise AssertionError("invalid GLV eigenvalue")
    return beta, lam


def eta(k: int, lam: int, order: int) -> complex:
    lam2 = lam * lam % order
    return sum(
        cmath.exp(2j * math.pi * exponent / order)
        for exponent in (
            k % order,
            lam * k % order,
            lam2 * k % order,
        )
    )


def run_case(
    p: int, order: int, generator: tuple[int, int]
) -> dict[str, object]:
    beta, lam = scalar_lambda(p, order, generator)
    seed = eta(1, lam, order) - eta(1, lam, order).conjugate()
    if abs(seed) <= TOLERANCE:
        raise AssertionError("canonical anti-Frobenius seed vanished")
    seed_carry = carry_sign(1, lam, order)

    seed_checks = 1
    fixed_checks = 0
    glv_checks = 0
    negation_checks = 0
    carry_checks = 0
    maximum_imaginary_residual = 0.0
    maximum_glv_residual = 0.0
    maximum_negation_residual = 0.0
    minimum_abs_real = math.inf

    values: dict[int, complex] = {}
    for k in range(1, order):
        numerator = eta(k, lam, order) - eta(k, lam, order).conjugate()
        value = numerator / seed
        values[k] = value
        maximum_imaginary_residual = max(
            maximum_imaginary_residual, abs(value.imag)
        )
        if abs(value.imag) > TOLERANCE:
            raise AssertionError("normalized resolvent left the fixed real line")
        if abs(value.real) <= TOLERANCE:
            raise AssertionError("normalized resolvent vanished")
        minimum_abs_real = min(minimum_abs_real, abs(value.real))
        fixed_checks += 1

        observed = seed_carry * (1 if value.real > 0 else -1)
        if observed != carry_sign(k, lam, order):
            raise AssertionError("normalized resolvent lost carry sign")
        carry_checks += 1

    if abs(values[1] - 1.0) > TOLERANCE:
        raise AssertionError("U(1) lost its normalization")

    for k in range(1, order):
        glv_k = lam * k % order
        glv_residual = abs(values[glv_k] - values[k])
        maximum_glv_residual = max(maximum_glv_residual, glv_residual)
        if glv_residual > TOLERANCE:
            raise AssertionError("normalized resolvent lost GLV invariance")
        glv_checks += 1

        negative = order - k
        neg_residual = abs(values[negative] + values[k])
        maximum_negation_residual = max(
            maximum_negation_residual, neg_residual
        )
        if neg_residual > TOLERANCE:
            raise AssertionError("normalized resolvent lost negation anti-invariance")
        negation_checks += 1

    return {
        "p": p,
        "order": order,
        "generator": generator,
        "beta": beta,
        "lambda": lam,
        "seed_carry": seed_carry,
        "seed_nonzero_checks": seed_checks,
        "fixed_line_checks": fixed_checks,
        "glv_invariance_checks": glv_checks,
        "negation_anti_invariance_checks": negation_checks,
        "carry_sign_checks": carry_checks,
        "maximum_imaginary_residual": maximum_imaginary_residual,
        "maximum_glv_residual": maximum_glv_residual,
        "maximum_negation_residual": maximum_negation_residual,
        "minimum_abs_normalized_real": minimum_abs_real,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "anti_frobenius_orientation_seed_results.json"
        ),
    )
    args = parser.parse_args()

    cases = [run_case(p, order, generator) for p, order, generator in FROZEN_CASES]
    quotient_states = (SECP256K1_N - 1) // 6

    payload = {
        "package": "ANTI-FROBENIUS-ORIENTATION-SEED-031",
        "scope": (
            "complex cyclotomic sign-convention replay on frozen toy "
            "subgroups; no external point, key, wallet, or production-sized "
            "target"
        ),
        "cases": cases,
        "secp256k1": {
            "order": SECP256K1_N,
            "natural_explicit_quotient_states": quotient_states,
            "gaussian_period_conjugate_pairs": quotient_states,
            "half_kernel_degree": quotient_states,
        },
        "aggregate": {
            "cases": len(cases),
            "total_fixed_line_checks": sum(
                int(row["fixed_line_checks"]) for row in cases
            ),
            "total_glv_invariance_checks": sum(
                int(row["glv_invariance_checks"]) for row in cases
            ),
            "total_negation_anti_invariance_checks": sum(
                int(row["negation_anti_invariance_checks"])
                for row in cases
            ),
            "total_carry_sign_checks": sum(
                int(row["carry_sign_checks"]) for row in cases
            ),
            "maximum_imaginary_residual": max(
                float(row["maximum_imaginary_residual"]) for row in cases
            ),
            "maximum_glv_residual": max(
                float(row["maximum_glv_residual"]) for row in cases
            ),
            "maximum_negation_residual": max(
                float(row["maximum_negation_residual"]) for row in cases
            ),
        },
        "decision": (
            "A_G(G) canonically normalizes the anti-Frobenius line and the "
            "resulting U_G has exactly the carry sign. The normalization does "
            "not provide a public Q-only evaluation and retains the natural "
            "(n-1)/6 quotient-state representation."
        ),
        "claim_boundary": [
            "Complex arithmetic validates identities and sign conventions but is not a finite-field public decoder.",
            "The quotient-state count is a natural explicit representation size, not a circuit lower bound.",
            "The secp256k1 subgroup is not enumerated.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
