#!/usr/bin/env python3
"""Exact toy replay for UORC056 ORIENTED HALF-DIVISOR INDEX B4.

No external curve, point, key, wallet, unknown scalar, or production-sized
ECDLP target is accepted.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Optional

Point = Optional[tuple[int, int]]
B_CURVE = 7
SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

FROZEN_CASES = (
    (13, 7, (7, 5)),
    (43, 31, (2, 12)),
    (61, 61, (2, 25)),
    (67, 79, (2, 22)),
    (79, 67, (1, 18)),
    (97, 79, (1, 28)),
    (127, 127, (1, 32)),
    (163, 139, (2, 34)),
    (211, 199, (3, 33)),
    (349, 313, (2, 109)),
)


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
        if y_left % p == 0:
            return None
        slope = 3 * x_left * x_left * pow(2 * y_left, -1, p) % p
    else:
        slope = (
            (y_right - y_left)
            * pow((x_right - x_left) % p, -1, p)
        ) % p
    x_sum = (slope * slope - x_left - x_right) % p
    y_sum = (slope * (x_left - x_sum) - y_left) % p
    return x_sum, y_sum


def ec_neg(point: Point, p: int) -> Point:
    if point is None:
        return None
    return point[0], (-point[1]) % p


def orbit(generator: tuple[int, int], order: int, p: int) -> list[Point]:
    points: list[Point] = [None]
    point: Point = None
    for _ in range(1, order):
        point = ec_add(point, generator, p)
        points.append(point)
    if ec_add(point, generator, p) is not None:
        raise AssertionError("declared order failed")
    if len(set(points)) != order:
        raise AssertionError("early orbit collision")
    return points


def point_sum(points: list[Point], labels: list[int], p: int) -> Point:
    total: Point = None
    for label in labels:
        total = ec_add(total, points[label], p)
    return total


def ceil_sqrt(value: int) -> int:
    root = math.isqrt(value)
    return root if root * root == value else root + 1


def run_case(
    p: int, order: int, generator: tuple[int, int]
) -> dict[str, object]:
    if (generator[1] * generator[1] - generator[0] ** 3 - B_CURVE) % p:
        raise AssertionError("generator is not on y^2=x^3+7")
    points = orbit(generator, order, p)
    half = (order - 1) // 2
    even_labels = list(range(2, order, 2))
    odd_labels = list(range(1, order, 2))
    if len(even_labels) != half or len(odd_labels) != half:
        raise AssertionError("unexpected parity-set cardinality")

    even_sum = point_sum(points, even_labels, p)
    odd_sum = point_sum(points, odd_labels, p)
    divisor_class_point = ec_add(even_sum, ec_neg(odd_sum, p), p)
    if divisor_class_point != points[half]:
        raise AssertionError("oriented divisor class was not [M]G")
    if divisor_class_point is None or math.gcd(half, order) != 1:
        raise AssertionError("oriented divisor class did not have order n")

    even_x = sorted(points[label][0] for label in even_labels if points[label])
    odd_x = sorted(points[label][0] for label in odd_labels if points[label])
    if even_x != odd_x:
        raise AssertionError("even and odd Kummer multisets differed")

    negative_generator = ec_neg(generator, p)
    if negative_generator is None:
        raise AssertionError("generator was the identity")
    negative_points = orbit(negative_generator, order, p)
    orientation_negation_checks = 0
    for label in range(1, half + 1):
        point = points[label]
        negative_point = negative_points[label]
        if point is None or negative_point is None:
            raise AssertionError("nonzero label produced identity")
        root_value = ((-1 if label % 2 else 1) * point[1]) % p
        negative_root_value = (
            (-1 if label % 2 else 1) * negative_point[1]
        ) % p
        if (root_value + negative_root_value) % p:
            raise AssertionError("marked root did not negate with generator")
        orientation_negation_checks += 1

    # Relax the index-system problem to cardinalities only. If a=#I, b=#J,
    # c=#K and the two injective disjoint images plus leftovers cover M labels,
    # then M <= 2ab+c. The work proxy W=a+b+c obeys n <= (W+1)^2.
    index_parameter_checks = 0
    best_work = half
    best_sizes = (0, 0, half)
    for size_i in range(half + 1):
        for size_j in range(half + 1):
            size_k = max(0, half - 2 * size_i * size_j)
            work = size_i + size_j + size_k
            if half > 2 * size_i * size_j + size_k:
                raise AssertionError("relaxed coverage failed")
            if order > (work + 1) ** 2:
                raise AssertionError("index square-root boundary failed")
            if work < best_work:
                best_work = work
                best_sizes = (size_i, size_j, size_k)
            index_parameter_checks += 1

    lower_bound = ceil_sqrt(order) - 1
    if best_work < lower_bound:
        raise AssertionError("relaxed optimum violated proved lower bound")

    return {
        "field_prime": p,
        "order": order,
        "generator": generator,
        "half_size": half,
        "parity_divisor_class_scalar": half,
        "parity_divisor_class_point": divisor_class_point,
        "class_has_exact_order_n": True,
        "even_odd_x_multisets_equal": True,
        "orientation_negation_checks": orientation_negation_checks,
        "index_parameter_checks": index_parameter_checks,
        "best_relaxed_index_work": best_work,
        "best_relaxed_index_sizes": best_sizes,
        "proved_index_work_lower_bound": lower_bound,
    }


def secp256k1_certificate() -> dict[str, object]:
    half = (SECP_N - 1) // 2
    lower_bound = ceil_sqrt(SECP_N) - 1
    return {
        "n": SECP_N,
        "bit_length": SECP_N.bit_length(),
        "half_size": half,
        "parity_divisor_class_scalar": half,
        "class_order": SECP_N,
        "standard_two_set_index_work_lower_bound": lower_bound,
        "lower_bound_is_2pow128_minus_1": lower_bound == 2**128 - 1,
        "standard_x_only_index_system_is_generator_blind": True,
        "does_standard_sqrt_velu_meet_fixed_epsilon_subroot": False,
        "central_target": "UNIFORM-ORIENTED-ROOT-CIRCUIT-056",
        "selected_successor": "UORC056-HIGHER-ARITY-INDEX-B5",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name(
            "uorc056_oriented_half_divisor_index_results.json"
        ),
    )
    args = parser.parse_args()

    cases = [run_case(*case) for case in FROZEN_CASES]
    payload = {
        "package": "UNIFORM-ORIENTED-ROOT-CIRCUIT-056-ORIENTED-HALF-DIVISOR-INDEX-B4",
        "cases": cases,
        "aggregate": {
            "cases": len(cases),
            "kummer_pairs": sum(case["half_size"] for case in cases),
            "orientation_negation_checks": sum(
                case["orientation_negation_checks"] for case in cases
            ),
            "index_parameter_checks": sum(
                case["index_parameter_checks"] for case in cases
            ),
            "all_classes_nontrivial_order_n": all(
                case["class_has_exact_order_n"] for case in cases
            ),
            "all_even_odd_x_multisets_equal": all(
                case["even_odd_x_multisets_equal"] for case in cases
            ),
            "all_index_work_bounds_hold": all(
                case["best_relaxed_index_work"]
                >= case["proved_index_work_lower_bound"]
                for case in cases
            ),
        },
        "secp256k1": secp256k1_certificate(),
        "decision": (
            "The oriented parity half-divisor has Picard class [M]G of exact "
            "order n, while its even and odd supports have the same Kummer "
            "x-multiset. Standard x-only square-root Velu data cannot choose "
            "the marked branch. Moreover every standard two-set index-system "
            "coverage with work W satisfies n <= (W+1)^2, giving the exact "
            "secp256k1 lower bound W >= 2^128-1 before resultant and branch "
            "costs. This mechanism reaches but cannot beat the square-root "
            "frontier."
        ),
        "claim_boundary": [
            "The point-sum/Picard-class arithmetic and Kummer multiset identity are exact.",
            "The index lower bound applies to the standard two-set injective-disjoint coverage architecture.",
            "It is not a lower bound against higher-arity, transposed, or unrestricted nonlinear circuits.",
            "No parity oracle, absolute EDS-residue oracle, or ECDLP improvement is obtained.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["aggregate"], indent=2))
    print(json.dumps(payload["secp256k1"], indent=2))


if __name__ == "__main__":
    main()
