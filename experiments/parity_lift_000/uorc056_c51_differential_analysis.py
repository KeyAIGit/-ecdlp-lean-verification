from __future__ import annotations

from typing import Any

from uorc056_c51_differential_core import (
    Curve, NetLineSeries, is_prime, logarithmic_derivatives,
    period_shift_eta_coefficient, point_count, quadratic_character,
    regularized_torsion_jet,
)

def polynomial_mul(left: list[int], right: list[int], prime: int) -> list[int]:
    out = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            out[i + j] = (out[i + j] + a * b) % prime
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out


def polynomial_from_roots(roots: list[int], prime: int) -> list[int]:
    out = [1]
    for root in roots:
        out = polynomial_mul(out, [-root % prime, 1], prime)
    return out


def polynomial_eval(poly: list[int], point: int, prime: int) -> int:
    out = 0
    for coefficient in reversed(poly):
        out = (out * point + coefficient) % prime
    return out


def interpolate(xs: list[int], ys: list[int], prime: int) -> list[int]:
    product = polynomial_from_roots(xs, prime)
    derivative = [index * product[index] % prime for index in range(1, len(product))]
    out = [0] * len(xs)
    for x, y in zip(xs, ys):
        degree = len(product) - 1
        quotient = [0] * degree
        quotient[-1] = product[-1]
        for index in range(degree - 2, -1, -1):
            quotient[index] = (product[index + 1] + x * quotient[index + 1]) % prime
        scale = y * pow(polynomial_eval(derivative, x, prime), -1, prime) % prime
        for index, value in enumerate(quotient):
            out[index] = (out[index] + scale * value) % prime
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out


def affine_character_survivors(
    values: list[int], parities: list[int], prime: int
) -> int:
    survivors = 0
    targets = [1 if parity == 0 else -1 for parity in parities]
    for constant in range(prime):
        signs = [quadratic_character(value + constant, prime) for value in values]
        if 0 not in signs and (
            signs == targets or signs == [-target for target in targets]
        ):
            survivors += 1
    return survivors


