#!/usr/bin/env python3
"""Exact cross-curve structural circuit screen for UORC-056.

Only frozen toy subgroups are accepted. The identical symbolic AST is tested on
five discovery curves and thirteen holdouts; no external point or scalar input
is exposed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Sequence

import uorc056_circuit_synth as base

Curve = tuple[int, int, tuple[int, int]]
Context = tuple[int, int, tuple[int, int], list[base.Point], int]
Feature = tuple[str, int]
Template = tuple


def prime(value: int) -> bool:
    if value < 2:
        return False
    if value % 2 == 0:
        return value == 2
    divisor = 3
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += 2
    return True


def parse_curve(row: dict) -> Curve:
    return int(row["p"]), int(row["n"]), tuple(row["G"])  # type: ignore[return-value]


def beta_pair(p: int) -> tuple[int, int]:
    roots = [z for z in range(2, p) if (z * z + z + 1) % p == 0]
    if len(roots) != 2:
        raise AssertionError("expected two nontrivial cube roots")
    return tuple(sorted(roots))  # type: ignore[return-value]


def symbol(name: str, curve: Curve) -> int:
    p, _, generator = curve
    xg, yg = generator
    beta_lo, beta_hi = beta_pair(p)
    values = {
        "zero": 0,
        "one": 1,
        "neg_one": -1,
        "two": 2,
        "neg_two": -2,
        "curve_b": 7,
        "neg_curve_b": -7,
        "x_G": xg,
        "neg_x_G": -xg,
        "y_G": yg,
        "neg_y_G": -yg,
        "beta_lo": beta_lo,
        "beta_hi": beta_hi,
        "x_G_plus_y_G": xg + yg,
        "x_G_minus_y_G": xg - yg,
    }
    if name not in values:
        raise AssertionError(f"unknown symbol {name}")
    return values[name] % p


def contexts(curves: Sequence[Curve]) -> tuple[list[Context], int]:
    result: list[Context] = []
    offset = 0
    for p, n, generator in curves:
        if not prime(p) or not prime(n) or p % 3 != 1:
            raise AssertionError("corpus requires prime p,n and p congruent 1 mod 3")
        points = base.orbit(generator, n, p)
        result.append((p, n, generator, points, offset))
        offset += n - 1
    return result, offset


def templates(grammar: dict) -> list[Template]:
    multipliers = grammar["coordinate_sources"]["small_multipliers"]
    same = grammar["coefficient_vocabulary"]["same_source_linear"]
    cross = grammar["coefficient_vocabulary"]["cross_source_nonzero"]
    offsets = grammar["coefficient_vocabulary"]["offsets"]
    result: list[Template] = []

    for multiplier in multipliers:
        for x_coefficient in same:
            for y_coefficient in same:
                if x_coefficient == y_coefficient == "zero":
                    continue
                for offset in offsets:
                    result.append(
                        ("same", multiplier, x_coefficient, y_coefficient, offset)
                    )

    features: list[Feature] = [
        (coordinate, multiplier)
        for multiplier in multipliers
        for coordinate in ("x", "y")
    ]
    for left_index, left in enumerate(features):
        for right in features[left_index + 1 :]:
            for left_coefficient in cross:
                for right_coefficient in cross:
                    for offset in offsets:
                        result.append(
                            (
                                "cross",
                                left,
                                left_coefficient,
                                right,
                                right_coefficient,
                                offset,
                            )
                        )
    result.extend(("phase", offset) for offset in offsets if offset != "zero")
    return result


def template_json(template: Template) -> dict:
    if template[0] == "same":
        _, multiplier, x_coefficient, y_coefficient, offset = template
        return {
            "kind": "same_source_affine",
            "multiplier": multiplier,
            "x_coefficient": x_coefficient,
            "y_coefficient": y_coefficient,
            "offset": offset,
        }
    if template[0] == "cross":
        _, left, left_coefficient, right, right_coefficient, offset = template
        return {
            "kind": "cross_source_affine",
            "left": {
                "coordinate": left[0],
                "multiplier": left[1],
                "coefficient": left_coefficient,
            },
            "right": {
                "coordinate": right[0],
                "multiplier": right[1],
                "coefficient": right_coefficient,
            },
            "offset": offset,
        }
    if template[0] == "phase":
        return {"kind": "public_phase", "offset": template[1]}
    raise AssertionError("unknown template")


def coordinate(point: base.Point, name: str) -> int:
    if point is None:
        raise AssertionError("small nonzero multiplier reached infinity")
    return point[0] if name == "x" else point[1]


def sign_bits(template: Template, curve_contexts: Sequence[Context]) -> int | None:
    bits = 0
    for p, n, generator, points, offset_bits in curve_contexts:
        curve = (p, n, generator)
        kind = template[0]
        if kind == "phase":
            sign = base.chi(symbol(template[1], curve), p)
            if sign == 0:
                return None
            if sign == -1:
                bits |= ((1 << (n - 1)) - 1) << offset_bits
            continue

        if kind == "same":
            _, multiplier, x_name, y_name, offset_name = template
            x_coefficient = symbol(x_name, curve)
            y_coefficient = symbol(y_name, curve)
            constant = symbol(offset_name, curve)
            for scalar in range(1, n):
                point = points[(multiplier * scalar) % n]
                assert point is not None
                value = x_coefficient * point[0] + y_coefficient * point[1] + constant
                sign = base.chi(value, p)
                if sign == 0:
                    return None
                if sign == -1:
                    bits |= 1 << (offset_bits + scalar - 1)
            continue

        _, left, left_name, right, right_name, offset_name = template
        left_coefficient = symbol(left_name, curve)
        right_coefficient = symbol(right_name, curve)
        constant = symbol(offset_name, curve)
        for scalar in range(1, n):
            left_point = points[(left[1] * scalar) % n]
            right_point = points[(right[1] * scalar) % n]
            value = (
                left_coefficient * coordinate(left_point, left[0])
                + right_coefficient * coordinate(right_point, right[0])
                + constant
            )
            sign = base.chi(value, p)
            if sign == 0:
                return None
            if sign == -1:
                bits |= 1 << (offset_bits + scalar - 1)
    return bits


def target_bits(curve_contexts: Sequence[Context]) -> int:
    result = 0
    for _, n, _, _, offset in curve_contexts:
        result |= base.parity_bits(n) << offset
    return result


def catalog(
    template_list: Sequence[Template], curve_contexts: Sequence[Context]
) -> tuple[int, dict[int, Template]]:
    valid = 0
    representatives: dict[int, Template] = {}
    for template in template_list:
        bits = sign_bits(template, curve_contexts)
        if bits is not None:
            valid += 1
            representatives.setdefault(bits, template)
    return valid, representatives


def pair_index(vectors: Sequence[int]) -> tuple[
    dict[int, list[tuple[int, int]]], list[tuple[int, int, int]]
]:
    by_xor: dict[int, list[tuple[int, int]]] = {}
    pairs: list[tuple[int, int, int]] = []
    for left in range(len(vectors)):
        for right in range(left + 1, len(vectors)):
            value = vectors[left] ^ vectors[right]
            by_xor.setdefault(value, []).append((left, right))
            pairs.append((value, left, right))
    return by_xor, pairs


def exact_search(
    representatives: dict[int, Template],
    target: int,
    total: int,
    maximum_weight: int,
) -> dict | None:
    vectors = list(representatives)
    lookup = {vector: index for index, vector in enumerate(vectors)}
    mask = (1 << total) - 1
    desired = ((target, 1), (target ^ mask, -1))

    for index, vector in enumerate(vectors):
        for goal, phase in desired:
            if vector == goal:
                return candidate_json(representatives, vectors, (index,), phase)
    if maximum_weight < 2:
        return None

    for left, vector in enumerate(vectors):
        for goal, phase in desired:
            right = lookup.get(goal ^ vector)
            if right is not None and right != left:
                return candidate_json(
                    representatives, vectors, tuple(sorted((left, right))), phase
                )
    if maximum_weight < 3:
        return None

    pairs_by_xor, pairs = pair_index(vectors)
    for single, vector in enumerate(vectors):
        for goal, phase in desired:
            for left, right in pairs_by_xor.get(goal ^ vector, ()):
                if single not in (left, right):
                    return candidate_json(
                        representatives,
                        vectors,
                        tuple(sorted((single, left, right))),
                        phase,
                    )
    if maximum_weight < 4:
        return None

    for value, left, right in pairs:
        for goal, phase in desired:
            for other_left, other_right in pairs_by_xor.get(goal ^ value, ()):
                if len({left, right, other_left, other_right}) == 4:
                    return candidate_json(
                        representatives,
                        vectors,
                        tuple(sorted((left, right, other_left, other_right))),
                        phase,
                    )
    return None


def candidate_json(
    representatives: dict[int, Template],
    vectors: Sequence[int],
    indices: tuple[int, ...],
    phase: int,
) -> dict:
    return {
        "weight": len(indices),
        "output_phase": phase,
        "templates": [
            template_json(representatives[vectors[index]]) for index in indices
        ],
    }


def signed_matches(bits: int, target: int, total: int) -> tuple[int, int]:
    direct = total - (bits ^ target).bit_count()
    return (direct, 1) if direct >= total - direct else (total - direct, -1)


def best_correlations(
    representatives: dict[int, Template], target: int, total: int
) -> dict:
    vectors = list(representatives)
    single = max(
        (signed_matches(vector, target, total)[0], -index)
        for index, vector in enumerate(vectors)
    )
    single_index = -single[1]
    single_matches, single_phase = signed_matches(
        vectors[single_index], target, total
    )

    pair = max(
        (
            signed_matches(vectors[left] ^ vectors[right], target, total)[0],
            -left,
            -right,
        )
        for left in range(len(vectors))
        for right in range(left + 1, len(vectors))
    )
    left, right = -pair[1], -pair[2]
    pair_matches, pair_phase = signed_matches(
        vectors[left] ^ vectors[right], target, total
    )
    return {
        "weight_one": {
            "matches": single_matches,
            "total": total,
            "accuracy": f"{single_matches / total:.9f}",
            "output_phase": single_phase,
            "templates": [template_json(representatives[vectors[single_index]])],
        },
        "weight_two": {
            "matches": pair_matches,
            "total": total,
            "accuracy": f"{pair_matches / total:.9f}",
            "output_phase": pair_phase,
            "templates": [
                template_json(representatives[vectors[left]]),
                template_json(representatives[vectors[right]]),
            ],
        },
    }


def run(grammar_path: Path) -> dict:
    grammar_bytes = grammar_path.read_bytes()
    grammar = json.loads(grammar_bytes)
    if grammar["profile_id"] != "UORC-056-STRUCTURAL-TRANSFER-V2":
        raise AssertionError("unexpected grammar")

    discovery = tuple(parse_curve(row) for row in grammar["discovery_corpus"])
    holdouts = tuple(parse_curve(row) for row in grammar["holdout_corpus"])
    discovery_contexts, discovery_total = contexts(discovery)
    full_contexts, full_total = contexts(discovery + holdouts)
    template_list = templates(grammar)
    discovery_valid, discovery_reps = catalog(
        template_list, discovery_contexts
    )
    full_valid, full_reps = catalog(template_list, full_contexts)
    maximum_weight = grammar["sign_circuit"]["maximum_weight"]
    discovery_target = target_bits(discovery_contexts)
    full_target = target_bits(full_contexts)
    discovery_candidate = exact_search(
        discovery_reps, discovery_target, discovery_total, maximum_weight
    )
    full_candidate = exact_search(
        full_reps, full_target, full_total, maximum_weight
    )

    if discovery_candidate is None:
        transfer_status = "not_reached_no_discovery_candidate"
        decision = "no_exact_structural_transfer_circuit_weight_le_4"
    elif full_candidate is None:
        transfer_status = "discovery_candidate_failed_full_corpus"
        decision = "finite_discovery_only_candidate"
    else:
        transfer_status = "full_corpus_candidate_requires_symbolic_lifting"
        decision = "symbolic_followup_required"

    return {
        "schema_version": "1.0",
        "experiment": "UORC-056-STRUCTURAL-TRANSFER-V2",
        "grammar_sha256": hashlib.sha256(grammar_bytes).hexdigest(),
        "corpus": {
            "discovery_curves": len(discovery),
            "holdout_curves": len(holdouts),
            "discovery_nonzero_points": discovery_total,
            "full_corpus_nonzero_points": full_total,
        },
        "enumeration": {
            "raw_symbolic_templates": len(template_list),
            "valid_on_discovery": discovery_valid,
            "unique_discovery_sign_vectors": len(discovery_reps),
            "valid_on_full_corpus": full_valid,
            "unique_full_corpus_sign_vectors": len(full_reps),
            "maximum_product_weight": maximum_weight,
        },
        "discovery_exact_search": {
            "candidate_found": discovery_candidate is not None,
            "candidate": discovery_candidate,
        },
        "full_corpus_exact_search": {
            "candidate_found": full_candidate is not None,
            "candidate": full_candidate,
        },
        "best_discovery_correlations": best_correlations(
            discovery_reps, discovery_target, discovery_total
        ),
        "transfer_status": transfer_status,
        "decision": decision,
        "cost_boundary": [
            "Every [u]Q coordinate source charges its group additions and doublings.",
            "Both beta branches are public representation-dependent constants whose construction is charged.",
            "Every quadratic character and sign multiplication is charged.",
            "The enumerative screen is discovery work, not free evaluator advice.",
        ],
        "claim_boundary": [
            "The negative result is exact only for the declared finite AST grammar and product weight at most four.",
            "It does not cover rational cancellation across exceptional zeros, index-growing EDS mechanisms, or unrestricted high-degree straight-line programs.",
            "No external point, wallet, real key, or production-sized discrete-log target is accepted.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--grammar",
        type=Path,
        default=Path("experiments/uorc056/structural_transfer_grammar.json"),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("experiments/uorc056/structural_transfer_results.json"),
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = json.dumps(run(args.grammar), indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.out.exists() or args.out.read_text(encoding="utf-8") != text:
            raise SystemExit("structural transfer result drift")
        print("UORC056_STRUCTURAL_TRANSFER_OK")
        return 0
    args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
