#!/usr/bin/env python3
"""Toy-only structured character screen for PARITY-LIFT-000.

The screen studies quadratic characters of elliptic division-polynomial values
on five frozen prime-order curves. It accepts no external curves, keys, wallets,
or production-sized instances.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path

Point = tuple[int, int] | None

FROZEN_CURVES = (
    (43, 31, (2, 12)),
    (67, 79, (2, 22)),
    (79, 67, (1, 18)),
    (127, 127, (1, 32)),
    (163, 139, (2, 34)),
)
MAX_PRODUCT_WEIGHT = 4


@dataclass(frozen=True)
class CurveResult:
    p: int
    order: int
    generator: tuple[int, int]
    multiplication_formula_checks: int
    distinct_division_character_vectors: int
    exact_single_for_any_index_generator_and_sign: bool
    exact_product_or_ratio_up_to_weight_four: bool
    best_single_matches: int
    best_single_total: int
    best_single_accuracy: float
    smallest_best_index: int
    smallest_best_generator_multiplier: int
    smallest_best_global_sign: int
    index_two_is_best: bool


def ec_add(left: Point, right: Point, p: int) -> Point:
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if left == right:
        if y1 % p == 0:
            return None
        slope = 3 * x1 * x1 * pow(2 * y1, -1, p) % p
    else:
        slope = (y2 - y1) * pow((x2 - x1) % p, -1, p) % p
    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    return x3, y3


def orbit(generator: tuple[int, int], order: int, p: int) -> list[Point]:
    points: list[Point] = []
    point: Point = None
    for _ in range(order):
        points.append(point)
        point = ec_add(point, generator, p)
    if point is not None or len(set(points)) != order:
        raise AssertionError("frozen generator does not have the declared order")
    for affine in points[1:]:
        assert affine is not None
        x, y = affine
        if (y * y - x * x * x - 7) % p:
            raise AssertionError("frozen point is not on y^2=x^3+7")
    return points


def quadratic_character(value: int, p: int) -> int:
    value %= p
    if value == 0:
        return 0
    return 1 if pow(value, (p - 1) // 2, p) == 1 else -1


def division_polynomial_evaluator(point: tuple[int, int], p: int):
    """Evaluate psi_m at one point of y^2=x^3+7 using standard recurrences."""
    x, y = point

    @lru_cache(maxsize=None)
    def psi(index: int) -> int:
        if index < 0:
            return -psi(-index) % p
        if index == 0:
            return 0
        if index == 1:
            return 1
        if index == 2:
            return 2 * y % p
        if index == 3:
            return (3 * x**4 + 84 * x) % p
        if index == 4:
            return 4 * y * (x**6 + 140 * x**3 - 392) % p
        if index & 1:
            m = (index - 1) // 2
            return (
                psi(m + 2) * pow(psi(m), 3, p)
                - psi(m - 1) * pow(psi(m + 1), 3, p)
            ) % p
        m = index // 2
        return (
            psi(m)
            * pow(2 * y, -1, p)
            * (
                psi(m + 2) * pow(psi(m - 1), 2, p)
                - psi(m - 2) * pow(psi(m + 1), 2, p)
            )
        ) % p

    return psi


def bit_vector(signs: list[int]) -> int:
    result = 0
    for index, sign in enumerate(signs):
        if sign == -1:
            result |= 1 << index
        elif sign != 1:
            raise AssertionError("character sequence contains zero")
    return result


def parity_target(order: int) -> int:
    return sum(1 << (k - 1) for k in range(1, order) if k & 1)


def permute_by_generator(vector: int, multiplier: int, order: int) -> int:
    result = 0
    for k in range(1, order):
        source_index = (multiplier * k) % order - 1
        if vector >> source_index & 1:
            result |= 1 << (k - 1)
    return result


def exact_xor_weight_at_most_four(
    representatives: dict[int, int], target: int
) -> bool:
    vectors = list(representatives)
    vector_set = set(vectors)
    if target in vector_set:
        return True
    for left in vectors:
        if target ^ left in vector_set:
            return True

    pair_vectors: set[int] = set()
    for index, left in enumerate(vectors):
        for right in vectors[index:]:
            pair_vectors.add(left ^ right)

    for single in vectors:
        if target ^ single in pair_vectors:
            return True
    for pair in pair_vectors:
        if target ^ pair in pair_vectors:
            return True
    return False


def run_curve(p: int, order: int, generator: tuple[int, int]) -> CurveResult:
    points = orbit(generator, order, p)
    psi_generator = division_polynomial_evaluator(generator, p)

    multiplication_checks = 0
    character_vectors_by_index: dict[int, int] = {}

    for k in range(1, order):
        point = points[k]
        assert point is not None
        psi_point = division_polynomial_evaluator(point, p)
        denominator = psi_generator(k)
        if denominator == 0:
            raise AssertionError("nonzero scalar unexpectedly gives zero psi_k(G)")
        denominator_inverse = pow(denominator, -1, p)
        for m in range(1, order):
            direct = psi_point(m)
            transported = (
                psi_generator(m * k) * pow(denominator_inverse, m * m, p)
            ) % p
            if direct != transported:
                raise AssertionError("division-polynomial multiplication formula failed")
            multiplication_checks += 1

    for m in range(1, order):
        signs: list[int] = []
        for k in range(1, order):
            point = points[k]
            assert point is not None
            value = division_polynomial_evaluator(point, p)(m)
            sign = quadratic_character(value, p)
            if sign == 0:
                raise AssertionError("psi_m vanished in a prime-order nonzero orbit")
            signs.append(sign)
        character_vectors_by_index[m] = bit_vector(signs)

    representatives: dict[int, int] = {}
    for index, vector in character_vectors_by_index.items():
        representatives.setdefault(vector, index)

    target = parity_target(order)
    complement_mask = (1 << (order - 1)) - 1
    exact_single = False
    exact_product = False
    best_matches = -1
    best_tuple: tuple[int, int, int] | None = None
    best_indices: set[int] = set()

    for multiplier in range(1, order):
        permuted_representatives = {
            permute_by_generator(vector, multiplier, order): index
            for vector, index in representatives.items()
        }
        if target in permuted_representatives or target ^ complement_mask in permuted_representatives:
            exact_single = True
        if exact_xor_weight_at_most_four(permuted_representatives, target):
            exact_product = True
        if exact_xor_weight_at_most_four(
            permuted_representatives, target ^ complement_mask
        ):
            exact_product = True

        for index, vector in character_vectors_by_index.items():
            permuted = permute_by_generator(vector, multiplier, order)
            matches = order - 1 - (permuted ^ target).bit_count()
            global_sign = 1
            if order - 1 - matches > matches:
                matches = order - 1 - matches
                global_sign = -1
            if matches > best_matches:
                best_matches = matches
                best_tuple = (index, multiplier, global_sign)
                best_indices = {index}
            elif matches == best_matches:
                best_indices.add(index)
                assert best_tuple is not None
                best_tuple = min(best_tuple, (index, multiplier, global_sign))

    if exact_single or exact_product:
        raise AssertionError("unexpected exact structured parity decoder found")
    assert best_tuple is not None

    return CurveResult(
        p=p,
        order=order,
        generator=generator,
        multiplication_formula_checks=multiplication_checks,
        distinct_division_character_vectors=len(representatives),
        exact_single_for_any_index_generator_and_sign=exact_single,
        exact_product_or_ratio_up_to_weight_four=exact_product,
        best_single_matches=best_matches,
        best_single_total=order - 1,
        best_single_accuracy=best_matches / (order - 1),
        smallest_best_index=best_tuple[0],
        smallest_best_generator_multiplier=best_tuple[1],
        smallest_best_global_sign=best_tuple[2],
        index_two_is_best=2 in best_indices,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("structured_char_parity_results.json"),
    )
    args = parser.parse_args()

    results = [run_curve(*curve) for curve in FROZEN_CURVES]
    payload = {
        "scope": "five frozen prime-order toy curves y^2=x^3+7 only",
        "maximum_product_or_ratio_weight": MAX_PRODUCT_WEIGHT,
        "division_multiplication_formula": (
            "psi_m([k]G)=psi_(m*k)(G)/psi_k(G)^(m^2)"
        ),
        "curves": [asdict(result) for result in results],
        "aggregate": {
            "all_multiplication_formula_checks_passed": True,
            "exact_single_decoders_found": 0,
            "exact_product_or_ratio_decoders_found": 0,
            "index_two_reaches_the_best_single_accuracy_on_every_curve": all(
                result.index_two_is_best for result in results
            ),
        },
        "claim_boundary": [
            "This is a bounded toy negative, not an asymptotic lower bound.",
            "Quadratic character makes products and ratios equivalent at sign level.",
            "The screen does not cover sums, shifted arguments, theta identities, or unbounded product weight.",
            "No external or production-sized input is accepted.",
            "High algebraic degree can still have low recurrence or circuit complexity.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
