#!/usr/bin/env python3
"""Exact toy replay for ELLIPTIC-GAUSS-PROJECTOR-035.

For the retained j=0 groups with n == 1 (mod 12), the C6-invariant coordinate
z(P)=x(P)^3 splits the nonzero subgroup into quadratic-residue and
nonresidue root sets.  The weighted projector

    S_3(G)=sum_a chi_n(a) z([a]G)

is six times the difference of their first power sums.  Under generator change
G -> [u]G the two factors are preserved or swapped according to chi_n(u), so
S_3 changes by that character while S_3^2 is generator-blind.

The script validates exact finite-field identities only on frozen toy groups.
It constructs no public sub-square-root decoder and accepts no external point,
key, wallet, or production-sized target.
"""
from __future__ import annotations

import argparse
import json
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


def scalar_lambda(
    field_prime: int, order: int, generator: tuple[int, int]
) -> tuple[int, int]:
    points = orbit(generator, order, field_prime)
    beta = primitive_cube_root(field_prime)
    point_to_scalar = {point: scalar for scalar, point in enumerate(points)}
    lam = point_to_scalar[(beta * generator[0] % field_prime, generator[1])]
    if lam in (0, 1) or pow(lam, 3, order) != 1:
        raise AssertionError("invalid GLV eigenvalue")
    return beta, lam


def polynomial_from_roots(roots: list[int], modulus: int) -> list[int]:
    """Ascending coefficients of the monic product of (X-root)."""
    coefficients = [1]
    for root in roots:
        updated = [0] * (len(coefficients) + 1)
        for index, coefficient in enumerate(coefficients):
            updated[index] = (updated[index] - root * coefficient) % modulus
            updated[index + 1] = (updated[index + 1] + coefficient) % modulus
        coefficients = updated
    return coefficients


