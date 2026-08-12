#!/usr/bin/env python3
"""Toy-only replay for GLV-GAUSSIAN-PERIOD-CUT-029.

For each frozen j=0 prime-order subgroup, the script verifies

    eta(k) = zeta^k + zeta^(lambda*k) + zeta^(lambda^2*k),
    (1-zeta^k)(1-zeta^(lambda*k))(1-zeta^(lambda^2*k))
        = conjugate(eta(k)) - eta(k),
    carry(k) = -sign(Im eta(k)).

The Galois orbit and conjugate-pair counts are checked combinatorially from the
C3 cosets. Numerical complex arithmetic only validates the implementation and
sign convention; it is not used as the proof of the degree statement.

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
TOLERANCE = 2.0e-10


def carry_sign(k: int, lam: int, order: int) -> int:
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
    if (1 + lam + lam * lam) % order != 0:
        raise AssertionError("lambda failed its cyclotomic equation")
    return beta, lam


def c3_cosets(order: int, lam: int) -> list[tuple[int, int, int]]:
    lam2 = lam * lam % order
    visited: set[int] = set()
    cosets: list[tuple[int, int, int]] = []
    for k in range(1, order):
        if k in visited:
            continue
        coset = tuple(sorted({k, lam * k % order, lam2 * k % order}))
        if len(coset) != 3:
            raise AssertionError("nonzero C3 coset had wrong size")
        visited.update(coset)
        cosets.append(coset)
    if len(visited) != order - 1:
        raise AssertionError("C3 cosets did not partition nonzero scalars")
    return cosets


def run_case(
    p: int, order: int, generator: tuple[int, int]
) -> dict[str, object]:
    beta, lam = scalar_lambda(p, order, generator)
    lam2 = lam * lam % order
    cosets = c3_cosets(order, lam)
    coset_set = set(cosets)

    if order % 6 != 1:
        raise AssertionError("prime GLV order was not 1 mod 6")
    if tuple(sorted({order - 1, (-lam) % order, (-lam2) % order})) in coset_set:
        raise AssertionError("-C3 unexpectedly equaled C3")

    conjugate_pairs: set[tuple[tuple[int, int, int], tuple[int, int, int]]] = set()
    for coset in cosets:
        negative = tuple(sorted({(-value) % order for value in coset}))
        if negative == coset or negative not in coset_set:
            raise AssertionError("invalid conjugate C3 pairing")
        conjugate_pairs.add(tuple(sorted((coset, negative))))

    maximum_residual = 0.0
    minimum_abs_imaginary = math.inf
    identity_checks = 0
    carry_checks = 0
    glv_checks = 0
    conjugation_checks = 0

    for k in range(1, order):
        exponents = (k, lam * k % order, lam2 * k % order)
        phases = [
            cmath.exp(2j * math.pi * exponent / order)
            for exponent in exponents
        ]
        eta = sum(phases)
        product = (1 - phases[0]) * (1 - phases[1]) * (1 - phases[2])
        expected = eta.conjugate() - eta
        residual = abs(product - expected)
        maximum_residual = max(maximum_residual, residual)
        if residual > TOLERANCE:
            raise AssertionError("Gaussian-period resolvent identity drifted")
        identity_checks += 1

        minimum_abs_imaginary = min(minimum_abs_imaginary, abs(eta.imag))
        if abs(eta.imag) <= TOLERANCE:
            raise AssertionError("nontrivial Gaussian period appeared real")
        observed = -1 if eta.imag > 0 else 1
        if observed != carry_sign(k, lam, order):
            raise AssertionError("Gaussian-period orientation lost carry")
        carry_checks += 1

        shifted_exponents = (
            lam * k % order,
            lam2 * k % order,
            k,
        )
        shifted_eta = sum(
            cmath.exp(2j * math.pi * exponent / order)
            for exponent in shifted_exponents
        )
        if abs(shifted_eta - eta) > TOLERANCE:
            raise AssertionError("Gaussian period lost C3 invariance")
        glv_checks += 1

        negative_eta = sum(
            cmath.exp(2j * math.pi * ((-exponent) % order) / order)
            for exponent in exponents
        )
        if abs(negative_eta - eta.conjugate()) > TOLERANCE:
            raise AssertionError("Gaussian period lost conjugation law")
        conjugation_checks += 1

    return {
        "p": p,
        "order": order,
        "generator": generator,
        "beta": beta,
        "lambda": lam,
        "c3_cosets": len(cosets),
        "expected_c3_cosets": (order - 1) // 3,
        "conjugate_pairs": len(conjugate_pairs),
        "expected_conjugate_pairs": (order - 1) // 6,
        "identity_checks": identity_checks,
        "carry_orientation_checks": carry_checks,
        "glv_invariance_checks": glv_checks,
        "conjugation_checks": conjugation_checks,
        "maximum_complex_residual": maximum_residual,
        "minimum_abs_period_imaginary": minimum_abs_imaginary,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "glv_gaussian_period_cut_results.json"
        ),
    )
    args = parser.parse_args()

    cases = [run_case(p, order, generator) for p, order, generator in FROZEN_CASES]
    secp_period_degree = (SECP256K1_N - 1) // 3
    secp_pair_count = (SECP256K1_N - 1) // 6

    payload = {
        "package": "GLV-GAUSSIAN-PERIOD-CUT-029",
        "scope": (
            "exact C3-coset counting and numerical sign-convention replay on "
            "frozen toy subgroups; no external point, key, wallet, or "
            "production-sized target"
        ),
        "cases": cases,
        "secp256k1": {
            "order": SECP256K1_N,
            "gaussian_period_degree": secp_period_degree,
            "conjugate_orientation_pairs": secp_pair_count,
            "half_kernel_degree": secp_pair_count,
        },
        "aggregate": {
            "cases": len(cases),
            "total_identity_checks": sum(int(row["identity_checks"]) for row in cases),
            "total_carry_orientation_checks": sum(
                int(row["carry_orientation_checks"]) for row in cases
            ),
            "total_glv_invariance_checks": sum(
                int(row["glv_invariance_checks"]) for row in cases
            ),
            "total_conjugation_checks": sum(
                int(row["conjugation_checks"]) for row in cases
            ),
            "all_c3_counts_exact": all(
                row["c3_cosets"] == row["expected_c3_cosets"] for row in cases
            ),
            "all_conjugate_pair_counts_exact": all(
                row["conjugate_pairs"] == row["expected_conjugate_pairs"]
                for row in cases
            ),
            "maximum_complex_residual": max(
                float(row["maximum_complex_residual"]) for row in cases
            ),
        },
        "decision": (
            "The global GLV carry phase is exactly the conjugate orientation "
            "of a C3 Gaussian period. Explicit period representations retain "
            "degree (n-1)/3 and (n-1)/6 conjugate-pair states; no public "
            "sub-square-root orientation evaluator is obtained."
        ),
        "claim_boundary": [
            "The period-degree proof is algebraic/Galois-theoretic; floating-point replay only checks implementation conventions.",
            "Equality between the period pair count and half-kernel degree does not establish an explicit map between their roots.",
            "No circuit lower bound against direct bit-only orientation evaluation is claimed.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
