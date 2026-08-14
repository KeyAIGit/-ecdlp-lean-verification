#!/usr/bin/env python3
"""Exact replay for UORC-056 Ward point-scale collapse V12.

For an F_p-rational point P of odd order n with gcd(n,p-1)=1, the Ward
quasi-period constants of W_j(P)=psi_j(P) satisfy

    b_P = phi_raw(P)^(-n^2),
    a_P = phi_raw(P)^(-2n),

where phi_raw is the already-public ratio-root point function.  Therefore
phi_raw(P) is recovered from b_P by one fixed exponentiation and the Ward state
contains no additional orientation information.

The replay uses only frozen toy curves and fixed public secp256k1 scalars.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from uorc056_division_polynomial_frontier import (
    DivisionPolynomialEvaluator,
    ec_mul,
    load_corpora,
    quadratic_character,
    stable_json,
)
from uorc056_eds_decimation_closure import ward_constants

PROFILE_ID = "UORC-056-WARD-POINT-SCALE-COLLAPSE-V12"
DEFAULT_GRAMMAR = Path("experiments/uorc056/divisor_aware_rational_grammar.json")
DEFAULT_OUTPUT = Path("experiments/uorc056/ward_point_scale_collapse_results.json")

SECP_P = int("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F", 16)
SECP_N = int("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141", 16)
SECP_G = (
    int("79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798", 16),
    int("483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8", 16),
)
SECP_SAMPLES = (1, 2, 3, 7, 11, 123456789, SECP_N - 2, SECP_N - 1)


def raw_point_scale(prime: int, order: int, point: tuple[int, int]) -> int:
    if math.gcd(order, prime - 1) != 1:
        raise ValueError("point-scale root needs gcd(n,p-1)=1")
    evaluator = DivisionPolynomialEvaluator(prime, 0, 7, point)
    numerator = evaluator.value(prime - 1)
    denominator = evaluator.value(prime - 1 + order)
    if numerator == 0 or denominator == 0:
        raise AssertionError("ratio-root point scale encountered zero")
    ratio = numerator * pow(denominator, -1, prime) % prime
    inverse_n_squared = pow(order * order % (prime - 1), -1, prime - 1)
    value = pow(ratio, inverse_n_squared, prime)
    if pow(value, order * order, prime) != ratio:
        raise AssertionError("point-scale root check failed")
    return value


def point_record(prime: int, order: int, point: tuple[int, int]) -> dict[str, Any]:
    if math.gcd(order, prime - 1) != 1:
        raise AssertionError("frozen V12 corpus violates gcd(n,p-1)=1")
    evaluator = DivisionPolynomialEvaluator(prime, 0, 7, point)
    a, b = ward_constants(evaluator, order)
    phi = raw_point_scale(prime, order, point)

    expected_b = pow(phi, -(order * order), prime)
    expected_a = pow(phi, -(2 * order), prime)
    if b != expected_b:
        raise AssertionError("Ward b != phi_raw^(-n^2)")
    if a != expected_a:
        raise AssertionError("Ward a != phi_raw^(-2n)")
    if pow(a, order, prime) != pow(b, 2, prime):
        raise AssertionError("Ward a^n=b^2 relation failed")

    inverse_n_squared = pow(order * order % (prime - 1), -1, prime - 1)
    recovered_phi = pow(b, -inverse_n_squared, prime)
    if recovered_phi != phi:
        raise AssertionError("phi_raw reconstruction from Ward b failed")

    chi_a = quadratic_character(a, prime)
    chi_b = quadratic_character(b, prime)
    chi_phi = quadratic_character(phi, prime)
    if chi_a != 1:
        raise AssertionError("Ward a must be a square for odd n")
    if chi_b != chi_phi:
        raise AssertionError("Ward b character must equal point-scale character")

    return {
        "chi_a": chi_a,
        "chi_b": chi_b,
        "chi_phi_raw": chi_phi,
        "a_power_identity": True,
        "b_power_identity": True,
        "a_n_equals_b_squared": True,
        "phi_recovered_from_b": True,
    }


def run(grammar_path: Path) -> dict[str, Any]:
    discovery, holdout = load_corpora(grammar_path)
    corpus = discovery + holdout
    total_points = 0
    curve_rows = []
    for prime, order, generator in corpus:
        if math.gcd(order, prime - 1) != 1:
            raise AssertionError("V12 transfer corpus contains noncoprime n,p-1")
        chi_a_values: set[int] = set()
        chi_b_values: set[int] = set()
        for k in range(1, order):
            point = ec_mul(k, generator, prime, 0)
            if point is None:
                raise AssertionError("nonzero subgroup point became infinity")
            row = point_record(prime, order, point)
            chi_a_values.add(int(row["chi_a"]))
            chi_b_values.add(int(row["chi_b"]))
            total_points += 1
        curve_rows.append(
            {
                "p": prime,
                "n": order,
                "points_checked": order - 1,
                "gcd_n_p_minus_one": math.gcd(order, prime - 1),
                "chi_a_values": sorted(chi_a_values),
                "chi_b_values": sorted(chi_b_values),
            }
        )

    secp_rows = []
    phi_g = raw_point_scale(SECP_P, SECP_N, SECP_G)
    psi_g = DivisionPolynomialEvaluator(SECP_P, 0, 7, SECP_G)
    for scalar in SECP_SAMPLES:
        point = ec_mul(scalar, SECP_G, SECP_P, 0)
        if point is None:
            raise AssertionError("fixed secp sample reached infinity")
        row = point_record(SECP_P, SECP_N, point)
        phi = raw_point_scale(SECP_P, SECP_N, point)
        w = psi_g.value(scalar)
        parity = -1 if scalar & 1 else 1
        bridge = quadratic_character(phi, SECP_P) * quadratic_character(w, SECP_P)
        if bridge != parity:
            raise AssertionError("secp EDS parity bridge drifted")
        row.update(
            {
                "scalar": str(scalar),
                "parity": parity,
                "chi_w_k": quadratic_character(w, SECP_P),
                "ward_b_times_eds_residue": row["chi_b"] * quadratic_character(w, SECP_P),
            }
        )
        if row["ward_b_times_eds_residue"] != parity:
            raise AssertionError("Ward-b bridge did not equal parity with hidden residue")
        secp_rows.append(row)

    return {
        "schema_version": "1.0",
        "profile_id": PROFILE_ID,
        "theorem": {
            "hypothesis": "P in E(F_p) has odd order n and gcd(n,p-1)=1",
            "ward_b": "b_P=phi_raw(P)^(-n^2)",
            "ward_a": "a_P=phi_raw(P)^(-2n)",
            "reconstruction": "phi_raw(P)=b_P^(-(n^2)^(-1) mod (p-1))",
            "characters": "chi(a_P)=+1 and chi(b_P)=chi(phi_raw(P))",
        },
        "frozen_corpus": {
            "curves": len(corpus),
            "points_checked": total_points,
            "rows": curve_rows,
        },
        "secp256k1": {
            "gcd_n_p_minus_one": math.gcd(SECP_N, SECP_P - 1),
            "chi_phi_raw_G": quadratic_character(phi_g, SECP_P),
            "fixed_samples": secp_rows,
            "interpretation": (
                "Ward b supplies exactly the public chi(phi_raw(Q)) factor; "
                "multiplication by the hidden chi(psi_k(G)) is still required for parity"
            ),
        },
        "decision": "ward_quasiperiod_constants_collapse_to_public_point_scale",
        "next_frontier": (
            "distinguished global orientation/seed propagation, not functions of Ward a_Q,b_Q alone"
        ),
        "scientific_boundary": (
            "V12 is an information-equivalence result for the classical Ward state, "
            "not a general circuit lower bound."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--grammar", type=Path, default=DEFAULT_GRAMMAR)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = stable_json(run(args.grammar))
    if args.check:
        if not args.out.exists() or args.out.read_text(encoding="utf-8") != text:
            raise SystemExit("V12 Ward point-scale artifact drift")
        print("UORC056_WARD_POINT_SCALE_COLLAPSE_OK")
        return 0
    args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
