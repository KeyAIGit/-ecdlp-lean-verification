#!/usr/bin/env python3
"""Exact replay for the H-RPCX Fourier-support barrier V3."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


PROFILE_ID = "UORC-056-HRPCX-FOURIER-SUPPORT-BARRIER-V3"
TOY_ORDERS = (31, 79, 67, 127, 139)
SECP256K1_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def is_prime(value: int) -> bool:
    if value < 2:
        return False
    small_primes = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for prime in small_primes:
        if value == prime:
            return True
        if value % prime == 0:
            return False
    exponent = value - 1
    shift = 0
    while exponent % 2 == 0:
        exponent //= 2
        shift += 1
    for base in (2, 325, 9375, 28178, 450775, 9780504, 1795265022):
        if base % value == 0:
            continue
        witness = pow(base, exponent, value)
        if witness in (1, value - 1):
            continue
        for _ in range(shift - 1):
            witness = witness * witness % value
            if witness == value - 1:
                break
        else:
            return False
    return True


def prime_factors(value: int) -> list[int]:
    factors: list[int] = []
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor == 0:
            factors.append(divisor)
            while value % divisor == 0:
                value //= divisor
        divisor += 1 if divisor == 2 else 2
    if value > 1:
        factors.append(value)
    return factors


def splitting_prime(n: int) -> int:
    multiplier = 1
    while True:
        candidate = multiplier * n + 1
        if is_prime(candidate):
            return candidate
        multiplier += 1


def primitive_root(prime: int) -> int:
    factors = prime_factors(prime - 1)
    for candidate in range(2, prime):
        if all(pow(candidate, (prime - 1) // factor, prime) != 1 for factor in factors):
            return candidate
    raise AssertionError("primitive root not found")


def fourier_profile(n: int) -> dict[str, object]:
    prime = splitting_prime(n)
    generator = primitive_root(prime)
    zeta = pow(generator, (prime - 1) // n, prime)
    if pow(zeta, n, prime) != 1:
        raise AssertionError("root relation failed")
    if any(pow(zeta, divisor, prime) == 1 for divisor in range(1, n)):
        raise AssertionError("root is not primitive")

    coefficients: list[int] = []
    formula_checks = 0
    for frequency in range(n):
        zeta_inverse_frequency = pow(pow(zeta, frequency, prime), -1, prime)
        coefficient = 0
        power = 1
        for k in range(n):
            sign = 1 if k % 2 == 0 else prime - 1
            coefficient = (coefficient + sign * power) % prime
            power = power * zeta_inverse_frequency % prime
        denominator = (1 + zeta_inverse_frequency) % prime
        if denominator == 0:
            raise AssertionError("odd-order root unexpectedly equals -1")
        expected = 2 * pow(denominator, -1, prime) % prime
        if coefficient != expected:
            raise AssertionError((n, frequency, coefficient, expected))
        formula_checks += 1
        coefficients.append(coefficient)

    nonzero = sum(value != 0 for value in coefficients)
    if nonzero != n:
        raise AssertionError((n, "Fourier support defect", nonzero))
    return {
        "n": n,
        "splitting_prime": prime,
        "primitive_nth_root": zeta,
        "nonzero_fourier_coefficients": nonzero,
        "formula_checks": formula_checks,
        "full_support": True,
    }


def minimum_degree_for_mode_budget(mode_count: int, target_size: int) -> int:
    degree = 0
    while math.comb(mode_count + degree, degree) < target_size:
        degree += 1
    return degree


def run() -> dict[str, object]:
    profiles = [fourier_profile(n) for n in TOY_ORDERS]
    budgets = [
        {
            "mode_count": mode_count,
            "minimum_polynomial_degree_from_counting_bound": minimum_degree_for_mode_budget(
                mode_count, SECP256K1_N
            ),
        }
        for mode_count in (1, 2, 3, 4, 8, 16, 32, 64, 128, 256, 512, 1024)
    ]
    return {
        "profile_id": PROFILE_ID,
        "theorem": {
            "parity_fourier_support": "all n frequencies",
            "decoder_support_bound": "at most binomial(r+d,d)",
            "necessary_condition": "binomial(r+d,d) >= n",
        },
        "toy_profiles": profiles,
        "secp256k1_budget_table": budgets,
        "aggregate": {
            "orders": len(profiles),
            "frequencies_checked": sum(profile["formula_checks"] for profile in profiles),
            "support_defects": sum(not profile["full_support"] for profile in profiles),
        },
        "decision": {
            "constant_mode_constant_degree_decoder_can_scale": False,
            "necessary_binomial_budget_enforced": True,
            "polylog_degree_decoder_refuted_in_full_generality": False,
            "nonlinear_non_spectral_state_open": True,
            "high_formal_degree_low_circuit_open": True,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = run()
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
