#!/usr/bin/env python3
"""Exact toy replay for DUAL-ORBIT-QUADRATIC-RESOLVENT-034.

The package studies two exact ways to expose the quadratic character of the
unknown scalar k in Q=[k]G:

1. a product over the quadratic-residue dual C3 orbit;
2. a public-line elliptic Gauss projector

       S_f(P) = sum_(a=1..n-1) chi_n(a) f([a]P).

For f(P)=x(P)^3 on the frozen j=0 family with n == 1 (mod 12), the projector
is compatible with negation and the GLV C3 action.  Reindexing gives the exact
identity

       S_f([k]G) = chi_n(k) S_f(G).

The direct replay costs Theta(n) point-function values and is not a
sub-square-root algorithm.  No external point, key, wallet, or production-sized
discrete-log target is accepted.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from nonlocal_odd_anchor_screen import FROZEN_CASES, orbit, primitive_cube_root

SECP256K1_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def quadratic_character(value: int, prime: int) -> int:
    value %= prime
    if value == 0:
        return 0
    result = pow(value, (prime - 1) // 2, prime)
    if result == 1:
        return 1
    if result == prime - 1:
        return -1
    raise AssertionError("Euler criterion returned a non-binary value")


def is_prime(value: int) -> bool:
    if value < 2:
        return False
    if value % 2 == 0:
        return value == 2
    divisor = 3
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += 2
    return True


def auxiliary_root_of_unity(order: int) -> tuple[int, int, int]:
    """Return q,z,m with q=m*order+1 prime and z of exact order order."""
    for multiplier in range(2, 5000):
        auxiliary_prime = multiplier * order + 1
        if not is_prime(auxiliary_prime):
            continue
        for seed in range(2, min(auxiliary_prime, 2000)):
            root = pow(seed, multiplier, auxiliary_prime)
            if root != 1 and pow(root, order, auxiliary_prime) == 1:
                # order is prime on every retained frozen case.
                return auxiliary_prime, root, multiplier
    raise AssertionError("no small auxiliary prime carrying mu_n was found")


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
        raise AssertionError("lambda failed 1+lambda+lambda^2=0")
    return beta, lam


def product(values: list[int], modulus: int) -> int:
    result = 1
    for value in values:
        result = result * value % modulus
    return result


def run_case(
    field_prime: int, order: int, generator: tuple[int, int]
) -> dict[str, object]:
    if order % 12 != 1:
        return {
            "p": field_prime,
            "order": order,
            "generator": generator,
            "status": "excluded_order_not_1_mod_12",
        }

    beta, lam = scalar_lambda(field_prime, order, generator)
    lam2 = lam * lam % order
    if quadratic_character(-1, order) != 1:
        raise AssertionError("-1 was not square modulo the subgroup order")
    if quadratic_character(lam, order) != 1:
        raise AssertionError("the order-three GLV scalar was not square")

    points = orbit(generator, order, field_prime)
    scalar_character = [0] + [
        quadratic_character(scalar, order) for scalar in range(1, order)
    ]
    x_powers: dict[int, list[int]] = {}
    for exponent in (1, 2, 3, 6):
        x_powers[exponent] = [0] + [
            pow(points[scalar][0], exponent, field_prime)
            for scalar in range(1, order)
        ]

    # The GLV reindexing forces powers x^j to vanish unless 3 divides j.
    weighted_power_sums = {
        exponent: sum(
            scalar_character[scalar] * x_powers[exponent][scalar]
            for scalar in range(1, order)
        )
        % field_prime
        for exponent in x_powers
    }
    if weighted_power_sums[1] != 0 or weighted_power_sums[2] != 0:
        raise AssertionError("non-C3-invariant coordinate powers did not vanish")

    base_projector = weighted_power_sums[3]
    if base_projector == 0:
        raise AssertionError("the frozen x^3 Gauss projector vanished")

    projector_checks = 0
    for hidden_scalar in range(1, order):
        projected = sum(
            scalar_character[weight]
            * x_powers[3][weight * hidden_scalar % order]
            for weight in range(1, order)
        ) % field_prime
        expected = scalar_character[hidden_scalar] * base_projector % field_prime
        if projected != expected:
            raise AssertionError("elliptic Gauss projector reindexing failed")
        projector_checks += 1

    # Exact multiplicative two-orbit resolvent in an auxiliary field carrying
    # a primitive n-th root.  This validates the exponent-set identity without
    # claiming that the auxiliary representation is efficient at secp scale.
    auxiliary_prime, root, multiplier = auxiliary_root_of_unity(order)
    residues = [
        scalar for scalar in range(1, order)
        if scalar_character[scalar] == 1
    ]
    nonresidues = [
        scalar for scalar in range(1, order)
        if scalar_character[scalar] == -1
    ]
    if len(residues) != (order - 1) // 2 or len(nonresidues) != (order - 1) // 2:
        raise AssertionError("quadratic classes had wrong cardinality")

    residue_product = product(
        [(1 - pow(root, scalar, auxiliary_prime)) % auxiliary_prime
         for scalar in residues],
        auxiliary_prime,
    )
    nonresidue_product = product(
        [(1 - pow(root, scalar, auxiliary_prime)) % auxiliary_prime
         for scalar in nonresidues],
        auxiliary_prime,
    )
    if residue_product == 0 or nonresidue_product == 0:
        raise AssertionError("quadratic cyclotomic product vanished")
    if residue_product * nonresidue_product % auxiliary_prime != order % auxiliary_prime:
        raise AssertionError("Phi_n(1)=n product identity failed")

    nonresidue_constant = (
        nonresidue_product * pow(residue_product, -1, auxiliary_prime)
    ) % auxiliary_prime
    if nonresidue_constant == 1:
        raise AssertionError("the two quadratic-orbit values collapsed")

    orbit_product_checks = 0
    qr_set = set(residues)
    nqr_set = set(nonresidues)
    for hidden_scalar in range(1, order):
        image = {hidden_scalar * scalar % order for scalar in residues}
        expected_set = qr_set if scalar_character[hidden_scalar] == 1 else nqr_set
        if image != expected_set:
            raise AssertionError("quadratic orbit was not mapped to the expected class")
        orbit_product_checks += 1

    # C3 invariance of x^3 and of the scalar character.
    c3_checks = 0
    for scalar in range(1, order):
        if scalar_character[lam * scalar % order] != scalar_character[scalar]:
            raise AssertionError("scalar character was not C3 invariant")
        if x_powers[3][lam * scalar % order] != x_powers[3][scalar]:
            raise AssertionError("x^3 was not C3 invariant")
        if x_powers[3][order - scalar] != x_powers[3][scalar]:
            raise AssertionError("x^3 was not negation invariant")
        c3_checks += 1

    return {
        "p": field_prime,
        "order": order,
        "generator": generator,
        "status": "screened",
        "beta": beta,
        "lambda": lam,
        "lambda_squared": lam2,
        "weighted_x_power_sums": {
            str(exponent): value for exponent, value in weighted_power_sums.items()
        },
        "x3_projector_nonzero": base_projector != 0,
        "x3_projector_at_generator": base_projector,
        "projector_reindex_checks": projector_checks,
        "quadratic_orbit_mapping_checks": orbit_product_checks,
        "c3_and_negation_checks": c3_checks,
        "auxiliary_prime": auxiliary_prime,
        "auxiliary_multiplier": multiplier,
        "auxiliary_root": root,
        "quadratic_residue_product": residue_product,
        "quadratic_nonresidue_product": nonresidue_product,
        "nonresidue_orbit_constant": nonresidue_constant,
        "two_orbit_values_distinct": nonresidue_constant != 1,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "dual_orbit_quadratic_resolvent_results.json"
        ),
    )
    args = parser.parse_args()

    cases = [run_case(p, order, generator) for p, order, generator in FROZEN_CASES]
    screened = [row for row in cases if row["status"] == "screened"]
    secp_n = SECP256K1_N
    payload = {
        "package": "DUAL-ORBIT-QUADRATIC-RESOLVENT-034",
        "scope": (
            "exact quadratic-orbit and public-line projector identities on "
            "frozen toy j=0 subgroups; no external point, key, wallet, or "
            "production-sized discrete-log target"
        ),
        "cases": cases,
        "secp256k1": {
            "order": secp_n,
            "order_mod_12": secp_n % 12,
            "quadratic_class_size": (secp_n - 1) // 2,
            "quadratic_c3_orbits": (secp_n - 1) // 6,
            "quadratic_c6_orbits": (secp_n - 1) // 12,
        },
        "aggregate": {
            "cases": len(cases),
            "screened_cases": len(screened),
            "excluded_cases": len(cases) - len(screened),
            "all_x3_projectors_nonzero": all(
                bool(row["x3_projector_nonzero"]) for row in screened
            ),
            "all_lower_glv_incompatible_power_sums_zero": all(
                row["weighted_x_power_sums"]["1"] == 0
                and row["weighted_x_power_sums"]["2"] == 0
                for row in screened
            ),
            "all_two_orbit_values_distinct": all(
                bool(row["two_orbit_values_distinct"]) for row in screened
            ),
            "total_projector_reindex_checks": sum(
                int(row["projector_reindex_checks"]) for row in screened
            ),
            "total_quadratic_orbit_mapping_checks": sum(
                int(row["quadratic_orbit_mapping_checks"]) for row in screened
            ),
            "total_c3_and_negation_checks": sum(
                int(row["c3_and_negation_checks"]) for row in screened
            ),
        },
        "decision": (
            "The quadratic dual-orbit product is exactly two-valued and exposes "
            "the scalar Legendre class. More constructively, the public-line "
            "x^3 elliptic Gauss projector satisfies S([k]G)=chi_n(k)S(G) and "
            "is nonzero on every retained frozen n=1 mod 12 case. Direct "
            "evaluation costs Theta(n); no classical sub-square-root carry, "
            "R3, parity, or full-ECDLP algorithm is obtained."
        ),
        "claim_boundary": [
            "Nonvanishing of the x^3 projector is frozen-family evidence, not a secp256k1 theorem.",
            "The reindexing identity is exact whenever the base projector is defined.",
            "The auxiliary cyclotomic field validates exponent-set products only and is not an efficient secp representation.",
            "A scalar Legendre oracle is negation-even and is not itself the GLV carry oracle.",
            "No external key or production-sized discrete-log instance is processed.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
