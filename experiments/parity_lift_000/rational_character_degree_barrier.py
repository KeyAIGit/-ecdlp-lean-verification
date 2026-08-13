#!/usr/bin/env python3
"""Frozen replay for RATIONAL-CHARACTER-DEGREE-BARRIER-036.

This script verifies the exact j=1 Fourier coefficient of the scalar GLV carry
on the fifteen frozen toy subgroups and evaluates the source-pinned rational
function degree lower bound

    n*|g_hat(1)| <= 2*degree*sqrt(p) + 1.

The character-sum inequality itself is not reproved by the script.  It is the
external Kummer-covering input from Shparlinski--Stange, Lemmas 4--5.

No external point, key, wallet, or production-sized target is accepted.  The
secp256k1 block uses fixed public integer parameters only and does not enumerate
the subgroup.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import mpmath as mp

from nonlocal_odd_anchor_screen import FROZEN_CASES, orbit, primitive_cube_root

mp.mp.dps = 100

SECP256K1_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
SECP256K1_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
SECP256K1_LAMBDA = 0x5363AD4CC05C30E0A5261C028812645A122E22EA20816678DF02967C1B23BD72
TOLERANCE = mp.mpf("1e-70")


def carry_sign(k: int, lam: int, order: int) -> int:
    k %= order
    if k == 0:
        return 0
    lam2 = lam * lam % order
    total = k + lam * k % order + lam2 * k % order
    if total == order:
        return -1
    if total == 2 * order:
        return 1
    raise AssertionError("canonical GLV representatives did not sum to n or 2n")


def scalar_lambda(p: int, order: int, generator: tuple[int, int]) -> tuple[int, int]:
    points = orbit(generator, order, p)
    beta = primitive_cube_root(p)
    point_to_scalar = {point: scalar for scalar, point in enumerate(points)}
    lam = point_to_scalar[(beta * generator[0] % p, generator[1])]
    if lam in (0, 1) or pow(lam, 3, order) != 1:
        raise AssertionError("invalid GLV eigenvalue")
    if (lam * lam + lam + 1) % order:
        raise AssertionError("lambda is not a root of X^2+X+1")
    return beta, lam


def carry_fourier_one(order: int, lam: int) -> mp.mpc:
    total = mp.mpc(0)
    for k in range(order):
        total += carry_sign(k, lam, order) * mp.e ** (
            -2j * mp.pi * mp.mpf(k) / order
        )
    return total / order


def cot_formula(order: int, lam: int) -> mp.mpc:
    lam2 = lam * lam % order
    value = (
        mp.cot(mp.pi / order)
        + mp.cot(mp.pi * lam / order)
        + mp.cot(mp.pi * lam2 / order)
    )
    return 1j * value / order


def degree_lower_from_coefficient(p: int, order: int, coefficient: mp.mpf) -> mp.mpf:
    return (mp.mpf(order) * coefficient - 1) / (2 * mp.sqrt(p))


def run_case(p: int, order: int, generator: tuple[int, int]) -> dict[str, object]:
    beta, lam = scalar_lambda(p, order, generator)
    lam2 = lam * lam % order
    if 1 + lam + lam2 != order:
        raise AssertionError("j=1 GLV angles do not sum to pi")

    direct = carry_fourier_one(order, lam)
    formula = cot_formula(order, lam)
    residual = abs(direct - formula)
    if residual > TOLERANCE:
        raise AssertionError("direct Fourier coefficient disagrees with cot formula")

    coefficient = abs(formula)
    cot_only = mp.cot(mp.pi / order) / order
    if not coefficient > cot_only:
        raise AssertionError("heavy coefficient did not dominate cot(pi/n)/n")
    if order >= 5 and not coefficient > 1 / (2 * mp.pi):
        raise AssertionError("uniform heavy coefficient lower bound failed")

    exact_degree_lower = degree_lower_from_coefficient(p, order, coefficient)
    conservative_degree_lower = (
        mp.mpf(order) / (2 * mp.pi) - 1
    ) / (2 * mp.sqrt(p))

    return {
        "p": p,
        "order": order,
        "generator": generator,
        "beta": beta,
        "lambda": lam,
        "lambda2": lam2,
        "angle_sum_multiple": (1 + lam + lam2) // order,
        "fourier_coefficient_abs": mp.nstr(coefficient, 50),
        "cot_only_lower": mp.nstr(cot_only, 50),
        "direct_formula_residual": mp.nstr(residual, 10),
        "degree_lower_exact_coefficient": mp.nstr(exact_degree_lower, 50),
        "degree_lower_uniform_coefficient": mp.nstr(conservative_degree_lower, 50),
    }


def secp_block() -> dict[str, object]:
    p, n, lam = SECP256K1_P, SECP256K1_N, SECP256K1_LAMBDA
    lam2 = lam * lam % n
    if (lam2 + lam + 1) % n or 1 + lam + lam2 != n:
        raise AssertionError("fixed secp256k1 lambda arithmetic failed")

    coefficient = abs(cot_formula(n, lam))
    exact_degree_lower = degree_lower_from_coefficient(p, n, coefficient)
    conservative_degree_lower = (
        mp.mpf(n) / (2 * mp.pi) - 1
    ) / (2 * mp.sqrt(p))
    quotient_degree_lower = (exact_degree_lower - 3) / 6

    return {
        "p": p,
        "order": n,
        "lambda": lam,
        "lambda2": lam2,
        "lambda_angle_sum_is_n": 1 + lam + lam2 == n,
        "fourier_coefficient_abs": mp.nstr(coefficient, 80),
        "one_over_pi": mp.nstr(1 / mp.pi, 80),
        "coefficient_minus_one_over_pi": mp.nstr(coefficient - 1 / mp.pi, 30),
        "degree_lower_exact_coefficient": mp.nstr(exact_degree_lower, 80),
        "degree_lower_exact_log2": mp.nstr(mp.log(exact_degree_lower, 2), 50),
        "degree_lower_uniform_coefficient": mp.nstr(conservative_degree_lower, 80),
        "degree_lower_uniform_log2": mp.nstr(
            mp.log(conservative_degree_lower, 2), 50
        ),
        "quotient_R_degree_lower": mp.nstr(quotient_degree_lower, 80),
        "quotient_R_degree_lower_log2": mp.nstr(
            mp.log(quotient_degree_lower, 2), 50
        ),
        "secp_subgroup_enumerated": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "rational_character_degree_barrier_results.json"
        ),
    )
    args = parser.parse_args()

    cases = [run_case(p, order, generator) for p, order, generator in FROZEN_CASES]
    secp = secp_block()

    payload = {
        "package": "RATIONAL-CHARACTER-DEGREE-BARRIER-036",
        "scope": (
            "frozen toy carry Fourier replay plus fixed-public secp256k1 "
            "numerical specialization; no external point or production target"
        ),
        "external_input": {
            "source": (
                "Shparlinski--Stange, Character Sums with Division Polynomials, "
                "Lemmas 4--5, arXiv:0912.5246"
            ),
            "bound": "|sum omega(P) eta(f(P))| <= 2*degree(f)*sqrt(p)",
            "premise": "geometrically non-power rational function; poles excluded",
        },
        "cases": cases,
        "aggregate": {
            "cases": len(cases),
            "total_fourier_formula_checks": len(cases),
            "all_angle_sums_equal_pi": all(
                row["angle_sum_multiple"] == 1 for row in cases
            ),
            "maximum_direct_formula_residual": max(
                row["direct_formula_residual"] for row in cases
            ),
            "minimum_fourier_coefficient_abs": mp.nstr(
                min(mp.mpf(row["fourier_coefficient_abs"]) for row in cases), 50
            ),
            "all_uniform_one_over_two_pi_bounds": all(
                mp.mpf(row["fourier_coefficient_abs"]) > 1 / (2 * mp.pi)
                for row in cases
            ),
        },
        "secp256k1": secp,
        "decision": (
            "An exact geometrically non-power rational-character carry decoder "
            "must have elliptic-function degree above 2^125.34 on secp256k1. "
            "This closes low-degree coordinate and explicit divisor-section "
            "mechanisms, but not high-degree low-size nonlinear circuits."
        ),
        "claim_boundary": [
            "The external Kummer-covering character-sum theorem is source-pinned, not reproved here.",
            "The result is a rational-map degree lower bound, not an arithmetic-circuit lower bound.",
            "Proper-power candidates require reduction to an admissible geometrically non-power representative.",
            "The secp256k1 subgroup is not enumerated.",
        ],
    }

    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