def polynomial_multiply(left: list[int], right: list[int], modulus: int) -> list[int]:
    result = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] = (result[i + j] + a * b) % modulus
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
    points = orbit(generator, order, field_prime)
    character = [0] + [
        quadratic_character(scalar, order) for scalar in range(1, order)
    ]
    c6 = {
        1,
        lam,
        lam2,
        order - 1,
        (-lam) % order,
        (-lam2) % order,
    }
    if len(c6) != 6:
        raise AssertionError("C6 had wrong size")
    if any(character[unit] != 1 for unit in c6):
        raise AssertionError("C6 was not contained in the square subgroup")

    visited: set[int] = set()
    residue_roots: list[int] = []
    nonresidue_roots: list[int] = []
    orbit_checks = 0
    scalar_to_root: dict[int, int] = {}
    for scalar in range(1, order):
        if scalar in visited:
            continue
        orbit6 = {scalar * unit % order for unit in c6}
        if len(orbit6) != 6:
            raise AssertionError("nonzero C6 orbit had wrong size")
        visited.update(orbit6)
        root = pow(points[scalar][0], 3, field_prime)
        for member in orbit6:
            if pow(points[member][0], 3, field_prime) != root:
                raise AssertionError("x^3 changed inside a C6 orbit")
            if character[member] != character[scalar]:
                raise AssertionError("quadratic class changed inside a C6 orbit")
            scalar_to_root[member] = root
            orbit_checks += 1
        if character[scalar] == 1:
            residue_roots.append(root)
        else:
            nonresidue_roots.append(root)

    expected_factor_degree = (order - 1) // 12
    if len(residue_roots) != expected_factor_degree:
        raise AssertionError("quadratic-residue factor had wrong degree")
    if len(nonresidue_roots) != expected_factor_degree:
        raise AssertionError("nonresidue factor had wrong degree")
    if set(residue_roots) & set(nonresidue_roots):
        raise AssertionError("quadratic factors shared a root")

    direct_projector = sum(
        character[scalar] * scalar_to_root[scalar]
        for scalar in range(1, order)
    ) % field_prime
    factor_projector = (
        6 * (sum(residue_roots) - sum(nonresidue_roots))
    ) % field_prime
    if direct_projector != factor_projector:
        raise AssertionError("factor coefficient did not reproduce S_3")
    if direct_projector == 0:
        raise AssertionError("frozen S_3 projector vanished")

    residue_factor = polynomial_from_roots(residue_roots, field_prime)
    nonresidue_factor = polynomial_from_roots(nonresidue_roots, field_prime)
    full_factor = polynomial_multiply(
        residue_factor, nonresidue_factor, field_prime
    )
    all_factor = polynomial_from_roots(
        residue_roots + nonresidue_roots, field_prime
    )
    if full_factor != all_factor:
        raise AssertionError("oriented factors did not multiply to the full factor")

    residue_root_sum = (-residue_factor[-2]) % field_prime
    nonresidue_root_sum = (-nonresidue_factor[-2]) % field_prime
    if 6 * (residue_root_sum - nonresidue_root_sum) % field_prime != direct_projector:
        raise AssertionError("first factor coefficients lost the projector")

    generator_change_checks = 0
    square_invariance_checks = 0
    qr_set = set(residue_roots)
    nqr_set = set(nonresidue_roots)
    base_square = direct_projector * direct_projector % field_prime
    for multiplier in range(1, order):
        mapped_qr = {
            scalar_to_root[multiplier * scalar % order]
            for scalar in range(1, order)
            if character[scalar] == 1
        }
        expected = qr_set if character[multiplier] == 1 else nqr_set
        if mapped_qr != expected:
            raise AssertionError("generator change did not preserve/swap factors")

        changed_projector = character[multiplier] * direct_projector % field_prime
        if changed_projector * changed_projector % field_prime != base_square:
            raise AssertionError("projector square was not generator-blind")
        generator_change_checks += 1
        square_invariance_checks += 1

    # Newton's identities imply that two distinct monic degree-d factors must
    # differ in one of the first d power sums.  The replay records the first
    # differing power; on this frozen family it is always the first one.
    first_differing_power = None
    for exponent in range(1, expected_factor_degree + 1):
        left = sum(pow(root, exponent, field_prime) for root in residue_roots) % field_prime
        right = sum(pow(root, exponent, field_prime) for root in nonresidue_roots) % field_prime
        if left != right:
            first_differing_power = exponent
            break
    if first_differing_power is None:
        raise AssertionError("distinct factors had all power sums equal")

    return {
        "p": field_prime,
        "order": order,
        "generator": generator,
        "status": "screened",
        "beta": beta,
        "lambda": lam,
        "c6_orbits": (order - 1) // 6,
        "oriented_factor_degree": expected_factor_degree,
        "residue_factor_coefficient_degree_minus_one": residue_factor[-2],
        "nonresidue_factor_coefficient_degree_minus_one": nonresidue_factor[-2],
        "projector": direct_projector,
        "projector_square": base_square,
        "first_differing_power": first_differing_power,
        "full_factor_degree": len(full_factor) - 1,
        "c6_orbit_checks": orbit_checks,
        "generator_change_checks": generator_change_checks,
        "square_invariance_checks": square_invariance_checks,
        "minimum_c6_invariant_polynomial_decoder_degree": expected_factor_degree,
        "minimum_curve_rational_decoder_degree": (order - 1) // 2,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("elliptic_gauss_projector_results.json"),
    )
    args = parser.parse_args()

    cases = [run_case(p, order, generator) for p, order, generator in FROZEN_CASES]
    screened = [row for row in cases if row["status"] == "screened"]
    n = SECP256K1_N
    payload = {
        "package": "ELLIPTIC-GAUSS-PROJECTOR-035",
        "scope": (
            "exact generator-change, factor-coefficient, and square-collapse "
            "identities on frozen toy j=0 subgroups; no external target"
        ),
        "cases": cases,
        "secp256k1": {
            "order": n,
            "c6_orbits": (n - 1) // 6,
            "quadratic_oriented_factor_degree": (n - 1) // 12,
            "bounded_rational_decoder_degree_lower_bound": (n - 1) // 2,
        },
        "aggregate": {
            "cases": len(cases),
            "screened_cases": len(screened),
            "excluded_cases": len(cases) - len(screened),
            "all_projectors_nonzero": all(int(row["projector"]) != 0 for row in screened),
            "all_first_differing_powers_equal_one": all(
                int(row["first_differing_power"]) == 1 for row in screened
            ),
            "total_c6_orbit_checks": sum(
                int(row["c6_orbit_checks"]) for row in screened
            ),
            "total_generator_change_checks": sum(
                int(row["generator_change_checks"]) for row in screened
            ),
            "total_square_invariance_checks": sum(
                int(row["square_invariance_checks"]) for row in screened
            ),
        },
        "decision": (
            "S_3 is the first coefficient separating the generator-oriented "
            "quadratic-residue and nonresidue C6 factors. Its square is "
            "generator-blind, matching the standard quadratic elliptic-Gauss "
            "invariant. Any exact bounded-degree C6-invariant polynomial "
            "decoder needs degree at least (n-1)/12, and any bounded-degree "
            "curve rational decoder needs degree at least (n-1)/2. These are "
            "representation-degree obstructions, not arithmetic-circuit lower "
            "bounds. No sub-square-root decoder is obtained."
        ),
        "claim_boundary": [
            "The rational-function degree lower bound does not exclude compact high-degree straight-line programs.",
            "Frozen nonvanishing is not a secp256k1 nonvanishing theorem.",
            "Standard universal elliptic-Gauss invariants may compute a square while losing the generator-oriented sign.",
            "No external key or production-sized discrete-log instance is processed.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
