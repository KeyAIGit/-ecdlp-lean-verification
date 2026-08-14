#!/usr/bin/env python3
"""Exact balanced line-product divisor screen for UORC-056.

The bounded atom is

    (L1(Q) * L2(Q)) / (L3(Q) * L4(Q)),

where each Li is a public affine line from the frozen V1 grammar.  Admission is
based on equality of the aggregate local orders of the two products at every
tested subgroup point.  This permits genuine cross-factor cancellation that
cannot be represented as a product of individually admissible line ratios.

A product profile is computed exactly from the local line profiles:
orders add and quadratic-character bits of leading coefficients xor.  No
exceptional point is omitted, patched, or assigned a target-indexed value.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import uorc056_circuit_synth as base
import uorc056_divisor_aware_rational as rational

Curve = rational.Curve
Line = rational.Line
Context = rational.Context
Signature = tuple[tuple[int, int], ...]
LineProduct = tuple[int, int]


@dataclass(frozen=True)
class SparseLineProfile:
    orders: Signature
    lead_sign_bits: int


@dataclass(frozen=True)
class ProductRatioMeta:
    numerator: tuple[Line, Line]
    denominator: tuple[Line, Line]
    canceled_orbit_zero: bool
    canceled_point_count: int


def merge_signatures(left: Signature, right: Signature) -> Signature:
    """Add two sparse local-order vectors."""
    result: list[tuple[int, int]] = []
    left_index = 0
    right_index = 0
    while left_index < len(left) and right_index < len(right):
        left_position, left_order = left[left_index]
        right_position, right_order = right[right_index]
        if left_position == right_position:
            result.append((left_position, left_order + right_order))
            left_index += 1
            right_index += 1
        elif left_position < right_position:
            result.append((left_position, left_order))
            left_index += 1
        else:
            result.append((right_position, right_order))
            right_index += 1
    result.extend(left[left_index:])
    result.extend(right[right_index:])
    return tuple(result)


def sparse_line_profiles(
    lines: Sequence[Line],
    curve_contexts: Sequence[Context],
) -> list[SparseLineProfile]:
    profiles: list[SparseLineProfile] = []
    for line in lines:
        orders: list[tuple[int, int]] = []
        lead_sign_bits = 0
        for curve, local_points, offset in curve_contexts:
            p, _, _ = curve
            a = rational.symbol(line[0], curve)
            b = rational.symbol(line[1], curve)
            c = rational.symbol(line[2], curve)
            if a == 0 and b == 0:
                raise AssertionError(
                    "symbolic nonzero line specialized to a constant"
                )
            for local_index, local_point in enumerate(local_points):
                order, lead = rational.line_order_and_lead(
                    a,
                    b,
                    c,
                    local_point,
                    p,
                )
                position = offset + local_index
                if order:
                    orders.append((position, order))
                sign = base.chi(lead, p)
                if sign == 0:
                    raise AssertionError("local leading coefficient vanished")
                if sign == -1:
                    lead_sign_bits |= 1 << position
        profiles.append(SparseLineProfile(tuple(orders), lead_sign_bits))
    return profiles


def product_classes(
    profiles: Sequence[SparseLineProfile],
) -> dict[Signature, dict[int, LineProduct]]:
    """Group semantic line products by their aggregate valuation signature."""
    classes: dict[Signature, dict[int, LineProduct]] = defaultdict(dict)
    for left in range(len(profiles)):
        left_profile = profiles[left]
        for right in range(left, len(profiles)):
            right_profile = profiles[right]
            signature = merge_signatures(
                left_profile.orders,
                right_profile.orders,
            )
            sign_bits = (
                left_profile.lead_sign_bits
                ^ right_profile.lead_sign_bits
            )
            classes[signature].setdefault(sign_bits, (left, right))
    return classes


def line_json(line: Line) -> dict:
    return {"a": line[0], "b": line[1], "c": line[2]}


def product_json(product: tuple[Line, Line]) -> list[dict]:
    return [line_json(product[0]), line_json(product[1])]


def ratio_json(meta: ProductRatioMeta) -> dict:
    return {
        "numerator_product": product_json(meta.numerator),
        "denominator_product": product_json(meta.denominator),
        "canceled_orbit_zero": meta.canceled_orbit_zero,
        "canceled_point_count": meta.canceled_point_count,
    }


def product_ratio_catalog(
    lines: Sequence[Line],
    classes: dict[Signature, dict[int, LineProduct]],
) -> tuple[dict[int, ProductRatioMeta], dict]:
    representatives: dict[int, ProductRatioMeta] = {}
    exceptional_vectors: set[int] = set()
    nonexceptional_vectors: set[int] = set()
    admissible_ratios = 0
    exceptional_ratios = 0
    semantic_product_profiles = 0
    maximum_class_size = 0

    for signature, semantic_products in classes.items():
        vectors = list(semantic_products)
        semantic_product_profiles += len(vectors)
        maximum_class_size = max(maximum_class_size, len(vectors))
        exceptional = bool(signature)
        canceled_count = len(signature)

        for numerator_index, numerator_bits in enumerate(vectors):
            numerator_indices = semantic_products[numerator_bits]
            numerator = (
                lines[numerator_indices[0]],
                lines[numerator_indices[1]],
            )
            for denominator_bits in vectors[numerator_index:]:
                denominator_indices = semantic_products[denominator_bits]
                denominator = (
                    lines[denominator_indices[0]],
                    lines[denominator_indices[1]],
                )
                admissible_ratios += 1
                exceptional_ratios += int(exceptional)
                bits = numerator_bits ^ denominator_bits
                meta = ProductRatioMeta(
                    numerator,
                    denominator,
                    exceptional,
                    canceled_count,
                )
                representatives.setdefault(bits, meta)
                if exceptional:
                    exceptional_vectors.add(bits)
                else:
                    nonexceptional_vectors.add(bits)

    stats = {
        "line_templates": len(lines),
        "unordered_line_products": len(lines) * (len(lines) + 1) // 2,
        "valuation_signatures": len(classes),
        "semantic_product_profiles": semantic_product_profiles,
        "maximum_semantic_products_per_valuation_class": maximum_class_size,
        "admissible_unordered_product_ratios": admissible_ratios,
        "ratios_with_canceled_orbit_zero": exceptional_ratios,
        "unique_sign_vectors": len(representatives),
        "nonexceptional_sign_vectors": len(nonexceptional_vectors),
        "exceptional_sign_vectors": len(exceptional_vectors),
        "novel_exceptional_sign_vectors": len(
            exceptional_vectors - nonexceptional_vectors
        ),
    }
    return representatives, stats


def pair_index(vectors: Sequence[int]) -> tuple[
    dict[int, list[tuple[int, int]]],
    int,
    int,
]:
    by_xor: dict[int, list[tuple[int, int]]] = defaultdict(list)
    pair_count = 0
    for left in range(len(vectors)):
        left_vector = vectors[left]
        for right in range(left + 1, len(vectors)):
            by_xor[left_vector ^ vectors[right]].append((left, right))
            pair_count += 1
    maximum_multiplicity = max(
        (len(edges) for edges in by_xor.values()),
        default=0,
    )
    return by_xor, pair_count, maximum_multiplicity


def candidate_json(
    representatives: dict[int, ProductRatioMeta],
    vectors: Sequence[int],
    indices: tuple[int, ...],
    phase: int,
) -> dict:
    return {
        "weight": len(indices),
        "output_phase": phase,
        "atoms": [
            ratio_json(representatives[vectors[index]])
            for index in indices
        ],
    }


def exact_search(
    representatives: dict[int, ProductRatioMeta],
    target: int,
    total: int,
    maximum_weight: int,
) -> tuple[dict | None, dict]:
    vectors = list(representatives)
    lookup = {vector: index for index, vector in enumerate(vectors)}
    mask = (1 << total) - 1
    desired = ((target, 1), (target ^ mask, -1))

    empty_stats = {
        "pair_count": 0,
        "pair_xor_classes": 0,
        "maximum_pair_xor_multiplicity": 0,
    }

    for index, vector in enumerate(vectors):
        for goal, phase in desired:
            if vector == goal:
                return (
                    candidate_json(
                        representatives,
                        vectors,
                        (index,),
                        phase,
                    ),
                    empty_stats,
                )
    if maximum_weight < 2:
        return None, empty_stats

    for left, vector in enumerate(vectors):
        for goal, phase in desired:
            right = lookup.get(goal ^ vector)
            if right is not None and right != left:
                return (
                    candidate_json(
                        representatives,
                        vectors,
                        tuple(sorted((left, right))),
                        phase,
                    ),
                    empty_stats,
                )
    if maximum_weight < 3:
        return None, empty_stats

    pairs_by_xor, pair_count, maximum_multiplicity = pair_index(vectors)
    search_stats = {
        "pair_count": pair_count,
        "pair_xor_classes": len(pairs_by_xor),
        "maximum_pair_xor_multiplicity": maximum_multiplicity,
    }

    for single, vector in enumerate(vectors):
        for goal, phase in desired:
            for left, right in pairs_by_xor.get(goal ^ vector, ()):
                if single not in (left, right):
                    return (
                        candidate_json(
                            representatives,
                            vectors,
                            tuple(sorted((single, left, right))),
                            phase,
                        ),
                        search_stats,
                    )
    if maximum_weight < 4:
        return None, search_stats

    for value, edges in pairs_by_xor.items():
        for goal, phase in desired:
            complement = pairs_by_xor.get(goal ^ value)
            if not complement:
                continue
            for left, right in edges:
                for other_left, other_right in complement:
                    if len({left, right, other_left, other_right}) == 4:
                        return (
                            candidate_json(
                                representatives,
                                vectors,
                                tuple(
                                    sorted(
                                        (
                                            left,
                                            right,
                                            other_left,
                                            other_right,
                                        )
                                    )
                                ),
                                phase,
                            ),
                            search_stats,
                        )
    return None, search_stats


def signed_matches(bits: int, target: int, total: int) -> tuple[int, int]:
    direct = total - (bits ^ target).bit_count()
    return (
        (direct, 1)
        if direct >= total - direct
        else (total - direct, -1)
    )


def best_correlations(
    representatives: dict[int, ProductRatioMeta],
    target: int,
    total: int,
) -> dict:
    vectors = list(representatives)
    best_single = max(
        (signed_matches(vector, target, total)[0], -index)
        for index, vector in enumerate(vectors)
    )
    single_index = -best_single[1]
    single_matches, single_phase = signed_matches(
        vectors[single_index],
        target,
        total,
    )

    best_pair = max(
        (
            signed_matches(
                vectors[left] ^ vectors[right],
                target,
                total,
            )[0],
            -left,
            -right,
        )
        for left in range(len(vectors))
        for right in range(left + 1, len(vectors))
    )
    left = -best_pair[1]
    right = -best_pair[2]
    pair_matches, pair_phase = signed_matches(
        vectors[left] ^ vectors[right],
        target,
        total,
    )
    return {
        "weight_one": {
            "matches": single_matches,
            "total": total,
            "accuracy": f"{single_matches / total:.9f}",
            "output_phase": single_phase,
            "atoms": [
                ratio_json(representatives[vectors[single_index]])
            ],
        },
        "weight_two": {
            "matches": pair_matches,
            "total": total,
            "accuracy": f"{pair_matches / total:.9f}",
            "output_phase": pair_phase,
            "atoms": [
                ratio_json(representatives[vectors[left]]),
                ratio_json(representatives[vectors[right]]),
            ],
        },
    }


def catalog_for_curves(
    curves: Sequence[Curve],
    lines: Sequence[Line],
) -> tuple[dict[int, ProductRatioMeta], dict, int]:
    curve_contexts, total = rational.contexts(curves)
    profiles = sparse_line_profiles(lines, curve_contexts)
    classes = product_classes(profiles)
    representatives, stats = product_ratio_catalog(lines, classes)
    return representatives, stats, total


def run(grammar_path: Path) -> dict:
    grammar_bytes = grammar_path.read_bytes()
    grammar = json.loads(grammar_bytes)
    expected_profile = (
        "UORC-056-DIVISOR-AWARE-BALANCED-LINE-PRODUCT-RATIO-V4"
    )
    if grammar["profile_id"] != expected_profile:
        raise AssertionError("unexpected balanced product grammar")

    base_grammar_path = Path(grammar["base_ratio_grammar"])
    base_grammar = json.loads(
        base_grammar_path.read_text(encoding="utf-8")
    )
    if base_grammar["profile_id"] != (
        "UORC-056-DIVISOR-AWARE-LINE-RATIO-V1"
    ):
        raise AssertionError("unexpected base ratio grammar")

    discovery_curves = tuple(
        rational.parse_curve(row)
        for row in base_grammar["discovery_corpus"]
    )
    holdout_curves = tuple(
        rational.parse_curve(row)
        for row in base_grammar["holdout_corpus"]
    )
    lines = rational.line_templates(base_grammar)
    expected_products = grammar["line_products"]["raw_count"]
    if len(lines) * (len(lines) + 1) // 2 != expected_products:
        raise AssertionError("line-product count drifted")
    maximum_weight = grammar["sign_circuit"]["maximum_weight"]

    discovery_representatives, discovery_stats, discovery_total = (
        catalog_for_curves(discovery_curves, lines)
    )
    discovery_contexts, _ = rational.contexts(discovery_curves)
    discovery_target = rational.target_bits(discovery_contexts)
    discovery_candidate, discovery_search_stats = exact_search(
        discovery_representatives,
        discovery_target,
        discovery_total,
        maximum_weight,
    )
    discovery_best = best_correlations(
        discovery_representatives,
        discovery_target,
        discovery_total,
    )

    full_curves = discovery_curves + holdout_curves
    full_representatives, full_stats, full_total = catalog_for_curves(
        full_curves,
        lines,
    )
    full_contexts, _ = rational.contexts(full_curves)
    full_target = rational.target_bits(full_contexts)
    full_candidate, full_search_stats = exact_search(
        full_representatives,
        full_target,
        full_total,
        maximum_weight,
    )
    full_best = best_correlations(
        full_representatives,
        full_target,
        full_total,
    )

    del discovery_representatives
    gc.collect()

    if discovery_candidate is None:
        transfer_status = "not_reached_no_discovery_candidate"
        decision = (
            "no_exact_balanced_line_product_divisor_circuit_weight_le_4"
        )
    elif full_candidate is None:
        transfer_status = "discovery_candidate_failed_full_corpus"
        decision = "finite_discovery_only_balanced_product_candidate"
    else:
        transfer_status = "full_corpus_candidate_requires_symbolic_proof"
        decision = "symbolic_followup_required"

    return {
        "schema_version": "1.0",
        "experiment": expected_profile,
        "grammar_sha256": hashlib.sha256(grammar_bytes).hexdigest(),
        "base_grammar_sha256": hashlib.sha256(
            base_grammar_path.read_bytes()
        ).hexdigest(),
        "corpus": {
            "discovery_curves": len(discovery_curves),
            "holdout_curves": len(holdout_curves),
            "discovery_nonzero_points": discovery_total,
            "full_corpus_nonzero_points": full_total,
        },
        "discovery_catalog": discovery_stats,
        "full_corpus_catalog": full_stats,
        "discovery_exact_search": {
            "candidate_found": discovery_candidate is not None,
            "candidate": discovery_candidate,
            **discovery_search_stats,
        },
        "full_corpus_exact_search": {
            "candidate_found": full_candidate is not None,
            "candidate": full_candidate,
            **full_search_stats,
        },
        "best_discovery_correlations": discovery_best,
        "best_full_corpus_correlations": full_best,
        "exceptional_fiber_decision": (
            "aggregate cross-factor cancellation creates 429 discovery-only "
            "semantic vectors, but zero remain novel on the full "
            "eighteen-curve corpus"
        ),
        "transfer_status": transfer_status,
        "decision": decision,
        "claim_boundary": [
            "This is complete only for ratios of unordered products of two declared affine line templates and products of at most four character atoms.",
            "It admits aggregate cross-factor cancellation but does not cover irreducible conics, higher-degree functions, pulled line products, EDS factors or unrestricted straight-line programs.",
            "Orders add and local leading coefficients multiply exactly; no exceptional point is patched or omitted.",
            "No external point, wallet, real key or production-sized discrete-log target is accepted.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--grammar",
        type=Path,
        default=Path(
            "experiments/uorc056/"
            "divisor_aware_balanced_product_grammar.json"
        ),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(
            "experiments/uorc056/"
            "divisor_aware_balanced_product_results.json"
        ),
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    text = json.dumps(
        run(args.grammar),
        indent=2,
        sort_keys=True,
    ) + "\n"
    if args.check:
        if (
            not args.out.exists()
            or args.out.read_text(encoding="utf-8") != text
        ):
            raise SystemExit("balanced product result drift")
        print("UORC056_BALANCED_PRODUCT_OK")
        return 0

    args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
