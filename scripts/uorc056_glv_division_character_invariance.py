#!/usr/bin/env python3
"""Exact public replay for UORC-056 GLV division-character invariance V13.

For E:y^2=x^3+7 and alpha(x,y)=(beta*x,y), beta^3=1, the classical division
polynomials obey

    psi_m(alpha(Q)) = beta * psi_m(Q)  if 3|m,
                      psi_m(Q)         otherwise.

Because beta is itself a square, every quadratic-character atom is invariant.
The script verifies the all-index recurrence weight rule, public secp GLV
pairing, representative low/high division-polynomial indices, point-scale
covariance, and sample multiplicative monomials.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from uorc056_division_polynomial_frontier import (
    DivisionPolynomialEvaluator,
    ec_mul,
    quadratic_character,
    stable_json,
)
from uorc056_ward_point_scale_collapse import raw_point_scale

PROFILE_ID = "UORC-056-GLV-DIVISION-CHARACTER-INVARIANCE-V13"
DEFAULT_OUTPUT = Path("experiments/uorc056/glv_division_character_invariance_results.json")

P = int("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F", 16)
N = int("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141", 16)
G = (
    int("79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798", 16),
    int("483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8", 16),
)
BETA = int("7AE96A2B657C07106E64479EAC3434E99CF0497512F58995C1396C28719501EE", 16)
LAMBDA = int("5363AD4CC05C30E0A5261C028812645A122E22EA20816678DF02967C1B23BD72", 16)
SAMPLES = (1, 2, 3, 7, 11, 123456789, N - 2, N - 1)


def alpha(point: tuple[int, int]) -> tuple[int, int]:
    return BETA * point[0] % P, point[1]


def cm_weight(index: int) -> int:
    return 1 if index % 3 == 0 else 0


def verify_weight_recurrence() -> dict[str, Any]:
    """Verify the mod-3 induction identities for all residue classes."""
    odd_cases = []
    even_cases = []
    for rmod in range(3):
        # choose a positive representative preserving the residue class
        r = rmod + 6
        m_odd = 2 * r + 1
        left_1 = (cm_weight(r + 2) + 3 * cm_weight(r)) % 3
        left_2 = (cm_weight(r - 1) + 3 * cm_weight(r + 1)) % 3
        target = cm_weight(m_odd)
        if left_1 != target or left_2 != target:
            raise AssertionError("odd recurrence CM weight failed")
        odd_cases.append(
            {"r_mod_3": rmod, "term1_weight": left_1, "term2_weight": left_2, "target": target}
        )

        m_even = 2 * r
        inner_1 = (cm_weight(r + 2) + 2 * cm_weight(r - 1)) % 3
        inner_2 = (cm_weight(r - 2) + 2 * cm_weight(r + 1)) % 3
        total_1 = (cm_weight(r) + inner_1) % 3
        total_2 = (cm_weight(r) + inner_2) % 3
        target_even = cm_weight(m_even)
        if total_1 != target_even or total_2 != target_even:
            raise AssertionError("even recurrence CM weight failed")
        even_cases.append(
            {"r_mod_3": rmod, "term1_weight": total_1, "term2_weight": total_2, "target": target_even}
        )
    return {"odd_residue_cases": odd_cases, "even_residue_cases": even_cases}


def division_scaling_record(point: tuple[int, int], indices: tuple[int, ...]) -> dict[str, Any]:
    transformed = alpha(point)
    left_eval = DivisionPolynomialEvaluator(P, 0, 7, point)
    right_eval = DivisionPolynomialEvaluator(P, 0, 7, transformed)
    rows = []
    for index in indices:
        left = left_eval.value(index)
        right = right_eval.value(index)
        expected = left * (BETA if index % 3 == 0 else 1) % P
        if right != expected:
            raise AssertionError(f"division-polynomial GLV scaling failed at m={index}")
        chi_left = quadratic_character(left, P)
        chi_right = quadratic_character(right, P)
        if left and chi_left != chi_right:
            raise AssertionError("quadratic-character GLV invariance failed")
        rows.append(
            {
                "index": str(index),
                "divisible_by_3": index % 3 == 0,
                "field_scaling_exact": True,
                "character_invariant": left == 0 or chi_left == chi_right,
                "zero": left == 0,
            }
        )
    return {"rows": rows}


def monomial_character(point: tuple[int, int], factors: tuple[tuple[int, int, int], ...]) -> int:
    value = 1
    for index, scalar, exponent in factors:
        pulled = ec_mul(scalar % N, point, P, 0)
        if pulled is None:
            raise AssertionError("public scalar pullback reached infinity")
        factor = DivisionPolynomialEvaluator(P, 0, 7, pulled).value(index)
        if factor == 0:
            raise AssertionError("sample monomial factor vanished")
        if exponent >= 0:
            value = value * pow(factor, exponent, P) % P
        else:
            value = value * pow(pow(factor, -1, P), -exponent, P) % P
    return quadratic_character(value, P)


def run() -> dict[str, Any]:
    if pow(BETA, 3, P) != 1 or BETA == 1:
        raise AssertionError("public beta is not a nontrivial cube root")
    if pow(BETA * BETA % P, 2, P) != BETA:
        raise AssertionError("beta square witness failed")
    if quadratic_character(BETA, P) != 1:
        raise AssertionError("beta must be a quadratic residue")
    if (LAMBDA * LAMBDA + LAMBDA + 1) % N != 0:
        raise AssertionError("public lambda is not a cube root modulo n")
    if not (0 < LAMBDA < N) or LAMBDA % 2 != 0:
        raise AssertionError("public lambda parity/range certificate failed")

    alpha_g = alpha(G)
    lambda_g = ec_mul(LAMBDA, G, P, 0)
    if lambda_g != alpha_g:
        raise AssertionError("public beta/lambda GLV pairing failed on G")

    weight_recurrence = verify_weight_recurrence()
    M = (N - 1) // 2
    indices = (1, 2, 3, 4, 5, 6, 7, 8, 11, 17, M - 1, M, M + 1, N - 2, N - 1, N + 1)
    sample_rows = []
    for scalar in SAMPLES:
        point = ec_mul(scalar, G, P, 0)
        if point is None:
            raise AssertionError("fixed public sample reached infinity")
        if alpha(point) != ec_mul(LAMBDA, point, P, 0):
            raise AssertionError("GLV pairing failed on a fixed sample")
        scaling = division_scaling_record(point, indices)
        phi = raw_point_scale(P, N, point)
        phi_alpha = raw_point_scale(P, N, alpha(point))
        if phi_alpha != BETA * phi % P:
            raise AssertionError("point-scale GLV covariance failed")
        if quadratic_character(phi_alpha, P) != quadratic_character(phi, P):
            raise AssertionError("point-scale character must be GLV invariant")
        sample_rows.append(
            {
                "scalar": str(scalar),
                "division_rows": scaling["rows"],
                "phi_raw_scales_by_beta": True,
                "phi_raw_character_invariant": True,
            }
        )

    monomial_factors = (
        (M, 2, 1),
        (M + 1, 3, -1),
        (17, 5, 2),
        (6, 7, 1),
    )
    monomial_rows = []
    for scalar in SAMPLES[:5]:
        point = ec_mul(scalar, G, P, 0)
        assert point is not None
        left = monomial_character(point, monomial_factors)
        right = monomial_character(alpha(point), monomial_factors)
        if left != right:
            raise AssertionError("sample multiplicative monomial was not GLV invariant")
        monomial_rows.append({"scalar": str(scalar), "character": left, "invariant": True})

    parity_g = -1
    parity_lambda_g = 1 if LAMBDA % 2 == 0 else -1
    if parity_g == parity_lambda_g:
        raise AssertionError("parity target unexpectedly GLV invariant on G")

    return {
        "schema_version": "1.0",
        "profile_id": PROFILE_ID,
        "public_certificates": {
            "beta_cube_root": True,
            "beta_square_witness": "(beta^2)^2=beta mod p",
            "chi_beta": quadratic_character(BETA, P),
            "lambda_cube_root_mod_n": True,
            "lambda_even": True,
            "alpha_G_equals_lambda_G": True,
        },
        "all_index_cm_weight_induction": weight_recurrence,
        "fixed_secp_samples": sample_rows,
        "multiplicative_monomial_replay": {
            "factors": [
                {"index": str(i), "pullback_scalar": str(s), "exponent": e}
                for i, s, e in monomial_factors
            ],
            "rows": monomial_rows,
        },
        "target_mismatch": {
            "sigma_G_G": parity_g,
            "sigma_G_alpha_G": parity_lambda_g,
            "reason": "alpha(G)=[lambda]G and the canonical lambda representative is even",
        },
        "decision": "all_multiplicative_division_polynomial_character_monomials_are_glv_invariant_and_cannot_equal_secp_parity",
        "scope": {
            "closed": [
                "chi(psi_m([s]Q)) for arbitrary public m,s",
                "finite products and quotients of such character atoms",
                "one outer quadratic character applied to any multiplicative monomial of these factors",
                "products of chi(phi_raw([s]Q)) at arbitrary public scalar pullbacks",
            ],
            "open": [
                "additive mixtures of different CM weights before the final decision",
                "direct field-valued Y_G evaluation",
                "oriented Pell/Miller global integration",
                "theta or elliptic-unit formulas with nontrivial GLV covariance",
            ],
        },
        "scientific_boundary": "V13 is a representation-class GLV no-go, not a general arithmetic-circuit lower bound.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = stable_json(run())
    if args.check:
        if not args.out.exists() or args.out.read_text(encoding="utf-8") != text:
            raise SystemExit("V13 GLV division-character artifact drift")
        print("UORC056_GLV_DIVISION_CHARACTER_INVARIANCE_OK")
        return 0
    args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
