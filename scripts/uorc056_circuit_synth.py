#!/usr/bin/env python3
"""Exact bounded circuit synthesis for the first UORC-056 gate profile.

The active profile is products of quadratic characters of projectively
normalized affine forms a*x+b*y+c. It validates synthesis, semantic quotient
and transfer machinery. It is not the full C_SYNTH_V1 universe.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable, Optional

Point = Optional[tuple[int, int]]
Form = tuple[int, int, int]
FROZEN_CURVES = (
    (43, 31, (2, 12)),
    (67, 79, (2, 22)),
    (79, 67, (1, 18)),
    (127, 127, (1, 32)),
    (163, 139, (2, 34)),
)


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
        raise AssertionError("invalid frozen generator/order")
    for point in points[1:]:
        assert point is not None
        x, y = point
        if (y * y - x * x * x - 7) % p:
            raise AssertionError("point is not on y^2=x^3+7")
    return points


def chi(value: int, p: int) -> int:
    value %= p
    if value == 0:
        return 0
    return 1 if pow(value, (p - 1) // 2, p) == 1 else -1


def normalized_forms(p: int) -> Iterable[Form]:
    for b in range(p):
        for c in range(p):
            yield 1, b, c
    for c in range(p):
        yield 0, 1, c
    yield 0, 0, 1


def sign_bits(form: Form, points: list[Point], p: int) -> int | None:
    a, b, c = form
    bits = 0
    for index, point in enumerate(points[1:]):
        assert point is not None
        x, y = point
        sign = chi(a * x + b * y + c, p)
        if sign == 0:
            return None
        if sign == -1:
            bits |= 1 << index
    return bits


def parity_bits(order: int) -> int:
    return sum(1 << index for index, k in enumerate(range(1, order)) if k & 1)


def semantic_quotient(p: int, points: list[Point]) -> tuple[int, dict[int, Form]]:
    valid = 0
    reps: dict[int, Form] = {}
    for form in normalized_forms(p):
        bits = sign_bits(form, points, p)
        if bits is None:
            continue
        valid += 1
        reps.setdefault(bits, form)
    return valid, reps


def minimum_product(reps: dict[int, Form], order: int, maximum_weight: int = 4) -> tuple[int, tuple[Form, ...], int] | None:
    vectors = list(reps)
    vector_set = set(vectors)
    target = parity_bits(order)
    mask = (1 << (order - 1)) - 1
    targets = ((target, 1), (target ^ mask, -1))
    for vector in vectors:
        for desired, phase in targets:
            if vector == desired:
                return 1, (reps[vector],), phase
    if maximum_weight < 2:
        return None
    for vector in vectors:
        for desired, phase in targets:
            partner = desired ^ vector
            if partner in vector_set:
                return 2, (reps[vector], reps[partner]), phase
    if maximum_weight < 3:
        return None
    pairs: dict[int, tuple[Form, Form]] = {}
    for i, left in enumerate(vectors):
        for right in vectors[i:]:
            pairs.setdefault(left ^ right, (reps[left], reps[right]))
    for vector in vectors:
        for desired, phase in targets:
            pair = pairs.get(desired ^ vector)
            if pair is not None:
                return 3, (reps[vector], *pair), phase
    if maximum_weight < 4:
        return None
    for pair_bits, left_pair in pairs.items():
        for desired, phase in targets:
            right_pair = pairs.get(desired ^ pair_bits)
            if right_pair is not None:
                return 4, (*left_pair, *right_pair), phase
    return None


def formula_bits(forms: tuple[Form, ...], phase: int, points: list[Point], p: int) -> int | None:
    bits = 0
    for index, point in enumerate(points[1:]):
        assert point is not None
        x, y = point
        value = phase % p
        for a, b, c in forms:
            value = value * (a * x + b * y + c) % p
        sign = chi(value, p)
        if sign == 0:
            return None
        if sign == -1:
            bits |= 1 << index
    return bits


def run(grammar_path: Path) -> dict:
    grammar_bytes = grammar_path.read_bytes()
    grammar = json.loads(grammar_bytes)
    if grammar["grammar_id"] != "UORC-056-C-SYNTH-V1":
        raise AssertionError("unexpected grammar")
    p, n, generator = FROZEN_CURVES[0]
    points = orbit(generator, n, p)
    valid, reps = semantic_quotient(p, points)
    result = minimum_product(reps, n, 4)
    if result is None:
        raise AssertionError("known finite weight-four seed was not rediscovered")
    weight, forms, phase = result
    if weight != 4:
        raise AssertionError(f"minimum weight drifted: {weight}")
    transfer = []
    for q, order, gen in FROZEN_CURVES:
        q_points = orbit(gen, order, q)
        bits = formula_bits(forms, phase, q_points, q)
        target = parity_bits(order)
        mask = (1 << (order - 1)) - 1
        transfer.append({
            "p": q,
            "n": order,
            "exact": bits == target,
            "exact_up_to_global_sign": bits in (target, target ^ mask),
            "defined_on_full_orbit": bits is not None,
        })
    exact_count = sum(row["exact"] for row in transfer)
    return {
        "schema_version": "1.0",
        "experiment": "UORC-056-C-SYNTH-V1-AFFINE-CHAR-PRODUCT",
        "grammar_sha256": hashlib.sha256(grammar_bytes).hexdigest(),
        "deep_case": {"p": p, "n": n, "generator": list(generator)},
        "enumeration": {
            "projective_normalized_forms": p * p + p + 1,
            "valid_nonvanishing_forms": valid,
            "unique_semantic_sign_vectors": len(reps),
            "global_sign_quotient": True,
            "maximum_product_weight": 4,
        },
        "minimum_exact_seed": {
            "weight": weight,
            "phase": phase,
            "forms": [list(form) for form in forms],
            "expression": "phase * product_i chi(a_i*x(Q)+b_i*y(Q)+c_i)",
        },
        "unchanged_integer_formula_transfer": transfer,
        "decision": "finite_nontransfer_seed" if exact_count < 3 else "transfer_followup_required",
        "claim_boundary": [
            "The active profile is a strict subgrammar of C_SYNTH_V1.",
            "Rediscovery on p=43 validates the synthesis engine but is not a scalable evaluator.",
            "A candidate requires unchanged transfer to at least three structural curves and a symbolic identity.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--grammar", type=Path, default=Path("experiments/uorc056/circuit_grammar.json"))
    parser.add_argument("--out", type=Path, default=Path("experiments/uorc056/circuit_synth_results.json"))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = json.dumps(run(args.grammar), indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.out.exists() or args.out.read_text(encoding="utf-8") != text:
            raise SystemExit("circuit synthesis result drift")
        print("UORC056_CIRCUIT_SYNTH_OK")
        return 0
    args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
