#!/usr/bin/env python3
"""Exact frozen replay for UORC056 translated quarter-kernel evaluator.

The executable scope is deliberately narrow: four fixed public toy curves of
prime order n == 1 (mod 4), plus a size-only secp256k1 certificate. The script
accepts no external curve, point, key, wallet, scalar, or production DLP target.

For n = 4h + 1, M = 2h, and R = [(n+1)/2]G (the unique half of G), define

    J_G(X) = product_{j=1}^h (X - x([(2j-1)]G)).

Then J_G(x(Q-R)) vanishes exactly on the even scalar points Q=[k]G. Homogeneous
translation gives polynomials A_G,B_G with

    d(X)^h J_G((u(X)+2*y(R)*Y)/d(X)) = A_G(X) + Y B_G(X),

where d=(X-x(R))^2 and u=x(R)X^2+x(R)^2X+14 on Y^2=X^3+7. The frozen replay
checks the polynomial Pell identity, the bridge to the oriented root Y_G, and

    -y(Q) B_G(x(Q)) / A_G(x(Q)) = (-1)^k.

This is an exact evaluator normal form, not a sub-square-root algorithm: the
explicit J_G/A_G/B_G representations remain Theta(n).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

Point = Optional[tuple[int, int]]
CURVE_B = 7
SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

FROZEN_CASES = (
    (61, 61, (2, 25)),
    (349, 313, (2, 109)),
    (2851, 397, (2276, 1015)),
    (1663, 433, (126, 1375)),
)


def trim(poly: list[int], p: int) -> list[int]:
    result = [coefficient % p for coefficient in poly]
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def poly_add(left: list[int], right: list[int], p: int) -> list[int]:
    size = max(len(left), len(right))
    return trim(
        [
            (left[index] if index < len(left) else 0)
            + (right[index] if index < len(right) else 0)
            for index in range(size)
        ],
        p,
    )


def poly_neg(poly: list[int], p: int) -> list[int]:
    return trim([-coefficient for coefficient in poly], p)


def poly_sub(left: list[int], right: list[int], p: int) -> list[int]:
    return poly_add(left, poly_neg(right, p), p)


def poly_scale(poly: list[int], scalar: int, p: int) -> list[int]:
    return trim([scalar * coefficient for coefficient in poly], p)


def poly_mul(left: list[int], right: list[int], p: int) -> list[int]:
    result = [0] * (len(left) + len(right) - 1)
    for i, left_value in enumerate(left):
        for j, right_value in enumerate(right):
            result[i + j] = (result[i + j] + left_value * right_value) % p
    return trim(result, p)


def poly_divmod(
    numerator: list[int], denominator: list[int], p: int
) -> tuple[list[int], list[int]]:
    numerator = trim(numerator.copy(), p)
    denominator = trim(denominator.copy(), p)
    if denominator == [0]:
        raise ZeroDivisionError("zero polynomial")
    if len(numerator) < len(denominator):
        return [0], numerator
    quotient = [0] * (len(numerator) - len(denominator) + 1)
    inverse_lead = pow(denominator[-1], -1, p)
    while numerator != [0] and len(numerator) >= len(denominator):
        shift = len(numerator) - len(denominator)
        coefficient = numerator[-1] * inverse_lead % p
        quotient[shift] = coefficient
        for index, value in enumerate(denominator):
            numerator[index + shift] = (
                numerator[index + shift] - coefficient * value
            ) % p
        numerator = trim(numerator, p)
    return trim(quotient, p), numerator


def poly_mod(poly: list[int], modulus: list[int], p: int) -> list[int]:
    return poly_divmod(poly, modulus, p)[1]


def poly_eval(poly: list[int], value: int, p: int) -> int:
    result = 0
    for coefficient in reversed(poly):
        result = (result * value + coefficient) % p
    return result


def poly_from_roots(roots: list[int], p: int) -> list[int]:
    result = [1]
    for root in roots:
        result = poly_mul(result, [(-root) % p, 1], p)
    return result


def divide_by_linear(
    poly: list[int], root: int, p: int
) -> tuple[list[int], int]:
    degree = len(poly) - 1
    if degree < 1:
        raise AssertionError("cannot divide a constant by a linear factor")
    quotient = [0] * degree
    quotient[-1] = poly[-1]
    for index in range(degree - 1, 0, -1):
        quotient[index - 1] = (poly[index] + root * quotient[index]) % p
    remainder = (poly[0] + root * quotient[0]) % p
    return trim(quotient, p), remainder


def interpolate(xs: list[int], ys: list[int], p: int) -> tuple[list[int], list[int]]:
    if len(xs) != len(ys) or len(xs) != len(set(xs)):
        raise AssertionError("interpolation nodes must be distinct")
    kernel = poly_from_roots(xs, p)
    result = [0]
    for x_value, y_value in zip(xs, ys, strict=True):
        quotient, remainder = divide_by_linear(kernel, x_value, p)
        if remainder != 0:
            raise AssertionError("kernel did not vanish at interpolation node")
        denominator = poly_eval(quotient, x_value, p)
        if denominator == 0:
            raise AssertionError("kernel was not squarefree")
        scale = y_value * pow(denominator, -1, p) % p
        result = poly_add(result, poly_scale(quotient, scale, p), p)
    return trim(result, p), kernel


def point_neg(point: Point, p: int) -> Point:
    if point is None:
        return None
    return point[0], (-point[1]) % p


def ec_add(left: Point, right: Point, p: int) -> Point:
    if left is None:
        return right
    if right is None:
        return left
    x_left, y_left = left
    x_right, y_right = right
    if x_left == x_right and (y_left + y_right) % p == 0:
        return None
    if left == right:
        if y_left == 0:
            return None
        slope = 3 * x_left * x_left * pow(2 * y_left, -1, p) % p
    else:
        slope = (y_right - y_left) * pow((x_right - x_left) % p, -1, p) % p
    x_sum = (slope * slope - x_left - x_right) % p
    y_sum = (slope * (x_left - x_sum) - y_left) % p
    return x_sum, y_sum


def scalar_mul(scalar: int, point: Point, p: int) -> Point:
    result: Point = None
    addend = point
    while scalar:
        if scalar & 1:
            result = ec_add(result, addend, p)
        addend = ec_add(addend, addend, p)
        scalar >>= 1
    return result


def orbit(generator: tuple[int, int], order: int, p: int) -> list[Point]:
    points = [scalar_mul(index, generator, p) for index in range(order)]
    if points[0] is not None or scalar_mul(order, generator, p) is not None:
        raise AssertionError("displayed point does not have the declared order")
    if any(point is None for point in points[1:]):
        raise AssertionError("nonzero scalar unexpectedly reached the identity")
    return points


PolyPair = tuple[list[int], list[int]]


def pair_add(left: PolyPair, right: PolyPair, p: int) -> PolyPair:
    return poly_add(left[0], right[0], p), poly_add(left[1], right[1], p)


def pair_mul(left: PolyPair, right: PolyPair, p: int) -> PolyPair:
    curve_rhs = [CURVE_B, 0, 0, 1]
    scalar_part = poly_add(
        poly_mul(left[0], right[0], p),
        poly_mul(poly_mul(left[1], right[1], p), curve_rhs, p),
        p,
    )
    y_part = poly_add(
        poly_mul(left[0], right[1], p),
        poly_mul(left[1], right[0], p),
        p,
    )
    return scalar_part, y_part


def homogeneous_translate_pair(
    polynomial: list[int],
    u_poly: list[int],
    y_coefficient: int,
    denominator_poly: list[int],
    p: int,
) -> PolyPair:
    """Return A,B with d^h J((u+c*y)/d)=A+B*y."""
    degree = len(polynomial) - 1
    pair: PolyPair = ([polynomial[-1]], [0])
    denominator_power = [1]
    translated_variable: PolyPair = (u_poly, [y_coefficient % p])
    for index in range(degree - 1, -1, -1):
        denominator_power = poly_mul(denominator_power, denominator_poly, p)
        pair = pair_mul(pair, translated_variable, p)
        pair = pair_add(
            pair,
            (poly_scale(denominator_power, polynomial[index], p), [0]),
            p,
        )
    return trim(pair[0], p), trim(pair[1], p)


def run_case(p: int, order: int, generator: tuple[int, int]) -> dict[str, object]:
    if order % 4 != 1:
        raise AssertionError("translated quarter-kernel requires n == 1 mod 4")
    points = orbit(generator, order, p)
    middle = (order - 1) // 2
    quarter = (order - 1) // 4
    if middle != 2 * quarter:
        raise AssertionError("inconsistent n=4h+1 decomposition")

    half_generator = points[middle + 1]
    if half_generator is None:
        raise AssertionError("half-generator is the identity")
    if ec_add(half_generator, half_generator, p) != generator:
        raise AssertionError("R is not the unique half of G")
    if points[middle] != point_neg(half_generator, p):
        raise AssertionError("the two public half scalars are not opposite")

    odd_pair_indices = list(range(1, middle, 2))
    quarter_roots = [points[index][0] for index in odd_pair_indices]  # type: ignore[index]
    if len(set(quarter_roots)) != quarter:
        raise AssertionError("quarter-kernel roots are not distinct")
    quarter_kernel = poly_from_roots(quarter_roots, p)

    negative_generator = point_neg(generator, p)
    if negative_generator is None:
        raise AssertionError("generator negation failed")
    negative_points = orbit(negative_generator, order, p)
    negative_roots = [negative_points[index][0] for index in odd_pair_indices]  # type: ignore[index]
    negative_quarter_kernel = poly_from_roots(negative_roots, p)
    if negative_quarter_kernel != quarter_kernel:
        raise AssertionError("J_(-G) must equal J_G")

    symmetric_odd_points: set[tuple[int, int]] = set()
    for index in odd_pair_indices:
        point = points[index]
        if point is None:
            raise AssertionError("unexpected identity in odd pair set")
        symmetric_odd_points.add(point)
        symmetric_odd_points.add(point_neg(point, p))  # type: ignore[arg-type]
    translated_points = {ec_add(half_generator, point, p) for point in symmetric_odd_points}
    expected_even_points = {points[index] for index in range(2, order, 2)}
    if translated_points != expected_even_points:
        raise AssertionError("R+A_G is not the canonical even set")

    zero_test_checks = 0
    for scalar in range(1, order):
        query = points[scalar]
        if query is None:
            raise AssertionError("unexpected identity query")
        shifted = ec_add(query, point_neg(half_generator, p), p)
        is_zero = shifted is not None and poly_eval(quarter_kernel, shifted[0], p) == 0
        decoded = 1 if query != half_generator and is_zero else -1
        expected = 1 if scalar % 2 == 0 else -1
        if decoded != expected:
            raise AssertionError("translated quarter-kernel zero test failed")
        zero_test_checks += 1

    x_half, y_half = half_generator
    denominator_base = poly_mul([(-x_half) % p, 1], [(-x_half) % p, 1], p)
    u_poly = [14 % p, (x_half * x_half) % p, x_half % p]
    trace_a, trace_b = homogeneous_translate_pair(
        quarter_kernel,
        u_poly,
        2 * y_half,
        denominator_base,
        p,
    )

    full_kernel_roots = [points[index][0] for index in range(1, middle + 1)]  # type: ignore[index]
    full_kernel = poly_from_roots(full_kernel_roots, p)
    curve_rhs = [CURVE_B, 0, 0, 1]

    pell_left = poly_sub(
        poly_mul(trace_a, trace_a, p),
        poly_mul(poly_mul(trace_b, trace_b, p), curve_rhs, p),
        p,
    )
    pole_factor = poly_from_roots([x_half] * middle, p)
    pell_base = poly_mul(full_kernel, pole_factor, p)
    pell_constant, pell_remainder = poly_divmod(pell_left, pell_base, p)
    if pell_remainder != [0] or len(pell_constant) != 1 or pell_constant[0] == 0:
        raise AssertionError("polynomial Pell identity did not have a nonzero constant quotient")

    oriented_xs: list[int] = []
    oriented_values: list[int] = []
    for index in range(1, middle + 1):
        point = points[index]
        if point is None:
            raise AssertionError("unexpected identity in Kummer representatives")
        x_value, y_value = point
        oriented_xs.append(x_value)
        oriented_values.append(y_value if index % 2 == 0 else (-y_value) % p)
    oriented_root, interpolation_kernel = interpolate(oriented_xs, oriented_values, p)
    if interpolation_kernel != full_kernel:
        raise AssertionError("interpolation and full Kummer kernels disagree")

    bridge = poly_add(
        poly_mul(oriented_root, trace_a, p),
        poly_mul(curve_rhs, trace_b, p),
        p,
    )
    if poly_mod(bridge, full_kernel, p) != [0]:
        raise AssertionError("Y_G*A_G + (X^3+7)*B_G did not vanish modulo K_H")

    ratio_checks = 0
    for scalar in range(1, order):
        query = points[scalar]
        if query is None:
            raise AssertionError("unexpected identity query")
        x_value, y_value = query
        denominator = poly_eval(trace_a, x_value, p)
        if denominator == 0:
            raise AssertionError("trace denominator vanished on a nonzero subgroup point")
        decoded = (
            -y_value
            * poly_eval(trace_b, x_value, p)
            * pow(denominator, -1, p)
        ) % p
        expected = 1 if scalar % 2 == 0 else p - 1
        if decoded != expected:
            raise AssertionError("trace-pair evaluator lost scalar parity")
        ratio_checks += 1

    negative_half = negative_points[middle + 1]
    if negative_half != point_neg(half_generator, p):
        raise AssertionError("R_(-G) != -R_G")
    if negative_half is None:
        raise AssertionError("negative half-generator is the identity")
    negative_a, negative_b = homogeneous_translate_pair(
        negative_quarter_kernel,
        u_poly,
        2 * negative_half[1],
        denominator_base,
        p,
    )
    if negative_a != trace_a or negative_b != poly_neg(trace_b, p):
        raise AssertionError("trace pair did not transform as (A,-B) under G -> -G")

    return {
        "p": p,
        "n": order,
        "generator": list(generator),
        "middle": middle,
        "quarter": quarter,
        "half_generator_scalar": middle + 1,
        "half_generator": list(half_generator),
        "quarter_kernel_degree": len(quarter_kernel) - 1,
        "quarter_kernel_nonzero_coefficients": sum(value != 0 for value in quarter_kernel),
        "trace_a_degree": len(trace_a) - 1,
        "trace_b_degree": len(trace_b) - 1,
        "pell_constant": pell_constant[0],
        "zero_test_checks": zero_test_checks,
        "trace_ratio_checks": ratio_checks,
        "quarter_kernel_generator_negation_invariant": True,
        "trace_pair_generator_negation_covariant": True,
        "oriented_root_bridge_verified": True,
        "all_checks_passed": True,
    }


def secp256k1_certificate() -> dict[str, object]:
    order = SECP_N
    middle = (order - 1) // 2
    quarter = (order - 1) // 4
    return {
        "n": order,
        "bit_length": order.bit_length(),
        "n_mod_4": order % 4,
        "middle": middle,
        "quarter": quarter,
        "half_generator_scalar": (order + 1) // 2,
        "quarter_kernel_degree": quarter,
        "trace_a_degree_upper_bound": middle,
        "trace_b_degree_upper_bound": middle - 2,
        "explicit_quarter_kernel_coefficients": quarter + 1,
        "explicit_trace_pair_coefficients_upper_bound": 2 * middle,
        "explicit_representation_is_theta_n": True,
        "full_cost_gate_passed": False,
        "remaining_compiler_target": (
            "evaluate the distinguished translated trace pair (A_G,B_G) "
            "without materializing J_G or its Theta(n) coefficients"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "uorc056_translated_quarter_kernel_results.json"
        ),
    )
    args = parser.parse_args()

    cases = [run_case(*case) for case in FROZEN_CASES]
    payload = {
        "package": "UORC056_TRANSLATED_QUARTER_KERNEL_C3",
        "central_target": "UNIFORM-ORIENTED-ROOT-CIRCUIT-056",
        "scope": "four fixed public n=1 mod 4 toy curves plus secp256k1 size certificate",
        "cases": cases,
        "aggregate": {
            "cases": len(cases),
            "total_zero_test_checks": sum(case["zero_test_checks"] for case in cases),
            "total_trace_ratio_checks": sum(case["trace_ratio_checks"] for case in cases),
            "all_translated_set_identities_passed": True,
            "all_pell_identities_passed": True,
            "all_oriented_root_bridges_passed": True,
            "all_generator_negation_checks_passed": True,
            "exact_evaluator_normal_form_found": True,
            "full_cost_gate_passed": False,
            "public_parity_oracle_found": False,
            "sub_sqrt_ecdlp_found": False,
        },
        "secp256k1": secp256k1_certificate(),
    }
    encoded = json.dumps(payload, indent=2, sort_keys=True)
    print(encoded)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(encoded + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
