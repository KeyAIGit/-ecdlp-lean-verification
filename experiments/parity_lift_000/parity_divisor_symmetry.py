#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

FROZEN_PRIMES = (31, 67, 127, 271, 397, 433, 1093)
SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
SECP_LAMBDA = 0x5363AD4CC05C30E0A5261C028812A417E8EF5B6D5F0B84D3A7A1E26F6A7A4B9B


def prime_factors(value: int) -> list[int]:
    factors: list[int] = []
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor == 0:
            factors.append(divisor)
            while value % divisor == 0:
                value //= divisor
        divisor = 3 if divisor == 2 else divisor + 2
    if value > 1:
        factors.append(value)
    return factors


def primitive_root(prime: int) -> int:
    factors = prime_factors(prime - 1)
    for candidate in range(2, prime):
        if all(pow(candidate, (prime - 1) // factor, prime) != 1 for factor in factors):
            return candidate
    raise AssertionError("primitive root not found")


def canonical_parity(value: int, prime: int) -> int:
    representative = value % prime
    if representative == 0:
        raise AssertionError("parity requested at zero")
    return representative & 1


def run_prime(prime: int) -> dict[str, object]:
    if prime % 6 != 1:
        raise AssertionError("prime must admit an order-three scalar")

    middle = (prime - 1) // 2
    even_set = {2 * index for index in range(1, middle + 1)}
    odd_set = set(range(1, prime)) - even_set
    if len(even_set) != middle or len(odd_set) != middle:
        raise AssertionError("parity set size failed")

    even_sum = sum(even_set) % prime
    expected_sum = middle * (middle + 1) % prime
    if even_sum != expected_sum:
        raise AssertionError("even sum formula failed")
    if 4 * even_sum % prime != prime - 1:
        raise AssertionError("even sum was not negative one quarter")

    preserving: list[int] = []
    swapping: list[int] = []
    for multiplier in range(1, prime):
        image = {multiplier * value % prime for value in even_set}
        if image == even_set:
            preserving.append(multiplier)
        if image == odd_set:
            swapping.append(multiplier)
    if preserving != [1]:
        raise AssertionError("unexpected parity stabilizer")
    if swapping != [prime - 1]:
        raise AssertionError("unexpected parity swapping set")

    root = primitive_root(prime)
    lam = pow(root, (prime - 1) // 3, prime)
    if lam in (1, prime - 1) or pow(lam, 3, prime) != 1:
        raise AssertionError("failed to construct nontrivial order-three scalar")
    if {lam * value % prime for value in even_set} in (even_set, odd_set):
        raise AssertionError("GLV unexpectedly preserved or swapped parity")

    visited: set[int] = set()
    orbit_results: list[dict[str, object]] = []
    lam2 = lam * lam % prime
    for scalar in range(1, prime):
        if scalar in visited:
            continue
        orbit6 = {
            scalar,
            prime - scalar,
            lam * scalar % prime,
            (-lam * scalar) % prime,
            lam2 * scalar % prime,
            (-lam2 * scalar) % prime,
        }
        if len(orbit6) != 6:
            raise AssertionError("C6 orbit was not free")
        visited.update(orbit6)
        even_count = sum(canonical_parity(member, prime) == 0 for member in orbit6)
        if even_count != 3:
            raise AssertionError("C6 parity balance failed")
        orbit_results.append(
            {
                "representative": min(orbit6),
                "even": even_count,
                "odd": 6 - even_count,
            }
        )

    if len(visited) != prime - 1:
        raise AssertionError("C6 orbits did not cover nonzero scalars")

    return {
        "prime": prime,
        "lambda": lam,
        "even_sum_mod_prime": even_sum,
        "preserving_multipliers": preserving,
        "swapping_multipliers": swapping,
        "c6_orbits": len(orbit_results),
        "all_c6_orbits_three_three": True,
        "glv_preserves_or_swaps": False,
    }


def secp_certificate() -> dict[str, object]:
    n = SECP_N
    lam = SECP_LAMBDA % n
    middle = (n - 1) // 2
    even_sum = middle * (middle + 1) % n
    if 4 * even_sum % n != n - 1:
        raise AssertionError("secp even-sum certificate failed")
    if pow(lam, 3, n) != 1 or lam in (1, n - 1):
        raise AssertionError("secp GLV scalar certificate failed")
    return {
        "n": n,
        "lambda": lam,
        "lambda_order_three": True,
        "lambda_not_plus_or_minus_one": True,
        "even_set_size": middle,
        "odd_set_size": middle,
        "even_sum_mod_n": even_sum,
        "four_times_even_sum_mod_n": 4 * even_sum % n,
        "parity_rational_degree_lower_bound": middle,
        "c6_orbit_count": (n - 1) // 6,
        "selected_successor": "ORIENTED-PARITY-DIVISOR-CIRCUIT-046",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("parity_divisor_symmetry_results.json"),
    )
    args = parser.parse_args()

    cases = [run_prime(prime) for prime in FROZEN_PRIMES]
    payload = {
        "package": "PARITY-DIVISOR-SYMMETRY-045",
        "cases": cases,
        "aggregate": {
            "cases": len(cases),
            "total_c6_orbits": sum(case["c6_orbits"] for case in cases),
            "all_preserving_sets_trivial": all(
                case["preserving_multipliers"] == [1] for case in cases
            ),
            "all_swapping_sets_negation": all(
                case["swapping_multipliers"] == [case["prime"] - 1] for case in cases
            ),
            "all_c6_orbits_three_three": all(
                case["all_c6_orbits_three_three"] for case in cases
            ),
            "all_glv_actions_mix_parity": all(
                not case["glv_preserves_or_swaps"] for case in cases
            ),
        },
        "secp256k1": secp_certificate(),
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["aggregate"], indent=2))
    print(json.dumps(payload["secp256k1"], indent=2))


if __name__ == "__main__":
    main()
