#!/usr/bin/env python3
"""Exact local GLV branch decomposition for UORC-056 C43."""
from __future__ import annotations

import hashlib
import json
from typing import Any

from uorc056_c39_half_miller import TOYS, half_sequence, sigma
from uorc056_c42_glv_transposed_resultant import (
    interpolate,
    poly_eval,
    poly_mod,
    poly_mul,
    poly_scale,
    polynomial_stats,
    root_polynomial,
    zero_like,
)

HELD_OUT = (
    (61, 61, (2, 25), 13, 47),
    (229, 229, (2, 106), 94, 134),
    (997, 997, (1, 101), 304, 692),
    (2137, 2137, (1, 524), 1828, 808),
)


def point_count_j0(prime: int) -> int:
    count = 1
    for x in range(prime):
        value = (x * x * x + 7) % prime
        if value == 0:
            count += 1
        elif pow(value, (prime - 1) // 2, prime) == 1:
            count += 2
    return count


def substitute_scale(poly, scalar):
    power = scalar ** 0
    out = []
    for coefficient in poly:
        out.append(coefficient * power)
        power = power * scalar
    return out


def carry_sign(index: int, order: int, eigenvalue: int) -> int:
    first = (eigenvalue * index) % order
    second = (eigenvalue * first) % order
    total = index + first + second
    if total == order:
        return -1
    if total == 2 * order:
        return 1
    raise AssertionError("GLV carry sum is not n or 2n")


def analyze_curve(
    row: tuple[int, int, tuple[int, int], int, int], label: str
) -> dict[str, Any]:
    curve, order, generator, shift, beta, lam, half, values = half_sequence(row)
    one = curve.c(1)
    zero = zero_like(one)
    beta_field = curve.c(beta)
    m = (order - 1) // 2
    if m % 3:
        raise AssertionError("C43 requires three GLV cells per quotient root")
    quotient_dimension = m // 3

    if point_count_j0(curve.p) != order:
        raise AssertionError("declared curve does not have the stated prime order")
    if curve.mul(order, generator) is not None:
        raise AssertionError("declared generator does not have order n")
    phi_generator = (beta_field * generator[0], generator[1])
    if curve.mul(lam, generator) != phi_generator:
        raise AssertionError("GLV eigenvalue does not match beta action")
    if beta_field ** 3 != one or beta_field == one:
        raise AssertionError("beta is not a nontrivial cube root of unity")

    points = [curve.mul(index, generator) for index in range(1, m + 1)]
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    kernel = root_polynomial(xs, one)
    if not all(
        exponent % 3 == 0 or not coefficient
        for exponent, coefficient in enumerate(kernel)
    ):
        raise AssertionError("K_H is not in X^3")
    kappa = [kernel[3 * exponent] for exponent in range(quotient_dimension + 1)]

    t_roots = []
    seen_t = set()
    for x in xs:
        t = x ** 3
        if t.tuple() not in seen_t:
            seen_t.add(t.tuple())
            t_roots.append(t)
    if len(t_roots) != quotient_dimension:
        raise AssertionError("incorrect number of GLV quotient roots")
    if root_polynomial(t_roots, one) != kappa:
        raise AssertionError("K_H(X)=kappa(X^3) failed")

    y_values = [curve.c(sigma(index, order)) * y for index, y in enumerate(ys, 1)]
    oriented_root = interpolate(xs, y_values, one)
    curve_rhs = [curve.c(7), zero, zero, one]
    if poly_mod(poly_mul(oriented_root, oriented_root), kernel) != poly_mod(
        curve_rhs, kernel
    ):
        raise AssertionError("Y_G^2 = X^3+7 failed")

    y_beta = substitute_scale(oriented_root, beta_field)
    y_beta2 = substitute_scale(oriented_root, beta_field ** 2)
    cubic_product_x = poly_mod(
        poly_mul(oriented_root, poly_mul(y_beta, y_beta2)), kernel
    )
    if not all(
        exponent % 3 == 0 or not coefficient
        for exponent, coefficient in enumerate(cubic_product_x)
    ):
        raise AssertionError("oriented cubic product is not GLV-invariant")
    carry_root = [
        cubic_product_x[3 * exponent]
        if 3 * exponent < len(cubic_product_x)
        else zero
        for exponent in range(quotient_dimension)
    ]
    while len(carry_root) > 1 and not carry_root[-1]:
        carry_root.pop()

    t_plus_seven = [curve.c(7), one]
    expected_carry_square = poly_mod(
        poly_mul(poly_mul(t_plus_seven, t_plus_seven), t_plus_seven),
        kappa,
    )
    if poly_mod(poly_mul(carry_root, carry_root), kappa) != expected_carry_square:
        raise AssertionError("C_G(T)^2=(T+7)^3 failed")

    sector_values = []
    carry_checks = 0
    for index, (x, y) in enumerate(zip(xs, ys), 1):
        first = (lam * index) % order
        second = (lam * first) % order
        sector = sigma(first, order) * sigma(second, order)
        carry = carry_sign(index, order, lam)
        if sigma(index, order) != carry * sector:
            raise AssertionError("parity=carry*sector failed")
        sector_values.append(curve.c(sector))
        t = x ** 3
        if poly_eval(carry_root, t) != curve.c(carry) * (y ** 3):
            raise AssertionError("carry-root value failed")
        if poly_eval(oriented_root, x) != curve.c(sigma(index, order)) * y:
            raise AssertionError("oriented-root value failed")
        carry_checks += 1

    sector_root = interpolate(xs, sector_values, one)
    if poly_mod(poly_mul(sector_root, sector_root), kernel) != [one]:
        raise AssertionError("J_G^2=1 failed")
    lhs_sector = poly_mod(poly_mul(y_beta, y_beta2), kernel)
    rhs_sector = poly_mod(poly_mul(sector_root, curve_rhs), kernel)
    if lhs_sector != rhs_sector:
        raise AssertionError("Y(beta X)Y(beta^2 X)=J(X)(X^3+7) failed")

    carry_lift = []
    for coefficient in carry_root:
        carry_lift.extend([coefficient, zero, zero])
    carry_lift = carry_lift[: max(1, len(carry_lift) - 2)]
    reconstruction_numerator = poly_mod(
        poly_mul(carry_lift, sector_root), kernel
    )
    if reconstruction_numerator != poly_mod(
        poly_mul(oriented_root, curve_rhs), kernel
    ):
        raise AssertionError("Y_G * (X^3+7)=C_G(X^3)J_G failed")

    reversal_y_values = [-value for value in y_values]
    reversal_root = interpolate(xs, reversal_y_values, one)
    reversal_product = poly_mod(
        poly_mul(
            reversal_root,
            poly_mul(
                substitute_scale(reversal_root, beta_field),
                substitute_scale(reversal_root, beta_field ** 2),
            ),
        ),
        kernel,
    )
    if reversal_root != poly_scale(oriented_root, curve.c(-1)):
        raise AssertionError("G reversal does not negate Y_G")
    if reversal_product != poly_scale(cubic_product_x, curve.c(-1)):
        raise AssertionError("G reversal does not negate carry root")

    return {
        "label": label,
        "p": curve.p,
        "n": order,
        "m": m,
        "glv_quotient_dimension": quotient_dimension,
        "beta": beta,
        "lambda": lam,
        "K_H": polynomial_stats(kernel),
        "kappa": polynomial_stats(kappa),
        "Y_G": polynomial_stats(oriented_root),
        "carry_root_C_G": polynomial_stats(carry_root),
        "sector_root_J_G": polynomial_stats(sector_root),
        "carry_value_checks": carry_checks,
        "identities": {
            "K_H_equals_kappa_X3": True,
            "Y_G_square": True,
            "carry_root_square": True,
            "carry_root_values_equal_g_y_cubed": True,
            "sector_root_square_one": True,
            "sector_pair_product": True,
            "parity_equals_carry_times_sector": True,
            "oriented_root_reconstruction": True,
            "generator_reversal_negates_Y_and_C": True,
        },
        "errors": 0,
    }


def build_branch_payload() -> dict[str, Any]:
    rows = [
        analyze_curve(row, f"frozen-{index + 1}")
        for index, row in enumerate(TOYS)
    ] + [
        analyze_curve(row, f"heldout-{index + 1}")
        for index, row in enumerate(HELD_OUT)
    ]
    payload: dict[str, Any] = {
        "profile_id": "UORC-056-C43-LOCAL-GLV-BRANCH",
        "schema_version": "1.0",
        "curves": rows,
        "theorems": {
            "carry_root": (
                "C_G(T)=Y_G(X)Y_G(beta X)Y_G(beta^2 X), T=X^3"
            ),
            "carry_square": "C_G(T)^2=(T+7)^3 mod kappa(T)",
            "carry_value": "C_G(x(Q)^3)=g_G(Q)y(Q)^3",
            "sector_root": (
                "J_G(X)=Y_G(beta X)Y_G(beta^2 X)/(X^3+7)"
            ),
            "reconstruction": (
                "Y_G(X)(X^3+7)=C_G(X^3)J_G(X) mod K_H(X)"
            ),
            "parity_decomposition": "(-1)^k=g_G(Q)J_G(x(Q))",
        },
        "aggregate": {
            "curves": len(rows),
            "frozen": len(TOYS),
            "heldout": len(HELD_OUT),
            "carry_value_checks": sum(
                int(row["carry_value_checks"]) for row in rows
            ),
            "all_kappa_dense": all(bool(row["kappa"]["dense"]) for row in rows),
            "all_carry_roots_dense": all(
                bool(row["carry_root_C_G"]["dense"]) for row in rows
            ),
            "errors": sum(int(row["errors"]) for row in rows),
        },
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["digest"] = hashlib.sha256(raw).hexdigest()
    return payload
