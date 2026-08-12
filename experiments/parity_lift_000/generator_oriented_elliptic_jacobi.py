#!/usr/bin/env python3
"""Exact toy replay for GENERATOR-ORIENTED-ELLIPTIC-JACOBI-037.

For a secp256k1-style j=0 subgroup with v_3(n-1)=1, let psi be the
GLV-adapted sextic scalar character from package 036. Put

    c = psi^4       (cubic component),
    q = psi^3       (quadratic component),

and define the three public-line character projectors

    T(P) = sum_a psi(a) x([a]P),
    C(P) = sum_a c(a)   x([a]P),
    S(P) = sum_a q(a)   x([a]P)^3.

For Q=[k]G they satisfy

    T(Q) = psi(k)^(-1) T(G),
    C(Q) = c(k)^(-1)   C(G),
    S(Q) = q(k)^(-1)   S(G).

Hence

    T(Q)^3 / T(G)^3 = q(k),
    T(P)^3 / S(P) is generator-blind,
    C(P) S(P) / T(P) is generator-blind.

The latter two identities are the exact obstruction behind the standard
elliptic-Jacobi route: balancing the total character creates a modular
invariant, but it cancels precisely the generator-oriented quadratic bit.

The script verifies these identities on the frozen toy groups satisfying the
same v_3(n-1)=1 branch as secp256k1. Direct projector evaluation is Theta(n).
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
SECP256K1_LAMBDA = 0x5363AD4CC05C30E0A5261C028812645A122E22EA20816678DF02967C1B23BD72
SECP256K1_GLV_A = 0x3086D221A7D46BCDE86C90E49284EB15
SECP256K1_GLV_B = -0xE4437ED6010E88286F547FA90ABFE4C3


def factor_distinct(value: int) -> list[int]:
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
    factors = factor_distinct(prime - 1)
    for candidate in range(2, prime):
        if all(pow(candidate, (prime - 1) // factor, prime) != 1 for factor in factors):
            return candidate
    raise AssertionError("primitive root was not found")


def discrete_log_table(generator: int, prime: int) -> dict[int, int]:
    result: dict[int, int] = {}
    value = 1
    for exponent in range(prime - 1):
        if value in result:
            raise AssertionError("generator repeated before exhausting the unit group")
        result[value] = exponent
        value = value * generator % prime
    if value != 1 or len(result) != prime - 1:
        raise AssertionError("discrete-log table did not cover the unit group")
    return result


def valuation(value: int, prime: int) -> int:
    exponent = 0
    while value % prime == 0:
        exponent += 1
        value //= prime
    return exponent


def scalar_lambda(
    field_prime: int, order: int, generator: tuple[int, int]
) -> tuple[int, int, list[tuple[int, int] | None]]:
    points = orbit(generator, order, field_prime)
    beta = primitive_cube_root(field_prime)
    point_to_scalar = {point: scalar for scalar, point in enumerate(points)}
    lam = point_to_scalar[(beta * generator[0] % field_prime, generator[1])]
    if lam in (0, 1) or pow(lam, 3, order) != 1:
        raise AssertionError("invalid GLV eigenvalue")
    if (1 + lam + lam * lam) % order != 0:
        raise AssertionError("lambda failed its cyclotomic equation")
    return beta, lam, points


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

    v3 = valuation(order - 1, 3)
    beta, lam, points = scalar_lambda(field_prime, order, generator)
    if v3 != 1:
        return {
            "p": field_prime,
            "order": order,
            "generator": generator,
            "status": "excluded_wrong_3_primary_branch",
            "v3_order_minus_one": v3,
            "beta": beta,
            "lambda": lam,
        }

    scalar_generator = primitive_root(order)
    scalar_logs = discrete_log_table(scalar_generator, order)
    field_generator = primitive_root(field_prime)
    zeta6 = pow(field_generator, (field_prime - 1) // 6, field_prime)
    target_glv_phase = pow(beta, 2, field_prime)

    matching = [
        exponent
        for exponent in (1, 5)
        if pow(zeta6, exponent * scalar_logs[lam], field_prime)
        == target_glv_phase
    ]
    if len(matching) != 1:
        raise AssertionError("unique GLV-adapted sextic character was not found")
    character_exponent = matching[0]

    psi = [0] + [
        pow(zeta6, character_exponent * scalar_logs[scalar], field_prime)
        for scalar in range(1, order)
    ]
    cubic = [0] + [
        pow(psi[scalar], 4, field_prime) for scalar in range(1, order)
    ]
    quadratic = [0] + [
        pow(psi[scalar], 3, field_prime) for scalar in range(1, order)
    ]

    for scalar in range(1, order):
        if psi[scalar] != cubic[scalar] * quadratic[scalar] % field_prime:
            raise AssertionError("psi did not split into cubic and quadratic parts")
        if pow(psi[scalar], 3, field_prime) != quadratic[scalar]:
            raise AssertionError("psi^3 did not equal the quadratic component")

    def projector(
        point_scalar: int, character: list[int], x_power: int
    ) -> int:
        return sum(
            character[weight]
            * pow(points[weight * point_scalar % order][0], x_power, field_prime)
            for weight in range(1, order)
        ) % field_prime

    base_t = projector(1, psi, 1)
    base_c = projector(1, cubic, 1)
    base_s = projector(1, quadratic, 3)
    if base_t == 0 or base_c == 0 or base_s == 0:
        raise AssertionError("a frozen base projector vanished")

    base_oriented_cube = pow(base_t, 3, field_prime)
    cube_over_quadratic = (
        base_oriented_cube * pow(base_s, -1, field_prime) % field_prime
    )
    mixed_jacobi = (
        base_c * base_s % field_prime * pow(base_t, -1, field_prime) % field_prime
    )
    sextic_invariant = pow(base_t, 6, field_prime)
    cubic_invariant = pow(base_c, 3, field_prime)
    quadratic_invariant = pow(base_s, 2, field_prime)

    scaling_checks = 0
    oriented_cube_checks = 0
    cube_over_quadratic_checks = 0
    mixed_jacobi_checks = 0
    invariant_power_checks = 0
    generator_orientation_checks = 0

    for hidden_scalar in range(1, order):
        observed_t = projector(hidden_scalar, psi, 1)
        observed_c = projector(hidden_scalar, cubic, 1)
        observed_s = projector(hidden_scalar, quadratic, 3)

        expected_t = (
            base_t * pow(psi[hidden_scalar], -1, field_prime) % field_prime
        )
        expected_c = (
            base_c * pow(cubic[hidden_scalar], -1, field_prime) % field_prime
        )
        expected_s = (
            base_s * pow(quadratic[hidden_scalar], -1, field_prime) % field_prime
        )
        if (observed_t, observed_c, observed_s) != (
            expected_t,
            expected_c,
            expected_s,
        ):
            raise AssertionError("character-projector scaling law failed")
        scaling_checks += 1

        normalized_cube = (
            pow(observed_t, 3, field_prime)
            * pow(base_oriented_cube, -1, field_prime)
            % field_prime
        )
        if normalized_cube != quadratic[hidden_scalar]:
            raise AssertionError("oriented cube lost the scalar quadratic character")
        oriented_cube_checks += 1

        observed_cube_over_quadratic = (
            pow(observed_t, 3, field_prime)
            * pow(observed_s, -1, field_prime)
            % field_prime
        )
        if observed_cube_over_quadratic != cube_over_quadratic:
            raise AssertionError("T^3/S was not generator-blind")
        cube_over_quadratic_checks += 1

        observed_mixed_jacobi = (
            observed_c
            * observed_s
            % field_prime
            * pow(observed_t, -1, field_prime)
            % field_prime
        )
        if observed_mixed_jacobi != mixed_jacobi:
            raise AssertionError("balanced mixed Jacobi ratio was not invariant")
        mixed_jacobi_checks += 1

        if (
            pow(observed_t, 6, field_prime) != sextic_invariant
            or pow(observed_c, 3, field_prime) != cubic_invariant
            or pow(observed_s, 2, field_prime) != quadratic_invariant
        ):
            raise AssertionError("an invariant character power changed with the generator")
        invariant_power_checks += 1

        expected_oriented_cube = (
            quadratic[hidden_scalar] * base_oriented_cube % field_prime
        )
        if pow(observed_t, 3, field_prime) != expected_oriented_cube:
            raise AssertionError("generator-oriented cube transformation failed")
        generator_orientation_checks += 1

    return {
        "p": field_prime,
        "order": order,
        "generator": generator,
        "status": "screened",
        "v3_order_minus_one": v3,
        "beta": beta,
        "lambda": lam,
        "scalar_primitive_root": scalar_generator,
        "field_primitive_root": field_generator,
        "zeta6": zeta6,
        "character_exponent": character_exponent,
        "psi_lambda": psi[lam],
        "cubic_lambda": cubic[lam],
        "quadratic_lambda": quadratic[lam],
        "base_sextic_projector": base_t,
        "base_cubic_projector": base_c,
        "base_quadratic_projector": base_s,
        "base_oriented_cube": base_oriented_cube,
        "cube_over_quadratic_invariant": cube_over_quadratic,
        "mixed_jacobi_invariant": mixed_jacobi,
        "scaling_checks": scaling_checks,
        "oriented_cube_checks": oriented_cube_checks,
        "cube_over_quadratic_checks": cube_over_quadratic_checks,
        "mixed_jacobi_checks": mixed_jacobi_checks,
        "invariant_power_checks": invariant_power_checks,
        "generator_orientation_checks": generator_orientation_checks,
        "direct_terms_per_projector": order - 1,
    }


def secp256k1_certificate() -> dict[str, object]:
    n = SECP256K1_N
    p = SECP256K1_P
    lam = SECP256K1_LAMBDA
    a = SECP256K1_GLV_A
    b = SECP256K1_GLV_B
    norm = a * a - a * b + b * b
    if norm != n:
        raise AssertionError("Eisenstein norm representation did not equal n")
    if (a + b * lam) % n != 0:
        raise AssertionError("public GLV lattice vector did not annihilate lambda")
    if valuation(n - 1, 3) != 1:
        raise AssertionError("secp256k1 did not have v3(n-1)=1")
    if n % 9 != 7 or n % 12 != 1:
        raise AssertionError("unexpected secp256k1 congruence class")

    level_degree = (n - 1) // math.gcd(n - 1, 12)
    strict_square_root = math.isqrt(n)
    if strict_square_root * strict_square_root < n:
        strict_square_root += 1

    return {
        "p": p,
        "n": n,
        "n_mod_9": n % 9,
        "n_mod_12": n % 12,
        "v3_n_minus_one": valuation(n - 1, 3),
        "lambda": lam,
        "eisenstein_a": a,
        "eisenstein_b": b,
        "eisenstein_norm": norm,
        "annihilator_residue": (a + b * lam) % n,
        "direct_projector_terms": n - 1,
        "c6_orbit_terms": (n - 1) // 6,
        "quadratic_oriented_factor_degree": (n - 1) // 12,
        "generic_gamma0_level_degree": level_degree,
        "ceil_sqrt_n": strict_square_root,
        "direct_term_count_exceeds_sqrt_by_factor_floor": (n - 1) // strict_square_root,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "generator_oriented_elliptic_jacobi_results.json"
        ),
    )
    args = parser.parse_args()

    cases = [run_case(p, order, generator) for p, order, generator in FROZEN_CASES]
    screened = [row for row in cases if row["status"] == "screened"]
    wrong_3 = [
        row for row in cases
        if row["status"] == "excluded_wrong_3_primary_branch"
    ]

    payload = {
        "package": "GENERATOR-ORIENTED-ELLIPTIC-JACOBI-037",
        "scope": (
            "exact character-projector and balanced-Jacobi identities on frozen "
            "toy j=0 subgroups plus public secp256k1 arithmetic; no external target"
        ),
        "cases": cases,
        "secp256k1": secp256k1_certificate(),
        "aggregate": {
            "cases": len(cases),
            "screened_cases": len(screened),
            "wrong_3_primary_exclusions": len(wrong_3),
            "other_exclusions": len(cases) - len(screened) - len(wrong_3),
            "all_base_projectors_nonzero": all(
                int(row["base_sextic_projector"]) != 0
                and int(row["base_cubic_projector"]) != 0
                and int(row["base_quadratic_projector"]) != 0
                for row in screened
            ),
            "total_scaling_checks": sum(
                int(row["scaling_checks"]) for row in screened
            ),
            "total_oriented_cube_checks": sum(
                int(row["oriented_cube_checks"]) for row in screened
            ),
            "total_cube_over_quadratic_checks": sum(
                int(row["cube_over_quadratic_checks"]) for row in screened
            ),
            "total_mixed_jacobi_checks": sum(
                int(row["mixed_jacobi_checks"]) for row in screened
            ),
            "total_invariant_power_checks": sum(
                int(row["invariant_power_checks"]) for row in screened
            ),
            "total_generator_orientation_checks": sum(
                int(row["generator_orientation_checks"]) for row in screened
            ),
        },
        "decision": (
            "The oriented cube T_psi(P)^3 carries exactly the scalar Legendre "
            "character. However, T_psi(P)^3/S_3(P) and the balanced mixed "
            "Jacobi quotient C(P)S_3(P)/T_psi(P) are generator-blind. Thus "
            "standard character-balanced Jacobi/CM normalization can compress "
            "only invariant data; the full quadratic orientation remains in "
            "the original quadratic projector S_3. Direct evaluation is Theta(n), "
            "and no public o(sqrt(n)) evaluator is obtained."
        ),
        "claim_boundary": [
            "The mixed quotient is an exact character-balanced analogue, not an identification with every universal elliptic Jacobi sum in the literature.",
            "Frozen nonvanishing of all three projectors is not a secp256k1 nonvanishing theorem.",
            "Asai's canonical cubic CM formulas concern cubic-character sums with special elliptic functions; no equality with this x-weighted sextic projector is assumed.",
            "Representation-degree and published modular-computation costs are not universal arithmetic-circuit lower bounds.",
            "No public carry, parity, hard-R3, shifted-Legendre, or ECDLP algorithm is constructed.",
            "No external key or production-sized discrete-log target is processed.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
