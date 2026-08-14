#!/usr/bin/env python3
"""Deterministic multi-curve circuit synthesis for UORC-056.

This executable is deliberately restricted to the five frozen prime-order toy
curves already present in PARITY-LIFT-000.  It accepts no external curve, point,
scalar, key, or wallet input.

The search asks a stricter question than finite interpolation: can one and the
same symbolic product of bounded quadratic-character atoms compute

    Q=[k]G  ->  (-1)^k

on several fields without fitting coefficients separately for each field?

A positive toy result is only a transfer seed.  A negative result is only a
bounded-grammar negative.  Neither is a production ECDLP claim.
"""
from __future__ import annotations

import argparse
import heapq
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence

Point = tuple[int, int] | None

FROZEN_CURVES: tuple[tuple[int, int, tuple[int, int]], ...] = (
    (43, 31, (2, 12)),
    (67, 79, (2, 22)),
    (79, 67, (1, 18)),
    (127, 127, (1, 32)),
    (163, 139, (2, 34)),
)

OBSERVABLE_NAMES: tuple[str, ...] = (
    "x1",
    "y1",
    "x2",
    "y2",
    "x3",
    "y3",
    "x4",
    "y4",
    "beta_x1",
    "beta2_x1",
    "doubling_slope",
    "chord_1_2",
)

CONSTANT_NAMES: tuple[str, ...] = (
    "zero",
    "one",
    "neg_one",
    "curve_b",
    "neg_curve_b",
    "beta",
    "beta2",
    "gx1",
    "gy1",
    "gx2",
    "gy2",
    "gx3",
    "gy3",
)

BINARY_CONSTANT_NAMES: tuple[str, ...] = (
    "zero",
    "one",
    "neg_one",
    "two",
    "neg_two",
    "curve_b",
    "neg_curve_b",
)

FEATURE_UPPER_COST: dict[str, dict[str, int]] = {
    "x1": {},
    "y1": {},
    "x2": {"group_double": 1},
    "y2": {"group_double": 1},
    "x3": {"group_double": 1, "group_add": 1},
    "y3": {"group_double": 1, "group_add": 1},
    "x4": {"group_double": 2},
    "y4": {"group_double": 2},
    "beta_x1": {"field_mul": 1},
    "beta2_x1": {"field_mul": 1},
    "doubling_slope": {"field_mul": 3, "field_inv": 1},
    "chord_1_2": {
        "group_double": 1,
        "field_add": 2,
        "field_mul": 1,
        "field_inv": 1,
    },
}


@dataclass(frozen=True)
class CurveContext:
    p: int
    order: int
    generator: tuple[int, int]
    points: tuple[Point, ...]
    beta: int
    beta2: int

    @property
    def curve_id(self) -> str:
        return f"E7-P{self.p}-N{self.order}"


@dataclass(frozen=True)
class AtomSpec:
    kind: str
    left: str | None = None
    right: str | None = None
    sign: int = 1
    constant: str = "zero"

    @property
    def atom_id(self) -> str:
        if self.kind == "phase":
            return f"phase:{self.constant}"
        if self.kind == "unary":
            return f"unary:{self.left}:{self.constant}"
        if self.kind == "sum":
            op = "plus" if self.sign == 1 else "minus"
            return f"sum:{self.left}:{op}:{self.right}:{self.constant}"
        if self.kind == "mul":
            return f"mul:{self.left}:{self.right}:{self.constant}"
        raise ValueError(f"unknown atom kind: {self.kind}")

    @property
    def features(self) -> tuple[str, ...]:
        if self.kind == "phase":
            return ()
        if self.kind == "unary":
            assert self.left is not None
            return (self.left,)
        assert self.left is not None and self.right is not None
        return (self.left, self.right)

    def render(self) -> str:
        if self.kind == "phase":
            body = self.constant
        elif self.kind == "unary":
            assert self.left is not None
            body = self.left if self.constant == "zero" else f"({self.left}+{self.constant})"
        elif self.kind == "sum":
            assert self.left is not None and self.right is not None
            op = "+" if self.sign == 1 else "-"
            body = f"({self.left}{op}{self.right}"
            if self.constant != "zero":
                body += f"+{self.constant}"
            body += ")"
        elif self.kind == "mul":
            assert self.left is not None and self.right is not None
            body = f"({self.left}*{self.right}"
            if self.constant != "zero":
                body += f"+{self.constant}"
            body += ")"
        else:
            raise ValueError(f"unknown atom kind: {self.kind}")
        return f"chi({body})"


