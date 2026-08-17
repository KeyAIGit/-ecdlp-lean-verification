#!/usr/bin/env python3
"""Exact toy-only replay for FROBENIUS-ORIENTATION-OBSTRUCTION-030.

For every eligible frozen subgroup, compute d=ord_n(p). When d is even,
verify p^(d/2)=-1 mod n and exhaustively check that half-Frobenius sends every
nonzero scalar k to -k while the GLV carry changes sign. Hence a predicate
invariant under multiplication by p cannot equal carry.

The anomalous p=n toy case and odd-order Frobenius cases are recorded outside
the half-Frobenius scope. The secp256k1 certificate checks the already-isolated
value d=(n-1)/6 and the exact half-power congruence without enumerating the
production-sized subgroup.

No external point, key, wallet, or production-sized target is accepted.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from sympy import isprime, n_order

from nonlocal_odd_anchor_screen import (
    FROZEN_CASES,
    orbit,
    primitive_cube_root,
)

SECP256K1_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
SECP256K1_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


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


def run_case(
    p: int, order: int, generator: tuple[int, int]
) -> dict[str, object]:
    if not isprime(order):
        raise AssertionError("frozen subgroup order lost primality")
    if math.gcd(p, order) != 1:
        return {
            "p": p,
            "order": order,
            "generator": generator,
            "status": "excluded_non_coprime_frobenius",
            "frobenius_order": None,
            "half_frobenius_is_negation": None,
            "scalar_checks": 0,
            "carry_flip_checks": 0,
        }

    d = int(n_order(p % order, order))
    if d % 2:
        return {
            "p": p,
            "order": order,
            "generator": generator,
            "status": "excluded_odd_frobenius_order",
            "frobenius_order": d,
            "half_frobenius_is_negation": False,
            "scalar_checks": 0,
            "carry_flip_checks": 0,
        }

    half_multiplier = pow(p, d // 2, order)
    if half_multiplier != order - 1:
        raise AssertionError("even-order Frobenius half-power was not -1")

    beta, lam = scalar_lambda(p, order, generator)
    scalar_checks = 0
    carry_checks = 0
    for k in range(1, order):
        image = half_multiplier * k % order
        if image != order - k:
            raise AssertionError("half-Frobenius scalar action lost negation")
        scalar_checks += 1
        if carry_sign(image, lam, order) != -carry_sign(k, lam, order):
            raise AssertionError("carry did not flip under half-Frobenius")
        carry_checks += 1

    return {
        "p": p,
        "order": order,
        "generator": generator,
        "status": "verified_half_frobenius_obstruction",
        "beta": beta,
        "lambda": lam,
        "frobenius_order": d,
        "half_frobenius_multiplier": half_multiplier,
        "half_frobenius_is_negation": True,
        "scalar_checks": scalar_checks,
        "carry_flip_checks": carry_checks,
        "frobenius_invariant_carry_decoder_possible": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "frobenius_orientation_obstruction_results.json"
        ),
    )
    args = parser.parse_args()

    cases = [run_case(p, order, generator) for p, order, generator in FROZEN_CASES]
    verified = [
        row for row in cases
        if row["status"] == "verified_half_frobenius_obstruction"
    ]
    excluded_odd = [
        row for row in cases
        if row["status"] == "excluded_odd_frobenius_order"
    ]
    excluded_non_coprime = [
        row for row in cases
        if row["status"] == "excluded_non_coprime_frobenius"
    ]

    if not isprime(SECP256K1_N):
        raise AssertionError("secp256k1 subgroup order lost primality")
    d = (SECP256K1_N - 1) // 6
    secp_full = pow(SECP256K1_P, d, SECP256K1_N)
    secp_half = pow(SECP256K1_P, d // 2, SECP256K1_N)
    if secp_full != 1 or secp_half != SECP256K1_N - 1:
        raise AssertionError("secp256k1 Frobenius certificate drifted")

    payload = {
        "package": "FROBENIUS-ORIENTATION-OBSTRUCTION-030",
        "scope": (
            "exact scalar and carry replay on eligible frozen toy subgroups, "
            "plus fixed-public secp256k1 half-Frobenius congruence; no "
            "external point, key, wallet, or production-sized target"
        ),
        "cases": cases,
        "secp256k1": {
            "p": SECP256K1_P,
            "order": SECP256K1_N,
            "certified_frobenius_order": d,
            "p_to_d_mod_n": secp_full,
            "p_to_half_d_mod_n": secp_half,
            "half_frobenius_is_negation": secp_half == SECP256K1_N - 1,
            "frobenius_invariant_carry_decoder_possible": False,
            "claim_boundary": (
                "minimality of d is reused from the existing exact embedding-"
                "degree certificate; this package rechecks p^d and p^(d/2)"
            ),
        },
        "aggregate": {
            "frozen_cases": len(cases),
            "verified_even_order_cases": len(verified),
            "excluded_odd_order_cases": len(excluded_odd),
            "excluded_non_coprime_cases": len(excluded_non_coprime),
            "total_scalar_checks": sum(int(row["scalar_checks"]) for row in verified),
            "total_carry_flip_checks": sum(
                int(row["carry_flip_checks"]) for row in verified
            ),
            "all_half_frobenius_actions_are_negation": all(
                bool(row["half_frobenius_is_negation"]) for row in verified
            ),
            "frobenius_invariant_carry_decoders": sum(
                bool(row.get("frobenius_invariant_carry_decoder_possible", False))
                for row in verified
            ),
        },
        "decision": (
            "Any period predicate invariant under Frobenius is invariant under "
            "half-Frobenius and therefore under scalar negation on the covered "
            "cases. It cannot equal the anti-invariant GLV carry."
        ),
        "claim_boundary": [
            "The obstruction covers Frobenius-invariant descent and does not prove a lower bound against anti-invariant or externally oriented circuits.",
            "Odd Frobenius-order toy cases do not satisfy the half-Frobenius premise and are excluded rather than interpreted negatively.",
            "The secp256k1 subgroup is not enumerated.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
