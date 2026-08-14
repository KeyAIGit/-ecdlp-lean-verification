#!/usr/bin/env python3
"""Frozen exact replay for UORC056 translation-resolvent branch selection.

This file uses only the six frozen toy subgroups from package 046. It checks
exact Kummer selector, odd-cycle resolvent, public defect seed, doubling
orientation cocycle, and bounded rank-one determinant identities. It does not
claim a secp256k1 evaluator or a sub-square-root algorithm.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from nonlocal_odd_anchor_screen import ec_add, orbit, quadratic_character
from oriented_parity_divisor_circuit import (
    CURVE_B,
    FROZEN_CASES,
    interpolate,
    poly_add,
    poly_eval,
    poly_mod,
    poly_mul,
)


def canonical_sqrt(value: int, p: int) -> int:
    if p % 4 != 3:
        raise AssertionError("requires p == 3 mod 4")
    root = pow(value % p, (p + 1) // 4, p)
    if root * root % p != value % p:
        raise AssertionError("value is not a square")
    return root


def determinant_mod(matrix: list[list[int]], p: int) -> int:
    work = [[entry % p for entry in row] for row in matrix]
    n = len(work)
    if any(len(row) != n for row in work):
        raise AssertionError("matrix must be square")
    determinant = 1
    for column in range(n):
        pivot = next(
            (row for row in range(column, n) if work[row][column]),
            None,
        )
        if pivot is None:
            return 0
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            determinant = -determinant
        pivot_value = work[column][column]
        determinant = determinant * pivot_value % p
        pivot_inverse = pow(pivot_value, -1, p)
        for row in range(column + 1, n):
            if not work[row][column]:
                continue
            factor = work[row][column] * pivot_inverse % p
            for index in range(column, n):
                work[row][index] = (
                    work[row][index] - factor * work[column][index]
                ) % p
    return determinant % p


def check_case(p: int, n: int, generator: tuple[int, int]) -> dict[str, object]:
    points = orbit(generator, n, p)
    middle = (n - 1) // 2
    xs: list[int] = []
    selector_values: list[int] = []
    root_values: list[int] = []

    for index in range(1, middle + 1):
        point = points[index]
        if point is None:
            raise AssertionError("unexpected identity")
        x_value, y_value = point
        root_zero = canonical_sqrt((x_value**3 + CURVE_B) % p, p)
        canonical_index = index if root_zero == y_value else n - index
        selector = 1 if canonical_index % 2 == 0 else p - 1
        expected = (
            (1 if index % 2 == 0 else p - 1)
            * (1 if quadratic_character(y_value, p) == 1 else p - 1)
        ) % p
        if selector != expected:
            raise AssertionError("canonical selector identity failed")
        xs.append(x_value)
        selector_values.append(selector)
        root_values.append(
            ((1 if index % 2 == 0 else p - 1) * y_value) % p
        )

    selector, kernel = interpolate(xs, selector_values, p)
    oriented_root, second_kernel = interpolate(xs, root_values, p)
    if kernel != second_kernel:
        raise AssertionError("Kummer kernels disagree")

    selector_square = poly_mod(
        poly_add(poly_mul(selector, selector, p), [1], p, -1),
        kernel,
        p,
    )
    if selector_square != [0]:
        raise AssertionError("C_G^2 != 1 mod K_H")

    inverse_two = pow(2, -1, p)
    idempotent = [
        ((1 if i == 0 else 0) - (selector[i] if i < len(selector) else 0))
        * inverse_two
        % p
        for i in range(max(1, len(selector)))
    ]
    if poly_mod(
        poly_add(poly_mul(idempotent, idempotent, p), idempotent, p, -1),
        kernel,
        p,
    ) != [0]:
        raise AssertionError("selector idempotent failed")

    if poly_mod(
        poly_add(
            poly_mul(oriented_root, oriented_root, p),
            [CURVE_B, 0, 0, 1],
            p,
            -1,
        ),
        kernel,
        p,
    ) != [0]:
        raise AssertionError("Y_G^2 != x^3+7 mod K_H")

    parity_checks = 0
    for scalar in range(1, n):
        point = points[scalar]
        if point is None:
            raise AssertionError("unexpected identity")
        x_value, y_value = point
        root_zero = canonical_sqrt((x_value**3 + CURVE_B) % p, p)
        decoded = (
            root_zero * poly_eval(selector, x_value, p) * pow(y_value, -1, p)
        ) % p
        if decoded != (1 if scalar % 2 == 0 else p - 1):
            raise AssertionError("parity bridge failed")
        parity_checks += 1

    negative_generator = (generator[0], -generator[1] % p)
    negative_points = orbit(negative_generator, n, p)
    negative_values: list[int] = []
    negative_xs: list[int] = []
    for index in range(1, middle + 1):
        point = negative_points[index]
        if point is None:
            raise AssertionError("unexpected identity")
        x_value, y_value = point
        root_zero = canonical_sqrt((x_value**3 + CURVE_B) % p, p)
        canonical_index = index if root_zero == y_value else n - index
        negative_xs.append(x_value)
        negative_values.append(1 if canonical_index % 2 == 0 else p - 1)
    negative_selector, negative_kernel = interpolate(negative_xs, negative_values, p)
    if negative_kernel != kernel:
        raise AssertionError("generator negation changed K_H")
    for index in range(max(len(selector), len(negative_selector))):
        left = selector[index] if index < len(selector) else 0
        right = negative_selector[index] if index < len(negative_selector) else 0
        if (left + right) % p:
            raise AssertionError("C_(-G) != -C_G")

    x_generator, y_generator = generator

    def delta_minus_generator(point: object) -> int:
        if point is None:
            return 0
        x_value, y_value = point
        x_equal = 1 - pow((x_value - x_generator) % p, p - 1, p)
        y_select = (1 - y_value * pow(y_generator, -1, p)) * inverse_two
        return x_equal * y_select % p

    delta_checks = 0
    for scalar, point in enumerate(points):
        if delta_minus_generator(point) != (1 if scalar == n - 1 else 0):
            raise AssertionError("coordinate delta failed")
        delta_checks += 1

    parity = [1 if scalar % 2 == 0 else p - 1 for scalar in range(n)]
    translated = [parity[(scalar + 1) % n] for scalar in range(n)]
    lhs = [(left + right) % p for left, right in zip(parity, translated, strict=True)]
    rhs = [0] * n
    rhs[n - 1] = 2
    if lhs != rhs:
        raise AssertionError("translation resolvent equation failed")

    seed = [0] * n
    seed[n - 1] = 1
    resolvent = [0] * n
    support: list[int] = []
    for exponent in range(n):
        sign = 1 if exponent % 2 == 0 else p - 1
        resolvent = [
            (current + sign * value) % p
            for current, value in zip(resolvent, seed, strict=True)
        ]
        support.append(sum(value != 0 for value in resolvent))
        if support[-1] != exponent + 1:
            raise AssertionError("unexpected point-basis support")
        seed = [seed[(scalar + 1) % n] for scalar in range(n)]
    if resolvent != parity:
        raise AssertionError("alternating resolvent failed")

    doubling_images: set[int] = set()
    for index in range(1, middle + 1):
        if 2 * index <= middle:
            unsigned_index, orientation = 2 * index, 1
        else:
            unsigned_index, orientation = n - 2 * index, -1
        if orientation != (1 if unsigned_index % 2 == 0 else -1):
            raise AssertionError("doubling cocycle failed")
        doubling_images.add(unsigned_index)
    if doubling_images != set(range(1, middle + 1)):
        raise AssertionError("unsigned doubling is not a permutation")

    determinant_checks = 0
    if n <= 67:
        base = [[0] * n for _ in range(n)]
        for row in range(n):
            base[row][row] = 1
            base[row][(row + 1) % n] += 1
        if determinant_mod(base, p) != 2:
            raise AssertionError("det(I+T_G) != 2")
        for scalar in range(n):
            updated = [row[:] for row in base]
            updated[n - 1][scalar] += 1
            expected = (2 + (1 if scalar % 2 == 0 else -1)) % p
            if determinant_mod(updated, p) != expected:
                raise AssertionError("rank-one determinant failed")
            determinant_checks += 1

    return {
        "p": p,
        "n": n,
        "generator": list(generator),
        "kummer_degree": middle,
        "selector_degree": len(selector) - 1,
        "oriented_root_degree": len(oriented_root) - 1,
        "parity_checks": parity_checks,
        "delta_checks": delta_checks,
        "point_basis_support": support[-1],
        "determinant_checks": determinant_checks,
        "all_checks_passed": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    cases = [check_case(p, n, generator) for p, n, generator in FROZEN_CASES]
    aggregate = {
        "case_count": len(cases),
        "all_cases_passed": all(case["all_checks_passed"] for case in cases),
        "all_point_basis_supports_equal_n": all(
            case["point_basis_support"] == case["n"] for case in cases
        ),
        "explicit_rank_one_determinant_checks": sum(
            case["determinant_checks"] for case in cases
        ),
        "evaluator_found": False,
        "parity_oracle_found": False,
        "sub_sqrt_ecdlp_found": False,
        "remaining_bottleneck": (
            "compact nonlinear application of (I+tau_G)^(-1) to delta_-G"
        ),
    }
    payload = {
        "experiment": "UORC056_TRANSLATION_RESOLVENT_C2",
        "scope": "six frozen toy subgroups only",
        "cases": cases,
        "aggregate": aggregate,
    }
    encoded = json.dumps(payload, indent=2, sort_keys=True)
    print(encoded)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(encoded + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
