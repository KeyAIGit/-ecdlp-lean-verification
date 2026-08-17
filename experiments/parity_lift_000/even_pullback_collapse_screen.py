#!/usr/bin/env python3
"""Frozen toy replay for EVEN-PULLBACK-COLLAPSE-001.

For every nonzero scalar k and every even invertible m on five frozen
prime-order toy curves, verify

    chi(psi_m([m^{-1}] [k]G)) = chi(phi_raw([k]G)).

The program accepts no external curves, keys, wallets, or production-sized
instances.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

from kummer_residue_toy_screen import raw_point_scale
from structured_char_parity_screen import (
    FROZEN_CURVES,
    division_polynomial_evaluator,
    orbit,
    quadratic_character,
)


@dataclass(frozen=True)
class CurveResult:
    p: int
    order: int
    generator: tuple[int, int]
    chi_phi_raw_g: int
    even_indices: int
    nonzero_scalars: int
    carry_parity_checks: int
    division_pullback_checks: int
    all_checks_passed: bool


def run_curve(p: int, order: int, generator: tuple[int, int]) -> CurveResult:
    if order % 2 == 0:
        raise AssertionError("the frozen order must be odd")

    points = orbit(generator, order, p)
    psi_g = division_polynomial_evaluator(generator, p)
    chi_phi_raw_g = quadratic_character(raw_point_scale(generator, p, order), p)

    public_point_function_char: dict[int, int] = {}
    rho: dict[int, int] = {}
    for k in range(1, order):
        point = points[k]
        assert point is not None
        public_point_function_char[k] = quadratic_character(
            raw_point_scale(point, p, order), p
        )
        rho[k] = quadratic_character(psi_g(k), p)
        expected = (chi_phi_raw_g if k & 1 else 1) * rho[k]
        if public_point_function_char[k] != expected:
            raise AssertionError("raw point-function parity bridge failed")

    carry_checks = 0
    pullback_checks = 0
    even_indices = 0

    for m in range(2, order, 2):
        if math.gcd(m, order) != 1:
            continue
        even_indices += 1
        inverse_m = pow(m, -1, order)

        for k in range(1, order):
            j = inverse_m * k % order
            if j == 0:
                raise AssertionError("nonzero k pulled back to the identity")

            carry_numerator = m * j - k
            if carry_numerator < 0 or carry_numerator % order:
                raise AssertionError("invalid canonical carry decomposition")
            carry = carry_numerator // order
            if carry % 2 != k % 2:
                raise AssertionError("even-pullback carry parity failed")
            carry_checks += 1

            point = points[j]
            assert point is not None
            value = division_polynomial_evaluator(point, p)(m)
            pullback_character = quadratic_character(value, p)
            if pullback_character != public_point_function_char[k]:
                raise AssertionError("even-pullback collapse identity failed")
            pullback_checks += 1

    return CurveResult(
        p=p,
        order=order,
        generator=generator,
        chi_phi_raw_g=chi_phi_raw_g,
        even_indices=even_indices,
        nonzero_scalars=order - 1,
        carry_parity_checks=carry_checks,
        division_pullback_checks=pullback_checks,
        all_checks_passed=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("even_pullback_collapse_results.json"),
    )
    args = parser.parse_args()

    results = [run_curve(*curve) for curve in FROZEN_CURVES]
    payload = {
        "scope": "five frozen prime-order toy curves y^2=x^3+7 only",
        "identity": (
            "chi(psi_m([m^(-1)]Q))=chi(phi_raw(Q)) for every even invertible m"
        ),
        "curves": [asdict(result) for result in results],
        "aggregate": {
            "all_checks_passed": all(result.all_checks_passed for result in results),
            "carry_parity_checks": sum(
                result.carry_parity_checks for result in results
            ),
            "division_pullback_checks": sum(
                result.division_pullback_checks for result in results
            ),
        },
        "claim_boundary": [
            "This replay checks a derived identity on frozen toy curves; it is not an asymptotic theorem.",
            "The identity returns the already-public point-function character, not rho_G or scalar parity separately.",
            "No external curve, public key, wallet, or production-sized target is accepted.",
            "The result does not close odd-index, nonlocal, p-adic, or unbalanced theta/elliptic-net constructions.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
