#!/usr/bin/env python3
"""Deterministic structured high-degree macro-DAG screen for H-RPCX V9.

This is a discovery screen, not an exhaustive circuit lower bound. It searches
unary composition chains built from public coordinate states and high-degree
powering/CM-style macro gates. Every macro records an expanded arithmetic-DAG
cost; for example, pow2_254 is charged as 254 squarings. A final exact binary
join is searched over the retained library.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

PROFILE_ID = "UORC-056-HRPCX-STRUCTURED-HIGH-DEGREE-DAG-SCREEN-V9"
Point = Optional[tuple[int, int]]


@dataclass(frozen=True)
class Curve:
    p: int
    n: int
    generator: tuple[int, int]


CURVES = (
    Curve(43, 31, (2, 12)),
    Curve(67, 79, (2, 22)),
    Curve(79, 67, (1, 18)),
    Curve(127, 127, (1, 32)),
    Curve(163, 139, (2, 34)),
)
BASE_MULTIPLIERS = (1, 2, 3, 4, 5, 7, 8)
BEAM_WIDTH = 4000
MAX_DEPTH = 4


def inv(value: int, p: int) -> int:
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
        slope = 3 * x1 * x1 * inv(2 * y1, p) % p
    else:
        slope = (y2 - y1) * inv(x2 - x1, p) % p
    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    return x3, y3


def scalar_mul(k: int, point: Point, p: int) -> Point:
    out: Point = None
    while k:
        if k & 1:
            out = point_add(out, point, p)
        point = point_add(point, point, p)
        k //= 2
    return out


def beta(p: int) -> int:
    for value in range(2, p):
        if pow(value, 3, p) == 1:
            return value
    raise AssertionError((p, "no nontrivial cube root"))


def binary_power_cost(exponent: int) -> int:
    if exponent <= 1:
        return 0
    return exponent.bit_length() - 1 + exponent.bit_count() - 1


def build_context() -> tuple[tuple[tuple[Point, ...], ...], tuple[int, ...], bytes]:
    orbits = []
    for curve in CURVES:
        orbit = tuple(scalar_mul(k, curve.generator, curve.p) for k in range(1, curve.n))
        assert all(point is not None for point in orbit)
        assert scalar_mul(curve.n, curve.generator, curve.p) is None
        orbits.append(orbit)
    lengths = [len(orbit) for orbit in orbits]
    offsets = [0]
    for length in lengths:
        offsets.append(offsets[-1] + length)
    target = b"".join(
        bytes(1 if k % 2 == 0 else curve.p - 1 for k in range(1, curve.n))
        for curve in CURVES
    )
    return tuple(orbits), tuple(offsets), target


ORBITS, OFFSETS, TARGET = build_context()


def blocks(semantic: bytes) -> tuple[bytes, ...]:
    return tuple(semantic[OFFSETS[index] : OFFSETS[index + 1]] for index in range(len(CURVES)))


def public_constant(curve_index: int, name: str) -> int:
    curve = CURVES[curve_index]
    return {
        "1": 1,
        "7": 7,
        "gx": curve.generator[0],
        "gy": curve.generator[1],
        "beta": beta(curve.p),
    }[name]


def base_semantic(definition: tuple) -> bytes:
    out = []
    for curve, orbit in zip(CURVES, ORBITS):
        p = curve.p
        gx, gy = curve.generator
        cube_root = beta(p)
        values = []
        for point in orbit:
            assert point is not None
            x, y = point
            if definition[0] == "coord":
                _, axis, multiplier = definition
                multiple = scalar_mul(multiplier, point, p)
                assert multiple is not None
                value = multiple[0 if axis == "x" else 1]
            else:
                kind = definition[1]
                value = {
                    "x-gx": x - gx,
                    "y-gy": y - gy,
                    "x+gx": x + gx,
                    "y+gy": y + gy,
                    "x+y": x + y,
                    "x-y": x - y,
                    "x3": x**3,
                    "beta*x": cube_root * x,
                }[kind]
            values.append(value % p)
        out.append(bytes(values))
    return b"".join(out)


BASE_DEFINITIONS: list[tuple] = []
for multiplier in BASE_MULTIPLIERS:
    BASE_DEFINITIONS.extend((("coord", "x", multiplier), ("coord", "y", multiplier)))
for kind in ("x-gx", "y-gy", "x+gx", "y+gy", "x+y", "x-y", "x3", "beta*x"):
    BASE_DEFINITIONS.append(("expr", kind))


@dataclass(frozen=True)
class Operation:
    name: str
    tables: tuple[bytes, ...]
    invalid: tuple[frozenset[int], ...]
    expanded_cost: int


def make_table(function, p: int) -> bytes:
    return bytes(function(value % p, p) % p for value in range(256))


def operation(name: str, function, invalid=None, expanded_cost: int = 1) -> Operation:
    tables = []
    for index, curve in enumerate(CURVES):
        tables.append(make_table(lambda z, p, i=index: function(i, z, p), curve.p))
    if invalid is None:
        invalid = tuple(frozenset() for _ in CURVES)
    return Operation(name, tuple(tables), tuple(invalid), expanded_cost)


def operation_catalogue() -> tuple[Operation, ...]:
    operations: list[Operation] = []
    for constant_name in ("1", "7", "gx", "gy", "beta"):
        operations.append(
            operation("add_" + constant_name, lambda i, z, p, k=constant_name: z + public_constant(i, k))
        )
        operations.append(
            operation("sub_" + constant_name, lambda i, z, p, k=constant_name: z - public_constant(i, k))
        )
        operations.append(
            operation("mul_" + constant_name, lambda i, z, p, k=constant_name: z * public_constant(i, k))
        )
    operations.append(operation("neg", lambda i, z, p: -z))

    for count in (1, 2, 4, 8, 16, 32, 64, 128, 254):
        operations.append(
            operation(
                f"pow2_{count}",
                lambda i, z, p, c=count: pow(z, 1 << c, p),
                expanded_cost=count,
            )
        )
    for count in (1, 2, 4, 8, 16, 32):
        operations.append(
            operation(
                f"pow3_{count}",
                lambda i, z, p, c=count: pow(z, 3**c, p),
                expanded_cost=2 * count,
            )
        )

    exponent_families = (
        ("chi2", lambda curve: (curve.p - 1) // 2),
        ("chi3", lambda curve: (curve.p - 1) // 3),
        ("chi6", lambda curve: (curve.p - 1) // 6),
        ("pow_half_n", lambda curve: (curve.n - 1) // 2),
        ("pow_n", lambda curve: curve.n),
    )
    for name, exponent_fn in exponent_families:
        expanded = max(binary_power_cost(exponent_fn(curve)) for curve in CURVES)
        operations.append(
            operation(
                name,
                lambda i, z, p, ef=exponent_fn: pow(z, ef(CURVES[i]), p),
                expanded_cost=expanded,
            )
        )

    zero_invalid = tuple(frozenset({0}) for _ in CURVES)
    operations.append(
        operation("inv", lambda i, z, p: 0 if z == 0 else pow(z, -1, p), invalid=zero_invalid)
    )
    for constant_name in ("1", "7", "gx", "gy", "beta"):
        invalid = tuple(
            frozenset({public_constant(index, constant_name) % curve.p})
            for index, curve in enumerate(CURVES)
        )
        operations.append(
            operation(
                "mob_" + constant_name,
                lambda i, z, p, k=constant_name: (
                    (z + public_constant(i, k)) * pow((z - public_constant(i, k)) % p, -1, p)
                    if (z - public_constant(i, k)) % p
                    else 0
                ),
                invalid=invalid,
                expanded_cost=3,
            )
        )
    operations.append(
        operation(
            "lattes",
            lambda i, z, p: -(z + 28) ** 3 * pow((27 * z * z) % p, -1, p) if z else 0,
            invalid=zero_invalid,
            expanded_cost=8,
        )
    )
    return tuple(operations)


OPERATIONS = operation_catalogue()


def apply_operation(semantic: bytes, op: Operation) -> bytes | None:
    out = []
    for index, block in enumerate(blocks(semantic)):
        forbidden = op.invalid[index]
        if forbidden and any(value in forbidden for value in block):
            return None
        out.append(block.translate(op.tables[index]))
    return b"".join(out)


def error_count(semantic: bytes) -> int:
    return sum(left != right for left, right in zip(semantic, TARGET))


def complement(semantic: bytes, kind: str) -> bytes | None:
    out = []
    for curve, block, target_block in zip(CURVES, blocks(semantic), blocks(TARGET)):
        p = curve.p
        values = []
        for value, target in zip(block, target_block):
            if kind == "target_minus":
                result = target - value
            elif kind == "target_plus":
                result = target + value
            elif kind == "target_div":
                if value == 0:
                    return None
                result = target * pow(value, -1, p)
            elif kind == "value_div_target":
                result = value * pow(target, -1, p)
            else:
                raise ValueError(kind)
            values.append(result % p)
        out.append(bytes(values))
    return b"".join(out)


def run() -> dict[str, object]:
    seen: dict[bytes, dict[str, object]] = {}
    frontier = []
    for definition in BASE_DEFINITIONS:
        semantic = base_semantic(definition)
        if semantic not in seen:
            seen[semantic] = {
                "expression": repr(definition),
                "depth": 0,
                "expanded_cost": 0,
                "errors": error_count(semantic),
            }
            frontier.append(semantic)

    layers = []
    exact = None
    for depth in range(1, MAX_DEPTH + 1):
        candidates: dict[bytes, dict[str, object]] = {}
        for semantic in frontier:
            parent = seen[semantic]
            for op in OPERATIONS:
                result = apply_operation(semantic, op)
                if result is None or result in seen or result in candidates:
                    continue
                record = {
                    "expression": f"{op.name}({parent['expression']})",
                    "depth": depth,
                    "expanded_cost": int(parent["expanded_cost"]) + op.expanded_cost,
                    "errors": error_count(result),
                }
                candidates[result] = record
                if result == TARGET:
                    exact = record
                    break
            if exact:
                break

        ordered = sorted(
            candidates.items(),
            key=lambda item: (item[1]["errors"], item[1]["expanded_cost"], item[0]),
        )
        raw_count = len(ordered)
        retained = ordered[:BEAM_WIDTH]
        for semantic, record in retained:
            seen[semantic] = record
        frontier = [semantic for semantic, _ in retained]
        layers.append(
            {
                "depth": depth,
                "raw_new_semantics": raw_count,
                "retained": len(retained),
                "best_errors": retained[0][1]["errors"] if retained else None,
                "best_expression": retained[0][1]["expression"] if retained else None,
                "best_expanded_cost": retained[0][1]["expanded_cost"] if retained else None,
            }
        )
        if exact or not frontier:
            break

    join = None
    library = set(seen)
    if exact is None:
        for semantic, record in list(seen.items()):
            tests = (
                ("add", complement(semantic, "target_minus")),
                ("subtract", complement(semantic, "target_plus")),
                ("multiply", complement(semantic, "target_div")),
                ("divide", complement(semantic, "value_div_target")),
            )
            for operation_name, needed in tests:
                if needed is not None and needed in library:
                    other = seen[needed]
                    join = {
                        "operation": operation_name,
                        "left": record["expression"],
                        "right": other["expression"],
                        "expanded_cost": int(record["expanded_cost"]) + int(other["expanded_cost"]) + 1,
                    }
                    break
            if join:
                break

    best = min(
        seen.values(),
        key=lambda record: (record["errors"], record["expanded_cost"], record["expression"]),
    )
    return {
        "profile_id": PROFILE_ID,
        "status": "deterministic_discovery_screen_not_exhaustive_beyond_depth_one",
        "corpus": {
            "curves": [
                {"p": curve.p, "n": curve.n, "generator": list(curve.generator)}
                for curve in CURVES
            ],
            "nonzero_points": len(TARGET),
        },
        "grammar": {
            "base_states": len(BASE_DEFINITIONS),
            "unary_macros": len(OPERATIONS),
            "max_macro_depth": MAX_DEPTH,
            "beam_width": BEAM_WIDTH,
            "power_macros_charge_expanded_DAG_cost": True,
            "largest_single_macro_cost": max(op.expanded_cost for op in OPERATIONS),
            "final_binary_joins": ["+", "-", "*", "/"],
        },
        "layers": layers,
        "search_statistics": {"retained_semantics": len(seen)},
        "result": {
            "exact_unary_candidate": exact,
            "exact_binary_join_candidate": join,
            "best_retained_errors": best["errors"],
            "best_retained_expression": best["expression"],
            "best_retained_expanded_cost": best["expanded_cost"],
        },
        "decision": {
            "parity_algorithm_found": bool(exact or join),
            "declared_class_exhaustively_closed": False,
            "negative_result_is_heuristic": not bool(exact or join),
            "continue_with_multiregister_DAG_templates": True,
        },
        "claim_boundary": {
            "proved": "deterministic replay of the stated beam and exact joins over its retained library",
            "not_proved": [
                "nonexistence of a structured high-degree DAG evaluator",
                "completeness beyond the unpruned first macro layer",
                "nonexistence of multiregister or secp256k1-specialized circuits",
            ],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    rendered = json.dumps(run(), indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
