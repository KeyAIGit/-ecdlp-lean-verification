#!/usr/bin/env python3
"""Toy-only finite-field character screen for PARITY-LIFT-000.

The script is restricted to five frozen prime-order toy curves. It does not
accept external curves, public keys, wallets, or production-sized inputs.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

Point = tuple[int, int] | None
Form = tuple[int, int, int]

FROZEN_CURVES = (
    (43, 31, (2, 12)),
    (67, 79, (2, 22)),
    (79, 67, (1, 18)),
    (127, 127, (1, 32)),
    (163, 139, (2, 34)),
)
DEEP_LIMITS = {43: 4, 67: 4, 79: 3}
P43_EXACT_FORMS: tuple[Form, ...] = (
    (1, 0, 17),
    (1, 1, 41),
    (1, 42, 41),
    (0, 1, 0),
)


@dataclass(frozen=True)
class CurveResult:
    p: int
    order: int
    generator: tuple[int, int]
    valid_projective_affine_lines: int
    unique_line_sign_vectors: int
    exact_weight_one: bool
    exact_weight_two: bool
    chi_y_best_matches: int
    chi_y_total: int
    chi_y_best_accuracy: float
    chi_y_best_generator_multiplier: int
    chi_y_best_global_sign: int
    deep_search_limit: int | None
    deep_minimum_weight: int | None
    deep_exact_forms: tuple[Form, ...] | None


def ec_add(P: Point, Q: Point, p: int) -> Point:
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
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
        raise AssertionError("generator does not have the frozen prime order")
    for affine in points[1:]:
        assert affine is not None
        x, y = affine
        if (y * y - x * x * x - 7) % p:
            raise AssertionError("point is not on y^2=x^3+7")
    return points


def quadratic_character(value: int, p: int) -> int:
    value %= p
    if value == 0:
        return 0
    return 1 if pow(value, (p - 1) // 2, p) == 1 else -1


def projective_normalized_affine_forms(p: int) -> Iterable[Form]:
    for b in range(p):
        for c in range(p):
            yield 1, b, c
    for c in range(p):
        yield 0, 1, c
    yield 0, 0, 1


def form_sign_bits(form: Form, points: list[Point], p: int) -> int | None:
    a, b, c = form
    bits = 0
    for index, point in enumerate(points[1:]):
        assert point is not None
        x, y = point
        value = (a * x + b * y + c) % p
        sign = quadratic_character(value, p)
        if sign == 0:
            return None
        if sign == -1:
            bits |= 1 << index
    return bits


def parity_target_bits(order: int) -> int:
    return sum(1 << index for index, k in enumerate(range(1, order)) if k & 1)


def equals_target_up_to_global_sign(bits: int, target: int, mask: int) -> bool:
    return bits == target or bits == (target ^ mask)


def enumerate_line_vectors(
    p: int, points: list[Point]
) -> tuple[int, dict[int, Form]]:
    valid = 0
    representatives: dict[int, Form] = {}
    for form in projective_normalized_affine_forms(p):
        bits = form_sign_bits(form, points, p)
        if bits is None:
            continue
        valid += 1
        representatives.setdefault(bits, form)
    return valid, representatives


def find_minimum_product(
    representatives: dict[int, Form], order: int, maximum_weight: int
) -> tuple[int, tuple[Form, ...]] | None:
    vectors = list(representatives)
    vector_set = set(vectors)
    target = parity_target_bits(order)
    mask = (1 << (order - 1)) - 1
    targets = (target, target ^ mask)

    for vector in vectors:
        if vector in targets:
            return 1, (representatives[vector],)
    if maximum_weight < 2:
        return None

    for vector in vectors:
        for desired in targets:
            partner = desired ^ vector
            if partner in vector_set:
                return 2, (representatives[vector], representatives[partner])
    if maximum_weight < 3:
        return None

    pair_representatives: dict[int, tuple[Form, Form]] = {}
    for index, left in enumerate(vectors):
        for right in vectors[index:]:
            pair_representatives.setdefault(
                left ^ right, (representatives[left], representatives[right])
            )

    for vector in vectors:
        for desired in targets:
            pair = pair_representatives.get(desired ^ vector)
            if pair is not None:
                return 3, (representatives[vector], *pair)
    if maximum_weight < 4:
        return None

    for pair_bits, left_pair in pair_representatives.items():
        for desired in targets:
            right_pair = pair_representatives.get(desired ^ pair_bits)
            if right_pair is not None:
                return 4, (*left_pair, *right_pair)
    return None


def evaluate_form_product(
    forms: tuple[Form, ...], points: list[Point], p: int
) -> int:
    bits = 0
    for index, point in enumerate(points[1:]):
        assert point is not None
        x, y = point
        value = 1
        for a, b, c in forms:
            value = value * (a * x + b * y + c) % p
        sign = quadratic_character(value, p)
        if sign == 0:
            raise AssertionError("frozen exact product has a zero")
        if sign == -1:
            bits |= 1 << index
    return bits


def best_chi_y(points: list[Point], p: int, order: int) -> tuple[int, int, int]:
    signs = {
        k: quadratic_character(points[k][1], p)  # type: ignore[index]
        for k in range(1, order)
    }
    best_matches = -1
    best_multiplier = -1
    best_global_sign = 1
    for multiplier in range(1, order):
        matches = sum(
            signs[(multiplier * k) % order] == (-1 if k & 1 else 1)
            for k in range(1, order)
        )
        if order - 1 - matches > matches:
            matches = order - 1 - matches
            global_sign = -1
        else:
            global_sign = 1
        if matches > best_matches:
            best_matches = matches
            best_multiplier = multiplier
            best_global_sign = global_sign
    return best_matches, best_multiplier, best_global_sign


def run_curve(
    p: int, order: int, generator: tuple[int, int], deep: bool
) -> CurveResult:
    points = orbit(generator, order, p)
    valid_count, representatives = enumerate_line_vectors(p, points)
    target = parity_target_bits(order)
    mask = (1 << (order - 1)) - 1
    vectors = set(representatives)
    exact_one = any(equals_target_up_to_global_sign(v, target, mask) for v in vectors)
    exact_two = any(
        (target ^ v) in vectors or ((target ^ mask) ^ v) in vectors
        for v in vectors
    )

    best_matches, best_multiplier, best_global_sign = best_chi_y(points, p, order)

    deep_limit = DEEP_LIMITS.get(p) if deep else None
    deep_result = (
        find_minimum_product(representatives, order, deep_limit)
        if deep_limit is not None
        else None
    )
    deep_weight = deep_result[0] if deep_result else None
    deep_forms = deep_result[1] if deep_result else None

    if p == 43:
        exact_bits = evaluate_form_product(P43_EXACT_FORMS, points, p)
        if exact_bits != target:
            raise AssertionError("frozen p=43 four-line identity drifted")
        if deep and (deep_weight != 4 or deep_forms != P43_EXACT_FORMS):
            raise AssertionError("p=43 minimum-weight replay drifted")
    if deep and p in (67, 79) and deep_result is not None:
        raise AssertionError("a new bounded exact product was unexpectedly found")

    return CurveResult(
        p=p,
        order=order,
        generator=generator,
        valid_projective_affine_lines=valid_count,
        unique_line_sign_vectors=len(representatives),
        exact_weight_one=exact_one,
        exact_weight_two=exact_two,
        chi_y_best_matches=best_matches,
        chi_y_total=order - 1,
        chi_y_best_accuracy=best_matches / (order - 1),
        chi_y_best_generator_multiplier=best_multiplier,
        chi_y_best_global_sign=best_global_sign,
        deep_search_limit=deep_limit,
        deep_minimum_weight=deep_weight,
        deep_exact_forms=deep_forms,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--deep",
        action="store_true",
        help="also run bounded weight-3/4 meet-in-the-middle searches",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).with_name("char_parity_toy_results.json"),
    )
    args = parser.parse_args()

    results = [run_curve(*curve, deep=args.deep) for curve in FROZEN_CURVES]
    payload = {
        "scope": "five frozen prime-order toy curves y^2=x^3+7 only",
        "deep_search": args.deep,
        "curves": [asdict(result) for result in results],
        "p43_exact_identity": {
            "generator": [2, 12],
            "formula": "(x+17)*(x+y+41)*(x+42*y+41)*y mod 43",
            "equals": "(-1)^k for Q=[k]G and 1<=k<31",
            "minimum_within_line_product_family": 4 if args.deep else None,
        },
        "claim_boundary": [
            "Finite toy interpolation is not an ECDLP algorithm.",
            "No external or production-sized input is accepted.",
            "Failure at bounded product weight is scoped to affine-line character factors.",
            "High algebraic degree may still admit low evaluation complexity.",
        ],
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
