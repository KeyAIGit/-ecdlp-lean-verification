#!/usr/bin/env python3
"""Exact toy-only replay for THETA-SPLITTING-DUALITY-028.

The package verifies two finite-group consequences used by the theorem-first
argument:

* on every frozen prime-order scalar group, every nonzero character exponent
  is a permutation, hence a nontrivial character has full order;
* the GLV carry is C3 invariant and negation anti-invariant, so it cannot be a
  binary group character on the odd-order subgroup.

The secp256k1 subgroup order is checked symbolically/primality-wise without
enumerating its elements. No external point, key, wallet, or production target
is accepted.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from sympy import isprime

from nonlocal_odd_anchor_screen import (
    FROZEN_CASES,
    orbit,
    primitive_cube_root,
)

SECP256K1_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def carry_sign(k: int, lam: int, order: int) -> int:
    if k == 0:
        return 0
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
    glv_point = (beta * generator[0] % p, generator[1])
    lam = point_to_scalar[glv_point]
    if lam in (0, 1) or pow(lam, 3, order) != 1:
        raise AssertionError("invalid GLV eigenvalue")
    return beta, lam


def verify_character_dichotomy(order: int) -> dict[str, int | bool]:
    if not isprime(order):
        raise AssertionError("frozen subgroup order lost primality")
    if math.gcd(order, 2) != 1:
        raise AssertionError("prime-order subgroup unexpectedly even")

    full_order_exponents = 0
    for exponent in range(order):
        image = {(exponent * k) % order for k in range(order)}
        expected = 1 if exponent == 0 else order
        if len(image) != expected:
            raise AssertionError("prime-order exponent map had intermediate image")
        if exponent:
            full_order_exponents += 1

    return {
        "order": order,
        "binary_character_count": math.gcd(order, 2),
        "trivial_exponent_maps": 1,
        "faithful_exponent_maps": full_order_exponents,
        "all_nonzero_exponents_faithful": full_order_exponents == order - 1,
    }


def verify_carry_symmetry(
    p: int, order: int, generator: tuple[int, int]
) -> dict[str, int | bool | tuple[int, int]]:
    beta, lam = scalar_lambda(p, order, generator)
    lam2 = lam * lam % order
    glv_checks = 0
    negation_checks = 0
    for k in range(1, order):
        value = carry_sign(k, lam, order)
        if carry_sign(lam * k % order, lam, order) != value:
            raise AssertionError("carry lost C3 invariance")
        if carry_sign(lam2 * k % order, lam, order) != value:
            raise AssertionError("carry lost second C3 invariance")
        glv_checks += 2
        if carry_sign(order - k, lam, order) != -value:
            raise AssertionError("carry lost negation anti-invariance")
        negation_checks += 1

    # A {+1,-1}-valued character has f(-Q)=f(Q)^(-1)=f(Q). The exact
    # anti-invariance above therefore certifies that carry is not a character.
    return {
        "p": p,
        "order": order,
        "generator": generator,
        "beta": beta,
        "lambda": lam,
        "glv_invariance_checks": glv_checks,
        "negation_anti_invariance_checks": negation_checks,
        "carry_is_binary_character": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "theta_splitting_duality_results.json"
        ),
    )
    args = parser.parse_args()

    character_cases = [
        verify_character_dichotomy(order)
        for _p, order, _generator in FROZEN_CASES
    ]
    carry_cases = [
        verify_carry_symmetry(p, order, generator)
        for p, order, generator in FROZEN_CASES
    ]

    if not isprime(SECP256K1_N):
        raise AssertionError("secp256k1 subgroup order lost primality")
    secp_certificate = {
        "order": SECP256K1_N,
        "prime": True,
        "odd": SECP256K1_N % 2 == 1,
        "binary_character_count": math.gcd(SECP256K1_N, 2),
        "nontrivial_character_image_order": SECP256K1_N,
        "intermediate_nontrivial_character_order_exists": False,
    }

    payload = {
        "package": "THETA-SPLITTING-DUALITY-028",
        "scope": (
            "exact finite-group and frozen toy GLV replay; no external point, "
            "key, wallet, or production-sized target"
        ),
        "character_cases": character_cases,
        "carry_cases": carry_cases,
        "secp256k1": secp_certificate,
        "aggregate": {
            "toy_prime_orders": len(character_cases),
            "all_nonzero_toy_exponents_faithful": all(
                row["all_nonzero_exponents_faithful"]
                for row in character_cases
            ),
            "all_binary_character_counts_one": all(
                row["binary_character_count"] == 1
                for row in character_cases
            ),
            "total_glv_invariance_checks": sum(
                int(row["glv_invariance_checks"]) for row in carry_cases
            ),
            "total_negation_anti_invariance_checks": sum(
                int(row["negation_anti_invariance_checks"])
                for row in carry_cases
            ),
            "carry_character_decoders": sum(
                bool(row["carry_is_binary_character"])
                for row in carry_cases
            ),
        },
        "decision": (
            "Standard splitting differences on the prime-order subgroup are "
            "either trivial or faithful order-n characters; the GLV carry is "
            "a nonlinear cut, not a binary character."
        ),
        "claim_boundary": [
            "The ratio-of-splittings theorem requires multiplicative splittings into a commutative central phase group.",
            "The replay does not formalize theta groups or prove a lower bound for arbitrary nonlinear circuits.",
            "A full-order character may still admit an unknown compressed bit predicate; package 029 isolates that question.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
