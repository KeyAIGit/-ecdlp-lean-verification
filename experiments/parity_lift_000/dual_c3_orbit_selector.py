#!/usr/bin/env python3
"""Exact arithmetic replay for DUAL-C3-ORBIT-SELECTOR-033.

The script works only with the frozen toy j=0 subgroups and the public curve
parameters of secp256k1. It verifies the Frobenius action on the abstract dual
scalar line, its quotient by the GLV unit group C6, and the exact extension
degrees required to define a point, a C3 orbit, or a plus/minus-C3 orbit.

No external point, key, wallet, or production-sized discrete-log target is
accepted.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from nonlocal_odd_anchor_screen import FROZEN_CASES, orbit, primitive_cube_root

SECP256K1_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
SECP256K1_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
SECP_D_FACTORIZATION = {
    2: 5,
    149: 1,
    631: 1,
    107361793816595537: 1,
    174723607534414371449: 1,
    341948486974166000522343609283189: 1,
}


def factor_small(value: int) -> dict[int, int]:
    result: dict[int, int] = {}
    divisor = 2
    while divisor * divisor <= value:
        while value % divisor == 0:
            result[divisor] = result.get(divisor, 0) + 1
            value //= divisor
        divisor = 3 if divisor == 2 else divisor + 2
    if value > 1:
        result[value] = result.get(value, 0) + 1
    return result


def multiplicative_order(value: int, modulus: int, factors: dict[int, int]) -> int:
    value %= modulus
    if math.gcd(value, modulus) != 1:
        raise ValueError("value was not a unit")
    order = modulus - 1
    for prime, exponent in factors.items():
        for _ in range(exponent):
            candidate = order // prime
            if pow(value, candidate, modulus) != 1:
                break
            order = candidate
    if pow(value, order, modulus) != 1:
        raise AssertionError("multiplicative-order certificate failed")
    return order


def scalar_lambda(
    field_prime: int, order: int, generator: tuple[int, int]
) -> tuple[int, int]:
    points = orbit(generator, order, field_prime)
    beta = primitive_cube_root(field_prime)
    point_to_scalar = {point: scalar for scalar, point in enumerate(points)}
    lam = point_to_scalar[(beta * generator[0] % field_prime, generator[1])]
    if lam in (0, 1) or pow(lam, 3, order) != 1:
        raise AssertionError("invalid GLV eigenvalue")
    if (1 + lam + lam * lam) % order != 0:
        raise AssertionError("lambda failed its cyclotomic equation")
    return beta, lam


def c3_and_c6(order: int, lam: int) -> tuple[set[int], set[int]]:
    c3 = {1, lam, lam * lam % order}
    c6 = c3 | {(-value) % order for value in c3}
    if len(c3) != 3 or len(c6) != 6:
        raise AssertionError("GLV unit group had wrong size")
    return c3, c6


def subgroup_generated(value: int, modulus: int, order: int) -> set[int]:
    result: set[int] = set()
    current = 1
    for _ in range(order):
        if current in result:
            raise AssertionError("subgroup repeated too early")
        result.add(current)
        current = current * value % modulus
    if current != 1 or len(result) != order:
        raise AssertionError("subgroup order mismatch")
    return result


def least_power_in_set(value: int, modulus: int, target: set[int], order: int) -> int:
    current = 1
    for exponent in range(1, order + 1):
        current = current * value % modulus
        if current in target:
            return exponent
    raise AssertionError("power orbit never met target")


def quotient_classes(order: int, c6: set[int]) -> list[frozenset[int]]:
    visited: set[int] = set()
    result: list[frozenset[int]] = []
    for scalar in range(1, order):
        if scalar in visited:
            continue
        cls = frozenset(scalar * unit % order for unit in c6)
        if len(cls) != 6:
            raise AssertionError("C6 quotient class had wrong size")
        visited.update(cls)
        result.append(cls)
    if len(visited) != order - 1:
        raise AssertionError("C6 classes did not partition units")
    return result


def quotient_frobenius_orbits(
    order: int, frobenius_scalar: int, classes: list[frozenset[int]]
) -> list[list[frozenset[int]]]:
    class_of: dict[int, frozenset[int]] = {}
    for cls in classes:
        for value in cls:
            class_of[value] = cls
    remaining = set(classes)
    result: list[list[frozenset[int]]] = []
    while remaining:
        start = next(iter(remaining))
        orbit_classes: list[frozenset[int]] = []
        current = start
        while current not in orbit_classes:
            orbit_classes.append(current)
            representative = next(iter(current))
            current = class_of[frobenius_scalar * representative % order]
        if current != start:
            raise AssertionError("quotient orbit did not close at its start")
        remaining.difference_update(orbit_classes)
        result.append(orbit_classes)
    return result


def run_toy_case(
    field_prime: int, order: int, generator: tuple[int, int]
) -> dict[str, object]:
    if math.gcd(order, field_prime * (field_prime - 1)) != 1:
        return {
            "p": field_prime,
            "order": order,
            "generator": generator,
            "status": "excluded_non_etale_or_non_distinct_frobenius",
        }

    beta, lam = scalar_lambda(field_prime, order, generator)
    c3, c6 = c3_and_c6(order, lam)
    factors = factor_small(order - 1)
    frobenius_scalar = field_prime % order
    point_degree = multiplicative_order(frobenius_scalar, order, factors)
    frobenius_subgroup = subgroup_generated(frobenius_scalar, order, point_degree)
    c3_degree = least_power_in_set(
        frobenius_scalar, order, c3, point_degree
    )
    c6_degree = least_power_in_set(
        frobenius_scalar, order, c6, point_degree
    )

    classes = quotient_classes(order, c6)
    quotient_orbits = quotient_frobenius_orbits(
        order, frobenius_scalar, classes
    )
    orbit_sizes = sorted(len(item) for item in quotient_orbits)
    if any(size != c6_degree for size in orbit_sizes):
        raise AssertionError("quotient orbit size disagreed with least power")

    square_subgroup = {
        scalar * scalar % order for scalar in range(1, order)
    }
    generated_with_units = {
        value * unit % order for value in frobenius_subgroup for unit in c6
    }

    return {
        "p": field_prime,
        "order": order,
        "generator": generator,
        "status": "screened",
        "beta": beta,
        "lambda": lam,
        "frobenius_scalar": frobenius_scalar,
        "point_field_degree": point_degree,
        "c3_orbit_field_degree": c3_degree,
        "pm_c3_orbit_field_degree": c6_degree,
        "c6_quotient_classes": len(classes),
        "frobenius_orbits_on_c6_quotient": len(quotient_orbits),
        "frobenius_quotient_orbit_sizes": orbit_sizes,
        "frobenius_intersection_c3": len(frobenius_subgroup & c3),
        "frobenius_intersection_c6": len(frobenius_subgroup & c6),
        "generated_with_c6_equals_squares": generated_with_units == square_subgroup,
    }


def secp256k1_certificate() -> dict[str, object]:
    n = SECP256K1_N
    p = SECP256K1_P
    d = (n - 1) // 6
    if math.prod(prime**exponent for prime, exponent in SECP_D_FACTORIZATION.items()) != d:
        raise AssertionError("hard-coded factorization did not multiply to d")
    order = multiplicative_order(p, n, {
        prime: exponent for prime, exponent in factor_small(6).items()
    } | SECP_D_FACTORIZATION)
    # multiplicative_order above expects a factorization of n-1, not d.
    # Verify the exact d certificate directly to avoid depending on dictionary
    # merging when the factor 2 appears in both 6 and d.
    if pow(p, d, n) != 1:
        raise AssertionError("p^d != 1")
    for prime in SECP_D_FACTORIZATION:
        if pow(p, d // prime, n) == 1:
            raise AssertionError("d was not the exact order")
    order = d

    half = d // 2
    if pow(p, half, n) != n - 1:
        raise AssertionError("half-Frobenius was not -1")
    if d % 6 != 4:
        raise AssertionError("unexpected d modulo 6")
    if n % 12 != 1:
        raise AssertionError("unexpected n modulo 12")
    if pow(p, (n - 1) // 2, n) != 1:
        raise AssertionError("p was not a square modulo n")

    point_orbits = (n - 1) // d
    quotient_classes_count = (n - 1) // 6
    quotient_orbit_size = half
    quotient_orbits = quotient_classes_count // quotient_orbit_size
    if point_orbits != 6 or quotient_orbits != 2:
        raise AssertionError("secp orbit count mismatch")

    return {
        "p": p,
        "n": n,
        "d_factorization": {
            str(prime): exponent for prime, exponent in SECP_D_FACTORIZATION.items()
        },
        "frobenius_order": order,
        "point_field_degree": d,
        "c3_orbit_field_degree": d,
        "pm_c3_orbit_field_degree": half,
        "nonzero_point_frobenius_orbits": point_orbits,
        "c6_quotient_classes": quotient_classes_count,
        "frobenius_orbits_on_c6_quotient": quotient_orbits,
        "frobenius_quotient_orbit_size": quotient_orbit_size,
        "half_frobenius": n - 1,
        "d_mod_6": d % 6,
        "n_mod_12": n % 12,
        "frobenius_times_c6_is_square_subgroup": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("dual_c3_orbit_selector_results.json"),
    )
    args = parser.parse_args()

    cases = [run_toy_case(p, order, generator) for p, order, generator in FROZEN_CASES]
    screened = [row for row in cases if row["status"] == "screened"]
    secp = secp256k1_certificate()

    payload = {
        "package": "DUAL-C3-ORBIT-SELECTOR-033",
        "scope": (
            "exact scalar-line Frobenius/C6 orbit arithmetic on frozen toy "
            "subgroups and public secp256k1 parameters; no external target"
        ),
        "cases": cases,
        "secp256k1": secp,
        "aggregate": {
            "cases": len(cases),
            "screened_cases": len(screened),
            "excluded_cases": len(cases) - len(screened),
            "all_quotient_orbit_sizes_match": all(
                all(
                    size == row["pm_c3_orbit_field_degree"]
                    for size in row["frobenius_quotient_orbit_sizes"]
                )
                for row in screened
            ),
            "toy_cases_where_frobenius_c6_equals_squares": sum(
                bool(row["generated_with_c6_equals_squares"])
                for row in screened
            ),
        },
        "decision": (
            "Frobenius canonically identifies the complementary eigendirection "
            "but not a distinguished faithful dual C6 class. For secp256k1 a "
            "nonzero dual point needs degree (n-1)/6, an unordered C6 orbit "
            "needs degree (n-1)/12, and Frobenius leaves two large quotient "
            "orbits corresponding to square and nonsquare scalar classes."
        ),
        "claim_boundary": [
            "The scalar-line replay assumes the standard ordinary Frobenius eigenspace decomposition.",
            "Field-of-definition degree is not a universal arithmetic-circuit lower bound.",
            "The two-orbit square/nonsquare collapse is not a carry decoder.",
            "No external key or production-sized discrete-log instance is processed.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
