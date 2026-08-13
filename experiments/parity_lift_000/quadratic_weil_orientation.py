#!/usr/bin/env python3
"""Exact scalar-model replay for QUADRATIC-WEIL-ORIENTATION-038.

Scope:
  * frozen toy prime orders with n == 1 (mod 12);
  * abstract Weil-pairing model e([x]G,[u]T)=zeta_n^(x*u);
  * public secp256k1 arithmetic certificates only;
  * no external point, key, wallet, or production-sized discrete-log target.

For nonzero u,k define

    W_u(k) = sum_(a mod n) zeta_n^(u*k*a^2).

The classical quadratic Gauss identity gives

    W_u(k) = chi_n(u) chi_n(k) W_1(1),
    W_u(k) / W_u(1) = chi_n(k).

The normalized ratio is independent of the chosen nonzero dual vector u. A
selector-free contraction over the whole nonzero dual line also satisfies

    C(k) = sum_(u != 0) W_u(k) W_u(1)
         = n (n-1) chi_n(k)          when n == 1 (mod 4).

Including u=0 and applying character orthogonality gives

    C0(k) = n * #{(a,b): k*a^2 + b^2 == 0 mod n}.

The incidence count is 2*n-1 for square k and 1 for nonsquare k. These are
exact public specifications of the scalar Legendre bit, but direct evaluation
uses Theta(n) states for one Gauss vector or Theta(n^2) terms for the symmetric
contraction. No sub-square-root evaluator is constructed.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

FROZEN_ORDERS = (397, 433, 1093, 1249, 3469, 4021)

SECP256K1_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
SECP256K1_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


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


def distinct_prime_factors(value: int) -> list[int]:
    result: list[int] = []
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor == 0:
            result.append(divisor)
            while value % divisor == 0:
                value //= divisor
        divisor = 3 if divisor == 2 else divisor + 2
    if value > 1:
        result.append(value)
    return result


def primitive_root(prime: int) -> int:
    factors = distinct_prime_factors(prime - 1)
    for candidate in range(2, prime):
        if all(pow(candidate, (prime - 1) // factor, prime) != 1 for factor in factors):
            return candidate
    raise AssertionError("primitive root not found")


def auxiliary_prime(order: int) -> tuple[int, int]:
    multiplier = 2
    while True:
        candidate = multiplier * order + 1
        if is_prime(candidate):
            return candidate, multiplier
        multiplier += 1


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


def run_case(order: int) -> dict[str, object]:
    if not is_prime(order) or order % 12 != 1:
        raise AssertionError("frozen order must be prime and 1 modulo 12")

    aux_prime, multiplier = auxiliary_prime(order)
    generator = primitive_root(aux_prime)
    zeta = pow(generator, (aux_prime - 1) // order, aux_prime)
    if zeta == 1 or pow(zeta, order, aux_prime) != 1:
        raise AssertionError("failed to construct a primitive order-n root")

    zeta_powers = [1] * order
    for exponent in range(1, order):
        zeta_powers[exponent] = zeta_powers[exponent - 1] * zeta % aux_prime

    square_exponents = [(scalar * scalar) % order for scalar in range(order)]
    gauss = []
    for coefficient in range(order):
        value = sum(
            zeta_powers[(coefficient * square) % order]
            for square in square_exponents
        ) % aux_prime
        gauss.append(value)

    base = gauss[1]
    if base == 0:
        raise AssertionError("quadratic Gauss base vanished")
    if base * base % aux_prime != order % aux_prime:
        raise AssertionError("quadratic Gauss square identity failed")

    scaling_checks = 0
    square_checks = 0
    for coefficient in range(1, order):
        expected = base if quadratic_character(coefficient, order) == 1 else -base % aux_prime
        if gauss[coefficient] != expected:
            raise AssertionError("quadratic Gauss scaling law failed")
        if gauss[coefficient] * gauss[coefficient] % aux_prime != order % aux_prime:
            raise AssertionError("generator-blind Gauss square failed")
        scaling_checks += 1
        square_checks += 1

    inverses = [0] + [pow(gauss[dual], -1, aux_prime) for dual in range(1, order)]
    dual_ratio_checks = 0
    selector_free_contraction_checks = 0
    full_dual_sum_cancellation_checks = 0
    incidence_checks = 0

    contraction_denominator = sum(
        gauss[dual] * gauss[dual] for dual in range(1, order)
    ) % aux_prime
    expected_denominator = order * (order - 1) % aux_prime
    if contraction_denominator != expected_denominator:
        raise AssertionError("selector-free contraction denominator failed")

    square_set = {scalar * scalar % order for scalar in range(order)}

    for hidden in range(1, order):
        character = quadratic_character(hidden, order)
        expected_character = 1 if character == 1 else aux_prime - 1

        for dual in range(1, order):
            ratio = gauss[dual * hidden % order] * inverses[dual] % aux_prime
            if ratio != expected_character:
                raise AssertionError("normalized ratio depended on dual scale")
            dual_ratio_checks += 1

        contraction = sum(
            gauss[dual * hidden % order] * gauss[dual]
            for dual in range(1, order)
        ) % aux_prime
        expected_contraction = character * order * (order - 1) % aux_prime
        if contraction != expected_contraction:
            raise AssertionError("selector-free contraction failed")
        selector_free_contraction_checks += 1

        full_dual_sum = sum(
            gauss[dual * hidden % order] for dual in range(1, order)
        ) % aux_prime
        if full_dual_sum != 0:
            raise AssertionError("unweighted full dual sum retained orientation")
        full_dual_sum_cancellation_checks += 1

        incidence_count = 0
        for left in range(order):
            value = (-hidden * (left * left % order)) % order
            if value == 0:
                incidence_count += 1
            elif value in square_set:
                incidence_count += 2
        expected_incidence = 2 * order - 1 if character == 1 else 1
        if incidence_count != expected_incidence:
            raise AssertionError("square-orbit incidence count failed")

        contraction_with_zero_dual = order * order + contraction
        if contraction_with_zero_dual % aux_prime != order * incidence_count % aux_prime:
            raise AssertionError("orthogonality contraction/count identity failed")
        incidence_checks += 1

    return {
        "order": order,
        "auxiliary_prime": aux_prime,
        "auxiliary_multiplier": multiplier,
        "primitive_root": generator,
        "primitive_order_root": zeta,
        "gauss_base": base,
        "gauss_base_square": base * base % aux_prime,
        "scaling_checks": scaling_checks,
        "square_checks": square_checks,
        "dual_ratio_checks": dual_ratio_checks,
        "selector_free_contraction_checks": selector_free_contraction_checks,
        "full_dual_sum_cancellation_checks": full_dual_sum_cancellation_checks,
        "incidence_checks": incidence_checks,
        "schrodinger_dimension": order,
        "square_orbit_support": (order + 1) // 2,
        "ceil_sqrt_order": math.isqrt(order - 1) + 1,
    }


def secp256k1_certificate() -> dict[str, object]:
    p = SECP256K1_P
    n = SECP256K1_N
    embedding_degree = (n - 1) // 6
    if n % 12 != 1:
        raise AssertionError("unexpected secp256k1 subgroup-order congruence")
    if pow(p, embedding_degree, n) != 1:
        raise AssertionError("claimed embedding degree did not return one")
    if pow(p, embedding_degree // 2, n) != n - 1:
        raise AssertionError("half-Frobenius did not act by minus one")

    sqrt_n = math.isqrt(n - 1) + 1
    return {
        "p": p,
        "n": n,
        "n_mod_12": n % 12,
        "embedding_degree": embedding_degree,
        "half_embedding_degree": embedding_degree // 2,
        "half_frobenius_residue": pow(p, embedding_degree // 2, n),
        "ceil_sqrt_n": sqrt_n,
        "single_gauss_terms": n,
        "selector_free_contraction_raw_terms": n * n,
        "square_orbit_support": (n + 1) // 2,
        "schrodinger_dimension": n,
        "dense_weil_matrix_entries": n * n,
        "embedding_degree_over_sqrt_floor": embedding_degree // sqrt_n,
        "schrodinger_dimension_over_sqrt_floor": n // sqrt_n,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("quadratic_weil_orientation_results.json"),
    )
    args = parser.parse_args()

    cases = [run_case(order) for order in FROZEN_ORDERS]
    payload = {
        "package": "QUADRATIC-WEIL-ORIENTATION-038",
        "scope": (
            "exact scalar-model Weil/Gauss identities on frozen toy prime orders "
            "and public secp256k1 arithmetic only; no external target"
        ),
        "cases": cases,
        "secp256k1": secp256k1_certificate(),
        "aggregate": {
            "cases": len(cases),
            "all_gauss_scaling_passed": all(row["scaling_checks"] == row["order"] - 1 for row in cases),
            "all_gauss_squares_passed": all(row["square_checks"] == row["order"] - 1 for row in cases),
            "total_dual_ratio_checks": sum(int(row["dual_ratio_checks"]) for row in cases),
            "total_selector_free_contraction_checks": sum(int(row["selector_free_contraction_checks"]) for row in cases),
            "total_full_dual_sum_cancellation_checks": sum(int(row["full_dual_sum_cancellation_checks"]) for row in cases),
            "total_incidence_checks": sum(int(row["incidence_checks"]) for row in cases),
        },
        "decision": (
            "The normalized quadratic Weil ratio is independent of the nonzero "
            "dual-vector scale, and a canonical selector-free contraction over "
            "the full dual line exactly recovers the scalar Legendre character. "
            "The same contraction is the Fourier transform of a square-orbit "
            "incidence count. Standard explicit realizations still require an "
            "n-dimensional Schrodinger model, an n-term Gauss vector, an n^2-term "
            "contraction, or a dual point over the large embedding-degree field. "
            "No classical sub-square-root evaluator is constructed."
        ),
        "claim_boundary": [
            "The abstract pairing model verifies exact scalar identities, not an efficient secp256k1 pairing implementation.",
            "The selector-free contraction removes the choice of a dual vector but not the representation-size problem.",
            "The n-dimensional standard Weil model is a scoped representation obstruction, not a lower bound against all arithmetic circuits.",
            "No public carry, parity, hard-R3, or EDS-residue decoder is constructed.",
            "No unconditional classical sub-square-root ECDLP algorithm is constructed.",
            "No external point, private key, wallet, or production-sized discrete-log target is processed.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
