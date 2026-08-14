#!/usr/bin/env python3
"""Principal-factor construction for UORC056 B7A."""
from __future__ import annotations

import math

from uorc056_oriented_principal_pell_core import (
    B_CURVE,
    Point,
    ec_add,
    inv,
    kernel_polynomial,
    normalize_vector,
    nullspace_mod,
    orbit,
    poly_divmod,
    poly_eval,
    poly_mul,
    poly_sub,
    proportional,
    quadratic_character,
    trim,
)

def build_principal_factor(
    p: int, order: int, generator: tuple[int, int]
) -> dict[str, object]:
    points = orbit(generator, order, p)
    half = (order - 1) // 2
    pole_order = half + 1
    sum_scalar = (-pow(4, -1, order)) % order
    if (4 * sum_scalar + 1) % order != 0:
        raise AssertionError("half-divisor sum scalar failed")
    even_scalars = [2 * index for index in range(1, half + 1)]
    if even_scalars != list(range(2, order, 2)):
        raise AssertionError("canonical even support mismatch")
    support_points = [points[scalar] for scalar in even_scalars]
    anchor_scalar = (-sum_scalar) % order
    anchor = points[anchor_scalar]
    sum_point: Point = None
    for point in support_points:
        sum_point = ec_add(sum_point, point, p)
    if sum_point != points[sum_scalar]:
        raise AssertionError("elliptic support sum mismatch")
    if ec_add(sum_point, anchor, p) is not None:
        raise AssertionError("anchored zero divisor does not sum to identity")

    degree_a = pole_order // 2
    degree_b = (pole_order - 3) // 2
    count_a = degree_a + 1
    count_b = max(0, degree_b + 1)
    rows: list[list[int]] = []
    for point in support_points + [anchor]:
        if point is None:
            raise AssertionError("zero support contains identity")
        x_coordinate, y_coordinate = point
        row = [pow(x_coordinate, degree, p) for degree in range(count_a)]
        row.extend(
            y_coordinate * pow(x_coordinate, degree, p) % p
            for degree in range(count_b)
        )
        rows.append(row)
    basis = nullspace_mod(rows, p)
    if len(basis) != 1:
        raise AssertionError(
            f"principal Riemann-Roch nullspace has dimension {len(basis)}"
        )
    vector = normalize_vector(basis[0], p)
    polynomial_a = trim(vector[:count_a], p)
    polynomial_b = (
        trim(vector[count_a:], p) if count_b else [0]
    )

    kernel = kernel_polynomial(points, order, p)
    sum_point_checked = points[sum_scalar]
    if sum_point_checked is None:
        raise AssertionError("sum scalar unexpectedly zero")
    norm_base = poly_mul(
        kernel, [(-sum_point_checked[0]) % p, 1], p
    )
    curve_rhs = [B_CURVE, 0, 0, 1]
    norm_left = poly_sub(
        poly_mul(polynomial_a, polynomial_a, p),
        poly_mul(curve_rhs, poly_mul(polynomial_b, polynomial_b, p), p),
        p,
    )
    quotient, remainder = poly_divmod(norm_left, norm_base, p)
    if remainder != [0] or len(quotient) != 1 or quotient[0] == 0:
        raise AssertionError("polynomial Pell norm identity failed")
    norm_constant = quotient[0]

    actual_pole_order = max(
        2 * (len(polynomial_a) - 1),
        3 + 2 * (len(polynomial_b) - 1)
        if polynomial_b != [0]
        else -1,
    )
    if actual_pole_order != pole_order:
        raise AssertionError("principal factor has the wrong pole order")
    if pole_order % 2 == 0:
        expected_constant = polynomial_a[-1] * polynomial_a[-1] % p
    else:
        expected_constant = -polynomial_b[-1] * polynomial_b[-1] % p
    if norm_constant != expected_constant % p:
        raise AssertionError("leading-term norm square class failed")

    values: dict[int, int] = {}
    for scalar in range(1, order):
        point = points[scalar]
        if point is None:
            raise AssertionError("unexpected identity in nonzero orbit")
        x_coordinate, y_coordinate = point
        values[scalar] = (
            poly_eval(polynomial_a, x_coordinate, p)
            + y_coordinate * poly_eval(polynomial_b, x_coordinate, p)
        ) % p
    expected_zero_scalars = set(even_scalars)
    expected_zero_scalars.add(anchor_scalar)
    actual_zero_scalars = {
        scalar for scalar, value in values.items() if value == 0
    }
    if actual_zero_scalars != expected_zero_scalars:
        raise AssertionError("principal factor zero set mismatch")

    ratio_checks = 0
    exceptional_checks = 0
    both_zero_scalars: list[int] = []
    for scalar in range(1, order):
        left = values[(-scalar) % order]
        right = values[scalar]
        if left == 0 and right == 0:
            both_zero_scalars.append(scalar)
            expected_exception = (
                1 if scalar == sum_scalar and scalar % 2 == 0 else
                -1 % p if scalar == anchor_scalar and scalar % 2 == 1 else
                None
            )
            if expected_exception is None:
                raise AssertionError("unexpected both-zero selector exception")
            exceptional_checks += 1
            continue
        denominator = (left + right) % p
        if denominator == 0:
            raise AssertionError("selector denominator vanished")
        selector = (left - right) * inv(denominator, p) % p
        expected_selector = 1 if scalar % 2 == 0 else -1 % p
        if selector != expected_selector:
            raise AssertionError("principal factor parity selector failed")
        ratio_checks += 1

    expected_both_zero = (
        {sum_scalar, anchor_scalar} if anchor_scalar % 2 == 1 else set()
    )
    if set(both_zero_scalars) != expected_both_zero:
        raise AssertionError("public selector exception pair mismatch")

    negated_generator = (generator[0], (-generator[1]) % p)
    negated_points = orbit(negated_generator, order, p)
    negated_support = [
        negated_points[scalar] for scalar in even_scalars
    ]
    negated_sum_scalar = sum_scalar
    negated_anchor = negated_points[anchor_scalar]
    negated_rows: list[list[int]] = []
    for point in negated_support + [negated_anchor]:
        if point is None:
            raise AssertionError("negated support contains identity")
        x_coordinate, y_coordinate = point
        row = [pow(x_coordinate, degree, p) for degree in range(count_a)]
        row.extend(
            y_coordinate * pow(x_coordinate, degree, p) % p
            for degree in range(count_b)
        )
        negated_rows.append(row)
    negated_basis = nullspace_mod(negated_rows, p)
    if len(negated_basis) != 1:
        raise AssertionError("negated principal factor is not unique")
    negated_vector = normalize_vector(negated_basis[0], p)
    conjugate_vector = vector[:count_a] + [
        (-value) % p for value in vector[count_a:]
    ]
    if not proportional(negated_vector, conjugate_vector, p):
        raise AssertionError("generator-negation conjugation failed")

    minimum_width = None
    width_witness: tuple[int, int, int] | None = None
    for baby in range(half + 1):
        for giant in range(half + 1):
            leftover = max(0, half - 2 * baby * giant)
            width = baby + giant + leftover
            if minimum_width is None or width < minimum_width:
                minimum_width = width
                width_witness = (baby, giant, leftover)
            if half <= 2 * baby * giant + leftover:
                if 2 * half > width * (width + 2):
                    raise AssertionError("one-level index width inequality failed")
    if minimum_width is None or width_witness is None:
        raise AssertionError("index width search failed")

    return {
        "field_prime": p,
        "order": order,
        "generator": generator,
        "half_size": half,
        "pole_order": pole_order,
        "sum_scalar": sum_scalar,
        "anchor_scalar": anchor_scalar,
        "anchor_is_already_even": anchor_scalar % 2 == 0,
        "degree_a": len(polynomial_a) - 1,
        "degree_b": len(polynomial_b) - 1,
        "nonzero_coefficients_a": sum(value != 0 for value in polynomial_a),
        "nonzero_coefficients_b": sum(value != 0 for value in polynomial_b),
        "norm_constant": norm_constant,
        "norm_constant_character": quadratic_character(norm_constant, p),
        "support_sum_identity_exact": True,
        "principal_divisor_exact": True,
        "pell_identity_exact": True,
        "zero_set_exact": True,
        "ratio_checks": ratio_checks,
        "exceptional_point_checks": exceptional_checks,
        "total_selector_checks": ratio_checks + exceptional_checks,
        "both_zero_scalars": both_zero_scalars,
        "selector_exceptions_are_public": True,
        "generator_negation_is_quadratic_conjugation": True,
        "binary_tree_merges": pole_order - 1,
        "binary_tree_leaves": pole_order,
        "binary_tree_depth_lower_bound": math.ceil(math.log2(pole_order)),
        "one_level_index_minimum_width": minimum_width,
        "one_level_index_width_witness": width_witness,
        "one_level_width_inequality_exact": True,
    }