@dataclass(frozen=True)
class CompiledAtom:
    spec: AtomSpec
    curve_bits: tuple[int | None, ...]


@dataclass(frozen=True)
class PoolEntry:
    atom_index: int
    vector: int


@dataclass(frozen=True)
class SearchOutcome:
    subset: tuple[int, ...]
    pool_size: int
    semantic_classes: int
    target_bits: int
    found: bool
    minimum_weight: int | None
    candidates: tuple[tuple[int, ...], ...]


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


def build_orbit(generator: tuple[int, int], order: int, p: int) -> tuple[Point, ...]:
    points: list[Point] = []
    point: Point = None
    for _ in range(order):
        points.append(point)
        point = ec_add(point, generator, p)
    if point is not None or len(set(points)) != order:
        raise AssertionError("declared generator does not have the frozen prime order")
    for affine in points[1:]:
        assert affine is not None
        x, y = affine
        if (y * y - x * x * x - 7) % p:
            raise AssertionError("frozen point is not on y^2=x^3+7")
    return tuple(points)


def build_context(p: int, order: int, generator: tuple[int, int]) -> CurveContext:
    roots = [value for value in range(2, p) if (value * value + value + 1) % p == 0]
    if len(roots) != 2:
        raise AssertionError("expected two nontrivial cube roots of unity")
    beta, beta2 = sorted(roots)
    if beta * beta % p != beta2 or beta2 * beta2 % p != beta:
        raise AssertionError("cube-root ordering invariant failed")
    return CurveContext(
        p=p,
        order=order,
        generator=generator,
        points=build_orbit(generator, order, p),
        beta=beta,
        beta2=beta2,
    )


