#!/usr/bin/env python3
"""Verify the public secp256k1 EDS-residue parity bridge.

The program uses only fixed public curve parameters and fixed scalars whose
values are already known. It accepts no external point, wallet, public key, or
discrete-log target.
"""
from __future__ import annotations

import argparse
import json
import math
from functools import lru_cache
from pathlib import Path

Point = tuple[int, int] | None

P = 2**256 - 2**32 - 977
N = int("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141", 16)
GX = int("79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798", 16)
GY = int("483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8", 16)
G = (GX, GY)
SAMPLES = (1, 2, 3, 7, 11, 123456789, N - 2, N - 1)


def ec_add(left: Point, right: Point) -> Point:
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % P == 0:
        return None
    if left == right:
        if y1 == 0:
            return None
        slope = 3 * x1 * x1 * pow(2 * y1, -1, P) % P
    else:
        slope = (y2 - y1) * pow((x2 - x1) % P, -1, P) % P
    x3 = (slope * slope - x1 - x2) % P
    y3 = (slope * (x1 - x3) - y1) % P
    return x3, y3


def ec_mul(scalar: int, point: Point) -> Point:
    result: Point = None
    addend = point
    while scalar:
        if scalar & 1:
            result = ec_add(result, addend)
        addend = ec_add(addend, addend)
        scalar >>= 1
    return result


def quadratic_character(value: int) -> int:
    value %= P
    if value == 0:
        return 0
    return 1 if pow(value, (P - 1) // 2, P) == 1 else -1


def division_polynomial_evaluator(point: tuple[int, int]):
    x, y = point

    @lru_cache(maxsize=None)
    def psi(index: int) -> int:
        if index < 0:
            return -psi(-index) % P
        if index == 0:
            return 0
        if index == 1:
            return 1
        if index == 2:
            return 2 * y % P
        if index == 3:
            return (3 * x**4 + 84 * x) % P
        if index == 4:
            return 4 * y * (x**6 + 140 * x**3 - 392) % P
        if index & 1:
            m = (index - 1) // 2
            return (
                psi(m + 2) * pow(psi(m), 3, P)
                - psi(m - 1) * pow(psi(m + 1), 3, P)
            ) % P
        m = index // 2
        return (
            psi(m)
            * pow(2 * y, -1, P)
            * (
                psi(m + 2) * pow(psi(m - 1), 2, P)
                - psi(m - 2) * pow(psi(m + 1), 2, P)
            )
        ) % P

    return psi


def periodic_scale(point: tuple[int, int]) -> int:
    """Compute the Lauter-Stange periodic scaling function at a nonzero point."""
    psi = division_polynomial_evaluator(point)
    numerator = psi(P - 1)
    denominator = psi(P - 1 + N)
    if numerator == 0 or denominator == 0:
        raise AssertionError("public prime-order point produced a zero denominator")
    ratio = numerator * pow(denominator, -1, P) % P
    inverse_n_squared = pow(N * N % (P - 1), -1, P - 1)
    value = pow(ratio, inverse_n_squared, P)
    if pow(value, N * N, P) != ratio:
        raise AssertionError("periodic scaling root check failed")
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("secp_eds_residue_bridge_results.json"),
    )
    args = parser.parse_args()

    if math.gcd(N, P - 1) != 1:
        raise AssertionError("secp256k1 order is not coprime to p-1")
    if ec_mul(N, G) is not None:
        raise AssertionError("public generator order check failed")

    phi_g = periodic_scale(G)
    if quadratic_character(phi_g) != -1:
        raise AssertionError("public secp256k1 periodic scale is not a nonresidue")

    psi_g = division_polynomial_evaluator(G)
    rows = []
    for scalar in SAMPLES:
        point = ec_mul(scalar, G)
        if point is None:
            raise AssertionError("fixed sample unexpectedly reached infinity")
        phi_q = periodic_scale(point)
        w_k = psi_g(scalar)

        corrected_identity = pow(phi_g, scalar * scalar, P) * w_k % P
        displayed_minus_one_identity = (
            pow(phi_g, scalar * scalar - 1, P) * w_k % P
        )
        if phi_q != corrected_identity:
            raise AssertionError("corrected periodic EDS identity failed")

        parity_sign = -1 if scalar & 1 else 1
        residue_product = quadratic_character(phi_q) * quadratic_character(w_k)
        if residue_product != parity_sign:
            raise AssertionError("EDS residue parity bridge failed")

        rows.append(
            {
                "scalar": str(scalar),
                "phi_q_hex": hex(phi_q),
                "chi_phi_q": quadratic_character(phi_q),
                "chi_w_k": quadratic_character(w_k),
                "product_equals_minus_one_pow_k": residue_product,
                "parity_sign": parity_sign,
                "corrected_k_squared_identity": True,
                "displayed_k_squared_minus_one_identity": (
                    phi_q == displayed_minus_one_identity
                ),
            }
        )

    payload = {
        "scope": "fixed public secp256k1 parameters and fixed known scalars only",
        "p_hex": hex(P),
        "n_hex": hex(N),
        "gcd_n_p_minus_one": math.gcd(N, P - 1),
        "phi_g_hex": hex(phi_g),
        "chi_phi_g": quadratic_character(phi_g),
        "bridge": (
            "(-1)^k = chi(phi([k]G))*chi(W_G(k)), because chi(phi(G))=-1"
        ),
        "normalization_check": {
            "corrected_identity": "phi([k]G)=phi(G)^(k^2)*W_G(k)",
            "printed_2008_equation_checked": (
                "phi([k]G)=phi(G)^(k^2-1)*W_G(k)"
            ),
            "printed_equation_passes_fixed_samples": all(
                row["displayed_k_squared_minus_one_identity"] for row in rows
            ),
            "interpretation": (
                "The k^2 exponent is consistent with k=1, the net transformation law, "
                "the later 2k+1 ratio formula, and every fixed replay sample."
            ),
        },
        "samples": rows,
        "claim_boundary": [
            "This verifies a public structural condition, not a discrete logarithm.",
            "The hidden value chi(W_G(k)) is not computed from an unknown target.",
            "The program accepts no external point or scalar.",
            "Independent CAS and source-level review remain required before promotion."
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
