#!/usr/bin/env python3
"""Exact joint semantic circuit census for H-RPCX V5."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from math import isqrt
from pathlib import Path
from typing import Optional


PROFILE_ID = "UORC-056-HRPCX-EXACT-RATIONAL-SLP-CENSUS-V5"
Point = Optional[tuple[int, int]]
Semantic = tuple[tuple[int, ...], ...]


@dataclass(frozen=True)
class Curve:
    p: int
    n: int
    generator: tuple[int, int]
    orbit: tuple[tuple[int, int], ...]


def is_prime(value: int) -> bool:
    if value < 2:
        return False
    for divisor in range(2, isqrt(value) + 1):
        if value % divisor == 0:
            return False
    return True


def inverse(value: int, p: int) -> int:
    return pow(value % p, -1, p)


def point_add(left: Point, right: Point, p: int) -> Point:
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
        slope = 3 * x1 * x1 * inverse(2 * y1, p) % p
    else:
        slope = (y2 - y1) * inverse(x2 - x1, p) % p
    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    return x3, y3


def scalar_mul(k: int, point: Point, p: int) -> Point:
    out: Point = None
    addend = point
    while k:
        if k & 1:
            out = point_add(out, addend, p)
        addend = point_add(addend, addend, p)
        k >>= 1
    return out


def distinct_prime_factors(value: int) -> list[int]:
    factors: list[int] = []
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor == 0:
            factors.append(divisor)
            while value % divisor == 0:
                value //= divisor
        divisor += 1
    if value > 1:
        factors.append(value)
    return factors


def discover_curves(count: int = 5) -> list[Curve]:
    discovered: list[Curve] = []
    for p in range(11, 100):
        if not is_prime(p):
            continue
        affine_points: list[tuple[int, int]] = []
        for x in range(p):
            rhs = (x**3 + 7) % p
            for y in range(p):
                if y * y % p == rhs:
                    affine_points.append((x, y))
        group_order = len(affine_points) + 1
        eligible = sorted(
            (
                factor
                for factor in distinct_prime_factors(group_order)
                if is_prime(factor) and 5 <= factor <= 23
            ),
            reverse=True,
        )
        for n in eligible:
            cofactor = group_order // n
            generator: Point = None
            for point in affine_points:
                candidate = scalar_mul(cofactor, point, p)
                if candidate is not None and scalar_mul(n, candidate, p) is None:
                    generator = candidate
                    break
            if generator is None:
                continue
            orbit: list[tuple[int, int]] = []
            current: Point = None
            for _ in range(1, n):
                current = point_add(current, generator, p)
                if current is None:
                    raise AssertionError((p, n, "early closure"))
                orbit.append(current)
            if point_add(current, generator, p) is not None:
                raise AssertionError((p, n, "orbit did not close"))
            discovered.append(Curve(p, n, generator, tuple(orbit)))
            break
        if len(discovered) == count:
            break
    if len(discovered) != count:
        raise AssertionError(("insufficient curves", len(discovered)))
    return discovered


def base_semantic(curves: list[Curve], name: str) -> Semantic:
    blocks: list[tuple[int, ...]] = []
    for curve in curves:
        p = curve.p
        if name == "0":
            values = [0] * len(curve.orbit)
        elif name == "1":
            values = [1] * len(curve.orbit)
        elif name == "-1":
            values = [p - 1] * len(curve.orbit)
        elif name == "7":
            values = [7 % p] * len(curve.orbit)
        elif name == "gx":
            values = [curve.generator[0]] * len(curve.orbit)
        elif name == "gy":
            values = [curve.generator[1]] * len(curve.orbit)
        elif name == "x":
            values = [point[0] for point in curve.orbit]
        elif name == "y":
            values = [point[1] for point in curve.orbit]
        else:
            raise ValueError(name)
        blocks.append(tuple(values))
    return tuple(blocks)


def binary_operation(curves: list[Curve], left: Semantic, right: Semantic, operation: str) -> Semantic:
    blocks: list[tuple[int, ...]] = []
    for curve, left_block, right_block in zip(curves, left, right):
        p = curve.p
        if operation == "+":
            values = tuple((a + b) % p for a, b in zip(left_block, right_block))
        elif operation == "-":
            values = tuple((a - b) % p for a, b in zip(left_block, right_block))
        elif operation == "*":
            values = tuple(a * b % p for a, b in zip(left_block, right_block))
        else:
            raise ValueError(operation)
        blocks.append(values)
    return tuple(blocks)


def inverse_operation(curves: list[Curve], semantic: Semantic) -> Semantic | None:
    blocks: list[tuple[int, ...]] = []
    for curve, block in zip(curves, semantic):
        if any(value == 0 for value in block):
            return None
        blocks.append(tuple(inverse(value, curve.p) for value in block))
    return tuple(blocks)


def target_semantic(curves: list[Curve]) -> Semantic:
    return tuple(
        tuple(1 if k % 2 == 0 else curve.p - 1 for k in range(1, curve.n))
        for curve in curves
    )


def run(max_gates: int = 8, semantic_cap: int = 800_000) -> dict[str, object]:
    curves = discover_curves()
    base_names = ("0", "1", "-1", "7", "gx", "gy", "x", "y")
    expression_by_semantic: dict[Semantic, str] = {}
    by_cost: list[list[Semantic]] = [[]]
    for name in base_names:
        semantic = base_semantic(curves, name)
        if semantic not in expression_by_semantic:
            expression_by_semantic[semantic] = name
            by_cost[0].append(semantic)

    target = target_semantic(curves)
    found_cost: int | None = 0 if target in expression_by_semantic else None

    for cost in range(1, max_gates + 1):
        level: list[Semantic] = []

        for semantic in by_cost[cost - 1]:
            result = inverse_operation(curves, semantic)
            if result is not None and result not in expression_by_semantic:
                expression_by_semantic[result] = f"inv({expression_by_semantic[semantic]})"
                level.append(result)

        for left_cost in range(cost):
            right_cost = cost - 1 - left_cost
            for left in by_cost[left_cost]:
                for right in by_cost[right_cost]:
                    if left_cost < right_cost or (
                        left_cost == right_cost and repr(left) <= repr(right)
                    ):
                        for operation in ("+", "*"):
                            result = binary_operation(curves, left, right, operation)
                            if result not in expression_by_semantic:
                                expression_by_semantic[result] = (
                                    f"({expression_by_semantic[left]}{operation}{expression_by_semantic[right]})"
                                )
                                level.append(result)
                    result = binary_operation(curves, left, right, "-")
                    if result not in expression_by_semantic:
                        expression_by_semantic[result] = (
                            f"({expression_by_semantic[left]}-{expression_by_semantic[right]})"
                        )
                        level.append(result)

        by_cost.append(level)
        if target in expression_by_semantic:
            found_cost = cost
            break
        if len(expression_by_semantic) > semantic_cap:
            raise RuntimeError(
                {
                    "reason": "semantic cap exceeded",
                    "cost": cost,
                    "total": len(expression_by_semantic),
                    "per_level": [len(level_values) for level_values in by_cost],
                }
            )

    return {
        "profile_id": PROFILE_ID,
        "grammar": {
            "leaves": list(base_names),
            "gates": ["+", "-", "*", "inv(total-on-corpus)"],
            "max_gates": max_gates,
            "same_expression_on_all_curves": True,
            "search": "exact semantic dynamic programming",
        },
        "curves": [
            {
                "p": curve.p,
                "n": curve.n,
                "generator": list(curve.generator),
                "nonzero_points": len(curve.orbit),
            }
            for curve in curves
        ],
        "search_statistics": {
            "semantic_counts_by_exact_gate_cost": [len(level) for level in by_cost],
            "distinct_semantics": len(expression_by_semantic),
        },
        "result": {
            "exact_parity_circuit_found": found_cost is not None,
            "minimum_gate_cost_if_found": found_cost,
            "expression_if_found": expression_by_semantic.get(target),
        },
        "decision": {
            "exact_circuit_exists_within_declared_grammar_and_gate_bound": found_cost is not None,
            "negative_result_is_exhaustive_for_declared_class": found_cost is None,
            "general_arithmetic_circuit_lower_bound_proved": False,
            "larger_or_richer_circuit_search_open": True,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    parser.add_argument("--max-gates", type=int, default=8)
    args = parser.parse_args()
    result = run(max_gates=args.max_gates)
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
