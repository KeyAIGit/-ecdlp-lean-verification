#!/usr/bin/env python3
"""Exact C42 GLV cubic relative-norm replay.

This module does not claim a cheap parity decoder. It proves an exact normal
form for the C39 orbit factors after grouping the half-kernel roots into the
order-three GLV orbits of a j=0 curve, and it records the representation
boundary that remains after that grouping.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable

from uorc056_c39_half_miller import TOYS, Fp2, half_sequence, sigma

HELD_OUT = ((61, 61, (2, 25), 13, 47),)


def trim(poly: list[Fp2]) -> list[Fp2]:
    while len(poly) > 1 and not poly[-1]:
        poly.pop()
    return poly


def zero_like(value: Fp2) -> Fp2:
    return value * 0


def poly_add(left: list[Fp2], right: list[Fp2]) -> list[Fp2]:
    zero = zero_like(left[0] if left else right[0])
    return trim([
        (left[i] if i < len(left) else zero)
        + (right[i] if i < len(right) else zero)
        for i in range(max(len(left), len(right)))
    ])


def poly_sub(left: list[Fp2], right: list[Fp2]) -> list[Fp2]:
    zero = zero_like(left[0] if left else right[0])
    return trim([
        (left[i] if i < len(left) else zero)
        - (right[i] if i < len(right) else zero)
        for i in range(max(len(left), len(right)))
    ])


def poly_scale(poly: list[Fp2], scalar: Fp2) -> list[Fp2]:
    return trim([coefficient * scalar for coefficient in poly])


def poly_mul(left: list[Fp2], right: list[Fp2]) -> list[Fp2]:
    zero = zero_like(left[0])
    out = [zero for _ in range(len(left) + len(right) - 1)]
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            out[i + j] = out[i + j] + a * b
    return trim(out)


def poly_eval(poly: list[Fp2], point: Fp2) -> Fp2:
    out = zero_like(point)
    for coefficient in reversed(poly):
        out = out * point + coefficient
    return out


def root_polynomial(roots: Iterable[Fp2], one: Fp2) -> list[Fp2]:
    out = [one]
    for root in roots:
        out = poly_mul(out, [-root, one])
    return out


def interpolate(xs: list[Fp2], ys: list[Fp2], one: Fp2) -> list[Fp2]:
    """Quadratic-time exact interpolation in ascending coefficient order."""
    product = root_polynomial(xs, one)
    derivative = [product[i] * i for i in range(1, len(product))]
    out = [zero_like(one) for _ in range(len(xs))]
    for x, y in zip(xs, ys):
        degree = len(product) - 1
        quotient = [zero_like(one) for _ in range(degree)]
        quotient[-1] = product[-1]
        for i in range(degree - 2, -1, -1):
            quotient[i] = product[i + 1] + x * quotient[i + 1]
        scalar = y / poly_eval(derivative, x)
        for i, value in enumerate(quotient):
            out[i] = out[i] + scalar * value
    return trim(out)


def poly_divmod(
    dividend: list[Fp2], divisor: list[Fp2]
) -> tuple[list[Fp2], list[Fp2]]:
    dividend = trim(dividend[:])
    divisor = trim(divisor[:])
    zero = zero_like(divisor[0])
    quotient = [zero for _ in range(max(1, len(dividend) - len(divisor) + 1))]
    while len(dividend) >= len(divisor) and not (
        len(dividend) == 1 and not dividend[0]
    ):
        offset = len(dividend) - len(divisor)
        scalar = dividend[-1] / divisor[-1]
        quotient[offset] = quotient[offset] + scalar
        dividend = poly_sub(
            dividend,
            [zero] * offset + poly_scale(divisor, scalar),
        )
    return trim(quotient), trim(dividend)


def poly_mod(poly: list[Fp2], modulus: list[Fp2]) -> list[Fp2]:
    return poly_divmod(poly, modulus)[1]


def polynomial_stats(poly: list[Fp2]) -> dict[str, int | bool]:
    nonzero = sum(bool(coefficient) for coefficient in poly)
    return {
        "degree": len(poly) - 1,
        "coefficients": len(poly),
        "nonzero": nonzero,
        "zeros": len(poly) - nonzero,
        "dense": nonzero == len(poly),
    }


def compress_mod_three(
    poly: list[Fp2], one: Fp2, block_dimension: int
) -> tuple[list[Fp2], list[Fp2], list[Fp2]]:
    zero = zero_like(one)
    parts = [[zero for _ in range(block_dimension)] for _ in range(3)]
    for exponent, coefficient in enumerate(poly):
        quotient, residue = divmod(exponent, 3)
        if quotient >= block_dimension:
            raise AssertionError("coefficient exceeds the cubic block")
        parts[residue][quotient] = coefficient
    return tuple(trim(part) for part in parts)  # type: ignore[return-value]


def cubic_relative_norm(
    parts: tuple[list[Fp2], list[Fp2], list[Fp2]],
    kappa: list[Fp2],
    variable: list[Fp2],
) -> list[Fp2]:
    """Norm of c0(T)+X c1(T)+X^2 c2(T) for X^3=T."""
    c0, c1, c2 = parts
    c0_cube = poly_mod(poly_mul(poly_mul(c0, c0), c0), kappa)
    c1_cube = poly_mod(poly_mul(variable, poly_mul(poly_mul(c1, c1), c1)), kappa)
    c2_cube = poly_mod(
        poly_mul(poly_mul(variable, variable), poly_mul(poly_mul(c2, c2), c2)),
        kappa,
    )
    mixed = poly_mod(
        poly_scale(
            poly_mul(variable, poly_mul(poly_mul(c0, c1), c2)),
            c0[0] * 0 + 3,
        ),
        kappa,
    )
    return poly_mod(
        poly_sub(poly_add(poly_add(c0_cube, c1_cube), c2_cube), mixed),
        kappa,
    )


def determinant(matrix: list[list[Fp2]]) -> Fp2:
    work = [row[:] for row in matrix]
    size = len(work)
    one = work[0][0] ** 0
    out = one
    sign = 1
    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if work[row][column]),
            None,
        )
        if pivot is None:
            return one * 0
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            sign = -sign
        value = work[column][column]
        out = out * value
        inverse = value.inv()
        for row in range(column + 1, size):
            if work[row][column]:
                factor = work[row][column] * inverse
                for j in range(column, size):
                    work[row][j] = work[row][j] - factor * work[column][j]
    return -out if sign < 0 else out


def multiplication_matrix(
    element: list[Fp2], kappa: list[Fp2], dimension: int, one: Fp2
) -> list[list[Fp2]]:
    zero = zero_like(one)
    columns: list[list[Fp2]] = []
    monomial = [one]
    variable = [zero, one]
    for _ in range(dimension):
        column = poly_mod(poly_mul(element, monomial), kappa)
        columns.append(column + [zero] * (dimension - len(column)))
        monomial = poly_mod(poly_mul(monomial, variable), kappa)
    return [
        [columns[column][row] for column in range(dimension)]
        for row in range(dimension)
    ]


def analyze_curve(
    row: tuple[int, int, tuple[int, int], int, int], label: str
) -> dict[str, Any]:
    curve, order, generator, shift, beta, lam, half, values = half_sequence(row)
    one = curve.c(1)
    m = (order - 1) // 2
    if m % 3:
        raise AssertionError("the declared j=0 GLV block requires 3 | m")
    block_dimension = m // 3

    points = [curve.mul(index, generator) for index in range(1, m + 1)]
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    kernel = root_polynomial(xs, one)

    if not all((index % 3 == 0) or not coefficient for index, coefficient in enumerate(kernel)):
        raise AssertionError("K_H is not a polynomial in X^3")
    kappa = [kernel[3 * index] for index in range(block_dimension + 1)]

    t_roots: list[Fp2] = []
    t_keys: set[tuple[int, int]] = set()
    for x in xs:
        value = x * x * x
        if value.tuple() not in t_keys:
            t_keys.add(value.tuple())
            t_roots.append(value)
    if len(t_roots) != block_dimension:
        raise AssertionError("incorrect GLV quotient root count")
    if root_polynomial(t_roots, one) != kappa:
        raise AssertionError("K_H(X)=kappa(X^3) reconstruction failed")

    inverse_two = one / 2
    a_values: list[Fp2] = []
    b_values: list[Fp2] = []
    y_values: list[Fp2] = []
    for index, (x, y) in enumerate(zip(xs, ys), 1):
        forward = values[index]
        reverse = values[order - index]
        a_values.append((forward + reverse) * inverse_two)
        b_values.append((forward - reverse) / (2 * y))
        y_values.append(sigma(index, order) * y)

    a_poly = interpolate(xs, a_values, one)
    b_poly = interpolate(xs, b_values, one)
    y_poly = interpolate(xs, y_values, one)
    yb_poly = poly_mod(poly_mul(y_poly, b_poly), kernel)

    b_zeros = sum(not poly_eval(b_poly, x) for x in xs)
    if b_zeros:
        raise AssertionError("B is not a unit on the half-kernel")

    p_even = root_polynomial([values[k] for k in range(2, order, 2)], one)
    p_odd = root_polynomial([values[k] for k in range(1, order, 2)], one)
    variable = [zero_like(one), one]

    dense_even = 0
    dense_odd = 0
    dense_difference = 0
    localized_checks = 0
    matrix_samples: list[dict[str, int | bool]] = []
    sample_indices = sorted({1, 2, 3, m, m + 1, order - 2, order - 1})

    for k in range(1, order):
        state = values[k]
        constant_poly = [state] + [zero_like(one)] * (m - 1)
        c_even = poly_sub(poly_sub(constant_poly, a_poly), yb_poly)
        c_odd = poly_add(poly_sub(constant_poly, a_poly), yb_poly)
        d_even = cubic_relative_norm(
            compress_mod_three(c_even, one, block_dimension),
            kappa,
            variable,
        )
        d_odd = cubic_relative_norm(
            compress_mod_three(c_odd, one, block_dimension),
            kappa,
            variable,
        )

        norm_even = one
        norm_odd = one
        for root in t_roots:
            norm_even = norm_even * poly_eval(d_even, root)
            norm_odd = norm_odd * poly_eval(d_odd, root)

        explicit_even = poly_eval(p_even, state)
        explicit_odd = poly_eval(p_odd, state)
        if norm_even != explicit_even or norm_odd != explicit_odd:
            raise AssertionError("outer norm does not reproduce the orbit factor")
        if (not norm_even) != (k % 2 == 0):
            raise AssertionError("even zero branch mismatch")
        if (not norm_odd) != (k % 2 == 1):
            raise AssertionError("odd zero branch mismatch")

        query = curve.mul(k, generator)
        x_query, y_query = query
        a_query = poly_eval(a_poly, x_query)
        b_query = poly_eval(b_poly, x_query)
        y_oriented = poly_eval(y_poly, x_query)
        if state != a_query + y_query * b_query:
            raise AssertionError("A+yB query decomposition failed")
        if y_oriented != sigma(k, order) * y_query:
            raise AssertionError("oriented root normalization failed")
        local_even = state - a_query - y_oriented * b_query
        local_odd = state - a_query + y_oriented * b_query
        denominator = local_odd + local_even
        if not denominator:
            raise AssertionError("localized denominator vanished")
        decoded = (local_odd - local_even) / denominator
        if decoded != sigma(k, order):
            raise AssertionError("localized branch decoder failed")
        localized_checks += 1

        even_stats = polynomial_stats(d_even)
        odd_stats = polynomial_stats(d_odd)
        difference_stats = polynomial_stats(poly_sub(d_odd, d_even))
        dense_even += bool(even_stats["dense"])
        dense_odd += bool(odd_stats["dense"])
        dense_difference += bool(difference_stats["dense"])

        if k in sample_indices:
            nonzero_branch = d_odd if k % 2 == 0 else d_even
            matrix = multiplication_matrix(
                nonzero_branch, kappa, block_dimension, one
            )
            expected = norm_odd if k % 2 == 0 else norm_even
            if determinant(matrix) != expected:
                raise AssertionError("multiplication determinant mismatch")
            nonzero_entries = sum(bool(value) for row_values in matrix for value in row_values)
            matrix_samples.append({
                "k": k,
                "dimension": block_dimension,
                "nonzero_entries": nonzero_entries,
                "total_entries": block_dimension * block_dimension,
                "determinant_matches_outer_norm": True,
            })

    return {
        "label": label,
        "p": curve.p,
        "n": order,
        "m": m,
        "beta": beta,
        "lambda": lam,
        "glv_block_dimension": block_dimension,
        "K_H": polynomial_stats(kernel),
        "kappa": polynomial_stats(kappa),
        "A": polynomial_stats(a_poly),
        "B": polynomial_stats(b_poly),
        "Y": polynomial_stats(y_poly),
        "YB": polynomial_stats(yb_poly),
        "B_zeros_on_half_kernel": b_zeros,
        "relative_norm_targets": order - 1,
        "localized_branch_checks": localized_checks,
        "dense_relative_even": dense_even,
        "dense_relative_odd": dense_odd,
        "dense_relative_difference": dense_difference,
        "sample_multiplication_matrices": matrix_samples,
        "all_outer_norm_identities": True,
        "all_zero_branches_match_parity": True,
        "all_localized_decoders_return_parity": True,
        "errors": 0,
    }


def build_glv_payload() -> dict[str, Any]:
    rows = [
        analyze_curve(row, f"frozen-{index + 1}")
        for index, row in enumerate(TOYS)
    ] + [
        analyze_curve(row, f"heldout-{index + 1}")
        for index, row in enumerate(HELD_OUT)
    ]
    payload: dict[str, Any] = {
        "profile_id": "UORC-056-C42-GLV-TRANSPOSED-RESULTANT",
        "schema_version": "1.0",
        "held_out_instances": [
            {
                "p": row[0],
                "n": row[1],
                "generator": list(row[2]),
                "beta": row[3],
                "lambda": row[4],
            }
            for row in HELD_OUT
        ],
        "curves": rows,
        "theorems": {
            "half_kernel_glv_factorization": "K_H(X)=kappa(X^3)",
            "relative_cubic_norm": (
                "N3(c0+X*c1+X^2*c2)="
                "c0^3+T*c1^3+T^2*c2^3-3*T*c0*c1*c2"
            ),
            "outer_norm": (
                "P_even_or_odd(z)=Norm_{Fp2[T]/kappa}(D_even_or_odd(T;z))"
            ),
            "query_root_localization": (
                "(C_odd(x_Q)-C_even(x_Q))/(C_odd(x_Q)+C_even(x_Q))="
                "Y_G(x_Q)/y_Q=(-1)^k"
            ),
        },
        "aggregate": {
            "curves": len(rows),
            "frozen": len(TOYS),
            "heldout": len(HELD_OUT),
            "relative_norm_targets": sum(
                int(row["relative_norm_targets"]) for row in rows
            ),
            "localized_branch_checks": sum(
                int(row["localized_branch_checks"]) for row in rows
            ),
            "all_outer_norm_identities": all(
                bool(row["all_outer_norm_identities"]) for row in rows
            ),
            "all_zero_branches_match_parity": all(
                bool(row["all_zero_branches_match_parity"]) for row in rows
            ),
            "all_localized_decoders_return_parity": all(
                bool(row["all_localized_decoders_return_parity"]) for row in rows
            ),
            "all_kappa_dense": all(bool(row["kappa"]["dense"]) for row in rows),
            "errors": sum(int(row["errors"]) for row in rows),
        },
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["digest"] = hashlib.sha256(raw).hexdigest()
    return payload