def analyze_curve(
    row: tuple[int, int, tuple[int, int], int, int], label: str
) -> dict[str, Any]:
    prime, order, generator, beta, eigenvalue = row
    curve = Curve(prime)
    if not is_prime(order):
        raise AssertionError("declared subgroup order is not prime")
    if point_count(curve) != order:
        raise AssertionError("declared curve order is incorrect")
    if curve.mul(order, generator) is not None:
        raise AssertionError("declared generator order is incorrect")
    if pow(beta, 3, prime) != 1 or beta == 1:
        raise AssertionError("beta is not a nontrivial cube root")
    if (eigenvalue * eigenvalue + eigenvalue + 1) % order:
        raise AssertionError("lambda is not a cubic eigenvalue")
    phi_generator = (beta * generator[0] % prime, generator[1])
    if curve.mul(eigenvalue, generator, order) != phi_generator:
        raise AssertionError("GLV eigenvalue does not match beta")

    h_values: dict[int, int] = {}
    x_ratios: dict[int, int] = {}
    for scalar in range(1, order):
        point = curve.mul(scalar, generator, order)
        if point is None:
            raise AssertionError("unexpected identity")
        h_value, x_ratio, _, _ = regularized_torsion_jet(prime, order, point)
        h_values[scalar] = h_value
        x_ratios[scalar] = x_ratio

    odd_checks = 0
    glv_checks = 0
    for scalar in range(1, order):
        if h_values[order - scalar] != -h_values[scalar] % prime:
            raise AssertionError("H_n is not odd")
        if h_values[eigenvalue * scalar % order] != (
            beta * beta * h_values[scalar]
        ) % prime:
            raise AssertionError("H_n does not have GLV weight beta^2")
        odd_checks += 1
        glv_checks += 1

    quotient_xs: list[int] = []
    quotient_ys: list[int] = []
    seen_t: set[int] = set()
    for scalar in range(1, order):
        point = curve.mul(scalar, generator, order)
        x, y = point
        t = pow(x, 3, prime)
        if t in seen_t or x == 0:
            continue
        seen_t.add(t)
        quotient_xs.append(t)
        quotient_ys.append(
            h_values[scalar] * y * pow(x * x % prime, -1, prime) % prime
        )
    quotient_poly = interpolate(quotient_xs, quotient_ys, prime)
    for scalar in range(1, order):
        x, y = curve.mul(scalar, generator, order)
        if x == 0:
            continue
        reconstructed = (
            x * x * pow(y, -1, prime)
            * polynomial_eval(quotient_poly, pow(x, 3, prime), prime)
        ) % prime
        if reconstructed != h_values[scalar]:
            raise AssertionError("CM quotient reconstruction failed")

    first_derivative_checks = 0
    second_derivative_checks = 0
    third_derivative_checks = 0
    a_values: list[int] = []
    first_values: list[int] = []
    h_query_values: list[int] = []
    parities: list[int] = []
    for scalar in range(2, order - 1):
        query = curve.mul(scalar, generator, order)
        query_plus = curve.add(query, generator)
        if query is None or query_plus is None:
            raise AssertionError("unexpected exceptional point")
        net_series = NetLineSeries(prime, generator, query, 4).value(order)
        if net_series.coefficients[0] == 0:
            raise AssertionError("A_n vanished on its regular chart")
        first, second, third = logarithmic_derivatives(prime, query, net_series)
        expected_first = (
            -h_values[1]
            + (order - 1) * h_values[scalar]
            + h_values[scalar + 1]
        ) % prime
        expected_second = (
            -order * order * generator[0]
            + (order * order - order) * query[0]
            + order * query_plus[0]
        ) % prime
        expected_third = (
            -2 * order**3 * generator[1]
            + 2 * (order * order - order) * query[1]
            + 2 * order * query_plus[1]
        ) % prime
        if first != expected_first:
            raise AssertionError("first differential normal form failed")
        if second != expected_second:
            raise AssertionError("second differential coordinate collapse failed")
        if third != expected_third:
            raise AssertionError("third differential coordinate collapse failed")
        a_values.append(net_series.coefficients[0])
        first_values.append(first)
        h_query_values.append(h_values[scalar])
        parities.append(scalar & 1)
        first_derivative_checks += 1
        second_derivative_checks += 1
        third_derivative_checks += 1

    character_survivors = {
        "H_query": affine_character_survivors(h_query_values, parities, prime),
        "dlog_A_n": affine_character_survivors(first_values, parities, prime),
        "A_n": affine_character_survivors(a_values, parities, prime),
    }

    eta_cancellation_checks = 0
    for a in range(-3, 4):
        for b in range(-3, 4):
            for r in range(-2, 3):
                for s in range(-2, 3):
                    for scalar in (1, 2, 3, (order - 1) // 2, order - 2):
                        if period_shift_eta_coefficient(
                            a, b, r, s, order, scalar
                        ) != 0:
                            raise AssertionError("quasiperiod coefficient did not cancel")
                        eta_cancellation_checks += 1

    h_distinct = len(set(h_query_values))
    h_mixed_collisions = 0
    seen_h: dict[int, int] = {}
    for parity, value in zip(parities, h_query_values):
        if value in seen_h and seen_h[value] != parity:
            h_mixed_collisions += 1
        seen_h[value] = parity

    return {
        "label": label,
        "p": prime,
        "n": order,
        "rows": order - 1,
        "regular_chart_rows": order - 3,
        "H_odd_checks": odd_checks,
        "H_glv_weight_checks": glv_checks,
        "H_glv_weight": "beta^2",
        "H_query_distinct_values": h_distinct,
        "H_query_mixed_parity_collisions": h_mixed_collisions,
        "cm_quotient": {
            "roots": len(quotient_xs),
            "degree": len(quotient_poly) - 1,
            "nonzero_coefficients": sum(value != 0 for value in quotient_poly),
            "dense": all(value != 0 for value in quotient_poly),
        },
        "first_derivative_checks": first_derivative_checks,
        "second_derivative_checks": second_derivative_checks,
        "third_derivative_checks": third_derivative_checks,
        "eta_cancellation_checks": eta_cancellation_checks,
        "affine_character_survivors": character_survivors,
        "identities": {
            "H_is_odd": True,
            "H_has_GLV_weight_beta_squared": True,
            "H_has_CM_quotient_form": True,
            "dlog_A_n_reduces_to_three_H_values": True,
            "second_dlog_is_coordinate_function": True,
            "third_dlog_is_coordinate_function": True,
            "period_shift_eta_cancels": True,
        },
        "errors": 0,
    }

