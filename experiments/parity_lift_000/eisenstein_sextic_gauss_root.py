#!/usr/bin/env python3
"""Exact toy replay for EISENSTEIN-SEXTIC-GAUSS-ROOT-036.

On a secp256k1-style prime-order j=0 subgroup with v_3(n-1)=1, choose a
sextic scalar character psi whose restriction to the order-three GLV subgroup
cancels the x-coordinate eigenphase. Define

    T_psi(P) = sum_(a=1..n-1) psi(a) x([a]P).

Then for Q=[k]G,

    T_psi(Q) = psi(k)^(-1) T_psi(G),
    (T_psi(Q)/T_psi(G))^3 = chi_n(k).

The script verifies this identity exactly on the frozen toy groups satisfying
the same v_3(n-1)=1 condition as secp256k1, records structural exclusions when
the sextic character is trivial on the GLV C3 subgroup, and checks the public
secp256k1 Eisenstein norm relation for the standard GLV lattice vector.

Direct evaluation is Theta(n). No external point, key, wallet, or
production-sized discrete-log target is accepted.
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


def quadratic_character(value: int, prime: int, target_prime: int) -> int:
    value %= prime
    if value == 0:
        return 0
    result = pow(value, (prime - 1) // 2, prime)
    if result == 1:
        return 1
    if result == prime - 1:
        return target_prime - 1
    raise AssertionError("Euler criterion returned a non-binary value")


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
    scalar_generator = primitive_root(order)
    scalar_logs = discrete_log_table(scalar_generator, order)
    field_generator = primitive_root(field_prime)
    zeta6 = pow(field_generator, (field_prime - 1) // 6, field_prime)

    candidate_exponents = (1, 5)
    target_glv_phase = pow(beta, 2, field_prime)
    matching = [
        exponent
        for exponent in candidate_exponents
        if pow(zeta6, exponent * scalar_logs[lam], field_prime) == target_glv_phase
    ]

    if v3 != 1:
        if matching:
            raise AssertionError("sextic character unexpectedly detected the full GLV C3")
        return {
            "p": field_prime,
            "order": order,
            "generator": generator,
            "status": "excluded_sextic_character_trivial_on_glv_c3",
            "v3_order_minus_one": v3,
            "beta": beta,
            "lambda": lam,
        }

    if len(matching) != 1:
        raise AssertionError("secp-style case did not have a unique matching sextic character")
    character_exponent = matching[0]

    psi = [0] + [
        pow(zeta6, character_exponent * scalar_logs[scalar], field_prime)
        for scalar in range(1, order)
    ]
    chi = [0] + [
        quadratic_character(scalar, order, field_prime)
        for scalar in range(1, order)
    ]

    for scalar in range(1, order):
        if pow(psi[scalar], 3, field_prime) != chi[scalar]:
            raise AssertionError("psi^3 did not equal the scalar quadratic character")
    if psi[lam] != target_glv_phase:
        raise AssertionError("sextic character did not cancel the GLV x phase")
    if psi[order - 1] != 1:
        raise AssertionError("sextic character was not even under negation")

    def gauss_sum(point_scalar: int, x_power: int = 1) -> int:
        return sum(
            psi[weight]
            * pow(points[weight * point_scalar % order][0], x_power, field_prime)
            for weight in range(1, order)
        ) % field_prime

    base_sums = {
        exponent: gauss_sum(1, exponent)
        for exponent in (1, 4, 7, 10)
    }
    if base_sums[1] == 0:
        raise AssertionError("the frozen primary sextic x-projector vanished")

    scaling_checks = 0
    cube_character_checks = 0
    sixth_power_checks = 0
    base = base_sums[1]
    base_sixth = pow(base, 6, field_prime)
    for hidden_scalar in range(1, order):
        observed = gauss_sum(hidden_scalar)
        expected = base * pow(psi[hidden_scalar], -1, field_prime) % field_prime
        if observed != expected:
            raise AssertionError("sextic projector scaling law failed")
        ratio = observed * pow(base, -1, field_prime) % field_prime
        if pow(ratio, 3, field_prime) != chi[hidden_scalar]:
            raise AssertionError("cubed normalized sextic projector lost Legendre class")
        if pow(observed, 6, field_prime) != base_sixth:
            raise AssertionError("sixth power was not generator-blind")
        scaling_checks += 1
        cube_character_checks += 1
        sixth_power_checks += 1

    # The first few natural GLV-compatible x-powers are all nonzero on the
    # retained secp-style cases.  This is bounded evidence, not a theorem.
    if any(value == 0 for value in base_sums.values()):
        raise AssertionError("a frozen natural sextic x-power projector vanished")

    # A sextic character splits canonically into its order-three and order-two
    # components as psi = psi^4 * psi^3, since 4+3 is congruent to 1 modulo 6.
    cubic_component = [0] + [
        pow(psi[scalar], 4, field_prime) for scalar in range(1, order)
    ]
    quadratic_component = [0] + [
        pow(psi[scalar], 3, field_prime) for scalar in range(1, order)
    ]
    factorization_checks = 0
    for scalar in range(1, order):
        if psi[scalar] != cubic_component[scalar] * quadratic_component[scalar] % field_prime:
            raise AssertionError("sextic character did not factor into cubic and quadratic parts")
        factorization_checks += 1

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
        "target_glv_phase": target_glv_phase,
        "base_gauss_sums": {str(exponent): value for exponent, value in base_sums.items()},
        "primary_projector_nonzero": base != 0,
        "scaling_checks": scaling_checks,
        "cube_character_checks": cube_character_checks,
        "sixth_power_checks": sixth_power_checks,
        "character_factorization_checks": factorization_checks,
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
    if pow(lam, (n - 1) // 3, n) != pow(lam, 2, n):
        raise AssertionError("cubic residue of the GLV unit had wrong orientation")
    return {
        "p": p,
        "n": n,
        "n_mod_9": n % 9,
        "n_mod_12": n % 12,
        "v3_n_minus_one": valuation(n - 1, 3),
        "lambda": lam,
        "lambda_cubic_residue": pow(lam, (n - 1) // 3, n),
        "lambda_squared": pow(lam, 2, n),
        "eisenstein_a": a,
        "eisenstein_b": b,
        "eisenstein_norm": norm,
        "annihilator_residue": (a + b * lam) % n,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("eisenstein_sextic_gauss_root_results.json"),
    )
    args = parser.parse_args()

    cases = [run_case(p, order, generator) for p, order, generator in FROZEN_CASES]
    screened = [row for row in cases if row["status"] == "screened"]
    structural_exclusions = [
        row for row in cases
        if row["status"] == "excluded_sextic_character_trivial_on_glv_c3"
    ]
    payload = {
        "package": "EISENSTEIN-SEXTIC-GAUSS-ROOT-036",
        "scope": (
            "exact sextic-character projector identities on frozen toy j=0 "
            "subgroups and public secp256k1 arithmetic only; no external target"
        ),
        "cases": cases,
        "secp256k1": secp256k1_certificate(),
        "aggregate": {
            "cases": len(cases),
            "screened_cases": len(screened),
            "structural_exclusions": len(structural_exclusions),
            "other_exclusions": len(cases) - len(screened) - len(structural_exclusions),
            "all_primary_projectors_nonzero": all(
                bool(row["primary_projector_nonzero"]) for row in screened
            ),
            "all_natural_x_power_projectors_nonzero": all(
                all(int(value) != 0 for value in row["base_gauss_sums"].values())
                for row in screened
            ),
            "total_scaling_checks": sum(int(row["scaling_checks"]) for row in screened),
            "total_cube_character_checks": sum(
                int(row["cube_character_checks"]) for row in screened
            ),
            "total_sixth_power_checks": sum(
                int(row["sixth_power_checks"]) for row in screened
            ),
            "total_character_factorization_checks": sum(
                int(row["character_factorization_checks"]) for row in screened
            ),
        },
        "decision": (
            "For every retained secp-style v3(n-1)=1 toy subgroup, a unique "
            "sextic character cancels the GLV x phase, its x-projector is "
            "nonzero, and the cube of the normalized projector exactly equals "
            "the scalar Legendre class. The sixth power is generator-blind. "
            "The direct projector still costs Theta(n), and a CM formula for "
            "the generator-oriented cube is not obtained."
        ),
        "claim_boundary": [
            "Frozen nonvanishing on four secp-style toy groups is not a secp256k1 theorem.",
            "Groups with v3(n-1)>1 require a character carrying the full 3-primary part, not a sextic character.",
            "The public Eisenstein norm certificate identifies the CM kernel but not a generator-oriented Gauss-sum branch.",
            "No sub-square-root carry, R3, parity, Legendre-hidden-shift, or ECDLP algorithm is constructed.",
            "No external key or production-sized discrete-log target is processed.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