def quadratic_character(value: int, p: int) -> int:
    value %= p
    if value == 0:
        return 0
    residue = pow(value, (p - 1) // 2, p)
    if residue == 1:
        return 1
    if residue == p - 1:
        return -1
    raise AssertionError("Euler criterion returned a non-sign")


def affine_point(context: CurveContext, scalar: int) -> tuple[int, int]:
    point = context.points[scalar % context.order]
    if point is None:
        raise AssertionError("unexpected identity in a nonzero small multiple")
    return point


def observable_row(context: CurveContext, k: int) -> dict[str, int]:
    p = context.p
    x1, y1 = affine_point(context, k)
    x2, y2 = affine_point(context, 2 * k)
    x3, y3 = affine_point(context, 3 * k)
    x4, y4 = affine_point(context, 4 * k)
    if y1 % p == 0:
        raise AssertionError("odd prime-order orbit unexpectedly contains 2-torsion")
    if (x2 - x1) % p == 0:
        raise AssertionError("chord denominator vanished; this would imply 3-torsion")
    doubling_slope = 3 * x1 * x1 * pow(2 * y1, -1, p) % p
    chord_1_2 = (y2 - y1) * pow((x2 - x1) % p, -1, p) % p
    return {
        "x1": x1,
        "y1": y1,
        "x2": x2,
        "y2": y2,
        "x3": x3,
        "y3": y3,
        "x4": x4,
        "y4": y4,
        "beta_x1": context.beta * x1 % p,
        "beta2_x1": context.beta2 * x1 % p,
        "doubling_slope": doubling_slope,
        "chord_1_2": chord_1_2,
    }


def constant_values(context: CurveContext) -> dict[str, int]:
    p = context.p
    gx1, gy1 = affine_point(context, 1)
    gx2, gy2 = affine_point(context, 2)
    gx3, gy3 = affine_point(context, 3)
    return {
        "zero": 0,
        "one": 1,
        "neg_one": -1 % p,
        "two": 2,
        "neg_two": -2 % p,
        "curve_b": 7 % p,
        "neg_curve_b": -7 % p,
        "beta": context.beta,
        "beta2": context.beta2,
        "gx1": gx1,
        "gy1": gy1,
        "gx2": gx2,
        "gy2": gy2,
        "gx3": gx3,
        "gy3": gy3,
    }


def generate_specs() -> tuple[AtomSpec, ...]:
    specs: list[AtomSpec] = []
    for constant in CONSTANT_NAMES:
        specs.append(AtomSpec(kind="phase", constant=constant))
    for observable in OBSERVABLE_NAMES:
        for constant in CONSTANT_NAMES:
            specs.append(AtomSpec(kind="unary", left=observable, constant=constant))
    for left_index, left in enumerate(OBSERVABLE_NAMES):
        for right in OBSERVABLE_NAMES[left_index + 1 :]:
            for sign in (1, -1):
                for constant in BINARY_CONSTANT_NAMES:
                    specs.append(
                        AtomSpec(
                            kind="sum",
                            left=left,
                            right=right,
                            sign=sign,
                            constant=constant,
                        )
                    )
    for left_index, left in enumerate(OBSERVABLE_NAMES):
        for right in OBSERVABLE_NAMES[left_index:]:
            for constant in BINARY_CONSTANT_NAMES:
                specs.append(
                    AtomSpec(kind="mul", left=left, right=right, constant=constant)
                )
    atom_ids = [spec.atom_id for spec in specs]
    if len(atom_ids) != len(set(atom_ids)):
        raise AssertionError("atom catalogue is not unique")
    return tuple(specs)


def evaluate_spec(
    spec: AtomSpec, row: dict[str, int], constants: dict[str, int], p: int
) -> int:
    constant = constants[spec.constant]
    if spec.kind == "phase":
        return constant
    assert spec.left is not None
    left = row[spec.left]
    if spec.kind == "unary":
        return (left + constant) % p
    assert spec.right is not None
    right = row[spec.right]
    if spec.kind == "sum":
        return (left + spec.sign * right + constant) % p
    if spec.kind == "mul":
        return (left * right + constant) % p
    raise ValueError(f"unknown atom kind: {spec.kind}")


def compile_atoms(
    contexts: Sequence[CurveContext], specs: Sequence[AtomSpec]
) -> tuple[CompiledAtom, ...]:
    rows_by_curve = [
        [observable_row(context, k) for k in range(1, context.order)]
        for context in contexts
    ]
    constants_by_curve = [constant_values(context) for context in contexts]
    compiled: list[CompiledAtom] = []
    for spec in specs:
        curve_bits: list[int | None] = []
        for context, rows, constants in zip(
            contexts, rows_by_curve, constants_by_curve, strict=True
        ):
            bits = 0
            valid = True
            for offset, row in enumerate(rows):
                sign = quadratic_character(
                    evaluate_spec(spec, row, constants, context.p), context.p
                )
                if sign == 0:
                    valid = False
                    break
                if sign == -1:
                    bits |= 1 << offset
            curve_bits.append(bits if valid else None)
        compiled.append(CompiledAtom(spec=spec, curve_bits=tuple(curve_bits)))
    return tuple(compiled)


def parity_target(order: int) -> int:
    return sum(1 << (k - 1) for k in range(1, order) if k & 1)


def pack_bits(
    curve_bits: Sequence[int | None],
    contexts: Sequence[CurveContext],
    subset: Sequence[int],
) -> int | None:
    packed = 0
    offset = 0
    for curve_index in subset:
        bits = curve_bits[curve_index]
        if bits is None:
            return None
        packed |= bits << offset
        offset += contexts[curve_index].order - 1
    return packed


def packed_target(contexts: Sequence[CurveContext], subset: Sequence[int]) -> int:
    packed = 0
    offset = 0
    for curve_index in subset:
        context = contexts[curve_index]
        packed |= parity_target(context.order) << offset
        offset += context.order - 1
    return packed


def packed_length(contexts: Sequence[CurveContext], subset: Sequence[int]) -> int:
    return sum(contexts[index].order - 1 for index in subset)


def spec_internal_cost(spec: AtomSpec) -> dict[str, int]:
    cost = {"field_add": 0, "field_mul": 0}
    if spec.kind == "unary":
        if spec.constant != "zero":
            cost["field_add"] += 1
    elif spec.kind == "sum":
        cost["field_add"] += 1
        if spec.constant != "zero":
            cost["field_add"] += 1
    elif spec.kind == "mul":
        cost["field_mul"] += 1
        if spec.constant != "zero":
            cost["field_add"] += 1
    return cost


def atom_rank(spec: AtomSpec) -> tuple[int, int, int, int, str]:
    feature_cost = {"field_add": 0, "field_mul": 0, "field_inv": 0, "group_add": 0, "group_double": 0}
    for feature in set(spec.features):
        for name, amount in FEATURE_UPPER_COST[feature].items():
            feature_cost[name] += amount
    internal = spec_internal_cost(spec)
    feature_cost["field_add"] += internal["field_add"]
    feature_cost["field_mul"] += internal["field_mul"]
    return (
        feature_cost["field_inv"],
        feature_cost["group_add"] + feature_cost["group_double"],
        feature_cost["field_mul"],
        feature_cost["field_add"],
        spec.atom_id,
    )


def build_pool(
    compiled: Sequence[CompiledAtom],
    contexts: Sequence[CurveContext],
    subset: Sequence[int],
) -> tuple[PoolEntry, ...]:
    best_by_semantics: dict[int, int] = {}
    for atom_index, atom in enumerate(compiled):
        vector = pack_bits(atom.curve_bits, contexts, subset)
        if vector is None:
            continue
        previous = best_by_semantics.get(vector)
        if previous is None or atom_rank(atom.spec) < atom_rank(compiled[previous].spec):
            best_by_semantics[vector] = atom_index
    return tuple(
        PoolEntry(atom_index=atom_index, vector=vector)
        for vector, atom_index in sorted(best_by_semantics.items(), key=lambda item: item[1])
    )


def _decode_pair(packed_pair: int) -> tuple[int, int]:
    return packed_pair >> 16, packed_pair & 0xFFFF


def _canonical_candidate(pool: Sequence[PoolEntry], local_indices: Iterable[int]) -> tuple[int, ...]:
    return tuple(sorted(pool[index].atom_index for index in local_indices))


def search_exact(
    compiled: Sequence[CompiledAtom],
    contexts: Sequence[CurveContext],
    subset: Sequence[int],
    maximum_weight: int = 4,
    maximum_candidates: int = 4,
) -> SearchOutcome:
    subset_tuple = tuple(subset)
    pool = build_pool(compiled, contexts, subset_tuple)
    target = packed_target(contexts, subset_tuple)
    if len(pool) >= 65536:
        raise AssertionError("pair packing assumes fewer than 65536 semantic atoms")

    candidates: set[tuple[int, ...]] = set()
    for local_index, entry in enumerate(pool):
        if entry.vector == target:
            candidates.add(_canonical_candidate(pool, (local_index,)))
    if candidates:
        return SearchOutcome(
            subset=subset_tuple,
            pool_size=len(pool),
            semantic_classes=len(pool),
            target_bits=packed_length(contexts, subset_tuple),
            found=True,
            minimum_weight=1,
            candidates=tuple(sorted(candidates)[:maximum_candidates]),
        )
    if maximum_weight < 2:
        return SearchOutcome(subset_tuple, len(pool), len(pool), packed_length(contexts, subset_tuple), False, None, ())

    pair_map: dict[int, int] = {}
    weight_two: set[tuple[int, ...]] = set()
    for left in range(len(pool)):
        left_vector = pool[left].vector
        for right in range(left + 1, len(pool)):
            semantics = left_vector ^ pool[right].vector
            pair_map.setdefault(semantics, (left << 16) | right)
            if semantics == target and len(weight_two) < maximum_candidates:
                weight_two.add(_canonical_candidate(pool, (left, right)))
    if weight_two:
        return SearchOutcome(
            subset=subset_tuple,
            pool_size=len(pool),
            semantic_classes=len(pool),
            target_bits=packed_length(contexts, subset_tuple),
            found=True,
            minimum_weight=2,
            candidates=tuple(sorted(weight_two)[:maximum_candidates]),
        )
    if maximum_weight < 3:
        return SearchOutcome(subset_tuple, len(pool), len(pool), packed_length(contexts, subset_tuple), False, None, ())

    weight_three: set[tuple[int, ...]] = set()
    for single in range(len(pool)):
        pair = pair_map.get(target ^ pool[single].vector)
        if pair is None:
            continue
        left, right = _decode_pair(pair)
        if single in (left, right):
            continue
        weight_three.add(_canonical_candidate(pool, (single, left, right)))
        if len(weight_three) >= maximum_candidates:
            break
    if weight_three:
        return SearchOutcome(
            subset=subset_tuple,
            pool_size=len(pool),
            semantic_classes=len(pool),
            target_bits=packed_length(contexts, subset_tuple),
            found=True,
            minimum_weight=3,
            candidates=tuple(sorted(weight_three)[:maximum_candidates]),
        )
    if maximum_weight < 4:
        return SearchOutcome(subset_tuple, len(pool), len(pool), packed_length(contexts, subset_tuple), False, None, ())

    weight_four: set[tuple[int, ...]] = set()
    for semantics, first_pair in pair_map.items():
        second_semantics = target ^ semantics
        if semantics > second_semantics:
            continue
        second_pair = pair_map.get(second_semantics)
        if second_pair is None:
            continue
        a, b = _decode_pair(first_pair)
        c, d = _decode_pair(second_pair)
        if len({a, b, c, d}) != 4:
            continue
        weight_four.add(_canonical_candidate(pool, (a, b, c, d)))
        if len(weight_four) >= maximum_candidates:
            break
    return SearchOutcome(
        subset=subset_tuple,
        pool_size=len(pool),
        semantic_classes=len(pool),
        target_bits=packed_length(contexts, subset_tuple),
        found=bool(weight_four),
        minimum_weight=4 if weight_four else None,
        candidates=tuple(sorted(weight_four)[:maximum_candidates]),
    )


def candidate_cost(
    compiled: Sequence[CompiledAtom], candidate: Sequence[int]
) -> dict[str, object]:
    features: set[str] = set()
    constants: set[str] = set()
    operations = {
        "field_add": 0,
        "field_mul": 0,
        "field_inv": 0,
        "group_add": 0,
        "group_double": 0,
        "quadratic_character": len(candidate),
        "sign_mul": max(0, len(candidate) - 1),
    }
    for atom_index in candidate:
        spec = compiled[atom_index].spec
        features.update(spec.features)
        constants.add(spec.constant)
        internal = spec_internal_cost(spec)
        operations["field_add"] += internal["field_add"]
        operations["field_mul"] += internal["field_mul"]
    for feature in features:
        for name, amount in FEATURE_UPPER_COST[feature].items():
            operations[name] += amount
    return {
        "operation_upper_bound": operations,
        "shared_observables": sorted(features),
        "public_constant_expressions": sorted(constants),
        "notes": [
            "The count is a conservative online upper bound after sharing identical named observables.",
            "It does not make finite-field inversion or quadratic character free.",
            "Construction and validation of public constants remain part of preprocessing/representation cost.",
        ],
    }


def evaluate_candidate(
    compiled: Sequence[CompiledAtom],
    contexts: Sequence[CurveContext],
    candidate: Sequence[int],
) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for curve_index, context in enumerate(contexts):
        value = 0
        defined = True
        for atom_index in candidate:
            bits = compiled[atom_index].curve_bits[curve_index]
            if bits is None:
                defined = False
                break
            value ^= bits
        target = parity_target(context.order)
        total = context.order - 1
        if defined:
            errors = (value ^ target).bit_count()
            matches = total - errors
            exact = errors == 0
            accuracy = matches / total
        else:
            errors = None
            matches = None
            exact = False
            accuracy = None
        results.append(
            {
                "curve_id": context.curve_id,
                "defined_on_full_nonzero_orbit": defined,
                "exact": exact,
                "matches": matches,
                "total": total,
                "accuracy": accuracy,
                "errors": errors,
            }
        )
    return results


def serialize_candidate(
    compiled: Sequence[CompiledAtom],
    contexts: Sequence[CurveContext],
    candidate: Sequence[int],
) -> dict[str, object]:
    atoms = [compiled[index].spec for index in candidate]
    return {
        "atom_ids": [atom.atom_id for atom in atoms],
        "formula": " * ".join(atom.render() for atom in atoms),
        "weight": len(candidate),
        "curve_validation": evaluate_candidate(compiled, contexts, candidate),
        "cost": candidate_cost(compiled, candidate),
    }


def serialize_outcome(
    outcome: SearchOutcome,
    compiled: Sequence[CompiledAtom],
    contexts: Sequence[CurveContext],
) -> dict[str, object]:
    return {
        "subset": [contexts[index].curve_id for index in outcome.subset],
        "pool_size_after_zero_rejection_and_semantic_quotient": outcome.pool_size,
        "semantic_classes": outcome.semantic_classes,
        "target_bits": outcome.target_bits,
        "found": outcome.found,
        "minimum_weight": outcome.minimum_weight,
        "candidates": [
            serialize_candidate(compiled, contexts, candidate)
            for candidate in outcome.candidates
        ],
    }


def _push_beam(
    heap: list[tuple[int, int, tuple[int, ...], int]],
    beam_size: int,
    distance: int,
    serial: int,
    candidate: tuple[int, ...],
    vector: int,
) -> None:
    item = (-distance, -serial, candidate, vector)
    if len(heap) < beam_size:
        heapq.heappush(heap, item)
    elif item > heap[0]:
        heapq.heapreplace(heap, item)


def near_miss_beam(
    compiled: Sequence[CompiledAtom],
    contexts: Sequence[CurveContext],
    subset: Sequence[int],
    beam_size: int,
) -> dict[str, object]:
    subset_tuple = tuple(subset)
    pool = build_pool(compiled, contexts, subset_tuple)
    target = packed_target(contexts, subset_tuple)
    total = packed_length(contexts, subset_tuple)
    if not pool:
        return {"found": false, "reason": "empty pool"}  # type: ignore[name-defined]

    best_distance = total + 1
    best_candidate: tuple[int, ...] = ()
    best_vector = 0
    for entry in pool:
        distance = (entry.vector ^ target).bit_count()
        candidate = (entry.atom_index,)
        if (distance, candidate) < (best_distance, best_candidate):
            best_distance, best_candidate, best_vector = distance, candidate, entry.vector

    pair_heap: list[tuple[int, int, tuple[int, ...], int]] = []
    serial = 0
    for left in range(len(pool)):
        for right in range(left + 1, len(pool)):
            vector = pool[left].vector ^ pool[right].vector
            candidate = tuple(sorted((pool[left].atom_index, pool[right].atom_index)))
            distance = (vector ^ target).bit_count()
            serial += 1
            _push_beam(pair_heap, beam_size, distance, serial, candidate, vector)
            if (distance, candidate) < (best_distance, best_candidate):
                best_distance, best_candidate, best_vector = distance, candidate, vector

    pair_beam = [
        (candidate, vector)
        for _, _, candidate, vector in sorted(pair_heap, reverse=True)
    ]
    seen: set[tuple[int, ...]] = set()
    for pair_candidate, pair_vector in pair_beam:
        pair_set = set(pair_candidate)
        for entry in pool:
            if entry.atom_index in pair_set:
                continue
            candidate = tuple(sorted((*pair_candidate, entry.atom_index)))
            if candidate in seen:
                continue
            seen.add(candidate)
            vector = pair_vector ^ entry.vector
            distance = (vector ^ target).bit_count()
            if (distance, candidate) < (best_distance, best_candidate):
                best_distance, best_candidate, best_vector = distance, candidate, vector

    for left_index, (left_candidate, left_vector) in enumerate(pair_beam):
        left_set = set(left_candidate)
        for right_candidate, right_vector in pair_beam[left_index + 1 :]:
            if left_set.intersection(right_candidate):
                continue
            candidate = tuple(sorted((*left_candidate, *right_candidate)))
            if candidate in seen:
                continue
            seen.add(candidate)
            vector = left_vector ^ right_vector
            distance = (vector ^ target).bit_count()
            if (distance, candidate) < (best_distance, best_candidate):
                best_distance, best_candidate, best_vector = distance, candidate, vector

    candidate_payload = serialize_candidate(compiled, contexts, best_candidate)
    candidate_payload["subset_errors"] = best_distance
    candidate_payload["subset_total"] = total
    candidate_payload["subset_accuracy"] = (total - best_distance) / total
    candidate_payload["diagnostic_only"] = True
    candidate_payload["search_completeness"] = (
        "complete for weights 1 and 2; deterministic beam diagnostic for weights 3 and 4"
    )
    return candidate_payload


def catalogue_statistics(
    compiled: Sequence[CompiledAtom], contexts: Sequence[CurveContext]
) -> dict[str, object]:
    valid_per_curve = {
        context.curve_id: sum(
            atom.curve_bits[curve_index] is not None for atom in compiled
        )
        for curve_index, context in enumerate(contexts)
    }
    all_subset = tuple(range(len(contexts)))
    all_pool = build_pool(compiled, contexts, all_subset)
    return {
        "raw_symbolic_atoms": len(compiled),
        "valid_nonzero_atoms_per_curve": valid_per_curve,
        "valid_nonzero_on_all_curves": sum(
            all(bits is not None for bits in atom.curve_bits) for atom in compiled
        ),
        "all_curve_semantic_classes": len(all_pool),
    }


def run(maximum_weight: int, beam_size: int) -> dict[str, object]:
    contexts = tuple(build_context(*curve) for curve in FROZEN_CURVES)
    specs = generate_specs()
    if len(specs) != 1639:
        raise AssertionError(f"grammar drift: expected 1639 atoms, got {len(specs)}")
    compiled = compile_atoms(contexts, specs)

    all_curves = tuple(range(len(contexts)))
    first_three = (0, 1, 2)
    all_outcome = search_exact(
        compiled, contexts, all_curves, maximum_weight=maximum_weight
    )
    train_outcome = search_exact(
        compiled, contexts, first_three, maximum_weight=maximum_weight
    )
    individual_outcomes = [
        search_exact(compiled, contexts, (index,), maximum_weight=maximum_weight)
        for index in range(3)
    ]

    if all_outcome.found:
        decision = "TRANSFER_SEED_FOUND_REQUIRES_SYMBOLIC_LIFTING"
        symbolic_lifting = "triggered_for_the_minimum_all_curve_candidate"
    elif train_outcome.found:
        decision = "NO_ALL_CORPUS_TRANSFER;_BOUNDED_TRAIN_EXACT_SEED_EXISTS"
        symbolic_lifting = "not_triggered_because_holdout_transfer_failed"
    else:
        decision = "NO_EXACT_CANDIDATE_IN_UORC-056-C-SYNTH-V2"
        symbolic_lifting = "not_triggered_because_no_three_curve_exact_seed_exists"

    payload: dict[str, object] = {
        "schema_version": "1.0",
        "experiment": "UORC-056-TRANSFER-SYNTH-V2",
        "scope": "five frozen prime-order toy curves y^2=x^3+7 only; no external input",
        "central_target": "Q=[k]G -> Y_G(x(Q))/y(Q)=(-1)^k",
        "grammar": {
            "id": "UORC-056-C-SYNTH-V2",
            "maximum_weight": maximum_weight,
            "field_specific_fitting": False,
            "free_per_curve_phase": False,
            "zero_or_pole_policy": "reject the atom on that curve",
            "symbolic_source": "experiments/uorc056/transfer_grammar_v2.json",
        },
        "corpus": [
            {
                "curve_id": context.curve_id,
                "p": context.p,
                "order": context.order,
                "generator": list(context.generator),
                "beta": context.beta,
                "beta2": context.beta2,
                "target_points": context.order - 1,
            }
            for context in contexts
        ],
        "catalogue": catalogue_statistics(compiled, contexts),
        "exact_all_five": serialize_outcome(all_outcome, compiled, contexts),
        "exact_train_first_three_then_unmodified_holdout": serialize_outcome(
            train_outcome, compiled, contexts
        ),
        "single_curve_minimum_seeds": [
            serialize_outcome(outcome, compiled, contexts)
            for outcome in individual_outcomes
        ],
        "near_miss_all_five": near_miss_beam(
            compiled, contexts, all_curves, beam_size=beam_size
        ),
        "decision": decision,
        "symbolic_lifting_status": symbolic_lifting,
        "task_status": [
            {"task": 14, "name": "freeze_transferable_grammar_v2", "status": "complete"},
            {"task": 15, "name": "compile_identical_symbolic_atoms_across_fields", "status": "complete"},
            {"task": 16, "name": "exact_meet_in_the_middle_weight_at_most_four", "status": "complete"},
            {"task": 17, "name": "train_holdout_transfer_without_refitting", "status": "complete"},
            {"task": 18, "name": "extract_near_miss_residual_diagnostic", "status": "complete"},
            {"task": 19, "name": "symbolic_lift_of_transfer_seed", "status": symbolic_lifting},
        ],
        "claim_boundary": [
            "An exact result on one toy curve is finite evidence, not a uniform evaluator.",
            "An exact result on all five toy curves is still only a transfer seed requiring a symbolic identity and all-in asymptotic cost proof.",
            "A negative result closes only this explicit bounded grammar.",
            "No unknown production scalar is accepted or recovered.",
        ],
    }
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("uorc056_transfer_synth_v2_results.json"),
    )
    parser.add_argument("--max-weight", type=int, default=4, choices=(1, 2, 3, 4))
    parser.add_argument("--beam-size", type=int, default=192)
    args = parser.parse_args()
    if args.beam_size < 8:
        raise SystemExit("--beam-size must be at least 8")
    payload = run(maximum_weight=args.max_weight, beam_size=args.beam_size)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(
        json.dumps(
            {
                "experiment": payload["experiment"],
                "catalogue": payload["catalogue"],
                "decision": payload["decision"],
                "exact_all_five": payload["exact_all_five"]["found"],  # type: ignore[index]
                "exact_first_three": payload[
                    "exact_train_first_three_then_unmodified_holdout"
                ]["found"],  # type: ignore[index]
                "output": str(args.out),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
