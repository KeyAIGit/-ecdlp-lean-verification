#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

FROZEN_PRIMES = (31, 67, 127, 271, 397, 433)
SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def divisors(value: int) -> list[int]:
    result: list[int] = []
    for candidate in range(1, math.isqrt(value) + 1):
        if value % candidate == 0:
            result.append(candidate)
            if candidate * candidate != value:
                result.append(value // candidate)
    return sorted(result)


def indicator(prime: int, modulus: int, residue: int) -> list[int]:
    return [1 if value % modulus == residue else 0 for value in range(prime)]


def minimal_cyclic_period(values: list[int]) -> int:
    length = len(values)
    for period in divisors(length):
        if all(values[index] == values[(index + period) % length] for index in range(length)):
            return period
    raise AssertionError("cyclic period not found")


def run_prime(prime: int) -> dict[str, object]:
    if prime < 5:
        raise AssertionError("prime too small")

    class_results: list[dict[str, object]] = []
    frequency_checks = 0
    period_checks = 0
    degree_checks = 0

    depth = 1
    while 1 << depth < prime:
        modulus = 1 << depth
        degree_lower_bound = (prime - 1 + modulus - 1) // modulus
        if modulus * degree_lower_bound < prime - 1:
            raise AssertionError("degree product certificate failed")
        degree_checks += 1

        for residue in range(modulus):
            values = indicator(prime, modulus, residue)
            support = [index for index, value in enumerate(values) if value]
            expected_support = list(range(residue, prime, modulus))
            if support != expected_support:
                raise AssertionError("residue support was not the expected progression")

            length = len(support)
            if length <= 0 or length >= prime:
                raise AssertionError("invalid progression length")

            # Exact nonvanishing conditions for the geometric-series Fourier
            # formula. For every nonzero frequency j, both j*m and j*m*L are
            # nonzero modulo the prime.
            for frequency in range(1, prime):
                if frequency * modulus % prime == 0:
                    raise AssertionError("Fourier denominator vanished")
                if frequency * modulus * length % prime == 0:
                    raise AssertionError("Fourier numerator vanished")
                frequency_checks += 1

            period = minimal_cyclic_period(values)
            if period != prime:
                raise AssertionError("dyadic indicator did not have full cyclic period")
            period_checks += 1

            class_results.append(
                {
                    "depth": depth,
                    "modulus": modulus,
                    "residue": residue,
                    "support_size": length,
                    "degree_lower_bound": degree_lower_bound,
                    "fourier_support_size": prime,
                    "minimal_cyclic_period": period,
                }
            )
        depth += 1

    return {
        "prime": prime,
        "classes": class_results,
        "class_count": len(class_results),
        "frequency_nonvanishing_checks": frequency_checks,
        "full_period_checks": period_checks,
        "degree_product_checks": degree_checks,
    }


def secp_certificate() -> dict[str, object]:
    n = SECP_N
    rows = []
    for depth in (1, 64, 96, 128):
        modulus = 1 << depth
        lower_bound = (n - 1 + modulus - 1) // modulus
        rows.append(
            {
                "depth": depth,
                "dyadic_classes": modulus,
                "rational_degree_lower_bound": lower_bound,
                "product": modulus * lower_bound,
                "degree_bits": math.log2(lower_bound),
            }
        )
        if modulus * lower_bound < n - 1:
            raise AssertionError("secp degree certificate failed")

    return {
        "n": n,
        "bit_length": n.bit_length(),
        "ceil_sqrt_n": math.isqrt(n - 1) + 1,
        "translation_linear_dimension_lower_bound": n,
        "rows": rows,
        "selected_successor": "PARITY-DIVISOR-SYMMETRY-045",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("nonlinear_dyadic_selector_results.json"),
    )
    args = parser.parse_args()

    cases = [run_prime(prime) for prime in FROZEN_PRIMES]
    payload = {
        "package": "NONLINEAR-DYADIC-SELECTOR-044",
        "cases": cases,
        "aggregate": {
            "cases": len(cases),
            "total_classes": sum(case["class_count"] for case in cases),
            "total_frequency_nonvanishing_checks": sum(
                case["frequency_nonvanishing_checks"] for case in cases
            ),
            "total_full_period_checks": sum(case["full_period_checks"] for case in cases),
            "total_degree_product_checks": sum(case["degree_product_checks"] for case in cases),
            "all_fourier_supports_full": True,
            "all_cyclic_periods_full": True,
            "all_degree_tradeoffs_passed": True,
        },
        "secp256k1": secp_certificate(),
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["aggregate"], indent=2))
    print(json.dumps(payload["secp256k1"], indent=2))


if __name__ == "__main__":
    main()
